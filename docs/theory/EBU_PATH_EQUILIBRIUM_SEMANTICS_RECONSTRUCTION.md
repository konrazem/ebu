# EBU — PATH, POTENTIAL, FIELD-CHANGE AND EQUILIBRIUM SEMANTICS

## A non-controlling theoretical reconstruction

```
STATUS:                        NON-CONTROLLING THEORETICAL RECONSTRUCTION
R-STAGE REPAIR:                COMPLETE — INDEPENDENT RE-AUDIT REQUIRED
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
| original reconstruction analysed at HEAD | `6767b3eab4a156aaa557f8745b35e2b561464535` |
| tree | `df4d544d141652ba31f46c272e16434fc962e322` |
| branch | `gaussian/stage-a-environment` |
| worktree at start | clean |

### Prospective bounded repair — 2026-10-05

This revision repairs only the six independent R7 audit findings against report commit
`0a4c229a3299ee1e6ed4a2e5efb964b7334ed0e4`. That audit returned **NOT CLEARED**.
The repair does not grant clearance; its status is **READY FOR RE-AUDIT**.

| repair starting coordinate | value |
|---|---|
| HEAD | `0a4c229a3299ee1e6ed4a2e5efb964b7334ed0e4` |
| tree | `082a38810c3bd964a9e8f0adc8071d335891300a` |
| branch | `gaussian/stage-a-environment` |
| `git status --porcelain` | empty; clean |
| verified remote branch HEAD | `dd0d6b0e5d370de1bda805e07215ea0be4d6d083` |
| original report SHA-256 | `64005a290b69ea71958d1aeb8ed1de9847a8dd9d9fa7aafd03a8a6f11801a561` |

Only this non-controlling report is corrected, prospectively in a new commit; the original
commit remains intact. The explicit repair authorization permits editing this report in
place. The frozen scientific-record artifacts discussed below are unaffected. No S-MG
theorem or prior-art programme, Book 1 work, code change or scientific execution is included.
The enclosing repair commit identifies the final revision without a self-referential hash.

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
one identifies a documentary inconsistency whose authority question is resolved by freeze
provenance.

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

**F-6 — A documentary / metadata inconsistency, with authority resolved by provenance.**
The foundation's opening status still says "FREEZE CANDIDATE. NOT FROZEN. NOT COMMITTED.
NO REPOSITORY AUTHORITY." The sidecar instead records `status: frozen`, `frozen: true` and
the FINAL NARROW AUDIT PASS. Freeze commit `c63d6833da10a75ef66db11f99fb5b5c68d94c5e`,
baseline §0 and `AGENTS.md` establish the controlling frozen authority. The current canonical
file was compared byte-for-byte with that commit: **identical, 49,098 bytes**, SHA-256
`6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507`, matching both
sidecar digest entries. The stale header and sidecar `committed: false` flag do not override
the actual commit and freeze record. **No human scientific decision about foundation status
is outstanding.** Documentary cleanup is outside this repair; the foundation and metadata
remain unchanged.

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

For any supplied single-valued `C¹` potential at fixed `θ`,

```
E_theta = V_pre - V_post = -int_Gamma grad V_theta . dx
```

remains exact along every admissible path. Adding a nonconservative force does **not**
invalidate this identity for the potential contribution.

If the physical model independently supplies an energy potential `U` and force
`F_total = -grad U + F_nonconservative`, the standard mechanical sign convention gives

```
W_total = int_Gamma F_total . dx
        = U_pre - U_post + int_Gamma F_nonconservative . dx
```

The additional work need not be an endpoint function: Example D proves this for its chosen
field and paths. The dimensionless `E_theta` represents the first term divided by `k_B T`
only when the benchmark normalization of §15 applies. It does not automatically represent
total work. Even an unrepresented external force must be accounted for before a total-work
claim is justified; being outside the declared state is not a reason to discard its work.

**No new EBU law is proposed here.** Example D shows that an arbitrary force field's work
need not admit a scalar-potential representation. It does not question the existence or
exactness of an independently supplied gradient contribution.

---

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

This decomposition is **exact**. Its total is necessarily an endpoint difference; the
separate state and field integrals **may depend on the joint path** and are not generally
guaranteed to be endpoint functions.

**Caution 1 — special structure can make the separate terms exact.** For
`V(x,θ) = a(x) + b(θ)` with sufficiently regular `a` and `b`,

```
E_state = a(x_pre) - a(x_post)
E_field = b(theta_pre) - b(theta_post)
```

For `V = x²/2 + θ²/2` between `(1,1)` and `(2,4)`, these are `−3/2` and `−15/2`,
with total `−9`, for every admissible joint path. Separability is a special case, not a
general assumption. For a coupled potential such as Example C, processes with the same
endpoints can instead have different splits. Neither case supplies a unique actor
attribution.

**Caution 2 — none of the following follows from the mathematics, and none is asserted:**

```
E_state  =  actor EBU                         NOT ESTABLISHED
E_field  =  external / environmental EBU      NOT ESTABLISHED
field change  =  an actor earning or spending event   EXPLICITLY NOT ASSUMED

