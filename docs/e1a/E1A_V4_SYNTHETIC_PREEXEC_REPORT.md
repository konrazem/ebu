# E1a v4 — SYNTHETIC VALIDATION PRE-EXECUTION REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**The synthetic-validation package is frozen and execution-ready, subject to three author
dispositions recorded below.** Nothing was executed.

The package freezes the eight cases, the generating model, the calibration procedure, the
seed families and their values, replicate counts, validation criteria, failure
classifications, manifests, output schema, procedure identities, the execution command and
the interpretation rules. **No adopted decision rule changed.**

---

## Authority

| item | identity |
|---|---|
| design contract | `89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c` |
| prospective design | `f20bc885bf400ce3429120e4a0e42915ba2fb15249d88914fd7e55eb1b373f68` |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| implementation work commit | `e4b73d7fbd84d329f4326af443fd1918bc44a874` |
| validation plan JSON | `142e9a8f424d970e063eaca8a0a209da365ad1408b80d9b5b7c67b763ca6c894` |
| validation plan Markdown | `ee0c8779176473899f32da9e3ece5f4291d537a07230079f1fa237de2eee6eaf` |
| seed map | `bb21dd6cc9959c1b61812d54925b56d64f7ecf8a8c36c68c03605af69802979d` |
| **analysis** procedure identity | `1983ba3af64cd62480feb642ce83f38cf7d2e5f06bf9398b41b81fe1f864648c` |
| **execution** procedure identity | `2f4902a17c3ce0d187e308bb061cf239ee328639d313f428e22a7af175384d71` |

The contract identity was verified against the value quoted in the implementation report
and matches exactly.

**Two identities, deliberately separate.** The **analysis procedure identity** binds the 12
analysis modules, the contract and the adopted rules; calibration artifacts bind to *this*,
as the bounded implementation requires, and **adding the validation package did not change
it** — a test asserts that. The **execution procedure identity** additionally binds the
seven validation modules, the plan and the seed map. It is derived at preflight rather than
embedded in the plan, because embedding it in the file whose hash it covers would be
self-referential.

One ambiguity is now closed: the configuration mapping is part of the analysis identity, so
a different configuration yields a different digest *by design*. The frozen value is the
**empty-configuration** variant; the implementation report quoted the
`{"stage": "bounded_implementation"}` variant `8dd48f42…`. Both are recorded in the plan.

**Frozen execution versus general implementation.** A general analysis reads whatever valid
contract it is given — correct architecture, no magic numbers in code. An **official
validation run may not**: `bind_execution` requires the exact adopted contract identity and
refuses anything else **before an RNG can be created**. Both behaviours are tested.

---

## Final case table

Eight cases, one per scientifically required purpose traceable to committed or adopted
authority.

| case | role | v4 classification | seed family | R |
|---|---|---|---|---:|
| `C1_true_bridge_complete` | primary | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION | `validation` | 300 |
| `C2_geometry_false_rejection` | primary | RETAINED BUT UPDATED FOR V4 | `validation` | 400 |
| `C3_g5_block` | primary | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION | `validation` | 400 |
| `C4_surrogate_validity` | primary | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION | `calibration + validation` | 2000 |
| `C5_plug_in_branch_a` | primary | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION | `validation + branch_a_measurement` | 400 |
| `C6_mode_resolution_boundary` | primary | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION | `validation` | 400 |
| `C7_false_bridge` | negative control | RETAINED BUT UPDATED FOR V4 | `validation` | 400 |
| `C8_blinded_scale_control` | positive control | RETAINED UNCHANGED | `blinded_scale_control` | 200 |

**Why eight.** Eight cases, one per scientifically required purpose traceable to committed or adopted authority. P2 (cross-field) and P3 (absolute) are NOT separate generating cases: they are endpoints evaluated on C1's data so the shared reference-field dependence and the common-mode calibration error are preserved. Simulating the three P2 ratios independently, or reverting P3 to reference-only, would destroy exactly the structure being validated. The count is eight because eight purposes are required, not to preserve a historical number.

Full descriptors — truth model, fields affected, beta truth, geometry truth, Branch-A
uncertainty, Branch-B process, expected qualitative outcome and the formal pass/fail
criterion — are in the plan for every case.

---

## Statistical assurance

