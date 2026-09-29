# E1a v4 — OFFICIAL CAMPAIGN DRIVER COMPLETION REPORT

**Status:** the five blocking findings of the independent campaign-driver audit are
repaired. The stochastic execution path is now implemented and was not executed.

| | |
|---|---|
| Audited coordinate | `4c679f46503f75218bc9a6736a427fbae0d526f2` (report), `29ffe6259105c34d63d7737d5f3c0f16b0becbae` (work) |
| Work commit | `2ee8212e49fef80366226b2a7cec8e3bdda7965c` |
| Work tree | `cff753b3de290cd58c0d159429ebfd551ae3d583` |
| Branch | `gaussian/stage-a-environment` (not pushed) |
| Plan version | 1.10.0, byte-unchanged |

---

## 1. Auditor blockers, each reproduced BEFORE any edit

Every finding was reproduced against the audited work commit using deterministic
isolated fixtures, with no RNG in scope. Nine of the ten listed probes escaped
exactly as reported; the tenth was confirmed statically because it sits behind the
seal gate. Nothing was taken on trust and nothing was repaired before it was seen
to fail.

| # | Probe | Behaviour at `29ffe625` |
|---|---|---|
| 1 | published execution identity edited | **ESCAPED** — verifier accepted |
| 2 | published calibration-condition hash edited | **ESCAPED** — verifier accepted |
| 3 | published publication state edited | **ESCAPED** — verifier accepted |
| 4 | C2 job + C7 aggregate | **ESCAPED** — recorded as `case_id=C2_geometry_false_rejection` |
| 5 | C2 job + empty field list | **ESCAPED** — `per_field` rows = 0 |
| 6 | mandatory diagnostic checked, then stored? | **ESCAPED** — stored keys were `branch_a_evidence_sha256, case_id, replicate_id, result, schema, scope, subcondition_id`; the diagnostic was absent |
| 7 | restart with `{}` while a publication exists | **ESCAPED** — `{'verified_publications': 0}` returned beside a real publication |
| 8 | injected directory-fsync failure | **ESCAPED** — raised `OSError`, job stayed `BRANCH_A_REALIZED`, **and the verifier accepted the file** |
| 9 | failing analysis outcome copy | **ESCAPED** — `RuntimeError` raised, state nevertheless `ANALYSED` |
| 10 | official stochastic execution path | **UNIMPLEMENTED** — `run_campaign` carried an explicit "the stochastic execution stage is not implemented" refusal; no `execute_job`, `execute_campaign`, `reconcile_restart`, `assemble_case_aggregates` or provider existed |

Probe 9 required care: a `dict` subclass is fast-pathed by CPython, so the first
hostile fixture never called `keys()` and produced a false negative. A real
`collections.abc.Mapping` whose `__iter__` raises reproduced the defect.

Each of the ten now has a permanent regression test, and each refuses for a coded,
asserted reason rather than merely raising.

---

## 2. The publication envelope

A publication is no longer authenticated by the Branch-A evidence hash. One
canonical digest binds the **complete** envelope, and it excludes itself so that
verification is a recomputation rather than a comparison of a field with itself:

```
publication_digest = sha256(canonical_json(envelope without publication_digest))
```

Bound fields (`PUBLICATION_FIELDS`, exact — a missing field and an unknown field
are both refusals):

| Field | Carries |
|---|---|
| `schema` | `e1a_v4_branch_a_publication/2` |
| `state` | `BRANCH_A_PUBLISHED` |
| `coordinates` | case, subcondition, replicate, scope |
| `branch_a_evidence` | the whole canonical realisation — field id, **Branch-A seed identity**, **common-mode seed identity**, H_A, T, k modes, orientation, tau, scale factor, n, dt, route, status, contract, plan, **analysis identity**, generator identity |
| `branch_a_evidence_sha256` | the evidence digest, recomputed on read |
| `calibration_condition_sha256` | the condition hash, or null where the case requires none |
| `package_identities` | contract, plan, seed map, analysis procedure identity, **execution identity** |
| `not_execution_authorisation` | always `true` |
| `publication_digest` | the seal over all of the above |

