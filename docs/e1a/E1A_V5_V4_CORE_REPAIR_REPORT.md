# E1a v5 — procedure version 4 core repair

```text
STATUS:                  V4 CORE PROCEDURE REPAIRED AND FROZEN
                         — INDEPENDENT AUDIT REQUIRED
V RELEASE:               NON-RELEASE — VALIDATION NOT YET COMPLETE
PROCEDURE VERSION:       4  (v1 superseded; v2 AUDIT FAILED; v3 NOT CLEARED)
REPAIR STARTING COMMIT:  86b95d4f44a090c5eddf753980c959a59e52dbff
V4 CORE REPAIR COMMIT:   6cc6d0a30a26b2784b1ce80342d447f4bb516388
V4 FREEZE COMMIT:        efaa423784e7972190ec8dd5fc733109a20e02bd
AUTHORITY MODIFIED:      NO
OLD V4 PACKAGE / SEAL:   UNTOUCHED
REAL DATA USED:          NO
EXECUTION AUTHORISED:    FALSE
W-STAGE:                 BLOCKED
```

The independent V3 audit returned **V3 CORE IMPLEMENTATION: NOT CLEARED** with
seven material defects. All seven are repaired here. Three further defects of
the same classes surfaced while repairing them and are also fixed and reported.

This document is the human rendering of the repair. The mechanical contract is
[`e1a_v5_validation_plan.json`](e1a_v5_validation_plan.json); any mismatch
between them is an integrity failure, not permission to choose one.

---

## 1. Defect 1 — malformed evidence could still yield complete SUPPORT

### What was wrong

V3 centralised the conjunction in `pipeline.complete_pipeline_result` but still
judged whatever evidence it was handed. Three distinct holes, all reproduced
against the V3 freeze before repair:

| Malformation | V3 verdict |
|---|---|
| invalid duplicate record placed *before* its valid twin | `SUPPORTED_WITHIN_DECLARED_TOLERANCES` |
| ninth extra record | `SUPPORTED_WITHIN_DECLARED_TOLERANCES` |
| every absolute interval reversed to `(+0.9, −0.9)` | `SUPPORTED_WITHIN_DECLARED_TOLERANCES` |

The duplicate holes came from one line, `by_key = {r.key: r for r in records}`:
a map keyed by identity, so the last record under a key silently won and an
extra key was simply never iterated. The reversed-interval hole came from
`Interval.strictly_inside`, which tests `−margin < lo and hi < margin`; with
`lo = +0.9` and `hi = −0.9` both clauses hold.

### What V4 does

A new module `e1a_v5/evidence.py` runs **before** the conjunction. It answers a
question the conjunction never asked: *is this evidence the preregistered
experiment at all?*

- **Canonical identities.** `RecordKey(block, fld)` and
  `ContrastKey(block, fld, reference, reference_block)` are typed, hashable and
  ordered. `RecordKey.expected()` is exactly the eight `(block, field)` pairs;
  `ContrastKey.expected()` is exactly the six within-block contrasts.
- **Exact cardinality.** `check_record_cardinality` counts a *list*, not a map,
  so duplicates, extras and missing keys are all visible. Each record also
  carries `embedded_key`, checked against the identity it was filed under, so a
  record whose contents disagree with its key is refused rather than re-filed.
- **No selection rule.** A duplicate yields `INVALID_RECORD_MONITOR`. First,
  last, best, valid and latest are all refused by construction — there is no
  code path that chooses among duplicates.
- **`ScientificInterval`.** An interval travels with the evidence that entitles
  it to be tested: the estimate, the standard error, the critical values and
  their status, and the bias bound actually applied. `validate()` re-derives
  `[b̂ − c₋s − b, b̂ + c₊s + b]` from those pieces and compares, so an interval
  whose numbers do not follow from its own inputs is caught.
- **Containment has three answers.** `strictly_inside` returns `None` for an
  unusable interval — never `False`. An unusable interval has no containment
  answer, and the caller must classify it as missing evidence rather than as a
  failed equivalence test.

The conjunction then skips any identity supplied more than once: not only is
the experiment refused, no duplicated identity contributes a pass to any tally.

### Regressions

Eleven malformations are tested, each required to fail closed before complete
support: duplicate before, duplicate after, two valid duplicates, two
conflicting duplicates, ninth record, missing record, wrong embedded identity,
reversed endpoints, NaN endpoint, infinite endpoint, duplicate contrast,
missing contrast, cross-block contrast, wrong-reference contrast, negative SE,
zero SE, missing critical-value provenance, uncalibrated critical value,
invalid critical value, endpoint identity mismatch, missing absolute bias,
missing contrast bias. One test records the *reason the object exists*: a raw
`Interval(0.9, −0.9)` still reports `strictly_inside = True`, and only the
validity object catches it.

