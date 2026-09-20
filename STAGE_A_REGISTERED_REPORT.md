# Stage-A registered scientific report

Protocol `EBU-STAGE-A-V1`. This reports the outcome of the preregistered study.
It is not a claim that EBU is stable.

## 1. Identity

| Item | Value |
|---|---|
| Repository branch | `gaussian/stage-a-environment` |
| Preregistration commit `C_pre` | `025eee1efaa0723d04234cfe5ae9d1a319de7206` (tag `stage-a-preregistration`) |
| Seed manifest commit | `2ec28e81eaf0a4dbd7b16015d2079faf8f5c3a27` |
| Analysis freeze commit | `1465bcd4b7d94a94a60aea864c825fde71a721ac` |
| Execution artifacts commit | `349872b6ad7f82c5d25d981e1f5ec831f9d21924` |
| `gaussian_harness` code identity | `a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55` |
| Configuration identity | `9058e253334a66f02ee6ac6c51800b2a70ac4dc88f136b90b4db797dc626e196` |
| Replicates / horizon | 128 paired / 256 post-shock actor ticks |

The analysis implementation was frozen before any registered result existed and
was not modified afterwards.

## 2. GATE A — foundation integrity: **PASS**

| Check | Result |
|---|---|
| Replicates observed / expected | 128 / 128 |
| Both arms present for every replicate | yes |
| Max absolute accounting residual | **exactly 0** |
| Max absolute conservation residual | **exactly 0** |
| Max negative physical stock | **exactly 0** |
| EBU-arm negative capacity ticks | 0 |
| Code identity matches preregistration | yes, all 256 artifacts |
| Configuration identity unique and matching | yes |
| Seeds match the mechanically derived manifest | yes, all 128 pairs |
| Matched pairs share shock and `D_r` | yes, all 128 |
| Replay: independent re-execution byte-identical | yes, replicates 0, 7, 63, 127, both arms |
| Unregistered fallback actions | none |
| Post-shock statuses observed | `EXECUTED` only |

`V + sum(B) = D` and `sum_i x_i = 30` held as exact rational equalities at every
one of the 65,536 post-shock ticks in both arms. No tolerance was used.

## 3. Primary result

Endpoint `A_r = (1/(H D_r)) sum_{t=1}^{H} V_r(t)`, exact rational. `D_r = 4`
for every replicate (world symmetry, as the preregistration recorded).

| Quantity | Value |
|---|---|
| Median `A_EBU` | 0.24414 (`125/512`) |
| Median `A_CONTROL` | 14.9736 |
| `A_EBU` min / max | 0.2061 / 0.2920 |
| `A_CONTROL` min / max | 4.8789 / 37.4346 |

Exact two-sided paired sign test, `alpha = 0.05`:

| Quantity | Value |
|---|---|
| Negative `Delta_r` (EBU lower) | **128** |
| Positive `Delta_r` (EBU higher) | 0 |
| Tied | 0 |
| Trials | 128 |
| Exact p-value | `1/170141183460469231731687303715884105728` = `2/2^128` ≈ 5.877e-39 |
| Significant at 0.05 | yes |
| Median paired difference | -14.7148 |
| Mean paired difference | -16.0719 |
| Range of paired differences | -37.178 to -4.642 |

## 4. The primary test is largely structurally forced — read section 3 with this

The preregistration (section 15) recorded that in the EBU arm
`V + sum B = D` with `B >= 0` implies `V <= D`, hence `0 <= A_EBU <= 1`. That
bound is an exact property of the accepted accounting model, not an observation.

Observed decomposition:

- `A_EBU <= 1` in 128/128 replicates — **structural**, guaranteed in advance.
- `A_CONTROL > 1` in 128/128 replicates — **empirical**, not guaranteed. The
  control could have stayed under 1 and did not in any replicate.
- Consequently the paired ordering was forced by the bound in **128/128**
  pairs.

So the unanimous sign test mostly re-detects the structural bound combined with
the empirical fact that the unconstrained control leaves the `[0, D]` band. Its
p-value is valid under its stated null but carries far less independent
scientific information than its magnitude suggests. **The preregistered primary
endpoint had almost no power to return anything other than unanimity once the
control exceeded the bound.** That is a design limitation, recorded here as
discovered; the preregistration is not amended.

The scientifically informative content is therefore the effect magnitudes and
the trajectory diagnostics below, not the p-value.

## 5. Dynamics — the EBU arm does not settle

Trajectory classes under the frozen deterministic rules:

| Arm | Class | Count |
|---|---|---|
| EBU | `REPEATED_CYCLING` | **128** |
| EBU | all other classes | 0 |
| Control | `NEVER_REACHED_EQUILIBRIUM` | 65 |
| Control | `REACHED_AND_LEFT` | 54 |
| Control | `REPEATED_CYCLING` | 9 |

