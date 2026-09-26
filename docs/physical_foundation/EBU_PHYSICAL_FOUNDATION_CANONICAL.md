# CANONICAL PHYSICAL EBU FOUNDATION — FREEZE CANDIDATE

**STATUS: FREEZE CANDIDATE. NOT FROZEN. NOT COMMITTED. NO REPOSITORY AUTHORITY.**

This document is a synthesis of the audited scientific record. It introduces no
new result, runs no experiment, and modifies no source code. Every equation
below is either quoted from that record or re-derived from it; every
qualification found by an independent audit is carried forward rather than
smoothed away.

## Authoritative source coordinate

| item | value |
|---|---|
| scientific-record branch | `origin/publication/scientific-record` |
| scientific-record commit | `481753895509524c9d2674d1880d87712bb0ec18` |
| scientific-record tree | `19e43ecb07608e76b6e95233a456fcadf8b8a9aa` |
| parent — Stage-A publication | `2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32` |
| Stage-A publication tree | `5afe39788ecc6bff675b0820eef1669fb8b78ebf` |
| `demand_driven_ebu` identity | `f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48` |

All six were verified independently before this document was written. The
package identity was recomputed under the recipe pinned in
`demand_driven_stage_a/sources.py`. All fourteen `EVIDENCE_MANIFEST.json`
entries were re-hashed: **0 byte failures**.

---

# 0. PURPOSE AND STANDING

This is a **conditional mathematical foundation**. Its theorems are exact given
their declared assumptions. It does **not** claim that those assumptions are
physically established, and it marks precisely which are not.

The single controlling rule of this document:

> **Nothing may replace `E = V_pre − V_post` as the general finite EBU
> definition.** Every edge polynomial is a corollary. Every Study-1 formula is a
> specialization. Every actor account is Layer 3. Every economic rule is Layer 4
> or 5.

---

# 1. THE FIVE LAYERS

No concept may move upward between layers without an independent physical
derivation.

| layer | contents |
|---|---|
| **LAYER 1 — PHYSICAL STATE / TRANSITION / CONSERVATION** | physical coordinates `x`; the declared physical transition map `Δx`; routes and stoichiometry; `η` as a physical transfer property of a route; per-resource carrier conservation; explicitly declared environment/sink coordinates where physically modelled |
| **LAYER 2 — EBU FIELD MATHEMATICS** | `V(x;θ)`; `μ = ∇V`; `E = V_pre − V_post`; the exact finite theorems; the local directional quantity `f`; the path integral; factor potentials; interaction/Möbius mathematics |
| **LAYER 3 — ATTRIBUTION / ACCOUNTING** | simultaneous receipt closure; the individual attribution convention; common-path attribution; the Shapley equivalence within its domain; the aggregate `C + V` accounting identity; historical actor contribution accounts |
| **LAYER 4 — ACTOR DECISION** | random; aligned; hostile; any future choice law |
| **LAYER 5 — INSTITUTION / ECONOMY** | affordability; account sign restrictions; borrowing; pooling; queues; service contracts; prices; welfare; privileges; scheduling |

**Layers 4 and 5 appear nowhere in Layers 1–3, and no Layer 1–3 theorem below
requires any of them.**

---

# 2. STATUS OF `V` — THE LOAD-BEARING DISTINCTION

Two questions must never be merged.

**Question A — the mathematics conditional on `V`.** Given a declared potential
`V(x;θ)` with sufficient regularity, the entire structure in §3–§18 follows
exactly. This is not weakened by anything unknown about `V`'s origin.

**Question B — the physical origin of `V`.** Why should a given physical system
have this `V`? **This is not derived.**

General form: `V(x;θ)` is the declared physical-field potential / burden state
function.

Gaussian Level 1:

```
V(x;θ) = ½ Σ_i ((x_i − x*_i)/σ_i)²
```

> **CLASSIFICATION: CONSTITUTIVE PHYSICAL / FIELD HYPOTHESIS.**
> It is **not** a universal physical law, and its exactness as mathematics is
> not evidence for its physical validity. Both independent audits state this
> explicitly: Skeptic 2 classes the Gaussian as a "**model choice**, not physical
> necessity"; the Independent Freeze Audit warns that "mathematical exactness of
> a chosen Gaussian does not establish its physical validity."

Likewise `E := V_pre − V_post` is a **declared definition of the measured
quantity**. Conservation alone does not force it.

---

# 3. CANONICAL GENERAL EBU EQUATIONS

These sit at the top of the hierarchy. Everything after §3 is below them.

```
μ(x;θ) = ∇_x V(x;θ)

E(x_pre → x_post | θ) = V(x_pre;θ) − V(x_post;θ)
```

**Path integral.** For fixed `θ`, a **single-valued `C¹`** potential on the
relevant domain, and any admissible piecewise-smooth path `γ` between the
endpoints lying in that domain:

```
E = − ∫_γ ∇V · dx
```

> **REGULARITY CORRECTION (required by the Independent Freeze Audit, §3).**
> "Differentiable" alone is **not** a sufficient general regularity statement for
> this identity. `C¹` is a simple sufficient condition, and the Gaussian
> satisfies it. Because a single-valued potential is already given, no
> simply-connected-domain assumption is needed; a topology objection that applies
> to an arbitrary curl-free vector field does not apply to an actual gradient.

**Local differential quantity.** For a differentiable physical action path
`x(q)`:

```
f = −dV/dq = −∇Vᵀ (dx/dq)
```

`f` may be called the **LOCAL DIFFERENTIAL DRIVING QUANTITY**, or the **EBU EDGE
FORCE / DRIVING FORCE**, only with this caution attached:

> **CAUTION.** `f` is a mathematical directional derivative. It does **not** by
> itself establish a mechanical law of motion, a measured mechanical force, or
> any dynamical response law. Naming it a "force" is a convention of this
> programme, not a physical finding. Both independent audits state this.

---

# 4. GAUSSIAN LEVEL-1 FINITE THEOREM

For `V(x) = ½ (x − x*)ᵀ H (x − x*)` with symmetric `H = diag(1/σ_i²)`:

```
μ = H(x − x*)

E = − μᵀ Δx − ½ Δxᵀ H Δx
```

**Derivation A — direct expansion.** Per coordinate,
`(x_i + Δ_i − x*_i)² = (x_i − x*_i)² + 2(x_i − x*_i)Δ_i + Δ_i²`. Summing with
weights `1/σ_i²` gives `V(x+Δ) − V(x) = μᵀΔ + ½ΔᵀHΔ`, hence the result. No
approximation and no small-action assumption occurs.

