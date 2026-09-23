# Stage-A preregistration — pre-execution correction 1

**Narrow precedence.** This record governs the identity and the change history
of `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` and nothing else. It changes no
scientific content of its own: the corrected text lives in the preregistration,
and this document exists so that the correction is recorded rather than applied
silently.

| | |
|---|---|
| document corrected | `DEMAND_DRIVEN_STAGE_A_PREREGISTRATION.md` |
| superseded identity (freeze 1) | `72a950721a81a7e0e2dba28e1a1a47124769a3378a4d28cd34d7e1f8aace78de` |
| **proposed** identity (freeze 2) | `36fb53b6a3fca61be79391d1ab02927f148fa0d13f526f9b0895903f0fa91c75` |
| epochs executed under freeze 1 | **zero** |
| epochs executed under freeze 2 | **zero** |
| behavioural outcomes inspected | **none** |
| recomputation | `scripts/stage_a_preregistration_identity.py` — reads the file, executes no model code |

---

## 1. Why a correction rather than a re-freeze

`AGENTS.md` provides a correction procedure for **committed** result artifacts
and manifests, and the repository's convention for amending a frozen
prospective source is a separate addendum whose precedence is stated narrowly
(the Gate 1D-C addenda are the worked example). Neither fits exactly here:

- the preregistration is **uncommitted** — it has never entered the Git record;
- **no epoch has executed** under freeze 1, so no data exists that the
  correction could bias;
- the corrections are **reconciliation with an implementation that did not
  change**: `demand_driven_ebu` is byte-identical to the audited coordinate,
  hash `f4e31a2a3f0fa0191532388484cb8e6bba95a1f937ce26ebfbdeb2fdd83eec48`.

So freeze 2 is **proposed, not claimed**. The authorization needed is the
author's confirmation that a pre-execution correction of an uncommitted,
unexecuted preregistration may be re-frozen in place with this record attached,
rather than requiring a fresh preregistration identity issued through a
separately authorized stage.

**Until that confirmation, treat freeze 2 as prepared and not in force.**

---

## 2. What changed, exactly

Every item is a reconciliation of the document with the audited implementation.
**None was derived from an observed outcome, and none altered the mechanism.**

### 2.1 Epoch convention and A1 stopping (§2, §7, §8)

| before | after |
|---|---|
| `return_time` defined as "the first epoch index with `state_after == x*`" in the reporting table, and as the post-state index `t+1` in §2 | one definition everywhere: the first **post-state index** `t+1` with `x_{t+1} == x*` |
| `T` used both as a transition count and as a maximum index | `T` is the **declared maximum number of transitions**; `transitions_recorded = N` is reported beside it, and `N < T` on an early stop |
| `stopping_reason` included `NO_PHYSICAL_SOLUTION` | removed; the normal outcomes are `RETURNED_TO_REFERENCE`, `NO_AFFORDABLE_SOLUTION`, `HORIZON_REACHED` |
| `NO_COMPLETE_PHYSICAL_PLAN` away from `x*` declared an integrity failure without scope | **scoped to A1**, the only P-only episode, because the 91-state enumeration that proves `x*` is the only absorbing state was run on the P-only graph. In A2/A3 a blocked economic component reporting it is an ordinary outcome |
| `terminal_no_active_demand` obtained by observation | **derived** from `x_N`; no extra epoch is executed |

### 2.2 A3 path-independent assertions (§4, §7)

| before | after |
|---|---|
| "both service plans for the order are sourced from `B`, with exact EBU `-1` and `-4`" stated as fixed regardless of path | demoted to **equilibrium-conditional examples**, true only if the arm stands at `x*` when the order arrives |
| affordability declared decidable against `B_B(3)` alone | decided **per owner** against the recorded vector `(B_A(3), B_B(3), B_C(3))` |
| the arrival baseline implicitly `x*` | the **recorded** pre-arrival state `x_3`, with an analytical witness that it need not be `x*` |
| no distinction between pre-existing and induced deficits | `deficit_provenance` records pre-state and post-state deficit vectors and classifies each coordinate as pre-existing, newly created or deepened |
| non-chain cases undefined | four declared outcomes: `ORDER_REJECTED`, `ORDER_PENDING_UNAFFORDABLE`, `SERVED_WITHOUT_RESTORATION`, `RESTORATION_COMPLETED`, each reported as itself |
| aggregate identity stated bare | retained **with its three assumptions named**: quiet disturbance, no admitted service before epoch 3, `B_total(0) = 0` |

