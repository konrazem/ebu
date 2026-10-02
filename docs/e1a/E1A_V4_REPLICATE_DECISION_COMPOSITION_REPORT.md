# E1a v4 — replicate-level derived decision composition (F1f-k)

Bounded runtime-integrity repair closing the two C1/C7 composition defects and the
C1 aggregation parity gap the independent audit found after the endpoint-domain
repair. No scientific decision is made here.

```text
STARTING COORDINATE
  work commit    51d7f80804385573af6861e2359bf47f0a7e2e7b
  work tree      cf41a848f25449ea3ae01aa3acd40e529effc224
  report commit  3409eca1711da37b3c66ed38c8b4bd67b3efc686
  tree           clean
  branch         gaussian/stage-a-environment
```

```text
THIS STAGE
  work commit    1f5ae3821298282f8ea4ce3c030eb1a16025b736
  work tree      dce33b7a230274391cdb926de3838f87256cd3d3
```

The audit confirmed the endpoint-domain repair's four guarantees, and all four
still hold: partial P1 groups refuse, non-Boolean block/P1 decisions refuse,
contradictory P1-vs-block records refuse, and C7/C8 records that legitimately have
no P1 group remain valid.

**The defect class is one thing, seen twice more.** A producer writes the
components *and* a derived boolean; the consumer trusts the derived boolean
without checking it follows from them.

---

## Auditor C1 counterexample

Reproduced **before any edit** at `3409eca`, by pure deterministic calls.

```text
record   analysis_status = ESTIMATED
         block1_rejected = true,  g5_rejected = false
         P1 = false,              p1_rejected = true      (internally consistent)
         P2 = true, P3 = true, P4 = true
         complete_pass = true

BEFORE   whole-record rule   SOUND
         C1 validator        ACCEPTED
         C1 aggregation      ACCEPTED, C1 successes counted = 1
```

The replicate's own two-block gate rejected, and the campaign counted it as a
complete-pipeline **success**.

### The C1 parity gap

```text
record   the ENTIRE composite-P1 group absent, complete_pass = true

BEFORE   C1 validator        ENDPOINT_EVENT_MISSING
         C1 aggregation      ACCEPTED, C1 successes counted = 1
```

`campaign_counts_from_records` never called `require_endpoint_events`, so direct
aggregation counted a record validation had already refused.

---

## Canonical C1 composition

From `campaign_driver.evaluate_replicate`, verbatim:

```python
p1_values = [row["P1"] for row in per_field.values() if "P1" in row]
p1_all = all(p1_values) if p1_values else None
...
"complete_pass": (bool(p1_all and p2.passed and p3.passed and p4.passed)
                  if p1_all is not None else None)
```

```text
complete_pass = p1_all AND P2 AND P3 AND P4        when any P1 was recorded
complete_pass = None                               when none was
```

**`p1_all` is a CROSS-FIELD quantity.** It ranges over every field record of the
replicate, so a single record can establish only the *necessary* condition that
its own P1 passed. The repair splits the work accordingly, and the split is
deliberate rather than a gap:

```text
classify_record        per record: complete_pass TRUE requires P2, P3, P4 and
                       this record's own P1 all to have passed
replicate_outcomes     per replicate, holding ALL its field records: the EXACT
                       equality against complete_pass_from_components
```

A record claiming `complete_pass = False` while its own constituents all pass is
therefore **accepted by the validator and refused by the replicate-level view** —
another field's P1 may have failed, and only the replicate view can tell. That is
the division of labour, not a parity violation, and it is tested as such.

---

## Auditor C7 counterexamples

```text
record   P2 = true, P3 = true, false_acceptance = false

BEFORE   whole-record rule   SOUND
         C7 validator        ACCEPTED
         C7 aggregation      ACCEPTED, false acceptances counted = 0
```

```text
record   P2 = true, P3 = true, false_acceptance = "true"

BEFORE   whole-record rule   SOUND
         C7 validator        ACCEPTED
         C7 aggregation      ACCEPTED, false acceptances counted = 0
```

The second is the more dangerous shape: the counter tests `is True`, so a truthy
string is counted as **no false acceptance** — a silent miscount, not an error.

## Canonical C7 composition

From `evaluate_replicate`, verbatim: `"false_acceptance": bool(p2.passed and p3.passed)`.

| P2 | P3 | false_acceptance |
|---|---|---|
| False | False | **False** |
| True | False | **False** |
| False | True | **False** |
| True | True | **True** |

All four combinations are tested in both directions — the correct value is
accepted and counted, the opposite refuses — and the count is checked, not just
the verdict.

---

## Strict Boolean domains

```text
ACCEPTED   True, False            (identity, via is_strict_bool)
REFUSED    "true" "false" "0" "1"
           0  1
           0.0  1.0
           []  {}  any other object
```

