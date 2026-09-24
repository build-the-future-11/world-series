import copy
import pickle
import numpy as np
import pytest
import torch
from world_series.qapen.causal import CausalLifecycle,FrozenQuantizer


def make(**kw):
    q=FrozenQuantizer.fit(np.random.default_rng(1).normal(size=(80,2)),k=4)
    return CausalLifecycle(q,**kw)


def test_causal_order_and_frozen_codebook():
    m=make();centers=m.quantizer.centers.copy()
    with pytest.raises(RuntimeError):m.observe(1.)
    m.predict([0.,1.])
    with pytest.raises(RuntimeError):m.predict([0.,1.])
    m.observe(2.)
    assert np.array_equal(centers,m.quantizer.centers)
    with pytest.raises(ValueError):m.quantizer.centers[0,0]=123.
    assert m.engrams[0].utility_count==0
    m.predict([0.,1.]);m.observe(2.)
    assert m.engrams[0].utility_count==1


def test_checkpoint_restores_optimizer_pending_rng_and_sleeping_identity():
    m=make(retrieval='random')
    for t in range(20):m.predict([t%3,.2]);m.observe(float(t%4))
    spare=m._spawn([10.,10.],'ACTIVE');m._transition(spare,'SLEEP')
    m.predict([1.,.2]);restored=CausalLifecycle.restore(pickle.loads(pickle.dumps(m.checkpoint())))
    assert m.observe(3.)==restored.observe(3.)
    for t in range(20):
        assert m.predict([t%3,.2])==restored.predict([t%3,.2])
        assert m.observe(float(t%4))==restored.observe(float(t%4))
    assert m.state_receipt()==restored.state_receipt()
    for identity in m.models:
        for a,b in zip(m.models[identity].parameters(),restored.models[identity].parameters()):assert torch.equal(a,b)
        opt=restored.optimizers[identity]
        assert list(opt.param_groups[0]['params'])[0] is next(restored.models[identity].parameters())
    assert spare in restored.models


def test_memory_changes_prediction_with_subsequent_utility():
    m=make(lifecycle=False)
    m.predict([0.,0.]);m.observe(6.)
    without=copy.deepcopy(m);without.memory_enabled=False
    assert m.predict([0.,0.])[0]!=without.predict([0.,0.])[0]
    m.observe(6.);without.observe(6.)
    assert m.engrams[0].utility_count==1


def test_warmup_is_prospective_and_caps_are_enforced():
    m=make(max_active=2,max_identities=4,memory_capacity=3,cooldown=8,warmup=3,sleep_after=4)
    for t in range(50):
        m.predict([float(t//10),0.]);m.observe(float(30 if t%20<10 else -30))
        assert len(m.engrams)<=3 and len(m.models)<=4
        assert sum(v.state in {'ACTIVE','REVIVED'} for v in m.metadata.values())<=2
    assert len(m.models)>1
    for event in m.events:
        if event.get('from')=='WARMUP':
            meta=m.metadata[event['identity']]
            assert event['time']>meta.birth and meta.prospective_count>=3
            if event['to']=='ACTIVE':assert meta.prospective_gain>0
    assert all(e.utility_count<=e.accesses for e in m.engrams)


def test_budget_and_disabled_ablation():
    m=make(lifecycle=False,memory=False,operation_cap=1000)
    for t in range(3):m.predict([0.,0.]);m.observe(100.)
    assert len(m.models)==1 and not m.engrams
    assert m.costs['retrieval_distances']==0
    m.operation_cap=m.operations
    with pytest.raises(RuntimeError,match='budget'):m.predict([0.,0.])


def test_failed_warmup_cannot_revive():
    m=make();identity=m._spawn([100.,100.]);m._transition(identity,'PRUNED')
    m.predict([100.,100.]);m.observe(0.)
    assert m.metadata[identity].state=='PRUNED'
