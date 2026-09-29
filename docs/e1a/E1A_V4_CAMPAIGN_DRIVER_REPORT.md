# E1a v4 — Official campaign driver and end-to-end blinding provenance

Work commit `29ffe6259105c34d63d7737d5f3c0f16b0becbae`, tree
`845861306320e06e2790a6806d79cf0f92b02771`, branch `gaussian/stage-a-environment`.
Starting coordinate `0ac1fab977a795d128f5ee0e6df01c701cfd79a9`.

**Nothing was executed.** No RNG object was constructed, no random number drawn, no
trajectory generated, no calibration sampled, no scientific outcome inspected.

---

## Canonical driver

```text
module      : e1a_v4.validation.campaign_driver
path        : e1a_v4/validation/campaign_driver.py
entry point : run_campaign
sha256      : e75cb7bd5251ee5128c257613745e1b91822b141867063cd67143b35a28f5330
```

The declaration in `e1a_v4/validation/driver.py` is **unchanged**. The path, module and
entry-point names are exactly the ones frozen prospectively while the file did not
exist. No second driver was created, and the declaration was not edited to make
implementation easier.

Supporting modules added: `e1a_v4/validation/publication.py` (the durable publication
primitive). It joins `VALIDATION_MODULES`, which is now 18. The **driver itself is
deliberately not in that list**: it is bound separately and explicitly as
`official_campaign_driver_sha256` in the same execution-identity preimage, and hashing
it twice would obscure which binding does the work.

---

## Campaign structure

Derived entirely from the frozen plan — `campaign_shape` reads the case list, the
subcondition list, `replicate_count` and `fields_affected`, and computes nothing of its
own.

| case | subconditions | R | field scopes | jobs | calibration jobs |
|---|---:|---:|---:|---:|---:|
| C1_true_bridge_complete | 4 | 300 | 4 | 4,800 | 4,800 |
| C2_geometry_false_rejection | 4 | 400 | 4 | 6,400 | 6,400 |
| C3_g5_block | 4 | 400 | 4 | 6,400 | 6,400 |
| C4_surrogate_validity | 1 | 2000 | 4 | 8,000 | 8,000 |
| C5_plug_in_branch_a | 12 | 400 | 4 | 19,200 | 19,200 |
| C6_mode_resolution_boundary | 3 | 400 | 1 | 1,200 | 1,200 |
| C7_false_bridge | 4 | 400 | 4 | 6,400 | **0** |
| C8_blinded_scale_control | 1 | 200 | 4 | 800 | **0** |
| **total** | | | | **53,200** | **46,000** |

**An independent cross-check the plan already carried.** Each calibrating case's planned
calibration-job count reproduces that case's own declared `calibration_artifact_count`
exactly — 4,800 / 6,400 / 6,400 / 8,000 / 19,200 / 1,200 — and C7 and C8 reproduce their
declared zero. The driver and the plan were written at different times by different
reasoning, and they agree.

Planning is RNG-free and deterministic: the frozen case order, then the frozen
subcondition order, then the replicate index, then the case's declared field scopes. No
clock, environment variable, filesystem listing or hash-ordering input is read. Planning
twice produces byte-identical descriptors.

### Plan / driver agreement

`require_plan_driver_agreement` rebuilds the expected job set from the plan and compares
both directions, including each job's calibration requirement and seed families:

```text
planned jobs           53200
driver jobs            53200
missing planned jobs       0
extra driver jobs          0
```

The check discriminates: a dropped job, an added job and a plan declaring one fewer
replicate each raise `CAMPAIGN_PLAN_MISMATCH`.

---

## Provenance chain

