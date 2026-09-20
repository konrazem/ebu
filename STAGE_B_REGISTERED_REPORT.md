# Stage-B registered scientific report

Protocol `EBU-STAGE-B-V1`. This reports the preregistered continuous-forcing
study. It is not a claim that EBU is stable.

## 1. Identity

| Item | Value |
|---|---|
| Branch | `gaussian/stage-a-environment` |
| Preregistration `C_pre_B` | `4c826a9be4c6306fa57698eb23c1076ebf75b970` (tag `stage-b-preregistration`) |
| Seed manifest commit | `8a41e114f87bf86b07be833f97e94deac7e04258` |
| Analysis freeze commit | `cda963261c09b4939e64f5c411424b04221e164c` |
| Execution artifacts commit | `5391518e81a8a627270b9fff42223978223e871c` |
| `gaussian_harness` code identity | `a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55` |
| Configuration identity | `46b71dd1e09d283346216470e347d33320233176c91a3523d0765f69037a48f2` |
| Replicates / horizon / burn-in | 64 paired / 8192 / 2048 |
| `V_max` (exact) | 300 |

The code identity is **identical to Stage A's**, so the mechanism under test is
unchanged. No capacity decay, expiry, cap, demurrage, taxation, pooling,
borrowing, actor intelligence or EBU-maximizing choice exists anywhere.

## 2. A. Exact mathematical and accounting properties — **PASS**

| Check | Result |
|---|---|
| Replicates / arms | 64/64, both arms present |
| Horizon completed | 8192 in every run |
| `V_t + sum_i B_i(t) = J_t` | violated in **0 of 1,048,576** ticks |
| Max accounting residual | **exactly 0** |
| Max conservation residual | **exactly 0** |
| Max negative physical stock | **exactly 0** |
| EBU-arm negative capacity ticks | 0 |
| Code / configuration identity | unique and matching preregistration |
| Seeds match derived manifest | all 64 pairs |
| Replay, full 8192-tick horizon | byte-identical, replicates 0 and 63, both arms |
| Unregistered fallback | none |

## 3. B. Primary physical deviation comparison

`L_r = (1/6144) sum_{t=2049}^{8192} V_r(t)/300`, exact rational. Bounded in
`[0,1]` in **both** arms by common physical constraints only — no EBU-only
structural bound can force the ordering. This is the correction to Stage A's
design fault, and it held: both arms' observed ranges sit well inside `[0,1]`
and overlap the same region of the scale.

| Quantity | Value |
|---|---|
| Median `L_EBU` | 0.199110 |
| Median `L_CONTROL` | 0.255138 |
| `L_EBU` range | 0.15623 – 0.23668 |
| `L_CONTROL` range | 0.20726 – 0.29124 |
| Negative / positive / tied `Delta_r` | **64 / 0 / 0** |
| Exact two-sided sign test | `p = 2/2^64 = 1/9223372036854775808` ≈ 1.084e-19 |
| Significant at `alpha = 0.05` | yes |
| Median paired difference | **-0.055872** |
| Mean paired difference | -0.056014 |
| Paired difference range | -0.10060 – -0.00300 |
| Sign-based 95% CI for the paired median | **[-0.061609, -0.050318]**, `k = 23`, order statistics 24 and 41 |

Unlike Stage A, this ordering is **not** structurally forced. The ranges of the
two arms overlap on the common scale, and the control's endpoint was free to
fall below the EBU arm's in any replicate. It did not in any of the 64.

## 4. C. Practical-effect comparison

`delta_meaningful = 0.05` on the `V/V_max` scale, declared before execution and
kept separate from `alpha`.

Whole-window `|median Delta_r| = 0.0559`, which **exceeds 0.05 — but only just**.
The 95% CI is `[-0.0616, -0.0503]`, whose nearer endpoint is 0.0503: the
practical threshold sits essentially at the edge of the interval.

More important, the effect is **not stable across the window**:

| Block (2048 ticks each) | Median paired difference | Negative |
|---|---|---|
| 1 (t 2049–4096) | **-0.074659** | 63/64 |
| 2 (t 4097–6144) | **-0.048378** | 60/64 |
| 3 (t 6145–8192) | **-0.044775** | 61/64 |

By blocks 2 and 3 the median paired difference has fallen **below** the
preregistered practical threshold. The whole-window figure clears 0.05 only
because the first block does.

## 5. D. External forcing exposure differences

Arms were paired on the same raw environmental process, not the same applied
increment, as registered.

| Arm | NULL_FORCING fraction, blocks 1/2/3 |
|---|---|
| EBU | 0.0229 / 0.0251 / 0.0261 |
| Control | 0.0359 / 0.0344 / 0.0337 |

The control suffers more `NULL_FORCING` because it drives cells closer to
empty, leaving sources unable to supply `q0`. So the arms did receive different
applied forcing, by roughly one percentage point of ticks, in the direction of
the control receiving *less* applied forcing. Block-3 sums: EBU `G+` 9380,
`G-` 8267; control `G+` 10273, `G-` 9308. Cumulative signed `J` at horizon end:
EBU 5434, control 3940.

This exposure difference is treatment-caused and was deliberately excluded from
the primary normalization, which is why `V_max` was used instead.

## 6. E. Physical late-window diagnostics (block 3)

| Diagnostic | EBU | Control |
|---|---|---|
| Mean `V/V_max` | 0.2060 | 0.2525 |
| Variance | 0.02997 | 0.03757 |
| Median | 0.1633 | 0.2100 |
| q90 / q99 | 0.4300 / 0.8100 | 0.5633 / 0.8133 |
| Equilibrium occupancy | 0.00342 | 0.00244 |
| Boundary occupancy (`min_i x_i = 0`) | 0.0789 | 0.0991 |
| Deadlock fraction | **0** | **0** |
| No-execution fraction | **0** | **0** |
| Autocorrelation `r_1` / `r_64` / `r_256` | 0.9492 / 0.0421 / -0.0022 | 0.9503 / 0.0658 / -0.0020 |
| Relaxation lag (first frozen lag with `r_k < 1/e`) | 32 | 32 |

The two arms have **the same relaxation timescale** (lag 32) and nearly
identical short-lag autocorrelation. The EBU constraint shifts the level of the
deviation distribution without changing its temporal structure.

## 7. F. Capacity drift — the registered falsification target

**Confirmed.** Capacity grows secularly and does not saturate.

| Block | EBU mean `B_tot` | EBU end `B_tot` | EBU growth/tick |
|---|---|---|---|
| 1 | 2325.6 | 2997.0 | 0.6353 |
| 2 | 3619.8 | 4253.5 | 0.6677 |
| 3 | 4794.5 | 5400.0 | 0.5583 |

Median terminal `B_tot` is 5400 while `V` never exceeds 300. This is exactly
the mechanism predicted before execution: the curvature term `(1/2)u^T H u`
equals exactly `+1` on every applied forcing event, so `J` drifts upward, and
because physical conservation bounds `V`, the drift must accumulate in
`sum_i B_i`.

Terminal capacity concentration `max_i B_i / sum_i B_i` in the EBU arm: median
**0.6616** — capacity concentrates substantially in one cell. (For the control
the same formula returns 2.0333, which is **not** a valid concentration index:
the control's shadow ledger is signed, so the ratio is not bounded by 1. It is
reported only to show the formula was applied identically, and it should not be
read as a concentration.)

## 8. G. Affordability rejection persistence

**The constraint weakens monotonically.**

| Block | EBU `rho_reject` | Control `rho_reject` (counterfactual) |
|---|---|---|
| 1 | 0.0662 | 0.6469 |
| 2 | 0.0497 | 0.5808 |
| 3 | 0.0332 | 0.5282 |

Zero ticks had an undefined `rho_reject`; the registered zero-denominator
convention was never exercised.

