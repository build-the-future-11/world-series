# Architecture: one workbench, nine independently testable projects

## Status and repository decision

This is a proposed layout, not an inspection of the user's current Git repositories. Bootstrap must inventory existing work before creating or copying files. Use one new monorepo `world-series` with one installable Python package `world_series`; retain pre-existing repositories as read-only provenance sources until reviewed. Do not merge their outcome records or automatically relocate files. Nine isolated namespaces share contracts, generators and reporting, not mutable global state.

```text
world-series/
  AGENTS.md
  .cursor/rules/
  pyproject.toml
  dependency-lock-file
  src/world_series/
    __init__.py
    __main__.py
    cli.py
    core/
      contracts.py
      budgets.py
      devices.py
      seeds.py
      artifacts.py
      registry.py
      protocols.py
    data/
      families.py
      generators.py
      splits.py
      provenance.py
    evaluation/
      runner.py
      metrics.py
      uncertainty.py
      cost.py
      reports.py
    qlearn/ qapen/ qwipii/ wcode/ wfim/ wft/ wpinn/ cwlnn/ ultron/
  configs/{project}/{smoke,dev,ablation}.yaml
  tests/{core,qlearn,qapen,qwipii,wcode,wfim,wft,wpinn,cwlnn,ultron}/
  docs/projects/
  tasks/tasks.json
  sources/references.json
  experiments/registry.json
  runs/{run_id}/{manifest.json,events.jsonl,metrics.json,artifacts/}
  demos/
  tools/
```

The final holdout and its evaluation runner live outside the development-agent workspace. The repository may contain a public evaluation API and toy fixtures, not sealed answers. A path exclusion alone does not seal data.

## Minimal dependency policy

Use Python 3.11 or 3.12 after checking the available environment; select one and lock it. Use NumPy, SciPy and PyTorch for numerical work, pytest and Hypothesis for tests, Ruff and a type checker for development, and a YAML parser for static configuration. SymPy is optional for exact symbolic checks, not a prerequisite for every module. Start with explicit dataclasses and argparse; do not spend the sprint building a generic workflow framework. Use standard-library graph adjacency structures first; large graph frameworks, Ray, Kubernetes and cloud schedulers are unnecessary for the reference workbench.

Resolve actual compatible dependency versions in CORE-01 and save the lock. The documentation links to a current PyTorch documentation version; this is not a claim that that version is installed or supports every target device. Keep a pure CPU mathematical reference. Document any MPS/CUDA fallbacks rather than silently changing the evaluated system. See [D02–D05].

## Typed boundaries

`TaskSpec`: project ID, task family, public inputs, resource contract, development split ID and objective. It must not contain inaccessible evaluation answers.

`ObservationBatch`: named arrays/tensors, masks, shape metadata and source IDs. No positional tensor guessing between modules.

`ModuleRequest`: request ID, operation, input artifact references, immutable config hash, budget allocation and allowed output types.

`ModuleResult`: status, typed output artifacts, measured cost, diagnostics and verification status. Failure is a first-class value with an error code.

`ArtifactRef`: local relative path, SHA-256, producer run ID, schema version and media/type label. Resolve paths beneath the designated artifact root and reject traversal.

`EvidenceRecord`: claim ID, protocol ID, input/run hashes, metric name, raw trial references, verifier result and limitations. Agent prose is not evidence.

`Budget`: maximum training steps, wall-clock allowance, simulator calls, candidate evaluations, artifact bytes and planned memory. Hard safety requires OS/container enforcement; Python estimates are advisory. Never assert a universal laptop-memory guarantee from a polling monitor.

## Interfaces: do not force a universal forward method

Use specialized protocols: `Learner.fit_task`, `WorldModel.predict`, `InvariantEngine.propose/verify`, `ProgramSearch.solve`, `Algebra.multiply`, `SpectralTransform.encode/decode`, `LawIdentifier.fit`, `Backbone.forward`, `Orchestrator.run`. Each adapter converts a shared ModuleRequest into a project-specific request. Require round-trip serialization and explicit version checks. A PINN and a program synthesizer should not pretend to accept the same tensor just to make an architecture diagram uniform.

## Dependency graph

All nine depend on core contracts and generators. No standalone training experiment depends on the other eight implementations. Optional integration dependencies are:

```text
wfim -> wft: structured coefficient experiment, later and optional
qwipii -> wpinn: verified applicable invariance constraints
wft -> wpinn: optional spectral features/operator estimates
cwlnn -> wcode or qapen: optional encoder swap, after standalone controls
qlearn -> selected model trainers: optional controller swap
all implemented adapters -> ultron: routing, not joint end-to-end training
```

The v0.1 Ultron demo may use three real capabilities. It must report which capabilities are not implemented; it must not call dummy versions of all eight and count them as integrated research.

## Experiment API

Target commands to implement, not commands that exist in this planning package:

```bash
python -m world_series doctor
python -m world_series validate-config configs/qlearn/smoke.yaml
python -m world_series run --config configs/qlearn/smoke.yaml
python -m world_series compare --protocol experiments/registry.json --split dev
python -m world_series report --run-id REAL_RUN_ID
python -m pytest tests/core tests/qlearn -q
```

`run` creates an immutable run directory after validation, stores environment/config/input hashes, and writes crash or interruption receipts. `compare` never selects the best test seed. `report` reads artifacts, never asks a language model to invent missing numbers. A manifest's `git_head` is nullable; a content hash is not a Git commit.

## Ownership and integration

One integrator owns `core`, schemas, config conventions, dependency locks and shared CI. Module implementers own only their namespace, tests and configs. A module interface change needs a small contract change request with migration tests, not simultaneous edits by every agent. Worktrees may separate concurrent editing, but all numerical runs share one resource queue by default. Shared file ownership is more important than maximizing agent count.

CI stages: syntax/lint/type checks; core property tests; nine tiny CPU smoke suites; schema/evidence integrity; selected integration smoke. Longer training runs are explicit development jobs, never an accidental pull-request default. A study can be software-correct and scientifically negative.


---