**Derivation B — exact line integral.** Along `γ(λ) = x + λΔ`,
`∇V(x + λΔ) = μ + λHΔ`, so
`E = −∫₀¹ (μ + λHΔ)ᵀ Δ dλ = −μᵀΔ − ½ΔᵀHΔ`. ∎

The two derivations agree identically.

> **CLASSIFICATION: EXACT GAUSSIAN FINITE-EQUATION THEOREM.**
> It is **not** the definition of EBU. The definition remains `E = V_pre − V_post`.

**Independent exact verification — zero mismatches in every tested domain.**

| source | scope | mismatches |
|---|---|---|
| Face the Devil | 4,000 random general-`σ`/`x*` exact-rational cases | **0** |
| Independent Skeptic 2 | 720 general Gaussian cases, dimensions 1–6, unequal rational references and scales | **0** |
| Independent Skeptic 2 | Study-1: **3,662 source-funded nonempty groups across 91 states** | **0** |
| Reconciliation Gate | Study-1: **5,734 feasible (state, group) pairs** under its own declared verification scope | **0** |
| Independent Freeze Audit | 2,768 exact-arithmetic checks; 66,396 checks against saved Stage-A records; all 768 episodes / 11,066 epochs | **0** |

**On the two Study-1 counts.** One independent audit reports **3,662
source-funded groups across 91 states**; the later reconciliation reports
**5,734 feasible (state, group) pairs** under its own verification scope. Each
count is reported exactly as its author defined it, and neither is a correction
of the other.

**The scopes are not completely documented in the authoritative record, and this
document does not manufacture an equivalence between them.** No filtering
reconstruction reconciling `3,662` to `5,734` appears in the preserved reports,
so none is asserted here and no methodology is attributed to either historical
author. A reader needing the exact relationship must derive it independently;
it is not established by the evidence bundle.

---

# 5. FINITE EBU VERSUS LOCAL DIFFERENTIAL VALUE — CANONICAL WARNING

```
first-order quantity:  − μᵀ Δx
exact finite value:    − μᵀ Δx − ½ Δxᵀ H Δx
```

> **THE DERIVATIVE ALONE DOES NOT GIVE THE FINITE ACTION VALUE.**
> The correction `−½ΔᵀHΔ` is second order and is invisible to the gradient.

**The first-order sign can differ from the finite sign.** Exact example, unit
scales, references `(4,4)`, state `(6,4)`, transfer `s→d` of quantity `q`:
`E = 2q − q²` while `E_linear = 2q`.

| `q` | first-order estimate | exact finite `E` |
|---|---:|---:|
| `1/10` | `1/5` | `19/100` |
| `1` | `2` | `1` |
| **`3`** | **`+6`** | **`−3`** |

At `q = 3` the first-order estimate is positive and the exact finite value is
negative.

### Strict negativity at equilibrium — CORRECTLY SCOPED

At `μ = 0` the first-order term vanishes for every action, yet a finite
displacement is generally not free:

```
E = − ½ Δxᵀ H Δx
```

> **EXACT CRITERION.** For quadratic `V` with `H` positive **semi**definite, at
> `x = x*` we have `E = −½ ΔᵀHΔ`, and therefore
>
> ```
> E < 0   iff   ΔᵀHΔ > 0
> E = 0   iff   Δ lies entirely in the nullspace of H
> ```
>
> The criterion is a property of `Δ` **relative to `H`**, not a property of
> which coordinates `Δ` happens to touch.

**A displacement may contain BOTH valued and unvalued (zero-curvature)
components and still have `E < 0`**, provided its valued component contributes
`ΔᵀHΔ > 0`. Only a `Δ` lying *entirely* in the nullspace gives `E = 0`.

**Verified exactly, in all three regimes:**

- **Mixed displacement — strictly negative.** In `audit_sink_world` (fixture:
  `sand|A`, `sand|B` valued; `sand|W` a `sink_audit_only` coordinate with no
  reference and no scale), the displacement `Δ = (−1, ½, ½)` from the reference
  state `(10, 10, 0)` has a **nonzero component in the unvalued sink direction**
  and nevertheless gives **`E = −5/8 < 0`**.
- **Pure-nullspace displacement — exactly zero.** In the same fixture the
  displacement `(0, 0, 3)` lies entirely in the nullspace of `H` and gives
  **`E = 0`**, not `E < 0`. This is what refutes the unrestricted claim.
- **Fully valued displacements.** Over all **60** nonzero conservative
  displacements at Study-1's `x* = (4,4,4)`, where all three coordinates are
  positively valued: **0 failures** of `E < 0`.

> **DO NOT STATE:** that any unvalued component destroys strict negativity. That
> is false — the `(−1, ½, ½)` witness above has one and is strictly negative.
> The governing condition is `ΔᵀHΔ > 0`.

This sign correction is guaranteed for a positive-definite quadratic potential.
It is **not** a universal sign theorem for arbitrary nonconvex potentials.

---

# 6. EDGE ACTION — KEPT BELOW `E`

EBU is never defined by an edge polynomial. If a specific physical action has
`Δx = q S_e`, the authoritative value is

```
E = V(x) − V(x + q S_e)
```

Only **after** choosing a Gaussian `V` **and** a specific `S_e` may an explicit
`q`-polynomial be derived. Such a polynomial is an expansion of the definition
under a chosen `Δx`, never a replacement for it.

---

# 7. LOSS / ENVIRONMENT DOMAIN

**This is settled from the authoritative implementation, not from theory.**

For `η < 1`, the generic declared physical transition is

```
source       −q
destination  +η q
sink         +(1−η) q
```

`PhysicalAction.increment` writes exactly this. `Route` validation **refuses**
`0 < η < 1` without a declared sink, and **refuses** a sink when `η = 1`. Both
sink declarations already exist as fixtures: `sink_in_potential` and
`sink_audit_only`.

> **THE SINK COORDINATE WAS NOT INVENTED BY ANY AUDIT OR BY THIS DOCUMENT.** It
> is part of the authoritative physical state model. No new physical coordinate
> is introduced here.

From `dx/dq = (−1, η, 1−η)` the chain rule gives, in the general declared loss
branch, the **exact** local quantity

```
f_e = μ_s − η μ_d − (1−η) μ_sink
```

whose sink contribution is the single term `−(1−η) μ_sink`.

