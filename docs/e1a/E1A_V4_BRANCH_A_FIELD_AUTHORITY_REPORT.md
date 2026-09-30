# E1a v4 — Complete Embedded Branch-A Field Authority Verification

**Stage.** Bounded driver / provenance correction. Pre-execution.
**Starting HEAD.** `4f648819f92ec2a83f2370386e938229180b5088`
**Work commit.** `da81d29e465c14386fc0aed8d8285e8568fafee7`
**Work tree.** `aecdfff845f96e9cc78ddb528b8e9c18d001402c`
**Branch.** `gaussian/stage-a-environment`. Not pushed.

---

## 1. Auditor blocker — digest authenticity is not authority conformance

```text
a digest answers      "were these exact bytes saved, unaltered?"
it does NOT answer    "does this value agree with the frozen job, the seed map,
                       the validation plan and the design contract?"
```

The previous repair bound the embedded **package** identities to the current
binding and classified everything else as `SCIENTIFIC` — a catch-all. Several of
those values are fixed **externally**. Each case below is a correctly committed
publication with the evidence digest, the envelope digest, the calibration lock
and the terminal record all consistently recomputed, so nothing local can tell:

| forged embedded value | shared verifier | terminal | restart |
|---|---|---|---|
| another planned job's **genuine** Branch-A seed | ACCEPT ← DEFECT | ACCEPT | ACCEPT |
| another subcondition's **genuine** common-mode stream | ACCEPT ← DEFECT | ACCEPT | ACCEPT |
| `n_samples` 2,000,000 → 2,000,001 | ACCEPT ← DEFECT | ACCEPT | ACCEPT |
| `dt` doubled | ACCEPT ← DEFECT | ACCEPT | ACCEPT |
| calibration route → the contract's **forbidden** equipartition route | ACCEPT ← DEFECT | ACCEPT | ACCEPT |
| `branch_a_status` → an invented value | ACCEPT ← DEFECT | ACCEPT | ACCEPT |

The last was found by enumerating the schema rather than named by the auditor.

