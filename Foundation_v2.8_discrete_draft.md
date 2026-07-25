# Energy Balance Project — Foundation Note V2.8 (discrete, DRAFT)

**Status: mathematics-first DRAFT for independent review. No engine, test, or metadata
is changed by this gate.** V2.7 proved a *continuous-time* energy–dissipation identity
for a smooth, unconstrained, simultaneous Onsager flow (Model C). This draft derives a
*discrete-time* counterpart for the **simplest compatible synchronous system (Model
D0)** and states precisely why that result does **not** yet cover the actual Python
engine (Model DE).

Epistemic labels are used strictly: **Definition / Assumption / Lemma / Theorem /
Corollary / Proof / Proof sketch / Counterexample / Conjecture / Proposed numerical
validation.** Numerical experiments are never used as proof.

---

## 1. Purpose and relationship to V2.7

V2.7 (Theorem 7.1) established, in continuous time, for the derived Onsager flow
`ẋ = u(x) + S J(x)`:

```
dV/dt = Σ_i μ_i u_i − Σ_e ( J_e²/M_e + θ_e J_e )   ≤   Σ_i μ_i u_i .
```

The Python engine does not run this flow. It advances in ticks of size `Δt = 1`,
applies **natural drive and transport as two ordered sub-steps**, evaluates the
transport force **loss-blind** (`μ_i − μ_j − θ`), applies accepted transfers
**sequentially against live state**, and **clips** to `[0,K]`. Theorem 7.1 explicitly
excluded all of that.

This draft takes the first step across that gap: a **synchronous, unconstrained,
loss-aware, explicit-Euler** discretisation (D0), for which we prove a discrete
descent inequality with an *explicit* finite-step remainder, a one-edge sufficient
step-size condition, a conservative graph-level condition, a conservation/loss ledger,
and a one-tick locality theorem — while cataloguing, with counterexamples, exactly
where the result stops.

---

## 2. Notation

**Definition 2.1 (state and functional).** State `x ∈ ℝⁿ` (unconstrained here — no
`[0,K]` box; see §11). Separable state functional and local potential
```
V(x) = Σ_i v_i(x_i),      μ_i(x) = ∂V/∂x_i = v_i'(x_i),      μ(x) = ∇V(x).
```
For the burden functional of the project,
`v_i(x) = α_i[L_i − x]₊² + β_i[x − U_i]₊² (+ χ_i[R_i − x]₊² on regenerative cells)`,
so `∇V` is piecewise-linear and continuous, and `V ∈ C¹` (each `v_i ∈ C¹`, `v_i''` a
step function taking values in `{0, 2α_i, 2β_i, 2χ_i, …}`).

**Definition 2.2 (directed lossy edge).** For an edge `e = (i,j)` with efficiency
`η_e ∈ [0,1]`, the state-change column `S_e ∈ ℝⁿ` has `(S_e)_i = −1`, `(S_e)_j = +η_e`,
all other entries `0`. A scalar transfer `q_e` maps `x ↦ x + q_e S_e`, i.e.
`x_i ↦ x_i − q_e`, `x_j ↦ x_j + η_e q_e`. Stack columns into `S ∈ ℝ^{n×|E|}` and fluxes
into `J ∈ ℝ^{|E|}`, so total transport is `S J = Σ_e J_e S_e`.

**Definition 2.3 (loss-aware force and Onsager flux).** The force is the negative
directional derivative of `V` along the transfer direction:
```
f_e(x) = −∇V(x)ᵀ S_e = −( μ_i·(−1) + μ_j·(η_e) ) = μ_i − η_e μ_j .
```
With threshold `θ_e ≥ 0` and mobility `M_e > 0`, the raw Onsager flux is
```
J_e(x) = M_e [ f_e(x) − θ_e ]₊ = M_e [ μ_i − η_e μ_j − θ_e ]₊ .
```
(The sign/convention is derived, not assumed; §10 counterexample D shows `μ_i − μ_j`
is the *wrong* force when `η_e < 1`.)

**Definition 2.4 (natural drive).** `u(x) ∈ ℝⁿ`, `u_i(x) = s_i + g_i(x_i) − d_i − λ_i −
κ_i x_i`, collecting supply, regeneration, demand, constant and proportional leak
(unconstrained: no saturation/clipping here).

