# E1a v5 — candidate pre-execution validation plan

```text
STATUS:                  NON-CONTROLLING CANDIDATE
POLICY VERSION:          E1A-T11a-RF-v1
PROCEDURE VERSION:       4  (v1 superseded; v2 AUDIT FAILED; v3 NOT CLEARED)
AUTHORITY MODIFIED:      NO
EXECUTION AUTHORISED:    FALSE
E1a-v4:                  UNTOUCHED (identities, contracts, plan, seal)
BASELINE SIGN DEFECT:    STILL OWED before W-stage authority freeze
```

This document is the normative human rendering of
[`e1a_v5_validation_plan.json`](e1a_v5_validation_plan.json). The JSON is the
mechanical schema and ordering source; any mismatch between them is an
integrity failure, not permission to choose one selectively.

It is frozen **before** validation runs. The commit that introduces it precedes
the commit carrying any validation outcome, so the record shows that no
validated quantity was tuned using the validation it was judged by.

## 1. Candidate procedure identities

| Object | SHA-256 |
|---|---|
| analysis procedure | `a687ea512a33561a8630d9c0b60e486b49bf72fb59242f0a2fbaa199141d1498` |
| packet schema | `b6e1e9b276ee8039e9784baa6d60e6cc3edcdd064956a0a5feaf783c348cd9f9` |
| gate semantics | `694f0769f547ebccdc13d664041ccc10f601d2042a264552081a9aea023c59ac` |
| seed map | `1357c19ea90a9912da088db68569311d8b7caf7ccc309bf28c7c818f8999e633` |
| synthetic generator | `a734b184f7169ee715005992171af69f2b9918c4c71bc299901410fb660ca7a9` |
| validation procedure | `305f4c7fbf25e1b92008b4d1a82fa684830c855711a7f2369de81135656e415c` |

Each identity is taken over an ordered preimage of module path and file digest,
followed by the canonical JSON of the declared configuration
`{"design_point": "e1a_v5_candidate_2026-10-06", "policy_version": "E1A-T11a-RF-v1", "procedure_version": 4, "supersedes": "procedure version 3 (audit: NOT CLEARED)"}`. Nothing ambient enters the preimage.

The validation identity binds, in addition to its own modules, the four
modules that decide what a result *means*: `evidence.py`, `diagnostics.py`,
`validation/dispatch.py` and `validation/events.py`. Under V3 a change to any
of those could alter every validation outcome without moving the identity.

## 2. Frozen thresholds

Every value below is an immutable input from the independently cleared T and U
sources. None may be changed after a validation outcome is seen.

| Quantity | Value | Source |
|---|---:|---|
| absolute equivalence margin `log 1.05` | 0.04879016417 | T.7 |
| cross-field margin `log 1.02` | 0.01980262730 | T.8 |
| geometry margin `log 1.05` | 0.04879016417 | T.9 |
| centre margin, thermal units | 0.10 | T.9 |
| reversibility margin `r_irr` | 0.02 | T.10 |
| critical-value ceiling | 2.10 | T 20.2 |
| normal starting critical value | 1.959963984540 | T 20.2 |
| absolute calibration ceiling | 0.009 | T.24 / U.23 |
| contrast calibration ceiling | 0.003 | T.24 / U.24 |
| bounded bias, absolute and contrast | 0.0005 | T.18 / U.22 |
| quadratic-observation equivalents `N*` | 450000 | T.23 |
| efficient information `I*` | 408164 | T.23 |

Boundary equality at a tolerance is **not** a pass; the interval must lie
strictly inside.

## 3. One-sided error budget

| Term | Allowance |
|---|---:|
| model tail | 0.0200 |
| auxiliary confidence-set noncoverage | 0.0010 |
| selection approximation | 0.0001 |
| residual for finite calibration and numerical envelope | 0.0039 |
| **total allowed one-sided false equivalence** | **0.025** |

## 4. Diagnostic family

Fixed before calibration: components `cvm_chi2_2_radii`, `angular_harmonics`, `innovation_lag_covariance`, `lag_antisymmetry_residual`, angular harmonics [1, 2, 3, 4], innovation lags
[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], familywise false-rejection target **0.005** across all eight records. No
search for a favourable subset of lags or moments is permitted.

## 5. Replicate counts and exact acceptance

| Family | Required replicates | Criterion | Exact acceptance |
|---|---:|---|---|
| false equivalence | 5000 per configuration | CP upper <= 0.025 | at most **106** events |
| diagnostic family | 5000 per configuration | CP upper <= 0.005 | at most **16** events |
| complete true-bridge power | 2000 complete 8-record experiments | CP lower >= 0.90 | at least **1823** successes |

Bounds are exact one-sided 95%% Clopper-Pearson beta quantiles. No normal
approximation enters any release criterion. Invalid, refused and
optimiser-failed experiments remain in the denominator.

