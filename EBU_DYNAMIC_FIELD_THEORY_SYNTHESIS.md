# EBU dynamic field theory — canonical synthesis, the freedom–equilibrium theorem, and Study-1 accessibility

**This document replaces the Theory I / II / III sequence as programme
authority.** Those three files and the two audit files remain readable as
working history; where they conflict with this document, **this document
governs**. No parallel "Theory IV" is created, and this pass creates none.

Pure theory consolidation and exact structural enumeration. No simulation, no
model redesign, no new mechanism, no `Lambda`, no history vectors, no source
portfolios, no global planner, no Stage A and no Stage B.

**What executed.** Static structural enumeration only: pure functions of
synthetic individual states (`can_happen_now`, `global_progress`,
`physically_serviceable`, the potential). No `EconomyRun`, no actor policy, no
arrival law, no RNG, no trajectory. No file in `demand_driven_ebu`,
`gaussian_harness`, `capacity_v2` or `homeostasis` was modified.

**STATUS UPDATE (implementation pass, revised).** The atomic P-demand semantics
analysed in §11 has since been **adopted and implemented** in
`demand_driven_ebu`, and recorded as finding **F-7** in
`DEMAND_DRIVEN_MODEL_FINDINGS.md`. A follow-up audit then strengthened the rule
to its **existential** form — progress on *at least one* pre-state P-demand,
never on every one of a coupled component — because the "every one" reading
still broke sequential refinement. §11's analysis is unaffected in substance;
its accessibility table is superseded by the recomputed one in F-7 and in
`DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` §0, where `x*` remains the only
absorbing state, reachable from all 91 states in at most five
burden-nonincreasing steps. The theory in
this document is unchanged by that; what changed is that the "candidate"
column of §11 and §12 is now the model. The withdrawn complete-service
enumeration is retained here and is reproduced from first principles in the
check module, because it is the evidence for the change. Cross-references:
contract §2.1 and §3, `DEMAND_DRIVEN_STUDY_ONE_DOMAIN.md` conditions 13/13a/14,
and `DEMAND_DRIVEN_STUDY_ONE_READINESS.md`.

Checks: `dynamic_ebu_theory_checks.py` — **288 deterministic checks, 0 failures**,
exact `Fraction`, tolerance literally zero, **no randomized search anywhere**
(the last seeded sampling check, `SY1`, was replaced in this pass by an
exhaustive edge-and-two-step enumeration).

---

## 1. Notation (frozen)

| symbol | meaning |
|---|---|
| `V_theta(x)` | current physical EBU burden field |
| `E_theta(G) = V_theta(pre) - V_theta(post)` | current exact work-like EBU of action `G` |
| `W(x)` | normalized / reference burden coordinate |
| `c_i` | actor `i`'s persistent normalized freedom coordinate |
| `C = sum_i c_i` | aggregate distributed freedom |
| `r_i` | per-owner common-path receipt, where one is genuinely needed |
| `x*` | declared reference state of the field |
| `M` | conserved resource total |

Sign convention throughout: *before minus after*. Accordingly
`Delta c = W(before) - W(after)`, and in differential form **`dc = -dW`**.

**The Study-1 world, used wherever "the actual graph" appears.** Three stocks in
a line `A <-> B <-> C`; one homogeneous resource; references `x* = (4,4,4)`,
scales `sigma = (1,1,1)`, conserved total `M = 12`; four routes (`A->B`, `B->A`,
`B->C`, `C->B`) of capacity 6; declared quanta `{1, 2}`; a plan uses each route
at most once. That gives **91 integer states** and a complete plan space of
**80**. `A` and `C` are **not adjacent**. This is `fixtures.study_one_world()`,
and `study_one.require_domain` accepts it.

---

## 2. Authority map

### RETAIN

| result | statement |
|---|---|
| current EBU | `E_theta = V_theta(pre) - V_theta(post)`, exact for finite actions |
| path form | `E_theta` equals the corresponding current-field path integral; receipts are `r_i = -∫ grad V_theta . delta_i` along the common path, summing to `E_theta` |
| static V1 | exact at the declared reference field: with `W = V_{theta_0}` and unit normalization, `Delta c = E_{theta_0}`, **including per-owner receipts** |
| aggregate closed cycles | at fixed field, actor-only closed cycles settle to zero in aggregate |
| same-ruler cancellation | multiplying wallet and cost by one positive factor changes no affordability decision |
| variable local normalizers | they live **inside** receipt integrals, never as an endpoint divisor |
| **freedom–burden invariant** | `I := C + W` invariant under actor-only evolution; `C = I - W`; `argmax C = argmin W` (§3) |
| **equilibrium location** | for the reference Gaussian with `x*` a reachable lattice point, `argmin W = {x*}` uniquely (§4) |
| **local-to-global on the complete lattice** | Theorem H3: separable convex `W` on `{x >= 0, sum x = M}` with **all** unit-transfer edges has every local minimum global (§9) |

### RETAIN WITH CORRECTED HYPOTHESIS

| result | correction |
|---|---|
| canonical normalization | `W := V_{theta_0}` is canonical **up to `aW + b`, `a > 0`**, forced by exact static-V1 recovery on each connected reachable component. A mathematical candidate, not an adopted mechanism |
| level-set compatibility | the **finite** condition `W_alpha(u) = W_alpha(v) => V_{alpha,theta}(u) = V_{alpha,theta}(v)` replaces the too-weak infinitesimal version |
| factorwise normalization | valid as a construction; factor **refinement** is legitimate only when both the reference and the current potential are exactly additive under it — genuine cross terms may not be discarded. **And a relation between two *total* potentials on a conservation slice never descends to the declared factors without its own proof** (§14) |
| directed-graph exactness | strong connectivity is **sufficient**, not necessary; the general criterion is equality of settlement sums over all paths with common endpoints |
| off-slice Gaussian alignment | when `x*` is off the reachable domain, alignment is **no longer guaranteed**; it does not *necessarily* fail. The affine-slice, integer-lattice and nonnegativity-constrained minimizers are three different objects (§8, §13) |
| sign-faithful scalar settlement | does **not** require uniform scalar rescaling on a finite domain; what forces uniformity is the additional demand that `W`-ties stay ties (§13) |

### SUPERSEDED

- Theory I's Theorem DS (existence of *some* ordering): it answers the wrong
  question. Canonicality, not existence, is what a settlement coordinate needs.
- Theory I's L2 (acyclicity after contraction): redundant, since each `V_theta`
  is already a state function.
- Theory II's presentation of factorwise normalization as a completed **dynamic
  regulatory** mechanism: it is anchored to `theta_0` and therefore tracks the
  reference field's sign (§7).
