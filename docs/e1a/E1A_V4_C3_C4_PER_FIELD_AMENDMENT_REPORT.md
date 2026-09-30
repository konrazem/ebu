# E1a v4 — C3/C4 per-field authority amendment report

Waterfall stage **F1e — PROSPECTIVE AUTHORITY AMENDMENT**. Companion to the
scientific-record entry `docs/e1a/E1A_V4_C3_C4_PER_FIELD_AMENDMENT.md`.

| | |
|---|---|
| Work commit | `c086cd259d1c2192f3e74abffce212ba8577e76d` |
| Work tree | `46493c11bbfe74151c4d596f68e63d4ce29fbaff` |
| Parent | `673a1ccabcdbd79e50cead8ca8657dbd0e4601a5` |
| Plan version | `1.10.0` → **`1.11.0`** |

---

## Authority files changed

For each file: why it must change, what authority it carries, and why the
amendment is prospective rather than post-outcome.

| file | why it must change | authority it carries | prospective? |
|---|---|---|---|
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | it is where the C3/C4 case definitions, assurance rows, derived boundaries and dispositions live, and it is where the field structure was contradictory (C3) and unstated (C4) | the mechanical schema and ordering source for the validation campaign | yes — no campaign job, trajectory or outcome exists |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | its generated regions must be byte-exact re-renders of the JSON; a stale rendering is an integrity failure under `AGENTS.md` | the normative human rendering of the same authority | yes — same |

### Files deliberately NOT changed, with reasons

| file | why no amendment is required |
|---|---|
| `docs/e1a/e1a_v4_design_contract.json` | the contract's `synthetic_validation_requirements[5]` and `[8]` — the items C4 and C3 cite — concern the surrogate operating quantile and the G5 delta-method error; neither expresses a size demonstration across geometries, so neither is the home of the field-structure rule. The contract already supports per-field semantics through `endpoints.P1_geometry`, whose `alpha_1`/`alpha_2` are per-field block allocations and whose budget charges `4x_alpha_geom`. **BYTE-UNCHANGED.** |
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | design §15 items 5 and 8 likewise never expressed a C3/C4 size test; the size tests are a package-level construct added by the V4 correction. **BYTE-UNCHANGED.** |
| physical foundation, theory baseline | no physical or theoretical content is touched. **BYTE-UNCHANGED.** |
| `docs/e1a/e1a_v4_seed_map.json` | no seed, family, scope or derivation changes. **BYTE-UNCHANGED.** |
| `docs/e1a/e1a_v4_execution_seal.json` | the seal must not be frozen or populated at this stage. **BYTE-UNCHANGED.** |

### Minimal non-scientific plumbing

| file | change | why it was unavoidable |
|---|---|---|
| `e1a_v4/validation/coherence.py` | classify the new `c4_semantics` per-case key; render and parse semantics blocks generically instead of hard-coding `c3_semantics` | `require_specification_totality` refuses any plan key the specification does not classify, so the new authority could not otherwise be represented at all |
| `e1a_v4/validation/release_authority.py` | C3/C4 `unit` → `per_field` and `pooling` → `FORBIDDEN` in the case release specification; new bindings for `field_structure`, `field_reduction` and the semantics `pooling`; a requirement that any cited prospective disposition exists and is `CLOSED PROSPECTIVELY` | the case release specification sits **above** the machine plan in the authority chain and is compared against it; leaving it stale would have been an integrity failure. The new bindings were forced by the mutation results below. |

No scientific execution behaviour was changed: endpoint aggregation, campaign
execution, classifier inputs and terminal result aggregation are untouched.

---

## Exact old ambiguity

```text
C3   assurance unit           "campaign"
     assurance pooling        "NOT_APPLICABLE"
     derived_boundaries.C3    no per_field key
     R, method, sided         DERIVED from contract synthetic_validation_requirements[2]
                              with the reason "... at the same declared geometries ..."
                              -- a PER-GEOMETRY reading of a clause that says
                              "at every declared geometry"
     => the same contract clause was cited both for a per-geometry R and for
        "C3 reports one campaign-level G5 rejection count"

C4   assurance unit           "campaign"
     assurance pooling        "NOT_APPLICABLE"
     derived_boundaries.C4    no per_field key
     R = 2000                 PACKAGE-level; the specification records that frozen
                              authority states no replicate count
     => field structure unstated entirely
```

Neither case's criterion, endpoint, assurance row or release rule defined the
reduction, while `G5` and `P1` are recorded per `field_id` with no replicate-level
counterpart in the output schema.

---

## Exact new rule

