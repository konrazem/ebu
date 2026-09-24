All verification complete. Every contested item re-derived independently, so the reconciliation does not rest on trusting either audit report.

---

# EBU PHYSICAL FOUNDATION — RECONCILIATION GATE

## 1. COORDINATE VERIFIED

| coordinate | expected | observed | status |
|---|---|---|---|
| commit | `2c4b71d15fe8cb46592d9f2ead8f5f4e62fe9e32` | identical | ✅ |
| tree | `5afe39788ecc6bff675b0820eef1669fb8b78ebf` | identical | ✅ |
| `demand_driven_ebu` identity | `f4e31a2a…3eec48` | identical | ✅ |

Recomputed from the worktree under the pinned recipe in `demand_driven_stage_a/sources.py` (sorted `*.py`, relative path bytes + file bytes). **Same mechanism.** No file was modified; nothing was committed; no Stage A or Stage B was run.

### Scope limitation, stated up front

I hold the full text of only **one** of the two audits — the "Face the devil" foundational audit (**Audit A**). **Audit B**'s positions are available to me only as reproduced in this brief's controlling text (§0, §6, §7, §8, §9, §13). I therefore **re-derived every contested item from scratch**, so each row below rests on my own verification rather than on either report. Rows where Audit B's position is known only through the brief are marked `(via brief)`.

---

## A. AUDIT-AGREEMENT TABLE

| # | item | Audit A | Audit B (via brief) | my re-verification | classification |
|---|---|---|---|---|---|
| 1 | `V(x;θ)` | Gaussian L1, constitutive | same | — | **EXACT AGREEMENT** |
| 2 | `μ = ∇V` | definition | same | 0 fail | **EXACT AGREEMENT** |
| 3 | `E = V_pre − V_post` | universal definition | universal, top of hierarchy | 0 fail | **EXACT AGREEMENT** |
| 4 | Gaussian finite theorem | derived 2 ways | corollary of (3) | **4,000 general cases, 0 fail** | **AGREEMENT WITH DOMAIN REFINEMENT** — A must not present it above (3) |
| 5 | path integral | proved via segment | proved for any admissible path | **600 curved-path cases, 0 fail** | **B GAVE THE STRONGER RESULT** |
| 6 | local/edge force | `μ_s − ημ_d` | `μ_s − ημ_d`, no third term | see §6 below | **REAL DISAGREEMENT — RESOLVED** |
| 7 | general Gaussian edge expansion | stated prominently | corollary only | 4,000 cases, 0 fail | **AGREEMENT WITH DOMAIN REFINEMENT** |
| 8 | Study-1 edge specialization | specialization + 2 counterexamples | specialization | 2,000 cases, 0 fail | **EXACT AGREEMENT** |
| 9 | loss / η<1 | "needs a sink coordinate" | "do not modify the EBU state" | see §7 below | **REAL DISAGREEMENT — RESOLVED AGAINST BOTH** |
| 10 | simultaneous receipts | closure a theorem | closure a theorem | **0 fail** | **EXACT AGREEMENT** |
| 11 | attribution uniqueness | not unique (5 splits) | convention, not physics | — | **EXACT AGREEMENT** |
| 12 | Shapley relation | = common-path for quadratic | quadratic only; demands non-quadratic counterexample | **300 quadratic, 0 fail; counterexample found** | **B GAVE THE STRONGER RESULT** |
| 13 | refinement / telescoping | exact; parallel-at-base fails | same; wants exact cross term | **2,000 cases, 0 fail** | **EXACT AGREEMENT** |
| 14 | conservation | `Σx` const (lossless) | represented-state law | **0 violations; full state closes** | **RESOLVED — see §7** |
| 15 | factor potentials | separability not needed for `E` | same | 0 fail | **EXACT AGREEMENT** |
| 16 | Möbius | terminates at order 2 | creates no EBU | **max nonzero order = 2, 0 fail** | **EXACT AGREEMENT** |
| 17 | `C + V` identity | accounting theorem | conditional accounting theorem | **0 violations / 4,000 steps** | **EXACT AGREEMENT** |
| 18 | owner-vector path dependence | not a state function | historical attribution object | **loop reproduced** | **EXACT AGREEMENT** |
| 19 | `B_i ≥ 0`, affordability | not derivable | forbidden in Layers 1–3 | — | **EXACT AGREEMENT** |
| 20 | borrowing / pooling | economic assumption | forbidden in Layers 1–3 | — | **EXACT AGREEMENT** |
| 21 | service / backlog semantics | service-contract theorem | institution-conditional | — | **EXACT AGREEMENT** |

