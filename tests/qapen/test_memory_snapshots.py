"""Causal memory and frozen codebooks retain their creation-time values."""

import copy

import numpy as np
import pytest

from world_series.qapen.causal import CausalLifecycle, FrozenQuantizer
from world_series.qapen.memory import EngramStore


def test_memory_write_does_not_alias_callers_context():
    context = np.array([1.0, 2.0])
    memory = EngramStore()
    memory.write(context, 3.0)
    context[:] = 99
    np.testing.assert_array_equal(memory.keys[0], [1, 2])


def test_stored_key_cannot_be_made_writeable():
    memory = EngramStore()
    memory.write(np.array([1.0]), 2.0)
    with pytest.raises(ValueError):
        memory.keys[0].setflags(write=True)


def test_zero_recent_count_is_empty_not_the_entire_history():
    memory = EngramStore()
    memory.write(np.array([1.0]), 2.0)
    assert memory.recent(0) == []


@pytest.mark.parametrize("capacity", [0, -1, 1.5, True])
def test_invalid_capacity_is_rejected_before_any_write(capacity):
    with pytest.raises(ValueError, match="capacity"):
        EngramStore(capacity=capacity)


def test_rejected_write_never_evicts_the_existing_memory():
    memory = EngramStore(capacity=1)
    memory.write(np.array([1.0]), 2.0)
    with pytest.raises(ValueError):
        memory.write(np.array([np.nan]), 3.0)
    np.testing.assert_array_equal(memory.keys[0], [1])
    assert memory.values == [2.0]


def test_quantizer_centers_cannot_be_made_writeable():
    quantizer = FrozenQuantizer([[0.0], [2.0]])
    with pytest.raises(ValueError):
        quantizer.centers.setflags(write=True)


def test_quantizer_codebook_cannot_be_reassigned():
    quantizer = FrozenQuantizer([[0.0], [2.0]])
    with pytest.raises(AttributeError):
        quantizer.centers = np.array([[99.0], [100.0]])


def test_deepcopy_and_lifecycle_restore_preserve_codebook_freeze():
    original = FrozenQuantizer([[0.0], [2.0]])
    lifecycle = CausalLifecycle(original, lifecycle=False, memory=False)
    restored = CausalLifecycle.restore(lifecycle.checkpoint())
    for quantizer in [copy.deepcopy(original), restored.quantizer]:
        with pytest.raises(ValueError):
            quantizer.centers.setflags(write=True)
        assert quantizer.encode(np.array([1.75]))[0] == 1


def test_bounded_fifo_retains_original_key_and_value_pairs():
    memory = EngramStore(capacity=2)
    for value in [1.0, 2.0, 3.0]:
        memory.write(np.array([value]), value*10)
    assert [key.item() for key in memory.keys] == [2, 3]
    assert memory.recent(1) == [30]
