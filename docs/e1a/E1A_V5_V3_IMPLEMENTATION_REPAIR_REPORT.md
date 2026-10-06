# E1a v5 — procedure version 3 implementation repair report

Report date: 2026-10-06. Scientific stage: **V**, bounded implementation
repair, report only.

```text
STATUS:                   NON-CONTROLLING CANDIDATE
PROCEDURE VERSION:        3
SUPERSEDES:               v1 (superseded), v2 (AUDIT FAILED)
V3 CORE PROCEDURE:        REPAIRED AND FROZEN - INDEPENDENT AUDIT REQUIRED
V RELEASE:                NON-RELEASE - VALIDATION NOT YET COMPLETE
W-STAGE:                  BLOCKED
AUTHORITY MODIFIED:       NO
E1a-v4:                   UNTOUCHED
T / U SOURCES:            UNTOUCHED
BOOK 1:                   UNCHANGED
REAL DATA:                NOT USED
PHYSICAL CALIBRATION:     NOT USED
FULL CAMPAIGN:            NOT RUN
EXECUTION AUTHORISED:     FALSE
PUSH:                     NO
```

## 1. Executive result

**All six audited defects are repaired, the `C_phi` path is completed end to
end, and the procedure is frozen as version 3 for independent audit.** No
finite-N campaign was run and none of the standing release blockers is
claimed solved.

Two of the repairs changed what the procedure *reports*, not merely how it is
written, and both corrections make the answer worse rather than better. That
is the point.

**The complete-power runner was counting successes it had not earned.** It
rebuilt its own predicate from four per-record gates and never consulted the
six cross-field contrasts, stationarity, the diagnostic family, the
realized-field statuses or packet validity — and never called the verdict
engine at all. There is now one judgement path. Running it at the design point
reports `0/8` passes on every gate with `INCOMPLETE_INPUT`, because **no
finite-N calibrated upper limit exists yet**. The old code compared raw
statistics against tolerances and would have counted some of those as passes.

**The circulating-current control was dimensionally meaningless.** A literal
`omega = 0.05` was supplied as a physical rate against a relaxation rate of
order `1e4 s^-1`, producing `r_irr ~ 1e11` and a bandwidth product of
`~1.5e10` against a ceiling of `0.2`. V2's report recorded 11 of 12 replicates
as non-evaluable on that control and flagged the cause as unresolved. It is now
resolved: the control was not probing a 5% current, it was probing a process
rotating ten orders of magnitude faster than the sampling could represent. The
construction is inverted from the dimensionless definition and reproduces
`r_irr` to nine decimals at a bandwidth of `0.150`.

The remaining four — a standard error published from a non-converged profile,
a frozen diagnostic component silently defaulting to zero, a validation
identity blind to its own result-counting code, and axial qualification that
treated absent evidence as qualified — are all repaired fail-closed.

A systematic SI-scale audit of the whole package found **two further material
defects the auditor had not listed**: `eigh2`'s symmetry check and `lu_solve`'s
pivot floor were both absolute, so a grossly asymmetric or genuinely singular
matrix at `1e-29` — the scale of the exposure covariance blocks — passed as
symmetric and non-singular.

Suites now total **430 checks, 0 failures**.

## 2. Coordinates

| Item | Value |
|---|---|
| Repair starting commit | `2e39ae682dd6d67561beaa5755b16546748d2f79` |
| V3 implementation repair | `b31d86d9c809ff42baeafc6a198cdf9ea5e70c5b` |
| V3 freeze | `ab668e97ec1c762d92301de3fca024be53baba52` |
| Branch | `codex/book-one-continuity`, no upstream, nothing pushed |

Procedure version 3 identities:

| Object | SHA-256 |
|---|---|
| analysis procedure | `feb287294cec4bbf85d430336a6a6b9a63dbac049b0c27ebaf8b011cff038078` |
| synthetic generator | `82f75d515d1cdb630429f339af19241f304c1a31d4fa81cca07e855efc882199` |
| validation procedure | `0b6ea6b7f230846938c42667fc42cb3510ba1fc2264f02120201183c6e76aac0` |
| packet schema | `a7db3c424bdb906a22a605169350d45802c3af56ef5e936df91287150cca3eb3` |
| seed map | `37785e764fb5b03613a9ad3d54fda80f39b343370a8ecaaeb7ad15b258990654` |
| gate semantics | `ffd6247e4fb0acb5af5c5d400c299b255bd84035e52178a4c6d9f5403f99f147` |

