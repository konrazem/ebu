# EBU — PATH, POTENTIAL, FIELD-CHANGE AND EQUILIBRIUM SEMANTICS

## A non-controlling theoretical reconstruction

```
STATUS:                        NON-CONTROLLING THEORETICAL RECONSTRUCTION
PHYSICAL FOUNDATION:           UNCHANGED
THEORY BASELINE:               UNCHANGED
CURRENT E1a-v4:                PRESERVED / PAUSED
MINIMAL DIRECT BRIDGE DESIGN:  NOT YET AUTHORITATIVE
OFFICIAL LONG-RUN CAMPAIGN:    NOT RUN
REAL OPTICAL-TRAP EXPERIMENT:  NOT RUN
EXECUTION SEAL:                NOT FROZEN
EXECUTION AUTHORISED:          FALSE
```

**Nothing proposed here is authority.** No wording below amends, supersedes or reinterprets
the physical foundation, the theory baseline, the E1a design, the contract or the plan. Where
this document and controlling authority differ, **authority controls**.

| | |
|---|---|
| analysed at HEAD | `6767b3eab4a156aaa557f8745b35e2b561464535` |
| tree | `df4d544d141652ba31f46c272e16434fc962e322` |
| branch | `gaussian/stage-a-environment` |
| worktree at start | clean |

### Note on location

The task specified `docs/scientific_record/`. That directory does **not** exist on this
branch; it exists on `publication/scientific-record` at commit `4817538955…`, where it holds
the **byte-manifested frozen evidence bundle** (`EVIDENCE_MANIFEST.json`, `stage_a/`,
`physical_foundation/`) whose fourteen entries the foundation records as re-hashed with zero
byte failures. Adding a new 2026 analytical report into a directory that elsewhere means
"the hash-manifested pre-freeze record" is a provenance hazard. `AGENTS.md` ranks authority
as *frozen foundation > working theory baseline > exploratory reports*, and `docs/theory/` is
the only theory-layer directory on this branch, so this exploratory report is placed beside
the baseline it analyses and below it in rank.

---

## 0. Findings, before the derivations

Six results. Four of them say the authority is **already correct and already complete** on
points this task suspected might be gaps; one identifies a genuine (small) derivational gap;
one identifies a documentary inconsistency that may need a human decision.

**F-1 — The path integral is not missing. It is already a foundation theorem.** Foundation
§3 states `E = −∫_γ ∇V·dx` explicitly, with a REGULARITY CORRECTION demanding a
single-valued `C¹` potential, and §25 lists it as a **derived theorem** verified by
"80 polynomial coefficient/integral cases; 600 curved-path cases". Layer 2 of §1 names "the
local directional quantity `f`; **the path integral**" among its contents. The headline
`E = V_pre − V_post` is a compressed quotation of a structure that is written out.

**F-2 — "Fixed `θ`" is already an explicit assumption on the definition itself.** The §25
canonical table gives `E = V_pre − V_post` the assumptions "state function, **fixed `θ`**",
and §17 states: "**Every fixed-field statement in this document is conditional on `θ` being
fixed**", adding that if the field changes during an action "its parameter-derivative
contribution likewise **cannot be silently omitted**". The boundary is declared. What is
*not* written out is the explicit term `−∫_Γ ∇_θV·dθ`. **That is the one real gap, and it is
derivational/pedagogical, not an authority gap.**

**F-3 — The canonical-equilibrium bridge is not in the physical foundation at all, and the
foundation explicitly forbids the circular proof.** The foundation contains no Boltzmann
distribution, no `p ∝ exp(−V)`, no detailed balance and no probability current. §21 states
**"CIRCULAR PROOF EXPLICITLY FORBIDDEN"** — choosing a distribution proportional to
`exp(−V)` "does **not** independently establish that `V` is a physical entropy or rate
function" — and §25 lists "`P ∝ exp(−V)` as proof" as a **forbidden overstatement**. The
equilibrium bridge lives one layer down, in theory baseline §14.1 and the E1a design.

**F-4 — The nonconservative boundary is already drawn, in the baseline's do-not-drift list.**
Corrected-result ledger item A: a complex spectrum "rules out a **pure gradient flow only**;
every asymptotically stable linear system admits a quadratic Lyapunov potential with
`A = −(D + Q_skew)H`, `D` positive — so existence is cheap and therefore weak". The baseline
forbids promoting `D + Q_skew` dynamics, SDEs, quasipotentials or Onsager transport into the
EBU core.

**F-5 — Conservation language is already correctly separated, and the separation must be
preserved.** §25 classifies `C + V = constant` as a **CONDITIONAL ACCOUNTING THEOREM** whose
forbidden overstatements are "**physical conservation**; thermodynamic law; any sign
constraint on `C`", and classifies carrier conservation at Layer 1 with the forbidden
overstatement "**calling `C+V` conservation**".

**F-6 — A documentary inconsistency, reported not resolved.** The foundation's own first line
reads **"STATUS: FREEZE CANDIDATE. NOT FROZEN. NOT COMMITTED. NO REPOSITORY AUTHORITY."**,
while `AGENTS.md` names it first in the required reading order and ranks "frozen foundation"
above everything else. Both cannot be literally true. This is the only item in this
reconstruction that plausibly requires a human decision.

---

## 1. What `E = V_pre − V_post` actually means

The task asks whether authority intends this as a state-function endpoint identity, a
path-integral shorthand, a physical work equation, an actor accounting definition, or a
combination. The foundation answers directly and the answer is **not** "a combination".

From foundation §0, the single controlling rule:

> **Nothing may replace `E = V_pre − V_post` as the general finite EBU definition.** Every
> edge polynomial is a corollary. Every Study-1 formula is a specialization. Every actor
> account is Layer 3. Every economic rule is Layer 4 or 5.

and from the §25 table:

| equation | layer | assumptions | kind | status |
|---|---|---|---|---|
| `E = V_pre − V_post` | 2 | state function, **fixed `θ`** | GENERAL — TOP OF HIERARCHY | **definition** of finite EBU |
| `E = −∫_γ ∇V·dx` | 2 | single-valued **`C¹`**, **fixed `θ`**, admissible piecewise-smooth `γ` in domain | general | **derived theorem** |

So, precisely:

```
IT IS         a DEFINITION, at Layer 2, of the finite EBU of a transition, scoped to
              fixed theta and to V being a state function.

IT IS ALSO    equivalent to a path integral -- but that equivalence is a DERIVED THEOREM
              with its own strictly stronger regularity assumptions, not part of the
              definition.

IT IS NOT     a physical work equation. Foundation section 3 attaches a CAUTION to f that
              it "does not by itself establish a mechanical law of motion, a measured
              mechanical force, or any dynamical response law".

IT IS NOT     an actor accounting definition. Attribution is Layer 3; section 1 states
              "Layers 4 and 5 appear nowhere in Layers 1-3".
```

**The four readings are layered, not merged.** The definition is the most general statement;
the path integral is a theorem *below* it needing more assumptions; work and accounting are
different layers entirely. Conflating them is what the foundation's forbidden-overstatement
column exists to prevent.

---

## 2. R1 — The fixed-field path form

### 2.1 Derivation

Let `θ` be fixed and `V_θ : Ω → ℝ` be `C¹` and single-valued on the relevant domain. Let
`Γ : q ∈ [q_0, q_1] ↦ x(q)` be admissible and piecewise-smooth with `x(q_0) = x_pre`,
`x(q_1) = x_post`, the image lying in `Ω`. The chain rule gives

