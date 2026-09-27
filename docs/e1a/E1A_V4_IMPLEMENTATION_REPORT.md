# E1a v4 — BOUNDED IMPLEMENTATION REPORT

Self-contained handoff for independent review. Complete without the originating
conversation.

---

## Result

**The bounded implementation is complete.** The adopted E1a v4 design is implemented in
a new `e1a_v4/` package with 119 deterministic checks, all passing. **No adopted design
rule changed** — every constant is read from the contract and none is typed into code.

**The stochastic synthetic-validation campaign was not run and is not authorised.**

---

## Repository preflight

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| starting local HEAD | `62083e2127219494621d9b18b01277a557664b77` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` |
| closure-report commit | `62083e2127219494621d9b18b01277a557664b77` |
| working tree at start | clean |

All unpushed ancestors audited, oldest first — every one is E1a design or report work,
and nothing outside `docs/e1a/` and `docs/theory/` is touched by any of them:

| commit | subject | disposition |
|---|---|---|
| `8c48103` | Record the E1a v4 design-correction report | 1 file added, documentation only |
| `c16eb6b` | Adopt corrected E1a v4 design | design + contract + validator + baseline repair |
| `fea828e` | Record the E1a v4 design-adoption handoff report | 1 file added |
| `f8a13fd` | Close E1a v4 pre-implementation review | C_V correction + report provenance |
| `62083e2` | Record the E1a v4 pre-implementation closure report | 1 file added |

No unexpected or unrelated commit appeared. Nothing was rewritten. Nothing pushed.

---

## Authority mapping

| design rule | implementation file | function / class |
|---|---|---|
| contract binding, fail-closed | `e1a_v4/contract.py` | `load_contract`, `ContractBinding` |
| procedure identity | `e1a_v4/identity.py` | `procedure_identity`, `procedure_preimage` |
| Branch-A field, anti-circularity | `e1a_v4/branch_a.py` | `BranchAField`, `build_field`, `assert_not_branch_b` |
| blinded scale control | `e1a_v4/branch_a.py` | `BranchAField.blinded` |
| Branch-B analysis | `e1a_v4/geometry.py` | `sample_covariance`, `rank_guard`, `analyse_field` |
| beta estimator | `e1a_v4/geometry.py` | `beta_mle` |
| G1–G4 | `e1a_v4/geometry.py` | `G1`, `G2`, `G3`, `G4` |
| G5 sample kurtosis | `e1a_v4/geometry.py` | `g2_per_mode`, `G5` |
| mode resolvability, θ_cap = 5° | `e1a_v4/geometry.py` | `resolvable`, `resolvability_blocks`, `resolvability_boundary_ratio` |
| finite-n correlation sums | `e1a_v4/effective_size.py` | `A_closed_form`, `A_from_sum`, `N_element`, `N_g2` |
| P1 two-block gate | `e1a_v4/endpoints.py` | `p1_geometry` |
| P2 cross-field | `e1a_v4/endpoints.py` | `p2_cross_field` |
| P3 absolute, all fields | `e1a_v4/endpoints.py` | `p3_absolute` |
| P4 deterministic check | `e1a_v4/endpoints.py` | `p4_consistency`, `declared_entropy_relation` |
| calibration artifact + identity | `e1a_v4/calibration.py` | `CalibrationArtifact`, `require_calibration`, `branch_a_signature` |
| structured refusal | `e1a_v4/status.py` | `AnalysisStatus` |
| future world configuration | `e1a_v4/world.py` | `WorldConfig`, `ForbiddenRNG` |
| seed-family separation | `e1a_v4/seeds.py` | `SeedFamily`, `SeedMap` |

`gaussian_harness`, `capacity_v2`, `demand_driven_ebu` and `homeostasis` are separate
registered model paths; none is imported, modified or reinterpreted. There was no prior
E1a code in the repository — the v1–v3 gate packages were never committed — so this is
the first E1a implementation, not a parallel second framework.

---

## Files changed

```
A	e1a_v4/__init__.py
A	e1a_v4/branch_a.py
A	e1a_v4/calibration.py
A	e1a_v4/contract.py
A	e1a_v4/effective_size.py
A	e1a_v4/endpoints.py
A	e1a_v4/geometry.py
A	e1a_v4/identity.py
A	e1a_v4/numerics.py
A	e1a_v4/seeds.py
A	e1a_v4/status.py
A	e1a_v4/world.py
A	test_e1a_v4.py
```

- `e1a_v4/__init__.py` — package identity, document paths, `k_B`, execution-class statement
- `e1a_v4/numerics.py` — float linear algebra and `Refusal`
- `e1a_v4/status.py` — `AnalysisStatus`
- `e1a_v4/contract.py` — contract loading and authority binding
- `e1a_v4/identity.py` — procedure identity
- `e1a_v4/branch_a.py` — Branch-A field and anti-circularity boundary
- `e1a_v4/effective_size.py` — finite-sampling correlation sums
- `e1a_v4/geometry.py` — Branch-B analysis and G1–G5
- `e1a_v4/calibration.py` — calibration schema, identity binding, p-values
- `e1a_v4/endpoints.py` — P1–P4
- `e1a_v4/world.py` — future synthetic-world configuration
- `e1a_v4/seeds.py` — seed-family separation
- `test_e1a_v4.py` — 119 deterministic checks

---

## Implemented mathematics

| result | classification |
|---|---|
| `S`, `K = S^-1`, `beta_hat = m/tr(H_A S)` | **EXACT** (definitions, up to floating-point rounding) |
| `H = H_U/(k_B T)` | **EXACT** (definition) |
| G1–G4 as functions of `(H_A, K)` | **EXACT**; their **null laws are not** |
| G5 statistic `g2 = m4/m2^2 - 3` | **EXACT** statistic; its finite-sample null is **NOT** exact |
| `A_p` finite-n closed form | **EXACT UNDER STATED ASSUMPTIONS** (stationary discrete AR(1)); verified against an explicit sum at n = 2, 3, 5, 17, 64, 257 |
| `N_ab` per element | **EXACT UNDER STATED ASSUMPTIONS**; the continuous `(T/2)(1/τ_a+1/τ_b)` form is its large-n limit and is **not used** |
| `var(g2) = 24 A4 / n`, `N_g2 = n/A4` | **APPROXIMATION** — leading-order delta method. The A2 cancellation is exact algebra *inside* that calculation, not a finite-sample distribution result |
| `bias(g2) = -6/N_2` | **APPROXIMATION** (leading order) |
| blinded scale control `beta -> beta/c` | **EXACT** (algebraic identity) |
| orientation entering beta at second order | **EXACT** for the population calculation |
| resolvability rule | **EXACT** rule; its operating characteristic **REQUIRES STOCHASTIC VALIDATION** |
| Besag–Clifford p-value | **EXACT UNDER STATED ASSUMPTIONS** — size ≤ α *conditional* on the draws coming from the true null; they come from a covariance-matched **surrogate**, so the unconditional size is **unvalidated** |
| block-2 analytic p | **APPROXIMATION** |
| P2 / P3 acceptance inequalities | **EXACT**; their uncertainty inputs are **first-order propagation approximations** |
| P4 | **EXACT UNDER STATED ASSUMPTIONS** |

Nothing is promoted to exact: not the surrogate calibration law, not the G5 delta-method
distribution, not plug-in calibration on measured `H_A`, not the finite-sample beta
uncertainty, not the mode-boundary operating characteristics.

---

## P1

Two-block union-valid gate, implemented in `p1_geometry`:

```
reject  iff  p_min(G1..G4) < critical_p_min(alpha_1)   OR   p(G5) < alpha_2
alpha_1 = 0.004   alpha_2 = 0.001   alpha_geom = 0.005
```

The union bound is valid under **arbitrary dependence** between the blocks. **No
independence is asserted between Block 1 and Block 2, and none is needed.** Block 1's
four-way dependence is carried exactly by the paired null draws in one artifact.

```
STOCHASTIC NULL CALIBRATION NOT RUN
```

`require_calibration` refuses when the artifact is absent, when it was produced under a
different procedure identity, or when its geometry signature differs from the analysed
`H_A`. **No threshold is hard-coded and no v3 value is substituted.** The artifacts used
in the tests are hand-written fixtures carrying `is_fixture=True`; they exercise decision
semantics and are not calibration.

---

## P2

```
r_j  = beta_hat_j / beta_hat_ref
h_j  = z_cross * sqrt( 2 sigma_fs^2 + sigma_stat_j^2 + sigma_stat_ref^2 )
accept j  iff  r_j (1 - h_j) >= 1 - delta_cross  AND  r_j (1 + h_j) <= 1 + delta_cross
P2 passes  iff  all three comparisons accept
delta_cross = 0.02    z_cross = 1.959963985    no Bonferroni (intersection-union)
```

The full interval must lie inside `[0.98, 1.02]`. This is **not** "the CI contains 1" and
**not** "p > 0.05" — a test asserts exactly that, showing a ratio of exactly 1 with a wide
interval **fails**. `sigma_cm` cancels in the ratio and does not appear. A non-estimated
comparison field or a non-estimated reference fails P2 closed.

---

## P3

```
h_theta = z_abs * sqrt( sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2 )
accept theta  iff  beta_hat_theta (1 - h_theta) >= 1 - delta_abs
              AND  beta_hat_theta (1 + h_theta) <= 1 + delta_abs
