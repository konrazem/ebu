# E1a v4 — Terminal Records Bound to the Actual Locked Calibration Artifact

**Stage.** Bounded driver/provenance repair. Pre-execution.
**Starting HEAD.** `d9cc1490e30273bced74d81075c3a3ecd7d677ea`
**Work commit.** `aae616e297e72cc215ba6a8583150c655e45e799`
**Work tree.** `d7b9a43c4d6af3a10779544e7b545cbf79b7b301`
**Branch.** `gaussian/stage-a-environment`. Not pushed.

**Execution state at completion.**

| | |
|---|---|
| FINAL EXECUTION SEAL | NOT FROZEN (`state: PRE_DRIVER`, `expected_execution_identity: null`) |
| EXECUTION AUTHORISED | FALSE |
| OFFICIAL CAMPAIGN JOBS | 0 |
| REAL RNG OBJECTS | 0 |
| REAL RANDOM DRAWS | 0 |
| OFFICIAL CAMPAIGN TRAJECTORIES | 0 |
| REAL CALIBRATION EXECUTIONS | 0 |

---

## 1. What this task fixed, and what it did not

An independent audit of the previous repair cleared five targeted checks:

```text
C2 per-field counting                         PASS
C3 G5 propagation                             PASS
C4 Block-1 propagation                        PASS
C8 scaled Branch-A control                    PASS
Branch-A publication linkage                  PASS
```

and left one implementation blocker standing. This task fixed **only** that
blocker.

Deliberately **not** done, as instructed: the open C3/C4 field-to-replicate
reduction rule is still undecided and still refuses by name; the execution seal
is not frozen; execution is not authorised; no trajectory, calibration or
campaign was run.

---

## 2. The auditor's counterexamples, reproduced before editing

Both were reproduced at `d9cc149` with pure deterministic fixtures — a
hand-written calibration artifact whose null draws are all a constant, driven
through the production constructors. No generator was built and no number drawn.

The job is a real calibrating job: `C2_geometry_false_rejection |
sigma_psi_0p0 | 000000 | theta0_circular`, `requires_calibration = True`,
artifact locked at `fb32dfbe3d1c0d6d…`.

```text
BASELINE valid record                             -> accepted (correct)

A. calibration_artifact_sha256 = null      + re-digest -> ACCEPTED   <-- DEFECT
B. calibration_artifact_sha256 = fabricated + re-digest -> ACCEPTED  <-- DEFECT
```

Three further cases escaped the same way and were found while reproducing:

```text
C. the key removed entirely                + re-digest -> ACCEPTED   <-- DEFECT
D. a malformed value ("not-a-sha")         + re-digest -> ACCEPTED   <-- DEFECT
E. another job's genuinely locked digest   + re-digest -> ACCEPTED   <-- DEFECT
```

And on the restart path, with the tampered record durably committed to disk and
reconciled through `inventory_job_records`:

```text
RESTART inventory of a FABRICATED artifact SHA -> ACCEPTED  <-- DEFECT
```

### The root cause was a missing referent, not a missing comparison

Walking the campaign output directory after a successful lock showed why no
comparison could have been written:

```text
branch_a/branch_a_08cfcb2f….json
branch_a/branch_a_08cfcb2f….commit.json
```

That is the whole of it. The adopted campaign-level implementation is
`STREAMING_PER_REPLICATE`, for a stated reason — one artifact carries four gates
× R_cal null draws, and materialising a case's artifacts at once would be tens of
gigabytes — so each artifact is finalised, locked and **spent**. Nothing on disk
recorded the lock. The terminal record was the only witness to its own
calibration, and a record cannot corroborate itself.

This matters scientifically, not clerically. For a Block-1 case the calibration
artifact **is** the threshold the job's P1 decision was taken against. An
unverifiable artifact identity is an unverifiable scientific result.

---

## 3. The repair

### 3.1 The lock became durable evidence

A new committed store, `calibration_locks/`, holds one immutable record per
calibrating job. It is written inside `JobExecution.lock_calibration`, **after**
the ledger registers the lock and **before** the job enters `CALIBRATION_LOCKED`
— therefore before Branch B can be unblinded. The external record of the
threshold exists before anything that could depend on the threshold's value.

It goes through the same two-step transaction as Branch-A evidence
(`publish_transaction`): the artifact, then a commit marker binding its exact
bytes. A record with no marker is an orphan and is refused, never promoted.

The lock record binds the complete chain as **one authenticated object**, so a
reader checks the chain rather than four unrelated fields:

```text
committed Branch-A publication
      -> the CalibrationCondition derived from that published evidence
      -> the artifact calibrated at that condition, and LOCKED
      -> the terminal record that names it
```

The Branch-A evidence hash and the publication digest are copied **from the
committed publication**, not from the caller, so a lock cannot cite evidence that
was never published. Its own `lock_digest` is a `sealed_digest` over everything
but itself.

