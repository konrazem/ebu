# E1a v4 — CASE-SCOPE REPAIR REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**All three blockers from the independent pre-execution re-audit are closed.**

| | blocker | closed how |
|---|---|---|
| **B4** | C7 and C8 forced through Block-1 calibration their endpoints never consume | calibration necessity is now a declared property; both cases lose the family and every code path |
| **B5** | C1/C2/C3 `sigma_psi` subconditions under-budgeted | explicit subcondition ids everywhere; count reconstructed from the plan: **46 000** |
| **B6** | seed identity had no subcondition dimension | `subcondition` and `scope` levels added, with intentional sharing preserved |

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
execution_authorised = false   RNG OBJECTS 0   RANDOM DRAWS 0   TRAJECTORIES 0
```

This is an execution-architecture correction. Nothing about the E1a bridge, its
endpoints, margins, alphas or thresholds moved.

---

## C1–C8 calibration table

**The frozen rule.** *A case requires Block-1 calibration only if its frozen scientific
analysis actually evaluates a P1 / Block-1 quantity whose result or predeclared diagnostic
requires a `CalibrationArtifact`.* **"Branch-A stochastic" and "Block-1 calibration
required" are different properties and are no longer equated.**

`p1_geometry` is the **only** consumer of a `CalibrationArtifact` in the package;
`p2_cross_field`, `p3_absolute`, `p4_consistency`, `analyse_field` and `block2_p_value` take
none.

| case | uses P1? | cal. required? | release endpoint | secondary diagnostics | Branch-A | subconds | seed families |
|---|---|---|---|---|---|---:|---|
| C1 | **YES** | **YES** | `COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4` | — | stochastic | 4 | `calibration`, `validation`, `branch_a_measurement` |
| C2 | **YES** | **YES** | `P1_FALSE_REJECTION_RATE_PER_FIELD` | — | stochastic | 4 | `calibration`, `validation`, `branch_a_measurement` |
| C3 | **YES** | **YES** | `G5_BLOCK_SIZE` | **two-block P1 interaction** | stochastic | 4 | `calibration`, `validation`, `branch_a_measurement` |
| C4 | **YES** | **YES** | `BLOCK1_ACHIEVED_SIZE` | two-sided interval, operating-quantile discrepancy | stochastic | 1 | `calibration`, `validation`, `branch_a_measurement` |
| C5 | **YES** | **YES** | `P1_REJECTION_RATE_PER_CELL` | — | stochastic | 12 | `calibration`, `validation`, `branch_a_measurement` |
| C6 | **YES** | **YES** | `P1_REJECTION_RATE_PER_RHO` | merge/split decision rate | stochastic | 3 | `calibration`, `validation`, `branch_a_measurement` |
| **C7** | **NO** | **NO** | `P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE` | — | stochastic | 4 | `validation`, `branch_a_measurement` |
| **C8** | **NO** | **NO** | `P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY` | — | stochastic | 1 | `blinded_scale_control`, `branch_a_measurement` |

`confirmatory` reaches no case. `blinded_scale_control` reaches C8 alone. Unused families
are not granted, and the plan loader refuses a case that is granted `calibration` while
declaring `requires_block1_calibration: false`.

---

## C3 resolution

The ambiguity the auditor flagged is closed **prospectively**, in machine-readable form:

| | |
|---|---|
| `primary_release_endpoint` | **`G5_BLOCK_SIZE`** |
| release criterion | **UNCHANGED**: R = 400, nominal `alpha_2 = 0.001`; inflation iff `CP_lower(G5 rejections, 400) > 0.001`; 0–2 clean, 3+ `STATISTICAL_SIZE_FAILURE` |
| `requires_block1_calibration` | **true** |
| `block1_role` | **`SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC`** |
| `joint_p1_result_changes_C3_release_verdict` | **false** |

**Why calibration is retained.** C3's frozen purpose requires reporting the two-mode max
statistic's *interaction with the two-block gate*. That interaction is a P1 quantity and
needs an artifact. **What is forbidden:** adding any new C3 release threshold based on
Block 1 or on the joint P1 result. The release verdict depends on the frozen Block-2 / G5
size criterion and nothing else.

This preserves both halves of the frozen design — the G5 release criterion *and* the
predeclared requirement to examine the two-block interaction — without inventing a
threshold.

---

## C7 repair

Calibration has **no code path into C7**, verified by fixture:

- C7 does not request the `calibration` family; the official route refuses it.
- `calibration_seed` refuses — C7 constructs no `CalibrationCondition`.
- `lock` refuses — C7 cannot lock an artifact.
- **C7 reaches Branch-B with no artifact, no lock and no calibration refusal path.**
- C7 budgets **0** artifacts; the ledger stays empty.

**Why this mattered.** Previously C7 had to generate and lock an artifact before
`validation_seed` would release Branch-B data. `surrogate_covariance_draw` can refuse
("surrogate draw is not positive definite"), and a refusal would have suppressed a replicate
that could otherwise have produced a **false acceptance** — *flattering* the negative
control. A negative control made anti-conservative by an unrelated failure path is worse
than no control.

C7 is evaluated through exactly the endpoints it was designed to test — the all-field P3 and
the IUT P2 — and G2 still requires each alternative independently at `<= 4/400`.

---

## C8 repair

Calibration has **no code path into C8**, verified by the same five fixtures. C8 budgets
**0** artifacts, and a Block-1 calibration refusal **cannot fail C8** because no calibration
step exists in its path. Previously a refusal would have made a field non-`ESTIMATED`,
failing that blinded branch and **degrading the positive control**.

`dispositions.py` reaches `p3_absolute` and mentions neither `p1_geometry` nor
`CalibrationArtifact`. The frozen semantics are intact: factors `(1.07, 0.90)`, both
branches must pass at every field within one replicate, campaign threshold **`>= 188/200`**
recomputed, not copied.

**The pairing is intentional and preserved.** Both factors act on the **same** underlying
synthetic replicate through the frozen deterministic transform `BranchAField.blinded(c)`.
They are not independent random subconditions, they receive no separate streams, and C8
declares exactly one subcondition, `paired_scale_control`. Verified: the two branches
resolve to one base replicate stream.

**C1–C6 ordering is not weakened.** Each still refuses Branch-B before its calibration lock.

---

## Randomness dependency graph

**Default rule.** Different declared synthetic subconditions use **independent
domain-separated random streams** unless the frozen design explicitly declares them paired
or shared.

**Exception.** That rule applies *between* declared subconditions. It must not destroy
correlations deliberately built into a **single** synthetic experiment.

| quantity | family | scope | shared with | independent from |
|---|---|---|---|---|
| Branch-A **common-mode** error `sigma_cm` | `branch_a_measurement` | **`experiment`** | **all four fields** of the same (case, subcondition, replicate) | other replicates and subconditions |
| Branch-A per-mode stiffness `sigma_k` | `branch_a_measurement` | `<field_id>` | nothing | other fields, replicates, subconditions |
| Branch-A orientation `sigma_psi` | `branch_a_measurement` | `<field_id>` | nothing | " |
| Branch-A thermometry `sigma_T` | `branch_a_measurement` | `<field_id>` | nothing | " |
| calibration surrogate draws | `calibration` | `<field_id>` | nothing | every other calibration job |
| Branch-B trajectory innovations | `validation` / `blinded_scale_control` | `<field_id>` | nothing | " |
| C8 factors `c = 1.07`, `0.90` | **not random** | n/a | **one base replicate** | — |

> **The load-bearing case.** The Branch-A common-mode error is drawn **once per synthetic
> experiment and shared across all four fields**, because that is exactly what makes it
> cancel in the P2 ratio and not in P3. Redrawing it per field would have destroyed the
> dependence structure P2 exists to test. `scope` is therefore a property of the *quantity*,
> not of the loop it sits in — randomness is **not** blindly field-scoped.

Traced from the frozen generator, not assumed: `BranchAErrorModel.measure` takes
`common_mode` as a **parameter** (it does not draw it) and draws `m + 2` values per field for
stiffness, orientation and thermometry.

**Verified by fixture:** the common-mode stream is identical across the four fields of one
experiment, differs from every per-field stream, and differs across subconditions and
replicates; the four per-field streams are mutually distinct.

---

## Seed hierarchy

```
master        H( DOMAIN | "master"    | contract_sha256 | campaign )        UNCHANGED
family        H( DOMAIN | "family"    | master_hex      | family    )        UNCHANGED
replicate     H( DOMAIN | "replicate" | family_hex      | case | rep )       UNCHANGED
subcondition  H( canon("subcondition", replicate_hex, subcondition_id) )     ADDED
scope         H( canon("scope",        subcondition_hex, scope)        )     ADDED
```

`canon` is a **deterministic domain-separated serialisation**, not concatenation: parts are
JSON-encoded with fixed separators and ASCII escaping, so a separator inside an identifier
cannot forge a different tuple. `scope` is `experiment` or a field id.

**Master, family and replicate values are bit-identical.** Subcondition ids come from the
frozen plan; an unknown id **refuses** at both the seed boundary and the calibration
boundary.

Declared subconditions: C1/C2/C3 `sigma_psi_0p0|0p2|0p5|1p0`; C4 `primary`; C5 twelve
`sk{0p00,0p50,1p00}_sp{0p0,0p2,0p5,1p0}`; C6 `rho_1p019573|1p024467|1p029360`; C7
`alt_1_06|alt_0_93_1_05|alt_1_10|hard_1_025`; C8 `paired_scale_control`.

---

## Collision audit

Enumerated deterministically over the **entire** frozen campaign — every case × allowed
family × subcondition × replicate × scope, including the `experiment` scope — with no
sampling:

```
job identities enumerated : 204,000
unique                    : 204,000
collisions                :       0
```

The 204 000 is the sum over cases of `families x subconditions x replicates x scopes`, where
scopes are the four fields plus `experiment`:

```
C1 3x4x300x5=18,000   C2 3x4x400x5=24,000   C3 3x4x400x5=24,000   C4 3x1x2000x5=30,000
C5 3x12x400x5=72,000  C6 3x3x400x5=18,000   C7 2x4x400x5=16,000   C8 2x1x200x5= 2,000
```

Scheduling is proved irrelevant: 64 C5 jobs derived in forward and fully reversed order
resolve to identical identities. Serial and parallel execution cannot differ.

Subcondition independence verified individually: different `sigma_psi` scenario, different C5
cell, different C6 rho and different C7 alternative each yield different streams, and all
four C7 alternatives are mutually distinct.

---

## Artifact-count reconstruction

Derived from the machine-readable plan, term by term — not typed first and matched
afterwards.

| case | replicates | × subconditions | × fields needing calibration | artifacts |
|---|---:|---:|---:|---:|
| C1 | 300 | 4 | 4 | **4 800** |
| C2 | 400 | 4 | 4 | **6 400** |
| C3 | 400 | 4 | 4 | **6 400** |
| C4 | 2 000 | 1 | 4 | **8 000** |
| C5 | 400 | 12 | 4 | **19 200** |
| C6 | 400 | 3 | 1 | **1 200** |
| C7 | 400 | 4 | — | **0** |
| C8 | 200 | 1 | — | **0** |
| | | | **TOTAL** | **46 000** |

Every factor was checked against current authority. C6 uses one synthetic two-mode field per
rho, so its field factor is 1, not 4 — which is why 400 × 3 × 1 = 1 200 rather than 4 800.

**The superseded 40 000 is recorded, not erased.** It arose from two compensating errors:

```
40,000  −  7,200 (C7 + C8 over-count)  +  13,200 (C1/C2/C3 sigma_psi under-count)  =  46,000
```

which is why a check on the **sum** passed while both components were wrong.

---

## Runtime correction

| | |
|---|---|
| one artifact build | **`2.674 s`** wall, `2.627 s` CPU, median of 5 — **MEASURED** |
| of which threshold finalisation | `0.057 s`, about **2 %** |
| of which surrogate generation + gates | `2.645 s`, about **98 %** — untouched by the B2 repair |
| **46 000 artifacts** | **34.2 core-hours** — **BENCHMARK-BASED PROJECTION** |

This supersedes the 29.7 core-hour figure, which rested on the incorrect 40 000 count.

**NOT MEASURED END-TO-END.** No campaign, calibration or trajectory has run. **Branch-B
trajectory generation is excluded** from every figure above and remains the larger term.
**No resource ceiling is declared, so this establishes neither feasibility nor
infeasibility** — only the projected cost. Cost played no part in the scope decision.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Verified against the contract file itself: `delta_cross = 0.02`, `delta_abs = 0.05`,
`z_cross = z_abs = 1.959963985`, `alpha_geom = 0.005`, `alpha_1 = 0.004`,
`alpha_2 = 0.001`, `theta_cap = 5°`, `rank_tol = 1e-12`, primary `sigma_psi = 0.5°`,
complete-pipeline target `>= 0.90`, all eight replicate counts
(300/400/400/2000/400/400/400/200), the G1 (188/200) and G2 (4/400) criteria recomputed, the
G3 disposition, the C2/C3/C4 size semantics (boundaries 5, 2, 13), the false-bridge
alternatives, the complete-pass denominator and the final ten-point conjunction.

---

## Identity changes

| item | old | new | outcome |
|---|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | *same* | **UNCHANGED** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | *same* | **UNCHANGED** |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` | *same* | **UNCHANGED** |
| **analysis procedure identity** | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | *same* | **UNCHANGED** |
| **master + all family seed values** | `13785910525869478477`, 5 families | *same* | **UNCHANGED** |
| validation plan JSON | `bb44d838e712fd4339560cb946257e5f64ad6508cac150353e271837a1d9849c` | `db4ba663c21945413d94de02062e21263e42a9ea4d0432ac9bb749a1bf9d165d` | changed |
| validation plan Markdown | `0dcaa37999bf208c5a5ea529618f627c1846da99e5121f454c3631d10a50b5bc` | `63fe9f669d7911e0c3ea5f685e43ea3c7a0f150fe290a405ec10a332cf5d3745` | changed |
| seed-map **file** | `a3f9023195845120c3bcf0412b3cdc675c394fd6317720e9a95bbb65569288f3` | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | changed |
| execution identity | `aa6231c6a323d018f426f175ba2ae6bf24d09a190139a38a875a60cd170752e8` | `ff79156c4b878e42598d9c19943bd4532d82b60b4e9aa1b0af269bb8b56b69cb` | changed |
| result schema | `e1a_v4_validation_result/1` | `e1a_v4_validation_result/2` | changed |
| manifest schema | `e1a_v4_validation_manifest/1` | `e1a_v4_validation_manifest/2` | changed |
| seed-map schema | `e1a_v4_seed_map/2` | `e1a_v4_seed_map/3` | changed |
| plan version | `1.4.0` | `1.5.0` | changed |