```text
Branch-A measurement
      │
      ▼
BranchARealisation            immutable; bound to case, subcondition, replicate,
      │                       scope, both Branch-A seed identities, and the
      │                       contract / plan / analysis identities
      ▼
evidence_sha256               sha256 over sorted-key compact canonical JSON,
      │                       floats via float.hex(), no rounding
      ▼
DURABLE PUBLICATION           publication.publish_atomic -> immutable 0444 file
      │                       at a coordinate-derived final path
      ▼
CalibrationCondition          derived FROM THAT EXACT REALISATION, after
      │                       re-verifying the published record
      ▼
calibration artifact          generated for the same coordinates
      │
      ▼
artifact LOCKED               field and condition digest checked here first,
      │                       then the frozen ReplicateCalibration ledger
      ▼
BranchBUnblindToken           issued only if publication verifies AND (where
      │                       required) the artifact is locked against this
      │                       job's own condition
      ▼
Branch-B stream               JobExecution.branch_b_seed — the ONLY route
      │
      ▼
analysis  ->  case result, with its mandatory contract diagnostics
```

`branch_b_seed` refuses without the token. This is structural, not conventional: there is
no other method on `JobExecution` that reaches a Branch-B stream, and the token is only
constructed inside `unblind`.

### What was missing before

`ReplicateCalibration` already enforced part of the chain — an artifact is checked
against a supplied condition, and the Branch-B seed is refused before the artifact is
locked. Two gaps remained, and both are closed:

1. **Nothing hashed or published Branch-A evidence at all.** The frozen rule was
   satisfied by no mechanism whatsoever.
2. **`lock()` accepted an externally prepared `CalibrationCondition`** as proof of
   Branch-A provenance, so a caller could present a condition that never came from that
   replicate's Branch-A measurement.

### A separation that had to be fixed during implementation

The first version advanced the job state and *then* did the work. A refused publication
or a refused lock therefore left the job in the advanced state, and the next step's
precondition was satisfied by a step that had failed. Checking and entering are now
separate (`_require_transition` then `_enter`), so a refusal leaves the job exactly where
it was. Three fixtures caught this.

---

## Meaning of publication

The frozen authority states the rule three times, identically, and **defines it nowhere**:

> `docs/theory/EBU_THEORY_BASELINE.md` line 459, `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md`
> line 60, and `docs/e1a/e1a_v4_design_contract.json`
> `information_separation.unblinding`:
>
> "Branch-A output is hashed and published **before** Branch B is unblinded."

That would be an ambiguity worth stopping over if the repository had no answer. It has
one. `V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md` §2, *Strict serialization and
publication primitives*:

> "Each temporary is opened at that exact name with `O_WRONLY|O_CREAT|O_EXCL` and
> `O_NOFOLLOW` where available, mode `0600`, only after `lstat` proves absence. Random or
> alternate names are forbidden. Its `st_dev` must equal the result directory's
> `st_dev`.
>
> Publication writes every byte, flushes, `fsync`s the file, changes the mode to `0444`,
> `fsync`s again, closes, and atomically creates the absent final path by
> `link(temp, final)`. Collision fails closed. The destination directory is `fsync`ed
> before the final path counts as durable. The temporary alias is then unlinked and the
> directory is `fsync`ed again. No alternate publication primitive is permitted."

and, for hashing:

> "Canonical hashing and nested canonical evidence use sorted-key compact JSON,
> `ensure_ascii=True`, `allow_nan=False`, UTF-8, and no final newline."
> "Every text artifact is UTF-8 without BOM, contains LF rather than CR or CRLF, contains
> no NUL, and ends in exactly one LF."

**Scope, stated honestly.** `AGENTS.md` makes that addendum's precedence deliberately
narrow: it governs Gate 1D-C execution mechanics and nothing else. It is therefore **not
E1a scientific authority**, and this implementation does not claim it is. What is adopted
is the repository's established operational *meaning* of publication and its canonical
serialisation, so E1a implements the repository's intent rather than inventing a weaker
one. The Gate 1D-C artifact names and paths are not borrowed; E1a supplies its own.

Concretely, published means: an immutable, world-readable file at a final path, created
atomically from a fully-written and `fsync`ed temporary, in a directory that has itself
been `fsync`ed. A partial write can never occupy the final path, and a second publication
at the same path fails closed.

