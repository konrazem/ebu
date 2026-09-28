# E1a v4 — CALIBRATION SCOPE REPORT

> **PARTIALLY SUPERSEDED — see `docs/e1a/E1A_V4_CASE_SCOPE_REPAIR_REPORT.md`.**
> An independent pre-execution re-audit did not clear execution. Nothing below is altered,
> and two figures in it are corrected there:
> 1. **the 40,000 artifact count is wrong.** It combined a 7,200 over-count (C7 and C8 were
>    budgeted artifacts their endpoints never consume) with a 13,200 under-count (the G3
>    `sigma_psi` subconditions of C1/C2/C3 were budgeted once instead of four times). The
>    corrected total is **46,000**, and the 29.7 core-hour projection becomes **34.2**.
> 2. **calibration is not required by every stochastic case.** C7 (P2 + P3) and C8
>    (P3-equivalent) evaluate no P1 / Block-1 quantity and now have no calibration path.
>
> The replicate-conditional architecture itself stands unchanged.

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

```
calibration_scope = REPLICATE_CONDITIONAL
```

**Every synthetic validation replicate that includes stochastic Branch-A measurement
uncertainty is analysed using calibration artifacts generated for that replicate's own
realised Branch-A calibration condition.**

```
H_true,theta  ->  H_A,theta,r  ->  C_theta,r  ->  Branch-B analysis_theta,r
```

