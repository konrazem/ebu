# E1a v4 — C3/C4 per-field size semantics: prospective authority amendment

Scientific-record entry for the amendment carried by work commit
`c086cd259d1c2192f3e74abffce212ba8577e76d`, recorded in the frozen validation
plan as **`authority_gaps` G4** at plan version **1.11.0**.

---

## Why amendment was necessary

The original authority did not define the C3/C4 field reduction sufficiently.

C3 and C4 each declare four physical fields, and the two-block P1 gate decides
**per field**: `p1_geometry` takes one field's analysis and rejects iff
`p_min(G1..G4) < alpha_1` or `p(G5) < alpha_2`. One replicate of C3 therefore
produces four Block-2 decisions and one replicate of C4 produces four Block-1
decisions, while both cases are scored against a **replicate** denominator
(R = 400 and R = 2000). No frozen document stated how four field decisions become
the one Bernoulli event those denominators count.

The frozen output schema made the gap concrete: `G5` and `P1` are
`per_record_fields` carried beside a `field_id`, and **no replicate-level G5 or
Block-1 field exists anywhere in the schema**. The counted quantity had to be
computed, and no rule said how.

Two specific defects were found by the authority reconstruction:

- **C3 was internally contradictory.** Its `R`, method and sided were marked
  `DERIVED` from contract `synthetic_validation_requirements[2]` with the stated
  reason that C3 "demonstrates one block of that same joint gate **at the same
  declared geometries**" — a per-geometry reading, since that clause reads "at
  every declared geometry". The **same** contract path was then cited for
  `pooling = NOT_APPLICABLE`, "C3 reports one campaign-level G5 rejection count".
  Both cannot be readings of one clause.
- **C4's field structure was unstated entirely.** Its `R = 2000` is package-level
  — the release specification itself records that frozen authority states no
  replicate count — its cited design item concerns the operating quantile rather
  than size across geometries, and nothing addressed field structure at all.

By contrast C2 was explicitly per field, from the contract clause "at every
declared geometry", with `pooling: FORBIDDEN`. The asymmetry was never a
deliberate statement about C3/C4; the C3/C4 size tests were added later and
addressed `R`, `alpha` and the integer boundary while never addressing fields.

---

## Timing

```text
BEFORE OFFICIAL EXECUTION
NO OUTCOMES OBSERVED
```

At the moment of amendment: no `results/e1a_v4_validation` directory exists;
execution seal `state = PRE_DRIVER`, `expected_execution_identity = None`,
`execution_authorised = false`, `random_draws = 0`, `trajectories = 0`; official
campaign jobs executed 0; official campaign trajectories 0. The amendment
therefore precedes outcome inspection and is **not** outcome-dependent tuning.

---

## Approved rule

```text
C3 = PER FIELD
C4 = PER FIELD
NO replicate-wide field reduction
NO pooling
```

For each declared field separately — `theta0_circular`, `theta1_power`,
`theta2_ellipse`, `theta3_temperature` — the case retains one R-replicate
sequence of **actual** rejection decisions (G5 / Block-2 for C3, Block-1 for C4)
and computes that field's own rejection count, rejection rate, Clopper-Pearson
bound and size-inflation classification.

There is no within-replicate any-field event, no every-field event, no
reference-field-only event, and no pooling of field rejection counts.

**Unchanged by this amendment**, and now applying per field:

| | C3 | C4 |
|---|---|---|
| R per field | 400 | 2000 |
| nominal | `alpha_2 = 0.001` | `alpha_1 = 0.004` |
| rule | `CP_lower(r, R) > alpha` detects inflation | same |
| integer boundary | clean 0–2, inflation 3+ | clean 0–13, inflation 14+ |

---

## Case-level semantics

Four field conditions enter the **existing** conjunctive final classifier.

The final rule is already conjunctive with no weighted score and no compensation,
and it already carries sub-case conditions natively — C2 contributes four
per-field conditions and C7 four per-alternative conditions. C3 and C4 now do the
same. Because conjunction is associative, a vector disposition entering as four
conditions and an all-fields-clean scalar entering as one are the same predicate
in every outcome; **no new scalar statistical event was created.**

The distinction that must survive implementation:

```text
ALLOWED    case clean  ==  all four FIELD SIZE GATES clean
                           (each gate = its own r_theta against its own boundary)

FORBIDDEN  case clean  ==  count of replicates where ANY field rejected,
                           scored against R
```

These are different statistical objects with different null rates. The failing
field's identity is preserved, exactly as C2 already preserves it.

---

## Operating characteristics

Disclosure, not thresholds. Exact binomial arithmetic at the exact nominal
per-field null; independently audited.

