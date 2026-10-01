# E1a v4 — C3/C4 structured-refusal semantics: prospective authority amendment

Scientific-record entry for the amendment carried by work commit
`df9837e13c6e44d4e9a006cc99810af269bb8a05`, recorded in the frozen validation plan as
**`authority_gaps` G5** at plan version **1.15.0**.

---

## Gap discovered

A **valid structured refusal** can leave a C3 or C4 **primary endpoint decision
undefined**.

C3 releases on the actual **G5 / Block-2** decision and C4 on the actual
**Block-1** decision. Both are decisions of *one block* of the two-block P1 gate.
When the gate produced no p-values at all — a rank-guard failure, an unsupported
`N_eff`, an invalid Branch-A declaration — neither block decision exists. The
record is a legitimate terminal record with a legitimate terminal status; the
quantity those cases measure simply has no value for that replicate.

Frozen authority defined the treatment of structured refusals for
**complete-pipeline success only**:

- the contract states the rule inside `complete_pipeline.denominator` — "every
  declared experiment; refusals counted as failures; no conditioning on survivors";
- `synthetic_validation_requirements[9]` names complete-pipeline success;
- the plan's key is literally `complete_pass_denominator`, and its `refusals`
  value ends "**for complete-pipeline success**";
- the mandatory diagnostic carrying the `denominator_rule` aggregate key is bound
  to `case_id: "C1_true_bridge_complete"`.

**No frozen document said what an undefined primary endpoint means for a
COMPONENT SIZE TEST.** C1 could not absorb it either: C1 and C3/C4 are disjoint
job sets — 300 replicates for C1 against 400 for C3 and 2000 for C4 — so a refusal
inside a C3 replicate is not one of C1's experiments.

The consequence was concrete. The frozen size vocabulary offered exactly two
verdicts, `STATISTICAL_SIZE_FAILURE` on detection and
`NO_SIGNIFICANT_SIZE_INFLATION_DETECTED` **otherwise**. Applying that detector to
an incomplete primary sequence would have reported a required field as showing no
significant size inflation on evidence that was never obtained — in the limit,
`0/400` with every replicate refused.

The full reconstruction is
`docs/e1a/E1A_V4_C3_C4_REFUSAL_AGGREGATION_AUTHORITY_REPORT.md`, which returned
**UNSPECIFIED** and asked the author one question.

---

## Timing

```text
BEFORE OFFICIAL EXECUTION
NO OUTCOMES OBSERVED
```

At the moment of amendment: no `results/e1a_v4_validation` directory exists;
execution seal `state = PRE_DRIVER`, `expected_execution_identity = None`,
`execution_authorised = false`; official campaign jobs executed 0; official
campaign trajectories 0; RNG draws 0; calibrations executed 0. The amendment
therefore precedes outcome inspection and is **not** outcome-dependent tuning.

---

## Human decision

Approved prospectively, in full:

```text
 1. A valid structured refusal that leaves the primary C3/C4 endpoint undefined
    SHALL NOT be coded as either rejection or non-rejection.

 2. The prospectively declared primary denominator remains the planned R:
       C3 = 400 per field
       C4 = 2000 per field

 3. The terminal result SHALL separately retain:
       planned R
       evaluable primary-endpoint count
       structured-refusal count
       rejection count among defined primary endpoints
       refusal identity/reason information

 4. If structured_refusals > 0 for a required C3 or C4 field, the preregistered
    PRIMARY size assessment for that field is NOT_EVALUABLE.

 5. NOT_EVALUABLE is NOT STATISTICAL_SIZE_INFLATION_DETECTED.

 6. NOT_EVALUABLE is also NOT NO_SIGNIFICANT_SIZE_INFLATION_DETECTED.

 7. Because C3 and C4 are mandatory validation conditions, a required field whose
    primary size assessment is NOT_EVALUABLE cannot satisfy final campaign release.

 8. Therefore the campaign cannot PASS when any required C3/C4 field is
    NOT_EVALUABLE.

 9. The final failure reason must identify incomplete required validation
    evidence, not statistical size inflation.

10. A survivor-conditioned rejection rate / confidence bound may be reported only
    as a clearly labelled SECONDARY diagnostic if the repository chooses to retain
    such a diagnostic.

11. A survivor-conditioned diagnostic SHALL NEVER substitute for the frozen
    primary planned-R assessment.

12. The terminal campaign report MUST still be produced when one, some, or every
    C3/C4 job is a valid structured refusal.

13. No cross-field pooling is introduced.

14. No ANY_FIELD / EVERY_FIELD within-replicate reduction is introduced.

15. No change is made to the C3/C4 per-field scientific endpoint definitions.
```

---

## Scientific meaning

Three objects, deliberately kept apart.

| | meaning | enters the binomial count? |
|---|---|---|
| **statistical rejection** | the preregistered predicate was evaluated and was true | yes, as a defined `1` |
| **statistical non-rejection** | the preregistered predicate was evaluated and was false | yes, as a defined `0` |
| **not evaluable** | the predicate has no value, because the gate produced no p-values | **no** |

