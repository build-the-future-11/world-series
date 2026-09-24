"""Cost accounting labels."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CostLedger:
    wall_seconds: float = 0.0
    steps: int = 0
    candidate_evals: int = 0
    simulator_calls: int = 0
    meta_training_seconds: float = 0.0
    adaptation_seconds: float = 0.0
    extra: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict[str, float]:
        out = {
            "wall_seconds": self.wall_seconds,
            "steps": float(self.steps),
            "candidate_evals": float(self.candidate_evals),
            "simulator_calls": float(self.simulator_calls),
            "meta_training_seconds": self.meta_training_seconds,
            "adaptation_seconds": self.adaptation_seconds,
        }
        out.update(self.extra)
        return out
