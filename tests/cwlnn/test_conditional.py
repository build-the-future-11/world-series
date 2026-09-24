import pytest
import torch

from world_series.cwlnn.conditional import (
    ConditionalWorld, SparseWorld, batch_graphs, coarse_edges, mean_aggregate,
    permute, pool, select,
)


def graph(n=12):
    generator = torch.Generator().manual_seed(31)
    a = torch.arange(max(n-1,0))
    edges = torch.stack([torch.cat([a, a+1]), torch.cat([a+1, a])]) if n else torch.empty((2,0),dtype=torch.long)
    return SparseWorld(torch.randn(n,4,generator=generator,dtype=torch.float64), edges,
                       torch.arange(n)//2, torch.zeros(n,dtype=torch.long), torch.arange(n))


def test_sparse_matches_dense_and_actual_quotient():
    g = graph()
    dense = torch.zeros(12,12,dtype=torch.float64)
    dense[g.edges[1],g.edges[0]] = 1
    dense /= dense.sum(1).clamp_min(1)[:,None]
    assert torch.allclose(mean_aggregate(g.x,g.edges),dense@g.x)
    assert torch.allclose(pool(g.x,g.parent),g.x.reshape(6,2,4).mean(1))
    arbitrary = torch.tensor([[0,1,2,4],[4,0,5,2]])
    quotient = coarse_edges(arbitrary,g.parent)
    assert set(map(tuple,quotient.T.tolist())) == {(0,2),(1,2),(2,1)}


def test_boundary_integrity():
    g = batch_graphs([graph(8),graph(6)])
    g.validate()
    model = ConditionalWorld(routing='learned').double().eval()
    separate = torch.cat([model(graph(8),.5)[0],model(graph(6),.5)[0]])
    combined, receipt = model(g,.5)
    assert torch.allclose(combined,separate,atol=1e-12)
    assert receipt['budgets'] == [4,3]
    g.edges[0,0] = 9
    with pytest.raises(ValueError,match='Cross-graph'): g.validate()
    g = batch_graphs([graph(8),graph(6)])
    g.parent[8] = 0
    with pytest.raises(ValueError,match='Parent crosses'): g.validate()


def test_exact_refinement_cap_and_disabled_routing_equivalence():
    torch.manual_seed(7)
    full = ConditionalWorld().double().eval()
    torch.manual_seed(7)
    routed = ConditionalWorld(routing='learned').double().eval()
    g = graph()
    actual = []
    hook = routed.refine.register_forward_pre_hook(lambda module,args: actual.append(len(args[0])))
    for fraction,count in [(0.,0),(.25,3),(.5,6),(1.,12)]:
        before = len(actual)
        output, receipt = routed(g,fraction)
        assert receipt['refine_rows'] == count
        assert (len(actual)==before if count==0 else actual[-1]==count)
    hook.remove()
    assert torch.allclose(output,full(g)[0],atol=1e-12)


def test_permutation_and_tied_priority_are_structurally_consistent():
    g = graph()
    order = torch.randperm(12,generator=torch.Generator().manual_seed(2))
    for mode in ('learned','norm','random'):
        model = ConditionalWorld(routing=mode).double().eval()
        before,_ = model(g,.5)
        after,_ = model(permute(g,order),.5)
        assert torch.allclose(after,before[order],atol=1e-12)
    selected,_ = select(torch.zeros(12),g.batch,g.node_id,.25)
    changed,_ = select(torch.zeros(12),g.batch[order],g.node_id[order],.25)
    assert torch.equal(g.node_id[selected],g.node_id[order][changed])


def test_selected_surrogate_has_router_and_backbone_gradients():
    torch.manual_seed(3)
    model = ConditionalWorld(routing='learned').double().train()
    output,_ = model(graph(),.5)
    output.square().mean().backward()
    for module in (model.router,model.encoder,model.refine):
        assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in module.parameters())
        assert sum(p.grad.abs().sum().item() for p in module.parameters()) > 0


def test_empty_singleton_and_attention_bound():
    for n in (0,1):
        for context in ('hierarchy','flat5','local','attention'):
            output,receipt = ConditionalWorld(context,routing='learned').double().eval()(graph(n),.5)
            assert output.shape == (n,) and torch.isfinite(output).all()
            assert receipt['selected'] == 0
    with pytest.raises(ValueError,match='size limit'):
        ConditionalWorld('attention',attention_limit=10).double()(graph(12))


def test_large_sparse_path_has_no_quadratic_attention_or_hidden_refinement():
    model = ConditionalWorld(routing='learned').double().eval()
    with torch.no_grad():
        _,receipt = model(graph(10000),.01)
    assert receipt['refine_rows'] == 100
    assert receipt['attention_pairs'] == 0
    assert receipt['fine_edges'] == 19998
    assert receipt['coarse_edges'] == 9998
