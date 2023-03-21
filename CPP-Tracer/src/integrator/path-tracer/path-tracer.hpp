#pragma once

#include <nlohmann/json.hpp>
#include <glm/vec3.hpp>

#include "../integrator.hpp"

class PathTracer : public Integrator
{
public:
    explicit PathTracer(const nlohmann::json& j) : Integrator(j) { }

    glm::dvec3 sampleRay(Ray ray) override;
};
