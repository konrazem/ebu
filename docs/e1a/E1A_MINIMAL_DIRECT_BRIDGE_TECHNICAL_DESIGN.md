# E1a — MINIMAL DIRECT BRIDGE: TECHNICAL DESIGN

## Exact OU likelihood, measurement-error propagation, sample-size requirement, topology interface

```
STATUS:                        DESIGN ANALYSIS ONLY
CURRENT E1a-v4:                PRESERVED AND PAUSED
CURRENT E1a-v4 AUTHORITY:      UNCHANGED
NEW DESIGN:                    NOT YET AUTHORITATIVE
OFFICIAL LONG-RUN CAMPAIGN:    NOT RUN
REAL OPTICAL-TRAP EXPERIMENT:  NOT RUN
EXECUTION SEAL:                NOT FROZEN
EXECUTION AUTHORISED:          FALSE
```

No scientific RNG, no trajectory, no calibration draw, no campaign job. Every number below
comes from declared repository constants through production code, or from closed-form
algebra. Nothing is invented; where a quantity is unavailable it is marked UNKNOWN or NOT
MEASURED.

| | |
|---|---|
| analysed at HEAD | `dd0d6b0e5d370de1bda805e07215ea0be4d6d083` |
| plan version | `1.17.0` |
| working tree | clean |
| authority read | foundation, theory baseline, design §§1–15, contract, plan JSON, bounded analysis, pause record |

---

## 1. Summary of conclusions

| | |
|---|---|
| direct Boltzmann bridge ≡ current Gaussian target | **CONDITIONAL** — exactly equivalent for harmonic `V`; strictly stronger otherwise |
| whitened-covariance `β̂` is a new estimator | **NO** — algebraically identical to `m/tr(H_A S)` |
| exact OU likelihood can replace the Monte-Carlo primary null | **CONDITIONAL** — yes for the Gaussian benchmark, conditional on finite-`N` size verification |
| 46,000 calibration artifacts still required | **NO** for the primary null; a far smaller size study remains |
| achieved-size verification still required | **YES** |
| current synthetic Branch-A error model adequate for real Route A | **NO** |
| absolute `β = 1` test systematics-limited | **YES** — `σ_cm` is 95% of the P3 variance at `N = 2×10⁶` |
| cross-field test limited by the same components | **NO** — `σ_cm` cancels exactly; `σ_fs` and `σ_stat` bind |
| `N = 2,000,000` necessary | **NOT ESTABLISHED** |
| implementation ready to begin | **NO** |

**The three results that should change the programme's direction:**

**R-1. The exact likelihood buys almost no precision.** Derived below: with the temporal
law estimated, `Var(log β̂) = 2 / (N Σ_r A_r⁻¹)` against the moment estimator's
`(2/N)(Σ_r A_r)/d²`. These are **equal** for isotropic fields and differ by `1.0566×` for
`theta2_ellipse`. The current moment estimator is already near-efficient. The likelihood's
value is the **analytic null distribution**, not precision — and that is what removes the
46,000 artifacts.

**R-2. The nuisance-parameter choice is decided by arithmetic, not taste.** Fixing the
temporal law at the Branch-A value `τ = γ/k` (strategy L1) improves the absolute endpoint
by **0.11%** and the cross-field endpoint by **2.45%**, in exchange for making the primary
estimate depend on the undeclared F4 drag inputs. Leaving `F` a free Branch-B nuisance
(strategy L2) costs essentially nothing and removes `η` and `a` from the point estimate
entirely. **L2.**

**R-3. Under Route A the temperature arm carries an undeclared field-specific systematic.**
`θ3` is the arm that tests the `k_B T` normalisation — the common-ruler claim itself. Under
force–displacement with Stokes drag, `k ∝ η(T)a`, so the **undeclared viscosity model
`η(T)`** enters `H_θ3` differently from the other three fields. An `η(T)` model error is
therefore *field-specific*, not common-mode, and does **not** cancel in the cross-field
comparison. This is the sharpest form of the Route-A gap and it sits on the most
load-bearing arm.

---

## 2. The bridge, and why the whitened estimator is not new

### 2.1 Equivalence chain

Foundation §3 fixes `E(x_pre → x_post | θ) = V(x_pre;θ) − V(x_post;θ)` and design §1 fixes
the thermal normalisation `V_θ(x) = [U_θ(x) − U_θ(x*_θ)] / (k_B T_θ)`. The proposed primary
statement is

```
p_θ(x) ∝ exp[ −β_θ V_θ(x) ]            with the prediction β_θ = 1
```

For the harmonic benchmark `V_θ(x) = ½ (x−x*)ᵀ H_θ (x−x*)`, write `z = H_θ^{1/2}(x−x*)`, so
`V_θ = ½‖z‖²`. Then

```
p ∝ exp(−β·½‖z‖²)   ⟺   z ~ N(0, β⁻¹ I)
                     ⟺   S_z := H^{1/2} Σ H^{1/2} = β⁻¹ I
                     ⟺   Σ = β⁻¹ H⁻¹
                     ⟺   K := Σ⁻¹ = β H          (design §7's K = βH)
```

all four statements are the same statement for a Gaussian. Outside the Gaussian family they
are **not**: `−ln p = βV + C` constrains the whole landscape, whereas `K = βH` constrains
only curvature at a point. That is the one genuine scientific gain of the reformulation.

### 2.2 The estimator is the existing estimator

```
tr(S_z) = tr(H^{1/2} Σ H^{1/2}) = tr(Σ H) = tr(H_A S)      (cyclicity)
⟹   β̂ = d / tr(S_z)  ≡  m / tr(H_A S)                      (design §4)
```

Verified bit-exactly on a deterministic SPD pair, no RNG:

```
H = [[2.5,0.7],[0.7,1.3]]   S = [[0.41,−0.18],[−0.18,0.86]]
d/tr(S_z)   = 1.0576414595452142
m/tr(H_A S) = 1.0576414595452142      tr equal at 1.891, relative difference 0.0
```

The energy form is the same again: `E[V] = d/(2β)` gives `β̂ = d/(2V̄)`, and for a harmonic
`V` the Boltzmann likelihood of §8 has `ln Z(β) = (d/2)ln(2π/β) − ½ln|H|`, so
`∂ℓ/∂β = 0 ⟹ β̂ = (d/2)/V̄`. MLE and moment estimator coincide.

**`β̂` is a ratio estimator and is biased**: `E[1/X] ≠ 1/E[X]`. Design §4 already carries the
exact finite-sample identity `β̂ = mβ / tr(G M)` with `G = H_true^{-1/2} H_A H_true^{-1/2}`.
Any redesign inherits this and must carry that identity forward.

---

## 3. The exact discrete-time OU model

### 3.1 Continuous-time physics and its assumptions

Design §3 fixes `τ_r = γ/k_r` with `γ = 6π η(T) a`, and contract `relaxation_time_rule`
repeats it. The overdamped Langevin equation for `y = x − x*` is

```
dy_t = −γ⁻¹ H_U y_t dt + sqrt(2 k_B T γ⁻¹) dW_t
```

**Physical assumptions required, each load-bearing:**

