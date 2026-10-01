# E1a v4 — C2 DERIVED-AUTHORITY BINDING REPAIR

**Stage.** `D6a3 — C2 DERIVED-AUTHORITY BINDING REPAIR`, implementing the
independently cleared D6a reconstruction
(`docs/e1a/E1A_V4_C2_POOLING_AUTHORITY_RECONSTRUCTION.md`, report commit `91b21fa`).

**Nothing was executed.** No RNG object constructed for scientific purposes, no random
number drawn, no trajectory generated, no calibration sampled, no campaign job run, no
official result observed.

| | |
|---|---|
| Work commit | `b075fac7d8ce215d427fd3c54bbeaaad30b47c36` |
| Work tree | `50b3fefa8612cda50eb4cac93fef115f934c8065` |
| Parent | `91b21faac7087d345141e96c801478fed5a14bf0` |
| Plan version | `1.14.0` — **unchanged** |
| Branch | `gaussian/stage-a-environment` (nothing pushed) |

---

## 1. Scientific disposition

```text
C2 ELEMENTARY EVENT            = P1 REJECTION FOR ONE DECLARED FIELD
C2 FIELD SCOPE                 = PER FIELD
C2 RELEASE ASSESSMENT          = FOUR SEPARATE R = 400 REJECTION-COUNT PROCESSES
POOLING                        = FORBIDDEN
WITHIN-REPLICATE FIELD REDUCTION = NONE
FINAL COMBINATION              = ALL REQUIRED FIELD-LEVEL CONDITIONS
```

This was resolved by the D6a reconstruction and independently cleared. **No new C2
scientific decision was introduced here.** This stage binds the already-derived rule.

"Four separate field-level rejection-count processes" is a **bookkeeping** statement. It
asserts no probabilistic independence between field outcomes, and the derivation needs
none.

---

## 2. Authority class: DERIVED, not EXACT

The case-release specification previously classified C2's no-pooling relationship as
`EXACT`. This repository defines

```text
EXACT    the frozen authority states this value literally
```

and no controlling document states "pooling forbidden" for C2. The binding's own reason
string was already derivation language. The relationship is now **`DERIVED`**, with the
reason recording what actually forces the rule:

1. contract `synthetic_validation_requirements[2]` requires the achieved joint gate size
   **at every declared geometry**, with `R = 400`;
2. prospective design §12 makes `gate_pass` a **per-field predicate** inside
   `AND over 4 fields`, so P1's elementary outcome is per field and its achieved size is
   a per-field quantity;
3. that section's budget allocates **`4 × alpha_geom = 0.02`** — four separate per-field
   P1 size events.

No other relationship was relabelled.

---

## 3. Provenance correction to the D6a1 reconstruction report

The earlier report is preserved unchanged as historical evidence. Three wording
corrections from the independent audit are recorded here instead.

**1. On where "never pooled" appears.** The D6a1 report said no controlling document
states the no-pooling rule. That is correct of the **contract and prospective design**,
but the **earlier validation plan** does contain explicit "PER FIELD, never pooled"
wording — it has since `8615405`, and the original package at `475633c` already read "at
EVERY declared field, R = 400 each". The plan is the MACHINE PLAN layer, **below** the
contract, so its wording cannot be the reason the rule derives from the contract. The
hierarchy is: higher design/contract do not literally say it but logically force it; the
lower plan does say it, as a restatement.

**2. On what a pooled rule would do.** The D6a1 report said the quantifier would
"constrain nothing" under pooling. That overstates it. A pooled assessment **would**
constrain an aggregate/average rejection rate. The actual defect is narrower and
sufficient: **it would not establish the contract-required size condition AT EVERY
declared geometry.** Pooled over 4 × 400, the contract's own coarse ceiling admits 36
rejections (CP upper ≈ 0.029605) while one declared geometry sits at 36/400 = 9.00%
(CP upper ≈ 0.117116). Those figures are provenance for the derivation and are **not**
release thresholds.

**3. On independence.** Four separate per-field assessments do not assume probabilistic
independence of field outcomes. The derivation uses none, and the canonical rule's
documentation says so explicitly.

---

## 4. Canonical rule

One object, `C2_RELEASE_RULE` in `e1a_v4/validation/release_authority.py`:

