# E1a v4 — DRIVER ENDPOINT MAPPING, C8 CONTROL AND TERMINAL PROVENANCE REPAIR

| | |
|---|---|
| Audited coordinate | `f27ad312c57ef00b6e1a810f8aa9ff3e6806d2fd` |
| Work commit | `77c6758855c7fc941afef57668b29367947ce25d` |
| Work tree | `0c342533009f12a53391403398767fc2f5895f9e` |
| Branch | `gaussian/stage-a-environment` (not pushed) |
| Files modified | `e1a_v4/validation/campaign_driver.py`, `e1a_v4/validation/refusals.py`, `test_e1a_v4_campaign_driver.py`, **new** `test_e1a_v4_driver_endpoints.py` |

**Working-tree note.** The audit expected one unrelated untracked item, the book
map. Between the audit and this task the author asked for it to be committed, and
it now lives at `0a028a01a4ebed788f2cd7cc31310fb6349ee0fb` on
`codex/book-series-eight-parts`. It was not edited, staged or included here, and
this branch's tree is otherwise clean.

---

## Result

Four defect classes, each reproduced with pure deterministic fixtures **before**
any edit, each repaired, each now a permanent counterexample.

| Auditor finding | Reproduced at `f27ad312` | After repair |
|---|---|---|
| **A** C2 counts the replicate-wide event | `[P,R,P,P]` → counts `{theta0:1, theta1:1, theta2:1, theta3:1}`, total **4** for one true rejection | total **1**, `[0,1,0,0]` |
| **B** C3 / C4 endpoint values lost | `g5_rejected = None`, `block1_rejected = None`; counts **0** whatever is observed | genuine booleans per field; 10 records with 2 Block-1 rejects → **2**, with 3 G5 rejects → **3** |
| **C** C8 is post-hoc multiplication | driver never calls `blinded()`; `c·beta_hat` = **1.07** / **0.90** | scaled Branch-A duplicate; `c·beta_blind` = **1.0** exactly |
| **D** terminal provenance self-consistent only | execution identity, evidence hash, publication digest and coordinates each changed + re-digested → **ACCEPTED** | each → `TERMINAL_PROVENANCE_MISMATCH` |

---

## C2 — exact event mapping

**Root cause.** `evaluate_replicate` computed `p1_all = all(per_field_p1.values())`
and returned a single `p1_rejected = not p1_all`. `execute_replicate` copied that
one shared dictionary onto all four field records. The counter filtered records
by field but read a value that was a property of the *replicate*.

**Trace, as frozen authority defines it:**

```
analyse_field(field)                     one FieldAnalysis per field
  -> p1_geometry(analysis, condition, artifact)    one EndpointResult per field
  -> per_field[field]["p1_rejected"] = not result.passed
  -> one record per (case, subcondition, replicate, FIELD)
  -> field_event_count(..., field_id, "p1_rejected", R)
  -> classify_size(rejections, 400, alpha_geom)    the FROZEN classifier
```

No new statistical test is derived in the driver: the already-existing field-level
indicator is `p1_geometry`'s own `passed`, and the frozen fail-closed semantic
(a non-ESTIMATED analysis does not pass) makes `not passed` well defined for
every field.

`size_validation_semantics.derived_boundaries.C2` carries `per_field: true` and
`pooling: "FORBIDDEN"`; C3 and C4 carry no such flag. That distinction is now
structural: `p1_rejected` is in `FIELD_LEVEL_EVENTS`, and `field_event_count`
**refuses** any attempt to count a `REPLICATE_LEVEL_EVENTS` member per field.

**Counterexamples (T1), all through the production counter:**

| replicate | per-field counts |
|---|---|
| `[P, R, P, P]` | `[0, 1, 0, 0]` |
| `[R, R, P, P]` | `[1, 1, 0, 0]` |
| `[P, P, P, P]` | `[0, 0, 0, 0]` |
| `[R, R, R, R]` | `[1, 1, 1, 1]` |

and over four replicates with rejections at `theta1, theta1, —, theta3`, the
totals are `{theta0: 0, theta1: 2, theta2: 0, theta3: 1}` — independently
identifiable per field.

**Mandatory diagnostic.** The C2 contract diagnostic and the primary size
classification now read the same per-field counts: both consume
`field_event_count(..., "p1_rejected")`, and the diagnostic's stored evidence
already carries the raw counts it was computed from.

---

## C3 — actual G5 propagation

**Root cause.** `"g5_rejected": None` was a literal in the returned dictionary.

**Repair.** `p1_block_decisions` reads the frozen result rather than recomputing:

```python
rows   = {gate: p_value for gate, _observed, p_value in result.rows}
p_min  = min(rows[g] for g in BLOCK1_GATES)
block1 = p_min < artifact.critical_p_min()     # the STORED critical value
g5     = rows["G5"] < binding.binding.alpha_2  # the contract's OWN alpha_2
```

