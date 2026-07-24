# Energy Balance Project — Foundation Note V2.7 (mathematics)

**Status:** mathematical specification only. **No change is made to the physical
engine.** Claims are labelled by epistemic status (*Theorem* / *Proof sketch* /
*Numerical observation* / *Regression test (proposed)* / *Conjecture*). A companion
`test_math.py` is proposed in §8 as numerical *validation* of the derived bounds;
passing tests are validation, **never proof**.

The note ends (§7) with the verdict separated as required: **A** the derived local
law; the engine split into **B_raw** (Onsager/explicit-Euler) and **B_safe** (gated
coordinate descent); **C** the compatibility conditions under which **B_raw is the
forward-Euler discretisation of A** (not an identity of trajectories — see §7), and
why `B_safe` is a different law. §7.1 promotes the dissipative Lyapunov statement C-1
to a continuous-time theorem.

---

## 0. Notation

Lattice `Λ` of cells `i`, von Neumann 4-neighbourhood `𝒩(i)`, directed edge set
`E = {(i→j) : j ∈ 𝒩(i)}`, graph distance `dist(i,k)`. State `x = (x_i)`,
`x_i ∈ [0, K_i]`. Per-cell parameters from [energy_balance.py](energy_balance.py):

| symbol | meaning |
|---|---|
| `K_i` | capacity (upper bound) |
| `L_i ≤ U_i` | viable band |
| `α_i, β_i ≥ 0` | deficit / excess penalty weights |
| `s_i ≥ 0`, `d_i ≥ 0` | inflow, demand |
| `λ_i ≥ 0`, `κ_i ≥ 0` | constant leak, proportional leak (`leak_frac`) |
| `ρ_i ≥ 0`, `A_i ≥ 0` | regeneration rate, Allee threshold |

Per-edge: mobility `M_e > 0`, transport threshold `θ_e ≥ 0`, transport efficiency
`η_e ∈ (0,1]`. Clip `Π_i(v) = min(max(v,0), K_i)`. Regeneration (`regen_at`):

```
g_i(x) = 0                              if ρ_i ≤ 0 or K_i ≤ 0
       = ρ_i x (1 − x/K_i)              logistic          (A_i = 0)
       = ρ_i x (1 − x/K_i) (x/A_i − 1)  Allee, signed      (A_i > 0)
```

Homeostatic penalty and its marginal (`local_penalty`, `mu`):

```
ℓ_i(x)  = α_i [L_i − x]₊² + β_i [x − U_i]₊²
ℓ_i'(x) = −2α_i (L_i − x)   (x < L_i);   2β_i (x − U_i)  (x > U_i);   0  (else)
```

`B_homeostasis(x) = Σ_i ℓ_i(x_i)`.

---

## 1. The dynamics — two clearly separated models

### 1.1 Model D — the discrete map the engine actually runs

Object of record; `energy_balance.py` implements exactly this. One tick is
`T = A ∘ N`.

**Natural map `N`** (one cell; order = inflow, regen, demand, leak, clip):

```
(N x)_i = Π_i( x_i + s_i + g_i(x_i) − d_i − λ_i − κ_i x_i )                    (D.1)
```

*Variant note.* `energy_balance.py` sums then clips once (D.1); the ledger-safe
`nat_cell` in [ebu_v23.py](ebu_v23.py) applies regen/leak/demand as sequential
non-negative clamps. They agree while the cell stays in `(0, K_i)`; they differ only
at the `0`/`K_i` boundaries. §3–§4 use D.1 interior dynamics, common to both.

**Actor map `A`** on `y = N x`. With marginals `μ_i = ℓ_i'(y_i)`, each actor at cell
`i` selects the steepest feasible out-edge (`_proposals`, `ebu_v22.py:140`):

```
j*(i) = argmax_{j∈𝒩(i)} F_ij ,   F_ij = μ_i − μ_j − θ    (engine force)        (D.2)
```

acts iff `F_{i j*} > 0`. Quantity is either the **raw flux** `q = M·F` (`gradient`
mode) or the **line-searched** minimiser (`safe` mode, `_line_search_q`,
`ebu_v22.py:111`)

```
q_safe = argmin_{0 ≤ q ≤ q_hi}  [ ℓ_i(y_i − c0 − q) + ℓ_j(y_j + η q) ]           (D.2s)
```

accepted only if it strictly lowers that pair penalty. Committed update:

```
y_i  ← y_i − (q + c0),   y_{j*} ← y_{j*} + η q      (loss (1−η)q + c0 ≥ 0)       (D.3)
```

