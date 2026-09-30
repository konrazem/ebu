# E1a v4 — C3/C4 per-field operating analysis

Prospective design calculation and authority analysis only. No frozen file, no
driver, no classifier and no scientific module was modified. Nothing was
executed. Read against `HEAD = ac1fc7b` on `gaussian/stage-a-environment`.

Continues `docs/e1a/E1A_V4_C3_C4_FIELD_REDUCTION_AUTHORITY_REPORT.md`, which
concluded `C3 = UNSPECIFIED`, `C4 = UNSPECIFIED`.

---

## Approved decision

Recorded as given, and not reopened here:

```text
C3 elementary event = PER FIELD
C4 elementary event = PER FIELD
NO within-replicate field reduction
NO field-count pooling
```

Each declared field keeps its own R-replicate Bernoulli rejection sequence and its
own rejection count `r_theta`, scored by its own frozen size test. There is no
any-field event, no every-field event, no reference-field-only event, and no
pooling of counts between fields.

---

## Per-field statistical rules, verified from authority

Recomputed with the repository's own `size_boundary` / `cp_lower`, not copied
from the plan text. Both agree with the frozen records.

| | C3 (Block-2, G5) | C4 (Block-1, surrogate) |
|---|---|---|
| `R` | 400 | 2000 |
| nominal | `alpha_2 = 0.001` | `alpha_1 = 0.004` |
| source of nominal | contract `endpoints.P1_geometry.alpha_2` | contract `endpoints.P1_geometry.alpha_1` |
| detector | `CP_lower(r, R) > alpha` | `CP_lower(r, R) > alpha` |
| `CP_lower` at boundary | `CP_lower(2, 400) = 0.0008891209` ≤ 0.001 | `CP_lower(13, 2000) = 0.0038489425` ≤ 0.004 |
| `CP_lower` at boundary+1 | `CP_lower(3, 400) = 0.0020472587` > 0.001 | `CP_lower(14, 2000) = 0.0042367805` > 0.004 |
| integer boundary | clean 0–2, inflation 3+ | clean 0–13, inflation 14+ |

Unchanged by this task.

---

## Per-field operating probabilities

`q_theta = P[field incorrectly classified as size-inflated]` under the **exact
nominal per-field null**, from the frozen binomial model and integer boundary.
Computed in exact rational arithmetic (`Fraction`, exact binomial sum), converted
once at the end. **No Monte Carlo, no RNG.**

| | C3 | C4 |
|---|---|---|
| event | `P(X ≥ 3 \| n = 400, p = 1/1000)` | `P(X ≥ 14 \| n = 2000, p = 1/250)` |
| exact value | `0.00788343125882217` | `0.033884449548367356` |
| full precision | `0.007883431259` | `0.033884449548` |
| percentage | **0.7883431 %** | **3.3884450 %** |
| `P(field clean)` | **0.992116568741** (99.21166 %) | **0.966115550452** (96.61156 %) |

Both per-field tests sit **below** the one-sided 5% design level, C3 markedly so.
That is discreteness, not slack: the integer boundary is the largest `k` whose
`CP_lower` still clears the nominal, so the achieved level is whatever that
integer yields.

### Verification of the stated approximations

| stated | computed | difference | verdict |
|---|---|---|---|
| C3 ≈ `0.0078834` (0.788 %) | `0.0078834313` | `3.1e-08` | **CONFIRMED** |
| C4 ≈ `0.0338844` (3.388 %) | `0.0338844495` | `5.0e-08` | **CONFIRMED** |
| C4 `P(field clean) ≈ 0.9661` | `0.9661156` | `1.6e-05` | **CONFIRMED** |

---

## Case-level requirement: is a scalar actually needed?

**No. A scalar case verdict is not a scientific requirement.** This is the
decisive structural finding, and it is checkable in the frozen classifier.

`classification.classify_campaign` builds a `failures: list[str]` and returns
`VALIDATION_PASS` iff that list is empty, under the stated rule:

> "conjunctive: every required case must pass on its own terms; no weighted
> score, no compensation between cases"

The conjunction **already carries sub-case conditions natively**:

```text
C2   for fid, k in counts.c2_rejections_by_field.items():
         ... failures.append(f"STATISTICAL_SIZE_FAILURE (C2 field {fid})")
C7   for alt, k in counts.c7_false_acceptances_by_alternative.items():
         ... failures.append(f"FALSE_BRIDGE_DISCRIMINATION_FAILURE (C7 {alt})")
```

C2 contributes **four** conditions, one per field, each naming its field. C7
contributes four, one per alternative. Nothing in the architecture requires a case
to contribute exactly one boolean.

The scalar for C3/C4 lives only in the counts data model:

```text
c2_rejections_by_field: Mapping[str, int]     # per-field shape ALREADY EXISTS
c3_rejections:          int                   # scalar
c4_rejections:          int                   # scalar
```

