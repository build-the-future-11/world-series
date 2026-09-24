#!/usr/bin/env python3
"""Frozen bounded development study; ring size transfer is not new puzzle families."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from world_series.qwipii.discovery import propose_grammar
from world_series.qwipii.verifier import complete_domain, verify_automorphism
from world_series.qwipii.learned_discovery import ProposalRanker, proposal_features, certificate_utility, ranked_certificates
from world_series.qwipii.search import bfs, quotient_bfs, ranking_only_bfs, certified_quotient_bfs, replay
from world_series.core.budgets import Budget, BudgetLedger

TRAIN = [(0,0,1), (0,1,2), (0,0,1,1), (0,1,0,1), (0,0,1,2)]
SELECT = [(0,0,0,1,1), (0,0,1,0,1), (0,0,1,1,2)]
HELD = [(0,1,0,1,0,1), (0,0,0,1,1,1), (0,1,2,0,1,2), (0,0,1,1,2,2)]
SEEDS = [2801,2803,2819,2833,2837,2843,2851,2857]


def dump(path, obj):
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


class MaskedRanker:
    def __init__(self, model, mask):
        self.model, self.mask = model, mask
    def score(self, goal, act, probes):
        return float((proposal_features(goal, act, probes) * self.mask) @ self.model.weights)


class RandomRanker:
    def __init__(self, rng): self.rng = rng
    def score(self, goal, act, probes): return float(self.rng.random())


def training_rows(goals, rng):
    x, y = [], []
    for goal in goals:
        domain = complete_domain(goal, max_states=1000)
        probes = [domain[i] for i in rng.choice(len(domain), size=min(3,len(domain)), replace=False)]
        for _, act, _ in propose_grammar(len(goal)):
            x.append(proposal_features(goal, act, probes))
            y.append(certificate_utility(verify_automorphism(domain, act, fixed_goal=True)))
    return np.asarray(x), np.asarray(y)


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    source = list(Path("src/world_series/qwipii").glob("*.py")) + [Path(__file__)]
    dump(output / "protocol.json", dict(train=TRAIN, selection=SELECT, held=HELD, seeds=SEEDS,
        source={str(p.relative_to(Path.cwd()) if p.is_absolute() else p):hashlib.sha256(p.read_bytes()).hexdigest() for p in source},
        verification_budget=4, starts_per_goal=4, probes=3, max_states=1000, max_expansions=1000,
        ridge_grid=[0.001,0.01,0.1,1.0], selection_rule="minimum proposal utility MSE; ties lower ridge",
        primary="paired end-to-end elapsed time and solved fraction versus random proposal ordering",
        costs="per-query probe enumeration, scoring, verification, certificate revalidation, orbit construction and search; training/selection measured separately",
        scope="development ring-size transfer; four fixed held goal patterns, not new puzzle families or independent confirmation",
        failure="retain failed rows; do not impute timing advantage or change caps; no population significance claim",
        confirmation="DRAFT_NOT_AUTHORIZED"))
    rows = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        begin = time.perf_counter_ns()
        x,y = training_rows(TRAIN,rng)
        sx,sy = training_rows(SELECT,rng)
        models, details = {}, {}
        for method, masked_index in [("learned",None),("no_goal_feature",3),("no_transition_feature",6)]:
            mask = np.ones(7)
            if masked_index is not None: mask[masked_index] = 0
            candidates = []
            for ridge in [0.001,0.01,0.1,1.0]:
                model = ProposalRanker.fit(x*mask,y,ridge)
                loss = float(np.mean(((sx*mask)@model.weights-sy)**2))
                candidates.append((loss,ridge,model))
            loss,ridge,model = min(candidates,key=lambda a:(a[0],a[1]))
            models[method] = MaskedRanker(model,mask)
            details[method] = dict(model=model.to_dict(),mask=mask.tolist(),ridge=ridge,
                                   selection_mse=loss,selection_candidates=[[a,b] for a,b,_ in candidates])
        training_ns = time.perf_counter_ns()-begin
        dump(output / f"training-{seed}.json",dict(x=x.tolist(),y=y.tolist(),sx=sx.tolist(),sy=sy.tolist(),models=details,elapsed_ns=training_ns))
        for goal in HELD:
            domain = complete_domain(goal,max_states=1000)
            indices = rng.choice(len(domain),size=4,replace=False)
            probe_indices = rng.choice(len(domain),size=3,replace=False)
            for index in indices:
                start = domain[index]
                methods = ["brute","hand_quotient","ranking_only","random","learned","no_goal_feature","no_transition_feature"]
                rng.shuffle(methods)
                for method in methods:
                    begin = time.perf_counter_ns()
                    attempts = []
                    ledger = BudgetLedger(Budget(max_candidate_evals=1000))
                    try:
                        if method == "brute": path,n,status = bfs(start,ledger,max_expansions=1000)
                        elif method == "hand_quotient": path,n,status = quotient_bfs(start,ledger,max_expansions=1000)
                        elif method == "ranking_only":
                            path,n,status = ranking_only_bfs(start,ledger,lambda s:-sum(a!=b for a,b in zip(s.tokens,s.goal)),max_expansions=1000)
                        else:
                            # Charge enumeration used to construct the sampled public probes.
                            probe_domain = complete_domain(goal,max_states=1000)
                            probes = [probe_domain[i] for i in probe_indices]
                            ranker = RandomRanker(rng) if method == "random" else models[method]
                            certs,attempts = ranked_certificates(goal,probes,ranker,4,max_states=1000)
                            path,n,status = certified_quotient_bfs(start,ledger,certs,max_expansions=1000,max_states=1000)
                        elapsed = time.perf_counter_ns()-begin
                        valid = path is not None and replay(start,path).tokens == goal
                        row = dict(seed=seed,start=start.serialize(),method=method,path=path,expansions=n,status=status,
                                   replay_ok=valid,elapsed_ns=elapsed,attempts=attempts)
                    except Exception as exc:
                        row = dict(seed=seed,start=start.serialize(),method=method,status="failed",error=repr(exc),elapsed_ns=time.perf_counter_ns()-begin)
                    rows.append(row)
                    with (output / "rows.jsonl").open("a") as handle: handle.write(json.dumps(row,sort_keys=True)+"\n")
        print(f"Finished seed {seed}",flush=True)
    summary = {}
    for method in sorted({r["method"] for r in rows}):
        selected = [r for r in rows if r["method"]==method]
        summary[method] = dict(cells=len(selected),solved=sum(r.get("replay_ok",False) for r in selected),
                               mean_elapsed_ms=float(np.mean([r["elapsed_ns"] for r in selected]))/1e6,
                               mean_expansions=float(np.mean([r.get("expansions",float("nan")) for r in selected])))
    dump(output / "summary.json",summary)
    print(json.dumps(summary))


if __name__ == "__main__":
    parser=argparse.ArgumentParser(); parser.add_argument("--output",type=Path,required=True)
    main(parser.parse_args().output)
