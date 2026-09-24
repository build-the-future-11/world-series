"""Replay all CWLNN predictions, selections and permutations; retain full curves."""
import hashlib
import argparse
import importlib.util
import json
from pathlib import Path

import numpy as np
import torch

from world_series.cwlnn.conditional import ConditionalWorld, permute
from world_series.cwlnn.tasks import prepare


def load_study():
    spec = importlib.util.spec_from_file_location('cwlnn_study','scripts/closure/cwlnn_study.py')
    study = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(study)
    return study


def main(replay_output=Path('campaigns/cwlnn-training-replay-v1')):
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    study = load_study()
    root = Path('campaigns/cwlnn-conditional-v1')
    complete = json.loads((root/'complete.json').read_text())
    assert complete['cells']==16
    identity = json.loads((root/'identity.json').read_text())
    for filename,digest in identity['files'].items():
        path=Path(filename)
        if path.is_absolute():
            assert path.parts[-3:-1]==('scripts','closure')
            path=Path('scripts/closure')/path.name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==digest
    ids,hashes,groups = set(),{},{}
    replayed=checkpoint_scores=0
    max_permutation_difference=0.
    rng = np.random.default_rng(270924)
    for cell in sorted(root.glob('*_*')):
        if not cell.is_dir(): continue
        seed,task_index=map(int,cell.name.split('_'))
        data=study.datasets(seed,task_index)
        metadata=json.loads((cell/'data.json').read_text())
        for role,samples in data.items():
            arrays=np.load(cell/f'{role}.npz')
            for i,sample in enumerate(samples):
                assert sample['seed'] not in ids
                ids.add(sample['seed'])
                assert metadata[role][i]=={k:v for k,v in sample.items() if k not in ('x','edges','node_id','target')}
                for key in ('x','edges','node_id','target'):
                    assert np.array_equal(arrays[f'{i}_{key}'],sample[key])
        models={}
        for name,configuration in study.MODELS.items():
            training=json.loads((cell/f'{name}_training.json').read_text())
            assert len(training['losses'])==160 and np.isfinite(training['losses']).all()
            model=ConditionalWorld(*configuration).double().eval()
            scores=[]
            for checkpoint in training['checkpoints']:
                path=cell/checkpoint['path']
                assert hashlib.sha256(path.read_bytes()).hexdigest()==checkpoint['sha256']
                model.load_state_dict(torch.load(path,weights_only=True))
                score=study.select_score(model,data['selection'])
                assert score==checkpoint['selection_mse']
                scores.append(score)
                checkpoint_scores+=1
            assert training['chosen']==int(np.argmin(scores))
            model.load_state_dict(torch.load(cell/training['checkpoints'][training['chosen']]['path'],weights_only=True))
            models[name]=model
        saved=np.load(cell/'predictions.npz')
        rows=json.loads((cell/'evaluation.json').read_text())
        assert len(rows)==1440
        with torch.no_grad():
            for row in rows:
                sample=data['evaluation'][row['graph_index']]
                graph=prepare(sample)
                model=models[row['model']]
                prediction,receipt=model(graph,row['fraction'])
                key=f"{row['model']}_{row['fraction']}_{row['graph_index']}"
                assert np.array_equal(prediction.numpy(),saved[key])
                assert receipt==row['receipt']
                assert float(np.mean((prediction.numpy()-sample['target'])**2))==row['mse']
                assert len(row['timing_seconds'])==5 and min(row['timing_seconds'])>0
                assert row['median_seconds']==float(np.median(row['timing_seconds']))
                order=torch.tensor(rng.permutation(sample['n']))
                changed,changed_receipt=model(permute(graph,order),row['fraction'])
                error=float(torch.max(torch.abs(changed-prediction[order])))
                max_permutation_difference=max(max_permutation_difference,error)
                assert error<2e-12
                assert set(changed_receipt['selected_ids'])==set(receipt['selected_ids'])
                group=(study.TASKS[task_index],row['model'],row['fraction'])
                groups.setdefault(group,[]).append({'seed':seed,**row})
                replayed+=1
        for path in cell.iterdir():
            hashes[str(path.relative_to(root))]=hashlib.sha256(path.read_bytes()).hexdigest()
        print(f'Audited {cell.name}',flush=True)
    # One full same-host training replay, not independent confirmation.
    replay_dir=Path(replay_output)
    replay_dir.mkdir(exist_ok=False)
    first=root/f'{study.SEEDS[0]}_0'
    original=json.loads((first/'hierarchy_learned_training.json').read_text())
    replay_model,replay=study.train(study.SEEDS[0],0,'hierarchy_learned',study.datasets(study.SEEDS[0],0),replay_dir)
    for key in ('losses','batch_choices','chosen'):
        assert replay[key]==original[key]
    for old,new in zip(original['checkpoints'],replay['checkpoints']):
        assert old['selection_mse']==new['selection_mse']
        a=torch.load(first/old['path'],weights_only=True)
        b=torch.load(replay_dir/new['path'],weights_only=True)
        assert all(torch.equal(a[k],b[k]) for k in a)
    summaries=[]
    for (task,model,fraction),rows in groups.items():
        seed_means=[float(np.mean([r['mse'] for r in rows if r['seed']==s])) for s in study.SEEDS]
        within=[float(np.mean([r['median_seconds']<=.003 for r in rows if r['seed']==s])) for s in study.SEEDS]
        interval=np.quantile(np.mean(rng.choice(seed_means,(10000,8)),axis=1),[.025,.975]).tolist()
        summaries.append({'task':task,'model':model,'fraction':fraction,'mean_mse':float(np.mean(seed_means)),
            'descriptive_seed_interval':interval,'seed_means':seed_means,
            'median_inference_ms':1000*float(np.median([r['median_seconds'] for r in rows])),
            'fraction_within_3ms_by_seed':within,'feasible_seeds':sum(v>=.95 for v in within),
            'primary_operating_point':fraction==(.5 if study.MODELS[model][1]!='none' else 1.),
            'mean_selected_fraction':float(np.mean([r['receipt']['selected']/r['n'] for r in rows]))})
    comparisons=[]
    for task in study.TASKS:
        selected=next(s for s in summaries if s['task']==task and s['model']=='hierarchy_learned' and s['fraction']==.5)
        for control in ('hierarchy_full','flat5_full','local_full','attention_full','hierarchy_norm','hierarchy_hash','flat5_learned'):
            baseline=next(s for s in summaries if s['task']==task and s['model']==control and s['primary_operating_point'])
            delta=np.array(selected['seed_means'])-np.array(baseline['seed_means'])
            interval=np.quantile(np.mean(rng.choice(delta,(10000,8)),axis=1),[.025,.975]).tolist()
            comparisons.append({'task':task,'control':control,'mean_paired_mse_difference':float(np.mean(delta)),
                'descriptive_seed_interval':interval,'both_feasible_all_seeds':selected['feasible_seeds']==baseline['feasible_seeds']==8})
    result={'source_identity':identity,'audit':{'predictions_replayed':replayed,'checkpoint_scores':checkpoint_scores,
        'unique_graph_ids':len(ids),'files_hashed':len(hashes),'permutations_checked':replayed,
        'max_permutation_difference':max_permutation_difference,'one_full_training_replay_exact':True},
        'summary':summaries,'paired_comparisons':comparisons,'file_hashes':hashes,'complete':complete}
    Path('docs/closure/CWLNN_RESULTS.json').write_text(json.dumps(result,indent=2))
    lines=['# CWLNN conditional routing development results','','DRAFT_NOT_AUTHORIZED for confirmation. CPU reference, finite synthetic graph tasks.','',
           '| Task | Model | Route fraction | MSE | Median ms | Feasible seeds /8 |',
           '|---|---|---:|---:|---:|---:|']
    for s in summaries:
        if s['primary_operating_point']:
            lines.append(f"| {s['task']} | {s['model']} | {s['fraction']} | {s['mean_mse']:.7g} | {s['median_inference_ms']:.4f} | {s['feasible_seeds']} |")
    lines+=['','All four budget curves, paired seed differences, raw timing lists and source hashes are retained. '
        'The routed primary point is fixed at 0.5; no held-error budget selection. Feasibility requires at least95% '
        'of72 graphs below3ms within each seed/task. Median latency alone does not establish feasibility.','',
        f'Audit: {replayed} predictions and permutations, {checkpoint_scores} selection scores, {len(ids)} disjoint graph IDs. '
        f'Maximum permutation discrepancy {max_permutation_difference:.3g}. One full160-update learned-router fit replays exactly.','',
        'Timing includes instrumented receipts, input conversion, validation, public hierarchy construction, routing and decoding. '
        'Training compute differs because full controls process all nodes. Learned routing adds49 parameters. '
        'The multiscale task is hierarchy-aligned; diffusion is not. Flat receptive-field matching is limited to training paths, '
        'not arbitrary tree groupings. No universal sparse-backbone, novelty or independent-replication claim.']
    Path('docs/closure/CWLNN_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'audit':result['audit'],'primary':[s for s in summaries if s['primary_operating_point']], 'paired':comparisons},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--replay-output',type=Path,default=Path('campaigns/cwlnn-training-replay-v1'))
    args=parser.parse_args()
    main(args.replay_output)