```
d/dq  V_θ(x(q))  =  ∇_x V_θ(x(q))ᵀ (dx/dq)
```

Integrating over `[q_0, q_1]` by the fundamental theorem of calculus,

```
V_θ(x_post) − V_θ(x_pre)  =  ∫_{q_0}^{q_1} ∇_x V_θ(x(q))ᵀ (dx/dq) dq
```

and therefore

```
E_θ[Γ]  =  V_θ(x_pre) − V_θ(x_post)  =  − ∫_{q_0}^{q_1} ∇_x V_θ(x(q))ᵀ (dx/dq) dq
        =  − ∫_Γ ∇V_θ · dx
```

**This is the authoritative form, with the authoritative sign.** Foundation §3 writes it as
`E = − ∫_γ ∇V · dx`. No sign or notation difference arises.

### 2.2 The authority's own regularity correction

Foundation §3 carries, verbatim:

> **REGULARITY CORRECTION (required by the Independent Freeze Audit, §3).** "Differentiable"
> alone is **not** a sufficient general regularity statement for this identity. `C¹` is a
> simple sufficient condition, and the Gaussian satisfies it. Because a single-valued
> potential is already given, **no simply-connected-domain assumption is needed**; a topology
> objection that applies to an arbitrary curl-free vector field does not apply to an actual
> gradient.

That last clause is important and is addressed again in §4.2 below. The foundation has
already anticipated and correctly dismissed the usual topological objection — **for the case
where `V` is given**.

### 2.3 Worked Example A — 1D quadratic, exact rational arithmetic

`V(x) = ½ k x²` with `k = 3`, from `x_0 = 1/2` to `x_1 = 5/2`:

```
V(x_0) − V(x_1)              = −9      (exact)
− ∫_{x_0}^{x_1} (dV/dx) dx   = −9      (exact)
EQUAL (exact rationals)      : True
```

### 2.4 Worked Example B — three paths, one endpoint pair

`V(x,y) = ½(2x² + 3y²) + xy`, from `(0,0)` to `(1,2)`. `V_pre = 0`, `V_post = 9`, so
`E = −9`. Three different admissible paths:

| path | `E` |
|---|---|
| straight `(q, 2q)` | **−9** |
| L-shaped via `(1,0)` | **−9** |
| curved `(q, 2q²)` | **−9** |

All three equal the endpoint difference, exactly. The closed loop
`(0,0) → (1,0) → (1,1) → (0,1) → (0,0)` gives exactly `0`.

---

## 3. R1 — The local differential quantity `f`

### 3.1 Verified against authority

Foundation §3, verbatim:

```
f = −dV/dq = −∇Vᵀ (dx/dq)
```

> `f` may be called the **LOCAL DIFFERENTIAL DRIVING QUANTITY**, or the **EBU EDGE FORCE /
> DRIVING FORCE**, only with this caution attached:
>
> **CAUTION.** `f` is a mathematical directional derivative. It does **not** by itself
> establish a mechanical law of motion, a measured mechanical force, or any dynamical
> response law. Naming it a "force" is a convention of this programme, not a physical
> finding. **Both independent audits state this.**

And §25's row for `f`:

| equation | assumptions | kind | evidence | **forbidden overstatement** |
|---|---|---|---|---|
| `f = −∇Vᵀ dx/dq` | differentiable action path | **derived theorem** | 120 + 360 checks | **"`f` establishes a law of motion"; "`f` is a measured mechanical force"** |

```
NAME       LOCAL DIFFERENTIAL DRIVING QUANTITY / EBU EDGE FORCE (a naming convention)
UNITS      [f] = 1/[q]     (theory baseline, dimensional table)
IS IT a mechanical force?        EXPLICITLY NO
IS IT a law of motion?           EXPLICITLY NO
IS IT a dynamical response law?  EXPLICITLY NO
```

### 3.2 The integral relation

Immediately from the definition and §2.1,

```
E_θ[Γ] = ∫_{q_0}^{q_1} f(q) dq
```

**Scope, exactly:** fixed `θ`; `V_θ` single-valued and `C¹` on a domain containing the image
of `Γ`; `Γ` admissible and piecewise-smooth; `x(q)` differentiable where `f` is evaluated.
Under those conditions `f dq = −dV` is an exact differential and the integral is the endpoint
difference. **It does not follow, and must not be stated, that `∫ f dq` is physical work.**

---

## 4. R2 — Why the integral collapses, and the two different situations

### 4.1 Situation A — `V` is already given globally

If `V : Ω → ℝ` is single-valued and `C¹`, then `∇V · dx = dV` is an **exact** differential by
construction, and the fundamental theorem of calculus gives path-independence on `Ω`
immediately. The precise requirements are:

```
REQUIRED   V single-valued on Omega
           V of class C^1 on Omega  (continuity of the gradient; "differentiable" alone
                                     is insufficient -- foundation section 3's correction)
           the path admissible, piecewise-smooth, and its IMAGE CONTAINED IN Omega
           theta fixed throughout

NOT REQUIRED   Omega simply connected
               Omega convex, open, or connected beyond what joining the endpoints needs
               any curl condition  (it holds identically for a gradient)
```

The foundation states the "not required" list explicitly for simple-connectedness. Adding the
others would be an overstatement in the opposite direction, and this report does not add them.

### 4.2 Situation B — starting only from a vector field

The converse problem is different and strictly harder. Given `μ : Ω → ℝⁿ`, does there exist
`V` with `μ = ∇V`?

```
NECESSARY (C^1 mu)    the Jacobian of mu is symmetric:  d mu_i / d x_j = d mu_j / d x_i
                      (equivalently curl mu = 0 in 3D)
SUFFICIENT            the above PLUS Omega simply connected (Poincare lemma)
NOT SUFFICIENT        the symmetry condition alone on a general domain
```

The punctured-plane field `μ = (−y, x)/(x²+y²)` satisfies the symmetry condition everywhere
on `ℝ²∖{0}` yet admits no single-valued global potential there; its integral around the unit
circle is `2π`.

> **This does not weaken foundation §3.** The foundation's `V` is *given*, so the programme
> is always in Situation A. The foundation says exactly this. Situation B matters only if a
> future programme tries to *construct* `V` from a measured field `μ` — which is a different
> and currently unposed problem.

---

## 5. R5 — The nonconservative / path-dependent boundary

### 5.1 Worked Example D — a genuinely path-dependent field

`W(x,y) = (−y, x)`, which has `∂W_y/∂x − ∂W_x/∂y = 2 ≠ 0`. From `(0,0)` to `(1,1)`:

```
route via (1,0):  ∫ W·dl = +1
route via (0,1):  ∫ W·dl = −1
difference = 2 ≠ 0      ⟹  no state function W = ∇(·) exists on any domain containing both
closed loop (0,0)→(1,0)→(1,1)→(0,1)→(0,0) = 2 ≠ 0
```

For contrast, the same closed loop evaluated on Example B's gradient field gives exactly `0`.

### 5.2 What the EBU endpoint potential captures and what it does not

