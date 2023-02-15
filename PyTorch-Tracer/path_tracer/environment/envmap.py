from torch import Tensor

from path_tracer.environment import Environment, environment_registry
from path_tracer.utils.equirect_utils import sample_panoramic_image
from path_tracer.utils.openexr_utils import read_openexr


class EnvMapEnvironment(Environment):
    def __init__(self, path: str) -> None:
        super().__init__()
        self.envmap = read_openexr(path, "RGB").permute(2, 0, 1)
        self.envmap.clamp_min_(0)

    def sample(self, rays_d: Tensor) -> Tensor:
        return sample_panoramic_image(rays_d, self.envmap.to(rays_d.device))


environment_registry.add("envmap", EnvMapEnvironment)
