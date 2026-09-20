# Stage-B preregistration CANDIDATE

Status: **candidate for author review. NOT FROZEN. NOT AUTHORIZED TO EXECUTE.**

Protocol id (proposed): `EBU-STAGE-B-V1`. Executing Stage B is roadmap gate G6
and requires separate authorization; `LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md`
makes Stage-B execution a distinct gate that a completed Stage A does not open.

Basis: `STAGE_B_CONTINUOUS_FORCING_DECISION_PACKET.md`. Stage-A code, artifacts
and results are unchanged, and no parameter here was chosen to make Stage B
favourable.

## 1. Question

Under continuing conservative stochastic forcing, does the EBU capacity
affordability constraint change the recurrent deviation regime relative to a
matched physical-random control?

Stage A showed the constrained arm cycles perpetually rather than settling.
Stage B asks what that recurrent regime looks like when the system is driven
continuously, and whether any component of it is stationary.

## 2. Physical model — unchanged from Stage A

3 cells, `x* = (10,10,10)`, `sigma = (1,1,1)`, `M = 30`, complete directed
graph, quantum set `{1}`, `m_max = 2`, 21 candidate groups, `C_G = 0`,
`owner(a) = src(a)`, exact rational arithmetic at zero tolerance.

Carried over deliberately so Stage B differs from Stage A in forcing regime
only.

## 3. Forcing — the Stage-B treatment

Every tick `t >= 0` draws one conservative increment from the forcing stream:

- edge uniform over the 6 sorted edges (draw index 0);
- magnitude uniform over the frozen alphabet **{1/2, 1, 2}** (draw index 1);
- `u_t = s_t(e_p - e_q)`, `1^T u_t = 0` exactly.

**Admissibility rule (frozen): `NULL_FORCING`.** If the increment would drive
any cell negative, nothing is applied, the tick is recorded `NULL_FORCING`, and
the draw is consumed so the stream stays address-aligned.

Consequence, declared rather than hidden: arms are paired on **common raw
draws**, not on common applied forcing. Once states diverge the applied forcing
may differ, and the exposure difference is a registered diagnostic (section 7).

## 4. Arms

Unchanged: `ebu_affordability_random_actor` and the matched control
`physical_feasibility_random_actor`, which removes only the affordability gate
and keeps a signed shadow ledger for measurement. The control is a scientific
control.

Before execution, the Stage-A behavioural blindness property must be
re-asserted on the Stage-B configuration: changing every Gaussian scale changes
every EBU value and receipt but no control-arm choice or state.

## 5. Sample size, burn-in and horizon

| Item | Proposed |
|---|---|
| Replicates `N` | 64 paired |
| Burn-in `H_burn` | 512 ticks, discarded |
| Measurement window `H_measure` | 2048 ticks |
| Total ticks per run | 2560 |

No early stopping for any reason. `N`, `H_burn` and `H_measure` are not changed
after any result is seen.

Burn-in adequacy must be justified against the section 7 relaxation diagnostic
and frozen before execution; if the recommended 512 is not defensible, change it
now, not afterwards.

## 6. Exact invariants — zero tolerance

At every tick of every replicate:

1. `V(x_t) + sum_i B_i(t) = J_t`, with `J_t = sum_{k<t} D_ext,k` (no longer constant)
2. `sum_i x_i = 30`
3. `x_i >= 0`
4. `sum_a R_a = E_G` for the executed group
5. EBU arm only: `B_i >= 0`

Any nonzero residual is a foundation failure, halts interpretation, and is
preserved as incident evidence.

Note that `J_t` grows, so the Stage-A ceiling `V <= D` weakens to `V <= J_t`.
This is deliberate: it is what allows a primary endpoint that is not
structurally forced.

## 7. Primary endpoint and test

    A_r = ( sum_{t in window} V_r(t) ) / ( sum_{t in window} D_ext,r(t) )