## 3. Defect 1 — complete-power counting

**Found.** `run_power_case` iterated the eight records and tested only the
absolute interval, geometry, centre and `r_irr`, breaking out early on the
first failure. It never checked the six within-block contrasts, stationarity,
the diagnostic family, the realized-field statuses, Branch-A validity or
observation validity, and it never invoked `decide`.

**Repaired.** A new module `e1a_v5/pipeline.py` holds the single authoritative
path:

```text
complete_pipeline_result(records, contrasts, diagnostic_rejected)
    -> verdict.decide(tally, reasons, not_evaluable)
    -> counts_as_complete_success  iff  SUPPORTED_WITHIN_DECLARED_TOLERANCES
```

`run_power_case` now assembles typed `RecordResultV3` objects and delegates.
It does not contain a success test of its own.

**Missing-result semantics.** Every required field is `None` when not
established, and `None`, `NaN`, non-finite, unevaluated, optimiser-failed and
qualification-unavailable each prevent success and are classified under T/U
semantics (`INCOMPLETE_INPUT`, `COMPUTATION_NOT_EVALUABLE`,
`INVALID_MEASUREMENT_OR_MODEL`). Nothing defaults to a pass.

**Regressions.** Eighteen mutations of a fully valid synthetic experiment —
each required condition removed, set to `None`, set to `NaN`, set exactly at
its tolerance, or made non-evaluable — all fail complete-success counting, and
one fully populated valid result does count. An unevaluated diagnostic family
yields `COMPUTATION_NOT_EVALUABLE` rather than a pass.

**Observed effect.** One complete experiment at the design point now returns
`INVALID_MEASUREMENT_OR_MODEL` with
`absolute_pass=0, shape_pass=0, centre_pass=0, stationarity_pass=0, current_pass=0`
and reason codes `INCOMPLETE_INPUT` and `OBSERVATION_MODEL_UNQUALIFIED`. This
is correct: V3 has no finite-N calibration, so no calibrated upper limit can be
published, so no gate can pass.

## 4. Defect 2 — current control dimensional scaling

**Found.** The control passed `omega = 0.05` directly as the antisymmetric
generator coefficient. In the implementation's parameterisation `omega` has
units of the dissipation matrix `D`, not of a dimensionless ratio.

**Repaired.** `current_control_drift` inverts the definition exactly. With
`A = (D + Q) Sigma^{-1}` and `Q = omega J`, the whitened parts are
`S = Sigma^{-1/2} D Sigma^{-1/2}` and
`Omega = omega Sigma^{-1/2} J Sigma^{-1/2}`, so

```text
omega = r_target * lambda_min(S) / || Sigma^{-1/2} J Sigma^{-1/2} ||_op
```

**Measured at the design point:**

| Target `r_irr` | `omega` | Achieved `r_irr` | Bandwidth `‖B‖ dt` |
|---:|---:|---:|---:|
| 0.00 | 0 | 0.000000000 | 0.1500 |
| 0.02 | 9.733e−15 | 0.020000000 | 0.1500 |
| 0.05 | 2.433e−14 | 0.050000000 | 0.1502 |
| 0.10 | 4.867e−14 | 0.100000000 | 0.1507 |

The adopted control target is **`r_irr = 0.05`**, above the `0.02` scientific
gate, with the bandwidth criterion `‖B‖ dt <= 0.2` satisfied. Regressions
confirm the target is met at stiffness scales `0.25x` and `4x`, that the
stationary covariance is unchanged, that the diffusion stays SPD so the density
remains canonical Gaussian, and that the current is genuinely nonzero.

This closes the unresolved item V2 flagged: the `CTL-CURRENT` non-evaluability
was a consequence of this defect, not a separate identifiability boundary.

## 5. Defect 3 — standard error from a non-converged profile

**Found.** `_profile_se` called `minimise` and read `-res.fun` without
consulting `res.converged`. Separately, `minimise` returned
`OptimizeResult(..., True)` unconditionally after exhausting its restarts.

