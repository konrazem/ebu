# E1a v4 — C3/C4 structured-refusal authority amendment (F1f-d)

Implementation report for the prospective authority amendment recorded as
**`authority_gaps` G5** at plan version **1.15.0**.

```text
STAGE               F1f-d  PROSPECTIVE AUTHORITY AMENDMENT FOR C3/C4
                           STRUCTURED REFUSALS
STARTING COMMIT     5aae2ff639f2ba44ad1969403b67f9f5d1879f6f
AMENDMENT RECORD    docs/e1a/E1A_V4_C3_C4_STRUCTURED_REFUSAL_AMENDMENT.md
```

This stage changes **authority only**. The driver, the classifier, the result
schemas and the serialization layer are untouched, and the runtime still aborts on
the counterexample by design — see §12.

---

## 1. The exact previous gap

A valid structured refusal can leave a C3 **G5 / Block-2** or C4 **Block-1**
decision undefined, because each is a decision of *one block* of the two-block P1
gate and a refusal that produced no p-values leaves that block with no value.

Frozen authority defined refusal treatment for **complete-pipeline success only**:
the contract states it inside `complete_pipeline.denominator`,
`synthetic_validation_requirements[9]` names complete-pipeline success, the plan's
key is literally `complete_pass_denominator` with its `refusals` value ending
"**for complete-pipeline success**", and the mandatory diagnostic carrying the
`denominator_rule` aggregate key is bound to `case_id: "C1_true_bridge_complete"`.

C1 could not absorb it: C1 and C3/C4 are **disjoint job sets** — 300 replicates for
C1 against 400 for C3 and 2000 for C4.

The frozen size vocabulary offered exactly two verdicts, the second of which was
`otherwise`. Applying that detector to an incomplete primary sequence would have
reported a required field as showing no significant size inflation on evidence
never obtained — in the limit `0/400` with every replicate refused.

The reconstruction `E1A_V4_C3_C4_REFUSAL_AGGREGATION_AUTHORITY_REPORT.md` returned
**UNSPECIFIED** and put one question to the author. This stage records the answer.

---

## 2. The approved human decision

Recorded verbatim in the amendment record. In one paragraph: an undefined primary
endpoint is **neither a rejection nor a non-rejection**; the planned `R` is
preserved as the primary denominator; any structured refusal affecting a required
field's primary endpoint makes that field's primary size assessment
`NOT_EVALUABLE`; `NOT_EVALUABLE` is neither of the two statistical verdicts;
`NOT_EVALUABLE` prevents the campaign from passing, under a failure reason that
names incomplete required evidence rather than size inflation; the terminal report
is still produced; a survivor-conditioned figure may exist only as a labelled
SECONDARY diagnostic; and nothing about per-field scope, pooling, cross-field
reduction, the endpoint definitions, the alphas or the boundaries changes.

```text
OFFICIAL CAMPAIGN RESULTS OBSERVED = NO
OFFICIAL CAMPAIGN JOBS EXECUTED = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
FINAL EXECUTION SEAL = NOT FROZEN
EXECUTION AUTHORISED = FALSE
```

The amendment therefore precedes outcome inspection and is not post-outcome tuning.

---

## 3. Authority files changed, and why

Each candidate layer was inspected and decided on its own merits rather than
edited by default.

