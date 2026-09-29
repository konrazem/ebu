# E1a v4 — Release-authority binding

Work commit `b596fe140687190c1898dac373c5d6ea6baeb73d`, tree
`95f32197d0f9e389741ca572688260f9392386a6`, branch `gaussian/stage-a-environment`.
Starting coordinate `ceda2b5a990fc14439b3849c3a3a35a06c4b0c33`.

**Nothing was executed.** No RNG object was constructed, no random number drawn, no
trajectory generated, no calibration sampled, no scientific outcome inspected.

---

## Result

All four reported release-rule escape routes **reproduced** at `ceda2b5a` and are now
**closed**.

| # | probe | at `ceda2b5a` | now |
|---|---|---|---|
| A | C1 complete-pipeline target `0.90 -> 0.80` | **ACCEPTED** | `CONTRACT_RELEASE_TARGET_MISMATCH` |
| B | C1 `R = 300 -> 301` | **ACCEPTED** | `CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH` |
| C | C3 `R = 400 -> 401` | **ACCEPTED** | `CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH` |
| D | C8 `R = 200 -> 201` | **ACCEPTED** | `CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH` |

Probe C needed one more step than the other three before it escaped. A bare
`400 -> 401` was caught by `PLAN_DERIVED_VALUE_MISMATCH`, because section 12a's
derived C3 boundary recomputes from the replicate count. Once the boundary, the
`cp_lower` values and the section-12a Markdown row were recomputed consistently — which
is what a careful auditor would do — the mutation was ACCEPTED. The fully coherent form
is the one carried as a permanent regression, because that is the form the audit is
about.

All four are permanent fixtures in `test_e1a_v4_release_authority.py`, each run through
the **whole** static preflight, and each first checked to confirm that Markdown/JSON
coherence still **passes** on the mutated package. That check is the point: these are
not malformed documents that some earlier gate would have rejected anyway.

### What was actually missing

Not a coherence problem. The missing edge was an authority edge:

```text
FROZEN DESIGN / VALIDATION AUTHORITY
        ↓
CASE RELEASE SPECIFICATION          <- did not exist
        ↓
MACHINE PLAN
        ↓
MARKDOWN PLAN
        ↓
CLASSIFIER / REPORTER
```

`contract_plan.py` bound the **generating** model — fields, stiffnesses, temperatures,
orientations, the relaxation rule, the true-bridge beta. It bound no release rule. The
release rules lived as prose inside each case's `formal_pass_fail_criterion` and in a
seven-column `assurance` table, and nothing compared either to the frozen contract. Two
renderings of a plan agreeing with each other is not authority to amend the contract
above them.

---

## Case release table

| case | R | release endpoint | confidence method | target | derived boundary | mandatory diagnostics | authority source (R) |
|---|---:|---|---|---|---|---|---|
| **C1** | 300 | complete pipeline P1∧P2∧P3∧P4 | CP one-sided 95% **LOWER** | `>= 0.90` | `>= 279/300` | unconditional complete-pipeline success | contract `synthetic_validation_requirements[3]` — EXACT |
| **C2** | 400 | P1 false-rejection rate, per field | CP one-sided 95% **LOWER** (inflation test) | `alpha_geom = 0.005` | `<= 5/400` | coarse one-sided 95% CP **UPPER** vs `0.03`, per field | contract `synthetic_validation_requirements[2]` — EXACT |
| **C3** | 400 | G5 / Block-2 size | CP one-sided 95% **LOWER** (inflation test) | `alpha_2 = 0.001` | `<= 2/400` | G5 delta-method error: measured `sd(g2)` vs `24·A4/n` | contract `synthetic_validation_requirements[2]` — DERIVED |
| **C4** | 2000 | Block-1 achieved size under the surrogate | CP one-sided 95% **LOWER** (inflation test) | `alpha_1 = 0.004` | `<= 13/2000` | operating-quantile discrepancy + full two-sided interval | adopted package — CASE_SPECIFIC |
| **C5** | 400 | P1 rejection rate, per declared cell | CP one-sided 95% **UPPER** | **REPORT ONLY** — no frozen threshold | — | the upper bound in every one of the 12 cells; no cell dropped | adopted package — CASE_SPECIFIC |
| **C6** | 400 | P1 rejection rate, per declared rho | CP one-sided 95% **UPPER** | `<= 0.03` | `<= 6/400` | merge/split decision rate at each rho | contract `synthetic_validation_requirements[2]` — EXACT |
| **C7** | 400 | P2 IUT ∧ all-field P3 | CP one-sided 95% **UPPER** | `<= 0.025` per alternative | `<= 4/400` | — | contract `G2…campaign_criterion.replicates_per_alternative` — EXACT |
| **C8** | 200 | P3-equivalent transformed-beta recovery | CP one-sided 95% **LOWER** | `>= 0.90` | `>= 188/200` | — | contract `G1…campaign_criterion.replicates` — EXACT |

