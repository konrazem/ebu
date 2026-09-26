# Dynamic EBU freedom-state theory — capacity as a current physical state function

**Subordinate to `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md`.** No programme
authority is claimed. This continues the four-part Dynamic EBU programme
(sufficient-state theory; differential forms; graph cohomology; dynamic field
geometry) and the companion study
`DYNAMIC_EBU_CAPACITY_SUFFICIENT_STATE_STUDY.md`. It does **not** rest on "a
forward wallet is sufficient"; that baseline is retained and is not the answer
given here.

**Pure mathematics.** No mechanism implemented. Study-1 not modified. The atomic
P-demand implementation not modified. Stage A/B not run. No history vector, no
source portfolio, no retroactive history reconstruction, no arbitrary viability
threshold, no monetary interpretation imposed. The only file changed is the
check module.

**Checks.** `dynamic_ebu_theory_checks.py` — **308 deterministic checks, 0
failures**, exact `Fraction`, tolerance literally zero, no randomized search.
The new section is tagged `FS-*`.

> **MODEL COORDINATE.** The `demand_driven_ebu` package was changed between
> passes: the physical-service predicate was strengthened to its **existential**
> form. Every figure below was computed against that current package — **91
> states, 408 menu edges (327 descending, 33 neutral, 48 ascending)**, `x*`
> reachable from all 91 and the unique absorbing state. Where this document
> quotes a count, the `FS-*` check is the authority.

---

## 0. The result

> **A current-state total freedom function exists, and its zero and scale are
> derived from physics rather than fixed by initialization.**

```
        F_total(x, theta)  =  W_max(theta, K)  -  V_theta(x)
```

where `K` is the declared physical data (the conserved total `M`,
nonnegativity, the declared reference `x*(theta)` and scales `sigma(theta)`),
and `W_max(theta, K) := max { V_theta(y) : y in the declared physical domain }`.

On the frozen Study-1 world `W_max = 48`, attained exactly at the three corners
`(12,0,0)`, `(0,12,0)`, `(0,0,12)`, and `F_total` is maximal exactly at `x*`
with value `48`. *(Checked: `FS-01`, `FS-02`.)*

**The scale is forced, not chosen.** Two axioms do it — (i) freedom is
non-negative on the physical domain (a reserve, not a debt), and (ii) the bound
is tight (no unphysical slack, hence no arbitrary viability threshold). Among
all constants `I` with `I - W >= 0` and `inf(I - W) = 0`, exactly one survives:
`I = W_max`. `I = 47` makes freedom negative at a physically realizable state;
`I = 49` leaves a gap nothing attains. *(Checked: `FS-03`.)*

**And this answers the central "what is constant in the world?" question by
separating two constants the programme has been running together.**

| | `I_dyn := C + W` | `I_phys := W_max(theta, K)` |
|---|---|---|
| value | `W(x_0)` — the initial burden | `max V_theta` over the declared domain |
| conserved under actor-only evolution | **yes** | **yes** |
| a function of the **present** state | **NO** | **yes** |
| analogy | total energy: a constant of the *motion*, fixed by initial data | a constant of the *world*, fixed by declared physics |

> **Theorem (§3.2).** `I_dyn` cannot satisfy the current-state requirement.
> `(3,6,3)` and `(0,6,6)` both reach `x*`, with `W = 3` and `W = 12`. Two worlds
> in the **identical** current state `x*` therefore carry `C = 3` and `C = 12`.
> No `F(x, theta, K)` equals `C`. *(Checked: `FS-13`.)*

> **Corollary.** `F_total` and `C` differ by the **constant** `W_max - W(x_0)`.
> They share every differential and every argmax, so `C + W = I`,
> `argmax C = argmin W` and `argmin W = {x*}` all transfer **verbatim**. Only
> the zero moves — from an initialization datum to a physical one. Golden
> requirement C is preserved *and* generalized. *(Checked: `FS-13`.)*

**Four results then follow, and two of them are negative.**

1. **Total is physical; distribution is not.** `F_total` is a state function;
   the per-owner shares are path-dependent (137 share diamonds) and are **not**
   localizable — of the 5 ownership partitions of the three stocks, exactly one
   supports every action's displacement, and it is the trivial single-owner
   block. §1, §10; checks `FS-12`.
