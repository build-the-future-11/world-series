import numpy as np
import torch
from world_series.wcode.dsl import BinOp,Var,Lit,If
from world_series.wcode.learned import MODES,ProgramScorer,pack_programs,program_pool,public_tensor,structure


def test_semantic_families_are_unique_and_compositions_are_held():
    pool=program_pool()
    assert len(pool)>250
    assert len({r['signature'] for r in pool})==len(pool)
    roles={r['role'] for r in pool}
    assert roles=={'train','selection','evaluation_family','evaluation_composition'}
    assert all(r['role']=='evaluation_composition' for r in pool if r['category'] in {'cubic','conditional'})


def test_batching_and_order_sensitive_structure():
    a=BinOp('-',Var('x'),Lit(2));b=BinOp('-',Lit(2),Var('x'))
    torch.manual_seed(14);m=ProgramScorer()
    whole=m.encode(pack_programs([a,b]))
    separate=torch.cat([m.encode(pack_programs([p])) for p in [a,b]])
    assert torch.allclose(whole,separate,atol=1e-6)
    assert not torch.allclose(whole[0],whole[1])
    _,edges=structure(If(BinOp('<',Var('x'),Lit(0)),Lit(1),Lit(2)))
    assert edges[0] and edges[1] and edges[2] and edges[4] and edges[5]


def test_matched_counts_public_example_permutation_and_gradient():
    counts=[];programs=[BinOp('+',Var('x'),Lit(i)) for i in [-1,0,1]]
    batch=pack_programs(programs);public=public_tensor([[-2,-1],[0,1],[2,3],[3,4]])
    for mode in MODES:
        torch.manual_seed(2);m=ProgramScorer(mode);counts.append(sum(p.numel() for p in m.parameters()))
        logits=m(batch,public)
        assert torch.allclose(logits,m(batch,public.flip(0)),atol=1e-6)
        torch.nn.functional.cross_entropy(logits,torch.tensor([2])).backward()
        assert sum(p.grad.abs().sum().item() for p in m.parameters() if p.grad is not None)>0
    assert len(set(counts))==1


def test_ranker_api_does_not_receive_verifier_targets():
    import inspect
    assert list(inspect.signature(ProgramScorer.forward).parameters)==['self','batch','public']
    pool=program_pool()[:3];batch=pack_programs([r['program'] for r in pool])
    m=ProgramScorer();public=public_tensor([[0,1],[1,2],[2,3],[3,4]])
    before=m(batch,public).detach().clone()
    for row in pool:row['signature']=tuple(np.random.default_rng(1).integers(0,10,17))
    assert torch.equal(before,m(batch,public).detach())
