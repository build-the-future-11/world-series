"""Train matched program encoders and evaluate charged finite-domain search."""
import argparse
import copy
from dataclasses import asdict
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
from world_series.wcode.learned import DOMAIN,MODES,ProgramScorer,pack_programs,program_pool,public_tensor
from world_series.wcode.dsl import ast_nodes
from world_series.wcode.interpreter import interpret,Fuel

SEEDS=[2017,2027,2039,2053,2063,2081,2087,2099]
CAPS=[8,24,64,331]

def dump(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def examples(pool,index,positions):return [[DOMAIN[int(p)],pool[index]['signature'][int(p)]] for p in positions]


def make_data(pool,seed):
    rng=np.random.default_rng(seed)
    train=[i for i,r in enumerate(pool) if r['role']=='train']
    indices=rng.choice(train,size=(80,32))
    positions=np.array([[rng.choice(17,4,replace=False) for _ in range(32)] for _ in range(80)])
    public=np.array([rng.choice(17,4,replace=False) for _ in pool])
    return indices,positions,public


def charged_search(pool,target,positions,order,cap):
    public_calls=0;verifier_calls=0;fuel_used=0;visited=[];chosen=None
    expected=dict(examples(pool,target,range(17)))
    start=time.perf_counter();verification_seconds=0.
    for index in order[:cap]:
        index=int(index);visited.append(index);fit=True
        for position in positions:
            x=DOMAIN[int(position)];fuel=Fuel(128)
            actual=interpret(pool[index]['program'],{'x':x},fuel)
            public_calls+=1;fuel_used+=128-fuel.remaining
            if actual!=expected[x]:fit=False;break
        if fit:chosen=index;break
    public_seconds=time.perf_counter()-start
    correct=False
    if chosen is not None:
        correct=True;start=time.perf_counter()
        for position in sorted(set(range(17))-set(map(int,positions))):
            x=DOMAIN[position];fuel=Fuel(128)
            actual=interpret(pool[chosen]['program'],{'x':x},fuel)
            verifier_calls+=1;fuel_used+=128-fuel.remaining
            correct=correct and actual==expected[x]
        verification_seconds=time.perf_counter()-start
    return {'target':target,'family':pool[target]['identity'],'role':pool[target]['role'],'cap':cap,
            'visited':visited,'selected':chosen,'public_fit':chosen is not None,'verified':bool(correct),
            'false_public_fit':chosen is not None and not correct,'candidate_evaluations':len(visited),
            'public_interpreter_calls':public_calls,'verifier_calls':verifier_calls,'fuel_used':fuel_used,
            'public_seconds':public_seconds,'verification_seconds':verification_seconds}


def train(pool,batch,seed,mode,data,output):
    torch.manual_seed(seed);model=ProgramScorer(mode);optimizer=torch.optim.Adam(model.parameters(),lr=.003)
    indices,positions,public=data
    selection=[i for i,r in enumerate(pool) if r['role']=='selection']
    selection_examples=public_tensor([examples(pool,i,public[i]) for i in selection])
    history=[];checkpoints=[];best=None;best_rank=float('inf');start=time.perf_counter();selection_seconds=0.
    for step in range(80):
        inputs=public_tensor([examples(pool,int(i),p) for i,p in zip(indices[step],positions[step])])
        optimizer.zero_grad();scores=model(batch,inputs)
        loss=torch.nn.functional.cross_entropy(scores,torch.tensor(indices[step]))
        if not torch.isfinite(loss):raise FloatingPointError('Nonfinite training loss')
        loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),5.,error_if_nonfinite=True);optimizer.step()
        history.append(float(loss.detach()))
        if step+1 in [20,40,80]:
            check_start=time.perf_counter()
            with torch.no_grad():validation=model(batch,selection_examples).numpy()
            ranks=[int(np.flatnonzero(np.argsort(-scores,kind='stable')==i)[0])+1 for i,scores in zip(selection,validation)]
            score=float(np.mean(ranks));selection_seconds+=time.perf_counter()-check_start
            checkpoint={'step':step+1,'state_dict':copy.deepcopy(model.state_dict()),'optimizer_state':copy.deepcopy(optimizer.state_dict()),'selection_mean_rank':score}
            filename=f'{seed}-{mode}-step{step+1}.pt';torch.save(checkpoint,output/filename)
            checkpoints.append({'step':step+1,'selection_mean_rank':score,'path':filename,'sha256':sha(output/filename)})
            if score<best_rank:best_rank=score;best=checkpoint
    total=time.perf_counter()-start;model.load_state_dict(best['state_dict'])
    return model,{'losses':history,'training_and_selection_seconds':total,'selection_seconds':selection_seconds,
                  'selected_step':best['step'],'selection_mean_rank':best_rank,'checkpoints':checkpoints,
                  'parameter_count':sum(p.numel() for p in model.parameters())}


