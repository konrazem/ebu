# E1a v4 — PROSPECTIVE DESIGN

**Authoritative prospective design for the E1a canonical Einstein–EBU benchmark.**

This document and its machine-readable counterpart `e1a_v4_design_contract.json` are the
authoritative prospective sources for the E1a v4 statistical design. They supersede, for E1a,
every conversational decision and every scratchpad artifact. Where this document and the
contract disagree, that is an integrity failure requiring fail-closed refusal, not a licence to
choose one selectively; the JSON is the mechanical schema and ordering source and this Markdown
is its normative human rendering.

**Authority rank.** Below the frozen physical foundation and below the working theory baseline.
This document introduces no physical theory. It fixes decision rules for one benchmark
experiment. Any conflict with
`docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` is resolved in favour of the
foundation; any conflict with `docs/theory/EBU_THEORY_BASELINE.md` on scientific content is
resolved in favour of the baseline.

**Status.** DESIGN ADOPTED PROSPECTIVELY. Implementation not started. Synthetic validation not
started. Preregistration not authorised. No physical execution.

---

## 1. Scientific question

Do independently measured physical-field geometry and independently measured statistical
geometry agree with **one scale factor** across the declared E1a field conditions?

```
K_theta = beta H_theta        one field-independent beta over the four declared fields
```

`H_theta` is the independently specified physical potential curvature. `K_theta` is the
independently observed probability-rarity curvature. `beta` is the proposed common conversion.

Thermal normalisation, preserved from baseline §14.1 (committed):

```
V_theta(x) = [ U_theta(x) - U_theta(x*_theta) ] / (k_B T_theta)
H_theta    = H_U,theta / (k_B T_theta)
sigma_r,theta^2 = k_B T_theta / k_r,theta
```

**E1a predicts `beta = 1` and `kappa = k_B` at every tested field.** That prediction is
benchmark-specific. It is not a universal EBU theorem.

`beta` is estimated from the measurement branches. **The reported estimate is never constrained
to equal the prediction.**

---

## 2. Information separation

**BRANCH A — physical field.** `U_theta` from mechanical force–displacement data; `T_theta` from
independent calibrated thermometry. Branch A never uses the position histogram.

**BRANCH B — statistics.** `P_theta` from position observations; derives `J_prob` and `K`.
Branch B never uses `V` or `H`.

Branch-A output is hashed and published **before** Branch B is unblinded.

### 2.1 Forbidden Branch-A calibration routes

| route | status |
|---|---|
| power-spectrum stiffness calibration | **FORBIDDEN** — baseline §14, committed. It uses the fluctuation data and closes the circular loop |
| **corner-frequency / fluctuation-spectrum route**, `k = 2 pi f_c gamma` | **FORBIDDEN for E1a** — it is the power-spectrum method under another name and reads the same fluctuation dataset Branch B tests |
| equipartition, `k = k_B T / sigma^2` | **FORBIDDEN** — it makes `beta = 1` a tautology |
| force–displacement with Stokes drag | **AUTHORISED** — baseline §14, committed |
| independent calibrated thermometry for `T_theta` | **AUTHORISED** — baseline §14, committed |

> **SUPERSESSION NOTICE.** `docs/e1a/E1A_V4_REPORT.md` at commit `8c48103` (Part II, §5.6)
> describes "Stokes-drag / corner-frequency (`k = 2 pi f_c gamma`)" as an independent
> calibration route. **That statement is superseded for E1a.** The corner-frequency branch of it
> is forbidden here. The historical artifact is deliberately not rewritten; this notice records
> the supersession.

### 2.2 Accessible directions and coordinates

Lateral `x`/`y` plane accessible. The axial `z` direction is **designed out and documented as
discarded** — never treated as an observed zero-curvature mode. Coordinates and normalisation
are fixed before unblinding and are never altered after inspecting agreement.

---

## 3. The four declared fields

| id | change | `k` (µN/m) | `T` (K) | rotation | reference | prediction |
|---|---|---|---:|---:|:--:|---|
| `theta0_circular` | baseline | 100, 100 | 298 | 0° | **yes** | `K = H`, `beta = 1` |
| `theta1_power` | laser power / stiffness | 210, 210 | 298 | 0° | no | `beta = 1` |
| `theta2_ellipse` | ellipticity / mode rotation | 150, 60 | 298 | 30° | no | `K` and `H` rotate together, `beta = 1` |
| `theta3_temperature` | temperature | 100, 100 | 318 | 0° | no | `beta = 1`, `kappa = k_B` unchanged |

