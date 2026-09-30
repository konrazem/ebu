# E1a v4 — Finalizing Persisted Publication and Restart Provenance Verification

**Stage.** Bounded driver / provenance correction. Pre-execution.
**Starting HEAD.** `fb21c6e9c42a5fda3155e6a613b77cc10b44b746`
**Work commit.** `92565f2eb293e1364149ace7ca5d22324f51b574`
**Work tree.** `51f75a16fb4f5afd16f8e9a33d2304fdad1e7275`
**Branch.** `gaussian/stage-a-environment`. Not pushed.

Two auditor blockers, both reproduced before any edit, both repaired, both locked
behind permanent pure counterexamples.

---

## 1. Findings reproduced

### Finding A — a durably committed publication was trusted without being verified

The previous repair made terminal validation resolve the Branch-A publication
from the store itself, which closed the caller-trust hole. But it resolved it
through `committed_publication`, which proves only the commit transaction. The
full `verify_publication` was never run on that path.

Each case below was committed into a real store through the real transaction, and
then the lock and the terminal record were re-digested so the **entire downstream
chain agreed with the forgery**:

```text
A1  invalid publication schema                    -> ACCEPTED   <-- DEFECT
A2  false package/execution identity              -> ACCEPTED   <-- DEFECT
A2b false analysis procedure identity             -> ACCEPTED   <-- DEFECT
A3  unknown extra field in the envelope           -> ACCEPTED   <-- DEFECT
A4  published state not BRANCH_A_PUBLISHED        -> ACCEPTED   <-- DEFECT
```

Every one of these *is* case A3 in the task's numbering: the chain
`invalid publication → consistent lock → consistent terminal` was forged in all
five, and all five were accepted.

### Finding B — `planned=None` silently disabled semantic reconciliation

```text
lock at job A's canonical slot, record job_id = job B
(both A and B legitimate planned calibrating jobs, no terminal record)

  verify_restart(planned=<full plan>)  -> CALIBRATION_LOCK_JOB_MISMATCH
  verify_restart(planned=None)         -> ACCEPTED   <-- DEFECT
  verify_restart(planned omitted)      -> ACCEPTED   <-- DEFECT

lock at job A's canonical slot, wrong field, no terminal record

  verify_restart(planned=<full plan>)  -> CALIBRATION_LOCK_FIELD_MISMATCH
  verify_restart(planned=None)         -> ACCEPTED   <-- DEFECT
```

---

## 2. Publication verification — commit verification is not publication validation

The two answer different questions, and the official path needs both:

```text
commit verification        "were these exact bytes durably committed?"
publication verification   "is this committed record a VALID Branch-A
                            publication, for this exact planned job, under the
                            current execution package?"
```

`verified_publication(output_dir, job, binding)` is the one canonical loader:

```text
planned job coordinates
      -> canonical path  branch_a/branch_a_<canonical_digest(coordinates)>.json
      -> read_committed(...)              commit transaction, byte-bound marker
      -> require_publication_schema(...)  STRICT PARSE, before any field is read
      -> record["coordinates"] == the PLANNED job's coordinates
      -> verify_publication(...)          the complete existing verifier
      -> return the verified record
```

Two design points worth stating.

**Nothing about publication validity is reimplemented.** The heavy lifting is
delegated to the existing `verify_publication` — the same routine the unblind path
and restart already used — which recomputes the envelope digest, compares the
marker digest, re-derives the basename, recomputes the evidence digest and
compares all five package identities against the current binding.

**The planned-job coordinate check cannot be delegated.** `verify_publication`
compares the record against a `BranchARealisation`, and on this path the only
available realisation is rebuilt *from the record*, so its coordinate check would
compare the record with itself. `verified_publication` therefore checks
`record["coordinates"]` against the frozen planner independently, before
delegating.

---

## 3. Terminal chain

```text
canonical planned job (frozen planner) + current execution package
      -> verified_publication(...)          full verification, not just commit
      -> verified_calibration_lock(...)     which itself resolves a VERIFIED
                                            publication, not a committed one
      -> cross-check lock against verified publication
      -> cross-check terminal record against verified upstream provenance
```

The hierarchy runs one way only. Internal consistency downstream cannot legalise
invalid upstream provenance, because each level is judged by the level above it
and ultimately by frozen authority, never by its own agreement with its
neighbours.

`publish_calibration_lock` was also moved onto the verified loader and now takes
the planned job rather than bare coordinates: a lock is a statement about the
evidence it is conditional on, so that evidence is proven valid before the lock
cites it.

---

## 4. Restart — semantic reconciliation cannot be switched off

`planned` is now **required** on both restart entry points, `verify_restart` and
`inventory_job_records`. Every `if planned is not None:` bypass is gone.

