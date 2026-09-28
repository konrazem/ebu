# E1a v4 — PLAN COHERENCE AND EXECUTION-SEAL REPAIR

**AUTHORITY-INTEGRITY REPAIR. NO CAMPAIGN WAS RUN. NO RANDOM NUMBER WAS DRAWN.**

| | |
|---|---|
| work commit | `d8eb67773899eea925c18415dfc599b25fd0ec55` |
| work tree | `e9d5614409bc4ae1b0b9659972e4828cfc76c406` |
| starting HEAD | `25b3c7177ed95be59eb876c6f386772a7610652b` |
| branch | `gaussian/stage-a-environment` |
| push status | **NOT PUSHED** |

---

## Result

**The disagreement was reproduced, and it was repaired.**

Before editing anything, all **79** duplicated normative fields were extracted from both
representations and compared. **77 agreed. Exactly two disagreed**, and both are the fields the
independent auditor named:

| field | Markdown | JSON | |
|---|---|---|---|
| plan version | `1.5.0` | `1.6.0` | **disagree** |
| analysis procedure identity | `bc1c0fce3b9004aed5f6b4be2162bc876697536ee614b2e57f680f3a65dc283e` | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | **disagree** |

Everything else already agreed: all eight case identifiers, roles, replicate counts,
subcondition lists, calibration-required flags, calibration scopes, seed-family grants, release
endpoints, `fields_affected`, the contract/design/foundation/baseline identities, the
calibration artifact schema, the implementation work commit, `execution_authorised`, both output
schema versions, all 25 per-record fields, all 11 aggregate fields and all 11 failure
classifications.

**The disagreement was stale metadata only. No substantive scientific rule differed**, so §4's
stop condition was not triggered and the repair proceeded.

> **The identity is worse than stale.** A stale value would at least have been correct once.
> `bc1c0fce…` was **never** the analysis procedure identity, at any commit. Recomputed from each
> historical tree:
>
> | commit | true `procedure_identity(binding, {}, root)` |
> |---|---|
> | `475633c` | `1983ba3af64c…` |
> | `1a0c00e` | `af1177a9d322…` |
> | `8615405` | `af1177a9d322…` |
> | `5727e10` | **`dd2ed732db43…`** |
> | `cb76b84` → `25b3c71` | **`dd2ed732db43…`** |
>
> It also matches no configuration variant: `{}`, `None`,
> `{"stage": "bounded_implementation"}`, `{"stage": "synthetic_validation"}`,
> `{"stage": "pre_execution_repair"}` and `{"stage": "validation"}` were all recomputed at
> `5727e10` and none produced it, nor did the sha256 of the plan Markdown, plan JSON or seed
> map. The Markdown asserted a frozen identity that the package has never had.

---

## Root cause

**Why the stale metadata survived while preflight passed.**

`bind_execution` called exactly one Markdown/JSON comparison, `require_output_schema_agreement`,
and that function reads **only section 9**:

```python
section = text.split("## 9. Output schema", 1)
...
if (f"`{schema['record_schema']}`" not in body or ...
```

The section-1 frozen-identity table and the version line were **never compared to anything**.
The `frozen_identities.analysis_procedure_identity` check in preflight compared the **JSON** to
a live recomputation — which passed, because the JSON was right — and nothing ever looked at
what the Markdown claimed. So the normative human rendering could assert an identity the
package had never computed, and the official preflight would print `PREFLIGHT PASSED`.

**How each defect entered.**

| defect | commit | what happened |
|---|---|---|
| analysis identity | `5727e10` *Repair E1a v4 validation calibration and seed enforcement* | Both files were edited in the **same commit**. The JSON received the true recomputed value `dd2ed732…`; the Markdown table cell received `bc1c0fce…`. The Markdown note in the *same hunk* correctly records the superseded value `af1177a9…`, so the document contradicted itself. |
| plan version | `8ea81ea` *Adopt E1a v4 pre-execution generator corrections* | The JSON was bumped `1.5.0` → `1.6.0`. The Markdown **was edited** in that commit (9 lines) but its version line was not touched. |

A second contributing factor: the normative Markdown was **outside the execution-identity
preimage**. A stale Markdown therefore moved no identity, so nothing downstream could notice.

---

## Authority reconciliation

### Which representation is the adopted authority, and why

Not "JSON wins because it is JSON." `dd2ed732…` is the value
`procedure_identity(binding, {}, root)` **actually produces**, verified by recomputation at
every commit from `5727e10` to `HEAD`. It is also the value carried independently by the JSON
plan and by four committed reports:

- `docs/e1a/E1A_V4_PREEXEC_REPAIR_REPORT.md` (recording the `af1177a9…` → `dd2ed732…` move)
- `docs/e1a/E1A_V4_CALIBRATION_SCOPE_REPORT.md`
- `docs/e1a/E1A_V4_CASE_SCOPE_REPAIR_REPORT.md`
- `docs/e1a/E1A_V4_PREEXEC_CORRECTION_ADOPTION_REPORT.md`

`bc1c0fce…` appeared in **exactly one place in the entire repository**: the Markdown table cell.
It was the sole dissenter and was demonstrably wrong. The Markdown cell was corrected to the
value the package computes; **nothing was reconciled by preference.**

### Old → new

| field | old | new |
|---|---|---|
| Markdown plan version | `1.5.0` | **`1.7.0`** |
| JSON plan version | `1.6.0` | **`1.7.0`** |
| Markdown analysis identity | `bc1c0fce3b9004aed5f6b4be2162bc876697536ee614b2e57f680f3a65dc283e` | **`dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f`** |
| JSON analysis identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | *unchanged* |
| record schema | `e1a_v4_validation_result/2` | *unchanged* |
| manifest schema | `e1a_v4_validation_manifest/2` | *unchanged* |
| authority block schema | *did not exist* | **`e1a_v4_plan_authority/1`** |
| execution seal schema | *did not exist* | **`e1a_v4_execution_seal/1`** |
| JSON `frozen_identities.execution_identity` | `""` | **removed** |
| JSON `final_expected_execution_identity` | *did not exist* | **`null`**, with explicit state and location |
| JSON `execution_seal.state` | *did not exist* | **`PRE_DRIVER`** |
| contract / design / foundation / baseline identity | | *unchanged, both sides* |
| every case id, role, replicate count, subcondition, calibration flag, scope, seed grant, endpoint | | *unchanged, both sides — they already agreed* |

The version went to `1.7.0`, not `1.6.0`, because this commit is itself a plan change: it adds
the coherence surface and the sealing architecture.

---

## Coherence surface

Preflight now compares a declared **13-key surface**, rebuilt from the JSON plan and compared
key by key:

| key | contents |
|---|---|
| `plan_id` | plan identifier |
| `plan_version` | frozen version string |
| `execution_stage` | declared stage |
| `execution_authorised` | the authorisation flag |
| `execution_seal_state` | `PRE_DRIVER` / `FROZEN` |
| `calibration_scope` | campaign-level calibration architecture |
| `frozen_identities` | contract, design, foundation, baseline, analysis identity, implementation work commit, calibration artifact schema, contract version — **8 scalars** |
| `implementation_file_hashes_digest` | sha256 over the canonical 12-module hash map |
| `seed_map_sha256` | the frozen seed map |
| `output_schema` | directory, record schema, manifest schema, 25 per-record fields, 11 aggregate fields |
| `failure_classifications` | all 11, in order |
| `cases` | all 8, each over an **11-field** per-case surface |
| `release_criteria` | 6 assurance rows (quantity, target, replicates, bound, confidence level) + the final campaign verdict, rule and 10 requirements |

Per-case surface (11 fields × 8 cases): `case_id`, `role`, `replicate_count`,
`subcondition_count`, `subconditions`, `requires_block1_calibration`, `calibration_scope`,
`allowed_seed_families`, `primary_release_endpoint`, `fields_affected`, `block1_role`.

Free prose is **not** compared, and no attempt is made to prove English paragraphs
byte-equivalent.

### Mechanism — why this is not prose scraping

The chosen mechanism is **option A plus a rendering check**, and both halves are necessary.

**Layer 1 — a generated block.** The Markdown carries one anchor-delimited `json` block
(section 1a), emitted by `e1a_v4.validation.coherence.render_authority_block` from the JSON
plan. Preflight rebuilds it and compares. Nothing is inferred from free text. Structurally it is
fail-closed: an absent, duplicated, malformed or wrong-schema block refuses, as does an
undeclared key or a missing surface key.

**Layer 2 — the human rendering.** A generated block alone **would not have caught the defect it
exists for**: the human table could still drift from the block while both block and JSON agreed.
So preflight also verifies that the human-visible renderings match the block — the version line,
all **7** section-1 identity rows, the execution-authorisation sentence, and the `role`,
`replicate count`, `subconditions (n)`, `requires Block-1 calibration`, `calibration scope`,
`allowed seed families` and `primary release endpoint` rows of **every** case table. Extraction
is anchored on exact row labels inside named sections; **an absent or ambiguous match is a
refusal, never a silent skip.**