P3 passes  iff  ALL FOUR declared fields accept
delta_abs = 0.05    z_abs = 1.959963985
```

One field outside 5% fails P3. One non-`ESTIMATED` field fails P3. **Reference-only
success is insufficient** — a test asserts that a run where only the reference passes
still fails.

---

## P4

```
DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK
```

`p4_consistency` takes no observations — its signature contains no Branch-B parameter,
and a test asserts that. On declared constants only it verifies

```
ds_med = + k_B E     identical across tested temperatures though the heat differs
ds_sys = - k_B E
ds_tot = 0
```

At `E = +5`: heat `2.057167e-20 J` at 298 K and `2.195232e-20 J` at 318 K — a 6.71%
difference — while `ds_med` is `+5.0000 k_B` at both. The constrained-macrostate statement
stays separate and symbolic, `Delta S_constr = k_B E + O(U^2/(T^2 C_V))`.
`Delta S_total = k_B E` is **not** reintroduced anywhere. Tests confirm P4 **fails** on a
deliberately altered relation and on a sign error in `ds_sys`.

**Passing P4 is not experimental confirmation of entropy production.**

---

## Branch separation

Anti-circularity is a **type boundary**, not a convention:

- `build_field` refuses any route on the contract's forbidden list — power spectrum,
  **corner frequency** `k = 2 pi f_c gamma`, equipartition — and refuses any route not on
  the authorised list rather than assuming it is acceptable;
- authorised routes are exactly `force_displacement_with_stokes_drag` and
  `independent_calibrated_thermometry`, read from the contract;
- `assert_not_branch_b` refuses any object exposing `sample_covariance`, `S`, `K`,
  `beta_hat`, `observations` or `positions`, so a Branch-B statistic cannot be passed in
  as stiffness;
- Branch B **consumes** observations and never generates them: `geometry.py` has no RNG.

---

## Refusal semantics

`AnalysisStatus`: `ESTIMATED`, `BRANCH_A_INVALID`, `NON_POSITIVE_DEFINITE`,
`RANK_GUARD_FAIL`, `N_EFF_UNSUPPORTED`, `MODE_UNRESOLVED`, `CALIBRATION_MISSING`,
`CALIBRATION_IDENTITY_MISMATCH`, `GEOMETRY_FAIL`, `ANALYSIS_INVALID`.

NaN is never a scientific status. A refused analysis carries **no** `beta_hat` at all, and
`FieldAnalysis.require_beta()` raises rather than returning a placeholder — the historical
unconditional `result["beta_hat"]` crash path cannot recur. Every downstream endpoint
fails closed on a non-estimated field.

---

## Effective sample-size treatment

`phi = exp(-dt/tau)` per mode, with `tau_r = gamma(T)/k_r` from Branch A — never one
scalar for an anisotropic field.

- **second moments** (S, K, beta, G1–G4) use `A` over `x = phi_a * phi_b`, giving a
  per-element `N_ab`; the diagonal is the `A2` case `x = phi_r^2`;
- **G5** uses `A` over `x = phi_r^4`, giving `N_g2 = n/A4`.

Tests confirm the closed form equals an explicit finite sum at n = 2, 3, 5, 17, 64, 257;
that θ2's two modes have genuinely different effective sizes (333,934 vs 134,632); that
the cross element lies between the diagonals; and that `N_g2/N_2 ≈ 1.946`, matching the
adopted design's ≈ 2.

---

## Mode resolvability

```
merge  iff  (rho - 1)/sqrt(rho)  <  1 / ( theta_cap_rad * sqrt(N_12) )
theta_cap = 5 degrees
```

Boundary convention: **equality merges** — resolvability requires a strict inequality.
At `N_12 = 224,726` the boundary ratio is **1.024467**, matching the adopted design's
1.0245. Fixtures cover a perfectly circular field, slightly below the boundary, exactly at
the boundary, slightly above, and a strongly elliptical θ2-like field at ρ = 2.5. An
unresolved pair forms one block and contributes **subspace** principal angles; no
direction is inferred for an individually unresolved mode.

---

## Procedure identity

Canonicalisation, exactly as implemented:

1. build a mapping with these keys and no others — `implementation_identity`,
   `contract_sha256`, `design_sha256`, `foundation_sha256`, `baseline_sha256`,
   `code` (relative path → sha256 for each of the 12 scientific modules, sorted),
   `analysis_rules` (adopted values read from the contract, sorted),
   `configuration`, `seed_map_schema`;
2. `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=True)`;
3. sha256 of the UTF-8 encoding.

No seed **values** enter at this stage; only the schema does.

```
procedure identity (configuration {"stage": "bounded_implementation"}):
8dd48f42f7ccd259a76e50ef4e1ee4c0a3c5b43986bc54d75438b1acdf15dbe0