## 6. Seed architecture

PRNG `python-stdlib-MersenneTwister-19937`, seed root `e1a_v5/validation/v4/2026-10-06`.
Derivation `sha256(root|family|case|'rep'|replicate)[:8] big-endian`.

| Family | Family seed | Role |
|---|---:|---|
| `critical-calibration-v4` | 12175842811704036618 | confirmatory |
| `size-validation-v4` | 3157330279942037537 | confirmatory |
| `diagnostic-validation-v4` | 2372191960314171408 | confirmatory |
| `complete-power-v4` | 6447534061085332118 | confirmatory |
| `negative-controls-v4` | 6660955642057257706 | confirmatory |
| `engineering-v4` | 8141223138503822625 | engineering only |

The five confirmatory families are frozen here and are **not executed**. Each
is checked disjoint from the corresponding V3 stream (root `e1a_v5/validation/v3/2026-10-06`) and
V2 stream (root `e1a_v5/validation/2026-10-06`), whose outcomes have already been inspected.

`engineering-v4` is a separate namespace carrying every draw made during
implementation and smoke testing. It is explicitly not part of any
confirmatory validation, and no result drawn from it may be reported as a
validation outcome. Keeping it separate is what stops a repair session from
consuming — and so inspecting — a future confirmatory stream.

**No `e1a_v4` seed is reused**: its scientific identity does not match this
procedure.

## 7. Synthetic design point

> This is a **synthetic prospective** configuration consistent with the T/U
> domains. It is not measured apparatus performance, and no value here is a
> real calibration.

| Parameter | Value |
|---|---:|
| reference temperature | 298 K |
| hot-field temperature | 318 K |
| reference stiffness | 1.0e-04 N/m |
| stiffness-challenge factor | 2.1 |
| ellipse eigenvalues | 1.5e-04, 6.0e-05 N/m |
| ellipse orientation | 0.523599 rad |
| bead radius | 5.0e-07 m |
| buffer viscosity at reference | 8.90e-04 Pa.s |
| axial stiffness fraction | 0.20 |
| lateral-axial coupling fraction | 0.05 |
| instantaneous localisation ratio | 0.020 |
| exposure, fraction of `tau_fast` | 0.05 |
| frame interval, fraction of bandwidth ceiling | 0.75 |

## 8. Preregistered cases

51 cases, 107808 required replicates in total.

### calibration (7 cases, 28000 replicates)

| Case | Purpose | Replicates | Expectation |
|---|---|---:|---|
| `CAL-SCALE-01` | Calibrate c_minus/c_plus for the absolute log-beta interval | 4000 | c_minus, c_plus <= 2.10 |
| `CAL-CONTRAST-01` | Calibrate the within-block contrast critical values | 4000 | c_minus, c_plus <= 2.10 |
| `CAL-SHAPE-01` | Calibrate the T4 geometry upper-limit radius | 4000 | radius finite at the zero-distance boundary |
| `CAL-CENTRE-01` | Calibrate the centre upper-limit radius | 4000 | radius finite |
| `CAL-STAT-01` | Calibrate the four-quarter stationarity upper limit | 4000 | radius finite |
| `CAL-CURRENT-01` | Calibrate the r_irr upper-limit radius at omega = 0 | 4000 | radius finite at the nonregular boundary |
| `CAL-DIAG-01` | Calibrate the joint diagnostic maximum and its null scales | 4000 | all four null scales strictly positive |

### size (11 cases, 55000 replicates)

| Case | Purpose | Replicates | Expectation |
|---|---|---:|---|
| `SIZE-ABS-LO` | Absolute equivalence at the lower boundary b = -log(1.05) | 5000 | CP upper <= 0.025 |
| `SIZE-ABS-HI` | Absolute equivalence at the upper boundary b = +log(1.05) | 5000 | CP upper <= 0.025 |
| `SIZE-CON-LO` | Cross-field contrast at the lower boundary -log(1.02) | 5000 | CP upper <= 0.025 |
| `SIZE-CON-HI` | Cross-field contrast at the upper boundary +log(1.02) | 5000 | CP upper <= 0.025 |
| `SIZE-SHAPE-BD` | Geometry upper limit at the shape boundary G = log(1.05) | 5000 | CP upper <= 0.025 |
| `SIZE-CENTRE-BD` | Centre upper limit at the boundary m = 0.10 | 5000 | CP upper <= 0.025 |
| `SIZE-CURRENT-BD` | Current upper limit at the boundary r_irr = 0.02 | 5000 | CP upper <= 0.025 |
| `SIZE-NUIS-NOISE` | Absolute boundary at the top of the qualified noise range | 5000 | CP upper <= 0.025 |
| `SIZE-NUIS-EXP` | Absolute boundary at the exposure ceiling | 5000 | CP upper <= 0.025 |
| `SIZE-NUIS-COND` | Absolute boundary near the conditioning limit kappa_2 = 100 | 5000 | CP upper <= 0.025 |
| `SIZE-NUIS-CAL` | Absolute boundary with the full qualified calibration covariance | 5000 | CP upper <= 0.025 |