FIELD EVOLUTION != REGISTERED ACTION
NO REGISTERED ALLOWED ACTION -> NO ACTOR EBU TRANSACTION
HISTORICAL EBU ENTRIES ARE NOT REPRICED
CURRENT FIELD PRICES A NEW REGISTERED ACTION
```

These accounting boundaries preserve baseline §§8–9 and §16: permanence of recorded
entries does not establish cross-field physical commensurability. Neither integral term
creates an actor transaction.

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
The second supplies a canonical-equilibrium physical justification for a particular V
governing a particular observed distribution. Its density conclusion can also hold in
other dynamics; density agreement alone does not establish reversible equilibrium.
```

---

## 9. R6 — Canonical equilibrium is sufficient for the thermal bridge

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

### 9.2 Assumptions separated by what they establish

The following are sufficient conditions for the intended physical benchmark, not a list
of mathematically necessary conditions for every occurrence of `p ∝ exp(−V)`.

**A — canonical density derivation.** E1–E5 and E8 specify the physical and measure context
used in §9.1:

```
E1  the canonical ensemble is independently physically justified at fixed theta
E2  the declared reference measure and support give 0 < Z_theta < infinity
E3  U_theta is the correct configurational energy for that measure; any density-of-states
    or marginalisation factor is accounted for, not silently discarded
E4  T_theta > 0 is the bath temperature; E1a measures it independently
E5  the declared coordinates/support represent the canonical density being compared;
    eliminated coordinates do not introduce an unaccounted x-dependent factor
E8  x*_theta and the thermal normalization are declared and fixed within each field
```

The displayed `dx` in §9.1 denotes the specified Lebesgue measure in the accessible
coordinates. A different reference measure must be declared; densities and their
curvatures are interpreted relative to it. Given the density form and normalization,
`−ln p = V + C` follows algebraically. Independent measurement is needed for a non-circular
empirical test, not for the subtraction or logarithm identity.

**B — reversible canonical equilibrium.** The dynamics must additionally preserve the
canonical measure and obey detailed balance with the appropriate time reversal. In E1a's
overdamped configurational setting, this is the zero-stationary-current condition:

```
E6  detailed balance / zero stationary probability current for the declared overdamped
    configurational dynamics and equilibrium boundary conditions
```

This is a stronger statement than density agreement. A divergence-free nonzero current
can preserve the same Boltzmann density (§13.3). Failure of E6 removes the ordinary
reversible-equilibrium interpretation, not necessarily the density identity. No equivalence
of zero current and detailed balance is asserted for arbitrary variables or dynamics.

**C — accepted entropy / P4 interpretation.** E1a design §§8–9 additionally require the
declared conservative overdamped model; fixed field and temperature; one reservoir;
the stationary equilibrium distribution at both times; and no additional work input omitted
from the accounting. These jointly justify `Δs_med = +k_B E`, `Δs_sys = −k_B E`, and
`Δs_tot = 0` in that benchmark. Density shape alone does not justify all three. The
constrained-macrostate result has its separate ensemble and boundary assumptions (§14).

**D — observation and estimation.**

```
E7  observations represent the stationary distribution rather than an unaccounted transient;
    a time-series estimate additionally needs a justified sampling/ergodicity argument
```

Ergodicity and finite-sample adequacy are sampling issues. They are not needed to take the
logarithm of a supplied density or to differentiate its potential. E1a's independent
branches remain mandatory for its empirical comparison.

```
CLASSIFICATION: STANDARD CANONICAL DENSITY DERIVATION, with separately stated
REVERSIBILITY, ENTROPY and SAMPLING conditions. No universal nonequilibrium bridge
and no new statistical-mechanical discovery are asserted.
```

---

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
> the density assumptions in §9.2 A, `β = 1` follows algebraically. A successful experiment
> is "consistent with the known equilibrium bridge under independent physical and statistical
> measurement" — never
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

### 11.1 General Boltzmann bridge and differential corollary

The canonical derivation of §9.1, under §9.2 A, does not assume `U_θ` quadratic. Where
`p_θ ∝ exp(−V_θ)` on the declared support and measure,

```
J_theta := -ln p_theta = V_theta + C_theta
K_theta(x) := Hess_x J_theta(x) = Hess_x V_theta(x) = H_theta(x)
```