```text
C3, C4   elementary size event          PER FIELD
         within-replicate reduction     NONE
         pooling                        FORBIDDEN
         fields                         theta0_circular, theta1_power,
                                        theta2_ellipse, theta3_temperature
         per-field test                 C3: R=400,  alpha_2=0.001, clean 0-2
                                        C4: R=2000, alpha_1=0.004, clean 0-13
         case level                     four required field conditions in the
                                        EXISTING conjunctive classifier; clean iff
                                        all four clean; no compensation; failing
                                        field identity preserved
         forbidden                      realising that conjunction as a
                                        replicate-wide "any field rejects" event
```

Recorded in the plan as: both `formal_pass_fail_criterion` strings; `c3_semantics`
extended and a new `c4_semantics` block; `assurance[C3]`/`assurance[C4]` `unit`,
`pooling`, `quantity` and `acceptance_rule`;
`size_validation_semantics.derived_boundaries.C3`/`.C4` gaining `per_field`,
`pooling` and `replicate_reduction`; final classification requirements 3 and 4;
and `authority_gaps` **G4**, `CLOSED PROSPECTIVELY`.

---

## Plan version change

`1.10.0` → `1.11.0`, following the repository's existing convention: every prior
prospective plan amendment took a minor bump (1.3.0 … 1.10.0), and the version is
carried in both renderings and checked by `normative_markdown_view`.

---

## Contract / plan identities

Computed twice from independent clean `git archive` extractions of the work
commit. Both agree.