| # | assumption | where it is used | what breaks without it |
|---|---|---|---|
| A1 | overdamped limit (inertia negligible) | first-order SDE | a second-order (Kramers) model; `F` no longer a single exponential |
| A2 | **scalar (isotropic) drag** `γ`, not a tensor `Γ` | `γ⁻¹H_U` symmetric | `Γ⁻¹H_U` not symmetric; `F` and `H` need not commute; §3.3 fails |
| A3 | harmonic `U_θ`, constant `H_U` | linear drift | non-Gaussian stationary law; `S_z = I` is no longer the bridge |
| A4 | equilibrium / detailed balance, no probability current | `Σ = (βH)⁻¹`, `F` symmetric | nonequilibrium steady state; this is the §27 future programme |
| A5 | fixed `θ` during the record | time-invariant `F`, `Q` | the field-changing problem of §27 |
| A6 | exact stationary initialisation | no burn-in term | a transient bias at small `N` |
| A7 | noiseless position observation | `Σ_obs = Σ` | detector noise adds a white term to `Σ`, biasing `β̂` downward |

A7 is **not** currently declared anywhere in authority and is flagged in §12.

### 3.2 Exact discrete transition

Sampling at spacing `dt` gives an exact VAR(1), not an approximation:

```
y_{n+1} = F_θ y_n + ε_n ,      ε_n ~ N(0, Q_θ) i.i.d.
F_θ = exp(−γ⁻¹ H_{U,θ} dt)
```

The implementation realises this in the `H_true` eigenbasis (`modal_ou_parameters`,
`ou_observations`): with eigenvalues `λ_r` of `H_U` and `τ_r = γ/k_r`,

```
φ_r = exp(−dt/τ_r)
z_{r,0} ~ N(0, 1/(β λ_r)) ,   z_{r,n+1} = φ_r z_{r,n} + sqrt(1−φ_r²)·(β λ_r)^{-1/2}·ε
```

and the module records that Euler–Maruyama is **not** used because it inflates the
stationary covariance by `2/(2 − dt/τ)`.

### 3.3 Stationarity relation — verified, not assumed

Under A1–A6 the Lyapunov relation holds exactly:

```
Q_θ = Σ_θ − F_θ Σ_θ F_θᵀ ,       Σ_θ = β_θ⁻¹ H_θ⁻¹
```

Checked numerically on `theta2_ellipse` — the only declared field that is **both**
anisotropic and rotated, so the one where a commutation failure would show:

```
max |Q − (Σ − F Σ Fᵀ)| vs the modal construction : 6.16e−33
max |Σ − (βH)⁻¹|                                  : 1.54e−32
[F,H] = 0 : max|FH−HF| / scale                    : 1.71e−16   (rounding)
F asymmetry : 2.78e−17 absolute, 4.84e−17 relative (rounding)
F = [[0.419257780046, −0.133820401271], [−0.133820401271, 0.573780269440]]
```

**`F` is symmetric and commutes with `H` because of A2 and A4 together**, not by
convention: `F = exp(−(k_B T/γ) H dt)` is a matrix function of `H`. Under a drag *tensor*
this fails. The redesign must either keep A2 as a declared assumption or let `F` be a
general matrix — which strategy L2 below does anyway, making the design robust to A2.

---

## 4. Nuisance-parameter strategy — L1 vs L2

### 4.1 The two candidates

**L1 — physical dynamics parameterisation.** Parameters `(β; γ or η,a; H_U, T, dt)`. The
temporal law is *fixed* at the Branch-A value `φ_r = exp(−dt k_r/γ)`.

**L2 — statistical transition nuisance parameterisation.** Parameters `(β; F)`, with `H`
supplied by Branch A and the stationary covariance constrained to `Σ = β⁻¹H⁻¹`. `F` is a
free Branch-B nuisance matrix subject only to stability (`spec(F) ⊂` unit disc) and
`Q = Σ − FΣFᵀ ≻ 0`.

### 4.2 Identifiability

The Branch-B record identifies the stationary VAR(1) completely: `Σ` from the marginal and
`F = Σ_1 Σ⁻¹` from the lag-1 autocovariance. So `F` is identified **without any Branch-A
input**, and `β` enters *only* through the constraint `Σ = β⁻¹H⁻¹`. The bridge hypothesis is
therefore exactly the statement that the Branch-B-identified `Σ` lies on the ray
`{β⁻¹H⁻¹ : β > 0}` fixed by Branch A.

**Does L2 preserve Branch-A / Branch-B independence?** Yes, and the boundary is sharp.
Design §2.1 forbids the corner-frequency route `k = 2π f_c γ` because it *reconstructs `H`*
from the Branch-B fluctuation record. L2 never does: `H` is supplied by Branch A and is
never estimated, adjusted or checked against the data. `F` is a pure temporal nuisance and
enters no statement about `H`. **This must be written into any redesigned preregistration
explicitly** — "the Branch-B record may inform the temporal nuisance parameter and may never
inform `H`" — rather than left implicit.

**Restrictions on `F`.** Minimum: stability and `Q ≻ 0`. Optionally `F` symmetric and
commuting with `H` (A2 + A4), which reduces `F` from `d²` to `d` parameters. The report
recommends **not** imposing it for the primary fit, because then A2 becomes testable rather
than assumed.

### 4.3 The decision, quantitatively

Derived in §6: with `φ` **known** the per-mode `Var(log β̂) = 2/N`; with `φ` **estimated**
it is `(2/N)(1+φ²)/(1−φ²)`. So L1 is genuinely more precise. By how much:

| field | SE(log β̂) under L2 | under L1 | L2/L1 |
|---|---|---|---|
| `theta0_circular` | 9.0241e−04 | 7.0711e−04 | 1.2762× |
| `theta1_power` | 7.4308e−04 | 7.0711e−04 | 1.0509× |
| `theta2_ellipse` | 9.1470e−04 | 7.0711e−04 | 1.2936× |
| `theta3_temperature` | 9.0241e−04 | 7.0711e−04 | 1.2762× |

Propagated to the endpoints at `N = 2×10⁶`:

```
P3 absolute    : L2 h = 0.023104    L1 h = 0.023078    L1 better by 0.11%
P2 cross-field : L2 h = 0.007184    L1 h = 0.007008    L1 better by 2.45%
```

**L1 buys 0.11% and 2.45% in exchange for making the primary scientific estimate depend on
`η` and `a` — quantities the contract lists as undeclared (F4 OPEN) and whose uncertainties
are undeclared.** That is a bad trade, and it is the trade the current design implicitly
makes by taking `τ` from Branch A.

> **RECOMMENDED: L2.** `β` is the bridge parameter, `H` is Branch-A measured, `F` is a
> Branch-B nuisance. `η` and `a` leave the primary inference entirely.

---

## 5. The exact likelihood

Let `w_n = H^{1/2} y_n` (whitening by the Branch-A `H`, which is data-independent), and
`F̃ = H^{1/2} F H^{−1/2}`. Under the bridge `Cov(w) = β⁻¹ I`, so the innovation covariance is
`Q_w = β⁻¹(I − F̃F̃ᵀ)`.

**Stationary (exact, including the `t = 0` term):**

```
ℓ(β, F̃) = log N(w_0 ; 0, β⁻¹I)  +  Σ_{n=0}^{N−2} log N(w_{n+1} ; F̃ w_n , β⁻¹(I − F̃F̃ᵀ))
```

Expanding, with `M := (I − F̃F̃ᵀ)⁻¹` and
`R(F̃) := w_0ᵀw_0 + Σ_n (w_{n+1} − F̃w_n)ᵀ M (w_{n+1} − F̃w_n)`:

```
ℓ = −(Nd/2) log(2π)  +  (Nd/2) log β  +  ((N−1)/2) log det M  −  (β/2) R(F̃)
```

