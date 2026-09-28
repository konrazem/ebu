# E1a v4 — SYNTHETIC VALIDATION PLAN

**PRE-EXECUTION FROZEN PACKAGE. NOTHING IN THIS PLAN HAS BEEN EXECUTED.**

Random draws: **0**. Trajectories: **0**. Calibration execution: **NOT RUN**. Validation
campaign: **NOT RUN**. No scientific outcome has been inspected.

This document and `docs/e1a/e1a_v4_synthetic_validation_plan.json` are the authoritative
prospective sources for the E1a v4 synthetic-validation campaign. The JSON is the mechanical
schema and ordering source; this Markdown is its normative human rendering. **Any mismatch is
an integrity failure requiring fail-closed refusal**, and `test_e1a_v4_preexec.py` checks it.

Authority rank: below the frozen foundation, below the working baseline, below the adopted
prospective design and its contract. **This plan changes no adopted decision rule.**

---

## 1. Frozen identities

The official runner refuses to execute if any of these differs.

| item | sha256 / value |
|---|---|
| design contract | `89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c` |
| prospective design | `f20bc885bf400ce3429120e4a0e42915ba2fb15249d88914fd7e55eb1b373f68` |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| analysis procedure identity | `1983ba3af64cd62480feb642ce83f38cf7d2e5f06bf9398b41b81fe1f864648c` |
| implementation work commit | `e4b73d7fbd84d329f4326af443fd1918bc44a874` |

Implementation file hashes are frozen for all 12 analysis modules; see the JSON.

> **Which configuration the frozen analysis identity uses.** The configuration mapping is
> part of the identity, so a different configuration yields a different digest *by design*.
> The frozen value above is `procedure_identity(binding, configuration={}, root)`. The
> implementation report quoted the `{"stage": "bounded_implementation"}` variant
> `8dd48f42f7ccd259a76e50ef4e1ee4c0a3c5b43986bc54d75438b1acdf15dbe0`. Preflight recomputes
> the empty-configuration value and compares it to the frozen one.

**Two identities, deliberately separate.** The **analysis procedure identity** binds the 12
analysis modules, the contract and the adopted rules — calibration artifacts bind to *this*, as
the bounded implementation requires, and adding the validation package does **not** change it.
The **execution procedure identity** binds the analysis identity plus the validation module
hashes, this plan and the seed map. It is derived at preflight rather than embedded here,
because embedding it in the file whose hash it covers would be self-referential; it is recorded
in the pre-execution report and recomputed by every preflight.

### Frozen execution versus general implementation

A **general** analysis reads whatever valid contract it is given — that is correct architecture
and prevents magic numbers in code. An **official validation run** may not: `bind_execution`
requires the exact adopted contract identity and refuses anything else **before an RNG can be
created**. Both behaviours are tested.

---

## 2. Adopted rules, unchanged

| rule | value |
|---|---|
| `delta_cross` | `0.02` |
| `z_cross` | `1.959963985` |
| `delta_abs` | `0.05` |
| `z_abs` | `1.959963985` |
| `alpha_geom` | `0.005` |
| `alpha_1` | `0.004` |
| `alpha_2` | `0.001` |
| `theta_cap_deg` | `5.0` |
| `rank_tol` | `1e-12` |
| `pipeline_target` | `0.9` |
| `P3_applies_to` | `EVERY tested field` |
| `P4_classification` | `DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK` |
| `multiplicity_correction` | `NONE - intersection-union test` |

Forbidden and unchanged: **Bonferroni correction**; **fixed-B0 normalisation**; **power-spectrum / corner-frequency / equipartition Branch-A calibration**.

---

## 3. The eight cases

Eight cases, one per scientifically required purpose traceable to committed or adopted authority. P2 (cross-field) and P3 (absolute) are NOT separate generating cases: they are endpoints evaluated on C1's data so the shared reference-field dependence and the common-mode calibration error are preserved. Simulating the three P2 ratios independently, or reverting P3 to reference-only, would destroy exactly the structure being validated. The count is eight because eight purposes are required, not to preserve a historical number.

