from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass(frozen=True)
class RingState:
    tokens: tuple[int, ...]
    goal: tuple[int, ...]

    def serialize(self) -> str:
        return ",".join(map(str, self.tokens)) + "|" + ",".join(map(str, self.goal))

def legal_moves(n: int) -> list[str]:
    # rotate L/R and adjacent swap at position 0..n-1
    return ["rotL", "rotR"] + [f"swap{i}" for i in range(n)]

def apply_move(state: RingState, move: str) -> RingState:
    t = list(state.tokens)
    n = len(t)
    if move == "rotL":
        t = t[1:] + t[:1]
    elif move == "rotR":
        t = t[-1:] + t[:-1]
    elif move.startswith("swap"):
        i = int(move[4:])
        j = (i + 1) % n
        t[i], t[j] = t[j], t[i]
    else:
        raise ValueError(move)
    return RingState(tuple(t), state.goal)

def is_goal(state: RingState) -> bool:
    return state.tokens == state.goal

def neighbors(state: RingState) -> Iterable[tuple[str, RingState]]:
    for m in legal_moves(len(state.tokens)):
        yield m, apply_move(state, m)
