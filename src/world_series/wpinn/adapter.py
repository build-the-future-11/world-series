from __future__ import annotations

from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry
from world_series.wpinn.systems import make_trajectory
from world_series.wpinn.train import weak_only_fit


def identify_dynamical_law(request: ModuleRequest) -> ModuleResult:
    traj = make_trajectory(0, k=1.5, c=0.2, noise=0.0)
    coef, rnorm, support = weak_only_fit(traj)
    return ModuleResult(
        status=RunStatus.SUCCEEDED,
        diagnostics={"coef": coef, "weak_residual_norm": rnorm, "support": sorted(support)},
        measured_cost={"steps": 1.0},
        verification_status="DEV_VERIFIER",
    )


def register() -> None:
    get_registry().register(
        Capability(
            "identify_dynamical_law",
            "wpinn",
            CapabilityState.AVAILABLE,
            handler=identify_dynamical_law,
        )
    )
