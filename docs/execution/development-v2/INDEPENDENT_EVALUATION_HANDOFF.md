# Independent evaluation handoff

State: BLOCKED on an independent evaluator and privately frozen protocol.
This document is a prepared handoff, not a record that an evaluator exists or a
holdout has been sealed. No external messages or submissions have been sent.

## Reviewable candidate

Use the development candidate commit identified in the campaign identity files
and the final report. The initial baseline is ae046d1; evaluation repairs and
new experiments are in 429c788. Preserve all follow-up commits and inspect the
diff before selecting a candidate for confirmation. Do not silently substitute
the newest local source for a recorded run's source hash.

Read PROTOCOL.md, RESULTS.md, CELO2_PROVENANCE.json, all_module_cells.csv,
digits_per_seed.csv, digits_comparisons.csv, malis_per_seed.csv and analysis.json.
The raw run index in analysis.json maps every result to its source and artifacts.
Original results, including failed and interrupted runs, remain under runs/.
Full source and Python dependencies are identified separately from data and
external checkpoint hashes. A development configuration is not preregistration.

## Reproduction before confirmation

1. Obtain a read-only copy of the selected source, data provenance, raw artifacts
   and dependency locks on another machine. Record OS, processor, Python,
   dependency versions, source SHA256 and Git commit. Do not use this developer's
   same-process receipts as independent evidence.
2. Run the local test suite with one numerical worker and a dedicated temporary
   directory with sufficient disk space. Preserve command output and exit code.
3. Verify every hash in each campaign receipt before inspecting results.
4. Re-run the declared development matrices with fresh output directories:
   `python scripts/run_development.py --plan configs/development-v2.json --output campaigns/independent-development`
   and the corresponding natural-digits and discrete-malis plans. Retain all
   attempted cells and failures. Copy the reviewer-produced records separately;
   never overwrite original runs or relabel them as independent.
5. For Celo2, fetch the exact official revision and pinned checkpoint described
   in CELO2_PROVENANCE.json, use its isolated dependency lock, and execute
   scripts/evaluate_celo2.py. Confirm parameter orientation, bias branch,
   dtype and the compatibility receipt before numerical comparison. Its
   pretrained compute and framework overhead are unmatched and must stay labeled.

## Confirmation protocol to freeze outside this workspace

The evaluator must choose and sign the protocol before seeing new outcomes:

- One bounded primary claim and decision rule; for QLearn, specify whether the
  target is gradient-step efficiency, wall-time efficiency or endpoint accuracy.
  Those are distinct questions. An equivalence claim requires a justified margin
  and power calculation, not a nonsignificant superiority test.
- Independently sampled datasets/task families, private seeds and whole-source
  split units. Public digit pairs and all visible synthetic tasks are development
  data. Eight repeated seeds on one dataset are not eight datasets.
- A sample-size/power justification using development variance, fixed comparator
  qualification, a hyperparameter search policy, and full compute accounting.
- A fixed hierarchy of hypotheses, uncertainty method and multiplicity policy;
  prohibit best-seed selection and post-outcome horizon/metric changes.
- Failure handling, tolerances, stopping conditions, resource limits, immutable
  receipts, and explicit forbidden claims. A failed required cell blocks a
  complete-matrix conclusion unless the protocol specified another estimator.
- Who can access the holdout and when the developer receives feedback. New
  feedback converts the exposed set into development data for later changes.

## Required reviewer receipt

Return the evaluator identity, independence statement, signed protocol hash and
freeze timestamp, candidate commit/content hash, machine/environment manifest,
dataset and checkpoint hashes, every command and exit code, complete attempted
denominators, raw artifact hashes, per-independent-unit results, deviations and
the bounded decision. This session must not populate the identity, signature,
private seeds or external verdict on the evaluator's behalf.

## Remaining scientific scope

Current studies are finite DSL search, finite word algebra, path-graph operators
and representations, linear oscillators, binary digits, causal stream memory,
and restricted tool routing. They cannot substantiate general PDE discovery,
general research agents, universal backbones, full MALIS/Q-APEN architectures,
FFT-like asymptotic speed, novel algebra, or superiority to untested papers.