### The two REAL DISAGREEMENTS, resolved mathematically

**§6 — edge force.** Both audits assert `f_e = μ_s − η μ_d`. The authoritative increment is not two-coordinate. `physical.PhysicalAction.increment` writes `source −q`, `destination +ηq`, **and `sink +(1−η)q`**. Verified directly:

```
AUTHORITATIVE lossy increment (η=3/4, q=4): (-4, 3, 1)   sum = 0
η<1 with NO sink declared:                   REFUSED
```

Chain rule on `S_e = −e_s + η e_d + (1−η) e_k` gives `f_e = μ_s − η μ_d − (1−η) μ_k`. Measured:

| sink declaration | `μ` | chain rule | `μ_s − ημ_d` | agree |
|---|---|---|---|---|
| audit-only (outside `V`) | `(2, −1, 0)` | `11/4` | `11/4` | **yes** |
| inside `V` | `(2, −1, 2)` | `9/4` | `11/4` | **no** |

> **RESOLUTION.** The brief's own conditions adjudicate this exactly, and both are simultaneously satisfiable. §6 permits a third term "**unless the authoritative physical state itself contains that coordinate and V evaluates it**" — the state *does* contain it, and `V` evaluates it *only when the sink is declared inside `V`*. Therefore:
> - **sink audit-only, or `η = 1`** → `μ_k = 0` → **`f_e = μ_s − η μ_d` is exact and canonical**, as §7 instructs.
> - **sink declared inside `V`** → **`f_e = μ_s − η μ_d − (1−η) μ_k`**, licensed by §6.
>
> This is a **domain condition on an existing equation, not a promotion of a special case and not a new coordinate.** Study-1 and all of Stage A sit in the first branch (`study_one.py:167,172` refuse any `efficiency ≠ 1` and any declared sink), so **no Stage-A result is touched.**

**§9/§15 — conservation.** Audit A said `η<1` needs a sink coordinate; the brief says full-state conservation is a hypothetical "enlarged model". **Both are superseded by the code.** The enlarged model is not hypothetical and was not introduced by this reconciliation — it is the implemented authoritative model, in which conservation closes exactly by construction (`sum(increment) = 0` above) and `REASON_CONSERVATION = "CONSERVATION_DOES_NOT_CLOSE"` exists as a refusal reason. Study-1 is its **lossless special case**.

---

## B. CANONICAL HIERARCHY

```
PHYSICAL TRANSITION LAW            determines Δx (incl. sink when declared)
        ↓
V(x; θ)                            constitutive field hypothesis
        ↓
μ = ∇ₓ V                           definition
        ↓
E = V(x_pre; θ) − V(x_post; θ)     ← THE UNIVERSAL DEFINITION. Nothing sits above it.
        ↓
f = −∇Vᵀ (dx/dq)                   local differential driving quantity
        ↓
─── everything below is a COROLLARY obtained by choosing a particular Δx ───
        Gaussian finite theorem
        general Gaussian two-coordinate edge corollary
        Study-1 edge specialization
```

---

## C. CANONICAL EQUATIONS

Both audits independently support these, and I re-verified each.

```
μ(x;θ) = ∇ₓ V(x;θ)

E(x_pre → x_post | θ) = V(x_pre;θ) − V(x_post;θ)

E = − ∫_γ ∇V · dx      for ANY admissible path γ at fixed θ
```

**Assumptions:** `V` single-valued and `C¹` on the relevant domain; `θ` fixed along `γ`; `γ` contained in that domain. **No Gaussian assumption, no separability, no edge structure, no η.**

> **Path independence verified independently of telescoping.** 600 exact-rational cases on genuinely **curved** paths `γ(t) = a + t(b−a) + t(1−t)w`, integrand expanded to an exact polynomial and integrated in closed form: **0 disagreements** with `V(a) − V(b)`. This is a stronger check than the segment/telescoping argument, which only tests piecewise-linear paths.

```
f = −dV/dq = −∇Vᵀ (dx/dq)
```

**Edge form (current authoritative state model):** with `S_e = −e_s + η_e e_d` (+ `(1−η)e_k` when a sink is declared),

