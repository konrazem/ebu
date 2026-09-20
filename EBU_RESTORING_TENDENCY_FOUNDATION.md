# Restoring tendency: the foundational homeostasis definition

**Status: definition, exact identities, and a review of what can and cannot be
proved.** It registers no experiment and no result. Results appear in
`RESTORING_DRIFT_EXPLORATORY_REPORT.md`.

---

## 1. The controlling definition

> **Homeostasis is a persistent restoring tendency toward the declared
> reference under disturbance.**

This replaces every previous success concept as the *foundational* definition.
It does **not** require `V = 0` at any tick, does **not** require staying
inside a fixed quantile region, and permits large temporary excursions. What
matters is what the dynamics do during and after displacement.

The previously used concepts remain valid *measurements* and are not deleted:
exact convergence to `V = 0`, first recovery time, `O95`/`O99` occupancy, and
mean `V` against a control. None of them is the definition.

## 2. The potential is a ruler, not a boundary

```
V_i(x_i) = (1/2) ((x_i - x*_i)/sigma_i)^2
```

Its role is to **measure standardized equilibrium deviation**. Nothing more.

A Gaussian quantile is not a viability or failure boundary. A real critical
boundary must come from the physical model — stock exhaustion, survivability,
an irreversible ecological threshold, a hardware limit — and **no such boundary
is declared for this synthetic world**, so none is used. The only genuine
physical constraints here are `x_i >= 0` and `sum_i x_i = M`.

## 3. Canonical tick decomposition

Every tick is:

```
x_t --[external forcing / demand]--> z_t --[actor action]--> x_{t+1}
```

with

```
dV_ext(t)   = V(z_t)     - V(x_t)
dV_actor(t) = V(x_{t+1}) - V(z_t)
dV_total(t) = V(x_{t+1}) - V(x_t) = dV_ext(t) + dV_actor(t)
```

and, because `E_t = V(z_t) - V(x_{t+1})` by definition of finite EBU,

```
dV_actor(t) = -E_t          exactly, not to first order.
```

**All four identities are recoverable exactly from the registered artifacts.**
`dV_ext` is the per-tick increment of the deviation ledger `J`; `dV_total` is
the per-tick increment of `R^2/2`; `dV_actor` is their difference. Verified
tick for tick against an independent re-execution, with zero mismatches, on a
control-random job where `E` plays no part in selection. On this lattice `R^2`
is always an even integer, so every quantity above is an **integer**.

Conformance: `test_restoring_tendency.py`, exact on every feasible state/group
pair it enumerates.

## 4. Actor restoring tendency

For the complete pre-action state `S_t = (z_t, B_t)`:

```
D_A(S_t) = E[ V(x_{t+1}) - V(z_t) | S_t ] = E[ -E_t | S_t ]
```

`D_A < 0` means the actor layer is restoring on average; `D_A > 0` means it
pushes outward; `0` means no directional tendency. For the deterministic
aligned and hostile policies this expectation is an exact value:
`-max E_G` and `-min E_G` over the admissible set.

## 5. Complete-system restoring tendency

For the complete start-of-tick state `Y_t = (x_t, B_t)`:

```
D_T(Y_t) = E[ V(x_{t+1}) - V(x_t) | Y_t ]
```

This is the central stochastic-homeostasis object. It is computed exactly by
averaging over the six equiprobable raw disturbance outcomes, with
`NULL_FORCING` applied as registered — an inadmissible draw leaves the state
unchanged and is not resampled.

## 6. The state is `(x, B)`, not `V`

**Markov sufficiency.** `x` fixes the feasible menu and every exact EBU value;
`B` fixes which of those the affordability gate admits. The deviation ledger
`J` is a pure audit and never feeds back into any decision, and the RNG is
counter-addressed and state-independent. Therefore `(x, B)` is Markov-
sufficient and `V` alone is not a state.

This is not a formality. Conditioning on `V` alone **visibly misleads** in this
model: the hostile arm's `V`-projected actor drift looks *restoring* at
moderate `V`, because reaching a moderate `V` also means having earned the
capacity that funds destruction. The projection mixes two capacity regimes with
opposite behaviour.

Aggregated curves

```
g_A(v) = E[D_A(S) | V(S) in bin around v]
g_T(v) = E[D_T(Y) | V(Y) in bin around v]
```

are therefore **explanatory projections only**. The rigorous object is the
full-state enumeration in `exact_state_drift.py`, which does not use
trajectories at all.

## 7. Interpreting restoring drift

`g_T(v) < 0` at sufficiently large deviation is evidence of a restoring
tendency. The expected qualitative pattern — small disturbances producing
outward drift, response dominating beyond some scale, then fluctuation around a
recurrent operating regime — is a pattern to look for, **not a requirement**.
`g_T(v) < 0` for every `v > 0` is not required and under persistent forcing is
not expected.

## 8. The empirical operating level

If the aggregated drift curve crosses zero at `v*`, that value is recorded as
an **empirical operating / restoring balance level**. It is not a universal
equilibrium, and no crossing is forced where none exists.

A caution this model supplies: the exact control-random curve is **not
monotone** and does not have a single clean crossing. It sits near `+2.43`
across low `V`, dips negative around `V = 73–91`, returns positive through
`V = 93–192`, and only becomes reliably negative above `V ≈ 217`. The
non-monotonicity is lattice geometry — shells at different `V` contain
different mixes of edge and corner states with different menus. **A single `v*`
should not be quoted for a curve that crosses more than once.**

