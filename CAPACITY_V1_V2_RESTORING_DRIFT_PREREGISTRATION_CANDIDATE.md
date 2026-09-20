# Capacity V1 vs V2 restoring drift — preregistration CANDIDATE

**Status: CANDIDATE. Not frozen, not registered, not executed. No execution is
authorized by this document.**

Mission section 20 requires the **smallest** experiment that answers what
remains unresolved. Most of the original question set has been closed by exact
enumeration and needs no experiment at all.

---

## 1. What is already settled without an experiment

| question | status | source |
|---|---|---|
| Does a restoring-drift structure exist, and where? | **settled exactly**, per state | `exact_state_drift.py` |
| Is EBU-random more restoring than control? | **settled exactly** — 99.8% vs 34.5% of states at `B = 0` | same |
| Does that advantage survive capacity accumulation under V1? | **settled exactly — no.** It decays monotonically to zero at `B_i = 29` | `capacity_drift_sweep.py` |
| Are EBU-random and control the same process at saturation? | **theorem R2** — identical drift maps at every state | `test_restoring_tendency.py` |
| Does V1 reach that regime? | `sum B → ∞` is a theorem; `min_i B_i` measured above 300 against a threshold of 29 | Stage B, exploratory re-reading |
| How much restoring tendency can V2 lose, at most? | **bounded exactly** — 87.7% of states, `g_T(V>=50) = -8.23` | `v2_gate_bound.py` |
| Does V2 fix hostile safety? | **bounded exactly — no.** `+17.5` at its bound, against V1's `+28.6` | same |

**Running a study to re-observe any of the above would produce no information.**

## 2. The one unresolved question

The V2 bound is an envelope, not a location. `-8.23` is the *worst* V2 can do;
`-18.43` is the zero-capacity value. Where V2 actually sits inside
`[-18.43, -8.23]` depends on the joint occupancy of `(x, B)` under the V2
ceiling, which is a dynamical fact that no enumeration can supply.

> **Unresolved:** where inside its exactly-computed envelope does Capacity V2
> operate under persistent disturbance, and does its retained gate prevent the
> outward late-window drift that V1 exhibits?

Everything in section 4 is chosen to answer exactly that and nothing else.

## 3. Hypotheses — registered as hypotheses

- **H1** Realized high-deviation total drift is more negative under V2 than
  under V1, for the EBU-random policy.
- **H2** Late-window outward movement of mean `V` is smaller under V2 than
  under V1, for the EBU-random policy.
- **H3** High-deviation drift is less outward under V2 than under V1, for the
  hostile policy.

**A hypothesis failure will not cause either mechanism to be modified.**

## 4. Design — the smallest that answers it

| item | value | why not larger |
|---|---|---|
| mechanisms | Capacity V1, Capacity V2 | the comparison |
| policies | `ebu_random`, `ebu_hostile`, plus `control_random` once | aligned is a theorem (Theorem A); control is mechanism-independent |
| arms | 5 = (2 × 2) + 1 | |
| loads | one, `p_force = 1/2` | the nested-load question is answered; load is not the variable here |
| menu | registered 21-group only | the menu factor was measured immaterial |
| replicates | 64 | matches existing registered practice, enabling paired sign tests |
| horizon | 8192, burn-in 2048, window 6144 | V1 must be given time to saturate, or H1 is untestable |
| **total** | **320 jobs, 2,621,440 arm-ticks** | ~10 min locally on 12 workers |

That is **21% of the previous study's size**.

## 5. Primary endpoint

```
D_hat_T = mean of dV_total(t) over ticks in the window with V(x_t) >= 50
```

per replicate per arm, computed exactly in integer arithmetic. This is the
realized counterpart of the enumerated `g_T(V >= 50)` and is directly
comparable to the exact values already in hand:

| reference value | source |
|---|---|
| `-18.43` | V1 at `B = 0`, exact |
| `-8.23` | V2 ceiling bound, exact |
| `-3.38` | V1 saturated = control, exact |

**Registered interpretation rule.** A realized `D_hat_T` for V1-random near
`-3.4` confirms saturation within the horizon; near `-18.4` would mean the
horizon was too short and H1 is untested rather than refuted. This is
registered in advance precisely so a short horizon cannot later be read as a
null result.

## 6. Contrasts and inference

Three contrasts, paired by replicate on shared seeds:

1. V2-random vs V1-random — **primary**
2. V2-hostile vs V1-hostile
3. V1-random vs control — replication check against a known exact value

Exact two-sided paired sign test, Holm across the three, family-wise
`alpha = 0.05`. Effect sizes reported first, with distribution-free
sign-based median intervals. `delta_meaningful = 2.0` in `D_hat_T` units,
justified as roughly a quarter of the exactly-computed gap between the V2 bound
and the V1 saturated value.

## 7. Secondary metrics — descriptive, no significance claim

Late-window movement of mean `V` by block; realized `min_i B_i` trajectory and
the fraction of ticks with `min_i B_i >= 29`; fraction of ticks where the gate
binds; high-deviation occupancy; return time from `V >= 200`; the full frozen
battery of `homeostasis/metrics.py`; occupancy diagnostics `O95` and `O99`,
which are **descriptive only** under the current definition.

## 8. Case-library coverage

This design instantiates `RT-C04` (persistent medium demand) crossed with
`RT-C08` (random actors) and `RT-C10` (hostile actors), at two capacity
regimes as section 5 of the library requires. Results are recorded against
those identifiers for both mechanisms, so a later mechanism is compared against
**exactly the same disturbances**.

## 9. Implementation requirement, not yet built

Both `gaussian_harness` and `homeostasis` are pinned by registered code
identities and **must not be modified**. `capacity_v2` carries its own identity
and its harness exposes only two arms.

The study therefore needs a **new package** composing the existing four
policies with a selectable ledger. It must:

- import `homeostasis.policies` and `capacity_v2.ledger` unchanged;
- reuse the registered event order and `NULL_FORCING` rule verbatim;
- carry its own code identity;
- reproduce the registered homeostasis harness tick-for-tick under the V1
  ledger, as the existing suite does for the two-arm harness — this is the
  check that makes the V1 arm a valid comparator rather than a re-implementation.

None of this is built, and building it is not authorized by this document.

## 10. Non-claims

- No result is anticipated. The exact bounds are an envelope, not a prediction
  of where V2 lands.
- V2 has **no** behavioural evidence at present; theorems and static
  conformance are not behaviour.
- This design does not address hostile safety adequately: the exact bound
  already shows V2 remains strongly outward for hostile actors, so a favourable
  H3 would be an improvement and not a solution.
- Nothing here addresses topology or scale (level 7), which no study has
  attempted.
