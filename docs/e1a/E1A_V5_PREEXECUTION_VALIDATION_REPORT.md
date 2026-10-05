# E1a v5 — candidate pre-execution implementation and validation report

Report date: 2026-10-06. Scientific stage: **V**, implementation and synthetic
pre-execution validation, report only.

```text
STATUS:                   NON-CONTROLLING CANDIDATE
PROCEDURE VERSION:        2  (version 1 repaired before any validation outcome existed)
POLICY VERSION:           E1A-T11a-RF-v1
V RELEASE VERDICT:        NON-RELEASE
REASON:                   FULL V VALIDATION NOT COMPLETED - computationally infeasible
                          in this environment, by a measured factor of about 1.4e5
                          core-hours against the available budget
W-STAGE:                  BLOCKED
E1a-v4:                   UNTOUCHED - identities, contracts, plan and seal byte-identical
SCIENTIFIC AUTHORITY:     UNCHANGED
BOOK 1:                   UNCHANGED
REAL PHYSICAL DATA:       NOT USED
REAL CALIBRATION DATA:    NOT USED
OFFICIAL CAMPAIGN:        NOT RUN
REAL OPTICAL-TRAP EXPT:   NOT RUN
EXECUTION AUTHORISED:     FALSE
PUSH:                     NO
```

## 1. Executive result

**The candidate procedure is implemented completely and its deterministic
validation passes in full, but the stochastic validation campaign the T-stage
requires cannot be run in this environment, so the verdict is NON-RELEASE.**

Three things are worth the reader's attention, in descending order of
importance.

**First, the implementation work found three real defects in its own
estimator, one of them severe.** All three appear only at the physical SI
scale of the experiment; none is an algebra error, and the 249-check algebraic
suite passed throughout while the estimator was returning `log beta = +1.355`
against a true `0`. The severe one was a convergence test written as
`max_abs(P_next - P) <= tol * max(1.0, max_abs(P_next))`. Latent covariances
here are of order `1e-17 m^2`, so the `max(1.0, .)` floor silently converted a
relative tolerance into an absolute one that is satisfied at the first step.
The Kalman gain froze at its unconverged first value for the whole record, and
the quantity being maximised was therefore not the likelihood of the declared
model. Section 5 gives the full account. These were repaired, the procedure was
re-frozen as version 2, and eleven regression checks were added and confirmed
to fail when the defect is reintroduced.

**Second, the full campaign is infeasible here by a wide and measured margin.**
The environment has no numerical library available -- no NumPy, no SciPy -- so
every linear-algebra and special-function primitive is pure Python. Measured at
the repaired procedure, one record at the required information target needs
`2.72e6` frames and about `1.25` hours, a complete eight-record experiment
about `10` hours, and the preregistered campaign about **`1.9e5` core-hours**,
roughly `1.5` years on the 14 cores available. The authorising brief
anticipates exactly this case and directs that replicate counts must not be
quietly reduced: implement completely, run the deterministic validation, run a
clearly labelled engineering smoke sample, and report
`FULL V VALIDATION NOT COMPLETED - NON-RELEASE`. That is what was done.

**Third, the continuous nuisance-domain coverage the T-stage requires was not
established, and that is an independent bar to release.** T-stage 20.2 is
explicit that a finite grid cannot establish a continuous-domain supremum and
that V must supply a proved least-favourable configuration, a certified
monotonicity argument, a rigorous enclosure, or a Berger-Boos construction.
None of those is supplied here. Even with unlimited computation, the procedure
would not qualify on that ground alone.

Two further results are reported as findings rather than failures. The
information actually available per frame at the design point is `0.150`, which
fixes the required record at `2.72e6` frames. And at the T-stage exposure ceiling
`t_exp = 0.1 tau_fast`, exposure averaging alone contributes an effective
noise-to-signal ratio of `0.0683`, before any detector noise; this is
consistent with T.23's own warning that the instantaneous-localisation
shortcut understates the penalty for an exposure-averaged state-space fit, and
it is quantified here.

Nothing in this report adopts the candidate, modifies authority, or authorises
physical data collection. W-stage remains blocked.

## 2. Scope, provenance and boundaries

