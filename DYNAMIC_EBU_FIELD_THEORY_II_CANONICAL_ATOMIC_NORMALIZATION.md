# Dynamic EBU field theory II — canonical atomic normalization and one-scalar local capacity

> **SUPERSEDED AS AUTHORITY by `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md`.**
> Retained as working history. Where this file conflicts with the synthesis, the
> synthesis governs. Do not cite this file as programme authority.


**Decisive theory report. No simulation, no mechanism implementation, no
Stage A/B, no viability threshold `Lambda`, no history vectors.**

> **CORRECTED AND RESCOPED BY `DYNAMIC_EBU_FIELD_THEORY_III_ONE_SCALAR_CURRENT_FIELD_CAPACITY.md`.**
> Three corrections apply: (i) infinitesimal N1 is replaced by **finite** level-set
> compatibility `W_a(u)=W_a(v) => V_a(u)=V_a(v)`; (ii) the differential sign is
> `dc = -dW`, so `Delta c = W_before - W_after`; (iii) factor refinement is valid
> only when **both** the reference and the current potential are exactly additive
> under it — genuine cross terms may not be discarded.
> **Scope:** the factorwise construction below is retained as a **proved
> mathematical construction**, NOT as the completed dynamic regulatory mechanism.
> It is anchored to `theta_0` and so tracks the reference field's sign; Theory III
> §2 exhibits an action where it earns `+1` while the current field prices it at
> `-1/3`. Read Theory III first.

This report answers:

> Can a changing physical EBU field be normalized **locally, action by action**,
> to **one canonical persistent scalar capacity coordinate**?

**Answer: YES, and the admissible class is characterized exactly.** The resolution
is *factorwise* normalization against a *canonical* reference coordinate. §20
states the verdict; §19 answers Q1–Q9.

Physical picture held throughout: no global threshold, no global planner,
arbitrarily fine atomic actions, and *current local field + one carried scalar →
local action freedom*. The field may be unbounded, as gravitational and
electrostatic potentials are. **No universal viability ceiling is assumed,
required, or introduced.**

Checks: `dynamic_ebu_theory_checks.py` — **165 deterministic checks, 0 failures**,
exact `Fraction`, tolerance zero, no randomized search.

---

## 0. Incorporating the independent audit

Theory I is **superseded on the following points**. All were found by the
independent audit and are corrected here, not carried forward.

| # | Theory-I statement | Disposition in Theory II |
|---|---|---|
| 1 | **L3 factor-additivity is necessary for R4** | **WITHDRAWN — too restrictive.** Counterexample: two declared factors, every action changing both, so R4 restricts nothing, yet no factor-additive `W` exists. Locality is a *graph-dependent spectator-invariance* condition, not additivity. §6 rebuilds the correct architecture |
| 2 | zero pattern left as an optional "reading" | **HYPOTHESIS Z now explicit**, and §6 shows it is required **only for a single global conversion**. Factorwise, only the per-factor zero condition is needed (§6.3) |
| 3 | **L2 acyclicity as independent content** | **WITHDRAWN as redundant.** Given L1 and that each `V_theta` is a state function, contraction can never create a cycle. Not retained as a requirement |
| 4 | `Z ∧ L1` establishes a usable `W` | **CORRECTED.** It establishes *some* ordering, **not a canonical one**. §2 supplies canonicality |
| 5 | multiple non-affinely-related `W` | **CONFIRMED as a real defect of Theory I.** They change affordability sets. Resolved in §2 by declaring `W := V_theta0` |
| 6 | graph-topological `W` supports receipts | **CORRECTED.** A topological-order `W` has no continuous extension. The canonical `W = V_theta0` does, and receipts are recovered exactly (§12) |
| 7 | fixed-field exact EBU; static V1; scalar revaluation; magnitude-faithful no-go; same-ruler cancellation; closed-cycle telescoping for a declared `W` | **PRESERVED**, unchanged |

Theory I's Theorem DS is therefore demoted: it answers *existence of some
ordering*, which is not the question. **The question is canonical local
normalization, and that is what this report settles.**

---

## 1. No viability threshold; refinement invariance instead

No universal `V <= Lambda` criterion is introduced. The architecture assumes
**arbitrarily fine physical actions**, so the governing requirement is not a
ceiling but **exact refinement invariance**: for every subdivision
`x_0 -> x_1 -> ... -> x_N` of the same physical path,

