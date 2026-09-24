
import pytest
from world_series.core.contracts import Budget, TaskSpec, WorldSeriesError, ErrorCode
from world_series.core.artifacts import ArtifactStore, safe_resolve
from world_series.core.config import validate_config, load_and_validate
from pathlib import Path

def test_budget_rejects_negative():
    with pytest.raises(WorldSeriesError):
        Budget(max_steps=-1)

def test_taskspec_rejects_answers():
    with pytest.raises(WorldSeriesError):
        TaskSpec("qlearn","f",{"answer":1}, Budget(), "smoke", "loss")

def test_path_traversal(tmp_path):
    store = ArtifactStore(tmp_path, "run")
    with pytest.raises(WorldSeriesError) as ei:
        safe_resolve(tmp_path, "../etc/passwd")
    assert ei.value.code == ErrorCode.PATH_TRAVERSAL

def test_config_validation_ok(tmp_path):
    cfg = {
        "project":"qlearn","experiment":"smoke","seed":0,"device":"cpu","split":"smoke",
        "budget":{"max_steps":8}
    }
    validate_config(cfg)

def test_config_validation_bad_project():
    with pytest.raises(WorldSeriesError):
        validate_config({"project":"nope","experiment":"x","seed":0,"device":"cpu","split":"smoke","budget":{}})
