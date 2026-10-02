# E1a v4 — structured-refusal record integrity hardening (F1f-g)

Bounded repair of **malformed-record acceptance** found by the independent runtime
audit of F1f-e. The structured-refusal science is unchanged: this stage decides
nothing new, it checks that the records the already-approved rule is applied to are
the records the frozen pipeline can actually produce.

```text
STARTING COORDINATE
  work commit    3cd1b171de88ab25aab68b40c5ffa1099bf2b693   (F1f-e runtime repair)
  report commit  bbf8b03536f038b2e453038c5ee486d894203b82
  tree           clean
  branch         gaussian/stage-a-environment
```

```text
THIS STAGE
  work commit    d01623617b105fb5ff0a5e16b2599acaf477368b
  work tree      f420d5412287ff5faebd4adcb701bf3efdf09cc3
```

The auditor confirmed the intended `NOT_EVALUABLE` semantics and found three
bounded validation gaps. All three are repaired below, each as a permanent
regression.

---

## Auditor counterexamples

Every counterexample was **reproduced before any edit**, at `bbf8b03`, by pure
deterministic calls against the frozen plan. No RNG, no trajectory, no job.

### A — unknown analysis status

```text
record
  {"analysis_status": "NOT_A_REAL_STATUS", "P1": false, "p1_rejected": true,
   "block1_rejected": null, "g5_rejected": null}

BEFORE
  is_structured_refusal(record, "g5_rejected")      -> True      ACCEPTED
  is_structured_refusal(record, "block1_rejected")  -> True      ACCEPTED
  require_endpoint_events(plan, "C3_g5_block", ...) -> ACCEPTED  (no refusal)
  require_endpoint_events(plan, "C4_surrogate_validity", ...) -> ACCEPTED
```

Cause, `e1a_v4/validation/campaign_driver.py` (F1f-e revision):

```python
and outcome["analysis_status"] != ESTIMATED_STATUS)
```

A literal inequality against one string. **Every** other string satisfies it — a
typo, a renamed status, a status from another pipeline — so an unrecognised status
authorised an undefined primary endpoint and the field went on to be reported
`NOT_EVALUABLE` on evidence that established nothing.

```text
AFTER
  all four calls above REFUSE with ENDPOINT_EVENT_MISSING
```

### B — recognised refusal status with a non-fail-closed composite P1

```text
record
  {"analysis_status": "RANK_GUARD_FAIL", "P1": true, "p1_rejected": false,
   "block1_rejected": null, "g5_rejected": null}

BEFORE
  is_structured_refusal(record, "g5_rejected")      -> True      ACCEPTED
  require_endpoint_events(plan, "C3_g5_block", ...) -> ACCEPTED  (no refusal)
```

The record asserts both that the analysis never reached `ESTIMATED` **and** that
the two-block gate passed. No part of the frozen pipeline can produce it. The
predicate accepted it because it never looked at P1 at all.

```text
AFTER
  REFUSES with ENDPOINT_EVENT_MISSING, in both the validator and the aggregator
```

### C — refusal-reason counts that do not balance

```text
FieldSizeOutcome(field_id="theta0_circular", planned_replicates=400,
                 evaluable=399, structured_refusals=1, rejections=0,
                 refusal_reasons=<below>)

BEFORE
  {}                     -> ACCEPTED    one refusal, NO reason attributed
  {"A": 2, "B": -1}      -> ACCEPTED    sums to 1 by cancelling a negative
  {"A": 1.0}             -> ACCEPTED    float
  {"A": True}            -> ACCEPTED    bool read as the integer 1
  {"A": "1"}             -> TypeError   an uncoded crash, not a refusal
  structured_refusals=0, {"A": 3}  -> correctly refused (pre-existing)
```

Cause, `e1a_v4/validation/classification.py`:

```python
total = sum(self.refusal_reasons.values())
if total and total != self.structured_refusals:
```

The leading `if total and ...` **disables the check whenever the reasons sum to
zero**, which is exactly the empty-attribution case. There was no type check and
no sign check, so `{A: 2, B: -1}` passed the arithmetic too.

```text
AFTER
  every row above REFUSES, each with a coded Refusal rather than a TypeError
```

---

## Canonical status validation

The roster is **read, never retyped**. Its source is:

```text
e1a_v4/status.py
    class AnalysisStatus(str, Enum)        10 declared members
    NON_ESTIMATED = frozenset(s for s in AnalysisStatus
                              if s is not AnalysisStatus.ESTIMATED)
```

