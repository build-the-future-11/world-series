#!/usr/bin/env python3
"""Exhaustive correctness and cost audit, not a learned-discovery benchmark."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from world_series.qwipii.verifier import complete_domain, verify_automorphism
from world_series.qwipii.group_actions import dihedral_actions
from world_series.qwipii.search import bfs, certified_quotient_bfs, replay
from world_series.core.budgets import Budget, BudgetLedger


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    goals = [(0,1,2), (0,0,1,1), (0,1,0,1), (0,0,0,1,1), (0,1,0,1,0,1)]
    identity = {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(Path("src/world_series/qwipii").glob("*.py"))}
    (output / "protocol.json").write_text(json.dumps({"goals": goals, "source": identity,
        "scope": "all starts in five declared multiset domains; hand dihedral proposals",
        "limits": {"max_states": 10000, "max_expansions": 10000},
        "cost": "verification is measured separately; certified search includes revalidation and orbit closure",
        "confirmation": "DRAFT_NOT_AUTHORIZED"}, indent=2) + "\n")
    rows = []
    for goal in goals:
        domain = complete_domain(goal)
        begin = time.perf_counter_ns()
        proposals = [verify_automorphism(domain, act, fixed_goal=True)
                     for _, act in dihedral_actions(len(goal))]
        certificates = [c for c in proposals if c["ok"]]
        verification_ns = time.perf_counter_ns() - begin
        name = "".join(map(str, goal))
        (output / f"certificates-{name}.json").write_text(json.dumps(proposals, sort_keys=True) + "\n")
        for start in domain:
            methods = {}
            for method in ("brute", "certified"):
                ledger = BudgetLedger(Budget(max_candidate_evals=10000))
                begin = time.perf_counter_ns()
                if method == "brute":
                    path, expansions, status = bfs(start, ledger, max_expansions=10000)
                else:
                    path, expansions, status = certified_quotient_bfs(start, ledger, certificates, max_expansions=10000)
                elapsed = time.perf_counter_ns() - begin
                assert status == "solved" and replay(start, path).tokens == goal
                methods[method] = dict(path=path, expansions=expansions, elapsed_ns=elapsed, status=status)
            assert len(methods["brute"]["path"]) == len(methods["certified"]["path"])
            rows.append(dict(start=start.serialize(), methods=methods,
                             proposal_verification_ns=verification_ns, accepted=len(certificates)))
    (output / "rows.json").write_text(json.dumps(rows, indent=2) + "\n")
    summary = {"states": len(rows), "all_paths_replay": True, "all_shortest_lengths_match": True,
               "scope": "finite declared domains only; timing is one same-host observation per start",
               "expansions": {m: sum(r["methods"][m]["expansions"] for r in rows) for m in ("brute", "certified")},
               "search_elapsed_ns": {m: sum(r["methods"][m]["elapsed_ns"] for r in rows) for m in ("brute", "certified")}}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    main(parser.parse_args().output)
