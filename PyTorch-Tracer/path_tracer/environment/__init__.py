from abc import ABC, abstractmethod

from torch import Tensor

from path_tracer.utils.import_utils import import_children
from path_tracer.utils.registry_utils import Registry


class Environment(ABC):
    @abstractmethod
    def sample(self, rays_d: Tensor) -> Tensor:
        """Sample from the environment

        rays_d: (N, 3) ray directions

        returns: (N, 3) color
        """
        raise NotImplementedError()


environment_registry = Registry("environment", Environment)
import_children(__file__, __name__)
