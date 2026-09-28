# E1a v4 — SYNTHETIC VALIDATION PLAN

**PRE-EXECUTION FROZEN PACKAGE, REPAIRED. NOTHING IN THIS PLAN HAS BEEN EXECUTED.**

Plan version **1.3.0**. An independent audit found three pre-execution defects in the
package that had been described as ready for execution; all three were reproduced and
repaired here, **before any random scientific outcome existed**. See section 14.
**No E1a scientific decision rule changed.**

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
| design contract | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| prospective design | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| analysis procedure identity | `bc1c0fce3b9004aed5f6b4be2162bc876697536ee614b2e57f680f3a65dc283e` |
| calibration artifact schema | `e1a_v4_block1_calibration/2` |
| implementation work commit | `e4b73d7fbd84d329f4326af443fd1918bc44a874` |

Implementation file hashes are frozen for all 12 analysis modules; see the JSON.

> The analysis procedure identity **moved** in the pre-execution repair, because
> `e1a_v4/calibration.py` and `e1a_v4/endpoints.py` changed. Its superseded value was
> `af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4`. The **contract** and
> the **seed map** did not move, and because the seed derivation binds only to the contract
> identity, **every seed value is unchanged**. See section 13.

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
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3] |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | complete pass in the large majority of replicates |
| seed family | `validation` |
| allowed seed families | `validation`, `branch_a_measurement` |
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
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3] |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | false rejection at or below alpha_geom = 0.5% |
| seed family | `validation` |
| allowed seed families | `validation`, `branch_a_measurement` |
| replicate count | **400** |

**Pass / fail criterion.** PER FIELD, never pooled, R = 400, nominal alpha_geom = 0.005. Inflation is detected iff CP_lower(rejections, 400) > 0.005, i.e. 6 or more rejections -> STATISTICAL_SIZE_FAILURE. 0-5 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED, which means this experiment did not establish excess size, NOT that nominal size is proved. Secondary gross-inflation diagnostic (CP upper <= 0.03) may be reported but is not validation of alpha_geom.

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
| Branch-A uncertainty | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3] |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | block-2 achieved size consistent with alpha_2 = 0.1%; delta-method error quantified |
| seed family | `validation` |
| allowed seed families | `validation`, `branch_a_measurement` |
| replicate count | **400** |

**Pass / fail criterion.** R = 400, nominal alpha_2 = 0.001. Inflation is detected iff CP_lower(G5 rejections, 400) > 0.001, i.e. 3 or more -> STATISTICAL_SIZE_FAILURE. 0-2 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED. Also report the measured sd(g2) against the leading-order 24 A4 / n prediction.

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
| allowed seed families | `calibration`, `validation`, `branch_a_measurement` |
| replicate count | **2000** |

**Pass / fail criterion.** R = 2000, nominal alpha_1 = 0.004. RETAIN the full two-sided interval and the observed operating-quantile discrepancy. IN ADDITION, classify inflation: detected iff CP_lower(rejections, 2000) > 0.004, i.e. 14 or more -> STATISTICAL_SIZE_FAILURE; 0-13 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED. The binary diagnostic does not replace the discrepancy report.

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
| allowed seed families | `validation`, `branch_a_measurement` |
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
| allowed seed families | `validation`, `branch_a_measurement` |
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
| allowed seed families | `validation`, `branch_a_measurement` |
| replicate count | **400** |

**Pass / fail criterion.** For EACH declared alternative INDEPENDENTLY: one-sided 95% Clopper-Pearson UPPER bound on the false-acceptance rate <= 0.025 over R = 400, i.e. <= 4/400; 5 or more fails. Counts are never pooled and easy and hard alternatives are never averaged. [disposition G2, closed prospectively]

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
| allowed seed families | `blinded_scale_control`, `branch_a_measurement` |
| replicate count | **200** |

**Pass / fail criterion.** beta_tilde_theta = c * beta_hat_theta must satisfy the SAME P3 absolute-equivalence rule (delta_abs = 0.05, z_abs = 1.959963985, h_theta = z sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2)) at EVERY tested field, for BOTH c = 1.07 and c = 0.90; any non-ESTIMATED field fails that branch. One replicate succeeds only if both branches pass. Campaign: one-sided 95% Clopper-Pearson LOWER bound on paired-control success >= 0.90 over R = 200, i.e. >= 188/200. [disposition G1, closed prospectively]


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

