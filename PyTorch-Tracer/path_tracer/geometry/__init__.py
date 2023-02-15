from abc import ABC, abstractmethod
from dataclasses import dataclass

import torch
from torch import Tensor

from path_tracer.utils.import_utils import import_children
from path_tracer.utils.registry_utils import Registry


@dataclass
class GeometryOutput:
    # (N, ) boolean tensor indicating whether ray hits
    mask: Tensor
    # (N, 3) intersection points
    points: Tensor
    # (N, 3) normals of triangles
    geo_normals: Tensor
    # (N, 3) interpolated vertex normals
    sh_normals: Tensor
    # (N,) indices of BRDF in scene
    brdf_i: Tensor
    # (N, 3) input rays of query
    rays_o: Tensor
    rays_d: Tensor


class Geometry(ABC):
    def __init__(self) -> None:
        super().__init__()
        self._emitters_idx: Tensor = None

    @property
    def emitters_idx(self) -> Tensor:
        if self._emitters_idx is None:
            self._emitters_idx = torch.ones(len(self), dtype=torch.int64) * -1
        return self._emitters_idx

    @abstractmethod
    def ray_intersect(self, rays_o: Tensor, rays_d: Tensor) -> GeometryOutput:
        """
        rays_o: (N, 3) ray origins
        rays_d: (N, 3) ray directions
        """
        raise NotImplementedError()

    @abstractmethod
    def __len__(self) -> int:
        """Get the number of geometry primitives, each has an associated BRDF"""
        raise NotImplementedError()

    def uniform_sample(self, i_primitive: int, n_samples: int, device: str) -> tuple[Tensor, Tensor]:
        """Uniformly sample points from the speicifed primitive.

        i_primitive: which primitive to sample from
        n_samples: number of samples
        device: device to put the returned tensors on

        Returns: [points, normals], two (N, 3) tensors
        """
        raise NotImplementedError()

    def uniform_sample_pos_pdf(self, i_primitive: int) -> float:
        """Compute the positional pdf of points sampled from the specified primitive.
        No points input because sampling is uniform.

        Returns: float, the pdf value
        """
        raise NotImplementedError()


geometry_registry = Registry("geometry", Geometry)
import_children(__file__, __name__)
