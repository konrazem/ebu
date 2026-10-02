# E1a v4 — whole-record consistency hardening (F1f-i)

Narrow consistency repair closing the one record-integrity gap the independent
re-audit found after F1f-g. No scientific decision is made here.

```text
STARTING COORDINATE
  work commit    d01623617b105fb5ff0a5e16b2599acaf477368b   (F1f-g hardening)
  report commit  a95c901c5fc38641f142c664c234e3f617a86d0e
  tree           clean
  branch         gaussian/stage-a-environment
```

```text
THIS STAGE
  work commit    e6b2ac00c6b9e74123089b2fbce2c2e03969a848
  work tree      443d74b76bb87554b7b81721318898ff7922d0b8
```

The re-audit confirmed the three F1f-g fixes as correct and reproduced the
corrected refusals over 498 checks in the two relevant pure suites, running no
campaign and changing nothing. It then found that record integrity was **not yet
fully closed**.

---

## What F1f-g got wrong

F1f-g asked its authorisation question **per event**, and only when that event's
decision was `None`:

```python
return (event in BLOCK_DECISION_EVENTS
        and event in outcome
        and outcome[event] is None
        and authorises_undefined_block_decision(outcome))     # only reached here
```

Two consequences, both real, both reproduced before any edit at `a95c901`:

### Finding 1 — one block decision undefined, the other defined

```text
record
  analysis_status  = RANK_GUARD_FAIL
  P1               = false
  p1_rejected      = true
  block1_rejected  = null
  g5_rejected      = false

BEFORE
  is_structured_refusal(record, "block1_rejected") -> True
  is_structured_refusal(record, "g5_rejected")     -> False
  C3 VALIDATOR   -> ACCEPTED
  C4 VALIDATOR   -> ACCEPTED
  C3 AGGREGATOR  -> ACCEPTED  evaluable=1 refusals=0 rejections=0
  C3 VERDICT     -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED
  C4 AGGREGATOR  -> ACCEPTED  evaluable=0 refusals=1 rejections=0
  C4 VERDICT     -> NOT_EVALUABLE
```

The record passes the per-event rule **twice**: the null block-1 decision is
authorised, and `g5_rejected` is never examined because it is not null. The
consequence is sharper than "an impossible record was accepted" — **the same
record made C3 and C4 disagree about whether the same replicate is evaluable**.
C4 read it as a structured refusal; C3 read it as a defined non-rejection and
reported a clean field.

### Finding 2 — an invented status with both decisions defined

```text
record
  analysis_status  = NOT_A_REAL_STATUS
  block1_rejected  = false
  g5_rejected      = false

BEFORE
  C3 / C4 VALIDATOR   -> ACCEPTED
  C3 / C4 AGGREGATOR  -> ACCEPTED  evaluable=1 refusals=0 rejections=0
  C3 / C4 VERDICT     -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED
```

Nothing consulted the status at all, because nothing was null. F1f-g bound the
status roster to the *undefined* path only, so an undeclared status flowed
straight through to a clean verdict.

---

## The frozen fact this rests on

```python
# campaign_driver.p1_block_decisions
rows = {gate: p for gate, _observed, p in getattr(result, "rows", ())}
if not rows or artifact is None:
    return None, None
...
return block1_rejected, g5_rejected
```

Both block decisions are read from **the same `rows`** the two-block gate either
produced or did not. The function returns `(None, None)` or `(bool, bool)`. It has
no branch that defines one and leaves the other undefined. A record that mixes them
describes no analysis the frozen pipeline can perform.

---

## The whole-record rule

`classification.record_consistency_failure(outcome) -> str | None` returns why a
record is impossible, or `None` if it is sound. Three conditions over the record as
a whole:

```text
DECLARED   analysis_status is a string in the canonical AnalysisStatus roster,
           WHATEVER the block decisions say. An unrecognised status describes no
           analysis the frozen pipeline can perform.

TOGETHER   the block decisions the record carries are ALL undefined or ALL
           defined, never a mixture.

AGREEING   all undefined  -> requires a status that fails the gate closed, plus
                             the frozen fail-closed composite P1 state
           all defined    -> requires a status that does NOT fail it closed,
                             because a gate that returned before computing a
                             p-value decided neither block
```

