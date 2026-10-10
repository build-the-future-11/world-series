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