**Classification: this is an implementation / data-model issue, not a scientific
requirement.** The per-field shape has an existing precedent in the same
dataclass, and adopting it for C3/C4 introduces no new statistical object.

---

## The case-level rule is forced, not chosen

Given the approved per-field elementary event and the already-frozen conjunctive
architecture, the case-level semantics are **uniquely determined**:

1. **Conjunction is associative.** A final rule `(θ0 ∧ θ1 ∧ θ2 ∧ θ3) ∧ rest` and a
   final rule `θ0 ∧ θ1 ∧ θ2 ∧ θ3 ∧ rest` are the same predicate. A vector-valued
   C3 disposition entering the conjunction as four conditions and an
   all-fields-clean scalar entering as one condition therefore produce **identical
   release verdicts** in every possible outcome. They are not two scientific
   rules; they are two renderings of one rule.
2. **No alternative survives the existing constraints.** Any rule that lets one
   field fail while the case passes is compensation, which the frozen classifier
   forbids in terms. Reference-field-only gating privileges `theta0`, excluded by
   the approved decision. Pooling is excluded by the approved decision. A weighted
   score is forbidden. Nothing coherent remains.
3. **The vector form is nevertheless the one to record**, for two reasons that are
   about science rather than logic: it preserves which field failed (below), and
   it avoids minting a replicate-wide event that the approved decision abolished.

### The distinction that must be maintained

```text
ALLOWED    case clean  ==  all four FIELD SIZE GATES clean
                           (each gate = its own r_theta against its own boundary)

FORBIDDEN  case clean  ==  count of replicates where ANY field rejected,
                           scored against R
```

These are statistically different objects — the second is the abolished
within-replicate union, and it has a different null rate. The derived rule is the
first. No implementation may realise it as the second.

---

## Preserving field failure information

The vector disposition retains, per field and per case, the full record required:

```text
r_theta                  the field's own rejection count
r_theta / R              its observed rate
CP_lower, CP_upper       its own interval
verdict                  NO_SIGNIFICANT_SIZE_INFLATION_DETECTED / STATISTICAL_SIZE_FAILURE
```

`classify_size` already returns exactly this structure per invocation, and C2
already stores it per field under `detail["C2"][fid]`. No scalar case flag may
replace or discard it: the four fields are four **distinct physical conditions**
— `theta0` circular 100/100 µN/m at 298 K, `theta1` 210/210, `theta2` elliptic
150/60 rotated 30°, `theta3` 100/100 at 318 K — and which one showed inflation is
scientifically load-bearing.

---

## Dependence

**Independence across fields is false by design, and is not assumed anywhere
below.**

Frozen `generating_model.branch_a`:

> `common_mode`: "**ONE draw per experiment, shared across every field**, so it
> cancels in the P2 ratio and not in P3"

This is implemented as `EXPERIMENT_SCOPE` in `scope.common_mode_seed`, documented
as "INTENTIONAL within-experiment sharing … it must not be redrawn per field", and
the seed layer *enforces* that experiment scope is legal only for the
`BRANCH_A_MEASUREMENT` family.

| component | across the four fields of one replicate |
|---|---|
| Branch-A common mode (`sigma_cm = 1.15 %`) | **SHARED** — one draw per experiment |
| Branch-A per-mode stiffness | independent per mode; per-field stream |
| Branch-A orientation, thermometry | per-field stream |
| Branch-B trajectories, calibration | domain-separated by `(case_id, replicate_id, field_id)` |

So a single shared multiplicative scale perturbs every field's `H_A` in the same
direction within a replicate, while the remaining randomness is field-separated.

**What can be said prospectively:** the mechanism is a positive-dependence
mechanism — a common scale error pushes all four fields the same way — so the four
field gate outcomes would be expected to be positively associated, which places
`P(all four clean)` **above** the independence benchmark. That is a qualitative
expectation from the frozen design, **not** an analytic result: no frozen document
derives the induced dependence of the G5 or Block-1 rejection indicators, and it
is not available in closed form. **What cannot be said:** any numeric dependence
value. It must not be estimated from official outcomes, of which there are none.

---

## All-fields conjunction: bounds and diagnostics

Marginals at the exact nominal null, `c = 1 - q` per field, four fields.

### Dependence-free bounds — VALID UNDER ARBITRARY DEPENDENCE

Fréchet: `P(∩ clean) ≤ min_i c_i`, and `P(∩ clean) ≥ max(0, Σ c_i − 3)`,
equivalently the union bound on failures `P(any flagged) ≤ Σ q_i = 4q`. For
unequal per-field probabilities the same forms apply with the actual `c_i`; at the
nominal null all four are equal.