> **THE SINK TERM VANISHES EXACTLY WHEN `(1−η) μ_sink = 0`.** That is the
> condition, and it can be met in two independent ways:
>
> **A.** `η = 1`, so the sink **coefficient** `(1−η)` is zero; or
> **B.** `μ_sink = 0`, because the sink coordinate is **not valued** by `V`.
>
> **DO NOT STATE** that `η = 1` implies `μ_sink = 0`. These are different
> statements about different objects — one is a property of the route, the other
> a property of the potential — and neither implies the other.

The three declared cases, kept distinct:

| declared situation | exact local quantity | why the sink term behaves so |
|---|---|---|
| **lossless Study-1 transition** — `η = 1`, no sink coordinate participates | `f_e = μ_s − μ_d` | coefficient `(1−η) = 0`; no sink term exists to evaluate |
| **CASE A** — lossy route, **audit-only** sink | `f_e = μ_s − η μ_d` | `μ_sink = 0`, since `V` does not value that coordinate |
| **CASE B** — lossy route, **valued** sink | `f_e = μ_s − η μ_d − (1−η) μ_sink` | The sink marginal must be included in the general formula; its contribution may vanish at particular states, including when the sink is at its reference. |

**Neither branch may replace `f = −∇Vᵀ dx/dq`.** Case A's two-coordinate form
remains correct exactly when the loss coordinate is outside `V` or its
contribution vanishes; it is **incomplete otherwise**.

Worked example from the record (unit scales, `x = (6,5,2)`, `r = (4,4,0)`,
`η = 1/2`): the full force is `1/2`, while omitting the sink gives `3/2`. The
exact finite differences satisfy `E(q)/q = 1/2 − (3/4)q`, which approaches
`1/2` — confirming the three-term form, not the two-term one.

> **STAGE A IS UNAFFECTED.** The Study-1 domain declares `η = 1` and no sink, and
> `study_one.py` refuses both. Neither loss branch is a loss-aware experimental
> result: **no registered study has exercised them.** The out-of-domain
> demand/coupling study limitations remain open.

### Reconciled position on a recorded discrepancy

`CROSS_REPORT_NOTES.md` Discrepancy 2 records that the Reconciliation Gate
summarized Independent Skeptic 2 as asserting no third term, and recorded the
valued-sink form as "not stated" by either audit. **That characterization was
wrong.** Independent Skeptic 2 §3 ("Essential qualification") contains the
valued-sink qualification, the third term and a worked example. The
reconciliation disclosed the cause itself: it held the full text of only one of
the two audits.

**Reconciled position: both branches were independently derived by Skeptic 2,
the Independent Freeze Audit and the Final Freeze-Closure Audit, and both are
carried above.** The historical bodies are unchanged; this states the resolved
position, as §1 of the build instruction permits.

---

# 8. VALUED LOSS — CORRECT WORDING AND A REQUIRED COUNTEREXAMPLE

> **DO NOT STATE:** that a valued sink automatically makes a lossy action
> negative EBU.
>
> **CANONICAL STATEMENT:** a valued sink contributes its declared change in `V`.
> The sign of the **complete action** is determined only by
> `E = V_pre − V_post` over the **complete valued state**.

**Exact counterexample — a lossy action with a valued sink and POSITIVE total
EBU.** In `loss_world` (`sand|A`, `sand|B`, `sand|C` valued with reference 10,
scale 1; `sand|W` a `sink_in_potential` coordinate with reference 0, scale 1;
route `A→B` at `η = 1/2`), at state `(20, 0, 10, 0)`, moving one unit:

```
increment  = (−1, +1/2, 0, +1/2)        sum = 0
post-state = (19, 1/2, 10, 1/2)
V_pre = 100        V_post = 343/4
E = 57/4 > 0
```

The sink's own contribution rises from `0` to `1/8` — genuinely adverse — but
the restoration at `B` outweighs it. Verified exactly and independently.
Furthermore, with a nonzero sink reference even the sink contribution need not
always be adverse.

> **RECORDED SOURCE DIVERGENCE — NOT CORRECTED IN PLACE.**
> `demand_driven_ebu/valuation.py` (module docstring) states that a sink inside
> `V` "makes a lossy plan cost EBU." Read as a claim about the sign of the whole
> plan, that wording is **too broad and is falsified by the `E = 57/4` case
> above**. `valuation.py` is inside the package pinned at `f4e31a2a…3eec48`;
> editing it would change that identity and break the Stage-A seal. **The
> divergence is therefore recorded here and the correct statement frozen in this
> document, rather than silently fixed.** Any future supersession of the package
> identity should carry this correction.

---

# 9. GENERAL GAUSSIAN TWO-COORDINATE COROLLARY

For the particular physical increment `Δ_s = −q`, `Δ_d = +q` inside Gaussian
`V`:

```
E = q[ (x_s − x*_s)/σ_s²  −  (x_d − x*_d)/σ_d² ]  −  (q²/2)[ 1/σ_s² + 1/σ_d² ]
```

> **CLASSIFICATION: CONDITIONAL GAUSSIAN TWO-COORDINATE COROLLARY.**
> It is **NOT** the general EBU edge equation. It is `E = V_pre − V_post`
> expanded under a chosen `Δx`. It allows unequal references and unequal scales.

Independently verified: 4,000 random cases (Face the Devil) and 120 general edge
cases (Skeptic 2), zero mismatches.

---

# 10. STUDY-1 EDGE SPECIALIZATION

```
E = q(x_s − x_d − q)
```

> **CLASSIFICATION: STUDY-1 SPECIALIZATION. PERMANENTLY.**
> **This must never be called "the EBU edge equation."**

**Every required assumption:**

1. Gaussian Level 1;
2. source and destination are the only changing **valued** coordinates;
3. `η = 1` (lossless);
4. no sink branch;
5. `x*_s = x*_d` (equal relevant references);
6. `σ_s = σ_d = 1` (unit scales).

Assumption 6 is a **numerical normalization**, not a physical fact. With a common
scale `σ` the STUDY-1 SPECIALIZATION reads `E = q(x_s − x_d − q)/σ²`; the
unit-scale form drops a factor that is not generally 1. Accidental agreement at an individual state
does not establish the identity generally.

**Four independent exact counterexamples outside its domain — all reproduced by
the Final Freeze-Closure Audit:**

