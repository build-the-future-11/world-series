# 04 — World-CNN Code
## Working research title
Relational Hierarchical Program Encoding for Verifier-Guided Bounded Synthesis.

The first deliverable is a coding research experiment, not a production coding agent and not a P-versus-NP result. A complete bounded language lets us measure correctness and search cost before trusting generated host code.

## Prior art and hypothesis

Program graphs already encode structural and semantic relations [R14]. DreamCoder learns programs and reusable abstractions [R15]. FunSearch's laboratory explanation illustrates evaluator-driven program search [R16]. Our candidate hypothesis is that a particular hierarchical relational encoder ranks localized candidates more efficiently than nonrelational encoders under the same enumerator and verifier. A speedup could be distribution-specific and does not imply a worst-case polynomial-time algorithm.

## Typed language and safety boundary

Start with scalar integers, booleans and bounded lists of integers. Whitelist arithmetic, comparisons, conditionals and a few total list operators such as sum, reverse, take, map with a bounded body and filter with a bounded predicate. Define overflow or arbitrary-precision behavior explicitly. No file operations, imports, network, shell, recursion or unbounded loops. Every interpretation receives fuel, maximum list length and a typed AST depth/node cap.

The interpreter must dispatch on typed AST constructors. Do not implement it using Python eval/exec. A timeout around arbitrary Python is not equivalent to a safe interpreter. Invalid types, division by zero, excessive integer size, exhausted fuel and malformed trees produce typed failures. General Python patching requires a later sandboxed runner and is not necessary for this study.

## Representation and candidate search

For program P, build a directed relational graph with AST child/parent, sibling order and permitted scope/use relations. Only claim data/control-flow edges actually defined by the DSL; do not label a simple AST as a full compiler representation. Node features include operator type, value category, scope/depth and type information. Relations have separate learned weights:

`h_v^{l+1}=σ(W_0h_v^l+Σ_r Σ_{u∈N_r(v)} W_rh_u^l/c_{v,r})`.

Pool expressions to blocks/root using sparse parent mappings. A scorer conditions on the task's public examples and returns candidate priority. It may guide beam order but cannot declare correctness. For an exhaustive bounded reference mode, ranking must not remove candidates needed for completeness. For beam search, explicitly acknowledge search incompleteness.

Use a common candidate generator across all encoder comparisons. Otherwise gains may come from proposing better programs, not from the claimed graph representation. Cache immutable AST/graph features by a canonical hash; invalidate any cache when a subtree changes.

## Correctness before efficiency

Use lexicographic selection: first satisfy the declared verification contract, then optimize cost/length. Public examples guide search. A separate verifier evaluates withheld inputs, or exhaustive finite inputs when the domain is small enough. Passing examples does not prove universal correctness. Record the exact scope: `EXHAUSTIVE_FINITE_DOMAIN`, `HELDOUT_TESTS`, or a later formal equivalence certificate.

Runtime objectives should use deterministic interpreter operations/fuel initially; very short wall-clock timing is noisy. Count parsing, graph construction, ranking, interpretation and verification. Do not reward a candidate for skipping cases or changing its own test harness. A cost penalty must never outweigh a correctness failure and make an incorrect program look better.

## Code units and shapes

| File | Responsibility |
|---|---|
| dsl.py | Frozen typed AST grammar and total semantics |
| interpreter.py | Whitelist evaluation with fuel/size limits |
| dataset.py | Target programs, public examples and source-family splits |
| graph.py | Node/edge extraction and canonical AST hashing |
| encoder.py | Relational convolution and sparse hierarchical pooling |
| search.py | Enumerative, beam and evolutionary-style bounded search |
| verifier.py | Separate finite-domain/test evaluator |
| baselines.py | Uniform/heuristic priority, token encoder and MLP encoders |
| evaluate.py | Correctness, searched candidates and total measured cost |
| adapter.py | `synthesize_dsl_program` capability |

`ProgramGraph` has node features `[V,F]`, edge index `[2,E]`, relation IDs `[E]`, parent indices `[V]` and masks. `SynthesisTask` includes input/output types and public examples, never verifier answers. `SearchResult` stores the AST, evidence ID, completeness mode and resource receipt.

## Data and leakage controls

Generate target programs with depth at most six and initially at most 64 AST nodes. Normalize commutative forms, variable names and exact syntactic identities before source-family splitting. Train and test cannot share the same target program merely with different input/output examples. Hold out operator compositions or depth ranges for transfer tests, but distinguish an unsupported grammar from failure inside the supported grammar.

Train the scorer on bounded search traces collected on development tasks. Label candidates by actual verifier progress/correctness within the development partition; do not train on final evaluation answers. Preserve unsuccessful traces so the learner sees realistic negative candidates instead of an artificially easy success-only distribution.

## Baselines and ablations

Use uniform enumeration, hand-coded length/type ordering, token-sequence encoding, graph encoding without semantic relations, and the proposed multiscale graph encoding. Keep candidate generation, examples, verifier and budget fixed. A later library-learning baseline inspired by DreamCoder may change the language/search space and must be evaluated as a distinct experiment. An external LLM baseline is optional and requires a fixed model/version, token budget, prompt and cost accounting; do not make it necessary for the core study.

Primary: verified solve rate at a fixed candidate-evaluation budget. Secondary: correct-program search cost, interpreter cost, generalization to held-out compositions, memory and failure categories. Report all tasks, including exhausted searches. Empirical `C(n)` plots describe tested distributions, not P=NP.

## Tests and Sunday slice

Test every DSL operator and type error, fuel accounting, AST hash stability, graph edge semantics, batching consistency, exhaustive search completeness on tiny grammar, verifier isolation, adversarial attempts to exceed list/integer bounds and a candidate that memorizes public examples but fails withheld cases. Compare learned and nonlearned searches on identical generated candidate pools.

Sunday demonstration: one small synthesis problem with a replayable search trace, verified output and matched baseline. Defer unrestricted repository editing, full Python semantics, compiler optimization, general NP-hard claims and self-modifying verifier code. The architecture can later become a coding-agent component once the bounded experiment establishes a useful mechanism.


---