Temperature is **not** a positive control for β-change. It is the strongest changing-field
commensurability test.

Per-field Branch-A relaxation times are `tau_r = gamma(T)/k_r` with `gamma = 6 pi eta(T) a`.
A single `tau_c` for all fields is **wrong** and is not used: `tau` depends on `k` and, through
`eta(T)`, on temperature.

### 3.1 Branch-A measured input domain — ADOPTED PROSPECTIVELY (disposition G6)

The relation above fixes the **form** of the drag coefficient. It never stated the admissible
domain of the two measured quantities that relation consumes, while §14 already fixed the
admissible domain of the measured stiffness. That asymmetry is closed here, **before any
official campaign job, trajectory or outcome existed**.

**The rule.**
For every E1a field, the Branch-A dynamic-viscosity input eta(T_theta) must be a finite real number strictly greater than zero. The bead-radius input a must be a finite real number strictly greater than zero.

```
eta(T_theta) in R ,   0 < eta(T_theta) < infinity        Pa s
a            in R ,   0 < a            < infinity        m
```

**"Finite real"** means of the declared real numeric representation, and not NaN, not +infinity and not -infinity. A truthy or non-numeric representation is not a number and is never admissible.

**The rule binds each primitive individually.**
eta and a are each authoritative domain objects and are validated INDIVIDUALLY. A rule stated only on the product gamma is INSUFFICIENT: eta < 0 together with a < 0 gives gamma = 6 pi eta a > 0 and would masquerade as an admissible passive-drag construction. Neither eta nor a is persisted in the Branch-A publication preimage, so no downstream check can recover them.

A rule stated only as `gamma > 0`, or only as `tau_r > 0`, is therefore recorded as
**insufficient** rather than as an alternative formulation of this one.

**Missing input and inadmissible input are different states.**

| state | meaning | verdict |
|---|---|---|
| `eta` or `a` absent, undeclared, or not supplied through the authorised field-construction source | we do not possess the required physical input | `UNDECLARED_FIELD_INPUTS` |
| `eta` or `a` present and nonfinite, zero or negative | we possess a value, but it is outside the admissible physical domain | `REFUSED_BRANCH_A_INVALID` |

The two are never conflated: an absent input is not a value that failed a domain test.
A neutral placeholder value MAY NOT substitute for the actual required measured field-construction input in any path that can produce an official valid Branch-A package. The existing UNDECLARED_FIELD_INPUTS lifecycle is preserved.

**`gamma` and `tau` are DERIVED.** With `gamma(T_theta) = 6 pi eta(T_theta) a` and `tau_r = gamma(T_theta)/k_r` unchanged,
admissible primitives give a finite, strictly positive `gamma`; together with the
already-explicit `lambda_r > 0` requirement of §14 every `tau_r` is then finite and strictly
positive. These are **consequences of one decision and one existing rule**, not four unrelated
positivity choices, and neither is an independent physical sign convention.

**Physical admissibility and executable representability are distinct.** Primitives may be
physically admissible while the computed binary64 `gamma` or `tau` underflows, overflows or is
otherwise unrepresentable. That case keeps the existing `BRANCH_A_MEASUREMENT_INVALID` semantics
and is **never** relabelled as an invalid `eta` or `a` measurement; the PHYSICAL-DOMAIN check on eta and a PRECEDES the numerical representability checks on the derived gamma and tau. The two are never conflated and neither is ever substituted for the other.
The previously cleared binary64 drag-representability, common-representable-`gamma`,
underflow/overflow, ties-to-even and relaxation-representability rules are **unchanged** by this
amendment.

**Consequence.**
A present but inadmissible primitive drag input can NEVER yield a VALID Branch-A status, a valid Branch-A publication, a valid calibration condition, a valid calibration lock or a valid Branch-B input. This is DERIVED from the existing REFUSED_BRANCH_A_INVALID lifecycle and introduces no second lifecycle.

**Stiffness is not reopened.** `H not symmetric / not positive definite / dimension mismatch -> REFUSED_BRANCH_A_INVALID` remains exactly as §14 states it.
Every retained mode satisfies lambda_r > 0; lambda_r < 0 and lambda_r = 0 were already invalid and are NOT reopened by this amendment. No negative-stiffness category and no "valid unstable trap" branch is
created here.

