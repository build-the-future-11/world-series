"""Run manifests, events, and failure receipts."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from world_series.core.artifacts import ArtifactStore
from world_series.core.contracts import Budget, ErrorCode, RunStatus, WorldSeriesError
from world_series.core.identity import hash_mapping, source_identity


def _new_run_id() -> str:
    ts = time.strftime("%Y%m%dT%H%M%S")
    return f"{ts}_{uuid.uuid4().hex[:8]}"


@dataclass
class RunManifest:
    run_id: str
    project: str
    experiment: str
    split: str
    seed: int
    device: str
    dtype: str
    config_hash: str
    source: dict[str, Any]
    budget: dict[str, Any]
    status: str
    created_at: float
    finished_at: Optional[float] = None
    error: Optional[dict[str, Any]] = None
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class RunDirectory:
    def __init__(self, runs_root: Path, manifest: RunManifest):
        self.runs_root = runs_root
        self.manifest = manifest
        self.path = runs_root / manifest.run_id
        if self.path.exists():
            raise WorldSeriesError(
                ErrorCode.INVALID_CONFIG,
                f"run directory already exists: {self.path} (will not overwrite)",
            )
        self.path.mkdir(parents=True, exist_ok=False)
        (self.path / "artifacts").mkdir()
        self.store = ArtifactStore(self.path, run_id=manifest.run_id)
        self.events_path = self.path / "events.jsonl"
        self.events_path.write_text("", encoding="utf-8")
        self._write_manifest()

    def _write_manifest(self) -> None:
        (self.path / "manifest.json").write_text(
            json.dumps(self.manifest.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def append_event(self, kind: str, payload: Optional[dict[str, Any]] = None) -> None:
        event = {
            "ts": time.time(),
            "kind": kind,
            "payload": payload or {},
        }
        with self.events_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, sort_keys=True) + "\n")

    def set_status(self, status: RunStatus, error: Optional[dict[str, Any]] = None) -> None:
        self.manifest.status = status.value
        self.manifest.error = error
        if status in {
            RunStatus.SUCCEEDED,
            RunStatus.FAILED,
            RunStatus.INTERRUPTED,
            RunStatus.UNSUPPORTED,
            RunStatus.BUDGET_EXHAUSTED,
        }:
            self.manifest.finished_at = time.time()
        self._write_manifest()

    def write_metrics(self, metrics: dict[str, Any]) -> None:
        self.manifest.metrics = metrics
        (self.path / "metrics.json").write_text(
            json.dumps(metrics, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self._write_manifest()


def create_run(
    repo_root: Path,
    cfg: dict[str, Any],
    *,
    runs_root: Optional[Path] = None,
    device_dtype: str = "float64",
) -> RunDirectory:
    runs_root = runs_root or (repo_root / "runs")
    runs_root.mkdir(parents=True, exist_ok=True)
    run_id = _new_run_id()
    config_hash = hash_mapping(cfg)
    budget = Budget(**cfg.get("budget", {}))
    manifest = RunManifest(
        run_id=run_id,
        project=cfg["project"],
        experiment=cfg["experiment"],
        split=cfg["split"],
        seed=int(cfg["seed"]),
        device=str(cfg["device"]),
        dtype=device_dtype,
        config_hash=config_hash,
        source=source_identity(repo_root),
        budget=asdict_budget(budget),
        status=RunStatus.PENDING.value,
        created_at=time.time(),
    )
    return RunDirectory(runs_root, manifest)


def asdict_budget(budget: Budget) -> dict[str, Any]:
    from dataclasses import asdict

    return asdict(budget)


def load_run(runs_root: Path, run_id: str) -> dict[str, Any]:
    path = runs_root / run_id
    if not path.is_dir():
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"unknown run-id: {run_id}")
    manifest = json.loads((path / "manifest.json").read_text(encoding="utf-8"))
    metrics = {}
    metrics_path = path / "metrics.json"
    if metrics_path.is_file():
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    events = []
    events_path = path / "events.jsonl"
    if events_path.is_file():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
    return {"path": str(path), "manifest": manifest, "metrics": metrics, "events": events}
