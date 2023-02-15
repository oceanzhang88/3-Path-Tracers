from dataclasses import dataclass

from hydra.core.config_store import ConfigStore

from path_tracer.config.object_config import ObjectConfig
from path_tracer.config.scene_config import SceneConfig


@dataclass
class RenderConfig:
    scale: float
    spp: int
    block_size: int
    scene: SceneConfig
    integrator: ObjectConfig
    gui: bool
    device: str
    save_exr: bool

cs = ConfigStore.instance()
cs.store(name="render_schema", node=RenderConfig)
