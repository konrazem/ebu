All computations complete. Here is the audit.

---

# EBU PHYSICAL FOUNDATION — FACE THE DEVIL

**Mechanism verified:** `demand_driven_ebu` = `f4e31a2a…3eec48`, matching the published Stage-A identity exactly. All work read-only.

## 1–2. THE PHYSICAL CORE, RE-DERIVED TWICE

**Symbols audited.** `x ∈ ℝⁿ` physical state [material]; `V(x;θ)` burden — **dimensionless**, because `σ` carries the material units; `μ = ∇ₓV`, units `1/[M]`; `E` dimensionless. Every product below is dimensionally consistent.

> **PROOF A (expansion).** `V(x+Δ) = ½Σ(1/σᵢ²)[(xᵢ−x*ᵢ) + Δᵢ]² = V(x) + μᵀΔ + ½ΔᵀHΔ`, so
> **`E = V(x) − V(x+Δ) = −μᵀΔ − ½ΔᵀHΔ`**, `H = diag(1/σᵢ²)`.

> **PROOF B (line integral).** `E = −∫₀¹∇V(x+λΔ)ᵀΔ dλ = −∫₀¹[(x−x*)ᵀHΔ + λΔᵀHΔ]dλ = −μᵀΔ − ½ΔᵀHΔ`. **Identical.** ∎

**Independent verification.** 4,000 random cases with **general** `σ`, `x*`, dimension 2–5, exact `Fraction`: A = B = direct `V_pre−V_post` with **0 disagreements**. Exhaustive over the whole Study-1 domain — **3,662 feasible (state, group) pairs, 0 mismatches**, checked against the mechanism's own `value_group`.

## 3. EDGE ACTION — GENERAL, THEN SPECIALIZED

> **General lossless `s→d`, quantity `q`:**
> ```
> E = q[(x_s − x*_s)/σ_s² − (x_d − x*_d)/σ_d²] − ½q²(1/σ_s² + 1/σ_d²)
> ```
> Verified: 4,000 random general edges, **0 disagreements**.

> **Specialization.** `E = q(x_s − x_d − q)` requires **BOTH** `σ_s = σ_d = 1` **AND** `x*_s = x*_d`. Verified 2,000 cases, 0 disagreements — and it **fails** when either hypothesis is dropped: with `σ=(1,2,1)` the exact value is `5/8` against the formula's `1`; with `x*=(4,6,4)` it is `3` against `1`.

> **This formula is a SPECIALIZATION, not the universal EBU equation.** It is valid for Study-1 only because `σ=(1,1,1)` and `x*=(4,4,4)`.

## 4. MARGINAL / FORCE EQUATION

Infinitesimal transfer with efficiency `η` gives `dx = −dq·e_s + η dq·e_d`, hence

```
dV/dq = η μ_d − μ_s        and        −dV/dq = μ_s − η μ_d = f_e
```

Numerically confirmed (`η=1`: numeric `−3599/1600` → analytic `−9/4`; `η=3/4`: `−279927/128000` → `−35/16`). **The calculus confirms the historical sign**: EBU's driving force is `−dV/dq`, i.e. EBU rises as burden falls. `η` sits on the **destination** marginal, because only `η·dq` arrives.

## 5. FINITE vs DIFFERENTIAL — THE FOUNDATIONAL DISTINCTION

```
local marginal:  −μᵀΔ            exact finite:  −μᵀΔ − ½ΔᵀHΔ
correction:      −½ΔᵀHΔ  ≤ 0     (strict for Δ ≠ 0, H positive definite)
```

**The first-order estimate always overstates EBU.** Decisive example: **at `x = x*`, `μ = 0`, so the derivative reports exactly 0 for *every* action, while the exact finite value is strictly negative** — `B→C@1` gives `−1`, `B→C@2` gives `−4`. This is precisely the Stage-A A2 result, and it is a second-order effect invisible to the gradient. Limit check: `exact/linear → 1` as `q → 0` (ratios `2, 3/2, 11/10` for `q = 1, ½, 1/10`); the correction is `O(q²)`.

