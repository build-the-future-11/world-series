import copy
import torch
from world_series.qlearn.malis import DiscreteEngine
from world_series.qlearn.regression import regression_task

def test_rollback_restores_all_optimizer_states_and_next_update():
    task = regression_task(12, 'sin', width=3, support_size=8, query_size=8)
    engine = DiscreteEngine(task)
    engine.act('adamw'); engine.act('momentum'); engine.act('checkpoint')
    snapshot = copy.deepcopy(engine.saved)
    engine.act('adamw')
    expected = {k: v.clone() for k, v in engine.model.state_dict().items()}
    engine.act('huber'); engine.act('replay'); spent = engine.gradient_evaluations
    engine.act('rollback')
    assert engine.gradient_evaluations == spent
    assert engine.controller_state == snapshot['controller_state']
    engine.act('adamw')
    assert all(torch.equal(v, expected[k]) for k, v in engine.model.state_dict().items())

def test_query_targets_cannot_change_actions_or_support_updates():
    from dataclasses import replace
    task = regression_task(12, 'sin', width=3, support_size=8, query_size=8)
    a = DiscreteEngine(task); b = DiscreteEngine(replace(task, query_y=task.query_y*1000))
    for action in ['sgd', 'adamw', 'huber']:
        a.act(action); b.act(action)
    assert all(torch.equal(v, b.model.state_dict()[k]) for k, v in a.model.state_dict().items())