**`β` enters as an exact scale parameter**, so for fixed `F̃` the conditional MLE is closed
form:

```
β̂(F̃) = N d / R(F̃)
```

and the profile likelihood `ℓ_p(β) = ℓ(β, F̃(β))` is obtained by maximising over `F̃`. The
implementation would therefore be: whiten by `H`; fit the VAR(1) nuisance; read `β̂` off the
closed form; profile for the interval.

**Parameter classification:**

| parameter | class |
|---|---|
| `β_θ` | **scientific parameter of interest** |
| `H_θ`, `T_θ`, `x*_θ` | **Branch-A measured inputs**, supplied, never estimated from Branch B |
| `F̃_θ` (or `F_θ`) | **Branch-B nuisance**, profiled |
| `dt`, `N` | design constants |

**Profiling vs marginalising:** profiling is sufficient and is what standard likelihood
theory covers; `β` and `F̃` are *not* information-orthogonal (§6), so the profile must be
used rather than plugging in a separately fitted `F̃` and treating `β̂` as if `F̃` were known.
Treating `F̃` as known is exactly the error that produces the spuriously optimistic
`sqrt(2/(Nd))` rate.

**Non-Gaussian successor.** For general `V_θ`, `ℓ(β) = −β Σ_i V_θ(x_i) − N log Z_θ(β)` with
`Z_θ(β) = ∫ e^{−βV_θ} dx` computed numerically, plus a temporal-correlation treatment that
is no longer VAR(1). That path exists; it is outside this benchmark.

---

## 6. Statistical precision — derived, not asserted

### 6.1 Single mode

In one mode, `z_{n+1} = φ z_n + σ_ε ε`, stationary variance `σ² = σ_ε²/(1−φ²) = 1/(βλ)`.
In the orthogonal parameterisation `(σ_ε², φ)`, `I_{σ_ε²σ_ε²} = N/(2σ_ε⁴)` and
`I_{φφ} = N/(1−φ²)`. Since

```
log β = log(1−φ²) − log λ − log σ_ε²
∂logβ/∂logσ_ε² = −1 ,    ∂logβ/∂φ = −2φ/(1−φ²)
```

the delta method gives

```
Var(log β̂) = 2/N  +  (2φ/(1−φ²))² · (1−φ²)/N  =  (2/N) · (1+φ²)/(1−φ²)
```

> **Temporal correlation DOES cost precision, and the naive argument that it cannot —
> "the innovations are i.i.d., so the scale is estimated at the i.i.d. rate" — is wrong.**
> It is wrong because `β` is a function of *both* the innovation scale and `φ`, so the
> error in `φ̂` propagates. With `φ` known the first term alone survives and
> `Var(log β̂) = 2/N`.

The factor `(1+φ²)/(1−φ²)` is exactly the `n → ∞` limit of the production
`A_closed_form(φ², n)` (verified: relative difference `2.5e−07` at `n = 2×10⁶`,
`φ = 0.489`). So the exact likelihood with `φ` estimated pays **precisely the correlation
penalty the current moment estimator already pays.**

### 6.2 Multiple modes

```
likelihood (F estimated) :  Var(log β̂) = 2 / ( N Σ_r A_r⁻¹ )
moment (current)         :  Var(log β̂) = (2/N) ( Σ_r A_r ) / d²     [ = σ_stat² ]
```

By Cauchy–Schwarz `(Σ A_r)(Σ A_r⁻¹) ≥ d²`, so the likelihood is never worse, with equality
iff all `A_r` are equal. Computed at `N = 2×10⁶`:

| field | `A_r` | SE moment | SE likelihood | gain |
|---|---|---|---|---|
| `theta0_circular` | 1.6287, 1.6287 | 9.024e−04 | 9.024e−04 | **1.0000×** |
| `theta1_power` | 1.1043, 1.1043 | 7.431e−04 | 7.431e−04 | **1.0000×** |
| `theta2_ellipse` | 1.2649, 2.4713 | 9.665e−04 | 9.147e−04 | **1.0566×** |
| `theta3_temperature` | 1.6287, 1.6287 | 9.024e−04 | 9.024e−04 | **1.0000×** |

The derived moment variance reproduces production `sigma_stat()` exactly (equality to the
last bit for all four fields). The i.i.d. floor `sqrt(2/(Nd)) = 7.071e−04` is reached only
as `φ → 0`.

**Conclusion R-1: the exact likelihood is not a precision upgrade.** It is identical for
isotropic fields and 5.7% better for the one anisotropic field, because the trace weights
modes equally while the likelihood weights them by information. The current estimator is
already near-efficient. **The likelihood's payoff is the analytic null, not the error bar.**

---

## 7. The nested model hierarchy

| model | constraint | free parameters (4 fields, `d = 2`) |
|---|---|---|
| **M3** geometry free | `Σ_θ` unconstrained | `4 × 3 = 12` |
| **M2** field-specific scale | `Σ_θ = β_θ⁻¹ H_θ⁻¹` | `4` |
| **M1** one common scale | `Σ_θ = β⁻¹ H_θ⁻¹`, one `β` | `1` |
| **M0** EBU prediction | `β = 1` | `0` |

Likelihood-ratio degrees of freedom, and the correspondence to the current endpoints:

```
M2 vs M3   geometry        df = 8    (2 per field)     <->  current P1
M1 vs M2   cross-field     df = 3    (3 comparisons)   <->  current P2
M0 vs M1   absolute        df = 1                      <->  current P3
```

The per-field geometry test is a **sphericity** hypothesis on `S_z` with
`d(d+1)/2 − 1 = 2` constraints. The `df = 3` of M1 vs M2 is exactly P2's three comparisons
against the reference field. The structure of the current design survives the
reformulation unchanged — which is itself evidence that the current design's endpoint
decomposition is the right one.

**Interpretation:**

```
M0 adequate   absolute β = 1 and one common ruler supported
M1 needed     common ruler exists; the absolute normalisation is off by one global factor
M2 needed     the ruler changes with the field; cross-field commensurability fails
M3 needed     the geometry itself fails; no scalar rescaling reconciles physics and statistics
```

---

## 8. Model selection is not equivalence testing

**A non-significant likelihood-ratio test is not evidence of equivalence.** It is failure to
reject, which at small `N` is guaranteed and at large `N` is informative only about the
*direction* of departure, not its size. The current design is built on prospective
*equivalence* margins and intersection–union logic (design §§6–7), which is the correct
frame and must not be silently replaced by model selection.

**Recommended form, preserving the current logic:**

```
absolute    accept θ iff the (1−α) profile-likelihood interval for log β_θ
            lies inside [log(1−δ_abs), log(1+δ_abs)]            — conjunctive over 4 fields

cross-field accept comparison j iff the interval for log β_θj − log β_θ0
            lies inside [log(1−δ_cross), log(1+δ_cross)]        — conjunctive over 3 comparisons

geometry    the per-field M2-vs-M3 LRT, at α_geom, retained as a REJECTION test
            (it is a goodness-of-fit question, not an equivalence question)
```

Intersection–union keeps the size at the per-comparison level, so no multiplicity
adjustment, exactly as design §§6–7 state.

**Can the current margins be retained?** On the computed bands, yes comfortably:
`h ≈ 0.0231` against `δ_abs = 0.05`, and `h_j ≈ 0.0072` against `δ_cross = 0.02`. Neither is
strained at any record length down to `N ≈ 10⁵`. **This task does not change them.** A later
human scientific decision would be required only if the Route-A drag uncertainty of §11,
once declared, inflates `σ_cm` or `σ_fs` enough to make `h` approach `δ_abs` or `δ_cross` —
which cannot be evaluated until F4 declares those terms.

