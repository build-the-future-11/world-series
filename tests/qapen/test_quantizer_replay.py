"""Codebook metadata and serialized state cannot change causal routing."""

import pickle

import numpy as np
import pytest
import torch

from world_series.qapen.causal import CausalLifecycle, FrozenQuantizer


@pytest.mark.parametrize("attribute", ["shape", "dtype"])
@pytest.mark.parametrize("exposed_part", ["array", "base"])
def test_exposed_array_metadata_does_not_change_codebook(attribute, exposed_part):
    quantizer = FrozenQuantizer([[0.0], [2.0]])
    label, features = quantizer.encode([1.75])
    exposed = quantizer.centers
    if exposed_part == "base":
        exposed = exposed.base
    if attribute == "shape":
        exposed.shape = (1, 2)
    else:
        exposed.dtype = np.int64
    assert quantizer.centers.shape == (2, 1)
    assert quantizer.centers.dtype == np.dtype(np.float64)
    actual_label, actual_features = quantizer.encode([1.75])
    assert actual_label == label == 1
    np.testing.assert_array_equal(actual_features, features)


@pytest.mark.parametrize("protocol", [4, 5])
def test_pickle_roundtrip_retains_immutable_codebook(protocol):
    original = FrozenQuantizer([[0.0], [2.0]])
    restored = pickle.loads(pickle.dumps(original, protocol=protocol))
    with pytest.raises(ValueError):
        restored.centers.setflags(write=True)
    assert restored.encode([1.75])[0] == 1
    np.testing.assert_array_equal(restored.centers, original.centers)


@pytest.mark.parametrize("state_key", ["centers", "_centers"])
@pytest.mark.parametrize("protocol", [4, 5])
def test_legacy_array_state_is_loaded_and_refrozen(monkeypatch, state_key, protocol):
    quantizer = FrozenQuantizer([[0.0], [2.0]])
    legacy_centers = quantizer.centers.copy()
    legacy_centers.setflags(write=False)
    # Construct the two state layouts produced by earlier implementations;
    # this is a locally generated fixture, not a historical outcome checkpoint.
    with monkeypatch.context() as patch:
        patch.setattr(
            FrozenQuantizer,
            "__getstate__",
            lambda self: {state_key: legacy_centers},
            raising=False,
        )
        payload = pickle.dumps(quantizer, protocol=protocol)
    restored = pickle.loads(payload)
    assert restored.encode([1.75])[0] == 1
    with pytest.raises(ValueError):
        restored.centers.setflags(write=True)


@pytest.mark.parametrize("centers", [[[np.nan], [2.0]], [0.0, 2.0]])
def test_invalid_legacy_codebook_state_is_rejected(monkeypatch, centers):
    quantizer = FrozenQuantizer([[0.0], [2.0]])
    with monkeypatch.context() as patch:
        patch.setattr(
            FrozenQuantizer,
            "__getstate__",
            lambda self: {"centers": np.asarray(centers)},
            raising=False,
        )
        payload = pickle.dumps(quantizer, protocol=4)
    with pytest.raises(ValueError, match="centers"):
        pickle.loads(payload)


@pytest.mark.parametrize("attribute", ["shape", "dtype"])
def test_pending_checkpoint_replay_survives_exposed_metadata_changes(attribute):
    original = CausalLifecycle(
        FrozenQuantizer([[0.0], [2.0]]), lifecycle=False, retrieval="random"
    )
    for context, target in [(0.0, 0.5), (2.0, 1.5), (1.0, -0.5)]:
        original.predict([context])
        original.observe(target)
    original.predict([1.75])
    checkpoint = original.checkpoint()
    exposed = checkpoint.quantizer.centers
    if attribute == "shape":
        exposed.shape = (1, 2)
    else:
        exposed.dtype = np.int64
    restored = CausalLifecycle.restore(pickle.loads(pickle.dumps(checkpoint)))
    assert original.observe(1.0) == restored.observe(1.0)
    for context, target in [(1.75, 1.25), (0.25, -0.25), (1.0, 0.5)]:
        assert original.predict([context]) == restored.predict([context])
        assert original.observe(target) == restored.observe(target)
    assert original.state_receipt() == restored.state_receipt()
    for identity in original.models:
        for left, right in zip(
            original.models[identity].parameters(), restored.models[identity].parameters()
        ):
            assert torch.equal(left, right)
        optimizer = restored.optimizers[identity]
        assert optimizer.param_groups[0]["params"][0] is next(
            restored.models[identity].parameters()
        )