**Scope.** This is a statement about the declared E1a passive equilibrium optical-trap benchmark ONLY. This is NOT a universal physical assertion: negative effective viscosity, negative effective transport coefficients and active-matter effective parameters are OUTSIDE this benchmark, not denied by it.

**What this does not declare.** The actual dynamic viscosity values, the viscosity model
`eta(T)`, the actual bead radius, measurement uncertainty for either, and their hardware
provenance. Those remain **F4 - field construction / absolute drag inputs**, which is **OPEN**. This amendment
supplies an admissible domain and nothing else, and does not make field construction
execution-ready.

---

## 4. Beta target and estimator

```
beta_hat = m / tr(H_A S)
```

`H_A` is the Branch-A curvature estimate; `S` is the Branch-B sample covariance about the
declared `x*`. Exact finite-sample identity, with `G := H_true^{-1/2} H_A H_true^{-1/2}` and `M`
the whitened sample covariance:

```
beta_hat = m beta / tr(G M)
```

The population limit `M -> I` gives `beta_hat_pop = m beta / tr(G)`; for mode-scaling errors
`delta_r` this is `beta / (1 + delta_bar)`, i.e. **only the mean of the per-mode errors enters
beta**. That is a population result describing one component of measurement error, **not** the
complete finite-sample estimator.

---

## 5. P1 — geometry gate

Five statistics, computed against the independently supplied Branch-A `H_A`:

| gate | statistic |
|---|---|
| G1 | trace-normalised shape difference between `H` and `K` |
| G2 | whitened spectral spread, eigenvalue ratio of `H^{-1/2} K H^{-1/2}` |
| G3 | principal angles between eigen-directions, with degeneracy blocks |
| G4 | eigenvalue-ratio agreement |
| G5 | fourth-moment gate, `g2_r = m4_r/m2_r^2 - 3`, `G5 = max_r |g2_r|`, on `Z = H^{1/2}(x - x*)` |

**Two-block union-valid procedure.** Independence between the blocks is **not asserted**:

```
reject  iff  p_min(G1..G4) < alpha_1   OR   p(G5) < alpha_2
alpha_geom = alpha_1 + alpha_2 = 0.005        union bound, valid under ARBITRARY dependence
alpha_1 = 0.004   (G1-G4 block)
alpha_2 = 0.001   (G5 block)
```

Block 1's four-way dependence is exact within the calibration model, because all four are
deterministic functions of `(H_A, S)` and share one draw of `S`. G5 is not a function of `S` and
cannot be produced from it; it is calibrated separately and combined by the union bound.

**All five gates are invariant to multiplying `H` by a positive scalar.** Verified against the
implementation to `<= 6.7e-16`. The modelled scalar calibration errors therefore move `beta`
only, never the gates.

---

## 6. P2 — cross-field commensurability

**Margin `delta_cross = 2%`, preserved exactly.**

```
r_j  = beta_hat_j / beta_hat_ref                         j over the three non-reference fields
h_j  = z_cross * sqrt( 2 sigma_fs^2 + sigma_stat,j^2 + sigma_stat,ref^2 )
accept comparison j  iff  r_j (1 - h_j) >= 1 - delta_cross  AND  r_j (1 + h_j) <= 1 + delta_cross
P2 passes iff every one of the three comparisons accepts
z_cross = 1.959963985
```

**This is an INTERSECTION–UNION equivalence test.** Requiring all three comparisons to accept
controls the size at the per-comparison level without any multiplicity adjustment, so
**no Bonferroni correction is applied**.

The 2% margin is a **per-comparison two-sided equivalence tolerance on the ratio to the common
reference field, applied conjunctively**. It is **not** a pooled tolerance, **not** an all-pairs
tolerance, and **not** a tolerance on absolute beta. `delta_cross` and `delta_abs` are different
requirements and are never merged.

`sigma_cm` cancels exactly in the ratio and does not appear in `h_j`.

---

## 7. P3 — absolute E1a calibration

**P3 is MANDATORY and applies to EVERY tested field.**

