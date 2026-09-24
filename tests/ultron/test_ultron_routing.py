from world_series.core.registry import reset_registry_for_tests
from world_series.ultron.capabilities import bootstrap_adapters, available_ops
from world_series.ultron.train_router import LinearRouter
from world_series.ultron.router import static_route
from world_series.ultron.state import EpisodeState


def test_learned_and_unsupported():
    reset_registry_for_tests()
    bootstrap_adapters()
    avail = available_ops()
    assert "identify_dynamical_law" in avail
    r = LinearRouter.from_oracle_traces(
        [{"task_type": "law_id", "best_op": "identify_dynamical_law"}]
    )
    assert r.score("law_id", "identify_dynamical_law") > r.score("law_id", "solve_invariant_problem")
    assert r.choose("law_id", avail) == "identify_dynamical_law"
    assert static_route(EpisodeState("g", "nope", (), tuple(avail), 1), avail) is None