A **positive control** runs alongside: a fully populated, fully qualified
eight-record experiment with six contrasts and a calibrated diagnostic family
*does* return `SUPPORTED_WITHIN_DECLARED_TOLERANCES` with 8/8, 6/6 and all four
gates. The repair is a gate, not a wall.

---

## 2. Record cardinality, critical-value status and gate limits

### Exact 8-record identity

`2 preparation blocks × 4 fields = 8 records`, one per canonical key. Unknown
block or field IDs cannot be constructed — `BlockId` and `FieldId` are enums —
and anything outside the expected set is an extra.

### Critical-value status

V3 carried `NORMAL_CRITICAL = CriticalValues(1.959963985, 1.959963985)` with no
indication that it is the *starting value* of a calibration search. V4 adds
`CriticalValueStatus`:

```text
UNCALIBRATED   no finite-N calibration has been performed
CALIBRATED     produced by a completed, identified calibration stream
INVALID        a calibration was attempted and its output is not usable
```

`NORMAL_CRITICAL` is `UNCALIBRATED`, and an uncalibrated critical value makes
its interval unusable. **For V4 this is the live state**: no finite-N critical
value exists, so ordinary V4 analysis cannot claim a final finite-N pass.
`confidence.synthetic_calibrated()` returns a `CALIBRATED` value whose
provenance string reads `SYNTHETIC FIXTURE - not a validation calibration`; it
exists only to exercise verdict code in deterministic unit tests, as §9 of the
brief permits.

### Gate limits

The four precision gates are calibrated one-sided upper limits, not raw
statistics. `evidence.GateLimit` carries the same three statuses, and
`passes(tolerance)` returns `None` when uncalibrated. Comparing the raw
statistic against the tolerance in its place — exactly the shortcut the audit
found in the control runner — has no code path.

---

## 3. Defect 2 — one authoritative diagnostic-family result

### What was wrong

`complete_pipeline_result(records, contrasts, diagnostic_family_rejected)`
accepted a caller-supplied boolean and never compared it against the
per-record `diagnostic_rejected` fields. `record.diagnostic_rejected = True`
beside `family = False` returned `SUPPORTED_WITHIN_DECLARED_TOLERANCES`.
Worse, `validation/run.py` manufactured that boolean from
`False if diag_evaluated else None` — it converted *raw components exist* into
*the family did not reject*.

### What V4 does

`diagnostics.DiagnosticFamilyResult` is **derived**, never supplied:

```text
status    CALIBRATED | UNCALIBRATED | NOT_EVALUABLE | CONTRADICTORY
statistic familywise maximum of the scaled components over all records
critical_value + critical_identity
rejected  bool, or None when the family is not usable
records   per-record components, scaled maxima and derived decisions
reason_codes
```

`evaluate_diagnostic_family` refuses in this order, each fail-closed:

1. a required record contributes no diagnostic, or a duplicate or unplanned
   record diagnostic appears, or a required component is absent or non-finite
   → `NOT_EVALUABLE`;
2. no frozen null scales, or no calibrated familywise critical value, or a
   critical value with no calibration identity → `UNCALIBRATED`;
3. a record's own claimed rejection disagrees with what its components give, or
   a caller's claimed family decision disagrees with the derivation →
   `CONTRADICTORY`;
4. otherwise `CALIBRATED`, with `rejected` derived.

Only status 4 can take part in a supported verdict. All four required
components — radial CvM, angular harmonics, innovation lag covariance and the
observed-minus-fitted lag-antisymmetry residual — must be present and finite
for every one of the eight records.

**V4's live state is `UNCALIBRATED`.** No finite-N diagnostic-family
calibration exists, so complete support remains unavailable, which is correct.

### Regressions

All records passing; one record rejecting; record-rejects-but-components-say-no;
caller-claims-rejected-but-components-say-no; missing record diagnostic; a
record with no components; a NaN antisymmetry component; no critical value; no
null scales; a NaN critical value; a critical value with no identity; an empty
expected set. Each is checked both at the family level and end-to-end through
the pipeline.

---

## 4. Defect 3 — the current-control runner route

### What was wrong

V3 repaired the constructor to take a dimensionless `r_irr_target` but left the
case declaring `omega=0.05` and the runner passing `kw["omega"]`. Calling the
public route raised:

```text
TypeError: design_specs() got an unexpected keyword argument 'omega'
```

No compatibility alias was added — an alias would have hidden the stale case
definition rather than exposing it.

