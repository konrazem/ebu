# E1a v4 — SYNTHETIC VALIDATION RESULTS

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

```
EXECUTION NOT PERFORMED — BLOCKED BEFORE THE FIRST RANDOM DRAW
RANDOM DRAWS 0   TRAJECTORIES 0   CALIBRATION NOT RUN   CAMPAIGN NOT RUN
```

The stochastic stage was authorised. It did **not** run. Two independent
pre-execution blockers were found by deterministic inspection of the frozen
package, before any RNG object was created:

| | blocker | class |
|---|---|---|
| **B1** | the four locked per-field calibration artifacts cannot cover any replicate whose `H_A` carries the declared `sigma_k` differential error — and the adopted design **requires** that error, because it is the declared mechanism by which `sigma_k` reaches G1 and G4 | frozen-package inconsistency |
| **B2** | the only rule-compliant alternative — one calibration artifact per replicate at that replicate's own measured geometry — costs **192 core-days**, 13.7 days at 14-way parallelism | infeasibility at the frozen `R_cal` |

There is no third reading. Either the analysed `H_A` carries the declared
Branch-A error, and B1 refuses it; or it does not, and the declared
`sigma_psi` and `sigma_k` scenarios — including **disposition G3's primary
release scenario** — have no effect on anything.

**This is not a scientific result about EBU.** No endpoint was evaluated, no
beta was estimated and no criterion passed or failed. The bridge
`K_theta = beta H_theta` is exactly as tested as it was before this task: not
yet tested synthetically at all.

`execution_authorised` was deliberately **left false**. See *Authorisation
disposition* below.

---

## Execution identity

Every frozen identity was verified mechanically before anything else, and none
of them moved during this task.

| item | value | status |
|---|---|---|
| authorisation commit | *none created* | see below |
| results commit | *none created* | no results exist |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | verified, unchanged |
| plan sha256 | `c9168b82c7420ca0edb92da0cb0624f0763958e95893900a35f27c3c97363ae9` | verified, unchanged |
| seed-map sha256 | `28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87` | verified, unchanged |
| analysis procedure identity | `af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4` | verified, unchanged |
| execution identity | `88037b9b2ac45bad0ab65151ab3f71897eb11bbd782ad09adfb9d0ca5d049837` | verified, unchanged |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | verified, unchanged |
| design sha256 | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | verified, unchanged |
| master seed | `13785910525869478477` | unchanged; **no seed was consumed** |

---

## B1 — the calibration geometry binding excludes the declared Branch-A error

### What the frozen package says

Three sources have to agree and do not.

**1. The plan freezes exactly four calibration artifacts**, one per declared
field, produced once from the `calibration` seed family at `R_cal = 50000`, and
**locked before validation data are evaluated**:

```
calibration/block1_theta0_circular.json     workflow:  CALIBRATION DATA
calibration/block1_theta1_power.json                -> fix artifacts and thresholds
calibration/block1_theta2_ellipse.json              -> lock artifact identities
calibration/block1_theta3_temperature.json          -> VALIDATION DATA
invariant: no validation result may change a calibration threshold
```

**2. `e1a_v4/calibration.py` binds each artifact to a geometry signature** that
is a SHA-256 of the **eigenvalue ratios** of `H_A` at twelve significant figures,
together with `n`:

```python
ratios = ",".join(f"{v / base:.12e}" for v in lam)
return hashlib.sha256(f"E1A-V4-GEOM|{ratios}|n={n}".encode("utf-8")).hexdigest()
```

`require_calibration` demands an exact match and otherwise raises
`CALIBRATION_IDENTITY_MISMATCH`.

**3. The adopted design requires the realised Branch-A error to move exactly
those eigenvalue ratios.** Design section 11:

| uncertainty | cross-field ratio | absolute beta | gates |
|---|:--:|:--:|:--:|
| `sigma_cm` | no — cancels exactly | yes, dominant | no |
| `sigma_k` mean part | yes | yes | no |
| **`sigma_k` differential part** | no | no | **yes (G1/G4)** |
| **`sigma_psi`** | negligible (2nd order) | negligible | **yes, dominant (G3)** |

The differential part of `sigma_k` reaches G1 and G4 **only** by changing the
eigenvalue ratios of `H_A`. That is the same quantity the signature hashes.

### Which components actually move the signature

Recomputed, not asserted. Fixed ±1σ offsets at the declared magnitudes, no draws:

