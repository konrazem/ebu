# E1a v4 — refusal-aware C3/C4 runtime repair (F1f-e)

Runtime implementation of the G5 structured-refusal amendment. **No scientific
decision was made in this stage**: every rule implemented here was settled by the
amendment, which the independent audit cleared.

```text
STAGE             F1f-e  REFUSAL-AWARE C3/C4 RUNTIME REPAIR
STARTING COMMIT   a6e94d4c9d25daff75588203b6c00247a2596a3a
AUTHORITY         UNCHANGED -- plan, Markdown, contract, design, foundation,
                  theory baseline and seed map are all byte-unchanged
```

---

## 1. The original counterexample

Reproduced before any edit, with pure deterministic records. No RNG, no
trajectory, no calibration, no campaign job.

```text
analysis_status  = RANK_GUARD_FAIL
refusal_reason   = REFUSED_ACCESSIBLE_SPACE
P1               = False      p1_rejected = True
block1_rejected  = None       g5_rejected = None       <- UNDEFINED
```

| layer | C3_g5_block | C4_surrogate_validity |
|---|---|---|
| `require_endpoint_events` | **ACCEPTED** | **ACCEPTED** |
| `per_field_rejections` (399 defined + 1 refusal) | `ENDPOINT_EVENT_MISSING` | `ENDPOINT_EVENT_MISSING` |
| `per_field_rejections` (all refused) | `ENDPOINT_EVENT_MISSING` | `ENDPOINT_EVENT_MISSING` |

**Exact code path**, captured from the traceback:

```text
per_field_rejections -> field_event_count
raised at e1a_v4/validation/campaign_driver.py:3588
code ENDPOINT_EVENT_MISSING
```

**What survived and what did not.** `publish_job_record` commits each terminal job
record *before* `campaign_counts_from_records` is reached, so the durable per-job
records would exist. The refusal then propagated out of `execute_campaign` before
its return statement, so the **campaign-level terminal result was never
produced** — directly contrary to the contract's "the report must finish even when
every job refuses".

Both cases are now permanent regressions in
`test_e1a_v4_driver_endpoints.py::test_refusal_aware_aggregation`.

---

## 2. Runtime representation

A per-field rejection count cannot express the amendment: `rejections = 2` over a
planned 400 means different things depending on whether the other 398 decisions
exist. C3 and C4 therefore carry a frozen `FieldSizeOutcome` per field rather than
an integer.

```python
@dataclass(frozen=True)
class FieldSizeOutcome:
    field_id: str
    planned_replicates: int          # the FROZEN prospective R, always
    evaluable: int                   # replicates whose primary endpoint EXISTS
    structured_refusals: int         # replicates whose endpoint is UNDEFINED
    rejections: int                  # TRUE decisions among the EVALUABLE only
    refusal_reasons: Mapping[str, int] = {}   # reason -> count
```

`refusal_reasons` is recovered from the record's own provenance —
`refusal_reason` where the schema carries it, `analysis_status` otherwise — so no
refusal category is invented. The object refuses on construction if

```text
0 <= evaluable, structured_refusals, rejections <= planned_replicates
rejections <= evaluable
evaluable + structured_refusals == planned_replicates
sum(refusal_reasons.values()) == structured_refusals   (when reasons are given)
```

does not hold, so a silently discarded record cannot reach the classifier.

**C2 deliberately keeps plain counts.** Its composite P1 endpoint fails closed, so
its elementary event is defined for every replicate including a refusal. Giving it
the richer type would create a `NOT_EVALUABLE` path that frozen authority marks
`NOT_APPLICABLE` for it. The asymmetry in the code mirrors the asymmetry in the
science.

---

## 3. Verdict precedence

Implemented as the authority states it, in one place:

```python
def classify_field_size(outcome, nominal):
    if not outcome.fully_evaluable:          # structured_refusals > 0
        return {... "verdict": SIZE_NOT_EVALUABLE ...}
    return classify_size(outcome.rejections, outcome.planned_replicates, nominal)
```

The refusal is resolved **first** and the detector is **not run** on an incomplete
sequence. The order is not a convenience: the two statistical verdicts partition
every `(rejections, R)` pair between them — `otherwise` catches everything that is
not a detection — so computing the detector first and overriding it afterwards
would already have claimed a clean field, and an all-refused field would report
`NO_SIGNIFICANT_SIZE_INFLATION_DETECTED` on zero observations.

`None` is never converted to a boolean anywhere on this path.

---

## 4. C3 behaviour

Primary endpoint unchanged: the **actual G5 / Block-2 decision**.

| record | C3 contribution |
|---|---|
| `g5_rejected = True` | `rejections += 1`, `evaluable += 1` |
| `g5_rejected = False` | `evaluable += 1` |
| `g5_rejected = None` with a valid refusal status | `structured_refusals += 1` |

