# E1a v4 — Binding Embedded Branch-A Identities to Current Package Authority

**Stage.** Bounded driver / provenance correction. Pre-execution.
**Starting HEAD.** `fa99874d6f621e0f7fb6330ec944a64064da9a57`
**Work commit.** `d7bdc658e66b67a35aca8ce8db46164e9b0c6be1`
**Work tree.** `f50708e5f660fdb6a3ca2087daf7be6e7b330d94`
**Branch.** `gaussian/stage-a-environment`. Not pushed.

One auditor blocker, reproduced before any edit, repaired, and locked behind a
permanent programmatic mutation audit.

---

## 1. Auditor blocker — the exact reproduced mismatch

A durably committed Branch-A publication could carry correct **outer**
`package_identities` while the identities **embedded inside** its Branch-A
evidence disagreed with the current frozen package. Each case below changed one
embedded identity, then consistently recomputed the evidence digest, the envelope
digest and the commit marker, and re-digested the calibration lock and the
terminal record so the whole downstream chain agreed:

```text
                                 shared verifier   terminal   restart
embedded analysis_identity       ACCEPT  <-DEFECT  ACCEPT     ACCEPT
embedded contract_sha256         ACCEPT  <-DEFECT  ACCEPT     ACCEPT
embedded plan_sha256             ACCEPT  <-DEFECT  ACCEPT     ACCEPT
embedded evidence schema         BRANCH_A_EVIDENCE_ALTERED (already caught)
embedded generator_identity      ACCEPT  (classification decision -- see §7)
```

The auditor named the first two; the embedded **plan identity** was found by
enumerating the evidence schema and escapes identically.

### Root cause

The recurring shape in this waterfall: **a field written from authority and never
read back against it.** `BranchARealisation.from_branch_a_field` stamps
`contract_sha256`, `plan_sha256` and `analysis_identity` into the evidence from
the binding, and the verifier only ever compared the envelope's *outer*
`package_identities`.

The existing `verify_publication` could not have caught it either, and this is the
important part. It compares the stored evidence against a `BranchARealisation` —
but on the shared-loader path that realisation is rebuilt **from the record** by
`realisation_from_record`, so for every embedded field that round-trips it was
comparing the record with itself. The embedded `schema` was the accidental
exception: `realisation_from_record` does not read it, so `.canonical()` re-stamps
the current constant and the mismatch surfaced. That is a fortunate accident, not
a check, so it is now explicit and cannot regress.

---

## 2. Embedded identity inventory

Every key `BranchARealisation.canonical()` emits — 19 of them — is now classified
in `EMBEDDED_EVIDENCE_CLASSIFICATION`:

| classification | keys | verified how |
|---|---|---|
| `PACKAGE_IDENTITY` | `schema`, `contract_sha256`, `plan_sha256`, `analysis_identity` | against the current binding, by `require_embedded_branch_a_identities` |
| `COORDINATES` | `coordinates`, `field_id` | against the **frozen planned job**, not the record |
| `SEED_IDENTITY` | `branch_a_seed`, `common_mode_seed` | on the realisation path, against the job's declared streams |
| `RECORDED_PROVENANCE` | `generator_identity` | required non-empty string; deliberately not pinned (§7) |
| `SCIENTIFIC` | `H_A`, `T_measured`, `k_modes_measured`, `rot_deg_measured`, `tau_modes`, `scale_factor`, `n_samples`, `dt`, `calibration_route`, `branch_a_status` | evidence digest + existing scientific validation |

`EMBEDDED_PACKAGE_IDENTITY_FIELDS` is **derived** from that mapping, not written
by hand:

```text
('analysis_identity', 'contract_sha256', 'plan_sha256', 'schema')
```

**Why a classification rather than a list.** A hand-maintained list of "identities
to check" goes stale the next time a field is added to the evidence — which is
exactly how this defect arose. A permanent test enumerates `canonical()` and
refuses any key the mapping does not classify, and any classified key the evidence
no longer emits. A new field must be classified to ship. Currently: 19 keys, **0
unclassified, 0 stale.**

`EMBEDDED_TO_OUTER_IDENTITY` records where the envelope restates the same
identity. The two spellings differ for the analysis identity — embedded
`analysis_identity` versus outer `analysis_procedure_identity` — which is
precisely why two independently editable copies of one truth went unnoticed.

---

## 3. Verification hierarchy

```text
current binding  (contract, plan, seed map, analysis identity, execution identity)
      |
      v
verified OUTER publication
      commit transaction            read_committed, marker binds exact bytes
      outer schema strict parse     require_publication_schema
      outer coordinates             == the FROZEN PLANNED JOB's
      embedded shape                presence + type, BEFORE the rebuild
      envelope digest               recomputed
      marker digest                 compared
      basename                      re-derived from coordinates
      evidence digest               recomputed over the stored evidence
      outer package identities      == the current binding
      |
      v
verified EMBEDDED Branch-A evidence          <-- NEW
      embedded identity  == current binding
      embedded identity  == outer envelope
      embedded schema    == envelope schema
      embedded coordinates, field == the frozen planned job
      |
      v
verified calibration lock   (resolves a VERIFIED publication, not a committed one)
      |
      v
terminal record
```