The superseded alternative — four globally locked per-field artifacts — is **prohibited**
wherever Branch-A is realised per replicate. All eight cases are `STOCHASTIC_PER_REPLICATE`
and therefore `REPLICATE_CONDITIONAL`, requiring **40 000** calibration artifacts.

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
execution_authorised = false   RANDOM DRAWS 0   TRAJECTORIES 0
```

---

## Scientific rationale

A synthetic replicate stands for **one repeated complete experiment**, and Branch-A
measurement is part of that experiment. When Branch-A is realised per replicate,

```
H_A,r1  !=  H_A,r2      in general
```

and the P1 calibration null depends on the realised Branch-A condition. Analysing both
against one nominal artifact **because the field label matches** would validate a procedure
nobody proposes to run: it would hold the null fixed while the thing the null describes
moves.

The campaign therefore validates

```
Branch-A measurement  +  conditional calibration  +  Branch-B measurement  +  endpoint analysis
```

as **one repeated pipeline**. This matters most for **C1**, whose complete-pipeline claim is
the release criterion, and for **C5**, whose entire declared purpose is plug-in Branch-A
conditioning — a case that cannot measure plug-in conditioning if its calibration is not
itself conditioned on the plug-in.

**Adopted because it matches the repeated-experiment scientific model, not because it is
cheaper.** It is the more expensive arm by four orders of magnitude, and that was not allowed
to weigh.

### What is prohibited, and on what grounds

- one `theta0` artifact reused across every replicate
- one `theta1` artifact reused across every replicate
- one `theta2` artifact reused across every replicate
- one `theta3` artifact reused across every replicate

whenever those replicates have independently realised Branch-A conditions. The prohibition is
**mathematical, not merely provenance-based**: the Block-1 null law moves with the realised
`H_A`.

> **A matching field name is insufficient. A nominal `H` is insufficient. An eigenvalue ratio
> is insufficient.** The complete repaired `CalibrationCondition` must match.

### Limited reuse rule — not a categorical ban

Reuse is permitted only when **all four** hold:

1. the frozen case definition explicitly holds the calibration condition fixed across the
   relevant analyses;
2. the complete `CalibrationCondition` digest is identical;
3. the plan explicitly classifies that shared calibration as part of the case design;
4. the resulting dependence is compatible with the statistical quantity being estimated.

`CampaignCalibrationLedger` refuses a digest already locked to a different
`(case, replicate, field)` under `REPLICATE_CONDITIONAL`, so **an identical digest is not
permission**. There is no implicit cache-based reuse. `CASE_FIXED` additionally requires a
written rationale, and constructing it without one is refused.

**No case uses `CASE_FIXED`** in this campaign. The value exists in the schema and is
enforced, exactly as `confirmatory` is a declared seed family authorised for no case.

---

## Case calibration-scope table

| case | Branch-A status | calibration scope | artifacts | basis | seed families |
|---|---|---|---:|---|---|
| `C1_true_bridge_complete` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 1 200 | 300 replicates × 4 fields | `calibration`, `validation`, `branch_a_measurement` |
| `C2_geometry_false_rejection` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 1 600 | 400 × 4 fields | `calibration`, `validation`, `branch_a_measurement` |
| `C3_g5_block` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 1 600 | 400 × 4 fields | `calibration`, `validation`, `branch_a_measurement` |
| `C4_surrogate_validity` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 8 000 | 2000 × 4 fields | `calibration`, `validation`, `branch_a_measurement` |
| `C5_plug_in_branch_a` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 19 200 | 400 × 12 cells × 4 fields | `calibration`, `validation`, `branch_a_measurement` |
| `C6_mode_resolution_boundary` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 1 200 | 400 × 3 declared rho | `calibration`, `validation`, `branch_a_measurement` |
| `C7_false_bridge` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 6 400 | 400 × 4 alternatives × 4 fields | `calibration`, `validation`, `branch_a_measurement` |
| `C8_blinded_scale_control` | STOCHASTIC_PER_REPLICATE | **REPLICATE_CONDITIONAL** | 800 | 200 paired × 4 fields | `calibration`, `blinded_scale_control`, `branch_a_measurement` |
| | | **total** | **40 000** | | |

> **Every case now declares `calibration`.** That is a *derived consequence* of the adopted
> scope, not a relaxation of B3: before this decision only C4 generated calibration data, and
> now every case builds its own artifacts. `confirmatory` remains authorised for **no case**
> and `blinded_scale_control` for **C8 alone**.

### Seed separation

The three families a replicate needs are domain-separated by the already-frozen algorithm.
A **job** level was added:

```
master      DOMAIN|master|contract_sha256|campaign
family      DOMAIN|family|master_hex16|family_name
replicate   DOMAIN|replicate|family_hex16|case=<id>|rep=<index>
job         DOMAIN|job|replicate_hex16|field=<field_id>            [ADDED]
```

It is a **fourth level and changes none of the three above**: the master seed and every
family seed are bit-identical.

**Why it is required, not a convenience.** One replicate needs one calibration artifact per
field. A single per-replicate stream consumed sequentially across fields would make the
artifact contents depend on the **order** fields were processed in, so a parallel execution
could not reproduce a serial one. Domain separation by field makes each calibration job a
pure function of `(family, case, replicate, field)`.

Verified: distinct across case, replicate and field; calibration distinct from
`branch_a_measurement` and from `validation`; no collision across 3 families × 6 replicates ×
4 fields; and every seed is derived, never hand-selected.

---

## Ordering — calibration is locked before Branch-B data

Per replicate and field, prospectively:

```
1. derive the frozen replicate/job seed identities        (no draw)
2. generate the Branch-A synthetic measurement            branch_a_measurement family
3. construct the complete CalibrationCondition
4. generate and finalise the calibration artifact         calibration family
5. LOCK it; it is immutable from here
6. ONLY THEN release the Branch-B validation stream       validation family
```

`ReplicateCalibration.validation_seed` **refuses** until that field's artifact is locked. The
threshold is therefore conditional on Branch A and **blind to Branch B**: it cannot inspect
Branch-B observations, G1–G5 from validation data, `beta_hat`, P1/P2/P3 or the complete-pass
result, because none of them exists when it is built.

Enforced in both directions and tested: requesting the Branch-B stream before the lock
refuses; locking after Branch-B has been released refuses; regenerating a calibration after
Branch-B opened refuses; relocking a locked slot refuses; and each field is gated
independently.

### Campaign-level implementation: `STREAMING_PER_REPLICATE`

The preferred Phase A / Phase B / Phase C separation would materialise all 40 000 artifacts
before any Branch-B draw. Each artifact carries 4 gates × `R_cal = 50000` float64 null draws
= **1.6 MB raw**, so full Phase-B materialisation is about **64 GB** binary — several hundred
GB as JSON — against **24 GB** of RAM on the reference machine.

Streaming is therefore adopted. It is **exactly equivalent** because `ReplicateCalibration`
mechanically guarantees that the artifact for replicate `r` is finalised and immutable
**before** the first Branch-B validation draw for replicate `r`, and that no later validation
result can alter it.

**Auditability is preserved.** The artifact **manifest** is materialised in full for all
40 000 artifacts — about 2.6 MB of digests — so threshold freezing remains auditable before
any validation outcome exists, even though the draws themselves are streamed.

---

## C1 — complete-replicate semantics

Each of the **300** declared replicates is one complete synthetic experiment and carries:

- its own Branch-A measurement realisation;
- its own calibration condition;
- its own locked calibration artifacts — 4 fields, so **1 200** for the case;
- its own Branch-B trajectory;
- its frozen P1 / P2 / P3 / P4 evaluation.

The denominator is unchanged: **every declared validation replicate**, with structured
refusals **counting as failures**. A calibration refusal or failure for a replicate counts
under exactly those already-frozen semantics.

> **C1 is not conditioned on replicates whose calibration happened to succeed.** Doing so
> would silently convert the release criterion into a conditional one and would make a
> calibration that fails often look like a pipeline that succeeds often.

C1's criterion is unchanged: one-sided 95% Clopper–Pearson lower bound `>= 0.90`, requiring
**`>= 279/300`**.

---

## C4 — surrogate validity under the chosen scope

C4 validates the **behaviour of the calibration procedure**, so it is replicate-conditional
like every other case: each of its **2000** replicates is calibrated at its own realised
Branch-A condition, giving **8 000** artifacts.

This is the point of the choice for C4. Evaluating surrogate validity against **one** fixed
artifact would measure that artifact — possibly an unusually favourable or unfavourable draw
— rather than the repeated procedure the campaign claims to validate. The frozen C4 design
does not state a conditional question, so the repeated-procedure reading is the correct one.

**No C4 criterion changes.** It retains, verified by fixture:

- Block-1 rejection count over `R = 2000`
- size-inflation classification at `alpha_1 = 0.004`, boundary **0–13 clean, 14+ fails**
- the full two-sided interval
- the surrogate-versus-actual diagnostic
- the operating-quantile discrepancy

---

## Artifact identities

Each locked artifact binds:

```
case_id                         replicate_id                    field_id
calibration_condition_sha256    artifact_sha256
analysis_procedure_identity     contract_sha256                 calibrator_identity
R_cal                           alpha_1                         calibration_seed_identity
artifact_schema
```

plus every calibration output the repaired implementation requires — `artifact_sha256` covers
the condition digest, the null draws **and** the stored derived quantities.

Artifacts are **immutable after finalisation**: the ledger refuses a second lock for the same
`(case, replicate, field)` and refuses any lock after that field's Branch-B stream has been
released. The campaign manifest records every hash.

---

## Runtime

**Verified by decomposition before being repeated**, because a number quoted without its
contents is not evidence.

| component of ONE artifact build | measured |
|---|---:|
| surrogate draws + four gates, `R_cal = 50000` | `2.645 s` |
| threshold finalisation | `0.057 s` |
| **total, wall, median of 5** | **`2.674 s`** (CPU `2.627 s`, range `2.616`–`2.698`) |

**MEASURED BENCHMARK** — macOS-26.6.1-arm64, CPython 3.14.2, 14 CPUs, pure Python (numpy and
scipy absent). Deterministic supplier; no RNG.

> **Threshold finalisation is about 2% of an artifact build.** The other ~98% is surrogate
> generation and gate evaluation, which the B2 repair did not touch and could not touch.
> Calling "N core-hours of calibration" *threshold work* would misattribute it.

**BENCHMARK-BASED PROJECTION**, from the measured per-unit cost × the declared counts:

| | artifacts | projection |
|---|---:|---:|
| replicate-conditional (**adopted**) | 40 000 | **29.7 core-hours** |
| four locked artifacts (superseded) | 4 | **10.7 s** |
| Branch-A realisations | 40 000 | `0.51 s` |
| compatibility checks + P1 uses | 40 000 | `1.0 s` |

**PARALLELISM ASSUMPTION** — any wall-clock-at-N-workers figure assumes perfect scaling, no
I/O and no scheduling overhead.

**NOT MEASURED END-TO-END** — no campaign, calibration or trajectory has run. **Branch-B
trajectory generation is excluded from every figure above** (2 000 000 steps per
field-replicate) and is the largest term in the campaign.

### Correction to the repair report's figures

The repair report quoted `3.008 s` per artifact and `33.4 core-hours`, from a **2-repetition**
timing taken while other work was running. A 5-repetition timing gives **`2.674 s`** and
**29.7 core-hours**. Both are projections from a measured per-unit cost; the earlier one was
noisier. Neither is a measured campaign runtime. The repair report is **not rewritten**.

**Cost is not the scientific decision rule.** The adopted architecture is ~10 000× the cost of
the alternative on this term, and that did not weigh.

### Parallelism

Permitted **as an execution optimisation only**. It must not alter seed derivation, artifact
contents, replicate identities, case definitions, result ordering semantics or thresholds. A
serial and a parallel execution must produce **identical** scientific artifacts and results
for the same frozen protocol, aside from non-scientific ordering and timing metadata.

The mechanism: every calibration job is a pure function of `(family, case, replicate, field)`.
Tested by deriving the same 20 jobs in forward and reverse order and by locking the same four
artifacts in opposite orders — identical digests both ways. **No stochastic job is executed.**

---

## One-ULP policy

```
KEEP THE FAIL-CLOSED EXACT CANONICAL DIGEST
```

> **Mathematical invariance of the statistic is not bitwise identity of the
> calibration-condition representation.**

Every Block-1 gate is invariant to `H_A -> c H_A` in exact arithmetic, verified numerically to
`~1e-12` relative. But `normalised_H(c*H)` differs from `normalised_H(H)` in the last unit in
the last place, so the digests differ and the artifact is refused.

This may create two artifacts where one would mathematically suffice. **Accepted for v4.**
Introducing rounding solely to increase artifact reuse is **forbidden** — it would make a
formatted string the scientific identity — and canonical numerical equivalence is **not**
redesigned in this task. The stricter digest reduces reuse without weakening scientific
separation.

---

## Static tests

| suite | passed | failed |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` | **113** | 0 |
| `test_e1a_v4.py` | **122** | 0 |
| `test_e1a_v4_preexec.py` | **94** | 0 |
| `test_e1a_v4_dispositions.py` | **64** | 0 |
| `test_e1a_v4_size_semantics.py` | **78** | 0 |
| `test_e1a_v4_repair.py` | **126** | 0 |
| `test_e1a_v4_calibration_scope.py` | **102** | 0 |
| **total** | **699** | **0** |

