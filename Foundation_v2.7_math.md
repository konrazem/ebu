# Energy Balance Project — Foundation Note V2.7 (mathematics)

**Status:** mathematical specification only. **No change is made to the physical
engine.** The claims here are labelled by epistemic status
(*Theorem* / *Proof sketch* / *Numerical observation* / *Regression test (proposed)*
/ *Conjecture*). A companion `test_math.py` is proposed in §8 as numerical
*validation* of the derived bounds; passing tests are validation, **never proof**.

This note answers one question: *is the EBP local actor law genuinely derived from
a global functional, or does it merely resemble that functional's gradient?* The
short answer (§7): the current law is exactly the projected gradient of
`B_homeostasis + B_transport`, but it is **not** the gradient of the full
regenerative functional `V_total`; the missing term is the reserve marginal
`−2χ_i(R_i−x_i)₊`, which V2.4's `threshold_penalty`/`hard_reserve` rules add by hand.

---

## 0. Notation

Lattice `Λ` of cells `i`, von Neumann 4-neighbourhood `𝒩(i)`, edge set
`E = {(i,j) : j ∈ 𝒩(i)}`. Graph distance `dist(i,k)` = fewest edges between cells.
State `x = (x_i)`, `x_i ∈ [0, K_i]`. Per-cell parameters (all from
[energy_balance.py](energy_balance.py)):

| symbol | meaning |
|---|---|
| `K_i` | capacity (upper bound) |
| `L_i ≤ U_i` | viable band |
| `α_i, β_i ≥ 0` | deficit / excess penalty weights |
| `s_i ≥ 0` | external inflow |
| `d_i ≥ 0` | demand / metabolism |
| `λ_i ≥ 0`, `κ_i ≥ 0` | constant leak, proportional leak (`leak_frac`) |
| `ρ_i ≥ 0`, `A_i ≥ 0` | regeneration rate, Allee threshold |

Clip operator `Π_i(v) = min(max(v,0), K_i)`. Regeneration (`regen_at`):

```
g_i(x) = 0                              if ρ_i ≤ 0 or K_i ≤ 0
       = ρ_i x (1 − x/K_i)              logistic          (A_i = 0)
       = ρ_i x (1 − x/K_i) (x/A_i − 1)  Allee, signed      (A_i > 0)
```

Local homeostatic penalty and its marginal (`local_penalty`, `mu`):

```
ℓ_i(x)  = α_i [L_i − x]₊² + β_i [x − U_i]₊²
ℓ_i'(x) = −2α_i (L_i − x)   for x < L_i
        =  2β_i (x − U_i)   for x > U_i
        =  0                for L_i ≤ x ≤ U_i     (flat interior)
```

`[·]₊ = max(·,0)`. `B_homeostasis(x) = Σ_i ℓ_i(x_i)` is the burden of the README.

---

## 1. The dynamics — two clearly separated models

### 1.1 Model D — the discrete map the engine actually runs

This is the object of record; `energy_balance.py` implements exactly this. One tick
is the composition `T = A ∘ N` of a natural on-site map `N` and an actor transport
map `A`.

**Natural map `N`** (one cell, order = inflow, regen, demand, leak, clip):

```
(N x)_i = Π_i( x_i + s_i + g_i(x_i) − d_i − λ_i − κ_i x_i )                    (D.1)
```

*Variant note.* `energy_balance.py` forms the sum and clips once (D.1). The
ledger-safe `nat_cell` in [ebu_v23.py](ebu_v23.py) applies regen/leak/demand as
sequential non-negative clamps so no intermediate goes below 0. The two agree
whenever the cell stays in `(0, K_i)` over the tick; they differ only at the `0`
and `K_i` boundaries, where D.1 can clip a negative intermediate to 0 in one shot.
All §3–§4 results are stated for D.1 and hold for the interior dynamics of both.

**Actor map `A`** on the post-natural state `y = N x`. With marginals
`μ_i = ℓ_i'(y_i)`, each actor at cell `i` selects the steepest feasible out-edge

