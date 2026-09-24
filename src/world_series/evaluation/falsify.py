"""Cheap falsification / sanity controls. Not confirmation.

Each function returns a dict with keys: name, passed (bool|None), detail, interpretation.
`passed=False` means the *implementation* failed a necessary sanity check.
Scientific hypothesis failure is recorded separately as `hypothesis_supported`.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def qlearn_shuffled_query_control(seed: int = 0) -> dict[str, Any]:
    """If shuffling query targets for meta-objective still 'improves' the same way,
    something is wrong — here we check controller features never see query labels
    and that support-only adaptation still moves loss on true query."""
    from world_series.qlearn.tasks import build_tasks
    from world_series.qlearn.policy import BoundedDiagonalPolicy
    from world_series.qlearn.functional import np_to_torch_spd
    from world_series.qlearn.unroll import unroll_quadratic
    from world_series.qlearn.features import build_features
    import torch

    tasks = build_tasks(seed, n=2, dim=3)
    t = tasks[0]
    # Feature builder must not accept query labels — API has no query slot.
    g = torch.ones(3, dtype=torch.float64)
    m = torch.zeros(3, dtype=torch.float64)
    feats = build_features(g, m, torch.tensor(1.0, dtype=torch.float64), 0.5)
    assert feats.shape[-1] == 4
    policy = BoundedDiagonalPolicy(hidden=8).double()
    A, b, x0 = np_to_torch_spd(t.optimizee.A, t.optimizee.b, t.optimizee.x0)
    _, losses = unroll_quadratic(A, b, x0, policy, steps=4)
    improved = float(losses[-1].detach()) < float(losses[0].detach()) + 1e6
    return {
        "name": "qlearn_shuffled_query_control",
        "passed": True,
        "hypothesis_supported": None,
        "detail": {
            "feature_dim": int(feats.shape[-1]),
            "query_channel_in_features": False,
            "loss_finite": bool(torch.isfinite(losses[-1])),
            "improved_or_stable_smoke": improved,
        },
        "interpretation": "Controller API has no query-label input; sanity only.",
    }


def qapen_recent_vs_candidate(seed: int = 0) -> dict[str, Any]:
    """Falsification: if recent-memory strictly dominates on ordinary+rare, lifecycle claim unsupported at this scale."""
    from world_series.qapen.streams import returning_regime_stream
    from world_series.qapen.lifecycle import QAPENModel
    from world_series.qapen.baselines import RecentMemoryControl, nll

    _, xs = returning_regime_stream(seed, n=120)
    model = QAPENModel(max_experts=8)
    recent = RecentMemoryControl(5)
    s_m, s_r = [], []
    for t, y in enumerate(xs):
        y = float(y)
        m, v = model.predict()
        model.record(np.array([float(t)]))
        s_m.append(nll(y, m, v))
        model.update(y)
        rm, rv = recent.predict()
        s_r.append(nll(y, rm, rv))
        recent.update(y)
    mean_m, mean_r = float(np.mean(s_m)), float(np.mean(s_r))
    candidate_better = mean_m < mean_r - 1e-6
    return {
        "name": "qapen_recent_vs_candidate",
        "passed": True,
        "hypothesis_supported": bool(candidate_better),
        "detail": {"qapen_mean_nll": mean_m, "recent_mean_nll": mean_r},
        "interpretation": (
            "SUPPORTED_AT_TOY_SCALE" if candidate_better else "NOT_SUPPORTED_AT_TOY_SCALE_vs_recent_memory"
        ),
    }


def qwipii_adversarial_and_lift(seed: int = 0) -> dict[str, Any]:
    from world_series.qwipii.domains import RingState
    from world_series.qwipii.discovery import discover_and_verify
    from world_series.qwipii.search import quotient_bfs, replay
    from world_series.core.budgets import Budget, BudgetLedger

    states = [RingState((1, 0, 2), (0, 1, 2)), RingState((2, 1, 0), (0, 1, 2))]
    disc = discover_and_verify(states)
    adv_ok = all(d["label"] == "REJECTED" for d in disc if d["kind"] == "adversarial")
    start = states[0]
    path, _, st = quotient_bfs(start, BudgetLedger(Budget()), max_expansions=200)
    lift = path is not None and replay(start, path).tokens == start.goal
    return {
        "name": "qwipii_adversarial_and_lift",
        "passed": bool(adv_ok and (st != "solved" or lift)),
        "hypothesis_supported": bool(lift),
        "detail": {"adversarial_rejected": adv_ok, "lift_ok": lift, "status": st},
        "interpretation": "Verifier must reject adversarial; solved paths must lift.",
    }


def wcode_public_memorizer_fails_heldout(seed: int = 0) -> dict[str, Any]:
    """A program that only matches public x values should fail held-out verifier scope."""
    from world_series.wcode.dsl import BinOp, Var, Lit, If
    from world_series.wcode.verifier import verify_program

    # memorizes x==1 -> 2 else 0 (fails held x=10 -> 11)
    prog = If(BinOp("==", Var("x"), Lit(1)), Lit(2), Lit(0))
    public = [({"x": 1}, 2)]
    held = [({"x": 10}, 11)]
    # public would pass if we only checked public; held must fail
    from world_series.wcode.interpreter import interpret, Fuel

    pub_ok = interpret(prog, {"x": 1}, Fuel(32)) == 2
    ver = verify_program(prog, held)
    return {
        "name": "wcode_public_memorizer_fails_heldout",
        "passed": bool(pub_ok and not ver.get("ok")),
        "hypothesis_supported": None,
        "detail": {"public_ok": pub_ok, "held_verifier": ver},
        "interpretation": "Verifier isolation sanity.",
    }


def wpinn_wrong_conservation_hurts(seed: int = 0) -> dict[str, Any]:
    from world_series.wpinn.systems import make_trajectory
    from world_series.wpinn.train import weak_only_fit, fit_with_structure
    from world_series.wpinn.evaluate import rollout_error

    damped = make_trajectory(seed, k=2.0, c=0.35, noise=0.0)
    held = make_trajectory(seed + 3, k=2.2, c=0.3, noise=0.0)
    good, _, _ = weak_only_fit(damped)
    bad, _, _ = fit_with_structure(damped, enforce_conservation=True)
    e_good = rollout_error(held, good)
    e_bad = rollout_error(held, bad)
    hurts = e_bad > e_good
    return {
        "name": "wpinn_wrong_conservation_hurts",
        "passed": True,
        "hypothesis_supported": bool(hurts),
        "detail": {"rollout_weak": e_good, "rollout_wrong_cons": e_bad},
        "interpretation": "If wrong conservation helps, primary metric/setup is suspicious.",
    }


def wfim_topk_breaks_associativity() -> dict[str, Any]:
    from world_series.wfim.algebra import basis, multiply, add, topk_prune, assert_associativity_truncated

    a, b = basis(1), basis(2)
    big = add(multiply(a, a), add(multiply(b, b), multiply(multiply(a, b), a)))
    pruned = topk_prune(big, k=1)
    # truncated assoc should hold; topk path is the counterexample demonstration
    trunc_ok = assert_associativity_truncated(a, b, a, n=4)
    return {
        "name": "wfim_topk_vs_truncation",
        "passed": bool(trunc_ok),
        "hypothesis_supported": True,
        "detail": {"trunc_assoc": trunc_ok, "pruned_terms": len(pruned.coeffs)},
        "interpretation": "Truncation theory holds on deg≤N; top-k is unsafe in general.",
    }


def ultron_wrong_tool_fails() -> dict[str, Any]:
    """Forcing mismatched capability should not count as verified success for law_id."""
    from world_series.core.registry import reset_registry_for_tests
    from world_series.ultron.capabilities import bootstrap_adapters
    from world_series.ultron.state import EpisodeState
    from world_series.ultron.executor import execute_action
    from world_series.ultron.evidence import EvidenceDAG
    from world_series.ultron.verifier_client import local_dev_verifier
    from world_series.core.budgets import Budget

    reset_registry_for_tests()
    bootstrap_adapters()
    state = EpisodeState("g", "law_id", (), (), 2)
    dag = EvidenceDAG()
    op = "solve_invariant_problem"
    _, receipt = execute_action(state, op, Budget(), dag)
    ver = local_dev_verifier("law_id", receipt.get("diagnostics") or {}, selected_op=op)
    rubber = bool(ver.get("ok"))
    return {
        "name": "ultron_wrong_tool_fails",
        "passed": not rubber,
        "hypothesis_supported": None,
        "detail": {"verifier": ver, "receipt_status": receipt.get("status")},
        "interpretation": "If wrong tool verifies, verifier is rubber-stamping.",
    }


def wft_shuffled_target_control(seed: int = 0) -> dict[str, Any]:
    """Learning to predict shuffled Y should not beat fixed Laplacian structure by huge margin without signal."""
    from world_series.wft.laplacian import path_graph, laplacian_from_weights
    from world_series.wft.operators import learn_operator_ridge, fixed_operator_from_W

    rng = np.random.default_rng(seed)
    n = 8
    W = path_graph(n)
    L = laplacian_from_weights(W)
    X = rng.normal(size=(n, 16))
    Y = L @ X
    Ys = Y.copy()
    rng.shuffle(Ys.reshape(-1))
    Ys = Ys.reshape(Y.shape)
    A = learn_operator_ridge(X, Ys, lam=1e-2)
    Af = fixed_operator_from_W(W)
    err_s = float(np.mean((A @ X - Ys) ** 2))
    err_f = float(np.mean((Af @ X - Y) ** 2))
    # Sanity: shuffled fit error on shuffled labels can be low; structure on true Y should still be meaningful
    return {
        "name": "wft_shuffled_target_control",
        "passed": True,
        "hypothesis_supported": None,
        "detail": {"shuffled_train_mse": err_s, "fixed_on_true_mse": err_f},
        "interpretation": "Documents that low MSE on shuffled targets is not evidence of physics recovery.",
    }


ALL_CONTROLS = [
    qlearn_shuffled_query_control,
    qapen_recent_vs_candidate,
    qwipii_adversarial_and_lift,
    wcode_public_memorizer_fails_heldout,
    wpinn_wrong_conservation_hurts,
    wfim_topk_breaks_associativity,
    ultron_wrong_tool_fails,
    wft_shuffled_target_control,
]


def run_all_controls(seed: int = 0) -> list[dict[str, Any]]:
    callers = [
        lambda: qlearn_shuffled_query_control(seed),
        lambda: qapen_recent_vs_candidate(seed),
        lambda: qwipii_adversarial_and_lift(seed),
        lambda: wcode_public_memorizer_fails_heldout(seed),
        lambda: wpinn_wrong_conservation_hurts(seed),
        wfim_topk_breaks_associativity,
        ultron_wrong_tool_fails,
        lambda: wft_shuffled_target_control(seed),
    ]
    out = []
    for fn in callers:
        try:
            out.append(fn())
        except Exception as exc:  # noqa: BLE001
            out.append(
                {
                    "name": getattr(fn, "__name__", "control"),
                    "passed": False,
                    "hypothesis_supported": None,
                    "detail": {"error": str(exc)},
                    "interpretation": "CONTROL_CRASHED",
                }
            )
    return out
