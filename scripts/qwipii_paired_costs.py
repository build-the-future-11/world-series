"""Paired, family-clustered QWIPII end-to-end latency analysis.

Input JSONL: family, instance, method, solved, optimal, runtime_ms,
optional offline_ms and planned_queries. Development analysis only.
"""
import argparse
import json
import math
import random
from collections import defaultdict

REQUIRED = ("family", "instance", "method", "solved", "optimal", "runtime_ms")


def validate_row(row, n):
    if not isinstance(row, dict):
        raise ValueError(f"row {n}: expected an object")
    missing = [key for key in REQUIRED if key not in row]
    if missing:
        raise ValueError(f"row {n}: missing {missing}")
    if not isinstance(row["solved"], bool) or not isinstance(row["optimal"], bool):
        raise ValueError(f"row {n}: solved/optimal must be booleans")
    if row["optimal"] and not row["solved"]:
        raise ValueError(f"row {n}: optimal without solved")
    for key in ("runtime_ms", "offline_ms"):
        value = row.get(key, 0)
        try:
            valid = (not isinstance(value, bool) and isinstance(value, (int, float))
                     and math.isfinite(value) and value >= 0)
        except OverflowError:
            valid = False
        if not valid:
            raise ValueError(f"row {n}: invalid {key}")
    q = row.get("planned_queries", 1)
    if isinstance(q, bool) or not isinstance(q, int) or q <= 0:
        raise ValueError(f"row {n}: invalid planned_queries")


def read_rows(path):
    rows = []
    with open(path, encoding="utf-8") as stream:
        for n, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            validate_row(row, n)
            rows.append(row)
    if not rows:
        raise ValueError("empty file")
    return rows


def compare(rows, candidate="learned", baseline="brute", bootstrap=2000, seed=1729):
    if candidate == baseline:
        raise ValueError("candidate and baseline must differ")
    if type(bootstrap) is not int or bootstrap < 2:
        raise ValueError("at least two bootstrap replicates required")
    indexed = {}
    for n, row in enumerate(rows, 1):
        validate_row(row, n)
        key = (str(row["family"]), str(row["instance"]), str(row["method"]))
        if key in indexed:
            raise ValueError(f"duplicate cell: {key}")
        indexed[key] = row
    candidate_keys = {(f, i) for f, i, m in indexed if m == candidate}
    baseline_keys = {(f, i) for f, i, m in indexed if m == baseline}
    if candidate_keys != baseline_keys:
        raise ValueError("unpaired cell: both method sets must match")
    families = defaultdict(list)
    for (family, instance, method), a in indexed.items():
        if method != candidate:
            continue
        b = indexed.get((family, instance, baseline))
        if b is None:
            raise ValueError(f"unpaired cell: {family}/{instance}")
        if not all(v["solved"] and v["optimal"] for v in (a, b)):
            raise ValueError(f"incorrect path: {family}/{instance}")
        def cost(v):
            return (float(v["runtime_ms"])
                    + float(v.get("offline_ms", 0)) / v.get("planned_queries", 1))
        ca, cb = cost(a), cost(b)
        if not all(math.isfinite(value) and value > 0 for value in (ca, cb)):
            raise ValueError("finite positive cost required for log effect")
        # Forming ca / cb first can overflow or underflow even though the
        # logarithmic effect and its family mean remain representable.
        families[family].append(math.log(ca) - math.log(cb))
    if not families:
        raise ValueError("no paired observations")
    means = [math.fsum(families[f]) / len(families[f]) for f in sorted(families)]
    observed = math.fsum(means) / len(means)
    rng = random.Random(seed)
    draws = (sorted(math.fsum(means[rng.randrange(len(means))] for _ in means) / len(means)
                    for _ in range(bootstrap)) if len(means) >= 2 else None)
    def ratio(log_effect):
        try:
            value = math.exp(log_effect)
        except OverflowError as exc:
            raise ValueError("cost ratio exceeds finite floating-point range") from exc
        if not math.isfinite(value) or value <= 0:
            raise ValueError("cost ratio exceeds positive floating-point range")
        return value
    return {
        "candidate": candidate, "baseline": baseline,
        "family_count": len(families),
        "paired_instances": sum(map(len, families.values())),
        "family_equal_weight_geomean_ratio": ratio(observed),
        "family_bootstrap_95pct_ratio": ([
            ratio(draws[int(.025 * (bootstrap - 1))]),
            ratio(draws[int(.975 * (bootstrap - 1))])] if draws is not None else None),
        "uncertainty_warning": ("Only one independent family; no bootstrap interval"
                                if draws is None else None),
        "method": "paired family-cluster bootstrap",
        "status": "DEVELOPMENT_ONLY_NOT_CONFIRMATORY",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("jsonl")
    p.add_argument("--candidate", default="learned")
    p.add_argument("--baseline", default="brute")
    a = p.parse_args()
    print(json.dumps(compare(read_rows(a.jsonl), a.candidate, a.baseline), indent=2))


if __name__ == "__main__":
    main()