**The asymmetry was the defect.** Seed correctness was checked when evidence was
CREATED (`realise_branch_a` compares against the replicate's boundary) and never
when it was RECOVERED. A read path that trusts what a write path proved is not a
verifier.

---

## 2. Complete embedded-field inventory

`BRANCH_A_FIELD_AUTHORITY` — one row per field, declaring meaning, authority
class, authority source and verification rule. The verifier **dispatches on the
table**; it never branches on field names.

| field | meaning | class | authority source | rule |
|---|---|---|---|---|
| `schema` | frozen publication schema | PACKAGE_BOUND | `BRANCH_A_PUBLICATION_SCHEMA` | equals expected |
| `contract_sha256` | contract it was produced under | PACKAGE_BOUND | `binding.binding.sha256` | equals expected |
| `plan_sha256` | plan it was produced under | PACKAGE_BOUND | `binding.plan_sha256` | equals expected |
| `analysis_identity` | analysis procedure identity | PACKAGE_BOUND | `binding.analysis_identity` | equals expected |
| `coordinates` | complete scientific address | JOB_BOUND | the frozen planner | equals expected |
| `field_id` | field/scope measured | JOB_BOUND | `job.coordinates.scope` | equals expected |
| `branch_a_seed` | per-field Branch-A stream | SEED_BOUND | `CaseSeedAccess.stream(branch_a_measurement, sub, replicate, scope)` | equals expected |
| `common_mode_seed` | ONE per experiment, SHARED across a replicate's fields | SEED_BOUND | `CaseSeedAccess.stream(..., EXPERIMENT_SCOPE)` | equals expected |
| `dt` | Branch-B sampling interval — a plan PRIMITIVE | PLAN_BOUND | `plan.generating_model.branch_b.dt_s` | equals expected |
| `calibration_route` | how Branch-A stiffness was calibrated | CONTRACT_BOUND | contract `authorised_branch_A_routes` / `forbidden_branch_A_routes` | contract route |
| `n_samples` | Branch-B record length | DERIVED | `int(round(T_total_s / dt_s))` via the plan layer's own `derived_n_samples` | equals expected |
| `branch_a_status` | whether the realised field is usable | DERIVED | `BranchAField.status`, closed set of two | status enum |
| `tau_modes` | `tau_r = gamma / k_r`, carried with ASCENDING k | DERIVED | the frozen pairing rule | tau pairing |
| `H_A` | realised Branch-A stiffness matrix | MEASURED | realised measurement | float matrix |
| `T_measured` | measured temperature, thermometry error | MEASURED | realised measurement | float |
| `k_modes_measured` | measured per-mode stiffnesses | MEASURED | realised measurement | float list |
| `rot_deg_measured` | measured trap-axis orientation | MEASURED | realised measurement | float |
| `scale_factor` | declared scale AFTER the common-mode perturbation | MEASURED | realised measurement | float |
| `generator_identity` | which code produced the measurement | OPEN_UNRESOLVED | **not declared** by frozen authority | non-empty string |

An embedded key the table does not declare is refused outright as an
unauthenticated channel.

---

## 3. Authority-class counts (machine-derived)

From `authority_class_counts()`, never hard-coded:

```text
total              19
PACKAGE_BOUND       4
JOB_BOUND           2
SEED_BOUND          2
PLAN_BOUND          1
CONTRACT_BOUND      1
DERIVED             3
MEASURED            5
OPEN_UNRESOLVED     1
unclassified        0
```

A permanent test requires the table to cover **exactly** the keys
`BranchARealisation.canonical()` emits — no unclassified key, no stale row — so a
new field must be classified to ship.

`EXTERNALLY_BOUND_EMBEDDED_FIELDS` (13) is derived from the table, not listed by
hand, and is what the mutation audit iterates.

---

## 4. Seeds — verified on read, through the frozen interface

```text
branch_a_seed      == CaseSeedAccess.stream(BRANCH_A_MEASUREMENT,
                        subcondition, replicate, scope)
common_mode_seed   == CaseSeedAccess.stream(BRANCH_A_MEASUREMENT,
                        subcondition, replicate, EXPERIMENT_SCOPE)
```

No seed arithmetic happens in the driver and no generator is constructed:
`CaseSeedAccess.stream` is the frozen authorisation boundary and is the only
route to a stream identity.

**The intentional sharing is preserved and asserted.** Within one replicate the
per-field Branch-A streams differ while the common-mode stream is identical
across fields — which is why it cancels in the P2 ratio and not in P3. The
verifier accepts that sharing rather than demanding a per-field common mode.

**Cross-job substitution refuses.** Another field's *genuine, authorised* seed
placed in this job's publication → `BRANCH_A_PROVENANCE_MISMATCH`. That is a
stronger probe than random garbage: the value is real somewhere, so only a
coordinate-specific check can tell.

---

## 5. Generating model — plan-bound and derived

`dt` is a plan **primitive**, read from the validated plan representation, never
from a literal in driver code. A doubled `dt` refuses.

`n_samples` is **DERIVED**, and this was determined from the repository rather
than guessed: the plan-coherence surface map already declares
`branch_b.n_samples` as `DERIVED: e1a_v4.world.World.n_samples is
int(round(T_total / dt))`, and `derived_n_samples` already exists. The verifier
calls that function, so the driver does not define the derivation. `2,000,001`
refuses; `240.0 / 0.00012 = 2,000,000` is the authority.

`tau_modes` is DERIVED with a stated limit: its absolute values depend on
`gamma = 6 pi eta a`, whose inputs are the **acknowledged-open
field-construction gap**, so only the frozen pairing and arity are verifiable
here. Reversing the taus to non-decreasing order — the same multiset, broken
pairing — refuses, because `tau_r = gamma / k_r` with ascending k gives a
non-increasing sequence, and a mispaired tau changes every `phi` and the whole
Block-1 null law. Resolving gamma's authority is **not** attempted.

---

## 6. Calibration route — contract-bound, both directions

Taken from the contract, not encoded as a one-off string:

```text
authorised:  force_displacement_with_stokes_drag,
             independent_calibrated_thermometry
forbidden:   power_spectrum_stiffness_calibration,
             corner_frequency_fluctuation_spectrum_route_k_equals_2pi_fc_gamma,
             equipartition_k_equals_kBT_over_sigma_squared
```

Rule: in `authorised` **and** not in `forbidden`, exactly as `build_field`
enforces on the creation path. Tested: every authorised route ACCEPTS, every one
of the three forbidden routes REFUSES, and a route on neither list REFUSES
(closed world).

---

## 7. Measured fields — observations, not expected constants

`H_A`, `T_measured`, `k_modes_measured`, `rot_deg_measured`, `scale_factor`.

No expectation is derived for any of them, and a test asserts that: none appears
in `embedded_authority_expectations`. Their guarantees are the schema and
canonical encoding, the evidence digest, the scientific coordinates, and the
existing scientific validation.

Two classifications here needed checking rather than assuming:

- **`scale_factor` is MEASURED, not the constant 1.0.** `BranchAErrorModel.measure`
  returns `scale_factor * (1 + sigma_cm * common_mode)`, so the common mode
  perturbs it. Pinning it to 1.0 would have rejected real measurements.
- **`branch_a_status` is closed-world over two values, not required to be `VALID`.**
  A realised field that fails its own validity check becomes `BRANCH_A_INVALID`,
  and publishing one is legitimate — the analysis then fails closed and that
  refusal is a scientific RESULT.

Confirmed by test: measured temperatures genuinely differ across the contract
fields and all verify; a *different* measured temperature is accepted; a
*malformed* one refuses.

---

## 8. Open unresolved fields

| field | why authority is unresolved | which decision must resolve it |
|---|---|---|
| `generator_identity` | Frozen authority declares no expected value. `generating_model.branch_a` describes the MODEL in prose; the only `generator_identity` the plan declares anywhere belongs to **calibration** (`EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1`). `BRANCH_A_GENERATOR_IDENTITY` is a driver constant, not plan-declared. | A pre-seal authority decision: whether the frozen contract or plan should declare an expected Branch-A generator identity, so official evidence is distinguishable from fixture evidence by provenance rather than convention. **Not made here.** |

It is required to be a non-empty string; no expectation is invented, the field is
not removed, and it is not pretended to be measured. A different non-empty value
is accepted *by classification, with a stated reason*.

Related and also untouched: `UNDECLARED_FIELD_INPUTS` (calibration route,
viscosity, bead radius as *construction* inputs) remains the open
field-construction gap, which is why `tau_modes` values cannot be recomputed.

---

## 9. Mutation audit

Every externally bound field, forged to a valid-looking different value, with the
evidence digest, envelope digest, lock and terminal record all re-digested, then
required to refuse on all three paths.

```text
externally bound fields tested   13
authority classes covered         6   PACKAGE_BOUND 4, JOB_BOUND 2,
                                      SEED_BOUND 2, PLAN_BOUND 1,
                                      CONTRACT_BOUND 1, DERIVED 3
unexpected passes                 0
```

Coverage is asserted, not assumed: the mutation set must equal
`EXTERNALLY_BOUND_EMBEDDED_FIELDS`, so a newly bound field nobody wrote a
mutation for fails the suite rather than being skipped.

Downstream re-digesting launders nothing. Each level is judged by the level above
and ultimately by frozen authority, never by its own agreement with its
neighbours.

---

## 10. Read-path coverage

All official consumers route through the one shared `verified_publication`:

```text
validate_job_record            terminal validation
verified_calibration_lock      resolves a VERIFIED publication, not a committed one
reconcile_calibration_locks    restart, via the same lock verifier
verify_restart                 every publication in the store, plus the claimed ones
inventory_job_records          via validate_job_record
publish_calibration_lock       the lock write path
JobExecution.unblind           via verified_calibration_lock
```

There is no weaker parallel path.

---

## 11. Positive controls

```text
production constructor, EVERY contract field (theta0..theta3)
  -> shared verifier ACCEPTS
  -> terminal validation ACCEPTS
  -> restart ACCEPTS

constructor source == verifier expectation, field by field, for all 11
  fields with a derived expectation
```

Previously cleared checks re-asserted, not regressed: embedded contract, plan,
analysis and schema identities; `planned` required on restart; `planned=None`
refuses; omission is a `TypeError`; wrong-job and wrong-field locks refuse
pre-terminal; valid partial restart accepts.

---

## 12. Execution identity

Computed after the work commit, from a clean `git archive` of
`da81d29e465c14386fc0aed8d8285e8568fafee7`, run twice, identical:

```text
DRIVER-PRESENT / UNSEALED execution identity
6887239f4afc5c8bae3c8fcb67810a8107e054f0384c119e8d29b8c819e77575
```

Moved from the pre-repair `e63fc5c766f9b71a51957e23840650a612516bd14d122ceffbf109f79dd7e675`,
as expected. **NOT FINAL. NOT FROZEN. NOT AN AUTHORISATION.**

| identity | value | moved? |
|---|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | no |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | no |
| plan sha256 | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | no |
| seed map sha256 | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | no |

---

## 13. Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

No `SCIENTIFIC_MODULES` entry modified — intersection with the work commit's
changed paths: **NONE**. No frozen authority file touched — **NONE**. This task
*reads* the contract, plan and seed map; it modifies none of them. No new refusal
codes; 62 total, unchanged.

```text
planned jobs            53,200   unchanged
calibration artifacts   46,000   unchanged
```

Changed files, all three:

```text
e1a_v4/validation/campaign_driver.py   the authority table, the dispatching
                                       verifier, and its wiring
test_e1a_v4_terminal_calibration.py    group E1; D1 updated for the new API
test_e1a_v4_driver_endpoints.py        MovedBinding gains case_access, since the
                                       verifier now consults the seed map
```

---

## 14. Tests

Pure/static only, each run under an instrumented `ou_observations`.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 316 | 316 | 0 | no (measured 0) |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no (measured 0) |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no (measured 0) |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no (measured 0) |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | no (measured 0) |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | no (measured 0) |
| **total** | **898** | **898** | **0** | **0 trajectories** |

The terminal-calibration suite grew from 13 groups / 222 checks to **14 groups /
316 checks**, the new group being `E1`. No historical total is reported as rerun.

### Deferred trajectory suite

`test_e1a_v4_campaign_driver.py` was **not run and not modified**. Verified
statically: it byte-compiles, all 14 call sites of the changed functions bind
against current signatures via `inspect.Signature.bind`, and it holds no
reference to any removed helper. **Runtime status unverified and not claimed —
KNOWN DEFERRED TEST.**

---

## 15. Open later stages — listed, not resolved

```text
generator identity authority          open (classified OPEN_UNRESOLVED)
C3/C4 field-to-replicate reduction    open, still fails closed
PRNG authority                        open
field construction authority          open (gamma: eta, a)
C6 implementation inputs              open
remaining C8 implementation inputs    open
diagnostic aggregator authority       open
```

**Next stage, NOT begun and NOT authorised.** An independent re-audit. The seal
stays `PRE_DRIVER`, `execution_authorised` stays false.

---

## 16. Safety

```text
REAL RNG OBJECTS = 0
REAL RANDOM DRAWS = 0
DETERMINISTIC TEST TRAJECTORIES = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
CALIBRATION EXECUTIONS = 0
OFFICIAL CAMPAIGN JOBS = 0
```

No results directory exists. The seal reports `state: PRE_DRIVER`,
`expected_execution_identity: null`, `execution_authorised: false`,
`random_draws: 0`, `trajectories: 0`.

---

BRANCH-A FIELD AUTHORITY REPAIR COMMITTED
