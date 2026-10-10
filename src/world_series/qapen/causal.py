"""Finite causal expert lifecycle with a frozen quantizer and delayed memory utility.

This version is separate from the historical write-only QAPENModel. It implements
explicit mechanisms, not nonparametric inference or an infinite ensemble.
"""
from collections import deque
import copy
from dataclasses import dataclass, asdict
import uuid
import math
from numbers import Real
import numpy as np
import torch
from torch import nn
from world_series.qapen.mixture import mixture_moments


class FrozenQuantizer:
    def __init__(self, centers):
        array=np.asarray(centers,dtype=np.float64)
        if array.ndim!=2 or not len(array) or not np.isfinite(array).all():
            raise ValueError('Finite two-dimensional centers required')
        # A read-only flag on an owned ndarray can be reversed by the caller.
        # Bind the frozen codebook to an immutable bytes owner instead.
        self._centers=np.frombuffer(array.tobytes(),dtype=np.float64).reshape(array.shape)

    @property
    def centers(self):
        return self._centers

    def __deepcopy__(self,memo):
        duplicate=type(self)(self.centers)
        memo[id(self)]=duplicate
        return duplicate

    @classmethod
    def fit(cls, observations, k=8, seed=17, iterations=30):
        x=np.asarray(observations,dtype=np.float64)
        rng=np.random.default_rng(seed)
        if len(x)<k:raise ValueError('Insufficient pretraining observations')
        centers=x[rng.choice(len(x),k,replace=False)].copy()
        for _ in range(iterations):
            labels=((x[:,None]-centers[None])**2).sum(-1).argmin(1)
            for j in range(k):
                if np.any(labels==j):centers[j]=x[labels==j].mean(0)
        return cls(centers)

    def encode(self, context):
        x=np.asarray(context,dtype=np.float64)
        if x.shape!=self.centers.shape[1:] or not np.isfinite(x).all():raise ValueError('Invalid context')
        label=int(((self.centers-x)**2).sum(1).argmin())
        residual=x-self.centers[label]
        return label,np.r_[x,residual,np.eye(len(self.centers))[label]]