2. **Condition A survives the whole Gaussian family.** `argmax F_theta =
   argmin V_theta = {x*(theta)}` for heterogeneous `sigma` and for moving `x*`
   alike — a strict improvement on the `theta_0`-anchored coordinate, which
   cannot track a moving reference at all. §8; check `FS-10`.
3. **`F_total` is a state function but NOT a sufficient statistic.** `(3,4,5)`
   and `(4,3,5)` carry the same `F`, yet one has a 2-plan menu with no
   strict-descent move and the other a 4-plan menu with one. The Nerode quotient
   is strictly *finer* than the level sets of `F`. §6; check `FS-06`.
4. **The identification `sum_i c_i = F_total` fails under genuine field
   change.** The same two actions on the same states accumulate `19/18`,
   `157/72` or `3` according to *when* `sigma -> (1,2,3)` occurs. §5.3; check
   `FS-08`. The defect vanishes exactly on the EBU-trivial class. Check `FS-09`.

**And the freedom/damage ambiguity is resolved by theorem, not rhetoric.**

> `F_total` is maximal **exactly** where the admissible action set is **empty**:
> `x*` is the unique absorbing state and the unique maximizer. A coordinate
> maximal precisely where nothing can be done does not measure available action.
> The coordinate that does is the dual `F_extract(x) = W(x)` — the maximum total
> EBU still extractable — and `F_total + F_extract = W_max` identically.
> *(Checked: `FS-07`.)*

---

## 1. Total freedom versus its distribution — PROVED

The proposed architecture is `F_total(x, theta)` together with shares `c_i`
summing to it. Both halves are now settled.

**Half 1 — the total is a state function.** `F_total = W_max - V_theta` is by
construction a function of `(x, theta, K)`. Along actor actions
`Delta F = -Delta W` on every one of the 408 menu edges, and increments add over
subdivisions of a path. *(Checked: `FS-05`.)*

**Half 2 — the distribution is not.** The share diamond of the companion study
survives the model change: two menu-legal histories from `(3,6,3)` to `x*`, one
through `(4,3,5)` and one through `(5,3,4)`, give **every** owner the same
balance under `sigma = (1,1,1)` (`+2` and `+1`) and different balances when
repriced to `sigma = (1,2,3)` (`7/8` vs `31/72`; `13/72` vs `5/8`). The graph
carries **137** such diamonds. *(Checked: `SS-01`–`SS-06`.)*

**Half 3 — and it is not repairable by locality.** §10 proves that a
state-determined *local* share rule requires every action's displacement to lie
inside one ownership block. On the Study-1 transfer network only the trivial
single-owner partition qualifies. *(Checked: `FS-12`.)*

> **THEOREM (separation).** The physical total is a state function of the
> present state; the ownership distribution is mechanism/accounting state and is
> irreducibly path-dependent on any connected transfer network. **Proved, both
> directions.**

This is the exact form of the evidence the task points at, and it is now a
theorem rather than a suggestion: what the share diamond measures is not a
defect in the physics but the fact that **ownership is not a physical
observable**.

---

## 2. The current-state requirement — discharged

`F_total = W_max(theta, K) - V_theta(x)` depends on:

| input | admissible? |
|---|---|
| current physical state `x` | yes — required |
| current field `theta` (through `x*(theta)`, `sigma(theta)`) | yes — required |
| conserved total `M`, nonnegativity, dimension | yes — declared physical invariants |
| actor action history | **not used** |
| old fields | **not used** |
| source provenance | **not used** |
| receipt vectors | **not used** |
| hidden path variables | **not used** |

Two histories arriving at the same full current physical state with the same
invariants produce the same `F_total` — immediately, because `F_total` is
*defined* as a function of those arguments. The content of this section is not
that definition but §3's theorem that **no such definition can reproduce `C`**,
and §0's corollary that it reproduces everything about `C` except its zero.

---

## 3. Static recovery, and what `I` actually is

### 3.1 Exact recovery at the reference field

At `theta_0` with `W := V_{theta_0}` under the accepted normalization,

```
F_total + W  =  W_max  =  I_phys ,
```

