import importlib.util
from pathlib import Path

import pytest


spec = importlib.util.spec_from_file_location(
    'source_paths', Path(__file__).resolve().parents[1] / 'scripts/closure/source_paths.py'
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_historical_path_uses_extracted_source(tmp_path):
    local = tmp_path / 'scripts/closure/study.py'
    local.parent.mkdir(parents=True)
    local.write_text('local source')
    assert module.source_path('/missing/author/repo/scripts/closure/study.py', tmp_path) == local
    assert module.source_path('scripts/closure/study.py', tmp_path) == local


def test_source_cannot_escape_extraction(tmp_path):
    with pytest.raises(ValueError):
        module.source_path('../outside.py', tmp_path)
    with pytest.raises(ValueError):
        module.source_path('/other/absolute/file.py', tmp_path)
    (tmp_path / 'escape').symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError):
        module.source_path('escape/outside.py', tmp_path)
