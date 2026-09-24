# Trained WCODE development protocol v1

This study evaluates the originally proposed task-conditioned relational program
scorer in a finite integer DSL. It does not certify novelty, unrestricted coding,
compiler optimization, or complexity-class claims. Earlier untrained rankers and
their results are preserved. Numerical source, script, protocol, dataset and
checkpoint hashes accompany new receipts.

## Frozen dataset and roles

The enumerator contains quadratic polynomials, integer floor/modulo compositions,
cubics and threshold conditionals, all represented by the existing AST whitelist.
Finite semantics are the 17 integer inputs -8 through 8. Semantically equivalent
targets are merged using their full output signature, choosing the smallest AST
then lexicographic representation. This defines finite-domain equivalence only.
There are 331 unique candidates: 171 training families, 49 selection families,
51 evaluation families and 60 held composition families (cubics/conditionals).
The exact signatures and roles are saved before training. The candidate pool is
identical for every method and contains every target, making exhaustive recovery
possible. Four public inputs are sampled without replacement; the remaining 13
are verifier-only. No task changes roles between training seeds.

Structural candidate features include operator, literal value and depth. The
ranker receives only these AST features and public input/output pairs. It cannot
access semantic signatures or verifier answers. Dataset construction does execute
the finite grammar for deduplication and labels; that curator cost is recorded
separately and is not free candidate evaluation during search. Evaluation always
uses fresh charged interpretation, never the curator's output cache.

## Models and training

Six models share exactly the same width (24), three message rounds, trainable
parameter count and optimization schedule. The relational model has distinct
first/second/third-child-to-parent, parent-to-child and forward/backward sibling
weights. It combines root and mean pooling with a permutation-invariant learned
public-example encoder. Its pooling uses the AST hierarchy, not a separately
learned coarsening algorithm. Controls: prefix-token neighborhood encoding;
pointwise encoding; flat graph with edge types removed. Ablations remove root
pooling or task conditioning. Disabled information paths reduce effective
capacity in ablations; equal parameter counts do not assert equal function classes.

Training seeds: 2017, 2027, 2039, 2053, 2063, 2081, 2087, 2099. Each receives 80
Adam steps, learning rate 0.003, batch size 32, gradient norm cap 5. Targets are
sampled from training families with new public subsets. Cross-entropy labels the
correct canonical candidate, retaining every incorrect candidate as a negative.
Every sampled public input, target index and loss is saved. There is no target-
conditioned candidate proposal and no success-only filtering of traces.

Unfiltered uniform-search traces at cap 24 are also saved for all 171 training
families, including exhausted searches and false fits. The training objective is
supervised canonical-candidate classification, not policy-gradient learning from
those trace rewards; all incorrect pool members contribute to the softmax loss.

Select among checkpoints at steps 20, 40 and 80 by mean exact-target rank on all
49 selection families with fixed public examples. Ties choose the earlier step.
No evaluation-family labels select the checkpoint. Full-pool classification is
a training surrogate; the actual endpoint is verified synthesis completion.

## Search and endpoints

Methods use candidate caps 8, 24, 64 and 331. Add fixed hash-order enumeration and
AST-length order. Rank all candidates once using structural embeddings and the
task's public examples. Search stops at the first public-example fit; an external
finite verifier checks the remaining 13 inputs exactly once. A false public fit
is failure and is not used to rerank or try again. Exhausted caps also fail.
Store visited IDs, fuel, interpreter calls, verifier calls, selected candidate,
public-fit status, full-domain correctness and times for every attempted task.

Primary descriptive endpoint: verified completion at cap 24, reported separately
for evaluation-family and held-composition partitions. Report all other caps and
failure types. Aggregate repeated example/training seeds within each semantic
family before descriptive paired family bootstrapping (10,000 draws, seed 240926).
Do not treat repeated examples as independent new families. Intervals condition
on this finite grammar; they are not powered population or novelty claims. No
equivalence margin is fabricated after outcomes. All comparisons are exploratory.

## Cost and stopping rules

One CPU worker, float32 model computations, explicit Python interpreter fuel.
Report dataset construction/graph packing, complete training/selection, frozen
candidate embedding, per-task scoring, public interpretation and held verification
separately. Charge candidate embedding as a shared cache over the explicitly
reported evaluation tasks and disclose cold-start cost/bytes. Uniform/length
controls have no training cost. Candidate budget alone is not equal computation.
Preserve failed models/cells; missing required cells invalidate the corresponding
full aggregate. Profile one training seed first with the full 80-step schedule;
use a separate immutable output directory. Full-study wall ceiling: 1,800 seconds.
No expensive launch follows an over-ceiling profile without a revised declared
resource plan. Confirmation remains DRAFT_NOT_AUTHORIZED.
