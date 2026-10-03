# E1a v4 — passive-drag runtime reconciliation report (F2e)

Implementation of the independently cleared G6 passive-drag domain across the
complete Branch-A lifecycle. **No new scientific decision is introduced**, and no
scientific authority text was edited.

---

## Starting coordinate

```text
STARTING HEAD    621c2716120c4aff7320c6579617b6454fa46232
STARTING TREE    0ebd569e90925e976006f6241864e73c9cc0de9f
WORKTREE         clean
BRANCH           gaussian/stage-a-environment

WORK COMMIT      7f0647624c4a415071411c719fd615a54357f452
WORK TREE        29917692d36ac942f1a8c014f2cdf13a776a1c12
```

---

## Runtime inventory, taken before editing

| surface | eta present | a present | gamma derived | domain checked | persisted | recovery checked |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| `BranchAField.__post_init__` | yes | yes | — | **NO** | — | — |
| `BranchAField.gamma` / `.tau_modes` | yes | yes | yes | **NO** | — | — |
| `build_field` | yes (arg) | yes (arg) | — | **NO** | — | — |
| `BranchARealisation.from_branch_a_field` | yes | yes | consumed via `tau` | **NO** | **NO** | — |
| `BranchARealisation.canonical()` (hash preimage) | **NO** | **NO** | — | — | **NO** | — |
| `BRANCH_A_FIELD_AUTHORITY` registry | **absent** | **absent** | — | — | — | — |
| `publication_envelope` | via evidence | via evidence | — | — | **NO** | — |
| `reconstructed_branch_a_field` | **placeholder 1.0** | **placeholder 1.0** | not recomputed | **NO** | — | **NO** |
| `require_branch_a_measurement_invariants` | — | — | interval only | **NO** | — | partial |
| `BranchARealisation.calibration_condition` | — | — | via `tau` | **NO** | — | — |
| `resolve_job_specification` | **undeclared** | **undeclared** | — | n/a | — | — |
| calibration lock / Branch-B gating | — | — | — | **NO** | — | — |

---

## Pre-repair lag, reproduced across the lifecycle

Measured at `621c271` before any edit, driving real fields through
`realise_branch_a → publish_branch_a → verified_publication → lock_calibration`:

| input | gamma | production | publish | recovery | lock |
|---|---:|---|---|---|---|
| `eta = 0` | `0` | **VALID** | **uncoded `ZeroDivisionError`** | — | — |
| `a = 0` | `0` | **VALID** | **uncoded `ZeroDivisionError`** | — | — |
| `eta < 0` | `< 0` | **VALID** | uncoded `Refusal` (calibration layer) | — | — |
| `a < 0` | `< 0` | **VALID** | uncoded `Refusal` | — | — |
| **`eta < 0` and `a < 0`** | **`> 0`** | **VALID** | **PUBLISHED** | **ACCEPTED** | **LOCKED** |
| `eta = +inf` | `inf` | **VALID** | uncoded `Refusal` | — | — |
| `a = NaN` | `nan` | **VALID** | uncoded `Refusal` | — | — |

All seven VALID at production. Six were stopped only incidentally, and never by
the primitive rule: four by an **uncoded** refusal raised in the *calibration*
layer — a derived quantity standing in for a measurement rule — and two by a raw
`ZeroDivisionError`. The seventh traversed the entire official chain.

The existing negative-stiffness precedent was measured in the same way:
`status = BRANCH_A_INVALID`, publication refused. F2e mirrors it exactly for the
drag primitives.

---

## Primitive-domain implementation

`e1a_v4/branch_a.py` gains `admissible_primitive`, applied to each primitive
**individually** and **before anything derived**:

```python
if isinstance(value, bool) or not isinstance(value, (int, float)):
    return False
number = float(value)
return math.isfinite(number) and number > 0.0
```

`bool` is rejected by identity because it subclasses `int`; a flag is not a
measurement. `__post_init__` then records `BRANCH_A_INVALID` — the same
disposition the sibling positive-definite stiffness rule records, so no new
behaviour class is invented. A second gate at `JobExecution.realise_branch_a`
refuses a non-VALID field at the boundary of the official chain, with a coded
refusal that names the offending primitive.