**Assumption 2.5 (L-smoothness of V).** `∇V` is `L`-Lipschitz on the relevant region
in the Euclidean norm `‖·‖₂`. Because `V` is separable with diagonal Hessian whose
entries lie in `{0, 2α_i, 2β_i, 2χ_i}`, a **global** constant is
```
L = 2 · max_i max(α_i, β_i, χ_i) .
```
All norms below are `ℓ²` unless stated; `‖·‖₂` on matrices is the spectral norm.

---

## 3. Three models kept strictly separate

**Definition 3.1 (Model C — continuous Onsager law, V2.7).**
`ẋ = u(x) + S J(x)`, all quantities evaluated at the instantaneous `x(t)`; smooth,
unconstrained, simultaneous. Subject of Theorem 7.1.

**Definition 3.2 (Model D0 — ideal synchronous discrete law, this draft).**
Frozen-state, simultaneous, explicit (forward) Euler discretisation of C:
```
x^{n+1} = x^n + Δt ( u(x^n) + S J(x^n) ),         (D0)
```
**all** forces and fluxes evaluated from the single state `x^n`; no clipping, no
constraints, loss-aware force (Def 2.3). This is the subject of the new theorem.

**Definition 3.3 (Model DE — the existing engine).** The Python operator actually run.
Reconciled from `energy_balance.py` (`step`), `ebu_v24.py`, `ebu_v26.py`
(`forced_tick`): one tick is a **split** `x^{n+1} = A(N(x^n))` where
- `N` applies natural drive **first**, per cell, decoupled (`natural_update`);
- `A` then computes `μ` at the **post-drive** state `y = N(x^n)` (not at `x^n`),
  selects a single steepest edge per actor by the **loss-blind** force
  `F = μ_i − μ_j − θ`, sizes it either raw `q = M[F]₊` or by a golden-section line
  search, applies accepted transfers **sequentially against live state**, with
  proportional conflict scaling, feasibility caps, and **clipping to `[0,K]`**;
- the tick size is fixed at `Δt = 1`.

> **Assumption 3.4 (non-transfer of results).** A theorem about **D0** does **not**
> automatically hold for **DE**. D0 and DE are *different discretisations of the same
> Model C*, differing in at least seven ways (Def 3.3): operator splitting, the state
> at which `μ` is frozen (`x^n` vs `N(x^n)`), loss-aware vs loss-blind force,
> simultaneous vs sequential application, absence vs presence of conflict scaling,
> unconstrained vs clipped, and `Δt` free vs `Δt = 1`. §7 and §10 quantify the gaps.

---

## 4. One-edge derivation

### 4.1 Exact first-order identity

**Lemma 4.1 (first-order contribution).** For the D0 update (D0), writing
`Δx = x^{n+1} − x^n = Δt(u + SJ)` (all at `x^n`),
```
∇V(x^n)ᵀ Δx = Δt · ∇V(x^n)ᵀ u(x^n)  −  Δt Σ_e f_e J_e .
```

*Proof.* `∇V ᵀ Δx = Δt(∇V ᵀ u + ∇V ᵀ S J)`. Per edge, `∇V ᵀ S_e = μ·S_e = −f_e` by
Def 2.3, so `∇V ᵀ S J = Σ_e (−f_e) J_e = −Σ_e f_e J_e`. ∎

**Lemma 4.2 (edge dissipation identity).** For every edge,
```
f_e J_e = J_e²/M_e + θ_e J_e .
```
*Proof.* If the edge is **active** (`f_e > θ_e`, so `J_e = M_e(f_e − θ_e) > 0`), then
`f_e = J_e/M_e + θ_e`, and multiplying by `J_e` gives the claim. If **inactive**
(`f_e ≤ θ_e`, so `J_e = 0`), both sides are `0` (the case `J_e = 0` is checked
separately: `f_e J_e = 0` regardless of the sign of `f_e`, and
`J_e²/M_e + θ_e J_e = 0`). ∎

Combining, the first-order transport term is
`−Δt Σ_e (J_e²/M_e + θ_e J_e) ≤ 0` (each summand `≥ 0` since `J_e ≥ 0`, `θ_e ≥ 0`).

### 4.2 Discrete descent inequality (one edge, explicit remainder)

