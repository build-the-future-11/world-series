#!/usr/bin/env python3
"""Current status views derived from named, verified evidence; archive old root views."""
from pathlib import Path
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'docs/execution/development-v2'

def main():
    analysis=json.loads((REPORT/'analysis.json').read_text())
    audit=json.loads((REPORT/'AUDIT_RECEIPT.json').read_text())
    replay_path=ROOT/'campaigns/meta-training-replay-v1/summary.json'
    replay=json.loads(replay_path.read_text()) if replay_path.exists() else None
    sensitivity_path=REPORT/'sensitivity.json'
    sensitivity=json.loads(sensitivity_path.read_text()) if sensitivity_path.exists() else None
    sensitivity_text='Sensitivity follow-up has not yet been analyzed.'
    if sensitivity:
        methods={r['method']:r for r in sensitivity['table']}
        def auc(method):
            value=methods[method]['sensitivity_auc']
            return f'{value:.4f}' if value is not None else 'INCOMPLETE (failed required trajectories)'
        sensitivity_text=(f"Separate eight-seed wider-grid/longer-training follow-up: {sensitivity['verified_trials']} tuning trials and {sensitivity['verified_trajectories']} evaluation trajectories audited. "
          f"32-step mean AUC: full {auc('full')}, AdamW {auc('adamw')}, momentum {auc('momentum')}. "
          f"Failed tuning trials: {len(sensitivity['failed_tuning_trials'])}; diverged/incomplete evaluation trajectories: {sensitivity['failed_evaluation_trajectories']}. "
          'See SENSITIVITY.md for every method, failed trials and grid boundaries. Original primary results remain unchanged; reused tasks provide development evidence only.')
    replay_text=(f"{replay['replayed_trials']}/{replay['expected_trials']} trials; all exact={replay['all_exact']}"
                 if replay else 'IN PROGRESS; no completion claim')
    cards={
      'qlearn':('BENCHMARKED / INCONCLUSIVE','Eight-seed natural-digit study: 288 tuning trials, 432 trajectories; official pretrained Celo2 adds 48 trajectories. Full mean AUC 13.2809 vs SGD 11.9562, AdamW 6.4145, Celo2 7.7454 at 32 steps. No general optimizer advantage established. Discrete action prototype evaluated separately.'),
      'qapen':('BENCHMARKED / INCONCLUSIVE','New causal context-memory intervention with all/rare/ordinary/return metrics and matched prediction calls. Tradeoffs remain: single-expert memory improves overall mean; fixed ensemble improves rare-regime mean. Legacy candidate memory is write-only.'),
      'qwipii':('BENCHMARKED / INCONCLUSIVE','Canonical keys retain concrete replayable paths. Exhaustive 3/4-token regression tests pass. No quotient savings on tested distinct fixed-goal puzzles; ranking-only control performs better under the limited cap.'),
      'wcode':('BENCHMARKED / INCONCLUSIVE','Eight-seed finite-DSL matrix with honest candidate accounting. Hierarchical, flat and token heuristics tie at the 24-candidate cap. Encoders are untrained structural heuristics.'),
      'wfim':('BENCHMARKED / INCONCLUSIVE','Finite support/degree/cost matrix and an actual top-k associativity counterexample. Truncation/transport identities do not establish learned downstream benefit or new algebra.'),
      'wft':('BENCHMARKED / INCONCLUSIVE','Weighted-path noise/sample/size matrix uses matched Laplacian targets. Unit-weight and true-graph oracle baselines are distinguished. Refit at each size is not transfer.'),
      'wpinn':('BENCHMARKED / INCONCLUSIVE','Three laws and three noise levels; independent held initial conditions. All polynomial terms evaluated with bounded integration. Seventeen failed rollouts remain in denominators; affected means are absent.'),
      'cwlnn':('BENCHMARKED / INCONCLUSIVE','Matched-size trained readouts on fixed sparse representations; graph sizes 24/48/96. Aggressive routing hurts the declared residual-propagation task. No universal-backbone evidence.'),
      'ultron':('BENCHMARKED / INCONCLUSIVE','Discriminating finite-DSL routing with identical tools/caps and disjoint semantic training/evaluation families. At cap 24: learned 81.94%, cheapest 66.67%, random 58.33%, static 44.44%. Not a general agent or sealed external evaluation.'),
    }
    cards['qlearn']=(cards['qlearn'][0],cards['qlearn'][1]+' '+sensitivity_text)
    lines=['# World Series current research status','',
      'Updated 24 September 2026 from named executed campaigns. This supersedes the September 22 root status snapshot; historical copies remain in docs/history/.',
      '', '**Verdict:** Runnable and benchmarked within bounded development scopes. No full-project, novelty, independent-replication or publication-readiness certification.',
      '',f"Engineering: 57 tests passed for the development candidate; {audit['verified_runs']} main run receipts passed the artifact audit. All 64 non-QLearn cells, eight natural-digit cells and eight discrete-action cells completed.",
      '',f'Original full meta-training replay: {replay_text}. Same-host replay is not independent replication.',
      '',sensitivity_text,
      '', 'There is one implementation repository, world-series/, with nine namespaces. The nine sibling named directories remain empty placeholders; world_series_cursor_pack is planning material.',
      '', '| Module | Status | Evidence and limit |','|---|---|---|']
    for key,(status,detail) in cards.items():lines.append(f'| {key} | {status} | {detail} |')
    lines += ['', '## Evidence','',
      '- Current protocol, complete tables, CSVs, figures and draft: world-series/docs/execution/development-v2/.',
      '- Raw immutable runs: world-series/runs/; canonical campaign receipts: world-series/campaigns/.',
      '- Initial baseline commit: ae046d1. Numerical development candidate: 429c788. Later analysis/documentation commits are separate.',
      '- UCI source files, attribution and hashes: world-series/data/optdigits/.',
      '- Official Celo2 revision, weights hash and isolated dependency lock: CELO2_PROVENANCE.json and celo2-requirements.txt.',
      '', '## Remaining work','',
      'Independent confirmation is BLOCKED on an external evaluator and privately frozen protocol. The concrete handoff is INDEPENDENT_EVALUATION_HANDOFF.md. Every existing confirmation registry entry remains DRAFT_NOT_AUTHORIZED.',
      '', 'Broader model development remains open: full proposed MALIS/Q-APEN architectures, trained relational synthesis encoders, general PDE/graph/sequence workloads, and stronger cross-dataset validation. These are not completed by the bounded studies. A working manuscript exists; submission and public release have not occurred.',
      '', 'No completion percentage is assigned: software execution, narrow mathematical properties, development results and independent scientific support are separate dimensions.']
    text='\n'.join(lines)+'\n'
    history=ROOT/'docs/history';history.mkdir(exist_ok=True)
    for filename in ['RESEARCH_STATUS.md','RESEARCH_BLOCKERS.md','RESEARCH_MASTER_CHECKLIST.md','AUDIT_FINAL_REPORT.md']:
        source=ROOT.parent/filename;destination=history/('20260922-'+filename)
        if source.exists() and not destination.exists():shutil.copy2(source,destination)
    (ROOT.parent/'RESEARCH_STATUS.md').write_text(text)
    (REPORT/'CURRENT_STATUS.md').write_text(text)
    (ROOT/'docs/exposition/STATUS_TABLE.md').write_text(text)
    card_lines=['# Current module cards','','Generated from executed development-v2 evidence; see complete protocol and result tables.','']
    for key,(status,detail) in cards.items():card_lines.extend([f'## {key}',f'**{status}**',detail,''])
    (ROOT/'docs/exposition/STATUS_CARDS.md').write_text('\n'.join(card_lines)+'\n')
    ledger=['# Current claims ledger','','Every claim is bounded by PROTOCOL.md and the raw run index. Confirmation remains DRAFT_NOT_AUTHORIZED.','']
    for key,(status,detail) in cards.items():
        records=[r for r in analysis['run_index'] if r['project']==key or key=='qlearn' and r['project'].startswith('qlearn-')]
        ledger.extend([f'## {key}',f'Status: {status}',detail,'',
          'Executed evidence: '+', '.join('`runs/'+r['run_id']+'/metrics.json`' for r in records),
          'Full denominators and method/condition tables: `docs/execution/development-v2/analysis.json`.', ''])
    ledger.extend(['Historical negative evidence remains in `experiments/falsification_results.json` and original runs. Later bounded interventions do not retroactively turn those negatives into wins.',
                   'No universal-intelligence, novelty, full-architecture, sealed-evaluator or publication-readiness claim is supported.'])
    (ROOT/'docs/exposition/CLAIMS_LEDGER.md').write_text('\n'.join(ledger)+'\n')
    (ROOT.parent/'RESEARCH_BLOCKERS.md').write_text('''# Current blockers — 24 September 2026

- BLOCKED: independent evaluator, privately frozen confirmation protocol and independent replication. A concrete handoff is prepared in world-series/docs/execution/development-v2/INDEPENDENT_EVALUATION_HANDOFF.md.
- INCONCLUSIVE / negative development evidence: the full optimizer does not establish an advantage over tuned strong controls. Preserve all comparisons and failed polynomial rollouts.
- NOT_RUN: broad cross-dataset/image-sequence/PDE confirmation and full proposed architecture evaluation. Bounded prototypes do not complete those obligations.
- NOT_RUN: submission or public release. A working draft and reproducible figures exist.

Resolved in the current bounded development scope: initial Git commit, source-bound studies, multi-seed coverage of all nine namespaces, discriminating local routing tasks, actual memory intervention, expanded ablations, natural binary-digit tasks, official pretrained Celo2 comparator, initialization-only and matched-parameter recurrence controls, full-state discrete actions, verified cell-level resume, artifact audits and refreshed status views.

System temporary storage filled during execution; this task uses .work-tmp on PRO-BLADE. Other tasks' files were not deleted. See archived historical blocker snapshot for earlier conditions.
''')
    checklist='''# Current execution checklist — 24 September 2026

- [x] Preserve original source, configs, raw runs and failed receipts.
- [x] Commit initial baseline and numerical development candidate.
- [x] Repair coordinate lifting, synthesis budget accounting, WFT target mismatch and false counterexample reporting.
- [x] Add and execute eight-seed bounded studies for all nine modules.
- [x] Add natural binary-digit tasks, official Celo2, initialization-only and identical-parameter recurrence controls.
- [x] Exercise discrete optimizer/replay/loss/checkpoint/rollback actions with full optimizer-state restoration tests.
- [x] Verify completed-cell resume by hashes; retain interrupted attempts.
- [x] Audit 80 main run receipts and external comparator artifacts.
- [x] Preserve 17 failed WPINN rollouts in denominators.
- [x] Generate all-cell tables, raw-seed contrasts, figures and a working manuscript.
- [x] Prepare a concrete independent-evaluation handoff.
'''
    checklist+=('- [x]' if replay and replay['all_exact'] else '- [ ]')+' Replay all 400 original learned-policy meta-training trials exactly.\n'
    checklist+=('- [x]' if sensitivity and sensitivity['artifact_and_auc_audit_passed'] else '- [ ]')+' Execute and audit the separately declared eight-seed wider-grid sensitivity study.\n'
    checklist+='''- [ ] Independent external reproduction and privately frozen confirmation.
- [ ] Full proposed architectures and broad out-of-domain validation.
- [ ] Publication-ready claim review, submission and public release.
'''
    (ROOT.parent/'RESEARCH_MASTER_CHECKLIST.md').write_text(checklist)
    (ROOT.parent/'AUDIT_FINAL_REPORT.md').write_text(text+'\n## Audit receipt\n\nSee world-series/docs/execution/development-v2/AUDIT_RECEIPT.json for verified denominators and scope. The interrupted WPINN profile remains recorded and was replaced by a separately identified capped evaluation. No research win was fabricated.\n')
    print('Refreshed root status, blockers, checklist, audit and exposition; historical snapshots retained.')

if __name__=='__main__':main()
