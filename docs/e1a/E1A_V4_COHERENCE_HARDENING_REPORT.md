# E1a v4 — COHERENCE HARDENING AND CANONICAL DRIVER BINDING

**AUTHORITY-INTEGRITY HARDENING. NO CAMPAIGN WAS RUN. NO RANDOM NUMBER WAS DRAWN.**

| | |
|---|---|
| work commit | `9a1f058fd23d73a304868c04124206ac24189f21` |
| work tree | `371694c0dd6aa142f7fe596e99840edd1e669d41` |
| starting HEAD | `66fdd7352f81be0e23bd88c895fa382d9a376e78` |
| branch | `gaussian/stage-a-environment` |
| push status | **NOT PUSHED** |

---

## Result

**All three independent-audit blockers were reproduced at the starting HEAD before
any edit, and all three are closed.** The non-blocking regression weakness is also
repaired.

| blocker | reproduced | closed |
|---|---|---|
| **A** scientifically meaningful drift still passes coherence | **YES — 9 / 9 probes ACCEPTED** | yes |
| **B** duplicate JSON keys accepted by ordinary parsing | **YES — block, nested record and plan JSON all ACCEPTED** | yes |
| **C** the seal can name an arbitrary existing file as the driver | **YES — the complete gate PASSED with no driver in existence** | yes |
| *(non-blocking)* fixtures assert refusal but not the reason | **YES** | yes |

### A — reproduction

The auditor named four examples. All four reproduced, and probing the same class
found five more:

| probe | before |
|---|---|
| visible `fields affected` changed only in the Markdown | **ACCEPTED** |
| visible primary `sigma_psi` wording changed only in the Markdown | **ACCEPTED** |
| visible C1 release threshold `279/300` → `240/300`, Markdown only | **ACCEPTED** |
| JSON `feeds_primary_claim` inverted, generated block regenerated | **ACCEPTED** |
| visible C7 threshold `4/400` → `40/400`, Markdown only | **ACCEPTED** |
| visible C8 threshold `188/200` → `100/200`, Markdown only | **ACCEPTED** |
| JSON C7 false-bridge `beta_true` altered, block regenerated | **ACCEPTED** |
| JSON C8 `scale_factors` altered, block regenerated | **ACCEPTED** |
| JSON C1 `sigma_psi_deg` altered, block regenerated | **ACCEPTED** |

**Why.** The generated block carried only case-level *scalars* — the entire
subcondition payload was reduced to a list of `subcondition_id` strings — and the
human check read only seven case rows (`role`, `replicate count`, `subconditions
(n)`, `requires Block-1 calibration`, `calibration scope`, `allowed seed
families`, `primary release endpoint`). So `fields_affected`,
`branch_a_uncertainty`, `formal_pass_fail_criterion`, `feeds_primary_claim`,
`g3_role`, `beta_true`, `scale_factors`, `rho`, `sigma_k`, the adopted-rules
table, the assurance table and the release rules were **all outside the surface**.

### B — reproduction

`json.loads` resolves a duplicate object key by silently keeping the **last**
occurrence. A human reads the **first**. The decisive fixture puts the hostile
value first and the correct value last, so the parser sees exactly what it
expects while every reader sees the tampered document:

```json
{ "plan_version": "0.0.1-TAMPERED",
  "plan_version": "1.8.0" }
```

Before: **ACCEPTED** in the generated authority block, **ACCEPTED** for a nested
duplicate inside a case record, and **ACCEPTED** in the authoritative plan JSON
itself.

### C — reproduction

`driver_present` was `os.path.exists` on whatever path the seal named. Every one
of `e1a_v4/validation/plan.py`, `e1a_v4/validation/seeds.py`,
`docs/e1a/e1a_v4_seed_map.json` and `AGENTS.md` satisfied it. With a correctly
**FROZEN** seal whose expected identity matched the recomputation, naming
`e1a_v4/validation/plan.py` as the driver, `require_execution_gate` **PASSED** —
clearing a campaign that had no driver at all. This was the most serious of the
three: a gate that cannot tell whether the thing it is about to run exists.

---

## Normative coherence surface

