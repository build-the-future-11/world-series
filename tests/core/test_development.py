import itertools
import numpy as np
import pytest
from world_series.core.budgets import Budget, BudgetLedger
from world_series.qwipii.domains import RingState
from world_series.qwipii.search import bfs, quotient_bfs, replay
from world_series.evaluation.development import ContextMemory, full_rollout_error, aggregate


def test_quotient_replays_every_small_permutation_and_obeys_cap():
    for n in [3, 4]:
        for tokens in itertools.permutations(range(n)):
            start=RingState(tokens,tuple(range(n)))
            b,_,bs=bfs(start,BudgetLedger(Budget()),100)
            q,_,qs=quotient_bfs(start,BudgetLedger(Budget()),100)
            assert bs==qs=='solved'
            assert replay(start,q).tokens==start.goal
            assert len(q)==len(b)
    ledger=BudgetLedger(Budget(max_candidate_evals=1))
    _,used,status=quotient_bfs(RingState((3,2,1,0),(0,1,2,3)),ledger,1)
    assert used==ledger.candidate_evals==1 and status=='budget'


def test_rankers_do_not_execute_unbudgeted_candidates(monkeypatch):
    from world_series.wcode import interpreter
    from world_series.wcode.encoder import score_candidate
    from world_series.wcode.dsl import Var
    def forbidden(*args,**kwargs): raise AssertionError('unbudgeted execution')
    monkeypatch.setattr(interpreter,'interpret',forbidden)
    for mode in ['uniform','length','token','flat','hierarchical']:
        score_candidate(Var('x'),[({'x':3},4)],mode)


def test_context_memory_is_causal_and_reads_are_an_actual_intervention():
    memory=ContextMemory(5); no=ContextMemory(5,memory=False)
    predictions=[]
    for y in np.sin(np.arange(60)):
        predictions.append((memory.predict(),no.predict()))
        memory.update(float(y));no.update(float(y))
    assert memory.reads>0 and no.reads==0
    assert any(a!=b for a,b in predictions[6:])
    assert len(memory.keys)==60


def test_rollout_does_not_drop_nonlinear_terms():
    from world_series.wpinn.systems import make_trajectory
    held=make_trajectory(7,2.,.3)
    correct=full_rollout_error(held,{'q':-2.,'v':-.3})
    wrong=full_rollout_error(held,{'q':-2.,'v':-.3,'q2':.1})
    assert correct<1e-10 and wrong>correct*100


def test_failed_row_invalidates_aggregate():
    result=aggregate([{'method':'a','value':1.},{'method':'a','value':None}])[0]
    assert result['mean'] is None and result['attempted']==2 and result['failures']==1


def test_real_topk_counterexample(tmp_path):
    from world_series.wfim.evaluate import run_experiment
    from world_series.evaluation.runner import create_run
    cfg={'project':'wfim','experiment':'test','split':'dev','device':'cpu','seed':1,'budget':{}}
    result=run_experiment(cfg,create_run(tmp_path,cfg))
    assert result['topk_counterexample_triggered']