The full P1 result is never substituted for a missing G5 value, and remains the
secondary predeclared interaction diagnostic.

## 5. C4 behaviour

Primary endpoint unchanged: the **actual Block-1 decision**, with the identical
three-way treatment. Neither the combined P1 result nor G5 is substituted for a
missing Block-1 value.

---

## 6. C2 non-effect

Proved rather than asserted:

```text
is_structured_refusal({... 'p1_rejected': None}, 'p1_rejected')  ->  False
```

`p1_rejected` is not in `BLOCK_DECISION_EVENTS`, so C2 has no refusal path at all.
C2 still flows through `per_field_rejections` and `field_event_count` unchanged,
still carries `Mapping[str, int]`, and under a refused replicate still counts
`p1_rejected = True` because P1 fails closed:

```text
C2, 10 replicates, 1 refusal -> {theta0: 1, theta1: 1, theta2: 1, theta3: 1}
```

The classifier reports C2's scope-out explicitly rather than by silence:
`undefined_primary_endpoint_possible: False`,
`verdict_on_structured_refusal: "NOT_APPLICABLE"`.

---

## 7. All-refused campaign

A **complete miniature campaign** is assembled from pure records — every planned
job of every case — and taken through the real chain: records →
`campaign_counts_from_records` → `classify_campaign` → terminal result. C3 and C4
keep their **frozen** planned counts (400 and 2000 per field); the other cases are
reduced, because writing 53,200 real jobs would be a campaign. The classifier
refuses evidence whose planned denominator differs from the frozen one, so
shrinking C3/C4 would have tested nothing.

With every C3 and C4 job a valid structured refusal:

```text
aggregation                     COMPLETES          (previously raised)
terminal campaign result        EXISTS             (previously never built)
every C3 / C4 field             NOT_EVALUABLE
C3 field evidence               planned 400,  evaluable 0,  refusals 400
C4 field evidence               planned 2000, evaluable 0,  refusals 2000
refusal reasons retained        {REFUSED_ACCESSIBLE_SPACE: 400} / {...: 2000}
campaign                        cannot PASS
statistical size failure        NONE fabricated
failure classification          VALIDATION_INCONCLUSIVE
C2                              counted normally, unaffected
```

## 8. Partial refusal

```text
C3  planned 400,  evaluable 399,  refusals 1,  defined rejections 2  -> NOT_EVALUABLE
C4  planned 2000, evaluable 1999, refusals 1,  defined rejections 13 -> NOT_EVALUABLE
```

Neither clean nor size inflation. The planned denominator is preserved — the
terminal row reports `planned_replicates = 400` / `2000`, never 399 / 1999 — and
the defined rejections are retained rather than discarded. The same fields with
nothing refused reach the ordinary frozen verdict, so the precedence is doing the
work rather than a blanket override.

## 9. Mixed reasons

The case the independent authority audit flagged. One campaign carrying both kinds
of failure at once:

```text
C3 / theta0_circular    NOT_EVALUABLE                  (structured refusal)
C3 / theta1_power       STATISTICAL_SIZE_FAILURE       (3 of 400, boundary 2)
C4 / theta1_power       NOT_EVALUABLE                  (structured refusal)
C4 / theta3_temperature STATISTICAL_SIZE_FAILURE       (14 of 2000, boundary 13)
C3 / theta2, theta3     clean
C4 / theta0, theta2     clean
```

Terminal result: **two** `VALIDATION_INCONCLUSIVE` failures and **two**
`STATISTICAL_SIZE_FAILURE` failures, each naming its own case and field. Neither
reason erases the other, the clean fields stay clean, and the campaign cannot
pass. The two facts are also reported separately:

```text
independent_facts.component_size_clean      False
independent_facts.component_size_evaluable  False
```

`component_size_evaluable` is new and deliberate: without it a campaign with a
`NOT_EVALUABLE` field would report `component_size_clean = True`, which reads as
"the components behaved" when a required assessment was never made.

## 10. Invalid missing endpoints still refuse

The repair is scoped to AUTHORISED absences. One predicate decides, and both
layers ask it:

```python
def is_structured_refusal(outcome, event) -> bool:
    return (event in BLOCK_DECISION_EVENTS     # a per-field block decision
            and event in outcome               # the key is PRESENT
            and outcome[event] is None         # and null
            and outcome.get("analysis_status") is not None
            and outcome["analysis_status"] != "ESTIMATED")
```

| record | result |
|---|---|
| null block decision, non-ESTIMATED status | **authorised refusal** → NOT_EVALUABLE path |
| null block decision while `analysis_status = ESTIMATED` | `ENDPOINT_EVENT_MISSING` |
| the decision key removed entirely | `ENDPOINT_EVENT_MISSING` |
| null block decision with **no** `analysis_status` | `ENDPOINT_EVENT_MISSING` |
| `p1_rejected = None` (C2) | not a refusal; still refuses |

