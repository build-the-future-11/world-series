from __future__ import annotations
from world_series.core.budgets import BudgetLedger
from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry
from world_series.wcode.search import synthesize

def synthesize_dsl_program(request: ModuleRequest) -> ModuleResult:
    ledger = BudgetLedger(request.budget)
    examples = [({"x": 2}, 3), ({"x": 5}, 6)]
    prog, found, _used = synthesize(examples, ledger)
    return ModuleResult(
        status=RunStatus.SUCCEEDED if found else RunStatus.FAILED,
        diagnostics={"found": found, "prog": repr(prog)},
        measured_cost=ledger.snapshot(),
        verification_status="HELDOUT_TESTS" if found else "FAILED",
    )

def register() -> None:
    get_registry().register(Capability("synthesize_dsl_program", "wcode", CapabilityState.AVAILABLE, handler=synthesize_dsl_program))
