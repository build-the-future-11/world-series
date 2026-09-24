"""Matched-output sequence encoders for the bounded coordinate experiment."""
import torch
from torch import nn
from world_series.wfim.coordinates import WordCoordinates


class CompositionModel(nn.Module):
    def __init__(self, kind, degree=6, width=32):
        super().__init__()
        self.kind=kind
        dimension=2**(degree+1)-1
        self.dimension=dimension
        if kind in ("learned_coordinates","identity_coordinates"):
            self.algebra=WordCoordinates(2,degree)
            self.algebra.theta.requires_grad_(kind=="learned_coordinates")
        elif kind=="vector":
            self.embedding=nn.Embedding(2,dimension,dtype=torch.float64)
            self.recurrent=nn.Linear(dimension,dimension,dtype=torch.float64)
        elif kind=="bilinear":
            self.embedding=nn.Embedding(2,dimension,dtype=torch.float64)
            self.recurrent=nn.Linear(dimension,dimension,dtype=torch.float64)
            self.interaction=nn.Parameter(torch.ones(dimension,dtype=torch.float64))
        elif kind=="binding":
            self.register_buffer("symbols",torch.randint(0,2,(2,dimension),dtype=torch.int64).double()*2-1)
        else: raise ValueError(kind)
        self.decoder=nn.Sequential(nn.Linear(dimension,width,dtype=torch.float64),nn.Tanh(),nn.Linear(width,1,dtype=torch.float64))

    def encode(self,tokens):
        if tokens.ndim!=2 or bool(((tokens < -1)|(tokens>1)).any()): raise ValueError("invalid tokens")
        batch,length=tokens.shape
        if hasattr(self,"algebra"):
            h=self.algebra.theta.new_zeros((batch,self.dimension));h[:,0]=1
            for i in range(length):
                active=tokens[:,i]>=0
                factor=torch.zeros_like(h);factor[:,0]=0.5
                factor[torch.arange(batch),tokens[:,i].clamp_min(0)+1]=0.5
                h=torch.where(active[:,None],self.algebra.multiply(h,factor),h)
            return h
        if self.kind=="binding":
            h=self.symbols.new_ones((batch,self.dimension))
            for i in range(length):
                update=torch.roll(h,1,dims=-1)*self.symbols[tokens[:,i].clamp_min(0)]
                h=torch.where((tokens[:,i]>=0)[:,None],update,h)
            return h
        h=self.embedding.weight.new_zeros((batch,self.dimension))
        for i in range(length):
            e=self.embedding(tokens[:,i].clamp_min(0))
            update=self.recurrent(h)+e
            if self.kind=="bilinear":update=update+self.interaction*h*e
            h=torch.where((tokens[:,i]>=0)[:,None],torch.tanh(update),h)
        return h

    def forward(self,tokens):return self.decoder(self.encode(tokens)).squeeze(-1)

    def storage(self):
        import json
        tensors=sum(t.numel()*t.element_size() for t in self.state_dict().values())
        metadata=len(json.dumps({"kind":self.kind,"dimension":self.dimension,"state_shapes":{k:list(v.shape) for k,v in self.state_dict().items()}},sort_keys=True).encode())
        vocabulary=self.algebra.storage()["vocabulary_json_bytes"] if hasattr(self,"algebra") else 0
        return dict(tensor_bytes=tensors,metadata_bytes=metadata,vocabulary_bytes=vocabulary,
                    total_payload_bytes=tensors+metadata+vocabulary,representation_bytes=self.dimension*8)
