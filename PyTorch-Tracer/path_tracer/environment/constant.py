import torch
from torch import Tensor

from path_tracer.environment import Environment, environment_registry


class ConstantEnvironment(Environment):
    def __init__(self, color: list[float]) -> None:
        super().__init__()

        assert len(color) == 3, "color should be RGB values"

        self.color = torch.tensor(color, dtype=torch.float32).view(1, 3)

    def sample(self, rays_d: Tensor) -> Tensor:
        return self.color.expand_as(rays_d).to(rays_d.device)


environment_registry.add("constant", ConstantEnvironment)
