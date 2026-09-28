# E1a v4 — SYNTHETIC VALIDATION PLAN

**PRE-EXECUTION FROZEN PACKAGE, REPAIRED. NOTHING IN THIS PLAN HAS BEEN EXECUTED.**

Plan version **1.9.0**. Calibration scope frozen as **`REPLICATE_CONDITIONAL`** for the six
cases that evaluate a P1 / Block-1 quantity — section 5.3. Declared subconditions are
independently random by default — section 7.2. An independent audit found three pre-execution defects in the
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
| analysis procedure identity | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` |
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
The **execution procedure identity** binds the analysis identity plus the 12 validation module
hashes, this plan's JSON, **this Markdown** and the seed map. It is derived at preflight rather
than embedded here, because embedding it in a file whose hash it covers would be
self-referential; the expected value is asserted **externally** by
`docs/e1a/e1a_v4_execution_seal.json`, which is excluded from the preimage. See section 13a.

> **The normative Markdown joined the preimage in version 1.7.0.** This document is normative
> authority, not commentary. Leaving it outside the sealed package meant a stale Markdown moved
> nothing and preflight reported PASS — which is exactly what happened, for four commits. It is
> now hashed into the execution identity **and** checked field-by-field against the JSON.

### Frozen execution versus general implementation

A **general** analysis reads whatever valid contract it is given — that is correct architecture
and prevents magic numbers in code. An **official validation run** may not: `bind_execution`
requires the exact adopted contract identity and refuses anything else **before an RNG can be
created**. Both behaviours are tested.

---

## 1a. Machine-readable authority block

`AGENTS.md` fixes the rule for every normative Markdown/JSON pair in this repository: **the
JSON is the mechanical schema and ordering source, this Markdown is its normative human
rendering, and any mismatch is an integrity failure, not permission to choose one
selectively.**

The superseded preflight compared only the section-9 output schema, so everything else a
reader relies on was unchecked. The block below closes that. It is **generated** from
`docs/e1a/e1a_v4_synthetic_validation_plan.json` by
`e1a_v4.validation.coherence.render_authority_block` and rebuilt and compared key-by-key at
every preflight, **before any RNG object can exist**. Do not hand-edit it; regenerate it.

A generated block alone would not have caught the defect it exists for — the *human* tables
could still drift from the block. So preflight additionally verifies that the human-visible
renderings agree with it: the version line above, every row of the section-1 identity table,
the execution-authorisation sentence in section 13, and the `role`, `replicate count`,
`subconditions (n)`, `requires Block-1 calibration`, `calibration scope`,
`allowed seed families` and `primary release endpoint` rows of **every** case table in
section 3. Extraction is anchored on exact row labels inside named sections; an absent or
ambiguous match is a **refusal**, never a silent skip. Free prose is never compared.

<!-- BEGIN GENERATED AUTHORITY BLOCK -- do not hand-edit -->

```json
{
  "field_count": 489,
  "fields": {
    "adopted_rules.P3_applies_to": "EVERY tested field",
    "adopted_rules.P4_classification": "DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK",
    "adopted_rules.alpha_1": 0.004,
    "adopted_rules.alpha_2": 0.001,
    "adopted_rules.alpha_geom": 0.005,
    "adopted_rules.delta_abs": 0.05,
    "adopted_rules.delta_cross": 0.02,
    "adopted_rules.forbidden": [
      "Bonferroni correction",
      "fixed-B0 normalisation",
      "power-spectrum / corner-frequency / equipartition Branch-A calibration"
    ],
    "adopted_rules.multiplicity_correction": "NONE - intersection-union test",
    "adopted_rules.pipeline_target": 0.9,
    "adopted_rules.rank_tol": 1e-12,
    "adopted_rules.theta_cap_deg": 5.0,
    "adopted_rules.z_abs": 1.959963985,
    "adopted_rules.z_cross": 1.959963985,
    "assurance.0.acceptance_rule": ">= 279 / 300 complete passes",
    "assurance.0.bound": "Clopper-Pearson one-sided LOWER",
    "assurance.0.confidence_level": 0.95,
    "assurance.0.estimator": "complete-pass proportion over declared replicates",
    "assurance.0.quantity": "complete true-bridge pipeline success",
    "assurance.0.replicates": 300,
    "assurance.0.target": ">= 0.90",
    "assurance.1.acceptance_rule": "no inflation detected: CP_lower <= 0.005, i.e. <= 5/400, per field",
    "assurance.1.bound": "Clopper-Pearson one-sided LOWER (inflation test)",
    "assurance.1.confidence_level": 0.95,
    "assurance.1.estimator": "rejection proportion",
    "assurance.1.quantity": "P1 false-rejection rate, per field",
    "assurance.1.replicates": 400,
    "assurance.1.target": "alpha_geom = 0.005",
    "assurance.2.acceptance_rule": "no inflation detected: CP_lower <= 0.001, i.e. <= 2/400",
    "assurance.2.bound": "Clopper-Pearson one-sided LOWER (inflation test)",
    "assurance.2.confidence_level": 0.95,
    "assurance.2.estimator": "rejection proportion",
    "assurance.2.quantity": "block-2 (G5) rejection rate",
    "assurance.2.replicates": 400,
    "assurance.2.target": "alpha_2 = 0.001",
    "assurance.3.acceptance_rule": "discrepancy REPORTED and classified; additionally no inflation detected: CP_lower <= 0.004, i.e. <= 13/2000",
    "assurance.3.bound": "Clopper-Pearson two-sided (reported) + one-sided LOWER (inflation test)",
    "assurance.3.confidence_level": 0.95,
    "assurance.3.estimator": "rejection proportion",
    "assurance.3.quantity": "Block-1 achieved size under the surrogate",
    "assurance.3.replicates": 2000,
    "assurance.3.target": "alpha_1 = 0.004",
    "assurance.4.acceptance_rule": "upper bound <= 0.025, i.e. <= 4 / 400, evaluated per alternative independently",
    "assurance.4.bound": "Clopper-Pearson one-sided UPPER",
    "assurance.4.confidence_level": 0.95,
    "assurance.4.estimator": "acceptance proportion",
    "assurance.4.quantity": "false-bridge acceptance, per alternative",
    "assurance.4.replicates": 400,
    "assurance.4.target": "<= 0.025 per alternative",
    "assurance.5.acceptance_rule": ">= 188 / 200 paired-control successes",
    "assurance.5.bound": "Clopper-Pearson one-sided LOWER",
    "assurance.5.confidence_level": 0.95,
    "assurance.5.estimator": "distribution of beta_hat * c",
    "assurance.5.quantity": "blinded scale recovery beta_hat * c",
    "assurance.5.replicates": 200,
    "assurance.5.target": ">= 0.90 paired-control success",
    "authority_gaps.G1.affects": "C8",
    "authority_gaps.G1.gap": "blinded scale control had no quantitative recovery criterion beyond beta = 1/c",
    "authority_gaps.G1.resolution": "beta_tilde = c * beta_hat must satisfy the SAME P3 absolute-equivalence construction (delta_abs = 0.05, z_abs = 1.959963985) at EVERY tested field for BOTH c = 1.07 and c = 0.90; a replicate succeeds only if both branches pass. Campaign: one-sided 95% CP LOWER bound >= 0.90 over R = 200, i.e. >= 188/200.",
    "authority_gaps.G1.status": "CLOSED PROSPECTIVELY",
    "authority_gaps.G2.affects": "C7",
    "authority_gaps.G2.gap": "false-bridge alternatives had no maximum acceptable acceptance rate",
    "authority_gaps.G2.resolution": "maximum false-acceptance probability 0.025, tied to the equivalence test's one-sided nominal level at z = 1.959963985 and NOT derived from any observed outcome. Per alternative INDEPENDENTLY: one-sided 95% CP UPPER bound <= 0.025 over R = 400, i.e. <= 4/400. Counts are never pooled.",
    "authority_gaps.G2.status": "CLOSED PROSPECTIVELY",
    "authority_gaps.G3.affects": "C1, C2, C3",
    "authority_gaps.G3.gap": "sigma_psi was recorded in the contract as 'to be declared'",
    "authority_gaps.G3.resolution": "PRIMARY RELEASE SCENARIO sigma_psi = 0.5 degrees; the complete true-bridge >= 0.90 claim is asserted there. 0.0 and 0.2 degrees are secondary lower-uncertainty sensitivity cases; 1.0 degree is a stress/robustness case. All are reported, none is pooled into the primary result, and the stress case neither redefines the primary criterion nor is removed if it performs poorly.",
    "authority_gaps.G3.status": "CLOSED PROSPECTIVELY",
    "calibration.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C1_true_bridge_complete.allowed_seed_families": [
      "calibration",
      "validation",
      "branch_a_measurement"
    ],
    "cases.C1_true_bridge_complete.authority": "design section 15 items 4 and 10; contract complete_pipeline.target_true_bridge_success",
    "cases.C1_true_bridge_complete.beta_truth": 1.0,
    "cases.C1_true_bridge_complete.block1_role": "PRIMARY_RELEASE_ENDPOINT",
    "cases.C1_true_bridge_complete.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3]",
    "cases.C1_true_bridge_complete.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C1_true_bridge_complete.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C1_true_bridge_complete.calibration_artifact_basis": "300 replicates x 4 subconditions x 4 fields requiring calibration = 4,800",
    "cases.C1_true_bridge_complete.calibration_artifact_count": 4800,
    "cases.C1_true_bridge_complete.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C1_true_bridge_complete.expected_qualitative_outcome": "complete pass in the large majority of replicates",
    "cases.C1_true_bridge_complete.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C1_true_bridge_complete.fields_requiring_calibration": 4,
    "cases.C1_true_bridge_complete.formal_pass_fail_criterion": "Clopper-Pearson one-sided 95% LOWER bound on the complete-pass rate >= 0.90; requires >= 279/300. An observed proportion above 0.90 is NOT sufficient by itself.",
    "cases.C1_true_bridge_complete.geometry_truth": "as declared per field",
    "cases.C1_true_bridge_complete.primary_release_endpoint": "COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4",
    "cases.C1_true_bridge_complete.replicate_count": 300,
    "cases.C1_true_bridge_complete.requires_block1_calibration": true,
    "cases.C1_true_bridge_complete.role": "primary",
    "cases.C1_true_bridge_complete.scientific_purpose": "Does the implemented COMPLETE pipeline (P1 AND P2 AND P3 AND P4) achieve the adopted >= 0.90 target?",
    "cases.C1_true_bridge_complete.seed_family": "validation",
    "cases.C1_true_bridge_complete.subcondition_count": 4,
    "cases.C1_true_bridge_complete.subconditions.order": [
      "sigma_psi_0p0",
      "sigma_psi_0p2",
      "sigma_psi_0p5",
      "sigma_psi_1p0"
    ],
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p0.feeds_primary_claim": false,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p0.g3_role": "SECONDARY",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p0.sigma_psi_deg": 0.0,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p0.subcondition_id": "sigma_psi_0p0",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p2.feeds_primary_claim": false,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p2.g3_role": "SECONDARY",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p2.sigma_psi_deg": 0.2,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p2.subcondition_id": "sigma_psi_0p2",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.feeds_primary_claim": true,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.g3_role": "PRIMARY",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.sigma_psi_deg": 0.5,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_0p5.subcondition_id": "sigma_psi_0p5",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_1p0.feeds_primary_claim": false,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_1p0.g3_role": "STRESS",
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_1p0.sigma_psi_deg": 1.0,
    "cases.C1_true_bridge_complete.subconditions.sigma_psi_1p0.subcondition_id": "sigma_psi_1p0",
    "cases.C1_true_bridge_complete.truth_model": "K_theta = H_theta with beta_true = 1 at every field",
    "cases.C1_true_bridge_complete.uses_p1_block1": true,
    "cases.C1_true_bridge_complete.v4_classification": "NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION",
    "cases.C1_true_bridge_complete.v4_classification_note": "",
    "cases.C2_geometry_false_rejection.allowed_seed_families": [
      "calibration",
      "validation",
      "branch_a_measurement"
    ],
    "cases.C2_geometry_false_rejection.authority": "design section 15 item 3",
    "cases.C2_geometry_false_rejection.beta_truth": 1.0,
    "cases.C2_geometry_false_rejection.block1_role": "PRIMARY_RELEASE_ENDPOINT",
    "cases.C2_geometry_false_rejection.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3]",
    "cases.C2_geometry_false_rejection.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C2_geometry_false_rejection.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C2_geometry_false_rejection.calibration_artifact_basis": "400 replicates x 4 subconditions x 4 fields requiring calibration = 6,400",
    "cases.C2_geometry_false_rejection.calibration_artifact_count": 6400,
    "cases.C2_geometry_false_rejection.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C2_geometry_false_rejection.expected_qualitative_outcome": "false rejection at or below alpha_geom = 0.5%",
    "cases.C2_geometry_false_rejection.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C2_geometry_false_rejection.fields_requiring_calibration": 4,
    "cases.C2_geometry_false_rejection.formal_pass_fail_criterion": "PER FIELD, never pooled, R = 400, nominal alpha_geom = 0.005. Inflation is detected iff CP_lower(rejections, 400) > 0.005, i.e. 6 or more rejections -> STATISTICAL_SIZE_FAILURE. 0-5 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED, which means this experiment did not establish excess size, NOT that nominal size is proved. Secondary gross-inflation diagnostic (CP upper <= 0.03) may be reported but is not validation of alpha_geom.",
    "cases.C2_geometry_false_rejection.geometry_truth": "as declared per field",
    "cases.C2_geometry_false_rejection.primary_release_endpoint": "P1_FALSE_REJECTION_RATE_PER_FIELD",
    "cases.C2_geometry_false_rejection.replicate_count": 400,
    "cases.C2_geometry_false_rejection.requires_block1_calibration": true,
    "cases.C2_geometry_false_rejection.role": "primary",
    "cases.C2_geometry_false_rejection.scientific_purpose": "Achieved P1 false-rejection rate per declared field, covering G1-G5, the two-block combination, mode resolution and structured refusals",
    "cases.C2_geometry_false_rejection.seed_family": "validation",
    "cases.C2_geometry_false_rejection.subcondition_count": 4,
    "cases.C2_geometry_false_rejection.subconditions.order": [
      "sigma_psi_0p0",
      "sigma_psi_0p2",
      "sigma_psi_0p5",
      "sigma_psi_1p0"
    ],
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p0.feeds_primary_claim": false,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p0.g3_role": "SECONDARY",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p0.sigma_psi_deg": 0.0,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p0.subcondition_id": "sigma_psi_0p0",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p2.feeds_primary_claim": false,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p2.g3_role": "SECONDARY",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p2.sigma_psi_deg": 0.2,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p2.subcondition_id": "sigma_psi_0p2",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p5.feeds_primary_claim": true,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p5.g3_role": "PRIMARY",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p5.sigma_psi_deg": 0.5,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_0p5.subcondition_id": "sigma_psi_0p5",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_1p0.feeds_primary_claim": false,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_1p0.g3_role": "STRESS",
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_1p0.sigma_psi_deg": 1.0,
    "cases.C2_geometry_false_rejection.subconditions.sigma_psi_1p0.subcondition_id": "sigma_psi_1p0",
    "cases.C2_geometry_false_rejection.truth_model": "true null K_theta = H_theta",
    "cases.C2_geometry_false_rejection.uses_p1_block1": true,
    "cases.C2_geometry_false_rejection.v4_classification": "RETAINED BUT UPDATED FOR V4",
    "cases.C2_geometry_false_rejection.v4_classification_note": "alpha_geom 1% -> 0.5%, two-block union rule",
    "cases.C3_g5_block.allowed_seed_families": [
      "calibration",
      "validation",
      "branch_a_measurement"
    ],
    "cases.C3_g5_block.authority": "design section 15 item 8",
    "cases.C3_g5_block.beta_truth": 1.0,
    "cases.C3_g5_block.block1_role": "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC",
    "cases.C3_g5_block.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3]",
    "cases.C3_g5_block.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C3_g5_block.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C3_g5_block.c3_semantics": {
      "block1_role": "SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC",
      "joint_p1_result_changes_C3_release_verdict": false,
      "primary_release_endpoint": "G5_BLOCK_SIZE",
      "release_criterion": "UNCHANGED: R = 400, nominal alpha_2 = 0.001, CP_lower(G5 rejections, 400) > 0.001 detects inflation; 0-2 clean, 3+ STATISTICAL_SIZE_FAILURE",
      "requires_block1_calibration": true,
      "status": "AMBIGUITY RESOLVED PROSPECTIVELY, before any random outcome exists",
      "what_is_forbidden": "adding any new C3 release threshold based on Block 1 or on the joint P1 result. The release verdict depends only on the already-frozen Block-2 / G5 size criterion.",
      "why_calibration_is_retained": "the frozen scientific purpose requires reporting the two-mode max statistic's INTERACTION WITH THE TWO-BLOCK GATE. That interaction is a P1 quantity and needs a CalibrationArtifact, so calibration is retained as a diagnostic input."
    },
    "cases.C3_g5_block.calibration_artifact_basis": "400 replicates x 4 subconditions x 4 fields requiring calibration = 6,400",
    "cases.C3_g5_block.calibration_artifact_count": 6400,
    "cases.C3_g5_block.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C3_g5_block.expected_qualitative_outcome": "block-2 achieved size consistent with alpha_2 = 0.1%; delta-method error quantified",
    "cases.C3_g5_block.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C3_g5_block.fields_requiring_calibration": 4,
    "cases.C3_g5_block.formal_pass_fail_criterion": "R = 400, nominal alpha_2 = 0.001. Inflation is detected iff CP_lower(G5 rejections, 400) > 0.001, i.e. 3 or more -> STATISTICAL_SIZE_FAILURE. 0-2 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED. Also report the measured sd(g2) against the leading-order 24 A4 / n prediction.",
    "cases.C3_g5_block.geometry_truth": "as declared per field",
    "cases.C3_g5_block.primary_release_endpoint": "G5_BLOCK_SIZE",
    "cases.C3_g5_block.replicate_count": 400,
    "cases.C3_g5_block.requires_block1_calibration": true,
    "cases.C3_g5_block.role": "primary",
    "cases.C3_g5_block.scientific_purpose": "Validate the actual G5 block from full generated observations: sample-mean centring, A4-based leading-order variance, finite-sample behaviour, correlation, the two-mode max statistic and its interaction with the two-block gate",
    "cases.C3_g5_block.seed_family": "validation",
    "cases.C3_g5_block.subcondition_count": 4,
    "cases.C3_g5_block.subconditions.order": [
      "sigma_psi_0p0",
      "sigma_psi_0p2",
      "sigma_psi_0p5",
      "sigma_psi_1p0"
    ],
    "cases.C3_g5_block.subconditions.sigma_psi_0p0.feeds_primary_claim": false,
    "cases.C3_g5_block.subconditions.sigma_psi_0p0.g3_role": "SECONDARY",
    "cases.C3_g5_block.subconditions.sigma_psi_0p0.sigma_psi_deg": 0.0,
    "cases.C3_g5_block.subconditions.sigma_psi_0p0.subcondition_id": "sigma_psi_0p0",
    "cases.C3_g5_block.subconditions.sigma_psi_0p2.feeds_primary_claim": false,
    "cases.C3_g5_block.subconditions.sigma_psi_0p2.g3_role": "SECONDARY",
    "cases.C3_g5_block.subconditions.sigma_psi_0p2.sigma_psi_deg": 0.2,
    "cases.C3_g5_block.subconditions.sigma_psi_0p2.subcondition_id": "sigma_psi_0p2",
    "cases.C3_g5_block.subconditions.sigma_psi_0p5.feeds_primary_claim": true,
    "cases.C3_g5_block.subconditions.sigma_psi_0p5.g3_role": "PRIMARY",
    "cases.C3_g5_block.subconditions.sigma_psi_0p5.sigma_psi_deg": 0.5,
    "cases.C3_g5_block.subconditions.sigma_psi_0p5.subcondition_id": "sigma_psi_0p5",
    "cases.C3_g5_block.subconditions.sigma_psi_1p0.feeds_primary_claim": false,
    "cases.C3_g5_block.subconditions.sigma_psi_1p0.g3_role": "STRESS",
    "cases.C3_g5_block.subconditions.sigma_psi_1p0.sigma_psi_deg": 1.0,
    "cases.C3_g5_block.subconditions.sigma_psi_1p0.subcondition_id": "sigma_psi_1p0",
    "cases.C3_g5_block.truth_model": "true null; G5 computed from generated trajectories, never as an independent companion variable",
    "cases.C3_g5_block.uses_p1_block1": true,
    "cases.C3_g5_block.v4_classification": "NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION",
    "cases.C3_g5_block.v4_classification_note": "",
    "cases.C4_surrogate_validity.allowed_seed_families": [
      "calibration",
      "validation",
      "branch_a_measurement"
    ],
    "cases.C4_surrogate_validity.authority": "design section 15 item 5; design Appendix classification of the surrogate as an APPROXIMATION",
    "cases.C4_surrogate_validity.beta_truth": 1.0,
    "cases.C4_surrogate_validity.block1_role": "PRIMARY_RELEASE_ENDPOINT",
    "cases.C4_surrogate_validity.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K",
    "cases.C4_surrogate_validity.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C4_surrogate_validity.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C4_surrogate_validity.calibration_artifact_basis": "2000 replicates x 1 subconditions x 4 fields requiring calibration = 8,000",
    "cases.C4_surrogate_validity.calibration_artifact_count": 8000,
    "cases.C4_surrogate_validity.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C4_surrogate_validity.expected_qualitative_outcome": "achieved Block-1 rejection rate close to alpha_1 = 0.4%",
    "cases.C4_surrogate_validity.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C4_surrogate_validity.fields_requiring_calibration": 4,
    "cases.C4_surrogate_validity.formal_pass_fail_criterion": "R = 2000, nominal alpha_1 = 0.004. RETAIN the full two-sided interval and the observed operating-quantile discrepancy. IN ADDITION, classify inflation: detected iff CP_lower(rejections, 2000) > 0.004, i.e. 14 or more -> STATISTICAL_SIZE_FAILURE; 0-13 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED. The binary diagnostic does not replace the discrepancy report.",
    "cases.C4_surrogate_validity.geometry_truth": "as declared per field",
    "cases.C4_surrogate_validity.primary_release_endpoint": "BLOCK1_ACHIEVED_SIZE",
    "cases.C4_surrogate_validity.replicate_count": 2000,
    "cases.C4_surrogate_validity.requires_block1_calibration": true,
    "cases.C4_surrogate_validity.role": "primary",
    "cases.C4_surrogate_validity.scientific_purpose": "Achieved Block-1 size when calibration uses the covariance-matched surrogate but validation data come from the declared actual correlated process; measure the OPERATING-QUANTILE discrepancy, not covariance agreement",
    "cases.C4_surrogate_validity.seed_family": "calibration + validation",
    "cases.C4_surrogate_validity.subcondition_count": 1,
    "cases.C4_surrogate_validity.subconditions.order": [
      "primary"
    ],
    "cases.C4_surrogate_validity.subconditions.primary.subcondition_id": "primary",
    "cases.C4_surrogate_validity.truth_model": "calibration from the surrogate, validation from the declared OU process",
    "cases.C4_surrogate_validity.uses_p1_block1": true,
    "cases.C4_surrogate_validity.v4_classification": "NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION",
    "cases.C4_surrogate_validity.v4_classification_note": "",
    "cases.C5_plug_in_branch_a.allowed_seed_families": [
      "calibration",
      "validation",
      "branch_a_measurement"
    ],
    "cases.C5_plug_in_branch_a.authority": "design section 15 item 6",
    "cases.C5_plug_in_branch_a.beta_truth": 1.0,
    "cases.C5_plug_in_branch_a.block1_role": "PRIMARY_RELEASE_ENDPOINT",
    "cases.C5_plug_in_branch_a.branch_a_uncertainty": "swept: sigma_k in {0, 0.5%, 1%} x sigma_psi in {0, 0.2, 0.5, 1.0} degrees, 12 cells",
    "cases.C5_plug_in_branch_a.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C5_plug_in_branch_a.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C5_plug_in_branch_a.calibration_artifact_basis": "400 replicates x 12 subconditions x 4 fields requiring calibration = 19,200",
    "cases.C5_plug_in_branch_a.calibration_artifact_count": 19200,
    "cases.C5_plug_in_branch_a.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C5_plug_in_branch_a.expected_qualitative_outcome": "achieved size degrades as sigma_psi grows; the magnitude is the result",
    "cases.C5_plug_in_branch_a.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C5_plug_in_branch_a.fields_requiring_calibration": 4,
    "cases.C5_plug_in_branch_a.formal_pass_fail_criterion": "report the Clopper-Pearson one-sided 95% UPPER bound on the P1 rejection rate in EVERY one of the 12 declared cells, R = 400 each. No cell may be dropped after inspection.",
    "cases.C5_plug_in_branch_a.geometry_truth": "as declared per field",
    "cases.C5_plug_in_branch_a.primary_release_endpoint": "P1_REJECTION_RATE_PER_CELL",
    "cases.C5_plug_in_branch_a.replicate_count": 400,
    "cases.C5_plug_in_branch_a.requires_block1_calibration": true,
    "cases.C5_plug_in_branch_a.role": "primary",
    "cases.C5_plug_in_branch_a.scientific_purpose": "Effect of analysing with measured/noisy H_A and tau_A while truth is generated from H_true and tau_true, including shape and orientation uncertainty",
    "cases.C5_plug_in_branch_a.seed_family": "validation + branch_a_measurement",
    "cases.C5_plug_in_branch_a.subcondition_count": 12,
    "cases.C5_plug_in_branch_a.subconditions.order": [
      "sk0p00_sp0p0",
      "sk0p00_sp0p2",
      "sk0p00_sp0p5",
      "sk0p00_sp1p0",
      "sk0p50_sp0p0",
      "sk0p50_sp0p2",
      "sk0p50_sp0p5",
      "sk0p50_sp1p0",
      "sk1p00_sp0p0",
      "sk1p00_sp0p2",
      "sk1p00_sp0p5",
      "sk1p00_sp1p0"
    ],
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p0.sigma_k": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p0.sigma_psi_deg": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p0.subcondition_id": "sk0p00_sp0p0",
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p2.sigma_k": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p2.sigma_psi_deg": 0.2,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p2.subcondition_id": "sk0p00_sp0p2",
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p5.sigma_k": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p5.sigma_psi_deg": 0.5,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp0p5.subcondition_id": "sk0p00_sp0p5",
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp1p0.sigma_k": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp1p0.sigma_psi_deg": 1.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p00_sp1p0.subcondition_id": "sk0p00_sp1p0",
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p0.sigma_k": 0.005,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p0.sigma_psi_deg": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p0.subcondition_id": "sk0p50_sp0p0",
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p2.sigma_k": 0.005,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p2.sigma_psi_deg": 0.2,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p2.subcondition_id": "sk0p50_sp0p2",
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p5.sigma_k": 0.005,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p5.sigma_psi_deg": 0.5,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp0p5.subcondition_id": "sk0p50_sp0p5",
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp1p0.sigma_k": 0.005,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp1p0.sigma_psi_deg": 1.0,
    "cases.C5_plug_in_branch_a.subconditions.sk0p50_sp1p0.subcondition_id": "sk0p50_sp1p0",
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p0.sigma_k": 0.01,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p0.sigma_psi_deg": 0.0,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p0.subcondition_id": "sk1p00_sp0p0",
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p2.sigma_k": 0.01,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p2.sigma_psi_deg": 0.2,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p2.subcondition_id": "sk1p00_sp0p2",
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p5.sigma_k": 0.01,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p5.sigma_psi_deg": 0.5,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp0p5.subcondition_id": "sk1p00_sp0p5",
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp1p0.sigma_k": 0.01,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp1p0.sigma_psi_deg": 1.0,
    "cases.C5_plug_in_branch_a.subconditions.sk1p00_sp1p0.subcondition_id": "sk1p00_sp1p0",
    "cases.C5_plug_in_branch_a.truth_model": "true null; analysis receives only the Branch-A measured field",
    "cases.C5_plug_in_branch_a.uses_p1_block1": true,
    "cases.C5_plug_in_branch_a.v4_classification": "NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION",
    "cases.C5_plug_in_branch_a.v4_classification_note": "",
    "cases.C6_mode_resolution_boundary.allowed_seed_families": [
      "calibration",
      "validation",
      "branch_a_measurement"
    ],
    "cases.C6_mode_resolution_boundary.authority": "design section 15 item 7; design section 10",
    "cases.C6_mode_resolution_boundary.beta_truth": 1.0,
    "cases.C6_mode_resolution_boundary.block1_role": "PRIMARY_RELEASE_ENDPOINT",
    "cases.C6_mode_resolution_boundary.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K",
    "cases.C6_mode_resolution_boundary.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C6_mode_resolution_boundary.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C6_mode_resolution_boundary.calibration_artifact_basis": "400 replicates x 3 subconditions x 1 fields requiring calibration = 1,200",
    "cases.C6_mode_resolution_boundary.calibration_artifact_count": 1200,
    "cases.C6_mode_resolution_boundary.calibration_scope": "REPLICATE_CONDITIONAL",
    "cases.C6_mode_resolution_boundary.expected_qualitative_outcome": "merge below the boundary, split above; size controlled on both sides",
    "cases.C6_mode_resolution_boundary.fields_affected": [
      "synthetic two-mode field at the declared rho"
    ],
    "cases.C6_mode_resolution_boundary.fields_requiring_calibration": 1,
    "cases.C6_mode_resolution_boundary.formal_pass_fail_criterion": "Clopper-Pearson one-sided 95% UPPER bound on the P1 rejection rate <= 3% at each of the three declared rho, R = 400 each; report the merge/split decision rate at each. theta_cap MUST NOT be changed after observing the result.",
    "cases.C6_mode_resolution_boundary.geometry_truth": "rho in {1.019573, 1.024467, 1.029360} at N_12 = 224726",
    "cases.C6_mode_resolution_boundary.primary_release_endpoint": "P1_REJECTION_RATE_PER_RHO",
    "cases.C6_mode_resolution_boundary.replicate_count": 400,
    "cases.C6_mode_resolution_boundary.requires_block1_calibration": true,
    "cases.C6_mode_resolution_boundary.role": "primary",
    "cases.C6_mode_resolution_boundary.scientific_purpose": "Size AND detection behaviour around theta_cap = 5 degrees at the predeclared boundary neighbourhood",
    "cases.C6_mode_resolution_boundary.seed_family": "validation",
    "cases.C6_mode_resolution_boundary.subcondition_count": 3,
    "cases.C6_mode_resolution_boundary.subconditions.order": [
      "rho_1p019573",
      "rho_1p024467",
      "rho_1p029360"
    ],
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p019573.rho": 1.019573,
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p019573.role": "boundary -20%",
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p019573.subcondition_id": "rho_1p019573",
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p024467.rho": 1.024467,
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p024467.role": "boundary",
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p024467.subcondition_id": "rho_1p024467",
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p029360.rho": 1.02936,
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p029360.role": "boundary +20%",
    "cases.C6_mode_resolution_boundary.subconditions.rho_1p029360.subcondition_id": "rho_1p029360",
    "cases.C6_mode_resolution_boundary.truth_model": "true null at rho = boundary, boundary -20%, boundary +20%",
    "cases.C6_mode_resolution_boundary.uses_p1_block1": true,
    "cases.C6_mode_resolution_boundary.v4_classification": "NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION",
    "cases.C6_mode_resolution_boundary.v4_classification_note": "",
    "cases.C7_false_bridge.allowed_seed_families": [
      "validation",
      "branch_a_measurement"
    ],
    "cases.C7_false_bridge.authority": "design section 13; contract false_bridge_controls",
    "cases.C7_false_bridge.beta_truth": "per alternative",
    "cases.C7_false_bridge.block1_role": "NONE",
    "cases.C7_false_bridge.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K",
    "cases.C7_false_bridge.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C7_false_bridge.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C7_false_bridge.calibration_artifact_basis": "0 - this case evaluates no P1 / Block-1 quantity",
    "cases.C7_false_bridge.calibration_artifact_count": 0,
    "cases.C7_false_bridge.calibration_not_required_reason": "its frozen endpoints do not evaluate any P1 / Block-1 quantity. p1_geometry is the ONLY consumer of a CalibrationArtifact in the package, and this case never reaches it. Generating one would add a calibration refusal path that cannot affect the science but CAN affect the outcome.",
    "cases.C7_false_bridge.calibration_scope": "NOT_APPLICABLE",
    "cases.C7_false_bridge.expected_qualitative_outcome": "acceptance close to zero for the coarse alternatives; the hard 2.5% case is the informative one",
    "cases.C7_false_bridge.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C7_false_bridge.fields_requiring_calibration": 0,
    "cases.C7_false_bridge.formal_pass_fail_criterion": "For EACH declared alternative INDEPENDENTLY: one-sided 95% Clopper-Pearson UPPER bound on the false-acceptance rate <= 0.025 over R = 400, i.e. <= 4/400; 5 or more fails. Counts are never pooled and easy and hard alternatives are never averaged. [disposition G2, closed prospectively]",
    "cases.C7_false_bridge.geometry_truth": "as declared per field",
    "cases.C7_false_bridge.primary_release_endpoint": "P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE",
    "cases.C7_false_bridge.replicate_count": 400,
    "cases.C7_false_bridge.requires_block1_calibration": false,
    "cases.C7_false_bridge.role": "negative_control",
    "cases.C7_false_bridge.scientific_purpose": "Probability of incorrectly ACCEPTING a false bridge, for every declared non-commensurable alternative including the hard near-margin case",
    "cases.C7_false_bridge.seed_family": "validation",
    "cases.C7_false_bridge.subcondition_count": 4,
    "cases.C7_false_bridge.subconditions.alt_0_93_1_05.beta_true": [
      1,
      0.93,
      1.05,
      1
    ],
    "cases.C7_false_bridge.subconditions.alt_0_93_1_05.subcondition_id": "alt_0_93_1_05",
    "cases.C7_false_bridge.subconditions.alt_1_06.beta_true": [
      1,
      1.06,
      1,
      1
    ],
    "cases.C7_false_bridge.subconditions.alt_1_06.subcondition_id": "alt_1_06",
    "cases.C7_false_bridge.subconditions.alt_1_10.beta_true": [
      1,
      1,
      1,
      1.1
    ],
    "cases.C7_false_bridge.subconditions.alt_1_10.subcondition_id": "alt_1_10",
    "cases.C7_false_bridge.subconditions.hard_1_025.beta_true": [
      1,
      1.025,
      1,
      1
    ],
    "cases.C7_false_bridge.subconditions.hard_1_025.role": "hard near-margin case",
    "cases.C7_false_bridge.subconditions.hard_1_025.subcondition_id": "hard_1_025",
    "cases.C7_false_bridge.subconditions.order": [
      "alt_1_06",
      "alt_0_93_1_05",
      "alt_1_10",
      "hard_1_025"
    ],
    "cases.C7_false_bridge.truth_model": "beta_theta = (1,1.06,1,1); (1,0.93,1.05,1); (1,1,1,1.10); hard (1,1.025,1,1)",
    "cases.C7_false_bridge.uses_p1_block1": false,
    "cases.C7_false_bridge.v4_classification": "RETAINED BUT UPDATED FOR V4",
    "cases.C7_false_bridge.v4_classification_note": "evaluated against the all-field P3 and the IUT P2",
    "cases.C8_blinded_scale_control.allowed_seed_families": [
      "blinded_scale_control",
      "branch_a_measurement"
    ],
    "cases.C8_blinded_scale_control.authority": "baseline section 14.2 (committed); design section 13",
    "cases.C8_blinded_scale_control.beta_truth": "1/c on the blinded branch",
    "cases.C8_blinded_scale_control.block1_role": "NONE",
    "cases.C8_blinded_scale_control.branch_a_uncertainty": "frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K",
    "cases.C8_blinded_scale_control.branch_a_uncertainty_status": "STOCHASTIC_PER_REPLICATE",
    "cases.C8_blinded_scale_control.branch_b_process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "cases.C8_blinded_scale_control.calibration_artifact_basis": "0 - this case evaluates no P1 / Block-1 quantity",
    "cases.C8_blinded_scale_control.calibration_artifact_count": 0,
    "cases.C8_blinded_scale_control.calibration_not_required_reason": "its frozen endpoints do not evaluate any P1 / Block-1 quantity. p1_geometry is the ONLY consumer of a CalibrationArtifact in the package, and this case never reaches it. Generating one would add a calibration refusal path that cannot affect the science but CAN affect the outcome.",
    "cases.C8_blinded_scale_control.calibration_scope": "NOT_APPLICABLE",
    "cases.C8_blinded_scale_control.expected_qualitative_outcome": "beta_hat on the blinded branch concentrates on 1/c",
    "cases.C8_blinded_scale_control.fields_affected": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "cases.C8_blinded_scale_control.fields_requiring_calibration": 0,
    "cases.C8_blinded_scale_control.formal_pass_fail_criterion": "beta_tilde_theta = c * beta_hat_theta must satisfy the SAME P3 absolute-equivalence rule (delta_abs = 0.05, z_abs = 1.959963985, h_theta = z sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2)) at EVERY tested field, for BOTH c = 1.07 and c = 0.90; any non-ESTIMATED field fails that branch. One replicate succeeds only if both branches pass. Campaign: one-sided 95% Clopper-Pearson LOWER bound on paired-control success >= 0.90 over R = 200, i.e. >= 188/200. [disposition G1, closed prospectively]",
    "cases.C8_blinded_scale_control.geometry_truth": "as declared per field",
    "cases.C8_blinded_scale_control.primary_release_endpoint": "P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY",
    "cases.C8_blinded_scale_control.replicate_count": 200,
    "cases.C8_blinded_scale_control.requires_block1_calibration": false,
    "cases.C8_blinded_scale_control.role": "positive_control",
    "cases.C8_blinded_scale_control.scientific_purpose": "Blinded duplicate-branch scale control: Branch-A declared scale multiplied by a hidden c, analysis must recover beta = 1/c",
    "cases.C8_blinded_scale_control.seed_family": "blinded_scale_control",
    "cases.C8_blinded_scale_control.subcondition_count": 1,
    "cases.C8_blinded_scale_control.subconditions.order": [
      "paired_scale_control"
    ],
    "cases.C8_blinded_scale_control.subconditions.paired_scale_control.pairing": "INTENTIONAL: both factors act on the SAME underlying synthetic replicate by the frozen deterministic Branch-A scale transform. They are NOT independent random subconditions and must not be given separate streams.",
    "cases.C8_blinded_scale_control.subconditions.paired_scale_control.scale_factors": [
      1.07,
      0.9
    ],
    "cases.C8_blinded_scale_control.subconditions.paired_scale_control.subcondition_id": "paired_scale_control",
    "cases.C8_blinded_scale_control.truth_model": "true null with the Branch-A scale multiplied by a hidden c on a DUPLICATE branch that never touches primary data",
    "cases.C8_blinded_scale_control.uses_p1_block1": false,
    "cases.C8_blinded_scale_control.v4_classification": "RETAINED UNCHANGED",
    "cases.C8_blinded_scale_control.v4_classification_note": "",
    "cases.order": [
      "C1_true_bridge_complete",
      "C2_geometry_false_rejection",
      "C3_g5_block",
      "C4_surrogate_validity",
      "C5_plug_in_branch_a",
      "C6_mode_resolution_boundary",
      "C7_false_bridge",
      "C8_blinded_scale_control"
    ],
    "controls.0.case": "C8",
    "controls.0.control": "blinded scale distortion",
    "controls.0.purpose": "scale-detection sensitivity",
    "controls.1.case": "C7",
    "controls.1.control": "geometry / coordinate permutation",
    "controls.1.purpose": "destroys the correlation structure; the geometry control",
    "controls.2.case": "C7",
    "controls.2.control": "false-beta alternatives",
    "controls.2.purpose": "false-bridge discrimination",
    "controls.3.case": "C7",
    "controls.3.control": "time shuffle",
    "controls.3.purpose": "AUTOCORRELATION control only, not a geometry control; leaves S identical to 1e-30",
    "controls.4.case": "C8",
    "controls.4.control": "paired hidden-scale distortion c = 1.07 / 0.90",
    "controls.4.purpose": "acts through P3/beta; gates are scale-invariant",
    "controls.5.case": "C7",
    "controls.5.control": "forbidden H := K",
    "controls.5.purpose": "recorded as vacuous; demonstration only",
    "driver.entry_point": "run_campaign",
    "driver.module": "e1a_v4.validation.campaign_driver",
    "driver.path": "e1a_v4/validation/campaign_driver.py",
    "execution_authorised": false,
    "execution_seal.state": "PRE_DRIVER",
    "execution_stage": "synthetic_validation",
    "failure_classifications": [
      "SOFTWARE_OR_INVARIANT_FAILURE",
      "CALIBRATION_FAILURE",
      "STATISTICAL_SIZE_FAILURE",
      "TRUE_BRIDGE_POWER_FAILURE",
      "FALSE_BRIDGE_DISCRIMINATION_FAILURE",
      "STRUCTURED_REFUSAL_EXCESS",
      "MODE_RESOLUTION_FAILURE",
      "BLINDED_SCALE_CONTROL_FAILURE",
      "NUMERICAL_OR_PRECISION_FAILURE",
      "VALIDATION_INCONCLUSIVE",
      "VALIDATION_PASS"
    ],
    "final_campaign.requirements.0": "1. C1 complete-pipeline success: CP lower >= 0.90 over R = 300 (>= 279/300)",
    "final_campaign.requirements.1": "2. C2 produces no STATISTICAL_SIZE_FAILURE in any required field",
    "final_campaign.requirements.2": "3. C3 produces no STATISTICAL_SIZE_FAILURE",
    "final_campaign.requirements.3": "4. C4 produces no STATISTICAL_SIZE_FAILURE",
    "final_campaign.requirements.4": "5. C5 satisfies its already-frozen plug-in Branch-A criterion",
    "final_campaign.requirements.5": "6. C6 satisfies its already-frozen mode-resolution criterion",
    "final_campaign.requirements.6": "7. EVERY C7 false-bridge alternative satisfies G2: CP upper <= 0.025 (<= 4/400)",
    "final_campaign.requirements.7": "8. C8 satisfies G1: CP lower >= 0.90 over R = 200 (>= 188/200)",
    "final_campaign.requirements.8": "9. no SOFTWARE_OR_INVARIANT_FAILURE, CALIBRATION_FAILURE, NUMERICAL_OR_PRECISION_FAILURE occurs",
    "final_campaign.requirements.9": "10. structured refusals counted exactly per the already-frozen unconditional denominator rule",
    "final_campaign.rule": "CONJUNCTIVE. Every required case must pass on its own terms.",
    "final_campaign.verdict_on_success": "VALIDATION_PASS",
    "frozen_identities.analysis_procedure_identity": "dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f",
    "frozen_identities.baseline_sha256": "0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa",
    "frozen_identities.calibration_artifact_schema": "e1a_v4_block1_calibration/2",
    "frozen_identities.contract_sha256": "91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b",
    "frozen_identities.contract_version": "1.1.0",
    "frozen_identities.design_sha256": "e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495",
    "frozen_identities.foundation_sha256": "6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507",
    "frozen_identities.implementation_file_hashes_digest": "787b8f5cef19a3eb7aa328282c421970cabbf9aae1060c4927bbdbd4476a6c5b",
    "frozen_identities.implementation_work_commit": "e4b73d7fbd84d329f4326af443fd1918bc44a874",
    "generating_model.branch_a.common_mode": "ONE draw per experiment, shared across every field, so it cancels in the P2 ratio and not in P3",
    "generating_model.branch_a.independence": "Branch-A measurement randomness is exogenous and never a function of the Branch-B trajectory",
    "generating_model.branch_a.model": "H_A = decorated H_true; its OWN seed family branch_a_measurement",
    "generating_model.branch_a.orientation": "trap-axis psi",
    "generating_model.branch_a.per_mode_stiffness": "independent per mode",
    "generating_model.branch_a.thermometry": "T measured with sigma_T",
    "generating_model.branch_b.T_total_s": 240.0,
    "generating_model.branch_b.dt_s": 0.00012,
    "generating_model.branch_b.initialisation": "x_0 ~ N(x*, Sigma_theta); stationary at step 0; burn_in_steps = 0",
    "generating_model.branch_b.n_samples": 2000000,
    "generating_model.branch_b.phi": "phi_r = exp(-dt / tau_r)",
    "generating_model.branch_b.process": "declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)",
    "generating_model.branch_b.superseded": "the v3 convention of starting at x = 0 is FORBIDDEN: it is not stationary",
    "generating_model.branch_b.transition": "x_{k+1} = phi_r x_k + sqrt(1 - phi_r^2) L z, per mode, EXACT",
    "generating_model.per_field.order": [
      "theta0_circular",
      "theta1_power",
      "theta2_ellipse",
      "theta3_temperature"
    ],
    "generating_model.per_field.theta0_circular.T_K": 298,
    "generating_model.per_field.theta0_circular.beta_true": 1.0,
    "generating_model.per_field.theta0_circular.k_uN_per_m": [
      100,
      100
    ],
    "generating_model.per_field.theta0_circular.reference": true,
    "generating_model.per_field.theta0_circular.rot_deg": 0,
    "generating_model.per_field.theta0_circular.tau_rule": "tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a",
    "generating_model.per_field.theta1_power.T_K": 298,
    "generating_model.per_field.theta1_power.beta_true": 1.0,
    "generating_model.per_field.theta1_power.k_uN_per_m": [
      210,
      210
    ],
    "generating_model.per_field.theta1_power.reference": false,
    "generating_model.per_field.theta1_power.rot_deg": 0,
    "generating_model.per_field.theta1_power.tau_rule": "tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a",
    "generating_model.per_field.theta2_ellipse.T_K": 298,
    "generating_model.per_field.theta2_ellipse.beta_true": 1.0,
    "generating_model.per_field.theta2_ellipse.k_uN_per_m": [
      150,
      60
    ],
    "generating_model.per_field.theta2_ellipse.reference": false,
    "generating_model.per_field.theta2_ellipse.rot_deg": 30,
    "generating_model.per_field.theta2_ellipse.tau_rule": "tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a",
    "generating_model.per_field.theta3_temperature.T_K": 318,
    "generating_model.per_field.theta3_temperature.beta_true": 1.0,
    "generating_model.per_field.theta3_temperature.k_uN_per_m": [
      100,
      100
    ],
    "generating_model.per_field.theta3_temperature.reference": false,
    "generating_model.per_field.theta3_temperature.rot_deg": 0,
    "generating_model.per_field.theta3_temperature.tau_rule": "tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a",
    "generating_model.truth_visibility": "H_true and tau_true are known to the SCORING layer only. The analysis pipeline receives only the Branch-A measured field, exactly as in the real experiment.",
    "output_schema.aggregate_fields": [
      "success_count",
      "failure_count",
      "refusal_count",
      "refusals_by_reason",
      "confidence_bound",
      "false_bridge_acceptance",
      "per_field_geometry_rates",
      "mode_resolution_behaviour",
      "g5_diagnostics",
      "scale_control_recovery",
      "classification"
    ],
    "output_schema.directory": "results/e1a_v4_validation",
    "output_schema.manifest_schema": "e1a_v4_validation_manifest/2",
    "output_schema.per_record_fields": [
      "case_id",
      "subcondition_id",
      "replicate_id",
      "seed_family",
      "seed_identity",
      "field_id",
      "truth_parameters",
      "branch_a_observed",
      "analysis_status",
      "G1",
      "G2",
      "G3",
      "G4",
      "G5",
      "P1",
      "beta_hat",
      "P2",
      "P3",
      "P4",
      "complete_pass",
      "refusal_reason",
      "procedure_identity",
      "contract_sha256",
      "plan_sha256",
      "implementation_commit"
    ],
    "output_schema.record_schema": "e1a_v4_validation_result/2",
    "plan_id": "e1a_v4_synthetic_validation",
    "plan_version": "1.9.0",
    "seed_map_sha256": "95870d7d33c256c4bd30118e13278a600271531fd945d12687a828de902e91ce"
  },
  "schema": "e1a_v4_plan_authority/2"
}
```

<!-- END GENERATED AUTHORITY BLOCK -->

---

## 2. Adopted rules, unchanged

These are the frozen scientific decision rules. The table and the forbidden list below are
**generated** from the JSON plan and verified byte-for-byte at every preflight.

<!-- BEGIN GENERATED ADOPTED RULES -- do not hand-edit -->

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
| `P3_applies_to` | `"EVERY tested field"` |
| `P4_classification` | `"DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK"` |
| `multiplicity_correction` | `"NONE - intersection-union test"` |

Forbidden and unchanged: **Bonferroni correction**; **fixed-B0 normalisation**; **power-spectrum / corner-frequency / equipartition Branch-A calibration**.

<!-- END GENERATED ADOPTED RULES -->

---

## 3. The eight cases

Eight cases, one per scientifically required purpose traceable to committed or adopted authority. P2 (cross-field) and P3 (absolute) are NOT separate generating cases: they are endpoints evaluated on C1's data so the shared reference-field dependence and the common-mode calibration error are preserved. Simulating the three P2 ratios independently, or reverting P3 to reference-only, would destroy exactly the structure being validated. The count is eight because eight purposes are required, not to preserve a historical number.

Every case section below is **generated** from the JSON plan, including each
subcondition's complete declared parameters. A subcondition parameter that is not
rendered here is not declared: `feeds_primary_claim`, `beta_true` and `scale_factors`
used to exist only in the JSON, so a reader could not see them drift.

<!-- BEGIN GENERATED CASES -- do not hand-edit -->

### `C1_true_bridge_complete` — primary

**Purpose.** Does the implemented COMPLETE pipeline (P1 AND P2 AND P3 AND P4) achieve the adopted >= 0.90 target?

| | |
|---|---|
| v4 classification | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION |
| v4 classification note |  |
| authority | design section 15 items 4 and 10; contract complete_pipeline.target_true_bridge_success |
| truth model | K_theta = H_theta with beta_true = 1 at every field |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3] |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | complete pass in the large majority of replicates |
| seed family | validation |
| allowed seed families | `"calibration"` `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `true` |
| requires Block-1 calibration | `true` |
| primary release endpoint | COMPLETE_PIPELINE_P1_AND_P2_AND_P3_AND_P4 |
| Block-1 role | PRIMARY_RELEASE_ENDPOINT |
| calibration scope | REPLICATE_CONDITIONAL |
| fields requiring calibration | `4` |
| calibration artifacts | `4800` |
| calibration artifact basis | 300 replicates x 4 subconditions x 4 fields requiring calibration = 4,800 |
| subcondition count | `4` |
| replicate count | `300` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `sigma_psi_0p0` | `{"feeds_primary_claim":false,"g3_role":"SECONDARY","sigma_psi_deg":0.0}` |
| `sigma_psi_0p2` | `{"feeds_primary_claim":false,"g3_role":"SECONDARY","sigma_psi_deg":0.2}` |
| `sigma_psi_0p5` | `{"feeds_primary_claim":true,"g3_role":"PRIMARY","sigma_psi_deg":0.5}` |
| `sigma_psi_1p0` | `{"feeds_primary_claim":false,"g3_role":"STRESS","sigma_psi_deg":1.0}` |