| declared component | magnitude | moves the signature? |
|---|---|---|
| common-mode scale `sigma_cm` | 1.15% | **no** — the signature uses ratios, so scale cancels |
| thermometry `sigma_T` | 0.1 K | **no** — enters `H = H_U/(k_B T)` as a scale |
| orientation `sigma_psi` | 0.5° | **no** — a rotation leaves eigenvalues unchanged |
| per-mode stiffness `sigma_k` | 0.34% | **YES** |

Three of the four declared components are invariant, by the same scale- and
rotation-invariance that makes the gates well posed. The fourth is not, and
nothing in the frozen package handles it.

The sensitivity is not marginal. A perturbation of **one tenth of one sigma**
(0.034%) already produces a different signature, because the match is exact to
twelve significant figures.

### The consequence, demonstrated

```
require_calibration REFUSED:
  CALIBRATION_IDENTITY_MISMATCH for theta0_circular: artifact geometry signature
  d806758364fe1d5f... != analysed geometry 3f0414fc2d984c0c...
```

`p1_geometry` calls `require_calibration` before it computes anything, so P1
fails closed: **no gate decision, no beta, no complete pass**. The identical
artifact is accepted at the nominal geometry, which establishes that the
declared `sigma_k` error is the whole cause.

Every one of the eight cases declares `sigma_k = 0.34%`. C5 sweeps it over
`{0, 0.5%, 1%}`, so only its four `sigma_k = 0` cells would survive. **The
primary case C1 is blocked**, and with it the complete-pipeline ≥ 0.90 claim.

### Why the alternative reading fails too

If the analysis instead receives the **nominal** field — no realised Branch-A
error — then B1 disappears and something worse takes its place:

- `sigma_psi` enters **nothing**. It is absent from
  `sigma_fs = sqrt(sigma_k^2/m + (sigma_T/T)^2)`, absent from `delta_cross` and
  `delta_abs`, and absent from every half-width. Its only declared channel is G3,
  which requires a realised rotation.
- Therefore **disposition G3 becomes vacuous**: the primary release scenario at
  0.5°, the 0.0°/0.2° secondary scenarios and the 1.0° stress case would all
  produce bit-identical results, and the claim "the complete true-bridge ≥ 0.90
  validation claim is asserted at `sigma_psi = 0.5 degrees`" would assert nothing.
- The differential part of `sigma_k` would likewise stop reaching G1 and G4,
  contradicting design section 11 directly.

A further symptom of the same unresolved question: only C5 declares the
`branch_a_measurement` seed family. C1–C4, C6 and C7 declare `validation` alone
and C8 declares `blinded_scale_control`, yet C1's own G3 scenarios require
Branch-A draws. `FrozenSeedMap.stream` refuses cross-family reads by design, so
a faithful driver cannot supply C1 with the draws C1's declared scenario needs.

---

## B2 — per-replicate calibration is not affordable

Calibrating per replicate, at that replicate's own measured geometry, is the
only construction that satisfies both the design's plug-in requirement and the
implemented signature binding. Its cost was measured, not estimated.

The dominant term is `CalibrationArtifact.p_min_null`, a leave-one-out
recomputation of the min-p null that is **O(R²)** with a four-gate inner scan —
about 10¹⁰ float comparisons at `R_cal = 50000`.

| probe | measured | extrapolated to `R_cal = 50000` |
|---|---:|---:|
| `p_min_null`, R = 500 | 0.040 s | 401.8 s |
| `p_min_null`, R = 1000 | 0.167 s | 417.4 s |
| `p_min_null`, R = 2000 | 0.669 s | 418.2 s |
| `generate_block1_artifact`, R = 2000 | 0.102 s | 2.6 s (linear) |

The quadratic extrapolation is stable to **4.1%** across three probe sizes, so
the figure is a measurement rather than a guess.

```
one calibration artifact            ~  415 s
declared field-replicates           40,000      (C5 alone 19,200)
per-replicate calibration        16,601,328 core-seconds = 192.1 core-days
                                       13.7 days at 14-way parallelism
```

For scale, the **four locked artifacts** cost about 28 minutes in total, which is
entirely affordable. It is the per-replicate construction, forced by B1, that is
not.

