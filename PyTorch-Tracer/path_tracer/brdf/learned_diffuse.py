import torch
import torch.nn as nn

from path_tracer.brdf import Brdf, BrdfQuery, brdf_registry
from path_tracer.utils.sampling_utils import sample_cosine_hemisphere, pdf_cosine_hemisphere


class LearnedDiffuseBrdf(Brdf, nn.Module):
    def __init__(self) -> None:
        super().__init__()

        # initialize the color to gray
        self.color = nn.Parameter(torch.ones(1, 3, dtype=torch.float32) * 0.5, requires_grad=True)

    def sample(self, query: BrdfQuery) -> BrdfQuery:
        wo = query.wo
        uv = torch.rand(len(wo), 2, device=wo.device)
        wi = sample_cosine_hemisphere(uv)

        return query.output(
            wi,
            torch.sigmoid(self.color).expand(len(wo), -1).to(wo.device),
            pdf_cosine_hemisphere(wi),
            torch.zeros_like(wi[:, 0], dtype=torch.bool),
        )

    def eval(self, query: BrdfQuery) -> BrdfQuery:
        query.values = torch.sigmoid(self.color).expand(len(query.wo), -1).to(query.wo.device) / torch.pi
        query.pdf = pdf_cosine_hemisphere(query.wi)
        query.is_specular = torch.zeros_like(query.wi[:, 0], dtype=torch.bool)

        query.values = query.values.clone()
        mask = (query.wi[:, 2] < 0) | (query.wo[:, 2] < 0)
        query.values[mask] = 0
        query.pdf[mask] = 0

        return query

    def get_albedo(self, device: str) -> torch.Tensor:
        return torch.sigmoid(self.color.to(device))


brdf_registry.add("learned_diffuse", LearnedDiffuseBrdf)