**Repaired.** `OptimizeResult` gains explicit reason codes and a `usable`
property requiring convergence, a finite objective and a finite point; the
restart-exhausted path now returns `converged=False` with
`restarts_exhausted_without_convergence`. A `ProfileFit` status object carries
the standard error with its licensing status:

```text
status, value, step, drop, evaluations, point_reasons
```

`value` is `None` whenever `status != valid`, and `require()` raises. There is
no path that reads a number out of a failed profile, and a non-converged
profile point is not treated as a licence to shrink the step and retry with the
final iterate.

**Regressions.** Budget exhaustion, restart exhaustion, NaN and infinite
objectives, and a value carried under a failure status all fail to produce an
official standard error or interval.

## 6. Defect 4 — lag-antisymmetry diagnostic

**Found.** `diagnostic_components` took `observed_lags=None, fitted_lags=None`
and set `anti = 0.0` when either was absent. The harness never supplied them,
so one frozen member of the family was permanently zero and never entered the
maximum.

**Repaired.** The lag inputs are required positional arguments. Absent, empty
or misaligned sets raise `DiagnosticNotEvaluable`, and the harness records
`COMPUTATION_NOT_EVALUABLE`. A diagnostic that was not computed is not a
diagnostic that passed.

`required_antisymmetry_lags(tau_slow, dt)` returns the integer frame lags
nearest `tau_slow/2`, `tau_slow` and `2 tau_slow` using the real sampling
interval, and refuses when a lag rounds below one frame.
`model_lag_covariance` supplies the fitted-model side, carrying the exposure
cross term `S^T (F^{k-1})^T C^T` at every lag — the term a filter that ignores
exposure correlation would omit.

**Regressions.** Identical observed and fitted give exactly zero residual; a
correctly modelled current gives zero residual while its *raw* antisymmetry is
large, preserving the distinction between the raw current diagnostic and the
model-residual diagnostic; a wrong fitted current and a transposed fitted
matrix both give nonzero residuals; and missing inputs are non-evaluable.

## 7. Defect 5 — validation identity

**Found.** `VALIDATION_MODULES` omitted `validation/run.py`, so the
result-counting and release semantics could change with no identity moving.

**Repaired.** The preimage now contains `validation/run.py`, `verdict.py` and
`pipeline.py` alongside the harness, cases, plan, seeds and identity module,
and the identity is hierarchical: `hierarchical_identity` folds in the
analysis, generator, seed-map, gate-semantics and packet identities as named
components. The exact preimage and the rationale for each entry are documented
in `validation_preimage()` and carried in the JSON contract.

**Regressions.** Perturbing any of the five bound component identities, or the
configuration, changes the validation identity.

## 8. Defect 6 — axial fail-open and the symmetry scale defect

**Found.** `reduce_axial` took `conservativity_qualified=True`,
`support_qualified=True` and `temporal_qualified=True` as defaults, and `c_v`
was optional. A packet with no conservativity, support, temporal or covariance
evidence qualified. The symmetry test used
`defect / max(1.0, ||K||) > 1e-9` against a stiffness of `1e-4 N/m`, so the
denominator was `1 N/m` and the test was absolute.

**Repaired.** `AxialEvidence` has nine fields, every one `None` by default
meaning *no evidence supplied*. Missing evidence fails closed with
`AXIAL_REDUCTION_UNQUALIFIED` naming the component; explicit `False` is refused
separately. The covariance is mandatory — a point Schur matrix without
uncertainty is not a valid Branch-A comparison field — and the nonlinear
remainder must be certified, not merely small, so an absent bound is refused
even though `0.0` would pass.

The symmetry test is replaced by the scale-invariant

```text
r_skew = ||K - K^T|| / ||(K + K^T)/2||
```

with a zero or unqualified symmetric scale **refused**, never rescued by
substituting `1.0`. The scientific conservativity pass comes from U's own
evidence; `r_skew` is a supporting numerical check, not a new scientific
tolerance.

**Regressions.** Each of the eight load-bearing evidence fields, omitted and
then explicitly failed, one at a time. A `1e-6` relative asymmetry is detected
at physical scales `1e-9`, `1.0` and `1e9` with identical `r_skew`.

## 9. Systematic SI-scale audit