`test_e1a_v4_preexec.py` rose from 93 to 94 (the validation-module count moved from 9 to 10),
`test_e1a_v4_repair.py` from 125 to 126, and the calibration-scope suite is new. No check was
removed or weakened.

```
$ python3 -m e1a_v4.validation.runner --preflight-only
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : bb44d838e712fd4339560cb946257e5f64ad6508cac150353e271837a1d9849c
  seed map sha256            : a3f9023195845120c3bcf0412b3cdc675c394fd6317720e9a95bbb65569288f3
  analysis procedure identity: dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
  execution identity         : aa6231c6a323d018f426f175ba2ae6bf24d09a190139a38a875a60cd170752e8
  declared cases             : 8
  execution_authorised       : False
  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)

$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
EXECUTION REFUSED: the frozen validation plan has execution_authorised = false.
The synthetic-validation campaign is a separate authorised stage. No random number
has been drawn.
  RANDOM DRAWS: 0   TRAJECTORIES: 0

$ git diff --check
[clean]
```

---

## Identities

Determined by the defined hashing recipes, not forced in either direction.

| item | old | new | outcome |
|---|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | *same* | **UNCHANGED** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | *same* | **UNCHANGED** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | *same* | **UNCHANGED** |
| **analysis procedure identity** | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | *same* | **UNCHANGED** |
| **every seed value** | master `13785910525869478477`, 5 family seeds | *same* | **UNCHANGED** |
| validation plan JSON | `6075e7a0015628fd9d05d095aaed0ebbe4924aaa7b64268fc5a5df00b3a8c347` | `bb44d838e712fd4339560cb946257e5f64ad6508cac150353e271837a1d9849c` | changed |
| validation plan Markdown | `1ffc54364716fe4dc5b39f6aba68a42d55141375317e7d2e14bbb0edc726fc6e` | `0dcaa37999bf208c5a5ea529618f627c1846da99e5121f454c3631d10a50b5bc` | changed |
| seed-map **file** | `28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87` | `a3f9023195845120c3bcf0412b3cdc675c394fd6317720e9a95bbb65569288f3` | changed |
| execution identity | `4ce4669c0296774e0780e5ddf2668a1cef3f28e8cfafd72ac529f527a62d1550` | `aa6231c6a323d018f426f175ba2ae6bf24d09a190139a38a875a60cd170752e8` | changed |
| calibration artifact schema | `e1a_v4_block1_calibration/2` | *same* | **UNCHANGED** |
| seed-map schema | `e1a_v4_seed_map/1` | `e1a_v4_seed_map/2` | changed |
| plan version | `1.3.0` | `1.4.0` | changed |