`require_authentic_plan(binding, planned, what)` then checks the supplied list
against `canonical_plan(binding)` — `plan_campaign` memoised on the plan digest,
so there is no second planner:

```text
planned=None                               -> CAMPAIGN_PLAN_MISMATCH
planned omitted                            -> TypeError
a job the frozen planner never produced    -> CAMPAIGN_PLAN_MISMATCH
a descriptor with edited coordinates,
  role, calibration requirement, seed
  families or result kind                  -> CAMPAIGN_PLAN_MISMATCH
a job listed twice                         -> CAMPAIGN_PLAN_MISMATCH
a SUBSET of the canonical plan             -> ACCEPTED, deliberately
```

**Why a subset is still allowed.** The campaign supports running part of the plan,
and omitting a job makes reconciliation *stricter*, not weaker: a persisted object
whose job is not listed refuses as `CALIBRATION_LOCK_UNPLANNED` or
`RESTART_INVENTORY_MISMATCH`. Nothing can be hidden by leaving it out. What is
refused is a descriptor that is not the frozen planner's, because that is what
could legalise a bad object.

`verify_restart` now also runs `verified_publication` over **every** publication
in the store, not only the ones a caller claims. Claimed ones additionally get
`verify_publication` against the evidence in hand, which proves something the
store alone cannot: that the evidence held is the evidence published.

### Default API semantics, stated exactly

| call | result |
|---|---|
| `verify_restart(out, realisations, binding, jobs)` | reconciles against those jobs, after checking they are the frozen planner's |
| `verify_restart(out, realisations, binding, None)` | `CAMPAIGN_PLAN_MISMATCH` |
| `verify_restart(out, realisations, binding)` | `TypeError` — no default exists |
| `inventory_job_records(out, binding, None)` | `CAMPAIGN_PLAN_MISMATCH` |
| `inventory_job_records(out, binding)` | `TypeError` |

There is no structural-inventory-only success path.

---

## 5. Counterexamples — exact results after the repair

Publication mutations, each durably committed with the whole downstream chain
re-digested, checked through the official terminal validator:

| mutation | refusal |
|---|---|
| invalid publication schema | `PUBLICATION_INCOMPLETE` |
| state not `BRANCH_A_PUBLISHED` | `PUBLICATION_INCOMPLETE` |
| unknown extra field in the envelope | `PUBLICATION_INCOMPLETE` |
| a declared field removed | `PUBLICATION_INCOMPLETE` |
| `not_execution_authorisation` false | `PUBLICATION_INCOMPLETE` |
| false execution identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| false analysis procedure identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| false contract identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| false plan identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| false seed-map identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| wrong case | `BRANCH_A_PROVENANCE_MISMATCH` |
| wrong subcondition | `BRANCH_A_PROVENANCE_MISMATCH` |
| wrong replicate | `BRANCH_A_PROVENANCE_MISMATCH` |
| wrong field/scope | `BRANCH_A_PROVENANCE_MISMATCH` |
| wrong evidence digest | `BRANCH_A_EVIDENCE_ALTERED` |

Every one of these is also refused on the restart path.

**Pinned, because it is the class that used to be invisible.** The package-identity
forgeries pass every structural check — the store still recovers them, and nothing
about their bytes can tell. They are refused inside `verify_restart` by the
publication verifier itself, with `BRANCH_A_PROVENANCE_MISMATCH`, not by an
earlier layer. That is asserted explicitly rather than inferred.

Restart plan requirements:

| case | refusal |
|---|---|
| wrong-job lock, canonical plan | `CALIBRATION_LOCK_JOB_MISMATCH` |
| wrong-job lock, `planned=None` | `CAMPAIGN_PLAN_MISMATCH` |
| wrong-job lock, `planned` omitted | `TypeError` |
| wrong-field lock, canonical plan | `CALIBRATION_LOCK_FIELD_MISMATCH` |
| wrong-field lock, `planned=None` | `CAMPAIGN_PLAN_MISMATCH` |
| terminal-record inventory, `planned=None` | `CAMPAIGN_PLAN_MISMATCH` |
| forged descriptor (calibration requirement edited) | `CAMPAIGN_PLAN_MISMATCH` |
| job the planner never produced | `CAMPAIGN_PLAN_MISMATCH` |

All of these hold with **no terminal record present**.

---

## 6. Positive controls

Mandatory, and they hold. A repair that refuses everything is not a repair.

```text
valid publication + valid lock + NO terminal record
  -> verify_restart ACCEPTS
     verified_publications 1, publications_on_disk 1, calibration_locks_on_disk 1
  -> inventory_job_records ACCEPTS
  -> reconcile_calibration_locks returns the verified lock

valid publication + valid lock + valid terminal record
  -> validate_job_record ACCEPTS
  -> verify_restart ACCEPTS
  -> inventory_job_records ACCEPTS

a job with no publication at all
  -> verified_publication returns None, not a refusal

a SUBSET of the canonical plan
  -> ACCEPTED
```

