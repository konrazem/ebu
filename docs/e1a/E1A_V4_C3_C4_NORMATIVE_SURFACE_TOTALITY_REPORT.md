# E1a v4 — C3/C4 NORMATIVE-SURFACE TOTALITY REPAIR

**Stage.** `F1e — PROSPECTIVE C3/C4 PER-FIELD AUTHORITY AMENDMENT`, repair round 3
(`F1e-r3`).

**Nothing was executed.** No RNG object was constructed for scientific purposes, no
random number drawn, no trajectory generated, no calibration sampled, no campaign job
run, no official result observed. The execution seal was not frozen and execution was
not authorised.

| | |
|---|---|
| Work commit | `29387fb49b1f058000b9487975f3769e2b015760` |
| Work tree | `fd4ee651f4acee22dad2525ea8948377877db0dc` |
| Follow-up work commit | `658c16a9c5aa9805d71175dd683b0fac92570dd2` |
| Follow-up work tree | `0fd2132769846edcc28e82258205df5491a3cc6d` |
| Parent | `b1d5a735ae6b78cbcdffe965a89ac401dd8e43af` (F1e-r2 report) |
| Plan version | `1.11.0` → **`1.12.0`** |
| Branch | `gaussian/stage-a-environment` (nothing pushed) |

The approved C3/C4 science was not under review and did not change.

---

## 1. Second-audit blockers, reproduced before repair

Both were reproduced on an isolated copy of the committed package at `b1d5a73`,
**before any edit**, by changing one JSON value and regenerating every generated
Markdown region so the two renderings still agreed.

### Escape A — derived-boundary pooling

Located structurally, not by line number:
`size_validation_semantics.derived_boundaries.C3.pooling` (and the identical `.C4`).

```text
old: "FORBIDDEN - every field is reported separately"
new: "POOLED - all four field counts are summed into one campaign count"

Markdown/JSON coherence : PASSES
FULL STATIC PREFLIGHT   : ACCEPTED        <-- the blocker
```

### Escape B — final campaign rule

`final_campaign_classification.rule`.

```text
old: "CONJUNCTIVE. Every required case must pass on its own terms."
new: "CONJUNCTIVE over cases. C3 and C4 pass when ANY ONE declared field is
      clean; a failure in the other three fields is tolerated."

Markdown/JSON coherence : PASSES
FULL STATIC PREFLIGHT   : ACCEPTED        <-- the blocker
```

After the repair both refuse:

```text
ESCAPE A -> PROSPECTIVE_AMENDMENT_MISMATCH
ESCAPE B -> PROSPECTIVE_AMENDMENT_MISMATCH
```

Both are permanent regressions in
`test_e1a_v4_release_authority.py::test_c3_c4_normative_surface_totality`, as classes
8 and 9 of the known-escape set, each asserting that Markdown and JSON still agree
before asserting that preflight refuses — the point of the audit is that coherence is
no defence.

---

## 2. Root cause — why the previous canonical bindings did not cover these

The F1e-r2 repair introduced the right architecture: a canonical `FIELD_SIZE_RULES`
object held in the case-release-specification layer *above* the machine plan, with
normative renderings generated from it and compared byte-exactly. That architecture
is sound and is retained unchanged.

What it lacked was **totality**. The set of bound locations was assembled by
enumeration — the three strings the first audit named, plus four more found by
inspecting the plan for field-structure prose. Enumeration produces a set that is
correct about what it contains and silent about what it omits. Specifically:

* **Escape A.** The `derived_boundaries` rows bound `per_field`,
  `replicate_reduction`, `rule`, `replicates`, `nominal_alpha` and `boundary` — six of
  the nine keys. `pooling` was simply not in the list. It is the one key in that
  container whose entire content is the pooling decision, and it was bound to nothing.

* **Escape B.** The final-campaign *requirement lines* for C3 and C4 were generated,
  but `rule` — the statement that governs how those lines combine — was free text. The
  lines said each case must produce no failure "in any required field"; the rule that
  made them conjunctive was unbound, so it could be replaced with a disjunctive one
  while the lines stayed correct.

The common shape is now explicit: **one scientific decision has several normative
representations, and nothing guaranteed the set of them was complete.** Two audits
found two different members of that set. A third enumeration would have been a third
guess.

