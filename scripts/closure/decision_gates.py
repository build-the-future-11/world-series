"""Source-bound diagnostic gates. Never alters prior runs or awards readiness."""
import argparse
from collections import defaultdict
import fcntl
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
import traceback
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from analyze_development import campaign
from world_series.core.identity import source_identity

def dump(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')

def quotient_gate():
    from world_series.qwipii.domains import RingState
    from world_series.qwipii.group_actions import dihedral_actions
    from world_series.qwipii.canonicalize import canonicalize
    from world_series.qwipii.search import bfs, quotient_bfs, replay
    from world_series.core.budgets import Budget,BudgetLedger
    rows=[]; instances=[]
    for goal in [(0,1,2),(0,1,2,3),(0,1,2,3,4),(0,1,2,3,4,5),(0,1,0,1),(0,1,0,1,0,1)]:
        n=len(goal); states=sorted(set(itertools.permutations(goal)))
        actions=dihedral_actions(n)
        stabilizer=[name for name,act in actions if act(goal)==goal]
        keys={canonicalize(RingState(s,goal))[0].serialize() for s in states}
        sampled=states[::10] if n==6 and len(set(goal))==n else states
        for s in sampled:
            record={'goal':list(goal),'start':list(s)}
            paths=[]
            for name,fn in [('brute',bfs),('quotient',quotient_bfs)]:
                start=time.perf_counter()
                path,used,status=fn(RingState(s,goal),BudgetLedger(Budget(max_candidate_evals=10000)),10000)
                assert status=='solved' and replay(RingState(s,goal),path).tokens==goal
                record[name]={'expansions':used,'path':path,'seconds':time.perf_counter()-start}
                paths.append(path)
            assert len(paths[0])==len(paths[1])
            instances.append(record)
        subset=[r for r in instances if r['goal']==list(goal)]
        rows.append({'goal':list(goal),'states':len(states),'orbits':len(keys),'stabilizer':stabilizer,
            'cases_replayed':len(subset),'brute_expansions':sum(r['brute']['expansions'] for r in subset),
            'quotient_expansions':sum(r['quotient']['expansions'] for r in subset),
            'brute_seconds':sum(r['brute']['seconds'] for r in subset),'quotient_seconds':sum(r['quotient']['seconds'] for r in subset)})
    return {'rows':rows,'instances':instances,'scope':'Exact finite feasibility and sampled n6 distinct-goal search; no learned discovery or broad efficacy.'}

def ultron_gate():
    from world_series.evaluation.development import synthesis_cases,synthesis_attempt
    rows=[]; selected=[]; original=[]
    for manifest,result in campaign('development-v2'):
        if manifest['project']!='ultron':continue
        seed=manifest['seed'];tasks=synthesis_cases(seed);train=tasks[::2];held=tasks[1::2]
        assert [t.task_id for t in held]==result['evaluation_task_ids']
        modes=result['identical_tool_sets']
        original.extend(dict(r,seed=seed) for r in result['rows'])
        for cap in [8,24,53]:
            scores=[]
            for mode in modes:
                ts=[r for r in result['training_traces'] if r['tool']==mode and r['cap']==cap]
                assert len(ts)==len(train)
                scores.append((-np.mean([r['value'] for r in ts]),np.mean([r['candidates'] for r in ts]),modes.index(mode)))
            best=modes[min(range(len(modes)),key=lambda i:scores[i])]
            selected.append({'seed':seed,'cap':cap,'tool':best,'training_scores':scores})
            for t in held:
                for mode in modes:
                    receipt=synthesis_attempt(t,mode,cap)
                    rows.append(dict(receipt,seed=seed,cap=cap,task=t.task_id,tool=mode))
                original_row=next(r for r in result['rows'] if r['task']==t.task_id and r['condition']==f'budget{cap}' and r['method']=='learned')
                matched=next(r for r in rows if r['seed']==seed and r['cap']==cap and r['task']==t.task_id and r['tool']==original_row['selected_tool'])
                assert matched['value']==original_row['value'] and matched['candidates']==original_row['candidates']
    summary=[];rng=np.random.default_rng(240924)
    for cap in [8,24,53]:
        by_family=defaultdict(list);learned=[];fixed=[]
        for sel in selected:
            if sel['cap']!=cap:continue
            for r in rows:
                if r['seed']!=sel['seed'] or r['cap']!=cap or r['tool']!=sel['tool']:continue
                old=next(o for o in original if o['seed']==r['seed'] and o['task']==r['task'] and o['condition']==f'budget{cap}' and o['method']=='learned')
                by_family[r['task']].append(old['value']-r['value']);learned.append(old['value']);fixed.append(r['value'])
        values=np.array([np.mean(v) for k,v in sorted(by_family.items())])
        boot=rng.choice(values,size=(10000,len(values)),replace=True).mean(axis=1)
        assert len(values)==9 and len(learned)==72
        summary.append({'cap':cap,'families':9,'task_seed_cases':72,'learned_rate':float(np.mean(learned)),
            'best_fixed_rate':float(np.mean(fixed)),'difference':float(values.mean()),
            'family_bootstrap_95':np.quantile(boot,[.025,.975]).tolist(),
            'family_differences':{k:float(np.mean(v)) for k,v in sorted(by_family.items())}})
    return {'summary':summary,'selection':selected,'all_tool_rows':rows,
        'scope':'Exploratory best-fixed control on exposed semantic families; bootstrap is conditional on this finite development collection.'}

def cwlnn_gate():
    from world_series.cwlnn.graphs import GraphLevel,path_edges
    from world_series.cwlnn.model import forward_multiscale
    from world_series.cwlnn.baselines import flat_mp
    modes=['flat2','flat4','hierarchy','route0','route4','route_half','route_all']
    rows=[]
    for seed in [101,211,307,401,503,601,701,809]:
        rng=np.random.default_rng(seed)
        def graph(n):
            x=rng.normal(size=(n,4));e=path_edges(n)
            target=flat_mp(x,e,layers=4)[:,:1]+.5*x[:,:1].mean()
            features={};times={}
            for mode in modes:
                start=time.perf_counter()
                if mode.startswith('flat'):h=flat_mp(x,e,layers=int(mode[-1]))
                else:
                    budget={'hierarchy':None,'route0':0,'route4':4,'route_half':max(1,n//4),'route_all':(n+1)//2}[mode]
                    h,_=forward_multiscale(GraphLevel(x,e),route_budget=budget)
                # Identical public graph-mean access and readout width for all methods.
                features[mode]=np.column_stack([x,h,np.tile(x.mean(axis=0),(n,1)),np.ones(n)])
                times[mode]=time.perf_counter()-start
            return features,target,times
        training=[graph(24) for _ in range(12)]
        weights={}
        for mode in modes:
            x=np.concatenate([g[0][mode] for g in training]);y=np.concatenate([g[1] for g in training])
            weights[mode]=np.linalg.solve(x.T@x+.01*np.eye(x.shape[1]),x.T@y)
        for n in [24,48,96]:
            for case in range(8):
                features,target,times=graph(n)
                for mode in modes:
                    rows.append({'seed':seed,'n':n,'case':case,'method':mode,
                        'mse':float(np.mean((features[mode]@weights[mode]-target)**2)),
                        'feature_seconds':times[mode],'readout_parameters':int(weights[mode].size),
                        'coarse_rows_computed':0 if mode.startswith('flat') else (n+1)//2})
    summary=[]
    for n in [24,48,96]:
        for mode in modes:
            rs=[r for r in rows if r['n']==n and r['method']==mode]
            summary.append({'n':n,'method':mode,'graphs':len(rs),'mse':float(np.mean([r['mse'] for r in rs])),
                            'feature_seconds':float(np.mean([r['feature_seconds'] for r in rs]))})
    return {'rows':rows,'summary':summary,'scope':'Current fixed-feature attribution check. All coarse rows are computed before the route mask; no conditional computation saving is implemented.'}

def wpinn_gate():
    from world_series.wpinn.systems import make_trajectory
    from world_series.wpinn.library import library_matrix
    from world_series.wpinn.weak_form import test_functions,assemble_weak_system
    from world_series.wpinn.train import weak_only_fit
    rows=[]
    for manifest,result in campaign('development-v2'):
        if manifest['project']!='wpinn':continue
        seed=manifest['seed']
        for r in result['rows']:
            parts=r['condition'].split('/')
            k,c,noise=float(parts[0][1:]),float(parts[1][1:]),float(parts[2][5:])
            traj=make_trajectory(seed*100+1,k,c,noise)
            theta,names,scales=library_matrix(traj.observations)
            a,b=assemble_weak_system(traj.times,traj.observations[:,1],theta,test_functions(traj.times,n=6))
            singular=np.linalg.svd(a,compute_uv=False)
            if r['method']=='weak':
                coef,_,_=weak_only_fit(traj)
                assert all(abs(coef[x]-r['coefficients'][x])<1e-10 for x in coef)
            condition=float(np.linalg.cond(a))
            rows.append(dict(r,seed=seed,weak_design_singular_values=singular.tolist(),
                weak_design_condition=condition if np.isfinite(condition) else None,
                weak_matrix_rank=int(np.linalg.matrix_rank(a)),
                spurious_coefficient_energy=float(sum(r['coefficients'].get(t,0.)**2 for t in ['q2','v2','qv']))))
    assert len(rows)==288 and sum(r['value'] is None for r in rows)==17
    failures=[r for r in rows if r['value'] is None]
    return {'rows':rows,'failures':failures,'scope':'Exact fit reconstruction and exploratory conditioning diagnosis; does not infer failure cause from correlation or repair frozen data.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--gate',choices=['qwipii','ultron','cwlnn','wpinn'],required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    receipt=args.output/(args.gate+'.json')
    if receipt.exists():raise RuntimeError('Preserve existing receipt; choose a new output path')
    fn={'qwipii':quotient_gate,'ultron':ultron_gate,'cwlnn':cwlnn_gate,'wpinn':wpinn_gate}[args.gate]
    with (args.output/'worker.lock').open('a+') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        identity={'source':source_identity(ROOT),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'protocol_sha256':hashlib.sha256((ROOT/'docs/closure/EXECUTION_PROTOCOL.md').read_bytes()).hexdigest(),
                  'gate':args.gate,'protocol_state':'DRAFT_NOT_AUTHORIZED','started_unix':time.time()}
        dump(args.output/(args.gate+'-identity.json'),identity)
        start=time.perf_counter()
        try:result=fn()
        except BaseException as exc:
            dump(args.output/(args.gate+'-failure-'+str(time.time_ns())+'.json'),{'message':str(exc),'traceback':traceback.format_exc(),'identity':identity})
            raise
        result.update(identity=identity,elapsed_seconds=time.perf_counter()-start,status='SUCCEEDED',research_outcome='INCONCLUSIVE')
        dump(receipt,result)
        print(json.dumps({'gate':args.gate,'rows':len(result.get('rows',result.get('all_tool_rows',[]))),
                          'elapsed_seconds':result['elapsed_seconds'],'summary':result.get('summary',result.get('rows',[]))[:25] if args.gate!='wpinn' else {'failures':len(result['failures'])}}))

if __name__=='__main__':main()