`p1_geometry` already computed every p-value and the artifact already finalised
its critical `p_min` at calibration time. No statistic, threshold or p-value is
recalculated and no new test is introduced. `e1a_v4/endpoints.py` is an
analysis-bound SCIENTIFIC MODULE and was deliberately **not** modified to expose
the two decisions, because that would move the frozen analysis procedure identity.

Verified: G5 far in the tail → `True` at every field; G5 benign → `False`, not
null. C3's primary release remains Block-2/G5 and its Block-1 interaction remains
a SECONDARY predeclared diagnostic — the repair adds no Block-1 term to C3's
release gate, and the secondary decision is retained rather than nulled.

---

## C4 — actual Block-1 propagation

Same root cause and same repair; `block1_rejected` is the `p_min < critical`
decision. Verified: Block-1 rejecting at one field yields
`[False, True, False, False]`, and ten records containing exactly two Block-1
rejections count **2**.

---

## Fail-closed on a missing decision

`required_endpoint_events(plan, case_id)` derives the owed decisions from the
frozen plan — `uses_p1_block1` and `primary_release_endpoint` — so the schema is
case-aware rather than uniformly nullable:

| case | owes |
|---|---|
| C1–C6 (`uses_p1_block1: true`) | `P1`, `p1_rejected`, `block1_rejected`, `g5_rejected` |
| C1 | `complete_pass` |
| C7 | `false_acceptance` |
| C8 | `scale_recovered` |

`require_endpoint_events` refuses absent or null decisions with
`ENDPOINT_EVENT_MISSING`, and `field_event_count` refuses to score a null as a
non-event. **The one justified absence** is a structured scientific refusal: when
the analysis did not reach ESTIMATED the gate produced no rows, so the two block
decisions do not exist and P1 has already failed closed. That exemption is
explicit, machine-checkable against the record's own `analysis_status`, and the
same absence while ESTIMATED refuses.

---

## C8 — the blinded Branch-A control

**Old implementation, removed.** It took the estimated beta and multiplied it:

```python
scaled = {f: dataclasses.replace(a, beta_hat=a.beta_hat * factor) ...}
p3_absolute(scaled, ...)
```

Under the true null `beta_hat ≈ 1`, so this evaluated to `c` — **1.07** and
**0.90** — which lies outside `delta_abs = 0.05` of 1 and could never pass P3. It
reproduced neither the declared control nor its arithmetic.

**New implementation.** The frozen transform already existed in the scientific
layer and the driver simply never called it. `e1a_v4/branch_a.py` declares
`scale_factor` as "1.0 for primary data; c for the blinded control", `H = H_U ·
scale_factor / (k_B T)`, and `BranchAField.blinded(c)` whose own docstring states
the consequence: *"Under the ideal null the analysis must then recover
beta_hat = 1/c, because beta_hat = m / tr(H_A S) and H_A → c H_A."* **No authority
gap: §17's question is answered by the frozen implementation.**

```
base replicate
  Branch A:  H                          measured field
  Branch B:  X                          observations, generated once
             analyse_field(H,  X)  -> beta_hat        = 1
PAIRED CONTROL, per declared c:
  Branch A': H' = c·H                   BranchAField.blinded(c), a NEW object
  Branch B:  X                          the SAME object, not regenerated
             analyse_field(H', X)  -> beta_hat_blind  = 1/c
  recovery:  c · beta_hat_blind   -> 1
             p3_absolute(beta_tilde)    the frozen rule decides
```

Measured, at every declared field, through the production path:

| c | `beta_hat_blind` | `1/c` | `c · beta_hat_blind` | superseded `c · beta_hat` |
|---|---|---|---|---|
| 1.07 | 0.9345794392523362 | 0.9345794392523364 | **0.9999999999999998** | 1.07 |
| 0.90 | 1.1111111111111107 | 1.1111111111111112 | **0.9999999999999997** | 0.90 |

The duplicates are built inside the per-field loop while the observations are
live, so Branch B is shared object-for-object and no trajectory is retained
beyond its own replicate. `H_U`, `T`, `k_modes` and orientation are untouched;
only the declared scale differs; the primary field is not mutated. Both factors
act on one underlying base replicate, as the frozen `pairing` note requires, and
no separate stream is drawn for either.

**Case-specific (§22).** `SCALE_CONTROL_CASE = "C8_blinded_scale_control"`; any
other case requesting the transform refuses with `SCALE_CONTROL_INVALID`, as does
C8 itself if the blinded analyses are not supplied — which is precisely the old
post-hoc shape.

**Provenance retained:** the transform used, the recovery rule, `branch_b_shared`,
the unblinded estimates, and per branch the `c`, `beta_hat_blind`,
`beta_tilde_recovered`, blinded field ids and the P3 verdict.