Descriptive secondary diagnostics (no significance claimed, no multiplicity
correction performed because no confirmatory inference is drawn from them):

| Diagnostic | EBU arm | Control arm |
|---|---|---|
| Reached `V = 0` at least once | 128/128 | 63/128 |
| Median first hitting time | 3.5 ticks | 22 ticks |
| Median equilibrium occupancy | 0.252 | 0.000 |
| Median departures from `V = 0` | 46 | 0 |
| Median terminal `V/D` | 0.250 | 14.75 |
| Max terminal `V/D` | 1.000 | 54.25 |
| Median minimum `V/D` | 0.000 | 0.250 |
| Deadlock ticks (total, all replicates) | **0** | **0** |
| Median executed events with `E > 0` | 62 | 104 |
| Median executed events with `E < 0` | 60 | 108 |
| Median terminal total capacity | 3.000 | -55.000 |
| Min terminal total capacity | 0.000 | -213.000 |

Three observations matter more than the p-value:

1. **The EBU arm reaches equilibrium quickly and never stays.** Every replicate
   hit `V = 0` (median 3.5 ticks) and every replicate then left it again, a
   median of 46 times. No replicate was classified `REACHED_AND_STAYED`. This is
   the exact-accounting-with-poor-dynamics cycling anticipated before execution:
   `(V, sum B)` exchanges between roughly `(D, 0)` and `(0, D)`. Low cumulative
   deviation here means *bounded oscillation*, not convergence.

2. **Executed positive- and negative-EBU events are nearly balanced in the EBU
   arm** (median 62 vs 60), which is the mechanism of the cycling: capacity is
   earned by restoration and then spent on damage at almost the same rate.

3. **No deadlock occurred anywhere**, in either arm, in any of the 65,536
   post-shock ticks. The deadlock semantics the design was built to detect were
   exercised by the conformance suite but never triggered by the registered
   world. With quantum 1 on a 3-cell complete graph, an affordable restorative
   action was always available.

The control's median terminal capacity of -55 quantifies what the affordability
gate refuses: the control accumulates large notional debt that the EBU rule
would have forbidden.

## 6. GATE B — scientific dynamical disposition

**Observed: substantially lower cumulative deviation under EBU affordability,
with the paired ordering structurally forced, and with no convergence in either
arm.**

Stated precisely:

- The EBU arm kept deviation within a narrow band (`A_EBU` in 0.206–0.292) and
  the control did not (`A_CONTROL` in 4.88–37.43).
- The EBU arm's confinement is partly guaranteed by the accounting identity plus
  nonnegative capacity, so it is not independent evidence of a restoring
  tendency.
- The genuinely empirical findings are that the unconstrained control diverges
  far above the injected disturbance, and that the constrained arm cycles
  perpetually rather than settling.

## 7. GATE C — model change requirement

**No model change is required or authorized by this result.** Nothing observed
contradicts the frozen model, and every exact invariant held. The cycling is a
dynamical property of the mechanism as declared, not a defect.

A negative, null or unfavourable Stage-A outcome would not have authorized
changing the mechanism either, and none is made.

## 8. Prior exploratory conformance exposure

Before registration, four short trajectories were observed on this same world
at `(forcing_seed, actor_seed)` pairs `(11,29)`, `(11,30)`, `(11,31)`, `(3,7)`,
for at most 8 ticks each, for software conformance only. No parameter was tuned
afterwards. Registered seeds were derived mechanically from `C_pre`; no derived
pair collided with a disclosed pair, and none was included or avoided by hand.
No result-dependent seed exclusion occurred.

## 9. What this study does NOT establish

- It does **not** show that EBU is stable. The EBU arm never settled at
  equilibrium in any replicate.
- It does **not** show convergence, damping or a stationary distribution.
- It does **not** establish that the capacity rule is correct causal or ethical
  attribution, or that the common-path receipt is a fair share.
- It does **not** support a boundedness claim. Both arms live on a bounded
  fixed-mass simplex; `A_EBU <= 1` is structural.
- It does **not** generalize beyond one synthetic 3-cell lossless world, one
  shock magnitude `D = 4`, one potential, quantum 1 and `m_max = 2`.
- It does **not** authorize Stage B by implication, nor any economic or
  institutional claim.
- The control is a scientific control, not a rival controller that lost.

## 10. Limitations discovered during this study

1. The primary endpoint is bounded above by construction in one arm only, which
   made the preregistered test nearly deterministic. A Stage-B primary endpoint
   should either be unbounded in both arms or be conditioned on the bound.
2. World symmetry fixed `D_r = 4` for every replicate, so the design varied the
   shock address but not its magnitude.
3. Deadlock was never observed, so Stage A provides no empirical information
   about deadlock frequency under this mechanism.
