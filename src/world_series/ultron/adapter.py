from __future__ import annotations
from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry

def orchestrate_episode(request: ModuleRequest) -> ModuleResult:
    from world_series.ultron.evaluate import run_experiment
    # not used via run_experiment path directly
    return ModuleResult(status=RunStatus.SUCCEEDED, diagnostics={"note": "use ultron evaluate"}, verification_status="PLUMBING_ONLY")

def register() -> None:
    get_registry().register(Capability("orchestrate_episode", "ultron", CapabilityState.AVAILABLE, handler=orchestrate_episode))
