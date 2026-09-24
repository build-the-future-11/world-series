from __future__ import annotations
from world_series.qwipii.domains import RingState
from world_series.qwipii.group_actions import dihedral_actions, apply_to_state

def canonicalize(state: RingState):
    best = None
    best_name = None
    best_act = None
    for name, act in dihedral_actions(len(state.tokens)):
        s2 = apply_to_state(state, act)
        key = s2.serialize()
        if best is None or key < best:
            best = key
            best_name = name
            best_act = act
            best_state = s2
    return best_state, best_name, best_act