```text
case_id                = C2_geometry_false_rejection
elementary_event       = P1_REJECTION_ONE_DECLARED_FIELD
evaluation_scope       = PER_FIELD
required_fields        = the contract's declared roster, in declaration order
replicates_per_field   = 400
nominal_alpha          = 0.005        (alpha_geom)
boundary               = size_boundary(400, 0.005)   -- RECOMPUTED, never copied
field_reduction        = NONE
pooling                = FORBIDDEN
final_combination      = ALL_REQUIRED_FIELD_CONDITIONS
primary_endpoint       = P1_FALSE_REJECTION_RATE_PER_FIELD
authority_relationship = DERIVED
```

`require_c2_release_binding(contract, plan)` checks two things the surface registry
cannot: that the roster **is** the contract's own `fields` declaration in order — the
rule carries no private copy — and that the canonical object still says what D6a
derived, so a later edit to the object itself is caught rather than silently
re-generating a different plan. Six drift mutations of the canonical rule are tested and
all refuse.

The field roster is not duplicated: C2 and C3/C4 share the one declared-field roster, now
checked against the contract.

---

## 5. Former quarantine — final classifications

All nine `derived_boundaries.C2.*` leaves migrated from `DEFERRED_OUT_OF_SCOPE` to real
classifications:

| Leaf | Final classification |
|---|---|
| `rule` | `GENERATED_FROM_CANONICAL` |
| `per_field` | `GENERATED_FROM_CANONICAL` |
| `pooling` | `GENERATED_FROM_CANONICAL` |
| `replicate_reduction` | `GENERATED_FROM_CANONICAL` |
| `replicates` | `STRICTLY_VERIFIED_DUPLICATE` |
| `nominal_alpha` | `STRICTLY_VERIFIED_DUPLICATE` |
| `boundary` | `STRICTLY_VERIFIED_DUPLICATE` |
| `cp_lower_at_boundary` | `STRICTLY_VERIFIED_DUPLICATE` |
| `cp_lower_at_boundary_plus_1` | `STRICTLY_VERIFIED_DUPLICATE` |

```text
C2 DEFERRED / QUARANTINED SCIENTIFIC LEAVES = 0
```

No C2 leaf's validity now rests on "we froze whatever bytes happened to be there".

**Structural protection was not deleted.** The deferred mechanism is kept, empty, so a
future exception still cannot be created by the document that would benefit from it.
Preserved and re-verified: unknown-key refusal, nested-child refusal, missing-key
refusal, type-change refusal and list-membership totality.

---

## 6. The four prose defects

| Surface | Before | Now |
|---|---|---|
| `cases[C2].scientific_purpose` | free prose; contradiction ACCEPTED | `GENERATED` — `render_c2_scientific_purpose` |
| `cases[C2].formal_pass_fail_criterion` | free prose; contradiction ACCEPTED | `GENERATED` — `render_c2_criterion` |
| `assurance[C2].quantity` | free prose; contradiction ACCEPTED | `GENERATED` — `render_c2_assurance` |
| `assurance[C2].acceptance_rule` | free prose; contradiction ACCEPTED | `GENERATED` — `render_c2_assurance` |

Each was mutated into all five wrong shapes (pooled, ANY_FIELD, EVERY_FIELD,
reference-field-only, single pooled 1600). **20 mutations, 0 accepted.** The refusal is
structural — the candidate text differs from the generated canonical rendering — not a
keyword blacklist.

---

## 7. Complete C2 normative surface

| Container | Generated | Strictly verified |
|---|---:|---:|
| `cases[C2]` | 4 | 21 |
| `assurance[C2_geometry_false_rejection]` | 5 | 13 |
| `derived_boundaries.C2` | 4 | 5 |
| **total** | **13** | **39** |

```text
C2 normative locations          : 52
UNBOUND C2 RULE-BEARING LOCATIONS: 0
semantically free C2 locations   : 0
```

Whole-registry counts, machine-derived:

```json
{
  "normative_surface_locations": 196,
  "generated_normative_fields": 66,
  "strictly_verified_duplicate_fields": 130,
  "non_normative_explanatory_fields": 0,
  "controlled_containers": 10,
  "controlled_normative_lists": 10,
  "unexpected_list_elements": 0,
  "missing_list_elements": 0,
  "deferred_exception_paths_expected": 0,
  "deferred_exception_paths_observed": 0,
  "semantically_free_rule_bearing_locations": 0,
  "unclassified_normative_amendment_fields": 0
}
```

C2's final-campaign requirement line is now generated too: slot 2 moved from the pin
table to `render_c2_requirement`, so C2's contribution of **four required field-level
conditions** is bound rather than pinned. The conjunction happens at classification
level and is explicitly **not** a replicate-wide EVERY_FIELD event — a mutation to
"at least three required fields" and one to "the reference field" both refuse.

