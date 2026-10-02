# E1a v4 — endpoint decision-domain and composite P1 consistency (F1f-i)

Bounded runtime-integrity repair closing the three malformed-record paths the
independent re-audit found after the whole-record repair. No scientific decision
is made here.

```text
STARTING COORDINATE
  work commit    e6b2ac00c6b9e74123089b2fbce2c2e03969a848
  work tree      443d74b76bb87554b7b81721318898ff7922d0b8
  report commit  b79b9ce3e049f68ef15d52648d6426ff761f62c6
  tree           clean
  branch         gaussian/stage-a-environment
```

```text
THIS STAGE
  work commit    51d7f80804385573af6861e2359bf47f0a7e2e7b
  work tree      cf41a848f25449ea3ae01aa3acd40e529effc224
```

The re-audit confirmed the previous repair's two guarantees, and both still hold:
mixed defined/undefined block decisions refuse, and an invented or undeclared
analysis status refuses.

---

## Auditor counterexamples

All three were reproduced **before any edit** at `b79b9ce`, by pure deterministic
calls against the frozen plan. No RNG, no trajectory, no job.

### Gap A — partial / omitted block decisions

```text
record   analysis_status = ESTIMATED, P1 = true, p1_rejected = false
         block1_rejected OMITTED
         g5_rejected     = false

BEFORE   whole-record rule        SOUND
         C3 validator             ENDPOINT_EVENT_MISSING
         C3 aggregator            ACCEPTED  ev=1 ref=0 rej=0
                                  -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED
         C2 validator             ENDPOINT_EVENT_MISSING
         C2 aggregator            ACCEPTED  counts all zero
```

The mirror image — `g5_rejected` omitted, `block1_rejected = false` — did the same
to C4. With **both** omitted, C3 and C4 refused but **C2's counter still accepted
the record**. In every variant the validator refused and an aggregator counted:
precisely the split the previous stage was supposed to have closed, surviving
because the previous rule asked only about the two block fields and said nothing
when one was absent entirely.

### Gap B — non-boolean defined block decisions

```text
record   analysis_status = ESTIMATED, g5_rejected = "false"

BEFORE   whole-record rule        SOUND
         C3 validator             ACCEPTED
         C3 aggregator            ACCEPTED  ev=1 ref=0 rej=1
                                  -> STATISTICAL_SIZE_FAILURE
```

Both layers accepted it, and the counter read `bool("false")`, which is `True`.
**A string spelling the word "false" was counted as a G5 rejection.** The same
happened for `block1_rejected = "false"` against C4, and for the integer `1`.

### Gap C — composite P1 contradicting the block decisions

```text
record   analysis_status = ESTIMATED
         block1_rejected = true,  g5_rejected = false
         P1 = true,               p1_rejected = false

BEFORE   whole-record rule        SOUND
         validator and aggregator ACCEPTED for C2, C3 and C4
```

`p1_geometry` passes P1 only when neither block rejects, so this record asserts
both that Block-1 rejected and that the composite gate passed.

---

## Canonical endpoint state machine

Read off `evaluate_replicate`, which writes the composite-P1 group in **one**
`row.update(...)` or not at all:

```text
STATE A — ESTIMATED_RECORD
    analysis_status    a declared status that does NOT fail the gate closed
    block1_rejected    strict bool
    g5_rejected        strict bool
    P1, p1_rejected    strict bools, EXACTLY as the frozen two-block
                       composition derives them from the two above

STATE B — STRUCTURED_REFUSAL_RECORD
    analysis_status    a declared status that fails the gate closed
    block1_rejected    None
    g5_rejected        None
    P1 = False, p1_rejected = True      the frozen fail-closed state
    the C3/C4 primary endpoint is UNDEFINED -> NOT_EVALUABLE
```

Any hybrid refuses.

**A third state exists and is the pipeline's own, not an invention.**
`evaluate_replicate` writes the group only when the field has a calibration
condition, and the frozen plan declares `uses_p1_block1 = false` for **C7 and
C8** — so their records legitimately carry no composite-P1 group at all:

