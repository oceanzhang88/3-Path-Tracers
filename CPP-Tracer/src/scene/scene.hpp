#pragma once

#include <vector>
#include <memory>
#include <filesystem>

#include <nlohmann/json.hpp>

#include "../ray/ray.hpp"
#include "../ray/intersection.hpp"
#include "../common/bounding-box.hpp"

class BVH;
namespace Surface { class Base; }

class Scene
{
public:
    Scene(const nlohmann::json& j);

    Intersection intersect(const Ray& ray) const;

    void generateEmissives();

    glm::dvec3 skyColor(const Ray& ray) const;

    std::vector<std::shared_ptr<Surface::Base>> surfaces;
    std::vector<std::shared_ptr<Surface::Base>> emissives; // subset of surfaces
    std::vector<double> cumulative_emissives_importance;

    std::shared_ptr<Surface::Base> selectLight(double u, double& select_probability) const;

    BoundingBox BB() const
    {
        return BB_;
    }

    std::shared_ptr<BVH> bvh;

    double ior;

    static std::filesystem::path path;

private:
    BoundingBox BB_;

    void computeBoundingBox();

    void parseOBJ(const std::filesystem::path &path,
                  std::vector<glm::dvec3> &vertices,
                  std::vector<glm::dvec3> &normals,
                  std::vector<std::vector<size_t>> &triangles_v,
                  std::vector<std::vector<size_t>> &triangles_vt,
                  std::vector<std::vector<size_t>> &triangles_vn) const;

    void generateVertexNormals(std::vector<glm::dvec3> &normals,
                               const std::vector<glm::dvec3> &vertices, 
                               const std::vector<std::vector<size_t>> &triangles) const;
};