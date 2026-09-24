from __future__ import annotations
import torch
import torch.nn as nn
from world_series.core.contracts import ErrorCode, WorldSeriesError

class BoundedDiagonalPolicy(nn.Module):
    """Maps features -> positive eta and diagonal D within configured bounds."""

    def __init__(self, feat_dim: int = 4, hidden: int = 32, eta_bounds=(1e-3, 0.5), d_bounds=(0.1, 2.0)):
        super().__init__()
        eta_min, eta_max = eta_bounds
        d_min, d_max = d_bounds
        if not (0 < eta_min < eta_max) or not (0 < d_min < d_max):
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "invalid positive update bounds")
        self.eta_min = float(eta_min)
        self.eta_max = float(eta_max)
        self.d_min = float(d_min)
        self.d_max = float(d_max)
        self.net = nn.Sequential(
            nn.Linear(feat_dim, hidden),
            nn.Tanh(),
            nn.Linear(hidden, 2),
        ).double()
        # initialize near moderate fixed rule
        with torch.no_grad():
            self.net[-1].weight.zero_()
            self.net[-1].bias[:] = torch.tensor([0.0, 0.0], dtype=torch.float64)

    def forward(self, features: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # features [P,F] -> aggregate mean for eta; per-param for D
        pooled = features.mean(dim=0, keepdim=True)
        raw = self.net(pooled)[0]
        eta = self.eta_min + (self.eta_max - self.eta_min) * torch.sigmoid(raw[0])
        d_raw = self.net(features)[:, 1]
        d = self.d_min + (self.d_max - self.d_min) * torch.sigmoid(d_raw)
        return eta, d

    def reset_state(self) -> None:
        return None
