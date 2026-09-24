"""Render the evidence-bound canonical registry and per-project audit dossiers."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
P=[]
def project(id,name,alias,state,question,claim,hypothesis,evidence,blockers,next_action,audit,negative='POSSIBLE',positive='UNSUPPORTED',arxiv='NOT APPROPRIATE YET',group='REQUIRES CORE EXPERIMENTS'):
    P.append(dict(id=id,project=name,canonical_location=str(ROOT/'world-series/src/world_series'/id),
        planning_spec=str(ROOT/'world_series_cursor_pack/docs/projects'/next(p.name for p in (ROOT/'world_series_cursor_pack/docs/projects').glob('*.md') if id in p.name)),
        aliases=[str(ROOT/alias)],scientific_state=state,research_question=question,central_claim=claim,hypothesis=hypothesis,
        current_stage='BENCHMARKED development slice; original contribution unclosed',
        manuscript_exists='Shared working draft only: world-series/docs/execution/development-v2/RESEARCH_DRAFT.md',
        code_exists=True,experiments_run=True,results_exist=True,positive_result=positive,
        reproducible='Saved-artifact and analysis verification passed; independent full reproduction absent',
        arxiv=arxiv,workshop='MAJOR WORK' if arxiv=='MAJOR WORK' else 'NOT APPROPRIATE',
        conference_journal='MAJOR WORK' if arxiv=='MAJOR WORK' else 'NOT APPROPRIATE',
        negative_result_publication=negative,evidence=evidence,primary_blocker=blockers[0],blockers=blockers,next_action=next_action,
        priority_group=group,audit=audit))

project('qlearn','Quantum Learning / MALIS','QL','E',
 'Can bounded recurrent updates conditioned on progress and remaining resources improve adaptation across held optimizee families at matched total compute?',
 'The bounded controller improves the predeclared compute-normalized adaptation objective over tuned fixed and learned optimizers.',
 'Budget features, recurrence and gates each add reproducible benefit across families and horizons after tuning and training costs are charged.',
 'Eight digit seeds: full 32-step AUC 13.2809 vs AdamW 6.41449, momentum 7.98933, SGD 11.9562, Celo2 7.74535; 288 selection trials and 432 evaluation trajectories. Follow-up: 432 trials, 16 tuning failures, 4 trajectory failures. Historical 400-trial exact-replay receipts retained; separate discrete-action prototype.',
 ['Primary intended compute-normalized benefit is untested; step-AUC shows no strong-baseline advantage.', 'One dataset, two held digit pairs, narrow width/horizon and very short meta-training.', 'Sensitivity jointly changes grid and training duration; full-policy aggregate is incomplete.', 'Independent evaluation, broader transfer, power and contribution relative to Celo2/ELO unresolved.'],
 'C04: isolate training-budget versus rate-grid sensitivity, then one frozen cross-family cost comparison; retain a scoped negative outcome if it fails.',
 {
 'A Claim reconstruction':'Learned update policy is implemented; full optimizer/curriculum/memory/architecture MALIS ambition is not. Do not substitute endpoint accuracy for the intended cost objective.',
 'B Protocol reconstruction':'Natural study: train pairs 01/23, select 45, evaluate 67/89; eight seeds; width 24; 8 training steps, 4 outer steps, evaluation at 8/16/32. Discrete study is a separate constructed-task protocol.',
 'C Evidence verification':'Campaign file hashes pass; regenerated digit tables and sensitivity outputs match byte-for-byte. Full AUC is worse than tuned AdamW. Two full-policy trajectories fail in sensitivity.',
 'D Baselines':'SGD/momentum/AdamW receive equal trial counts; official Celo2 source/weights provenance exists. External pretraining and framework overhead are unmatched. ELO comparison absent.',
 'E Statistics':'Seed-paired analysis, two task rows averaged per seed, exact sign flips and Holm adjustment are implemented. No multiplicity-adjusted general advantage. Eight seeds are not eight datasets; justified practical margin/power remain absent.',
 'F Robustness':'Larger rate grid plus 3x outer training exposes failures but confounds both interventions. No cross-dataset/model-width robustness certification.',
 'G Ablations':'Reset-state matches GRU parameter count; no-budget/no-gates/feedforward and initialization-only exist. Broader discrete MALIS components are not established by this ablation suite.',
 'H Leakage':'Source/row/role disjointness passed for 16 main/follow-up runs. Policy features use support loss/gradients; query diagnostics do not stop held adaptation. Exposed evaluation tasks were reused in sensitivity; Celo2 pretraining overlap unresolved.',
 'I Novelty':'Celo2 and ELO already address learned optimizer transfer and efficient training. A bounded-cost or stability distinction needs direct evidence; no first-in-field claim justified.',
 'J Reproducibility':'Current source hash matches archive; analysis rerun passed. Historical exact replay concerns constructed-neural training, not a newly rerun natural-data study or independent reproduction.',
 'K Manuscript':'Shared draft has methods, negative results and limitations but no stand-alone complete optimizer paper or full novelty/power analysis.',
 'L Consistency':'Negative step-AUC and instability are valuable bounded findings. They neither establish general optimizer superiority nor disprove every proposed MALIS mechanism.'
 },arxiv='MAJOR WORK',group='NEGATIVE/INCONCLUSIVE BUT POTENTIALLY PUBLISHABLE')

project('qapen','Q-APEN','QAPEN','C',
 'Do adaptive expert lifecycle and delayed-utility engram memory jointly improve prediction on returning regimes under a fixed resource budget?',
 'Quantized world ensembles with causal delayed-utility memory outperform matched fixed, adaptive-no-memory and memory-only controls.',
 'Capacity adaptation and useful retrieval each explain gains beyond recent history and a single expert.',
 'Eight 400-observation streams; seven controls; 22,400 individual prediction records. Context-memory all-stream NLL 1.14129 vs no-memory 1.34936; single-expert memory 1.10035. Rare NLL 1.61910 vs fixed 1.56712.',
 ['Full quantization, delayed utility, sleep/revive and warmup protocol are not the evaluated mechanism.', 'Only one recurring two-Gaussian schedule; equal calls do not equalize compute or parameters.', 'Single-expert memory beats multi-expert candidate overall; no lifecycle-specific benefit.'],
 'C05: verify lifecycle activation and delayed utility, then run factorial memory/capacity controls across independently varied recurrence and noise.',
 {
 'A Claim reconstruction':'Original lifecycle-plus-memory contribution is preserved. The new ContextMemory wrapper is a narrower causal intervention; original QAPENModel memory is write-only.',
 'B Protocol reconstruction':'Four cycles of 80 ordinary and 20 rare Gaussian observations; score before update; last-five-observation keys; five-neighbor retrieval; 128-memory cap; eight seeds.',
 'C Evidence verification':'Recomputed all Gaussian NLLs and per-condition means. Memory helps the no-memory comparator in all seeds, but single-expert memory wins overall in all seeds.',
 'D Baselines':'No-memory, random retrieval, single-expert memory, recent, cumulative and fixed controls exist. These are scalar prototypes; matched call counts omit unequal retrieval/spawn costs.',
 'E Statistics':'Per-seed contrasts retained; audit adds exploratory unadjusted sign flips. No schedule-level generalization, calibrated uncertainty or confirmatory family-wise inference.',
 'F Robustness':'No randomized recurrence gaps, no-shift case, delayed-cue challenge, independent noise/shift sweeps or real stream evaluation.',
 'G Ablations':'Memory and expert-cap interventions exist; quantization/delayed utility/sleep/revival are not independently tested.',
 'H Leakage':'Context uses only past observations and writes after prediction; evaluator alone records regime labels. Code spawns and immediately activates experts, so proposed subsequent-block warmup validation is absent.',
 'I Novelty':'CN-DPM already studies expanding neural expert mixtures without task boundaries. Nearest-context retrieval plus capped scalar experts does not establish a distinct delayed-utility lifecycle contribution.',
 'J Reproducibility':'Eight raw streams and prediction records are hash-bound; NLL and aggregates were independently recalculated locally. No fresh external run.',
 'K Manuscript':'Shared draft states the narrower intervention and its tradeoffs. No full Q-APEN methods/results manuscript.',
 'L Consistency':'A causal retrieval gain is partial mechanism evidence, not proof of the original joint architecture. Negative legacy results remain separate from the new wrapper.'
 })

project('qwipii','QWIPII','QWRIPII','E',
 'Can verified discovered invariants reduce reasoning/search while retaining exact correctness and replayable solutions?',
 'Verification-gated quotienting and invariant guidance improve bounded search without invalid merges.',
 'Useful problem symmetries exist, are correctly certified, and save work beyond equally budgeted ranking alone.',
 'Eight seeds, sizes 4/5/6, six instances per size, two caps, three methods. Brute and quotient tie in every reported condition; at n6/cap120 both solve 10.4167%, ranking solves 100%. Small exhaustive path-lifting tests pass.',
 ['Distinct fixed goals eliminate nontrivial stabilizer in the evaluated domain, so current study cannot establish quotient savings.', 'No learned invariant discovery with demonstrated search benefit or external reasoning benchmark.', 'Canonicalization time is not equalized by expansion caps.'],
 'C02: prove orbit/stabilizer feasibility before more runs; keep fixed-goal result, then test only an already-specified symmetry-bearing domain with verifier controls.',
 {
 'A Claim reconstruction':'Finite verified search and rational projective checks exist; quantization/RG/Olympiad reasoning are not demonstrated.',
 'B Protocol reconstruction':'Ring permutations, fixed distinct goal labels, caps 12/120; canonical keys transform full states including goals, queue keeps original coordinates.',
 'C Evidence verification':'Every solved development path replays to its original goal; caps hold; brute/quotient equality is retained. Exhaustive 3/4-token correctness tests pass.',
 'D Baselines':'Brute and Hamming ranking share transitions and caps. Ranking-only implementation is greedy priority search, not guaranteed shortest-path BFS despite its name.',
 'E Statistics':'Eight seeds repeatedly sample a small finite state space; report paired instances and overlap. Solve-rate ties do not prove equivalence over general domains.',
 'F Robustness':'Sizes 4-6 and two caps; no symmetry-breaking stress matrix, external puzzles or discovered-transform generalization.',
 'G Ablations':'Brute/quotient/ranking compare mechanisms. No learned-discovery or certificate-ablation efficacy study.',
 'H Leakage':'Goal is legitimate public search input. Whole-state canonicalization avoids board-only incorrect merges; fixed-goal setup trivializes useful symmetry. Some sampled permutations can recur across seeds.',
 'I Novelty':'Symmetry reduction and property-preserving quotient structures are longstanding. Correctness tests and fixed-goal limitations alone are insufficient novelty.',
 'J Reproducibility':'Raw starts, goals, paths and expansion counts available and replayed in this audit.',
 'K Manuscript':'Shared negative-search discussion exists; no complete correctness proof plus original reasoning result paper.',
 'L Consistency':'No-savings conclusion holds for tested fixed goals only. Exact Möbius identities are classical sanity checks; neither establishes novel intelligence.'
 },arxiv='MAJOR WORK',group='NEGATIVE/INCONCLUSIVE BUT POTENTIALLY PUBLISHABLE')

project('wcode','World-CNN Code','WCNNCODE','C',
 'Does a trained relational hierarchical program encoder improve verifier-guided synthesis at fixed search cost?',
 'The hierarchical relational representation ranks candidates more effectively than trained nonrelational controls with the same enumerator and verifier.',
 'The learned representation contributes beyond candidate length, token counts and changed search space.',
 '53 candidate ASTs collapse to 18 semantic targets; eight public-example seeds, caps 8/24/53. Token/flat/hierarchical solve rates tie at cap24 (0.666667); all solve at cap53. No trained encoder.',
 ['Scorers are fixed norms of hand-built structural features, not the intended trained encoders.', 'Only 18 repeated semantic functions with shallow grammar; no held composition/depth transfer.', 'Scoring/graph construction and verifier work need full cost accounting.'],
 'C09: train the already-specified encoder and matched controls on family-disjoint traces; stop if there is no residual benefit over length/token ordering.',
 {
 'A Claim reconstruction':'Typed DSL, graph features, interpreter and bounded enumerator are implemented; learned hierarchical relational ranking is not.',
 'B Protocol reconstruction':'Common 53-program pool; deduplicate exact behaviors on integers -8 through 8; three public inputs from -4 through 4; remaining finite inputs verify outputs.',
 'C Evidence verification':'Budget caps and aggregate tables verified; semantic identity repeats across all eight seeds. Success at full enumeration is coverage of this pool.',
 'D Baselines':'Uniform, length, token, flat and hierarchical structural heuristics share enumeration. No trained token/GNN/scorer control or faithful DreamCoder experiment.',
 'E Statistics':'Seed variation changes public examples, not the set of target functions. No 144-independent-family inference; paired family uncertainty and effect size remain required.',
 'F Robustness':'Three caps; no larger grammar, depth/composition holdout or broader program tasks.',
 'G Ablations':'Feature-norm variants exist, but cannot isolate learned relational information because all are untrained.',
 'H Leakage':'Held inputs are withheld from candidate scoring; scores intentionally ignore examples until charged candidate execution. These evaluation semantic families overlap Ultron tasks.',
 'I Novelty':'Program graphs and neural-guided library/program learning already exist (Allamanis; DreamCoder). Hand-crafted node-count features add no established scientific distinction.',
 'J Reproducibility':'Finite grammar, raw public examples and receipts enable regeneration. Test suite checks uncharged interpretation is forbidden.',
 'K Manuscript':'Only shared development paragraph/tables; no learned-method paper.',
 'L Consistency':'Structural-heuristic ties neither establish nor refute the unimplemented learned-encoder hypothesis. No general coding-agent or complexity claim.'
 },negative='WEAK')

project('wfim','World-FIM infinity','WFIM','C',
 'Can learned degree-preserving coordinates in a certified finite word algebra improve downstream compositional learning under storage limits?',
 'Learned coordinates yield useful finite-budget representations while retaining algebraic and tail guarantees.',
 'Coordinate learning changes useful representations beyond the same fixed algebra and capacity-matched vector/bilinear controls.',
 'Eight finite-support studies, degrees 2/3/4 and 12 cases each. Truncation/transport coefficient errors are numerical zero; top-k counterexample exists. Audit proves per-letter transport cancels and confirms this in 200 comparisons (max difference 3.55e-15).',
 ['Current transport is an algebra automorphism: transported multiplication equals ordinary multiplication for all nonzero letter scales.', 'No trained coordinate model, downstream task or byte-matched decoder comparison.', 'Classical identities and top-k counterexamples do not alone establish a novel contribution.'],
 'C01 completed the product-level falsification. C10: stop current transport efficacy runs; decide whether already-proposed coordinate-aware encode/decode has a nontrivial testable effect, otherwise archive the method claim and retain the library.',
 {
 'A Claim reconstruction':'Sparse word algebra and transport exist; trainable useful representation is absent. WFIM is distinct from the separate Fabric-Induced Memory repository outside this workspace.',
 'B Protocol reconstruction':'Random finite words, fixed letter scales, degrees 2/3/4; compare with exact degree projection; top-k matches term count, not stored bytes.',
 'C Evidence verification':'Raw coefficients/summary checks and deliberate top-k counterexample retained. New algebraic falsification: s(uv)=s(u)s(v), so S^-1(Sx*Sy)=x*y.',
 'D Baselines':'Degree projection/top-k/product controls exist. Same-algebra identity representation, vector/bilinear/HDC downstream controls absent.',
 'E Statistics':'Algebraic equality is a proof obligation, not a statistical win. Floating-point differences around 1e-15 cannot support an empirical representation claim.',
 'F Robustness':'Finite support/degree tests only; no learned long-composition generalization, conditioning or certified unknown-tail deployment.',
 'G Ablations':'Truncation and top-k compared; no learned-versus-identity end-to-end comparison.',
 'H Leakage':'Exact projection is the definitionally aligned target; zero error is expected. No downstream train/test split exists to audit. Unknown infinite tails cannot be inferred from stored prefixes.',
 'I Novelty':'Tensor/word algebra and signature features are established. The proposed transported algebra is isomorphic, and current scaling leaves the product unchanged.',
 'J Reproducibility':'Finite numerical checks and top-k witness reproducible locally. Algebraic no-effect proof is recorded separately from original results.',
 'K Manuscript':'Shared algebra paragraph; no original theorem or complete empirical paper.',
 'L Consistency':'Do not rename known identities as new mathematics or train an invariant product expecting new expressivity. Current proposal remains experimentally incomplete; the product-level branch has a proved no-effect limitation.'
 },negative='WEAK',group='EARLY STAGE')

project('wft','World Fourier Transform','WFT','C',
 'Do verified symmetry and cross-resolution constraints improve a learned graph spectral operator on limited/noisy data and held resolutions?',
 'The proposed constraints improve representation/prediction beyond the identical unconstrained learned-Laplacian model at matched total cost.',
 'The constraints add identifiable benefit on valid symmetries and degrade or are rejected when invalid.',
 'Eight seeds; path graphs n12/24, noise 0/.1/.5, 8/32 samples; independent test vectors. Ridge, postprocessed PSD Laplacian, unit-weight graph and true-graph oracle. Refit at each size.',
 ['Specified symmetry and cross-resolution losses are not evaluated.', 'Current task is Lx supervised operator regression, not transform transfer or missing-signal reconstruction.', 'No otherwise identical trainable learned-Laplacian baseline with constraint toggles.'],
 'C08: use the existing graph-operator question to isolate constraint effects with matched parameterization and genuinely held graphs/resolutions.',
 {
 'A Claim reconstruction':'Finite Laplacian/eigendecomposition library and supervised operator-fit slice exist; universal transform and transfer claims absent.',
 'B Protocol reconstruction':'Independent weighted path draws for each size/noise/sample cell; train Y=LX+noise; evaluate on 32 new vectors; separate fits at each size.',
 'C Evidence verification':'All raw means regenerate; PSD diagnostic and true-graph zero error are sanity properties. Oracle zero is not a learned result.',
 'D Baselines':'Ridge differs structurally from constrained postprocessing; unit-weight control is not the true graph. No parameter-identical learned Laplacian with and without novel constraints.',
 'E Statistics':'Eight random draws per condition with twelve conditions; no frozen primary condition, graph-distribution effect interval or multiplicity decision.',
 'F Robustness':'Noise, size and sample count are varied, but every topology is a path. Refit does not test frozen transfer.',
 'G Ablations':'PSD projection is compared; symmetry/cross-resolution/scale/degenerate-subspace ablations required by the proposal remain missing.',
 'H Leakage':'Test vectors are generated separately; true weights are limited to generator/oracle in this study. Oracle values must remain excluded from fair superiority claims.',
 'I Novelty':'Graph Laplacian learning predates this project. The project-specific constraint benefit has not been demonstrated.',
 'J Reproducibility':'Hash-bound rows and common CPU code available; no independent full run.',
 'K Manuscript':'Shared development paragraph/tables; no defined new transform or complete graph-learning paper.',
 'L Consistency':'Complete-basis reconstruction and PSD do not establish usefulness, FFT complexity or cross-resolution generalization.'
 },negative='WEAK')

project('wpinn','World-PINN','WPINN','C',
 'Does verified physical structure improve weak-form sparse law identification from noisy observations beyond comparable discovery methods?',
 'Valid symmetry/dissipation constraints improve support recovery or held-trajectory prediction; invalid constraints are rejected or harmful.',
 'Any benefit survives matched data, tuning, library, noise and trajectory splits without access to generator truth.',
 'Eight seeds, three oscillator laws, three noise levels, four methods: 288 fitted rollouts, 17 failures retained. Each fit has independent held initial condition; all polynomial terms are integrated.',
 ['Current candidate is weak-only fitting; no positive verified-structure method or trained neural field in the main matrix.', '17 failures prevent complete means; weak-form identifiability and sampling sensitivity unresolved.', 'Faithful WSINDy/SINDy and matched valid-structure controls absent.'],
 'C07: diagnose failure/support conditioning first, then compare verified valid structure against weak-only, WSINDy and oracle-labeled known support on whole held trajectories.',
 {
 'A Claim reconstruction':'Weak sparse oscillator identification is implemented. A general PINN/PDE-discovery architecture is not.',
 'B Protocol reconstruction':'Laws (1,0),(2,.3),(4,.8), noise 0/.02/.1, independent train/held initial conditions, q/v/q2/v2/qv library and bounded integration.',
 'C Evidence verification':'36 rows per seed, 288 total, 17 None rollout values. Recomputed means preserve missing required cells; train and held IDs differ.',
 'D Baselines':'Weak-only, derivative-based data-only, known-support oracle-assisted fit and wrong-conservation control. No faithful published WSINDy or inverse-PINN baseline.',
 'E Statistics':'Failures stay in denominators. No success-only summary permitted; primary failure-aware estimand and law/trajectory-level uncertainty not frozen.',
 'F Robustness':'Three linear laws and three noise levels; no missingness, sample-rate, nonlinear law or PDE generalization.',
 'G Ablations':'Wrong conservation is a negative control, not the proposed beneficial verified structure. Smoothing/sparsity/quadrature/valid-constraint contributions not isolated.',
 'H Leakage':'Fits consume observations; generator coefficients are evaluation truth. Same law with independent initial condition is interpolation, not held-law transfer. Known support is privileged and labeled.',
 'I Novelty':'SINDy and especially WSINDy already cover sparse/weak discovery from noisy data. Merely using integration by parts is insufficient novelty.',
 'J Reproducibility':'Raw coefficients and trajectories/configuration are reconstructable; local tests verify nonlinear terms are not dropped. Numerical failures are scientific evidence, not an infrastructure blocker.',
 'K Manuscript':'Shared draft acknowledges failures and ODE limits; no complete physical-structure contribution paper.',
 'L Consistency':'Harm from imposing conservation on damped systems is expected and does not establish the positive constraint mechanism. Preserve every failed fit.'
 })

project('cwlnn','CWLNN','CWLNN','E',
 'Can sparse multiscale processing and budgeted routing improve the error/latency tradeoff on held graph sizes?',
 'Routed hierarchy improves performance under a declared inference budget while retaining valid permutation and scaling behavior.',
 'Savings from routing outweigh accuracy loss after hierarchy construction, training and decoding are counted.',
 'Eight seeds, 12 training path graphs n24, eight evaluation graphs each at n24/48/96, four representations and equal-sized ridge readouts. At n96: hierarchy MSE 1.20434, flat 2.11086, routed 13.6939, attention 33.4272.',
 ['Aggressive route budget 4 degrades accuracy; no matched inference-cost frontier proves compensation.', 'Features are fixed, readouts trained; no learned routing/universal backbone result.', 'One path topology and one residual-propagation target; limited task diversity.'],
 'C06: sweep the existing routing budget against matched-depth flat/unrouted controls, including hierarchy construction cost and nonhierarchical tasks; stop if dominated.',
 {
 'A Claim reconstruction':'Sparse local/coarse/routed reference features exist; the original learnable universal backbone remains unimplemented at claimed scope.',
 'B Protocol reconstruction':'Training at n24, frozen ridge readouts at n24/48/96, target (I+P)^4 X plus graph mean, route budget 4.',
 'C Evidence verification':'768 raw graph/method rows aggregate correctly. Unrouted hierarchy beats flat on this target, but routing is much worse in every n96 seed.',
 'D Baselines':'Readout parameter counts match; underlying features/receptive field and preprocessing work differ. Flat default has fewer propagation steps than target. Attention cap limits usable interactions.',
 'E Statistics':'Nodes share graphs and graphs share trained readouts. Use training seeds/graph families, not every node as independent. No accuracy-cost superiority interval.',
 'F Robustness':'Readout transfers to larger path sizes; no topology transfer, broad node relabeling study or wall-time-controlled workload matrix.',
 'G Ablations':'Flat, hierarchy, routed and attention features exist; route-budget sweep and learned/constant routing controls missing.',
 'H Leakage':'Independent random feature graphs; public path topology. Target is not directly the candidate hierarchy but is aligned with residual graph propagation; compare receptive-field-matched controls.',
 'I Novelty':'Hierarchical pooling and graph representations already exist (DiffPool). Distinction must be demonstrable routing/scaling behavior, not hierarchy alone.',
 'J Reproducibility':'Raw graph errors, feature times and readout counts retained; aggregates replay locally. Measured times alone do not certify asymptotic complexity.',
 'K Manuscript':'Shared bounded-results narrative only; no complete routing frontier or scaling paper.',
 'L Consistency':'A hierarchy gain does not validate routing; a routing accuracy loss alone does not settle the intended cost tradeoff. Hence E rather than full-project negative.'
 },arxiv='MAJOR WORK',group='NEGATIVE/INCONCLUSIVE BUT POTENTIALLY PUBLISHABLE')

project('ultron','Ultron','Ultron','B',
 'Can evidence-aware routing improve verified completion with identical capabilities and per-task budgets?',
 'A learned selection policy improves verified completion over static, cheapest and random policies with fixed tools and charged training cost.',
 'Available task features predict which valid tool will succeed, and the gain persists on new semantic families and capability types.',
 'Eight public-example seeds on nine training and nine held semantic DSL functions. At cap24: learned 81.9444%, cheapest 66.6667%, random 58.3333%, static 44.4444%. All tie at cap53; all 22.2222% at cap8.',
 ['Positive result uses nine repeated held semantic families in a single finite DSL; broader routing and verifier independence untested.', 'Nearest-neighbor selection over five ordering variants does not implement general evidence-aware heterogeneous research orchestration.', 'Training and verifier costs, confidence intervals, novelty against algorithm selection, and external confirmation remain open.'],
 'C03: family-level leave-out/generalization and all-budget reporting, then the already-planned multi-capability external evaluation with fixed tools.',
 {
 'A Claim reconstruction':'One-step verified tool selection is the legitimate initial slice. General scientific autonomy, sequential planning and self-modification are not evaluated.',
 'B Protocol reconstruction':'18 finite semantic functions split by alternating identity into nine train/nine evaluation; five synthesis orderings; nearest-neighbor selector; caps 8/24/53; eight example seeds.',
 'C Evidence verification':'Hashes, all row means, candidate limits and training/evaluation ID disjointness pass. Learned exceeds cheapest by 15.2778 percentage points at cap24 in all eight seeds.',
 'D Baselines':'Every router has identical five tools/caps. Cheapest is selected from measured training costs. All tools are orderings of the same finite synthesizer, not diverse research capabilities.',
 'E Statistics':'72 held task-seed cases reuse nine functions; not 72 new families. Post hoc sign-flip p=.0078125 is diagnostic only; cap24 selection and multiple policies/caps require correction or a frozen primary.',
 'F Robustness':'No advantage at caps8/53. No held language/composition/depth, different task-type or external verifier test.',
 'G Ablations':'Policy comparisons isolate selection with fixed tools; evidence-DAG, failure-history and sequential action benefits untested.',
 'H Leakage':'Semantic IDs disjoint within routing training/evaluation, but evaluation tasks overlap WCODE development. Verifier is local, not privately controlled; cannot label as sealed confirmation.',
 'I Novelty':'Learned cost/performance routing is established (RouteLLM; broader algorithm selection). Need a distinct verified-capability benefit; no direct comparability to LLM routing numbers.',
 'J Reproducibility':'Routing traces, selected tools and counts are saved; shared task identities verified in this audit. No independent evaluator receipt.',
 'K Manuscript':'Shared draft reports all three caps and narrow scope, but lacks stand-alone routing analysis, full cost and independence evidence.',
 'L Consistency':'B means promising for the bounded routing question. It is not evidence for general agents, ASI or a complete Ultron system.'
 },positive='PARTIAL',arxiv='MAJOR WORK')

assert len(P)==9 and len({p['id'] for p in P})==9
registry={'schema_version':'1.0','audit_date':'2026-09-24','scope':str(ROOT),
 'classification_rule':'One A-H state per canonical research identity; state concerns intended contribution, not run success. Narrow negatives are recorded separately.',
 'projects':P,
 'non_project_artifacts':[
   {'path':str(ROOT/'world_series_cursor_pack'),'state':'H','role':'Planning/specification source; nine aliases, not nine additional projects.'},
   {'path':str(ROOT/'WORLD_SERIES_COMPLETE_BLUEPRINT.md'),'state':'G','role':'Compiled planning text; retain provenance, count no additional research identity.'},
   {'path':str(ROOT/'world-series/external/celo2'),'state':'H','role':'Third-party comparator checkout with its own Git history; not an authored project.'},
   {'path':str(ROOT/'world-series/.work-tmp/frozen-v1'),'state':'G','role':'145-file historical source snapshot of the same nine projects; source hash matches original QLearn replay identity.'},
   {'path':str(ROOT/'world-series/docs/execution/development-v2/RESEARCH_DRAFT.md'),'state':'H','role':'Shared working manuscript about existing nine modules; not a tenth research project.'}],
 'alias_disposition':'Nine empty sibling folders are noncanonical placeholders, not duplicate completed studies; preserve without deletion.',
 'scope_limits':'No remote configured for authored repo; external protected repositories are lineage references and were not included. Runtime/cache/Git internals excluded from research file hashing and recorded in inventory.'}
(OUT/'PROJECT_REGISTRY.json').write_text(json.dumps(registry,indent=2)+'\n')
lines=['# Canonical project registry','', 'All locations are current local paths. A shared working manuscript is present for every module; none has a completed stand-alone submission. All have code, executed development experiments and raw results. Local artifact/analysis reproducibility passes; independent numerical reproduction is unverified.','',
 '| Project | State | Positive claim | arXiv | Workshop | Conference/journal | Negative paper | Canonical location |',
 '|---|---|---|---|---|---|---|---|']
for p in P:
    lines.append(f"| {p['project']} | {p['scientific_state']} | {p['positive_result']} | {p['arxiv']} | {p['workshop']} | {p['conference_journal']} | {p['negative_result_publication']} | [{p['id']}]({p['canonical_location']}) |")
lines+=['','The JSON registry includes the question, central claim, hypothesis, evidence, stage, manuscript/code/experiment/result existence, reproducibility, full blocker list and next action for every identity. G/H records identify non-project material and do not inflate the nine-project denominator.']
(OUT/'PROJECT_REGISTRY.md').write_text('\n'.join(lines)+'\n')
lines=['# Full project audit dossiers','', 'A–L assessments distinguish verified facts, missing controls and unresolved novelty. The source-defined research questions are retained. “Unverified” or “missing” is an explicit audit finding, never an assumed success.','']
for p in P:
    lines += [f"## {p['project']} — state {p['scientific_state']}",'',f"Canonical: [{p['id']}]({p['canonical_location']}). Specification: [original question]({p['planning_spec']}).",'',f"**Question:** {p['research_question']}",'',f"**Claim:** {p['central_claim']}",'',f"**Hypothesis:** {p['hypothesis']}",'',f"**Evidence:** {p['evidence']}",'','| Audit dimension | Finding |','|---|---|']
    lines += [f'| {k} | {v} |' for k,v in p['audit'].items()]
    lines += ['', '**Blockers:** '+ '; '.join(p['blockers']),'','**Next action:** '+p['next_action'],'']
(OUT/'PROJECT_AUDITS.md').write_text('\n'.join(lines)+'\n')
print('Wrote registry and A-L dossiers for',len(P),'canonical projects')