**C5 and C6 had no assurance row at all.** That was a real gap, not named in the audit:
C6 in particular carries a genuine release criterion which *is* the contract's own
`<= 3%` requirement at three declared geometries. Both now have one.

### Where R is, and is not, frozen upstream

An honest split, stated rather than smoothed over:

- **EXACT (C1, C2, C6, C7, C8)** — the frozen authority states the count literally.
- **DERIVED (C3)** — the contract freezes `R = 400` for demonstrating *joint gate* size
  at every declared geometry. P1 is the two-block union declared in
  `endpoints.P1_geometry.procedure`; C3 demonstrates the Block-2 half of that same joint
  gate at the same four declared geometries, so it inherits the same R.
- **CASE_SPECIFIC (C4 = 2000, C5 = 400)** — **no upstream contract value exists.** Design
  section 15 items 5 and 6 freeze *what* must be validated, not how many replicates. Both
  counts were frozen with the package at `475633c` and have never changed. They are
  pinned in `release_authority.py`, whose hash is in `VALIDATION_MODULES` and therefore in
  the execution-identity preimage — so editing one moves the execution identity, which
  editing the plan alone would not do. `CASE_SPECIFIC` is a pin, not a licence: the
  mutation audit below mutates all ten and every one refuses.

---

## C1

Every component is bound, and the boundary is regenerated rather than typed twice.

| component | value | relationship | authority |
|---|---|---|---|
| R | 300 | EXACT | contract `synthetic_validation_requirements[3]` |
| target | 0.90 | EXACT | contract `complete_pipeline.target_true_bridge_success` |
| confidence level | 0.95 | EXACT | `synthetic_validation_requirements[3]` |
| sidedness | one-sided | EXACT | `synthetic_validation_requirements[3]` |
| bound direction | LOWER | EXACT | `synthetic_validation_requirements[3]` |
| estimator / method | Clopper–Pearson | EXACT | **prospective design** section 15 item 4 |
| comparison | `>=` | EXACT | `synthetic_validation_requirements[3]` |
| integer boundary | 279 | **DERIVED** | smallest `k` with `cp_lower(k, 300) >= 0.90` |
| complete-pass denominator | every declared replicate | DERIVED | `complete_pipeline.denominator` |
| structured refusals | count as failures | DERIVED | `complete_pipeline.denominator` |
| complete-pass event | all four fields, then P2∧P3∧P4 | EXACT | `complete_pipeline.complete_pass_event` |
| pooling | FORBIDDEN across the four G3 σψ levels | EXACT | G3 `reporting_rule` |

The interval **method** is the one component the contract JSON does not state: it says
"one-sided 95% LOWER bound", not which interval. The prospective design's section 15
item 4 does say Clopper–Pearson, and the design document's hash is already verified by
`bind_execution`, so the phrase is read out of the frozen document rather than restated
in code. If that line ever changes, `ContractReleaseBindingUnclassified` fires rather
than a regex quietly matching something else.

`279` is not stored as authority anywhere. It is recomputed on every preflight and
compared both to `assurance[0].integer_boundary` and to the integers stated in the
acceptance prose. Changing `279` alone refuses; changing the target and recomputing
`279` consistently also refuses, because the *source* is frozen.

Verified: `cp_lower(279, 300) = 0.9007607390 >= 0.90`, `cp_lower(278, 300) = 0.8969385314 < 0.90`.

---

## C2

Two rules, deliberately kept separate.