| source | case | exact `E` | STUDY-1 SPECIALIZATION formula claims |
|---|---|---:|---:|
| Reconciliation Gate | `x=(5,3,4)`, `σ=(1,2,1)`, `A→B@1` | `5/8` | `1` |
| Reconciliation Gate | `x=(5,3,4)`, `x*=(4,6,4)`, `A→B@1` | `3` | `1` |
| Independent Skeptic 2 / Freeze Audit | `x=(6,4)`, refs `(0,0)`, scales `(2,1)`, `q=1` | `−25/8` | `1` |
| Independent Skeptic 2 / Freeze Audit | `x=(6,4)`, refs `(5,4)`, scales `(1,1)`, `q=1` | `0` | `1` |

Within its declared domain it is exact: 2,000 random cases and 576 executable
directed-transfer checks, zero mismatches.

---

# 11. CONSERVATION

**Physical carrier conservation is distinct from EBU accounting.**

```
lossless:     −q + q = 0
loss-aware:   −q + η q + (1−η) q = 0
```

Both are already implemented and hold **per physical carrier / resource**.
Loss-aware full-state conservation is **not** an optional future model; it is the
current declared model. Study-1 is its lossless special case.

Without a declared sink or boundary, the represented source-plus-destination
subsystem loses `(1−η)q`, which must cross a declared boundary. The
implementation forbids that case outright.

> **Do not sum dimensionally incompatible quantities without an explicit
> conversion law.** Conservation is stated per homogeneous carrier, or for
> appropriately converted conserved quantities.
>
> **`C + V = constant` is NOT carrier conservation and is not a physical
> conservation law.** See §17.

---

# 12. REFINEMENT / TELESCOPING

**General theorem, any state function `V`:**

```
E(x → x+Δ₁+Δ₂) = E(x → x+Δ₁) + E(x+Δ₁ → x+Δ₁+Δ₂)
```

This holds **solely** because `E` is a state-function difference. It requires no
demand-legality, provenance, attribution or service assumption. **Action
legality, provenance and service semantics are outside this theorem.**

**Same-base summation is a different construction and generally fails.** For
quadratic `V`, quoting both pieces from the *original* baseline:

```
E(x,Δ₁+Δ₂) − E(x,Δ₁) − E(x,Δ₂) = − Δ₁ᵀ H Δ₂
```

equivalently `E(x,Δ₁) + E(x,Δ₂) − E(x,Δ₁+Δ₂) = Δ₁ᵀ H Δ₂`. The two forms are the
same statement; both audits and the freeze audit agree on the sign.

**The practical consequence.** Splitting a unit transfer from equilibrium into
`m` equal fragments: updating the baseline gives total **`−1`** for every `m`;
quoting every fragment at the original equilibrium gives **`−1/m`**, which
approaches zero as refinement increases. Checked exactly for `m = 1, 2, 3, 7,
100`. **The same-base construction is the incorrect one.**

---

# 13. FACTOR POTENTIALS

For a declared factorization `V = Σ_α φ_α(x_{S_α})`:

- gradients add: `∇V = Σ_α ∇φ_α` (embedded);
- finite EBU remains the endpoint difference:
  `E = Σ_α [ φ_α(pre) − φ_α(post) ]`;
- unchanged factors cancel exactly; with `T = supp Δ`, a sufficient touched set
  is `{α : S_α ∩ T ≠ ∅}`;
- **a touched coupled factor must be reevaluated as a whole**, not truncated to a
  supposed independent contribution of the changed coordinate;
- the path identity holds per factor.

> **Coordinate separability is NOT required for `E = V_pre − V_post`.** A factor
> may itself be internally coupled and nonseparable. Verified on potentials
> containing explicit cross terms, and on coupled cubic and quartic factors:
> 80 coefficient-level chain-rule checks, 80 curved-path integral checks, 80
> touched-factor checks, 80 factor-gradient checks, plus an independent 400-case
> non-separable run — **zero mismatches**.

---

# 14. MÖBIUS / INTERACTION STRUCTURE

**Finite EBU exists before any interaction decomposition.** Möbius inversion
decomposes already-defined subset values:

```
v(G) = Σ_{S ⊆ G} I(S)
```

> **It creates no additional EBU. No interaction term is additional issuance.**

**Assumptions for the order bound:** quadratic `V` **and** fixed additive action
increments, with a defined value for every relevant subset. Then

```
v(S) = Σ_{a∈S} [ −μᵀΔ_a − ½ Δ_aᵀ H Δ_a ] − Σ_{{a,b} ⊆ S} Δ_aᵀ H Δ_b
```

so the highest possible nonzero interaction order is **two**, with
`I({a,b}) = −Δ_aᵀ H Δ_b`.

> **BOTH hypotheses are load-bearing; neither alone suffices.** Fixed additive
> increments do **not** by themselves imply order ≤ 2. Exact counterexample:
> `V(x) = x³`, baseline `x = 0`, three unit increments — the increments are
> fixed and additive, `V` is not quadratic, and the third-order Möbius term is
> **`I({a,b,c}) = −6 ≠ 0`**.

Verified: 1,120 reconstruction checks and 240 higher-order-zero checks
(Skeptic 2); an independent 200-group run measuring maximum nonzero order
exactly **2** with 0 failures (Reconciliation Gate).

> **The order bound does not automatically survive** if each subset resolves a
> different, nonadditive action vector. Physical application additionally
> requires the relevant subsets to be admissible; algebra cannot supply missing
> subset experiments.

---

# 15. SIMULTANEOUS GROUP CLOSURE

For `Δ_G = Σ_a Δ_a` with fixed additive increments, under the **declared
common-path convention**:

```
R_a = − ∫₀¹ ∇V(x + λ Δ_G)ᵀ Δ_a dλ
```

**Theorem (closure).** Summing inside the integral,

```
Σ_a R_a = − ∫₀¹ ∇V(x + λ Δ_G)ᵀ Δ_G dλ = V(x) − V(x + Δ_G) = E_G
```

by linearity and the fundamental theorem of calculus. **No Gaussian assumption
is used.** ∎

Gaussian specialization: `R_a = −μᵀΔ_a − ½ Δ_aᵀ H Δ_G`.

| part | classification |
|---|---|
| **TOTAL CLOSURE** | **DERIVED MATHEMATICAL THEOREM** |
| **INDIVIDUAL SPLIT** | **ATTRIBUTION CONVENTION** |

> **The individual split is not claimed to be physically unique.** Closure
> establishes arithmetic only. It is not causal identification, fairness, desert,
> ownership or a spending entitlement.

