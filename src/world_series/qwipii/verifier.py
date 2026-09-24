from __future__ import annotations

from collections import Counter
from hashlib import sha256
from math import factorial
import json
from world_series.qwipii.domains import RingState, neighbors


def complete_domain(goal: tuple[int, ...], max_states: int = 10000) -> list[RingState]:
    """Enumerate unique multiset permutations, checking allocation limit first."""
    if not goal:
        raise ValueError("empty ring")
    counts = Counter(goal)
    size = factorial(len(goal))
    for count in counts.values():
        size //= factorial(count)
    if size > max_states:
        raise ValueError(f"domain requires {size} states; cap is {max_states}")
    result = []
    def visit(prefix):
        if len(prefix) == len(goal):
            result.append(RingState(tuple(prefix), goal))
            return
        for token in sorted(counts):
            if counts[token]:
                counts[token] -= 1
                visit(prefix + [token])
                counts[token] += 1
    visit([])
    return result


def verify_automorphism(states: list[RingState], act, *, fixed_goal: bool = False) -> dict:
    """Exact unit-cost ring isomorphism; fixed_goal additionally certifies pruning.

    Input must exhaust one multiset domain. Simultaneous transformation of board
    and goal certifies equivalence to another problem, not a fixed-goal action.
    The witness records evaluated images, never an approval of future calls to act.
    """
    def fail(reason, **witness):
        return {"ok": False, "reason": reason, **witness}
    if not states:
        return fail("empty_domain")
    goal = states[0].goal
    if not goal or any(s.goal != goal or Counter(s.tokens) != Counter(goal) for s in states):
        return fail("inconsistent_domain")
    domain = {s.tokens for s in states}
    if len(domain) != len(states):
        return fail("duplicate_states")
    expected = factorial(len(goal))
    for count in Counter(goal).values():
        expected //= factorial(count)
    if len(domain) != expected:
        return fail("incomplete_domain", expected_states=expected, checked_states=len(domain))
    try:
        mapping = {t: tuple(act(t)) for t in sorted(domain)}
        # Detect ordinary stateful proposals before issuing a witness.
        if any(tuple(act(t)) != mapping[t] for t in sorted(domain)):
            return fail("unstable_action")
    except Exception as exc:
        return fail("action_error", error=type(exc).__name__)
    target_goal = mapping[goal]
    if fixed_goal and target_goal != goal:
        return fail("goal_not_fixed")
    if any(Counter(t) != Counter(goal) for t in mapping.values()):
        return fail("multiset_not_preserved")
    if len(set(mapping.values())) != expected:
        return fail("not_bijective")
    edges = 0
    for tokens in sorted(domain):
        s = RingState(tokens, goal)
        target = RingState(mapping[tokens], target_goal)
        if (tokens == goal) != (target.tokens == target.goal):
            return fail("goal_set_not_preserved", state=s.serialize())
        reachable = {t.tokens for _, t in neighbors(target)}
        for move, nxt in neighbors(s):
            edges += 1
            if mapping[nxt.tokens] not in reachable:
                return fail("transition_not_preserved", state=s.serialize(), move=move)
    witness = {"goal": goal, "target_goal": target_goal,
               "mapping": [[t, mapping[t]] for t in sorted(domain)],
               "unit_edge_cost": 1, "domain_version": "ring-multiset-v1",
               "scope": "fixed_goal" if fixed_goal else "simultaneous_problem_equivalence"}
    digest = sha256(json.dumps(witness, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"ok": True, "checked_states": expected, "checked_edges": edges,
            "complete_domain": True, "witness": witness, "witness_sha256": digest}