### `C1_true_bridge_complete` — primary

**Purpose.** Does the implemented COMPLETE pipeline (P1 AND P2 AND P3 AND P4) achieve the adopted >= 0.90 target?

| | |
|---|---|
| v4 classification | **NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION** |
| authority | design section 15 items 4 and 10; contract complete_pipeline.target_true_bridge_success |
| truth model | K_theta = H_theta with beta_true = 1 at every field |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi from the design section 15 item 6 declared set |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | complete pass in the large majority of replicates |
| seed family | `validation` |
| replicate count | **300** |

**Pass / fail criterion.** Clopper-Pearson one-sided 95% LOWER bound on the complete-pass rate >= 0.90; requires >= 279/300. An observed proportion above 0.90 is NOT sufficient by itself.

### `C2_geometry_false_rejection` — primary

**Purpose.** Achieved P1 false-rejection rate per declared field, covering G1-G5, the two-block combination, mode resolution and structured refusals

| | |
|---|---|
| v4 classification | **RETAINED BUT UPDATED FOR V4** |
| classification note | alpha_geom 1% -> 0.5%, two-block union rule |
| authority | design section 15 item 3 |
| truth model | true null K_theta = H_theta |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | false rejection at or below alpha_geom = 0.5% |
| seed family | `validation` |
| replicate count | **400** |

**Pass / fail criterion.** Clopper-Pearson one-sided 95% UPPER bound <= 3% at EVERY declared field, R = 400 each (max 6 rejections). An UPPER bound is required; a lower bound cannot demonstrate control.

### `C3_g5_block` — primary

**Purpose.** Validate the actual G5 block from full generated observations: sample-mean centring, A4-based leading-order variance, finite-sample behaviour, correlation, the two-mode max statistic and its interaction with the two-block gate

| | |
|---|---|
| v4 classification | **NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION** |
| authority | design section 15 item 8 |
| truth model | true null; G5 computed from generated trajectories, never as an independent companion variable |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | block-2 achieved size consistent with alpha_2 = 0.1%; delta-method error quantified |
| seed family | `validation` |
| replicate count | **400** |

**Pass / fail criterion.** Clopper-Pearson one-sided 95% UPPER bound on the block-2 rejection rate <= 3%, R = 400; report the measured sd(g2) against the leading-order 24 A4 / n prediction.

### `C4_surrogate_validity` — primary

**Purpose.** Achieved Block-1 size when calibration uses the covariance-matched surrogate but validation data come from the declared actual correlated process; measure the OPERATING-QUANTILE discrepancy, not covariance agreement

| | |
|---|---|
| v4 classification | **NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION** |
| authority | design section 15 item 5; design Appendix classification of the surrogate as an APPROXIMATION |
| truth model | calibration from the surrogate, validation from the declared OU process |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | achieved Block-1 rejection rate close to alpha_1 = 0.4% |
| seed family | `calibration + validation` |
| replicate count | **2000** |

**Pass / fail criterion.** report the achieved Block-1 rate with a Clopper-Pearson 95% two-sided interval over R = 2000 validation draws against the nominal alpha_1; calibration uses R_cal = 50000 (realised size 0.4000% +/- 0.0282%). Discrepancy is REPORTED and classified, not tuned away.

### `C5_plug_in_branch_a` — primary

**Purpose.** Effect of analysing with measured/noisy H_A and tau_A while truth is generated from H_true and tau_true, including shape and orientation uncertainty

| | |
|---|---|
| v4 classification | **NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION** |
| authority | design section 15 item 6 |
| truth model | true null; analysis receives only the Branch-A measured field |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty | swept: sigma_k in {0, 0.5%, 1%} x sigma_psi in {0, 0.2, 0.5, 1.0} degrees, 12 cells |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | achieved size degrades as sigma_psi grows; the magnitude is the result |
| seed family | `validation + branch_a_measurement` |
| replicate count | **400** |

**Pass / fail criterion.** report the Clopper-Pearson one-sided 95% UPPER bound on the P1 rejection rate in EVERY one of the 12 declared cells, R = 400 each. No cell may be dropped after inspection.