The second line holds on the relevant smooth interior region wherever these derivatives
exist (for example, for `C²` potentials). The relative rarity `J_prob = -ln[p(x)/p(x*)]`
differs from `J_theta` by a constant and has the same Hessian. This is a **general
differential corollary**, not a Gaussian assumption. For `V = x²/2 + x⁴`, for example,
`K(x) = H(x) = 1 + 12x²` despite the non-Gaussian density. No boundary derivative or
covariance-inverse identity follows from this interior calculation.

A quartic or double-well potential can therefore satisfy `β_bridge = 1` without being
Gaussian. The density still requires normalizability and an appropriate physical
justification for the empirical interpretation; defining it from `V` is not evidence.

### 11.2 Global harmonic Gaussian corollary — support matters

Sufficient assumptions for the inverse-covariance identity are:

- `V_θ(x) = ½(x−x*)ᵀ H_θ(x−x*)` throughout the **full accessible affine state space**;
- Lebesgue measure in declared orthonormal coordinates on that space;
- symmetric positive-definite `H_θ` on **all accessible directions**, and `β_bridge > 0`;
- normalizability, with no truncation or boundary that changes the Gaussian moments;
- the density bridge `p_θ ∝ exp(−β_bridge V_θ)` on that space.

Then, in those accessible coordinates,

```
Sigma_theta = beta_bridge^(-1) H_theta^(-1)
K_theta = beta_bridge H_theta = Sigma_theta^(-1)
at beta_bridge = 1:   Sigma_theta^(-1) = H_theta
```

For an affine constraint `x = x* + Qz`, use the restricted curvature `H_T = QᵀHQ`
and covariance of `z`; the ambient covariance need not be invertible. This preserves
baseline §5's accessible-direction warning.

**Bounded-support counterexample.** With `V(x) = x²/2` and
`p(x) = Z^(-1) exp(−x²/2)` on `[-1,1]`, symmetry gives mean zero. Integration by parts,
using `(x exp(−x²/2))' = (1−x²) exp(−x²/2)`, gives

```
Z = int_{-1}^{1} exp(-x^2/2) dx
Sigma = Var(x) = 1 - 2 exp(-1/2)/Z < 1
K(x) = H(x) = 1 on (-1,1), but Sigma^(-1) != H
```

The interior density bridge and curvature identity survive truncation; the global Gaussian
moment formula does not. No assertion about the Hessian at the support boundary is made.
A local near-minimum quadratic expansion alone gives neither an exact global Gaussian
nor its covariance. An approximation needs its own error control.

```
GENERAL BOLTZMANN BRIDGE             J = V + C
GENERAL DIFFERENTIAL COROLLARY      K(x) = Hess V(x), on a smooth interior
GLOBAL HARMONIC GAUSSIAN COROLLARY   Sigma^(-1) = H, only with the assumptions above
```

### 11.3 Why the direction matters

`K(x*) = βH(x*)` is a local curvature statement; `−ln p = βV + C` holds across a
landscape. The landscape identity implies the curvature identity where differentiable.
The reverse does not follow from a Hessian at one point. Even for full Gaussians, common
mean/reference, support and measure must accompany equal precision for density equality;
the Hessian alone does not fix the mean. The three levels above must remain distinct.

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
> §13.1 follows from a supplied potential. Density, reversible dynamics, entropy accounting
> and empirical sampling require their separate justifications in §9.2 A–D.

### 13.3 R5 — Density agreement is not reversible equilibrium

The following are boundaries on the accepted equilibrium derivation, not proofs that every
listed mechanism necessarily changes a stationary density:

| mechanism | what follows, and what does not |
|---|---|
| nonzero stationary probability current | violates zero-current reversible equilibrium in the declared overdamped setting; **does not necessarily destroy Boltzmann density agreement** |
| detailed-balance violation | removes the reversible-equilibrium guarantee and its entropy-accounting interpretation; the same density can still be invariant |
| time-dependent fields or lag | instantaneous canonical density is not automatically the actual density; any exact tracking or lag approximation needs separate justification |
| dissipative or externally driven work | the accepted no-omitted-work entropy accounting cannot be carried over without checking the full work/heat model |
| entropy production | the E1a equilibrium cancellation `Δs_tot = 0` is not guaranteed; the affine foundation ansatz alone supplies no production law |
| nonconservative forcing | total work may be path-dependent; the identity for any independently supplied gradient contribution remains exact (§5) |

**Exact nonreversible-density counterexample — mathematical only.** In dimensionless
coordinates and thermal units, let

```
V(x,y) = (x^2+y^2)/2
p(x,y) = (2 pi)^(-1) exp(-V(x,y))
b(x,y) = (-x-y, -y+x)
diffusion operator = Laplacian; probability current j = b p - grad p
```