time-averaged deviation normalised by cumulative injected deviation over the
measurement window, exact rational. **Bounded in neither arm**, which is the
specific correction to Stage A's design fault.

Primary contrast `Delta_r = A_r^EBU - A_r^CTRL`.

**Primary confirmatory test: exact two-sided paired sign test**, `alpha = 0.05`,
ties reported and excluded from the denominator, p-value computed exactly from
integer binomial counts.

**Meaningful-effect threshold, declared in advance:** a median `|Delta_r|`
below **0.05** is to be reported as statistically detectable but scientifically
negligible, regardless of p-value. This exists because Stage A's report had to
lean on effect magnitudes after its test proved structurally forced; Stage B
states the magnitude that matters before seeing data.

Power note recorded in advance: with `N = 64` the smallest attainable two-sided
exact p-value is `2/2^64`, and unanimity remains possible. A small p-value is
therefore not by itself a scientific result.

## 8. Registered descriptive diagnostics

No significance is attached to any of these and no multiplicity correction is
performed, because no confirmatory inference is drawn from them.

**Forcing exposure (mandatory, from section 3):** `NULL_FORCING` count per arm;
total applied injected deviation per arm; first tick at which applied forcing
diverged between arms.

**Stationarity, stated per object:** split-half comparison of median `V` across
the measurement window; the same for `sum B`, which is expected to drift;
`J` is excluded as a stationarity candidate by construction. Stationarity of
`V` is declared in advance **not** to imply stationarity of the accounts, and
the augmented `(x, B, J)` process is not claimed stationary.

**Relaxation:** autocorrelation of `V` at lags 1, 2, 4, 8, 16, 32, 64; smallest
lag with autocorrelation below `1/e`, censored if never; mean excursion length
above and below median `V`.

**Capacity concentration:** `max_i B_i / sum_i B_i` at window end; fraction of
measured ticks with some owner at zero capacity; per-owner time-averaged
balance.

**Deadlock:** tick count, longest consecutive run, fraction of replicates with
any deadlock. Stage A observed zero, so Stage B is the first real test of these
semantics.

**Trajectory classification:** Stage A's classes describe a transient and do
**not** transfer. Stage B classes must be defined over the recurrent regime and
frozen before execution; they are not yet written and are an open item.

## 9. Seeds

Not selected by hand. Derived mechanically from this document's own frozen
preregistration commit by the Stage-A rule with the protocol id changed:

    first 8 bytes big-endian of SHA256(ASCII("EBU-STAGE-B-V1|<C_pre_B>|rrr|STREAM"))

streams `FORCING` and `ACTOR`, `rrr` zero-padded to 3 digits, `|` = `0x7C`, no
trailing newline. Materialized only after that commit is immutable. No
result-dependent exclusion.

## 10. Failure handling, exclusion and stopping

No exclusion on scientific grounds. A foundation-integrity failure invalidates
the study and halts interpretation. All `N` replicates run the full horizon; no
interim inspection informs later replicates.

## 11. Non-claims

Stage B, whatever it shows, will not establish that EBU is stable, that the
capacity rule is correct attribution, that the reference is an optimum, or that
any real economy behaves this way. It concerns one synthetic 3-cell lossless
world under one declared forcing process.

Stationarity of `V`, if observed, is not stability of the mechanism and not
evidence about the accounts.

## 12. Open items requiring an author decision before freezing

1. **Stage-B trajectory classes** over the recurrent regime — not yet written.
2. **Burn-in adequacy** for `H_burn = 512`.
3. **Magnitude alphabet** `{1/2, 1, 2}`.
4. **`N = 64`** and the resulting attainable p-value floor.
5. **Meaningful-effect threshold** of 0.05 on median `|Delta_r|`.
6. Confirmation of the `NULL_FORCING` admissibility rule over the two recorded
   alternatives, since it is the one genuinely new scientific choice Stage B
   introduces.

Items 1 and 6 are load-bearing: they change the measured process. The rest set
cost and sensitivity.
