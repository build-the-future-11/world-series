from __future__ import annotations
import torch

def build_features(grad: torch.Tensor, momentum: torch.Tensor, loss: torch.Tensor, remaining_budget: float) -> torch.Tensor:
    # Query labels must never appear here.
    g = grad.detach()
    m = momentum.detach()
    gn = g / (g.norm() + 1e-8)
    mn = m / (m.norm() + 1e-8)
    loss_feat = torch.full_like(g, float(loss.detach()))
    budget_feat = torch.full_like(g, float(remaining_budget))
    return torch.stack([gn, mn, loss_feat, budget_feat], dim=-1)
