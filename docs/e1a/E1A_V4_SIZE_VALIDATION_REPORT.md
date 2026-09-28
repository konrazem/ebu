# E1a v4 — SIZE-VALIDATION REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**The final prospective ambiguity is closed.** The inherited 3% criterion is superseded
for release classification and replaced by prospective nominal-inflation tests, frozen
before any random outcome exists. The final campaign classification is frozen as an
explicit ten-point conjunction.

No E1a scientific endpoint changed. `execution_authorised` remains **false** and the
official execution command still refuses before any RNG is created.

---

## Why 3% was insufficient

The earlier frozen plan validated the geometry gates with a one-sided 95%
Clopper–Pearson **upper** bound ≤ 0.03. That is a **coarse gross-inflation tolerance**
inherited from development analysis, not validation of the nominal alpha allocations. At
the declared nominal levels it would have tolerated:

| case | tolerated | nominal alpha | ratio |
|---|---|---:|---:|
| C2 | 6/400 = 0.0150 | `alpha_geom = 0.005` | **3×** |
| C3 | 6/400 = 0.0150 | `alpha_2 = 0.001` | **15×** |
| C4 | 47/2000 = 0.0235 | `alpha_1 = 0.004` | **6×** |

**A rule that passes fifteen times the nominal rate cannot be called validation of it.**

The distinction is between a *gross tolerance* — "nothing catastrophic is happening" —
and *validation of a nominal alpha* — "the achieved rate is consistent with the level the
design declares". Only the second is a size validation, and the 3% rule was never the
second. It is retained solely as a clearly labelled **secondary gross-inflation
diagnostic**, and its provenance is preserved: commit `475633c` and
`docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md` are **not rewritten**.

### Two questions, never merged

**Question A — complete practical performance.** C1, UNCHANGED. One-sided 95% Clopper-Pearson LOWER bound on complete-pipeline success >= 0.90 over R = 300, i.e. >= 279/300. This is the direct prospective validation of whether the whole implemented pipeline meets the release target.

**Question B — component size inflation.** C2, C3 and C4. At the feasible replicate counts these are NOT positive proofs that the achieved rate is at or below a tiny nominal alpha. They prospectively TEST FOR EVIDENCE OF INFLATION: H0: p <= nominal alpha vs H1: p > nominal alpha, one-sided 5%.

```
H0: p <= nominal alpha        H1: p > nominal alpha       one-sided 5%

STATISTICAL SIZE INFLATION is detected iff CP_lower(rejections, R) > nominal alpha
```

Each boundary below is **recomputed** by `size_boundary(R, nominal)` in the test suite,
never copied from the plan.

| case | R | nominal alpha | no inflation detected | `STATISTICAL_SIZE_FAILURE` | CP_lower at boundary | CP_lower at boundary+1 |
|---|---:|---:|---|---|---:|---:|
| **C2** | 400 | `0.005` | **0–5** | **6+** | `0.0049379342` | `0.0065521458` |
| **C3** | 400 | `0.001` | **0–2** | **3+** | `0.0008891209` | `0.0020472587` |
| **C4** | 2000 | `0.004` | **0–13** | **14+** | `0.0038489425` | `0.0042367805` |

---

## C2 rule — whole P1 geometry gate

**Per field, never pooled.** `R = 400`, nominal `alpha_geom = 0.005`.

```
STATISTICAL_SIZE_FAILURE   iff  CP_lower(rejections, 400) > 0.005
```

| | |
|---|---|
| `CP_lower(5, 400)` | `0.0049379342` ≤ 0.005 → **no significant inflation detected** |
| `CP_lower(6, 400)` | `0.0065521458` > 0.005 → **`STATISTICAL_SIZE_FAILURE`** |
| derived boundary | **0–5 clean, 6+ fails** |

Every field is reported separately. The inherited `upper ≤ 0.03` diagnostic may still be
reported alongside, labelled as secondary; it is **not** validation of `alpha_geom`.

---

## C3 rule — G5 block

`R = 400`, nominal `alpha_2 = 0.001`.

```
STATISTICAL_SIZE_FAILURE   iff  CP_lower(G5 rejections, 400) > 0.001
```

| | |
|---|---|
| `CP_lower(2, 400)` | `0.0008891209` ≤ 0.001 → **no significant inflation detected** |
| `CP_lower(3, 400)` | `0.0020472587` > 0.001 → **`STATISTICAL_SIZE_FAILURE`** |
| derived boundary | **0–2 clean, 3+ fails** |