```
sum_k Delta c(x_k -> x_{k+1})  =  Delta c(x_0 -> x_N).
```

Hard physical constraints — nonnegative stock, route capacity, conservation,
genuine physical impossibility — remain physics. **No new universal EBU burden
ceiling is invented.**

**Theorem RI (refinement invariance forces exactness).** Let a settlement rule
assign `F(x, y)` to a transition. If `F` is additive under subdivision along
every allowed path, then `F(x, y) = W(x) - W(y)` for some state function `W`,
unique up to an additive constant.

*Proof.* Additivity gives `F(x,z) = F(x,y) + F(y,z)` whenever `y` lies on an
allowed path from `x` to `z`. Fix a base point `x_0` on the component and set
`W(x) := F(x, x_0)`. Then `F(x,y) = F(x,x_0) + F(x_0,y) = W(x) - W(y)`. ∎

> **Refinement invariance alone selects `dc = dW`.** No cycle argument, no global
> planner and no threshold is needed — a purely local additivity requirement
> already forces a state function. This replaces Theory I's cycle-space route as
> the *primary* justification.

**Corollary (no slicing evasion).** Because `Delta c` depends only on endpoints,
no actor can escape a negative finite consequence by slicing it into many tiny
actions. *Verified:* the exact rule returns `21` for every subdivision
`N = 1,2,4,8,16`, while the prohibited endpoint rule `E/p(start)` returns
`30, 417/16, 1515/64, 5727/256, 22215/1024` — a different number at every
resolution, never equal to the exact value. *(Checked: `CA8`, `CA9`.)*

---

## 2. The canonical reference coordinate — the load-bearing theorem

The audit's decisive finding was that a merely *existing* `W` is not enough:
non-affinely-related choices change affordability. The resolution is to declare
one reference field `theta_0` and set

```
W(x) := V_{theta_0}(x).
```

**Theorem CAN (canonicality).** Suppose the settlement recovers Capacity V1
exactly at the declared reference field: for every allowed action at `theta_0`,

```
Delta c(x -> y) = E_{theta_0}(x -> y) / p(theta_0),   one constant p(theta_0) > 0.
```

Then on each connected component of the allowed-transition graph

```
W = V_{theta_0} / p(theta_0) + b,
```

i.e. **`W` is unique up to one positive scale and one additive constant.**

*Proof.* The hypothesis says `W(x) - W(y) = [V_{theta_0}(x) - V_{theta_0}(y)]/p`
on every edge. Hence `W - V_{theta_0}/p` has zero increment along every edge, so
it is constant on each connected component. ∎ *(Checked: `CA1`, `CA2` — the
3-cell action graph is connected, every `(p>0, b)` satisfies edge recovery, and a
non-affine candidate such as `W = V_0^2` fails it.)*

**Answers to the four questions posed.**

- **(A) Is this enough to make `W` canonical?** **Yes**, given a connected
  reachable component. Static-V1 recovery is a *proportionality* requirement, not
  a sign requirement; Theory I's L1 constrained only signs, which is exactly why
  it left `W` free.
- **(B) When is another `W` physically equivalent?** Exactly when
  `W' = aW + b`, `a > 0`. Then `c' = a c` and `Delta c' = a Delta c`, so
  `c' + Delta c' >= 0 ⟺ c + Delta c >= 0` — the same-ruler cancellation. The
  constant `b` never appears in a difference. **Affordability is unchanged.**
- **(C) Can a genuinely non-affinely-related `W` satisfy static-V1 recovery?**
  **No** — Theorem CAN.
- **(D)** No missing axiom: uniqueness is proved. The only residual freedom is
  one additive constant per additional connected component, which is a
  declaration about cross-component comparability, not a physical degree of
  freedom.

> Theory I's Finding-4 defect is thereby **closed**: the canonical `W` is fixed by
> the *static* EBU authority the programme already possesses.

---

## 3. Atomic / differential normalization

Let `M` be the reachable manifold, `T_x M` the space of allowed infinitesimal
displacements at `x` (the conservation slice, route constraints included), and
`W` canonical. Ask for a positive **local** scalar `p(x, theta) > 0` with

```
dV_theta |_T  =  p(x, theta) dW |_T        i.e.   grad_T V_theta = p grad_T W.
```

**Zero condition.** Where `grad_T W(x) = 0`, the relation forces
`grad_T V_theta(x) = 0`. So a single global normalizer requires **the critical
sets of `V_theta` and `W` on the slice to coincide**. This is the differential
form of hypothesis Z. (§6.3 shows the factorwise architecture needs only the
*per-factor* version of this, which is much weaker.)

