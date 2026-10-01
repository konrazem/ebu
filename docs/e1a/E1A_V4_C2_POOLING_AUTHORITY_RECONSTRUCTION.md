# E1a v4 — C2 pooling authority: reconstruction

**D6a — C2 POOLING AUTHORITY-TEXT BINDING.**

Authority reconstruction only. No authority file, implementation, driver, classifier
or verifier was changed. Read-only against `HEAD = d43daa5` on
`gaussian/stage-a-environment`.

**Nothing was executed.** No RNG object constructed for scientific purposes, no random
number drawn, no trajectory generated, no calibration sampled, no campaign job run, no
official result observed.

---

## 0. The question

The F1e repair sequence quarantined the nine `derived_boundaries.C2.*` leaves against
byte mutation without validating their science. This task asks whether

```text
C2 pooling across fields      = FORBIDDEN
C2 within-replicate reduction = NONE
```

is **explicitly specified**, **logically derived**, or **unspecified** by authority that
existed *before* the C3/C4 amendment.

---

## 1. Verified C2 semantics

Every value in §2 of the task brief was checked against the repository rather than
assumed. All hold.

| Property | Value | Source | Level |
|---|---|---|---|
| elementary event | P1 rejection for **one declared field** | design §12 complete-pass event: `C = [ AND over 4 fields: … gate_pass ] AND …` | **controlling** (prospective design) |
| R | 400 | contract `synthetic_validation_requirements[2]`; design §15 item 3 | **controlling** |
| nominal size | 0.005 | contract `endpoints.P1_geometry.alpha_geom` | **controlling** |
| size-inflation decision | one-sided 95% CP **LOWER** > 0.005 | plan `assurance[C2]`, bound `DERIVED` from the adopted inflation test | machine plan / case-release spec |
| integer boundary | 0–5 clean, 6+ detected | **recomputed here**: `cp_lower(5,400)=0.0049379342 ≤ 0.005`, `cp_lower(6,400)=0.0065521458 > 0.005` | derived, verified |
| final classifier | four C2 field-level conditions | `classification.classify_campaign`, loop over `c2_rejections_by_field` | implementation |

The contract's own literal C2 clause is the **coarse** rule (CP **upper** ≤ 3%), which
commit `8615405` superseded as the release classifier and retained as a mandatory
diagnostic. Both rules are examined below, because the "at every declared geometry"
quantifier belongs to the contract text and therefore governs both.

---

## 2. Authority inventory

### Controlling — frozen design and contract

| Statement | Location | Meaning | Controlling? |
|---|---|---|---|
| `achieved joint gate size: Clopper-Pearson one-sided 95% UPPER bound <= 3%, R = 400, at every declared geometry` | contract `synthetic_validation_requirements[2]` | the C2 requirement, with a universal quantifier over declared geometries | **controlling** |
| `achieved joint gate size demonstrated at every declared geometry: … R = 400` | design §15 item 3 | same requirement | **controlling** |
| four declared fields with distinct `(k, T, rot)` | contract `fields`; design §3 "The four declared fields" | the declared set | **controlling** |
| `C = [ AND over 4 fields: BranchA_valid & rank_ok & Neff_ok & mode_rule_ok & gate_pass ] AND …` | design §12 | **`gate_pass` is a per-field predicate** | **controlling** |
| `4 × alpha_geom = 0.02000000` — "nominal design allocation" | design §12 budget table | the union bound allocates **four** P1 size events, one per field | **controlling** |
| `reject iff p_min(G1..G4) < alpha_1 OR p(G5) < alpha_2`, `alpha_geom = 0.005` | contract `endpoints.P1_geometry`; design §5 | the gate applied to one field's `H`/`K` | **controlling** |
| P3 "applies to EVERY tested field … passes iff every one of the four fields accepts … Conjunctive over all four fields — an intersection–union test" | design §7 | the programme's established pattern for field-level tests | controlling (P3, diagnostic for C2) |
| G2 item 12: "for **each declared alternative independently** … **Counts are never pooled**" | design §15 item 12 | the design *does* say "never pooled" where it means it | controlling (C7) |

**Superior authority is silent.** `EBU_PHYSICAL_FOUNDATION_CANONICAL.md` and
`EBU_THEORY_BASELINE.md` contain no C2, `alpha_geom`, declared-geometry or joint-gate-size
statement. C2 lives entirely at the design/contract level.

### Case-release specification layer

