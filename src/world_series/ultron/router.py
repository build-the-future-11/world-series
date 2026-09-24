from __future__ import annotations
import random
from world_series.ultron.state import EpisodeState

TASK_DEFAULTS = {
    "invariant_puzzle": "solve_invariant_problem",
    "dsl_synthesis": "synthesize_dsl_program",
    "law_id": "identify_dynamical_law",
}

def static_route(state: EpisodeState, available: list[str]) -> str | None:
    pref = TASK_DEFAULTS.get(state.task_type)
    if pref in available:
        return pref
    return None

def cheapest_valid(state: EpisodeState, available: list[str]) -> str | None:
    # proxy: prefer shorter name as stand-in for cost ordering among valid
    valid = [a for a in available if a in TASK_DEFAULTS.values()]
    if state.task_type in TASK_DEFAULTS and TASK_DEFAULTS[state.task_type] in available:
        return TASK_DEFAULTS[state.task_type]
    return sorted(valid)[0] if valid else None

def random_valid(state: EpisodeState, available: list[str], seed: int = 0) -> str | None:
    valid = [a for a in available if a == TASK_DEFAULTS.get(state.task_type)]
    if not valid:
        return None
    rng = random.Random(seed)
    return rng.choice(valid)
