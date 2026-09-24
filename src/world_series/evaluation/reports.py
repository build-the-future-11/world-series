"""Reports generated from real run artifacts only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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
    out.write_text(text, encoding="utf-8")
    return out
