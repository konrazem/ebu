# E1a v4 — C3/C4 NESTED SEMANTIC-LEAF TOTALITY REPAIR

**Stage.** `F1e — PROSPECTIVE C3/C4 PER-FIELD AUTHORITY AMENDMENT`, repair round 7
(`F1e-r7`), closing the blockers raised by the fifth independent audit (`F1e-r6`).

**Nothing was executed.** No RNG object constructed for scientific purposes, no random
number drawn, no trajectory generated, no calibration sampled, no campaign job run, no
official result observed. The execution seal was not frozen; execution was not
authorised.

| | |
|---|---|
| Work commit | `2bbca6b38853f0775b91cb5112434fa7685ce29a` |
| Work tree | `9c3d48a27fc00559881fc48e8e033af92f4d88ce` |
| Audited parent | `e2a53f8ccfb7a9683bd105ffe55efd1902208974` |
| Plan version | `1.13.0` → **`1.14.0`** |
| Branch | `gaussian/stage-a-environment` (nothing pushed) |

The approved C3/C4 science was not under review and did not change.

---

## 1. F1e-r6 blockers, reproduced before repair

Both reproduced on an isolated copy of the committed package at `e2a53f8`, **before
any edit**, by changing one nested JSON string and regenerating every generated
Markdown region.

### Blocker 1 — `size_validation_semantics.interpretation.detector`

```text
original : "inflation detected iff CP_lower(rejections, R) > nominal alpha"

contrary : "inflation detected iff CP_lower(pooled rejections across the four
            fields, 4R) > nominal alpha; C3 and C4 pool their four fields into
            one count"
```

### Blocker 2 — `size_validation_semantics.two_questions.B_component_size_inflation`

```text
original : "C2, C3 and C4. At the feasible replicate counts these are NOT positive
            proofs that the achieved rate is at or below a tiny nominal alpha.
            They prospectively TEST FOR EVIDENCE OF INFLATION: H0: p <= nominal
            alpha vs H1: p > nominal alpha, one-sided 5%."

contrary : "C2, C3 and C4. These are FAMILYWISE component tests over the pooled
            four-field count: a case is flagged only if the pooled rate exceeds
            nominal alpha, and a single clean field is sufficient for the case to
            pass."
```

### Results

| Checker | Blocker 1 | Blocker 2 |
|---|---|---|
| plan coherence | PASS | PASS |
| prospective-amendment checker | ACCEPTED | ACCEPTED |
| normative-surface totality checker | ACCEPTED | ACCEPTED |
| **full static preflight** | **ACCEPTED** | **ACCEPTED** |
| reported `semantically_free_rule_bearing_locations` | 0 | 0 |
| reported `unclassified_normative_amendment_fields` | 0 | 0 |

Both now refuse:

```text
Blocker 1 -> PROSPECTIVE_AMENDMENT_MISMATCH
Blocker 2 -> PROSPECTIVE_AMENDMENT_MISMATCH
```

raised by the new `require_size_semantics_leaf_totality`. Both are permanent
regressions in
`test_e1a_v4_release_authority.py::test_nested_semantic_leaf_totality`, each
asserting that Markdown and JSON still agree before asserting that preflight refuses.

---

## 2. Root cause

The F1e-r5 repair established that no *semantically free* text existed in the
controlled C3/C4 surface. That claim was true of the surface as it was then defined,
and false of the plan, because the surface was defined over **containers and their
immediate keys** rather than over **structures**.

Three consequences, all of which the audit exploited:

* **Classification stopped at the registered parent.** `size_validation_semantics`
  was registered and two of its top-level strings were pinned. Its nested objects —
  `interpretation`, `two_questions`, `verdicts`, `superseded_criterion` — were
  entirely unvisited. A classified parent implicitly trusted everything below it.
* **The coverage metric measured the wrong thing.** `controlled_string_locations`
  counted top-level strings only, so it reported 107 strings and 0 free while 29
  nested leaves were unbound. The number was not wrong about what it counted; it was
  counting a set that did not include the defect. That is the more serious failure
  here: the metric gave false assurance.