- **This pass:** the previous Corollary H4, "on the Study-1 Gaussian transfer
  graph any strictly freedom-increasing trajectory terminates at a global
  `W`-minimum, and at `x*` when `x*` is a reachable lattice point." **Withdrawn.**
  It applied Theorem H3, which is about the *complete* unit-transfer lattice, to
  the Study-1 action graph, which is neither complete nor a unit-transfer
  lattice: `A` and `C` are not adjacent, quanta are `{1, 2}`, and — decisively —
  a plan enters an actor's menu only if it *completely serves* a currently
  derived demand and is irredundant. §10 gives the exhaustive replacement.

### DISPROVED

| claim | counterexample |
|---|---|
| L3 factor-additivity is necessary for factor-locality | two declared factors with every action touching both: locality restricts nothing, yet no additive `W` exists |
| edge-sign compatibility characterizes global representability | the chain `a–b–c–d` with `W = (9/4, 1/4, 1/4, 9/4)`, `V = (9/2, 1/2, 1/2, 5/2)` |
| `dc = dW` | integrating gives `W_after - W_before`; the correct sign is `dc = -dW` |
| refinement invariance proves path independence | refinement invariance gives **additivity over subdivisions of one path**; it does not by itself compare two distinct paths with the same endpoints |
| a strictly increasing `f` has `f' > 0` | `f(w) = w^3` at `w = 0` |
| exact history-free revaluation of the wallet across a field change | two actions with the same old receipt `5` need new receipts `17/9` and `19/8`; one scalar cannot hold both |
| **convexity of `W` on the complete lattice gives convergence on the Study-1 graph** | **36 of the 91 Study-1 states are absorbing away from equilibrium under the frozen complete-service rule (§10)** |
| **with two cells even condition D holds for unequal `sigma`** | **the four-edge 2-cell world of §13: the covector ratio is `3/8, -1/8, 11/8, 7/8` — not constant, and not even of constant sign** |

### REJECTED — OUT OF SCOPE

History-vector architectures: source portfolios, per-action dependency records,
field-history vectors, global future optimization. Theory III shows exact
current-field wallet revaluation *would* require exactly this information; that
is why such revaluation is **not** part of the retained architecture.

### ADOPTED SINCE (implementation pass)

**Strong** atomic P-demand semantics (§11, strengthened). Implemented in
`demand_driven_ebu.service`, recorded as finding F-7, documented in contract
§2.1, §3 and §4, and carried by permanent regressions at `(5,4,3)`, `(2,6,4)`,
`(1,4,7)` and `(0,6,6)` plus the 91-state accessibility oracle. Economic
service is unchanged and remains complete-service only; contract §6 protection
of an existing physical need moved to a separate coexistence question.

### OPEN / EXPERIMENTAL

Whether actor policies actually follow the `W`-nonincreasing paths that exist.
That is the **policy-dynamics** question, it is empirical, and it belongs to
Stage A/B. Nothing in this document asserts or predicts it.

---

## 3. The freedom–burden invariant — RETAINED, unchanged

**Hypotheses.** (i) exact aggregate normalized settlement
`Delta C = W(x_before) - W(x_after)`; (ii) actor-only evolution — no external
physical injection and no field change; (iii) no process burdens; (iv) `W`
evaluated on one reachable component.

**Theorem F1.** `C_after + W(x_after) = C_before + W(x_before)`.

*Proof.* `C_after = C_before + Delta C = C_before + W(before) - W(after)`;
move `W(after)` to the left. ∎

**Corollary F2.** `I := C + W` is invariant under actor-only evolution, hence

```
C = I - W          and therefore          argmax C = argmin W .
```

*(Checked: `SY1` — exhaustively over every edge and every directed two-step walk
of the declared lattice, and symbolically against three opening balances. This
replaces the 500 seeded random walks of the previous revision: sampling cannot
establish an identity.)*

**This is not a new identity.** It is the programme's existing exchange
invariance `V + sum_i B_i = J` written in normalized coordinates. §5 says why
that matters.

**This result is not weakened by anything below.** The accessibility correction
in §10 concerns *where the physics can go*, not *where the maximum is*.

---

## 4. Gaussian equilibrium — RETAINED

For the reference field `W(x) = 1/2 sum_i ((x_i - x*_i)/sigma_{i0})^2` on the
declared reachable manifold:

- **`W >= 0`**, with equality exactly at `x = x*`;
- **if `x*` is reachable, `min W = 0` is attained there**;
- **uniqueness:** `W` is a strictly convex quadratic, so on a *convex* reachable
  set the minimizer is unique. On a **lattice** the minimizer is unique whenever
  `x*` is itself a reachable lattice point; if it is not, the minimizers are the
  nearest balanced states and may be several.

*(Checked: `SY2`; and `S1-00` for the Study-1 world, where `x* = (4,4,4)` is a
reachable lattice point and `sum x = M = 12 = sum x*` at every state — so **no
Study-1 state is resource-short against the reference**.)*

**Corollary.** Under §3, aggregate freedom `C` is maximal exactly where `W` is
minimal; if the minimum is unique, `C` is maximal **iff** `x = x*`. No
behavioural claim is attached.

---

## 5. Entropy-like interpretation — and one warning that must not be lost

**Structural analogy only.** In thermodynamics an extremal principle
characterizes equilibrium under constraints; here a distributed state coordinate
`C` reaches its extremum where the burden coordinate `W` is minimal. `E_theta` is
the **process / work-like** valuation; `c` and `C` are the **persistent
state-coordinate** side. **`C` is not thermodynamic entropy**, `W` is not energy,
and no second law is claimed.

Nor are the signs of `E_theta` and `Delta c` forced to agree — §13 derives exactly
when they do.

**The warning.** `C = I - W` is the same equation the programme's own failure
analysis states as `P(t) = D - V(t)`, reading `P` as *stored, spendable damage
potential* and concluding that under V1 "repairing deviation does not reduce the
system's capacity for future damage; it converts realized damage into stored
damage potential at a one-to-one rate."

> **"Aggregate freedom is maximal at equilibrium" and "stored damage potential is
> maximal at equilibrium" are the same mathematical statement with opposite
> valence.** The mathematics does not choose between them.

Consequently the scope of §3 must be stated exactly:

- **Theorem F1 holds under V1-style accounting** — exact aggregate settlement with
  no sink.
- **Capacity V2 deliberately breaks it.** V2 caps each balance by the owner's own
  current local burden and retires the excess into a monotone ledger, so at
  `x = x*` every `V_i = 0`, every balance is `0`, and aggregate spendable capacity
  is **minimal**, not maximal. Under V2 the identity becomes
  `V + sum_i B_i + C_retired = J`, and `argmax(sum B) != argmin W`.

The freedom–equilibrium theorem is therefore a theorem **about V1 accounting**.
It does not re-legitimize what V2 was selected to remove, and it must not be
cited as if it did.

