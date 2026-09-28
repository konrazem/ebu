# E1a v4 — COMPLETE GENERATING-MODEL COHERENCE COVERAGE

**AUTHORITY-INTEGRITY REPAIR. NO CAMPAIGN WAS RUN. NO RANDOM NUMBER WAS DRAWN.**

| | |
|---|---|
| work commit | `df08b2b8a0e299a1cc3080c74943a28c04265675` |
| work tree | `438c9ad1c194af273053dd91578e619bdc1bfdd9` |
| starting HEAD | `addd7046aec04f76cab23dbb8096500a15968a47` |
| branch | `gaussian/stage-a-environment` |
| push status | **NOT PUSHED** |

---

## Result

**The section-4 blocker was reproduced and repaired**, and the seal-ordering
discrepancy is repaired.

`generating_model` was classified `JSON_ONLY` with a single subtree-level
shortcut, although section 4 visibly renders its scientific settings. Every
descendant was therefore outside the checked surface.

### Reproduction, before any edit

The auditor named three examples. Probing the same class found six more, and one
further defect the audit had not named.

| one-sided change | before |
|---|---|
| **Markdown** `n_samples` `2000000` → `2000001` | **ACCEPTED** |
| **Markdown** `dt` `0.00012` → `0.00013` | **ACCEPTED** |
| **Markdown** `theta1_power` stiffness `[210,210]` → `[200,200]` | **ACCEPTED** |
| **Markdown** `theta3_temperature` `T` `318 K` → `350 K` | **ACCEPTED** |
| **Markdown** `theta2_ellipse` rotation `30°` → `45°` | **ACCEPTED** |
| **Markdown** `T_total` `240.0` → `480.0 s` | **ACCEPTED** |
| **Markdown** `theta0_circular` reference `yes` → `no` | **ACCEPTED** |
| **Markdown** `theta1_power` `beta_true` `1.0` → `1.06` | **ACCEPTED** |
| **Markdown** `burn_in_steps` `0` → `5000` | **ACCEPTED** |
| **JSON** `n_samples`, `dt_s`, `T_total_s`, `k_uN_per_m`, `T_K`, `rot_deg` (6 probes) | **ACCEPTED** |
| **the plan contradicting the FROZEN DESIGN CONTRACT** on `theta1_power` stiffness | **ACCEPTED** |

9 / 9 Markdown-only and 6 / 6 JSON-only probes accepted. The last row was **not in
the audit**: the plan restates contract authority and nothing compared the two, so
the plan could have silently outranked the frozen contract.

### After the repair

**0 / 9 and 0 / 6 accepted.** Every probe refuses, with a specific code, and the
contract-contradiction probe refuses too.

---

## Generating-model inventory

Complete, traced from the current JSON schema rather than assumed. Every primitive
beneath the generating-model authority, classified individually — **no
subtree-level shortcut may hide a duplicated descendant**.

| JSON path | type | human-rendered? | Markdown location | classification |
|---|---|---|---|---|
| `branch_b.process` | str | yes | §4 Branch-B table | **BOTH** |
| `branch_b.transition` | str | yes | §4 Branch-B table | **BOTH** |
| `branch_b.phi` | str | yes | §4 Branch-B table | **BOTH** |
| `branch_b.initialisation` | str | yes | §4 Branch-B table | **BOTH** |
| `branch_b.superseded` | str | yes | §4 Branch-B table | **BOTH** |
| `branch_b.dt_s` | float | yes | §4 Branch-B table | **BOTH** (primitive) |
| `branch_b.T_total_s` | float | yes | §4 Branch-B table | **BOTH** (primitive) |
| `branch_b.n_samples` | int | yes | §4 Branch-B table | **DERIVED_RENDERING** |
| `branch_a.model` | str | yes | §4 Branch-A table | **BOTH** |
| `branch_a.common_mode` | str | yes | §4 Branch-A table | **BOTH** |
| `branch_a.per_mode_stiffness` | str | yes | §4 Branch-A table | **BOTH** |
| `branch_a.orientation` | str | yes | §4 Branch-A table | **BOTH** |
| `branch_a.thermometry` | str | yes | §4 Branch-A table | **BOTH** |
| `branch_a.independence` | str | yes | §4 Branch-A table | **BOTH** |
| `truth_visibility` | str | yes | §4 truth-visibility line | **BOTH** |
| `per_field.id` | str | yes | §4 per-field table | **BOTH** |
| `per_field.k_uN_per_m` | list | yes | §4 per-field table | **BOTH** |
| `per_field.T_K` | int | yes | §4 per-field table | **BOTH** |
| `per_field.rot_deg` | int | yes | §4 per-field table | **BOTH** |
| `per_field.reference` | bool | yes | §4 per-field table | **BOTH** |
| `per_field.beta_true` | float | yes | §4 per-field table | **BOTH** |
| `per_field.tau_rule` | str | yes | §4 per-field table | **BOTH** |

