# EBU WORKING THEORY BASELINE

Status:
    WORKING RESEARCH BASELINE —
    NOT FROZEN PHYSICAL FOUNDATION

This document records the **current post-freeze research status** of the EBU
programme. It is self-contained: a future research, implementation, book or
experiment task should be able to read this one file, plus the frozen
foundation, and know what is settled, what is conditional, what is open, and
what must never drift.

---

## 0. AUTHORITY HIERARCHY

| rank | source | role |
|---|---|---|
| **1** | `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | **FROZEN PHYSICAL FOUNDATION.** Wins every conflict |
| **2** | `docs/scientific_record/` (branch `publication/scientific-record`) | historical provenance — audits, gates, evidence manifest |
| **3** | **this document** | current post-freeze research status |
| **4** | exploratory reports / AI task transcripts | candidate claims only, never authority |

Frozen foundation coordinates:

```
branch   origin/publication/physical-foundation
commit   c63d6833da10a75ef66db11f99fb5b5c68d94c5e
canonical docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md
sha256   6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
```

Scientific record: `publication/scientific-record` at
`481753895509524c9d2674d1880d87712bb0ec18`.

> **If this document conflicts with the frozen foundation, THE FROZEN
> FOUNDATION WINS**, and this document is the thing that must be corrected.

Nothing marked CONDITIONAL, OPEN or EXPERIMENTAL here may be promoted into the
physical core without an explicit independent scientific gate.

---

## 1. DO NOT DRIFT

Future tasks must **NOT**:

- modify the frozen `V` / `mu` / `E` / `f` hierarchy;
- protect the word **"burden"** against physics;
- equate `sigma` with a marginal standard deviation in general;
- derive `H` from the same `P` used to test `H` against `K`;
- treat `K = beta H` as universally validated;
- treat `beta` or `kappa` as universal;
- treat E1a as a discovery of new statistical mechanics;
- keep using the **superseded fixed-`B0`** E1 temperature design;
- claim `1 BU = k_B T_ref`;
- promote `D + Q_skew` dynamics, SDEs, or quasipotentials into the EBU core;
- reintroduce `c_i >= 0`;
- reintroduce affordability;
- reprice completed historical `c_i`;
- confuse **permanence** with **commensurability**;
- confuse the dynamic Jacobian `J_dyn` with the Hessian `H`;
- confuse local `mu` / `f` with exact finite `E`.

---

## 2. CORE EBU — PRESERVED EXACTLY

Top of the scientific hierarchy. Nothing discovered after the freeze may
replace these.

```
mu = grad_x V

E  = V_pre - V_post

E  = - integral_gamma grad V . dx        (fixed theta, single-valued C1 V,
                                          admissible piecewise-smooth path)

f  = - grad V^T dx/dq                    (differentiable physical action path)
```

Gaussian Level 1, and the frozen diagonal declaration:

```
V(x) = 1/2 (x - x*)^T H (x - x*)         H = diag(1/sigma_i^2)
```

Exact Gaussian finite theorem:

```
E = - mu^T Delta - 1/2 Delta^T H Delta
```

This is exact — no approximation, no small-action assumption. It is **not** the
definition of EBU; the definition remains `E = V_pre - V_post`.

**Authority: FROZEN CORE.**

---

## 3. `V` IS THE PROTECTED OBJECT; "BURDEN" IS NOT

`V` is the canonical EBU potential. The word **"burden"** is intuitive and
historical, inherited from the original homeostatic penalty interpretation. It
carries **no protected physical meaning**.

Future physics may identify `V` with, or relate `V` to:

- free-energy excess;
- entropy deficit;
- quasipotential;
- viability potential;
- statistical cost;
- another physical state potential.

Those are **interpretations of `V`**, not renamings of it.

**Never rename canonical `V`, `mu`, `E`, `f`, `H`.** If the evidence says the
best physical identification of `V` is "free-energy excess", record that as an
interpretation and keep the symbol.

Current best-supported interpretation, outside the frozen core: **`V`
corresponds to a free-energy excess, equivalently a normalised entropy deficit
under the Onsager mapping.** Status: CONDITIONAL.

---

## 4. UNITS

Frozen normalised Gaussian units:

```
[x_i] = [x_i*] = [sigma_i] = U_i
[V]   = [E]    = 1                       (dimensionless)
[mu_i] = U_i^-1
[H_ij] = (U_i U_j)^-1
[f]    = 1/[q]
```

A research-layer scaling `V_phys = B0 V_norm` is mathematically consistent:
every frozen identity is homogeneous of degree one in `B0`, so all theorems
survive up to that one common scale.

> **`B0` / BU calibration is an OPEN INTERPRETATION-LAYER QUESTION.**
> It is not part of the core and not part of E1a.

**CRITICAL — RETRACTED CLAIM.** Do **not** claim `1 BU = k_B T_ref`. That
proposal created an energy-valued unit and reintroduced a temperature-dependent
`kappa`, which destroys the very commensurability the programme requires. It
was withdrawn by the E1a correction. E1a keeps normalised EBU **dimensionless**
and tests `E = Delta s_med / k_B` inside the canonical benchmark, where
`Delta s_med` is the entropy delivered to the thermal reservoir. It is **NOT** total
stochastic entropy production — see §14.3.

---

## 5. FIELD GEOMETRY `H` AND MODAL `sigma`

```
H = Hess V
```

For symmetric positive definite `H`:

```
H = Q Lambda Q^T          q_r = eigenvectors (natural modes)
                          lambda_r = mode stiffnesses