| quantity | target | bound | R | acceptance rule |
|---|---|---|---:|---|
| complete true-bridge pipeline success | `>= 0.90` | Clopper-Pearson one-sided LOWER | 300 | >= 279 / 300 complete passes |
| P1 false-rejection rate, per field | `alpha_geom = 0.005` | Clopper-Pearson one-sided UPPER | 400 | upper bound <= 0.03, i.e. <= 6 rejections of 400 |
| block-2 (G5) rejection rate | `alpha_2 = 0.001` | Clopper-Pearson one-sided UPPER | 400 | upper bound <= 0.03 |
| Block-1 achieved size under the surrogate | `alpha_1 = 0.004` | Clopper-Pearson two-sided | 2000 | REPORTED and classified; the discrepancy is the result |
| false-bridge acceptance, per alternative | `AUTHORITY GAP G2` | Clopper-Pearson one-sided UPPER | 400 | NOT DECLARED IN ADOPTED AUTHORITY - must be declared before execution |
| blinded scale recovery beta_hat * c | `AUTHORITY GAP G1` | reported | 200 | NOT DECLARED IN ADOPTED AUTHORITY - must be declared before execution |

**Complete-pass denominator, frozen:** every declared validation replicate. Structured
refusals **count as failures**. Conditional diagnostics are permitted only when explicitly
labelled SECONDARY and reported beside the unconditional figure. Refusal counts **and
reasons** are reported.

Two errors from the project's history are explicitly avoided: an **upper** bound is used
for every size claim (a lower bound cannot demonstrate control), and an observed proportion
above 0.90 is **not** sufficient by itself for the complete-pipeline target — 279/300 is
required.

---

## Calibration

Generator `e1a_v4.validation.calibrate.generate_block1_artifact`, identity
`EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1`, seed family `calibration`,
**R = 50000**, gates G1, G2, G3, G4.
Realised size 0.4000% +/- 0.0282% at alpha_1 = 0.004 (Beta(k, R+1-k), k = ceil(alpha_1 R) = 200).

**G5 is deliberately absent from calibration.** G5 is NOT generated here. It is not a function of the covariance, so producing it as an independent companion would destroy its real dependence on the trajectory statistics. G5 is validated in the validation layer from full observations.

Frozen workflow: CALIBRATION DATA -> fix calibration artifacts and thresholds -> lock artifact identities -> VALIDATION DATA -> evaluate predeclared operating characteristics -> CONFIRMATORY DATA only if the adopted protocol requires it.

Invariants: no validation result may change a calibration threshold; no confirmatory result may change calibration or validation design.

The artifact binds to the analysis procedure identity, the Branch-A geometry signature, the
contract hash and the plan hash.

---

## Validation generator

Branch B is the declared correlated process, not a shortcut that samples the statistics
being tested: `x_{k+1} = phi_r x_k + sqrt(1 - phi_r^2) L z, per mode, EXACT`, with
`phi_r = exp(-dt / tau_r)` and stationary initialisation
`x_0 ~ N(x*, Sigma_theta); stationary at step 0; burn_in_steps = 0`.
the v3 convention of starting at x = 0 is FORBIDDEN: it is not stationary.

Branch A is a separate layer with its own seed family: common mode drawn **once per
experiment** and shared across every field (so it cancels in the P2 ratio and not in P3),
per-mode stiffness independent per mode, trap-axis orientation, and thermometry.

**Truth visibility.** H_true and tau_true are known to the SCORING layer only. The analysis pipeline receives only the Branch-A measured field, exactly as in the real experiment.

---

## Seed separation

Seeds are **derived, never chosen**, and the runner refuses if the committed map does not
rederive from its own declared algorithm.

```
master     DOMAIN|master|contract_sha256|campaign
family     DOMAIN|family|master_hex16|family_name
replicate  DOMAIN|replicate|family_hex16|case=<id>|rep=<index>
hash       first 8 bytes of sha256(text), big-endian unsigned
```

| family | seed |
|---|---:|
| master | `12737552942663785904` |
| `blinded_scale_control` | `9479310386300230328` |
| `branch_a_measurement` | `11004995623645776693` |
| `calibration` | `15379082101033647447` |
| `confirmatory` | `9585841150145721670` |
| `validation` | `11476631527835384658` |

`branch_a_measurement` is its **own** family — Branch-A measurement error is exogenous
randomness the analysis never sees, so it never reuses the Branch-B trajectory stream. The
analysis layer's four families are a strict subset, so the analysis identity is untouched.
No single mutable global RNG is used anywhere.

---

## Execution command

```
OFFICIAL EXECUTION COMMAND FROZEN
python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation

OFFICIAL EXECUTION COMMAND NOT RUN
```

`execution_authorised` is **false** in the frozen plan, so the command refuses before
drawing anything. The authorised execution stage flips that flag in a separate reviewed
commit. The preflight command, which runs today and draws nothing:

```
python3 -m e1a_v4.validation.runner --preflight-only
```

```
PREFLIGHT PASSED
  contract sha256            : 89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c
  plan sha256                : 142e9a8f424d970e063eaca8a0a209da365ad1408b80d9b5b7c67b763ca6c894
  seed map sha256            : bb21dd6cc9959c1b61812d54925b56d64f7ecf8a8c36c68c03605af69802979d
  analysis procedure identity: 1983ba3af64cd62480feb642ce83f38cf7d2e5f06bf9398b41b81fe1f864648c
  execution identity         : 2f4902a17c3ce0d187e308bb061cf239ee328639d313f428e22a7af175384d71
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)
```

---

## Fail-closed preflight

Every check below completes **before any RNG is created**:

1. working scientific contract identity equals the frozen contract sha256
2. prospective design, foundation and baseline identities
3. analysis procedure identity
4. every implementation file hash
5. validation plan identity
6. seed map identity and its rederivation from the declared algorithm
7. execution identity
8. no output collision
9. expected execution stage
10. execution_authorised flag

---

## Output schema

Directory `results/e1a_v4_validation`, record schema
`e1a_v4_validation_result/1`, manifest schema
`e1a_v4_validation_manifest/1`.

Per record: `case_id`, `replicate_id`, `seed_family`, `seed_identity`, `field_id`, `truth_parameters`, `branch_a_observed`, `analysis_status`, `G1`, `G2`, `G3`, `G4`, `G5`, `P1`, `beta_hat`, `P2`, `P3`, `P4`, `complete_pass`, `refusal_reason`, `procedure_identity`, `contract_sha256`, `plan_sha256`, `implementation_commit`.

Aggregate: `success_count`, `failure_count`, `refusal_count`, `refusals_by_reason`, `confidence_bound`, `false_bridge_acceptance`, `per_field_geometry_rates`, `mode_resolution_behaviour`, `g5_diagnostics`, `scale_control_recovery`, `classification`.

Reproduction: seed family + master seed + case id + replicate index regenerate any record exactly.

Failure classifications, frozen before execution:
`SOFTWARE_OR_INVARIANT_FAILURE`, `CALIBRATION_FAILURE`, `STATISTICAL_SIZE_FAILURE`, `TRUE_BRIDGE_POWER_FAILURE`, `FALSE_BRIDGE_DISCRIMINATION_FAILURE`, `STRUCTURED_REFUSAL_EXCESS`, `MODE_RESOLUTION_FAILURE`, `BLINDED_SCALE_CONTROL_FAILURE`, `NUMERICAL_OR_PRECISION_FAILURE`, `VALIDATION_INCONCLUSIVE`, `VALIDATION_PASS`.

An inconvenient scientific result is NOT classified as a software bug unless an actual implementation defect is demonstrated. A demonstrated bug preserves the failed result and requires a separately versioned correction and revalidation stage.

**Prohibited after execution:**
margins, alpha allocations, theta_cap, replicate definitions, case definitions, uncertainty scenarios, field parameters, acceptance rules, seed values, false-bridge alternatives, complete-pass denominator.

---

## Author dispositions required before execution

### G1 — affects `C8`

**Gap.** blinded scale control has no quantitative recovery criterion beyond beta = 1/c

**Source.** baseline section 14.2 and design section 13 state the target but no tolerance or coverage rule

**Resolution.** AUTHOR DISPOSITION REQUIRED BEFORE EXECUTION. Not chosen here, and must not be chosen after execution.

### G2 — affects `C7`

**Gap.** false-bridge alternatives have no maximum acceptable acceptance rate

**Source.** design section 13 states 'acceptance = failure to detect' but sets no numeric criterion

**Resolution.** AUTHOR DISPOSITION REQUIRED BEFORE EXECUTION.

### G3 — affects `C1, C2, C3`

**Gap.** sigma_psi is recorded in the contract as 'to be declared'

**Source.** contract hypothetical_uncertainty_scenario.sigma_psi

**Resolution.** The plan evaluates these cases at EVERY sigma_psi in the design section 15 item 6 declared set {0, 0.2, 0.5, 1.0} degrees rather than inventing one value. The author must fix which sigma_psi the >= 0.90 target is asserted at.

---

## Static tests