**Lemma 4.3 (descent lemma).** Under Assumption 2.5, for any `x, y` in the region,
`V(y) ≤ V(x) + ∇V(x)ᵀ(y−x) + (L/2)‖y−x‖²`.

**Theorem 4.4 (one-step discrete inequality).** Under Assumption 2.5, the D0 update
satisfies, with `Δx = Δt(u + SJ)`,
```
V(x^{n+1}) − V(x^n)
  ≤  Δt · ∇V(x^n)ᵀ u(x^n)
     − Δt Σ_e ( J_e²/M_e + θ_e J_e )
     + R_n ,        R_n := (L/2)‖Δx‖² = (L Δt²/2) ‖ u + S J ‖² .        (★)
```
Moreover the remainder splits explicitly, exposing the **drive–transport cross term**:
```
R_n = (L Δt²/2) ( ‖u‖²  +  2 uᵀ S J  +  ‖S J‖² ) .
```

*Proof.* Apply Lemma 4.3 with `x = x^n`, `y = x^{n+1}`; substitute Lemma 4.1 for the
first-order term and Lemma 4.2 for the edge sum; expand `‖u + SJ‖²`. ∎

**Remark 4.5 (norm and constant).** The bound uses the `ℓ²` norm and the global
smoothness constant `L = 2 max_i max(α_i,β_i,χ_i)` (Assumption 2.5). `R_n` is a genuine
explicit upper bound, **not** an unquantified `O(Δt²)`; the true forward-Euler local
truncation error is likewise `Θ(Δt²)` (§7).

---

## 5. Graph derivation

### 5.1 Undriven descent, one edge (exact-sufficient)

**Theorem 5.1 (one-edge step-size bound, `u = 0`).** For a single active edge
`e=(i,j)` with `u ≡ 0`, the D0 step satisfies `V(x^{n+1}) ≤ V(x^n)` whenever
```
Δt  ≤  2 / ( L · M_e · (1 + η_e²) ) .            (one-edge sufficient)
```
Including `θ_e` only relaxes this (the true admissible range is
`Δt ≤ (2/(L(1+η_e²)))·(1/M_e + θ_e/J_e)`).

*Proof.* With `u = 0`, (★) gives `V(x^{n+1}) − V(x^n) ≤ −Δt(J²/M_e + θ_e J) +
(LΔt²/2)‖S_e‖² J²`, where `‖S_e‖² = 1 + η_e²`. A sufficient condition for the RHS
`≤ 0` is `Δt(J²/M_e) ≥ (LΔt²/2)(1+η_e²)J²` (dropping the non-negative `θ_e J` term),
i.e. `Δt ≤ 2/(L M_e(1+η_e²))`. Keeping `θ_e J` yields the relaxed range. ∎

**Consistency check with V2.7 §5.** Setting `Δt = 1` gives `M_e ≤ 2/(L(1+η_e²))`; with
`L = 2w` (equal weights `w`), `M_e ≤ 1/(w(1+η_e²))` — identical to the V2.7 §5.2
symmetric single-transfer bound `M ≤ 1/(w(1+η²))`. Counterexample A (§10) shows this
bound is **tight** (necessary and sufficient) in the symmetric pure-quadratic case, so
it is not merely a loose sufficient condition there.

### 5.2 Undriven descent, graph (conservative sufficient)

**Theorem 5.2 (spectral step-size bound, `u = 0`).** Let `D_M = diag(M_e)` and
`‖·‖₂` the spectral norm. If
```
Δt  ≤  2 / ( L · ‖ S D_M^{1/2} ‖₂² ) ,            (graph sufficient)
```
then the D0 step satisfies `V(x^{n+1}) ≤ V(x^n)` for `u = 0`, **for every** flux
vector `J` (in particular the state-generated one).

*Proof.* From (★) with `u=0`, a sufficient condition is
`Jᵀ D_M^{-1} J ≥ (LΔt/2) Jᵀ SᵀS J` (dropping `θ`, using
`Σ_e J_e²/M_e = Jᵀ D_M^{-1} J` and `‖SJ‖² = Jᵀ SᵀS J`). Substitute `y = D_M^{-1/2}J`:
the condition becomes `‖y‖² ≥ (LΔt/2) yᵀ (D_M^{1/2} SᵀS D_M^{1/2}) y` for all `y`,
which holds iff `(LΔt/2)·λ_max(D_M^{1/2}SᵀS D_M^{1/2}) ≤ 1`. Since
`D_M^{1/2}SᵀS D_M^{1/2} = (S D_M^{1/2})ᵀ(S D_M^{1/2})`, its largest eigenvalue is
`‖S D_M^{1/2}‖₂²`. Rearrange. ∎