```
f_e = μ_s − η_e μ_d          exact when μ_k = 0 (audit-only sink, or η = 1)
f_e = μ_s − η_e μ_d − (1−η_e) μ_k     when the sink is declared inside V
```

Sign verified 2,000 cases, 0 disagreements.

---

## D. SPECIALIZATIONS / COROLLARIES

**D1 — EXACT GAUSSIAN FINITE-EQUATION THEOREM.** For `V = ½(x−x*)ᵀH(x−x*)`, `H = diag(1/σᵢ²)`:

```
μ = H(x − x*)          E = −μᵀΔx − ½ Δxᵀ H Δx
```

*Derivation A (expansion):* `V(x+Δ) = V(x) + μᵀΔ + ½ΔᵀHΔ`.
*Derivation B (line integral):* `−∫₀¹[(x−x*)ᵀHΔ + λΔᵀHΔ]dλ = −μᵀΔ − ½ΔᵀHΔ`. Identical. ∎
*Independent verification:* 4,000 random general-`σ`/`x*` exact-rational cases, **0 disagreements**; plus **5,734 feasible Study-1 (state, group) pairs, 0 mismatches** against the mechanism's own valuation.
**Classification: EXACT GAUSSIAN FINITE-EQUATION THEOREM. It is not the definition of EBU.**

**D2 — CONDITIONAL GAUSSIAN TWO-COORDINATE COROLLARY.** For `Δ_s = −q`, `Δ_d = +q` inside Gaussian `V`:

```
E = q[(x_s−x*_s)/σ_s² − (x_d−x*_d)/σ_d²] − (q²/2)[1/σ_s² + 1/σ_d²]
```

Verified 4,000 cases, 0 disagreements. **This is `E = V_pre − V_post` after choosing one particular `Δx`. It has no foundational standing and must never be written as "the EBU edge equation."**

**D3 — STUDY-1 SPECIALIZATION.**

```
E = q(x_s − x_d − q)
```

**Required assumptions, all of them:** Gaussian Level 1; source/destination the only changing coordinates; lossless (`η = 1`, no sink); `x*_s = x*_d`; `σ_s = σ_d = 1`. Verified 2,000 cases, 0 disagreements. **Exact counterexamples outside its domain**, at `x=(5,3,4)`, `A→B@1`:

| violated assumption | exact `V_pre − V_post` | formula claims |
|---|---|---|
| `σ = (1,2,1)` | **5/8** | 1 |
| `x* = (4,6,4)` | **3** | 1 |

**Classification: STUDY-1 SPECIALIZATION, permanently.**

**D4 — FINITE vs DIFFERENTIAL — CANONICAL WARNING.**

```
first-order term:  −μᵀΔ              finite value:  −μᵀΔ − ½ΔᵀHΔ ≤ first-order
```

> **At equilibrium `μ = 0` the force is zero for every action, yet every nonzero finite displacement has `E = −½ΔᵀHΔ < 0`.** Measured at `x = x*`: linear estimate `0` for both, exact `E = −1` (`q=1`) and `−4` (`q=2`). **Never infer finite action value from force alone.**

**D5 — REFINEMENT AND THE CROSS TERM.**

```
E(x → x+Δ₁+Δ₂) = E(x → x+Δ₁) + E(x+Δ₁ → x+Δ₁+Δ₂)        exact, any V
```

because `E` is a state-function difference. **But evaluated from a common base**, for quadratic `V`:

```
E(x,Δ₁+Δ₂) − [E(x,Δ₁) + E(x,Δ₂)] = −Δ₁ᵀHΔ₂
```

Both verified, 2,000 cases, 0 failures; telescoping 0 failures over all 5,734 Study-1 pairs. **Action legality, provenance and service rules are outside this theorem.**

**D6 — FACTOR POTENTIALS.** For `V = Σ_α φ_α(x_{S_α})`: gradients add; `E = Σ_α[φ_α(pre) − φ_α(post)]`; untouched factors contribute exactly 0; the path identity holds per factor. **Coordinate separability is NOT required for `E = V_pre − V_post`** — verified on a `V` containing the cross term `x₀x₁/2`, 0 mismatches. A factor may itself be internally coupled.

**D7 — MÖBIUS / INTERACTION STRUCTURE.** Finite EBU exists *before* decomposition; Möbius inversion **creates no EBU** (`Σ_S m(S) = E(full set)`, verified). For quadratic `V` with fixed additive increments, `m({a}) = E(Δ_a)` and `m({a,b}) = −Δ_aᵀHΔ_b`, and **interaction order terminates at 2** — measured `max nonzero order = 2` across 200 random 3–5-action groups, 0 failures. **Interactions are not extra issuance.**

