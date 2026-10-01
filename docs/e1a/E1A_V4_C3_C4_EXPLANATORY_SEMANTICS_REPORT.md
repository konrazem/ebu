# E1a v4 — C3/C4 EXPLANATORY-SEMANTICS REPAIR

**Stage.** `F1e — PROSPECTIVE C3/C4 PER-FIELD AUTHORITY AMENDMENT`, repair round 5
(`F1e-r5`), closing the blocker raised by the fourth independent audit (`F1e-r4`).

**Nothing was executed.** No RNG object constructed for scientific purposes, no random
number drawn, no trajectory generated, no calibration sampled, no campaign job run, no
official result observed. The execution seal was not frozen; execution was not
authorised.

| | |
|---|---|
| Work commit | `0107635b444bc48544ecf9fb71bbaad0f2040afc` |
| Work tree | `73340c3e6e5be7f8b51105eb1123a02583f8e7f8` |
| Audited parent | `a4c494ddddd4730dbca737633d42968752964cfc` |
| Plan version | `1.12.0` → **`1.13.0`** |
| Branch | `gaussian/stage-a-environment` (nothing pushed) |

The approved C3/C4 science was not under review and did not change.

---

## 1. F1e-r4 blocker, reproduced before repair

Reproduced on an isolated copy of the committed package at `a4c494d`, **before any
edit**, by replacing one JSON string and regenerating every generated Markdown region
so the two renderings still agreed.

**Location.** `cases[2].c3_semantics.why_calibration_is_retained`.

```text
approved: "the frozen scientific purpose requires reporting the two-mode max
           statistic's INTERACTION WITH THE TWO-BLOCK GATE. That interaction is a
           P1 quantity and needs a CalibrationArtifact, so calibration is
           retained as a diagnostic input."

attack:   "The full P1 verdict is the deciding condition for C3."
```

The attack states the opposite of the approved science: C3's primary release is the
per-field G5 / Block-2 size, and the full P1 result is a
`SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` that does **not** feed primary release.

```text
Markdown/JSON coherence : PASS
FULL STATIC PREFLIGHT   : ACCEPTED        <-- the blocker
```

Five paraphrases from the audit brief, and one further paraphrase that avoids every
plausible rule word, were all **ACCEPTED** as well:

| Attack | Before repair | After repair |
|---|---|---|
| "The full P1 verdict is the deciding condition for C3." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| "The outcome of the complete P1 procedure determines whether C3 succeeds." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| "C3 succeeds according to the full P1 result." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| "The G5 result is informative, while the complete P1 result governs C3." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| "Only a successful full P1 outcome permits C3 acceptance." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| "C3 follows the combined P1 verdict." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |
| "For C3 the complete two-block result carries the release; the block-2 number is reported alongside it." | ACCEPTED | `PROSPECTIVE_AMENDMENT_MISMATCH` |

All are permanent regressions in
`test_e1a_v4_release_authority.py::test_c3_explanatory_semantics`, each asserting that
Markdown and JSON still agree before asserting that preflight refuses.

---

## 2. Root cause

Two things combined.

**The location was semantically free.** It was the single registry entry classified
`NON_NORMATIVE_EXPLANATION`. That classification was a deliberate choice in the F1e-r3
repair, justified at the time as "it says *why* a diagnostic input is kept and sets no
field rule". The justification was about the text that happened to be there, not about
what the location permitted. Anyone who could edit it could write a different rule.

**The guard was a keyword heuristic.** The only protection was a seven-token list —
`pool`, `compensat`, `reduction`, `field`, `any one`, `every one`, `reference-field` —
and the auditor's sentence contains **none of them**. Verified mechanically:

```text
"The full P1 verdict is the deciding condition for C3."   blacklist tokens: []
"C3 follows the combined P1 verdict."                     blacklist tokens: []
```

This is not a gap in the list; it is the wrong kind of guarantee. Natural language
states any rule without any particular word, so a finite vocabulary can never decide
whether prose has become rule-bearing. Adding `deciding`, `condition` and `verdict`
would have left the identical defect one paraphrase away — which is exactly the
enumeration failure that F1e-r3 was supposed to have ended, repeated at the level of
words instead of locations.

