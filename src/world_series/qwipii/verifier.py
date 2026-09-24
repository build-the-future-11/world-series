from __future__ import annotations
from world_series.qwipii.domains import RingState, neighbors, apply_move, legal_moves
from world_series.qwipii.group_actions import apply_to_state

def verify_automorphism(states: list[RingState], act) -> dict:
    """Check act preserves transitions and goals on the provided finite domain."""
    for s in states:
        g_ok = (s.tokens == s.goal) == (apply_to_state(s, act).tokens == apply_to_state(s, act).goal)
        if not g_ok:
            return {"ok": False, "reason": "goal_set_not_preserved", "state": s.serialize()}
        for move, nxt in neighbors(s):
            s2 = apply_to_state(s, act)
            nxt2 = apply_to_state(nxt, act)
            # corresponding move after conjugation: apply same named move in transformed coords
            # For dihedral board symmetries of this puzzle, named moves are not all equivariant.
            # We require existence of some legal move taking s2 to nxt2.
            reachable = {t.serialize() for _, t in neighbors(s2)}
            if nxt2.serialize() not in reachable:
                return {"ok": False, "reason": "transition_not_preserved", "state": s.serialize(), "move": move}
    return {"ok": True, "checked_states": len(states)}