## 6. COMMON-PATH SIMULTANEOUS RECEIPTS

> **Theorem (exactness, any `V`).** `Σ_a R_a = −∫₀¹∇V(x+λΔ_G)ᵀ(Σ_aΔ_a)dλ = −∫₀¹∇V(x+λΔ_G)ᵀΔ_G dλ = V(x) − V(x+Δ_G)`. This is the fundamental theorem of calculus along the segment; it needs **no** Gaussian assumption. ∎

> **Gaussian specialization:** `R_a = −μᵀΔ_a − ½Δ_GᵀHΔ_a`. With `H = I` this is exactly `r_i = −(x−x*)·δ_i − ½δ_G·δ_i`. **Confirmed: the recently derived Study-1 formula is precisely the `H=I` specialization.**

**Independent exhaustive verification:** over all 3,662 feasible Study-1 pairs, `Σ receipts = E_G` with **0 failures**, and every individual receipt matches the closed form with **0 mismatches**.

## 7. WHAT ARE RECEIPTS PHYSICALLY? — **ANSWER: C**

Five *distinct* exact decompositions of the same `E_G = 3` at `x=(6,4,2)`:

| decomposition | value |
|---|---|
| common-path (implemented) | `(1, 2)` |
| sequential, action 0 then 1 | `(0, 3)` |
| sequential, action 1 then 0 | `(2, 1)` |
| Shapley (mean over orders) | `(1, 2)` |
| proportional to `‖Δ_a‖²` | `(12/5, 3/5)` |

All sum to `E_G`. **Attribution is not unique, and actor ownership is not a law of physics.**

**But one upgrade is earned.** For a *simultaneous* group there is no intermediate physical state, so no path is observable — yet:

> **Theorem (Shapley equivalence).** For quadratic `V`, the common-path receipt **is exactly the Shapley value** of the coalition game `v(S) = E(Σ_{a∈S}Δ_a)`.
> *Proof.* `v(S) = −Σ_{a∈S}μᵀΔ_a − ½Σ_{a∈S}Δ_aᵀHΔ_a − Σ_{{a,b}⊆S}Δ_aᵀHΔ_b`. Shapley gives each additive and own-quadratic term wholly to its action and splits each pair term equally: `Sh_a = −μᵀΔ_a − ½Δ_aᵀHΔ_a − ½Σ_{b≠a}Δ_aᵀHΔ_b = −μᵀΔ_a − ½Δ_aᵀHΔ_G`. ∎
> Verified: 300 random general-`σ`, general-`x*` cases, **0 disagreements**.

**Classification: B/C — mathematically canonical under an axiomatic selection (efficiency, symmetry, linearity, null-action), one exact decomposition among many, not physically observable.** It is an **ACCOUNTING / ATTRIBUTION CONVENTION with an axiomatic justification**, not a physical law.

## 8. ATOMIC REFINEMENT

> **Theorem (telescoping, any `V`).** `E(x→x+Δ₁+Δ₂) = E(x→x+Δ₁) + E(x+Δ₁→x+Δ₁+Δ₂)`, because `E` is a difference of a state function. ∎ Verified: 0 failures over the Study-1 domain.

> **The crux, which must never be confused again.** *Sequential* evaluation telescopes; *parallel* evaluation at a common base does **not**. At `x=(5,3,4)`: joint `E = 0`, sequential sum `= 0`, **parallel-at-`x` sum `= −1`**, discrepancy exactly the cross term `−Δ₁ᵀHΔ₂ = +1`.

**Classification.** Telescoping is **MATHEMATICAL** and unconditional. Action legality, P-provenance and service semantics are **MODELLING ASSUMPTIONS** and contaminate nothing: the refinement theorem holds whether or not the halves are legal.

## 9. CONSERVATION