The surface is now an **enumerable specification**, not a hand-counted list.
Every count below is produced by `specification_counts`, read out of the
implementation; none is quoted by hand.

| quantity | value |
|---|---:|
| **duplicated normative keys (BOTH)** | **431** |
| of which human-rendered | 422 |
| of which rendered only in the generated authority block | 9 |
| **Markdown-only keys** | **0** |
| top-level keys classified `BOTH` | 14 |
| top-level keys classified `JSON_ONLY` | 23 |
| per-case keys classified `BOTH` | 30 |
| per-case keys classified `JSON_ONLY` | 3 |
| per-subcondition keys classified `BOTH` | 10 |
| per-subcondition keys classified `JSON_ONLY` | 0 |

**Totality is enforced, not assumed.** `require_specification_totality` refuses if
the plan carries any top-level, per-case or per-subcondition key the
specification does not classify:

```
[PLAN_SURFACE_UNDECLARED] the plan carries top-level keys the normative coherence
specification does not classify: ['an_undeclared_authority_section']
```

This is what prevents the defect recurring: authority cannot be added to the plan
and quietly go unchecked.

**The nine block-only keys**, each with no separate human rendering — the block
*is* their Markdown rendering: `plan_id`, `execution_stage`,
`calibration.calibration_scope`, `output_schema.directory`, `seed_map_sha256`,
`frozen_identities.contract_version`,
`frozen_identities.implementation_file_hashes_digest`, `driver.module`,
`driver.entry_point`.

**`JSON_ONLY` classifications** are rationale, provenance, narrative and
mechanism-description — for example `calibration_scope_rationale` (the scope
itself is `BOTH`), `allowed_seed_families_rationale` (the grants are `BOTH`),
`created`, `normative_pair`, `superseded_package`, and
`plan_authority_coherence`, which describes the checking mechanism and would be
self-referential as checked authority. Each carries a stated reason in the
specification, and a test asserts every reason is non-empty.

### Enumerable views

`normative_json_view(plan, root)` and `normative_markdown_view(root)` build the
**same flat dotted canonical mapping**, and the comparison names the exact
mismatching key:

```
[PLAN_CASE_MISMATCH] MARKDOWN/JSON AUTHORITY DISAGREEMENT at
'cases.C1_true_bridge_complete.formal_pass_fail_criterion': ...
```

---

## Human-visible authority

`AGENTS.md` makes the Markdown the *normative human rendering*. A generated block
alone cannot discharge that, as the audit showed: the block can be right while the
visible protocol is stale. So the normative visible tables are now **generated
from the same canonical data** and verified byte-exact.

| region | anchor-delimited, generated | covers |
|---|---|---|
| **cases** | yes | all 8 case sections: purpose, 24 declared rows, **every subcondition's complete parameters**, and the pass/fail criterion |
| **adopted rules** | yes | the 13 frozen decision rules and the forbidden list |
| **assurance** | yes | all 6 release criteria: quantity, target, confidence, estimator, bound, R, acceptance rule |
| **release rules** | yes | G1 / G2 / G3 gaps and resolutions, and the final-campaign verdict, rule and 10 numbered requirements |
| **authority block** | yes | the complete 431-key flat normative view |

Parsed and compared **outside** generated regions: the plan version line, all 7
section-1 frozen-identity rows, the `execution_authorised` sentence, the
execution-seal state line, the canonical driver line, the section-9 output schema
and the section-10 failure classifications.

Two consequences worth stating plainly:

- **Every subcondition parameter is now visible to a reader.** `feeds_primary_claim`,
  `g3_role`, `beta_true`, `scale_factors`, `rho` and `sigma_k` previously existed
  only in the JSON, so a reader could not see them drift. They are rendered per
  subcondition, with the note that a parameter not rendered is not declared.
- **Section 12b no longer restates the final-campaign requirements.** It carried a
  second hand-maintained copy of the release rules, unchecked. A second copy of a
  release rule is exactly the drift this package now refuses, so that section
  points at the generated region instead.

The assurance table also had a **pre-existing rendering defect**: five of its six
rows were missing the `estimator` column, silently shifting every later cell.
Generating it from the JSON fixed that as a side effect.

