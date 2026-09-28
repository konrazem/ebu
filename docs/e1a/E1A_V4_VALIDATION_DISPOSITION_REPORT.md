# E1a v4 — VALIDATION DISPOSITION REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**All three pre-execution authority gaps — G1, G2 and G3 — are closed prospectively**,
before execution and before any outcome was observed. Every dependent identity was rebound
mechanically. The package is re-frozen.

`execution_authorised` remains **false**. The official execution command still refuses
before any RNG is created.

These dispositions complete missing **validation** rules. They do **not** redesign the E1a
bridge: these complete missing VALIDATION rules; they do not redesign the E1a bridge. P1, P2, P3, P4, delta_cross, delta_abs, the z factors, alpha allocations, theta_cap, rank_tol, the four physical fields, the complete-pipeline target and the anti-circularity rules are all unchanged.

---

## G1 — blinded scale control

Committed scientific target, unchanged: `beta_blinded = 1/c`. Retained paired distortions:
**c = 1.07** and **c = 0.90**.

```
beta_tilde_theta = c * beta_hat_theta_blinded        should equal 1

h_theta = z_abs * sqrt( sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2 )

branch for factor c passes  iff  for EVERY tested field:
    beta_tilde_theta (1 - h_theta) >= 1 - delta_abs
    beta_tilde_theta (1 + h_theta) <= 1 + delta_abs

delta_abs = 0.05     z_abs = 1.959963985
```

**No new tolerance was introduced.** This is the *same* absolute-equivalence construction
already adopted for P3, and `g1_blinded_branch` literally calls `p3_absolute` on the
transformed betas — a test asserts the results are identical row for row.

Any non-`ESTIMATED` field fails that branch. **One C8 replicate succeeds only if the
c = 1.07 branch passes at all four fields AND the c = 0.90 branch passes at all four
fields.** The underlying primary synthetic observations are not altered to create the
control.

**Campaign criterion, R = 200:** one-sided 95% Clopper–Pearson **lower** bound on
paired-control success ≥ 0.90.

| | |
|---|---|
| derived integer threshold | **≥ 188 / 200** |
| `cp_lower(188, 200)` | `0.904599` ≥ 0.90 → **passes** |
| `cp_lower(187, 200)` | `0.898643` < 0.90 → **fails** |

The threshold is **recomputed** by `g1_success_threshold(200, 0.90)` in the test suite,
not copied from the plan; the test then asserts the plan records the same value.

**Scope.** tests recovery of a deliberately changed Branch-A scale. Does not change P3, does not change the primary-data analysis, and is not part of the primary E1a evidence.

---

## G2 — false-bridge discrimination

Declared alternatives **unchanged**, disparities **not weakened**:
`beta = (1, 1.06, 1, 1)`, `(1, 0.93, 1.05, 1)`, `(1, 1, 1, 1.10)`, and the hard
`(1, 1.025, 1, 1)` near-margin case.

Maximum acceptable false-acceptance probability: **0.025**. tied prospectively to the existing equivalence-test one-sided nominal level associated with z = 1.959963985; NOT derived from observed validation outcomes

**Campaign criterion, R = 400 per alternative:** one-sided 95% Clopper–Pearson **upper**
bound ≤ 0.025.

| | |
|---|---|
| derived integer threshold | **≤ 4 / 400** |
| `cp_upper(4, 400)` | `0.022737` ≤ 0.025 → **passes** |
| `cp_upper(5, 400)` | `0.026102` > 0.025 → **fails** |

**Each alternative must independently satisfy the rule.** Counts are never pooled and easy
and hard alternatives are never averaged. A test makes the consequence explicit: with
counts `(0, 0, 0, 5)` the campaign **fails**, even though the pooled mean of `1.25/400`
would have passed.

---

## G3 — primary sigma_psi

| role | `sigma_psi` | treatment |
|---|---:|---|
| **PRIMARY RELEASE SCENARIO** | **0.5°** | the complete true-bridge **≥ 0.90** claim is asserted here |
| secondary, lower-uncertainty sensitivity | 0.0°, 0.2° | reported, never pooled into the primary result |
| stress / robustness | 1.0° | reported; does **not** redefine the primary release criterion, and is **not** removed if it performs poorly |

