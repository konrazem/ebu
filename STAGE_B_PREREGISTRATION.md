# Stage-B registered preregistration (FROZEN except seeds)

Protocol id: `EBU-STAGE-B-V1`
Status: **FROZEN.** Every scientific decision is fixed here. Only the concrete
seed values are left unmaterialized; they are derived mechanically from this
document's own commit SHA (section 14).

Supersedes `STAGE_B_PREREGISTRATION_CANDIDATE.md` and the parts of
`STAGE_B_CONTINUOUS_FORCING_DECISION_PACKET.md` it revises; both are retained as
the review record. Where they differ, this document governs.

Stage-A artifacts, results and preregistration are untouched and immutable.
Stage A's observed result stands as reported: exact integrity, no convergence,
`REPEATED_CYCLING` in 128/128, zero `REACHED_AND_STAYED`, and a primary
comparison that was structurally biased because EBU accounting guaranteed
`V <= D_shock`.

**The mechanism is unchanged.** No capacity expiry, decay, demurrage, taxation,
cap, redistribution, borrowing, pooling, credit line beyond nonnegativity,
actor intelligence, EBU-maximizing choice or mean reversion is added. Stage B
tests the present mechanism.

## 1. Question

Under persistent conservative external disturbance:

1. What recurrent physical regime emerges?
2. How does EBU affordability alter that regime relative to the control?
3. **Does accumulated capacity progressively weaken affordability itself?**

Convergence is not assumed. Stationarity of the joint state/account process is
not assumed.

## 2. Pre-execution theoretical observation (drives the falsification target)

For the quadratic model,

    D_ext = V(x + u) - V(x) = mu(x)^T u + (1/2) u^T H u.

The curvature term is nonnegative, so even a zero-mean physical disturbance law
can inject positive potential on average. With the frozen `q0 = 1` and
`sigma = 1` that term equals exactly **+1** on every applied forcing event, so

    D_ext = mu(x)^T u + 1.

Verified before execution: at `x = x*` where `mu = 0`, every one of the six
edges gives `D_ext = 1` exactly.

Since `V_t + sum_i B_i(t) = J_t` and physical conservation confines `x` to a
compact simplex, `V` is bounded. Therefore if `J_t -> infinity` then
`sum_i B_i(t) -> infinity`.

**Registered falsification target:** capacity grows secularly, affordability
rejection falls over time, and the EBU arm becomes progressively similar to the
unconstrained control. Stage B tests this. Capacity decay is deliberately
**not** added to prevent it.

## 3. Frozen physical model — unchanged from Stage A

| Item | Frozen value |
|---|---|
| Potential family | `EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1` |
| Cells `n` | 3 |
| Reference `x*` | (10, 10, 10) exact |
| Scales `sigma` | (1, 1, 1) exact |
| Declared mass `M` | 30 exact |
| Initial state `x_0` | `x*`, so `V_0 = 0`, `B_i(0) = 0`, `J_0 = 0` |
| Topology | complete directed graph, 6 edges |
| Transfer quantum set | {1} exact |
| Max group size `m_max` | 2 |
| Candidate groups | 21, exhaustive deterministic |
| Process burden `C_G` | 0 |
| Ownership | `owner(a) = src(a)` |
| Event profile | `EBU-GAUSSIAN-EVENT-PROFILE-v1` |
| Arithmetic | exact rational, tolerance 0 |

## 4. Frozen forcing process

External forcing acts at **every** tick `t = 0 .. H-1`.

- **Amplitude is fixed, not random**: `q_ext = q0 = 1`, the smallest — and only
  — declared physical transfer quantum of the accepted world. No multi-amplitude
  alphabet is used; forcing-intensity variation is separate future work.
- **Randomness selects location and orientation only**: the edge is drawn
  uniform over the 6 canonically sorted directed edges from the forcing stream
  at `(tick = t, event_index = 0, draw_index = 0)`.
- The raw proposal is `u_t = q0 (e_dst - e_src)`, satisfying `1^T u_t = 0`
  exactly.

The raw draw depends only on the forcing seed and the tick, so **both arms
receive the identical raw environmental process**.

### 4.1 NULL_FORCING rule (confirmed)

Evaluated **per arm independently** against that arm's own current state:

- if the raw proposal is physically admissible (`x_src >= q0`), apply it exactly;
- otherwise apply zero physical forcing and record `NULL_FORCING`.

There is **no** resampling, clipping, reversal, edge substitution or magnitude
change. The draw is consumed either way so the stream stays address-aligned.