### 5.1 Complete calibration condition (repair B1)

An artifact is compatible only with the **exact condition it was calibrated at**, digested by
`e1a_v4.calibration.CalibrationCondition`. Artifact schema **`e1a_v4_block1_calibration/2`**; a
schema-1 artifact is **refused, not reinterpreted**.

**Bound** — every input that changes the Block-1 null law:

`field_id`, `H_normalised` (= `H_A / tr H_A`: eigenvalue ratios **and** orientation), `n`,
`dt`, `tau_modes`, `phi_modes`, `mode_blocks`, `theta_cap_deg`, `alpha_1`, `replicates`,
`gates`, `calibrator_identity`, `procedure_identity`, `contract_sha256`, `plan_sha256`.

**Not bound, with reason:**

| quantity | why not |
|---|---|
| `T_total` | exactly `n * dt` |
| `N_ab` | exactly determined by `(phi_modes, n)`; the primitives are bound instead, which is strictly stronger |
| `rank_tol` | never read on the calibration path |
| `alpha_2` | block 2 only |
| `delta_cross`, `delta_abs`, `z_cross`, `z_abs` | P2 and P3 only |
| `sigma_k`, `sigma_cm`, `sigma_psi`, `sigma_T` | the calibrator never reads them |
| overall scale of `H_A` | every Block-1 gate is invariant to `H_A -> c H_A` in **exact arithmetic**, verified numerically to ~1e-12 relative. The trace-normalised form is the canonical representative but is **not bit-invariant**: `c*H` renormalises one ulp away, so the digest refuses the rescaled artifact. Fail-closed by one ulp, the conservative direction, and free because no cross-field reuse is permitted |

Canonicalisation is `float.hex()` per float, then `json.dumps(sort_keys, separators,
ensure_ascii)`, then SHA-256. **A rounded human-formatted string is never the identity.**

> **Superseded.** `branch_a_signature` bound only the eigenvalue **ratios** and `n`.
> `theta0_circular` and `theta1_power` are both isotropic, so their ratios are **identical**,
> yet `tau = gamma/k` differs by `2.1x` and their per-element effective sizes differ by about
> **1.47x**. The `theta0` artifact was accepted for `theta1`, and the stored `field_id` was
> never compared. `branch_a_signature` is retained as **provenance only**.

`field_id` is validated as provenance and fail-safe isolation. It is **not** the mathematical
protection: the complete condition is.

### 5.2 Threshold algorithm and artifact reuse (repair B2)

```
1 + #{j != i : d_j >= d_i}  =  #{j : d_j >= d_i}
```

Exact, not an approximation: the excluded term contributes exactly `1` because `d_i >= d_i`,
both sides are integer counts, and ties are handled identically.

| | old | new |
|---|---|---|
| p_min null | `O(R^2)` | `O(R log R)` |
| when computed | **rebuilt on every P1 evaluation** | **once**, at artifact construction |

Finalised once and stored on the artifact: the sorted null marginals per gate, the p_min null
distribution, and the critical p_min. `p1_geometry` reads the stored threshold.
`p_min_null_reference` retains the superseded quadratic form **for equivalence tests only**.

A non-finite null draw or observed statistic is **refused as an invalid calibration artifact**,
never sorted.

**No circularity.** The stored quantities are functions of the calibration draws and the frozen
`alpha_1` alone. No validation or confirmatory observation can reach them, and no validation
result can trigger a threshold recomputation. `CalibrationArtifact.artifact_sha256` covers the
condition digest, the draws **and** the stored derived quantities.

Artifact filenames: `calibration/block1_theta0_circular.json`, `calibration/block1_theta1_power.json`, `calibration/block1_theta2_ellipse.json`, `calibration/block1_theta3_temperature.json`.

---

## 6. Statistical assurance

