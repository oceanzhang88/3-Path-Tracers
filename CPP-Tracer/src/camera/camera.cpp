#include "camera.hpp"

#include <thread>
#include <algorithm>
#include <functional>
#include <iostream>
#include <iomanip>
#include <sstream>

#include "../integrator/path-tracer/path-tracer.hpp"
#include "../integrator/photon-mapper/photon-mapper.hpp"
#include "../sampling/sampling.hpp"
#include "../sampling/sampler.hpp"
#include "../common/util.hpp"
#include "../common/format.hpp"

Camera::Camera(const nlohmann::json &j, const Option &option)
{
    if (option.photon_map)
    {
        integrator = std::make_shared<PhotonMapper>(j);
    }
    else
    {
        integrator = std::make_shared<PathTracer>(j);
    }

    const nlohmann::json &c = j.at("cameras").at(option.camera_idx);

    image = Image(c.at("image"));
    if (c.find("film") != c.end())
        film = Film(image.width, image.height, c.at("film"));
    else
        film = Film(image.width, image.height);

    eye = c.at("eye");
    focal_length = c.at("focal_length").get<double>() / 1000.0;
    sensor_width = c.at("sensor_width").get<double>() / 1000.0;
    sqrtspp = c.at("sqrtspp");
    savename = c.at("savename");
    aperture_radius = (focal_length / getOptional(c, "f_stop", -1.0)) / 2.0;
    focus_distance = getOptional(c, "focus_distance", -1.0);

    if (c.find("look_at") != c.end())
    {
        glm::dvec3 look_at = c.at("look_at");
        lookAt(look_at);
        if (focus_distance < 0.0)
        {
            focus_distance = glm::distance(eye, look_at);
        }
    }
    else
    {
        forward = glm::normalize(c.at("forward").get<glm::dvec3>());
        up = glm::normalize(c.at("up").get<glm::dvec3>());
        left = glm::normalize(glm::cross(up, forward));
    }

    thin_lens = aperture_radius > 0.0 && focus_distance > 0.0;
}

void Camera::samplePixel(size_t x, size_t y)
{
    double pixel_size = sensor_width / image.width;
    size_t spp = pow2(sqrtspp);

    glm::dvec2 half_dim = glm::dvec2(image.width, image.height) * 0.5;

    Sampler::initiate(static_cast<uint32_t>(y * image.width + x));

    for(int i = 0; i < spp; i++)
    {
        Sampler::setIndex(i);

        auto u = Sampler::get<Dim::PIXEL, 2>();
        glm::dvec2 px(x + u[0], y + u[1]);
        glm::dvec2 local = pixel_size * (half_dim - px);
        glm::dvec3 direction = glm::normalize(forward * focal_length + left * local.x + up * local.y);

        // Pinhole camera ray
        Ray ray(eye, direction, integrator->scene.ior);

        if (thin_lens)
        {
            // Thin lens camera ray for depth of field
            auto u = Sampler::get<Dim::LENS, 2>();
            glm::dvec2 aperture_sample = Sampling::uniformDisk(u[0], u[1]) * aperture_radius;
            glm::dvec3 focus_point = ray(focus_distance / glm::dot(ray.direction, forward));
            glm::dvec3 start = eye + left * aperture_sample.x + up * aperture_sample.y;
            ray = Ray(start, glm::normalize(focus_point - start), integrator->scene.ior);
        }
        film.deposit(px, integrator->sampleRay(ray));
    }
    num_sampled_pixels++;
}

