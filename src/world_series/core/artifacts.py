"""Artifact store with path-traversal rejection and content hashing."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Union

from world_series.core.contracts import ArtifactRef, ErrorCode, WorldSeriesError

PathLike = Union[str, Path]


def json_bytes(payload: Any, *, indent: int | None = None) -> bytes:
    """Encode strict JSON completely before touching an evidence path."""
    try:
        return (json.dumps(payload, indent=indent, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")
    except (ValueError, TypeError, OverflowError) as exc:
        raise WorldSeriesError(
            ErrorCode.INVALID_CONFIG,
            f"JSON evidence must contain finite, serializable values: {exc}",
        ) from exc


def publish_bytes(path: Path, data: bytes, *, overwrite: bool = False) -> None:
    """Publish complete bytes; new evidence paths have exactly one winner.

    Staging is on the destination filesystem. Hard-link publication fails
    without changing an existing file, directory or dangling symlink. Mutable
    manifests opt into replacement explicitly. Parent directories are trusted;
    atomic visibility is not a claim of power-loss durability.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".pending-", dir=path.parent)
    staging = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if overwrite:
            os.replace(staging, path)
        else:
            try:
                os.link(staging, path)
            except FileExistsError as exc:
                raise WorldSeriesError(
                    ErrorCode.INVALID_CONFIG,
                    f"evidence path already exists (will not overwrite): {path}",
                ) from exc
    finally:
        staging.unlink(missing_ok=True)


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
        relative_path = Path(relative)
        # Validate the full path, then retain its leaf so a dangling symlink is
        # rejected by publication rather than silently followed to a new path.
        safe_resolve(self.root / "artifacts", relative)
        if relative_path.name in {"", ".", ".."}:
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "artifact filename required")
        parent = safe_resolve(self.root / "artifacts", str(relative_path.parent))
        path = parent / relative_path.name
        publish_bytes(path, data)
        digest = sha256_bytes(data)
        return ArtifactRef(
            relative_path=f"artifacts/{relative}",
            sha256=digest,
            producer_run_id=self.run_id,
            schema_version=self.schema_version,
            media_type=media_type,
        )

    def write_json(self, relative: str, payload: Any) -> ArtifactRef:
        data = json_bytes(payload, indent=2)
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
