# EBU T-stage — minimal E1a equilibrium experiment design

- **STATUS:** NON-CONTROLLING T-STAGE EXPERIMENT DESIGN
- **R:** CLEARED
- **S:** INDEPENDENTLY CLEARED (S9 clearance supplied in the task)
- **T1–T11:** DESIGN COMPLETE, subject to T12 review and the qualification gates below
- **T12:** INDEPENDENT AUDIT REQUIRED
- **E1a:** PRESERVED / PAUSED
- **AUTHORITY:** UNCHANGED
- **IMPLEMENTATION:** NEW DESIGN NOT IMPLEMENTED; existing v4 implementation preserved
- **EXECUTION:** NOT AUTHORISED

Prepared on 2026-10-05. Starting commit:
`0fad60bfb8df919df24227756f8ef03480dad2e3`, branch
`codex/book-one-continuity`. This report is the only repository change.
“Complete” describes a prospective scientific design, not apparatus qualification,
achieved test size, demonstrated power, or permission to run an experiment.

## 1. Executive result

The proposed experiment compares an independently measured mechanical energy landscape
with an independently observed probability distribution. Its primary hypothesis is

\[
p_\theta(x)=Z_\theta(\beta_\theta)^{-1}
             \exp[-\beta_\theta V_{A,\theta}(x)],\qquad
V_{A,\theta}=\frac{U_{A,\theta}(x)-U_{A,\theta}(x^*_{A,\theta})}{k_BT_\theta}.
\tag{T.1}
\]

The prediction is **one at every field**, not merely the same fitted number at every
field. The first realization deliberately uses a two-dimensional harmonic trap. This
makes normalization analytic and lets one test the direct density model without
estimating a logarithm of a histogram. It does not make Gaussianity a premise of the
general equilibrium theorem.

The selected inference is a **stationary Gaussian state-space likelihood**, with an
independently calibrated observation model and freely estimated temporal nuisance
parameters. Reversibility is not imposed on that density fit. An independent, mandatory
reversibility assessment prevents a stationary circulating Gaussian from being called
equilibrium. Shape and centre agreement are mandatory because a scalar energy average
alone cannot establish the landscape correspondence.

There are four fields and **two separately prepared physical calibration blocks**: eight
records, eight absolute scale comparisons, and six reference-field contrasts. No
hierarchical population claim is made. The statistical design target for each record is
**450,000 independent quadratic-observation equivalents**, or conditional efficient
information at least **408,164 for log beta**. These are information targets, not a claim
that recorded frames are independent. The frame-count and duration rule is fixed in
§22; physical relaxation times, noise and shutter response instantiate it in U-stage.

The retained scientific margins are 5% absolute and 2% cross-field, expressed by the
slightly conservative reciprocal-symmetric bands `[1/1.05, 1.05]` and
`[1/1.02, 1.02]`. Agreement requires complete confidence intervals inside the bands.
Measurement qualification requires total calibration standard uncertainties no greater
than 0.9% in an absolute log scale and 0.30% in each within-block log contrast, together
with the other explicit qualification conditions below. These are required capabilities,
**not measured capabilities**. The old hypothetical 1.15% common error does not satisfy
the new sufficient absolute-error specification.

This design removes the five-statistic geometry minimum-p surrogate as the primary
architecture. It does **not** remove finite-sample validation. The normal planning
calculation gives a conservative scale-endpoint failure sum of approximately 0.03341;
the full experiment still has to demonstrate at least 0.90 unconditional complete-pass
probability in V-stage. No trajectory, random draw, apparatus calibration, or campaign
was run to obtain this report.

For EBU this tests the physical ruler used to compare potential changes across these
fields. A successful result would support that ruler in this controlled benchmark. It
would not establish economic efficiency, social welfare, ecological benefit, or any
incentive mechanism; those are different scientific questions.

## 2. Authority and provenance

### 2.1 Source order and scope

The frozen foundation outranks the working baseline; both outrank exploratory reports.
The foundation and baseline, followed by R, S-MG and S, were read in this conversation;
their unchanged bytes were reverified for this stage. The relevant current E1a documents,
JSON bindings, field definitions, decision rules, seed map, Branch-A measurement code,
generator, identity recipes and paused/redesign records were inspected directly. No
scientific module was imported to perform these inspections.

| Source | Role in this report |
|---|---|
| `AGENTS.md` | Static-only stage, provenance, exact change boundary and no later-stage execution |
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` and metadata | Frozen definitions and authority |
| `docs/theory/EBU_THEORY_BASELINE.md` | Working theory and E1a frontier; §14.3 sign defect retained as a documented defect |
| `docs/theory/EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md` | Cleared R-stage semantic repair |
| `docs/theory/EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md` | Cleared finite-change/generator theory; not a new experimental assumption |
| `docs/theory/EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md` | S1–S8 theorem artifact, commit `0fad60bfb8df919df24227756f8ef03480dad2e3` |
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md`, `e1a_v4_design_contract.json` | Existing controlling prospective E1a pair, preserved |
| `docs/e1a/E1A_V4_SYNTHETIC_VALIDATION_PLAN.md`, corresponding JSON, seed map and seal | Preserved historical/current operational bindings, not adapted here |
| `docs/e1a/E1A_V4_PROGRAMME_PAUSE_RECORD.md` | Current programme pause; stale “not started” fields in older sources do not erase intervening work |
| `docs/e1a/E1A_BRIDGE_REDESIGN_BOUNDED_ANALYSIS.md` | Prior analysis; useful findings and claims requiring correction |
| `docs/e1a/E1A_MINIMAL_DIRECT_BRIDGE_TECHNICAL_DESIGN.md` | Previous non-controlling design; the eight specific defects are disposed in §27 |
| `docs/e1a/E1A_V4_REPORT.md` | Historical derivations, with later authority overriding its calibration and finite-bath defects |
| `e1a_v4/{branch_a,geometry,effective_size,endpoints,world,identity}.py` and relevant `validation/` sources | Existing calculation, data separation and identity construction; inspected, not executed |

The supplied T-stage brief explicitly reports independent S9 clearance. This report
uses that authorization; it does not manufacture an auditor's report or edit the earlier
S artifact's pending-audit header. Likewise, T12 is not performed or claimed here.

### 2.2 Physical and statistical precedent

The methods are established statistical mechanics and inference, not claimed as new
physical laws. Primary methodological sources checked for this design include:

