"""Family-level split controls."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable, Sequence

from world_series.core.contracts import ErrorCode, WorldSeriesError
from world_series.core.seeds import SeededStreams


@dataclass(frozen=True)
class FamilyRecord:
    family_id: str
    item_id: str
    payload: object


def split_by_family(
    records: Sequence[FamilyRecord],
    *,
    fractions: dict[str, float],
    streams: SeededStreams,
) -> dict[str, list[FamilyRecord]]:
    """Split whole families, never adjacent rows from the same family."""
    if abs(sum(fractions.values()) - 1.0) > 1e-9:
        raise WorldSeriesError(ErrorCode.INVALID_CONFIG, "split fractions must sum to 1")
    by_family: dict[str, list[FamilyRecord]] = {}
    for r in records:
        by_family.setdefault(r.family_id, []).append(r)
    families = sorted(by_family)
    streams.data.shuffle(families)
    n = len(families)
    out: dict[str, list[FamilyRecord]] = {k: [] for k in fractions}
    # assign contiguous blocks after shuffle
    keys = list(fractions.keys())
    cuts = []
    acc = 0.0
    for k in keys[:-1]:
        acc += fractions[k]
        cuts.append(int(round(acc * n)))
    cuts.append(n)
    start = 0
    for k, end in zip(keys, cuts):
        for fam in families[start:end]:
            out[k].extend(by_family[fam])
        start = end
    # leakage check
    assigned: dict[str, str] = {}
    for split_name, items in out.items():
        for item in items:
            if item.family_id in assigned and assigned[item.family_id] != split_name:
                raise WorldSeriesError(
                    ErrorCode.INTERNAL,
                    f"family leakage for {item.family_id}",
                )
            assigned[item.family_id] = split_name
    return out


def assert_disjoint_ids(a: Iterable[Hashable], b: Iterable[Hashable], label: str = "ids") -> None:
    sa, sb = set(a), set(b)
    overlap = sa & sb
    if overlap:
        raise WorldSeriesError(ErrorCode.INTERNAL, f"{label} overlap: {sorted(list(overlap))[:5]}")