**Content preservation was verified, not assumed.** Of 476 distinct informative
tokens in the superseded hand-written section 3, exactly one is absent from the
new document: the literal `True`, because a boolean now renders as `` `true` ``
in JSON form. No scientific value was lost; the generated rendering is a strict
superset, adding Block-1 role, fields requiring calibration, the artifact basis,
the classification note, the calibration-not-required reason and the full
subcondition payloads.

---

## Strict JSON

`e1a_v4/validation/strict_json.py` parses every authoritative document through an
`object_pairs_hook` that refuses a repeated key at **any depth**.

| fixture | result |
|---|---|
| duplicate top-level key | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate nested key | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate inside a case record | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate inside a subcondition record | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate three levels deep | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate in the generated authority block, hostile first / correct last | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate in the authoritative plan JSON | **REFUSE** `PLAN_DUPLICATE_KEY` |
| duplicate in the execution seal | **REFUSE** `PLAN_DUPLICATE_KEY` |
| valid unique-key JSON | **parses normally** |

**Neither first nor last is adopted.** Normalising to either would pick a winner
between two contradictory statements; an authoritative document that says two
things is ambiguous, and the only safe resolution is refusal.

Applied to: `docs/e1a/e1a_v4_synthetic_validation_plan.json`,
`docs/e1a/e1a_v4_seed_map.json`, the embedded authority block, the per-subcondition
payloads inside the generated case region, and
`docs/e1a/e1a_v4_execution_seal.json`.

---

## Generated block ambiguity