```
CAPTURED        every contribution expressible as the gradient of a single-valued
                state function V_theta on the relevant domain, at fixed theta.
                Its integral over any admissible path is V_pre - V_post, exactly.

NOT CAPTURED    any contribution with a nonzero circulation. If a physical process
                carries F_total = F_conservative + F_nonconservative, then
                -int F_total . dx  =  (V_pre - V_post)  -  int F_nonconservative . dx
                and the second term is PATH-DEPENDENT and is NOT a function of the
                endpoints.

CONSEQUENCE     TOTAL PHYSICAL WORK MUST NOT BE IDENTIFIED WITH V_pre - V_post unless
                the nonconservative part is independently shown to vanish or to be
                outside the declared state.
```

**No new EBU law is proposed here.** The boundary is stated, not crossed.

### 5.3 Authority already draws this boundary

Theory baseline, corrected-result ledger item **A**:

> original claim: a complex spectrum means **no potential exists**
> corrected claim: a complex spectrum rules out a **pure gradient flow only**; every
> asymptotically stable linear system admits a quadratic Lyapunov potential with
> `A = −(D + Q_skew) H`

with the baseline's own gloss that "existence is cheap and therefore weak" evidence, and
near-equilibrium "Onsager reciprocity forces `Q_skew = 0`". The baseline's do-not-drift list
states:

> **Do NOT promote into the EBU core:** `D + Q_skew` dynamics, stochastic differential
> equations, quasipotentials, or Onsager transport equations.

So the rotational/nonconservative extension is **a recognised, explored and deliberately
unadopted direction**, not an oversight.

---

## 6. R3 — The field-changing path

### 6.1 Derivation

Let `V = V(x, θ)` be `C¹` in both arguments and let the path be
`Γ : q ↦ (x(q), θ(q))`, with `θ` possibly **vector-valued**. Then

```
dV/dq = ∇_x V(x(q),θ(q))ᵀ (dx/dq)  +  ∇_θ V(x(q),θ(q))ᵀ (dθ/dq)
```

and integrating,

```
V_pre − V_post  =  − ∫_Γ ∇_x V · dx  −  ∫_Γ ∇_θ V · dθ
```

For **scalar** `θ` the second term may be written `− ∫_Γ (∂V/∂θ) dθ`. For vector-valued `θ`
it may not, and the inner-product form must be kept — the future environmental field is
expected to be vector-valued, so the scalar form is not adopted here.

### 6.2 Worked Example C — the state term alone is not enough

`V(x,θ) = ½ θ x²`, path `x(q) = 1+q`, `θ(q) = 1+3q`, `q ∈ [0,1]`, i.e. `(1,1) → (2,4)`.
Exact rational arithmetic:

```
V_pre  = V(1,1) = 1/2            V_post = V(2,4) = 8
E_total = V_pre − V_post                         = −15/2
E_state = − ∫ ∇_x V · dx                         = −4
E_field = − ∫ ∇_θ V · dθ                         = −7/2
E_state + E_field                                = −15/2    ✓ equals E_total
E_state ALONE equals E_total?                    : NO
fraction of the total carried by the field term  : 7/15 ≈ 46.7%
```

**Nearly half the endpoint difference is in the field term.** Omitting it is not a small
correction.

### 6.3 Authority already says the term cannot be omitted

Foundation §17, "External events and changing fields — the identity acquires explicit terms":

```
(C_{t+1} + V_{θ'_t}(x_{t+1})) − (C_t + V_{θ_t}(x_t))
      = V_{θ'_t}(y_t) − V_{θ_t}(x_t) + J_t
```

> **That right-hand side generally does not vanish and must be recorded.** If the field
> changes *during* an action, **its parameter-derivative contribution likewise cannot be
> silently omitted. Every fixed-field statement in this document is conditional on `θ` being
> fixed.**

So the foundation (i) scopes every fixed-field statement, (ii) names the parameter-derivative
contribution, and (iii) forbids omitting it. **What it does not do is write out
`−∫_Γ ∇_θV·dθ`.** That is the derivational gap of F-2, and §6.1 above fills it as a
*proposal*, not as authority.

Foundation §23 open question 5 is "How does `θ` evolve?" and question 11 is "Does `E = ΔF`
survive moving-field decomposition?"; roadmap gate **P4** asks whether `E = ΔF` defines a
permanent normalized actor contribution under **changing** fields. The topic is on the
declared open list.

---

## 7. R4 — The state/field attribution boundary

A **mathematical** decomposition is available immediately from §6.1:

```
E_state := − ∫_Γ ∇_x V · dx
E_field := − ∫_Γ ∇_θ V · dθ
E_total  = E_state + E_field
```

This decomposition is **exact and path-dependent in each term separately** — only the sum is
an endpoint function. Two separate cautions follow, and both matter.

**Caution 1 — the split is not unique as an attribution.** `E_state` and `E_field`
individually depend on the path taken through `(x, θ)` space, even though their sum does not.
Two processes with the same endpoints can have different `(E_state, E_field)` splits. So the
split is a property of the *path*, not of the *transition*.

**Caution 2 — none of the following follows from the mathematics, and none is asserted:**

```
E_state  =  actor EBU                         NOT ESTABLISHED
E_field  =  external / environmental EBU      NOT ESTABLISHED
field change  =  an actor earning or spending event   EXPLICITLY NOT ASSUMED
```

Foundation §1 places attribution at **Layer 3** and actor decision at **Layer 4**, and states
"no concept may move upward between layers without an independent physical derivation".
Assigning `E_state` to an actor would be exactly such an upward move. **Attribution under
changing fields is recorded here as a separate later theory problem**, consistent with
roadmap gate P4.

---

## 8. R6 — Equilibrium is not required for the potential identity

### 8.1 The mathematical answer

```
DOES  E_theta = V_theta(x_pre) - V_theta(x_post)  REQUIRE THERMODYNAMIC EQUILIBRIUM?

NO.
```

Nothing in §2.1's derivation mentions a distribution, a temperature, a reservoir, detailed
balance or a stationary state. It requires only that `V_θ` be a single-valued `C¹` function
of the state at fixed `θ`. A system arbitrarily far from equilibrium still has a well-defined
`V_θ(x_pre) − V_θ(x_post)` provided `V_θ` is declared and the states are declared.

### 8.2 Authority agrees, by omission and by construction

The foundation's assumption lists for `E = V_pre − V_post` and `E = −∫∇V·dx` are, verbatim,
"state function, fixed `θ`" and "single-valued `C¹`, fixed `θ`, admissible piecewise-smooth
`γ` in domain". **Neither mentions equilibrium.** Foundation §2 makes the separation
load-bearing:

> **Question A — the mathematics conditional on `V`.** Given a declared potential `V(x;θ)`
> with sufficient regularity, the entire structure in §3–§18 follows exactly. This is not
> weakened by anything unknown about `V`'s origin.
> **Question B — the physical origin of `V`.** Why should a given physical system have this
> `V`? **This is not derived.**

### 8.3 The statement that must never be merged

```
STATE-POTENTIAL / PATH-INTEGRAL IDENTITY            is NOT the same theorem as
THERMODYNAMIC EQUILIBRIUM BRIDGE

The first is Layer-2 mathematics, conditional on V's regularity, and holds arbitrarily
far from equilibrium.
The second is a physical claim about why a particular V governs a particular observed
distribution, and holds only under canonical-equilibrium assumptions.
```

---

## 9. R6 — Equilibrium *is* load-bearing for `β_bridge = 1`

### 9.1 Derivation