Trajectory generation is *not* the obstacle. The declared Branch-B record is
`n_samples = 2,000,000` at `dt = 1.2e-4 s`; a measured pure-Python cost of
≈ 2.0–2.6 s per two-mode trajectory puts the whole generating load near one hour
at 14-way parallelism. The campaign is blocked by the calibration architecture,
not by its physics.

> Recorded as an open specification point, **not** a blocker: the plan does not
> state whether C5's twelve cells share Branch-B trajectories or draw fresh ones.
> That changes C5's cost by a factor of twelve and changes whether the twelve
> cells are statistically correlated.

---

## Per-case status

No case ran. Nothing below is a result, and none of it may be read as one.

| case | declared R | status |
|---|---:|---|
| C1 true-bridge complete pipeline | 300 | **NOT EXECUTED** — blocked by B1 |
| C2 geometry false rejection | 400 per field | **NOT EXECUTED** — blocked by B1 |
| C3 G5 block | 400 | **NOT EXECUTED** — blocked by B1 |
| C4 surrogate validity | 2000 | **NOT EXECUTED** — blocked by B1 |
| C5 plug-in Branch-A | 400 × 12 cells | **NOT EXECUTED** — blocked by B1 and B2 |
| C6 mode-resolution boundary | 400 × 3 rho | **NOT EXECUTED** — blocked by B1 |
| C7 false-bridge discrimination | 400 × 4 alternatives | **NOT EXECUTED** — blocked by B1 |
| C8 blinded scale control | 200 paired | **NOT EXECUTED** — blocked by B1 |

No calibration artifact was produced. No trajectory was generated. No
`beta_hat`, G1–G5, P1, P2, P3 or P4 value exists. Refusal accounting is
undefined because there were no replicates to account for.

## Final ten-point classification

**NOT EVALUATED.** `classify_campaign` was not called, and calling it would
require fabricating counts. A conjunctive rule with no observations does not
return a verdict — it has nothing to conjoin.

## Secondary orientation scenarios

`sigma_psi` = 0.0°, 0.2° and 1.0° — **NOT EXECUTED**, and separately: under the
no-realised-error reading they would be indistinguishable from the 0.5° primary,
which is part of B1 rather than a result.

---

## Static gates

All five static authority gates pass at the unchanged HEAD. **None of them
detects B1 or B2**, which is itself worth recording: the existing suites test
the calibration binding only against artifacts built at the analysed field's own
geometry, so the campaign-scale mismatch has no fixture.

| gate | passed | failed |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` | **113** | 0 |
| `test_e1a_v4.py` | **119** | 0 |
| `test_e1a_v4_preexec.py` | **93** | 0 |
| `test_e1a_v4_dispositions.py` | **64** | 0 |
| `test_e1a_v4_size_semantics.py` | **78** | 0 |

```
$ python3 -m e1a_v4.validation.runner --preflight-only
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : c9168b82c7420ca0edb92da0cb0624f0763958e95893900a35f27c3c97363ae9
  seed map sha256            : 28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87
  analysis procedure identity: af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4
  execution identity         : 88037b9b2ac45bad0ab65151ab3f71897eb11bbd782ad09adfb9d0ca5d049837
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)

