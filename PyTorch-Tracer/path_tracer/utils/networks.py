from itertools import chain

import torch
import torch.nn as nn


class PositionalEncoding:
    def __init__(self,
                 in_channels: int,
                 n_freqs: int,
                 max_freq_log2: int,
                 ):
        self.in_channels = in_channels
        self.out_channels = in_channels * (n_freqs * 2 + 1)
        self.freq_bands = 2 ** torch.linspace(0, max_freq_log2, steps=n_freqs)

    def __call__(self, x):
        return torch.cat([x] + list(chain.from_iterable((
            [torch.sin(x * freq), torch.cos(x * freq)] for freq in self.freq_bands
        ))), dim=-1)


class NeradMlp(nn.Module):
    """MLP network for Neural Radiosity

    Input to the network: (points, dirs, normals, albedo), all (N, 3) tensors
    Output: (N, 3) radiance from points toward dirs
    """
    def __init__(self):
        super().__init__()

        self.pos_enc = PositionalEncoding(3, 8, 7)

        # positional encoding of points, dirs, normals; plus albedo
        in_size = 3 * self.pos_enc.out_channels + 3

        net_width = 128
        self.network = nn.Sequential(
            nn.Linear(in_size, net_width),
            nn.ReLU(),
            nn.Linear(net_width, net_width),
            nn.ReLU(),
            nn.Linear(net_width, net_width),
            nn.ReLU(),
            nn.Linear(net_width, 3),
        )

    def forward(self, points, dirs, normals, albedo):
        net_in = torch.cat([self.pos_enc(points), self.pos_enc(dirs), self.pos_enc(normals), albedo], dim=-1)
        ret = torch.abs(self.network(net_in))
        ret[(dirs*normals).sum(dim=-1) < 0] = 0
        return ret
