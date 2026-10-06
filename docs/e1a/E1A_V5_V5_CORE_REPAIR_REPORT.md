# E1a v5 — V-stage procedure version 5 core repair

```text
STATUS:                  V5 CORE PROCEDURE REPAIRED AND FROZEN
                         — INDEPENDENT AUDIT REQUIRED
V RELEASE:               NON-RELEASE — VALIDATION NOT YET COMPLETE
PROCEDURE VERSION:       5  (v1 superseded; v2 AUDIT FAILED;
                             v3 NOT CLEARED; v4 NOT CLEARED)
REPAIR STARTING COMMIT:  c56aa6338995414a329353af7c5ccdc86c7875ed
AUTHORITY MODIFIED:      NO
OLD e1a_v4 PACKAGE/SEAL: UNTOUCHED
REAL DATA USED:          NO
EXECUTION AUTHORISED:    FALSE
W-STAGE:                 BLOCKED
```

> **Naming.** "V5" throughout means the **V-stage procedure version**. The
> Python package is `e1a_v5/` and has carried that name since procedure
> version 1; the two are unrelated.

The independent V4 audit returned **V4 CORE IMPLEMENTATION: NOT CLEARED** with
five material blockers and a fail-open search that was also not cleared. All
five are repaired here, together with two further defects of the same classes
that surfaced while repairing them.

The mechanical contract is
[`e1a_v5_validation_plan.json`](e1a_v5_validation_plan.json), which is now the
**source of truth** the deterministic suite compares the implementation
against. Any mismatch between this document and that file is an integrity
failure, not permission to choose one.

---

## 1. Blocker 1 — the numerical sensitivity enclosure was not certified

### What was wrong

V4 built its "certified" enclosure from two ingredients, neither of which is a
bound:

1. **fine/coarse finite-difference agreement.** Agreement between the
   derivative at step `h` and at step `2h` constrains the *difference* of
   their truncation remainders. It says nothing about either remainder.
2. **a nine-point least-squares smoothness residual.** A residual at sampled
   points bounds the scatter at those points. No theorem converts it into a
   bound on an unobserved higher derivative between them.

The audit rejected this, correctly.

### A construction that defeats the V4 heuristic

Take the entire function

```text
f(x) = x + (h² / 2π) · sin(2π x / h)
```

Its central difference at step `h` samples the sine at multiples of its own
period, so the oscillation cancels **exactly** and the difference returns `1`.
At step `2h` the same thing happens. The two agree to machine precision — while
the true derivative at the origin is `1 + h`.

Measured at `h = 1e-3`:

| Quantity | Value |
|---|---|
| fine central difference | 1.000000000000 |
| coarse central difference | 1.000000000000 |
| fine − coarse | < 1e-12 |
| exact derivative | 1.001 |
| **V4 radius (≈ \|fine − coarse\|)** | **~1e-16** |
| **actual error** | **1e-3** |

The V4 enclosure understates the error by thirteen orders of magnitude. This
is a regression in the V5 suite.

### What V5 does: remove the estimate, not patch it

**Truncation error is exactly zero.** Derivatives are evaluated by
**hyper-dual arithmetic**:

```text
x = v + d₁ε₁ + d₂ε₂ + d₁₂ε₁ε₂ ,    ε₁² = ε₂² = 0
```

Seeding `ε₁` along one coordinate and `ε₂` along another makes the `d₁₂`
component of the result the exact mixed second partial derivative of the
*algorithm*. There is no step size, so there is no remainder term to bound.

**Floating point is enclosed.** Each hyper-dual component is an **interval**,
outward rounded after every operation. IEEE-754 gives correctly-rounded
`+ − × ÷` and `sqrt` within half an ulp, so a one-ulp outward widening is
sound; `log` and `exp` are not guaranteed correctly rounded by the platform
libm and are widened by two ulps. The returned interval therefore encloses the
exact real result of the algorithm.

