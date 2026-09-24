from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from world_series.core.contracts import ErrorCode, WorldSeriesError
from world_series.core.artifacts import sha256_bytes
import json

@dataclass
class EvidenceNode:
    node_id: str
    parents: tuple[str, ...]
    payload_hash: str
    verifier: str

@dataclass
class EvidenceDAG:
    nodes: dict[str, EvidenceNode] = field(default_factory=dict)

    def add(self, node_id: str, parents: tuple[str, ...], payload: dict[str, Any], verifier: str) -> EvidenceNode:
        for p in parents:
            if p not in self.nodes:
                raise WorldSeriesError(ErrorCode.VERIFICATION_FAILED, f"missing parent evidence {p}")
        # cycle check: parents should not reach node_id
        if node_id in self.nodes:
            raise WorldSeriesError(ErrorCode.VERIFICATION_FAILED, "duplicate evidence id")
        blob = json.dumps(payload, sort_keys=True).encode()
        node = EvidenceNode(node_id, parents, sha256_bytes(blob), verifier)
        self.nodes[node_id] = node
        return node
