from __future__ import annotations
from world_series.core.contracts import ModuleRequest, ModuleResult, RunStatus
from world_series.core.registry import Capability, CapabilityState, get_registry
import numpy as np
from world_series.cwlnn.graphs import GraphLevel, path_edges
from world_series.cwlnn.model import forward_multiscale

def encode_multiscale_world(request: ModuleRequest) -> ModuleResult:
    feats = np.ones((8, 2))
    out, receipt = forward_multiscale(GraphLevel(feats, path_edges(8)), route_budget=3)
    return ModuleResult(status=RunStatus.SUCCEEDED, diagnostics={"out_mean": float(out.mean()), "routing": receipt.actual if receipt else None}, verification_status="REFERENCE")

def register() -> None:
    get_registry().register(Capability("encode_multiscale_world", "cwlnn", CapabilityState.AVAILABLE, handler=encode_multiscale_world))
