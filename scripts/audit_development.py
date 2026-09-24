#!/usr/bin/env python3
"""Independent contract checks over saved artifacts (same-author, same-host audit)."""
import hashlib
import json
from pathlib import Path
import numpy as np
from analyze_development import campaign, ROOT

def audit():
    checks=[]; row_counts={}; failure_count=0
    for manifest,result in campaign('development-v2'):
        project=manifest['project']; rows=result['rows']
        row_counts[project]=row_counts.get(project,0)+len(rows)
        if project=='qapen':
            raw=result['trajectories']
            assert len(raw)==400*7
            for row in raw:
                expected=.5*np.log(2*np.pi*row['predicted_variance'])+.5*(row['observed']-row['predicted_mean'])**2/row['predicted_variance']
                assert abs(expected-row['nll'])<1e-12
            assert result['memory_reads']['context_memory']>0 and result['memory_reads']['no_memory']==0
        elif project=='qwipii':
            from world_series.qwipii.domains import RingState
            from world_series.qwipii.search import replay
            for row in rows:
                cap=int(row['condition'].split('budget')[1])
                assert row['expansions']<=cap
                if row['value']:
                    assert replay(RingState(tuple(row['start']),tuple(row['goal'])),row['path']).tokens==tuple(row['goal'])
        elif project in {'wcode','ultron'}:
            for row in rows:
                assert row['candidates']<=int(row['condition'].split('budget')[1])
                assert not row['value'] or row['public_fit']
            if project=='ultron':
                assert set(result['training_task_ids']).isdisjoint(result['evaluation_task_ids'])
                for row in rows: assert row['selected_tool'] in result['identical_tool_sets']
        elif project=='wfim':
            for row in rows:
                assert row['truncated_associative']
                if row['method'] in {'truncated','transported'}: assert row['value']<1e-20
        elif project=='wft':
            for row in rows:
                if row['method']=='oracle_true_graph': assert row['value']==0.
                if row['method']=='constrained_laplacian': assert row['min_eigenvalue_symmetric_part']>=-1e-10
        elif project=='wpinn':
            assert len(rows)==36
            assert all(row['train_id']!=row['held_id'] for row in rows)
            failure_count+=sum(row['value'] is None for row in rows)
        elif project=='cwlnn':
            assert len(rows)==96
            assert len({row['readout_parameters'] for row in rows})==1
        checks.append({'run_id':manifest['run_id'],'project':project,'passed':True})
    digit_rows=0; trial_count=0
    for manifest,result in campaign('natural-digits-v1'):
        assert len(result['trials'])==36 and len(result['rows'])==54
        assert set(result['selected'])=={'sgd','momentum','adamw','full','reset_state','no_budget','no_gates','feedforward','initialization_only'}
        trial_count+=len(result['trials']);digit_rows+=len(result['rows'])
        for row in result['rows']:
            curve=np.array(row['query_losses'])/row['normalization_scale']
            assert abs(float(np.trapezoid(curve))-row['gradient_step_auc'])<1e-10
        count={r['method']:r['parameter_count'] for r in result['rows']}
        assert count['full']==count['reset_state']
        checks.append({'run_id':manifest['run_id'],'project':'qlearn-natural','passed':True})
    for manifest,result in campaign('discrete-malis-v1'):
        assert len(result['rows'])==24
        assert all(r['attempted_actions']==32 and r['gradient_evaluations']<=32 for r in result['rows'])
        checks.append({'run_id':manifest['run_id'],'project':'qlearn-discrete','passed':True})
    external=ROOT/'campaigns/celo2'
    provenance=json.loads((ROOT/'docs/execution/development-v2/CELO2_PROVENANCE.json').read_text())
    # An artifact audit checks the qualified source bytes, not an installed runtime.
    # Full comparator execution still requires its separately pinned environment/weights.
    qualified_source=ROOT/'provenance/celo2-source/celo2_optax.py'
    if not qualified_source.exists():
        qualified_source=ROOT/'.venv-celo2/lib/python3.12/site-packages/celo2_optax.py'
    assert hashlib.sha256(qualified_source.read_bytes()).hexdigest()==provenance['source_sha256']
    result=json.loads((external/'results.json').read_text())
    assert result['weights_sha256']==provenance['weights_sha256']
    assert len(result['rows'])==48 and len(result['trials'])==32
    receipt={'checks':checks,'passed':True,'verified_runs':len(checks),'row_counts':row_counts,
      'natural_trials':trial_count,'natural_trajectories':digit_rows,'celo2_trajectories':48,
      'wpinn_failed_rollouts_retained':failure_count,
      'qualified_celo2_source':str(qualified_source.relative_to(ROOT)),
      'external_artifact_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in external.glob('*.json')},
      'scope':'Same-author same-host artifact contract audit, not independent replication'}
    output=ROOT/'docs/execution/development-v2/AUDIT_RECEIPT.json'
    output.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k not in {'checks','external_artifact_hashes'}}))

if __name__=='__main__': audit()