Seed identities and the analysis identity are inside `branch_a_evidence` and are
not restated: duplicating them would create two places for one fact.

**Verification is three independent layers, each demonstrated reachable:**

| Adversary | Caught by |
|---|---|
| edits the artifact | the commit marker's byte digest → `PUBLICATION_INCOMPLETE` |
| edits the artifact **and** re-commits a consistent marker | the envelope digest → `PUBLICATION_DIGEST_MISMATCH` |
| repairs the envelope digest too | comparison against the realisation and the current package → `BRANCH_A_EVIDENCE_ALTERED` / `BRANCH_A_PROVENANCE_MISMATCH` |

Ten provenance fields are edited individually against the second adversary and
each refuses; `state` and `schema` are refused earlier still, by the strict schema,
because an invalid state is not a record worth authenticating.

Strict schema refusals: missing field, unknown field, wrong type, invalid state,
malformed digest, missing or unknown package identity, incomplete coordinates.
Duplicate keys are refused one layer down by `strict_loads`, so an ambiguous record
never reaches the schema — no second, permissive parser was created.

---

## 3. The publication transaction

The audit's sharpest finding was that

```
final file created -> directory sync fails -> operation raises -> reader accepts
```

made `publish() raised FAILURE` and `the reader treats it as PUBLISHED`
simultaneously true.

The repository already answers this, in
`V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md` §5: a result directory is not
`FINALIZED` because its artifacts exist, but because a **separate** registered
artifact exists and validates against them, and state is classified by
inventorying the directory rather than by asking the writer what it did. That
mechanism is adopted one level down, not reinvented:

```
PREPARED EVIDENCE      <dir>/<name>.json          the artifact bytes
COMMITTED PUBLICATION  <dir>/<name>.commit.json   the marker, binding
                                                  the exact bytes + the digest
```

**The durability point.** Inside one artifact there is exactly one instant at which
the final path becomes durable: the directory fsync immediately after
`link(temp, final)`.

- Failure **at or before** it → the final link is removed, the temporary removed, and the operation raises. Nothing a reader can accept survives.
- Failure **after** it → the artifact *is* durable; only the alias is outstanding. The addendum calls that recoverable residue, so publication succeeds and reports it. Raising there would claim a publication failed that in fact succeeded.

**The invariant now holds mechanically:**

```
publish_transaction() returns  iff  a reader may treat the artifact as PUBLISHED
publish_transaction() raises   ==>  no reader will, whatever residue remains
```

**Fault injection.** Fourteen deterministic single-stage failures are injected
across both artifacts of the transaction (`lstat`, `open_temp`, `write`,
`fsync_file`, `fchmod`, `link`, `fsync_dir`, `unlink`, each at the call index that
selects the evidence or its marker). For every pre-durability failure: the
operation reports failure, the job does not advance, the verifier does not accept,
and restart does not infer a completed publication. For every post-durability
failure: publication succeeds and the residue is reported. The injection seam is
module-level stage functions with no parameter, flag or environment variable, so
production cannot select a different implementation.

**Orphans.** An artifact whose marker is absent is `PUBLICATION_ORPHANED` — never
promoted, and never deleted, because the orphan is the only surviving record of
what was attempted. A marker whose artifact is absent is `DANGLING`. An artifact
whose marker no longer matches its bytes is `TAMPERED` and re-read so the refusal
states exactly what disagrees. Anything else in the directory is
`PUBLICATION_UNEXPECTED_ENTRY`.

**Limitation, stated plainly.** If a non-durable final path cannot itself be
removed, no scheme can distinguish "durable" from "written but unfsynced" by
reading the filesystem. That case raises `PUBLICATION_NOT_DURABLE` naming the
residue and blocks the campaign for manual recovery; restart's set-equality check
is the second line of defence. Durability remains a procedural guarantee, exactly
as it is in the addendum.

