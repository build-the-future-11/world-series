#!/usr/bin/env python3
"""Aggregate multiseed outputs from run manifests — real artifacts only."""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict
import math

ROOT = Path(__file__).resolve().parents[1]
runs = [p for p in (ROOT / "runs").iterdir() if p.is_dir()]
by = defaultdict(list)
for r in runs:
    m = json.loads((r / "manifest.json").read_text())
    if m.get("experiment") != "dev_multiseed":
        continue
    met = {}
    if (r / "metrics.json").is_file():
        met = json.loads((r / "metrics.json").read_text())
    by[m["project"]].append({"run_id": r.name, "seed": m.get("seed"), "status": m.get("status"), "metrics": met})

def mean_std(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and (math.isnan(x) or math.isinf(x)))]
    if not xs:
        return {"mean": None, "std": None, "n": 0}
    mu = sum(xs) / len(xs)
    var = sum((x - mu) ** 2 for x in xs) / max(len(xs) - 1, 1)
    return {"mean": mu, "std": var ** 0.5, "n": len(xs)}

summary = {"note": "Development multiseed only; DRAFT_NOT_AUTHORIZED; not confirmation.", "projects": {}}
for proj, rows in sorted(by.items()):
    primaries = []
    for row in rows:
        met = row["metrics"]
        v = met.get("primary_value")
        if v is None and isinstance(met.get("mean_nll"), dict):
            v = met["mean_nll"].get("qapen")
        if v is None:
            v = met.get("verified_solved_fraction")
        if v is None and isinstance(met.get("completion_rates"), dict):
            v = met["completion_rates"].get("learned")
        primaries.append(v if isinstance(v, (int, float)) else None)
    summary["projects"][proj] = {
        "runs": [{"run_id": r["run_id"], "seed": r["seed"], "status": r["status"]} for r in rows],
        "primary_aggregate": mean_std(primaries),
        "research_outcomes": list({r["metrics"].get("research_outcome") for r in rows}),
    }

out = ROOT / "experiments" / "RESULTS_SUMMARY.md"
lines = ["# RESULTS_SUMMARY (real multiseed artifacts only)\n\n", summary["note"], "\n\n"]
if not by:
    lines.append("_No `experiment: dev_multiseed` runs found yet._\n")
else:
    lines.append("| Project | n | primary mean | std | outcomes |\n|---|---:|---:|---:|---|\n")
    for proj, block in summary["projects"].items():
        agg = block["primary_aggregate"]
        lines.append(
            f"| `{proj}` | {agg['n']} | {agg['mean']} | {agg['std']} | {', '.join(str(x) for x in block['research_outcomes'])} |\n"
        )
    lines.append("\n## Raw run IDs\n\n")
    lines.append("```json\n" + json.dumps(summary, indent=2) + "\n```\n")
out.write_text("".join(lines), encoding="utf-8")
(ROOT / "experiments" / "results_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print("wrote", out)