The fourth row is a defect my own test found while being written. The first draft
read `outcome.get("analysis_status") != "ESTIMATED"`, which is **also true when the
key is absent** — so a record that simply failed to record its status would have
been read as an authorised refusal, with silence granting the exemption.
Authorisation must be stated, so the predicate now requires the status to be
present and affirmative.

### Cross-layer invariant

The original bug was a disagreement between two layers. It is now structural
rather than coincidental: `require_endpoint_events` and `field_primary_outcome`
both call `is_structured_refusal`, and a deterministic test asserts that for a
valid refusal and for a fully estimated record the validator and the aggregator
reach the same verdict.

## 11. Persistence and restart

The per-job record schema is **unchanged**: records were already per field, with
`coordinates.scope = field_id`, `analysis_status`, `refusal_reason` and the null
block decisions. Nothing new needs persisting at record level, and an undefined
endpoint is stored as `null` rather than reconstructed as a boolean.

A round trip through canonical JSON is asserted: recovered C3 and C4 evidence
equals fresh evidence object-for-object, the nulls survive as nulls, and the
campaign verdict is identical.

### The assembly path itself

`execute_campaign` builds the terminal result immediately after
`classify_campaign` and returns it unconditionally — there is no branch on the
verdict, so no ordinary scientific outcome can abort assembly. The only thing that
could was the exception raised inside `campaign_counts_from_records`, which is
what this stage removed. That function is verified by inspection rather than
execution: `execute_campaign` is trajectory-bearing and was not run.

`CAMPAIGN_RESULT_SCHEMA` moves `e1a_v4_campaign_result/2` → `/3`, because the
embedded per-field classification now carries the evaluable count, the refusal
count with reasons and a verdict that may be `NOT_EVALUABLE`. A version-2 result
is **not convertible**: it holds one rejection count per field and cannot say
whether the remaining replicates were defined non-rejections or undefined
endpoints — exactly the distinction the release rule turns on. No official result
data exists at any version, so nothing is migrated and nothing is reinterpreted;
an older ambiguous result is refused rather than guessed.

---

## 12. Implementation conformance

Preflight's `require_per_field_implementation_conformance` now asserts the
three-state behaviour, so a runtime that is not refusal-aware is **refused**
rather than tolerated. Three independent layers:

```text
SHAPE      the per-field evidence declares planned_replicates, evaluable,
           structured_refusals, rejections, refusal_reasons and field_id --
           the terminal counts frozen authority names
BEHAVIOUR  one structured refusal must yield NOT_EVALUABLE, with the planned
           denominator preserved, a uniquely identified VALIDATION_INCONCLUSIVE
           failure, no STATISTICAL_SIZE_FAILURE, and a campaign that cannot pass;
           the SAME counts with nothing refused must reach the ordinary verdict
DRIVER     the canonical driver declares is_structured_refusal,
           structured_refusal_reason, field_primary_outcome and
           per_field_primary_outcomes
```

The driver layer is checked by **parsing the driver's AST**, never by importing
it. Importing would execute driver code, which this stage forbids and which
`e1a_v4/validation/driver.py` already avoids for the same reason — it checks the
entry point the same way. A driver that only counts occurrences of a per-field
event declares none of those names, has no defined aggregation path for a valid
refusal, and is detected.

Three sandbox fixtures that overwrite the driver with a stub to exercise later
lifecycle gates now declare that surface too, exactly as they already declared
`run_campaign`. One assertion in `coherence_hardening` was strengthened as a
result: it asserted the parsed name list was *empty*, which held only because the
old stub defined nothing; it now asserts the entry point is absent while the
surface names are present, which is the property it was really about.

## 13. Tests

All fifteen pure/static suites, run at the work commit.

| suite | checks | failures |
|---|---:|---:|
| `test_e1a_v4_terminal_calibration.py` | 538 | 0 |
| `test_e1a_v4_release_authority.py` | 1205 | 0 |
| `test_e1a_v4_driver_endpoints.py` | 308 | 0 |
| `test_e1a_v4_coherence_hardening.py` | 138 | 0 |
| `test_e1a_v4_repair.py` | 126 | 0 |
| `test_e1a_v4.py` | 122 | 0 |
| `test_e1a_v4_generating_model.py` | 113 | 0 |
| `test_e1a_v4_plan_coherence.py` | 113 | 0 |
| `test_e1a_v4_case_scope.py` | 114 | 0 |
| `test_e1a_v4_size_semantics.py` | 113 | 0 |
| `test_e1a_v4_calibration_scope.py` | 105 | 0 |
| `test_e1a_v4_preexec.py` | 104 | 0 |
| `test_e1a_v4_contract_plan.py` | 75 | 0 |
| `test_e1a_v4_dispositions.py` | 64 | 0 |
| `test_e1a_v4_preexec_corrections.py` | 52 | 0 |

