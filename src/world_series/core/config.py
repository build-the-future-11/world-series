"""Configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any

import yaml

from world_series.core.contracts import Budget, ErrorCode, WorldSeriesError
from world_series import PROJECT_NAMESPACES


REQUIRED_TOP = ("project", "experiment", "seed", "device", "budget", "split")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"config not found: {path}")
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content) if path.suffix.lower() == '.json' else yaml.safe_load(content)
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"YAML parse error: {exc}") from exc
    if not isinstance(data, dict):
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "config root must be a mapping")
    return data


def validate_config(cfg: dict[str, Any]) -> dict[str, Any]:
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
    if not isinstance(cfg["seed"], int):
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