```
j*(i) = argmax_{j ∈ 𝒩(i)}  F_ij ,   F_ij = μ_i − μ_j − θ                       (D.2)
```

acts only if `F_{i j*} > 0`, proposes gross flux `q = M · F_{i j*}` (linear-flux
rule `q = M[F]₊`), then `q` is feasibility-capped `q̃` (destination headroom
`K_j − y_j`, source floor `y_i − x_min,i`, `q_max`, and proportional conflict
scaling when one source is oversubscribed). The committed update is

```
y_i  ← y_i − (q̃ + c0)
y_j* ← y_j* + η · q̃          (η ∈ (0,1]; transport loss (1−η)q̃ + c0 ≥ 0)      (D.3)
```

`x(t+1) = y`. The gains `M` (actor) and `ρ` (regeneration) double as **step sizes**;
this is why the stability results below are step-size conditions.

### 1.2 Model C — a continuous-time approximation (labelled as such)

Reading D.1/D.3 as a forward-Euler step with `Δt = 1`, the `Δt → 0` limit is

```
ẋ_i = s_i + g_i(x_i) − d_i − λ_i − κ_i x_i
      + Σ_{j∈𝒩(i)} ( η J_{ji} − J_{ij} ),   J_{ij} = M [ μ_i − μ_j − θ ]₊       (C.1)
```

**Model C is an approximation, not the engine.** Two discrete phenomena proved
below vanish in Model C: the harvest flip bifurcation (§3, stability needs
`ρ√D < 2`, a `Δt=1` artifact) and transport overshoot (§5, `M ≤ 1/(α+β)`, likewise).
Continuous gradient flow descends `V` unconditionally; the discrete map does not.
Analyses that must reflect engine behaviour therefore use **Model D**.

---

## 2. Candidate global functional and the derived local law

The README functional `B_homeostasis` alone is provably blind to regenerative
danger (§5, and the V2.3 collapse): a cell can sit inside `[L_i, U_i]` with
`ℓ_i = 0` while `x_i < A_i`, i.e. already inside the Allee death basin, and its
marginal `μ_i = 0` gives the actor no signal. We therefore propose a **decomposable**
functional, every term a sum of local cell or local edge contributions:

```
V_total(x) = B_homeostasis + B_regeneration + B_transport

B_homeostasis = Σ_i  ℓ_i(x_i)                                                  (2.1)
B_regeneration = Σ_{i : ρ_i>0, A_i>0}  χ_i [R_i − x_i]₊² ,   R_i = A_i + δ_i    (2.2)
B_transport   = Σ_{(i,j)∈E}  θ_ij · f_ij      (f_ij ≥ 0 flow on edge)          (2.3)
```

**Derived local chemical potential.** Because every term is on-site or on-edge,

```
μ_i^tot = ∂V_total/∂x_i = ℓ_i'(x_i) + r_i'(x_i),
r_i'(x) = −2χ_i (R_i − x)   for x < R_i,   0 otherwise.                         (2.4)
```

The derived edge signal is the difference of local potentials minus the edge's own
marginal transport cost:

```
F_ij^derived = μ_i^tot − μ_j^tot − θ_ij.                                       (2.5)
```

**Locality of the derived law (as required).** Evaluating `F_ij^derived` needs only
`x_i`, the adjacent `x_j`, and cell-local constants (`L,U,α,β,χ,R,A,θ`). No global
quantity enters. `B_regeneration` uses each cell's *own* `A_i`; it does **not**
require a diffused danger field. (If a future variant introduces a propagated
danger signal, §6 requires it propagate by local hops, not a global solve.)

*Remark.* `B_regeneration` is exactly the `pen`/`marg` augmentation implemented in
[ebu_v24.py](ebu_v24.py) (`v += χ (R_i − x)²`, `μ += −2χ(R_i − x)`), there added as
a *rule choice*, not derived from a stated functional. §7 makes this identification
precise.