**Ordering** is `primitive availability → eta domain → a domain → stiffness
domain → derive gamma → gamma representability → derive tau → tau
representability → publication eligibility`. Nothing derived is ever what
certifies the primitives that produced it.

---

## Missing versus invalid

| state | runtime behaviour |
|---|---|
| `eta` or `a` **absent / undeclared** | `resolve_job_specification` refuses with `UNDECLARED_FIELD_INPUTS`, unchanged. A primitive cannot be absent at the constructor at all — both are required dataclass fields — so absence is resolved strictly upstream, where it belongs |
| `eta` or `a` **present, nonfinite / zero / negative** | `BRANCH_A_INVALID`, then a coded `BRANCH_A_MEASUREMENT_INVALID` at the chain boundary |

`classify_drag_inputs` resolves **missing first**: an input we do not possess has
no value to be outside a domain. The two never collapse, and a direct regression
asserts the inequality of the two dispositions.

---

## Gamma

`gamma = 6 pi eta a`, relation unaltered. For admissible primitives it is derived
positive — but the **executable representation is checked, never assumed**.
Underflow to `0.0` and overflow to `inf` both occur for finite positive
primitives and both are caught.

## Tau

`tau_r = gamma / k_r`, relation unaltered, carried with ascending `k` exactly as
production pairs them. The new `TAU_FROM_PRIMITIVES` invariant recomputes gamma
and every relaxation time **through the production object's own properties** and
compares the canonical encodings exactly. No second tau validator was written and
no tolerance was introduced; the previously cleared shared-gamma feasibility test,
its ties-to-even endpoints and the one-common-gamma invariant are retained
unweakened and still run.

---

## Double-negative closure

```text
eta = -8.9e-04 , a = -1e-06
gamma = 1.6776104770169493e-08   > 0   FINITE
tau   = 0.0001677610477016949    > 0   FINITE
```

| boundary | before | after |
|---|---|---|
| production status | `VALID` | **`BRANCH_A_INVALID`** |
| realise / publish | published | **refused, naming the primitives** |
| recovery (forged artifact) | accepted | **`BRANCH_A_MEASUREMENT_INVALID`** |
| calibration lock | locked | **refused** |
| Branch B | reachable | **unreachable** |

A gamma-only implementation cannot pass this. Proved, not asserted: weakening
production to `6 pi eta a > 0` in a sandbox makes the **full static preflight**
refuse with `BRANCH_A_DOMAIN_AUTHORITY_MISMATCH`, naming the double-negative pair.

---

## Underflow / overflow — the separation holds

| case | primitives | production | refusal pathway |
|---|---|---|---|
| `eta = a = 5e-324` | both admissible | **`VALID`** | numerical: *"relaxation time 0 is 0.0"* |
| `eta = a = 1e300` | both admissible | **`VALID`** | numerical: *"relaxation time 0 is inf"* |
| `eta < 0` | inadmissible | `BRANCH_A_INVALID` | physical: *"inadmissible measured primitive(s): viscosity=-0.00089"* |

Physically admissible primitives are **never** relabelled invalid. Both reuse the
existing `BRANCH_A_MEASUREMENT_INVALID` status — no new scientific status was
created — and the diagnostic text carries the specificity.

---

## Persistence

Evidence now carries `viscosity` and `bead_radius` as `float.hex()` canonical
floats, **inside `canonical()`**, which is the hashing preimage. Both have rows in
`BRANCH_A_FIELD_AUTHORITY` classified `MEASURED` with the existing
`POSITIVE_FLOAT` rule, and both are bound to the record's `field_id`.

`eta(T_theta)` is field-indexed by authority and is persisted per field.
Authority writes `a` **without** a field index throughout, with a single bead, so
F2e does **not** invent a cross-field equality rule for it; it is persisted per
package because it is an input to that package's gamma. That choice is recorded
here rather than made silently.

Non-finite values cannot be persisted at all: `canonical_float` refuses them, so
there is no NaN normalisation loophole.

## Artifact schema version

```text
e1a_v4_branch_a_publication/2  ->  /3
```

A version-2 record cannot say which primitives produced its gamma. **No lossless
migration exists** — `eta < 0, a < 0` and a legitimate pair give the same gamma,
so the map is not injective. A version-2 artifact is **REFUSED**, never
reinterpreted, and `SUPERSEDED_BRANCH_A_PUBLICATION_SCHEMAS` records both prior
versions. No official artifact of any version exists: the campaign has not run.