**Pass / fail criterion.** Clopper-Pearson one-sided 95% LOWER bound on the complete-pass rate >= 0.90; requires >= 279/300. An observed proportion above 0.90 is NOT sufficient by itself.

### `C2_geometry_false_rejection` — primary

**Purpose.** Achieved P1 false-rejection rate per declared field, covering G1-G5, the two-block combination, mode resolution and structured refusals

| | |
|---|---|
| v4 classification | RETAINED BUT UPDATED FOR V4 |
| v4 classification note | alpha_geom 1% -> 0.5%, two-block union rule |
| authority | design section 15 item 3 |
| truth model | true null K_theta = H_theta |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3] |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | false rejection at or below alpha_geom = 0.5% |
| seed family | validation |
| allowed seed families | `"calibration"` `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `true` |
| requires Block-1 calibration | `true` |
| primary release endpoint | P1_FALSE_REJECTION_RATE_PER_FIELD |
| Block-1 role | PRIMARY_RELEASE_ENDPOINT |
| calibration scope | REPLICATE_CONDITIONAL |
| fields requiring calibration | `4` |
| calibration artifacts | `6400` |
| calibration artifact basis | 400 replicates x 4 subconditions x 4 fields requiring calibration = 6,400 |
| subcondition count | `4` |
| replicate count | `400` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `sigma_psi_0p0` | `{"feeds_primary_claim":false,"g3_role":"SECONDARY","sigma_psi_deg":0.0}` |
| `sigma_psi_0p2` | `{"feeds_primary_claim":false,"g3_role":"SECONDARY","sigma_psi_deg":0.2}` |
| `sigma_psi_0p5` | `{"feeds_primary_claim":true,"g3_role":"PRIMARY","sigma_psi_deg":0.5}` |
| `sigma_psi_1p0` | `{"feeds_primary_claim":false,"g3_role":"STRESS","sigma_psi_deg":1.0}` |

**Pass / fail criterion.** PER FIELD, never pooled, R = 400, nominal alpha_geom = 0.005. Inflation is detected iff CP_lower(rejections, 400) > 0.005, i.e. 6 or more rejections -> STATISTICAL_SIZE_FAILURE. 0-5 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED, which means this experiment did not establish excess size, NOT that nominal size is proved. Secondary gross-inflation diagnostic (CP upper <= 0.03) may be reported but is not validation of alpha_geom.

### `C3_g5_block` — primary

**Purpose.** Validate the actual G5 block from full generated observations: sample-mean centring, A4-based leading-order variance, finite-sample behaviour, correlation, the two-mode max statistic and its interaction with the two-block gate

| | |
|---|---|
| v4 classification | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION |
| v4 classification note |  |
| authority | design section 15 item 8 |
| truth model | true null; G5 computed from generated trajectories, never as an independent companion variable |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K; sigma_psi PRIMARY = 0.5 deg, with 0.0/0.2 deg secondary and 1.0 deg stress, reported separately and never pooled [disposition G3] |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | block-2 achieved size consistent with alpha_2 = 0.1%; delta-method error quantified |
| seed family | validation |
| allowed seed families | `"calibration"` `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `true` |
| requires Block-1 calibration | `true` |
| primary release endpoint | G5_BLOCK_SIZE |
| Block-1 role | SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC |
| calibration scope | REPLICATE_CONDITIONAL |
| fields requiring calibration | `4` |
| calibration artifacts | `6400` |
| calibration artifact basis | 400 replicates x 4 subconditions x 4 fields requiring calibration = 6,400 |
| subcondition count | `4` |
| replicate count | `400` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `sigma_psi_0p0` | `{"feeds_primary_claim":false,"g3_role":"SECONDARY","sigma_psi_deg":0.0}` |
| `sigma_psi_0p2` | `{"feeds_primary_claim":false,"g3_role":"SECONDARY","sigma_psi_deg":0.2}` |
| `sigma_psi_0p5` | `{"feeds_primary_claim":true,"g3_role":"PRIMARY","sigma_psi_deg":0.5}` |
| `sigma_psi_1p0` | `{"feeds_primary_claim":false,"g3_role":"STRESS","sigma_psi_deg":1.0}` |