**The analysis identity did not move** because no analysis-layer module changed — the repair
lives entirely in `e1a_v4/validation/`. **The seed-map file hash moved for documentation
only**: the superseded `job` level is replaced by `subcondition` + `scope`, and every seed
value still rederives from the committed algorithm. Leaving the authoritative seed map
describing a derivation the code no longer uses would be the same class of incomplete
binding that defect B1 was.

Result schema 2 adds `subcondition_id`; a record is reproducible from
`(case_id, subcondition_id, replicate_id, field/scope, seed family, seed identity)`. No
official result data exists, so the break is made explicit now rather than leaving old
records ambiguous.

---

## Tests

| suite | passed | failed |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` | **113** | 0 |
| `test_e1a_v4.py` | **122** | 0 |
| `test_e1a_v4_preexec.py` | **94** | 0 |
| `test_e1a_v4_dispositions.py` | **64** | 0 |
| `test_e1a_v4_size_semantics.py` | **78** | 0 |
| `test_e1a_v4_repair.py` | **126** | 0 |
| `test_e1a_v4_calibration_scope.py` | **102** | 0 |
| `test_e1a_v4_case_scope.py` (**new**) | **112** | 0 |
| **total** | **811** | **0** |

`docs/e1a/e1a_v4_execution_feasibility_probe.py` also passes. No check was removed or
weakened; the suites that changed did so because the API they exercise changed.

```
$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : db4ba663c21945413d94de02062e21263e42a9ea4d0432ac9bb749a1bf9d165d
  seed map sha256            : 95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce
  analysis procedure identity: dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
  execution identity         : ff79156c4b878e42598d9c19943bd4532d82b60b4e9aa1b0af269bb8b56b69cb
  declared cases             : 8
  execution_authorised       : False