**Sequential application (load-bearing for §6).** Accepted transfers are applied one
at a time, strongest `F` first, each reading and mutating the **live** `y`
(`ebu_v22.py:204`). The *direction* `j*(i)` is frozen (from `μ` on `y = N x`); the
*quantity/feasibility* is live.

### 1.2 Model C — continuous-time approximation (labelled as such)

Reading D.1/D.3 as forward Euler with `Δt = 1`, the `Δt → 0` limit is

```
ẋ_i = s_i + g_i(x_i) − d_i − λ_i − κ_i x_i + Σ_{j∈𝒩(i)} ( η_ji J_ji − J_ij )     (C.1)
```

with `J_e` from §2. **Model C is an approximation, not the engine.** Discrete
phenomena proved below (§3 flip bifurcation, §5 overshoot) are `Δt=1` artifacts that
vanish as `Δt → 0`; results meant to reflect engine behaviour use **Model D**.

---

## 2. State functional, dissipation potential, and the derived local law

Keep the **state** functional separate from transport **dissipation** — they are
different objects; only the state functional takes cell-state arguments. Transport is
*not* placed inside a state functional (no edge-state variable exists).

```
V_state(x)     = B_homeostasis + B_regeneration                                 (2.1)
B_homeostasis  = Σ_i  ℓ_i(x_i)
B_regeneration = Σ_{i : ρ_i>0, A_i>0}  χ_i [R_i − x_i]₊²,   R_i = A_i + δ_i       (2.2)

Ψ(J) = Σ_{e∈E} [ J_e² / (2 M_e) + θ_e J_e ],   J_e ≥ 0     (dissipation potential) (2.3)
```

**Local chemical potential** (state marginal), on-site by construction:

```
μ_i^tot = ∂V_state/∂x_i = ℓ_i'(x_i) + r_i'(x_i),
r_i'(x) = −2χ_i (R_i − x)   (x < R_i),   0 otherwise.                            (2.4)
```

**Derived flux (gradient flow with loss and dissipation).** For a directed edge
`e = (i→j)`, a flux `J_e` removes `J_e` from `i` and deposits `η_e J_e` at `j`
(lossy continuity). Hence

```
dV_state/dt = Σ_i μ_i^tot ẋ_i = − Σ_e J_e ( μ_i^tot − η_e μ_j^tot ) = − Σ_e J_e f_e,
f_e := μ_i^tot − η_e μ_j^tot.                                                    (2.5)
```

`f_e` is the **η-weighted thermodynamic force** — exactly the corrected directional
derivative `dV/dq = −μ_i + η μ_j` (with `q = J_e`). The Onsager / gradient-flow rule
sets the flux by balancing dissipation against the work done on `V_state`,
`min_{J_e ≥ 0} [ Ψ_e(J_e) − f_e J_e ]`, giving

```
J_e = M_e [ f_e − θ_e ]₊ = M_e [ μ_i^tot − η_e μ_j^tot − θ_e ]₊.                 (2.6)
```

> **This is the derived local law.** Its edge force is
> `F_e^derived = μ_i^tot − η_e μ_j^tot − θ_e`. It reads only `x_i`, adjacent `x_j`,
> and edge/cell-local constants — local (§6). The engine force (D.2)
> `F = μ_i − μ_j − θ` matches `F_e^derived` **only when `η_e = 1` and `χ = 0`**
> (see §7); for `η_e < 1` the two differ by `(1 − η_e) μ_j`.

### 2.1 Three distinct laws (do not conflate)

Let `S_e` be the transfer direction of edge `e = (i→j)`: the vector with `−1` in
slot `i` and `+η_e` in slot `j`. The three laws are:

```
(1) Continuous Onsager law:      J_e  = M_e [ f_e − θ_e ]₊                       (2.7)
(2) Raw discrete explicit-Euler: q_e  = Δt · M_e [ f_e − θ_e ]₊                  (2.8)
(3) Current safe rule:           q_e* = argmin_{0 ≤ q ≤ q_hi} V_state(x + S_e q),
                                        executed iff the edge passes its force
                                        gate F_ij > 0 and the acceptance test
                                        V_state(x + S_e q*) < V_state(x).         (2.9)
```

(1) is the gradient-flow flux of §2; (2) is its forward-Euler discretisation with
`Δt = 1` in the engine (the mobility bound of §5 is the step-size condition for (2)).