| quantity | target | estimator | bound | R | acceptance rule |
|---|---|---|---|---:|---|
| complete true-bridge pipeline success | `>= 0.90` | complete-pass proportion over declared replicates | Clopper-Pearson one-sided LOWER | 300 | >= 279 / 300 complete passes |
| P1 false-rejection rate, per field | `alpha_geom = 0.005` | Clopper-Pearson one-sided LOWER (inflation test) | 400 | no inflation detected: CP_lower <= 0.005, i.e. <= 5/400, per field |
| block-2 (G5) rejection rate | `alpha_2 = 0.001` | Clopper-Pearson one-sided LOWER (inflation test) | 400 | no inflation detected: CP_lower <= 0.001, i.e. <= 2/400 |
| Block-1 achieved size under the surrogate | `alpha_1 = 0.004` | Clopper-Pearson two-sided (reported) + one-sided LOWER (inflation test) | 2000 | discrepancy REPORTED and classified; additionally no inflation detected: CP_lower <= 0.004, i.e. <= 13/2000 |
| false-bridge acceptance, per alternative | `<= 0.025 per alternative` | Clopper-Pearson one-sided UPPER | 400 | upper bound <= 0.025, i.e. <= 4 / 400, evaluated per alternative independently |
| blinded scale recovery beta_hat * c | `>= 0.90 paired-control success` | Clopper-Pearson one-sided LOWER | 200 | >= 188 / 200 paired-control successes |

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
| master | `13785910525869478477` |
| `blinded_scale_control` | `11987123625083329897` |
| `branch_a_measurement` | `62746336670861162` |
| `calibration` | `6644164099584621674` |
| `confirmatory` | `9827224290341944517` |
| `validation` | `5088042359768187837` |

`branch_a_measurement` is its **own** family: Branch-A measurement error is exogenous
randomness the analysis never sees, so it never reuses the Branch-B trajectory stream. The
analysis layer's four families are a strict subset, so the analysis procedure identity is
untouched. No single mutable global RNG is used anywhere.

### 7.1 Case-level seed permissions, mechanically enforced (repair B3)

| case | allowed seed families | why |
|---|---|---|
| `C1_true_bridge_complete` | `validation`, `branch_a_measurement` | Branch-B trajectories from validation; Branch-A measurement error is REQUIRED because disposition G3 asserts the primary >= 0.90 claim at sigma_psi = 0.5 deg and sigma_psi reaches nothing except a realised rotation into G3 |
| `C2_geometry_false_rejection` | `validation`, `branch_a_measurement` | Branch-B trajectories from validation; the declared frozen candidate scenario including sigma_psi is realised per replicate |
| `C3_g5_block` | `validation`, `branch_a_measurement` | Branch-B trajectories from validation; G5 is computed from those observations and the declared Branch-A scenario is realised |
| `C4_surrogate_validity` | `calibration`, `validation`, `branch_a_measurement` | calibration produces the surrogate null; validation produces the actual correlated observations; the declared Branch-A scenario is realised |
| `C5_plug_in_branch_a` | `validation`, `branch_a_measurement` | the sweep over sigma_k x sigma_psi IS a Branch-A measurement sweep; already declared |
| `C6_mode_resolution_boundary` | `validation`, `branch_a_measurement` | Branch-B trajectories at the three declared rho; the declared Branch-A scenario is realised |
| `C7_false_bridge` | `validation`, `branch_a_measurement` | Branch-B trajectories under each alternative; the declared Branch-A scenario is realised |
| `C8_blinded_scale_control` | `blinded_scale_control`, `branch_a_measurement` | the blinded control draws its own paired Branch-B replicates from its dedicated family; the declared Branch-A scenario is realised. The blinding factor c is applied deterministically by BranchAField.blinded and is not a draw |

`confirmatory` is declared in the seed map and is authorised for **no case** in this campaign.

**Enforcement.** `e1a_v4.validation.seeds.CaseSeedAccess, reached via ExecutionBinding.case_access / runner.case_seed_access`. A case may obtain **only** the families its frozen plan
entry declares in `allowed_seed_families`.