---

## Recovery

The neutral placeholder is **gone from the authoritative path**.
`reconstructed_branch_a_field` now builds the production object from the recorded
primitives, so every creation-time rule is re-applied on read. Two invariants
were added to the inventory, which grows from five to seven:

```text
PRIMITIVE_DRAG_DOMAIN   eta and a re-tested against the approved domain BEFORE
                        anything derived from them is examined
TAU_FROM_PRIMITIVES     gamma and every tau recomputed exactly through the
                        production object and compared
```

Recovery does not trust a stored `status`: it recomputes it.

### Primitive tamper results

| tamper | result |
|---|---|
| `viscosity` = 0 / negative | `BRANCH_A_MEASUREMENT_INVALID` |
| `bead_radius` = 0 / negative | `BRANCH_A_MEASUREMENT_INVALID` |
| either = `"inf"` / `"nan"` / bool / `"0.001"` | refused at the parse boundary |
| either removed or renamed | `BRANCH_A_MEASUREMENT_INVALID` + `PUBLICATION_INCOMPLETE` |
| `viscosity` doubled, taus untouched | refused — taus no longer follow |
| `bead_radius` halved, taus untouched | refused |
| taus scaled, primitives untouched | refused |
| unknown field added to the evidence | refused by the publication schema |
| **double-negative, fully self-consistent, re-digested and re-committed** | **refused on the primitives** |

Cryptographic self-consistency does not substitute for scientific validity: every
forgery above was re-digested through the evidence hash, the envelope digest and
the commit marker before being read back.

---

## Calibration condition, lock and Branch B

The condition is derived from the realisation, whose digest now binds the
primitives, so the binding is **transitive through existing package identity** —
no field was duplicated into the condition preimage. The calibration boundary
gained a coded guard so a non-finite or non-positive tau no longer escapes as a
raw arithmetic error.

For `eta < 0`, `eta < 0 ∧ a < 0`, `eta = 0` and the gamma-underflow case, all
three downstream gates were verified directly rather than inferred: **no Branch-A
publication exists, no calibration condition can be derived, and Branch B cannot
be unblinded.**

---

## Production / recovery parity matrix

| case | production | official chain | agree? |
|---|---|---|:--:|
| 1 missing `eta` | `UNDECLARED_FIELD_INPUTS` (upstream) | blocked | ✓ |
| 2 missing `a` | `UNDECLARED_FIELD_INPUTS` (upstream) | blocked | ✓ |
| 3 `eta = 0` | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 4 `a = 0` | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 5 `eta < 0` | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 6 `a < 0` | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 7 `eta < 0, a < 0`, gamma > 0 | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 8 `eta` nonfinite (`+inf`, `-inf`, `NaN`) | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 9 `a` nonfinite (`+inf`, `NaN`) | `BRANCH_A_INVALID` | refused, coded | ✓ |
| 10 valid primitives, gamma underflow | `VALID` | refused *numerically* | ✓ |
| 11 valid primitives, gamma overflow | `VALID` | refused *numerically* | ✓ |
| 12 fully valid | `VALID` | publish / recover / lock all OK | ✓ |

**Production and recovery never disagree about scientific validity, and no case
produces an uncoded exception.**

---

## The seven disclosed examples

| input | before | after |
|---|---|---|
| `eta < 0` | VALID | **BRANCH_A_INVALID** |
| `a < 0` | VALID | **BRANCH_A_INVALID** |
| `eta < 0` and `a < 0` | VALID → published → recovered → locked | **BRANCH_A_INVALID, blocked at every gate** |
| `eta = 0` | VALID | **BRANCH_A_INVALID** |
| `a = 0` | VALID | **BRANCH_A_INVALID** |
| `eta = inf` | VALID | **BRANCH_A_INVALID** |
| `eta = NaN` | VALID | **BRANCH_A_INVALID** |

```text
F2 IMPLEMENTATION LAG: CLOSED  (0 of 7 behind authority)
```

The lag test was **flipped, not deleted**: the same seven inputs are still
checked, and the assertion is now conformance. Preflight additionally carries
`require_runtime_conformance`, which fails if production ever drifts back.