> **(3) is gated coordinate descent, not the Onsager flux.** `q_e*` minimises the
> *state functional* along the edge direction; it is **not** `M_e F_e`, even for
> `η_e = 1`. Its quantity optimiser (D.2s, `_line_search_q`) uses **only** the two
> penalty terms — it **excludes** the linear cost `θ_e q` and the quadratic
> dissipation `q²/(2M_e)` of the Onsager objective `Ψ_e(q) − f_e q`. `θ_e` enters
> law (3) **only** through edge eligibility (the `F_ij > 0` gate in `_proposals`),
> never through the chosen size; `M_e` does not enter (3) at all. So (3) solves a
> different variational problem from (1)/(2) and generally lands at a different `q`.

Consequently the verdict (§7) splits the engine into **B_raw** (law 2) and **B_safe**
(law 3): only B_raw is a *discretisation* of the derived law A (the forward-Euler
scheme, under the restricted conditions listed there); B_safe is a different law, not
a discretisation of A, even at `η = 1`.

*Remark (dissipation is not a state cost).* The loss `(1−η)q` and `θ_e J_e` live in
`Ψ`, not in `V_state`. The correct global statement is the dissipative inequality
`ΔV_state ≤ (drive) − (dissipation)`, not `ΔV_state ≤ 0` (Conjecture C-1, §7).

