# Energy Balance Project — Foundation Note V2.8 (discrete, DRAFT)

**Status: mathematics-first DRAFT for independent review. No engine, test, or metadata
is changed by this gate.** V2.7 proved a *continuous-time* energy–dissipation identity
for a smooth, unconstrained, simultaneous Onsager flow (Model C). This draft derives a
*discrete-time* counterpart for the **simplest compatible synchronous system (Model
D0)** and states precisely why that result does **not** yet cover the actual Python
engine family (the DE family, §3.3).

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

**Assumption 2.5 (L-smoothness of V).** `∇V` is `L_V`-Lipschitz on the relevant region
in the Euclidean norm `‖·‖₂`.

*Exact branchwise slope.* For
`v_i(x) = α_i[L_i − x]₊² + β_i[x − U_i]₊² + χ_i[R_i − x]₊²`,
```
v_i'(x) = −2α_i(L_i − x)₊ + 2β_i(x − U_i)₊ − 2χ_i(R_i − x)₊ ,
```
a continuous piecewise-linear function whose slope (the a.e. second derivative) is
```
v_i''(x) = 2[ α_i·𝟙_{x<L_i} + β_i·𝟙_{x>U_i} + χ_i·𝟙_{x<R_i} ] .
```
Because the homeostatic deficit branch (`x<L_i`) and the reserve branch (`x<R_i`) — or
the excess branch (`x>U_i`) and the reserve branch — can be **active simultaneously**,
the slope is a *sum* of active weights, not their maximum. Hence the exact global
Lipschitz constant is
```
L_V = max_i sup_x  2[ α_i·𝟙_{x<L_i} + β_i·𝟙_{x>U_i} + χ_i·𝟙_{x<R_i} ] ,
```
read through the slopes of the continuous piecewise-linear gradient. Since `L_i ≤ U_i`,
at most one of the deficit/excess branches is active at any `x`, so a convenient
**safe upper bound** is
```
L_V ≤ 2 max_i [ max(α_i, β_i) + χ_i ] .
```
(The former draft's `2 max_i max(α_i,β_i,χ_i)` is **too small** whenever a homeostatic
and the reserve penalty overlap — see Counterexample E, §10.) The symbol `L_V` is used
consistently in every descent, one-edge, graph, and driven bound below. All norms are
`ℓ²` unless stated; `‖·‖₂` on matrices is the spectral norm.

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

**Definition 3.3 (the DE engine family — three distinct update laws).** The Python
operators actually run are **not one identical map**; they share related state
accounting but differ. We name three members and attribute a feature only where it is
confirmed in that function. All three apply the natural update `N` **first** and then a
transport pass, evaluate `μ` at the **post-drive** state `y = N(x^n)` (not `x^n`), use
the **loss-blind** force `F = μ_i − μ_j − θ`, apply transfers **sequentially against
live state**, and fix `Δt = 1`.

| Member | Function | Transport sizing | Conflict scaling | Constraints |
|---|---|---|---|---|
| **DE-core** | `energy_balance.step` | raw `q = M[F]₊` | **proportional** source scaling | feasibility caps + **clip to `[0,K]`** |
| **DE24-safe** | `ebu_v24.step_v24` | `_golden_min` line search (approx.) or horizon-opt, then a strict-decrease accept gate | **none** (sequential, sorted by `F`, per-proposal feasibility) | per-proposal `q_hi`, reserve floor |
| **DE26-adversarial** | `ebu_v26.forced_tick` | externally supplied quantities (search/policy); no force or search computed | none | `feasible_q` caps (`q_max`, source floor, dest headroom) |

(So proportional conflict scaling is a property of **DE-core only**; the safe line
search is **DE24-safe only**; DE26 executes *given* actions. Do not attribute any of
these to all members.)

