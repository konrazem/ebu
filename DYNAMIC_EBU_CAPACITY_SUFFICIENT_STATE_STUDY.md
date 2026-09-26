# Dynamic EBU capacity — is one scalar an entropy-like minimal sufficient state?


> **FIGURES RECOMPUTED (strong atomic P-provenance).** Every count in this
> document that depends on the Study-1 menu graph was recomputed after the
> physical-service predicate was strengthened to its existential form —
> progress on *at least one* pre-state P-demand rather than on every one of
> a coupled component. The graph grew from 226 to **408** realized menu
> edges. **No conclusion changed, and the figures moved in both directions.**
> The accessibility order became *more* comparable — 1689 of 4095 pairs, up
> from 1053, so 2406 remain incomparable rather than 3042 — and the Comparison
> Hypothesis still fails, because 2406 is not zero. The ascending set grew from
> 4 edges to 48 and the negative settlements from `{-2}` to `{-1,-2,-3,-4,-6}`,
> which strengthens F-3 rather than weakening it. The cycle space grew from
> Betti 126 to 254. Checks `SS-01` to `SS-12` in
> `dynamic_ebu_theory_checks.py` carry the new numbers and are what should be
> trusted over any figure quoted in prose.

**Subordinate to `EBU_DYNAMIC_FIELD_THEORY_SYNTHESIS.md`.** This is not a
"Theory IV" and claims no programme authority. Where it touches a synthesis
row it says so explicitly and sharpens it; where it disagrees with the
superseded Theory I / II / III files it says which statement and why. Nothing
here overrides the synthesis.

**Pure mathematics and literature.** No mechanism was implemented. `Study-1`
was not modified. The atomic P-demand implementation was not modified. Stage A
and Stage B were not run. No history vector, no source portfolio and no
capacity-as-money assumption was introduced. The only file changed is the
check module.

**Checks.** `dynamic_ebu_theory_checks.py` — **306 deterministic checks, 0
failures**, exact `Fraction`, tolerance literally zero, no randomized search.
The new section is tagged `SS-*` and enumerates the **actual** frozen Study-1
action graph through `demand_driven_ebu` pure functions, exactly as the
existing `S1-*` section does: no `EconomyRun`, no actor policy, no arrival law,
no trajectory.

---

## 0. The result, in one page

The central question decomposes into two questions that the programme has been
running together, and they have **opposite answers**.

> **Q-forward.** Under the *retained* architecture — settle every action at the
> field in force, never reprice an existing balance — is `c_i` a sufficient
> state?
>
> **YES, unconditionally.** For every field family, every world, every
> `sigma(theta)`, however heterogeneous. No history is required, and no
> condition on the field family is needed. (§4, Theorem S.)
>
> But `c_i` is **not minimal**. On every finite EBU world with rational field
> data the fractional part of `c_i` is invariant under every admissible future
> and enters no gate; on the frozen Study-1 world **all 408 realized
> settlements are integers**. The scalar carries strictly more information than
> any future can use. (§4, Theorem M; check `SS-07`.)

> **Q-retro.** If the architecture is additionally required to reprice existing
> balances when `theta` changes, is `c_i` a sufficient state?
>
> **NO** — and the reason is *not* the one on record.

The recorded obstruction (Theory III §4, carried into synthesis §13 as Claim B)
uses two histories ending at **different physical states**, `(1,0,5)` and
`(1,5,0)`. It therefore refutes a wallet-only revaluation `F(B)`, which is what
it was aimed at, but it is **not a counterexample to the sufficiency property
this task defines**, because that property grants the revaluer the current
physical state as well. The question needed its own witness. Here it is, on the
frozen Study-1 graph, under the **implemented** atomic P-demand rule:

```
                    (4,3,5)                      W = 1
                   /       \
   (3,6,3)  ------            ------>  (4,4,4)   W = 3  ->  0
     W = 3         \       /
                    (5,3,4)                      W = 1
```

Two owners. The first mover executes the first plan, the second owner the
second. In **both** histories:

| | H1 via `(4,3,5)` | H2 via `(5,3,4)` |
|---|---|---|
| terminal physical state | `(4,4,4)` | `(4,4,4)` |
| field in force | `sigma = (1,1,1)` | `sigma = (1,1,1)` |
| first mover's balance | **+2** | **+2** |
| second owner's balance | **+1** | **+1** |
| repriced to `sigma = (1,2,3)` — first mover | **7/8** | **31/72** |
| repriced to `sigma = (1,2,3)` — second owner | **13/72** | **5/8** |

*(Checked: `SS-01`, `SS-02`, `SS-03`.)* Everything the sufficiency property
allows the mechanism to see is identical, and exact repricing still demands two
different numbers. **The discarded information is exactly `4/9`.**

And the diagnosis is new:

> **Theorem A (§5.3).** The *aggregate* is a state function under **every**
> field: `sum_i c_i = W(x_0) - W(x)` and, repriced,
> `sum_i c'_i = V_{theta'}(x_0) - V_{theta'}(x)`. In the witness both histories
> give `3` and `19/18`. **What is path-dependent is not the total but the
> per-owner share of a path-independent total.** *(Checked: `SS-04`, `SS-05`.)*

So the obstruction requires **at least two owners**. With one owner the balance
telescopes to a difference of potentials and exact history-free revaluation
exists for every field family whatsoever. That, together with the
uniform-rescaling class `D`, is the precise class in the final verdict.

**And `C` is not an entropy.** Three independent reasons, each exact:

1. **Carathéodory is vacuous here.** EBU's Pfaffian form is already exact —
   `E_theta` is the difference of a potential by definition. There is no
   inexact form to repair, so there is no integrating factor to find. (§6.)
2. **Lieb–Yngvason is inapplicable, not merely unproved.** The declared state
   space is a *fixed-total* integer lattice; `lambda X` leaves it for every
   `lambda != 1`, so axioms **A4** (scaling) and **A5** (splitting) have no
   referent. And the Comparison Hypothesis fails badly: **2406 of the 4095**
   unordered Study-1 state pairs are accessibility-incomparable. (§7; checks
   `SS-08`, `SS-10`.)
3. **`C` is not monotone along accessibility.** **48 of the 408** menu edges
   strictly increase `W`, under the adopted AP variant and under AP-NO alike,
   so `X ≺ Y` does not imply `C(X) <= C(Y)`. An entropy that can decrease
   along an allowed process is not an entropy. (§7; check `SS-09`.)

`C` is a **conserved-complement potential**, `C = I - W`. That is a weaker and
different object, and the programme already proved it (synthesis §3). This
study adds that it is *not* upgradeable to an accessibility representation on
the actual graph.

---

## 1. Literature review

Every imported result is stated with its source, its original hypotheses, which
of those EBU satisfies, which it does not, and the classification
**DIRECT APPLICATION / ANALOGY ONLY / CONJECTURAL EXTENSION**. No analogy is
used as a step in any proof below.

### A. Carathéodory, Pfaffian forms, integrating factors

**Source.** C. Carathéodory, *Untersuchungen über die Grundlagen der
Thermodynamik*, Mathematische Annalen **67** (1909), 355–386.

