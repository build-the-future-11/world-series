from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from world_series.core.contracts import ErrorCode, WorldSeriesError

class ExpertState(str, Enum):
    CREATED = "CREATED"
    WARMUP = "WARMUP"
    ACTIVE = "ACTIVE"
    SLEEP = "SLEEP"
    REVIVED = "REVIVED"

@dataclass
class Expert:
    expert_id: int
    mean: float = 0.0
    var: float = 1.0
    weight: float = 0.0
    state: ExpertState = ExpertState.CREATED
    n_obs: int = 0

@dataclass
class ExpertBank:
    max_experts: int = 8
    experts: list[Expert] = field(default_factory=list)

    def spawn(self) -> Expert:
        if len(self.experts) >= self.max_experts:
            raise WorldSeriesError(ErrorCode.BUDGET_EXHAUSTED, "expert capacity reached")
        e = Expert(expert_id=len(self.experts), state=ExpertState.CREATED)
        self.experts.append(e)
        return e

    def transition(self, e: Expert, new_state: ExpertState) -> None:
        allowed = {
            ExpertState.CREATED: {ExpertState.WARMUP},
            ExpertState.WARMUP: {ExpertState.ACTIVE, ExpertState.SLEEP},
            ExpertState.ACTIVE: {ExpertState.SLEEP},
            ExpertState.SLEEP: {ExpertState.REVIVED, ExpertState.ACTIVE},
            ExpertState.REVIVED: {ExpertState.ACTIVE, ExpertState.SLEEP},
        }
        if new_state not in allowed[e.state]:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"illegal transition {e.state}->{new_state}")
        e.state = new_state

    def reset(self) -> None:
        self.experts.clear()