---

## 6. Equilibrium alignment versus action alignment

Two conditions, kept strictly separate.

> **A — equilibrium alignment.**
> `argmin_reachable W = argmin_reachable V_theta`.
>
> **B — edge / action alignment.** For every allowed action `x -> y`,
> `sign[W(x) - W(y)] = sign[V_theta(x) - V_theta(y)]`, zeros included
> (`W(x) = W(y)` iff `V_theta(x) = V_theta(y)`).

**Theorem AB1 (what B does give).** B implies `W` and `V_theta` have **the same
local minima** with respect to the action graph. ∎

**Theorem AB2 (B does NOT imply A).** Edge alignment is an *adjacent-pair*
condition and cannot compare non-adjacent states.

*Counterexample.* Path `a — b — c` with

```
W = (0, 1, 1/2)        V_theta = (0, 1, -1)
```

Both edges agree in sign, so B holds; yet `argmin W = {a}` and
`argmin V_theta = {c}`. *(Checked: `SY5`.)*

**Corollary AB3.** B **does** imply A when each of `W` and `V_theta` has a
*unique* local minimum on the reachable set. This is a uniqueness condition, not
mere connectivity.

**Theorem AB4 (A does NOT imply B).** §7's example has A and violates B.

> **A and B are logically independent.** This is the central distinction of the
> synthesis.

**Note on the zero clause.** B as stated includes zeros. §13 shows the zero
clause is not decoration: on the Study-1 graph it is *exactly* what forces the
current field to be a uniform rescaling of the reference.

---

## 7. The audit example

`x* = (2,2,2)`, `sigma_ref = (1,1,1)`, `sigma_current = (1,2,3)`, action
`(2,0,4) -> (3,0,3)`:

```
W(before) = 4 ,  W(after) = 3              ->   Delta W = +1
V_cur(before) = 13/18 , V_cur(after) = 19/18  ->   E_current = -1/3
```

*(Checked: `T3-1`.)*

**Do the minima agree?** Yes. `V_current >= 0` with equality exactly at `x*`, and
`x* = (2,2,2)` is a reachable lattice point, so

```
argmin W  =  argmin V_current  =  {(2,2,2)} .
```

*(Checked: `SY3`.)*

> **Stated plainly: this action-level sign disagreement does NOT imply the freedom
> maximum points away from equilibrium.** Both coordinates are minimized at the
> same unique state.

**What it does prove.** Exactly three things, and nothing more:

1. **B fails** — the normalized coordinate is not a faithful *local* proxy for
   current burden; across the 126 allowed actions the ratio `E_current/Delta W`
   takes 33 distinct values, some negative.
2. **The path, not the destination, is unaligned.**
3. **The mechanism is transparent** and is not anomalous: the action's
   per-coordinate contributions have **mixed signs** — coordinate 0 moves away
   from `x*` while coordinate 2 moves toward it — and the two fields weight them
   differently. Reference weights `(1,1,1)` give `E = +1`; current weights
   `(1, 1/4, 1/9)` give `E = -1/3`. *(Checked: `SY9`.)*

**On the actual Study-1 graph** the same field `sigma = (1,2,3)` disagrees in
sign with `W` on **13 of the 99** demand-driven edges. *(Checked: `S1-23`.)*

---

## 8. Gaussian dynamic-alignment theorem

For `V_theta(x) = 1/2 sum_i ((x_i - x*_i(theta))/sigma_i(theta))^2`:

| | condition | exact criterion |
|---|---|---|
| **A** | same reachable equilibrium as `W` | holds **iff** `argmin V_theta = argmin W` on the reachable set |
| **B** | action-sign alignment on every allowed transfer, zeros included | a finite check on the graph |
| **C** | factorwise local normalization | per factor, `V_{alpha,theta}` a strictly increasing function of `W_alpha` with positive derivative and matching finite level sets |
| **D** | global scalar normalization | `V_theta = q W + const`; for `n >= 3` this forces `H_theta = q H_0`, i.e. common `sigma` scaling |

**Implications.** `D => A`, `D => B`, `D => C`. **`C` does not imply `B`** (§7).
**`B` does not imply `A`** (Theorem AB2). `A` is the weakest.

**The decisive question: fixed `x*` with arbitrary positive `sigma_i(theta)`.**

> **Theorem G1.** If `x*` is fixed and **reachable**, then for *every* positive
> scale vector `sigma(theta)`, `V_theta >= 0` with equality exactly at `x*`.
> Hence `argmin V_theta = argmin W = {x*}`: **condition A always holds**, even
> though B may fail on many individual actions.

*(Checked: `SY6` — `sigma = (1,2,3)`, `(5, 1/2, 7)`, `(1/3, 9, 2)` all give
`argmin = {(2,2,2)}`.)*

### Theorem G2 — CORRECTED

**Previous statement (withdrawn):** *if `x*` is not reachable, the induced
minimizer is `x* + lambda sigma^2`, which moves with `sigma`, so A fails.*

That conflated three different objects. Separate them:

| object | definition |
|---|---|
| **affine-slice minimizer** | minimizer of `V_theta` over the *continuous* affine slice `sum_i x_i = M`, equal to `x* + lambda sigma^2` with `lambda = (M - sum_i x*_i)/sum_i sigma_i^2` |
| **integer-lattice minimizer** | minimizer over the reachable integer states |
| **nonnegativity-constrained minimizer** | minimizer over `{x >= 0, sum_i x_i = M}` |

**Theorem G2 (corrected).** If `x*` is off the reachable domain, then
**equilibrium alignment under changing `sigma` is no longer guaranteed**. It is
not automatic that it fails, and `x* + lambda sigma^2` may not be substituted for
the reachable optimum.

Three exact witnesses, all on `n = 3`, `M = 6`:

1. **It can fail.** `x* = (0,0,0)`: the affine-slice minimizer moves from
   `(2,2,2)` at `sigma = (1,1,1)` to `(3/7, 12/7, 27/7)` at `sigma = (1,2,3)`, and
   the lattice minimizer moves with it, from `(2,2,2)` to `(0,2,4)`.
2. **Movement of the affine minimizer does not imply failure.** `x* = (1,1,1)`:
   `sigma = (1,1,1)` gives affine minimizer `(2,2,2)`, and
   `sigma = (1, 11/10, 9/10)` gives `(301/151, 665/302, 545/302)` — a different
   point — yet **the lattice argmin is `{(2,2,2)}` in both cases**. A is
   preserved; the projection step is what decides.
3. **Nonnegativity can make the formula inadmissible.** `x* = (8,0,0)`,
   `sigma = (1,1,1)`: `x* + lambda sigma^2 = (22/3, -2/3, -2/3)` is not even
   feasible, while the constrained optimum is `(6,0,0)`.