If the relation holds, then along any allowed path

```
dc = dV_theta / p(x, theta) = dW ,        Delta c = ∫_gamma dW = W(before) - W(after),
```

**exactly**. The prohibited rule `finite E / p(start)` is not used anywhere: §1
shows it is not even refinement invariant.

---

## 4. Refinement / atomic-invariance theorem

Proved in §1 (Theorem RI) in the stronger direction: refinement invariance does
not merely *follow* from `dc = dW`, it **characterizes** it.

The discrete statement, `sum_k [W(x_k) - W(x_{k+1})] = W(x_0) - W(x_N)`, is
telescoping; the continuous statement is the fundamental theorem of calculus
applied to `lambda -> W(x(lambda))`, which needs `W` differentiable along the
path — supplied by canonicality, since `W = V_{theta_0}` is a declared smooth
potential.

> **Atomic decomposition changes computational resolution, not physical
> settlement.**

---

## 5. Direction-independence at a point — the local no-go test

At a state `x` with two independent allowed directions `u, v`, a single scalar
normalizer requires

```
dV_theta(u)/dW(u) = dV_theta(v)/dW(v) = p(x, theta)
```

wherever the denominators are nonzero.

**Theorem DIR (necessary and sufficient).** A single `p(x,theta) > 0` exists at
`x` **iff** the covectors `dV_theta|_T` and `dW|_T` are proportional with a
positive factor, equivalently

```
dV_theta(u) dW(v) - dV_theta(v) dW(u) = 0     for all u, v in T_x M,
```

i.e. `dV_theta|_T ∧ dW|_T = 0`, with the common ratio positive.

*Proof.* Two covectors on a vector space are proportional iff every `2x2`
determinant of their values on pairs of vectors vanishes; positivity of the
factor is the sign condition. ∎

**If the ratios differ by direction, no one-scalar *global* normalizer exists at
that point.** This is the exact continuum analogue of nonuniform edge rescaling.
*(Checked: `CA11` — for `W_a = (x^2+y^2)/2` and `V_a = (x^2+4y^2)/2` the wedge is
`3` at `(1,1)` and `18` at `(2,3)`, so no `p` exists off the axes.)*

**This is not the end of the story.** §6 shows the obstruction is relative to the
declared *factor decomposition*, and that refining the decomposition dissolves it.

---

## 6. Factor-local generalization — the resolution

The project is **factor-local, not coordinate-separable**. Let the declared
factors be `{S_alpha}` with

```
W(x) = sum_alpha W_alpha(x_{S_alpha}),        V_theta(x) = sum_alpha V_{alpha,theta}(x_{S_alpha}).
```

### 6.1 The architecture

Require normalization **per factor**:

```
dV_{alpha,theta} = p_alpha(x_{S_alpha}, theta) dW_alpha ,      p_alpha > 0,
```

and define the **single** carried settlement

```
dc = sum_alpha  dV_{alpha,theta} / p_alpha  =  sum_alpha dW_alpha  =  dW.
```

**The actor stores no vector.** All factor structure is used only during the
current action's calculation; what persists is the single scalar `c`.

**Theorem FL (factorwise settlement).** Under the per-factor relation, finite
settlement is

```
Delta c = sum_alpha [ W_alpha(before) - W_alpha(after) ],
```

exact, and only **touched** factors need re-evaluation (untouched factors
contribute zero identically).

*Proof.* Sum the per-factor fundamental theorem of calculus; untouched factors
have `dW_alpha = 0` along the path. ∎

### 6.2 Why this strictly extends a single global `p`

Different factors may carry **different** `p_alpha`. A single global `p` requires
them all equal; the factorwise architecture does not.

*Verified instance.* Three coordinates, common reference `x* = (2,2,2)`,
reference scales `s = (1,1,1)`, current scales `u = (1,2,3)` — three
**independent** `sigma` changes:

```
p_0 = s_0^2/u_0^2 = 1      p_1 = 1/4      p_2 = 1/9      (each exactly constant)
```

and `sum_alpha dV_alpha/p_alpha = dW` on **all 126 oriented edges**, with zero
mismatches. A single global `p` **fails**: the edge ratios take **33 distinct
values**. *(Checked: `CA3`, `CA4`, `CA5`.)*

