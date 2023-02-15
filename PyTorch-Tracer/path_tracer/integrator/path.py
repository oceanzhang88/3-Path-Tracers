import logging

import torch
from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator, integrator_registry

logger = logging.getLogger(__name__)


class PathIntegrator(Integrator):
    def __init__(self, max_path_length: int, cont_prob: float, enable_emitter_sample: bool, mis: bool) -> None:
        """A path tracer implementation

        enable_emitter_sample: by default this integrator is brute-force. If set, it performs next event estimation.
        mis: requires enable_emitter_sample. When set, enables importance sampling.
        """
        super().__init__()
        self.max_path_length = max_path_length
        self.cont_prob = cont_prob
        self.enable_emitter_sample = enable_emitter_sample
        self.mis = mis

    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        result = torch.zeros_like(rays_d)
        # TODO:: implement the path tracer
        return result


integrator_registry.add("path", PathIntegrator)
