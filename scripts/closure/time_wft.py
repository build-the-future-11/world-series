"""Separate reproducible-order timing audit over unchanged frozen WFT models."""
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from world_series.core.identity import source_identity
from world_series.wft.constraints import DiffusionField,domain,spectral_projection


def timed(model,data,row,samples):
    start=time.perf_counter();g=domain(row['groups'],row['topology'],row['level']);graph_seconds=time.perf_counter()-start
    key=f"{row['groups']}-{row['topology']}-{row['level']}";x=data['x-'+key]
    with torch.no_grad():
        start=time.perf_counter();l=model.laplacian(g);laplacian_seconds=time.perf_counter()-start
        start=time.perf_counter();transition=torch.matrix_exp(-.15*l/g.mass[:,None]);transition_seconds=time.perf_counter()-start
        start=time.perf_counter();prediction=transition@torch.as_tensor(x);apply_seconds=time.perf_counter()-start
        start=time.perf_counter();projection,receipt=spectral_projection(l.numpy(),g.mass.numpy(),x,k=min(5,samples));spectral_seconds=time.perf_counter()-start
    retained=sum(v.numel()*v.element_size() for v in g.__dict__.values() if isinstance(v,torch.Tensor))
    # Include an n*n float64 eigenbasis as a documented retained-output estimate.
    numerical_bytes=l.numel()*8+transition.numel()*8+prediction.numel()*8+projection.nbytes+len(g.mass)**2*8
    return {'graph_seconds':graph_seconds,'laplacian_seconds':laplacian_seconds,'transition_seconds':transition_seconds,
            'apply_16_seconds':apply_seconds,'spectral_seconds':spectral_seconds,
            'domain_tensor_bytes':retained,'numerical_array_bytes_estimate':numerical_bytes,'rank_retained':receipt['rank_retained']}


def main():
    torch.set_num_threads(1);directory=ROOT/'campaigns/wft-constraints-v1';out=ROOT/'campaigns/wft-constraints-v1-timing'
    out.mkdir(exist_ok=False)
    summary=json.loads((directory/'summary.json').read_text());tasks=[];models={};datasets={};loading=0.
    start_all=time.perf_counter()
    for receipt in summary['receipts']:
        start=time.perf_counter();key=receipt['key'];record=json.loads((directory/(key+'.json')).read_text())
        checkpoint=directory/(key+'.pt')
        assert hashlib.sha256(checkpoint.read_bytes()).hexdigest()==receipt['files'][checkpoint.name]
        model=DiffusionField();model.load_state_dict(torch.load(checkpoint,weights_only=True)['state_dict']);models[key]=model
        data_key=(record['seed'],record['samples'],record['noise'])
        if data_key not in datasets:
            path=directory/f'{data_key[0]}-{data_key[1]}-{data_key[2]}-data.npz'
            assert hashlib.sha256(path.read_bytes()).hexdigest()==receipt['files'][path.name]
            with np.load(path) as loaded:datasets[data_key]={k:loaded[k] for k in loaded.files}
        tasks.extend((key,data_key,record['method'],r) for r in record['rows']);loading+=time.perf_counter()-start
    order=np.random.default_rng(240928).permutation(len(tasks));rows=[]
    for index in order:
        if time.perf_counter()-start_all>1800:raise RuntimeError('Timing wall ceiling reached')
        key,data_key,method,row=tasks[index];model=models[key];data=datasets[data_key]
        timed(model,data,row,data_key[1])
        repetitions=[timed(model,data,row,data_key[1]) for _ in range(3)]
        rows.append({'key':key,'method':method,'groups':row['groups'],'topology':row['topology'],'level':row['level'],'repetitions':repetitions})
    assert len(rows)==2688
    tables=[]
    for method in sorted({r['method'] for r in rows}):
        selected=[s for r in rows if r['method']==method for s in r['repetitions']]
        tables.append({'method':method,'timed_repetitions':len(selected),**{k:float(np.mean([s[k] for s in selected])) for k in selected[0] if k.endswith('seconds')}})
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    result={'complete':True,'cases':2688,'repetitions_per_case':3,'table':tables,'rows':rows,'loading_seconds':loading,
            'elapsed_seconds':time.perf_counter()-start_all,'peak_process_rss_bytes':int(rss if sys.platform=='darwin' else rss*1024),
            'source':source_identity(ROOT),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'protocol_sha256':hashlib.sha256((ROOT/'docs/closure/WFT_TIMING_PROTOCOL.md').read_bytes()).hexdigest(),
            'scope':'Post-study same-host cost accounting. Cumulative RSS and retained bytes are not per-method peak allocation; no wall-time superiority claim.'}
    (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    receipt={k:v for k,v in result.items() if k!='rows'}
    receipt['raw_sha256']=hashlib.sha256((out/'results.json').read_bytes()).hexdigest()
    (ROOT/'docs/closure/WFT_TIMING_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in {'table','source'}}))


if __name__=='__main__':main()