EXECUTION REFUSED: the frozen validation plan has execution_authorised = false.
No random number has been drawn.
  RANDOM DRAWS: 0   TRAJECTORIES: 0

$ git diff --check
[clean]
```

---

## Execution state

```
execution_authorised = false

RNG OBJECTS = 0

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
| starting coordinate | `27497856ac2ffde4e8945aa5f3282f3c896c16c1` |
| **work commit** | `941674f14d22520ad9de7ac443874fdf6e6125f4` |
| **work tree SHA** | `a4ad8efb13ec5e880973c0e67e845e2cbc383669` |
| report commit | *this file's commit* |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — unchanged |

All previous reports are preserved and none is rewritten. The superseded 40 000 count is
corrected here and in the plan, with its provenance recorded.

---

## Next stage

```
E1a v4 synthetic validation EXECUTION
READY FOR FINAL INDEPENDENT RE-AUDIT
NOT STARTED
```

Execution is **not** authorised. A re-audit should check in particular: that C7 and C8 now
have no reachable calibration path in either direction; that the `experiment` scope really
does preserve the common-mode sharing P2 depends on; and the 46 000 reconstruction, whose C6
term uses one field per rho rather than four.

Preregistration, physical execution, E1b and Stage B remain unauthorised and unstarted.

---

```
CASE-SCOPE REPAIR COMMITTED
```
