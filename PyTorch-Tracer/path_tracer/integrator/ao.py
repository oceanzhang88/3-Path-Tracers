import torch
from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator, integrator_registry


class AmbientOcclusionIntegrator(Integrator):
    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        result = torch.zeros_like(rays_o)
        # TODO:: implement ambient occlusion rendering
        return result


integrator_registry.add("ao", AmbientOcclusionIntegrator)