---

## 4. Result recording

The recorder no longer trusts caller-supplied structure. From the immutable planned
job and the frozen plan it derives:

```
job_id -> frozen planned job -> case / subcondition / result kind / role
                             -> required field set (plan order)
                             -> mandatory diagnostic set
```

- **Case compatibility is explicit.** The aggregate's `case_id` must equal the job's, its `schema` must be the frozen manifest schema, and a declared `subcondition_id` must equal the job's. Every drivable case was tested against all seven foreign aggregates — 49 probes, all `RESULT_CASE_MISMATCH` — plus a foreign subcondition and a superseded schema. After each refusal the job is still `ANALYSED`.
- **The field set is derived.** Empty, missing, extra, duplicated and wrong-name lists all refuse with `RESULT_FIELD_SET_MISMATCH`. Ordering is not semantic here, so a correct set in another order is canonicalised to plan order rather than refused; omitting the argument derives it.
- `result_kind`, `role` and `requires_calibration` are copied from the frozen job. The caller cannot supply them at all.

`C6_mode_resolution_boundary` cannot be driven through the state machine because its
field is declared as prose (see §8); its gap is asserted by name instead.

---

## 5. Mandatory diagnostics are stored

A result that passes validation and then discards what it was validated against
cannot demonstrate the requirement. Every checked diagnostic is now carried into
the record with its authority path and its full evidence, and the record
revalidates **from itself**:

For C2's frozen contract diagnostic the stored evidence retains, per declared
field: `rejections`, `replicates` (raw counts), `cp_upper` (computed value),
`direction` and `confidence_level` (confidence rule), `threshold`, and `pass`
(classification). `validate_job_record` rebuilds the minimum aggregate from the
stored rows and re-runs the *same* validator, so the evidence is checked rather
than merely present.

Demonstrated: a round-tripped record revalidates without its original aggregate;
an edited result, a record with its diagnostics removed, and a diagnostic
inconsistent with its own counts each refuse (`RESULT_SCHEMA_INVALID`,
`CONTRACT_MANDATORY_DIAGNOSTIC_MISSING`, `CONTRACT_MANDATORY_DIAGNOSTIC_MISMATCH`).
A C7 job presented with C2's diagnostic refuses as a case mismatch — a C7 result
cannot satisfy C2's requirement because it is not a C2 result at all.

Where frozen authority owes a diagnostic whose computation it states only in prose,
`default_case_aggregate` refuses by name rather than reporting an empty one.

---

## 6. Restart reconciliation

Restart no longer consults the caller about what exists. Two persisted stores are
inventoried independently:

```
<output>/branch_a/      committed Branch-A publications
<output>/job_records/   committed terminal job records
```

Each entry is classified, each record's coordinates must hash back to its own
basename, and each is re-verified against the current package. Then set equality is
required in **both** directions.

| Scenario | Outcome |
|---|---|
| publication exists, caller supplies `[]` | `RESTART_INVENTORY_MISMATCH` |
| caller omits half the store | `RESTART_INVENTORY_MISMATCH` |
| caller claims a publication whose bytes are missing | `RESTART_INVENTORY_MISMATCH` |
| restart record filed under the wrong key | `RESTART_INVENTORY_MISMATCH` |
| publication for an undeclared job | `RESTART_INVENTORY_MISMATCH` |
| duplicated publication | refuses |
| artifact without its commit marker | `PUBLICATION_ORPHANED` |
| marker without its artifact | `PUBLICATION_INCOMPLETE` |
| terminal record without its Branch-A publication | `RESTART_INVENTORY_MISMATCH` |
| published evidence with no committed terminal record | `RESTART_INVENTORY_MISMATCH` — interrupted between publication and recording; the evidence is immutable, so the job can be neither re-run nor completed automatically, and recovery is an authorised decision |
| terminal record edited after commit | `PUBLICATION_INCOMPLETE` |
| **empty inventory, empty claim** | **valid, and only then** |