| fixture | result |
|---|---|
| block absent | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| two blocks | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| nested anchors | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| malformed JSON | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| wrong block schema | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| more than one ```` ```json ```` fence | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| `field_count` disagreeing with the field map | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| unknown top-level block key | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| unknown normative key in `fields` | **REFUSE** `PLAN_SURFACE_UNDECLARED` |
| missing required normative key | coded by key class |
| any generated region not a byte-exact re-render | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |
| a generated region absent or duplicated | **REFUSE** `PLAN_AMBIGUOUS_BLOCK` |

The unknown-top-level-key check was **added during this work**, after the
duplicate-key probe exposed it: an extra top-level key was neither a duplicate nor
a declared field, so it would be read by a human and ignored by every check — the
same two-readers ambiguity duplicate keys create.

---

## Canonical driver declaration

Declared in **`e1a_v4/validation/driver.py`**:

```
module      : e1a_v4.validation.campaign_driver
path        : e1a_v4/validation/campaign_driver.py
entry point : run_campaign
state       : ABSENT
```

The path was chosen prospectively. **The file is not created, and no placeholder
stands in for it** — a placeholder would satisfy the existence test and defeat the
gate under audit. Lifecycle states beyond `ABSENT` are exercised only with
throwaway sandbox fixtures, and the repository's
`e1a_v4/validation/` contains no `campaign_driver.py`.

**Identity binding.** `driver.py` is one of the 15 `VALIDATION_MODULES` hashed
into the execution identity, so changing the declared module or path changes the
pre-driver execution identity. Separately, the driver's **own file sha256** enters
the execution-identity preimage — or the sentinel `"ABSENT"` while it does not
exist — so the identity moves the moment a real driver appears. That is precisely
why today's value is a diagnostic and not a seal.

**Interface, machine-checkable without executing anything.** The declared
`run_campaign` entry point is verified by parsing the module's AST. Importing
would execute driver code, which this stage forbids.

---

## Seal authority

The seal **cannot redefine the driver**:

| fixture | result |
|---|---|
| seal restates the canonical path | accepted (reporting only) |
| seal restates `e1a_v4/validation/plan.py` | **REFUSE** `DRIVER_IDENTITY_MISMATCH` |
| seal restates `e1a_v4/validation/seeds.py` | **REFUSE** `DRIVER_IDENTITY_MISMATCH` |
| seal restates `AGENTS.md` | **REFUSE** `DRIVER_IDENTITY_MISMATCH` |
| seal restates `docs/e1a/e1a_v4_seed_map.json` | **REFUSE** `DRIVER_IDENTITY_MISMATCH` |
| seal carries an **authoritative** `official_campaign_driver_module` key | **REFUSE** `EXECUTION_SEAL_MALFORMED` |
| **the audit scenario**: FROZEN seal, matching identity, naming `plan.py` | **REFUSE** `DRIVER_IDENTITY_MISMATCH` |

`ExecutionSeal.driver_module` always returns the canonical declaration, whatever
the seal wrote, and `driver_present` accepts and **ignores** a caller-supplied
path so no caller can steer the answer.

---

## Lifecycle

Two independent axes, deliberately not collapsed.

**Driver:** `ABSENT` → `PRESENT` (file exists and declares `run_campaign`).
**Seal:** `PRE_DRIVER` → `FROZEN`; then, separately, `execution_authorised = true`.

| state | outcome | code |
|---|---|---|
| `PRE_DRIVER` + canonical driver ABSENT | preflight passes; **execution refuses** | `DRIVER_ABSENT` |
| `PRE_DRIVER` + `execution_authorised = true` | **refuses before RNG** | `DRIVER_ABSENT` |
| canonical path declared but absent, seal otherwise perfect | **refuses** | `DRIVER_ABSENT` |
| driver present but no declared entry point | **refuses** | `DRIVER_IDENTITY_MISMATCH` |
| driver present and identity-bound, seal missing | **refuses** | `EXECUTION_SEAL_MALFORMED` |
| driver present, seal `PRE_DRIVER` | **refuses** | `EXECUTION_SEAL_NOT_FROZEN` |
| seal `FROZEN`, expected identity mismatch | **refuses** | `EXECUTION_IDENTITY_MISMATCH` |
| seal `FROZEN` and matching, `execution_authorised = false` | **refuses** | `EXECUTION_NOT_AUTHORISED` |
| driver + seal + identity + authorisation | **gate ELIGIBLE** | — |

The final row is a **sentinel/mock boundary only**: `require_execution_gate`
returns cleanly against a sandbox fixture, and `run` then stops at the
unimplemented-execution-path refusal. No real driver was implemented, no RNG
object was created, no draw occurred — the sentinel counter stands at 0.

**Coherence and immutability are different jobs, and that boundary is tested.** A
change propagated to *both* representations is coherent by construction, and
coherence correctly accepts it; what catches it is the execution identity, which
that change does move. The seal is deliberately still `PRE_DRIVER`, so nothing is
frozen against that identity yet. Both behaviours are asserted.

---

## Refusal codes

26 stable codes. They live in the **validation** layer, not in `e1a_v4/numerics.py`,
because that module is one of the twelve whose hash the analysis procedure
identity binds — adding codes there would move a scientific identity for an
operational reason.

```
PLAN_VERSION_MISMATCH              CONTRACT_IDENTITY_MISMATCH
PLAN_ANALYSIS_IDENTITY_MISMATCH    FROZEN_SOURCE_MISMATCH
PLAN_IDENTITY_MISMATCH             IMPLEMENTATION_HASH_MISMATCH
PLAN_CASE_MISMATCH                 SEED_MAP_NOT_REPRODUCIBLE
PLAN_SUBCONDITION_MISMATCH         UNEXPECTED_EXECUTION_STAGE
PLAN_RELEASE_RULE_MISMATCH         OUTPUT_COLLISION
PLAN_ADOPTED_RULE_MISMATCH         DRIVER_ABSENT
PLAN_SURFACE_MISMATCH              DRIVER_IDENTITY_MISMATCH
PLAN_SURFACE_UNDECLARED            EXECUTION_SEAL_MALFORMED
PLAN_DUPLICATE_KEY                 EXECUTION_SEAL_STATE_DISAGREEMENT
PLAN_AMBIGUOUS_BLOCK               EXECUTION_SEAL_NOT_FROZEN
PLAN_STRUCTURE_INVALID             EXECUTION_IDENTITY_MISMATCH
EXECUTION_GATE_REFUSED             EXECUTION_NOT_AUTHORISED
```

`EXECUTION_GATE_REFUSED` is the umbrella: `DriverAbsent`,
`ExecutionSealNotFrozen`, `ExecutionIdentityUnsealed` and
`ExecutionAuthorisationMissing` all subclass it, so a refusal can never be read as
*"just flip the authorisation flag"* while naming which precondition is missing.
`EXECUTION_IDENTITY_MISMATCH` is deliberately shared by two raise sites — the
plan's frozen slot and the external seal — because it is one condition asked of
two authorities. The code is embedded in the message, so it survives into logs.

---

## Old-fixture reason checks

The non-blocking weakness was real and had already bitten: when the coherence and
seal checks were added earlier in `bind_execution`, **all eight** fixtures below
began refusing before reaching the path each was written to exercise, and all
eight still reported PASS. Each now asserts its exact code.

| fixture | asserted code | verified |
|---|---|---|
| contract identity mismatch | `CONTRACT_IDENTITY_MISMATCH` | PASS |
| execution identity mismatch | `EXECUTION_IDENTITY_MISMATCH` | PASS |
| analysis identity mismatch | `PLAN_ANALYSIS_IDENTITY_MISMATCH` | PASS |
| implementation hash mismatch | `IMPLEMENTATION_HASH_MISMATCH` | PASS |
| edited seed family | `SEED_MAP_NOT_REPRODUCIBLE` | PASS |
| edited master seed | `SEED_MAP_NOT_REPRODUCIBLE` | PASS |
| output collision | `OUTPUT_COLLISION` | PASS |
| unexpected execution stage | `UNEXPECTED_EXECUTION_STAGE` | PASS |

The two seed fixtures share a code deliberately: the seed map is a single
mechanical function of the contract identity, so either edit fails the same
reproduction check. Saying otherwise would invent a distinction the code does not
make.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

Verified by explicit test, not assertion:

| rule | value | |
|---|---|---|
| `delta_cross` / `delta_abs` | `0.02` / `0.05` | unchanged |
| `z_cross` / `z_abs` | `1.959963985` / `1.959963985` | unchanged |
| `alpha_geom` / `alpha_1` / `alpha_2` | `0.005` / `0.004` / `0.001` | unchanged |
| `theta_cap_deg` / `rank_tol` | `5.0` / `1e-12` | unchanged |
| primary `sigma_psi` | `0.5` deg | unchanged |
| complete true-bridge target | `>= 0.90` | unchanged |
| G1 / G2 / C2 / C3 / C4 boundaries | 188/200, 4/400, 5/400, 2/400, 13/2000 | unchanged |
| replicate counts | 300, 400, 400, 2000, 400, 400, 400, 200 | unchanged |
| calibration scopes | 6 × `REPLICATE_CONDITIONAL`, 2 × `NOT_APPLICABLE` | unchanged |
| C7 false-bridge alternatives | `(1,1.06,1,1)`, `(1,0.93,1.05,1)`, `(1,1,1,1.10)`, `(1,1.025,1,1)` | unchanged |
| C8 scale factors | `1.07`, `0.90` | unchanged |
| rotated OU generator, calibration condition, case scopes, seed hierarchy, subcondition semantics | | unchanged |
| C3 release-vs-diagnostic, C7/C8 no-calibration semantics | | unchanged |
| master seed and every seed value | | unchanged |

No analysis-layer module was touched: the analysis procedure identity is
**bit-identical**.

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
| validation plan JSON | `a8591a986bf2f76075ed947fd3bab9f3d95db42f785ae308402dc34d8bef3989` | changed |
| validation plan Markdown | `46291d86971f1e4922cc5b9cabeea4660643d5e89bc889c75c6b56970a0a3c49` | changed |
| execution seal file | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` | changed |
| **PRE-DRIVER PACKAGE EXECUTION IDENTITY** | `13392827863aeb9814cdd264008ba501bfa8eafa846bdeb918bb824ef9a0481d` | changed |