> **Assumption 3.4 (non-transfer of results).** A theorem about **D0** does **not**
> automatically hold for any member of the DE family. **D0 is the forward-Euler
> discretisation of Model C; the DE members are not.** They are **distinct update laws
> built on related state accounting**: the loss-blind raw law (`DE-core`) and the
> approximate coordinate-search law (`DE24-safe`) are *not faithful discretisations of
> the loss-aware Onsager law C* — they use the wrong (loss-blind) force (Counterexample
> D) and, for `DE24-safe`, a different sizing rule entirely. D0 and the DE family differ
> in at least: operator splitting, the state at which `μ` is frozen (`x^n` vs `N(x^n)`),
> loss-aware vs loss-blind force, simultaneous vs sequential application, presence of
> conflict scaling (`DE-core`) or line search (`DE24-safe`), unconstrained vs clipped,
> and `Δt` free vs `Δt = 1`. §7 and §10 quantify the gaps.

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
`V(y) ≤ V(x) + ∇V(x)ᵀ(y−x) + (L_V/2)‖y−x‖²`.

**Theorem 4.4 (one-step discrete inequality).** Under Assumption 2.5, the D0 update
satisfies, with `Δx = Δt(u + SJ)`,
```
V(x^{n+1}) − V(x^n)
  ≤  Δt · ∇V(x^n)ᵀ u(x^n)
     − Δt Σ_e ( J_e²/M_e + θ_e J_e )
     + R_n ,        R_n := (L_V/2)‖Δx‖² = (L_V Δt²/2) ‖ u + S J ‖² .        (★)
```
Moreover the remainder splits explicitly, exposing the **drive–transport cross term**:
```
R_n = (L_V Δt²/2) ( ‖u‖²  +  2 uᵀ S J  +  ‖S J‖² ) .
```

*Proof.* Apply Lemma 4.3 with `x = x^n`, `y = x^{n+1}`; substitute Lemma 4.1 for the
first-order term and Lemma 4.2 for the edge sum; expand `‖u + SJ‖²`. ∎

**Remark 4.5 (norm and constant).** The bound uses the `ℓ²` norm and the global
smoothness constant `L_V` (Assumption 2.5). `R_n` is a genuine explicit upper bound on
the **Taylor/descent remainder of the functional `V`**, `R_n ≤ (L_V Δt²/2)‖u+SJ‖² =
O(Δt²)`. It is *not* the local truncation error of the state trajectory, and must not be
conflated with it (§7 and §10 keep the three error notions separate).

---

## 5. Graph derivation

### 5.1 Undriven descent, one edge (exact-sufficient)

**Theorem 5.1 (one-edge step-size bound, `u = 0`).** For a single active edge
`e=(i,j)` with `u ≡ 0`, the D0 step satisfies `V(x^{n+1}) ≤ V(x^n)` whenever
```
Δt  ≤  2 / ( L_V · M_e · (1 + η_e²) ) .            (one-edge sufficient)
```
Including `θ_e` only relaxes this (the true admissible range is
`Δt ≤ (2/(L_V(1+η_e²)))·(1/M_e + θ_e/J_e)`).

*Proof.* With `u = 0`, (★) gives `V(x^{n+1}) − V(x^n) ≤ −Δt(J²/M_e + θ_e J) +
(L_V Δt²/2)‖S_e‖² J²`, where `‖S_e‖² = 1 + η_e²`. A sufficient condition for the RHS
`≤ 0` is `Δt(J²/M_e) ≥ (L_V Δt²/2)(1+η_e²)J²` (dropping the non-negative `θ_e J` term),
i.e. `Δt ≤ 2/(L_V M_e(1+η_e²))`. Keeping `θ_e J` yields the relaxed range. ∎

**Consistency check with V2.7 §5.** Setting `Δt = 1` gives `M_e ≤ 2/(L_V(1+η_e²))`;
with `L_V = 2w` (a single homeostatic branch of weight `w`, no reserve overlap),
`M_e ≤ 1/(w(1+η_e²))` — identical to the V2.7 §5.2 symmetric single-transfer bound
`M ≤ 1/(w(1+η²))`. Counterexample A (§10) shows this bound is **tight** (necessary and
sufficient) in the symmetric *pure-quadratic* fixture defined there, so it is not merely
a loose sufficient condition in that case.

