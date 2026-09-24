from __future__ import annotations
import torch
from world_series.qlearn.functional import np_to_torch_spd
from world_series.qlearn.policy import BoundedDiagonalPolicy
from world_series.qlearn.unroll import unroll_quadratic

def meta_step(tasks, policy: BoundedDiagonalPolicy, steps: int = 4, lr: float = 0.01):
    opt = torch.optim.Adam(policy.parameters(), lr=lr)
    opt.zero_grad()
    total = torch.tensor(0.0, dtype=torch.float64)
    for task in tasks:
        A, b, x0 = np_to_torch_spd(task.optimizee.A, task.optimizee.b, task.optimizee.x0)
        _, qlosses = unroll_quadratic(A, b, x0, policy, steps=steps)
        total = total + sum(qlosses) / len(qlosses)
    total = total / max(len(tasks), 1)
    total.backward()
    opt.step()
    return float(total.detach())

def finite_diff_check(policy: BoundedDiagonalPolicy, A, b, x0, eps: float = 1e-5) -> float:
    """Compare analytic meta-grad on one scalar param vs finite differences."""
    # pick first parameter element
    p = next(policy.parameters())
    idx = (0,) * p.ndim
    # analytic
    policy.zero_grad(set_to_none=True)
    _, qlosses = unroll_quadratic(A, b, x0, policy, steps=2)
    loss = sum(qlosses) / len(qlosses)
    loss.backward()
    analytic = float(p.grad[idx])
    # FD
    with torch.no_grad():
        p[idx] += eps
    _, q1 = unroll_quadratic(A, b, x0, policy, steps=2)
    l1 = float((sum(q1) / len(q1)).detach())
    with torch.no_grad():
        p[idx] -= 2 * eps
    _, q0 = unroll_quadratic(A, b, x0, policy, steps=2)
    l0 = float((sum(q0) / len(q0)).detach())
    with torch.no_grad():
        p[idx] += eps
    fd = (l1 - l0) / (2 * eps)
    return abs(analytic - fd)