identically on the declared domain, by construction. `argmax F_total =
argmin W = {x*}` for the reference Gaussian with reachable `x*`, so golden
requirements C and D hold exactly. *(Checked: `FS-02`.)*

### 3.2 The two constants, and why only one is physical

The programme's invariant is `I_dyn = C + W`. With balances opened at `beta_i`
and the world at `x_0`, telescoping gives

```
I_dyn  =  sum_i beta_i  +  W(x_0) .
```

> **Theorem I-1 (`I_dyn` is option A, and unavoidably so).** `I_dyn` is a
> constant of the motion but is **not** determined by the present state. Witness:
> `(3,6,3)` and `(0,6,6)` both reach `x*` under the implemented rule, with
> `W = 3` and `W = 12`. Two worlds in the identical current state `x*` carry
> `C = 3` and `C = 12`. Hence no function of `(x, theta, K)` equals `C`.
> *(Checked: `FS-13`.)*

*Why this is unavoidable, not an artifact.* `C` is defined as an **accumulated**
quantity — the running sum of settled receipts. Its value at `x` records the
burden *already shed*, which is a fact about where the world started, not about
where it is. Any accumulator has this property; it is the defining difference
between a constant of the motion and a state function.

> **Theorem I-2 (`I_phys` is option B, and is unique).** Among constants `I` for
> which `F := I - W` satisfies (i) `F >= 0` on the declared physical domain and
> (ii) `inf F = 0`, there is exactly one: `I = max_domain W`. On Study-1 that is
> `48`. *(Checked: `FS-01`, `FS-03`.)*

*Proof.* (i) forces `I >= max W`; (ii) forces `I <= max W`. ∎

**Axiom (i)** is the statement that freedom is a reserve, not a debt — it is what
makes the coordinate a *freedom* rather than a *burden*. **Axiom (ii)** is
exactly the task's prohibition on an arbitrary viability threshold: any
`I > max W` would declare a floor no physical state ever reaches, which is a
threshold smuggled in as a constant. The scale is therefore **derived from the
physical domain**, and the constraint `F >= 0` is not an extra gate — it is the
domain boundary itself.

### 3.3 The relation between the two

```
F_total(x)  =  C(x)  +  [ W_max - W(x_0) - sum_i beta_i ]
```

— a constant. `dF_total = dC`, `argmax F_total = argmax C`, and every proved
fixed-field result carries over unchanged. *(Checked: `FS-13`.)* The bracket is
the actors' **derived initial endowment**: the theory says what the opening
balances must sum to, instead of leaving it free.

> **Answer to §3.** `I` is **both** things, and conflating them is the error.
> The accounting invariant is option **A** and provably cannot be option B. The
> freedom-state theory does not need it: it uses `I_phys = W_max`, which is
> option **B**, derived from the declared physics, and which differs from the
> accounting constant only by the endowment.

---

## 4. Physical invariant search

Systematic search over the invariants the declared EBU ontology actually
supports.

| candidate | status on the declared physics |
|---|---|
| **conserved material total `M`** | **available.** Every declared route is a transfer, so `sum_i x_i` is conserved |
| **stoichiometric / graph invariants** | the four routes span a rank-2 displacement space, so the annihilator is **one-dimensional**: `M` is the **unique** linear conserved charge. There is no second invariant to fix a scale. *(Checked: `FS-04`.)* |
| **physical energy / Hamiltonian constants** | **unavailable.** EBU declares no kinetic term, no symplectic form, no time parameter and no equation of motion. `V_theta` is a declared burden field, not a Hamiltonian, and calling it energy would be an identification without a derivation |
| **Noether invariants** | **unavailable.** Noether requires a declared *continuous* symmetry of a declared action functional. EBU declares neither. The cell-permutation symmetry present when `x*` and `sigma` are uniform is **discrete**, and discrete symmetries yield no Noether current |
| **`W(x_0)`** | conserved, but **initial data**, not present data (Theorem I-1) |
| **`W_max(theta, K)`** | **available and derived**: a function of `M`, nonnegativity, `x*(theta)` and `sigma(theta)` alone |