Consequence, declared rather than hidden: arms are paired on the **same raw
environmental process**, not necessarily on the same applied physical
increment. This is intentional. `NULL_FORCING` frequency is itself an
outcome/mechanism diagnostic.

Recorded per arm per tick: raw proposal, applied forcing, `NULL_FORCING`
indicator, `D_ext`, positive injection and negative relief.

## 5. Frozen horizon and windows

| Item | Frozen value |
|---|---|
| Total horizon `H` | **8192** ticks |
| Burn-in `B` | **2048** ticks, discarded |
| Analysis window | `t = 2049 .. 8192` |
| Window length `T` | **6144** |
| Blocks | exactly three consecutive blocks of 2048 ticks |

Burn-in is **not** moved or extended after results are inspected. If
block-to-block drift remains substantial the report states
**NO EVIDENCE OF LATE-WINDOW STATIONARITY**; it does not re-cut the window.

## 6. Frozen common physical normalization

`V` is maximised on the compact simplex `{x >= 0, sum_i x_i = M}` at a vertex,
because `V` is convex there. Evaluating the vertices `x = M e_k`:

    V_max = max_k (1/2) sum_i ((M*1[i=k] - x*_i)/sigma_i)^2

which for this world equals **exactly 300** at every vertex. Verified before
execution and not exceeded by 20,000 random interior probes.

This denominator is **identical in both arms and independent of treatment**. It
replaces any arm-specific cumulative-injection normalization, which would be
post-treatment because `NULL_FORCING` can differ by arm.

## 7. Frozen primary endpoint

For each arm of each replicate:

    L_r = (1/T) * sum_{t=B+1}^{H} V_r(t) / V_max

so `0 <= L_r <= 1` in **both** arms, from common physical state constraints
alone. No EBU-only structural bound determines the ordering, which is the
specific correction to Stage A's design fault.

Primary paired difference:

    Delta_r = L_r^EBU - L_r^CTRL

Negative means lower time-averaged physical deviation under EBU affordability;
positive means higher.

## 8. Frozen replicate count

**N = 64** paired replicates. Not altered after execution begins. No early
stopping for any reason, including significance reached or significance
appearing impossible.

## 9. Frozen primary statistical plan

- Report all 64 paired `Delta_r`, counts negative / positive / tied, paired
  median, paired mean, and the empirical distribution.
- **Primary confirmatory test: exact two-sided paired sign test** for a zero
  directional median, ties excluded from the denominator, p-value computed
  exactly from integer binomial counts. `alpha = 0.05` is used **only** as the
  inferential significance level.
- **Distribution-free sign-based confidence interval** for the paired median:
  with the `Delta_r` sorted ascending, the interval is
  `[Delta_(k+1), Delta_(N-k)]` where `k` is the largest integer with
  `P(Bin(N, 1/2) <= k) <= alpha/2`, computed exactly. If no such `k >= 0`
  exists the interval is reported as the full order-statistic range.

## 10. Frozen practical-effect threshold

    delta_meaningful = 0.05

on the common `V/V_max` scale: five percentage points of the physically
available deviation range. This is an **effect-magnitude interpretation
threshold, not the statistical alpha level**, and it is not combined into any
weighted score. A statistically significant `|median Delta_r| < 0.05` is
reported as detectable but not scientifically large.

## 11. Frozen descriptive diagnostics

No confirmatory inference is drawn from any of these, and no multiplicity
correction is performed because none is needed.

### 11.1 External-exposure (per arm, per replicate)

`G+_t = sum_{s<=t} max(D_ext,s, 0)`, `G-_t = sum_{s<=t} max(-D_ext,s, 0)`,
signed `J_t`; raw forcing count, applied forcing count, `NULL_FORCING` count
and rate. These are treatment-affected and are **never** used as the primary
normalization.

### 11.2 Capacity drift (central)

`B_tot(t) = sum_i B_i(t)`. Per block: mean `B_tot`, ending `B_tot`, blockwise
growth `Delta B_tot / Delta t`, per-cell distribution, and concentration
`max_i B_i / sum_i B_i` (defined as 0 when `sum_i B_i = 0`). `B` is **not**
assumed stationary.

### 11.3 Affordability-constraint persistence (central)

