# E1a v4 — C3/C4 authority consistency repair

Waterfall stage **F1e — PROSPECTIVE C3/C4 AUTHORITY AMENDMENT**, consistency
repair. The approved per-field science was not reconsidered and did not change.

| | |
|---|---|
| Work commit | `aa884e45b0c75673965ed221536432e084bc68c1` |
| Work tree | `1a57c2b32a2a5f4fa08c55faa59481940c736d66` |
| Parent | `f19a45a3e24e9eeca6df791e71729a562c027b39` |
| Amendment record | `docs/e1a/E1A_V4_C3_C4_PER_FIELD_AMENDMENT.md` |

---

## Auditor blockers

All three reproduced against the unmodified package **before** any edit. In each
the structured fields were left saying the approved rule, only the normative
English was changed, and the Markdown was regenerated from the mutated JSON so
the two renderings agreed with each other.

| # | mutation | preflight before | preflight after |
|---|---|---|---|
| A | G4 resolution → ANY-FIELD reduction and pooling | **ACCEPTS** | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| B | C3 formal criterion → ANY-FIELD replicate event | **ACCEPTS** | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| C | C4 formal criterion → pooled four-field event | **ACCEPTS** | `PROSPECTIVE_AMENDMENT_MISMATCH` |

**Root cause.** One decision was described four times by hand — the G4
resolution, the two formal pass/fail criteria, and the per-case semantics prose —
while only the *structured* fields were bound to anything. Markdown/JSON coherence
cannot detect this by construction: it proves the two renderings agree, and here
they agreed perfectly while both contradicted the approved amendment.

---

## Canonical rule object

`FIELD_SIZE_RULES` in `e1a_v4/validation/release_authority.py` — the
case-release-specification layer that already sits **above** the machine plan in
the authority chain, so the expected semantics are never read from the text under
test.

```text
FIELD_SIZE_DISPOSITION_ID       G4
FIELD_SIZE_DISPOSITION_TYPE     C3_C4_PER_FIELD_SIZE
FIELD_SIZE_DISPOSITION_STATUS   CLOSED PROSPECTIVELY
FIELD_SIZE_DISPOSITION_AFFECTS  C3, C4
EVALUATION_SCOPE_PER_FIELD      PER_FIELD
FIELD_REDUCTION_NONE            NONE
POOLING_FORBIDDEN               FORBIDDEN
FINAL_RELEASE_REPRESENTATION    FIELD_CONDITION_VECTOR
FINAL_RELEASE_COMPENSATION      FORBIDDEN
FIELD_SIZE_REQUIRED_FIELDS      theta0_circular, theta1_power,
                                theta2_ellipse, theta3_temperature

FieldSizeRule(C3_g5_block)        scope PER_FIELD, reduction NONE, pooling FORBIDDEN,
                                  endpoint G5_BLOCK_SIZE, R 400, alpha_2 0.001,
                                  boundary 2, decision G5,
                                  secondary SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC,
                                  secondary_feeds_primary_release False
FieldSizeRule(C4_surrogate_validity)  scope PER_FIELD, reduction NONE, pooling FORBIDDEN,
                                  endpoint BLOCK1_ACHIEVED_SIZE, R 2000, alpha_1 0.004,
                                  boundary 13, decision Block-1
```

The field order, membership and multiplicity are load-bearing, and the exact
operating-characteristic decimals are carried on the rule so they cannot drift
between renderings.

Architecture **A** of the two offered: every normative rendering is
**deterministically generated** from this object and compared byte-exactly. No
unconstrained English is treated as scientific authority.

```text
canonical rule object (code, above the plan)
        -> G4 gap statement and resolution
        -> C3 / C4 formal pass/fail criteria
        -> per-case semantics blocks
        -> assurance rows
        -> section-12a boundary prose
        -> final-classification requirement lines
        -> Markdown, regenerated from the JSON as before
```

---

## G4 binding

Status alone is explicitly **not** sufficient. `require_field_size_amendment`
checks, against the canonical object:

- the `G4` disposition exists at all;
- `status == "CLOSED PROSPECTIVELY"`;
- `affects == "C3, C4"`;
- `gap` equals `render_field_size_gap_statement()` exactly;
- `resolution` equals `render_field_size_disposition()` exactly.

A disposition reading `status = CLOSED PROSPECTIVELY` with an ANY_FIELD + pooling
resolution therefore refuses, because the resolution text must **be** the
generated canonical text. The earlier binding — any release rule citing
`authority_gaps.G4` requires that disposition to exist and be closed — is
retained, so deleting or reopening it still refuses as well.

---

## C3 normative binding