> **`I = Phi(physical conserved quantities, field parameters)` is derivable, and
> the derivation is `Phi = max V_theta` over the domain cut out by the conserved
> charge.** Explicitly, `I_phys` is a function of `(M, x*(theta), sigma(theta))`
> through the constrained maximization — for Study-1 it is attained at a corner
> of the simplex, giving `48` at the reference field, `314/9` at
> `sigma = (1,2,3)`, `157392/1225` at `sigma = (5,1/2,7)` and `76` at
> `x* = (2,4,6)`.

**What physical datum would be missing if one insisted on `I_dyn` instead.** A
record of the initial state `x_0`. That is precisely a history datum, and it is
the single piece of information the architecture forbids. So the prohibition on
history is not merely compatible with the freedom-state theory — **it is what
forces `I_phys` and therefore fixes the scale.**

---

## 5. Differential / state-function formulation

### 5.1 The canonical split

`F_total` is a function of `(x, theta)`, so its differential splits canonically,
because actor actions move `x` at fixed `theta` and field events move `theta` at
fixed `x`:

```
dF_total  =  -dV_theta |_x          (actor part)
             +  [ d W_max(theta) - (partial V_theta / partial theta) ] dtheta
                                     (field part)
```

The actor part is exactly the negative of the current EBU one-form, so along an
actor action `Delta F = E_theta(G)` — **an identity, not an analogy** (§12, Q6).
The field part is a field contribution and is never an actor reward, preserving
the required separation *what the actor did ≠ what happened to the world*.

### 5.2 Exactness

`dF_total` is an exact current-state differential **unconditionally**, because
`F_total` is defined as a function of the state. The non-trivial content is that
the **actor part alone** is exact — it is `-dV_theta`, the differential of a
declared potential — and hence closes on cycles. `Delta F = -Delta W` on all 408
menu edges, and increments add over every two-step subdivision. *(Checked:
`FS-05`.)* Golden requirement F (atomic/refinement invariance) holds.

### 5.3 Where it breaks — and this is the decisive obstruction

The identity `sum_i c_i = F_total` is a *different* demand from exactness of
`dF`, and it fails.

> **Theorem D (field defect).** Under actor-only evolution at fixed field, the
> aggregate settled wallet equals `F_total` up to the constant endowment. Under a
> **mid-history field change** it does not: the accumulated aggregate is
>
> ```
> sum_k [ V_{theta_k}(x_k) - V_{theta_k}(x_{k+1}) ]
> ```
>
> which depends on **when** the field changed relative to the actions.

*Exact witness.* Two actions `(3,6,3) -> (4,3,5) -> (4,4,4)` with
`sigma -> (1,2,3)` inserted before both, between them, or after both:

| insertion point | accumulated aggregate |
|---|---|
| before both actions | `19/18` |
| between the two actions | `157/72` |
| after both actions | `3` |

*(Checked: `FS-08`.)* Three different totals for the same endpoints.

> **Theorem D' (exactly when the defect vanishes).** The accumulated aggregate is
> endpoint-determined **iff** every field change satisfies
> `V_{theta'} = V_theta + const` on each reachable component — i.e. iff no field
> change alters any EBU value.

*Witness of the trivial class.* Moving `x*` from `(4,4,4)` to `(5,5,5)` shifts
`V` by the constant `3/2` at every one of the 91 states, and all three insertion
orders then accumulate `3`. *(Checked: `FS-09`.)*

**The one escape, and why it is blocked.** One could *define* the settlement as
`Delta F` including the field part, making `sum_i c_i = F_total` true by
construction. That credits field revaluation to actors, violating the retained
requirement that field revaluation is a field contribution and never an actor
reward — and violating the author axiom, since an action the current field
prices as negative could then earn positive capacity. The escape is closed by
the golden requirements, not by preference.

**What the residue is.** Write `L := F_total - sum_i c_i`. Then `L` is a
**single world-level scalar** carrying the accumulated field defect. It is not a
history vector, not per-actor, and not per-source — but it is honestly not a
state function either. **The architecture therefore contains exactly one scalar
of irreducible memory, located at the field ledger and nowhere else.**

---

## 6. The four-stage information-theoretic question

Applied to `F_total`, not to a wallet, using deterministic state equivalence
(Myhill–Nerode) where it genuinely applies.

**Stage 1 — is `F_total` a sufficient current-state statistic for the physical
freedom available to the whole system?**