design contract sha256:
89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c
```

Tests confirm identical inputs give an identical identity and that a changed relevant
input changes it.

---

## Deterministic validation

```
$ python3 test_e1a_v4.py

contract binding
  [PASS] valid contract accepted and bound to all three authority documents  -- contract sha 89a935dd98b0, foundation 6d9aed244019
  [PASS] adopted constants read from contract, not typed
  [PASS] z_cross == z_abs == 1.959963985
  [PASS] modified constant is READ, not overridden by code  -- the design wins; implementation never substitutes its own value
  [PASS] reintroduced Bonferroni rejected
  [PASS] P3 narrowed to the reference field rejected
  [PASS] incoherent alpha split rejected
  [PASS] bad foundation hash rejected (fail closed)
  [PASS] design identity mismatch rejected
  [PASS] missing mandatory endpoint rejected
  [PASS] unsupported contract version rejected

beta estimator
  [PASS] hand-written points reproduce sigma exactly
  [PASS] ideal beta = 1 recovered exactly  -- 1.000000000000000
  [PASS] beta_true=0.75 recovered, estimate never forced to 1
  [PASS] beta_true=1.3 recovered, estimate never forced to 1
  [PASS] scalar H scaling: beta_hat halves exactly
  [PASS] differential stiffness with zero mean leaves beta exactly unchanged  -- 1.000000000000
  [PASS] mean stiffness error moves beta by 1/(1+delta_bar)
  [PASS] orientation error enters beta only at second order, exactly  -- 0.999862954863 vs 0.999862954863
  [PASS] rank-deficient S refused, not regularised