```text
PRIMARY RELEASE CLASSIFICATION
    nominal-inflation test against alpha_geom = 0.005.
    Inflation detected iff CP_lower(rejections, 400) > 0.005,
    i.e. 6 or more rejections in any required field -> STATISTICAL_SIZE_FAILURE.
    0-5 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED.
    THIS IS THE RELEASE GATE.

MANDATORY CONTRACT DIAGNOSTIC
    synthetic_validation_requirements[2]:
    one-sided 95% Clopper-Pearson UPPER bound <= 0.03, R = 400,
    reported PER REQUIRED FIELD with an explicit PASS/FAIL.
    NOT the release gate. NOT validation of alpha_geom.
    Absent from a campaign result -> RESULT_SCHEMA_INVALID.
```

### The implication proof

Verified independently, not taken from the audit.

The adopted rule's accepting range is `size_boundary(400, 0.005) = 5`, so it accepts
exactly `k ∈ {0, 1, 2, 3, 4, 5}` — finite and enumerable. Every one:

| k | `cp_upper(k, 400)` | `<= 0.03` |
|---:|---|---|
| 0 | 0.0074613555 | ✓ |
| 1 | 0.0118043045 | ✓ |
| 2 | 0.0156551799 | ✓ |
| 3 | 0.0192692293 | ✓ |
| 4 | 0.0227366936 | ✓ |
| **5** | **0.0261017991** | **✓** |

The auditor's figure at the passing boundary is confirmed: `cp_upper(5, 400) ≈ 0.0261 < 0.03`.

The implication does not rest on that one example. `cp_upper(k, n)` is **strictly
increasing in k** — checked over the whole range `0..400` during this work, and asserted
in the permanent fixture over the accepting range plus one, which is where it is relied
on. So establishing the inequality at the largest accepted count establishes it for
every smaller one:

```text
adopted C2 rule PASSES  =>  k <= 5
                        =>  cp_upper(k, 400) <= cp_upper(5, 400) = 0.0261 < 0.03
                        =>  contract requirement PASSES
```

Classification: **`IMPLIED_STRONGER`**. Confirmed.

`k = 6` also satisfies `<= 0.03` (0.0293901), but already fails the adopted rule, so it
lies outside the range and is irrelevant to the implication.

A fixture that loosens `alpha_geom` to `0.02` breaks the implication and raises
`CONTRACT_RELEASE_IMPLICATION_BROKEN`, so the check discriminates rather than always
passing.

### The wording, corrected

The plan said the contract diagnostic *"may be reported"*. The frozen contract
**requires** it. Changed throughout — the C2 criterion, the superseded-criterion record,
and the runtime `GROSS_INFLATION_LABEL` — to mandatory language naming
`synthetic_validation_requirements[2]`, the `0.03` threshold, and the consequence of
omission. **The statistical rule itself is unchanged.** The stricter nominal-inflation
test remains the release classifier, at exactly the same numbers.

The phrase survives in exactly one place: quoted inside the new section-20 supersession
record, which preserves what was wrong rather than rewriting it. A fixture asserts that
it appears nowhere in any operative section, and exactly once as that quotation.

---

## C3 — C8

**C3.** `R = 400` DERIVED from the joint-gate requirement; target `alpha_2 = 0.001`
EXACT from `endpoints.P1_geometry.alpha_2`; boundary `<= 2/400` derived. The frozen
semantic distinction is bound so a replicate change cannot move it silently:
`primary_release_endpoint = G5_BLOCK_SIZE`,
`block1_role = SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC`, and
`joint_p1_result_changes_C3_release_verdict = false`. Mandatory diagnostic: the G5 block
delta-method error (`synthetic_validation_requirements[7]`).

**C4.** `R = 2000` pinned CASE_SPECIFIC; `alpha_1 = 0.004` EXACT; boundary `<= 13/2000`
derived. The release-bearing rule and the mandatory diagnostics are now separated
explicitly: the binary inflation classification is the gate, while the **operating-quantile
discrepancy** and the **full two-sided interval** are mandatory contract diagnostics
(`synthetic_validation_requirements[4]`) reported regardless of the gate's outcome.

**C5.** `R = 400` pinned CASE_SPECIFIC. The frozen authority states *no threshold*, so
`comparison = REPORT_ONLY` and `target_value = null`, classified accurately rather than
given an invented pass rule. Its criterion is entirely a mandatory reporting requirement:
the one-sided 95% CP upper bound in **every one of the 12 declared cells**, no cell
dropped after inspection. The 3×4 grid itself remains bound by `contract_plan.py`.

