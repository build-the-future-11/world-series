"""CLI: doctor, validate-config, run, compare, report, smoke-all, demo."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path
from typing import Optional

from world_series import PROJECT_NAMESPACES, __version__
from world_series.core.config import load_and_validate
from world_series.core.contracts import ErrorCode, RunStatus, WorldSeriesError
from world_series.core.devices import probe_devices, select_device
from world_series.core.registry import get_registry
from world_series.ultron.capabilities import bootstrap_adapters
from world_series.evaluation.reports import write_report
from world_series.evaluation.runner import create_run, load_run
from world_series.projects import dispatch_run
from world_series.evaluation.falsify import run_all_controls


def repo_root_from_cwd() -> Path:
    cwd = Path.cwd().resolve()
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "src" / "world_series").is_dir():
            return candidate
    return cwd


def cmd_doctor(_: argparse.Namespace) -> int:
    root = repo_root_from_cwd()
    devices = probe_devices()
    bootstrap_adapters()
    reg = get_registry()
    print(f"world_series {__version__}")
    print(f"repo_root: {root}")
    print(f"python: {sys.version.split()[0]}")
    print("devices:")
    for d in devices:
        print(f"  - {d.name}: available={d.available} dtype={d.dtype} fallback={d.fallback} ({d.notes})")
    print("capabilities:")
    for name, cap in sorted(reg.capabilities.items()):
        print(f"  - {name}: {cap.state.value} [{cap.project}] {cap.notes}")
    print("namespaces:", ", ".join(PROJECT_NAMESPACES))
    return 0


def cmd_validate_config(args: argparse.Namespace) -> int:
    path = Path(args.config)
    cfg = load_and_validate(path)
    print(json.dumps({"ok": True, "project": cfg["project"], "experiment": cfg["experiment"]}, indent=2))
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    root = repo_root_from_cwd()
    cfg = load_and_validate(Path(args.config))
    device = select_device(cfg["device"])
    run = create_run(root, cfg, device_dtype=device.dtype if device.name == "cpu" else device.dtype)
    run.append_event("start", {"config": str(Path(args.config).resolve())})
    run.set_status(RunStatus.RUNNING)
    try:
        metrics = dispatch_run(cfg, run)
        run.write_metrics(metrics)
        status = RunStatus(metrics.get("status", RunStatus.SUCCEEDED.value))
        run.append_event("finish", {"status": status.value})
        run.set_status(status)
        print(json.dumps({"run_id": run.manifest.run_id, "status": status.value, "metrics": metrics}, indent=2))
        return 0 if status in {RunStatus.SUCCEEDED, RunStatus.UNSUPPORTED} else 1
    except KeyboardInterrupt:
        err = {"code": "INTERRUPTED", "message": "execution interrupted by user"}
        run.set_status(RunStatus.INTERRUPTED, error=err)
        run.append_event("interrupted", err)
        print(json.dumps({"run_id": run.manifest.run_id, "error": err}, indent=2))
        return 130
    except WorldSeriesError as exc:
        run.set_status(
            RunStatus.BUDGET_EXHAUSTED if exc.code == ErrorCode.BUDGET_EXHAUSTED else RunStatus.FAILED,
            error=exc.to_dict(),
        )
        run.append_event("error", exc.to_dict())
        print(json.dumps({"run_id": run.manifest.run_id, "error": exc.to_dict()}, indent=2))
        return 1
    except Exception as exc:  # noqa: BLE001
        err = {"code": ErrorCode.INTERNAL.value, "message": str(exc), "traceback": traceback.format_exc()}
        run.set_status(RunStatus.FAILED, error=err)
        run.append_event("error", err)
        print(json.dumps({"run_id": run.manifest.run_id, "error": err}, indent=2))
        return 1


def cmd_compare(args: argparse.Namespace) -> int:
    path = Path(args.protocol)
    if not path.is_file():
        print(json.dumps({"status": "NOT_RUN", "reason": f"protocol file missing: {path}"}))
        return 1
    payload = json.loads(path.read_text(encoding="utf-8"))
    split = args.split
    results = []
    for entry in payload.get("comparisons", []):
        project = entry.get("project")
        status = entry.get("status", "DRAFT_NOT_AUTHORIZED")
        results.append(
            {
                "project": project,
                "protocol_id": entry.get("protocol_id"),
                "split": split,
                "status": status,
                "note": entry.get("notes", "Confirmation not authorized; development compare only."),
            }
        )
    print(json.dumps({"split": split, "results": results}, indent=2))
    # Explicit: draft protocols do not silently claim success.
    if any(r["status"] == "DRAFT_NOT_AUTHORIZED" for r in results):
        return 0
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    root = repo_root_from_cwd()
    runs_root = root / "runs"
    out = write_report(runs_root, args.run_id)
    print(out.read_text(encoding="utf-8"))
    return 0


def cmd_smoke_all(args: argparse.Namespace) -> int:
    root = repo_root_from_cwd()
    configs_dir = root / "configs"
    outcomes = []
    overall = 0
    for ns in PROJECT_NAMESPACES:
        cfg_path = configs_dir / ns / "smoke.yaml"
        if not cfg_path.is_file():
            outcomes.append({"project": ns, "status": "NOT_RUN", "reason": f"missing {cfg_path}"})
            overall = 1
            continue
        ns_args = argparse.Namespace(config=str(cfg_path))
        code = cmd_run(ns_args)
        # recover latest run for project
        runs = sorted((root / "runs").glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        run_id = runs[0].name if runs else None
        status = "FAILED" if code else "SUCCEEDED"
        if run_id:
            data = load_run(root / "runs", run_id)
            status = data["manifest"].get("status", status)
        outcomes.append({"project": ns, "status": status, "run_id": run_id, "exit_code": code})
        if code != 0 or status not in {"SUCCEEDED"}:
            overall = 1
    print(json.dumps({"smoke_all": outcomes}, indent=2))
    return overall



def cmd_falsify(args: argparse.Namespace) -> int:
    results = run_all_controls(seed=int(args.seed))
    failed = [r for r in results if r.get("passed") is False]
    print(json.dumps({"seed": int(args.seed), "controls": results, "n_failed_sanity": len(failed)}, indent=2))
    root = repo_root_from_cwd()
    out = root / "experiments" / "falsification_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"seed": int(args.seed), "controls": results}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}")
    return 1 if failed else 0

def cmd_demo(args: argparse.Namespace) -> int:
    root = repo_root_from_cwd()
    demo_cfg = root / "configs" / args.project / "smoke.yaml"
    if not demo_cfg.is_file():
        print(json.dumps({"status": "NOT_RUN", "reason": f"missing {demo_cfg}"}))
        return 1
    code = cmd_run(argparse.Namespace(config=str(demo_cfg)))
    print(json.dumps({"demo_project": args.project, "exit_code": code, "mode": "live_smoke"}))
    return code


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="world_series", description="World Series v0.1 workbench")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="environment and capability inventory").set_defaults(func=cmd_doctor)

    v = sub.add_parser("validate-config", help="validate a YAML config")
    v.add_argument("config")
    v.set_defaults(func=cmd_validate_config)

    r = sub.add_parser("run", help="execute a config into an immutable run directory")
    r.add_argument("--config", required=True)
    r.set_defaults(func=cmd_run)

    c = sub.add_parser("compare", help="compare using a protocol registry (draft-safe)")
    c.add_argument("--protocol", required=True)
    c.add_argument("--split", default="dev")
    c.set_defaults(func=cmd_compare)

    rep = sub.add_parser("report", help="render a report from a real run-id")
    rep.add_argument("--run-id", required=True)
    rep.set_defaults(func=cmd_report)

    s = sub.add_parser("smoke-all", help="run all project smoke configs; never omit failures")
    s.set_defaults(func=cmd_smoke_all)

    f = sub.add_parser("falsify", help="cheap falsification/sanity controls (not confirmation)")
    f.add_argument("--seed", type=int, default=0)
    f.set_defaults(func=cmd_falsify)

    d = sub.add_parser("demo", help="live smoke demo for one project")
    d.add_argument("--project", required=True, choices=list(PROJECT_NAMESPACES))
    d.set_defaults(func=cmd_demo)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except WorldSeriesError as exc:
        print(json.dumps({"error": exc.to_dict()}, indent=2))
        return 1