---

## E. ATTRIBUTION / ACCOUNTING STATUS

**E1 — TOTAL CLOSURE: DERIVED THEOREM.** For `Δ_G = Σ_a Δ_a` and `R_a = −∫₀¹∇V(x+λΔ_G)ᵀΔ_a dλ`:

```
Σ_a R_a = −∫₀¹ ∇V(x+λΔ_G)ᵀ Δ_G dλ = V(x) − V(x+Δ_G) = E_G
```

by the fundamental theorem of calculus — **no Gaussian assumption**. Gaussian form `R_a = −μᵀΔ_a − ½Δ_aᵀHΔ_G`. Verified: **0 failures over all 5,734 Study-1 pairs**, both closure and closed form.

**E2 — INDIVIDUAL SPLIT: ATTRIBUTION CONVENTION.** Not uniquely observable physics. At least five exact decompositions of one `E_G` exist (common-path, two sequential orders, Shapley, proportional). **Not claimed as physics.**

**E3 — SHAPLEY RELATION: MATHEMATICALLY CANONICAL UNDER EXTRA AXIOMS.**

> **Theorem.** For **quadratic** `V` and **fixed additive** increments, the common-path attribution equals the Shapley value of `v(S) = V(x) − V(x + Σ_{a∈S}Δ_a)`.
> *Proof.* `v(S) = −Σ_{a∈S}μᵀΔ_a − ½Σ_{a∈S}Δ_aᵀHΔ_a − Σ_{{a,b}⊆S}Δ_aᵀHΔ_b`. Shapley assigns additive and own-quadratic terms wholly to their action and splits each pair term equally: `Sh_a = −μᵀΔ_a − ½Δ_aᵀHΔ_a − ½Σ_{b≠a}Δ_aᵀHΔ_b = −μᵀΔ_a − ½Δ_aᵀHΔ_G`. ∎
> *Verified:* 300 random general-`σ`, general-`x*` cases, **0 disagreements**.

> **COUNTEREXAMPLE FOR NON-QUADRATIC `V` — the equivalence is quadratic-only.**
> `V(x) = x⁴/4`, `x = 0`, `Δ₁ = 1`, `Δ₂ = 2`:
>
> | | action 1 | action 2 | sum |
> |---|---|---|---|
> | common-path | **−27/4** | **−27/2** | −81/4 |
> | Shapley | **−33/4** | **−12** | −81/4 |
>
> Both are exact and both close on `E_G = −81/4`; **they disagree action-by-action.** The Shapley equivalence is therefore a *property of quadratic `V`*, not a general justification of the common-path convention. **This must be preserved.**

**E4 — FIXED-FIELD AGGREGATE ACCOUNTING: CONDITIONAL ACCOUNTING THEOREM.**

> If `ΔC_total = E_t` each step, then `C_T = C_0 + Σ_t[V(x_t) − V(x_{t+1})] = C_0 + V(x_0) − V(x_T)`, hence **`C + V = const`**. ∎
> **Required:** exact settlement; `θ` fixed; no omitted external physical event; no external `C` source or sink; one reachable component.
> *Verified:* 4,000-step random admissible walk on the live mechanism, **0 violations**.
> **This is NOT a physical conservation law.** No sign constraint on `C` is introduced or needed.

**E5 — PER-OWNER ATTRIBUTION: HISTORICAL ATTRIBUTION OBJECT.**

> Closed physical loop on the live mechanism, `x* → (4,3,5) → x*`:
>
> | step | `E` | owner receipts |
> |---|---|---|
> | `B→C@1` | −1 | `{B: −1}` |
> | `C→B@1` | +1 | `{C: +1}` |
> | **net** | **0** | **`{B: −1, C: +1}`** |
>
> The state returns identically; the attribution vector does not. **`Σ_i ω_i = −dV` is exact, so aggregate `C` is a state function; each `ω_i` is not closed, so the owner vector is a genuine path integral.** Aggregate closure does **not** imply actor balances are functions of `x`.
>
> **No economic restriction is inferred from this.** Path dependence is what an attribution *is*; it is not evidence for or against any account rule.

---

## F. FORBIDDEN FOUNDATION LIST

