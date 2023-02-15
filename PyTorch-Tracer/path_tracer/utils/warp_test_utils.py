import importlib
from collections import OrderedDict
from functools import partial

import plotly.graph_objects as go
import torch
from IPython.display import display
from ipywidgets import Button, Dropdown, HBox
from torch import Tensor

import path_tracer.utils.sampling_utils as su


class WarpDef:
    def __init__(self, warp_func, pdf_func, avg_error_threshold: float, abs_error_threshold: float, dimensions: int) -> None:
        self.warp_func = warp_func
        self.pdf_func = pdf_func
        self.dimensions = dimensions
        self.avg_error_threshold = avg_error_threshold
        self.abs_error_threshold = abs_error_threshold

    def warp_for_visualization(self, n_points):
        uv = torch.rand(n_points, 2)
        points = self.warp_func(uv)
        if points.shape[1] == 2:
            points = torch.cat([points, torch.zeros_like(points[:, 0:1])], dim=1)
        return points

    def check(self, n_points):
        uv = torch.rand(n_points, 2, requires_grad=True)
        points = self.warp_func(uv)
        with torch.no_grad():
            pdf = self.pdf_func(points)

        # check output shape
        if len(points.shape) != 2 or points.shape[0] != n_points or points.shape[1] != self.dimensions:
            raise ValueError(f"warped points has shape {list(points.shape)} instead of [{n_points}, {self.dimensions}]")
        if len(pdf.shape) != 1 or pdf.shape[0] != n_points:
            raise ValueError(f"pdf has shape {list(pdf.shape)} instead of [{n_points},]")
        if torch.sum(~torch.isfinite(pdf)) > 0:
            raise ValueError("found inf / NaN values in pdf")

        self._check_density(uv, points, pdf)

    def _check_density(self, uv: Tensor, points: Tensor, pdf: Tensor):
        raise NotImplementedError()


class SeparableWarpDef(WarpDef):
    def _check_density(self, uv: Tensor, points: Tensor, pdf: Tensor):
        xy = self._convert_points(points)
        dxduv = torch.autograd.grad(xy[:, 0], uv, torch.ones(len(xy)), retain_graph=True)[0]
        dyduv = torch.autograd.grad(xy[:, 1], uv, torch.ones(len(xy)), retain_graph=True)[0]

        xidx = 0 if dxduv[:, 0].abs().sum() > dxduv[:, 1].abs().sum() else 1
        yidx = 1 - xidx

        with torch.no_grad():
            density = self._convert_density(xy, dxduv[:, xidx], dyduv[:, yidx])
            if torch.sum(~torch.isfinite(density)) > 0:
                raise ValueError("found inf / NaN values in density")

            abs_error = torch.abs(density - pdf)
            abs_error_max = float(abs_error.max())
            avg_error = float(abs_error.sum()) / len(density)

        avg_ok = avg_error <= self.avg_error_threshold
        avg_text = "(pass)" if avg_ok else "(fail)"
        abs_ok = abs_error_max <= self.abs_error_threshold
        abs_text = "(pass)" if abs_ok else "(fail)"

        error_text = f"avg pdf error is {avg_error:.4e} {avg_text}, max is {abs_error_max:.4e} {abs_text}"
        if not abs_ok:
            error_text += f", {(abs_error > self.abs_error_threshold).sum()} samples has error > {self.abs_error_threshold}"
        if not abs_ok or not avg_ok:
            print(f"Failed, {error_text}")
        else:
            print(f"Passed, {error_text}")

    def _convert_points(self, points: Tensor) -> Tensor:
        return points

    def _convert_density(self, xy: Tensor, dxduv: Tensor, dyduv: Tensor) -> Tensor:
        return 1 / (dxduv * dyduv)


class SeparableXYDef(SeparableWarpDef):
    def __init__(self, warp_func, pdf_func) -> None:
        super().__init__(warp_func, pdf_func, 1e-7, 1e-6, 2)


class SeparablePolarDef(SeparableWarpDef):
    def __init__(self, warp_func, pdf_func) -> None:
        super().__init__(warp_func, pdf_func, 1e-7, 1e-5, 2)

    def _convert_points(self, points: Tensor) -> Tensor:
        r = torch.linalg.vector_norm(points, dim=1)
        theta = torch.atan2(points[:, 1], points[:, 0])
        return torch.stack([r, theta], dim=1)

    def _convert_density(self, xy: Tensor, dxduv: Tensor, dyduv: Tensor) -> Tensor:
        return torch.abs(1 / (dxduv * dyduv * xy[:, 0]))


