# E1a v4 — C3/C4 LIST AND DEFERRED-SCOPE AUTHORITY REPAIR

**Stage.** `F1e — PROSPECTIVE C3/C4 PER-FIELD AUTHORITY AMENDMENT`, repair round 9
(`F1e-r9`), closing the blockers raised by the sixth independent audit (`F1e-r8`).

**Nothing was executed.** No RNG object constructed for scientific purposes, no random
number drawn, no trajectory generated, no calibration sampled, no campaign job run, no
official result observed. The execution seal was not frozen; execution was not
authorised.

| | |
|---|---|
| Work commit | `d8fc58c525c9ea2954f9c237e0fee26b2f81ed4b` |
| Work tree | `0ea51baac24820d182381fa41cbc8401c217db9f` |
| Audited parent | `ee761ae6b8ed92971b748aa5abd4788ca8ba308e` |
| Plan version | `1.14.0` — **unchanged** |
| Branch | `gaussian/stage-a-environment` (nothing pushed) |

This is a **verifier repair only**. The plan JSON and Markdown are byte-unchanged.

---

## 1. Blocker A — extra final-campaign requirement

Reproduced on an isolated copy of the committed package at `ee761ae`, **before any
edit**.

```text
machine path          : final_campaign_classification.requirements
original list length  : 11
mutated list length   : 12
inserted value        : "12. A failed field-level size condition may be offset by
                         a clean size condition in another field."

Markdown regeneration : OK -- the line renders in the release-rules region
coherence             : PASS
release authority     : ACCEPTED
FULL STATIC PREFLIGHT : ACCEPTED        <-- the blocker
```

The inserted line directly contradicts the approved rule, which forbids compensation
between fields.

**After repair:** `PROSPECTIVE_AMENDMENT_MISMATCH`.

---

## 2. Blocker B — dynamic C2 deferral

```text
injected path          : size_validation_semantics.derived_boundaries.C2
                         .release_override = "C3 may pool its field counts"

pre-mutation deferred  : 9 paths
post-mutation deferred : 10 paths
newly deferred         : ["release_override"]
classification assigned: DEFERRED_OUT_OF_SCOPE

reported unknown_child_keys  : 0
reported unclassified_leaves : 0
leaf totality          : ACCEPTED
release authority      : ACCEPTED
FULL STATIC PREFLIGHT  : ACCEPTED       <-- the blocker
```

A C3 rule was introduced through the C2 branch, and the checker classified it as a
deferred C2 item because the exception set was read from the candidate.

**After repair:** `NORMATIVE_SURFACE_UNCLASSIFIED`, deferred count stays at 9,
`unknown_child_keys` reports 1.

Both are permanent regressions in
`test_e1a_v4_release_authority.py::test_list_and_deferred_scope_totality`.

---

## 3. Root causes

### A — selective list checking

The requirements list was secured by two mechanisms: the C3 and C4 lines were pinned
by position, and a count asserted that exactly two lines mentioned C3 or C4. Both held
under the attack. Neither constrained the **rest of the list**, so the list could grow.

The error was treating a list as a bag of individually interesting entries. For
authoritative content the opposite is true: **membership itself is authority**. A
requirements list that can be extended is not a specification of what is required.

The C3/C4-vocabulary heuristic made it worse — it is the same lexical-guard mistake
corrected in round r5, reintroduced at list level. An added requirement that never
names C3, C4, pooling or a field is still an added requirement.

### B — candidate-derived exception set

The deferred set was built as

```python
for key in plan[root]["derived_boundaries"].get(short) or {}:
    add(SemanticLeaf(..., DEFERRED_OUT_OF_SCOPE, ...))
```

i.e. *whatever the candidate currently carries under C2 is deferred*. An exception set
read from the document it excuses is self-authorising. The candidate could widen its
own exemption, and the coverage counters reported zero unknown keys while doing it,
because the new key had been silently classified.

This is the same shape as r5 (text excused by classification) and r7 (descendants
excused by a classified parent): **an exception that the candidate can grow**.

---

## 4. Final-list architecture

### Canonical complete list

`final_campaign_requirements()` returns the complete ordered sequence, built from:

* `FINAL_CAMPAIGN_REQUIREMENT_PINS` — the nine lines belonging to other cases (C1, C2,
  C5–C8, failure classes, denominator rule, mandatory diagnostics), held as exact pins;
* `_GENERATED_REQUIREMENT_SLOTS = (2, 3)` — the C3 and C4 lines, **generated** by
  `render_field_size_requirement` from `FIELD_SIZE_RULES`.

Nothing in it is read from the candidate.

### Order semantics — normative

**Order is scientifically normative here**, so an exact ordered sequence comparison
applies. Two independent reasons:

* every line carries its own ordinal (`"1. "`, `"2. "`, …), so position is part of the
  statement and a reordering makes the text self-contradictory;
* the Markdown renders them as a numbered list, re-deriving the display number from
  position.

The suite asserts the ordinal-matches-position property directly.

### What the single comparison secures

One row compares the whole list, which yields all of:

```text
length          addition         omission
membership      duplication      replacement
order           prepend/insert   swap
```

Verified by eleven list mutations; **all refuse**, including three that name no C3,
C4, pooling or field vocabulary at all.

---

## 5. Deferred-exception architecture

### Fixed path set

```text
DEFERRED_C2_QUARANTINE   : the exact nine pre-existing C2 leaf keys and values
DEFERRED_C2_LEAF_PATHS   : the nine full paths, derived from that table
DEFERRED_C2_TRACKER      : "D6a - C2 pooling authority-text binding"
```

Built from the fixed table, never from the candidate. Consequences, each tested:

| Attempt | Result |
|---|---|
| add a new deferred C2 leaf | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| add a nested child object under the C2 branch | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| rename a deferred leaf | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| delete a deferred leaf | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| change a deferred leaf's type | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| replace a deferred leaf with an object | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| mutate a quarantined value | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| smuggle a C3 rule through a new C2 child | `NORMATIVE_SURFACE_UNCLASSIFIED` |

A deferred ancestor authorises no descendants: the declared leaves are scalars, so any
nesting beneath one produces undeclared leaves and refuses.

### No candidate-driven expansion

The suite rebuilds the verifier structures exactly as preflight does, from candidates
that add a C2 child, remove a C2 child, and replace the entire C2 branch. In all three
the expected deferred set is **unchanged** and equal to the fixed nine.

### Quarantine is not approval

This distinction is the point of §12–§14 and is held explicitly:

```text
MUTATION QUARANTINE          : CLOSED
  the unresolved C2 bytes may not drift before D6a

SCIENTIFIC C2 POOLING AUTHORITY : OPEN
  C2 has no canonical pooling rule object, its text is generated from nothing,
  and its leaves remain classified DEFERRED_OUT_OF_SCOPE naming D6a
```

Both halves are asserted separately in the suite, and the leaf `source` field reads
`"DEFERRED_C2_QUARANTINE (mutation quarantine only)"` so the distinction is visible at
the point of use.

---

## 6. Two further instances found by the same audit

Searching for both shapes — selectively-checked lists, and candidate-derived
registration — found two more, now closed:

**Other controlled lists.** `cases[C3/C4].allowed_seed_families` and
`cases[C3/C4].subconditions` accepted added, removed and reordered elements. They
belong to G3 and the declared subcondition set, so they are **pinned** (`CASE_LIST_PINS`)
as tripwires rather than taken into F1e custody. Eight list mutations now refuse.

**Candidate-conditional registration.** Two `c3_semantics` keys were registered only
`if key in semantics`, so deleting the key deleted its check — the mirror image of
blocker B. Registration is now driven by the canonical rule
(`rule.secondary_diagnostic is not None`), and a **declared key that is absent now
refuses**. The `derived_boundaries` leaf loop was likewise switched from iterating the
candidate's keys to iterating the canonical surface registry.

| Deletion | Before | After |
|---|---|---|
| `c3_semantics.requires_block1_calibration` | ACCEPTED | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| `c3_semantics.why_calibration_is_retained` | ACCEPTED | `NORMATIVE_SURFACE_UNCLASSIFIED` |
| `cases[C3].allowed_seed_families` | ACCEPTED | `NORMATIVE_SURFACE_UNCLASSIFIED` |

---

## 7. Machine-derived coverage

From `field_size_amendment_counts(plan)`:

```json
{
  "controlled_normative_lists": 7,
  "canonical_list_elements": 30,
  "unexpected_list_elements": 0,
  "missing_list_elements": 0,
  "deferred_exception_paths_expected": 9,
  "deferred_exception_paths_observed": 9,
  "unexpected_deferred_paths": 0,
  "missing_deferred_paths": 0,
  "semantically_free_rule_bearing_locations": 0,
  "normative_surface_locations": 144,
  "unclassified_normative_amendment_fields": 0
}
```

and from `size_semantics_leaf_counts(plan)`:

```json
{
  "total_leaves": 50, "declared_leaves": 50,
  "unclassified_leaves": 0, "unknown_child_keys": 0,
  "missing_declared_leaves": 0, "deferred_out_of_scope_leaves": 9
}
```

### Controlled normative lists and their verification mode

