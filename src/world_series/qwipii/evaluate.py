from __future__ import annotations
from fractions import Fraction
from typing import Any
from world_series.core.budgets import Budget, BudgetLedger
from world_series.core.contracts import RunStatus
from world_series.evaluation.runner import RunDirectory
from world_series.qwipii.domains import RingState
from world_series.qwipii.search import bfs, quotient_bfs, ranking_only_bfs, replay
from world_series.qwipii.projective import cross_ratio_invariant
from world_series.qwipii.certificates import Certificate
from world_series.qwipii.discovery import discover_and_verify

def _problems():
    return [
        RingState((1, 0, 2), (0, 1, 2)),
        RingState((2, 0, 1), (0, 1, 2)),
        RingState((0, 2, 1), (0, 1, 2)),
        RingState((1, 2, 0, 3), (0, 1, 2, 3)),
    ]

def run_experiment(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    budget = Budget(**cfg.get("budget", {}))
    ledger = BudgetLedger(budget)
    problems = _problems()
    rows = []
    for start in problems:
        path_b, exp_b, st_b = bfs(start, ledger, max_expansions=400)
        path_q, exp_q, st_q = quotient_bfs(start, ledger, max_expansions=400)
        # ranking-only: prefer states closer to goal by Hamming
        def ranker(s: RingState) -> float:
            return -sum(int(a != b) for a, b in zip(s.tokens, s.goal))
        path_r, exp_r, st_r = ranking_only_bfs(start, ledger, ranker, max_expansions=400)
        lifted_ok = False
        if path_q is not None:
            lifted_ok = replay(start, path_q).tokens == start.goal
        rows.append({
            "start": start.serialize(),
            "brute": {"status": st_b, "expansions": exp_b},
            "quotient": {"status": st_q, "expansions": exp_q, "lifted_ok": lifted_ok},
            "ranking_only": {"status": st_r, "expansions": exp_r},
        })
    disc = discover_and_verify(problems[:3])
    rejected_adv = [d for d in disc if d["kind"] == "adversarial" and d["label"] == "REJECTED"]
    verified = [d for d in disc if d["verified"]]
    pts = [Fraction(0), Fraction(1), Fraction(2), Fraction(3)]
    cr0, cr1 = cross_ratio_invariant(2, 1, 1, 1, pts)
    cert = Certificate(
        domain_version="ring-mixed-v1",
        property_name="quotient_vs_brute_and_ranking",
        assumptions=["finite dihedral canonicalization when verified", "ranking never prunes"],
        witness={"rows": rows, "discovery": disc},
        verification_method="replay_and_exhaustive_small_domain",
        ok=all(r["quotient"]["lifted_ok"] or r["quotient"]["status"] != "solved" for r in rows),
    )
    run.store.write_json("certificate.json", cert.to_dict())
    mean_brute = sum(r["brute"]["expansions"] for r in rows) / len(rows)
    mean_q = sum(r["quotient"]["expansions"] for r in rows) / len(rows)
    mean_r = sum(r["ranking_only"]["expansions"] for r in rows) / len(rows)
    return {
        "status": RunStatus.SUCCEEDED.value,
        "n_problems": len(rows),
        "mean_expansions": {"brute": mean_brute, "quotient": mean_q, "ranking_only": mean_r},
        "verification_overhead_note": "discovery+verify counted separately in discovery list",
        "discovery": disc,
        "adversarial_rejected": len(rejected_adv) > 0,
        "n_verified_transforms": len(verified),
        "cross_ratio_preserved": cr0 == cr1,
        "rows": rows,
        "cost": ledger.snapshot(),
        "primary_metric": "verified_solved_fraction",
        "verified_solved_fraction": sum(1 for r in rows if r["quotient"].get("lifted_ok")) / len(rows),
        "research_outcome": "INCONCLUSIVE",
        "note": "Small finite puzzles only; not Olympiad reasoning.",
    }
