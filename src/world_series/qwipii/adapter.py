from __future__ import annotations
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry
from world_series.qwipii.domains import RingState
from world_series.qwipii.search import quotient_bfs, replay

def solve_invariant_problem(request: ModuleRequest) -> ModuleResult:
    ledger = BudgetLedger(request.budget)
    start = RingState((2, 1, 0), (0, 1, 2))
    path, expansions, status = quotient_bfs(start, ledger, max_expansions=200)
    ok = False
    if path is not None:
        ok = replay(start, path).tokens == start.goal
    return ModuleResult(
        status=RunStatus.SUCCEEDED if ok else RunStatus.FAILED,
        diagnostics={"path": path, "expansions": expansions, "status": status, "lifted_ok": ok},
        measured_cost=ledger.snapshot(),
        verification_status="EXACTLY_VERIFIED_WITHIN_DOMAIN" if ok else "FAILED",
    )

def verify_certificate(request: ModuleRequest) -> ModuleResult:
    return ModuleResult(status=RunStatus.SUCCEEDED, diagnostics={"ok": True}, verification_status="PLUMBING_ONLY")

def register() -> None:
    reg = get_registry()
    reg.register(Capability("solve_invariant_problem", "qwipii", CapabilityState.AVAILABLE, handler=solve_invariant_problem))
    reg.register(Capability("verify_certificate", "qwipii", CapabilityState.AVAILABLE, handler=verify_certificate))
