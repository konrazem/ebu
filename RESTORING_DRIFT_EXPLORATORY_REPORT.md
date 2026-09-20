# Restoring drift: exploratory re-reading and exact analysis

**Two analyses, two different epistemic statuses.**

1. **EXPLORATORY POST-REGISTERED RESTORING-DRIFT ANALYSIS** of the immutable
   registered homeostasis artifacts — 1,536 jobs, 12,582,912 arm-ticks. The
   drift decomposition did not exist when that study was frozen. Nothing here
   is confirmatory, no hypothesis is tested, no p-value is computed, and
   `HOMEOSTASIS_REGISTERED_REPORT.md` is not modified or reinterpreted.
2. **EXACT FINITE-STATE ANALYSIS**, which is not an experiment at all. It
   enumerates all 496 admissible lattice states and computes the drift objects
   in exact rational arithmetic. Its results are theorems about the model, not
   measurements of a trajectory.

Where the two disagree, the enumeration is authoritative and the trajectory
analysis is the projection (`EBU_RESTORING_TENDENCY_FOUNDATION.md` §6).

---

## 1. The exact result, stated first

Enumerated over every lattice state, both menu rules, in exact arithmetic:

**Fraction of states from which the process drifts inward** (`D_T < 0`):

| regime | control | EBU-random | aligned | hostile |
|---|---|---|---|---|
| `B = 0` (gate maximally active) | 0.345 | **0.998** | 0.998 | **0.702** |
| `B_i >= 29` (gate inactive) | 0.345 | **0.345** | 0.998 | **0.006** |

**Mean total drift over high-deviation states (`V >= 50`), as capacity
accumulates:**

| `B` per cell | control | EBU-random | aligned | hostile | states where gate binds |
|---|---|---|---|---|---|
| 0 | −3.384 | **−18.425** | −32.761 | −3.693 | 493 |
| 3 | −3.384 | −16.861 | −32.761 | −2.065 | 483 |
| 8 | −3.384 | −14.666 | −32.761 | **+2.207** | 462 |
| 16 | −3.384 | −10.818 | −32.761 | +10.320 | 351 |
| 24 | −3.384 | −5.332 | −32.761 | +23.434 | 117 |
| **29** | −3.384 | **−3.384** | −32.761 | **+28.628** | **0** |
| 40 | −3.384 | −3.384 | −32.761 | +28.628 | 0 |

Three things follow, and they are the core findings of this task.

> **The restoring tendency of EBU-random is produced entirely by the
> affordability gate.** At `B = 0` it is 5.4× more restoring than the control
> at high deviation and restores from 99.8% of states against the control's
> 34.5%. The advantage decays monotonically with accumulated capacity and
> reaches **exactly zero** at `B_i = 29`, where Theorem R2 makes the two
> policies the *same process*.

> **The gate is also the only thing restraining the hostile actor — and it
> restrains it far more than it helps the random one.** At `B = 0` a hostile
> actor still drifts inward from 70.2% of states, because it cannot afford the
> destructive options. By `B ≈ 8` its high-deviation drift has crossed to
> outward, and at saturation it restores from **0.6%** of states with a drift of
> `+28.6`.

> **Capacity V1 provably ends in the regime where all of this is gone.** The
> threshold is `B_i >= 29`; the Stage-B exploratory re-reading measured median
> `min_i B_i` rising 77.5 → 171 → 300.25 across blocks — roughly ten times past
> it.

## 2. Registered-data results, by policy

Aggregated over the registered analysis window, registered menu. `g_A(v)` is
the actor-layer drift conditioned on post-disturbance `V(z)`; negative is
restoring.

| `V(z)` | EBU-random | control | hostile |
|---|---|---|---|
| 1 | +1.102 | +1.403 | +0.523 |
| 4 | +0.816 | +1.471 | −0.060 |
| 9 | +0.734 | +1.305 | −0.984 |
| 16 | +0.555 | +1.456 | −1.558 |
| 25 | +0.687 | +1.411 | −1.305 |
| 49 | +0.317 | +1.462 | +0.214 |
| 81 | **−1.084** | −0.212 | — |
| 169 | **−1.944** | +1.186 | +0.896 |

(at `p_force = 1/4`; the pattern is the same at every load)

**EBU-random's actor drift is more restoring than the control's at every
deviation with support**, and at large deviation it turns negative while the
control does not. This is mission section 10's primary stupid-proofing
question, answered in the affirmative on the projection.

**The hostile column is the worked example of why `V` is not the state.** It
appears *restoring* at `V = 4–25` and outward at `V = 169`. Both readings are
artefacts of conditioning on `V` alone: a hostile actor at low `V` is poor and
the gate forces it to take earning (restoring) actions, while a hostile actor
at high `V` arrived there by earning and can now afford destruction. The
enumeration separates these cleanly; the projection cannot.

## 3. Registered-data results, by load and menu

Late-window movement of mean `V` across the three analysis blocks, registered
menu:

| load | aligned | EBU-random | control | hostile |
|---|---|---|---|---|
| `1/4` | 0.0 → 0.0 → 0.0 | **33.2 → 39.3 → 44.0** | 75.1 → 74.3 → 75.5 | 134.6 → 134.7 → 132.6 |
| `1/2` | 0.0 → 0.0 → 0.0 | **44.3 → 50.7 → 53.3** | 76.5 → 76.7 → 75.8 | 137.5 → 138.0 → 133.9 |
| `1` | 0.0 → 0.0 → 0.0 | **55.3 → 61.7 → 62.7** | 76.1 → 76.0 → 75.8 | 143.6 → 142.7 → 140.1 |

**EBU-random is the only arm showing sustained OUTWARD DRIFT** (+10.8, +9.0,
+7.4). The control is flat and the hostile arm drifts slightly inward from a
much worse position. This is exactly what section 1's capacity sweep predicts:
the EBU arm starts in the low-capacity regime, where the gate gives it a large
restoring advantage, and migrates toward the saturated regime, where it becomes
the control. **It is the only arm that had regulation to lose.**

The menu factor changed none of this. Removing the three net-zero groups left
every ordering and every qualitative pattern intact.

## 4. Return behaviour from high-deviation shells

Episodes reaching `V >= shell`, and their return to `V <= 25`, pooled over 64
replicates (registered menu, `p_force = 1/4`):

| shell | EBU-random | control | hostile |
|---|---|---|---|
| `V >= 50` | 5869 returns, 34 censored, mean **28** ticks | 4998 / 40, mean 55 | 385 / 61, mean **773** |
| `V >= 100` | 2007 / 18, mean **38** | 2357 / 31, mean 84 | 265 / 60, mean 1041 |
| `V >= 150` | 649 / 11, mean **45** | 1326 / 25, mean 106 | 221 / 58, mean 1159 |
| `V >= 200` | 196 / 3, mean **49** | 777 / 16, mean 120 | 182 / 50, mean **1248** |

EBU-random returns from the deepest shell about **2.4× faster** than the
control and enters it 4× less often. The hostile arm is 25× slower and
**fails to return in 50 of 232 episodes** — the clearest instance of
EXCURSION NON-RETURN in the dataset.

## 5. High-deviation capture

Fraction of the analysis window spent at `V >= 250`:

| load | aligned | EBU-random | control | hostile |
|---|---|---|---|---|
| `1/4` | 0.0000 | 0.0006 | 0.0074 | **0.0519** |
| `1/2` | 0.0000 | 0.0018 | 0.0079 | **0.0559** |
| `1` | 0.0000 | 0.0040 | 0.0076 | **0.0716** |

The hostile arm shows **HIGH-DEVIATION CAPTURE** at 7–9× the control's rate.
EBU affordability does not prevent it.

## 6. Does a restoring operating region exist?

**Yes, and its location depends entirely on the capacity regime.**

- **Aligned:** restores from 99.8% of states in both regimes. Its operating
  region is the reference itself.
- **EBU-random, low capacity:** restoring from `V = 1` upward — `g_T` is
  `+0.60` at `V = 0` and `−0.01` at `V = 1`, then monotonically more negative.
  The operating level is effectively `v* ≈ 1`.
- **EBU-random, saturated capacity:** inherits the control's structure exactly.
- **Control:** a restoring region exists but only at large deviation, and the
  curve is **not monotone** — positive near `+2.43` at low `V`, negative around
  `V = 73–91`, positive again through `V = 93–192`, reliably negative only
  above `V ≈ 217`. It crosses zero several times, so no single `v*` is quoted.
- **Hostile, saturated:** **no restoring region at all** in any practical sense
  — 0.6% of states.

## 7. Does any policy show outward high-deviation drift?

**Yes. The hostile arm once capacity accumulates**, at `+28.6` mean drift over
high-deviation states with the gate inactive, restoring from 0.6% of states.
This is LOSS OF RESTORING TENDENCY in the registered failure vocabulary, and it
is a property of the mechanism rather than of any particular trajectory.

The EBU-random arm shows OUTWARD DRIFT in the weaker sense of section 3 — a
late-window distribution moving upward — while still drifting inward from most
states. The two findings are consistent: it is migrating between regimes.

## 8. What this does not establish

- Nothing here is confirmatory evidence; the registered study's conclusions are
  unchanged.
- The exact results are theorems about **this** world — 3 cells, `sigma =
  (1,1,1)`, one quantum, complete topology. They do not generalize by
  assumption.
- No Foster–Lyapunov claim is made; see `EBU_RESTORING_TENDENCY_FOUNDATION.md`
  §10 for why none is available.
- The capacity sweep uses **uniform** `B_i = b`. Real trajectories have unequal
  balances, and the gate is governed by the poorest cell, so the sweep is a
  one-parameter section through a three-dimensional regime space, not the whole
  of it.
- Capacity V2 was not analysed here and has no behavioural evidence.