**The execution identity above is a PRE-DRIVER PACKAGE IDENTITY, not a final
seal.** It will change again when the canonical driver is implemented, because
the driver's file hash replaces the `ABSENT` sentinel in the preimage by
construction.

| schema / state | value |
|---|---|
| plan version | `1.7.0` → **`1.8.0`** |
| record / manifest schema | `e1a_v4_validation_result/2` / `e1a_v4_validation_manifest/2` — unchanged |
| authority block schema | `e1a_v4_plan_authority/1` → **`e1a_v4_plan_authority/2`** |
| execution seal schema | `e1a_v4_execution_seal/1` → **`e1a_v4_execution_seal/2`** |
| execution seal state | `PRE_DRIVER` |
| expected execution identity | `null` (deliberately not yet frozen) |
| canonical driver | `e1a_v4.validation.campaign_driver` / `e1a_v4/validation/campaign_driver.py` / `run_campaign` / **ABSENT** |
| driver identity component | `ABSENT` (sentinel) |

---

## Static tests

| suite | checks | failures |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` — contract/design authority | 113 | 0 |
| `test_e1a_v4.py` — bounded implementation | 122 | 0 |
| `test_e1a_v4_preexec.py` — pre-execution *(+ exact refusal-reason checks)* | **100** | 0 |
| `test_e1a_v4_dispositions.py` — dispositions | 64 | 0 |
| `test_e1a_v4_size_semantics.py` — size semantics | 78 | 0 |
| `test_e1a_v4_repair.py` — B1/B2/B3 repair | 126 | 0 |
| `test_e1a_v4_calibration_scope.py` — calibration scope | 105 | 0 |
| `test_e1a_v4_case_scope.py` — case scope | 113 | 0 |
| `test_e1a_v4_preexec_corrections.py` — rotated OU correction | 37 | 0 |
| `test_e1a_v4_plan_coherence.py` — plan coherence + seal lifecycle | **112** | 0 |
| `test_e1a_v4_coherence_hardening.py` — **surface, strict JSON, driver binding (new)** | **122** | 0 |
| **TOTAL** | **1092** | **0** |

Movement from 952: **+122** new hardening checks, **+15** in the plan-coherence
suite (the enumerable specification and the widened surface), **+3** in the
pre-execution suite. **No earlier coverage was removed.** Three suites had
presentation-format assertions updated because the visible tables are now
generated — in each case the substance checked is unchanged or stronger.

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
EXECUTION REFUSED: [DRIVER_ABSENT] the official campaign driver
e1a_v4/validation/campaign_driver.py is ABSENT. The path is the canonical
identity-bound declaration in e1a_v4/validation/driver.py; no execution seal may
nominate another file in its place. A passing static preflight is not an
execution clearance.
  RANDOM DRAWS: 0   TRAJECTORIES: 0
```

