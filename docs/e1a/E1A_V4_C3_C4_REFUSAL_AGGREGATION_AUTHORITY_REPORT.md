# E1a v4 — refusal-aware C3/C4 aggregation: authority reconstruction (F1f-b)

**READ-ONLY.** No implementation file, schema, preflight check or scientific
authority document was modified by this task. No RNG object was constructed, no
trajectory generated, no calibration executed and no campaign job run.

```text
STAGE               F1f-b  REFUSAL-AWARE C3/C4 AGGREGATION SEMANTICS
COORDINATE          d1d00dbc9c94233224c55dd6ffdcd4cf9cc84edf
F1f WORK COMMIT     4d4e37d79de2c0ac4dd9eee366674593f81d4b80
QUESTION            what does existing authority require when a planned C3/C4
                    field/replicate is a VALID STRUCTURED REFUSAL and the
                    primary block decision is therefore undefined?
```

---

## 1. Counterexample reproduction

Reproduced with **pure deterministic records only** — hand-written dictionaries and
hand-written `FieldAnalysis` objects passed through the production endpoint
assembly. No RNG, no trajectories, no campaign execution.

### 1.1 The record is accepted, then the aggregation refuses

```text
analysis_status  = RANK_GUARD_FAIL
P1               = False          (P1 FAILS CLOSED)
p1_rejected      = True
block1_rejected  = None           UNDEFINED
g5_rejected      = None           UNDEFINED
```

| step | C3_g5_block | C4_surrogate_validity |
|---|---|---|
| `require_endpoint_events` | **ACCEPTED** | **ACCEPTED** |
| `per_field_rejections`, 399 defined + 1 refusal | `ENDPOINT_EVENT_MISSING` | `ENDPOINT_EVENT_MISSING` |
| `per_field_rejections`, all refused | `ENDPOINT_EVENT_MISSING` | `ENDPOINT_EVENT_MISSING` |

**CURRENT BUG REPRODUCED: YES.** The terminal-event validator accepts the record as
a legitimate structured refusal — correctly, by its own explicit exemption — and the
per-field counter then refuses on the same record.

The refusal is raised inside `campaign_counts_from_records`, which
`execute_campaign` calls **before** `classify_campaign` and before it returns the
campaign result. The durable per-job records have already been committed by that
point, so they survive; what never materialises is the **campaign-level terminal
report**.

### 1.2 Only C3 and C4 are affected

Running the production endpoint assembly on a `RANK_GUARD_FAIL` analysis:

| case | elementary event | value under refusal | |
|---|---|---|---|
| C1 | `complete_pass` | `False` | **TOTAL** — defined |
| C2 | `p1_rejected` | `True` | **TOTAL** — defined |
| C3 | `g5_rejected` | `None` | **PARTIAL** — undefined |
| C4 | `block1_rejected` | `None` | **PARTIAL** — undefined |
| C7 | `false_acceptance` | `False` | **TOTAL** — defined |
| C8 | `scale_recovered` | (own event) | — |

This is the structural root. C1, C2, C7 and C8 score **composite** endpoints that
fail closed, so their Bernoulli outcome exists for every replicate. C3 and C4 score
**sub-block** decisions — `p(G5) < alpha_2` and `p_min(G1..G4) < critical` — which
do not exist when the gate produced no p-values at all. C2 is unaffected precisely
because `p1_rejected` is `True` under refusal.

---

## 2. Authority inventory

Authority order per `AGENTS.md` and `release_authority.authority_rule`:
FROZEN DESIGN / VALIDATION AUTHORITY → CASE RELEASE SPECIFICATION → MACHINE PLAN →
MARKDOWN PLAN → CLASSIFIER / REPORTER.

`EBU_PHYSICAL_FOUNDATION_CANONICAL.md` and `EBU_THEORY_BASELINE.md` contain nothing
governing this question; their "refuse" occurrences concern `Route`/`η` validation.
The controlling documents are the design contract and the prospective design.

