# E1a v4 — C2/C3/C4 per-field driver and classifier implementation (F1f)

Scientific-record entry for the runtime implementation stage that makes the driver
and the release classifier express the already-cleared per-field authority for
**C2**, **C3** and **C4**.

```text
STAGE              F1f  DRIVER / CLASSIFIER IMPLEMENTATION UPDATE
STARTING COMMIT    ff8493bf63e52e932c7a0f5e00f82abd64611da9
AUTHORITY CHANGED  NONE
```

This stage introduced **no new scientific decision**. Every rule it implements was
settled earlier: C3/C4 by the G4 per-field amendment (`c086cd2`, recorded at plan
version 1.11.0) and C2 by the derived-authority binding (`b075fac`, D6a3). The
frozen validation plan and its normative Markdown are **byte-unchanged** by F1f.

---

## 1. Starting implementation discrepancy

The driver was inspected at `ff8493b` before any edit. Three of the four things
the stage brief listed as *possible* defects were **already repaired**, and are
not re-done here.

### 1.1 Already repaired — C2 per-field P1 recording

`evaluate_replicate` builds a `per_field` block with one row per declared field.
Each row carries that field's **own** decision from that field's own
`p1_geometry` call:

```python
row.update({"P1": bool(result.passed),
            "p1_rejected": bool(not result.passed),
            "block1_rejected": block1, "g5_rejected": g5})
per_field[field_id] = row
```

`execute_replicate` then merges `replicate["per_field"][field_id]` into **that
field's record only**, and `field_event_count` refuses by name if asked to count
anything listed in `REPLICATE_LEVEL_EVENTS`. The replicate-wide `p1_rejected` that
was once stamped onto all four records no longer exists as a key.