**Exactness does not imply uniqueness.** With `V = ½‖x‖²`, `x = (2,0,0)`,
`Δ_a = (−1,1,0)`, `Δ_b = (−1,0,1)`, total EBU is `1`, yet: common-path gives
`(1/2, 1/2)`; sequential with `a` first gives `(1, 0)`; sequential with `b` first
gives `(0, 1)`. All totals are exact. A claim that the common path was
*physically realized* requires a separate physical specification.

Closure verified over all Study-1 groups and over 80 nonquadratic, nonseparable
polynomial cases — zero mismatches.

---

# 16. QUADRATIC SHAPLEY RELATION

Define the **mathematical** subset game `v(S) = V(x) − V(x + Σ_{a∈S} Δ_a)`.

**Theorem.** For **quadratic `V`** and **fixed additive increments**, the
marginal contribution of `a` after subset `S` is
`−μᵀΔ_a − ½Δ_aᵀHΔ_a − Σ_{b∈S} Δ_aᵀHΔ_b`. Averaging over all permutations, each
other action precedes `a` with probability `1/2`, giving

```
Shapley_a = − μᵀ Δ_a − ½ Δ_aᵀ H Δ_G  =  R_a
```

— exactly the common-path formula. ∎

> **CLASSIFICATION: MATHEMATICAL EQUIVALENCE UNDER ADDITIONAL AXIOMS AND
> CONDITIONS. NOT A UNIQUE PHYSICAL OBSERVATION.**
> Every required subset value must be defined; a physical interpretation
> additionally requires the subsets to be admissible.

Verified: 120 complete permutation-average checks including nonseparable
quadratic Hessians (Skeptic 2); 300 independent random general-`σ`/`x*` cases
(Reconciliation Gate) — zero mismatches.

### It fails outside the quadratic class — two independent counterexamples

| potential | baseline | increments | common-path | Shapley | common total | Shapley total |
|---|---|---|---|---|---|---|
| `V(x) = x³` | `0` | `1, 2` | `(−9, −18)` | `(−10, −17)` | `−27` | `−27` |
| `V(x) = x⁴/4` | `0` | `1, 2` | `(−27/4, −27/2)` | `(−33/4, −12)` | `−81/4` | `−81/4` |

Both decompositions are exact and both close on `E_G`; they disagree
action-by-action. **The Shapley equivalence is a property of quadratic `V`, not
a general justification of the common-path convention.**

---

# 17. AGGREGATE ACCOUNTING

Considered **only after** the physical theory, and belonging to Layer 3.

**IF** `ΔC_total = E_t` at each step, and

- `θ` is fixed (one fixed potential, including fixed parameters);
- settlement closes exactly;
- state endpoints are consistent;
- no omitted external physical event occurs between endpoints;
- no external `C` source or sink and no separately charged burden exists;

**THEN** by telescoping

```
C_{t+1} + V(x_{t+1}) = C_t + V(x_t)      i.e.   C + V = constant
```

> **CLASSIFICATION: CONDITIONAL ACCOUNTING THEOREM.**
> It is **not** carrier conservation, **not** a thermodynamic law, and **not** a
> physical conservation law.
>
> **No assumption `C ≥ 0` is used, and none is permitted in this theorem.**
> `C` may be signed.

Verified: 100 fixed-field and 100 extended exact cases (Skeptic 2); an
independent 4,000-step random admissible walk on the live mechanism with **0
violations** (Reconciliation Gate); and, within Stage A, the identity
`B_total(t) = V(x₀) − V(x_t)` at all 2,618 A1 checks.

### External events and changing fields — the identity acquires explicit terms

If an external event changes `(x_t, θ_t)` to `(y_t, θ'_t)`, the action then
reaches `x_{t+1}`, and an external accounting entry contributes `J_t`, then with
actor EBU evaluated at `θ'_t`:

```
(C_{t+1} + V_{θ'_t}(x_{t+1})) − (C_t + V_{θ_t}(x_t))
      = V_{θ'_t}(y_t) − V_{θ_t}(x_t) + J_t
```

**That right-hand side generally does not vanish and must be recorded.** If the
field changes *during* an action, its parameter-derivative contribution likewise
cannot be silently omitted. Every fixed-field statement in this document is
conditional on `θ` being fixed.

---

# 18. PER-ACTOR / PER-OWNER ACCOUNTS

> **`c_i` is presently a HISTORICAL ATTRIBUTION OBJECT.**
> It is **not** generally a state function of the current physical state `x`.

**Closed-loop construction.** At reference `(4,4,4)`, assigning each action's
receipt to its source owner:

| step | state after | `E` | attributed to |
|---|---|---:|---|
| `B→C@1` | `(4,3,5)` | `−1` | `B` |
| `C→B@1` | `(4,4,4)` | `+1` | `C` |

The physical state returns **exactly**. Aggregate change is **zero**. The owner
vector changes by **`(0, −1, +1)`**. No borrowing, no account constraint and no
economic assumption enters this construction.

An exhaustive search over **576** directed two-action reverse-transfer loops
found **528** with nonzero owner redistribution.

**Structurally:** `Σ_i ω_i = −dV` is exact, so aggregate `C` is a state-function
difference. The individual `ω_i` **need not be closed**, so the owner vector is
in general a genuine path integral. **Aggregate cycle closure does not imply
owner-by-owner cycle closure** — that implication is what the loop above refutes.

> **QUANTIFIER — stated exactly.** What is proved is an existence result: there
> exists a closed physical loop with **aggregate change `0`** and **nonzero owner
> redistribution**. Therefore per-owner historical attribution is **not
> guaranteed** to be a state function of `x`.
>
> **DO NOT STATE** that every possible individual attribution convention is
> necessarily non-exact or non-closed. That stronger universal claim is **not**
> established here, and nothing in this document requires it.

> **This is expected for historical attribution, and it does NOT imply debt,
> insolvency, privilege, action prohibition or affordability.**
> At the physical-foundation level, **`c_i` may be signed.**

---

# 19. FORBIDDEN FOUNDATION BACKFLOW

The following must **NOT** enter Layers 1–3 unless a future physical derivation
independently establishes them:

```
c_i >= 0                       B_i >= 0
pre-action affordability       no borrowing
no pooling                     complete-service requirement
persistent economic orders     no partial service
FIFO                           backlog
price                          actor utility
welfare                        privilege
service priority
```

All three independent audits classify every one of these as **NOT DERIVED FROM
PHYSICS** / **NOT REQUIRED** by any audited foundational identity.

