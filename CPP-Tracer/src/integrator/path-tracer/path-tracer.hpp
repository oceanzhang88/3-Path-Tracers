#pragma once

#include <nlohmann/json.hpp>
#include <glm/vec3.hpp>

#include "../integrator.hpp"

class PathTracer : public Integrator
{
public:
    PathTracer(const nlohmann::json& j) : Integrator(j) { }

    virtual glm::dvec3 sampleRay(Ray ray);
};
