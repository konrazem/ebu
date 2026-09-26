# Dynamic EBU field theory III — one-scalar current-field capacity

> **SUPERSEDED AS AUTHORITY by `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md`.**
> Retained as working history. Where this file conflicts with the synthesis, the
> synthesis governs. Do not cite this file as programme authority.


**Pure mathematics. No simulation, implementation or Stage A/B.**

This report answers one question:

> Can **one persistent scalar actor balance** remain an **exact** representation
> of **current-field** EBU capacity when `theta` changes?

**Answer: only for uniform rescalings — and those are exactly the field changes
that alter no affordability decision at all.** §8 states the verdict.

Checks: `dynamic_ebu_theory_checks.py` — **183 deterministic checks, 0 failures**,
exact `Fraction`, tolerance zero, no randomized search.

---

## 0. Three corrections to Theory II

**0.1 Finite level-set compatibility replaces infinitesimal N1.** The condition is
not `grad W_alpha = 0 ⟺ grad V_alpha = 0` but the **finite** statement

```
W_alpha(u) = W_alpha(v)   =>   V_{alpha,theta}(u) = V_{alpha,theta}(v)
```

on the reachable factor domain — i.e. `V_{alpha,theta}` is a genuine function of
`W_alpha`. The infinitesimal version is strictly weaker: with `W(x) = x^2/2` and
`V(x) = x^2/2` for `x >= 0`, `x^2` for `x < 0`, the gradients are positively
proportional everywhere and both vanish only at `0`, yet `W(1) = W(-1)` while
`V(1) != V(-1)`, and the finite action `1 -> -1` has `Delta W = 0` with
`Delta V = -1/2` — settlement zero for a priced action.

**0.2 Differential sign.** The correct differential is

```
dc = -dW ,        so        Delta c = W_before - W_after ,
```

with `dc = delta_e / p` and `delta_e := -dV_theta` the infinitesimal EBU in the
before-minus-after convention. **Positive capacity is earned when `W`
decreases.** Theory II's finite rule and its receipt formula
`C_a = -∫ grad W . delta_a` were already consistent with this; only the
shorthand `dc = dW` was wrong.

**0.3 Factor refinement.** Refinement is valid **only when both the reference and
the current physical potential are exactly additive under it.** Genuine cross
terms may not be discarded: `W = (x^2 + y^2 + xy)/2` has mixed second difference
`1/2 != 0`, so it admits no separable refinement, and the obstruction there is
final.

**Status of factorwise normalization.** Retained as a **proved mathematical
construction**: it yields an exact, refinement-invariant, cycle-closing,
history-free scalar coordinate. It is **not** the completed dynamic regulatory
mechanism, for the reason §2 makes precise.

---

## 1. The author axiom and the architecture it forces

> **AXIOM.** An action whose **current** exact aggregate EBU is negative may not
> earn positive actor capacity.

Current physical valuation is `E_theta(G) = V_theta(pre) - V_theta(post)` with
current common-path per-owner receipts `R_{i,theta}(G)`.

**A. Actor event** (at fixed `theta`): `B_i^+ = B_i^- + R_{i,theta}(G)`.
Hence current EBU `> 0` ⟹ positive aggregate settlement, and `< 0` ⟹ negative.
The axiom holds by construction.

**B. Field event** (at fixed `x`, `theta -> theta'`): a history-free local scalar
revaluation `B' = F_{theta->theta'}(B)`, subject to:

| | requirement |
|---|---|
| 1 | `F_{theta->theta}(B) = B` |
| 2 | `F` order preserving |
| 3 | `F(0) = 0` |
| 4 | consistent composition across successive field changes |
| 5 | static `theta` recovers V1 exactly |
| 6 | closed state+field cycles create no unexplained capacity |
| 7 | field revaluation is a **field** contribution, never actor reward |

---

## 2. Why Theory II's coordinate is not a current-field regulator

The author's example, verified exactly. Reference `x* = (2,2,2)`,
`sigma_ref = (1,1,1)`, `sigma_cur = (1,2,3)`, action `(2,0,4) -> (3,0,3)`:

```
W(before) = 4 ,  W(after) = 3        ->   Delta W = W_before - W_after = +1
V_cur(before) = 13/18 , V_cur(after) = 19/18   ->   E_theta = -1/3
```

*(Checked: `T3-1`.)* The reference-anchored coordinate of Theory II settles
**+1** — it **earns** — on an action the current field prices as a **cost of
1/3**. That directly violates the axiom.

> **Theory II's factorwise coordinate is anchored to `theta_0` and therefore
> tracks the reference field's sign, not the current one.** It remains a valid
> exact coordinate; it is not a regulator of the current field. *(Checked:
> `T3-2`.)*

This is why the question must be re-asked with current-field receipts, which is
what the rest of this report does.

---

## 3. The central commutation test

For any action `G` representable under both fields, exactness requires

```
F(B + R_theta(G))  =  F(B) + R_{theta'}(G).
```