In the EBU arm the fraction of physically feasible groups refused on capacity
grounds **halved** across the analysis window, from 6.6% to 3.3%. The control's
counterfactual figures show how much *would* have been refused had the gate
been active — around 53–65% — confirming that the gate is doing real work in
the EBU arm while progressively doing less of it.

## 9. H. Does the EBU arm approach the control over time?

**Yes, directionally, and the study does not reach the limit.**

Three independent registered diagnostics move together:

1. Paired difference shrinks: -0.0747 → -0.0484 → -0.0448.
2. `rho_reject` halves: 0.0662 → 0.0497 → 0.0332.
3. `B_tot` keeps growing without saturating: 2998 → 4254 → 5400.

This is the registered falsification target being met: accumulated capacity
progressively weakens affordability itself, and the constrained arm becomes
more like the unconstrained control.

**What the study does not establish:** that the difference reaches zero. Over
this 8192-tick horizon it is still clearly negative in block 3 (61/64
replicates). The trend is consistent with eventual nonbindingness but the
horizon does not demonstrate a limit, and no extrapolation is registered.

Per section 15 of the preregistration, no new significance tests were created
for these block comparisons.

## 10. I. Deadlock and boundary phenomena

**Zero deadlock ticks and zero no-execution ticks in both arms across all
1,048,576 ticks.** Stage A also observed none. The deadlock semantics remain
exercised only by the conformance suite. Under continuous forcing at `q0 = 1`
on a 3-cell complete graph, an affordable nonempty group was always available —
unsurprising in hindsight given the large accumulated capacity.

Boundary occupancy (some cell exactly empty) was 7.9% of ticks in the EBU arm
and 9.9% in the control, which is the direct cause of the `NULL_FORCING`
difference in section 5.

## 11. J. Stationarity limitations

Reported separately per object, as registered.

- **Physical state.** Control mean `V/V_max` across blocks: 0.2571 → 0.2527 →
  0.2525, maximum block-to-block drift 0.0043 — close to flat. EBU arm:
  0.1877 → 0.2018 → 0.2060, maximum drift **0.0142**, still rising and of the
  same order as the effect being measured (0.05).

  For the EBU arm the report therefore states:
  **NO EVIDENCE OF LATE-WINDOW STATIONARITY.**

  Burn-in was not moved or extended, and the window was not re-cut.

- **Account state.** `sum_i B_i` is plainly **not** stationary in either arm; it
  grows at roughly 0.43–0.67 per tick throughout and shows no sign of
  saturating.

- **Joint process.** The joint `(x, B)` process is **not** claimed to possess a
  stationary distribution, and these results are consistent with it not having
  one. The physical marginal in the control looks close to recurrent while the
  accounts diverge — exactly the split the preregistration required be reported
  separately.

## 12. What this study does NOT establish

- It does **not** show that EBU is stable, convergent or damping.
- It does **not** show a stationary joint system; the accounts diverge.
- It does **not** establish that the affordability difference reaches zero, only
  that it shrinks over this horizon.
- It does **not** establish that the capacity rule is correct causal or ethical
  attribution, nor that the common-path receipt is a fair share.
- It does **not** generalize beyond one synthetic 3-cell lossless world, one
  potential, one fixed forcing amplitude `q0 = 1`, quantum 1 and `m_max = 2`.
- A single forcing amplitude was used by design; forcing-intensity dependence is
  untested.
- The control is a scientific control, not a rival controller that lost.
- The finding of secular capacity growth is evidence **about the present
  mechanism**. It does **not** authorize inserting a new one.

## 13. Prior exploratory conformance exposure

Stage B: one 512-tick paired run at non-registered seeds `(1, 1)`, to verify the
continuous-forcing and `NULL_FORCING` path. No registered trajectory was
observed before registration, and the derived manifest contains no `(1,1)` pair.
Stage A's disclosure of four 8-tick runs at `(11,29)`, `(11,30)`, `(11,31)`,
`(3,7)` is retained. No result-dependent seed selection or exclusion occurred in
either stage.