### What V4 does

`CaseConfig` has no `omega` field at all. `CTL-CURRENT` declares
`r_irr_target = 0.05`, the dispatcher routes it to `design_specs`, and the test
exercises the **exact public route** a later campaign will use:

```text
case registry → instantiate() → design_specs() → GeneratorSpec
```

Measured on the generated world:

| Quantity | Value |
|---|---|
| achieved `r_irr` | 0.05 to nine decimals |
| above the 0.02 gate | yes |
| bandwidth `‖B‖₂ Δ` | 0.1502, inside the 0.2 ceiling |
| stationary covariance | unchanged |
| diffusion | SPD |
| current | nonzero |
| scale-freedom | `ω` tracks the dissipative rate exactly at 0.25× and 4× |

---

## 5. Defect 4 — C_phi on the official path, with the profiled U.20 derivative

### 5.1 What was wrong

Two separate problems. The covariance assembler existed but the official record
builder never called it, so the claimed complete `C_φ` was not
production-complete. And `pseudo_true_log_beta` maximised over `log β` alone
while holding the centre at zero and deriving the drift from the true
diffusion — not the U.20 production derivative, which must profile the actual
temporal likelihood nuisance.

### 5.2 The profiled nuisance vector

The production locked fit maximises exactly

```text
θ = (log β, μx, μy, d_chol₀, d_chol₁, d_chol₂, ω)
```

in the T-stage 8.2 parameterisation, with `A Σ = D + Q`, `D` SPD from its
Cholesky parameters and `Q = ω J`. V4 profiles **that** vector. The log-beta
row is extracted only after the full 7-parameter system is solved.

The expected log likelihood gained an innovation **mean** term. Without it the
objective is blind to the centre, and a detector-offset calibration error would
appear to shift `log β`. At steady state, with `Δc = c_truth − c_model`:

```text
x̄ = (I − F_m + K C_m)⁻¹ K Δc
v̄ = Δc − C_m x̄
E[ℓ] = −½ ( log det S + tr(S⁻¹ Var v) + v̄ᵀ S⁻¹ v̄ + d log 2π )
```

`I − (F_m − K C_m)` is invertible because the closed-loop filter matrix is
stable. `Var v` comes from one discrete Lyapunov solve on the joint (true
latent, filter state) system. **No trajectory is generated anywhere in this
calculation.**

### 5.3 Option A — implicit differentiation

```text
dθ*/dφ = − (∂_θ E s)⁻¹ (∂_φ E s)     with   E s = ∂_θ L
```

Both blocks are second derivatives of a smooth closed-form function, so no
inner-optimiser noise enters. Differentiation happens in dimensionless θ
coordinates (`ThetaScaling`), since a step on `d_chol₁` of magnitude `e^{−39}`
is otherwise meaningless.

### 5.4 The perturbation side — a sign correction

V3 perturbed the **truth** and held `h_locked` fixed. The experimental
situation is the mirror image: the physics is whatever it is, Branch A
*measures* calibration primitives with error, and the analyst locks `H_A`
computed from the measured values. So φ moves the **analysis** side.

The magnitudes agree, so the propagated absolute σ is unaffected — but the sign
determines whether a shared calibration error cancels or adds in a cross-field
contrast, so the production path uses the analysis-side derivative. V3's
reported `+1` for stiffness is `−1` in production.

### 5.5 Analytic references

Each derived from the primitive map, not reused:

> `Σ_m = e^{−b} H_A⁻¹` is matched to `Σ_true`. With
> `H_A = K e^{φ₀} / (k_B T e^{φ₁})` this gives `b* = φ₁ − φ₀`.
> A detector offset is absorbed entirely by the centre:
> `μ* = μ_true + P⁻¹(b_det,true − b_det,A)`.

| Derivative | Exact | Computed | Error | Certified radius |
|---|---:|---:|---:|---:|
| `d log β*/d log k_A` | −1 | −1.000001672 | 1.7e−06 | 7.1e−06 |
| `d log β*/d log T_A` | +1 | +1.000001672 | 1.7e−06 | 7.1e−06 |
| `d log β*/d b_det,x` | 0 | 0.000000000 | 0 | 9.5e−07 |
| `d μ_x*/d b_det,x` | −1 | −0.999999925 | 7.5e−08 | 1.0e−06 |
| `d μ_y*/d b_det,x` | 0 | 0.000000000 | 0 | 3.2e−09 |

Every enclosure brackets its exact value.

### 5.6 Option B and the equivalence demonstration

