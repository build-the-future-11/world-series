import numpy as np
from world_series.qwipii.discovery import propose_grammar
from world_series.qwipii.verifier import complete_domain, verify_automorphism
from world_series.qwipii.learned_discovery import (
    ProposalRanker, proposal_features, certificate_utility, ranked_certificates)


def test_training_changes_scores_and_verification_remains_mandatory():
    goal = (0, 1, 0, 1)
    domain = complete_domain(goal)
    x, y = [], []
    for _, act, _ in propose_grammar(len(goal)):
        x.append(proposal_features(goal, act, domain[:2]))
        y.append(certificate_utility(verify_automorphism(domain, act, fixed_goal=True)))
    model = ProposalRanker.fit(x, y)
    assert np.linalg.norm(model.weights) > 0
    assert np.mean((np.asarray(x) @ model.weights - y) ** 2) < np.mean(np.asarray(y) ** 2)
    accepted, attempts = ranked_certificates(goal, domain[:2], model, 3)
    assert len(attempts) == 3 and accepted
    assert all(c["complete_domain"] and c["witness"]["scope"] == "fixed_goal" for c in accepted)
    assert ranked_certificates(goal, domain[:2], model, 0) == ([], [])


def test_arbitrary_high_scores_cannot_bypass_verification():
    class AdversarialRanker:
        def score(self, goal, act, probes):
            return 1000.0
    domain = complete_domain((0, 1, 2, 3))
    accepted, attempts = ranked_certificates(domain[0].goal, domain[:1], AdversarialRanker(), 100)
    bad = next(a for a in attempts if a["name"] == "sort_suffix")
    assert not bad["certificate"]["ok"]
    assert all(c["witness"]["goal"] == c["witness"]["target_goal"] for c in accepted)
