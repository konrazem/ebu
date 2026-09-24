Extraction complete. Repository untouched; all work read-only against the published export.

## A. REGISTERED ANALYSIS CONTRACT

Derived from preregistration §4, §6, §6a, §7, §8 only.

| element | registered content |
|---|---|
| **Primary endpoints** | **A1:** `stopping_reason` ∈ {`RETURNED_TO_REFERENCE`, `NO_AFFORDABLE_SOLUTION`, `HORIZON_REACHED`}; `return_time`. **A2:** `arrival_state`, `epoch_status`, `menu_size`, `affordable_count`, `physical_consequence`, `induced_p_demand`, `receipts`. **A3:** `prelude_reserve`, `arrival_baseline`, `order_admission_status`, `order_service_epoch`, `order_pending_epochs`, `candidate_table`, `order_outcome`, `served_without_restoration_reason`, `deficit_provenance`, `induced_deficit`, `restoration_outcome` |
| **Secondary / episode-level** | A1: `transitions_recorded` (beside `horizon`), `burden_path`, `restoring_drift`, `plateau_crossings`, `terminal_state`, `terminal_no_active_demand`, `reserve_path`, `restoration_ledger`. A3: residuals ×4, `joint_gate`, `decomposition_gate`, `capacity_source_residual` |
| **Arm comparisons** | **NONE.** §L11 "makes no comparison between arms a success or a failure"; §L244 "the mechanism demonstration, not a comparison"; §L559 "no hypothesis and performs no test"; §L689 forbids "anything comparative between arms as a tested result" |
| **Pairing** | §6: seeds `(1, 2, 3+k, 1000+k)`, k = 0..63; 64 replicates per arm per class; episode defined independently of policy |
| **Censoring / stopping** | A1: S1→S2→S3 in order; `return_time` undefined = censored, retained as `None`. A3: horizon only; `first_simultaneous_closure` = `None` if no closure by N |
| **Failure / integrity** | §8: an integrity hit means the job produced **no valid data** — invalid, not an outcome. Not a censoring category |
| **Registered descriptive summaries** | None beyond the per-episode fields above. `O95` occupancy explicitly **not** an endpoint |

## B. COMPLETE ACCOUNTING — 768/768

| class | episodes | per arm | replicates 0–63 complete | status | integrity failures | manifest-matched |
|---|---|---|---|---|---|---|
| A1 | 256 | 64 × 4 | yes | `COMPLETED` 256 | 0 | 256/256 |
| A2 | 256 | 64 × 4 | yes | `COMPLETED` 256 | 0 | 256/256 |
| A3 | 256 | 64 × 4 | yes | `COMPLETED` 256 | 0 | 256/256 |

**768 accounted, 0 silently dropped, 11,066 epochs.** No job was invalidated, so the §8 category is empty and no episode is excluded.

## C. A1 RESULTS

| arm | `stopping_reason` | `return_time` defined | censored | `terminal_no_active_demand` | `terminal_state` | `V(x_N)` | terminal `B_total` |
|---|---|---|---|---|---|---|---|
| `control_random_no_ebu` | `RETURNED_TO_REFERENCE` 64 | 64/64 | 0 | 64/64 | `(4,4,4)` ×64 | `0` | `9` |
| `ebu_random` | `RETURNED_TO_REFERENCE` 64 | 64/64 | 0 | 64/64 | `(4,4,4)` ×64 | `0` | `9` |
| `ebu_aligned` | `RETURNED_TO_REFERENCE` 64 | 64/64 | 0 | 64/64 | `(4,4,4)` ×64 | `0` | `9` |
| `ebu_hostile` | `HORIZON_REACHED` 64 | 0/64 | **64** | 0/64 | 8 distinct states | `1` ×36, `3` ×28 | `8` ×36, `6` ×28 |

`return_time` distribution (registered field, verbatim): control `{2:33, 3:15, 4:6, 5:4, 6:1, 7:2, 12:1, 14:1, 20:1}`; `ebu_random` `{2:33, 3:14, 4:6, 6:5, 7:1, 8:2, 10:1, 12:1, 14:1}`; `ebu_aligned` `{2:64}`; `ebu_hostile` `{None:64}`.

`plateau_crossings` per episode: control `{0:43, 1:10, 2:4, 3:3, 4:1, 5:2, 9:1}`; `ebu_random` `{0:43, 1:8, 2:4, 3:2, 4:3, 5:2, 6:2}`; `ebu_aligned` `{0:64}`; `ebu_hostile` spread 2–17. `V(x_0) = 9` in all 256. `restoration_ledger` non-empty in 256/256. `N == T` only for `ebu_hostile` (64).

## D. A2 RESULTS — isolated E-demand at equilibrium, zero opening reserve

| arm | `epoch_status` | `arrival_state` | `menu_size` | `affordable_count` | increment | `potential_change` | `induced_p_demand` | balances | n |
|---|---|---|---|---|---|---|---|---|---|
| `control_random_no_ebu` | `EXECUTED` | `SERVED` | 2 | 2 | `(0,−1,1)` | `+1` | `{B:1}` | `B = −1` | 33 |
| `control_random_no_ebu` | `EXECUTED` | `SERVED` | 2 | 2 | `(0,−2,2)` | `+4` | `{B:2}` | `B = −4` | 31 |
| `ebu_random` | `ALL_PLANS_EBU_UNAFFORDABLE` | `ADMITTED_BUT_EBU_UNAFFORDABLE` | 2 | **0** | `(0,0,0)` | `0` | `{}` | all `0` | 64 |
| `ebu_aligned` | same | same | 2 | **0** | `(0,0,0)` | `0` | `{}` | all `0` | 64 |
| `ebu_hostile` | same | same | 2 | **0** | `(0,0,0)` | `0` | `{}` | all `0` | 64 |