class SeparableSphericalDef(SeparableWarpDef):
    def __init__(self, warp_func, pdf_func) -> None:
        super().__init__(warp_func, pdf_func, 1e-7, 5e-5, 3)

    def _convert_points(self, points: Tensor) -> Tensor:
        phi = torch.atan2(points[:, 1], points[:, 0])
        theta = torch.arccos(points[:, 2])
        return torch.stack([phi, theta], dim=1)

    def _convert_density(self, xy: Tensor, dxduv: Tensor, dyduv: Tensor) -> Tensor:
        return torch.abs(1 / (dxduv * dyduv * torch.sin(xy[:, 1])))


def reload_su():
    global su
    su = importlib.reload(su)


def get_warps() -> dict[str, WarpDef]:
    reload_su()

    result: dict[str, WarpDef] = OrderedDict([
        ["uniform_square", SeparableXYDef(su.sample_uniform_square, su.pdf_uniform_square)],
        ["tent", SeparableXYDef(su.sample_tent, su.pdf_tent)],

        ["uniform_disk", SeparablePolarDef(su.sample_uniform_disk, su.pdf_uniform_disk)],

        ["uniform_sphere", SeparableSphericalDef(su.sample_uniform_sphere, su.pdf_uniform_sphere)],
        ["uniform_hemisphere", SeparableSphericalDef(su.sample_uniform_hemisphere, su.pdf_uniform_hemisphere)],
        ["cosine_hemisphere", SeparableSphericalDef(su.sample_cosine_hemisphere, su.pdf_cosine_hemisphere)],
    ])

    for alpha in [0.1, 0.5, 0.9]:
        result[f"beckmann_{alpha}"] = SeparableSphericalDef(
            partial(su.sample_beckmann, alpha=alpha),
            partial(su.pdf_beckmann, alpha=alpha),
        )

    # beckmann computation has larger numerical errors
    result["beckmann_0.5"].avg_error_threshold = 5e-7
    result["beckmann_0.5"].abs_error_threshold = 1e-4
    result["beckmann_0.1"].avg_error_threshold = 2e-4
    result["beckmann_0.1"].abs_error_threshold = 5e-3

    return result


def visualize_warping(scatter, warp_func, n_points=1000):
    uv = torch.rand(n_points, 2)
    points = warp_func(uv)
    if points.shape[1] == 2:
        points = torch.cat([points, torch.zeros_like(points[:, 0:1])], dim=1)

    scatter.x = points[:, 0]
    scatter.y = points[:, 1]
    scatter.z = points[:, 2]


def visualize_warping_ui():
    warps = get_warps()
    axis_ranges = [-1, 1]

    key_dropdown = Dropdown(
        options=list(warps.keys()),
        value="uniform_square",
        description="Transform:",
    )
    refresh_btn = Button(
        description="Refresh",
    )
    figure = go.FigureWidget(
        [
            go.Scatter3d(
                x=[0], y=[0], z=[0],
                mode="markers",
                marker=dict(
                    size=2,
                ),
            )
        ],
        layout=dict(
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(
                xaxis=dict(range=axis_ranges),
                yaxis=dict(range=axis_ranges),
                zaxis=dict(range=axis_ranges),
                aspectmode="cube",
            )
        )
    )

    def update(*args, **kwargs):
        scatter = figure.data[0]
        # always reload so you can see your changes immediately
        warps = get_warps()
        key = key_dropdown.value
        points = warps[key].warp_for_visualization(1000)
        scatter.x = points[:, 0]
        scatter.y = points[:, 1]
        scatter.z = points[:, 2]

    key_dropdown.observe(update, names="value")
    refresh_btn.on_click(update)

    display(
        HBox([key_dropdown, refresh_btn]),
        figure,
    )

    update()


def check_warping():
    warps = get_warps()
    length = max([len(name) for name in warps])

    for name, warp in warps.items():
        try:
            print(f"Check {name+'...':<{length+4}}", end="")
            warp.check(1000)
        except ValueError as err:
            print(str(err))