Tested: the file is `0444`; no temporary survives; the bytes are canonical JSON plus
exactly one LF; a second publication raises `PUBLICATION_COLLISION`; a record with no
terminating LF, with appended bytes, or absent raises `PUBLICATION_INCOMPLETE`; and
publishing over a leftover temporary refuses rather than clobbering evidence of an
interrupted publication.

---

## Substitution protection

The publication path is a **pure function of the coordinates**, so foreign evidence can
never be read as though it belonged to other coordinates — there is simply no record
there. That is stronger than a comparison, and it is why several cross-coordinate probes
refuse with `PUBLICATION_INCOMPLETE` rather than a mismatch code.

| substitution | outcome |
|---|---|
| wrong case Branch-A | different hash, different path, `PUBLICATION_INCOMPLETE` |
| wrong subcondition Branch-A | different hash, different path, `PUBLICATION_INCOMPLETE` |
| wrong replicate Branch-A | different hash, different path, `PUBLICATION_INCOMPLETE` |
| wrong field Branch-A | different hash, different path, `PUBLICATION_INCOMPLETE` |
| **same coordinates, different evidence** | `BRANCH_A_EVIDENCE_ALTERED` |
| wrong Branch-A seed identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| wrong common-mode identity | `BRANCH_A_PROVENANCE_MISMATCH` |
| edited published evidence | `BRANCH_A_EVIDENCE_ALTERED` |
| edited published hash | `BRANCH_A_EVIDENCE_ALTERED` |
| rebound coordinates in the record | `BRANCH_A_PROVENANCE_MISMATCH` |
| package identity changed after publication | `BRANCH_A_PROVENANCE_MISMATCH` |
| unpublished evidence, Branch-B requested | `BRANCH_B_PREMATURE` |
| unpublished evidence, unblind requested | `BRANCH_A_NOT_PUBLISHED` |
| artifact from another field | `BRANCH_A_PROVENANCE_MISMATCH` |
| artifact from different Branch-A evidence | `BRANCH_A_PROVENANCE_MISMATCH` |
| republication, same execution | `JOB_STATE_INVALID` |
| republication, second execution | `PUBLICATION_COLLISION` |
| explicit republish attempt | `BRANCH_A_PUBLICATION_IMMUTABLE` |

The same-coordinates / different-evidence probe is the one that matters most: it
substitutes `theta1_power`'s measurement under `theta0_circular`'s coordinates. The two
differ only in stiffness, so the resulting conditions look numerically similar — and it
still refuses, because provenance identity, not numeric resemblance, is what is checked.

Twelve separate mutations of the canonical evidence — every coordinate, `H_A`,
`T_measured`, `tau_modes`, both seed identities, the scale factor, the plan hash and the
analysis identity — each change the evidence hash. The hash does not depend on dictionary
iteration order, locale, timestamps, process ID or scheduling.

---

## Case semantics

**C1** — complete-pipeline job per (subcondition, replicate, field); calibration required;
result kind `complete_pass`.

**C2** — per-field P1 false-rejection; calibration required; result kind `p1_rejection`;
its mandatory contract diagnostic is required at record time (below).

**C3** — see below.

**C4** — Block-1 achieved size under the surrogate; one subcondition, R = 2000;
calibration required.

**C5** — twelve declared plug-in cells, R = 400 each; calibration required; the release
rule is report-only, which the driver carries as a result kind and never as a threshold.

**C6** — three declared rho, **one** synthetic field scope, R = 400 each. The driver
schedules 1,200 jobs, not 4,800: the single synthetic two-mode field is not expanded into
the four physical fields.

**C7 / C8** — see below.

### C3

```text
PRIMARY C3 RELEASE ENDPOINT          G5 / Block-2 size
FULL P1 TWO-BLOCK RESULT             SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC
```