### diagnostic (3 cases, 15000 replicates)

| Case | Purpose | Replicates | Expectation |
|---|---|---:|---|
| `DIAG-NULL-NOM` | Diagnostic familywise size at the nominal true benchmark | 5000 | CP upper <= 0.005 |
| `DIAG-NULL-EXP` | Diagnostic familywise size at the exposure ceiling | 5000 | CP upper <= 0.005 |
| `DIAG-NULL-COND` | Diagnostic familywise size near the conditioning limit | 5000 | CP upper <= 0.005 |

### power (3 cases, 6000 replicates)

| Case | Purpose | Replicates | Expectation |
|---|---|---:|---|
| `POWER-NOMINAL` | Complete eight-record success at the nominal true benchmark | 2000 | CP lower >= 0.90 |
| `POWER-CONDLIM` | Complete success near the conditioning limit | 2000 | CP lower >= 0.90 |
| `POWER-NOISEHI` | Complete success at the top of the qualified noise range | 2000 | CP lower >= 0.90 |

### control (27 cases, 3410 replicates)

| Case | Purpose | Replicates | Expectation |
|---|---|---:|---|
| `CTL-BLIND-107` | Hidden A scale c = 1.07; expect beta_blinded = beta/c | 200 | recovered log beta matches after multiplying by c |
| `CTL-BLIND-090` | Hidden A scale c = 0.90; expect beta_blinded = beta/c | 200 | recovered log beta matches after multiplying by c |
| `CTL-COMMON-07` | Common wrong scale beta = 0.7 in every field | 200 | cross-field contrasts may pass; absolute must fail |
| `CTL-FIELD-106` | Field-specific alternative (1, 1.06, 1, 1) | 200 | false support bounded |
| `CTL-FIELD-MIX` | Field-specific alternative (1, 0.93, 1.05, 1) | 200 | false support bounded |
| `CTL-FIELD-110` | Field-specific alternative (1, 1, 1, 1.10) | 200 | false support bounded |
| `CTL-HARD-025` | Hard 2.5% single-field contrast | 200 | false support bounded |
| `CTL-GEOM-TRACE` | Trace-preserving wrong geometry | 200 | scalar beta plausible; T4 geometry rejects |
| `CTL-GEOM-ROT` | Correct eigenvalues, wrong orientation | 200 | geometry detects the rotation |
| `CTL-CURRENT` | Current-preserving Gaussian, A Sigma = D + omega J | 200 | density/geometry pass; current gate blocks support |
| `CTL-ETA-T-COV` | Omitted eta/T covariance versus the correct shared covariance | 1 | coverage consequence detected |
| `CTL-NOISE-HI` | Localisation noise above the qualified ratio | 200 | diagnose, refuse or lose support |
| `CTL-NOISE-HEAVY` | Non-Gaussian heavy-tailed localisation noise | 200 | diagnose, refuse or lose support |
| `CTL-NOISE-COLOR` | Coloured localisation noise | 200 | diagnose, refuse or lose support |
| `CTL-NOISE-STATE` | State-dependent localisation noise | 200 | diagnose, refuse or lose support |
| `CTL-BLUR-MISMATCH` | Generator exposure differs from the analysed shutter model | 200 | diagnose, refuse or lose support |
| `CTL-DRIFT` | Slow centre drift during the record | 200 | stationarity or diagnostics prevent full support |
| `CTL-SELECTION` | Clipping / tracking selection of observations | 200 | invalid measurement or model, not a reconditioned pass |
| `CTL-AXIAL-COUPLE` | 3D stiffness with K_qz != 0; plane block would bias | 1 | pipeline uses H_eff; K_qq bias quantified |
| `CTL-AXIAL-MEMORY` | Lateral density matches Schur but the 2D temporal model fails | 1 | TEMPORAL_MODEL_UNQUALIFIED or model failure |
| `CTL-RF-TEMP-304` | Realized temperature 304 K | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-STIFF-1021` | Realized stiffness 1.021-fold | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-MODES` | One weak and one strong stiffness mode | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-ELLIPSE` | Unrotated target-eigenvalue ellipse | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-STRADDLE` | Uncertainty region straddling a realization boundary | 1 | FIELD_REALIZATION_UNRESOLVED |
| `CTL-RF-VALID` | Nominal-like realized field | 1 | FIELD_REALIZATION_VALID (synthetic) |
| `CTL-OPT-FAIL` | Forced optimiser failure modes | 1 | COMPUTATION_NOT_EVALUABLE; beta never fabricated |

