import torch
from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator, integrator_registry


class AlbedoIntegrator(Integrator):
    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        result = torch.zeros_like(rays_o)
        geometry = scene.geometry.ray_intersect(rays_o, rays_d)

        mask = geometry.mask
        result[mask] = scene.get_albedo_brdf(geometry.brdf_i[mask])

        return result

    def need_tonemap(self) -> None:
        return False


integrator_registry.add("albedo", AlbedoIntegrator)
