import torch
from path_tracer.brdf import Brdf, BrdfQuery, brdf_registry


class DielectricBrdf(Brdf):
    def __init__(self, ext_ior: float, int_ior: float) -> None:
        super().__init__()
        self.ext_ior = ext_ior
        self.int_ior = int_ior

    def sample(self, query: BrdfQuery) -> BrdfQuery:
        wo = query.wo

        # TODO:: sample wi according to Fresnel
        wi = torch.zeros_like(wo)

        return query.output(
            wi,
            torch.ones_like(wo),
            torch.zeros_like(wo[:, 0]),
            torch.ones_like(wi[:, 0], dtype=torch.bool),
        )

    def eval(self, query: BrdfQuery) -> BrdfQuery:
        # Discrete BRDFs evaluate to zero
        wo = query.wo
        query.values = torch.zeros_like(wo)
        query.pdf = torch.zeros_like(wo[:, 0])
        query.is_specular = torch.ones_like(wo[:, 0], dtype=torch.bool)
        return query


brdf_registry.add("dielectric", DielectricBrdf)
