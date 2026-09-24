"""Audit model selection and every recorded search, then aggregate by family."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(Path(__file__).resolve().parent)]
from world_series.wcode.learned import program_pool,pack_programs,ProgramScorer,public_tensor
from world_series.wcode.dsl import ast_nodes
from wcode_study import charged_search,examples

DIRECTORY=ROOT/'campaigns/wcode-trained-v1'
OUT=ROOT/'docs/closure'


def main():
    torch.set_num_threads(1)
    summary=json.loads((DIRECTORY/'summary.json').read_text())
    assert summary['complete'] and len(summary['receipts'])==64
    pool=program_pool();batch=pack_programs([r['program'] for r in pool]);results=[];seen=set();verified_files=set()
    stored=json.loads((DIRECTORY/'dataset.json').read_text())['families']
    assert len(stored)==331 and len({tuple(r['signature']) for r in stored})==331
    for expected,actual in zip(pool,stored):
        assert expected['identity']==actual['identity'] and expected['role']==actual['role']
        assert list(expected['signature'])==actual['signature']
    parameter_counts=set();all_rows=[];checked_checkpoints=0;training_trace_rows=0
    for receipt in summary['receipts']:
        for filename,digest in receipt['files'].items():
            if filename not in verified_files:
                assert hashlib.sha256((DIRECTORY/filename).read_bytes()).hexdigest()==digest
                verified_files.add(filename)
        result=json.loads((DIRECTORY/(receipt['key']+'.json')).read_text());seed=result['seed'];mode=result['method']
        assert result['complete'] and len(result['rows'])==444
        with np.load(DIRECTORY/f'{seed}-training-data.npz') as data:
            targets=data['targets'];positions=data['selection_evaluation_positions']
        assert targets.shape==(80,32) and all(pool[int(i)]['role']=='train' for i in targets.flat)
        if result['training']:
            training=result['training'];parameter_counts.add(training['parameter_count'])
            minimum=min(c['selection_mean_rank'] for c in training['checkpoints'])
            assert training['selection_mean_rank']==minimum
            assert training['selected_step']==next(c['step'] for c in training['checkpoints'] if c['selection_mean_rank']==minimum)
            selection=[i for i,r in enumerate(pool) if r['role']=='selection']
            for checkpoint in training['checkpoints']:
                saved=torch.load(DIRECTORY/checkpoint['path'],weights_only=True)
                model=ProgramScorer(mode);model.load_state_dict(saved['state_dict'])
                with torch.no_grad():scores=model(batch,public_tensor([examples(pool,i,positions[i]) for i in selection])).numpy()
                ranks=[int(np.flatnonzero(np.argsort(-s,kind='stable')==i)[0])+1 for i,s in zip(selection,scores)]
                assert abs(np.mean(ranks)-checkpoint['selection_mean_rank'])<1e-12
                checked_checkpoints+=1
            selected=next(c for c in training['checkpoints'] if c['step']==training['selected_step'])
            model.load_state_dict(torch.load(DIRECTORY/selected['path'],weights_only=True)['state_dict'])
            with torch.no_grad():embeddings=model.encode(batch)
        orders={}
        for row in result['rows']:
            unit=(seed,mode,row['target'],row['cap']);assert unit not in seen;seen.add(unit)
            assert row['role']==pool[row['target']]['role'] and row['role'].startswith('evaluation')
            assert len(row['public_positions'])==len(set(row['public_positions']))==4
            assert row['public_positions']==positions[row['target']].tolist()
            target=row['target']
            if target not in orders:
                if mode=='uniform':order=np.arange(len(pool))
                elif mode=='length':order=np.array(sorted(range(len(pool)),key=lambda i:(ast_nodes(pool[i]['program']),i)))
                else:
                    with torch.no_grad():
                        query=model.example(public_tensor(examples(pool,target,positions[target]))[None]).mean(1)
                        if mode=='no_task':query=query*0
                        logits=torch.tanh(model.task(query))@embeddings.T/(model.width**.5)
                    order=np.argsort(-logits[0].numpy(),kind='stable')
                orders[target]=order.tolist()
            assert row['visited']==orders[target][:len(row['visited'])]
            # Re-execute all listed candidates and verifier calls; no semantic-output cache.
            replay=charged_search(pool,row['target'],row['public_positions'],row['visited'],row['cap'])
            for field in ['selected','public_fit','verified','false_public_fit','candidate_evaluations','public_interpreter_calls','verifier_calls','fuel_used']:
                assert replay[field]==row[field],(unit,field)
            assert row['candidate_evaluations']<=row['cap']
            assert row['verifier_calls']==(13 if row['public_fit'] else 0)
            all_rows.append(row)
        results.append(result)
    assert len(all_rows)==28416 and len(parameter_counts)==1
    for seed in sorted({r['seed'] for r in results}):
        traces=json.loads((DIRECTORY/f'{seed}-training-search-traces.json').read_text())['rows']
        assert len(traces)==171 and all(pool[t['target']]['role']=='train' for t in traces)
        training_trace_rows+=len(traces)
    cells=[];family_rows=[]
    grouped=defaultdict(list)
    for row in all_rows:grouped[(row['method'],row['role'],row['cap'],row['family'])].append(row)
    for (method,role,cap,family),rows in sorted(grouped.items()):
        assert len(rows)==8
        family_rows.append({'method':method,'role':role,'cap':cap,'family':family,'seeds':8,
                            'verified_rate':float(np.mean([r['verified'] for r in rows])),
                            'false_fit_rate':float(np.mean([r['false_public_fit'] for r in rows])),
                            'mean_fuel':float(np.mean([r['fuel_used'] for r in rows]))})
    for method,role,cap in sorted({(r['method'],r['role'],r['cap']) for r in all_rows}):
        rows=[r for r in all_rows if (r['method'],r['role'],r['cap'])==(method,role,cap)]
        expected=51 if role=='evaluation_family' else 60;assert len(rows)==expected*8
        cells.append({'method':method,'role':role,'cap':cap,'families':expected,'cases':len(rows),
                      'verified_rate':float(np.mean([r['verified'] for r in rows])),
                      'false_public_fit_rate':float(np.mean([r['false_public_fit'] for r in rows])),
                      'mean_candidate_evaluations':float(np.mean([r['candidate_evaluations'] for r in rows])),
                      'mean_fuel':float(np.mean([r['fuel_used'] for r in rows])),
                      'total_ranking_seconds':sum(r['ranking_seconds'] for r in rows),
                      'total_public_seconds':sum(r['public_seconds'] for r in rows),
                      'total_verification_seconds':sum(r['verification_seconds'] for r in rows)})
    rng=np.random.default_rng(240926);contrasts=[]
    for role in ['evaluation_family','evaluation_composition']:
        base={r['family']:r['verified_rate'] for r in family_rows if r['method']=='relational' and r['role']==role and r['cap']==24}
        for mode in sorted({r['method'] for r in all_rows}-{'relational'}):
            other={r['family']:r['verified_rate'] for r in family_rows if r['method']==mode and r['role']==role and r['cap']==24}
            assert base.keys()==other.keys()
            differences=np.array([base[k]-other[k] for k in sorted(base)])
            interval=np.quantile(rng.choice(differences,size=(10000,len(differences)),replace=True).mean(1),[.025,.975]).tolist()
            contrasts.append({'role':role,'control':mode,'families':len(base),'candidate_minus_control':float(differences.mean()),'descriptive_family_bootstrap95':interval})
    costs=[{k:r[k] for k in ['seed','method','training','graph_packing_seconds','embedding_seconds','embedding_cache_bytes','ranking_tasks']} for r in results]
    payload={'audit':{'passed':True,'verified_files':len(verified_files),'replayed_searches':len(all_rows),'recomputed_checkpoint_selections':checked_checkpoints,
                      'training_family_search_traces':training_trace_rows,'equal_parameter_count':next(iter(parameter_counts))},
             'identity':summary['identity'],'cells':cells,'family_rows':family_rows,'contrasts':contrasts,'costs':costs,
             'scope':'Finite-domain exposed development with family-conditional unadjusted intervals. No independent confirmation or novelty verdict.'}
    (OUT/'WCODE_RESULTS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    lines=['# Trained program-scorer results','','Eight seeds, six trained scorers and two fixed orderings. All 28,416 attempted searches are retained, including false public fits. All 144 checkpoint selection scores were recomputed from the selection partition. All trained models have the same parameter count.','',
           '| Method | Family holdout, cap 24 | Composition holdout, cap 24 |','|---|---:|---:|']
    for method in sorted({r['method'] for r in cells}):
        values=[next(r['verified_rate'] for r in cells if r['method']==method and r['cap']==24 and r['role']==role) for role in ['evaluation_family','evaluation_composition']]
        lines.append(f'| {method} | {values[0]:.4f} | {values[1]:.4f} |')
    lines+=['','The relational scorer uses six ordered AST relations and root/mean pooling. `no_relations` is the flat-graph control; `flat` is the pointwise control; `token` uses prefix-neighborhood edges. Removing root pooling is `no_hierarchy`. `no_task` cannot use public examples for ranking. Equal parameter counts do not equalize information or effective capacity in ablations.','',
      '## Primary descriptive contrasts','','| Partition | Control | Relational minus control | Family bootstrap 95% interval |','|---|---|---:|---|']
    for r in contrasts:lines.append(f"| {r['role']} | {r['control']} | {r['candidate_minus_control']:.5f} | {r['descriptive_family_bootstrap95']} |")
    lines+=['','Intervals are exploratory and unadjusted, conditional on 51 or 60 finite semantic families. Eight example/training seeds per family are averaged before resampling; they do not create new independent families. No practical-equivalence or unrestricted programming claim follows.','',
            'All-cap completion, false-fit, candidate and fuel tables; full training/selection traces; candidate-cache costs; and per-family data are in WCODE_RESULTS.json. Ranking time is shared across cap conditions and must not be summed four times. Cold-start graph/embedding costs are separate from per-task scoring; uniform/length methods require no trained encoder. All methods execute the same enumerator and fresh interpreter/verifier calls.','',
            'The common pool contains each target; unsupported programs, lists and unseen variable arities are not evaluated by this study. Compositions and depth ranges represented here remain narrow. No source-visible task is a sealed external holdout.',
            '', 'Fifteen functions overlap the earlier 18-function WCODE/Ultron collection; four are in the current evaluation-family partition. They remain in the declared endpoint and are not described as fresh independent tasks. WCODE_ULTRON_OVERLAP.json lists identities and roles.',
            '', 'For relational scoring, six seeds select step 20 and two select step 40; none select step 80. There is no simple selection-at-the-budget-edge justification for extending training to seek a positive result. WCODE_TRAINING_REPLAY.json separately records exact same-host loss/checkpoint replay for seed 2017 only.']
    (OUT/'WCODE_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(payload['audit']))


if __name__=='__main__':main()
