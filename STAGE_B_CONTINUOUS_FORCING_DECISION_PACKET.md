# Stage-B continuous-forcing decision packet

Status: **preparation only. Stage B is NOT authorized to execute by this
document.** It resolves the implementation-level choices a Stage-B
preregistration needs, reusing the Stage-A architecture unchanged wherever
possible.

Inputs: `STAGE_A_PREREGISTRATION.md`, `STAGE_A_REGISTERED_REPORT.md`,
`LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md` sections 7 and 8,
`LOCAL_GAUSSIAN_EBU_IMPLEMENTATION_ROADMAP.md` gates G5/G6.

No Stage-A code, artifact or result is modified. No parameter is chosen to make
Stage B favourable.

## 0. What Stage A did and did not settle

Settled: the mechanism is implementable at exact rational arithmetic with zero
residuals; the accounting identity holds tick by tick; replay is exact.

Not settled, and therefore Stage B's subject: whether anything about the
constrained process is *stationary*. Stage A found perpetual cycling
(`REPEATED_CYCLING` in 128/128) with no replicate settling at equilibrium, so
Stage B must be designed to characterise a recurrent regime rather than to
detect a return to rest.

Carried forward as a correction, not an amendment: Stage A's primary endpoint
was structurally bounded above in one arm only, which made its confirmatory
test nearly deterministic. Stage B must not repeat that.

## A. Forcing process

Continuous conservative stochastic forcing. At every tick `t >= 0` the forcing
stream draws one increment, in contrast to Stage A's single shock:

    u_t = s_t (e_{p_t} - e_{q_t}),   1^T u_t = 0 exactly.

Reuse `ForcingIncrement` and the existing forcing stream unchanged. The draw
address advances by tick, so the whole forcing path is a pure function of the
forcing seed.

## B. Rational forcing alphabet and distribution

Frozen finite rational alphabet, uniform over its elements, drawn with the
existing exact-residue sampler:

- edge: uniform over the 6 canonically sorted edges (draw index 0);
- magnitude: uniform over a frozen alphabet (draw index 1).

Recommended alphabet `{1/2, 1, 2}` rather than Stage A's `{2}`, so intensity
varies within a replicate and the design is not confounded by a single
magnitude. All values exact rationals; the G0 Exact Arithmetic Decision
carries over unchanged.

## C. Forcing intensity

Intensity is set by the magnitude alphabet and by forcing every tick. Expected
per-tick injected deviation is a declared consequence of the alphabet, not a
separately tuned knob. Do **not** tune intensity to produce a desired amount of
deadlock or recovery.

## D. Physical admissibility of forcing — the one genuinely new choice

Stage A could not hit this: from `x*` a single shock of 2 leaves every cell at
8. Under continuous forcing a cell can approach zero, so a drawn increment may
be physically inadmissible (`x_q - s < 0`).

**Recommended frozen rule: NULL_FORCING.** If the drawn increment would drive
any cell negative, apply nothing, record the tick with status `NULL_FORCING`,
and consume the draw anyway so the forcing stream stays address-aligned.

Rationale: it is deterministic, auditable, conserves mass trivially, and keeps
the raw draw sequence identical across arms. Its cost is that *applied* forcing
becomes state-dependent, so once the arms' states diverge they no longer
receive identical physical input.

This is exactly the distinction the programme reconciliation section 8 requires
be made explicit rather than papered over with "same seed". Therefore:

- Stage B pairs arms on **common raw draws**, not on common applied forcing;
- the **forcing exposure difference is a registered diagnostic**, reported per
  replicate: count of `NULL_FORCING` ticks per arm, total applied deviation
  injected per arm, and the first tick at which the arms' applied forcing
  diverged.

Recorded alternatives, not adopted: (i) redraw downward to the largest
admissible alphabet element, which biases the magnitude distribution toward
small values in exactly the states where dynamics matter most; (ii) rejection
resampling until admissible, which is unbounded and breaks address alignment;
(iii) clamping, which breaks exact conservation and is refused outright.

## E. Pairing and control

Unchanged from Stage A: arm A `ebu_affordability_random_actor`, arm B
`physical_feasibility_random_actor`, identical world, menu, feasibility,
canonical ordering, matched forcing seed and matched actor seed.

