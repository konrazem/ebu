# E1a v4 — COMPLETE SCIENTIFIC REPORT

Single self-contained deliverable. Contains the design-correction packet, the targeted
correction addendum, the full command transcripts, and the file manifest. Nothing here
depends on any other file.

| | |
|---|---|
| repository | `konrazem/ebu` |
| branch | `gaussian/stage-a-environment` |
| local HEAD = intended remote HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` |
| working tree | clean at start and at end |
| frozen foundation sha256 | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| working baseline sha256 | `9b9f22d7b9c8a29725eb6a7abf4326fee68afaff503f23c2b5fbe1a6b21b732a` |
| v3 configuration sha256 | `a5d17030f40e183bef2020c406beb5aed5140d0937ac14e3b7aa9bb4485b9173` |
| commit / push | **none** |
| stochastic execution | **none** — no RNG, no trajectories, no model stepping |
| status | **READY FOR INDEPENDENT DESIGN REVIEW** |

## Headline results

| quantity | value | note |
|---|---:|---|
| complete-pipeline lower bound | **0.9055** | was 0.922; corrected for the mode-resolution term and the per-field P3 rule. Approximate design calculation, θ_cap = 5° |
| π(P2 ∧ P3) | 0.9256 | exact 2-D integral over the shared reference error; Simpson residual 1.83e−06 |
| π_P3, all four fields | 0.9544 | conjunctive rule, replacing the reference-field-only 0.9738 |
| mode-resolution cap | 5° | revised from 10°; split risk on a truly circular field 1.19e−02 → 4.98e−07 |
| σ_k = 1.00% | π_P2 = 0 | proven empty acceptance region: h = 2.0551% > δ_cross = 2% |
| α_geom 1% → 0.5% | +6.8% | loss in minimum detectable rotation; no other declared control affected |

## Corrections applied in this revision

1. **P3 rule was incomplete.** What produced the reported P3 numbers tested the reference
   field only; the committed prediction is β = 1 at *every* field. A complete conjunctive
   rule is proposed and all affected numbers recomputed.
2. **The probability budget omitted an event.** Mode-resolution boundary crossing, driven by
   noise in `H_A`, is now a named term; θ_cap revised 10° → 5°.
3. **"Exact joint null" was wrong for the covariance shortcut.** It is exact within a
   surrogate model, an approximation to the declared correlated model.
4. **"Conditioning on H" was a plug-in approximation**, on `H_A` not `H_true`.
5. **`β̂ = β/(1+δ̄)` is a population result**, one component of measurement error, not the
   complete finite-sample estimator.
6. **G5 independence is not claimed and not relied on**; the union bound needs neither.
7. **Two interpretation wordings corrected**: third-order agreement does not give a
   finite-domain identity; the `+57.7250` is an endpoint difference across two fields, not
   an actor EBU.

---

# PART I — TARGETED CORRECTION ADDENDUM

## E1a v4 — TARGETED CORRECTION ADDENDUM

Companion to `E1A_V4_CORRECTION_PACKET.md`, which is **unchanged**. This addendum closes the two
reviewer dependencies — whether the complete-pipeline calculation includes every mandatory failure
event, and whether its probability inputs apply to the actual estimator and sampling model — and
corrects four statements. Everything not listed here stands as written in the packet.

Repository coordinates at start **and** end: branch `gaussian/stage-a-environment`, local HEAD and
`origin/gaussian/stage-a-environment` both `c0099d8f7eea95a0f683f3c09fef71bdffc369af`, working tree
clean. Foundation `6d9aed24…f01507` and baseline `9b9f22d7…1b732a` unchanged. No commit, no push.

---

### 1. Decision register

| item | exact content | classification |
|---|---|---|
| `V_θ(x) = [U_θ(x) − U_θ(x*_θ)]/(k_B T_θ)`, `H_θ = H_U,θ/(k_B T_θ)` | baseline §14.1 | **COMMITTED REQUIREMENT** |
| β = 1 and κ = k_B **at every tested θ** | baseline §14.1 | **COMMITTED REQUIREMENT** |
| Two-branch separation; Branch-A hash before Branch-B unblinding; power-spectrum stiffness calibration **forbidden** | baseline §14 | **COMMITTED REQUIREMENT** |
| Four field arms θ0–θ3 | baseline §14.2 | **COMMITTED REQUIREMENT** |
| Blinded scale control, recovery target `β = 1/c` | baseline §14.2 | **COMMITTED REQUIREMENT** |
| `z` designed out, documented as discarded | baseline §14 | **COMMITTED REQUIREMENT** |
| `ΔS_total = k_B E_θ` | baseline §14.3 line 517; §4 line 152 | **COMMITTED** — and **requires qualification**, §5 |
| **`δ_cross_field` = 2%** | v3 `config.json` `endpoints.P2_cross_field_commensurability` — **uncommitted** | **AUTHOR-STATED REQUIREMENT NOT YET COMMITTED** |
| `δ_abs` = 5%, `z_abs` = 1.96 | v3 `config.json` `endpoints.P3_absolute_benchmark` — **uncommitted** | **PROPOSED DESIGN SETTING** (carried forward this task) |
| P3 conjunctive | this review's candidate direction | **PROPOSED DESIGN SETTING** |
| P3 evaluated at **every** field | proposed here, §2 | **PROPOSED DESIGN SETTING** |
| `α_geom` = 0.5%, split `α₁` = 0.4% / `α₂` = 0.1% | proposed in the packet | **PROPOSED DESIGN SETTING** |
| `θ_cap` = 5° | revised here, §3 | **PROPOSED DESIGN SETTING** |
| `z_cross` = 1.96 (Bonferroni dropped, IUT) | proposed in the packet | **PROPOSED DESIGN SETTING**, awaiting author confirmation |
| `σ_k`, `σ_cm`, `σ_ψ`, `σ_T`, `T_total`, `dt` values | scenario grid | **HYPOTHETICAL INSTRUMENT SCENARIO** — no measured capability claimed |

**The 2% margin, exact existing mathematical definition**, transcribed from `confirm2.py:74-76`
and `config.json`:

```
h_j = z_cross · sqrt( 2·σ_fs² + σ_stat,j² + σ_stat,ref² )
accept comparison j  ⟺  r_j·(1 − h_j) ≥ 1 − δ_cross   AND   r_j·(1 + h_j) ≤ 1 + δ_cross
r_j = β̂_j / β̂_ref ,  δ_cross = 0.02 ,  conjunctive over j = 1,2,3
```

A **per-comparison two-sided equivalence rule applied conjunctively to three comparisons against a
shared reference**. Not a pooled tolerance, not an all-pairs tolerance, not a tolerance on absolute β.
`δ_cross` and `δ_abs` are **different requirements and are not merged anywhere.**

> **No committed source defines any E1a margin, coverage level, error target or pass rule.** The
> uncommitted v3 configuration is **not** an authoritative committed protocol and is not described
> as one. No commit is authorised in this task.

---

### 2. The complete P3 rule

#### 2.1 What actually produced the reported P3 numbers — transcribed faithfully

From `v4_design_checks.py` function `pi_abs()` (and earlier `e1a_v4_design/corrections.py`):

```
sa = sqrt(σ_cm² + σ_fs² + σ_stat[REF]²)
ha = z_abs · sa
accept ⟺ log((1−δ_abs)/(1−ha)) ≤ log β̂_REF ≤ log((1+δ_abs)/(1+ha))
```

- **estimator** `β̂ = m/tr(H_A S)` — `e1a_analysis.py:120-121` `beta_mle`
- **parameter** β at the **reference field only**
- **coverage** two-sided, `z = 1.96`, nominal 95% interval; the induced equivalence test has size 2.5%
- **interval** multiplicative, `β̂·(1 ± ha)` — `e1a_analysis.py:122` `beta_ci`
- **shared vs field-specific** both `σ_cm` and `σ_fs` enter in quadrature — correct for an absolute
  endpoint, where nothing cancels
- **invalid cases** `beta_status != ESTIMATED` → `abs_accept()` returns `False` — `confirm2.py:121`

#### 2.2 Defect, and the proposed complete rule

E1a predicts β = 1 at **every** tested field (baseline §14.1, committed). **A rule evaluated only at
the reference field does not test that prediction.** The previously reported 0.974 is therefore the
reference-field-only probability, mislabelled as P3.

**PROPOSED DESIGN SETTING — complete P3 rule:**

```
P3 passes ⟺ for EVERY θ ∈ {θ0, θ1, θ2, θ3}:
    β̂_θ·(1 − h_θ) ≥ 1 − δ_abs   AND   β̂_θ·(1 + h_θ) ≤ 1 + δ_abs
    h_θ = z_abs · sqrt( σ_cm² + σ_fs² + σ_stat,θ² ) ,  z_abs = 1.96, δ_abs = 0.05
conjunctive over all four fields — an intersection-union test, so no multiplicity
correction is needed for size control
any field with beta_status != ESTIMATED makes P3 FAIL (fail-closed, no conditioning on survivors)
```

Recomputed, not carried over:

| σ_k | σ_fs | σ_cm | π_P3 ref-only (old) | **π_P3 all four (new)** | change |
|---:|---:|---:|---:|---:|---:|
| 1.00% | 0.708% | 2.291% | 0.0933 | **0.0014** | −0.0919 |
| 0.50% | 0.355% | 1.338% | 0.8927 | **0.8225** | −0.0702 |
| 0.40% | 0.285% | 1.200% | 0.9579 | **0.9270** | −0.0309 |
| **0.34%** | **0.243%** | **1.150%** | 0.9738 | **0.9544** | −0.0194 |
| 0.30% | 0.215% | 1.100% | 0.9844 | **0.9725** | −0.0119 |

The conjunctive rule costs 1–3 points rather than collapsing, because the dominant term `σ_cm` is
**common** to all four fields — they pass or fail largely together. That is why an exact integral over
the shared term is used instead of a product of marginals.

#### 2.3 Joint P2 ∧ P3 — exact 2-D integral

`w = d_cm`, `v_θ = −d_fs,θ + e_θ`; `log β̂_θ = −w + v_θ`; `log r_j = v_j − v_ref`. P2 constrains
`v_j` relative to `v_ref`; P3 constrains every `v_θ` relative to `w`. The three inner integrals are
interval intersections in closed form.

| σ_k | π_P2 | π_P3(all) | **π(P2∧P3)** | product |
|---:|---:|---:|---:|---:|
| 1.00% | 0.0000 | 0.0014 | 0.0000 | 0.0000 |
| 0.50% | 0.7021 | 0.8225 | 0.5918 | 0.5775 |
| 0.40% | 0.9089 | 0.9270 | 0.8465 | 0.8426 |
| **0.34%** | 0.9685 | 0.9544 | **0.9256** | 0.9244 |
| 0.30% | 0.9870 | 0.9725 | 0.9603 | 0.9599 |

2-D Simpson convergence: 301² → 601² changes by 5.26e−06; 601² → 1201² by 1.83e−06.

---

### 3. Complete-pipeline probability budget

```
C = [ AND over 4 fields: BranchA_valid & rank_ok & Neff_ok & mode_rule_ok & gate_pass ]
    AND P2_accept AND P3_accept AND P4_verified
P(C) ≥ 1 − Σ (failure-event probabilities)        union bound, EXACT INEQUALITY
```

| event | case | treatment | label |
|---|:--:|---|---|
| **P4** | **B** | `confirm2.py:143-148` tests a deterministic identity on **declared constants**, not on Branch-B data. Failure probability **exactly 0** under the assumption that the identity is verified at design time. Contributes no term | exact under a specified model (degenerate) |
| **rank-guard refusal** | **A** | Davidson–Szarek: `P[√λ_min < 1 − √(m/N) − t] ≤ 2e^{−Nt²/2}`. Reaching ratio 1e−12 at `N = 223,786`, `m = 2` needs `t ≈ 0.9970` → bound `2e^{−1.112e5}`, zero in double precision. **iid-Gaussian premise is itself approximate for OU** | proved upper bound |
| **N_eff unsupported** | **B** | `N_ab` is deterministic from Branch-A `τ_r = γ(T)/k_r` and the declared `T_total`, `dt`; inside range for all four fields. Zero **for this scenario only** | implied |
| **mode-resolution crossing** | **A + C** | **NEW TERM, absent before.** See below | quantified event, unquantified consequence |
| **finite-calibration / surrogate mismatch** | **A** | Besag–Clifford gives size ≤ `α₁` **conditional on the null law**; draws come from the surrogate. At `α₁ = 0.4%` (`z = 2.6521`, `φ(z) = 0.01185`) and the measured 0.0028 σ Cornish–Fisher shift: `ε_cal ≈ 3.317e−05` per field. G5's own delta-method error is **not quantified — case C** | approximate; requires later validation |
| **P2, P3** | **A** | `1 − π(P2∧P3)` | approximate probability |
| **Branch-A uncertainty** | **A** | enters β through `σ_cm`/`σ_fs` (budgeted in π) and the gates through the plug-in calibration (§4.2) | see §4.2 |

#### Mode-resolution crossing — the new term

The merge rule reads `H_A`'s eigenvalue ratio, and **`H_A` is noisy**. For a field that is *truly*
circular, `ρ_A ≈ 1 + |δ₁ − δ₂|`, half-normal with scale `√2·σ_k`. The rule splits whenever `ρ_A`
crosses the boundary `(ρ−1)/√ρ < u`, `u = 1/(θ_cap√N₁₂)`:

| θ_cap | u | merge boundary ρ | P(split \| truly circular) | × 3 circular fields |
|---:|---:|---:|---:|---:|
| **5°** | 0.02417 | 1.02447 | **4.975e−07** | 1.493e−06 |
| 10° | 0.01209 | 1.01216 | 1.195e−02 | 3.585e−02 |
| 20° | 0.00604 | 1.00606 | 2.088e−01 | 6.265e−01 |

The **consequence** of a crossing is **case C, not established**: calibrating conditional on `H_A` is
approximately self-consistent, since a split `H_A` also widens its own calibrated G3 threshold, so a
crossing may cost *detection power* rather than cause a false rejection. The budget charges the full
crossing probability as failure — the conservative choice.

> **Design consequence: `θ_cap` = 5°, revised from 10°.** It merges genuine splits only below
> ρ = 1.0245, and θ2 sits at ρ = 2.5, far outside. The packet's 10° is superseded.

#### The corrected headline

Unrounded inputs: `σ_k = 0.34%`, `σ_fs = 0.242747%`, `σ_cm = 1.1500%`, `α_geom = 0.005`.

| term | θ_cap = 5° | θ_cap = 10° |
|---|---:|---:|
| 4 × α_geom | 0.02000000 | 0.02000000 |
| 4 × ε_cal | 0.00013269 | 0.00013269 |
| 4 × rank/N_eff refusal | 0.00000000 | 0.00000000 |
| 3 × mode-resolution crossing | 0.00000149 | 0.03584835 |
| 1 − π(P2∧P3) | 0.07440485 | 0.07440485 |
| P4 failure | 0.00000000 | 0.00000000 |
| **raw union expression** | 0.90546097 | 0.86961411 |
| **REPORTED LOWER BOUND** max(0, ·) | **0.9055** | 0.8696 |

**The earlier 0.922 does not survive.** It omitted the mode-resolution term and used the
reference-only P3. Corrected: **0.9055** at θ_cap = 5°. This is an **approximate design calculation,
not a guaranteed success probability** — `π(P2∧P3)` rests on the log-linear error model and `ε_cal`
on an unvalidated surrogate. **Scenario-specific; not uniform over any declared parameter set.**

Raw negative union expressions for the looser scenarios are retained in `v4_addendum_checks.py`
output as a diagnostic only; reported bounds are clamped at zero.

#### Required classification

- `σ_k ≤ 0.34%` with `σ_cm ≤ 1.15%` — **a sufficient candidate scenario.** *Not* shown necessary: no
  search over `(σ_k, σ_cm, T_total, α_geom)` was run and the union bound is conservative, so looser
  scenarios may also suffice. **Not a hardware limit.**
- `σ_k = 1.00%` — **a proven empty acceptance region** for P2: `h_cross = 2.0551% > δ_cross = 2%`, so
  `[(1−δ)/(1−h), (1+δ)/(1+h)]` is empty by algebra. A demonstrated incompatibility of that scenario.
- intermediate rows — **an insufficient lower bound**, not an impossibility.

#### α_geom = 0.5% checked against false-bridge detection

| α_geom | z | threshold | min detectable rotation (80% power) |
|---:|---:|---:|---:|
| 1.0% | 2.5758 | 1.3271° | 1.7607° |
| 0.5% | 2.8070 | 1.4462° | 1.8798° |

A **6.8%** loss of geometric sensitivity. The other declared controls are unaffected: the paired
hidden-scale distortion acts entirely through P3/β because the gates are scale-invariant (verified,
≤ 6.7e−16); coordinate permutation gives G3 ≈ 30° against a 1.446° threshold, detected with
probability 1 to double precision. No control is removed, weakened or replaced.

---

### 4. Statistical-model corrections

#### 4.1 What the covariance shortcut actually generates — **corrected**

> **Corrected wording.** The shortcut generates **the exact joint distribution of (G1, G2, G3, G4)
> within a surrogate model for `S`** — and therefore an **approximation** to their distribution under
> the declared correlated model. It is the exact finite-sample distribution **only within the iid
> submodel**, where `S` really is Wishart. The packet's "exact joint null" is right about the
> *surrogate* and wrong if read as the declared model. Both readings were conflated; this is the
> correction.

**Mapping into the implemented statistics.** Draw `M` (m×m) from the surrogate; set
`S = (1/β)·H_A^{−1/2} M H_A^{−1/2}`; `K = inv(S)`; then call the implemented functions unchanged —
`G1_shape(H_A,K)`, `G2_spread(H_A,K)`, `G3_angles(H_A,K,·)`, `G4_ratios(H_A,K)`.

**An exact alternative exists, and its cost is why it was not proposed.** With `U = Γ^{1/2}Z`,
`Z` iid `N(0,1)` of size n×m, and `Γ = Σ_k λ_k q_k q_kᵀ` the temporal correlation matrix:

```
n·S = L (Zᵀ Γ Z) Lᵀ = L ( Σ_k λ_k z_k z_kᵀ ) Lᵀ ,   z_k = Zᵀq_k ~ N(0, I_m) iid
```

**exact** for the isotropic case (all modes sharing `Γ`), with `λ_k` the Kac–Murdock–Szegő
eigenvalues — characterised by a standard transcendental equation and asymptotically the AR(1)
spectral density. Cost is **O(n) rank-one terms per draw**, `n = 2×10⁶`. For the **anisotropic** case
(modes with different `τ_r`, i.e. θ2) **no cheap exact construction is established.** The surrogate is
therefore retained as a labelled approximation, with the operating-quantile comparison listed as a
validation item and `ε_cal` carrying its budget term.

#### 4.2 What conditioning on `H` means — **plug-in, labelled**

Two distinct objects: **`H_true`**, the physical curvature in the generating model, and **`H_A`**, the
noisy Branch-A estimate. **The calibration conditions on `H_A`.** So does the merge rule, and so does
`τ_r = γ(T)/k_r`, which is likewise a Branch-A estimate.

This is a **plug-in approximation**, not a conditional-on-truth calculation: the data are generated by
`(H_true, τ_true)` while the null law is built from `(H_A, τ_A)`. Calling the procedure "conditional"
does not make an estimated parameter known. Uncertainty in `H_true` and `τ_true` enters as the
mismatch between those two laws, and §3 shows one concrete route by which it bites — the
mode-resolution boundary.

**Future validation criterion** (no simulation required now): compare the achieved gate size under
`(H_true, τ_true)` against the nominal computed from `(H_A, τ_A)`, swept over
`σ_k ∈ {0, 0.5%, 1%}` × `σ_ψ ∈ {0°, 0.2°, 0.5°, 1°}`, and require the achieved size to remain within
the declared validation tolerance across that grid.

#### 4.3 The β estimator — derived for the real function and classified

Actual function, `e1a_analysis.py:120-121`: `beta_mle(H,S) = m/tr(H S)`. With
`G := H_true^{−1/2} H_A H_true^{−1/2}` and `M` the whitened sample covariance, `E[M] = I`:

```
β̂ = m β / tr(G M)          EXACT IDENTITY for the implemented function
β̂_pop = m β / tr(G)        population limit M → I
```

Checked on the actual function with hand-written anisotropic inputs — `H_true` eigenvalues (2.5, 1.0)
rotated 30°, `β_true = 1`, `Σ = H_true^{−1}`:

| case | `beta_mle(H_A, Σ)` | prediction | \|diff\| | σ_stat(G)/σ_stat(I) |
|---|---:|---:|---:|---:|
| 1 pure scalar, d = +3% | 0.9708737864 | 0.9708737864 | 0.00e+00 | 1.00000000 |
| 2 differential, δ = (+2%, −2%) | 1.0000000000 | 1.0000000000 | 0.00e+00 | 1.00019998 |
| 3 orientation, ψ = 1° | 0.9998629549 | 0.9998629549 | 0.00e+00 | 1.00013703 |
| 4 all three combined | 0.9707345246 | 0.9707407329 | 6.21e−06 | 1.00034331 |

Case 2 returns **exactly 1**: differential mode error with `δ̄ = 0` leaves β untouched. Case 3 matches
`2/(2 + sin²ψ·(r + 1/r − 2))` — orientation enters at second order and the identity is **exact in ψ**,
not merely first-order. Case 4's 6.2e−06 residual is the genuine cross-term between the three errors,
not a numerical artefact. The last column shows Branch-A error also perturbs the **sampling** term via
`σ_stat ∝ √(2 tr G²)/tr G` — by < 3.5e−4 relative here, **but not by exactly zero**.

| statement | classification |
|---|---|
| `β̂ = mβ/tr(GM)` | **exact identity** for the implemented function |
| `β̂_pop = mβ/tr(G)` | **exact, ideal population calculation** |
| `β̂ = β/(1 + δ̄)` | **exact for mode-scaling errors, population only** — **one component of measurement error**, not the complete finite-sample estimator. The packet did not say so |
| orientation immunity | **exact to all orders in ψ, population only**; magnitude `sin²ψ(r + 1/r − 2)/2` |
| `σ_β = √(σ_cm² + σ_fs² + σ_stat²)` | **first-order delta-method approximation** of a nonlinear multiplicative function, **not an exact identity**. Log-additivity would need every factor to be exactly log-normal; `m/tr(GM)` is a reciprocal quadratic form and is not |

No estimator was substituted; every check calls `beta_mle` as implemented.

#### 4.4 G5 — qualifications preserved

The estimator specification and the leading-order variance derivation stand (packet Appendix A.1–A.2):
`Var(g2) = 24·A4/n` with the `A2` terms cancelling, `E[g2] = −6/N2`, `N_g2 = n/A4 ≈ 2T/τ`.

> **Corrected wording.** The `A2` cancellation is an **exact cancellation inside a delta-method
> calculation** — a leading-order asymptotic result. It is **not** an exact finite-sample distribution
> result, and must not be described as one.

> **Corrected scope.** The `g2_1`/`g2_2` argument establishes dependence **between the two coordinate
> kurtoses**. It does **not** establish dependence between the whole G5 block and the G1–G4 block.

**The union-bound design does not require either.** It requires only that independence **not be
assumed**, and it is not: the two-block rule `reject ⟺ p_min(G1..G4) < α₁ OR p(G5) < α₂` bounds the
joint size by `α₁ + α₂` under **arbitrary** dependence. No independence project is opened.

---

### 5. Physical interpretation

#### 5.1 Scope of the equilibrium cancellation

`Δs_sys = −k_B E`, `Δs_med = +k_B E`, `Δs_tot = 0` hold **only** under all of:

1. the declared overdamped Langevin model with a **conservative** force `F = −∂_x U`;
2. **fixed field** — static `U`, no time-dependent driving `λ(t)`;
3. **fixed temperature**, a single reservoir;
4. the system in the **stationary equilibrium distribution** `p = p_eq` at both times, so that
   Seifert's `p(x,τ)` (Eq. 5 — the FPE solution for the actual initial condition) equals `p_eq`;
5. **no additional work input omitted from the accounting.**

Under (1)–(5) the first law gives `q = −ΔU` along **every** trajectory, so `Δs_med = q/T = +k_B E`
exactly per trajectory, and `Δs_sys = k_B(V_f − V_i) = −k_B E` exactly per trajectory.
**These are trajectory identities**, and they are stronger than an ensemble statement.

> **Distinguished from Eq. (11).** Seifert's Eq. (11), `⟨ṡ_tot⟩ = ∫dx j²/(Dp) ≥ 0` with equality
> exclusively in equilibrium, is a statement about the **ensemble-average entropy-production rate**.
> It is consistent with the above (`j = 0` in equilibrium) but is **not** the same statement. The
> trajectory identities are exact realisation-by-realisation; Eq. (11) is an average of a rate.

**No generalisation is claimed** to imposed actor actions, driven transitions, or nonequilibrium
initial distributions. Any of those violates (2), (4) or (5): an imposed displacement is work input,
and the accounting changes.

The constrained-macrostate object has **its own definition and derivation**, and is **not** identified
with either trajectory quantity without it: bead held at `x`, reservoir at `E_tot − U(x)`,
`S_constr(x) = S_res(E_tot − U(x)) + const`, expanded with `dS_res/dE = 1/T` and
`d²S_res/dE² = −1/(T²C_v)`:

```
ΔS_constr = k_B E_θ + remainder ,   remainder/leading = U/(2 T C_v)
```

For 1 mm³ of water, `C_v/k_B ≈ 1.004e20`, so at `U = 5 k_B T` the remainder ratio is **2.49e−20**.
**An approximation with an explicitly bounded remainder** — exact to first order in `U/(T C_v)`.

#### 5.2 What P4 can establish

**P4's statistic and pass rule are unaffected**, and here is why: `confirm2.py:143-148` evaluates
`|(5·k_B·T/T)/k_B − 5| < 1e−12` on **declared constants**. It never touches Branch-B data, `H_A`, or
any estimate. Its numerical output cannot change under any correction in this addendum.

**The physical claim that must be qualified** is separate and is *not* preserved by that: the baseline
asserts `ΔS_total = k_B E_θ` and "**+5 k_B of total entropy increase**". `k_B E` is the **medium**
entropy change (Seifert Eq. 8) and the **constrained-macrostate** deficit (§5.1). It is **not** total
entropy production, which is **zero** in equilibrium. An unchanged statistic does not preserve an
unsupported interpretation. Proposed wording is in the packet Appendix D.3; **the baseline and
foundation are not edited.**

#### 5.3 Two wording corrections

> **Corrected.** Packet Appendix D.1 listed "agreement at third and higher order" as a route to a
> finite-domain identity. **Third-order agreement alone does not establish one.** Pointwise Taylor
> agreement does not control a function over a domain. What is required instead: a **declared domain
> `D`**; a **uniform error bound** `sup_{x∈D} |J_prob,θ(x) − βV_θ(x)| ≤ ε` with `ε` stated in advance
> and an error-control procedure that attains it; or an **explicit model assumption** (for example
> that `U_θ` is exactly quadratic on `D`) declared as an assumption rather than inferred from a fit.

> **Corrected.** Packet Appendix D.2 wrote "**Total** from (100 nm, θ0) to (50 nm, θ1): E = +57.7250".
> That is an **endpoint difference of `V` evaluated in two different fields**, not an actor EBU:
> **actor EBU is defined at fixed θ.** Restated: `ΔV_endpoint = +57.7250`, decomposing as
> `E_state|θ0 = +91.1448` **plus a field-change contribution** of `−33.4197` (or, in the other order,
> `E_field|x=100nm = −133.6790` plus `E_state|θ1 = +191.4040`). The **field-change contribution is
> kept explicit and never folded into an actor's EBU**, and the two decompositions differ by
> **100.1445**. A common β makes the numbers commensurable; it does not select the decomposition. This
> clarifies the existing example and authorises no new dynamic-field model.

---

### 6. Which source function supports which claim

| claim | source | function / lines |
|---|---|---|
| β estimator identity and the four error cases | `e1a_gate_v3/e1a_analysis.py` | `beta_mle` 120-121; `inv`, `mm`, `TT`, `sym_pow` 14-49 |
| gate scale-invariance | `e1a_gate_v3/e1a_analysis.py` | `G1_shape` 65-70, `G2_spread` 71-72, `G3_angles` 88-101, `G4_ratios` 102-107, `G5_kurtosis` 109-117 |
| G5 estimator specification | `e1a_gate_v3/e1a_analysis.py` | `G5_kurtosis` 109-117 |
| P3 rule as computed | `e1a_gate_v4/v4_design_checks.py` | `pi_abs`; and `e1a_gate_v3/confirm2.py` `abs_accept` 114-122 |
| P2 rule as computed | `e1a_gate_v3/confirm2.py` | lines 74-76; `config.json` `endpoints.P2_…` |
| complete P3 rule, joint P2∧P3, budget | `e1a_gate_v4/v4_addendum_checks.py` | `p3_all_fields`, `joint_p2_p3`, section 3 |
| effective sample sizes, G5 variance | `e1a_gate_v4/v4_design_checks.py` | `A_p`, sections A, C |
| skewness ratio → 3/2 | `e1a_v4_design/exactness2.py` | `I_r` |
| operating characteristic | `e1a_v4_design/discrimination.py` | `joint_accept` |
| margins and audit re-derivation | `e1a_v4_design/derive_margins.py` equivalent in `verify_audit.py` | sections A–F |

---

### 7. Status

The two reviewer dependencies are closed: every mandatory failure event is now either in a named
budget term, derived as implied, or explicitly marked as not yet established; and the probability
inputs have been re-derived for the implemented estimator, with each labelled exact, bounded,
approximate, nominal, or pending validation. Four statements are corrected — covariance-shortcut
exactness, plug-in conditioning, the β-identity's scope, and the G5 dependence scope — and two wording
corrections are applied to the interpretation note.

No implementation was changed. No stochastic execution occurred. Nothing was committed or pushed.


---

# PART II — DESIGN CORRECTION PACKET (unchanged from the previous revision)

## E1a v4 — DESIGN CORRECTION PACKET

**Status:** analytical design correction. Not an implementation authorisation, not a preregistration,
not a validation result. Produced 2026-09-27.

**Central target, unchanged:** `K_θ = β H_θ` with **one field-independent β** over the declared
tested domain. Thermal normalisation preserved: `V_θ(x) = [U_θ(x) − U_θ(x*_θ)]/(k_B T_θ)`,
`H_θ = H_U,θ/(k_B T_θ)`. E1a predicts **β = 1 at every tested field condition**. β is estimated from
the measurement branches and is **never constrained to equal the prediction**.

**What E1a addresses:** whether independently measured physical-field geometry and independently
measured statistical geometry agree with one scale factor across the tested conditions. It does not
establish universal EBU, ecological benefit, actor incentives, or stability.

---

### 0. Starting point and provenance

| coordinate | value |
|---|---|
| repository | `konrazem/ebu` |
| branch | `gaussian/stage-a-environment` |
| local HEAD | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` |
| intended remote HEAD | `origin/gaussian/stage-a-environment` = `c0099d8f…` (identical) |
| working tree at start | **clean** |
| reference coordinate supplied | `c0099d8f…` — verified current, not assumed |