Under canonical equilibrium at temperature `T_θ` with mechanical potential energy `U_θ`,

```
p_θ(x) = Z_θ⁻¹ exp[ −U_θ(x) / (k_B T_θ) ] ,      Z_θ = ∫ exp[ −U_θ(x)/(k_B T_θ) ] dx
```

With the thermal normalisation of theory baseline §14.1 and E1a design §1,

```
V_θ(x) := [ U_θ(x) − U_θ(x*_θ) ] / (k_B T_θ)
```

so `U_θ(x)/(k_B T_θ) = V_θ(x) + U_θ(x*_θ)/(k_B T_θ)`, and

```
−ln p_θ(x) = V_θ(x) + ln Z_θ + U_θ(x*_θ)/(k_B T_θ)
           = V_θ(x) + C_θ
```

with `C_θ` independent of `x`. Comparing with the bridge form `J_θ = β_bridge V_θ + C_θ`:

```
β_bridge = 1
```

### 9.2 Every assumption required

```
E1  canonical (Gibbs) equilibrium ensemble at temperature T_theta
E2  a normalizable Boltzmann measure: Z_theta finite on the accessible domain
E3  U_theta is THE correct physical potential energy of the state coordinate x
E4  T_theta is the true thermodynamic temperature of the bath, independently measured
E5  x is the complete relevant state coordinate; no hidden coordinate is marginalised
    in a way that changes the effective potential
E6  no probability current; detailed balance holds
E7  the observation is of the stationary distribution (ergodic sampling, no transient)
E8  the normalisation reference x*_theta is declared and fixed
```

```
CLASSIFICATION:  EQUILIBRIUM THERMODYNAMIC RESULT.
It is NOT a universal nonequilibrium result, and it is NOT a new discovery -- it is
standard equilibrium statistical mechanics applied to a declared normalisation.
```

### 9.3 The foundation's forbidden circular proof — and why E1a is not it

Foundation §21:

> **CIRCULAR PROOF EXPLICITLY FORBIDDEN.** Choosing or defining a normalizable distribution
> proportional to `exp(−V)` does **not** independently establish that `V` is a physical
> entropy or rate function. That would define the ensemble from the potential and then
> present the potential as a consequence of the ensemble.

and §25 lists "`P ∝ exp(−V)` as proof" as a forbidden overstatement for the entropy row.

**E1a avoids the circularity by construction, and that is the whole point of its two-branch
design.** `V_θ` is built in Branch A from mechanical force–displacement data and independent
thermometry; `p_θ` is observed in Branch B from positions; Branch A never reads the histogram
and Branch B never reads `V` or `H`. The measured distribution is therefore not *defined* from
the potential. Design §2.1's forbidden routes (power spectrum, corner frequency, equipartition)
are precisely the ones that would close the loop.

> **What E1a therefore tests is the measurement architecture, not the Boltzmann law.** Under
> E1–E8 the result `β = 1` is a theorem. A successful experiment is "consistent with the known
> equilibrium bridge under independent physical and statistical measurement" — never
> "discovery of the Boltzmann distribution".

---

## 10. Thermodynamic `β` versus bridge `β` — disambiguation

These must never be confused, and they differ in dimension:

| symbol | definition | dimension | value here |
|---|---|---|---|
| `β_thermo` | `1/(k_B T)` | energy⁻¹ | `≈ 2.43×10²⁰ J⁻¹` at 298 K |
| `β_bridge` | the coefficient in `J_θ = β_bridge V_θ + C_θ` | **dimensionless** | predicted `1` |

The reason they are different objects: `β_thermo` converts energy to dimensionless units;
`V_θ` has **already been divided by `k_B T_θ`** and is therefore dimensionless, so
`β_bridge` multiplies an already-normalised quantity. Writing `β` without a subscript in a
context where both could be meant is an error this programme should avoid.

Theory baseline records the retraction that arose from exactly this confusion
(corrected-result ledger item **E**): `1 BU = k_B T_ref` was **retracted** because "it creates
an energy-valued unit and a temperature-dependent `kappa`, which destroys the very
commensurability the programme requires". Ledger item **C** records the related correction:
with `V = ΔU/(k_B T)`, `β = 1` and `κ = k_B`, and temperature becomes the **strongest
commensurability test** rather than a `β`-changing variable.

---

## 11. Gaussianity is not the equilibrium theorem

### 11.1 The general statement needs no Gaussian

The derivation of §9.1 used only E1–E8. **`U_θ` was never assumed quadratic.** For any
normalizable `V_θ`,

```
p_θ(x) ∝ exp[ −V_θ(x) ]        and        −ln p_θ(x) = V_θ(x) + C_θ
```

A quartic, a double-well or an arbitrary anharmonic `V_θ` gives a manifestly non-Gaussian
`p_θ` and `β_bridge = 1` all the same.

### 11.2 The harmonic case is a corollary

For `V_θ(x) = ½(x−x*)ᵀ H_θ (x−x*)` the Boltzmann measure is Gaussian with

```
Σ_θ = β_bridge⁻¹ H_θ⁻¹        hence at β_bridge = 1:    Σ_θ⁻¹ = H_θ
```

and since for a Gaussian `K_θ := ∇²(−ln p_θ) = Σ_θ⁻¹`,

```
K_θ = H_θ
```

```
CLASSIFICATION:  HARMONIC GAUSSIAN COROLLARY of the equilibrium theorem.
NOT the general equilibrium theorem, and NOT the definition of the bridge.
```

### 11.3 Why the direction matters

`K = βH` is a statement about **curvature at a point**; `−ln p = βV + C` is a statement about
the **whole landscape**. For a Gaussian they coincide, because a Gaussian is determined by its
curvature. For anything else they do not: two distributions can share a Hessian at `x*` and
differ everywhere else. Treating `K = βH` as the definition silently imports the harmonic
assumption into the statement of the hypothesis.

---

## 12. R4/R3 — Fixed-field and field-changing topology

### 12.1 Fixed-field sequential composition — already a foundation theorem

Foundation §12, verbatim:

> **General theorem, any state function `V`:**
> `E(x → x+Δ₁+Δ₂) = E(x → x+Δ₁) + E(x+Δ₁ → x+Δ₁+Δ₂)`
> This holds **solely** because `E` is a state-function difference. It requires no
> demand-legality, provenance, attribution or service assumption.

and §25 lists "sequential refinement / telescoping" with assumptions "`V` a state function",
kind "general", status **derived theorem**, evidence "all Study-1 groups; 720 cases", and the
forbidden overstatements "requiring legality/provenance; confusing with same-base summation".

**This report claims no discovery.** For `A → B → C`:

```
E_{A→B} + E_{B→C} = (V_A − V_B) + (V_B − V_C) = V_A − V_C = E_{A→C}
```

and in integral form, for any admissible concatenation `Γ = Γ₁ ∘ Γ₂`,

```
− ∫_{Γ₁} ∇V·dx − ∫_{Γ₂} ∇V·dx = − ∫_{Γ} ∇V·dx
```

For a closed cycle `A → B → C → A` the sum is `(V_A−V_B)+(V_B−V_C)+(V_C−V_A) = 0`, verified
numerically in Example B (closed loop `= 0` exactly, against `2` for the nonconservative field
of Example D).

**The foundation's companion warning must travel with this.** Same-base summation is a
*different* construction and generally fails: for quadratic `V`,

