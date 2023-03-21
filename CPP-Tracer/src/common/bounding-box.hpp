#pragma once

#include <glm/vec3.hpp>
#include "../ray/ray.hpp"

struct BoundingBox
{
    BoundingBox() = default;
    BoundingBox(const glm::dvec3 min, const glm::dvec3 max) 
        : min(min), max(max) { }

    bool intersect(const Ray &ray, double &t) const;
    [[nodiscard]] bool contains(const glm::dvec3 &p) const;
    [[nodiscard]] glm::dvec3 dimensions() const;
    [[nodiscard]] glm::dvec3 centroid() const;
    [[nodiscard]] double area() const;
    [[nodiscard]] double distance2(const glm::dvec3 &p) const;
    [[nodiscard]] double max_distance2(const glm::dvec3& p) const;
    void merge(const BoundingBox &BB);
    void merge(const glm::dvec3 &p);
    [[nodiscard]] bool valid() const;

    glm::dvec3 min = glm::dvec3(std::numeric_limits<double>::max());
    glm::dvec3 max = glm::dvec3(std::numeric_limits<double>::lowest());
};