None of the following appears in Layers 1–3, and none is required by any Layer 1–3 theorem:

`B_i ≥ 0` · `B_i + R_i ≥ 0` before an action · no borrowing · no pooling · complete-service requirement · persistent additive economic orders · no partial service · FIFO · backlog · price · utility · welfare · privilege · debt restrictions · service priority.

**These may never be used to modify `V`, `μ`, `E`, `f`, conservation or attribution backwards.** They may be studied only as explicitly declared external actor/institutional hypotheses at Layers 4–5.

---

## G. LAYER MODEL

| layer | contents |
|---|---|
| **1 — PHYSICAL STATE / TRANSITION / CONSERVATION** | `x`; coordinates (valued and audit-only); routes; `S_e`/`Δx`; `η` as a physical transfer property; **the declared loss sink, which is already part of the authoritative state**; carrier conservation |
| **2 — EBU FIELD MATHEMATICS** | `V`; `μ = ∇V`; `E = V_pre − V_post`; `f = −∇Vᵀdx/dq` and the edge form; Gaussian finite theorem; path integral; factor structure; Möbius identities; the finite-vs-differential warning |
| **3 — ATTRIBUTION / ACCOUNTING** | simultaneous receipt closure (theorem); common-path convention; Shapley relation under quadratic `V`; aggregate `C+V` identity; historical actor accounts |
| **4 — ACTOR DECISION** | random; aligned; hostile; any future decision strategy |
| **5 — INSTITUTION / ECONOMY** | affordability; account sign restrictions; service contracts; queues; prices; welfare; privileges |

**No upward leakage.** Layers 4–5 appear nowhere in Layers 1–3.

---

## H. RECLASSIFIED STAGE-B "DISCOVERIES" *(mathematics unchanged)*

| result | classification |
|---|---|
| closed capacity budget `C + W = I` | **ACCOUNTING** (conditional, E4 assumptions) |
| owner-capacity blocking | **INSTITUTION / SERVICE-CONTRACT CONDITIONAL** — vanishes without the V1 gate |
| `p_B` drift results | **ACCOUNTING**, conditional on gate + service semantics + minimal-cycle class |
| leaf-backlog absorption | **INSTITUTION / SERVICE-CONTRACT CONDITIONAL** — physics contributes only the leaf topology; the result additionally requires one-action-per-route, complete service, additivity, persistence, no partial service |
| continuity / survival results | **INSTITUTION / SERVICE-CONTRACT CONDITIONAL + EXPERIMENTAL HARNESS** |

**None is PHYSICAL EBU. None feeds backward into Layers 1–2.** Nothing is deleted.

---

## I. STAGE-A STATUS AFTER RECONCILIATION

Stage A was **not** rerun, and the Stage-A record is **not** rewritten.

> **Stage-A observations remain valid observations of the frozen historical V1 mechanism.** Their *foundational* classification is now explicit:

| episode | classification |
|---|---|
| **A1** policy observations | **actor/mechanism study** (Layer 4) — not a physical law |
| **A2** affordability result | **evidence that the historical institutional V1 gate changes execution** (Layer 5). It is **not** evidence of a physical EBU law. The underlying physics it exposes — that at `μ = 0` every finite action has `E = −½ΔᵀHΔ < 0` — is D4, and D4 stands on its own without A2 |
| **A3** lifecycle | **conditional on its declared service semantics** (Layer 5) |

**A short classification addendum is warranted** — a layer-assignment note appended to the Stage-A record stating that its observations are Layer 4–5 results about the V1 mechanism, with no change to any number, claim or preregistered metric. **I have not created it**, as this task forbids editing files.

---

## J. REMAINING PHYSICAL QUESTIONS

Genuine foundational openings only; no economic questions.

1. **Why does `V` have its physical form?** Currently a constitutive hypothesis with no deeper derivation.
2. **Is Gaussian `V` exact, local, or a Level-1 approximation?** Unresolved; the quadratic assumption is load-bearing for D1, D2, D3, D7 and the Shapley relation (E3), and the non-quadratic counterexample shows the last of these genuinely fails outside it.
3. **Physical meaning of `σ`.** A declared scale with no independent measurement procedure.
4. **Relation of `σ` to fluctuation covariance / susceptibility.** If `σ²` is a variance, `H` is an inverse covariance — unestablished.
5. **Changing `θ`.** Every theorem above is at fixed `θ`. Nothing here covers a moving field.
6. **Full physical treatment of loss and environment**, in particular whether a loss sink *should* be inside `V` or audit-only — currently a declaration, and §6 above shows the edge-force law depends on it.
7. **Entropy-deficit relation** (see K).
8. **Large-deviation / rate-function interpretation** of `V`.
9. **Universal scale `κ` and cross-field commensurability.**