`recover_realisations` is the authorised deterministic recovery: it rebuilds the
checkpoint from the publications themselves — losslessly, because the canonical
form is `float.hex()` — and the recovered set then goes through the *same* strict
reconciliation. Recovery is a way to obtain the set honestly, not a way around set
equality. A successful and a refused reconciliation were both shown to write
nothing and delete nothing.

---

## 7. Failure atomicity, transition by transition

`_require_transition` checks first; the work runs; the output is verified; `_enter`
is the last statement. Proved by injected failure at each transition:

| Transition | Injected failure | State afterwards |
|---|---|---|
| → `BRANCH_A_REALIZED` | foreign Branch-A seed | `PLANNED` |
| → `BRANCH_A_PUBLISHED` | directory fsync at the durability point | `BRANCH_A_REALIZED` |
| → `CALIBRATION_CONDITION_BOUND` | commit marker removed | `BRANCH_A_PUBLISHED` |
| → `CALIBRATION_LOCKED` | artifact from another condition | `CALIBRATION_CONDITION_BOUND` |
| → `BRANCH_B_UNBLINDED` | publication altered after the lock | `CALIBRATION_LOCKED` (and Branch B still unreachable) |
| → `ANALYSED` | outcome cannot be copied / empty / non-serialisable / non-string keys | `BRANCH_B_UNBLINDED`, four times |
| → `RECORDED` | foreign aggregate | `ANALYSED` |
| after `RECORDED` | any further call | `JOB_STATE_INVALID` |

`publish_branch_a` additionally re-reads the record from disk and verifies it
before entering the published state: re-reading is what separates "the write
returned" from "a reader can now obtain exactly this evidence".

Structured scientific refusals remain results — recorded, terminal, verbatim, not
retried under another seed (the Branch-B stream is a pure function of the frozen
coordinates, so "retry under another seed" is not an operation the interface has),
not dropped, and not converted into a software error.

---

## 8. Stochastic execution orchestration

**IMPLEMENTED != EXECUTED.**

The production path now exists in full:

```
load frozen authority (bind_execution)
  -> THE LIFECYCLE GATE
  -> authorised deterministic recovery of the checkpoint from disk
  -> reconcile both persisted stores
  -> deterministic job plan (53,200 jobs)
  -> per replicate: ONE common-mode draw shared across fields
       -> per field: Branch-A measurement -> realise -> hash -> publish -> COMMIT
                  -> [condition from the PUBLISHED evidence -> calibrate -> lock]
                  -> unblind -> Branch-B trajectory -> analyse
       -> cross-field endpoints P1/P2/P3/P4
  -> per case: aggregate -> immutable terminal record -> durably committed
  -> campaign completeness: every frozen job, exactly once
  -> case aggregates from the IMMUTABLE planned job identities
  -> the frozen release classifier
```

It **calls** the existing frozen implementations and duplicates no formula:
`generate.BranchAErrorModel.measure`, `calibrate.generate_block1_artifact`,
`generate.ou_observations`, `generate.truth_from_field`, `geometry.analyse_field`,
`endpoints.p1_geometry / p2_cross_field / p3_absolute / p4_consistency`,
`effective_size.sigma_stat`, `classification.classify_campaign`, and seeds solely
through `ReplicateCalibration`. The driver contributes the order, the provenance
and the seeds. `grep` finds no scientific constant in it: `0.005`,
`1.959963985`, `0.00012`, `2000000` and `279/300` each occur zero times.

### Four authority gaps, found by writing the path before the seal

The production resolver refuses for every job today and names exactly what is
missing. A driver that supplies a plausible default for an undeclared generating
parameter has quietly become the author of the experiment.