**C6.** `R = 400`, `<= 0.03`, one-sided 95% CP UPPER — all four EXACT from
`synthetic_validation_requirements[2]`, because the three declared rho are declared
geometries. Boundary `<= 6/400` derived. The single-field structure is pinned:
`fields_affected` is exactly `["synthetic two-mode field at the declared rho"]` and
`fields_requiring_calibration = 1`, so the one synthetic field cannot become four.
Mandatory diagnostic: the merge/split decision rate at each rho — the **power** half of
`synthetic_validation_requirements[6]`, which the size criterion does not cover.

**C7.** `R = 400` per alternative, `<= 0.025`, one-sided 95% CP UPPER — all EXACT from
`G2_false_bridge_discrimination.campaign_criterion`. Boundary `<= 4/400` derived and
verified against the contract's own recorded `integer_threshold`
(`cp_upper(4,400) = 0.0227367 <= 0.025`, `cp_upper(5,400) = 0.0261018 > 0.025`).
`unit = per_alternative`, `pooling = FORBIDDEN`. The four alternatives remain the
already-authorised case-specific beta overrides, unchanged, still bound by
`contract_plan.py`.

**C8.** `R = 200`, target `>= 0.90`, one-sided 95% CP LOWER — all EXACT from
`G1_blinded_scale_control.campaign_criterion`. Boundary `>= 188/200` derived
(`cp_lower(188,200) = 0.9045986 >= 0.90`, `cp_lower(187,200) = 0.8986430 < 0.90`) and
verified against the contract's recorded `integer_threshold`. The paired scale factors
`[1.07, 0.90]` are bound EXACT to `cases[7].subconditions[0].scale_factors`, and the
paired semantics sentence is pinned **in full** rather than by prefix — a prefix check
would have accepted a sentence that still began `INTENTIONAL:` while saying the
opposite. The all-four-field P3-equivalent branch rule, `delta = 0.05` and
`z = 1.959963985` are bound leaf by leaf with the rest of the G1 disposition.

---

## Binding specification

Machine-derived. Nothing below is hand-counted or asserted.

```text
release-relevant authority items   162
release-relevant contract leaves   119

EXACT                              101
DERIVED                             39
IMPLIED_STRONGER                     1
CASE_SPECIFIC                       10
REPORT_ONLY_MANDATORY                8
NOT_APPLICABLE                      77

unclassified                         0
```

Scope: every leaf of `synthetic_validation_requirements`,
`synthetic_validation_release_criteria`, `complete_pipeline`, `endpoints`,
`mode_resolution` and `refusal_semantics`. Each leaf must be covered by a binding row or
appear in `RELEASE_NOT_APPLICABLE` **with a stated reason**; anything else is counted
`unclassified`, and a non-zero count refuses. `unclassified = 0` is measured against the
actual contract leaves, not declared.

### NOT_APPLICABLE audit

The auditor's specific finding was that C1's own contract requirement had effectively
been classified not-applicable while the plan restated it. `contract_plan.py` carried
`synthetic_validation_requirements[3]` in `NOT_REPEATED_CONTRACT_LEAVES` — along with
`[4]`, `[6]`, `[7]`, `[8]` and `[9]`. All six are removed. A release-bearing leaf now
bound by the new layer is marked **`DELEGATED_TO_RELEASE_AUTHORITY`** in the contract-plan
inventory — naming where it *is* bound, never reading as "not applicable". 18 leaves
carry that marker; the contract-plan layer still measures
`unclassified_execution_relevant = 0` over 206 leaves.

A fixture asserts that no frozen requirement stating a replicate count or a confidence
rule appears in `RELEASE_NOT_APPLICABLE`, and that each of
`synthetic_validation_requirements[2..9]` is bound rather than excused.

The 77 `NOT_APPLICABLE` leaves are the analytic complete-pipeline **budget** (its terms,
supporting probabilities and epistemic labels — the contract itself states
`is_demonstrated_empirical_power = false`), endpoint formulae and taxonomy implemented in
analysis code, and the design-time `theta_cap` split probabilities. None affects a sample
size, a release decision, a confidence rule or a mandatory report. Each carries its own
reason string.

---

## Propagated mutation audit