`e1a_v4/status.py` is listed in `e1a_v4/identity.py::SCIENTIFIC_MODULES`, so
editing it would move the frozen **analysis procedure identity**. It is therefore
imported and read, and not modified. The derived sets live in
`e1a_v4/validation/classification.py`, which is a validation module:

```text
DECLARED_ANALYSIS_STATUSES   every AnalysisStatus value                  (10)
ESTIMATED_STATUS             AnalysisStatus.ESTIMATED.value
NON_FAIL_CLOSED_STATUSES     {GEOMETRY_FAIL}                              (1)
REFUSAL_AUTHORISING_STATUSES NON_ESTIMATED values - NON_FAIL_CLOSED       (8)
```

### Per-status determination (not "every non-ESTIMATED status is alike")

The statuses were **not** treated as interchangeable. Each was decided against
`e1a_v4/endpoints.py::p1_geometry`, whose first statement is

```python
if not analysis.is_estimated and analysis.status not in (AnalysisStatus.GEOMETRY_FAIL,):
    return EndpointResult("P1", False, f"fail-closed on status {analysis.status.value}")
```

| status | authorises an undefined block decision? | why |
|---|---|---|
| `ESTIMATED` | **no** — the decision must EXIST | the gate produced its rows |
| `BRANCH_A_INVALID` | yes | fail-closed return, `rows = ()` |
| `NON_POSITIVE_DEFINITE` | yes | fail-closed return |
| `RANK_GUARD_FAIL` | yes | fail-closed return |
| `N_EFF_UNSUPPORTED` | yes | fail-closed return |
| `MODE_UNRESOLVED` | yes | fail-closed return |
| `CALIBRATION_MISSING` | yes | fail-closed return |
| `CALIBRATION_IDENTITY_MISMATCH` | yes | fail-closed return |
| `ANALYSIS_INVALID` | yes | fail-closed return |
| `GEOMETRY_FAIL` | **no** | the ONE status the guard excludes |

`GEOMETRY_FAIL` is carried **past** the fail-closed return and scored against real
gate statistics, so it either yields **defined** block decisions or raises an
outright `Refusal`. It never leaves a block decision undefined, and
`p1_block_decisions` already documented the same thing — `(None, None)` arises
"exactly when the analysis was not ESTIMATED **and P1 failed closed**".

This exclusion is **latent-state hardening with no reachable behaviour change**:
`GEOMETRY_FAIL` is declared in the enum but constructed nowhere in the repository.
`analyse_field` produces only `ESTIMATED`, `BRANCH_A_INVALID`, `ANALYSIS_INVALID`,
`RANK_GUARD_FAIL` and `NON_POSITIVE_DEFINITE`. The exclusion is proved against
`p1_geometry`'s actual behaviour — the endpoint is called once per declared status
with an analysis carrying no gate statistics — rather than asserted, so a future
edit to the guard breaks the test instead of silently widening the rule.

---

## Fail-closed invariant

The P1 rule is **pre-existing and unmodified**. Two frozen facts define it:

```text
e1a_v4/endpoints.py        p1_geometry returns EndpointResult("P1", False, ...)
                           for every status above that authorises a refusal

campaign_driver.evaluate_replicate   the record assembly, verbatim:
    "P1":          bool(result.passed)
    "p1_rejected": bool(not result.passed)
```

So for an authorised refusal the frozen pipeline writes, necessarily,
`P1 = False` and `p1_rejected = True`. That state is now what terminal-record
validation requires:

```python
FAIL_CLOSED_P1_STATE = (("P1", False), ("p1_rejected", True))
...
return all(outcome.get(name) is expected for name, expected in FAIL_CLOSED_P1_STATE)
```

Compared with `is`, not `==`: an integer `1` or `0` arriving from a loosely typed
producer is not the frozen boolean state, and `1 == True` would have concealed
that. A missing `P1` or `p1_rejected` key does not express the state either, so it
refuses — the record is validated for what it **affirms**, never for what it omits.

No new P1 semantic is introduced. P1 is not recomputed, and the composite P1
result is still never substituted for the missing block decision.

---

## Refusal-authorisation helper

One rule, one definition, three consumers:

```text
classification.authorises_undefined_block_decision(outcome)      THE rule
    |
    +-- campaign_driver.is_structured_refusal(outcome, event)    delegates
    |       |
    |       +-- require_endpoint_events      the endpoint VALIDATOR
    |       +-- field_primary_outcome        the per-field AGGREGATOR
    |
    +-- release_authority.require_per_field_implementation_conformance
            probed DIRECTLY at preflight
```