def run(output,profile=False):
    output.mkdir(parents=True,exist_ok=True);torch.set_num_threads(1)
    identity={'source':source_identity(ROOT),'script_sha256':sha(Path(__file__)),'protocol_sha256':sha(ROOT/'docs/closure/WCODE_PROTOCOL.md'),
              'profile':profile,'confirmation':'DRAFT_NOT_AUTHORIZED'}
    identity_path=output/'identity.json'
    if identity_path.exists():
        old=json.loads(identity_path.read_text())
        assert old['source']['content_hash']==identity['source']['content_hash']
        assert all(old[k]==identity[k] for k in ['script_sha256','protocol_sha256','profile'])
    else:dump(identity_path,identity)
    start=time.perf_counter();pool=program_pool();generation_seconds=time.perf_counter()-start
    assert len(pool)==331
    dataset=[{k:asdict(v) if k=='program' else v for k,v in r.items()} for r in pool]
    if not (output/'dataset.json').exists():dump(output/'dataset.json',{'families':dataset,'construction_seconds':generation_seconds,'domain':DOMAIN})
    start=time.perf_counter();batch=pack_programs([r['program'] for r in pool]);packing_seconds=time.perf_counter()-start
    evaluation=[i for i,r in enumerate(pool) if r['role'].startswith('evaluation')]
    receipts=[];wall_start=time.perf_counter()
    with (output/'worker.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for seed in SEEDS[:1] if profile else SEEDS:
            data=make_data(pool,seed);data_path=output/f'{seed}-training-data.npz'
            if not data_path.exists():np.savez_compressed(data_path,targets=data[0],public_positions=data[1],selection_evaluation_positions=data[2])
            trace_path=output/f'{seed}-training-search-traces.json'
            if not trace_path.exists():
                trace_start=time.perf_counter()
                traces=[charged_search(pool,i,data[2][i],np.arange(len(pool)),24) for i,r in enumerate(pool) if r['role']=='train']
                dump(trace_path,{'rows':traces,'seconds':time.perf_counter()-trace_start,
                     'scope':'Unfiltered training-family uniform-search traces. Supervised candidate labels use canonical training targets; these traces audit failures rather than define a policy-gradient objective.'})
            for mode in MODES+['uniform','length']:
                assert source_identity(ROOT)['content_hash']==identity['source']['content_hash'],'Source changed'
                if time.perf_counter()-wall_start>1800:raise RuntimeError('Study wall ceiling reached; completed receipts preserved')
                key=f'{seed}-{mode}';receipt_path=output/(key+'-receipt.json')
                if receipt_path.exists():
                    receipt=json.loads(receipt_path.read_text())
                    for name,digest in receipt['files'].items():assert sha(output/name)==digest
                    receipts.append(receipt);continue
                training=None;embedding_seconds=0.;cache_bytes=0
                if mode in MODES:
                    model,training=train(pool,batch,seed,mode,data,output)
                    start=time.perf_counter()
                    with torch.no_grad():embeddings=model.encode(batch)
                    embedding_seconds=time.perf_counter()-start;cache_bytes=embeddings.numel()*embeddings.element_size()
                rows=[]
                for target in evaluation:
                    positions=data[2][target];start=time.perf_counter()
                    if mode=='uniform':order=np.arange(len(pool))
                    elif mode=='length':order=np.array(sorted(range(len(pool)),key=lambda i:(ast_nodes(pool[i]['program']),i)))
                    else:
                        with torch.no_grad():
                            public=public_tensor(examples(pool,target,positions))[None]
                            query=model.example(public).mean(1)
                            if mode=='no_task':query=query*0
                            logits=torch.tanh(model.task(query))@embeddings.T/(model.width**.5)
                        order=np.argsort(-logits[0].numpy(),kind='stable')
                    ranking_seconds=time.perf_counter()-start
                    for cap in CAPS:
                        row=charged_search(pool,target,positions,order,cap)
                        row.update(seed=seed,method=mode,public_positions=positions.tolist(),ranking_seconds=ranking_seconds)
                        rows.append(row)
                result={'seed':seed,'method':mode,'rows':rows,'training':training,'graph_packing_seconds':packing_seconds,
                        'embedding_seconds':embedding_seconds,'embedding_cache_bytes':cache_bytes,'ranking_tasks':len(evaluation),
                        'complete':len(rows)==111*4,'scope':'Finite integer DSL and exposed development families; no general coding claim'}
                if mode in {'uniform','length'}:result['graph_packing_seconds']=0.
                result_path=output/(key+'.json');dump(result_path,result)
                files=[result_path,data_path,trace_path,output/'dataset.json']
                if training:files.extend(output/c['path'] for c in training['checkpoints'])
                receipt={'key':key,'complete':result['complete'],'files':{p.name:sha(p) for p in files}}
                dump(receipt_path,receipt);receipts.append(receipt)
                print(json.dumps({'key':key,'rows':len(rows),'training_seconds':training['training_and_selection_seconds'] if training else 0.,'cap24_success':sum(r['verified'] for r in rows if r['cap']==24)/111}),flush=True)
        dump(output/'summary.json',{'complete':all(r['complete'] for r in receipts),'expected_models':8 if profile else 64,'receipts':receipts,'identity':identity,'elapsed_seconds':time.perf_counter()-wall_start})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=Path);p.add_argument('--profile',action='store_true');a=p.parse_args()
    try:run(a.output,a.profile)
    except BaseException as exc:
        a.output.mkdir(exist_ok=True,parents=True)
        dump(a.output/('failure-'+str(time.time_ns())+'.json'),{'message':str(exc),'traceback':traceback.format_exc(),'source':source_identity(ROOT)})
        raise
