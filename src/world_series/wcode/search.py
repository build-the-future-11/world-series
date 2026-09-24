from __future__ import annotations
from world_series.wcode.dsl import Lit, Var, BinOp, ListLit, ListOp, AST
from world_series.wcode.interpreter import interpret, Fuel, validate_ast
from world_series.wcode.encoder import score_candidate
from world_series.core.budgets import BudgetLedger

def enumerate_small_programs() -> list[AST]:
    xs = [Lit(0), Lit(1), Lit(2), Var("x")]
    progs: list[AST] = list(xs)
    for a in xs:
        for b in xs:
            for op in ("+", "-", "*"):
                progs.append(BinOp(op, a, b))
    progs.append(ListOp("sum", ListLit((Var("x"), Lit(1), Lit(2)))))
    return progs

def synthesize(examples: list[tuple[dict, int]], ledger: BudgetLedger, max_candidates: int = 64, rank_mode: str = "uniform"):
    pool = enumerate_small_programs()
    # shared enumerator: same pool for all modes; only order changes
    ranked = sorted(pool, key=lambda p: -score_candidate(p, examples, mode=rank_mode))
    for prog in ranked[:max_candidates]:
        ledger.consume_candidates(1)
        try:
            validate_ast(prog, max_depth=6, max_nodes=64)
            ok = True
            for env, y in examples:
                out = interpret(prog, env, Fuel(64))
                if out != y:
                    ok = False
                    break
            if ok:
                return prog, True, ledger.candidate_evals
        except Exception:
            continue
    return None, False, ledger.candidate_evals

def compare_rankers(examples, heldout, ledger_factory, max_candidates=64):
    from world_series.wcode.verifier import verify_program
    results = {}
    for mode in ("uniform", "length", "token", "flat", "hierarchical"):
        # fresh ledger per mode but identical budget cap
        ledger = ledger_factory()
        prog, found, used = synthesize(examples, ledger, max_candidates=max_candidates, rank_mode=mode)
        ver = {"ok": False}
        if found and prog is not None:
            ver = verify_program(prog, heldout)
        results[mode] = {"found": found, "candidates_used": used, "verifier": ver}
    return results