> **No.** `F_total` is a *state function* but its level sets are strictly coarser
> than the Nerode partition of the transition system. `(3,4,5)` and `(4,3,5)`
> have `W = 1`, hence identical `F`, yet `(3,4,5)` has a 2-plan menu with **no**
> strict-descent move while `(4,3,5)` has a 4-plan menu with one. Equal freedom,
> non-isomorphic futures. *(Checked: `FS-06`.)*

**Stage 2 — is the physical state `x` sufficient?** Yes, trivially and by
construction: the menu is re-derived from `x`.

**Stage 3 — are `{c_i}` sufficient to distribute and use that freedom?**

> **At fixed field, yes** — aggregate closure is exact and each gate is a
> function of `(c_i, r_i)`. **Under field change, no**, by Theorem D.

**Stage 4 — sufficiency versus minimality, kept apart.** The two failures point
in *opposite* directions and must not be merged:

| object | relation to the Nerode partition | verdict |
|---|---|---|
| `F_total` | strictly **coarser** | **sub-sufficient** — it forgets what the physics needs |
| `c_i` | strictly **finer** (every settlement is an integer, so the fractional part is never read) | **super-sufficient** — it remembers what nothing can use |
| `x` | equal, by construction | sufficient and minimal for the physics |

> **The freedom coordinate and the wallet fail the same test in opposite
> directions, and neither failure is the other's fix.** This is the precise
> reason the task's warning — do not confuse sufficiency with minimality — is
> load-bearing here.

---

## 7. Topological exactness

Let the freedom change on an edge be `Delta F(e) = F(y) - F(x)`.

**Exactness holds.** `Delta F = -Delta W` on all 408 menu edges, so the freedom
cochain is the coboundary of `-W` and every physically closed actor cycle
settles to exactly zero. *(Checked: `FS-05`.)*

**And the cycle space is genuinely non-trivial**, so this is a real constraint:
the underlying undirected action graph is connected with 91 vertices and 344
edges, giving first Betti number `344 - 91 + 1 = 254`. *(Checked: `SS-12`.)*

**But topology does not choose `F`, and must not be allowed to.** Cohomology
determines a cochain's potential only **up to `H^0`**, which for a connected
graph is exactly `R` — one additive constant. Topology is therefore silent on
precisely the question §3 asks. The gauge is fixed by physics:

> **`H^1 = 0` (exactness) gives the cochain; `H^0 = R` is the residual gauge;
> Theorem I-2 fixes that gauge by the physical domain.** Topology supplies the
> differential structure, physics supplies the zero. Neither alone determines
> `F_total`.

---

## 8. Dynamic field geometry

For `V_theta(x) = 1/2 sum_i ((x_i - x*_i(theta))/sigma_i(theta))^2` and
`F_theta = W_max(theta) - V_theta`, keeping the three conditions strictly apart:

> **A** same equilibrium; **B** same local action ordering; **C** same
> magnitudes.

> **Theorem G (condition A is preserved by the whole family).** Since
> `V_theta >= 0` with equality exactly at `x*(theta)`, `argmax F_theta =
> argmin V_theta = {x*(theta)}` whenever `x*(theta)` is reachable, for **every**
> positive scale vector and **every** reference position.

| field change | `argmax F_theta` | condition A |
|---|---|---|
| `sigma = (1,2,3)`, fixed `x*` | `{(4,4,4)}` | **holds** |
| `sigma = (5, 1/2, 7)`, fixed `x*` | `{(4,4,4)}` | **holds** |
| `x*` moved to the reachable `(2,4,6)` | `{(2,4,6)}` | **holds — and tracks** |
| `x*` moved off-slice to `(5,5,5)` | `{(4,4,4)}` | **holds**; the shift is EBU-trivial (`V` moves by the constant `3/2`) |

*(Checked: `FS-10`, `FS-09`.)*

> **This is a strict improvement over the `theta_0`-anchored coordinate.** A
> coordinate anchored to the reference field cannot track a moving `x*` at all —
> its maximum stays at the old equilibrium while the physics has moved.
> `F_theta` follows the current field by construction, which is exactly what
> golden requirement B (freedom is *current* physical freedom) demands.