G1-G5 geometry
  [PASS] G1 deterministic fixture  -- 0.035238095238095
  [PASS] G2 deterministic fixture  -- 1.165935010017951
  [PASS] G4 deterministic fixture  -- 0.114033105039501
  [PASS] G3 deterministic fixture  -- 4.065051177078
  [PASS] G5 deterministic fixture  -- 0.961945787584
  [PASS] G1 scale-invariant in H
  [PASS] G2 scale-invariant in H
  [PASS] G3 scale-invariant in H
  [PASS] G4 scale-invariant in H
  [PASS] G5 scale-invariant in H
  [PASS] G5 is the kurtosis estimator, not a raw fourth moment  -- a two-valued coordinate has g2 = m4/m2^2 - 3 = -2 exactly; a raw fourth moment would give 1.0
  [PASS] G5 refuses a degenerate whitened coordinate rather than returning NaN

mode resolvability
  [PASS] boundary ratio matches the adopted design  -- 1.024467 at theta_cap=5.0 deg
  [PASS] perfectly circular field is merged
  [PASS] slightly below boundary merged
  [PASS] exactly at boundary merged (equality merges)
  [PASS] slightly above boundary resolved
  [PASS] strongly elliptical theta2-like field resolved
  [PASS] circular field gives ONE block, no inferred directions
  [PASS] elliptical field gives TWO blocks

status propagation
  [PASS] valid analysis reaches ESTIMATED
  [PASS] ESTIMATED result exposes beta
  [PASS] rank failure yields RANK_GUARD_FAIL
  [PASS] no beta on a refused analysis
  [PASS] require_beta fails closed instead of crashing on a missing key
  [PASS] non-positive-definite Branch A yields BRANCH_A_INVALID