| Statement | Location | Meaning |
|---|---|---|
| `pooling: ('FORBIDDEN', EXACT, design_contract, synthetic_validation_requirements[2], "'at every declared geometry' requires a per-field figure")` | `release_authority.case_release_specification` | binds `assurance[C2].pooling` |
| `unit: per_field` | same | binds `assurance[C2].unit` |
| `endpoint: P1_FALSE_REJECTION_RATE_PER_FIELD` | same | binds `cases[C2].primary_release_endpoint` |

### Machine plan — C2's own records

| Path | Text | Bound today? |
|---|---|---|
| `cases[C2].scientific_purpose` | "Achieved P1 false-rejection rate **per declared field**…" | **no** (free prose) |
| `cases[C2].formal_pass_fail_criterion` | "**PER FIELD, never pooled**, R = 400, nominal alpha_geom = 0.005…" | **no** (free prose) |
| `cases[C2].primary_release_endpoint` | `P1_FALSE_REJECTION_RATE_PER_FIELD` | yes — EXACT |
| `cases[C2].fields_affected` | the four fields | yes — `plan.py` vs `REQUIRED_C2_FIELDS` |
| `cases[C2].replicate_count` | 400 | yes — EXACT from contract |
| `assurance[C2].unit` | `per_field` | yes — EXACT |
| `assurance[C2].pooling` | `FORBIDDEN` | yes — EXACT from contract |
| `assurance[C2].quantity` | "P1 false-rejection rate, **per field**" | **no** (free prose) |
| `assurance[C2].acceptance_rule` | "… **per field**" | **no** (free prose) |
| `derived_boundaries.C2.*` (9 leaves) | `per_field: true`, `pooling: "FORBIDDEN - every field is reported separately"`, `replicate_reduction: "NONE"`, R/alpha/boundary/CP values | quarantine pin only |
| `final_campaign_classification.requirements[1]` | "2. C2 produces no STATISTICAL_SIZE_FAILURE in any required field" | yes — complete-list pin |

Verified by mutation: contradicting any of the four free-prose locations is **ACCEPTED**
by full static preflight today. That is the same normative-text defect class F1e closed
for C3/C4, still open for C2 — but it is a *verifier* gap, not the scientific question.

---

## 3. Provenance trace

| Commit | Date | What it established |
|---|---|---|
| `475633c` "Prepare E1a v4 synthetic validation" | 2026-09-28 | The **original** C2 case already read `scientific_purpose: "…per declared field"`, `fields_affected` = all four, and `formal_pass_fail_criterion: "Clopper-Pearson one-sided 95% UPPER bound <= 3% at EVERY declared field, **R = 400 each** (max 6 rejections)."` |
| `941674f` "Repair E1a v4 case calibration and seed scopes" | 2026-09-28 | introduced `P1_FALSE_REJECTION_RATE_PER_FIELD`; message states "NO E1a SCIENTIFIC DECISION RULE CHANGED" |
| `8615405` "Freeze E1a v4 size-validation semantics" | 2026-09-28 | introduced `derived_boundaries.C2.pooling` and the "PER FIELD, never pooled" criterion; message states "**C2 is per field and never pooled**" |
| `b596fe1` "Bind E1a v4 release rules to frozen authority" | 2026-09-29 | introduced the case-release-specification binding with reason "'at every declared geometry' requires a per-field figure" |

**Two findings matter.**

First, `475633c` — the original adopted package, predating the size-semantics freeze and
the entire C3/C4 amendment sequence — already rendered the contract clause as **"at EVERY
declared field, R = 400 each"**. The per-field, four-separate-processes structure is
original, not a by-product of the C3/C4 work.

Second, **no commit records a separate human scientific decision adopting "C2 pooling =
FORBIDDEN"**. At every stage it is presented as *following from* the contract clause.
That is consistent with a derivation and inconsistent with an independent adoption.

---

## 4. What "at every declared geometry" requires

The phrase is a **universal quantifier over the declared set**. "Declared geometry" maps
to the four declared fields: the contract declares exactly four `fields`, each with its
own `(k, T, rot)`; the endpoint is named `P1_geometry`; design §12 applies `gate_pass`
once per field; and `E1A_V4_RELEASE_AUTHORITY_REPORT.md` reads it as "the same **four**
declared geometries".

The requirement is therefore

```text
for every declared geometry g :   CP_upper( size at g ) <= 0.03     (contract, coarse)
```

A pooled statistic estimates one aggregate over 4 × 400 = 1600 field-observations. The
aggregate bound does not imply the per-geometry bound, so a pooled figure cannot
establish the quantified property. **Recomputed here, exactly:**

| | per-field reading | pooled reading |
|---|---|---|
| contract coarse rule, CP upper ≤ 0.03 | max **6** rejections per field | max **36** rejections over 1600 |
| release rule, CP lower > 0.005 | clean 0–**5** of 400 | clean 0–**13** of 1600 |

