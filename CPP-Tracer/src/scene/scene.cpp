#include "scene.hpp"

#include "glm/glm.hpp"
#include "glm/gtx/component_wise.hpp"

#include "../common/util.hpp"
#include "../common/constants.hpp"
#include "../common/format.hpp"
#include "../material/material.hpp"
#include "../surface/surface.hpp"
#include "../bvh/bvh.hpp"
#include "../sampling/sampling.hpp"

#include <fstream>
#include <sstream>
#include <iostream>

Scene::Scene(const nlohmann::json& j)
{
    std::unordered_map<std::string, std::shared_ptr<Material>> materials = j.at("materials");
    auto vertices = getOptional(j, "vertices", std::unordered_map<std::string, std::vector<glm::dvec3>>());
    ior = getOptional(j, "ior", 1.0);

    for (const auto& s : j.at("surfaces"))
    {
        std::string material_str = "default";
        if (s.find("material") != s.end())
        {
            material_str = s.at("material");
        }
        auto& material = materials.at(material_str);

        std::unique_ptr<Transform> transform;
        if (s.find("position") != s.end() || s.find("scale") != s.end() || s.find("rotation") != s.end())
        {
            transform = std::make_unique<Transform>(
                getOptional(s, "position", glm::dvec3(0.0)),
                getOptional(s, "scale", glm::dvec3(1.0)),
                glm::radians(getOptional(s, "rotation", glm::dvec3(0.0)))
            );
        }

        std::string type = s.at("type");
        if (type == "object")
        {
            std::vector<glm::dvec3> v, n;
            std::vector<std::vector<size_t>> triangles_v, triangles_vt, triangles_vn;
            if (s.find("file") != s.end())
            {
                auto obj_path = path / s.at("file").get<std::string>();
                parseOBJ(obj_path, v, n, triangles_v, triangles_vt, triangles_vn);
            }
            else
            {
                v = vertices.at(s.at("vertex_set"));
                triangles_v = s.at("triangles").get<std::vector<std::vector<size_t>>>();
            }

            bool smooth = getOptional(s, "smooth", false);

            if (smooth && n.empty())
            {
                generateVertexNormals(n, v, triangles_v);
                triangles_vn = triangles_v;
            }

            bool is_emissive = glm::compMax(material->emittance) > C::EPSILON;
            double total_area = 0.0;
            if (is_emissive)
            {
                for (const auto& t : triangles_v)
                {
                    total_area += Surface::Triangle(v.at(t.at(0)), v.at(t.at(1)), v.at(t.at(2)), nullptr).area();
                }
            }

            for (size_t i = 0; i < triangles_v.size(); i++)
            {
                const auto &t = triangles_v[i];

                // Entire object emits the flux of assigned material emittance in scene file.
                // The flux of the material therefore needs to be distributed amongst all object triangles.
                std::shared_ptr<Material> mat;
                if (is_emissive && total_area > C::EPSILON)
                {
                    double area = Surface::Triangle(v.at(t.at(0)), v.at(t.at(1)), v.at(t.at(2)), nullptr).area();
                    mat = std::make_shared<Material>(*material);
                    mat->emittance *= area / total_area;
                }
                else
                {
                    mat = material;
                }

                if (smooth)
                {
                    const auto &tn = triangles_vn[i];
                    surfaces.push_back(std::make_shared<Surface::Triangle>(
                        v.at(t.at(0)), v.at(t.at(1)), v.at(t.at(2)),
                        n.at(tn.at(0)), n.at(tn.at(1)), n.at(tn.at(2)), mat)
                    );
                }
                else
                {
                    surfaces.push_back(std::make_shared<Surface::Triangle>(
                        v.at(t.at(0)), v.at(t.at(1)), v.at(t.at(2)), mat)
                    );
                }
                if (transform) surfaces.back()->transform(*transform);
            }
        }
        else
        {
            if (type == "triangle")
            {
                const auto& v = s.at("vertices");
                surfaces.push_back(std::make_shared<Surface::Triangle>(v.at(0), v.at(1), v.at(2), material));
            }
            else if (type == "sphere")
            {
                surfaces.push_back(std::make_shared<Surface::Sphere>(s.at("radius"), material));
            }
            else if (type == "quadric")
            {
                // Emittance is not supported for general quadrics 
                // (no parameterization -> no uniform surface sampling or surface area integral)
                std::shared_ptr<Material> mat = material;
                if (glm::compMax(material->emittance) > C::EPSILON)
                {
                    mat = std::make_shared<Material>(*material);
                    mat->emittance = glm::dvec3(0.0);
                }
                surfaces.push_back(std::make_shared<Surface::Quadric>(s, mat));
            }
            if (transform && !surfaces.empty()) surfaces.back()->transform(*transform);
        }
    }

    computeBoundingBox();

    std::cout << "\nNumber of primitives: " << Format::largeNumber(surfaces.size()) << std::endl;

    if (j.find("bvh") != j.end())
    {
        bvh = std::make_shared<BVH>(BB_, surfaces, j.at("bvh"));
    }

    generateEmissives();
}

Intersection Scene::intersect(const Ray& ray) const
{
    Intersection intersection;

    if (bvh)
    {
        intersection = bvh->intersect(ray);
    }
    else
    {
        for (const auto& s : surfaces)
        {
            Intersection t_intersection;
            if (s->intersect(ray, t_intersection))
            {
                if (t_intersection.t < intersection.t)
                {
                    intersection = t_intersection;
                    intersection.surface = s;
                }
            }
        }
    }

    return intersection;
}

