import torch
from world_series.wfim.learning import CompositionModel


def test_all_encoders_padding_gradients_and_storage():
    tokens=torch.tensor([[0,1,0],[1,0,1]])
    for kind in ["learned_coordinates","identity_coordinates","vector","bilinear","binding"]:
        torch.manual_seed(42)
        model=CompositionModel(kind,degree=3)
        original=model(tokens)
        padded=model(torch.cat([tokens,torch.full((2,2),-1)],dim=1))
        assert torch.equal(original,padded)
        original.square().sum().backward()
        assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters() if p.requires_grad)
        assert model.storage()["total_payload_bytes"]>model.storage()["representation_bytes"]


def test_identical_initial_coordinate_control():
    torch.manual_seed(8);learned=CompositionModel("learned_coordinates",degree=3)
    torch.manual_seed(8);fixed=CompositionModel("identity_coordinates",degree=3)
    tokens=torch.tensor([[0,1,0],[1,0,1]])
    assert torch.equal(learned(tokens),fixed(tokens))
