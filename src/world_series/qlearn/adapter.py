from __future__ import annotations
from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry

def adapt_learner(request: ModuleRequest) -> ModuleResult:
    return ModuleResult(
        status=RunStatus.SUCCEEDED,
        diagnostics={"operation": "adapt_learner", "note": "thin adapter over qlearn smoke path"},
        measured_cost={"candidate_evals": 1.0},
        verification_status="PLUMBING_ONLY",
    )

def register() -> None:
    reg = get_registry()
    reg.register(Capability("adapt_learner", "qlearn", CapabilityState.AVAILABLE, handler=adapt_learner, notes="v0.1 thin adapter"))
