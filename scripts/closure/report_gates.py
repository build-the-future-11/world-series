"""Reconcile interrupted diagnostic work and report the complete factorial."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from analyze_development import campaign, stats


def main():
    out=ROOT/'docs/closure';out.mkdir(exist_ok=True)
    gates={}
    for name in ['qwipii','ultron','cwlnn','wpinn']:
        path=ROOT/'campaigns/closure-20260924'/(name+'.json')
        value=json.loads(path.read_text())
        assert value['status']=='SUCCEEDED'
        assert value['identity']['script_sha256']==hashlib.sha256((ROOT/'scripts/closure/decision_gates.py').read_bytes()).hexdigest()
        assert value['identity']['protocol_sha256']==hashlib.sha256((out/'EXECUTION_PROTOCOL.md').read_bytes()).hexdigest()
        gates[name]={'path':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'summary':value['summary'] if 'summary' in value else value['rows'] if name=='qwipii' else {'failed_rollouts':len(value['failures'])}}
    cells=[]; units=defaultdict(dict); run_index=[]
    for corner,name in [('narrow4','natural-digits-v1'),('wide12','natural-digits-sensitivity-v1'),
                        ('narrow12','closure-factorial-narrow12'),('wide4','closure-factorial-wide4')]:
        runs=campaign(name);assert len(runs)==8
        for manifest,result in runs:
            seed=manifest['seed'];run_index.append({'corner':corner,'seed':seed,'run_id':manifest['run_id'],'source':manifest['source']})
            expected=54 if corner.startswith('wide') else 36
            assert len(result['trials'])==expected and len(result['rows'])==54
            for method in result['selected']:
                rows=[r for r in result['rows'] if r['method']==method and r['requested_steps']==32]
                assert len(rows)==2
                bad=sum(r['diverged'] or not r['complete'] for r in rows)
                trials=[r for r in result['trials'] if r['method']==method]
                row={'corner':corner,'seed':seed,'method':method,
                     'auc':None if bad else float(np.mean([r['gradient_step_auc'] for r in rows])),
                     'failures':bad,'tuning_failures':sum(t['score'] is None for t in trials),
                     'tuning_seconds':sum(t['wall_seconds'] for t in trials)}
                cells.append(row);units[(method,seed)][corner]=row['auc']
    summary=[]
    for corner,method in sorted({(r['corner'],r['method']) for r in cells}):
        rows=[r for r in cells if (r['corner'],r['method'])==(corner,method)];assert len(rows)==8
        summary.append({'corner':corner,'method':method,'auc':stats([r['auc'] for r in rows])['mean'],
                        'evaluation_failures':sum(r['failures'] for r in rows),'tuning_failures':sum(r['tuning_failures'] for r in rows),
                        'tuning_seconds':sum(r['tuning_seconds'] for r in rows)})
    contrasts=[]
    for method in sorted({r['method'] for r in cells}):
        pairs=[v for (m,s),v in units.items() if m==method];assert len(pairs)==8
        for label,a,b in [('grid_at4','wide4','narrow4'),('grid_at12','wide12','narrow12'),
                          ('steps_narrow','narrow12','narrow4'),('steps_wide','wide12','wide4')]:
            differences=[v[a]-v[b] if v[a] is not None and v[b] is not None else None for v in pairs]
            contrasts.append({'method':method,'contrast':label,'paired_seed_differences':differences,
                              'mean':stats(differences)['mean']})
    payload={'gates':gates,'factorial':summary,'paired_contrasts':contrasts,'per_seed':cells,'run_index':run_index,
             'scope':'Source-exposed same-host development diagnostics. No powered equivalence, novelty or independent confirmation.'}
    (out/'GATE_RESULTS.json').write_text(json.dumps(payload,indent=2,allow_nan=False)+'\n')
    lines=['# Closure diagnostics and recovered factorial','','All original studies remain unchanged. The two missing corners were completed using the same numerical source; resume verified completed cell hashes. These are exposed development tasks.','',
      '## QLearn: separate grid width from training duration','','| Method | Narrow/4 | Wide/4 | Narrow/12 | Wide/12 |','|---|---:|---:|---:|---:|']
    for method in sorted({r['method'] for r in summary}):
        values=[next(r['auc'] for r in summary if r['method']==method and r['corner']==c) for c in ['narrow4','wide4','narrow12','wide12']]
        lines.append('| '+method+' | '+' | '.join('INCOMPLETE' if v is None else f'{v:.6g}' for v in values)+' |')
    lines+=['','Lower 32-step AUC is better. All failures, measured tuning times and paired seed differences are retained in GATE_RESULTS.json. Missing required cells prevent a complete contrast; no survivor-only aggregate is substituted. Times are descriptive, not randomized equal-wall-time comparisons.',
      '', '## Other decision gates','',
      '- WFIM: per-letter multiplicative transport cancels exactly. See WFIM_BRANCH_DECISION.md. No parameter search can improve this product.',
      '- QWIPII: distinct fixed goals have no nontrivial stabilizer. Alternating repeated-label goals admit reduction, but canonicalization overhead exceeds the brute-search timing on these small cases. This establishes finite feasibility, not a novel general reasoning result.',
      '- Ultron: learned minus training-selected best-fixed completion is 0 at cap 8, 0.15278 at cap 24, and 0 at cap 53. The cap-24 nine-family descriptive bootstrap interval is [-0.11111, 0.5]. The finite-family evidence is uncertain; 72 repeated example cases are not 72 independent task families.',
      '- CWLNN: receptive-field-matched flat4 reaches approximately 1.77e-8 MSE at size 96 versus hierarchy 1.20174. The target itself uses four flat propagation steps, which explains this control advantage. The original hierarchy advantage over flat2 does not establish a hierarchy benefit. Current routing masks after coarse computation, so it does not save that computation.',
      '- WPINN: all 288 fits reconstructed and all 17 failed rows retained with weak-design singular values, ranks, conditions and spurious-term energy. These diagnostics alone do not isolate a causal reason for failure.',
      '', 'Independent confirmation and full architectural claims remain open. Exact gate artifact hashes are listed in GATE_RESULTS.json.']
    (out/'GATE_RESULTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({'factorial_runs':len(run_index),'cells':len(summary),'verified_gates':len(gates)}))


if __name__=='__main__':main()
