import argparse
import json

import pytest

from world_series import cli


@pytest.mark.parametrize("interrupt", [True, False])
def test_cli_retains_interrupted_evidence_and_normal_negative_result(tmp_path, monkeypatch, interrupt):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "project": "qlearn", "experiment": "smoke", "seed": 0,
        "device": "cpu", "split": "smoke", "budget": {"max_steps": 4},
    }))
    monkeypatch.setattr(cli, "repo_root_from_cwd", lambda: tmp_path)

    def dispatch(cfg, run):
        run.store.write_json("attempt.json", {"observed_delta": -0.2})
        if interrupt:
            raise KeyboardInterrupt
        return {"status": "SUCCEEDED", "result": "NOT_SUPPORTED"}

    monkeypatch.setattr(cli, "dispatch_run", dispatch)
    assert cli.cmd_run(argparse.Namespace(config=str(config))) == (130 if interrupt else 0)
    directories = list((tmp_path / "runs").iterdir())
    assert len(directories) == 1
    run = directories[0]
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["status"] == ("INTERRUPTED" if interrupt else "SUCCEEDED")
    assert manifest["finished_at"] is not None
    assert json.loads((run / "artifacts/attempt.json").read_text()) == {"observed_delta": -0.2}


@pytest.mark.parametrize("output_error", [KeyboardInterrupt, BrokenPipeError])
def test_completed_receipt_survives_output_interruption(tmp_path, monkeypatch, output_error):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({
        "project": "qlearn", "experiment": "smoke", "seed": 0,
        "device": "cpu", "split": "smoke", "budget": {"max_steps": 4},
    }))
    monkeypatch.setattr(cli, "repo_root_from_cwd", lambda: tmp_path)
    metrics = {"status": "SUCCEEDED", "result": "NOT_SUPPORTED"}
    monkeypatch.setattr(cli, "dispatch_run", lambda cfg, run: metrics)

    def disconnected_output(*args, **kwargs):
        raise output_error("output interrupted after completion")

    monkeypatch.setattr(cli, "print", disconnected_output, raising=False)
    with pytest.raises(output_error, match="after completion"):
        cli.cmd_run(argparse.Namespace(config=str(config)))
    run, = (tmp_path / "runs").iterdir()
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["status"] == "SUCCEEDED"
    assert manifest["error"] is None
    assert manifest["finished_at"] is not None
    assert manifest["metrics"] == metrics

