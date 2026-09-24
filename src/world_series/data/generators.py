"""Shared tiny generators used by smoke configs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from world_series.core.seeds import SeedBundle, SeededStreams
from world_series.data.splits import FamilyRecord


@dataclass
class QuadraticTask:
    family_id: str
    task_id: str
    A: np.ndarray
    b: np.ndarray
    x0: np.ndarray

    def loss(self, x: np.ndarray) -> float:
        return float(0.5 * x @ self.A @ x + self.b @ x)

    def grad(self, x: np.ndarray) -> np.ndarray:
        return self.A @ x + self.b


def generate_quadratics(streams: SeededStreams, n: int = 4, dim: int = 8) -> list[FamilyRecord]:
    out: list[FamilyRecord] = []
    for i in range(n):
        family = f"cond_{(i % 2) + 1}"
        B = streams.data.normal(size=(dim, dim))
        A = B.T @ B + (0.1 + 0.5 * (i % 2)) * np.eye(dim)
        b = streams.data.normal(size=(dim,))
        x0 = streams.data.normal(size=(dim,))
        task = QuadraticTask(family_id=family, task_id=f"{family}/q{i}", A=A, b=b, x0=x0)
        out.append(FamilyRecord(family_id=family, item_id=task.task_id, payload=task))
    return out


def smoke_payload(project: str, seed: int) -> dict[str, Any]:
    ss = SeededStreams(SeedBundle.from_master(seed))
    if project == "qlearn":
        tasks = generate_quadratics(ss, n=2, dim=4)
        return {"n_tasks": len(tasks), "families": sorted({t.family_id for t in tasks})}
    return {"project": project, "note": "generic smoke payload"}
