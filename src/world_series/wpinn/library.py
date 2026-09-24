from __future__ import annotations
import numpy as np

TERM_NAMES = ["q", "v", "q2", "qv", "v2"]

def library_matrix(qv: np.ndarray):
    q = qv[:, 0]
    v = qv[:, 1]
    Theta = np.column_stack([q, v, q * q, q * v, v * v])
    scales = np.linalg.norm(Theta, axis=0) + 1e-12
    return Theta / scales, TERM_NAMES, scales

def true_support_damped():
    return {"q", "v"}
