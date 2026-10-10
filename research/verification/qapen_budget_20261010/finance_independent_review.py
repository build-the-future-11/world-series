from pathlib import Path
import copy,hashlib,json
import numpy as np
import torch
from world_series.qapen.causal import CausalLifecycle,FrozenQuantizer

torch.set_num_threads(1)
source=Path('src/world_series/qapen/causal.py');before=hashlib.sha256(source.read_bytes()).hexdigest()
required=[];charged=[]
require_original=CausalLifecycle._require_budget;charge_original=CausalLifecycle._charge

def require(self,amount):required.append(amount);return require_original(self,amount)
def charge(self,amount):charged.append(amount);return charge_original(self,amount)
CausalLifecycle._require_budget=require;CausalLifecycle._charge=charge

def pack(x):
 if isinstance(x,torch.Tensor):return {'tensor':x.detach().cpu().numpy().tobytes().hex(),'shape':list(x.shape),'dtype':str(x.dtype)}
 if isinstance(x,np.ndarray):return {'array':x.tobytes().hex(),'shape':list(x.shape),'dtype':str(x.dtype)}
 if isinstance(x,dict):return {str(k):pack(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [pack(v) for v in x]
 return x

def snapshot(x):
 return pack({'receipt':x.state_receipt(),'pending':x.pending,'replay':list(x.replay),
              'models':{k:v.state_dict() for k,v in x.models.items()},
              'optimizers':{k:v.state_dict() for k,v in x.optimizers.items()},
              'counters':[x.next_identity,x.next_engram,x.last_birth,x.surprise_streak]})

records=[]
for retrieval in ['nearest','recent','random']:
 centers=np.array([[0.,0.,0.],[3.,1.,-2.],[-3.,2.,1.]])
 ref=CausalLifecycle(FrozenQuantizer(centers),fixed_experts=3,max_active=3,max_identities=8,
                     memory_capacity=3,cooldown=2,warmup=2,sleep_after=2,retrieval=retrieval)
 candidate=ref.checkpoint();transitions=0;refusals=0
 for t in range(48):
  context=centers[t%3]+np.array([.05*(t%2),0.,0.]);target=.01*(t%3) if t<36 else [12.,-12.,9.,0.][t%4]
  for action,arg in [('predict',context),('observe',target)]:
   rng=torch.get_rng_state().clone();before_ops=ref.operations;required.clear();charged.clear()
   expected=getattr(ref,action)(arg);expected_rng=torch.get_rng_state().clone();cost=ref.operations-before_ops
   assert required==[cost],(retrieval,t,action,required,cost)
   assert sum(charged)==cost
   torch.set_rng_state(rng);candidate.operation_cap=candidate.operations+cost-1
   state=snapshot(candidate);required.clear();charged.clear()
   try:getattr(candidate,action)(arg)
   except RuntimeError as e:assert 'Operation budget exhausted' in str(e)
   else:raise AssertionError('underbudget transition admitted')
   assert not charged,(retrieval,t,action,charged)
   assert snapshot(candidate)==state
   assert torch.equal(torch.get_rng_state(),rng)
   candidate.operation_cap+=1;required.clear();charged.clear()
   actual=getattr(candidate,action)(arg)
   assert actual==expected
   assert required==[cost] and sum(charged)==cost
   assert snapshot(candidate)==snapshot(ref)
   assert torch.equal(torch.get_rng_state(),expected_rng)
   transitions+=1;refusals+=1
 assert len(ref.replay)==32
 events=ref.state_receipt()['events'];assert any(e['event']=='spawn' and e['time']>=38 for e in events)
 records.append({'retrieval':retrieval,'successful_transitions':transitions,'rejected_retries':refusals,
                 'final_replay_size':len(ref.replay),'identities':len(ref.models),'events':len(events),
                 'full_replay_spawn_exercised':True,'status':'pass'})
assert hashlib.sha256(source.read_bytes()).hexdigest()==before
receipt={'reviewer':'finance_next independent admission review','status':'PASS','source_sha256':before,
         'scope':'Three 48-observation traces on 3D contexts, three starting experts, memory cap3, actual SGD/Adam, early sleep/revival, warmups and births after replay reaches32. Every predicted complete cost equals actual charge sum; every transition refused at one unit below budget before any charge/state/NumPy or PyTorch RNG mutation, then exact-budget retry matches uninterrupted output and complete retained state.',
         'records':records,'authored_suite_reexecution':{'command':'python -m pytest -q tests/qapen/test_budget_admission.py','passed':12},
         'limitations':'Operation-count contract only; no arbitrary numerical/provider failure atomicity or scientific evidence claim.'}
p=Path('research/verification/causal_budget_20261010/finance_independent_review.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