Seven `max(1.0, .)` sites and six literal numeric thresholds were located and
classified.

| Site | Quantity | Classification | Action |
|---|---|---|---|
| `reduction.py` symmetry denominator | stiffness, `1e-4 N/m` | **MATERIAL** | replaced by scale-invariant `r_skew` |
| `numerics.py` `eigh2` symmetry check | any matrix, `1e-29`…`1e16` | **MATERIAL** (not in the audit list) | relative to the matrix's own scale |
| `numerics.py` `lu_solve` pivot floor `1e-300` | any matrix | **MATERIAL** (not in the audit list) | relative pivot floor |
| `numerics.py` `eigh2` isotropy guard `1e-300` | any matrix | minor | relative to the matrix scale |
| `confidence.py` contrast PSD guard | log-beta variance, `~1e-5` | dimensionless, sloppy | scaled to the covariance diagonal |
| `gates.py` centre quadratic guard | thermal units, `~1` | dimensionless, self-referential | scaled to the summand magnitudes |
| `optimize.py` `scale_x`, `F_TOL` | dimensionless optimiser coordinates | **SAFE** | unchanged |
| `numerics.py` Jacobi convergence, rotation skip | relative already | **SAFE** | unchanged |
| `numerics.py` `_spd_function` eigenvalue floor | relative already | **SAFE** | unchanged |

The two `eigh2`/`lu_solve` findings matter because both routines are called on
the exposure covariance blocks, which are of order `1e-29`. Under the absolute
tests, a matrix with a `43%` relative asymmetry passed as symmetric, and a
genuinely singular `1e-29` system passed as non-singular. Both are now caught;
regressions assert each.

A test asserts that the only surviving `max(1.0, .)` occurrences in the package
are the two dimensionless optimiser tolerances.

## 10. Full `C_phi` — completed end to end

New module `e1a_v5/calibration.py`.

**Primitive vector.** `Primitive` carries a `Scope` of `GLOBAL`, `BLOCK` or
`FIELD`, and its `key` deliberately omits the record for shared scopes. A
standard used by several fields therefore occupies **one** column of `phi`;
sharing is expressed by variable identity, not by an off-diagonal assertion.
Re-registering the same key with a different value or sigma is refused.
Supported categories: temperature, viscosity model, bead radius,
force/velocity/displacement calibration, 3D stiffness, Schur variables,
coordinate transforms, centre, observation noise, shutter timing, and shared,
block-specific and field-specific standards.

**To `H_eff`.** Through the implemented Schur derivative (U.A10) and
`dH = dS/(k_B T) - H dT/T`, retaining cross-covariance with temperature,
centre, coordinate transform and observation model.

**To fitted `log beta`.** This is the part T and U constrain most tightly:
U section 25 forbids the ideal Gaussian trace formula as the production
sensitivity once the noisy temporal likelihood is active. The implementation
uses the U.20 implicit derivative **evaluated by its definition** — the
pseudo-true `log beta` is located by maximising the exact expected likelihood
of the exposure-integrated, noise-bearing state-space model, and `J_beta` is
its derivative with `H_A` held locked, as in the experiment.

The expected likelihood is closed form. The joint (true latent, filter state)
system is linear, so its stationary covariance solves a discrete Lyapunov
equation and `Var(v)` follows exactly; **no trajectory is generated**.

Verified against exact analytic answers:

| Quantity | Computed | Exact |
|---|---:|---:|
| pseudo-true `log beta` at the truth | `1.8e−07` | `0` |
| pseudo-true `log beta` at a `+0.01` stiffness log error | `+0.010000` | `+0.01` |
| `d log beta / d log stiffness` | `+0.9999994` | `+1` |
| `d log beta / d log T` | `−1.0000173` | `−1` |

**To the absolute interval and the cross-field contrast.**
`assemble_calibration_covariance` builds the joint `C_b,cal = J C_phi J^T` over
all eight records at once, so shared primitives produce correlated rows
automatically. A purely common error gives equal absolute sigmas that cancel
**exactly** in the contrast (`< 1e−9` of the absolute sigma); independent
per-field errors give `sqrt(2)` times the absolute sigma, with no cancellation.