Since `grad p = (-x,-y)p`, one obtains

```
j = (-y,x)p
div j = -y(-x p) + x(-y p) = 0
j/p at (1,0) = (0,1) != 0
```

The normalized density is stationary, with decay at infinity, despite its nonzero
stationary current. Thus `p ∝ exp(−V)` and `β_bridge = 1` do not certify detailed balance.
This is a closed-form counterexample to a necessity claim, not an adopted EBU dynamics
model, a new nonequilibrium bridge, or a simulation. Baseline §18's quarantine remains.
The equilibrium entropy/P4 claims still require all their own conditions in §9.2 C.

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

| object | value under the declared conditions | scope of the accepted interpretation |
|---|---|---|
| medium entropy change `Δs_med` | `+k_B E_θ` | conservative overdamped, fixed-field, fixed-temperature single-bath process with no omitted additional work |
| stochastic system entropy `Δs_sys` | `−k_B E_θ` | follows from stochastic entropy `−k_B ln p` and the same Boltzmann density at both times; this identity alone does not certify reversibility |
| total stochastic entropy production `Δs_tot` | **`0`** — not `k_B E` | the full static-equilibrium conditions of E1a design §9, including both preceding contributions |
| constrained-macrostate entropy deficit `ΔS_constr` | `k_B E_θ` + remainder | separate microcanonical bead-plus-reservoir derivation, bead held at `x`, constant-volume derivatives and large-reservoir regime |

**Which statements connect to `E`, and under what scope:**

```
PURELY MATHEMATICAL, no equilibrium   Delta S / kappa = E   (foundation section 21, GIVEN the
                                      affine ansatz with constant kappa and constant S_eq --
                                      it is a change of variable, not a physical result)

ACCEPTED BENCHMARK INTERPRETATION     The joint medium/system/total entropy statements use
                                      all conditions of E1a design section 9. The benchmark's
                                      kappa = k_B is not a universal identification. A matching
                                      density alone cannot supply the missing dynamical or
                                      work-accounting conditions.
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
`F_trap = −∇U_θ`, as E1a design §9 declares. Therefore

```
W_by_trap = int F_trap . dx = -int grad U_theta . dx = U_pre - U_post
E_theta = W_by_trap / (k_B T_theta)
```

This is the **normalized conservative-force / trap-work contribution**, with fixed `θ`,
fixed `T`, and `V_θ = (U_θ − U_θ*)/(k_B T_θ)`. The work is **BY the trap force**.
For quasistatic externally imposed motion against that conservative force, the corresponding
external work is `−W_by_trap`; it is not the same signed quantity. Example: `U=x²/2`,
`0→1`, gives trap work `−1/2` and external work against the trap `+1/2`.

The repository's accepted entropy terminology remains **entropy delivered to the thermal
reservoir**, `Δs_med = +k_B E_θ`, only under the no-omitted-work conditions of design §9.
The externally imposed example establishes the mechanical sign, not that entropy claim.
The general foundation `V` carries no mechanical identification, because foundation §2
Question B says its physical origin "is not derived".

---

## 16. Measurement error and approximation — bounded, not universalised

### 16.1 A uniform potential-error bound, independent of discrepancy source

If the estimated potential is `V̂(x) = V(x) + δ(x)`, then for any pair of states,

```
Ê_ab − E_ab = [V̂(a) − V̂(b)] − [V(a) − V(b)] = δ(a) − δ(b)
```

and if `|δ(x)| ≤ ε` uniformly on the states used,

```
| Ê_ab − E_ab | ≤ 2ε
```

If potential errors are modelled as random with finite covariance `C_V`, then for edge
errors `Dδ`, where `D` has `+1` at the source and `−1` at the destination,
`C_E = D C_V Dᵀ`. In particular,

```
Var(delta_a - delta_b) = Var(delta_a) + Var(delta_b) - 2 Cov(delta_a, delta_b)
```

The same linear covariance rule applies to random potential values. It does not require
independent node errors.

```
CLASSIFICATION: UNIFORM ERROR BOUND FOR TWO DEFINED SCALAR POTENTIALS.
The discrepancy may come from measurement, calibration, approximation or another source.
The scientific task of establishing the uniform bound is separate. This arithmetic does
NOT establish that a valid potential exists, establish equilibrium, or validate a model
outside its domain.
```

### 16.2 The six error kinds, which must not be merged

| kind | what it is | does the bound of §16.1 apply? |
|---|---|---|
| measurement error in `V` | measured values differ from the target potential | **yes, if** the uniform residual bound is established |
| parameter-estimation error | `V̂ = V(·; θ̂)`, `θ̂ ≠ θ` | **yes, if** parameter uncertainty implies the stated uniform potential bound |
| model approximation error | the approximating family differs from a defined target potential | **yes, if** their uniform difference is bounded on the relevant common domain |
| failure of potential representation | no single-valued target `V` exists | **no** — the bound presupposes two defined potentials |
| field-calibration error | the estimated field changes the potential | **yes, if** the resulting potentials satisfy the uniform bound on the relevant common domain |
| departure from equilibrium | the physical bridge lacks its equilibrium guarantee | **not by itself a potential-error bound**; any supplied potentials still obey the arithmetic if bounded, but this does not restore a physical bridge |

No universal size for any discrepancy is claimed, and no nonequilibrium correction is guessed.

---

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

ACCURACY RELATIVE TO REALITY     Requires a justified target potential, domain and error
                                 bound; algebraic closure supplies none of them.
```

