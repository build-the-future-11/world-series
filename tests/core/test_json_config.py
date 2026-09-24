import json

from world_series.core.config import load_and_validate


def test_json_scientific_notation_retains_numeric_values(tmp_path):
    config = {'project': 'qlearn', 'experiment': 'numeric-config', 'seed': 1,
              'device': 'cpu', 'split': 'dev', 'budget': {},
              'params': {'outer_learning_rates': [1e-5, 1e-4, 0.003]}}
    path = tmp_path / 'study.json'
    path.write_text(json.dumps(config))
    assert load_and_validate(path) == config