**Fixed points carry explicit residual bounds.** The Riccati map contracts by
`‖F_cl‖²`, so a one-step residual `r` places the exact fixed point within
`r / (1 − ‖F_cl‖²)`. That bound is computed per evaluation and reported.

**The linear solve carries a certified bound.** For `F_θ x = −F_φ`, the
residual is enclosed in interval arithmetic and amplified by
`‖F_θ⁻¹‖ ≤ 1/λ_min`, with `λ_min` obtained by Weyl from the computed
eigenvalues less the backward error less the interval perturbation. If that
quantity is not certifiably positive the sensitivity refuses rather than
returning a number.

### One implementation, cross-checked against the cleared core

The generic kernel in `e1a_v5/certified.py` runs at float and at
interval-hyper-dual from the **same source**. At float it reproduces
`e1a_v5/numerics.py` and `e1a_v5/observation.py` **bit for bit** — every
state-space block and the expected log likelihood agree to a relative
difference of exactly `0.0`. That is what entitles the interval evaluation to
stand in for the cleared numerical core rather than quietly replacing it, and
it is a regression.

### Result

| Quantity | V4 | V5 |
|---|---|---|
| `d log β*/d log k_A`, error vs exact `−1` | 1.7e−06 | **4.9e−11** |
| `d log β*/d log T_A`, error vs exact `+1` | 1.7e−06 | **4.8e−11** |
| basis of the enclosure | agreement + fitted residual | truncation-free + interval + residual bounds |
| `σ_abs` enclosure half-width | — | **8.5e−08** |
| margin to the 0.009 ceiling | — | 2.7e−03 |

The enclosure resolves the ceiling with roughly four orders of magnitude of
headroom, so the qualification is `PASS` on a genuinely certified basis.

### The three-way rule, and what happens without certification

```text
PASS       iff  u₊ ≤ c
FAIL       iff  u₋ >  c
UNRESOLVED otherwise
```

with T/U **inclusive** ceiling semantics and `c` never widened. Two
fail-closed paths: no enclosure at all is `UNRESOLVED`, and
`ExperimentCalibration.absolute_qualification` returns `UNRESOLVED` whenever
**any** record's sensitivity is not certified, so an uncertified calibration
cannot qualify at all.

### The profiled nuisance vector is preserved

```text
θ = (log β, μx, μy, d_chol₀, d_chol₁, d_chol₂, ω)
```

exactly the production locked-fit vector in the T 8.2 parameterisation. The
log-beta row is extracted only after the full seven-parameter system is
solved. There is no regression to a scalar log-β-only pseudo-true fit.

### What was deleted

`profiled_sensitivity` — the finite-difference production sensitivity — is
**removed from the module**, so no caller can reach it. The
profiled-optimisation route survives as a cross-check and is explicitly
`certified = False`; it carries a backward-error bound on its located maximum,
which is a real bound on *that* step but not on truncation, so no
qualification may be taken from it.

---

## 2. Blocker 2 — the axial remainder's finite effects

### What was wrong

V4 normalised the remainder correctly to `E_K = K_eff^{−1/2} ΔK K_eff^{−1/2}`
but then reported **first-order** effects: `|tr E|/d` for the scale and
`‖E − (tr E/d)I‖_op` for the geometry. Those are the leading terms, not the
finite effects, and the audit's counterexamples show the difference is
decisive exactly at the budget boundary.

### The auditor's counterexamples, reproduced

**Scale.** `E = −0.0004999 · I`:

| | value | 0.0005 budget |
|---|---|---|
| V4 first order `\|tr E\|/d` | 0.000499900000 | **PASS** |
| **exact finite effect** | **0.000500024992** | **FAIL** |

The audit reported `~0.00050002499`. Reproduced to 1e−11.

**Geometry.** `E = diag(+0.048752, −0.048752)`:

| | value | `log 1.05` budget |
|---|---|---|
| V4 first order `‖E − (tr E/d)I‖_op` | 0.048752000000 | **PASS** |
| **exact finite effect** | **0.048790679067** | **FAIL** |
| (`log 1.05` = 0.048790164169) | | |

