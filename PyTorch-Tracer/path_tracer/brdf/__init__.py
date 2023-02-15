from abc import ABC, abstractmethod
from dataclasses import dataclass

import torch
from torch import Tensor

from path_tracer.utils.import_utils import import_children
from path_tracer.utils.registry_utils import Registry


@dataclass
class BrdfQuery:
    """ This class keeps data for a BRDF query

    For sampling, caller sets wo and normals in local coordinates, and BRDF sets sampled wi, values, pdf, and is_specular.
    Also, sampled values are computed as (eval values) / pdf * cos(theta).

    For eval, caller sets wo, normals and wi. BRDF sets values, pdf, and is_specular.
    """
    wo: Tensor  # (N, 3)
    normals: Tensor  # (N, 3)

    wi: Tensor = None  # (N, 3)
    values: Tensor = None  # (N,)
    pdf: Tensor = None  # (N,)
    is_specular: Tensor = None  # (N,)

    def output(self, wi: Tensor, values: Tensor, pdf: Tensor, is_specular: Tensor) -> "BrdfQuery":
        """Set output of query and return self"""
        self.wi = wi
        self.values = values
        self.pdf = pdf
        self.is_specular = is_specular
        return self


class Brdf(ABC):
    @abstractmethod
    def sample(self, query: BrdfQuery) -> BrdfQuery:
        """Sample the BRDF, modify and return the input object"""
        raise NotImplementedError()

    @abstractmethod
    def eval(self, query: BrdfQuery) -> BrdfQuery:
        """Evaluate the BRDF, modify and return the input object"""
        raise NotImplementedError()

    def get_albedo(self, device: str) -> Tensor:
        """Get the albedo (diffuse) color"""
        return torch.zeros(1, 3, device=device)


brdf_registry = Registry("brdf", Brdf)
import_children(__file__, __name__)