Concrete counterexamples, all rejections concentrated in one declared geometry:

```text
36 rejections in one field, 0 in the other three
    pooled  36/1600  CP_upper = 0.029605   PASS
    field   36/400   CP_upper = 0.117116   FAIL     ( 9.00% = 18x alpha_geom )

13 rejections in one field, 0 in the other three
    pooled  13/1600  CP_lower = 0.00481248  CLEAN
    field   13/400   CP_lower = 0.01932882  STATISTICAL_SIZE_FAILURE
```

Under the pooled reading a package satisfies "achieved joint gate size ≤ 3%" while one
declared geometry sits at 9% — three times the contract's own ceiling and eighteen times
the nominal. **The phrase "at every declared geometry" would then constrain nothing.** A
reading that renders explicit contract language inoperative is not a tenable reading of
controlling authority; under the per-field reading the phrase does exactly the work its
words describe.

This argument is independent of the C3/C4 amendment and uses only contract text plus
arithmetic.

---

## 5. Alternative interpretations

| # | Interpretation | Classification | Reason |
|---|---|---|---|
| **A** | **PER_FIELD, no pooling** — four R = 400 rejection-count processes, each with its own CP bound | **COMPATIBLE WITH AUTHORITY — uniquely** | Produces "achieved joint gate size at g" for every g, so the universal quantifier is satisfied as written. `R = 400` applies at each geometry, matching the original package's "R = 400 each". Matches design §12's per-field `gate_pass` and its `4 × alpha_geom` allocation. |
| **B** | **ANY_FIELD replicate event**, then R = 400 case count | **CONTRADICTS AUTHORITY** | The counted event is "at least one of four fields rejects", whose null is ≈ `1-(1-0.005)^4 ≈ 0.0199` under independence — about 4× `alpha_geom`. Comparing it to 0.005 compares the wrong quantity, and the result is not a size "at" any geometry. Design §12 would also have budgeted it once, not as `4 × alpha_geom`. |
| **C** | **EVERY_FIELD replicate event**, then R = 400 case count | **CONTRADICTS AUTHORITY** | Null ≈ `0.005^4 ≈ 6.25e-10`; the test becomes vacuous and detects no per-geometry inflation. Again not a per-geometry figure, and again inconsistent with the `4 × alpha_geom` allocation. |
| **D** | **Pooled count over 4 × 400** | **CONTRADICTS AUTHORITY** | Demonstrated in §4: passes while one declared geometry is at 18× nominal. Renders "at every declared geometry" inoperative, and makes the effective denominator 1600, contradicting the stated `R = 400`. |
| **E** | **Reference-field-only** | **CONTRADICTS AUTHORITY** | Directly violates the universal quantifier — it demonstrates at one geometry, not every. Also contradicts design §12's `AND over 4 fields` and design §3's declaration of four fields as the tested set. |

Exactly one interpretation survives.

### The distinction the brief warns about

The final classifier contributes **four C2 field-level failure conditions** to the global
conjunction. That is an intersection–union test preserving four separate size
assessments — design §7 uses exactly this construction for P3 and names it as such. It is
**not** a pooled elementary event and must not be described as pooling. Likewise, four
entries in the campaign `failures` list are four field-level conditions, not one pooled
C2 rejection count.

---

## 6. Explicit or derived?

**Not explicit.** No controlling document states "pooling is forbidden" or "no
within-replicate reduction" for C2. The design demonstrably *does* use such wording when
it means it — §15 item 12 says "Counts are never pooled" for C7 — and no equivalent
sentence exists for C2.

**Derived, and forced.** The rule follows by necessity from three controlling facts:

1. contract `synthetic_validation_requirements[2]` quantifies the size requirement **at
   every declared geometry**, with `R = 400`;
2. design §12 makes `gate_pass` a **per-field** predicate inside `AND over 4 fields`, so
   P1's elementary outcome is per field and its achieved size is a per-field quantity;
3. design §12's budget allocates **`4 × alpha_geom`** — four separate per-field P1 size
   events — which is only coherent if four such events exist.

Given (2), the P1 size is a per-field quantity; given (1), it must be demonstrated for
each of the four; given (3), the design's own error budget already counts four. Pooling
or any within-replicate reduction destroys the per-geometry quantity that (1) demands,
as §4 shows numerically. Nothing further is required to fix the rule.

**Disposition: B — DERIVED FROM EXISTING AUTHORITY.** No new human scientific decision is
required.

---

## 7. The quarantined `derived_boundaries.C2.*`