**Result A1 (Carathéodory's theorem).** Let `omega = sum_i X_i(x) dx_i` be a
Pfaffian form, continuously differentiable on a domain in `R^n`. If in every
neighbourhood of every point there exist points not connected to it by a
solution curve of `omega = 0`, then `omega` admits an integrating factor: there
are functions `lambda > 0` and `sigma` with `omega = lambda d sigma`.

**Result A2 (Frobenius).** For `n >= 3` a nonvanishing `omega` is integrable —
admits an integrating factor locally — **iff** `omega ∧ d omega = 0`. For
`n = 2` every nonvanishing Pfaffian form is integrable, unconditionally.

**Original assumptions.** A smooth manifold of states; a genuinely **inexact**
one-form (`delta Q`) which is *not* the differential of a state function; a
local inaccessibility axiom; `n >= 2` continuous coordinates.

**What EBU satisfies.** Nothing that matters, and this is the finding, not an
omission. EBU's action valuation is `E_theta(G) = V_theta(pre) - V_theta(post)`
with `V_theta` a **declared potential**. Its differential form `dV_theta` is
therefore **exact by construction**, for every `theta` separately.

**What EBU does not satisfy.** The hypothesis that the form is inexact — the
entire premise of the theorem. Also: the Study-1 state space is a finite
integer lattice, not a manifold, so `d omega` is not defined on it at all.

> **Classification: NOT APPLICABLE (vacuously satisfied).** For a single field
> the Carathéodory question has the trivial answer `lambda = 1`,
> `sigma = V_theta`. Invoking Carathéodory to license an EBU entropy would be
> an error of the same shape as invoking the fundamental theorem of calculus to
> prove that a constant is constant.

**The non-vacuous question, and what Carathéodory does *not* answer.** The real
EBU problem is not integrability of one form but existence of a **common**
potential for a *family*: functions `lambda_theta(x) > 0` with

```
lambda_theta(x) · dV_theta |_{A_x}  =  dW |_{A_x}     for every theta,
```

on the allowed action space `A_x`. This is a *simultaneous* integrating-factor
problem across a family, which is a different and strictly harder problem;
Carathéodory addresses one form at a time and says nothing about it. §10
solves it exactly, and the answer is a rank-and-orientation condition, not an
integrability condition.

### B. Lieb–Yngvason axiomatic entropy

**Source.** E. H. Lieb and J. Yngvason, *The physics and mathematics of the
second law of thermodynamics*, Physics Reports **310** (1999), 1–96; expository
version, *A guide to entropy and the second law of thermodynamics*, Notices of
the AMS **45** (1998) — May issue; preprint arXiv:math-ph/9805005. (Secondary
sources disagree on the page range for the Notices version, so none is quoted
here.)

**Result B1 (the axioms).** On a set of equilibrium states with an adiabatic
accessibility relation `≺`:

| | axiom |
|---|---|
| **A1** | reflexivity: `X ~A X` |
| **A2** | transitivity: `X ≺ Y` and `Y ≺ Z` ⟹ `X ≺ Z` |
| **A3** | consistency: `X ≺ X'` and `Y ≺ Y'` ⟹ `(X,Y) ≺ (X',Y')` |
| **A4** | **scaling invariance**: `lambda > 0` and `X ≺ Y` ⟹ `lambda X ≺ lambda Y` |
| **A5** | **splitting and recombination**: `X ~A ((1-lambda)X, lambda X)` for `0 < lambda < 1` |
| **A6** | stability: `(X, eps Z_0) ≺ (Y, eps Z_1)` for a sequence `eps -> 0` ⟹ `X ≺ Y` |

**Result B2 (Comparison Hypothesis, CH).** Any two states of a state space are
comparable: `X ≺ Y` or `Y ≺ X`. Lieb and Yngvason call this a *hypothesis*, not
an axiom, precisely because it is not self-evident and must be derived.

**Result B3 (Entropy principle).** Under A1–A6 and CH there is a real function
`S` with

```
X ≺ Y   if and only if   S(X) <= S(Y),
S(X,Y) = S(X) + S(Y),        S(lambda X) = lambda S(X),
```

unique up to `S -> aS + B` with `a > 0`.

**What EBU satisfies.** A1 and A2 — reachability under the declared menu is a
preorder, trivially. A3 in a restricted form.

**What EBU does not satisfy — decisively.**

- **A4 and A5 have no referent.** The declared Study-1 state space is the
  fixed-total lattice `{x >= 0 integer : sum_i x_i = 12}`. `lambda X` has total
  `12 lambda`, so it is not a state of the space for any `lambda != 1`. The
  premises of A4 and A5 cannot even be written down. *(Checked: `SS-10`.)*
- **CH fails, and not marginally.** Of the `4095` unordered pairs of Study-1
  states, **`1689` are comparable and `2406` are not**. *(Checked: `SS-08`.)*
- **The order is not merely partial, it is nearly trivial at the top.** `x*` is
  reachable from all 91 states and **nothing but `x*` is reachable from `x*`**
  — the equilibrium is absorbing. *(Checked: `SS-08`.)*

> **Classification: INAPPLICABLE.** Not "unproved for EBU" — the
> extensivity/scaling scaffolding that carries the entire Lieb–Yngvason
> construction is absent from EBU's declared ontology, and CH is false on the
> actual graph. Any statement of the form "EBU capacity is an entropy because
> entropy is derivable from accessibility" is unavailable.

**What survives, and it is much weaker.** On a *finite* set, a preorder always
admits an order-**preserving** real function (`X ≺ Y ⟹ F(X) <= F(Y)`), by
topological sorting of the condensation. That is a triviality, not a theorem
about EBU, and it is *order-reflection* (`⟸`) that carries all the content —
and order-reflection requires totality, which §7 disproves. The honest import
from Lieb–Yngvason is therefore **negative**: it tells us exactly which
hypotheses to check, and EBU fails them.

### C. Mori–Zwanzig and exact model reduction

**Sources.** R. Zwanzig, *Ensemble method in the theory of irreversibility*,
J. Chem. Phys. **33** (1960), 1338–1341; H. Mori, *Transport, collective
motion, and Brownian motion*, Prog. Theor. Phys. **33** (1965), 423–455;
R. Zwanzig, *Nonequilibrium Statistical Mechanics*, OUP 2001, ch. 8;
A. J. Chorin, O. H. Hald and R. Kupferman, *Optimal prediction with memory*,
Physica D **166** (2002), 239–257.

**Result C1 (generalized Langevin equation / Dyson identity).** For a linear
generator `L` on observables and a projection `P` onto the resolved subspace,
with `Q = 1 - P`, the Dyson–Duhamel identity gives, exactly,

```
d/dt (P e^{tL} A)  =  P L P e^{tL} A
                      + ∫_0^t P L e^{sQL} Q L P e^{(t-s)L} A ds     <- memory
                      + P L e^{tQL} Q A                             <- noise
```

**Result C2 (exact Markovian closure).** The memory integral and the noise term
vanish identically for every `A` in the resolved subspace **iff**

```
Q L P = 0 ,
```

i.e. iff the resolved subspace is **invariant** under the generator. This is
immediate from C1 and is the standard criterion; it is not asymptotic and
involves no timescale separation.

**Original assumptions.** A linear evolution generator on a Hilbert space of
observables; an inner-product (orthogonal or conditional-expectation)
projection; a stationary measure defining that inner product.

**What EBU satisfies.** The *structure* of the question — a high-dimensional
object (the history) is projected onto a low-dimensional resolved variable
(`c_i`, `x`, `theta`), and one asks when the reduced description is exactly
closed.

**What EBU does not satisfy.** EBU's evolution is a deterministic finite
automaton on a lattice with a demand-derived menu. There is no linear
generator, no Hilbert space, no stationary measure and hence no orthogonal
projection. `Q L P = 0` cannot be evaluated because `L`, `P` and `Q` do not
exist as stated.

> **Classification: ANALOGY ONLY.** The Mori–Zwanzig apparatus is used here as
> *vocabulary* — "memory kernel", "exact closure" — and never as a proof step.

**The deterministic counterpart, which IS a direct application.** The exact
analogue of C2 for a deterministic system with outputs is the invariance of the
resolved partition under the transition map, and that is classical automata
theory (§D). §4 proves the EBU closure condition from that, not from C1–C2. The
useful transfer is one sentence, and it is exact:

> **Omitted history returns as memory precisely when the architecture applies to
> the wallet an operator that is not a function of `(c, x, theta)`.** Retroactive
> field revaluation is such an operator; every forward settlement is not. In the
> witness of §5 the memory term is exactly `4/9` — a finite number, not a decaying
> kernel, because the EBU "memory" is a one-shot algebraic defect rather than a
> relaxation process.

### D. Minimal sufficient statistics, causal states, graph cohomology

**Source D-i.** R. A. Fisher (1922) and J. Neyman (1935) — the factorization
criterion; E. L. Lehmann and H. Scheffé, *Completeness, similar regions, and
unbiased estimation*, Sankhyā **10** (1950), 305–340 — minimal sufficiency.

**Result D1.** A statistic `T` is sufficient for a family iff the likelihood
factorizes as `g(T(x), param) h(x)`; `T` is minimal sufficient iff its induced
partition is the coarsest sufficient one, and it is then a function of every
other sufficient statistic.

**What EBU satisfies / does not.** EBU's forward dynamics is deterministic:
there is no likelihood and no parameter family, so D1 does not apply as written.
**Classification: ANALOGY ONLY**, and the *language* of sufficient/minimal
sufficient is retained because §4's theorems are its exact deterministic
counterpart.

**Source D-ii.** J. P. Crutchfield and K. Young, *Inferring statistical
complexity*, Phys. Rev. Lett. **63** (1989), 105–108; C. R. Shalizi and
J. P. Crutchfield, *Computational mechanics: pattern and prediction, structure
and simplicity*, J. Stat. Phys. **104** (2001), 817–879 (arXiv
cond-mat/9907176).

**Result D2 (causal states).** Define `s⃖ ~ s⃖'` iff
`P(S⃗ = s⃗ | S⃖ = s⃖) = P(S⃗ = s⃗ | S⃖ = s⃖')` for every future `s⃗`. The
equivalence classes — **causal states** — are sufficient statistics of the past
for the future; among all *prescient* rivals (statistics attaining maximal
predictive power) the causal states have minimal statistical complexity
(Theorem 1), are minimal (Theorem 2), and are unique up to isomorphism
(Theorem 4).

**What EBU satisfies.** The *shape* of the question, exactly: "when are two
different actor histories physically indistinguishable for every possible future
local decision?" is literally the definition of the equivalence relation.

**What EBU does not satisfy.** EBU's future is deterministic, so the conditional
distributions collapse to point masses and the machinery of statistical
complexity, entropy rates and prescience is not needed.

> **Classification: DIRECT APPLICATION of the deterministic specialization.**
> When the future is deterministic, D2's relation degenerates to the **Nerode
> right congruence** of automata theory (A. Nerode, *Linear automaton
> transformations*, Proc. AMS **9** (1958), 541–544; J. Myhill, 1957): two
> histories are equivalent iff every future input suffix produces the same
> output. The Myhill–Nerode theorem says the quotient by this congruence is the
> unique minimal state set realizing the behaviour. §4 uses exactly this, and
> uses it as a proof, not as an analogy.

**Source D-iii.** Simplicial/graph cohomology; for the graph case see e.g.
N. Biggs, *Algebraic Graph Theory*, 2nd ed., CUP 1993, ch. 4 (cycle space and
cut space).

**Result D3.** For a finite graph `G = (V, E)` let `C^0 = R^V`, `C^1 = R^E`, and
`delta: C^0 -> C^1`, `(delta f)(u,v) = f(u) - f(v)`. A 1-cochain `s` is **exact**
(`s = delta f` for some `f`) iff its circulation vanishes on every cycle,
equivalently on any cycle basis. `H^1 = C^1 / im(delta)` has dimension
`|E| - |V| + c` (`c` = number of connected components).

**What EBU satisfies.** Exactly and completely. This is a finite combinatorial
statement about a finite graph, and the Study-1 action graph is one.
**Classification: DIRECT APPLICATION.** §12 uses it as a proof step.

---

## 2. Source-discipline summary

| import | used for | classification |
|---|---|---|
| Carathéodory A1/A2, Frobenius | to show the integrating-factor question is **vacuous** for EBU, and to isolate the real (family) question | **NOT APPLICABLE**, and this is the finding |
| Lieb–Yngvason A1–A6, CH, entropy principle | to state exactly which hypotheses an EBU entropy would need, then to disprove A4, A5 and CH on the actual graph | **INAPPLICABLE**; used negatively only |
| Mori–Zwanzig C1/C2 | vocabulary for "memory returns"; no proof step | **ANALOGY ONLY** |
| Fisher–Neyman / Lehmann–Scheffé D1 | vocabulary "sufficient", "minimal sufficient" | **ANALOGY ONLY** |
| Shalizi–Crutchfield D2 | the question's exact shape | **ANALOGY ONLY** in the stochastic form |
| **Myhill–Nerode** (deterministic specialization of D2) | Theorems S and M of §4 | **DIRECT APPLICATION** |
| **Graph cohomology D3** | §12, exactness of the settlement cochain, Betti number `254` | **DIRECT APPLICATION** |
| positive-ray / rank algebra | §10 | internal; proved here |

No result below is proved by analogy. Every theorem in §4–§13 is proved from
EBU's own declared rules plus D3 or Myhill–Nerode, and is accompanied by an
exact check.

---

## 3. EBU process value — unchanged

Retained verbatim from synthesis §2 (RETAIN), and **not** replaced by capacity:

```
E_theta(G)  =  V_theta(pre) - V_theta(post)
```

equivalently the exact path integral of the current field, with per-owner
common-path receipts `r_i = -∫ grad V_theta . delta_i` summing to `E_theta`.
This is the current work-like physical action value. Capacity does not replace
it and is not identified with it anywhere in this document.

Sign convention throughout is the programme's: *before minus after*, so
`Delta c = W(before) - W(after)` and `dc = -dW`.

---

## 4. The sufficiency question, formalized — and answered for the forward
architecture

### 4.1 The declared architecture

From synthesis §16, the retained runtime state is: current local physical state
`x`; current field parameters `theta`; the declared reference structure (a model
constant); one scalar `c_i` per actor. The three declared rules:

| | rule | depends on |
|---|---|---|
| **menu** | `M(x)` — the admissible plan groups at `x` | `x` alone **for P-demand**: `derive_physical_demands(world, state)` is a pure function of the state, "no cache, no queue, no memory" (contract §2.1). See the scope note below for E-demand |
| **settlement** | `r_i(G, x, theta)` | the plan, the current state, the current field |
| **gate** | participate iff `c_i + r_i >= 0` | `c_i` and `r_i` |

### 4.2 The sufficiency property

Let `H` be an actor's complete physical-action history and `T` a compression
`c = T(H) in R`. Say `T` has the **EBU sufficient-state property** if for any
two histories `H1, H2` with the same current physical state `x`, the same
current field `theta`, and the same `c` for every actor, **every** allowed
future sequence produces identical capacity updates, identical admissibility
decisions, and identical physically relevant future local behaviour.

This is the deterministic Nerode congruence of §1.D: `T` is sufficient iff its
fibres are contained in the Nerode classes, and minimal iff they coincide.

### 4.3 Theorem S — forward sufficiency, unconditional

> **Theorem S.** Under the declared architecture of §4.1, `c` has the EBU
> sufficient-state property. No history is required, for **any** field family.

*Proof.* Induction on the length of the future sequence. Base case: the menu
`M(x)` is a function of `x` alone; for each `G in M(x)` the receipt vector
`r(G, x, theta)` is a function of `(G, x, theta)` alone; the gate is
`c_i + r_i >= 0`, a function of `(c_i, r_i)`; the update is `c_i + r_i`. Hence
the one-step successor tuple `(x', theta', c')` is a function of
`(x, theta, c, G)` — all of which `H1` and `H2` share. Inductive step:
the successor tuples coincide, so the hypothesis holds at the next step. ∎

**Scope note on the menu hypothesis, stated rather than assumed.** Theorem S
needs the menu to be a function of the *declared current state*. That holds
exactly for **P-demand**, which is re-derived from `x` every epoch by
`derive_physical_demands(world, state)`. **E-demand is different**: it carries
an identity and a lifecycle
(`E_PROPOSED -> E_ADMITTED_PENDING -> E_SERVED`, `demand_driven_ebu/demand.py`),
so an E-menu depends on the admitted order book. That book is **declared
mechanism state, not actor history** — the theorem goes through with `x` read as
the full declared state — but it is *not* recoverable from the physical
coordinates alone, and the distinction is exactly the E/P asymmetry synthesis
§11.7 already formalizes ("the P residual has a home and the E residual does
not"). The Study-1 fixture carries no E-demand, so every check below sits in the
pure-P regime where the menu is a function of the physical state alone.

**This is not a triviality about the proof; it is a statement about the
architecture.** Theorem S holds because the architecture never reads the past.
It is exactly the deterministic form of the Mori–Zwanzig closure criterion C2:
the resolved set `{c, x, theta}` is *invariant* under the transition map, so
there is no memory term. Every field family satisfies it — including
`sigma = (1,2,3)`, including moving `x*`, including everything Theory III's
no-go excludes. **Theory III's no-go is not a no-go for this question.**

### 4.4 Theorem M — `c` is sufficient but strictly NOT minimal

> **Theorem M.** On the frozen Study-1 world, every one of the 408 realized menu
> settlements `W(x) - W(y)` is an **integer**. Hence the fractional part of
> `c_i` is invariant under every admissible future and enters no gate: two
> balances with the same integer part are Nerode-equivalent. `c` is therefore a
> sufficient statistic that is **strictly coarser-refinable** — it is not
> minimal. *(Checked: `SS-07`.)*

*Proof.* Every gate is `c + s >= 0` with `s` a sum of realized settlements,
hence an integer. For integers `s`, `1/3 + s >= 0` iff `2/3 + s >= 0`. ∎

> **Corollary M'.** On **every finite** EBU world with rational field data the
> realized cumulative settlements form a discrete subset of `R`, so `c` is never
> minimal. `c` is minimal only if the realizable cumulative settlements are
> **dense** in `R`, which no finite world achieves.

**The exact separation, stated honestly.** The negative settlements realized
anywhere on the Study-1 graph are exactly `-1, -2, -3, -4, -6`, all integers,
and they do separate balances an integer apart, so they separate balances two
integers apart. *(Checked: `SS-07`.)* So the distinctions any future can draw
form a **discrete index**, coarser than `c` and never finer.

> **This inverts the framing of the task's title question.** The scalar is not
> straining to hold enough information; it is holding **more than the mechanism
> can ever use**. An entropy-like *minimal* sufficient state would be the
> discrete index, not the real number. One scalar is not too small. It is too
> big — and it is exactly right only because real arithmetic is convenient.

---

## 5. Information-loss theorem — the exact boundary

### 5.1 What the recorded counterexample does and does not show

Theory III §4 and synthesis §13 Claim B record: two actions with the same old
receipt `5` need new receipts `17/9` and `19/8`, so one scalar cannot hold both.
That result is **correct and is not disturbed here**. But its two histories end
at `(1,0,5)` and `(1,5,0)` — **different physical states**. The sufficiency
property of §4.2 grants the mechanism the current physical state, so a witness
must hold `x` fixed. The recorded example does not, and therefore does not
answer this question. The witness below does.

### 5.2 Theorem I — the share diamond

> **Definition (share diamond).** Two menu-legal histories from a common start
> `x_0` to a common terminal `x_2`, assigning owners so that **every** owner
> holds the same balance under `theta` in both, yet some owner's balance
> differs when every receipt is recomputed under `theta'`.

> **Theorem I.** A share diamond for `(theta, theta')` exists **iff** no
> function `F: (c, x, theta, theta') -> c'` implements exact revaluation.
> Existence of a share diamond is therefore necessary and sufficient for the
> failure of one-scalar sufficiency under retroactive revaluation.

*Proof.* (⟸) If no share diamond exists, then `(x, c, theta)` determines the
repriced vector, and `F` may be *defined* as that map; it is well defined
exactly because no two histories with equal `(x, c, theta)` disagree. (⟹) If a
share diamond exists, `F` would have to take two values on one argument. ∎

**The witness, on the frozen Study-1 graph, under the implemented rule.**

```
x_0 = (3,6,3)   W = 3
   -- {B->A@1, B->C@2} -->  y_1 = (4,3,5)   W = 1   -- {C->B@1} -->  x* = (4,4,4)
   -- {B->A@2, B->C@1} -->  y_2 = (5,3,4)   W = 1   -- {A->B@1} -->  x* = (4,4,4)
```

All four edges are in the menu. *(Checked: `SS-01`.)* Owner 1 takes the first
plan, owner 2 the second.

| quantity | H1 | H2 |
|---|---|---|
| owner-1 balance under `sigma = (1,1,1)` | `3 - 1 = +2` | `3 - 1 = +2` |
| owner-2 balance under `sigma = (1,1,1)` | `1 - 0 = +1` | `1 - 0 = +1` |
| owner-1 repriced to `sigma = (1,2,3)` | `19/18 - 13/72 = ` **`7/8`** | `19/18 - 5/8 = ` **`31/72`** |
| owner-2 repriced to `sigma = (1,2,3)` | `13/72 - 0 = ` **`13/72`** | `5/8 - 0 = ` **`5/8`** |

*(Checked: `SS-02`, `SS-03`.)* Same terminal state, same field, same balances
for **every** owner — and repricing demands `7/8` for one history and `31/72`
for the other.

```
        the exact information lost  =  7/8 - 31/72  =  4/9
```

**This is not an isolated accident.** The frozen graph carries **137** share
diamonds for `sigma = (1,2,3)`. *(Checked: `SS-06`.)*

### 5.3 Theorem A — the obstruction is the SPLIT, not the total

> **Theorem A.** For every history and every field `phi`, the aggregate
> repriced balance telescopes:
> `sum_i c_i^{(phi)} = V_phi(x_0) - V_phi(x_now)`.
> The **aggregate** is a state function of the endpoints; the **per-owner
> share** is not.

*Proof.* `E_phi(G) = V_phi(pre) - V_phi(post)` and receipts sum to `E_phi`, so
summing over owners and over the history telescopes. ∎

*(Checked: `SS-04` on the witness — `3` and `19/18` in both histories — and
`SS-05` exhaustively on **every** two-step menu path of the graph, under both
fields.)*

> **Corollary A1 (the single-owner class).** If there is exactly one owner, its
> balance equals `V_phi(x_0) - V_phi(x_now)` under every field. Exact
> history-free revaluation therefore exists **for every field family
> whatsoever**, and `c` is in fact redundant — a function of `x` and the
> declared constant `x_0`.

> **Corollary A2 (the obstruction needs two owners).** Any share diamond
> requires at least two owners. One-scalar insufficiency under revaluation is a
> **distribution** phenomenon, not a field-geometry phenomenon.

This sharpens synthesis §15 — "the physical field constrains total freedom;
settlement determines how that freedom is distributed" — from a statement about
*where* freedom sits into a statement about *what is and is not recoverable*:
the total is recoverable from the state under any field; the distribution is
recoverable under none, except in the two classes of §14.

### 5.4 The boundary, stated — no vector is introduced

Per the task, the response to Theorem I is the boundary, not a wider state:

> **Only a retroactive field revaluation can distinguish two histories that
> share `(c, x, theta)`. No future ACTION ever can.**

This follows from Theorem S: under forward settlement the successor tuple is a
function of the shared data, so no sequence of actions, however long, separates
them. The information the scalar discards is invisible to the entire future of
the mechanism **unless** the mechanism is asked to reach back and reprice. The
boundary is therefore not between field families; it is between **forward** and
**retroactive** architectures.

---

## 6. The entropy-like state coordinate — and why `dS = delta Q_rev / T` is the
wrong template

Does there exist an exact one-form / state coordinate with `dc = -omega`, where
`omega` is determined locally from the current physical action valuation and the
field?

**Yes — trivially, and the triviality is the point.** Take `omega = dW`. Then:

| requirement | status |
|---|---|
| path-independent finite settlement | **holds**: `Delta c = W(before) - W(after)` depends on endpoints only |
| zero circulation around admissible closed cycles | **holds**: the settlement cochain is `delta W`, a coboundary (§12, check `SS-12`) |
| arbitrary refinement invariance | **holds** for the settlement cochain: subdividing a path telescopes |
| no historical field/action storage | **holds**: `W` is evaluated at the current state |

So the state coordinate exists, and the programme already has it. What it is
**not** is an entropy.

> **The disanalogy, exactly.** `dS = delta Q_rev / T` is a theorem about
> converting an **inexact** form into an exact one; `1/T` is the integrating
> factor that does the converting, and its existence is the content of
> Carathéodory's theorem. **In EBU there is nothing inexact.** `dV_theta` is
> exact for every `theta` because `V_theta` is a declared potential. There is no
> integrating factor to find, no `T` to identify, and consequently no entropy to
> derive by this route.

The non-trivial residue is the *family* problem of §1.A: a common `W` with
positive normalizers `lambda_theta(x)` across the field family. That problem has
an exact answer, and it is not an integrability condition — §10.

**And the coordinate that does exist fails the two properties that would make it
entropy-like.** It is not minimal (Theorem M) and it is not monotone along
accessibility (§7). Both failures are exact and on the actual graph.

---

## 7. Accessibility-based construction

Rather than declaring `c`, define the relation directly:

```
X ≺ Y     iff   Y is reachable from X by menu-legal plans
                under the declared EBU architecture.
```

This is reflexive and transitive — a preorder — by construction. Three exact
findings on the frozen Study-1 graph under the **implemented** atomic rule.

**F-1. The order has a unique maximum and is absorbing there.** `x*` is
reachable from all 91 states; from `x*` nothing but `x*` is reachable.
*(Checked: `SS-08`.)*

**F-2. The order is far from total.** `1689` of `4095` unordered pairs are
comparable; **`2406` are not**. *(Checked: `SS-08`.)* Hence the Comparison
Hypothesis fails, and **no order-reflecting scalar exists**: there is no `F`
with `X ≺ Y ⟺ F(X) <= F(Y)`, because the right-hand side is total and the
left-hand side is not. Per the task's instruction, no total ordering is forced.

**F-3. `C = I - W` is NOT an accessibility potential.** Of the 408 menu edges,
**48 strictly increase `W`** — hence strictly *decrease* `C` — under the adopted
AP variant, and 42 under AP-NO as well, so the finding is variant-independent.
*(Checked: `SS-09`.)* Therefore `X ≺ Y` does **not** imply `C(X) <= C(Y)`.

> An entropy must not decrease along an allowed adiabatic process. `C` does.
> **`C` is not an entropy for this accessibility relation**, and the failure is
> exhibited by 48 explicit edges, not conjectured.

Every ascending edge settles a negative integer, drawn from `-1, -2, -3, -4, -6` — the negative settlements on the
graph — so it is affordable only out of an already-positive balance.

### Which of the three is EBU freedom?

| candidate | verdict |
|---|---|
| a **state ranking** (order-reflecting `F`) | **No.** Requires totality; `2406` incomparable pairs |
| an **accessibility potential** (order-preserving `F`) | **No** for `C`. 48 ascending edges. (Such an `F` *exists* — any topological order does — but it is not `C`, and an arbitrary topological order has no physical content) |
| **neither** | **This.** `C` is a *conserved-complement potential*: `C = I - W` with `I` invariant under actor-only evolution (synthesis §3). It is pinned by a conservation law, not by an order |

**The extra hypothesis that would repair it, stated exactly.** `C` becomes an
accessibility potential **iff** no menu-legal action increases `W` — i.e. iff
the menu is `W`-nonincreasing. That is a *declaration about the action
generator*, not a mathematical fact, and on the frozen generator it is **false**
by 48 edges. Whether to adopt it is a design decision this document does not
take and does not pre-empt.

---

## 8. Relation to `C + W = I`

The fixed-field accounting theorem is preserved exactly as proved (synthesis
§3, hypotheses: exact aggregate normalized settlement; actor-only evolution; no
process burdens; one reachable component):

```
C_after + W(x_after)  =  C_before + W(x_before) ,     C = I - W ,
argmax C = argmin W .
```

Nothing in this document weakens it. Theorem A of §5.3 is its per-field
strengthening: `C` telescopes to `V_phi(x_0) - V_phi(x)` under **every** field
`phi`, not only the reference one.

### Can `C` be read as an accessibility/freedom coordinate?

**Only in the weak sense, and §7 bounds it.** `C` is an exact state function of
`x` on a reachable component, so it is a *potential*. It is not an accessibility
representation, because 48 menu edges decrease it.

### The dual readings, and the operational assumption that separates them

Synthesis §5 records the warning: *"aggregate freedom is maximal at
equilibrium"* and *"stored damage potential is maximal at equilibrium"* are the
same equation with opposite valence, and the mathematics does not choose.

> **This document does not settle it rhetorically. It names the operational
> assumption that decides it, and reports which way the frozen architecture
> falls.**

| reading | what it commits to |
|---|---|
| **aggregate action reserve** | a positive `c_i` is a licence to act, and the actions it licences are ones the architecture wants |
| **stored damage potential** | a positive `c_i` is a licence to act, and among the actions it licences are ones that move the world **away** from equilibrium |

> **The distinguishing operational assumption is: does the admissibility gate
> permit `W`-increasing actions to be funded out of an existing balance?**

- **Under V1 it does.** The gate is `c_i + r_i >= 0`, and `r_i < 0` is
  affordable whenever `c_i` is large enough. The Study-1 graph contains **48**
  such edges, each settling a negative integer. *(Checked: `SS-09`.)* So under V1 the
  stored-damage-potential reading has **operational content**: the licence is
  real, the actions it funds exist on the actual graph, and they are exhibited.
- **Under Capacity V2 it does not, by design.** V2 caps each balance by the
  owner's own current local burden and retires the excess, so at `x = x*` every
  balance is `0` and there is nothing to spend (synthesis §5). V2 breaks
  `C + W = I` deliberately, and that is precisely the intervention that removes
  the damage reading.

> **Conclusion, non-rhetorical.** The two readings are not a matter of
> interpretation. They are separated by one checkable architectural question,
> V1 answers it in the direction that makes "stored damage potential" literally
> true, and Capacity V2 is exactly the mechanism that answers it the other way.
> The freedom–equilibrium theorem is, as synthesis §5 already insists, a theorem
> **about V1 accounting**, and nothing here re-legitimizes what V2 removed.

---

## 9. The sign disagreement — `E_theta < 0` while `Delta c > 0`

The established phenomenon (synthesis §7, §13; Theory III §2): at
`x* = (2,2,2)`, `sigma_ref = (1,1,1)`, `sigma_cur = (1,2,3)`, the action
`(2,0,4) -> (3,0,3)` has `Delta W = +1` and `E_current = -1/3`. On the actual
Study-1 graph, `sigma = (1,2,3)` disagrees in sign with `W` on 13 of the 99
complete-service edges.

The task asks whether this is (A) a contradiction for an accessibility-state
interpretation, (B) a legitimate entropy-like effect analogous to the difference
between a total process quantity and a normalized state change, or (C) dependent
on the chosen accessibility axioms.

> **Answer: (C), resolving to (A) for the current-field reading and to no
> problem at all for the reference-field reading. Explicitly NOT (B).**

**Why not (B) — this must be stated, because (B) is the tempting answer.** The
proposed analogy is `delta Q` (process) versus `dS` (state). That analogy
requires one of the two quantities to be an **inexact** form. Here **both are
exact**: `E_theta` is the increment of the potential `V_theta`, and `Delta c` is
the increment of the potential `W`. Two exact forms, two genuine state
functions. The thermodynamic mechanism that produces a sign difference — path
dependence of heat — **has no counterpart here**, and invoking it would be a
category error.

**What actually produces the disagreement, exactly.** Both quantities are
positively weighted sums of the **same** per-coordinate terms
`[(x'_i - x*_i)^2 - (x_i - x*_i)^2]/2`, with weights `1/sigma_i^2` from two
different fields. When those terms have **mixed signs** — one coordinate moving
toward `x*` while another moves away — two positively weighted sums can differ
in sign. That is the whole of it (synthesis §13, §7 item 3). It is a statement
about two rulers disagreeing on a mixed-sign bundle, not about integrability.

**Why (C).** The question "is this a contradiction?" has no field-free answer
because it depends entirely on **which field defines accessibility**:

| declared accessibility | verdict |
|---|---|
| accessibility is ordered by the **current** field `V_theta` | **(A) — a genuine contradiction.** `C` would have to be a potential for `V_theta`, and the disagreeing edges show it is not |
| accessibility is ordered by the **reference** field `W` | **no contradiction whatsoever.** `C = I - W` is exactly a potential for `W`, by Theorem F1 |
| accessibility is the **menu reachability** relation of §7 | **(A) again, for an independent reason** — the 48 `W`-ascending edges — which has nothing to do with the sign disagreement |

> **So the sign disagreement does not invalidate the theory, and it does not
> vindicate an entropy reading either.** It is a precise, local statement that
> condition B fails, it is already correctly recorded in synthesis §13, and it
> becomes a contradiction only under an accessibility axiom the programme has
> not declared. The decisive obstacle to the entropy reading is **not** the sign
> disagreement; it is the 48 ascending edges of §7 and the inapplicability of
> A4/A5 — neither of which is about signs of `E_theta` at all.

---

## 10. Dynamic field rank / dimension

At each state `x`, project every current-field differential onto the allowed
local action space: the family `{ dV_theta |_{A_x} : theta in Theta }`. For
conservation-respecting transfers `A_x ⊆ 1^perp`.

**The task's conjecture.** *Is a one-scalar exact history-free coordinate
possible exactly when the future-relevant field family is rank-one after
admissible local normalization?*

> **Answer: No — but it is nearly right about a different question, and the
> correction is precise.** Rank-one (refined to a **common open ray**) is
> necessary and sufficient for the existence of a common positive
> **normalizer**. It is *not* the condition for a one-scalar sufficient
> **state**. The two are different objects and the study separates them.

### 10.1 Theorem R — the exact normalizer criterion

> **Theorem R.** A common `W` with positive local normalizers `lambda_theta(x)`
> satisfying `lambda_theta(x) dV_theta|_{A_x} = dW|_{A_x}` for every `theta`
> exists **iff** at every reachable `x` the projected covectors
> `{ P_{A_x} dV_theta }` lie in **one open ray** — rank one **and** pairwise
> *positively* proportional. When they do, `W := V_{theta_0}` works.

*Proof.* (⟹) If two fields give covectors that are not positive multiples of
each other on `A_x`, no `lambda > 0` can carry both to the same `dW`. (⟸) If
they share a ray, each `dV_theta|_{A_x}` is a positive multiple of
`dV_{theta_0}|_{A_x}`, which is the differential of the declared potential
`V_{theta_0}`; take `W := V_{theta_0}` and `lambda_theta` the pointwise ratio. ∎

**Rank one alone is not enough, and the refinement is load-bearing.** Rank one
gives a *line*; positivity requires the *same half* of it. The synthesis's own
2-cell witness has `dim A_x = 1` — so rank one is automatic — yet the ratios are
`3/8, -1/8, 11/8, 7/8`, which **change sign**. Rank one holds; the criterion
fails. This is why the ray formulation, not the rank formulation, is correct.

**How hard the criterion bites on the actual world.** For the pair
`sigma = (1,1,1)` and `sigma = (1,2,3)` on the Study-1 slice, the projected
covectors share a ray at **exactly one** of the 91 states — `x*` itself, where
both vanish. **At no state with a nonzero gradient does a positive
`lambda(x)` relate the two fields.** *(Checked: `SS-11`.)* At `(5,4,3)` the two
covectors are `(1, 1)` and `(1, 1/9)`: rank **2**.

By contrast, a uniform rescaling `sigma -> 2 sigma` shares the ray at **every**
state. *(Checked: `SS-11`.)* That is condition `D`, and by same-ruler
cancellation it changes no decision.

### 10.2 The correct condition for a one-scalar STATE

Theorem R governs *normalizers*. The sufficiency question is governed by
Theorem I:

| demand | exact criterion |
|---|---|
| a common positive normalizer exists at `x` | projected covectors share one **open ray** at `x` (Theorem R) |
| sign-/order-faithful settlement on a finite domain | the ray condition on **strict** edges only — cheap, and holds for non-uniform `sigma` (synthesis §13 Claim A) |
| exact magnitude-faithful revaluation | the ray condition **plus a globally constant factor** — condition `D`, `V_{theta'} = qW + const` |
| **one-scalar sufficient state under revaluation** | **no share diamond exists** (Theorem I) |
| **one-scalar sufficient state, forward architecture** | **no condition at all** (Theorem S) |

`D` implies no share diamond — if every receipt rescales by one global `q`, the
per-owner split rescales with it and repricing is multiplication by `q`. The
converse is not asserted; the single-owner class of Corollary A1 has no share
diamond and is not `D`. **So the rank/ray condition is sufficient-via-`D` but
not necessary, and it is not the criterion.**

---

## 11. Factor-local structure

Repeating the question for the declared EBU factor hypergraph: can multiple
factor-local normalizers combine into one scalar state without hidden memory?

Three constraints, all already proved in the programme and all retained:

1. **Refinement is legitimate only when both potentials are exactly additive
   under it** (Theory III §0.3; synthesis §2, RETAIN WITH CORRECTED HYPOTHESIS).
   Genuine cross terms may not be discarded: `W = (x^2 + y^2 + xy)/2` has mixed
   second difference `1/2 != 0` and admits no separable refinement. That
   obstruction is final. Per the task, no arbitrary factor refinement is
   performed here and physical interaction factors are left intact.
2. **A total-potential relation never descends to the declared factors**
   (synthesis §14, check `FQ1`): two potentials agreeing at every state of a
   conservation slice can relate factorwise by `2` on one factor and by no
   positive constant at all on another.
3. **Level-set compatibility must be taken in its finite form**
   `W_alpha(u) = W_alpha(v) => V_{alpha,theta}(u) = V_{alpha,theta}(v)`; the
   infinitesimal version is strictly weaker (Theory III §0.1).

> **Answer.** Factor-local normalizers combine into one scalar state without
> hidden memory **iff** (i) both the reference and the current potential are
> exactly additive over the declared decomposition, **and** (ii) each factor's
> normalizer is a function of that factor's own current state. Under (i)–(ii)
> the factor settlements sum and each is a coboundary, so the total is a
> coboundary and no storage is needed.

> **But this is orthogonal to sufficiency, and that is the finding worth
> recording.** Even when (i) and (ii) hold perfectly, Theorem I is untouched:
> the share diamond of §5.2 is about **which owner** took which factor-local
> step, and factor-locality says nothing about ownership. **Factor decomposition
> cannot repair a distribution obstruction.** Locality is a statement about
> *where* a receipt may look; sufficiency is a statement about *whose* receipt
> it was.

---

## 12. Graph-topological version

For the finite EBU state/action graph: current field values define edge action
quantities; candidate capacity defines edge settlement; zero cycle circulation
gives exactness. Using D3 (a direct application):

**Result 1 — the settlement cochain is exact.** The Study-1 settlement cochain
`s(x,y) = W(x) - W(y)` is `delta W`, hence a coboundary, hence has zero
circulation on every cycle. *(Checked: `SS-12`.)*

**Result 2 — and the cycle space is genuinely non-trivial.** The underlying
undirected action graph is **connected**, with **91** vertices and **344**
edges, so its first Betti number is

```
dim H^1  =  344 - 91 + 1  =  254 .
```

*(Checked: `SS-12`.)* Exactness is therefore a real constraint on this graph —
254 independent cycle conditions — not an artifact of a tree.

**Result 3 — the two concepts are logically independent, in both directions.**
The task requires them kept separate; they are, and here are the witnesses.

> **Exact does NOT imply sufficient.** The Study-1 settlement cochain is exact
> (Result 1), and `c` is nevertheless *not* a sufficient state under
> revaluation (§5.2, same graph, same cochain). *(Checked: `SS-12`.)*

> **Sufficient does NOT imply exact.** On a 3-ring settling `+1` per traversal,
> the update and the gate are functions of `(c, vertex)` alone — perfect
> sufficiency by Theorem S — yet the circulation is `3`, so the cochain is not a
> coboundary and closed cycles mint. *(Checked: `SS-12`.)*

> **Conclusion.** **Graph cohomology characterizes path independence ONLY.** It
> is the complete answer to "does a closed cycle settle to zero" and it says
> **nothing** about future sufficiency. Sufficiency is a property of the
> *automaton* — the Nerode quotient of the transition system — and lives in a
> different invariant from `H^1`.

**A conjectural extension, flagged as such and not used.** The sufficiency
question has the shape of a cocycle condition valued in the group generated by
the revaluation maps rather than in `R`: exactness is `H^1(G; R)`, sufficiency
would be the vanishing of an obstruction in a non-abelian analogue whose
coefficients are the transition maps themselves. **CONJECTURAL EXTENSION.** No
theorem is claimed and nothing below depends on it.

---

## 13. Gaussian specialization

For `V_theta(x) = 1/2 sum_i ((x_i - x*_i(theta))/sigma_i(theta))^2` on the
conservation slice, combining Theorem R (§10), Theorem I (§5) and the synthesis's
Gaussian results (§8, §13):

| dynamic field class | common ray (Thm R) | condition `D` | share diamond | **one exact history-free scalar?** |
|---|---|---|---|---|
| fixed `x*`, **common `sigma` scaling** `sigma -> c sigma` | yes, at every state | yes, `q = 1/c^2` | none | **YES — and it changes no decision** (same-ruler cancellation) |
| fixed `x*`, **heterogeneous `sigma_i`**, `n >= 3` | **no** — for `(1,1,1)` vs `(1,2,3)` the ray is shared at 1 of 91 states, and that one has zero gradient | no (`n >= 3` forces `H' = qH`) | **yes — 137 on the frozen graph** | **NO under revaluation; YES under forward settlement** |
| fixed `x*`, heterogeneous `sigma_i`, `n = 2` | rank one automatic, **ray can still fail** — witness ratios `3/8, -1/8, 11/8, 7/8` | no (factor is state dependent) | possible | **NO under revaluation; YES forward** |
| **moving `x*`**, reachable | fails; `argmin V_theta = {x*(theta)} != argmin W` | no | possible | **NO under revaluation; YES forward** |
| moving `x*` along `span(sigma_1^2, ..., sigma_n^2)` | yes | `q = 1`, no EBU value changes | none | **YES — and vacuously, nothing changes** |
| `x*` **off** the reachable slice | not guaranteed either way; the affine-slice, integer-lattice and nonnegativity-constrained minimizers are three different objects (synthesis §8, `OS1`–`OS3`) | decided case by case | decided case by case | **decided case by case; forward settlement is unaffected** |
| **conservation slices** | the projection onto `1^perp` is what produces the *centred* condition | — | — | it is what makes `n = 2` special, and the 2-cell witness shows even that is not enough |
| **1-D vs higher-dimensional action spaces** | `dim A_x = 1` makes rank one automatic but **not** the ray condition | still needs a *global* constant | — | dimension is not decisive; **orientation** is |

> **The classification in one line.** Among Gaussian dynamic fields, **exactly
> the uniform rescalings** (and reference motion along `span(sigma_i^2)`, which
> changes nothing) admit one exact history-free scalar capacity **under
> retroactive revaluation** — and those are precisely the field changes that
> alter no admissibility decision. **Under forward settlement, every Gaussian
> dynamic field admits one**, without exception.

This reproduces synthesis §8 and Theory III §8 for the revaluation column and
adds the forward column, which is the one the retained architecture actually
uses.

---

## 14. The no-history requirement — the architectural boundary

The architectural requirement is **no historical vector**. Where the exact
mathematics says higher-dimensional memory would be necessary, the required
statement is made and no vector is implemented:

> ## ONE-SCALAR EBU CANNOT EXACTLY REPRESENT THE CLASS
> ## { retroactive revaluation, two or more owners, non-uniform field change }

**The class, stated exactly.** Exact history-free one-scalar capacity under
retroactive field revaluation holds **iff** no share diamond exists (Theorem I),
and the two exactly characterized sufficient classes are:

| class | why it works |
|---|---|
| **one owner** (Corollary A1) | the balance telescopes to `V_phi(x_0) - V_phi(x)`, a state function under every field |
| **condition `D`** — `V_{theta'} = qW + const`, a uniform rescaling | every receipt rescales by one global `q`, so repricing is multiplication by `q` |

Outside those, repairing exactness would require the per-owner receipt record —
a source/dependency vector — which the architecture forbids and which is **not**
introduced here.

**What is NOT on the boundary, and must not be confused with it.** Under the
**retained forward architecture** — settle at the field in force, never reprice —
there is **no boundary at all**. Theorem S holds for every field family, every
world, every `sigma(theta)`. The programme's retained architecture is already on
the safe side of this line, and synthesis §16 already records that exact
history-free revaluation is *not* part of it. This study confirms that decision
was the load-bearing one.

---

## 15. Final synthesis

**1. What does current EBU measure?**
> The exact work-like physical action value of a finite action under the field
> in force: `E_theta(G) = V_theta(pre) - V_theta(post)`, equivalently the path
> integral of the current field, distributed to owners as common-path receipts
> summing to `E_theta`. It is a **process** valuation, it is **exact**, and it
> is unchanged by everything above.

**2. What could an entropy-like capacity scalar measure?**
> Not entropy. `C = I - W` is a **conserved-complement potential**: the
> complement of the reference burden with respect to an invariant fixed by the
> accounting identity. It is a genuine state function of the physical state on a
> reachable component, and under **every** field its total telescopes to
> `V_phi(x_0) - V_phi(x)` (Theorem A). What it is not: an integrating-factor
> construction (nothing is inexact — §6), a Lieb–Yngvason entropy (A4/A5 have no
> referent and CH fails — §7), or monotone along accessibility (48 ascending
> edges — §7).

**3. Under what exact conditions is one scalar sufficient?**
> **Forward architecture: unconditionally** (Theorem S) — every field family,
> no hypotheses. **Under retroactive revaluation: iff no share diamond exists**
> (Theorem I); sufficient classes are one owner (Corollary A1) and condition `D`
> (uniform rescaling). And in **no** finite world is the scalar *minimal*: on
> Study-1 every settlement is an integer, so the fractional part of `c` is
> information no future can ever use (Theorem M).

**4. When does omitted history necessarily reappear as memory?**
> Exactly when the architecture applies to the wallet an operator that is not a
> function of `(c, x, theta)`. Retroactive field revaluation is the only such
> operator in the declared design. No future **action** ever reveals the omitted
> history (Theorem S); only a reach-back does. In the witness the memory term is
> exactly `4/9` — finite and algebraic, not a decaying kernel.

**5. What is the precise role of accessibility?**
> Diagnostic, and negative. Constructing `≺` first and asking for a
> representation shows that EBU freedom is **neither** a state ranking (no
> order-reflecting `F`: `2406` of `4095` pairs incomparable) **nor** an
> accessibility potential for `C` (48 `W`-ascending menu edges). `C` earns its
> status from a **conservation law**, not from an order. The extra hypothesis
> that would make `C` an accessibility potential — a `W`-nonincreasing menu — is
> a declaration about the action generator, and on the frozen generator it is
> false.

**6. Does sign disagreement between EBU and capacity invalidate the theory?**
> **No.** It is a precise, already-recorded failure of condition B, produced by
> two positive weightings of the *same* mixed-sign per-coordinate terms. It is
> **not** the `delta Q` / `dS` phenomenon — both EBU forms are exact, so the
> thermodynamic mechanism has no counterpart — and it becomes a contradiction
> only under a current-field accessibility axiom the programme has not declared.
> The real obstacles to an entropy reading are elsewhere (§7), and they do not
> involve signs of `E_theta`.

**7. Is `C` in `C + W = I` legitimately interpretable as decentralized physical
freedom?**
> As a **potential**, yes; as an **accessibility** coordinate, no (§7). And the
> "reserve versus stored damage potential" ambiguity is **not** a matter of
> interpretation: it is decided by whether the gate funds `W`-increasing actions
> out of an existing balance. **Under V1 it does** — 48 such edges exist on the
> frozen graph, each settling a negative integer — so the damage reading has literal
> operational content there. Capacity V2 is precisely the mechanism that answers
> the question the other way, and it breaks `C + W = I` by design. The
> freedom–equilibrium theorem remains a theorem about V1 accounting and does not
> re-legitimize what V2 removed.

**8. What is the maximal dynamic-field class compatible with one scalar and no
history?**
> **Under forward settlement: all of them** — every Gaussian family, every
> `sigma(theta)`, moving or fixed `x*`, any number of owners. **Under retroactive
> revaluation: exactly the single-owner case together with the uniform-rescaling
> class `D`** (plus reference motion along `span(sigma_i^2)`, which changes no
> EBU value) — and those field changes alter no admissibility decision at all.

### What this study changes in the programme record

| synthesis row | change |
|---|---|
| §13 Claim B / Theory III §4 no-go | **not withdrawn** — but it does **not** answer the sufficiency question, because its two histories end at different physical states. §5.2 supplies the witness that does |
| §15 individual vs aggregate freedom | **sharpened to a recoverability statement** (Theorem A): the total is a state function under every field; the split is under none, outside the two classes of §14 |
| §5 the damage-potential warning | **given an operational test** rather than left as a valence ambiguity (§8) |
| §16 no history vector | **confirmed as the load-bearing decision**: the forward architecture has no boundary; the excluded revaluation is the only thing that creates one |
| — | **new**: `c` is sufficient but never minimal on a finite world (Theorem M) |
| — | **new**: `C` is not an accessibility potential — 48 ascending menu edges (§7) |
| — | **new**: exactness and sufficiency are logically independent in both directions (§12) |

### No mechanism implementation

No mechanism was implemented, no history vector was introduced, no source
portfolio was introduced, Study-1 was not modified, the atomic P implementation
was not modified, and Stage A/B were not run. The only file changed is
`dynamic_ebu_theory_checks.py`, which gains the `SS-*` section: **306
deterministic checks, 0 failures**, exact `Fraction`, tolerance zero, no
randomized search.

---

# VERDICT

```
ONE-SCALAR CAPACITY VALID ONLY FOR [ the forward-settled architecture, where it
is exactly sufficient for every field family but strictly non-minimal; and,
under retroactive revaluation, only for a single owner or for the uniform-
rescaling class V_theta' = q V_theta + const, which alters no admissibility
decision ]
```

END TASK.