This layer is directly tested: regenerate the block from a changed JSON, leave the human table
stale, and preflight still refuses — the exact historical failure.

---

## Preflight

Every fixture below is a deliberate disagreement. **All refuse, and all refuse with
`RNG_CALL_COUNT` delta = 0**, verified by a sentinel RNG provider that raises on any draw.

| fixture | result |
|---|---|
| same version / identity | **PASS** (positive control) |
| Markdown version changed only | **REFUSE** |
| Markdown analysis identity changed only | **REFUSE** |
| JSON version changed only | **REFUSE** |
| JSON analysis identity changed only | **REFUSE** |
| output-schema version mismatch | **REFUSE** |
| case replicate-count mismatch | **REFUSE** |
| case subcondition mismatch | **REFUSE** |
| calibration-required mismatch | **REFUSE** |
| case calibration-scope mismatch | **REFUSE** |
| `execution_authorised` mismatch | **REFUSE** |
| case allowed-seed-families mismatch | **REFUSE** |
| case role / release endpoint / Block-1 role / fields-affected mismatch | **REFUSE** |
| block absent / duplicated / malformed / wrong schema | **REFUSE** |
| undeclared key in the block / missing surface key | **REFUSE** |
| duplicated or absent human row (ambiguity) | **REFUSE** |
| block regenerated but **human** version line stale | **REFUSE** |
| block regenerated but **human** identity table stale | **REFUSE** |
| block regenerated but **human** case table stale | **REFUSE** |
| JSON + block + prose changed **consistently** | **ACCEPT** (discrimination control) |

The last row matters: it shows the gate discriminates rather than always refusing.

### A weakening found and repaired in the existing suite

Adding checks earlier in `bind_execution` silently changed what eight existing fixtures in
`test_e1a_v4_preexec.py` were testing: with the sandbox not carrying the new seal file, and with
JSON edits now tripping the coherence check first, those fixtures refused for the **wrong
reason**. That is precisely the class of defect this task exists to remove, so it was repaired
rather than accepted. The sandbox now copies the seal, fixtures regenerate the block, and each
of the eight was re-verified to refuse on its intended path:

| fixture | refusal now reported |
|---|---|
| contract mismatch | `contract identity is 553b5155…` |
| frozen execution-identity mismatch | `execution identity is 89ee5e80…, frozen ffff…` |
| analysis identity mismatch | `analysis procedure identity is dd2ed732…` |
| implementation file hash mismatch | `e1a_v4/__init__.py changed since the freeze` |
| hand-edited seed map | `seed map does not reproduce from its own declared derivation` |
| master seed mismatch | `seed map does not reproduce from its own declared derivation` |
| output collision | `output collision, results/e1a_v4_validation already contains results` |
| unexpected execution stage | `unexpected execution stage 'something_else'` |

---

## Execution-seal architecture

### The state machine

| state | meaning | `expected_execution_identity` | preflight | execution |
|---|---|---|---|---|
| **`PRE_DRIVER`** | official campaign driver absent | **MUST be `null`** | may pass | **REFUSES** |
| **`FROZEN`** | driver implemented and independently audited; a reviewer has frozen the expected identity | **MUST be 64-hex** | may pass | eligible **only** if the recomputation matches **and** `execution_authorised` is true |
| **AUTHORISED** | not a seal state — `execution_authorised = true`, set by a **separate** task | | | the final precondition |

A `FROZEN` seal is **not** an authorisation, and an authorisation without a `FROZEN` seal is
refused. The two are deliberately independent.

### Avoiding the self-reference

```
execution identity = H( validation module hashes (12),
                        analysis procedure identity,
                        plan JSON sha256,
                        plan MARKDOWN sha256,          <- joined the preimage in 1.7.0
                        seed-map sha256 )

execution seal     = an EXTERNAL assertion of the expected execution identity
                     docs/e1a/e1a_v4_execution_seal.json
                     DELIBERATELY EXCLUDED from the preimage
```

The expected value cannot live in any preimage input: writing it into the plan changes the
plan's sha256 and therefore changes the value it records — an impossible fixed point. The
assertion therefore sits **outside** the package it describes. This is tested directly: writing
the expected identity into the seal leaves the recomputed identity **bit-identical**, while
appending one line to the normative Markdown **does** move it.

### Not-yet-frozen versus forgotten

The superseded plan slot held the empty string `""`, which could express neither state, and
which preflight **silently skipped** (`if ... not in ("", None)`). Now:

- **`null`** in `final_expected_execution_identity`, paired with `state = PRE_DRIVER`, means
  *deliberately not yet frozen*;