| Question | Answer |
|---|---|
| what it says | `per_field: true`, `pooling: "FORBIDDEN - every field is reported separately"`, `replicate_reduction: "NONE"`, plus R = 400, alpha 0.005, boundary 5 and the two CP values |
| when it first appeared | `8615405` "Freeze E1a v4 size-validation semantics", 2026-09-28 |
| generated from controlling authority? | **No.** Hand-authored plan prose. No renderer produces it; there is no canonical C2 rule object analogous to `FIELD_SIZE_RULES` |
| merely hand-authored plan prose? | The *wording* yes; the *numbers* are recomputable and recompute exactly |
| independently bound elsewhere? | **Yes, partly.** `assurance[C2].pooling = FORBIDDEN` and `assurance[C2].unit = per_field` are bound EXACT to `design_contract / synthetic_validation_requirements[2]`, and `cases[C2].primary_release_endpoint` is bound EXACT. So the *rule* is bound even though this *restatement* of it is not |

The numeric leaves were independently recomputed in this task and are correct:
`size_boundary(400, 0.005) = 5`, `cp_lower(5,400) = 0.0049379342`,
`cp_lower(6,400) = 0.0065521458`.

**Discrepancy to record.** The case-release specification classifies C2's pooling as
relationship `EXACT`, which this repository defines as "the frozen authority states this
value literally". The contract does not state it literally — it states "at every declared
geometry", and the binding's own reason string ("…**requires** a per-field figure") is
derivation language. The relationship should be `DERIVED`. This is a labelling error, not
a scientific one: the value is right and the stated reason is the correct derivation. It
belongs in the D6a implementation step, not here.

---

## 8. Implementation comparison

Inspected as evidence of what software does, never as authority.

| Component | Behaviour | Agrees with authority? |
|---|---|---|
| `classification.classify_campaign` | `# 2. C2 per field, never pooled` — loops `c2_rejections_by_field`, `classify_size(k, 400, 0.005)` per field, appending one failure condition per failing field | **yes** |
| `classification.REQUIRED_C2_FIELDS` | the exact four fields; `classify_campaign` refuses on set mismatch | **yes** |
| `plan.load_plan` | refuses unless `cases[C2].fields_affected` equals `REQUIRED_C2_FIELDS` and the binding's field set matches | **yes** |
| `campaign_driver` | refuses `ENDPOINT_EVENT_REDUCTION_UNDECLARED` for C3/C4 but **not** C2, its comment noting that `derived_boundaries` marks C2 `per_field: true` "and says nothing of the kind for C3 or C4" | **yes** |

No implementation/authority discrepancy was found on the pooling question. The driver's
differential behaviour is itself evidence that C2's per-field structure was already
declared when C3/C4's was not.

---

## 9. Execution state

```text
OFFICIAL RESULTS OBSERVED      = NO
OFFICIAL CAMPAIGN JOBS         = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
FINAL EXECUTION SEAL           = NOT FROZEN  (state PRE_DRIVER)
EXECUTION AUTHORISED           = FALSE
```

Plan version `1.14.0`; `results/` is empty. No authority, implementation or verifier file
was modified by this task.

---

## 10. Disposition

```text
C2 POOLING AUTHORITY:
DERIVED FROM EXISTING AUTHORITY

POOLING:
FORBIDDEN

WITHIN-REPLICATE FIELD REDUCTION:
NONE

NEW HUMAN SCIENTIFIC DECISION REQUIRED:
NO
```

The derivation is given in §6 and rests only on contract
`synthetic_validation_requirements[2]`, design §12 and arithmetic — all of which predate
the C3/C4 amendment. No C3/C4 rule was used as authority for C2.

---

## 11. What remains for the D6a implementation step

Not performed here, and not authorised by this task:

1. Record the derived rule as a canonical C2 object in the case-release-specification
   layer, so C2's normative text can be generated rather than hand-kept — the F1e
   architecture, applied to C2.
2. Bind the four still-free C2 prose locations: `cases[C2].scientific_purpose`,
   `cases[C2].formal_pass_fail_criterion`, `assurance[C2].quantity`,
   `assurance[C2].acceptance_rule`.
3. Replace the byte quarantine on `derived_boundaries.C2.*` with generation from that
   canonical object, and retire `DEFERRED_C2_QUARANTINE`.
4. Correct the relationship label on C2's pooling binding from `EXACT` to `DERIVED`
   (§7), preserving the existing reason string.

Until that step runs, the quarantine remains the only protection on
`derived_boundaries.C2.*`, and the four prose locations remain contradictable.

---

```text
D6a C2 POOLING AUTHORITY RECONSTRUCTION COMPLETE — DISPOSITION B (DERIVED)
```