| Item | Verified value |
|---|---|
| Repository | `/Users/konrad.grzyb/code/ebu` |
| Branch | `codex/book-one-continuity` |
| Starting HEAD | `c3f64361be74f1ade30856f528c0987719bb7947` |
| Upstream | none configured; nothing pushed |
| Authorised scope | V-stage pre-execution implementation and synthetic validation only |

Cleared inputs, all verified as ancestors of the starting HEAD:

| Input | Commit |
|---|---|
| T base design | `ebcf2641fa2d8fe4ab95fef011e96fe53feeadc6` |
| U axial repair | `097aec81bcfe420bb9e25d0152cd8b4a08f69fde` |
| T11a amendment | `fb977f425a25d3252fdcfb510b767448aa839fe9` |
| U completion | `c3f64361be74f1ade30856f528c0987719bb7947` |

Controlling identities, recomputed at the end of this work and **unchanged**:

| Object | SHA-256 |
|---|---|
| Frozen physical foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Working theory baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| T-stage design | `10ddfdceb90454a87cd83a7868c65a1e1b7a7147cc4e8360faf70225ba6d4519` |
| U-stage specification | `af66f3fe640c25b5bf0bc11e61f3b77e944c70f2e4a2a040841b65a12d4b8d0a` |
| E1a-v4 design contract | `d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4` |
| E1a-v4 validation plan | `fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4` |
| E1a-v4 seed map | `c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af` |
| E1a-v4 execution seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` |

`git diff` over `e1a_v4/`, every `docs/e1a/E1A_V4_*` and `e1a_v4_*` path,
`books/`, `docs/physical_foundation/` and `docs/theory/` is **empty** across the
whole V-stage work. The v4 seal remains `PRE_DRIVER` with
`execution_authorised: false`, `random_draws: 0` and `trajectories: 0`. No
`results/e1a_v5*` output exists: no official campaign was created.

The baseline section 14.3 sign defect is **not** repaired here and remains owed
before W-stage authority freeze. All new code uses the ordinary post-minus-pre
convention, and the ambiguous bare symbol `Delta J` appears nowhere in the
package.

## 3. Implementation

A new isolated package `e1a_v5/` holds the candidate. Nothing in `e1a_v4` is
read, imported, modified or reused, and no shared utility was extracted.

| Layer | Module | Content |
|---|---|---|
| numerical kernel | `numerics.py` | Cholesky solves, symmetric eigendecomposition with a certified `1e-10` relative backward-error ceiling, symmetric matrix log and square root, generalised eigenvalues by symmetric whitening, scaling-and-squaring `expm`, Van Loan blocks, exact Clopper-Pearson through the regularised incomplete beta |
| A, unit safety | `units.py`, `packets.py` | canonical SI at the boundary; typed packets with six provenance kinds; synthetic-only construction is enforced in `__post_init__` |
| B, Branch-A | `branch_a.py` | the old-F2 rule separately on `eta`, `a`, `T`, then separately on derived `Gamma`, `gamma`, `tau`, `H` |
| C, axial | `reduction.py` | Schur complement, the (U.A10) Jacobian, covariance propagation, nonlinear remainder, (U.A13) diagnostics |
| D, observation | `observation.py` | the T.17 detector model with exact shutter integration by state augmentation |
| E, generator | `generate.py`, `rng.py` | synthetic latent and observation generation on an independent formula path |
| F, likelihood | `likelihood.py`, `estimate.py`, `optimize.py` | the exact T.6 likelihood through an innovations recursion, the frozen optimiser, the profile standard error |
| G, confidence | `confidence.py` | strict equivalence intervals, calibration and bias qualification |
| H and I, gates | `gates.py` | T4 geometry and centre, four-quarter stationarity, the T.10 current gate |
| J, diagnostics | `diagnostics.py` | the frozen four-component family |
| K, realization | `realization.py` | policy `E1A-T11a-RF-v1` |
| L, verdict | `verdict.py` | the T section 21 conjunction and five classifications |
| M, identity | `identity.py`, `seeds.py` | candidate procedure identities and the five disjoint seed families |
| N and O | `validation/` | plan, case list, harness, runner |

### 3.1 Choices worth recording

**The likelihood carries the correlation the shutter creates.** Exposure
averaging puts the same Brownian increments into both the transition noise and
the measurement noise, so `Cov(n_i, m_i)` is not zero. The recursion uses the
correlated-noise predictor form with `K_i = (F P_i C^T + S) S_i^{-1}`. A filter
that drops that term is not this likelihood, and T-stage 8.2 says so
explicitly. Setting `t_exp = 0` reduces the construction exactly to the
instantaneous case, with `C = P`, `R_eff = R_obs` and zero cross-covariance;
that reduction is asserted in the suite.

**Currents are representable by construction.** `A Sigma` is split as `D + Q`
with `D` symmetric positive definite and `Q` antisymmetric, so
`A = (D + Q) Sigma^{-1}` and `L L^T = 2 D` is positive definite for every
`omega`. `A Sigma = Sigma A^T` is deliberately never imposed in the density
fit, and in these coordinates the reversibility statistic is exactly
`S = Sigma^{-1/2} D Sigma^{-1/2}`, `Omega = Sigma^{-1/2} Q Sigma^{-1/2}`.

**`K_eff` is used everywhere; `K_qq` never is.** The axial coupling control
quantifies what the substitution would cost: at a coupling fraction of `0.30`
the axial ratio is `r = 0.5625`, and using the plane block would produce
`log beta_plane = -0.4964` and `G_plane = 0.4133` -- respectively about ten
times the `log 1.05` absolute margin and eight times the shape margin.

**The generator does not reuse the estimator's formulas.** The estimator takes
its exposure blocks from Van Loan's block-exponential identity; the generator
takes the same blocks from Gauss-Legendre quadrature of the analytic OU
covariance kernel, with the double integral split at `s = t` so the `|t - s|`
kink does not degrade the rule. The two agree to better than `1e-13` relative
across the exposure range, which makes their agreement evidence rather than a
tautology. Splitting at the diagonal mattered: integrating over the full square
left a relative error of `4.7e-8`, which would have masked a real discrepancy.

## 4. Freeze-before-validate record

| Step | Commit | Content |
|---|---|---|
| 1 | `4cd4609f04fc74077ce254d82a6c2a868248e310` | reference implementation, layers A-M |
| 2 | `7ef53d537cc3c46f28da96d600c63e210ebda865` | generator, seed architecture, harness, test suites |
| 3 | `0aea510aefe4067fceb4db6b11971f1538ddf4a2` | **procedure version 1 frozen** -- identities, thresholds, seed map, 51-case list |
| 4 | `29872b00b5e126ae32d8f061736869915a1b7ffa` | three defects repaired; **procedure version 2 frozen** |
| 5 | this commit | validation outcomes and this report |

The order is the point. Every validated quantity was fixed in a commit that
precedes the commit carrying any outcome, so no threshold in this report can
have been tuned using the validation that judges it.

Procedure version 1 was frozen and then repaired. **No validation outcome
existed under version 1**, so nothing required invalidation; version 1 was not
patched in place and continued, it was superseded, and fresh identities were
frozen before any validation ran.

Procedure version 2 identities:

| Object | SHA-256 |
|---|---|
| analysis procedure | `659d6e16321b545511915c7cdd3d0f68aab2978ee0bb83470e7e7dd3fd2240e3` |
| synthetic generator | `7f0859e02ee40a073471b74dd406913252c95043dff0f379a3ffd92164f9a83e` |
| validation procedure | `c53761d760cedfff1d18906ab6d744ba00479433b019301d2ae3c039222e6196` |
| packet schema | `576ebed583fb8c5399efff493df3b96c57aa615c1be73c86fd03a95d70c1fe3b` |
| seed map | `ca903abf11b5cab40dd0b21ae3ff546506d399fe8a46ffb9a4e52485842930df` |

## 5. Defects found in the candidate implementation

All three were found by running the pipeline at the physical design point, not
by the algebraic suites, and all three are invisible in dimensionless fixtures.
This is itself a result: a 249-check algebraic suite can pass while the
estimator is wrong by forty standard errors.

### 5.1 Frozen Kalman gain (severe)

The Riccati convergence test read

```text
max_abs(P_next - P) <= RICCATI_TOL * max(1.0, max_abs(P_next))
```

Physical latent covariances are of order `1e-17 m^2`. The `max(1.0, .)` floor
therefore turns a relative tolerance of `1e-13` into an absolute one, which the
first step satisfies trivially. The filter declared steady state after one
frame and used that unconverged gain and innovation covariance for the entire
record. The quantity being maximised was not the likelihood of the declared
model.

The consequence was large, not marginal. At the design point the fit drove the
diffusion to `D_11 = 1.4e-27` against a true `4.9e-13` -- fourteen orders of
magnitude -- and reported `log beta = +1.355` against a true `0`, beating the
true parameters by `835` log-likelihood units. The degenerate limit it ran to
is `D -> 0`, a frozen latent state.

The test is now relative to the covariance's own scale. After repair, steady
state is reached by genuine convergence after four frames, the fit returns
`log beta = +0.053`, `D` is recovered to within `7.5` percent, and the fit
beats the truth by `2.27` -- about half the free-parameter count, which is what
overfitting should cost.

### 5.2 Optimiser coordinates not dimensionless

The optimiser worked on raw model parameters. Those mix a physical length of
order `1e-8 m` with logarithms of Cholesky entries of magnitude 14 to 40. A
single `5` percent relative initial step cannot serve both: on a logarithm of
magnitude 40 it is a factor-of-seven jump, which destroys the simplex. A
`Scaling` layer now maps dimensionless coordinates, all of order one and
measured against the frozen initialisation, onto model parameters.

### 5.3 Profile standard error swamped by optimiser noise

The profile curvature used a fixed `1e-3` step. The log likelihood is `O(N)`,
so the second difference was a difference of nearly equal large numbers: with
`ll ~ 1e5` the optimiser's own convergence noise was about `1e-4` while the
signal was about `6e-4`. The step is now chosen adaptively so the profile drop
is of order one, and objectives are offset so the relative tolerance acts on an
`O(1)` quantity. A profile that beats the incumbent is reported as "no unique
maximum established" rather than returning a fabricated standard error.

A fourth, smaller defect: a field-order error in `run_record` placed the
failure reason in the `evaluable` slot, so a refused record looked evaluable.

### 5.4 Regression coverage

Eleven checks were added for these. Reintroducing the Riccati defect alone
fails seven of them, including the steady-state convergence check, the
degenerate-`D` comparison, and the `log beta` recovery check. Suites now total
**260 checks, 0 failures**.

## 6. Computational feasibility: the measured basis for NON-RELEASE

### 6.1 Environment

The validation environment provides CPython 3.14 and **no numerical library**:
NumPy, SciPy, SymPy and mpmath are all absent. Every linear-algebra and
special-function primitive used here is therefore pure Python. 14 cores are
available.

### 6.2 Measured cost at the repaired procedure

Record wall time is linear in frame count. Measured at procedure version 2:

| Frames | Wall seconds | `log beta` | SE | Information per frame |
|---:|---:|---:|---:|---:|
| 1,500 | 9.9 | −0.04317 | 0.067983 | 0.14425 |
| 3,000 | 11.8 | +0.07476 | 0.045649 | 0.15996 |
| 6,000 | 17.2 | −0.00322 | 0.033840 | 0.14555 |

Least squares on those three points gives
`seconds = 7.20 + 1.648e-3 * N` per record.

**Information per frame at the design point is `0.150`**, stable across the
three frame counts, which confirms the expected linear accumulation. (An
earlier figure of `0.374` appears in the working notes; it was measured at a
different synthetic operating point before the section 5.1 repair and is not
comparable to this one. Only the `0.150` measured at the design point with the
repaired procedure is used here.) Meeting the fixed target `I_* = 408,164`
therefore needs

```text
N_required = 408164 / 0.14992 = 2.723e6 frames per record
```

which is `4,493` seconds, about `1.25` hours, per record, and about `10.0`
hours per complete eight-record experiment.

### 6.3 Required campaign against available budget

| Family | Cases | Replicates each | Core-hours |
|---|---:|---:|---:|
| calibration | 7 | 4,000 | 34,945 |
| false equivalence | 11 | 5,000 | 68,642 |
| diagnostic family | 3 | 5,000 | 18,720 |
| complete power | 3 | 2,000 × 8 records | 59,906 |
| negative controls | 27 | 200 | 6,739 |
| **total** | **51** | **107,808** | **188,952** |

That is about **`1.9e5` core-hours**, or `13,497` hours on the 14 available
cores: roughly **1.5 years** of continuous wall-clock computation. The gap is
not marginal and no permitted optimisation closes it. The speed-ups already
applied -- an unrolled steady-state inner recursion worth a measured 10x, and
deterministic parallel seed partitioning -- are included in the figures above.

Reducing replicate counts to fit is explicitly forbidden, and reducing them
silently would be worse. The brief's instruction for this situation is to
implement completely, run the deterministic validation, run a clearly labelled
engineering smoke sample, and report
`FULL V VALIDATION NOT COMPLETED - NON-RELEASE`.

## 7. Deterministic validation: complete and passing

These controls have exact expected outcomes and were run at full fidelity. All
nine pass.

| Case | Expected | Observed | Pass |
|---|---|---|:-:|
| `CTL-RF-TEMP-304` | `OUT_OF_SPEC` | `OUT_OF_SPEC`; retention `0.3068790100`, planning detection `0.0002274435852` | yes |
| `CTL-RF-STIFF-1021` | `OUT_OF_SPEC` | `OUT_OF_SPEC`; retention `0.0280111782`, planning detection `0.0005218639151` | yes |
| `CTL-RF-MODES` | `OUT_OF_SPEC` | `OUT_OF_SPEC` for modes `(1.9, 2.25)`, whose harmonic scalar `2.0602409639` lies inside the band | yes |
| `CTL-RF-ELLIPSE` | `OUT_OF_SPEC` | `OUT_OF_SPEC`; distance `0.458145365937` against `epsilon_2 = 0.05108256237659907` | yes |
| `CTL-RF-STRADDLE` | `UNRESOLVED` | `UNRESOLVED` | yes |
| `CTL-RF-VALID` | `VALID` (synthetic) | `VALID`, explicitly marked synthetic | yes |
| `CTL-AXIAL-COUPLE` | pipeline uses `H_eff`; `K_qq` bias quantified | `r = 0.5625`, `log beta_plane = -0.496437`, `G_plane = 0.413339` | yes |
| `CTL-AXIAL-MEMORY` | `TEMPORAL_MODEL_UNQUALIFIED` or linked axial refusal | axial refusal on `lateral temporal reduction qualified` | yes |
| `CTL-OPT-FAIL` | `COMPUTATION_NOT_EVALUABLE`; `beta` never fabricated | `OptimizerFailure` on NaN objective, inadmissible start and singular factorisation; budget exhaustion reported as non-converged | yes |

Every published T11a constant reproduces exactly: `c_T* = 0.06495789627477229`,
`h_90 = 0.03778351913824557`, `s_c = 0.00372827037646145`,
`log 2.1 = 0.7419373447293773`, `epsilon_2 = 0.05108256237659907`, the `L_2^*`
entries, the retention lower limit `0.05846210664729507`, and the lower-boundary
planning detection `1 - 4.30590784e-12`.

The algebraic suites cover the remainder: units failing closed on every named
confusion, Clopper-Pearson solved against the exact binomial tail identity, the
old-F2 rule including two negative primitives whose product is positive, Schur
invariance under axial reparametrisation, the (U.A10) Jacobian against finite
differences, the quadratic term that survives at `b = 0`, orthogonal invariance
of the ellipse metric including a reflection, the documented `G` and `r_irr`
examples, boundary equality failing equivalence, and the verdict conjunction.

**260 checks, 0 failures.**

## 8. Engineering smoke sample

> **ENGINEERING SMOKE SAMPLE - NOT A VALIDATION RESULT**
> 
> Run at **1500 frames** per record against a required **2,723,000**, with
> **100** size replicates against a required 5,000, **10** complete
> experiments against a required 2,000, and **12** control replicates.
> Every statistic below is therefore between two and three orders of
> magnitude short of its required precision, and **none of it supports or
> opposes release**. It is reported to show the pipeline runs end to end and
> to record what it actually does, not as evidence about operating
> characteristics. Total wall time 627 s on 13 workers.

### 8.1 Size family

| Case | Status | Replicates | Events | Point | CP upper | Required |
|---|---|---:|---:|---:|---:|---:|
| `SIZE-ABS-LO` | run | 100 | 0 | 0.0000 | 0.0295 | <= 0.025 |
| `SIZE-ABS-HI` | run | 100 | 0 | 0.0000 | 0.0295 | <= 0.025 |
| `SIZE-CON-LO` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-CON-HI` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-SHAPE-BD` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-CENTRE-BD` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-CURRENT-BD` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-NUIS-NOISE` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-NUIS-EXP` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-NUIS-COND` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |
| `SIZE-NUIS-CAL` | **NOT RUN** -- requires the multi-record contrast or gate-boundary driver | 0 | - | - | - | <= 0.025 |

