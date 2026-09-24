# Remaining requirement map

Every original checklist item remains in results/requirement_map.json. External dependencies do not block unrelated local work.

| Class | Items |
|---|---:|
| EXTERNAL_REQUIRED | 6 |
| LOCAL_AND_EXTERNAL | 11 |
| LOCAL_EXECUTABLE | 95 |
| RESOLVED_SCOPED | 33 |

The 33 resolved entries include one original-scope N/A (WP07). No shared paper-level gate is inferred from a narrow numerical pass.

| Open item | Project | Work class | Exact requirement |
|---|---|---|---|
| G03 | shared | LOCAL_EXECUTABLE | Decide the actual paper unit and contribution. Review WCODE/Ultron overlap; resolve whether WFIM has a research contribution beyond support code. Do not count the shared draft as nine papers. |
| G04 | shared | LOCAL_EXECUTABLE | Complete a full-paper novelty comparison against the closest work, including exact differences, already-known results, baseline availability and what would refute the proposed distinction. |
| G05 | shared | LOCAL_EXECUTABLE | Freeze one primary question, estimand, endpoint, effect direction, practically meaningful margin and decision rule for each empirical claim. |
| G06 | shared | LOCAL_EXECUTABLE | Define the independent sampling unit, target population and train/selection/evaluation split. Separate repeated examples/seeds from new task families or datasets. |
| G07 | shared | LOCAL_EXECUTABLE | Determine sample size and precision/power from development evidence using the correct independent unit; fix the seed list and all required condition cells. |
| G08 | shared | LOCAL_EXECUTABLE | Freeze exclusions, failures/divergence handling, missing-cell policy, stopping rules and multiplicity correction before new evaluation outcomes. |
| G09 | shared | LOCAL_EXECUTABLE | Freeze comparator implementations, tuning/search budgets, checkpoint versions and information access. Label privileged oracle controls separately. |
| G10 | shared | LOCAL_EXECUTABLE | Freeze the cost definition: training, selection, preprocessing, adaptation/inference, ranking, verification, memory and amortization where relevant. |
| G11 | shared | LOCAL_AND_EXTERNAL | Assign execution ownership and required reviewer/evaluator ownership; record dependencies, actual hardware/storage availability and measured runtime projections. |
| G12 | shared | LOCAL_EXECUTABLE | Profile before expensive runs, fix allocation/stopping limits and preserve existing locks/failed receipts. Resource limits may block a required study; they cannot justify substituting a smaller demonstration and claiming completion. |
| G13 | shared | LOCAL_EXECUTABLE | Freeze code, config, environment, data and protocol hashes. Fresh evaluation feedback must not be used for further tuning while retaining a confirmation label. |
| G14 | shared | LOCAL_EXECUTABLE | Define finite outcomes: supported, adequately tested negative, inconclusive, or archive. Additional iterations require a documented scientific reason rather than repeated attempts to obtain a win. |
| QL01 | qlearn | LOCAL_EXECUTABLE | Map bounded updates and discrete MALIS actions to separate claims; implement any missing mechanism required by the retained original claim. |
| QL03 | qlearn | LOCAL_EXECUTABLE | Evaluate adequately sampled held optimizee families, datasets, widths and adaptation horizons required by the original generalization claim. |
| QL04 | qlearn | LOCAL_EXECUTABLE | Qualify tuned SGD, momentum and AdamW plus compatible official learned-optimizer comparators; document deviations, pretraining compute and unresolved data overlap. |
| QL05 | qlearn | LOCAL_EXECUTABLE | Complete budget, gate, recurrence/reset-state, feedforward and initialization-only ablations with fair parameter/information access. |
| QL06 | qlearn | LOCAL_EXECUTABLE | Measure the frozen full-cost objective, memory and amortization; retain step-AUC and endpoint accuracy as separately labeled metrics. |
| QL07 | qlearn | LOCAL_EXECUTABLE | Retain every failed tuning trial and evaluation trajectory; analyze divergence and long-horizon stability with the frozen failure policy. |
| QL08 | qlearn | LOCAL_EXECUTABLE | Establish a powered positive/negative/inconclusive decision. Do not rescue a failed efficiency claim by switching to accuracy or a weaker baseline. |
| QA01 | qapen | LOCAL_EXECUTABLE | Implement and verify the proposed quantizer/codebook behavior, stable expert identities and complete checkpoint/restore state. |
| QA02 | qapen | LOCAL_EXECUTABLE | Implement the specified delayed-utility memory read/write/consolidation mechanism; prove retrieval affects prediction rather than merely logging writes. |
| QA03 | qapen | LOCAL_EXECUTABLE | Implement and test warmup, activation, sleep/revival, capacity caps and the required lifecycle rules; newly fitted experts must be evaluated on subsequent data. |
| QA04 | qapen | LOCAL_EXECUTABLE | Verify predict-before-observe causal order and absence of future labels/regime IDs in learner inputs. |
| QA05 | qapen | LOCAL_EXECUTABLE | Run a lifecycle × memory factorial comparison against single-expert memory, fixed ensemble, no-memory, random/recent/replay and qualified expansion controls. |
| QA06 | qapen | LOCAL_EXECUTABLE | Evaluate independent schedules with no shifts, rare returns, long gaps, delayed cues and independently varied observation noise. |
| QA07 | qapen | LOCAL_EXECUTABLE | Report full-cost NLL, calibration, recovery, ordinary/rare-regime performance, expert growth and memory utility with uncertainty. |
| QA08 | qapen | LOCAL_EXECUTABLE | Demonstrate incremental lifecycle and delayed-memory contribution beyond the strongest simple control, or close a precise negative/inconclusive result. |
| QW01 | qwipii | LOCAL_EXECUTABLE | Prove useful goal-preserving symmetries exist in the intended evaluated domains before allocating more search compute. |
| QW02 | qwipii | LOCAL_EXECUTABLE | Verify group/domain actions preserve legal transitions, costs and goal predicates; prove or exhaustively verify quotient/path-lifting correctness over the claimed finite scope. |
| QW03 | qwipii | LOCAL_EXECUTABLE | Implement/evaluate the discovery component if discovered invariants are claimed; distinguish proposal, empirical support and exact verification. |
| QW04 | qwipii | LOCAL_EXECUTABLE | Compare brute, quotient, ranking-only and discovery-guided search with identical candidate access and charged canonicalization/verification work. |
| QW05 | qwipii | LOCAL_EXECUTABLE | Evaluate new whole puzzle families, larger cases, symmetry-breaking goals and deliberately invalid transformations; retain existing fixed-goal no-savings results. |
| QW06 | qwipii | LOCAL_EXECUTABLE | Replay all returned paths; measure solve rate, total work, memory and path quality without treating greedy ranking as guaranteed shortest-path BFS. |
| QW07 | qwipii | LOCAL_EXECUTABLE | Establish a useful verified reduction or a novel, adequately scoped limitation. Classical projective identities alone do not complete the contribution. |
| WC04 | wcode | LOCAL_EXECUTABLE | Hold out compositions, depths and appropriate program families; expand beyond the repeatedly used 18 semantic functions to the coverage justified by the original claim. |
| WC05 | wcode | LOCAL_EXECUTABLE | Charge graph construction, scoring, candidate interpretation, verification and training; report exhausted searches and incorrect public-example fits. |
| WC06 | wcode | LOCAL_EXECUTABLE | Ablate relations, hierarchy and task conditioning; demonstrate any gain remains beyond candidate length and changed enumeration. |
| WC07 | wcode | LOCAL_EXECUTABLE | Resolve cross-use of WCODE and Ultron task families; disclose shared results and decide separate versus consolidated paper on scientific grounds. |
| WC08 | wcode | LOCAL_EXECUTABLE | Decide supported/negative/inconclusive using the frozen family-level solve/cost endpoint; do not claim unrestricted coding from a finite DSL. |
| WF02 | wfim | LOCAL_EXECUTABLE | Locate a mathematically nontrivial parameter effect in the already-proposed coordinate-aware representation/decoder, or stop that branch as supporting infrastructure. Do not invent a new project to avoid the finding. |
| WF03 | wfim | LOCAL_EXECUTABLE | If a legitimate mechanism remains, implement/train it with verified invertibility, conditioning, unit and associativity contracts as applicable. |
| WF04 | wfim | LOCAL_EXECUTABLE | Compare learned and identity coordinates using the same algebra, decoder and total byte budget; include matched vector and bilinear/binding controls. |
| WF05 | wfim | LOCAL_EXECUTABLE | Evaluate held composition templates and lengths, order-sensitive and appropriate negative-control tasks. |
| WF06 | wfim | LOCAL_EXECUTABLE | Measure all coefficient/index/metadata/parameter storage, multiplication cost, approximation error and norm growth; justify every claimed tail bound. |
| WF07 | wfim | LOCAL_EXECUTABLE | Establish a distinct downstream contribution or explicitly archive the standalone method-paper claim. Archive is a closed disposition, not a publication pass. |
| FT07 | wft | LOCAL_EXECUTABLE | Establish incremental constraint benefit or a precise negative finding. Full-basis reconstruction and oracle zero error cannot serve as the learning result. |
| WP01 | wpinn | LOCAL_EXECUTABLE | Diagnose all 17 saved rollout failures and preserve their original receipts; separate conditioning, support-selection, quadrature, model and integration failures. |
| WP02 | wpinn | LOCAL_EXECUTABLE | Check identifiability/excitation, library scaling, quadrature accuracy and support recovery across sampling/noise conditions. |
| WP04 | wpinn | LOCAL_EXECUTABLE | Qualify SINDy/WSINDy and other genuinely comparable baselines; match observations, libraries and tuning while labeling known-support privileges. |
| WP06 | wpinn | LOCAL_EXECUTABLE | Evaluate independent complete trajectories, initial conditions, held physical parameters/laws and required sampling/noise/missingness regimes. |
| WP09 | wpinn | LOCAL_EXECUTABLE | Establish valid-structure benefit beyond strong weak discovery, or a scientifically distinct negative/identifiability result. |
| CW02 | cwlnn | LOCAL_EXECUTABLE | Compare receptive-field-, depth-, width- and information-matched flat/unrouted/attention controls with the same training and selection policy. |
| UL02 | ultron | LOCAL_EXECUTABLE | Freeze genuinely new held families and the already-proposed heterogeneous capability types, with tools/checkpoints fixed throughout comparison. |
| UL03 | ultron | LOCAL_EXECUTABLE | Qualify best-fixed/static, measured-cheapest, random and learned policies with identical available capabilities and budgets. |
| UL04 | ultron | LOCAL_EXECUTABLE | Charge router training/counterfactual tool calls, inference, failed actions, retries, execution and verification; retain unavailable/unsupported tasks. |
| UL05 | ultron | LOCAL_EXECUTABLE | Test evidence integrity, invalid artifacts, verifier rejection, budget exhaustion and uncertainty/failure handling. |
| UL06 | ultron | LOCAL_EXECUTABLE | If evidence-aware or sequential orchestration is claimed, implement it and isolate its contribution beyond one-step feature-based routing. |
| UL07 | ultron | EXTERNAL_REQUIRED | Obtain an actually independent evaluator and externally frozen verifier/protocol for the intended independent-verification claim; a local client interface is insufficient. |
| UL08 | ultron | LOCAL_EXECUTABLE | Establish family-level verified-completion benefit at the frozen full-cost budget and identify its limits across task types/caps. |
| S01 | shared | LOCAL_EXECUTABLE | Reconcile planned versus attempted versus completed units; every excluded/missing/failed case has the predeclared treatment and a retained receipt. |
| S02 | shared | LOCAL_EXECUTABLE | Calculate effect sizes and uncertainty at the correct sampling level; preserve pairing and account for shared training/datasets/task families. |
| S03 | shared | LOCAL_EXECUTABLE | Apply the frozen multiplicity/sequential-testing policy; disclose exploratory analyses separately. |
| S04 | shared | LOCAL_EXECUTABLE | Test sensitivity to justified estimator/model assumptions and report whether conclusions survive; do not select a favorable sensitivity as the new primary. |
| S05 | shared | LOCAL_EXECUTABLE | Verify statistical conclusions match the frozen meaningful-effect/equivalence margin; nonsignificance alone cannot establish equivalence or a negative claim. |
| S06 | shared | LOCAL_EXECUTABLE | Audit all dataset/checkpoint versions, semantic duplicates, overlap across projects, external pretraining exposure and role leakage. |
| S07 | shared | LOCAL_EXECUTABLE | Reconcile differing metric definitions, baseline implementations and cost units across reports; explain genuine scope-dependent findings and stale contradictions. |
| S08 | shared | LOCAL_EXECUTABLE | Complete all required robustness and mechanism-ablation cells; missing required studies remain blockers. |
| S09 | shared | LOCAL_EXECUTABLE | Map each headline to its exact raw evidence and analysis; reject unsupported extensions, cherry-picked seeds and survivor-only tables. |
| S10 | shared | EXTERNAL_REQUIRED | Obtain a scientific review of design, inference and novelty; resolve substantive criticisms with evidence or explicit bounded claim decisions. |
| R01 | shared | LOCAL_EXECUTABLE | Pin release source, protocol/configs, dataset versions, comparator code/weights and environment separately; retain hashes and dirty-source provenance where applicable. |
| R02 | shared | LOCAL_EXECUTABLE | Remove reliance on author-specific absolute paths or missing external `.portfolio` files; include or reproducibly fetch every required input. |
| R03 | shared | LOCAL_EXECUTABLE | Provide exact runtime/OS/hardware dependencies, lockfiles and deterministic/randomness settings; document supported nondeterminism and numerical tolerances. |
| R04 | shared | LOCAL_EXECUTABLE | Supply one command to regenerate every headline table/figure from preserved raw results, plus separate commands for full experimental reproduction. |
| R05 | shared | LOCAL_EXECUTABLE | Reproduce required full experiments in a clean environment with fresh output paths; record commands, exit codes, runtimes, all failures and differences. |
| R06 | shared | EXTERNAL_REQUIRED | Obtain second-environment/person replication where required by the claim or project contract; never relabel same-host analysis replay as independent replication. |
| R07 | shared | LOCAL_EXECUTABLE | Package raw outputs, split ledgers, tuning traces, checkpoints or exact fetch instructions, proofs, tests, failure receipts and provenance. |
| R08 | shared | LOCAL_EXECUTABLE | Build `results/claim_index.json` linking every headline to code/config/data hashes, all attempted units, raw files, estimator and table/figure. |
| R09 | shared | LOCAL_AND_EXTERNAL | Resolve the actual project license, third-party/data/model permissions and required attribution; replace the current placeholder license decision. |
| R10 | shared | LOCAL_EXECUTABLE | Verify a clean extracted package with no hidden local state: installation, tests, data/checkpoint resolution, analysis regeneration and numerical tolerances all pass. |
| R11 | shared | LOCAL_EXECUTABLE | Freeze and checksum the final package; preserve its final reproduction log and source identity. |
| M01 | shared | LOCAL_EXECUTABLE | Choose a coherent paper title and precise contribution statement supported by the completed science. |
| M02 | shared | LOCAL_EXECUTABLE | Write the complete abstract, motivation, related work and explicit research question; distinguish prior work from the actual contribution. |
| M03 | shared | LOCAL_EXECUTABLE | Describe mathematics/algorithm, assumptions, implementations, datasets/splits, selection procedures, resource budgets and full evaluation protocol sufficiently for reproduction. |
| M04 | shared | LOCAL_EXECUTABLE | Include all primary results, appropriate uncertainty, strong comparators, meaningful ablations, robustness and failure/negative outcomes. |
| M05 | shared | LOCAL_EXECUTABLE | Supply proofs or appropriately bounded empirical checks for mathematical/correctness claims; remove unsupported generalization or complexity statements. |
| M06 | shared | LOCAL_EXECUTABLE | Explain limitations, identifiability, data contamination uncertainty, scope, threats to validity and negative findings without disguising them. |
| M07 | shared | LOCAL_EXECUTABLE | Generate every figure/table from the frozen artifact; include clear units, denominators, labels, accessible rendering and captions describing uncertainty/failures. |
| M08 | shared | LOCAL_EXECUTABLE | Complete supplementary methods, detailed hyperparameters, all-condition tables, unsuccessful runs and protocol deviations. |
| M09 | shared | LOCAL_EXECUTABLE | Verify citations and bibliography against original sources; finish exact novelty comparison rather than relying on abstract screening. |
| M10 | shared | EXTERNAL_REQUIRED | Resolve authorship, contribution statements, affiliations, acknowledgments, funding/conflict and relevant data/code/AI-assistance disclosures with the actual authors. |
| M11 | shared | LOCAL_EXECUTABLE | Render and inspect the final PDF and supplement; fix broken references, missing assets, unreadable plots, formatting errors and every TODO/placeholder. |
| M12 | shared | EXTERNAL_REQUIRED | Have a reviewer read the paper without conversation context; resolve all substantive scientific/editorial objections and reconcile paper ↔ tables ↔ code ↔ registry. |
| P01 | shared | LOCAL_AND_EXTERNAL | Select a venue whose scope and contribution expectations fit the completed result; independently decide whether an arXiv preprint is appropriate. |
| P02 | shared | LOCAL_AND_EXTERNAL | Check the selected venue's current official requirements: format, length, anonymity, supplementary material, artifact availability, disclosure/ethics requirements and applicable submission dates. |
| P03 | shared | LOCAL_AND_EXTERNAL | Prepare the exact venue-formatted manuscript, supplement, bibliography and artifact access instructions; inspect any anonymous build for identity leaks if required. |
| P04 | shared | LOCAL_AND_EXTERNAL | Complete the venue research/reproducibility checklist and any required metadata, cover letter or statements; all assertions must match evidence. |
| P05 | shared | EXTERNAL_REQUIRED | Confirm all authors approve the final version, authorship, disclosures, license and submission destination; resolve any simultaneous-submission constraints that apply. |
| P06 | shared | LOCAL_AND_EXTERNAL | Finalize the artifact repository/deposit and persistent citation/version where required; verify access from a clean environment and preserve the exact submission source. |
| P07 | shared | LOCAL_EXECUTABLE | Independently record arXiv READY/not-ready and peer-review READY/not-ready with reasons; a preprint does not imply peer-review readiness. |
| P08 | shared | LOCAL_AND_EXTERNAL | Run the final zero-open-items gate below and save its signed/owned readiness decision. |
| Z01 | shared | LOCAL_EXECUTABLE | The completed study establishes a defensible supported result, rigorous negative result, or substantive uncertainty/identifiability finding with a distinct contribution; an unfinished pilot has not been relabeled as complete. |
| Z02 | shared | LOCAL_EXECUTABLE | Original question, final scope and any explicit scope decisions are recorded; no required full experiment was silently replaced by a toy study. |
| Z03 | shared | LOCAL_EXECUTABLE | All required controls, ablations, robustness studies and statistical decisions are complete and source-bound. |
| Z04 | shared | LOCAL_AND_EXTERNAL | Every claimed external/independent review or evaluation actually occurred and has a verifiable receipt. |
| Z05 | shared | LOCAL_EXECUTABLE | Every headline is reproducible from the final package and agrees with the manuscript. |
| Z06 | shared | LOCAL_EXECUTABLE | Paper, source, figures, tables, supplement, configs, results, scripts, README, LICENSE, environment and reproduction instructions are complete. |
| Z07 | shared | LOCAL_EXECUTABLE | No unresolved required item is open, blocked, placeholder or assigned unsupported N/A; there are no unexplained failed required cells. |
| Z08 | shared | LOCAL_AND_EXTERNAL | Novelty, authorship, permissions, current venue requirements and final author approval are resolved. |
| Z09 | shared | LOCAL_AND_EXTERNAL | Final scientific and editorial review finds no substantive blocker; arXiv and peer-review verdicts are recorded separately. |
| Z10 | shared | LOCAL_EXECUTABLE | Every one of the nine registry entries points to a submission-ready paper or an explicit negative/inconclusive/archive/supporting-library disposition. Unpublishable dispositions are not counted as ready papers. |
| Z11 | shared | LOCAL_EXECUTABLE | Shared data, reused results, merged paper decisions and remaining research ambitions are clearly disclosed; no duplicate claims are presented as independent contributions. |
| Z12 | shared | LOCAL_EXECUTABLE | The final registry, reports, archive and public-facing claims agree with the verified final state. |