**22 primitives: 21 `BOTH`, 1 `DERIVED_RENDERING`, 0 `JSON_ONLY`.** Expanded over
the four declared fields, the canonical view is **40 paths**.

**Field geometry is covered in full.** Each of `theta0_circular`, `theta1_power`,
`theta2_ellipse` and `theta3_temperature` has its stiffness, temperature,
orientation, reference flag, `beta_true` and relaxation rule in the surface. None
can change in one representation alone.

### Units and numeric representation

`0.00012 s`, `1.2e-4 s` and `0.12 ms` denote the same quantity, so only one
canonical representation is ever written: the value is rendered as **exact JSON in
its own cell**, with the unit in a **separate column** (`| dt | \`0.00012\` | s |`).
Parsing maps back by `json.loads` on that cell, so the round trip is exact.
Quantities keep their declared unit in the key name — `dt_s`, `T_total_s`,
`k_uN_per_m`, `T_K`, `rot_deg` — which is also the frozen contract's own
convention, so no unit conversion is invented.

**No tolerance is applied to the generating model.** `0.00012` → `0.00013` refuses,
and the all-primitives mutation audit below proves it for every primitive, not
just this one.

---

## Primitive versus derived values

Determined **from the implementation**, not assumed:

```python
# e1a_v4/world.py
@property
def n_samples(self) -> int:
    return int(round(self.T_total / self.dt))
```

So the authority direction is:

```
dt_s, T_total_s   (PRIMITIVE)
        ↓
n_samples = int(round(T_total / dt))   (DERIVED)
        ↓
Markdown display
```

`240.0 / 0.00012 = 2000000` exactly. Preflight **recomputes** it rather than
trusting the stored number, so `n_samples` can never become a third authority that
quietly disagrees with its own primitives. A plan declaring `1999999` refuses with
`PLAN_DERIVED_VALUE_MISMATCH`.

The section-12a size boundaries are derived the same way — the section itself says
they are "recomputed by `size_boundary(R, nominal)`, never copied" — so they are
recomputed by `size_boundary` and `cp_lower` and compared to the rendered table.

### Upstream authority: the plan may not outrank the contract

`generating_model.per_field` restates the **frozen design contract's** `fields`,
and `branch_b.dt_s` / `T_total_s` restate its
`hypothetical_uncertainty_scenario`. Nothing compared them. Preflight now refuses
a plan that contradicts the contract on any field's stiffness, temperature,
orientation or reference flag, or on `dt` or `T_total` — the contract outranks the
plan, and a restatement may not become a rival authority.

---

## Normative section registry

Whole-document coverage. Every `## ` section is classified with a reason, and
`require_section_registry_totality` refuses an unregistered section, a renamed
section, a duplicated heading, or a registry entry the document no longer carries.

