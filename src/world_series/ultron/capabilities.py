from __future__ import annotations

import importlib

from world_series.core.registry import CapabilityState, get_registry


def bootstrap_adapters() -> None:
    for mod in (
        "world_series.qwipii.adapter",
        "world_series.wcode.adapter",
        "world_series.wpinn.adapter",
        "world_series.qlearn.adapter",
        "world_series.qapen.adapter",
        "world_series.wfim.adapter",
        "world_series.wft.adapter",
        "world_series.cwlnn.adapter",
        "world_series.ultron.adapter",
    ):
        try:
            importlib.import_module(mod).register()
        except Exception:
            continue


def available_ops() -> list[str]:
    reg = get_registry()
    return [n for n, c in reg.capabilities.items() if c.state == CapabilityState.AVAILABLE]
