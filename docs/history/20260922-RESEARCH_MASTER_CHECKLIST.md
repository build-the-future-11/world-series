# RESEARCH_MASTER_CHECKLIST.md

Workspace-level. Per-namespace detail lives under `world-series/`.

## world-series monorepo

- [x] research question explicit (nine mechanism questions)
- [x] hypothesis falsifiable (stated in RESEARCH_STATUS.md)
- [x] scientific spec exists (`world-series/docs/SCIENTIFIC_SPEC.md`)
- [x] model/reference implemented (thin)
- [x] data pipeline validated (synthetic generators + family splits)
- [x] no train labels in controller features (qlearn design + test)
- [x] training/eval runs (smoke/dev)
- [x] baseline implemented (toy)
- [~] ablations implemented (partial; plan exists)
- [x] smoke tests pass
- [x] run manifests / content_hash
- [x] seeds controlled (SeedBundle)
- [~] multi-seed robustness (in progress)
- [x] results stored structurally (`runs/`)
- [x] negative results preserved (not overwritten by protocol)
- [x] unsupported claims identified (PAPER_AUDIT)
- [ ] figures reproducible (minimal; no paper figures yet)
- [x] README accurate for tested commands
- [x] dependencies lockfile
- [x] canonical commands documented
- [ ] paper-code consistency (no paper)
- [ ] confirmation protocol frozen + external eval

## Placeholder dirs QL…Ultron
- [ ] anything — empty (N/A)

Legend: [x] done  [~] partial  [ ] not done
