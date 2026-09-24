from __future__ import annotations
import numpy as np
import torch

def flatten_params(params: dict[str, torch.Tensor]) -> tuple[torch.Tensor, dict]:
    pieces = []
    meta = {}
    offset = 0
    for k, v in params.items():
        flat = v.reshape(-1)
        meta[k] = {"shape": tuple(v.shape), "start": offset, "end": offset + flat.numel()}
        pieces.append(flat)
        offset += flat.numel()
    return torch.cat(pieces), meta

def unflatten_params(vec: torch.Tensor, meta: dict) -> dict[str, torch.Tensor]:
    out = {}
    for k, m in meta.items():
        out[k] = vec[m["start"]:m["end"]].reshape(m["shape"])
    return out

def quadratic_loss_torch(A: torch.Tensor, b: torch.Tensor, x: torch.Tensor) -> torch.Tensor:
    return 0.5 * (x * (A @ x)).sum() + (b * x).sum()

def np_to_torch_spd(A: np.ndarray, b: np.ndarray, x0: np.ndarray, device="cpu"):
    return (
        torch.tensor(A, dtype=torch.float64, device=device),
        torch.tensor(b, dtype=torch.float64, device=device),
        torch.tensor(x0, dtype=torch.float64, device=device),
    )
