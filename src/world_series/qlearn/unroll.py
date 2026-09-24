from __future__ import annotations
import torch
from world_series.qlearn.features import build_features
from world_series.qlearn.functional import quadratic_loss_torch

def bounded_update(theta: torch.Tensor, grad: torch.Tensor, eta: torch.Tensor, d: torch.Tensor) -> torch.Tensor:
    return theta - eta * d * grad

def unroll_quadratic(A, b, theta0, policy, steps: int, include_query: bool = True):
    theta = theta0.clone().requires_grad_(True)
    momentum = torch.zeros_like(theta)
    query_losses = []
    policy.reset_state()
    for t in range(steps):
        loss = quadratic_loss_torch(A, b, theta)
        grad, = torch.autograd.grad(loss, theta, create_graph=True)
        momentum = 0.9 * momentum + 0.1 * grad.detach()
        feats = build_features(grad, momentum, loss, remaining_budget=(steps - t) / steps)
        eta, d = policy(feats)
        theta = bounded_update(theta, grad, eta, d)
        if include_query:
            query_losses.append(quadratic_loss_torch(A, b, theta))
    return theta, query_losses