Lossless: `Σᵢ Δᵢ = −q + q = 0` ⇒ `Σᵢxᵢ` constant. Verified: 0 violations over 3,662 pairs.
`η < 1`: `Σᵢ Δᵢ = −(1−η)q < 0`. **This is represented-stock loss, not a conservation violation**, provided a sink coordinate carries `+(1−η)q`; the full-state law `Σ_stocks + Σ_sinks = const` then holds exactly. A true violation would be unaccounted loss with no sink coordinate.

## 10. FACTOR POTENTIALS

For `V = Σ_α φ_α(x_{S_α})`: `∇V = Σ_α ∇φ_α`; `E = Σ_α [φ_α(pre) − φ_α(post)]`; untouched factors contribute exactly 0; the path identity holds per factor. Verified on a **deliberately non-separable** `V` containing the cross term `x₀x₁/2`: **0 mismatches in 400 cases, 0 untouched-factor violations.**

> **Separability is NOT required for `E = V_pre − V_post`** (that is unconditional). It is required only to *attribute* `E` to factors.

## 11. MÖBIUS / INTERACTION TERMS

> **Theorem.** The Möbius transform of `S ↦ E(Δ_S)` reproduces `E` exactly and **creates no value**: `Σ_S m(S) = E(full set)`. For quadratic `V` it **terminates at order 2**, with `m({a}) = E(Δ_a)` and `m({a,b}) = −Δ_aᵀHΔ_b`.

Verified on a 4-action group: order-1 `(1,−3,1,−3)`, order-2 `(2,1,−1,−1,1,2)`, **order-3 all exactly 0, order-4 exactly 0**, sum `= 0 = E(full set)`. The expected distinction is **confirmed**: total finite EBU is already `V_pre − V_post`; Möbius only exposes interaction structure.

## 12. FIXED-FIELD CAPACITY IDENTITY

> **Theorem.** If `ΔC_total = E_t` each step, then `C_T = C_0 + Σ_t[V(x_t) − V(x_{t+1})] = C_0 + V(x_0) − V(x_T)`, hence **`C_t + V(x_t) = C_0 + V(x_0) = const`.** Under a normalization `W = aV + b` (`a>0`) the invariant is `C + aV`. ∎

**Every assumption required:** (i) exact settlement, `Σ receipts = E_t` with zero residual; (ii) **fixed field** `θ` throughout; (iii) actor-only evolution — no exogenous change to `x` outside the accounting; (iv) no other source or sink of `C`; (v) `V` evaluated on one connected reachable component.

**This is an ACCOUNTING THEOREM, not physics.** It follows from telescoping plus the *definition* `ΔC = E`. It says nothing about whether `C` is physical. **Aggregate identity ≠ per-owner vector** (§13). No use is made of `C_i ≥ 0`, no-borrowing, no-pooling or affordability, and none is needed.

## 13. PER-OWNER PATH DEPENDENCE — VERIFIED TWO WAYS

> **PROOF A (analytic).** Closed loop `x* → (4,3,5) → x*` by `B→C@1` then `C→B@1`: returns to start, **aggregate = 0**, **owner vector `{B: −1, C: +1}`**. Generally, for any 2-loop through states of unequal `V`, the owner vector is `(Δ, −Δ)` with `Δ = V(x)−V(y) ≠ 0`.
> **PROOF B (exhaustive).** Over all service-plus-restoration cycles `x* → x*`, the net owner vector takes **18 distinct values for destination A, 18 for C, 9 for B**, including net-zero.

> **Exact statement.** `Σ_i ω_i = −dV` is an **exact** 1-form, so aggregate `C` is a state function. The individual `ω_i = −∇V·δ_i` is **not closed**, so the owner vector is a genuine path integral.

**Does this invalidate the actor account?** **No.** It shows the account is a *history object by construction* — expected, since an attribution is not a state function. It invalidates only the claim that owner balances are determined by physical state. **Classification: ACCOUNTING / ATTRIBUTION CONVENTION.**

## 14. HARD AFFORDABILITY GATE — NOT DERIVABLE

> **Can `B_i + r_i ≥ 0` be derived from `V`, `μ`, `E`, conservation, telescoping? NO.** The physical core never references `B`. `B` is a Layer-3 accounting object; a constraint on it cannot follow from Layers 1–2. ∎

