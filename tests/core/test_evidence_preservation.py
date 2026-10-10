"""Evidence must survive retries, concurrent writers and interrupted execution."""

import json
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from world_series.core.artifacts import ArtifactStore
from world_series.core.budgets import BudgetLedger
from world_series.core.contracts import Budget, RunStatus, WorldSeriesError
from world_series.evaluation.runner import create_run, load_run


def make_run(tmp_path):
    return create_run(tmp_path, {
        "project": "qlearn", "experiment": "smoke", "seed": 0,
        "device": "cpu", "split": "smoke", "budget": {"max_steps": 4},
    })


def test_artifact_cannot_replace_retained_bytes(tmp_path):
    store = ArtifactStore(tmp_path, "run")
    ref = store.write_bytes("predictions.bin", b"retained negative result")
    with pytest.raises(WorldSeriesError, match="exist|replace|overwrite"):
        store.write_bytes("predictions.bin", b"later favorable result")
    assert store.read_bytes(ref.relative_path) == b"retained negative result"
    store.verify(ref)


def test_concurrent_artifact_writers_have_one_complete_winner(tmp_path):
    store = ArtifactStore(tmp_path, "run")
    gate = threading.Barrier(2)
    payloads = [b"A" * 100_000, b"B" * 110_000]

    def write(payload):
        gate.wait()
        try:
            return store.write_bytes("prediction.bin", payload)
        except WorldSeriesError:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        refs = list(pool.map(write, payloads))
    winners = [ref for ref in refs if ref is not None]
    assert len(winners) == 1
    assert store.read_bytes(winners[0].relative_path) in payloads
    store.verify(winners[0])
    assert list((tmp_path / "artifacts").iterdir()) == [tmp_path / "artifacts/prediction.bin"]


def test_dangling_artifact_symlink_is_not_followed(tmp_path):
    store = ArtifactStore(tmp_path, "run")
    target = tmp_path / "artifacts/other-writer.bin"
    link = tmp_path / "artifacts/prediction.bin"
    link.symlink_to(target.name)
    with pytest.raises(WorldSeriesError):
        store.write_bytes("prediction.bin", b"new result")
    assert link.is_symlink()
    assert not target.exists()


@pytest.mark.parametrize("terminal", [RunStatus.FAILED, RunStatus.INTERRUPTED,
    RunStatus.BUDGET_EXHAUSTED, RunStatus.UNSUPPORTED, RunStatus.SUCCEEDED])
def test_terminal_receipt_cannot_be_rewritten(tmp_path, terminal):
    run = make_run(tmp_path)
    run.set_status(RunStatus.RUNNING)
    error = {"code": "INTERNAL", "message": "retained failure"}
    run.set_status(terminal, error=error)
    before = (run.path / "manifest.json").read_bytes()
    with pytest.raises(WorldSeriesError, match="terminal|finished"):
        run.set_status(RunStatus.RUNNING)
    with pytest.raises(WorldSeriesError, match="terminal|finished"):
        run.set_status(terminal, error=None)
    with pytest.raises(WorldSeriesError, match="terminal|finished"):
        run.write_metrics({"score": 1.0})
    assert (run.path / "manifest.json").read_bytes() == before
    assert not (run.path / "metrics.json").exists()


def test_repeated_terminal_status_is_an_idempotent_noop(tmp_path):
    run = make_run(tmp_path)
    error = {"code": "INTERNAL", "message": "retained failure"}
    run.set_status(RunStatus.FAILED, error=error)
    before = (run.path / "manifest.json").read_bytes()
    run.set_status(RunStatus.FAILED, error=dict(error))
    assert (run.path / "manifest.json").read_bytes() == before


def test_metrics_cannot_be_replaced_with_a_later_measurement(tmp_path):
    run = make_run(tmp_path)
    run.write_metrics({"score": -2.0})
    before = (run.path / "manifest.json").read_bytes()
    with pytest.raises(WorldSeriesError):
        run.write_metrics({"score": 2.0})
    assert json.loads((run.path / "metrics.json").read_text()) == {"score": -2.0}
    assert (run.path / "manifest.json").read_bytes() == before
    assert run.manifest.metrics == {"score": -2.0}


def test_metric_snapshot_does_not_alias_callers_mutable_input(tmp_path):
    run = make_run(tmp_path)
    metrics = {"by_seed": {"0": -2.0}}
    run.write_metrics(metrics)
    metrics["by_seed"]["0"] = 2.0
    run.set_status(RunStatus.SUCCEEDED)
    record = load_run(tmp_path / "runs", run.manifest.run_id)
    assert record["manifest"]["metrics"] == record["metrics"] == {"by_seed": {"0": -2.0}}


@pytest.mark.parametrize("field,value", [
    ("max_steps", float("nan")), ("max_steps", float("inf")),
    ("max_steps", 2.5), ("max_steps", True), ("max_steps", "2"),
    ("max_wall_seconds", float("nan")), ("max_wall_seconds", float("inf")),
    ("max_wall_seconds", True), ("max_wall_seconds", "30"),
])
def test_budgets_reject_unenforceable_values(field, value):
    with pytest.raises(WorldSeriesError):
        Budget(**{field: value})


@pytest.mark.parametrize("method", ["consume_step", "consume_candidates", "consume_sim", "consume_bytes"])
@pytest.mark.parametrize("amount", [-1, 0.5, float("nan"), True, "1"])
def test_invalid_consumption_never_credits_the_budget(method, amount):
    ledger = BudgetLedger(Budget(max_wall_seconds=30))
    with pytest.raises(WorldSeriesError):
        getattr(ledger, method)(amount)
    assert (ledger.steps_used, ledger.candidate_evals, ledger.simulator_calls, ledger.artifact_bytes) == (0, 0, 0, 0)


def test_normal_run_round_trip_preserves_metrics_and_receipt(tmp_path):
    run = make_run(tmp_path)
    run.set_status(RunStatus.RUNNING)
    ref = run.store.write_json("negative.json", {"improvement": -0.01})
    run.write_metrics({"status": "SUCCEEDED", "result": "NOT_SUPPORTED"})
    run.set_status(RunStatus.SUCCEEDED)
    run.append_event("finish", {"status": "SUCCEEDED"})
    run.store.verify(ref)
    record = load_run(tmp_path / "runs", run.manifest.run_id)
    assert record["manifest"]["status"] == "SUCCEEDED"
    assert record["metrics"]["result"] == "NOT_SUPPORTED"