0–2 does **not** prove exact size ≤ 0.001. It means only that this experiment did not
establish excess size at the chosen confidence level.

---

## C4 rule — Block-1 surrogate validity

`R = 2000`, nominal `alpha_1 = 0.004`.

```
STATISTICAL_SIZE_FAILURE   iff  CP_lower(Block-1 rejections, 2000) > 0.004
```

| | |
|---|---|
| `CP_lower(13, 2000)` | `0.0038489425` ≤ 0.004 → **no significant inflation detected** |
| `CP_lower(14, 2000)` | `0.0042367805` > 0.004 → **`STATISTICAL_SIZE_FAILURE`** |
| derived boundary | **0–13 clean, 14+ fails** |

**The detailed C4 discrepancy report is retained, not replaced.** The full two-sided
interval and the observed operating-quantile discrepancy are still reported; this binary
diagnostic is an addition.

---

## What a pass means

> **`NO_SIGNIFICANT_SIZE_INFLATION_DETECTED`** — this experiment did not establish excess
> size at the chosen confidence level.
>
> It does **not** mean the achieved rate is mathematically proved to be at or below the
> nominal alpha.

Forbidden wording, recorded machine-readably and asserted by test:
`NOMINAL SIZE PROVED`, `nominal size proved`, `size proved`, `exact size established`.

---

## Final campaign classification

A final **`VALIDATION_PASS`** requires **all** of the following.
CONJUNCTIVE. Every required case must pass on its own terms. There is **no weighted score** and **no compensation** between cases.

1. C1 complete-pipeline success: CP lower >= 0.90 over R = 300 (>= 279/300)

2. C2 produces no STATISTICAL_SIZE_FAILURE in any required field

3. C3 produces no STATISTICAL_SIZE_FAILURE

4. C4 produces no STATISTICAL_SIZE_FAILURE

5. C5 satisfies its already-frozen plug-in Branch-A criterion

6. C6 satisfies its already-frozen mode-resolution criterion

7. EVERY C7 false-bridge alternative satisfies G2: CP upper <= 0.025 (<= 4/400)

8. C8 satisfies G1: CP lower >= 0.90 over R = 200 (>= 188/200)

9. no SOFTWARE_OR_INVARIANT_FAILURE, CALIBRATION_FAILURE, NUMERICAL_OR_PRECISION_FAILURE occurs

10. structured refusals counted exactly per the already-frozen unconditional denominator rule

> complete-pipeline achievement and component size cleanliness are REPORTED SEPARATELY and never collapsed. A campaign may fail because complete-pipeline success < target even with no significant size-inflation diagnostic: a valid scientific failure. Conversely C1 may reach >= 0.90 while a component case detects significant size inflation: also a validation failure, because the implemented calibration is not behaving according to its declared nominal structure. Both facts are reported.

Implemented by `e1a_v4.validation.classification.classify_campaign`. Deterministic fixtures confirm that each required
case failing **alone** produces a failure: C1, C2, C3, C4, C5, C6, the C7 hard
alternative, C8, a release-failing hard classification, and broken refusal accounting.
Two mixed fixtures confirm the independence rule in both directions.

---

## Identity changes

Determined by the defined hashing recipes, not forced in either direction.

| item | old | new | outcome |
|---|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | *same* | **UNCHANGED** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | *same* | **UNCHANGED** |
| analysis procedure identity | `af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4` | *same* | **UNCHANGED** |
| seed map | `28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87` | *same* | **UNCHANGED** |
| validation plan JSON | `88d0f1d54231dff01325aa0ea2251ce6316a3c7070880f08c184f00c72bd5185` | `c9168b82c7420ca0edb92da0cb0624f0763958e95893900a35f27c3c97363ae9` | changed |
| validation plan Markdown | `a334c8692d9f5326a0abdf9d253ee9c415f49bda3c163d95ac88410cbff1b74a` | `940c01b78a49301b2cd54a2ccdce1a6b99e279075247b79769314b09120d5cf1` | changed |
| execution identity | `0f4ec684de445390fa6d00b4bf7be0c6ce9656fee496f6891e9347ab1d5f0341` | `88037b9b2ac45bad0ab65151ab3f71897eb11bbd782ad09adfb9d0ca5d049837` | changed |

**The design contract was NOT changed.** These are validation-classification semantics,
and repository authority places them in the validation plan, not in the core E1a
contract. Because the contract did not change, the analysis procedure identity did not
change either, and — since the committed seed derivation binds only to the contract
identity — **the seeds legitimately remain unchanged**. No seed was used in this task.

