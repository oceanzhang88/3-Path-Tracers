import torch
from torch import Tensor


def dot(a: Tensor, b: Tensor) -> Tensor:
    """Given two tensors, compute the dot product at last dimension, and keep the dimension.

    a, b: (*, C) tensors
    returns: (*, 1) tensor
    """
    return torch.sum(a * b, dim=-1, keepdim=True)
