from typing import Optional

import torch
from torch import Tensor

from path_tracer.brdf import Brdf, BrdfQuery
from path_tracer.camera import Camera
from path_tracer.emitter import Emitter
from path_tracer.environment import Environment
from path_tracer.geometry import Geometry
from path_tracer.utils.coords_utils import LocalFrames


class Scene:
    def __init__(
        self,
        geometry: Geometry,
        brdf: list[Brdf],
        camera: Camera,
        environment: Optional[Environment],
        emitters: list[Emitter],
    ) -> None:
        self.geometry = geometry
        self.brdf = brdf
        self.camera = camera
        self.environemt = environment
        self.emitters = emitters

    def sample_brdf(self, wo: Tensor, normals: Tensor, brdf_i: Tensor) -> BrdfQuery:
        """A helper function that takes care of BRDF sampling calls for you.

        wo: (N, 3) outgoing directions, in world space
        normals: (N, 3) surface normals
        brdf_i: (N,) indices of BRDF instances in the scene
        """
        frames = LocalFrames(normals)
        wo_local = frames.to_local(wo)

        result = BrdfQuery(
            wo,
            normals,
            wi=torch.zeros_like(wo),
            values=torch.zeros_like(wo),
            pdf=torch.zeros_like(wo[..., 0]),
            is_specular=torch.zeros_like(wo[..., 0], dtype=torch.bool),
        )

        for i in range(len(self.brdf)):
            brdf = self.brdf[i]
            mask = brdf_i == i

            if torch.sum(mask) == 0:
                continue

            batch = brdf.sample(BrdfQuery(
                wo_local[mask],
                normals[mask],
            ))

            result.wi[mask] = batch.wi
            result.values[mask] = batch.values
            result.pdf[mask] = batch.pdf
            result.is_specular[mask] = batch.is_specular

        result.wi = frames.to_world(result.wi)
        return result

    def eval_brdf(self, wo: Tensor, normals: Tensor, wi: Tensor, brdf_i: Tensor) -> BrdfQuery:
        """A helper function that takes care of BRDF evaluate calls for you.

        wo: (N, 3) outgoing directions, in world space
        normals: (N, 3) surface normals
        brdf_i: (N,) indices of BRDF instances in the scene
        """
        frames = LocalFrames(normals)
        wo_local = frames.to_local(wo)
        wi_local = frames.to_local(wi)

        result = BrdfQuery(
            wo,
            normals,
            wi=wi,
            values=torch.zeros_like(wo),
            pdf=torch.zeros_like(wo[..., 0]),
            is_specular=torch.zeros_like(wo[..., 0], dtype=torch.bool),
        )

        for i in range(len(self.brdf)):
            brdf = self.brdf[i]
            mask = brdf_i == i

            if torch.sum(mask) == 0:
                continue

            batch = brdf.eval(BrdfQuery(
                wo_local[mask],
                normals[mask],
                wi=wi_local[mask]
            ))

            result.values[mask] = batch.values
            result.pdf[mask] = batch.pdf
            result.is_specular[mask] = batch.is_specular

        return result

    def get_albedo_brdf(self, brdf_i: Tensor) -> Tensor:
        """A helper function to call the BRDF get_albedo functions

        brdf_i: (N,) indices of BRDF instances in the scene
        returns: (N, 3) albedo color of each queried BRDF
        """
        result = torch.zeros(len(brdf_i), 3, device=brdf_i.device)
        for i in range(len(self.brdf)):
            brdf = self.brdf[i]
            mask = brdf_i == i

            if torch.sum(mask) == 0:
                continue

            result[mask] = brdf.get_albedo(brdf_i.device)

        return result