z = Q^T (x - x*)          sigma_r = 1 / sqrt(lambda_r)
V = 1/2 sum_r (z_r / sigma_r)^2
```

> **`sigma` is fundamentally a MODE / DIRECTION scale in the general quadratic
> geometry.** The frozen diagonal Level-1 case is the special case in which the
> declared coordinates already align with the normal modes.

**Status: ESTABLISHED MATHEMATICAL GENERALISATION.** It does **not** replace the
frozen diagonal declaration.

**`sigma` is NOT generally a marginal standard deviation.** It equals one only
in the special case of independent, unconstrained, exactly Gaussian coordinates
with `kappa = k_B`. Under conservation constraints or correlation, the
observable object is the restricted precision / curvature matrix on the
accessible directions, not one marginal variance per coordinate.

**Conservation and accessible directions.** For constraints `C x = const`, build
an orthonormal basis `Q` of `{Delta x : C Delta x = 0}` and work with
`H_T = Q^T H Q`. Curvature outside the accessible subspace is **unobservable**
from that system: `H` and `H + c 1 1^T` give identical `V` on every accessible
state. Document discarded directions; never treat an inaccessible direction as
an observed zero-curvature mode.

---

## 6. MARGINAL POTENTIAL, DIRECTIONAL VALUE, FINITE EBU

Three distinct objects, never merged:

| object | meaning |
|---|---|
| `mu = grad V` | local marginal potential |
| `f = - grad V^T dx/dq` | directional differential value along an action path |
| `E = V_pre - V_post` | **exact finite EBU** |

`f` is a mathematical directional derivative. **It is not a mechanical law of
motion, not a measured force, and not a dynamical response law.** Naming it a
"force" is a convention of this programme.

`E` is **not** the local gradient approximation except in the infinitesimal
limit. The first-order term `- mu^T Delta` can even have the opposite sign to
the exact finite `E`.

**Loss-aware form.** For `eta < 1` the declared transition is
`source -q, destination +eta q, sink +(1-eta) q`, and

```
f_e = mu_s - eta mu_d - (1-eta) mu_sink
```

The sink term vanishes exactly when `(1-eta) mu_sink = 0`, satisfied
independently by `eta = 1` (zero coefficient) or `mu_sink = 0` (unvalued
coordinate). `eta = 1` does **not** imply `mu_sink = 0`. The sink marginal must
appear in the general formula; its contribution may vanish at particular states.

---

## 7. FACTORS, MÖBIUS, COARSE-GRAINING

**Factor potentials.** For `V = sum_alpha phi_alpha(x_{S_alpha})`: gradients add;
`E` remains the endpoint difference; unchanged factors cancel exactly; a touched
coupled factor must be reevaluated **as a whole**. Coordinate separability is not
required.

**Möbius / interaction structure.** `v(G) = sum_{S subset G} I(S)` decomposes
already-defined subset values. **It creates no additional EBU.**

The Möbius coefficient is the negative mixed **finite difference**:

```
I(A) = - (mixed finite difference of V over the increments in A)
     = - integral_{[0,1]^A} D^|A| V [Delta_a1, ..., Delta_ar] ds
