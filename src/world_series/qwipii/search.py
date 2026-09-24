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
        if expansions >= max_expansions:
            return None, expansions, "budget"
        ledger.consume_candidates(1)
        state, path = q.popleft()
        expansions += 1
        if is_goal(state):
            return path, expansions, "solved"
        for move, nxt in neighbors(state):
            key = nxt.serialize()
            if key not in seen:
                seen.add(key)
                q.append((nxt, path + [move]))
    return None, expansions, "exhausted"

def quotient_bfs(start: RingState, ledger: BudgetLedger, max_expansions: int = 500):
    # Canonical keys merge orbits; queued representatives retain replayable coordinates.
    start_can, _, _ = canonicalize(start)
    q = deque([(start, [])])
    seen = {start_can.serialize()}
    expansions = 0
    while q:
        if expansions >= max_expansions:
            return None, expansions, "budget"
        ledger.consume_candidates(1)
        state, path = q.popleft()
        expansions += 1
        if is_goal(state):
            return path, expansions, "solved"
        for move, nxt in neighbors(state):
            nxt_can, _, _ = canonicalize(nxt)
            key = nxt_can.serialize()
            if key not in seen:
                seen.add(key)
                q.append((nxt, path + [move]))
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
        if expansions >= max_expansions:
            return None, expansions, "budget"
        ledger.consume_candidates(1)
        _, _, state, path = heapq.heappop(h)
        expansions += 1
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


def certified_quotient_bfs(start: RingState, ledger: BudgetLedger, certificates: list[dict],
                           max_expansions: int = 500, max_states: int = 10000):
    """Revalidate serialized maps, close generator orbits, then retain concrete paths.

    A supplied ok flag or hash is not trusted. No proposal callable is executed.
    All certificate loading and orbit construction happen within the timed call.
    """
    from world_series.qwipii.verifier import complete_domain, verify_automorphism
    domain = complete_domain(start.goal, max_states=max_states)
    tokens = {s.tokens for s in domain}
    if start.tokens not in tokens:
        raise ValueError("start is outside certificate domain")
    parent = {t: t for t in tokens}

    def find(t):
        while parent[t] != t:
            parent[t] = parent[parent[t]]
            t = parent[t]
        return t

    for certificate in certificates:
        witness = certificate.get("witness", {})
        if witness.get("scope") != "fixed_goal" or tuple(witness.get("goal", ())) != start.goal:
            raise ValueError("certificate must preserve this fixed goal")
        pairs = witness.get("mapping", [])
        mapping = {tuple(a): tuple(b) for a, b in pairs}
        if len(mapping) != len(pairs) or set(mapping) != tokens:
            raise ValueError("certificate mapping must exhaust this domain exactly once")
        verified = verify_automorphism(domain, mapping.__getitem__, fixed_goal=True)
        if not verified["ok"] or verified["witness_sha256"] != certificate.get("witness_sha256"):
            raise ValueError("invalid or altered certificate")
        for a, b in mapping.items():
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[max(ra, rb)] = min(ra, rb)
    keys = {t: find(t) for t in tokens}
    q = deque([(start, [])])
    seen = {keys[start.tokens]}
    expansions = 0
    while q:
        if expansions >= max_expansions:
            return None, expansions, "budget"
        ledger.consume_candidates(1)
        state, path = q.popleft()
        expansions += 1
        if is_goal(state):
            return path, expansions, "solved"
        for move, nxt in neighbors(state):
            key = keys[nxt.tokens]
            if key not in seen:
                seen.add(key)
                q.append((nxt, path + [move]))
    return None, expansions, "exhausted"
