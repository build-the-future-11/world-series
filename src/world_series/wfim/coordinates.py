"""Bounded per-word coordinates on a fixed degree-truncated word algebra."""
from itertools import product
import math
import torch
from torch import nn


class WordCoordinates(nn.Module):
    def __init__(self, alphabet_size=2, max_degree=6, log_bound=1.0,
                 max_terms=4096, max_pairs=200000):
        super().__init__()
        if alphabet_size < 1 or max_degree < 0 or not math.isfinite(log_bound) or log_bound <= 0:
            raise ValueError("invalid algebra or scale bounds")
        size = sum(alphabet_size ** d for d in range(max_degree + 1))
        pairs = sum((d + 1) * alphabet_size ** d for d in range(max_degree + 1))
        if size > max_terms or pairs > max_pairs:
            raise ValueError(f"allocation cap exceeded: {size} terms, {pairs} product pairs")
        self.alphabet_size, self.max_degree, self.log_bound = alphabet_size, max_degree, log_bound
        self.words = tuple(w for d in range(max_degree+1) for w in product(range(alphabet_size),repeat=d))
        self.index = {w:i for i,w in enumerate(self.words)}
        left,right,target = [],[],[]
        for k,w in enumerate(self.words):
            for cut in range(len(w)+1):
                left.append(self.index[w[:cut]]); right.append(self.index[w[cut:]]); target.append(k)
        self.register_buffer("left",torch.tensor(left,dtype=torch.long))
        self.register_buffer("right",torch.tensor(right,dtype=torch.long))
        self.register_buffer("target",torch.tensor(target,dtype=torch.long))
        self.theta = nn.Parameter(torch.zeros(size-1,dtype=torch.float64))

    def scales(self):
        return torch.cat((self.theta.new_ones(1),torch.exp(self.log_bound*torch.tanh(self.theta))))

    def transport(self,x,inverse=False):
        if x.shape[-1] != len(self.words): raise ValueError("wrong coefficient dimension")
        s=self.scales()
        return x/s if inverse else x*s

    def multiply(self,x,y):
        if x.shape != y.shape or x.shape[-1] != len(self.words):
            raise ValueError("matching coefficient arrays required")
        s=self.scales()
        values=x[...,self.left]*y[...,self.right]*s[self.left]*s[self.right]/s[self.target]
        index=self.target.expand(values.shape)
        return torch.zeros_like(x).scatter_add(-1,index,values)

    def storage(self):
        """Exact tensor payload and canonical vocabulary bytes; Python overhead excluded."""
        import json
        return {"parameter_bytes":sum(t.numel()*t.element_size() for t in self.parameters()),
                "buffer_bytes":sum(t.numel()*t.element_size() for t in self.buffers()),
                "vocabulary_json_bytes":len(json.dumps(self.words,separators=(",",":")).encode()),
                "scope":"tensor payload plus serialized vocabulary, not process RSS or checkpoint container size"}