`profiled_sensitivity_by_optimisation` locates `θ*(φ)` by maximising the *same*
expected likelihood over all seven parameters and differences it. It carries
its own certified radius from the located-maximum error, measured as
`δθ = H⁻¹ ∇L` at the point the optimiser actually returned — a standard
backward-to-forward error bound, not an assumed tolerance.

**All 28 entries of the 7×4 Jacobian have overlapping enclosures.** Option B's
radius runs up to 630× wider than option A's, which is why option A is the
production path.

### 5.7 Certified numerical error — the fixed 1e-5 band is gone

`CALIBRATION_NUMERICAL_RTOL = 1e-5` and `classify_against_ceiling` are deleted.
Each quantity now carries its own enclosure:

```text
radius = |J(h) − J(2h)|                        step consistency
       + ‖H⁻¹‖ ( ε_L/(h g) + ε_L/h² ·|J| )     roundoff through the solve
```

The first term is the *full* fine/coarse gap, three times the Richardson error
estimate for an `h²` scheme and so conservative. `ε_L`, the absolute evaluation
error of one expected-likelihood call, is **measured per record**: the
objective is smooth, so over a `1e-6` window its exact values lie on a
low-order polynomial, and whatever departs from a least-squares quadratic fit
is floating-point noise. The measured value here is `6.4e-14`.

Propagation to σ uses the fact that `x ↦ √(xᵀCx)` is a seminorm for PSD `C`:

```text
| σ(j + d) − σ(j) | ≤ σ(d) ,     sup over |d_k| ≤ r_k  ≤  √( rᵀ|C_φ| r )
```

with `|C_φ|` entrywise. That bound is rigorous given the Jacobian radius.

### 5.8 The qualification rule

```text
PASS       iff  u₊ ≤ c
FAIL       iff  u₋ >  c
UNRESOLVED otherwise
```

with T/U **inclusive** ceiling semantics — an exact value at `c` passes — and
`c` never widened. No enclosure at all is `UNRESOLVED`, which is fail-closed.
The unresolved region is this quantity's own certified error, not a fixed
fraction of the threshold: an enclosure of radius `1e-12` at `c(1−1e-7)` passes
while one of radius `1e-6` at the same point does not.

### 5.9 The official path

`ExperimentCalibration` is an experiment-level object, because shared
calibration primitives couple records and a record is therefore not an isolated
scalar inference object:

```text
C_b,cal = J_β C_φ J_βᵀ          all eight log-β endpoints jointly
C_d     = D C_b Dᵀ              contrasts, off the SAME matrix
```

`build_record_result` consumes it. The total error combines the two
contributions exactly once:

```text
Var_total = Var_cond + Var_cal
```

The conditional part is Branch-B observation noise at a fixed locked
calibration; the calibration part is Branch-A measurement error. They are
measured on physically separate apparatus and share no primitive, so the
declared model carries no cross term. Contrast conditional parts are
independent across records and add in quadrature; the calibration part arrives
already correlated from the joint matrix.

At the design point: `σ_abs = 6.265220e-03 ± 7.5e-07 → PASS` against 0.009;
`σ_contrast = 2.121327e-03 ± 1.5e-06 → PASS` against 0.003.

Verified end to end:

| Property | Result |
|---|---|
| purely shared standard, correlation of two endpoints | 1.000000000 |
| purely shared standard, contrast / absolute | 4.8e−08 (exact cancellation) |
| independent per-field errors, contrast / absolute | 1.414213523 vs √2 = 1.414213562 |
| `σ_contrast` vs `√(D C_b Dᵀ)` | agree to 1e−9 |

### 5.10 Bounded bias — missing is not zero

`BoundedBias.absolute_bound` used `dict.get(key, 0.0)`, so the *absence* of a
certification became a certification of **zero** — the strongest possible claim,
obtainable by supplying nothing. Every bound is now a `BiasEvidence` with
status `QUALIFIED` / `MISSING` / `INVALID`. `BiasEvidence.qualified(0.0)` is a
certified claim of zero and is distinguishable from `BiasEvidence.missing()`.
Missing bias evidence prevents complete support for both absolute endpoints
and contrasts, and a contrast bound still may not be inferred from two absolute
bounds (which would imply only 0.001, not 0.0005).

---

## 6. Defect 5 — the axial remainder's units

### What was wrong

`schur_nonlinear_remainder` returned `max |exact − linearised|` over the `vech`
entries: a **stiffness residual in N/m**. It was compared against

```python
#: Maximum admissible relative second-order Schur remainder (U-stage 5.4).
NONLINEAR_REMAINDER_CEILING = 1.0e-3
```