$ git diff --check
[clean]
```

The probe that establishes B1 and B2 is committed and re-runnable:

```
$ python3 docs/e1a/e1a_v4_execution_feasibility_probe.py
```

It imports no RNG module, generates no trajectory and inspects no scientific
outcome. The only generator it supplies to frozen code is a fixed repeating
sequence used to measure arithmetic cost.

---

## Authorisation disposition

`execution_authorised` was **left false**, and no authorisation commit was
created. This departs from the instruction to flip it first, and the reason is
narrow: that flag is the single mechanism preventing an RNG object from being
constructed. Setting it true while the package is known to be unable to execute
would leave the repository fail-open — any later session running the official
command would begin drawing on a package whose primary case refuses.

The reviewer's authorisation is recorded here and is not withdrawn by this
report. Activating it is a one-line change to the plan, appropriate as the
first step of the correction stage below, once B1 has a decided answer.

Nothing was tuned, weakened, removed or reinterpreted. No criterion, margin,
alpha, threshold, replicate count, seed, case definition or classification rule
was touched. The frozen preregistration is byte-identical to the reviewed state.

---

## What would unblock execution

Recorded for the separately authorised correction stage. **Not implemented here** —
a correction plus execution inside one stage is exactly what the frozen protocol
forbids.

**B1 requires a decision, not a patch.** The plan must say explicitly which of
these is the adopted architecture:

1. **Per-replicate calibration** at the measured `H_A`. Matches design section 12
   qualification 3 ("calibration conditions on measured `H_A`") and keeps the
   `sigma_k`/`sigma_psi` channels to the gates intact. Requires B2 to be solved
   and requires the case→seed-family map to add `branch_a_measurement` wherever
   Branch-A error is realised.
2. **A declared calibration domain** replacing exact signature equality — an
   explicit tolerance on the eigenvalue ratios, with the size cost of
   calibrating at a neighbouring geometry quantified. This is a new
   approximation and needs its own prospective justification.
3. **Nominal-geometry analysis**, accepting that `sigma_psi` and the
   differential part of `sigma_k` reach nothing. This contradicts design
   section 11 and empties disposition G3; it is listed for completeness, not
   recommended.

**B2 has an implementation-only route.** `p_min_null` computes, for each draw
and gate, a leave-one-out count of `{d >= obs}`. That is obtainable from one
sort with tie counts in O(R log R) instead of O(R²), giving **exactly** the same
integers. At ~415 s → well under a second per artifact, per-replicate
calibration would fall to roughly 2.5 hours at 14-way parallelism. Because
`e1a_v4/calibration.py` is one of the twelve modules bound into the analysis
procedure identity, this is a **versioned correction stage** with re-derived
identities, not an edit. Seeds bind to the contract identity alone and would
not move. Exact reproduction of the current integers must be demonstrated, not
assumed.

---

## Interpretation

What this establishes:

> The frozen E1a v4 synthetic-validation package, as committed, cannot execute
> its own declared campaign. The obstruction is in the validation architecture —
> how the Block-1 null is bound to the measured Branch-A geometry — and was
> found before any random number was drawn.

What it does **not** establish, and must not be reported as:

```
anything about beta, K_theta = beta H_theta, or the Einstein-EBU bridge
any defect in the frozen physical foundation
any defect in P1, P2, P3, P4, the margins, the alphas or theta_cap
real apparatus validity
universal EBU
general thermodynamic identity outside stated assumptions
actor attribution
ecological usefulness
economic validity
Stage-B stability
```

The endpoints, margins and dispositions were reviewed and frozen on their own
terms and are untouched by this finding. What failed is the wiring between the
calibration artifact and the measured geometry it is supposed to describe.

A pre-execution blocker is the cheapest possible outcome of an execution gate.
It cost zero random draws and leaves every scientific rule intact and still
prospective, which a campaign run on a defective package would not have done.

---

## Post-hoc observations

```
POST-HOC — NOT PART OF THE FROZEN RELEASE TEST
```

- The four Branch-A error components split cleanly into three that are invariant
  under the geometry signature and one that is not, and the split is exactly the
  scale/rotation invariance that makes the five gates well posed. B1 is the
  narrow residue of an otherwise coherent invariance structure, which is
  probably why it survived design review.
- `e1a_v4/validation/runner.py` never contained a campaign driver; the frozen
  package states plainly that "the campaign driver is added by the authorised
  execution task". Writing that driver is what surfaced B1. No amount of static
  review of the frozen package would have surfaced it, because no static fixture
  exercises a locked artifact against a perturbed geometry.

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting coordinate | `a233811478f6d570b656a1696c4bf3e7be768c0b` |
| authorisation commit | **none created** — see *Authorisation disposition* |
| results commit | **none created** — no results exist |
| probe commit | `58388d7ee53debfcc0070284bc926293dceb2cfb` |
| probe tree SHA | `9680b3834ed672c29e3172baa035f0617bf4180f` |
| report commit | *this file's commit* |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — unchanged |

---

## Next stage

```
E1a v4 SYNTHETIC VALIDATION EXECUTION
BLOCKED — NOT STARTED
requires a separately versioned correction stage resolving B1 and B2
```

Preregistration, physical execution, E1b and Stage B remain unauthorised and
unstarted.

---

None of the three declared end markers is used, because all three assert that a
campaign ran. It did not.

```
SYNTHETIC VALIDATION NOT EXECUTED:
B1 CALIBRATION_GEOMETRY_BINDING_EXCLUDES_DECLARED_BRANCH_A_ERROR
B2 PER_REPLICATE_CALIBRATION_INFEASIBLE_AT_FROZEN_R_CAL
RANDOM DRAWS 0   TRAJECTORIES 0
```
