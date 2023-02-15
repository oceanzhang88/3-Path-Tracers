import logging

import torch
from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator, integrator_registry

logger = logging.getLogger(__name__)


class WhittedIntegrator(Integrator):
    def __init__(self, max_path_length: int, cont_prob: float) -> None:
        super().__init__()
        self.max_path_length = max_path_length
        self.cont_prob = cont_prob

    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        result = torch.zeros_like(rays_d)

        # Whitted: keep track of the 1/p multiplications
        throughput = torch.ones_like(rays_d)

        # Note: you can also start by initializing the active_indices with all indices,
        # and move the first ray_intersect inside the loop.
        # Doing so may or may not simplify the implementaion, it's up to your preferences.

        # start by shooting the rays into the scene
        geo_out = scene.geometry.ray_intersect(rays_o, rays_d)

        # indices of rays that are being traced
        # these are indices in the inputs, for indexing result and throughput
        active_indices = torch.nonzero(geo_out.mask)[:, 0]  # (N, 1) -> (N,)

        # Whitted: we keep tracing the rays that hit specular surfaces,
        # until they hit a diffuse surface (so we sample an emitter),
        # or goes into the void (result is zero),
        # or is terminated by Russian-roulette (result is zero)
        for i_path in range(self.max_path_length):
            if len(active_indices) == 0:
                break

            # TODO:: implement Distribution Ray Tracing

            # Hints (you don't have to follow this)

            # 1. Check if a ray hits an emitter

            # 2. Sample a point on emitters for all the remaining points
            # First, choose an emitter for every point (see np.random.choice)
            # Then, query each emitter with the assigned points
            # Whitted: only process the points that hit a diffuse surface

            # Whitted: now, process the points that hit a specular surface
            if i_path > 3:
                # Do Russian-roulette after at least 3 bounces
                pass

            # Whitted: remove this break
            break

        return result


integrator_registry.add("whitted", WhittedIntegrator)