A record from a case that carries no block decisions at all is sound as far as
TOGETHER and AGREEING are concerned; only DECLARED applies to it.

The rule returns a reason string rather than raising, exactly as
`authorises_undefined_block_decision` returns a bool: preflight probes it as a pure
function. `campaign_driver.require_consistent_record` is the **single raise site**,
so the validator and both aggregators report the same finding in the same words.

### Relationship to the F1f-g rule

`authorises_undefined_block_decision` is kept and unchanged. It answers the
per-event question `is_structured_refusal` needs. The whole-record rule is the
layer above it, and reuses the same constants — `DECLARED_ANALYSIS_STATUSES`,
`REFUSAL_AUTHORISING_STATUSES`, `FAIL_CLOSED_P1_STATE` — so the two cannot
disagree about which statuses fail closed.

---

## Where it is enforced

```text
VALIDATION    require_endpoint_events          every case, every record
AGGREGATION   field_primary_outcome            C3 / C4 three-state evidence
AGGREGATION   field_event_count                C2 / C6 counting
```

**Aggregation is enforced separately from validation on purpose.**
`campaign_counts_from_records` never calls `require_endpoint_events` — the two are
genuinely different paths, which is the asymmetry that produced the original F1f-e
defect. A counter that trusted upstream validation would be trusting a call that
does not happen.

`field_event_count` is covered beyond the two findings the auditor named. C2 and C6
read `p1_rejected`, which is defined under a structured refusal, so they never take
the `NOT_EVALUABLE` path and neither finding reaches them through that route — but
they can still be handed the same impossible record, and counting one would put a
rejection into a frozen denominator on evidence that cannot exist. This is recorded
explicitly as a deliberate extension of scope, not a silent one. **C2's semantics
are untouched**: it still counts `p1_rejected` per field over its frozen 400, it
gains no `NOT_EVALUABLE` pathway, and a sound record counts exactly as before.

### Ordering, and why the existing refusal codes did not move

`require_consistent_record` runs **after** the per-event absence checks at every
call site. A record that is simply *missing* a decision stays
`ENDPOINT_EVENT_MISSING`; that distinction is worth keeping, and every F1f-g
expectation is preserved unchanged. The new rule fires only when every required
decision is present and the combination is still impossible, under a new code:

```text
TERMINAL_RECORD_INCONSISTENT
```

---

## Preflight

`require_per_field_implementation_conformance` now probes the whole-record rule
directly — three sound records that must be accepted, six impossible ones that must
be refused. The driver surface gains `require_consistent_record`:

```text
REFUSAL_AWARE_DRIVER_SURFACE
    is_structured_refusal
    require_consistent_record          <- new
    structured_refusal_reason
    field_primary_outcome
    per_field_primary_outcomes
```

The three sandbox driver stubs generate themselves from that tuple, so they
required no edit. The existing drop-one-name negative test covers the new entry
automatically.

Preflight is still probed for **detection**, not just for passing: four blunted
whole-record rules — one that never finds a record impossible, one that checks the
status but not the two decisions together, one that checks the decisions but not
the status, and one that refuses even a sound record — must each be refused with
`IMPLEMENTATION_AUTHORITY_LAG`.

---

## Regressions

The auditor's record is tested **through both layers, for both cases**, after a
genuine JSON round trip:

```text
C3 / C4  VALIDATION  refuses the mixed block decisions     TERMINAL_RECORD_INCONSISTENT
C3 / C4  AGGREGATION refuses the mixed block decisions     TERMINAL_RECORD_INCONSISTENT
C3 / C4  VALIDATION  refuses an invented analysis status   TERMINAL_RECORD_INCONSISTENT
C3 / C4  AGGREGATION refuses an invented analysis status   TERMINAL_RECORD_INCONSISTENT
C2       AGGREGATION refuses both of the above             TERMINAL_RECORD_INCONSISTENT
```

Sound records, unchanged:

```text
SOUND  a valid structured refusal: both decisions undefined
SOUND  a fully estimated record: both decisions defined
SOUND  an estimated record whose blocks both rejected
SOUND  a record carrying no block decisions at all
       both layers still accept the first two for C3 and for C4
       C2 still counts a sound record to exactly the same per-field totals
```