```
E(x,Δ₁+Δ₂) − E(x,Δ₁) − E(x,Δ₂) = − Δ₁ᵀ H Δ₂
```

Telescoping re-bases each fragment at the previous endpoint; same-base summation does not.
Confusing them is the forbidden overstatement the table names.

### 12.2 Field-changing topology on the extended state space

If a single-valued `V(x,θ)` exists on the extended space and nodes are taken to be pairs
`(x,θ)`, then telescoping holds **by exactly the same argument**, because `E` is still a
difference of one state function evaluated at two points:

```
E_{(x₁,θ₁)→(x₂,θ₂)} + E_{(x₂,θ₂)→(x₃,θ₃)} = V(x₁,θ₁) − V(x₃,θ₃) = E_{(x₁,θ₁)→(x₃,θ₃)}
```

**Two things must be kept apart here, and the separation is the point of this subsection:**

```
MATHEMATICAL telescoping in the extended state space
    HOLDS, for the same reason as the fixed-field case: it needs only that V(x,theta) be a
    single-valued state function on the extended space. It needs no equilibrium, no beta,
    no Gaussianity, and no commensurability evidence.

PHYSICAL / ECONOMIC interpretation of the field-change contribution
    DOES NOT FOLLOW. That E_field is well defined does not establish what it MEANS, who it
    is attributed to, or whether EBU earned under theta_1 is denominated in the same unit as
    EBU earned under theta_0.
```

> **Cross-field EBU denomination is NOT established by the extended-space telescoping
> identity.** It requires bridge evidence — specifically, evidence that `β_θ` is common
> across the fields in question. That is what the four-field E1a benchmark exists to test and
> it has not been run.

---

## 13. R6 — Nonequilibrium scope

### 13.1 What survives away from equilibrium

```
SURVIVES   V(x,theta) as a declared state function              (it is a declaration)
SURVIVES   endpoint potential differences V_pre - V_post        (arithmetic on a state function)
SURVIVES   the path-integral identity for the exact dV          (calculus, given C^1)
SURVIVES   topology / telescoping / cycle-zero                  (state-function difference)
SURVIVES   the state/field decomposition of section 6.1         (chain rule)
```

Every item survives because every item is a consequence of `V` being a single-valued
sufficiently-regular function of the declared state. None of them mentions a distribution.

### 13.2 What is not guaranteed away from equilibrium

```
NOT GUARANTEED   p_theta(x) proportional to exp(-V_theta(x))
NOT GUARANTEED   beta_bridge = 1
NOT GUARANTEED   zero probability current
NOT GUARANTEED   detailed balance
NOT GUARANTEED   the equilibrium entropy interpretation
NOT GUARANTEED   that a stationary distribution exists at all
NOT GUARANTEED   that the stationary distribution, if it exists, is a function of U alone
```

> **The survival of the state-potential mathematics does not carry the thermodynamic bridge
> with it.** This is the single most important statement in this section. The mathematics of
> §13.1 is cheap — it follows from a declaration. The physics of §13.2 is the expensive part
> and is exactly what assumptions E1–E8 buy.

### 13.3 R5 — Why the bridge can fail in driven systems

Without proposing any nonequilibrium EBU formula, the recognised mechanisms are:

| mechanism | effect on the bridge |
|---|---|
| nonzero probability currents | the stationary density is no longer `∝ exp(−U/k_BT)`; a current-carrying steady state generally has a different "effective potential" |
| detailed-balance violation | `E6` fails directly; the Boltzmann form has no derivation |
| time-dependent fields `θ(t)` | `p(x,t)` lags the instantaneous Boltzmann measure; `E5`/`E7` fail |
| lag behind the instantaneous field | even a slowly driven system has `O(dθ/dt)` corrections to the quasi-static density |
| dissipation | work and free-energy change separate; `V_pre − V_post` no longer equals either |
| entropy production | the equilibrium entropy relation of foundation §21 has additional terms |
| nonconservative forcing | §5 — the contribution is not a gradient at all |

```
Each of these requires a LATER THEOREM. None is derived here, and no final nonequilibrium
EBU formula is proposed.
```

---

## 14. Relation to entropy

Reconstructed from foundation §21 and E1a design §9, without redoing the P4 analysis.

**Foundation §21 — the compatibility statement, not a physical claim.** At fixed `θ`, with
`S_eq(θ)` spatially constant and `κ` constant and nonzero:

```
S_θ(x) = S_eq(θ) − κ V_θ(x)      ⟹      ∇S = −κ μ ,    ΔS/κ = V_pre − V_post = E
```

> **CLASSIFICATION: MATHEMATICALLY COMPATIBLE. PHYSICALLY UNPROVED.** "It is an affine change
> of variable and adds no physical content." Variable `κ` or spatially varying `S_eq`
> introduces extra derivative terms and the relation no longer holds as written.

Foundation §22 records that `κ` is **not** assumed equal to `k_B`, **not** assumed equal to 1,
and **not** assumed universal; four possibilities remain open.

**E1a design §9 — four distinct objects, never equated:**

| object | value under the declared conditions | nature | equilibrium-dependent? |
|---|---|---|---|
| medium entropy change `Δs_med` | `+k_B E_θ` | process quantity, no-work transitions only | **YES** |
| stochastic system entropy `Δs_sys` | `−k_B E_θ` | trajectory quantity | **YES** |
| total stochastic entropy production `Δs_tot` | **`0`** — not `k_B E` | — | **YES** |
| constrained-macrostate entropy deficit `ΔS_constr` | `k_B E_θ` + remainder | state function, separate derivation | partly |

**Which statements connect to `E`, and under what scope:**

```
PURELY MATHEMATICAL, no equilibrium   Delta S / kappa = E   (foundation section 21, GIVEN the
                                      affine ansatz with constant kappa and constant S_eq --
                                      it is a change of variable, not a physical result)

EQUILIBRIUM-DEPENDENT                 Delta s_med = +k_B E_theta, Delta s_tot = 0, and every
                                      identification of kappa with k_B. These rest on the
                                      canonical ensemble and on the declared static-equilibrium,
                                      no-work conditions of E1a design section 9.
```

The foundation's standing requirement is unmet and must be repeated: before any entropy
interpretation may be claimed, there must be "an independent measurement or derivation of `S`
not defined through `V`; physical identification of `κ` with units; evidence that `S_eq(θ)`
is a genuine equilibrium entropy; and a statistical ensemble in which `V` is independently the
large-deviation rate function."

---

## 15. Relation to mechanical work — verified

```
IS  -grad V  CURRENTLY DEFINED AS A MECHANICAL FORCE?    NO.
```

Verified in §3.1: foundation §3 names `f` a "LOCAL DIFFERENTIAL DRIVING QUANTITY" with an
explicit CAUTION, and §25's forbidden-overstatement column reads "**`f` establishes a law of
motion**; **`f` is a measured mechanical force**".

```
THEREFORE  -int grad V . dx  MUST NOT be rewritten as "physical mechanical work"
           unless BOTH (a) authority and (b) the physical model of the specific system
           justify the identification.
```