1. **The pseudo-random generator.** The seed map declares the master seed, the family seeds and the derivation of stream identities. *No frozen document declares the PRNG algorithm or the transform from uniform to standard normal.* Two algorithms seeded identically produce different trajectories, so this determines every number the campaign draws.
2. **Branch-A field construction inputs** — `calibration_route`, viscosity η, bead radius *a*. The frozen rule τ_r = γ(T)/k_r with γ = 6πη(T)a makes them set every φ, every effective size N_ab and the entire Block-1 null law. Test fixtures pass literals; an official campaign may not.
3. **The C6 field.** `C6_mode_resolution_boundary` declares its field as prose — "synthetic two-mode field at the declared rho". The contract declares four fields and none is at a declared ρ. The driver refuses to invent a geometry whose eigenvalue ratio *is* the quantity under test.
4. **C8's beta truth**, declared as the string `"1/c on the blinded branch"`. Six cases carry a numeric `beta_truth` and C7 carries per-alternative vectors; C8's is prose, so the driver refuses to read it as a generating parameter.

A fifth, smaller item: the per-case **mandatory-diagnostic aggregator** is the
reporting layer's contribution and several diagnostics (C4's operating-quantile
discrepancy, C3's delta-method error) are stated only in prose. The driver
*requires* them, which is its job; computing them is not.

All five must be declared in frozen authority — and thereby enter the execution
identity — **before the seal is frozen**. Finding them now is what writing the
driver before sealing is for.

### Control flow exercised without any RNG

Deterministic van der Corput suppliers drive the complete orchestration for a
calibration-requiring replicate (C1), a no-calibration replicate (C7) and the C8
paired path, plus a structured-refusal outcome and a restart/resume path. Verified
per run: one common-mode draw per experiment, one Branch-A stream per field, one
Branch-B stream per field, calibration streams exactly matching the case's declared
requirement, every publication committed, every job reaching one terminal record,
and a subset run **not** classified. These are control-flow exercises; the numbers
are not samples from any distribution and no verdict in them is a result.

---

## 9. The execution gate

`require_execution_lifecycle` runs the plan's declared `execution_gate_order`, most
fundamental precondition first:

1. the canonical campaign driver is present and declares its entry point
2. the external execution seal is `FROZEN`
3. the recomputed execution identity equals the independently sealed one
4. `execution_authorised` is true
5. the campaign manifest is valid
6. both persisted stores are clean

On this package it refuses at step 2 with `EXECUTION_SEAL_NOT_FROZEN`. The refusal
happens **before** `AuthorisedStochasticProvider` is constructed — the gate is
lexically and dynamically above it in `run_campaign`, asserted by AST inspection of
the source. The sentinel confirms **real RNG requests = 0**.

**No production bypass.** `run_campaign(root, *, output_dir, plan_only)` — three
parameters, confirmed by both `inspect.signature` and the AST. No `force`,
`skip_gate`, `ignore_seal`, `test_mode`, `provider` or `resolver`; the previous
`rng_factory` parameter was itself an injection point on the production entry point
and has been removed. The CLI declares only `--plan-only` and `--preflight-only`.
`resolver` and `aggregator` exist on the internal `execute_campaign`, which is
below the gate and never reached when it refuses.

Were it ever reached, the production provider refuses too, with
`STOCHASTIC_PROVIDER_REFUSED`, naming authority gap 1. That refusal is deliberately
reachable only after the gate, so a reviewer who sees it knows the gate passed and
the remaining gap is an authority gap, not a software one.

---

## 10. Plan agreement

Recomputed independently from frozen authority, not hard-coded:

| | |
|---|---|
| Planned jobs | **53,200** |
| Calibration jobs | **46,000** |
| Missing planned jobs | 0 |
| Extra driver jobs | 0 |
| Duplicate job identities | 0 |
| C7 calibration jobs | **0** |
| C8 calibration jobs | **0** |

Per case the planned calibration count still independently reproduces each case's
declared `calibration_artifact_count` (C1 4,800; C2 6,400; C3 6,400; C4 8,000;
C5 19,200; C6 1,200; C7 0; C8 0). The driver and the plan were written by different
reasoning and agree.