**Pass / fail criterion.** R = 400, nominal alpha_2 = 0.001. Inflation is detected iff CP_lower(G5 rejections, 400) > 0.001, i.e. 3 or more -> STATISTICAL_SIZE_FAILURE. 0-2 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED. Also report the measured sd(g2) against the leading-order 24 A4 / n prediction.

#### `C3_g5_block` semantics — resolved prospectively

| | |
|---|---|
| status | AMBIGUITY RESOLVED PROSPECTIVELY, before any random outcome exists |
| primary release endpoint | G5_BLOCK_SIZE |
| release criterion | UNCHANGED: R = 400, nominal alpha_2 = 0.001, CP_lower(G5 rejections, 400) > 0.001 detects inflation; 0-2 clean, 3+ STATISTICAL_SIZE_FAILURE |
| requires Block-1 calibration | `true` |
| Block-1 role | SECONDARY_PREDECLARED_INTERACTION_DIAGNOSTIC |
| joint P1 result changes the C3 release verdict | `false` |
| why calibration is retained | the frozen scientific purpose requires reporting the two-mode max statistic's INTERACTION WITH THE TWO-BLOCK GATE. That interaction is a P1 quantity and needs a CalibrationArtifact, so calibration is retained as a diagnostic input. |
| what is forbidden | adding any new C3 release threshold based on Block 1 or on the joint P1 result. The release verdict depends only on the already-frozen Block-2 / G5 size criterion. |