| # | statement | source | level | implication for C3/C4 |
|---|---|---|---|---|
| 1 | "jobs declared = jobs completed + jobs refused, with a per-status count; **the report must finish even when every job refuses**" | contract `refusal_semantics.reconciliation`; design §14 | FROZEN CONTRACT + DESIGN | a valid refusal may **never** abort terminal aggregation |
| 2 | "every declared job reconciled by status" | contract `synthetic_validation_requirements[8]` | FROZEN CONTRACT | refusals are reported, per status |
| 3 | "Every declared job emits exactly one record with exactly one terminal status. No missing-key crash, **no silently dropped replicate**, **no conditional-on-survivor rate unless explicitly labelled SECONDARY beside its unconditional counterpart**." | design §14 | DESIGN, campaign-wide | constrains any evaluable-only denominator |
| 4 | "every declared experiment; refusals counted as failures; no conditioning on survivors" | contract `complete_pipeline.denominator` | FROZEN CONTRACT | scoped to **complete-pipeline** success |
| 5 | "complete-pipeline success reported UNCONDITIONALLY" | contract `synthetic_validation_requirements[9]` | FROZEN CONTRACT | scoped to **complete-pipeline** success |
| 6 | `UNCONDITIONAL_COMPLETE_PIPELINE_SUCCESS`, `case_id: "C1_true_bridge_complete"`, `aggregate_key: denominator_rule` | plan `release_authority.mandatory_diagnostics[6]` | MACHINE PLAN | the unconditional-denominator diagnostic is **declared for C1 only** |
| 7 | `rule: "every declared validation replicate"`; `refusals: "structured refusals COUNT AS FAILURES for complete-pipeline success"`; `conditional_diagnostics: "permitted only when explicitly labelled SECONDARY, reported beside the unconditional figure"` | plan `complete_pass_denominator` | MACHINE PLAN | key name and wording both scope it to complete-pipeline |
| 8 | "10. structured refusals counted exactly per the already-frozen unconditional denominator rule" | plan `final_campaign_classification.requirements[9]` | MACHINE PLAN | routes refusal accounting through the **C1-scoped** rule |
| 9 | `non_estimated_field: "FAILS P3 — fail-closed, no conditioning on surviving fields"` | contract `endpoints.P3_absolute` | FROZEN CONTRACT | the **only** explicit contract treatment of a non-estimated quantity; scoped to P3 |
| 10 | `P1_geometry` carries **no** `non_estimated_field` key | contract `endpoints.P1_geometry` | FROZEN CONTRACT | the contract did not state the analogous rule for P1 or its blocks |
| 11 | budget terms `4 × alpha_geom = 0.02` and `4 × rank/N_eff refusal = 0.00000000` listed **separately** | contract `complete_pipeline.budget_terms`; design §12 | FROZEN CONTRACT + DESIGN | the design treats refusal and geometry rejection as **distinct failure events** |
| 12 | `C = [AND over 4 fields: BranchA_valid & rank_ok & Neff_ok & mode_rule_ok & gate_pass] AND P2 AND P3 AND P4` | contract `complete_pipeline.complete_pass_event`; design §12 | FROZEN CONTRACT | `rank_ok` is an explicit conjunct — see §5 |
| 13 | statuses include `BETA_NOT_ESTIMATED`, `COMPARISON_NOT_EVALUABLE` | contract `refusal_semantics.statuses`; design §14 | FROZEN CONTRACT | a NOT_EVALUABLE concept exists in the **job-status** vocabulary |
| 14 | `verdicts: {on_detection: STATISTICAL_SIZE_FAILURE, otherwise: NO_SIGNIFICANT_SIZE_INFLATION_DETECTED}`, block `status: "FROZEN PROSPECTIVELY"` | plan `size_validation_semantics` | MACHINE PLAN | the size verdict vocabulary is **binary and frozen** |
| 15 | "STATISTICAL SIZE INFLATION is detected iff `CP_lower(rejections, R) > nominal alpha`" | plan `size_validation_semantics.detector` | MACHINE PLAN | a total function of (rejections, R); `otherwise` catches everything else |
| 16 | "a case is clean only when all 4 are clean, NO required condition may fail" | plan `final_campaign_classification.rule` | MACHINE PLAN | binary per condition; no third state |
| 17 | `failure_classifications` includes `STRUCTURED_REFUSAL_EXCESS` and `VALIDATION_INCONCLUSIVE` | plan; design | MACHINE PLAN | names exist; **no trigger condition is declared anywhere** |
| 18 | C2 purpose: "…covering G1-G5, the two-block combination, mode resolution **and structured refusals**" | plan `cases[C2].scientific_purpose` | MACHINE PLAN | C2's estimand **explicitly includes** refusals |
| 19 | C3 and C4 case records mention refusal **nowhere** | plan `cases[C3]`, `cases[C4]` | MACHINE PLAN | the equivalent sentence was not written for them |
| 20 | prohibited after execution: "replicate definitions", "case definitions", "acceptance rules", "complete-pass denominator" | plan `no_post_outcome_tuning` | MACHINE PLAN | whatever is decided must be decided **before** execution |

