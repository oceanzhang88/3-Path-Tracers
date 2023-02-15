import logging
from typing import Any, Optional

import numpy as np
import open3d as o3d
import torch
import torch.nn.functional as F
from torch import Tensor

from path_tracer.geometry import Geometry, GeometryOutput, geometry_registry
from path_tracer.utils.obj_utils import ObjMesh, read_obj_file

logger = logging.getLogger(__name__)


def apply_transforms(mesh: ObjMesh, transforms: list[dict[str, Any]]):
    for transform in transforms:
        tp = transform["type"]
        assert tp in {"scale", "translate"}

        if tp == "scale":
            values = transform["params"]
            assert len(values) == 3
            logger.info(f"Scale: {values}")
            mesh.vertices[..., 0] *= values[0]
            mesh.vertices[..., 1] *= values[1]
            mesh.vertices[..., 2] *= values[2]
        elif tp == "translate":
            values = transform["params"]
            assert len(values) == 3
            logger.info(f"Translate: {values}")
            mesh.vertices[..., 0] += values[0]
            mesh.vertices[..., 1] += values[1]
            mesh.vertices[..., 2] += values[2]


class MeshGeometry(Geometry):
    """Geometry consisting of multiple meshes"""

    def __init__(self, paths: list[str], transforms: Optional[list[list[dict[str, Any]]]] = None) -> None:
        """
        paths: list of paths to obj files
        transforms: list of transforms to apply to each mesh
        """
        super().__init__()

        def tf(arr):
            return o3d.core.Tensor(arr, o3d.core.float32)  # pylint: disable=no-member

        def ti(arr):
            return o3d.core.Tensor(arr, o3d.core.int32)  # pylint: disable=no-member

        self.scene = o3d.t.geometry.RaycastingScene()
        self.meshes = []

        # keep areas of meshes to compute positional pdf
        self.areas = []

        # O3D does not support computing for ray casting, so we keep track of the normals and compute them later
        self.obj_normals = []
        self.obj_normal_indices = []

        # create O3D meshes from obj files
        for i, path in enumerate(paths):
            obj = read_obj_file(path)
            if transforms is not None:
                apply_transforms(obj, transforms[i])

            mesh = o3d.t.geometry.TriangleMesh()
            mesh.vertex["positions"] = tf(obj.vertices)
            mesh.triangle["indices"] = ti(obj.face_vertex_indices)

            self.scene.add_triangles(mesh)

            self.obj_normals.append(torch.from_numpy(obj.normals))
            self.obj_normal_indices.append(torch.from_numpy(obj.face_normal_indices))

            mesh = mesh.to_legacy()
            self.meshes.append(mesh)
            self.areas.append(mesh.get_surface_area())
            logger.info(f"Add mesh to O3D scene (area: {self.areas[-1]})")

    def __len__(self) -> int:
        return len(self.meshes)

    def ray_intersect(self, rays_o: Tensor, rays_d: Tensor) -> GeometryOutput:
        rays_o_input = rays_o.detach()
        rays_d_input = rays_d.detach()
        device = rays_o.device

        # See http://www.open3d.org/docs/release/python_api/open3d.t.geometry.RaycastingScene.html
        rays = o3d.core.Tensor(  # pylint: disable=no-member
            np.stack([
                rays_o_input.cpu().numpy(),
                rays_d_input.cpu().numpy(),
            ], axis=1).reshape([-1, 6])
        )
        rt = self.scene.cast_rays(rays)

        # Helper functions to convert O3D output to PyTorch tensors
        def get_rt_result(key):
            return torch.from_numpy(rt[key].numpy()).to(device)

        def get_rt_indices(key):
            return torch.from_numpy(rt[key].numpy().astype(np.int64))

        dist = get_rt_result("t_hit")
        mask = torch.isfinite(dist)
        points = torch.zeros_like(rays_o)
        points[mask] = rays_o[mask] + dist[mask, None] * rays_d_input[mask]

        geo_normals = get_rt_result("primitive_normals")
        geo_ids = get_rt_indices("geometry_ids").to(device)

        # Compute shading (interpolated) normals
        sh_normals = torch.zeros_like(rays_o)
        sh_mask = torch.zeros(len(sh_normals), dtype=torch.bool)
        sh_indices = get_rt_indices("primitive_ids")
        sh_uvs = get_rt_result("primitive_uvs")
        u = sh_uvs[:, 0]
        v = sh_uvs[:, 1]
        w = 1 - u - v
        sh_weights = torch.stack([w, u, v], dim=1).view(-1, 3, 1)

        for i in range(len(self.obj_normals)):
            obj_normals = self.obj_normals[i]
            if len(obj_normals) == 0:
                continue

            obj_normal_indices = self.obj_normal_indices[i]
            if len(obj_normal_indices) == 0:
                continue

            i_mask = (geo_ids == i) & mask
            if int(i_mask.sum()) == 0:
                continue

            sh_mask[i_mask] = True
            i_tri_indices = sh_indices[i_mask]
            i_normal_indices = obj_normal_indices[i_tri_indices].view(-1)
            i_normals = obj_normals[i_normal_indices].view(-1, 3, 3).to(device)
            sh_normals[i_mask] = F.normalize(torch.sum(i_normals * sh_weights[i_mask], dim=1))

        # For meshes without shading normals, just use geometry normals
        sh_normals[~sh_mask] = geo_normals[~sh_mask]

        return GeometryOutput(
            mask,
            points,
            geo_normals,
            sh_normals,
            geo_ids,
            rays_o,
            rays_d,
        )

    def uniform_sample(self, i_primitive: int, n_samples: int, device: str) -> tuple[Tensor, Tensor]:
        """Unifomly (per area) sample points from a mesh"""
        mesh = self.meshes[i_primitive]
        pc = mesh.sample_points_uniformly(n_samples, use_triangle_normal=True)
        points = np.asarray(pc.points).astype(np.float32)
        normals = np.asarray(pc.normals).astype(np.float32)

        # O3D sampling is grouped by faces, so we shuffle it here
        indices = np.arange(len(points))
        np.random.shuffle(indices)
        points = points[indices]
        normals = normals[indices]

        return torch.from_numpy(points).to(device), torch.from_numpy(normals).to(device)

    def uniform_sample_pos_pdf(self, i_primitive: int) -> float:
        """For a mesh, the pdf is inversed area"""
        return 1 / self.areas[i_primitive]


geometry_registry.add("mesh", MeshGeometry)
