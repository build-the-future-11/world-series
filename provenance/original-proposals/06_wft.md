# 06 — World Fourier Transform
## Working research title
Constraint-Guided Learned Graph Spectra for Transferable Signal Representation.

A Fourier-like transform requires an operator, inner product, basis and inverse. “Decompose anything” is not a complete mathematical specification. The first domain is finite weighted graphs with a self-adjoint operator; arbitrary manifolds, non-normal dynamics and universal transforms are deferred.

## Related work and corrected novelty

Graph Fourier analysis [R21] and learning Laplacians from signal data [R22] already cover learning an operator and its spectrum. FNO [R23], neural operators [R24] and DeepONet [R25] address mappings between function spaces, which is related but not identical to learning a transform. The candidate question is whether specific verified symmetry and cross-resolution constraints help an operator learned from limited/noisy signals. The constraints must demonstrate an advantage over an otherwise identical learned-Laplacian baseline.

## Operator construction

Given sparse candidate edges, orient each edge arbitrarily to form incidence matrix B. Use nonnegative trainable weights `w=softplus(a)+ε` and

`Lθ=Bᵀdiag(w)B`.

For positive diagonal mass M, define `Sθ=M^(-1/2)LθM^(-1/2)`. This is symmetric positive semidefinite. Normalize or constrain a scale statistic such as trace/total edge weight according to the declared generative model; without a scale convention, a trivial near-zero operator can minimize some smoothness losses. Do not introduce a normalization that rules out the physical operator you are trying to estimate.

Let `SθQ=QΛ`, `Φ=M^(-1/2)Q`. Encode `c=ΦᵀMf`; decode `f_hat=Φ_k c_k`. With all modes, Parseval holds in the M inner product. With k modes, reconstruction is a projection. In the full-rank case, perfect reconstruction is automatic for any valid basis and therefore cannot establish that the learned operator is meaningful.

## Training objectives that identify something

Use observed development signal transitions or missing/noisy signal reconstruction. For diffusion-like data, a model may predict `f(t+Δt)≈exp(−Δt Sθ)f(t)` in appropriately mass-normalized coordinates. Use a small matrix exponential reference or a polynomial filter `Σ_j α_j Sθ^j` for training. Evaluate which approximation is used and its error.

A proposed loss combines held-in prediction error, operator regularization, verified symmetry commutation and optional cross-resolution consistency:

`L=L_pred+λ_reg R(Lθ)+λ_sym Σ_g||T_gLθ−LθT_g||²+λ_scale||R L_f−L_c R||²`.

Transform maps T_g and coarsening R must be applicable to the problem and available under the same information contract as controls. They are not arbitrary augmentation operators. In weighted spaces, define compatible mass-weighted actions rather than assuming Euclidean commutation covers every discretization. Add each constraint as a separate ablation before combining them.

An eigensolver's residual is a numerical diagnostic, not a learning signal for physical correctness. Likewise a reconstruction loss with all N modes cannot choose among complete orthogonal bases. Use a real prediction/compression/missing-data task with held-out signals and graphs.

## Numerical stability

Eigenvectors have sign ambiguity and repeated-eigenspace nonuniqueness; derivatives through them become problematic near repeated eigenvalues [D03]. Train polynomial/operator actions first and compute eigenspectra after freezing the candidate. For tests compare projectors or principal angles, not arbitrary eigenvector columns. If a truncation boundary cuts a repeated cluster, report the ambiguity or retain the complete cluster.

Dense `eigh` is acceptable for small reference graphs, not a scalable FFT replacement. Cap dense diagnostics at a declared small N. The implementation must not market an O(N³) eigendecomposition as an O(N log N) transform without counting setup and repeated-use assumptions.

## Contracts and code units

`GraphDomain`: node count, edge index, mass vector, coordinates if public, admissible transformations and provenance.
`OperatorModel.apply(f[N,C]) -> [N,C]`.
`SpectralBasis`: eigenvalues[k], basis[N,k], mass[N], operator hash and degeneracy metadata.
`Transform.encode/decode`: shape-checked weighted coefficients and reconstruction.

| File | Responsibility |
|---|---|
| domains.py | Graph instances, public edge candidates and signal splits |
| laplacian.py | Sparse PSD construction and scale constraints |
| mass.py | Weighted inner products and coordinate conversion |
| filters.py | Polynomial action and small exponential reference |
| train.py | Prediction loss and individually toggled constraints |
| spectra.py | Frozen eigendecomposition and subspace diagnostics |
| transform.py | Encode/decode with mode-selection policy |
| baselines.py | Fixed geometry Laplacian, learned Laplacian, PCA and valid grid DFT |
| evaluate.py | Predictive/compression error, cost and discretization transfer |
| adapter.py | `fit_spectral_operator` and `transform_signal` |

## First benchmark

Generate signals on small graphs with hidden edge weights and public candidate connectivity. Do not pass the exact true operator into the candidate as “geometry.” Create train/dev graph instances with different weight distributions and hold out additional graph sizes or discretizations. Start at 32–128 nodes, two to eight signal channels and a small polynomial degree. Reserve a regular grid as a sanity case where a conventional basis should be strong, not an artificially weak baseline.

Minimum comparisons: fixed geometry-based Laplacian; learned-Laplacian model with identical parameterization but no new constraints; PCA fit only on training signals; random orthogonal basis; DFT only on a domain where ordering/periodicity makes it legitimate. Include the true generator operator only as an explicitly privileged oracle. Compare FNO/DeepONet only for a common prediction task, not as nonsensical transforms of one graph snapshot.

Primary proposal: held-out transition prediction or missing-signal reconstruction at a fixed total computational budget—choose one before confirmation. Secondary: k-mode compression, weighted reconstruction error, operator recovery when identifiable, cost including setup, and transfer across declared graph sizes. Reusing a frozen learned operator over many signals may amortize cost; state the reuse count.

## Tests and failure controls

PSD and symmetry; row sums zero in the unweighted Laplacian; constant null mode; positive masses; mass-weighted Parseval; encode/decode on a complete basis; permutation covariance including mass and edges; repeated-eigenspace projector consistency; degree-zero filter; analytic gradients for a small simple-spectrum case; polynomial gradients independent of eigenvector choice; no dense allocation beyond the cap; wrong supplied symmetry rejected or shown harmful in a labeled ablation.

Sunday demonstration: a learned sparse operator, its spectrum and a genuine held-out reconstruction/prediction comparison. Defer universal spectral theory, arbitrary Koopman diagonalization, learned graph topology plus learned masses plus learned basis simultaneously, and coupling to every other module before this single-domain study is interpretable.


---
