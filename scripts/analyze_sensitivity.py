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
    trials_count=0; trajectories_count=0; evaluation_failures=0; failed_rows=[]
    for manifest,result in campaign('natural-digits-sensitivity-v1'):
        assert len(result['trials'])==54 and len(result['rows'])==54
        assert set(result['selected'])==set(original)-{'official_celo2'}
        trials_count+=len(result['trials']); trajectories_count+=len(result['rows'])
        evaluation_failures+=sum(not r['complete'] or r['diverged'] for r in result['rows'])
        failed_rows.extend({'seed':manifest['seed'],'method':r['method'],'task_id':r.get('task_id'),
          'horizon':r['requested_steps'],'complete':r['complete'],'diverged':r['diverged']}
          for r in result['rows'] if not r['complete'] or r['diverged'])
        for row in result['rows']:
            curve=np.asarray(row['query_losses'])/row['normalization_scale']
            assert abs(float(np.trapezoid(curve))-row['gradient_step_auc'])<1e-10
        parameter_counts={r['method']:r['parameter_count'] for r in result['rows']}
        assert parameter_counts['full']==parameter_counts['reset_state']
        run_index.append({'run_id':manifest['run_id'],'seed':manifest['seed'],'source':manifest['source']})
        for trial in result['trials']:
            if trial['score'] is None:failures.append({'seed':manifest['seed'],'method':trial['method'],'trial':trial['trial'],'failure':trial['failure']})
        for method,selection in result['selected'].items():
            valid_trials=[t for t in result['trials'] if t['method']==method and t['score'] is not None]
            assert selection['score']==min(t['score'] for t in valid_trials)
            assert next(t for t in valid_trials if t['trial']==selection['trial'])['score']==selection['score']
            boundary[method][selection['trial']]+=1
        for method in result['selected']:
            rows=[r for r in result['rows'] if r['method']==method and r['requested_steps']==32]
            valid=len(rows)==2 and all(r['complete'] and not r['diverged'] for r in rows)
            groups[method].append({'seed':manifest['seed'],
              'auc':float(np.mean([r['gradient_step_auc'] for r in rows])) if valid else None,
              'accuracy':float(np.mean([r['accuracy'] for r in rows])) if valid else None,
              'final_loss':float(np.mean([r['normalized_final_loss'] for r in rows])) if valid else None})
    assert len(run_index)==8 and len({r['seed'] for r in run_index})==8
    assert trials_count==432 and trajectories_count==432
    table=[]
    for method,rows in sorted(groups.items()):
        table.append({'method':method,'seeds':len(rows),'primary_auc':original[method]['auc'],
          'sensitivity_auc':stats([r['auc'] for r in rows])['mean'],
          'sensitivity_final_loss':stats([r['final_loss'] for r in rows])['mean'],
          'sensitivity_accuracy':stats([r['accuracy'] for r in rows])['mean'],
          'selected_upper_boundary':boundary[method][5], 'selected_lower_boundary':boundary[method][0]})
    payload={'scope':'Wider-grid and 3x meta-step development sensitivity on reused tasks; not independent confirmation.',
       'expected_trials':432,'expected_evaluation_trajectories':432,'failed_tuning_trials':failures,
       'verified_trials':trials_count,'verified_trajectories':trajectories_count,
       'failed_evaluation_trajectories':evaluation_failures,'failed_evaluation_rows':failed_rows,'artifact_and_auc_audit_passed':True,
       'run_index':run_index,'per_seed':dict(groups),'table':table,'selected_trial_counts':{k:dict(v) for k,v in boundary.items()}}
    (OUT/'sensitivity.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    with (OUT/'sensitivity.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(table[0]));writer.writeheader();writer.writerows(table)
    lines=['# Selection and training-budget sensitivity','',
      'This separately declared follow-up keeps the original result unchanged. All methods receive six selection trials; meta-learning uses twelve rather than four outer steps. Tasks and seeds are reused development data, not a new holdout.',
      '',f'Completed: eight seed runs, 432 tuning trials and 432 evaluation trajectories. Failed tuning trials retained: {len(failures)}.',
      '',f'Diverged or incomplete evaluation trajectories: {evaluation_failures}. Required-cell aggregates are INCOMPLETE wherever a trajectory fails; no survivor-only mean is reported.',
      '', '| Method | Original 32-step AUC | Follow-up AUC | Follow-up accuracy | Seeds choosing upper grid edge |','|---|---:|---:|---:|---:|']
    for r in table:
        lines.append(f"| {r['method']} | {r['primary_auc']:.6g} | {r['sensitivity_auc'] if r['sensitivity_auc'] is not None else 'INCOMPLETE'} | {r['sensitivity_accuracy'] if r['sensitivity_accuracy'] is not None else 'INCOMPLETE'} | {r['selected_upper_boundary']} |")
    lines += ['', 'Lower AUC is better. Celo2 retains its original four-rate external evaluation and is excluded from this matched-six-trial table. Grid-boundary selections remain a limitation wherever shown. The follow-up simultaneously changes trial range and meta-training duration, so it cannot isolate their individual effects.',
              '', 'Per-seed values, failed trials and source-bound run IDs are in sensitivity.json. A favorable development contrast must not be promoted to a confirmatory claim.']
    (OUT/'SENSITIVITY.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'rows':table,'failed_trials':len(failures)}))

if __name__=='__main__':main()
