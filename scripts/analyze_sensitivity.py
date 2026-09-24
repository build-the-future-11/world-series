#!/usr/bin/env python3
"""Report the predeclared wider-grid follow-up without replacing primary results."""
from collections import defaultdict, Counter
import csv
import json
import numpy as np
from analyze_development import ROOT, OUT, campaign, stats

def main():
    original={r['method']:r for r in json.loads((OUT/'analysis.json').read_text())['digit_cells'] if r['horizon']==32}
    groups=defaultdict(list); boundary=defaultdict(Counter); failures=[]; run_index=[]
    for manifest,result in campaign('natural-digits-sensitivity-v1'):
        run_index.append({'run_id':manifest['run_id'],'seed':manifest['seed'],'source':manifest['source']})
        for trial in result['trials']:
            if trial['score'] is None:failures.append({'seed':manifest['seed'],'method':trial['method'],'trial':trial['trial'],'failure':trial['failure']})
        for method,selection in result['selected'].items():boundary[method][selection['trial']]+=1
        for method in result['selected']:
            rows=[r for r in result['rows'] if r['method']==method and r['requested_steps']==32]
            valid=len(rows)==2 and all(r['complete'] and not r['diverged'] for r in rows)
            groups[method].append({'seed':manifest['seed'],
              'auc':float(np.mean([r['gradient_step_auc'] for r in rows])) if valid else None,
              'accuracy':float(np.mean([r['accuracy'] for r in rows])) if valid else None,
              'final_loss':float(np.mean([r['normalized_final_loss'] for r in rows])) if valid else None})
    table=[]
    for method,rows in sorted(groups.items()):
        table.append({'method':method,'seeds':len(rows),'primary_auc':original[method]['auc'],
          'sensitivity_auc':stats([r['auc'] for r in rows])['mean'],
          'sensitivity_final_loss':stats([r['final_loss'] for r in rows])['mean'],
          'sensitivity_accuracy':stats([r['accuracy'] for r in rows])['mean'],
          'selected_upper_boundary':boundary[method][5], 'selected_lower_boundary':boundary[method][0]})
    payload={'scope':'Wider-grid and 3x meta-step development sensitivity on reused tasks; not independent confirmation.',
       'expected_trials':432,'expected_evaluation_trajectories':432,'failed_tuning_trials':failures,
       'run_index':run_index,'per_seed':dict(groups),'table':table,'selected_trial_counts':{k:dict(v) for k,v in boundary.items()}}
    (OUT/'sensitivity.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    with (OUT/'sensitivity.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
    lines=['# Selection and training-budget sensitivity','',
      'This separately declared follow-up keeps the original result unchanged. All methods receive six selection trials; meta-learning uses twelve rather than four outer steps. Tasks and seeds are reused development data, not a new holdout.',
      '',f'Completed: eight seed runs, 432 tuning trials and 432 evaluation trajectories. Failed tuning trials retained: {len(failures)}.',
      '', '| Method | Original 32-step AUC | Follow-up AUC | Follow-up accuracy | Seeds choosing upper grid edge |','|---|---:|---:|---:|---:|']
    for r in table:
        lines.append(f"| {r['method']} | {r['primary_auc']:.6g} | {r['sensitivity_auc'] if r['sensitivity_auc'] is not None else 'INCOMPLETE'} | {r['sensitivity_accuracy'] if r['sensitivity_accuracy'] is not None else 'INCOMPLETE'} | {r['selected_upper_boundary']} |")
    lines += ['', 'Lower AUC is better. Celo2 retains its original four-rate external evaluation and is excluded from this matched-six-trial table. Grid-boundary selections remain a limitation wherever shown. The follow-up simultaneously changes trial range and meta-training duration, so it cannot isolate their individual effects.',
              '', 'Per-seed values, failed trials and source-bound run IDs are in sensitivity.json. A favorable development contrast must not be promoted to a confirmatory claim.']
    (OUT/'SENSITIVITY.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'rows':table,'failed_trials':len(failures)}))

if __name__=='__main__':main()