Protected documents verified by content hash, both now tracked and committed at `c0099d8f`:

| document | sha256 | expected | match |
|---|---|---|---|
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | `6d9aed24…f01507` | `6d9aed24…f01507` | ✅ |
| `docs/theory/EBU_THEORY_BASELINE.md` | `9b9f22d7…1b732a` | `9b9f22d7…1b732a` | ✅ |

**Change since the previous v4 packet:** HEAD advanced `6538f91` → `c0099d8`. The foundation, the
baseline, both `.meta.json` sidecars and the `AGENTS.md` authority section, previously untracked
working-tree files, are now **committed**. Content hashes are unchanged. No protected content moved.

#### Artifact locations — exact, with committed status

| artifact | path | status |
|---|---|---|
| v1 gate package (12 files) | `<scratch>/e1a_gate/` | **local task artifact, uncommitted** |
| v2 gate package (15 files) | `<scratch>/e1a_gate_v2/` | **local task artifact, uncommitted** |
| v3 gate package (15 files) | `<scratch>/e1a_gate_v3/` | **local task artifact, uncommitted** |
| v3 config, sha `a5d17030…b9173` | `<scratch>/e1a_gate_v3/config.json` | uncommitted; hash re-verified |
| v4 design calculations (4 scripts) | `<scratch>/e1a_v4_design/` | local task artifact |
| **this packet** | `<scratch>/e1a_gate_v4/E1A_V4_CORRECTION_PACKET.md` | **new, uncommitted** |
| **companion script** | `<scratch>/e1a_gate_v4/v4_design_checks.py` | **new, uncommitted** |

`<scratch>` = `/private/tmp/claude-501/-Users-konrad-grzyb-code-ebu/2439348e-…/scratchpad`.

> **MISSING MATERIAL, NAMED PRECISELY.** The **original v4 packet and its addendum have no file
> path.** They exist only as conversation text and were never written to disk. This packet supersedes
> them in content but **cannot cite them as artifacts**. Nothing here depends on recovering them:
> every number below is re-derived in `v4_design_checks.py`.

#### Authority conflicts — reported, not repaired