**B and C are not required and generally fail.** `B` fails wherever the two
fields disagree on an edge's orientation; `C` fails outside uniform rescaling
(for `n >= 3`, `V_{theta'} = qW + const` forces `H_{theta'} = q H_0`). Per the
task, neither is demanded merely because `A` is wanted. **The freedom-state
theory needs only `A`, and `A` it has, unconditionally.**

**Conservation-slice and dimension effects.** The projection onto `1^perp` is
what produces the centred criterion; `dim A_x = 1` (two cells) makes rank-one
automatic but **not** the orientation condition. Neither affects `A`.

---

## 9. Entropy connection — answered by theorem

No claim is made that `F_total` is thermodynamic entropy. The structural
properties that motivated the analogy are tested one at a time.

| structural property | `F_total` | verdict |
|---|---|---|
| determined by the current macrostate | yes, by construction | **MATCH** |
| path independent | yes — coboundary of `-W`, zero circulation on all 254 independent cycles | **MATCH** |
| history free | yes — no history, source or receipt input | **MATCH** |
| extremized at equilibrium | yes — maximal exactly at `x*` | **MATCH** |
| compatible with local/atomic transitions | yes — refinement invariant, increments telescope | **MATCH** |
| concave / has a genuine maximum principle | yes — `W` is strictly discretely convex along every transfer direction, so `F` is strictly concave | **MATCH** |
| **monotone along accessibility** (a second law) | **no** — 48 of 408 menu edges strictly decrease `F` | **FAIL** |
| **additive over subsystems** | **no** across a shared conservation law: joint `W_max = 48` while the product domain at `M_A = 4`, `M_BC = 8` gives `16` | **FAIL** |

*(Checked: `FS-11`.)*

> **THEOREM (entropy-likeness, exactly bounded).** `F_total` is entropy-like in
> six structural respects and fails exactly two. It is a **strictly concave
> state potential with a maximum principle** — structurally a Massieu-type
> potential — but it is **not** a Lyapunov function, because 48 admissible
> actions decrease it, and it is **not** extensive, because the conservation law
> that defines the domain is precisely what couples the subsystems.

**The two failures are not repairable by a better choice of `F`.** Monotonicity
would require the action generator to be `W`-nonincreasing, which is a
declaration about the menu, not a property of any coordinate. Additivity would
require the domain to be a product, which conservation forbids. Both are
properties of the *world*, not of the coordinate — which is why the answer is a
theorem about `F_total` and not a search for a different `F`.

---

## 10. Local actor shares — necessary and sufficient conditions

Suppose `F_total` is a physical state function. When can it be distributed as one
scalar per actor with `sum_i c_i = F_total`, preserving decentralized autonomy,
locality, exact aggregate closure and no history vector?

> **Theorem S-loc.** A **state-determined local** share rule
> `c_i = phi_i(x_{S_i})` over an ownership partition `{S_i}`, satisfying
> `sum_i phi_i = F_total` and reproducing the declared common-path receipt
> (`phi_i(post) - phi_i(pre) = r_i`) for every admissible action, exists **iff**
>
> (a) `W` is exactly additive over the partition, **and**
> (b) every admissible action's displacement is supported inside a single block.

*Proof sketch.* (⟸) Under (a) set `phi_i = (W_max)_i - sum_{alpha in S_i}
w_alpha` with the block maxima summing to `W_max`; under (b) each action changes
only its own block's terms, so the receipt matches. (⟹) If some action's support
crosses blocks, the common-path receipt attributes to the acting owner a change
in another owner's coordinates, which no function of the actor's own block can
reproduce. ∎

**On the Study-1 network, (b) forces the trivial partition.** The routes are
`A<->B` and `B<->C`, so the blocks would have to contain `{A,B}` and `{B,C}` —
hence `{A,B,C}`. Of the five partitions of the three stocks, exactly one
qualifies, and it is the single-owner block. *(Checked: `FS-12`.)*

> **Answer to §10 — it is not (A), and it is not (C).**
>
> - **Not (C).** The path dependence is **not** removable by any physically local
>   share rule on a connected transfer network. Condition (b) fails as soon as
>   two owners can trade, which is the entire point of the economy.
> - **Not (A) either**, if "harmless" is read as "the shares are physical". They
>   are not: two histories with identical physics assign different shares.
> - **It is (B) restricted to the right object.** It is a **fatal obstruction to
>   any claim that `c_i` is a physical quantity**, and **harmless to the
>   physics**, because the total — the only part the physics determines — is a
>   state function regardless.