### `C6_mode_resolution_boundary` — primary

**Purpose.** Size AND detection behaviour around theta_cap = 5 degrees at the predeclared boundary neighbourhood

| | |
|---|---|
| v4 classification | **NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION** |
| authority | design section 15 item 7; design section 10 |
| truth model | true null at rho = boundary, boundary -20%, boundary +20% |
| fields affected | synthetic two-mode field at the declared rho |
| beta truth | `1.0` |
| geometry truth | rho in {1.019573, 1.024467, 1.029360} at N_12 = 224726 |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | merge below the boundary, split above; size controlled on both sides |
| seed family | `validation` |
| replicate count | **400** |

**Pass / fail criterion.** Clopper-Pearson one-sided 95% UPPER bound on the P1 rejection rate <= 3% at each of the three declared rho, R = 400 each; report the merge/split decision rate at each. theta_cap MUST NOT be changed after observing the result.

### `C7_false_bridge` — negative control

**Purpose.** Probability of incorrectly ACCEPTING a false bridge, for every declared non-commensurable alternative including the hard near-margin case

| | |
|---|---|
| v4 classification | **RETAINED BUT UPDATED FOR V4** |
| classification note | evaluated against the all-field P3 and the IUT P2 |
| authority | design section 13; contract false_bridge_controls |
| truth model | beta_theta = (1,1.06,1,1); (1,0.93,1.05,1); (1,1,1,1.10); hard (1,1.025,1,1) |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `per alternative` |
| geometry truth | as declared per field |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | acceptance close to zero for the coarse alternatives; the hard 2.5% case is the informative one |
| seed family | `validation` |
| replicate count | **400** |

**Pass / fail criterion.** report the Clopper-Pearson one-sided 95% UPPER bound on the acceptance rate for EVERY alternative, R = 400 each. NO adopted maximum acceptance rate exists -- see authority_gaps G2. The criterion must be declared BEFORE execution.

### `C8_blinded_scale_control` — positive control

**Purpose.** Blinded duplicate-branch scale control: Branch-A declared scale multiplied by a hidden c, analysis must recover beta = 1/c

| | |
|---|---|
| v4 classification | **RETAINED UNCHANGED** |
| authority | baseline section 14.2 (committed); design section 13 |
| truth model | true null with the Branch-A scale multiplied by a hidden c on a DUPLICATE branch that never touches primary data |
| fields affected | theta0_circular, theta1_power, theta2_ellipse, theta3_temperature |
| beta truth | `1/c on the blinded branch` |
| geometry truth | as declared per field |
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | beta_hat on the blinded branch concentrates on 1/c |
| seed family | `blinded_scale_control` |
| replicate count | **200** |

**Pass / fail criterion.** report the distribution of beta_hat * c. NO quantitative recovery tolerance exists in adopted authority -- see authority_gaps G1. The criterion must be declared BEFORE execution.

---

## 4. Generating model

**Branch B — the declared observation process.**

```
process        declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)
transition     x_{k+1} = phi_r x_k + sqrt(1 - phi_r^2) L z, per mode, EXACT
phi            phi_r = exp(-dt / tau_r)
initialisation x_0 ~ N(x*, Sigma_theta); stationary at step 0; burn_in_steps = 0
dt             0.00012 s
T_total        240.0 s
n_samples      2000000
```

> **the v3 convention of starting at x = 0 is FORBIDDEN: it is not stationary.**

**Branch A — the measurement-error model.**

- **model**: H_A = decorated H_true; its OWN seed family branch_a_measurement
- **common mode**: ONE draw per experiment, shared across every field, so it cancels in the P2 ratio and not in P3
- **per mode stiffness**: independent per mode
- **orientation**: trap-axis psi
- **thermometry**: T measured with sigma_T
- **independence**: Branch-A measurement randomness is exogenous and never a function of the Branch-B trajectory

**Truth visibility.** H_true and tau_true are known to the SCORING layer only. The analysis pipeline receives only the Branch-A measured field, exactly as in the real experiment.