Enforced on `false_acceptance`, `complete_pass` (when not None), `P2`, `P3`, `P4`
and `scale_recovered` (when not None), in addition to the block and P1 fields the
previous stage covered. `complete_pass` and `scale_recovered` are legitimately
`None` — the first when the replicate recorded no per-field P1 at all, the second
for every case but C8 — and `None` is never confused with `False`.

The three replicate-level counters no longer test `is True` on an unvalidated
value; each reads `endpoint_decision`, which returns the recorded boolean and
refuses anything else.

---

## Missing constituent behavior

```text
false_acceptance present, P2 or P3 absent   -> REFUSE
complete_pass present and not None,
    P2, P3 or P4 absent                     -> REFUSE
C1 record, composite-P1 group absent        -> ENDPOINT_EVENT_MISSING,
                                               in validation AND aggregation
```

`P2`, `P3` and `P4` are declared in `results.RESULT_FIELDS`, so a record carrying
a derived event without them is schema-incomplete. `false_acceptance` is required
for C7 and `complete_pass` for C1 by `required_endpoint_events`, read from the
frozen plan. Absence is never converted into `False`, `None` or "no event".

---

## Validation / aggregation parity

```text
classification.classify_record          THE invariant
    |
    +-- _classify_p1_group                 status and composite-P1 layer
    +-- _classify_replicate_decisions      C1 / C7 / C8 derived layer
    |
    +-- campaign_driver.require_consistent_record   single raise site
            +-- require_endpoint_events     endpoint VALIDATION
            +-- field_primary_outcome       C3 / C4 aggregation
            +-- field_event_count           C2 / C6 counting
            +-- replicate_outcomes          C1 / C5 / C7 / C8 counting
```

**`replicate_outcomes` now calls `require_endpoint_events` itself**, per record —
literally the same validator the official orchestration runs — rather than
assuming a call that `campaign_counts_from_records` never made. That closes the
parity gap by construction rather than by a parallel check.

Deterministic matrices, each record passed through a real JSON round trip:

```text
C1   10 shapes  valid success / valid failure / complete_pass TRUE against a
                failing P1, P2 or P4 / P1 group absent / complete_pass absent /
                non-Boolean complete_pass / non-Boolean constituent, plus the
                cross-field case where one field rejects
C7    9 shapes  valid acceptance / valid non-acceptance / contradictory value in
                both directions / string and integer substitutes / non-Boolean
                P2 / P2 or P3 absent
```

For every invalid shape both layers refuse; for every valid shape both accept and
the count matches the recorded event.

---

## Other derived-decision inventory

Every release-bearing replicate-level boolean on this terminal-record surface:

| field | case(s) | producer | bound before | bound now |
|---|---|---|---|---|
| `complete_pass` | C1 | `p1_all AND P2 AND P3 AND P4` | no | **yes** |
| `false_acceptance` | C7 | `P2 AND P3` | no | **yes** |
| `scale_recovered` | C8 | `all(p3_passed)` over the declared scale factors | no | **yes** |
| `P1` / `p1_rejected` | C1–C6 | `not (block1 OR g5)` | yes (F1f-i) | yes |
| `P2`, `P3`, `P4` | all | the frozen endpoints themselves | n/a — primitive | type-checked |

`scale_recovered` is the same class and was repaired with the same shared
mechanism: `evaluate_scale_control` records each factor's `p3_passed` inside
`scale_control.branches`, and the derived value must equal their conjunction. The
check applies only when those components are actually recorded, so **C8's
scientific behaviour is untouched** — its criterion, its factors and its recovery
rule are unchanged; an impossible record simply cannot be counted.

No DSL or inference engine was introduced. Each composition is a named helper
restating one already-frozen producer.

---

## C7 / C8 NO_P1_DECISION_GROUP

```text
PRESERVED
```

The frozen plan declares `uses_p1_block1 = false` for C7 and C8, so their records
legitimately carry no composite-P1 group. `record_state` still returns
`NO_P1_DECISION_GROUP` for them, validation accepts them, and `replicate_outcomes`
counts them. A record with no P1 group has `p1_all = None` and therefore
`complete_pass = None`, which is exactly what the producer writes.

---

## Prior-regression preservation

Re-run and green, unchanged:

```text
partial P1 decision group refuses
mixed None/bool block pair refuses
unknown and missing analysis status refuse
non-Boolean Block-1 and G5 refuse
contradictory P1 vs Block-1/G5 refuses
valid structured refusal accepted
C3/C4: single refusal -> NOT_EVALUABLE; all-refused terminal result produced;
       NOT_EVALUABLE cannot pass and is not size inflation; mixed
       NOT_EVALUABLE + STATISTICAL_SIZE_FAILURE both preserved
C2: per-field P1 counting, fail-closed refusal semantics, no pooling, and NO
    NOT_EVALUABLE pathway
```

