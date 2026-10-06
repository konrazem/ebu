# E1a v5 — candidate pre-execution validation plan

```text
STATUS:                  NON-CONTROLLING CANDIDATE
POLICY VERSION:          E1A-T11a-RF-v1
PROCEDURE VERSION:       5  (v1 superseded; v2 AUDIT FAILED;
                             v3 NOT CLEARED; v4 NOT CLEARED)
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
| analysis procedure | `c10efe5109da9d8b3f4a6bd2ec0bb0f57e4718bed7ee5b763f06f646a92f4e75` |
| packet schema | `b6e1e9b276ee8039e9784baa6d60e6cc3edcdd064956a0a5feaf783c348cd9f9` |
| gate semantics | `694f0769f547ebccdc13d664041ccc10f601d2042a264552081a9aea023c59ac` |
| seed map | `909521bc2204f714108aebeee0b882ad406cc2d537b226ea5221c8bbfe25a165` |
| synthetic generator | `95b14ee4321f522c17fdded41c8e7521f327543caed82c753c536fb3209530a9` |
| validation procedure | `6be714826bd8d6d08125dd0f1b5a8f40cc71622f122e5cf351712a924953cba9` |

Each identity is taken over an ordered preimage of module path and file digest,
followed by the canonical JSON of the declared configuration
`{"design_point": "e1a_v5_candidate_2026-10-06", "policy_version": "E1A-T11a-RF-v1", "procedure_version": 5, "supersedes": "procedure version 4 (audit: NOT CLEARED)"}`. Nothing ambient enters the preimage.

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

PRNG `python-stdlib-MersenneTwister-19937`, seed root `e1a_v5/validation/v5/2026-10-06`.
Derivation `sha256(root|family|case|'rep'|replicate)[:8] big-endian`.

| Family | Family seed | Role |
|---|---:|---|
| `critical-calibration-v5` | 15280046052714316182 | confirmatory |
| `size-validation-v5` | 10157267318770872789 | confirmatory |
| `diagnostic-validation-v5` | 8067945209365484799 | confirmatory |
| `complete-power-v5` | 3060025210657503379 | confirmatory |
| `negative-controls-v5` | 17829790455794060110 | confirmatory |
| `engineering-v5` | 12900281823331069400 | engineering only |

The five confirmatory families are frozen here and are **not executed**. Each
is checked disjoint from the corresponding V4 (`e1a_v5/validation/v4/2026-10-06`), V3 and V2
streams, and from **every** engineering stream past and present — an earlier
version's engineering draws have been inspected just as thoroughly as its
confirmatory ones.

`engineering-v5` carries every draw made during implementation and smoke
testing. It is explicitly not part of any confirmatory validation, and no
result drawn from it may be reported as a validation outcome.

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

51 cases, 117408 required replicates in total.

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

### control (27 cases, 13408 replicates)

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
| `CTL-ETA-T-COV` | Omitted eta/T covariance versus the correct shared thermometry covariance | 5000 | false complete support bounded; covariance consequence recorded |
| `CTL-NOISE-HI` | Localisation noise above the qualified ratio | 200 | diagnose, refuse or lose support |
| `CTL-NOISE-HEAVY` | Non-Gaussian heavy-tailed localisation noise | 200 | diagnose, refuse or lose support |
| `CTL-NOISE-COLOR` | Coloured localisation noise | 200 | diagnose, refuse or lose support |
| `CTL-NOISE-STATE` | State-dependent localisation noise | 200 | diagnose, refuse or lose support |
| `CTL-BLUR-MISMATCH` | Generator exposure differs from the analysed shutter model | 200 | diagnose, refuse or lose support |
| `CTL-DRIFT` | Slow centre drift during the record | 200 | stationarity or diagnostics prevent full support |
| `CTL-SELECTION` | Clipping / tracking selection of observations | 200 | invalid measurement or model, not a reconditioned pass |
| `CTL-AXIAL-COUPLE` | 3D stiffness with K_qz != 0; plane block would bias | 1 | pipeline uses H_eff; K_qq bias quantified |
| `CTL-AXIAL-MEMORY` | Lateral density matches Schur but the 2D temporal model fails | 5000 | TEMPORAL_MODEL_UNQUALIFIED / INVALID; false complete support bounded |
| `CTL-RF-TEMP-304` | Realized temperature 304 K | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-STIFF-1021` | Realized stiffness 1.021-fold | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-MODES` | One weak and one strong stiffness mode | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-ELLIPSE` | Unrotated target-eigenvalue ellipse | 1 | FIELD_REALIZATION_OUT_OF_SPEC |
| `CTL-RF-STRADDLE` | Uncertainty region straddling a realization boundary | 1 | FIELD_REALIZATION_UNRESOLVED |
| `CTL-RF-VALID` | Nominal-like realized field | 1 | FIELD_REALIZATION_VALID (synthetic) |
| `CTL-OPT-FAIL` | Forced optimiser failure modes | 1 | COMPUTATION_NOT_EVALUABLE; beta never fabricated |

## 8a. Negative-control release events

This section makes explicit what the controlling T-stage design already
requires. It introduces **no new scientific threshold** and alters no margin:
T names temperature/viscosity covariance error as a required negative control,
and requires each required negative control separately to satisfy the
false-support bound.

### `CTL-ETA-T-COV`

**Primary release event — `FALSE_SUPPORT`.** The complete authoritative
pipeline returns `SUPPORTED_WITHIN_DECLARED_TOLERANCES` under the declared
eta/T covariance-misspecification alternative. This is the quantity whose
probability is controlled.