| section | classification |
|---|---|
| 1. Frozen identities | **PARSED** |
| 1a. Machine-readable authority block | **GENERATED** |
| 2. Adopted rules, unchanged | **GENERATED** |
| 3. The eight cases | **GENERATED** |
| **4. Generating model** | **GENERATED** *(was unchecked)* |
| 5. Calibration | NON_NORMATIVE |
| 6. Statistical assurance | **GENERATED** |
| 7. Seed separation | NON_NORMATIVE |
| **8. Controls** | **GENERATED** *(was unchecked)* |
| 9. Output schema | **PARSED** |
| 10. Failure classifications | **PARSED** |
| 11. No post-outcome tuning | NON_NORMATIVE |
| 12. Author dispositions | **GENERATED** |
| **12a. Size-validation semantics** | **DERIVED** *(was unchecked)* |
| 12b. Final campaign classification | NON_NORMATIVE |
| 13. Execution | **PARSED** |
| 13a. Execution-seal architecture | **PARSED** |
| 14. Pre-execution repair — supersession | NON_NORMATIVE |
| 15. Parallelism policy | NON_NORMATIVE |
| 16. What the cost figures actually contain | NON_NORMATIVE |
| 17. Correction — superseded artifact count | NON_NORMATIVE |
| 18. Plan-coherence repair — supersession | NON_NORMATIVE |
| 19. Generating-model coherence — supersession | NON_NORMATIVE |

**23 sections: 7 GENERATED, 5 PARSED, 1 DERIVED, 10 NON_NORMATIVE.** Each
`NON_NORMATIVE` entry states *why* it is single-source: §5 and §7 are derivation
narrative whose operative values live in the cases region and the authority block;
§12b now points at the generated release rules instead of restating them; §11 and
§15 change nothing executable; §14, §16, §17, §18 and §19 are historical or
measurements about the package rather than parameters of the experiment.

### Machine-derived counts

Every figure below is read out of the implementation. **`markdown_only_keys` and
`unclassified_normative_candidates` are now MEASURED, not asserted** — they were
hardcoded zeros, which is precisely the unearned completeness claim that let the
generating model sit outside the surface while the package reported full
coherence.

| quantity | value |
|---|---:|
| duplicated normative keys checked | **489** |
| of which human-rendered | 480 |
| of which rendered only in the authority block | 9 |
| **JSON-only normative keys** (top level) | **20** |
| **Markdown-only normative keys** *(measured)* | **0** |
| **derived-rendering keys** | **2** |
| generating-model primitives | 22 |
| of which `BOTH` | 21 |
| **registered normative sections** | **23** |
| unregistered sections *(measured)* | 0 |
| **unclassified normative candidates** *(measured)* | **0** |

The surface grew from **431 → 489** keys: the generating model and the controls
table.

---

## Automatic mutation audit

Not three hand-picked tests. The targets are **enumerated from the specification**,
so a primitive added later is tested automatically:

| | |
|---|---:|
| primitives classified `BOTH` under the generating-model surface | **38** |
| mutated on the **JSON** side, refusal required | 38 / 38 |
| mutated on the **Markdown** side, refusal required | 38 / 38 |
| **total mutations executed** | **76** |

Mutations are deterministic and type-appropriate — `int → +1`, `float → ×2`,
`bool → flip`, `str → suffixed`, `list → first element mutated` — and every one
stays **well-formed**. What is proven is *semantic mismatch detection*, never
malformed-input rejection.

---

## Known regression probes

Permanent tests, both sides, with the exact code asserted:

| probe | result | code |
|---|---|---|
| visible `n_samples` changed | **REFUSE** | `PLAN_GENERATING_MODEL_MISMATCH` |
| visible `dt` changed | **REFUSE** | `PLAN_GENERATING_MODEL_MISMATCH` |
| visible `theta1_power` stiffness changed | **REFUSE** | `PLAN_GENERATING_MODEL_MISMATCH` |
| JSON `n_samples` changed | **REFUSE** | `PLAN_DERIVED_VALUE_MISMATCH` |
| JSON `dt_s` changed | **REFUSE** | `PLAN_DERIVED_VALUE_MISMATCH` |
| JSON `theta1_power` stiffness changed | **REFUSE** | `PLAN_GENERATING_MODEL_MISMATCH` |

