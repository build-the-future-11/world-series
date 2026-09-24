# Reproduce this audit

Start in `/Volumes/PRO-BLADE/World-Series`. The authored repository was clean at `83b838a47234517733da673113bf59073d24ac27`; Python source content hash `037b1c7f5ed8781c6622c07c21606b1ae84e90113fd905eeed44eae465038f16`. The audit files live outside that Git repository and are local, uncommitted deliverables.

```sh
rtk proxy env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 world-series/.venv/bin/python publication_audit/20260924/verify_collection.py
rtk proxy env PYTHONDONTWRITEBYTECODE=1 world-series/.venv/bin/python publication_audit/20260924/verify_archive.py
rtk proxy env PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 world-series/.venv/bin/python publication_audit/20260924/verify_scope.py
rtk proxy python3 publication_audit/20260924/build_registry.py
```

Tests were run from the implementation repository, serially before numerical audit checks:

```sh
rtk proxy env OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -q -p no:cacheprovider
```

Test exit code: 0; 57 tests passed; one existing autograd scalar-conversion warning. Full output is `receipts/pytest.txt`. Analysis verification exit code: 0. Archive verification exit code: 0.

The verifier recalculates saved-results analysis, checks hashes, finite search paths, source/row splits and the WFIM product identity. It does not train the full proposed architectures, redo every historical run, download datasets/weights, acquire an external evaluator or claim independent replication. Rerunning updates this audit's receipts only. The historical reports under `world-series/docs/` are not overwritten.

`build_registry.py` renders human audit judgments supplied in its data; it is not an automatic scientific classifier. Read `PROJECT_AUDITS.md` for the evidence and boundaries behind each classification. `LITERATURE_COMPARISON.md` records the manually screened primary sources and reading depth.

Supporting discovery files: `inventory.json` gives path/size/SHA256 for 4,138 primary non-runtime project files; `frozen_source_inventory.json` separately records 145 historical-source files under `.work-tmp/frozen-v1`, whose content hash matches the historical replay source. `run_index.json` includes every discovered run status; `duplicates.json` records exact file matches; `paragraph_duplicates.json` records repeated prose; `receipts/shared_tasks.json` records the cross-project semantic-task overlap. Cache/Git/runtime exclusions and lack of followed symlinks are explicit in the inventory. `verify_scope.py` also matches 320 saved digit arrays to original source rows and confirms all original primary inventoried files remain unchanged.

See `CLOSURE_PROGRAM.md` for unexecuted scientific work. Proposed experiments there must not be confused with the audit commands above.