### 3.2 The external binding verifier

`require_calibration_artifact_binding(record, job, lock, publication, binding)`.

What is authoritative here is **not** the terminal record, which is the object
under test, and **not** a caller-supplied expected digest, which would only move
the question one step. It is the committed lock record for these exact
coordinates.

Two structural properties do most of the work:

- the lock's basename is a pure function of the job coordinates
  (`calibration_lock_{canonical_digest(coordinates)}.json`), so a lock belonging
  to another case, subcondition, replicate or field **cannot be read in this
  one's place**; and
- `committed_calibration_lock` re-checks the coordinates inside the record it
  read, so a misfiled lock refuses rather than being believed.

On top of that: the record's digest must equal the lock's; the record's condition
must equal the lock's; the lock's condition, evidence hash and publication digest
must equal the committed publication's; the locked artifact's field must be this
job's field; and the lock's package identities must be the current ones.

### 3.3 Restart is not the weaker path

`inventory_job_records` and the `execute_campaign` final sweep call the **same**
`validate_job_record`, now with the same three external anchors — the planned
job, the committed publication and the committed lock. There is one threshold
rule and one code path for it.

`verify_restart` additionally reconciles the lock store on the same terms it
reconciles the publication store: `inventory_calibration_locks` discovers every
committed lock independently of any caller argument, and a lock that belongs to
no planned job, belongs to a non-calibrating case, has no committed Branch-A
publication, or is not bound to that publication refuses.

`require_execution_lifecycle` now also requires the lock store to be clean.

### 3.4 C7 and C8 — no calibration requirement was invented

The frozen plan gives `C7_false_bridge` and `C8_blinded_scale_control` no
calibration. The existing rule is preserved unchanged: a non-null
`calibration_condition_sha256` or `calibration_artifact_sha256` on such a record
still refuses with `TERMINAL_PROVENANCE_MISMATCH`.

The new check adds the **other** direction only: a committed calibration lock for
a no-calibration case refuses, because it would be an artifact the case never
needed.

### 3.5 New refusal code

`CalibrationArtifactBindingInvalid` / `CALIBRATION_ARTIFACT_BINDING_INVALID`.
The layer now declares 56 codes.

---

## 4. Verification: every required case

Run against the repaired driver, on the same fixtures that reproduced the defect.
"Another field / replicate / subcondition / case" use digests of artifacts that
were **genuinely locked** by four further real jobs, not invented strings.

| case | result |
|---|---|
| terminal artifact SHA absent | REFUSE |
| terminal artifact SHA null | REFUSE |
| terminal artifact SHA malformed (`"not-a-sha256"`, uppercase hex, 63 digits) | REFUSE |
| terminal artifact SHA fabricated | REFUSE |
| terminal artifact SHA for another field | REFUSE |
| terminal artifact SHA for another replicate | REFUSE |
| terminal artifact SHA for another subcondition | REFUSE |
| terminal artifact SHA for another case | REFUSE |
| correct artifact SHA but artifact not locked | REFUSE |
| correct locked artifact SHA for the exact job | **ACCEPT** |
| C7 / C8 with null artifact SHA and no lock | **ACCEPT** |
| C7 / C8 with a fabricated artifact SHA | REFUSE |
| C7 / C8 with a calibration lock present | REFUSE |

Every refusal is `CALIBRATION_ARTIFACT_BINDING_INVALID` except the two C7/C8
record-side cases, which remain `TERMINAL_PROVENANCE_MISMATCH` — the existing
rule, unchanged.

Restart parity, with the tampered record durably committed and reconciled:

| case | result |
|---|---|
| null artifact SHA, re-digested | REFUSE |
| fabricated artifact SHA, re-digested | REFUSE |
| absent artifact SHA, re-digested | REFUSE |
| another job's locked artifact SHA, re-digested | REFUSE |
| a lock whose Branch-A publication is absent | REFUSE |

Round trip for a valid calibrating record — write, read, verify, restart verify —
preserves the artifact identity exactly, and `verify_restart` reports
`calibration_locks_on_disk: 1`.

---

## 5. Tests

New permanent suite: `test_e1a_v4_terminal_calibration.py`, 56 checks in 7
groups, all pure.

| suite | result |
|---|---|
| `test_e1a_v4_terminal_calibration.py` (new) | 56 passed, 0 failed, 7 groups |
| `test_e1a_v4_driver_endpoints.py` | 122 passed, 0 failed, 9 groups |
| `test_e1a_v4_campaign_driver.py` | 598 passed, 0 failed, 47 groups |
| `test_e1a_v4_calibration_scope.py` | 105 passed, 0 failed |

