#include "ray.hpp"

#include "../common/constexpr-math.hpp"
#include "../sampling/sampling.hpp"
#include "../sampling/sampler.hpp"
#include "../common/constants.hpp"
#include "../material/material.hpp"
#include "interaction.hpp"

Ray::Ray(const glm::dvec3& start, const glm::dvec3& end)
    : start(start), direction(glm::normalize(end - start)), inv_direction(1.0 / direction), medium_ior(1.0) { }

Ray::Ray(const glm::dvec3& start, const glm::dvec3& direction, double medium_ior)
    : start(start), direction(direction), inv_direction(1.0 / direction), medium_ior(medium_ior) { }

Ray::Ray(const Interaction &interaction) :
        depth(interaction.ray.depth + 1), diffuse_depth(interaction.ray.diffuse_depth),
        refraction_scale(interaction.ray.refraction_scale), start(interaction.position),
        refraction_level(interaction.ray.refraction_level), dirac_delta(interaction.impulse_specular)
{
    switch (interaction.type)
    {
        case Interaction::REFLECT:
        {
            glm::dvec3 specular_normal = interaction.specularNormal();
            direction = glm::reflect(interaction.ray.direction, specular_normal);
            medium_ior = interaction.n1;
            start += interaction.normal * C::EPSILON;
            break;
        }
        case Interaction::REFRACT:
        {
            glm::dvec3 specular_normal = interaction.specularNormal();
            double inv_eta = interaction.n1 / interaction.n2;
            double cos_theta = glm::dot(specular_normal, interaction.ray.direction);
            double k = 1.0 - pow2(inv_eta) * (1.0 - pow2(cos_theta)); // 1 - (n1/n2 * sin(theta))^2
            if (k >= 0.0)
            {
                /* SPECULAR REFRACTION */
                direction = inv_eta * interaction.ray.direction - (inv_eta * cos_theta + std::sqrt(k)) * specular_normal;
                medium_ior = interaction.n2;
                start -= interaction.normal * C::EPSILON;
                interaction.inside ? refraction_level-- : refraction_level++;
                refraction_scale *= pow2(1.0 / inv_eta);
                refraction = true;
            }
            else
            {
                /* CRITICAL ANGLE, SPECULAR REFLECTION */
                direction = interaction.ray.direction - specular_normal * cos_theta * 2.0;
                medium_ior = interaction.n1;
                start += interaction.normal * C::EPSILON;
            }
            break;
        }
        case Interaction::DIFFUSE:
        {
            diffuse_depth++;
            auto u = Sampler::get<Dim::BSDF, 2>();
            direction = interaction.shading_cs.from(Sampling::cosWeightedHemi(u[0], u[1]));
            medium_ior = interaction.n1;
            start += interaction.normal * C::EPSILON;
            break;
        }
    }
    inv_direction = 1.0 / direction;
}

glm::dvec3 Ray:: operator()(double t) const
{
    return start + direction * t;
}

RefractionHistory::RefractionHistory(const Ray& ray) :
    iors(1, ray.medium_ior)
{
    iors.reserve(8);
}

void RefractionHistory::update(const Ray& ray)
{
    if (ray.refraction_level > 0)
    {
        if (ray.refraction_level == iors.size())
        {
            iors.push_back(ray.medium_ior);
        }
        else if (ray.refraction_level < iors.size() - 1)
        {
            iors.pop_back();
        }
    }
}

double RefractionHistory::externalIOR(const Ray& ray) const
{
    return iors[std::clamp(ray.refraction_level - 1, 0, (int)iors.size() - 1)];
}