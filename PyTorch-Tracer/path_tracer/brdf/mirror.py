import torch

from path_tracer.brdf import Brdf, BrdfQuery, brdf_registry


class MirrorBrdf(Brdf):
    def sample(self, query: BrdfQuery) -> BrdfQuery:
        wo = query.wo

        # in local coordinates, normal is (0, 0, 1)
        wi = wo.clone()
        wi[:, 0:2] = -wi[:, 0:2]

        return query.output(
            wi,
            torch.ones_like(wo),
            torch.ones_like(wo[:, 0]),
            torch.ones_like(wi[:, 0], dtype=torch.bool),
        )

    def eval(self, query: BrdfQuery) -> BrdfQuery:
        # Discrete BRDFs evaluate to zero
        wo = query.wo
        query.values = torch.zeros_like(wo)
        query.pdf = torch.zeros_like(wo[:, 0])
        query.is_specular = torch.ones_like(wo[:, 0], dtype=torch.bool)
        return query


brdf_registry.add("mirror", MirrorBrdf)