| file | authority it carries | decision |
|---|---|---|
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | MACHINE PLAN — the case set, the size-validation semantics, the derived boundaries, the disposition records and the final campaign classification | **CHANGED.** C3 and C4 are *plan* constructs and the size verdict vocabulary is plan-owned. This is where the decision operates. |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | MARKDOWN PLAN — the normative human rendering of the same authority | **CHANGED.** Regenerated so the amendment is human-visible; a JSON-only rule would be authority hidden from its readers. |
| `docs/e1a/e1a_v4_design_contract.json` | FROZEN DESIGN / VALIDATION AUTHORITY | **NOT CHANGED.** The contract **does not name C3 or C4 anywhere** (zero occurrences), so the decision cannot be stated there without inventing case names at a layer that does not carry them. Its refusal vocabulary, its reconciliation rule and its complete-pipeline denominator are all preserved and are *relied on* by the amendment. |
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | FROZEN DESIGN | **NOT CHANGED.** Its §14 refusal semantics and its §12 complete-pass event remain exactly as frozen; the amendment adds nothing to them and contradicts nothing in them. |
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | physical core | **NOT CHANGED.** This is validation-protocol science; it alters no EBU physical theory. |
| `docs/theory/EBU_THEORY_BASELINE.md` | working theory baseline | **NOT CHANGED**, same reason. |
| `e1a_v4/validation/release_authority.py` | CASE RELEASE SPECIFICATION / machine authority | **CHANGED.** Carries the canonical `STRUCTURED_REFUSAL_RULE` and its renderers, so every normative rendering of the amendment is *generated* from one object rather than hand-kept prose. |
| `e1a_v4/validation/coherence.py` | the Markdown/JSON rendering specification | **CHANGED.** `SEMANTICS_LABELS` gained a label per new semantics key; without it the new keys would not render and the JSON/Markdown comparison refuses — which is exactly what it did on the first regeneration attempt. |

**The precedent is exact.** The G4 per-field amendment (`c086cd2`) was an equally
genuine new human decision about C3/C4 and changed the same set: plan JSON, plan
Markdown, `coherence.py`, `release_authority.py` and tests. The design contract was
not touched then either.

The rule is **not hidden in verifier code**. It is stated in the controlling
machine plan, rendered in the normative Markdown as the G5 disposition and as rows
in each case's semantics table, and the code holds the canonical object the plan is
checked against.

---

## 4. Status vocabulary

The size verdict vocabulary becomes **three-way**, with an explicit precedence:

```json
"verdicts": {
  "on_detection": "STATISTICAL_SIZE_FAILURE",
  "otherwise": "NO_SIGNIFICANT_SIZE_INFLATION_DETECTED",
  "on_undefined_primary_endpoint": "NOT_EVALUABLE",
  "evaluation_order": "resolved in order: if any required PRIMARY endpoint decision
    for the field is undefined because of a valid structured refusal the verdict is
    NOT_EVALUABLE and the detector is NOT run; only on a COMPLETE primary sequence,
    with structured_refusal_count = 0, do on_detection and otherwise apply"
}
```

Repository-native names were kept where they existed: `STATISTICAL_SIZE_FAILURE`
and `NO_SIGNIFICANT_SIZE_INFLATION_DETECTED` are unchanged, and only
`NOT_EVALUABLE` is new.

The **precedence is itself normative**. The two statistical verdicts partition
every `(rejections, R)` pair between them, so without an explicit order the
`otherwise` branch would keep claiming a clean field from an incomplete sequence —
the pathology the amendment exists to prevent.

**No new failure classification was invented.** The campaign-level reason is
`VALIDATION_INCONCLUSIVE`, which was already frozen in `failure_classifications`
and carried no declared trigger anywhere in authority; this supplies one. It is
deliberately not `STATISTICAL_SIZE_FAILURE`, which would assert a rejection that
never happened, and deliberately not `STRUCTURED_REFUSAL_EXCESS`, whose name
implies a tolerated fraction this amendment does not create.

---

## 5. Planned / evaluable / refusal count semantics

The primary denominator does **not** shrink.

```text
primary_denominator            PLANNED_R_PRESERVED
C3 planned_R                   400 per field
C4 planned_R                   2000 per field
```

Three quantities are therefore distinguished and all three are required per field:

| quantity | meaning |
|---|---|
| `planned_R` | the declared replicate count — the primary denominator, always |
| `evaluable_primary_endpoint_count` | replicates whose primary endpoint decision exists |
| `structured_refusal_count` | replicates whose primary endpoint is undefined |
| `defined_rejection_count` | rejections among the defined primary endpoints only |
| `primary_size_status` | one of the three verdicts |
| `refusal_reasons` | the refusal identities/reasons |

