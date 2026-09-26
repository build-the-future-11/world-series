"""QAPEN ridge-hard successor pilot (qapen-ridgehard-v1).

Nonlinear emission and long delayed cues. Does not modify historical lifecycle-v1.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from collections import deque
from pathlib import Path
import sys
import time
import traceback

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from world_series.core.identity import source_identity
from world_series.qapen.causal import CausalLifecycle, FrozenQuantizer, gaussian_nll

PROTOCOL = ROOT / "docs/closure/LOSS_REVERSAL_PROTOCOL.md"
SEEDS = [1009, 1103, 1201, 1301]
SCHEDULES = ["nonlinear_switch", "long_delayed_cue"]
NOISES = [0.1, 0.6]
METHODS = {
    "lifecycle_memory": {},
    "single_memory": {"lifecycle": False},
    "recent_memory": {"retrieval": "recent"},
    "rolling_ridge": None,
}


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stream(seed, schedule, noise, n=320):
    rng = np.random.default_rng(seed + 17)
    regime = np.zeros(n, dtype=int)
    if schedule == "nonlinear_switch":
        regime = (np.arange(n) // 64) % 2
    elif schedule == "long_delayed_cue":
        regime = (np.arange(n) // 80) % 2
    else:
        raise ValueError(schedule)
    coefficients = rng.uniform(0.25, 0.8, 2)
    offsets = np.array([-1.0, 1.0]) * rng.uniform(0.5, 1.5, 2)
    delay = 12 if schedule == "long_delayed_cue" else 0
    if delay:
        cue_regime = np.r_[regime[delay:], np.repeat(regime[-1], delay)]
    else:
        cue_regime = regime
    cues = offsets[cue_regime] + rng.normal(0, 0.3, n)
    context = []
    ys = []
    previous = 0.0
    recovery = []
    last_switch = -100
    for t in range(n):
        if t and regime[t] != regime[t - 1]:
            last_switch = t
        context.append([previous, cues[t]])
        linear = coefficients[regime[t]] * previous + offsets[regime[t]]
        if schedule == "nonlinear_switch":
            previous = float(np.tanh(linear)) + rng.normal(0, noise)
        else:
            previous = float(linear) + rng.normal(0, noise)
        ys.append(previous)
        recovery.append(t - last_switch < 8)
    return {
        "context": context,
        "targets": ys,
        "regime": regime.tolist(),
        "recovery": recovery,
        "seed": seed,
        "schedule": schedule,
        "noise": noise,
    }


class RollingRidge:
    def __init__(self, cap=2_000_000):
        self.window = deque(maxlen=32)
        self.operations = 0
        self.cap = cap
        self.pending = None
        self.variance = 1.0

    def predict(self, context):
        if self.pending is not None:
            raise RuntimeError("Observe pending prediction")
        x = np.r_[context, 1.0]
        self.operations += len(self.window) * 9 + 27
        if self.operations > self.cap:
            raise RuntimeError("Operation budget exhausted")
        if self.window:
            a = np.array([r[0] for r in self.window])
            b = np.array([r[1] for r in self.window])
            weights = np.linalg.solve(a.T @ a + 0.1 * np.eye(3), a.T @ b)
            mean = float(x @ weights)
        else:
            mean = 0.0
        self.pending = (x, mean, self.variance)
        return mean, self.variance

    def observe(self, y):
        x, mean, var = self.pending
        self.window.append((x, y))
        self.pending = None
        self.variance = max(0.05, 0.95 * self.variance + 0.05 * min((y - mean) ** 2, 100.0))
        return {
            "mean": mean,
            "variance": var,
            "nll": gaussian_nll(y, mean, var),
            "operations": self.operations,
        }


def run_cell(method, data, quantizer):
    raise RuntimeError("unused")


def run(output: Path, profile: bool = False):
    torch.set_num_threads(1)
    output.mkdir(parents=True, exist_ok=True)
    identity = {
        "source": source_identity(ROOT),
        "script_sha256": sha(Path(__file__)),
        "protocol_sha256": sha(PROTOCOL),
        "profile": profile,
        "confirmation": "DRAFT_NOT_AUTHORIZED",
        "study": "qapen-ridgehard-v1",
    }
    dump(output / "identity.json", identity)
    seeds = SEEDS[:1] if profile else SEEDS
    schedules = SCHEDULES[:1] if profile else SCHEDULES
    noises = [0.1] if profile else NOISES
    # Fit codebook once on separate streams
    training = np.concatenate([np.asarray(stream(s, "nonlinear_switch", 0.3)["context"], dtype=np.float64) for s in [31, 37, 41, 43]])
    quantizer = FrozenQuantizer.fit(training)
    receipts = []
    wall = time.perf_counter()
    with (output / "worker.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for seed in seeds:
            for schedule in schedules:
                for noise in noises:
                    data = stream(seed, schedule, noise)
                    for method in METHODS:
                        if time.perf_counter() - wall > 1800:
                            raise RuntimeError("wall ceiling")
                        key = f"{seed}-{schedule}-{noise}-{method}"
                        path = output / f"{key}.json"
                        if path.exists():
                            receipts.append(json.loads(path.read_text()))
                            continue
                        start = time.perf_counter()
                        if METHODS[method] is None:
                            model = RollingRidge()
                        else:
                            model = CausalLifecycle(quantizer, seed=seed, **METHODS[method])
                        rows = []
                        failure = None
                        try:
                            for context, y in zip(data["context"], data["targets"]):
                                model.predict(context)
                                obs = model.observe(y)
                                rows.append({"nll": float(obs["nll"])})
                        except Exception as exc:
                            failure = {"message": str(exc), "traceback": traceback.format_exc()}
                        result = {
                            "key": key,
                            "seed": seed,
                            "schedule": schedule,
                            "noise": noise,
                            "method": method,
                            "mean_nll": float(np.mean([r["nll"] for r in rows])) if rows and failure is None else None,
                            "seconds": time.perf_counter() - start,
                            "complete": len(rows) == len(data["targets"]) and failure is None,
                            "failure": failure,
                            "n": len(rows),
                        }
                        dump(path, result)
                        receipts.append(result)
                        print(json.dumps({"key": key, "mean_nll": result["mean_nll"], "seconds": result["seconds"]}), flush=True)
    # Paired seed means over all schedule×noise for lifecycle vs ridge
    by_seed_method = {}
    for r in receipts:
        if not r["complete"]:
            continue
        by_seed_method.setdefault((r["seed"], r["method"]), []).append(r["mean_nll"])
    seed_means = {
        (seed, method): float(np.mean(vals)) for (seed, method), vals in by_seed_method.items() if vals
    }
    deltas = []
    for seed in seeds:
        a = seed_means.get((seed, "lifecycle_memory"))
        b = seed_means.get((seed, "rolling_ridge"))
        if a is not None and b is not None:
            deltas.append(a - b)
    decision = {
        "n_paired_seeds": len(deltas),
        "mean_lifecycle_minus_ridge": float(np.mean(deltas)) if deltas else None,
        "label": (
            "INCOMPLETE"
            if len(deltas) < len(seeds)
            else ("LIFECYCLE_HELPS" if float(np.mean(deltas)) < 0 else "RIDGE_STILL_WINS_OR_TIE")
        ),
    }
    dump(
        output / "summary.json",
        {
            "study": "qapen-ridgehard-v1",
            "identity": identity,
            "n_receipts": len(receipts),
            "complete": all(r.get("complete") for r in receipts),
            "decision": decision,
            "elapsed_seconds": time.perf_counter() - wall,
            "historical_primary_unchanged": "campaigns/qapen-lifecycle-v1",
        },
    )
    print(json.dumps(decision), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--profile", action="store_true")
    a = p.parse_args()
    try:
        run(a.output, a.profile)
    except BaseException as exc:
        a.output.mkdir(exist_ok=True, parents=True)
        dump(
            a.output / f"failure-{time.time_ns()}.json",
            {"message": str(exc), "traceback": traceback.format_exc()},
        )
        raise
