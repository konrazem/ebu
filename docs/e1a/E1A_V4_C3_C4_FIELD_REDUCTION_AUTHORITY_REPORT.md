# E1a v4 — C3/C4 field-to-replicate reduction: authority reconstruction

Authority reconstruction only. No implementation, no scientific amendment, no
execution. Read-only against `HEAD = d4f5878` on `gaussian/stage-a-environment`.

---

## Current question

C3 and C4 each declare **four** `fields_affected`, and the two-block P1 gate
decides **per field**: `p1_geometry(analysis: FieldAnalysis, ...)` takes one
field's analysis and returns that field's decision, rejecting iff
`p_min(G1..G4) < alpha_1` **or** `p(G5) < alpha_2`. So one replicate of C3
produces four Block-2 (G5) decisions, and one replicate of C4 produces four
Block-1 decisions.

Both cases are scored against a **replicate** denominator:

```text
C3   R = 400     nominal alpha_2 = 0.001    SIZE_FAILURE iff CP_lower(k, 400)  > 0.001   -> 3+
C4   R = 2000    nominal alpha_1 = 0.004    SIZE_FAILURE iff CP_lower(k, 2000) > 0.004   -> 14+
```

Four field decisions must therefore become the one Bernoulli event each
denominator counts. **No frozen document states how.** The frozen output schema
confirms the asymmetry: `G5` and `P1` are `per_record_fields` carried beside a
`field_id`, and there is no replicate-level G5 or Block-1 field anywhere in the
schema. The quantity the denominators count does not exist in the record; it has
to be computed, and the rule for computing it is absent.

This is not a formatting question. The choice changes the measured size, so it is
a scientific decision.

---

## C3 authority history

| # | source | statement | classification |
|---|---|---|---|
| 1 | design §15 item 8 — the authority C3 itself cites | "G5 block delta-method error quantified" | **EXPLICIT FROZEN AUTHORITY**, but it specifies no size test, no replicate count, no alpha and no field structure |
| 2 | `475633c` original C3 | criterion was "CP one-sided 95% UPPER bound on the block-2 rejection rate <= 3%, R = 400"; `fields_affected` already four | **HISTORICAL / SUPERSEDED**; still no reduction rule |
| 3 | `8615405` "Freeze E1a v4 size-validation semantics" | introduced the present inflation test and boundaries; states "**C2 is per field and never pooled**" and says nothing of the kind for C3 | **EXPLICIT FROZEN AUTHORITY** for the boundary; **NOT SPECIFIED** for the reduction |
| 4 | `size_validation_semantics.derived_boundaries.C2` | `per_field: true`, `pooling: "FORBIDDEN"` | **EXPLICIT** — and the C3 entry has **no `per_field` key at all** |
| 5 | contract `endpoints.P1_geometry` | `alpha_2 = 0.001` is Block-2's allocation inside the **per-field** two-block union rule | **EXPLICIT FROZEN AUTHORITY** |
| 6 | contract `complete_pipeline.budget_terms.4x_alpha_geom = 0.02` | the design's own union budget charges **four** separate per-field P1 tests at `alpha_geom` each | **EXPLICIT FROZEN AUTHORITY** that P1 is per field |
| 7 | plan `output_schema.per_record_fields` | `G5`, `P1`, `beta_hat` recorded per record, each record carrying `field_id`; no replicate-level G5 field exists | **EXPLICIT FROZEN AUTHORITY** on structure |
| 8 | `c3_semantics` | `primary_release_endpoint = G5_BLOCK_SIZE`; `block1_role = SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC`; forbids any new C3 threshold based on Block 1 or the joint P1 result | **EXPLICIT FROZEN AUTHORITY** — preserved below |
| 9 | `assurance[C3].unit = "campaign"`, `pooling = "NOT_APPLICABLE"` | introduced only at `b596fe1`, the most recent plan commit | **PACKAGE ASSERTION** — see below |
| 10 | `release_authority.CaseRelease("C3_g5_block", 2, "campaign", ...)` | `unit` is the one release-rule component carrying **no** `(value, relationship, source, path, reason)` authority tuple; `pooling` carries relationship `NOT_APPLICABLE` with reason "C3 reports one campaign-level G5 rejection count", citing path `synthetic_validation_requirements[2]` | **AMBIGUOUS / restatement** — the reason asserts the conclusion rather than citing a source |