void Camera::sampleImage()
{
    std::vector<Bucket> buckets_vec;
    for (size_t x = 0; x < image.width; x += bucket_size)
    {
        size_t x_end = x + bucket_size;
        if (x_end >= image.width) x_end = image.width;
        for (size_t y = 0; y < image.height; y += bucket_size)
        {
            size_t y_end = y + bucket_size;
            if (y_end >= image.height) y_end = image.height;
            buckets_vec.emplace_back(glm::ivec2(x, y), glm::ivec2(x_end, y_end));
        }
    }

    std::shuffle(buckets_vec.begin(), buckets_vec.end(), Random::engine);
    WorkQueue<Bucket> buckets(buckets_vec);
    buckets_vec.clear();

    std::function<void(Camera*, WorkQueue<Bucket>&)> f = &Camera::sampleImageThread;

    std::vector<std::unique_ptr<std::thread>> threads(integrator->num_threads);
    for (auto& thread : threads)
    {
        thread = std::make_unique<std::thread>(f, this, std::ref(buckets));
    }

    std::function<void(Camera*, WorkQueue<Bucket>&)> p = &Camera::printInfoThread;
    std::thread print_thread(p, this, std::ref(buckets));

    print_thread.join();

    for (auto& thread : threads)
    {
        thread->join();
    }

    for (int y = 0; y < image.height; y++)
    {
        for (int x = 0; x < image.width; x++)
        {
            image(x, y) = film.scan(x, y);
        }
    }
}

void Camera::sampleImageThread(WorkQueue<Bucket>& buckets)
{
    Bucket bucket;
    while (buckets.getWork(bucket))
    {
        for (size_t y = bucket.min.y; y < bucket.max.y; y++)
        {
            for (size_t x = bucket.min.x; x < bucket.max.x; x++)
            {
                samplePixel(x, y);
            }
        }
    }
}

void Camera::lookAt(const glm::dvec3& p)
{
    forward = glm::normalize(p - eye);
    left = glm::cross({0.0, 1.0, 0.0}, forward);
    left = glm::length(left) < C::EPSILON ? glm::dvec3(-1.0, 0.0, 0.0) : glm::normalize(left);
    up = glm::normalize(glm::cross(forward, left));
}

void Camera::capture()
{
    std::cout << std::endl << std::string(28, '-') << "| MAIN RENDERING PASS |" << std::string(28, '-') << std::endl;
    std::cout << std::endl << "Samples per pixel: " << pow2(static_cast<double>(sqrtspp)) << std::endl << std::endl;
    auto before = std::chrono::system_clock::now();
    sampleImage();
    saveImage();
    auto now = std::chrono::system_clock::now();
    std::cout << "\r" + std::string(100, ' ') + "\r";
    std::cout << "Render Completed: " << Format::date(now);
    std::cout << ", Elapsed Time: " << Format::timeDuration(std::chrono::duration_cast<std::chrono::milliseconds>(now - before).count()) << std::endl;
}

void Camera::printInfoThread(WorkQueue<Bucket>& buckets)
{
    auto printProgressInfo = [](double progress, size_t msec_duration, size_t sps, std::ostream& out)
    {
        auto ETA = std::chrono::system_clock::now() + std::chrono::milliseconds(msec_duration);

        std::stringstream ss;
        ss << "\rTime remaining: " << Format::timeDuration(msec_duration)
           << " || " << Format::progress(progress)
           << " || ETA: " << Format::date(ETA)
           << " || Samples/s: " << Format::largeNumber(sps) + "    ";

        out << ss.str();
    };

    while (!buckets.empty())
    {
        if (num_sampled_pixels != last_num_sampled_pixels)
        {
            size_t delta_pixels = num_sampled_pixels - last_num_sampled_pixels;
            size_t pixels_left = image.num_pixels - num_sampled_pixels;

            auto now = std::chrono::steady_clock::now();
            auto delta_t = std::chrono::duration_cast<std::chrono::milliseconds>(now - last_update);

            times.push_back(static_cast<double>(delta_pixels) / delta_t.count());
            if (times.size() > num_times)
                times.pop_front();

            // moving average
            double pixels_per_msec = std::accumulate(times.begin(), times.end(), 0.0) / times.size();

            double progress = 100.0 * static_cast<double>(num_sampled_pixels) / image.num_pixels;
            auto msec_left = static_cast<size_t>(pixels_left / pixels_per_msec);
            auto sps = static_cast<size_t>(pixels_per_msec * 1000.0 * pow2(static_cast<double>(sqrtspp)));

            printProgressInfo(progress, msec_left, sps, std::cout);

            last_update = now;
            last_num_sampled_pixels = num_sampled_pixels;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
    }
}