---

## 3. Denominator analysis

**What `R` means is declared for complete-pipeline success and for nothing else.**

Every occurrence of an unconditional "every declared … refusals count as failures"
denominator rule in authority is scoped to complete-pipeline success:

- the contract states it inside the `complete_pipeline` block (row 4);
- the contract's requirement [9] names complete-pipeline success (row 5);
- the plan's key is literally `complete_pass_denominator` and its `refusals` value
  ends "**for complete-pipeline success**" (row 7);
- the mandatory diagnostic that carries the `denominator_rule` aggregate key is
  bound to `case_id: "C1_true_bridge_complete"` (row 6);
- the final-classification requirement that mentions refusals defers to "the
  already-frozen unconditional denominator rule" — singular, i.e. that one (row 8).

For C3 and C4, authority states `R = 400 per field` and `R = 2000 per field` and a
`replicate_count`, but **never says whether `R` is the planned count or the
evaluable count**. Four readings — planned, evaluable, attempted, non-refused —
are all consistent with the words actually written in the C3/C4 records.

Two general constraints do apply, and they are campaign-wide, not C1-scoped:

- **no silently dropped replicate** (row 3);
- **a conditional-on-survivor rate is permitted only when explicitly labelled
  SECONDARY beside its unconditional counterpart** (rows 3 and 7).

