#!/usr/bin/env python3
"""Verify the published finite-closure archive and run restored-source checks."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".work-tmp" / "OSS_VERIFY_20260926"
DELIVERY = ROOT / "deliveries" / "20260924-finite-closure"
PY = ROOT / ".venv" / "bin" / "python"
EXPECTED_SHA = "f9ce4c2f8a1cfbdff969db392492870438607fe6b1d44c9f38b1d2d94c413a53"
ARCHIVE_SHA = EXPECTED_SHA


def run(name: str, argv: list[str], cwd: Path | None = None, timeout: int = 3600, env: dict | None = None) -> bool:
    start = time.monotonic()
    cwd = cwd or ROOT
    logfile = OUT / f"{name}.log"
    use_env = dict(os.environ)
    use_env.update(
        {
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
            "PYTHONNOUSERSITE": "1",
        }
    )
    if env:
        use_env.update(env)
    with logfile.open("w") as handle:
        try:
            proc = subprocess.run(
                argv,
                cwd=cwd,
                stdout=handle,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                env=use_env,
            )
            code = proc.returncode
        except subprocess.TimeoutExpired:
            code = 124
    row = {
        "step": name,
        "argv": argv,
        "cwd": str(cwd),
        "exit_code": code,
        "seconds": round(time.monotonic() - start, 3),
        "log": logfile.name,
        "log_sha256": hashlib.sha256(logfile.read_bytes()).hexdigest(),
    }
    with (OUT / "steps.jsonl").open("a") as handle:
        handle.write(json.dumps(row) + "\n")
    print(json.dumps(row), flush=True)
    return code == 0


def main() -> int:
    if OUT.exists():
        # Keep prior partial logs but require fresh extract dirs
        for name in ("extracted", "restored", "pytest"):
            path = OUT / name
            if path.exists():
                raise SystemExit(f"Refusing to overwrite existing {path}; remove it first")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "steps.jsonl").write_text("")

    ok = True
    archive = DELIVERY / "world-series-review.tar.gz"
    got = hashlib.sha256(archive.read_bytes()).hexdigest()
    sha_ok = got == EXPECTED_SHA
    print(json.dumps({"step": "archive_sha", "exit_code": 0 if sha_ok else 1, "got": got}), flush=True)
    ok &= sha_ok

    ok &= run(
        "verify_delivery",
        [str(PY), "scripts/verify_delivery.py", str(DELIVERY), "--extract", str(OUT / "extracted")],
        timeout=7200,
    )
    ok &= run(
        "restore_delivery",
        [str(PY), "scripts/restore_delivery.py", str(OUT / "extracted"), "--output", str(OUT / "restored")],
    )

    restored = OUT / "restored"
    ok &= run("claim_verify", [str(PY), "scripts/verify_headline_claims.py", "--claim-index", "results/claim_index.json"], cwd=ROOT)
    ok &= run("tests", [str(PY), "-m", "pytest", "tests", "-q", "--basetemp", str(OUT / "pytest")], cwd=restored)
    ok &= run(
        "doctor",
        [str(PY), "-m", "world_series", "doctor"],
        cwd=restored,
        env={"PYTHONPATH": str(restored / "src")},
    )
    ok &= run(
        "wfim_predictions",
        [
            str(PY),
            "scripts/closure/analyze_wfim_learning.py",
            "--root",
            "campaigns/wfim-coordinate-development-v1",
            "--output",
            str(OUT / "wfim_predictions.json"),
        ],
        cwd=restored,
        env={"PYTHONPATH": str(restored / "src")},
    )
    ok &= run(
        "artifact_audit",
        [str(PY), "scripts/audit_development.py"],
        cwd=restored,
        env={"PYTHONPATH": str(restored / "src")},
    )

    summary = {
        "passed": ok,
        "archive_sha256": got,
        "expected_sha256": EXPECTED_SHA,
        "scope": "Published finite-closure archive integrity + restored-source tests/doctor/WFIM prediction analysis; not independent replication or full nine-study retrain.",
        "repos": {
            "implementation": "https://github.com/build-the-future-11/world-series",
            "records": "https://github.com/build-the-future-11/world-series-research-records",
            "release": "https://github.com/build-the-future-11/world-series/releases/tag/v0.1.0-oss",
        },
    }
    (OUT / "reproduction.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("SUMMARY " + json.dumps(summary), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
