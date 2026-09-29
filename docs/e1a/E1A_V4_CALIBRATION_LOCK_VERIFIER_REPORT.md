# E1a v4 — Removing Caller Trust from Calibration-Lock Verification

**Stage.** Bounded driver / provenance correction. Pre-execution.
**Starting HEAD.** `ac6e8e91c94d9f3522c30da57d39cb62ea53c933`
**Work commit.** `46901dd5a517b670e621f88962dd5ac0010b8246`
**Work tree.** `d1e288fe9257a82a404b95090198eb07ebe55c0e`
**Branch.** `gaussian/stage-a-environment`. Not pushed.

Two auditor blockers, both reproduced before any edit, both repaired, both locked
behind permanent pure counterexamples. Neither was a comparison defect; both were
trust-boundary defects.

---

## 1. Original auditor blockers, reproduced first

### Finding A — the official terminal validator trusted a caller's lock

Fixture: a real planned calibrating job
`C2_geometry_false_rejection | sigma_psi_0p0 | 000000 | theta0_circular`, a real
committed Branch-A publication, and a real durable calibration lock at
`98d1d20545fdbcb0…`. Then a terminal record with
`calibration_artifact_sha256 = a1b2c3d4…` (re-digested), plus a matching
fabricated lock mapping that was **never persisted**.

```text
validate_job_record(tampered terminal, CALLER-SUPPLIED fake lock)
  -> ACCEPTED                                            <-- DEFECT

validate_job_record(tampered terminal, ACTUAL PERSISTED lock)
  -> refused CALIBRATION_ARTIFACT_BINDING_INVALID
```

The comparison logic was already correct. The defect was that the official
validator accepted, as an argument, the very object whose job is to prove the
record.

### Finding B — restart accepted semantically wrong locks before any terminal

Both cases use canonically formed, committed locks written into the campaign's own
store with a valid commit marker and a recomputed `lock_digest`, with **no
terminal record present**.

```text
Case 1  lock at job A's canonical slot, record job_id = job B
        (A = …|theta1_power, B = …|theta0_circular; both legitimate,
         both calibrating)
        verify_restart          -> ACCEPTED              <-- DEFECT
        inventory_job_records   -> ACCEPTED              <-- DEFECT

Case 2  lock at job A's canonical slot, artifact_field_id = theta0_circular
        while job A's field is theta1_power
        verify_restart          -> ACCEPTED              <-- DEFECT
        inventory_job_records   -> ACCEPTED              <-- DEFECT
```

Root cause: the lock's own semantic identity — *which job*, *which field* — was
checked only inside terminal validation. Since Branch-A published + calibration
locked + terminal not yet written is the **ordinary resumable state**, the case
with nothing downstream to catch it was exactly the case left unguarded.

---

## 2. Trust boundary — callers can no longer supply authoritative locks

`validate_job_record` is the official entry point. Its signature is now:

```text
validate_job_record(record, plan, binding, job, output_dir)
```

A caller identifies the campaign output **root**, the planned **job** and the
**record**. It supplies no provenance object at all:

| parameter | present? |
|---|---|
| `lock` | no |
| `publication` | no |
| `expected_artifact_sha256` | no |
| `expected_lock_digest` | no |
| `output_dir` | yes |

The fabricated-lock attack is no longer expressible — passing it raises
`TypeError: validate_job_record() takes 5 positional arguments but 6 were given`
— and the same tampered record through the official path refuses with
`CALIBRATION_ARTIFACT_BINDING_INVALID`.

**The publication was closed along with the lock.** The auditor named the lock;
the publication was caller-supplied by exactly the same mechanism and would have
left an identical hole one step over. Closing only half would have been a defect
an auditor would find next, so both are now resolved from the output root. This
is the one place this repair goes beyond the literal finding, and it adds no
scientific information.

The pure comparison survives, deliberately private (§6):

```text
_compare_terminal_to_verified_lock(record, job, lock, publication, binding)
_require_terminal_links(record, binding, job, publication)
```

`lock` there means a record that has **already** passed the canonical
durable-store verifier. Both are private precisely because being convenient to
unit test is what made the public form dangerous.

---

## 3. Durable lock loading — the exact canonical resolution path

One routine, `verified_calibration_lock(output_dir, job, binding)`:

```text
planned job coordinates (case_id, subcondition_id, replicate_id, scope)
      -> canonical_digest(coordinates)
      -> calibration_locks/calibration_lock_<digest>.json
      -> read_committed(...)            artifact + commit marker, byte-bound
      -> require_calibration_lock_schema(...)
      -> record["coordinates"] == the coordinates it was read for
      -> record["job_id"] == job.job_id
      -> record["artifact_field_id"] == job.coordinates.scope
      -> record["publication_basename"] == publication_basename(coordinates)
      -> committed_publication(output_dir, coordinates)   resolved HERE
      -> branch_a_evidence_sha256 / publication_digest /
         calibration_condition_sha256 all == the committed publication's
      -> package_identities == the current ExecutionBinding
      -> analysis_procedure_identity == the current analysis identity
      -> return the verified record
```

The caller never chooses which file represents the job: the basename is a pure
function of the frozen coordinates. **Store location identity == expected planned
job identity == lock record identity**, or it refuses.

---

## 4. Restart validation — locks are complete objects before any terminal exists

`reconcile_calibration_locks(output_dir, binding, planned)` enumerates the store
itself through `inventory_calibration_locks`, then for every entry:

```text
discovered lock
      -> coordinates from the record, basename must match them
      -> the job must exist in the frozen plan          else UNPLANNED
      -> the job must require calibration               else UNPLANNED
      -> verified_calibration_lock(...)   THE SAME routine terminal validation uses
```

It runs whether or not a terminal record exists. It is called by `verify_restart`
and, before the record loop, by `inventory_job_records`, so no restart entry point
is the weak one. The authoritative universe is the campaign storage root compared
against the frozen planned jobs — never "locks the caller says exist". A caller
cannot invent, omit or replace a lock by manipulating an argument.

**One verifier, not two** (§22). `verified_calibration_lock` is the single
canonical durable-lock routine. Terminal validation, restart reconciliation, the
terminal-record inventory, `lock_calibration`'s read-back and `unblind` all route
through it.

---

## 5. Counterexamples — exact results after the repair

| counterexample | before | after |
|---|---|---|
| fabricated unpersisted lock, passed to the official validator | ACCEPTED | not expressible (`TypeError`) |
| that tampered terminal record, official path | ACCEPTED | `CALIBRATION_ARTIFACT_BINDING_INVALID` |
| other-job committed lock at job A's slot | ACCEPTED | `CALIBRATION_LOCK_JOB_MISMATCH` |
| wrong-field committed lock at job A's slot | ACCEPTED | `CALIBRATION_LOCK_FIELD_MISMATCH` |

Both Finding-B refusals now fire identically through `verify_restart`,
`inventory_job_records`, `reconcile_calibration_locks` and
`verified_calibration_lock` — with no terminal record present.

The full regression matrix, all permanent:

```text
TERMINAL OFFICIAL PATH
  fabricated unpersisted matching lock        -> cannot satisfy validation
  terminal null artifact SHA                  -> REFUSE
  terminal fabricated artifact SHA            -> REFUSE
  terminal malformed SHA (3 forms)            -> REFUSE
  terminal another-field / -replicate /
    -subcondition / -case SHA                 -> REFUSE
  correct SHA, artifact never locked          -> CALIBRATION_LOCK_MISSING
  terminal exact persisted artifact SHA       -> ACCEPT

RESTART PRE-TERMINAL PATH
  job A store entry containing job B lock     -> CALIBRATION_LOCK_JOB_MISMATCH
  job A lock with wrong field                 -> CALIBRATION_LOCK_FIELD_MISMATCH
  unplanned lock                              -> CALIBRATION_LOCK_UNPLANNED
  non-calibrating-job lock (C7, C8)           -> CALIBRATION_LOCK_UNPLANNED
  lock without publication                    -> CALIBRATION_LOCK_WITHOUT_PUBLICATION
  wrong evidence hash / publication digest /
    condition identity / execution identity /
    cited publication basename                -> CALIBRATION_LOCK_PROVENANCE_MISMATCH
  valid publication + exact lock + no terminal -> ACCEPT
```

### Positive controls (mandatory, and they hold)