A further point that matters for later topological and economic use: with `δ_A = 1/5`,
`δ_C = 1/8`, the true error on `E_AC` is `δ_A − δ_C = 3/40`, and **`δ_B` does not appear at
all**. The intermediate node's error cancels *deterministically*, before any variance is
taken. For adjacent-edge errors `X = δ_A−δ_B` and `Y = δ_B−δ_C`, retain

```
Var(X+Y) = Var(X) + Var(Y) + 2 Cov(X,Y)
```

Omitting covariance **overestimates** variance when the covariance is negative,
**underestimates** it when positive, and leaves it unchanged when zero. With mutually
independent node errors, the shared-node contribution gives `Cov(X,Y)=−Var(δ_B)`;
that special case explains overestimation, but it is not general.

Exact symbolic counterexample: take centered errors `δ_A=0`, `δ_B=ξ`, `δ_C=2ξ`, with
`Var(ξ)=σ²>0`. Then `X=Y=−ξ`, true endpoint-error variance is `4σ²`, and the naive
sum is only `2σ²`. No samples are drawn. Graph/path propagation must preserve the full
covariance structure.

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
  ERROR TYPE       bounded potential discrepancy (section 16.1); representation failure
                   is OUT OF DOMAIN, not a small error
  OUT OF DOMAIN    V multivalued; V not C^1; path leaving Omega; theta varying
  SPECIAL CARE     an additional nonconservative force does NOT invalidate this identity;
                   total physical work needs separate accounting. f is not generally a
                   mechanical force; same-base summation is not telescoping
  STATUS           ALREADY A FOUNDATION THEOREM (section 3 + section 25)

LAYER F -- EXTENDED STATE, FIELD-CHANGING PATH
  ASSUMPTIONS      V(x,theta) single-valued and C^1 in BOTH arguments on the extended domain
  DOMAIN           paths q -> (x(q), theta(q)); theta scalar OR vector
  CONCLUSION       V_pre - V_post = -int grad_x V . dx - int grad_theta V . dtheta
                   and telescoping holds on the extended space
  ERROR TYPE       as Layer P, plus field-calibration error
  OUT OF DOMAIN    V not jointly C^1; theta discontinuous without a declared jump convention
  SPECIAL CARE     the separate integrals MAY depend on the joint path; neither is generally
                   guaranteed to be an endpoint function. Separability can make both exact.
                   The total is necessarily an endpoint function. NO attribution follows.
  STATUS           PROPOSED. The foundation declares the scoping and forbids omitting the
                   term (section 17) but does not write the integral. Open questions 5 and 11;
                   roadmap gate P4.

LAYER E -- CANONICAL DENSITY BRIDGE, WITH DISTINCT PHYSICAL CONDITIONS
  ASSUMPTIONS      section 9.2 A suffices for the canonical density derivation
  DOMAIN           canonical configurational density on the declared support and measure,
                   with the correct U and thermal normalization
  CONCLUSION       p_theta proportional to exp(-V_theta); J = -ln p = V + C;
                   beta_bridge = 1
  ERROR TYPE       thermometry/U-calibration error; finite-sample statistical error
  SPECIAL CARE     reversibility requires section 9.2 B; entropy/P4 requires 9.2 C;
                   sampling requires 9.2 D. Density alone certifies none of these.
                   Outside canonical equilibrium the density identity is not guaranteed,
                   but can still hold. Independent branches prevent circular validation.
  STATUS           STANDARD CANONICAL STATISTICAL MECHANICS. Not a new EBU result.

LAYER K -- GENERAL DIFFERENTIAL COROLLARY
  ASSUMPTIONS      J = V + C on the relevant smooth interior, with second derivatives
  CONCLUSION       K(x) = Hess V(x) = H(x)
  SPECIAL CARE     requires neither Gaussianity nor an inverse-covariance identity;
                   no derivative claim at a support boundary
  STATUS           DIFFERENTIATION of the density bridge, not an equilibrium certificate

