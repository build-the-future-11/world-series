# WFIM per-letter product-expressivity — ARCHIVED

**Date:** 26 September 2026  
**Disposition:** `ARCHIVED` / `ADEQUATELY_TESTED_NEGATIVE` for the implemented
per-letter multiplicative transport claim.

## Reason

For \(s(w)=\prod_i s(w_i)\), we have \(s(uv)=s(u)s(v)\). Transported products
are independent of letter scales in exact arithmetic (see
`WFIM_BRANCH_DECISION.md`). Training cannot recover a cancelled degree of freedom.

## What remains open (requires a NEW protocol)

- Non-absorbable decoder constraints with exact used-byte matching (WF04)
- Tasks where isomorphism cannot be inverted away
- Broader task-family sampling

Do **not** reopen the cancelled per-letter product claim under a new name.
Historical learning-study outcomes (identity beats learned on ordered-pattern
held-length MSE) remain unchanged in `campaigns/wfim-coordinate-development-v1/`.