### The internal tension in C3

C3's `replicates`, `method` and `sided` are marked `DERIVED` from contract
`synthetic_validation_requirements[2]` with this stated reason:

> "P1 is the two-block union declared in `endpoints.P1_geometry.procedure`; this
> case demonstrates one block of that same joint gate **at the same declared
> geometries**, so it inherits the frozen R of the joint-gate size requirement"

The clause it inherits from reads "achieved joint gate size … R = 400, **at every
declared geometry**". So C3's `R = 400` is justified by treating 400 as a
**per-geometry** replicate count — exactly as for C2.

The **same** contract path `[2]` is then cited for `pooling = NOT_APPLICABLE`,
"C3 reports one campaign-level G5 rejection count".

Both cannot be straightforward readings of the same clause. Either `R = 400` is
per-geometry (and C3 is per-field, contradicting `unit: campaign`), or C3 is
campaign-level (and its `R` does not in fact inherit from a per-geometry
requirement). **This is an unresolved internal inconsistency in the package, not
a resolved rule.**

---

## C4 authority history

| # | source | statement | classification |
|---|---|---|---|
| 1 | design §15 item 5 — the authority C4 cites | "surrogate calibration law validated at the operating quantile against directly generated trajectories" | **EXPLICIT FROZEN AUTHORITY**, specifying no size test, no replicate count, no alpha, no field structure |
| 2 | `475633c` original C4 | "report the achieved Block-1 rate with a CP 95% two-sided interval over R = 2000 … Discrepancy is REPORTED and classified"; `fields_affected` already four | **HISTORICAL** context; no reduction rule |
| 3 | `8615405` | added the binary inflation classification, `R = 2000`, `alpha_1 = 0.004`, boundary 13/14 | **EXPLICIT** for the boundary; silent on the reduction |
| 4 | `release_authority` C4 `replicates` | `_c(2000, CASE_SPECIFIC, PACKAGE, ...)` with `PACKAGE_R_REASON`: "the frozen authority states WHAT must be validated but **no replicate count**; this count was frozen with the adopted package at `475633c`" | **PACKAGE-LEVEL**, explicitly *not* contract authority |
| 5 | contract `endpoints.P1_geometry.alpha_1 = 0.004` | Block-1's allocation inside the per-field two-block rule | **EXPLICIT FROZEN AUTHORITY** |
| 6 | `assurance[C4].unit = "campaign"`, `pooling = "NOT_APPLICABLE"`; `CaseRelease` reason "C4 reports one campaign-level Block-1 rejection count" | introduced at `b596fe1` | **PACKAGE ASSERTION / restatement** |

C4 is weaker than C3 on every axis. Its replicate count is not contract
authority at all, and unlike C3 it does **not** inherit any "at the same declared
geometries" framing — so the one piece of evidence that pulls C3 toward per-field
does not exist for C4.

---

## Candidate rules

Assessed independently for each case. None is stated by any frozen document.

| candidate | meaning | authority found |
|---|---|---|
| **A. Reference field only** | count `theta0_circular`'s decision; other fields reported but not counted | **NONE.** `reference_field_id = theta0_circular` exists in the contract but anchors the **P2 cross-field ratio**. Nothing in C3, C4, the assurance rows or the release specification ties either case to it. |
| **B. Any field rejects** | union over the four fields | **NONE.** Named in the driver's refusal text as a guess, never in authority. |
| **C. Every field rejects** | intersection over the four fields | **NONE.** No document connects C3/C4 to an intersection-union-test reading. |
| **D. Per field, no reduction** | four independent size tests, as C2 | **PARTIAL and contradicted.** Supported by C3's own `R` derivation ("at the same declared geometries"), by the per-field structure of `P1`/`alpha_1`/`alpha_2`, and by the record schema. Contradicted by `assurance.unit = "campaign"`. |
| **E. Another explicitly authorised rule** | — | **NONE found.** |

---

## Original size derivations

What event probability do the frozen boundaries assume?