The remaining twelve E1a suites were also run to confirm no collateral breakage
and all pass: `test_e1a_v4` 122, `_repair` 126, `_dispositions` 64, `_case_scope`
113, `_preexec` 104, `_preexec_corrections` 37, `_plan_coherence` 113,
`_coherence_hardening` 138, `_contract_plan` 75, `_generating_model` 113,
`_release_authority` 225, `_size_semantics` 79.

**Total: 16 suites, 2,190 checks, 0 failures.**

### Trajectory accounting, measured rather than assumed

`ou_observations` was instrumented and each suite run under the counter:

```text
test_e1a_v4_terminal_calibration.py   trajectories = 0     samples = 0
test_e1a_v4_driver_endpoints.py       trajectories = 0     samples = 0
test_e1a_v4_campaign_driver.py        trajectories = 32    samples = 12,800
```

The new suite generates **no trajectory at all** — it produces no observation
array, so `ou_observations` is never reached. The 32 in the campaign-driver suite
are pre-existing deterministic test trajectories driven by a van der Corput
supplier inside temporary sandboxes; this repair neither added nor removed one.
They are **software orchestration testing, not scientific execution**, and they
are counted here rather than folded into a flat zero.

Two fixture facts worth recording, because both were the code working correctly:

- Identical hand-written artifacts hash identically, and the ledger refused the
  second with `CALIBRATION_REUSE_REFUSED` — under `REPLICATE_CONDITIONAL`
  calibration an identical digest is not permission to share an artifact. The
  fixtures were made distinct.
- A lock record rewritten in place and re-digested under its unchanged commit
  marker refuses with `PUBLICATION_INCOMPLETE` ("the bytes changed after the
  publication was committed"), not a new code. The existing transaction layer
  already covers that.

---

## 6. Scientific files unchanged

No file in `SCIENTIFIC_MODULES` (12 entries) was modified. Verified by set
intersection against the commit's changed paths: **NONE**.

| identity | value | moved? |
|---|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | no |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | no |
| plan sha256 | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | no |
| seed map sha256 | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | no |
| execution identity | `dd2932d1d27e47dc3eafc49357c69c8bf5429e9c720323f9c411c1bad50392d6` | yes — the driver changed |

The execution identity moving is expected and harmless: it is a hash over the
driver package, the seal's `expected_execution_identity` is still `null`
(deliberately not yet frozen), and freezing it is a later authorised stage.

Untouched: foundation, baseline, prospective design, design contract, Markdown
plan, JSON plan, seed map, release criteria, case definitions, and the C2 / C3 /
C4 / C8 semantics. The frozen plan still yields **53,200 jobs** and **46,000
calibration artifacts**, and the driver still agrees with it in both directions.

No frozen document declares the campaign output directory layout, so adding a
store is not a plan change.

Changed files, all four tracked plus one new:

```text
e1a_v4/validation/campaign_driver.py    the lock store, its verifier, the wiring
e1a_v4/validation/refusals.py           one new coded refusal (56 total)
test_e1a_v4_campaign_driver.py          call sites updated for the new argument
test_e1a_v4_driver_endpoints.py         call sites updated for the new argument
test_e1a_v4_terminal_calibration.py     NEW permanent regression suite
```

---

## 7. Limitations and what remains open

**The binding is exactly as strong as the commit transaction.** The repair proves
that a terminal record names the artifact recorded as locked for its coordinates,
in a record written before unblinding, bound to the committed Branch-A
publication, and authenticated by its own digest and its commit marker's byte
hash. It does **not** make the calibration artifact itself recoverable — under
`STREAMING_PER_REPLICATE` the artifact is spent by design, for the stated size
reason — so the lock record, not the artifact, is the terminus of the chain. An
adversary with write access to a committed store before reconciliation remains
outside what this layer can detect, exactly as for Branch-A publications.

**Six pre-seal authority gaps remain OPEN and were deliberately not resolved**,
per the task's explicit instruction. In particular the one the previous repair
discovered is untouched: C3 and C4 are scored over *replicates* (assurance
`unit: campaign`, R = 400 and R = 2000) while the two-block P1 gate decides *per
field*, and both cases declare four fields. No frozen document states how four
per-field decisions reduce to the one replicate-level event those denominators
count, so `replicate_level_rejections` still refuses with
`ENDPOINT_EVENT_REDUCTION_UNDECLARED` rather than choosing between "any field
rejects", "the reference field rejects" and "every field rejects". C6 declares
one field, so its reduction is unambiguous and is implemented.

The other open gaps — PRNG authority, field construction, C6, C8 input, and the
per-case mandatory diagnostic aggregator — are unchanged by this task.

**Next stage, NOT begun and NOT authorised.** A further bounded driver re-audit.
The seal stays `PRE_DRIVER`, `execution_authorised` stays false, and nothing here
authorises execution.

---

TERMINAL CALIBRATION PROVENANCE COMMITTED