---

## 9. Absolute versus cross-field error model

Write, in logs,

```
log β̂_θ = log β_θ  −  c  −  f_θ  +  ε_θ
```

| term | meaning | declared value |
|---|---|---|
| `c` | **common-mode** Branch-A log-scale error, one draw per experiment, shared across fields | `σ_cm = 1.15%` |
| `f_θ` | **field-specific** Branch-A calibration error | `σ_fs = 0.243%` |
| `ε_θ` | Branch-B statistical error | `σ_stat`, per field, §6 |

The sign of `c` and `f_θ` is negative because an over-estimated `H_A` *reduces* `β̂`
(§10).

**Absolute endpoint.** All three terms enter:

```
Var(log β̂_θ) = σ_cm² + σ_fs² + σ_stat,θ²
h_θ = z · sqrt(σ_cm² + σ_fs² + σ_stat,θ²)                (design §7)
```

**Cross-field endpoint.** `c` is common to both fields and **cancels exactly**:

```
log β̂_θj − log β̂_θ0 = (log β_θj − log β_θ0) − (f_θj − f_θ0) + (ε_θj − ε_θ0)
Var = 2σ_fs² + σ_stat,j² + σ_stat,ref²
h_j = z · sqrt(2σ_fs² + σ_stat,j² + σ_stat,ref²)         (design §6)
```

matching design §6's "`sigma_cm` cancels exactly in the ratio and does not appear in `h_j`".

**Variance shares, computed:**

| | `σ_cm` | `σ_fs` | `σ_stat` |
|---|---:|---:|---:|
| absolute, `N = 50,000` | 77.47% | 3.45% | 19.08% |
| absolute, `N = 200,000` | 90.41% | 4.03% | 5.57% |
| absolute, `N = 2,000,000` | **95.17%** | 4.24% | 0.59% |
| cross-field, `N = 50,000` | — | 15.14% | **84.86%** |
| cross-field, `N = 200,000` | — | 41.65% | 58.35% |
| cross-field, `N = 2,000,000` | — | **87.71%** | 12.29% |

**The two endpoints are limited by different things and must be designed separately.** The
absolute test is `σ_cm`-bound at every record length. The cross-field test is
*statistics*-bound below `N ≈ 3×10⁵` and `σ_fs`-bound above it.

> **This corrects the bounded analysis at `dd0d6b0`**, which suggested `N ≈ 2×10⁵–10⁶`
> suffices. At `N = 2×10⁵` the cross-field endpoint is still 58% statistical and `h_j` is
> 55% above its systematic floor. The crossover is near `N ≈ 3×10⁵`, and diminishing
> returns begin near `N ≈ 5×10⁵–10⁶`.

---

## 10. Identifiability of absolute β

Let `H_A = c H_true` with `Σ = β_true⁻¹ H_true⁻¹`. Then

```
tr(H_A Σ) = tr(c H_true · β_true⁻¹ H_true⁻¹) = c d / β_true
β̂ = d / tr(H_A Σ) = β_true / c
```

Verified exactly (deterministic, no RNG):

```
c = 1.000 -> β̂ = 1.000000000000     1/c = 1.000000000000     exact
c = 1.070 -> β̂ = 0.934579439252     1/c = 0.934579439252     exact
c = 0.900 -> β̂ = 1.111111111111     1/c = 1.111111111111     exact
c = 1.150 -> β̂ = 0.869565217391     1/c = 0.869565217391     exact
```

This reproduces design §13's blinded-scale control (`c = 1.07 / 0.90`) exactly, confirming
C8 computes what it claims.

> **Absolute `β` and a common unknown Branch-A physical scale are exactly confounded.** No
> quantity of Branch-B data separates them, because `β` and `c` enter the likelihood only
> through the product. The absolute `β = 1` claim is therefore a claim about Branch-A
> absolute calibration, and it cannot be made more precise than `σ_cm`. At the declared
> `σ_cm = 1.15%`, the 95% absolute band is `±2.25%` **no matter how long the record**.

This is the mathematical content of R-2 in the bounded analysis, and it is why `σ_cm`, not
`N`, is the design variable that matters for the primary claim.

---

## 11. Branch-A error propagation under Route A

### 11.1 The measurement relation

Design §2.1 authorises exactly one mechanical route: **force–displacement with Stokes
drag**. The standard realisation applies a known viscous drag force by moving the medium at
velocity `v` and reading the equilibrium displacement `Δx`:

```
k Δx = γ v = 6π η(T) a v        ⟹        k = 6π η(T) a v / Δx
```

In logs, with `q = (log η, log a, log v, log Δx, T, ψ)` the primitive observables:

```
log k = log(6π) + log η + log a + log v − log Δx
```

so the Jacobian row for `log k` is `(+1, +1, +1, −1, ∂logη/∂T · ∂T, 0)`, and

```
H_θ = H_U(k_modes, ψ) / (k_B T_θ)
log H-scale = log k − log k_B − log T
```

### 11.2 First-order propagation

For `H = g(q)` with primitive covariance `C_A`:

```
C_H ≈ J_g C_A J_gᵀ
```

The terms, and their field structure — **this is the part that matters**:

| primitive | enters | varies across fields? | error class |
|---|---|---|---|
| `log η` at fixed `T` | `log k` with coefficient `+1` | no (one medium) | **common-mode `c`** |
| `log a` | `log k` with coefficient `+1` | no (one bead) | **common-mode `c`** |
| `η(T)` **model** | `log k_θ3` differs from the rest | **YES** — only `θ3` changes `T` | **field-specific `f_θ3`** |
| `log v` | `log k` with `+1` | per-calibration | partly common, partly field-specific |
| `log Δx` | `log k` with `−1` | per-field measurement | **field-specific `f_θ`** |
| detector scale `δ` | `Δx` **and** Branch-B `Σ` | no | **common-mode, correlated across branches** (§11.4) |
| `T_θ` | `H = H_U/(k_B T)` | yes | field-specific, declared as `σ_T` |
| `ψ` orientation | `H_U(k, ψ)` | yes | field-specific, declared as `σ_psi_deg` |

### 11.3 The θ3 finding

`θ3_temperature` is the only arm that changes `T` (298 K → 318 K). Under Route A its
stiffness is calibrated with `η(318 K)`, the others with `η(298 K)`. Water viscosity falls
roughly a third over that interval, so the **viscosity model `η(T)`** — which contract
`values_not_set.not_declared_here` lists explicitly as **not declared** — contributes a
*field-specific* error to `θ3` alone.

**Consequence.** It does **not** cancel in the cross-field comparison. It lands directly in
`f_θ3`, hence in `h_j` for the `θ3 vs θ0` comparison, which is the comparison that tests the
`k_B T` normalisation — the common-ruler claim itself. The arm carrying the most scientific
weight is the one with the undeclared systematic.

### 11.4 Detector-scale correlation between branches

If the position detector has scale error `δ` (measured `x_m = δx`), then

```
Σ_m = δ² Σ        and        Δx_m = δ Δx  ⟹  k_m = k/δ  ⟹  H_{A,m} = H/δ
tr(H_{A,m} Σ_m) = δ · tr(H Σ)        ⟹        β̂ = β_true / δ
```

