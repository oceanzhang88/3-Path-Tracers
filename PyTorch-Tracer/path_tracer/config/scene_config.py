from dataclasses import dataclass

from path_tracer.config.object_config import ObjectConfig


@dataclass
class SceneConfig:
    brdf: list[ObjectConfig]
    camera: ObjectConfig
    environment: ObjectConfig
    geometry: ObjectConfig
    emitters: list[ObjectConfig]
    width: int
    height: int