The F1e-r3 report named this residual in its own §16 ("prose in a brand-new field
whose name avoids the vocabulary would not be [covered]"). The audit found the sharper
case: prose in an **already-registered** field.

---

## 3. Final architecture

The repair follows §5 of the task: **canonical rule → generated explanation**.

### The location is GENERATED

`render_field_size_calibration_rationale(rule)` in
`e1a_v4/validation/release_authority.py` builds the text from canonical values only.
Its generated form keeps the original reason verbatim and then states the approved
role:

```text
the frozen scientific purpose requires reporting the two-mode max statistic's
INTERACTION WITH THE TWO-BLOCK GATE. That interaction is a P1 quantity and needs a
CalibrationArtifact, so calibration is retained as a diagnostic input. The full P1
result is the SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC and does NOT determine
the C3 primary release verdict, which remains the PER_FIELD G5_BLOCK_SIZE
assessment over theta0_circular, theta1_power, theta2_ellipse, theta3_temperature.
```

Every semantic token there is read off `FIELD_SIZE_RULES`, including the **verb**:

```python
decides = ("does NOT determine" if rule.secondary_feeds_primary_release is False
           else "determines")
```

So the sentence cannot contradict the structured flag beside it — flip the flag and
the prose flips with it. That is asserted directly in the suite.

### No semantically free text remains in the controlled surface

Generating one field would have left the same class open in its neighbours, so the
guarantee is now structural rather than textual:

```text
every STRING inside a controlled C3/C4 record is
    GENERATED_FROM_CANONICAL   or   STRICTLY_VERIFIED_DUPLICATE (pinned exactly)
```

`require_field_size_surface_totality` enforces four properties:

1. every key inside a controlled container is classified;
2. **every string inside a controlled C3/C4 record is generated or pinned** — an
   unregistered string refuses;
3. **`NON_NORMATIVE_EXPLANATION` is forbidden inside the controlled surface** — the
   classification that bought the attack its freedom can no longer be applied there;
4. non-string keys remain swept by field-rule key vocabulary (a number or flag cannot
   state a rule in prose).

Property 2 is the guarantee. `CASE_PROSE_PINS` holds the exact approved text of all
36 remaining strings in the two C3/C4 case records; `SHARED_SIZE_SEMANTICS_PINS` holds
the two top-level `size_validation_semantics` strings, including `detector`, which
states the size-detection rule itself.

### Why pinning rather than removal

§6 offered removal to non-normative commentary as the alternative. Generation was
chosen for `why_calibration_is_retained` because the statement is genuinely useful
beside the rule it qualifies, and the repository convention in that container is
already generation — eleven of its fourteen keys were generated before this repair.
Pinning was chosen for the surrounding case prose because those strings belong to
**other** dispositions (the frozen scientific purpose, G3 seed-family grants,
calibration scope). Moving them would restructure authority this stage does not own;
pinning freezes the text this stage was built against without taking custody of the
decision. A later authorised amendment to one of those dispositions must update its
pin deliberately — that tripwire is intended behaviour, not a conflict.

---

## 4. The keyword heuristic is no longer the guarantee

Stated explicitly, as §7 requires: **`FIELD_RULE_PROSE_TOKENS` is not treated as the
primary semantic guarantee.** It is retained only as a cheap secondary tripwire that
would fire if some future entry were ever classified `NON_NORMATIVE_EXPLANATION`
again, and the module comment says so.

Demonstrated two independent ways in the suite:

* **The list would never have fired.** Seven of the eight attack texts contain zero
  listed tokens.
* **Refusal survives the list being emptied.** With
  `FIELD_RULE_PROSE_TOKENS` set to `()`, every attack still refuses with
  `PROSPECTIVE_AMENDMENT_MISMATCH` — the refusal comes from the candidate text
  differing from the generated canonical rendering, nothing else.

```text
with the keyword list EMPTIED:
  auditor attack                         -> PROSPECTIVE_AMENDMENT_MISMATCH
  paraphrase, no rule words              -> PROSPECTIVE_AMENDMENT_MISMATCH
  semantically correct manual paraphrase -> PROSPECTIVE_AMENDMENT_MISMATCH
```

---

## 5. Correct paraphrases also refuse — deliberately

A hand-written paraphrase that is **scientifically correct** also refuses:

```text
"Block-1 calibration is kept only as a diagnostic input; the full P1 result is a
 secondary predeclared interaction diagnostic and does not decide C3, whose
 primary release stays the per-field G5 block size assessment."

-> PROSPECTIVE_AMENDMENT_MISMATCH
```

This is recorded as intended behaviour, per §12. For this controlled plan surface:

```text
canonical semantics  >  free editorial paraphrasing
```

Scientific authority does not need unrestricted prose editing. Wording changes here
are made by changing the renderer in the case-release-specification layer and
regenerating, which leaves a reviewable diff in the authority code rather than in the
document under test.

---

## 6. Explanatory-location inventory

Every location in the controlled C3/C4 surface whose name matches
`why|rationale|explan|note|comment|descript|interpret|purpose|basis|reason` was
examined against the §9 question — *could changing only this text alter how a
competent reader understands what passes, what fails, what is primary, what is
secondary, whether fields pool, whether reduction occurs, whether compensation is
allowed?*

The honest answer for **every** free-text field is yes, because free text can say
anything. All were therefore generated or pinned.

| | Before | After |
|---|---:|---:|
| controlled explanatory locations | 1 | 0 |
| generated/bound explanatory locations | 0 | 1 (generated) |
| **semantically free rule-bearing locations** | **≥ 1** | **0** |
| **unclassified normative locations** | 0 | **0** |
| controlled string locations | 107 | 107 |

Machine-derived from `field_size_amendment_counts(plan)`:

```json
{
  "canonical_rule_fields": 62,
  "semantically_free_rule_bearing_locations": 0,
  "controlled_string_locations": 107,
  "normative_surface_locations": 140,
  "generated_normative_fields": 53,
  "strictly_verified_duplicate_fields": 87,
  "non_normative_explanatory_fields": 0,
  "controlled_containers": 8,
  "checked_total": 140,
  "unclassified_normative_amendment_fields": 0
}
```

### By container

| Container | Generated | Verified | Explanatory |
|---|---:|---:|---:|
| `authority_gaps.G4` | 2 | 3 | 0 |
| `cases[2]` (C3 record) | 4 | 19 | 0 |
| `cases[2].c3_semantics` | 12 | 2 | 0 |
| `assurance[C3_g5_block]` | 5 | 13 | 0 |
| `derived_boundaries.C3` | 4 | 5 | 0 |
| `cases[3]` (C4 record) | 4 | 19 | 0 |
| `cases[3].c4_semantics` | 9 | 0 | 0 |
| `assurance[C4_surrogate_validity]` | 5 | 13 | 0 |
| `derived_boundaries.C4` | 5 | 5 | 0 |
| `size_validation_semantics` (shared header) | 0 | 2 | 0 |
| `final_campaign_classification` | 3 | 6 | 0 |
| **total** | **53** | **87** | **0** |

### A second finding from the same audit

`cases[3].block1_role` — C4's declaration that Block-1 is its
`PRIMARY_RELEASE_ENDPOINT` — carried **no binding from any checker**: not the
normative-surface registry, not the release bindings, not contract/plan conformance.
It is a primary/secondary status statement, squarely inside §4's list, and it was
free. It is now generated from the canonical primary endpoint
(`render_field_size_block1_role`), and both directions of swap refuse:

```text
C4 block1_role -> SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC -> REFUSED
C3 block1_role -> PRIMARY_RELEASE_ENDPOINT                     -> REFUSED
```

---

## 7. Complete known-escape regression set

Every escape class any audit has demonstrated, re-run through the **whole** static
preflight with the Markdown regenerated so coherence passes first:

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
| 10 | **fourth** | **C3 explanatory text makes full P1 the release condition** | REFUSED |
| 11 | **fourth** | **C4 Block-1 role demoted to secondary** | REFUSED |

All refuse with `PROSPECTIVE_AMENDMENT_MISMATCH`.

```text
KNOWN COHERENT-WRONG ESCAPES SURVIVING: 0
```

---

## 8. Mutation coverage

```text
coherent wrong mutations : 150
unexpected passes        :   0
```

| Group | Count |
|---|---:|
| semantic token mutations across every normative surface class | 72 |
| required-field-list mutations (× 2 cases) | 10 |
| G4 structured-field mutations | 13 |
| known escape classes re-run end to end | 12 |
| new-authoritative-field injections | 13 |
| explanatory attacks and paraphrases | 8 |
| the same attacks re-run with the keyword list emptied | 8 |
| new free-text key injections into controlled records (3 keys × 2 cases) | 6 |
| smuggled rules in pinned prose (4 case pins + 2 shared pins) | 6 |
| `block1_role` primary/secondary swaps | 2 |
| **total** | **150** |

Every mutation names its semantic component and exact structural path, asserts the old
value was present, asserts the new value differs, and asserts it is readable back at
that path. No unrestricted whole-document first-match replacement is used anywhere.

### Totality guarantees preserved (§14)

Re-verified unchanged by this repair: controlled containers, unknown-key refusal, the
surface registry, exact path targeting, no-self-validation (expectations rebuilt from
a *mutated* plan are byte-identical to those from the honest plan), canonical source
independent of the candidate plan, and `unclassified normative locations = 0`.
Totality was not weakened to close the explanatory problem; it was extended.

---

## 9. Scientific non-change

```text
NO C3/C4 SCIENTIFIC DECISION CHANGED
```

Verified against the plan, not assumed:

| | C3 | C4 |
|---|---|---|
| primary release | per-field **G5 / Block-2** size | per-field **Block-1** achieved size |
| full P1 role | `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` | — |
| full P1 feeds primary release | **FALSE** | — |
| evaluation scope | `PER_FIELD` | `PER_FIELD` |
| within-replicate reduction | `NONE` | `NONE` |
| pooling | `FORBIDDEN` | `FORBIDDEN` |
| R per field | 400 | 2000 |
| nominal alpha | `alpha_2 = 0.001` | `alpha_1 = 0.004` |
| Clopper-Pearson rule | one-sided LOWER, 0.95 | one-sided LOWER, 0.95 |
| integer boundary | 2 (clean 0–2) | 13 (clean 0–13) |

* Final campaign rule unchanged: all four required C3 field conditions, all four
  required C4 field conditions, global conjunction, compensation `FORBIDDEN`.
* The complete-pipeline ≥ 0.90 target remains **C1-only**; no C3/C4 familywise target
  exists and a mutation creating one refuses.
* The dependence wording still states that independence must not simply be assumed and
  that direction and magnitude are not established. The unsupported
  "shared common-mode draw → positive association" claim is absent; a mutation
  introducing it refuses.

**The only plan content change** is `cases[2].c3_semantics.why_calibration_is_retained`
(plus the version bump). The original sentence is preserved verbatim; the generated
form appends the approved role statement that the audit showed was unprotected.

---

## 10. C2 residual

```text
C2 DERIVED-BOUNDARY POOLING ISSUE:
CONFIRMED
OUT OF SCOPE
NOT REPAIRED
```

`C2 RESIDUAL = CONFIRMED, UNCHANGED, DEFERRED TO D6a`

Verified at this commit that the repair did not accidentally close or mask it:

```text
derived_boundaries.C2.pooling in the F1e registry : False
value                                             : "FORBIDDEN - every field is
                                                     reported separately"
mutation to "POOLED - all four counts summed"
    -> require_field_size_amendment          : ACCEPTED (not refused)
    -> require_field_size_surface_totality   : ACCEPTED (not refused)
```

Pinning `size_validation_semantics.status` and `.detector` — strings shared by C2, C3
and C4 — is a tripwire on that shared text only. It changes no C2 science and does not
address C2's actual defect, which is that its derived-boundary pooling statement has
no binding to a canonical pooling rule. That remains open for its own bounded task.

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

This is not a theory amendment.

---

## 12. Identity consequences

Computed twice from two independent clean `git archive` extractions of `0107635`;
both passes agreed exactly.

| Identity | Value |
|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` — **UNCHANGED** |
| unsealed execution identity | `56427563…` → `666ee1e35a2d81c134315e5a929a446429192c41777784f2ab4d9bf54328b517` |
| plan JSON | `bbb5fd60ea657a9204a27b57ba982ebb75519ff6cd6c4c57a5329fa401b85db8` |
| plan Markdown | `eeed237aeda14f03b309cadbc8f3ff5d682f7016151a3132238d3d398a38d3c6` |

The analysis identity did not move: no analysis-bound scientific file changed. The
unsealed execution identity moved because the authority-verification code and one
authority rendering changed. **It was not frozen.**

Chain: `2d1ae732…` → `94870965…` → `43e493ff…` → `56427563…` → `666ee1e3…`.

---

## 13. Changed files

| File | Purpose |
|---|---|
| `e1a_v4/validation/release_authority.py` | `render_field_size_calibration_rationale`, `render_field_size_block1_role`, `CASE_PROSE_PINS`, `SHARED_SIZE_SEMANTICS_PINS`; no-free-prose rule and explanatory-mode ban in `require_field_size_surface_totality`; keyword list demoted to secondary; `semantically_free_rule_bearing_locations` metric |
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | generated `why_calibration_is_retained`; `plan_version` → `1.13.0` |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | regenerated: 7 generated regions, authority block, version line |
| `test_e1a_v4_release_authority.py` | new `test_c3_explanatory_semantics` group; escape set extended to 12 classes |
| `test_e1a_v4_driver_endpoints.py` | plan JSON/Markdown hash pins; the other five frozen entries deliberately still pass unchanged |

No new refusal code was needed: `NORMATIVE_SURFACE_UNCLASSIFIED` and
`PROSPECTIVE_AMENDMENT_MISMATCH` already express both failures. The file still declares
82 classes / 81 distinct codes.

---

## 14. Tests

```text
suites      : 15 (all pure/static; the authoritative set was re-enumerated, not assumed)
checks      : 2,507
failures    : 0
trajectories: 0
```

| Suite | Checks |
|---|---:|
| `test_e1a_v4_release_authority.py` | 657 |
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

No RNG object was constructed for scientific purposes, no calibration executed and no
campaign job run. `test_e1a_v4_campaign_driver.py` remains a **KNOWN DEFERRED TEST**:
not executed, no runtime status claimed.

---

## 15. Runtime status

```text
F1f DRIVER/CLASSIFIER UPDATE = NOT STARTED
```

The driver and classifier were not modified. `replicate_level_rejections` still raises
`ENDPOINT_EVENT_REDUCTION_UNDECLARED` for both C3 and C4 — correct pre-F1f behaviour,
asserted behaviourally rather than by source search.

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

* The no-free-prose rule covers the eight controlled containers, the two C3/C4 case
  records and the two shared `size_validation_semantics` header strings. Nested
  structures inside those records (`subconditions`) are swept by key vocabulary only;
  their string values are enum-like identifiers governed by G3 and contract/plan
  conformance, not free prose.
* The prose pins take a snapshot of text owned by other dispositions. This is a
  deliberate tripwire, documented at the constant. A later authorised amendment to the
  frozen scientific purpose, G3 or calibration scope must update the corresponding pin.
* **C2 derived-boundary pooling** remains confirmed, unchanged and deferred (§10).
* Standing open items, unchanged by this task: shared-drag gamma-sign authority,
  absolute drag and field construction (η, a), generator identity, PRNG authority,
  C6 inputs, remaining C8 inputs, diagnostic aggregator authority.

---

## 18. Next stage

```text
F1e-r6 INDEPENDENT RE-AUDIT
READY
```

Not started and not authorised. `F1f — DRIVER/CLASSIFIER IMPLEMENTATION UPDATE`
remains **NOT STARTED**.

---

```text
C3/C4 EXPLANATORY-SEMANTICS REPAIR COMMITTED
```