## C2 / C3 / C4 scientific non-change

```text
SCIENTIFIC SEMANTICS UNCHANGED
```

No endpoint, threshold, alpha, boundary, denominator or verdict moves for any of
them. C1's complete-pass event, R and >= 0.90 target are unchanged; C7's
alternatives, R, target, P2/P3 criteria, confidence rule and no-pooling rule are
unchanged. Only the recorded derived value is now required to follow from the
components recorded beside it.

---

## Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

No authority file was touched; every authority hash is byte-identical:

```text
physical foundation    6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
theory baseline        0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa
prospective design     e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495
design contract        91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
validation plan JSON   dcf0c575a048ceebfcd3deb261d1a76ff269bfb16178a531b8911b5bdf8808ec
validation plan MD     5b76c3095ecbf5bc0f0273f2b83da8fab2d0c51154efc7628031b6445a4fbb18
refusal amendment      844d512f6ffe75a5...
plan version           1.15.0
```

Error classification reuses the existing vocabulary: composition contradictions
and domain violations are `TERMINAL_RECORD_INCONSISTENT`, a genuinely absent
required endpoint stays `ENDPOINT_EVENT_MISSING`. No new status was invented.

### Identities

```text
analysis procedure identity   dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                              UNCHANGED

execution identity            baf2ad9dbf1710275ac20c47faafea6ace6a8910bf34a90194a287b9c237006a
                           -> d854df3c37134ee8c6b19f9e6a367bbc4c1c46325541c7e0601ddf0e0b79be4a
                              MOVED, expectedly, and NOT FROZEN
```

Both were recomputed **twice, from two independent clean `git archive`
extractions** of the work commit, and the two agree in every field. The analysis
identity hashes `SCIENTIFIC_MODULES`, none of which this stage edited --
`endpoints.py` in particular is read, never modified, so the frozen analysis
procedure is untouched. The execution identity hashes `VALIDATION_MODULES` plus
the canonical driver, three of which changed. The seal stays `PRE_DRIVER` with
`expected_execution_identity = None`.

### Changed files

```text
e1a_v4/validation/classification.py     complete_pass_from_components,
                                        false_acceptance_from_components, and
                                        the replicate-decision layer of
                                        classify_record
e1a_v4/validation/campaign_driver.py    replicate_outcomes takes the plan, runs
                                        require_endpoint_events per record and
                                        checks the cross-field complete_pass
                                        equality; the three replicate counters
                                        consume endpoint_decision
e1a_v4/validation/release_authority.py  composition preflight probes
test_e1a_v4_driver_endpoints.py         the composition regression group and the
                                        C1/C7 parity matrices; result_row derives
                                        every decision from its components
test_e1a_v4_release_authority.py        preflight-detection regressions
test_e1a_v4_terminal_calibration.py     the C7 fixture given its constituents
```

---

## Tests

```text
suite                                      checks   failures   delta
test_e1a_v4_release_authority.py             1231          0      +6
test_e1a_v4_driver_endpoints.py               610          0     +61
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
TOTAL                                        3643          0     +67
                                   (3576 before this stage)
```

```text
SUITES RUN                 15
SUITES NOT CLEAN            0
FAILURES                    0
SCIENTIFIC RNG              0
REAL RNG OBJECTS            0
OU TRAJECTORIES             0
CALIBRATION EXECUTIONS      0
OFFICIAL CAMPAIGN JOBS      0
```

The hardened runner introduced in the previous stage is preserved and did its
job again: when `terminal_calibration` first failed on a corrected fixture, the
batch reported it as an unclean suite with the failing checks named, rather than
silently omitting it. That batch was discarded and the whole set re-run after the
fixture fix; the figures above are from one coherent clean run.

New regression groups:

```text
test_e1a_v4_driver_endpoints.py   "F1f-k replicate decision composition"
                                  the four-row C7 truth table with its COUNTS, the
                                  C1 composition over p1_all in {False, True, None},
                                  a 10-shape C1 and 9-shape C7 parity matrix with
                                  real JSON round trips, the cross-field case where
                                  one field rejects, the NO_P1_DECISION_GROUP
                                  preservation, and the C8 scale_recovered binding
test_e1a_v4_release_authority.py  preflight DETECTION: a C7 composition accepting
                                  on EITHER endpoint, a C1 composition ignoring P1,
                                  and a record rule binding nothing must each be
                                  refused
```

Preflight cost is unchanged within noise: `bind_execution` 3.58s against the 3.47s
F1f-e baseline, conformance 0.60s.

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

Record-composition integrity, not execution readiness. Still open:

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
F1f-l INDEPENDENT RE-AUDIT
READY
```

Not begun, and not authorised by this report. Nothing here authorises sealing.

---

```text
REPLICATE-LEVEL DECISION COMPOSITION HARDENING COMMITTED
```
