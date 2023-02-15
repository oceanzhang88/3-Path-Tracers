from abc import ABC, abstractmethod
from dataclasses import dataclass

from torch import Tensor

from path_tracer.geometry import Geometry
from path_tracer.utils.import_utils import import_children
from path_tracer.utils.registry_utils import Registry


@dataclass
class EmitterQuery:
    # (N, 3) points on the emitter (y)
    points: Tensor
    # (N, 3) normals of above points (n_y)
    normals: Tensor
    # (N,) pdf of the emitter sampling these points
    pdf: Tensor = None
    # (N, 3) points to be lit (x)
    targets: Tensor = None
    # (N, 3) computed Le(y, y->x)
    le: Tensor = None
    # (N,) where Le is not zero
    mask: Tensor = None
    # (N, 3) direction (normalized) from targets to points, the integrator should compute and set this
    d_target_point: Tensor = None


class Emitter(ABC):
    def __init__(self, geometry: Geometry, i_primitive: int, i_emitter: int) -> None:
        super().__init__()
        self.geometry = geometry
        self.i_primitive = i_primitive
        geometry.emitters_idx[i_primitive] = i_emitter

    @abstractmethod
    def sample(self, n_samples: int, device: str) -> EmitterQuery:
        raise NotImplementedError()

    @abstractmethod
    def pos_pdf(self, query: EmitterQuery) -> EmitterQuery:
        raise NotImplementedError()

    @abstractmethod
    def le(self, query: EmitterQuery, geometry: Geometry) -> EmitterQuery:
        raise NotImplementedError()


emitter_registry = Registry("emitter", Emitter)
import_children(__file__, __name__)