### 5.2 Undriven descent, graph (conservative sufficient)

**Theorem 5.2 (spectral step-size bound, `u = 0`).** Let `D_M = diag(M_e)` and
`‖·‖₂` the spectral norm. If
```
Δt  ≤  2 / ( L_V · ‖ S D_M^{1/2} ‖₂² ) ,            (graph sufficient)
```
then the D0 step satisfies `V(x^{n+1}) ≤ V(x^n)` for `u = 0`. The matrix inequality
below is **uniform over all vectors `J`**, so in particular it holds for every
**Onsager-generated** flux vector (Def 2.3); the descent conclusion still relies on that
flux law (via Lemma 4.2), not on an arbitrary `J`.

*Proof.* From (★) with `u=0`, `V(x^{n+1}) − V(x^n) ≤ −Δt Σ_e(J_e²/M_e + θ_e J_e) +
(L_V Δt²/2)‖SJ‖²`, where the dissipation term used the **flux law** (Lemma 4.2, valid
only for `J = M_e[f_e−θ_e]₊`). Dropping the non-negative `θ` term, a sufficient
condition for the RHS `≤ 0` is `Jᵀ D_M^{-1} J ≥ (L_V Δt/2) Jᵀ SᵀS J`, where
`Σ_e J_e²/M_e = Jᵀ D_M^{-1} J` and `‖SJ‖² = Jᵀ SᵀS J`. We secure this **uniformly in
`J`** via the matrix inequality `D_M^{-1} ⪰ (L_V Δt/2) SᵀS`: substituting
`y = D_M^{-1/2}J`, it reads `‖y‖² ≥ (L_V Δt/2) yᵀ(D_M^{1/2}SᵀS D_M^{1/2})y ∀y`, i.e.
`(L_V Δt/2)·λ_max(D_M^{1/2}SᵀS D_M^{1/2}) ≤ 1`. Since
`D_M^{1/2}SᵀS D_M^{1/2} = (S D_M^{1/2})ᵀ(S D_M^{1/2})`, its largest eigenvalue is
`‖S D_M^{1/2}‖₂²`. Rearrange. (Uniformity over `J` is a convenience: it lets one bound
hold for whichever active flux the state produces. It does **not** assert that an
arbitrary flux vector dissipates — only the Onsager-law flux does, through Lemma 4.2.) ∎

**Corollary 5.3 (one-edge special case).** For a single edge, `S D_M^{1/2} = √M_e S_e`,
`‖S D_M^{1/2}‖₂² = M_e(1+η_e²)`, recovering Theorem 5.1 exactly.

**Remark 5.4 (structure of `SᵀS`, and a degree-weighted Gershgorin bound).**
`(SᵀS)_{e,e'} = S_e·S_{e'}`: diagonal `1+η_e²`; `+1` for two edges sharing their
**source**; `η_e η_{e'}` for two sharing their **destination**; `−η` when one edge's
destination is the other's source.

To bound `‖S D_M^{1/2}‖₂² = λ_max(D_M^{1/2}SᵀS D_M^{1/2})` by row sums, first note the
**similarity** (equal spectra): for invertible `P = D_M^{1/2}`,
```
D_M^{1/2} SᵀS D_M^{1/2} = P^{-1}(D_M SᵀS)P  ~  D_M SᵀS ,
```
so `λ_max(D_M^{1/2}SᵀS D_M^{1/2}) = λ_max(D_M SᵀS)`. Apply Gershgorin to the rows of
the (generally **non-symmetric**) matrix `D_M SᵀS`, whose row `e` has diagonal
`M_e(1+η_e²)` and off-diagonals `M_e (S_e·S_{e'})`:
```
‖S D_M^{1/2}‖₂²  =  λ_max(D_M SᵀS)
   ≤  max_e  M_e [ (1 + η_e²) + Σ_{e'≠e} |S_e·S_{e'}| ] ,
```
a fully explicit degree-weighted quantity. (Gershgorin is applied to `D_M SᵀS`, **not**
directly to the symmetric `D_M^{1/2}SᵀS D_M^{1/2}`; the mobility weights `M_e` multiply
each *row*, which is exactly what the similarity produces.)