Repaired in `77c6758855c7fc941afef57668b29367947ce25d` ("Repair E1a v4 driver
scientific endpoint mapping", 2026-09-29). Permanent regression:
`test_c2_counts_per_field` in `test_e1a_v4_driver_endpoints.py`, which asserts
`[P, R, P, P] -> [0, 1, 0, 0]` and that the endpoint assembly publishes no
replicate-wide `p1_rejected`.

### 1.2 Already repaired — C3 actual G5 and C4 actual Block-1 recording

`p1_block_decisions` reads the frozen P1 result's per-gate p-values and the
artifact's own stored critical value; it recomputes no statistic and no threshold:

```python
p_min = min(rows[gate] for gate in _BLOCK1_GATES)
block1_rejected = bool(p_min < artifact.critical_p_min())
g5_rejected = bool(rows["G5"] < binding.binding.alpha_2)
```

`(None, None)` is returned only when the gate produced no rows at all, which is
exactly the structured-refusal case, and `require_endpoint_events` refuses a null
decision on an `ESTIMATED` record rather than scoring it zero. Same repair commit.
Permanent regression: `test_g5_and_block1_propagate`.

### 1.3 The real remaining gap — C3/C4 could not be COUNTED at all

`replicate_level_rejections` refused for any case declaring more than one field:

```python
raise EndpointEventReductionUndeclared(
    f"{case_id}: {UNDECLARED_EVENT_REDUCTION} It declares {len(fields)} fields "
    f"and scores {event!r} over {declared} replicates.")
```

C3 and C4 each declare four fields, so `campaign_counts_from_records` could not
produce their counts: a complete campaign would have refused at aggregation. That
refusal was correct when written — frozen authority then stated no field structure
for C3 or C4 — and it is the refusal F1f replaces.

### 1.4 The refusal's stated justification had gone stale

`UNDECLARED_EVENT_REDUCTION` asserted that the case "is scored over replicates
(assurance unit 'campaign')" and that `derived_boundaries` "marks C2
`per_field: true` and says nothing of the kind for C3 or C4". Both statements were
false against the amended plan read at `ff8493b`:

| | C2 | C3 | C4 |
|---|---|---|---|
| `assurance[...].unit` | `per_field` | `per_field` | `per_field` |
| `derived_boundaries.*.per_field` | `true` | `true` | `true` |
| `derived_boundaries.*.pooling` | `FORBIDDEN - …` | `FORBIDDEN - …` | `FORBIDDEN - …` |
| `derived_boundaries.*.replicate_reduction` | `NONE` | `NONE` | `NONE` |

### 1.5 The classifier input carried a scalar for C3 and C4

```python
c3_rejections: int                             # of 400
c4_rejections: int                             # of 2000
```

and the classifier produced `"STATISTICAL_SIZE_FAILURE (C3 G5 block)"` with **no
field identity**. C2 was already per field. A scalar cannot express the declared
result: it cannot say which field inflated, and the quantity it would hold —
replicates in which *some* field rejected — is a different statistical object with
a different null rate.

### 1.6 The field roster was bound for C2 only

`bind_execution` compared `cases["C2_geometry_false_rejection"]["fields_affected"]`
against the canonical roster. Nothing compared C3's or C4's, although both are now
release-bearing per-field lists.

---

## 2. C2 implementation

Unchanged in substance, and now routed through the same shared counter as C3 and
C4 rather than its own inline comprehension:

```python
c2 = per_field_rejections(plan, records, "C2_geometry_false_rejection",
                          "p1_rejected")
```

Each declared field's `p1_rejected` is counted over that field's own R = 400
replicates. The recorded C2 event for field θ depends only on that field's own P1
decision for that replicate, because that is the only value in that field's
record.

Routing C2 through the shared helper also closed a latent hole: the old inline
code took `release_subconditions(plan, c2_case)[0]` without checking that there
was exactly one release subcondition, so a plan that stopped marking
`feeds_primary_claim` would have silently counted one cell of four. The shared
counter refuses that.

## 3. C3 implementation

```python
c3 = per_field_rejections(plan, records, "C3_g5_block", "g5_rejected")
```

The counted event is the **actual G5 / Block-2 decision**, per field, per
replicate — `g5_rejected`, which `p1_block_decisions` derived from the frozen
gate's own `p(G5)` against the contract's own `alpha_2`. The combined P1 scalar is
never the C3 primary event.

R = 400 per field, nominal `alpha_2 = 0.001`, clean 0–2, inflation 3+. The
boundary is not written in the counting layer: `classify_size` derives it with
`size_boundary(400, 0.001)`, and preflight refuses if the recomputed value differs
from the frozen `derived_boundaries.C3.boundary`.

## 4. C3 secondary diagnostic

The full P1 result remains **observable and non-release-bearing**.

*Observable*: every C3 field record still carries `P1` and `p1_rejected` beside
`g5_rejected`. `required_endpoint_events` still requires all of them for any case
declaring `uses_p1_block1`, so the diagnostic cannot be dropped.

*Non-release-bearing*: it is not the event `per_field_rejections` counts for C3,
so it cannot enter the C3 rejection count or the failures list. The classifier
states this in its result rather than leaving it to be inferred:

```python
"C3": {"primary_endpoint": "G5_BLOCK_SIZE",
       "secondary_diagnostic": {
           "label": "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC",
           "quantity": "the full two-block P1 result, recorded per field",
           "release_bearing": False, ...}}
```

and preflight refuses an implementation that reports `release_bearing` as anything
but `False`. No new release semantics were invented for it: it fails nothing on
its own, exactly as `joint_p1_result_changes_C3_release_verdict: false` declares.

## 5. C4 implementation

```python
c4 = per_field_rejections(plan, records, "C4_surrogate_validity",
                          "block1_rejected")
```

The counted event is the **actual Block-1 decision**, per field, per replicate,
and it is never derived retrospectively from a combined P1 scalar: the real
decision exists in the record because `p1_block_decisions` put it there.

R = 2000 per field, nominal `alpha_1 = 0.004`, clean 0–13, inflation 14+, boundary
recomputed.

## 6. Data model

| | before F1f | after F1f |
|---|---|---|
| C2 | `c2_rejections_by_field: Mapping[str, int]` | unchanged |
| C3 | `c3_rejections: int` | `c3_rejections_by_field: Mapping[str, int]` |
| C4 | `c4_rejections: int` | `c4_rejections_by_field: Mapping[str, int]` |

**No backward-compatible scalar was retained.** An unused convenience field
carrying "replicates in which some field rejected" would be exactly the ambiguity
the amendment removed, and there is no non-scientific reason to keep one: no
official result data exists at any schema version.

The four canonical field IDs are **not re-typed**. One roster is declared once —
`REQUIRED_SIZE_FIELDS` in `classification.py`, formerly `REQUIRED_C2_FIELDS` — and
the driver derives its roster from the frozen plan's own `fields_affected`.
`bind_execution` now checks that roster for **all three** per-field size cases and
refuses a missing, duplicated, extra, unknown or reference-field-only set.

### Schema version

`CAMPAIGN_RESULT_SCHEMA` moves `e1a_v4_campaign_result/1` → `/2`, because the
embedded classification's C3 and C4 shape changed meaning. A version-1 result is
**not convertible**: `c3_rejections = N` cannot be resolved into four field
counts, and reinterpreting it as "N replicates in which some field rejected" would
assert a different statistic. Nothing is migrated, because nothing exists —
`results/e1a_v4_validation` does not exist at any point in this stage.

The per-record and per-job schemas are **unchanged**. They were already per field:
a job record's coordinates carry `scope = field_id` and its result carries that
field's own decisions.

## 7. Classifier

C2, C3 and C4 are now the same shape, and each contributes **four** field
conditions to the existing conjunction:

```python
for case, endpoint in (("C2", "P1 geometry"), ("C3", "G5 block"),
                       ("C4", "Block-1 surrogate")):
    replicates, nominal = PER_FIELD_SIZE_CASES[case]
    detail[case] = {}
    for fid in sorted(per_field[case]):
        res = classify_size(per_field[case][fid], replicates, nominal)
        detail[case][fid] = res
        if res["verdict"] == SIZE_FAILURE:
            failures.append(
                f"STATISTICAL_SIZE_FAILURE ({case} {endpoint}, field {fid})")
```

Each failing field contributes an **independently identifiable** failure carrying
both the case and the endpoint and the field — for example
`STATISTICAL_SIZE_FAILURE (C3 G5 block, field theta1_power)`. The global verdict
remains `PASS iff the failures list is empty`; it is a scalar because it derives
from the complete failure list, not because the evidence was collapsed.

Four field conditions entering a conjunction is an **intersection–union test**,
not a replicate-level reduction — the same shape C7 already uses per alternative.

### No multiplicity correction

Each field is scored at its own **unadjusted** nominal alpha against the boundary
derived from that alpha. No Bonferroni, no familywise correction, no pooled
threshold, no adjusted C3/C4 alpha. The family-level false-validation
characteristics remain operating characteristics, not thresholds.

### ≥ 0.90 remains C1-only

No `0.90` target is attached to C2, C3 or C4 in the detail rows or in the endpoint
semantics. `0.90` is C1's target and C8's.

---

## 8. No-reduction proof

The obsolete refusal was **replaced, not deleted**, and in two independent places.

### 8.1 The driver-level structural ban

`replicate_level_rejections` is kept and now refuses unconditionally, with a
stronger reason. It used to say authority was *silent*; it now says authority has
*spoken*:

```python
raise CrossFieldReductionForbidden(
    f"{case_id}: {FORBIDDEN_EVENT_REDUCTION} It declares {len(fields)} fields "
    f"and {declared} replicates per field for {event!r}.")
```

A new refusal code `CROSS_FIELD_REDUCTION_FORBIDDEN` was added rather than reusing
`ENDPOINT_EVENT_REDUCTION_UNDECLARED`, because a code reading "undeclared" where
authority has declared would misreport the condition. The older code remains in
use for the two places where authority genuinely is silent: a case with more than
one release subcondition, and a C6 that declared more than one field.

The **single-field case is refused too**. C6 declares one field and reaches
`field_event_count` directly, so permitting a "trivial" reduction would only leave
a path by which a case that later declared four fields could be reduced without
anyone re-reading the rule.

No `any(...)`, `all(...)` or cross-field `sum(...)` over field decisions exists
anywhere in the scientific counting path.

### 8.2 The preflight implementation-conformance check

`require_per_field_implementation_conformance` runs inside
`require_release_authority_conformance`, so **every** preflight asserts that the
runtime expresses the cleared authority. It checks three independent things:

```text
SHAPE       four field counts declared for each of C2, C3, C4, and no scalar
            case count that could carry a pooled or any-field total
PARAMETERS  the runtime R and alpha equal the frozen derived_boundaries values,
            and the boundary RECOMPUTED from them equals the frozen integer
BEHAVIOUR   two classifications, below
```

**Probe 1** pushes a *different* field one over its boundary in each of the three
cases simultaneously. Exactly three size failures must return, each naming its own
case and its own field, with the other nine field conditions clean.

**Probe 2** puts every field of every case at *exactly* its boundary. Under the
declared per-field rule that is clean. Under any pooled or any-field reduction of
the same counts it is not.

A pooled implementation cannot satisfy both probes. The exhaustive
field-by-field enumeration deliberately lives in the test suites rather than in
preflight: preflight runs on every bind, and a Clopper–Pearson bound is not cheap.

### 8.3 The arithmetic demonstration

C3's boundary is 2 per field.

```text
8 rejections spread 2 / 2 / 2 / 2   ->  every field clean   ->  VALIDATION_PASS
the SAME 8 in one field            ->  8 > 2               ->  SIZE FAILURE
```

A pooled rule could not tell these apart. That difference is the whole content of
`pooling: FORBIDDEN`, and it is asserted as a permanent test.

### 8.4 Mutations proved to refuse or to produce a demonstrably wrong count

| mutation | result |
|---|---|
| C2/C3/C4 scalar case count restored | `IMPLEMENTATION_AUTHORITY_LAG` |
| scalar kept *beside* the per-field map | `IMPLEMENTATION_AUTHORITY_LAG` |
| per-field counts dropped entirely | `IMPLEMENTATION_AUTHORITY_LAG` |
| runtime R or alpha drifted from frozen | `IMPLEMENTATION_AUTHORITY_LAG` |
| classifier reports `pooling = PERMITTED` | `IMPLEMENTATION_AUTHORITY_LAG` |
| classifier reports reduction `ANY_FIELD` | `IMPLEMENTATION_AUTHORITY_LAG` |
| classifier reports `field_scope = PER_REPLICATE` | `IMPLEMENTATION_AUTHORITY_LAG` |
| C3 secondary diagnostic made release-bearing | `IMPLEMENTATION_AUTHORITY_LAG` |
| any cross-field reduction requested | `CROSS_FIELD_REDUCTION_FORBIDDEN` |
| counting a replicate-level event per field | `RESULT_SCHEMA_INVALID` † |
| a field's record removed | `CAMPAIGN_INCOMPLETE` |
| an extra replicate record inserted | `CAMPAIGN_INCOMPLETE` |
| a record relabelled to an undeclared field | `CAMPAIGN_INCOMPLETE` |
| a decision nulled in storage | `ENDPOINT_EVENT_MISSING` |
| missing / extra / reference-only field map | `Refusal` at the classifier |
| C3 full P1 substituted for the G5 event | different, demonstrably wrong counts |
| C4 combined P1 substituted for Block-1 | different, demonstrably wrong counts |
| field identities permuted | the count moves with the label; result differs |

† a pre-existing guard in `field_event_count`, re-confirmed rather than added here.

### 8.5 Positive deterministic fixtures

Non-RNG replicate fixtures drive Block 1 and Block 2 **independently**, so the two
can be made to disagree on purpose:

```text
replicate: theta0 pass, theta1 FAIL, theta2 pass, theta3 pass
  -> theta1 += 1      and the other three stay 0
  -> NOT all four += 1, and NOT one pooled += 1
```

and for multiple failures `theta0 FAIL, theta1 pass, theta2 FAIL, theta3 pass`
increments exactly `theta0` and `theta2`. Repeated for C2, C3 and C4 against each
case's own endpoint decision type.

### 8.6 Block distinction

One replicate is constructed in which **Block 1 rejects for `theta1_power` while
Block 2 rejects for `theta3_temperature`**:

```text
C3 (G5 / Block-2)  counts  theta3_temperature,  not theta1_power
C4 (Block-1)       counts  theta1_power,        not theta3_temperature
```

Substituting the full P1 result for either primary endpoint changes the count, so
the two blocks are demonstrably distinguished rather than coincidentally equal.

## 9. Persistence and restart

Field identity and the actual endpoint decisions survive storage for a structural
reason: a terminal job record is **already per field**. Its coordinates carry
`scope = field_id`; its result carries that field's own decisions. There is no
case-level scalar in storage, so no restart path can reconstruct per-field events
from an ambiguous one.

A deterministic test round-trips the records through canonical JSON and recounts:
recovered counts equal fresh counts, scopes survive, decisions survive as booleans
rather than nulls, and a storage gap or a nulled decision **refuses** instead of
counting zero.

Schema consequence: only `CAMPAIGN_RESULT_SCHEMA` moves (`/1` → `/2`, §6). The
record and job-record schemas are untouched.

## 10. Authority regression

Nothing in the authority layer was weakened to accommodate the runtime.

```text
C2 authority class ................... DERIVED   (unchanged by F1f)
C2 pooling / reduction / scope ....... FORBIDDEN / NONE / PER_FIELD
C3, C4 scope / reduction / pooling ... PER_FIELD / NONE / FORBIDDEN
G4 disposition still affects ......... C3, C4
C3 secondary diagnostic .............. still non-release-bearing
```

`NormativeSurface` totality, nested semantic-leaf totality, list totality, the
canonical renderings, unknown-key refusal and the no-self-validation checks are
all unchanged and all green. The frozen plan and its normative Markdown are
byte-identical to `ff8493b`:

```text
docs/e1a/e1a_v4_synthetic_validation_plan.json
  16b0384d0022bb34e5733e09d0d6a233ab245f066987604f0a721e286629067e
docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md
  70f81dce52161bb17122d27f1c9211e9d7f724493a92cc4581df43d3e43c3d76
```

### Tests whose meaning changed, deliberately

Four assertions written before F1f asserted that the driver was *still behind*
authority and still raised `ENDPOINT_EVENT_REDUCTION_UNDECLARED` for C3 and C4.
F1f is the stage that changes that, so they now assert the new reality: the
reduction is refused as **forbidden**, not as undeclared.

### A performance regression I introduced and fixed

The first version of the conformance check ran sixteen classifications per
preflight and cost **2.96 s** on its own — it would have doubled every preflight
in the repository. It was restructured to the two decisive probes described in
§8.2 and now costs **0.32 s**; `size_boundary` was additionally memoised, because
scoring three cases per field evaluates the same three derived boundaries twelve
times per classification. The memoised function returns the identical derived
integers (5, 2, 13), which the suites recompute independently.

```text
full preflight at ff8493b (baseline) .... 2.95 s
full preflight after F1f ................ 3.32 s
```

---

## 11. Tests

All fifteen pure/static suites, run at the work commit.

| suite | checks | failures |
|---|---:|---:|
| `test_e1a_v4_terminal_calibration.py` | 538 | 0 |
| `test_e1a_v4_release_authority.py` | 1024 | 0 |
| `test_e1a_v4_driver_endpoints.py` | 221 | 0 |
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
CHECKS ...................... 3022
FAILURES .................... 0
OFFICIAL RNG USE ............ 0
RNG OBJECTS CONSTRUCTED ..... 0
TRAJECTORY COUNT ............ 0
CAMPAIGN JOBS ............... 0
CALIBRATION EXECUTIONS ...... 0
```

F1f added **179** checks: +99 in `driver_endpoints`, +34 in `size_semantics`,
+31 in `release_authority` and +15 in `preexec_corrections`. New groups:

```text
F1f  cross-field reduction is FORBIDDEN
F1f  C2/C3/C4 counted PER FIELD
F1f  field misattribution is visible and refused
F1f  Block-1 and Block-2 are distinguished
F1f  counts survive serialisation/restart
F1f  the failing field reaches the classifier
F1f  per-field release semantics
F1f  runtime implementation conformance
```

### Deterministic unit fixtures versus official trajectories

Everything run here is a **deterministic unit fixture**: hand-written analyses,
arithmetic calibration fixtures and plain record dicts. `ou_observations` is never
called, no world state advances, and no RNG object is constructed. Where a fixture
needed a small denominator, the *declared replicate count* was reduced in a
deep-copied plan rather than the completeness guard being bypassed — writing 400
real replicates would have been a campaign.

### The deferred trajectory-bearing suite

`test_e1a_v4_campaign_driver.py` **remains deferred and was NOT run.** It was
inspected statically rather than executed:

```text
calls execute_campaign  : YES  -> execute_replicate -> ou_observations
calls run_campaign      : YES
TRAJECTORY-BEARING      : YES, through the production call chain
```

It is therefore still out of scope without explicit authorisation. A static AST
check confirms it remains **import-compatible** with this change: all 61 names it
imports from `campaign_driver` still exist, and it references neither
`c3_rejections` nor `c4_rejections`. No runtime status is claimed for it.

## 12. Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

No threshold, replicate count, nominal alpha, boundary, target, confidence rule,
bound direction or endpoint was changed. Every rule implemented here was settled
before this stage, and the frozen authority documents are byte-identical to the
starting commit. C1, C5, C6, C7, C8, P2, P3, P4, G1 and G2 semantics are
untouched; the only cases this stage reaches are C2, C3 and C4.

### Identities

Recomputed **twice** from independent clean `git archive` extractions of the work
commit; both agreed.

```text
analysis identity    dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                     UNCHANGED  -- no analysis-bound scientific module was modified

execution identity   b49d659b94442a9a1796b7504047157481258dfcd4702e498175521d0d123232
                  -> 5be9c4ea2ecf0cb9a8a87ed13577ee618e58a21577356d5cd2d9151b16cbb120
                     MOVED, as a runtime implementation change must. NOT FROZEN.

contract             91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
design               e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495
foundation           6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
theory baseline      0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa
plan json            16b0384d0022bb34e5733e09d0d6a233ab245f066987604f0a721e286629067e
plan markdown        70f81dce52161bb17122d27f1c9211e9d7f724493a92cc4581df43d3e43c3d76
seed map             95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce
                     ALL BYTE-UNCHANGED

plan version         1.14.0   (unchanged)
```

The execution identity moved because `campaign_driver.py` is bound into the
preimage by its own file hash and because `classification.py`, `plan.py`,
`refusals.py`, `release_authority.py` and `results.py` are VALIDATION_MODULES.
That is the intended behaviour: it is a PRE-DRIVER diagnostic, not a seal.

## 13. Execution status

```text
OFFICIAL RESULTS = NONE
OFFICIAL CAMPAIGN JOBS = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
FINAL EXECUTION SEAL = NOT FROZEN
EXECUTION AUTHORISED = FALSE
```

`results/e1a_v4_validation` does not exist. The execution seal is `PRE_DRIVER`
with `expected_execution_identity = None`, and the plan's `execution_authorised`
is `false`.

## 14. Remaining blockers

F1f closes the C2/C3/C4 runtime implementation gap and **nothing else**. The
following authority items remain open, and a successful F1f does not mean seal
ready, campaign ready or execution authorised.

```text
F2  Negative-stiffness / gamma-sign authority
F3  PRNG choice
F4  Field construction / absolute drag inputs
F5  Generator identity
F6  C6 implementation inputs
F7  Remaining C8 implementation inputs
F8  Diagnostic aggregator
```

Also open:

- `test_e1a_v4_campaign_driver.py`, the trajectory-bearing integration validation,
  remains **deferred** and unexecuted.
- `resolve_job_specification` still refuses for every job, naming the authority
  gaps F3–F5 supply.
- The per-case mandatory diagnostic aggregator is still not supplied (F8); the
  driver requires those diagnostics, which is its job, but does not compute them.

## 15. Next stage

```text
F1g INDEPENDENT IMPLEMENTATION AUDIT
READY
```

Not begun, and not authorised here.

---

C2/C3/C4 PER-FIELD DRIVER/CLASSIFIER IMPLEMENTATION COMMITTED