`results/e1a_v4_validation` does not exist. No calibration artifact, trajectory or
result record was produced at any point in this task.

---

## Limitations and unresolved questions

- **Coherence is not immutability.** It enforces that the two representations
  agree. A scientific change propagated to both is coherent, and only a **frozen**
  seal would refuse it. The seal is deliberately `PRE_DRIVER`, so the plan is
  agreement-protected but not yet change-protected. This is the intended state
  before the driver exists, and it is stated here rather than left implicit.
- **End-to-end Branch-A provenance remains open**, unchanged by this task. The
  calibration lock enforces condition *consistency*, not that the condition came
  from that replicate's actual Branch-A measurement.
- **The `JSON_ONLY` classifications are judgements.** Each has a stated reason and
  totality is enforced, but a value classified `JSON_ONLY` today could later be
  rendered in the Markdown and would then need reclassifying. The totality check
  catches new *keys*, not a new *rendering* of an existing `JSON_ONLY` key.
- **The driver interface check is minimal by design** — module present, entry
  point declared, file hash bound. It cannot establish that the driver is
  *correct*; that is what the independent audit before freezing is for.
- The seal asserts an expected identity but cannot, by itself, establish that
  whoever froze it audited the driver. That remains a procedural control.

---

## Next stage

```
E1a v4 official campaign-driver implementation
READY FOR FINAL INDEPENDENT RE-AUDIT
NOT STARTED
```

---

```
COHERENCE HARDENING COMMITTED
```
