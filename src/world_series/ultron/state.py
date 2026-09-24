from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class EpisodeState:
    goal: str
    task_type: str
    evidence_ids: tuple[str, ...]
    capabilities: tuple[str, ...]
    remaining_budget_steps: int
    failure_history: tuple[str, ...] = ()