`g3_primary_claim_inputs` returns only the primary scenario's successes and lists the
others under `excluded_from_primary` with `pooling_prohibited = True`, so a stress outcome
cannot overwrite the primary classification. A value off the declared grid is refused.

This remains a **hypothetical synthetic uncertainty scenario**. It is **not** a claim that
any real apparatus has demonstrated 0.5° orientation uncertainty.

---

## Authority changes

| file | change |
|---|---|
| `docs/e1a/e1a_v4_design_contract.json` | version 1.1.0; `sigma_psi_deg = 0.5` with its classification; new `synthetic_validation_release_criteria` section carrying G1 and G2 |
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | §11 `sigma_psi` row; new §11.1 primary/secondary/stress table; §15 items 11 and 12; scope note that items 11–12 are validation criteria only |
| `docs/e1a/e1a_v4_synthetic_validation_plan.json` | version 1.1.0; `author_dispositions`; gaps marked CLOSED PROSPECTIVELY; C7 and C8 criteria; assurance rows; `superseded_package` |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md` | identity table, seed table, C7/C8 criteria, Branch-A rows, assurance rows, §12 rewritten as dispositions |
| `docs/e1a/e1a_v4_seed_map.json` | rederived mechanically under the new contract identity |
| `docs/theory/EBU_THEORY_BASELINE.meta.json` | records the new design hash and contract version |
| `e1a_v4/contract.py` | accepts contract minor version 1.1; every coherence check unchanged |
| `e1a_v4/validation/dispositions.py` | **new** — G1/G2/G3 rules and exact Clopper–Pearson thresholds |
| `e1a_v4/validation/plan.py` | registers `dispositions.py` in the execution identity |
| `test_e1a_v4_dispositions.py` | **new** — 64 deterministic checks |
| `test_e1a_v4_preexec.py` | updated for the closed dispositions |

**The frozen foundation and the baseline text are untouched.** Only the baseline sidecar
moved, to record the new design hash.

---

## Rebound identities

Rebound mechanically. No hash was preserved artificially and no seed was hand-edited.

| item | old | new |
|---|---|---|
| contract | `89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c` | `91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b` |
| design | `f20bc885bf400ce3429120e4a0e42915ba2fb15249d88914fd7e55eb1b373f68` | `e59dcff6b363e6ba59222b06867973703fd429f1223452cdfa2a4d47fadca495` |
| validation plan JSON | `142e9a8f424d970e063eaca8a0a209da365ad1408b80d9b5b7c67b763ca6c894` | `88d0f1d54231dff01325aa0ea2251ce6316a3c7070880f08c184f00c72bd5185` |
| validation plan Markdown | `ee0c8779176473899f32da9e3ece5f4291d537a07230079f1fa237de2eee6eaf` | `a334c8692d9f5326a0abdf9d253ee9c415f49bda3c163d95ac88410cbff1b74a` |
| seed map | `bb21dd6cc9959c1b61812d54925b56d64f7ecf8a8c36c68c03605af69802979d` | `28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87` |
| analysis identity | `1983ba3af64cd62480feb642ce83f38cf7d2e5f06bf9398b41b81fe1f864648c` | `af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4` |
| execution identity | `2f4902a17c3ce0d187e308bb061cf239ee328639d313f428e22a7af175384d71` | `0f4ec684de445390fa6d00b4bf7be0c6ce9656fee496f6891e9347ab1d5f0341` |

The contract hash changed because `sigma_psi` is now prospectively fixed and the release
criteria were added. That is expected and correct.

---

## Seed map

Because the derivation binds to the frozen authority identity, **every seed changed**. The
committed map rederives from the already-committed algorithm, and the runner refuses if it
does not.

| family | old | new |
|---|---|---|
| master | `12737552942663785904` | `13785910525869478477` |
| `blinded_scale_control` | `9479310386300230328` | `11987123625083329897` |
| `branch_a_measurement` | `11004995623645776693` | `62746336670861162` |
| `calibration` | `15379082101033647447` | `6644164099584621674` |
| `confirmatory` | `9585841150145721670` | `9827224290341944517` |
| `validation` | `11476631527835384658` | `5088042359768187837` |

**No seed was used.** No value was drawn from either the old or the new seeds.

---

## Static validation

```
$ python3 test_e1a_v4_dispositions.py

