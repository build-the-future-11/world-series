# Trained program-scorer results

Eight seeds, six trained scorers and two fixed orderings. All 28,416 attempted searches are retained, including false public fits. All 144 checkpoint selection scores were recomputed from the selection partition. All trained models have the same parameter count.

| Method | Family holdout, cap 24 | Composition holdout, cap 24 |
|---|---:|---:|
| flat | 0.0760 | 0.0063 |
| length | 0.0588 | 0.0000 |
| no_hierarchy | 0.0956 | 0.0000 |
| no_relations | 0.0858 | 0.0000 |
| no_task | 0.1005 | 0.0000 |
| relational | 0.1054 | 0.0000 |
| token | 0.0980 | 0.0000 |
| uniform | 0.0196 | 0.0500 |

The relational scorer uses six ordered AST relations and root/mean pooling. `no_relations` is the flat-graph control; `flat` is the pointwise control; `token` uses prefix-neighborhood edges. Removing root pooling is `no_hierarchy`. `no_task` cannot use public examples for ranking. Equal parameter counts do not equalize information or effective capacity in ablations.

## Primary descriptive contrasts

| Partition | Control | Relational minus control | Family bootstrap 95% interval |
|---|---|---:|---|
| evaluation_family | flat | 0.02941 | [-0.00980392156862745, 0.07107843137254902] |
| evaluation_family | length | 0.04657 | [-0.0392156862745098, 0.12009803921568628] |
| evaluation_family | no_hierarchy | 0.00980 | [-0.04656862745098039, 0.06862745098039216] |
| evaluation_family | no_relations | 0.01961 | [-0.0196078431372549, 0.06372549019607843] |
| evaluation_family | no_task | 0.00490 | [-0.022058823529411766, 0.03431372549019608] |
| evaluation_family | token | 0.00735 | [-0.03676470588235294, 0.056372549019607844] |
| evaluation_family | uniform | 0.08578 | [0.024509803921568627, 0.13970588235294118] |
| evaluation_composition | flat | -0.00625 | [-0.014583333333333334, 0.0] |
| evaluation_composition | length | 0.00000 | [0.0, 0.0] |
| evaluation_composition | no_hierarchy | 0.00000 | [0.0, 0.0] |
| evaluation_composition | no_relations | 0.00000 | [0.0, 0.0] |
| evaluation_composition | no_task | 0.00000 | [0.0, 0.0] |
| evaluation_composition | token | 0.00000 | [0.0, 0.0] |
| evaluation_composition | uniform | -0.05000 | [-0.11666666666666667, 0.0] |

Intervals are exploratory and unadjusted, conditional on 51 or 60 finite semantic families. Eight example/training seeds per family are averaged before resampling; they do not create new independent families. No practical-equivalence or unrestricted programming claim follows.

All-cap completion, false-fit, candidate and fuel tables; full training/selection traces; candidate-cache costs; and per-family data are in WCODE_RESULTS.json. Ranking time is shared across cap conditions and must not be summed four times. Cold-start graph/embedding costs are separate from per-task scoring; uniform/length methods require no trained encoder. All methods execute the same enumerator and fresh interpreter/verifier calls.

The common pool contains each target; unsupported programs, lists and unseen variable arities are not evaluated by this study. Compositions and depth ranges represented here remain narrow. No source-visible task is a sealed external holdout.

Fifteen functions overlap the earlier 18-function WCODE/Ultron collection; four are in the current evaluation-family partition. They remain in the declared endpoint and are not described as fresh independent tasks. WCODE_ULTRON_OVERLAP.json lists identities and roles.

For relational scoring, six seeds select step 20 and two select step 40; none select step 80. There is no simple selection-at-the-budget-edge justification for extending training to seek a positive result. WCODE_TRAINING_REPLAY.json separately records exact same-host loss/checkpoint replay for seed 2017 only.
