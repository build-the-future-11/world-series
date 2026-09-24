"""Serial source-frozen causal lifecycle study with per-stream immutable receipts."""
import argparse
from collections import deque
import fcntl
import hashlib
import json
from pathlib import Path
import pickle
import sys
import time
import traceback
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from world_series.qapen.causal import CausalLifecycle,FrozenQuantizer,gaussian_nll
from world_series.core.identity import source_identity

SEEDS=[1009,1103,1201,1301,1409,1511,1601,1709]
SCHEDULES=['no_shift','rare_return','long_gap','delayed_cue']
METHODS={
    'lifecycle_memory':{},'lifecycle_no_memory':{'memory':False},
    'fixed_memory':{'lifecycle':False,'fixed_experts':4},
    'fixed_no_memory':{'lifecycle':False,'fixed_experts':4,'memory':False},
    'single_memory':{'lifecycle':False},'random_memory':{'retrieval':'random'},
    'recent_memory':{'retrieval':'recent'},'rolling_ridge':None}


def dump(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def stream(seed,schedule,noise,n=320):
    rng=np.random.default_rng(seed);regime=np.zeros(n,dtype=int)
    if schedule=='rare_return':regime[(np.arange(n)%100)>=88]=1
    elif schedule=='long_gap':regime[40:64]=1;regime[256:280]=1
    elif schedule=='delayed_cue':regime=(np.arange(n)//80)%2
    elif schedule!='no_shift':raise ValueError(schedule)
    coefficients=rng.uniform(.25,.8,2);offsets=np.array([-1.,1.])*rng.uniform(.5,1.5,2)
    cue_regime=np.r_[regime[4:],np.repeat(regime[-1],4)] if schedule=='delayed_cue' else regime
    cues=offsets[cue_regime]+rng.normal(0,.3,n)
    context=[];ys=[];previous=0.;recovery=[];last_switch=-100
    for t in range(n):
        if t and regime[t]!=regime[t-1]:last_switch=t
        context.append([previous,cues[t]])
        previous=coefficients[regime[t]]*previous+offsets[regime[t]]+rng.normal(0,noise)
        ys.append(previous);recovery.append(t-last_switch<8)
    return {'context':context,'targets':ys,'regime':regime.tolist(),'recovery':recovery,
            'parameters':{'ar':coefficients.tolist(),'offsets':offsets.tolist()},
            'seed':seed,'schedule':schedule,'noise':noise}


class RollingRidge:
    def __init__(self,cap=2_000_000):
        self.window=deque(maxlen=32);self.operations=0;self.cap=cap;self.pending=None;self.variance=1.
    def predict(self,context):
        if self.pending is not None:raise RuntimeError('Observe pending prediction')
        x=np.r_[context,1.];self.operations+=len(self.window)*9+27
        if self.operations>self.cap:raise RuntimeError('Operation budget exhausted')
        if self.window:
            a=np.array([r[0] for r in self.window]);b=np.array([r[1] for r in self.window])
            weights=np.linalg.solve(a.T@a+.1*np.eye(3),a.T@b);mean=float(x@weights)
        else:mean=0.
        self.pending=(x,mean,self.variance);return mean,self.variance
    def observe(self,y):
        x,mean,var=self.pending;self.window.append((x,y));self.pending=None
        self.variance=max(.05,.95*self.variance+.05*min((y-mean)**2,100.))
        return {'mean':mean,'variance':var,'nll':gaussian_nll(y,mean,var),'base_nll':gaussian_nll(y,mean,var),
                'operations':self.operations,'active':1,'identities':1,'memory_id':None,'memory_size':len(self.window)}


def run(output,profile=False):
    output.mkdir(parents=True,exist_ok=True);torch.set_num_threads(1)
    protocol=ROOT/'docs/closure/QAPEN_PROTOCOL.md'
    identity={'source':source_identity(ROOT),'script_sha256':sha(Path(__file__)),
              'protocol_sha256':sha(protocol),'profile':profile,'confirmation':'DRAFT_NOT_AUTHORIZED'}
    ident=output/'identity.json'
    if ident.exists():
        old=json.loads(ident.read_text())
        assert old['source']['content_hash']==identity['source']['content_hash']
        assert all(old[k]==identity[k] for k in ['script_sha256','protocol_sha256','profile'])
    else:dump(ident,identity)
    training=np.concatenate([stream(s,'delayed_cue',.3)['context'] for s in [31,37,41,43]])
    start=time.perf_counter();quantizer=FrozenQuantizer.fit(training)
    pretrain_seconds=time.perf_counter()-start
    if not (output/'codebook.json').exists():dump(output/'codebook.json',{'centers':quantizer.centers.tolist(),'pretraining_seconds':pretrain_seconds,'seeds':[31,37,41,43]})
    planned=[(s,c,n,m) for s in (SEEDS[:1] if profile else SEEDS) for c in (SCHEDULES[:1] if profile else SCHEDULES) for n in ([.1] if profile else [.1,.6]) for m in METHODS]
    receipts=[]
    with (output/'worker.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        for seed,condition,noise,method in planned:
            assert source_identity(ROOT)['content_hash']==identity['source']['content_hash'],'Source changed during study'
            key=f'{seed}-{condition}-{noise}-{method}';receipt=output/(key+'-receipt.json')
            if receipt.exists():
                record=json.loads(receipt.read_text())
                for name,digest in record['files'].items():assert sha(output/name)==digest
                receipts.append(record);continue
            data=stream(seed,condition,noise);datafile=output/f'{seed}-{condition}-{noise}-data.json'
            if not datafile.exists():dump(datafile,data)
            model=RollingRidge() if method=='rolling_ridge' else CausalLifecycle(quantizer,seed=seed,**METHODS[method])
            rows=[];failure=None;start=time.perf_counter()
            try:
                for t,(context,y) in enumerate(zip(data['context'],data['targets'])):
                    model.predict(context);row=model.observe(y)
                    row.update(time=t,target=y,rare=data['regime'][t]==1,recovery=data['recovery'][t],coverage95=bool(abs(y-row['mean'])<=1.959963984540054*np.sqrt(row['variance'])))
                    rows.append(row)
            except Exception as exc:failure={'message':str(exc),'traceback':traceback.format_exc()}
            elapsed=time.perf_counter()-start
            statefile=output/(key+'-checkpoint.pkl');start_storage=time.perf_counter()
            checkpoint={'kind':'rolling_ridge','state':model.__dict__} if method=='rolling_ridge' else {'kind':'causal_lifecycle','model':model}
            statefile.write_bytes(pickle.dumps(checkpoint,protocol=5));storage_seconds=time.perf_counter()-start_storage
            summaries={}
            for label,selected in [('all',rows),('rare',[r for r in rows if r['rare']]),('ordinary',[r for r in rows if not r['rare']]),('recovery',[r for r in rows if r['recovery']])]:
                summaries[label]={'n':len(selected),'nll':float(np.mean([r['nll'] for r in selected])) if selected and failure is None else None,
                                  'coverage95':float(np.mean([r['coverage95'] for r in selected])) if selected and failure is None else None}
            result={'seed':seed,'schedule':condition,'noise':noise,'method':method,'rows':rows,'summary':summaries,
                    'complete':len(rows)==320 and failure is None,'failure':failure,'elapsed_seconds':elapsed,
                    'operations':model.operations,'checkpoint_bytes':statefile.stat().st_size,'checkpoint_seconds':storage_seconds,
                    'state':model.state_receipt() if method!='rolling_ridge' else {'window_size':len(model.window)}}
            resultfile=output/(key+'.json');dump(resultfile,result)
            record={'key':key,'complete':result['complete'],'files':{p.name:sha(p) for p in [resultfile,statefile,datafile]}}
            dump(receipt,record);receipts.append(record)
            print(json.dumps({'key':key,'complete':result['complete'],'nll':summaries['all']['nll'],'seconds':elapsed}),flush=True)
        dump(output/'summary.json',{'expected_stream_methods':len(planned),'complete':all(r['complete'] for r in receipts),'receipts':receipts,'identity':identity})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--profile',action='store_true');a=p.parse_args()
    try:run(a.output,a.profile)
    except BaseException as exc:
        a.output.mkdir(parents=True,exist_ok=True)
        dump(a.output/('failure-'+str(time.time_ns())+'.json'),{'message':str(exc),'traceback':traceback.format_exc(),'source':source_identity(ROOT)})
        raise