The JSON `dt` and `n_samples` probes refuse on the **derived** relation first:
changing either primitive without the other breaks `n_samples = T_total / dt`
before the rendering is even consulted. That is the stronger failure, and it is
why the derived relation is checked rather than the stored number trusted.

---

## Seal ordering

The gate validated the seal **before** checking driver presence, so a missing seal
reported `EXECUTION_SEAL_MALFORMED` while the real missing precondition was the
driver.

### Implemented lifecycle

```
1. canonical official driver exists and satisfies its declared interface
2. external execution seal exists, is well-formed and is FROZEN
3. recomputed execution identity equals the frozen seal
4. execution_authorised is true
5. cross the RNG boundary
```

The driver is now checked first — and, on the execute path, **before preflight**,
because preflight validates the seal as part of package coherence and would
otherwise preempt it. That is a deliberate trade-off, stated in the code: the
`--preflight-only` path is unchanged, and the CLI still runs and prints the
complete preflight before attempting execution, so integrity defects remain
visible.

### Missing versus malformed

| condition | code |
|---|---|
| seal file **absent** | `EXECUTION_SEAL_NOT_FROZEN` |
| seal exists but **unparseable** | `EXECUTION_SEAL_MALFORMED` |
| seal exists, valid, `PRE_DRIVER` | `EXECUTION_SEAL_NOT_FROZEN` |
| seal `FROZEN` but identity differs | `EXECUTION_IDENTITY_MISMATCH` |
| driver absent, **whatever the seal's state** | `DRIVER_ABSENT` |

A seal nobody has written yet has not been frozen; reporting "malformed" for it
names the wrong missing precondition.

Three new codes: `PLAN_GENERATING_MODEL_MISMATCH`, `PLAN_DERIVED_VALUE_MISMATCH`,
`PLAN_SECTION_UNREGISTERED`.

---

## Scientific rules

```
NO E1a SCIENTIFIC DECISION RULE CHANGED
```

| rule | value | |
|---|---|---|
| `delta_cross` / `delta_abs` | `0.02` / `0.05` | unchanged |
| `z_cross` / `z_abs` | `1.959963985` / `1.959963985` | unchanged |
| `alpha_geom` / `alpha_1` / `alpha_2` | `0.005` / `0.004` / `0.001` | unchanged |
| `theta_cap_deg` / `rank_tol` | `5.0` / `1e-12` | unchanged |
| primary `sigma_psi` | `0.5` deg | unchanged |
| complete true-bridge target | `>= 0.90` | unchanged |
| G1 / G2 / C2 / C3 / C4 boundaries | 188/200, 4/400, 5, 2, 13 | unchanged |
| **the generating model itself** | `dt = 0.00012 s`, `T_total = 240.0 s`, `n_samples = 2000000` | **unchanged** |
| **every field's physical parameters** | 100/100@298, 210/210@298, 150/60@298 rot 30°, 100/100@318 | **unchanged** |
| corrected rotated-OU generator | | unchanged |
| master seed and every seed value | | unchanged |

No analysis-layer module was touched: the analysis procedure identity is
**bit-identical**. The repair changed *what is checked*, never *what is declared*.

---

## Identity changes

