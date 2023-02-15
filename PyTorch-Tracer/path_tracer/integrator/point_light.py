import logging

import torch
from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator, integrator_registry

logger = logging.getLogger(__name__)


class PointLightIntegrator(Integrator):
    def __init__(self, position: list[float], energy: list[float]) -> None:
        super().__init__()
        assert len(position) == 3, "position must be [x, y, z]"
        assert len(energy) == 3, "energy must be [r, g, b]"

        self.position = torch.tensor(position, dtype=torch.float32).view(1, 3)
        self.energy = torch.tensor(energy, dtype=torch.float32).view(1, 3)

    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        result = torch.zeros_like(rays_o)
        # TODO:: implement the point light integrator
        return result


integrator_registry.add("point", PointLightIntegrator)
