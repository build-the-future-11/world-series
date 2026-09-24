from __future__ import annotations
from dataclasses import dataclass
import math

TASK_FEATURES = {
    "invariant_puzzle": (1.0, 0.0, 0.0),
    "dsl_synthesis": (0.0, 1.0, 0.0),
    "law_id": (0.0, 0.0, 1.0),
}

OPS = ["solve_invariant_problem", "synthesize_dsl_program", "identify_dynamical_law"]

@dataclass
class LinearRouter:
    """Development-only contextual bandit / linear ranker over task features."""
    weights: dict[str, list[float]]

    @staticmethod
    def from_oracle_traces(traces: list[dict]) -> "LinearRouter":
        # one-shot: set weight of correct op high on that feature
        w = {op: [0.0, 0.0, 0.0] for op in OPS}
        for tr in traces:
            feat = TASK_FEATURES[tr["task_type"]]
            op = tr["best_op"]
            for i, f in enumerate(feat):
                w[op][i] += f
        return LinearRouter(w)

    def score(self, task_type: str, op: str) -> float:
        feat = TASK_FEATURES.get(task_type, (0, 0, 0))
        ww = self.weights.get(op, [0, 0, 0])
        return sum(a * b for a, b in zip(feat, ww))

    def choose(self, task_type: str, available: list[str]) -> str | None:
        cands = [o for o in OPS if o in available]
        if not cands:
            return None
        scored = [(self.score(task_type, o), o) for o in cands]
        scored.sort(key=lambda x: (-x[0], x[1]))
        return scored[0][1]