---

## 8. Mutation coverage

```text
coherent wrong C2 mutations tested : 51
unexpected passes                  :  0
```

| Group | Count | Accepted |
|---|---:|---:|
| four prose surfaces × five wrong shapes | 20 | 0 |
| five alternative interpretations (A accepted, B–E refuse) | 4 | 0 |
| other C2 normative surfaces (scope, reduction, pooling, roster, R, alpha, boundary, confidence rule, endpoint, final line, block-1 role) | 16 | 0 |
| canonical-rule drift mutations | 6 | 0 |
| no-self-validation rebuilds | 2 | n/a (expectations unchanged) |
| former-quarantine leaf rewrite | 3 | 0 |

### The five alternative interpretations

| | Interpretation | Result |
|---|---|---|
| A | PER_FIELD / no pooling | **ACCEPTED** (canonical) |
| B | ANY_FIELD replicate event | REFUSED |
| C | EVERY_FIELD replicate event | REFUSED |
| D | pooled 1600 field observations | REFUSED |
| E | reference-field-only | REFUSED |

### No self-validation

The suite mutates the candidate plan, rebuilds the registry **from the mutated plan**,
and asserts every expected value is unchanged. The candidate never defines its own
expected rule.

---

## 9. C2 numeric size rule — preserved

| Quantity | Value | How held |
|---|---|---|
| R per field | 400 | strictly verified |
| nominal alpha | `alpha_geom = 0.005` | strictly verified |
| confidence rule | one-sided 95% Clopper-Pearson **LOWER** inflation test | strictly verified |
| integer boundary | 5 (0–5 clean, 6+ detected) | **recomputed** via `size_boundary(400, 0.005)` |
| `cp_lower(5, 400)` | `0.004937934174346348` | recomputed, matches the audit |
| `cp_lower(6, 400)` | `0.006552145786997754` | recomputed, matches the audit |

Nothing was retuned. The 3% coarse contract ceiling keeps its existing semantics as a
mandatory reported diagnostic; the 36/1600 and 36/400 figures appear only as derivation
provenance and are not thresholds.

---

## 10. Scientific non-change

```text
NO NEW C2 SCIENTIFIC DECISION WAS INTRODUCED
```

Provable by hash: the plan JSON and Markdown are **byte-unchanged**.

| Artifact | SHA-256 | Status |
|---|---|---|
| plan JSON | `16b0384d0022bb34e5733e09d0d6a233ab245f066987604f0a721e286629067e` | unchanged |
| plan Markdown | `70f81dce52161bb17122d27f1c9211e9d7f724493a92cc4581df43d3e43c3d76` | unchanged |

Every generated C2 string reproduces the approved text exactly, so binding moved no
content. Superior authority is likewise byte-unchanged: physical foundation
`6d9aed24…`, theory baseline `0a01b356…`, design contract `91d6ae76…`, prospective
design `e59dcff6…`, seed map `95870d7d…`, seal `PRE_DRIVER`.

---

## 11. C3/C4 regression

```text
C3/C4 AUTHORITY: UNCHANGED
```

C3 and C4 remain `PER_FIELD`, reduction `NONE`, pooling `FORBIDDEN`, R = 400 at
`alpha_2 = 0.001` (clean 0–2) and R = 2000 at `alpha_1 = 0.004` (clean 0–13). C3's
primary release is the G5 block with full P1 a non-release secondary diagnostic; C4's
primary is the Block-1 achieved size. The G4 disposition still affects **C3, C4** only —
C2 is bound by its own rule, which is asserted directly.

All previously cleared C3/C4 mutation groups still pass: the 16-class escape set, the
nested semantic-leaf totality group, the explanatory-semantics group and the list and
deferred-scope group.

---

## 12. Tests

```text
suites      : 15 (all pure/static)
checks      : 2,843
failures    : 0
trajectories: 0
```

| Suite | Checks |
|---|---:|
| `test_e1a_v4_release_authority.py` | 993 |
| `test_e1a_v4_terminal_calibration.py` | 538 |
| `test_e1a_v4_coherence_hardening.py` | 138 |
| `test_e1a_v4_repair.py` | 126 |
| `test_e1a_v4_driver_endpoints.py` | 122 |
| `test_e1a_v4.py` | 122 |
| `test_e1a_v4_case_scope.py` | 114 |
| `test_e1a_v4_generating_model.py` | 113 |
| `test_e1a_v4_plan_coherence.py` | 113 |
| `test_e1a_v4_calibration_scope.py` | 105 |
| `test_e1a_v4_preexec.py` | 104 |
| `test_e1a_v4_size_semantics.py` | 79 |
| `test_e1a_v4_contract_plan.py` | 75 |
| `test_e1a_v4_dispositions.py` | 64 |
| `test_e1a_v4_preexec_corrections.py` | 37 |