**Theorem C (necessary and sufficient functional form).** Put `g := F - F(0)`.

1. Setting `B = 0` gives `g(R_theta(G)) = R_{theta'}(G)` for every `G`.
2. Substituting back, `g(B + r) = g(B) + g(r)` for every achievable receipt `r`
   and every reachable balance `B`.
3. **Every reachable `B` is itself a finite sum of achievable receipts** — the
   balance starts at `0` and accumulates only receipts — so `g` is **additive on
   the whole reachable balance set**.
4. Additive **and order preserving** (requirement 2) forces `g(B) = qB` with
   `q > 0`.
5. Requirement 3 gives `F(0) = 0`, hence

```
F(B) = q B          and          R_{theta'}(G) = q R_theta(G)   for every G.
```

∎

**Exactly how rich the action set must be.** Step 3 needs the reachable balance
set to be additively generated by the achievable receipts — **automatic** in this
architecture. Step 4 needs that set to carry no non-linear additive function.
This is automatic when the set is cyclic (a lattice of receipts) or dense in `R`;
in the general case it is delivered by monotonicity, which excludes the
Hamel-basis pathologies (on `Z + sqrt2 Z` one could otherwise set `g(1) = 1`,
`g(sqrt2) = 0`). **No further richness is required, and the claim in the task
statement is therefore proved, not merely plausible.**

**Requirements 4, 6, 7 are then automatic.** Composition gives
`q_{theta->theta''} = q_{theta'->theta''} q_{theta->theta'}` and
`q_{theta'->theta} = 1/q_{theta->theta'}`; a closed state cycle at fixed field
sums receipts to zero by telescoping, and a closed field cycle multiplies by
`q · (1/q) = 1`, so closed state+field cycles create nothing; and the increment
`(q-1)B` is booked to the field ledger, never to an actor.

---

## 4. The nonuniform no-go

**Theorem NU-III.** If there exist allowed actions `G1, G2` with

```
R_{theta'}(G1)/R_theta(G1)  !=  R_{theta'}(G2)/R_theta(G2),
```

then **no history-free one-scalar `F` is exact.**

*Proof.* Theorem C forces `R_{theta'}(G) = q R_theta(G)` for a single `q`,
contradicting the two distinct ratios. ∎

**Information-theoretic counterexample** — the sharper form, exhibiting exactly
what the scalar has lost. In the 3-cell world with `sigma_ref = (1,1,1)`,
`sigma_cur = (1,2,3)`:

```
G1 : (0,0,6) -> (1,0,5)      R_theta = 5      R_theta' = 17/9
G2 : (0,6,0) -> (1,5,0)      R_theta = 5      R_theta' = 19/8
```

Two actors starting at `B = 0`, one performing `G1` and the other `G2`, hold the
**same** balance `B = 5`. Exactness under `theta'` demands simultaneously
`F(5) = 17/9` and `F(5) = 19/8`. **One scalar cannot hold two values.**
*(Checked: `T3-3`.)*

> The balance `B` is a **lossy summary of the history**, and the revaluation
> depends on *which* history produced it. Restoring exactness would require
> carrying the information that distinguishes `G1` from `G2` — precisely the
> source/dependency vector the architecture forbids.

Across all 126 allowed actions of that world the ratio takes **33 distinct
values**, and some are **negative** — so not even a sign-consistent `q` exists.
*(Checked: `T3-4`.)*

---

## 5. Atomic local form

At a physical state `x` with allowed infinitesimal directions `u` in the allowed
action space `T`, a single local `q` requires

```
dE_{theta'}(u) = q dE_theta(u)      for every allowed u.
```

Since `dE_theta(u) = -grad V_theta . u`, this is exactly

> **`P_T grad V_{theta'} = q P_T grad V_theta`** — the **projected** gradients on
> the allowed action space must be positively proportional, with `q` independent
> of `x` (Theorem C makes `q` global, not merely local).

For conservation-respecting transfers `T = 1^perp`, so the condition is on the
**centred** marginal vectors.

**Subdivision does not change this.** At `x = (2,0,4)` with the two independent
allowed directions `u = -e_0 + e_2` and `v = -e_2 + e_1`:

```
direction u :  dE_ref = -2 ,  dE_cur = -2/9   ->  ratio 1/9
direction v :  dE_ref = +4 ,  dE_cur = 13/18  ->  ratio 13/72
```

*(Checked: `T3-9`.)* Subdividing a finite action merely samples the **same**
gradient field more finely; the two directional ratios are unchanged. **Arbitrary
refinement cannot repair a directional disagreement** — which is the exact
contrast with Theory II, where refinement invariance was the *selection*
principle.

---

## 6. Gaussian specialization

`V_theta = 1/2 sum_i ((x_i - x*_i(theta))/sigma_i(theta))^2`, with
`grad V_theta = H_theta (x - x*(theta))`, `H = diag(1/sigma_i^2)`, and
`T = 1^perp`.

Matching the `x`-dependence and the constant separately gives the exact criterion