```

For quadratic `V` with fixed additive increments the highest nonzero order is
**two**, with `I({a,b}) = - Delta_a^T H Delta_b`. **Both hypotheses are
load-bearing**; fixed additive increments alone do not bound the order.

Higher-order Möbius terms are **finite-difference diagnostics of
nonquadraticity**, not point derivatives, and not cumulants. A nonzero
third-order coefficient shows the quadratic representation fails **on the tested
finite configuration**. **One zero coefficient proves nothing** — a quartic `V`
can give exactly zero at a particular base point.

**Quadratic coarse-graining theorem.** For `V_y(y) = min{V_x(x) : A x = y}` with
quadratic `V_x`, `H_x` positive definite and `A` of full row rank:

```
H_y = (A H_x^-1 A^T)^-1
```

Plain reading: **stiffness does not carry forward; slackness does.** This is
the Schur complement, and it specialises to `sigma_B^2 = sum_i sigma_i^2` for
sum-aggregation of independent coordinates. It composes exactly along chains.

**Do not claim quadratic closure generally** — coarse-graining a quartic gives
a quartic. Splitting / disaggregation is underdetermined and requires new
physical information.

**Status: ESTABLISHED under the stated assumptions.**

---

## 8. WHY ENTROPY ENTERED THE PROGRAMME

This section must stay historically and scientifically correct.

**Entropy did NOT enter because of actor incentives.** It entered because **the
physical field may change.**

For `theta0 -> theta1` the field may change `sigma(theta)`, `H(theta)`,
`x*(theta)` and therefore `V_theta`. The actor-account requirement had two
parts, and they are different:

**PERMANENCE.** An action credited `+5` at execution remains `+5` forever. No
later field change may reprice that completed historical contribution. *This is
bookkeeping — a recording convention, and it is free.*

**COMMENSURABILITY.** `+5` earned at `theta0` and `+5` earned at `theta1` must
represent the **same physical quantity** before they may be added directly.
*This is a physical claim, and it is not free.*

A historical scalar account requires **one common physical coordinate across
changing fields**. Entropy / normalised freedom was investigated as that
candidate.

> **Permanence is not commensurability. Confusing them is a named drift
> failure.**

---

## 9. ENTROPY / FREEDOM CANDIDATE

```
S_theta(x) = S_eq(theta) - kappa V_theta(x)          F = S / kappa
```

At fixed `theta`, if the candidate is physically valid:

```
Delta F_actor = E_theta
```

Historical account:

```
c_i = c_i0 + sum of executed Delta F_i
```

with **no repricing**, **no `c_i >= 0`**, and **no affordability gate**.

Assumptions carried from the frozen foundation: fixed `theta`, `S_eq(theta)`
spatially constant, `kappa` constant and nonzero, `kappa > 0` for the intended
deficit orientation. Variable `kappa` or spatially varying `S_eq` introduces
extra derivative terms and the relation no longer holds as written.

**Status: CONDITIONAL PHYSICAL IDENTIFICATION. Not frozen core.**

---

## 10. LOCAL ENTROPY THEOREM (P1-B)

Let `S` be an independently physically justified entropy-like state function,
`C3` near an accessible equilibrium `x*`. If `grad S(x*) = 0` and, on the
physically accessible tangent directions,

```
A := - Hess S(x*) = kappa H
```

then

```
S_eq - S(x) = kappa V(x) + O(||x - x*||^3)
```

**Classification: LOCAL SECOND-ORDER CONDITIONAL THEOREM.**

Global equality remains **OPEN**. For exact equality on a finite or open domain
the corresponding quadratic identity must hold **throughout that domain**;
`C3` regularity alone does not exclude fourth- and higher-order terms.

This is the high-water mark of P1. It is conditional on a physical `S` existing
at all, and on `A = kappa H`, which is itself underived.

---

## 11. EINSTEIN / BOLTZMANN BRIDGE

Let `P_theta(x)` be an **independently measured** macrostate probability, and

```
J_prob,theta(x) = - ln [ P_theta(x) / P_theta(x*_theta) ]
```

`J_prob` is the finite log-probability rarity cost: dimensionless, defined
whenever `P(x*) > 0`. **It is distinct from a large-deviation rate function `I`,
which is asymptotic and meaningless without its speed `a_N`.** Do not identify
`J_prob` with `I` without stating the speed. Do not use `J_prob` for a Jacobian
or a thermodynamic flux.

Where the Einstein/Boltzmann physical relation is independently valid:

```
J_prob = [S_eq - S] / k_B
```

Combining with the entropy candidate:

```
J_prob = beta V              beta = kappa / k_B
```

**FORBIDDEN:** defining `P` proportional to `exp(-V)` and treating the resulting
agreement as evidence. That is circular and is explicitly prohibited by the
frozen foundation.

**Do not claim this relation is universal.**

---

## 12. CENTRAL CURRENT BRIDGE

General research target:

```
J_prob,theta  ?=  beta V_theta
```

Locally, with `K_theta := Hess J_prob,theta` and `H_theta := Hess V_theta`:

```
K_theta  ?=  beta H_theta        (on accessible directions)
```

If true, then `H` and `K` share:

- the same normal modes;
- the same eigenvectors;
- the same eigenvalue ratios;
- the same coupling geometry;
- one overall scale difference only.

This is far more falsifiable than fitting one scalar, and **the shape can be
tested while the overall scale remains unknown**. Recommended scale-free
diagnostics: trace-normalised shape comparison, and the **whitened** spectral
spread — eigenvalues of `H_T^{-1/2} K_T H_T^{-1/2}`, all equal iff
`K_T = beta H_T`. The naive `H^-1 K` eigensystem loses roughly half its digits
at the null and must not be used.

**Status: CONDITIONAL THEOREM / EXPERIMENTAL TARGET.
NOT experimentally established in general.**

---

## 13. THE CHANGING-FIELD PROBLEM

| case | situation | consequence |
|---|---|---|
| **A** | `K_theta` not proportional to `H_theta` | geometry / bridge **failure** |
| **B** | `K_theta = beta(theta) H_theta` | local geometry works; units are **field-specific**; raw historical `E` is **not** automatically commensurable |
| **C** | `K_theta = beta H_theta` with **one** `beta` | common field scale in the tested domain |

**Only case C supports direct accumulation of raw `E` as one normalised
entropy/freedom contribution coordinate**, and then only subject to the entropy
gate of §11.

---

## 14. E1a — CURRENT EXPERIMENTAL FRONTIER

**E1a — CANONICAL EINSTEIN–EBU BENCHMARK REALISATION.**

Selected system: multi-dimensional optical trap; single micron-scale bead; water;
thermal equilibrium; lateral `x`/`y` plane accessible. The axial `z` direction is
**designed out** and documented as discarded, not treated as an observed
zero-curvature mode.

Two independent branches, compared only at the end:

**BRANCH A — PHYSICAL FIELD**
`U_theta` from mechanical force–displacement data (Stokes drag);
`T_theta` from calibrated thermometry.
**Neither uses the position histogram.**

**BRANCH B — STATISTICS**
`P_theta` from position observations; derives `J_prob` and `K`.
**Never uses `V` or `H`.**

Branch A output is hashed and published **before** Branch B is unblinded. The
power-spectrum method of stiffness calibration is **forbidden** here: it uses
the fluctuation data and would close the circular loop.

### 14.1 Corrected thermal normalisation — SUPERSEDES the `B0` design

```
V_theta(x) := [ U_theta(x) - U_theta(x*_theta) ] / (k_B T_theta)
```

Under canonical equilibrium statistical mechanics this gives, identically,

```
J_prob,theta(x) = V_theta(x)
```

so **E1a predicts `beta = 1` and `kappa = k_B` at EVERY tested `theta`.**

Energy Hessian `H_U,theta := Hess U_theta` (mechanical). EBU Hessian:

```
H_theta = H_U,theta / (k_B T_theta)