*(Checked: `OS1`, `OS2`, `OS3`.)*

**Moving `x*`.** If the reference itself moves and remains reachable, then
`argmin V_theta = {x*(theta)} != {x*} = argmin W`, so A fails outright. Reference
shifts along `span(sigma_1^2, ..., sigma_n^2)` are the exception: they change no
EBU value on the conservation slice at all.

### One- versus multi-dimensional action spaces — CORRECTED

**Previous wording (withdrawn):** *with two cells the allowed action space is
one-dimensional, so any two covectors on it are proportional and even condition D
holds for unequal `sigma`.*

The premise is right and the conclusion does not follow. At **each state** the
allowed directions span a one-dimensional space, so `dV_theta` and `dW` restricted
to it are proportional — **with a state-dependent factor**. Condition D asks for
*one global constant*, which is a different and strictly stronger demand.

*Witness.* Two cells, `x* = (1,1)`, `M = 4`, `sigma = (1,2)`. Along the four
adjacent transitions the ratio `E_V/E_W` is

```
3/8 ,   -1/8 ,   11/8 ,   7/8 .
```

Not constant — and **it changes sign**, so this 2-cell world fails not only D but
also B. *(Checked: `TC1`.)*

---

## 9. Location, accessibility and policy — the three separated questions

This pass's central correction. Three questions were previously run together;
they are now named and kept apart. **These labels are deliberately distinct from
the A/B/C/D of §6 and §8.**

> **L — EQUILIBRIUM LOCATION.** Where is `W` minimized?
> **STATUS: PROVED** (§3, §4). Under V1 accounting, `argmax C = argmin W`, and
> for the reference Gaussian with `x*` a reachable lattice point that is `{x*}`.
>
> **R — ACCESSIBILITY.** Do the *allowed Study-1 actions* provide a path from a
> given state to the minimum?
> **STATUS: now settled exhaustively, and the previous claim was wrong** (§10–§12).
>
> **P — POLICY DYNAMICS.** Do random / aligned / hostile policies actually tend to
> follow such paths?
> **STATUS: OPEN / EXPERIMENTAL. Belongs to Stage A/B. Not touched here.**

### What survives unchanged

**Theorem H1.** If an executed action satisfies `Delta C > 0`, then
`Delta C = W(before) - W(after) > 0`, so `W(after) < W(before)`: **strict freedom
increase is strict burden descent.** ∎

**Theorem H2.** On a finite reachable state graph, a trajectory of strictly
freedom-increasing actions cannot cycle (each step strictly decreases `W`) and
must terminate, after finitely many steps, at a state admitting no
freedom-increasing action — a **local** minimum of `W` *with respect to whatever
action graph is in force*. ∎

**Theorem H3 (local minima are global — on the complete unit-transfer lattice).**
Let `W(x) = sum_i w_i(x_i)` with each `w_i` convex, on the lattice
`{x >= 0 : sum_i x_i = M}` **with an edge for every unit transfer between every
ordered pair of coordinates**. Then every local minimum is global.

*Proof.* Let `x` be a local minimum and `y` any state. Put
`S = {i : y_i < x_i}`, `D = {j : y_j > x_j}`; conservation makes both empty or
both nonempty. For `i in S` write `d_i^- = w_i(x_i) - w_i(x_i - 1)` and for
`j in D` write `d_j^+ = w_j(x_j + 1) - w_j(x_j)`. Local minimality of `x` against
the transfer `i -> j` (feasible since `x_i > y_i >= 0`) says exactly
`d_i^- <= d_j^+`. Convexity gives
`w_j(y_j) - w_j(x_j) >= (y_j - x_j) d_j^+` for `j in D` and
`w_i(y_i) - w_i(x_i) >= -(x_i - y_i) d_i^-` for `i in S`. Summing, with
`T = sum_{j in D}(y_j - x_j) = sum_{i in S}(x_i - y_i)`,

```
W(y) - W(x)  >=  T * min_{j in D} d_j^+  -  T * max_{i in S} d_i^-  >=  0 .
```
∎

*(Checked: `SY8`, across seven declared worlds.)*

### What is WITHDRAWN

> **The previous Corollary H4 is withdrawn.**

H3's hypothesis is **every** unit transfer between **every** ordered pair. The
Study-1 action graph satisfies none of that:

1. `A` and `C` are **not adjacent** — there is no route between them, so the
   transfer H3's proof invokes for the pair `(A, C)` does not exist;
2. the declared quanta are `{1, 2}`, not unit steps only;
3. decisively, **an edge exists only if some plan completely serves a currently
   derived demand and is irredundant.** The action graph is generated by the
   demand rule, not by the lattice.

Point 3 is not a technicality. §10 shows it is the binding one.

---

## 10. The actual Study-1 action graph, enumerated exhaustively

Edges are the successor states of the **decomposition-free progress reference**
`oracle.global_progress` — one complete plan per non-blocked part, blocked parts
contributing nothing — evaluated at every one of the 91 states. This is what the
runtime is required to reproduce.

### 10.1 The `(5,4,3)` plateau case, reproduced exactly

`x* = (4,4,4)`, state `(5,4,3)`, **`W = 1` exactly.** *(Checked: `S1-01`.)*

**Every allowed primitive physical transfer.** All eight `(route, quantum)`
pairs are executable here:

| action | post-state | `W` |
|---|---|---|
| `A->B @1` | `(4,5,3)` | 1 |
| `A->B @2` | `(3,6,3)` | 3 |
| `B->A @1` | `(6,3,3)` | 3 |
| `B->A @2` | `(7,2,3)` | 7 |
| `B->C @1` | `(5,3,4)` | 1 |
| `B->C @2` | `(5,2,5)` | 3 |
| `C->B @1` | `(5,5,2)` | 3 |
| `C->B @2` | `(5,6,1)` | 7 |

> **CONFIRMED: no single one-step transfer strictly decreases `W`.** Two are
> `W`-neutral, six ascend. *(Checked: `S1-02`.)*

**But a simultaneous plan does.** `{A->B @1, B->C @1}` is executable at `(5,4,3)`
— `A` funds 1 from 5, `B` funds 1 from 4 — and lands exactly on `(4,4,4)` with
`W = 0`. *(Checked: `S1-03`.)*

**And the model still forbids it.** At `(5,4,3)` the only P-deficit is at `C`
(`x_C = 3 < 4`, shortfall 1). The requirement is `delta_C >= 1`, and the menu is

```
{B->C @1}  ->  (5,3,4),  W = 1     (neutral)
{B->C @2}  ->  (5,2,5),  W = 3     (ascending)
```

`{A->B @1, B->C @1}` is **not** in the menu: dropping `A->B @1` leaves a plan that
still serves `C` and still executes, so the pair is **redundant**, and
irredundancy is the structural guard that enforces demand provenance.
*(Checked: `S1-04`, `S1-05`.)*

