"""Natural-data binary digit optimizees; whole digit pairs separated by role."""
from __future__ import annotations
import copy
from dataclasses import dataclass
import hashlib
import io
import time
from pathlib import Path
import numpy as np
import torch
from torch.func import functional_call

from world_series.core.budgets import Budget, BudgetLedger
from world_series.qlearn.regression import RegressionTask, RecurrentUpdatePolicy, MetaTrainer, adapt, fixed_adapt, trajectory_record, loss
from world_series.qlearn.regression_study import summarize, dataset_hash


@dataclass(frozen=True)
class InitializedTask(RegressionTask):
    initialization: dict | None = None

    def build(self):
        model = super().build()
        if self.initialization is not None: model.load_state_dict(self.initialization)
        return model


def natural_tasks(root, seed, width=24, size=48):
    train=np.loadtxt(root/'optdigits.tra',delimiter=',')
    test=np.loadtxt(root/'optdigits.tes',delimiter=',')
    rng=np.random.default_rng(seed)
    tasks=[]; records=[]
    for pair, role in [((0,1),'train'),((2,3),'train'),((4,5),'selection'),((6,7),'evaluation'),((8,9),'evaluation')]:
        arrays=[]; ids=[]
        for source, pool, partition in [('optdigits.tra',train,'support'),
                                         ('optdigits.tes' if role=='evaluation' else 'optdigits.tra',test if role=='evaluation' else train,'query')]:
            choices=np.flatnonzero(np.isin(pool[:,-1],pair))
            if partition=='query' and role!='evaluation': choices=np.setdiff1d(choices,ids[0])
            chosen=rng.choice(choices,size,replace=False);ids.append(chosen)
            x=torch.tensor(pool[chosen,:64]/16.,dtype=torch.float64)
            y=torch.tensor(np.where(pool[chosen,-1:]==pair[0],-1.,1.),dtype=torch.float64)
            arrays.extend([x,y])
            records.append({'role':role,'pair':list(pair),'partition':partition,'source':source,'row_ids':chosen.tolist()})
        tasks.append(RegressionTask(f'{role}/digits{pair[0]}{pair[1]}/seed{seed}',f'digits{pair[0]}{pair[1]}',seed+1_000_003,width,*arrays))
    return tasks[:2],tasks[2:3],tasks[3:],records


def train_initialization(tasks, steps, outer_steps, outer_lr, ledger):
    """Exact initialization-only meta-learning with fixed SGD inner steps."""
    model=tasks[0].build(); optimizer=torch.optim.AdamW(model.parameters(),lr=outer_lr,weight_decay=.01)
    history=[]
    for _ in range(outer_steps):
        optimizer.zero_grad(set_to_none=True); values=[]
        for task in tasks:
            parameters=dict(model.named_parameters())
            for _ in range(steps):
                ledger.consume_step()
                objective=loss(model,parameters,task.support_x,task.support_y)
                gradients=torch.autograd.grad(objective,tuple(parameters.values()),create_graph=True)
                parameters={k:p-.03*g for (k,p),g in zip(parameters.items(),gradients)}
            outer=loss(model,parameters,task.query_x,task.query_y)/task.scale
            if not torch.isfinite(outer): raise FloatingPointError('Initialization meta-training diverged')
            (outer/len(tasks)).backward();values.append(float(outer.detach()))
        torch.nn.utils.clip_grad_norm_(model.parameters(),1.,error_if_nonfinite=True);optimizer.step()
        history.append(float(np.mean(values)))
    return copy.deepcopy(model.state_dict()),history


def with_initialization(task,state):
    return InitializedTask(**task.__dict__,initialization=state)