The detector error propagates to `β̂` with power `−1`; it does **not** cancel between the
branches. This is **not** an anti-circularity violation — Branch A reads a displacement, not
the position histogram, so design §2.1 is satisfied — but it **is** a shared systematic that
must not be entered twice as if Branch A and Branch B were independent in this respect.

### 11.5 Terms required by Route A and currently absent from authority

```
σ_log η                              NOT DECLARED  (contract: "measurement uncertainty for eta")
σ_log a                              NOT DECLARED  (contract: "measurement uncertainty for a")
the viscosity model η(T) and its error  NOT DECLARED  (contract: "the viscosity model eta(T)")
σ_log v   (drag-flow velocity)       NOT DECLARED
σ_log Δx  (displacement readout)     NOT DECLARED
detector scale δ and its cross-branch correlation   NOT DECLARED
Cov(η, a) and any shared instrument covariance      NOT DECLARED
observation noise on Branch-B positions (A7)        NOT DECLARED
```

All are F4 territory. **None is repaired here.**

---

## 12. Is the current synthetic Branch-A error model adequate?

```
ANSWER: NO.
```

| element | what it does | consequence |
|---|---|---|
| `build_field` | `k_modes` comes from the contract spec `k_uN_per_m`; `viscosity` and `bead_radius` are **independent arguments** | `H_U` carries no `η`/`a` dependence at all |
| `BranchAErrorModel.measure` | perturbs `k_modes` by `σ_k`, `rot_deg` by `σ_psi_deg`, `T` by `σ_T`, scale by `σ_cm`; passes `η`, `a` through **unchanged** | no drag error ever reaches `H_A`; `η`/`a` are not even perturbed |
| `σ_fs` (contract) | `sqrt(σ_k²/m + (σ_T/T)²)` | **no drag term** |
| `η(T)` | not modelled; `η` is one constant for every field | the `θ3` finding of §11.3 cannot arise in simulation |
| observation noise | absent | A7 untestable |

The generator therefore cannot produce the error structure Route A would have, and **no
number of replicates can detect that**, because the dependency is absent from the generating
model rather than mis-estimated within it.

**This finding is independent of whether the exact OU likelihood is adopted.** It is a
property of the current synthetic Branch A versus the currently authorised laboratory route.

**What is required later, not now:** a prospective authority decision declaring either
(a) the Route-A primitive covariance `C_A` including `η`, `a`, `η(T)`, `v`, `Δx` and the
detector scale, with the synthetic generator extended to realise it; or (b) Route B, with
its own declared covariance. **Not repaired in this task.**

---

## 13. Route A versus Route B — information needed

Apparatus characterisation is **not in the repository**. This table states what must be
supplied; it does not choose.

| dimension | Route A — Stokes / force–displacement | Route B — independent active force |
|---|---|---|
| absolute stiffness uncertainty | depends on `σ_η`, `σ_a`, `σ_v`, `σ_Δx` — **all UNKNOWN** | depends on force-calibration traceability — **UNKNOWN** |
| field-specific stiffness uncertainty | `σ_Δx` per field + `η(T)` model error on `θ3` — **UNKNOWN** | **UNKNOWN** |
| temperature dependence | **enters through `η(T)`**, undeclared; couples the `θ3` arm to the drag model | enters only through `k_B T` normalisation; no drag coupling |
| x/y anisotropy | requires drag isotropy (A2) and two-axis displacement readout | requires two-axis force calibration — **UNKNOWN** |
| rotation measurement | `σ_psi_deg = 0.5°` declared as a HYPOTHETICAL scenario | **UNKNOWN** |
| common-mode scale uncertainty | `σ_cm = 1.15%` declared as HYPOTHETICAL; would need the `η`,`a` terms added | **UNKNOWN** |
| apparatus requirements | flow cell / stage with calibrated velocity; known `η`, `a` | traceable force actuator and readout — **UNKNOWN** |
| independence from Branch-B equilibrium statistics | satisfied — reads a driven displacement, not the passive histogram | satisfied |
| reuses existing E1a-v4 work | yes, substantially | estimator and endpoints yes; Branch-A model no |

**No route is recommended here.** The only asymmetry the repository supports is §11.3: Route
A couples the temperature arm to an undeclared viscosity model, and Route B as described
would not.

---

## 14. β sensitivity — the basis for a new uncertainty budget

With `β = d/q`, `q = tr(HΣ)`:

```
dlog β = −dq/q ,      dq = tr(Σ dH) + tr(H dΣ)
```

At the truth `Σ = β⁻¹H⁻¹`, so `q = d/β` and

```
dlog β = −(1/d) tr(H⁻¹ dH)  −  (β/d) tr(H dΣ)
```

*Check:* a pure scale error `dH = εH` gives `tr(H⁻¹εH) = εd`, hence `dlog β = −ε`, matching
`β̂ = β/c` exactly (§10).

**Variance.** With Branch A and Branch B independent, the cross term vanishes:

```
Var(log β̂) = (1/d²) Var[tr(H⁻¹dH)]  +  (β²/d²) Var[tr(H dΣ)]
                  Branch-A term              Branch-B term
```

- The **Branch-A term** must be computed from the full `C_H ≈ J_g C_A J_gᵀ` of §11, with
  correlations *inside* Branch A retained — `η` and `a` are shared across all fields and
  across both modes, so their contributions are perfectly correlated and belong in `c`, not
  in independent per-field terms.
- The **Branch-B term** is `σ_stat²` of §6.
- The **cross term is zero only under branch independence**, which §11.4 shows is violated
  by a shared detector scale. That term must be carried explicitly, not assumed away.

---

## 15. Sample-size design

Computed with the L2 likelihood SE and the declared `σ_fs`, `σ_cm`, at the planned
`dt = 1.2e−4 s` and the four declared fields. `theta0` is the reference, `theta2` the hardest
target.

| `N` | `T_total` (s) | SE(log β̂) θ0 | SE θ2 | P3 `h` | P2 `h_j` | ΔP3 | ΔP2 |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 50,000 | 6.0 | 5.707e−03 | 5.785e−03 | 0.02561 | 0.01729 | | |
| 100,000 | 12.0 | 4.036e−03 | 4.091e−03 | 0.02436 | 0.01312 | 4.89% | 24.12% |
| 200,000 | 24.0 | 2.854e−03 | 2.893e−03 | 0.02371 | 0.01043 | 2.67% | 20.53% |
| 500,000 | 60.0 | 1.805e−03 | 1.829e−03 | 0.02331 | 0.00840 | 1.68% | 19.38% |
| 1,000,000 | 120.0 | 1.276e−03 | 1.294e−03 | 0.02317 | 0.00761 | 0.58% | 9.42% |
| 2,000,000 | 240.0 | 9.024e−04 | 9.147e−04 | 0.02310 | 0.00718 | 0.29% | 5.63% |

```
margins:                   δ_abs = 0.05        δ_cross = 0.02
systematic-only floors:    P3 h = 0.02304      P2 h_j = 0.00673
```

**Reading.**

- **P3 is saturated everywhere.** Even at `N = 50,000` (6 s) `h = 0.0256` against
  `δ_abs = 0.05`, and the systematic floor is `0.02304`. Record length is not a design
  variable for the absolute test.
- **P2 binds.** `h_j` falls steeply to `N ≈ 5×10⁵` (19–24% per step), then flattens
  (9.4%, 5.6%). At `N = 2×10⁶` it is within 7% of the `σ_fs`-only floor.
- **Diminishing returns begin at `N ≈ 5×10⁵` and are essentially complete by `N ≈ 10⁶`.**
  Below `N ≈ 3×10⁵` the cross-field test is statistics-dominated; above it, `σ_fs`-dominated.