| Item | Value |
|---|---|
| Replicates | 5000 independent outer validation experiments |
| Event count | number of complete SUPPORT outcomes under the covariance-error alternative |
| Release condition | one-sided 95% Clopper–Pearson upper bound ≤ 0.025 |

**Secondary recorded consequence — mandatory, not a release criterion.** Each
replicate additionally records the correct standard uncertainty, the
misspecified standard uncertainty, their ratio and difference, the interval
width, and any classification change. The earlier wording *coverage
consequence detected* named no per-replicate event; it is superseded here.

### `CTL-AXIAL-MEMORY`

**Expected physical classification.** `TEMPORAL_MODEL_UNQUALIFIED` and/or
`INVALID_MEASUREMENT_OR_MODEL`, according to the actual qualification result,
recorded per replicate.

**Primary release event — `FALSE_SUPPORT`.** The complete authoritative
pipeline returns `SUPPORTED_WITHIN_DECLARED_TOLERANCES` under the hidden-memory
world.

| Item | Value |
|---|---|
| Replicates | 5000 independent outer validation experiments |
| Release condition | one-sided 95% Clopper–Pearson upper bound ≤ 0.025 |

Neither control's 5000 replicates are executed in this repair. They are a
prospective requirement of the frozen plan.

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

## 11. Procedure version 5 repairs

V4 was **NOT CLEARED** by independent audit. Version 5 repairs the five
material blockers it found, and two further defects of the same classes that
surfaced while doing so.

| Item | V5 state |
|---|---|
| numerical sensitivity | **certified**. Derivatives come from interval-arithmetic hyper-dual arithmetic: the chain rule is evaluated, not approximated, so truncation error is exactly zero and there is no step size to bound |
| floating point | every hyper-dual component is an interval, outward rounded after each operation — one ulp for the IEEE-correctly-rounded `+ - * /` and `sqrt`, two for `log` and `exp` |
| Riccati fixed point | one-step residual divided by `1 − ‖F_cl‖²`, the map's own contraction factor |
| linear solve | residual enclosed in interval arithmetic, amplified by a Weyl-certified lower bound on the smallest eigenvalue of the symmetric expected information |
| fine/coarse heuristic | **removed from qualification**. The finite-difference production sensitivity is deleted; the profiled-optimisation route survives only as a cross-check and is explicitly `certified = False` |
| no enclosure | `UNRESOLVED_AT_NUMERICAL_PRECISION`, which is fail-closed; an uncertified calibration cannot qualify at all |
| axial scale effect | **exact and finite**: `b* = log d − log tr((I+E)⁻¹)`, with supremum `−log(1−ρ)` over the certified set. The first-order `|tr E|/d` is gone |
| axial geometry effect | **exact and finite**: `G = maxᵢ |log(1+λᵢ) − mean_j log(1+λⱼ)|`, with supremum `(d−1)/d · log((1+ρ)/(1−ρ))`. The first-order deviatoric norm is gone |
| axial qualification object | a certified **set** `‖E‖_op ≤ ρ` built by a closed-form bound on the exact Schur remainder over the declared primitive covariance; every step is an inequality. One evaluated witness no longer qualifies anything |
| axial centre effect | a purely **multiplicative** factor `√(1+ρ)`. The remainder is not a translation, so no additive centre enlargement is applied |
| axial rate effect | factor `1+ρ` on every relaxation rate, routed into the exposure, bandwidth and localisation envelopes |
| gate calibration | a typed `CalibratedGateProcedure` carrying family, procedure version, procedure identity, calibration identity, coverage target, domain identity, radius, status and a fixture flag. `GateLimit.calibrated(statistic, limit, identity)` is **deleted** |
| raw statistic separation | `limit = statistic + procedure.radius` always; no constructor accepts a limit, so `upper_limit = raw_statistic` cannot be expressed |
| test fixtures | `synthetic_calibrated_gate_fixture` sets `fixture_only` and puts every identity in the `SYNTHETIC-FIXTURE` namespace; the production builder refuses it |
| observation qualification | evaluated per record against T 15.2 / T.23: `R_obs` PSD, `P` invertible, localisation ratio ≤ 0.05, exposure ≤ 0.1 τ_fast, `‖B‖dt` ≤ 0.2, shutter inside the frame, noise model in the qualified set. No caller may assert `observation_valid` |
| `CTL-ETA-T-COV` | **restored** to 200 replicates as a full-pipeline stochastic control (superseded by §8a, which sets 5000 and names the release event). The analysis `C_φ` omits the declared correlation between the stiffness and temperature standards, which share one thermometry error |
| `CTL-AXIAL-MEMORY` | **restored** to 200 replicates (superseded by §8a, which sets 5000 and names the release event), generated from an actual 3D hidden-memory world whose lateral marginal is exactly the Schur density and whose lateral path no 2D Markov generator produces |
| plan correspondence | the deterministic suite parses this plan's JSON and compares case ID, purpose, replicate count, seed family, expected event, parameter specification and validation family. Any difference fails; there is no warning-only mode and no registry-as-source-of-truth fallback |

Two further defects surfaced during the repair and are also fixed: the V4
meta-test compared the case registry to the dispatcher — both of them code —
and never to the machine plan; and the V4 machine plan's `cases` block was
never regenerated, so it still carried V3 seed namespaces and had no
`expected_event` field at all.

V2, V3 and V4 results are retained as historical evidence and are labelled
**SUPERSEDED PROCEDURE EVIDENCE**. They are not V5 validation.

Open release blockers are listed in the JSON contract under
`open_release_blockers`. Finite-N critical calibration, false-equivalence
size, diagnostic size and complete power are all **NOT RUN FOR V5**,
continuous nuisance-domain coverage remains **OPEN**, and the `e1a_v5` test
suites still require CI integration before W.