---

## K. ENTROPY-DEFICIT COMPATIBILITY STATUS

Assume only `S_θ(x) = S_eq(θ) − κ V_θ(x)` with `κ > 0` constant and `θ` fixed. Then

```
∇S = −κ μ            ΔS/κ = V_pre − V_post = E
```

Verified: 500 exact-rational cases, **0 disagreements**.

> **Classification: MATHEMATICALLY COMPATIBLE. Nothing more.** This is an affine change of variable; it adds no physical content and proves nothing about entropy.
>
> **Still required before any entropy interpretation may be claimed:** an independent measurement of `S` not defined through `V`; physical identification of `κ` with units; evidence that `S_eq(θ)` is a genuine equilibrium entropy; a statistical ensemble in which `V` is the large-deviation rate function.
>
> **Explicitly refused as circular:** asserting `P ∝ exp(−V)` merely because `V` was chosen. That would define the ensemble from the potential and then present the potential as a consequence of the ensemble.

---

## L. CANONICAL EQUATION TABLE

| canonical equation / statement | layer | assumptions | general or specialization | status | Audit A | Audit B | reconciliation | warning / forbidden overstatement |
|---|---|---|---|---|---|---|---|---|
| `V(x;θ) = ½Σ((xᵢ−x*ᵢ)/σᵢ)²` | 2 | Level-1 declaration | **specialization of "some `V`"** | **constitutive physical/field hypothesis** | agree | agree | EXACT | never call it a derived law |
| `μ = ∇ₓV` | 2 | `V ∈ C¹` | **general** | mathematical definition | agree | agree | EXACT | — |
| **`E = V_pre − V_post`** | 2 | `V` a state function at fixed `θ` | **GENERAL — TOP OF HIERARCHY** | mathematical definition | agree | agree | EXACT | **never replace with an edge polynomial** |
| `E = −∫_γ ∇V·dx`, any `γ` | 2 | `V` single-valued `C¹`, `θ` fixed | **general** | derived theorem | agree | **stronger** | B stronger; 600 curved-path cases, 0 fail | do not confuse with attribution-path dependence |
| `f = −∇Vᵀ dx/dq` | 2 | differentiability | **general** | derived theorem | agree | agree | EXACT | — |
| `f_e = μ_s − η μ_d` | 2 | `S_e = −e_s + ηe_d`; **`μ_sink = 0`** (audit-only sink, or `η=1`) | **edge form** | derived theorem | agree | agree | **RESOLVED domain condition** | **not valid when the sink is declared inside `V`** |
| `f_e = μ_s − ημ_d − (1−η)μ_k` | 2 | sink declared **inside** `V` | **edge form, in-`V`-sink branch** | derived theorem | not stated | not stated | new, licensed by §6 | **not a new coordinate — the state already has it** |
| `μ = H(x−x*)`, `E = −μᵀΔ − ½ΔᵀHΔ` | 2 | Gaussian `V` | **EXACT GAUSSIAN FINITE THEOREM** | derived theorem | derived ×2 | corollary | AGREEMENT + refinement | **not the definition of EBU** |
| `E = −½ΔᵀHΔ` at `μ=0` | 2 | Gaussian, `x = x*` | corollary | derived theorem | agree | agree | EXACT | **never infer finite value from force** |
| general two-coordinate edge expansion | 2 | Gaussian, lossless, `s`/`d` only | **CONDITIONAL COROLLARY** | derived theorem | prominent | corollary | refinement — moved **down** | **not the general EBU edge equation** |
| `E = q(x_s − x_d − q)` | 2 | Gaussian, lossless, `s`/`d` only, `x*_s = x*_d`, `σ_s = σ_d = 1` | **STUDY-1 SPECIALIZATION** | derived theorem | agree | agree | EXACT | **never the general EBU equation**; fails at `σ=(1,2,1)` (5/8 vs 1) and `x*=(4,6,4)` (3 vs 1) |
| sequential telescoping | 2 | `V` a state function | **general** | derived theorem | agree | agree | EXACT | legality/provenance are outside it |
| `E(x,Δ₁+Δ₂) − [E₁+E₂] = −Δ₁ᵀHΔ₂` | 2 | quadratic `V`, common base | corollary | derived theorem | agree | agree | EXACT | same-base sums are **not** the joint value |
| carrier conservation (full state) | 1 | sink coordinate present when `η<1` | **general in the current model** | physical law of the represented state | "needs a sink" | "optional enlarged model" | **RESOLVED — already implemented** | not optional; `η<1` without a sink is refused |
| `V = Σφ_α` factor identities | 2 | `V` factorizes | corollary | derived theorem | agree | agree | EXACT | **separability not needed for `E`** |
| Möbius, order terminates at 2 | 2 | quadratic `V`, fixed additive increments | corollary | derived theorem | agree | agree | EXACT | **creates no EBU** |
| `Σ_a R_a = E_G` | 3 | any `V`, common path | **general** | derived theorem | agree | agree | EXACT | closure ≠ identification |
| `R_a = −μᵀΔ_a − ½Δ_aᵀHΔ_G` | 3 | Gaussian `V` | corollary | **attribution convention** | agree | agree | EXACT | **not uniquely observable physics** |
| common-path = Shapley | 3 | **quadratic `V`**, fixed additive increments | corollary | canonical **under extra axioms** | derived | quadratic-only | **B stronger** — counterexample `V=x⁴/4` | **fails for non-quadratic `V`** |
| `C + V = const` | 3 | E4 (i)–(v) | conditional | **accounting theorem** | agree | agree | EXACT | **not a conservation law**; no sign constraint on `C` |
| owner vector is path-dependent | 3 | attribution defined | — | **historical attribution object** | agree | agree | EXACT | **infer no economics from it** |
| `B_i ≥ 0`, affordability, borrowing, pooling | **5** | — | — | **institutional rule** | not derivable | forbidden in 1–3 | EXACT | **never physics** |
| service / backlog semantics | **5** | — | — | **service contract** | agree | agree | EXACT | topology alone proves nothing here |