> They may be studied **only** as external actor / institutional hypotheses at
> Layers 4–5. **They may never modify `V`, `μ`, `E`, `f`, conservation or
> attribution backwards.** In particular, no economic desirability argument is a
> proof criterion anywhere in this document.

---

# 20. STAGE-A CLASSIFICATION

**Stage A is not rerun, not altered, and not reinterpreted numerically.** All
recorded numerical findings remain exactly as published. Only the *foundational
classification* is stated here. Refer to the published scientific-record archive
(`docs/scientific_record/stage_a/`) for the full reports.

| episode | foundational classification |
|---|---|
| **A1** | historical **Layer-4** actor/policy study. Fixture-specific behavioural evidence. |
| **A2** | historical demonstration that the **V1 institutional affordability gate changes execution**. This is **Layer 5**. It is **NOT** evidence that affordability is a physical EBU law. |
| **A3** | historical lifecycle result **conditional on its declared service semantics**. |

Stage-A disposition, unchanged: **STAGE A SCIENTIFICALLY ACCEPTED WITH BOUNDED
CLAIMS**, with all fifteen carried qualifications attached. Stage A's gate chain
was Gates 1–4 CONDITIONAL PASS, then Gate 5 acceptance.

Two Stage-A facts bear directly on how this foundation must be read:

- The physical fact underlying A2 — that at `μ = 0` every nonzero finite
  displacement in positively valued coordinates has `E = −½ΔᵀHΔ < 0` — is §5 of
  this document and stands on its own **without** A2. A2 is evidence about an
  institutional rule, not about the physics.
- In A3 **the affordability gate never bound**: every candidate plan was
  affordable in all 256 episodes. A3 exercises the lifecycle, not the gate.

> **RECORDED HISTORICAL DISCREPANCY — NOT a reconciled compatibility.**

`CROSS_REPORT_NOTES.md` Discrepancy 1 preserves two historical formulations
about A3 reserve dependence:

- **Gate 4** supplied a concrete arithmetic counterexample to the universal
  claim that A3 service necessarily depends on positive previously earned
  reserve (`A3|ebu_random|k=10`, arrival `(5,4,3)`, plan `B→C@1`, receipt to
  `B` of `0`).
- **Gate 5** later described that same universal claim — *"all A3 service
  necessarily requires positive previously earned reserve"* — as **NOT TESTED
  — neither ruled in nor out**.

**These two formulations are not logically identical, and this document does not
present them as compatible.** A concrete counterexample to a universal claim
rules that universal claim out *within the stated observed domain*. That a
universal claim was refuted by arithmetic on recorded data, and that no
preregistered arm contrast tested reserve dependence, are **two different
issues**; the absence of a registered contrast does not convert a refuted
universal into an untested one.

**Both historical reports stand unaltered**, and the archival note records the
disagreement rather than resolving it. This document's role is to **flag the
discrepancy**, not to adjudicate it, and it adds no inferential claim beyond
what the recorded evidence supports. The underlying question is Layer 4/5, not
foundational: nothing in Layers 1–3 depends on its resolution.

---

# 21. ENTROPY-DEFICIT BOUNDARY

**No claim of physical entropy is made. Only compatibility is recorded.**

**Assumptions, stated in full.** At fixed `θ`, with `S_eq(θ)` **spatially
constant** and `κ` **constant and nonzero**:

```
S_θ(x) = S_eq(θ) − κ V_θ(x)
```

Then

```
∇S = − κ μ            ΔS / κ = V_pre − V_post = E
```

For the intended **entropy-deficit orientation**, `κ > 0`.

> **CLASSIFICATION: MATHEMATICALLY COMPATIBLE. PHYSICALLY UNPROVED.**

Verified as an exact algebraic identity (500 exact-rational cases, zero
mismatches). It is an affine change of variable and adds no physical content.

> **Variable `κ` or spatially varying `S_eq` introduces extra derivative terms**
> and the relation above no longer holds as written. The constancy assumptions
> are load-bearing.

> **CIRCULAR PROOF EXPLICITLY FORBIDDEN.** Choosing or defining a normalizable
> distribution proportional to `exp(−V)` does **not** independently establish
> that `V` is a physical entropy or rate function. That would define the ensemble
> from the potential and then present the potential as a consequence of the
> ensemble.

**Still required before any entropy interpretation may be claimed:** an
independent measurement or derivation of `S` not defined through `V`; physical
identification of `κ` with units; evidence that `S_eq(θ)` is a genuine
equilibrium entropy; and a statistical ensemble in which `V` is independently the
large-deviation rate function.

---

# 22. STATUS OF `κ`

> **`κ` is NOT assumed equal to the Boltzmann constant.**
> **`κ` is NOT assumed equal to 1.**
> **`κ` is NOT assumed universal.**

**All four possibilities remain open, and none is presently established:**

| | possibility |
|---|---|
| **A** | `κ` is only a normalization / unit conversion, with no independent physical content |
| **B** | `κ` is system-specific |
| **C** | `κ` depends on `θ` |
| **D** | one universal physical `κ` exists |

### Normalized freedom — conditional definition only

**IF** the entropy-deficit relation of §21 holds with **constant positive `κ`**,
define `F = S/κ`. Then

```
F = F_eq − V              ΔF = E
```

> **The normalized relation does not require knowing the numerical value of
> `κ`.** That is a genuine simplification.
>
> **But the physical interpretation of `F` still depends entirely on
> independently establishing the entropy / rate-function relation of §21.**
> Until then `F` is a rescaled restatement of `−V`, not an established physical
> coordinate.

---

# 23. OPEN PHYSICAL QUESTIONS

Foundational only. **None is answered in this document**, and none blocks
freezing a clearly conditional mathematical core.

1. Why does `V` have its physical form?
2. Is Gaussian `V` exact, near-equilibrium, a Level-1 approximation, or a
   rate-function approximation?
3. What is the independently measurable physical meaning of `σ`?
4. Is `σ` related to covariance, susceptibility or a fluctuation scale?
5. How does `θ` evolve?
6. How should physically represented environment / loss be valued — inside `V`
   or audit-only? §7 shows the local force law depends on this declaration.
7. Does an independently measurable entropy / rate function satisfy
   `S_eq − S ∝ V`?
8. Does `κ` physically exist as an identifiable constant?
9. If yes: system-specific, `θ`-dependent, or universal?
10. Is normalized freedom `F = S/κ` a genuine physical coordinate?
11. Does `E = ΔF` survive moving-field decomposition?
12. Why, if at all, would an actor locally maximize its own freedom
    contribution?