---

## 3. Normative-surface architecture

```text
            FIELD_SIZE_RULES  (canonical source, above the plan)
                              |
            NORMATIVE SURFACE REGISTRY  (total over controlled containers)
                              |
        +---------------------+---------------------+
        |                     |                     |
  GENERATED_FROM_      STRICTLY_VERIFIED_    NON_NORMATIVE_
     CANONICAL            DUPLICATE          EXPLANATION
        |                     |                     |
        +---------------------+---------------------+
                              |
                require_field_size_surface_totality   -> NORMATIVE_SURFACE_UNCLASSIFIED
                require_field_size_amendment          -> PROSPECTIVE_AMENDMENT_MISMATCH
                              |
                          PREFLIGHT
```

### Canonical source

`e1a_v4/validation/release_authority.py`. `FIELD_SIZE_RULES` gained three fields so
that statements the plan already carried stop being hand-kept text:
`bound_statement`, `retention_statement`, `earlier_status`. Module constants gained
`FINAL_RELEASE_CONJUNCTION`, `FINAL_RELEASE_VERDICT`,
`FINAL_RELEASE_IMPLEMENTATION`, `FINAL_RELEASE_INDEPENDENT_FACTS` and the assurance
confidence vocabulary.

Two new renderers close the two escapes at their source:

* `render_field_size_pooling_statement(rule)` → `f"{rule.pooling} - every field is
  reported separately"`. The canonical constant `POOLING_FORBIDDEN` is the only place
  the word can come from. The generated value is **byte-identical to what the plan
  already carried**, so this bound an existing string without changing it.
* `render_final_campaign_rule()` → the conjunction, the per-field condition count
  derived from `len(FIELD_SIZE_REQUIRED_FIELDS)`, and
  `FINAL_RELEASE_COMPENSATION`.

### Surface registry

`NormativeSurface` is a frozen dataclass recording, per statement: the case, the
semantic role, the machine container and key, the Markdown rendering location, the
verification mode, the canonical expectation and the plan's actual value.
`normative_surface_registry(plan)` builds them all.

### Totality refusal

`require_field_size_surface_totality(plan)` enforces three properties and is wired
into `require_release_authority_conformance` immediately before the amendment check:

1. **Container totality.** Every key the plan carries inside a controlled container
   must have a registry entry. Eight containers are swept exhaustively.
2. **Vocabulary totality.** Inside the two C3/C4 case records and
   `size_validation_semantics`, any key whose *name* matches the field-rule
   vocabulary (`pool`, `compensat`, `reduction`, `field_structure`, `any_field`,
   `every_field`, `elementary_event`, `release_rule`, `field_condition`) must be
   registered. These containers are not swept exhaustively because they declare many
   things that are not field-size rules — seed families, subconditions, calibration
   scope — each governed by its own authority, and claiming all of them would be
   claiming authority this stage does not have.
3. **Explanation may not become rule.** Text classified `NON_NORMATIVE_EXPLANATION`
   may not contain field-rule prose vocabulary. An explanatory field that starts
   stating a field rule is refused.

### No self-validation

Expectations come only from the canonical layer. This is asserted directly rather
than argued: the test mutates the plan's own text, rebuilds the registry from the
mutated plan, and checks that **every expected value is unchanged** and still differs
from the mutated text. The forbidden architecture — derive the expectation from the
text under test — would make that assertion fail.

---

## 4. Complete inventory

Machine-derived from `field_size_amendment_counts(plan)`:

```json
{
  "canonical_rule_fields": 62,
  "normative_surface_locations": 101,
  "generated_normative_fields": 51,
  "strictly_verified_duplicate_fields": 49,
  "non_normative_explanatory_fields": 1,
  "controlled_containers": 8,
  "checked_total": 100,
  "unclassified_normative_amendment_fields": 0
}
```

```text
total normative C3/C4 semantic locations : 101
canonical sources                        :  62 fields on the canonical object
generated representations                :  51
strictly verified duplicates             :  49
non-normative explanatory occurrences    :   1
UNCLASSIFIED NORMATIVE LOCATIONS         :   0
```

`checked_total` is 100: every location except the single explanatory one carries an
equality row against the canonical rule.