The C3 formal criterion is **generated**, not kept: the plan must carry exactly
`render_field_size_criterion(rule_C3)`. It cannot independently encode ANY_FIELD,
EVERY_FIELD, reference-only or pooling, because any such text is simply not equal
to the generated string. Also generated and compared: `c3_semantics`
`field_structure`, `field_reduction`, `pooling`, `field_structure_rule`,
`case_level_rule`, `what_is_forbidden`, `release_criterion`,
`primary_release_endpoint`, `field_structure_status` and `block1_role`; the
assurance row's `quantity`, `unit`, `pooling` and `acceptance_rule`; the
section-12a boundary prose; and final-classification requirement 3. Strictly
compared in addition: `fields_affected`, `primary_release_endpoint`,
`joint_p1_result_changes_C3_release_verdict`, and the derived-boundary
`per_field`, `replicate_reduction`, `replicates`, `nominal_alpha` and `boundary`.

## C4 normative binding

Identical treatment with `rule_C4`: generated criterion, generated `c4_semantics`,
generated assurance row, generated boundary prose, generated requirement 4, and
the same strict comparisons. Any normative C4 text defining a pooled four-field
event, an ANY_FIELD replicate event or a reference-field-only event contradicts
the canonical rule and refuses.

---

## Normative representation inventory

Every string in the plan pair that mentions field structure was enumerated and
classified. The Markdown is excluded from separate classification because every
one of its normative regions is a byte-exact re-render of the JSON, already
enforced.

| classification | members |
|---|---|
| **CANONICAL SOURCE** | `FIELD_SIZE_RULES` and the module-level constants in `release_authority.py` — the only place the rule is stated |
| **GENERATED RENDERING** | `authority_gaps.G4.gap`, `authority_gaps.G4.resolution`; both `cases[].formal_pass_fail_criterion`; both semantics blocks' generated members; both `assurance[].quantity`/`unit`/`pooling`/`acceptance_rule`; both `derived_boundaries.*.rule`; `final_campaign_classification.requirements[2]` and `[3]` |
| **STRICTLY VERIFIED DUPLICATE** | `cases[].fields_affected`, `cases[].primary_release_endpoint`, `c3_semantics.joint_p1_result_changes_C3_release_verdict`, `derived_boundaries.*.per_field`/`replicate_reduction`/`replicates`/`nominal_alpha`/`boundary`, `final_campaign_classification.no_compensation_between_cases`/`no_weighted_score`, `G4.status`/`affects` |
| **NON-NORMATIVE EXPLANATION** | the C2/C5/C6/C7 occurrences of "per field"/"per cell" (other cases, unrelated to this amendment); `plan_authority_coherence`, `author_dispositions`, `output_schema.aggregate_fields`, `release_authority.mandatory_diagnostics[].required_keys` (schema vocabulary, not the C3/C4 rule); and the scientific-record documents `E1A_V4_C3_C4_PER_FIELD_AMENDMENT.md` and its report, which are records of the decision, not authority above the plan |

Machine-derived totality counts:

```text
canonical rule fields                        45
generated normative fields                   25
strictly verified duplicate fields           29
checked total                                54
unclassified normative amendment fields       0
```

There is no unguarded duplicated normative rule.

---

## Semantic mutation audit

Every mutation is coherent — the Markdown is regenerated from the mutated JSON —
and each one asserts its target component, the exact normative path edited, and
that the edit actually landed. No whole-document first-match replacement is used:
every swap is applied to one addressed JSON value.

| group | mutations | unexpected passes |
|---|---|---|
| G4 resolution: scope, reduction, pooling, compensation, C3 secondary role, dependence wording, ≥ 0.90 scope | 7 | 0 |
| C3 and C4 formal criteria: → ANY_FIELD, → REFERENCE_ONLY, → EVERY_FIELD, → pooled, → compensating case level | 10 | 0 |
| per-case semantics: `field_structure`, `field_reduction`, `pooling`, `field_structure_rule`, `case_level_rule`, `what_is_forbidden` | 12 | 0 |
| assurance rows and derived boundaries: `unit`, `pooling`, `replicate_reduction` | 6 | 0 |
| newly guarded prose: `acceptance_rule`, `quantity`, boundary rule, `release_criterion`, G4 gap statement | 9 | 0 |
| C3 secondary diagnostic → release-bearing | 1 | 0 |
| final release requirements → reference-field / partial pass | 2 | 0 |
| **semantic mutation audit subtotal** | **47** | **0** |
| required field list: remove, duplicate, replace, extra, reorder, on both cases | 10 | 0 |
| earlier structured-field group (unit, pooling, field lists, G4 presence/status) | 13 | 0 |
| **total coherent-but-wrong mutations** | **70** | **0** |

The critical property is demonstrated directly: **Markdown and JSON agree with
each other, both contradict the approved amendment, and preflight refuses.** The
new layer is therefore not representation coherence.