**No economic question belongs on this list.**

---

# 24. NEXT PROGRAMME ROADMAP

| gate | name | question |
|---|---|---|
| **P1** | ENTROPY / RATE-FUNCTION FOUNDATION | Is there an independently derived or measured physical quantity such that `S_eq − S = κ V`? |
| **P2** | `κ` EXISTENCE / IDENTIFIABILITY | Is `κ` physically identifiable, or merely normalization freedom? |
| **P3** | `κ` UNIVERSALITY | *Only if P2 establishes identifiability.* Is the same `κ` valid across fields and systems? |
| **P4** | FREEDOM / CONTRIBUTION | Does `E = ΔF` define a permanent normalized actor contribution under **changing** fields? |
| **P5** | NATURAL INCENTIVE | Why would an actor maximize its freedom contribution? |

**P5 must not assume its answer.** The task is to derive whether local freedom
contribution corresponds to future physical option volume, reachable-set
freedom, survivability, another physical possibility measure, **or nothing**.
"Nothing" is a permitted outcome.

**ONLY AFTER P1–P5: UNGATED STAGE B**, with **signed `c_i`** and **no artificial
`c_i ≥ 0` boundary**. Institutional gate experiments occur only later, and only
if the ungated physical model shows they are scientifically needed.

---

# 25. CANONICAL EQUATION TABLE

| equation / statement | layer | assumptions | kind | status | exact verification evidence | forbidden overstatement |
|---|---|---|---|---|---|---|
| `V(x;θ)` general | 2 | declared potential, sufficient regularity | general declaration | **constitutive hypothesis** | — | "derived physical law" |
| `V = ½Σ((x_i−x*_i)/σ_i)²` | 2 | declared references, positive scales | **specialization** of "some `V`" | **CONSTITUTIVE PHYSICAL / FIELD HYPOTHESIS** | 720 general cases | "universal physical law"; "exactness proves physical validity" |
| `μ = ∇_x V` | 2 | differentiable `V` | general | mathematical **definition** | 720 independent cases | — |
| **`E = V_pre − V_post`** | 2 | state function, fixed `θ` | **GENERAL — TOP OF HIERARCHY** | **definition** of finite EBU | endpoint evaluation; saved-record agreement | **"an edge polynomial defines EBU"**; "conservation forces this definition" |
| `E = −∫_γ ∇V·dx` | 2 | single-valued **`C¹`**, fixed `θ`, admissible piecewise-smooth `γ` in domain | general | **derived theorem** | 80 polynomial coefficient/integral cases; 600 curved-path cases | "differentiable alone suffices"; confusing with attribution-path dependence |
| `f = −∇Vᵀ dx/dq` | 2 | differentiable action path | general | **derived theorem** | 120 + 360 checks | **`f` establishes a law of motion**; "`f` is a measured mechanical force" |
| `μ = H(x−x*)`, `E = −μᵀΔ − ½ΔᵀHΔ` | 2 | fixed quadratic `V` | **EXACT GAUSSIAN FINITE THEOREM** | derived theorem, **two derivations** | 4,000 + 720 + 3,662 + 5,734 + 66,396; **0 mismatches** | "this is the definition of EBU" |
| `E` first-order vs finite; `E = −½ΔᵀHΔ` at `μ=0` | 2 | quadratic `V`; **positively valued coordinates** | corollary | derived theorem, **scoped** | 60/60 Study-1 displacements; `audit_sink_world` gives `E=0` | **"every nonzero increment gives `E<0`"** (false with zero-curvature directions); "the derivative gives the finite value" |
| `f_e = μ_s − η μ_d` | 2 | `dx/dq=(−1,η,1−η)`, lossy route with an **audit-only** sink, so **`μ_sink = 0`** | **CONDITIONAL COROLLARY** | derived theorem | 120 + 360 loss-aware checks | "valid for a valued sink"; **"`η=1` implies `μ_sink=0`"** — the sink term vanishes when `(1−η) μ_sink = 0`, which `η=1` and `μ_sink=0` satisfy **independently**; replacing `f = −∇Vᵀdx/dq` |
| `f_e = μ_s − η μ_d − (1−η)μ_sink` | 2 | sink **inside** `V` | **CONDITIONAL COROLLARY** | derived theorem | worked example `1/2` vs `3/2`; `E(q)/q = 1/2 − ¾q` | "a new model extension"; "a loss-aware experimental result" |
| valued sink ⇒ sign of whole action | 2 | — | — | **statement corrected** | `loss_world` `(20,0,10,0)`, `η=1/2`: **`E = 57/4 > 0`** | **"a valued sink makes a lossy plan cost EBU"** |
| two-coordinate `q`-polynomial | 2 | Gaussian, lossless, `s`/`d` only | **CONDITIONAL GAUSSIAN TWO-COORDINATE COROLLARY** | derived theorem | 4,000 + 120 cases | "the general EBU edge equation" |
| `E = q(x_s − x_d − q)` | 2 | the six assumptions of §10 | **STUDY-1 SPECIALIZATION** | derived theorem | 2,000 + 576 checks; **4 counterexamples outside domain** | **"the EBU edge equation"** |
| sequential refinement / telescoping | 2 | `V` a state function | general | **derived theorem** | all Study-1 groups; 720 cases | requiring legality/provenance; confusing with same-base summation |
| same-base cross term `−Δ₁ᵀHΔ₂` | 2 | quadratic `V`, common base | corollary | derived theorem | explicit subdivisions `m=1,2,3,7,100` | "same-base sums give the joint value" |
| carrier conservation | **1** | declared increments; sink present when `η<1` | general in current model | **physical law of the declared state** | 3,662 lossless + 120 loss-aware; increment sums `=0` | calling `C+V` conservation; summing unlike carriers |
| factor potential identities | 2 | declared differentiable factors | corollary | derived theorem | 4 × 80 checks + 400 non-separable | "separability is required for `E`"; truncating a coupled factor |
| Möbius decomposition; order ≤ 2 | 2 | defined subset values; **quadratic `V` AND fixed additive increments** — both are required for the order bound | corollary | derived theorem | 1,120 + 240 checks; max order **2** | "interactions are extra issuance"; **assuming the bound from additive increments alone** — `V(x)=x³`, baseline `0`, three unit increments has fixed additive increments and a nonzero **third**-order term `I = −6` |
| `Σ_a R_a = E_G` | 3 | fixed increments summing to `Δ_G`; declared common path | general | **derived theorem (closure)** | all 3,662 groups; 80 nonquadratic cases | "closure proves unique attribution / fairness / ownership" |
| `R_a = −μᵀΔ_a − ½Δ_aᵀHΔ_G` | 3 | Gaussian `V` | corollary | **ATTRIBUTION CONVENTION** | all Study-1 groups | **the common-path split is physically unique**; "the common path was physically realized" |
| common-path `=` Shapley | 3 | **quadratic `V`**, fixed additive increments, all subset values defined | corollary | **equivalence under additional axioms** | 120 + 300 checks | "general"; "unique physical observation" — fails for `V=x³` and `V=x⁴/4` |
| `C + V = constant` | 3 | §17 list, fixed `θ` | conditional | **CONDITIONAL ACCOUNTING THEOREM** | 100 + 100 exact; 4,000-step walk; 2,618 A1 checks | **physical conservation**; thermodynamic law; any sign constraint on `C` |
| historical `c_i`, path dependence | 3 | declared source assignment | — | **HISTORICAL ATTRIBUTION OBJECT** | 576 loops, 528 redistributions; `(0,−1,+1)` | "`c_i` is a state function of `x`"; inferring debt/insolvency/prohibition |
| `S = S_eq − κV` ⇒ `∇S = −κμ`, `ΔS/κ = E` | 2/open | fixed `θ`, **`S_eq` spatially constant**, **`κ` constant ≠ 0**, `κ>0` for deficit orientation | conditional | **MATHEMATICALLY COMPATIBLE, PHYSICALLY UNPROVED** | 500 exact cases | **physical entropy established**; `P ∝ exp(−V)` as proof |
| `κ` | open | — | — | **UNDETERMINED — A/B/C/D all open** | — | `κ = k_B`; `κ = 1`; "`κ` is universal" |
| `F = S/κ`, `ΔF = E` | open | §21 holds with constant `κ > 0` | conditional | **conditional definition only** | — | "`F` is an established physical coordinate" |
| `c_i ≥ 0`, affordability, borrowing, pooling, complete service, persistent orders, no partial service, FIFO, backlog, price, utility, welfare, privilege, service priority | **5** | — | — | **NOT DERIVED FROM PHYSICS / NOT REQUIRED** | — | **any appearance in Layers 1–3**; any backward modification of `V`, `μ`, `E`, `f` or conservation |

