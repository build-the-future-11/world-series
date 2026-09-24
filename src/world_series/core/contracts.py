"""Typed contracts, status enums, and structured errors."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping, MutableMapping, Optional, Sequence


class EvidenceState(str, Enum):
    SPECIFIED = "SPECIFIED"
    IMPLEMENTED = "IMPLEMENTED"
    SMOKE_PASSED = "SMOKE_PASSED"
    BENCHMARKED = "BENCHMARKED"
    SUPPORTED = "SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    INCONCLUSIVE = "INCONCLUSIVE"
    BLOCKED = "BLOCKED"
    NOT_RUN = "NOT_RUN"
    INVALIDATED = "INVALIDATED"


class RunStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    INTERRUPTED = "INTERRUPTED"
    UNSUPPORTED = "UNSUPPORTED"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"


class ErrorCode(str, Enum):
    INVALID_CONFIG = "INVALID_CONFIG"
    INVALID_SHAPE = "INVALID_SHAPE"
    INVALID_DTYPE = "INVALID_DTYPE"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    BUDGET_EXHAUSTED = "BUDGET_EXHAUSTED"
    UNSUPPORTED_CAPABILITY = "UNSUPPORTED_CAPABILITY"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    INTERNAL = "INTERNAL"


class WorldSeriesError(Exception):
    def __init__(self, code: ErrorCode, message: str, details: Optional[Mapping[str, Any]] = None):
        super().__init__(f"{code.value}: {message}")
        self.code = code
        self.message = message
        self.details = dict(details or {})

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code.value, "message": self.message, "details": self.details}


@dataclass(frozen=True)
class Budget:
    max_steps: int = 32
    max_wall_seconds: float = 30.0
    max_simulator_calls: int = 10_000
    max_candidate_evals: int = 10_000
    max_artifact_bytes: int = 50_000_000
    max_planned_memory_bytes: int = 512_000_000
    max_graph_nodes: int = 128
    max_algebra_degree: int = 6
    max_dsl_depth: int = 6
    max_experts: int = 8

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if isinstance(value, (int, float)) and value < 0:
                raise WorldSeriesError(ErrorCode.INVALID_CONFIG, f"Budget.{name} must be non-negative")


@dataclass(frozen=True)
class TaskSpec:
    project_id: str
    task_family: str
    public_inputs: Mapping[str, Any]
    resource_contract: Budget
    split_id: str
    objective: str
    schema_version: str = "0.1.0"
    task_id: str = ""

    def __post_init__(self) -> None:
        if "answer" in self.public_inputs or "labels_query" in self.public_inputs:
            raise WorldSeriesError(
                ErrorCode.INVALID_CONFIG,
                "TaskSpec.public_inputs must not contain inaccessible evaluation answers",
            )


@dataclass(frozen=True)
class ArrayMeta:
    name: str
    shape: Sequence[int]
    dtype: str
    source_id: str = ""


@dataclass
class ObservationBatch:
    arrays: MutableMapping[str, Any]
    masks: MutableMapping[str, Any] = field(default_factory=dict)
    meta: Sequence[ArrayMeta] = field(default_factory=tuple)
    source_ids: Sequence[str] = field(default_factory=tuple)

    def require(self, name: str, ndim: Optional[int] = None) -> Any:
        if name not in self.arrays:
            raise WorldSeriesError(ErrorCode.INVALID_SHAPE, f"Missing array '{name}'")
        arr = self.arrays[name]
        if ndim is not None and getattr(arr, "ndim", None) != ndim:
            raise WorldSeriesError(
                ErrorCode.INVALID_SHAPE,
                f"Array '{name}' expected ndim={ndim}, got {getattr(arr, 'ndim', None)}",
            )
        return arr


@dataclass(frozen=True)
class ArtifactRef:
    relative_path: str
    sha256: str
    producer_run_id: str
    schema_version: str
    media_type: str


@dataclass(frozen=True)
class ModuleRequest:
    request_id: str
    operation: str
    input_artifacts: Sequence[ArtifactRef]
    config_hash: str
    budget: Budget
    allowed_output_types: Sequence[str]
    schema_version: str = "0.1.0"


@dataclass
class ModuleResult:
    status: RunStatus
    outputs: list[ArtifactRef] = field(default_factory=list)
    measured_cost: dict[str, float] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)
    verification_status: str = "NOT_RUN"
    error: Optional[dict[str, Any]] = None


@dataclass(frozen=True)
class EvidenceRecord:
    claim_id: str
    protocol_id: str
    input_hash: str
    run_hash: str
    metric_name: str
    raw_trial_refs: Sequence[str]
    verifier_result: str
    limitations: Sequence[str]
    state: EvidenceState = EvidenceState.NOT_RUN
    value: Optional[float] = None
    unit: str = ""
    sample_count: int = 0