**Theorem 5.5 (active-set spectral bound, `u = 0`).** Let
`A(x^n) = { e : f_e(x^n) > θ_e }` be the active edge set at `x^n`, and let `S_A`,
`D_{M,A}` be `S`, `D_M` restricted to `A(x^n)`. Because inactive edges carry `J_e = 0`,
`SJ = S_A J_A` and `Σ_e J_e²/M_e = Σ_{e∈A} J_e²/M_e`, so the proof of Theorem 5.2
applies verbatim with `S ↦ S_A`, `D_M ↦ D_{M,A}`. Hence
```
Δt  ≤  2 / ( L_V · ‖ S_A D_{M,A}^{1/2} ‖₂² )        (active-set sufficient)
```
guarantees `V(x^{n+1}) ≤ V(x^n)` for the current step. Since `A(x^n) ⊆ E`,
`‖S_A D_{M,A}^{1/2}‖₂² ≤ ‖S D_M^{1/2}‖₂²`, so Theorem 5.5 is never worse than Theorem
5.2 and is often strictly larger.

**Theorem 5.6 (direct state-specific bound, `u = 0`).** At a fixed state `x^n` with
Onsager flux `J = J(x^n)`:
- if `SJ = 0` (transport is stock-and-potential neutral, e.g. a balanced cycle), the
  remainder vanishes and `V(x^{n+1}) ≤ V(x^n)` for **every** `Δt > 0`;
- if `J = 0` (no active edge), the transport step is trivial and `V` is unchanged by
  transport;
- otherwise (`‖SJ‖ > 0`),
  ```
  Δt  ≤  2 Σ_e ( J_e²/M_e + θ_e J_e )  /  ( L_V ‖SJ‖² )
  ```
  guarantees `V(x^{n+1}) ≤ V(x^n)`.

*Proof.* Direct from `V(x^{n+1}) − V(x^n) ≤ −Δt Σ_e(J_e²/M_e+θ_e J_e) +
(L_V Δt²/2)‖SJ‖²` (Theorem 4.4, `u=0`): the `SJ=0` and `J=0` cases make the remainder
or the whole transport term vanish; otherwise solve the quadratic-in-`Δt` inequality. ∎

**Conjecture 5.7 (tightness).** The active-set bound (Theorem 5.5) and the state-specific
bound (Theorem 5.6) are *sufficient* current-step conditions. Whether either coincides
with the **tight** admissible `Δt` (the exact threshold below which descent holds and
above which it can fail) is **open**; the pure-quadratic one-edge fixture of
Counterexample A is the only case where tightness is established. No empirical threshold
is claimed as a theorem.

---

## 6. The discrete driven inequality (`u ≠ 0`)

**Theorem 6.1 (driven one-step inequality).** Under Assumption 2.5, (★) holds verbatim
for `u ≠ 0`. In particular `V` is governed by the competition of three terms:
```
V(x^{n+1}) − V(x^n)  ≤   Δt·μᵀu   −   Δt Σ_e(J_e²/M_e + θ_e J_e)   +   (L_V Δt²/2)‖u+SJ‖² .
                         └ drive ┘      └──── dissipation ────┘        └── remainder ──┘
```