The driver function keeps the **shape** question — is `event` one of
`BLOCK_DECISION_EVENTS`, and is its key present and null (an absent key is a
malformed record, not a refusal). The classifier function keeps the
**authorisation** question. The original F1f-e defect was two layers holding two
definitions; that remains structurally impossible.

The rule moved out of the driver for a specific reason: preflight must be able to
**probe its behaviour**, and preflight cannot import the driver — importing would
execute driver code the pre-execution stage forbids, which is why
`release_authority` checks the driver surface by parsing its AST. The driver still
declares `is_structured_refusal`, so `REFUSAL_AWARE_DRIVER_SURFACE` and its AST
check are unaffected.

---

## FieldSizeOutcome invariants

Exact constructor checks, in order. Every one raises a coded `Refusal`:

```text
 1  planned_replicates is a strict non-negative int        (bool excluded)
 2  planned_replicates >= 1
 3  evaluable, structured_refusals, rejections are strict non-negative ints
 4  each of those three lies in [0, planned_replicates]
 5  rejections <= evaluable
        a rejection is a DEFINED decision and cannot exceed the decisions
        that exist
 6  evaluable + structured_refusals == planned_replicates
        every planned replicate accounted for exactly once; a silently
        discarded record refuses
 7  refusal_reasons is a Mapping
 8  every reason key is a NON-EMPTY string
 9  every reason count is a strict non-negative int        (bool excluded)
10  sum(reason counts) == structured_refusals              UNCONDITIONAL
11  structured_refusals == 0  =>  refusal_reasons == {}
```

Rules 1, 3 and 7–11 are new in F1f-g. Rules 2 and 4–6 are the F1f-e invariants,
preserved. The type checks run **before** the arithmetic, because
`{A: 2, B: -1}` sums correctly and is still nonsense.

---

## Reason accounting

```text
each count    strict non-negative int; bool, float, str and None all REFUSE
each key      non-empty str
the sum       MUST equal structured_refusal_count, unconditionally
zero case     structured_refusals == 0 requires the EMPTY mapping
```

`bool` is excluded explicitly. Python makes `True` an `int` worth 1, so an
unguarded `isinstance(value, int)` would have read `{reason: True}` as "one
refusal" — an accident of the type system, not a recorded count.

**Reason-key vocabulary (§13 determination): NO closed vocabulary exists, and none
was invented.** The evidence:

```text
results.ResultRecord.refusal_reason : str | None        free text
results.RESULT_FIELDS               carries refusal_reason, no roster
the frozen plan                     names `refusal_reasons` among
                                    required_terminal_counts but declares
                                    NO key roster
"REFUSED_ACCESSIBLE_SPACE"          appears only as a preflight probe
                                    fixture; it is not authority
```

Per §13 the "NO" branch therefore applies: count arithmetic and type integrity are
enforced, keys are required only to be nameable, and **no refusal-reason
vocabulary is created in this task**.

The zero case follows the existing schema convention rather than inventing an
alternative: both producers emit `{}` when nothing refused —
`field_primary_outcome` builds the map from the refusals it actually saw, and
`classify_field_size` writes `{}` on the fully evaluable branch — so a key
counting its reason zero times is not an alternative spelling of "nothing
refused", and refuses.

---

## Positive regressions

Valid refusal records still behave exactly as the G5 amendment requires:

```text
the canonical refusal record is accepted in BOTH block events
a valid refusal survives a genuine JSON round trip and both layers accept it
C3 / C4 all-refused            -> NOT_EVALUABLE, planned R preserved
partial refusal                -> NOT_EVALUABLE, defined rejections retained
reason attribution balances    -> {REFUSED_ACCESSIBLE_SPACE: 1} for 1 refusal
sound accounting ACCEPTED      one reason; two distinct reasons; one repeated
                               reason counted twice; the empty zero form
structured_refusals > 0        -> the primary verdict is NOT_EVALUABLE
structured_refusals == 0       -> NEVER NOT_EVALUABLE, at 0, at the boundary
                                  and one over it
```

## Negative regressions

Every malformed authorisation claim refuses, in **both** block events and in
**both** layers:

```text
an analysis status outside the declared roster
a status differing from a declared one only in case
a whitespace-padded status
NO analysis status at all
a null analysis status
a non-string analysis status
an ESTIMATED analysis status
a status the frozen gate does not fail closed on
a composite P1 that PASSED
P1 passed while p1_rejected still says rejected
p1_rejected cleared while P1 still says failed
no composite P1 field at all
no p1_rejected field at all
integers 0/1 standing in for the frozen booleans
```

and every unsound accounting refuses on construction:

```text
a refusal with NO reason attributed
reasons balancing only because a NEGATIVE cancels a positive
a negative count even where the total is right
a reason attributed where NOTHING refused
a zero-valued reason key standing in for the empty mapping
reasons that over-account the refusals
float / bool / str reason counts
an empty reason key; a non-string reason key
reason counts that are not a mapping at all
a bool structured-refusal count
a float planned denominator; a float rejection count
```

**The F1f-e distinction is preserved**: a recognised structured refusal is
accepted and aggregated as `NOT_EVALUABLE`; an arbitrary missing endpoint still
raises `ENDPOINT_EVENT_MISSING`. The hardening did not turn `None` into a
legitimate refusal — it narrowed which records may carry one. An `ESTIMATED`
record with a missing block decision still refuses, tested in both directions.

Preflight itself is tested for detection, not just for passing. Four weakened
authorisation rules — including the exact F1f-e rule the audit broke — and a
permissive evidence class are substituted in turn, and
`require_per_field_implementation_conformance` must refuse each with
`IMPLEMENTATION_AUTHORITY_LAG`.

## All-refused and mixed-reason regressions

Re-run unchanged from F1f-e, and still green:

```text
ALL-REFUSED   the terminal result EXISTS; every C3 field (planned 400,
              evaluable 0, refusals 400) and every C4 field (planned 2000,
              evaluable 0, refusals 2000) is NOT_EVALUABLE; the campaign
              cannot PASS; reason counts are retained and now satisfy the new
              accounting invariants; no size failure is fabricated

MIXED         2 VALIDATION_INCONCLUSIVE and 2 STATISTICAL_SIZE_FAILURE
              coexist, each naming its own case and field; clean fields stay
              clean; neither reason erases the other

RESTART       recovered aggregation equals fresh aggregation; nulls survive;
              a malformed persisted record REFUSES on recovery rather than
              being normalised into a refusal
```

---

## C2

```text
UNCHANGED
```

`c2_rejections_by_field` remains `Mapping[str, int]` — plain counts, by design.
`p1_rejected` is not in `BLOCK_DECISION_EVENTS`, so C2 has no structured-refusal
path and acquires no `NOT_EVALUABLE` pathway. Its composite P1 endpoint fails
closed, so its elementary event is defined for every replicate including a
refusal. The frozen scope-out is untouched:
`derived_boundaries.C2.undefined_primary_endpoint_possible = false`,
`verdict_on_structured_refusal = "NOT_APPLICABLE"`.

## Cross-field / case science

```text
C2  composite P1, existing fail-closed semantics      unchanged
C3  PER FIELD / G5 Block-2 primary                    unchanged
C4  PER FIELD / Block-1 primary                       unchanged
pooling                FORBIDDEN                      unchanged
cross-field reduction  NONE                           unchanged
alphas, boundaries, planned R                         unchanged
```

---

## Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

This stage validates records; it does not redefine an endpoint, a threshold, a
denominator or a verdict. No authority file was touched, and every authority hash
is byte-identical to its F1f-d/F1f-e value:

```text
physical foundation    6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
theory baseline        0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa
design contract        91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
prospective design     e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495
validation plan JSON   dcf0c575a048ceebfcd3deb261d1a76ff269bfb16178a531b8911b5bdf8808ec
validation plan MD     5b76c3095ecbf5bc0f0273f2b83da8fab2d0c51154efc7628031b6445a4fbb18
seed map               95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce
structured-refusal amendment   unmodified
plan version           1.15.0
```

### Identities

```text
analysis procedure identity   dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                              UNCHANGED, as required

execution identity            7abea4513757d89fcb6a4eeb3893cb05a156521e5fad99fd38f7dde12d644ac2
                           -> 03b98b8ee4265e27a139979092b63eb8f60f3727cce97c6a9bbc25c13bd24354
                              MOVED, legitimately and expectedly, and NOT FROZEN
```

Both values were recomputed **twice, from two independent clean `git archive`
extractions of `d016236`**, and the two extractions agree in every field.

The analysis identity cannot move: it hashes `SCIENTIFIC_MODULES`, and this stage
edited none of them. The execution identity hashes `VALIDATION_MODULES` plus the
canonical driver, three of which changed, so it moves; the seal remains
`PRE_DRIVER` with `expected_execution_identity = None`, so nothing is contradicted.

### Schema versioning

```text
NO VERSION BUMP, and no migration
```

Construction became stricter; the **serialized shape did not change**.
`RESULT_FIELDS`, `ResultRecord`, `RESULT_SCHEMA` and `MANIFEST_SCHEMA` are
untouched, and `CAMPAIGN_RESULT_SCHEMA` stays `e1a_v4_campaign_result/3`. No field
was added or removed, so there is nothing to migrate and no persisted artifact to
reinterpret — and none exists at any version.