Both now fail, as they must.

### The exact finite effects, derived

**Scale.** The locked analysis fixes the shape of the latent covariance to
`H_A⁻¹` and fits only the scale, so the pseudo-true `b` maximises

```text
E[ℓ] = −½ ( −d·b + log det M + e^b · tr(M⁻¹ Σ_true) + d log 2π ) ,   M = H_A⁻¹
```

Setting the derivative to zero gives `b* = log d − log tr(H_A Σ_true)`. With
`H_A = K_eff/(k_B T)`, `Σ_true = k_B T K_true⁻¹` and
`K_true = K_eff^{1/2}(I+E)K_eff^{1/2}`, cyclicity collapses the trace:

```text
tr(H_A Σ_true) = tr(K_eff K_true⁻¹) = tr((I+E)⁻¹)
```

so

```text
b* = log d − log tr((I + E)⁻¹)                       EXACT, FINITE
```

First order this is `tr(E)/d`, which is what V4 used. The orientation is the
experimental one: `K_eff` is what Branch A reports and locks, `K_true` is the
physical field, `E` is the certified residual by which the reported Schur
complement misses it.

**Geometry.** T4 evaluates `G = ‖log M − (log det M / d) I‖_op` with `M`
similar to `H_A Σ_B`. Under the remainder `H_A Σ_true = K_eff K_true⁻¹` is
similar to `(I+E)⁻¹`, whose logarithm has eigenvalues `−log(1+λᵢ(E))`, so

```text
G = maxᵢ | log(1+λᵢ) − mean_j log(1+λⱼ) |            EXACT, FINITE
```

evaluated through the actual matrix logarithm the downstream statistic uses.

### Qualification is over the whole certified set

A single evaluated witness qualifies nothing. The admissible set is declared
as a spectral ball `𝓔 = {E = Eᵀ : ‖E‖_op ≤ ρ}` and every effect is taken as a
**supremum in closed form**:

| Effect | Supremum over the ball | Derivation |
|---|---|---|
| scale | `−log(1−ρ)` | `b*` is strictly increasing in each `λᵢ`, so its range is `[log(1−ρ), log(1+ρ)]` |
| geometry | `(d−1)/d · log((1+ρ)/(1−ρ))`; for `d=2`, `artanh ρ` | the spread of `gᵢ = log(1+λᵢ)` is maximised with one eigenvalue at `+ρ` and the rest at `−ρ` |
| centre | `√(1+ρ)` | `m = √(δᵀH_Aδ)` scales as `√(1+λ)` |
| rates | `1+ρ` | `A = K/γ`, so every relaxation rate carries `1+λ` |

A regression checks that the supremum dominates every sampled member of the
set at several radii.

### The set itself is certified, not sampled

The exact second-order Schur remainder has the closed form

```text
R = ( −u²S + uT − D ) / ( κ(1+u) ) ,
S = bbᵀ,  T = b·dbᵀ + db·bᵀ,  D = db·dbᵀ,  u = dκ/κ
```

obtained by subtracting the (U.A10) linearisation from
`−(b+db)(b+db)ᵀ/(κ+dκ)` and collecting terms. Submultiplicativity and the
triangle inequality give

```text
‖R‖ ≤ ( u²‖b‖² + 2u‖b‖·δ_b + δ_b² ) / ( κ(1−u) ) ,      ρ = ‖R‖ / λ_min(K_eff)
```

Every step is an inequality, so this bounds the whole primitive uncertainty
region rather than sampling it. At the design point, 3σ of the declared
primitive covariance gives `ρ = 1.33e−04`, and a regression checks that `ρ`
dominates the exact remainder of all 27 sampled corner perturbations.

### Routing into the existing budgets — and what is *not* routed

| Effect | Lands in |
|---|---|
| exact scale | the per-record absolute bounded bias (T.18 / U.22, 0.0005) |
| exact contrast | the contrast bounded bias, from **both** records' certified sets |
| exact geometry | the T4 shape budget (`δ_G`), as a limit enlargement |
| centre | a **multiplicative** factor on the centre limit |
| rates | the exposure, bandwidth and localisation envelopes |