Per tick: physically feasible group count, affordable group count, and the
number of physically feasible groups rejected on capacity grounds. Per block:

    rho_reject = (# feasible groups rejected by affordability) / (# feasible groups)

**Zero-denominator convention, frozen:** if a tick has zero feasible groups,
`rho_reject` is undefined for that tick, is excluded from the block aggregate,
and the count of such ticks is reported. (With `sum_i x_i = 30` some cell always
holds at least 10, so at least one singleton is always feasible; the convention
is registered for completeness.)

The report states descriptively whether `rho_reject` declines across blocks as
capacity accumulates.

For the control arm the same counts are computed against its signed shadow
ledger as a **counterfactual measurement only**; they never affect control
behaviour.

### 11.4 Behavioural convergence toward control

`Delta^(1)`, `Delta^(2)`, `Delta^(3)`: the paired difference computed separately
within each 2048-tick block. Reported as increasing, similar, or decreasing
toward zero. **No new significance tests are created for these.**

### 11.5 Physical regime (per arm, per block)

Mean, variance, median and upper quantiles (0.9, 0.99) of `V/V_max`; boundary
occupancy (fraction of ticks with `min_i x_i = 0`); exact equilibrium occupancy
(fraction with `V = 0`); deadlock fraction; no-execution fraction;
`NULL_FORCING` fraction.

**Autocorrelation, estimator frozen before any result inspection:** for each
block, `r_k = sum_t (V_t - Vbar)(V_{t+k} - Vbar) / sum_t (V_t - Vbar)^2` at lags
`k in {1, 2, 4, 8, 16, 32, 64, 128, 256}`, computed in float64 from the exact
rational series (a descriptive statistic where exact rationals are
impractical; every primary quantity stays exact). Relaxation proxy: the
smallest frozen lag with `r_k < 1/e`, censored if none. If the variance
denominator is zero, all `r_k` are reported as undefined.

The process is **not** called stationary merely because these look flat.

## 12. No load-bearing trajectory classification

Stage-A transient trajectory classes are **not** carried into Stage B and no
named trajectory class is a preregistered inferential outcome. Descriptive
labels may be written after analysis only if clearly marked descriptive.

## 13. Frozen exact invariants — zero tolerance

Every tick of every replicate:

1. `V_t + sum_i B_i(t) = J_t` (EBU arm, zero-initialized)
2. `sum_i x_i = 30`
3. `x_i >= 0`
4. `sum_a R_a = E_G` for the executed group
5. EBU arm only: `B_i >= 0`

The control arm satisfies 2, 3, 4 and the signed analogue of 1. Any nonzero
residual invalidates the run as a foundation/software incident and halts
scientific interpretation.

## 14. Frozen seed-derivation rule (materialized only after this commit)

Seeds are not selected by hand. For replicate `r = 0..63` and stream
`S in {FORCING, ACTOR}`, the seed is the first 8 bytes, big-endian unsigned, of

    SHA256( ASCII( "EBU-STAGE-B-V1" | C_pre_B | rrr | S ) )

with `|` the single ASCII byte `0x7C`, `C_pre_B` the 40-character lowercase hex
SHA-1 of **this document's preregistration commit**, `rrr` the replicate index
zero-padded to exactly 3 digits, and no trailing newline. The same derived pair
is used for both arms. No result-dependent inclusion or exclusion.

## 15. Frozen stationarity stance

Physical-state recurrence and account-state stationarity are reported
separately. The joint `(x, B)` process is **not** required to possess a
stationary distribution. If physical variables stabilise while `B` grows, the
report says exactly that.

## 16. Frozen control arm

Physical feasibility plus uniform random choice, without EBU affordability.
Identical raw forcing draws, topology, candidate generator, physical
feasibility and actor RNG protocol. Control behaviour remains EBU-blind; `EBU`
and `V` are computed offline for measurement only. The control is a scientific
control, not a rival controller.

## 17. Frozen failure handling, exclusion and stopping

No exclusion on scientific grounds. A foundation-integrity failure invalidates
the study and halts interpretation, preserved as incident evidence. All 64
replicates run the full 8192-tick horizon; no interim inspection informs later
replicates.

## 18. Non-claims

Stage B will not establish that EBU is stable, that the capacity rule is
correct causal or ethical attribution, that the reference is an optimum, or
that any real economy behaves this way. It concerns one synthetic 3-cell
lossless world under one declared forcing process at one fixed amplitude.

Stationarity of `V`, if observed, is not stability of the mechanism and says
nothing about the accounts. A finding of secular capacity growth is evidence
about the present mechanism and does **not** authorize inserting a new one.