> **This is the central result.** Independent per-coordinate field deformation —
> which Theory I correctly showed is *not* a global scalar revaluation — is
> exactly normalizable factorwise, while the actor still carries one scalar.

### 6.3 The zero condition weakens correspondingly

A **global** conversion needs `dW = 0 ⟹ dV_theta = 0` (hypothesis Z). The
factorwise architecture does **not**.

*Verified instance.* In the same world, the transfer `(0,1,5) -> (1,0,5)` has
`dW = 0` while `dV_theta = 9/8`. A single global `p` would have to be infinite.
Factorwise, `dc = sum_alpha dV_alpha/p_alpha = 0 = dW` — finite and well defined.
*(Checked: `CA6`.)*

> **Hypothesis Z is required only where a single global conversion is claimed.**
> The factorwise requirement is the strictly weaker **per-factor** condition:
> within each factor, `dW_alpha = 0 ⟹ dV_{alpha,theta} = 0`, i.e. the critical
> points of `V_{alpha,theta}` and `W_alpha` coincide inside that factor.

---

## 7. Factorwise monotone dynamic fields

Study

```
V_{alpha,theta} = f_{alpha,theta}(W_alpha) + k_{alpha,theta},
```

with `f_{alpha,theta}` strictly monotone on the reachable range of factor
`alpha`. Then `dV_alpha = f'_{alpha,theta}(W_alpha) dW_alpha`, so the candidate
local normalizer is

```
p_alpha = f'_{alpha,theta}(W_alpha).
```

**Points where `f' = 0` must be handled explicitly.** Strict monotonicity gives
only `f' >= 0` (witness `f(w) = w^3`, `f'(0) = 0`). Where `f'_alpha = 0` the
division is undefined, so the admissible class requires **`f'_{alpha,theta} > 0`
on the reachable range**, not merely strict monotonicity.

**Theorem FM (exact finite settlement in the monotone class).** For finite factor
changes,

```
Delta c_alpha = W_alpha(before) - W_alpha(after),        NOT   Delta V_alpha / p_alpha(start).
```

*Proof.* The first is `∫ dW_alpha` by the fundamental theorem of calculus. The
second is not refinement invariant (§1) and therefore cannot be a settlement at
all: subdividing changes its value. ∎

**Two sub-classes, with different computational consequences.**

| sub-class | `p_alpha` | finite rule |
|---|---|---|
| **affine** `f_{alpha,theta}(w) = p_alpha w + k` | constant in `x` | `Delta c_alpha = Delta V_alpha / p_alpha` is **exact** — the actor may divide directly |
| **strictly monotone, nonlinear** | varies with `x_{S_alpha}` | the actor must evaluate `W_alpha` at both endpoints; dividing by `p_alpha(start)` mints |

**Properties of the class.**

- **Factor-local valuation is preserved.** `V_theta = sum_alpha f_{alpha,theta}(W_alpha)`
  is factor-additive, so an action's value depends only on touched factors. *(This
  is the decisive contrast with Theory I's `f` applied to the **total** `W`, which
  destroyed locality — the correct move is factorwise, not global.)*
- **EBU's local-action architecture is preserved**: `p_alpha` depends only on that
  factor's own current state and the current field parameters.
- **Different physical factors may change scale and shape independently** — §6.2.
- **One scalar still results**, by summation at calculation time.

---

## 8. Current EBU magnitude versus persistent settlement

These must not be confused. For a finite factor transition with
`Delta W_alpha != 0` define

```
p_eff,alpha = Delta V_{alpha,theta} / Delta W_alpha ,      so   Delta V_alpha = p_eff,alpha Delta W_alpha  exactly.
```

An action touching several factors generally has **different** `p_eff,alpha`.

**Theorem NW (no global nominal wallet).** If two factors touched by an action
have `p_eff,alpha != p_eff,beta`, then no single nominal wallet value
`B_current = q c` faithfully represents all current EBU magnitudes of that action.

*Proof.* `B_current = qc` and `E = q Delta c` would force
`Delta V_alpha / Delta W_alpha = q` for every touched factor. ∎

**This is acceptable, and is the architecture.** The actor carries only `c`, and
converts the **currently proposed** action into capacity units from the touched
factors. **No global revaluation of the wallet is ever performed.** The edge-level
conversion is not free either:

**Theorem PE (p_eff is determined, not fitted).** For an edge,

```
p_eff(e) = sum_alpha p_alpha * Delta W_alpha  /  sum_alpha Delta W_alpha ,
```