**No new axial allowance.** And V4's additive centre enlargement is removed:
the remainder perturbs `H_A` but does **not** translate the trap, so `δ` is
unchanged and the effect on `m = √(δᵀH_Aδ)` is purely multiplicative. Applying
an additive enlargement misrepresented the model.

One instructive regression: a **traceless** `E` has zero first-order scale
effect but a nonzero exact one — at `E = diag(+0.02, −0.02)` the exact scale
effect is `4.0e−04`, which the first-order quantity reports as zero.

### What was deleted

`axial_remainder_bias`, which evaluated one proportional 5% perturbation whose
trace nearly cancelled and used its first-order scale effect as the
qualification.

---

## 3. Blocker 3 — a raw statistic could become a calibrated limit

### What was wrong

```python
GateLimit.calibrated(statistic=0.0, limit=0.0, identity="arbitrary")
# -> status CALIBRATED, usable True, passes(DELTA_G) True
```

A bare non-empty string was accepted as proof of calibration. A string carries
no gate family, no procedure version, no calibration stream, no coverage
target and no domain of applicability, so nothing about it could be checked —
and the caller supplied the limit directly, so a raw zero statistic became a
passing calibrated upper limit.

### What V5 does

`GateLimit.calibrated` is **deleted**. A limit can only be built from a typed
artifact:

```text
CalibratedGateProcedure
    family                 GateFamily enum, not a string
    procedure_version      must match the live V-stage procedure version
    procedure_identity     the frozen validation-procedure identity
    calibration_identity   which stream and how many replicates produced it
    coverage_target        the one-sided coverage the radius was calibrated to
    domain_identity        the nuisance/domain envelope it applies within
    radius                 the calibrated confidence radius
    status                 UNCALIBRATED / CALIBRATED / INVALID
    fixture_only           test-only flag, refused in production
```

and

```text
limit = statistic + procedure.radius        always
```

There is no constructor that accepts a limit, so `upper_limit = raw_statistic`
cannot be expressed. `GateLimit.from_procedure` additionally checks the gate
family, the procedure version, the domain identity, the calibration status,
the provenance strings, the radius sign and the coverage target, and refuses
a fixture outside test mode.

### Regressions

Eleven injection attempts, each required to yield no calibrated gate: an
arbitrary string identity (now unexpressible), no procedure at all, wrong gate
family, wrong procedure version, wrong nuisance domain, uncalibrated status,
missing calibration identity, missing procedure identity, missing domain
identity, negative radius, impossible coverage target, and a synthetic fixture
in production mode. Enlarging or scaling an unusable limit leaves it unusable.

### Live V5 state

Finite-N calibration has **not** run, so there is no calibrated procedure for
any family and `shape`, `centre`, `stationarity` and `current` are all
`UNCALIBRATED`. Complete support is therefore unavailable outside explicitly
marked fixtures — which is the correct state of the procedure.

---

## 4. Blocker 4 — observation qualification now enforces T 15.2

### What was wrong

`build_record_result` set `observation_valid=True` unconditionally for every
synthetic record. `CTL-NOISE-HI` generates a localisation ratio of **0.25**,
five times the T.23 ceiling, and was still marked observation-valid. The
control's entire scientific purpose is that such a record must not enter
complete support, so the flag defeated the control.

### What V5 does

`observation.qualify_observation` evaluates every T/U observation requirement
per record, from the **fitted** model, which is what the analysis can actually
see:

```text
R_obs positive definite
P invertible
instantaneous localisation ratio  ≤ 0.05      (T.23 / T 15.2)
t_exp / tau_fast                  ≤ 0.1
||B||₂ dt                         ≤ 0.2
0 ≤ t_exp ≤ dt
noise model in the qualified Gaussian set
```