**Consequence for the architecture.** `F_total` is physical and decentralizable
in the sense that every actor can evaluate it from local current data; the
*split* is a declared accounting convention with genuine freedom in it. That
freedom is not a defect to be engineered away — §1 proves it cannot be — and it
is the exact formal content of the synthesis's "settlement determines how that
freedom is distributed among autonomous actors."

---

## 11. Freedom versus damage potential

The ambiguity is stated in the programme as: `C = I - W` supports both "reserve /
freedom" and "stored damage potential". The resolution here is structural.

> **THEOREM (anti-correlation).** On the frozen Study-1 world:
>
> - `F_total = W_max - W` is maximal **exactly** at `x*`, and `x*` is the
>   **unique absorbing state** — its admissible action set is empty;
> - `F_extract(x) :=` the maximum total EBU still extractable from `x` equals
>   `W(x)` exactly, because `x*` is reachable from all 91 states;
> - `F_total + F_extract = W_max` identically.
>
> *(Checked: `FS-07`.)*

So the two readings are **not two valences of one quantity**. They are **two
different state functions**, and they are exact complements:

| quantity | maximal at | operational meaning |
|---|---|---|
| `F_total = W_max - W` | `x*`, where **nothing can be done** | burden already shed — **banked restoration** |
| `F_extract = W` | the corners, where the world is worst | work still available — **capacity to act** |

> **The distinguishing axiom, stated exactly.** It is the choice of what
> "freedom" is *for*: a coordinate maximal where the action set is empty measures
> **what has been accomplished**; a coordinate maximal where the action set is
> richest measures **what may yet be done**. Golden requirement C
> (`argmax C = argmin W`) **selects the first**. That is a declaration, it is the
> programme's, and it is coherent — but it entails that `C` and `F_total` do not
> measure available action, and the "stored potential" reading is therefore not
> a rhetorical gloss but the literally correct description of what the
> mathematics selects.

**Does the current-state construction make "freedom" objective?** **Partly, and
the part matters.** `F_total` is now objective in three respects the accounting
coordinate was not: its value is a function of present physics, its zero is fixed
by the physical domain rather than by initialization, and its maximum tracks the
current field. What the construction does **not** do is make `F_total` a measure
of available action — §11's theorem forbids that — nor make the shares `c_i`
physical — §10 forbids that. **Objectivity is achieved for the total and denied
for the distribution**, which is the same separation §1 proves.

**And the V1 spendability test sharpens.** 48 of the 408 menu edges strictly
increase `W`, funded out of an existing balance under the V1 gate. Under the
current model that is 48 explicit witnesses that the licence to move away from
equilibrium is real, against 4 in the previous model — the model change
strengthened the finding.

---

## 12. Decisive output

**Q1. Does a current-state total freedom function `F_total` exist?**
> **Yes.** `F_total(x, theta) = W_max(theta, K) - V_theta(x)`, with
> `W_max = max V_theta` over the domain cut out by the conserved charge. It
> satisfies every golden requirement: `E_theta` unchanged (A), it is current
> physical freedom (B), `F + W = I` with `argmax F = argmin W` (C),
> `argmin W = {x*}` (D), no history (E), refinement invariant (F).

**Q2. Is `F_total` determined by present physics only?**
> **Yes** — and the sharp content is the accompanying impossibility: the
> programme's accounting invariant `I_dyn = C + W = W(x_0)` is **not**, and
> cannot be made so. `(3,6,3)` and `(0,6,6)` both reach `x*` with `W = 3` and
> `12`. `F_total` and `C` differ by a constant, so nothing proved about `C` is
> lost.

**Q3. What physical invariant fixes its zero and scale?**
> `W_max(theta, K)`, the constrained maximum of the current burden over the
> physical domain — a function of the conserved total `M`, nonnegativity,
> `x*(theta)` and `sigma(theta)`. It is **unique** given two axioms: freedom is
> non-negative on the domain, and the bound is tight. `M` is the **only** linear
> conserved charge the declared physics supplies, and no Hamiltonian or Noether
> invariant is available without declaring structure EBU does not have.

