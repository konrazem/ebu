# The Gaussian homeostatic reference region

**Status: derived definition, frozen for the homeostasis mission.** This
document defines a *geometry*. It registers no pass rule, no threshold on
occupancy, no hypothesis and no result. Nothing here is evidence that any
policy keeps the system anywhere.

Implementation: `homeostasis/region.py`. Every number below is reproduced by
that module in exact rational arithmetic; none is copied from a chi-square
table.

---

## 1. What is being defined, and what is deliberately not

Stage A and Stage B measured departure from the reference as `V > 0`. That
criterion is unusable for the mission question, because under continuing
disturbance and mandatory action `V = 0` at every tick is not the target and
not attainable. The mission needs a *region*, so that "localized around `x*`"
becomes a measurable physical-state property.

The region is built from the declared Gaussian model geometry alone. It is not
derived from any observed trajectory, and it does not claim that the driven
process visits states with the reference distribution — that is exactly the
empirical question the mission asks.

**Account balances, capacity, receipts, settlement and the deviation ledger `J`
appear nowhere in this document.** Homeostasis is a physical-state property
(mission section 4).

---

## 2. Gaussian model definition

The active Level-1 field is separable:

```
V(x) = sum_i V_i(x_i),    V_i(x_i) = (1/2) ((x_i - x*_i)/sigma_i)^2
```

Standardized coordinates and the radial statistic:

```
z_i = (x_i - x*_i)/sigma_i        R^2(x) = 2 V(x) = sum_i z_i^2
```

`R` is the standardized radial distance from the declared equilibrium
reference. `R^2 = 2V` is an identity, not an approximation, and
`region.radial_square` computes it from `V` so the identity holds in code too.

---

## 3. Physical conservation subspace, and the derived effective dimension

The 3-cell world carries one declared conservation law:

```
x_1 + x_2 + x_3 = M = 30
```

In standardized coordinates a law `w^T x = M` reads `(w_i sigma_i)^T z = M - w^T x*`.

**Lemma 3.1 (centrality).** The admissible set in `z` is a *linear* subspace
through the origin if and only if the reference itself satisfies the
conservation law.

Here `sum_i x*_i = 30 = M`, so the right-hand side is zero and

```
S = { z : (w_i sigma_i)^T z = 0 }
```

is a linear subspace containing `z = 0`.

This clause is load-bearing. Had the reference violated the law, `S` would be
an affine subspace missing the origin, `R^2` restricted to `S` would be
**noncentral** chi-square, and every quantile in section 5 would be wrong.
`effective_dimension` raises `REFERENCE_OFF_CONSTRAINT` on such a world rather
than reporting a dimension that silently means something else.

**Derived effective dimension.** With `rank` computed by exact rational
elimination on the standardized constraint normals:

```
d = n - rank(w~) = 3 - 1 = 2
```

> **`d = 2`, derived from the manifold and the potential metric — not assumed.**

The derivation is generic: it takes the potential, the declared laws and
nothing else. A different cell count or a second conservation law would change
`d` through the same code path.

---

## 4. Reference distribution assumption

Under the declared Gaussian reference measure `exp(-V) = exp(-|z|^2/2)`
conditioned on `S`, the coordinates in any orthonormal basis of `S` are i.i.d.
standard normal. Hence

```
R^2 ~ chi^2_d = chi^2_2
```

**This is an assumption about the declared model geometry, stated as such.** It
is not a fitted distribution, not a stationary distribution, and not a claim
about any arm's trajectory.

---

## 5. Derived quantiles — exact, not tabulated

For two degrees of freedom the chi-square CDF has an elementary closed form,
`F(r) = 1 - exp(-r/2)`, so the quantile is elementary too:

```
r_p = -2 ln(1 - p)
r_0.95 = 2 ln 20       r_0.99 = 2 ln 100
```

These are irrational while `R^2` is rational, so the module never uses a float.
It reduces both to two fast-converging `atanh` series with certified tails,

```
ln 2     = 2 atanh(1/3)
ln(5/4)  = 2 atanh(1/9)
ln 20    = 4 ln 2 + ln(5/4)
ln 100   = 6 ln 2 + 2 ln(5/4)
```

and encloses each threshold in exact rational bounds:

| Level | Threshold on `R^2 = 2V` | Enclosure width | Equivalent bound on `V` |
|---|---|---|---|
| `H95` | `2 ln 20 = 5.991464547107981...` | `< 4e-63` | `V <= ln 20` |
| `H99` | `2 ln 100 = 9.210340371976184...` | `< 6e-63` | `V <= ln 100` |

These reproduce the usual `5.99146` and `9.21034` to every digit shown, but as
*derivations* that a different world would recompute rather than inherit.

So

```
H95 = { x : R^2(x) <= 2 ln 20 }        H99 = { x : R^2(x) <= 2 ln 100 }
```

**Membership is exactly decided.** A comparison landing inside a certified
bracket raises `THRESHOLD_ENCLOSURE_TOO_COARSE` rather than guessing. At the
widths above this cannot occur for any `R^2` this world produces, but the
refusal is real code, not a comment.