The ratio is `λ_max(Σ^{−1/2} R_obs Σ^{−1/2})`, T's own definition, not a trace
substitute. Each quantity is enlarged by the certified axial **rate factor**
before comparison, and a quantity whose enclosure straddles its ceiling does
**not** pass: the record is not demonstrated to lie inside the envelope.
Semantics are inclusive, so an exact value at the ceiling passes.

`observation_valid` now comes from that function and from nowhere else. A
regression asserts the record builder contains no executable
`observation_valid=True`.

### Measured

| Case | generated ratio | observation_valid |
|---|---:|---|
| nominal | 0.020 | **True** |
| ratio target 0.049999 | 0.049999 | **True** |
| ratio target 0.05 (exactly at the ceiling) | 0.050000 | **True** |
| ratio target 0.050001 | 0.050001 | **False** |
| `CTL-NOISE-HI` | 0.250 | **False** |

In the engineering smoke, all eight `CTL-NOISE-HI` records are
observation-invalid and the experiment cannot reach complete support.

---

## 5. Blocker 5 — the two weakened controls are restored

### What was wrong

V4 reclassified `CTL-ETA-T-COV` and `CTL-AXIAL-MEMORY` from 200 stochastic
replicates each to one deterministic check, while
`e1a_v5_validation_plan.json` continued to require 200. The V4 meta-test
compared the case **registry** to the **dispatcher** — both of them code — so
it could not see the divergence and passed. The audit determined that both
controls are still required; that determination is controlling here and
neither control is weakened.

### `CTL-AXIAL-MEMORY` — an actual hidden-memory world

V4 set `temporal_qualified = False`, which exercises the refusal path and not
the physics. V5 generates from a full 3D Gaussian Ornstein–Uhlenbeck process
and observes only its lateral coordinates through the declared camera model:

```text
A₃ = Γ⁻¹K⁽³⁾ ,  Σ₃ = k_B T (K⁽³⁾)⁻¹
```

with `K⁽³⁾` built so its **Schur complement is exactly the nominal lateral
field**, chosen prospectively at coupling 0.15 and a soft axial mode
(`k_z = 0.08 k_ref`).

**The witness, established before any replicate is generated:**

| Property | Measured |
|---|---|
| `K⁽³⁾` positive definite | yes |
| Schur complement valid | yes |
| lateral marginal `= k_B T K_eff⁻¹` | relative error **1.5e−16** |
| `cond₂(K_eff)` | 1.00 |
| **Chapman–Kolmogorov residual at τ_slow/4** | **9.3e−02** |
| at τ_slow/2 | 5.7e−02 |
| at τ_slow | 2.1e−02 |

The witness is exact and needs no fitting. Every stationary 2D
Ornstein–Uhlenbeck process satisfies

```text
C(2τ) = C(τ) Σ⁻¹ C(τ)
```

for every `τ` and **every** admissible `A`, because `C(τ) = e^{−Aτ}Σ`. A
nonzero residual therefore proves that **no** 2D Markov generator reproduces
the observed lag structure. With the coupling set to zero the residual drops
to `< 1e−15`, confirming the witness measures the coupling and not a numerical
artefact.

The generated records then run through the **ordinary production pipeline** —
the same estimator, gates and diagnostics. Only the generator differs, which
is what makes this a full-pipeline control.

### `CTL-ETA-T-COV` — a full-pipeline covariance misspecification

The stiffness standard is realised by equipartition against a measured
temperature, so an error in the temperature standard enters the reported
stiffness as well as the explicit `−H dT/T` term: they share one variable and
are positively correlated (declared ρ = 0.7). The misspecified alternative
omits exactly that declaration and treats them as independent.

Because `d log β*/d log k_A = −1` and `d log β*/d log T_A = +1`, the correct
variance carries `−2ρσ_kσ_T`. Measured at the design point:

```text
sigma_abs, correct shared model   5.554e-03
sigma_abs, omitted covariance     6.265e-03
ratio                             1.128
```

So at this design point the omission **overstates** the uncertainty by 12.8%.