Arm B keeps the signed shadow ledger for measurement only. The Stage-A
behavioural blindness property — changing every Gaussian scale changes every
EBU value but no control choice — must be re-asserted in the Stage-B
conformance run before execution.

## F. Horizon and replicate count

Stage B needs a burn-in plus a measurement window, because the question is
about a recurrent regime rather than a transient.

Recommended: `H_burn = 512` discarded ticks, `H_measure = 2048` measured ticks,
`N = 64` paired replicates. Cost estimate from the measured Stage-A rate
(~1.1 s per 257-tick paired replicate): roughly
`64 * 2 * 2560 / 257 * 0.55 s` ≈ 6 minutes, so the horizon is affordable and
the constraint is scientific, not computational.

Burn-in length must be justified against the relaxation diagnostic in H, and
frozen before execution.

## G. Stationary-regime diagnostics

The reconciliation warns that physical observables may stabilise while `B` and
`J` drift, so stationarity must be stated per object:

- `x` and `V`: split-half comparison of the measurement window, reporting the
  difference in median `V` between first and second halves;
- `sum B`: same split-half test — expected to drift, and that is a finding;
- `J`: grows by construction under continuous forcing and is **not** a
  stationarity candidate;
- the augmented `(x, B, J)` process: explicitly **not** claimed stationary.

Declare in advance that stationarity of `V` does not imply stationarity of the
accounts.

## H. Autocorrelation and relaxation diagnostics

- Sample autocorrelation of `V(t)` over the measurement window at lags
  1, 2, 4, 8, 16, 32, 64, computed exactly where practical.
- Integrated relaxation proxy: smallest lag at which autocorrelation falls
  below `1/e`, censored if never.
- Mean excursion length above and below the median `V`.

These characterise the cycling Stage A found; they are descriptive.

## I. Capacity concentration

Stage A ended with median total capacity 3 of a possible 4 in the EBU arm, so
concentration is worth measuring under continuous drive:

- Gini-like concentration `max_i B_i / sum_i B_i` at the end of the measurement
  window;
- fraction of measured ticks in which some owner holds zero capacity;
- per-owner time-averaged balance.

A mechanism in which one cell accumulates all capacity while others are frozen
out is a scientifically important outcome and must be reportable.

## J. Deadlock under continuous drive

Stage A observed **zero** deadlock ticks, so Stage B is the first real test of
the deadlock semantics. Keep them unchanged: the empty group stays out of the
menu, no fallback is injected, `DEADLOCK` is recorded when `V > 0` and no
affordable nonempty group exists, `IDLE` when `V = 0`.

Register: deadlock tick count, longest consecutive deadlock run, and fraction
of replicates with any deadlock. A high deadlock rate is a finding, not a bug.

## K. Exact accounting

Unchanged and mandatory at zero tolerance. Under continuous forcing the
identity becomes

    V(x_t) + sum_i B_i(t) = J_t,    J_t = sum_{k<t} D_ext,k

with `J_t` no longer constant. Because `J_t` grows, the Stage-A structural
ceiling `V <= D` weakens to `V <= J_t`, which is exactly why Stage B can carry a
primary endpoint that is not forced.

## L. Statistical plan

One primary confirmatory test only, as in Stage A.

Recommended primary endpoint: **time-averaged deviation over the measurement
window normalised by cumulative injected deviation**,

    A_r = (sum_{t in window} V_r(t)) / (sum_{t in window} D_ext,r(t))

which is bounded in neither arm and therefore does not repeat Stage A's design
fault.

Primary test: exact two-sided paired sign test on `Delta_r = A_r^EBU -
A_r^CTRL`, `alpha = 0.05`, ties excluded from the denominator, p-value computed
exactly from integer binomial counts. Everything in G, H, I and J is
descriptive with no significance attached.

Before freezing, a power consideration must be recorded: with `N = 64`, the
smallest attainable two-sided exact p-value is `2/2^64`, and unanimity is again
possible. The preregistration must state in advance what effect magnitude would
be considered scientifically meaningful, so the report is not left leaning on a
p-value alone as Stage A's was.

## M. What is deliberately NOT decided here

Burn-in adequacy, the exact magnitude alphabet, `N`, and the meaningful-effect
threshold are proposals. They belong in `STAGE_B_PREREGISTRATION_CANDIDATE.md`
and must be frozen, with seeds derived mechanically from that document's own
commit, before any Stage-B replicate runs.