Generated from the binding specification, not hand-written. For every distinct plan path
the specification binds: mutate the JSON to a valid-looking different value of the same
type, then require release conformance to refuse.

```text
EXACT release bindings tested        101
unexpected passes                      0

CASE_SPECIFIC pins tested             10
unexpected passes                      0

DERIVED values tested                 39
unexpected passes                      0
```

A representative sample additionally goes through the **full stack** with the Markdown
regenerated — `assurance[0].replicates`, `assurance[6].target_value`,
`cases[7].primary_release_endpoint`, `release_authority.complete_pass_event`. For each,
Markdown/JSON coherence is confirmed to **pass** before preflight is required to refuse
with a `CONTRACT_RELEASE_*` code. That ordering is what makes the audit meaningful: it
proves semantic disagreement with frozen authority is caught, not merely that a mangled
document is rejected.

Because the audit is generated, a release binding added later is covered automatically.

---

## Derived rules

No integer threshold is hand-maintained. The derivation rule is chosen mechanically from
`(bound_direction, comparison)`:

| direction | comparison | derivation | used by |
|---|---|---|---|
| LOWER | `>=` | smallest `k` with `cp_lower(k, R) >= target` | C1 → 279, C8 → 188 |
| LOWER | `<=` | largest `k` with `cp_lower(k, R) <= target` | C2 → 5, C3 → 2, C4 → 13 |
| UPPER | `<=` | largest `k` with `cp_upper(k, R) <= target` | C6 → 6, C7 → 4 |
| — | `REPORT_ONLY` | no threshold: the requirement is to REPORT, not to gate | C5 → none |

Also derived and recomputed: the contract's own recorded `integer_threshold` values
(`G1` = 188, `G2` = 4), which the contract itself annotates "verified, not copied" — they
are now actually recomputed rather than trusted, and a contract that recorded a threshold
its own inputs do not derive would refuse.

Tested in both directions, as required:

1. **Inputs fixed, stored derived value altered** → refuses.
2. **Authoritative source altered in a fixture, derived value recomputed consistently** →
   still refuses, because the source is frozen. Checked for C1 and C8.

`derived_boundary` is memoised. That caches a *derivation*, not an authority: the inputs
are re-read from the contract on every call, so a changed input is a cache miss and is
recomputed. (Without it, one preflight took ~20 s; it now takes ~4 s.)

---

## Mandatory reporting

Seven mandatory diagnostics, each derived from the contract requirement that makes it
mandatory, each naming where it must appear in the campaign result:

| diagnostic | case | authority | aggregate key |
|---|---|---|---|
| `C2_CONTRACT_COARSE_UPPER_BOUND` | C2 | `synthetic_validation_requirements[2]` | `contract_diagnostics.per_field` |
| `C3_G5_DELTA_METHOD_ERROR` | C3 | `synthetic_validation_requirements[7]` | `g5_diagnostics` |
| `C4_OPERATING_QUANTILE_DISCREPANCY` | C4 | `synthetic_validation_requirements[4]` | `contract_diagnostics` |
| `C5_PER_CELL_UPPER_BOUND` | C5 | `synthetic_validation_requirements[5]` | `contract_diagnostics.per_cell` |
| `C6_MERGE_SPLIT_DECISION_RATE` | C6 | `synthetic_validation_requirements[6]` | `mode_resolution_behaviour.per_rho` |
| `JOB_STATUS_RECONCILIATION` | campaign | `synthetic_validation_requirements[8]`, `refusal_semantics.reconciliation` | `refusals_by_reason` |
| `UNCONDITIONAL_COMPLETE_PIPELINE_SUCCESS` | C1 | `synthetic_validation_requirements[9]` | `denominator_rule` |

### Schema requirements

Manifest schema **`e1a_v4_validation_manifest/2` → `/3`**, adding `contract_diagnostics`.
Record schema stays at `/2`. The plan's `output_schema.aggregate_fields` and the Markdown
section 9 both carry the change, and `final_campaign_classification.requirements` gains an
eleventh item making the mandatory diagnostics part of the conjunctive release rule
rather than prose.

For C2 the diagnostic must carry, per required field: `rejections`, `replicates`,
`cp_upper`, `threshold`, `direction`, `confidence_level` and `pass`. Every one is
validated by **recomputation** from the raw count the same record carries. Tested with
deterministic fixtures — no campaign was executed:

```text
present and internally consistent          -> schema valid
absent entirely                            -> RESULT_SCHEMA_INVALID
one required field missing                 -> CONTRACT_MANDATORY_DIAGNOSTIC_MISSING
any of the seven keys missing              -> CONTRACT_MANDATORY_DIAGNOSTIC_MISSING
cp_upper inconsistent with its own count   -> CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH
wrong bound DIRECTION (LOWER not UPPER)    -> CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH
wrong confidence LEVEL                     -> CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH
wrong contract threshold                   -> CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH
wrong replicate count                      -> CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH
PASS/FAIL disagreeing with the bound       -> CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH
```

A diagnostic that **fails** the contract threshold is still schema-valid: the schema
requires the figure to be reported, not to pass. Suppressing a real failure is exactly
what this must not encourage.

### Refusal codes

`CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH`, `CONTRACT_RELEASE_TARGET_MISMATCH`,
`CONTRACT_RELEASE_CONFIDENCE_RULE_MISMATCH`, `CONTRACT_RELEASE_BOUND_DIRECTION_MISMATCH`,
`CONTRACT_RELEASE_DERIVED_THRESHOLD_MISMATCH`, `CONTRACT_RELEASE_ENDPOINT_MISMATCH`,
`CONTRACT_RELEASE_BINDING_UNCLASSIFIED`, `CONTRACT_RELEASE_IMPLICATION_BROKEN`,
`CONTRACT_MANDATORY_DIAGNOSTIC_MISSING`, `CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH`,
`RESULT_SCHEMA_INVALID`. Every refusal names the exact canonical authority path, the plan
path, the relationship and both values.

---

## Independent layers

Four permanent fixtures prove the layers are genuinely separate:

```text
Markdown-only release drift (generated region)  -> PLAN_AMBIGUOUS_BLOCK
Markdown-only drift in the DERIVED section 12a  -> PLAN_DERIVED_VALUE_MISMATCH
JSON-only release drift                         -> PLAN_AMBIGUOUS_BLOCK
Markdown + JSON drifting COHERENTLY             -> CONTRACT_RELEASE_REPLICATE_COUNT_MISMATCH
```

The third case is the one that matters, and the fixture asserts that
`require_plan_authority_coherence` **passes** on it before preflight refuses — the drift
really does reach the release layer rather than dying earlier. The second exists because
a generated region is checked for byte-exactness before it is parsed; without it, the
first two would only prove byte equality and not that a drifted value outside a generated
region is caught.

---

## Scientific rules

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Verified by fixture, not by assertion:
`delta_cross = 0.02`, `delta_abs = 0.05`, `z_cross = z_abs = 1.959963985`,
`alpha_geom = 0.005`, `alpha_1 = 0.004`, `alpha_2 = 0.001`, `theta_cap = 5°`,
`rank_tol = 1e-12`, primary `sigma_psi = 0.5°`, complete true-bridge target `0.90`.
Eight cases. Every replicate count and every derived threshold unchanged. The corrected
OU generator untouched (`dt = 0.00012`, `T_total = 240.0`, `n_samples = 2000000`). The
four declared fields, their stiffnesses, temperatures and orientations identical to the
contract. C7's four alternatives and C8's `[1.07, 0.90]` unchanged.

Earlier propagated mutations still refuse: field removal, field duplication, field
parameter drift, relaxation-rule drift, true-bridge beta drift, reference-field drift,
`dt` drift.

---

## Identities

| artifact | sha256 | |
|---|---|---|
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | **unchanged** |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` | **unchanged** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | **unchanged** |
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | **unchanged** |
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | **unchanged** |
| seed map | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | **unchanged** |
| execution seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` | **unchanged** |
| validation plan JSON | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | changed (1.9.0 → **1.10.0**) |
| validation plan Markdown | `3f4715b465da295e21ad99a86390585c9eb7deac44a7810114a88f40aa4bf940` | changed |
| PRE-DRIVER execution identity | `b7c2ed268ebe45daba4df4b6b744a795ab58ad19a2666831584fd5d20a33b7f8` | changed, not forced |

Master seed `13785910525869478477` unchanged. Result record schema
`e1a_v4_validation_result/2` unchanged; manifest schema `e1a_v4_validation_manifest/3`
(was `/2`). `VALIDATION_MODULES` is now 17, adding `release_authority.py`, which is why
the pre-driver execution identity moved. It was not forced anywhere.