---

## M. CRITICAL THEORY-DRIFT CHECK

| drift risk | finding |
|---|---|
| replaced `E = V_pre − V_post` by an edge polynomial | **No.** `E` sits at the top; D2 and D3 are placed below it and labelled. |
| introduced a new physical coordinate | **No — and this was the one real risk.** The sink coordinate was **not introduced by me**. It is in `world.Route.sink`, written by `physical.PhysicalAction.increment`, and `η<1` without it is **refused** by the authoritative model. Verified by direct execution before any claim was made. |
| changed the meaning of `η` | **No.** `η` remains a physical transfer property of a route at Layer 1. |
| modified the canonical force law | **No.** `f_e = μ_s − η μ_d` is retained verbatim and given its exact domain; the three-term form is the same chain rule on the branch where `V` evaluates the sink, exactly as §6 permits. |
| promoted attribution into physics | **No.** Closure is a theorem; the split is a convention; the Shapley relation is explicitly quadratic-only and now carries a counterexample. |
| promoted accounting into conservation | **No.** `C+V` is labelled a conditional accounting theorem in every occurrence. |
| promoted institutional rules into EBU | **No.** The full forbidden list is held at Layer 5. |
| inferred economics from desired behaviour | **No.** No economic desirability was used as a proof criterion. I note for the record that an earlier Stage-B design pass of mine proposed amplitude and `p_B` levels partly so the affordability gate would be exercised; that reasoning is **excluded** here and must not enter any preregistration. |

---

## N. OPEN CONFLICTS

**None unresolved.** Both REAL DISAGREEMENTS (edge force; loss/conservation) were resolved mathematically and by direct execution against the authoritative mechanism, using only coordinates that model already contains. Two items required correcting a premise rather than an equation, and neither changes any Stage-A result:

1. `f_e = μ_s − η μ_d` needs the explicit domain condition `μ_sink = 0`.
2. Full-state carrier conservation is the **current implemented law**, not a hypothetical enlarged model.

Everything else is either exact agreement or a specialization moved **down** the hierarchy, never a modification upward.

---

# FINAL DISPOSITION

```
PHYSICAL EBU FOUNDATION RECONCILED —
CANONICAL CORE READY FOR INDEPENDENT FREEZE AUDIT
```

No freeze document was created or edited. No repository file was modified. Nothing was committed or pushed. Stage B was not resumed, designed or discussed.