effective sample size
  [PASS] closed form == finite sum (n=2, x=0.0)
  [PASS] closed form == finite sum (n=2, x=0.25)
  [PASS] closed form == finite sum (n=2, x=0.5)
  [PASS] closed form == finite sum (n=2, x=0.81873)
  [PASS] closed form == finite sum (n=3, x=0.0)
  [PASS] closed form == finite sum (n=3, x=0.25)
  [PASS] closed form == finite sum (n=3, x=0.5)
  [PASS] closed form == finite sum (n=3, x=0.81873)
  [PASS] closed form == finite sum (n=5, x=0.0)
  [PASS] closed form == finite sum (n=5, x=0.25)
  [PASS] closed form == finite sum (n=5, x=0.5)
  [PASS] closed form == finite sum (n=5, x=0.81873)
  [PASS] closed form == finite sum (n=17, x=0.0)
  [PASS] closed form == finite sum (n=17, x=0.25)
  [PASS] closed form == finite sum (n=17, x=0.5)
  [PASS] closed form == finite sum (n=17, x=0.81873)
  [PASS] closed form == finite sum (n=64, x=0.0)
  [PASS] closed form == finite sum (n=64, x=0.25)
  [PASS] closed form == finite sum (n=64, x=0.5)
  [PASS] closed form == finite sum (n=64, x=0.81873)
  [PASS] closed form == finite sum (n=257, x=0.0)
  [PASS] closed form == finite sum (n=257, x=0.25)
  [PASS] closed form == finite sum (n=257, x=0.5)
  [PASS] closed form == finite sum (n=257, x=0.81873)
  [PASS] anisotropic field: modes have DIFFERENT effective sizes  -- 333934 vs 134632
  [PASS] cross element uses phi_a*phi_b, lying between the diagonals
  [PASS] second moments use A2 (x = phi^2)
  [PASS] G5 uses A4 (x = phi^4)
  [PASS] N_g2 is about twice N_2, as the adopted design records  -- ratio 1.946
  [PASS] var(g2) = 24/N_g2
  [PASS] sigma_stat positive and small at the declared record length  -- 0.2283%

P1 decision semantics
  [PASS] P1 refuses when calibration is ABSENT  -- no hard-coded threshold, no v3 substitution
  [PASS] fixture artifact accepted when identities match
  [PASS] artifact from a different procedure identity refused
  [PASS] artifact calibrated at a different geometry refused
  [PASS] block-2 p-value is a number in [0,1]
  [PASS] block-2 p-value shrinks as G5 grows
  [PASS] union bound: alpha_1 + alpha_2 == alpha_geom, no independence asserted

P2 cross-field
  [PASS] P2 clear pass when every ratio is 1
  [PASS] P2 clear fail at a 10% disparity
  [PASS] P2 one failing comparison fails the whole endpoint  -- intersection-union: all three required
  [PASS] P2 boundary convention: interval must lie WHOLLY inside the margin
  [PASS] P2 fails closed on a non-estimated comparison field
  [PASS] P2 fails closed on a non-estimated REFERENCE
  [PASS] P2 is equivalence, not 'CI contains 1': a wide interval FAILS  -- ratio exactly 1 but the interval overflows the margin

P3 absolute
  [PASS] P3 all four fields pass
  [PASS] P3 one field outside 5% fails the endpoint
  [PASS] P3 one non-estimated field fails the endpoint
  [PASS] P3 reference alone passing is insufficient  -- every tested field is required
  [PASS] P3 evaluates all four declared fields

P4 deterministic check
  [PASS] P4 declared consistency relation passes
  [PASS] P4 needs no Branch-B observations
  [PASS] P4 fails on a deliberately altered relation
  [PASS] P4 fails when ds_sys loses its sign
  [PASS] ds_med identical across temperatures though the heat differs  -- ds_med 5.0000 k_B at both T; heat differs by 6.71%

procedure identity
  [PASS] same inputs -> same procedure identity  -- 8dd48f42f7ccd259...
  [PASS] relevant changed input -> different identity
  [PASS] identity is a sha256 hex digest

