#pragma once

#include <glm/vec2.hpp>
#include <glm/vec3.hpp>
#include <nlohmann/json.hpp>

struct ComplexIOR;

class Material
{
public:
    Material()
    {
        roughness = 0.0;
        specular_roughness = 0.0;
        ior = -1.0;
        complex_ior = nullptr;
        transparency = 0.0;
        perfect_mirror = false;
        reflectance_color = glm::dvec3(1.0);
        specular_reflectance_color = glm::dvec3(1.0);
        emittance_color = glm::dvec3(0.0);
        transmittance_color = glm::dvec3(1.0);

        computeProperties();
    }

    glm::dvec3 diffuseReflection(const glm::dvec3& i, const glm::dvec3& o, double& PDF) const;
    glm::dvec3 specularReflection(const glm::dvec3& wi, const glm::dvec3& wo, double& PDF) const;
    glm::dvec3 specularTransmission(const glm::dvec3& wi, const glm::dvec3& wo, double n1, 
                                    double n2, double& PDF, bool inside, bool flux) const;

    [[nodiscard]] glm::dvec3 visibleMicrofacet(double u, double v, const glm::dvec3& o) const;

    void computeProperties();

    glm::dvec3 reflectance_color{}, specular_reflectance_color{}, transmittance_color{}, emittance_color{};
    double roughness, specular_roughness, ior, transparency;
    std::shared_ptr<ComplexIOR> complex_ior;

    bool rough{}, rough_specular{}, opaque{}, emissive{}, dirac_delta{};

    // Represents ior = infinity -> fresnel factor = 1.0 -> all rays specularly reflected
    bool perfect_mirror;

private:
    [[nodiscard]] glm::dvec3 lambertian() const;
    [[nodiscard]] glm::dvec3 OrenNayar(const glm::dvec3& wi, const glm::dvec3& wo) const;

    // Pre-computed Oren-Nayar variables.
    double A{}, B{};

    // Specular roughness
    glm::dvec2 a{};
};

void from_json(const nlohmann::json &j, Material &m);

namespace std
{
    void from_json(const nlohmann::json &j, shared_ptr<Material> &m);
}