**Where the identification *is* justified, and why that is a special case.** In the E1a
optical-trap benchmark `U_θ` is the *mechanical potential energy* of the trap, so
`−∫∇U_θ·dx` genuinely is mechanical work against the trap. But note what that requires: a
declared mechanical `U`, a conservative trap, and `V_θ = (U_θ − U_θ*)/(k_B T_θ)`, i.e. `V_θ`
is `U_θ` *in thermal units*. So `E_θ` is mechanical work divided by `k_B T_θ` — dimensionless
— **in that benchmark only**. The general foundation `V` carries no such guarantee, because
foundation §2 Question B says its physical origin "is not derived".

---

## 16. Measurement error and approximation — bounded, not universalised

### 16.1 A measurement-error identity, labelled as such

If the estimated potential is `V̂(x) = V(x) + δ(x)`, then for any pair of states,

```
Ê_ab − E_ab = [V̂(a) − V̂(b)] − [V(a) − V(b)] = δ(a) − δ(b)
```

and if `|δ(x)| ≤ ε` uniformly on the states used,

```
| Ê_ab − E_ab | ≤ 2ε
```

If instead the errors are modelled as random with covariance `C_V`, then for edge values
`e = Dv` with `D` the oriented incidence matrix, `C_E = D C_V Dᵀ`, and for a single edge

```
Var(E_ab) = Var(V_a) + Var(V_b) − 2 Cov(V_a, V_b)
```

```
CLASSIFICATION:  MEASUREMENT-ERROR BOUND.
It is NOT a universal theorem about model misspecification, and NOT a statement about
nonequilibrium physics. It assumes the functional form of V is correct and only its
VALUES are mis-measured.
```

### 16.2 The six error kinds, which must not be merged

| kind | what it is | does the bound of §16.1 apply? |
|---|---|---|
| measurement error in `V` | `V̂ = V + δ`, correct functional form | **yes** |
| parameter-estimation error | `V̂ = V(·; θ̂)`, `θ̂ ≠ θ` | only after propagating `θ̂`'s error into `δ` |
| model approximation error | the declared `V` family does not contain the true one | **no** |
| failure of potential representation | no single-valued `V` exists (§5) | **no** — the object being estimated does not exist |
| field-calibration error | `θ` itself mis-specified | **no** — this is a different `V`, not a perturbed one |
| departure from equilibrium | E1–E8 fail | **no** — this breaks the bridge, not the arithmetic |

**Nothing is filled in for the last two rows.** No approximate nonequilibrium correction is
guessed.

### 16.3 Worked Example E — internal consistency versus accuracy

An estimated potential `V̂` with `V̂_A = 10`, `V̂_B = 27/4`, `V̂_C = 3/2`:

```
(V̂_A − V̂_B) + (V̂_B − V̂_C) = 13/4 + 21/4 = 17/2
 V̂_A − V̂_C                                = 17/2
INTERNAL TELESCOPING EXACT                 : True
```

```
CRUCIAL DISTINCTION

INTERNAL ALGEBRAIC CONSISTENCY   Telescoping of V_hat is EXACT for ANY numbers whatsoever.
                                 It is a property of subtraction, not of accuracy. An
                                 entirely wrong estimated potential telescopes perfectly.

ACCURACY RELATIVE TO REALITY     An entirely separate question, governed by delta and by
                                 the five non-measurement error kinds above.
```

A further point that matters for later topological and economic use: with `δ_A = 1/5`,
`δ_C = 1/8`, the true error on `E_AC` is `δ_A − δ_C = 3/40`, and **`δ_B` does not appear at
all**. The intermediate node's error cancels *deterministically*, before any variance is
taken. Treating `E_AB` and `E_BC` as independent and adding their variances double-counts
`Var(V_B)` and **overstates** the uncertainty on `E_AC`.

---

## 17. Conservation language — audit

The task asks what may legitimately be called conservation. The foundation **already makes
the distinction**, and it should be preserved rather than restated differently.

| term | what it legitimately denotes | authority |
|---|---|---|
| **telescoping** | `E(x→x+Δ₁+Δ₂) = E(x→x+Δ₁) + E(x+Δ₁→x+Δ₁+Δ₂)`; a consequence of `E` being a state-function difference | §12, **derived theorem** |
| **cycle-zero identity** | `Σ E = 0` around a closed path of one single-valued potential at fixed `θ` | §12 corollary |
| **potential accounting** | `C + V = constant` under the §17 list at fixed `θ` | §25: **CONDITIONAL ACCOUNTING THEOREM** |
| **carrier conservation** | per-resource increment sums `= 0` in the declared state | §25: Layer 1, "physical law of the declared state" |
| **energy conservation / first law** | **not claimed anywhere** | — |

The forbidden overstatements the foundation itself records:

```
for  C + V = constant   :  "physical conservation"; "thermodynamic law"; any sign
                           constraint on C
for  carrier conservation: "calling C + V conservation"; "summing unlike carriers"
```

> **`Σ E = 0` around an exact-potential cycle is NOT the first law of thermodynamics.** It is
> the statement that a state function returns to its value when the state returns to itself.
> It involves no heat, no work, no internal energy and no energy balance. Conflating them
> would be exactly the overstatement §25 forbids.

**Book language — NOT AUDITED.** The topology and conservation material in the book series
was not read in this task. Whether any book wording risks the conflation above is recorded as
**NOT VERIFIED**. No book file was opened or edited.

---

## 18. Proposed theorem hierarchy — NON-AUTHORITATIVE

```
LAYER P -- STATE POTENTIAL / PATH IDENTITY
  ASSUMPTIONS      theta fixed; V_theta single-valued and C^1 on Omega; path admissible,
                   piecewise-smooth, image in Omega
  DOMAIN           any declared state space with such a V. No equilibrium required.
  CONCLUSION       E = V_pre - V_post = -int_Gamma grad_x V . dx = int f dq
  ERROR TYPE       measurement error in V (section 16.1); representation failure is
                   OUT OF DOMAIN, not an error
  OUT OF DOMAIN    V multivalued; V not C^1; path leaving Omega; theta varying;
                   a nonconservative contribution present
  SPECIAL CARE     f is NOT a mechanical force; same-base summation is not telescoping
  STATUS           ALREADY A FOUNDATION THEOREM (section 3 + section 25)

LAYER F -- EXTENDED STATE, FIELD-CHANGING PATH
  ASSUMPTIONS      V(x,theta) single-valued and C^1 in BOTH arguments on the extended domain
  DOMAIN           paths q -> (x(q), theta(q)); theta scalar OR vector
  CONCLUSION       V_pre - V_post = -int grad_x V . dx - int grad_theta V . dtheta
                   and telescoping holds on the extended space
  ERROR TYPE       as Layer P, plus field-calibration error
  OUT OF DOMAIN    V not jointly C^1; theta discontinuous without a declared jump convention
  SPECIAL CARE     E_state and E_field are individually PATH-DEPENDENT; only the sum is an
                   endpoint function. NO attribution follows.
  STATUS           PROPOSED. The foundation declares the scoping and forbids omitting the
                   term (section 17) but does not write the integral. Open questions 5 and 11;
                   roadmap gate P4.

LAYER E -- CANONICAL EQUILIBRIUM BRIDGE
  ASSUMPTIONS      E1-E8 of section 9.2
  DOMAIN           systems in canonical equilibrium with a declared mechanical U and an
                   independently measured T
  CONCLUSION       p_theta(x) proportional to exp(-V_theta(x)); -ln p = V + C;
                   beta_bridge = 1
  ERROR TYPE       thermometry error; U-calibration error; finite-sample statistical error;
                   departure from equilibrium is OUT OF DOMAIN
  OUT OF DOMAIN    driven systems; nonzero current; time-dependent theta; hidden coordinates
  SPECIAL CARE     must NOT be proved by assuming p proportional to exp(-V) -- foundation
                   section 21 forbids exactly that. Independent branches are what make the
                   test non-circular.
  STATUS           STANDARD EQUILIBRIUM STATISTICAL MECHANICS. Not in the foundation; in the
                   theory baseline section 14.1 and the E1a design. NOT a new result.

LAYER G -- HARMONIC GAUSSIAN COROLLARY
  ASSUMPTIONS      Layer E, plus V_theta = (1/2)(x-x*)^T H_theta (x-x*)
  DOMAIN           harmonic traps; near-minimum expansions where the quartic term is
                   demonstrably negligible
  CONCLUSION       Sigma_theta = H_theta^{-1} and K_theta = H_theta at beta_bridge = 1
  ERROR TYPE       all of Layer E, plus anharmonicity bias
  OUT OF DOMAIN    anharmonic V; large excursions; multi-well landscapes
  SPECIAL CARE     K = beta H is a CURVATURE statement; -ln p = beta V + C is a LANDSCAPE
                   statement. They coincide only here.
  STATUS           COROLLARY, not the general theorem.

LAYER N -- NONEQUILIBRIUM
  STATUS           NOT ESTABLISHED. No formula proposed. Section 13.3 lists the mechanisms
                   by which Layer E fails; each needs its own theorem.
```

