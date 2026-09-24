from __future__ import annotations
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import ModuleRequest, RunStatus
from world_series.core.registry import get_registry
from world_series.ultron.state import EpisodeState
from world_series.ultron.evidence import EvidenceDAG

def execute_action(state: EpisodeState, op: str, budget: Budget, dag: EvidenceDAG) -> tuple[EpisodeState, dict]:
    if state.remaining_budget_steps <= 0:
        return state, {"status": RunStatus.BUDGET_EXHAUSTED.value}
    ledger = BudgetLedger(budget)
    req = ModuleRequest(
        request_id=f"{state.goal}:{op}",
        operation=op,
        input_artifacts=(),
        config_hash="ultron-dev",
        budget=budget,
        allowed_output_types=("json",),
    )
    result = get_registry().execute(req)
    if result.status == RunStatus.SUCCEEDED:
        node = dag.add(f"ev_{len(dag.nodes)}", tuple(state.evidence_ids), result.diagnostics, result.verification_status)
        new_state = EpisodeState(
            goal=state.goal,
            task_type=state.task_type,
            evidence_ids=state.evidence_ids + (node.node_id,),
            capabilities=state.capabilities,
            remaining_budget_steps=state.remaining_budget_steps - 1,
            failure_history=state.failure_history,
        )
    else:
        new_state = EpisodeState(
            goal=state.goal,
            task_type=state.task_type,
            evidence_ids=state.evidence_ids,
            capabilities=state.capabilities,
            remaining_budget_steps=state.remaining_budget_steps - 1,
            failure_history=state.failure_history + (op,),
        )
    return new_state, {"status": result.status.value, "diagnostics": result.diagnostics, "cost": ledger.snapshot()}