| rule | classification |
|---|---|
| `B_i + r_i ≥ 0` before execution | **INSTITUTIONAL RULE / historical V1 design assumption**, operationalized as an experimental mechanism |
| `B_i ≥ 0` | same — a *consequence* of the gate given zero opening balances, not an independent physical law |
| no borrowing | **ECONOMIC ASSUMPTION** |
| no pooling | **ECONOMIC ASSUMPTION** |

Not defended because Stage A used it; not rejected because it caused inconvenience. It is simply not physics.

## 15. E-DEMAND — STRIPPED

**Minimum physical content:** a specification of a desired physical consequence — a target increment or target region. Nothing more.

| element | classification |
|---|---|
| destination | **PHYSICAL** (a coordinate) |
| persistent held order | **SERVICE CONTRACT** |
| additive orders | **SERVICE CONTRACT** |
| complete-service requirement | **SERVICE CONTRACT** |
| no partial service | **SERVICE CONTRACT** |
| deadline, priority, FIFO, backlog | **SERVICE CONTRACT / SCHEDULER** (none in the current model except persistence) |

> **Decomposition of `LEAF_BACKLOG_ABSORBED`.** It requires: (a) one action per route per plan — *harness assumption*; (b) quanta `{1,2}` — *domain assumption*; (c) leaf topology, one inbound route — **physical/topological**; (d) complete-service; (e) additivity; (f) persistence with no discard; (g) no partial service — **all service contract**.
>
> **Answer: `LEAF_BACKLOG_ABSORBED` is a theorem of a particular SERVICE CONTRACT layered on EBU physics, NOT a theorem of EBU physics.** Physics contributes only the topology. **I must correct my own prior packet**, which called it "structural, policy-independent" — accurate as to *policy* independence, but it invited reading as physical. It is not.

## 16. RELABELLING THE RECENT "CONTINUITY" THEOREMS

| theorem | corrected label |
|---|---|
| Closed capacity budget `C + W = I` | **ACCOUNTING THEOREM** (assumptions in §12) |
| Owner-capacity blocking | **CONDITIONAL ON V1 GATE** — vanishes without the gate |
| `p_B` idealized drift `2p_B − 1` | **ACCOUNTING THEOREM, conditional on gate + service semantics + minimal-cycle class** |
| `p_B` general failure (18 vectors) | **ACCOUNTING THEOREM** — a true statement about attribution path dependence |
| Leaf backlog absorption | **CONDITIONAL ON SERVICE SEMANTICS** (§15) |
| Continuity vs survival | **CONDITIONAL ON V1 GATE + SERVICE SEMANTICS + EXPERIMENTAL HARNESS** |

None is discarded; none is physics.

## 17. CIRCULARITY AUDIT

| site | finding |
|---|---|
| Affordability gate | Introduced so capacity would *do* something, then tested. **The record keeps it honest** — Stage A's preregistration declares it an arm property, never a physical law. No violation, but the *vocabulary* ("capacity", "afford", "pay", "earn") imports economic connotation into Layer 3 and should be read as accounting terms. |
| Complete-service → atomic P (finding F-7) | The rule was changed **after** enumeration showed 36 absorbing states. Justified on *ontological* grounds (the P residual lives in the state), not on economic desirability. **Defensible, but borderline** — it is a model change prompted by model behaviour, and it should be recorded as such. |
| **My own prior Stage-B design packet** | I proposed choosing displacement amplitude and `p_B` levels partly so the gate would be *exercised*. That is "desired mechanism activity → parameter choice". I flagged it at the time; **I restate it here as a genuine near-violation of the pipeline** and it should not survive into any preregistration. |

No instance was found of physics being altered to produce an economic conclusion.

## 19. EQUATION STATUS TABLE