```
h_theta = z_abs * sqrt( sigma_cm^2 + sigma_fs^2 + sigma_stat,theta^2 )
accept theta  iff  beta_hat_theta (1 - h_theta) >= 1 - delta_abs
              AND  beta_hat_theta (1 + h_theta) <= 1 + delta_abs
P3 passes iff every one of the four fields accepts
delta_abs = 0.05 ,  z_abs = 1.959963985
```

Conjunctive over all four fields — again an intersection–union test, so no multiplicity
adjustment. **Any field whose `beta_status` is not `ESTIMATED` makes P3 fail.** Fail-closed; no
conditioning on surviving fields.

### 7.1 Provenance of the 5% band — recorded plainly

- `delta_abs = 5%` is **prospectively adopted here, for E1a v4.**
- It was **never historically committed authority.** Its only prior written appearance is an
  uncommitted scratch configuration.
- **Adoption occurs before any stochastic validation and before any physical execution.**
- The earlier rule evaluated the reference field only, which does not test the committed
  prediction of `beta = 1` at every field. The all-field rule adopted here replaces it.

---

## 8. P4 — deterministic consistency check

**Classification: `DETERMINISTIC PHYSICAL/THEORETICAL CONSISTENCY CHECK`.**

P4 evaluates a closed-form identity on **declared constants**. It never reads Branch-B data,
`H_A`, or any estimate. It is **mandatory** as a design consistency check and is **not dropped**.

Because it is deterministic, once it has passed it **contributes no stochastic failure
probability** to the complete-pipeline budget.

> **Its algebraic pass is not experimental evidence** and must never be reported as such.

What P4 checks, in the corrected wording of §9 below: that under the declared static-equilibrium
conditions `Delta s_med = +k_B E_theta` is identical across the tested temperatures although the
mechanical energies differ, and that `Delta s_tot = 0`.

---

## 9. Entropy interpretation

Four **distinct** objects. They are never equated.

| object | value under the declared conditions | nature |
|---|---|---|
| medium entropy change `Delta s_med` | `+k_B E_theta` | process quantity, no-work transitions only |
| stochastic system entropy `Delta s_sys` | `-k_B E_theta` | trajectory quantity |
| **total stochastic entropy production** `Delta s_tot` | **`0`** | **not `k_B E`** |
| constrained-macrostate entropy deficit `Delta S_constr` | `k_B E_theta` + remainder | state function, separate derivation |

Conditions required for the cancellation — all of them:

1. the declared overdamped Langevin model with a **conservative** force `F = -grad U`;
2. **fixed field** — static `U`, no time-dependent driving;
3. **fixed temperature**, a single reservoir;
4. the system in the **stationary equilibrium distribution** at both times;
5. **no additional work input omitted from the accounting.**

Under (1)–(5) these are **trajectory identities**, exact realisation by realisation. They are
distinct from the ensemble-average entropy-production rate statement, which bounds
`<s_tot_dot> >= 0` with equality exclusively in equilibrium.

**No generalisation** is claimed to imposed actor actions, driven transitions, or nonequilibrium
initial distributions: each violates condition (2), (4) or (5).

### 9.1 Constrained-macrostate object, with its own derivation

**Ensemble and boundary assumptions.** Composite of bead + a single thermal reservoir with
**total energy fixed** (microcanonical composite). The bead is **held at `x`** by an external
constraint, so its configurational entropy at fixed `x` is an `x`-independent constant and drops
out of the difference. The reservoir holds `E_tot - U(x)`. Its temperature is **defined** by
`dS_res/dE|_V = 1/T`, and the second derivative is taken **at constant volume**,
`d2S_res/dE2|_V = -1/(T^2 C_V)`. Large-reservoir regime: `C_V` finite but `C_V >> U/T`.

**Both derivatives are constant-volume quantities, so `C_V` is the correct heat capacity.
Substituting `C_P` is not licensed by the derivation.**

```
Delta S_constr = k_B E_theta + O( U^2 / (T^2 C_V) )

epsilon_bath   ~  U / (2 T C_V)
```

**This result is authoritative in symbolic form only.** No numerical heat-capacity value is part
of the E1a design, and **no E1a decision rule depends on one**. An order-of-magnitude
illustration for one concrete reservoir, including a properly derived `C_V` and the quantified
size of the `C_P`/`C_V` gap, is in the **non-normative** explanatory note
`docs/e1a/finite_bath_remainder.py`.

