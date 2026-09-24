# WFT constraint and frozen-transfer development protocol v1

State: DRAFT_NOT_AUTHORIZED. This evaluates the originally proposed symmetry
and cross-resolution regularization of a learned positive graph Laplacian. It
does not replace earlier mismatched-target repairs or claim universal transforms,
FFT complexity, continuous PDE convergence, novelty or independent confirmation.

## Physical and information contract

Each graph has m groups. A fine graph has two nodes in every group and unit
node mass. Adjacent groups have four edges of weight w/2; each pair has a
positive internal edge. A coarse graph has one node per group, mass two, and
adjacent edge weight 2w. Connectivity is a cycle or path. All connectivity,
positions, masses, the averaging restriction R and reflection action are public.
Hidden weights are not supplied to the learned or fixed-geometry methods.

Let P duplicate a coarse value across its two fine nodes; R=P^T/2. The generator
satisfies Lc=P^T Lf P and Ac=Mc^-1 Lc, Af=Mf^-1 Lf. Equal cross-group degrees
give R Af=Ac R exactly, hence R exp(-t Af)=exp(-t Ac) R. This is an equitable
finite-graph coarsening construction. Larger graphs sample the same coefficient
field at more group positions; no continuum-discretization convergence is claimed.

The generator's log-weight field is a constant plus cosine modes at frequencies
one and two. Coefficients vary independently across physical-instance seeds.
Reflection is therefore valid; a one-group cyclic shift generally does not
commute with the weighted generator despite preserving cycle topology. That
shift is used only as the labeled wrong-symmetry control. A topology automorphism
alone is insufficient to certify symmetry of an unknown weighted operator.

Every learned method has independent fine/coarse five-coefficient fields
(constant, sine/cosine at frequencies one and two), plus an internal-edge
parameter: 11 trainable parameters total. Softplus enforces positive weights.
Independent fine/coarse fields mean consistency is not tautological. Public
position features and the parametric smoothness bias are identical in all learned
controls. Scale is identified by supervised transitions at known time 0.15;
there is no zero-operator smoothness objective or hidden trace normalization.

## Training and ablations

Physical-instance seeds: 2203, 2213, 2221, 2237, 2243, 2251, 2267, 2269.
Train only on the cycle with 16 groups (32 fine nodes, 16 coarse nodes). Both
levels receive 4 or 16 observed input/output signals. Observation noise 0 or
0.1 is independently crossed with sample count. Inputs are independent normal
signals smoothed by the true diffusion for time 0.4; the same observed arrays
are available to every method. Noise affects transition outputs, not the public
graph geometry. The teacher is used only by the data generator and oracle.

Five identically parameterized learned methods: no constraints, reflection only,
cross-resolution only, both, and wrong-symmetry only. Optimize 100 Adam steps at
learning rate 0.03, gradient cap 10; no per-method hyperparameter search. Primary
loss is mean normalized squared transition error over both observed levels.
Each enabled constraint has fixed coefficient 0.1. Symmetry uses squared action
commutation error normalized by node count; consistency uses ||R Af-Ac R||^2/m.
Save every loss component and final parameters. A fixed unit-weight geometry
operator and a explicitly privileged true-operator oracle complete prediction
controls. No eigendecomposition is differentiated through in training.

## Frozen evaluation

After fitting, weights are frozen. Evaluate independent clean inputs on groups
16, 32 and 64, for both cycle and path connectivity and both levels. The same
parameter tensors generate each new operator; there is no per-size or held-graph
refit. Primary descriptive endpoint is mean normalized mass-weighted prediction
error on the previously unseen group counts 32/64, averaged over both topologies
and levels. Group16 cycle is a held-signal condition; group16 path is topology
transfer. Report them separately instead of counting them all as new domains.

Each condition supplies 16 held signals. They are repeated observations within
one physical-instance seed, not independent datasets. Average conditions within
seed, then report paired differences for all controls and descriptive bootstrap
intervals from 10,000 seed resamples, seed 240927. These eight instances and
fixed graph constructions do not establish powered equivalence or general
graph-distribution superiority. Keep all required cells and all failures.

## Transform and cost diagnostics

After freezing, compute mass-weighted eigenspectra with dense allocation capped
at 128 nodes. Verify PSD, null mode, row sums, residuals, Parseval and complete-
basis reconstruction as numerical contracts, never as learned efficacy.
Nominal compression rank is min(5, training signal count). If a repeated cluster
crosses the boundary, retain the whole cluster and report actual rank. This can
change storage, so compression is descriptive rather than a fixed-rank claim.

On the training-size cycle only, compare compression against uncentered PCA
fitted to observed training inputs and a seeded random orthogonal projection.
Neither baseline is relabeled as a transferable diffusion predictor. Fixed
geometry and oracle spectra are included at all sizes. Report setup, training,
constraint, matrix-exponential, eigensolver and reuse costs, parameter/storage
bytes and actual ranks. Dense eigensolvers are not an FFT-like speed claim.

One float64 CPU worker. Profile one physical-instance/sample/noise condition with
all five learned models and both fixed controls. Full study has 32 such fitting
conditions, 160 learned fits, and 2,688 evaluation rows. Full wall ceiling:
1,800 seconds. Source/config/protocol hashes precede outcomes; failures and
interruptions get preserved receipts. No new training is justified solely by
an unfavorable result.