---

## Static tests

| suite | checks | failures |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` | 113 | 0 |
| `test_e1a_v4.py` | 122 | 0 |
| `test_e1a_v4_preexec.py` | 103 | 0 |
| `test_e1a_v4_dispositions.py` | 64 | 0 |
| `test_e1a_v4_size_semantics.py` | 79 | 0 |
| `test_e1a_v4_repair.py` | 126 | 0 |
| `test_e1a_v4_calibration_scope.py` | 105 | 0 |
| `test_e1a_v4_case_scope.py` | 113 | 0 |
| `test_e1a_v4_preexec_corrections.py` | 37 | 0 |
| `test_e1a_v4_plan_coherence.py` | 112 | 0 |
| `test_e1a_v4_coherence_hardening.py` | 135 | 0 |
| `test_e1a_v4_generating_model.py` | 112 | 0 |
| `test_e1a_v4_contract_plan.py` | 75 | 0 |
| **`test_e1a_v4_release_authority.py`** | **224** | **0** |
| **total** | **1520** | **0** |

14 suites, **0 nonzero exits**.

Four pre-existing fixtures needed updating for counts my change legitimately moved, and
they are recorded here rather than buried: `VALIDATION_MODULES` 16 → 17,
`final_campaign_classification.requirements` 10 → 11, and two suites that hard-coded the
plan version string `1.9.0`. The version fixtures now read the live plan version — they
test the coherence **gate**, not the current version number, and a version bump should
not look like a gate failure.

---

## Execution state

```text
execution_authorised = false

official campaign driver = ABSENT

final execution seal = NOT FROZEN

RNG OBJECTS = 0

RANDOM DRAWS = 0

TRAJECTORIES = 0

CALIBRATION EXECUTION = NOT RUN

VALIDATION CAMPAIGN = NOT RUN
```

`python3 -m e1a_v4.validation.runner --preflight-only` → PREFLIGHT PASSED, seal state
`PRE_DRIVER`, expected execution identity `None`, `RANDOM DRAWS: 0 TRAJECTORIES: 0`.

`python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation` → exit
2, `EXECUTION REFUSED: [DRIVER_ABSENT]`.

`e1a_v4/validation/campaign_driver.py` does not exist. `results/e1a_v4_validation` does
not exist.

---

## Limitations

Stated plainly, because the pattern matters more than this particular repair.

**This is the fourth escape of the same shape.** The identity table, the generating
model, the contract-plan generating bindings, and now the release rules: each time, an
enumerable surface existed and something release-bearing sat outside it. The answer here
is the same structural one — a totality check with `unclassified = 0` measured, and a
mutation audit generated from the specification rather than hand-written — but that only
closes the surface it is scoped to.

**Where a fifth escape is most likely.** The 77 `NOT_APPLICABLE` release leaves are
judgements. Each carries a reason and none affects a sample size, release decision,
confidence rule or mandatory report *by my reading* — but that reading is the same kind
of judgement that previously classified `generating_model` as JSON-only and C1's own
contract requirement as not-applicable. The contract sections *outside*
`RELEASE_AUTHORITY_SECTIONS` are a second such boundary: `scientific_target`,
`information_separation`, `entropy_semantics`, `false_bridge_controls` and
`hypothetical_uncertainty_scenario` are covered by `contract_plan.py`'s own totality
sweep, but the decision that they carry no release-bearing statistics is mine.

**C4's `R = 2000` and C5's `R = 400` have no upstream authority.** Pinning them in an
identity-bound module is the strongest available guarantee short of amending the frozen
contract, which this task is not authorised to do — but it is a pin against silent
change, not a derivation from first principles. A reviewer who believes those counts
should be frozen in the contract itself should say so; it would be a contract amendment,
not a plan repair.

**The mandatory-diagnostic validation is fixture-tested only.** `require_mandatory_diagnostics`
has never seen a real campaign aggregate, because none exists and none may exist yet. Its
correctness against real result shapes is untested by construction.

---

## Next stage

```text
E1a v4 official campaign-driver implementation
READY FOR FINAL INDEPENDENT RE-AUDIT
NOT STARTED
```

---

RELEASE AUTHORITY COMMITTED
