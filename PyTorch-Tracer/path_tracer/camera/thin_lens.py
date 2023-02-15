from torch import Tensor

from path_tracer.camera import Camera, camera_registry
from path_tracer.camera.perspective import PerspectiveCamera


class ThinLensCamera(Camera):
    def __init__(self,
                 width: int,
                 height: int,
                 fov: float,
                 c2w: list[list[float]],
                 aperture: float,
                 focal_distance: float,
                 ) -> None:
        self.camera = PerspectiveCamera(width, height, fov, c2w)
        self.aperture = aperture
        self.focal_distance = focal_distance

    def image_to_rays(self, coords: Tensor) -> tuple[Tensor, Tensor]:
        # TODO:: implement the thin lens camera, based on the perspective camera
        # Hint: transform the camera-space rays before converting them to world-space
        pass


camera_registry.add("thin", ThinLensCamera)