**Q4. Is `F_total` maximal exactly at the current physical equilibrium?**
> **Yes**, for the entire Gaussian family, fixed or moving `x*`, homogeneous or
> heterogeneous `sigma`. And the honest corollary: that is exactly what makes it
> the *banked* rather than the *available-action* coordinate, since `x*` is the
> unique absorbing state.

**Q5. Can one scalar `c_i` per actor distribute `F_total` without history?**
> **At fixed field, yes**, exactly. **Under genuine field change, no**: the
> accumulated aggregate is not endpoint-determined (`19/18`, `157/72`, `3`), and
> the identity survives only on the EBU-trivial class. The residue is **one
> world-level scalar** — a field ledger, not a history vector, not per-actor, not
> per-source. Separately, the **shares are never physical**: 137 share diamonds,
> and locality cannot remove them on a connected network.

**Q6. What is the exact role of `E_theta` relative to `Delta F`?**
> **Identity, not analogy.** Along an actor action at fixed field
> `Delta F_total = E_theta(G)` exactly; `E_theta` **is** the actor part of the
> one-form `dF_total`. The field part
> `[dW_max - partial_theta V_theta] dtheta` is disjoint from it and is never an
> actor reward. The canonical split exists because actor events move `x` at fixed
> `theta` and field events move `theta` at fixed `x`.

**Q7. Which dynamic Gaussian families preserve the theory?**
> **All of them preserve `F_total` and condition A** — every positive
> `sigma(theta)`, fixed or moving `x*`, on-slice or off. Condition **B** fails
> generically and **C** only outside uniform rescaling; neither is required. The
> identification `sum_i c_i = F_total` is preserved exactly on the **EBU-trivial
> class** `V_{theta'} = V_theta + const` (which includes reference motion along
> `span(sigma_i^2)`) and on **no larger class**.

**Q8. What exact obstruction appears when the theory fails?**
> **The field defect** `L = F_total - sum_i c_i`, whose non-vanishing is
> necessary and sufficient for failure of the wallet identification, and which is
> nonzero iff some field change alters an EBU value. Two further exact
> obstructions, both independent of it: the **Nerode gap** (`F_total`'s level
> sets are strictly coarser than the physics requires — `(3,4,5)` vs `(4,3,5)`)
> and the **ownership gap** (shares are path-dependent and not localizable).

### What this pass changes in the programme record

| row | change |
|---|---|
| `C + W = I`, `argmax C = argmin W` | **preserved and generalized**: same differentials, same argmax, with the zero moved from initialization to `W_max` |
| "what is the invariant `I`?" | **answered and split**: `I_dyn` is an accounting constant of the motion and provably not a state function; `I_phys = W_max` is derived from physics |
| the share diamond | **upgraded to a theorem** (§1): total physical, distribution accounting — and §10 proves locality cannot repair it |
| freedom vs stored damage potential | **resolved structurally** (§11): two complementary state functions with `F_total + F_extract = W_max`, not one quantity with two valences |
| "is capacity entropy-like?" | **bounded exactly** (§9): six structural properties match, two fail, and both failures are properties of the world rather than of the coordinate |
| — | **new**: the field defect `L` — exactly one world-level scalar of irreducible memory, and no more |

---

## 13. FINAL VERDICT

```
DYNAMIC EBU FREEDOM-STATE THEORY VALID ONLY FOR [ the TOTAL, where it is fully
derived: F_total(x,theta) = W_max(theta,K) - V_theta(x) is a current-state
function whose zero and scale are forced by the conserved charge and the
declared field, preserving C + W = I and argmax F = argmin W for the entire
Gaussian family, fixed or moving x*.  It does NOT extend to the DISTRIBUTION:
per-actor shares are path dependent (137 share diamonds) and are not localizable
on any connected transfer network, so no c_i is a physical quantity.  And the
identification sum_i c_i = F_total holds exactly at fixed field and, across a
field change, exactly on the EBU-trivial class V_theta' = V_theta + const on each
reachable component -- outside it the aggregate is not endpoint determined
(19/18, 157/72, 3) and exactly one world-level scalar of irreducible memory, the
field ledger, separates the wallet from the physics ]
```

END TASK.