### By container

| Container | Markdown rendering | Generated | Verified | Explanatory |
|---|---|---:|---:|---:|
| `authority_gaps.G4` | generated release-rules region | 2 | 3 | 0 |
| `cases[2]` (C3, registered keys) | generated cases region | 4 | 1 | 0 |
| `cases[2].c3_semantics` | generated cases region | 11 | 2 | 1 |
| `assurance[C3_g5_block]` | generated assurance region | 5 | 13 | 0 |
| `derived_boundaries.C3` | section 12a boundary table | 4 | 5 | 0 |
| `cases[3]` (C4, registered keys) | generated cases region | 3 | 1 | 0 |
| `cases[3].c4_semantics` | generated cases region | 9 | 0 | 0 |
| `assurance[C4_surrogate_validity]` | generated assurance region | 5 | 13 | 0 |
| `derived_boundaries.C4` | section 12a boundary table | 5 | 5 | 0 |
| `final_campaign_classification` | generated release-rules region | 3 | 6 | 0 |

The eight exhaustively swept containers are the last column's rows excluding
`cases[2]` and `cases[3]`, which are vocabulary-swept.

### The semantic classes required by the task, and where each lives

| Semantic class | Machine path | Mode |
|---|---|---|
| field scope | `cases[i].<semantics>.field_structure` | GENERATED |
| field membership | `cases[i].fields_affected` | GENERATED |
| field reduction | `cases[i].<semantics>.field_reduction` | GENERATED |
| pooling | `cases[i].<semantics>.pooling` | GENERATED |
| derived-boundary semantics | `derived_boundaries.{C3,C4}.per_field`, `.replicate_reduction` | GENERATED |
| **derived-boundary pooling** | `derived_boundaries.{C3,C4}.pooling` | **GENERATED (new)** |
| rejection-count semantics | `cases[i].<semantics>.field_structure_rule` | GENERATED |
| pass/fail criterion | `cases[i].formal_pass_fail_criterion` | GENERATED |
| release criterion | `cases[i].<semantics>.release_criterion` | GENERATED |
| assurance quantity | `assurance[case].quantity` | GENERATED |
| assurance acceptance rule | `assurance[case].acceptance_rule` | GENERATED |
| boundary prose | `derived_boundaries.{C3,C4}.rule` | GENERATED |
| case semantics | `cases[i].<semantics>.case_level_rule` | GENERATED |
| **final campaign rule** | `final_campaign_classification.rule` | **GENERATED (new)** |
| final campaign conjunction | `final_campaign_classification.requirements[2..3]`, `requirements` | GENERATED / VERIFIED |
| compensation | `final_campaign_classification.no_compensation_between_cases` | VERIFIED |
| required-field count | `cases[i].fields_affected` (order, membership, multiplicity) | GENERATED |
| G4 gap statement | `authority_gaps.G4.gap` | GENERATED |
| G4 resolution | `authority_gaps.G4.resolution` | GENERATED |
| G4 disposition | `authority_gaps.G4.{id,status,affects}` | VERIFIED |
| C3 primary endpoint | `cases[2].primary_release_endpoint` | GENERATED |
| C3 secondary diagnostic role | `cases[2].block1_role`, `.c3_semantics.joint_p1_result_changes_C3_release_verdict` | GENERATED |
| C4 primary endpoint | `cases[3].primary_release_endpoint` | GENERATED |
| C1-only ≥ 0.90 separation | `authority_gaps.G4.resolution`, `final_campaign_classification.independent_facts_rule` | GENERATED / VERIFIED |
| dependence wording | `authority_gaps.G4.resolution` | GENERATED |

---

## 5. Normative versus explanatory (§9 classification)

The registry does not treat every occurrence of "field" or "pooling" as normative.
Each entry was classified deliberately:

* **GENERATED_FROM_CANONICAL** — the statement *is* the rule. A formal acceptance
  criterion, the machine release rule, the derived-boundary rule and pooling
  sentences, the final campaign rule, the G4 resolution and gap statement. These are
  produced by a renderer and compared byte-exactly, so they cannot be edited at all.