class GaussianExpert(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.linear=nn.Linear(width,1,dtype=torch.float64)
        nn.init.zeros_(self.linear.weight);nn.init.zeros_(self.linear.bias)
        self.register_buffer('variance',torch.tensor(1.,dtype=torch.float64))

    def moments(self, x):
        with torch.no_grad():return float(self.linear(torch.as_tensor(x,dtype=torch.float64)).item()),float(self.variance)


@dataclass
class ExpertMetadata:
    identity:str
    state:str
    birth:int
    last_used:int
    key:list
    prospective_count:int=0
    prospective_gain:float=0.
    updates:int=0


@dataclass
class Engram:
    identity:int
    code:int
    key:list
    value:float
    variance:float
    expert_id:str
    written_at:int
    accesses:int=0
    utility_count:int=0
    utility_sum:float=0.


def gaussian_nll(y,mean,variance):
    for name,value in [('target',y),('mean',mean),('variance',variance)]:
        if isinstance(value,(bool,np.bool_)) or not isinstance(value,Real) or not math.isfinite(value):
            raise ValueError(f'{name} must be a finite real number')
    if variance<=0:raise ValueError('variance must be positive')
    y,mean,variance=float(y),float(mean),float(variance)
    root=math.sqrt(variance);error=y-mean
    standardized=error/root if math.isfinite(error) else y/root-mean/root
    value=.5*math.log(2*math.pi)+.5*math.log(variance)+(.5*standardized)*standardized
    if not math.isfinite(value):raise ValueError('Gaussian NLL exceeds the finite numeric range')
    return value


class CausalLifecycle:
    def __init__(self, quantizer, *, lifecycle=True, memory=True, retrieval='nearest',
                 fixed_experts=1, max_active=4, max_identities=16, memory_capacity=64,
                 cooldown=24, warmup=8, sleep_after=48, seed=0, operation_cap=2_000_000):
        if retrieval not in {'nearest','random','recent'}:raise ValueError('Unknown retrieval mode')
        if not 1<=fixed_experts<=max_active<=max_identities:raise ValueError('Invalid expert caps')
        if min(memory_capacity,cooldown,warmup,sleep_after,operation_cap)<1:raise ValueError('Positive resource and lifecycle limits required')
        self.quantizer=quantizer;self.lifecycle=lifecycle;self.memory_enabled=memory;self.retrieval=retrieval
        self.max_active=max_active;self.max_identities=max_identities;self.capacity=memory_capacity
        self.cooldown=cooldown;self.warmup=warmup;self.sleep_after=sleep_after;self.seed=seed
        self.models=nn.ModuleDict();self.optimizers={};self.metadata={};self.engrams=[]
        self.replay=deque(maxlen=32);self.rng=np.random.default_rng(seed)
        self.t=0;self.next_identity=0;self.next_engram=0;self.last_birth=-cooldown
        self.surprise_streak=0;self.pending=None;self.events=[];self.operations=0;self.operation_cap=operation_cap
        self.costs={'expert_predictions':0,'expert_updates':0,'retrieval_distances':0,'quantizer_distances':0,'warmup_updates':0,'consolidation_checks':0}
        for j in range(fixed_experts):self._spawn(quantizer.centers[j%len(quantizer.centers)],'ACTIVE')

    def _charge(self, amount):
        if self.operations+amount>self.operation_cap:raise RuntimeError('Operation budget exhausted')
        self.operations+=amount

    def _spawn(self,key,state='WARMUP'):
        if len(self.models)>=self.max_identities:return None
        identity=uuid.uuid5(uuid.NAMESPACE_OID,f'world-series-qapen-{self.seed}-{self.next_identity}').hex
        self.next_identity+=1
        width=2*self.quantizer.centers.shape[1]+len(self.quantizer.centers)
        model=GaussianExpert(width);self.models[identity]=model
        self.optimizers[identity]=torch.optim.Adam(model.parameters(),lr=.02)
        self.metadata[identity]=ExpertMetadata(identity,state,self.t,self.t,np.asarray(key).tolist())
        self.events.append({'time':self.t,'event':'spawn','identity':identity,'state':state})
        return identity

    def _transition(self,identity,state):
        old=self.metadata[identity].state
        allowed={'WARMUP':{'ACTIVE','PRUNED'},'ACTIVE':{'SLEEP'},'SLEEP':{'REVIVED'},'REVIVED':{'ACTIVE','SLEEP'}}
        if state not in allowed[old]:raise ValueError(f'Illegal lifecycle transition {old}->{state}')
        self.metadata[identity].state=state
        self.events.append({'time':self.t,'event':'transition','identity':identity,'from':old,'to':state})

    def _make_room(self):
        active=[m for m in self.metadata.values() if m.state in {'ACTIVE','REVIVED'}]
        if len(active)>=self.max_active:
            oldest=min(active,key=lambda m:(m.last_used,m.birth,m.identity))
            self._transition(oldest.identity,'SLEEP')

    def predict(self,context):
        if self.pending is not None:raise RuntimeError('Observe the pending prediction before predicting again')
        context=np.asarray(context,dtype=np.float64).copy()
        self._charge(self.quantizer.centers.size);self.costs['quantizer_distances']+=len(self.quantizer.centers)
        code,features=self.quantizer.encode(context)
        if self.lifecycle:
            self._charge(len(self.metadata)*len(context))
            closest=min((m for m in self.metadata.values() if m.state in {'ACTIVE','REVIVED','SLEEP'}),key=lambda m:np.linalg.norm(context-m.key))
            if closest.state=='SLEEP':
                self._make_room();self._transition(closest.identity,'REVIVED')
        active=[m for m in self.metadata.values() if m.state in {'ACTIVE','REVIVED'}]
        self._charge(len(active)*(len(features)+len(context)))
        distances=np.array([np.sum((context-m.key)**2) for m in active])
        weights=np.exp(-(distances-distances.min())/2);weights/=weights.sum()
        moments=[self.models[m.identity].moments(features) for m in active]
        self.costs['expert_predictions']+=len(moments)
        weights,mean,variance=mixture_moments(weights,np.array([mu for mu,var in moments]),np.array([var for mu,var in moments]))
        variance=max(.05,variance)
        base=(mean,variance);selected=active[int(weights.argmax())].identity
        candidates=[e for e in self.engrams if e.written_at<self.t]
        retrieved=None
        if self.memory_enabled and candidates:
            self._charge(len(candidates)*len(context));self.costs['retrieval_distances']+=len(candidates)
            if self.retrieval=='random':retrieved=candidates[int(self.rng.integers(len(candidates)))]
            elif self.retrieval=='recent':retrieved=max(candidates,key=lambda e:e.written_at)
            else:retrieved=min(candidates,key=lambda e:np.sum((context-e.key)**2))
            retrieved.accesses+=1
            _,mean,variance=mixture_moments(np.array([.65,.35]),np.array([base[0],retrieved.value]),np.array([base[1],retrieved.variance]))
            variance=max(.05,variance)
        warm={}
        for identity,m in self.metadata.items():
            if m.state=='WARMUP' and m.birth<self.t:
                self._charge(len(features));self.costs['expert_predictions']+=1
                warm[identity]=self.models[identity].moments(features)
        self.pending={'time':self.t,'context':context,'features':features,'code':code,'mean':mean,'variance':variance,
                      'base':base,'selected':selected,'memory_id':retrieved.identity if retrieved else None,'warm':warm}
        return mean,variance

    def _fit(self,identity,features,y,warmup=False):
        self._charge(4*len(features));self.costs['expert_updates']+=1
        if warmup:self.costs['warmup_updates']+=1
        model=self.models[identity];optimizer=self.optimizers[identity]
        x=torch.as_tensor(features,dtype=torch.float64);prediction=model.linear(x).squeeze()
        error=y-float(prediction.detach())
        optimizer.zero_grad();((prediction-y)**2/2).backward()
        nn.utils.clip_grad_norm_(model.parameters(),5.);optimizer.step()
        with torch.no_grad():model.variance.mul_(.95).add_(.05*min(error**2,100.)).clamp_(.05,100.)
        self.metadata[identity].updates+=1

    def observe(self,y):
        if self.pending is None:raise RuntimeError('Prediction must precede observation')
        if not np.isfinite(y):raise ValueError('Finite target required')
        p=self.pending;nll=gaussian_nll(y,p['mean'],p['variance'])
        base_nll=gaussian_nll(y,*p['base'])
        if p['memory_id'] is not None:
            engram=next(e for e in self.engrams if e.identity==p['memory_id'])
            assert engram.written_at<self.t
            engram.utility_sum+=base_nll-nll;engram.utility_count+=1
        for identity,moments in p['warm'].items():
            m=self.metadata[identity];m.prospective_gain+=base_nll-gaussian_nll(y,*moments);m.prospective_count+=1
            if m.prospective_count>=self.warmup:
                if m.prospective_gain>0:self._make_room();self._transition(identity,'ACTIVE')
                else:self._transition(identity,'PRUNED')
        selected=p['selected'];self._fit(selected,p['features'],y)
        m=self.metadata[selected];m.last_used=self.t;m.key=(.95*np.array(m.key)+.05*p['context']).tolist()
        if m.state=='REVIVED':self._transition(selected,'ACTIVE')
        for identity,m in list(self.metadata.items()):
            if m.state=='WARMUP':self._fit(identity,p['features'],y,warmup=True)
            if self.lifecycle and m.state in {'ACTIVE','REVIVED'} and self.t-m.last_used>=self.sleep_after:
                active=sum(z.state in {'ACTIVE','REVIVED'} for z in self.metadata.values())
                if active>1:self._transition(identity,'SLEEP')
        self.replay.append((p['features'].copy(),float(y)))
        surprise=(y-p['base'][0])**2/p['base'][1]
        self.surprise_streak=self.surprise_streak+1 if surprise>4. else 0
        if self.lifecycle and self.surprise_streak>=3 and self.t-self.last_birth>=self.cooldown:
            identity=self._spawn(p['context'])
            if identity:
                for x,target in self.replay:self._fit(identity,x,target,warmup=True)
                self.last_birth=self.t;self.surprise_streak=0
        if self.memory_enabled:
            if len(self.engrams)>=self.capacity:
                self._charge(len(self.engrams));self.costs['consolidation_checks']+=len(self.engrams)
                victim=min(self.engrams,key=lambda e:(e.utility_sum/max(1,e.utility_count),e.written_at))
                self.engrams.remove(victim)
            self.engrams.append(Engram(self.next_engram,p['code'],p['context'].tolist(),float(y),p['base'][1],selected,self.t))
            self.next_engram+=1
        result={'time':self.t,'mean':p['mean'],'variance':p['variance'],'nll':nll,'base_nll':base_nll,
                'memory_id':p['memory_id'],'expert_id':selected,'active':sum(m.state in {'ACTIVE','REVIVED'} for m in self.metadata.values()),
                'identities':len(self.metadata),'operations':self.operations,'memory_size':len(self.engrams)}
        self.pending=None;self.t+=1
        return result

    def checkpoint(self):
        return copy.deepcopy(self)

    @classmethod
    def restore(cls,checkpoint):
        model=copy.deepcopy(checkpoint)
        model.quantizer.centers.setflags(write=False)
        return model

    def state_receipt(self):
        return {'time':self.t,'experts':{k:asdict(v) for k,v in self.metadata.items()},
                'engrams':[asdict(e) for e in self.engrams],'costs':dict(self.costs),'operations':self.operations,
                'events':copy.deepcopy(self.events),'rng':copy.deepcopy(self.rng.bit_generator.state)}
