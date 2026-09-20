# Formal analysis of the Capacity-V1 failure modes

Derives the mechanism behind the two registered empirical findings. Every claim
is labelled **Theorem** (proved here), **Lemma**, **Corollary**, or
**Conjecture / Empirical** (observed but not proved).

Scope: the registered world — Level-1 Local Gaussian
`V_i = (1/2)((x_i - x*_i)/sigma_i)^2`, finite transfer actions
`delta_a = q(e_d - e_s)`, `owner(a) = src(a)`, common-path receipts, exact
rational arithmetic, random choice among physically feasible affordable groups.

**Capacity V1** is the registered mechanism: `B_i' = B_i + Delta B_i` subject to
`B_i >= 0`, with `Delta B_i = sum_{a : owner(a)=i} R_a`.

Registered evidence: `STAGE_A_REGISTERED_REPORT.md`,
`STAGE_B_REGISTERED_REPORT.md`. Those artifacts are immutable and nothing here
reinterprets them.

## 1. The exchange identity and what it really says

**Theorem 1 (exchange invariance).** Under V1, for any executed group `G` from
baseline `z` to `z' = z + delta_G`,

    V(z') + sum_i B_i' = V(z) + sum_i B_i.

*Proof.* `sum_i Delta B_i = sum_a R_a = E_G` by common-path closure, and
`E_G = V(z) - V(z')` by definition of the finite value. Hence
`sum_i B_i' = sum_i B_i + V(z) - V(z')`. □

**Corollary 1.1 (damage potential is conserved).** With forcing off, `J = D` is
constant and `V(t) + sum_i B_i(t) = D` for all `t`. Define the *stored damage
potential* `P(t) := sum_i B_i(t)`. Then `P(t) = D - V(t)` exactly.

**This is the core diagnosis.** Repairing deviation does not reduce the
system's capacity for future damage; it converts realized damage into stored,
spendable damage potential at a one-to-one rate. V1 contains **no sink**: the
sum `V + P` is invariant by construction, so no quantity decreases and no
Lyapunov function exists.

Stage A's `REPEATED_CYCLING` in 128/128 is this identity made visible.

## 2. Why the shock world cycles

**Lemma 2.1 (restorative singletons are free).** A singleton whose value is
`E > 0` has `Delta B_owner = E > 0`, so `B + Delta B >= 0` for any `B >= 0`. A
strictly restorative single action is therefore always affordable.

**Lemma 2.2 (a restorative singleton exists whenever `V > 0`).** On the integer
lattice with `q = 1`, `sigma = 1`, moving one unit from cell `i` to cell `j`
gives exactly

    E = (x_i - x_j) - 1.

(Verified exactly against the implementation.) If `V > 0` then, since
`sum_i x_i = sum_i x*_i`, some cell has `x_i >= x*_i + 1` and some cell has
`x_j <= x*_j - 1`, whence `x_i - x_j >= 2` and `E >= 1 > 0`. Feasibility holds
because `x_i >= 1`. □

**Theorem 2 (equilibrium is not absorbing).** Let `sigma_i = 1`, quantum `q`,
`n` cells, and suppose the state is `x = x*` with `sum_i B_i = D`. A damaging
singleton on edge `(s,d)` has `E = -q^2` and `Delta B_s = -q^2`, and is
feasible since `x*_s >= q`. Because `max_i B_i >= D/n`, the condition

    D >= n q^2

implies some owner `s` has `B_s >= q^2` and its damaging singleton is
affordable. Hence `x*` is **not** absorbing. □

Stage A: `D = 4`, `n = 3`, `q = 1`, so `D >= n q^2` reads `4 >= 3`. **Every
registered Stage-A replicate was structurally guaranteed to leave equilibrium.**
This is why `REACHED_AND_STAYED` occurred zero times in 128 replicates — it was
not a statistical outcome but a theorem.

**Theorem 3 (perpetual recurrence).** With forcing off, `x` lies on a finite
lattice inside the simplex and each `B_i` lies in `[0, D]` on a lattice of
bounded denominator, so the reachable state space is finite and the process is a
finite Markov chain. By Lemmas 2.1–2.2 a value-increasing path to `x*` exists
and is affordable from every reachable state, so `x*` communicates with every
reachable state; by Theorem 2 it is not absorbing. Hence `x*` lies in the unique
recurrent class, and almost surely the process returns to and departs from `x*`
infinitely often. □

**Corollary 3.1 (no damping).** `V(t) -> 0` almost surely is impossible under
V1 when `D >= n q^2`. Absence of damping follows from **accounting symmetry**
(Theorem 1) *together with* the affordability threshold (Theorem 2). It is not
attributable to the random policy alone: no policy that is blind to EBU can
create a sink that the accounting does not contain.

## 3. Why continuous forcing drives capacity without bound

**Theorem 4 (exact forcing drift).** For the registered Stage-B law — amplitude
fixed at `q`, edge drawn uniformly over ordered pairs of distinct cells —

    D_ext = mu(x)^T u + (1/2) u^T H u,
    E[D_ext | x] = q^2 * (1/n) * sum_i 1/sigma_i^2,

**exactly, and independently of `x`.**

*Proof.* Write `u = q(e_d - e_s)`. The first term is `q(mu_d - mu_s)`; under a
uniform draw over ordered pairs `s` and `d` are exchangeable, so its expectation
vanishes for every `x`. The second term is `(1/2)q^2(1/sigma_d^2 + 1/sigma_s^2)`,
whose expectation is `q^2 (1/n) sum_i 1/sigma_i^2` because each index is
marginally uniform. □

Verified exactly: for `sigma = (1,1,1)` the predicted value is `1`, and for
`sigma = (1/2, 1, 2)` it is `7/4`; the empirical mean over the six edges matched
with residual exactly `0` at 300 random states in both cases.

**The drift is a property of curvature, not of the actor.** The gradient term
averages away; the Hessian term is nonnegative and cannot.

**Corollary 4.1.** If forcing is applied at every tick, `E[J_t] = t q^2 (1/n)
sum_i 1/sigma_i^2`, growing linearly without bound.

**Conjecture / Empirical 4.2 (the NULL_FORCING correction).** Under the
registered admissibility rule the draw is conditioned on `x_s >= q`, which
breaks exchangeability and lowers the drift. Observed blockwise growth of
`sum_i B_i` was 0.56–0.67 per tick in the EBU arm against the unconditional
prediction of 1. Not derived here.

**Theorem 5 (capacity divergence).** Physical conservation confines `x` to a
compact simplex, so `V <= V_max` with `V_max = 300` exactly for the registered
world (`V` is convex, so its maximum is at a vertex `M e_k`). With
`V + sum_i B_i = J` this gives

    sum_i B_i(t) = J_t - V(t) >= J_t - V_max.

Hence `J_t -> infinity` implies `sum_i B_i(t) -> infinity`. □

Observed: median terminal `sum_i B_i = 5400` against a deviation ceiling of 300.

## 4. Why, and how fast, the gate goes slack

**Theorem 6 (a sufficient condition for the gate to be inactive).** Receipts are
bounded on the compact simplex:
`|R_a| = |mu^T delta_a + (1/2) delta_a^T H delta_G| <= R_max`, and an owner
holds at most `m_max` actions in a group, so `|Delta B_i| <= m_max R_max`. If

    min_i B_i(t) >= m_max * R_max

then no feasible group is rejected and `rho_reject(t) = 0`. □

For the registered world `|mu_i| <= 20`, giving `R_max <= 42` and
`m_max R_max <= 84`.

**This makes the gate a property of the poorest cell, not of the total.**
`sum_i B_i -> infinity` does *not* imply `min_i B_i -> infinity`, because
capacity may concentrate.

**Empirical 6.1 (exploratory, post-registered).** Re-reading the registered
Stage-B EBU artifacts — no confirmatory claim attached — the poorest cell tracks
the rejection rate closely:

| Block | median `min_i B_i` | fraction of ticks with `min_i B_i < R_max` | `rho_reject` |
|---|---|---|---|
| 1 | 77.50 | 0.3999 | 0.0662 |
| 2 | 171.00 | 0.2837 | 0.0497 |
| 3 | 300.25 | 0.2109 | 0.0332 |

`min_t min_i B_i = 0` was observed, so cells are still drained to empty at
times. Terminal concentration was 0.6616.

**Interpretation, offered as conjecture not theorem.** The gate did not vanish
within the Stage-B horizon because concentration keeps re-creating momentarily
poor cells; but the fraction of such ticks fell monotonically, and with it the
rejection rate and the arm difference. The registered report's "self-attenuation"
is therefore mediated specifically by the **poorest** cell's balance crossing the
receipt scale.

## 5. Summary of the formal position

| Claim | Status |
|---|---|
| `V + sum B = J` is exactly preserved by every executed group | **Theorem 1** |
| Repair converts realized damage into stored damage potential 1:1; V1 has no sink | **Corollary 1.1** |
| Equilibrium is not absorbing when `D >= n q^2` | **Theorem 2** |
| Cycling recurs infinitely often almost surely | **Theorem 3** |
| Damping is impossible under V1 in the registered world | **Corollary 3.1** |
| `E[D_ext | x] = q^2 (1/n) sum_i 1/sigma_i^2`, exactly and independently of `x` | **Theorem 4** |
| `J -> infinity` implies `sum_i B_i -> infinity` | **Theorem 5** |
| `min_i B_i >= m_max R_max` implies the gate is inactive | **Theorem 6** |
| NULL_FORCING lowers the drift below `q^2 (1/n) sum 1/sigma_i^2` | Empirical |
| `min_i B_i -> infinity`, hence the gate vanishes asymptotically | **Conjecture** |
| Stage-B self-attenuation is mediated by the poorest cell | **Conjecture**, strongly indicated |

## 6. What must change, stated minimally

Both failure modes trace to one structural property: **V1's capacity is an
unbounded integral of history with no sink.** Theorem 1 makes it exactly
conservative, so repair funds re-damage exactly; Theorems 4–5 make it absorb an
unbounded external drift.

A replacement must therefore introduce a sink — some explicitly accounted way
for capacity to stop being spendable — without introducing an arbitrary
constant, without abandoning locality, and without letting EBU choose actions.
That target is formalized in `EBU_CAPACITY_REQUIREMENTS_V2.md`.
