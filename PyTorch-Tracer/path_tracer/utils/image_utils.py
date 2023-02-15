import os
from pathlib import Path
from typing import Union

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from path_tracer.utils.openexr_utils import read_openexr


def save_image(file: Union[str, os.PathLike], array: np.ndarray, tonemap: bool = True, clip: bool = True):
    """save an np.ndarray as an image file

    array: [H, W, 3], float32, values in [0, 1]
    """
    if tonemap:
        array = tonemap_image(array)
    if clip:
        array = np.clip(array, 0, 1)

    ext = os.path.splitext(file)[1].lower()
    kwargs = {}
    if ext == ".jpg":
        kwargs["quality"] = 95
    elif ext == ".png":
        kwargs["optimize"] = True

    img = Image.fromarray((array * 255).astype(np.uint8))
    img.save(file, **kwargs)


def tonemap_image(img: np.ndarray):
    """Adapted from Nori"""
    img = img.copy()
    small = img < 0.0031308
    img[small] *= 12.92
    img[~small] = 1.055 * np.power(img[~small], 1/2.4) - 0.055
    return img


def scale_array(
    arr: np.ndarray, scale: float, mode="bilinear", align_corners=True
) -> np.ndarray:
    """ Scale an HWC array to [H*scale, W*scale, C] with torch.nn.functional.interpolate
    HW input is also supported.
    """
    is_hw = len(arr.shape) == 2
    if is_hw:
        arr = arr[..., None]

    H, W, C = arr.shape
    arr = np.transpose(arr, [2, 0, 1])  # HWC -> CHW
    arr = torch.from_numpy(arr).view(1, C, H, W)
    arr = F.interpolate(
        arr,
        scale_factor=(scale, scale),
        mode=mode,
        align_corners=align_corners,
        recompute_scale_factor=False,
    )
    arr = arr[0].numpy()

    if is_hw:
        return arr[0]

    arr = np.transpose(arr, [1, 2, 0])
    return arr


def read_image(path: str, scale: float = 1, resample=Image.BILINEAR) -> np.ndarray:
    """Load an image with optional scale, handles EXR and other images

    returns: array with value in [0, 1]
    """
    path: Path = Path(path)
    if path.suffix == ".exr":
        img = read_openexr(str(path), "RGB")
        if scale > 0:
            img = scale_array(img, scale)
        return img

    img = Image.open(path)
    if scale > 0:
        img = img.resize((int(img.width * scale), int(img.height * scale)), resample)
    img = np.array(img).astype(np.float32) / 255
    return img