* **Markdown coherence could not help.** Neither leaf is rendered into any generated
  Markdown region, so the two-rendering agreement check never sees them. These leaves
  are JSON-only authority.

The pattern is the same enumeration failure as rounds r3 and r5, moved one structural
level down: locations (r3), then words (r5), now depth. The repair had to be depth-
independent, not a longer list of paths.

---

## 3. Repair architecture

```text
canonical sources above the plan
  FIELD_SIZE_RULES
  classification.SIZE_INTERPRETATION
  classification.SIZE_FAILURE / SIZE_NO_INFLATION
  the exact pins
                 |
         SemanticLeaf registry  (one entry per LEAF, any depth)
                 |
   recursive walk of the plan's OWN structure
                 |
   require_size_semantics_leaf_totality  -> NORMATIVE_SURFACE_UNCLASSIFIED
                                         -> PROSPECTIVE_AMENDMENT_MISMATCH
                 |
             PREFLIGHT
```

### Recursive traversal

`_subtree_leaf_paths` walks the live `size_validation_semantics` object to its leaves,
at any depth, treating a list of scalars as one leaf. The walk is over the **plan's
structure**, not over a list of expected paths, which is what makes the check
depth-independent: a new nested child anywhere appears as an undeclared leaf.

### Recursive child totality

`require_size_semantics_leaf_totality` enforces, in order:

1. every declared leaf carries a valid classification;
2. **every actual leaf is declared** — an unknown child at any depth refuses;
3. **every declared leaf exists** — an authority leaf may not be silently dropped;
4. every non-deferred leaf equals its canonical expectation exactly, by value and by
   type.

A classified parent authorises nothing. This is asserted directly: adding
`interpretation.whatever` refuses even though `interpretation` is registered.

### Leaf-level classification

Five classes, each leaf in exactly one:

| Class | Meaning |
|---|---|
| `GENERATED_FROM_CANONICAL` | produced by a renderer from the canonical rule |
| `STRICTLY_VERIFIED_DUPLICATE` | restates a canonical value held in code above the plan |
| `STRICTLY_PINNED_NON_RULE_TEXT` | exact pin of prose that is record rather than live rule |
| `STRUCTURAL_VALUE_WITH_EXPLICIT_SCHEMA` | number, flag or scalar list with an explicit expected value |
| `DEFERRED_OUT_OF_SCOPE` | enumerated and classified, deliberately **not** bound; names the task that owns it |

### Canonical sources that already existed

The strongest part of this repair required no new authority. `classification.py`
already held `SIZE_INTERPRETATION` — a machine-readable statement of exactly what a
size pass does and does not mean, including a `detector` entry — and the verdict
labels `SIZE_FAILURE` / `SIZE_NO_INFLATION`. The plan restates all of them. **Nothing
had ever compared them.** The whole `interpretation` block is now bound to that
constant, which closes blocker 1 against an independent source in code rather than
against anything in the document under test.

---

## 4. Machine-derived coverage

From `size_semantics_leaf_counts(plan)`:

```json
{
  "controlled_subtrees": 1,
  "controlled_nested_objects": 10,
  "total_leaves": 50,
  "declared_leaves": 50,
  "generated_leaves": 10,
  "strictly_verified_leaves": 17,
  "exact_pinned_leaves": 12,
  "structural_schema_leaves": 2,
  "deferred_out_of_scope_leaves": 9,
  "unclassified_leaves": 0,
  "unknown_child_keys": 0,
  "missing_declared_leaves": 0
}
```

```text
UNCLASSIFIED LEAVES UNDER size_validation_semantics = 0
UNKNOWN NESTED AUTHORITY KEYS                       = 0
CONTRARY-RULE-CAPABLE UNBOUND LEAVES (in scope)     = 0
```

The counts are derived from the actual structures, not hard-coded; the suite asserts
that the five class counts sum to the declared total and that declared equals actual.

### By nested object