```text
STATE C — NO_P1_DECISION_GROUP
    none of the four fields present
```

Refusing State C would have refused every valid C7 and C8 record. Whether a case
*requires* the group is a separate question, already answered from the frozen plan
by `required_endpoint_events`; the state machine governs only what a record that
carries the group may look like.

The single entry point is `classification.classify_record(outcome)`, returning
`(state, failure)` with exactly one of the two set. `record_state` and
`record_consistency_failure` are thin accessors over it, so there is one
implementation and no parallel partial truth table.

---

## Strict Boolean domain

```text
ACCEPTED   True, False            (identity against the two singletons)
REFUSED    "false" "true" "0" "1" ""
           0  1
           0.0  1.0
           []  {}
           any other object
           None, where a definition is required
```

`is_strict_bool` uses `value is True or value is False`. Identity, not
`isinstance`: `bool` is a subclass of `int`, so an `isinstance(value, int)` guard
would admit `True` while an `isinstance(value, bool)` guard would still reject
`1` — identity makes the intent exact and unmistakable.

The domain is enforced on `block1_rejected`, `g5_rejected`, **and** the composite
`P1` and `p1_rejected`.

### No truthiness coercion

Both counters previously read `bool(result[event])`. Both now read
`endpoint_decision(result, event, where)`, which returns the recorded value when
it is a strict boolean and refuses otherwise. A scientific decision is **consumed
as recorded, never coerced**: guessing what a malformed value meant is how a data
defect becomes a result. The only surviving `bool(...)` calls on these fields are
in `p1_block_decisions` and `evaluate_replicate`, where they *construct* the
decision from a comparison — construction, not consumption.

---

## P1 truth table

From `endpoints.p1_geometry`: `passed = not (block1_reject or block2_reject)`, a
union bound valid under **arbitrary dependence** between the blocks.

| block1_rejected | g5_rejected | P1 | p1_rejected |
|---|---|---|---|
| False | False | **True** | False |
| False | True | False | **True** |
| True | False | False | **True** |
| True | True | False | **True** |

`classification.composite_p1_from_blocks` states this once and is used by both
validation and the test fixtures. It **never produces a record**:
`evaluate_replicate` still records what the frozen endpoint's own `passed`
returned. `endpoints.py` was deliberately not extended to expose the relation,
because it is an analysis-bound scientific module and editing it would move the
frozen analysis procedure identity.

All four combinations are tested in both directions: the correct composite is
accepted and reaches `ESTIMATED_RECORD`, and every contradictory composite for
each pair refuses.

---

## Missing-vs-None semantics

The serialized `ResultRecord` schema (`RESULT_FIELDS`) carries `P1` but **not**
`p1_rejected`, `block1_rejected` or `g5_rejected`; those live in the per-field
`result` mapping that `evaluate_replicate` builds. So required presence is not a
flat schema rule — it is:

```text
WHO REQUIRES THE GROUP   required_endpoint_events, from the frozen plan's
                         uses_p1_block1 (true for C1-C6, false for C7/C8)

HOW IT IS WRITTEN        all four together in one update, or none of them

THEREFORE
    a PARTIAL group                         -> REFUSE
    an absent group on a case that needs it -> ENDPOINT_EVENT_MISSING
    an absent group on C7 / C8              -> NO_P1_DECISION_GROUP, valid
```

Omission is **never** normalized into `None`. A valid structured refusal must
carry both keys explicitly set to `None`; dropping them is a partial group and
refuses. This matters because the two mean different things scientifically —
`None` says the gate ran and produced nothing, absence says nothing at all — and
the audit showed absence being read as a clean non-rejection.

---

## Shared validation