**`N` is not frozen here.** The purpose is the location of the knee, which is
`N ≈ 5×10⁵ – 10⁶` (60–120 s per field-replicate). `N = 2,000,000` is comfortable and
defensible but is **NOT ESTABLISHED as necessary**: moving from `10⁶` to `2×10⁶` doubles
every trajectory for a 5.6% improvement in the binding endpoint and 0.29% in the other.

---

## 16. Performance consequences

### 16.1 Counts from the frozen plan — known, not estimated

| case | R | sub | fields | artifacts | trajectories |
|---|---:|---:|---:|---:|---:|
| `C1_true_bridge_complete` | 300 | 4 | 4 | 4,800 | 4,800 |
| `C2_geometry_false_rejection` | 400 | 4 | 4 | 6,400 | 6,400 |
| `C3_g5_block` | 400 | 4 | 4 | 6,400 | 6,400 |
| `C4_surrogate_validity` | 2,000 | 1 | 4 | 8,000 | 8,000 |
| `C5_plug_in_branch_a` | 400 | 12 | 4 | 19,200 | 19,200 |
| `C6_mode_resolution_boundary` | 400 | 3 | 1 | 1,200 | 1,200 |
| `C7_false_bridge` | 400 | 4 | 4 | 0 | 6,400 |
| `C8_blinded_scale_control` | 200 | 1 | 4 | 0 | 800 |
| **total** | | | | **46,000** | **53,200** |

```
R_cal = 50,000 draws x 4 gates x 8 bytes      = 1.60 MB raw per artifact
all artifacts raw                             = 73.6 GB   (plan: "about 74 GB", streamed)
trajectory steps at N = 2e6                   = 1.064e11
trajectory steps at N = 5e5                   = 2.660e10   (4x fewer)
```

### 16.2 Runtime — measured versus projected

The plan is explicit that only per-unit costs were measured:

```
MEASURED      one artifact build: 2.674 s wall median, 5 reps, spread 2.616-2.698 s
              of which 2.645 s surrogate draws + four gates, 0.057 s threshold finalisation
PROJECTION    46,000 x 2.674 s = 123,004 core-seconds = 34.2 core-hours
              (recomputed here: 34.17 core-hours)
NOT MEASURED  Branch-B trajectory generation -- the plan states it is
              "excluded from these figures entirely and is the larger term"
```

> **Plan-internal inconsistency, recorded not repaired.**
> `campaign_projection.architecture_B...repaired_core_hours = 34.2` carries the note
> "supersedes the 29.7 core-hour figure, which rested on the incorrect 40,000 count", yet
> `what_the_headline_numbers_actually_contain.corrected_projection.replicate_conditional_core_hours`
> still reads `29.7` — which is `40,000 × 2.674 / 3600 = 29.71`, the superseded count.
> Cosmetic; no scientific consequence; not a defect requiring action in this task.

### 16.3 Comparison

| | current path | direct path with exact likelihood |
|---|---|---|
| primary null | Monte Carlo, per replicate at realised `H_A` | analytic LRT, asymptotic `χ²` + finite-`N` check |
| calibration artifacts | **46,000** | **0** |
| artifact storage (raw) | 73.6 GB | 0 |
| artifact build cost | 34.2 core-hours (PROJECTION from a MEASURED unit cost) | 0 |
| `C4` surrogate-validity case | 8,000 artifacts + 8,000 trajectories | **eliminated** — the object it validates no longer exists |
| trajectories | 53,200 | fewer: the minimal suite of §17, at `N ≈ 5×10⁵–10⁶` |
| trajectory steps | 1.064e11 | ~`10⁹`–`10¹⁰` depending on the suite and `N` |
| provenance machinery | `CalibrationCondition`, locks, ledger, reuse rules, lock recovery and reconciliation | **none of it** — nothing per-replicate to identify, lock or recover |
| per-fit cost | — | one VAR(1) fit per record; **NOT MEASURED** |

**Honest separation.** The **count** reductions (46,000 → 0 artifacts; 73.6 GB → 0; `C4`
eliminated) are known from the frozen plan. The **wall-clock** improvement is **NOT
MEASURED**: the cost of a VAR(1) profile fit in this pure-Python environment has not been
benchmarked, and trajectory generation — the dominant term under either path — was never
measured at all. No speed-up factor is claimed.

---

## 17. Validation that remains necessary

**Exact likelihood does not mean no validation.**

| id | purpose | how it can be validated |
|---|---|---|
| **V0** | `β = 1` baseline recovery | small synthetic OU; also partly **analytic** (the estimator is unbiased to `O(1/N)` by §2.2) |
| **V1** | stiffness changed, `β = 1` | small synthetic |
| **V2** | rotated anisotropy, `β = 1` | small synthetic — the only test that separates geometry from scalar variance |
| **V3** | temperature changed, `β = 1` | small synthetic; **cannot test the `η(T)` systematic of §11.3 until F4 declares it** |
| **V4** | hidden Branch-A scale `c`, expect `β = 1/c` | **ANALYTIC — already proved exactly in §10**, no simulation needed for correctness; a small run confirms the implementation |
| **V5** | deliberate geometry mismatch must be detected | small synthetic; power, not size |
| **V6** | strong temporal correlation | small synthetic at large `φ`; this is where the asymptotic `χ²` is most strained |
| **V7** | Branch-A uncertainty propagation / common-mode perturbation | **analytic** via §14 for the first-order budget; synthetic for the finite-sample check |

**Mapping of the current cases:**

| case | status under the redesigned primary path |
|---|---|
| `C2` geometry false-rejection | **STILL NECESSARY** — achieved size of the LRT at finite `N` with correlation |
| `C5` plug-in Branch-A | **STILL NECESSARY** — design §12.1 item 3; representation-independent |
| `C7` false bridge | **STILL NECESSARY** — negative control |
| `C8` blinded scale | **REPLACED BY ANALYTICAL PROPERTY for correctness** (§10 is exact), retained as an implementation check |
| `C3` G5 / non-Gaussianity | **PROMOTED** — under `p ∝ e^{−βV}` the Gaussian form is an assumption, so non-Gaussianity becomes a primary falsifier rather than a side gate |
| `C6` mode resolution | **CHANGES FORM** — becomes conditioning of `H^{1/2}` near degeneracy, not a principal-angle blocking rule |
| `C4` surrogate validity | **OBSOLETE** — validates the surrogate, which no longer exists |
| `C1` complete pipeline ≥ 0.90 | **SECONDARY** — an operating-characteristic release claim, not needed for a first scientific result |

**`C1–C8` are not deleted.** They remain the Track-V specification.

---

## 18. Achieved size must still be demonstrated

Replacing Monte-Carlo calibration removes the *artifact*, not the *obligation*. Under the
redesigned path the LRT null is asymptotically `χ²` with the degrees of freedom of §7, but
that is an asymptotic result and the following can break it:

```
finite N with strong temporal correlation (phi near 1)
model misspecification: non-scalar drag (A2), inertia (A1), observation noise (A7)
boundary effects: beta > 0 is an interior constraint, but Q > 0 is not
the plug-in H_A rather than H_true (design 12.1 item 3)
```

**Recommended minimum defensible method:** a **parametric bootstrap** under the fitted null,
at a small predeclared number of replicates, per field, reporting the achieved rejection
rate against the nominal `α`. It uses the same generator the experiment assumes, needs no
surrogate, and produces a direct size estimate. Asymptotic theory alone is not sufficient and
should not be presented as such.

