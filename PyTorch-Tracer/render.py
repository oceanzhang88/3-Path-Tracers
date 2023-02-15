import itertools
import logging
from pathlib import Path

import cv2
import hydra
import numpy as np
import torch
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf
from torch import Tensor
from tqdm import tqdm

from path_tracer.config.render_config import RenderConfig
from path_tracer.core.io import build_integrator, build_scene
from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator
from path_tracer.utils.image_utils import save_image, tonemap_image
from path_tracer.utils.openexr_utils import write_openexr
from path_tracer.utils.render_utils import get_coords_multisample

logger = logging.getLogger(__name__)
window_name = "main"


@hydra.main(version_base="1.2", config_path="config", config_name="render")
def main(cfg: RenderConfig = None):
    # save everything to out_dir
    out_dir = Path(HydraConfig().get().run.dir)

    # print and save config for debugging
    config_yaml = OmegaConf.to_yaml(cfg)
    logger.info(config_yaml)
    with open(out_dir / "config.yaml", mode="w", encoding="utf-8") as f:
        f.write(config_yaml + "\n")

    # configure the integrator
    integrator = build_integrator(cfg.integrator)

    # render at lower resolution for debugging
    if cfg.scale > 0:
        cfg.scene.width = int(cfg.scale * cfg.scene.width)
        cfg.scene.height = int(cfg.scale * cfg.scene.height)
        logger.info(
            f"render at scale {cfg.scale} ({cfg.scene.width}x{cfg.scene.height})")

    # configure the scene
    scene = build_scene(cfg.scene)
    logger.info("Built scene")

    # generate all pixel coordinates to render
    H, W = cfg.scene.height, cfg.scene.width
    coords = torch.stack(
        torch.meshgrid(torch.linspace(0, W - 1, W),
                       torch.linspace(0, H - 1, H), indexing="xy"),
        dim=-1,
    )

    result = torch.zeros(H, W, 3)

    # configure the progress bar
    bs = cfg.block_size
    n_blocks = int(np.ceil(H / bs) * np.ceil(W / bs))
    pbar = tqdm(total=n_blocks)

    # show a window that updates every block
    if cfg.gui:
        cv2.namedWindow(window_name)

    # render every block
    for y, x in itertools.product(range(0, H, bs), range(0, W, bs)):
        b_coords = coords[y:y+bs, x:x+bs]
        b_H, b_W = b_coords.shape[:2]
        try:
            b_colors = render_block(
                cfg, b_coords.reshape(-1, 2), scene, integrator).view(b_H, b_W, 3)
        except KeyboardInterrupt:
            break

        result[y:y+bs, x:x+bs] = b_colors
        pbar.update(1)

        if cfg.gui:
            key = cv2.waitKey(1)
            if key == 27:  # esc
                logger.warning("Rendering cancelled by user")
                break
            displayed = np.clip(tonemap_image(result.numpy()), 0, 1)
            cv2.imshow(window_name, cv2.cvtColor(displayed, cv2.COLOR_RGB2BGR))

        save_image(out_dir / "output.png", result.numpy(),
                   tonemap=integrator.need_tonemap())

    if cfg.save_exr:
        write_openexr(out_dir / "output.exr", result, "RGB")

    integrator.on_render_ended()

    if cfg.gui:
        try:
            while True:
                key = cv2.waitKey(20) & 0xFFFF
                if key == 27:  # esc
                    break
        except KeyboardInterrupt:
            pass
        cv2.destroyAllWindows()


def render_block(cfg: RenderConfig, coords: Tensor, scene: Scene, integrator: Integrator) -> Tensor:
    device = cfg.device
    spp = cfg.spp
    N = len(coords)

    # render multiple samples per ray
    coords = get_coords_multisample(coords, spp, "uniform")

    # transform pixel coordinates to world coordinates
    rays_o, rays_d = scene.camera.image_to_rays(coords)

    # integrate
    colors = integrator.render(scene, rays_o.to(device), rays_d.to(device))

    # sanity check: colors shall be non-negative
    n_infinite = int(torch.sum(~torch.isfinite(colors)))
    n_negative = int(torch.sum(colors < 0))
    if n_infinite + n_negative > 0:
        logger.warning(
            f"Found invalid colors, please check your integrator (min = {float(colors.min())}, negative = {n_negative}, infinite / NaN = {n_infinite}).")

    # average multiple samples
    colors = colors.view(N, spp, 3).sum(dim=1) / spp
    return colors.cpu()


if __name__ == "__main__":
    main()
