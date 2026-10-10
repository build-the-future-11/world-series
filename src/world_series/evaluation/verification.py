"""Read-only consistency admission for run receipts and hash-bound artifacts.

These checks validate recorded byte identities, not scientific conclusions or
unreferenced raw files. Historical model replay still needs its frozen source.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from world_series.core.contracts import ErrorCode, RunStatus, WorldSeriesError

_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_TERMINAL = {status.value for status in RunStatus} - {"PENDING", "RUNNING"}


def _reject(message: str) -> None:
    raise WorldSeriesError(ErrorCode.VERIFICATION_FAILED, message)


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _reject(f"duplicate JSON key in run evidence: {key}")
        result[key] = value
    return result


def _number(text: str) -> float:
    value = float(text)
    # Inspect the significand directly: Decimal itself rejects exponents beyond
    # its representation limits, whereas JSON permits arbitrarily long ones.
    nonzero = any(digit in "123456789" for digit in text.lower().split("e", 1)[0])
    if not math.isfinite(value) or (value == 0 and nonzero):
        _reject("run evidence contains a nonfinite or unrepresentable JSON number")
    return value


def _constant(text: str) -> None:
    _reject(f"nonfinite JSON constant in run evidence: {text}")


def _object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw, object_pairs_hook=_pairs, parse_float=_number,
                           parse_constant=_constant)
    except (ValueError, UnicodeError, OverflowError, RecursionError) as exc:
        _reject(f"invalid JSON in {label}: {exc}")
    if not isinstance(value, dict):
        _reject(f"{label} must contain a JSON object")
    return value


def _file(root: Path, relative: str) -> Path:
    """Admit a literal regular file; never follow a run evidence symlink."""
    if (not isinstance(relative, str) or not relative or "\\" in relative
            or any(part in {"", ".", ".."} for part in relative.split("/"))
            or Path(relative).is_absolute()):
        _reject(f"invalid confined evidence path: {relative!r}")
    candidate = root
    for part in relative.split("/"):
        candidate /= part
        if candidate.is_symlink():
            _reject(f"symlink is not admitted as retained evidence: {relative}")
    if not candidate.is_file():
        _reject(f"missing regular evidence file: {relative}")
    return candidate


def _timestamp(value: Any, field: str) -> None:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or (isinstance(value, float) and not math.isfinite(value))):
        _reject(f"{field} must be a finite numeric timestamp")


def _canonical(value: Any) -> str:
    # Python equality would conflate true, 1 and 1.0, hiding a changed snapshot.
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_run(runs_root: Path, run_id: str) -> dict[str, Any]:
    if (not isinstance(run_id, str) or not run_id or run_id in {".", ".."}
            or "/" in run_id or "\\" in run_id or "\x00" in run_id):
        _reject("run-id must name exactly one directory inside the run root")
    path = Path(runs_root) / run_id
    if path.is_symlink() or not path.is_dir():
        _reject(f"unknown or linked run-id: {run_id}")

    observed: dict[str, bytes] = {}

    def read(relative: str) -> bytes:
        try:
            raw = _file(path, relative).read_bytes()
        except OSError as exc:
            _reject(f"cannot read run evidence {relative}: {exc}")
        observed[relative] = raw
        return raw

    manifest = _object(read("manifest.json"), "manifest.json")
    if manifest.get("run_id") != run_id:
        _reject("manifest run_id does not match the selected run directory")
    for key in ("project", "experiment", "split", "device", "dtype"):
        if not isinstance(manifest.get(key), str) or not manifest[key]:
            _reject(f"manifest {key} must be a nonempty string")
    if (isinstance(manifest.get("seed"), bool)
            or not isinstance(manifest.get("seed"), int)):
        _reject("manifest seed must be an integer")
    if (not isinstance(manifest.get("config_hash"), str)
            or _DIGEST.fullmatch(manifest["config_hash"]) is None):
        _reject("manifest config_hash must be a SHA-256 digest")
    for key in ("source", "budget", "metrics"):
        if not isinstance(manifest.get(key), dict):
            _reject(f"manifest {key} must be an object")
    status = manifest.get("status")
    if not isinstance(status, str) or status not in {item.value for item in RunStatus}:
        _reject("manifest status is not a valid execution status")
    _timestamp(manifest.get("created_at"), "created_at")
    if status in _TERMINAL:
        _timestamp(manifest.get("finished_at"), "finished_at")
    elif manifest.get("finished_at") is not None:
        _reject("nonterminal receipt must not have a finished_at timestamp")
    if manifest.get("error") is not None and not isinstance(manifest["error"], dict):
        _reject("manifest error must be an object or null")

    metrics_path = path / "metrics.json"
    metrics_present = metrics_path.exists() or metrics_path.is_symlink()
    metrics = _object(read("metrics.json"), "metrics.json") if metrics_present else {}
    if not metrics_present and status == RunStatus.SUCCEEDED.value:
        _reject("successful run is missing metrics.json")
    if _canonical(metrics) != _canonical(manifest["metrics"]):
        _reject("metrics.json does not match the manifest metric snapshot")
    if status == RunStatus.SUCCEEDED.value and metrics.get("status", status) != status:
        _reject("successful manifest conflicts with the recorded metric status")

    events = []
    for index, raw in enumerate(read("events.jsonl").splitlines(), 1):
        if not raw.strip():
            continue
        event = _object(raw, f"events.jsonl line {index}")
        _timestamp(event.get("ts"), f"event {index} ts")
        if not isinstance(event.get("kind"), str) or not event["kind"]:
            _reject(f"event {index} kind must be a nonempty string")
        if not isinstance(event.get("payload"), dict):
            _reject(f"event {index} payload must be an object")
        events.append(event)

    bound: dict[str, str] = {}

    def check_refs(value: Any) -> None:
        if isinstance(value, list):
            for item in value:
                check_refs(item)
        elif isinstance(value, dict):
            is_reference = ("relative_path" in value or "producer_run_id" in value
                or ("path" in value and "sha256" in value)
                or (isinstance(value.get("path"), str)
                    and value["path"].startswith("artifacts/")))
            if is_reference:
                relative = value.get("relative_path", value.get("path"))
                digest = value.get("sha256")
                if (not isinstance(relative, str) or not relative.startswith("artifacts/")
                        or not isinstance(digest, str) or _DIGEST.fullmatch(digest) is None):
                    _reject("malformed hash-bound artifact reference")
                if "path" in value and "relative_path" in value and value["path"] != relative:
                    _reject("artifact reference contains conflicting paths")
                if "producer_run_id" in value and value["producer_run_id"] != run_id:
                    _reject("artifact producer_run_id does not match the run")
                if relative in bound and bound[relative] != digest:
                    _reject(f"conflicting artifact hashes: {relative}")
                if relative not in bound:
                    actual = hashlib.sha256(read(relative)).hexdigest()
                    if actual != digest:
                        _reject(f"artifact hash mismatch: {relative}")
                    bound[relative] = digest
            for item in value.values():
                check_refs(item)

    check_refs(metrics)
    check_refs(events)
    artifacts = path / "artifacts"
    if artifacts.is_symlink() or not artifacts.is_dir():
        _reject("run is missing its regular artifacts directory")
    inventory: set[str] = set()
    for entry in artifacts.rglob("*"):
        if entry.is_symlink():
            _reject("artifact inventory contains a symlink")
        if entry.is_file():
            inventory.add(entry.relative_to(path).as_posix())
        elif not entry.is_dir():
            _reject("artifact inventory contains a nonregular entry")

    # Reject a normal writer advancing the receipt during verification. Each
    # reference was hashed from the same bytes retained in this read snapshot.
    for relative, raw in observed.items():
        try:
            if _file(path, relative).read_bytes() != raw:
                _reject(f"run evidence changed while reading: {relative}")
        except OSError as exc:
            _reject(f"run evidence became unavailable while reading: {relative}: {exc}")

    return {"path": str(path), "manifest": manifest, "metrics": metrics, "events": events,
            "verification": {"status": "CONSISTENCY_VERIFIED",
                "referenced_artifacts_verified": len(bound),
                "artifact_sha256": dict(sorted(bound.items())),
                "unreferenced_artifact_count": len(inventory - bound.keys()),
                "scope": "Receipt consistency and recorded artifact hashes only; unreferenced "
                         "files, source authenticity, metric recomputation and scientific "
                         "conclusions are not verified."}}