---

## Changed files

```text
e1a_v4/validation/classification.py     the canonical authorisation rule, the
                                        derived status sets, the strict count
                                        helper, the FieldSizeOutcome invariants
e1a_v4/validation/campaign_driver.py    is_structured_refusal delegates; the
                                        local string blacklist removed
e1a_v4/validation/release_authority.py  preflight record-integrity probes
test_e1a_v4_driver_endpoints.py         record-integrity regressions
test_e1a_v4_size_semantics.py           reason-accounting regressions
test_e1a_v4_release_authority.py        preflight-detection regressions
```

---

## Test results

```text
suite                                      checks   failures   delta
test_e1a_v4_release_authority.py             1213          0      +8
test_e1a_v4_terminal_calibration.py           538          0       0
test_e1a_v4_driver_endpoints.py               360          0     +52
test_e1a_v4_coherence_hardening.py            138          0       0
test_e1a_v4_size_semantics.py                 138          0     +25
test_e1a_v4_repair.py                         126          0       0
test_e1a_v4.py                                122          0       0
test_e1a_v4_case_scope.py                     114          0       0
test_e1a_v4_generating_model.py               113          0       0
test_e1a_v4_plan_coherence.py                 113          0       0
test_e1a_v4_calibration_scope.py              105          0       0
test_e1a_v4_preexec.py                        104          0       0
test_e1a_v4_contract_plan.py                    75          0       0
test_e1a_v4_dispositions.py                     64          0       0
test_e1a_v4_preexec_corrections.py              52          0       0
-----------------------------------------------------------------
TOTAL                                        3375          0     +85
                                   (3290 before this stage)
```

Every previously green authority suite stayed green and none was weakened: C2
derived binding, C3/C4 per-field authority, the structured-refusal amendment,
normative-surface totality, nested-leaf totality, list totality, plan coherence,
contract-plan conformance, strict JSON and release authority all pass unchanged.

The three new regression groups:

```text
test_e1a_v4_driver_endpoints.py    "F1f-g structured-refusal record integrity"
                                   unknown / missing / malformed status, the
                                   fail-closed P1 relation, the GEOMETRY_FAIL
                                   exclusion proved against p1_geometry itself,
                                   and both layers agreeing on every case
test_e1a_v4_size_semantics.py      "refusal-reason accounting (F1f-g)"
                                   strict type, non-negativity, sum and zero-form
                                   invariants; status/verdict consistency both ways
test_e1a_v4_release_authority.py   preflight DETECTION: four weakened
                                   authorisation rules and a permissive evidence
                                   class must each be refused
```

Preflight cost is unchanged: the whole `bind_execution` preflight measures 3.30s
against the 3.47s F1f-e baseline, and the conformance check 0.57s against 0.60s.
The new probes are dictionary and dataclass work only — no Clopper-Pearson bound
and no filesystem record — so they are free at this scale.

---

## Execution status

```text
OFFICIAL CAMPAIGN = NOT RUN
OFFICIAL TRAJECTORIES = 0
FINAL EXECUTION SEAL = NOT FROZEN
EXECUTION AUTHORISED = FALSE
```

```text
REAL RNG OBJECTS ............. 0
SCIENTIFIC RANDOM DRAWS ...... 0
OU TRAJECTORIES .............. 0
CALIBRATION EXECUTIONS ....... 0
OFFICIAL CAMPAIGN JOBS ....... 0
results/e1a_v4_validation .... does not exist
execution seal state ......... PRE_DRIVER
```

`test_e1a_v4_campaign_driver.py` **remains a KNOWN DEFERRED TEST** and was not
executed. It is still trajectory-bearing through
`execute_campaign -> execute_replicate -> ou_observations`. It was inspected
statically only: all 105 names it imports from `e1a_v4` still resolve, so this
repair did not break it. **No runtime status is claimed for that suite.**

---

## Limitations

This is record-integrity hardening, not execution readiness. Still open:

```text
F2  Negative-stiffness / gamma-sign authority
F3  PRNG choice
F4  Field construction / absolute drag inputs
F5  Generator identity
F6  C6 implementation inputs
F7  Remaining C8 implementation inputs
F8  Diagnostic aggregator
```

Trajectory-bearing integration validation also remains deferred.

---

## Next stage

```text
F1f-h INDEPENDENT RE-AUDIT
READY
```

Not begun, and not authorised by this report.

---

```text
STRUCTURED-REFUSAL RECORD INTEGRITY HARDENING COMMITTED
```