```text
SUITES ...................... 15
CHECKS ...................... 3290        (3183 before this stage, +107)
FAILURES .................... 0
OFFICIAL RNG USE ............ 0
RNG OBJECTS CONSTRUCTED ..... 0
TRAJECTORY COUNT ............ 0
CAMPAIGN JOBS ............... 0
CALIBRATION EXECUTIONS ...... 0
```

New permanent groups:

```text
F1f-e refusal-aware aggregation            the counterexample, all-refused and
                                           partial refusal at the frozen R
F1f-e validator and aggregator agree       the cross-layer invariant and every
                                           invalid absence that must still refuse
F1f-e the terminal result materialises     the complete miniature campaign,
                                           mixed reasons, restart round trip
F1f-e per-field count invariants           inconsistent evidence is refused
F1f-e refusal-aware runtime conformance    preflight detects a non-conforming
                                           runtime shape, behaviour or driver
```

Everything is a **deterministic unit fixture**: hand-written record dictionaries
and plain arithmetic. `ou_observations` is never called, no RNG object is
constructed, no calibration runs and no campaign job executes. Where a fixture
needed a small denominator the *declared replicate count* was reduced in a
deep-copied plan rather than the completeness guard being bypassed — and C3 and C4
were deliberately left at their frozen 400 and 2000, because the classifier
refuses a shrunk planned denominator and a shrunken fixture would have proved
nothing.

`test_e1a_v4_campaign_driver.py` **remains deferred and was NOT run.** Inspected
statically: it calls `execute_campaign` and `run_campaign`, which reach
`ou_observations` through `execute_replicate`, so it is trajectory-bearing. All 61
names it imports from `campaign_driver` still exist, so it stays import-compatible,
but no runtime status is claimed for it.

## 14. Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

No threshold, replicate count, nominal alpha, integer boundary, confidence method,
confidence level or endpoint definition changed. No refusal tolerance was
introduced — one structured refusal affecting a required primary endpoint is still
sufficient. No pooling, no ANY_FIELD or EVERY_FIELD reduction: nothing in the
aggregation path computes `any(...)` or `all(...)` across fields, and field
statuses combine only at final campaign classification.

The authority documents are byte-unchanged:

```text
docs/e1a/e1a_v4_synthetic_validation_plan.json      UNCHANGED
docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md        UNCHANGED
docs/e1a/e1a_v4_design_contract.json                UNCHANGED
docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md               UNCHANGED
docs/physical_foundation/...CANONICAL.md            UNCHANGED
docs/theory/EBU_THEORY_BASELINE.md                  UNCHANGED
docs/e1a/e1a_v4_seed_map.json                       UNCHANGED
plan version                                        1.15.0, unchanged
```

### Identities

Recomputed twice from independent clean `git archive` extractions of the work
commit; both agreed.

```text
analysis identity   dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                    UNCHANGED -- no analysis-bound scientific module was modified

execution identity  e48ebae7d3ace30546adc67e9a481b2434b128e59594a3275873141ef26e13bd
                 -> 7abea4513757d89fcb6a4eeb3893cb05a156521e5fad99fd38f7dde12d644ac2
                    MOVED, as a runtime change must. NOT FROZEN.
```

## 15. Campaign status

```text
OFFICIAL RESULTS = NONE
OFFICIAL CAMPAIGN JOBS = 0
OFFICIAL TRAJECTORIES = 0
FINAL EXECUTION SEAL = NOT FROZEN
EXECUTION AUTHORISED = FALSE
```

`results/e1a_v4_validation` does not exist. The seal is `PRE_DRIVER` with
`expected_execution_identity = None`; the plan's `execution_authorised` is `false`.

## 16. Remaining blockers

F1f-e closes the C3/C4 refusal-aware runtime gap and nothing else.

```text
F2  Negative-stiffness / gamma-sign authority
F3  PRNG choice
F4  Field construction / absolute drag inputs
F5  Generator identity
F6  C6 implementation inputs
F7  Remaining C8 implementation inputs
F8  Diagnostic aggregator
```

Also open: the trajectory-bearing integration validation
(`test_e1a_v4_campaign_driver.py`) remains deferred;
`resolve_job_specification` still refuses for every job, naming the gaps F3–F5
supply; and the per-case mandatory diagnostic aggregator is still not supplied
(F8). A successful F1f-e does **not** mean seal ready, campaign ready or execution
authorised.

## 17. Next stage

```text
F1f-f INDEPENDENT REFUSAL-AWARE RUNTIME AUDIT
READY
```

Not begun, and not authorised here.

---

C3/C4 REFUSAL-AWARE RUNTIME REPAIR COMMITTED