void Scene::generateEmissives()
{
    for (const auto& surface : surfaces)
    {
        if (surface->material->emissive)
        {
            emissives.push_back(surface);
        }
    }

    // Sort emissives based on importance (flux) to reduce the 
    // number of iterations needed to select a random emissive.
    std::sort(emissives.begin(), emissives.end(),
        [](const auto& a, const auto& b)
        {
            return glm::compMax(a->material->emittance) > glm::compMax(b->material->emittance);
        }
    );
    
    double cumulative_max_flux = 0.0;
    for (const auto& emissive : emissives)
    {
        cumulative_max_flux += glm::compMax(emissive->material->emittance);
        cumulative_emissives_importance.push_back(cumulative_max_flux);
        emissive->material->emittance /= emissive->area(); // flux to radiosity
    }

    for (auto& ei : cumulative_emissives_importance)
    {
        ei /= cumulative_max_flux;
    }
}

void Scene::computeBoundingBox()
{
    for (const auto& surface : surfaces)
    {
        BB_.merge(surface->BB());
    }
}

glm::dvec3 Scene::skyColor(const Ray& ray) const
{
    double fy = (1.0 + std::asin(glm::dot(glm::dvec3(0.0, 1.0, 0.0), ray.direction)) / C::PI) / 2.0;
    return glm::mix(glm::dvec3(1.0, 0.5, 0.0), glm::dvec3(0.0, 0.5, 1.0), fy);
}

std::shared_ptr<Surface::Base> Scene::selectLight(double u, double& select_probability) const
{
    size_t emissive_idx = Sampling::weightedIdx(u, cumulative_emissives_importance);

    select_probability = cumulative_emissives_importance[emissive_idx];
    if (emissive_idx > 0)
    {
        select_probability -= cumulative_emissives_importance[emissive_idx - 1];
    }

    return emissives[emissive_idx];
}

void Scene::parseOBJ(const std::filesystem::path &path,
                     std::vector<glm::dvec3> &vertices,
                     std::vector<glm::dvec3> &normals,
                     std::vector<std::vector<size_t>> &triangles_v,
                     std::vector<std::vector<size_t>> &triangles_vt,
                     std::vector<std::vector<size_t>> &triangles_vn) const
{
    if (!std::filesystem::exists(path))
    {
        std::cout << std::endl << path.string() << " not found.\n";
        return;
    }

    std::ifstream file(path);

    auto isNumber = [](const std::string &s) 
    {
        return !s.empty() && std::all_of(s.begin(), s.end(), ::isdigit);
    };

    std::string line;
    while (std::getline(file, line))
    {
        std::stringstream ss(line);
        std::string line_type;
        ss >> line_type;

        if (line_type == "v")
        {
            glm::dvec3 v;
            ss >> v.x >> v.y >> v.z;

            vertices.push_back(v);
        }
        if (line_type == "vn")
        {
            glm::dvec3 vn;
            ss >> vn.x >> vn.y >> vn.z;

            normals.push_back(vn);
        }
        else if (line_type == "f")
        {
            std::vector<size_t> triangle_v, triangle_vt, triangle_vn;
            for (int i = 0; i < 3; i++)
            {
                std::string element;
                ss >> element;
                std::stringstream ss_f(element);

                std::vector<size_t> idxs;
                while (ss_f.good())
                {
                    if (ss_f.peek() == '-')
                    {
                        throw std::runtime_error("OBJ files with negative offsets are not supported.");
                    }
                    std::string idx;
                    std::getline(ss_f, idx, '/');
                    idxs.push_back(isNumber(idx) ? std::stoull(idx) : 0);
                }

                if (idxs.size() == 1)
                {
                    triangle_v.push_back(idxs[0] - 1);
                }
                else if (idxs.size() == 2)
                {
                    triangle_v.push_back(idxs[0] - 1);
                    triangle_vt.push_back(idxs[1] - 1);
                }
                else if (idxs.size() == 3)
                {
                    triangle_v.push_back(idxs[0] - 1);
                    if (idxs[1]) triangle_vt.push_back(idxs[1] - 1);
                    triangle_vn.push_back(idxs[2] - 1);
                }
            }
            if (triangle_v.size() == 3) triangles_v.push_back(triangle_v);
            if (triangle_vt.size() == 3) triangles_vt.push_back(triangle_vt);
            if (triangle_vn.size() == 3) triangles_vn.push_back(triangle_vn);
        }
    }

    file.close();
}

void Scene::generateVertexNormals(std::vector<glm::dvec3> &normals,
                                  const std::vector<glm::dvec3> &vertices,
                                  const std::vector<std::vector<size_t>> &triangles) const
{
    normals.resize(vertices.size(), glm::dvec3(0.0));

    auto angleBetween = [](const auto& v0, const auto& v1)
    {
        return std::acos(glm::dot(glm::normalize(v0), glm::normalize(v1)));
    };

    for (const auto &t : triangles)
    {
        const auto &v0 = vertices.at(t.at(0));
        const auto &v1 = vertices.at(t.at(1));
        const auto &v2 = vertices.at(t.at(2));

        auto triangle = Surface::Triangle(v0, v1, v2, nullptr);

        glm::dvec3 area_weighted_normal = triangle.normal() * triangle.area();

        normals.at(t.at(0)) += area_weighted_normal * angleBetween(v0 - v1, v0 - v2);
        normals.at(t.at(1)) += area_weighted_normal * angleBetween(v1 - v0, v1 - v2);
        normals.at(t.at(2)) += area_weighted_normal * angleBetween(v2 - v0, v2 - v1);
    }

    for (auto &n : normals)
    {
        n = glm::normalize(n);
    }
}

std::filesystem::path Scene::path = std::filesystem::current_path() / "scenes";