The driver's result kind for every C3 job is `g5_block_rejection`, not the joint P1
result. C3 still requires Block-1 calibration, because the frozen scientific purpose
requires reporting the two-mode max statistic's interaction with the two-block gate — but
that interaction is an input to a diagnostic, not to the release verdict.
`joint_p1_result_changes_C3_release_verdict` is `false`, and the plan's prohibition on
adding any new C3 release threshold based on Block 1 or the joint P1 result is asserted
verbatim.

### C7 / C8 — no-calibration semantics

Both read `requires_block1_calibration` from the plan; neither acquires an accidental
calibration dependency. For both, asking for a calibration condition or a calibration
stream raises `JOB_STATE_INVALID`, and the frozen alternative prerequisite for Branch-B
access is **publication alone** — which is the frozen rule, not a weakening of it. Their
unblind tokens carry `calibration_condition_sha256 = null` and
`calibration_artifact_sha256 = null`.

C7 schedules exactly the four frozen alternatives, 400 × 4 jobs each, never pooled;
result kind `false_bridge_acceptance`; role `negative_control`.

### C8 — pairing

C8 declares one subcondition and 200 replicates, so the driver schedules 200 × 4 = 800
jobs — **not** 200 per scale factor, and no job per scale factor. One Branch-A realisation
is published per (replicate, field), and the two blinded branches are a deterministic
transform of that same underlying field: `blinded(c)` preserves `H_U`, `T`, `k_modes` and
`rot_deg` and multiplies only `scale_factor`. Tested: both branches share the same
underlying field, differ only by the frozen factors `[1.07, 0.9]` read from the plan, and
leave the underlying true bridge unchanged. C8 uses its own
`blinded_scale_control` Branch-B family.

---

## Seed scopes

The driver performs **no seed arithmetic**. Every identity comes from `CaseSeedAccess`
through `ReplicateCalibration`; there is no global random state and no manually
constructed generator.

**Intentional sharing.** One experiment-scope common-mode stream per (case, subcondition,
replicate), shared across that replicate's four fields. It cancels in the P2 ratio and
not in P3, so it must not be redrawn per field. Verified: the four fields return the same
common mode, their per-field Branch-A streams are all distinct, and none equals the shared
common mode. Supplying a common-mode identity that is not this experiment's raises
`BRANCH_A_PROVENANCE_MISMATCH`.

**Independence.** A different replicate and a different subcondition each yield a
different common mode.

**Order invariance.** Forward, reverse and a scope-sorted permutation of the schedule
produce identical job identities, identical derived seed identities and identical
publication destinations.

---

## Manifest and restart

The pre-execution manifest (`e1a_v4_campaign_manifest/1`) binds the foundation, baseline,
contract, design, analysis identity, plan JSON, plan Markdown, seed map, execution
identity, the canonical driver path and its sha256, the validation-module list, the case
structure with subconditions and replicate counts, the result and manifest schemas, the
mandatory diagnostics and the output location. It records
`final_expected_execution_identity: null` and `execution_authorised: false`, carries
`state: DRIVER_PRESENT_UNSEALED`, and says of itself
`not_execution_authorisation: true`. **The final seal is not frozen and is not included.**
A manifest missing a required identity raises `CAMPAIGN_MANIFEST_INVALID`. Its digest is
deterministic.

Current manifest sha256: `a678e6b6f11d7ae719f54de151bfba0d54ce5dc4e12c234f3f81a53b4f493827`.

**Restart.** `verify_restart` re-reads every published record, recomputes its digest from
the published evidence, compares the evidence with the realisation in hand, and checks
the package identities. A tampered record raises `BRANCH_A_EVIDENCE_ALTERED` on resume
and the record is **left in place**: resume never regenerates a completed replicate and
never silently replaces provenance.

---

## Mandatory diagnostics

`JobExecution.record` calls `require_mandatory_diagnostics` before entering `RECORDED`.
Recording a C2 result with no `contract_diagnostics` raises `RESULT_SCHEMA_INVALID`; the
job stays in `ANALYSED`. The C2 contract diagnostic — the coarse one-sided 95%
Clopper–Pearson **upper** bound versus the contract threshold 0.03, per required field,
with an explicit PASS/FAIL — is therefore structurally required, not optional logging.
All seven mandatory diagnostics are bound into the manifest.

