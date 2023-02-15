import numpy as np
import torch
from torch import Tensor

from path_tracer.camera import Camera, camera_registry


class PerspectiveCamera(Camera):
    def __init__(self,
                 width: int,
                 height: int,
                 fov: float,
                 c2w: list[list[float]],
                 ) -> None:
        """
        hwf: [H, W, focal] of image (at original scale)
        c2w: (3, 4) array of camera-to-world transform
        render_hw: [H, W] of rendering
        """
        super().__init__()

        H, W = height, width
        focal = 0.5 * W / np.tan(0.5 * np.deg2rad(fov))

        self.hwf = [H, W, focal]

        # image-to-camera space transform
        self.i2c = torch.tensor([
            [1/focal, 0, -0.5*W/focal],
            [0, 1/focal, -0.5*H/focal],
            [0, 0, 1],
        ], dtype=torch.float64)

        # camera-to-world space transform
        self.c2w = torch.tensor(c2w, dtype=torch.float32)

        c2w_shape = str(list(self.c2w.shape))
        assert c2w_shape == "[3, 4]", f"c2w matrix should have shape (3, 4), but got {c2w_shape}"

    def image_to_camera(self, coords: Tensor) -> Tensor:
        coords = coords.to(torch.float64)
        coords = torch.cat([coords, torch.ones_like(coords[..., 0:1])], dim=1)  # homogeneous coords

        rays_d = self.i2c[None] @ coords[..., None]  # (1, 3, 3) @ (N, 3, 1) -> (N, 3, 1)
        rays_d = rays_d[..., 0].to(torch.float32)  # convert to (N, 3) and float32

        # NeRF coords system
        rays_d[:, 1:3] = -rays_d[:, 1:3]

        return rays_d

    def camera_to_world(self, rays_o: Tensor, rays_d: Tensor) -> tuple[Tensor, Tensor]:
        c2w = self.c2w
        rotation = c2w[:3, :3][None]  # (1, 3, 3)
        translation = c2w[:, 3:][None]  # (1, 3, 1)

        rays_d = rotation @ rays_d[..., None]
        rays_o = rotation @ rays_o[..., None] + translation

        return rays_o[..., 0], rays_d[..., 0]

    def image_to_rays(self, coords: Tensor) -> tuple[Tensor, Tensor]:
        rays_d = self.image_to_camera(coords)
        rays_o = torch.zeros_like(rays_d)

        return self.camera_to_world(rays_o, rays_d)


camera_registry.add("perspective", PerspectiveCamera)