---

## 6. Physical admissibility boundary, and why truncation is immaterial

Section 3 of the mission requires checking that the nonnegativity boundary does
not materially distort the chi-square reading.

The physical constraint `x_i >= 0` is the half-space `z_i >= -c_i` with
`c_i = x*_i/sigma_i = 10`. Inside `S` the distance from the origin to that
boundary is `c_i / |P_S e_i|`, and `|P_S e_i|^2 = 1 - sigma_i^2/|sigma|^2 = 2/3`,
giving an inscribed radius

```
r_boundary = 10 / sqrt(2/3) = 5 sqrt(6) = 12.2474...      r_boundary^2 = 150
```

computed exactly by `boundary_radial_square()`.

The reference mass excluded by the physical boundary is bounded above by the
union of the three half-spaces, each of which is a standard normal tail at
`12.2474` standard deviations:

```
P(excluded) <= 3 * Phi(-12.2474) <= 3 exp(-75)/(2 * 12.2474) < 3.3e-34
```

> **Disposition: the truncation is immaterial.** The excluded mass is below
> `1e-33`, while `H99` sits at `R^2 = 9.21` against a boundary at `R^2 = 150`
> — a factor of 16 in squared radius. The standard central chi-square radial
> interpretation is used without constrained-quantile correction, and no such
> correction is needed.

For orientation, the same geometry gives the extreme of the potential at a
simplex vertex `M e_k`, where `z = (20,-10,-10)` and `R^2 = 600`, i.e.
`V_max = 300` — the exact constant already frozen in the Stage-B registry.

---

## 7. The state lattice: an exactness result and a real limitation

The registered worlds move integer quantities (`reference` integral,
`quanta = {1}`, forcing quantum `1`), so the physical state is confined to the
integer conservation lattice.

**Lemma 7.1 (integrality and parity).** On that lattice `z` is integral and
`sum_i z_i = 0`, so `R^2 = sum z_i^2 ≡ sum z_i = 0 (mod 2)`. Hence `R^2` is a
non-negative **even integer** and `V = R^2/2` is a non-negative integer.

**Corollary 7.2 (the thresholds collapse to integers).** Because `R^2` is an
even integer, membership needs no logarithm at runtime:

```
H95  <=>  R^2 <= 5   <=>  R^2 in {0, 2}        <=>  V in {0, 1}
H99  <=>  R^2 <= 9   <=>  R^2 in {0, 2, 6, 8}  <=>  V in {0, 1, 3, 4}
```

(`R^2 = 4` is not attainable: no three integers summing to zero have squares
summing to 4.) The enclosure machinery of section 5 remains the definition; this
corollary is a derived consequence, verified by enumeration, and is what makes
occupancy an **exactly integer-decided** statistic with no floating point.

**Limitation — the region is geometrically natural but lattice-coarse.** Of the
496 admissible integer states:

| Region | Attainable `R^2` | Lattice states | Share of the lattice |
|---|---|---|---|
| `H95` | `{0, 2}` | 7 | 1.41% |
| `H99` | `{0, 2, 6, 8}` | 19 | 3.83% |

`H95` is exactly *"the reference, or one unit transfer away from it"*: `x*`
itself plus the six permutations of `(11, 9, 10)`. This must be read carefully.
`H95` carries 95% of the **reference measure**; it carries 1.4% of the
**state lattice**. High `O95` is therefore a demanding property in this world,
not a formality, and a low `O95` is not by itself evidence of divergence —
section 8.

---

## 8. Scientific limitations

1. **The region defines geometry, not a pass rule.** Mission section 15 is
   explicit: `O_95 >= 0.95` must not be treated as a required pass condition
   merely because the region is called "95%". No occupancy criterion is
   registered in this document.
2. **The reference distribution is not realizable on the lattice.** `chi^2_2`
   is continuous; the physical state is confined to a coarse sublattice with
   `R^2 in {0, 2, 6, 8, 14, ...}`. The region is well defined on lattice
   points, but no lattice process can have the reference distribution exactly.
   Occupancy is therefore a comparison against a declared *continuum* geometry.
3. **Quantization dominates near the reference.** The gap between `H95` and
   `H99` is two lattice shells. Fine gradations of "how close" are unavailable
   at this quantum; `q = 1` on `sigma = 1` is a coarse instrument near `x*`.
4. **`d = 2` is specific to one conservation law on three cells.** A different
   topology or a second conserved quantity changes `d`, and the exact quantile
   reduction in section 5 covers `d = 2` only. `ReferenceRegion.derive` refuses
   any other derived dimension rather than reusing the reduction.
5. **Isotropy is a consequence of `sigma = (1,1,1)`, not a general law.** For
   unequal scales `S` is still a subspace and `d` is still `n - 1`, but the
   inscribed radius of section 6 becomes cell-dependent and the truncation
   check must be redone; the code computes it per cell for exactly that reason.
6. **Nothing here measures return, excursion or drift.** Those are separate
   metrics built on this region, defined in `homeostasis/metrics.py`.