---

## F4

```text
ACTUAL ETA/A VALUES STILL UNDECLARED
F4 OPEN
OFFICIAL JOB RESOLUTION STILL BLOCKED AS EXPECTED
```

`resolve_job_specification` still refuses with `CAMPAIGN_PLAN_MISMATCH` carrying
the unchanged `UNDECLARED_FIELD_INPUTS` text naming `viscosity (eta)` and
`bead_radius (a)`. The contract's `values_not_set.status` is still `OPEN`, no
contract field carries either quantity, and no viscosity model, bead radius,
uncertainty or hardware provenance was introduced. Every eta and a in the test
suites is a labelled **TEST FIXTURE**, not a field-construction input.

This is the desired state: the machinery is complete, and the campaign is still
blocked by F4.

---

## Identities

Recomputed **twice** from independent clean `git archive` extractions of
`7f06476`. Both agree.

| identity | before | after | |
|---|---|---|---|
| physical foundation | `6d9aed24…` | `6d9aed24…` | **unchanged** |
| theory baseline | `0a01b356…` | `0a01b356…` | **unchanged** |
| prospective design | `25b637c3…` | `25b637c3…` | **unchanged** |
| design contract | `d7215ae4…` | `d7215ae4…` | **unchanged** |
| **seed map** | `c25f2da8…` | `c25f2da8…` | **unchanged** |
| master seed | `4447657248690327258` | same | **unchanged** |
| all five family seeds | — | — | **unchanged**, `drawn_in_this_stage: false` |
| analysis procedure identity | `8cf86c96…` | **`60122602…`** | **moved** |
| plan JSON | `c213b5d3…` | `fbe18778…` | rebound |
| plan Markdown | `dcbff1b7…` | `2d407815…` | rebound |
| unsealed execution identity | `e2838a3f…` | **`442e3d53…`** | moved |

### Why the analysis identity moved, and the deviation it forced

`procedure_identity` hashes the twelve `SCIENTIFIC_MODULES`. Exactly one moved:

```text
e1a_v4/branch_a.py   748c2e86… -> 8a1a66ab…
```

The approved rule is a statement about a **measured Branch-A quantity**, and its
sibling — the positive-definite stiffness rule — already lives in
`BranchAField.__post_init__`. Implementing the eta/a half anywhere else would
leave the core object reporting `VALID` for `eta < 0`, which is both false and a
production/recovery disagreement the required parity matrix forbids.

The task expected the validation-plan JSON and Markdown to stay byte-fixed while
also instructing that the old identity must not be artificially preserved.
**Those two cannot both hold once a scientific module changes**, because the plan
records the analysis identity and preflight compares them. This report records the
choice explicitly rather than resolving it silently:

- rebound: `frozen_identities.analysis_procedure_identity`,
  `implementation_file_hashes["e1a_v4/branch_a.py"]`, and `plan_version`
  `1.16.0 → 1.17.0` per the repository convention that 17 of 18 prior plan-JSON
  commits follow;
- **the plan's scientific content is byte-identical** — adopted rules, replicate
  counts, the G1–G6 roster and the G6 resolution were all verified unchanged, and
  the whole JSON diff is three identity lines.

The seed map derives from the **contract** digest, which did not move, so no seed
changed and none was drawn. The unsealed execution identity moved because the
runtime and plan both did; it is a pre-driver diagnostic and remains **not
frozen**, with `expected_execution_identity` still `null`.

---

## Tests

From the **committed tree**:

| suite | checks | |
|---|---:|---|
| `test_e1a_v4_release_authority.py` | 1,237 | |
| `test_e1a_v4_driver_endpoints.py` | 626 | |
| `test_e1a_v4_terminal_calibration.py` | 538 | |
| `test_e1a_v4_drag_domain.py` | 181 | |
| `test_e1a_v4_coherence_hardening.py` | 178 | |
| `test_e1a_v4_size_semantics.py` | 138 | |
| `test_e1a_v4_repair.py` | 126 | |
| `test_e1a_v4.py` | 122 | |
| `test_e1a_v4_case_scope.py` | 114 | |
| **`test_e1a_v4_drag_runtime.py`** | **114** | **new** |
| `test_e1a_v4_generating_model.py` | 113 | |
| `test_e1a_v4_plan_coherence.py` | 113 | |
| `test_e1a_v4_calibration_scope.py` | 105 | |
| `test_e1a_v4_preexec.py` | 105 | |
| `test_e1a_v4_contract_plan.py` | 76 | |
| `test_e1a_v4_dispositions.py` | 64 | |
| `test_e1a_v4_preexec_corrections.py` | 52 | |
| **Total** | **4,002** | |