*Remark on dissipation.* The `(1−η)q̃` transport loss and `c0` in D.3 are **not**
part of the reversible potential `V_total`; they are dissipation. The correct
book-keeping is the inequality form `ΔV ≤ (external drive) − (local dissipation)`,
not `ΔV ≤ 0`. Proving a clean global inequality for the full driven system is left
as Conjecture C-1 (§7).

---

## 3. Logistic harvest — existence is not sustainability

Isolated logistic source, constant net harvest `h` (single cell, `s=λ=κ=0`,
interior of D.1): `x_{t+1} = φ(x_t)`, `φ(x) = x + ρx(1 − x/K) − h`.

> **Theorem 3.1 (equilibria exist iff `h ≤ h*`).** With `h* = ρK/4` and
> `D = 1 − 4h/(ρK)`, the interior fixed points of `φ` are
> `x_±(h) = (K/2)(1 ± √D)`, real iff `h ≤ h*`. At `h = h*` they merge at `x = K/2`
> (saddle-node / fold).

> **Theorem 3.2 (stability and the collapse threshold).** `φ'(x) = 1 + ρ(1 − 2x/K)`,
> so `φ'(x_±) = 1 ∓ ρ√D`. Hence:
> - `x_−` is **always unstable** (`φ'(x_−) = 1 + ρ√D > 1`); it is the collapse
>   threshold.
> - `x_+` is locally asymptotically stable **iff** `0 < ρ√D < 2`. When `ρ√D > 2`
>   it loses stability by a flip (period-doubling) bifurcation.

> **Corollary 3.3 (sustainability conditions — corrected).** A logistic source
> persists to a viable steady state **iff all three** hold:
> **(i)** existence `h ≤ ρK/4`; **(ii)** initial condition `x(0) > x_−(h)` (basin);
> **(iii)** discrete stability `ρ√D < 2`. Condition (i) alone — the claim in the
> first draft of this note — establishes only *existence* of an equilibrium, not
> that any trajectory reaches or stays at it.

*Proof sketch.* Standard scalar-map analysis: solve `ρx(1−x/K)=h` for the roots;
linearise `φ` at each; `|φ'|<1` gives local attraction, `|φ'|>1` repulsion; the flip
occurs when `φ'(x_+)` crosses `−1`, i.e. `ρ√D = 2`. Below `x_−`, `φ(x) < x`, so
iterates decrease monotonically to the absorbing state `0`. ∎

*Numerical observation (validates 3.1–3.3, `ρ=0.4, K=20, h*=2`).*

| `h` | `x_−` | `x_+` | start `x_−−0.05` | start `x_−+0.05` | `|φ'(x_+)|` | `|φ'(x_−)|` |
|---|---|---|---|---|---|---|
| 1.00 | 2.9289 | 17.0711 | → 0 (collapse) | → 17.071 | 0.717 | 1.283 |
| 1.60 | 5.5279 | 14.4721 | → 0 (collapse) | → 14.472 | 0.821 | 1.179 |
| 1.99 | 9.2929 | 10.7071 | → 0 (collapse) | → 10.707 | 0.972 | 1.028 |

Flip check (`h = 0.3 h*`): `ρ ≤ 2.2` (`ρ√D ≤ 1.84`) → fixed point; `ρ = 2.6`
(`ρ√D = 2.18 > 2`) → sustained 2-cycle `20.0 ↔ 16.1`. Matches Theorem 3.2.

---

## 4. Allee reserve under driving — the reserve is not `x = A`

> **Theorem 4.1 (invariant reserve, isolated undriven case).** For the isolated
> undriven Allee source `ẋ = ρx(1−x/K)(x/A−1)` (equivalently the interior of D.1
> with `s=d=λ=κ=h=0`), the equilibria are `{0, A, K}`; `0` and `K` are stable, and
> `x = A` is the **unstable** equilibrium separating the collapse basin `(0,A)` from
> the recovery basin `(A,K)`. **This is the only case in which the basin boundary
> equals `A`.**

