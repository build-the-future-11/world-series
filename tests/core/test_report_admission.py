"""Public reports must admit a coherent receipt and its recorded raw bytes."""

import argparse
import hashlib
import json
from dataclasses import asdict

import pytest

from world_series import cli
from world_series.core.contracts import RunStatus, WorldSeriesError
from world_series.evaluation.reports import render_report, write_report
from world_series.evaluation.runner import create_run, load_run


def make_receipt(tmp_path, *, full_ref=False):
    run = create_run(tmp_path, {
        "project": "wft", "experiment": "report-admission", "seed": 0,
        "device": "cpu", "split": "smoke", "budget": {"max_steps": 4},
    })
    run.set_status(RunStatus.RUNNING)
    ref = run.store.write_json("raw/negative.json", {"delta": -0.25})
    raw = asdict(ref) if full_ref else {"path": ref.relative_path, "sha256": ref.sha256}
    run.write_metrics({"status": "SUCCEEDED", "research_outcome": "NOT_SUPPORTED",
                       "score": -0.25, "raw": raw})
    run.append_event("finish", {"status": "SUCCEEDED"})
    run.set_status(RunStatus.SUCCEEDED)
    return run, ref


def snapshots(path):
    return {p.relative_to(path).as_posix(): p.read_bytes()
            for p in path.rglob("*") if p.is_file()}


def rewrite(path, change):
    value = json.loads(path.read_text())
    change(value)
    path.write_text(json.dumps(value))


@pytest.mark.parametrize("full_ref", [False, True])
def test_valid_negative_report_is_verified_without_rewriting_evidence(tmp_path, full_ref):
    run, _ = make_receipt(tmp_path, full_ref=full_ref)
    before = snapshots(run.path)
    data = load_run(run.runs_root, run.manifest.run_id)
    report = render_report(run.runs_root, run.manifest.run_id)
    assert data["verification"]["referenced_artifacts_verified"] == 1
    assert data["verification"]["unreferenced_artifact_count"] == 0
    assert "NOT_SUPPORTED" in report and "SUCCEEDED" in report
    assert "1 referenced artifact" in report
    assert snapshots(run.path) == before


@pytest.mark.parametrize("corruption", ["changed", "missing", "foreign_producer", "wrong_digest",
                                         "missing_digest", "outside", "symlink", "conflicting_ref"])
def test_corrupt_bound_artifacts_cannot_generate_a_report(tmp_path, corruption):
    run, ref = make_receipt(tmp_path, full_ref=corruption == "foreign_producer")
    raw = run.path / ref.relative_path
    if corruption == "changed":
        raw.write_bytes(b"a later favorable result")
    elif corruption == "missing":
        raw.unlink()
    elif corruption == "symlink":
        retained = raw.read_bytes()
        raw.unlink()
        other = tmp_path / "outside.json"
        other.write_bytes(retained)
        raw.symlink_to(other)
    else:
        metrics = json.loads((run.path / "metrics.json").read_text())
        if corruption == "foreign_producer":
            metrics["raw"]["producer_run_id"] = "another-run"
        elif corruption == "wrong_digest":
            metrics["raw"]["sha256"] = "not-a-sha256"
        elif corruption == "missing_digest":
            metrics["raw"].pop("sha256")
        elif corruption == "outside":
            metrics["raw"]["path"] = "../other.json"
            (run.runs_root / "other.json").write_bytes(raw.read_bytes())
        elif corruption == "conflicting_ref":
            metrics["second"] = {"path": ref.relative_path, "sha256": "0" * 64}
        (run.path / "metrics.json").write_text(json.dumps(metrics))
        rewrite(run.path / "manifest.json", lambda m: m.update(metrics=metrics))
    report = run.path / "report.md"
    report.write_text("retained earlier report\n")
    before = snapshots(run.path)
    with pytest.raises(WorldSeriesError):
        write_report(run.runs_root, run.manifest.run_id)
    assert snapshots(run.path) == before


@pytest.mark.parametrize("corruption", ["metric_value", "bool_integer_alias", "missing_metrics",
    "foreign_identity", "unknown_status", "missing_finish_time", "missing_manifest", "missing_events"])
def test_inconsistent_receipt_is_rejected(tmp_path, corruption):
    run, _ = make_receipt(tmp_path)
    if corruption == "metric_value":
        rewrite(run.path / "metrics.json", lambda m: m.update(score=8.0))
    elif corruption == "bool_integer_alias":
        rewrite(run.path / "metrics.json", lambda m: m.update(score=True))
        rewrite(run.path / "manifest.json", lambda m: m["metrics"].update(score=1))
    elif corruption.startswith("missing_") and corruption != "missing_finish_time":
        (run.path / {"missing_metrics": "metrics.json", "missing_manifest": "manifest.json",
                     "missing_events": "events.jsonl"}[corruption]).unlink()
    else:
        change = {"foreign_identity": {"run_id": "other-run"},
                  "unknown_status": {"status": "SUPPORTED"},
                  "missing_finish_time": {"finished_at": None}}[corruption]
        rewrite(run.path / "manifest.json", lambda m: m.update(change))
    with pytest.raises(WorldSeriesError):
        load_run(run.runs_root, run.manifest.run_id)