---

## Scientific authority

```text
NO C3/C4 SCIENTIFIC DECISION CHANGED
```

Unchanged and asserted: C3 `R = 400` per field at `alpha_2 = 0.001` with boundary
2; C4 `R = 2000` per field at `alpha_1 = 0.004` with boundary 13; the
Clopper-Pearson rule, level and bound direction; the four declared fields; C3's
primary G5 endpoint with the full P1 result remaining
`SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` and
`joint_p1_result_changes_C3_release_verdict = false`; the ≥ 0.90 target as
**C1-only**; and the dependence wording, which still says only that independence
must not be assumed and that the direction and magnitude are not established —
the unsupported positive-association claim is absent and a mutation introducing it
refuses.

The amendment remains **plan-level prospective authority**. The design and
contract were not rewritten as though they had always contained this rule.

| item | value |
|---|---|
| unsealed execution identity (before) | `2d1ae73233f7dc972ddcab000010d4fac703d29b2eb55408c48c8812982b473c` → after the amendment `948709654add8fa950c4eeb8fb2c729fc661b7625a1c6e4ae4cd5f24bc9c2eec` |
| **unsealed execution identity (now)** | **`43e493ff5c502ae52a81fc15e94486da640d59535c104ae3e5594dc888fe4c70`** |
| JSON plan | `dc2442dd34dca69330575e2ad9a8c647f72ad47a4ba6bb77311d6933bb0d6f0c` |
| Markdown plan | `28ad45fb00598a7857ca78bbe9878d57fd3fd614d9cff8e379b0d796e2d89304` |
| **analysis identity** | **unchanged** `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` |
| design contract | **byte-unchanged** `91d6ae76…431b` |
| prospective design | **byte-unchanged** `e59dcff6…a495` |
| seed map | **byte-unchanged** `95870d7d…e91ce` |
| execution seal | **byte-unchanged**, `PRE_DRIVER` |
| plan version | `1.11.0` (unchanged: the rule did not change, only how it is stated and checked) |
| campaign structure | 53,200 jobs / 46,000 calibration artifacts |

Computed twice from independent clean `git archive` extractions of the work
commit; both agree. The execution identity moves because the plan and
`release_authority.py` are both in its preimage. No analysis-bound scientific
module was modified, so the analysis identity does not move — verified, not
assumed.

One new refusal code, `PROSPECTIVE_AMENDMENT_MISMATCH`: "a normative rendering
contradicts the canonical rule" is a different failure from a release-binding
mismatch and is worth naming.

---

## Implementation status

```text
F1f DRIVER/CLASSIFIER UPDATE = NOT STARTED
```

`campaign_driver.py` and `classification.py` are untouched. The driver still
raises `ENDPOINT_EVENT_REDUCTION_UNDECLARED` for both C3 and C4, asserted
behaviourally after the repair rather than by a text search. That refusal was not
weakened and remains authority-correct.

### Tests

All pure. Each suite run with `ou_observations` replaced by a counter that aborts
on first call, so the trajectory count is measured.

| suite | checks | passed | failed | trajectories |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 538 | 538 | 0 | 0 |
| `test_e1a_v4_release_authority.py` | 415 | 415 | 0 | 0 |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | 0 |
| `test_e1a_v4_repair.py` | 126 | 126 | 0 | 0 |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | 0 |
| `test_e1a_v4.py` | 122 | 122 | 0 | 0 |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | 0 |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | 0 |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | 0 |
| **total** | **1,783** | **1,783** | **0** | **0** |

The release-authority suite grows from 273 checks in 15 groups to 415 in 16.
`test_e1a_v4_campaign_driver.py` was **not run** — trajectory-bearing; its runtime
status is not claimed.

One pre-existing probe expectation was widened rather than removed: probe C
(C3 `R = 400 → 401`) now refuses at the amendment layer first, because the
generated criterion carries `R = 400`. Both refusals are correct and the test
accepts either, naming why.

---

## Execution status

```text
OFFICIAL RESULTS = NONE

FINAL EXECUTION SEAL = NOT FROZEN

EXECUTION AUTHORISED = FALSE

CAMPAIGN = NOT RUN
```

Verified after the repair: no `results/e1a_v4_validation` directory; seal
`state = PRE_DRIVER`, `expected_execution_identity = None`,
`execution_authorised = false`, `random_draws = 0`, `trajectories = 0`. No RNG
object was constructed and no calibration or campaign job ran. Nothing was pushed.

---

## Next stage

```text
F1e-r2 INDEPENDENT RE-AUDIT
READY
```

---

C3/C4 AUTHORITY CONSISTENCY REPAIR COMMITTED