**The analytical witness**, verified by isolated pure-function evaluation on
declared synthetic states with **no prelude executed**:

```
(1,7,4) --B->A@1--> (2,6,4) --B->A@1--> (3,5,4) --B->A@2--> (5,3,4)
   V=9      EBU +5      V=4     EBU +3     V=1     EBU  0      V=1
```

Pre-arrival account vector on this path: `(0, 8, 0)`, total `8 = V(x_0) - V(x_3)`.
At `(5,3,4)`, with a pre-existing one-unit deficit at `B`, the admitted one-unit
order at `C` has a four-plan menu:

| plan | post-state | aggregate EBU | owner receipts | serves | deficit worsened |
|---|---|---|---|---|---|
| `B->C@1` | `(5,2,5)` | `-2` | `B: -2` | order only | `B` (pre-existing) |
| `B->C@2` | `(5,1,6)` | `-6` | `B: -6` | order only | `B` (pre-existing) |
| `{A->B@2, B->C@1}` | `(3,4,5)` | `0` | `A: +1`, `B: -1` | order **and** `P:r\|B` | `A` (newly created) |
| `{A->B@2, B->C@2, C->B@1}` | `(3,4,5)` | `0` | `A: +1`, `B: -2`, `C: +1` | order **and** `P:r\|B` | `A` (newly created) |

### 2.3 Deterministic arrival schedule (§4)

Retained as a **proposed Stage-A-only mechanism-demonstration fixture**, with
four limits stated in the document: its schedule is fixed independently of any
observed outcome; it is not evidence about a stochastic arrival law; it
authorizes nothing for Stage B and decides no arrival-law parameter; and the
scope declaration permitting it is a **modeling disposition, not a theorem**.
It was not replaced by a stochastic process and its scope was not broadened.

---

## 3. What did NOT change

- the environment, world, references, quanta, routes or conserved total;
- the A1/A2/A3 fixtures: opening states, displacement, prelude length, arrival
  epoch, horizons;
- the policy arms, seeds, replicate structure or job count;
- the opening balances, which remain zero for every owner;
- **any line of `demand_driven_ebu`.** The implementation is byte-identical to
  the audited coordinate.

---

## 4. Verification performed for this correction

Execution-free throughout. `EconomyRun.run_epoch` and `EconomyRun.run` were
**monkey-patched to raise** for the duration of every check below, so an
accidental transition would have failed loudly rather than passing quietly.

| check | result |
|---|---|
| the `(1,4,7)` refinement witness: whole `+2`, halves `+2` then `0`, second half legitimate | reproduced |
| conditional refinement counts: 152 legal two-unit restorations, 120 with both halves legitimate, 32 where the first half clears the deficit | reproduced, **0** failures of the conditional statement |
| the served-set-relative joint-plan example at `(3,6,3)` | reproduced: `{B->A@1, B->C@1}` serves both, each singleton serves one, the joint plan is in the menu |
| the A3 four-plan witness at `(5,3,4)` | reproduced exactly, EBUs `-2, -6, 0, 0` with the receipts tabulated above |
| 768 Stage-A job identities, distinct and reproducible | **768 / 768**, construction only, zero epochs |
| protected package identities unchanged | `gaussian_harness`, `capacity_v2`, `homeostasis` — `git diff` empty |
| pure-function conformance subset | **51 checks, 0 failed**, across 10 groups |
| analytical enumeration module | **308 deterministic checks, 0 failed** |

Full suites that execute epochs were **not** run in this pass, by instruction.
Their last recorded result, at the unchanged implementation, was 1045 passed /
0 failed.

---

## 5. Standing author decision

Whether **unrestricted subdivision invariance** is required instead of the
proved conditional form. The proved result is:

> if a two-unit restorative action is legitimate and the quanta permit the
> split, the first half is legitimate, and the second half is legitimate for as
> long as a deficit remains at the destination.

In 32 of 152 cases the first half clears the deficit and the second half is
correctly refused as an unrelated continuation. Obtaining unrestricted
invariance would need persistent demand, historical entitlement or an overshoot
exception — **none of which was introduced**, and each of which would change
the model. Recorded as unresolved.