```text
classification.classify_record            THE invariant
    |
    +-- campaign_driver.require_consistent_record     the single raise site
    |       |
    |       +-- require_endpoint_events     endpoint VALIDATION (every case)
    |       +-- field_primary_outcome       C3 / C4 three-state aggregation
    |       +-- field_event_count           C2 / C6 counting
    |
    +-- release_authority preflight         probed directly, no driver import
```

A **parity matrix** of thirteen record shapes is run through validation and
aggregation for C2, C3 and C4 — thirty-nine combinations — asserting the
invariant: where validation refuses, no aggregator accepts; where validation
accepts, every aggregator accepts. The refusal *code* may differ between layers
(an absent decision is `ENDPOINT_EVENT_MISSING`, an impossible combination is
`TERMINAL_RECORD_INCONSISTENT`), but the outcome never does.

### Error codes

No new code was introduced. All three new defect classes are
`TERMINAL_RECORD_INCONSISTENT`: each is a record whose own fields contradict the
declared domain, and the reason string names the exact violation. A genuinely
absent decision keeps `ENDPOINT_EVENT_MISSING`, so the existing distinction and
every earlier expectation survive unchanged.

---

## C2

```text
SCIENTIFIC SEMANTICS UNCHANGED
```

C2 still counts the composite P1 event per field over its frozen 400 replicates,
with no pooling, no cross-field reduction and **no `NOT_EVALUABLE` pathway**. A
valid structured-refusal record still contributes its canonical fail-closed C2 P1
event exactly as before. What changed is only that an impossible terminal record
can no longer enter the count:

```text
BEFORE   both block decisions omitted under ESTIMATED -> C2 counted the record
AFTER    TERMINAL_RECORD_INCONSISTENT
BEFORE   g5_rejected = "false"                        -> C2 counted the record
AFTER    TERMINAL_RECORD_INCONSISTENT
```

and a sound record counts to exactly the same per-field totals as before, verified
across all four `(block1, g5)` combinations.

## C3 / C4

```text
SCIENTIFIC SEMANTICS UNCHANGED
```

```text
valid ESTIMATED record    C3 uses the actual strict-bool G5 decision
                          C4 uses the actual strict-bool Block-1 decision
valid structured refusal  C3 -> NOT_EVALUABLE, C4 -> NOT_EVALUABLE
                          planned R preserved, refusal reasons retained
```

The all-refused terminal report is still produced, and a `NOT_EVALUABLE` field and
a `STATISTICAL_SIZE_FAILURE` field still both survive terminal assembly with their
own case and field named.

## Other shared consumers

`field_event_count` is the counter for **both C2 and C6** — C6 reads
`p1_rejected` per rho subcondition. Hardening it covers C6 with **no scientific
change**: C6's per-rho count, its `cp_upper` comparison and its target are
untouched; it simply can no longer count an impossible record. C1, C7 and C8 read
replicate-level events (`complete_pass`, `false_acceptance`, `scale_recovered`)
with `is True` identity comparisons, which were already coercion-free.

---

## Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

No endpoint, threshold, alpha, boundary, denominator or verdict moves. No
authority file was touched; every authority hash is byte-identical:

```text
physical foundation    6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
theory baseline        0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa
prospective design     e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495
design contract        91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
validation plan JSON   dcf0c575a048ceebfcd3deb261d1a76ff269bfb16178a531b8911b5bdf8808ec
validation plan MD     5b76c3095ecbf5bc0f0273f2b83da8fab2d0c51154efc7628031b6445a4fbb18
refusal amendment      844d512f6ffe75a5...
seed map               95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce
plan version           1.15.0
```

### Identities

```text
analysis procedure identity   dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                              UNCHANGED

execution identity            4d2e74d2567c554b09337ff5f7ea891c4713df6044013efdbc70cdf9b3d1f353
                           -> baf2ad9dbf1710275ac20c47faafea6ace6a8910bf34a90194a287b9c237006a
                              MOVED, expectedly, and NOT FROZEN
```