G1 blinded scale control
  [PASS] transformed blinded beta is exactly c * beta_hat  -- c = 1.07, beta_hat = 1/c
  [PASS] the SAME P3 rule is reused, not a new tolerance
  [PASS] G1 uses the adopted P3 margin and coverage factor, read from the contract
  [PASS] G1 branch passes when recovery is exact
  [PASS] one field outside the 5% band fails the branch
  [PASS] a non-ESTIMATED field fails the branch
  [PASS] all four fields are evaluated
  [PASS] the declared factors are exactly 1.07 and 0.90
  [PASS] a replicate passes only when BOTH factors pass
  [PASS] failing the c = 0.90 branch fails the replicate
  [PASS] a missing branch fails the replicate
  [PASS] CP lower threshold RECOMPUTED for R = 200, target 0.90  -- cp_lower(188,200) = 0.904599
  [PASS] one count below the threshold fails  -- cp_lower(187,200) = 0.898643
  [PASS] 188/200 passes the campaign criterion  -- CP lower = 0.904599
  [PASS] 187/200 fails the campaign criterion  -- CP lower = 0.898643
  [PASS] plan records the derived threshold, and it matches the recomputation
  [PASS] G1 does not alter P3 itself

G2 false-bridge discrimination
  [PASS] declared alternatives unchanged
  [PASS] CP upper threshold RECOMPUTED for R = 400, target 0.025  -- cp_upper(4,400) = 0.022737
  [PASS] the next count fails  -- cp_upper(5,400) = 0.026102
  [PASS] 4/400 passes  -- CP upper = 0.022737
  [PASS] 5/400 fails  -- CP upper = 0.026102
  [PASS] target is exactly 0.025
  [PASS] 0.025 is tied to the equivalence z, not to an observed outcome
  [PASS] every alternative satisfying the rule passes
  [PASS] ONE alternative at 5/400 fails the whole campaign  -- counts are never pooled; the hard case cannot be rescued by easy ones
  [PASS] pooling would have hidden the failure  -- mean 1.25/400 would pass, but the rule is per alternative
  [PASS] each alternative is evaluated independently
  [PASS] plan records the derived threshold, and it matches the recomputation

G3 primary sigma_psi
  [PASS] primary sigma_psi is exactly 0.5 degrees
  [PASS] 0.0 and 0.2 are secondary
  [PASS] 1.0 is stress
  [PASS] roles resolve correctly
  [PASS] a value off the declared grid is refused
  [PASS] the >= 0.90 claim is asserted at the primary value
  [PASS] only the primary scenario feeds the primary claim
  [PASS] the stress result cannot overwrite the primary classification
  [PASS] a missing primary scenario is refused
  [PASS] the stress case is not removed for performing poorly
  [PASS] it remains a hypothetical scenario, not a measured capability

rebound identities and seeds
  [PASS] the contract hash changed
  [PASS] the design hash changed
  [PASS] the analysis identity changed with the contract
  [PASS] the frozen analysis identity matches a live recomputation
  [PASS] the plan hash changed
  [PASS] the seed-map hash changed
  [PASS] the execution identity changed  -- 0f4ec684de445390...
  [PASS] the seed map mechanically rederives under the NEW authority
  [PASS] every seed actually changed
  [PASS] no seed overlap  -- 5 families
  [PASS] seeds are still derived, never hand-picked
  [PASS] the disposition module imports no RNG source  -- imports ['__future__', 'dataclasses', 'math', 'typing']
  [PASS] the disposition module contains no draw call site  -- 3 attribute call sites, none a draw

nothing else moved
  [PASS] P2 margin unchanged
  [PASS] P3 margin unchanged
  [PASS] z factors unchanged
  [PASS] alpha allocations unchanged
  [PASS] theta_cap unchanged
  [PASS] rank_tol unchanged
  [PASS] four physical fields unchanged
  [PASS] complete-pipeline target unchanged
  [PASS] anti-circularity rules unchanged
  [PASS] P4 classification unchanged
  [PASS] execution remains unauthorised

