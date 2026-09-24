
from pathlib import Path
from world_series.evaluation.runner import create_run
from world_series.core.contracts import RunStatus

def test_run_not_overwrite(tmp_path):
    cfg = {"project":"qlearn","experiment":"smoke","seed":0,"device":"cpu","split":"smoke","budget":{"max_steps":4}}
    # patch repo root as tmp
    run = create_run(tmp_path, cfg, runs_root=tmp_path/"runs")
    run.set_status(RunStatus.FAILED, error={"code":"INTERNAL","message":"x"})
    assert (tmp_path/"runs"/run.manifest.run_id/"manifest.json").exists()