def run_experiment(cfg, run):
    p=cfg['params'];seed=int(cfg['seed']);ledger=BudgetLedger(Budget(**cfg['budget']))
    root=Path(p['data_root']);train,selection,held,records=natural_tasks(root,seed,p['width'],p['examples'])
    run.store.write_json('digits/splits.json',records)
    tasks=train+selection+held
    arrays=io.BytesIO();np.savez_compressed(arrays,**{f'task_{i}_{f}':getattr(t,f).numpy() for i,t in enumerate(tasks) for f in ['support_x','support_y','query_x','query_y']})
    run.store.write_bytes('digits/data.npz',arrays.getvalue())
    run.store.write_json('digits/input.json',{'config':cfg,'tasks':[{'id':t.task_id,'hash':dataset_hash(t),'scale':t.scale} for t in tasks],
      'source_files':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in ['optdigits.tra','optdigits.tes']},
      'objective':'Binary +/-1 squared loss; accuracy threshold 0. No ten-class claim.',
      'scope':'Digit pair holdout and source writer split; shared dataset is not cross-dataset generalization.'})
    variants={'full':{},'reset_state':{'reset_state':True},'no_budget':{'use_budget':False},
              'no_gates':{'learn_gates':False},'feedforward':{'use_recurrence':False}}
    rates=p['rates'];outer_rates=p['outer_rates'];steps=p['train_steps'];selected={};trials=[]
    assert len(rates)==len(outer_rates)
    def score(rows):
        return float(np.mean([r['gradient_step_auc'] for r in rows])) if all(not r['diverged'] and r['complete'] for r in rows) else None
    for method in ['sgd','momentum','adamw',*variants,'initialization_only']:
        best=float('inf')
        for trial in range(len(rates)):
            ledger.consume_candidates();torch.manual_seed(seed);start=time.perf_counter()
            checkpoint=None;history=[];failure=None
            try:
                if method in variants:
                    policy=RecurrentUpdatePolicy(hidden=p['hidden'],layers=2,**variants[method]);trainer=MetaTrainer(policy,outer_rates[trial])
                    for _ in range(p['meta_steps']): history.append(trainer.step(train,steps,ledger))
                    checkpoint=trainer.checkpoint()
                    trajectories=[adapt(t,policy,steps,gradient_mode='evaluation',ledger=ledger) for t in selection]
                elif method=='initialization_only':
                    state,history=train_initialization(train,steps,p['meta_steps'],outer_rates[trial],ledger)
                    b=io.BytesIO();torch.save(state,b);checkpoint=b.getvalue()
                    trajectories=[fixed_adapt(with_initialization(t,state),'sgd',steps,.03,ledger=ledger) for t in selection]
                else: trajectories=[fixed_adapt(t,method,steps,rates[trial],ledger=ledger) for t in selection]
                rows=[trajectory_record(t,method,tr,steps) for t,tr in zip(selection,trajectories)];value=score(rows)
            except (FloatingPointError,RuntimeError) as exc:
                failure=str(exc);value=None;rows=[]
            record={'method':method,'trial':trial,'score':value,'failure':failure,'history':history,
                    'selection_rows':rows,'wall_seconds':time.perf_counter()-start}
            trials.append(record);run.store.write_json(f'digits/{method}-trial{trial}.json',record)
            if checkpoint is not None: run.store.write_bytes(f'digits/{method}-trial{trial}.pt',checkpoint)
            if value is not None and value<best:
                best=value;selected[method]={'trial':trial,'score':value,'checkpoint':checkpoint}
    rows=[]
    for method,chosen in selected.items():
        trial=chosen['trial']
        if method in variants:
            policy=RecurrentUpdatePolicy(hidden=p['hidden'],layers=2,**variants[method]);MetaTrainer(policy).restore(chosen['checkpoint'])
        elif method=='initialization_only': state=torch.load(io.BytesIO(chosen['checkpoint']),weights_only=True)
        for horizon in p['horizons']:
            for task in held:
                t=with_initialization(task,state) if method=='initialization_only' else task
                tr=adapt(t,policy,horizon,gradient_mode='evaluation',ledger=ledger) if method in variants else fixed_adapt(t,'sgd' if method=='initialization_only' else method,horizon,.03 if method=='initialization_only' else rates[trial],ledger=ledger)
                row=trajectory_record(t,method,tr,horizon);row['training_seed']=seed
                parameters=tr.parameters if method in variants else tr['parameters']
                with torch.no_grad(): prediction=functional_call(t.build(),parameters,(t.query_x,),strict=True)
                row['accuracy']=float(((prediction>=0)==(t.query_y>=0)).double().mean())
                row['parameter_count']=sum(x.numel() for x in policy.parameters()) if method in variants else None
                rows.append(row)
    result={'status':'SUCCEEDED' if len(rows)==(3+len(variants)+1)*len(p['horizons'])*len(held) else 'FAILED',
            'study':'natural-digits-v1','research_outcome':'INCONCLUSIVE','protocol_state':'DRAFT_NOT_AUTHORIZED',
            'rows':rows,'summary':summarize(rows),'trials':trials,
            'selected':{k:{x:y for x,y in v.items() if x!='checkpoint'} for k,v in selected.items()},
            'cost':ledger.snapshot(),'scope':'Natural binary digit development, full vs identical-parameter reset-state control; independent seed units share dataset.'}
    ref=run.store.write_json('digits/results.json',result)
    result['raw_artifact']={'path':ref.relative_path,'sha256':ref.sha256}
    return result