> **The plateau at `(5,4,3)` is real, and its cause is irredundancy — demand
> provenance — not the quantum set and not one-step-ness.**

**A `W`-nonincreasing path to equilibrium exists.**

```
(5,4,3)  --{B->C @1}-->  (5,3,4)  --{A->B @1}-->  (4,4,4)
  W = 1                    W = 1                    W = 0
```

Both steps are in the menu at their state: at `(5,3,4)` the deficit moves to `B`,
and `A->B @1` serves it completely. *(Checked: `S1-06`.)*

**The route offered in the task — `(5,4,3) -> (4,5,3) -> (4,4,4)` — is not the
model's.** `A->B @1` at `(5,4,3)` has **no P-demand provenance**: `B` sits exactly
at its reference, so there is no requirement for that action to serve, and it is
not in the menu. The model-permitted equivalent is the one above: the same two
actions, in the opposite order, each acquiring provenance when the deficit
arrives at its destination. *(Checked: `S1-07`.)*

> **"No strict-descent edge" and "no path to equilibrium" are therefore different
> statements, and `(5,4,3)` separates them: the first holds, the second does not.**

### 10.2 Exhaustive classification of all 91 states

| quantity | count |
|---|---|
| states | **91** |
| distinct successor edges | **99** |
| strictly `W`-descending edges | **80** |
| `W`-neutral edges | **13** |
| `W`-ascending edges | **6** |
| absorbing states (empty menu) | **37** |
| — of which the equilibrium `x*` | **1** |
| — **non-equilibrium absorbing** | **36** |
| states with a menu but **no** strict-descent edge | **4** |
| — every one of which has a neutral edge | **4** |

The four plateau-locked states are `(2,4,6)`, `(3,4,5)`, `(5,4,3)`, `(6,4,2)`.
None of them is strictly-ascending-only. *(Checked: `S1-08`, `S1-10`.)*

### 10.3 Level-set / plateau structure

Grouping each `W`-level into components connected by `W`-neutral edges:

| plateau components | count |
|---|---|
| total | **84** |
| containing `x*` | **1** |
| with an exit to lower `W` | **47** |
| with **no** lower exit | **36** |
| non-singleton | **5** |

Every one of the 36 no-exit components is a **singleton absorbing state**, and
every one of the 5 non-singleton plateau components **has** a lower exit. The
non-singleton ones are

```
W = 1 :  { (3,4,5), (4,3,5), (4,5,3) }      W = 1 :  { (3,5,4), (5,3,4), (5,4,3) }
W = 3 :  { (3,6,3), (5,2,5) }               W = 4 :  { (2,4,6), (4,2,6) }
W = 4 :  { (6,2,4), (6,4,2) }
```

*(Checked: `S1-12`.)*

> **So plateau motion is never a trap in Study 1. Every genuine plateau leads out.
> What traps the system is the empty menu, not the flat level set.**

### 10.4 Why the 36 non-equilibrium absorbing states are absorbing

**No state is resource-short.** `sum_i x_i = 12 = sum_i x*_i` at every state, so
the material needed to reach `x*` always exists somewhere in the world.
*(Checked: `S1-00`.)* Two mechanisms account for all 36:

| cause | count | nature |
|---|---|---|
| a deficit exceeds the maximum any single plan can deliver into that coordinate | **28** | `A` and `C` have one inbound route each and the largest quantum is 2, so a deficit of 3 or more there can never be completely served in one plan |
| **joint complete-service conflict**: every deficit is serviceable *alone*, the pair is not | **8** | `(2,2,8)`, `(2,3,7)`, `(3,1,8)`, `(3,2,7)`, `(7,2,3)`, `(7,3,2)`, `(8,1,3)`, `(8,2,2)` |
| genuine physical scarcity or topology | **0** | — |

*(Checked: `S1-13`.)*

The eight joint conflicts are the sharpest: at `(2,2,8)` the shortfall at `A` is
serviceable on its own (`B->A @2`), the shortfall at `B` is serviceable on its own
(`A->B @2`), and `physically_serviceable` returns `PHYSICALLY_IMPOSSIBLE` for the
pair — `A` would have to both receive 2 and fund `B`'s 2 from a stock of 2.

> **All 36 are artifacts of the *action generator*, specifically of the
> complete-service rule. None is physical scarcity.** This is the same class of
> finding as `DEMAND_DRIVEN_MODEL_FINDINGS.md` F-1 — "a declared complete-service
> and allocation restriction, not unavoidable physical scarcity" — but for
> P-demand alone, and far more severe than F-1's statement suggested.

### 10.5 Accessibility under the frozen rule

| from how many of the 91 states is `x*` reachable … | count |
|---|---|
| at all | **31** |
| by `W`-nonincreasing paths | **31** |
| by strictly `W`-descending paths | **23** |

The first two sets are **identical**: in Study 1, wherever equilibrium is
reachable at all it is reachable monotonically. The third is strictly smaller,
which is exactly the plateau-step requirement of §10.1. *(Checked: `S1-11`.)*

> **60 of the 91 states cannot reach equilibrium at all under the frozen
> complete-service P-demand rule.**

---

## 11. P-demand semantics — fundamental review

### 11.1 The ontological tension, stated exactly

The contract's own §2.1 declares P-demand **state-derived**:

> the shortfall persists ⟹ the demand persists, automatically; the shortfall is
> resolved ⟹ the demand disappears, automatically; P-demand cannot be rejected.

and the package implements exactly that: `derive_physical_demands` reads the
state, with "no cache, no queue, no memory".

If the residual need lives in the physical state and is re-derived every epoch,
then **requiring one plan to erase the entire deficit is an additional demand
that the ontology does not motivate.** Nothing is lost by partial restoration —
the remainder is still there, still visible, still a demand — because the state
itself is the record.

### 11.2 The `(0,6,6)` reproduction

State `(0,6,6)`, reference `(4,4,4)`. Deficit at `A` is **4**; the only route into
`A` is `B->A`, and the largest declared quantum is 2, so no plan delivers more
than 2 into `A`.

> **CONFIRMED: under complete-service semantics no P-demand plan executes.** The
> menu is empty and `physically_serviceable` returns `PHYSICALLY_IMPOSSIBLE` —
> a *proved* impossibility, not an undecided search. *(Checked: `S1-14`.)*

### 11.3 The atomic interpretation, tested — and since ADOPTED

**Rule tested.** A plan serves the P-demand of a part iff it makes strictly
positive progress at every deficit coordinate of that part; P-demand is
re-derived from the new state afterwards. **Irredundancy is unchanged.** No
backlog, no queue, no record of any kind is introduced.

Two variants were computed: **AP** (overshoot permitted, matching the contract's
existing rule) and **AP-NO** (a plan may not carry a coordinate past its own
reference).