The embedded shape pass runs **before** `realisation_from_record`, so an absent,
null, empty or non-string embedded identity refuses with a coded provenance
failure rather than crashing on a `KeyError` inside the reconstruction.

All of this lives in the **one** shared `verified_publication`, so terminal
validation, restart reconciliation, the calibration-lock verifier and the lock
write path get it identically. There is no terminal-only embedded check.

---

## 4. Mutation audit

Programmatic, over every field the classification marks package-bound. For each:
mutate to a foreign valid-looking value → recompute the evidence digest →
recompute the envelope digest → commit correctly → re-digest the lock and terminal
record → require refusal on all three paths.

```text
embedded identity fields tested   4
refused on every path             4
unexpected passes                 0
```

| embedded field | shared verifier | terminal | restart |
|---|---|---|---|
| `analysis_identity` | `BRANCH_A_PROVENANCE_MISMATCH` | same | same |
| `contract_sha256` | `BRANCH_A_PROVENANCE_MISMATCH` | same | same |
| `plan_sha256` | `BRANCH_A_PROVENANCE_MISMATCH` | same | same |
| `schema` | `BRANCH_A_EVIDENCE_ALTERED` | same | `RESTART_INVENTORY_MISMATCH` |

Absent / null / empty / non-string, for each of the five required embedded fields
(the four package-bound plus `generator_identity`) — 20 cases, all
`PUBLICATION_INCOMPLETE`.

And the harder variant: **both** copies of one identity moved to the same foreign
value, so the record is fully self-consistent *and* disagrees with the binding —
refused for all three of `contract_sha256`, `plan_sha256`, `analysis_identity`
with `BRANCH_A_PROVENANCE_MISMATCH`.

### Downstream consistency cannot launder bad root provenance

Every mutation above was tested with the calibration lock and the terminal record
re-digested to agree with the forged publication. All refuse, because each level
is judged by the level above it and ultimately by frozen authority — never by its
own agreement with its neighbours.

No new refusal codes were added. `BRANCH_A_PROVENANCE_MISMATCH` already meant
"published X != current X; the package changed since publication", which is exactly
this condition. 62 codes, unchanged.

---

## 5. Restart

Wrong embedded identities refuse on the reconciliation path with no terminal
record present:

```text
embedded analysis identity != current   -> BRANCH_A_PROVENANCE_MISMATCH
embedded contract identity != current   -> BRANCH_A_PROVENANCE_MISMATCH
embedded plan identity != current       -> BRANCH_A_PROVENANCE_MISMATCH
```

One mechanical note worth recording: the claimed-realisation set must be the
recovered one for these tests, otherwise an earlier unclaimed-publication check
fires before the publication verifier is reached. The tests use
`recover_realisations` so the refusal genuinely comes from the embedded check.

---

## 6. Positive control and round trip

```text
a publication built by the production constructor
  -> shared verifier ACCEPTS
  -> terminal validation ACCEPTS
  -> restart ACCEPTS

construct -> serialise -> commit -> read
  -> every package identity preserved exactly
  -> the rebuilt realisation round-trips to the same evidence digest
```

**Constructor / verifier agreement** (§18) is asserted field by field: for each
package-bound embedded identity, the value the constructor stamped equals the value
`embedded_identity_expectations(binding)` expects. That is the specific check whose
absence was the root defect.

Nothing normal is rejected: the repair refuses forged provenance, not ordinary
evidence.

---

## 7. `generator_identity` — a recorded classification, not an omission

It is classified `RECORDED_PROVENANCE` and **not pinned**, deliberately, and the
reasoning is asserted by test rather than left implicit:

- frozen authority declares no expected value for it. The plan's
  `generating_model.branch_a` describes the **model** in prose (`"H_A = decorated
  H_true; its OWN seed family branch_a_measurement"`, common mode, per-mode
  stiffness, orientation, thermometry, independence) and contains no
  implementation path;
- the only `generator_identity` the plan declares **anywhere** is
  `calibration.generator_identity = "EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1"`,
  which belongs to calibration, not to Branch-A evidence;
- `BRANCH_A_GENERATOR_IDENTITY` is a driver constant, not plan-declared;
- pinning it would invent a requirement the frozen schema does not state (§17) and
  would forbid the deterministic pre-execution fixtures, which legitimately record
  that the official generator did **not** run.

It is therefore schema-enforced as a required non-empty string, and a different
non-empty value is accepted **by classification, with a stated reason** — not
because it was overlooked.