> **CORRECTION NOTICE.** `docs/e1a/E1A_V4_REPORT.md` at commit `8c48103` contains a units error:
> it treated 1 mm³ and 1 µL as different volumes (the row labelled "1 µL" used `1e-9 * 1e3` m³,
> which is 1 mL), and estimated the heat capacity of liquid water by a generic `3 N k_B`
> Dulong–Petit expression that is not justified for a liquid. A first correction pass then used
> `c_P`, which is inconsistent with a derivation that calls for `C_V`. Both are corrected: the
> authoritative statement here is symbolic in `C_V`, and the numerical illustration has been
> moved to the non-normative note. **This quantity is not a statistical endpoint.**

---

## 10. Mode-resolution rule

Two modes are merged into one degeneracy block when their eigen-directions are **not resolvable**:

```
merge  iff  (rho - 1)/sqrt(rho) < 1/( theta_cap * sqrt(N_12) )
theta_cap = 5 degrees          PROSPECTIVE DESIGN SETTING
```

`rho` is the Branch-A eigenvalue ratio and `N_12` the per-element effective size. Branch-A only,
`N`-dependent, and non-arbitrary in form.

`theta_cap = 5°` is chosen because the merge decision reads **noisy** `H_A`: for a truly circular
field the estimated ratio is `1 + |delta_1 - delta_2|`, and at `sigma_k = 0.34%` the probability
of splitting a truly circular field is `4.98e-07` at 5°, against `1.19e-02` at 10° and `2.09e-01`
at 20°. It merges genuine splits only below `rho = 1.0245`; `theta2` sits at `rho = 2.5`.

> **`theta_cap = 5°` remains subject to future size/power validation around its boundary**
> (`rho = boundary ± 20%`). It is adopted prospectively, not validated.

---

## 11. Hypothetical uncertainty scenario

**Every value in this section is a HYPOTHETICAL INSTRUMENT SCENARIO for synthetic validation.
None is a measured apparatus capability. None is a necessary instrument limit.**

| symbol | meaning | scenario value |
|---|---|---:|
| `sigma_k` | per-mode stiffness calibration, independent per mode | 0.34% |
| `sigma_T` | thermometry | 0.1 K |
| `sigma_fs` | field-specific, **derived** `sqrt(sigma_k^2/m + (sigma_T/T)^2)` | 0.242747% |
| `sigma_cm` | common-mode calibration, one draw per experiment | 1.15% |
| `sigma_psi` | Branch-A trap-axis orientation | **0.5°** primary; grid {0.0, 0.2, 0.5, 1.0}° |
| `T_total` | record length per field | 240 s |
| `dt` | sampling interval | 1.2e-4 s |

Which term limits what:

| uncertainty | cross-field ratio | absolute beta | gates |
|---|:--:|:--:|:--:|
| `sigma_cm` | no — cancels exactly | **yes, dominant** | no |
| `sigma_k` mean part | yes | yes | no |
| `sigma_k` differential part | no | no | **yes (G1/G4)** |
| `sigma_psi` | negligible (2nd order) | negligible | **yes, dominant (G3)** |
| `sigma_stat` | yes | yes | yes |

> `sigma_k <= 0.34%` and `sigma_cm <= 1.15%` are a **sufficient hypothetical candidate scenario
> for validation**. They are **not** demonstrated necessary instrument limits: no search over the
> parameter space was performed and the budget bound is conservative.

### 11.1 Orientation uncertainty — primary, secondary and stress (disposition G3)

`sigma_psi` was previously recorded as "to be declared". It is now fixed **prospectively, before
execution**:

| role | `sigma_psi` | treatment |
|---|---:|---|
| **PRIMARY RELEASE SCENARIO** | **0.5°** | the complete true-bridge **≥ 0.90** validation claim is asserted here |
| secondary, lower-uncertainty sensitivity | 0.0°, 0.2° | reported, never pooled into the primary result |
| stress / robustness | 1.0° | reported; does **not** redefine the primary release criterion, and is **not** removed if it performs poorly |

This remains a **hypothetical synthetic uncertainty scenario**. It is **not** a claim that any real
apparatus has demonstrated 0.5° orientation uncertainty.

---

## 12. Provisional analytical complete-pipeline budget

**Target, adopted prospectively:**

```
target true-bridge complete-pipeline success >= 90%    for the declared validation scenario
```