**Classifier boundary (§42).** The driver supplies `scale_recovered` from the
actual blinded control; the frozen `classify_campaign` owns the campaign rule
(`cp_lower ≥ 0.90` over R = 200, threshold 188). No control arithmetic moved into
the classifier.

---

## Terminal provenance

`validate_job_record` kept its internal digest **and** gained
`require_terminal_provenance`. Both layers are required and all three anchors are
mandatory — a missing planned job or missing publication refuses rather than
skipping the check.

| link | cross-checked against |
|---|---|
| `contract_sha256`, `plan_sha256`, `seed_map_sha256`, `analysis_procedure_identity`, `execution_identity` | the current `ExecutionBinding` |
| `coordinates`, `job_id`, `result_kind`, `role`, `requires_calibration` | the frozen deterministic planner |
| `branch_a_evidence_sha256`, `publication_digest`, `calibration_condition_sha256` | the **committed** Branch-A publication for those exact coordinates |
| calibration links null for C7 / C8 | the planned job's `requires_calibration` |

Each mutation below was **re-digested** so the record is internally self-consistent
again, and each still refuses with `TERMINAL_PROVENANCE_MISMATCH`: execution
identity, analysis identity, plan identity, seed-map identity, Branch-A evidence
hash, publication digest, job coordinates, `job_id`, `result_kind`, `role`, and an
invented calibration link on a no-calibration case. An edit *without* re-digesting
still refuses on the bytes (`RESULT_SCHEMA_INVALID`), so both layers are live.

## Restart

`inventory_job_records` calls **the same verifier** with the same three anchors;
there is no weaker restart path. A record belonging to no planned job is named as
such before the verifier runs, so the refusal is specific. A terminal record whose
Branch-A evidence has been deleted now refuses with `TERMINAL_PROVENANCE_MISMATCH`
rather than the vaguer inventory code — a strictly more precise refusal for the
same scenario.

---

## Campaign structure

Re-derived from authority, not hard-coded:

| | |
|---|---|
| Planned jobs | **53,200** |
| Calibration artifacts | **46,000** |
| Missing / extra jobs | 0 / 0 |
| C1 / C2 / C3 / C4 | 4,800 / 6,400 / 6,400 / 8,000 |
| C5 / C6 / C7 / C8 | 19,200 / 1,200 / **0** / **0** |

Every per-case calibration count still independently reproduces the case's
declared `calibration_artifact_count`. The repair changes no campaign cardinality.

---

## Outstanding authority gaps — OPEN, not resolved here

Carried forward unchanged from the previous report, plus one found by this repair.

1. **PRNG.** The seed map declares the master seed, family seeds and stream derivation; no frozen document declares the pseudo-random algorithm or the uniform→normal transform.
2. **Branch-A field construction.** `calibration_route`, viscosity η and bead radius *a* are undeclared, and τ_r = γ(T)/k_r with γ = 6πη(T)a makes them set every φ, every effective size and the whole Block-1 null law.
3. **C6 field.** Declared as prose, "synthetic two-mode field at the declared rho"; no machine-readable construction exists.
4. **C8 implementation inputs.** `C8.beta_truth` is the string `"1/c on the blinded branch"`, so the generating beta for the underlying replicate is not machine-readable. *(The C8 scale transform itself is NOT a gap — `BranchAField.blinded` is frozen and is now used.)*
5. **Diagnostic aggregator.** Several mandatory diagnostics are stated only in prose; the driver requires them and refuses rather than reporting an empty one.
6. **NEW — C3 / C4 replicate-level event reduction.** C3 and C4 are scored over replicates (assurance `unit: campaign`, R = 400 and R = 2000) while the two-block gate decides **per field**, and both declare four fields. No frozen document states how four per-field decisions reduce to the one replicate-level event those denominators count. `replicate_level_rejections` refuses with `ENDPOINT_EVENT_REDUCTION_UNDECLARED` rather than choosing between "any field rejects", "the reference field rejects" and "every field rejects", which are different measured sizes. C6 declares one field, so its reduction is unambiguous and is implemented.

Gap 6 is a consequence of repairing C2/C3/C4 honestly: once the per-field events
are real, the question of how they combine can no longer be hidden behind a null.

---

## Scientific authority

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Byte-unchanged and asserted in the suite: physical foundation
`6d9aed24…`, theory baseline `0a01b356…`, design contract `91d6ae76…`,
prospective design `e59dcff6…`, JSON plan `dcb35075…`, Markdown plan `3f4715b4…`,
seed map `95870d7d…`.