> **What the superseded check actually did.** `FrozenSeedMap.stream(consumer, requested)`
> compares the caller's two family arguments and nothing else. Passing the same family twice
> satisfies it, so **any** family was reachable for **any** case, and a C1 Branch-A seed was
> derivable. That was a specification requirement honoured by convention, **not** a mechanically
> enforced rule. The earlier pre-execution report described it as stronger than it was; this
> plan corrects the claim rather than restating it.

`family_seed` and `replicate_seed` remain importable and remain correct mathematics. **A
derivation is not an authorisation:** an official run reaches a family only through the
case-scoped boundary.

**Seed derivation is not a draw.** Deriving a seed constructs no generator and draws no number.
Seed derivation, RNG construction, random draw and trajectory generation stay separately
reported.

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

## 12. Author dispositions — CLOSED PROSPECTIVELY

All three gaps identified in the previous frozen package are now closed **before execution and
before any outcome was observed**. They complete missing *validation* rules; they do **not**
redesign the E1a bridge.

### G1 — affects `C8` — **CLOSED PROSPECTIVELY**

**Gap.** blinded scale control had no quantitative recovery criterion beyond beta = 1/c

**Resolution.** beta_tilde = c * beta_hat must satisfy the SAME P3 absolute-equivalence construction (delta_abs = 0.05, z_abs = 1.959963985) at EVERY tested field for BOTH c = 1.07 and c = 0.90; a replicate succeeds only if both branches pass. Campaign: one-sided 95% CP LOWER bound >= 0.90 over R = 200, i.e. >= 188/200.

### G2 — affects `C7` — **CLOSED PROSPECTIVELY**

**Gap.** false-bridge alternatives had no maximum acceptable acceptance rate

**Resolution.** maximum false-acceptance probability 0.025, tied to the equivalence test's one-sided nominal level at z = 1.959963985 and NOT derived from any observed outcome. Per alternative INDEPENDENTLY: one-sided 95% CP UPPER bound <= 0.025 over R = 400, i.e. <= 4/400. Counts are never pooled.

### G3 — affects `C1, C2, C3` — **CLOSED PROSPECTIVELY**

**Gap.** sigma_psi was recorded in the contract as 'to be declared'

**Resolution.** PRIMARY RELEASE SCENARIO sigma_psi = 0.5 degrees; the complete true-bridge >= 0.90 claim is asserted there. 0.0 and 0.2 degrees are secondary lower-uncertainty sensitivity cases; 1.0 degree is a stress/robustness case. All are reported, none is pooled into the primary result, and the stress case neither redefines the primary criterion nor is removed if it performs poorly.

### Superseded package

The previous frozen pre-execution package — work commit `475633c`, report commit
`b4b2575` — was **execution-blocked** by G1–G3 and is superseded
**prospectively** by this closure. neither commit is rewritten, amended or deleted; the historical report is retained as provenance.

---
## 12a. Size-validation semantics — FROZEN PROSPECTIVELY

### Why the inherited 3% rule was insufficient

The earlier frozen plan validated the geometry gates with a one-sided 95% Clopper–Pearson
**upper** bound ≤ 0.03. That is a **coarse gross-inflation tolerance** inherited from development
analysis, not validation of the nominal alpha allocations. At the declared nominal levels it would
have tolerated:

| case | tolerated | nominal alpha | ratio |
|---|---|---:|---:|
| C2 | 6/400 = 0.0150 | `alpha_geom = 0.005` | **3×** |
| C3 | 6/400 = 0.0150 | `alpha_2 = 0.001` | **15×** |
| C4 | 47/2000 = 0.0235 | `alpha_1 = 0.004` | **6×** |

**A rule that passes fifteen times the nominal rate cannot be called validation of it.** The 3%
criterion is superseded for release classification and retained only as a clearly labelled
secondary gross-inflation diagnostic. It is preserved in provenance, and commit `475633c` and
`docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md` are not rewritten.

### Two different questions, never merged

**Question A — complete practical performance.** C1, UNCHANGED. One-sided 95% Clopper-Pearson LOWER bound on complete-pipeline success >= 0.90 over R = 300, i.e. >= 279/300. This is the direct prospective validation of whether the whole implemented pipeline meets the release target.