### 8.2 Complete-power family

| Case | Replicates | Successes | Point | CP lower | Required |
|---|---:|---:|---:|---:|---:|
| `POWER-NOMINAL` | 10 | 0 | 0.0000 | 0.0000 | >= 0.90 |
| `POWER-CONDLIM` | 10 | 0 | 0.0000 | 0.0000 | >= 0.90 |
| `POWER-NOISEHI` | 10 | 0 | 0.0000 | 0.0000 | >= 0.90 |

Refusals and optimiser failures remain in the denominator, as required.

### 8.3 Diagnostic family

| Case | Status |
|---|---|
| `DIAG-NULL-NOM` | **NOT RUN** -- requires the joint familywise calibration of the diagnostic maximum, which needs the frozen null scales from the calibration family |
| `DIAG-NULL-EXP` | **NOT RUN** -- requires the joint familywise calibration of the diagnostic maximum, which needs the frozen null scales from the calibration family |
| `DIAG-NULL-COND` | **NOT RUN** -- requires the joint familywise calibration of the diagnostic maximum, which needs the frozen null scales from the calibration family |

### 8.4 Calibration family

| Case | Status |
|---|---|
| `CAL-SCALE-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |
| `CAL-CONTRAST-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |
| `CAL-SHAPE-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |
| `CAL-CENTRE-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |
| `CAL-STAT-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |
| `CAL-CURRENT-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |
| `CAL-DIAG-01` | **NOT RUN** -- finite-N calibration not performed; see section 10 |