Impossible records, all refused:

```text
block-1 undefined while G5 is defined
block-1 undefined while G5 rejected
G5 undefined while block-1 is defined
an undeclared status with BOTH decisions defined
an undeclared status differing only in case
a non-string status with BOTH decisions defined
a fail-closed status with BOTH decisions defined
an ESTIMATED status with BOTH decisions undefined
a refusal whose composite P1 did not fail closed
a status the frozen gate does not fail closed on, both undefined
```

---

## Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

No endpoint, threshold, denominator, alpha, boundary or verdict moves. No
authority file was touched and every authority hash is byte-identical:

```text
physical foundation    6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
theory baseline        0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa
design contract        91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
prospective design     e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495
validation plan JSON   dcf0c575a048ceebfcd3deb261d1a76ff269bfb16178a531b8911b5bdf8808ec
validation plan MD     5b76c3095ecbf5bc0f0273f2b83da8fab2d0c51154efc7628031b6445a4fbb18
seed map               95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce
plan version           1.15.0
```

```text
C2   UNCHANGED      plain per-field counts, no NOT_EVALUABLE pathway
C3   PER FIELD / G5 Block-2 primary        unchanged
C4   PER FIELD / Block-1 primary           unchanged
pooling FORBIDDEN, cross-field reduction NONE, planned R preserved
serialized record shape unchanged; CAMPAIGN_RESULT_SCHEMA stays /3; no migration
```

### Identities

```text
analysis procedure identity   dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                              UNCHANGED

execution identity            03b98b8ee4265e27a139979092b63eb8f60f3727cce97c6a9bbc25c13bd24354
                           -> 4d2e74d2567c554b09337ff5f7ea891c4713df6044013efdbc70cdf9b3d1f353
                              MOVED, expectedly, and NOT FROZEN
```

Both were recomputed **twice, from two independent clean `git archive`
extractions** of the work commit, and the two extractions agree in every field.
The analysis identity cannot move: it hashes `SCIENTIFIC_MODULES`, and this stage
edited none of them. The execution identity hashes `VALIDATION_MODULES` plus the
canonical driver; four of those changed, so it moves. The seal stays `PRE_DRIVER`
with `expected_execution_identity = None`, so nothing is contradicted.

### Changed files

```text
e1a_v4/validation/classification.py     record_consistency_failure, the whole-
                                        record rule, and BLOCK_DECISION_FIELDS
e1a_v4/validation/campaign_driver.py    require_consistent_record, the single
                                        raise site, wired into the validator and
                                        both aggregators
e1a_v4/validation/refusals.py           TerminalRecordInconsistent
e1a_v4/validation/release_authority.py  whole-record preflight probes; the driver
                                        surface gains require_consistent_record
test_e1a_v4_driver_endpoints.py         the whole-record regression group
test_e1a_v4_release_authority.py        preflight-detection regressions
```

---

## Test results

```text
suite                                      checks   failures   delta
test_e1a_v4_release_authority.py             1219          0      +6
test_e1a_v4_terminal_calibration.py           538          0       0
test_e1a_v4_driver_endpoints.py               391          0     +31
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
TOTAL                                        3412          0     +37
                                   (3375 before this stage)
```

Every previously green suite stayed green and none was weakened. The three suites
that install a sandbox stand-in driver -- `plan_coherence`, `generating_model` and
`coherence_hardening` -- needed no edit, because each generates its stub from
`REFUSAL_AWARE_DRIVER_SURFACE` itself.

Preflight cost is unchanged within noise: `bind_execution` 3.53s against the 3.47s
F1f-e baseline, and the conformance check 0.56s against 0.60s. The whole-record
probes are dictionary work only.

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
executed; it is still trajectory-bearing. It was inspected statically only: every
name it imports from `e1a_v4` still resolves. **No runtime status is claimed for
that suite.**

---

## Limitations

Record integrity is now closed for the defect classes found. This is not execution
readiness. Still open:

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
WHOLE-RECORD CONSISTENCY HARDENING COMMITTED
```