```text
terminal validation   the untampered record validates through the official path
                      verified_calibration_lock returns this job's own lock
                      the private helper accepts the verified lock

pre-terminal restart  valid publication + exact durable lock + NO terminal
                      -> verify_restart ACCEPTS, calibration_locks_on_disk = 1
                      -> inventory_job_records ACCEPTS
                      -> reconcile_calibration_locks returns the verified lock
```

### Duplicates and aliases (§20)

Structurally prevented, and now asserted: all **46,000** calibrating jobs have
distinct canonical lock filenames, all 53,200 planned jobs map to distinct slots,
and a second committed file holding the same job's lock record refuses with
`CALIBRATION_LOCK_JOB_MISMATCH`. No job can acquire a second valid provenance
history.

### Retained properties (§34)

A lock whose canonical path is obstructed fails; the job stays in
`CALIBRATION_CONDITION_BOUND`, never `CALIBRATION_LOCKED`; `unblind()` refuses
with `JOB_STATE_INVALID`; and no Branch-B seed is reachable
(`BRANCH_B_PREMATURE`). C7 and C8 remain no-calibration paths.

---

## 6. Refusal codes

Six lock-specific codes were added as **subclasses** of the existing
`CalibrationArtifactBindingInvalid`, so every existing `except` clause still
catches them while tests can assert the precise category:

```text
CALIBRATION_LOCK_MISSING
CALIBRATION_LOCK_JOB_MISMATCH
CALIBRATION_LOCK_FIELD_MISMATCH
CALIBRATION_LOCK_UNPLANNED
CALIBRATION_LOCK_WITHOUT_PUBLICATION
CALIBRATION_LOCK_PROVENANCE_MISMATCH
```

`CALIBRATION_ARTIFACT_BINDING_INVALID` is retained with a clean split of meaning:
the umbrella code now means *the terminal record's artifact identity is wrong*
(absent, malformed, or not the locked one); the six new codes mean *the lock
itself is wrong*. 62 codes total.

---

## 7. Lifecycle terminology — the machine is right, the wording was stale

Inspected, as §26 requires, before changing any wording:

| machine-readable behaviour | value |
|---|---|
| driver file exists | `True` |
| `driver_state()` | `PRESENT` |
| driver identity component | the file's sha256, **not** the `ABSENT` sentinel |
| `require_execution_gate` | refuses, `EXECUTION_SEAL_NOT_FROZEN` |

**The lifecycle machine does not assume driver absence.** It detects the driver,
hashes it into the execution identity, and refuses execution for the correct
reason: the expected identity is not yet frozen. Nothing mechanical is wrong, so
per §26 only the reporting wording is corrected here, and no frozen file was
edited to rename a label.

The accurate description of the current state is:

```text
OFFICIAL CAMPAIGN DRIVER   PRESENT, implemented, declared canonically in
                           e1a_v4/validation/driver.py, and hashed into the
                           execution identity
EXECUTION SEAL             NOT FROZEN -- expected_execution_identity is
                           explicitly null, which the machine distinguishes
                           from FORGOTTEN
EXECUTION                  NOT AUTHORISED
```

**Flagged, not changed:** the seal's own descriptive strings are stale in the same
way — `official_campaign_driver_status` still reads `"ABSENT, NOT IMPLEMENTED,
NOT AUDITED"`, and `lifecycle.PRE_DRIVER` still reads `"canonical campaign driver
absent; …"`, as does the `seal.py` module docstring. These are human-readable
descriptions with no mechanical effect: the driver's presence is established by
`driver_exists`, never by these strings, and the seal is deliberately excluded
from the execution-identity preimage. Correcting them is a seal edit and belongs
to the authorised freeze task, not to this two-verifier correction. The state
name `PRE_DRIVER` would be better read as *pre-freeze*.

---

## 8. Current execution identity — recomputed, and a correction

Recomputed after the work commit, from a **clean `git archive` of
`46901dd5a517b670e621f88962dd5ac0010b8246`**, and confirmed identical in the
working tree:

```text
DRIVER-PRESENT / UNSEALED execution identity
dfcb2dc82f5691cf0802f8c19240cb4be7eb44cd660870db52bb4dfd259ddf64
```

**NOT FINAL. NOT FROZEN. NOT AN AUTHORISATION.** It is a diagnostic that moves
whenever the driver or validation layer changes, and it will move again.

| identity | value | moved? |
|---|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | no |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | no |
| plan sha256 | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | no |
| seed map sha256 | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | no |