A survivor-conditioned rate computed over `evaluable_primary_endpoint_count` is
permitted only in the role design §14 and
`complete_pass_denominator.conditional_diagnostics` already allow: labelled
**SECONDARY**, beside the unconditional figure. `survivor_conditioned_rate_role` is
`SECONDARY_DIAGNOSTIC_ONLY`, and it **never** substitutes for the primary
planned-R assessment.

Creating that diagnostic is **not** made mandatory. The mandatory set is the six
items above.

---

## 6. Release semantics

```text
release_requires    EVALUABLE_AND_CLEAN
```

A required field satisfies its condition only when its primary size assessment is
an evaluable, clean verdict. Both other states block release, with **different
reasons**:

| field state | campaign | reason |
|---|---|---|
| `NO_SIGNIFICANT_SIZE_INFLATION_DETECTED` | may pass | — |
| `STATISTICAL_SIZE_FAILURE` | cannot pass | the size test rejected |
| `NOT_EVALUABLE` | cannot pass | required validation evidence is incomplete |

The generated requirement lines now carry it:

```text
3. C3 is EVALUABLE_AND_CLEAN in every required field: no
   STATISTICAL_SIZE_FAILURE and no NOT_EVALUABLE field
4. C4 is EVALUABLE_AND_CLEAN in every required field: no
   STATISTICAL_SIZE_FAILURE and no NOT_EVALUABLE field
```

and so does the generated final rule, which previously spoke only of "clean":

> A required field satisfies its condition only when it is EVALUABLE_AND_CLEAN: a
> field whose primary size assessment is NOT_EVALUABLE has NOT satisfied it, and
> prevents the campaign from passing under VALIDATION_INCONCLUSIVE rather than
> under STATISTICAL_SIZE_FAILURE.

`NOT_EVALUABLE` applies **independently by field**; one field's evaluability never
rescues another's. No pooling, no ANY_FIELD or EVERY_FIELD reduction, and no
multiplicity correction is introduced. The tolerated structured-refusal fraction is
`NONE` — one refusal is enough.

---

## 7. All-refused semantics

For a required C3 field with `planned_R = 400`, `evaluable_N = 0`,
`structured_refusals = 400`:

```text
primary result   NOT_EVALUABLE
campaign         cannot PASS, classified VALIDATION_INCONCLUSIVE
terminal report  STILL PRODUCED
```

It must **not** report `0/400 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED`, which is
what the frozen two-way detector would mechanically have produced, and must **not**
fabricate 400 statistical rejections. C4 is analogous.

---

## 8. Partial-refusal semantics

For `planned_R = 400`, `evaluable_N = 399`, `structured_refusals = 1`, defined G5
rejections `= 2`:

```text
primary result   NOT_EVALUABLE
campaign         cannot PASS
```

`2 / 399` is **not** promoted to the primary preregistered size assessment. It may
exist only as a labelled SECONDARY diagnostic.

This is the case the reconstruction quantified: `2 + 1 refusal` at C3 and
`13 + 1 refusal` at C4 sat exactly where the candidate semantics diverged, one
flipping the field to a size failure and the others to clean. Under the approved
rule the field is neither — it is not evaluable, and the campaign fails for the
honest reason.

---

## 9. Terminal-report requirement

```text
valid structured refusal
-> terminal record preserved
-> campaign aggregation completes
-> final report exists
```

`terminal_report_required_under_all_refusals: true`. This is not a new rule: the
contract's `refusal_semantics.reconciliation` and design §14 already say the report
"must finish even when every job refuses". The amendment **connects** that standing
requirement explicitly to C3 and C4, where the current runtime violates it.

---

## 10. Mutation tests

A new permanent group, `F1f-d G5 structured-refusal authority`, with **110 checks**
in `test_e1a_v4_release_authority.py`. It asserts the canonical rule, asserts that
every normative rendering IS the generated canonical text, asserts the numeric size
rules are untouched, and then runs a **39-mutation audit**: each mutation edits one
named authoritative location, the Markdown is regenerated so the package stays
fully coherent, and full static preflight must still refuse.