E1a v4 disposition gate: 64 passed, 0 failed, 5 groups
Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)
  RANDOM DRAWS          : 0
  TRAJECTORIES          : 0
  CALIBRATION EXECUTION : NOT RUN
  VALIDATION CAMPAIGN   : NOT RUN
  G1 threshold (derived): >= 188 / 200
  G2 threshold (derived): <= 4 / 400
  primary sigma_psi     : 0.5 degrees
```

| suite | passed | failed |
|---|---:|---:|
| disposition | **64** | 0 |
| pre-execution | **92** | 0 |
| implementation | **119** | 0 |
| design authority | **113** | 0 |

```
$ python3 -m e1a_v4.validation.runner --preflight-only
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : 88d0f1d54231dff01325aa0ea2251ce6316a3c7070880f08c184f00c72bd5185
  seed map sha256            : 28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87
  analysis procedure identity: af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4
  execution identity         : 0f4ec684de445390fa6d00b4bf7be0c6ce9656fee496f6891e9347ab1d5f0341
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
  RANDOM DRAWS: 0   TRAJECTORIES: 0   (preflight only)
```

```
$ python3 -m e1a_v4.validation.runner --execute --i-have-execution-authorisation
PREFLIGHT PASSED
  contract sha256            : 91d6ae76ccb6fdbeb7f926722433c574c30b7c0b6105c7c1ec20436fa2ec431b
  plan sha256                : 88d0f1d54231dff01325aa0ea2251ce6316a3c7070880f08c184f00c72bd5185
  seed map sha256            : 28d8b0584b1cd4da0b9a536c8d332d03a116a3f227efaed135297d46aa944d87
  analysis procedure identity: af1177a9d3220f60f78ef738bbee6c925da3ed632b68a9f51830fffe5e985eb4
  execution identity         : 0f4ec684de445390fa6d00b4bf7be0c6ce9656fee496f6891e9347ab1d5f0341
  output directory           : results/e1a_v4_validation
  declared cases             : 8
  execution_authorised       : False
EXECUTION REFUSED: EXECUTION REFUSED: the frozen validation plan has execution_authorised = false. The synthetic-validation campaign is a separate authorised stage. No random number has been drawn.
  RANDOM DRAWS: 0   TRAJECTORIES: 0
```

```
$ git diff --check
[clean]
```

---

## Execution state

```
execution_authorised = false

RANDOM DRAWS = 0
TRAJECTORIES = 0
CALIBRATION EXECUTION = NOT RUN
VALIDATION CAMPAIGN = NOT RUN
```

---

## Superseded package

The previous frozen pre-execution package — work commit `475633c`, report commit
`b4b2575` — was **execution-blocked** by G1–G3 and is superseded **prospectively** by this
closure. Neither commit is rewritten, amended or deleted, and
`docs/e1a/E1A_V4_SYNTHETIC_PREEXEC_REPORT.md` is retained as provenance. The old
identities are recorded inside the plan under `superseded_package.old_identities`.

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting local HEAD | `b4b25754b919d2583b0942115ba630d67535a50d` |
| **work commit** | `1a0c00ee3b0801d0a711c8088d93ae95a871e732` |
| **tree SHA** | `176602d1169dea86f7bd429b139f56affc81da12` |
| working tree after the work commit | **clean** |
| frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — **unchanged** |
| baseline text | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` — **unchanged** |

Committed files:

```
M	docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md
M	docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md
M	docs/e1a/e1a_v4_design_contract.json
M	docs/e1a/e1a_v4_seed_map.json
M	docs/e1a/e1a_v4_synthetic_validation_plan.json
M	docs/theory/EBU_THEORY_BASELINE.meta.json
M	e1a_v4/contract.py
A	e1a_v4/validation/dispositions.py
M	e1a_v4/validation/plan.py
A	test_e1a_v4_dispositions.py
M	test_e1a_v4_preexec.py
```

Generated after the work commit `1a0c00e` and committed separately, per the convention
in `docs/e1a/E1A_V4_ADOPTION_REPORT.md`.

---

## Next stage

```
E1a v4 synthetic validation EXECUTION
READY FOR AUTHORISATION
NOT STARTED
```

All three dispositions are closed, so no authority gap remains open. Execution requires a
separate authorisation that flips `execution_authorised`. Preregistration, physical
execution, E1b and Stage B remain unauthorised.

---

```
VALIDATION DISPOSITIONS FROZEN
```
