"""Project run dispatch — each namespace implements smoke/dev experiments."""

from __future__ import annotations

from typing import Any, Callable

from world_series.core.contracts import RunStatus
from world_series.core.seeds import set_global_determinism
from world_series.evaluation.runner import RunDirectory

Runner = Callable[[dict[str, Any], RunDirectory], dict[str, Any]]


def _unsupported(project: str) -> Runner:
    def _run(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
        run.append_event("unsupported", {"project": project})
        return {
            "status": RunStatus.UNSUPPORTED.value,
            "project": project,
            "note": f"{project} runner not registered yet",
        }

    return _run


def dispatch_run(cfg: dict[str, Any], run: RunDirectory) -> dict[str, Any]:
    project = cfg["project"]
    runners = _load_runners()
    runner = runners.get(project, _unsupported(project))
    seed_receipt = set_global_determinism(int(cfg['seed']))
    run.append_event('seed_control', {'seed': int(cfg['seed']), **seed_receipt})
    if cfg.get("params", {}).get("study") == "development_v2":
        from world_series.evaluation.development import run_experiment
        return run_experiment(cfg, run)
    if cfg.get("params", {}).get("study") == "natural_digits_v1":
        from world_series.qlearn.natural_study import run_experiment
        return run_experiment(cfg, run)
    if cfg.get("params", {}).get("study") == "discrete_malis_v1":
        from world_series.qlearn.malis import run_experiment
        return run_experiment(cfg, run)
    return runner(cfg, run)


def _load_runners() -> dict[str, Runner]:
    # Lazy imports so missing optional modules do not break doctor/validate.
    out: dict[str, Runner] = {}
    try:
        from world_series.qlearn.evaluate import run_experiment as qlearn_run

        out["qlearn"] = qlearn_run
    except Exception:  # noqa: BLE001
        out["qlearn"] = _unsupported("qlearn")
    try:
        from world_series.qapen.evaluate import run_experiment as qapen_run

        out["qapen"] = qapen_run
    except Exception:  # noqa: BLE001
        out["qapen"] = _unsupported("qapen")
    try:
        from world_series.qwipii.evaluate import run_experiment as qwipii_run

        out["qwipii"] = qwipii_run
    except Exception:  # noqa: BLE001
        out["qwipii"] = _unsupported("qwipii")
    try:
        from world_series.wcode.evaluate import run_experiment as wcode_run

        out["wcode"] = wcode_run
    except Exception:  # noqa: BLE001
        out["wcode"] = _unsupported("wcode")
    try:
        from world_series.wfim.evaluate import run_experiment as wfim_run

        out["wfim"] = wfim_run
    except Exception:  # noqa: BLE001
        out["wfim"] = _unsupported("wfim")
    try:
        from world_series.wft.evaluate import run_experiment as wft_run

        out["wft"] = wft_run
    except Exception:  # noqa: BLE001
        out["wft"] = _unsupported("wft")
    try:
        from world_series.wpinn.evaluate import run_experiment as wpinn_run

        out["wpinn"] = wpinn_run
    except Exception:  # noqa: BLE001
        out["wpinn"] = _unsupported("wpinn")
    try:
        from world_series.cwlnn.evaluate import run_experiment as cwlnn_run

        out["cwlnn"] = cwlnn_run
    except Exception:  # noqa: BLE001
        out["cwlnn"] = _unsupported("cwlnn")
    try:
        from world_series.ultron.evaluate import run_experiment as ultron_run

        out["ultron"] = ultron_run
    except Exception:  # noqa: BLE001
        out["ultron"] = _unsupported("ultron")
    return out
