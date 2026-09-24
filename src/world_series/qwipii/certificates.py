from __future__ import annotations
from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class Certificate:
    domain_version: str
    property_name: str
    assumptions: list[str]
    witness: dict[str, Any]
    verification_method: str
    ok: bool

    def to_dict(self):
        return asdict(self)