Both were recomputed **twice, from two independent clean `git archive`
extractions** of the work commit, and the two agree in every field. The analysis
identity hashes `SCIENTIFIC_MODULES`, none of which this stage edited --
`endpoints.py` and `status.py` in particular are read, never modified. The
execution identity hashes `VALIDATION_MODULES` plus the canonical driver, three of
which changed. The seal stays `PRE_DRIVER` with
`expected_execution_identity = None`.

### Changed files

```text
e1a_v4/validation/classification.py     classify_record and the state machine,
                                        is_strict_bool, composite_p1_from_blocks,
                                        P1_DECISION_FIELDS
e1a_v4/validation/campaign_driver.py    endpoint_decision replaces both
                                        bool(result[event]) coercions
e1a_v4/validation/release_authority.py  decision-domain and truth-table preflight
                                        probes; endpoint_decision joins the
                                        declared driver surface
test_e1a_v4_driver_endpoints.py         the decision-domain regression group and
                                        the parity matrix; result_row now derives
                                        the composite P1 from its blocks
test_e1a_v4_release_authority.py        preflight-detection regressions
test_e1a_v4_terminal_calibration.py     two impossible fixtures corrected
```

---

## Tests

```text
suite                                      checks   failures   delta
test_e1a_v4_release_authority.py             1225          0      +6
test_e1a_v4_driver_endpoints.py               549          0    +158
test_e1a_v4_terminal_calibration.py           538          0       0
test_e1a_v4_coherence_hardening.py            138          0       0
test_e1a_v4_size_semantics.py                 138          0       0
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
TOTAL                                        3576          0    +164
                                   (3412 before this stage)
```

```text
SUITES RUN              15
SUITES NOT CLEAN         0
FAILURES                 0
REAL RNG OBJECTS         0
SCIENTIFIC RANDOM DRAWS  0
OU TRAJECTORIES          0
CALIBRATION EXECUTIONS   0
OFFICIAL CAMPAIGN JOBS   0
```

**A reporting defect in my own test runner was found and fixed during this
stage.** When `terminal_calibration` first crashed on the corrected invariant, the
runner printed `0 passed ? failed` and its totaliser silently skipped the
unparseable failure count, reporting "0 failures" for a batch that contained a
crashed suite. The runner now prints `NO SUMMARY LINE -- SUITE DID NOT COMPLETE`
with the tail of the output and counts the suite as not clean, which is why the
table above carries an explicit *suites not clean* figure. The earlier
intermediate figure of 3038 checks should be disregarded; it was a batch with one
suite missing, not a clean run.

The three new regression groups:

```text
test_e1a_v4_driver_endpoints.py   "F1f-i endpoint decision domain"
                                  the four-row truth table in both directions,
                                  the strict-boolean domain on all four fields,
                                  partial-group refusal, the three record states,
                                  a 13 x 3 validation/aggregation parity matrix
                                  with a real JSON round trip, and proof the
                                  hardening does not OVER-refuse: C2, C3 and C4
                                  counts are correct for all four (block1, g5)
                                  combinations
test_e1a_v4_release_authority.py  preflight DETECTION: a rule admitting a truthy
                                  decision, a composition that passes P1 unless
                                  BOTH blocks reject, and a classifier
                                  recognising no state must each be refused
```

Preflight cost is unchanged within noise: `bind_execution` 3.61s against the 3.47s
F1f-e baseline, conformance 0.58s against 0.60s.

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

`test_e1a_v4_campaign_driver.py` remains a **KNOWN DEFERRED TEST** and was not
executed; it is still trajectory-bearing through
`execute_campaign -> execute_replicate -> ou_observations`. Inspected statically
only: all 105 names it imports from `e1a_v4` still resolve. **No runtime status is
claimed for that suite.**

---

## Limitations

This is record-domain integrity, not execution readiness. Still open:

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
F1f-j INDEPENDENT RE-AUDIT
READY
```

Not begun, and not authorised by this report. Nothing here authorises sealing.

---

```text
ENDPOINT DECISION-DOMAIN HARDENING COMMITTED
```