> **Theorem 4.2 (reserve shift under drive).** Add constant local drive: harvest
> `h`, demand `d`, leak `λ + κx`, supply `s`. The persistence boundary is the
> unstable middle root `x_r` of
>
> ```
> G(x) = ρ x (1 − x/K)(x/A − 1) + s − d − λ − κx − h = 0.               (4.1)
> ```
>
> At that root `G'(x_r) > 0`, so by the implicit function theorem
>
> ```
> ∂x_r/∂h = ∂x_r/∂d = ∂x_r/∂λ = 1/G'(x_r) > 0,
> ∂x_r/∂κ = x_r/G'(x_r) > 0,     ∂x_r/∂s = −1/G'(x_r) < 0.               (4.2)
> ```
>
> Harvest, demand and leakage **raise** the reserve (a driven source must hold
> *more* than `A`); external supply **lowers** it (supply can rescue a source below
> `A`). Transport *out* of a source enters as harvest (raises `x_r`); transport
> *in* enters as supply (lowers `x_r`).

*Proof sketch.* `x_r` is the middle root where `G` crosses `−→+`, hence
`G'(x_r) > 0`. Differentiate `G(x_r; p) = 0` in each parameter `p` and solve
`∂x_r/∂p = −(∂G/∂p)/G'(x_r)`, using `∂G/∂h = ∂G/∂d = ∂G/∂λ = −1`,
`∂G/∂κ = −x_r`, `∂G/∂s = +1`. ∎

*Numerical observation (validates 4.1–4.2, `ρ=0.6, K=20, A=5`).* Undriven middle
root `= 5.0 = A`. Driven middle root: `h=0.5 → 5.99`; `d=0.5 → 5.99`; `κ=0.05 →
5.58` (all `> A`); `s=0.5 → 3.58` (`< A`). Signs match (4.2).

*Consequence for the actor.* The quantity a foresightful actor must protect is
`x_r`, a function of that cell's *local* drive and its edge flows — computable from
local data. V2.4's fixed reserve `R_i = A_i + δ_i` is a **constant surrogate** for
`x_r`; §7 notes this and Conjecture C-2 asks when the surrogate dominates `x_r`.

---

## 5. The descent condition — analytic bound, not a magic number

The first draft reported `M_crit ≈ 1.79` as if it were structural. It is not; it is
one fixture's numerical threshold. The structural statement is a sufficient
step-size bound.

Consider one actor edge `(i,j)`, post-natural state `y`, lossless `η=1`, `c0=0`
(costs and `θ` only shrink the step). Along the conservative transfer
`q ↦ (y_i − q, y_j + q)` define

```
ψ(q) = ℓ_i(y_i − q) + ℓ_j(y_j + q)   [+ reserve terms r_i, r_j if present].
```

`ψ` is convex (sum of convex piecewise-quadratics), and `ψ'` is Lipschitz with
constant `Λ_ij = 2(α_i + β_j)` in the active (out-of-band) regions and `0` in the
flat viable band. The actor's committed flux is a projected gradient step
`q = M·[−ψ'(0) − θ]₊` with step size `M`.

> **Theorem 5.1 (sufficient descent).** If `M ≤ 2/Λ_ij = 1/(α_i + β_j)` (more
> generally `M ≤ 1/max-curvature` over the regions the step traverses), then
> `ψ(q) ≤ ψ(0)`: the transport substep does not increase `V_total`. `θ ≥ 0` and the
> feasibility caps only reduce `q`, preserving the inequality.

*Proof sketch.* Descent lemma for an `L`-smooth convex function `f`:
`f(x − t∇f) ≤ f(x)` for `0 < t ≤ 2/L`. Apply with `f = ψ`, `L = Λ_ij`, `t = M`. ∎

