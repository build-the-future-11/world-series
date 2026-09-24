from __future__ import annotations
from collections import deque
from world_series.qwipii.domains import RingState, neighbors, is_goal
from world_series.qwipii.canonicalize import canonicalize
from world_series.core.budgets import BudgetLedger

def bfs(start: RingState, ledger: BudgetLedger, max_expansions: int = 500):
    q = deque([(start, [])])
    seen = {start.serialize()}
    expansions = 0
    while q:
        ledger.consume_candidates(1)
        state, path = q.popleft()
        expansions += 1
        if expansions > max_expansions:
            return None, expansions, "budget"
        if is_goal(state):
            return path, expansions, "solved"
        for move, nxt in neighbors(state):
            key = nxt.serialize()
            if key not in seen:
                seen.add(key)
                q.append((nxt, path + [move]))
    return None, expansions, "exhausted"

def quotient_bfs(start: RingState, ledger: BudgetLedger, max_expansions: int = 500):
    start_can, _, _ = canonicalize(start)
    q = deque([(start_can, [])])
    seen = {start_can.serialize()}
    expansions = 0
    while q:
        ledger.consume_candidates(1)
        state, path = q.popleft()
        expansions += 1
        if expansions > max_expansions:
            return None, expansions, "budget"
        if is_goal(state):
            return path, expansions, "solved"
        for move, nxt in neighbors(state):
            nxt_can, _, _ = canonicalize(nxt)
            key = nxt_can.serialize()
            if key not in seen:
                seen.add(key)
                q.append((nxt_can, path + [move]))
    return None, expansions, "exhausted"

def ranking_only_bfs(start: RingState, ledger: BudgetLedger, ranker, max_expansions: int = 500):
    """BFS order perturbed by ranker scores; never merges/prunes by approximate invariance."""
    # use priority queue by (-score, expansions, state)
    import heapq
    start_can, _, _ = canonicalize(start)
    h = []
    counter = 0
    heapq.heappush(h, (-ranker(start), counter, start, []))
    seen = {start.serialize()}
    expansions = 0
    while h:
        ledger.consume_candidates(1)
        _, _, state, path = heapq.heappop(h)
        expansions += 1
        if expansions > max_expansions:
            return None, expansions, "budget"
        if is_goal(state):
            return path, expansions, "solved"
        for move, nxt in neighbors(state):
            key = nxt.serialize()
            if key not in seen:
                seen.add(key)
                counter += 1
                heapq.heappush(h, (-ranker(nxt), counter, nxt, path + [move]))
    return None, expansions, "exhausted"

def replay(start: RingState, path: list[str]) -> RingState:
    from world_series.qwipii.domains import apply_move
    s = start
    for m in path:
        s = apply_move(s, m)
    return s