## 9. Release logic

`RELEASE` only if **every** mandatory validation requirement passes. No
weighted score, no majority vote. A partial validation cannot produce
`RELEASE`, and a reduced-count smoke run forces `NON-RELEASE`.

Changing any calibrated threshold using held-out validation outcomes
invalidates that validation and requires a new reviewed procedure with fresh
seeds. A failed power result does not grant permission to lengthen a record.

## 10. What this plan does not do

It modifies no authority. It does not adopt the candidate procedure, authorise
physical data collection, authorise an official campaign, or authorise
unblinding. W-stage remains a separate authorisation.

## 11. Procedure version 4 repairs

V3 was **NOT CLEARED** by independent audit. Version 4 repairs the seven
material defects it found, and three more that surfaced while doing so.

| Item | V4 state |
|---|---|
| evidence validation | runs **before** the conjunction, in `e1a_v5.evidence`: exactly eight canonical `(block, field)` records and exactly six within-block contrasts, each present once |
| duplicate records | `INVALID / INCOMPLETE EVIDENCE`; no first, last, best, valid or latest selection is permitted |
| interval validity | one `ScientificInterval` carrying the estimate, SE, critical values and bias bound; endpoints are re-derived from them, so a reversed, non-finite or unexplained interval is refused |
| unusable interval containment | returns `None`, never `True` and never `False` |
| critical-value status | `UNCALIBRATED` / `CALIBRATED` / `INVALID`; the normal quantile is the *starting value* of the search and is marked `UNCALIBRATED` |
| gate limits | the same three statuses; an uncalibrated limit has no answer, and the raw statistic may not be compared against the tolerance in its place |
| diagnostic family | one `DiagnosticFamilyResult` **derived** from the per-record components and a calibrated familywise critical value; a caller-supplied boolean is checked for consistency, never substituted |
| record/family contradiction | `CONTRADICTORY`; never silently resolved in either direction |
| current control | the runner passes the dimensionless `r_irr_target`; the obsolete `omega` field is gone from the case schema |
| `CTL-AXIAL-MEMORY`, `CTL-ETA-T-COV` | reclassified from 200 sampled replicates to 1 **exact** deterministic check each. Both compare closed-form quantities — an axial reduction refusal and two covariance propagations — so sampling them repeated an exact computation. No threshold or acceptance criterion changes; `CTL-ETA-T-COV` was additionally a no-op as a stochastic case, which is how the reclassification was found. |
| `C_phi` | on the official path: one experiment-level `C_b,cal = J_beta C_phi J_beta^T`, with contrasts `C_d = D C_b D^T` read off the same matrix |
| U.20 sensitivity | implicit differentiation of the expected-score system over the full production nuisance vector (scale, centre and the temporal `A`); the log-beta row is extracted only after the system is solved |
| numerical error | a certified per-quantity enclosure with a measured evaluation-noise constant; the fixed `1e-5` band is removed |
| 0.009 / 0.003 | `PASS` iff `u+ <= c`, `FAIL` iff `u- > c`, `UNRESOLVED` otherwise, with inclusive ceiling semantics and `c` never widened |
| bounded bias | a missing bound is `MISSING`, not `0.0`, everywhere |
| axial remainder | a typed stiffness residual in N/m, normalised to `E_K = K_eff^{-1/2} ΔK K_eff^{-1/2}` and propagated into the existing log-beta, contrast, geometry and centre budgets; the dimensional `1e-3` predicate is removed |
| validation cases | typed `CaseConfig`; an unknown case ID or an unconsumed declaration is an invalid plan, never a nominal run |
| case events | one versioned evaluator; a complete-support event reads the authoritative verdict and nothing else |
| per-replicate reasons | retained in full alongside the histograms; the summary is a convenience, the records are the evidence |
| seeds | fresh V4 confirmatory namespaces plus a separate `engineering-v4` namespace |

Three further defects surfaced during the repair and are also fixed: V3's
deterministic control battery raised `TypeError` before its first assertion and
so never ran at all; `CTL-ETA-T-COV` declared a world no generated record could
distinguish, making it a no-op case of the same class as defect 6; and three
`confidence.py` helpers returned a pass from `all(())` on an empty
qualification sequence.

V2 and V3 results are retained as historical evidence and are labelled
**SUPERSEDED PROCEDURE EVIDENCE**. They are not V4 validation.

Open release blockers are listed in the JSON contract under
`open_release_blockers`. Finite-N critical calibration, false-equivalence
size, diagnostic size and complete power are all **NOT RUN FOR V4**, and
continuous nuisance-domain coverage remains **OPEN**.
