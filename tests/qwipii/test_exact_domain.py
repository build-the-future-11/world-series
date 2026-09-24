import pytest
from world_series.qwipii.domains import RingState
from world_series.qwipii.verifier import complete_domain, verify_automorphism
from world_series.qwipii.group_actions import rotate_tokens


def test_incomplete_and_duplicate_domains_cannot_certify():
    domain = complete_domain((0, 1, 2))
    identity = lambda t: t
    assert verify_automorphism([], identity)["reason"] == "empty_domain"
    assert verify_automorphism(domain[:-1], identity)["reason"] == "incomplete_domain"
    assert verify_automorphism(domain + domain[:1], identity)["reason"] == "duplicate_states"
    assert verify_automorphism(domain, identity)["complete_domain"]


def test_problem_equivalence_is_not_fixed_goal_symmetry():
    domain = complete_domain((0, 1, 2))
    rotate = lambda t: rotate_tokens(t, 1)
    cert = verify_automorphism(domain, rotate)
    assert cert["ok"] and cert["checked_states"] == 6
    assert cert["checked_edges"] == 30
    assert cert["witness"]["scope"] == "simultaneous_problem_equivalence"
    assert verify_automorphism(domain, rotate, fixed_goal=True)["reason"] == "goal_not_fixed"
    repeated = complete_domain((0, 1, 0, 1))
    assert verify_automorphism(repeated, lambda t: rotate_tokens(t, 2), fixed_goal=True)["ok"]


def test_hidden_bad_state_is_rejected():
    domain = complete_domain((0, 1, 2, 3))
    bad = domain[-1].tokens
    transform = lambda t: domain[0].tokens if t == bad else t
    assert all(transform(s.tokens) == s.tokens for s in domain[:3])
    assert verify_automorphism(domain, transform)["reason"] == "not_bijective"


def test_bijection_without_graph_preservation_is_rejected():
    domain = complete_domain((0, 1, 2, 3))
    a, b = domain[1].tokens, domain[-1].tokens
    transform = lambda t: b if t == a else a if t == b else t
    assert verify_automorphism(domain, transform)["reason"] == "transition_not_preserved"


def test_multiset_enumeration_and_preallocation_cap():
    assert len(complete_domain((0, 0, 1, 1))) == 6
    with pytest.raises(ValueError, match="cap"):
        complete_domain(tuple(range(12)), max_states=100)