```
$ python3 test_e1a_v4_preexec.py

preflight refuses before RNG
  [PASS] clean tree preflights successfully
  [PASS] FROZEN contract mismatch refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] plan hash mismatch refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] analysis procedure mismatch refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] implementation file hash mismatch refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] hand-edited seed map refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] master seed mismatch refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] output collision refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] unexpected execution stage refuses before RNG  -- RNG_CALL_COUNT delta = 0
  [PASS] no RNG was created by ANY failed preflight  -- RNG_CALL_COUNT = 0

execution not authorised
  [PASS] frozen plan has execution_authorised = false
  [PASS] run(execute=True) refuses on the frozen plan
  [PASS] the RNG factory was never called  -- RNG_CALL_COUNT = 0
PREFLIGHT PASSED
  contract sha256            : 89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c
  plan sha256                : 142e9a8f424d970e063eaca8a0a209da365ad1408b80d9b5b7c67b763ca6c894
  seed map sha256            : bb21dd6cc9959c1b61812d54925b56d64f7ecf8a8c36c68c03605af69802979d
  analysis procedure identity: 1983ba3af64cd62480feb642ce83f38cf7d2e5f06bf9398b41b81fe1f864648c
  execution identity         : 2f4902a17c3ce0d187e308bb061cf239ee328639d313f428e22a7af175384d71
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)
  [PASS] preflight-only CLI returns 0
PREFLIGHT PASSED
  contract sha256            : 89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c
  plan sha256                : 142e9a8f424d970e063eaca8a0a209da365ad1408b80d9b5b7c67b763ca6c894
  seed map sha256            : bb21dd6cc9959c1b61812d54925b56d64f7ecf8a8c36c68c03605af69802979d
  analysis procedure identity: 1983ba3af64cd62480feb642ce83f38cf7d2e5f06bf9398b41b81fe1f864648c
  execution identity         : 2f4902a17c3ce0d187e308bb061cf239ee328639d313f428e22a7af175384d71
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
EXECUTION REFUSED: --execute requires --i-have-execution-authorisation
  [PASS] --execute without the authorisation flag returns 2
  [PASS] CLI never drew a random number  -- RNG_CALL_COUNT = 0

seed separation
  [PASS] committed seed map rederives exactly
  [PASS] no seed overlap between families  -- 5 families
  [PASS] calibration and validation families are distinct
  [PASS] branch_a_measurement has its own family, not Branch-B's
  [PASS] analysis-layer families are a strict subset
  [PASS] seed values are not hand-picked
  [PASS] replicate IDs deterministic  -- 16726996319146113107
  [PASS] different replicate index -> different seed
  [PASS] same index in a different family -> different seed
  [PASS] a consumer cannot read another family's stream
  [PASS] a family may read its own stream
  [PASS] master seed derives from the contract identity, not a chosen number
  [PASS] a different contract gives a different master seed

plan determinism and MD/JSON agreement
  [PASS] plan declares exactly 8 cases  -- C1_true_bridge_complete, C2_geometry_false_rejection, C3_g5_block, C4_surrogate_validity, C5_plug_in_branch_a, C6_mode_resolution_boundary, C7_false_bridge, C8_blinded_scale_control
  [PASS] every case carries all 14 required descriptors
  [PASS] every case carries an EXACT v4 classification enum  -- C1=NEWLY REQUIR; C2=RETAINED BUT; C3=NEWLY REQUIR; C4=NEWLY REQUIR; C5=NEWLY REQUIR; C6=NEWLY REQUIR; C7=RETAINED BUT; C8=RETAINED UNC
  [PASS] explanatory detail lives in a separate note field, not in the enum
  [PASS] markdown renders the enum and the note separately
  [PASS] case plan deterministic: loading twice gives identical content
  [PASS] adopted rules in the plan match the contract exactly
  [PASS] no Bonferroni and no fixed-B0 may return
  [PASS] three authority gaps are recorded, none invented away
  [PASS] gap cases carry no invented criterion
  [PASS] markdown carries case C1_true_bridge_complete
  [PASS] markdown carries case C2_geometry_false_rejection
  [PASS] markdown carries case C3_g5_block
  [PASS] markdown carries case C4_surrogate_validity
  [PASS] markdown carries case C5_plug_in_branch_a
  [PASS] markdown carries case C6_mode_resolution_boundary
  [PASS] markdown carries case C7_false_bridge
  [PASS] markdown carries case C8_blinded_scale_control
  [PASS] markdown carries the exact frozen execution command
  [PASS] markdown states the command was NOT run
  [PASS] markdown carries the frozen seed for blinded_scale_control
  [PASS] markdown carries the frozen seed for branch_a_measurement
  [PASS] markdown carries the frozen seed for calibration
  [PASS] markdown carries the frozen seed for confirmatory
  [PASS] markdown carries the frozen seed for validation
  [PASS] markdown and JSON agree on the contract identity

output schema
  [PASS] result schema freezes all 24 fields
  [PASS] plan and code agree on the record fields
  [PASS] 11 failure classifications frozen
  [PASS] plan and code agree on the classifications
  [PASS] manifest reproducible and identical across calls
  [PASS] aggregate carries the unconditional denominator rule
  [PASS] conditional diagnostics are labelled SECONDARY
  [PASS] calibration generator identity recorded in the plan
  [PASS] G5 is excluded from calibration by design

identities
  [PASS] adding the validation package did NOT move the analysis identity  -- 1983ba3af64cd624...
  [PASS] execution identity deterministic  -- 2f4902a17c3ce0d1...
  [PASS] execution identity differs from the analysis identity
  [PASS] a changed plan changes the execution identity
  [PASS] all 7 validation modules enter the execution identity
  [PASS] frozen hash matches on disk: e1a_v4/__init__.py
  [PASS] frozen hash matches on disk: e1a_v4/branch_a.py
  [PASS] frozen hash matches on disk: e1a_v4/calibration.py
  [PASS] frozen hash matches on disk: e1a_v4/contract.py
  [PASS] frozen hash matches on disk: e1a_v4/effective_size.py
  [PASS] frozen hash matches on disk: e1a_v4/endpoints.py
  [PASS] frozen hash matches on disk: e1a_v4/geometry.py
  [PASS] frozen hash matches on disk: e1a_v4/identity.py
  [PASS] frozen hash matches on disk: e1a_v4/numerics.py
  [PASS] frozen hash matches on disk: e1a_v4/seeds.py
  [PASS] frozen hash matches on disk: e1a_v4/status.py
  [PASS] frozen hash matches on disk: e1a_v4/world.py

E1a v4 pre-execution gate: 81 passed, 0 failed, 6 groups
Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)
  RNG_CALL_COUNT        : 0
  RANDOM DRAWS          : 0
  TRAJECTORIES          : 0
  CALIBRATION EXECUTION : NOT RUN
  VALIDATION CAMPAIGN   : NOT RUN
```