---

## Identity

```text
DRIVER-PRESENT / UNSEALED EXECUTION IDENTITY (NOT the final seal):
a42b190959183a5e8218a0bd636db36f035f942adb06a67bd39cc8d9bbd0de2c
```

This is **not** the final identity. It is a diagnostic. The seal is frozen by a reviewer
only after the driver has been independently audited, and authorisation is a separate
task again.

**Driver identity binding, verified:** appending one comment line to the driver source
changes the execution identity; removing the driver changes it again, to a third value.
The driver's sha256 enters the preimage as `official_campaign_driver_sha256`, replacing
the `ABSENT` sentinel it carried before.

| artifact | sha256 | |
|---|---|---|
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | **unchanged** |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` | **unchanged** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | **unchanged** |
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | **unchanged** |
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | **unchanged** |
| validation plan JSON | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | **unchanged** |
| validation plan Markdown | `3f4715b465da295e21ad99a86390585c9eb7deac44a7810114a88f40aa4bf940` | **unchanged** |
| seed map | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | **unchanged** |
| execution seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` | **unchanged** |
| official campaign driver | `e75cb7bd5251ee5128c257613745e1b91822b141867063cd67143b35a28f5330` | **new** |
| execution identity | `a42b190959183a5e8218a0bd636db36f035f942adb06a67bd39cc8d9bbd0de2c` | moved, not forced |

Master seed `13785910525869478477` unchanged. Result schema
`e1a_v4_validation_result/2` and manifest schema `e1a_v4_validation_manifest/3` unchanged.

---

## Scientific authority

```text
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Verified by fixture: `delta_cross = 0.02`, `delta_abs = 0.05`,
`z_cross = z_abs = 1.959963985`, `alpha_geom = 0.005`, `alpha_1 = 0.004`,
`alpha_2 = 0.001`, `theta_cap = 5°`, `rank_tol = 1e-12`, complete true-bridge target
`0.90`. Eight cases with replicate counts 300 / 400 / 400 / 2000 / 400 / 400 / 400 / 200.
Release boundaries 279 / 5 / 2 / 13 / — / 6 / 4 / 188. The corrected OU generator
untouched (`dt = 0.00012`, `T_total = 240.0`, `n_samples = 2000000`). The frozen
foundation, baseline, design, contract, plan and seed map are byte-identical to the
starting coordinate.

**No contradiction between the frozen protocol and its implementation was found.** The
frozen design was neither reopened nor modified.

A fixture additionally asserts the driver restates no scientific constant: `0.005`,
`1.959963985`, `0.00012`, `2000000` and `279/300` appear nowhere in its source.

---

## Static tests

| suite | checks | pass/fail | RNG boundary involved |
|---|---:|---|---|
| `docs/e1a/validate_e1a_v4_contract.py` | 113 | pass | no |
| `test_e1a_v4.py` | 122 | pass | no |
| `test_e1a_v4_preexec.py` | 104 | pass | **yes** — sentinel asserts 0 |
| `test_e1a_v4_dispositions.py` | 64 | pass | no |
| `test_e1a_v4_size_semantics.py` | 79 | pass | no |
| `test_e1a_v4_repair.py` | 126 | pass | **yes** — sentinel asserts 0 |
| `test_e1a_v4_calibration_scope.py` | 105 | pass | **yes** — ordering boundary |
| `test_e1a_v4_case_scope.py` | 113 | pass | **yes** — ordering boundary |
| `test_e1a_v4_preexec_corrections.py` | 37 | pass | no |
| `test_e1a_v4_plan_coherence.py` | 113 | pass | **yes** — sentinel asserts 0 |
| `test_e1a_v4_coherence_hardening.py` | 138 | pass | **yes** — seal/driver gate |
| `test_e1a_v4_generating_model.py` | 113 | pass | **yes** — seal/driver ordering |
| `test_e1a_v4_contract_plan.py` | 75 | pass | no |
| `test_e1a_v4_release_authority.py` | 225 | pass | **yes** — sentinel asserts 0 |
| **`test_e1a_v4_campaign_driver.py`** | **255** | **pass** | **yes** — the unblind gate |
| **total** | **1782** | **0 failures** | 0 nonzero exits |

Fifteen suites. The real campaign runner was not run.

**Fixtures updated, and why.** Fifteen checks across four suites asserted that the
official campaign driver was ABSENT — a lifecycle fact this task deliberately changes.
None was deleted. Each was re-expressed to remove the driver **in its own sandbox** and
assert `DRIVER_ABSENT` there, so the driver-before-seal ordering guarantee — including the
original audit scenario, a seal nominating `plan.py` as the driver — is still tested, and
is now independent of which lifecycle stage the repository happens to be in. Two module
counts also moved: `VALIDATION_MODULES` 17 → 18.

---

## Stochastic boundary

```text
RNG OBJECTS = 0

