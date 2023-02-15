from abc import ABC, abstractmethod

from torch import Tensor

from path_tracer.core.scene import Scene
from path_tracer.utils.import_utils import import_children
from path_tracer.utils.registry_utils import Registry


class Integrator(ABC):
    @abstractmethod
    def render(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> Tensor:
        """Render a batch of rays in the scene.

        rays_o: (N, 3) ray origins
        rays_d: (N, 3) ray directions (not normalized)
        """
        raise NotImplementedError()

    def on_render_ended(self) -> None:
        """Called when render completes.

        You can print some statistics, for example.
        """

    def need_tonemap(self) -> bool:
        """Whether the output from the integrator is in linear space and should be tone-mapped for display"""
        return True

    def init_nerad(self):
        """Initialize neural radiosity network, if the integrator supports"""
        raise NotImplementedError()

    def render_nerad(self, scene: Scene, rays_o: Tensor, rays_d: Tensor) -> tuple[Tensor, Tensor]:
        """Render a batch of rays using neural radiosity method, if the integrator supports"""
        raise NotImplementedError()


integrator_registry = Registry("integrator", Integrator)
import_children(__file__, __name__)