Dimensionally invalid. At the design point the remainder for a 5% axial
perturbation measures `2.6e-23 N/m`, so it passed by nineteen orders of
magnitude purely on the SI magnitude of the stiffness. Every physically
possible remainder passed.

### What V4 does

**Type it.** `NonlinearRemainder` carries a symmetric 2×2 matrix, a
`RemainderKind` and a declared unit. A raw unlabelled float is refused, and a
`NORMALISED` remainder may not claim `N/m`.

**Normalise it.** From U 5.4/5.8:

```text
E_K = K_eff^{−1/2} ΔK K_eff^{−1/2}
```

Because `H_eff = K_eff/(k_B T)` and `ΔH = ΔK/(k_B T)` share the same scalar,
`E_K` is *identically* the normalised thermal-Hessian residual
`H_eff^{−1/2} ΔH H_eff^{−1/2}` — the same object in either coordinate, which is
why no separate thermal form is carried. Its spectrum is the set of generalised
eigenvalues of `(ΔK, K_eff)`, so it is invariant under any congruence
`K → M K Mᵀ`, `ΔK → M ΔK Mᵀ` and under an overall rescaling. Verified to
2.9e−16.

**Propagate it into the existing budgets.** U gives the remainder no allowance
of its own. Its effect is a perturbation `H_A → H_A(I + E)` of the locked
comparison field, and that already has places to go:

| Impact | Derivation | Lands in |
|---|---|---|
| `log β` bias | locked-scale ML satisfies `tr(H_A Σ) = d`, so `b = log(d/(d+tr E))`, i.e. `\|tr E_K\|/d` | per-record absolute bounded bias (T.18 / U.22) |
| contrast bias | the two records' magnitudes, independently certified | contrast bounded bias |
| geometry | `G` shifts by the deviatoric part of `log(I+E)`, bounded by `‖E − (tr E/d)I‖_op` | T4 shape budget (`δ_G`) |
| centre | `m = √(δᵀH_Aδ)` scales as `√(1+E)` | relative enlargement `‖E‖_op/2` |

**Remove the standalone rule.** The `1e-3` constant is not traceable to a
dimensionally valid T/U requirement and is removed as a release predicate. The
only surviving axial constant is a **domain guard** at `‖E_K‖_op = 1`, with a
stated derivation: beyond it `K_eff + ΔK` need not remain positive definite, so
the linearisation whose remainder is being bounded has no meaning. That is a
domain condition, not a tolerance, and it cannot weaken any budget because the
budgets are checked downstream on the propagated impacts.

### Regressions

Zero explicit remainder qualifies when all else passes; a missing remainder is
refused; a 5× nominal stiffness remainder leaves the domain and exceeds the
bias budget by over 100×; an isotropic remainder lands in the scale budget and
not the geometry; a traceless remainder lands in the geometry budget and not
the scale; a coordinate-scaled equivalent remainder and an overall rescaling
both classify identically.

---

## 7. Defect 6 — cases must instantiate their declared worlds

### What was wrong

`POWER-CONDLIM` declared `condition=100.0` and `POWER-NOISEHI` declared
`noise_ratio=0.05`, but `run_power_case` called
`run_complete_experiment(seed_map, case.case_id, rep, frames)` with no
`spec_kw` at all. Both generated **nominal** records under a non-nominal name.
Several field-specific controls fell through the same way. And
`run_control_case` computed "support" from four raw statistics:

```python
if abs_ok and geo_ok and cen_ok and cur_ok:
    counts["support"] += 1
```

skipping the cross-field contrasts, stationarity, the diagnostic family, the
realized-field statuses and packet validity, comparing raw statistics where
calibrated upper limits are required, and never calling the verdict engine.

### What V4 does

**Typed registry.** `CaseConfig` has one explicitly named field per declarable
world property. `declared_fields()` returns those actually set.

**Central dispatcher.** `validation/dispatch.instantiate(case_id)` is the only
route from a case ID to a world. An unknown ID raises `InvalidValidationPlan` —
never a nominal run. A declared field no handler consumes **also** raises:

```text
InvalidValidationPlan: POWER-CONDLIM declares ['condition'] but no handler
consumes them; a declared world must be instantiated, not ignored
```

**Configuration digest.** Every result carries both the declared configuration
and the *measured* properties of the world actually generated — localisation
ratio, exposure fraction, condition number, `ω`, noise model, drift, per-field
betas — so a case that declared a world and built a nominal one is visible in
its own result.

**Verified instantiation.**