**Ceiling semantics.** The sensitivity is located numerically, so it carries a
declared relative precision (`CALIBRATION_NUMERICAL_RTOL = 1e−5`). A value
within that band of a `0.009` or `0.003` ceiling is
`UNRESOLVED_AT_NUMERICAL_PRECISION`, not a pass — the same enclosure discipline
the realized-field predicates use for a straddling region. This is tested at,
below and above both ceilings.

**Bounded bias stays separate.** `BoundedBias` holds deterministic systematics
and deliberately exposes no covariance interface. A contrast bound must be
supplied from its own joint calculation: `contrast_bound` raises if asked for
one that was not computed, and two `0.0005` absolute bounds are shown to imply
only `0.001` for a contrast, in both same-signed and opposite-signed cases.

**This does not solve continuous nuisance-domain coverage.** Completing the
implementation of `C_phi` is not a proof of uniform coverage over the qualified
domain. That remains **OPEN** and is a later validation and theoretical task.

## 11. Reason retention

Every non-evaluable record now stores structured `Refusal` objects with codes,
failing predicates and detail, plus its measured bandwidth product. The power
runner tallies verdict classifications and reason codes across replicates.
V2's report could only say that 11 of 12 current-control replicates were
non-evaluable; V3 records which refusal fired on each.

## 12. V2 evidence status

V2 smoke counts, stochastic-control counts and validation results are
**V2 / SUPERSEDED PROCEDURE EVIDENCE**. They are preserved historically in
`docs/e1a/E1A_V5_PREEXECUTION_VALIDATION_REPORT.md` and
`docs/e1a/e1a_v5_smoke_results.json`, and are **not** V3 validation. The
success predicate, axial qualification, diagnostic family, profile standard
error and current control all changed, so no V2 count transfers.

Fresh V3 seed namespaces were created under a new root with all five families
versioned (`calibration-v3`, `size_validation-v3`, `diagnostic_validation-v3`,
`complete_power-v3`, `negative_control-v3`) and checked disjoint from the
already-inspected V2 streams.

## 13. Tests and benchmark

| Suite | Checks | Failures |
|---|---:|---:|
| `test_e1a_v5_kernel.py` | 83 | 0 |
| `test_e1a_v5_procedure.py` | 180 | 0 |
| `test_e1a_v5_v3_repairs.py` | 167 | 0 |
| **total** | **430** | **0** |

Performance instrumentation, retained per the brief:

| Frames | Likelihood | Record | SE | Information/frame |
|---:|---:|---:|---:|---:|
| 800 | 1.181 µs/frame | 4.5 s | 0.08979 | 0.15505 |
| 1,600 | 0.751 µs/frame | 4.7 s | 0.06610 | 0.14306 |
| 3,200 | 0.545 µs/frame | 7.7 s | 0.04622 | 0.14629 |

Information per frame is **0.148**, consistent with V2's `0.150`: the repairs
did not change the likelihood's statistical content, as intended. The
record-length requirement is therefore unchanged at about `2.7e6` frames, and
the full-campaign resource requirement remains **OPEN**.

No scientific procedure was altered for speed, and no approximate likelihood
was introduced. NumPy and SciPy remain absent and are not a requirement; an
accelerated backend is recorded as a future engineering option only.

## 14. Remaining release blockers

| Blocker | Status |
|---|---|
| continuous nuisance-domain coverage | **OPEN** |
| finite-N critical-value calibration | **NOT RUN FOR V3** |
| 5000-replicate false-equivalence validation | **NOT RUN FOR V3** |
| 5000-replicate diagnostic-size validation | **NOT RUN FOR V3** |
| 2000 complete eight-record power validation | **NOT RUN FOR V3** |
| full-campaign resource requirement | **OPEN** |

`V RELEASE: NON-RELEASE — VALIDATION NOT YET COMPLETE.`

The baseline section 14.3 sign defect remains **owed before W-stage authority
freeze**; it is not repaired here, and the bare symbol `Delta J` appears
nowhere in the package.

## 15. Stage boundary

V3 is **READY FOR INDEPENDENT AUDIT**. No validation-result commit accompanies
it, and no fresh finite-N campaign is authorised until V3 clears. W-stage
remains **BLOCKED**. Nothing here adopts the candidate, modifies authority, or
authorises physical data collection.
