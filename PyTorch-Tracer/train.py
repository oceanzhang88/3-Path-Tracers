import itertools
import logging
from pathlib import Path

import hydra
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from hydra.core.hydra_config import HydraConfig
from omegaconf import OmegaConf
from torch import Tensor
from torch.optim import Adam
from torch.utils.tensorboard.writer import SummaryWriter
from tqdm import tqdm

from path_tracer.config.train_config import TrainConfig
from path_tracer.core.io import build_integrator, build_scene
from path_tracer.core.scene import Scene
from path_tracer.integrator import Integrator
from path_tracer.utils.image_utils import read_image, save_image
from path_tracer.utils.pbar import ProgressBar
from path_tracer.utils.render_utils import get_coords_multisample

logger = logging.getLogger(__name__)


@hydra.main(version_base="1.2", config_path="config", config_name="train")
def main(cfg: TrainConfig = None):
    device = cfg.device
    mode = cfg.mode
    out_dir = Path(HydraConfig().get().run.dir)
    config_yaml = OmegaConf.to_yaml(cfg)
    logger.info(config_yaml)
    logger.info(f"Output: {str(out_dir)}")
    with open(out_dir / "config.yaml", mode="w", encoding="utf-8") as f:
        f.write(config_yaml + "\n")

    integrator = build_integrator(cfg.integrator)

    if cfg.scale > 0:
        cfg.scene.width = int(cfg.scale * cfg.scene.width)
        cfg.scene.height = int(cfg.scale * cfg.scene.height)
        logger.info(f"Train at scale {cfg.scale} ({cfg.scene.width}x{cfg.scene.height})")

    scene = build_scene(cfg.scene)
    logger.info("Built scene")

    # load ground truth image
    assert Path(cfg.gt).suffix == ".exr", "Must use EXR image for training"
    gt = read_image(cfg.gt, cfg.scale)
    gt = torch.from_numpy(gt).view(-1, 3).to(device)

    # find out what needs to be trained
    # currently, we only optimize BRDF
    trained_models: dict[str, tuple[nn.Module, torch.optim.Optimizer]] = {}
    trained_brdf = [o for o in scene.brdf if isinstance(o, nn.Module)]
    for i, brdf in enumerate(trained_brdf):
        optim = Adam(brdf.parameters(), lr=cfg.learning_rate)
        trained_models[f"brdf_{i}"] = [brdf, optim]

    if mode == "nerad":
        # TODO: (1/3):
        # initialize nerad for the integrator,
        # setup its optimizer,
        # put it in the trained_models dict for saving checkpoints
        pass

    if len(trained_models) == 0:
        logger.error("No model to train!")
        return

    # create all pixel coordinates
    H, W = cfg.scene.height, cfg.scene.width
    coords = torch.stack(
        torch.meshgrid(torch.linspace(0, W - 1, W), torch.linspace(0, H - 1, H), indexing="xy"),
        dim=-1,
    ).view(-1, 2)

    # setup logging
    writer = SummaryWriter(out_dir / "tensorboard")
    ckpt_dir = out_dir / "checkpoints"
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    # start training
    global_step = 0
    pbar = ProgressBar(cfg.pbar, cfg.steps)
    spp = cfg.train_spp
    batch_size = cfg.batch_size
    while global_step < cfg.steps:
        # get a random batch of coordinates
        # due to computational constraints, we typically don't render the entire image at each step
        # instead, we randomly choose some pixels from the image and call them a batch
        # in every iteration, we optimize using pixel values from (batch_size * spp) rays
        b_indices = np.random.choice(H*W, batch_size, replace=False)
        b_coords = get_coords_multisample(coords[b_indices], spp, "uniform")
        rays_o, rays_d = scene.camera.image_to_rays(b_coords)

        if mode == "render":
            # render the batch
            colors = integrator.render(scene, rays_o.to(device), rays_d.to(device))
            colors = colors.view(batch_size, spp, 3).sum(dim=1) / spp

            # reconstruction loss
            loss = F.mse_loss(colors, gt[b_indices])
        elif mode == "nerad":
            # TODO: (2/3): fill in the blanks indicated by comments
            lhs, rhs = None, None  # <- fill this

            # residual loss
            residual = F.mse_loss(lhs, rhs.detach())

            # reconstruction loss using rhs,
            # remember to take care of spp
            recons = None  # <- fill this

            loss = residual + recons

            writer.add_scalar("loss/residual", float(residual), global_step)
            writer.add_scalar("loss/recons", float(recons), global_step)

        # optimize
        for _, optim in trained_models.values():
            optim.zero_grad()
        loss.backward()
        for _, optim in trained_models.values():
            optim.step()

        # log for monitoring
        loss = float(loss)
        global_step += 1
        pbar.update({"loss": float(loss)})
        writer.add_scalar("loss/all", loss, global_step)

        # visualize during training
        if (cfg.render_first_step and global_step == 1) or \
                global_step % cfg.render_step_size == 0 or \
                global_step == cfg.steps:
            logger.info("Render full image")

            image = render_full_image(cfg, coords, scene, integrator).numpy()

            vis_dir = out_dir / "visualization" / f"step_{global_step}"
            vis_dir.mkdir(parents=True, exist_ok=True)

            if mode == "render":
                save_image(vis_dir / "output.png", image)
            elif mode == "nerad":
                save_image(vis_dir / "lhs.png", image[..., :3])
                save_image(vis_dir / "rhs.png", image[..., 3:])

        # save checkpoint
        if (cfg.save_first_step and global_step == 1) or \
                global_step % cfg.save_step_size == 0 or \
                global_step == cfg.steps:
            logger.info("Save progress")

            ckpt = {
                "global_step": global_step,
                "model": {},
                "optim": {},
            }

            for key, [model, optim] in trained_models.items():
                ckpt["model"][key] = model.state_dict()
                ckpt["optim"][key] = optim.state_dict()

            torch.save(ckpt, ckpt_dir / f"step_{global_step}.ckpt")


@torch.no_grad()
def render_full_image(cfg: TrainConfig, coords: Tensor, scene: Scene, integrator: Integrator):
    mode = cfg.mode
    bs = cfg.block_size
    device = cfg.device
    spp = cfg.render_spp
    H, W = cfg.scene.height, cfg.scene.width
    coords = coords.view(H, W, 2)

    if mode == "render":
        result = torch.zeros(H, W, 3)
    elif mode == "nerad":
        # for nerad we return a 6-channel image, i.e. two 3-channel images
        result = torch.zeros(H, W, 6)

    # render the image block-by-block
    n_blocks = int(np.ceil(H / bs) * np.ceil(W / bs))
    pbar = tqdm(total=n_blocks)
    for y, x in itertools.product(range(0, H, bs), range(0, W, bs)):
        b_coords = coords[y:y+bs, x:x+bs]
        b_H, b_W = b_coords.shape[:2]

        b_coords = get_coords_multisample(b_coords.reshape(-1, 2), spp, "uniform")
        rays_o, rays_d = scene.camera.image_to_rays(b_coords)

        if mode == "render":
            colors = integrator.render(scene, rays_o.to(device), rays_d.to(device))
        elif mode == "nerad":
            # TODO: (3/3): complete the line (hint: same as task 2)
            lhs, rhs = None, None
            colors = torch.cat([lhs, rhs], dim=-1)

        colors = colors.view(b_H * b_W, spp, -1).sum(dim=1) / spp
        result[y:y+bs, x:x+bs] = colors.view(b_H, b_W, -1).cpu()
        pbar.update(1)

    return result


if __name__ == "__main__":
    main()