> **Numerical observation (validates 5.1, and explains 1.79).** Bisected empirical
> `M_crit` for burden-monotonicity, `(α,β) = (1, 0.5)` unless noted:
>
> | band | sufficient `1/(α+β)` | empirical `M_crit` |
> |---|---|---|
> | wide `[5,15]` | 0.667 | 1.788 |
> | narrow `[9.9,10.1]` | 0.667 | 0.676 |
> | zero-width | 0.667 | 0.668 |
> | zero-width, `α=β=1` | 0.500 | 0.501 |
>
> As the viable band shrinks to zero, the flat zero-penalty slack disappears and the
> empirical threshold converges to the analytic bound. The `1.79` of a wide band is
> **band slack**, not structure: a step may overshoot the near edge yet still land
> in the flat interior. `1.79` is retained only as a fixture-specific number.

> **Regression test (proposed, §8).** Assert `M ≤ 1/(α_i+β_j)` ⇒ per-tick burden
> non-increasing on the closed two-cell fixture, across band widths. This
> *validates* Theorem 5.1; it does not prove it.

*Why V2.2 needs no such condition.* The V2.2/V2.4 "safe" rule replaces `q = M·F`
with the line-searched minimiser of `ψ` (`_golden_min`) gated on `ψ(q) < ψ(0)`
([ebu_v24.py](ebu_v24.py) lines 145–152). That is the *exact* one-dimensional
minimiser plus an accept-only-if-descending gate, so it lowers `ψ` for **any** `M`.
Theorem 5.1 is precisely the condition under which the raw V2.0 flux may skip that
line search safely.

---

## 6. Finite causal speed

> **Theorem 6.1 (locality / bounded signal speed, Model D).** Under `T = A ∘ N`,
> `x_i(t + n)` is a function only of `{ x_k(t) : dist(i,k) ≤ n }`. Equivalently, a
> perturbation at cell `k` cannot influence cell `i` in fewer than `dist(i,k)`
> ticks: the causal speed is `≤ 1` cell per tick.

*Proof sketch.* `N` (D.1) is on-site: `(Nx)_i` depends only on `x_i` (0 hops). `A`
(D.2–D.3) reads `μ_i` and `μ_{j∈𝒩(i)}` and moves mass only across single edges, so
each committed update to `y_i` depends on state within 1 hop. Thus one tick has
dependency radius 1; compose `n` ticks and induct: the domain of dependence of `i`
after `n` ticks is the graph ball `{k : dist(i,k) ≤ n}`. Conflict-resolution scaling
couples only actors drawing on a **common** source cell — all within 1 hop of that
cell — so it does not enlarge the radius. ∎

**Non-local approximations — flagged.** (a) `B_homeostasis`, `B_regeneration` and
`V_total` are global sums, but they are used only for *evaluation*; no actor reads
them, so Theorem 6.1 stands. (b) The horizon rules (V2.3/V2.4) roll a *local*
`radius`-bounded counterfactual (`_radius_cells`, radius 2) — local, not global.
(c) **If** any future `V_total` variant computes a signal/danger field by a global
or instantaneous solve (e.g. an elliptic pressure solve each tick), Theorem 6.1
fails and that step **must be labelled a non-local approximation** with its own
convergence and locality analysis. Nothing in the present engine does this.

---

## 7. Is the present law derived from `V_total`, or does it resemble its gradient?

Collecting §2 and §5:

**What is genuinely derived.** The V2.0/V2.2 driving force (D.2) is
`F_ij = μ_i^hom − μ_j^hom − θ`, which is exactly the edge gradient of
`B_homeostasis + B_transport` (2.5 with `χ = 0`). The actor performs *greedy
(steepest-edge) projected gradient descent* on those two terms — genuinely their
gradient, realised either as a bounded step (Theorem 5.1) or as the exact line
search (V2.2). For `B_homeostasis + B_transport`, the law **is** derived, not merely
resembling.

**What is missing.** The present default/`safe` law is **not** the gradient of the
full `V_total`. The gap is exactly the regeneration marginal

```
∂B_regeneration/∂x_i = −2χ_i (R_i − x_i)₊     (regenerative cells only).       (7.1)
```

