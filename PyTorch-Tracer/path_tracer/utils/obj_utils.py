import logging
import os
from dataclasses import dataclass
from typing import Optional

import numpy as np

from path_tracer.utils.io_utils import read_lines

logger = logging.getLogger(__name__)


@dataclass
class ObjMesh:
    vertices: np.ndarray
    normals: np.ndarray
    uvs: np.ndarray
    face_vertex_indices: np.ndarray
    face_uv_indices: np.ndarray
    face_normal_indices: np.ndarray


def _parse_floats(l: list[str]) -> list[float]:
    return [float(v) for v in l]


def _parse_ints(l: list[str]) -> list[int]:
    return [int(v) if len(v) > 0 else -1 for v in l]


def read_obj_file(path: str) -> ObjMesh:
    """Read triangles from a .obj file"""
    logger.info(f"Read obj file {path}")

    cache = path + ".npz"
    mesh = load_cache(cache)
    if mesh is not None:
        return mesh

    mesh = ObjMesh(*[[] for _ in range(6)])

    ignored_cmds = {
        "mtllib",  # material
        "usemtl",
        "o",  # object name
        "s",  # smoothing group
        "l",  # line
    }
    unknown_cmds = set()
    for line in read_lines(path, strip_spaces=True, remove_empty=True):
        if line[0] == "#":
            continue

        split = line.split(" ")
        split = list(filter(None, split))  # remove empty string
        cmd = split[0]

        if cmd == "v":
            mesh.vertices.append(_parse_floats(split[1:]))
        elif cmd == "vn":
            mesh.normals.append(_parse_floats(split[1:]))
        elif cmd == "vt":
            mesh.uvs.append(_parse_floats(split[1:]))
        elif cmd == "f":
            assert len(split) == 4
            face = [_parse_ints(l.split("/")) for l in split[1:]]
            mesh.face_vertex_indices.append([v[0]-1 for v in face])
            if len(face[0]) > 1:
                mesh.face_uv_indices.append([v[1]-1 for v in face])
            if len(face[0]) > 2:
                mesh.face_normal_indices.append([v[2]-1 for v in face])
        elif cmd in ignored_cmds:
            pass
        else:
            unknown_cmds.add(cmd)

    if len(unknown_cmds) > 0:
        logger.warning(f"Found unknown cmds in obj file: {unknown_cmds}")

    for k, v in mesh.__dict__.items():
        dtype = np.int64 if k.endswith("_indices") else np.float32
        mesh.__dict__[k] = np.array(v, dtype=dtype)

    logger.info(f"Cache loaded obj to {cache}")
    np.savez(cache, **mesh.__dict__)

    return mesh


def load_cache(path: str) -> Optional[ObjMesh]:
    if not os.path.isfile(path):
        return None

    logger.info(f"Load cached obj from {path}")
    cache = np.load(path)
    mesh = ObjMesh(*[None for _ in range(6)])

    for k in mesh.__dict__:
        if k not in cache:
            logger.warning(f"Key [{k}] not found in cache, reload obj file")
            return None
        mesh.__dict__[k] = cache[k]

    return mesh