At `(0,6,6)` the atomic menu is `{B->A @1}` and `{B->A @2}`, and the ladder closes:

```
(0,6,6)  ->  (2,4,6)  ->  (3,3,6)  ->  (4,4,4)
 W = 12      W = 4       W = 3       W = 0
```

*(Checked: `S1-16`.)*

Exhaustively, under **both** variants:

| | complete service | atomic |
|---|---|---|
| absorbing states | 37 (36 non-equilibrium) | **1 — `x*` alone** |
| `x*` reachable at all | 31 / 91 | **91 / 91** |
| `x*` reachable by `W`-nonincreasing paths | 31 / 91 | **91 / 91** |
| `x*` reachable by strict descent only | 23 / 91 | 83 / 91 |
| plateau-locked states | 4 | **2** — `(3,4,5)` and `(5,4,3)` |
| longest `W`-nonincreasing distance to `x*` | — | **5 steps** |

*(Checked: `S1-17`, `S1-20`.)*

> **Under atomic P-demand the whole 91-state Study-1 world reaches equilibrium,
> and reaches it monotonically. The eight strict-descent exceptions are exactly
> the states that must cross a plateau, which §10.3 shows always has an exit.**

**The demand provenance guard survives.** At `(5,4,3)` the atomic menu is still
exactly `{B->C @1}` and `{B->C @2}`: the unrelated `A->B @1` is still excluded by
irredundancy. *(Checked: `S1-19`.)* Incremental restoration does **not** make an
unrelated transfer legal.

### 11.4 Refinement / atomic consistency

**Complete service is not refinement-consistent.** At `(2,6,4)` the deficit at `A`
is 2, and `{B->A @2}` is a legal restorative plan reaching `(4,4,4)`. Its split
half `{B->A @1}` is physically executable and **illegal**, because it does not
completely serve. *(Checked: `S1-15`.)*

> Splitting a valid restorative action into valid parts destroys its demand
> provenance under complete service, and preserves it under atomic semantics.
> This is the project's own atomic-action principle — *physical state itself
> remembers unresolved P-demand* — and complete-service P-demand contradicts it.

### 11.5 Provenance under incremental restoration

Every field of the required record is a function of `(pre-state, plan,
post-state)`. Nothing is stored between epochs. For `(0,6,6)` with `{B->A @2}`:

| field | value |
|---|---|
| pre-action deficit at `A` | 4 |
| restorative amount delivered at `A` | 2 |
| post-action deficit at `A` | 2 — **re-derived from the new state, not carried** |
| touched physical coordinates | `{A, B}` |
| overshoot | 0 |

*(Checked: `S1-16` and the provenance reproduction.)*

### 11.6 Overshoot

