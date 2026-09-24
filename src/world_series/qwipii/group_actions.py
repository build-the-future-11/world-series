from __future__ import annotations
from world_series.qwipii.domains import RingState

def rotate_tokens(tokens: tuple[int, ...], k: int) -> tuple[int, ...]:
    n = len(tokens)
    k %= n
    return tokens[k:] + tokens[:k]

def reflect_tokens(tokens: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(reversed(tokens))

def dihedral_actions(n: int) -> list[tuple[str, callable]]:
    acts = []
    for k in range(n):
        acts.append((f"rot{k}", lambda tokens, k=k: rotate_tokens(tokens, k)))
    for k in range(n):
        acts.append((f"ref{k}", lambda tokens, k=k: rotate_tokens(reflect_tokens(tokens), k)))
    return acts

def apply_to_state(state: RingState, act) -> RingState:
    return RingState(act(state.tokens), act(state.goal))