- an **absent** slot, an **absent** seal file, an **absent** state, or an **absent**
  `expected_execution_identity` key is treated as **FORGOTTEN** and **refuses**;
- `PRE_DRIVER` with a non-null expected identity refuses; `FROZEN` with a null or malformed one
  refuses; an undeclared state refuses; a plan/seal state disagreement refuses.

### The execution gate

1. the official campaign driver exists on disk
2. the external execution seal is `FROZEN`
3. the recomputed execution identity equals the independently frozen seal
4. `execution_authorised` is true

Ordered most-fundamental-first, so a refusal never reads as *"just flip the authorisation
flag"* when the driver that would do the work does not exist. `ExecutionNotAuthorised` is now
the umbrella type, with `CampaignDriverAbsent`, `ExecutionSealNotFrozen`,
`ExecutionIdentityUnsealed` and `ExecutionAuthorisationMissing` naming which precondition is
missing. Every branch refuses before the RNG factory is touched.

### Lifecycle, tested

| scenario | outcome | refusal type |
|---|---|---|
| `PRE_DRIVER` + `authorised = false` | preflight-only **succeeds**; execution **refuses** | `CampaignDriverAbsent` |
| `PRE_DRIVER` + `authorised = true` | **refuses** before RNG | `ExecutionNotAuthorised` |
| driver present, seal **missing** | **refuses** | seal is FORGOTTEN |
| driver present, seal `PRE_DRIVER` | **refuses** | `ExecutionSealNotFrozen` |
| seal `FROZEN`, identity **mismatch** | **refuses** | `ExecutionIdentityUnsealed` |
| seal `FROZEN` + match, `authorised = false` | **refuses** | `ExecutionAuthorisationMissing` |
| seal `FROZEN` + match + `authorised = true` | gate is **ELIGIBLE** | — |

The last row is a **sentinel/mock boundary only**: `require_execution_gate` returns cleanly, and
`run` then stops at the unimplemented-execution-path refusal. **No driver was implemented, no
RNG object was created and no draw occurred**, confirmed by the sentinel counter at 0.

---

## Current execution identity

```
PRE-DRIVER PACKAGE EXECUTION IDENTITY
9e8f1401bbc0d98f1edccb0932957477f8020c06fc0b19555a9ad7346cb41649
```

**This is NOT the final execution seal.** It is a diagnostic. It moved from the superseded
`e973ce655a0798bb9da47026cc98bb601973fbe75c4ce55a34da2e5bada55037` because two validation
modules were added, `plan.py`/`runner.py` changed, the plan JSON and Markdown changed, and the
Markdown entered the preimage. It **will** change again when the official campaign driver is
implemented and added to `VALIDATION_MODULES`.

---

## Final-seal requirement

The final expected execution identity will be frozen **only after**:

1. the official campaign driver (`e1a_v4/validation/campaign_driver.py`) is implemented;
2. it is **independently audited**;
3. it is added to `VALIDATION_MODULES`, so it enters the execution-identity preimage;
4. Markdown and JSON authority representations agree;
5. contract, analysis, seed-map and validation-plan identities all match;
6. a reviewer writes the recomputed identity into the seal and sets `state = FROZEN`.

Only then may a **separate** final authorisation task set `execution_authorised = true`.
Freezing today's identity would seal a package whose executing component does not exist.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Verified by explicit test, not assertion:

| rule | value | |
|---|---|---|
| `delta_cross` / `z_cross` | `0.02` / `1.959963985` | unchanged |
| `delta_abs` / `z_abs` | `0.05` / `1.959963985` | unchanged |
| `alpha_geom` / `alpha_1` / `alpha_2` | `0.005` / `0.004` / `0.001` | unchanged |
| `theta_cap_deg` / `rank_tol` | `5.0` / `1e-12` | unchanged |
| primary `sigma_psi` | `0.5` deg | unchanged |
| complete-pipeline target | `0.90` | unchanged |
| G1 / G2 / C2 / C3 / C4 thresholds | 188/200, 4/400, 5/400, 2/400, 13/2000 | unchanged |
| replicate counts | 300, 400, 400, 2000, 400, 400, 400, 200 | unchanged |
| calibration scopes | 6 × `REPLICATE_CONDITIONAL`, 2 × `NOT_APPLICABLE` | unchanged |
| C7 / C8 no-calibration semantics | | unchanged |
| C3 release-vs-diagnostic semantics | | unchanged |
| rotated OU correction, modal ordering, calibration condition, subcondition semantics, stream hierarchy | | unchanged |
| master seed and every seed value | | unchanged |