**The existing contract already permits overshoot** (§6 item 4: "Delivering more
than required still delivers the requirement. This is what leaves a hostile actor
a real choice"). So **AP is the variant consistent with the frozen contract**, and
**forbidding P-overshoot would be a new author decision**, not a clarification.

That decision is **inert for Study 1**: AP and AP-NO have the identical absorbing
set, the identical accessibility classes and the identical plateau-locked set;
they differ only in which of the 226 versus 216 edges exist.
*(Checked: `S1-17`, `S1-18`.)*

Because the declared quanta include 1 and every Study-1 deficit is a positive
integer, **overshoot is always avoidable here** — indivisible quanta never force
it. In a world whose smallest quantum did not divide the deficit they could, and
then the decision would bite. **Isolated, stated, and not taken.**

### 11.7 E-demand and P-demand need not share completion semantics

**The distinction follows cleanly from existing project semantics.** Formalized:

| | **E-demand** | **P-demand** |
|---|---|---|
| origin | externally declared service contract, with an identity and a lifecycle (`E_PROPOSED -> E_ADMITTED_PENDING -> E_SERVED`) | derived from physical state every epoch, `derive_physical_demands`, no cache and no queue |
| residual after partial fulfilment | would have to be **stored against that order id** — a backlog quantity, which the contract structurally forbids | **already in the physical state**; re-derivation recovers it exactly |
| may be rejected | yes — `E_REJECTED_PHYSICAL_SCARCITY`, `E_REJECTED_INCOMPATIBLE` | no — contract §2.1 |
| completion contract | complete fulfilment, as the first model requires | **incremental restorative progress is sufficient** |

> **The asymmetry is structural, not stylistic: the P residual has a home and the
> E residual does not.** "No partial service, no backlog" was one rule applied to
> two objects; for P it is not needed, because there is nothing to store.

**The exact contradiction, if the atomic rule were taken with a no-overshoot
clause.** `service.CoordinateRequirement.required_delta` currently collapses the
two claims into `max(economic_total, physical_deficit)`. Under split semantics it
must become a **pair**: `delta_c >= economic_total` *and* `delta_c > 0`. With
overshoot permitted the pair is consistent, and it collapses back to
`max(economic_total, 1 unit of progress)`. With a no-overshoot clause it is
**inconsistent**: at a coordinate with deficit 1 and an admitted order for 3, the
E-claim requires `delta_c >= 3` and the no-overshoot P-claim forbids `delta_c > 1`,
so no plan is legal and a serviceable order becomes unserviceable. **This is the
precise reason the no-overshoot variant must not be adopted silently**, and it is
independent of Study 1, where no E-demand accompanies the P fixture.

No partial E-demand service is introduced anywhere in this pass.

---

## 12. Study-1 accessibility — the five questions

All five answered exhaustively over the 91 states, for the frozen complete-service
rule and for the atomic candidate. **No actor policy was run and no behaviour is
interpreted.**

**A. Is `x*` reachable at all?**
Complete service: **from 31 of 91 states**. Atomic: **from all 91**.

**B. Is `x*` reachable through `W`-nonincreasing restoration paths?**
Complete service: **from the same 31** — monotone reachability coincides exactly
with plain reachability. Atomic: **from all 91**. Witness under the frozen rule:
`(5,4,3) -> (5,3,4) -> (4,4,4)` at `W = 1, 1, 0`.

**C. Does any non-equilibrium absorbing P-demand state exist because of the action
generator rather than true physical scarcity?**
**Yes — 36 of them, and every one is a generator artifact.** 28 from the
one-plan delivery ceiling into `A` or `C`; 8 from joint complete-service
conflicts. **Zero** from scarcity: every state holds exactly the 12 units that
`x*` needs. Canonical witness `(0,6,6)`; sharpest witness `(2,2,8)`.

**D. Which states require plateau motion before strict `W` descent?**
Complete service: **4** — `(2,4,6)`, `(3,4,5)`, `(5,4,3)`, `(6,4,2)`, each with a
neutral edge and none strictly-ascending-only. Atomic: **2** — `(3,4,5)` and
`(5,4,3)`. In both cases every plateau component that is not the equilibrium and
is not a singleton absorbing state **has a lower exit**.

**E. Which states are genuinely blocked by physical resources or topology?**
**None.** Conservation gives `sum_i x_i = sum_i x*_i` at every state; the line
`A—B—C` connects every coordinate to every other; and under atomic semantics all
91 states reach `x*`. Every block observed under the frozen rule is a
consequence of the **complete-service completion contract**.

---

## 13. Current EBU versus normalized freedom — CORRECTED

**Do not assume `sign(E_theta) = sign(Delta c)`.**

**Theorem S1.** On a given allowed action the two agree **iff** condition B holds
for that action. Across a field family, they agree on every action iff B holds
globally.

**When they may differ.** Both are weighted sums of the *same* per-coordinate
quantities `[(x'_i - x*_i)^2 - (x_i - x*_i)^2]/2`, with different positive weights
`1/sigma_i^2`. **Two positively weighted sums of terms of mixed sign may have
opposite signs.** That is the whole of the phenomenon, and §7 is the worked
instance.

### The correction: two claims that must not be merged

> **Claim A — SIGN-/ORDER-FAITHFUL scalar settlement on a finite reachable
> domain.** For every allowed action, `E_theta` and `Delta c` agree in sign.
>
> **Claim B — MAGNITUDE-FAITHFUL retroactive one-scalar revaluation** of all
> current EBU receipts across a field change.

**Claim A does NOT require uniform scalar rescaling.**

*Witness on the actual Study-1 graph.* Take `sigma = (1, 3/2, 1)` — plainly not a
uniform rescaling of `(1,1,1)`. On **all 86 strictly `W`-changing demand-driven
edges** it agrees in sign with `W`, with **19 distinct** `E_V/E_W` ratios spanning
`1/6` to `59/54`. So A holds while D fails — there is no single constant
conversion. *(Checked: `S1-22`.)*

*Witness on a 2-cell world.* `x* = (1,1)`, `M = 4`, `sigma = (1, 3/2)`:
sign-faithful on **every** strictly `W`-changing ordered pair, `sigma` non-uniform,
and no constant conversion. *(Checked: `TC2`.)*

**What *does* force uniformity is the zero clause.** If condition B is imposed in
full — `W`-neutral edges must stay neutral — then on the Study-1 graph the field
is pinned:

> **Theorem U.** Write `t_i = 1/sigma_i^2` with `t_A = 1` (a uniform rescaling of
> `sigma` changes no sign). Two of the 13 `W`-neutral demand-driven edges,
> `(2,4,6) -> (4,2,6)` and `(5,4,3) -> (5,3,4)`, give the independent linear
> equations `t_B = 1` and `t_B = t_C`. Hence `t_A = t_B = t_C`: **`sigma` is
> uniform.** All 13 neutral edges are then consistent. *(Checked: `S1-21`.)*

This is an exact algebraic proof on the actual graph, not a search. Its converse
is visible in the witness above: `sigma = (1, 3/2, 1)` breaks 8 of the 13 neutral
edges, which is exactly what Theorem U forbids.

> **So the strength of the demand decides the answer. Strict-order faithfulness on
> a finite domain is cheap; demanding that indifference be preserved as well is
> what collapses the field family to a uniform rescaling — and a uniform rescaling
> changes no decision at all (same-ruler cancellation).**

**Claim B is the strong one**, and Theory III's no-go applies to it under its
exact hypotheses: two actions with the same old receipt `5` need new receipts
`17/9` and `19/8`. Claim A's finite-domain results say nothing about Claim B, and
Claim B's impossibility says nothing against Claim A.

**Language.** The correct terms are **current EBU action value** `E_theta` and
**normalized freedom-coordinate change** `Delta c`. Monetary framing such as
"rewarding damage" is **not** used.

---

## 14. Factor-decomposition qualification

Any implication involving factorwise normalization must **state the declared
factor decomposition** it is relative to.

> **Two total potentials being equal — or constant-shifted — on a conservation
> slice does not imply that each coordinate factor satisfies the same relation.**

*Witness.* Two cells, `x* = (1,1)`, slice `x_0 + x_1 = 2`, states
`(0,2), (1,1), (2,0)`. Put

```
W_total(x) = (x_0-1)^2/2 + (x_1-1)^2/2 ,      V_total(x) = (x_0-1)^2 .
```

On the slice `x_1 = 2 - x_0`, so `W_total = V_total` at **every** state. Yet
factorwise, `V_0 = 2 W_0` while `V_1 = 0` with `W_1` not identically zero: there
is no positive constant, and no increasing function, relating factor 1's two
potentials. *(Checked: `FQ1`.)*

**Rule adopted.** Factorwise properties are never inferred from total-potential
identities. Each factorwise claim carries its own proof and names its
decomposition. This also closes the refinement question of §2: additivity of
**both** potentials under the refinement is a hypothesis, not a consequence.

---

## 15. Individual versus aggregate freedom

`Delta C = W(before) - W(after)` constrains the **total**. The individual `c_i`
are fixed by the receipts `r_i` with `sum_i r_i = Delta C`, and closed-cycle
no-issuance constrains `C`, never each `c_i` separately: capacity may redistribute
between actors while the total is pinned — as in the programme's worked
circulation example, which returns a total of 100 while individual balances end at
`(23.5, 28.5, 9, 39)` from a uniform opening of 25.

> **The physical field constrains total freedom; settlement determines how that
> freedom is distributed among autonomous actors.**

No reward or punishment reading is adopted.

---

## 16. No history vector

The retained architecture requires, at runtime, only:

- the current local physical state;
- current field parameters;
- the declared reference / normalized field structure (a model constant, like
  `sigma` and `x*` — not a recorded trajectory);
- one scalar `c_i` per actor.

**No historical source, action or field vector is required.** The atomic
P-demand candidate of §11 **preserves this**: the residual deficit is re-derived
from the state, and no backlog, queue, deadline or service-order field is
introduced anywhere.

One theorem is explicitly marked **incompatible** with this architecture and is
therefore not retained as a mechanism: exact history-free revaluation of the
wallet across a field change (Claim B of §13).

---

## 17. Final theorem map

### PROVED

| result | where |
|---|---|
| `I = C + W` invariant; `C = I - W`; `argmax C = argmin W` | §3 |
| reference Gaussian: `argmin W = {x*}` when `x*` is a reachable lattice point | §4 |
| **equilibrium/freedom location theorem** (the two together) | §3–§4 |
| A and B are logically independent | §6 |
| H1, H2 (strict ascent is strict descent; terminates) | §9 |
| H3 on the **complete** unit-transfer lattice | §9 |
| Theorem U: preserving `W`-ties on the Study-1 graph forces uniform `sigma` | §13 |
| the exhaustive Study-1 accessibility structure (§10, §12), including the 36 generator-caused absorbing states | §10, §12 |

### PROVED UNDER EXTRA CONDITIONS

| result | condition |
|---|---|
| **dynamic Gaussian equilibrium alignment** (Theorem G1) | `x*` fixed **and reachable**; any positive `sigma(theta)` |
| B ⟹ A | each field has a unique local minimum (Corollary AB3) |
| canonical `W = V_{theta_0}` | up to `aW + b`, `a > 0`, per connected reachable component |
| sign-faithful settlement without uniform `sigma` | finite domain, strict edges only (Claim A, §13) |

### OPEN / EXPERIMENTAL

| question | status |
|---|---|
| **actual actor-policy restoring tendency** | belongs to Stage A/B; untouched here |
| whether a regulator should require edge alignment (B) or only common equilibrium (A) | a declaration, not mathematics |
| ~~whether complete-service semantics are the right long-run P-demand contract~~ | **RESOLVED and implemented.** Withdrawn for physical restoration as finding F-7; retained for economic demand. Contract §2.1, §3, §15 |
| off-slice `x*` under changing `sigma` | alignment not guaranteed; decided case by case by the projection (§8) |

### SUPERSEDED

| claim | replacement |
|---|---|
| **automatic Study-1 convergence from complete-lattice convexity** (the previous Corollary H4) | **§10's exhaustive enumeration: 36 of 91 states are absorbing away from equilibrium under the frozen rule** |
| Theorem G2 as "A fails when `x*` is off the slice" | "alignment is no longer guaranteed"; three-way separation of minimizers (§8) |
| "with two cells even D holds for unequal `sigma`" | local proportionality with a state-dependent factor; the witness ratios `3/8, -1/8, 11/8, 7/8` (§8) |
| "sign-faithful settlement requires uniform rescaling" | Claim A / Claim B separation; Theorem U (§13) |

---

## 18. Stage-A readiness

> # READY TO FREEZE STAGE-A PREREGISTRATION

**Why.** Stage A is a set of isolated mechanism demonstrations. Everything a
Stage-A preregistration needs to know about the environment is now exact and
public: the 91-state graph, its edges, its absorbing states with their causes,
its plateau components, and its accessibility partition. No mathematical
question about the environment is open.

**Superseded by the implementation pass.** At the time this section was written
the complete-service rule was frozen and the atomic rule was a candidate. The
candidate has since been adopted (F-7), so the two conditions below are
restated against the implemented semantics: under atomic P-service `x*` is
reachable from all 91 states, so there is no unreachable set for a fixture to
fall into, and no amplitude is permanently unserviceable. The preregistration
is frozen in `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md`.

**Two conditions the preregistration must satisfy, both structural and neither
derived from any observed outcome.**

1. It must **declare the accessibility partition** — that under the frozen rule
   `x*` is reachable from 31 of 91 states — and state, for each declared fixture,
   which side of it the fixture starts on. A fixture may legitimately start in
   the unreachable set, but it must say so, and it must not report the resulting
   non-recovery as a behavioural finding about EBU.
2. It must **not choose the P-disturbance amplitude to dodge the structure**. A
   disturbance of 3 or more at `A` or `C` is permanently unserviceable under the
   frozen rule — `(0,6,6)` is the canonical instance — and that is a declared
   property of the contract, not a defect to be avoided by parameter choice.

**Remaining preregistration choices — these only.** Not taken here, and none may
be chosen from observed outcomes:

| # | choice |
|---|---|
| 1 | the exact **Stage-A shock / demand fixtures**: coordinate, amplitude, epochs of recovery for the isolated P disturbance; destination, quantity, arrival epoch for the isolated E demand; the `E -> P -> restoration` cycle fixture |
| 2 | the **primary endpoint** |
| 3 | the **policy arms** |
| 4 | the **replicate / seed structure**, if any arm is stochastic |
| 5 | the **stop conditions** |

The existing `DEMAND_DRIVEN_STUDY_ONE_READINESS.md` A1–A4 and B1–B6 rows remain
the register of these decisions; this pass adds the structural constraint above
to A1 and changes nothing else there.

**Stage A was not run, and nothing in this document is evidence about the
mechanism.**

---

## 19. Final answer

**1. Where is maximum aggregate reserve?**
> At `argmin W`. Under V1-style accounting `I = C + W` is invariant, so
> `C = I - W` and `argmax C = argmin W`; for the reference Gaussian with `x*` a
> reachable lattice point that is the single state `x*` — `(4,4,4)` in Study 1.
> **Retained, and untouched by everything else in this pass.** The §5 scope
> warning travels with it: this is the same equation the programme reads as
> *stored damage potential*, and Capacity V2 breaks it by design.

**2. Can the actual Study-1 physics reach it?**
> **Under the implemented atomic P-demand rule: from all 91 states,
> monotonically, in at most 5 steps.** Under the withdrawn complete-service
> rule it was reachable from only 31 of the 91 states. 36 states are absorbing away from equilibrium — 28 because a deficit
> exceeds what one plan can deliver into its coordinate, 8 because two
> individually serviceable deficits are jointly impossible. **None is physical
> scarcity**; every state holds exactly the 12 units `x*` requires. Where
> equilibrium is reachable it is reachable by `W`-nonincreasing paths, and the
> four plateau-locked states all have exits. **Under atomic P-demand: from all 91
> states, monotonically, in at most 5 steps.**

**3. Does P-demand need complete one-shot service?**
> **No — and it no longer has it.** The rule was withdrawn and replaced
> (finding F-7). It was not required by the ontology, and it is what created
> all 36 absorbing states. P-demand is state-derived, so its residual is already stored
> in the physical state; complete service is a *declared rule*, not a consequence.
> It is also **not refinement-consistent** — splitting a legal restorative action
> into legal parts destroys its provenance — which contradicts the project's own
> atomic-action principle. E-demand is different in kind: its residual would need
> a new record, so complete fulfilment there is motivated. The distinction
> formalizes cleanly **provided overshoot stays permitted**, which the contract
> already does; a no-overshoot clause would contradict complete E-service outright.
> **The contract decision was subsequently taken and implemented** in the
> authorized implementation pass: contract §2.1 and §3, finding F-7, and
> `demand_driven_ebu.service`. Overshoot stayed permitted, exactly as this
> section required.

**4. What remains for Stage A to test empirically?**
> **Only question P — policy dynamics.** L (location) is proved; R (accessibility)
> is now settled exhaustively and is not an empirical question at all. What no
> enumeration can answer is whether aligned, random and hostile actors actually
> take the `W`-nonincreasing paths that exist, and how the arms differ in doing
> so. That is exactly the restoring-tendency question no registered study has
> asked, and it is unchanged by this pass.
