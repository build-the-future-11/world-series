from copy import deepcopy
import pytest
from world_series.core.budgets import Budget, BudgetLedger
from world_series.qwipii.verifier import complete_domain, verify_automorphism
from world_series.qwipii.group_actions import dihedral_actions
from world_series.qwipii.search import bfs, certified_quotient_bfs, replay


def ledger():
    return BudgetLedger(Budget(max_candidate_evals=10000))


def test_exhaustive_paths_and_optimality_with_generator_closure():
    domain = complete_domain((0, 1, 0, 1, 0, 1))
    certificates = [verify_automorphism(domain, act, fixed_goal=True)
                    for _, act in dihedral_actions(6)]
    certificates = [c for c in certificates if c["ok"]]
    saved = 0
    for start in domain:
        plain, n, status = bfs(start, ledger())
        path, nq, sq = certified_quotient_bfs(start, ledger(), certificates)
        assert status == sq == "solved"
        assert replay(start, path).tokens == start.goal
        assert len(path) == len(plain)
        saved += n - nq
    assert saved > 0


def test_untrusted_certificate_flags_and_hashes_do_not_authorize_pruning():
    domain = complete_domain((0, 1, 0, 1))
    cert = verify_automorphism(domain, lambda t: t, fixed_goal=True)
    broken = deepcopy(cert)
    broken["witness"]["mapping"][0][1] = [9, 9, 9, 9]
    with pytest.raises(ValueError, match="invalid"):
        certified_quotient_bfs(domain[0], ledger(), [broken])
    equivalence = verify_automorphism(domain, lambda t: t[1:] + t[:1])
    with pytest.raises(ValueError, match="fixed goal"):
        certified_quotient_bfs(domain[0], ledger(), [equivalence])
    assert certified_quotient_bfs(domain[0], ledger(), [cert], max_expansions=0)[2] == "budget"
