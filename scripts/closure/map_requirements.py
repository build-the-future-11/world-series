"""Index every checklist requirement without converting references into passes."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]
PROJECTS={'QL':'qlearn','QA':'qapen','QW':'qwipii','WC':'wcode','WF':'wfim','FT':'wft','WP':'wpinn','CW':'cwlnn','UL':'ultron'}
EXTERNAL={'UL07','R06','S10','M10','M12','P05'}
MIXED={'G11','R09','P01','P02','P03','P04','P06','P08','Z04','Z08','Z09'}
NEXT={
 'qlearn':'Complete original held optimizee-family/width/horizon protocol and full measured-cost/stability analysis; qualify missing compatible strong comparator.',
 'qapen':'Audit lifecycle/memory implementation against original delayed-cue/noise and expansion-control requirements; complete fixed-cost NLL/calibration/recovery inference.',
 'qwipii':'Repair/verify certificate domain completeness, train bounded discovery/ranking and evaluate full overhead on new whole puzzle families.',
 'wcode':'Complete original scalar/list/depth/composition coverage and full scoring/execution costs; resolve shared Ultron paper lineage.',
 'wfim':'Test the original bounded per-word coordinates/decoder effect; execute byte-matched controls if nontrivial, otherwise close with explicit evidence.',
 'wft':'Resolve original graph-weight-distribution, full-cost and distinct-contribution requirements before interpreting bounded constraint improvement as paper closure.',
 'wpinn':'Add held physical-parameter regimes and original known-support inverse-PINN/data-only controls; finish identifiability/support attribution.',
 'cwlnn':'Close receptive-field matching on arbitrary held topology or explicitly restrict only the affected comparison with justified evidence.',
 'ultron':'Execute fresh heterogeneous DSL/law/invariant family study, full training/tool cost and evidence-integrity attribution; obtain actual external verifier for independence claims.',
 'shared':'Complete this exact cross-project requirement for each retained paper; existing scoped project passes do not automatically resolve it.'}


def main():
    source=ROOT/'docs/closure/CHECKLIST_STATUS.json'
    state=json.loads(source.read_text())
    rows=[]
    for item in state['items']:
        prefix=re.match(r'[A-Z]+',item['id'])[0]
        project=PROJECTS.get(prefix,'shared')
        mode='RESOLVED_SCOPED' if item['status']=='COMPLETE' else 'EXTERNAL_REQUIRED' if item['id'] in EXTERNAL else 'LOCAL_AND_EXTERNAL' if item['id'] in MIXED else 'LOCAL_EXECUTABLE'
        rows.append({**item,'project':project,'work_class':mode,
                     'next_action':None if mode=='RESOLVED_SCOPED' else NEXT[project],
                     'completion_rule':'The exact requirement and scope above must be proved by authoritative artifacts; a reference or generated document alone is not a scientific pass.'})
    out=ROOT/'results'; out.mkdir(exist_ok=True)
    payload={'source':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
             'scope':'All 145 original checklist items retained. An index of evidence/gaps, not a readiness certificate or headline claim index.',
             'counts':{mode:sum(r['work_class']==mode for r in rows) for mode in sorted({r['work_class'] for r in rows})},'requirements':rows}
    (out/'requirement_map.json').write_text(json.dumps(payload,indent=2)+'\n')
    lines=['# Remaining requirement map','','Every original checklist item remains in results/requirement_map.json. External dependencies do not block unrelated local work.','',
           '| Class | Items |','|---|---:|']
    lines += [f'| {key} | {value} |' for key,value in payload['counts'].items()]
    lines += ['', 'The 33 resolved entries include one original-scope N/A (WP07). No shared paper-level gate is inferred from a narrow numerical pass.', '',
              '| Open item | Project | Work class | Exact requirement |','|---|---|---|---|']
    lines += [f"| {r['id']} | {r['project']} | {r['work_class']} | {r['requirement']} |" for r in rows if r['status']!='COMPLETE']
    (ROOT/'docs/closure/REMAINING_REQUIREMENTS.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(payload['counts']))


if __name__=='__main__': main()