**V4's assertion that "omitting the shared η/T covariance always understates
the uncertainty" is removed.** It was never established, V4's own exact check
produced ratios `0.327 / 1.005 / 0.317` that contradict a universal direction,
and the design point measured here goes the other way. A regression asserts no
executable code in the validation layer asserts any direction.

### A plan ambiguity, reported rather than resolved downward

The frozen plan's expectation for `CTL-ETA-T-COV` reads **"coverage consequence
detected"**, which does not name a per-replicate event. Per the brief's
instruction not to silently select a weaker event, the exact ambiguity is
recorded here and in the JSON contract:

- The control family's standard event — complete support, with a
  Clopper–Pearson upper bound on false support — is used, because it is the
  **stronger** reading for a misspecification that could narrow intervals.
- At this design point the misspecification *widens* them, so that bound is
  not the binding consequence; the binding consequence is a coverage and power
  shift which the plan does not quantify.
- The coverage consequence is therefore **measured and recorded in every
  result** (both σ values and their ratio) rather than reduced to a pass/fail.

This is flagged for the auditor. No threshold is invented.

### The exact checks survive as supplementary references

Per the brief's §35, the deterministic battery keeps the useful exact
computations under names that cannot be mistaken for the controls:
`REF-ETA-T-COV-ALGEBRA`, `REF-AXIAL-REFUSAL` and `REF-AXIAL-MEMORY-WITNESS`.
A regression asserts that `CTL-ETA-T-COV` and `CTL-AXIAL-MEMORY` are **not**
in the deterministic battery and that all three references are.

---

## 6. Plan-to-code correspondence

`e1a_v5/validation/contract.py` parses
`docs/e1a/e1a_v5_validation_plan.json` and compares every registered case
field by field:

```text
case_id   purpose   replicates   seed_namespace   expected_event   family   detail
```

The plan is the source of truth. Any difference fails the deterministic suite:
there is no warning-only mode and no registry-as-source-of-truth fallback.
Regressions mutate each compared field in turn and require failure, and
separately require failure when a case is missing from either side or
duplicated on either side.

Running the checker against the V4 artefacts immediately produced **130
findings**: the V4 machine plan's `cases` block had never been regenerated, so
it still carried **V3** seed namespaces and had no `expected_event` field at
all. That is a second instance of the same defect class as blocker 5 and is
reported here.

---

## 7. Systematic fail-open re-audit

Twelve pattern classes scanned across all of `e1a_v5/`, token-aware so that
docstrings describing a repaired pattern are not themselves flagged. 104
occurrences in 8 classes, every one classified.

| Pattern | Hits | Disposition |
|---|---:|---|
| bare string grants scientific status | 0 | eliminated with `GateLimit.calibrated` |
| `.get(..., <pass-reading default>)` | 0 | — |
| raw statistic substituted for a limit | 0 | unexpressible by construction |
| bare `except:` | 0 | — |
| `all(...)` / `any(...)` over data | 16 | the three empty-set qualification fail-opens remain repaired; the rest are finiteness guards where `all(())` on an empty matrix is correct |
| missing becomes zero | 24 | all accumulator initialisations; the bias path uses `BiasEvidence`, where missing is `MISSING` |
| missing becomes true | 11 | all mode flags or **fail-closed** defaults (`requires_positive_se=True`, `synthetic=True`) |
| fixture in production | 23 | all the fixture-refusal machinery itself |
| dict keyed by scientific identity | 3 | `diagnostics` (duplicates detected before the map is consulted), `CASES_BY_ID` (static, uniqueness tested), `contract` — **repaired** to detect duplicates on both sides |
| NaN fall-through | 2 | both explicit `isnan` guards that refuse |
| nominal fallback | 23 | all named design-point values; the dispatcher has no nominal fallback branch |
| `max(1.0, .)` absolute scale | 2 | both in `optimize.py` on genuinely dimensionless optimiser coordinates. **SAFE, unchanged** |

**Two repairs** came out of this pass beyond the five blockers:

1. `ExperimentCalibration.absolute_qualification` and
   `contrast_qualification` never checked the `certified` flag, so the
   three-way rule could have been applied to an uncertified number. They now
   return `UNRESOLVED` unless **every** record's sensitivity is certified.
2. `check_correspondence` built maps keyed by case ID on both sides, so a
   duplicated ID would have vanished into its map and taken its mismatch with
   it. Duplicates are now detected before the maps are used.

### Validation-event search

Every `ExpectedEvent` has an explicit branch, and a regression asserts the
evaluator body references none of `GateLimit`, `gate_identity`, `DELTA_G`,
`DELTA_M`, `DELTA_A`, `DELTA_R_IRR`, `upper_limit` or `.limit`. No event can
fabricate calibrated support from a raw identity.

---

## 8. Per-replicate metadata

The V4 audit marked `optimizer`, `realization` and `bandwidth` per-replicate
metadata blank and non-blocking. They are now populated wherever the
underlying result exists:

- `optimizer_status` ∈ {`CONVERGED`, `NOT_CONVERGED`, `OPTIMIZER_FAILURE`,
  `NUMERICAL_FAILURE`, `NOT_ATTEMPTED`}, carried on every `RecordOutcome` and
  reduced to the least successful across the eight records;
- `realization_status`, or `MIXED:` plus the sorted statuses, or
  `NOT_APPLICABLE`;
- `bandwidth_product`, read from the measured configuration digest.

`NOT_APPLICABLE` is used rather than a blank where the quantity is not defined
for that replicate. Nothing is fabricated.

---

## 9. Identities and seeds

```text
analysis procedure   c10efe5109da9d8b3f4a6bd2ec0bb0f57e4718bed7ee5b763f06f646a92f4e75
synthetic generator  95b14ee4321f522c17fdded41c8e7521f327543caed82c753c536fb3209530a9
validation procedure 6be714826bd8d6d08125dd0f1b5a8f40cc71622f122e5cf351712a924953cba9
packet schema        b6e1e9b276ee8039e9784baa6d60e6cc3edcdd064956a0a5feaf783c348cd9f9
seed map             909521bc2204f714108aebeee0b882ad406cc2d537b226ea5221c8bbfe25a165
gate semantics       694f0769f547ebccdc13d664041ccc10f601d2042a264552081a9aea023c59ac
```

The validation identity now binds **every result-affecting module**, including
the six V5 additions: `certified.py` and `calibration.py` (the certified
sensitivity and its enclosure), `observation.py` (whether a record is inside
the declared T 15.2 envelope at all), `reduction.py` (the exact finite axial
effects), `generate.py` (the 3D hidden-memory world) and
`validation/contract.py` (the plan-to-code correspondence rule itself).

Seeds use a new root `e1a_v5/validation/v5/2026-10-06` with five confirmatory
families, each checked disjoint from the V4, V3 and V2 streams **and from
every engineering stream, past and present** — an earlier version's
engineering draws have been inspected just as thoroughly as its confirmatory
ones. `engineering-v5` carries every draw made during this repair.

The confirmatory families are **frozen and unconsumed**.

---

## 10. What was run, and what was not

### Deterministic verification

| Suite | Checks |
|---|---:|
| `test_e1a_v5_kernel.py` | 83 |
| `test_e1a_v5_procedure.py` | 184 |
| `test_e1a_v5_v3_repairs.py` | 175 |
| `test_e1a_v5_v4_repairs.py` | 482 |
| `test_e1a_v5_v5_repairs.py` | 243 |
| **total** | **1167**, 0 failures |

The V2, V3 and V4 suites were ported to the V5 API where the semantics
changed; every surviving assertion keeps its scientific content. Three V4
assertions changed meaning and are recorded as such: the axial remainder
predicate is now over the certified set rather than one witness; a traceless
remainder has a nonzero *exact* scale effect where the first-order quantity
reported zero; and fixture gate limits are built through the typed artifact
rather than a string identity.

