# Workspace scientific audit — final report (2026-09-22)

## PROJECTS COMPLETED (bounded execution)
- **world-series**: core + nine thin modules + falsify suite + 3-seed dev aggregate for priority projects
- **world_series_cursor_pack**: planning complete (not software)
- Empty placeholder dirs: nothing to complete

## PROJECTS SCIENTIFICALLY TESTABLE
- All nine namespaces at **CPU-TINY / toy** scale (class **A** with confirmation **blocked**)

## PROJECTS STILL BLOCKED
- Confirmation / publication claims (no sealed evaluator; DRAFT protocols)
- Faithful external baseline reproductions
- Empty named folders are not projects

## IMPORTANT NEGATIVE RESULTS (preserve)
1. **Q-APEN vs recent memory:** `hypothesis_supported=False` — `NOT_SUPPORTED_AT_TOY_SCALE_vs_recent_memory` (`experiments/falsification_results.json`)
2. **QWIPII** verified solve fraction **0.75** stable across 3 seeds (not 1.0)
3. **Ultron** completion **1.0** for all policies on easy tasks — **non-discriminating**; cannot claim routing gains
4. **qlearn** multiseed primary mean≈1.52 with **std≈2.64** — unstable / underpowered

## CRITICAL BUGS FIXED (this audit wave)
- Ultron verifier now fails mismatched operations (`selected_op`)
- Q-APEN metrics encode beat/lose vs recent & fixed; can emit `NOT_SUPPORTED`
- Falsification suite + canonical scripts added
- WPINN IBP sign was fixed in prior session (validated again via falsify)

## EXPERIMENTS ACTUALLY RUN
- pytest (30 tests)
- `world_series falsify --seed 0`
- `dev_multiseed` seeds 0,1,2 for qlearn, qapen, qwipii, wpinn, ultron
- Prior smoke/dev corpus under `world-series/runs/`

## EXPERIMENTS PREPARED BUT NOT RUN
- Full ablation matrix GPU/large domains
- Faithful Celo2/ELO/PETS ports
- Sealed Ultron confirmation

## NEW BASELINES / CONTROLS
- Falsify controls (query isolation, memorizer held-out, wrong tool, shuffled spectral targets, wrong conservation, recent-vs-qapen)
- Ultron op-mismatch gate

## NEW ABLATIONS
- Documented in `world-series/experiments/ABLATION_PLAN.md` with RUN_NOW classes; subset executed via falsify + evaluate paths

## CLAIMS THAT SHOULD BE REMOVED OR WEAKENED
- Any “Ultron routing improves completion”
- Any “Q-APEN beats memory controls”
- Any confirmation / novelty / Olympiad / ASI language
- Treating empty `QL/`… directories as research codebases

## TOP 10 REMAINING ACTIONS

| # | Repo | Where | Action | Why | Compute |
|---|---|---|---|---|---|
| 1 | world-series | `configs/qlearn` | Diagnose qlearn AUC instability across seeds; add divergence/failure rates to primary table | Huge std | CPU-TINY |
| 2 | world-series | `qapen/evaluate.py` + rare metrics | Report rare-regime primary separately; test if engrams help **rare** even when mean loses | Honest tradeoff | CPU-TINY |
| 3 | world-series | `ultron/tasks.py` | Add hard/adversarial tasks where wrong routing fails | Discriminating eval | CPU-TINY |
| 4 | world-series | `experiments/ABLATION_PLAN.md` | Execute remaining RUN_NOW rows with logged artifacts | Complete ablation evidence | CPU-TINY |
| 5 | world-series | baselines | Optional `inspired_by` notes for AdamW/SINDy-style; still not faithful papers | Avoid name-claim | CPU-TINY |
| 6 | world-series | git | User commit freeze for stable `git_head` in manifests | Reproducibility | CPU-TINY |
| 7 | world-series | wcode/cwlnn/wft/wfim | Add to multiseed aggregate | Coverage | CPU-MODERATE |
| 8 | world-series | external | Design sealed evaluator outside agent FS | Confirmation | CPU-TINY prep |
| 9 | world-series | docs | Keep exposition/status regenerated from `runs/` only | Anti-drift | CPU-TINY |
| 10 | placeholders | `QL/`… | Leave empty or delete only with explicit user auth | Avoid fake repos | n/a |

## Key paths
- `RESEARCH_STATUS.md`, `RESEARCH_BLOCKERS.md`, `RESEARCH_MASTER_CHECKLIST.md` (workspace root)
- `world-series/docs/SCIENTIFIC_SPEC.md`, `PAPER_AUDIT.md`, `REPRODUCIBILITY.md`
- `world-series/experiments/ABLATION_PLAN.md`, `RESULTS_SUMMARY.md`, `falsification_results.json`