**Flagged for the authorised stage, not resolved here:** whether frozen authority
should declare an expected Branch-A generator identity, so that official evidence
can be distinguished from fixture evidence by provenance rather than by convention.
That is an authority question, not a verifier repair.

---

## 8. Cleared restart-plan issue — preserved, not reopened

The previous finding remains fixed, and the test suite now re-asserts it in this
group so it cannot silently regress:

```text
verify_restart(planned=None)      -> CAMPAIGN_PLAN_MISMATCH
verify_restart(planned omitted)   -> TypeError
valid partial restart             -> ACCEPTS
```

The restart planned-job architecture was not refactored.

---

## 9. Execution identity

Computed in the required order — implement, test, **commit**, then compute from the
committed tree. Method: `git archive d7bdc658e66b67a35aca8ce8db46164e9b0c6be1` into
a clean temporary directory, then `bind_execution(".")` there. Run twice, identical,
and identical to the working tree.

```text
DRIVER-PRESENT / UNSEALED execution identity
e63fc5c766f9b71a51957e23840650a612516bd14d122ceffbf109f79dd7e675
```

It moved from the pre-repair `2bc09e0ca08273da44b3dd1ed2531955045304794b1de42772c9182ce0918d3b`,
as expected: the driver file is in the preimage.

**NOT FINAL. NOT FROZEN. NOT AN AUTHORISATION.** `driver_state()` is `PRESENT`,
the driver's real file hash is in the preimage, and the execution gate refuses
with `EXECUTION_SEAL_NOT_FROZEN`. The seal's stale display strings remain
**REPORT-ONLY** and were not touched.

| identity | value | moved? |
|---|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | no |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | no |
| plan sha256 | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | no |
| seed map sha256 | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | no |

---

## 10. Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

No file in `SCIENTIFIC_MODULES` (12 entries) was modified — intersection with the
work commit's changed paths: **NONE**. No frozen authority file was touched —
intersection: **NONE**.

Changed files, both:

```text
e1a_v4/validation/campaign_driver.py   the embedded classification, the embedded
                                       verifier, and its wiring into the one
                                       shared verified-publication loader
test_e1a_v4_terminal_calibration.py    group D1
```

The driver diff is purely additive apart from two replaced lines at the wiring
point. No scientific measurement value is compared against the plan: §11 was
respected, and the `SCIENTIFIC` classification exists to make that boundary
explicit rather than incidental.

### Campaign structure

```text
planned jobs            53,200   unchanged
calibration artifacts   46,000   unchanged
```

No changed cases, no changed calibration scopes.

---

## 11. Tests

Pure/static suites only. Each was run under an instrumented `ou_observations`, so
the trajectory column is measured, not assumed.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 216 | 216 | 0 | no (measured 0) |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no (measured 0) |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no (measured 0) |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no (measured 0) |
| **total** | **547** | **547** | **0** | **0 trajectories** |

The terminal-calibration suite grew from 12 groups / 155 checks to **13 groups /
216 checks**, the new group being `D1`. No historical total is reported as rerun;
the ten other E1a suites were not run in this task.

### Deferred trajectory suite

`test_e1a_v4_campaign_driver.py` was **not run and not modified** in this task, per
§28. Verified statically only: it byte-compiles, and all 14 call sites of
`verify_restart`, `inventory_job_records`, `validate_job_record`,
`verify_publication`, `verified_publication` and `publish_calibration_lock` were
parsed from the AST and bound against the current signatures with
`inspect.Signature.bind` — all bind, none fail.

**Its runtime status remains unverified and is not claimed.** KNOWN DEFERRED TEST.

---

## 12. Open issues — listed, not resolved

```text
C3/C4 field-to-replicate reduction   still fails closed with
                                     ENDPOINT_EVENT_REDUCTION_UNDECLARED
PRNG authority                       open
field construction authority         open
C6 implementation inputs             open
remaining C8 implementation inputs   open
diagnostic aggregator authority      open
```

New, raised by this repair and **not** resolved: whether frozen authority should
declare an expected Branch-A `generator_identity` (§7).

**Next stage, NOT begun and NOT authorised.** An independent re-audit of this
embedded-identity correction. The seal stays `PRE_DRIVER`, `execution_authorised`
stays false, and nothing here authorises execution.

---

## 13. Safety

```text
REAL RNG OBJECTS = 0
REAL RANDOM DRAWS = 0
DETERMINISTIC TEST TRAJECTORIES = 0
OFFICIAL CAMPAIGN TRAJECTORIES = 0
CALIBRATION EXECUTIONS = 0
OFFICIAL CAMPAIGN JOBS = 0
```

No results directory exists. The execution seal reports `state: PRE_DRIVER`,
`expected_execution_identity: null`, `execution_authorised: false`,
`random_draws: 0`, `trajectories: 0`.

---

EMBEDDED BRANCH-A IDENTITY REPAIR COMMITTED
