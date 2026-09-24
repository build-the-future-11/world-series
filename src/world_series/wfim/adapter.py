from __future__ import annotations
from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry
from world_series.wfim.algebra import basis, multiply

def algebra_multiply(request: ModuleRequest) -> ModuleResult:
    out = multiply(basis(1), basis(2))
    return ModuleResult(status=RunStatus.SUCCEEDED, diagnostics={"coeffs": {str(k): v for k, v in out.coeffs.items()}}, verification_status="EXACT")

def register() -> None:
    get_registry().register(Capability("algebra_multiply", "wfim", CapabilityState.AVAILABLE, handler=algebra_multiply))