### 8.5 Controls

| Case | Expectation | Observed |
|---|---|---|
| `CTL-BLIND-107` | recovered log beta matches after multiplying by c | support 0/12; abs fail 12, geom fail 10, centre fail 10, current fail 7, non-evaluable 0 ; false-support CP upper 0.221 ; blinded recovery max abs error 0.0853 |
| `CTL-BLIND-090` | recovered log beta matches after multiplying by c | support 0/12; abs fail 12, geom fail 8, centre fail 6, current fail 9, non-evaluable 0 ; false-support CP upper 0.221 ; blinded recovery max abs error 0.1126 |
| `CTL-COMMON-07` | cross-field contrasts may pass; absolute must fail | support 0/12; abs fail 12, geom fail 11, centre fail 9, current fail 10, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-FIELD-106` | false support bounded | **NOT RUN** |
| `CTL-FIELD-MIX` | false support bounded | **NOT RUN** |
| `CTL-FIELD-110` | false support bounded | **NOT RUN** |
| `CTL-HARD-025` | false support bounded | **NOT RUN** |
| `CTL-GEOM-TRACE` | scalar beta plausible; T4 geometry rejects | support 0/12; abs fail 12, geom fail 12, centre fail 11, current fail 10, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-GEOM-ROT` | geometry detects the rotation | support 0/12; abs fail 12, geom fail 12, centre fail 6, current fail 10, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-CURRENT` | density/geometry pass; current gate blocks support | support 0/12; abs fail 1, geom fail 1, centre fail 0, current fail 1, non-evaluable 11 ; false-support CP upper 0.950 |
| `CTL-ETA-T-COV` | coverage consequence detected | **NOT RUN** |
| `CTL-NOISE-HI` | diagnose, refuse or lose support | support 0/12; abs fail 12, geom fail 9, centre fail 5, current fail 11, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-NOISE-HEAVY` | diagnose, refuse or lose support | support 0/12; abs fail 12, geom fail 9, centre fail 11, current fail 11, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-NOISE-COLOR` | diagnose, refuse or lose support | support 0/12; abs fail 12, geom fail 11, centre fail 4, current fail 8, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-NOISE-STATE` | diagnose, refuse or lose support | support 0/12; abs fail 12, geom fail 9, centre fail 9, current fail 10, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-BLUR-MISMATCH` | diagnose, refuse or lose support | support 0/12; abs fail 12, geom fail 9, centre fail 7, current fail 10, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-DRIFT` | stationarity or diagnostics prevent full support | support 0/12; abs fail 12, geom fail 9, centre fail 12, current fail 11, non-evaluable 0 ; false-support CP upper 0.221 |
| `CTL-SELECTION` | invalid measurement or model, not a reconditioned pass | **NOT RUN** |
| `CTL-AXIAL-COUPLE` | pipeline uses H_eff; K_qq bias quantified | **deterministic, PASS** -- r=0.562500 log_beta_plane=-0.496437 G_plane=0.413339 |
| `CTL-AXIAL-MEMORY` | TEMPORAL_MODEL_UNQUALIFIED or model failure | **deterministic, PASS** -- ['lateral temporal reduction qualified'] |
| `CTL-RF-TEMP-304` | FIELD_REALIZATION_OUT_OF_SPEC | **deterministic, PASS** -- FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-STIFF-1021` | FIELD_REALIZATION_OUT_OF_SPEC | **deterministic, PASS** -- FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-MODES` | FIELD_REALIZATION_OUT_OF_SPEC | **deterministic, PASS** -- FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-ELLIPSE` | FIELD_REALIZATION_OUT_OF_SPEC | **deterministic, PASS** -- FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-STRADDLE` | FIELD_REALIZATION_UNRESOLVED | **deterministic, PASS** -- FIELD_REALIZATION_UNRESOLVED |
| `CTL-RF-VALID` | FIELD_REALIZATION_VALID (synthetic) | **deterministic, PASS** -- FIELD_REALIZATION_VALID |
| `CTL-OPT-FAIL` | COMPUTATION_NOT_EVALUABLE; beta never fabricated | **deterministic, PASS** -- ['NaN objective: OptimizerFailure', 'inadmissible start: OptimizerFailure', 'singular factorisation: Optimizer |

Across all 51 preregistered cases: **9 deterministic controls complete and
passing**, **17 stochastic cases exercised at smoke scale**, and the
remainder **NOT RUN** with the reason stated. No case was dropped silently.

### 8.6 How to read these numbers

Three readings would be wrong, and the smoke scale is the reason.

**The `0/10` complete-power results are not a power failure.** At 1,500 frames
the per-record standard error is about `0.068`, so a nominal interval
half-width is about `0.134` against an absolute margin of `0.0488`. No interval
can lie strictly inside the margin at this record length, whatever the truth
is. The required record is `2.72e6` frames, about 1,800 times longer, where the
standard error falls by roughly `42`. These runs show the eight-record pipeline
executes and that refusals stay in the denominator; they say nothing about
achieved power.

**The `0/100` false-equivalence results do not demonstrate size control.** Zero
events in 100 replicates gives a one-sided 95% Clopper-Pearson upper bound of
`0.0295`, which is **above** the required `0.025`. Even a perfect run at this
replicate count cannot meet the criterion: that is precisely why the T-stage
fixes 5,000, where the acceptance region is up to 106 events. The smoke result
is consistent with the requirement being unmet for lack of replicates, which is
what it is.

**The controls did not discriminate, and could not have.** Every stochastic
control shows `support 0/12` -- but so does the true benchmark at this record
length, for the reason just given. A control that rejects when the positive
case also rejects has demonstrated nothing. These rows record that each control
path runs, generates its intended departure, and reaches a verdict; they do not
show that any control detects what it is meant to detect. That demonstration
requires the full-length records.

One observation is substantive rather than scale-limited. `CTL-CURRENT`, with
`omega` driving a circulating current, returned **11 of 12 replicates
non-evaluable** against zero non-evaluable in every other control. The
estimator is failing to establish a unique maximum on exactly the configuration
the T-stage 12.2 counterexample identifies as the hard case for the
reversibility gate. Whether that is a real identifiability boundary of the free
fit or a remaining optimiser weakness is **not resolved here**, and it is
flagged as the first thing a future V attempt should investigate.

## 9. Uncovered nuisance domain

This is an independent bar to release and would remain so with unlimited
computation.

T-stage 20.2 states that the target is an upper envelope of the tail
probability over the **complete qualified nuisance domain**, that boundary-only
calibration is permitted only with a demonstrated monotonicity or
least-favourable-null argument, and that **a finite grid alone cannot establish
a continuous-domain supremum**. It names four acceptable routes: a proved
least-favourable configuration, certified monotonicity, a rigorous
enclosure or interpolation bound, or a Berger-Boos nuisance confidence set
whose noncoverage is added to the budget, capped at `0.001` per one-sided
procedure.

**None of the four is supplied by this work.** What exists is the
infrastructure for the fourth: the error budget is decomposed and carried
(`0.020` model tail, `0.001` auxiliary set, `0.0001` selection, leaving
`0.0039` for finite calibration and numerical envelope error), and the
realization layer evaluates its predicates over certified enclosures rather
than grids, refusing to return `VALID` for an enclosure whose certificate is
`unspecified` or `grid`. The argument that would justify boundary-only
calibration for the scale, shape, centre, stationarity and current procedures
is absent.

Specifically uncovered:

| Nuisance direction | Status |
|---|---|
| absolute and cross-field equivalence boundaries | only point configurations declared; no envelope argument |
| qualified calibration-uncertainty domain | not exercised; the synthetic auxiliary law is declared but its full covariance is not propagated into the fitted intervals |
| noise and exposure range | endpoints declared as cases; interior not covered by a certified bound |
| temporal nuisance range | not characterised |
| conditioning range up to `kappa_2 = 100` | endpoint declared; no monotonicity argument in conditioning |
| field geometry and centre nuisance | not characterised |
| shared covariance structures | implemented in the reduction layer; not validated end to end |

## 10. Release verdict

```text
V RELEASE VERDICT: NON-RELEASE
```

Release requires every mandatory validation requirement to pass. Three
independent requirements are not met:

1. **The required stochastic campaign was not run.** `1.9e5` core-hours are
   needed against a budget smaller by about five orders of magnitude. A partial
   validation cannot produce RELEASE, and the reduced-count run reported above
   is an engineering smoke sample, not a validation result.
2. **Finite-N critical values were not calibrated.** All intervals above use
   the normal starting value `1.959963985`. The T-stage ceiling
   `c_minus, c_plus <= 2.10` is therefore **not demonstrated**: no calibrated
   value exists to compare against it. Whether the ceiling can be met is
   unknown, not satisfied.
3. **Continuous nuisance-domain coverage is unproved**, by the standard the
   T-stage sets out and this work does not meet.

No threshold was weakened, no hard case was dropped, and no replicate count was
quietly reduced to reach a different answer.

## 11. What a future V attempt would need

In priority order, and none of it is authorised here:

1. **A numerical library.** NumPy alone would plausibly move the campaign from
   `1.9e5` core-hours to a few hundred, because the inner recursion is a dense
   small-matrix loop that vectorises across replicates rather than within a
   record. This is an environment change, not a procedure change: the
   statistical procedure must not be altered for speed.
2. **A nuisance-coverage argument**, which is mathematical work independent of
   computing budget. The Berger-Boos route is the one this implementation is
   already shaped for.
3. **Finite-N calibration of all seven critical quantities**, then an
   independent validation on disjoint streams, with the `2.10` ceiling checked
   against the calibrated values.
4. **The multi-record size driver.** The cross-field contrast and gate-boundary
   size cases are declared `NOT RUN` above rather than silently skipped: the
   current driver exercises one record, and those cases need the contrast and
   gate-boundary paths.
5. **Resolution of the `CTL-CURRENT` non-evaluability.** 11 of 12 replicates
   failed to establish a unique maximum under a circulating current, against
   zero failures in every other control. This sits exactly on the T-stage 12.2
   counterexample. It is unresolved here and should be investigated before any
   further validation effort is spent.

## 12. Stage boundary

W-stage is **BLOCKED**. This report adopts nothing, modifies no authority, and
authorises no physical data collection, no campaign, and no unblinding. The
candidate artifacts are marked `NON-CONTROLLING CANDIDATE` throughout.

The baseline section 14.3 sign defect remains **owed before W-stage authority
freeze**.

Two editorial items reported in the commissioning brief are recorded and not
repaired here: the malformed rendered `r != 0` in Book 1 chapter 33, and 17
diagram assets against 16 placed figures. Book 1 is unchanged.