| | C3 | C4 |
|---|---|---|
| per-field clean `c` | `0.9921165687` | `0.9661155505` |
| **lower bound** `1 − 4q` | **`0.9684662750`** | **`0.8644622018`** |
| **upper bound** `min_i c_i` | **`0.9921165687`** | **`0.9661155505`** |
| case false-failure probability | **`[0.0078834, 0.0315337]`** | **`[0.0338844, 0.1355378]`** |

### Diagnostics — NOT AUTHORITY

Reported to bracket the effect of dependence. Neither approves nor rejects any
rule, because intentional shared stochastic structure exists.

| | C3 | C4 |
|---|---|---|
| independence `c⁴` — **DIAGNOSTIC — NOT AUTHORITY** | `0.9688372100` | `0.8711968371` |
| perfect dependence (comonotonic) — **DIAGNOSTIC — NOT AUTHORITY** | `0.9921165687` | `0.9661155505` |
| case false-failure at independence | `0.0311628` | `0.1288032` |

The perfect-dependence limit coincides with the Fréchet upper bound: if the four
gates always moved together, the case would be exactly as reliable as one field.

### What this means scientifically — the C4 observation

Verified as requested: `P(C4 field clean) = 0.96612`, and under the independence
diagnostic `P(all four clean) = 0.87120`, with the dependence-free lower bound
`0.86446`.

Read plainly: **a perfectly correct implementation whose true Block-1 size equals
the nominal 0.004 exactly would still see C4 declared
`STATISTICAL_SIZE_FAILURE` with probability up to 13.55 %** (12.88 % at the
independence diagnostic, and as little as 3.39 % under strong positive
dependence). For C3 the same figure is at most 3.15 %.

This is an operating characteristic worth recording, and it is **not** caused by
the case-level aggregation:

- the aggregation is *forced* (conjunction, no compensation), so there is no
  aggregation choice available to change it;
- it is inherited from the already-frozen **per-field** design — `R = 2000`,
  `alpha_1 = 0.004`, one-sided 95 %, integer boundary 13, per-field false-flag
  3.39 % — applied at four distinct physical conditions.

Per §16 the diagnosis is therefore: **the per-field size-validation design, not
the case-level semantics.** No `R`, `alpha`, confidence level or integer boundary
was changed here, and any adjustment would be a separate prospective decision
outside this task. It is recorded for whoever owns that stage.

### No multiplicity correction was applied

Bonferroni, Holm and Šidák were considered and **not** used, deliberately:

- the scientific claim is **per field**, not a single familywise hypothesis — the
  four fields are four different physical geometries and temperatures, and the
  design's own budget already charges them separately (`complete_pipeline.budget_terms.4x_alpha_geom = 0.02`);
- the multiplicity here inflates the **false-failure** rate (spuriously blocking
  release), not the false-**pass** rate. It is the conservative direction for
  release safety; a correction would *weaken* the per-field tests;
- applying one would change the frozen per-field boundaries, which §16 forbids
  here, to protect a familywise target that **no frozen authority declares**.

---

## Complete-pipeline target: exact applicability

**The frozen `>= 0.90` target does NOT apply to C3/C4 gate success.**

What it describes, verbatim from contract `complete_pipeline`:

```text
target_true_bridge_success : 0.9
complete_pass_event        : all 4 fields: BranchA_valid AND rank_ok AND Neff_ok
                             AND mode_rule_ok AND gate_pass; AND P2_accept AND
                             P3_accept AND P4_verified
denominator                : every declared experiment; refusals counted as
                             failures; no conditioning on survivors
```

It is a target on the **per-replicate success rate of the scientific pipeline**,
measured by **C1** over `R = 300` with integer boundary 279
(`assurance[C1]`, `unit: campaign`, CP one-sided LOWER ≥ 0.90).

The frozen size-validation semantics separate the two questions explicitly:

> **A** complete practical performance — "C1, UNCHANGED … **This is the direct
> prospective validation of whether the whole implemented pipeline meets the
> release target.**"
>
> **B** component size inflation — "C2, C3 and C4 … They prospectively **TEST FOR
> EVIDENCE OF INFLATION**."

and `classify_campaign.independent_facts` records that `complete_pipeline_met` and
`component_size_clean` "are reported separately and **never collapsed**".

Consequences:

- C3/C4 **size-validation gate success is not a term in the ≥ 0.90 budget.**
- The case-level C3/C4 false-failure probability **must not** be folded into it.
- The ≥ 0.90 target is a **separate pre-execution validation requirement**, carried
  by C1 alone.
- Therefore the compatibility check conditioned on "if ≥ 0.90 does apply" **does
  not trigger**. The C4 figure of up to 13.55 % is not a violation of the 0.90
  target; it is an operating characteristic of a different experiment.

---

## Scientific interpretation

What each rendering permits us to claim.