**Corollary 5.3 (one-edge special case).** For a single edge, `S D_M^{1/2} = √M_e S_e`,
`‖S D_M^{1/2}‖₂² = M_e(1+η_e²)`, recovering Theorem 5.1 exactly.

**Remark 5.4 (structure of `SᵀS`).** `(SᵀS)_{e,e'} = S_e·S_{e'}`: diagonal `1+η_e²`;
`+1` for two edges sharing their **source**; `η_e η_{e'}` for two sharing their
**destination**; `−η` when one edge's destination is the other's source. A Gershgorin
bound gives the cruder, fully explicit
`‖S D_M^{1/2}‖₂² ≤ max_e M_e[ (1+η_e²) + Σ_{e'≠e} |S_e·S_{e'}| ]`, a degree-weighted
quantity.

**Conjecture 5.5 (tight graph threshold).** Theorem 5.2 is conservative because it
demands the PSD inequality for *all* `J`, whereas the physical `J = M_e[f_e−θ_e]₊` is
state-determined and active only on a subset of edges. We **conjecture** a tighter,
state-dependent admissible `Δt` governed by the spectral norm of `S D_M^{1/2}`
restricted to the active edge set, but do **not** prove it here. (No empirical
threshold is claimed as a theorem.)

---

## 6. The discrete driven inequality (`u ≠ 0`)

**Theorem 6.1 (driven one-step inequality).** Under Assumption 2.5, (★) holds verbatim
for `u ≠ 0`. In particular `V` is governed by the competition of three terms:
```
V(x^{n+1}) − V(x^n)  ≤   Δt·μᵀu   −   Δt Σ_e(J_e²/M_e + θ_e J_e)   +   (LΔt²/2)‖u+SJ‖² .
                         └ drive ┘      └──── dissipation ────┘        └── remainder ──┘
```

**Corollary 6.2 (sufficient one-step decrease).** `V(x^{n+1}) ≤ V(x^n)` holds if
```
Σ_e ( J_e²/M_e + θ_e J_e )   ≥   μᵀu   +   (LΔt/2) ‖u + SJ‖² .
```
Two readings: (i) if `μᵀu ≤ 0` (drive already lowers `V`) and `Δt` is small enough for
dissipation to dominate the remainder, `V` decreases; (ii) if `μᵀu > 0` (drive raises
`V`), decrease requires transport dissipation to exceed the drive **plus** the remainder.

**Non-result 6.3.** `V` is **not** monotone in the driven case in general — Counterexample
C (§10) exhibits `u` making `V` strictly increase in one step despite valid transport
dissipation elsewhere. We claim only the conditional Corollary 6.2, never unconditional
descent.

---

## 7. Relationship to V2.7 (Model C)

- **Consistency (`Δt → 0`).** Dividing (★) by `Δt` and letting `Δt → 0`, `R_n/Δt =
  (L Δt/2)‖u+SJ‖² → 0`, recovering exactly the Theorem 7.1 identity
  `dV/dt = μᵀu − Σ_e(J_e²/M_e + θ_e J_e)`. **Theorem 7.1 is the `Δt→0` limit of (★).**
- **Local truncation error.** D0 is forward Euler; its per-step LTE is `Θ(Δt²)` (the
  `(L/2)‖Δx‖²` term is a rigorous upper bound on `V`'s Taylor remainder; the trajectory
  LTE of the state is `½Δt² ẍ + O(Δt³)`). Global error over a fixed horizon is `O(Δt)`.
- **Finite-`Δt` trajectories are not identical to C.** The Euler iterate departs from
  the continuous flow by the accumulated remainder; equality holds only in the limit.
- **Safe line search ≠ explicit Onsager flux.** DE's `safe` rule sets
  `q* = argmin_q V(x + q S_e)` (an exact one-dimensional minimiser, then gated on
  descent). That is *coordinate descent on V*, not `q = M_e[f_e−θ_e]₊`; the two agree
  only in degenerate cases. So D0 (explicit flux) and DE-safe are different laws
  (already established in V2.7 §2.1, §7).