| | C3 | C4 |
|---|---|---|
| per-field false size-inflation flag | `0.00788343125882217` | `0.033884449548367356` |
| `P(field clean)` | `0.992116568741` | `0.966115550452` |
| **dependence-free** `P(all four clean)` | `[0.9684663, 0.9921166]` | `[0.8644622, 0.9661156]` |

No `R`, `alpha`, confidence level, method or integer boundary was altered to
change these numbers, and no multiplicity correction was applied.

---

## Dependence wording

```text
The frozen generating model intentionally shares a Branch-A common-mode draw
across fields within a replicate, so probabilistic independence of field-level
gate outcomes must not simply be assumed.

The direction and magnitude of the resulting dependence are not established by
the current authority/analysis.
```

The Fréchet/union bounds above rely on **no** association assumption.

---

## C4 conservative false-failure characteristic

The C4 union bound admits a family-level false-failure probability of
approximately **13.55 %**: a perfectly correct implementation whose true Block-1
size equals the nominal 0.004 exactly could still see C4 declared
`STATISTICAL_SIZE_FAILURE` with that probability.

This is recorded as an **operating characteristic**. It is:

- **NOT a target.** No 13.55 % or any other family-level figure becomes a
  threshold, and the ≥ 0.90 target is not extended to cover it.
- **NOT a false-pass risk.** It is a *conservative validation failure* — a
  spurious block on release — not a route to releasing something that should not
  be released.
- **NOT caused by the case-level aggregation**, which is forced by the
  conjunctive architecture. It is inherited from the already-frozen **per-field**
  design applied at four distinct physical conditions. Any remedy lies in that
  per-field design and would be a separate prospective decision, not taken here.

---

## `>= 0.90`

The frozen complete-pipeline target **remains C1-only**. It governs
`complete_pipeline.complete_pass_event`, the per-replicate scientific pipeline
success measured by C1 over R = 300 with boundary 279. The frozen size-validation
semantics keep the two questions "never merged", and the classifier reports
`complete_pipeline_met` and `component_size_clean` as independent facts. **No new
0.90 requirement was introduced for C3 or C4.**

---

## Scientific effects

Exactly what changed:

1. C3's elementary size event is now explicitly **per field**; its previously
   contradictory `unit: campaign` / `pooling: NOT_APPLICABLE` records are replaced
   by `unit: per_field` / `pooling: FORBIDDEN`, removing the contradiction with
   its own contract-derived `R`.
2. C4's elementary size event is now explicitly **per field**, where its field
   structure was previously unstated.
3. Both cases now declare, in machine-readable form, `field_structure: PER_FIELD`,
   `field_reduction: NONE` and `pooling: FORBIDDEN`, and both criteria state "PER
   FIELD, never pooled" in prose.
4. The final classification requirements for C3 and C4 now read "in any required
   field", matching C2's existing wording.
5. `authority_gaps` G4 records the gap, its resolution, the operating
   characteristics, the dependence limitation and the C1-only scope of ≥ 0.90.

---

## Scientific non-effects

Everything that did not change:

- `R`, nominal alphas, confidence method, confidence level, bound direction,
  comparison and **integer boundaries** for C3 and C4.
- C3's primary release endpoint `G5_BLOCK_SIZE`; Block-1 remains
  `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` with
  `joint_p1_result_changes_C3_release_verdict: false`, and the prohibition on any
  C3 release threshold based on Block 1 or the joint P1 result stands.
- C4's primary release endpoint `BLOCK1_ACHIEVED_SIZE`, its operating-quantile
  discrepancy and its full two-sided interval as mandatory contract diagnostics.
- C1, C2, C5, C6, C7, C8; P1, P2, P3, P4; G1 and G2 dispositions; `delta_cross`,
  `delta_abs`, the z values, `alpha_geom`, `alpha_1`, `alpha_2`, `theta_cap`,
  `rank_tol`; the four field definitions; the OU generator; calibration scopes;
  the seed hierarchy and every seed value.
- Campaign structure: 53,200 planned jobs, 46,000 calibration artifacts.
- **Byte-unchanged files**: design contract, prospective design, physical
  foundation, theory baseline, seed map, execution seal.
- The **analysis identity** does not move: no analysis-bound scientific module was
  modified.

---

## Next stage

```text
F1f — DRIVER/CLASSIFIER IMPLEMENTATION UPDATE
NOT STARTED
```

The driver and classifier were deliberately **not** updated. They still refuse
C3/C4 reduction with `ENDPOINT_EVENT_REDUCTION_UNDECLARED`, which is now
**authority-correct** rather than a guess: the scalar reduction they refuse to
invent is exactly what the amended authority forbids. That refusal was not
weakened. Execution remains blocked.
