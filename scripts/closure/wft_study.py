"""Serial constraint ablation and genuinely frozen graph/resolution transfer."""
import argparse
import fcntl
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from world_series.core.identity import source_identity
from world_series.wft.constraints import DiffusionField,domain,teacher,spectral_projection

SEEDS=[2203,2213,2221,2237,2243,2251,2267,2269]
METHODS={'unconstrained':(False,False,False),'symmetry':(True,False,False),
         'resolution':(False,True,False),'both':(True,True,False),'wrong_symmetry':(True,False,True)}

def dump(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def state_hash(model):return hashlib.sha256(b''.join(p.detach().numpy().tobytes() for p in model.parameters())).hexdigest()


def make_data(seed,samples,noise):
    model=teacher(seed);rng=np.random.default_rng(seed*100+samples*2+int(noise*10));data={}
    with torch.no_grad():
        for level in [0,1]:
            graph=domain(16,level=level);n=len(graph.mass)
            x=model.transition(graph,.4)@torch.tensor(rng.normal(size=(n,samples)))
            y=model.transition(graph)@x
            data[f'train_x_{level}']=x.numpy();data[f'train_y_clean_{level}']=y.numpy()
            data[f'train_y_{level}']=y.numpy()+rng.normal(0,noise,size=y.shape)
        for groups in [16,32,64]:
            for topology in ['cycle','path']:
                for level in [0,1]:
                    graph=domain(groups,topology,level);key=f'{groups}-{topology}-{level}'
                    x=model.transition(graph,.4)@torch.tensor(rng.normal(size=(len(graph.mass),16)))
                    data['x-'+key]=x.numpy();data['y-'+key]=(model.transition(graph)@x).numpy()
    return data


def fit(observed_inputs,observed_outputs,method):
    model=DiffusionField();optimizer=torch.optim.Adam(model.parameters(),lr=.03)
    graphs=[domain(16,level=level) for level in [0,1]]
    inputs=[torch.as_tensor(x) for x in observed_inputs];outputs=[torch.as_tensor(y) for y in observed_outputs]
    sym_on,scale_on,wrong=METHODS[method];history=[];constraint_seconds=0.;start=time.perf_counter()
    for step in range(100):
        optimizer.zero_grad()
        prediction=sum(((model.transition(g)@x-y)**2*g.mass[:,None]).sum()/(y.square()*g.mass[:,None]).sum().clamp_min(1e-12)
                       for g,x,y in zip(graphs,inputs,outputs))/2
        constraint_start=time.perf_counter();sym,scale=model.penalties(*graphs,wrong=wrong)
        penalty=.1*(sym if sym_on else 0.)+.1*(scale if scale_on else 0.)
        constraint_seconds+=time.perf_counter()-constraint_start
        loss=prediction+penalty
        if not torch.isfinite(loss):raise FloatingPointError('Nonfinite objective')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),10.,error_if_nonfinite=True);optimizer.step()
        history.append({'step':step+1,'prediction_loss':float(prediction.detach()),'symmetry_penalty':float(sym.detach()),
                        'resolution_penalty':float(scale.detach()),'objective':float(loss.detach())})
    return model,{'state_dict':model.state_dict(),'optimizer_state':optimizer.state_dict()},history,{
        'training_seconds':time.perf_counter()-start,'constraint_forward_seconds':constraint_seconds,
        'parameter_count':sum(p.numel() for p in model.parameters())}


def evaluate(model,data,seed,samples):
    rows=[];predictions={};frozen=state_hash(model)
    with torch.no_grad():
        for groups in [16,32,64]:
            for topology in ['cycle','path']:
                for level in [0,1]:
                    graph=domain(groups,topology,level);key=f'{groups}-{topology}-{level}'
                    x=data['x-'+key];y=data['y-'+key];start=time.perf_counter()
                    l=model.laplacian(graph);setup_seconds=time.perf_counter()-start
                    start=time.perf_counter();transition=torch.matrix_exp(-.15*l/graph.mass[:,None]);transition_seconds=time.perf_counter()-start
                    start=time.perf_counter();prediction=(transition@torch.as_tensor(x)).numpy();apply_seconds=time.perf_counter()-start
                    mass=graph.mass.numpy();denom=float(np.sum(mass[:,None]*y**2))
                    error=float(np.sum(mass[:,None]*(prediction-y)**2)/denom)
                    start=time.perf_counter();compressed,spectral=spectral_projection(l.numpy(),mass,x,k=min(5,samples));spectral_seconds=time.perf_counter()-start
                    compression=float(np.sum(mass[:,None]*(compressed-x)**2)/np.sum(mass[:,None]*x**2))
                    baselines={}
                    if groups==16 and topology=='cycle':
                        for name in ['pca','random']:
                            start=time.perf_counter();white=np.sqrt(mass)[:,None]*data[f'train_x_{level}']
                            if name=='pca':q=np.linalg.svd(white,full_matrices=False)[0][:,:min(5,samples)]
                            else:q=np.linalg.qr(np.random.default_rng(seed+level).normal(size=(len(mass),min(5,samples))))[0]
                            projected=q@(q.T@(np.sqrt(mass)[:,None]*x));reconstructed=projected/np.sqrt(mass)[:,None]
                            baselines[name]={'rank':q.shape[1],'relative_mass_error':float(np.sum(mass[:,None]*(reconstructed-x)**2)/np.sum(mass[:,None]*x**2)),
                                             'setup_and_apply_seconds':time.perf_counter()-start}
                    assert state_hash(model)==frozen,'Evaluation modified parameters'
                    predictions[key]=prediction
                    rows.append({'groups':groups,'nodes':len(mass),'topology':topology,'level':level,
                                 'relative_prediction_error':error,'relative_compression_error':compression,'spectral':spectral,
                                 'compression_controls':baselines,'setup_seconds':setup_seconds,'transition_seconds':transition_seconds,
                                 'apply_16_signals_seconds':apply_seconds,'spectral_seconds':spectral_seconds,
                                 'operator_bytes':l.numel()*l.element_size(),'frozen_parameter_hash':frozen})
    return rows,predictions