**Question B — component size inflation.** C2, C3 and C4. At the feasible replicate counts these are NOT positive proofs that the achieved rate is at or below a tiny nominal alpha. They prospectively TEST FOR EVIDENCE OF INFLATION: H0: p <= nominal alpha vs H1: p > nominal alpha, one-sided 5%.

```
H0: p <= nominal alpha        H1: p > nominal alpha       one-sided 5%

STATISTICAL SIZE INFLATION is detected iff CP_lower(rejections, R) > nominal alpha
```

### Derived boundaries

Each is **recomputed** by `size_boundary(R, nominal)`, never copied.

| case | R | nominal alpha | no inflation detected | `STATISTICAL_SIZE_FAILURE` | CP_lower at boundary | CP_lower at boundary+1 |
|---|---:|---:|---|---|---:|---:|
| **C2** | 400 | `0.005` | 0–5 | 6+ | `0.0049379342` | `0.0065521458` |
| **C3** | 400 | `0.001` | 0–2 | 3+ | `0.0008891209` | `0.0020472587` |
| **C4** | 2000 | `0.004` | 0–13 | 14+ | `0.0038489425` | `0.0042367805` |

C2 is evaluated **per field and never pooled**. C4 **retains** its full two-sided interval and
operating-quantile discrepancy report; the binary diagnostic does not replace them.

### What a pass means

> **`NO_SIGNIFICANT_SIZE_INFLATION_DETECTED`** — this experiment did not establish excess size at the chosen confidence level.
> It does **not** mean that the achieved rate is mathematically proved to be at or below the nominal alpha.
> Forbidden wording: `NOMINAL SIZE PROVED`, `nominal size proved`, `size proved`, `exact size established`.

---

## 12b. Final campaign classification — FROZEN PROSPECTIVELY

A final **`VALIDATION_PASS`** requires **all** of the following. CONJUNCTIVE. Every required case must pass on its own terms. There is **no weighted score** and **no compensation** between cases.

1. C1 complete-pipeline success: CP lower >= 0.90 over R = 300 (>= 279/300)

2. C2 produces no STATISTICAL_SIZE_FAILURE in any required field

3. C3 produces no STATISTICAL_SIZE_FAILURE

4. C4 produces no STATISTICAL_SIZE_FAILURE

5. C5 satisfies its already-frozen plug-in Branch-A criterion

6. C6 satisfies its already-frozen mode-resolution criterion

7. EVERY C7 false-bridge alternative satisfies G2: CP upper <= 0.025 (<= 4/400)

8. C8 satisfies G1: CP lower >= 0.90 over R = 200 (>= 188/200)

9. no SOFTWARE_OR_INVARIANT_FAILURE, CALIBRATION_FAILURE, NUMERICAL_OR_PRECISION_FAILURE occurs

10. structured refusals counted exactly per the already-frozen unconditional denominator rule

> complete-pipeline achievement and component size cleanliness are REPORTED SEPARATELY and never collapsed. A campaign may fail because complete-pipeline success < target even with no significant size-inflation diagnostic: a valid scientific failure. Conversely C1 may reach >= 0.90 while a component case detects significant size inflation: also a validation failure, because the implemented calibration is not behaving according to its declared nominal structure. Both facts are reported.

Implemented by `e1a_v4.validation.classification.classify_campaign`.

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


---

## 14. Pre-execution repair — SUPERSESSION RECORD

**Status.** PRE-EXECUTION SOFTWARE AND SPECIFICATION REPAIR. No stochastic evidence existed, so nothing scientific is retracted.

**Trigger.** independent audit of the frozen validation package

| finding | reproduced defect | repair |
|---|---|---|
| **B1** | calibration identity incomplete: an artifact for theta0_circular was accepted for theta1_power; field_id never compared; the temporal-correlation law never bound | complete `CalibrationCondition`, artifact schema `e1a_v4_block1_calibration/2`, `field_id` validated as provenance — section 5.1 |
| **B2** | Block-1 threshold computation was O(R_cal^2) and was repeated on every P1 evaluation instead of computed once | exact rank identity, `O(R log R)`, finalised once on the artifact — section 5.2 |
| **B3** | seed-family enforcement was a symmetry check on the caller's own arguments, not a case-level permission check; a C1 Branch-A seed was derivable | `CaseSeedAccess`, machine-readable `allowed_seed_families` per case — section 7.1 |