sigma_r,theta^2 = k_B T_theta / k_r,theta
```

which is the **equipartition variance** in this benchmark. Preserve the general
warning of §5: `sigma` is not generally a marginal standard deviation. **E1a
lies exactly in the special domain where it is.**

> **SUPERSEDED — DO NOT USE.** The earlier E1 design fixed an arbitrary energy
> scale `B0`, giving `V = Delta U / B0` and therefore
> `beta_theta = B0 / (k_B T_theta)` and `kappa_theta = B0 / T_theta`. That makes
> `kappa` temperature-dependent and destroys cross-field commensurability — the
> exact property the programme needs. Retained here only as design history.

### 14.2 Field conditions

| arm | change | prediction |
|---|---|---|
| `theta0` | baseline | `K = H`, `beta = 1` |
| `theta1` | laser power / stiffness | `H` changes; **`beta = 1`** |
| `theta2` | ellipticity / mode rotation | `K` and `H` rotate together; **`beta = 1`** |
| `theta3` | temperature | `H` changes through division by `T`; `sigma` changes; **`beta = 1`, `kappa = k_B` unchanged** |

> **Temperature is NOT a positive-control `beta`-changing arm. It is THE
> STRONGEST CHANGING-FIELD COMMENSURABILITY TEST.**

The positive control for scale-detection sensitivity is instead a **blinded
analysis control**: Branch A's declared scale is multiplied by a pre-declared
hidden factor `c`, on a duplicate branch that never touches primary data, and
the analysis must recover `beta = 1/c`.

### 14.3 Action and entropy result

For fixed `theta`, `E_theta = V_theta(x_pre) - V_theta(x_post)`. In the
benchmark `J_prob = V`, so `Delta J_prob = E_theta`.

Under the declared static-equilibrium stochastic-thermodynamic conditions —
conservative overdamped dynamics, fixed field, fixed temperature, a single
reservoir, the stationary equilibrium distribution at both times, and no work
input omitted from the accounting — the entropy bookkeeping is:

```
Delta s_med = + k_B E_theta      entropy delivered to the thermal reservoir
Delta s_sys = - k_B E_theta      stochastic system entropy
Delta s_tot = 0                  TOTAL stochastic entropy production
```

> **`k_B E` is NOT total stochastic entropy production.** The total **vanishes**
> in equilibrium. The two lines above are trajectory identities under those
> conditions, and are distinct from the ensemble-average entropy-production
> rate, which is non-negative with equality exclusively in equilibrium. Nothing
> here generalises to imposed actor actions, driven transitions or
> nonequilibrium initial distributions: each violates one of the conditions.

A **separately derived** constrained-macrostate reading also yields `k_B E`.
With the bead held at `x` and a reservoir of heat capacity `C`:

```
Delta S_constr = k_B E_theta + remainder ,   remainder / leading = U / (2 T C)
```

which is of order `1e-20` for any macroscopic bath, so `Delta S_constr = k_B E`
holds to first order in `U/(T C)`. Derivation and one sourced value:
`docs/e1a/finite_bath_remainder.py`.

**Medium entropy, stochastic system entropy, total stochastic entropy
production and the constrained-macrostate entropy deficit are four different
objects.** They are never equated.

Therefore `+5 EBU` at `theta0` and `+5 EBU` at `theta1` both represent **`+5 k_B`
delivered to the reservoir**, even when their mechanical energy changes differ.
**This is the exact changing-field commensurability property the programme
originally sought.**

### 14.4 Scope — stated plainly

**E1a does NOT discover statistical mechanics.** The proportionality
`J_prob = V` is already predicted by canonical equilibrium physics once the
physically correct thermal normalisation is applied.

E1a **is** a canonical benchmark realisation. If executed successfully it
establishes: that the EBU architecture is compatible with one exact physical
regime; that changing-field entropy commensurability works there; and that the
analysis pipeline survives real experimental systematics.

It does **not** establish universal EBU, universal `beta`, ecosystem or
planetary EBU, natural incentive, or economic optimality.

### 14.5 Status and outstanding item

**E1a v4 DESIGN ADOPTED; IMPLEMENTATION / SYNTHETIC VALIDATION PENDING.**

The v3 synthetic release gate **failed**, and the independent reviews that
followed found defects in the decision rules themselves. The corrected
prospective design is adopted in `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` with
its machine-readable contract `docs/e1a/e1a_v4_design_contract.json`. Those two
are the authoritative prospective sources for E1a decision rules.

Outstanding, in order: **bounded implementation** of the v4 pipeline, then the
**synthetic validation campaign** of design §15.

> The design has **NOT** empirically passed validation, and E1a is **NOT**
> preregistration-ready. The earlier statement that "no new design decision is
> required" is **superseded**: the v4 review changed the procedure.

The suite must retain the fourth-moment gate added after it was discovered that
`theta` mixing across fields differing by a pure scalar is invisible to every
second-order geometry test — a mixture of proportional Gaussians has a
covariance that is still exactly proportional.

---

## 15. E1b — FUTURE HARDER TEST

**E1b — INDEPENDENT PHYSICAL CHALLENGE.** An independently grounded EBU field in
a system where proportionality to probability or entropy is **not** already
built into the known canonical equilibrium normalisation.

**Status: NAMED ONLY. NOT DESIGNED.** Do not invent E1b without a task that
asks for it.

---

## 16. HISTORICAL ACTOR ACCOUNT

`c_i` remains **signed historical attribution**.

If an E1-like entropy/freedom bridge is established for a domain, `c_i` may be
interpreted as **accumulated normalised entropy/freedom contribution in that
domain**. Otherwise `c_i` remains **accumulated EBU attribution only**.

**Never impose `c_i >= 0`. Never reprice completed contributions.**

Per-owner attribution **need not** be closed: there exists a closed physical
loop with zero aggregate change and nonzero owner redistribution, so per-owner
historical attribution is not guaranteed to be a state function of `x`. The
stronger universal claim — that every individual attribution convention is
non-exact — is **not** established and is not required.

---

## 17. ACCOUNTING BOUNDARY

`C + V = constant` is a **CONDITIONAL ACCOUNTING THEOREM**, requiring fixed
field, exact settlement, consistent endpoints, no omitted external physical
event, and no external `C` source or sink.

It is **not** carrier conservation, **not** a thermodynamic law, and **not** a
physical conservation law. No assumption `C >= 0` is used or permitted.

The actor vector remains **path dependent**.

**Do not feed actor, institutional or economic quantities back into `V`, `H` or
`sigma`.** The forbidden backflow list of the frozen foundation stands in full:
`c_i >= 0`, `B_i >= 0`, pre-action affordability, no borrowing, no pooling,
complete-service requirement, persistent economic orders, no partial service,
FIFO, backlog, price, actor utility, welfare, privilege, service priority.

---

## 18. EXPLORATORY DYNAMICS — QUARANTINED

**Do NOT promote into the EBU core:** `D + Q_skew` dynamics, stochastic
differential equations, quasipotentials, or Onsager transport equations.

Useful lessons established, recorded only as lessons:

- **Potential geometry does not itself define a motion law.** The frozen
  Layers 1–3 contain no law of motion; supplying one requires a declared
  mobility or `(D, Q_skew)` pair, which is an extra physical declaration.
- **Oscillation does not automatically invalidate a scalar potential.** A
  complex spectrum rules out a *pure* gradient flow only. Every asymptotically
  stable linear system admits a quadratic Lyapunov potential with
  `A = -(D + Q_skew) H`, `D` positive — so existence is cheap and therefore
  uninformative. The real obstruction at large scales is **non-identifiability**:
  many such potentials exist and nothing physical selects one.
- **Near-equilibrium Onsager consistency was explored successfully.** With
  `X = grad S = - kappa grad V`, the flux law `J_flux = L X` gives
  `D + Q_skew = kappa L`; Onsager reciprocity forces `Q_skew = 0`; and the
  fluctuation–dissipation condition reduces exactly to the standard
  `B B^T = 2 k_B L`.
- **Quasipotential remains future architecture.** `Phi_qp` is external and is
  **not** identified with `V` by definition.
- **`J_dyn` is not `H`.** Community matrices, metabolic-control elasticity
  coefficients and critical-slowing-down eigenvalues are all Jacobian objects.

**Status: EXPLORATORY PHYSICAL INTERPRETATION. NOT ADOPTED EBU THEORY.**

---

## 19. STAGE B

**Status: NOT RESUMED.**

The historical ungated signed-account Stage-B idea remains available. But the
physical claim "`c_i` = accumulated entropy/freedom contribution" requires the
relevant bridge evidence.

**No `c_i >= 0`, no affordability, no debt restriction belongs in the physical
core.**

---

## 20. MASTER THEORY-STATUS TABLE

| concept | equation / object | status | assumptions | authority | allowed claim | prohibited overclaim |
|---|---|---|---|---|---|---|
| `V` | canonical EBU potential | **FROZEN** | declared field potential | foundation | the protected scalar state function | that "burden" is its physical meaning |
| `mu` | `grad V` | **FROZEN** | differentiable `V` | foundation | local marginal potential | a measured physical force |
| `E` | `V_pre - V_post` | **FROZEN** | state function | foundation | exact finite EBU | that a gradient term replaces it |
| `f` | `- grad V^T dx/dq` | **FROZEN** | differentiable action path | foundation | directional differential value | a mechanical law of motion |
| Gaussian Level 1 | `1/2 (x-x*)^T H (x-x*)` | **FROZEN as a hypothesis** | declared `H = diag(1/sigma^2)` | foundation | a constitutive field hypothesis | a universal physical law |
| finite Gaussian theorem | `E = -mu^T D - 1/2 D^T H D` | **FROZEN, exact** | quadratic `V`, fixed increment | foundation | exact, no small-action limit | that first order suffices |
| `H` | `Hess V` | **FROZEN** (+ established generalisation) | symmetric | foundation / baseline | field curvature | that it equals `J_dyn` |
| modal `sigma` | `sigma_r = 1/sqrt(lambda_r)` | **ESTABLISHED GENERALISATION** | `H` positive definite | baseline | `sigma` is a mode scale | that `sigma_i` is a marginal s.d. in general |
| factor potentials | `V = sum phi_alpha` | **FROZEN** | declared factorisation | foundation | touched-factor locality | that a zero in `H` proves no factor |
| Möbius | `I(A)` = negative mixed finite difference | **ESTABLISHED** | defined subset values | baseline | nonquadraticity diagnostic | that it is a point derivative or a cumulant |
| coarse-graining | `H_y = (A H_x^-1 A^T)^-1` | **ESTABLISHED** | quadratic `V`, `H>0`, `A` full row rank | baseline | exact inheritance, composes | general quadratic closure |
| entropy candidate | `S_eq - S = kappa V` | **CONDITIONAL** | fixed `theta`, `S_eq` constant, `kappa` constant | baseline | mathematically compatible | that entropy is thereby established |
| P1-B local theorem | `S_eq - S = kappa V + O(r^3)` | **LOCAL SECOND-ORDER CONDITIONAL** | physical `S`, `C3`, `A = kappa H` | baseline | local approximation | global exactness |
| Einstein/Boltzmann | `J_prob = (S_eq - S)/k_B` | **DOMAIN-DEPENDENT** | ensemble + reservoir assumptions | baseline | valid where derived | universal validity |
| `J_prob` | `-ln[P/P*]` | **DEFINED** | `P` independently measured, `P(x*)>0` | baseline | finite rarity cost | that it equals an LDP `I` without a speed |
| `K` | `Hess J_prob` | **DEFINED** | local smoothness | baseline | statistical rarity curvature | that it is automatically `beta H` |
| `beta` | `kappa / k_B` | **OPEN / conditional** | the bridge holds | baseline | dimensionless scale | universality |
| `K = beta H` | central bridge | **CONDITIONAL / EXPERIMENTAL TARGET** | bridge + accessible directions | baseline | a falsifiable prediction | experimentally established |
| changing-field one `beta` | case C of §13 | **OPEN** | one scale across `theta` | baseline | the commensurability requirement | that it holds anywhere yet |
| **E1a** | canonical benchmark | **v4 DESIGN ADOPTED; IMPL / VALIDATION PENDING** | canonical equilibrium, thermal normalisation | baseline + `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | benchmark realisation | discovery of statistical mechanics; empirical validation |
| **E1b** | independent challenge | **NAMED ONLY** | — | baseline | a future gate | any result |
| actor `c_i` | signed historical attribution | **LAYER 3** | attribution convention | foundation | accumulated EBU attribution | entropy capacity without the bridge |
| BU scaling | `V_phys = B0 V_norm` | **OPEN INTERPRETATION LAYER** | `B0` constant | baseline | consistent up to one scale | `1 BU = k_B T_ref` |
| exploratory dynamics | `D + Q_skew`, SDE, `Phi_qp`, Onsager | **NOT ADOPTED** | — | baseline | useful lessons only | EBU core status |
| Stage B | ungated signed account | **NOT RESUMED** | — | baseline | available as an idea | that the bridge is established |