With `χ = 0` (the engine default) the actor is blind to regenerative danger:
`μ_i^hom = 0` whenever `L_i ≤ x_i ≤ U_i`, even if `x_i < A_i ≤ R_i`. This is the
mechanism of the V2.3 collapse — `B_homeostasis` can be zero while a source crosses
its Allee threshold.

**Where the missing term already lives.** V2.4's `threshold_penalty` and
`penalty_horizon` rules add precisely (2.2) and its marginal (7.1)
([ebu_v24.py](ebu_v24.py), `pen`/`marg`), and `hard_reserve` adds a non-smooth
barrier surrogate for the same term. These are **hand-installed approximations of
`∂B_regeneration/∂x`**, selectable per run, not consequences of a declared
functional.

**Conclusion.** The present EBP local law is the projected gradient of
`V_total − B_regeneration`. The difference from the `V_total`-derived law (2.5) is
exactly the reserve marginal (7.1) on regenerative cells — supplied today only when
`threshold_penalty`/`penalty_horizon`/`hard_reserve` is chosen, absent from the
default and `safe` laws. **No implementation change is made in this note**; this is
the specification of the gap. Two further caveats, kept as conjectures:

- **Conjecture C-1 (dissipative Lyapunov inequality).** For the full driven system
  there exist local dissipation and drive terms giving
  `V_total(x(t+1)) − V_total(x(t)) ≤ Σ_i (drive_i) − Σ_{edges} (loss)` under the
  derived law with `M ≤ 1/max-curvature`. (§2 remark; unproven here.)
- **Conjecture C-2 (reserve surrogate).** V2.4's constant `R_i = A_i + δ_i`
  dominates the true driven reserve `x_r` of Theorem 4.2 (hence is safe) iff
  `δ_i ≥ x_r − A_i` over the operating envelope of local drive and edge flow.

---

## 8. Proposed regression tests (`test_math.py`) — validation, not proof

To be added **after** this note, and described as numerical validation only:

1. **Fold & basin (Thm 3.1–3.3):** for a grid of `h < h*`, assert engine
   equilibrium matches `x_+(h)` to tolerance, and that `x(0) = x_−(h) ± ε`
   lands in the collapse / recovery basin respectively.
2. **Flip (Thm 3.2):** assert a sustained 2-cycle appears once `ρ√D > 2`.
3. **Driven reserve (Thm 4.2):** assert the numerically located middle root moves
   in the signed directions of (4.2) for `h, d, λ, κ, s`.
4. **Descent bound (Thm 5.1):** assert `M ≤ 1/(α_i+β_j)` ⇒ per-tick burden
   non-increasing on the two-cell fixture across band widths; record (do not
   assert as structural) the wider empirical `M_crit`.
5. **Locality (Thm 6.1):** assert a single-cell perturbation leaves cells at graph
   distance `> n` bit-identical after `n` ticks.

None of these constitutes a proof; each is a guard that the engine has not drifted
from the analysis above.

---

## 9. Summary of corrections to the first draft

| First-draft claim | Corrected statement |
|---|---|
| `h ≤ ρK/4` ⇒ sustainable | existence of equilibria only; also need basin `x(0) > x_−(h)` and `ρ√D < 2` (Thm 3.1–3.3) |
| `x = A` is the basin boundary | true only for the isolated undriven Allee source; under drive it is `x_r` of `G(x)=0` (Thm 4.1–4.2) |
| `M_crit ≈ 1.79` (as a theorem) | numerical, fixture-specific; the theorem is the sufficient bound `M ≤ 1/(α_i+β_j)`, tight as band width → 0 (Thm 5.1) |
| `V = B_homeostasis` | `B_homeostasis` is blind to Allee danger; use `V_total = B_hom + B_reg + B_tr` (§2, §7) |
| law "is" the gradient of `B` | law is the gradient of `V_total − B_regeneration`; the missing term is `−2χ_i(R_i−x_i)₊` (§7) |