### `C4_surrogate_validity` — primary

**Purpose.** Achieved Block-1 size when calibration uses the covariance-matched surrogate but validation data come from the declared actual correlated process; measure the OPERATING-QUANTILE discrepancy, not covariance agreement

| | |
|---|---|
| v4 classification | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION |
| v4 classification note |  |
| authority | design section 15 item 5; design Appendix classification of the surrogate as an APPROXIMATION |
| truth model | calibration from the surrogate, validation from the declared OU process |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | achieved Block-1 rejection rate close to alpha_1 = 0.4% |
| seed family | calibration + validation |
| allowed seed families | `"calibration"` `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `true` |
| requires Block-1 calibration | `true` |
| primary release endpoint | BLOCK1_ACHIEVED_SIZE |
| Block-1 role | PRIMARY_RELEASE_ENDPOINT |
| calibration scope | REPLICATE_CONDITIONAL |
| fields requiring calibration | `4` |
| calibration artifacts | `8000` |
| calibration artifact basis | 2000 replicates x 1 subconditions x 4 fields requiring calibration = 8,000 |
| subcondition count | `1` |
| replicate count | `2000` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `primary` | `{}` |

**Pass / fail criterion.** R = 2000, nominal alpha_1 = 0.004. RETAIN the full two-sided interval and the observed operating-quantile discrepancy. IN ADDITION, classify inflation: detected iff CP_lower(rejections, 2000) > 0.004, i.e. 14 or more -> STATISTICAL_SIZE_FAILURE; 0-13 -> NO_SIGNIFICANT_SIZE_INFLATION_DETECTED. The binary diagnostic does not replace the discrepancy report.

### `C5_plug_in_branch_a` — primary

**Purpose.** Effect of analysing with measured/noisy H_A and tau_A while truth is generated from H_true and tau_true, including shape and orientation uncertainty

| | |
|---|---|
| v4 classification | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION |
| v4 classification note |  |
| authority | design section 15 item 6 |
| truth model | true null; analysis receives only the Branch-A measured field |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | `1.0` |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | swept: sigma_k in {0, 0.5%, 1%} x sigma_psi in {0, 0.2, 0.5, 1.0} degrees, 12 cells |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | achieved size degrades as sigma_psi grows; the magnitude is the result |
| seed family | validation + branch_a_measurement |
| allowed seed families | `"calibration"` `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `true` |
| requires Block-1 calibration | `true` |
| primary release endpoint | P1_REJECTION_RATE_PER_CELL |
| Block-1 role | PRIMARY_RELEASE_ENDPOINT |
| calibration scope | REPLICATE_CONDITIONAL |
| fields requiring calibration | `4` |
| calibration artifacts | `19200` |
| calibration artifact basis | 400 replicates x 12 subconditions x 4 fields requiring calibration = 19,200 |
| subcondition count | `12` |
| replicate count | `400` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `sk0p00_sp0p0` | `{"sigma_k":0.0,"sigma_psi_deg":0.0}` |
| `sk0p00_sp0p2` | `{"sigma_k":0.0,"sigma_psi_deg":0.2}` |
| `sk0p00_sp0p5` | `{"sigma_k":0.0,"sigma_psi_deg":0.5}` |
| `sk0p00_sp1p0` | `{"sigma_k":0.0,"sigma_psi_deg":1.0}` |
| `sk0p50_sp0p0` | `{"sigma_k":0.005,"sigma_psi_deg":0.0}` |
| `sk0p50_sp0p2` | `{"sigma_k":0.005,"sigma_psi_deg":0.2}` |
| `sk0p50_sp0p5` | `{"sigma_k":0.005,"sigma_psi_deg":0.5}` |
| `sk0p50_sp1p0` | `{"sigma_k":0.005,"sigma_psi_deg":1.0}` |
| `sk1p00_sp0p0` | `{"sigma_k":0.01,"sigma_psi_deg":0.0}` |
| `sk1p00_sp0p2` | `{"sigma_k":0.01,"sigma_psi_deg":0.2}` |
| `sk1p00_sp0p5` | `{"sigma_k":0.01,"sigma_psi_deg":0.5}` |
| `sk1p00_sp1p0` | `{"sigma_k":0.01,"sigma_psi_deg":1.0}` |

