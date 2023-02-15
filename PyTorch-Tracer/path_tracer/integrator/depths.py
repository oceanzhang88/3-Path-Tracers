import torch
from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator, integrator_registry


class DepthsIntegrator(Integrator):
    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        # Depth integrator
        # cast the rays to find the intersection points
        geometry = scene.geometry.ray_intersect(rays_o, rays_d)
        mask = geometry.mask
        t = (geometry.points - rays_o) / rays_d
        t_depth = 1 / t
        t_depth[~mask] = t_depth[~mask] * 0
        t_depth = torch.nan_to_num(t_depth, nan=0.0)
        # return depth
        return t_depth


integrator_registry.add("depths", DepthsIntegrator)