---

## 19. Conceptual diagram

```
                         state potential  V
                                 |
        +------------------------+------------------------+
        |                        |                        |
  fixed-field path          field-dependent          canonical equilibrium
  theorem  (Layer P)        V(x,theta) (Layer F)     assumptions E1-E8 (Layer E)
        |                        |                        |
  E = -int grad_x V . dx    dV = grad_x V . dx        p  proportional to  exp(-V)
        |                        + grad_theta V . dtheta          |
  topology / telescoping         |                        beta_bridge = 1
  cycle-zero identity       E_state + E_field                     |
        |                        |                        harmonic Gaussian
  NEEDS NO equilibrium      NEEDS NO equilibrium                  |
  NEEDS NO beta             attribution NOT implied       Sigma^-1 = H ;  K = H


   nonequilibrium / nonconservative physics
                 |
                 v
   probability currents, detailed-balance violation, theta(t), lag,
   dissipation, entropy production, nonconservative forcing
                 |
                 v
   requires an ADDITIONAL theorem or model
                 |
                 v
   NOT automatically covered by beta = 1
```

Two directions of implication that are **not** symmetric, and that this diagram exists to
make visible:

```
Layer P and Layer F survive into the nonequilibrium region.
Layer E and Layer G DO NOT.
Therefore "the EBU mathematics still works out of equilibrium" is TRUE and
          "therefore the bridge still holds" is a NON SEQUITUR.
```

---

## 20. Is the current foundation wording too easy to misread?

| question | finding |
|---|---|
| Does the foundation already contain enough path-integral semantics? | **YES.** §3 gives the integral, the `C¹` regularity correction and the dismissal of the simple-connectedness objection; §25 classifies it as a derived theorem with 680 verification cases; §1 lists the path integral in Layer 2. |
| Is the relation mathematically correct but pedagogically compressed? | **The relation is correct.** The compression is in *quotation*: the headline `E = V_pre − V_post` travels on its own into summaries, and its two assumptions — "state function" and "**fixed `θ`**" — live in a table on line 938 of a 1,020-line document. |
| Is any actual scientific statement missing? | **One, and it is small.** §17 says the parameter-derivative contribution "cannot be silently omitted" but never writes `−∫_Γ ∇_θV·dθ`. §6.1 of this report supplies it as a proposal. Nothing else was found missing. |
| Would a future clarification/addendum be useful? | **YES** — a non-controlling theorem-hierarchy document, of which §18 above is a candidate. |
| Would modifying the frozen foundation be necessary? | **NO, not on the evidence of this reconstruction.** Every needed statement is either present or derivable from present statements. A clarification *below* the foundation suffices. |

> **The foundation is scientifically complete on R1, R2, R5 and R6 and scoped-but-underived
> on R3/R4.** The risk is reader misreading of a compressed headline, not an error of content.

---

## 21. Effect on the topology programme

Answered only to the depth the question requires; the book series was **not** audited.

| question | answer |
|---|---|
| Does fixed-field topology follow from the state-potential theorem? | **YES.** Foundation §12, "solely because `E` is a state-function difference". |
| Does it depend on equilibrium? | **NO.** §8, §13.1. |
| Does it depend on `β = 1`? | **NO.** `β` does not appear in §12 and the foundation contains no `β`. |
| Does it depend on Gaussianity? | **NO.** §12 says "any state function `V`". |
| Does cross-field physical interpretation need extra evidence? | **YES.** §12.2 — extended-space telescoping is mathematics; commensurability of the *unit* is physics and needs the bridge. |

**Scale versus offset — the distinction that governs cross-field use:**

```
common ADDITIVE offset     V^meas = V + k   =>  E^meas = E            CANCELS in every edge
common MULTIPLICATIVE scale V^meas = c V    =>  E^meas = c E          DOES NOT CANCEL;
                                                                      every EBU value rescales
```

A common `c` across all fields preserves every path identity, every ratio and all of topology,
and changes only the denomination — the "M1" outcome. Field-dependent `c_θ` (equivalently
`β_θ`) makes `E_θ0 + E_θ1` a sum in two different units; fixed-field topology stays valid and
cross-field accumulation does not. **This is precisely what the four-field benchmark tests,
and it has not been run.**

**NOT VERIFIED:** the book-series topology and motif material, and whether any of it uses
notation or claims inconsistent with the above.

---

## 22. Relation to the paused minimal direct bridge redesign

The proposed ordering is:

```
general path / potential mathematics      (Layer P, F)
        -> canonical equilibrium theorem  (Layer E)
        -> direct Boltzmann bridge beta=1 (Layer E conclusion)
        -> harmonic Gaussian corollary    (Layer G)
        -> statistical implementation
```

```
IS THIS ORDERING SCIENTIFICALLY COHERENT?   YES.
```

Each arrow adds assumptions and narrows the domain, and no arrow is reversible. It matches the
foundation's own layering (§1) and its Question A / Question B split (§2). It also makes
visible something the Hessian-first presentation obscures: `K = βH` sits **two** levels below
the general statement, not at the top.

One refinement this reconstruction suggests, as a proposal: the redesign document treats
`p ∝ exp(−βV)` as "the deepest EBU question". On the layering above it is a **Layer E**
statement — standard equilibrium statistical mechanics — while the EBU-specific content is at
Layers P and F, which need no equilibrium at all. The deepest *EBU* question is whether a
single `V(x,θ)` with a stable denomination exists across fields; the Boltzmann bridge is the
instrument for measuring that, not the question itself.

**Deliberately not addressed here**, as instructed: free `F` / reversibility, likelihood versus
moment estimation, finite-`N` size, the Route-A covariance, and observation noise. Those remain
later-stage tasks.

---

## 23. Required questions