`require_campaign_completeness` derives the expected total from the job plan the
frozen plan produces, so a plan declaring different replicate counts changes it
mechanically. Missing, extra, duplicate and non-terminal records all refuse.
`assemble_case_aggregates` groups by the planned job's case identity and refuses a
record that claims a different case, preventing cross-case substitution.
`classify_campaign` runs over the complete campaign or not at all, decided by
comparing the supplied job set with the complete frozen plan — not by a parameter.

---

## 11. Scientific authority

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Byte-unchanged, asserted in the suite:

| Source | sha256 |
|---|---|
| `EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| `EBU_THEORY_BASELINE.md` | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| `e1a_v4_design_contract.json` | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| `E1A_V4_PROSPECTIVE_DESIGN.md` | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` |
| `e1a_v4_synthetic_validation_plan.json` | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` |
| `E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | `3f4715b465da295e21ad99a86390585c9eb7deac44a7810114a88f40aa4bf940` |
| `e1a_v4_seed_map.json` | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` |

No threshold, count, field, case or release rule was touched. The twelve
SCIENTIFIC_MODULES are unchanged, so the **analysis procedure identity is
unmoved** at `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f`
— confirmed by the preflight, which refuses on any disagreement. No
analysis-bound file was modified and §42's stop condition was not triggered.

**Observation for the re-audit, not repaired here.** The plan's
`driver_requirements` block still reads `status: "MANDATORY, NOT YET SATISFIED"`
and `official_campaign_driver_present: false`, and asks for the driver module to be
added to `VALIDATION_MODULES`. The driver is bound instead, explicitly, as
`official_campaign_driver_sha256` in the same execution-identity preimage, which
satisfies the stated intent. These are operational statements, not scientific ones,
and correcting them would move the plan digest — outside this task's scope, and a
matter for whoever freezes the seal.

## 12. Identities

Changed files are all in the driver/provenance layer and all inside the
execution-identity preimage, so the identity moved — as it must:

| File | sha256 | Bound as |
|---|---|---|
| `e1a_v4/validation/campaign_driver.py` | `e7854485303f80c5185a81f7008bb410cd844117549ae838896371426857e0e0` | `official_campaign_driver_sha256` |
| `e1a_v4/validation/publication.py` | `f54ac2d408b08e33b67bcd5f378326745fcaee0ee13115a61cf7a07f97d2ac94` | `VALIDATION_MODULES` |
| `e1a_v4/validation/refusals.py` | `3724f723aee84b044f72f46069eb5877be69dc397137d11e1bd74ebb504f678c` | `VALIDATION_MODULES` |
| `e1a_v4/validation/results.py` | `465a19a34ab32562e2420502c8902b561f543f9f400d763123d035c695439e07` | `VALIDATION_MODULES` |

```
DRIVER-PRESENT / UNSEALED EXECUTION IDENTITY (NOT the final seal)
da7bfd0b1b21d5a35fef74fd939b764f5d4c1fec9236ce3f171a1deaba50f981

