"""Experiment protocol registry — confirmation stays DRAFT_NOT_AUTHORIZED until frozen."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Sequence


class ProtocolStatus(str, Enum):
    DRAFT_NOT_AUTHORIZED = "DRAFT_NOT_AUTHORIZED"
    FROZEN = "FROZEN"
    INVALIDATED = "INVALIDATED"


@dataclass
class ProtocolSpec:
    protocol_id: str
    project: str
    primary_metric: str
    effect_direction: str
    practical_effect: Optional[float]
    baselines: Sequence[str]
    tuning_budget: dict[str, Any]
    uncertainty_method: str
    stopping_rule: str
    code_identity: str
    config_identity: str
    status: ProtocolStatus = ProtocolStatus.DRAFT_NOT_AUTHORIZED
    notes: str = ""


@dataclass
class ProtocolRegistry:
    protocols: dict[str, ProtocolSpec] = field(default_factory=dict)

    def add(self, spec: ProtocolSpec) -> None:
        self.protocols[spec.protocol_id] = spec

    def get(self, protocol_id: str) -> ProtocolSpec:
        return self.protocols[protocol_id]

    def to_jsonable(self) -> dict[str, Any]:
        out = {}
        for k, v in self.protocols.items():
            d = asdict(v)
            d["status"] = v.status.value
            out[k] = d
        return out

    @staticmethod
    def load(path: Path) -> "ProtocolRegistry":
        payload = json.loads(path.read_text(encoding="utf-8"))
        reg = ProtocolRegistry()
        for item in payload.get("protocols", []):
            status = ProtocolStatus(item.get("status", ProtocolStatus.DRAFT_NOT_AUTHORIZED.value))
            reg.add(
                ProtocolSpec(
                    protocol_id=item["protocol_id"],
                    project=item["project"],
                    primary_metric=item["primary_metric"],
                    effect_direction=item.get("effect_direction", "lower_better"),
                    practical_effect=item.get("practical_effect"),
                    baselines=item.get("baselines", []),
                    tuning_budget=item.get("tuning_budget", {}),
                    uncertainty_method=item.get("uncertainty_method", "paired_bootstrap_dev"),
                    stopping_rule=item.get("stopping_rule", "fixed_budget"),
                    code_identity=item.get("code_identity", ""),
                    config_identity=item.get("config_identity", ""),
                    status=status,
                    notes=item.get("notes", ""),
                )
            )
        return reg