- Schuirmann (1987), [two one-sided equivalence tests](https://pubmed.ncbi.nlm.nih.gov/3450848/),
  for positive equivalence rather than accepting an unrejected point null.
- Berger and Boos (1994), [maximizing p-values over a nuisance confidence set](https://doi.org/10.1080/01621459.1994.10476836),
  for accounting for nuisance uncertainty rather than treating a fitted null as known.
- Berglund (2010), [camera measurement, localization error and motion blur](https://www.nist.gov/publications/statistics-camera-based-single-particle-tracking),
  and Calderon, [motion-blur likelihood for confined trajectories](https://arxiv.org/abs/1510.06062).
  These motivate explicit observation modelling; no claim that their free-diffusion
  formulas automatically apply to this trap is made.
- Godrèche and Luck (2018), [irreversibility of multivariate OU processes](https://arxiv.org/abs/1807.00694),
  as precedent for separating stationary Gaussian density from detailed balance.

The equations below specify this experiment independently; numerical design values are
our prospective choices or inherited margins, not apparatus facts taken from those papers.

## 3. Scientific objective

The narrow question is whether, for each specified stationary passive trap configuration,
the physical thermal normalization and the observed configurational probability assign
the same dimensionless slope, within declared resolution. The three necessary checks are:

1. absolute slope near one at every field and preparation;
2. the same denomination relative to the reference within each preparation;
3. a compatible full Gaussian landscape, centre and equilibrium path law in the observed plane.

A common slope of 0.7 fails the first check even if every cross-field comparison passes.
A trace-correct covariance with the wrong shape fails the third. A Gaussian density with
a persistent rotational current fails the equilibrium part of the third. These are
scientifically different outcomes and will remain distinguishable in the report.

A benchmark success confirms an already predicted correspondence under its conditions.
It does not identify a unique microscopic theory, prove a universal EBU law, or test
all potentials, reservoirs, coordinates and coarse-grainings.

## 4. Cleared theorem handoff

S1–S4 establish the canonical density on its declared support and reference measure,
normalizability, the thermal denominator and the direct identity

\[
J_{\rm prob}(x):=-\log[p(x)/p(x^*)]=V(x),\qquad \beta_{\rm bridge}=1.
\tag{T.2}
\]

The slope is identifiable only for a nonconstant potential. Here positive curvature on
a two-dimensional observed space provides that condition. S5 establishes that the
result is not restricted to quadratic potentials. For twice differentiable densities,
`K = beta H` is a derivative consequence; equality of Hessians at a point does not
establish the whole density, and global equality of Hessians leaves an affine ambiguity.

S6 supplies the special case actually used here: a quadratic potential on a full affine
space, Lebesgue reference measure, positive-definite restricted Hessian and no material
truncation imply `Sigma = beta^{-1} H^{-1}`. S7 supplies the no-work entropy signs and
conditions, separately from density agreement. S8 explains why thermal denomination is
the same mathematical unit at different fields without saying that every physical
transition has an unchanged numerical value.

R and S-MG remain upstream cleared dependencies. Telescoping fixed-potential increments,
finite-difference/Möbius identities and generator bookkeeping do not wait on E1a.
Conversely, their algebra cannot prove that an observed probability law is canonical.

## 5. Baseline sign convention

Use ordinary post-minus-pre differences throughout:

\[
E_{\rm EBU}=V(x_{\rm pre})-V(x_{\rm post}),\qquad
\Delta J_{\rm prob}=J_{\rm post}-J_{\rm pre}=-E_{\rm EBU}.
\tag{T.3}
\]

For a no-work conservative overdamped transition at one fixed temperature,
`q_to_medium = k_B T E_EBU`, `Delta s_medium = +k_B E_EBU`,
`Delta s_system = -k_B E_EBU`, and `Delta s_total = 0` under the S7 conditions.
The separately defined constrained-macrostate entropy relation retains its finite-bath
remainder in `C_V`. It is not total stochastic entropy production.

The positive `Delta J` form in baseline §14.3 is a known documentary defect under this
ordinary difference convention. It is **non-blocking for T and must be repaired before
W-stage adoption**. This task neither repairs nor silently reinterprets the baseline.

## 6. Branch independence architecture

### 6.1 Three packets and one comparison

**A packet, locked before B is unblinded:** field ID, preparation/block ID, mechanical
force-displacement records, the physical force model, `eta(T)`, bead radius, independent
thermometry, `H_U`, `H=H_U/(k_B T)`, independently established centre `x_A*`, axis and
pixel calibration, full primitive covariance and bounded systematics, calibration
provenance and validity range. Include independently measured instrument noise,
shutter/response kernel and timing provenance in a separately identified observation
subpacket. Include the acquisition-time qualification, without estimating stiffness
from equilibrium fluctuations.

**B packet:** timestamped detector data, frozen tracking and coordinate conversion,
missing-frame and saturation flags, acquisition metadata, reference-channel drift
records, retained-frame mask, and a free Gaussian state-space characterization
`(mu_B, Sigma_B, A_B)` with uncertainty. This characterization receives the common
coordinate/observation calibration but no energy Hessian or predicted beta. It must
not use `H_A` to choose axes, remove outliers, choose a time window or define a covariance.

**Comparison packet after both locks:** frozen A and B hashes; the direct bridge-family
likelihood evaluated on B; free-density shape/centre comparisons; all uncertainty
propagation; scale, geometry and equilibrium verdicts; controls; and the final reasoned
classification. Evaluating `p(y | beta, H_A)` here is the intended comparison, not a
Branch-B reconstruction secretly conditioned on `H_A`.

Measurement errors may be correlated through a shared coordinate calibration. Branch
independence means independent scientific information and no outcome feedback, not an
unjustified assertion that every uncertainty is statistically independent.

### 6.2 Lock and acquisition order

Fix fields, block order, acquisition settings and all preprocessing rules; perform the
independent A/observation calibration; lock and hash that packet and the resulting
fixed acquisition duration; acquire B (or keep already independently acquired B
sealed); freeze B processing and its A-blind characterization; lock B; then unblind the
comparison. Hashes and provenance identify both shared and block-specific calibrations.

Forbidden A routes remain passive fluctuation-spectrum/corner-frequency calibration,
equipartition from B, `H := K_B`, and any fit of physical stiffness to the tested density.
Temporal parameters fitted to B in the comparison model describe its observed dynamics;
they never overwrite A's energy landscape or determine `k_B T`.

### 6.3 Preprocessing and failures

Freeze detector tracking, axis transform, time origin, shutter kernel, missing-data
policy, fixed burn-in, clipping rules and record length before the comparison. Retain
all valid scheduled measurements. Do not trim tails, recenter windows, detrend using
the bead's own path, or extend records until beta passes. Subtract only a separately
observed reference drift using a frozen transfer rule and propagated uncertainty.
Unexpected saturation, state-dependent loss, detector failure or calibration drift
makes the affected cell invalid; it is not replaced silently. Planned cells stay in
the denominator. A later replacement would require a new, separately authorized block.

## 7. Field architecture

Retain four physically distinct field roles, with the following existing values as
**prospective nominal targets**, not measured calibration results:

| Field | Stiffness eigenvalues (micro N/m) | T (K) | Orientation | Distinct purpose |
|---|---:|---:|---:|---|
| theta0_circular | 100, 100 | 298 | 0 degrees | Absolute reference and within-block comparison denominator |
| theta1_power | 210, 210 | 298 | 0 degrees | Change confinement/relaxation scale at fixed nominal geometry and temperature |
| theta2_ellipse | 150, 60 | 298 | 30 degrees | Unequal modes, coupling and orientation relative to independently calibrated physical axes |
| theta3_temperature | 100, 100 | 318 | 0 degrees | Test the thermal normalization; viscosity and physical force calibration must change consistently |

The temperature field is indispensable to this stated multi-field denomination question.
Keeping only three stiffness/geometry fields would not probe the temperature denominator.
Actual stiffness at 318 K must be measured, not assumed identical because the table
lists the same target. The power field is retained because a scale-dependent detector
or temporal error can evade a single circular setting. A circular field can detect
anisotropy; the ellipse adds a physically identifiable orientation comparison.

A smaller two-field experiment could answer a narrower scalar question, but would omit
one of the requested distinct falsifiers. No fifth field, anharmonic arm or factorial
interaction arm is added. U may qualify the listed targets or report inability; it may
not quietly substitute temperatures or tolerances. A necessary change returns to design
review before any B outcome exists.

## 8. T1 — direct bridge hypothesis and selected model

### 8.1 Density model

In the common calibrated lateral coordinates,

\[
V_A(x)=\tfrac12(x-x_A^*)^T H_A(x-x_A^*),\quad H_A\succ0,\quad d=2,
\]
\[
Z_A(\beta)=(2\pi/\beta)^{d/2}|H_A|^{-1/2}.
\tag{T.4}
\]

No unknown normalization constant is fitted. The scientific density null fixes the
centre at `x_A*` and covariance at `beta^{-1} H_A^{-1}`. For estimation the centre is
allowed as a nuisance `mu`, and its agreement with `x_A*` is separately required in
§11. Thus centre estimation is neither hidden nor free evidence for the null.

### 8.2 Temporal embedding and observation likelihood

Let the latent continuous process obey

\[
dX_t=-A(X_t-\mu)dt+L\,dW_t,\quad
\Sigma_\beta=\beta^{-1}H_A^{-1},\quad
LL^T=A\Sigma_\beta+\Sigma_\beta A^T\succ0.
\tag{T.5}
\]

Initialize with the stationary law. Fit `beta > 0`, `mu` and `A` within the independently
qualified temporal bandwidth and diffusion domain. In particular, **do not impose**
`A Sigma = Sigma A^T` in the primary density fit. The parameterization permits currents;
it is not named an equilibrium model until the separate equilibrium gate is satisfied.
The free B characterization replaces `Sigma_beta` by an unrestricted SPD `Sigma`.
This requires only a stationary linear Gaussian Markov description of the latent
benchmark, not knowledge of its friction from the B trajectory.

With noiseless instantaneous observations, `F = exp(-A Delta)` and
`Q = Sigma - F Sigma F^T` give the exact transition law. For the actual observation
model, integrate that latent process over the independently known shutter kernel and
add localization noise (§15). The resulting stacked observations have a multivariate
Gaussian law with mean vector `m(mu)` and covariance `C(beta,A; phi_obs)`. Its log
likelihood is

\[
\ell=-\tfrac12\{\log|C|+(y-m)^TC^{-1}(y-m)+nd\log(2\pi)\}.
\tag{T.6}
\]

A correct augmented-state innovations recursion is a computational factorization of
this same law. Exposure averaging generally correlates measurement and transition
errors; a filter that ignores that correlation is not this likelihood. No numerical
factorization or optimizer is implemented in T.

The conditional point estimator maximizes (T.6) with the **locked point calibration**.
Calibration errors are then propagated and included in the repeated-measurement
confidence procedure. Physical `H_A` is never refitted from B. All likelihood maxima,
boundary cases and optimizer failures must be reported, with failure to establish a
unique usable maximum classified as non-evaluable. Exact likelihood specification does
not imply a closed-form estimator, unbiasedness, or an exact chi-square likelihood-ratio
null distribution.

### 8.3 Why this choice is minimal

It uses every frame, represents the known noise mechanism, and gives scale, shape,
centre and temporal diagnostics from the same two-dimensional model. It avoids density
binning, a nonparametric log-density reconstruction, arbitrary thinning and a separate
four-statistic covariance surrogate. Its extra temporal parameters are necessary
nuisances; fitting them does not calibrate the physical potential. Reversibility remains
a testable property rather than an assumption that predetermines the conclusion.

The model has a real boundary: non-Markov hydrodynamic memory or unmodelled detector
filtering invalidates this chosen first realization. It is not cured by calling a
Gaussian covariance approximation exact. U must qualify the temporal window; V must
exercise the declared departures; an unsuccessful qualification returns the design for
revision.

## 9. T2 — absolute beta endpoint

Write `b_jr = log beta_jr`, for field `j` and preparation `r`. Set

\[
\delta_a=\log(1.05)=0.04879016417.
\tag{T.7}
\]

For each of the eight cells test the non-equivalence null
`b <= -delta_a OR b >= delta_a` against the interior. Construct lower and upper
confidence limits from one-sided tests of nominal level 0.025, with the finite-sample
procedure in §20 and bounded-error enlargement in §15. **Pass only if the entire
interval lies strictly inside `(-delta_a, delta_a)`.** Equality at a boundary is not a
pass. Exponentiated limits are reported alongside beta.

The 5% margin retains the existing programme's prospective tolerance. Reciprocal
symmetry makes an upward change and its inverse comparable on a multiplicative scale;
its lower endpoint is 0.95238095, slightly stricter than the former 0.95. It was not
derived as a necessary physical precision or selected from new outcomes. The theorem
predicts exact one; the experiment resolves a declared neighbourhood of it.

A two-sided point-null test of `beta=1` is optional descriptive output and cannot decide
success. A narrow interval excluding one but lying wholly within the tolerance passes
equivalence; a wide interval containing one does not. Every cell must pass; no common
beta is imposed before checking absolute agreement.

## 10. T3 — cross-field endpoint

Within each preparation use only the three preregistered reference contrasts

\[
c_{jr}=b_{jr}-b_{0r},\quad j=1,2,3,\qquad
\delta_c=\log(1.02)=0.01980262730.
\tag{T.8}
\]

All six confidence intervals must lie strictly inside `(-delta_c, delta_c)`, using the
same one-sided nominal 0.025 procedure. This is the retained 2% scientific margin with
the same conservative reciprocal interpretation. There is no all-pairs claim and no
pooled tolerance. A common 0.7 would give zero contrasts while failing §9.

For the complete covariance matrix `C_b`, a contrast has variance
`C_b[j,j] + C_b[0,0] - 2 C_b[j,0]`. Shared reference uncertainty is retained between
contrasts. A scalar common multiplicative error cancels exactly only if it enters every
field with exactly the same coefficient. Temperature-dependent viscosity, distinct
pixel maps, orientation effects and field-dependent calibration do not automatically
cancel. The derivative map in §16 determines what cancels.

## 11. T4 — geometry and centre endpoint

Use the latent covariance from the **unrestricted B density fit**, with observation
noise and blur accounted for. With `H_A = R^T R` (Cholesky, positive diagonal), form

\[
M=R\Sigma_B R^T,\quad
G=\left\|\log M-\frac{\log|M|}{d}I\right\|_{\rm op},\quad
m=\sqrt{(\mu_B-x_A^*)^TH_A(\mu_B-x_A^*)}.
\tag{T.9}
\]

Set `delta_G = log(1.05)` and `delta_m = 0.10` thermal coordinate units. Require a
calibrated one-sided 97.5% upper confidence bound for `G` below `delta_G`, and for `m`
below `delta_m`, in every cell. These are positive precision requirements, not a failure
to reject exact shape or centre equality. Their boundary laws are generally nonregular;
§20 calibrates them rather than invoking a generic Wilks degree of freedom.

`G=0` iff `Sigma_B` is a positive scalar multiple of `H_A^{-1}`. It therefore detects
relative mode strengths, anisotropy, off-diagonal coupling and, in the elliptical field,
orientation error. For example, `H=I` and `Sigma=diag(1.5,0.5)` give trace beta one but
`G=(log 3)/2`, decisively not zero. A pure rotation within an isotropic eigenspace changes
nothing physically and is not a geometry failure. No principal-angle estimate is
required where eigenvalues coincide.

These tolerances describe different coefficients of the Gaussian landscape. The 5%
shape tolerance permits each normalized covariance eigenvalue between `1/1.05` and
`1.05`; it does **not** promise the entire pointwise density is within 5% on unbounded
tails. Combining scale and shape bands can permit up to a factor `1.05^2` in a
directional precision. Centre agreement bounds a different, linear landscape error;
it does not follow from covariance agreement. Report all three resolutions explicitly.

For numerical qualification require the full 99.9% A uncertainty region to retain an
SPD Hessian with `kappa_2(H) <= 100` after a fixed scalar nondimensionalization; likewise
require an SPD latent covariance and a numerically supported fit. Use Cholesky solves
and symmetric eigenvalue/log calculations, not an ambient pseudoinverse or unstable
explicit matrix square root. Values near the boundary, failed factorization, or an
uncertainty region touching zero curvature are `INSUFFICIENT_GEOMETRY_CALIBRATION` or
`INVALID_MODEL`, not evidence against beta. A relative backward-error ceiling of
`1e-10` is the prospective numerical requirement for the normalized 2-by-2 operations.
Repeated positive eigenvalues do not make a square root ill-conditioned; approaching
zero eigenvalues does. The nominal condition numbers are 1, 1, 2.5 and 1.

## 12. T5 — equilibrium and reversibility gate

### 12.1 Physical and stationarity conditions

Every record requires a fixed conservative field during acquisition, one stable thermal
reservoir, no stage motion or feedback forcing, no omitted imposed work, and calibrated
spatial temperature uniformity. Temperature/reference-channel monitors must support
maximum within-record `|Delta log T| <= 0.001`; independently bounded changes of the
physical normalized curvature must be at most 0.002 in operator log scale. These are
qualification bounds, not corrections estimated by forcing B to look stationary.
Their residual effect enters the bounded-error allowance of §15; if that allowance
cannot cover it, the cell is invalid.

Use four fixed equal-duration quarters. In the unrestricted B model, assess all six
quarter-pair contrasts. Define one stationarity statistic as the maximum of (i) thermal
centre separation divided by 0.10 and (ii) affine-invariant covariance log distance
divided by `log(1.05)`. Require its calibrated 97.5% upper bound below one. Covariance
log distance for quarters `u,v` is the maximum absolute log generalized eigenvalue of
`(Sigma_u,Sigma_v)`. Model fit and residual checks additionally cover departures within
quarters (§18). Finite observations resolve these declared scales and windows; they do
not prove stationarity at every unobserved time.

Do not estimate a bead drift and subtract it to pass this gate. An independently measured
reference drift may be corrected only by the frozen rule, retaining its uncertainty.
Burn-in is fixed prospectively at **20 upper-bounded slow relaxation times**, after
thermal and mechanical setpoints have independently settled. Also require the qualified
initial displacement to be at most ten thermal units and a bounded initial second
moment; the residual mean contraction is then at most `10 exp(-20)` under the qualified
OU envelope. Longer thermal equilibration follows the instrument's independent settling
criterion, not the bead histogram. None of this justifies stationary initialization
before settling has occurred.

### 12.2 Detailed balance remains a separate property

For the free fitted density/dynamics let

\[
B=\Sigma^{-1/2}A\Sigma^{1/2},\quad
S=(B+B^T)/2\succ0,\quad \Omega=(B-B^T)/2,\quad
r_{\rm irr}=\|\Omega\|_{\rm op}/\lambda_{\min}(S).
\tag{T.10}
\]

In these whitened coordinates the stationary current is `-Omega z p(z)`.
Detailed balance holds iff `Omega=0`. The first benchmark requires a calibrated
one-sided 97.5% upper bound `r_irr < 0.02`: at most a 2% antisymmetric drift relative
to the slowest dissipative rate at the experiment's resolved bandwidth. This is a
prospective instrumental resolution, not an assertion of exactly zero entropy production
or a universal thermodynamic tolerance. It is chosen to resolve current contamination
at the same order as the tighter denomination comparison.

Fit the continuous-time generator within the independently qualified non-aliasing
bandwidth `||B||_2 Delta <= 0.2`. Cross-check observed versus fitted-model lag-covariance antisymmetry at lags
nearest `tau_slow/2`, `tau_slow`, and `2 tau_slow`, with their actual timestamps retained.
Raw lag antisymmetry is also reported as a current diagnostic. The model-residual lag
checks belong to the diagnostic family, not three extra equivalence endpoints.
Without a justified bandwidth/response envelope, a rapidly rotating aliased process
cannot be excluded and the equilibrium conclusion is unavailable. A Gaussian marginal
alone never supplies that envelope.

The counterexample `A=I+omega [[0,-1],[1,0]]`, `Sigma=I`, `LL^T=2I` preserves exactly
the canonical Gaussian at every omega. Its scale and geometry pass at population level,
but `r_irr=|omega|`; a sufficiently resolved omega above 0.02 fails equilibrium. This
control must appear in V.

### 12.3 Required interpretation

If density/scale/geometry pass but reversibility is contradicted, report
**DENSITY BRIDGE SUPPORTED WITHIN TOLERANCE; EQUILIBRIUM ANCHOR NOT ESTABLISHED — CURRENT DETECTED**.
If the current interval is too wide, replace the last phrase by **REVERSIBILITY
INCONCLUSIVE**. A thermal or stationarity failure receives its own reason. No such
outcome becomes an equilibrium success, and none by itself falsifies the general
canonical density theorem.

## 13. T6 — estimator comparison and finite-sample facts

### 13.1 Ideal independent, noiseless observations

With known centre, known SPD `H` and independent latent observations define
`Q = sum_i (x_i-mu)^T H (x_i-mu)`, `nu=Nd`. Then

\[
\ell(\beta)=\tfrac{Nd}{2}\log\beta-\tfrac\beta2 Q+\text{constant},\quad
\widehat\beta_{ML}=\frac{Nd}{Q},\quad \beta Q\sim\chi^2_\nu.
\tag{T.11}
\]

Consequently, for `nu>4`,

\[
E\widehat\beta_{ML}=\frac{Nd}{\nu-2}\beta,\qquad
\operatorname{Var}(\widehat\beta_{ML})=
\frac{2(Nd)^2\beta^2}{(\nu-2)^2(\nu-4)}.
\tag{T.12}
\]

The unbiased estimator is `(nu-2)/Q`, with variance `2 beta^2/(nu-4)`.
An exact equal-tailed `1-alpha` interval is
`[chi2_nu(alpha/2)/Q, chi2_nu(1-alpha/2)/Q]`. These are distributional statements
under the assumptions, not labels transferable to correlated camera frames.

If the centre is estimated by the sample mean, use
`Q_c = sum_i (x_i-xbar)^T H (x_i-xbar)` and `nu=d(N-1)`.
The joint MLE is still **`Nd/Q_c`**, not `nu/Q_c`; its expectation and variance are
(T.12) with this new `nu`. The unbiased numerator and exact interval use the new `nu`.
Using a covariance divided by `N-1` produces a different moment estimator. This
experiment estimates the temporal model's centre as a nuisance and compares it with
A's centre; it never treats that fitted centre as externally known.

For known-centre noiseless independent data, `d/tr(H S_N)`, `d/(2 mean(V))`, and
(T.11) are exactly the same estimator. This exact identity has this precise scope.
For a fixed wrong centre with displacement `delta`, the quadratic statistic is
noncentral, with noncentrality `N beta delta^T H delta`; pretending it is central
biases the scale. Centre uncertainty is therefore explicitly included.

### 13.2 General direct-potential estimator

For independent exact positions and a fixed general potential on a fixed measure,

\[
\ell(\beta)=-\beta\sum_i V(x_i)-N\log Z(\beta),\quad
\ell'(\beta)=N E_\beta V-\sum_i V(x_i),\quad
-\ell''(\beta)=N\operatorname{Var}_\beta V.
\tag{T.13}
\]

A unique interior MLE requires nonzero variance and the observed energy mean to lie in
the model's attainable mean range. Normalization, boundary estimates and integrability
must be handled, not absorbed into a fitted arbitrary constant. The harmonic case
makes these formulas analytic. No nonquadratic numerical partition-function branch is
added to the present experiment after seeing a Gaussian diagnostic fail.

### 13.3 Correlation changes the estimator and its law

For known noiseless transition `F` in whitened coordinates with stationary covariance
`beta^{-1} I`, put `M_F=(I-FF^T)^{-1}` and

\[
Q_F=\|z_0\|^2+\sum_{i=1}^{N-1}
 (z_i-Fz_{i-1})^T M_F(z_i-Fz_{i-1}).
\tag{T.14}
\]

If `F` and centre are truly known, `beta Q_F` is exactly `chi2_(Nd)` and the conditional
MLE is `Nd/Q_F`. When `F` is estimated, maximizing the profile likelihood is not the
same operation as dividing by the sample mean energy. The fitted residual statistic
has no asserted `chi2_(Nd)` law. A general stable `F` can be irreversible; neither
(T.14) nor stationarity alone establishes detailed balance.

For one reversible scalar OU mode, with lag correlation `rho`, the large-N variance
of the log scale after estimating the temporal parameter is
`2(1+rho^2)/[N(1-rho^2)]`. Known temporal parameters would give `2/N` in the ideal
fully observed case. In multiple independent modes, the efficient temporal-profile
information and the trace-moment information generally differ. For mode inflation
`a_r=(1+rho_r^2)/(1-rho_r^2)`, the asymptotic log-scale variances are

\[
\operatorname{avar}(\log\widehat\beta_{profile})=
\frac{2}{N\sum_r a_r^{-1}},\quad
\operatorname{avar}(\log\widehat\beta_{moment})=
\frac{2\sum_r a_r}{Nd^2}.
\tag{T.15}
\]

The harmonic-mean/arithmetic-mean inequality orders these ideal asymptotic variances;
it does not assert finite-sample equality of estimators. Noise, exposure integration,
free centre and calibration uncertainty require the actual likelihood information.

### 13.4 Additive noise changes the likelihood score

For independent instantaneous observations with known noise covariance `R_obs`,
`C_beta = beta^{-1}H^{-1}+R_obs`. For known mean, the score is

\[
\partial_\beta\ell=
\frac{1}{2\beta^2}\left\{N\operatorname{tr}(C_\beta^{-1}H^{-1})-
\sum_i e_i^TC_\beta^{-1}H^{-1}C_\beta^{-1}e_i\right\}.
\tag{T.16}
\]

The noise-corrected trace estimator
`d/tr[H(S_y-R_obs)]` is a method-of-moments estimator, **not generally the MLE**.
It can be undefined when the corrected covariance is not positive; truncating it into
a plausible beta is forbidden. The formulas coincide only in special cases such as
zero noise or an appropriately isotropic whitened noise covariance, with consistent
mean and covariance normalization. In the latter case an interior solution still has
to exist. The actual primary estimator is the numerical maximizer of (T.6); its bias,
coverage and failure probability require V. An asymptotic Fisher variance is a
planning quantity, not a finite-sample exact law.

## 14. T7 — five different equivalences

| Level | Valid statement | What does not follow |
|---|---|---|
| Model | On the declared harmonic full-space Gaussian family, the direct bridge is equivalent to `Sigma=beta^{-1}H^{-1}` **and** the correct centre | Covariance alone characterizes an arbitrary density |
| Population | That model gives `E[V]=d/(2 beta)` and normalized covariance scalar identity | Matching one energy moment establishes shape, tails or equilibrium |
| Estimator | Ideal iid known-centre noiseless Gaussian trace, energy and MLE formulas coincide | The noisy state-space MLE equals the trace estimator |
| Test | Full Gaussian likelihood and appropriately specified full covariance/mean inference can address the same population hypothesis | Their statistics, confidence sets or rejection regions coincide |
| Finite sample | The stated ideal pivots are exact with their stated degrees of freedom | Profile LR, effective-N substitution, estimated calibration or noisy observations inherit those pivots |

In particular, the richer fitted path law adds temporal assumptions beyond the static
density theorem. A path-model diagnostic failure makes this inferential realization
unusable; it is not a proof that the general equilibrium theorem is false.

## 15. T8 — observation model

### 15.1 Selected strategy: explicit calibrated noise and exposure

Use the independently characterized linear detector model

\[
y_i=b_{\rm det}+P\int w_i(s)X_s\,ds+\epsilon_i,
\qquad \int w_i(s)ds=1,\qquad
\epsilon_i\sim N(0,R_{\rm obs}).
\tag{T.17}
\]

`P` is the invertible physical-coordinate to detector-coordinate matrix. The known
shutter weights have finite, recorded support. After independently justified electronic
filter handling, localization errors are independent between frames and independent
of the latent path. If that is not true, the chosen observation model is not qualified;
a coloured-noise extension needs prospective revision, not an unrecorded workaround.

For `s>=t`, `Cov(X_s,X_t)=exp[-A(s-t)] Sigma`; the reverse-time block is its transpose.
Thus every block of `C` in (T.6) is the double integral of this kernel against `w_i,w_j`,
left/right transformed by `P,P^T`, plus the appropriate detector-noise block. This
includes motion blur and interframe correlations exactly **within the specified model**.
Exposure length and `R_obs` cannot be estimated by assuming `beta_true=1`.

Immobilized targets, independent positional standards and timed detector measurements
are possible independent sources for these calibrations. U must establish their
relevance to brightness, temperature and exposure in all four fields. A static-bead
noise estimate does not itself characterize motion blur. Blur uses independently known
shutter timing together with the fitted temporal likelihood, with timing uncertainty
propagated. The temporal fit is not a substitute for the independent energy measurement.

### 15.2 Qualification limits and bounded residuals

Use a prospective exposure ceiling `t_exp <= 0.1 tau_fast` and require the largest
noise-to-signal covariance eigenvalue to be at most **0.05** over the validated
scale/field envelope. These are design qualification limits, not known detector
performance. Exact exposure integration is still used; the ceiling does not license
setting blur to zero. Actual conditional Fisher information is checked because a
5% instantaneous noise ratio alone does not prove a 5% precision penalty for an
exposure-averaged state-space fit.

Digitization, residual distortion, timing approximation, independent drift correction,
small physical departures within the calibration interval and likelihood numerical
error must together have a certified log-scale bias bound

\[
b_a\le0.0005\quad\text{per absolute comparison},\qquad
b_c\le0.0005\quad\text{per within-block contrast}.
\tag{T.18}
\]

The contrast bound is calculated jointly; it is not inferred by calling two errors
common. Two separate 0.0005 absolute bounds alone would only give 0.001 for a contrast.
For example, uniform per-cell bounds of 0.00025 suffice for the stated contrast bound.
The interval for the ideal model is enlarged on each side by the applicable bound.
For worst-case true-bridge power, an additional equal displacement of the estimator
must be allowed: the planning margin is `delta - 2b`, not `delta - b`.

U must give an explicit deterministic error propagation or a separately covered
uncertainty model for these bounds. Reporting a fine pixel grid without propagating
its effect on the likelihood does not suffice. If digitization cannot meet the bound,
one must prospectively use the integrated bin-probability likelihood or redesign the
instrument before W; the current Gaussian observation approximation is then unqualified.
No observed B outcome selects between a noise-free and noisy model.

For geometry, centre and equilibrium statistics, residual-error sets are propagated
through the same comparisons and included in their upper limits. A scalar log-beta
bound does not cover arbitrary shape or current error. Their separate error sets must
fit the precision qualification in §22.4.

### 15.3 Separation of statistical and physical validity

The measured `R_obs` must be PSD with uncertainty accounted for; `P` must be nonsingular
and geometrically calibrated. The latent fitted covariance must remain SPD. A failure
is an invalid observation/model result, not a negative beta. Cross-channel noise,
rotational calibration error and unequal magnifications cannot be replaced by one
scalar variance. Detector uncertainty that is shared with A is represented once in the
joint primitive vector rather than independently double-counted.

## 16. Branch-A uncertainty propagation

### 16.1 Primitive model

Let `phi` contain thermometry offsets and slopes, viscosity-model parameters, bead
radius, force/velocity calibration, displacement calibration, both coordinate maps,
orientation, centre, wall corrections if applicable, detector noise, shutter/timing,
and independently observed drift corrections. Record the complete joint covariance
`C_phi`, its estimation uncertainty and distributional/coverage basis, and separately
record any bounded systematic errors. A covariance matrix by itself is not a calibrated
sampling distribution. V must use U's justified auxiliary measurement law, not silently
assign independent Gaussian errors to every entry.

Under the retained Stokes force-displacement route, for a decoupled mode,

\[
k_r=6\pi\eta(T)a\,\frac{v_r}{\Delta x_r},\qquad
h_r=\frac{k_r}{k_BT},
\]
\[
d\log h_r=d\log\eta+d\log a+d\log v_r-d\log\Delta x_r-d\log T.
\tag{T.19}
\]

If `eta=eta(T;zeta)`, the coefficient of the same temperature error is
`partial_T log eta - 1/T`, together with derivatives in `zeta`. Do not add an independent
viscosity-temperature error and then count the same thermometer error again. Radius,
wall effects and velocity standards may correlate multiple modes and fields. Even if
A's point estimate of stiffness is subsequently expressed as a matrix, these dependencies
remain in its covariance. An anisotropic force/displacement fit must propagate its full
matrix calibration rather than applying independent scalar-mode errors by default.

Validate `eta(T)` and `a` separately as finite real strictly positive physical inputs.
Checking only their product allows two negative primitives to masquerade as positive
drag. Missing values, inadmissible values and numerical representation failures retain
distinct meanings. Stokes drag itself requires independently qualified fluid, geometry
and wall conditions. No placeholder viscosity or bead radius produces a valid packet.

### 16.2 Common, block and cell components

Decompose only for provenance, not to discard cross-covariances:
`phi = (phi_shared, phi_block1, phi_block2, phi_cells)`. Shared standards may correlate
the two preparations despite independent bead preparation and acquisition. Within a
preparation the same bead radius or velocity scale may be common, while viscosity at
318 K has a different derivative from viscosity at 298 K. The full covariance is used.

For the conditional comparison estimator vector `bhat`, first-order propagation is

\[
C_b\simeq C_{B\mid\phi}+J_\phi C_\phi J_\phi^T,
\qquad J_\phi=\partial\widehat b/\partial\phi.
\tag{T.20}
\]

This expression assumes exogenous calibration errors conditional on the physical
state. If an auxiliary measurement has statistical covariance with the B noise, retain
the associated cross terms; independence is not inferred from separate filenames.
The derivative includes the effect of `phi` on both the A landscape and the B coordinate
or observation model. For the simple noiseless moment estimator,
`d log beta = -tr(S dH + H dS)/tr(HS)`. A shared pixel scale can therefore enter twice
or cancel partly, depending on how velocity and displacement were measured. It cannot
be removed by a blanket “common-mode cancellation” sentence.

Propagate nonlinearities and calibration distribution tails in V's complete
measurement procedure. The analytic covariance is for planning and studentization;
it is not a replacement for that validation. The locked physical values remain locked.
Permitting calibration nuisance values in coverage calculations does not grant B
permission to publish a revised `H_A`.

## 17. Temporal correlation and acquisition information

No frame count is inserted as degrees of freedom into an iid chi-square law. All
frames enter (T.6). The information accounting used to plan the record is separate.
For a scalar stationary Gaussian OU mode, squared observations have correlation
`exp(-2 h Delta/tau)`, giving the exact variance inflation of their sample mean

\[
a_N=1+2\sum_{h=1}^{N-1}(1-h/N)e^{-2h\Delta/\tau},\qquad
N_{Q,eff}=N/a_N.
\tag{T.21}
\]

Its large-N conservative upper bound is `a_inf=coth(Delta/tau)`. For a whitened
multivariate OU with `S` in (T.10), `||exp(-Bt)|| <= exp[-lambda_min(S)t]`; hence
`tau_slow=1/lambda_min(S)` supplies a conservative quadratic-correlation envelope.
This follows by differentiating the squared norm along `zdot=-Bz`; the antisymmetric
part contributes zero. It does not assume reversibility.

Mean and quadratic effective sizes differ: the corresponding mean inflation is
`coth(Delta/(2 tau))`. Off-diagonal covariance elements likewise have their own mode
products. A universal scalar “ESS” is not an exact description of a multivariate
record. These envelopes help plan data collection and assess precision; they do not
turn the observed data into independent samples.

In the continuous Gaussian observation model with parameters `theta`, the exact
finite-record expected information has entries

\[
I_{ab}=(\partial_a m)^TC^{-1}(\partial_b m)
+\tfrac12\operatorname{tr}(C^{-1}C_{,a}C^{-1}C_{,b}).
\tag{T.22}
\]

For scale, take the Schur complement over fitted centre and temporal parameters.
This defines conditional efficient information `I_b.eff`; calibration uncertainty is
not counted as information from extra frames. Evaluating (T.22) deterministically from
a qualified parameter envelope is not a simulated trajectory. U supplies that envelope;
V checks the finite-sample estimator and the numerical information calculation.

The standard OU planning time `tau_r=6 pi eta(T) a/k_r` remains field-specific. A shared
`tau_c` across the power, ellipse and temperature fields is forbidden. The fitted B
dynamics may diagnose a departure from this physical prediction but cannot be fed back
to set the independently measured `k_r`.

## 18. T9 — non-Gaussianity and model adequacy

A nonquadratic canonical potential may have a non-Gaussian density and satisfy (T.1)
exactly. Non-Gaussianity cannot falsify the general S-stage theorem. Here, however,
independent A calibration qualifies a quadratic benchmark, and the selected likelihood
requires linear Gaussian dynamics and the specified noise model. Substantial
non-Gaussianity or residual time structure makes **this realization** inadequate.

Use standardized innovations from the unrestricted B fit, with parameter estimation
included in their null calibration. Freeze a compact diagnostic statistic as the maximum
of three components: (i) a Cramer–von Mises distance of squared innovation radii from
`chi2_2`; (ii) the summed squared sine/cosine sample means at angular harmonics 1 through
4; (iii) the squared Frobenius norms of innovation lag-covariances at lags 1 through 10,
and the three observed-minus-fitted-model lag-antisymmetry checks in §12. The free
model may contain a current; a nonzero raw lag asymmetry is not by itself its
goodness-of-fit failure. Scale each component by its frozen
null standard deviation and calibrate the maximum **jointly**, preserving dependence.
Zero/undefined null scale is a validation failure, not a dropped diagnostic. These
statistics and lag limits are fixed before V calibration; no search for favourable lags
or moments is permitted.

Use a familywise false-rejection target **0.005 across all eight records**. The V
procedure calibrates the maximum across records, including shared calibration effects.
A rejected diagnostic vetoes a model-qualified bridge conclusion. Non-rejection is
labelled **NO DECLARED MODEL DIAGNOSTIC REJECTED**, not positive proof of Gaussianity or
absence of every alternative. Positive scale, shape and centre confidence requirements
supply the precision claim; a finite diagnostic family cannot establish unrestricted
density equality. Overall conclusions are explicitly conditional on the qualified
harmonic state-space/observation family.

## 19. Support, truncation and coordinate scope

The scientific support is the full lateral affine plane with its calibrated Cartesian
Lebesgue measure. Axial `z` is designed out, not an observed zero-curvature conserved
mode. U must establish either lateral/axial separability or the appropriate independently
calibrated lateral potential of mean force; an unaccounted x-dependent marginalization
factor breaks the comparison. With a genuine linear conservation constraint in another
system one would use a basis `Q_T` and `H_T=Q_T^T H Q_T` on the accessible subspace, not
invert a singular ambient covariance. No such extra constraint is invented here.

A finite camera window, localization failure or clipped signal selects observations.
Keeping only selected positions and still using (T.4) is invalid. Require an independently
qualified detection envelope such that the total probability of **any** selection or
clipping over the entire eight-record experiment is at most `10^-4` throughout the
validated power/qualification envelope; the union bound `sum_i Pr(loss_i)` suffices and needs no
independence. Every scheduled detector slot must be accounted for; actual state-dependent
loss or saturation invalidates the entire cell, with no conditional-on-survival
analysis or replacement. Outside the power envelope, the same veto can only remove
success events from an otherwise valid unconditional density test, not increase its
false-support probability. The small selection allowance in §20 additionally covers
the qualified observation approximation; an undetected selection mechanism is not
covered by the veto argument. If unattainable, a truncated
or censored observation likelihood must be designed prospectively; it is not introduced
after seeing tails. A physical hard boundary also changes `Z` and fails this full-space
benchmark qualification.

For a constant invertible linear coordinate map, use its covariance transformation and
Jacobian consistently; the constant density Jacobian cancels in probability ratios.
Nonlinear coordinates or nonconstant density-of-states factors add to `-log p` and must
be part of the model. Relabelling pixels does not fix a wrong reference measure.
Normalizability is analytical for (T.4), but only on its stated support. For a later
anharmonic experiment, independently controlled quadrature error in `Z(beta)` would
be needed; that is not a hidden fallback branch of this design.

## 20. T10 — finite-N null and coverage strategy

### 20.1 Classification of every inferential law

| Object | Status before V |
|---|---|
| Ideal iid/noiseless/known-H gamma pivot in §13 | Exact under those stated assumptions |
| Gaussian OU transition and integrated Gaussian observation density | Exact model likelihood if all specified physical/statistical conditions hold |
| Actual conditional MLE bias, sampling law and uncertainty | No closed-form finite-N law asserted |
| Fisher/first-order calibration propagation and normal power in §22 | Analytically justified asymptotic planning approximations |
| Studentized log-scale intervals | Finite-N calibration required; not released |
| Shape, centre, stationarity and current upper limits | Finite-N calibration required, including nonregular zero-distance boundaries |
| Model diagnostic maximum | Finite-N joint calibration required |
| Deterministic entropy/P4 identity | Exact under S7; not a stochastic experimental endpoint |

An exact likelihood does not make Wilks' theorem finite-sample exact. A bootstrap at one
fitted null does not establish nuisance-uniform size. Correlated Wishart surrogates and
non-integer chi-square degrees of freedom are not substituted for the actual model.

### 20.2 Defined prospective confidence procedure

For each absolute scale or cross contrast, construct the studentized error using the
conditional MLE, its temporal-profile variance and the full auxiliary covariance in
(T.20). Its two tails are calibrated separately if necessary. The final interval is
`[bhat-c_minus s-b_bound, bhat+c_plus s+b_bound]`; use the corresponding contrast in
cross-field comparisons. The normal starting critical value is `Phi^-1(0.98)`, not an
assumption that the distribution is normal. Choose the **smallest conservative calibrated
critical values** satisfying the tail rules below, with a design qualification ceiling
`c_minus,c_plus <= 2.10`. Larger necessary values mean this T sample/power design has
not qualified and must return for prospective review; V cannot relax the error rate.

The mathematical target is an upper envelope of the relevant tail probability over
the complete qualified nuisance domain and the appropriate one-sided non-equivalence
null, including boundary points. Include scale, dynamics, noise, measurement errors,
shared standards, nonlinear calibration and selection. Boundary-only calibration is
permitted only with a demonstrated monotonicity or least-favourable-null argument;
it is not inferred from a convenient plot. A finite grid alone cannot establish a
continuous-domain supremum. V must provide a valid envelope/interpolation bound, a
reduction to proved least-favourable configurations, or state that qualification failed.

A nuisance confidence set may replace an unrestricted supremum: add its noncoverage
probability to the worst-case tail probability, as in the Berger–Boos construction.
The maximum total noncoverage allowance for such auxiliary confidence sets is **0.001
per one-sided procedure**. This includes any uncertain U envelope used by that procedure.
The set's randomness must be reproduced or bounded; it cannot be silently treated as
fixed true calibration. Any use of B to bound temporal nuisances serves only coverage
calculation, never to revise `H_A`. A data-dependent nuisance set needs the same coverage
proof. Bounded physical systematics are enlarged explicitly rather than redrawn as
independent zero-mean errors.

For shape, centre, stationarity and current, construct a calibrated confidence set for
the relevant unrestricted B/auxiliary contrasts and maximize the stated statistic over
it, including bounded error sets. Their one-sided noncoverage target is 0.025. This is
a complete definition of the upper-limit rule even when a statistic is zero and its
ordinary delta-method standard error vanishes. Do not use a zero Wald error at that
boundary. V determines and freezes the finite-N critical radii, then validates them.

### 20.3 Calibration and independent achieved-size release

This section specifies requirements for a later V task, not a validation plan amendment
or permission to run it. Freeze the new reference procedure, nuisance envelope, numerical
error bounds and calibration seeds before validation. Calibration, validation and
confirmatory streams are disjoint; existing v4 seeds and artifacts are not recycled as
if their scientific identity matched this procedure.

For scale procedures reserve, conservatively, at most 0.020 for the model-tail target,
0.001 for auxiliary-set noncoverage and 0.0001 for selection approximation. That leaves
at least 0.0039 below the maximum allowed one-sided false-equivalence size **0.025**
for finite calibration uncertainty and numerical envelope error. Explicitly account for
these terms rather than treating simulated critical quantiles as population quantiles.
Calibration order statistics or binomial tail bounds must include their own uncertainty.
The final 2.10 critical ceiling and all physical bias bounds remain binding.

At every declared least-favourable or otherwise required null configuration, use
**5,000 independent validation experiments** for achieved-size assessment and require
a one-sided 95% Clopper–Pearson upper bound no greater than 0.025 for false equivalence.
An outer experiment includes fresh auxiliary measurements and the required shared-error
structure; its frames are not validation replicates. Check both tails, shape/current
boundary nulls, the absolute and cross-field composite boundaries, and each negative
control separately. Upper-bound Monte Carlo error does not validate an unexamined
nuisance region. All required cases must pass; failure causes non-release.

For the diagnostic family, require the corresponding upper bound at most 0.005;
use at least 5,000 validation experiments and an internally conservative critical
value so the bound can meet the target. For full true-bridge success use **2,000 complete
eight-record experiments** and require a one-sided 95% lower bound at least 0.90.
The design aims for approximately 0.93 or better before finite-N validation, providing
headroom for that release criterion. Invalid, refused and optimizer-failed experiments
remain in the denominator. Exact integer acceptance counts are derived from the binomial
rule in V's separately reviewed plan; they are not copied from old R=300/400 criteria.

These are per-configuration validation requirements. Requiring every case to satisfy
its criterion is an intersection-union release test; it does not supply simultaneous
95% coverage for a table of all displayed confidence limits. Report that distinction.
Calibration sample counts must be sufficient to certify the stated quantile/error
budget; V may allocate those computational draws prospectively without altering the
experimental record length, endpoints, margins or release rules. No such draws occur
in T.

### 20.4 Necessary controls

Retain hidden A scale factors `c=1.07` and `0.90`, expecting `beta_blinded=beta/c` and
recovery of the unblinded value after multiplying by c. In (T.5), scaling `H` and
inversely scaling beta leaves `Sigma` unchanged with the same temporal nuisance,
so this remains an exact model-level reparameterization even with the fixed detector
model. Apply the transform to comparison copies, never mutate primary A data.

Exercise fieldwise alternatives `(1,1.06,1,1)`, `(1,0.93,1.05,1)`, `(1,1,1,1.10)` and
the hard 2.5% single-field contrast; common beta 0.7; trace-preserving wrong geometry;
rotated ellipse; current-preserving Gaussian density; temperature/viscosity covariance
errors; localization and blur mismatch; slow drift; and support selection. A time shuffle
is solely a temporal-control diagnostic: it cannot change a covariance-based geometry
statistic. Do not call a permutation that only reorders sample times a geometry control.

Each out-of-tolerance alternative must meet the false-support bound, but this is not
a promise to demonstrate an outside-tolerance discrepancy with high power when the
truth is only 0.5 percentage points beyond a margin. That separate power question is
quantified in §22.5. No outcome is allowed to tune the tolerances or remove a hard case.

## 21. Multiplicity and verdict logic

The primary success event is the conjunction of valid A, valid observation/support,
all eight absolute intervals, all six within-block contrast intervals, all eight shape
and centre limits, all eight stationarity/current gates, and no rejected diagnostic.
P4 consistency is recorded but adds no independent experimental support.

For positive equivalence, the global null is the **union** of component failures. If at
least one component is outside its tolerance, the probability all components pass is
at most that component's valid 0.025 size. Thus no Bonferroni adjustment of every
positive-equivalence interval is required for this single global conjunction, regardless
of shared reference or calibration dependence. This is different from making
simultaneously valid claims for every individual interval. Such individual intervals are
reported as marginal intervals.

The negative model-diagnostic maximum has its own joint familywise 0.005 rule. If the
report additionally declares one or more statistically established discrepancies,
use a separately frozen Holm family at 0.05 across the announced discrepancy tests,
or simultaneous 95% regions. A marginal interval outside a tolerance can be shown as
an individual result but is not relabelled a multiplicity-controlled discovery.
Multiplicity for false rejection and false positive support must not be conflated.

| Classification | Meaning |
|---|---|
| SUPPORTED_WITHIN_DECLARED_TOLERANCES | Every required positive condition and validity condition passes, within the specified model/bandwidth |
| DISCREPANCY_ESTABLISHED | Valid inference establishes at least one named beyond-margin discrepancy with the declared discovery control |
| INCONCLUSIVE / INSUFFICIENT_PRECISION | Intervals overlap a margin, required precision is not reached, or density and equilibrium conclusions differ without a resolved contradiction |
| INVALID_MEASUREMENT_OR_MODEL | Missing/invalid calibration, support loss, unqualified dynamics/noise, nonstationarity or an invalid statistical model prevents the intended interpretation |
| COMPUTATION_NOT_EVALUABLE | Numerical/optimizer/provenance failure; no scientific verdict fabricated |

A failed equivalence test is not automatically evidence of a discrepancy. Failure to
establish reversibility is not automatically evidence of a current. All scalar estimates
may still be shown diagnostically, clearly marked when their model is invalid. Invalid
or refused cells never disappear from the planned experiment or its complete-pass denominator.

## 22. T11 — power and final sample-size decision

### 22.1 Fixed information target and calibration floor

Adopt, for **each of the eight cells**,

\[
N_* = 450{,}000\quad\text{independent quadratic-observation equivalents},\qquad
I_* = \left\lceil\frac{N_*}{1.05^2}\right\rceil=408{,}164
\quad\text{for }b=\log\beta.
\tag{T.23}
\]

For two ideal noiseless iid coordinates, log-scale information is `N`; with at most
5% independent instantaneous localization variance in each whitened direction, the
information is at least `N/(1.05)^2` when other inputs are known. This follows by
diagonalizing the whitened noise: each coordinate contributes
`N/[2(1+r_i)^2]`, `0<=r_i<=0.05`. In the actual fitted, blurred temporal model, use the
Schur-complement information (T.22), not this shortcut. Both the conservative quadratic
count and the actual conditional information threshold must be met.

The sufficient qualification envelope is

\[
\sigma_{a,cal}\le0.009,\qquad
\sigma_{c,cal}\le0.003,\qquad b_a,b_c\le0.0005,
\qquad c_-,c_+\le2.10.
\tag{T.24}
\]

Calibration here includes all A, shared-coordinate and observation-calibration
uncertainty projected into the endpoint, with all covariances; it excludes the conditional
B sampling term. The 0.9% absolute and 0.30% contrast limits are a **sufficient instrument
specification** for the selected replication and power requirement. They are not
necessary universal limits and are not assumed achieved by the old hypothetical
apparatus. They are chosen from the power calculation below while preserving the
existing scientific margins, not by making a tolerance convenient.

If an irreducible calibration floor violates this specification, more B frames do not
qualify this design. U must report that fact. Improving independent calibration or a
prospectively reviewed redesign are possible later responses; widening the scientific
margins after outcomes is not. Retaining two blocks and the tighter envelope gives
preparation reproducibility without fitting a poorly identified random-effects model.

### 22.2 Analytic power calculation

For planning use conservative standard errors

\[
s_a(N)=\sqrt{0.009^2+1.1025/N},\qquad
s_c(N)=\sqrt{0.003^2+2.205/N}.
\tag{T.25}
\]

The cross-field sampling sum is valid for independent records conditional on shared
calibration; shared calibration has already entered its contrast term. At a true zero
log difference, a conservative normal-approximation bound on the probability a scale
interval fails is

\[
f(\delta,s)=\min\left\{1,\;2\left[1-\Phi\left(
\frac{\delta-0.001}{s}-2.10\right)\right]\right\}.
\tag{T.26}
\]

The 0.001 is **twice** the 0.0005 bounded residual: interval enlargement plus worst-case
estimator displacement. The union bound across eight absolute and six cross comparisons
requires no independence. It yields `8 f(delta_a,s_a)+6 f(delta_c,s_c)` as an upper
planning bound on scale failure, capped at one if necessary.

As a deliberately conservative preliminary allocation, require each of the fourteen
scale comparisons to have failure probability at most `0.06/14`. Then
`q=Phi^-1(1-0.06/28)=2.856328527` and

\[
N\ge\max\left\{
\frac{1.1025}{[(\delta_a-0.001)/(2.10+q)]^2-0.009^2},\;
\frac{2.205}{[(\delta_c-0.001)/(2.10+q)]^2-0.003^2}
\right\}.
\tag{T.27}
\]

The requirements are approximately **92,083** and **408,950** equivalents respectively.
The **450,000** choice rounds the binding cross-field requirement upward by about 10%.
A nonpositive denominator would prove that this sufficient power allocation cannot be
met at any sample size. That is the relevant calibration-floor test, not a raw frame count.

| Quadratic equivalents per cell | Absolute log SE | Cross log SE | Approximate union scale-failure bound |
|---:|---:|---:|---:|
| 100,000 | 0.0095930 | 0.0055723 | Uninformative (uncapped sum exceeds 1) |
| 200,000 | 0.0093012 | 0.0044749 | 0.23249 |
| 400,000 | 0.0091518 | 0.0038095 | 0.04181 |
| **450,000** | **0.0091351** | **0.0037283** | **0.03340** |
| 500,000 | 0.0091217 | 0.0036620 | 0.02801 |
| 1,000,000 | 0.0090610 | 0.0033474 | 0.01464 |
| 2,000,000 | 0.0090306 | 0.0031784 | 0.01212 |

At the selected target, nominal planning half-widths **including one** 0.0005 interval
enlargement are about 0.019684 absolute and 0.008329 cross. As N tends to infinity,
the corresponding floors are 0.0194 and 0.0068. Absolute precision is already almost
at its calibration floor; cross-field precision still gains modestly above 450,000,
but the stated power requirement has been met in the planning approximation. The
50,000-to-1,000,000 **raw-frame** table in the previous technical design is not this
table and cannot be read as independent observations.

For full-pipeline planning reserve at most 0.025 failure probability for all positive
geometry/centre/stationarity/current precision gates together, 0.005 for the diagnostic
veto family, and 0.005 for remaining qualification/numerical refusal events in the
qualified repeated-experiment model. With the 0.03341 scale bound, this gives an
**approximate planning success budget of at least 0.93159**. These are prospective
allocations, not measured probabilities or a theorem about the implemented pipeline.
They are included in V's unconditional complete-pass validation; failure of any
allocation or the complete 0.90 lower-bound criterion prevents release.

### 22.3 Frame count and duration: a decision rule, not a new U choice

For each cell, U supplies independent upper slow-time bound `tau_s` and lower fast-time
bound `tau_f`, covering the specified bandwidth and nuisance uncertainty. In the simple
passive isotropic-drag design these derive from `6 pi eta(T) a/k_r`; uncertainty must
be included. The hardware must support

\[
\Delta=\min(120\text{ microseconds},\;\tau_f/5),\qquad
t_{exp}\le0.1\tau_f,
\]
\[
N_0=\left\lceil450000\coth(\Delta/\tau_s)\right\rceil.
\tag{T.28}
\]

If an allowed clock has discrete settings, use the largest available interval no
greater than this Delta and recalculate `N_0`; do not round toward slower sampling.
Use `D=N_raw Delta` for planned exposure-slot duration. All scheduled post-burn-in
frames are retained; no thinning is applied. Missing independently random frames
must be explicitly handled by the likelihood and information calculation; unplanned
loss cannot be compensated by outcome-dependent extension.

The final pre-B count is the **smallest integer N_raw between N_0 and 2 N_0** for which
(i) the conservative quadratic information remains at least `N_*`, (ii) the infimum of
`I_b.eff(N_raw)` over the qualified design/power envelope is at least `I_*`, and
(iii) the positive-gate precision requirement in §22.4 holds. The power envelope covers
beta in `[1/1.10,1.10]` and the qualified physical/calibration parameters; false-support
coverage must still handle the full composite null as required in §20. The interval
of counts, targets, cap and minimization rule are **fixed here**. U instantiates them
with independent measurements and deterministic information calculations; it does not
choose a sample target or look at B outcomes.

If no count in this bounded range meets all three conditions, this minimal design is
**UNQUALIFIED**, and returns for prospective T revision. It does not silently double
again, loosen a gate or proceed underpowered. The cap prevents an unspecified
open-ended acquisition campaign. Acquisition includes fixed burn-in and independent
thermal settling in addition to D. V must also verify the selected finite-N procedure
before W adoption and any physical execution.

### 22.4 Precision of the positive gates

The scale calculation is not allowed to conceal underpowered geometry or equilibrium
gates. There are 32 such positive gates: shape, centre, stationarity and current for
each of eight cells. Allocate planning false-inconclusive risk
`gamma_g=0.025/32` to each at the ideal benchmark. Their null values are zero.

For each gate define a vector `w_g` of its smooth underlying contrasts: two traceless
log-shape components; two centre components; the quarter-pair centre and log-covariance
contrasts; or the antisymmetric drift component together with its dissipative-rate
nuisance. Obtain its planning covariance from the full free-model information and
auxiliary uncertainty, including shared observations between quarters. Remove only
algebraic redundancies using a **fixed** contrast basis; rank is not selected from an
outcome. Let `E_q` be the corresponding Gaussian planning error ellipsoid at probability
q on that rank. Let `B_g` be the independently bounded systematic-error set.

U must verify by deterministic propagation that

\[
\sup_{w\in E_{1-\gamma_g}\oplus E_{.975}\oplus B_g\oplus B_g}
 g(w)<\delta_g
\tag{T.29}
\]

at the canonical zero contrasts, evaluated about each positive qualified nuisance
rate, over the design envelope. The dissipative rate is a nuisance level, not a
contrast that is set to zero.
For stationarity `g` is already divided by its tolerances, so `delta_g=1`; the other
thresholds are those of §§11–12. Two copies of the bounded set account for displacement
and interval expansion. The ellipsoid construction is a **planning approximation**;
V's calibrated regions must attain their coverage and its full-experiment validation
must verify power. If V's required region is wider, the previously selected sample count
cannot be called qualified on the strength of (T.29) alone. This check can make the
frame-count rule binding before scale information does.

Equation (T.29), the fixed risk allocation and the count cap resolve the geometry and
equilibrium precision decision prospectively. They do not invent an orientation,
thermometry or drift capability. If a calibration floor makes (T.29) fail even at infinite
N, U records that physical obstacle; it cannot be solved by collecting a longer path.

### 22.5 Meaningful alternatives and what power does not mean

The margin edges themselves are the smallest discrepancies this equivalence design
promises not to endorse: 5% absolute and 2% relative, with reciprocal symmetry. False
support at or beyond those edges has the §20 bound. That is not the same as a 90%
probability of proving a value beyond the edge.

For a separate discrimination scale, use **10% absolute** and **5% relative** deviations
(and their reciprocal counterparts). Under the same worst-case planning SEs and
bounded-error allowance, a conservative normal critical value about 3.273 covers a
Bonferroni first-step bound for 47 two-sided discrepancy tests (14 scale, 32 positive-gate
and one diagnostic-family hypotheses), hence is conservative for the corresponding
Holm family. The approximate probability of establishing a named positive-direction
scale discrepancy beyond its tolerance is

\[
\Phi\left(\frac{|h_{true}|-\delta-0.001}{s}-3.273078364\right).
\tag{T.30}
\]

It is about **0.9564 for a 10% absolute deviation** and **0.99999 for a 5% cross-field
deviation**, under this planning approximation and local variance envelope. These are
not claimed achieved powers. At a 2.5% cross-field deviation the corresponding marginal
2.10-critical calculation is only about **0.145**, and the conservative 47-test value
about **0.013**. Therefore the hard 2.5% control is a false-support challenge, not a
promised high-power positive-discrepancy demonstration. A non-pass there is often
correctly inconclusive.

## 23. Replicate structure

Use **two complete preparations**, with a fresh bead/preparation and an independently
repeated force-displacement and thermometry calibration in each. Run fields in fixed
orders `theta0, theta1, theta2, theta3` for block 1 and the reverse for block 2. Reverse
order is a minimal check against confounding field effects with time; it is not a
randomized population design. Preserve common traceable standards and their covariance
rather than claiming every calibration error was independently redrawn.

Both blocks must meet every endpoint separately. There is no pooling of all frames into
one apparent replicate and no rule that averages away a failing block. Within-block
cross-field contrasts use the same preparation's reference. Descriptive between-block
beta differences and preparation metadata are reported, but no random-effects variance
or population reproducibility claim is inferred from two blocks. Additional biological,
economic or instrument-population replication is outside this first benchmark.

One block would measure only one preparation; two is the smallest design that can
reveal a preparation-dependent failure while preserving all four field contrasts.
The stronger all-blocks success criterion is why its calibration and power budget
cannot simply be copied from the older one-block hypothetical design.

## 24. Field-by-field acquisition design

The table applies separately to both preparations, using their own U-qualified time
bounds. `N_U` denotes the exact deterministic choice from §22.3, not a future statistical
preference. Every row has target `N_Q,eff >= 450,000`, `I_b.eff >= 408,164` and the same
§22.4 gate precision requirement.

| Field / preparations | Sampling / base recorded and retained frames | Final duration after settling and burn-in | Role in primary comparisons |
|---|---|---|---|
| theta0 / r=1,2 | Delta_0 from (T.28); N_0,0=ceil(450000 coth(Delta_0/tau_s,0)); retain all N_U,0 in [N_0,0,2N_0,0] | N_U,0 Delta_0 | Two absolute comparisons; reference in six contrasts |
| theta1 / r=1,2 | Delta_1 from (T.28); same formula with field-1 times; retain all N_U,1 | N_U,1 Delta_1 | Two absolute and two power/reference comparisons |
| theta2 / r=1,2 | Delta_2 from fastest mode; N_0,2 uses slowest mode; retain all N_U,2 | N_U,2 Delta_2 | Two absolute, two ellipse/reference and full geometry comparisons |
| theta3 / r=1,2 | Delta_3 from independently measured eta(318 K), radius and stiffness; retain all N_U,3 | N_U,3 Delta_3 | Two absolute and two temperature/reference comparisons |

For insight into the rule, **not an apparatus prediction**, insert exact nominal modal
ratios and no uncertainty in the time bounds, and suppose `Delta=tau_fast/5`. The base
counts and durations become:

| Field | Base frames per preparation | Base D / tau_slow | Instantaneous idealized scale information basis |
|---|---:|---:|---|
| theta0 | 2,279,921 | 455,984.2 | 450,000 quadratic equivalents |
| theta1 | 2,279,921 | 455,984.2 | Same information, faster physical relaxation |
| theta2 | 5,636,995 | 450,959.6 | Conservative slow-mode bound; faster mode supplies extra information |
| theta3 | 2,279,921 | 455,984.2 | Same nominal ratios, separately measured thermal drag |

For a **hypothetical arithmetic illustration only**, `eta(298 K)=0.00089 Pa s` and
`a=1 micrometre` give base durations about 76.50 s, 36.43 s and 126.09 s in the first
three fields; their frame intervals are about 33.55, 15.98 and 22.37 microseconds.
No viscosity is invented for 318 K; its duration stays symbolic until independent
qualification. Shutter integration, nuisance uncertainty and positive-gate precision
can increase each count by the prescribed rule up to the fixed cap. These numbers
must not be substituted for measured A values or used to authorize acquisition.

Compared with the old **2,000,000 frames at 120 microseconds = 240 s per field**, this
is an information decision with finer temporal resolution for reversibility. It can
use more recorded frames while requiring less physical time in the illustrative regime.
It makes no universal storage-saving claim. Old counts were already near a calibration
floor for their scale endpoints; copying two million to every new field would ignore
both the new current diagnostic's bandwidth and the new two-preparation power budget.

## 25. Consolidated design decisions

| Question | Selected decision | Qualification or non-pass condition |
|---|---|---|
| Primary scientific object | Direct Boltzmann density bridge | Conditional on stated harmonic/measure/support model |
| Primary inferential model | Gaussian OU state-space likelihood with explicit detector noise and exposure | Unqualified memory/noise/bandwidth invalidates realization |
| Physical calibration route | Independent force-displacement with Stokes drag plus thermometry | Full eta(T), radius, geometry and covariance qualification required |
| Beta estimator | Conditional likelihood maximizer, physical calibration fixed | Numerical and finite-sample performance must qualify |
| Absolute agreement | All 8 log intervals inside plus/minus log(1.05) | Outside, overlap and invalidity distinguished |
| Cross agreement | All 6 within-preparation reference contrasts inside plus/minus log(1.02) | No forced shared beta or assumed universal cancellation |
| Shape and centre | Positive upper bounds on G and m | No pass from non-rejection alone |
| Equilibrium | Physical conditions, positive stationarity/current bounds, diagnostics | Density-only success remains separate |
| Noise strategy | Explicit independently calibrated model | Never choose a noise-free model after looking at beta |
| Time correlation | Full likelihood; information/ESS only for planning | No iid degrees-of-freedom substitution |
| Replication | Two complete independently prepared blocks | No selective pooling or silent replacement |
| Sample target | 450,000 quadratic equivalents and information 408,164 per cell | Fixed U instantiation rule, cap 2N_0, precision/floor qualification |
| Finite-N release | Separate calibration and validation, achieved-size and power bounds | Exact likelihood alone cannot release |
| Additional human scientific choice | NONE for T1–T11 | Apparatus facts and subsequent stage authorizations remain necessary |

## 26. Comparison with old E1a-v4

This is a **prospective replacement proposal**, not an amendment in force. The old
controlling Markdown/JSON pair, plan, seed map, seal, identities and implementation
remain byte-identical. Only W-stage may adopt a new authority after the prerequisite
reviews and qualification. “Remove” below means from the proposed new design, never
from repository history.

| Old item | Action in proposed design | Reason |
|---|---|---|
| Independent A mechanical/thermal versus B probability branches | KEEP and specify shared calibration covariance | Core protection against circular confirmation |
| `K=beta H` as central statement | REPLACE by direct density bridge; KEEP as harmonic diagnostic | Correct theorem hierarchy |
| Trace beta point estimate | REPLACE primary by actual noisy temporal likelihood; KEEP ideal algebra/MoM diagnostic | Old formula is not general noisy/profile MLE |
| P3 all-field absolute tolerance | KEEP purpose and 5%; use reciprocal log interval and two blocks | Positive absolute denomination test |
| P2 reference ratios | KEEP purpose and 2%; full covariance, two blocks | Exact common-mode cancellation only where proved |
| G1–G4 minimum-p surrogate and G5 primary Gaussian block | REPLACE by shape/centre positive limits and model diagnostics | Avoid redundant geometry summaries and preserve correct non-Gaussian scope |
| Principal-angle blocking around circularity | REMOVE as primary rule | Intrinsic shape statistic remains regular as a matrix at repeated eigenvalues |
| Equilibrium implicit in the generator | REPLACE with explicit separately assessed reversibility and stationarity | Density does not establish detailed balance |
| Camera/noise absent from synthetic position model | REPLACE with independent observation subpacket and integrated likelihood | Measurements are not latent exact positions |
| eta/a treated mainly as correlation inputs in old error generator | REPLACE propagation model | Route-A H_U itself depends on eta and radius |
| Uniform two-million-frame records | REPLACE by fixed information, sampling-bandwidth and duration rule | Compare information and floors, not historical frame counts |
| Four field roles | KEEP | Each has a distinct requested falsifier |
| P4 entropy consistency | KEEP secondary deterministic check | No independent B evidence or extra primary endpoint |
| C1 true-bridge complete success | KEEP purpose, new two-block procedure and validation count | Unconditional performance still matters |
| C2 false geometry rejection | REPLACE test; KEEP operating-characteristic validation | Positive geometry support and diagnostic rejection need separate size treatment |
| C3 non-Gaussian/G5 role | REPLACE by chosen-model diagnostic | General direct theorem permits non-Gaussian equilibria |
| C4 covariance-matched surrogate validity | REMOVE obsolete surrogate; KEEP actual temporal/noise-model validation | Eliminating a surrogate does not eliminate achieved-size validation |
| C5 plug-in A | KEEP and strengthen full primitive propagation | Dominant systematic source is not solved by longer trajectories |
| C6 mode boundary | REPLACE by SPD/conditioning, isotropic invariance and geometry power checks | Repeated eigenvalues differ from near-zero curvature |
| C7 false bridge and C8 hidden scale | KEEP scientific purposes | Discrimination and noncircular scale recovery remain necessary |
| Old calibration ledgers, driver and frozen operational identifiers | DEFER any reuse/adaptation to W | No new scientific identity may be silently attached to old artifacts |
| Old v4 results and campaign | PRESERVE pause; no execution | T is design only |

## 27. Previous technical-design defects: explicit closure

| Failed-design issue | T disposition | Resolution and later owner |
|---|---|---|
| Arbitrary stable irreversible transition called equilibrium | RESOLVED IN DESIGN | Broad temporal model is explicitly a density embedding; (T.10), bandwidth qualification and separate positive current gate are mandatory. U qualifies physical bandwidth; V validates detection. |
| Moment estimator described as generally identical to correlated/noisy MLE | RESOLVED | §§13–14 give exact limited identity, unknown-mean degrees of freedom, noise score and distinct profile estimator. No finite-sample identity is asserted outside its premises. |
| Exact likelihood confused with exact finite-N null | RESOLVED IN DESIGN; ACHIEVED SIZE DEFERRED TO V | §20 classifies every law, specifies nuisance control, critical ceiling, seed separation and achieved-size release. No test declared validated now. |
| Endpoint/authority transition incomplete | RESOLVED PROSPECTIVELY | §§21,25–26 specify the entire conjunction, verdicts and old-to-new map. W must enact a new reviewed authority; old contracts remain controlling meanwhile. |
| Sample-size knee left undecided | RESOLVED | 450,000 equivalents / information 408,164 per cell; eight cells; explicit power, floors, frame rule and cap. U supplies physical quantities, not a new sample-size preference. |
| eta(T), temperature and radius covariance incomplete | RESOLVED IN MODEL; MEASUREMENTS DEFERRED TO U | Full primitive map and shared/block/cell covariance in §16; no inference that eta/a leave Route A. |
| Matrix square-root conditioning / degeneracy conflation | RESOLVED | SPD envelope, kappa<=100, stable Cholesky computation and intrinsic matrix geometry; repeated positive eigenvalues allowed. Numerical realization verified later. |
| Observation noise/blur unresolved | RESOLVED IN DESIGN; CALIBRATION DEFERRED TO U | Explicit independent Gaussian localization plus known exposure kernel selected now, with bounded residuals; no outcome-dependent model choice. V tests the full law. |

“Deferred” in this table names measurements or validation that belong to later authorized
stages, not an unselected T scientific option. Failure of those qualifications stops
progress; their future success is not presumed.

## 28. U-stage handoff — independent physical qualification

**U IS BLOCKED PENDING T12 CLEARANCE AND SEPARATE AUTHORIZATION. It has not begun.**
The deliverable should establish, with raw provenance and uncertainty:

1. Feasibility of all four nominal fields, two preparations and the stipulated temporal
   resolution; actual force-displacement calibration, no equilibrium-fluctuation
   stiffness route, calibrated thermometry and its spatial/time stability.
2. Positive eta(T) and radius, viscosity law and covariance with the same thermometer,
   fluid/wall applicability, velocity/displacement standards, full geometric transforms,
   force matrix, centre, and all shared/block/cell covariance.
3. Shutter kernel, localization covariance and its distribution, detector bandwidth,
   independent drift reference, coordinate error and digitization bounds; demonstrate
   the observation law without using beta=1 as a calibration identity.
4. Lateral support, negligible experiment-wide selection, axial elimination and the
   absence of imposed drive; independently qualified relaxation/bandwidth bounds and
   settling conditions. Passive B fluctuation fitting cannot supply A stiffness.
5. The precise parameter/uncertainty domain for V; auxiliary sampling laws, bounded
   errors and any finite-coverage regions. Check (T.24) and (T.29), instantiate (T.28),
   and lock the smallest qualifying fixed count under §22.3, or declare UNQUALIFIED.

No value of eta, bead radius, detector noise or calibration uncertainty is inferred here
from a convenient power calculation. A failed U qualification is a useful scientific
result about feasibility. It does not authorize weakening T endpoints. Actual physical
measurements must be separately authorized; this handoff is not their execution.

## 29. V-stage handoff — pre-execution statistical validation

**V HAS NOT BEGUN.** After cleared T and U, a separately authorized V task must freeze
an isolated reference implementation, all likelihood/information conventions, critical
calibration algorithm, nuisance envelope, numerical checks and independent seeds before
its calibration and validation. This is validation implementation for qualification;
production authority/driver adoption remains W's separate task.

Required outputs are finite-N bias and coverage for the actual MLE; positive-equivalence
size at every required boundary/envelope; the nonregular geometry/current confidence
construction; complete-pipeline power with all refusals included; the controls of §20.4;
robustness to qualified nuisance variation; and demonstrated behaviour when the model
is invalid. Include the shared calibration covariance and the physical eta(T)-T-radius
measurement map in the generated auxiliary data. The old diagonal stiffness perturbation
model is insufficient. Include actual exposure integration and detector error; exact
latent OU transitions alone do not validate a camera likelihood.

Validate near equal eigenvalues, near qualification boundaries, correlation/noise
effects, free-centre estimation, small residual systematics, omitted-drive/current
counterexamples and temperature-dependent errors. A noise-free ideal pivot check is a
useful unit reference, not a replacement for these cases. No “calibration-free” claim
is made merely because the old minimum-p surrogate is removed.

V must return **RELEASE / NON-RELEASE**, per-case binomial bounds and an honest account
of any uncovered nuisance region. Changing a calibrated threshold using held-out
validation outcomes invalidates that validation and needs a new reviewed procedure and
fresh validation. A failed power result does not grant permission to lengthen a
confirmatory record after seeing it. No V files, seeds or implementation are created
in this T task.

## 30. W-stage handoff — authority and production implementation

**W HAS NOT BEGUN.** After T12 and the separately reviewed physical/statistical
qualifications, W would need an explicit new authority pair, estimator/observation
contract, full decision and failure semantics, provenance/seed specification and
implementation verification. It must state precisely which old v4 rules are superseded
and which infrastructure is reused, preserving old identities for old artifacts.
The baseline §14.3 sign defect must be repaired before that authority freeze.
A new execution seal, any campaign and any real optical-trap experiment need their
own authorization; no inference from this report permits them.

Book 1 is unchanged. The supplied brief's editorial observations — malformed rendered
`r != 0` in Chapter 33, and 17 diagram assets versus 16 placed figures — are recorded
for later editorial repair only. They do not affect this experiment design and are
not repaired here. This task does not resume the broader book rewrite, a simulation
programme, or any nonequilibrium/economic stage.

## 31. T1–T11 formal disposition

| Item | Disposition | Completed scientific decision | Not claimed complete |
|---|---|---|---|
| T1 direct bridge | COMPLETE | Direct normalized density hypothesis; selected harmonic state-space realization | Universal density identification |
| T2 absolute beta=1 | COMPLETE | Positive log-scale equivalence at all eight cells | Measured beta or achieved equivalence |
| T3 cross-field beta | COMPLETE | Six within-block reference contrasts with full covariance | Empirical common denomination |
| T4 geometry | COMPLETE | Intrinsic log-shape and centre upper bounds, SPD/conditioning/refusal rules | Measured geometry or validated finite-N bounds |
| T5 equilibrium/reversibility | COMPLETE | Separate physical, stationarity and current gates; density-only outcome defined | Exact absence of every unobserved current |
| T6 estimators | COMPLETE | Actual likelihood estimator; exact ideal pivots and limitations derived | General unbiasedness or exact fitted-null law |
| T7 equivalence logic | COMPLETE | Model, population, estimator, test and finite-sample levels separated | Equality of non-equivalent procedures |
| T8 observation noise | COMPLETE | Explicit calibrated noise/exposure law and complete auxiliary uncertainty | Apparatus capability or completed calibration |
| T9 non-Gaussianity | COMPLETE | Diagnostic of this harmonic realization, not a universal theorem falsifier | Omnibus proof from a finite diagnostic family |
| T10 finite-N size | COMPLETE AS DESIGN | Error/coverage targets, nuisance envelope rule, independent calibration/validation, release criteria | Achieved size, Monte Carlo results or implementation |
| T11 sample size | COMPLETE AS DESIGN | 450,000 quadratic equivalents / 408,164 information per cell, two blocks, fixed count rule/cap and power/floor analysis | Physical acquisition duration without U inputs or achieved power |

**Human scientific decision required for this bounded T design: NONE.** T12 may find a
scientific gap and require revision. U may find the stated capabilities unattainable.
V may fail size, power or nuisance-envelope qualification. These are explicit gates,
not hidden assumptions of successful completion.

## 32. Verification record and final status

### 32.1 Static checks performed

The task began from a clean tree at `0fad60bfb8df919df24227756f8ef03480dad2e3` on
`codex/book-one-continuity`. The configured remote was inspected; the locally cached
`origin/gaussian/stage-a-environment` was
`dd0d6b0e5d370de1bda805e07215ea0be4d6d083`. No fetch or push was needed or performed;
this is not a claim about a newly queried remote server HEAD.

A SHA-256 snapshot of **2,988 existing tracked regular files** was taken before writing.
All were verified unchanged after the report was prepared. The new report lies outside
the analysis and execution identity preimages. Strict JSON parsing and literal AST
inspection reconstructed the existing 12-source analysis identity and 19-source
validation identity plus driver without importing or executing those modules. The
foundation bytes were compared with the frozen Git object and its metadata. The plan
and seal still say execution is unauthorized; the seal remains PRE_DRIVER with no
frozen expected execution identity, and no official validation-results directory exists.

**67 completed static assertions** covering deterministic arithmetic and rational/matrix
checks verified the inverse-chi-square
moment algebra, known-versus-fitted-centre degrees of freedom, the scalar-vs-geometry
counterexample, the stationary-current example, the positive primitive counterexample,
the correlation bound, information and power formulas, count table and calibration
floors. Normal probabilities are analytic design aids, not empirical results. All checks
were performed outside the production package. No scientific RNG, optimization on data,
model step, simulated trajectory, calibration run or campaign was used.

The full new-file diff and exact staged path were inspected, whitespace validation was
performed, and a local commit contains only this report. The containing commit's full
SHA is returned with the final delivery; it is not embedded self-referentially in its
own contents. Final existing-file hashes and identity results were checked again after
commit, with a clean worktree required.

### 32.2 Preserved identities

| Object | SHA-256 |
|---|---|
| Frozen foundation (49,098 bytes) | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Foundation metadata | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| Working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| R-stage report | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| S-MG report | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| S-stage anchor | `5b92fdf5749ee05db63f32320e2b34a10afa2c98ceaf2e7a996f78b2df60505f` |
| Existing E1a design | `25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6` |
| Existing contract | `d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4` |
| Existing plan JSON | `fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4` |
| Existing plan Markdown | `2d40781593c607de31e68f42e713641a97335e198ed3453bbe677e76682f0d93` |
| Existing seed map | `c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af` |
| Existing seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` |
| Existing analysis identity | `60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527` |
| Existing execution identity | `442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b` |

### 32.3 Final stage boundary

- T1–T11: minimal experiment **design complete**, independent T12 audit required.
- E1a-v4 preserved and paused; scientific authority unchanged.
- Baseline sign defect: non-blocking here, repair before W-stage authority freeze.
- U blocked pending T12 and separate authorization; U, V and W not begun.
- Book 1, code, old plans/contracts, seed map and seal unchanged.
- No scientific RNG, model trajectory, calibration, official campaign or physical
  optical-trap experiment run. Execution authorization remains false.
- Local commit only. **No push.**

**T1–T11 MINIMAL E1a EXPERIMENT DESIGN COMPLETE — T12 INDEPENDENT AUDIT REQUIRED.**