Preserved and still protected by regression: the innovations likelihood, the
shutter integration, the direct-Gaussian vs innovations agreement, the V2
Riccati convergence repair, the profile-fit failure semantics, the `eigh2` and
`lu_solve` SI-scale repairs, the dimensionless current-control constructor and
its public route, the eight-record and contrast cardinality, `ScientificInterval`
validation, and the diagnostic-family contradiction handling.

### Engineering smoke — NOT a validation result

`docs/e1a/e1a_v5_v5_smoke_results.json`, drawn entirely from
`engineering-v5` at 300 frames per record — about 0.01% of the T.23
information target, so every statistic in it is at small-N noise.

| Check | Result |
|---|---|
| eleven deterministic controls and references | all pass |
| certified calibration, `fully_certified` | **true** |
| worst second-derivative enclosure | 1.3e−06 |
| Riccati fixed-point bound | 3.5e−10 |
| log-beta Jacobian row | exactly `(−1, +1, −1, 0, …)` |
| `σ_abs` | 5.554278e−03 ± 9.4e−08 → **PASS** |
| `σ_contrast` | 2.121320e−03 ± 1.9e−07 → **PASS** |
| certified remainder set radius | 1.33e−04 |
| `CTL-AXIAL-MEMORY` witness | marginal 1.5e−16, CK residual 9.3e−02 |
| `CTL-ETA-T-COV` consequence | ratio 1.128 (omission **overstates**) |
| `CTL-NOISE-HI` | 8/8 records observation-invalid |
| authoritative path, no calibration | `COMPUTATION_NOT_EVALUABLE` |

The uncalibrated result is the **correct** V5 state: with no finite-N critical
value, no calibrated gate procedure and no calibrated diagnostic family,
nothing may pass. A separate deterministic positive control, using fully
populated fixture evidence, confirms the conjunction does reach
`SUPPORTED_WITHIN_DECLARED_TOLERANCES`, so the repair is a gate and not a
wall.

### Not run

```text
finite-N critical calibration     NOT RUN
false-equivalence validation      NOT RUN
diagnostic size validation        NOT RUN
complete power validation         NOT RUN
the 200 replicates of either restored control   NOT RUN
full campaign                     NOT RUN
real optical-trap experiment      NOT RUN
```

---

## 11. Remaining V blockers

| Blocker | State |
|---|---|
| continuous nuisance-domain coverage | **OPEN**. V5 certifies the sensitivity's numerical error and makes the axial effects exact; neither establishes finite-N coverage uniform over the nuisance domain. No claim is made that this repair solves it. |
| finite-N critical calibration | not run; V5 audit must come first |
| false-equivalence, diagnostic-size and complete-power campaigns | not run |
| the two restored 200-replicate controls | frozen, not run |
| multi-record contrast driver | not implemented; two size cases report NOT RUN |
| geometry/centre gate-boundary driver | not implemented; two size cases report NOT RUN |
| full-campaign resource requirement | OPEN |
| `CTL-ETA-T-COV` plan wording | the expectation "coverage consequence detected" does not name a per-replicate event. Reported in §5, not silently resolved downward. |
| baseline §14.3 sign defect | **still owed** before W-stage authority freeze. `ΔJ_prob = E` needs pre-minus-post while `Δs_sys = −k_B E` three lines later needs post-minus-pre, and since `s_sys = k_B J_prob + const` they must share one orientation. Not repaired here; this stage modifies no authority. |
| CI integration | the `e1a_v5` suites are still absent from `.github/workflows/tests.yml`. Non-blocking for core repair, **blocking before W adoption**. |

---

## 12. Status

```text
V5 CORE PROCEDURE:   REPAIRED AND FROZEN — INDEPENDENT AUDIT REQUIRED
V RELEASE:           NON-RELEASE — VALIDATION NOT YET COMPLETE
W-STAGE:             BLOCKED
```

Nothing here adopts the candidate procedure, authorises physical data
collection, authorises an official campaign, or authorises unblinding.