*Remark (this is V2.4's rule, un-derived).* `B_regeneration` (2.2) and its marginal
(2.4) are exactly the `pen`/`marg` augmentation in [ebu_v24.py](ebu_v24.py), there a
*rule choice*, not a consequence of a stated functional.

---

## 3. Logistic harvest — existence is not sustainability

Isolated logistic source, constant net harvest `h` (`s=λ=κ=0`, interior of D.1):
`x_{t+1} = φ(x_t)`, `φ(x) = x + ρx(1 − x/K) − h`.

> **Theorem 3.1 (equilibria exist iff `h ≤ h*`).** With `h* = ρK/4`,
> `D = 1 − 4h/(ρK)`: fixed points `x_±(h) = (K/2)(1 ± √D)`, real iff `h ≤ h*`; they
> merge at `x = K/2` when `h = h*` (fold).

> **Theorem 3.2 (stability / collapse threshold).** `φ'(x) = 1 + ρ(1 − 2x/K)`, so
> `φ'(x_±) = 1 ∓ ρ√D`. `x_−` is **always unstable** (`φ'(x_−) = 1 + ρ√D > 1`) — the
> collapse threshold; `x_+` is stable **iff** `0 < ρ√D < 2` (flip/period-doubling
> when `ρ√D > 2`).

> **Corollary 3.3 (sustainability — corrected).** A logistic source persists **iff
> all three** hold: (i) `h ≤ ρK/4`; (ii) `x(0) > x_−(h)` (basin); (iii) `ρ√D < 2`.
> Condition (i) alone gives only *existence* of an equilibrium — the error in the
> first draft, which called `h ≤ ρK/4` sufficient for sustainability.

*Proof sketch.* Scalar-map fixed points + multipliers; flip at `φ'(x_+) = −1`; below
`x_−`, `φ(x) < x` so iterates fall to the absorbing `0`. ∎

*Numerical observation (`ρ=0.4, K=20, h*=2`).*

| `h` | `x_−` | `x_+` | `x_−−0.05` | `x_−+0.05` | `|φ'(x_+)|` | `|φ'(x_−)|` |
|---|---|---|---|---|---|---|
| 1.00 | 2.929 | 17.071 | → 0 | → 17.071 | 0.717 | 1.283 |
| 1.60 | 5.528 | 14.472 | → 0 | → 14.472 | 0.821 | 1.179 |
| 1.99 | 9.293 | 10.707 | → 0 | → 10.707 | 0.972 | 1.028 |

Flip (`h = 0.3h*`): `ρ ≤ 2.2` → fixed point; `ρ = 2.6` (`ρ√D = 2.18`) → 2-cycle
`20.0 ↔ 16.1`.

---

## 4. Allee reserve under driving — the reserve is not `x = A`

> **Theorem 4.1 (isolated undriven case only).** For `ẋ = ρx(1−x/K)(x/A−1)`
> (interior of D.1 with `s=d=λ=κ=h=0`), equilibria are `{0, A, K}`; `0` and `K` are
> stable, `x = A` is **unstable** and separates the collapse basin `(0,A)` from the
> recovery basin `(A,K)`. This is the **only** case where the basin boundary equals
> `A`.

> **Theorem 4.2 (reserve shift under drive).** With harvest `h`, demand `d`, leak
> `λ+κx`, supply `s`, the persistence boundary is the unstable middle root `x_r` of
>
> ```
> G(x) = ρ x (1 − x/K)(x/A − 1) + s − d − λ − κx − h = 0.               (4.1)
> ```
>
> There `G'(x_r) > 0`, so by the implicit function theorem
>
> ```
> ∂x_r/∂h = ∂x_r/∂d = ∂x_r/∂λ = 1/G'(x_r) > 0,
> ∂x_r/∂κ = x_r/G'(x_r) > 0,     ∂x_r/∂s = −1/G'(x_r) < 0.               (4.2)
> ```
>
> Harvest/demand/leak **raise** the reserve; supply **lowers** it. Transport *out* of
> a source acts as harvest (raises `x_r`); transport *in* acts as supply (lowers it).

*Proof sketch.* At the middle root `G` crosses `−→+`, so `G'(x_r) > 0`; differentiate
`G(x_r; p)=0` and use `∂G/∂{h,d,λ} = −1`, `∂G/∂κ = −x_r`, `∂G/∂s = +1`. ∎

*Numerical observation (`ρ=0.6, K=20, A=5`).* Undriven middle root `= 5.0 = A`.
`h=0.5 → 5.99`; `d=0.5 → 5.99`; `κ=0.05 → 5.58` (all `> A`); `s=0.5 → 3.58` (`< A`).

*Consequence.* The protected quantity is the local, drive-dependent `x_r`, not `A`.
V2.4's constant `R_i = A_i + δ_i` is a surrogate (Conjecture C-2, §7).

---

## 5. Descent condition — corrected for loss, curvature, and rule type

The first draft reported `M_crit ≈ 1.79` as structural and used the loss-free
curvature `2(α+β)`. Both are corrected here.

Fix an edge `(i→j)`, post-natural `y`, cost-free (`θ, c0` only shrink the step).
Along the **lossy** transfer `q ↦ (y_i − q, y_j + η q)`,

```
ψ(q) = ℓ_i(y_i − q) + ℓ_j(y_j + η q)   [+ reserve terms if χ>0].
```

`ψ` is convex. `ψ''(q) = ℓ_i''(y_i − q) + η² ℓ_j''(y_j + η q)`, with each `ℓ''`
in `{2α, 2β, 0}` depending on branch.

> **Theorem 5.1 (operating-branch curvature — corrected).** With the **source in
> excess** (`y_i > U_i`) and the **destination in deficit** (`y_j < L_j`), the
> directional curvature is
> ```
> ψ''  =  2( β_source + η² α_destination ).                              (5.1)
> ```
> The loss enters as `η²` on the destination term (chain rule twice); the earlier
> `2(α+β)` was the `η=1` special case with mismatched indices.

> **Theorem 5.2 (sufficient descent bound for the raw rule).** `ψ'` is Lipschitz
> along the transfer line with constant
> `L = 2[ max(α_i,β_i) + η² max(α_j,β_j) ]` (the max over the penalty branches the
> step may enter — overshoot can drive the source below `L_i` (weight `α_i`) and the
> destination above `U_j` (weight `β_j`)). Hence the **raw** flux `q = M[F]₊` does not
> increase `ψ` if
> ```
> M ≤ 1 / [ max(α_i,β_i) + η² max(α_j,β_j) ].                            (5.2)
> ```
> For symmetric weights `α_i=β_i=w_i` this is tight: `M ≤ 1/(w_i + η² w_j)`; with a
> single global `w`, `M ≤ 1/(w(1+η²))`.

*Proof sketch.* Descent lemma for `L`-smooth convex `f`: `f(x − t∇f) ≤ f(x)` for
`0 < t ≤ 2/L`. Apply with `f = ψ`, `t = M`, `L` the global Lipschitz constant of
`ψ'`. `θ ≥ 0` and feasibility caps only reduce `q`. ∎

> **Numerical observation (validates 5.1–5.2; the bound must be ≤ empirical).**
>
> | `α` | `β` | `η` | bound (5.2) | empirical `M_crit` |
> |---|---|---|---|---|
> | 1 | 1 | 0.9 | 0.5525 | 0.5525 (tight) |
> | 0.5 | 0.5 | 0.8 | 1.2195 | 1.2195 (tight) |
> | 1 | 0.5 | 1.0 | 0.5000 | 0.6667 |
> | 1 | 0.5 | 0.9 | 0.5525 | 0.7372 |
> | 2 | 0.5 | 0.8 | 0.3049 | 0.4926 |
>
> Symmetric weights hit the bound exactly; asymmetric weights make it conservative
> (the far-branch curvature dominates). The wide-band `1.79` of the first draft was
> band slack (a step may overshoot the near edge yet land in the flat viable
> interior); it is retained only as a fixture number, **not** a bound.

**Raw rule vs. safe line search (required distinction).** Theorem 5.2 governs the raw
`q = M[F]₊` rule only. The `safe` rule (D.2s) instead sets
`q_safe = argmin_{[0,q_hi]} ψ(q)` gated on `ψ(q) < ψ(0)`. Its size is controlled by
`q_hi` (feasibility) and the accept gate, **not by `M`** — so it has no mobility
stability bound and cannot overshoot. Theorem 5.2 is exactly the condition under
which the raw rule may skip that line search safely. (The `safe` line search does use
the correct `η`-geometry in its objective, D.2s; its *direction*, from D.2, does not
— see §7.)

---

## 6. Finite causal speed — corrected for sequential execution

> **Theorem 6.1 (1-hop speed under frozen-state simultaneous update).** *If* all edge
> fluxes for a tick are computed from the single frozen state `y = N x` and applied
> **simultaneously**, then `x_i(t+n)` depends only on `{x_k(t) : dist(i,k) ≤ n}`:
> causal speed ≤ 1 cell/tick.

*Proof sketch.* `N` (D.1) is on-site (0 hops); a simultaneous `A` reads `μ` at `i`
and `𝒩(i)` and moves mass across single edges (1 hop). One tick has dependency
radius 1; induct on `n`. ∎ *Validated:* with frozen-state simultaneous application, a
`+0.5` perturbation at cell 0 leaves cell 2 bit-identical after one tick (leak `0`).

> **Numerical observation 6.2 (the current engine violates 1-hop speed).** The safe
> engine freezes proposal *directions* but applies accepted transfers **sequentially**
> against live intermediate state (§1.1). A chain `0→1→2` applied in that order lets
> the `1→2` line-searched quantity read the `x_1` that `0→1` just raised. Measured: a
> `+0.5` perturbation at cell 0 alone moved cell 2 by **+0.124 in one tick** — a
> 2-hop influence.

**Resolution (no engine change now).** Three options were on the table; we adopt the
first for the *current* engine and record the third as the target discipline:

- **(a) Weakened theorem (matches the engine).** Under sequential application, one
  nominal tick is a sequence of up to `E_acc` micro-steps (`E_acc` = accepted
  transfers). Causal speed is ≤ 1 edge **per micro-step**; per **tick** it is bounded
  by the longest chain of accepted transfers sharing cells in application order — not
  by 1. This is the honest statement for V2.0/V2.2/V2.4 as implemented.
- **(c) Strict 1-hop (target).** Recover Theorem 6.1 exactly by computing all fluxes
  from the frozen `y` and applying them simultaneously (validated above). Proposed for
  a future engine; **not applied here**.

**Global-solve caveat (retained).** `V_state`/`B_homeostasis` are global sums but are
*evaluation-only*; no actor reads them, so locality is unaffected. The horizon rules
(V2.3/V2.4) roll a `radius`-bounded local counterfactual — local. **If** any future
`V_total` variant computes a signal/danger field by a global or instantaneous solve,
Theorem 6.1 fails and that step must be labelled a non-local approximation. Nothing in
the present engine does this.

---

## 7. Verdict — derived law (A), engine laws (B_raw / B_safe), discretisation (C)

**A — the mathematically derived law (§2, law (1)/(2.7)).**
```
J_e = M_e [ μ_i^tot − η_e μ_j^tot − θ_e ]₊,   μ_i^tot = ∂(B_hom + B_reg)/∂x_i .
```
Onsager gradient-flow flux of `V_state` under lossy continuity and dissipation `Ψ`.

**B_raw — engine raw rule (law (2)/(2.8), `gradient` mode).** Direction from the
**loss-blind** force `F = μ_i^hom − μ_j^hom − θ` (D.2); size `q = M[F]₊`; `χ = 0` by
default; fixed activation cost `c0` possible; applied **sequentially**.

**B_safe — engine safe rule (law (3)/(2.9), `safe` mode).** Same loss-blind direction
and gate; size `q* = argmin V_state(x + S_e q)` (D.2s), which **excludes** `θ_e q` and
`q²/(2M_e)`; executed only on its acceptance test; applied **sequentially**.

**C — compatibility conditions under which `B_raw` is the forward-Euler
discretisation of `A`.** (`B_safe` is excluded from C; see below.) This is a statement
about the *scheme*, not the *trajectories*: even when all conditions hold, the
finite-`Δt` discrete trajectory is **not** identical to the continuous flow of A — a
forward-Euler step incurs local truncation error `O(Δt²)` (global `O(Δt)`), and the
engine runs at `Δt = 1`. All of the following must hold:

1. **`η_e = 1`** — else A's force `μ_i − η μ_j − θ` differs from B_raw's
   `μ_i − μ_j − θ` by `(1 − η)μ_j`.
2. **`χ = 0` on active edges** — else A carries `−2χ_i(R_i−x_i)₊`, which B_raw's
   default omits (the V2.3 collapse mechanism: `μ^hom = 0` in `[L_i,U_i]` even when
   `x_i < A_i`).
3. **`c0 = 0`** — a fixed activation cost is a discrete jump in the transfer, not part
   of the smooth Onsager flux; `c0 > 0` requires a hybrid / nonsmooth formulation and
   breaks exact correspondence.
4. **No overlapping sequential transfers** (single active edge, or frozen-state
   simultaneous application, §6) — else B_raw's live-state coupling is not the
   simultaneous step A specifies.
5. **Mobility bound `M ≤ 1/[max(α,β)_i + η² max(α,β)_j]`** (5.2) — the step-size
   condition for the explicit-Euler law (2).

Under 1–5, one `B_raw` update **is** one forward-Euler step (`Δt = 1`) applied to A's
vector field at the current state — the two share the flux at each point. They do
**not** share trajectories: the discrete iterate departs from the continuous solution
of A with per-step error `O(Δt²)`, accumulating to `O(Δt)` over a fixed horizon.

> **`A ≠ B_safe` in general — even at `η = 1`, `χ = 0`, `c0 = 0`, single transfer.**
> `B_safe` sets `q*` by minimising the *state functional* along the edge (2.9); A/B_raw
> set `q = M_e F_e`, a linear Onsager/Euler step. These agree only in the degenerate
> case where the unconstrained pair minimiser happens to equal `M_e F_e` — not an
> identity. `B_safe` is **gated coordinate descent on `V_state`**, a genuinely
> different dynamics from the Onsager flux; do not claim it equals A.

**Plain statement.** `B_raw` **is the forward-Euler discretisation of** the derived
gradient flow A — only in the lossless, danger-free, cost-free, single-transfer,
mobility-bounded regime, and only as a *scheme* (finite-`Δt` trajectories differ,
`O(Δt²)` local error). Outside that regime it is not even that scheme: it differs by
the `(1−η)μ_j` loss term, the `−2χ_i(R_i−x_i)₊` reserve term, the `c0` jump, and the
sequential coupling. `B_safe` is never the Onsager flux; it is a different
(coordinate-descent) law that happens to share A's search direction and its
per-transfer non-increase of `V_state`. **No implementation change is made here**;
these are the specifications a corrected engine would close.

### 7.1 C-1 promoted: continuous-time energy–dissipation theorem

> **Theorem 7.1 (energy–dissipation identity for law A).** *Assume:* continuous time
> (Model C, C.1); `c0 = 0`; fixed graph; local lossy continuity with efficiency
> `η_e ∈ (0,1]`; Onsager flux `J_e = M_e[f_e − θ_e]₊` with `f_e = μ_i − η_e μ_j`.
> Each penalty is `C¹`, so `V_state ∈ C¹` and `μ = ∇V_state` is continuous; the RHS of
> (C.1) is **locally Lipschitz** (the regeneration terms `g_i` are polynomial, hence
> not globally Lipschitz on `ℝⁿ`), so a unique `C¹` solution exists locally in time.
> Global forward existence is not asserted here in general; for the undriven case it is
> established in Corollary 7.2 via a compact positively-invariant sublevel set. Writing
> the local drive `u_i(x) = s_i + g_i(x_i) − d_i − λ_i − κ_i x_i`, then along any solution
> (on its interval of existence)
>
> ```
> dV_state/dt = Σ_i μ_i u_i − Σ_e [ J_e²/M_e + θ_e J_e ],                (7.1)
> dV_state/dt ≤ Σ_i μ_i u_i.                                             (7.2)
> ```

> **Excluded engine mechanisms (scope of Theorem 7.1).** The theorem governs the
> *smooth, unconstrained, continuous-time* flow only. It does **not** cover the
> following engine mechanisms, each of which needs its own nonsmooth / projected /
> hybrid / discrete treatment and can violate (7.1)–(7.2):
> - **clipping / projection** at the bounds `0` and `K_i` (a projected dynamical
>   system, not the free flow);
> - **spill** at `K_i` (mass discarded at the upper bound);
> - **unmet-demand saturation** (demand truncated to available stock, `nat_cell`);
> - **hard-reserve constraints** (`hard_reserve`: an inequality constraint / barrier);
> - **fixed activation cost `c0`** (a discrete jump per transfer — hybrid dynamics);
> - **sequential live-state transfers** (§6; breaks the simultaneous-flux assumption);
> - **finite-step discrete updates** (`Δt = 1`; forward Euler adds an `O(Δt²)`
>   remainder absent from the identity).
> Establishing analogues under any of these is open (Conjecture C-1′ addresses the
> finite-step case).

*Proof.* Continuity (C.1): `ẋ_i = u_i + Σ_{e=(k→i)} η_e J_e − Σ_{e=(i→k)} J_e`. Since
`V_state ∈ C¹`, the chain rule gives `dV_state/dt = Σ_i μ_i ẋ_i = Σ_i μ_i u_i + T`,
with `T` the transport part. Reorganise `T` by edge: edge `e = (i→j)` contributes
`μ_i(−J_e) + μ_j(η_e J_e) = −J_e(μ_i − η_e μ_j) = −J_e f_e`, so `T = −Σ_e f_e J_e`.
On an active edge `J_e = M_e(f_e − θ_e) > 0`, hence `f_e = J_e/M_e + θ_e` and
`f_e J_e = J_e²/M_e + θ_e J_e`; on an inactive edge both sides vanish. Summing gives
(7.1). As `J_e ≥ 0`, `θ_e ≥ 0`, the dissipation term is `≥ 0`, giving (7.2). ∎

> **Corollary 7.2 (undriven case — LaSalle via a coercive sublevel set).** Assume
> `u_i ≡ 0` (closed system: no supply, demand, regeneration, leak) and that `V_state`
> is **coercive** on the unconstrained state space, i.e.
> `‖x‖ → ∞ ⟹ V_state(x) → ∞`.
>
> *Coercivity is an explicit assumption, not a property of the model.* The penalty
> weights `α_i, β_i` (and `χ_i`) may be zero for some cells, in which case `V_state` is
> flat in some direction and not coercive. A **sufficient** condition for the present
> piecewise-quadratic `V_state` is that every cell has strictly positive lower- and
> upper-deviation weights, `α_i > 0` and `β_i > 0` for all `i` (each coordinate is then
> penalised quadratically in both directions, forcing `V_state → ∞` with `‖x‖`). This
> is offered only as an example; we do not silently impose it on the engine and instead
> assume coercivity directly.
>
> Under these assumptions:
> - By Theorem 7.1, `dV_state/dt = −Σ_e[J_e²/M_e + θ_e J_e] ≤ 0`.
> - Hence `V_state(x(t)) ≤ V_state(x(0))` for all `t ≥ 0`, so the trajectory stays in
>   the sublevel set `Ω₀ = { x : V_state(x) ≤ V_state(x(0)) }`.
> - `V_state` is continuous and coercive, so `Ω₀` is **compact**; and because `V_state`
>   is non-increasing along the flow, `Ω₀` is **positively invariant**.
> - The vector field is **locally Lipschitz** and the solution remains in the compact
>   `Ω₀`, so it cannot escape in finite time: the forward solution extends **globally**
>   in `t`.
> - LaSalle's invariance principle then gives convergence toward the **largest invariant
>   subset** of the zero-dissipation set
>   `Z = { x : J_e(x) = 0 ∀e } = { x : f_e(x) ≤ θ_e ∀e }`. With `u ≡ 0` every point of
>   `Z` is an equilibrium, so `Z` is invariant.
>
> **Retained limitations.** This does **not** prove `V_state = 0`, **not** complete
> homeostasis, **not** a unique equilibrium, and **not** that the physical interval
> `[0,K]` is positively invariant — Theorem 7.1 excludes clipping/projection at `0` and
> `K`, so invariance of `[0,K]` is not established by the unconstrained flow. The reached
> point of `Z` may depend on the initial condition. (Boundedness here comes from the
> coercive sublevel set `Ω₀`, **not** from the physical bounds.)

*Numerical validation (Theorem 7.1).* Fine-`dt` integration (`dt = 10⁻⁴`) of a driven
3-cell path matched (7.1) to `O(dt)` (max `|numeric − analytic dV/dt| = 6.2×10⁻⁵`).
`dV_state/dt` turned **positive** once the drive `Σ μ_i u_i` exceeded the dissipation —
consistent with (7.2) being an inequality that bites only when the drive is
non-positive.

**Scope (as required).** Theorem 7.1 is a **continuous-time** statement about law A.
It does **not** transfer verbatim to the discrete engine:

- **B_raw (discrete):** needs the §5 step-size condition; forward Euler can overshoot
  and *increase* `V_state` within a step when (5.2) is violated. A discrete analogue
  of (7.1) with a step-size penalty term is the remaining open item (below).
- **B_safe (discrete):** obtains per-accepted-transfer non-increase `ΔV_state ≤ 0`
  directly from its acceptance test (2.9) — a *different* mechanism (exact line-search
  gate acting on the post-natural state), **not** the Onsager identity (7.1), and with
  no drive term (the natural/drive update `N` has already been applied).

Remaining open items:

- **Conjecture C-1′ (discrete driven bound).** A discrete counterpart of (7.1) holds
  for B_raw under (5.2): `V_state(x_{t+1}) − V_state(x_t) ≤ Σ_i μ_i u_i − D_t` with a
  dissipation term `D_t ≥ 0` (continuous C-1 is now Theorem 7.1; the discrete case
  remains conjectural pending the step-size remainder and the sequential-execution
  caveat of §6).
- **Conjecture C-2 (reserve surrogate).** V2.4's constant `R_i = A_i + δ_i` dominates
  the driven reserve `x_r` of Theorem 4.2 (hence is safe) iff `δ_i ≥ x_r − A_i` over
  the operating envelope of local drive and edge flow.

---

## 8. Regression tests (`test_math.py`) — validation, not proof

`test_math.py` contains **8 groups holding 34 numerical regression checks** in total.
The check count is an implementation detail of the harness, **not** a count of
theorems: several checks probe one theorem at different points, and a passing run
validates the tested points only — it does not prove any statement in this note. The
groups:

1. **Fold & basin (3.1–3.3):** engine equilibrium matches `x_+(h)`; `x(0)=x_−(h)±ε`
   lands in the collapse / recovery basin.
2. **Flip (3.2):** a sustained 2-cycle appears once `ρ√D > 2`.
3. **Driven reserve (4.2):** the numerically located middle root moves in the signed
   directions of (4.2) for `h,d,λ,κ,s`.
4. **Loss-corrected descent (5.1–5.2):** the derived law with
   `M ≤ 1/[max(α,β)_i + η² max(α,β)_j]` is per-tick non-increasing; symmetric weights
   hit the bound; record (not assert) the wider band slack.
5. **Force coincidence (§7 C1):** `F_engine = F_derived` iff `η = 1`.
6. **Causality (§6):** a single-cell perturbation leaves cells at distance `> n`
   bit-identical after `n` ticks **under frozen-state simultaneous application**, and
   the current **sequential** engine exhibits the multi-hop leak (both recorded).
7. **Energy–dissipation identity (Theorem 7.1):** fine-`dt` integration of law A on a
   driven graph matches (7.1) to `O(dt)`; assert the residual scales with `dt`.
8. **Three-law separation (§2.1, §7):** on a shared fixture, record that
   `q_safe ≠ M_e F_e` even at `η = 1, θ = 0, c0 = 0` — i.e. B_safe is not the Onsager
   flux (a distinctness check, not an equality).

None of these is a proof; each guards against drift between engine and analysis.

---

## 9. Corrections applied

| Prior claim | Corrected statement |
|---|---|
| `h ≤ ρK/4` ⇒ sustainable | existence only; also need basin `x(0) > x_−(h)` and `ρ√D < 2` (3.1–3.3) |
| `x = A` is the basin boundary | only for the isolated undriven Allee source; under drive it is `x_r` of `G(x)=0` (4.1–4.2) |
| `M_crit ≈ 1.79` as a theorem | numerical, fixture-specific; theorem is the bound (5.2), tight for symmetric weights |
| directional curvature `2(α+β)` | `2(β_source + η² α_destination)` in the operating branch (5.1); bound uses max over branches |
| force is the exact gradient | derived force is `μ_i − η μ_j − θ`; engine `μ_i − μ_j − θ` coincides only at `η=1` (§2, §7) |
| `B_transport` inside a state functional | transport is dissipation `Ψ(J)` (2.3), separate from `V_state = B_hom + B_reg`; flux derived via (2.5)–(2.6) |
| 1-hop causal speed per tick | holds only under frozen-state simultaneous update; the sequential engine leaks multi-hop (§6) |
| `V = B_homeostasis` | `B_hom` is blind to Allee danger; state functional is `V_state = B_hom + B_reg` (§2, §7) |
| one engine law `B` compared to A | split into **B_raw** (Onsager/Euler, law 2) and **B_safe** (gated coordinate descent, law 3); only B_raw can equal A (§2.1, §7) |
| `A = B` under four conditions | under five conditions incl. **`c0 = 0`**, `B_raw` is the **forward-Euler discretisation** of A (a scheme; finite-`Δt` trajectories differ, `O(Δt²)` local error) — not a trajectory identity; `B_safe` is a different law even at `η=1` (§7 C) |
| C-1 a conjecture | promoted to **Theorem 7.1** in continuous time (energy–dissipation identity + inequality); discrete case restated as Conjecture C-1′ (§7.1) |
