"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import yaml

from world_series.core.contracts import Budget, ErrorCode, WorldSeriesError
from world_series import PROJECT_NAMESPACES


REQUIRED_TOP = ("project", "experiment", "seed", "device", "budget", "split")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate configuration key: {key}")
        result[key] = value
    return result


class _UniqueSafeLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        pairs = [(self.construct_object(key, deep=deep), self.construct_object(value, deep=deep))
                 for key, value in node.value]
        return _unique_object(pairs)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"config not found: {path}")
    try:
        content = path.read_text(encoding="utf-8")
        data = (json.loads(content, object_pairs_hook=_unique_object) if path.suffix.lower() == '.json'
                else yaml.load(content, Loader=_UniqueSafeLoader))
    except (yaml.YAMLError, ValueError, TypeError) as exc:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"configuration parse error: {exc}") from exc
    if not isinstance(data, dict):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "config root must be a mapping")
    return data


def validate_config(cfg: dict[str, Any]) -> dict[str, Any]:
    try:
        json.dumps(cfg, allow_nan=False)
    except (ValueError, TypeError, OverflowError) as exc:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"configuration must contain finite JSON values: {exc}") from exc
    missing = [k for k in REQUIRED_TOP if k not in cfg]
    if missing:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"missing keys: {missing}")
    project = cfg["project"]
    if project not in PROJECT_NAMESPACES:
        raise WorldSeriesError(
            ErrorCode.INVALID_CONFIG,
            f"unknown project '{project}'",
            {"allowed": list(PROJECT_NAMESPACES)},
        )
    if type(cfg["seed"]) is not int:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "seed must be int")
    if cfg["device"] not in {"cpu", "mps", "cuda"}:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "device must be cpu|mps|cuda")
    if cfg["split"] not in {"smoke", "dev", "demo", "ablation"}:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "split must be smoke|dev|demo|ablation")
    budget_raw = cfg["budget"]
    if not isinstance(budget_raw, dict):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "budget must be a mapping")
    # Construct Budget to validate non-negative fields; allow subset of keys.
    allowed = set(Budget.__dataclass_fields__.keys())
    unknown = set(budget_raw) - allowed
    if unknown:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"unknown budget keys: {sorted(unknown)}")
    Budget(**budget_raw)
    experiment = cfg["experiment"]
    if not isinstance(experiment, str) or not experiment:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "experiment must be non-empty string")
    return cfg


def load_and_validate(path: Path) -> dict[str, Any]:
    return validate_config(load_yaml(path))