| item | value | |
|---|---|---|
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` | **UNCHANGED** |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` | **UNCHANGED** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` | **UNCHANGED** |
| working theory baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` | **UNCHANGED** |
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | **UNCHANGED** |
| seed map | `95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce` | **UNCHANGED** |
| validation plan JSON | `45911bf9cb19db298e8f2d09da86d1e23de35b609cd8271e6da61952cb99e169` | changed |
| validation plan Markdown | `fab1b2411cba064a5ca046c8a04ed192ee3a755db40f5b822ed4daa81f4fb680` | changed |
| execution seal file | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` | unchanged |
| **PRE-DRIVER PACKAGE EXECUTION IDENTITY** | `ed4966705a1ae9be5f90d06fe8b80b774b9189bf137e23d3fa98ea06b766746b` | changed |

**Not a final seal.** It will change again when the canonical driver replaces the
`ABSENT` sentinel in the preimage.

| schema / state | value |
|---|---|
| plan version | `1.8.0` → **`1.9.0`** |
| authority block schema | `e1a_v4_plan_authority/2` (unchanged) |
| execution seal schema | `e1a_v4_execution_seal/2` (unchanged) |
| execution seal state | `PRE_DRIVER` |
| expected execution identity | `null` |
| canonical driver | `e1a_v4/validation/campaign_driver.py` — **ABSENT** |
| driver identity component | `ABSENT` (sentinel) |

---

## Static tests

| suite | checks | failures |
|---|---:|---:|
| `docs/e1a/validate_e1a_v4_contract.py` — contract/design authority | 113 | 0 |
| `test_e1a_v4.py` — bounded implementation | 122 | 0 |
| `test_e1a_v4_preexec.py` — pre-execution, exact refusal reasons | 100 | 0 |
| `test_e1a_v4_dispositions.py` — dispositions | 64 | 0 |
| `test_e1a_v4_size_semantics.py` — size semantics | 78 | 0 |
| `test_e1a_v4_repair.py` — B1/B2/B3 calibration repair | 126 | 0 |
| `test_e1a_v4_calibration_scope.py` — calibration scope | 105 | 0 |
| `test_e1a_v4_case_scope.py` — case scope | 113 | 0 |
| `test_e1a_v4_preexec_corrections.py` — rotated OU correction | 37 | 0 |
| `test_e1a_v4_plan_coherence.py` — plan coherence, seal lifecycle | 112 | 0 |
| `test_e1a_v4_coherence_hardening.py` — surface, strict JSON, driver binding | **135** | 0 |
| `test_e1a_v4_generating_model.py` — **generating model, mutation audit, section coverage, seal order (new)** | **112** | 0 |
| **TOTAL** | **1217** | **0** |

Movement from 1092: **+112** new, **+3** in the hardening suite (the
missing-versus-malformed seal distinction and the driver-present substitution
probe). **No earlier coverage was removed.** Three assertions were updated where
the intended behaviour itself changed, each noted in place.

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

The official execution command was run and **refused**, exit code 2, on the
**driver** — before any seal, identity or authorisation path:

```
$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
EXECUTION REFUSED: [DRIVER_ABSENT] the official campaign driver
e1a_v4/validation/campaign_driver.py is ABSENT. ...
  RANDOM DRAWS: 0   TRAJECTORIES: 0
```

`results/e1a_v4_validation` does not exist. No campaign driver was created — a
placeholder would satisfy the existence test and defeat the gate, so lifecycle
states beyond `ABSENT` are exercised only with throwaway sandbox fixtures. No
calibration artifact, trajectory or result record was produced at any point.

---

## Limitations and unresolved questions

- **This is the third escape of the same kind.** The identity table, then the
  case subconditions and release rules, now the generating model. The registry
  and the measured `unclassified_normative_candidates` are the structural answer,
  but they guard *sections* and *keys* — a new rendering of an existing
  `JSON_ONLY` key inside an already-registered `NON_NORMATIVE` section would still
  need human judgement to catch.
- **`NON_NORMATIVE` classifications are judgements.** Ten sections carry that
  label with a stated reason. Each says why its operative values live elsewhere;
  none is asserted without one. They remain the most likely place for a fourth
  escape.
- **Coherence is still not immutability.** A change propagated to both
  representations *and* consistent with the contract is coherent; only a frozen
  seal would refuse it, and the seal is deliberately `PRE_DRIVER`.
- **Checking the plan against the contract is one-directional.** It catches a plan
  that contradicts the contract; it does not verify the contract itself, which is
  protected only by its frozen hash.
- **End-to-end Branch-A provenance remains open**, unchanged by this task.

---

## Next stage

```
E1a v4 official campaign-driver implementation
READY FOR FINAL INDEPENDENT RE-AUDIT
NOT STARTED
```

---

```
GENERATING-MODEL COHERENCE COMMITTED
```