No analysis-layer module was touched: the analysis procedure identity is **bit-identical**.

---

## Identities

| item | value | |
|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | **UNCHANGED** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | **UNCHANGED** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | **UNCHANGED** |
| working theory baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` | **UNCHANGED** |
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | **UNCHANGED** |
| seed map | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | **UNCHANGED** |
| master seed | `13785910525869478477` | **UNCHANGED** |
| validation plan JSON | `7d2395e7…` → `64a4074caa3ccd7e044e756b96b896b9e2c8c95cc04e0c1078ce96a7c1f7675d` | changed |
| validation plan Markdown | `6e590e87…` → `ae7de223dbe5df536f61cf943dfbc654120bef2bb00b0a6a59b60c664e6ba909` | changed |
| execution seal file | `b02de208e03ccd22ad39d8d932fdf6366d60c4d273d3ed1b336696feac751807` | new |
| **pre-driver execution identity** | `e973ce65…` → `9e8f1401bbc0d98f1edccb0932957477f8020c06fc0b19555a9ad7346cb41649` | changed |
| plan version | `1.6.0` → `1.7.0` | |
| record / manifest schema | `e1a_v4_validation_result/2` / `e1a_v4_validation_manifest/2` | **UNCHANGED** |
| authority block schema | `e1a_v4_plan_authority/1` | new |
| execution seal schema | `e1a_v4_execution_seal/1` | new |

---

## Static tests

Complete package, every applicable static/pure suite:

| suite | checks | failures |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` — contract/design authority | 113 | 0 |
| `test_e1a_v4.py` — bounded implementation | 122 | 0 |
| `test_e1a_v4_preexec.py` — pre-execution | **97** | 0 |
| `test_e1a_v4_dispositions.py` — dispositions | 64 | 0 |
| `test_e1a_v4_size_semantics.py` — size semantics | 78 | 0 |
| `test_e1a_v4_repair.py` — B1/B2/B3 repair | 126 | 0 |
| `test_e1a_v4_calibration_scope.py` — calibration scope | 105 | 0 |
| `test_e1a_v4_case_scope.py` — case scope | 113 | 0 |
| `test_e1a_v4_preexec_corrections.py` — rotated OU correction | 37 | 0 |
| `test_e1a_v4_plan_coherence.py` — **plan coherence + seal lifecycle (new)** | **97** | 0 |
| **TOTAL** | **952** | **0** |

Movement from the previous 852: **+97** new plan-coherence and seal-lifecycle checks, **+3** in
the pre-execution suite (the Markdown-in-preimage check and two additional validation modules
present-on-disk checks). **No earlier coverage was removed**; the two repaired fixtures test
strictly more than before.

`docs/e1a/e1a_v4_execution_feasibility_probe.py` also re-run: completes, no RNG.

---

## Execution state

```
execution_authorised = false

official campaign driver = ABSENT

final execution seal = NOT FROZEN

RNG OBJECTS = 0

RANDOM DRAWS = 0

TRAJECTORIES = 0

VALIDATION CAMPAIGN = NOT RUN
```

The official execution command was run and **refused**, exit code 2:

```
$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
EXECUTION REFUSED: the official campaign driver e1a_v4/validation/campaign_driver.py
is ABSENT. A passing static preflight is not an execution clearance.
  RANDOM DRAWS: 0   TRAJECTORIES: 0
```

`results/e1a_v4_validation` does not exist. No calibration artifact, trajectory or result record
was produced at any point in this task.

---

## Limitations and unresolved questions

- **End-to-end Branch-A provenance remains open**, unchanged by this task. The calibration lock
  enforces condition *consistency*, not that the condition came from that replicate's actual
  Branch-A measurement. Recorded as a mandatory, unsatisfied driver requirement.
- The seal asserts an expected identity but cannot, by itself, establish that the reviewer who
  froze it audited the driver. That remains a **procedural** control, and the seal records it
  explicitly rather than implying otherwise.
- `bc1c0fce…` could not be attributed to any computation. Six configuration variants and three
  file digests were tested at the commit that introduced it, and none reproduce it; its origin
  is therefore **undetermined**, not explained.
- The coherence surface covers duplicated machine-relevant authority. Prose that exists only in
  the Markdown is unverified by construction, and the surface must be extended by hand if a new
  normative field is later duplicated.

---

## Next stage

```
E1a v4 official campaign-driver implementation
READY FOR AUTHORISATION
NOT STARTED
```

---

```
PLAN COHERENCE REPAIRED
```
