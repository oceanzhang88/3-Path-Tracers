from typing import Any, Dict, Optional

import torch
import torch.nn.functional as F
from torch import Tensor


def directions_to_image(directions: Tensor) -> Tensor:
    """ Convert direction vectors to equirectangular pixel locations for sampling

    directions: [N, 3] unit direction vectors

    returns: [N, 2] sampling coordinates in range [-1, 1]
    """
    x = directions[..., 0]
    y = directions[..., 1]
    z = directions[..., 2]
    return torch.stack(
        [
            -torch.atan2(y, x) / torch.pi,
            torch.arccos(z) / torch.pi * 2 - 1,
        ],
        axis=-1,
    ).to(directions.device)


def sample_panoramic_image(
    directions: Tensor,
    image: Tensor,
    grid_sample_args: Optional[Dict[str, Any]] = None,
) -> Tensor:
    """ Sample data from a panoramic image, given direction vectors

    directions: [N, 3]
    image: [C, H, W] data to sample from
    grid_sample_args: passed to torch.nn.functional.grid_sample

    returns: [N, C] sampled points
    """
    coords = directions_to_image(directions)  # [N, 2]
    image = image[None]

    if grid_sample_args is None:
        grid_sample_args = {}
    if "align_corners" not in grid_sample_args:
        grid_sample_args["align_corners"] = True

    sampled = F.grid_sample(
        image,
        coords[None, None],
        **grid_sample_args,
    )  # [1, C, 1, N]

    sampled = sampled[0, :, 0].transpose(0, 1)  # convert to [N, C]

    return sampled