Complete-pass event, with refusals counted as failures and the denominator **every declared
experiment** — no conditioning on survivors:

```
C = [ AND over 4 fields: BranchA_valid & rank_ok & Neff_ok & mode_rule_ok & gate_pass ]
    AND P2_accept AND P3_accept AND P4_verified
P(C) >= 1 - SUM(failure-event probabilities)           UNION INEQUALITY, EXACT THEOREM
```

| budget term | value | label |
|---|---:|---|
| 4 × `alpha_geom` | 0.02000000 | nominal design allocation |
| 4 × `eps_cal` surrogate mismatch | 0.00013269 | approximate; requires later validation |
| 4 × rank/`N_eff` refusal | 0.00000000 | proved upper bound, iid-Gaussian premise |
| 3 × mode-resolution crossing at 5° | 0.00000149 | quantified event; consequence not established |
| `1 - pi(P2 AND P3)` | 0.07440485 | approximate probability |
| P4 failure | 0.00000000 | exact, degenerate — deterministic check |
| **raw union expression** | **0.90546097** | |
| **reported lower bound** `max(0, ·)` | **0.9055** | |

Supporting probabilities for the declared scenario: `pi_P2 = 0.9685`, `pi_P3 = 0.9544`
(all four fields), `pi(P2 AND P3) = 0.9256` by exact two-dimensional integration over the shared
reference-field error, Simpson residual `1.83e-06`.

### 12.1 Required interpretation of 0.9055

> Under the declared Gaussian/log-linear uncertainty model, the surrogate calibration model and
> the stated approximations, the provisional analytical complete-pipeline budget is approximately
> **0.9055**. This exceeds the prospective 0.90 design target, but **does not certify achieved
> pipeline power**. The full stochastic validation gate remains **mandatory**.

It is **neither** a demonstrated empirical power **nor** an unconditional mathematical lower bound
on the actual implemented pipeline. The union inequality itself is an exact theorem; its
**inputs** are labelled separately:

| input | label |
|---|---|
| union inequality | **exact theorem**, any dependence |
| `pi(P2 AND P3)` | **approximate probability** — log-linear multiplicative error model |
| `alpha_geom` | **nominal design allocation** — achieved size must be demonstrated |
| `eps_cal` | **approximate; requires later validation** |
| rank/`N_eff` bound | **proved upper bound**, under an iid-Gaussian premise that is approximate for OU data |
| mode-resolution crossing | **quantified event, unestablished consequence; requires validation** |

Standing qualifications, all mandatory to repeat wherever 0.9055 is quoted:

1. **the surrogate calibration law is approximate for correlated observations** — the sample
   covariance of a correlated record is a weighted sum of chi-squares, not Wishart; the exact law
   is `3/2` times more skewed than any covariance-matched surrogate, which shifts the operating
   quantile by `0.0014–0.0028` sd at the declared record length;
2. **G5 uses a leading-order delta-method treatment** — `Var(g2) = 24 A4/n` with the
   second-moment terms cancelling exactly *inside* the delta-method calculation. That is an
   asymptotic result, not an exact finite-sample distribution result;
3. **calibration conditions on measured `H_A`, not unknown `H_true`** — a plug-in approximation.
   Calling the procedure conditional does not make an estimated parameter known. `tau_r` is
   likewise a Branch-A plug-in;
4. **the achieved null size must be demonstrated in the future stochastic validation** — a
   numerically calibrated procedure does not have exact size by construction.

---

## 13. False-bridge controls

Defined **separately** from the true-bridge success target and never netted against it.

| control | mechanism | status |
|---|---|---|
| blinded scale control | Branch-A declared scale × hidden `c`; analysis must recover `beta = 1/c` | baseline §14.2, committed |
| paired hidden-scale distortion | `c = 1.07 / 0.90` on a retained dataset | acts through P3/beta; gates are scale-invariant |
| independent coordinate permutation | destroys the correlation structure | the geometry control |
| non-commensurable alternatives | `beta = (1,1.06,1,1)`, `(1,0.93,1.05,1)`, `(1,1,1,1.10)`, and a **hard 2.5% single-field** case | acceptance = failure to detect |
| time shuffle | leaves `S` identical to `1e-30` | **autocorrelation control only**, not a geometry control |
| forbidden `H := K` | returns `beta = 1` identically | recorded as vacuous; demonstration only |