The execution identity changed because it binds the validation module hashes and the plan
hash, both of which moved.

---

## Static tests

```
$ python3 test_e1a_v4_size_semantics.py

C2 whole P1 geometry gate
  [PASS] C2: boundary RECOMPUTED, not copied  -- size_boundary(400, 0.005) = 5
  [PASS] C2: CP_lower(5,400) <= 0.005  -- 0.0049379342
  [PASS] C2: CP_lower(6,400) > 0.005  -- 0.0065521458
  [PASS] C2: 5 does NOT trigger inflation
  [PASS] C2: 6 DOES trigger inflation
  [PASS] C2: 0 rejections never triggers
  [PASS] C2: plan records the same boundary  -- plan says 5
  [PASS] C2 nominal alpha is alpha_geom from the contract
  [PASS] C2 is per field and pooling is forbidden

C3 G5 block
  [PASS] C3: boundary RECOMPUTED, not copied  -- size_boundary(400, 0.001) = 2
  [PASS] C3: CP_lower(2,400) <= 0.001  -- 0.0008891209
  [PASS] C3: CP_lower(3,400) > 0.001  -- 0.0020472587
  [PASS] C3: 2 does NOT trigger inflation
  [PASS] C3: 3 DOES trigger inflation
  [PASS] C3: 0 rejections never triggers
  [PASS] C3: plan records the same boundary  -- plan says 2
  [PASS] C3 nominal alpha is alpha_2 from the contract

C4 Block-1 surrogate
  [PASS] C4: boundary RECOMPUTED, not copied  -- size_boundary(2000, 0.004) = 13
  [PASS] C4: CP_lower(13,2000) <= 0.004  -- 0.0038489425
  [PASS] C4: CP_lower(14,2000) > 0.004  -- 0.0042367805
  [PASS] C4: 13 does NOT trigger inflation
  [PASS] C4: 14 DOES trigger inflation
  [PASS] C4: 0 rejections never triggers
  [PASS] C4: plan records the same boundary  -- plan says 13
  [PASS] C4 nominal alpha is alpha_1 from the contract
  [PASS] C4 still retains its discrepancy report
  [PASS] C4 diagnostic reports BOTH bounds, not just the binary verdict

interpretation of a pass
  [PASS] a pass is worded as 'no significant inflation detected'
  [PASS] the machine-readable record states what a pass does NOT mean
  [PASS] 'nominal size proved' is explicitly forbidden wording
  [PASS] the frozen plan carries the same distinction
  [PASS] no verdict string asserts 'NOMINAL SIZE PROVED'
  [PASS] no verdict string asserts 'nominal size proved'
  [PASS] no verdict string asserts 'size proved'
  [PASS] no verdict string asserts 'exact size established'
  [PASS] the Markdown plan states what a pass does not mean
  [PASS] the 3% rule is recorded as superseded, not erased
  [PASS] its provenance is preserved  -- docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md and commit 475633c, neither rewritten
  [PASS] the 15x G5 discrepancy is recorded
  [PASS] the secondary diagnostic is labelled, not called validation

final campaign classification
  [PASS] all required cases pass -> VALIDATION_PASS  -- C1 cp_lower = 0.944115
  [PASS] C1 threshold is 279/300 and 290 clears it
  [PASS] C1 fails alone -> failure  -- TRUE_BRIDGE_POWER_FAILURE (C1 complete-pipeline success)
  [PASS] C2 fails alone -> failure  -- STATISTICAL_SIZE_FAILURE (C2 field theta2_ellipse)
  [PASS] C3 fails alone -> failure  -- STATISTICAL_SIZE_FAILURE (C3 G5 block)
  [PASS] C4 fails alone -> failure  -- STATISTICAL_SIZE_FAILURE (C4 Block-1 surrogate)
  [PASS] C5 fails alone -> failure  -- STATISTICAL_SIZE_FAILURE (C5 plug-in Branch-A)
  [PASS] C6 fails alone -> failure  -- MODE_RESOLUTION_FAILURE (C6 theta_cap boundary)
  [PASS] C7 hard alternative fails alone -> failure  -- FALSE_BRIDGE_DISCRIMINATION_FAILURE (C7 hard_1_025)
  [PASS] C8 fails alone -> failure  -- BLINDED_SCALE_CONTROL_FAILURE (C8)
  [PASS] a software failure alone -> failure  -- SOFTWARE_OR_INVARIANT_FAILURE
  [PASS] refusal accounting broken alone -> failure  -- STRUCTURED_REFUSAL_EXCESS (denominator accounting)
  [PASS] C1 at exactly 279 passes
  [PASS] C2 at exactly 5 per field passes
  [PASS] C3 at exactly 2 passes
  [PASS] C4 at exactly 13 passes
  [PASS] C7 at exactly 4 per alternative passes
  [PASS] C8 at exactly 188 passes
  [PASS] C1 meeting the target does NOT rescue a size failure  -- both facts reported separately, never collapsed
  [PASS] a size-clean campaign can still fail on complete-pipeline success
  [PASS] no weighted score and no compensation
  [PASS] multiple failures are all listed, none swallowed  -- TRUE_BRIDGE_POWER_FAILURE (C1 complete-pipeline success); STATISTICAL_SIZE_FAILU
  [PASS] C2 is evaluated per field, all four reported
  [PASS] release-failing classifications are exactly the three declared
  [PASS] a non-release-failing classification does not fail the campaign
  [PASS] plan and code agree on the ten requirements
  [PASS] out-of-range counts are refused

nothing else moved
  [PASS] alpha allocations unchanged
  [PASS] margins unchanged
  [PASS] theta_cap and rank_tol unchanged
  [PASS] primary sigma_psi unchanged at 0.5 degrees
  [PASS] complete-pipeline target unchanged
  [PASS] C1 criterion unchanged: 279/300
  [PASS] G1 threshold unchanged: 188/200
  [PASS] G2 threshold unchanged: 4/400
  [PASS] the design contract was NOT changed by this task  -- contract still 91d6ae76ccb6, version 1.1.0
  [PASS] classification.py is registered in the execution identity
  [PASS] execution remains unauthorised

E1a v4 size-semantics gate: 78 passed, 0 failed, 6 groups
Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)
  RANDOM DRAWS          : 0
  TRAJECTORIES          : 0
  CALIBRATION EXECUTION : NOT RUN
  VALIDATION CAMPAIGN   : NOT RUN
  C2 boundary (derived) : 0-5 of 400 at alpha 0.005
  C3 boundary (derived) : 0-2 of 400 at alpha 0.001
  C4 boundary (derived) : 0-13 of 2000 at alpha 0.004
```