```
P_T H_{theta'} P_T = q P_T H_theta P_T        and        P_T H_{theta'} x*_{theta'} = q P_T H_theta x*_theta .
```

| case | verdict |
|---|---|
| **common `sigma` scaling** `sigma -> c sigma` | **admissible**, `q = 1/c^2`; the ratio is a single value across all 126 actions for `c = 2, 1/2, 3` *(`T3-5`)* |
| **independent `sigma_i` changes** | **inadmissible** for `n >= 3`: the compression `sum_i c_i t_i^2 = 0` on `1^perp` with `t = e_i - e_j` forces `c_i + c_j = 0` for all pairs, hence `c = 0` and `H' = qH` *(`T3-8`)*. This is the author's `(1,2,3)` example |
| **moving references** | admissible **only** along `span(sigma_1^2,...,sigma_n^2)`, where `q = 1` and no EBU value changes; any other shift destroys the single ratio *(`T3-6`)* |
| **conservation-respecting directions** | the projection onto `1^perp` is what produces the *centred* condition; it is what makes `n = 2` special |
| **1-D versus multi-D action spaces** | **decisive.** With two cells `dim T = 1`, so any two covectors on `T` are proportional and a single `q` always exists — verified: `sigma (1,1) -> (1,2)` gives the single ratio `5/8` *(`T3-7`)*. With `n >= 3`, `dim T >= 2` and the no-go bites |

**Why a valid Dynamic EBU regulator must follow the current EBU sign.** In the
author's example the reference coordinate rewards `+1` while the current field
prices the action at `-1/3`. A regulator anchored to `theta_0` would licence an
actor to **earn** capacity by degrading the field as it now stands, and to repeat
it: the licence would be issued against a potential nobody is any longer subject
to. Only settlement by `R_{i,theta}` — the current receipts — makes the sign of
the licence agree with the sign of the physical consequence actually incurred.

---

## 7. What exactly survives

Inside the admissible class, `F(B) = qB` and `R_{theta'} = q R_theta`. By
same-ruler cancellation, `qB + qR >= 0 ⟺ B + R >= 0`, so **no affordability
decision changes** *(Checked: `T3-10`)*.

> **The admissible field changes are precisely the economically vacuous ones.**
> A uniform rescaling is a change of units: every current EBU magnitude and the
> whole wallet move by one common positive factor, and nothing an actor may or
> may not do is altered. Exact one-scalar current-field capacity survives
> **exactly** where the field change does not matter.

This is not a defect of the proof; it is the content of the result.

---

## 8. FINAL RESULT

> # EXACT ONE-SCALAR CURRENT-FIELD CAPACITY EXISTS ONLY FOR UNIFORM RESCALINGS

**The class.** A single persistent scalar balance is an exact representation of
current-field EBU capacity across `theta -> theta'` **if and only if** there is
one global `q > 0` with

```
R_{theta'}(G) = q R_theta(G)   for every representable action G,
```

equivalently `P_T grad V_{theta'} = q P_T grad V_theta` at every reachable state,
equivalently `V_{theta'} = q V_theta + const` on each reachable component. The
revaluation is then forced to be `F(B) = qB`.

For the Gaussian family with `n >= 3` cells this is **exactly** common `sigma`
scaling, together with reference motion along `span(sigma_i^2)` (which changes no
EBU value at all). For `n = 2`, where the allowed action space is
one-dimensional, every per-coordinate `sigma` change also qualifies.

**Proof of impossibility outside the class.** Theorem C shows the commutation
test forces `F(B) = qB` and `R_{theta'} = q R_theta` with one global `q`; the
richness needed is automatic, because the balance is by construction a sum of
receipts and `F` is order preserving. If two allowed actions rescale differently,
that single `q` cannot exist (Theorem NU-III). The failure is
**information-theoretic, not merely algebraic**: two histories — `G1` and `G2`
above — produce the **identical** balance `B = 5` yet must revalue to `17/9` and
`19/8`. The scalar has discarded exactly the information its own revaluation
requires. Recovering it would demand a per-source or per-action record, which the
axioms forbid.

**The no-go boundary, stated exactly.** Outside the class what fails is the
**exact history-free scalar revaluation of the wallet** — requirements 2–5
together with the commutation test. What does **not** fail, and is not claimed
to: current-field settlement at fixed `theta` (which always satisfies the author
axiom); exactness and closed-cycle closure of the reference-anchored coordinate of
Theory II; and static V1. **No alternative multi-dimensional wallet is proposed
here** — per the instruction, the boundary is stated instead.

**One consequence worth recording.** Because the admissible class is exactly the
set of field changes that alter no decision, a Dynamic EBU regulator that must
both (i) follow the current EBU sign and (ii) carry one history-free scalar
**cannot represent any field change that genuinely matters**. Any future
mechanism must give up one of: exactness of revaluation, the single scalar, or
history-freedom. Which to give up is a design question this report does not
answer and does not pre-empt.