the `Delta W`-weighted average of the declared factor normalizers. *(Checked:
`CA7`, exact on every edge of the 3-cell world.)*

> This restores non-vacuity. `p_eff` is **not** an arbitrary edge lookup table; it
> is forced by the declared local factor rule.

---

## 9. Action-specific current affordability

Affordability is evaluated **directly in canonical capacity units**:

```
c_i + Delta c_i(G) >= 0 ,      Delta c_i(G) = sum_alpha [ W_alpha(before) - W_alpha(after) ]
```

over the factors the group touches, with the owner attribution of §13.

Consequences: there is **no separately revalued `B_current`**; the actor carries
only `c_i`; each candidate action is translated into `c`-units at decision time;
current field information is used locally in that translation; and at a frozen
field the rule reduces to ordinary V1 (§12).

**Exact equivalence class.** Deciding in `c`-units agrees with comparing current
EBU receipts against a revalued wallet **iff all factors touched by the action
share one common `p_eff`**. *(Checked: `CA13` — in the `u = (1,2,3)` world there
exist edges touching factors with `p_alpha ∈ {1, 1/4}` and `{1/4, 1/9}`, for which
no single `q` is valid, while `Delta c` remains a single well-defined scalar.)*

Outside that class the two rules differ, and **the `c`-unit rule is the correct
one**, because it is the one that telescopes and is refinement invariant.

---

## 10. Discrete graph analogue

Fix canonical `W = V_{theta_0}` on the vertices. For every field and edge
`e : x -> y`, write `Delta W(e) = W(x) - W(y)` and
`E_theta(e) = V_theta(x) - V_theta(y)`.

For a finite positive **global** conversion on that edge:

```
required zero condition:    E_theta(e) = 0  <=>  Delta W(e) = 0
required orientation:       sign E_theta(e) = sign Delta W(e)
exact conversion:           p_eff(theta, e) = E_theta(e) / Delta W(e) > 0.
```

**But `p_eff` fitted edge by edge is vacuous** (at a frozen field `s = E` is
already exact, so per-edge weights carry no information). It is admissible only
when it *arises from* a declared local rule

```
p_eff = P( local physical state, local field parameters, touched factors, declared local constraints ).
```

Theorem PE (§8) supplies exactly that: `p_eff(e)` is the `Delta W`-weighted
average of the declared factor normalizers. The discrete and continuous
statements therefore agree: **the edge conversion is a consequence of the
factorwise rule, never an independent fit.**

Note also that on a sparse action graph the edge conditions are *weaker* than the
differential conditions of §3 and §5 — the graph only constrains transitions it
actually realizes.

---

## 11. Topological consistency

Because `W` is canonical and declared, `s(e) = Delta W(e)` is exact **by
construction**, so

```
sum_{e in cycle} s(e) = 0
```

on every reachable cycle, sparse graphs included — telescoping is indifferent to
sparsity.

**What graph cohomology is still needed for** — and it is not existence:

1. **Checking a proposed normalizer when `W` is not given.** If someone proposes
   a local `p` and claims `dV_theta/p` is a settlement, exactness must be verified:
   zero circulation on a fundamental cycle basis, `m - n + 1` checks rather than
   all cycles.
2. **Auditing local implementations.** Confirming that an implemented local rule
   actually reproduces `Delta W` on every edge.
3. **Detecting violations of exactness** introduced by a bug or a non-conservative
   rule.

> Cohomology is a **verification** tool here, not an existence tool. It must
> **not** be used to pick an arbitrary non-canonical `W` — that is precisely the
> mistake the audit exposed in Theory I.

---

## 12. Static V1 recovery

Freeze `theta = theta_0` and normalize `W = V_{theta_0}`, `p = 1`. Then for every
finite action

```
Delta c = W(before) - W(after) = V_{theta_0}(before) - V_{theta_0}(after) = E_{theta_0},
```

exactly — Capacity V1.

**Simultaneous actions, per-owner.** Because `W = V_{theta_0}` *identically as
functions*, `grad W = grad V_{theta_0}` at **every point of the common path**, not
merely at lattice vertices. Hence the `W`-path receipts coincide with the V1
common-path receipts:

*Verified:* with `sigma = (1,1,2,1)`, baseline `(9, 23/2, 10, 19/2)` and group
`{0->1 by 1, 2->3 by 1/2}`, the `W`-path receipts are `(-7/2, 3/32)` — **identical**
to the V1 receipts — and close on `Delta W = -109/32` exactly. *(Checked: `CA12`.)*