| equation / statement | assumptions | analytic | independent verification | units | counterexample | classification | status |
|---|---|---|---|---|---|---|---|
| `V = ½Σ((xᵢ−x*ᵢ)/σᵢ)²` | Gaussian Level-1 declaration | — | — | dimensionless ✓ | — | **MATHEMATICAL DEFINITION** (choice of `V` is a CONSTITUTIVE HYPOTHESIS) | **definition** |
| `μ = ∇V`, `μᵢ = (xᵢ−x*ᵢ)/σᵢ²` | differentiability | ✓ | ✓ | `1/[M]` ✓ | — | **DEFINITION** | **FOUNDATIONAL** |
| `E = V_pre − V_post` | `V` a state function | ✓ | 3,662 exact | dimensionless ✓ | — | **DEFINITION** | **FOUNDATIONAL** |
| `E = −μᵀΔ − ½ΔᵀHΔ` | Gaussian `V` | **A and B agree** | 4,000 general + 3,662 exhaustive, 0 fail | ✓ | none | **DERIVED THEOREM** | **FOUNDATIONAL** |
| path integral `V_a−V_b = −∫∇V·dx` | `V` ∈ C¹, any path | ✓ | implied by above | ✓ | none | **DERIVED THEOREM** | **FOUNDATIONAL** |
| `f_e = μ_s − ημ_d = −dV/dq` | lossless/η edge | ✓ | numeric limit ✓ | `1/[M]` ✓ | none | **DERIVED THEOREM** | **FOUNDATIONAL** |
| `E = q(x_s−x_d−q)` | **`σ_s=σ_d=1` AND `x*_s=x*_d`** | ✓ | 2,000 + exhaustive | ✓ | **fails** at `σ=(1,2,1)` (5/8 vs 1) and `x*=(4,6,4)` (3 vs 1) | **DERIVED — SPECIALIZATION** | **valid on Study-1 only** |
| `R_a = −μᵀΔ_a − ½Δ_GᵀHΔ_a` | common-path convention | ✓ | 3,662 exact | ✓ | — | **ATTRIBUTION CONVENTION** (= Shapley) | **exact, not unique** |
| `Σ_a R_a = E_G` | any `V`, segment path | ✓ (FTC) | 3,662, 0 fail | ✓ | none | **DERIVED THEOREM** | **FOUNDATIONAL** |
| telescoping / refinement | `V` a state function | ✓ | 0 fail | ✓ | parallel-at-base fails by `−Δ₁ᵀHΔ₂` | **DERIVED THEOREM** | **FOUNDATIONAL** |
| `Σxᵢ` conserved | lossless edges | ✓ | 0 violations | `[M]` ✓ | `η<1` needs a sink coordinate | **DERIVED (domain-conditional)** | **FOUNDATIONAL on lossless** |
| factor potential identities | `V = Σφ_α` | ✓ | 400, 0 fail | ✓ | separability not needed for `E` | **DERIVED THEOREM** | **FOUNDATIONAL** |
| Möbius interpretation | finite action set | ✓ | order ≥3 exactly 0 | ✓ | none | **DERIVED THEOREM** | **FOUNDATIONAL** |
| `C + V = const` | §12 (i)–(v) | ✓ | Stage-A 768 episodes | ✓ | breaks if `θ` changes | **ACCOUNTING THEOREM** | **conditional** |
| owner-vector path dependence | attribution defined | ✓ | 18 vectors + loop | ✓ | — | **ACCOUNTING THEOREM** | **established** |
| `B_i ≥ 0` | — | **not derivable** | — | — | — | **INSTITUTIONAL RULE** | **not physics** |
| affordability gate | — | **not derivable** | — | — | — | **INSTITUTIONAL RULE** | **not physics** |
| leaf backlog absorption | (a)–(g) of §15 | ✓ within contract | 0/91 at k=3 | ✓ | — | **SERVICE-CONTRACT THEOREM** | **not physics** |

## 20. WHAT EBU ACTUALLY IS AFTER THIS AUDIT

