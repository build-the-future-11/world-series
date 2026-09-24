"""Module capability registry — no fake successes for missing adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional

from world_series.core.contracts import ErrorCode, ModuleRequest, ModuleResult, RunStatus, WorldSeriesError


class CapabilityState(str, Enum):
    AVAILABLE = "AVAILABLE"
    UNAVAILABLE = "UNAVAILABLE"
    BLOCKED_BY_CONTRACT = "BLOCKED_BY_CONTRACT"


Handler = Callable[[ModuleRequest], ModuleResult]


@dataclass
class Capability:
    name: str
    project: str
    state: CapabilityState
    handler: Optional[Handler] = None
    notes: str = ""


@dataclass
class Registry:
    capabilities: dict[str, Capability] = field(default_factory=dict)

    def register(self, cap: Capability) -> None:
        self.capabilities[cap.name] = cap

    def get(self, name: str) -> Capability:
        if name not in self.capabilities:
            raise WorldSeriesError(ErrorCode.UNSUPPORTED_CAPABILITY, f"unknown capability '{name}'")
        return self.capabilities[name]

    def list_available(self) -> list[str]:
        return sorted(n for n, c in self.capabilities.items() if c.state == CapabilityState.AVAILABLE)

    def execute(self, request: ModuleRequest) -> ModuleResult:
        cap = self.get(request.operation)
        if cap.state != CapabilityState.AVAILABLE or cap.handler is None:
            return ModuleResult(
                status=RunStatus.UNSUPPORTED,
                error=WorldSeriesError(
                    ErrorCode.UNSUPPORTED_CAPABILITY,
                    f"capability '{request.operation}' is {cap.state.value}",
                    {"notes": cap.notes},
                ).to_dict(),
            )
        return cap.handler(request)


_GLOBAL: Optional[Registry] = None


def get_registry() -> Registry:
    global _GLOBAL
    if _GLOBAL is None:
        _GLOBAL = Registry()
        _bootstrap_defaults(_GLOBAL)
    return _GLOBAL


def reset_registry_for_tests() -> Registry:
    global _GLOBAL
    _GLOBAL = Registry()
    _bootstrap_defaults(_GLOBAL)
    return _GLOBAL


def _bootstrap_defaults(reg: Registry) -> None:
    for name, project, notes in [
        ("adapt_learner", "qlearn", "registers after QL adapter"),
        ("predict_world", "qapen", "registers after QA adapter"),
        ("solve_invariant_problem", "qwipii", "registers after QW adapter"),
        ("verify_certificate", "qwipii", "registers after QW adapter"),
        ("synthesize_dsl_program", "wcode", "registers after WC adapter"),
        ("algebra_multiply", "wfim", "registers after WF adapter"),
        ("spectral_transform", "wft", "registers after FT adapter"),
        ("identify_dynamical_law", "wpinn", "registers after WP adapter"),
        ("encode_multiscale_world", "cwlnn", "registers after CW adapter"),
        ("orchestrate_episode", "ultron", "registers after UL adapter"),
    ]:
        reg.register(
            Capability(name=name, project=project, state=CapabilityState.UNAVAILABLE, notes=notes)
        )