| List | Elements | Mode |
|---|---:|---|
| `final_campaign_classification.requirements` | 11 | generated slots + exact pins, whole sequence compared |
| `cases[C3].fields_affected` | 4 | `GENERATED_FROM_CANONICAL` |
| `cases[C4].fields_affected` | 4 | `GENERATED_FROM_CANONICAL` |
| `cases[C3].allowed_seed_families` | 3 | `STRICTLY_VERIFIED_DUPLICATE` (pinned) |
| `cases[C4].allowed_seed_families` | 3 | `STRICTLY_VERIFIED_DUPLICATE` (pinned) |
| `cases[C3].subconditions` | 4 | `STRICTLY_VERIFIED_DUPLICATE` (pinned) |
| `cases[C4].subconditions` | 1 | `STRICTLY_VERIFIED_DUPLICATE` (pinned) |
| `interpretation.forbidden_wording` | 4 | `STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA` |

All counts are derived from the registry and the live structures, not hard-coded.

---

## 8. Regression tests

### Known escape classes

| # | Audit | Escape class | Result |
|---|---|---|---|
| 1 | first | G4 ANY_FIELD / pooling | REFUSED |
| 2 | first | C3 ANY_FIELD criterion | REFUSED |
| 3 | first | C4 pooled criterion | REFUSED |
| 4 | r2 inventory | assurance `acceptance_rule` | REFUSED |
| 4b | r2 inventory | assurance `quantity` | REFUSED |
| 5 | r2 inventory | section-12a boundary prose | REFUSED |
| 6 | r2 inventory | semantics `release_criterion` | REFUSED |
| 7 | r2 inventory | G4 gap statement | REFUSED |
| 8 | second | derived-boundary pooling | REFUSED |
| 9 | second | final campaign any-one-field rule | REFUSED |
| 10 | fourth | C3 explanatory P1-decides-release | REFUSED |
| 11 | fourth | C4 Block-1 role | REFUSED |
| 12 | fifth | nested `interpretation.detector` | REFUSED |
| 13 | fifth | nested `two_questions.B_component_size_inflation` | REFUSED |
| 14 | **sixth** | **extra contradictory final-campaign requirement** | REFUSED |
| 15 | **sixth** | **rule smuggled through a dynamically deferred C2 child** | REFUSED |

```text
16 classes tested, 0 survive, unexpected passes = 0
```

### Mutation groups in this round

| Group | Count | Accepted |
|---|---:|---:|
| final-campaign requirement list mutations | 11 | 0 |
| other controlled list mutations | 8 | 0 |
| deferred-path structural attacks | 8 | 0 |
| declared-key deletions | 3 | 0 |
| candidate-independence rebuilds of the deferred set | 3 | n/a (set unchanged) |
| final-rule combination mutations | 3 | 0 |
| preserved earlier attacks (r5, r7) | 4 | 0 |

### Preserved guarantees

Re-verified unchanged: recursive `size_validation_semantics` leaf totality, unknown-child
refusal, required-leaf deletion refusal, no classified parent auto-authorising
descendants, the r5 explanatory-semantics protection and its paraphrase, and the r7
nested-leaf blockers. No-self-validation now holds for the requirements list and the
deferred set as well as the surface registry.

---

## 9. Scientific non-change

```text
NO C3/C4 SCIENTIFIC DECISION CHANGED
```

The plan JSON and Markdown are **byte-unchanged** at `1.14.0`, so this is provable by
hash rather than by inspection:

| Artifact | SHA-256 |
|---|---|
| plan JSON | `16b0384d0022bb34e5733e09d0d6a233ab245f066987604f0a721e286629067e` |
| plan Markdown | `70f81dce52161bb17122d27f1c9211e9d7f724493a92cc4581df43d3e43c3d76` |

C3 and C4 remain `PER_FIELD`, reduction `NONE`, pooling `FORBIDDEN`, with R = 400 at
`alpha_2 = 0.001` (clean 0–2) and R = 2000 at `alpha_1 = 0.004` (clean 0–13),
one-sided 95% Clopper-Pearson LOWER. C3's primary release is the G5 block with full P1
a non-release secondary diagnostic; C4's primary is the Block-1 achieved size. The
≥ 0.90 target remains C1-only, and the dependence wording still claims no direction.

---

## 10. C2 status

```text
C2 SCIENTIFIC POOLING AUTHORITY:
OPEN

D6a:
REQUIRED

THIS TASK DID NOT SCIENTIFICALLY CLEAR C2
```

```text
C2 DEFERRED SURFACE: FIXED / QUARANTINED AGAINST EXPANSION
```

What changed: the nine C2 leaves can no longer be added to, renamed, deleted, retyped
or edited. What did **not** change: C2 still has no canonical pooling rule object, no
generated criterion, and no binding between its pooling text and any approved rule. The
quarantine pin asserts *these bytes*, not *this rule is right* — if C2's approved
science were ever determined to differ from the pinned text, nothing here would catch
it. That is precisely the work D6a must still do.

---

## 11. Superior authority unchanged

