"""Artifact store with path-traversal rejection and content hashing."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Union

from world_series.core.contracts import ArtifactRef, ErrorCode, WorldSeriesError

PathLike = Union[str, Path]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_resolve(root: Path, relative: str) -> Path:
    if Path(relative).is_absolute():
        raise WorldSeriesError(ErrorCode.PATH_TRAVERSAL, "absolute artifact paths are forbidden")
    candidate = (root / relative).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise WorldSeriesError(
            ErrorCode.PATH_TRAVERSAL,
            f"path escapes artifact root: {relative}",
            {"root": str(root_resolved), "candidate": str(candidate)},
        ) from exc
    return candidate


class ArtifactStore:
    def __init__(self, root: PathLike, run_id: str, schema_version: str = "0.1.0"):
        self.root = Path(root)
        self.run_id = run_id
        self.schema_version = schema_version
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "artifacts").mkdir(parents=True, exist_ok=True)

    def write_bytes(self, relative: str, data: bytes, media_type: str = "application/octet-stream") -> ArtifactRef:
        path = safe_resolve(self.root / "artifacts", relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        digest = sha256_bytes(data)
        return ArtifactRef(
            relative_path=f"artifacts/{relative}",
            sha256=digest,
            producer_run_id=self.run_id,
            schema_version=self.schema_version,
            media_type=media_type,
        )

    def write_json(self, relative: str, payload: Any) -> ArtifactRef:
        data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
        return self.write_bytes(relative, data, media_type="application/json")

    def read_bytes(self, relative: str) -> bytes:
        path = safe_resolve(self.root, relative)
        return path.read_bytes()

    def verify(self, ref: ArtifactRef) -> None:
        path = safe_resolve(self.root, ref.relative_path)
        digest = sha256_file(path)
        if digest != ref.sha256:
            raise WorldSeriesError(
                ErrorCode.VERIFICATION_FAILED,
                "artifact hash mismatch",
                {"expected": ref.sha256, "actual": digest, "path": ref.relative_path},
            )