## 9. Failure language

Homeostasis failure is **not** `V > V_95`. The registered failure concepts are
dynamical:

- **LOSS OF RESTORING TENDENCY** — `g_T(v) >= 0` throughout the large-deviation
  states represented;
- **OUTWARD DRIFT** — the late-window distribution of `V` moves progressively
  upward;
- **HIGH-DEVIATION CAPTURE** — increasing occupation of maximum-deviation
  states;
- **EXCURSION NON-RETURN** — return probability or time from high-deviation
  shells deteriorates strongly;
- **PHYSICAL-BOUNDARY FAILURE** — only where a genuine physical threshold is
  declared, which it is not here.

The state space is compact and finite, so the word *divergence* is not used for
any quantity of the physical state. It remains correct only for the capacity
ledger, which is genuinely unbounded.

## 10. Foster–Lyapunov: what applies, what does not

Mission section 17 requires this distinction to be explicit.

**The classical criterion.** For a Markov chain on a countable state space with
`W >= 0`, if `E[W(X_{t+1}) - W(X_t) | X_t = x] <= -eps < 0` for all `x` outside
a finite set `C`, and the drift is bounded on `C`, then the chain is positive
recurrent.

**Why it does not apply to `V` on this model — three independent reasons.**

1. **`V` is not a function of the state.** `V` depends on `x` only, while the
   chain lives on `(x, B)`. A Lyapunov function that ignores an unbounded
   coordinate cannot certify recurrence of the full chain.
2. **The full chain is not positive recurrent.** Under Capacity V1 the audit
   ledger grows linearly — `E[D_ext | x]` is an exact positive constant
   independent of `x` (Theorem 4, `CURRENT_CAPACITY_FAILURE_THEOREMS.md`) — and
   `V` is bounded by `V_max = 300`, so `sum_i B_i = J - V` grows without bound.
   A chain with a coordinate escaping to infinity is not positive recurrent, so
   **no Foster–Lyapunov theorem can hold for it**, whatever `W` is chosen.
3. **The drift condition fails anyway.** `g_T(v) >= 0` on a large low-`V`
   region for every arm except aligned, and that region is not a finite
   exceptional set in any useful sense — it is most of the state space.

**What is therefore claimed.** `D_A` and `D_T` are **exact one-step drift
diagnostics**, not Lyapunov drift conditions. They are computed, not estimated.
They license statements about the direction of one-step motion from a given
state, and they do **not** license any claim of positive recurrence, stationary
existence, ergodicity or stability. Calling them a Foster–Lyapunov argument
would be a category error.

**What can be proved, and is.** The following are theorems about this model,
established by exhaustive finite verification rather than by analogy:

> **Theorem R1 (gate inactivity).** For the registered world, if every cell
> holds `B_i >= 29`, then at every one of the 496 admissible lattice states the
> affordable set equals the feasible set. Verified by enumeration over all
> states and all groups, under both menu rules.

> **Theorem R2 (process identity).** In the regime of Theorem R1, the
> EBU-random and control-random policies induce **identical** transition
> kernels on the physical state. Their exact drift maps are equal at every
> state. Verified by direct comparison, under both menu rules.

> **Corollary R3.** Any restoring advantage of EBU-random over control-random
> under Capacity V1 is a property of the *low-capacity* regime alone, and
> vanishes identically once the gate becomes inactive.

Theorem R1's premise concerns `min_i B_i`. That `sum_i B_i` grows without bound
is a theorem; that `min_i B_i` exceeds 29 is **empirical** — the Stage-B
exploratory re-reading measured its median rising 77.5 → 171 → 300.25 across
blocks, an order of magnitude past the threshold. The distinction is kept.

## 11. The status of H95, H99, O95 and O99

**Retained, and explicitly downgraded.** They are no longer the definition of
EBU homeostasis. Their new status is:

> **GAUSSIAN REFERENCE OCCUPANCY DIAGNOSTICS** — descriptive summaries of where
> a trajectory's `V` distribution sits relative to declared reference regions.

They remain useful and are still computed. What changes is what they may be
used for: they describe a distribution, they do not define regulation, and a
low occupancy is not by itself evidence of regulatory failure.

**No historical registered metric is deleted and no preregistered result is
reinterpreted.** `HOMEOSTASIS_REGISTERED_REPORT.md` stands exactly as written;
its `O95` findings remain valid statements about occupancy. The change is
prospective: future studies take restoring drift as primary and occupancy as
descriptive.

## 12. The emergency / extreme-demand principle

> **EBU must not be interpreted as requiring the system to remain near
> equilibrium during every event.**

Some physically mandatory events will intentionally produce `E < 0` and large
deviation — emergency resource concentration, disaster response, life-saving
demand. Under mandatory action an actor facing only damaging candidates still
acts, and the aligned actor takes the least damaging one; that is correct
behaviour, not a failure.

The homeostatic question is what happens afterwards:

> **During and after the disturbance, does the feasible action process retain a
> restoring tendency, and does the state subsequently return toward the
> reference?**

**No emergency override mechanism is added by this document.** This is an
interpretation principle only. No mechanism, potential or policy is modified.
