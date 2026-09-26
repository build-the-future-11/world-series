#!/usr/bin/env python3
"""Verify claim-index analysis digests against local report files."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--claim-index",
        type=Path,
        default=Path("results/claim_index.json"),
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Implementation repository root (paths in the index may be prefixed with world-series/).",
    )
    args = parser.parse_args()
    data = json.loads(args.claim_index.read_text())
    failures: list[str] = []
    for claim in data["claims"]:
        rel = claim["analysis"]["path"]
        if rel.startswith("world-series/"):
            rel = rel[len("world-series/") :]
        path = args.repo_root / rel
        expected = claim["analysis"]["sha256"]
        if not path.is_file():
            failures.append(f"{claim['id']}: missing {path}")
            continue
        got = sha256(path)
        if got != expected:
            failures.append(f"{claim['id']}: digest mismatch for {path}\n  expected {expected}\n  got      {got}")
        else:
            print(f"OK {claim['id']} {path}")
    if failures:
        print("FAILURES:", file=sys.stderr)
        for line in failures:
            print(line, file=sys.stderr)
        return 1
    print(f"verified {len(data['claims'])} claim analysis digests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
