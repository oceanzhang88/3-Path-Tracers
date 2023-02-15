from typing import Optional

import torch

from path_tracer.emitter import Emitter, EmitterQuery, emitter_registry
from path_tracer.geometry import Geometry


class AreaLight(Emitter):
    def __init__(self, radiance: list[int], geometry: Geometry, i_primitive: int, i_emitter: int) -> None:
        """Area light implementation

        radiance: energy of this light source
        geometry: the scene geometry
        i_primitive: the index of the geometry primitive (e.g. mesh) this emitter is attached to
        i_emitter: the index of this emitter in all emitters
        """

        super().__init__(geometry, i_primitive, i_emitter)

        assert len(radiance) == 3, "radiance should be RGB values"

        self.radiance = torch.tensor(radiance, dtype=torch.float32).view(1, 3)

    def sample(self, n_samples: int, device: str) -> EmitterQuery:
        """Sample points from the area light"""
        # TODO:: sample a point from the mesh of this emitter
        # return an EmitterQuery with points, normals, and pdf set correctly
        # Hint: see Geometry.uniform_sample
        return None

    def pos_pdf(self, query: EmitterQuery) -> EmitterQuery:
        """Position pdf of points from the area light"""
        # TODO:: given an EmitterQuery with points already set,
        # compute the PDF of sampling these points, and set query.pdf
        return query

    def le(self, query: EmitterQuery, geometry: Optional[Geometry]) -> EmitterQuery:
        """Compute the Le term

        If geometry is not None, check if the points and targets are mutually visible
        """
        # TODO:: given an EmitterQuery with points, normals, targets, and d_target_point set,
        # compute the Le term from points to targets, and set query.le
        # also, set query.mask to indicate which targets are lid
        return query


emitter_registry.add("area", AreaLight)