- **Proving D0 does not prove DE.** Beyond the safe-vs-explicit point, DE differs by
  operator splitting, `μ` frozen at `N(x^n)`, the loss-blind force, sequential live
  state, conflict scaling, and clipping (Def 3.3, §10 B and D). Each is out of scope
  (§11).

---

## 8. Conservation and loss ledger

**Theorem 8.1 (synchronous stock balance).** With `1` the all-ones vector, the D0 step
changes total stock by
```
1ᵀ(x^{n+1} − x^n) = Δt [ 1ᵀ u(x^n)  −  Σ_e (1 − η_e) J_e(x^n) ] .
```
*Proof.* `1ᵀΔx = Δt(1ᵀu + 1ᵀSJ)` and `1ᵀS_e = (−1) + η_e = −(1−η_e)`, so
`1ᵀSJ = −Σ_e(1−η_e)J_e`. ∎

**Corollary 8.2 (loss is explained, not destroyed).** Since `η_e ≤ 1` and `J_e ≥ 0`,
transport removes exactly `Σ_e (1−η_e)J_e ≥ 0` units of stock — the **efficiency
loss**, an accounted outflow. If every edge is lossless (`η_e = 1`) then `1ᵀS_e = 0`
and transport conserves stock exactly; all stock change is then attributable to the
natural drive `1ᵀu`.

**Remark 8.3 (two different statements).** Stock balance (Theorem 8.1, about `1ᵀx`) and
Lyapunov descent (Theorem 4.4/6.1, about the potential `V`) are independent: `V` is not
a stock, and a lossy transfer that *reduces* `V` still *removes* physical stock. Keep
them separate.

---

## 9. Locality and causal speed

**Theorem 9.1 (one-tick dependency radius, D0).** Under the synchronous frozen-state
update (D0), `x^{n+1}_i` depends only on `{ x^n_k : dist(i,k) ≤ 1 }` (graph distance
via the edge set). By induction, `x^{n+m}_i` depends only on `{ x^n_k : dist(i,k) ≤ m}`:
information propagates at most one edge per tick.

*Proof.* `x^{n+1}_i = x^n_i + Δt( u_i(x^n) + (SJ)_i )`. `u_i` is on-site (0 hops).
`(SJ)_i = Σ_{e=(i,·)} (−J_e) + Σ_{e=(·,i)} (η_e J_e)`, and each incident `J_e =
M_e[μ_a − η_e μ_b − θ_e]₊` depends only on the two endpoints of `e`, i.e. on `x^n_i`
and its graph neighbours (1 hop). Hence one tick has dependency radius `1`; compose and
induct. ∎

**Counterexample / Observation 9.2 (sequential live state breaks this).** Model DE
applies accepted transfers **sequentially against live state**. Then a transfer on
`(i,j)` mutates `x_j` *before* a later transfer on `(j,k)` reads it, so `x^{n+1}_k` can
depend on `x^n_i` — a **2-hop** influence in a single nominal tick, even though each
individual transfer is local. (V2.7 §6 exhibits this concretely: on a `0→1→2` chain, a
`+0.5` perturbation at cell 0 moved cell 2 by `+0.124` in one tick under the sequential
engine, versus exactly `0` under a frozen-state simultaneous application.) Theorem 9.1
therefore holds for **D0 only**; DE's causal speed per tick is bounded not by 1 but by
the length of the longest chain of accepted transfers sharing cells in application
order.

---

## 10. Counterexamples

**Counterexample A (step above the bound increases `V`).** One edge `e=(i,j)`,
`η_e = 1`, `θ_e = 0`, weights `α = β = w` (both cells outside band, so `v'' = 2w`,
`L = 2w`). Let cell `i` sit at `x_i = U + d` (excess `d`) and cell `j` at `x_j = L − d`
(deficit `d`). Then `μ_i = 2wd`, `μ_j = −2wd`, `f_e = μ_i − μ_j = 4wd`, `J = M f_e =
4Mwd`. After the D0 step both deviations become `d − ΔtJ = d(1 − 4MwΔt)`, so
`V_after = 2w d²(1 − 4MwΔt)²`, while `V_before = 2wd²`. Hence
```
V_after > V_before  ⟺  |1 − 4MwΔt| > 1  ⟺  Δt > 1/(2Mw).
```
The one-edge bound (Theorem 5.1) here is `Δt ≤ 2/(L M (1+η²)) = 2/(2w·M·2) = 1/(2Mw)`.
So the bound is **exactly tight**: any `Δt` above it strictly increases `V` (e.g.
`w=M=1, d=1`: `Δt=0.6 ⇒ V: 2 → 3.92`). The step-size condition is therefore not
vacuous, and cannot be dropped.

