#!/usr/bin/env python3
"""Regenerate development tables from verified immutable campaign artifacts."""
from collections import defaultdict
import csv
import hashlib
import itertools
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/execution/development-v2'

def campaign(name):
    directory = ROOT / 'campaigns' / name
    summary = json.loads((directory / 'summary.json').read_text())
    if not summary['complete']:
        raise RuntimeError(f'Incomplete campaign: {name}')
    results = []
    for receipt in summary['cells']:
        run = ROOT / 'runs' / receipt['run_id']
        for relative, sha in receipt['file_hashes'].items():
            if hashlib.sha256((run / relative).read_bytes()).hexdigest() != sha:
                raise RuntimeError(f'Artifact changed: {run / relative}')
        manifest = json.loads((run / 'manifest.json').read_text())
        results.append((manifest, json.loads((run / 'metrics.json').read_text())))
    return results

def stats(values):
    if any(v is None or not np.isfinite(v) for v in values):
        return {'n': len(values), 'mean': None, 'std': None}
    return {'n': len(values), 'mean': float(np.mean(values)), 'std': float(np.std(values, ddof=1)) if len(values)>1 else None}

def sign_flip(values):
    x = np.asarray(values)
    threshold = abs(float(x.mean())) - 1e-12
    return sum(abs(float(np.mean(x*np.asarray(signs)))) >= threshold
               for signs in itertools.product([-1, 1], repeat=len(x))) / 2**len(x)