* **STRICTLY_VERIFIED_DUPLICATE** — the statement restates something fixed elsewhere:
  the numeric size rules (R, nominal alpha, integer boundary, the two Clopper-Pearson
  values, recomputed here from `cp_lower`), the confidence vocabulary, the G4
  disposition identifiers, the final verdict and implementation pointer, and the
  count of requirement lines naming C3 or C4.
* **NON_NORMATIVE_EXPLANATION** — exactly one location:
  `cases[2].c3_semantics.why_calibration_is_retained`. It says *why* a diagnostic
  input is kept and sets no field rule. Marking it explanatory is not a loophole: the
  prose guard refuses it if it ever starts carrying field-rule vocabulary, and that
  case is tested.

An operating-characteristic note is non-normative unless it sets a rule; the one in
the G4 resolution is generated anyway, because its numbers are disclosure that must
not drift.

---

## 6. Known escape regression set

Every escape class any audit has demonstrated, re-run through the **whole** static
preflight with the Markdown regenerated so coherence passes first:

| # | Audit | Escape class | Result after repair |
|---|---|---|---|
| 1 | first | G4 resolution declares ANY_FIELD and pooling | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 2 | first | C3 formal criterion defines a replicate-wide event | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 3 | first | C4 formal criterion pools the four field counts | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 4 | first repair inventory | assurance `acceptance_rule` contradicts | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 5 | first repair inventory | section-12a boundary prose contradicts | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 6 | first repair inventory | semantics `release_criterion` contradicts | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 7 | first repair inventory | G4 gap statement contradicts | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 8 | **second** | **derived-boundary pooling says pool all four counts** | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| 9 | **second** | **final campaign rule: one clean field is enough** | `PROSPECTIVE_AMENDMENT_MISMATCH` |

```text
KNOWN COHERENT-WRONG ESCAPES SURVIVING: 0
```

For classes 1–9 the test also asserts that `require_plan_authority_coherence` still
**passes** on the mutated package, so each is confirmed to be the coherent-but-wrong
case the audits describe rather than a malformed document caught earlier.

---

## 7. Mutation coverage

```text
coherent wrong mutations : 117
unexpected passes        :   0
```

| Group | Count |
|---|---:|
| semantic token mutations across every normative surface class | 72 |
| required-field-list mutations (remove / duplicate / replace / extra / reorder, × 2 cases) | 10 |
| structured-field mutations of the G4 authority block | 13 |
| known escape classes re-run end to end | 9 |
| new-authoritative-field injections | 13 |
| **total** | **117** |

Every mutation names its semantic component and the exact structural path it edits,
asserts the old value was present, asserts the new value differs, and asserts the new
value is readable back at that path afterwards. There is no unrestricted whole-document
first-match replacement anywhere in the suite, and a mutation that fails to land is an
assertion error rather than a silent pass.

### Coverage against the required list

| Required mutation | Covered by |
|---|---|
| scope `PER_FIELD → ANY_FIELD` | semantics `field_structure`; both formal criteria |
| scope `PER_FIELD → REFERENCE_ONLY` | both formal criteria |
| reduction `NONE → ANY_FIELD` | derived-boundary `replicate_reduction` |
| reduction `NONE → EVERY_FIELD` | semantics `field_reduction`; both formal criteria |
| pooling `FORBIDDEN → ALLOWED` | semantics `pooling`; assurance `pooling`; derived-boundary `pooling` |
| pooling `FORBIDDEN → POOL_ALL_FIELDS` | derived-boundary `pooling` (both cases) |
| field set: remove / duplicate / replace / extra | `fields_affected` list mutations |
| derived boundary: per-field → pooled counts | derived-boundary `rule`, `pooling`, `per_field` |
| final campaign: all required → any one | `rule` (two independent token swaps) |
| final campaign: all required → three of four | `rule`; both requirement lines |
| final campaign: no compensation → compensation allowed | `rule`; `no_compensation_between_cases` |
| C3 diagnostic: secondary → release-bearing | `block1_role`; `joint_p1_...`; G4 resolution |
| C1-only target ≥ 0.90 applied to C3/C4 | G4 resolution; `independent_facts_rule`; 12th-requirement injection |
| dependence: unknown direction → positive-association assertion | G4 resolution |

### New-authoritative-field negative test (§15)