**Counterexample B (sequential 3-cell over-propagation).** See Observation 9.2: the
`0→1→2` chain under sequential live-state application transmits a cell-0 perturbation to
cell 2 within one tick, exceeding the one-edge-per-tick propagation that Theorem 9.1
proves for the synchronous law. This invalidates any attempt to extend Theorem 9.1 to
DE unchanged.

**Counterexample C (drive increases `V` despite valid dissipation).** Single cell `c`
with `v_c(x) = β[x − U]₊²`, at `x^n_c = U` (`μ_c = 0`), constant supply `u_c = s > 0`,
no incident active edge. Elsewhere in the graph a separate active edge dissipates
normally. The `c`-update gives `x^{n+1}_c = U + Δt s`, so `V` gains `β(Δt s)² > 0` from
`c` alone. Transport dissipation on the far edge cannot offset a *local* drive term at
`c`. Hence driven `V` is not monotone (supports Non-result 6.3); only the conditional
Corollary 6.2 survives.

**Counterexample D (loss-blind force is wrong for `η < 1`).** Take `η_e = 0.5`,
`θ_e < 1`, and endpoint potentials `μ_i = −3`, `μ_j = −4` (both cells in deficit, `j`
more deficient). The **loss-blind** rule uses `g_e = μ_i − μ_j = 1 > θ_e` and would
transfer `i→j`. But the **true** loss-aware force is `f_e = μ_i − η_e μ_j = −3 −
0.5·(−4) = −1 < 0`. By Lemma 4.1 the first-order change from this edge is
`−f_e·(ΔtJ) = +ΔtJ > 0`: the loss-blind transfer **increases** `V` to first order,
because at `η = 0.5` the efficiency loss wastes more than the deficit relief it buys.
The correct variational force is `f_e = μ_i − η_e μ_j` (Def 2.3), **not** `μ_i − μ_j`.
This is exactly why DE (which uses `μ_i − μ_j − θ`) is not guaranteed descending under
loss, and why D0 must use the loss-aware force.

*Effect on the theorems.* A, C, D do not invalidate the D0 results — they confirm the
necessity of (respectively) the step-size condition, the driven caveat, and the
loss-aware force. B invalidates only the *extension* of the locality theorem to DE,
which we accordingly restrict to D0.

---

## 11. Exact scope and exclusions

**The D0 theorems (4.4, 5.1, 5.2, 6.1, 8.1, 9.1) hold only for the synchronous,
unconstrained, loss-aware, explicit-Euler law of Def 3.2.** Each mechanism below is
**excluded** and, we indicate, the framework its rigorous treatment will likely need:

| Excluded mechanism | Likely framework |
|---|---|
| clipping / projection at `0` and `K` | projected dynamical systems / variational inequalities |
| spill at `K` | one-sided projection / complementarity |
| unmet-demand saturation (`min(d, ·)`) | nonsmooth / Filippov / piecewise-smooth analysis |
| hard-reserve constraints | constrained optimisation (KKT) / barrier methods |
| fixed activation cost `c₀` | hybrid / impulsive systems (discontinuous jumps) |
| safe golden-section / coordinate line search | operator splitting with exact prox; coordinate-descent theory |
| sequential live-state transfers | Gauss–Seidel operator splitting (vs Jacobi) |
| horizon optimisation | optimal control / dynamic programming |
| global / instantaneous field solves | elliptic PDE / implicit (nonlocal) solves |
| ledger incentives, EBU issuance | mechanism design — no dynamical-descent claim applies |

Also excluded from D0 but present in DE and unaddressed here: **operator splitting**
(drive `N` then transport `A`) and **`μ` frozen at `N(x^n)`** rather than `x^n`. These
alone make D0 ≠ DE even before constraints; a Lie/Strang-splitting error analysis is
the natural next tool.

