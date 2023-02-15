"""See Assignment 2 descriptions"""

from typing import Union

import torch
from torch import Tensor


def sample_uniform_square(uv: Tensor) -> Tensor:
    return uv * 2 - 1


def pdf_uniform_square(p: Tensor) -> Tensor:
    return torch.ones_like(p[:, 0]) / 4


def sample_tent(uv: Tensor) -> Tensor:
    def sample_tent_1d(u: Tensor) -> Tensor:
        return None

    return torch.stack([sample_tent_1d(uv[:, 0]), sample_tent_1d(uv[:, 1])], dim=1)


def pdf_tent(p: Tensor) -> Tensor:
    return None


def sample_uniform_disk(uv: Tensor) -> Tensor:
    r = None
    theta = None
    return torch.stack([r * torch.cos(theta), r * torch.sin(theta)], dim=1)


def pdf_uniform_disk(p: Tensor) -> Tensor:
    return None


def sample_uniform_sphere(uv: Tensor) -> Tensor:
    theta = None
    phi = None
    return torch.stack([
        torch.sin(theta) * torch.cos(phi),
        torch.sin(theta) * torch.sin(phi),
        torch.cos(theta),
    ], dim=1)


def pdf_uniform_sphere(p: Tensor) -> Tensor:
    return None


def sample_uniform_hemisphere(uv: Tensor) -> Tensor:
    theta = None
    phi = None
    return torch.stack([
        torch.sin(theta) * torch.cos(phi),
        torch.sin(theta) * torch.sin(phi),
        torch.cos(theta),
    ], dim=1)


def pdf_uniform_hemisphere(p: Tensor) -> Tensor:
    return None


def sample_cosine_hemisphere(uv: Tensor) -> Tensor:
    return None


def pdf_cosine_hemisphere(p: Tensor) -> Tensor:
    return None


def sample_beckmann(uv: Tensor, alpha: Union[Tensor, float]) -> Tensor:
    return None


def pdf_beckmann(p: Tensor, alpha: Union[Tensor, float]) -> Tensor:
    return None