```
Q1   IS E = Vpre - Vpost MATHEMATICALLY MISSING A PATH INTEGRAL?
     NO -- PEDAGOGICALLY COMPRESSED. Foundation section 3 states the path integral
     explicitly, with its C^1 regularity correction; section 25 classifies it a derived
     theorem with 80 + 600 verification cases; section 1 lists it in Layer 2.

Q2   AT FIXED FIELD, IS IT EQUIVALENT TO A LINE INTEGRAL OF -grad V?
     CONDITIONAL -- yes, given single-valued C^1 V on a domain containing an admissible
     piecewise-smooth path. The conditions are strictly stronger than those on the
     definition itself, which is why authority separates them.

Q3   DOES THE FIXED-FIELD ENDPOINT IDENTITY REQUIRE THERMODYNAMIC EQUILIBRIUM?
     NO.

Q4   DOES beta_bridge = 1 REQUIRE THE CURRENT CANONICAL-EQUILIBRIUM ASSUMPTIONS?
     YES -- all of E1-E8 in section 9.2.

Q5   DOES beta_bridge = 1 REQUIRE GAUSSIANITY?
     NO. The derivation never assumes U quadratic.

Q6   DOES THE HARMONIC K=H COROLLARY REQUIRE THE GAUSSIAN/HARMONIC SPECIAL CASE?
     YES -- K = Sigma^-1 holds for a Gaussian; for a general distribution the curvature
     at a point does not determine the landscape.

Q7   WHEN theta CHANGES, IS -int grad_x V . dx ALONE GENERALLY ENOUGH?
     NO. Example C: the state term gives -4 against a total of -15/2; the field term
     carries 7/15, about 46.7%, of the endpoint difference.

Q8   DOES THE FULL EXTENDED-STATE DIFFERENTIAL ADD A FIELD TERM?
     YES -- minus the integral of grad_theta V against d theta, kept in inner-product
     form because theta may be vector-valued.

Q9   DOES A NONCONSERVATIVE PATH-DEPENDENT CONTRIBUTION REQUIRE SPECIAL TREATMENT?
     YES. Example D: same endpoints, values +1 and -1, closed loop 2 != 0. No state
     function represents it and the endpoint account cannot capture it.

Q10  DO PURE FIXED-FIELD TOPOLOGY IDENTITIES REQUIRE beta=1?
     NO. Foundation section 12 needs only that V be a state function.

Q11  DO CROSS-FIELD PHYSICAL EBU ADDITIONS REQUIRE ADDITIONAL COMMENSURABILITY EVIDENCE?
     YES. Extended-space telescoping is mathematics; a common denomination is physics.

Q12  SHOULD THE CURRENT FROZEN FOUNDATION BE AMENDED NOW?
     NO -- with one caveat. On the scientific content of R1-R6 no amendment is indicated.
     The caveat is the STATUS inconsistency of F-6, which is documentary and is a human
     decision, not a scientific one.

Q13  IS A NON-CONTROLLING CLARIFICATION / THEOREM-HIERARCHY DOCUMENT WARRANTED?
     YES. Section 18 is a candidate.
```

---

## 24. Classification of every issue raised

| issue | classification |
|---|---|
| fixed-field path integral `E = −∫∇V·dx` | **ALREADY AUTHORISED** — foundation §3, §25 |
| `C¹` regularity, no simple-connectedness needed | **ALREADY AUTHORISED** — §3 regularity correction |
| `f` is not a mechanical force or law of motion | **ALREADY AUTHORISED** — §3 CAUTION, §25 forbidden column |
| fixed-field telescoping and cycle-zero | **ALREADY AUTHORISED** — §12, §25 |
| same-base summation ≠ telescoping | **ALREADY AUTHORISED** — §12 |
| endpoint identity needs no equilibrium | **MATHEMATICALLY SETTLED** — §2 Question A; assumption lists omit equilibrium |
| `β_bridge = 1` requires E1–E8 | **MATHEMATICALLY SETTLED** — standard statistical mechanics |
| `β_bridge = 1` needs no Gaussianity | **MATHEMATICALLY SETTLED** — §11.1 |
| `K = H` is a harmonic corollary | **MATHEMATICALLY SETTLED** — §11.2 |
| circular `p ∝ exp(−V)` proof forbidden | **ALREADY AUTHORISED** — §21, §25 |
| nonconservative contributions need separate treatment | **MATHEMATICALLY SETTLED**, and **ALREADY AUTHORISED** as a do-not-promote item in the baseline |
| `Σ E = 0` is not the first law | **ALREADY AUTHORISED** — §25 forbidden column |
| the explicit `−∫∇_θV·dθ` term | **PEDAGOGICAL CLARIFICATION** — scoped and named by §17, not written out |
| state/field attribution to actors | **FUTURE NONEQUILIBRIUM / ATTRIBUTION THEORY** — §23 Q11, roadmap P4 |
| nonequilibrium bridge | **FUTURE NONEQUILIBRIUM THEORY** — no formula proposed |
| book-series topology wording | **NOT VERIFIED** — not audited in this task |
| foundation header says NOT FROZEN / NO REPOSITORY AUTHORITY while `AGENTS.md` ranks it first | **SCIENTIFIC AUTHORITY GAP → HUMAN DECISION REQUIRED** |

### Human decisions

```
D1  FOUNDATION STATUS. docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md
    opens with "STATUS: FREEZE CANDIDATE. NOT FROZEN. NOT COMMITTED. NO REPOSITORY
    AUTHORITY." while AGENTS.md requires it be read first and ranks "frozen foundation"
    above the theory baseline and all reports. Both cannot be literally true. Someone must
    decide whether the document is frozen authority, a freeze candidate, or authority-
    by-convention-with-a-stale-header. This reconstruction treated it as controlling,
    which is what AGENTS.md directs, and flags the discrepancy rather than resolving it.
    CLASSIFICATION: documentary, not scientific. Nothing in R1-R6 turns on it.

D2  WHETHER TO ADOPT A CLARIFICATION DOCUMENT, and at what rank. Section 18's hierarchy
    is a candidate; adopting it would be a prospective, non-controlling addition BELOW the
    foundation. Not required for correctness. (Q13 says it is warranted; whether to do it
    is the decision.)

NO OTHER HUMAN DECISION IS EXPOSED. Every other item in the table above is either settled
by mathematics, already authorised, a pedagogical matter, or explicitly future work.
```

---

## 25. Identities and state

Report-only. Recomputed independently; reports are outside every identity preimage, and none
was artificially adjusted.

```
foundation  6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507   UNCHANGED
baseline    0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa   UNCHANGED
design      25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6   UNCHANGED
contract    d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4   UNCHANGED
plan        fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4   UNCHANGED
seed map    c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af   UNCHANGED
analysis    60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527   UNCHANGED
execution   442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b   UNCHANGED
```

```
4,002 checks, 0 failures, 17 suites, 0 not clean ; static preflight PASSED
execution_authorised = false ; execution seal state PRE_DRIVER, NOT FROZEN
OFFICIAL CAMPAIGN NOT RUN       SCIENTIFIC RNG DRAWS   0
OFFICIAL RESULTS  NONE          OFFICIAL TRAJECTORIES  0
REAL OPTICAL-TRAP EXPERIMENT NOT RUN             CALIBRATION EXECUTIONS 0
```

`results/e1a_v4_validation` does not exist. Every calculation in this report is exact
rational arithmetic or closed-form algebra; **no RNG, no trajectory, no Monte Carlo, no
calibration, no campaign job**.

**This report authorises nothing and amends nothing.**