**Pass / fail criterion.** report the Clopper-Pearson one-sided 95% UPPER bound on the P1 rejection rate in EVERY one of the 12 declared cells, R = 400 each. No cell may be dropped after inspection.

### `C6_mode_resolution_boundary` — primary

**Purpose.** Size AND detection behaviour around theta_cap = 5 degrees at the predeclared boundary neighbourhood

| | |
|---|---|
| v4 classification | NEWLY REQUIRED BY AN ADOPTED V4 CORRECTION |
| v4 classification note |  |
| authority | design section 15 item 7; design section 10 |
| truth model | true null at rho = boundary, boundary -20%, boundary +20% |
| fields affected | `"synthetic two-mode field at the declared rho"` |
| beta truth | `1.0` |
| geometry truth | rho in {1.019573, 1.024467, 1.029360} at N_12 = 224726 |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | merge below the boundary, split above; size controlled on both sides |
| seed family | validation |
| allowed seed families | `"calibration"` `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `true` |
| requires Block-1 calibration | `true` |
| primary release endpoint | P1_REJECTION_RATE_PER_RHO |
| Block-1 role | PRIMARY_RELEASE_ENDPOINT |
| calibration scope | REPLICATE_CONDITIONAL |
| fields requiring calibration | `1` |
| calibration artifacts | `1200` |
| calibration artifact basis | 400 replicates x 3 subconditions x 1 fields requiring calibration = 1,200 |
| subcondition count | `3` |
| replicate count | `400` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `rho_1p019573` | `{"rho":1.019573,"role":"boundary -20%"}` |
| `rho_1p024467` | `{"rho":1.024467,"role":"boundary"}` |
| `rho_1p029360` | `{"rho":1.02936,"role":"boundary +20%"}` |

**Pass / fail criterion.** Clopper-Pearson one-sided 95% UPPER bound on the P1 rejection rate <= 3% at each of the three declared rho, R = 400 each; report the merge/split decision rate at each. theta_cap MUST NOT be changed after observing the result.

### `C7_false_bridge` — negative_control

**Purpose.** Probability of incorrectly ACCEPTING a false bridge, for every declared non-commensurable alternative including the hard near-margin case

| | |
|---|---|
| v4 classification | RETAINED BUT UPDATED FOR V4 |
| v4 classification note | evaluated against the all-field P3 and the IUT P2 |
| authority | design section 13; contract false_bridge_controls |
| truth model | beta_theta = (1,1.06,1,1); (1,0.93,1.05,1); (1,1,1,1.10); hard (1,1.025,1,1) |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | per alternative |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | acceptance close to zero for the coarse alternatives; the hard 2.5% case is the informative one |
| seed family | validation |
| allowed seed families | `"validation"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `false` |
| requires Block-1 calibration | `false` |
| calibration not required because | its frozen endpoints do not evaluate any P1 / Block-1 quantity. p1_geometry is the ONLY consumer of a CalibrationArtifact in the package, and this case never reaches it. Generating one would add a calibration refusal path that cannot affect the science but CAN affect the outcome. |
| primary release endpoint | P2_INTERSECTION_UNION_AND_P3_ALL_FIELD_ABSOLUTE |
| Block-1 role | NONE |
| calibration scope | NOT_APPLICABLE |
| fields requiring calibration | `0` |
| calibration artifacts | `0` |
| calibration artifact basis | 0 - this case evaluates no P1 / Block-1 quantity |
| subcondition count | `4` |
| replicate count | `400` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `alt_1_06` | `{"beta_true":[1,1.06,1,1]}` |
| `alt_0_93_1_05` | `{"beta_true":[1,0.93,1.05,1]}` |
| `alt_1_10` | `{"beta_true":[1,1,1,1.1]}` |
| `hard_1_025` | `{"beta_true":[1,1.025,1,1],"role":"hard near-margin case"}` |