```text
SUITES                 17
CHECKS                 4002
FAILURES               0
UNCLEAN SUITES         0
SCIENTIFIC RNG DRAWS   0
CALIBRATION EXECUTIONS 0
TRAJECTORIES           0
CAMPAIGN JOBS          0
```

Every suite printed exactly one parseable summary; the hardened runner rule — a
suite with no clean summary line counts as unclean — is preserved.
`git diff --check` is clean.

### Fixtures updated, and why

`valid_measurement` and `forced_measurement` previously built a field with
placeholder primitives while deriving relaxation times from an unrelated fixture
gamma. That was only possible while gamma was never recomputed. Both now realise
their requested gamma as a **TEST-ONLY admissible pair** (`a = 1`,
`eta = gamma / 6 pi`) and read the relaxation times back from the production
object, so each fixture is a record production could actually have written.
`production_record` persists the primitives it already used. Registry-count
assertions moved from 5 to 7 invariants and the MEASURED set gained two entries.
The stale comment claiming the gamma sign was "an open field-construction
question" was corrected: the domain is declared, and the tolerated parity
divergence is now attributable to the stiffness rule alone.

### F1 and F2 authority regressions

Unchanged and passing: C2 per-field P1, C3 G5, C4 Block-1, structured refusals,
`NOT_EVALUABLE`, whole-record consistency, C1/C7 compositions, C8 factor-evidence
preflight; G1–G6 authority-gap totality, drag-domain authority, contract/plan
conformance, Markdown/JSON coherence, strict JSON and release authority. The
negative-stiffness and zero-stiffness regressions still produce the prior invalid
disposition — the parity divergence **set** is unchanged, which is the assertion
that F2e altered no stiffness science.

### Deferred integration

```text
trajectory-bearing campaign-driver suite NOT RUN
```

`test_e1a_v4_campaign_driver.py` was **not modified**. It remains KNOWN DEFERRED
with pins stale from before F2c and is not validation evidence. Its 102 imported
package names were confirmed to still resolve after the schema and signature
changes.

---

## Scientific non-change

```text
NO NEW SCIENTIFIC DECISION INTRODUCED
```

The eta/a domain, the missing-versus-invalid dispositions, the Stokes and
relaxation relations, the stiffness rule, the representability semantics, every
threshold, the case roster and every replicate count are exactly as the
independently cleared F2 authority states them. No new scientific status was
created; the existing `UNDECLARED_FIELD_INPUTS`, `BRANCH_A_INVALID` and
`BRANCH_A_MEASUREMENT_INVALID` categories carry the verdicts, with diagnostic
detail supplying the specificity.

---

## Execution state

```text
OFFICIAL RESULTS       NONE   (results/e1a_v4_validation does not exist)
OFFICIAL CAMPAIGN      NOT RUN
OFFICIAL TRAJECTORIES  0
FINAL EXECUTION SEAL   NOT FROZEN   (state PRE_DRIVER)
EXECUTION AUTHORISED   FALSE
```

---

## Remaining programme blockers

```text
F3  PRNG choice                                   OPEN
F4  field construction / actual eta and a inputs  OPEN
F5  generator identity                            OPEN
F6  C6 implementation inputs                      OPEN
F7  remaining C8 implementation inputs            OPEN
F8  diagnostic aggregator                         OPEN
G1  deferred trajectory-bearing integration       DEFERRED / NOT RUN
```

This stage is **not** an execution-readiness claim. The seal is not ready, the
campaign is not ready, and official job resolution still refuses.

---

## Next stage

```text
F2f INDEPENDENT RUNTIME / PROVENANCE AUDIT
READY
```

---

```text
PASSIVE-DRAG RUNTIME RECONCILIATION COMMITTED
```