@pytest.mark.parametrize("filename", ["manifest.json", "metrics.json", "events.jsonl"])
@pytest.mark.parametrize("invalid", ['{"x": 1, "x": 2}', '{"x": NaN}',
                                     '{"x": 1e999}', '{"x": 1e-999}', '[]'])
def test_ambiguous_or_nonfinite_json_is_rejected(tmp_path, filename, invalid):
    run, _ = make_receipt(tmp_path)
    (run.path / filename).write_text(invalid + "\n")
    with pytest.raises(WorldSeriesError):
        load_run(run.runs_root, run.manifest.run_id)


@pytest.mark.parametrize("status", [RunStatus.FAILED, RunStatus.INTERRUPTED,
                                    RunStatus.BUDGET_EXHAUSTED, RunStatus.UNSUPPORTED])
def test_failed_unmeasured_receipt_remains_available(tmp_path, status):
    run = create_run(tmp_path, {"project": "wft", "experiment": "failed", "seed": 0,
        "device": "cpu", "split": "smoke", "budget": {}})
    run.store.write_bytes("partial.bin", b"partial evidence")
    run.set_status(status, {"code": "INTERNAL", "message": "retained outcome"})
    before = snapshots(run.path)
    report = render_report(run.runs_root, run.manifest.run_id)
    data = load_run(run.runs_root, run.manifest.run_id)
    assert status.value in report and "retained outcome" in report
    assert data["verification"]["unreferenced_artifact_count"] == 1
    assert snapshots(run.path) == before


def test_event_artifact_references_are_verified(tmp_path):
    run, ref = make_receipt(tmp_path)
    run.append_event("retained_prediction", asdict(ref))
    (run.path / ref.relative_path).write_bytes(b"changed")
    with pytest.raises(WorldSeriesError):
        load_run(run.runs_root, run.manifest.run_id)


@pytest.mark.parametrize("relative", ["../runs/{id}", "./{id}", "/absolute", ".", ".."])
def test_run_id_cannot_address_outside_the_named_run(tmp_path, relative):
    run, _ = make_receipt(tmp_path)
    with pytest.raises(WorldSeriesError):
        load_run(run.runs_root, relative.format(id=run.manifest.run_id))


def test_cli_verification_failure_preserves_existing_report(tmp_path, monkeypatch, capsys):
    run, _ = make_receipt(tmp_path)
    rewrite(run.path / "metrics.json", lambda m: m.update(score=1.0))
    previous = run.path / "report.md"
    previous.write_text("retained report")
    monkeypatch.setattr(cli, "repo_root_from_cwd", lambda: tmp_path)
    assert cli.main(["report", "--run-id", run.manifest.run_id]) == 1
    output = json.loads(capsys.readouterr().out)
    assert output["error"]["code"] == "VERIFICATION_FAILED"
    assert previous.read_text() == "retained report"


def test_report_cannot_replace_its_raw_evidence(tmp_path):
    run, ref = make_receipt(tmp_path)
    raw = run.path / ref.relative_path
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    with pytest.raises(WorldSeriesError):
        write_report(run.runs_root, run.manifest.run_id, out_path=raw)
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == digest


def test_report_atomic_publish_failure_preserves_prior_bytes(tmp_path, monkeypatch):
    from world_series.core import artifacts
    run, _ = make_receipt(tmp_path)
    out = run.path / "report.md"
    out.write_text("older derived report")
    def fail_replace(*args, **kwargs):
        raise OSError("simulated publication failure")
    monkeypatch.setattr(artifacts.os, "replace", fail_replace)
    with pytest.raises(OSError, match="publication failure"):
        write_report(run.runs_root, run.manifest.run_id)
    assert out.read_text() == "older derived report"


def test_real_cli_can_report_a_negative_development_receipt(tmp_path, monkeypatch):
    run, _ = make_receipt(tmp_path)
    monkeypatch.setattr(cli, "repo_root_from_cwd", lambda: tmp_path)
    assert cli.cmd_report(argparse.Namespace(run_id=run.manifest.run_id)) == 0
    assert "NOT_SUPPORTED" in (run.path / "report.md").read_text()


@pytest.mark.parametrize("separate_root", [False, True])
@pytest.mark.parametrize("relative", ["manifest.json", "metrics.json", "events.jsonl", "artifacts/raw/negative.json"])
def test_report_cannot_replace_another_runs_raw_evidence(tmp_path, separate_root, relative):
    run, _ = make_receipt(tmp_path)
    other, _ = make_receipt(tmp_path / "independent" if separate_root else tmp_path)
    before = snapshots(other.path)
    with pytest.raises(WorldSeriesError):
        write_report(run.runs_root, run.manifest.run_id, out_path=other.path / relative)
    assert snapshots(other.path) == before


@pytest.mark.parametrize("filename", ["manifest.json", "metrics.json", "events.jsonl"])
def test_extreme_json_exponent_is_a_structured_verification_error(tmp_path, filename):
    run, _ = make_receipt(tmp_path)
    (run.path / filename).write_text('{"x": 1e-9999999999999999999999999}')
    with pytest.raises(WorldSeriesError):
        load_run(run.runs_root, run.manifest.run_id)