**Rejecting correct geometry** (a P1 false rejection, target `alpha_geom`) and **falsely declaring
cross-field equivalence** (a P2 acceptance under a true disparity) are different errors, reported
separately.

`alpha_geom = 0.5%` was checked against detection, not only against pass rate: it costs **6.8%**
in minimum detectable rotation relative to 1%, and affects no other declared control.

**These values must not be tuned after stochastic validation outcomes are inspected.**

---

## 14. Refusal semantics

Every declared job emits exactly one record with exactly one terminal status. No missing-key
crash, no silently dropped replicate, no conditional-on-survivor rate unless explicitly labelled
SECONDARY beside its unconditional counterpart.

```
OK                          gates passed, beta estimated
REFUSED_BRANCH_A_INVALID    H not symmetric / not positive definite / dimension mismatch
REFUSED_ACCESSIBLE_SPACE    rank guard failed on S (or S_T), rank_tol = 1e-12
REFUSED_NEFF_UNSUPPORTED    N_ab outside the declared validation domain
REFUSED_UNSUPPORTED_GEOM    condition outside the declared calibration domain
GEOMETRY_FAIL               gate rejected; beta deliberately NOT estimated
BETA_NOT_ESTIMATED          umbrella for every branch above
COMPARISON_NOT_EVALUABLE    reference or target field has no beta
EXECUTION_ERROR             exception; traceback hash recorded, job not lost
```

`REFUSED_BRANCH_A_INVALID` covers the stiffness conditions listed above **and**, under
§3.1, a Branch-A measured `eta` or `a` that is present but nonfinite, zero or negative. An
`eta` or `a` that is absent or undeclared is **not** that refusal: it keeps the separate
input-availability lifecycle, because we do not possess the input rather than possess an
inadmissible one. A derived `gamma` or `tau` that is physically admissible but numerically
unrepresentable keeps the existing Branch-A measurement/representability semantics, which
§3.1 does not alter.

The release report must reconcile: **jobs declared = jobs completed + jobs refused**, with a
per-status count, and must finish even when every job refuses.

---

## 15. Synthetic validation requirements

Mandatory before preregistration. **Not started.**

| # | requirement |
|---|---|
| 1 | `procedure_sha256` over `{config ∪ per-file code hashes ∪ decision rules ∪ seed map}` frozen before the first confirmatory run — the configuration hash alone is **not** a procedure freeze |
| 2 | development, calibration, validation and confirmatory **seed families disjoint**; thresholds fixed from calibration before any validation datum is analysed |
| 3 | achieved joint gate size demonstrated at every declared geometry: Clopper–Pearson one-sided 95% **upper** bound ≤ 3%, R = 400 |
| 4 | joint equivalence power demonstrated: one-sided 95% **lower** bound ≥ 0.90, R = 300, against a design target of `pi >= 0.95` |
| 5 | surrogate calibration law validated at the operating quantile against directly generated trajectories |
| 6 | plug-in conditioning validated: achieved size under `(H_true, tau_true)` against nominal from `(H_A, tau_A)`, swept over `sigma_k ∈ {0, 0.5%, 1%}` × `sigma_psi ∈ {0°, 0.2°, 0.5°, 1°}` |
| 7 | `theta_cap` size **and** power demonstrated at `rho =` boundary ± 20% |
| 8 | G5 block delta-method error quantified |
| 9 | every declared job reconciled by status |
| 10 | complete-pipeline success reported **unconditionally** |
| 11 | **blinded scale control (disposition G1)**: with `beta_tilde = c·beta_hat_blinded`, the **same** P3 absolute-equivalence construction (`delta_abs = 5%`, `z_abs = 1.959963985`) must accept at **every** tested field for **both** `c = 1.07` and `c = 0.90`; a replicate succeeds only if both branches pass. Campaign criterion: one-sided 95% Clopper–Pearson **lower** bound ≥ 0.90 over R = 200, i.e. **≥ 188/200** |
| 12 | **false-bridge discrimination (disposition G2)**: for **each declared alternative independently**, the one-sided 95% Clopper–Pearson **upper** bound on false acceptance must be ≤ **0.025** over R = 400, i.e. **≤ 4/400**. Counts are never pooled and easy and hard alternatives are never averaged |