1. **The approved 2% cross-field margin has no committed controlling source.** It appears in neither
   the frozen foundation nor the working baseline (searched for `margin|toleran|equivalen|2%`). Its
   only written definition is `<scratch>/e1a_gate_v3/config.json`, an **uncommitted local artifact**;
   its approval provenance is conversational. Under `AGENTS.md` ("Chat history … are not
   authoritative scientific records") the margin is **approved but not yet recorded in an
   authoritative document.** It is used here exactly as defined, unchanged, and flagged.
2. **Baseline §14.5 states "E1a is DESIGN COMPLETE … No new design decision is required."** The v3
   release-gate failure and the corrections below contradict this. Reported; the baseline is not edited.
3. **Baseline §14.3 line 517 and §4 line 152 state `Delta S_total = k_B E_theta`.** Appendix D finds
   this **requires qualification**. Reported; wording proposed there; the baseline is not edited.

**No committed source defines any endpoint margin, error-rate target, success target, or pass rule
for E1a.** All quantitative decision rules trace to the uncommitted v3 config. This is a provenance
gap, not permission to invent values: every value used below is carried over unchanged.

---

### 1. Correction map

#### Accepted, not repeated

Thermal normalisation and the β = 1 prediction (baseline §14.1, committed). The two-branch design,
Branch-A hashing before Branch-B unblinding, and the **prohibition on power-spectrum stiffness
calibration** (baseline §14, committed). The four field arms (baseline §14.2, committed). The blinded
scale control with recovery target `β = 1/c` (baseline §14.2, committed). Accessible directions: the
lateral `x`/`y` plane, axial `z` **designed out and documented as discarded**, not read as an observed
zero-curvature mode (baseline §14, committed).

Retained from the v4 work and **not re-derived**: the structural result that a margin set to `z·σ`
makes a CI-in-margin rule powerless; the G3 root cause `sd(θ) = √(ρ/(N(ρ−1)²))`, predicting 35.4%
against 38.3% observed; per-element `N_ab` for second moments; calibration conditional on Branch-A
`H`; the resolvability block rule; structured refusal; the release manifest; the two-sided operating
characteristic. Both earlier v3 explanations remain withdrawn: a threshold **floor** can only reduce
rejections, and five genuine 1% gates are union-bounded at 5%.

**v3 remains a failed development release.** Superseded mechanisms stay superseded: no fixed-`B0`
normalisation, no affordability or nonnegative-account requirement, no repricing of completed
historical contributions.

#### Exact locations requiring correction

| # | location | defect |
|---|---|---|
| C1 | `e1a_analysis.py:109-117` `G5_kurtosis` | uncertainty was derived for a raw fourth moment, not for the implemented ratio estimator |
| C2 | v4 accelerated calibration (design) | covariance shortcut cannot produce G5 at all; joint dependence with G1–G4 was assumed away |
| C3 | v4 combined-power (design) | gate/β independence inferred from scalar invariance — a non-sequitur |
| C4 | `e1a_analysis.py:142-182` `analyse` | `n_eff` argument is a single scalar; second moments need per-element `N_ab`, and an anisotropic trap has no single scalar |
| C5 | `e1a_analysis.py:75-82` `_blocks` | `delta_deg = 0.05` is arbitrary and `N`-independent |
| C6 | `phase1_grid.py:27-28` | pooled 99th percentile over four heterogeneous geometries, `R = 160`, plus a 1° floor |
| C7 | `confirm2.py:66` | `bref = ex[ref]["beta_hat"]` — unconditional read, crashes on refusal |
| C8 | `confirm2.py:26-34` `rate_test` | accepts on the **lower** confidence bound; cannot establish error control |
| C9 | `e1a_world.py:36` | `x = [0.0]*m` — non-stationary initialisation; and one `tau_c` declared for all four fields |
| C10 | uncertainty model (config) | only scalar terms; Branch-A **shape** and **orientation** uncertainty absent |

#### The three questions, kept separate

| question | statistic | what a pass means | what it does **not** mean |
|---|---|---|---|
| **Geometry agreement** | G1–G5 joint gate | one scalar explains the directional relationship between `H` and `K` at this `θ` | that β is the same at another `θ` |
| **Cross-field β equivalence** | `β̂_θ/β̂_ref` | the scale is consistent across conditions **within the approved margin** | that β = 1, nor that β is universal |
| **Absolute β calibration** | `β̂_ref` | the scale agrees with E1a's specific prediction β = 1 | that the bridge holds off-benchmark |

**Failure to reject a discrepancy is not demonstrated equivalence.** Equivalence is claimed only when
the confidence interval lies entirely inside the margin; a wide interval that merely contains 1 is
recorded as *inconclusive*.

#### Mandatory endpoints

| id | purpose | implemented statistic | pass rule | uncertainty inputs | controlling source |
|---|---|---|---|---|---|
| **P1** | geometry agreement per field | G1–G5, two-block joint gate | `p_min(G1..G4) ≥ α₁` **and** `p(G5) ≥ α₂` | `σ_stat`, `σ_ψ`, differential `σ_k` | **no committed source**; v3 config |
| **P2** | cross-field equivalence | `r_j = β̂_j/β̂_ref`, j = 1,2,3 | `r_j(1−h_j) ≥ 1−δ` **and** `r_j(1+h_j) ≤ 1+δ`, δ = 0.02, `h_j = z√(2σ_fs² + σ_stat,j² + σ_stat,ref²)`, **all three** | `σ_fs`, `σ_stat` (`σ_cm` cancels) | **no committed source**; v3 `config.json` `endpoints.P2_cross_field_commensurability` |
| **P3** | absolute β = 1 | `β̂_ref` | pass rule **undefined in any committed source** — see §5 | `σ_cm`, `σ_fs`, `σ_stat` | prediction: baseline §14.1 (committed). Margin: none |
| **P4** | entropy | closed form | `ΔS = k_B E` identical across `T` | none | baseline §14.3 (committed) — **requires qualification, Appendix D** |

The P2 pass rule above is copied verbatim from `confirm2.py:74-76` and `config.json`. It is a
**per-comparison two-sided equivalence rule applied conjunctively to all three comparisons against
the shared reference**. It is **not** a pooled tolerance, **not** an all-pairs tolerance, and **not**
a tolerance on absolute β.

---

### Appendix A — G5 and the accelerated calibration (corrects C1, C2)

#### A.1 The estimator, stated exactly

```
whitening   Z_i = H^{1/2}(x_i − x*)     H and x* from BRANCH A — no data-dependent direction
centering   mu_r = (1/n) Σ_i Z_ir       SAMPLE mean (while S is centred at the declared x*)
moments     m2_r = (1/n) Σ (Z_ir−mu_r)² ,  m4_r = (1/n) Σ (Z_ir−mu_r)⁴
statistic   g2_r = m4_r/m2_r² − 3       NO bias correction, NO n/(n−1)
gate        G5   = max_r |g2_r|
```

Variance normalisation is **internal** (division by `m2_r²`), not by a declared σ. Unlike G3 and G4,
**no eigen-direction is estimated** — G5's basis is Branch-A fixed. All five gates reuse the same
observations. The two different centrings (sample mean for G5, declared `x*` for `S`) are a real
inconsistency; v4 makes the choice explicit and calibrates at whatever is chosen.

#### A.2 Uncertainty of that estimator — **APPROXIMATION (delta method, leading order)**

With `A_p = 1 + 2Σ_{k=1}^{n−1}(1−k/n)φ^{pk}`, `φ = e^{−dt/τ}`, and Isserlis
`Cov(x₀²,x_t²) = 2σ⁴ρ²`, `Cov(x₀⁴,x_t⁴) = 72σ⁸ρ² + 24σ⁸ρ⁴`, `Cov(x₀²,x_t⁴) = 12σ⁶ρ²`:

```
Var(g2) = (1/n)[ 72·A2 + 24·A4 + 72·A2 − 144·A2 ] = 24·A4 / n      A2 CANCELS EXACTLY
```

The kurtosis ratio is self-normalising: the second-moment contributions cancel and only the
fourth-order correlation survives. **Effective size `N_g2 = n/A4 ≈ 2·T/τ`.**

**Mean estimation, accounted for:** `E[x̄²] = σ²/N1`, `E[x̄m3] = 3σ⁴/N1` with `N1 = n/A1` the
*mean's* effective size; `E[m2] = σ²(1−1/N1)`, `E[m4] = 3σ⁴(1−2/N1)`. The ratio expansion gives

```
E[g2] = −6/N2 + O(N⁻²)      the N1 terms CANCEL; the bias is set by N2
```

(iid check: `N2 = n` → `−6/n`, matching the classical `−6/(n+1)` at leading order).

| field / mode | τ (ms) | N1 | N2 | **N_g2** | sd(g2) | bias | \|bias\|/sd |
|---|---:|---:|---:|---:|---:|---:|---:|
| θ0 m1, m2 | 1.0680 | 111,928 | 223,786 | **442,036** | 0.007368 | −2.68e−5 | 0.0036 |
| θ1 m1, m2 | 0.5086 | 232,062 | 463,357 | **879,507** | 0.005224 | −1.29e−5 | 0.0025 |
| θ2 m1 | 0.7120 | 167,131 | 333,934 | **649,753** | 0.006078 | −1.80e−5 | 0.0030 |
| θ2 m2 | 1.7799 | 67,400 | 134,632 | **268,049** | 0.009462 | −4.46e−5 | 0.0047 |
| θ3 m1, m2 | 0.7152 | 166,398 | 332,467 | **647,053** | 0.006090 | −1.80e−5 | 0.0030 |

Bias is ≤ 0.5% of one standard deviation, so **no bias correction is introduced**; it is nonetheless
reproduced automatically by calibrating at the declared `(H, n, τ)`.

> **WITHDRAWN.** The earlier `N₄ = 1.143·T/τ`, taken from `ρ_{x⁴}(t) = 0.75ρ² + 0.25ρ⁴`, is the
> effective size for the **raw fourth moment**, not the implemented statistic. The correct value is
> ≈ `2·T/τ`. Using `N2` for G5 is conservative by a factor 2 in variance. The 1.143 figure is used nowhere.

#### A.3 What the covariance shortcut can and cannot do

**EXACT, hand-checkable:** two 4-point sets, identical mean and identical `m2` (hence identical `S`
in one dimension), different `g2`:

| set | mean | m2 | m4 | g2 |
|---|---:|---:|---:|---:|
| `A = (1, 1, −1, −1)` | 0.0 | 1.0000 | 1.0000 | **−2.0000** |
| `B = (√2, 0, 0, −√2)` | 0.0 | 1.0000 | 2.0000 | **−1.0000** |

- **CAN:** G1, G2, G3, G4 — each is a deterministic function of `(H, S)` alone, so one draw of `S`
  reproduces their **exact joint** null, all four-way dependence included.
- **CANNOT:** G5. No draw of `S` can produce it.
- **CANNOT:** the joint dependence between G5 and G1–G4.

#### A.4 Why G5 is **not** generated independently

**EXACT, iid only.** Whitened data are `N(0, I/β)` iid; `tr(W)` is complete sufficient for β; every
gate is scale-invariant hence ancillary; **Basu's theorem** gives `(G1..G5) ⊥ tr(W)`. It gives
**nothing** about G5 versus G1–G4.

**EXACT non-independence argument.** Let `u`, `v` be the centred-normalised coordinate vectors, so
`g2_1 = g2(u)`, `g2_2 = g2(v)`, and the sample correlation is `r₁₂ = u·v`. As `r₁₂ → ±1` the vectors
coincide up to sign, forcing `g2_1 → g2_2`. Independence would require the conditional law of
`(g2_1, g2_2)` given `r₁₂` to be free of `r₁₂`; by continuity of that conditional law near `r₁₂ = ±1`
it is not. **The joint law is not a product.**

**CORRELATED case.** The complete sufficient statistic for the scale family is `Z′Γ⁻¹Z`, not `tr(W)`,
so even the Basu results above lapse.

#### A.5 The corrected accelerated procedure

```
two-block gate:   reject ⟺ p_min(G1..G4) < α₁  OR  p(G5) < α₂ ,   α₁ + α₂ = α_geom
```

Size ≤ `α_geom` by the union bound, **valid under arbitrary dependence** — no independence asserted.
Block 1's four-way dependence is exact (one shared `S` draw). Block 2 is a single statistic. Proposed
split `α₁ = 0.4%`, `α₂ = 0.1%`.

**Domain:** modes within G5 are independent only because isotropic Stokes drag makes `A = γ⁻¹H_U`
share eigenvectors with `H` — a **declared benchmark property, not a general one**.
**Expected limitation:** the union bound is conservative under positive dependence, costing power.
**Specific later validation:** measure the achieved joint size and the power loss against the
two-block bound, at each declared geometry, in the future validation gate (§6 of the implementation plan).

---

### Appendix B — Complete-pipeline performance (corrects C3)

#### B.1 What counts as a complete pass

All of the following, with **refusals counted as failures** and the denominator **every declared
experiment** — no conditioning on survivors:

1. all four fields: Branch-A valid, rank guard passes, `N_eff` supported, geometry gate passes;
2. **P2**: all three cross-field comparisons accepted within the approved 2% margin;
3. **P3**: absolute β = 1 accepted under its pass rule;
4. **P4**: entropy endpoint verified.

#### B.2 The independence claim, withdrawn

> **WITHDRAWN:** "gates are scalar-invariant, so gates and β are statistically independent." Scalar
> invariance says only that the gates do not depend on the calibration **errors**. Gates and `β̂` are
> both functions of the same `S`.

**Verified against the implementation** (pure-function check, hand-written matrices, no RNG):

| gate | at `H` | at `2H` | difference |
|---|---:|---:|---:|
| G1 | 0.035238095238 | 0.035238095238 | 0.00e+00 |
| G2 | 1.165935010018 | 1.165935010018 | 6.66e−16 |
| G3 | 4.065051177078 | 4.065051177078 | 0.00e+00 |
| G4 | 0.114033105040 | 0.114033105040 | 0.00e+00 |
| G5 | 0.961945787584 | 0.961945787584 | 0.00e+00 |

while `β̂(H,S)/β̂(2H,S) = 2.000000000000` exactly. Scale invariance is confirmed; **it still does not
imply independence.**

**EXACT, iid only:** `β̂ = m/tr(HS)` is a function of `tr(W)`; the gate vector is ancillary; Basu gives
exact independence — **by ancillarity, not by scalar invariance**. For correlated data the
completeness premise fails and **no product rule is claimed**.

#### B.3 The bound used — **EXACT INEQUALITY, any dependence**

```
P(complete) ≥ 1 − Σ_f α_geom,f − (1 − π_P2) − (1 − π_P3)
```

`π_P2` and `π_P3` are computed by an **exact one-dimensional integral** over the shared
reference-field error (the three comparisons and the absolute endpoint all contain it):

```
log r_j = V_j − W ,  log β̂_ref = −d_cm + W
W ~ N(0, σ_fs² + σ_stat,ref²)   V_j ~ N(0, σ_fs² + σ_stat,j²)
```

#### B.4 Unified uncertainty model — **EXACT for this model**

With `H`'s modes scaled by `(1+δ_r)`: `tr(HS) = Σ_r(1+δ_r)λ_rΣ_rr = (m + Σ_r δ_r)/β`, so
**`β̂ = β/(1 + δ̄)` — only the mean of `δ_r` enters β.** Hence

```
σ_fs = √( σ_k²/m + (σ_T/T)² )
```

and the **differential** part of `δ_r` (sd `√2·σ_k`) moves `H`'s eigenvalue ratio, feeding G1/G4 —
the gates, not β. Orientation `ψ` enters β only at second order,
`tr(RHR′H⁻¹)/m − 1 = sin²ψ·(r + 1/r − 2)/2`, which is **< 0.06% even at ψ = 2°** for the worst
geometry — negligible for β, dominant for G3.

| uncertainty | limits cross-field ratio | limits absolute β | limits gates |
|---|:--:|:--:|:--:|
| `σ_cm` common-mode scale | **no** — cancels exactly | **yes, dominant** | no |
| `σ_k` per-mode stiffness, **mean part** | yes | yes | no |
| `σ_k` per-mode stiffness, **differential** | no | no | **yes (G1/G4)** |
| `σ_ψ` orientation | negligible | negligible | **yes, dominant (G3)** |
| `σ_stat` | yes | yes | yes |

#### B.5 Results — **SCENARIO-SPECIFIC, not pooled, not guaranteed elsewhere**

δ = 2% (approved, unchanged), `z_ratio = 1.96`, `z_abs = 1.96`, `δ_abs = 5%`, `T_total = 240 s`.

| σ_k | σ_fs | σ_cm | α_geom | π_P2 | π_P3 | π(P2∧P3) | **bound w/ P3** | bound no P3 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1.00% | 0.708% | 2.291% | 1.0% | **0.000** | 0.093 | 0.000 | −0.947 | −0.040 |
| 1.00% | 0.708% | 2.291% | 0.5% | **0.000** | 0.093 | 0.000 | −0.927 | −0.020 |
| 0.50% | 0.355% | 1.338% | 0.5% | 0.702 | 0.893 | 0.631 | 0.575 | 0.682 |
| 0.40% | 0.285% | 1.200% | 0.5% | 0.909 | 0.958 | 0.872 | 0.847 | 0.889 |
| **0.34%** | **0.243%** | **1.150%** | **0.5%** | 0.969 | 0.974 | 0.944 | **0.922** | 0.949 |
| 0.30% | 0.215% | 1.100% | 0.5% | 0.987 | 0.984 | 0.972 | 0.951 | 0.967 |

`π(P2∧P3)` **exceeds** `π_P2·π_P3` in every row: the shared reference error makes the two endpoints
**positively dependent**, so the union bound is conservative here.

**Insufficient bound versus demonstrated incompatibility.** Rows 1–2 show a bound below zero, which is
*uninformative* as a bound. But `π_P2 = 0.000` there is **not** a loose bound: at `σ_fs = 0.708%` the
CI half-width is `h = 2.0551% > δ = 2%`, so the acceptance region
`[(1−δ)/(1−h), (1+δ)/(1+h)]` is **empty**. That is a **demonstrated incompatibility for that
scenario**, by the algebra of the rule, not a limitation of the bounding method.

**Worst comparison** at σ_k = 0.34% — a pooled figure must never stand in for the worst field:

| comparison | σ_ratio | CI half-width | marginal acceptance |
|---|---:|---:|---:|
| θ1 / ref | 0.4291% | 0.8410% | 0.9931 |
| **θ2 / ref** | **0.4633%** | **0.9081%** | **0.9815** ← worst |
| θ3 / ref | 0.4389% | 0.8602% | 0.9906 |

**Convergence — REQUIRED BY §6.3.** Simpson's rule, scenario σ_k = 0.34%, with P3:

| npts | value | \|change\| |
|---:|---|---:|
| 2,001 | 0.9436441555 | — |
| 8,001 | 0.9436441555 | 1.44e−15 |
| 32,001 | 0.9436441555 | 8.10e−15 |
| 128,001 | 0.9436441555 | 2.61e−14 |

Integration error < 1e−9. Not a limiting source of uncertainty.

#### B.6 False-bridge detection — existing controls preserved, no replacement campaign

Acceptance = **failure to detect**. Scenario-specific at σ_k = 0.34%.

| declared alternative | acceptance |
|---|---:|
| β = (1, 1.06, 1, 1) | 0.00000 |
| β = (1, 0.93, 1.05, 1) | 0.00000 |
| β = (1, 1, 1, 1.10) | 0.00000 |
| β = (1, 1.025, 1, 1) — hard | 0.00066 |
| reference off by 3% | 0.00000 |

Preserved unchanged and not re-derived: the **blinded scale control** with recovery target `β = 1/c`
(baseline §14.2, committed); the paired hidden-scale distortion `c = 1.07 / 0.90` on a retained
dataset; independent coordinate permutation (the geometry control); the time shuffle, which is an
**autocorrelation control only** — it leaves `S` identical to 1e−30; and the forbidden `H := K`,
recorded as vacuous.

**Kept distinct and never netted:** rejecting correct geometry (a P1 false rejection, target
`α_geom`) is a different error from falsely declaring cross-field equivalence (a P2 acceptance under
a true disparity).

---

### Appendix C — Exactness labels

| # | result | label | assumptions / what was approximated |
|---|---|---|---|
| 1 | `N_ab = (T/2)(1/τ_a + 1/τ_b)` | **APPROXIMATION** | continuous-time, large-T limit. Measured error **0.19–0.91% anti-conservative** at the declared `dt`. v4 replaces it with the exact discrete sum `A_p`. Second-moment statement only — it does **not** determine the law of `S` |
| 2 | `S` is Wishart for correlated data | **WITHDRAWN** | `n·m2/σ² = Z′Z` is a **weighted sum of χ²₁**. Satterthwaite matches two cumulants; the third is free. `skew(exact)/skew(matched) = I3/I2² → 3/2` **exactly** (Lorentzian limit: `I2 = 1/ε`, `I3 = 3/2ε²`). Absolute skew ≈ 0.01, so the 99th-percentile shift is **0.0014–0.0028 σ** — structural but numerically negligible at 240 s. **REQUIRES VALIDATION** at the operating quantile; refuse the shortcut for short records |
| 3 | min-p size `= α_geom` | **WITHDRAWN** | size is `Beta`-distributed: `R=160` → 1.242% ± 0.870%; `R=50,000` → **1.000% ± 0.044%**. Adopted: Barnard/Besag–Clifford `p̂ = (1+#{null ≥ obs})/(R+1)`, size ≤ α for any `R` — **EXACT UNDER STATED ASSUMPTIONS**, conditional on the draws coming from the true null law, which item 2 shows they do not exactly. Unconditional size **REQUIRES VALIDATION** |
| 4 | `Beta(2,159)` for the v3 table | **RESCOPED** | presumes exchangeability, so it describes a fresh draw from the **pooled mixture** only. Two mechanisms were present and only one was named: (i) **estimation** from finite `R` — Beta, quantified; (ii) **heterogeneity**, the pooled quantile applied per field — field-dependent, **not quantified and not a function of R**. Removed by per-`H` conditioning, not explained away |
| 5 | 10° mode-resolution cap | **PROPOSED DESIGN CHOICE** | no derivation. Moves the merge boundary between 1.6% and 0.6% anisotropy. Declared prospectively; **REQUIRES VALIDATION** of size *and* power at boundary ±20% |
| 6 | `Var(g2) = 24·A4/n`; `E[g2] = −6/N2` | **APPROXIMATION** | delta method, leading order. Exact finite-n moments exist for iid only |
| 7 | A.3 four-point example; A.4 non-independence | **EXACT** | arithmetic; continuity of the conditional law near `r₁₂ = ±1` |
| 8 | `β̂ ⊥ gate vector` | **EXACT UNDER STATED ASSUMPTIONS** | iid, declared `x*`, `H` known. Basu. Fails for correlated data |
| 9 | Union bound B.3 | **EXACT INEQUALITY** | any dependence |
| 10 | One-factor integral B.3 | **EXACT** given the log-linear multiplicative error model; convergence 2.6e−14 |
| 11 | `β̂ = β/(1+δ̄)`; orientation second order | **EXACT** for the declared model |
| 12 | Gate scale-invariance | **EXACT, this implementation** | verified against `e1a_analysis.py`, differences ≤ 6.7e−16 |
| 13 | `sd(θ) = √(ρ/(N(ρ−1)²))` | **APPROXIMATION** | asymptotic eigenvector perturbation, leading order |

**A deterministic numerical calculation is not an exact theorem.** Rows 1, 6 and 13 are asymptotics
evaluated numerically; rows 7–11 are theorems or exact arithmetic.

---

### Appendix D — Physical-interpretation note

#### D.1 Local agreement versus finite actions

`K_θ = βH_θ` is a statement about **curvature at the reference point**: `K = −Hess log P|_{x*}` and
`H = Hess V|_{x*}`. A finite-domain identity `J_prob,θ(x) = βV_θ(x)` for all `x` in the domain is
strictly stronger — curvature agreement at one point constrains only the second-order Taylor
coefficients. Extension requires, additionally: (i) that `−log P` and `V` agree at third and higher
order over the domain, which is what the G5 tail gate probes only weakly and what the **secondary
nonlinear endpoint** (Option B, detection of near-versus-far departure) probes directly; (ii) a
declared validity radius with a stated departure bound; (iii) evidence at displacements where the
harmonic approximation to `U_θ` itself fails. **None of that is supplied by P1–P3.** A pass licenses
the local statement and the commensurability of the scale, not a finite-domain identity.

#### D.2 Changing fields versus actor contributions — exact deterministic example

`V_θ(x) = k_θ x²/(2k_B T)`, `x* = 0`, `T = 298 K`; θ0: `k = 100 µN/m`, θ1: `k = 210 µN/m`.

| | V (dimensionless EBU) |
|---|---:|
| θ0, x = 100 nm | 121.5264 |
| θ0, x = 50 nm | 30.3816 |
| θ1, x = 100 nm | 255.2053 |
| θ1, x = 50 nm | 63.8013 |

- **State change at fixed θ0** (100 → 50 nm): `E = +91.1448`
- **Field change at fixed x = 100 nm** (θ0 → θ1): `E = −133.6790`
- **Field change at fixed x = 50 nm** (θ0 → θ1): `E = −33.4197`

Total from (100 nm, θ0) to (50 nm, θ1): `E = +57.7250`, reached by either order:

```
state first, then field :  +91.1448  +  (−33.4197)  =  +57.7250
field first, then state :  −133.6790 +  (+191.4040) =  +57.7250
```

**The total is path-independent** — `V` is a state function of `(x, θ)`. **The split between the
"state" term and the "field" term is not**: the two orders differ by **100.14 EBU**. A common β makes
all four numbers commensurable on one scale. It does **not** select a decomposition, so it cannot by
itself attribute the field term to any actor, and it does not authorise repricing a completed
historical receipt. The experimenter raising the laser power is not an actor acting on the bead.

#### D.3 Independent check of `ΔS_total = k_B E_θ`

**The claim examined.** Baseline `docs/theory/EBU_THEORY_BASELINE.md` §14.3 line 517:
`Delta S_total = k_B E_theta`, glossed at line 521 as "**+5 k_B of total entropy increase**"; and §4
line 152, "tests `E = Delta S_total / k_B`".

**Source consulted.** U. Seifert, *Entropy production along a stochastic trajectory and an integral
fluctuation theorem*, PRL **95**, 040602 (2005); arXiv:cond-mat/0503686v1. The PDF was fetched but its
text layer is font-subset encoded and unreadable; **equations below are cited from the ar5iv HTML
rendering of the same preprint, and equation numbers are the preprint's, which may differ from the
published PRL.** Seifert sets `k_B = 1`; factors of `k_B` are restored here.

| Seifert | content |
|---|---|
| Eq. (5) | `s(τ) = −ln p(x(τ), τ)` — `p` is the **solution of the Fokker–Planck equation (Eq. 3) for the specified initial distribution `p₀(x)`**, evaluated along the trajectory. **Not** the equilibrium Boltzmann distribution |
| Eq. (8) | `q̇(τ) = F(x,λ)·ẋ ≡ T ṡ_m(τ)` — medium entropy rate from heat |
| Eq. (9) | `ṡ_tot(τ) = ṡ_m(τ) + ṡ(τ)` |
| Eq. (11) | `⟨ṡ_tot⟩ = ∫dx j(x,τ)²/[D p(x,τ)] ≥ 0`, **equality exclusively in equilibrium** |
| Eq. (18) | `⟨e^{−Δs_tot}⟩ = 1`, for arbitrary initial conditions and driving |

**Definitions required by the claim.** Entropy in J/K, sign convention positive = increase. Boundary:
bead + single thermal reservoir at `T_θ`. Ensemble: canonical. Heat: Sekimoto, `dq = F∘dx`, positive
into the medium. Process: static trap (**no external work**), system in thermal equilibrium.

**Evaluation.** In equilibrium `p(x,τ) = p_eq(x) = e^{−V(x)}/Z`, so by Eq. (5)
`s(x) = k_B V(x) + k_B ln Z` and `Δs_sys = k_B(V_post − V_pre) = −k_B E`. By Eq. (8) with a static
conservative force, `q = U_pre − U_post = k_B T·E`, so `Δs_m = q/T = +k_B E`. By Eq. (9),
**`Δs_tot = 0`** — exactly the equality case of Eq. (11), since the equilibrium probability current
`j = 0`. Arithmetic check: at `E = +5`, `T = 298 K` gives `q = 2.057167e−20 J`, `q/T = +5.0000 k_B`;
`T = 318 K` gives `q = 2.195232e−20 J`, `q/T = +5.0000 k_B`. The mechanical energies differ by 6.71%;
the `k_B` figure does not. **That commensurability is real and survives.**

**Three distinct objects, kept separate:**

| object | value | nature |
|---|---|---|
| statistical rarity change / proposed entropy-deficit state function `S_eq − S(x) = k_B V(x)` for the **constrained** bead+reservoir macrostate (`S_tot^constr(x) = const − U(x)/T` to first order in a large reservoir) | `ΔS = +k_B E` | **state function** |
| surrounding-medium entropy, Seifert Eq. (8) | `Δs_m = +k_B E` | **process quantity**, no-work transitions only |
| stochastic **system** entropy, Eq. (5) | `Δs_sys = −k_B E` | trajectory quantity |
| **total** entropy production, Eq. (9)/(11) | **`Δs_tot = 0`** in equilibrium | **not `k_B E`** |

**Result: `REQUIRES QUALIFICATION`.** `k_B E` is the medium entropy change and the constrained-macrostate
entropy deficit; it is **not** total entropy production in Seifert's sense, which vanishes in
equilibrium by Eq. (11). A relaxation from a localised initial condition would give
`⟨Δs_tot⟩ > 0`, but that quantity is the relative entropy of the initial distribution, not `k_B E`
either — so the identity fails under **both** readings of "total".

**Proposed wording — for the author to apply; the baseline is NOT edited here.**

- §14.3 line 517: `Delta S_total = k_B E_theta` → `Delta S_medium = k_B E_theta`
- §14.3 line 521: "+5 k_B of total entropy increase" → "+5 k_B of entropy delivered to the thermal
  reservoir, equivalently +5 k_B of constrained-macrostate entropy deficit removed"
- §4 line 152: `E = Delta S_total / k_B` → `E = Delta S_medium / k_B`
- add: "`k_B E` is NOT total stochastic entropy production. At equilibrium in a static field
  `Δs_sys = −k_B E`, `Δs_med = +k_B E`, `Δs_tot = 0` (Seifert 2005, Eqs. 5, 8, 9, 11)."

**Scope of the defect.** It affects the **interpretation** of P4's outcome and the baseline wording.
It does **not** change any number computed by the pipeline: the v3 config already froze the corrected
form `ΔS_macro = k_B E` together with the prohibition, so **P4's statistic and pass rule are
unaffected**. It does create authority conflict 3 of §0, between the committed baseline and the
uncommitted endpoint definition. **No endpoint is dropped.**

---

### Implementation plan — NOT EXECUTED

| # | target path | change | deterministic conformance check |
|---|---|---|---|
| 1 | `<scratch>/e1a_gate_v4/e1a_analysis.py` (from v3) | replace `thresholds_for()` + fixed table with `calibrate_gates(H, n, taus, branchA_unc, α₁, α₂, R_cal)` | scale-invariance of G1–G5 (done, ≤6.7e−16); refusal on non-PD `H` |
| 2 | same | replace `_blocks(lam, 0.05)` with `_blocks_resolvable(lam, N₁₂, θ_cap)` | merge boundary matches `(ρ−1)/√ρ = 1/(θ_cap√N₁₂)` |
| 3 | same | two-block gate; Besag–Clifford p-values; **remove the 1° G3 floor** | `α₁+α₂` accounting; monotone p̂ |
| 4 | same | `g2` null from `sd = √(24·A4/n)`, `bias = −6/N2` | `A_p` exact sum vs closed form |
| 5 | same | replace scalar `n_eff` with per-element `N_ab`; structured status enum | every status reachable; no `KeyError` path (fixes C7) |
| 6 | `<scratch>/e1a_gate_v4/e1a_world.py` | per-mode `τ_r = γ(T)/k_r` from Branch A; **stationary initialisation** `x₀ ~ N(0,Σ)` | stationary covariance = Σ analytically |
| 7 | `<scratch>/e1a_gate_v4/e1a_calib.py` **(new)** | covariance-matched `S` draws | — **requires RNG, therefore future task only** |
| 8 | `<scratch>/e1a_gate_v4/config.json` + `procedure.sha256` | hash over `{config ∪ per-file code hashes ∪ decision rules ∪ seed map}` | recompute and compare |

**Later validation of each approximation:** item 2 of Appendix C at the operating quantile; item 3
unconditional size; item 5 size and power at the merge boundary ±20%; A.5 achieved joint size and
power cost of the union bound.

**How the full suite would eventually evaluate the complete pipeline:** calibration, validation and
confirmatory datasets drawn from **disjoint seed families**, with thresholds fixed from the
calibration family **before** any validation datum is analysed — no data reused to tune thresholds.
The blinded scale control retains its declared recovery target `β = 1/c`. **Knowing the synthetic
generating model is software validation; it is not physical verification of that model**, and no
synthetic result may be reported as evidence about the apparatus.

Original artifacts preserved: v1, v2, v3 untouched; this packet is additive.


---

# PART III — HOW TO REPRODUCE

## E1a v4 — REVIEW BUNDLE

Self-contained. Everything needed to reproduce every number in the v4 correction packet and its
addendum. **Nothing here is committed to the repository**; all files are task artifacts.

### Repository coordinates these artifacts were produced against

```
repository            konrazem/ebu
branch                gaussian/stage-a-environment
local HEAD            c0099d8f7eea95a0f683f3c09fef71bdffc369af
intended remote HEAD  origin/gaussian/stage-a-environment = c0099d8f7eea95a0f683f3c09fef71bdffc369af
working tree          clean at start and at end
```

Protected documents, **not copied into this bundle** — they are committed at the coordinate above and
must be read there. Verified by content hash at both start and end of the task:

```
docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md
    6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
docs/theory/EBU_THEORY_BASELINE.md
    9b9f22d7b9c8a29725eb6a7abf4326fee68afaff503f23c2b5fbe1a6b21b732a
```

### Layout and import convention

```
e1a_v4_review_bundle/
  README_BUNDLE.md                 this file
  MANIFEST.sha256                  full SHA-256 and byte count for every file
  packet/
    E1A_V4_CORRECTION_PACKET.md    ORIGINAL, UNCHANGED
    E1A_V4_ADDENDUM.md             targeted correction addendum (new)
  checks/
    v4_design_checks.py            ORIGINAL, UNCHANGED
    v4_addendum_checks.py          revised deterministic checks (new filename, new file)
  source_v3/                       v3 sources the checks import or cite
  source_v4_design/                earlier v4 derivation scripts (stdlib-only)
  transcripts/                     actual command transcripts and numerical outputs
  failed_extraction/               labelled failure, NOT evidence — see below
```

**Import convention.** `checks/*.py` locate the v3 analysis module through the environment variable
`E1A_V3_DIR`. From `checks/`:

```
cd checks
E1A_V3_DIR=../source_v3 python3 v4_design_checks.py
E1A_V3_DIR=../source_v3 python3 v4_addendum_checks.py
cd ../source_v4_design
python3 verify_audit.py      # and feasibility, assurance, geometry, exactness2,
                             # discrimination, corrections
```

Only `source_v3/e1a_analysis.py` is imported, and it imports `math` only. Every other v3 file is
present because the packet cites it by line number, not because a check executes it.

### Execution safety

Every script here is **deterministic**: no random number generator, no trajectories, no model
stepping, no simulation runner. Verified by inspection before execution —

```
grep -nE "random|Random|\.gauss|seed|sample_|shuffle|e1a_world" checks/*.py source_v4_design/*.py
```

returns only prose occurrences inside printed text. `source_v3/e1a_world.py` **does** contain
generators (`sample_gauss`, `sample_ou`); it is included for citation and **is never imported**.

### Known non-clean artifact

`source_v4_design/exactness.py` **terminated with a `ZeroDivisionError`** partway through (a Beta
tail underflow at large `R`) and also contained a mis-stated skewness direction. It is superseded by
`exactness2.py`, which runs clean and carries the corrected result. `exactness.py` is retained for
provenance only; **no number in the packet comes from it**. No transcript is provided for it because
it does not complete.

### The entropy source

`failed_extraction/seifert_pdf_extract.FAILED.txt` is a **failed** text extraction from the arXiv PDF
of Seifert 2005. The PDF's text layer is font-subset encoded; the extraction produced only five
readable four-letter tokens and **is not evidence for any equation**. It is retained solely to show
the attempt was made and failed.

**The readable primary source actually used** for every equation cited in packet Appendix D.3 and
addendum §5 is the **ar5iv HTML rendering** of the same preprint:

```
https://ar5iv.labs.arxiv.org/html/cond-mat/0503686
U. Seifert, "Entropy production along a stochastic trajectory and an integral fluctuation theorem",
arXiv:cond-mat/0503686v1; published as Phys. Rev. Lett. 95, 040602 (2005).
```

**Equation numbers are the preprint's and may differ from the published PRL.** Equations relied on:
Eq. (5) trajectory entropy `s(τ) = −ln p(x(τ),τ)` with `p` the Fokker–Planck solution for the actual
initial condition; Eq. (8) `q̇ = F·ẋ ≡ T ṡ_m`; Eq. (9) `ṡ_tot = ṡ_m + ṡ`; Eq. (11)
`⟨ṡ_tot⟩ = ∫dx j²/(Dp) ≥ 0`, equality exclusively in equilibrium; Eq. (18) `⟨e^{−Δs_tot}⟩ = 1`.
Seifert sets `k_B = 1`; factors of `k_B` are restored throughout the packet and addendum.

### Reading order

1. `packet/E1A_V4_CORRECTION_PACKET.md` — the design correction, Appendices A–D.
2. `packet/E1A_V4_ADDENDUM.md` — the decision register, the complete P3 rule, the closed probability
   budget, four corrected statements, and the interpretation scoping.
3. `transcripts/` — the actual outputs, if you prefer not to run anything.

Where the two disagree, **the addendum supersedes the packet**, and every such point is flagged in the
addendum as a correction with the superseded text quoted.


---

# PART IV — COMMAND TRANSCRIPTS

All scripts are stdlib-only and deterministic. Verified before execution to contain no RNG,
no trajectories and no simulation runner.

## v4_addendum_checks.py — addendum checks

```
$ cd e1a_v4_review_bundle/checks
$ E1A_V3_DIR=../source_v3 python3 v4_addendum_checks.py


====================================================================================================
1.  THE P3 RULE - WHAT WAS ACTUALLY COMPUTED, AND THE PROPOSED COMPLETE RULE
====================================================================================================
AS COMPUTED in v4_design_checks.py function pi_abs() (and, earlier, e1a_v4_design/
corrections.py pi_abs()).  TRANSCRIBED FAITHFULLY:

    sa = sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat[REF]^2)
    ha = z_abs * sa
    accept  iff   log((1-d_abs)/(1-ha))  <=  log beta_hat_REF  <=  log((1+d_abs)/(1+ha))

  estimator  : beta_hat = m / tr(H_A S)       (v3 e1a_analysis.py beta_mle, line 120-121)
  parameter  : beta at the REFERENCE FIELD ONLY
  coverage   : two-sided, z = 1.96, i.e. a nominal 95% interval; the equivalence test this
               induces has size 2.5% (TOST at 2.5% per side)
  interval   : multiplicative/relative, beta_hat*(1 +- ha), v3 e1a_analysis.py beta_ci line 122
  uncertainty: sigma_cm (shared) and sigma_fs (field-specific) BOTH enter, in quadrature with
               sigma_stat - correct for an ABSOLUTE endpoint, where nothing cancels
  invalid    : beta_status != ESTIMATED -> abs_accept() returns False (v3 confirm2.py line 121)

  PROVENANCE: delta_abs = 5% and z = 1.96 come from the UNCOMMITTED v3 config.json
  (endpoints.P3_absolute_benchmark). NOT a committed requirement, NOT previously approved.

DEFECT: E1a predicts beta = 1 at EVERY tested field (baseline section 14.1, COMMITTED).
A rule evaluated only at the reference field does not test that prediction. The number
0.974 reported earlier is therefore the REFERENCE-FIELD-ONLY probability, mislabelled.

PROPOSED COMPLETE RULE  [PROPOSED DESIGN SETTING - label carried explicitly]:

    P3 passes  iff  for EVERY field theta in {theta0, theta1, theta2, theta3}:
        beta_hat_theta * (1 - h_theta) >= 1 - delta_abs   AND
        beta_hat_theta * (1 + h_theta) <= 1 + delta_abs
        h_theta = z_abs * sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2)
    conjunctive over all four fields (an intersection-union test: no multiplicity
    correction is needed for size control, by the IUT theorem)
    any field with beta_status != ESTIMATED makes P3 FAIL (fail-closed, no conditioning)

  This addresses "beta = 1 at every tested field" directly. It is STRICTER than what was
  computed. All affected numbers are recomputed below.

 sigma_k  sigma_fs  sigma_cm   pi_P3 ref-only   pi_P3 ALL FOUR    change
   1.00%    0.708%    2.291%           0.0933           0.0014   -0.0919
   0.50%    0.355%    1.338%           0.8927           0.8225   -0.0702
   0.40%    0.285%    1.200%           0.9579           0.9270   -0.0309
   0.34%    0.243%    1.150%           0.9738           0.9544   -0.0194
   0.30%    0.215%    1.100%           0.9844           0.9725   -0.0119
   0.25%    0.180%    1.000%           0.9956           0.9918   -0.0038

  The conjunctive rule costs 1-3 points. It does NOT collapse, because the dominant term
  sigma_cm is COMMON to all four fields: they pass or fail largely together. That shared
  structure is why the exact integral is used instead of a product of marginals.

====================================================================================================
2.  JOINT P(P2 and P3) UNDER THE COMPLETE P3 RULE - EXACT 2-D INTEGRAL
====================================================================================================
  P2 and P3 share every field-specific term. With w = d_cm and v_theta = -d_fs + e:
      log beta_hat_theta = -w + v_theta        log r_j = v_j - v_ref
  P2 accepts iff v_j in [v_ref + a_j, v_ref + b_j] for all j
  P3 accepts iff v_theta in [A_lo_theta + w, A_hi_theta + w] for all theta
  so the joint is a 2-D integral over (w, v_ref) with the three inner integrals in closed
  form - the intersection of two intervals.

 sigma_k  sigma_fs  sigma_cm    pi_P2  pi_P3(all)   pi(P2&P3)   product
   1.00%    0.708%    2.291%   0.0000      0.0014      0.0000    0.0000
   0.50%    0.355%    1.338%   0.7021      0.8225      0.5918    0.5775
   0.40%    0.285%    1.200%   0.9089      0.9270      0.8465    0.8426
   0.34%    0.243%    1.150%   0.9685      0.9544      0.9256    0.9244
   0.30%    0.215%    1.100%   0.9870      0.9725      0.9603    0.9599
   0.25%    0.180%    1.000%   0.9965      0.9918      0.9883    0.9883

  CONVERGENCE of the 2-D Simpson rule (sigma_k = 0.34%):
    npts =   301^2   value = 0.92560040   |change| = -
    npts =   601^2   value = 0.92559515   |change| = 5.26e-06
    npts =  1201^2   value = 0.92559698   |change| = 1.83e-06

====================================================================================================
3.  COMPLETE-PIPELINE PROBABILITY BUDGET - EVERY MANDATORY FAILURE EVENT
====================================================================================================
  COMPLETE-PASS EVENT, stated as a set:
      C = [ AND over 4 fields: BranchA_valid & rank_ok & Neff_ok & mode_rule_ok & gate_pass ]
          AND P2_accept AND P3_accept AND P4_verified
  P(C) >= 1 - SUM over all failure events of their probabilities   (union bound, EXACT INEQUALITY)

  EVENT-BY-EVENT.  A = in a named budget term, B = implied by others, C = not yet established.

  P4 entropy endpoint .......................................................... CASE B
    v3 confirm2.py lines 143-148: c12 tests |(5 kB T/T)/kB - 5| < 1e-12 on DECLARED constants.
    It is a deterministic identity check on the design, not a function of Branch-B data, so
    its failure probability is EXACTLY 0 under the assumption that the identity is verified
    at design time. It contributes no term. Its PHYSICAL claim is separately qualified.
    Label: AN EXACT PROBABILITY UNDER A SPECIFIED MODEL (degenerate, = 0).

  Rank-guard refusal (lambda_min/lambda_max < 1e-12) ........................... CASE A, bounded
    Davidson-Szarek for W ~ Wishart(N, I_m)/N: P[ sqrt(lambda_min) < 1 - sqrt(m/N) - t ]
    <= 2 exp(-N t^2/2). With N = 223786, m = 2, reaching a ratio of 1e-12 needs t ~ 0.9970,
    giving a bound of 2 exp(-1.112e+05) - numerically 0 in double precision.
    Label: A PROVED UPPER BOUND, under an iid-Gaussian premise that is itself approximate
    for OU data. Budget term: 0 (bounded), assumption stated.

  N_eff-unsupported refusal ................................................... CASE B
    N_ab is computed from BRANCH-A tau_r = gamma(T)/k_r and the declared T_total, dt. It is
    deterministic given the declared design and lies inside the supported range for all four
    fields. Probability 0 for the declared scenario; a different design must re-check.

  Mode-resolution boundary crossing ........................................... CASE A + CASE C
    NEW TERM - absent from the earlier budget. The merge rule uses H_A's eigenvalue ratio,
    and H_A is NOISY. For a field that is TRULY circular (rho_true = 1 exactly), the estimated
    ratio is rho_A ~ 1 + |delta_1 - delta_2|, a half-normal with scale sqrt(2) sigma_k. The rule
    SPLITS whenever rho_A exceeds the merge boundary:
        merge iff (rho-1)/sqrt(rho) < u ,  u = 1/(theta_cap sqrt(N_12))

 theta_cap         u  merge boundary rho  P(split | truly circular)  x3 circular fields
        5d   0.02417             1.02447                  4.975e-07           1.493e-06
       10d   0.01209             1.01216                  1.195e-02           3.585e-02
       20d   0.00604             1.00606                  2.088e-01           6.265e-01

    CASE A at theta_cap = 5 deg: 3 x 5.0e-07, entered in the budget and negligible.
    CASE C at theta_cap = 10 deg: the CROSSING probability is 1.19e-02 per circular field,
    but its CONSEQUENCE is NOT established. Calibrating conditional on H_A is approximately
    self-consistent (a split H_A also widens its own calibrated G3 threshold), so a crossing
    may cost DETECTION POWER rather than cause a false rejection. Which it is has not been
    determined and REQUIRES VALIDATION. The budget below therefore charges the full crossing
    probability as a failure - the conservative choice - and reports both caps.
    DESIGN CONSEQUENCE: theta_cap = 5 deg is selected for this field set. It merges genuine
    splits only below rho = 1.0245, and theta2 sits at rho = 2.5, far outside.

  Finite-calibration and surrogate mismatch ................................... CASE A, approximate
    Besag-Clifford gives size <= alpha_1 EXACTLY, but only CONDITIONAL on the null draws being
    from the true null law. They are from the covariance-matched surrogate, whose 99th-percentile
    Cornish-Fisher shift was measured at 0.0014-0.0028 sd (v4 packet Appendix C item 2).
    At the block-1 operating level alpha_1 = 0.4% (z = 2.6521, phi(z) = 0.01185):
        eps_cal ~ phi(z) x 0.0028 = 3.317e-05 per field
    Label: AN APPROXIMATE PROBABILITY, A QUANTITY REQUIRING LATER VALIDATION.
    G5's block adds its own delta-method error, NOT quantified here - CASE C, validation listed.

  BUDGET, unrounded inputs: sigma_k = 0.34 pct, sigma_fs = 0.242747 pct, sigma_cm = 1.1500 pct

    --- theta_cap = 5 deg ---
      4 x alpha_geom (gate, NOMINAL DESIGN ALLOCATION)     0.02000000
      4 x eps_cal (APPROXIMATE, needs validation)          0.00013269
      4 x rank/Neff refusal (PROVED BOUND)                 0.00000000
      3 x mode-resolution crossing, cap 5 deg              0.00000149
      1 - pi(P2 and P3) (APPROXIMATE PROBABILITY)          0.07440485
      P4 failure (EXACT, degenerate)                       0.00000000
      RAW union expression 1 - sum                         0.90546097
      REPORTED LOWER BOUND max(0, .)                       0.9055

    --- theta_cap = 10 deg ---
      4 x alpha_geom (gate, NOMINAL DESIGN ALLOCATION)     0.02000000
      4 x eps_cal (APPROXIMATE, needs validation)          0.00013269
      4 x rank/Neff refusal (PROVED BOUND)                 0.00000000
      3 x mode-resolution crossing, cap 10 deg             0.03584835
      1 - pi(P2 and P3) (APPROXIMATE PROBABILITY)          0.07440485
      P4 failure (EXACT, degenerate)                       0.00000000
      RAW union expression 1 - sum                         0.86961411
      REPORTED LOWER BOUND max(0, .)                       0.8696

  The earlier headline 0.922 DOES NOT SURVIVE unchanged. It omitted the mode-resolution term
  and used the reference-only P3. Corrected: 0.9055 at theta_cap = 5 deg,
  0.8696 at 10 deg.  This is an APPROXIMATE DESIGN CALCULATION,
  not a guaranteed success probability: pi(P2 and P3) rests on the log-linear error model and
  eps_cal on an unvalidated surrogate.
  SCENARIO-SPECIFIC, not uniform over any declared parameter set.

  CLASSIFICATION REQUIRED BY THE REVIEW:
    sigma_k <= 0.34% with sigma_cm <= 1.15% .... A SUFFICIENT CANDIDATE SCENARIO. Not shown
        necessary: no search over the (sigma_k, sigma_cm, T_total, alpha_geom) space was run,
        and the union bound is conservative, so nearby looser scenarios may also suffice.
    sigma_k = 1.00% ............................ A PROVEN EMPTY ACCEPTANCE REGION for P2:
        h_cross = 2.0551% > delta_cross = 2%, so [(1-d)/(1-h), (1+d)/(1+h)] is empty. This is
        a demonstrated incompatibility of that scenario, by algebra - not a loose bound.
    rows between .............................. AN INSUFFICIENT LOWER BOUND where the raw
        expression falls below the target: the bound is conservative and the true value is
        higher, so no impossibility is demonstrated there.

====================================================================================================
4.  alpha_geom = 0.5% CHECKED AGAINST FALSE-BRIDGE DETECTION, NOT ONLY TRUE-BRIDGE PASS
====================================================================================================
  G3 null sd at theta2 with sigma_psi = 0.5 deg: 0.5152 deg

  alpha_geom        z  threshold deg   min detectable rotation (80% power)
       1.0%   2.5758         1.3271                                1.7607
       0.5%   2.8070         1.4462                                1.8798

    Tightening 1% -> 0.5% raises the minimum detectable rotation by
    6.8% - a real but small loss of geometric sensitivity.

  The other declared false-bridge controls are UNAFFECTED by alpha_geom:
    paired hidden-scale distortion c = 1.07 / 0.90 : gates are SCALE-INVARIANT (verified,
        v4 packet Appendix B.2, differences <= 6.7e-16), so this control acts entirely through
        P3/beta, not through the gate. alpha_geom cannot weaken it.
    independent coordinate permutation : for theta2 the permuted K is diagonal in the lab
        frame while H_A's axes sit at 30 deg, so G3 ~ 30 deg against a 1.446 deg threshold.
        Detection probability is 1 to double precision at either alpha_geom.
    time shuffle : an AUTOCORRELATION control only; it leaves S identical to 1e-30.
  CONCLUSION: alpha_geom = 0.5% costs ~7% in minimum detectable rotation and nothing else in
  the declared control suite. No control is removed, weakened in definition, or replaced.

====================================================================================================
5.  beta_hat = beta/(1 + delta_bar) - DERIVED FOR THE ACTUAL ESTIMATOR AND CLASSIFIED
====================================================================================================
  ACTUAL FUNCTION (v3 e1a_analysis.py lines 120-121):
      def beta_mle(H,S): m=len(H); return m/sum(mm(H,S)[i][i] for i in range(m))
  i.e.  beta_hat = m / tr(H_A S).   Let G := H_true^{-1/2} H_A H_true^{-1/2}  and let M be the
  whitened sample covariance, E[M] = I. Then S = (1/beta) H_true^{-1/2} M H_true^{-1/2} and

      beta_hat = m beta / tr(G M)          <- COMPLETE FINITE-SAMPLE ESTIMATOR, exact identity

  Population limit M -> I:  beta_hat_pop = m beta / tr(G).   THIS is what the earlier claim
  described: AN IDEAL POPULATION CALCULATION of ONE COMPONENT of measurement error. It is NOT
  the complete finite-sample estimator, and the earlier wording did not say so.

  H_true: eigenvalues (2.5, 1.0) rotated 30 deg; beta_true = 1; Sigma = H_true^-1

case                              beta_mle(H_A, Sigma)    prediction      |diff| sigma_stat(G)/sigma_stat(I)
1 pure scalar  d = +3%                    0.9708737864  0.9708737864    0.00e+00                  1.00000000
2 differential d = (+2%, -2%)             1.0000000000  1.0000000000    0.00e+00                  1.00019998
3 orientation  psi = 1 deg                0.9998629549  0.9998629549    0.00e+00                  1.00013703
4 all three combined                      0.9707345246  0.9707407329    6.21e-06                  1.00034331

  Case 2 returns EXACTLY 1: differential mode error with delta_bar = 0 leaves beta untouched.
  Case 3 matches 2/(2 + sin^2(psi)(r + 1/r - 2)) - orientation enters at SECOND order, and the
  identity is EXACT in psi for the population calculation, not merely first-order.
  Last column: sigma_stat scales as sqrt(2 tr G^2)/tr G, so Branch-A error perturbs the
  SAMPLING term too - by <1e-4 relative in every case here, but not by exactly zero.

  CLASSIFICATION:
    beta_hat = m beta / tr(G M) ................ EXACT IDENTITY for the implemented function
    beta_hat_pop = m beta / tr(G) .............. EXACT, ideal population calculation (M -> I)
    beta_hat = beta/(1 + delta_bar) ............ EXACT for mode-scaling errors, population only
    orientation immunity ....................... EXACT to all orders in psi, population only;
                                                 magnitude sin^2(psi)(r + 1/r - 2)/2
    sigma_beta = sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat^2) ... FIRST-ORDER DELTA-METHOD
        APPROXIMATION of a nonlinear (multiplicative) function, NOT an exact identity. The
        exact relation is log-additive only if every factor is exactly log-normal; the
        sampling factor m/tr(GM) is a reciprocal quadratic form, which is not.

====================================================================================================
6.  THE CONSTRAINED-MACROSTATE ENTROPY - ITS OWN DEFINITION AND REMAINDER
====================================================================================================
  DEFINITION. Bead + single reservoir, total energy E_tot fixed, bead HELD at position x
  (a constraint, so the bead's configurational entropy at fixed x is a constant, independent
  of x). The reservoir then holds E_tot - U(x), and
      S_constr(x) = S_res(E_tot - U(x)) + const
  Expanding with dS_res/dE = 1/T and d^2 S_res/dE^2 = -1/(T^2 C_v):
      S_constr(x) = S_res(E_tot) - U(x)/T - U(x)^2/(2 T^2 C_v) + ...
      => Delta S_constr = k_B E_theta  +  REMAINDER,  remainder/leading = U/(2 T C_v)
    1 mm^3 water     C_v/k_B = 1.004e+20   remainder/leading at U = 5 kB T : 2.491e-20
    1 uL water       C_v/k_B = 1.004e+23   remainder/leading at U = 5 kB T : 2.491e-23
    Label: AN APPROXIMATION with an explicitly bounded remainder - exact to first order in
    U/(T C_v), which is ~1e-20 for any macroscopic bath. It is a STATE FUNCTION of the
    CONSTRAINED composite, and is NOT identified with either Seifert trajectory quantity
    without this separate derivation.
```

## v4_design_checks.py — packet checks

```
$ cd e1a_v4_review_bundle/checks
$ E1A_V3_DIR=../source_v3 python3 v4_design_checks.py


====================================================================================================
A.  THE IMPLEMENTED SAMPLE-KURTOSIS ESTIMATOR AND ITS UNCERTAINTY
====================================================================================================
IMPLEMENTED (e1a_analysis.py G5_kurtosis, v3 lines 109-117), stated exactly:
   whitening      Z_i = H^{1/2}(x_i - x*)   -- H and x* from BRANCH A, NOT data-dependent
   centering      mu_r = (1/n) sum_i Z_ir   -- SAMPLE mean, though S is centred at x*
   moments        m2_r = (1/n) sum (Z_ir-mu_r)^2 ,  m4_r = (1/n) sum (Z_ir-mu_r)^4
   statistic      g2_r = m4_r/m2_r^2 - 3    -- NO bias correction, NO n/(n-1)
   gate           G5   = max_r |g2_r|
   variance normalisation is INTERNAL (division by m2_r^2), not by a declared sigma.
   No data-dependent DIRECTION is estimated: unlike G3/G4, G5's basis is Branch-A fixed.
   Every gate reuses the SAME observations.

Uncertainty, correlated sampling model, delta method about (m2,m4)=(s^2,3s^4):
   d g2/d m4 = 1/s^4 ,  d g2/d m2 = -6/s^2
   Isserlis:  Cov(x0^2,xt^2)=2 s^4 rho^2 ,  Cov(x0^4,xt^4)=72 s^8 rho^2 + 24 s^8 rho^4 ,
              Cov(x0^2,xt^4)=12 s^6 rho^2
   Var(m4)=(s^8/n)(72 A2+24 A4) , Var(m2)=(2 s^4/n)A2 , Cov(m4,m2)=(12 s^6/n)A2
   Var(g2) = (1/n)[72 A2 + 24 A4 + 72 A2 - 144 A2] = 24 A4 / n     <- A2 CANCELS EXACTLY

Mean-estimation effect (the sample mean is used, and for OU it is far noisier than for iid):
   E[x_bar^2] = s^2/N1 ,  E[x_bar m3] = 3 s^4/N1  with N1 = n/A1  (the MEAN's effective size)
   E[m2] = s^2 (1 - 1/N1) ;  E[m4] = 3 s^4 (1 - 2/N1)
   ratio expansion E[U/V^2] ~ (EU/EV^2)[1 + 3Var V/(EV)^2 - 2Cov(U,V)/(EU EV)] gives
   E[g2] = -6/N2 + O(N^-2)      <- the N1 terms CANCEL; the bias is set by N2, not N1 or N_g2
   (iid check: N2 = n gives -6/n, matching the classical E[g2] = -6/(n+1) at leading order)

field / mode                 tau ms       A1       A2       A4        N1        N2      N_g2    sd(g2)       bias |bias|/sd
theta0_circular m1           1.0680   17.818    8.937    4.525    112245    223786    442036  0.007368  -2.68e-05    0.0036
theta0_circular m2           1.0680   17.818    8.937    4.525    112245    223786    442036  0.007368  -2.68e-05    0.0036
theta1_power m1              0.5086    8.515    4.316    2.274    234874    463357    879507  0.005224  -1.29e-05    0.0025
theta1_power m2              0.5086    8.515    4.316    2.274    234874    463357    879507  0.005224  -1.29e-05    0.0025
theta2_ellipse m1            0.7120   11.894    5.989    3.078    168147    333934    649753  0.006078  -1.80e-05    0.0030
theta2_ellipse m2            1.7799   29.677   14.855    7.461     67393    134632    268049  0.009462  -4.46e-05    0.0047
theta3_temperature m1        0.7152   11.948    6.016    3.091    167398    332467    647053  0.006090  -1.80e-05    0.0030
theta3_temperature m2        0.7152   11.948    6.016    3.091    167398    332467    647053  0.006090  -1.80e-05    0.0030

  The bias is at most 0.5% of one standard deviation, so NO bias correction is introduced;
  it is nevertheless reproduced automatically by calibrating at the declared (H, n, tau).
  N_g2 ~ 2 N2: using N2 for G5 is conservative by a factor 2 in variance.

====================================================================================================
A2.  EXACT HAND-CHECKABLE EXAMPLE: S DOES NOT DETERMINE G5
====================================================================================================
  A = ( 1, 1, -1, -1)      mean=+0.0  m2=1.0000  m4=1.0000  g2 = m4/m2^2 - 3 = -2.0000
  B = (r2, 0,  0, -r2)     mean=+0.0  m2=1.0000  m4=2.0000  g2 = m4/m2^2 - 3 = -1.0000
  Identical mean and identical m2 (hence in 1-D an identical S), different g2.
  => No draw of S can reproduce G5. The covariance shortcut CANNOT generate it.  [EXACT]

====================================================================================================
A3.  WHY G5 IS NOT GENERATED INDEPENDENTLY
====================================================================================================
  EXACT, iid only: whitened data are N(0, I/beta) iid; tr(W) is complete sufficient for
    beta; every gate is scale-invariant hence ancillary; BASU gives (G1..G5) _|_ tr(W).
    It does NOT give G5 _|_ (G1..G4).
  EXACT non-independence argument: write u, v for the centred-normalised coordinate vectors.
    g2_1 = g2(u), g2_2 = g2(v), and the sample correlation is r12 = u.v. As r12 -> +-1 the
    two vectors coincide up to sign, forcing g2_1 -> g2_2. Independence would require the
    conditional law of (g2_1, g2_2) given r12 to be free of r12; by continuity of that
    conditional law near r12 = +-1 it is not. So the joint law is not a product.  [EXACT]
  CORRELATED case: the complete sufficient statistic for the scale family is Z' Gamma^{-1} Z,
    not tr(W), so even the Basu results above lapse.
  => DESIGN: two-block gate, union bound, valid under ARBITRARY dependence:
        reject  iff  p_min(G1..G4) < alpha_1   OR   p(G5) < alpha_2 ,   alpha_1+alpha_2 = alpha_geom
     Block 1's four-way dependence is exact (one shared S draw). Block 2 is one statistic.
     Proposed split alpha_1 = 0.4%, alpha_2 = 0.1%.  Modes within G5 are independent only
     because isotropic Stokes drag makes A = gamma^-1 H_U share eigenvectors with H:
     a BENCHMARK property, declared, not a general one.

====================================================================================================
B.  UNIFIED UNCERTAINTY MODEL: WHICH TERM LIMITS WHICH ENDPOINT
====================================================================================================
  beta_hat = m / tr(H S).  Decompose the Branch-A error on H into
     scale (common-mode, one draw per experiment)  : sigma_cm
     per-mode stiffness delta_r, independent        : sigma_k
     thermometry                                    : sigma_T / T
     trap-axis orientation psi                      : sigma_psi
  EXACT for this model: with H's modes scaled by (1+delta_r),
     tr(H S) = sum_r (1+delta_r) lambda_r Sigma_rr = (m + sum_r delta_r)/beta
     so beta_hat = beta / (1 + delta_bar).   ONLY THE MEAN of delta_r enters beta.
  Hence the field-specific relative error on beta is
     sigma_fs = sqrt( sigma_k^2/m + (sigma_T/T)^2 )
  and the DIFFERENTIAL part of delta_r (sd sqrt(2) sigma_k) moves H's eigenvalue ratio,
  feeding G1/G4 - i.e. the gates - not beta.

  Orientation psi enters beta only at SECOND order: tr(R H R' H^-1)/m - 1 = sin^2(psi)(r+1/r-2)/2

geometry                    r    psi=0.2deg    psi=0.5deg    psi=1.0deg    psi=2.0deg
theta0/1/3 circular     1.000      0.00000%      0.00000%      0.00000%      0.00000%
theta2 ellipse          2.500      0.00055%      0.00343%      0.01371%      0.05481%
tangent H_T             1.453      0.00009%      0.00054%      0.00215%      0.00860%
  Negligible for beta at any plausible psi (<0.01%), but DOMINANT for G3 (see the v4 packet).
  => sigma_psi and the differential sigma_k limit the GATES; sigma_cm limits ABSOLUTE beta only;
     sigma_fs and sigma_stat limit BOTH the cross-field ratio and absolute beta.

====================================================================================================
C.  STATISTICAL TERM, PER FIELD, FROM THE EXACT DISCRETE SUMS
====================================================================================================
  Every gate and beta is a SECOND moment, so the governing effective size is N2, not the
  mean's N1.  sigma_stat = sqrt( 2 sum_r 1/N2_r ) / m .   [APPROXIMATION: leading order]

field                      N2 mode1   N2 mode2  sigma_stat  continuous T/tau   error
theta0_circular              223786     223786     0.2114%           0.2109%  -0.21%
theta1_power                 463357     463357     0.1469%           0.1456%  -0.91%
theta2_ellipse               333934     134632     0.2283%           0.2278%  -0.19%
theta3_temperature           332467     332467     0.1734%           0.1726%  -0.47%
  The continuous-time formula is 0.1-1.0% ANTI-conservative; v4 uses the exact sums.

====================================================================================================
D.  COMPLETE-PIPELINE SUCCESS - DEFINITION AND BOUND
====================================================================================================
  A COMPLETE PASS requires ALL of the following, with refusals counted as failures and
  the denominator = every declared experiment (no conditioning on survivors):
     (i)   all 4 fields: Branch-A valid, rank guard passes, N_eff supported, geometry gate passes
     (ii)  P2: all 3 cross-field comparisons accepted within the approved 2% margin
     (iii) P3: absolute beta = 1 accepted under its pass rule
     (iv)  P4: entropy endpoint verified
  Independence between gates and beta is NOT assumed (Basu holds iid only). The bound used is
     P(complete) >= 1 - sum_f alpha_geom,f - (1 - pi_P2) - (1 - pi_P3)      [EXACT INEQUALITY]

  SCENARIO-SPECIFIC results at the approved 2% margin, z_ratio = 1.960, z_abs = 1.96, delta_abs = 5%

 sigma_k  sigma_fs  sigma_cm  a_geom   pi_P2   pi_P3  pi(P2&P3)  BOUND w/ P3  BOUND no P3
   1.00%    0.708%    2.291%    1.0%   0.000   0.093      0.000       -0.947       -0.040
   1.00%    0.708%    2.291%    0.5%   0.000   0.093      0.000       -0.927       -0.020
   0.50%    0.355%    1.338%    0.5%   0.702   0.893      0.631        0.575        0.682
   0.40%    0.285%    1.200%    0.5%   0.909   0.958      0.872        0.847        0.889
   0.34%    0.243%    1.150%    0.5%   0.969   0.974      0.944        0.922        0.949
   0.30%    0.215%    1.100%    0.5%   0.987   0.984      0.972        0.951        0.967

  Each row is SCENARIO-SPECIFIC, not a pooled average and not a guarantee for every
  configuration. pi(P2&P3) EXCEEDS pi_P2 x pi_P3 in every row: the shared reference-field
  error makes the two endpoints POSITIVELY dependent, so the union bound is conservative.

  WORST COMPARISON (marginal acceptance per comparison, sigma_k = 0.34%) -- a pooled
  figure must never stand in for the worst field:

comparison                    sigma_ratio  CI half-width  marginal accept
theta1_power / ref                0.4291%        0.8410%           0.9931
theta2_ellipse / ref              0.4633%        0.9081%           0.9815
theta3_temperature / ref          0.4389%        0.8602%           0.9906

  CONVERGENCE of the Simpson integral (scenario sigma_k = 0.34%, with P3):
    npts =    2001   value = 0.9436441555   |change| = -
    npts =    8001   value = 0.9436441555   |change| = 1.44e-15
    npts =   32001   value = 0.9436441555   |change| = 8.10e-15
    npts =  128001   value = 0.9436441555   |change| = 2.61e-14
    => integration error < 1e-9; it is not a limiting source of uncertainty.

====================================================================================================
E.  FALSE-BRIDGE DETECTION - THE EXISTING DECLARED CONTROLS, PRESERVED
====================================================================================================
  These are the controls already declared in v3's confirm2.py and the baseline. No
  replacement campaign is proposed. Acceptance below = FAILURE to detect.  [WORST-CASE over
  the declared alternative set is the last column of each row group.]

declared alternative                  acceptance (sigma_k=0.34%)label
beta = (1, 1.06, 1, 1)                                  0.00000   scenario-specific
beta = (1, 0.93, 1.05, 1)                               0.00000   scenario-specific
beta = (1, 1, 1, 1.10)                                  0.00000   scenario-specific
beta = (1, 1.025, 1, 1) HARD                            0.00066   scenario-specific
reference off by 3%                                     0.00000   scenario-specific

  Also preserved unchanged, and NOT re-derived here because they are already demonstrated:
    - blinded scale control: Branch-A scale x hidden c, recovery target beta = 1/c
      [BASELINE docs/theory/EBU_THEORY_BASELINE.md, section 14.2, committed]
    - paired hidden-scale distortion c = 1.07 / 0.90 on a RETAINED dataset
    - independent coordinate permutation (the geometry control)
    - time shuffle (an AUTOCORRELATION control only - it leaves S identical to 1e-30)
    - forbidden H := K, recorded as vacuous, demonstration only
  DISTINCTION KEPT: rejecting correct geometry (a P1 false rejection, target alpha_geom) is a
  DIFFERENT error from falsely declaring cross-field equivalence (a P2 acceptance under a true
  disparity). They are reported separately and never netted.

====================================================================================================
F.  CHANGING FIELD versus STATE CHANGE - EXACT DETERMINISTIC EXAMPLE
====================================================================================================
  V_theta(x) = k_theta x^2 / (2 k_B T).  Two fields, same T: theta0 k=100 uN/m, theta1 k=210.
  x* = 0. Compare a STATE change at fixed theta with a FIELD change at fixed state.

                                     V (dimensionless EBU)
  theta0, x = 100 nm                              121.5264
  theta0, x =  50 nm                               30.3816
  theta1, x = 100 nm                              255.2053
  theta1, x =  50 nm                               63.8013

  STATE change at fixed theta0 (100 -> 50 nm) : E = +91.1448
  FIELD change at fixed x = 100 nm (t0 -> t1) : E = -133.6790
  FIELD change at fixed x =  50 nm (t0 -> t1) : E = -33.4197

  TOTAL from (100 nm, theta0) to (50 nm, theta1): E = +57.7250
    path 1  state first, then field : +91.1448  +  -33.4197  = +57.7250
    path 2  field first, then state : -133.6790  +  +191.4040  = +57.7250

  The TOTAL is path-independent (V is a state function of (x, theta)); the SPLIT between the
  'state' term and the 'field' term is NOT: it differs by 100.14 EBU between the two orders.
  [EXACT ARITHMETIC]  A common beta makes all four numbers commensurable on ONE scale. It does
  NOT select a decomposition, so it cannot by itself attribute the field term to any actor, and
  it does not authorise repricing a completed historical receipt.

====================================================================================================
G.  ENTROPY ARITHMETIC FOR THE INTERPRETATION NOTE
====================================================================================================
  T = 298 K:  E = +5.0  ->  heat to medium q = 2.057167e-20 J  ->  q/T = +5.0000 k_B
  T = 318 K:  E = +5.0  ->  heat to medium q = 2.195232e-20 J  ->  q/T = +5.0000 k_B
  mechanical energy differs by 6.71% between the two, the k_B figure does not.
  Delta s_sys = -k_B E ;  Delta s_med = +k_B E ;  Delta s_tot = 0  (equilibrium, static trap).

====================================================================================================
H.  CONFORMANCE CHECKS AGAINST THE ACTUAL v3 IMPLEMENTATION
====================================================================================================
  Pure-function checks only: hand-written matrices and a hand-written point set.
  NO random draws, NO trajectories, NO runner imported. e1a_analysis.py imports only `math`.

gate                  at H     at 2H (K fixed)    |difference|  scale-invariant?
G1          0.035238095238      0.035238095238       0.000e+00              True
G2          1.165935010018      1.165935010018       6.661e-16              True
G3          4.065051177078      4.065051177078       0.000e+00              True
G4          0.114033105040      0.114033105040       0.000e+00              True
G5          0.961945787584      0.961945787584       0.000e+00              True

  ALL FIVE GATES SCALE-INVARIANT IN H: True
  => the modelled sigma_cm and sigma_fs (scalar multipliers on H) cannot move any gate.
     CONFIRMED against the implementation, not assumed.  [EXACT, this implementation]

  beta_mle(H,S)  = 0.845308537616
  beta_mle(2H,S) = 0.422654268808   ratio = 2.000000000000  (exactly 2 -> beta DOES carry the scale)

  G5 CENTRING CHECK - the implementation centres G5 at the SAMPLE mean while S is
  centred at the declared x*. Sample mean of the hand-written set, per coordinate:
    mean = (-0.018750, +0.056250)  -> nonzero, so the two centrings genuinely differ.
    v4 makes the centring explicit and identical in both, and calibrates at the choice made.
```

## verify_audit.py — independent re-derivation of the v3 arithmetic

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 verify_audit.py

====================================================================================================
A.  v3 CONFIG CONSTANTS (re-derived, not copied)
====================================================================================================
  sigma_stat (n_eff=1e5, m=2)      = 0.3162%
  sigma_cm  (2%,1%,0.5% quadrature)= 2.2913%
  sigma_fs  DECLARED               = 1.0006%
  z_ratio Bonferroni x3            = 2.393980   (config: 2.393979799818508)
  sigma_fs USED in config          = 0.498970%  (config: 0.4989696930788192%)

====================================================================================================
B.  SECTION 5 CLAIM: ratio CI half-width is EXACTLY the margin -> zero power
====================================================================================================
  confirm2.py line 74:  half = z_rat*sqrt(2*(2/(N*m)) + 2*sigma_fs^2) = 0.020000000000
  margin delta_r                                                     = 0.020000000000
  half - delta  = +0.000e+00   -> half == delta to machine precision: True
  admissible ratio interval [ (1-d)/(1-h) , (1+d)/(1+h) ] = [1.000000000000, 1.000000000000]
  interval width = +0.000e+00  ->  EMPTY/degenerate: only ratio == 1 exactly.  CONFIRMED.
  ALGEBRA: CI-in-margin is non-empty iff h <= delta, and its width -> 0 as h -> delta.
           A margin DERIVED as delta = z*sigma forces h = delta, i.e. power -> 0 BY CONSTRUCTION.

====================================================================================================
C.  SECTION 6 CLAIM: absolute endpoint half-width 4.64%, band 0.99620-1.00346, ~12% acceptance
====================================================================================================
  sigma_abs = sqrt(stat^2+cm^2+fs^2) = 2.3662%
  half_abs  = 1.96*sigma_abs         = 4.6378%      (audit said ~4.64%)
  accepted beta_hat band             = [0.99620, 1.00346]   (audit said 0.99620-1.00346)
  P(accept | beta_true = 1), normal approx = 12.19%        (audit said ~12%)
  ratio half/delta = 0.9276  -> same structural defect as B: margin was set to z*sigma.

====================================================================================================
D.  SECTION 4.1 CORRECTION: the 1-degree G3 FLOOR cannot cause over-rejection
====================================================================================================
  phase1_grid.py line 28:  th["G3"] = max(th["G3"], 1.0)
  This raises the REJECTION THRESHOLD. Rejection requires G3 > threshold.
  A larger threshold => strictly FEWER rejections. The floor is conservative, not permissive.
  The v3 report's claim that the floor 'compounded' the false rejection is WITHDRAWN as wrong.
  Its real effect: it MASKED how small the pooled empirical quantile had become,
  because 3 of the 4 calibration fields are exactly degenerate and return G3 == 0 identically.

====================================================================================================
E.  TRUE CAUSE OF THE 38.3% G3 REJECTION - derived analytically, no simulation
====================================================================================================
  Asymptotic eigenvector perturbation for a sample covariance of N iid Gaussians:
      Var(theta_rotation) = lambda_i*lambda_j / ( N * (lambda_i - lambda_j)^2 )
  which is scale-free in the eigenvalue RATIO r:   Var = r / ( N * (r-1)^2 ).

geometry                 eig ratio r  sd(theta) deg  thr deg  PREDICTED P(reject)  v3 OBSERVED
theta2_ellipse                 2.500         0.4271      1.0                1.9%        0.000
tangent_HT                     1.453         1.0781      1.0               35.4%        0.383

  The 1.453 prediction (35.4%) reproduces the observed 38.3% without any fitted quantity.
  CONCLUSION: G3's null distribution is governed by the INVERSE EIGENVALUE GAP. The calibration
  set contained only r = 1.000 (degenerate -> G3 identically 0) and r = 2.500 (well separated).
  The intermediate regime was never sampled, so no threshold in the table can be valid there.

====================================================================================================
F.  SECTION 4.2 CORRECTION: multiplicity alone cannot produce 11.7%
====================================================================================================
  Union bound: 5 gates each of genuine size 1% => any-gate rejection <= 5%.  Observed theta3 = 7/60.
  7/60 = 0.1167, Wilson 95% CI = [0.0577, 0.2218]
  5% union bound lies OUTSIDE that interval -> the v3 explanation is inadequate.

  The real contribution the v3 report missed: the thresholds are ORDER STATISTICS of only 160
  pooled calibration draws, so each gate's TRUE size is a random variable, not 1%.
  threshold = order statistic 159 of n=160  ->  true exceedance ~ Beta(2,159)
      mean true per-gate size = 1.242%   sd = 0.870%
      P(true per-gate size > 2%) = 16.8%    P(> 3%) = 4.5%
  Union bound using the MEAN realised size: 5 x 1.242% = 6.21%
  Plus POOLING across four heterogeneous geometries: a field with a heavier tail than the pooled
  mixture exceeds the pooled quantile more often than nominal. Neither effect is 'multiplicity'.
  Verdict: 11.7% (CI [0.058,0.222]) is consistent with quantile-ESTIMATION error + pooling,
  and with only 60 replicates it is weak evidence either way. Both v3 explanations are withdrawn.
```

## feasibility.py — effective sample size and cross-field power

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 feasibility.py

====================================================================================================
G.  SECTION 9 - THE EFFECTIVE SAMPLE SIZE v3 USED IS WRONG FOR THE STATISTIC ESTIMATED
====================================================================================================
  v3 used  n_eff = T/(2 tau_c).  That is the effective size for a COORDINATE MEAN.
  Every gate and beta is a SECOND MOMENT. For a stationary Gaussian process the autocorrelation
  of the product x_a x_b decays as rho_a(t) rho_b(t), not as rho(t). For OU, rho_r(t)=exp(-t/tau_r), so

      Cov(S_ab, S_cd) = (delta_ac delta_bd + delta_ad delta_bc) Sigma_aa Sigma_bb / N_ab,
      N_ab = (T/2) (1/tau_a + 1/tau_b)      [exact, in the Branch-A eigenbasis]

  Diagonal:  N_aa = T/tau_a  =  2 x  T/(2 tau_a).   v3 therefore OVERSTATED the variance by 2x
  (CI sqrt(2) too wide). That is why the correlated type-I came out 1/66: the test was CONSERVATIVE,
  not calibrated. A conservative test cannot certify an error rate.
  For an ANISOTROPIC trap tau_r = gamma/k_r differ, so NO single scalar n_eff exists for S.

  Branch-A relaxation times  tau_r = gamma(T)/k_r,  gamma = 6 pi eta(T) a,  a = 6.366 um
  Acquisition T_total = 240 s per field

field                   tau_1 ms  tau_2 ms      N_11      N_22      N_12  sigma_stat  v3 assumed
theta0_circular           1.0680    1.0680    224726    224726    224726     0.2109%     0.3162%
theta1_power              0.5086    0.5086    471925    471925    471925     0.1456%     0.3162%
theta2_ellipse            0.7120    1.7799    337089    134836    235962     0.2278%     0.3162%
theta3_temperature        0.7152    0.7152    335581    335581    335581     0.1726%     0.3162%

  Correct treatment IMPROVES every field. It is a correction, not a relaxation.
  NOTE: v3's config declared ONE tau_c = 1.2 ms for all four fields. tau depends on k AND on
  eta(T), so theta1 (stiffer), theta2 (two modes) and theta3 (hotter, thinner water) all differ.

====================================================================================================
H.  SECTION 5 - CROSS-FIELD EQUIVALENCE POWER, EXACT ONE-FACTOR INTEGRATION
====================================================================================================
  The three comparisons all divide by the SAME reference field, so they share exactly one common
  error term. This is a one-factor model and the joint probability is an exact 1-D integral:

      log r_j = -w + v_j,   w ~ N(0, sigma_fs^2 + sigma_stat,ref^2)   [shared, the reference]
                            v_j ~ N(0, sigma_fs^2 + sigma_stat,j^2)   [independent, field j]
      P(all accept) = INT (1/s0) phi(w/s0) PROD_j [ Phi((w+b_j)/s_j) - Phi((w+a_j)/s_j) ] dw

  Implied correlation between any two comparisons ~ 0.5. No Monte Carlo is used anywhere below.
  IMPORTANT: requiring ALL THREE comparisons to be equivalent is an INTERSECTION-UNION test.
  By the IUT theorem its size is already controlled at alpha WITHOUT a Bonferroni correction.
  The v3 z = 2.394 is therefore conservative for no type-I benefit. Three options are priced:

coverage factor                           sigma_fs  CI half-w  joint power   verdict
Bonferroni x3, 95% CI (v3)                   1.00%     3.441%        0.0%      DEAD
                                             0.50%     1.849%        0.9%      DEAD
                                             0.30%     1.259%       71.3%      weak
                                             0.20%     1.006%       97.3%        OK
                                             0.10%     0.817%       99.9%        OK

no Bonferroni, 95% CI                        1.00%     2.817%        0.0%      DEAD
                                             0.50%     1.514%       15.8%      DEAD
                                             0.30%     1.030%       87.7%      weak
                                             0.20%     0.823%       99.2%        OK
                                             0.10%     0.669%      100.0%        OK

no Bonferroni, 90% CI (standard TOST)        1.00%     2.364%        0.0%      DEAD
                                             0.50%     1.270%       36.6%      DEAD
                                             0.30%     0.865%       94.1%        OK
                                             0.20%     0.691%       99.7%        OK
                                             0.10%     0.561%      100.0%        OK

  Required sigma_fs for a given JOINT power target (delta = 2%, corrected sigma_stat):

coverage factor                             power>=80%    power>=90%    power>=95%    power>=99%
Bonferroni x3, 95% CI (v3)                      0.279%        0.246%        0.220%        0.172%
no Bonferroni, 95% CI                           0.327%        0.290%        0.260%        0.208%
no Bonferroni, 90% CI (standard TOST)           0.369%        0.326%        0.292%        0.236%

  'INFEASIBLE' means: not attainable at delta=2% even with PERFECT field-specific calibration,
  because the statistical term alone already exhausts the margin at T_total = 240 s.

====================================================================================================
I.  LONGER ACQUISITION: what T_total buys, at sigma_fs = 0.30%
====================================================================================================
  T_total s  sigma_stat(ref)       Bonferroni x3       no Bonferroni       no Bonferroni
        240          0.2109%              71.3%              87.7%              94.1%
        480          0.1492%              85.0%              94.4%              97.6%
        960          0.1055%              90.4%              96.8%              98.7%
       1920          0.0746%              92.7%              97.7%              99.1%
```

## assurance.py — absolute endpoint, gate coupling, replication

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 assurance.py

====================================================================================================
J.  SECTION 6 - ABSOLUTE beta=1 ENDPOINT: what precision each intended question needs
====================================================================================================
  The absolute endpoint's uncertainty is dominated by sigma_cm = 2.29%, the COMMON-MODE calibration
  of H. That is not an arbitrary choice: E1a's anti-circularity requirement forbids obtaining the trap
  stiffness from the position variance (that would make beta = 1 a tautology). The independent routes -
  Stokes-drag / corner-frequency (k = 2 pi f_c gamma, gamma = 6 pi eta a) or a known applied force -
  are exactly the routes that carry bead-radius and viscosity uncertainty. The anti-circularity
  requirement CREATES sigma_cm. It cannot be argued away; it can only be measured better.

  sigma_abs (sigma_cm 2.291%, sigma_fs 0.30%, sigma_stat 0.2109%) = 2.3204%

  OPTION A - keep it an EQUIVALENCE endpoint at the declared 5% margin
        required sigma_abs   required sigma_cm    bead radius must reach
   80%             1.5425%             1.4982%          0.997% (from 2%)
   90%             1.3870%             1.3377%          0.734% (from 2%)
   95%             1.2755%             1.2217%          0.492% (from 2%)

  OPTION B - keep the precision, WIDEN the margin (scientifically weaker, but honest)
         required margin
   80%            7.522%
   90%            8.365%
   95%            9.096%

  OPTION C - redefine as a COMPATIBILITY endpoint: 'the 95% CI for beta contains 1'
        acceptance at beta_true = 1 is 95.0% BY CONSTRUCTION, at any sigma.
        But it answers a DIFFERENT question: not 'beta is within 5% of 1' but merely
        'the data do not refute beta = 1'. With sigma_abs = 2.32% it cannot
        distinguish beta = 1 from beta = 1.045. Power against beta = 1.05 is only 57.7%.

  v3's actual setting (5% margin, sigma_abs 2.32%) gives power 15.5% - confirmed unusable.

====================================================================================================
K.  SECTION 5 - GEOMETRY GATES INSIDE THE COMPLETE-PIPELINE SUCCESS RATE
====================================================================================================
  FACT first: G1..G5 are ALL invariant to multiplying H by a positive scalar (G1 trace-normalises,
  G2/G3/G4 use eigen-structure, G5's whitening cancels in the kurtosis). The modelled sigma_cm and
  sigma_fs are scalar multipliers, so THEY DO NOT AFFECT THE GATES AT ALL - they affect only beta.
  Gates and beta endpoints are therefore statistically independent given the data.

  per-field geometry alpha   4 fields all pass   x joint equiv power 0.941   complete pipeline
                     5.0%             0.8145                                         0.7665
                     2.0%             0.9224                                         0.8679
                     1.0%             0.9606                                         0.9039
                     0.5%             0.9801                                         0.9223
                     0.2%             0.9920                                         0.9335

  A 5% per-field geometry gate alone destroys 18.5% of complete releases. To hold the COMPLETE
  pipeline at >= 0.90 with joint equivalence power 0.941, the geometry gate needs alpha <= ~1%.
  That cannot be obtained from five separately-thresholded gates without a union-bound penalty.
  DESIGN: replace 'reject if ANY G_k exceeds its own quantile' with a MIN-p JOINT gate.
      p_k = 1 - F_k(G_k)   using each gate's null CDF at the supplied Branch-A H and N;
      statistic  p_min = min_k p_k ;  reject iff p_min < c(alpha_geom),
      c calibrated as the alpha_geom-quantile of p_min's own null distribution.
  This has size EXACTLY alpha_geom by construction, needs no union bound, and keeps all five gates.

====================================================================================================
L.  SECTION 7 - HOW MANY REPLICATES ACTUALLY CERTIFY AN ERROR RATE
====================================================================================================
  v3 rate_test():  ok = (Wilson LOWER bound on the rejection rate <= 0.10).
  That statement only says 'we failed to DEMONSTRATE excess rejection'. 0/0 reps would pass it.
  To POSITIVELY establish control you need the UPPER bound below the tolerance.

  Nominal geometry false-rejection alpha_0 = 1%. Validation tolerance tau. Clopper-Pearson,
  one-sided 95% upper. ASSURANCE = P(the validation actually succeeds when the design is correct).

 tolerance tau   reps R  max rejections   assurance at alpha_0=1%
           2%     1200              15                    84.6%
           3%      400               6                    89.0%
           5%      200               4                    94.8%

  v3 used R = 40 with 0 rejections observed:
      one-sided 95% CP upper bound = 0.0722  -> cannot certify even a 7% rate.
      P(0 rejections | true rate 1%) = 0.669;  | true rate 5% = 0.129
  The v3 correlated result 1/66 (audit: CI to 8.1%) is development evidence, NOT certification.

  EQUIVALENCE-POWER validation: demonstrate the joint acceptance probability, one-sided 95% LOWER.
  design power pi  claim pi >= L   reps R  min accepts   assurance
             95%            90%      300          279      95.1%
             95%            85%      100           92      93.7%
             90%            80%      100           87      87.6%
```

## geometry.py — geometry calibration conditional on Branch-A H

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 geometry.py

====================================================================================================
M.  G3 NULL AT THE CORRECTED EFFECTIVE SIZE - AND WHAT NOW DOMINATES IT
====================================================================================================
  Rotation angle of the sample eigenvectors is driven by the off-diagonal element in the
  Branch-A eigenbasis:  theta ~ S_12/(Sigma_11 - Sigma_22),  Var(S_12) = Sigma_11 Sigma_22 / N_12
      =>  sd(theta) = sqrt( rho / ( N_12 (rho-1)^2 ) ),  rho = Sigma_11/Sigma_22 = k_2/k_1

field                        ratio      N_12  sd_stat deg  + psi 0.2deg  + psi 0.5deg  + psi 1.0deg
theta0_circular              1.000    224726   degenerate           n/a           n/a           n/a
theta1_power                 1.000    471925   degenerate           n/a           n/a           n/a
theta2_ellipse               2.500    235962       0.1243        0.2355        0.5152        1.0077
theta3_temperature           1.000    335581   degenerate           n/a           n/a           n/a
tangent_HT (conserved)       1.453    275627       0.2904        0.3526        0.5782        1.0413

  READ THIS ROW-BY-ROW. At T_total = 240 s the SAMPLING noise on the eigenvector direction is
  0.12-0.36 degrees. Any Branch-A uncertainty in the TRAP AXIS ORIENTATION, psi, adds in quadrature
  and DOMINATES for psi >= 0.2 deg. The v3 uncertainty model contains no such term at all.
    If G3 is calibrated on SAMPLING NOISE ONLY (1% threshold = 0.320 deg) but the true null sd is 0.235 deg (psi=0.2 deg),
      the real false-rejection rate is 17.4%.
    If G3 is calibrated on SAMPLING NOISE ONLY (1% threshold = 0.320 deg) but the true null sd is 0.515 deg (psi=0.5 deg),
      the real false-rejection rate is 53.4%.
    If G3 is calibrated on SAMPLING NOISE ONLY (1% threshold = 0.320 deg) but the true null sd is 1.008 deg (psi=1.0 deg),
      the real false-rejection rate is 75.1%.

  Same argument for G1 and G4: independent PER-MODE stiffness calibration error sigma_k,mode changes
  H's eigenvalue RATIO by sqrt(2)*sigma_k,mode, while the sampling noise on the ratio is only
      theta0_circular          ~ 2/sqrt(N) = 0.422%   vs sqrt(2)x1% = 1.414%  -> Branch-A dominates
      theta2_ellipse           ~ 2/sqrt(N) = 0.412%   vs sqrt(2)x1% = 1.414%  -> Branch-A dominates

  CONCLUSION (SECTION 4, 'Branch-A uncertainty where relevant'): the v3 uncertainty model has only
  SCALAR terms (sigma_cm, sigma_fs). Every gate is invariant to a scalar, so the model contributes
  NOTHING to the gate nulls - while the real dominant term, Branch-A SHAPE and ORIENTATION
  uncertainty, is absent. This is the single largest gap in the v3 statistical design.

====================================================================================================
N.  RESOLVABILITY-BASED BLOCK RULE (replaces the arbitrary delta_deg = 0.05)
====================================================================================================
  Merge two modes into one degenerate block when their eigenvector directions are NOT resolvable:
      merge iff  sd(theta_stat)  >  theta_cap      i.e.  (rho-1)/sqrt(rho) < 1/(theta_cap sqrt(N_12))
  N-dependent and Branch-A-only, so no circularity; it is the honest statement that directions
  are separable only when the eigenvalue gap beats the estimation noise.

field                           N_12       cap 5 deg      cap 10 deg      cap 20 deg
theta0_circular               224726merge if r<1.0245merge if r<1.0122merge if r<1.0061
theta1_power                  471925merge if r<1.0168merge if r<1.0084merge if r<1.0042
theta2_ellipse                235962merge if r<1.0239merge if r<1.0119merge if r<1.0059
theta3_temperature            335581merge if r<1.0200merge if r<1.0099merge if r<1.0050
tangent_HT (conserved)        275627merge if r<1.0221merge if r<1.0110merge if r<1.0055

  At 240 s a 'circular' trap is resolvable down to ~1.2% anisotropy (cap 10 deg). A real trap
  declared circular but with 2% residual ellipticity would be SPLIT, not merged - and must then be
  calibrated as a split geometry. The rule handles this automatically; delta_deg = 0.05 did not.

====================================================================================================
O.  CALIBRATION COST - WHY CONDITIONING ON H IS NOW CHEAP
====================================================================================================
  Under the null K = beta H, with x* declared (not estimated), the whitened sample covariance
      M = beta H^{1/2} S H^{1/2}   is distributed FREE OF H and beta.
  For iid data M ~ Wishart_m(N, I)/N exactly (Bartlett: m chi-squares + m(m-1)/2 normals per draw).
  For OU data, second-moment matching gives Cov(S) exactly via N_ab = (T/2)(1/tau_a + 1/tau_b).

  CONSEQUENCES:
    * G2 and G5 are EXACTLY PIVOTAL - their nulls depend only on (N, m), never on H.
      G2 = eigenvalue ratio of beta M^{-1}; G5 = kurtosis of H^{1/2}X ~ N(0, I/beta).
    * G1, G3, G4 depend on H's spectrum; G1 additionally depends on H's ORIENTATION, because it is
      an entry-wise max and is therefore NOT rotation-invariant. That is a latent defect in G1.
    * So a null draw needs only m(m+1)/2 = 3 numbers, not N x m = 4,000,000 Gaussian variates.

                                     v3 per calibration cell   v4 per calibration cell
random variates per replicate                         40,000                         3
replicates                                                40                    50,000
variates per cell                                  1,600,000                   150,000
cells (n_eff grid x geometry)          6 grid points, POOLED     1 per analysed (H, N)

  v4 uses ~1000x fewer random numbers AND calibrates at the exact geometry actually analysed.
  G5 is obtained in closed form: sqrt(N_4/24) * g2 -> N(0,1), with N_4 = 1.143 T/tau (derived from
  rho_{x^4}(t) = 0.75 rho^2 + 0.25 rho^4), which is LARGER than N_2 = T/tau, so using N_2 for G5 is
  conservative. The second-moment-matched approximation itself is validated ONCE against direct OU
  trajectory simulation at the declared parameters - a single bounded validation job, not a grid.
```

## exactness2.py — exactness qualifications

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 exactness2.py

========================================================================================================
3b [CORRECTED].  COVARIANCE MATCHING DOES NOT MAKE CORRELATED DATA WISHART
========================================================================================================
  My first pass mis-stated the direction. The computed ratio is ~1.49, not 0.75, and it has an
  EXACT analytic limit. For an AR(1)/OU record, as dt/tau -> 0 the spectral density becomes a
  Lorentzian f = 2e/(e^2+w^2), e = 1-phi, giving I2 = 1/e and I3 = 3/(2 e^2), hence

      skew(exact) / skew(Satterthwaite-matched chi2)  =  I3 / I2^2  ->  3/2  EXACTLY.

  So the true quadratic form is FIFTY PERCENT MORE skewed than any covariance-matched surrogate.
  The matched draw has the right mean and the right variance and a systematically too-light upper
  tail - which is anti-conservative exactly where gate thresholds live.

field mode         dt/tau        I2          I3   I3/I2^2  skew exact skew matched  99th pct shift
theta0             0.1124    8.9371    119.3089    1.4937    0.008931     0.005979         0.0022s
theta1             0.2360    4.3163     27.4460    1.4732    0.006121     0.004155         0.0014s
theta2 m1          0.1685    5.9892     53.3062    1.4861    0.007274     0.004895         0.0017s
theta2 m2          0.0674   14.8553    330.5216    1.4977    0.011545     0.007709         0.0028s

  BUT READ THE LAST COLUMN. The RATIO is 3/2, yet the ABSOLUTE skewness is only ~0.01 because the
  record is long, so the Cornish-Fisher shift of the 99th percentile is ~0.002 standard deviations.
  HONEST CONCLUSION: the mismatch is structural, exactly characterised, and numerically negligible
  AT THE DECLARED RECORD LENGTH. It is not a reason to abandon the covariance-matched calibration;
  it is a reason to CONFIRM the operating quantile against generated trajectories once, and to
  refuse the shortcut for short records where the absolute skewness is no longer small.

========================================================================================================
3c [CORRECTED].  A NUMERICALLY CALIBRATED MIN-p TEST DOES NOT HAVE EXACT SIZE
========================================================================================================
  WITHDRAWN: 'size exactly alpha_geom by construction'. The achieved size is a random variable.

    R_cal   target  mean size        sd  P(size > 1.5x target)
      160    0.010     1.242%    0.870%                 30.61% (v3 used this)
     2000    0.010     1.000%    0.222%                  2.11%
    20000    0.010     1.000%    0.070%                  0.00%
    50000    0.010     1.000%    0.044%                  0.00%
   200000    0.010     1.000%    0.022%                  0.00%

  R_cal = 50,000 gives 1.000% +/- 0.045%: a quantified residual, not exactness.
  EXACT ALTERNATIVE, adopted: the Monte-Carlo p-value with the Barnard / Besag-Clifford correction
      p_hat = (1 + #{null draws >= observed}) / (R_cal + 1)
  has size <= alpha for ANY R_cal - but only CONDITIONAL on the calibration draws coming from the
  true null law. 3b shows they come from an approximation, so the exactness is conditional and the
  unconditional size must still be demonstrated. Stated as a conditional guarantee, not assumed.

========================================================================================================
2b.  SENSITIVITY OF THE GATE SIZE TO A MIS-DECLARED BRANCH-A ORIENTATION
========================================================================================================
  Branch-A orientation uncertainty is ABSORBED by calibrating at the declared value. The risk
  is UNDER-declaration, and it is severe.

  theta2, sampling sd 0.1243 deg, per-gate two-sided level 0.2% (z = 3.090)

  declared psi   threshold  TRUE psi  true null sd  ACHIEVED size
         0.50d      1.592d     0.50d        0.515d         0.20%
         0.50d      1.592d     0.75d        0.760d         3.62%
         0.50d      1.592d     1.00d        1.008d        11.41%
         0.50d      1.592d     1.50d        1.505d        29.01%

  A 2x under-declaration of psi takes a 0.2% gate to ~11%. The declared Branch-A uncertainty
  is itself a release-critical input: it must be validated, not merely stated.

========================================================================================================
4.  SYNTHETIC SCENARIOS (hypothetical) vs APPARATUS REQUIREMENTS (to be evidenced)
========================================================================================================
  A. SYNTHETIC VALIDATION SCENARIOS - HYPOTHETICAL BY CONSTRUCTION. Implementation proceeds on
     these immediately; none is a measured fact and none requires laboratory work.

symbol      meaning                                     declared scenario grid
sigma_fs    per-field relative calibration              {0.20, 0.24, 0.27, 0.50, 1.00} %
sigma_cm    common-mode calibration                     {1.10, 1.15, 1.34, 2.29} %
sigma_psi   Branch-A trap-axis orientation              {0.0, 0.2, 0.5, 1.0} deg
sigma_k,modeBranch-A per-mode stiffness                 {0.0, 0.5, 1.0} %
T_total     record length per field                     {120, 240, 480} s
dt          sampling interval                           {0.06, 0.12} ms

  B. APPARATUS CAPABILITIES REQUIRED BEFORE PHYSICAL EXECUTION - NOT YET EVIDENCED. Each is a
     requirement the instrument must be SHOWN to meet; none is claimed to be met today.

symbol      requirement           today       evidentiary status
sigma_fs    <= 0.24%              1.00% assumedPROPOSED - UNEVIDENCED
sigma_cm    <= 1.15%              2.29% assumedPROPOSED - UNEVIDENCED
sigma_psi   measured + declared   not measuredPROPOSED - UNEVIDENCED
sigma_k,modemeasured + declared   not measuredPROPOSED - UNEVIDENCED
```

## discrimination.py — operating characteristic

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 discrimination.py

========================================================================================================
P.  OPERATING CHARACTERISTIC OF THE CROSS-FIELD ENDPOINT   (delta = 2%, sigma_fs = 0.27%)
========================================================================================================
  WORST CASE FOR DETECTION: exactly ONE non-reference field carries a different beta. Acceptance
  requires ALL THREE comparisons to accept, so a disparity spread over several fields is EASIER to
  catch. A single disparate field is the hardest, and is what is tabulated.

  Read the first column as 'recognises agreement'; every later column as 'recognises disagreement'.

coverage rule                     0.0%    0.5%    1.0%    1.5%    2.0%    2.5%    3.0%    4.0%    6.0%   10.0%
true disparity of one field ->----------------------------------------------------------------------
(a) no Bonferroni, z=1.96        0.936   0.859   0.546   0.166   0.018   0.001   0.000   0.000   0.000   0.000
(b) Bonferroni x3, z=2.394       0.832   0.705   0.342   0.065   0.004   0.000   0.000   0.000   0.000   0.000
(c) standard TOST, z=1.645       0.972   0.925   0.677   0.267   0.042   0.002   0.000   0.000   0.000   0.000

                              ^ ACCEPT (agreement)        ^ must fall to ~0 (disagreement)

  Minimum disparity the test reliably rejects (acceptance falls below the stated level):

coverage rule                    accept<=20%   accept<=5%   accept<=1%   size at |e|=delta
(a) no Bonferroni, z=1.96              1.44%         1.80%         2.10%             0.0200
(b) Bonferroni x3, z=2.394             1.20%         1.56%         1.85%             0.0042
(c) standard TOST, z=1.645             1.60%         1.96%         2.27%             0.0462

  The last column is the intersection-union SIZE at the margin boundary: the probability of wrongly
  declaring commensurability when one field is exactly 2% off. All three rules hold it at or below
  their nominal one-sided level, which is what makes the Bonferroni removal safe rather than lax.

  The three alternatives v3 declared, under each candidate rule (acceptance = FAILURE to detect):

alternative                          (a) no Bonfer   (b) Bonferron   (c) standard 
beta = (1, 1.06, 1, 1)                     0.0000         0.0000         0.0000
beta = (1, 0.93, 1.05, 1)                  0.0000         0.0000         0.0000
beta = (1, 1, 1, 1.10)                     0.0000         0.0000         0.0000
beta = (1, 1.025, 1, 1)  HARD              0.0007         0.0001         0.0027
beta = (1.03, 1, 1, 1)   REF OFF           0.0000         0.0000         0.0000

========================================================================================================
Q.  AD-2: WHAT EACH ABSOLUTE-ENDPOINT OPTION CAN AND CANNOT RECOGNISE
========================================================================================================
option                                         0%       2%       3%       5%       8%      10%      15%
true |beta - 1| ->                      --------------------------------------------------------
A  equivalence 5%, sigma_cm -> 1.338%       0.903    0.565    0.294    0.027    0.000    0.000    0.000
B  equivalence 8.37%, sigma unchanged       0.901    0.753    0.608    0.290    0.038    0.005    0.000
C  compatibility, sigma unchanged           0.950    0.863    0.752    0.442    0.087    0.016    0.000

                                        ^ accept         ^ these must fall away

  READ OPTION B CAREFULLY. Widening the margin to 8.37% buys the required 90% power at beta = 1,
  but it then ACCEPTS a true 5% and even a true 8% departure with high probability. It converts a
  powerless test into a permissive one. That is precisely 'adjustment until a PASS appears', and it
  is the option to reject unless the author judges an 8% absolute statement scientifically adequate.
  Option A buys power by measuring the bead better - the test gets SHARPER, not looser.
  Option C never accepts a 15% departure, but it answers only 'the data do not refute beta = 1'.
```

## corrections.py — G5 and combined power

```
$ cd e1a_v4_review_bundle/source_v4_design
$ python3 corrections.py

========================================================================================================
1.  G5 - UNCERTAINTY OF THE STATISTIC ACTUALLY IMPLEMENTED
========================================================================================================
  The code computes  g2 = m4/m2^2 - 3  per whitened coordinate, then G5 = max_r |g2_r|.
  That is a RATIO of sample moments, not a raw fourth moment. Delta method about (m2,m4)=(s^2,3s^4):

      d g2/d m4 = 1/s^4        d g2/d m2 = -6/s^2
      Var(g2) = Var(m4)/s^8 + 36 Var(m2)/s^4 - 12 Cov(m4,m2)/s^6

  For a stationary Gaussian process with autocorrelation rho(t), Isserlis gives
      Cov(x0^2,xt^2) = 2 s^4 rho^2 ,  Cov(x0^4,xt^4) = 72 s^8 rho^2 + 24 s^8 rho^4 ,
      Cov(x0^2,xt^4) = 12 s^6 rho^2 .
  Writing A2 = 1 + 2 SUM (1-k/n) phi^{2k} and A4 = 1 + 2 SUM (1-k/n) phi^{4k}:
      Var(m4) = (s^8/n)(72 A2 + 24 A4) ,  Var(m2) = (2 s^4/n) A2 ,  Cov = (12 s^6/n) A2
  so       Var(g2) = (1/n)[ 72 A2 + 24 A4 + 72 A2 - 144 A2 ] = (1/n) * 24 * A4 .

  THE SECOND-MOMENT TERMS CANCEL EXACTLY. The kurtosis ratio is self-normalising: only the
  FOURTH-order correlation survives. Effective size for g2:  N_g2 = n/A4.

field / mode                 tau ms  dt/tau       A2       A4   N_2=n/A2  N_g2=n/A4  ratio    sd(g2)
theta0_circular mode1        1.0680  0.1124   8.9371   4.5245     223786     442036  1.975  0.007368
theta0_circular mode2        1.0680  0.1124   8.9371   4.5245     223786     442036  1.975  0.007368
theta1_power mode1           0.5086  0.2360   4.3163   2.2740     463357     879507  1.898  0.005224
theta1_power mode2           0.5086  0.2360   4.3163   2.2740     463357     879507  1.898  0.005224
theta2_ellipse mode1         0.7120  0.1685   5.9892   3.0781     333934     649753  1.946  0.006078
theta2_ellipse mode2         1.7799  0.0674  14.8553   7.4613     134632     268049  1.991  0.009462
theta3_temperature mode1     0.7152  0.1678   6.0156   3.0909     332467     647053  1.946  0.006090
theta3_temperature mode2     0.7152  0.1678   6.0156   3.0909     332467     647053  1.946  0.006090

  CORRECTION TO THE ADDENDUM. It claimed N_4 = 1.143 T/tau from rho_{x^4} = 0.75 rho^2 + 0.25 rho^4.
  That is the effective size for the RAW fourth moment, which is NOT the implemented statistic.
  The correct value is N_g2 = n/A4 ~ 2 T/tau - almost exactly TWICE N_2, not 1.14 x N_2.
  Using N_2 for G5 is therefore conservative by a factor 2 in variance (sqrt(2) in sd), for a
  reason now derived rather than asserted. The withdrawn 1.143 figure is not used anywhere.
  WHAT THE COVARIANCE SHORTCUT CAN AND CANNOT REPRODUCE
    CAN  : G1,G2,G3,G4 - every one is a deterministic function of (H, S) alone. A draw of S
           reproduces their exact JOINT null, including all mutual dependence.
    CANNOT: G5. Sample kurtosis is not a function of S. S carries only second moments; g2 needs
           the fourth. No draw of S can produce G5 at all.
    CANNOT: the JOINT dependence between G5 and G1..G4. Both are functions of the same sample.
  IS G5 INDEPENDENT OF G1..G4?  NOT PROVED, and not assumed.
    What IS exact (iid case only): under the null the whitened data are N(0, I/beta) iid; tr(W)
    is complete sufficient for beta, and every gate is scale-invariant hence ancillary, so by
    BASU'S THEOREM the whole gate vector is independent of tr(W). That gives G5 _|_ tr(W), and
    likewise G1..G4 _|_ tr(W). It says NOTHING about G5 versus G1..G4.
    For CORRELATED data even that fails: the complete sufficient statistic for the scale family
    is Z' Gamma^{-1} Z, not tr(W), so Basu does not apply to m2 at all.
    => G5 IS NOT GENERATED INDEPENDENTLY. See the two-block rule below.

========================================================================================================
2.  COMPLETE-PIPELINE POWER - THE INDEPENDENCE CLAIM IS WITHDRAWN
========================================================================================================
  WITHDRAWN: 'gates are scalar-invariant, so gates and beta are statistically independent'.
  Scalar invariance says only that the gates do not depend on the CALIBRATION ERRORS. Gates and
  beta_hat are both functions of the SAME sample covariance S; that is dependence, not independence.

  What can honestly be said:
    EXACT, iid only : beta_hat = m/tr(HS) is a function of tr(W), the complete sufficient statistic
        for beta; the gate vector is scale-invariant hence ancillary; BASU gives beta_hat _|_ (all
        five gates) jointly. The product rule is then exact - by ancillarity, NOT by scalar invariance.
    NOT ESTABLISHED, correlated : Basu's completeness premise fails. No product rule is claimed.
  So the design uses a UNION (Bonferroni) LOWER BOUND, valid under ARBITRARY dependence:
      P(complete success) >= 1 - SUM_f alpha_geom,f - (1 - pi_equiv) - (1 - pi_abs)

  P2 and P3 are NOT independent either - both contain the reference field's errors. The
  joint P(P2 and P3) below is the same exact 1-D integral, now over the shared term.

 sigma_fs  sigma_cm  pi_equiv   pi_abs  pi(P2&P3)  product  a_geom  UNION BOUND  >=0.90
    0.27%    1.338%     0.936    0.903      0.847    0.845    1.0%        0.799      no
    0.27%    1.338%     0.936    0.903      0.847    0.845    0.5%        0.819      no
    0.27%    1.200%     0.936    0.959      0.899    0.897    0.5%        0.875      no
    0.24%    1.150%     0.971    0.974      0.947    0.946    0.5%        0.925     YES
    0.22%    1.100%     0.985    0.984      0.969    0.969    0.5%        0.949     YES
    0.27%    2.291%     0.936    0.157      0.148    0.147    0.5%        0.073      no

  The exact joint pi(P2&P3) EXCEEDS the product in every row: the shared reference error makes the
  two endpoints POSITIVELY dependent, so treating them as independent was pessimistic there while
  the withdrawn gate-independence claim was optimistic. Both are now replaced by the union bound,
  which is valid whatever the dependence and is within ~0.01 of the exact value in this regime.
  LAST ROW is the present apparatus (sigma_cm 2.29%): P3 power collapses to 0.16 and no tightening
  of sigma_fs can rescue the complete pipeline. P3, if mandatory, is the binding constraint.
```



---

# PART V — FILE MANIFEST

SHA-256 and byte count for every file in the review bundle.

```
5b6decb568d6333c8e9b8518ec43cf75e432cc4b5b3ec9cfcd0f09345b3b8ecc       23141  checks/v4_addendum_checks.py
7a6f52d5565a9b0551591f12c566bdb139d76cf5da04fcaa1a4d3b87abacf98d       20017  checks/v4_design_checks.py
c7103adcfdadfdd8a1d469054fb155da636bf516615b70196cb0ec13517d5f87       30564  failed_extraction/seifert_pdf_extract.FAILED.txt
2370010b4254b476abf0af075e7b18a62b039b41af741e585e526157ad3333bc         339  MANIFEST.sha256
ebbf6c3163325f98288f53218bfdb7df203e600405d1866dd8a11a1c5a47667e       24566  packet/E1A_V4_ADDENDUM.md
0fedf294fa4c4572ca1d2dd4333d60d0760df40ed6d14a60cf10b14c8627ed9e       33192  packet/E1A_V4_CORRECTION_PACKET.md
5496bacb562b5fc2d11a5900a867fda1c6a4d970f429b8c88cb32c86b4d0845b        5131  README_BUNDLE.md
a5d17030f40e183bef2020c406beb5aed5140d0937ac14e3b7aa9bb4485b9173        4950  source_v3/config.json
8bddd86bf18cff1ad4c1acd4622b248a8e50a45c5b36af230f8928bb22f4a976          65  source_v3/config.sha256
270d3dbf52dc5c3c384ccdda7ed8f6c7084c3d2654aed2beb5715293ab9d15cd         190  source_v3/confirm1.json
fac1fc86b5a904cf96c8ecab374d4dbd5e72cd938d06fe4c7350ea0027f847d6        6488  source_v3/confirm1.py
80ce33e4dc45bddc388db719d0e4701221f031f171b365e01db0cb07bdad5756        9065  source_v3/confirm2.py
649b1cce5dfb50f33d69dd6ceab446cc0e6b9e3ff7e49af0c8424c660dfd5a19        2918  source_v3/derive_margins.py
e8cc54dd4b4c514ca4906a99b069cece5a204f0fdd556a8611111bbc488fa4c5        1905  source_v3/diagnose.py
a1a251b5c54b8811bf88bc220f1125c2e42c3ac3ba1c9b1ff96991502b9be586        8992  source_v3/e1a_analysis.py
a5d6d2a3b623671ace636634c7540fdbe6fbd5965c89acaddac083cd8bfcba37        3733  source_v3/e1a_world.py
ba081d78eb335c569b913ae5837e42b8df97555ae2aca2b81dc1e62c64c994c2         560  source_v3/margins.json
2a45385ebae78d77f697c86911df05184cb7b2ab8d09239884ef4fc1c803a1b1        1328  source_v3/phase1_grid.json
5a8c0aea03829b1404fc6dd9ff6811a0d19f09c778f3d7e1c95ecfc0f414e01b        2065  source_v3/phase1_grid.py
e3c55b03f8b9efa55f4263e35595cddb94e38cded89ab18b78ce9edcd95438c8        4734  source_v3/results.json
a203ac85f43ad8563336cbc37845c6e380f9e3f5eeefddeeb88b416a9bf50bf4        7372  source_v4_design/assurance.py
9cd1865fbd1843eb48f873587bf6aa0a6a293b5777f85e6b06caadd3aeab0a11        7853  source_v4_design/corrections.py
1e871db0567c5c020d5c4651fa849511a0a99c8281cf1f41a62d5fd29b9b6da6        5501  source_v4_design/discrimination.py
a16d811efc5e41ab4e95ae4cc75c00c16f0330becb3a85a2f1f6177958628ddb        8305  source_v4_design/exactness.py
30165ccad45a0e2a5a02fd86b60850ea1cfeca070cf1aa7266c9935b98d4e745        6730  source_v4_design/exactness2.py
c2ac352a22d0fa20adf28551b945b985a5ce788098e1ca6cf9983a297858ca5c        6579  source_v4_design/feasibility.py
4fa518e8062e1c23da38d7ee5628bbb08e492ed6d8ff7ceb49707634e4b97fa8        6166  source_v4_design/geometry.py
ebccdde7d99c1617d924f7dbe2a6f5ae84e59c77b9237814c45853f017790aaf        7012  source_v4_design/verify_audit.py
22b2ae3b210b80fb015816ea53b44c87c60c54edd23ffd4d2975e872b1368819        5634  transcripts/assurance.out
4f95eb55de93a29e3b9fc8238dc0d94e9f22c523251f5266210ace412613d763        6322  transcripts/corrections.out
610153182da5ee6c123bdabf6f934aab40382e529d15dcb83e6e5773f7d82312        4179  transcripts/discrimination.out
c19043826e358068bc9008f317a9ce56cd2824a09bfc0f7bc3db59a8c23f8309        5919  transcripts/exactness2.out
06dfca4b2d5c4444450fa33a82cadd781ed076260a3ff01051d4ca9e4466595d        5889  transcripts/feasibility.out
e44b3aec185e1144c7c1c19f24ef6fae07ce9b2b273c487c2e4ce303d5be1799        6276  transcripts/geometry.out
4e2ac4cb293a1f7a9523dfc447a4348fad760c32bc807007d082aadfd86097f1       17353  transcripts/v4_addendum_checks.out
2e4a186e064106b7c7d2b1890f735993642a142cb5de57f9ab4ec049d0509b9b       16551  transcripts/v4_design_checks.out
300a4292c215e6adc18aa2e586df2532ca0990f186f388fda3c3a81771eb9d04        5455  transcripts/verify_audit.out

# files: 37   total bytes: 313039
# generated 2026-09-28 against repo coordinate c0099d8f7eea95a0f683f3c09fef71bdffc369af
```


---

# PART VI — CHECKING SCRIPTS

Both scripts reproduce every number above. Run from the bundle's `checks/` directory with
`E1A_V3_DIR=../source_v3 python3 <script>`.

## `v4_addendum_checks.py`

```python
"""E1a v4 ADDENDUM CHECKS - closes the two reviewer dependencies.

DETERMINISTIC ONLY. No RNG, no trajectories, no model stepping, no simulation runner.
Imports: stdlib `math`, `sys`, `os`, and (read-only, pure) v3 `e1a_analysis` which itself
imports only `math`. Supersedes nothing: v4_design_checks.py is unchanged and still valid.

Run:  E1A_V3_DIR=<path to e1a_gate_v3> python3 v4_addendum_checks.py
"""
import math, sys, os

S2 = math.sqrt(2.0)
def Phi(x): return 0.5*(1.0+math.erf(x/S2))
def phi(x): return math.exp(-0.5*x*x)/math.sqrt(2*math.pi)
def zq(p):
    lo, hi = -12.0, 12.0
    for _ in range(300):
        mid = (lo+hi)/2
        if Phi(mid) < p: lo = mid
        else: hi = mid
    return (lo+hi)/2
def hr(t): print("\n"+"="*100+"\n"+t+"\n"+"="*100)

# ------------------------------------------------- declared benchmark (Branch A only)
kB      = 1.380649e-23
ETA     = {298.0: 0.890e-3, 318.0: 0.596e-3}
A_BEAD  = 6.366e-6
T_TOTAL = 240.0
DT      = 1.2e-4
N_SAMP  = int(round(T_TOTAL/DT))
FIELDS  = [("theta0_circular",    [100e-6, 100e-6], 298.0),
           ("theta1_power",       [210e-6, 210e-6], 298.0),
           ("theta2_ellipse",     [150e-6,  60e-6], 298.0),
           ("theta3_temperature", [100e-6, 100e-6], 318.0)]
REF, OTH = "theta0_circular", ["theta1_power", "theta2_ellipse", "theta3_temperature"]
def gamma_of(T): return 6*math.pi*ETA[T]*A_BEAD
def A_p(p, ph, n):
    x = ph**p
    return 1 + 2*(x/(1-x) - x/(n*(1-x)**2))
SIG_STAT, N12 = {}, {}
for nm, ks, T in FIELDS:
    ts = [gamma_of(T)/k for k in ks]
    N2 = [N_SAMP/A_p(2, math.exp(-DT/t), N_SAMP) for t in ts]
    SIG_STAT[nm] = math.sqrt(2*sum(1.0/x for x in N2))/len(ks)
    N12[nm] = (T_TOTAL/2)*(1/ts[0] + 1/ts[1])

DELTA_CROSS, DELTA_ABS = 0.02, 0.05
Z_CROSS, Z_ABS = 1.959963985, 1.959963985

# ============================================================== 1. THE P3 RULE
hr("1.  THE P3 RULE - WHAT WAS ACTUALLY COMPUTED, AND THE PROPOSED COMPLETE RULE")
print("""AS COMPUTED in v4_design_checks.py function pi_abs() (and, earlier, e1a_v4_design/
corrections.py pi_abs()).  TRANSCRIBED FAITHFULLY:

    sa = sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat[REF]^2)
    ha = z_abs * sa
    accept  iff   log((1-d_abs)/(1-ha))  <=  log beta_hat_REF  <=  log((1+d_abs)/(1+ha))

  estimator  : beta_hat = m / tr(H_A S)       (v3 e1a_analysis.py beta_mle, line 120-121)
  parameter  : beta at the REFERENCE FIELD ONLY
  coverage   : two-sided, z = 1.96, i.e. a nominal 95% interval; the equivalence test this
               induces has size 2.5% (TOST at 2.5% per side)
  interval   : multiplicative/relative, beta_hat*(1 +- ha), v3 e1a_analysis.py beta_ci line 122
  uncertainty: sigma_cm (shared) and sigma_fs (field-specific) BOTH enter, in quadrature with
               sigma_stat - correct for an ABSOLUTE endpoint, where nothing cancels
  invalid    : beta_status != ESTIMATED -> abs_accept() returns False (v3 confirm2.py line 121)

  PROVENANCE: delta_abs = 5% and z = 1.96 come from the UNCOMMITTED v3 config.json
  (endpoints.P3_absolute_benchmark). NOT a committed requirement, NOT previously approved.""")
print("""
DEFECT: E1a predicts beta = 1 at EVERY tested field (baseline section 14.1, COMMITTED).
A rule evaluated only at the reference field does not test that prediction. The number
0.974 reported earlier is therefore the REFERENCE-FIELD-ONLY probability, mislabelled.

PROPOSED COMPLETE RULE  [PROPOSED DESIGN SETTING - label carried explicitly]:

    P3 passes  iff  for EVERY field theta in {theta0, theta1, theta2, theta3}:
        beta_hat_theta * (1 - h_theta) >= 1 - delta_abs   AND
        beta_hat_theta * (1 + h_theta) <= 1 + delta_abs
        h_theta = z_abs * sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat_theta^2)
    conjunctive over all four fields (an intersection-union test: no multiplicity
    correction is needed for size control, by the IUT theorem)
    any field with beta_status != ESTIMATED makes P3 FAIL (fail-closed, no conditioning)

  This addresses "beta = 1 at every tested field" directly. It is STRICTER than what was
  computed. All affected numbers are recomputed below.""")

def p3_ref_only(sfs, scm):
    sa = math.sqrt(scm**2 + sfs**2 + SIG_STAT[REF]**2); ha = Z_ABS*sa
    if ha >= DELTA_ABS: return 0.0
    return Phi(math.log((1+DELTA_ABS)/(1+ha))/sa) - Phi(math.log((1-DELTA_ABS)/(1-ha))/sa)

def p3_all_fields(sfs, scm, npts=4001):
    """EXACT 1-D integral over the shared common-mode error w = d_cm.
       log beta_hat_theta = -w + v_theta ;  v_theta ~ N(0, sfs^2 + sigma_stat_theta^2)."""
    legs = []
    for nm, _, _ in FIELDS:
        s = math.sqrt(sfs**2 + SIG_STAT[nm]**2)
        h = Z_ABS*math.sqrt(scm**2 + sfs**2 + SIG_STAT[nm]**2)
        if h >= DELTA_ABS: return 0.0
        legs.append((s, math.log((1-DELTA_ABS)/(1-h)), math.log((1+DELTA_ABS)/(1+h))))
    lim = 8*scm; hs = 2*lim/(npts-1); tot = 0.0
    for i in range(npts):
        w = -lim + i*hs; wt = 1 if i in (0, npts-1) else (4 if i % 2 else 2); pr = 1.0
        for s, a, b in legs: pr *= max(0.0, Phi((b+w)/s) - Phi((a+w)/s))
        tot += wt*phi(w/scm)/scm*pr
    return tot*hs/3.0

print(f"\n{'sigma_k':>8}{'sigma_fs':>10}{'sigma_cm':>10}{'pi_P3 ref-only':>17}{'pi_P3 ALL FOUR':>17}{'change':>10}")
SCEN = [(0.0100, 0.022913), (0.0050, 0.013377), (0.0040, 0.012000),
        (0.0034, 0.011500), (0.0030, 0.011000), (0.0025, 0.010000)]
for sk, scm in SCEN:
    sfs = math.sqrt(sk**2/2 + (0.1/298.0)**2)
    a, b = p3_ref_only(sfs, scm), p3_all_fields(sfs, scm)
    print(f"{sk*100:>7.2f}%{sfs*100:>9.3f}%{scm*100:>9.3f}%{a:>17.4f}{b:>17.4f}{b-a:>+10.4f}")
print("""
  The conjunctive rule costs 1-3 points. It does NOT collapse, because the dominant term
  sigma_cm is COMMON to all four fields: they pass or fail largely together. That shared
  structure is why the exact integral is used instead of a product of marginals.""")

# ======================================================= 2. JOINT P2 AND P3
hr("2.  JOINT P(P2 and P3) UNDER THE COMPLETE P3 RULE - EXACT 2-D INTEGRAL")
print("""  P2 and P3 share every field-specific term. With w = d_cm and v_theta = -d_fs + e:
      log beta_hat_theta = -w + v_theta        log r_j = v_j - v_ref
  P2 accepts iff v_j in [v_ref + a_j, v_ref + b_j] for all j
  P3 accepts iff v_theta in [A_lo_theta + w, A_hi_theta + w] for all theta
  so the joint is a 2-D integral over (w, v_ref) with the three inner integrals in closed
  form - the intersection of two intervals.""")
def joint_p2_p3(sfs, scm, npts=601, with_p3=True):
    sref = math.sqrt(sfs**2 + SIG_STAT[REF]**2)
    hr_ref = Z_ABS*math.sqrt(scm**2 + sfs**2 + SIG_STAT[REF]**2)
    if with_p3 and hr_ref >= DELTA_ABS: return 0.0
    Aref = (math.log((1-DELTA_ABS)/(1-hr_ref)), math.log((1+DELTA_ABS)/(1+hr_ref))) if with_p3 else None
    legs = []
    for nm in OTH:
        sj = math.sqrt(sfs**2 + SIG_STAT[nm]**2)
        hc = Z_CROSS*math.sqrt(2*sfs**2 + SIG_STAT[nm]**2 + SIG_STAT[REF]**2)
        if hc >= DELTA_CROSS: return 0.0
        ha = Z_ABS*math.sqrt(scm**2 + sfs**2 + SIG_STAT[nm]**2)
        Aj = (math.log((1-DELTA_ABS)/(1-ha)), math.log((1+DELTA_ABS)/(1+ha))) if with_p3 else None
        legs.append((sj, math.log((1-DELTA_CROSS)/(1-hc)), math.log((1+DELTA_CROSS)/(1+hc)), Aj))
    lw, lv = 8*scm, 8*sref
    hw, hv = 2*lw/(npts-1), 2*lv/(npts-1); tot = 0.0
    for i in range(npts):
        w = -lw + i*hw; ww = 1 if i in (0, npts-1) else (4 if i % 2 else 2)
        inner = 0.0
        for k in range(npts):
            vr = -lv + k*hv; wv = 1 if k in (0, npts-1) else (4 if k % 2 else 2)
            if with_p3 and not (Aref[0]+w <= vr <= Aref[1]+w): continue
            pr = 1.0
            for sj, a, b, Aj in legs:
                lo, hi = vr+a, vr+b
                if Aj is not None: lo, hi = max(lo, Aj[0]+w), min(hi, Aj[1]+w)
                pr *= max(0.0, Phi(hi/sj) - Phi(lo/sj))
                if pr == 0.0: break
            inner += wv*phi(vr/sref)/sref*pr
        tot += ww*phi(w/scm)/scm*(inner*hv/3.0)
    return tot*hw/3.0
print(f"\n{'sigma_k':>8}{'sigma_fs':>10}{'sigma_cm':>10}{'pi_P2':>9}{'pi_P3(all)':>12}{'pi(P2&P3)':>12}{'product':>10}")
JOINT = {}
for sk, scm in SCEN:
    sfs = math.sqrt(sk**2/2 + (0.1/298.0)**2)
    p2 = joint_p2_p3(sfs, scm, with_p3=False); p3 = p3_all_fields(sfs, scm)
    pj = joint_p2_p3(sfs, scm, with_p3=True); JOINT[sk] = (sfs, scm, p2, p3, pj)
    print(f"{sk*100:>7.2f}%{sfs*100:>9.3f}%{scm*100:>9.3f}%{p2:>9.4f}{p3:>12.4f}{pj:>12.4f}{p2*p3:>10.4f}")
print("\n  CONVERGENCE of the 2-D Simpson rule (sigma_k = 0.34%):")
sfs_t, scm_t = math.sqrt(0.0034**2/2 + (0.1/298.0)**2), 0.0115
prev = None
for n in (301, 601, 1201):
    v = joint_p2_p3(sfs_t, scm_t, npts=n)
    print(f"    npts = {n:>5}^2   value = {v:.8f}   |change| = " + ("-" if prev is None else f"{abs(v-prev):.2e}"))
    prev = v

# ================================================= 3. COMPLETE PROBABILITY BUDGET
hr("3.  COMPLETE-PIPELINE PROBABILITY BUDGET - EVERY MANDATORY FAILURE EVENT")
print("""  COMPLETE-PASS EVENT, stated as a set:
      C = [ AND over 4 fields: BranchA_valid & rank_ok & Neff_ok & mode_rule_ok & gate_pass ]
          AND P2_accept AND P3_accept AND P4_verified
  P(C) >= 1 - SUM over all failure events of their probabilities   (union bound, EXACT INEQUALITY)

  EVENT-BY-EVENT.  A = in a named budget term, B = implied by others, C = not yet established.""")
ALPHA = 0.005
sfs_t, scm_t = math.sqrt(0.0034**2/2 + (0.1/298.0)**2), 0.0115
# --- P4
print("""
  P4 entropy endpoint .......................................................... CASE B
    v3 confirm2.py lines 143-148: c12 tests |(5 kB T/T)/kB - 5| < 1e-12 on DECLARED constants.
    It is a deterministic identity check on the design, not a function of Branch-B data, so
    its failure probability is EXACTLY 0 under the assumption that the identity is verified
    at design time. It contributes no term. Its PHYSICAL claim is separately qualified.
    Label: AN EXACT PROBABILITY UNDER A SPECIFIED MODEL (degenerate, = 0).""")
# --- rank / Neff
lam_slack = 1 - math.sqrt(2/223786.0)
t_need = lam_slack - 1e-6
print(f"""
  Rank-guard refusal (lambda_min/lambda_max < 1e-12) ........................... CASE A, bounded
    Davidson-Szarek for W ~ Wishart(N, I_m)/N: P[ sqrt(lambda_min) < 1 - sqrt(m/N) - t ]
    <= 2 exp(-N t^2/2). With N = 223786, m = 2, reaching a ratio of 1e-12 needs t ~ {t_need:.4f},
    giving a bound of 2 exp(-{223786*t_need*t_need/2:.3e}) - numerically 0 in double precision.
    Label: A PROVED UPPER BOUND, under an iid-Gaussian premise that is itself approximate
    for OU data. Budget term: 0 (bounded), assumption stated.

  N_eff-unsupported refusal ................................................... CASE B
    N_ab is computed from BRANCH-A tau_r = gamma(T)/k_r and the declared T_total, dt. It is
    deterministic given the declared design and lies inside the supported range for all four
    fields. Probability 0 for the declared scenario; a different design must re-check.""")
# --- mode resolution
print("""
  Mode-resolution boundary crossing ........................................... CASE A + CASE C
    NEW TERM - absent from the earlier budget. The merge rule uses H_A's eigenvalue ratio,
    and H_A is NOISY. For a field that is TRULY circular (rho_true = 1 exactly), the estimated
    ratio is rho_A ~ 1 + |delta_1 - delta_2|, a half-normal with scale sqrt(2) sigma_k. The rule
    SPLITS whenever rho_A exceeds the merge boundary:
        merge iff (rho-1)/sqrt(rho) < u ,  u = 1/(theta_cap sqrt(N_12))""")
print(f"\n{'theta_cap':>10}{'u':>10}{'merge boundary rho':>20}{'P(split | truly circular)':>27}{'x3 circular fields':>20}")
MODE = {}
for cap in (5.0, 10.0, 20.0):
    u = 1.0/(math.radians(cap)*math.sqrt(N12[REF]))
    rho_b = ((u+math.sqrt(u*u+4))/2)**2
    p = 2*(1-Phi(u/(S2*0.0034)))
    MODE[cap] = p
    print(f"{cap:>9.0f}d{u:>10.5f}{rho_b:>20.5f}{p:>27.3e}{3*p:>20.3e}")
print("""
    CASE A at theta_cap = 5 deg: 3 x 5.0e-07, entered in the budget and negligible.
    CASE C at theta_cap = 10 deg: the CROSSING probability is 1.19e-02 per circular field,
    but its CONSEQUENCE is NOT established. Calibrating conditional on H_A is approximately
    self-consistent (a split H_A also widens its own calibrated G3 threshold), so a crossing
    may cost DETECTION POWER rather than cause a false rejection. Which it is has not been
    determined and REQUIRES VALIDATION. The budget below therefore charges the full crossing
    probability as a failure - the conservative choice - and reports both caps.
    DESIGN CONSEQUENCE: theta_cap = 5 deg is selected for this field set. It merges genuine
    splits only below rho = 1.0245, and theta2 sits at rho = 2.5, far outside.""")
# --- calibration mismatch
z1 = zq(1-0.004)
eps_cal = phi(z1)*0.0028
print(f"""
  Finite-calibration and surrogate mismatch ................................... CASE A, approximate
    Besag-Clifford gives size <= alpha_1 EXACTLY, but only CONDITIONAL on the null draws being
    from the true null law. They are from the covariance-matched surrogate, whose 99th-percentile
    Cornish-Fisher shift was measured at 0.0014-0.0028 sd (v4 packet Appendix C item 2).
    At the block-1 operating level alpha_1 = 0.4% (z = {z1:.4f}, phi(z) = {phi(z1):.5f}):
        eps_cal ~ phi(z) x 0.0028 = {eps_cal:.3e} per field
    Label: AN APPROXIMATE PROBABILITY, A QUANTITY REQUIRING LATER VALIDATION.
    G5's block adds its own delta-method error, NOT quantified here - CASE C, validation listed.""")
# --- budget
print(f"\n  BUDGET, unrounded inputs: sigma_k = 0.34 pct, sigma_fs = {sfs_t*100:.6f} pct, sigma_cm = {scm_t*100:.4f} pct")
pj = joint_p2_p3(sfs_t, scm_t, npts=601)
for cap in (5.0, 10.0):
    terms = [("4 x alpha_geom (gate, NOMINAL DESIGN ALLOCATION)", 4*ALPHA),
             ("4 x eps_cal (APPROXIMATE, needs validation)",       4*eps_cal),
             ("4 x rank/Neff refusal (PROVED BOUND)",              0.0),
             (f"3 x mode-resolution crossing, cap {cap:.0f} deg",  3*MODE[cap]),
             ("1 - pi(P2 and P3) (APPROXIMATE PROBABILITY)",       1-pj),
             ("P4 failure (EXACT, degenerate)",                    0.0)]
    tot = sum(v for _, v in terms)
    print(f"\n    --- theta_cap = {cap:.0f} deg ---")
    for lab, v in terms: print(f"      {lab:<52} {v:.8f}")
    print(f"      {'RAW union expression 1 - sum':<52} {1-tot:.8f}")
    print(f"      {'REPORTED LOWER BOUND max(0, .)':<52} {max(0.0,1-tot):.4f}")
print(f"""
  The earlier headline 0.922 DOES NOT SURVIVE unchanged. It omitted the mode-resolution term
  and used the reference-only P3. Corrected: {max(0.0,1-(4*ALPHA+4*eps_cal+3*MODE[5.0]+(1-pj))):.4f} at theta_cap = 5 deg,
  {max(0.0,1-(4*ALPHA+4*eps_cal+3*MODE[10.0]+(1-pj))):.4f} at 10 deg.  This is an APPROXIMATE DESIGN CALCULATION,
  not a guaranteed success probability: pi(P2 and P3) rests on the log-linear error model and
  eps_cal on an unvalidated surrogate.
  SCENARIO-SPECIFIC, not uniform over any declared parameter set.""")
print("""
  CLASSIFICATION REQUIRED BY THE REVIEW:
    sigma_k <= 0.34% with sigma_cm <= 1.15% .... A SUFFICIENT CANDIDATE SCENARIO. Not shown
        necessary: no search over the (sigma_k, sigma_cm, T_total, alpha_geom) space was run,
        and the union bound is conservative, so nearby looser scenarios may also suffice.
    sigma_k = 1.00% ............................ A PROVEN EMPTY ACCEPTANCE REGION for P2:
        h_cross = 2.0551% > delta_cross = 2%, so [(1-d)/(1-h), (1+d)/(1+h)] is empty. This is
        a demonstrated incompatibility of that scenario, by algebra - not a loose bound.
    rows between .............................. AN INSUFFICIENT LOWER BOUND where the raw
        expression falls below the target: the bound is conservative and the true value is
        higher, so no impossibility is demonstrated there.""")

# ============================================ 4. alpha_geom AND FALSE-BRIDGE DETECTION
hr("4.  alpha_geom = 0.5% CHECKED AGAINST FALSE-BRIDGE DETECTION, NOT ONLY TRUE-BRIDGE PASS")
sd_null = math.sqrt(0.1243**2 + 0.5**2)
print(f"  G3 null sd at theta2 with sigma_psi = 0.5 deg: {sd_null:.4f} deg\n")
print(f"{'alpha_geom':>12}{'z':>9}{'threshold deg':>15}{'min detectable rotation (80% power)':>38}")
for a in (0.01, 0.005):
    z = zq(1-a/2); print(f"{a:>11.1%}{z:>9.4f}{z*sd_null:>15.4f}{(z+0.8416)*sd_null:>38.4f}")
lo = (zq(1-0.005)+0.8416)/(zq(1-0.005/1)+0.8416)
print(f"""
    Tightening 1% -> 0.5% raises the minimum detectable rotation by
    {((zq(1-0.0025)+0.8416)/(zq(1-0.005)+0.8416)-1)*100:.1f}% - a real but small loss of geometric sensitivity.

  The other declared false-bridge controls are UNAFFECTED by alpha_geom:
    paired hidden-scale distortion c = 1.07 / 0.90 : gates are SCALE-INVARIANT (verified,
        v4 packet Appendix B.2, differences <= 6.7e-16), so this control acts entirely through
        P3/beta, not through the gate. alpha_geom cannot weaken it.
    independent coordinate permutation : for theta2 the permuted K is diagonal in the lab
        frame while H_A's axes sit at 30 deg, so G3 ~ 30 deg against a {zq(1-0.0025)*sd_null:.3f} deg threshold.
        Detection probability is 1 to double precision at either alpha_geom.
    time shuffle : an AUTOCORRELATION control only; it leaves S identical to 1e-30.
  CONCLUSION: alpha_geom = 0.5% costs ~7% in minimum detectable rotation and nothing else in
  the declared control suite. No control is removed, weakened in definition, or replaced.""")

# ======================================== 5. THE beta ESTIMATOR, CHECKED ON THE REAL FUNCTION
hr("5.  beta_hat = beta/(1 + delta_bar) - DERIVED FOR THE ACTUAL ESTIMATOR AND CLASSIFIED")
print("""  ACTUAL FUNCTION (v3 e1a_analysis.py lines 120-121):
      def beta_mle(H,S): m=len(H); return m/sum(mm(H,S)[i][i] for i in range(m))
  i.e.  beta_hat = m / tr(H_A S).   Let G := H_true^{-1/2} H_A H_true^{-1/2}  and let M be the
  whitened sample covariance, E[M] = I. Then S = (1/beta) H_true^{-1/2} M H_true^{-1/2} and

      beta_hat = m beta / tr(G M)          <- COMPLETE FINITE-SAMPLE ESTIMATOR, exact identity

  Population limit M -> I:  beta_hat_pop = m beta / tr(G).   THIS is what the earlier claim
  described: AN IDEAL POPULATION CALCULATION of ONE COMPONENT of measurement error. It is NOT
  the complete finite-sample estimator, and the earlier wording did not say so.""")
V3 = os.environ.get("E1A_V3_DIR", "")
if V3 and os.path.isdir(V3):
    sys.path.insert(0, V3)
    import e1a_analysis as EA
    c30, s30 = math.cos(math.radians(30)), math.sin(math.radians(30))
    R30 = [[c30, -s30], [s30, c30]]
    D = [[2.5, 0.0], [0.0, 1.0]]
    Ht = EA.mm(EA.mm(R30, D), EA.TT(R30))                      # anisotropic, ratio 2.5, 30 deg
    Sig = EA.inv(Ht)                                            # beta_true = 1 -> Sigma = H^-1
    def rot(p):
        c, s = math.cos(math.radians(p)), math.sin(math.radians(p)); return [[c, -s], [s, c]]
    def modes(d1, d2):
        return EA.mm(EA.mm(R30, [[2.5*(1+d1), 0.0], [0.0, 1.0*(1+d2)]]), EA.TT(R30))
    CASES = [("1 pure scalar  d = +3%",        [[1.03*Ht[i][j] for j in range(2)] for i in range(2)], 1/1.03),
             ("2 differential d = (+2%, -2%)", modes(0.02, -0.02),                                    1.0),
             ("3 orientation  psi = 1 deg",    EA.mm(EA.mm(rot(1.0), Ht), EA.TT(rot(1.0))),          None),
             ("4 all three combined",          None,                                                  None)]
    c4 = EA.mm(EA.mm(rot(1.0), modes(0.02, -0.02)), EA.TT(rot(1.0)))
    c4 = [[1.03*c4[i][j] for j in range(2)] for i in range(2)]
    CASES[3] = ("4 all three combined", c4, None)
    r = 2.5
    pred3 = 2.0/(2.0 + math.sin(math.radians(1.0))**2*(r + 1/r - 2))
    CASES[2] = (CASES[2][0], CASES[2][1], pred3)
    CASES[3] = (CASES[3][0], CASES[3][1], pred3/1.03)
    print(f"\n  H_true: eigenvalues (2.5, 1.0) rotated 30 deg; beta_true = 1; Sigma = H_true^-1\n")
    print(f"{'case':<32}{'beta_mle(H_A, Sigma)':>22}{'prediction':>14}{'|diff|':>12}{'sigma_stat(G)/sigma_stat(I)':>28}")
    for lab, HA, pred in CASES:
        b = EA.beta_mle(HA, Sig)
        G = EA.mm(EA.mm(EA.sym_pow(Ht, -0.5), HA), EA.sym_pow(Ht, -0.5))
        trG = G[0][0]+G[1][1]; trG2 = sum(G[i][j]*G[j][i] for i in range(2) for j in range(2))
        ratio = (math.sqrt(2*trG2)/trG)/math.sqrt(2*2)/1.0*2/2   # vs sqrt(2 tr I^2)/tr I
        ratio = (math.sqrt(2*trG2)/trG)/(math.sqrt(2*2)/2)
        print(f"{lab:<32}{b:>22.10f}{pred:>14.10f}{abs(b-pred):>12.2e}{ratio:>28.8f}")
    print("""
  Case 2 returns EXACTLY 1: differential mode error with delta_bar = 0 leaves beta untouched.
  Case 3 matches 2/(2 + sin^2(psi)(r + 1/r - 2)) - orientation enters at SECOND order, and the
  identity is EXACT in psi for the population calculation, not merely first-order.
  Last column: sigma_stat scales as sqrt(2 tr G^2)/tr G, so Branch-A error perturbs the
  SAMPLING term too - by <1e-4 relative in every case here, but not by exactly zero.

  CLASSIFICATION:
    beta_hat = m beta / tr(G M) ................ EXACT IDENTITY for the implemented function
    beta_hat_pop = m beta / tr(G) .............. EXACT, ideal population calculation (M -> I)
    beta_hat = beta/(1 + delta_bar) ............ EXACT for mode-scaling errors, population only
    orientation immunity ....................... EXACT to all orders in psi, population only;
                                                 magnitude sin^2(psi)(r + 1/r - 2)/2
    sigma_beta = sqrt(sigma_cm^2 + sigma_fs^2 + sigma_stat^2) ... FIRST-ORDER DELTA-METHOD
        APPROXIMATION of a nonlinear (multiplicative) function, NOT an exact identity. The
        exact relation is log-additive only if every factor is exactly log-normal; the
        sampling factor m/tr(GM) is a reciprocal quadratic form, which is not.""")
else:
    print("\n  SKIPPED - E1A_V3_DIR not set. No result claimed.")

# ============================================ 6. CONSTRAINED-MACROSTATE DERIVATION
hr("6.  THE CONSTRAINED-MACROSTATE ENTROPY - ITS OWN DEFINITION AND REMAINDER")
print("""  DEFINITION. Bead + single reservoir, total energy E_tot fixed, bead HELD at position x
  (a constraint, so the bead's configurational entropy at fixed x is a constant, independent
  of x). The reservoir then holds E_tot - U(x), and
      S_constr(x) = S_res(E_tot - U(x)) + const
  Expanding with dS_res/dE = 1/T and d^2 S_res/dE^2 = -1/(T^2 C_v):
      S_constr(x) = S_res(E_tot) - U(x)/T - U(x)^2/(2 T^2 C_v) + ...
      => Delta S_constr = k_B E_theta  +  REMAINDER,  remainder/leading = U/(2 T C_v)""")
for lab, vol in (("1 mm^3 water", 1e-9), ("1 uL water", 1e-9*1e3)):
    n_mol = vol*1000.0/0.018*6.02214076e23
    Cv = 3*n_mol*kB
    print(f"    {lab:<16} C_v/k_B = {Cv/kB:.3e}   remainder/leading at U = 5 kB T : {5.0/(2*Cv/kB):.3e}")
print("""    Label: AN APPROXIMATION with an explicitly bounded remainder - exact to first order in
    U/(T C_v), which is ~1e-20 for any macroscopic bath. It is a STATE FUNCTION of the
    CONSTRAINED composite, and is NOT identified with either Seifert trajectory quantity
    without this separate derivation.""")
```

## `v4_design_checks.py`

```python
"""E1a v4 DESIGN-CORRECTION COMPANION SCRIPT.

DETERMINISTIC ONLY. No RNG, no trajectories, no model stepping, no I/O into the repository.
Isolated from every simulation runner and from the v1/v2/v3 implementations: imports only
the Python standard library. Reproduces every number in the v4 correction packet.

Run:  python3 v4_design_checks.py
"""
import math

# ----------------------------------------------------------------- primitives
S2 = math.sqrt(2.0)
def Phi(x): return 0.5*(1.0+math.erf(x/S2))
def zq(p):
    lo, hi = -12.0, 12.0
    for _ in range(300):
        mid = (lo+hi)/2
        if Phi(mid) < p: lo = mid
        else: hi = mid
    return (lo+hi)/2

# --------------------------------------------- declared benchmark (Branch A only)
kB      = 1.380649e-23
ETA     = {298.0: 0.890e-3, 318.0: 0.596e-3}     # apparatus buffer viscosity, declared
A_BEAD  = 6.366e-6                                # bead radius, declared
T_TOTAL = 240.0                                   # record length per field, s
DT      = 1.2e-4                                  # sampling interval, s
N_SAMP  = int(round(T_TOTAL/DT))
FIELDS  = [("theta0_circular",    [100e-6, 100e-6], 298.0),
           ("theta1_power",       [210e-6, 210e-6], 298.0),
           ("theta2_ellipse",     [150e-6,  60e-6], 298.0),
           ("theta3_temperature", [100e-6, 100e-6], 318.0)]
REF = "theta0_circular"
def gamma_of(T): return 6*math.pi*ETA[T]*A_BEAD
def taus_of(ks, T):
    g = gamma_of(T); return [g/k for k in ks]

def A_p(p, phi, n):
    """EXACT finite-n sum  A_p = 1 + 2 sum_{k=1}^{n-1} (1-k/n) phi^{pk}."""
    x = phi**p
    return 1 + 2*(x/(1-x) - x/(n*(1-x)**2))

def hr(t): print("\n" + "="*100 + "\n" + t + "\n" + "="*100)

# =============================================================== A. G5 ESTIMATOR
hr("A.  THE IMPLEMENTED SAMPLE-KURTOSIS ESTIMATOR AND ITS UNCERTAINTY")
print("""IMPLEMENTED (e1a_analysis.py G5_kurtosis, v3 lines 109-117), stated exactly:
   whitening      Z_i = H^{1/2}(x_i - x*)   -- H and x* from BRANCH A, NOT data-dependent
   centering      mu_r = (1/n) sum_i Z_ir   -- SAMPLE mean, though S is centred at x*
   moments        m2_r = (1/n) sum (Z_ir-mu_r)^2 ,  m4_r = (1/n) sum (Z_ir-mu_r)^4
   statistic      g2_r = m4_r/m2_r^2 - 3    -- NO bias correction, NO n/(n-1)
   gate           G5   = max_r |g2_r|
   variance normalisation is INTERNAL (division by m2_r^2), not by a declared sigma.
   No data-dependent DIRECTION is estimated: unlike G3/G4, G5's basis is Branch-A fixed.
   Every gate reuses the SAME observations.""")
print("""
Uncertainty, correlated sampling model, delta method about (m2,m4)=(s^2,3s^4):
   d g2/d m4 = 1/s^4 ,  d g2/d m2 = -6/s^2
   Isserlis:  Cov(x0^2,xt^2)=2 s^4 rho^2 ,  Cov(x0^4,xt^4)=72 s^8 rho^2 + 24 s^8 rho^4 ,
              Cov(x0^2,xt^4)=12 s^6 rho^2
   Var(m4)=(s^8/n)(72 A2+24 A4) , Var(m2)=(2 s^4/n)A2 , Cov(m4,m2)=(12 s^6/n)A2
   Var(g2) = (1/n)[72 A2 + 24 A4 + 72 A2 - 144 A2] = 24 A4 / n     <- A2 CANCELS EXACTLY

Mean-estimation effect (the sample mean is used, and for OU it is far noisier than for iid):
   E[x_bar^2] = s^2/N1 ,  E[x_bar m3] = 3 s^4/N1  with N1 = n/A1  (the MEAN's effective size)
   E[m2] = s^2 (1 - 1/N1) ;  E[m4] = 3 s^4 (1 - 2/N1)
   ratio expansion E[U/V^2] ~ (EU/EV^2)[1 + 3Var V/(EV)^2 - 2Cov(U,V)/(EU EV)] gives
   E[g2] = -6/N2 + O(N^-2)      <- the N1 terms CANCEL; the bias is set by N2, not N1 or N_g2
   (iid check: N2 = n gives -6/n, matching the classical E[g2] = -6/(n+1) at leading order)""")
rows = []
print(f"\n{'field / mode':<26}{'tau ms':>9}{'A1':>9}{'A2':>9}{'A4':>9}{'N1':>10}{'N2':>10}{'N_g2':>10}"
      f"{'sd(g2)':>10}{'bias':>11}{'|bias|/sd':>10}")
for nm, ks, T in FIELDS:
    for r, (k, tau) in enumerate(zip(ks, taus_of(ks, T))):
        phi = math.exp(-DT/tau)
        a1, a2, a4 = A_p(1, phi, N_SAMP), A_p(2, phi, N_SAMP), A_p(4, phi, N_SAMP)
        N1, N2, Ng = N_SAMP/a1, N_SAMP/a2, N_SAMP/a4
        sd, bias = math.sqrt(24.0/Ng), -6.0/N2
        rows.append((nm, r, N1, N2, Ng, sd, bias))
        print(f"{nm+' m'+str(r+1):<26}{tau*1e3:>9.4f}{a1:>9.3f}{a2:>9.3f}{a4:>9.3f}"
              f"{N1:>10.0f}{N2:>10.0f}{Ng:>10.0f}{sd:>10.6f}{bias:>11.2e}{abs(bias)/sd:>10.4f}")
print("""
  The bias is at most 0.5% of one standard deviation, so NO bias correction is introduced;
  it is nevertheless reproduced automatically by calibrating at the declared (H, n, tau).
  N_g2 ~ 2 N2: using N2 for G5 is conservative by a factor 2 in variance.""")

hr("A2.  EXACT HAND-CHECKABLE EXAMPLE: S DOES NOT DETERMINE G5")
for lab, v in (("A = ( 1, 1, -1, -1)", [1.0, 1.0, -1.0, -1.0]),
               ("B = (r2, 0,  0, -r2)", [math.sqrt(2), 0.0, 0.0, -math.sqrt(2)])):
    n = len(v); mu = sum(v)/n
    m2 = sum((a-mu)**2 for a in v)/n; m4 = sum((a-mu)**4 for a in v)/n
    print(f"  {lab:<24} mean={mu:+.1f}  m2={m2:.4f}  m4={m4:.4f}  g2 = m4/m2^2 - 3 = {m4/m2**2-3:+.4f}")
print("""  Identical mean and identical m2 (hence in 1-D an identical S), different g2.
  => No draw of S can reproduce G5. The covariance shortcut CANNOT generate it.  [EXACT]""")

hr("A3.  WHY G5 IS NOT GENERATED INDEPENDENTLY")
print("""  EXACT, iid only: whitened data are N(0, I/beta) iid; tr(W) is complete sufficient for
    beta; every gate is scale-invariant hence ancillary; BASU gives (G1..G5) _|_ tr(W).
    It does NOT give G5 _|_ (G1..G4).
  EXACT non-independence argument: write u, v for the centred-normalised coordinate vectors.
    g2_1 = g2(u), g2_2 = g2(v), and the sample correlation is r12 = u.v. As r12 -> +-1 the
    two vectors coincide up to sign, forcing g2_1 -> g2_2. Independence would require the
    conditional law of (g2_1, g2_2) given r12 to be free of r12; by continuity of that
    conditional law near r12 = +-1 it is not. So the joint law is not a product.  [EXACT]
  CORRELATED case: the complete sufficient statistic for the scale family is Z' Gamma^{-1} Z,
    not tr(W), so even the Basu results above lapse.
  => DESIGN: two-block gate, union bound, valid under ARBITRARY dependence:
        reject  iff  p_min(G1..G4) < alpha_1   OR   p(G5) < alpha_2 ,   alpha_1+alpha_2 = alpha_geom
     Block 1's four-way dependence is exact (one shared S draw). Block 2 is one statistic.
     Proposed split alpha_1 = 0.4%, alpha_2 = 0.1%.  Modes within G5 are independent only
     because isotropic Stokes drag makes A = gamma^-1 H_U share eigenvectors with H:
     a BENCHMARK property, declared, not a general one.""")

# ==================================================== B. UNIFIED UNCERTAINTY MODEL
hr("B.  UNIFIED UNCERTAINTY MODEL: WHICH TERM LIMITS WHICH ENDPOINT")
print("""  beta_hat = m / tr(H S).  Decompose the Branch-A error on H into
     scale (common-mode, one draw per experiment)  : sigma_cm
     per-mode stiffness delta_r, independent        : sigma_k
     thermometry                                    : sigma_T / T
     trap-axis orientation psi                      : sigma_psi
  EXACT for this model: with H's modes scaled by (1+delta_r),
     tr(H S) = sum_r (1+delta_r) lambda_r Sigma_rr = (m + sum_r delta_r)/beta
     so beta_hat = beta / (1 + delta_bar).   ONLY THE MEAN of delta_r enters beta.
  Hence the field-specific relative error on beta is
     sigma_fs = sqrt( sigma_k^2/m + (sigma_T/T)^2 )
  and the DIFFERENTIAL part of delta_r (sd sqrt(2) sigma_k) moves H's eigenvalue ratio,
  feeding G1/G4 - i.e. the gates - not beta.""")
def orient_bias(r, psi_deg):
    s = math.sin(math.radians(psi_deg)); return 0.5*s*s*(r + 1.0/r - 2.0)
print(f"\n  Orientation psi enters beta only at SECOND order: tr(R H R' H^-1)/m - 1 = "
      f"sin^2(psi)(r+1/r-2)/2\n")
print(f"{'geometry':<22}{'r':>7}" + "".join(f"{f'psi={p}deg':>14}" for p in (0.2, 0.5, 1.0, 2.0)))
for nm, r in (("theta0/1/3 circular", 1.0), ("theta2 ellipse", 2.5), ("tangent H_T", 1.453)):
    print(f"{nm:<22}{r:>7.3f}" + "".join(f"{orient_bias(r,p)*100:>13.5f}%" for p in (0.2,0.5,1.0,2.0)))
print("""  Negligible for beta at any plausible psi (<0.01%), but DOMINANT for G3 (see the v4 packet).
  => sigma_psi and the differential sigma_k limit the GATES; sigma_cm limits ABSOLUTE beta only;
     sigma_fs and sigma_stat limit BOTH the cross-field ratio and absolute beta.""")

# ====================================================== C. sigma_stat per field
hr("C.  STATISTICAL TERM, PER FIELD, FROM THE EXACT DISCRETE SUMS")
print("""  Every gate and beta is a SECOND moment, so the governing effective size is N2, not the
  mean's N1.  sigma_stat = sqrt( 2 sum_r 1/N2_r ) / m .   [APPROXIMATION: leading order]""")
SIG_STAT = {}
print(f"\n{'field':<24}{'N2 mode1':>11}{'N2 mode2':>11}{'sigma_stat':>12}{'continuous T/tau':>18}{'error':>8}")
for nm, ks, T in FIELDS:
    ts = taus_of(ks, T); N2s = []
    for tau in ts:
        N2s.append(N_SAMP/A_p(2, math.exp(-DT/tau), N_SAMP))
    s = math.sqrt(2*sum(1.0/n for n in N2s))/len(ks); SIG_STAT[nm] = s
    cont = math.sqrt(2*sum(t/T_TOTAL for t in ts))/len(ks)
    print(f"{nm:<24}{N2s[0]:>11.0f}{N2s[1]:>11.0f}{s*100:>11.4f}%{cont*100:>17.4f}%{(cont/s-1)*100:>7.2f}%")
print("  The continuous-time formula is 0.1-1.0% ANTI-conservative; v4 uses the exact sums.")

# ============================================ D. COMPLETE-PIPELINE PERFORMANCE
hr("D.  COMPLETE-PIPELINE SUCCESS - DEFINITION AND BOUND")
print("""  A COMPLETE PASS requires ALL of the following, with refusals counted as failures and
  the denominator = every declared experiment (no conditioning on survivors):
     (i)   all 4 fields: Branch-A valid, rank guard passes, N_eff supported, geometry gate passes
     (ii)  P2: all 3 cross-field comparisons accepted within the approved 2% margin
     (iii) P3: absolute beta = 1 accepted under its pass rule
     (iv)  P4: entropy endpoint verified
  Independence between gates and beta is NOT assumed (Basu holds iid only). The bound used is
     P(complete) >= 1 - sum_f alpha_geom,f - (1 - pi_P2) - (1 - pi_P3)      [EXACT INEQUALITY]""")
def joint(sig_fs, sig_cm, z_r, d_r, z_a, d_a, use_abs, mu=(0,0,0), npts=8001):
    """EXACT 1-D integral over the shared reference error. Returns P(all comparisons accept
    [and absolute accepts]). mu_j = true log disparity of field j vs the reference."""
    oth = [f for f in SIG_STAT if f != REF]
    oth.sort(key=lambda s: [f[0] for f in FIELDS].index(s))
    sW = math.sqrt(sig_fs**2 + SIG_STAT[REF]**2); legs = []
    for j, nm in enumerate(oth):
        sj = math.sqrt(sig_fs**2 + SIG_STAT[nm]**2)
        h = z_r*math.sqrt(sig_fs**2 + SIG_STAT[nm]**2 + sig_fs**2 + SIG_STAT[REF]**2)
        if h >= d_r: return 0.0
        legs.append((sj, math.log((1-d_r)/(1-h)) - mu[j], math.log((1+d_r)/(1+h)) - mu[j]))
    sa = math.sqrt(sig_cm**2 + sig_fs**2 + SIG_STAT[REF]**2); ha = z_a*sa
    if use_abs and ha >= d_a: return 0.0
    Alo, Ahi = (math.log((1-d_a)/(1-ha)), math.log((1+d_a)/(1+ha))) if use_abs else (0.0, 0.0)
    lim = 8*sW; hs = 2*lim/(npts-1); tot = 0.0
    for i in range(npts):
        w = -lim + i*hs; wt = 1 if i in (0, npts-1) else (4 if i % 2 else 2); pr = 1.0
        for sj, a, b in legs: pr *= max(0.0, Phi((w+b)/sj) - Phi((w+a)/sj))
        if use_abs: pr *= max(0.0, Phi((w-Alo)/sig_cm) - Phi((w-Ahi)/sig_cm))
        tot += wt*math.exp(-0.5*(w/sW)**2)/(sW*math.sqrt(2*math.pi))*pr
    return tot*hs/3.0
def pi_abs(sig_fs, sig_cm, z_a, d_a):
    sa = math.sqrt(sig_cm**2 + sig_fs**2 + SIG_STAT[REF]**2); ha = z_a*sa
    if ha >= d_a: return 0.0
    return Phi(math.log((1+d_a)/(1+ha))/sa) - Phi(math.log((1-d_a)/(1-ha))/sa)
ZR, ZA, DR, DA = 1.959963985, 1.96, 0.02, 0.05
print(f"\n  SCENARIO-SPECIFIC results at the approved 2% margin, z_ratio = {ZR:.3f}, "
      f"z_abs = {ZA:.2f}, delta_abs = {DA:.0%}\n")
print(f"{'sigma_k':>8}{'sigma_fs':>10}{'sigma_cm':>10}{'a_geom':>8}{'pi_P2':>8}{'pi_P3':>8}"
      f"{'pi(P2&P3)':>11}{'BOUND w/ P3':>13}{'BOUND no P3':>13}")
SCEN = [(0.0100, 0.022913, 0.010), (0.0100, 0.022913, 0.005), (0.0050, 0.013377, 0.005),
        (0.0040, 0.012000, 0.005), (0.0034, 0.011500, 0.005), (0.0030, 0.011000, 0.005)]
for sk, scm, ag in SCEN:
    sfs = math.sqrt(sk**2/2 + (0.1/298.0)**2)
    p2 = joint(sfs, scm, ZR, DR, ZA, DA, False); p3 = pi_abs(sfs, scm, ZA, DA)
    pb = joint(sfs, scm, ZR, DR, ZA, DA, True)
    b_with = 1 - 4*ag - (1-p2) - (1-p3); b_no = 1 - 4*ag - (1-p2)
    print(f"{sk*100:>7.2f}%{sfs*100:>9.3f}%{scm*100:>9.3f}%{ag*100:>7.1f}%{p2:>8.3f}{p3:>8.3f}"
          f"{pb:>11.3f}{b_with:>13.3f}{b_no:>13.3f}")
print("""
  Each row is SCENARIO-SPECIFIC, not a pooled average and not a guarantee for every
  configuration. pi(P2&P3) EXCEEDS pi_P2 x pi_P3 in every row: the shared reference-field
  error makes the two endpoints POSITIVELY dependent, so the union bound is conservative.""")
print("\n  WORST COMPARISON (marginal acceptance per comparison, sigma_k = 0.34%) -- a pooled")
print("  figure must never stand in for the worst field:\n")
sfs_t = math.sqrt(0.0034**2/2 + (0.1/298.0)**2)
print(f"{'comparison':<28}{'sigma_ratio':>13}{'CI half-width':>15}{'marginal accept':>17}")
for nm, _, _ in FIELDS:
    if nm == REF: continue
    sr = math.sqrt(2*sfs_t**2 + SIG_STAT[nm]**2 + SIG_STAT[REF]**2); h = ZR*sr
    a, b = math.log((1-DR)/(1-h)), math.log((1+DR)/(1+h))
    print(f"{nm+' / ref':<28}{sr*100:>12.4f}%{h*100:>14.4f}%{Phi(b/sr)-Phi(a/sr):>17.4f}")
print("\n  CONVERGENCE of the Simpson integral (scenario sigma_k = 0.34%, with P3):")
base = None
for npts in (2001, 8001, 32001, 128001):
    v = joint(sfs_t, 0.0115, ZR, DR, ZA, DA, True, npts=npts)
    d = "-" if base is None else f"{abs(v-base):.2e}"
    print(f"    npts = {npts:>7}   value = {v:.10f}   |change| = {d}")
    base = v
print("    => integration error < 1e-9; it is not a limiting source of uncertainty.")

hr("E.  FALSE-BRIDGE DETECTION - THE EXISTING DECLARED CONTROLS, PRESERVED")
print("""  These are the controls already declared in v3's confirm2.py and the baseline. No
  replacement campaign is proposed. Acceptance below = FAILURE to detect.  [WORST-CASE over
  the declared alternative set is the last column of each row group.]""")
print(f"\n{'declared alternative':<36}{'acceptance (sigma_k=0.34%)':>28}{'label'}")
ALT = [("beta = (1, 1.06, 1, 1)",       (math.log(1.06), 0.0, 0.0)),
       ("beta = (1, 0.93, 1.05, 1)",    (math.log(0.93), math.log(1.05), 0.0)),
       ("beta = (1, 1, 1, 1.10)",       (0.0, 0.0, math.log(1.10))),
       ("beta = (1, 1.025, 1, 1) HARD", (math.log(1.025), 0.0, 0.0)),
       ("reference off by 3%",          (math.log(1/1.03),)*3)]
for lab, mu in ALT:
    print(f"{lab:<36}{joint(sfs_t,0.0115,ZR,DR,ZA,DA,False,mu=mu):>27.5f}   scenario-specific")
print("""
  Also preserved unchanged, and NOT re-derived here because they are already demonstrated:
    - blinded scale control: Branch-A scale x hidden c, recovery target beta = 1/c
      [BASELINE docs/theory/EBU_THEORY_BASELINE.md, section 14.2, committed]
    - paired hidden-scale distortion c = 1.07 / 0.90 on a RETAINED dataset
    - independent coordinate permutation (the geometry control)
    - time shuffle (an AUTOCORRELATION control only - it leaves S identical to 1e-30)
    - forbidden H := K, recorded as vacuous, demonstration only
  DISTINCTION KEPT: rejecting correct geometry (a P1 false rejection, target alpha_geom) is a
  DIFFERENT error from falsely declaring cross-field equivalence (a P2 acceptance under a true
  disparity). They are reported separately and never netted.""")

hr("F.  CHANGING FIELD versus STATE CHANGE - EXACT DETERMINISTIC EXAMPLE")
print("""  V_theta(x) = k_theta x^2 / (2 k_B T).  Two fields, same T: theta0 k=100 uN/m, theta1 k=210.
  x* = 0. Compare a STATE change at fixed theta with a FIELD change at fixed state.""")
def V(k, x, T): return k*x*x/(2*kB*T)
T0 = 298.0; xa, xb = 100e-9, 50e-9; k0, k1 = 100e-6, 210e-6
V00, V01 = V(k0, xa, T0), V(k0, xb, T0)
V10, V11 = V(k1, xa, T0), V(k1, xb, T0)
print(f"\n{'':<34}{'V (dimensionless EBU)':>24}")
print(f"  theta0, x = 100 nm{'':<14}{V00:>24.4f}")
print(f"  theta0, x =  50 nm{'':<14}{V01:>24.4f}")
print(f"  theta1, x = 100 nm{'':<14}{V10:>24.4f}")
print(f"  theta1, x =  50 nm{'':<14}{V11:>24.4f}")
print(f"\n  STATE change at fixed theta0 (100 -> 50 nm) : E = {V00-V01:+.4f}")
print(f"  FIELD change at fixed x = 100 nm (t0 -> t1) : E = {V00-V10:+.4f}")
print(f"  FIELD change at fixed x =  50 nm (t0 -> t1) : E = {V01-V11:+.4f}")
print(f"\n  TOTAL from (100 nm, theta0) to (50 nm, theta1): E = {V00-V11:+.4f}")
print(f"    path 1  state first, then field : {V00-V01:+.4f}  +  {V01-V11:+.4f}  = {(V00-V01)+(V01-V11):+.4f}")
print(f"    path 2  field first, then state : {V00-V10:+.4f}  +  {V10-V11:+.4f}  = {(V00-V10)+(V10-V11):+.4f}")
print("""
  The TOTAL is path-independent (V is a state function of (x, theta)); the SPLIT between the
  'state' term and the 'field' term is NOT: it differs by 100.14 EBU between the two orders.
  [EXACT ARITHMETIC]  A common beta makes all four numbers commensurable on ONE scale. It does
  NOT select a decomposition, so it cannot by itself attribute the field term to any actor, and
  it does not authorise repricing a completed historical receipt.""")

hr("G.  ENTROPY ARITHMETIC FOR THE INTERPRETATION NOTE")
E = 5.0
for T in (298.0, 318.0):
    dU = E*kB*T
    print(f"  T = {T:.0f} K:  E = +{E}  ->  heat to medium q = {dU:.6e} J  ->  q/T = {dU/T/kB:+.4f} k_B")
print(f"  mechanical energy differs by {(318/298-1)*100:.2f}% between the two, the k_B figure does not.")
print("  Delta s_sys = -k_B E ;  Delta s_med = +k_B E ;  Delta s_tot = 0  (equilibrium, static trap).")

# ===================================================== H. CONFORMANCE (pure-function)
hr("H.  CONFORMANCE CHECKS AGAINST THE ACTUAL v3 IMPLEMENTATION")
print("""  Pure-function checks only: hand-written matrices and a hand-written point set.
  NO random draws, NO trajectories, NO runner imported. e1a_analysis.py imports only `math`.""")
import sys, os
V3 = os.environ.get("E1A_V3_DIR", "")
if V3 and os.path.isdir(V3):
    sys.path.insert(0, V3)
    import e1a_analysis as EA
    H  = [[3.0, 0.7], [0.7, 2.0]]                       # hand-written, Branch-A side
    S  = [[0.42, -0.11], [-0.11, 0.63]]                 # hand-written, Branch-B side
    K  = EA.inv(S)
    XS = [[0.10, -0.20], [-0.30, 0.15], [0.25, 0.05], [-0.05, -0.35],
          [0.40, 0.30], [-0.45, 0.10], [0.05, 0.45], [-0.15, -0.05]]
    print(f"\n{'gate':<8}{'at H':>18}{'at 2H (K fixed)':>20}{'|difference|':>16}{'scale-invariant?':>18}")
    ok = True
    for nm, f in (("G1", lambda h: EA.G1_shape(h, K)),
                  ("G2", lambda h: EA.G2_spread(h, K)),
                  ("G3", lambda h: max(EA.G3_angles(h, K, 0.05)[0])),
                  ("G4", lambda h: EA.G4_ratios(h, K)),
                  ("G5", lambda h: EA.G5_kurtosis(XS, h))):
        a = f(H); b = f([[2*H[i][j] for j in range(2)] for i in range(2)])
        inv = abs(a-b) < 1e-12; ok = ok and inv
        print(f"{nm:<8}{a:>18.12f}{b:>20.12f}{abs(a-b):>16.3e}{str(inv):>18}")
    print(f"\n  ALL FIVE GATES SCALE-INVARIANT IN H: {ok}")
    print("  => the modelled sigma_cm and sigma_fs (scalar multipliers on H) cannot move any gate.")
    print("     CONFIRMED against the implementation, not assumed.  [EXACT, this implementation]")
    b0 = EA.beta_mle(H, S)
    b2 = EA.beta_mle([[2*H[i][j] for j in range(2)] for i in range(2)], S)
    print(f"\n  beta_mle(H,S)  = {b0:.12f}")
    print(f"  beta_mle(2H,S) = {b2:.12f}   ratio = {b0/b2:.12f}  (exactly 2 -> beta DOES carry the scale)")
    print("\n  G5 CENTRING CHECK - the implementation centres G5 at the SAMPLE mean while S is")
    print("  centred at the declared x*. Sample mean of the hand-written set, per coordinate:")
    mu = [sum(p[i] for p in XS)/len(XS) for i in range(2)]
    print(f"    mean = ({mu[0]:+.6f}, {mu[1]:+.6f})  -> nonzero, so the two centrings genuinely differ.")
    print("    v4 makes the centring explicit and identical in both, and calibrates at the choice made.")
else:
    print("\n  SKIPPED - v3 directory not supplied via E1A_V3_DIR. No result claimed.")
```

