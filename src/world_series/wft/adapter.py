from __future__ import annotations

import numpy as np

from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry
from world_series.wft.laplacian import encode, laplacian_from_weights, path_graph, weighted_spectral


def spectral_transform(request: ModuleRequest) -> ModuleResult:
    W = path_graph(6)
    L = laplacian_from_weights(W)
    M = np.eye(6)
    evals, _Q, Phi = weighted_spectral(L, M)
    c = encode(np.ones(6), Phi, M)
    return ModuleResult(
        status=RunStatus.SUCCEEDED,
        diagnostics={"coeffs": c.tolist(), "evals": evals.tolist()},
        verification_status="REFERENCE",
    )


def register() -> None:
    get_registry().register(
        Capability("spectral_transform", "wft", CapabilityState.AVAILABLE, handler=spectral_transform)
    )