> This closes the audit's Finding 5. Its objection applied to a **topological-order
> `W`**, which has no continuous extension. The canonical `W = V_{theta_0}` has one
> by construction.

---

## 13. Simultaneous group actions

Along the group path `x(lambda) = x + lambda delta_G`, the capacity-coordinate
receipts are

```
C_a = - ∫_0^1  grad W(x(lambda))^T delta_a  d lambda ,        sum_a C_a = W(x) - W(x + delta_G),
```

by the fundamental theorem of calculus. The current-EBU receipts are
`R_a = - ∫ grad V_theta^T delta_a`.

Under factorwise normalizers, `grad V_theta` equals `grad W` scaled **factor by
factor**, so writing `R_{a,alpha}` for the factor-`alpha` part of `a`'s receipt:

```
C_a = sum_alpha R_{a,alpha} / p_alpha .
```

| situation | conversion |
|---|---|
| all touched factors share one `p` | **one scalar converts every receipt**: `C_a = R_a / p` |
| factors carry different `p_alpha` | **factor-specific conversion is required** — still local, still one scalar out |
| special cancellation | a common factor can exist **accidentally**: with `W = sum x_i^2/2`, `f(w) = w^2/2`, baseline `(3,0,2,1)`, group `{0->1 by 1, 2->3 by 2}`, the profiles `3-2s` and `2-8s` are not proportional yet both receipts share the factor `37/6` |

**Not overgeneralized:** a single counterexample does not establish universal
impossibility, and the accidental-cancellation witness shows why. The exact
per-group criterion is `∫ (f'(W) - p) omega_a = 0` for every action `a`.

---

## 14. Moving field versus moving physical state

The golden separation is preserved:

```
actor action              ->   changes x
external field evolution  ->   changes theta
```

and **what the actor did is not what happened to the physical world**.

Field-only change carries **no** actor settlement — under the canonical
architecture this is automatic, since `Delta c = W(before) - W(after)` depends on
`W = V_{theta_0}` and the physical states alone, and a field move changes neither.
External revaluation goes to the external ledger.

The **next** actor action is nevertheless evaluated using the new current field:
the current `V_theta` and the current `p_alpha` enter the translation of that
action into `c`-units. **No historical field vector is stored** — only the
declared reference potential, which is a model constant, and the single scalar
`c`.

---

## 15. Gaussian specialization

```
V_theta(x) = 1/2 sum_i ( (x_i - x*_i(theta)) / sigma_i(theta) )^2 ,      W = V_{theta_0}.
```

With Level-1 (one coordinate per factor), `W_i = ((x_i - m_i)/s_i)^2/2` and
`V_i = ((x_i - t_i)/u_i)^2/2`, so

```
p_i(x_i) = dV_i/dW_i = (s_i^2/u_i^2) * (x_i - t_i)/(x_i - m_i).
```

| case | verdict |
|---|---|
| **A. common `sigma` scaling** | works; all `p_i` equal — also a global scalar revaluation |
| **B. independent `sigma_i` changes, fixed reference** | **works factorwise**, `p_i = s_i^2/u_i^2` constant and different; a single global `p` fails. *(Checked: `CA3`–`CA5`)* |
| **C. moving `x*_i`** | **fails** whenever the reachable range of coordinate `i` straddles the interval between `m_i` and `t_i`: the ratio changes sign. Admissible only on one-sided reachable ranges. *(Checked: `CA10`)* |
| **D. conservation slice** | **no exception needed.** The per-factor relation is one-dimensional and holds for every `dx_i`, hence on any slice. This is a strict simplification over the global-`p` analysis, where the slice was load-bearing |
| **E. one-dimensional reachable slices** | per-coordinate reasoning is unaffected |
| **F. sparse action graphs** | the differential conditions are *stronger* than needed; a sparse graph only constrains the transitions it realizes, so more families qualify |

**Where `grad_T V_theta = p grad_T W` holds with one `p`:** only case A (and the
invisible reference motions along `span(sigma_i^2)`). **Where factorwise
`dV_i = p_i dW_i` holds although one global `p` fails:** case B — the main gain —
and any combination of independent scale changes with fixed references.

> A factorwise solution is acceptable precisely because the actor still stores
> **one** scalar `c`. No capacity vector is introduced anywhere.