| field | k (µN/m) | T (K) | rotation | reference | beta_true |
|---|---|---:|---:|:--:|---:|
| `theta0_circular` | [100, 100] | 298 | 0° | yes | 1.0 |
| `theta1_power` | [210, 210] | 298 | 0° | no | 1.0 |
| `theta2_ellipse` | [150, 60] | 298 | 30° | no | 1.0 |
| `theta3_temperature` | [100, 100] | 318 | 0° | no | 1.0 |

Relaxation rule: `tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a`.

---

## 5. Calibration

Generator `e1a_v4.validation.calibrate.generate_block1_artifact`, identity `EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1`, seed family
`calibration`, **R = 50000**, gates G1, G2, G3, G4.
Realised size 0.4000% +/- 0.0282% at alpha_1 = 0.004 (Beta(k, R+1-k), k = ceil(alpha_1 R) = 200).

> **G5 is deliberately absent from calibration.** G5 is NOT generated here. It is not a function of the covariance, so producing it as an independent companion would destroy its real dependence on the trajectory statistics. G5 is validated in the validation layer from full observations.

Workflow, frozen:

```
    CALIBRATION DATA
    -> fix calibration artifacts and thresholds
    -> lock artifact identities
    -> VALIDATION DATA
    -> evaluate predeclared operating characteristics
    -> CONFIRMATORY DATA only if the adopted protocol requires it
```

- **no validation result may change a calibration threshold**
- **no confirmatory result may change calibration or validation design**

Artifact filenames: `calibration/block1_theta0_circular.json`, `calibration/block1_theta1_power.json`, `calibration/block1_theta2_ellipse.json`, `calibration/block1_theta3_temperature.json`.

---

## 6. Statistical assurance

| quantity | target | estimator | bound | R | acceptance rule |
|---|---|---|---|---:|---|
| complete true-bridge pipeline success | `>= 0.90` | complete-pass proportion over declared replicates | Clopper-Pearson one-sided LOWER | 300 | >= 279 / 300 complete passes |
| P1 false-rejection rate, per field | `alpha_geom = 0.005` | rejection proportion | Clopper-Pearson one-sided UPPER | 400 | upper bound <= 0.03, i.e. <= 6 rejections of 400 |
| block-2 (G5) rejection rate | `alpha_2 = 0.001` | rejection proportion | Clopper-Pearson one-sided UPPER | 400 | upper bound <= 0.03 |
| Block-1 achieved size under the surrogate | `alpha_1 = 0.004` | rejection proportion | Clopper-Pearson two-sided | 2000 | REPORTED and classified; the discrepancy is the result |
| false-bridge acceptance, per alternative | `AUTHORITY GAP G2` | acceptance proportion | Clopper-Pearson one-sided UPPER | 400 | NOT DECLARED IN ADOPTED AUTHORITY - must be declared before execution |
| blinded scale recovery beta_hat * c | `AUTHORITY GAP G1` | distribution of beta_hat * c | reported | 200 | NOT DECLARED IN ADOPTED AUTHORITY - must be declared before execution |

**Complete-pass denominator:** every declared validation replicate. structured refusals COUNT AS FAILURES for complete-pipeline success permitted only when explicitly labelled SECONDARY, reported beside the unconditional figure refusal counts AND reasons are reported.

---

## 7. Seed separation

Seeds are **derived, never chosen**. Every value below reproduces from the declared algorithm,
and the runner refuses if the committed map does not rederive.

```
hash                   first 8 bytes of sha256(text), big-endian unsigned
master                 DOMAIN|master|contract_sha256|campaign
family                 DOMAIN|family|master_hex16|family_name
replicate              DOMAIN|replicate|family_hex16|case=<id>|rep=<index>
hand_picked_values     False
```

| family | seed |
|---|---:|
| master | `12737552942663785904` |
| `blinded_scale_control` | `9479310386300230328` |
| `branch_a_measurement` | `11004995623645776693` |
| `calibration` | `15379082101033647447` |
| `confirmatory` | `9585841150145721670` |
| `validation` | `11476631527835384658` |

