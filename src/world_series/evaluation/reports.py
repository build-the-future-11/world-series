"""Reports generated from real run artifacts only."""

from __future__ import annotations

import json
from pathlib import Path

from world_series.core.artifacts import publish_bytes
from world_series.core.contracts import ErrorCode, WorldSeriesError
from world_series.evaluation.runner import load_run


def render_report(runs_root: Path, run_id: str) -> str:
    data = load_run(runs_root, run_id)
    m = data["manifest"]
    metrics = data["metrics"]
    lines = [
        f"# Report for run `{run_id}`",
        "",
        f"- project: `{m.get('project')}`",
        f"- experiment: `{m.get('experiment')}`",
        f"- split: `{m.get('split')}`",
        f"- status: `{m.get('status')}`",
        f"- device/dtype: `{m.get('device')}` / `{m.get('dtype')}`",
        f"- config_hash: `{m.get('config_hash')}`",
        f"- git_head: `{m.get('source', {}).get('git_head')}`",
        f"- git_dirty: `{m.get('source', {}).get('git_dirty')}`",
        f"- content_hash: `{m.get('source', {}).get('content_hash')}`",
        "",
        "## Metrics",
        "",
    ]
    if not metrics:
        lines.append("_No metrics.json present (NOT_RUN or failed before write)._")
    else:
        lines.append("```json")
        lines.append(json.dumps(metrics, indent=2, sort_keys=True))
        lines.append("```")
    if m.get("error"):
        lines.extend(["", "## Error", "", "```json", json.dumps(m["error"], indent=2), "```"])
    verification = data["verification"]
    lines.extend([
        "", "## Evidence verification", "",
        f"- {verification['referenced_artifacts_verified']} referenced artifact files matched their recorded SHA-256 hashes.",
        f"- {verification['unreferenced_artifact_count']} other artifact files have no recorded hash binding in metrics/events.",
        f"- {verification['scope']}",
    ])
    lines.extend(
        [
            "",
            "## Events",
            "",
            f"- event_count: {len(data['events'])}",
            f"- path: `{data['path']}`",
            "",
            "_This report is generated from on-disk artifacts only._",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(runs_root: Path, run_id: str, out_path: Path | None = None) -> Path:
    text = render_report(runs_root, run_id)
    out = out_path or (runs_root / run_id / "report.md")
    run_path = (runs_root / run_id).resolve()
    resolved = out.resolve()
    # Custom destinations may point at a different retained run or run root.
    # Recognize their evidence layout before publishing a derived document.
    candidates = {run_path}
    for ancestor in resolved.parents:
        if (ancestor / "manifest.json").is_file() and (
            (ancestor / "artifacts").is_dir() or (ancestor / "events.jsonl").is_file()
        ):
            candidates.add(ancestor)
    for candidate in candidates:
        if (resolved in {candidate / name for name in ("manifest.json", "metrics.json", "events.jsonl")}
                or resolved.is_relative_to(candidate / "artifacts")):
            raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "a report cannot replace retained raw run evidence")
    publish_bytes(out, text.encode("utf-8"), overwrite=True)
    return out
