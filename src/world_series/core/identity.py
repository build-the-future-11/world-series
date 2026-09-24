"""Source identity: git revision when available, content hash when dirty/absent."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Iterable


def _run_git(args: list[str], cwd: Path) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            check=False,
        )
        return proc.returncode, (proc.stdout or "").strip()
    except FileNotFoundError:
        return 127, ""


def content_hash_paths(root: Path, paths: Iterable[Path]) -> str:
    h = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p.relative_to(root))):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root)).replace("\\", "/")
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(path.read_bytes())
        h.update(b"\0")
    return h.hexdigest()


def source_identity(repo_root: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    identity: dict[str, Any] = {
        "git_head": None,
        "git_dirty": None,
        "content_hash": None,
        "note": "A content hash is not a Git commit.",
    }
    code, head = _run_git(["rev-parse", "HEAD"], repo_root)
    if code == 0 and head:
        identity["git_head"] = head
        code2, status = _run_git(["status", "--porcelain"], repo_root)
        dirty = bool(status) if code2 == 0 else True
        identity["git_dirty"] = dirty
    src = repo_root / "src" / "world_series"
    if src.is_dir():
        files = list(src.rglob("*.py"))
        identity["content_hash"] = content_hash_paths(repo_root, files)
    return identity


def hash_mapping(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()