The second is decisive for candidate C: an evaluable-only C3/C4 size rate is a
survivor-conditioned rate, so it may not be the primary release figure, and it may
only be reported at all **beside an unconditional counterpart** — which is exactly
the quantity that does not exist when the block decision is undefined. The
repository already carries the slot for such a figure
(`aggregate_skeleton`'s `conditional_diagnostic_secondary`, labelled "SECONDARY,
conditional on estimable runs only"), which is evidence of the intended shape but
is implementation, not authority.

---

## 4. Refusal-status analysis

Three objects, kept separate as the brief requires.

**A. Scientific endpoint decision.** For C3 the estimand is the probability that
`p(G5) < alpha_2`; for C4, that `p_min(G1..G4) < critical_p_min`. Under a rank-guard
failure the gate produced no p-values, so neither predicate has a truth value. The
observation is **not** a Bernoulli realisation of the event being measured. It is
the third thing the brief names: *no defined Bernoulli outcome*, as distinct from a
defined 0 and a defined 1.

**B. Structured refusal status.** Fully specified. `RANK_GUARD_FAIL` maps to the
contract's `REFUSED_ACCESSIBLE_SPACE` ("rank guard failed on S (or S_T),
rank_tol = 1e-12") under the `BETA_NOT_ESTIMATED` umbrella. It is a valid terminal
status, it must be recorded, and it must be reconciled per status.

**C. Final campaign reporting.** Fully specified, and the strongest statement in the
whole inventory: the report **must finish even when every job refuses** (row 1),
stated identically in the frozen contract and in the prospective design, and backed
by contract requirement [8].

**A valid structured refusal may therefore never abort terminal aggregation.** The
current implementation does exactly that, and on this point authority is explicit:
this part of the defect needs no new decision.

---

## 5. C1 interaction

`complete_pass_event` names `rank_ok` as an explicit conjunct (row 12), so a
rank-guard failure does set `complete_pass = False` — confirmed by reproduction —
and C1's unconditional denominator counts it as a failure. The complete-pipeline
mechanism genuinely does record structured refusal as pipeline failure.

**But C1 cannot absorb a C3 or C4 refusal.** The cases are disjoint job sets:

```text
planned jobs, by case (one job = case / subcondition / replicate / field)

  C1_true_bridge_complete      4800      300 replicates
  C2_geometry_false_rejection  6400      400 replicates
  C3_g5_block                  6400      400 replicates
  C4_surrogate_validity        8000     2000 replicates
  ...
  TOTAL                       53200

  C1 job ids shared with C3: 0
```

A refusal occurring inside one of C3's 400 replicates is **not** one of C1's 300
experiments and does not enter C1's complete-pass rate at all. It is captured by the
campaign-wide `JOB_STATUS_RECONCILIATION` diagnostic (`refusals_by_reason`) and
nowhere else.

This matters because it removes the easiest reading of candidate E. "Leave C3/C4
statistically non-evaluable and let C1 record the pipeline failure" does **not**
follow: for a refusal inside a C3 replicate, C1 records nothing.

---

## 6. Size rejection is not pipeline failure

Authority does make the distinction the brief asks about, in three places:

- `two_questions` separates **A, complete practical performance** (C1) from
  **B, component size inflation** (C2/C3/C4), each "a COMPONENT size test and never
  a familywise or pooled test";
- `independent_facts_rule`: complete-pipeline achievement and component size
  cleanliness "are REPORTED SEPARATELY and never collapsed";
- `failure_classifications` names `STATISTICAL_SIZE_FAILURE` and
  `STRUCTURED_REFUSAL_EXCESS` as **different** classifications.

So "the statistical test produced no rejection decision" and "the pipeline failed to
establish the required evidence" are recognised as different facts. What authority
does **not** supply is the rule that converts the second into a release outcome for
C3 or C4: `STRUCTURED_REFUSAL_EXCESS` appears in the failure vocabulary of the
contract, the design and the plan, and **no document anywhere declares the condition
that triggers it**. (`refusal_accounting` appears nowhere in `docs/`; it exists only
as an implementation input.)

Statistically, the detector `CP_lower(rejections, R) > nominal alpha` presupposes
`R` Bernoulli trials of the event being measured. An undefined outcome is not such a
trial. Converting it silently into a 0 or a 1 changes the estimand, and the frozen
`verdicts.otherwise` branch means any count that is not a detection is reported as
`NO_SIGNIFICANT_SIZE_INFLATION_DETECTED` — a positive-sounding statement that would
then rest partly on evidence that was never obtained.

---

## 7. Partial refusal: 399 defined + 1 refusal

The arithmetic, computed here and not copied:

**C3** — `alpha_2 = 0.001`, boundary 2 of 400. Scenario: 2 real G5 rejections,
1 structured refusal, 397 clean.

| semantics | k | n | `CP_lower` | verdict |
|---|---:|---:|---|---|
| A refusal counted as rejection | 3 | 400 | 0.00204726 | **STATISTICAL_SIZE_FAILURE** |
| B refusal counted as clean | 2 | 400 | 0.00088912 | clean |
| C refusal dropped from R | 2 | 399 | 0.00089135 | clean |
| D/E defined events only | 2 | 400 | 0.00088912 | clean |

**C4** — `alpha_1 = 0.004`, boundary 13 of 2000. Scenario: 13 real Block-1
rejections, 1 structured refusal, 1986 clean.

| semantics | k | n | `CP_lower` | verdict |
|---|---:|---:|---|---|
| A refusal counted as rejection | 14 | 2000 | 0.00423678 | **STATISTICAL_SIZE_FAILURE** |
| B refusal counted as clean | 13 | 2000 | 0.00384894 | clean |
| C refusal dropped from R | 13 | 1999 | 0.00385087 | clean |
| D/E defined events only | 13 | 2000 | 0.00384894 | clean |

**One structured refusal flips the release verdict of a required field in both
cases.** The candidate semantics are not notational variants of each other; they
produce different release decisions on the same data. This is a scientific decision,
not an implementation detail.

Note also that B, C and D/E agree numerically here while asserting different things:
B and C assert a clean field, D/E assert that the *defined* events were clean and
that one observation was never obtained. §6 is why that difference cannot be waved
away.

---

## 8. All-refused campaign

Authority is explicit that the report must still be produced (rows 1, 2). What it
does **not** supply is the scientific result that report should carry for an
all-refused C3 or C4 field.

- `size_validation_semantics.verdicts` declares exactly two outcomes and the block
  is `"FROZEN PROSPECTIVELY, before any random outcome exists"` (row 14). There is
  no `NOT_EVALUABLE`, no `REFUSED`, no `VALIDATION_INCOMPLETE` in the **size verdict**
  vocabulary.
- `COMPARISON_NOT_EVALUABLE` and `BETA_NOT_ESTIMATED` do exist (row 13) — but in the
  **job-status** vocabulary, for a record, not as a field-level size verdict.
- `VALIDATION_INCONCLUSIVE` exists in `failure_classifications` (row 17) with no
  declared trigger.
- Applying the frozen detector literally to 0 rejections out of 400 yields
  `CP_lower(0, 400) = 0 < 0.001` → `otherwise` → `NO_SIGNIFICANT_SIZE_INFLATION_DETECTED`.
  A campaign in which **every** C3 replicate refused would therefore report its G5
  block as showing no significant size inflation, on zero observations. That is
  plainly not intended, and it is what the frozen binary detector mechanically
  produces if refusals are simply excluded from the count with `R` preserved.

That last point is the sharpest form of the gap: the frozen vocabulary has no way to
say "this field was not evaluated".

---

## 9. Candidate-semantics comparison

Classified against authority, not by preference.

### A — count refusal as rejection (`None → TRUE`)

```text
UNSPECIFIED (COMPATIBLE). NOT REQUIRED, NOT FORBIDDEN.
```

*For:* the only explicit contract treatment of a non-estimated quantity resolves it
fail-closed (`non_estimated_field: "FAILS P3"`, row 9); C2's estimand explicitly
covers structured refusals (row 18) and `p1_rejected` is `True` under refusal;
counting it preserves both the frozen binary verdict vocabulary and the declared
denominator, and is conservative for the gate.

*Against:* the design's own union budget lists `4 × rank/N_eff refusal` as a term
**separate** from `4 × alpha_geom` (row 11), i.e. the design does not fold refusal
into the geometry-rejection term; `STATISTICAL_SIZE_FAILURE` and
`STRUCTURED_REFUSAL_EXCESS` are distinct classifications (row 17); and the contract
pointedly did **not** give `P1_geometry` the `non_estimated_field` key it gave P3
(row 10). A single refusal would be reported as evidence that the G5 block's size is
inflated, which is not what happened.

Note also that under A the same non-event is a rejection for C2 (via `p1_rejected`),
for C3 (via G5) and for C4 (via Block-1) simultaneously — one absent observation
counted as three rejections of three different statistics.

### B — count refusal as non-rejection (`None → FALSE`)

```text
FORBIDDEN.
```

It contradicts the only explicit contract precedent for a non-estimated quantity
(row 9), which resolves against the favourable reading, and it manufactures a clean
Bernoulli 0 from absent evidence — the most favourable possible reading of missing
data, in a repository whose stated posture throughout is fail-closed. It is also
irreconcilable with `interpretation.does_not_mean`, since the resulting
`NO_SIGNIFICANT_SIZE_INFLATION_DETECTED` would rest partly on observations never
made. (The prohibition is by precedent and posture; no sentence names C3/C4.)

### C — remove refusal from the statistical denominator (399 of 400)

```text
FORBIDDEN AS THE PRIMARY RELEASE RATE.
COMPATIBLE ONLY as an explicitly labelled SECONDARY figure beside an
unconditional counterpart — which does not exist here.
```

Direct application of row 3 and row 7: "no conditional-on-survivor rate unless
explicitly labelled SECONDARY beside its unconditional counterpart". C alone cannot
satisfy that, because the unconditional counterpart it must sit beside is precisely
the quantity that is undefined.

### D — preserve declared denominator, field verdict `NOT_EVALUABLE`

```text
UNSPECIFIED. Compatible with the reporting authority; requires a verdict
frozen authority does not declare.
```

Compatible with rows 1, 2, 3 and with preserving `R`. But it needs a **third
field-level size verdict**, and `size_validation_semantics.verdicts` declares
exactly two and is frozen prospectively (row 14), while
`final_campaign_classification.rule` is binary per condition — "clean" or "fail",
with no third state (row 16). Adopting D means extending a frozen vocabulary.

### E — refusal excluded from the count; release blocked on incomplete evidence

```text
UNSPECIFIED. The separation it relies on is authorised; its trigger is not.
```

The distinction it rests on is real and authorised (§6). But the mechanism that
blocks release is not declared: `STRUCTURED_REFUSAL_EXCESS` has no trigger condition
anywhere in authority, `requirements[9]` routes refusal accounting through the
C1-scoped unconditional denominator rule, and §5 shows C1 does not see C3/C4
refusals at all. Without a declared trigger, E degenerates into B — the count is
clean and nothing fails.

### F — any other mechanism required by current authority

None found. The search covered the physical foundation, the theory baseline, the
prospective design, the design contract, both plan renderings and every
`refusal` / `denominator` / `evaluable` / `not estimated` / `fail closed`
occurrence in `docs/`.

---

## 10. What IS settled

These require **no** new scientific decision and should be treated as binding on the
eventual repair:

1. **The terminal campaign report must be produced**, even if every planned job
   refuses. A valid structured refusal may never abort terminal aggregation. The
   current `ENDPOINT_EVENT_MISSING` abort is contrary to explicit authority.
2. **No replicate may be silently dropped**; every declared job carries exactly one
   terminal status, and `jobs declared = jobs completed + jobs refused` must
   reconcile with a per-status count.
3. **A survivor-conditioned size rate may never be the primary figure**, and may be
   reported only when explicitly labelled SECONDARY beside an unconditional
   counterpart.
4. **A refusal may not be scored as a clean non-rejection** (candidate B).
5. **C2 is unaffected** and must not be changed: its elementary event is `p1_rejected`,
   which is defined under refusal, and its declared estimand explicitly covers
   structured refusals.
6. **The decision must be made before execution.** `no_post_outcome_tuning` prohibits
   changing replicate definitions, case definitions and acceptance rules after
   execution.

## 11. What is NOT settled

Candidates **A**, **D** and **E** remain materially different and all remain
compatible with frozen authority. §7 shows they produce different release verdicts
on identical data, so the choice cannot be deferred to implementation.

---

## 12. Final disposition

```text
REFUSAL-AWARE C3/C4 AGGREGATION:
UNSPECIFIED

NEW HUMAN SCIENTIFIC DECISION REQUIRED:
YES
```

### The smallest exact question the author must decide

> For **C3** and **C4**, when a planned field/replicate terminates in a valid
> structured refusal and the case's primary block decision — `p(G5) < alpha_2` for
> C3, `p_min(G1..G4) < critical_p_min` for C4 — is therefore **undefined**:
>
> **(i)** does that observation contribute a **rejection** to that field's binomial
> count, leaving `R` at its declared value and the frozen two-verdict vocabulary
> intact (candidate A)?
>
> **or (ii)** is the field's size assessment **incomplete**, with the rejection count
> formed only from defined events — and if so, **(ii-a)** what verdict does that
> field carry, given that `size_validation_semantics.verdicts` declares exactly two
> and is frozen, and **(ii-b)** by what declared rule does the campaign fail, given
> that `STRUCTURED_REFUSAL_EXCESS` has no trigger condition in authority and C1 does
> not see C3/C4 refusals?

Answering (i) settles the matter alone. Answering (ii) requires both sub-answers,
because without (ii-a) the frozen `otherwise` branch reports a clean field and
without (ii-b) nothing blocks release.

**No rule is chosen here.** Per the brief, this task returns the authority result
only.

---

## 13. Implementation gap, for the record

Inspected as **evidence, not authority**:

- `require_endpoint_events` grants an explicit exemption for `block1_rejected` and
  `g5_rejected` when `analysis_status != "ESTIMATED"` — correct, and it is what makes
  the refused record a valid terminal record.
- `field_event_count` raises `EndpointEventMissing` on any `None`, with no
  corresponding exemption.
- `per_field_rejections` calls it for all three per-field size cases.
- `campaign_counts_from_records` calls that, and `execute_campaign` calls it before
  `classify_campaign` and before returning the campaign result.

The two guards are individually defensible and mutually inconsistent. No repair is
proposed here; the implementation stage follows the authority decision.

## 14. Execution status

```text
OFFICIAL RESULTS = NONE
OFFICIAL CAMPAIGN JOBS = 0
OFFICIAL TRAJECTORIES = 0
FINAL EXECUTION SEAL = NOT FROZEN
EXECUTION AUTHORISED = FALSE
```

`results/e1a_v4_validation` does not exist. The execution seal is `PRE_DRIVER` with
`expected_execution_identity = None`; the plan's `execution_authorised` is `false`.
Plan version 1.14.0; analysis identity `dd2ed732…`; no authority file changed.

```text
F1f:
NOT YET CLEARED
```