Byte-identical at this commit, verified by SHA-256 over a clean `git archive`
extraction:

| Source | SHA-256 |
|---|---|
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| `docs/theory/EBU_THEORY_BASELINE.md` | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| `docs/e1a/e1a_v4_design_contract.json` | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` |
| `docs/e1a/e1a_v4_seed_map.json` | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` |
| execution seal | state `PRE_DRIVER`, unchanged |

---

## 12. Identity consequences

Computed twice from two independent clean `git archive` extractions of `d8fc58c`; both
passes agreed exactly.

| Identity | Value |
|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **UNCHANGED** |
| unsealed execution identity | `e9cba511…` → `76e3190a3d1a7d5ff7c6a0778636e1b9ad6a96c80283ab23220e4af10be5cf88` |

The execution identity moved because the authority-verification code changed; no plan
or scientific file did. **It was not frozen.**

Chain: `2d1ae732…` → `94870965…` → `43e493ff…` → `56427563…` → `666ee1e3…` →
`e9cba511…` → `76e3190a…`.

---

## 13. Changed files

| File | Purpose |
|---|---|
| `e1a_v4/validation/release_authority.py` | `final_campaign_requirements`, `FINAL_CAMPAIGN_REQUIREMENT_PINS`, `CASE_LIST_PINS`, `DEFERRED_C2_QUARANTINE`, `DEFERRED_C2_LEAF_PATHS`, `DEFERRED_C2_TRACKER`; whole-list comparison; canonical-driven registration; declared-key existence rule; deferred leaves compared; list and deferred coverage counts |
| `test_e1a_v4_release_authority.py` | new `test_list_and_deferred_scope_totality` group; escape set → 16 classes; probe D widened; the r7 C2 test rewritten (below) |

Two tests changed meaning, both deliberately:

* **Probe D (C8 R 200 → 201)** recomputes C8's requirement line, which the complete
  sequence now pins, so the list check refuses before the replicate-count binding.
  Both refusals are correct; the expectation accepts either, with the reason recorded.
* **The r7 test "the C2 residual is STILL reachable"** asserted that the C2 pooling
  rewrite was accepted. §13 of this task deliberately changes that. It is replaced by
  two separate assertions — quarantine closed, scientific authority still open — so the
  distinction cannot quietly collapse into "C2 is fine".

---

## 14. Tests

```text
suites      : 15 (all pure/static)
checks      : 2,755
failures    : 0
trajectories: 0
```

| Suite | Checks |
|---|---:|
| `test_e1a_v4_release_authority.py` | 905 |
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

`test_e1a_v4_campaign_driver.py` remains a **KNOWN DEFERRED TEST**: not executed, no
runtime status claimed.

---

## 15. Runtime status

```text
F1f DRIVER/CLASSIFIER UPDATE = NOT STARTED
```

The campaign driver, C3/C4 aggregation, classifier and terminal aggregation were not
modified. `replicate_level_rejections` still raises
`ENDPOINT_EVENT_REDUCTION_UNDECLARED` for both cases.

---

## 16. Execution status

```text
OFFICIAL RESULTS            = NONE
OFFICIAL CAMPAIGN JOBS      = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
FINAL EXECUTION SEAL        = NOT FROZEN
EXECUTION AUTHORISED        = FALSE
CAMPAIGN                    = NOT RUN
```

Nothing was pushed.

---

## 17. Limitations and open items

* The pins in `CASE_LIST_PINS`, `FINAL_CAMPAIGN_REQUIREMENT_PINS` and
  `DEFERRED_C2_QUARANTINE` are tripwires over text owned by other cases and
  dispositions. A later authorised amendment to C1, C5–C8, G3 or the subcondition set
  must update its pin deliberately.
* Recursive leaf totality is enforced for `size_validation_semantics`. The C3/C4 case
  records are swept exhaustively for their own keys, prose and now lists, but are still
  not a full recursive leaf walk of nested sub-objects; element-level content inside
  `subconditions` is now pinned, which closes the practical gap without making the walk
  general. Extending the recursive walk to the remaining containers remains the natural
  next hardening step and is **not** claimed to be done.
* **C2 scientific pooling authority** remains OPEN; D6a REQUIRED (§10).
* Standing open items, unchanged: shared-drag gamma-sign authority, absolute drag and
  field construction (η, a), generator identity, PRNG authority, C6 inputs, remaining
  C8 inputs, diagnostic aggregator authority.

---

## 18. Next stage

```text
F1e-r10 INDEPENDENT RE-AUDIT
READY
```

Not started and not authorised. `F1f — DRIVER/CLASSIFIER IMPLEMENTATION UPDATE`
remains **NOT STARTED**.

---

```text
C3/C4 LIST AND DEFERRED-SCOPE AUTHORITY REPAIR COMMITTED
```