**Scientific rules changed: NONE.** `delta_cross`, `delta_abs`,
`z_cross`, `z_abs`, `alpha_geom`, `alpha_1`, `alpha_2`, `theta_cap`, `rank_tol`, primary
`sigma_psi`, the complete-pipeline target, every replicate count, the G1/G2 criteria, the G3
disposition, the C2/C3/C4 size semantics, the false-bridge alternatives, the seed-derivation
algorithm, the complete-pass denominator and the final campaign conjunction are all untouched.

### Superseded, not erased

The package previously described as ready for execution is **SUPERSEDED BEFORE EXECUTION**.
Nothing is rewritten. Preserved in full:

- `docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md`
- `docs/e1a/E1A_V4_VALIDATION_DISPOSITION_REPORT.md`
- `docs/e1a/E1A_V4_SIZE_VALIDATION_REPORT.md`
- `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md`
- `docs/e1a/e1a_v4_execution_feasibility_probe.py`

### Runtime accounting correction

Supersedes the runtime figures in `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md`, which is **not rewritten**:

- '192 core-days' and '13.7 days at 14-way parallelism' were BENCHMARK-BASED PROJECTIONS resting on a quadratic extrapolation and an assumed artifact count, not MEASURED end-to-end runtimes
- '~415 s per artifact at R_cal = 50000' was a PROJECTION extrapolated from measurements at R = 500, 1000 and 2000
- 'four locked artifacts cost about 28 minutes' was likewise a PROJECTION
- the word 'infeasible' overstated the evidence: no explicit resource ceiling was part of the study. The supported statement is 'very expensive under the previous implementation'

Every runtime figure must now carry one of: **MEASURED BENCHMARK**, **BENCHMARK-BASED
PROJECTION**, **PARALLELISM ASSUMPTION**, **NOT MEASURED END-TO-END**.

**MEASURED BENCHMARK** — macOS-26.6.1-arm64, CPython 3.14.2, 14 CPUs, pure Python
(numpy and scipy are absent). Deterministic van der Corput arrays; no RNG.

| R | p_min_null, superseded `O(R^2)` | repaired finalisation | speedup | exact match |
|---:|---:|---:|---:|:--:|
| 1 000 | 0.1585 s | 0.0014 s | 113x | yes |
| 10 000 | 17.8104 s | 0.0179 s | 995x | yes |
| 50 000 | **415.5725 s** | **0.4543 s** | **915x** | yes |

Generate + finalise one artifact at `R_cal = 50000`: **3.008 s** wall, 2.792 s CPU.
One P1 use: **1.94 us**. One compatibility check: **22.99 us**, constant in `R`.

> The earlier report projected 415.0 s for the superseded threshold at `R_cal = 50000`.
> The measured value is **415.5725 s**. The projection was accurate — but it was a
> projection, and it was reported as though it were a measurement.

**BENCHMARK-BASED PROJECTION** — 40 000 field-replicates, hence 40 000 P1 evaluations:

| | artifact builds | repaired | superseded |
|---|---:|---:|---:|
| four locked artifacts | 4 | **13 s** | ~28 min |
| one artifact per field-replicate | 40 000 | **33.4 core-hours** | **193.6 core-days** |

**PARALLELISM ASSUMPTION** — "2.4 hours at 14-way" assumes 14 workers, perfect scaling,
no I/O and no scheduling overhead.

**NOT MEASURED END-TO-END** — no campaign, calibration or trajectory has been run.
Branch-B trajectory generation is excluded from every figure above and is the larger
term under either architecture.

### Still open, and NOT decided by this repair

whether the campaign calibrates ONE artifact per field or one per replicate at that replicate's measured H_A remains a SPECIFICATION decision, recorded in docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_RESULTS.md. This repair makes either choice mechanically safe and affordable; it does not decide it.

---

```
execution_authorised = false
RANDOM DRAWS = 0   TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN   VALIDATION CAMPAIGN = NOT RUN
```