**Corollary 6.2 (sufficient one-step decrease).** `V(x^{n+1}) ≤ V(x^n)` holds if
```
Σ_e ( J_e²/M_e + θ_e J_e )   ≥   μᵀu   +   (L_V Δt/2) ‖u + SJ‖² .
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

- **Consistency (`Δt → 0`) — from the exact identity, not the inequality.** Because `V`
  is differentiable (`C¹`), the directional derivative is exact:
  `d/dt V(x(t)) = ∇V(x)ᵀ ẋ = ∇V(x)ᵀ(u + SJ)`. Applying the **exact** first-order
  identity (Lemma 4.1) and the edge identity (Lemma 4.2) — not the descent
  *inequality* — gives
  `dV/dt = μᵀu − Σ_e(J_e²/M_e + θ_e J_e)`, which is exactly Theorem 7.1. Equivalently,
  the D0 forward difference `(V(x^{n+1})−V(x^n))/Δt` converges to this as `Δt → 0`
  because `R_n/Δt = (L_V Δt/2)‖u+SJ‖² → 0`. **Theorem 7.1 is recovered from the exact
  identity plus differentiability**, with the inequality only bounding the finite-`Δt`
  gap.
- **Three distinct error quantities (do not conflate).** (1) the **Taylor/descent
  remainder of `V`**, rigorously bounded by `(L_V Δt²/2)‖u+SJ‖² = O(Δt²)` (Theorem 4.4);
  (2) the **local truncation error of the state trajectory**, `x(t_n+Δt) −
  x^{n+1} = ½Δt² ẍ(t_n) + O(Δt³) = O(Δt²)` — this expansion needs the vector field to be
  differentiable along the step and is valid only in **smooth regions away from the
  switching surfaces** `{x_i = L_i, U_i, R_i}` where `∇V` is only Lipschitz, not `C¹`;
  (3) the **accumulated global trajectory error** `‖x^N − x(T)‖ = O(Δt)` over a fixed
  finite interval `[0,T]`, which requires additionally a **locally Lipschitz vector
  field** and a **bounded solution** on `[0,T]`. Item (1) is a statement about the
  functional `V`; items (2)–(3) are about the trajectory; they are different objects.
- **Finite-`Δt` trajectories are not identical to C.** The Euler iterate departs from
  the continuous flow by the accumulated `O(Δt)` error above; equality holds only in the
  limit.
- **The safe search is an *approximate* minimiser, not the Onsager flux.** In the engine
  family, `DE24-safe` sizes a transfer by `_golden_min`, a **finite 24-iteration
  golden-section** search — an *approximate bounded one-dimensional minimiser* of
  `q ↦ v_i(x_i − q) + v_j(x_j + η q)` on `[0, q_hi]`, gated on strict decrease. This is
  an (approximate) **coordinate-descent-style** step on `V`, **not** the explicit flux
  `q = M_e[f_e − θ_e]₊`, and it is **not** proximal (no proximal objective or proof is
  claimed). So D0 (explicit Onsager flux) and `DE24-safe` are different update laws
  (cf. V2.7 §2.1, §7).
- **Proving D0 does not prove the DE family.** Beyond the flux-vs-search point, the DE
  family members differ from D0 by operator splitting, `μ` frozen at `N(x^n)`, the
  loss-blind force `μ_i − μ_j − θ`, sequential live state, (for `DE-core`) proportional
  conflict scaling, and clipping (§3.3, §10 B and D). Each is out of scope (§11).

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

**Definition 9.0 (undirected dependency graph).** Let `G_u = (V, E_u)` be the
**undirected** graph on the cells in which `i` and `j` are adjacent iff there is a
directed transfer edge `(i,j)` or `(j,i)`. Let `dist(·,·)` denote graph distance in
`G_u`.

**Assumption 9.0′ (on-site drive).** Each `u_i(x)` depends only on `x_i` (Def 2.4:
`u_i = s_i + g_i(x_i) − d_i − λ_i − κ_i x_i`, all on-site). A drive coupling several
cells would break the result below.

**Theorem 9.1 (one-tick dependency radius, D0).** Under the synchronous frozen-state
update (D0) with Assumption 9.0′, `x^{n+1}_i` depends only on
`{ x^n_k : dist(i,k) ≤ 1 }` in `G_u`. By induction, `x^{n+m}_i` depends only on
`{ x^n_k : dist(i,k) ≤ m }`: information propagates at most one edge per tick.

*Proof.* `x^{n+1}_i = x^n_i + Δt( u_i(x^n) + (SJ)_i )`. `u_i` is on-site by Assumption
9.0′ (0 hops). `(SJ)_i = Σ_{e=(i,·)} (−J_e) + Σ_{e=(·,i)} (η_e J_e)`, and each incident
`J_e = M_e[μ_a − η_e μ_b − θ_e]₊` depends only on the two endpoints of `e`, i.e. on
`x^n_i` and its `G_u`-neighbours (1 hop). Hence one tick has dependency radius `1`;
compose and induct. ∎

**Counterexample / Observation 9.2 (sequential live state breaks this).** Every member
of the DE family applies accepted transfers **sequentially against live state**. Then a transfer on
`(i,j)` mutates `x_j` *before* a later transfer on `(j,k)` reads it, so `x^{n+1}_k` can
depend on `x^n_i` — a **2-hop** influence in a single nominal tick, even though each
individual transfer is local. (V2.7 §6 exhibits this concretely: on a `0→1→2` chain, a
`+0.5` perturbation at cell 0 moved cell 2 by `+0.124` in one tick under the sequential
engine, versus exactly `0` under a frozen-state simultaneous application.) Theorem 9.1
therefore holds for **D0 only**; the DE family's causal speed per tick is bounded not by 1 but by
the length of the longest chain of accepted transfers sharing cells in application
order.

---

## 10. Counterexamples

**Counterexample A (step above the bound increases `V`).** To keep the calculation
valid **across the whole step** (with no flat viable band that an overshoot could land
in), use a **pure-quadratic** fixture: set `L_i = U_i = L_j = U_j = 0` and `χ = 0`, with
equal weight `α_i = β_i = α_j = β_j = w`, so `v_i(x) = v_j(x) = w x²` for all `x` (a
genuine global quadratic, `v'' ≡ 2w`, hence `L_V = 2w`). One edge `e=(i,j)`, `η_e = 1`,
`θ_e = 0`. Let `x_i = d`, `x_j = −d`. Then `μ_i = 2wd`, `μ_j = −2wd`,
`f_e = μ_i − μ_j = 4wd`, `J = M f_e = 4Mwd`. The D0 step gives `x_i ↦ d − ΔtJ`,
`x_j ↦ −d + ΔtJ`, so
`V_after = w(d−ΔtJ)² + w(−d+ΔtJ)² = 2w d²(1 − 4MwΔt)²`, versus `V_before = 2wd²`
(both expressions exact, since `v = w x²` everywhere). Hence
```
V_after > V_before  ⟺  |1 − 4MwΔt| > 1  ⟺  Δt > 1/(2Mw).
```
The one-edge bound (Theorem 5.1) here is `Δt ≤ 2/(L_V M (1+η²)) = 2/(2w·M·2) = 1/(2Mw)`.
So on **this symmetric pure-quadratic fixture** the bound is **exactly tight** — any
`Δt` above it strictly increases `V` (e.g. `w=M=1, d=1`: `Δt=0.6 ⇒ V: 2 → 3.92`).
Tightness is claimed for this fixture only; with a positive-width viable band the flat
zero-penalty interior makes the bound merely sufficient, not tight (cf. Conjecture 5.7).

**Counterexample B (sequential 3-cell over-propagation).** See Observation 9.2: the
`0→1→2` chain under sequential live-state application transmits a cell-0 perturbation to
cell 2 within one tick, exceeding the one-edge-per-tick propagation that Theorem 9.1
proves for the synchronous law. This invalidates any attempt to extend Theorem 9.1 to
the DE family unchanged.

**Counterexample C (drive increases `V`).** Take the simplest valid witness: a single
supplied cell `c` with `v_c(x) = β[x − U]₊²`, **no active transport edges anywhere**,
initial state `x^n_c = U` (`μ_c = 0`), constant supply `u_c = s > 0`. The D0 step gives
`x^{n+1}_c = U + Δt s`, so
```
V(x^{n+1}) − V(x^n) = β (Δt s)² > 0 .
```
Thus driven `V` is not monotone in general (supports Non-result 6.3); only the
conditional Corollary 6.2 survives. *(If, instead, a distant dissipative edge were also
present, one can only say that **sufficiently small** remote dissipation need not offset
the local increase — a distant edge could in principle offset it in the global
functional, so we do not claim it "cannot".)*

**Counterexample D (loss-blind force is wrong for `η < 1`).** Take `η_e = 0.5`,
`θ_e < 1`, and endpoint potentials `μ_i = −3`, `μ_j = −4` (both cells in deficit, `j`
more deficient). The **loss-blind** rule uses `g_e = μ_i − μ_j = 1 > θ_e` and would
transfer `i→j`. But the **true** loss-aware force is `f_e = μ_i − η_e μ_j = −3 −
0.5·(−4) = −1 < 0`. By Lemma 4.1 the first-order change from this edge is
`−f_e·(ΔtJ) = +ΔtJ > 0`: the loss-blind transfer **increases** `V` to first order,
because at `η = 0.5` the efficiency loss wastes more than the deficit relief it buys.
The correct variational force is `f_e = μ_i − η_e μ_j` (Def 2.3), **not** `μ_i − μ_j`.
This is exactly why the DE family (whose members all use the loss-blind `μ_i − μ_j − θ`)
is not guaranteed descending under loss, and why D0 must use the loss-aware force.

**Counterexample E (the former Lipschitz constant is too small).** This is a
counterexample **to the former constant `2 max_i max(α_i,β_i,χ_i)`**, not to the
corrected theorem. Take a **zero lower and reserve threshold** (`L = R = 0`), weights
`α = χ = 1`, `β` inactive, so for `x < 0`
`v(x) = α[−x]₊² + χ[−x]₊² = 2x²` and `v''(x) = 2(α+χ) = 4`. One edge, `η = M = 1`,
`θ = 0`, `Δt = 0.4`, with two negative states `x_i = −1`, `x_j = −2`. Then `μ =
(v'(−1), v'(−2)) = (−4, −8)`, `f_e = μ_i − η μ_j = −4 − (−8) = 4`, `J = M[f]₊ = 4`. The
step maps
```
(x_i, x_j) = (−1, −2)  ↦  (−1 − 0.4·4,  −2 + 0.4·4) = (−2.6, −0.4),
```
and `V: 2(−1)² + 2(−2)² = 10  ↦  2(−2.6)² + 2(−0.4)² = 13.52 + 0.32 = 13.84` — `V`
**increases**. The **former** constant would read `L = 2 max(α,β,χ) = 2`, whose one-edge
bound `Δt ≤ 2/(2·1·2) = 0.5` **incorrectly permits** `Δt = 0.4`. The **corrected**
constant is `L_V = 2(α+χ) = 4` (both the homeostatic-deficit and reserve branches are
active at `x < 0`), whose bound `Δt ≤ 2/(4·1·2) = 0.25` correctly forbids `Δt = 0.4`.
This is exactly why `L_V` must sum simultaneously-active weights (Assumption 2.5).

*Effect on the theorems.* A, C, D confirm the **necessity** of (respectively) the
step-size condition, the driven caveat, and the loss-aware force — they do not
invalidate the corrected D0 results. E is a counterexample to the *former* Lipschitz
constant and motivates the corrected `L_V`. B invalidates only the *extension* of the
locality theorem to the sequential DE family, which we accordingly restrict to D0.

---

## 11. Exact scope and exclusions

**The D0 theorems (4.4, 5.1, 5.2, 5.5, 5.6, 6.1, 8.1, 9.1) hold only for the
synchronous, unconstrained, loss-aware, explicit-Euler law of Def 3.2.** Each mechanism
below is **excluded** and, we indicate, the framework its rigorous treatment will likely
need:

| Excluded mechanism | Likely framework |
|---|---|
| clipping / projection at `0` and `K` | projected dynamical systems / variational inequalities |
| spill at `K` | one-sided projection / complementarity |
| unmet-demand saturation (`min(d, ·)`) | nonsmooth / Filippov / piecewise-smooth analysis |
| hard-reserve constraints | constrained optimisation (KKT) / barrier methods |
| fixed activation cost `c₀` | hybrid / impulsive systems (discontinuous jumps) |
| safe golden-section / coordinate line search (`DE24-safe`) | coordinate-descent theory (approximate 1-D minimisation); *not* proximal unless a proximal objective and proof are supplied |
| sequential live-state transfers | Gauss–Seidel operator splitting (vs Jacobi) |
| horizon optimisation | optimal control / dynamic programming |
| global / instantaneous field solves | elliptic PDE / implicit (nonlocal) solves |
| ledger incentives, EBU issuance | mechanism design — no dynamical-descent claim applies |

Also excluded from D0 but present in the DE family and unaddressed here: **operator
splitting** (drive `N` then transport `A`) and **`μ` frozen at `N(x^n)`** rather than
`x^n`. These alone make D0 ≠ (any DE member) even before constraints; a Lie/Strang
splitting-error analysis is the natural next tool.

---

## 12. Proposed numerical validation plan (NOT proof)

For a later, separately-authorised gate — **numerical validation only, never proof**:

- **Proposed numerical validation 12.1 (first-order identity 4.1/4.2).** On random
  synchronous D0 fixtures, check `[V(x+Δx) − V(x) − (Δt μᵀu − Δt Σ(J²/M+θJ))] / Δt² `
  is bounded as `Δt → 0` (i.e. the residual is `O(Δt²)` with the predicted constant).
- **Proposed numerical validation 12.2 (one-edge bound 5.1).** Confirm `Δt ≤
  2/(L_V M(1+η²))` gives per-step `V` non-increase; sweep across `η`, and record (not
  assert) the tightness observed in Counterexample A.
- **Proposed numerical validation 12.3 (graph bounds 5.2 / 5.5 / 5.6).** Confirm the
  spectral, active-set, and state-specific bounds are safe on random graphs, and measure
  the conservatism gap vs the empirical threshold (feeds Conjecture 5.7).
- **Proposed numerical validation 12.4 (stock ledger 8.1).** Check
  `1ᵀ(x^{n+1}−x^n) = Δt(1ᵀu − Σ(1−η)J)` to machine precision.
- **Proposed numerical validation 12.5 (locality 9.1 vs 9.2).** Confirm one-hop
  dependency under synchronous D0 and reproduce the multi-hop leak under a sequential
  variant.

These would live in a *new* file at a future gate; **this gate creates no test.**

---

## 13. Unresolved conjectures and proof gaps

1. **Conjecture 5.7 (tightness)** — the active-set (Theorem 5.5) and state-specific
   (Theorem 5.6) sufficient bounds are *proved*; whether either is the **tight**
   admissible `Δt` is open (only the pure-quadratic one-edge case of Counterexample A is
   settled).
2. **Driven global behaviour** — Corollary 6.2 is a one-step condition; multi-step
   boundedness/convergence under persistent drive (a discrete analogue of a coercive
   sublevel-set / LaSalle argument, cf. V2.7 Cor 7.2) is **open**.
3. **Splitting error (D0 → DE family, step 1).** The engine's `A∘N` splitting with `μ`
   at `N(x^n)`: bound the discrepancy from D0 via Lie/Strang splitting error. **Open.**
4. **Loss-blind engine force.** The DE family uses `μ_i − μ_j − θ`; characterise the set of states
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
step is `Δt ≤ 2/(L_V·M·(1+η²))`; for a network it is governed by a spectral norm of the
pipe layout. Physical *stock* is a separate ledger: transport never destroys resource
mysteriously — whatever doesn't arrive is the named efficiency loss `(1−η)`.

Two honest caveats. First, if the outside world keeps pumping resource in (drive), the
score need not fall every tick; we can only say when dissipation beats drive plus the
step penalty. Second — and most important — this all concerns the **idealised
synchronous law (D0)**. The **real engine family (DE)** applies drive and transport in two
ordered passes, moves resource one transfer at a time against a changing state (which
can carry information two cells in a single tick), uses the naive loss-blind force, and
clamps values to a physical range. Proving D0 is a first brick, not the building: the
engine's own guarantees still have to be earned separately.