**Per-field elementary event + all-fields conjunction (the derived rule):**

> "No significant size inflation was detected at **any of the four declared
> geometries**, each tested separately at its own nominal level over its own R
> replicates."

and, on a failure, the strictly stronger and more useful:

> "Significant size inflation was detected **at `theta2_ellipse`**; the other
> three declared geometries showed none."

**What it does NOT permit**, and what a pooled or replicate-reduced event would
have produced instead:

> ~~"No significant size inflation was detected in a pooled/global field
> experiment."~~

That claim is unavailable, correctly: no pooled quantity is computed.

The already-frozen interpretation limits stand unchanged. A pass means only that
**this experiment did not establish excess size at the chosen confidence level**;
"NOMINAL SIZE PROVED" and its variants remain **forbidden wording**.

---

## C3 secondary diagnostic remains separate

Preserved unchanged under the derived rule:

```text
C3 PRIMARY    G5 / Block-2 size assessment, now per field
C3 SECONDARY  full two-block P1 interaction diagnostic
```

`c3_semantics` fixes `primary_release_endpoint = G5_BLOCK_SIZE`,
`block1_role = SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC` and
`joint_p1_result_changes_C3_release_verdict: false`, and forbids "adding any new
C3 release threshold based on Block 1 or on the joint P1 result". The per-field
decision changes the *unit* of the primary G5 assessment and touches none of that.
The secondary P1 diagnostic does not enter the primary C3 release verdict.

---

## Derived next authority form

Stated because it is uniquely determined, not proposed as one option among
several. Implementation is **not** part of this task.

```text
C3 case disposition = { theta0: CLEAN|INFLATED, theta1: ..., theta2: ..., theta3: ... }
    each member from that field's own r_theta against R = 400, alpha_2 = 0.001,
    boundary 2 (clean 0-2, inflation 3+)

C4 case disposition = { theta0: ..., theta1: ..., theta2: ..., theta3: ... }
    each member from that field's own r_theta against R = 2000, alpha_1 = 0.004,
    boundary 13 (clean 0-13, inflation 14+)

FINAL CONJUNCTION
    each member enters as its own condition, naming its field, exactly as C2 does:
        STATISTICAL_SIZE_FAILURE (C3 field <theta>)
        STATISTICAL_SIZE_FAILURE (C4 field <theta>)
    equivalently and identically: the case is clean iff all four members are clean

POOLING          FORBIDDEN
COMPENSATION     FORBIDDEN
REPLICATE-WIDE FIELD REDUCTION   FORBIDDEN
```

When written into frozen authority this would touch `assurance[C3]`/`assurance[C4]`
(`unit`, `pooling`), `size_validation_semantics.derived_boundaries.C3`/`.C4`
(adding `per_field`), the two `formal_pass_fail_criterion` strings, and the
`release_authority` C3/C4 rows — plus the counts data model and the driver's
refusal. That amendment is a separate authorised step and was **not** performed.

---

## Remaining decision

**A. UNIQUE CONSEQUENCE OF THE APPROVED PER-FIELD DECISION — no additional human
scientific choice is required for the case-level semantics.**

Given the approved per-field elementary event, the frozen conjunctive release rule
with no compensation, and the frozen prohibition on pooling and on privileging the
reference field, the case-level rule is forced; the vector-valued and
all-fields-clean renderings are logically identical at release.

One item is **recorded but not a case-level decision**: the C4 case-level
false-failure probability of up to 13.55 % at the exact nominal null. Per §16 this
belongs to the per-field size-validation design (`R`, `alpha`, level, boundary),
not to case-level aggregation, and is out of scope here. It is reported so that
whoever owns that stage decides with the number in front of them. Nothing was
tuned.

---

## Execution status

```text
OFFICIAL CAMPAIGN RESULTS = NONE

FINAL EXECUTION SEAL = NOT FROZEN

EXECUTION AUTHORISED = FALSE

RNG OBJECTS = 0

TRAJECTORIES = 0
```

Verified: no `results/e1a_v4_validation` directory exists; seal `state =
PRE_DRIVER`, `expected_execution_identity = None`, `execution_authorised = False`,
`random_draws = 0`, `trajectories = 0`. Every probability above is exact binomial
arithmetic on the frozen nominal null. No simulation was run and no outcome
informed any statement.

---

C3/C4 CASE-LEVEL SEMANTICS DERIVED:
each declared field keeps its own R-replicate size test at its own frozen boundary
(C3: R=400, alpha_2=0.001, clean 0-2; C4: R=2000, alpha_1=0.004, clean 0-13); the
case disposition is the VECTOR of the four field verdicts, and each field verdict
enters the final release conjunction as its own named condition, so the case is
clean iff all four fields are clean — with no pooling, no compensation, no
reference-field privilege, and no within-replicate field reduction.
