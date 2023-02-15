from dataclasses import dataclass

from hydra.core.config_store import ConfigStore

from path_tracer.config.object_config import ObjectConfig
from path_tracer.config.scene_config import SceneConfig
from path_tracer.utils.pbar import ProgressBarConfig


@dataclass
class TrainConfig:
    scale: float
    device: str

    ### training
    # either "render" or "nerad"
    # "render" is inverse rendering with differentiable renderer,
    # "nerad" is with neural radiosity
    mode: str
    # path to ground truth (reference) exr image
    gt: str
    # number of iterations to optimize
    steps: int
    # samples per pixel used for training
    train_spp: int
    # number of pixels used for training in each iteration
    batch_size: int
    # strength of iteration update
    learning_rate: float

    # rendering (for visualization during training)
    render_spp: int
    block_size: int

    # logging
    # how many iterations to produce a full image render
    render_step_size: int
    # how many iterations to save checkpoint
    save_step_size: int
    # whether to render / save the first step, for comparison and debugging
    render_first_step: bool
    save_first_step: bool

    scene: SceneConfig
    integrator: ObjectConfig
    pbar: ProgressBarConfig

cs = ConfigStore.instance()
cs.store(name="train_schema", node=TrainConfig)
