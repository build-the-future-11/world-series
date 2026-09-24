"""Trainable proposal ranking; scores never constitute proof certificates."""
from dataclasses import dataclass
import numpy as np
from world_series.qwipii.discovery import propose_grammar
from world_series.qwipii.domains import RingState, neighbors
from world_series.qwipii.verifier import complete_domain, verify_automorphism


def proposal_features(goal, act, probes):
    """Public goal plus sampled action behavior, without exhaustive proof labels."""
    if not probes or any(s.goal != goal for s in probes):
        raise ValueError("nonempty probes with the same goal are required")
    images = [tuple(act(s.tokens)) for s in probes]
    moves = changed = 0
    for s, image in zip(probes, images):
        reachable = {t.tokens for _, t in neighbors(RingState(image, goal))}
        changed += image != s.tokens
        for _, nxt in neighbors(s):
            moves += tuple(act(nxt.tokens)) in reachable
    n = len(goal)
    return np.array([1., n / 10., len(set(goal)) / n,
                     float(tuple(act(goal)) == goal),
                     len(set(images)) / len(images), changed / len(probes),
                     moves / (len(probes) * (n + 2))], dtype=np.float64)


@dataclass
class ProposalRanker:
    weights: np.ndarray

    @classmethod
    def fit(cls, features, utilities, ridge=0.01):
        x = np.asarray(features, dtype=np.float64)
        y = np.asarray(utilities, dtype=np.float64)
        if x.ndim != 2 or x.shape[1] != 7 or y.shape != (len(x),) or not len(x):
            raise ValueError("invalid training arrays")
        if ridge <= 0 or not np.isfinite(x).all() or not np.isfinite(y).all():
            raise ValueError("finite data and positive regularization required")
        return cls(np.linalg.solve(x.T @ x + ridge * np.eye(7), x.T @ y))

    def score(self, goal, act, probes):
        return float(proposal_features(goal, act, probes) @ self.weights)

    def to_dict(self):
        return {"version": "sample-behavior-ridge-v1", "weights": self.weights.tolist()}


def certificate_utility(certificate):
    """Training target: fraction of domain eliminated by this single generator."""
    if not certificate["ok"]:
        return 0.0
    mapping = {tuple(a): tuple(b) for a, b in certificate["witness"]["mapping"]}
    unseen = set(mapping)
    orbits = 0
    while unseen:
        t = min(unseen)
        orbits += 1
        while t in unseen:
            unseen.remove(t)
            t = mapping[t]
    return 1 - orbits / len(mapping)


def ranked_certificates(goal, probes, ranker, verification_budget, max_states=10000):
    """Verify only the highest-ranked proposals; rejected candidates consume budget."""
    if verification_budget < 0:
        raise ValueError("negative verification budget")
    grammar = propose_grammar(len(goal))
    ranked = sorted([(ranker.score(goal, act, probes), name, act) for name, act, _ in grammar],
                    key=lambda row: (-row[0], row[1]))
    domain = complete_domain(goal, max_states=max_states)
    attempts, accepted = [], []
    for score, name, act in ranked[:verification_budget]:
        certificate = verify_automorphism(domain, act, fixed_goal=True)
        attempts.append({"name": name, "score": score, "certificate": certificate})
        if certificate["ok"]:
            accepted.append(certificate)
    return accepted, attempts