pre-execution campaign manifest sha256
99cc680f290a2a70f02d81d0372eb69deb0e3c9e834f6215523c5d32467e7a48
```

This is a **diagnostic, not a seal**. It is not frozen and must not be frozen until
the driver has been independently re-audited and the authority gaps of §8 are
closed — closing them will move it again, which is the point of naming them now.

Eight refusal codes were added (51 in the layer): `PUBLICATION_ORPHANED`,
`PUBLICATION_UNEXPECTED_ENTRY`, `PUBLICATION_DIGEST_MISMATCH`,
`RESTART_INVENTORY_MISMATCH`, `RESULT_CASE_MISMATCH`, `RESULT_FIELD_SET_MISMATCH`,
`CAMPAIGN_INCOMPLETE`, `STOCHASTIC_PROVIDER_REFUSED`.

---

## 13. Tests

| Suite | Result |
|---|---|
| `test_e1a_v4_campaign_driver.py` | **598 passed, 0 failed, 47 groups** (was 255 / 24) |
| `test_e1a_v4_release_authority.py` | 225 passed, 0 failed |
| `test_e1a_v4_coherence_hardening.py` | 138 passed, 0 failed |
| `test_e1a_v4_repair.py` | 126 passed, 0 failed |
| `test_e1a_v4.py` | 122 passed, 0 failed |
| `test_e1a_v4_case_scope.py` | 113 passed, 0 failed |
| `test_e1a_v4_plan_coherence.py` | 113 passed, 0 failed |
| `test_e1a_v4_generating_model.py` | 113 passed, 0 failed |
| `test_e1a_v4_calibration_scope.py` | 105 passed, 0 failed |
| `test_e1a_v4_preexec.py` | 104 passed, 0 failed |
| `test_e1a_v4_size_semantics.py` | 79 passed, 0 failed |
| `test_e1a_v4_contract_plan.py` | 75 passed, 0 failed |
| `test_e1a_v4_dispositions.py` | 64 passed, 0 failed |
| `test_e1a_v4_preexec_corrections.py` | 37 passed, 0 failed |
| **E1a total** | **2,012 checks, 0 failures** |

New groups: publication-envelope tampering, strict publication schema, publication
fault injection, orphan and dangling detection, case/result-type compatibility,
field-set derivation, mandatory-diagnostic persistence and round trip, result round
trip for every drivable case, restart inventory reconciliation, restart cannot
delete history, transition atomicity, structured refusals stay results, campaign
completeness and aggregation, release units, the execution gate before RNG,
authority-gap naming, fake full-orchestration control flow, fake refusal and
restart paths, publication and result restart interactions, the diagnostic
aggregator, no production bypass, frozen authority unchanged, and the deterministic
supplier is not an RNG.

The rest of the repository was run. Four suites fail identically at the audited
`4c679f46` and at this commit — `test_authority_coordinate.py` (the known
off-v3.0-branch assertion), `test_v30_gate1dc.py`, `test_v30_adversary.py`,
`test_v30_o14.py` — verified in a detached worktree at `4c679f46`. Four harnesses
correctly refuse to run because they advance model state, and four `test_v2x`
suites fail on a missing `matplotlib`. None imports `e1a_v4`. **No suite regressed.**

---

## 14. Stochastic boundary

```
REAL RNG OBJECTS = 0
REAL RANDOM DRAWS = 0
REAL TRAJECTORIES = 0
REAL CALIBRATION EXECUTIONS = 0
REAL CAMPAIGN JOBS = 0
```

Reported separately, and never described as scientific execution: **79 deterministic
van der Corput suppliers** constructed and **825,752 deterministic values**
supplied inside temporary sandboxes, driving the orchestration's control flow.
Among them the Block-1 calibration *generator* was exercised on that deterministic
input for one C1 replicate — the repository's own established convention for this
(the plan's benchmark note: "deterministic van der Corput arrays and a fixed
repeating normal supplier; NO RNG"). No artifact from a random draw exists, none is
retained, and every sandbox is deleted. `results/e1a_v4_validation` does not exist
in the repository.

---

## 15. Lifecycle

```
OFFICIAL CAMPAIGN DRIVER      = PRESENT
DRIVER IMPLEMENTATION         = COMPLETE
DRIVER AUDIT                  = PENDING RE-AUDIT
FINAL EXECUTION SEAL          = NOT FROZEN  (state PRE_DRIVER)
EXPECTED FINAL EXECUTION ID   = NULL
EXECUTION AUTHORISED          = FALSE
VALIDATION CAMPAIGN           = NOT RUN
```

## 16. Next stage

```
OFFICIAL CAMPAIGN DRIVER INDEPENDENT RE-AUDIT
READY
```

Not begun, and not authorised by this report. Before the seal may be frozen, the
four authority gaps of §8 and the diagnostic aggregator must be declared in frozen
authority; each will move the execution identity again.

```
CAMPAIGN DRIVER COMPLETION COMMITTED
```