**Pass / fail criterion.** For EACH declared alternative INDEPENDENTLY: one-sided 95% Clopper-Pearson UPPER bound on the false-acceptance rate <= 0.025 over R = 400, i.e. <= 4/400; 5 or more fails. Counts are never pooled and easy and hard alternatives are never averaged. [disposition G2, closed prospectively]

### `C8_blinded_scale_control` — positive_control

**Purpose.** Blinded duplicate-branch scale control: Branch-A declared scale multiplied by a hidden c, analysis must recover beta = 1/c

| | |
|---|---|
| v4 classification | RETAINED UNCHANGED |
| v4 classification note |  |
| authority | baseline section 14.2 (committed); design section 13 |
| truth model | true null with the Branch-A scale multiplied by a hidden c on a DUPLICATE branch that never touches primary data |
| fields affected | `"theta0_circular"` `"theta1_power"` `"theta2_ellipse"` `"theta3_temperature"` |
| beta truth | 1/c on the blinded branch |
| geometry truth | as declared per field |
| Branch-A uncertainty scenario | frozen candidate scenario: sigma_k = 0.34%, sigma_cm = 1.15%, sigma_T = 0.1 K |
| Branch-A uncertainty status | STOCHASTIC_PER_REPLICATE |
| Branch-B process | declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta) |
| expected qualitative outcome | beta_hat on the blinded branch concentrates on 1/c |
| seed family | blinded_scale_control |
| allowed seed families | `"blinded_scale_control"` `"branch_a_measurement"` |
| uses P1 / Block 1 | `false` |
| requires Block-1 calibration | `false` |
| calibration not required because | its frozen endpoints do not evaluate any P1 / Block-1 quantity. p1_geometry is the ONLY consumer of a CalibrationArtifact in the package, and this case never reaches it. Generating one would add a calibration refusal path that cannot affect the science but CAN affect the outcome. |
| primary release endpoint | P3_EQUIVALENT_TRANSFORMED_BETA_RECOVERY |
| Block-1 role | NONE |
| calibration scope | NOT_APPLICABLE |
| fields requiring calibration | `0` |
| calibration artifacts | `0` |
| calibration artifact basis | 0 - this case evaluates no P1 / Block-1 quantity |
| subcondition count | `1` |
| replicate count | `200` |

**Declared subconditions.** Every parameter is shown; a subcondition parameter that is not rendered here is not declared.

| subcondition | declared parameters |
|---|---|
| `paired_scale_control` | `{"pairing":"INTENTIONAL: both factors act on the SAME underlying synthetic replicate by the frozen deterministic Branch-A scale transform. They are NOT independent random subconditions and must not be given separate streams.","scale_factors":[1.07,0.9]}` |

**Pass / fail criterion.** beta_tilde_theta = c * beta_hat_theta must satisfy the SAME P3 absolute-equivalence rule (delta_abs = 0.05, z_abs = 1.959963985, h_theta = z sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2)) at EVERY tested field, for BOTH c = 1.07 and c = 0.90; any non-ESTIMATED field fails that branch. One replicate succeeds only if both branches pass. Campaign: one-sided 95% Clopper-Pearson LOWER bound on paired-control success >= 0.90 over R = 200, i.e. >= 188/200. [disposition G1, closed prospectively]

<!-- END GENERATED CASES -->


## 4. Generating model

The tables below are **generated** from `generating_model` in the JSON plan and
verified path-by-path at every preflight. Explanatory prose stays *outside* the
generated region: only the declared values participate in equality checking, and
every value that defines the synthetic experiment is inside it.

> `n_samples` is **derived**, not an independent input: `e1a_v4.world.World`
> computes it as `int(round(T_total / dt))`. Preflight recomputes it from the two
> primitives rather than trusting the stored number, so it can never become a third
> authority that quietly disagrees.

> The field table restates **frozen design-contract authority**. Preflight refuses a
> plan whose stiffness, temperature, orientation, reference flag, `dt` or `T_total`
> contradicts `docs/e1a/e1a_v4_design_contract.json`.

<!-- BEGIN GENERATED GENERATING MODEL -- do not hand-edit -->

**Branch B — the declared observation process.**

| setting | value | unit |
|---|---|---|
| process | `"declared correlated OU, exact transition, stationary initialisation x0 ~ N(x*, Sigma_theta)"` |  |
| transition | `"x_{k+1} = phi_r x_k + sqrt(1 - phi_r^2) L z, per mode, EXACT"` |  |
| phi | `"phi_r = exp(-dt / tau_r)"` |  |
| initialisation | `"x_0 ~ N(x*, Sigma_theta); stationary at step 0; burn_in_steps = 0"` |  |
| superseded convention | `"the v3 convention of starting at x = 0 is FORBIDDEN: it is not stationary"` |  |
| dt | `0.00012` | s |
| T_total | `240.0` | s |
| n_samples *(derived: T_total / dt)* | `2000000` | samples |

**Branch A — the measurement-error model.**

| setting | value |
|---|---|
| model | `"H_A = decorated H_true; its OWN seed family branch_a_measurement"` |
| common mode | `"ONE draw per experiment, shared across every field, so it cancels in the P2 ratio and not in P3"` |
| per mode stiffness | `"independent per mode"` |
| orientation | `"trap-axis psi"` |
| thermometry | `"T measured with sigma_T"` |
| independence | `"Branch-A measurement randomness is exogenous and never a function of the Branch-B trajectory"` |

**Truth visibility.** `"H_true and tau_true are known to the SCORING layer only. The analysis pipeline receives only the Branch-A measured field, exactly as in the real experiment."`

**Per-field generating parameters.** Every declared parameter is shown; a parameter not rendered here is not declared.

| field | k (uN/m) | T (K) | rotation (deg) | reference | beta_true | tau rule |
|---|---|---|---|---|---|---|
| `theta0_circular` | `[100, 100]` | `298` | `0` | `true` | `1.0` | `"tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a"` |
| `theta1_power` | `[210, 210]` | `298` | `0` | `false` | `1.0` | `"tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a"` |
| `theta2_ellipse` | `[150, 60]` | `298` | `30` | `false` | `1.0` | `"tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a"` |
| `theta3_temperature` | `[100, 100]` | `318` | `0` | `false` | `1.0` | `"tau_r = gamma(T)/k_r, gamma = 6 pi eta(T) a"` |

<!-- END GENERATED GENERATING MODEL -->

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

### 5.3 Calibration scope — REPLICATE-CONDITIONAL, frozen prospectively

```
calibration_scope = REPLICATE_CONDITIONAL
```

**Author disposition.** Every synthetic validation replicate that includes stochastic branch-a measurement uncertainty is analysed using calibration artifacts generated for that replicate's own realised branch-a calibration condition.

```
H_true,theta -> H_A,theta,r -> C_theta,r -> Branch-B analysis_theta,r
```

**Why.** a replicate stands for one repeated COMPLETE experiment and Branch-A measurement is part of it. The campaign validates Branch-A measurement + conditional calibration + Branch-B measurement + endpoint analysis as ONE repeated pipeline.

**Adopted because it matches the repeated-experiment scientific model, not because of cost.**
The superseded alternative was *four globally locked per-field calibration artifacts*.

| case | uses P1? | calibration scope | subconds | artifacts | basis |
|---|---|---|---:|---:|---|
| `C1_true_bridge_complete` | YES | **REPLICATE_CONDITIONAL** | 4 | 4,800 | 300 replicates x 4 subconditions x 4 fields requiring calibration = 4,800 |
| `C2_geometry_false_rejection` | YES | **REPLICATE_CONDITIONAL** | 4 | 6,400 | 400 replicates x 4 subconditions x 4 fields requiring calibration = 6,400 |
| `C3_g5_block` | YES | **REPLICATE_CONDITIONAL** | 4 | 6,400 | 400 replicates x 4 subconditions x 4 fields requiring calibration = 6,400 |
| `C4_surrogate_validity` | YES | **REPLICATE_CONDITIONAL** | 1 | 8,000 | 2000 replicates x 1 subconditions x 4 fields requiring calibration = 8,000 |
| `C5_plug_in_branch_a` | YES | **REPLICATE_CONDITIONAL** | 12 | 19,200 | 400 replicates x 12 subconditions x 4 fields requiring calibration = 19,200 |
| `C6_mode_resolution_boundary` | YES | **REPLICATE_CONDITIONAL** | 3 | 1,200 | 400 replicates x 3 subconditions x 1 fields requiring calibration = 1,200 |
| `C7_false_bridge` | **NO** | **none** | 4 | 0 | 0 - this case evaluates no P1 / Block-1 quantity |
| `C8_blinded_scale_control` | **NO** | **none** | 1 | 0 | 0 - this case evaluates no P1 / Block-1 quantity |
| | | | | **46,000** | |

> **A case requires Block-1 calibration only if its frozen analysis actually evaluates a
> P1 / Block-1 quantity.** `p1_geometry` is the sole consumer of a `CalibrationArtifact`
> in the package. *Branch-A stochastic* and *Block-1 calibration required* are **different
> properties** and are no longer equated. **C7** (P2 + P3) and **C8** (P3-equivalent) have
> **no calibration code path at all**: giving them one would add a refusal path that cannot
> affect the science but can affect the outcome — flattering C7's negative control and
> degrading C8's positive control.

No case uses `CASE_FIXED`. The value exists in the schema and is enforced, in the same way
`confirmatory` is a declared seed family authorised for no case.

#### Prohibited

- one theta0 artifact reused across every replicate
- one theta1 artifact reused across every replicate
- one theta2 artifact reused across every replicate
- one theta3 artifact reused across every replicate

whenever those replicates have independently realised Branch-A conditions. The prohibition
is **mathematical, not merely provenance-based**: the Block-1 null law moves with the
realised `H_A`.

> **A matching field name is insufficient. A nominal `H` is insufficient. An eigenvalue
> ratio is insufficient.** The complete repaired `CalibrationCondition` must match.

#### Limited reuse rule

Reuse is **not** categorically prohibited, but it is never implicit. All four conditions are
required:

1. the frozen case definition explicitly holds the calibration condition fixed across the relevant analyses
2. the complete CalibrationCondition digest is identical
3. the plan explicitly classifies that shared calibration as part of the case design
4. the resulting dependence is compatible with the statistical quantity being estimated

no cache-based reuse is permitted merely because two digests happen to match. CampaignCalibrationLedger refuses a digest already locked to a different (case, replicate, field) under REPLICATE_CONDITIONAL.

#### Ordering — calibration is blind to Branch B

```
1. derive frozen replicate/job seed identities (no draw)
2. generate the Branch-A synthetic measurement, branch_a_measurement family
3. construct the complete CalibrationCondition
4. generate and finalise the calibration artifact, calibration family
5. LOCK the artifact; it is immutable from here
6. ONLY THEN release the Branch-B validation stream, validation family
```

`ReplicateCalibration.validation_seed` **refuses** until that field's artifact is locked, so
the threshold cannot inspect Branch-B observations, G1-G5 from validation data, `beta_hat`,
or any endpoint result — none of them exists when it is built.

**Campaign-level implementation: `STREAMING_PER_REPLICATE`.**
the preferred PHASE A / PHASE B / PHASE C separation would materialise all 46,000 artifacts before any Branch-B draw. Each artifact carries 4 gates x R_cal = 50000 float64 null draws = 1.6 MB raw, so full Phase-B materialisation is about 74 GB binary and several hundred GB as JSON, against 24 GB of RAM on the reference machine. Streaming is therefore adopted, and it is exactly equivalent because ReplicateCalibration mechanically guarantees that the artifact for a given (case, subcondition, replicate, field) is finalised and immutable BEFORE the first Branch-B validation draw for it, and that no later validation result can alter it.

The artifact manifest is materialised in full for all 46,000 artifacts, about 3 MB of digests, so threshold freezing remains auditable before any validation outcome exists even though the draws themselves are streamed.

#### Artifact identity

Each locked artifact binds: `case_id`, `replicate_id`, `field_id`, `calibration_condition_sha256`, `artifact_sha256`, `analysis_procedure_identity`, `contract_sha256`, `calibrator_identity`, `R_cal`, `alpha_1`, `calibration_seed_identity`, `artifact_schema`.

