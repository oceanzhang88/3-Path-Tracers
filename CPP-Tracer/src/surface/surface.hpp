#pragma once

#include <glm/vec3.hpp>
#include <glm/mat4x4.hpp>
#include <nlohmann/json.hpp>
#include <utility>
#include <utility>

#include "../ray/ray.hpp"
#include "../ray/intersection.hpp"
#include "../common/bounding-box.hpp"
#include "../common/util.hpp"

class Material;

namespace Surface
{
    class Base
    {
    public:
        explicit Base(std::shared_ptr<Material> material)
            : material(std::move(std::move(material))), area_(0) { };

        virtual ~Base() = default;

        virtual bool intersect(const Ray& ray, Intersection& intersection) const = 0;
        virtual glm::dvec3 operator()(double u, double v) const = 0;
        [[nodiscard]] virtual glm::dvec3 normal(const glm::dvec3& pos) const = 0;
        virtual void transform(const Transform &T) = 0;

        [[nodiscard]] virtual glm::dvec3 interpolatedNormal(const glm::dvec2& uv) const
        { 
            return {};
        }

        [[nodiscard]] BoundingBox BB() const
        {
            return BB_;
        }

        [[nodiscard]] double area() const
        {
            return area_;
        }

        std::shared_ptr<Material> material;

    protected:
        virtual void computeArea() = 0;
        virtual void computeBoundingBox() = 0;
        double area_;
        BoundingBox BB_;
    };

    class Sphere : public Base
    {
    public:
        Sphere(double radius, std::shared_ptr<Material> material);

        bool intersect(const Ray& ray, Intersection& intersection) const override;
        glm::dvec3 operator()(double u, double v) const override;
        [[nodiscard]] glm::dvec3 normal(const glm::dvec3& pos) const override;
        void transform(const Transform &T) override;

    protected:
        void computeArea() final;
        void computeBoundingBox() final;

    private:
        glm::dvec3 origin;
        double radius;
    };

    class Triangle : public Base
    {
    public:
        Triangle(const glm::dvec3& v0, const glm::dvec3& v1, const glm::dvec3& v2,
                 std::shared_ptr<Material> material);

        Triangle(const glm::dvec3& v0, const glm::dvec3& v1, const glm::dvec3& v2,
                 const glm::dvec3& n0, const glm::dvec3& n1, const glm::dvec3& n2,
                 std::shared_ptr<Material> material);

        bool intersect(const Ray& ray, Intersection& intersection) const override;

        glm::dvec3 operator()(double u, double v) const override;

        [[nodiscard]] glm::dvec3 normal(const glm::dvec3& pos) const override;

        [[nodiscard]] glm::dvec3 interpolatedNormal(const glm::dvec2& uv) const override;

        void transform(const Transform &T) override;

        [[nodiscard]] glm::dvec3 normal() const;

    protected:
        void computeArea() final;
        void computeBoundingBox() final;
        glm::dvec3 v0, v1, v2;
        const std::unique_ptr<glm::dmat3> N; // vertex normals
        // Pre-computed edges and normal
        glm::dvec3 E1, E2, normal_;
    };

    class Quadric : public Base
    {
    public:
        Quadric(const nlohmann::json &j, std::shared_ptr<Material> material);

        bool intersect(const Ray& ray, Intersection& intersection) const override;
        glm::dvec3 operator()(double u, double v) const override;
        [[nodiscard]] glm::dvec3 normal(const glm::dvec3& pos) const override;
        void transform(const Transform &T) override;

    protected:
        void computeArea() final;
        void computeBoundingBox() final { }

    private:
        glm::dmat4x4 Q{}; // Quadric matrix
        glm::dmat4x3 G{}; // Gradient matrix
    };
}