Three results deserve explanation.

**The analysis procedure identity did NOT move.** It binds the twelve analysis modules, and
calibration-scope enforcement is `e1a_v4/validation/scope.py` — a **validation** module. The
task anticipated that it might move "depending on whether calibration-scope enforcement is
included in its defined code set". It is not, so it did not. This is the correct outcome, not
a suppressed one: the scope decision changes *which* calibration an analysis receives, never
*how* the analysis works.

**The seed-map file hash moved, but no seed value did.** The file gained the `job` derivation
rule and moved to schema `/2`; `master_seed` and all five family seeds are bit-identical and
still rederive from the committed algorithm. This departs from the task's expectation that
the seed map would be unchanged, and it is the honest choice: leaving the authoritative
seed-map document describing three of four derivation levels would be precisely the kind of
incomplete binding that defect B1 was. **The substantive expectation — seed values unchanged —
is met exactly.**

**The execution identity moved** because it binds the validation module hashes (now ten, with
`scope.py` added), the plan hash and the seed-map hash.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Asserted by fixture: `delta_cross = 0.02`, `delta_abs = 0.05`,
`z_cross = z_abs = 1.959963985`, `alpha_geom = 0.005`, `alpha_1 = 0.004`, `alpha_2 = 0.001`,
`theta_cap = 5 deg`, `rank_tol = 1e-12`, primary `sigma_psi = 0.5 deg`, complete-pipeline
target `>= 0.90`, all eight replicate counts (300 / 400 / 400 / 2000 / 400 / 400 / 400 / 200),
the G1 and G2 criteria, the G3 disposition, the C2/C3/C4 size semantics, the false-bridge
alternatives, the seed-derivation algorithm for master/family/replicate, the complete-pass
denominator and the final ten-point conjunction are all unchanged.