Finalised artifacts are immutable; the ledger refuses a second lock for the same (case, replicate, field) and refuses any lock after that field's branch-b stream has been released.

#### One-ulp policy

**KEEP THE FAIL-CLOSED EXACT CANONICAL DIGEST.** Mathematical invariance of the statistic is not bitwise identity of the calibration-condition representation.

Every block-1 gate is invariant to h_a -> c h_a in exact arithmetic, but normalised_h(c*h) differs from normalised_h(h) in the last ulp, so the digests differ and the artifact is refused. this may create two artifacts where one would mathematically suffice. ACCEPTED for v4. Introducing rounding solely to increase
artifact reuse is **forbidden**, and canonical numerical equivalence is not redesigned here.

---

## 6. Statistical assurance

The release criteria. **Generated** from the JSON plan and verified at every preflight.

<!-- BEGIN GENERATED ASSURANCE -- do not hand-edit -->

| quantity | target | confidence | estimator | bound | R | acceptance rule |
|---|---|---:|---|---|---:|---|
| complete true-bridge pipeline success | `>= 0.90` | `0.95` | complete-pass proportion over declared replicates | Clopper-Pearson one-sided LOWER | `300` | >= 279 / 300 complete passes |
| P1 false-rejection rate, per field | `alpha_geom = 0.005` | `0.95` | rejection proportion | Clopper-Pearson one-sided LOWER (inflation test) | `400` | no inflation detected: CP_lower <= 0.005, i.e. <= 5/400, per field |
| block-2 (G5) rejection rate | `alpha_2 = 0.001` | `0.95` | rejection proportion | Clopper-Pearson one-sided LOWER (inflation test) | `400` | no inflation detected: CP_lower <= 0.001, i.e. <= 2/400 |
| Block-1 achieved size under the surrogate | `alpha_1 = 0.004` | `0.95` | rejection proportion | Clopper-Pearson two-sided (reported) + one-sided LOWER (inflation test) | `2000` | discrepancy REPORTED and classified; additionally no inflation detected: CP_lower <= 0.004, i.e. <= 13/2000 |
| false-bridge acceptance, per alternative | `<= 0.025 per alternative` | `0.95` | acceptance proportion | Clopper-Pearson one-sided UPPER | `400` | upper bound <= 0.025, i.e. <= 4 / 400, evaluated per alternative independently |
| blinded scale recovery beta_hat * c | `>= 0.90 paired-control success` | `0.95` | distribution of beta_hat * c | Clopper-Pearson one-sided LOWER | `200` | >= 188 / 200 paired-control successes |