| Object | Leaves | How held |
|---|---:|---|
| `size_validation_semantics` (top level) | 2 | exact-pinned (`status`, `detector`) |
| `.two_questions` | 2 | 1 generated (`B_component_size_inflation`), 1 pinned (C1's statement) |
| `.verdicts` | 2 | strictly verified against `SIZE_FAILURE` / `SIZE_NO_INFLATION` |
| `.interpretation` | 6 | strictly verified against `classification.SIZE_INTERPRETATION` (5) + structural list (1) |
| `.superseded_criterion` | 5 | exact-pinned (4) + structural tolerance (1) |
| `.superseded_criterion.why_insufficient` | 4 | exact-pinned |
| `.derived_boundaries.C3` | 9 | generated / verified via the normative-surface registry |
| `.derived_boundaries.C4` | 10 | generated / verified via the normative-surface registry |
| `.derived_boundaries.C2` | 9 | **deferred out of scope** (see §8) |
| `.derived_boundaries` | — | container |

---

## 5. Unknown-key attacks at multiple depths

Ten unregistered children injected into the controlled subtree. **All refuse** with
`NORMATIVE_SURFACE_UNCLASSIFIED`:

| Depth | Injected key | Result |
|---|---|---|
| 1 | `size_validation_semantics.pooling_override` | REFUSED |
| 2 | `interpretation.pooling_override` | REFUSED |
| 2 | `interpretation.release_rule` | REFUSED |
| 2 | `two_questions.C3_global_pooling` | REFUSED |
| 2 | `two_questions.release_override` | REFUSED |
| 2 | `verdicts.on_pooled_detection` | REFUSED |
| 2 | `superseded_criterion.new_rule` | REFUSED |
| 3 | `derived_boundaries.C3.pooling_override` | REFUSED |
| 3 | `derived_boundaries.C4.field_reduction` | REFUSED |
| 3 | `superseded_criterion.why_insufficient.C5` | REFUSED |

Plus two structural properties:

```text
classified parent + unregistered child  -> REFUSED
deletion of a declared authority leaf   -> REFUSED
```

---

## 6. Complete known-escape regression set

| # | Audit | Escape class | Result |
|---|---|---|---|
| 1 | first | G4 resolution declares ANY_FIELD and pooling | REFUSED |
| 2 | first | C3 formal criterion defines a replicate-wide event | REFUSED |
| 3 | first | C4 formal criterion pools the four field counts | REFUSED |
| 4 | first repair inventory | assurance `acceptance_rule` contradicts | REFUSED |
| 4b | first repair inventory | assurance `quantity` contradicts | REFUSED |
| 5 | first repair inventory | section-12a boundary prose contradicts | REFUSED |
| 6 | first repair inventory | semantics `release_criterion` contradicts | REFUSED |
| 7 | first repair inventory | G4 gap statement contradicts | REFUSED |
| 8 | second | derived-boundary pooling says pool all four counts | REFUSED |
| 9 | second | final campaign rule: one clean field is enough | REFUSED |
| 10 | fourth | C3 explanatory text makes full P1 the release condition | REFUSED |
| 11 | fourth | C4 Block-1 role demoted to secondary | REFUSED |
| 12 | **fifth** | **nested `interpretation.detector` pools the four fields** | REFUSED |
| 13 | **fifth** | **nested `two_questions.B` becomes a pooled familywise test** | REFUSED |

```text
14 classes tested, 0 survive, unexpected passes = 0
```

### Nested leaf mutation classes

Sixteen coherent contrary rewrites across every string-leaf class in the subtree — per
field → pooled, component → familywise, all fields → any field, secondary → deciding,
diagnostic → release-bearing, did-not-establish → proved, superseded → live
classifier, confidence level 5% → 50%, verdict labels relabelled, C1's 0.90 target
moved and extended to C3/C4. **All refuse; 0 unexpected passes.**

### The guarantee is structural, not lexical

Re-asserted here as in F1e-r5: with `FIELD_RULE_PROSE_TOKENS` emptied to `()`, both
audit blockers still refuse. The refusal comes from the leaf differing from its
canonical expectation, not from word detection. The keyword list remains a secondary
diagnostic only.

### No self-validation

The suite mutates the candidate subtree, rebuilds the leaf registry **from the mutated
plan**, and asserts every expected value is unchanged and still differs from the
mutated text. Expectations derive from `FIELD_SIZE_RULES`,
`classification.SIZE_INTERPRETATION`, the verdict constants and the pins — never from
the subtree being checked.

### Earlier repairs preserved

The F1e-r4 attack `"The full P1 verdict is the deciding condition for C3."` and its
paraphrases still refuse, and the normative-surface registry still reports
`unclassified = 0` and `semantically free = 0`. Totality was extended, not weakened.

---

## 7. Scientific non-change

```text
NO C3/C4 SCIENTIFIC DECISION CHANGED
```

| | C3 | C4 |
|---|---|---|
| evaluation scope | `PER_FIELD` | `PER_FIELD` |
| within-replicate reduction | `NONE` | `NONE` |
| pooling | `FORBIDDEN` | `FORBIDDEN` |
| primary release | G5 / Block-2 size | Block-1 achieved size |
| full P1 role | `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` | — |
| full P1 feeds primary release | **FALSE** | — |
| R per field | 400 | 2000 |
| nominal alpha | `alpha_2 = 0.001` | `alpha_1 = 0.004` |
| Clopper-Pearson rule | one-sided LOWER, 0.95 | one-sided LOWER, 0.95 |
| integer boundary | 2 (clean 0–2) | 13 (clean 0–13) |

* Final release unchanged: four required C3 field conditions, four required C4 field
  conditions, all required, global conjunction, compensation `FORBIDDEN`.
* The complete-pipeline ≥ 0.90 target remains **C1-only**. A mutation extending it to
  C3/C4 refuses.
* The dependence wording still states that independence must not simply be assumed and
  that direction and magnitude are not established.

**The only plan content change** is
`two_questions.B_component_size_inflation` (plus the version bump). The original three
sentences are preserved; the generated form appends the canonical per-field scope so
the pooled/familywise rewrite cannot be stated there. The H0/H1 clause spacing now
matches `classification.SIZE_INTERPRETATION["test"]` exactly, because the generated
text takes it from that constant rather than restating it.

---

## 8. C2 residual

```text
C2 DERIVED-BOUNDARY POOLING ISSUE:
CONFIRMED
OUT OF SCOPE
NOT REPAIRED
```

`C2 RESIDUAL = CONFIRMED / UNCHANGED / DEFERRED`

C2's nine derived-boundary leaves fall inside the subtree this task made total, so
leaving them undeclared would have left `unclassified_leaves > 0`, while binding them
would have made the tracked defect's symptom disappear. Neither is acceptable, so they
are classified `DEFERRED_OUT_OF_SCOPE`, each naming the task that owns it
(`D6a - C2 pooling authority-text binding`).

They are therefore **enumerated and classified but deliberately unbound**. Verified at
this commit, and asserted permanently in the suite:

```text
derived_boundaries.C2.pooling -> "POOLED - all four field counts summed"
    require_size_semantics_leaf_totality : ACCEPTED (not refused)
    require_field_size_amendment         : ACCEPTED (not refused)
```

The open item remains visible and reachable. This repair neither closed nor masked it.

---

## 9. Superior authority unchanged

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

This is verifier hardening only. Not a theory amendment.

---

## 10. Identity consequences

Computed twice from two independent clean `git archive` extractions of `2bbca6b`; both
passes agreed exactly.

| Identity | Value |
|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **UNCHANGED** |
| unsealed execution identity | `666ee1e3…` → `e9cba5119d191c0e66b7df057da13f8661e24e19f671dec91fa2fd9e9376c143` |
| plan JSON | `16b0384d0022bb34e5733e09d0d6a233ab245f066987604f0a721e286629067e` |
| plan Markdown | `70f81dce52161bb17122d27f1c9211e9d7f724493a92cc4581df43d3e43c3d76` |

The analysis identity did not move: no analysis-bound scientific file changed. The
unsealed execution identity moved because the authority-verification code and one
authority leaf changed. **It was not frozen.**

Chain: `2d1ae732…` → `94870965…` → `43e493ff…` → `56427563…` → `666ee1e3…` →
`e9cba511…`.

---

## 11. Changed files

| File | Purpose |
|---|---|
| `e1a_v4/validation/release_authority.py` | `SemanticLeaf`, `size_semantics_leaves`, `_subtree_leaf_paths`, `require_size_semantics_leaf_totality`, `size_semantics_leaf_counts`, `render_component_size_question`, `TWO_QUESTIONS_COMPLETE_PIPELINE_PIN`, `SUPERSEDED_CRITERION_PINS`, three new leaf classes |
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | generated `two_questions.B_component_size_inflation`; `plan_version` → `1.14.0` |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | regenerated: 7 generated regions, authority block, version line |
| `test_e1a_v4_release_authority.py` | new `test_nested_semantic_leaf_totality` group; escape set → 14 classes; probes A and B widened (below) |
| `test_e1a_v4_driver_endpoints.py` | plan JSON/Markdown hash pins; the other five frozen entries deliberately still pass unchanged |

No new refusal code was needed.

### A note on probes A and B

The two oldest named release probes — C1 target `0.90 → 0.80` and C1 `R = 300 → 301` —
deliberately rewrite `two_questions.A_complete_practical_performance` so the mutation
is coherent everywhere the target is stated. That leaf is now exact-pinned, so the
leaf-totality check refuses **before** the contract-release binding is reached. Both
refusals are correct; the expectations were widened to accept either, with the reason
recorded at the probe table. This is a side effect of the C1 statement gaining a
binding it did not have.

---

## 12. Tests

```text
suites      : 15 (all pure/static; the set was re-enumerated, not assumed)
checks      : 2,653
failures    : 0
trajectories: 0
```

| Suite | Checks |
|---|---:|
| `test_e1a_v4_release_authority.py` | 803 |
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

---

## 13. Runtime status

```text
F1f DRIVER/CLASSIFIER UPDATE = NOT STARTED
```

The campaign driver, C3/C4 endpoint aggregation, classifier and terminal result
aggregation were not modified. `replicate_level_rejections` still raises
`ENDPOINT_EVENT_REDUCTION_UNDECLARED` for both C3 and C4 — correct pre-F1f behaviour.

---

## 14. Execution status

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

## 15. Limitations and open items

* Recursive leaf totality is now enforced for `size_validation_semantics`. The C3/C4
  case records and the other controlled containers are covered by the
  normative-surface registry, which sweeps their **own** keys exhaustively and their
  prose completely, but is not itself a recursive leaf walk of nested sub-objects
  inside those containers. The one nested structure there (`subconditions`) holds
  enum-like identifiers governed by G3 and contract/plan conformance. Extending the
  same recursive walk to the remaining controlled containers is the natural next
  hardening step and is **not** claimed to be done here.
* The pins take snapshots of text owned by other dispositions (C1's statement, the
  superseded criterion). These are deliberate tripwires; a later authorised amendment
  must update the corresponding pin.
* `superseded_criterion.retained_as` in the plan and `classification.GROSS_INFLATION_
  LABEL` in code state the same thing in different words. The plan's value is pinned
  as it stands; this divergence is recorded as an observation, not repaired, because
  aligning them would be a content change without authority.
* **C2 derived-boundary pooling** remains confirmed, unchanged and deferred (§8).
* Standing open items, unchanged: shared-drag gamma-sign authority, absolute drag and
  field construction (η, a), generator identity, PRNG authority, C6 inputs, remaining
  C8 inputs, diagnostic aggregator authority.

---

## 16. Next stage

```text
F1e-r8 INDEPENDENT RE-AUDIT
READY
```

Not started and not authorised. `F1f — DRIVER/CLASSIFIER IMPLEMENTATION UPDATE`
remains **NOT STARTED**.

---

```text
C3/C4 NESTED SEMANTIC-LEAF TOTALITY REPAIR COMMITTED
```