The detector `CP_lower(rejections, R) > nominal alpha` presupposes `R` Bernoulli
trials of the event being measured. An undefined outcome is not such a trial.
Silently converting it into a `0` or a `1` changes the estimand:

- as a `1`, a data-quality failure would be reported as evidence that the G5 block
  or the Block-1 gate has inflated size — a statement about the implementation's
  statistical behaviour that the data never supported;
- as a `0`, missing evidence would be reported as evidence of nominal behaviour,
  which is the stronger and more dangerous error.

`NOT_EVALUABLE` says neither. It says the preregistered evidence was not fully
observed.

The verdict vocabulary is therefore **three-way**, and its resolution has an
explicit **precedence**: a structured refusal is resolved **first**, and the
two-way detector is not run on an incomplete primary sequence. Without that
precedence the frozen `otherwise` branch would keep claiming a clean field.

---

## Denominator

```text
planned R preserved
```

`C3 planned_R = 400 per field`, `C4 planned_R = 2000 per field`. A refusal does
**not** silently transform the primary experiment to 399 or 1999. The primary
release semantics therefore distinguish `planned_R`, `evaluable_N` and
`structured_refusals`, and all three are retained per field.

A survivor-conditioned figure remains permitted only in the role design section 14
and `complete_pass_denominator.conditional_diagnostics` already allow: explicitly
labelled **SECONDARY**, beside the unconditional figure, never substituting for the
primary planned-R assessment.

---

## Release

```text
NOT_EVALUABLE prevents PASS because mandatory evidence is incomplete.
```

C3 and C4 remain mandatory final-release conditions. A required field satisfies its
condition only when it is `EVALUABLE_AND_CLEAN`. Either
`STATISTICAL_SIZE_FAILURE` or `NOT_EVALUABLE` prevents the campaign from passing —
but **the failure reasons differ**, and the terminal report must make it possible
to tell "the size test rejected" from "the size test could not be validly evaluated
as preregistered".

The campaign-level classification for the second case is **`VALIDATION_INCONCLUSIVE`**,
which was already frozen in `failure_classifications` and carried no declared
trigger; this amendment supplies one. It is deliberately **not**
`STATISTICAL_SIZE_FAILURE`, which would assert a rejection that never happened, and
deliberately **not** `STRUCTURED_REFUSAL_EXCESS`, whose name implies a tolerated
fraction that this amendment does not create.

**There is no tolerated-refusal fraction.** One structured refusal affecting a
required primary endpoint is sufficient. No refusal threshold, Bonferroni
correction, familywise correction, new alpha and no new integer boundary is
introduced.

`NOT_EVALUABLE` applies **independently by field**. One field's evaluability never
rescues another's.

---

## Reporting

```text
terminal report always produced.
```

The contract and the prospective design already require it — "jobs declared = jobs
completed + jobs refused, with a per-status count; **the report must finish even
when every job refuses**". This amendment connects that standing rule explicitly to
C3 and C4, where the current runtime violates it. Required, per field:

```text
planned_R
evaluable_primary_endpoint_count
structured_refusal_count
defined_rejection_count
primary_size_status
refusal_reasons
```

---

## Scientific non-effects

Unchanged by this amendment:

| | |
|---|---|
| **C2** | untouched. Its composite P1 endpoint **fails closed**, so `p1_rejected` is defined for every replicate including a structured refusal. Its boundary row records the scope-out explicitly rather than by silence: `undefined_primary_endpoint_possible: false`, `verdict_on_structured_refusal: "NOT_APPLICABLE"`. |
| **C3 primary endpoint** | still the actual G5 / Block-2 decision |
| **C4 primary endpoint** | still the actual Block-1 decision |
| **per-field scope** | `PER_FIELD` for both |
| **pooling** | `FORBIDDEN` for both |
| **within-replicate cross-field reduction** | `NONE` for both |
| **nominal alphas** | `alpha_2 = 0.001` (C3), `alpha_1 = 0.004` (C4) |
| **integer boundaries** | clean 0–2 of 400 (C3), clean 0–13 of 2000 (C4) |
| **C3 secondary P1 role** | still `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC`; the amendment does **not** make full P1 release-bearing, and an undefined G5 is **not** replaced by the P1 result |
| **physical foundation, theory baseline** | not modified; this is validation-protocol science |
| **design contract** | not modified; it does not name C3 or C4, and the G4 precedent recorded an equivalent C3/C4 decision in the plan alone |
| **seed values, generating model, C1, C5–C8, P2, P3, P4** | unchanged |

When `structured_refusals = 0` the ordinary frozen size rules apply exactly as
before.

---

## Next stage

```text
F1f-e REFUSAL-AWARE IMPLEMENTATION REPAIR
NOT STARTED
```

The runtime deliberately still lags this authority: `per_field_rejections` raises
`ENDPOINT_EVENT_MISSING` on a valid structured refusal, so the terminal report the
contract requires is still not produced. That lag is recorded as a permanent test
rather than papered over, and F1f-e repairs it.