| Case | Declared | Measured in the generated world |
|---|---|---|
| `POWER-CONDLIM` | `κ₂ = 100` | `cond₂(H_eff) = 99.999999999`, nominal is 1.016 |
| `POWER-NOISEHI` | ratio 0.05 | 0.050000000, vs nominal 0.020 |
| `SIZE-NUIS-EXP` | exposure 0.1 | `t_exp` doubles |
| `CTL-FIELD-106` | `(1, 1.06, 1, 1)` | field 1 at 1.06, field 0 at 1.0 |
| `CTL-NOISE-HEAVY` | heavy tails | `noise_model = "heavy"` |
| `CTL-BLUR-MISMATCH` | 0.9 | generator exposure override set |

A meta-test runs over **every** registered case and asserts: the dispatcher has
an explicit handler, every declared parameter is consumed, the generated
configuration records them, and a declared event evaluator exists. A second
meta-test asserts no non-nominal runnable case has a no-op configuration
relative to nominal.

The conditioning case needed one numerical decision. A world constructed
*exactly at* `κ₂ = 100` was refused by the `cond₂ ≤ 100` qualification: the
symmetric eigensolver reports `cond₂` with a relative backward error of order
`n·ε·cond₂`, about 4e−13 at 100, and that alone pushed it over. The world is
now placed `1e-11` relatively inside. **The scientific limit is unchanged**;
this is a placement far below any physical resolution, and it stops a case
designed to sit at a limit from having its outcome decided by the rounding of
the limit's own evaluation.

**Authoritative event evaluation.** `validation/events.py` holds one versioned
evaluator, `e1a-v5-event-evaluator-v4`. Each case declares a typed
`ExpectedEvent`. `COMPLETE_SUPPORT` reads `outcome.classification` — which comes
from `CompleteResult.counts_as_complete_success`'s own verdict — and nothing
else. No raw statistic appears anywhere in the function. A replicate with
`absolute_contained = True` but no classification does not count.

Other cases target their own events explicitly: `REALIZATION_STATUS` with an
exact target status, `BLINDED_RECOVERY`, `REFUSAL_CODE`, `DISCREPANCY`,
`INVALID`, `NOT_EVALUABLE`, `FALSE_EQUIVALENCE`, `DIAGNOSTIC_REJECTION`.
`CALIBRATION_OUTPUT` and `DETERMINISTIC` raise rather than returning a boolean,
because they have no sampled pass/fail event.

**Drivers and honest NOT RUN.** Six drivers; three implemented in this build.
Cases routed to an unimplemented driver report `NOT RUN` with the reason, and
are never silently executed as nominal:

```text
multi_record_contrast   SIZE-CON-LO, SIZE-CON-HI
gate_boundary           SIZE-SHAPE-BD, SIZE-CENTRE-BD
finite_n_calibration    the seven CAL-* cases
```

---

## 8. Defect 7 — per-replicate reasons survive aggregation

`run_record` returned structured `Refusal` objects and `run_control_case` threw
them away, keeping six integer counters. An audit facing `nonevaluable = 11`
could not tell a bandwidth refusal from an optimiser non-convergence without
re-running the campaign.

Every replicate now retains:

```text
case_id, replicate, seed, classification,
reason_codes, reason_predicates, affected record or contrast,
optimizer_status, diagnostic_status, realization_status,
bandwidth_product, absolute_contained, blinded_error, configuration digest
```

`ReasonAggregate` adds classification counts, a reason-code histogram, a
reason-**predicate** histogram, joint reason combinations and an
affected-record histogram — while `replicates` keeps the raw records. The
summary is a convenience; the records are the evidence.

The predicate histogram matters: two failures sharing
`COMPUTATION_NOT_EVALUABLE` stay distinguishable as
`unique usable maximum established` versus `diagnostic family evaluable`.
Engineered specimens failing separately by bandwidth, optimiser, diagnostic
input, diffusion and conditioning are checked to remain distinguishable in the
aggregate.

---

## 9. Three further defects found during the repair

Not in the audit's list of seven.

### 9.1 The deterministic control battery was dead

`deterministic_controls()` called

```python
reduce_axial(plan.nominal_k3(0), plan.T_REF, temporal_qualified=False)
```

with a keyword the V3 fail-closed `AxialEvidence` repair had already removed.
Verified against the V3 freeze `86b95d4f`:

```text
V3 deterministic_controls FAILED: TypeError reduce_axial() got an
unexpected keyword argument 'temporal_qualified'
```

It raised before its first assertion, so **none** of V3's nine deterministic
controls ran. This is the same class as defect 3 — a stale call signature after
a fail-closed repair — in the deterministic route rather than the stochastic
one. All nine now run and pass, joined by `CTL-ETA-T-COV` for ten, and
`deterministic_coverage()` asserts every case the dispatcher routes to the
deterministic driver has a handler.