---

## 21. DEPENDENCY GRAPH

```
FROZEN CORE
    physical state / transition
        -> V
        -> mu
        -> E , f

QUADRATIC GEOMETRY
    V quadratic
        -> H
        -> modes / sigma

INDEPENDENT PROBABILITY
    observations
        -> P
        -> J_prob
        -> K

GENERAL CANDIDATE BRIDGE
    entropy candidate + Einstein/Boltzmann
        -> J_prob = beta V
        -> K = beta H

E1a SPECIAL REALISATION
    mechanical U + calibrated T
        -> V = Delta U / (k_B T)
    canonical probability
        -> J_prob
    prediction: J_prob = V , beta = 1 , kappa = k_B

ACCOUNTING
    E -> attribution -> c_i

FORBIDDEN, NO ARROW EXISTS:
    c_i / economy  -X->  V / H / sigma
```

---

## 22. CORRECTED-RESULT LEDGER

Superseded history is preserved, not erased.

| # | original claim | corrected claim | correcting report |
|---|---|---|---|
| **A** | a complex spectrum means **no potential exists** | a complex spectrum rules out a **pure gradient flow only**; every asymptotically stable linear system admits a quadratic Lyapunov potential with `A = -(D + Q_skew) H` | P2.6 correction and generalisation gate |
| **B** | for a chemical system, ambient `K = diag(1/n_i)` under conservation | use the **tangent space**: `K_T = beta H_T` on the stoichiometric compatibility class; the ambient claim is wrong by the factor `(1-p)` | P2.6 correction, §11 |
| **C** | E1 with fixed `B0`: `beta = B0/(k_B T)`, so **temperature changes `beta`** | `V = Delta U/(k_B T)`, so **`beta = 1`, `kappa = k_B`**, and temperature becomes the **strongest commensurability test** | E1a narrow design correction |
| **D** | the time-shuffle negative control **destroys `K` geometry** | time shuffling destroys **only temporal correlation** and leaves `P`, the covariance and `K` unchanged; it is an autocorrelation control. Independent **coordinate** permutation is the genuine geometry control | E1a narrow design correction, §10 |
| **E** | `1 BU = k_B T_ref` as an operational Burden Unit | **retracted** — it creates an energy-valued unit and a temperature-dependent `kappa`; BU calibration stays an open interpretation-layer question | E1a narrow design correction, §8 |
| **F** | Claim A (action increment) is an **independent** test | given pointwise `J_prob = beta V` on the same domain, `Delta J = beta E` follows by **endpoint subtraction**; retained as **finite-domain validation** beyond the local Hessian test | E1a narrow design correction, §9 |

