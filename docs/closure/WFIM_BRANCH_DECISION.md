# WFIM: close the current product-expressivity branch

Disposition: NOT_SUPPORTED for learned product expressivity from the implemented
per-letter scales. Preserve the exact finite algebra as supporting infrastructure.
This closes that particular empirical branch; it is not a publication-readiness
verdict and does not erase the broader coordinate-aware representation proposal.

For a word w=(w1,...,wk), the implementation uses s(w)=product_i s(wi), with
s(empty)=1. Therefore s(uv)=s(u)s(v). The coefficient of word w in
S^-1((Sx)(Sy)) is

    sum_{uv=w} x_u y_v s(u)s(v)/s(w) = sum_{uv=w} x_u y_v.

The equality holds for nonzero letter scales; degree truncation does not change
the equality at retained words. It is an algebra automorphism, so product outputs
are independent of these scales in exact arithmetic. Floating-point differences
cannot be presented as learned expressivity. Associativity, unit preservation and
the weighted l1 submultiplicativity guarantee are classical algebraic properties.

Inspection of src/world_series/wfim finds algebra.py, transport.py, evaluate.py
and the adapter, but no trained coordinate-aware encoder or decoder. The existing
evaluator only compares finite products and truncation. Consequently there is no
implemented downstream learning mechanism to qualify or test under this claim.

The planning document permits bounded positive per-word diagonal coordinates and
a downstream task, but the implementation specializes this to multiplicative
per-letter scaling. A nonmultiplicative coordinate/decoder study would require
its own explicit protocol, conditioning constraints and matched controls. It is
not silently substituted here to rescue the failed implemented-product claim.

Evidence: src/world_series/wfim/transport.py; the collection audit A08; finite
algebra tests and development-v2 all_module_cells.csv. Keep all source and raw
outcomes. No standalone novel-algebra paper is justified by this implementation.