LAYER G -- GLOBAL HARMONIC GAUSSIAN COROLLARY
  ASSUMPTIONS      density bridge; globally quadratic V on the full accessible affine
                   space; Lebesgue measure in its orthonormal coordinates; positive-definite
                   restricted H; normalizability; no moment-changing truncation (section 11.2)
  CONCLUSION       Sigma^(-1) = H at beta_bridge = 1, in accessible coordinates
  ERROR TYPE       approximation requires its own error control
  OUT OF DOMAIN    truncated support; merely local harmonic approximation; unconfined null
                   directions; anharmonic V for this exact Gaussian moment identity
  SPECIAL CARE     local K = H does not establish this global covariance result
  STATUS           GLOBAL GAUSSIAN COROLLARY, not the general bridge

LAYER N -- NONEQUILIBRIUM
  STATUS           NO GENERAL BRIDGE ESTABLISHED. No new EBU formula proposed.
                   Section 13.3 distinguishes a loss of guarantee from a necessary failure.
```

---

## 19. Conceptual diagram

```
supplied state potential V
    |-- fixed theta + C1 + admissible path -> endpoint/path identity (Layer P)
    |-- joint C1 V(x,theta) -> full state/field chain rule (Layer F)
    |                         total exact; separate terms may depend on joint path
    |
    +-- independently justified canonical density + thermal normalization (9.2 A)
            -> J = V + C, beta_bridge = 1 (Layer E density conclusion)
                |-- smooth interior -> K(x) = Hess V(x) (Layer K)
                +-- global quadratic + full support/measure/positivity (11.2)
                        -> Sigma^(-1) = H (Layer G)

Reversible dynamics / detailed balance: separate conditions (9.2 B)
Accepted entropy / P4 interpretation:   full additional conditions (9.2 C)
Sampling and estimation:               separate requirements (9.2 D)

Nonequilibrium / nonconservative setting
    -> supplied-potential mathematics remains valid within its domain
    -> Boltzmann density and Gaussian moments are NOT guaranteed, but may persist
    -> density agreement alone does NOT certify reversibility or P4 accounting
```

Thus "the EBU potential mathematics still works out of equilibrium" does not imply
"therefore the physical bridge holds". Conversely, failure of reversible-equilibrium
conditions does not by itself prove that the density identity is false.

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
        -> direct Boltzmann bridge beta=1 (Layer E density conclusion)
        -> differential K = Hess V        (Layer K, smooth interior)
        -> global Gaussian Sigma^-1 = H   (Layer G, section 11.2 assumptions)
        -> statistical implementation
```

```
IS THIS ORDERING SCIENTIFICALLY COHERENT?   YES.
```

This is a proposed order of justification, not a claim that the physical experiment is
validated by the algebra. It respects the foundation's Question A / Question B distinction
(§2): `K = βH` follows by differentiation from the density bridge, while identifying that
curvature with `Σ^(-1)` needs the additional global Gaussian assumptions.

One refinement this reconstruction suggests, as a proposal: the redesign document treats
`p ∝ exp(−βV)` as "the deepest EBU question". Its canonical justification above is a
**Layer E** statement from standard equilibrium statistical mechanics; the same density
identity need not imply reversible equilibrium. Layers P and F need no equilibrium at all. The deepest *EBU* question is whether a
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
     NOT AS A MATHEMATICAL NECESSITY. Section 9.2 A supplies the canonical physical
     derivation; B, C and D separately justify reversibility, entropy/P4 and sampling.
     A current-carrying stationary density can still satisfy beta_bridge = 1.

Q5   DOES beta_bridge = 1 REQUIRE GAUSSIANITY?
     NO. The derivation never assumes U quadratic.

Q6   DOES K=H REQUIRE THE GAUSSIAN/HARMONIC SPECIAL CASE?
     NO -- J = V + C implies K(x) = Hess V(x) on a smooth interior. The additional
     identity Sigma^-1 = H requires the global Gaussian assumptions in section 11.2.

Q7   WHEN theta CHANGES, IS -int grad_x V . dx ALONE GENERALLY ENOUGH?
     NO. Example C: the state term gives -4 against a total of -15/2; the field term
     carries 7/15, about 46.7%, of the endpoint difference.

Q8   DOES THE FULL EXTENDED-STATE DIFFERENTIAL ADD A FIELD TERM?
     YES -- minus the integral of grad_theta V against d theta, kept in inner-product
     form because theta may be vector-valued.