The **design contract was not changed**, and no case was made that it must be.

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
| starting coordinate | `cf99cda7bc4c105e306cde3a2462be618555175d` |
| **work commit** | `cb76b84f77673226945f660c8dd3a0096cf0bb46` |
| **work tree SHA** | `1e89725482afa94f9931dbc9df640f5cb2313cde` |
| report commit | *this file's commit* |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — unchanged |

Preserved and not rewritten: `E1A_V4_SYNTHETIC_PREEXEC_REPORT.md`,
`E1A_V4_VALIDATION_DISPOSITION_REPORT.md`, `E1A_V4_SIZE_VALIDATION_REPORT.md`,
`E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md`, `E1A_V4_PREEXEC_REPAIR_REPORT.md`.

---

## Next stage

```
E1a v4 synthetic validation EXECUTION
READY FOR INDEPENDENT RE-AUDIT
NOT STARTED
```

Execution is **not** authorised. Every prospective decision the campaign needs is now frozen:
the eight cases, the generating model, the endpoints and margins, the seeds, the replicate
counts, the G1/G2/G3 dispositions, the size-validation semantics, the final campaign
classification, the complete calibration-condition binding, the exact threshold algorithm and
now the calibration scope.

Two items the re-audit should weigh in particular: the **40 000-artifact** cost of the adopted
architecture against its ~29.7 projected core-hours plus the excluded Branch-B term, and the
**`STREAMING_PER_REPLICATE`** implementation choice, which rests on the per-replicate
mechanical guarantee rather than on full Phase-B materialisation.

Preregistration, physical execution, E1b and Stage B remain unauthorised and unstarted.

---

```
CALIBRATION SCOPE FROZEN
```
