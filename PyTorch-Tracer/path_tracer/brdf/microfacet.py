import torch
from torch import Tensor

from path_tracer.brdf import Brdf, BrdfQuery, brdf_registry


class MicrofacetBrdf(Brdf):
    def __init__(self, color: list[float], roughness: float, ext_ior: float, int_ior: float) -> None:
        super().__init__()

        assert len(color) == 3, "color should be RGB values"
        assert all(0 <= v <= 1 for v in color), "color must be in range [0, 1]"
        assert 0 < roughness < 1, "roughness must be in range (0, 1)"

        self.color = torch.tensor(color, dtype=torch.float32).view(1, 3)
        self.roughness = roughness
        self.ks = 1 - max(color)
        self.ext_ior = ext_ior
        self.int_ior = int_ior

    def sample(self, query: BrdfQuery) -> BrdfQuery:
        wo = query.wo

        # TODO:: sample the incident directions
        wi = torch.zeros_like(wo)

        # Use eval to set sampled values and pdf
        query.wi = wi
        self.eval(query, is_sample=True)

        return query

    def eval(self, query: BrdfQuery, is_sample: bool = False) -> BrdfQuery:
        wi = query.wi
        wo = query.wo
        albedo = self.color.to(wo.device)
        roughness = self.roughness

        # ignore samples that cross boundary
        valid = (wi[:, 2] > 0) & (wo[:, 2] > 0)

        # set place holders
        values = torch.zeros_like(wo)
        pdf = torch.zeros_like(wo[..., :1])

        query.values = values
        query.pdf = pdf.view(-1)
        query.is_specular = torch.zeros_like(wi[:, 0], dtype=torch.bool)

        if torch.sum(valid) == 0:
            return query

        # compute for valid samples only
        values[valid] = microfacet_eval(wi[valid], wo[valid], self.ks, albedo, roughness, self.ext_ior, self.int_ior)
        pdf[valid] = microfacet_pdf(wi[valid], wo[valid], self.ks, roughness)

        # for BRDF sampling, compute values / pdf * cos(theta)
        if is_sample:
            values[valid] *= wi[valid, 2:] / pdf[valid]

        return query


def microfacet_eval(wi: Tensor, wo: Tensor, ks: Tensor, albedo: Tensor, roughness: float, ext_ior: float, int_ior: float) -> Tensor:
    """Evaluate the microfacet BRDF

    The returned Tensor should have shape (N, 3)
    """
    # TODO:: complete the implementation
    return torch.zeros_like(wi)


def microfacet_pdf(wi: Tensor, wo: Tensor, ks: Tensor, roughness: Tensor) -> Tensor:
    """Compute pdf values of the microfacet BRDF

    The returned Tensor should have shape (N, 1)
    """
    # TODO:: complete the implementation
    return torch.zeros_like(wi[:, 0:1])


brdf_registry.add("microfacet", MicrofacetBrdf)