---

## 12. Proposed numerical validation plan (NOT proof)

For a later, separately-authorised gate — **numerical validation only, never proof**:

- **Proposed numerical validation 12.1 (first-order identity 4.1/4.2).** On random
  synchronous D0 fixtures, check `[V(x+Δx) − V(x) − (Δt μᵀu − Δt Σ(J²/M+θJ))] / Δt² `
  is bounded as `Δt → 0` (i.e. the residual is `O(Δt²)` with the predicted constant).
- **Proposed numerical validation 12.2 (one-edge bound 5.1).** Confirm `Δt ≤
  2/(LM(1+η²))` gives per-step `V` non-increase; sweep across `η`, and record (not
  assert) the tightness observed in Counterexample A.
- **Proposed numerical validation 12.3 (graph bound 5.2).** Confirm the spectral bound
  is safe on random graphs, and measure the conservatism gap vs the empirical threshold
  (feeds Conjecture 5.5).
- **Proposed numerical validation 12.4 (stock ledger 8.1).** Check
  `1ᵀ(x^{n+1}−x^n) = Δt(1ᵀu − Σ(1−η)J)` to machine precision.
- **Proposed numerical validation 12.5 (locality 9.1 vs 9.2).** Confirm one-hop
  dependency under synchronous D0 and reproduce the multi-hop leak under a sequential
  variant.

These would live in a *new* file at a future gate; **this gate creates no test.**

---

## 13. Unresolved conjectures and proof gaps

1. **Conjecture 5.5** — a tight, state-dependent graph step-size threshold (active-set
   spectral norm) rather than the conservative all-`J` bound.
2. **Driven global behaviour** — Corollary 6.2 is a one-step condition; multi-step
   boundedness/convergence under persistent drive (a discrete analogue of a coercive
   sublevel-set / LaSalle argument, cf. V2.7 Cor 7.2) is **open**.
3. **Splitting error (D0 → DE step 1).** The engine's `A∘N` splitting with `μ` at
   `N(x^n)`: bound the discrepancy from D0 via Lie/Strang splitting error. **Open.**
4. **Loss-blind engine force.** DE uses `μ_i − μ_j − θ`; characterise the set of states
   on which this is (non-)descending under `η < 1` (Counterexample D is one witness).
   **Open.**
5. **Constrained descent.** A projected-dynamics analogue of Theorem 4.4 that admits
   clipping/spill/reserve while retaining a dissipation inequality. **Open.**
6. **`θ` and the flat viable band.** The bounds drop the `θ_e J_e` term and ignore the
   flat (`v'' = 0`) interior; a curvature-aware, band-aware bound would be less
   conservative. **Open.**

---

## 14. Plain-language interpretation

Think of `V` as a "stress score" for the whole grid and `μ_i` as the local pressure at
cell `i`. Moving resource down a pressure gradient lowers stress — but along a lossy
pipe only a fraction `η` arrives, so the *right* pressure difference to act on is
`μ_i − η μ_j`, **not** `μ_i − μ_j`. If you use the naive difference you can "help" a
starving neighbour while wasting so much in transit that the grid is worse off
(Counterexample D).

In continuous time (V2.7) stress falls at a rate equal to how hard the drive pushes
minus how much the pipes dissipate. In discrete ticks you also pay a **step-size
penalty**: take too big a step and you overshoot and *increase* stress (Counterexample
A) — exactly like too large a learning rate in gradient descent. For one pipe the safe
step is `Δt ≤ 2/(L·M·(1+η²))`; for a network it is governed by a spectral norm of the
pipe layout. Physical *stock* is a separate ledger: transport never destroys resource
mysteriously — whatever doesn't arrive is the named efficiency loss `(1−η)`.

Two honest caveats. First, if the outside world keeps pumping resource in (drive), the
score need not fall every tick; we can only say when dissipation beats drive plus the
step penalty. Second — and most important — this all concerns the **idealised
synchronous law (D0)**. The **real engine (DE)** applies drive and transport in two
ordered passes, moves resource one transfer at a time against a changing state (which
can carry information two cells in a single tick), uses the naive loss-blind force, and
clamps values to a physical range. Proving D0 is a first brick, not the building: the
engine's own guarantees still have to be earned separately.