RANDOM DRAWS = 0

TRAJECTORIES = 0

CALIBRATION EXECUTION = NOT RUN

VALIDATION CAMPAIGN = NOT RUN
```

The suite's `SentinelRNG` raises on construction of a real provider and on any draw;
both counters are asserted zero at the end. Branch-A fields are built from the frozen
contract without the measurement-error model applied (applying it needs a generator), and
calibration artifacts are deterministic fixtures whose columns are arithmetic. No
`results/e1a_v4_validation` directory exists in the repository.

---

## Lifecycle

```text
OFFICIAL CAMPAIGN DRIVER = PRESENT

FINAL EXECUTION SEAL = NOT FROZEN

EXPECTED FINAL EXECUTION IDENTITY = NULL

EXECUTION AUTHORISED = FALSE
```

State: **`DRIVER_PRESENT_UNSEALED`**. This is not execution-ready.

`python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation` exits 2
with `EXECUTION REFUSED: [EXECUTION_SEAL_NOT_FROZEN]`. The gate now advances past the
driver check — which is the visible consequence of implementing it — and stops at the
seal.

`python3 -m e1a_v4.validation.campaign_driver --plan-only` exits 0, plans 53,200 jobs and
reports `RNG OBJECTS: 0 RANDOM DRAWS: 0 TRAJECTORIES: 0`. `--preflight-only` is
supported. `run_campaign` called without `plan_only` refuses, naming the seal state and
the authorisation flag. There is no `--force`, `--skip-seal` or `--ignore-authorisation`
flag and no equivalent parameter; fixtures assert their absence in both the signature and
the source.

---

## Limitations

**The stochastic stage is not implemented.** Everything above the first random draw is
complete and statically tested; the draw itself, the OU trajectory generation, the real
calibration artifacts and the analysis are a separately authorised stage. `run_campaign`
refuses there explicitly rather than silently doing nothing.

**`JobExecution.analyse` takes an outcome rather than computing one.** The driver
orchestrates and gates; it does not yet call the endpoint analysis. That boundary is
where the next stage attaches, and the state machine already refuses to reach it early.

**The publication primitive's durability is asserted, not fault-injected.** `fsync`
ordering and `link()` atomicity are implemented exactly as the repository specifies and
the observable consequences are tested — mode, byte content, collision, leftover
temporary, truncation — but no test kills a process mid-publication. Proving crash safety
would need fault injection this stage does not have.

**Publication draws on an addendum whose precedence is narrow.** The meaning of
"published" is taken from Gate 1D-C's frozen primitive because E1a's own authority
defines the word nowhere. That is a judgement — a defensible one, and stated plainly
above rather than buried — but a reviewer who thinks E1a should define publication in its
own frozen authority should say so; it would be a contract amendment, not a driver
repair.

---

## Next stage

```text
OFFICIAL CAMPAIGN DRIVER INDEPENDENT AUDIT
READY
```

---

CAMPAIGN DRIVER IMPLEMENTED
