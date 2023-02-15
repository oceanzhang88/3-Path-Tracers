import torch

from path_tracer.brdf import Brdf, BrdfQuery, brdf_registry
from path_tracer.utils.sampling_utils import (pdf_cosine_hemisphere,
                                              sample_cosine_hemisphere)


class DiffuseBrdf(Brdf):
    def __init__(self, color: list[float]) -> None:
        super().__init__()

        assert len(color) == 3, "color should be RGB values"
        assert all(0 <= v <= 1 for v in color), "color must be in range [0, 1]"

        self.color = torch.tensor(color, dtype=torch.float32).view(1, 3)

    def sample(self, query: BrdfQuery) -> BrdfQuery:
        wo = query.wo
        uv = torch.rand(len(wo), 2, device=wo.device)
        wi = sample_cosine_hemisphere(uv)

        return query.output(
            wi,
            # values / pdf * cos(theta) == values for diffuse BRDF
            self.color.expand(len(wo), -1).to(wo.device),
            pdf_cosine_hemisphere(wi),
            torch.zeros_like(wi[:, 0], dtype=torch.bool),
        )

    def eval(self, query: BrdfQuery) -> BrdfQuery:
        query.values = self.color.expand(len(query.wo), -1).to(query.wo.device) / torch.pi
        query.pdf = pdf_cosine_hemisphere(query.wi)
        query.is_specular = torch.zeros_like(query.wi[:, 0], dtype=torch.bool)

        query.values = query.values.clone()
        mask = (query.wi[:, 2] < 0) | (query.wo[:, 2] < 0)
        query.values[mask] = 0
        query.pdf[mask] = 0

        return query

    def get_albedo(self, device: str) -> torch.Tensor:
        return self.color.to(device)


brdf_registry.add("diffuse", DiffuseBrdf)
