from __future__ import annotations
from dataclasses import dataclass
from world_series.wcode.dsl import AST, BinOp, Var, Lit, ListOp, ListLit
from world_series.data.splits import FamilyRecord, split_by_family
from world_series.core.seeds import SeedBundle, SeededStreams

@dataclass
class SynthesisTask:
    family_id: str
    task_id: str
    target: AST
    public_examples: list[tuple[dict, int]]
    heldout: list[tuple[dict, int]]

def _family_programs():
    return {
        "plus_const": BinOp("+", Var("x"), Lit(1)),
        "times_const": BinOp("*", Var("x"), Lit(2)),
        "minus_const": BinOp("-", Var("x"), Lit(1)),
        "sum_list": ListOp("sum", ListLit((Var("x"), Lit(1), Lit(2)))),
    }

def make_examples(prog: AST, xs: list[int]):
    from world_series.wcode.interpreter import interpret, Fuel
    pubs, held = [], []
    for i, x in enumerate(xs):
        y = interpret(prog, {"x": x}, Fuel(64))
        # only int-producing programs in this suite
        item = ({"x": x}, int(y) if not isinstance(y, list) else len(y))
        (pubs if i < 3 else held).append(item)
    return pubs, held

def build_tasks(seed: int = 0) -> list[SynthesisTask]:
    out = []
    for fam, prog in _family_programs().items():
        # skip list sum for int IO mismatch — specialize
        if fam == "sum_list":
            pubs = [({"x": 1}, 4), ({"x": 2}, 5), ({"x": 3}, 6)]  # x+1+2
            held = [({"x": 10}, 13)]
        else:
            pubs, held = make_examples(prog, list(range(1, 7)))
        out.append(SynthesisTask(fam, f"{fam}/0", prog, pubs, held))
    return out

def split_tasks(tasks: list[SynthesisTask], seed: int):
    recs = [FamilyRecord(t.family_id, t.task_id, t) for t in tasks]
    ss = SeededStreams(SeedBundle.from_master(seed))
    # with 4 families use 50/50
    return split_by_family(recs, fractions={"train": 0.5, "dev": 0.5}, streams=ss)