| item | before | after |
|---|---|---|
| **unsealed execution identity** | `2d1ae73233f7dc972ddcab000010d4fac703d29b2eb55408c48c8812982b473c` | **`948709654add8fa950c4eeb8fb2c729fc661b7625a1c6e4ae4cd5f24bc9c2eec`** |
| JSON plan | `dcb3507585791c851e616c81a113fe89d61d2e830a4694f49733d1d04c5b8f5a` | `02d2117ac9c7f18ccb005b1b774f54e78ee23847ecfce4382084e74a36cfbc95` |
| Markdown plan | `3f4715b465da295e21ad99a86390585c9eb7deac44a7810114a88f40aa4bf940` | `af5d7e9a5ddcc7e1f3714916f10fdcc9cb6eafb539a67e35e361ef2d69b839c2` |
| design contract | `91d6ae76…431b` | **unchanged** `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| prospective design | `e59dcff6…a495` | **unchanged** `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` |
| seed map | `95870d7d…e91ce` | **unchanged** `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` |
| **analysis identity** | `dd2ed732…2e1f` | **unchanged** `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` |

The execution identity moves because the plan and its Markdown rendering are in
its preimage — which is the point of binding a prospective amendment to it. The
analysis identity does **not** move, verified rather than assumed: no
`SCIENTIFIC_MODULES` entry was modified. Campaign structure is unchanged at
**53,200 planned jobs** and **46,000 calibration artifacts**.

---

## Coherence / conformance results

| check | result |
|---|---|
| `require_specification_totality` (no unclassified plan key) | PASS |
| Markdown ↔ JSON: all 7 generated regions byte-exact re-renders | PASS |
| embedded authority block equals the full JSON normative view | PASS |
| human-visible renderings equal the JSON normative view | PASS |
| `require_derived_boundaries` (boundaries RECOMPUTED, not copied) | PASS |
| `require_generating_model_coherence` | PASS |
| contract ↔ plan conformance | PASS |
| release-rule authority (`require_release_authority_conformance`) | PASS |
| normative-field completeness / section registry totality | PASS |
| strict JSON parsing (duplicate keys refuse at any depth) | PASS |

---

## Mutation tests

New group `C3/C4 per-field authority (G4)` in `test_e1a_v4_release_authority.py`.
Every mutation is **coherent** — the Markdown is regenerated from the mutated JSON
— so none is caught merely by a rendering mismatch.

| coherent-but-wrong mutation | refusal |
|---|---|
| C3 `unit` `per_field` → `campaign` | `CONTRACT_RELEASE_ENDPOINT_MISMATCH` |
| C3 `pooling` `FORBIDDEN` → `ALLOWED` | `CONTRACT_RELEASE_TARGET_MISMATCH` |
| C3 `field_structure` `PER_FIELD` → `ANY_FIELD` | `CONTRACT_RELEASE_ENDPOINT_MISMATCH` |
| C3 `field_reduction` `NONE` → `ANY_FIELD` | `CONTRACT_RELEASE_ENDPOINT_MISMATCH` |
| C3 four fields → reference field only | `CONTRACT_GENERATING_PARAMETER_MISMATCH` |
| C4 `unit` `per_field` → `campaign` | `CONTRACT_RELEASE_ENDPOINT_MISMATCH` |
| C4 `pooling` `FORBIDDEN` → `ALLOWED` | `CONTRACT_RELEASE_TARGET_MISMATCH` |
| C4 `field_structure` `PER_FIELD` → `ANY_FIELD` | `CONTRACT_RELEASE_ENDPOINT_MISMATCH` |
| C4 `field_reduction` `NONE` → `EVERY_FIELD` | `CONTRACT_RELEASE_ENDPOINT_MISMATCH` |
| C4 field list missing one field | `CONTRACT_GENERATING_PARAMETER_MISMATCH` |
| C4 four fields → reference field only | `CONTRACT_GENERATING_PARAMETER_MISMATCH` |
| G4 disposition deleted | `CONTRACT_RELEASE_BINDING_UNCLASSIFIED` |
| G4 status flipped to `OPEN` | `CONTRACT_RELEASE_BINDING_UNCLASSIFIED` |

**Six of these thirteen initially PASSED**, and that is why the release-authority
bindings above exist. Writing new authority fields (`field_structure`,
`field_reduction`, the semantics `pooling`) and a new disposition into the plan
did not, by itself, make their *values* load-bearing: they were carried and
coherence-checked but bound to nothing, so a coherent edit could change the
measured size or delete the justification and still pass preflight. The bindings
close that; all thirteen now refuse.

---

## Implementation status

```text
AUTHORITY AMENDED
IMPLEMENTATION UPDATE REQUIRED
EXECUTION REMAINS BLOCKED
```

The driver and classifier were **not** updated, by instruction. `campaign_driver`
still raises `ENDPOINT_EVENT_REDUCTION_UNDECLARED` for both C3 and C4, verified
after the amendment. That refusal was **not weakened**, and it is now
*authority-correct* rather than a fail-closed guess: the scalar replicate-level
reduction it declines to invent is precisely what the amended authority forbids.
`CampaignCounts` still carries `c3_rejections: int` / `c4_rejections: int` beside
the already per-field `c2_rejections_by_field`; converting those and emitting four
field conditions per case is stage F1f.

### Tests

All pure. Each suite run with `ou_observations` replaced by a counter that aborts
on first call, so the trajectory count is measured.

| suite | checks | passed | failed | trajectories |
|---|---|---|---|---|
| `test_e1a_v4_terminal_calibration.py` | 538 | 538 | 0 | 0 |
| `test_e1a_v4_release_authority.py` | 273 | 273 | 0 | 0 |
| `test_e1a_v4_coherence_hardening.py` | 138 | 138 | 0 | 0 |
| `test_e1a_v4_repair.py` | 126 | 126 | 0 | 0 |
| `test_e1a_v4_driver_endpoints.py` | 122 | 122 | 0 | 0 |
| `test_e1a_v4.py` | 122 | 122 | 0 | 0 |
| `test_e1a_v4_plan_coherence.py` | 113 | 113 | 0 | 0 |
| `test_e1a_v4_calibration_scope.py` | 105 | 105 | 0 | 0 |
| `test_e1a_v4_preexec.py` | 104 | 104 | 0 | 0 |
| **total** | **1,641** | **1,641** | **0** | **0** |

The release-authority suite grows from 225 checks in 14 groups to 273 in 15.
Two pre-existing assertions were updated because the amendment legitimately moves
what they pin: the disposition roster (`G1, G2, G3` → `G1, G2, G3, G4`) and the
two plan hashes in the frozen-authority guard — whose other five entries
(foundation, baseline, contract, design, seed map) deliberately still pass
unchanged.

**Known deferred test.** `test_e1a_v4_campaign_driver.py` was not run — it is the
trajectory-bearing suite. Its runtime status is **not claimed**; static only.

---

## Execution status

```text
C3/C4 SCIENTIFIC AUTHORITY AMENDED PROSPECTIVELY

OFFICIAL RESULTS OBSERVED = NO

DRIVER/CLASSIFIER UPDATE = REQUIRED

FINAL EXECUTION SEAL = NOT FROZEN

EXECUTION AUTHORISED = FALSE

CAMPAIGN = NOT RUN
```

Verified after the amendment: no `results/e1a_v4_validation` directory; seal
`state = PRE_DRIVER`, `expected_execution_identity = None`,
`execution_authorised = false`, `random_draws = 0`, `trajectories = 0`. Nothing
was pushed.

---

C3/C4 PER-FIELD AUTHORITY AMENDMENT COMMITTED