Thirteen plausible unregistered authoritative fields were injected into the controlled
sections. **All thirteen refuse.** Twelve are caught by the registry's own totality
check when it is called directly; the thirteenth — appending a twelfth requirement
line that weakens C3 — is caught by the amendment row that counts requirement lines
naming C3 or C4. Through the full stack the refusal codes are
`NORMATIVE_SURFACE_UNCLASSIFIED` (8), `PLAN_CASE_MISMATCH` (2),
`PLAN_SURFACE_UNDECLARED` (2) and `PROSPECTIVE_AMENDMENT_MISMATCH` (1) — several
layers refuse independently, which is the intended defence in depth.

---

## 8. Scientific non-change

```text
NO C3/C4 SCIENTIFIC DECISION CHANGED
```

Verified against the plan rather than assumed:

| Quantity | C3 | C4 |
|---|---|---|
| R per field | 400 | 2000 |
| nominal alpha | `alpha_2 = 0.001` | `alpha_1 = 0.004` |
| confidence method / level / side | Clopper-Pearson, 0.95, one-sided LOWER | same |
| integer rejection boundary | 2 (clean 0–2, 3+ inflation) | 13 (clean 0–13, 14+ inflation) |
| `cp_lower` at boundary / +1 | `0.0008891209480547668` / `0.002047258667372265` | `0.0038489424981444365` / `0.004236780498405868` |
| primary endpoint | `G5_BLOCK_SIZE` | `BLOCK1_ACHIEVED_SIZE` |

* C3's full P1 interaction result is still
  `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` and
  `joint_p1_result_changes_C3_release_verdict` is still `false`.
* The complete-pipeline ≥ 0.90 target remains **C1-only**. No C3 or C4 familywise
  target was created; a mutation that creates one refuses.
* The dependence wording still states that independence must not simply be assumed and
  that direction and magnitude are not established. The unsupported claim
  "shared common-mode draw → positive association" is absent, and a mutation
  introducing it refuses.
* Evaluation scope `PER_FIELD`, within-replicate reduction `NONE`, pooling
  `FORBIDDEN`, required fields exactly `theta0_circular, theta1_power,
  theta2_ellipse, theta3_temperature` in that order.

**The only plan content change** is `final_campaign_classification.rule`, which now
states the per-field conjunction it always implied:

```text
CONJUNCTIVE. Every required case must pass on its own terms. C3 and C4 each
contribute 4 required field-level conditions, one per declared field; a case is
clean only when all 4 are clean, NO required condition may fail, a single clean
field is NEVER sufficient, and compensation is FORBIDDEN both between fields and
between cases.
```

This strengthens the statement without changing the rule: the pre-existing
requirement lines already required no `STATISTICAL_SIZE_FAILURE` in any required
field, and `no_compensation_between_cases` and `no_weighted_score` were already
`true`. The derived-boundary pooling sentences are **byte-unchanged** — they were
bound, not rewritten.

---

## 9. A defect this task found and fixed in passing

`test_e1a_v4_case_scope.py` had been failing since `b1d5a73` and was not run during
F1e-r2. That repair regenerated `cases[2].c3_semantics.what_is_forbidden` from the
canonical rule; the regenerated wording names the three forbidden reductions without
using the word "forbidden", which a stale string-shape assertion required.

The defect was in the assertion, not in the plan. It is replaced by checks on the
three reductions the canonical text actually names, plus a new check that C3's release
criterion states no Block-1 threshold. The claim the old assertion stood for — that a
Block-1 release threshold cannot be added to C3 — is carried by the structured,
canonical-bound facts asserted immediately above it. Committed separately as
`658c16a`; no plan, authority or scientific content changed.

This is recorded because the F1e-r2 report stated nine suites green without this one
among them. The correct figure for that commit is one failing check in a suite that
was not run.

---

## 10. Superior authority unchanged

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

This is not a theory amendment.

---

## 11. Identity consequences

Computed twice from two independent clean `git archive` extractions of
`658c16a`; both passes agreed exactly, and both agreed with the pass taken at
`29387fb` (the test-only follow-up commit does not enter the package identity).