---

## 23. EVIDENCE SOURCES CONSOLIDATED

This baseline consolidates the corrected results of:

- P0 topology / Möbius / recursion / dynamics / entropy synthesis validation;
- the corrected P1 entropy / rate-function theorem packet, and the P1
  independent audit and its applied corrections;
- P2 identifiability, physical scale and natural-source analysis;
- P2.5 field-geometry, normal-mode, coarse-graining and Burden-Unit analysis;
- the original P2.6 natural-source anchoring report;
- the corrected and generalised P2.6 report (potential, Onsager limit,
  rotational dynamics, quasipotential boundary, conserved chemical systems);
- the changing-field freedom and calibration studies;
- the E1 Einstein–EBU bridge experimental design;
- the **E1a narrow design correction**, which supersedes the fixed-`B0`
  temperature-arm formulation of E1.

Historical provenance for the pre-freeze material is in
`docs/scientific_record/` on `publication/scientific-record` at
`481753895509524c9d2674d1880d87712bb0ec18`.

---

## 24. NEXT GATE

**E1a v4 bounded implementation**, against the adopted prospective design
`docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` and its contract
`docs/e1a/e1a_v4_design_contract.json`. The synthetic validation campaign of
design §15 follows implementation and is a **separate** authorization.

The superseded gate — "re-run the eight-case suite under thermal normalisation"
— is retained as history only: the v3 attempt failed and the decision rules
themselves were corrected afterwards.

Not started: E1a v4 implementation, E1a synthetic validation, E1a
preregistration, E1a execution, E1b design, P2.7, Stage B.
