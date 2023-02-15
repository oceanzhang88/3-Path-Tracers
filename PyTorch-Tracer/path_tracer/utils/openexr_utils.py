import array

import Imath
import numpy as np
import OpenEXR
import torch


def read_openexr(exr_path, channels, scale: float = 1) -> torch.Tensor:
    """
    See: https://excamera.com/articles/26/doc/openexr.html
    """
    file = OpenEXR.InputFile(exr_path)
    dw = file.header()['dataWindow']

    channels = file.channels(channels, Imath.PixelType(Imath.PixelType.FLOAT))
    result = [np.frombuffer(ch, dtype=np.float32).reshape(dw.max.y - dw.min.y + 1, -1) for ch in channels]

    if len(result) == 1:
        result = result[0]
    else:
        result = np.dstack(result)

    return torch.from_numpy(result)


def write_openexr(file, image: torch.Tensor, channels: str):
    H, W = image.shape[:2]
    exr = OpenEXR.OutputFile(str(file), OpenEXR.Header(W, H))

    data = {}
    for ch in range(len(channels)):
        data[channels[ch]] = array.array('f', image[..., ch].reshape([-1])).tobytes()

    exr.writePixels(data)
    exr.close()
