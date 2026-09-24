"""Budget reservation and advisory resource accounting."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional

from world_series.core.contracts import Budget, ErrorCode, WorldSeriesError


@dataclass
class BudgetLedger:
    budget: Budget
    steps_used: int = 0
    simulator_calls: int = 0
    candidate_evals: int = 0
    artifact_bytes: int = 0
    started_at: float = field(default_factory=time.monotonic)
    reserved_steps: int = 0

    def remaining_wall_seconds(self) -> float:
        return max(0.0, self.budget.max_wall_seconds - (time.monotonic() - self.started_at))

    def check_alive(self) -> None:
        if self.remaining_wall_seconds() <= 0:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "wall-clock budget exhausted")
        if self.steps_used > self.budget.max_steps:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "step budget exhausted")

    def consume_step(self, n: int = 1) -> None:
        if self.steps_used + n > self.budget.max_steps:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "step budget exhausted")
        self.steps_used += n
        self.check_alive()

    def consume_candidates(self, n: int = 1) -> None:
        if self.candidate_evals + n > self.budget.max_candidate_evals:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "candidate evaluation budget exhausted")
        self.candidate_evals += n

    def consume_sim(self, n: int = 1) -> None:
        if self.simulator_calls + n > self.budget.max_simulator_calls:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "simulator call budget exhausted")
        self.simulator_calls += n

    def consume_bytes(self, n: int) -> None:
        if self.artifact_bytes + n > self.budget.max_artifact_bytes:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "artifact byte budget exhausted")
        self.artifact_bytes += n

    def refuse_allocation(self, *, nodes: Optional[int] = None, degree: Optional[int] = None,
                          depth: Optional[int] = None, experts: Optional[int] = None) -> None:
        if nodes is not None and nodes > self.budget.max_graph_nodes:
            raise WorldSeriesError(
                ErrorCode.BUDGET_EXHAUSTED,
                f"refusing allocation of {nodes} nodes > max_graph_nodes={self.budget.max_graph_nodes}",
            )
        if degree is not None and degree > self.budget.max_algebra_degree:
            raise WorldSeriesError(
                ErrorCode.BUDGET_EXHAUSTED,
                f"refusing algebra degree {degree} > max={self.budget.max_algebra_degree}",
            )
        if depth is not None and depth > self.budget.max_dsl_depth:
            raise WorldSeriesError(
                ErrorCode.BUDGET_EXHAUSTED,
                f"refusing DSL depth {depth} > max={self.budget.max_dsl_depth}",
            )
        if experts is not None and experts > self.budget.max_experts:
            raise WorldSeriesError(
                ErrorCode.BUDGET_EXHAUSTED,
                f"refusing experts {experts} > max={self.budget.max_experts}",
            )

    def snapshot(self) -> dict[str, float]:
        return {
            "steps_used": float(self.steps_used),
            "simulator_calls": float(self.simulator_calls),
            "candidate_evals": float(self.candidate_evals),
            "artifact_bytes": float(self.artifact_bytes),
            "wall_seconds": float(time.monotonic() - self.started_at),
            "remaining_wall_seconds": float(self.remaining_wall_seconds()),
        }
