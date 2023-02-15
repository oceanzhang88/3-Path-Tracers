from abc import ABC, abstractmethod

from torch import Tensor

from path_tracer.utils.import_utils import import_children
from path_tracer.utils.registry_utils import Registry


class Camera(ABC):
    @abstractmethod
    def image_to_rays(self, coords: Tensor) -> tuple[Tensor, Tensor]:
        """Map image coordinates to rays

        coords: (N, 2) image coordinates

        returns: (rays_o, rays_d), tuple of two (N, 3) tensors
        """
        raise NotImplementedError()


camera_registry = Registry("camera", Camera)
import_children(__file__, __name__)