Single epoch, `x_0 = x*`. Not generalized to restoration or long-run behaviour.

## E. A3 RESULTS — **baselines are endogenous**

> **Qualification attached to every row:** `arrival_baseline` and `prelude_reserve` are produced by each arm's own prelude. The four arms do **not** face epoch 3 from a common physical or capacity state; differences after epoch 3 may not be read as if they did.
>
> **`RESTORATION_COMPLETED` means:** simultaneous closure, within the horizon, of the deficits tracked at `x_{s+1}` — **not** equilibrium return, **not** sustained closure, **not** absence of new deficits.

| arm | `arrival_baseline` x₃ | `prelude_reserve` (total; owners) | `order_service_epoch` | pending | `tracked_deficits` | `first_simultaneous_closure` | `closure_count`/`tracked` | `order_outcome` |
|---|---|---|---|---|---|---|---|---|
| `control_random_no_ebu` | `(4,4,4)`×48, `(5,3,4)`×9, `(5,4,3)`×4, `(3,5,4)`×2, `(5,5,2)`×1 | `9`(B9)×43, `8`(B8)×15, `9`(A1,B8)×5, `6`(B8,C−2)×1 | 3 ×64 | 0 | `{B:1}`×33, `{B:2}`×23, `{A:1}`×6, `{B:3}`×2 | `5`×50, `6`×13, `7`×1 | 1/1 ×64 | `RESTORATION_COMPLETED` 64 |
| `ebu_random` | `(4,4,4)`×47, `(5,3,4)`×9, `(5,4,3)`×6, `(3,5,4)`×2 | `9`(B9)×43, `8`(B8)×17, `9`(A1,B8)×4 | 3 ×64 | 0 | `{B:1}`×32, `{B:2}`×24, `{A:1}`×6, `{B:3}`×2 | `5`×50, `6`×12, `7`×2 | 1/1 ×64 | `RESTORATION_COMPLETED` 64 |
| `ebu_aligned` | `(4,4,4)`×64 | `9`(B9)×64 | 3 ×64 | 0 | `{B:1}`×64 | `5`×64 | 1/1 ×64 | `RESTORATION_COMPLETED` 64 |
| `ebu_hostile` | `(5,3,4)`×64 | `8`(B8)×64 | 3 ×64 | 0 | `{B:3}`×64 | `6`×64 | 1/1 ×64 | `RESTORATION_COMPLETED` 64 |

`order_admission_status` = `SERVED` in all 256; `served_without_restoration_reason` = `None` in all 256 (L4 matched, never L5). `stopping_reason` = `HORIZON_REACHED`, `transitions_recorded` = 32 = `horizon` in all 256 — so **no `first_simultaneous_closure` was horizon-censored** (all ∈ {5,6,7}).

## F. REGISTERED PAIRED CONTRASTS

**None computed, because none is preregistered.** The pairing machinery is nonetheless intact and verified: across all 192 (class, replicate) cells, the four arms' configurations differ in **nothing but `policy`** (0/192 exceptions) and share one seed tuple (0/192 exceptions). No effect size, contrast, confidence interval or test was registered, so none is introduced.

## G. EXPLORATORY APPENDIX

Empty. Every quantity in C–E is a registered field or an element of a registered sequence. The only derived items are tabulations of registered fields (counts, distributions, and the min/max of `transitions_recorded`); no unregistered metric, threshold or summary statistic was constructed, and no alternative metric was searched for.

## H. INTEGRITY CHECK

Every number traces to `results/demand_driven_stage_a/`: `EPISODES_A1.json.gz` `sha256:2fd1c855…`, `EPISODES_A2.json.gz` `027e6263…`, `EPISODES_A3.json.gz` `7c6d025d…`, `JOB_MANIFEST.json` `8c9772ce…`, `EXECUTION_INVENTORY.json` `4ed84363…`. Episode counts, epoch total (11,066) and run-id set all re-derived here and consistent with Gates 1–2.

---

# GATE 3 CONDITIONAL PASS

**Exact analysis qualification** — two registered A3/A1 endpoint fields are not directly extractable from the preserved artifacts, and were reconstructed rather than read:

1. **`capacity_source_residual`** (registered §7 A3: "exactly 0 at every epoch and at the end") is **not persisted** in any artifact. Gate 1 reconstructed it from `balance_total`, `potential_*`, and the verified absence of external forcing: exactly `0` at all 11,066 epochs. The registered field itself cannot be read back.
2. **`reserve_path`** is emitted at length `N` (`t = 1..N`) against the registered `t = 0..N`; the omitted `B_total(0)` is pinned to exactly `0` by the accounting identity at all 2,618 A1 checks.

Neither is analytic drift — no metric was changed, no criterion invented, no contrast manufactured, no threshold tuned. Both are carried from Gate 1 and are restated here because they bear on **extractability of registered endpoints**, which is this gate's subject.

The three Gate-2 carry-forwards are attached where they bite: uniform-over-plan multiplicity (exposure: repeated post-state in the arrival menu in 9 `control` and 9 `ebu_random` A3 episodes, shape 4 plans → 3 outcomes; outcome-invariant for `ebu_aligned`/`ebu_hostile`; **no post-hoc reweighting applied — the registered sampling rule stands**); A3's endogenous baseline; and the frozen scope of `RESTORATION_COMPLETED`.

**READY FOR SCIENTIFIC GATE 4 — ADVERSARIAL INTERPRETATION**

Gate 4 not begun. No arm was called better, no mechanism claim made, no result generalized beyond `study-one-v1`, and no Dynamic EBU theory applied.