| Identity | Value |
|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **UNCHANGED** |
| unsealed execution identity | `43e493ff…` → `56427563967dc769f222688811b9ae7ac341ee44f204d1a73ef6509114adc662` |
| plan JSON | `2239b14f1cbd7303319999af9bfaf42fc69a1f0ae4e4153533eb59f81feec7f2` |
| plan Markdown | `f426d1c0bf35f704dc6f6234b2c701f358f9eed0159bb8aec21fb58baca3da0e` |

The analysis identity did not move, as required: no analysis-bound scientific file
changed. The unsealed execution identity moved because the authority-verification code
and one authority rendering changed. **It was not frozen.**

Chain of unsealed execution identities across this repair sequence:
`2d1ae732…` → `94870965…` → `43e493ff…` → `56427563…`.

---

## 12. Changed files

| File | Purpose |
|---|---|
| `e1a_v4/validation/release_authority.py` | canonical constants and renderers for the two escaped surfaces; `NormativeSurface`; `normative_surface_registry`; `require_field_size_surface_totality`; registry-derived `_amendment_rows` and counts |
| `e1a_v4/validation/refusals.py` | new `NormativeSurfaceUnclassified` / `NORMATIVE_SURFACE_UNCLASSIFIED` |
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | `final_campaign_classification.rule`; `plan_version` → `1.12.0` |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | regenerated: 7 generated regions, authority block, version line |
| `test_e1a_v4_release_authority.py` | new `test_c3_c4_normative_surface_totality` group; 25 further semantic mutations |
| `test_e1a_v4_driver_endpoints.py` | plan JSON/Markdown hash pins; the other five frozen entries deliberately still pass unchanged |
| `test_e1a_v4_case_scope.py` | the stale assertion of §9 (separate commit `658c16a`) |

Refusal codes: 81 classes / 80 distinct codes → **82 classes / 81 distinct codes**.
Exactly one added.

---

## 13. Tests

Fifteen pure deterministic suites. All static: text, JSON, hashing, arithmetic and
isolated pure-function checks. Sentinel RNG providers assert zero constructions on
every refusal path.

| Suite | Checks |
|---|---:|
| `test_e1a_v4_terminal_calibration.py` | 538 |
| `test_e1a_v4_release_authority.py` | 536 |
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
| **total** | **2,386 passed, 0 failed** |

`test_e1a_v4_campaign_driver.py` remains a **KNOWN DEFERRED TEST**: it was not
executed and no runtime status is claimed for it.

---

## 14. Runtime status

```text
F1f DRIVER/CLASSIFIER UPDATE = NOT STARTED
```

The driver and classifier were not modified. `replicate_level_rejections` still
raises `ENDPOINT_EVENT_REDUCTION_UNDECLARED` for both C3 and C4, which is the correct
pre-F1f behaviour: the runtime is deliberately behind prospective authority. This is
asserted behaviourally — by calling the function and reading the refusal code — not by
searching source text.

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

Nothing was pushed.

---

## 16. Limitations and open items

* The vocabulary sweep over the two case records and `size_validation_semantics`
  matches **key names**, not arbitrary new prose inside an already-registered field.
  Prose inside registered fields is covered because those fields are generated or
  strictly verified; prose in a brand-new field whose name avoids the vocabulary would
  not be. That is the honest residual boundary of this repair.
* `derived_boundaries.C2.pooling` carries the same free-text pooling sentence and is
  **outside this task's C3/C4 scope**. It is not currently bound to a canonical rule.
  C2's `unit` and `pooling` in its assurance row *are* bound by the contract bindings,
  and C2's per-field structure is carried from the contract clause "at every declared
  geometry", so the sentence is corroborated — but the same class of defect is open
  there and should be closed when C2 is next in scope.
* Standing open items, deliberately unresolved and unchanged by this task:
  shared-drag gamma-sign authority, absolute drag and field construction (η, a),
  generator identity, PRNG authority, C6 inputs, remaining C8 inputs, diagnostic
  aggregator authority.

---

## 17. Next stage

```text
F1e-r4 INDEPENDENT RE-AUDIT
READY
```

Not started and not authorised. `F1f — DRIVER/CLASSIFIER IMPLEMENTATION UPDATE`
remains **NOT STARTED**.

---

```text
C3/C4 NORMATIVE-SURFACE TOTALITY REPAIR COMMITTED
```