Restart is not over-repaired into requiring terminal completion: Branch-A
published, calibration locked, terminal not yet written remains an ordinary
resumable state.

---

## 7. One expectation moved, and it is strictly more precise

A terminal record checked under a moved execution package now refuses with
`BRANCH_A_PROVENANCE_MISMATCH` instead of `TERMINAL_PROVENANCE_MISMATCH`. That is
the new hierarchy working: the committed publication is verified against the
current package *before* the terminal record is judged, so the refusal names the
upstream object where the disagreement actually is. Nothing was weakened; the
record is still refused.

---

## 8. Execution identity

Computed in the order §24 requires — implement, check, **commit**, then compute
from the committed tree:

```text
DRIVER-PRESENT / UNSEALED execution identity
2bc09e0ca08273da44b3dd1ed2531955045304794b1de42772c9182ce0918d3b
```

**Method.** `git archive 92565f2eb293e1364149ace7ca5d22324f51b574` into a clean
temporary directory, then `bind_execution(".")` there. Run twice, identical both
times, and identical to the working tree. It was not read from a dirty tree and
reported as a committed value — which is exactly the mistake the previous report
made and disclosed.

**NOT FINAL. NOT FROZEN. NOT AN AUTHORISATION.** It moves whenever the driver or
validation layer changes, and it will move again.

| identity | value | moved? |
|---|---|---|
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | no |
| contract sha256 | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | no |
| plan sha256 | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | no |
| seed map sha256 | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | no |

`driver_state()` is `PRESENT` and the driver's real file hash, not the `ABSENT`
sentinel, is in the preimage. The execution gate refuses with
`EXECUTION_SEAL_NOT_FROZEN`. The seal's stale display strings remain
**REPORT-ONLY** and were not touched, per §25.

---

## 9. Tests

Pure/static suites only. Each was run under an instrumented `ou_observations`, so
the trajectory column is measured, not assumed.

| suite | checks | passed | failed | trajectory-producing? |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 155 | 155 | 0 | no (measured 0) |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | no (measured 0) |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | no (measured 0) |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | no (measured 0) |
| **total** | **486** | **486** | **0** | **0 trajectories** |

The terminal-calibration suite grew from 10 groups / 101 checks to **12 groups /
155 checks**: `C1` (Finding A, a committed publication is not a valid one) and
`C2` (Finding B, restart requires the canonical plan).

No historical aggregate is repeated. The ten other E1a suites were not run in this
task and nothing is claimed about them.

### Deferred trajectory suite

`test_e1a_v4_campaign_driver.py` was **modified but NOT executed**, per §28 — it
invokes `ou_observations`. Its fourteen `verify_restart` call sites were updated
to pass `harness.jobs`, which is `plan_campaign(binding.plan)`, the canonical plan
itself. Verified statically only: the file byte-compiles, and all ten
`verify_restart` / `inventory_job_records` / `validate_job_record` call sites were
parsed from the AST and bound against the current signatures with
`inspect.Signature.bind` — all bind, none fail.

**Its runtime status remains unverified and is not claimed.** KNOWN DEFERRED TEST.
It should be executed by whoever next runs a trajectory-permitting stage.

---

## 10. Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

No file in `SCIENTIFIC_MODULES` (12 entries) was modified — verified by set
intersection against the work commit's changed paths: **NONE**. No frozen
authority file was touched: physical foundation, theory baseline, prospective
design, design contract, Markdown plan, JSON plan, seed map and execution seal —
intersection: **NONE**.

Changed files, all four:

```text
e1a_v4/validation/campaign_driver.py   verified_publication, canonical_plan,
                                       require_authentic_plan, and the wiring
test_e1a_v4_terminal_calibration.py    groups C1 and C2
test_e1a_v4_driver_endpoints.py        one expectation, now upstream-precise
test_e1a_v4_campaign_driver.py         call sites updated (deferred, not run)
```

No new refusal codes were added; 62 total, unchanged. `CAMPAIGN_PLAN_MISMATCH`
already meant "the job plan disagrees with the frozen machine plan", which is
exactly this condition.

### Campaign structure

```text
planned jobs            53,200   unchanged
calibration artifacts   46,000   unchanged, and equal to the plan's own declaration
```

C7 and C8 still require no calibration. No new scientific jobs, no changed
calibration scope.

---

## 11. Open issues — listed, not resolved

```text
C3/C4 field-to-replicate reduction   still fails closed with
                                     ENDPOINT_EVENT_REDUCTION_UNDECLARED
PRNG authority                       open
field construction authority         open
C6 implementation inputs             open
remaining C8 implementation inputs   open
diagnostic aggregator authority      open
```

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

PERSISTED PROVENANCE VERIFIER REPAIR COMMITTED