---

## 16. The no-go boundary

**Theorem NG (exact boundary).** Relative to a declared factor decomposition
`{S_alpha}` and the canonical `W = V_{theta_0}`, a one-scalar canonical atomic
capacity exists **iff** for every factor `alpha`, every field `theta` in the
declared family and every reachable `x`:

> **(N1) zeros coincide within the factor:** `dW_alpha = 0 ⟺ dV_{alpha,theta} = 0`;
>
> **(N2) gradients are positively proportional within the factor:**
> `grad V_{alpha,theta} = p_alpha grad W_alpha` with `p_alpha > 0` on the allowed
> directions inside `S_alpha`.

Equivalently, on a connected reachable factor range: **`V_{alpha,theta}` is a
strictly increasing function of `W_alpha` with strictly positive derivative.**

Settlement is then `Delta c = sum_alpha [W_alpha(before) - W_alpha(after)]`:
exact, refinement invariant, cycle closing, history free, one scalar, and V1 at
`theta = theta_0`.

**The obstruction, stated exactly.** If at some reachable `x` two allowed
directions **inside one factor** give different ratios — `dV_alpha|_T ∧ dW_alpha|_T
!= 0` — then no `p_alpha` exists and one scalar cannot faithfully represent that
field **under the declared decomposition**. Exactly two remedies:

1. **Refine the factor decomposition.** For a one-dimensional factor the
   directional test is vacuous, so `p_alpha` always exists given (N1) and sign
   agreement. The obstruction is therefore *relative to the declaration*, not
   absolute. *(Checked: `CA11` — the anisotropic 2-D factor fails, and both of its
   1-D refinements succeed.)*
2. **Declare the field outside the admissible class.**

**Which architectural requirements fail outside the class** — stated precisely,
and **not** as "no scalar wallet can ever exist":

| failing requirement | why |
|---|---|
| positive local conversion | `p_alpha` would have to take two values at one state |
| factor-local valuation | resolving it needs information from outside the factor |
| refinement invariance | any endpoint-fitted repair is resolution dependent (§1) |

What does **not** fail: exactness, closed-cycle closure and history-freedom, all
of which follow from `Delta c = Delta W` for *any* declared `W`. **The failure is
of faithful normalization, not of scalar settlement.**

---

## 17. Entropy analogy — final form

Retained only as this precise mathematical statement:

> a local physical normalization converts a current process valuation into the
> differential of a persistent state coordinate,

comparing `dS = delta Q_rev / T` with `dc = dV_theta / p_local = dW`.

**Emphasized, and not claimed otherwise:** frozen-field EBU is already exact — it
needs no integrating factor, which is the sharpest disanalogy; EBU is not heat;
`c`/`W` is not entropy; `p` is not temperature (it has no zero point, only ratio
meaning); and **no second-law monotonicity is claimed anywhere**.

The genuinely transferable lesson is negative and is the one used throughout:

> **never approximate a finite transition by dividing total change by a varying
> endpoint factor.**

---

## 18. No global viability-boundary language

No `Lambda`, no universal burden ceiling, and no global viability criterion is
introduced. The Gaussian field may remain unbounded, exactly as gravitational and
electrostatic potentials are. The local rule acts continuously and atomically.

Where a specific physical domain has a genuine hard constraint — nonnegative
stock, route capacity, conservation — that constraint is represented explicitly as
**physics**. It is not a universal component of EBU capacity theory.

---

## 19. Decisive answers

**Q1. Is there a CANONICAL persistent scalar `W` fixed by static EBU authority?**
> **YES.** `W := V_{theta_0}`, unique up to one positive scale and one additive
> constant on each connected reachable component (Theorem CAN). The scale and
> constant are economically irrelevant by same-ruler cancellation.

**Q2. Can genuinely changing fields be locally normalized to `W` using present
physical information only?**
> **YES, exactly on the class of Theorem NG** — factorwise, with
> `p_alpha = f'_{alpha,theta}(W_alpha) > 0`. The normalizer reads only the current
> local factor state and the current field parameters.

**Q3. Does factorwise normalization allow nonuniform dynamic field changes while
the actor still stores only ONE scalar `c`?**
> **YES.** Independent per-coordinate `sigma` changes are admissible with
> `p_i = s_i^2/u_i^2` all different, while a single global `p` fails. The actor
> stores one scalar; factor structure is used only during the current
> calculation. *(Verified on all 126 edges.)*