No RNG object was constructed for scientific purposes, no calibration executed, no
campaign job run. `test_e1a_v4_campaign_driver.py` remains a **KNOWN DEFERRED TEST**:
not executed, no runtime status claimed.

### Tests whose meaning changed, deliberately

Four assertions written for the F1e-r9 quarantine stage asserted that C2 was *not*
scientifically cleared and that its leaves were `DEFERRED`. D6a3 is exactly the stage
that changes that, so they are replaced by assertions of the new reality: no leaf is
deferred, the nine C2 leaves are generated or strictly verified, the deferred registry
is empty, and C2 is bound by its own rule rather than by the C3/C4 amendment.

### A bug this repair introduced and fixed

Registering C2's derived-boundary leaves explicitly while the generic
`derived_boundaries.*` loop already covered them double-counted all nine, inflating the
leaf class counts to 59 against 50 declared. Caught by the existing "class counts account
for every declared leaf" assertion, which is what that check exists for. The duplicate
registration was removed; counts now reconcile exactly.

---

## 13. Changed files

| File | Purpose |
|---|---|
| `e1a_v4/validation/release_authority.py` | `C2ReleaseRule`, `C2_RELEASE_RULE`, `C2_DERIVATION_REASON`, six C2 renderers, `require_c2_release_binding`, `C2_CASE_PROSE_PINS`, `C2_CASE_LIST_PINS`; C2 registered across the surface registry and controlled containers; C2's requirement slot generated; `EXACT` → `DERIVED`; quarantine tables retired |
| `test_e1a_v4_release_authority.py` | new `test_c2_derived_authority_binding` group; quarantine-era assertions replaced |

No plan, contract, design, foundation, theory, seed-map, driver or classifier file was
modified. `F1f` was not started.

---

## 14. Runtime status

```text
F1f DRIVER/CLASSIFIER UPDATE = NOT STARTED
```

The campaign driver, C3/C4 endpoint aggregation, classifier and terminal aggregation
were not modified. The classifier's existing per-field C2 handling was read as evidence
only and left untouched.

---

## 15. Execution status

```text
OFFICIAL RESULTS            = NONE
OFFICIAL CAMPAIGN JOBS      = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
FINAL EXECUTION SEAL        = NOT FROZEN
EXECUTION AUTHORISED        = FALSE
CAMPAIGN                    = NOT RUN
```

### Identities

Computed twice from two independent clean `git archive` extractions of `b075fac`; both
passes agreed.

| Identity | Value |
|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **UNCHANGED** |
| unsealed execution identity | `76e3190a…` → `b49d659b94442a9a1796b7504047157481258dfcd4702e498175521d0d123232` |

The execution identity moved because the authority-binding code changed; no plan or
scientific file did. **It was not frozen.**

---

## 16. Limitations

* The pins in `C2_CASE_PROSE_PINS` and `C2_CASE_LIST_PINS` are tripwires over text owned
  by other dispositions (the frozen purpose, G3 seed grants, calibration scope). A later
  authorised amendment to one of those must update its pin deliberately.
* `derived_boundaries.C2.rule` is generated byte-identically to the approved text, which
  does not itself carry the words "PER FIELD" as C3's and C4's rows do. The per-field
  semantics are carried beside it by `per_field`, `pooling` and `replicate_reduction`,
  all now generated. Making the prose symmetric would be a plan content change and was
  deliberately not made under the minimum-change rule.
* Standing open items, unchanged: shared-drag gamma-sign authority, absolute drag and
  field construction (η, a), generator identity, PRNG authority, C6 inputs, remaining C8
  inputs, diagnostic aggregator authority.

---

## 17. Next stage

```text
D6a4 INDEPENDENT AUDIT OF C2 DERIVED-AUTHORITY BINDING
READY
```

Not started and not authorised. `F1f — DRIVER/CLASSIFIER IMPLEMENTATION UPDATE` remains
**NOT STARTED**.

---

```text
C2 DERIVED-AUTHORITY BINDING REPAIR COMMITTED
```