def write_csv(name, rows):
    with (OUT / name).open('w') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    by_cell = defaultdict(list); run_index = []; failures = []
    for manifest, result in campaign('development-v2'):
        run_index.append({'project': manifest['project'], 'seed': manifest['seed'], 'run_id': manifest['run_id'], 'source': manifest['source']})
        for row in result['summary']:
            by_cell[(manifest['project'],row['method'],row['condition'])].append(row['mean'])
            if row['failures']:
                failures.append({'project':manifest['project'],'seed':manifest['seed'],**row})
    cells = [{'project':p,'method':m,'condition':c,**stats(v)} for (p,m,c),v in sorted(by_cell.items())]
    write_csv('all_module_cells.csv', cells)
    digit_rows = []; tuning_failures = []
    for manifest, result in campaign('natural-digits-v1'):
        run_index.append({'project':'qlearn-natural','seed':manifest['seed'],'run_id':manifest['run_id'],'source':manifest['source']})
        digit_rows.extend(result['rows'])
        tuning_failures.extend({'seed':manifest['seed'],'method':r['method'],'trial':r['trial'],'failure':r['failure']}
                               for r in result['trials'] if r['score'] is None)
    external = ROOT/'campaigns/celo2/results.json'
    if external.exists(): digit_rows.extend(json.loads(external.read_text())['rows'])
    seed_groups = defaultdict(list)
    for row in digit_rows:
        seed_groups[(row['method'],row['requested_steps'],row['training_seed'])].append(row)
    seeds = []
    for (method,horizon,seed),rows in sorted(seed_groups.items()):
        valid=all(not r['diverged'] and r['complete'] for r in rows)
        seeds.append({'method':method,'horizon':horizon,'seed':seed,'attempted_tasks':len(rows),
                      'failures':sum(r['diverged'] or not r['complete'] for r in rows),
                      'auc':float(np.mean([r['gradient_step_auc'] for r in rows])) if valid else None,
                      'final_loss':float(np.mean([r['normalized_final_loss'] for r in rows])) if valid else None,
                      'accuracy':float(np.mean([r['accuracy'] for r in rows])) if valid else None,
                      'adapt_seconds':float(np.mean([r['elapsed_seconds'][-1] for r in rows]))})
    write_csv('digits_per_seed.csv',seeds)
    digit_cells=[]
    for method,horizon in sorted({(r['method'],r['horizon']) for r in seeds}):
        rs=[r for r in seeds if r['method']==method and r['horizon']==horizon]
        digit_cells.append({'method':method,'horizon':horizon,'seeds':len(rs),
          'auc':stats([r['auc'] for r in rs])['mean'],'final_loss':stats([r['final_loss'] for r in rs])['mean'],
          'accuracy':stats([r['accuracy'] for r in rs])['mean'],'adapt_seconds':stats([r['adapt_seconds'] for r in rs])['mean'],
          'failed_tasks':sum(r['failures'] for r in rs)})
    write_csv('digits_cells.csv',digit_cells)
    comparisons=[]
    full={r['seed']:r for r in seeds if r['method']=='full' and r['horizon']==32}
    for method in sorted({r['method'] for r in seeds}-{'full'}):
        other={r['seed']:r for r in seeds if r['method']==method and r['horizon']==32}
        paired=[(s,other[s]['auc']-full[s]['auc']) for s in sorted(full)
                if s in other and full[s]['auc'] is not None and other[s]['auc'] is not None]
        complete=len(paired)==8
        values=[v for s,v in paired]
        comparisons.append({'comparator':method,'n':len(paired),'seed_differences':values,
                            'comparator_minus_full_auc':float(np.mean(values)) if complete else None,
                            'p_exact':sign_flip(values) if complete else None,'p_holm':None})
    ordered=sorted([r for r in comparisons if r['p_exact'] is not None],key=lambda r:r['p_exact'])
    previous=0.
    for i,row in enumerate(ordered):
        previous=max(previous,min(1.,(len(ordered)-i)*row['p_exact']));row['p_holm']=previous
    write_csv('digits_comparisons.csv',comparisons)
    malis=[]
    for manifest,result in campaign('discrete-malis-v1'):
        run_index.append({'project':'qlearn-discrete','seed':manifest['seed'],'run_id':manifest['run_id'],'source':manifest['source']})
        for method in sorted({r['method'] for r in result['rows']}):
            rs=[r for r in result['rows'] if r['method']==method]
            malis.append({'seed':manifest['seed'],'method':method,'value':stats([r['value'] for r in rs])['mean'],
                          'actions':sum(r['attempted_actions'] for r in rs),'gradients':sum(r['gradient_evaluations'] for r in rs),
                          'rollbacks':sum(e['rollback'] for r in rs for e in r['events'])})
    write_csv('malis_per_seed.csv',malis)
    output={'protocol':'DRAFT_NOT_AUTHORIZED','run_index':run_index,'module_cells':cells,
            'module_failures':failures,'natural_tuning_failures':tuning_failures,
            'digit_cells':digit_cells,'digit_comparisons':comparisons,'malis':malis}
    (OUT/'analysis.json').write_text(json.dumps(output,indent=2,allow_nan=False)+'\n')
    lines=['# Executed development results','',
           'Development evidence only; no confirmatory or independent-replication claim. All tables are regenerated from hash-verified runs.',
           '',f'Completed run receipts: {len(run_index)}. Natural tuning failures: {len(tuning_failures)}. Module cells with integration/nonfinite failures: {len(failures)}.',
           '', '## Natural digit tasks at 32 adaptation steps','',
           '| Method | Mean step AUC | Mean final loss | Accuracy | Adaptation seconds |',
           '|---|---:|---:|---:|---:|']
    def fmt(v): return 'INCOMPLETE' if v is None else f'{v:.6g}'
    for row in digit_cells:
        if row['horizon']==32:
            lines.append('| '+row['method']+' | '+' | '.join(fmt(row[k]) for k in ['auc','final_loss','accuracy','adapt_seconds'])+' |')
    lines += ['', 'Step counts do not equalize training compute. Celo2 uses external pretrained weights and a PyTorch/JAX bridge; its time includes compilation/transfers.',
              '', '## Paired seed diagnostics','', '| Comparator | Comparator minus full AUC | Exact p | Holm p |','|---|---:|---:|---:|']
    for row in comparisons:
        lines.append('| '+row['comparator']+' | '+' | '.join(fmt(row[k]) for k in ['comparator_minus_full_auc','p_exact','p_holm'])+' |')
    lines += ['', 'Positive differences favor the full controller. Eight seed units share the same underlying dataset. Sign-flip diagnostics assume sign symmetry; these exploratory values do not authorize a superiority claim.',
              '', '## Other modules','', '| Project | Method | Condition | Mean | Seeds |','|---|---|---|---:|---:|']
    for row in cells:
        lines.append(f"| {row['project']} | {row['method']} | {row['condition']} | {fmt(row['mean'])} | {row['n']} |")
    lines += ['', 'All method/condition cells, missing values and denominators are retained in the adjacent CSV and JSON files. INCOMPLETE means at least one required seed contains a failed/nonfinite row; no finite-only mean is substituted.',
              '', 'Discrete MALIS results are in malis_per_seed.csv. They concern a phase-conditioned support-progress controller and full-state action engine, not completion of the full proposed architecture.']
    (OUT/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'runs':len(run_index),'module_cells':len(cells),'digit_cells':len(digit_cells),'tuning_failures':len(tuning_failures),'module_failure_cells':len(failures)}))

if __name__=='__main__': main()