**Q4. Is finite settlement invariant under arbitrary action subdivision?**
> **YES**, and more strongly, refinement invariance **characterizes** `dc = dW`
> (Theorem RI). The prohibited endpoint rule is resolution dependent and returns
> a different number at every subdivision.

**Q5. Does the theory recover V1 exactly when `theta` is frozen?**
> **YES**, including simultaneous per-owner common-path receipts, with the
> identities holding along the **continuous** path because `W = V_{theta_0}`
> identically.

**Q6. Can current affordability be decided directly in `c`-units without globally
revaluing the wallet?**
> **YES.** `c_i + Delta c_i(G) >= 0` with `Delta c_i(G)` computed from the touched
> factors. It coincides with comparing current EBU receipts **iff** all touched
> factors share one `p_eff`; outside that class the `c`-unit rule is the correct
> one.

**Q7. Which Gaussian field changes satisfy the theory?**
> Common `sigma` scaling; **independent per-coordinate `sigma` changes with fixed
> references** (the main gain); reference motion along `span(sigma_i^2)`, which is
> invisible on the conservation slice. **Excluded:** reference motion that makes a
> coordinate's reachable range straddle the old and new reference, and anisotropic
> deformation *inside* a declared multi-coordinate factor.

**Q8. What exact class of dynamic field deformation makes one-scalar EBU capacity
impossible?**
> Exactly those violating (N1) or (N2) of Theorem NG **for every admissible
> refinement of the factor decomposition**: a field whose restriction to some
> irreducible factor is not a strictly-increasing, strictly-positive-derivative
> reparametrization of that factor's reference potential. Concretely: sign
> reversal inside a factor (straddling a moved reference), a vanishing `f'`, and
> direction-dependent ratios inside an irreducible factor.

**Q9. Is any history vector, source portfolio or global future optimization
required?**
> **NO.** The actor stores one scalar `c`. The reference potential `W = V_{theta_0}`
> is a declared model constant evaluated at the current local state; `p_alpha`
> reads only the current local factor state and current field parameters. No
> trajectory, no source portfolio, no dependency vector, no global optimization.

---

## 20. FINAL VERDICT

> # CANONICAL ATOMIC DYNAMIC EBU CAPACITY SOLVED

**The necessary-and-sufficient theorem.** Given a declared factor decomposition
`{S_alpha}` and the canonical coordinate `W := V_{theta_0} = sum_alpha W_alpha`
(unique up to `aW + b`, `a > 0`, by Theorem CAN), a one-scalar canonical atomic
capacity coordinate exists **if and only if**, for every factor `alpha`, every
declared field `theta` and every reachable state:

> **(N1)** `dW_alpha = 0  ⟺  dV_{alpha,theta} = 0` inside the factor, **and**
>
> **(N2)** `grad V_{alpha,theta} = p_alpha(x_{S_alpha}, theta) * grad W_alpha`
> with `p_alpha > 0` on the allowed directions inside the factor
>
> — equivalently, `V_{alpha,theta}` is a strictly increasing function of
> `W_alpha` with strictly positive derivative on that factor's reachable range.

Settlement is then

```
dc = sum_alpha dV_{alpha,theta} / p_alpha = dW ,
Delta c = sum_alpha [ W_alpha(before) - W_alpha(after) ],
```

which is **exact for finite actions, invariant under arbitrary subdivision, zero
on every closed cycle, free of any history vector, a single scalar per actor, and
exactly Capacity V1 — receipts included — when `theta = theta_0`.**

**The boundary, stated with equal prominence.** The class is not all fields. It
excludes reference motion that reverses a factor's gradient sign over the
reachable range, points where `f'_{alpha,theta} = 0`, and direction-dependent
ratios inside an irreducible factor. Outside it, what fails is **faithful local
normalization** — positive local conversion and factor-local valuation — **not**
exactness, cycle closure or history-freedom, which hold for any declared `W`.

**What this supersedes.** Theory I's Theorem DS answered the wrong question
(existence of *some* ordering) and its L3 was too restrictive; both are withdrawn
in favour of the above. Theory I's preserved results — fixed-field exact EBU,
static V1, the scalar-revaluation theorem, the magnitude-faithful no-go under
nonuniform *global* scaling, same-ruler cancellation and closed-cycle telescoping
for a declared `W` — stand unchanged.

**No mechanism is adopted, implemented or preregistered, and Stage A/B is not
authorized by this report.**