**Not implemented here.** Its replicate count is a later decision (§21).

---

## 19. Topology interface — mathematical layer

**Authoritative notation.** The foundation does **not** use an incidence-matrix formulation.
Its canonical statements are foundation §3

```
μ(x;θ) = ∇_x V(x;θ)
E(x_pre → x_post | θ) = V(x_pre;θ) − V(x_post;θ)
```

and foundation §12, the refinement/telescoping theorem for any state function `V`:

```
E(x → x+Δ₁+Δ₂) = E(x → x+Δ₁) + E(x+Δ₁ → x+Δ₁+Δ₂)
```

which the foundation states "holds **solely** because `E` is a state-function difference".
The foundation also records the companion warning that **same-base summation is a different
construction and generally fails**: for quadratic `V`,
`E(x,Δ₁+Δ₂) − E(x,Δ₁) − E(x,Δ₂) = −Δ₁ᵀHΔ₂`.

**Incidence representation.** On a finite set of states with potentials
`v = (V_1,…,V_n)ᵀ` and an oriented incidence matrix `D` (row per edge, `+1` at the pre-state,
`−1` at the post-state), the edge values are

```
e = D v
```

This is a *representation* of foundation §3 on a finite state set, not a new definition.
Telescoping follows immediately: `e` is a coboundary of `v`, so the sum along any path
depends only on its endpoints, and `D` applied to a closed cycle gives zero. This reproduces
foundation §12 and nothing more.

> **Pure mathematical topology does not depend on the choice of `β` estimator, on the
> Branch-A route, or on any experimental outcome.** It depends only on `V` being a
> single-valued state function. No bridge result can falsify it.

**Not verified against the topology/motif programme.** There are no `docs/*topolog*` sources;
the topology material lives in the book series, which this task did not audit. The statements
above are taken from the **physical foundation**, which is authoritative, and the mapping to
the books' notation is **NOT VERIFIED**.

---

## 20. Topology error propagation

With node-potential covariance `C_V`, edge values `e = Dv` have

```
C_E = D C_V Dᵀ
```

For a single edge `E_ij = V_i − V_j`:

```
Var(E_ij) = Var(V_i) + Var(V_j) − 2 Cov(V_i, V_j)
```

**Shared-node and shared-calibration errors must not be treated as independent.** Two
reasons, and they are different:

1. **Shared node.** For a path `A → B → C`, `E_AC = E_AB + E_BC = (V_A − V_B) + (V_B − V_C)
   = V_A − V_C`. The intermediate potential cancels **deterministically**, before any
   variance is taken. So
   `Var(E_AC) = Var(V_A) + Var(V_C) − 2Cov(V_A, V_C)` with **no contribution from `V_B` at
   all**. Treating `E_AB` and `E_BC` as independent and adding their variances
   double-counts `Var(V_B)` and **overstates** the uncertainty.
2. **Shared calibration.** Every `V_i` in one field is divided by the same `k_B T_θ` and
   carries the same Branch-A scale error. That induces a rank-one, perfectly correlated
   component in `C_V`. In a *difference* a common additive offset cancels; a common
   *multiplicative* scale does **not** — see §21.

---

## 21. Common scale versus field-dependent scale

If a single field's measured potential is rescaled, `V^meas = c V`, then for every edge

```
E^meas = V_i^meas − V_j^meas = c (V_i − V_j) = c E
```

so **all** EBU values scale by `c`. Path identities, telescoping and every ratio of edge
values are preserved exactly; only the physical denomination changes. A common scale error
is therefore *harmless to topology and fatal to absolute denomination* — which is precisely
the M1 outcome of §7.

If different fields require different `c_θ` (equivalently different `β_θ`), then

```
E_θ0^meas = c_θ0 E_θ0        E_θ1^meas = c_θ1 E_θ1        c_θ0 ≠ c_θ1
```

and `E_θ0^meas + E_θ1^meas` is a sum of quantities in **two different units**. Fixed-field
topology remains valid; cross-field accumulation requires an explicit conversion that the
experiment has not supplied. That is the M2 outcome, and it is exactly what the four-field
bridge test exists to detect.

**Provisional classification** (§25 of the brief), consistent with the foundation but
**NOT verified against the topology source material and NOT promoted to authority**:

```
T0  mathematical topology            no physical beta evidence required
T1  fixed-field physical topology    requires a valid physical potential within one field
T2  cross-field physical topology    requires cross-field beta commensurability evidence
```

---

## 22. Field-changing systems remain future work

For a field-dependent potential `V(x,θ)`,

```
dV = ∇_x V · dx  +  (∂V/∂θ) dθ
```

separating state change inside a field from change of the field itself. **This task does not
solve it.** The four-field equilibrium benchmark uses **separately equilibrated** fields
(set field → equilibrate → measure → next field) and establishes nothing about continuously
changing fields, where `p(x,t)` need not equal the instantaneous Boltzmann distribution and
assumption A4 fails.

---

## 23. Proposed minimum experiment

**Conceptual proposal only. Not authority.**

```
fields                4 -- theta0 baseline, theta1 stiffness, theta2 ellipse+rotation,
                      theta3 temperature. None is interchangeable: theta1 is the only
                      pure-tau arm, theta2 the only geometry arm, theta3 the only
                      normalisation arm.

Branch A              H_theta and T_theta per field, by one declared route with a
                      DECLARED primitive covariance C_A (section 11). eta and a are NOT
                      required by the estimator under L2; they are required by Route A
                      for H_U itself.

Branch B              passive equilibrium positions, one record per field-replicate,
                      N in the 5e5 - 1e6 region (section 15). Never used to inform H.

primary beta          profile-likelihood interval for log beta_theta from the exact
                      OU likelihood, L2 parameterisation, conditional MLE
                      beta_hat(F) = N d / R(F).

absolute endpoint     M0 vs M1 equivalence at delta_abs, conjunctive over 4 fields.

cross-field endpoint  M1 vs M2 equivalence at delta_cross, conjunctive over the
                      3 comparisons to the reference field.

geometry endpoint     M2 vs M3 LRT per field, df = 2, at alpha_geom -- a rejection test.

positive control      hidden Branch-A scale c; expected beta = 1/c, EXACT by section 10.

uncertainty model     log beta_hat = log beta - c - f_theta + eps_theta, with the
                      Branch-A terms from C_A via C_H = J C_A J^T, the cross-branch
                      detector term carried explicitly, and eps from section 6.

pre-execution         V0-V7 of section 17 plus a parametric-bootstrap size study
validation            (section 18). Not C1-C8; not 46,000 artifacts.
```

---

## 24. Decision table

| | CURRENT E1a-v4 | DIRECT BRIDGE + current MC null | DIRECT BRIDGE + exact OU likelihood |
|---|---|---|---|
| scientific target | `K = βH` | `p ∝ e^{−βV}`, Gaussian form | `p ∝ e^{−βV}`, Gaussian form |
| `β` estimator | `m/tr(H_A S)` | **identical** | identical point estimate; profile interval |
| temporal correlation | `N_ab(φ)` from Branch-A `τ` | same | `F` as Branch-B nuisance (L2) |
| absolute error | `σ_cm ⊕ σ_fs ⊕ σ_stat` | same | same — **`σ_cm` floor unchanged** |
| cross-field error | `2σ_fs² + σ_stat²`, `σ_cm` cancels | same | same |
| geometry diagnostic | G1–G5, two-block union | `S_z = I`, reduced resolution | M2-vs-M3 LRT, `df = 2`/field |
| Monte-Carlo calibration | required | required | **not required for the primary null** |
| artifacts | 46,000 (73.6 GB) | 46,000 | **0** |
| provenance complexity | condition identity, locks, ledger, recovery | same | **none per-replicate** |
| sample requirement | `N = 2e6` declared | same | knee at `5e5–1e6`, **not frozen** |
| non-Gaussian extensibility | none | native in principle | native |
| topology compatibility | full | full | full — §19 is estimator-independent |
| main unresolved risk | Route-A error model (§12); C7/C8 defect | same, plus no simplification gained | **finite-`N` size of the LRT (§18)** and the same Route-A gap |