### 9.2 CTL-ETA-T-COV was itself a no-op case

The control compares two **covariance propagations** of the same primitives —
with and without the shared η/T covariance — so no generated world
distinguishes them. Declared as a 200-replicate stochastic support case, it ran
nominal records under a non-nominal name: precisely the defect-6 pattern, found
by the defect-6 meta-test. It is reclassified as an exact deterministic control
and given a real handler, which reports that omitting the shared covariance
drops a negative cross term and so *understates* the uncertainty:

```text
sigma_ratio (with shared covariance / without) = [0.327, 1.005, 0.317]
```

`CTL-AXIAL-MEMORY` is reclassified the same way. Both go from 200 sampled
replicates to one exact check. No threshold or acceptance criterion changes;
this is a strengthening, since sampling an exact computation 200 times adds
nothing.

### 9.3 Empty-set `all()` returned a pass

```python
return all(s <= SIGMA_CAL_ABS_MAX for s in sds), sds
```

`all(())` is `True`, so `absolute_qualification([])`,
`contrast_qualification(C, [])` and `bias_qualification([], [])` each returned a
**pass** from no evidence — supplying nothing was the strongest possible
evidence. All three now refuse, as does an empty diagnostic family.

---

## 10. Systematic fail-open search

Eight pattern classes scanned across all of `e1a_v5/`. 34 occurrences found in
6 classes; every one classified.

| Pattern | Hits | Disposition |
|---|---:|---|
| `.get(..., <pass-reading default>)` | 8 | 6 are integer histogram counters (benign); 2 were the docstrings describing the V3 defect. The one material case, `BoundedBias`, is repaired. |
| dict keyed by scientific identity | 3 | `CASES_BY_ID` (static registry, uniqueness tested); `diagnostics` (duplicates detected *before* the map is consulted); `run.build_contrast_results` — **repaired** to group into lists so a duplicate cannot disappear here either. |
| `all(...)` / `any(...)` over data | 13 | 3 material empty-set fail-opens repaired (§9.3) plus the empty diagnostic family; the rest are finiteness guards where `all(())` on an empty matrix is correct. |
| `or <literal>` fallback | 1 | **repaired** — `max(...) or 1.0` in the calibration variance clamp turned a degenerate `C_φ` into an absolute test. |
| `max(1.0, .)` absolute scale | 7 | 5 are comments documenting the V3 repair; 2 are `optimize.py` on genuinely dimensionless optimiser coordinates. **SAFE, unchanged.** |
| bare `except:` | 0 | — |
| NaN comparison | 2 | both explicit `isnan` guards that refuse. |
| default-zero bias | 0 | — |

A test enforces the inventory, scanning **tokens** rather than raw text so the
docstrings that describe a repaired pattern are not themselves flagged: no
load-bearing `max(1.0, .)` outside `optimize.py`, and no `dict.get` with a
pass-reading default anywhere.

### Case-dispatch search

The `if/elif` chain over case IDs inside `run_control_case` is gone. There is
one typed dispatcher, no default branch that generates a nominal world, and the
meta-test proves no `CaseConfig` field is ever written and not read. All 51
registered cases instantiate; the machine-readable plan and the implementation
are checked to correspond on every case ID, purpose, replicate count,
expectation, per-family total and all six identities.

---

## 11. Identities and seeds

```text
analysis procedure   a687ea512a33561a8630d9c0b60e486b49bf72fb59242f0a2fbaa199141d1498
synthetic generator  a734b184f7169ee715005992171af69f2b9918c4c71bc299901410fb660ca7a9
validation procedure 305f4c7fbf25e1b92008b4d1a82fa684830c855711a7f2369de81135656e415c
packet schema        b6e1e9b276ee8039e9784baa6d60e6cc3edcdd064956a0a5feaf783c348cd9f9
seed map             1357c19ea90a9912da088db68569311d8b7caf7ccc309bf28c7c818f8999e633
gate semantics       694f0769f547ebccdc13d664041ccc10f601d2042a264552081a9aea023c59ac
```

The validation identity binds, hierarchically over the analysis, generator,
seed-map, gate and packet identities, the four modules that decide what a
result *means*: `evidence.py`, `diagnostics.py`, `validation/dispatch.py` and
`validation/events.py`, alongside the runner, harness, cases, plan, seeds and
identity rule. Under V3 a change to any of those four could alter every
validation outcome without moving the identity.

Seeds use a new root `e1a_v5/validation/v4/2026-10-06`:

| Family | Role |
|---|---|
| `critical-calibration-v4` | confirmatory, frozen, **not executed** |
| `size-validation-v4` | confirmatory, frozen, **not executed** |
| `diagnostic-validation-v4` | confirmatory, frozen, **not executed** |
| `complete-power-v4` | confirmatory, frozen, **not executed** |
| `negative-controls-v4` | confirmatory, frozen, **not executed** |
| `engineering-v4` | implementation and smoke draws only |

Each confirmatory family is checked disjoint from both its V3 and its V2
stream, whose outcomes have been inspected. `engineering-v4` is checked
disjoint from all five: every draw made during this repair came from it, so no
future confirmatory stream has been consumed or inspected.

---

## 12. What was run, and what was not

### Deterministic verification

| Suite | Checks |
|---|---:|
| `test_e1a_v5_kernel.py` | 83 |
| `test_e1a_v5_procedure.py` | 182 |
| `test_e1a_v5_v3_repairs.py` | 170 |
| `test_e1a_v5_v4_repairs.py` | 470 |
| **total** | **905**, 0 failures |

The V2 and V3 suites were ported to the V4 API where the V4 semantics changed;
every surviving assertion keeps its scientific content. The V3 suite's
sensitivity assertions flipped sign, for the reason given in §5.4.

Preserved and still protected by regression, per the brief's §60: the
innovations likelihood, the shutter integration, the V2 Riccati convergence
repair, the profile-fit failure semantics, and the `eigh2` and `lu_solve`
SI-scale repairs.

### Engineering smoke — NOT a validation result

`docs/e1a/e1a_v5_v4_smoke_results.json`, 400 frames per record, drawn entirely
from `engineering-v4`. 400 frames is **0.015%** of the T.23 information target,
so every statistic in it is at small-N noise.

| Check | Result |
|---|---|
| ten deterministic controls | all pass |
| one complete experiment, no calibration | `INVALID_MEASUREMENT_OR_MODEL`, 0/8 gates, `evidence_ok = False` |
| same, with a labelled synthetic fixture | `evidence_ok = True`, diagnostic family `CALIBRATED` and not rejecting |
| `CTL-CURRENT` through the repaired route | runs; per-replicate reasons and measured world retained |
| official calibration | `σ_abs = 6.265e-03 ± 7.5e-07 → PASS` |

The uncalibrated result is the **correct** V4 state: with no finite-N critical
value, no calibrated gate limit and no calibrated diagnostic family, nothing
may pass. The fixture run exists to show the conjunction is reachable.

Information per frame measures 0.145 across 500–32,000 frames, against V3's
0.148 and V2's 0.150, so the repairs did not change the statistical content of
the likelihood and the ~2.7×10⁶-frame record requirement is unchanged.

### Not run

```text
finite-N critical calibration     NOT RUN FOR V4
false-equivalence validation      NOT RUN FOR V4
diagnostic size validation        NOT RUN FOR V4
complete power validation         NOT RUN FOR V4
full campaign                     NOT RUN
real optical-trap experiment      NOT RUN
```

---

## 13. Remaining V blockers

| Blocker | State |
|---|---|
| continuous nuisance-domain coverage | **OPEN**. Completing `C_φ` on the official path does not prove it. The coverage claim quantifies over a continuum of nuisance values; what V4 establishes is that the propagation is correct, dimensionally valid and certified at the points evaluated. |
| finite-N critical calibration | not run; V4 audit must come first |
| false-equivalence, diagnostic-size and complete-power campaigns | not run |
| multi-record contrast driver | not implemented; two size cases report NOT RUN |
| geometry/centre gate-boundary driver | not implemented; two size cases report NOT RUN |
| full-campaign resource requirement | OPEN — ~1.9×10⁵ core-hours at the measured information rate |
| baseline §14.3 sign defect | **still owed** before W-stage authority freeze. `ΔJ_prob = E` needs pre-minus-post while `Δs_sys = −k_B E` three lines later needs post-minus-pre, and since `s_sys = k_B J_prob + const` they must share one orientation. Not repaired here; this stage modifies no authority. |
| CI coverage | the e1a_v5 suites are not in `.github/workflows/tests.yml`, as the V2 and V3 suites were not. Out of scope for a bounded repair of a non-cleared candidate procedure; flagged for the auditor. |

---

## 14. Status

```text
V4 CORE PROCEDURE:   REPAIRED AND FROZEN — INDEPENDENT AUDIT REQUIRED
V RELEASE:           NON-RELEASE — VALIDATION NOT YET COMPLETE
W-STAGE:             BLOCKED
```

Nothing here adopts the candidate procedure, authorises physical data
collection, authorises an official campaign, or authorises unblinding.