**LAYER 1 — physical state and conservation.** `x`, `Δx = Sq`, `Σx` conserved (with explicit sinks when `η<1`).
**LAYER 2 — EBU field mathematics.** `V`, `μ = ∇V`, `E = V_pre − V_post`, the exact finite expansion, the path integral, `f_e = μ_s − ημ_d`, telescoping, factor and Möbius identities. **This is the whole of EBU physics, and it survives intact.**
**LAYER 3 — exact attribution.** `Σ_aR_a = E_G` (theorem); the common-path/Shapley split (convention); `C + V = const` (accounting theorem); owner-vector path dependence.
**LAYER 4 — actor behaviour.** Policies, selection rules.
**LAYER 5 — institutional/economic rules.** Affordability gate, `B_i ≥ 0`, no borrowing, no pooling, complete-service, additivity, persistence, no partial service.

Layers 4–5 appear nowhere in Layers 1–3 and are not required by any Layer 1–3 theorem.

## 21. FALSIFICATION ATTEMPT — RESULTS

Sign errors: none (`f_e` confirmed against the numeric derivative). Missing `½`: none (both proofs, 4,000 general cases). Wrong `σ` power: none — `μ` carries `1/σ²`, `H` carries `1/σ²`; a `1/σ` form would fail dimensionally and numerically. Efficiency placement: confirmed on the **destination** marginal. Path dependence of supposed state functions: `V` and `E` are exact; **`R_a` is correctly *not* claimed to be one**. Refinement failure: none sequentially; the parallel-at-base discrepancy is exactly the cross term and is now stated. Simultaneous-action inconsistency: none — receipts sum exactly. Conservation: 0 violations. Units: consistent throughout. **Hidden assumption of equal `σ`: FOUND — in `E = q(x_s−x_d−q)`.** **Hidden assumption of equal `x*`: FOUND — in the same formula.** Both are now stated as explicit hypotheses. Topology-dependent counterexample: the leaf-absorption result is topology-dependent, and is correctly demoted to a service-contract theorem.

**No core Layer-1/2 equation failed.** Two hidden hypotheses were found in a *specialization*, not in the core.

---

# 22. FINAL VERDICTS

### A. PHYSICAL EBU CORE

```
FOUNDATIONAL CORE SURVIVES DOUBLE-CHECK
```
Every Layer-1/2 equation has an analytic derivation, an independent exact computational verification (4,000+ general-parameter cases and 3,662 exhaustive Study-1 pairs, zero mismatches), a clean dimensional check, and correct limiting behaviour. **Domain of survival:** differentiable `V` on a real state space, with the Gaussian expansion requiring quadratic `V`; conservation requiring lossless edges or explicit sinks. **One correction to the programme's presentation, not to the mathematics:** `E = q(x_s − x_d − q)` is a specialization valid only when `σ_s = σ_d = 1` **and** `x*_s = x*_d`, and must never be written as the EBU edge equation.

### B. CAPACITY / ATTRIBUTION

```
DERIVED ONLY CONDITIONALLY
```
`Σ_a R_a = E_G` is a genuine theorem for any `V`. `C + V = const` is an **accounting** theorem requiring exact settlement, fixed field, actor-only evolution, no external `C` source/sink, and one reachable component. The **per-owner split is not unique** — at least five exact decompositions exist — and is canonical only under Shapley's axioms, which are a choice, not a measurement. The owner vector is **path-dependent** and is therefore **not a physical state function**. Nothing here derives `B_i ≥ 0`, affordability, no-borrowing or no-pooling.

### C. ECONOMIC / SERVICE MECHANISM

```
CONTAINS EXTRA NON-PHYSICAL ASSUMPTIONS
```
Namely: the affordability gate `B_i + r_i ≥ 0`; `B_i ≥ 0`; no borrowing; no pooling; complete-service; additive orders; no partial service; persistent held orders with no discard; one action per route per plan; and the declared quantum set. **Every one of the recent "continuity" results — owner-capacity blocking, the `p_B` drift theorems, leaf-backlog absorption, continuity-vs-survival — depends on this list and none of them is a theorem of EBU physics.**

No overall "EBU works/fails" verdict is given, and none is warranted.