def run(output,profile=False):
    torch.set_num_threads(1);output.mkdir(parents=True,exist_ok=True)
    identity={'source':source_identity(ROOT),'script_sha256':sha(Path(__file__)),'protocol_sha256':sha(ROOT/'docs/closure/WFT_PROTOCOL.md'),
              'profile':profile,'confirmation':'DRAFT_NOT_AUTHORIZED'}
    ident=output/'identity.json'
    if ident.exists():
        old=json.loads(ident.read_text());assert old['source']['content_hash']==identity['source']['content_hash']
        assert all(old[k]==identity[k] for k in ['script_sha256','protocol_sha256','profile'])
    else:dump(ident,identity)
    conditions=[(s,n,v) for s in (SEEDS[:1] if profile else SEEDS) for n in ([4] if profile else [4,16]) for v in ([.1] if profile else [0.,.1])]
    receipts=[];wall_start=time.perf_counter()
    with (output/'worker.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for seed,samples,noise in conditions:
            data_path=output/f'{seed}-{samples}-{noise}-data.npz'
            if not data_path.exists():
                start=time.perf_counter();data=make_data(seed,samples,noise);np.savez_compressed(data_path,**data)
                dump(data_path.with_suffix('.json'),{'seed':seed,'samples':samples,'noise':noise,'generation_seconds':time.perf_counter()-start,'sha256':sha(data_path)})
            else:
                with np.load(data_path) as loaded:data={k:loaded[k] for k in loaded.files}
            for method in [*METHODS,'fixed_geometry','oracle_true_operator']:
                if time.perf_counter()-wall_start>1800:raise RuntimeError('Study wall ceiling reached')
                assert source_identity(ROOT)['content_hash']==identity['source']['content_hash'],'Source changed'
                key=f'{seed}-{samples}-{noise}-{method}';receipt_path=output/(key+'-receipt.json')
                if receipt_path.exists():
                    receipt=json.loads(receipt_path.read_text())
                    for filename,digest in receipt['files'].items():assert sha(output/filename)==digest
                    receipts.append(receipt);continue
                if method in METHODS:
                    model,checkpoint,history,cost=fit([data[f'train_x_{i}'] for i in [0,1]],[data[f'train_y_{i}'] for i in [0,1]],method)
                else:
                    model=teacher(seed) if method=='oracle_true_operator' else DiffusionField()
                    checkpoint={'state_dict':model.state_dict()};history=[];cost={'training_seconds':0.,'constraint_forward_seconds':0.,'parameter_count':0}
                checkpoint_path=output/(key+'.pt');torch.save(checkpoint,checkpoint_path)
                rows,predictions=evaluate(model,data,seed,samples)
                prediction_path=output/(key+'-predictions.npz');np.savez_compressed(prediction_path,**predictions)
                result={'seed':seed,'samples':samples,'noise':noise,'method':method,'rows':rows,'history':history,'cost':cost,
                        'parameter_hash':state_hash(model),'complete':len(rows)==12,'oracle':method=='oracle_true_operator',
                        'scope':'Finite equitable-graph coarsening, frozen size/topology transfer; no continuous PDE convergence claim'}
                result_path=output/(key+'.json');dump(result_path,result)
                receipt={'key':key,'complete':result['complete'],'files':{p.name:sha(p) for p in [result_path,checkpoint_path,prediction_path,data_path,data_path.with_suffix('.json')]}}
                dump(receipt_path,receipt);receipts.append(receipt)
                print(json.dumps({'key':key,'training_seconds':cost['training_seconds'],'transfer_mean_error':float(np.mean([r['relative_prediction_error'] for r in rows if r['groups']>16]))}),flush=True)
        dump(output/'summary.json',{'complete':len(receipts)==len(conditions)*7,'expected_fits':len(conditions)*7,'receipts':receipts,
                                  'identity':identity,'elapsed_seconds':time.perf_counter()-wall_start})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--profile',action='store_true');a=p.parse_args()
    try:run(a.output,a.profile)
    except BaseException as exc:
        a.output.mkdir(exist_ok=True,parents=True)
        dump(a.output/('failure-'+str(time.time_ns())+'.json'),{'message':str(exc),'traceback':traceback.format_exc(),'source':source_identity(ROOT)})
        raise
