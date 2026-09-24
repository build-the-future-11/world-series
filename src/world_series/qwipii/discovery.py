from __future__ import annotations
from world_series.qwipii.group_actions import dihedral_actions, apply_to_state, rotate_tokens, reflect_tokens
from world_series.qwipii.verifier import verify_automorphism, complete_domain
from world_series.qwipii.domains import RingState

def propose_grammar(n: int) -> list[tuple[str, object, str]]:
    """Bounded grammar: dihedral actions + deliberately bad sort-prefix."""
    props = []
    for name, act in dihedral_actions(n):
        props.append((name, act, "dihedral"))
    # adversarial plausible transform
    props.append(("sort_suffix", lambda tokens: (tokens[0],) + tuple(sorted(tokens[1:])), "adversarial"))
    props.append(("identity", lambda tokens: tokens, "trivial"))
    return props

def score_proposal(act, states: list[RingState]) -> float:
    # heuristic: fraction of states where goal predicate preserved (not sufficient for pruning)
    ok = 0
    for s in states:
        s2 = apply_to_state(s, act)
        if (s.tokens == s.goal) == (s2.tokens == s2.goal):
            ok += 1
    return ok / max(len(states), 1)

def discover_and_verify(states: list[RingState]) -> list[dict]:
    if not states:
        raise ValueError("discovery requires a nonempty problem sample")
    goal = states[0].goal
    if any(s.goal != goal or sorted(s.tokens) != sorted(goal) for s in states):
        raise ValueError("discovery requires a single multiset problem domain")
    domain = complete_domain(goal)
    n = len(goal)
    out = []
    for name, act, kind in propose_grammar(n):
        score = score_proposal(act, states)
        ver = verify_automorphism(domain, act)
        label = "EXACTLY_VERIFIED_WITHIN_DOMAIN" if ver["ok"] else ("PROPOSED" if score > 0.5 else "REJECTED")
        if kind == "adversarial" and not ver["ok"]:
            label = "REJECTED"
        out.append({"name": name, "kind": kind, "score": score, "verified": ver["ok"], "label": label, "ver": ver})
    return out