Items 11 and 12 are **synthetic-validation release criteria only**. They close two pre-execution
authority gaps and change **no** primary-data analysis rule: P1, P2, P3 and P4, the margins, the
coverage factors, the alpha allocations, `theta_cap`, `rank_tol`, the four physical fields, the
complete-pipeline target and the anti-circularity rules are all unchanged. The 0.025 ceiling in item
12 is tied prospectively to the equivalence test's one-sided nominal level at `z = 1.959963985`; it
is **not** derived from any observed outcome. Item 11 reuses the P3 construction rather than
introducing a new tolerance.

Knowing the synthetic generating model is **software validation**. It is not physical
verification of that model, and no synthetic result may be reported as evidence about the
apparatus.

---

## 16. Interpretation boundaries

Three questions, kept separate. A pass on one does not establish the others.

| question | a pass means | a pass does **not** mean |
|---|---|---|
| **geometry agreement** (P1) | one scalar explains the directional relationship between `H` and `K` at this `theta` | that `beta` is the same at another `theta` |
| **cross-field equivalence** (P2) | the scale is consistent across conditions within the approved margin | that `beta = 1`, nor that `beta` is universal |
| **absolute calibration** (P3) | the scale agrees with E1a's specific prediction | that the bridge holds off-benchmark |

**Failure to reject a discrepancy is not demonstrated equivalence.** Equivalence is claimed only
when the interval lies wholly inside the margin; a wide interval merely containing 1 is recorded
as **inconclusive**.

**Local curvature agreement is not a finite-domain identity.** Pointwise Taylor agreement does not
control a function over a domain; third-order agreement alone establishes nothing. A
finite-domain claim requires a declared domain `D`, a uniform error bound
`sup_{x in D} |J_prob,theta(x) - beta V_theta(x)| <= epsilon` with `epsilon` stated in advance and
an error-control procedure that attains it, or an explicit declared model assumption.

**A common beta does not assign field changes to actors.** `V` is a state function of
`(x, theta)`, so the endpoint difference between two `(state, field)` pairs is path-independent —
but its **decomposition** into a state term and a field term is **not**. Actor EBU is defined at
fixed `theta`; a field-change contribution is kept explicit and never folded into an actor's EBU,
and a common beta does not authorise repricing a completed historical receipt.

---

## 17. Explicit non-claims

E1a does **not** discover statistical mechanics: `J_prob = V` is already predicted by canonical
equilibrium physics once the thermal normalisation is applied.

A successful E1a does **not** establish:

- universal EBU, or a universal `beta`;
- ecosystem, planetary or economic EBU;
- natural incentive, actor incentive, or economic optimality;
- stability, habitability, or any dynamic-field claim;
- ecological benefit;
- that the entropy candidate `S_eq - S = kappa V` is thereby established in general;
- preregistration readiness, until the §15 requirements pass.

It **does** establish, if executed successfully: that the EBU architecture is compatible with one
exact physical regime; that changing-field commensurability works there; and that the analysis
pipeline survives real experimental systematics.

**Superseded mechanisms stay superseded.** The fixed-`B0` normalisation
(`V = Delta U / B0`, giving `beta_theta = B0/(k_B T_theta)` and temperature-dependent `kappa`) is
**forbidden**. So are affordability and nonnegative-account requirements, and repricing of
completed historical contributions.

---

## 18. Authorization boundaries

| stage | status |
|---|---|
| analytical design | **ADOPTED** by this document |
| bounded implementation | **NOT STARTED** — requires separate authorization |
| pre-execution validation | **NOT STARTED** |
| synthetic validation campaign | **NOT STARTED** — requires separate authorization |
| preregistration | **NOT AUTHORISED** |
| physical execution | **NOT AUTHORISED** |
| E1b | **NOT STARTED** |
| Stage B | **NOT RESUMED** |

Analytical design, implementation, pre-execution validation, execution, interpretation and
publication are **separate authorization boundaries**. Later-stage files do not authorize
later-stage work.

Adopting this design **does not** authorize the stochastic pipeline, and **no** value in it has
been validated against a stochastic campaign.

---

## Provenance

Previous E1a work is preserved as provenance and is **not rewritten**: the v1, v2 and v3 gate
packages, the v4 design derivations, and `docs/e1a/E1A_V4_REPORT.md` at commit `8c48103`. Where
this document corrects them, the correction is recorded as a supersession notice (§2.1, §9.1)
rather than by editing the historical artifact.