---

# 26. EVIDENCE PROVENANCE AND ITS LIMITATIONS

Recorded so that the strength of each source is visible rather than implied.

**Locally transcript-authenticated (7 required + 1 optional).** Gates 1, 2, 3, 5;
Face the Devil; Reconciliation Gate; Final Freeze-Closure Audit; and the optional
publication verification. Each sidecar names the session, line index, message
uuid and authoring timestamp.

**External project conversation record, byte-fixed but NOT locally
authenticated (3).** `STAGE_A_GATE_4_ADVERSARIAL_INTERPRETATION.md`,
`FOUNDATION_INDEPENDENT_SKEPTIC_2.md`, `FOUNDATION_INDEPENDENT_FREEZE_AUDIT.md`.
Their original transcript source and authoring timestamps were not
independently authenticated by the local environment. **This is a provenance
distinction only and implies nothing about their scientific content or rigour.**

**Authorship / recovery-independence limitation.**
`FOUNDATION_FINAL_FREEZE_CLOSURE_AUDIT.md` was authored in the same session that
later performed the record recovery and its self-checks. Byte provenance is
sound; recovery/self-check independence is **limited**. A reviewer wanting
independent assurance on that report specifically should obtain it elsewhere.

**Documentary blockers now closed.** The Final Freeze-Closure Audit left two
open: (i) Gates 1–5 absent from the repository, and (ii) the reconciliation text
having no immutable repository identity. **Both are closed by commit
`4817538955…`**, which contains all five Stage-A gates and the reconciliation
with byte-verified hashes. No foundational blocker was ever recorded.

---

# 27. THEORY-DRIFT SELF-AUDIT OF THIS DOCUMENT

| check | result |
|---|---|
| `E = V_pre − V_post` replaced by an edge polynomial | **No.** §3 places it at the top; §6 forbids definition by polynomial; §9 and §10 sit below and are labelled. |
| new physical coordinate introduced | **No.** The sink pre-exists in `world.py` / `physical.py`; §7 states this and cites the refusal of `η<1` without a sink. |
| meaning of `η` changed | **No.** `η` remains a physical transfer property of a route, at Layer 1. |
| canonical force law modified | **No.** `f = −∇Vᵀ dx/dq` is general; both edge forms are labelled CONDITIONAL COROLLARY. |
| attribution promoted into physics | **No.** §15 splits closure (theorem) from the split (convention); §16 is quadratic-only with two counterexamples. |
| accounting promoted into conservation | **No.** §17 is labelled a conditional accounting theorem; §11 states explicitly that `C + V` is not a physical conservation law. |
| institutional rules promoted into EBU | **No.** §19 holds the entire list at Layer 5. |
| economics inferred from desired behaviour | **No.** No economic desirability is used as a proof criterion anywhere. |
| every `q(x_s − x_d − q)` marked | **Yes** — §10 heading, table row, and every in-text occurrence carry "STUDY-1 SPECIALIZATION". |
| every Gaussian two-coordinate `q`-polynomial marked | **Yes** — §9 and the table row carry "CONDITIONAL GAUSSIAN TWO-COORDINATE COROLLARY". |
| `κ = k_B` asserted | **No** — §22 explicitly denies it. |
| physical entropy asserted as established | **No** — §21 is "MATHEMATICALLY COMPATIBLE, PHYSICALLY UNPROVED". |
| common-path split asserted physically unique | **No** — §15 denies it and supplies a three-way non-uniqueness example. |
| `C + V` asserted as physical conservation | **No** — denied in §11 and §17. |
| `f` asserted to generate motion | **No** — §3 attaches the explicit caution. |
| strict negativity at `μ=0` left unscoped | **No** — §5 scopes it and supplies the `E = 0` counterexample. |
| valued-loss overbroad wording repeated | **No** — §8 states the scoped form, supplies `E = 57/4`, and records the `valuation.py` divergence without editing it. |
| `S_eq` constancy left implicit | **No** — §21 states it explicitly as load-bearing. |

---

**END OF CANONICAL FREEZE CANDIDATE.**

This document is **not frozen**. The next step is an independent file-level
freeze audit of this file and its `.meta.json` sidecar.