---

## 25. Required yes/no conclusions

```
Q1   DIRECT BOLTZMANN BRIDGE EQUIVALENT TO CURRENT GAUSSIAN BETA TARGET?
     CONDITIONAL -- exactly equivalent for harmonic V; strictly stronger for anharmonic V.

Q2   IS THE WHITENED-COVARIANCE BETA ESTIMATOR NEW?
     NO -- d/tr(S_z) = m/tr(H_A S), verified bit-exactly.

Q3   CAN AN EXACT OU LIKELIHOOD REPLACE THE CURRENT MONTE-CARLO-CALIBRATED PRIMARY NULL?
     CONDITIONAL -- yes for the Gaussian benchmark under A1-A7, conditional on a
     finite-N achieved-size study (section 18) and on A2/A7 being declared or tested.

Q4   DOES THIS REMOVE THE NEED FOR 46,000 CALIBRATION ARTIFACTS?
     YES for the primary null -- the per-replicate artifact disappears entirely, with
     CalibrationCondition, locks, ledger and lock recovery. A far smaller predeclared
     size study replaces it.

Q5   DOES IT REMOVE THE NEED TO VERIFY ACHIEVED TEST SIZE?
     NO.

Q6   IS THE CURRENT SYNTHETIC BRANCH-A ERROR MODEL ADEQUATE FOR REAL ROUTE A?
     NO.

Q7   IS THE ABSOLUTE BETA=1 CLAIM CURRENTLY SYSTEMATICS-LIMITED?
     YES -- sigma_cm is 95.17% of the P3 variance at N = 2e6, and beta is exactly
     confounded with a common Branch-A scale error.

Q8   IS THE CROSS-FIELD COMPARISON LIMITED BY THE SAME COMPONENTS AS THE ABSOLUTE TEST?
     NO -- sigma_cm cancels exactly. Cross-field is statistics-dominated below
     N ~ 3e5 and sigma_fs-dominated above it.

Q9   IS N = 2,000,000 JUSTIFIED AS NECESSARY?
     NOT ESTABLISHED -- the knee is at N ~ 5e5-1e6; 1e6 -> 2e6 buys 5.63% on the
     binding endpoint and 0.29% on the other.

Q10  CAN PURE MATHEMATICAL TOPOLOGY TESTS CONTINUE INDEPENDENTLY?
     YES from the physical foundation (sections 3 and 12); NOT VERIFIED against the
     book-series topology material, which was not audited.

Q11  SHOULD CROSS-FIELD PHYSICAL TOPOLOGY WAIT FOR THE BRIDGE RESULT?
     YES -- T2 in section 21. Fixed-field (T1) and mathematical (T0) need not.

Q12  IS IMPLEMENTATION OF THE NEW DESIGN READY TO BEGIN?
     NO.
```

---

## 26. Human decisions required

Separated by kind. **Mathematical conclusions are not listed as decisions.**

**Settled by mathematics or existing authority — NOT decisions:**

```
the estimator identity (section 2.2)
beta_hat = beta/c confounding (section 10)
the nested-model dof structure (section 7)
L2 over L1 (section 4.3 -- arithmetic, not taste)
that achieved size must still be demonstrated (section 18)
that pure mathematical topology is unaffected (section 19)
```

**SCIENTIFIC-POLICY decisions (human, prospective, before any implementation):**

```
D1  Whether to adopt the direct-bridge formulation at all, and if so whether with the
    exact OU likelihood (the only variant that simplifies anything).
D2  The accepted absolute-calibration uncertainty. sigma_cm = 1.15% caps the absolute
    claim at +/-2.25% regardless of N. Is that the claim the programme wants to make?
D3  Whether delta_abs = 5% and delta_cross = 2% survive once the Route-A drag terms of
    section 11.5 are declared. Not evaluable until F4 closes.
D4  Which diagnostics remain release-bearing: in particular whether C3/non-Gaussianity
    is promoted to a primary falsifier (section 17).
D5  Whether assumption A2 (scalar drag) is declared, or left testable by not constraining F.
```

**APPARATUS-DEPENDENT decisions (need experimental input this repository lacks):**

```
D6  Branch-A route: A or B. The only repository-supported asymmetry is section 11.3.
D7  The primitive covariance C_A -- every entry in section 11.5 is UNDECLARED.
D8  Whether observation noise (A7) is negligible at the declared dt and N.
```

**IMPLEMENTATION choices (not scientific decisions):**

```
D9   Final N, once D2/D3 fix the targets. The knee is at 5e5-1e6.
D10  Parametric-bootstrap replicate count for the size study.
D11  Whether F is parameterised as a full matrix or constrained symmetric.
```

---

## 27. Conflicts with existing authority

Identified, **not resolved, not silently rewritten**:

| # | conflict | nature |
|---|---|---|
| 1 | Design §5 fixes five gates `G1–G5` with a two-block union bound and `α_1 + α_2 = 0.005`. The redesign's per-field `df = 2` LRT is a different statistic with a different allocation. | Would require a prospective design amendment. The redesign is **not** a reinterpretation of §5. |
| 2 | Plan `calibration.*` specifies the surrogate generator, `R_cal = 50,000`, artifact schema and `REPLICATE_CONDITIONAL` scope. The direct path makes all of it inapplicable. | Would require a prospective plan amendment, not deletion. |
| 3 | Contract `relaxation_time_rule` makes `τ_r = γ/k_r` with `γ = 6πηa` a declared Branch-A quantity. Under L2 the temporal law is a Branch-B nuisance instead. | Not a contradiction — `τ` remains the physical truth — but the *inferential role* changes and must be stated. |
| 4 | Design §2.1 authorises Route A, whose declared uncertainty budget is incomplete (§11.5, §12). | A defect in the current authority, independent of the redesign. |

---

## 28. State and integrity

Identities recomputed independently; reports are outside every preimage:

```
contract   d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4   UNCHANGED
design     25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6   UNCHANGED
foundation 6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507   UNCHANGED
baseline   0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa   UNCHANGED
plan       fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4   UNCHANGED
seed map   c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af   UNCHANGED
analysis   60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527   UNCHANGED
execution  442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b   UNCHANGED
```

```
4,002 checks, 0 failures, 17 suites, 0 not clean ; static preflight PASSED
OFFICIAL CAMPAIGN NOT RUN       SCIENTIFIC RNG DRAWS   0
OFFICIAL RESULTS  NONE          OFFICIAL TRAJECTORIES  0
EXECUTION SEAL    NOT FROZEN    CALIBRATION EXECUTIONS 0
EXECUTION AUTHORISED  FALSE     CAMPAIGN JOBS          0
```

`results/e1a_v4_validation` does not exist. E1a-v4 remains PRESERVED and PAUSED. This
report is **not** an authority amendment and authorises nothing.