| mutation class | tested | all refuse |
|---|---|---|
| `None -> rejection` (block, C3, C4) | 3 | yes |
| `None -> non-rejection` (block, C3, C4) | 3 | yes |
| evaluable_N promoted to primary denominator | 3 | yes |
| refusal resolved to an ordinary clean verdict | 2 | yes |
| refusal resolved to a statistical size failure | 2 | yes |
| detector run on an incomplete sequence / precedence inverted | 2 | yes |
| `NOT_EVALUABLE` allowed to pass release | 5 | yes |
| terminal report no longer required under all-refused | 2 | yes |
| survivor-conditioned figure promoted to primary | 2 | yes |
| a tolerated-refusal threshold introduced | 3 | yes |
| full P1 substituted for an undefined G5 / Block-1 | 4 | yes |
| C2 dragged into the amendment | 2 | yes |
| failure reason turned into a size failure | 2 | yes |
| the G5 disposition record itself (affects / status / gap / encoding) | 4 | yes |

```text
structured-refusal mutation audit: 39 tested, 0 unexpected passes
```

Every one is a *coherent* edit: the JSON and the Markdown agree after the
regeneration, so these are not caught by Markdown/JSON coherence. They refuse
because each location is bound to the canonical rule object.

### Totality hardening preserved

The amendment was **integrated into** the existing machinery rather than bolted
beside it. Nothing was weakened:

- the **normative-surface registry** grew from 196 to 236 locations; the G5
  disposition record joins the exhaustively swept containers, which rose from 10
  to 11;
- the **recursive semantic-leaf walk** over `size_validation_semantics` grew from
  50 to 74 declared leaves, covering the new `structured_refusal` block, the third
  verdict and its precedence, and the per-case boundary encodings;
- **unknown-key refusal**, **list totality**, **canonical renderings**,
  **no-self-validation** and the **C2 derived-authority binding** are unchanged and
  still green;
- `semantically_free_rule_bearing_locations` and
  `unclassified_normative_amendment_fields` both remain **0**.

Two assertions written before this stage changed meaning deliberately: the verdict
vocabulary is no longer exactly two entries, and C2's derived-boundary row no
longer has exactly nine leaves (it has twelve, the three extra recording its
scope-out). Both now assert the new reality, and the two statistical verdicts are
separately asserted unchanged.

---

## 11. Coherence and conformance

All checks run at the amended authority:

```text
Markdown <-> JSON coherence .............. PASS
contract <-> plan conformance ............ PASS   (contract byte-unchanged)
normative-surface totality ............... PASS   236 locations, 0 unclassified
nested semantic-leaf totality ............ PASS   74 leaves, 0 unregistered
list totality ............................ PASS
release authority ........................ PASS
strict JSON parsing ...................... PASS
result-schema authority .................. PASS   (schemas unchanged)
full static preflight .................... PASS
```

The new semantics keys required one rendering change: `SEMANTICS_LABELS` in
`coherence.py` gained a human label per key. Without it the keys did not render and
the JSON/Markdown comparison refused — which is the machinery working, and is how
the omission was caught on the first regeneration attempt.

---

## 12. Implementation status

```text
AUTHORITY AMENDED
RUNTIME REPAIR REQUIRED
F1f-e NOT STARTED
EXECUTION BLOCKED
```

The runtime is **deliberately still behind** this authority, and was verified to be
so after the amendment:

```text
require_endpoint_events   on a RANK_GUARD_FAIL record ..... ACCEPTED
per_field_rejections      399 defined + 1 refusal ......... ENDPOINT_EVENT_MISSING
per_field_rejections      all refused ..................... ENDPOINT_EVENT_MISSING
```