Q9   DOES A NONCONSERVATIVE PATH-DEPENDENT CONTRIBUTION REQUIRE SPECIAL TREATMENT?
     YES. Example D: same endpoints, values +1 and -1, closed loop 2 != 0. No state
     function represents that field's work. A separately supplied gradient contribution
     remains exact and must not be confused with total work.

Q10  DO PURE FIXED-FIELD TOPOLOGY IDENTITIES REQUIRE beta=1?
     NO. Foundation section 12 needs only that V be a state function.

Q11  DO CROSS-FIELD PHYSICAL EBU ADDITIONS REQUIRE ADDITIONAL COMMENSURABILITY EVIDENCE?
     YES. Extended-space telescoping is mathematics; a common denomination is physics.

Q12  SHOULD THE CURRENT FROZEN FOUNDATION BE AMENDED NOW?
     NO. No R1-R6 scientific amendment is indicated. Freeze provenance resolves the
     authority status; the stale header is a documentary / metadata inconsistency whose
     cleanup is outside this task, not an unresolved scientific decision.

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
| canonical assumptions suffice for `β_bridge = 1` | **CONDITIONAL CANONICAL DERIVATION** — §9.2 A; reversibility, entropy and sampling are separate |
| `β_bridge = 1` needs no Gaussianity | **MATHEMATICALLY SETTLED** — §11.1 |
| `K(x) = H(x)` on a smooth interior | **GENERAL DIFFERENTIAL COROLLARY** of `J = V + C` — §11.1 |
| `Σ^(-1) = H` | **GLOBAL GAUSSIAN COROLLARY**, only under §11.2's support/measure/positivity assumptions |
| circular `p ∝ exp(−V)` proof forbidden | **ALREADY AUTHORISED** — §21, §25 |
| nonconservative contributions need separate treatment | **MATHEMATICALLY SETTLED**, and **ALREADY AUTHORISED** as a do-not-promote item in the baseline |
| `Σ E = 0` is not the first law | **ALREADY AUTHORISED** — §25 forbidden column |
| the explicit `−∫∇_θV·dθ` term | **PEDAGOGICAL CLARIFICATION** — scoped and named by §17, not written out |
| state/field attribution to actors | **FUTURE NONEQUILIBRIUM / ATTRIBUTION THEORY** — §23 Q11, roadmap P4 |
| nonequilibrium bridge | **FUTURE NONEQUILIBRIUM THEORY** — no formula proposed |
| book-series topology wording | **NOT VERIFIED** — not audited in this task |
| stale foundation header conflicts with freeze provenance | **DOCUMENTARY / METADATA INCONSISTENCY** — frozen authority confirmed in F-6; no scientific decision required |

### Human scientific decisions required for R1–R6

**NONE identified by this bounded repair.** The former D1 foundation-status decision is
removed because freeze provenance resolves it. No replacement decision is introduced.
Adopting any future clarification at a new authority rank remains outside this repair and
is not required for its mathematical correctness. Open physical questions already marked
in the foundation remain open. Independent re-audit, not this repair's self-check, decides
whether R1–R6 is cleared.

---

## 25. Identities and state

Report-only. The original reconstruction recorded the identities below. This bounded repair
recomputed them before and after editing: all are unchanged. The report is outside the
analysis and execution identity preimages inspected in `e1a_v4/identity.py` and
`e1a_v4/validation/plan.py`; no authority identity was adjusted.

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

**Historical validation record from the original reconstruction — not rerun by this repair:**

```
4,002 checks, 0 failures, 17 suites, 0 not clean ; static preflight PASSED
execution_authorised = false ; execution seal state PRE_DRIVER, NOT FROZEN
OFFICIAL CAMPAIGN NOT RUN       SCIENTIFIC RNG DRAWS   0
OFFICIAL RESULTS  NONE          OFFICIAL TRAJECTORIES  0
REAL OPTICAL-TRAP EXPERIMENT NOT RUN             CALIBRATION EXECUTIONS 0
```

### Bounded repair verification — 2026-10-05

The repair used exact rational polynomial integration and closed-form algebra, strict JSON
parsing, static inspection of the identity recipes, SHA-256 recomputation and Git inspection.
No scientific package was imported; no RNG, trajectory, Monte Carlo, calibration, campaign,
test suite or execution preflight was run. The historical 4,002-check claim above is not
presented as new validation evidence.

