from __future__ import annotations

import json

import pytest

from world_series.core.artifacts import ArtifactStore
from world_series.core.config import load_and_validate, validate_config
from world_series.core.contracts import WorldSeriesError
from world_series.evaluation.runner import create_run


def config():
    return {"project": "qlearn", "experiment": "json-contract", "split": "smoke",
            "seed": 0, "device": "cpu", "budget": {}}


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
@pytest.mark.parametrize("writer", ["artifact", "metrics", "event"])
def test_nonfinite_evidence_is_rejected_before_any_write(tmp_path, value, writer):
    run = create_run(tmp_path, config())
    before = {p.relative_to(run.path).as_posix(): p.read_bytes() for p in run.path.rglob("*") if p.is_file()}
    with pytest.raises(WorldSeriesError, match="finite"):
        if writer == "artifact":
            run.store.write_json("invalid.json", {"nested": [value]})
        elif writer == "metrics":
            run.write_metrics({"loss": value})
        else:
            run.append_event("metric", {"loss": value})
    assert before == {p.relative_to(run.path).as_posix(): p.read_bytes() for p in run.path.rglob("*") if p.is_file()}
    assert not list(run.path.rglob(".pending-*"))


@pytest.mark.parametrize("suffix,addition", [
    (".json", ', "seed": 7'),
    (".json", ', "budget": {"max_steps": 1, "max_steps": 99}'),
    (".yaml", "seed: 7\n"),
    (".yaml", "model:\n  width: 4\n  width: 8\n"),
])
def test_ambiguous_config_keys_are_rejected(tmp_path, suffix, addition):
    if suffix == ".json":
        text = json.dumps(config())[:-1] + addition + "}"
    else:
        text = "project: qlearn\nexperiment: json-contract\nsplit: smoke\nseed: 0\ndevice: cpu\nbudget: {}\n" + addition
    path = tmp_path / ("config" + suffix)
    path.write_text(text)
    with pytest.raises(WorldSeriesError, match="duplicate"):
        load_and_validate(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_model_config_cannot_acquire_a_run_identity(value):
    cfg = config()
    cfg["model"] = {"learning_rate": value}
    with pytest.raises(WorldSeriesError, match="finite"):
        validate_config(cfg)


def test_boolean_seed_is_not_an_integer_experiment_identity():
    cfg = config()
    cfg["seed"] = True
    with pytest.raises(WorldSeriesError, match="seed"):
        validate_config(cfg)


def test_finite_artifact_bytes_keep_the_existing_format_and_hash(tmp_path):
    payload = {"loss": 0.125, "missing": None, "nested": [1, False]}
    store = ArtifactStore(tmp_path, run_id="fixture")
    ref = store.write_json("valid.json", payload)
    assert store.read_bytes(ref.relative_path) == (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    store.verify(ref)
