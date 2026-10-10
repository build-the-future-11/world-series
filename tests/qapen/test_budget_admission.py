"""Exact transition budgets preserve causal state at a rejected retry boundary."""

import copy
import json

import numpy as np
import pytest
import torch

from world_series.qapen.causal import CausalLifecycle, FrozenQuantizer


def model(**kwargs):
    return CausalLifecycle(FrozenQuantizer(np.array([[0.], [4.]])),
                           max_active=2, max_identities=4, cooldown=1,
                           memory_capacity=2, **kwargs)


def warm_model(**kwargs):
    value = model(**kwargs)
    for context, target in [([0.], .1), ([1.], .2), ([0.], .3)]:
        value.predict(context)
        value.observe(target)
    return value


def snapshot(value):
    return copy.deepcopy({
        'receipt': value.state_receipt(),
        'pending': value.pending,
        'replay': list(value.replay),
        'models': {key: module.state_dict() for key, module in value.models.items()},
        'optimizers': {key: opt.state_dict() for key, opt in value.optimizers.items()},
        'counters': (value.next_identity, value.next_engram, value.last_birth, value.surprise_streak),
    })


def identical(left, right):
    if isinstance(left, torch.Tensor):
        assert torch.equal(left, right)
    elif isinstance(left, np.ndarray):
        np.testing.assert_array_equal(left, right)
    elif isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            identical(left[key], right[key])
    elif isinstance(left, (list, tuple)):
        assert len(left) == len(right)
        for x, y in zip(left, right, strict=True):
            identical(x, y)
    else:
        assert left == right


@pytest.mark.parametrize('scenario', ['initial', 'memory-random-warm', 'revival'])
def test_rejected_prediction_preserves_state_and_exact_budget_can_retry(scenario):
    value = model(lifecycle=False, memory=False)
    context = [0.]
    if scenario == 'memory-random-warm':
        value = warm_model(retrieval='random')
        identity = value._spawn([0.])
        value.metadata[identity].birth = value.t - 1
    elif scenario == 'revival':
        value = model()
        identity = value._spawn([4.])
        value._transition(identity, 'ACTIVE')
        value._transition(identity, 'SLEEP')
        context = [4.]
    reference = value.checkpoint()
    result = reference.predict(context)
    cost = reference.operations - value.operations
    value.operation_cap = value.operations + cost - 1
    before = snapshot(value)
    with pytest.raises(RuntimeError, match='Operation budget exhausted'):
        value.predict(context)
    identical(snapshot(value), before)
    value.operation_cap += 1
    assert value.predict(context) == result
    identical(snapshot(value), snapshot(reference))
    assert value.operations == value.operation_cap


@pytest.mark.parametrize('scenario', ['memory-utility', 'warm-update', 'promotion', 'birth-replay'])
def test_rejected_observation_preserves_state_and_exact_budget_can_retry(scenario):
    value = warm_model(warmup=2)
    target = .4
    if scenario in {'warm-update', 'promotion'}:
        identity = value._spawn([0.])
        value.metadata[identity].birth = value.t - 1
        if scenario == 'promotion':
            value.metadata[identity].prospective_count = 1
            value.metadata[identity].prospective_gain = 100.
    if scenario == 'birth-replay':
        value.surprise_streak = 2
        target = 20.
    value.predict([0.])
    reference = value.checkpoint()
    result = reference.observe(target)
    cost = reference.operations - value.operations
    value.operation_cap = value.operations + cost - 1
    before = snapshot(value)
    with pytest.raises(RuntimeError, match='Operation budget exhausted'):
        value.observe(target)
    identical(snapshot(value), before)
    value.operation_cap += 1
    assert value.observe(target) == result
    identical(snapshot(value), snapshot(reference))
    assert value.operations == value.operation_cap


@pytest.mark.parametrize('context', [[1., 2.], [float('nan')]])
def test_invalid_context_does_not_consume_the_next_prediction_budget(context):
    value = model()
    before = snapshot(value)
    with pytest.raises(ValueError, match='Invalid context'):
        value.predict(context)
    identical(snapshot(value), before)


@pytest.mark.parametrize('retrieval', ['nearest', 'random', 'recent'])
def test_repeated_budget_refusals_do_not_change_a_complete_causal_trace(retrieval):
    value = model(retrieval=retrieval, warmup=2, sleep_after=2)
    reference = value.checkpoint()
    contexts = [[0.], [4.], [1.], [3.]] * 4
    targets = [8., -8., 8., 0.] * 4
    outputs = []
    for context, target in zip(contexts, targets, strict=True):
        expected_prediction = reference.predict(context)
        needed = reference.operations - value.operations
        value.operation_cap = value.operations + needed - 1
        before = snapshot(value)
        with pytest.raises(RuntimeError, match='Operation budget exhausted'):
            value.predict(context)
        identical(snapshot(value), before)
        value.operation_cap += 1
        assert value.predict(context) == expected_prediction
        expected = reference.observe(target)
        needed = reference.operations - value.operations
        value.operation_cap = value.operations + needed - 1
        before = snapshot(value)
        with pytest.raises(RuntimeError, match='Operation budget exhausted'):
            value.observe(target)
        identical(snapshot(value), before)
        value.operation_cap += 1
        actual = value.observe(target)
        assert actual == expected
        outputs.append(actual)
        identical(snapshot(value), snapshot(reference))
    # The trace goes through real SGD, delayed memory utility and expert birth.
    assert value.t == 16
    assert value.next_identity > 1
    assert any(entry['memory_id'] is not None for entry in outputs)
    json.dumps(outputs, allow_nan=False)