```
$ python3 test_e1a_v4.py
E1a v4 implementation gate: 119 passed, 0 failed, 13 groups

$ python3 docs/e1a/validate_e1a_v4_contract.py
============================================================================
  113 / 113 checks passed
============================================================================

$ git diff --check
[clean]
```

| suite | passed | failed |
|---|---:|---:|
| pre-execution | **81** | 0 |
| implementation | **119** | 0 |
| design authority | **113** | 0 |

Every failed-preflight check asserts, with a sentinel provider that counts calls, that
`RNG_CALL_COUNT == 0`.

Everything requiring stochastic execution is **PENDING EXECUTION**, never PASS.

---

## Explicit non-execution

```
RANDOM DRAWS = 0
TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN
VALIDATION CAMPAIGN = NOT RUN
```

No calibration distribution was sampled and no scientific outcome was inspected.

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting local HEAD | `6ca47f4e9e99a729161f9c4a14d4e52ec11353a6` |
| **work commit** | `475633ced7ae7192849e9bbf0116dc9ef99e86c1` |
| **tree SHA** | `3e2e1cdebc9c767c0bed045a1677e86f0fe770d0` |
| working tree after the work commit | **clean** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — **unchanged** |

Every unpushed ancestor was audited and is E1a design, implementation or report work;
nothing touches anything outside `docs/e1a/`, `docs/theory/`, `e1a_v4/` and the two E1a
test files. No commit was amended, no history rewritten.

Committed files:

```
A	docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md
A	docs/e1a/e1a_v4_seed_map.json
A	docs/e1a/e1a_v4_synthetic_validation_plan.json
A	e1a_v4/validation/__init__.py
A	e1a_v4/validation/calibrate.py
A	e1a_v4/validation/generate.py
A	e1a_v4/validation/plan.py
A	e1a_v4/validation/results.py
A	e1a_v4/validation/runner.py
A	e1a_v4/validation/seeds.py
A	test_e1a_v4_preexec.py
```

This report was generated **after** the work commit `475633c` and is committed
separately, per the convention in `docs/e1a/E1A_V4_ADOPTION_REPORT.md`.

---

## Next stage

```
E1a v4 synthetic validation EXECUTION
READY FOR AUTHORISATION
NOT STARTED
```

Execution requires separate authorisation **and** the three author dispositions above.
Preregistration, physical execution, E1b and Stage B remain unauthorised.

---

```
SYNTHETIC VALIDATION PACKAGE FROZEN
```
