"""Trained CWLNN conditional-compute experiment with complete timing curves."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time
import traceback

import numpy as np
import torch

from world_series.cwlnn.conditional import ConditionalWorld, batch_graphs
from world_series.cwlnn.tasks import generate, prepare

SEEDS = [2707,2711,2713,2719,2729,2731,2741,2749]
TASKS = ['multiscale','diffusion']
MODELS = {
    'hierarchy_full': ('hierarchy','none'), 'flat5_full': ('flat5','none'),
    'local_full': ('local','none'), 'attention_full': ('attention','none'),
    'hierarchy_learned': ('hierarchy','learned'), 'hierarchy_norm': ('hierarchy','norm'),
    'hierarchy_hash': ('hierarchy','random'), 'flat5_learned': ('flat5','learned'),
}
FRACTIONS = [0.,.25,.5,1.]


def identity():
    files = sorted(Path('src/world_series').rglob('*.py'))+[Path(__file__),Path('docs/closure/CWLNN_PROTOCOL.md')]
    hashes = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    return {'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
            'files':hashes,'sha256':hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest()}


def datasets(seed,task_index):
    data = {}
    for role,amount,offset in [('train',32,0),('selection',8,1000)]:
        data[role] = [generate(seed*100000+task_index*10000+offset+i,24 if i%2==0 else 48,
                               'path' if (i//2)%2==0 else 'cycle',.3 if (i//4)%2==0 else .8,TASKS[task_index]) for i in range(amount)]
    data['evaluation'] = []
    for n in (96,192,384):
        for topology in ('path','cycle','tree'):
            for tau in (.3,1.2):
                for repeat in range(4):
                    index = len(data['evaluation'])
                    data['evaluation'].append(generate(seed*100000+task_index*10000+2000+index,n,topology,tau,TASKS[task_index]))
    return data


def save_data(data,out):
    metadata = {}
    for role,samples in data.items():
        values = {f'{i}_{key}':sample[key] for i,sample in enumerate(samples) for key in ('x','edges','node_id','target')}
        np.savez_compressed(out/f'{role}.npz',**values)
        metadata[role] = [{k:v for k,v in s.items() if k not in ('x','edges','node_id','target')} for s in samples]
    (out/'data.json').write_text(json.dumps(metadata,indent=2))


def select_score(model,samples):
    model.eval()
    values = []
    with torch.no_grad():
        for sample in samples:
            graph = prepare(sample)
            for fraction in (FRACTIONS if model.routing!='none' else [1.]):
                pred,_ = model(graph,fraction)
                values.append(float(np.mean((pred.numpy()-sample['target'])**2)))
    return float(np.mean(values))


def train(seed,task_index,name,data,out):
    start = time.perf_counter()
    torch.manual_seed(seed*100+task_index)
    model = ConditionalWorld(*MODELS[name]).double()
    torch.manual_seed(seed*100+task_index+1)
    optimizer = torch.optim.Adam(model.parameters(),lr=.003)
    rng = np.random.default_rng(seed*100+task_index+2)
    graphs = [prepare(s) for s in data['train']]
    losses,choices,checkpoints = [],[],[]
    for step in range(160):
        model.train()
        indices = rng.choice(len(graphs),size=4,replace=False)
        choices.append(indices.tolist())
        graph = batch_graphs([graphs[i] for i in indices])
        target = torch.tensor(np.concatenate([data['train'][i]['target'] for i in indices]))
        fraction = FRACTIONS[step%4] if model.routing!='none' else 1.
        optimizer.zero_grad()
        prediction,receipt = model(graph,fraction,explore=True)
        loss = (prediction-target).square().mean()
        if not torch.isfinite(loss):
            raise FloatingPointError('Nonfinite training loss')
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
        if step+1 in (80,160):
            score = select_score(model,data['selection'])
            path = out/f'{name}_{step+1}.pt'
            torch.save(model.state_dict(),path)
            checkpoints.append({'step':step+1,'selection_mse':score,'path':path.name,
                                'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    chosen = min(range(2),key=lambda i:checkpoints[i]['selection_mse'])
    model.load_state_dict(torch.load(out/checkpoints[chosen]['path'],weights_only=True))
    model.eval()
    record = {'model':name,'configuration':MODELS[name],'losses':losses,'batch_choices':choices,
              'checkpoints':checkpoints,'chosen':chosen,'parameters':sum(p.numel() for p in model.parameters()),
              'parameter_bytes':sum(p.numel()*p.element_size() for p in model.parameters()),
              'training_and_selection_seconds':time.perf_counter()-start}
    (out/f'{name}_training.json').write_text(json.dumps(record,indent=2))
    return model,record


def evaluate(models,samples,out,seed):
    rng = np.random.default_rng(seed+20260924)
    configs = [(name,f) for name,model in models.items() for f in (FRACTIONS if model.routing!='none' else [1.])]
    rows,predictions = [],{}
    with torch.no_grad():
        for index,sample in enumerate(samples):
            records = {}
            for name,fraction in configs:
                pred,receipt = models[name](prepare(sample),fraction)
                key = f'{name}_{fraction}_{index}'
                predictions[key] = pred.numpy()
                records[(name,fraction)] = {'model':name,'fraction':fraction,'graph_index':index,
                    'graph_seed':sample['seed'],'n':sample['n'],'topology':sample['topology'],'tau':sample['tau'],
                    'mse':float(np.mean((pred.numpy()-sample['target'])**2)), 'receipt':receipt,
                    'input_array_bytes':sum(sample[k].nbytes for k in ('x','edges','node_id')),
                    'timing_seconds':[]}
            for repeat in range(5):
                for ci in rng.permutation(len(configs)):
                    name,fraction = configs[ci]
                    started = time.perf_counter_ns()
                    pred,receipt = models[name](prepare(sample),fraction)
                    elapsed = (time.perf_counter_ns()-started)/1e9
                    records[(name,fraction)]['timing_seconds'].append(elapsed)
            for record in records.values():
                record['median_seconds'] = float(np.median(record['timing_seconds']))
                rows.append(record)
    np.savez_compressed(out/'predictions.npz',**predictions)
    (out/'evaluation.json').write_text(json.dumps(rows,indent=2))
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output',required=True)
    p.add_argument('--profile',action='store_true')
    args = p.parse_args()
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    out = Path(args.output)
    out.mkdir(parents=True,exist_ok=False)
    frozen = identity()
    (out/'identity.json').write_text(json.dumps(frozen,indent=2))
    jobs = [(2699,0)] if args.profile else [(seed,task) for seed in SEEDS for task in range(2)]
    started = time.perf_counter()
    try:
        for seed,task_index in jobs:
            assert identity()['sha256']==frozen['sha256'],'Source changed during campaign'
            cell = out/f'{seed}_{task_index}'
            cell.mkdir()
            data = datasets(seed,task_index)
            save_data(data,cell)
            models = {}
            for name in MODELS:
                model,record = train(seed,task_index,name,data,cell)
                models[name] = model
                print(json.dumps({'seed':seed,'task':TASKS[task_index],'model':name,
                                  'train_seconds':record['training_and_selection_seconds']}),flush=True)
            rows = evaluate(models,data['evaluation'],cell,seed)
            print(json.dumps({'completed':cell.name,'rows':len(rows)}),flush=True)
        (out/'complete.json').write_text(json.dumps({'cells':len(jobs),'elapsed_seconds':time.perf_counter()-started,
            'peak_process_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss},indent=2))
    except Exception:
        (out/'failure.txt').write_text(traceback.format_exc())
        raise


if __name__=='__main__':
    main()
