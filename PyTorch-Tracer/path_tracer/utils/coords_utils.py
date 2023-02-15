import torch
from torch import Tensor

from path_tracer.utils.tensor_utils import dot


def find_tangents(normals: Tensor) -> tuple[Tensor, Tensor]:
    # adapted from nori
    x = normals[:, 0]
    y = normals[:, 1]
    z = normals[:, 2]
    z2 = z*z

    bt = torch.zeros_like(normals)

    mask = x.abs() > y.abs()
    inv_len = 1 / torch.sqrt(x[mask]*x[mask] + z2[mask])
    bt[mask, 0] = z[mask] * inv_len
    bt[mask, 2] = -x[mask] * inv_len

    mask = ~mask
    inv_len = 1 / torch.sqrt(y[mask]*y[mask] + z2[mask])
    bt[mask, 1] = z[mask] * inv_len
    bt[mask, 2] = -y[mask] * inv_len

    t = torch.cross(bt, normals, dim=-1)
    return t, bt


def to_world(v: Tensor, normals: Tensor, t: Tensor, bt: Tensor) -> Tensor:
    return t * v[:, 0:1] + bt * v[:, 1:2] + normals * v[:, 2:3]


def to_local(v: Tensor, normals: Tensor, t: Tensor, bt: Tensor) -> Tensor:
    return torch.cat([
        dot(v, t),
        dot(v, bt),
        dot(v, normals),
    ], dim=-1)


class LocalFrames:
    """Utility class to convert directions between the world space and the local space defined by the normals"""

    def __init__(self, normals: Tensor) -> None:
        self.normals = normals
        self.tangent, self.bi_tangent = find_tangents(normals)

    def to_world(self, v: Tensor) -> Tensor:
        return to_world(v, self.normals, self.tangent, self.bi_tangent)

    def to_local(self, v: Tensor) -> Tensor:
        return to_local(v, self.normals, self.tangent, self.bi_tangent)
