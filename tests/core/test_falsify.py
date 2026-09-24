from world_series.evaluation.falsify import run_all_controls, ultron_wrong_tool_fails

def test_falsify_suite_runs():
    results = run_all_controls(seed=0)
    assert len(results) >= 6
    crashed = [r for r in results if r.get("interpretation") == "CONTROL_CRASHED"]
    assert not crashed, crashed
    failed = [r for r in results if r.get("passed") is False]
    assert not failed, failed

def test_ultron_mismatch():
    r = ultron_wrong_tool_fails()
    assert r["passed"] is True
