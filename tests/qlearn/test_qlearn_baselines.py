
from world_series.qlearn.tasks import build_tasks
from world_series.qlearn.baselines import tune_fixed, adamw_trajectory, auc_normalized

def test_adamw_and_tune():
    tasks = build_tasks(0, n=1, dim=3)
    r = tune_fixed(tasks[0], "adamw", steps=5, etas=(0.05, 0.1))
    assert r["final"] < 1e6
    _, curve = adamw_trajectory(tasks[0], 5, eta=r["eta"])
    assert auc_normalized(curve) >= 0