| suite | passed | failed |
|---|---:|---:|
| size semantics | **78** | 0 |
| pre-execution | **93** | 0 |
| disposition | **64** | 0 |
| implementation | **119** | 0 |
| design authority | **113** | 0 |

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
```

```
$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : c9168b82c7420ca0edb92da0cb0624f0763958e95893900a35f27c3c97363ae9
  seed map sha256            : 28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87
  analysis procedure identity: af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4
  execution identity         : 88037b9b2ac45bad0ab65151ab3f71897eb11bbd782ad09adfb9d0ca5d049837
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
EXECUTION REFUSED: EXECUTION REFUSED: the frozen validation plan has execution_authorised = false. The synthetic-validation campaign is a separate authorised stage. No random number has been drawn.
  RANDOM DRAWS: 0   TRAJECTORIES: 0
```

```
$ git diff --check
[clean]
```

---

## Execution state

```
execution_authorised = false
RANDOM DRAWS = 0
TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN
VALIDATION CAMPAIGN = NOT RUN
```

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting local HEAD | `dd52c614826a1b163e2c3babd4cd8d58f5d1b236` |
| **work commit** | `861540548f8e3fbd75130c423f58cc94219e9efd` |
| **tree SHA** | `b22b5fd3eb49bba1ed62d35fa69bcfa2aa937638` |
| working tree after the work commit | **clean** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — **unchanged** |

Committed files:

```
M	docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md
M	docs/e1a/e1a_v4_synthetic_validation_plan.json
A	e1a_v4/validation/classification.py
M	e1a_v4/validation/plan.py
M	test_e1a_v4_preexec.py
A	test_e1a_v4_size_semantics.py
```

Generated after the work commit `8615405` and committed separately, per the convention
in `docs/e1a/E1A_V4_ADOPTION_REPORT.md`.

---

## Next stage

```
E1a v4 synthetic validation EXECUTION
READY FOR AUTHORISATION
NOT STARTED
```

Every release rule is now frozen prospectively: the eight cases, the generating model,
calibration, seeds, replicate counts, the G1/G2/G3 dispositions, the size-validation
semantics and the final campaign classification. Execution requires a separate
authorisation that flips `execution_authorised`. Preregistration, physical execution, E1b
and Stage B remain unauthorised.

---

```
SIZE-VALIDATION SEMANTICS FROZEN
```