**No `SCIENTIFIC_MODULES` entry was modified**, so the analysis procedure identity
is unmoved at `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f`.
§42's stop condition was not triggered. Thresholds, counts, fields, cases,
confidence rules, mandatory diagnostics, seed hierarchy, C7 alternatives, C8 c
factors and the corrected OU generator are untouched.

**New execution identity (DRIVER-PRESENT / UNSEALED, a diagnostic, not a seal):**

```
a2f77bbcfb051fc02a6bbd7a4501e438420c404c07a061261387aa43d6dbbb47
```

Four refusal codes added (55 in the layer): `ENDPOINT_EVENT_MISSING`,
`ENDPOINT_EVENT_REDUCTION_UNDECLARED`, `SCALE_CONTROL_INVALID`,
`TERMINAL_PROVENANCE_MISMATCH`.

---

## Tests

Every suite listed individually; all run, none omitted.

| suite | result | deterministic test trajectories |
|---|---|---|
| **`test_e1a_v4_driver_endpoints.py`** (new) | **122 passed, 0 failed, 9 groups** | **0** (measured) |
| `test_e1a_v4_campaign_driver.py` | 598 passed, 0 failed, 47 groups | **32** (measured; 12,800 samples) |
| `test_e1a_v4_release_authority.py` | 225 passed, 0 failed | 0 |
| `test_e1a_v4_coherence_hardening.py` | 138 passed, 0 failed | 0 |
| `test_e1a_v4_repair.py` | 126 passed, 0 failed | 0 |
| `test_e1a_v4.py` | 122 passed, 0 failed | 0 |
| `test_e1a_v4_case_scope.py` | 113 passed, 0 failed | 0 |
| `test_e1a_v4_plan_coherence.py` | 113 passed, 0 failed | 0 |
| `test_e1a_v4_generating_model.py` | 113 passed, 0 failed | 0 |
| `test_e1a_v4_calibration_scope.py` | 105 passed, 0 failed | 0 |
| `test_e1a_v4_preexec.py` | 104 passed, 0 failed | 0 |
| `test_e1a_v4_size_semantics.py` | 79 passed, 0 failed | 0 |
| `test_e1a_v4_contract_plan.py` | 75 passed, 0 failed | 0 |
| `test_e1a_v4_dispositions.py` | 64 passed, 0 failed | 0 |
| `test_e1a_v4_preexec_corrections.py` | 37 passed, 0 failed | 0 |
| **total** | **2,134 checks, 0 failures** | **32** |

The new suite is fully pure: it generates **no** trajectory at all. Its
observation arrays are written out by hand, laid along each field's own
eigenvectors with semi-axes `sqrt(2/λ_r)` so the sample covariance is exactly
`inv(H)` and the frozen estimator returns exactly 1 at every declared field.
`ou_observations` is never called from it.

The auditor's required counterexamples are all present: C2 one-field rejection is
not four; C3 actual G5 rejections are counted; C4 actual Block-1 rejections are
counted; C8 scaled Branch-A gives `beta_blind ≈ 1/c`; C8 post-hoc multiplication
is refused as a control construction; execution identity, Branch-A hash and
publication digest each refuse after re-digesting; and restart refuses the same
re-digested records.

---

## Execution activity

Measured, in the precise categories the audit asked for:

```
REAL RNG OBJECTS = 0
REAL STOCHASTIC RANDOM DRAWS = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
DETERMINISTIC TEST TRAJECTORIES = 32   (12,800 samples, all in
                                        test_e1a_v4_campaign_driver.py, all from a
                                        deterministic van der Corput supplier
                                        inside temporary sandboxes)
OFFICIAL CAMPAIGN JOBS = 0
REAL CALIBRATION EXECUTIONS = 0
```

The previous report's flat `TRAJECTORIES = 0` was too broad and is corrected here:
`execute_campaign` driven by a deterministic supplier does call `ou_observations`
and does produce synthetic trajectory arrays. That is **software orchestration
testing**, not scientific execution — but it is not "no trajectories", and the
count above is measured by instrumenting `ou_observations`, not estimated.

---

## Lifecycle

```
OFFICIAL CAMPAIGN DRIVER      = PRESENT
DRIVER IMPLEMENTATION AUDIT   = PENDING RE-AUDIT
PRODUCTION RESOLVER           = REFUSES UNDECLARED INPUTS
FINAL EXECUTION SEAL          = NOT FROZEN  (state PRE_DRIVER)
EXPECTED FINAL EXECUTION ID   = NULL
EXECUTION AUTHORISED          = FALSE
VALIDATION CAMPAIGN           = NOT RUN
```

No gate was weakened to make a test easier.

## Next stage

```
BOUNDED DRIVER RE-AUDIT
READY
```

Seal freeze is **not** ready: the six pre-seal authority items above remain open,
and closing them will move the execution identity again.

```
DRIVER ENDPOINT/PROVENANCE REPAIR COMMITTED
```