information boundary
  [PASS] Branch-A construction refuses an object carrying Branch-B output
  [PASS] forbidden corner-frequency route refused
  [PASS] forbidden equipartition route refused
  [PASS] unlisted route refused rather than assumed
  [PASS] blinded scale control recovers beta = 1/c exactly  -- 0.729927007299 vs 0.729927007299
  [PASS] blinding does not mutate the primary field

no stochastic execution
  [PASS] world config computes per-mode tau deterministically
  [PASS] stationary covariance available without any draw
  [PASS] stationary initial distribution is a SPECIFICATION, not a draw
  [PASS] the only available RNG refuses every call
  [PASS] trajectory generation refuses
  [PASS] no seed values assigned in this stage
  [PASS] a consumer cannot read another family's stream
  [PASS] a family may read its own stream
  [PASS] duplicate seeds across families refused

E1a v4 implementation gate: 119 passed, 0 failed, 13 groups
Execution class: NON-MODEL-ADVANCING STATIC/PURE (this suite only)
  contract sha256      : 89a935dd98b08a13c9fca62ae6b8b12c8f76297df6d87a62877716bbed45600c
  procedure identity   : 8dd48f42f7ccd259a76e50ef4e1ee4c0a3c5b43986bc54d75438b1acdf15dbe0
  stochastic calibration: NOT AUTHORISED IN THIS STAGE
  synthetic campaign    : NOT AUTHORISED IN THIS STAGE
  random numbers drawn  : 0
  trajectories generated: 0
```

```
$ python3 docs/e1a/validate_e1a_v4_contract.py

============================================================================
  113 / 113 checks passed
============================================================================
```

```
$ git diff --check
[clean]
```

| | |
|---|---|
| implementation checks passed | **119** |
| implementation checks failed | **0** |
| design-authority checks passed | **113** |
| design-authority checks failed | **0** |
| tests skipped | **0** |
| stochastic work | **NOT AUTHORISED IN THIS STAGE** |

Residuals: exact-covariance fixtures recover beta to `< 1e-12`; scale invariance holds to
`≤ 1e-12`; `A_closed_form` matches the explicit sum to `< 1e-12`; the orientation
second-order prediction matches to `< 1e-9`.

---

## Explicitly unexecuted stochastic work

Every item below is deferred to the next authorised stage and none is disguised as a unit
test:

- Block-1 min-p **null calibration** — the schema, identity binding, p-value consumption
  and decision semantics exist; the draws do not;
- Monte-Carlo calibration of any gate;
- OU trajectory generation and stepping — `ForbiddenRNG` refuses every call;
- stationary **initial-state drawing** — the specification exists, the draw does not;
- the synthetic eight-case campaign;
- power simulations and type-I simulations;
- false-bridge stochastic controls;
- the blinded **stochastic** control — the algebra is tested on hand-written matrices only;
- seed-value assignment for any family;
- validation of the surrogate calibration law at the operating quantile;
- validation of plug-in conditioning on `H_A`;
- `theta_cap` boundary size and power;
- G5 block delta-method error quantification;
- any real, laboratory or apparatus data.

**Random numbers drawn: 0. Trajectories generated: 0.** The provisional analytical figure
0.9055 is **not** used as a software-test expected value anywhere; whether the implemented
pipeline achieves the ≥ 0.90 target is exactly what the future stochastic validation must
decide.

---

## Git identity

| | |
|---|---|
| branch | `gaussian/stage-a-environment` |
| remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` — **not pushed** |
| starting local HEAD | `62083e2127219494621d9b18b01277a557664b77` |
| **work commit SHA** | `e4b73d7fbd84d329f4326af443fd1918bc44a874` |
| **work tree SHA** | `6e6c2e696a7b9fe43412810725865eb222a08eb7` |
| parent | `62083e2127219494621d9b18b01277a557664b77` |
| working tree after the work commit | **clean** |
| frozen foundation sha256 | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` — **unchanged** |

No commit was amended. No history was rewritten. Nothing was pushed.

---

## Report provenance

Generated **after** the work commit `e4b73d7` and committed separately, per the
convention recorded in `docs/e1a/E1A_V4_ADOPTION_REPORT.md`. No SHA in this document was
asserted before it existed.

---

## Next possible stage

```
E1a v4 synthetic validation campaign
READY FOR AUTHORISATION
NOT STARTED
```

It requires separate authorisation. Preregistration, physical execution, E1b and Stage B
all remain unauthorised.

---

```
BOUNDED IMPLEMENTATION COMMITTED
```