`branch_a_measurement` is its **own** family: Branch-A measurement error is exogenous
randomness the analysis never sees, so it never reuses the Branch-B trajectory stream. The
analysis layer's four families are a strict subset, so the analysis procedure identity is
untouched. No single mutable global RNG is used anywhere.

---

## 8. Controls

| control | purpose | case |
|---|---|---|
| blinded scale distortion | scale-detection sensitivity | `C8` |
| geometry / coordinate permutation | destroys the correlation structure; the geometry control | `C7` |
| false-beta alternatives | false-bridge discrimination | `C7` |
| time shuffle | AUTOCORRELATION control only, not a geometry control; leaves S identical to 1e-30 | `C7` |
| paired hidden-scale distortion c = 1.07 / 0.90 | acts through P3/beta; gates are scale-invariant | `C8` |
| forbidden H := K | recorded as vacuous; demonstration only | `C7` |

---

## 9. Output schema

Directory `results/e1a_v4_validation`, record schema `e1a_v4_validation_result/1`, manifest schema
`e1a_v4_validation_manifest/1`.

Per record: `case_id`, `replicate_id`, `seed_family`, `seed_identity`, `field_id`, `truth_parameters`, `branch_a_observed`, `analysis_status`, `G1`, `G2`, `G3`, `G4`, `G5`, `P1`, `beta_hat`, `P2`, `P3`, `P4`, `complete_pass`, `refusal_reason`, `procedure_identity`, `contract_sha256`, `plan_sha256`, `implementation_commit`.

Aggregate: `success_count`, `failure_count`, `refusal_count`, `refusals_by_reason`, `confidence_bound`, `false_bridge_acceptance`, `per_field_geometry_rates`, `mode_resolution_behaviour`, `g5_diagnostics`, `scale_control_recovery`, `classification`.

Reproduction: seed family + master seed + case id + replicate index regenerate any record exactly.

---

## 10. Failure classifications

- `SOFTWARE_OR_INVARIANT_FAILURE`
- `CALIBRATION_FAILURE`
- `STATISTICAL_SIZE_FAILURE`
- `TRUE_BRIDGE_POWER_FAILURE`
- `FALSE_BRIDGE_DISCRIMINATION_FAILURE`
- `STRUCTURED_REFUSAL_EXCESS`
- `MODE_RESOLUTION_FAILURE`
- `BLINDED_SCALE_CONTROL_FAILURE`
- `NUMERICAL_OR_PRECISION_FAILURE`
- `VALIDATION_INCONCLUSIVE`
- `VALIDATION_PASS`

> An inconvenient scientific result is NOT classified as a software bug unless an actual implementation defect is demonstrated. A demonstrated bug preserves the failed result and requires a separately versioned correction and revalidation stage.

---

## 11. No post-outcome tuning

**Prohibited after execution:** margins, alpha allocations, theta_cap, replicate definitions, case definitions, uncertainty scenarios, field parameters, acceptance rules, seed values, false-bridge alternatives, complete-pass denominator.

- On scientific failure: **report failure**.
- On a demonstrated software defect: preserve the failed result; require a separately versioned correction and revalidation stage.

---

## 12. Authority gaps — AUTHOR DISPOSITION REQUIRED BEFORE EXECUTION

These are identified **now**, before execution, precisely so that no criterion is chosen after
results are seen. **None is invented here.**

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

## 13. Execution

Preflight, which runs today and draws nothing:

```
python3 -m e1a_v4.validation.runner --preflight-only
```

**OFFICIAL EXECUTION COMMAND, FROZEN:**

```
python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
```

**OFFICIAL EXECUTION COMMAND NOT RUN.** `execution_authorised` is `false` in the frozen plan,
so the command refuses before drawing anything. The authorised execution stage flips that flag
in a separate reviewed commit.

Preflight checks, all completed **before any RNG is created**:

1. working scientific contract identity equals the frozen contract sha256
1. prospective design, foundation and baseline identities
1. analysis procedure identity
1. every implementation file hash
1. validation plan identity
1. seed map identity and its rederivation from the declared algorithm
1. execution identity
1. no output collision
1. expected execution stage
1. execution_authorised flag