So the terminal report the contract requires is still not produced. That refusal
was **not weakened to make preflight green**: it is recorded as a permanent test
("KNOWN LAG: the runtime still refuses to aggregate a valid structured refusal,
which F1f-e must repair"), sitting beside an assertion that authority now requires
the report. No driver, classifier, result-schema or serialization code was touched.

The per-field terminal counts the amendment requires are **declared** in authority
now; implementing them in the result structures, and any schema version consequence
that follows, belongs to F1f-e.

---

## 13. Identity changes

Recomputed twice from independent clean `git archive` extractions of the work
commit; both agreed.

```text
analysis identity   dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f
                    UNCHANGED -- no analysis-bound scientific module was modified

execution identity  5be9c4ea2ecf0cb9a8a87ed13577ee618e58a21577356d5cd2d9151b16cbb120
                 -> e48ebae7d3ace30546adc67e9a481b2434b128e59594a3275873141ef26e13bd
                    MOVED, as a plan amendment must. NOT FROZEN.

plan json           16b0384d... -> dcf0c575a048ceebfcd3deb261d1a76ff269bfb16178a531b8911b5bdf8808ec
plan markdown       70f81dce... -> 5b76c3095ecbf5bc0f0273f2b83da8fab2d0c51154efc7628031b6445a4fbb18
plan version        1.14.0 -> 1.15.0

contract            91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b  UNCHANGED
contract_version    1.1.0                                                              UNCHANGED
design              e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495  UNCHANGED
foundation          6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507  UNCHANGED
theory baseline     0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa  UNCHANGED
seed map            95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce  UNCHANGED
```

The plan hashes moved because the plan is where the decision lives; the execution
identity moved because both plan renderings and two VALIDATION_MODULES are in its
preimage. Neither was artificially preserved. The seal remains `PRE_DRIVER` with
`expected_execution_identity = None`, so no identity was frozen.

---

## 14. Tests

All fifteen pure/static suites, run at the work commit.

| suite | checks | failures |
|---|---:|---:|
| `test_e1a_v4_terminal_calibration.py` | 538 | 0 |
| `test_e1a_v4_release_authority.py` | 1185 | 0 |
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
CHECKS ...................... 3183        (3022 before this stage, +161)
FAILURES .................... 0
OFFICIAL RNG USE ............ 0
RNG OBJECTS CONSTRUCTED ..... 0
TRAJECTORY COUNT ............ 0
CAMPAIGN JOBS ............... 0
CALIBRATION EXECUTIONS ...... 0
```

The new `F1f-d G5 structured-refusal authority` group contributes **110 checks**
on its own, including the 39-mutation audit. The remainder of the increase is the
existing per-leaf and per-surface loops now covering more registered locations.

`test_e1a_v4_campaign_driver.py` remains a **KNOWN DEFERRED TEST**: trajectory-
bearing through `execute_campaign` -> `execute_replicate` -> `ou_observations`, not
executed, no runtime status claimed.

Two assertions written before this stage were updated to the new reality, and one
assertion in the new group was wrong when first written: it required the word
"Bonferroni" to be absent from the disposition, when the disposition legitimately
names Bonferroni and familywise corrections in order to FORBID them. It now asserts
the prohibition instead.

---

## 15. Execution status

```text
C3/C4 STRUCTURED-REFUSAL AUTHORITY AMENDED PROSPECTIVELY

OFFICIAL RESULTS OBSERVED = NO

F1f-e RUNTIME REPAIR = REQUIRED

FINAL EXECUTION SEAL = NOT FROZEN

EXECUTION AUTHORISED = FALSE

CAMPAIGN = NOT RUN
```

`results/e1a_v4_validation` does not exist. The execution seal is `PRE_DRIVER` with
`expected_execution_identity = None`; the plan's `execution_authorised` is `false`.

F1f-d closes the C3/C4 structured-refusal authority gap and nothing else. The other
F-stage items — F2 negative-stiffness / gamma-sign authority, F3 PRNG choice,
F4 field construction and absolute drag inputs, F5 generator identity, F6 C6
implementation inputs, F7 remaining C8 implementation inputs, F8 diagnostic
aggregator — remain open, and the deferred trajectory-bearing integration
validation remains deferred. A successful F1f-d does not mean seal ready, campaign
ready or execution authorised.

---

C3/C4 STRUCTURED-REFUSAL AUTHORITY AMENDMENT COMMITTED