<!-- END GENERATED ASSURANCE -->

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
subcondition           canon("subcondition", replicate_hex16, subcondition_id)  [ADDED]
scope                  canon("scope", subcondition_hex16, scope)                [ADDED]
hand_picked_values     False
```

`canon` is a deterministic domain-separated **serialisation**, not concatenation: the parts
are JSON-encoded with fixed separators and ASCII escaping, so a separator inside an
identifier cannot forge a different tuple.

**`scope`** is `experiment` for a quantity drawn once per synthetic experiment and shared
across fields, or a field id for a per-field quantity.

> **The `subcondition` and `scope` levels change none of the three above**: the master seed
> and **every family seed below are bit-identical**.
>
> **`subcondition` is required.** A case declares several distinct synthetic scenarios — four
> `sigma_psi` scenarios for C1/C2/C3, twelve uncertainty cells for C5, three rho conditions
> for C6, four false-bridge alternatives for C7. Without this level they all resolved to one
> stream, so **different declared scenarios silently shared random numbers**. They are
> separate declared scenarios and are **independently random by default**.
>
> **`scope` is required, and it is not simply "per field".** Randomness scope is a property of
> the quantity, not of the loop it sits in. See section 7.2.

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
| `C1_true_bridge_complete` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C2_geometry_false_rejection` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C3_g5_block` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C4_surrogate_validity` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C5_plug_in_branch_a` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C6_mode_resolution_boundary` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C7_false_bridge` | `calibration`, `validation`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |
| `C8_blinded_scale_control` | `calibration`, `blinded_scale_control`, `branch_a_measurement` | REPLICATE-CONDITIONAL CALIBRATION: this case builds its own calibration artifact per replicate and field, so it consumes the calibration fam… |

`confirmatory` is declared in the seed map and is authorised for **no case** in this campaign.
`blinded_scale_control` is authorised for **C8 alone**.

> **Every case declares `calibration`.** That is a *derived consequence* of adopting
> replicate-conditional calibration (section 5.3), not a relaxation: before the scope
> decision only C4 generated calibration data; now every case builds its own artifact per
> replicate and field.

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

### 7.2 Randomness dependency — what is shared, and what must not be

**Default rule.** Different declared synthetic subconditions use independent domain-separated random streams unless the frozen design explicitly declares them paired or shared.

**Exception.** the default applies BETWEEN declared subconditions. It must NOT destroy correlations deliberately built into a single synthetic experiment.

| quantity | family | scope | shared with | why |
|---|---|---|---|---|
| Branch-A common-mode calibration error (sigma_cm) | `branch_a_measurement` | `experiment` | all four fields of the SAME (case, subcondition, replicate) | INTENTIONAL |
| Branch-A per-mode stiffness error (sigma_k) | `branch_a_measurement` | `<field_id>` | nothing | drawn inside measure() from that field's own generator |
| Branch-A orientation error (sigma_psi) | `branch_a_measurement` | `<field_id>` | nothing | drawn inside measure() from that field's own generator |
| Branch-A thermometry error (sigma_T) | `branch_a_measurement` | `<field_id>` | nothing | drawn inside measure() from that field's own generator |
| calibration surrogate draws | `calibration` | `<field_id>` | nothing | one artifact per (case, subcondition, replicate, field); independence is what makes scheduling order irrelevant |
| Branch-B trajectory innovations | `validation, or blinded_scale_control for C8` | `<field_id>` | nothing | one OU record per field per replicate |
| C8 blinded scale factors c = 1.07 and c = 0.90 | `NONE - not random` | `n/a` | both factors act on the SAME underlying synthetic replicate | INTENTIONAL PAIRING |

> **The distinction this table exists to make.** *Accidental cross-subcondition sharing* is a
> defect and is closed by the `subcondition` seed level. *Intentional within-experiment
> sharing* is part of the frozen model and is preserved by the `experiment` scope. The
> Branch-A **common-mode** error is the load-bearing case: one draw per synthetic experiment,
> shared across all four fields, because that is exactly what makes it cancel in the P2 ratio
> and not in P3. Redrawing it per field would destroy the dependence structure P2 exists to
> test.

> **C8 pairing is intentional.** `c = 1.07` and `c = 0.90` act on the **same** underlying
> synthetic replicate through the frozen deterministic transform `BranchAField.blinded(c)`.
> They are **not** independent random subconditions, they get no separate streams, and the
> paired-success rule — both factors must pass within one replicate — is unchanged.

---

## 8. Controls

**Generated** from `controls` in the JSON plan.

<!-- BEGIN GENERATED CONTROLS -- do not hand-edit -->

| control | purpose | case |
|---|---|---|
| blinded scale distortion | scale-detection sensitivity | `C8` |
| geometry / coordinate permutation | destroys the correlation structure; the geometry control | `C7` |
| false-beta alternatives | false-bridge discrimination | `C7` |
| time shuffle | AUTOCORRELATION control only, not a geometry control; leaves S identical to 1e-30 | `C7` |
| paired hidden-scale distortion c = 1.07 / 0.90 | acts through P3/beta; gates are scale-invariant | `C8` |
| forbidden H := K | recorded as vacuous; demonstration only | `C7` |

<!-- END GENERATED CONTROLS -->

---

## 9. Output schema

Directory `results/e1a_v4_validation`, record schema `e1a_v4_validation_result/2`, manifest schema
`e1a_v4_validation_manifest/2`.

Per record: `case_id`, `subcondition_id`, `replicate_id`, `seed_family`, `seed_identity`, `field_id`, `truth_parameters`, `branch_a_observed`, `analysis_status`, `G1`, `G2`, `G3`, `G4`, `G5`, `P1`, `beta_hat`, `P2`, `P3`, `P4`, `complete_pass`, `refusal_reason`, `procedure_identity`, `contract_sha256`, `plan_sha256`, `implementation_commit`.

Aggregate: `success_count`, `failure_count`, `refusal_count`, `refusals_by_reason`, `confidence_bound`, `false_bridge_acceptance`, `per_field_geometry_rates`, `mode_resolution_behaviour`, `g5_diagnostics`, `scale_control_recovery`, `classification`.

Reproduction: seed family + master seed + case id + subcondition id + replicate index
and declared scope regenerate any record exactly.

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

<!-- BEGIN GENERATED RELEASE RULES -- do not hand-edit -->

#### G1 — affects `C8` — **CLOSED PROSPECTIVELY**

**Gap.** blinded scale control had no quantitative recovery criterion beyond beta = 1/c

**Resolution.** beta_tilde = c * beta_hat must satisfy the SAME P3 absolute-equivalence construction (delta_abs = 0.05, z_abs = 1.959963985) at EVERY tested field for BOTH c = 1.07 and c = 0.90; a replicate succeeds only if both branches pass. Campaign: one-sided 95% CP LOWER bound >= 0.90 over R = 200, i.e. >= 188/200.

#### G2 — affects `C7` — **CLOSED PROSPECTIVELY**

**Gap.** false-bridge alternatives had no maximum acceptable acceptance rate

**Resolution.** maximum false-acceptance probability 0.025, tied to the equivalence test's one-sided nominal level at z = 1.959963985 and NOT derived from any observed outcome. Per alternative INDEPENDENTLY: one-sided 95% CP UPPER bound <= 0.025 over R = 400, i.e. <= 4/400. Counts are never pooled.

#### G3 — affects `C1, C2, C3` — **CLOSED PROSPECTIVELY**

**Gap.** sigma_psi was recorded in the contract as 'to be declared'

**Resolution.** PRIMARY RELEASE SCENARIO sigma_psi = 0.5 degrees; the complete true-bridge >= 0.90 claim is asserted there. 0.0 and 0.2 degrees are secondary lower-uncertainty sensitivity cases; 1.0 degree is a stress/robustness case. All are reported, none is pooled into the primary result, and the stress case neither redefines the primary criterion nor is removed if it performs poorly.

#### Final campaign classification

**Verdict on success.** `VALIDATION_PASS`

**Rule.** CONJUNCTIVE. Every required case must pass on its own terms.

1. 1. C1 complete-pipeline success: CP lower >= 0.90 over R = 300 (>= 279/300)
2. 2. C2 produces no STATISTICAL_SIZE_FAILURE in any required field
3. 3. C3 produces no STATISTICAL_SIZE_FAILURE
4. 4. C4 produces no STATISTICAL_SIZE_FAILURE
5. 5. C5 satisfies its already-frozen plug-in Branch-A criterion
6. 6. C6 satisfies its already-frozen mode-resolution criterion
7. 7. EVERY C7 false-bridge alternative satisfies G2: CP upper <= 0.025 (<= 4/400)
8. 8. C8 satisfies G1: CP lower >= 0.90 over R = 200 (>= 188/200)
9. 9. no SOFTWARE_OR_INVARIANT_FAILURE, CALIBRATION_FAILURE, NUMERICAL_OR_PRECISION_FAILURE occurs
10. 10. structured refusals counted exactly per the already-frozen unconditional denominator rule

<!-- END GENERATED RELEASE RULES -->

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

A final **`VALIDATION_PASS`** requires **all** of the declared requirements. CONJUNCTIVE.
Every required case must pass on its own terms. There is **no weighted score** and **no
compensation** between cases.

> The verdict, the rule and the numbered requirements are rendered **once**, in the
> generated release-rules region in section 12. They were previously restated here as
> well, unchecked; a second hand-maintained copy of a release rule is exactly the drift
> this package now refuses, so this section points at the generated one instead.

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

**OFFICIAL EXECUTION COMMAND NOT RUN.** `execution_authorised` is `false` in the frozen plan.
The command refuses before drawing anything — and it refuses **first** because the official
campaign driver is ABSENT, not because of the flag. That ordering is deliberate: a refusal must
never read as *"just flip the authorisation flag"* when the driver that would do the work does
not exist. See section 13a.

Preflight checks, all completed **before any RNG is created**:

1. **Markdown/JSON authority coherence** — the generated authority block equals the block
   derived from the JSON plan, and the human-visible renderings equal that block
1. **execution-seal state** declared in the plan equals the state in the external seal file
1. working scientific contract identity equals the frozen contract sha256
1. prospective design, foundation and baseline identities
1. analysis procedure identity
1. every implementation file hash
1. validation plan identity
1. seed map identity and its rederivation from the declared algorithm
1. execution identity, recomputed — compared to `final_expected_execution_identity` only when
   that slot is non-null
1. the `final_expected_execution_identity` slot is **present**: an absent slot is a forgotten
   freeze and refuses
1. no output collision
1. expected execution stage
1. execution_authorised flag


---

## 13a. Execution-seal architecture — FROZEN PROSPECTIVELY

A package that recomputes its own execution identity and compares it to *nothing* has not been
sealed: any change to the package changes the identity, and the check still passes. A seal is
only a seal if the expected value was frozen **independently, in advance, by a reviewer**.

### Avoiding the self-reference

| | |
|---|---|
| **execution identity** | `H(`validation module hashes, analysis identity, plan JSON sha256, **plan Markdown sha256**, seed-map sha256`)` |
| **execution seal** | an **external** assertion of the expected execution identity |
| seal file | `docs/e1a/e1a_v4_execution_seal.json` |
| seal in the preimage? | **NO — deliberately excluded** |

The expected value cannot live in any preimage input: writing it into the plan would change the
plan's sha256 and therefore change the very value it records, an impossible fixed point. So the
assertion lives outside the package it describes.

### The state machine

| state | meaning | `expected_execution_identity` | preflight | execution |
|---|---|---|---|---|
| **`PRE_DRIVER`** | official campaign driver absent | **MUST be `null`** | may pass | **REFUSES** |
| **`FROZEN`** | driver implemented and independently audited; reviewer has frozen the expected identity | **MUST be a 64-hex digest** | may pass | eligible **only** if the recomputation matches **and** `execution_authorised` is true |

`execution_authorised = true` is set by a **separate** final authorisation task. A `FROZEN`
seal is not an authorisation, and an authorisation without a `FROZEN` seal is refused.

### Not-yet-frozen versus forgotten

These must never look alike. An **absent** seal file, an **absent** state, or an **absent**
`expected_execution_identity` key is treated as **FORGOTTEN** and refuses. Only the explicit
pair (`state = PRE_DRIVER`, `expected_execution_identity = null`) means *deliberately not yet
frozen*. The superseded plan slot held the empty string `""`, which could express neither, and
which preflight silently skipped.

### The execution gate, in order

1. the official campaign driver exists on disk
1. the external execution seal is `FROZEN`
1. the recomputed execution identity equals the independently frozen seal
1. `execution_authorised` is true

Most fundamental missing precondition first. Every branch refuses **before** the RNG factory is
touched.

### Current state

```
execution seal state            = PRE_DRIVER
expected execution identity     = null   (deliberately NOT YET FROZEN)
official campaign driver        = e1a_v4/validation/campaign_driver.py (canonical, identity-bound)
official campaign driver state  = ABSENT   (a runtime fact, checked by the execution gate)
execution_authorised            = false
```

The identity preflight reports today is a **PRE-DRIVER PACKAGE EXECUTION IDENTITY**: a
diagnostic, not the final expected value. It **will** legitimately change when the official
campaign driver is implemented and enters the preimage — which is precisely why it is not
frozen now.

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


---

## 15. Parallelism policy

Parallel execution is permitted **as an execution optimisation only**. It must not alter seed
derivation, artifact contents, replicate identities, case definitions, result ordering
semantics or thresholds. A serial and a parallel execution must produce **identical**
scientific artifacts and results for the same frozen protocol, aside from non-scientific
ordering and timing metadata.

The mechanism: every calibration job is a pure function of `(family, case, replicate, field)`.
Deterministic scheduling is tested in `test_e1a_v4_calibration_scope.py`. **No stochastic job
is executed.**

---

## 16. What the cost figures actually contain

Re-measured and decomposed before being repeated, because a number quoted without its
contents is not evidence.

| component of ONE artifact build | measured |
|---|---:|
| surrogate draws + four gates, `R_cal = 50000` | `2.645 s` |
| threshold finalisation | `0.057 s` |
| **total, wall, median of 5** | **`2.674 s`** (CPU `2.627 s`, range `2.616`–`2.698`) |

**Threshold finalisation is about 2% of an artifact build.** The other ~98% is surrogate
generation and gate evaluation, which the B2 repair did not touch and could not touch. A
figure of "N core-hours of calibration" is therefore almost entirely surrogate generation,
and calling it "threshold work" would misattribute it.

| | artifacts | projection |
|---|---:|---:|
| replicate-conditional (adopted) | 40 000 | **29.7 core-hours** |
| four locked artifacts (superseded) | 4 | **10.7 s** |
| Branch-A realisations | 40 000 | 0.51 s |
| compatibility checks + P1 uses | 40 000 | 1.0 s |

**BENCHMARK-BASED PROJECTION** from a MEASURED per-unit cost. **NOT MEASURED END-TO-END.**
**EXCLUDED from every figure above:** Branch-B trajectory generation, 2 000 000 steps per
field-replicate, which is the largest term in the campaign.

> The repair report quoted `3.008 s` per artifact and `33.4 core-hours` from a 2-repetition
> timing taken while other work was running. A 5-repetition timing gives `2.674 s` and
> **29.7 core-hours**. Both are projections; the earlier one was noisier. Neither is a
> measured campaign runtime.

**Cost is not the scientific decision rule.** Replicate-conditional calibration is adopted
because it matches the repeated-experiment model. The cost is recorded for planning only and
was not allowed to weaken the architecture.

```
execution_authorised = false
RANDOM DRAWS = 0   TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN   VALIDATION CAMPAIGN = NOT RUN
```


---

## 17. Correction — the superseded 40,000 artifact count

An independent pre-execution re-audit found that the previously declared total of
**40,000** was wrong. it was produced by two compensating errors: a 7,200 OVER-count (C7 and C8 were budgeted artifacts their endpoints never consume) and a 13,200 UNDER-count (the G3 sigma_psi subconditions of C1, C2 and C3 were budgeted for one scenario each instead of four). 40,000 - 7,200 + 13,200 = 46,000, so a check on the SUM alone passed while both components were wrong.

| case | replicates | subconditions | fields needing calibration | artifacts |
|---|---:|---:|---:|---:|
| `C1_true_bridge_complete` | 300 | 4 | 4 | **4,800** |
| `C2_geometry_false_rejection` | 400 | 4 | 4 | **6,400** |
| `C3_g5_block` | 400 | 4 | 4 | **6,400** |
| `C4_surrogate_validity` | 2,000 | 1 | 4 | **8,000** |
| `C5_plug_in_branch_a` | 400 | 12 | 4 | **19,200** |
| `C6_mode_resolution_boundary` | 400 | 3 | 1 | **1,200** |
| `C7_false_bridge` | 400 | 4 | 0 | **0** |
| `C8_blinded_scale_control` | 200 | 1 | 0 | **0** |
| | | | **TOTAL** | **46,000** |

Every factor is derived from the machine-readable plan, not typed first and matched
afterwards.

### Runtime, recomputed from the corrected count

| | |
|---|---|
| measured cost of one artifact build | **`2.674 s`** wall, `2.627 s` CPU, median of 5 — **MEASURED** |
| of which threshold finalisation | `0.057 s`, about 2% — the rest is surrogate generation |
| 46,000 artifacts | **34.2 core-hours** — **BENCHMARK-BASED PROJECTION** |

This supersedes the 29.7 core-hour figure, which rested on the incorrect 40,000 count.
**NOT MEASURED END-TO-END**: no campaign, calibration or trajectory has run, and Branch-B
trajectory generation is excluded from every figure above and remains the larger term.
No resource ceiling is declared, so this establishes **neither feasibility nor
infeasibility** — only the projected cost.

```
execution_authorised = false
RNG OBJECTS = 0   RANDOM DRAWS = 0   TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN   VALIDATION CAMPAIGN = NOT RUN
```

---

## 18. Plan-coherence and execution-seal repair — SUPERSESSION RECORD

**Status.** PRE-EXECUTION AUTHORITY-INTEGRITY REPAIR. No stochastic evidence exists, so nothing
scientific is retracted. **No E1a scientific decision rule changed.**

**Trigger.** independent audit finding that this Markdown and the JSON plan disagreed on their
frozen metadata while preflight still reported PASS.

### What was wrong

| field | superseded value here | adopted value | verdict |
|---|---|---|---|
| plan version | `1.5.0` | `1.7.0` | **stale by two releases** |
| analysis procedure identity | `bc1c0fce3b9004aed5f6b4be2162bc876697536ee614b2e57f680f3a65dc283e` | `dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f` | **never true at any commit** |

The identity is the more serious of the two. A stale value would at least have been correct
once; `bc1c0fce…` was recomputed at every commit in this package's history and **matches none
of them**, nor any tested configuration variant. It entered this document at
`5727e10` — the same commit that wrote the correct `dd2ed732…` into the JSON plan and into
`E1A_V4_PREEXEC_REPAIR_REPORT.md` — and appeared nowhere else in the repository. The version
drift entered separately, at `8ea81ea`, which bumped the JSON to `1.6.0` and edited this
document without touching its version line.

Both survived because preflight compared **only** the section-9 output schema. Neither the
identity table nor the version line was checked against anything.

### Why the JSON won

Not because it is JSON. `dd2ed732…` is the value `procedure_identity(binding, {}, root)`
actually produces, verified by recomputation at every commit from `5727e10` to HEAD, and it is
the value carried independently by the JSON plan and by four committed reports. The Markdown
cell was the sole dissenter and was demonstrably wrong. **Nothing was reconciled by preference.**

### Scope, verified

All **79** duplicated normative fields were compared before any edit: 77 agreed, and the only
two that disagreed are the two above. Every case identifier, role, replicate count,
subcondition list, calibration flag, calibration scope, seed-family grant, release endpoint,
output-schema field and failure classification **already agreed**. No scientific rule, threshold,
seed, case semantic or generator behaviour was touched by this repair.

### What is now enforced

- a generated, anchor-delimited authority block in this document — section 1a
- a human-rendering check covering the version line, the identity table, the authorisation
  sentence and every case table — section 1a
- this Markdown hashed into the execution-identity preimage — section 1
- an external, non-self-referential execution seal with an explicit lifecycle — section 13a
- an execution gate that refuses on driver absence **before** it reaches the authorisation flag

```
execution_authorised = false
official campaign driver = ABSENT
final execution seal = NOT FROZEN
RNG OBJECTS = 0   RANDOM DRAWS = 0   TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN   VALIDATION CAMPAIGN = NOT RUN
```

---

## 19. Generating-model coherence — SUPERSESSION RECORD

**Status.** PRE-EXECUTION AUTHORITY-INTEGRITY REPAIR. No stochastic evidence exists, so nothing
scientific is retracted. **No E1a scientific decision rule changed.**

**Trigger.** independent audit finding that section 4 renders the generating model's scientific
settings while the coherence specification classified `generating_model` as JSON-only.

### What was wrong

The whole object was classified with one subtree-level shortcut, so **every** descendant was
outside the checked surface. Reproduced at `addd704`, before any edit:

| one-sided change | before |
|---|---|
| visible `n_samples` `2000000` → `2000001` | **ACCEPTED** |
| visible `dt` `0.00012` → `0.00013` | **ACCEPTED** |
| visible `theta1_power` stiffness `[210,210]` → `[200,200]` | **ACCEPTED** |
| visible `theta3_temperature` `T` `318 K` → `350 K` | **ACCEPTED** |
| visible `theta2_ellipse` rotation `30°` → `45°` | **ACCEPTED** |
| visible `T_total` `240.0` → `480.0 s` | **ACCEPTED** |
| visible `theta0_circular` reference `yes` → `no` | **ACCEPTED** |
| visible `beta_true` `1.0` → `1.06` | **ACCEPTED** |
| visible `burn_in_steps` `0` → `5000` | **ACCEPTED** |
| the same six changes made in the **JSON** alone | **ACCEPTED** |
| the plan **contradicting the frozen design contract** on `theta1_power` stiffness | **ACCEPTED** |

Nine Markdown-only and six JSON-only probes, all accepted. The auditor named three; the class was
wider than the three.

### What is now enforced

- every descendant primitive of `generating_model` is classified **individually** — no
  subtree-level shortcut may hide a duplicated descendant
- section 4's normative tables are **generated** from the JSON and compared path by path
- `n_samples` is **DERIVED**, recomputed as `int(round(T_total / dt))` exactly as
  `e1a_v4.world.World` derives it, never trusted as a third authority
- the plan's restatement of **frozen design-contract authority** — every field's stiffness,
  temperature, orientation and reference flag, plus `dt` and `T_total` — is checked against the
  contract, which outranks the plan
- section 8's control-to-case mapping is generated
- the section-12a size boundaries are recomputed by `size_boundary` and `cp_lower`
- **every** `##` section of this document is registered as GENERATED, PARSED, DERIVED or
  NON_NORMATIVE with a reason, and an unregistered section refuses

```
execution_authorised = false
official campaign driver = ABSENT
final execution seal = NOT FROZEN
RNG OBJECTS = 0   RANDOM DRAWS = 0   TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN   VALIDATION CAMPAIGN = NOT RUN
```