| deterministic recheck | result |
|---|---|
| Example A | endpoint and integral both `−9` |
| Example B | straight, L-shaped and curved paths all `−9`; closed gradient loop `0` |
| Example C | state `−4`, field `−7/2`, total `−15/2` |
| Example D | routes `+1` and `−1`; closed nonconservative loop `2` |
| Example E | telescoping `17/2`; endpoint residual `3/40` |
| stationary-current counterexample | `div j = 0`, `j != 0`, Boltzmann density retained |
| truncated harmonic density | exact integration-by-parts variance formula; `K=H=1` in the interior, `Σ^(-1) != H` |
| covariance sign | with unit edge variances, covariance `−1,0,+1` gives total variance `0,2,4`; naive sum is `2` |
| separable state/field potential | individual endpoint values `−3/2`, `−15/2`; total `−9` |
| mechanical sign | trap work `−1/2`; quasistatic external work against trap `+1/2` |
| foundation provenance | current bytes identical to freeze commit; sidecar SHA and 49,098-byte count match |
| analysis / execution identity recipes | independently reconstructed using only static source data and hashing; both match §25 |
| authorization / seal | plan and seal both `execution_authorised = false`; seal `PRE_DRIVER`, expected execution identity `null` |
| allowed-file and whitespace checks | complete diff reviewed; only this report changed; `git diff --check` passed |

`results/e1a_v4_validation` remains absent. The seal's state above is reported literally;
it is not an assertion that its historical driver-absence commentary describes current code.
No seal or authorization change is made.

### Disposition of the six audit findings

| finding | repair | sections |
|---|---|---|
| 1 — probability current and supplied-potential boundary | **CORRECTED**: density agreement separated from reversibility/P4; added force does not destroy a supplied gradient identity | §§5, 8–9, 13–14, 18–19, 22–24 |
| 2 — harmonic covariance | **CORRECTED**: smooth-interior curvature separated from global Gaussian moments; support, measure and positivity explicit | §§11, 18–19, 22–24 |
| 3 — work sign | **CORRECTED**: work by the conservative trap; external work against it has opposite sign | §§5, 15 |
| 4 — uncertainty | **CORRECTED**: covariance sign retained; uniform bound applies to any bounded discrepancy between defined potentials | §§16, 18 |
| 5 — field/state decomposition | **CORRECTED**: separate terms may depend on path; separable counterexample and actor-accounting boundary explicit | §§7, 18–19 |
| 6 — foundation status | **CORRECTED**: frozen provenance verified; documentary inconsistency; D1 removed | F-6, §§23–25 |

These are repair dispositions, not an independent clearance verdict.

### Required repair classifications

```
PATH INTEGRAL ALREADY PRESENT: YES
FIXED-FIELD ENDPOINT IDENTITY: exact for a supplied state function; line-integral equality
    under single-valued C1 V and an admissible piecewise-smooth path in its domain
NONZERO CURRENT NECESSARILY DESTROYS BOLTZMANN DENSITY: NO
BOLTZMANN DENSITY ALONE CERTIFIES REVERSIBLE EQUILIBRIUM: NO
GENERAL CURVATURE IDENTITY K=H: J=V+C implies K=Hess V on the smooth interior where
    second derivatives exist; no Gaussianity or boundary claim
GLOBAL Sigma^-1=H: only with the full accessible affine support, Lebesgue measure,
    global positive-definite quadratic potential and normalizable untruncated density
    of section 11.2, at beta_bridge=1
TRAP WORK SIGN: E = W_by_trap/(k_B T) in the fixed-field thermal benchmark;
    quasistatic external work against the conservative trap has the opposite sign
UNCERTAINTY COVARIANCE: MUST BE RETAINED; omitting it can overestimate, underestimate
    or leave variance unchanged
UNIFORM POTENTIAL ERROR BOUND: sup |V_hat-V| <= epsilon implies |E_hat-E| <= 2 epsilon
    for two defined potentials on the relevant common domain; no physical validation follows
FIELD/STATE TERMS INDIVIDUALLY ENDPOINT FUNCTIONS: NOT GUARANTEED;
    MAY BE UNDER SPECIAL STRUCTURE, including V(x,theta)=a(x)+b(theta)
ACTOR FIELD-CHANGE TRANSACTION: NO; field evolution alone creates no registered action
FOUNDATION AUTHORITY STATUS: FROZEN, confirmed from repository freeze provenance
FOUNDATION HEADER CONFLICT: DOCUMENTARY / METADATA INCONSISTENCY
HUMAN SCIENTIFIC DECISION REQUIRED FOR R1-R6: NONE identified by this repair
R1-R6 READY FOR RE-AUDIT: YES
S-MG THEOREM PROGRAMME: NOT STARTED
BOOK 1: NOT MODIFIED
OFFICIAL LONG-RUN CAMPAIGN: NOT RUN
REAL OPTICAL-TRAP EXPERIMENT: NOT RUN
EXECUTION AUTHORISED: FALSE
EXECUTION SEAL: NOT FROZEN
PUSH: NO
STATUS: R-STAGE REPAIR COMPLETE — RE-AUDIT REQUIRED
```

**This report authorises nothing and amends no controlling authority.**
