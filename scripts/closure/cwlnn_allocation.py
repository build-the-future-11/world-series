"""Bounded CPU allocation-shape probe; not a per-method peak-memory estimator."""
import json
from pathlib import Path
import resource
import time

import torch
from torch.utils._python_dispatch import TorchDispatchMode
from world_series.cwlnn.conditional import ConditionalWorld, SparseWorld


class Shapes(TorchDispatchMode):
    def __init__(self):
        self.max_elements=0
        self.shape=None
        self.operations=0

    def __torch_dispatch__(self,func,types,args=(),kwargs=None):
        result=func(*args,**(kwargs or {}))
        def inspect(value):
            if isinstance(value,torch.Tensor):
                if value.numel()>self.max_elements:
                    self.max_elements=value.numel()
                    self.shape=list(value.shape)
            elif isinstance(value,(tuple,list)):
                for item in value: inspect(item)
        inspect(result)
        self.operations+=1
        return result


torch.set_num_threads(1)
torch.manual_seed(270924)
model=ConditionalWorld(routing='learned').double().eval()
rows=[]
for n in (1000,10000,100000):
    ids=torch.arange(n)
    a=ids[:-1]
    edges=torch.stack([torch.cat([a,a+1]),torch.cat([a+1,a])])
    graph=SparseWorld(torch.randn(n,4,dtype=torch.float64),edges,ids//2,torch.zeros(n,dtype=torch.long),ids)
    observer=Shapes()
    started=time.perf_counter()
    with torch.no_grad(),observer:
        prediction,receipt=model(graph,.01)
    assert receipt['refine_rows']==n//100 and receipt['attention_pairs']==0
    assert observer.max_elements<=128*n
    rows.append({'nodes':n,'largest_operator_output_elements':observer.max_elements,
                 'largest_operator_output_shape':observer.shape,'observed_operations':observer.operations,
                 'instrumented_seconds':time.perf_counter()-started,'receipt':receipt})
out=Path('campaigns/cwlnn-allocation-v1')
out.mkdir(exist_ok=False)
(out/'results.json').write_text(json.dumps({'rows':rows,
    'peak_process_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    'scope':'One bounded shape-instrumented sparse forward per size, 1% refinement. Largest individual operator output, not sum of live allocations or a per-method peak. No attention path at these sizes.'},indent=2))
print(json.dumps([{k:v for k,v in r.items() if k!='receipt'} for r in rows],indent=2))
