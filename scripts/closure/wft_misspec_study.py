"""WFT prior-misspecification falsification (wft-misspec-v1).

Preserves historical wft-constraints-v1 outcomes. New immutable campaign only.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from world_series.core.identity import source_identity
from world_series.wft.constraints import DiffusionField, domain, teacher, spectral_projection

PROTOCOL = ROOT / "docs/closure/LOSS_REVERSAL_PROTOCOL.md"
SEEDS = [2203, 2213, 2221, 2237, 2243]
STRATA = ["compatible", "sine_perturbed", "unequal_degree"]
METHODS = {
    "unconstrained": (False, False, False),
    "both": (True, True, False),
    "wrong_symmetry": (True, False, True),
}


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def state_hash(model):
    return hashlib.sha256(b"".join(p.detach().numpy().tobytes() for p in model.parameters())).hexdigest()


def make_data(seed, samples, noise, stratum):
    model = teacher(seed, stratum=stratum)
    rng = np.random.default_rng(seed * 1009 + samples * 17 + int(noise * 10) + sum(map(ord, stratum)))
    data = {}
    with torch.no_grad():
        for level in [0, 1]:
            graph = domain(16, level=level)
            n = len(graph.mass)
            x = model.transition(graph, 0.4) @ torch.tensor(rng.normal(size=(n, samples)))
            y = model.transition(graph) @ x
            data[f"train_x_{level}"] = x.numpy()
            data[f"train_y_{level}"] = y.numpy() + rng.normal(0, noise, size=y.shape)
        for groups in [16, 32, 64]:
            for topology in ["cycle", "path"]:
                for level in [0, 1]:
                    graph = domain(groups, topology, level)
                    key = f"{groups}-{topology}-{level}"
                    x = model.transition(graph, 0.4) @ torch.tensor(rng.normal(size=(len(graph.mass), 16)))
                    data["x-" + key] = x.numpy()
                    data["y-" + key] = (model.transition(graph) @ x).numpy()
    return data


def fit(observed_inputs, observed_outputs, method):
    model = DiffusionField()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.03)
    graphs = [domain(16, level=level) for level in [0, 1]]
    inputs = [torch.as_tensor(x) for x in observed_inputs]
    outputs = [torch.as_tensor(y) for y in observed_outputs]
    sym_on, scale_on, wrong = METHODS[method]
    history = []
    start = time.perf_counter()
    for step in range(100):
        optimizer.zero_grad()
        prediction = sum(
            ((model.transition(g) @ x - y) ** 2 * g.mass[:, None]).sum()
            / (y.square() * g.mass[:, None]).sum().clamp_min(1e-12)
            for g, x, y in zip(graphs, inputs, outputs)
        ) / 2
        sym, scale = model.penalties(*graphs, wrong=wrong)
        penalty = 0.1 * (sym if sym_on else 0.0) + 0.1 * (scale if scale_on else 0.0)
        loss = prediction + penalty
        if not torch.isfinite(loss):
            raise FloatingPointError("Nonfinite objective")
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 10.0, error_if_nonfinite=True)
        optimizer.step()
        history.append(
            {
                "step": step + 1,
                "prediction_loss": float(prediction.detach()),
                "symmetry_penalty": float(sym.detach()),
                "resolution_penalty": float(scale.detach()),
                "objective": float(loss.detach()),
            }
        )
    return model, history, {"training_seconds": time.perf_counter() - start}


def evaluate(model, data):
    rows = []
    frozen = state_hash(model)
    with torch.no_grad():
        for groups in [16, 32, 64]:
            for topology in ["cycle", "path"]:
                for level in [0, 1]:
                    graph = domain(groups, topology, level)
                    key = f"{groups}-{topology}-{level}"
                    x = data["x-" + key]
                    y = data["y-" + key]
                    l = model.laplacian(graph)
                    transition = torch.matrix_exp(-0.15 * l / graph.mass[:, None])
                    prediction = (transition @ torch.as_tensor(x)).numpy()
                    mass = graph.mass.numpy()
                    denom = float(np.sum(mass[:, None] * y**2))
                    error = float(np.sum(mass[:, None] * (prediction - y) ** 2) / denom)
                    assert state_hash(model) == frozen
                    rows.append(
                        {
                            "groups": groups,
                            "topology": topology,
                            "level": level,
                            "relative_prediction_error": error,
                            "transfer": groups > 16,
                        }
                    )
    return rows


def aggregate(receipts):
    by = {}
    for receipt in receipts:
        if not receipt.get("complete"):
            continue
        key = (receipt["stratum"], receipt["method"])
        by.setdefault(key, []).append(receipt["transfer_mean_error"])
    summary = []
    for (stratum, method), values in sorted(by.items()):
        summary.append(
            {
                "stratum": stratum,
                "method": method,
                "n_seeds": len(values),
                "mean_transfer_error": float(np.mean(values)),
                "std_transfer_error": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
            }
        )
    decisions = []
    for stratum in STRATA:
        u = next((r for r in summary if r["stratum"] == stratum and r["method"] == "unconstrained"), None)
        b = next((r for r in summary if r["stratum"] == stratum and r["method"] == "both"), None)
        if not u or not b or u["n_seeds"] < 1 or b["n_seeds"] < 1:
            decisions.append({"stratum": stratum, "label": "INCOMPLETE", "delta_both_minus_unconstrained": None})
            continue
        delta = b["mean_transfer_error"] - u["mean_transfer_error"]
        label = "CONSTRAINTS_HELP" if delta < 0 else "CONSTRAINTS_HURT_OR_NEUTRAL"
        decisions.append({"stratum": stratum, "label": label, "delta_both_minus_unconstrained": delta})
    return summary, decisions


def run(output: Path, profile: bool = False):
    torch.set_num_threads(1)
    output.mkdir(parents=True, exist_ok=True)
    identity = {
        "source": source_identity(ROOT),
        "script_sha256": sha(Path(__file__)),
        "protocol_sha256": sha(PROTOCOL),
        "profile": profile,
        "confirmation": "DRAFT_NOT_AUTHORIZED",
        "study": "wft-misspec-v1",
    }
    ident = output / "identity.json"
    if ident.exists():
        old = json.loads(ident.read_text())
        assert old["source"]["content_hash"] == identity["source"]["content_hash"]
        assert old["script_sha256"] == identity["script_sha256"]
        assert old["protocol_sha256"] == identity["protocol_sha256"]
    else:
        dump(ident, identity)

    seeds = SEEDS[:1] if profile else SEEDS
    samples_list = [4] if profile else [4, 16]
    noises = [0.1] if profile else [0.0, 0.1]
    strata = STRATA[:1] if profile else STRATA
    receipts = []
    wall_start = time.perf_counter()
    with (output / "worker.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for stratum in strata:
            for seed in seeds:
                for samples in samples_list:
                    for noise in noises:
                        data_key = f"{stratum}-{seed}-{samples}-{noise}-data"
                        data_path = output / f"{data_key}.npz"
                        if not data_path.exists():
                            data = make_data(seed, samples, noise, stratum)
                            np.savez_compressed(data_path, **data)
                            dump(
                                output / f"{data_key}.json",
                                {"stratum": stratum, "seed": seed, "samples": samples, "noise": noise, "sha256": sha(data_path)},
                            )
                        else:
                            with np.load(data_path) as loaded:
                                data = {k: loaded[k] for k in loaded.files}
                        for method in [*METHODS, "fixed_geometry", "oracle_true_operator"]:
                            if time.perf_counter() - wall_start > 1800:
                                raise RuntimeError("Study wall ceiling reached")
                            assert source_identity(ROOT)["content_hash"] == identity["source"]["content_hash"]
                            key = f"{stratum}-{seed}-{samples}-{noise}-{method}"
                            receipt_path = output / f"{key}-receipt.json"
                            if receipt_path.exists():
                                receipt = json.loads(receipt_path.read_text())
                                for filename, digest in receipt["files"].items():
                                    assert sha(output / filename) == digest
                                receipts.append(receipt)
                                continue
                            if method in METHODS:
                                model, history, cost = fit(
                                    [data[f"train_x_{i}"] for i in [0, 1]],
                                    [data[f"train_y_{i}"] for i in [0, 1]],
                                    method,
                                )
                            else:
                                model = teacher(seed, stratum=stratum) if method == "oracle_true_operator" else DiffusionField()
                                history, cost = [], {"training_seconds": 0.0}
                            rows = evaluate(model, data)
                            transfer = [r["relative_prediction_error"] for r in rows if r["transfer"]]
                            result = {
                                "stratum": stratum,
                                "seed": seed,
                                "samples": samples,
                                "noise": noise,
                                "method": method,
                                "rows": rows,
                                "history": history,
                                "cost": cost,
                                "transfer_mean_error": float(np.mean(transfer)),
                                "complete": len(rows) == 12,
                                "scope": "Prior-misspecification falsification; not a replacement of wft-constraints-v1",
                            }
                            result_path = output / f"{key}.json"
                            dump(result_path, result)
                            ckpt = output / f"{key}.pt"
                            torch.save(model.state_dict(), ckpt)
                            receipt = {
                                "key": key,
                                "stratum": stratum,
                                "seed": seed,
                                "samples": samples,
                                "noise": noise,
                                "method": method,
                                "complete": result["complete"],
                                "transfer_mean_error": result["transfer_mean_error"],
                                "files": {p.name: sha(p) for p in [result_path, ckpt, data_path]},
                            }
                            dump(receipt_path, receipt)
                            receipts.append(receipt)
                            print(json.dumps({k: receipt[k] for k in ("key", "transfer_mean_error", "complete")}), flush=True)
    summary_rows, decisions = aggregate(receipts)
    dump(
        output / "summary.json",
        {
            "study": "wft-misspec-v1",
            "complete": all(r.get("complete") for r in receipts),
            "n_receipts": len(receipts),
            "identity": identity,
            "elapsed_seconds": time.perf_counter() - wall_start,
            "per_stratum_method": summary_rows,
            "decisions": decisions,
            "historical_primary_unchanged": "campaigns/wft-constraints-v1",
        },
    )
    print(json.dumps({"decisions": decisions, "elapsed": time.perf_counter() - wall_start}), flush=True)


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
            {"message": str(exc), "traceback": traceback.format_exc(), "source": source_identity(ROOT)},
        )
        raise