### Correction to the previous report

The previous report (`E1A_V4_TERMINAL_CALIBRATION_PROVENANCE_REPORT.md`) recorded
the post-repair execution identity as `dd2932d1…`. **That figure was wrong.** The
auditor's `e09f1074…` is correct, and clean archives confirm it exactly:

```text
d9cc149  a2f77bbcfb051fc02a6bbd7a4501e438420c404c07a061261387aa43d6dbbb47
aae616e  e09f1074deed0beafe2192147da9eb4a6ae0d079b390cc821d63e88d052030e7
ac6e8e9  e09f1074deed0beafe2192147da9eb4a6ae0d079b390cc821d63e88d052030e7
```

Cause: the identity was computed from the working tree *before* the final edit to
`campaign_driver.py` (an import-ordering fix) and never recomputed after the
commit. Because the driver's file hash is in the preimage, that edit moved the
identity. The figure was a pre-commit reading reported as a post-commit one. This
report therefore computes the identity from a clean archive of the work commit,
not from the working tree — which is why §27 is right to require it.

---

## 9. Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

No file in `SCIENTIFIC_MODULES` (12 entries) was modified — verified by set
intersection against the work commit's changed paths: **NONE**. No frozen
authority file was touched: physical foundation, theory baseline, prospective
design, design contract, Markdown plan, JSON plan, seed map and execution seal
are all byte-identical — verified by the same intersection: **NONE**.

Changed files, all five:

```text
e1a_v4/validation/campaign_driver.py   the canonical verifier, the reconciler,
                                       the trust boundary, the wiring
e1a_v4/validation/refusals.py          six lock codes as subclasses (62 total)
test_e1a_v4_terminal_calibration.py    both counterexamples + regression matrix
test_e1a_v4_driver_endpoints.py        call sites updated for the new signature
test_e1a_v4_campaign_driver.py         call sites updated for the new signature
```

The frozen plan still yields **53,200 jobs** and **46,000 calibration artifacts**.
C7 and C8 still require no calibration.

---

## 10. Tests — exactly what was run

Per §32, only pure/static provenance suites were run. Each was executed under an
instrumented `ou_observations`, so the trajectory column is measured, not assumed.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 101 | 101 | 0 | no (measured 0) |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no (measured 0) |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no (measured 0) |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no (measured 0) |
| `test_e1a_v4_dispositions.py` | 64 | 64 | 0 | no (measured 0) |
| **total** | **496** | **496** | **0** | **0 trajectories** |

The terminal-calibration suite grew from 7 groups / 58 checks to **10 groups / 101
checks**: `B1` (Finding A, the trust boundary), `B2` (Finding B, locks valid
before any terminal) and `B3` (one verifier, no aliases, ordering preserved).

### Not run, and therefore not claimed

`test_e1a_v4_campaign_driver.py` is **modified but was NOT executed**, because
§32 forbids running the trajectory-bearing suite (it generates 32 deterministic
test trajectories). Its two `validate_job_record` call sites were instead verified
**statically**: the file byte-compiles cleanly, and both call sites were parsed
from the AST and bound against the new signature via `inspect.Signature.bind`,
which both satisfy. Two imports left dead by the change were removed.

**Its runtime status after this change is therefore unverified.** That is a
consequence of the instruction, not an oversight, and it should be executed by
whoever next runs a trajectory-permitting stage. No full-suite total is claimed:
the ten remaining E1a suites were not run in this task.

---

## 11. Open issues — listed, not solved

Untouched by this task, as instructed:

```text
C3/C4 field-to-replicate reduction   still fails closed with
                                     ENDPOINT_EVENT_REDUCTION_UNDECLARED; no
                                     ANY / EVERY / reference-field / per-field
                                     choice was made
PRNG authority                       open
field construction authority         open
C6 implementation inputs             open
remaining C8 implementation inputs   open
diagnostic aggregator authority      open
```

The spent-artifact behaviour is **not** reopened: the auditor classified it
NON-BLOCKING, and no calibration artifact is retained.

**Next stage, NOT begun and NOT authorised.** An independent re-audit of these two
verifier corrections. The seal stays `PRE_DRIVER`, `execution_authorised` stays
false, and nothing here authorises execution.

---

## 12. Safety

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

CALIBRATION LOCK VERIFIER REPAIR COMMITTED
