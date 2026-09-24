from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from world_series.core.seeds import SeedBundle, SeededStreams
from world_series.data.generators import QuadraticTask, generate_quadratics
from world_series.data.splits import FamilyRecord, split_by_family

@dataclass
class SupportQueryTask:
    family_id: str
    task_id: str
    optimizee: QuadraticTask
    support_points: np.ndarray
    query_points: np.ndarray

    def support_batch(self):
        return self.support_points

    def query_batch(self):
        return self.query_points

def build_tasks(seed: int, n: int = 4, dim: int = 4) -> list[SupportQueryTask]:
    ss = SeededStreams(SeedBundle.from_master(seed))
    records = generate_quadratics(ss, n=n, dim=dim)
    out = []
    for rec in records:
        opt: QuadraticTask = rec.payload  # type: ignore
        support = ss.data.normal(size=(8, dim))
        query = ss.data.normal(size=(8, dim))
        out.append(SupportQueryTask(rec.family_id, rec.item_id, opt, support, query))
    return out

def family_split(tasks: list[SupportQueryTask], seed: int):
    records = [FamilyRecord(t.family_id, t.task_id, t) for t in tasks]
    ss = SeededStreams(SeedBundle.from_master(seed + 17))
    return split_by_family(records, fractions={"train": 0.5, "dev": 0.5}, streams=ss)