The boundaries themselves are **event-agnostic**: `size_boundary(R, alpha)` is the
largest `k` with `CP_lower(k, R) <= alpha`, a function of `R` and `alpha` only.
Recomputed here and matching the frozen values:

```text
C2  cp_lower(5, 400)    = 0.0049379342 <= 0.005    cp_lower(6, 400)    = 0.0065521458 >  0.005
C3  cp_lower(2, 400)    = 0.0008891209 <= 0.001    cp_lower(3, 400)    = 0.0020472587 >  0.001
C4  cp_lower(13, 2000)  = 0.0038489425 <= 0.004    cp_lower(14, 2000)  = 0.0042367805 >  0.004
```

So the derivation tells us nothing directly about the reduction. What it *does*
fix is the **comparison target**: `alpha_2` and `alpha_1` are, by the contract's
own `endpoints.P1_geometry`, the nominal levels of Block-2 and Block-1 **within
one field's** two-block gate. A **necessary derivation** follows:

> the Bernoulli event counted must be one whose null probability is the
> **single-field** block rate, or the test is comparing a rate against a nominal
> level that is not its own.

This constrains the *rate*. It does not by itself say which field, or whether
there is one test or four.

---

## C2 comparison

C2's per-field semantics are **explicit**, not inferred. Its authority is contract
`synthetic_validation_requirements[2]`: "achieved joint gate size … R = 400, **at
every declared geometry**", and `release_authority` records C2's `pooling =
FORBIDDEN` with the reason "'at every declared geometry' requires a per-field
figure".

Does C2's wording illuminate C3/C4? Only partly, and the honest answer is neither
of the two options §9 offers:

- It is **not** simply "an omission in wording" of a parallel requirement, because
  C3's and C4's cited authority items (design §15 items 8 and 5) are different in
  kind. Item 8 asks for a delta-method error to be *quantified*; item 5 asks for
  the surrogate law to be *validated at the operating quantile*. Neither ever
  expressed a size demonstration across geometries, so there was no per-geometry
  phrase to omit.
- It is **not** demonstrated to be "intentionally different semantics" either. No
  document says C3/C4 are deliberately campaign-level; the `unit: campaign`
  assertion appears only at `b596fe1`, without an authority tuple, and for C3 it
  sits against that case's own contract-derived `R`.

The correct reading of the evidence is that the C3/C4 size tests were **added** by
the V4 correction at `8615405`, which specified `R`, `alpha` and the boundary, and
**never addressed field structure at all** — for either case.

---

## Authority versus inference

| classification | items |
|---|---|
| **EXPLICIT FROZEN AUTHORITY** | P1 is per field (`p1_geometry(FieldAnalysis)`, `endpoints.P1_geometry`); `alpha_1`/`alpha_2` are per-field block allocations; `4x_alpha_geom = 0.02` budgets four per-field tests; `G5`/`P1` recorded per `field_id` with no replicate-level counterpart; C3's `primary_release_endpoint = G5_BLOCK_SIZE` with Block-1 as `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC`; C2 per-field and never pooled; the `R`/`alpha`/boundary triples for C3 and C4 |
| **NECESSARY DERIVATION** | the counted event's null probability must be the single-field block rate, because the comparison target is a per-field nominal level |
| **HISTORICAL / SUPERSEDED** | the coarse `CP_upper <= 0.03` rule (retained only as a mandatory reported diagnostic); the original `475633c` C3/C4 criteria |
| **IMPLEMENTATION ONLY** | `FIELD_LEVEL_EVENTS` / `REPLICATE_LEVEL_EVENTS` in the driver; the driver's refusal text |
| **AMBIGUOUS** | `assurance[C3/C4].unit = "campaign"` and `pooling = "NOT_APPLICABLE"` — introduced at `b596fe1`, `unit` carries no authority tuple, and the `pooling` reason restates its own conclusion while citing a clause that says "at every declared geometry"; C3's `R` derivation contradicts its own `unit` |
| **NOT SPECIFIED** | the field-to-replicate reduction itself, for **both** C3 and C4 |

Driver behaviour was **not** treated as authority. Tests were not treated as
authority.

---

## Consistency diagnostic — NOT authority

How each candidate would behave under a **correctly implemented** null. Presented
strictly as a diagnostic; it is evidence about coherence, never a substitute for a
prospective decision.

**Field independence is NOT assumed and is known to be false**: the common-mode
uncertainty stream is shared across the fields of a replicate by design (it
cancels in P2 and not in P3), and the Branch-A realisation is per replicate. The
independence column is therefore one point inside a range; Fréchet bounds under
arbitrary dependence are given beside it.

| case | candidate | null p (independent) | E[rejections] | P(declare `STATISTICAL_SIZE_FAILURE`) | Fréchet range for p |
|---|---|---|---|---|---|
| C3 | single field (A or D) | 0.001 | 0.40 | **0.0079** | — (exact) |
| C3 | any field (B) | 0.003994 | 1.60 | **0.2158** | [0.001, 0.004] |
| C3 | every field (C) | 1e-12 | 0.000 | **0.0000** | [0, 0.001] |
| C4 | single field (A or D) | 0.004 | 8.00 | **0.0339** | — (exact) |
| C4 | any field (B) | 0.015904 | 31.81 | **0.9999** | [0.004, 0.016] |
| C4 | every field (C) | 2.56e-10 | 0.000 | **0.0000** | [0, 0.004] |

Reading:

- Only the **single-field** event yields a calibrated test against the frozen
  boundary — 0.8% and 3.4% false-alarm rates against a one-sided 5% design.
- **Any field** would declare a correctly implemented C4 pipeline a size failure
  with probability ≈ 0.9999 under independence. Under *perfect positive*
  dependence its probability collapses to `alpha` and it becomes calibrated, so
  this is strong evidence against B but not a proof — the dependence structure is
  not declared anywhere.
- **Every field** makes both tests vacuous under independence: the boundary can
  essentially never be reached, so the case would validate nothing. Under perfect
  dependence it too collapses to `alpha`.
- The diagnostic **cannot** separate A from D: a reference-field event and a
  per-field event have the same null rate. It narrows the field, and leaves the
  two readings that authority does not adjudicate.

---

## Current driver behaviour

The driver is **already fail-closed and must stay that way**.
`replicate_level_rejections` implements the reduction only where it is
unambiguous (a single declared field, which is C6's situation) and otherwise
raises the dedicated coded refusal `ENDPOINT_EVENT_REDUCTION_UNDECLARED`, naming
the gap:

> "frozen authority does not declare how the four PER-FIELD decisions of a
> replicate combine into the ONE replicate-level event this case's denominator
> counts … The driver refuses rather than choosing between 'any field rejects',
> 'the reference field rejects' and 'every field rejects', which are different
> measured sizes."

The per-field decisions are recorded faithfully regardless, so whichever rule is
eventually authorised will have genuine events to consume. C6 carries an
equivalent guard should its declared field count ever change. A test asserts the
refusal. **No implementation blocker: the driver does not choose.**

---

## No-outcome status

```text
OFFICIAL CAMPAIGN RESULTS = NONE
```

Verified: no `results/e1a_v4_validation` directory exists; execution seal
`state = PRE_DRIVER`, `expected_execution_identity = None`,
`execution_authorised = False`, `random_draws = 0`, `trajectories = 0`. The plan's
own status records that nothing has been executed. No scientific outcome informed
any statement in this report.

---

## Decision table

Only scientifically viable options. **No option is recommended**, and none is
preferred for software simplicity.

### C3 — endpoint `G5_BLOCK_SIZE`, Block-2, `alpha_2 = 0.001`

| option | meaning | relation to field tests | null-size interpretation | effect on frozen boundary | `R`/boundary still valid? | files needing prospective amendment |
|---|---|---|---|---|---|---|
| **A. Reference field** | count `theta0_circular`'s G5 decision | other three reported, not counted | achieved Block-2 size at one geometry | none | yes, unchanged | plan `cases.C3.formal_pass_fail_criterion`, `assurance[C3]`, `size_validation_semantics.derived_boundaries.C3`, `release_authority` C3 row; must also state *why* one geometry defines the case |
| **B. Any field** | union of four G5 decisions | replicate-level union | union size, ≈ up to 4× `alpha_2` | boundary calibrated for `alpha_2`, not for the union | **no** — target would need restating as the union level | all of the above **plus** the nominal target; contract `endpoints.P1_geometry` untouched |
| **C. Every field** | intersection of four | replicate-level intersection | intersection size, ≤ `alpha_2`, vacuous under independence | boundary unreachable | **no** — the case would validate nothing | as B; would also need a scientific justification connecting C3 to an intersection reading |
| **D. Per field** | four size tests, as C2 | none — no reduction | achieved Block-2 size at every geometry | boundary unchanged; applied four times | yes, unchanged per field | `assurance[C3].unit` (`campaign` → `per_field`) and `pooling`, `release_authority` C3 `unit`/`pooling`, `size_validation_semantics.derived_boundaries.C3` (add `per_field`) |

### C4 — endpoint `BLOCK1_ACHIEVED_SIZE`, Block-1, `alpha_1 = 0.004`

| option | meaning | relation to field tests | null-size interpretation | effect on frozen boundary | `R`/boundary still valid? | files needing prospective amendment |
|---|---|---|---|---|---|---|
| **A. Reference field** | count `theta0_circular`'s Block-1 decision | others reported | surrogate-induced Block-1 size at one geometry | none | yes, unchanged | plan `cases.C4.formal_pass_fail_criterion`, `assurance[C4]`, `derived_boundaries.C4`, `release_authority` C4 row |
| **B. Any field** | union of four | replicate-level union | ≈ up to 4× `alpha_1` | **severe**: a correct pipeline fails with probability ≈ 0.9999 under independence | **no** | as A **plus** the nominal target |
| **C. Every field** | intersection | replicate-level intersection | ≤ `alpha_1`, vacuous | boundary unreachable | **no** | as B, plus a justification |
| **D. Per field** | four size tests | none | surrogate-induced Block-1 size at every geometry | unchanged, applied four times | yes, unchanged per field | `assurance[C4].unit`/`pooling`, `release_authority` C4 `unit`/`pooling`, `derived_boundaries.C4` |

### Must C3 and C4 share one rule?

**No, and they should be decided separately.** Their endpoints differ (Block-2 vs
Block-1), their cited authority differs (design §15 item 8 vs item 5), and their
replicate counts have different provenance — C3's `R` is *derived from contract
requirement [2]* via a reason invoking "the same declared geometries", while C4's
`R = 2000` is explicitly package-level with the contract stating no count at all.
The evidence for C3 is contradictory; the evidence for C4 is simply absent. No
document ties the two cases to a common reduction.

### Preserved regardless of the decision

C3's already-frozen separation must survive any amendment: the C3 **primary
release** endpoint is `G5_BLOCK_SIZE` (Block-2), while the full two-block P1
result is `SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` with
`joint_p1_result_changes_C3_release_verdict: false`. `c3_semantics.what_is_forbidden`
prohibits adding any C3 release threshold based on Block 1 or the joint P1 result.
The secondary P1 diagnostic must not become the C3 primary event.

---

## Open issues not addressed here

Out of scope by instruction, and untouched: negative-stiffness / shared-drag
sign-domain authority; absolute drag / field construction; generator identity;
PRNG authority; C6 inputs; remaining C8 inputs; diagnostic aggregator authority.

---

## Disposition

C3 and C4 are reported separately, and both reach the same disposition.

**C3 — UNSPECIFIED.** No frozen document states the reduction. The package
contains *contradictory* signals: `R = 400` is derived from a contract clause
whose text is "at every declared geometry", while `unit`/`pooling` assert a single
campaign-level count without an authority tuple. Resolving C3 requires choosing
between those two readings, which is a prospective scientific decision.

**C4 — UNSPECIFIED.** No frozen document states the reduction, and C4 lacks even
C3's contradictory evidence: its replicate count is package-level, its cited
design item concerns the operating quantile rather than size across geometries,
and nothing addresses field structure.

No rule was chosen. No frozen scientific file was modified. The driver's
fail-closed refusal was not loosened.

```text
C3/C4 REDUCTION NOT SPECIFIED:
PROSPECTIVE SCIENTIFIC DECISION REQUIRED BEFORE EXECUTION
```
