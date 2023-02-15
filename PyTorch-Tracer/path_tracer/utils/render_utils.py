import torch
from torch import Tensor


def get_coords_multisample(
    coords: Tensor,
    spp: int,
    jitter: str,
) -> Tensor:
    """Get multiple samples per coordinate"""
    coords = torch.repeat_interleave(coords, spp, dim=0)
    if spp > 1 and jitter == "uniform":
        coords += torch.rand_like(coords) - 0.5

    return coords
