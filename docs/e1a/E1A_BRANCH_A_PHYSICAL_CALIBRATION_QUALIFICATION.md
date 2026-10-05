# E1a Branch-A physical calibration and qualification specification

**Status: NON-CONTROLLING U-STAGE PHYSICAL CALIBRATION SPECIFICATION.**

| Programme item | Status |
|---|---|
| R / S-MG / S | CLEARED inputs; no theoretical reopening |
| T1–T12 | INDEPENDENTLY CLEARED, as reported in the commissioning brief |
| U1–U12 | COMPLETE AS SPECIFICATION; independent audit required |
| Physical calibration data | NOT COLLECTED |
| Apparatus qualification | NOT ESTABLISHED |
| V / W | NOT STARTED |
| Execution | NOT AUTHORISED; existing execution flags remain false |

Prepared on 2026-10-05 against repository commit
`ebcf2641fa2d8fe4ab95fef011e96fe53feeadc6`, branch `codex/book-one-continuity`.
This report specifies future measurements and decisions. It contains neither an actual
calibration packet nor a claim that an apparatus meets its requirements.

## 1. Executive result

Branch A will construct the potential through **controlled, externally driven
force–displacement calibration**, using a calibrated translating chamber, independently
measured fluid viscosity and actual bead radius, and a qualified finite-chamber
hydrodynamic resistance. A full two-dimensional mechanical fit supplies the stiffness
matrix and zero-force centre. Traceable local thermometry supplies the temperature in
`H = H_U/(k_B T)`. Coordinate, localization-noise and shutter calibrations are separate
measurement streams with a shared covariance ledger.

The selected route retains Stokes drag only inside its measured domain. It does not
assume an infinite liquid, a perfectly spherical bead, a correct nominal temperature,
or an exact stage-to-fluid velocity transfer. Hydrodynamic memory is a particular
qualification risk: static drag calibration alone does not establish the temporal
Gaussian model required by T. Independently driven response measurements must qualify
that approximation over the observation bandwidth; otherwise the apparatus is refused
for this design.

The result is a complete **conditional specification**, not achieved physical
qualification. It fixes the method, estimator, dependencies, decision functionals,
packet contents and lock order. Instrument serial numbers, measured values, certified
ranges and attainable uncertainties are mandatory future inputs, not values invented
here. All physical acceptance tests remain unevaluated until those inputs exist.
There is no identified missing T field definition and no new scientific decision is
required. The role checks below are consequences of T's existing tolerances; they do
not authorize replacing T's nominal fields or changing its power claims.

For the EBU programme, the purpose is concrete: the mechanical energy landscape is
constructed without learning its scale from the distribution used to test it. A
successful later comparison can therefore inform the thermal-normalization claim.
A calibration refusal instead identifies a measurement limitation. It establishes
neither a failure of the equilibrium theorem nor a result about social mechanisms.

## 2. Authority and provenance

Authority remains frozen foundation, then working baseline, then stage reports within
their explicitly cleared scope. The controlling scientific inputs are:

- [Frozen physical foundation](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md)
  and its freeze metadata. The canonical bytes match the frozen source at
  `c63d6833da10a75ef66db11f99fb5b5c68d94c5e`; the older candidate wording in its header
  does not override the verified freeze metadata.
- [Working theory baseline](../theory/EBU_THEORY_BASELINE.md), particularly §§14.1–14.3.
- [R-stage reconstruction](../theory/EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md),
  [S-MG continuity](../theory/EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md) where applicable to the
  hierarchy, and [S-stage anchor](../theory/EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md).
- [T-stage experiment design](E1A_MINIMAL_EQUILIBRIUM_EXPERIMENT_DESIGN.md), committed
  at the starting SHA. T12 clearance is an explicit input of the user's U brief;
  this report does not invent a separately committed T12 audit document.

The current branch has no `docs/scientific_record/` directory. Its absence is already
reconstructed in R; no record from another branch is silently promoted into this one.
Repository guidance and the committed prospective design, contract, validation plans,
seal, calibration/field-authority reports and implementation were inspected. The old
E1a-v4 track remains paused. In particular, this report uses the correction in the
[calibration-package binding addendum](E1A_V4_CALIBRATION_PACKAGE_BINDING_RECONSTRUCTION_ADDENDUM.md),
not the unsupported distinct-contract-digest claim in the earlier reconstruction.

The baseline's ordinary post-minus-pre `Delta J` wording is a known defect: for
`E = V(pre)-V(post)` and `J_prob=V`, ordinary `Delta J_prob=-E`. It is non-blocking for
this calibration specification and must be repaired before W. No baseline edit is
made. No actor balance, transaction price, repricing rule or social-efficiency claim
is inferred from the physical calibration.

Selected SHA-256 identities, measured directly at the start:

| Object | SHA-256 |
|---|---|
| Foundation, 49,098 bytes | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Foundation metadata | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| Working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| T report | `1f613f93dd5c6eda10fdc8b15e1b7ba72e9fde7d68f8166062fbf81b896db326` |
| Existing prospective design | `25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6` |
| Existing contract | `d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4` |
| Existing validation plan JSON | `fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4` |
| Existing validation plan Markdown | `2d40781593c607de31e68f42e713641a97335e198ed3453bbe677e76682f0d93` |
| Existing seed map | `c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af` |
| Existing execution seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` |
| Reconstructed analysis identity | `60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527` |
| Reconstructed execution identity | `442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b` |

External sources cited below supply physical or metrological evidence only. They
cannot change EBU authority, T's likelihood, tolerances, sample targets or execution
status. Formulae and acceptance rules identified as U derivations are this report's
prospective specification, not claims copied from those papers.

## 3. Fixed T-stage handoff

The following are immutable inputs, not recommendations:

| Item | Fixed T requirement |
|---|---|
| Design | Four fields, two separately prepared blocks, eight records |
| Nominal theta0 | `(100,100)` micro-newtons/metre, 298 K, circular |
| Nominal theta1 | `(210,210)` micro-newtons/metre, 298 K, circular |
| Nominal theta2 | `(150,60)` micro-newtons/metre, 298 K, 30-degree ellipse |
| Nominal theta3 | `(100,100)` micro-newtons/metre, 318 K, circular |
| Scale equivalence | Every absolute beta in `[1/1.05,1.05]`; all six within-block reference contrasts in `[1/1.02,1.02]` |
| Calibration floors | Standard uncertainty in each log beta at most 0.009; in each log-beta contrast at most 0.003 |
| Residual error | Jointly certified absolute and contrast log-bias bounds each at most 0.0005 |
| Shape / centre | Shape upper bound below `ln(1.05)`; centre upper bound below 0.1 thermal units |
| Geometry | Full 99.9% A region SPD; `kappa_2(H)<=100`; Cholesky backward error at most `1e-10` |
| Thermal / curvature drift | Within-record `abs(Delta ln T)<=0.001` and normalized-curvature operator-log change at most 0.002; also satisfy stricter propagated bias budget |
| Reversibility | Independent physical conditions plus current upper bound `r_irr<0.02`; T's stationarity and lag checks retained |
| Information | At least 450,000 independent quadratic-observation equivalents and conditional efficient information at least 408,164 for log beta in each record |
| Observation | Full temporal Gaussian likelihood, exact qualified shutter integration, independent calibrated localization covariance; no thinning |
| Timing | `Delta=min(120 microseconds,tau_f/5)`; exposure at most `0.1 tau_f` |
| Count | Smallest qualifying integer in `[N_0,2N_0]`, `N_0=ceil(450000 coth(Delta/tau_s))`; also satisfy T.29 |
| Settling | Independent mechanical/thermal settling, then at least `20 tau_s` burn-in under T's bounded initial displacement and second-moment conditions |

Here `tau_f` is an independently qualified lower bound on the fastest relaxation time;
`tau_s` is an upper bound on the slowest. The sampling interval must also meet T's
independently qualified non-alias band `||B|| Delta<=0.2`, with B the whitened drift,
not a stream label in that formula. Actual shutter/noise and drift information, rather
than an ideal count alone, decide qualification.

The 0.009 and 0.003 numbers are **standard uncertainties**, not expanded uncertainties,
99.9% interval half-widths, or per-primitive allowances. T's finite-calibration critical
ceiling 2.10, auxiliary noncoverage accounting and complete-pass validation remain
unchanged. A component that consumes the full allowance leaves no allowance for other
components. Later V must validate the actual auxiliary law, finite-N intervals and
power. U does not substitute a Gaussian planning calculation for that validation.

## 4. Calibration independence architecture

Every input has exactly one acquisition-stream label and may name shared standards:

| Stream | Permitted content | Boundary |
|---|---|---|
| BRANCH A CALIBRATION | Driven force/displacement records; viscometry; bead metrology; local thermometry; geometry and physical qualification | No passive B density, covariance, stiffness fit, beta or current result |
| OBSERVATION-INSTRUMENT CALIBRATION | Immobilized targets, calibrated detector motion, timing pulses, shutter and localization measurements | No extraction of noise by subtracting a predicted thermal variance from B |
| BRANCH B PASSIVE OBSERVATION | Subsequent undriven time series and free characterization | Cannot update A's potential or choose its measurement method |
| SHARED METROLOGY STANDARD | Traceable length, time, temperature, viscosity, wavelength and optical references | Shared identity and covariance retained; not counted once per record as independent |

A deliberately driven bead is allowed as an A measurement. The mean displacement
under a known external force, measured in repeated balanced probes, estimates a
mechanical response. Its fluctuations may determine the uncertainty of that driven
mean, with their temporal correlation accounted for. They may not determine stiffness
through equipartition, a passive power spectrum, a corner frequency or `k_B T/S`.
Separate driven tracer measurements may establish flow transfer without assigning a
thermal diffusion constant as a force standard.

A's mechanical estimator never receives a B trajectory or B summary. B's free-density
and dynamical characterization receives observation calibration and coordinate
conversion but not A's H or V. The comparison layer accesses both only after their
separate outputs are frozen. Physical parameters can be statistically dependent
because they share instruments; independence here means independence of **scientific
construction**, not a false diagonal covariance assumption.

## 5. Physical field and record architecture

Use one sealed, temperature-controlled chamber per preparation, a trapped nonporous
microsphere, independently observed chamber geometry, two-dimensional stage translation
and a common physical coordinate frame. The working liquid must be homogeneous,
Newtonian and compatible with the selected fluorescence thermometer. The spherical
hydrodynamic boundary must be qualified. The exact liquid recipe, bead material,
nominal size, dye concentration, chamber dimensions and instrument models are apparatus
inputs to a **pre-A acquisition manifest**. They are not established by this report.
A manifest names one realization of this route; no menu of calibration estimators
remains available after B. Reject a material incompatible with any of these conditions.

These apparatus choices do not change the four scientific field targets. They must
be fixed before acquiring the packet's calibration records. Failed A qualification
may lead to a newly identified preparation and a complete new pre-B packet; it cannot
license selecting among packets after inspecting B. All failed preparations and their
reason codes remain in the acquisition ledger.

For each block b and field j, construct actual measured quantities

\[
U_{bj}(x)-U_{bj}(x^*_{bj})=\tfrac12 q^T K_{bj}q,
\quad q=x-x^*_{bj},\quad K_{bj}=H_{U,bj},
\]
\[
H_{bj}=\frac{K_{bj}}{k_BT_{bj}},\qquad
V_{bj}(x)=\tfrac12 q^T H_{bj}q. \tag{U.1}
\]

K has units N/m = J/m², H has units m⁻², and V is dimensionless. An arbitrary energy
zero does not affect V; no absolute U zero is claimed. The declared model is a full
rank two-dimensional affine space with Lebesgue measure `dx_1 dx_2`. A nonsingular
coordinate change carries its Jacobian; a nonlinear coordinate density is not silently
identified with the same Gaussian.

Finite camera support is an observation limitation, not a conditioning of the physical
law on survival. The complete T field-of-view tail requirement is retained. The axial
coordinate must be independently shown separable over the qualified range, or its
independently determined potential of mean force must satisfy the same harmonic model.
Simply dropping a coupled axial coordinate is invalid. Neither a camera crop nor a
wall is an EBU conservation constraint.

## 6. Candidate physical calibration routes

| Route | Independence and metrological burden | Disposition |
|---|---|---|
| Driven Stokes force with independently measured viscosity/radius | External force scale; must establish wall, flow, slip, temperature and radius corrections | **Selected**, with full qualifications below |
| Calibrated electrostatic or magnetic forcing | Independent in principle; requires bead charge or moment, field map, environmental and possible heating corrections | Not selected; adds unestablished force standards |
| Direct photon-momentum force measurement | Independent in principle; demands collection of outgoing momentum and detector/aperture calibration in this apparatus | Not selected; no such apparatus or accuracy established here |
| Optical electromagnetic calculation alone | Depends strongly on refractive index, beam structure, aberrations and collection geometry | Not selected as primary force standard |
| Passive equipartition, PSD/corner-frequency, equilibrium histogram fitting | Uses precisely the thermal relation being tested | Forbidden for A, including an ostensibly separate fit to the same passive B record |

The comparison selects a measurement route, not a claimed performance winner for all
laboratories. Controlled drag is minimal because it uses independently accessible
length, time, viscosity and geometry quantities and exposes their covariance. A primary
demonstration of stage-imposed flow and drag calibration is
[Ghoddoosi Dehnavi et al. (2020)](https://link.springer.com/article/10.1007/s00348-020-03031-4).
Its achieved performance is not imported as the accuracy of an EBU apparatus, nor is
its particular estimator adopted.

## 7. Selected mechanical calibration

Translate the whole closed chamber at independently calibrated velocities while the
trap remains fixed in the laboratory frame. In a qualified steady plateau, with
fluid velocity at the bead `v_rel` relative to the mean bead velocity, force balance is

\[
F_{\rm ext}=\Gamma v_{\rm rel},\qquad
F_{\rm trap}=-K(x-x^*),\qquad
K(x-x^*)=\Gamma v_{\rm rel}. \tag{U.2}
\]

The sign is fixed by this convention. Reversing chamber velocity must reverse the
induced displacement. Gamma is the positive definite hydrodynamic resistance tensor,
not necessarily a scalar. Its frame is the same physical frame as K and x. The force
is inferred from measured fluid-relative motion, not from an unverified stage command.

Measure stage motion by a calibrated interferometric encoder. Establish its vector
transfer to chamber walls and local fluid using independent driven tracer advection,
with known coordinate/time calibration, and the finite-chamber flow model. Use tracer
**mean advection**, not its equilibrium variance or an Einstein-relation diffusion
estimate. Remove those flow tracers from the test volume or include their independently
bounded interactions. Account for ramps, chamber compliance and flow settling; only
predeclared steady plateaux enter the static force fit. A's recorded bead displacement
can be nonzero, and its true force need not align with either camera axis.

Measure the zero-velocity background flow before and after each drive cycle. A material
uncontrolled background force invalidates zero-force-centre inference and the passive
record. Averaging opposite velocities cancels some odd/even artefacts but does not
prove absence of background flow or nonconservative forces.

The future acquisition manifest fixes drive amplitudes, durations, repetitions and
maximum A acquisition before B. They follow the A-only pilot rule in §13. Calibrations
use the actual illumination, axial height, bead, liquid, optical field and detection
settings associated with each future passive record. A transfer across changed
settings requires the explicitly measured transfer covariance and bias bound; a
nominally identical setting is insufficient.

## 8. Hydrodynamic scope

The base coefficient is `gamma_0=6 pi eta a`. Use

\[
\Gamma=6\pi\eta(T)a\,C(g,\chi), \tag{U.3}
\]

where the dimensionless symmetric resistance correction C depends on measured chamber
geometry g and qualified boundary/shape parameters chi. No default `C=I` is allowed.
A full finite-chamber Stokes solution with verified numerical error and boundary inputs
is the selected correction model. A controlled asymptotic reduction is acceptable
only when its remainder is bounded below the **joint** residual-error allowance.
This is a model-calculation requirement for a later stage, not an instruction to run
hydrodynamic simulations in U. In the chamber frame solve incompressible creeping
flow, `div u=0` and `-grad p+div[eta(grad u+grad u^T)]=0`, with the measured no-slip
walls at rest and prescribed bead translation. Surface-traction integrals define
the resistance columns. Include measured slip or shape only through the separately
qualified boundary model. A pressure/mean-flow disturbance needs its own measured
input; it cannot be absorbed into a free resistance scale. Certify discretization,
domain and boundary errors against the downstream endpoint budget. This defines
the physical calculation without choosing an unverified approximation by convenience.

| Effect | Required treatment |
|---|---|
| Distances to both faces and lateral walls, bead height, wall tilt | MUST MEASURE; MUST MODEL tensor resistance and its position dependence |
| Finite chamber, transfer from wall motion to local flow | MUST MODEL and independently qualify with driven measurements |
| Sphericity, porosity, surface layer, rotational coupling | MUST MEASURE or bound; effective optical radius alone does not establish hydrodynamic radius |
| Slip or uncertain surface boundary | INVALID IF UNCONTROLLED; model only with independently bounded slip parameters |
| Distribution of bead sizes | MUST MEASURE the actual bead; batch spread is not its measurement uncertainty |
| Liquid composition, concentration, ageing and evaporation | MUST MEASURE/control; viscosity sample must represent the chamber liquid |
| Mean flow, convection, thermophoresis | INVALID IF UNCONTROLLED; bound contributions to force, centre and reversibility |
| Finite Reynolds number | NEGLIGIBLE WITH BOUND or MUST MODEL; evaluate from measured maximum drive, a, density and viscosity |
| Fluid/bead inertia and hydrodynamic memory | MUST QUALIFY by driven response across the observation band; INVALID if incompatible with T's retained temporal law |
| Inter-particle hydrodynamic interaction | Exclude other mobile beads from the qualified volume or establish a negligible bound |

For illustration of scale, the parallel mobility at one no-slip plane has the familiar
Faxén expansion, with u=a/h,

\[
\frac{\gamma_0}{\gamma_\parallel}
=1-\frac9{16}u+\frac18u^3-\frac{45}{256}u^4-\frac1{16}u^5+\cdots . \tag{U.4}
\]

Using just the displayed terms gives approximately 5.948% additional drag at h=10a and
0.566% at h=100a. These are deterministic magnitude illustrations, not certified
corrections for a two-wall chamber. Even a distant wall can matter at the required
precision. Do not add two first-order corrections and call their omitted cross terms
zero. [Dufresne, Altman and Grier (2001)](https://physics.nyu.edu/grierlab/publication/dufresne01/)
studies two-wall confinement; its diffusion measurements are physical evidence for
wall effects, not the calibration route used here.

For each modeled correction, retain both parameter uncertainty and a separately
bounded approximation error. If a physical bound cannot be established over the entire
operating volume and bandwidth, return HYDRODYNAMIC_MODEL_UNQUALIFIED. Small Reynolds
number alone does not establish negligible hydrodynamic memory.

## 9. Viscosity

**Selected method: traceable capillary viscometry of the actual working-liquid batch,
with independently measured density, at controlled temperatures spanning both fields.**
The calibrated capillary measures kinematic viscosity; dynamic viscosity is

\[
\nu=f_{\rm cap}(t_{\rm efflux},c_{\rm cap},\text{corrections}),
\qquad \eta=\rho\nu. \tag{U.5}
\]

Use the instrument's certified efflux-time formula, kinetic-energy/end corrections,
valid flow/time ranges and uncertainty. Do not replace that certificate with an
invented universal correction formula. The [NBS capillary-viscometry monograph](https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph55.pdf)
provides the measurement basis; its historical liquid constants are not current EBU
calibration values.

Use sealed aliquots from the actual preparation, including any thermometric dye,
salts or additives. Record batch, preparation masses, contamination/evaporation controls,
pressure, sample custody and before/after composition checks. Independently measure
density with a calibrated densimeter at matching temperatures. A supplier viscosity
for a nominally similar liquid is insufficient. A Newtonian qualification covers the
capillary shear range and the bead's drive range; a shear-dependent material is outside
this route unless its departure is independently negligible within the error budget.

The fixed prospective temperature grid is 293 K through 323 K in 1 K steps, including
298 and 318 K. At each node collect at least five efflux readings in each of an
ascending and descending temperature sweep after independent thermal equilibration;
retain every reading and the sweep order. A dedicated pre-A pilot sets longer fixed
averaging if needed; repeated acquisition after B to obtain a better calibration is
forbidden. Paired heating/cooling discrepancies enter the model or refusal, not selective
removal of one sweep. Reference-liquid checks bracket each sweep.

Fit **log viscosity with linear interpolation between measured temperature nodes**.
Store the entire vector of node estimates and its full covariance, density uncertainty,
shared capillary constants and thermometer errors. This fixes the interpolation method
before B and preserves positivity. A separately justified bound M_2 on the second
T derivative of log viscosity gives the interpolation remainder
`M_2 (1 K)^2/8`. Establish that bound from a qualified constitutive description and
independent midpoint measurements; midpoint agreement alone is not a proof between
samples. Measure the half-Kelvin nodes for this validation with the same retained
replication rule. Include the derivative/model bound in the residual-error set. If
this grid plus its bound cannot meet the joint budget, this realization is unqualified;
no unreported choice of a smoother fit or wider uncertainty is permitted after B.

Actual temperatures and their uncertainty regions must lie inside the certified
measurement and interpolation domain. For local laser heating, evaluate viscosity
at the measured local temperature, not the controller setpoint. A spatially varying
viscosity requires the qualified flow model or a negligible spatial-effect bound.
For ordinary water, [IAPWS R12-08](https://www.iapws.org/relguide/viscosity.html) is an
independent reference check with its own state-dependent uncertainty and composition
scope; it is not a substitute for measuring the actual dyed or mixed liquid.

The packet contains finite, strictly positive eta values, units Pa s, admissible T and
pressure ranges, measured composition range, capillary validity limits, all model
coefficients and sources of covariance. A positive number outside these domains is
invalid. No arbitrary machine-epsilon threshold is used as a physical viscosity bound.

## 10. Bead radius

**Selected method: per-bead in-situ quantitative holographic microscopy with a
Lorenz–Mie optical model, traceable wavelength/length calibration and independently
qualified refractive-index and aberration inputs.** Measure the actual trapped bead
used in each block. A batch certificate is a provenance and comparison input, not the
primary estimate of that bead's radius.

Acquire through-focus holograms at independently registered positions and illumination
levels in the selected model's certified range; fit all retained images jointly for
radius, refractive index, centre and optical nuisances. Calibrate and bracket the optical
system with dimensionally certified reference spheres. Freeze fit region, background
handling, optical model, aberration parameters, rejection rules and uncertainty method
in the pre-A instrument procedure. The pilot establishes a fixed sufficient image
count and range before the eight record packets are acquired; it cannot select a
favourable fit from B.

[Lee et al. (2007)](https://www.physics.nyu.edu/grierlab/publication/lee07a/)
demonstrates simultaneous holographic size and refractive-index measurement, reporting
approximately 1% single-image accuracy for those quantities. That does not establish
the tighter absolute or differential accuracy sought in the illustrative budget here. Increased image count reduces repeatability noise, not a shared
length, refractive-index or model bias.

Inspect sphericity and surface-layer/porosity compatibility independently. Optical
radius becomes the hydrodynamic no-slip radius only under a qualified material and
boundary model. Otherwise include a separately measured optical-to-hydrodynamic
conversion with covariance and bounded model remainder, or refuse the specimen.
A fitted effective sphere for an irregular particle is not sufficient.

Use one identified bead across all four fields within a block and a new bead in the
other block. Measure radius before and after the field sequence, including the
298-to-318 K thermal excursion. Use direct per-field-temperature holographic
measurements as the selected route, retaining their common scale/model covariance. A measured expansion coefficient
can explain and cross-check the differences, but does not replace these measurements
or impose zero expansion. Thus the 318 K field never silently inherits the 298 K
radius. Keep all before/after comparisons as stability checks, not an invitation
to select the radius estimate giving a preferred result.

Covariance separates shared optical scale/model errors, shared material expansion,
block-specific bead radius and repeat-image error. Manufacturing dispersion describes
how two actual beads can differ. After per-bead measurement it must not be added again
as an independent uncertainty in that same bead's measured radius. Require a finite
strictly positive radius, a valid imaging/model range, a separately qualified material
boundary and a complete uncertainty law. Their absence cannot be hidden by a finite
positive product `eta*a`.

## 11. Drag coefficient and numerical validity

For scalar unbounded reference drag,

\[
d\log\gamma_0=d\log\eta+d\log a,
\]
\[
u^2(\log\gamma_0)=u^2(\log\eta)+u^2(\log a)
+2\operatorname{Cov}(\log\eta,\log a). \tag{U.6}
\]

The leading `u` on the left denotes standard uncertainty, not kinematic viscosity.
For the actual tensor, differentiate all of (U.3): radius also enters wall ratios,
slip/shape factors and local flow. There is generally no justified independent scalar
uncertainty for each eigenmode. A common input shared between Gamma and K is represented
once, preserving cancellations and correlations.

Dimensional checks are explicit: `[eta]=kg m^-1 s^-1`, `[a]=m`,
`[Gamma]=kg s^-1=N s/m`, `[Gamma v]=N`, and `[Gamma/K]=s` in a scalar mode.
Check units before evaluating a formula. Named SI units and conversion factors are
part of the packet's semantic content; an unlabelled `0.89` is not a viscosity.

Validation has three different layers:

1. **Physical primitives:** real numeric measurements, not booleans/strings; finite and
   strictly positive eta, a and T; correctly dimensioned; entire required uncertainty
   domain inside independently certified physical ranges.
2. **Physical derivation:** qualified fluid/boundary model; Gamma symmetric positive
   definite and finite over its domain; K and H satisfy the complete geometry tests.
3. **Numerical representation:** checked multiplication/division and eigenvalue bounds;
   finite positive representable gamma, relaxation times and scale factors; bounded
   roundoff and no overflow, underflow-to-zero or invalid covariance factorization.

These checks precede every publication and lock, including control paths that bypass
statistical calibration. A tiny positive primitive may be physically outside its
certificate, numerically unrepresentable after multiplication, or both; the reason
codes distinguish these failures. A numerical lower bound is precision/representation
specific, never an invented physical admissibility threshold. Log-domain diagnostics
may detect the issue but cannot turn an unusable downstream gamma into a valid value.

## 12. Force/displacement tensor calibration

For probe r, fit the vector relation

\[
F_r=Kx_r+c,\qquad c=-Kx^*. \tag{U.7}
\]

A symmetric two-dimensional K has three components; c has two. Three noncollinear
exact points can identify them algebraically, but provide inadequate checks. The
selected overdetermined design has four physical directions (0, 45, 90 and 135 degrees),
both signs and three nonzero amplitude levels: **24 driven plateaux**, plus a
zero-velocity reference before and after each directional group. Repeat the full
cycle at least three times, with the direction/amplitude order reversed on alternate
cycles. The final number of complete cycles is fixed by the independent pilot and
recorded before production A measurements. No single-axis reduction is allowed for
theta2, and circular target fields still receive the full tensor measurement.

The pilot maps commanded velocity to physical displacement; frozen production drives
must cover the prescribed spatial domain in §13. Directions refer to the calibrated
laboratory basis, not raw camera pixels. Record both components of actual velocity,
force and displacement with timing. Retain force/displacement cross-covariance when
the same coordinate, clock or reference enters both.

Use a **joint errors-in-variables likelihood**, with latent true plateau positions
and velocities and the measurement model for their noisy observations. Its physical
constraint is (U.7) with `F_r=Gamma(phi) v_r`. Estimate the primitive parameters,
latent nuisance quantities, K and c jointly or with an algebraically equivalent
profile likelihood. The Gaussian measurement-law case minimizes the joint quadratic
residual using the full covariance plus its log determinant when parameter dependent.
Shared calibration variables enter once as auxiliary observations. Ignoring errors
in displacement or regressing noisy displacement as exact generally biases K.

Retain the full covariance of `(K_11,K_12,K_22,c_1,c_2)` and all correlations with
thermometry, drag, coordinates and observation calibration. Account for temporal
correlation of driven plateau means; use their independently estimated mean-covariance
law and degrees of freedom, not one independent sample per camera frame. A normal
auxiliary law requires measurement evidence and finite-sample justification. If it
is inadequate, its actual independently calibrated law must be carried into V; no
silent independent Gaussian replacement is allowed.

First fit an unrestricted 2-by-2 response matrix as a conservativity diagnostic.
Its antisymmetric component, closed-loop work and amplitude-dependent residuals must
be bounded, not erased by imposing symmetry. The physical symmetric fit is accepted
only after the conservativity and harmonic-model qualification. An uncertain negative
eigenvalue is not repaired by clipping or nearest-SPD projection. Information-matrix
or profile curvature calculations supply candidate covariance; the actual auxiliary
coverage and estimator behaviour are later V responsibilities.

## 13. Harmonic linearity and force range

The mechanical pilot uses only controlled A drives to obtain a coarse stiffness,
centre and flow transfer. It then fixes the production amplitudes to cover the
independently predicted observation domain. For a dimensionless ellipsoid
`q^T H q<=R^2`, choose three target radii `R/3`, `2R/3`, R in each of §12's directions,
translated into velocity commands using the pilot response. The measured production
positions, not the commands, must cover that domain with propagated placement error.
The same deterministic rule applies to every field. No observed B thermal width or
B fit sets an amplitude.

Choose R prospectively from the complete T acquisition envelope, the smallest beta
in its design/power range, coordinate/noise uncertainty, and the whole-campaign
field-of-view/escape budget. For instantaneous d=2 Gaussian positions a useful
point-observation bound is

\[
\Pr(q^THq>R^2)=e^{-\beta R^2/2},\qquad
M e^{-\beta_{\min}R^2/2}\le\alpha_{\rm tail}, \tag{U.8}
\]

where M is the total scheduled observation count across eight records. This union
bound needs no independence of frames. It is **not** a continuous-path bound between
frames. The later qualification must also bound excursions during exposures, shutter
integration and burn-in using the qualified continuous-time model and a certified
crossing bound. Combined clipping/tail allocations must meet T's whole-record
`1e-4` field-of-view requirement and fit its invalid-record allocation. If the
required domain cannot be covered by mechanical and optical qualification, refuse;
never crop to the region that looked Gaussian in B.

Fit linear and independently specified polynomial residuals through cubic force order
on the retained drive data. Include offset, quadratic and cubic vector terms, not just
a change of scalar slope. Inspect signed residuals, force-loop work, reversal/hysteresis,
spatial dependence and repeat cycles. Establish a uniform force/Hessian remainder
bound over the ellipsoid from a qualified optical-force smoothness model plus the
measurements. Finite points alone cannot certify the unsampled interior; inability
to bound it is HARMONIC_DOMAIN_UNQUALIFIED.

For a nonlinear force law, force balance concerns the **mean force**, not generally
the force evaluated at the mean position. In the polynomial qualification fit use
`F_ext=sum_alpha B_alpha E_A[X^alpha]`, estimating these position moments from the
separate driven A observations with independently calibrated detector corrections
and their joint uncertainty. Do not substitute an assumed equilibrium thermal width
or `beta=1` to make this averaging correction. For the accepted linear model the
identity reduces exactly to (U.7) with the plateau mean. Position-dependent Gamma
or fluid velocity similarly requires the measured averaged force or a certified
bound, not an unexamined product of means. Unresolved fluctuation-averaging error
belongs to the harmonic/hydrodynamic refusal and residual budget.

Translate the force remainder into potential and geometry errors. If
`F_trap=-Kq+r(q)`, `r(0)=0`, and in thermal coordinates
`||H^(-1/2) D r H^(-1/2)/(k_B T)||<=epsilon_K`, then the symmetric conservative
part gives

\[
|\delta V(q)-\delta V(0)|\le \tfrac12\epsilon_K q^T H q. \tag{U.9}
\]

This follows by integrating the gradient along the segment from the centre, provided
the bound covers that segment and the residual is conservative. An antisymmetric
force has no scalar-potential repair; it must be negligible under the physical
reversibility and error gates or cause refusal. Map the allowed residual set through
the actual T likelihood and geometry gates (§25); do not equate a 5% force residual
with the much smaller 0.0005 log-scale bias allowance.

All nonlinear, drift, wall, optical and numerical residuals share that allowance.
One small component does not grant a separate full allowance to each other component.
The nominal harmonic model is retained only when the combined bounds qualify it.
A failed model check does not falsify a general equilibrium identity.

## 14. Trap centre

The A centre is the **zero-external-force intercept** of the driven mechanical fit,
transferred to the B observation frame through independently measured fiducials:

\[
x^*=-K^{-1}c,\qquad
dx^*=-K^{-1}(dc+dK\,x^*). \tag{U.10}
\]

Propagate the K–c covariance and all frame-transfer errors through this expression.
A sample mean from the later passive record is not the A centre. Nor does setting the
camera origin to zero establish a physical centre with zero uncertainty. Background
flow, axial coupling and beam drift enter the uncertainty or a refusal before centre
qualification.

Bracket the A sequence with independently observed trap/fiducial references and
continue the prescribed reference measurements during the later B acquisition.
A frozen transfer rule may correct measured apparatus drift; it may not use B's
mean to adjust A. Store both the original centre and the deterministic reference-based
transfer, with uncertainty and any induced temporal correlations.

The T centre test compares its free fitted B mean with this A centre. For planning,
the calibration covariance in thermal coordinates is
`H^(1/2) C_xstar H^(1/2)`, including the uncertainty in H and shared coordinate terms.
It joins B-mean and transfer covariance in T.29. If this floor makes the 0.1-thermal-unit
positive gate unattainable, more B frames cannot repair it. Equal eigenvalues in a
circular field do not make a centre undefined; only its arbitrary eigenvector angle
is unidentifiable.

## 15. Thermometry

**Selected method: calibrated platinum resistance thermometry for traceable bulk
anchors, plus independently calibrated fluorescence thermometry for the local trap
volume.** Use two resistance probes to resolve bulk gradients and drift, and a
rhodamine-B fluorescence intensity ratio against a reference-temperature image to map
local temperature. The exact dye concentration, illumination, spectral filters,
reference images and chemical environment belong to the pre-A manifest and the
calibration curve. Use the same working liquid in capillary and chamber measurements.

Calibrate the fluorescence response in that liquid against the resistance standards
across 293–323 K. Correct monitored excitation intensity, background, camera response,
concentration/bleaching and the reference-temperature dependence. Freeze the inversion
function and its range from these independent calibration measurements. Use spatially
registered maps at every actual trap power, ellipticity, axial height and ambient
setpoint. The thermometer measures a field `T(r,t)`, not only one controller number.
Bulk probes alone cannot rule out a localized optical hotspot.

The local estimate at the bead and over its qualified displacement volume includes
fluorescence point-spread averaging, axial resolution, bead-induced optical distortion,
finite spatial sampling and interpolation. A thermal transport model constrained by
those measurements must bound unresolved gradients and the bead–liquid temperature
difference. No extrapolated central value with an unbounded resolution error is valid.
Resistance-probe self-heating, thermodynamic-temperature conversion, heat conduction
along leads and measurement timing also enter the model.

[Ross, Gaitan and Locascio (2001)](https://www.nist.gov/publications/temperature-measurement-microfluidic-systems-using-temperature-dependent-fluorescent)
provides primary evidence for spatially resolved fluorescence thermometry, with reported
precision ranging from 0.03 to 3.5 degrees C depending on measurement conditions.
Those precision figures are not absolute-accuracy or unresolved-hotspot certificates
for this apparatus. The reference-temperature dependence in the
[Shah, Gaitan and Geist (2009) measurement equations](https://www.nist.gov/publications/generalized-temperature-measurement-equations-rhodamine-b-dye-solution-and-its)
must be respected. An intensity curve calibrated with one reference temperature
cannot simply be reused with another by relabelling the reference.

Acquire the maps under matched optical settings. Thermometric illumination must
remain identically configured during A and the future passive record, or its thermal
and mechanical perturbation must have an independently certified transfer bound.
Dye photophysics and probe illumination must not introduce an unaccounted force,
reaction, flow or time-varying reservoir. If a nonperturbing local measurement cannot
be qualified, the apparatus is unqualified; controller readings are not the fallback.

## 16. Temperature covariance and viscosity coupling

Represent temperature estimates by shared offset/gain and calibration-curve variables,
block probe-transfer variables, field-specific local-heating corrections and time-series
measurement errors. For example, the decomposition

\[
T_{bj}=f_T(r_{bj};\zeta_T)+\Delta T_{\rm local,bj}
\]

is a dependency statement, not a claim that its components are independent. The two
298 K preparations share reference standards while retaining independent chamber
preparation errors. Temperature difference precision can improve by common-mode
cancellation, but the calibration slope, local laser heating and interpolation errors
need not cancel between 298 and 318 K.

Let `ell_eta(T;zeta)=ln eta(T;zeta)` denote the measured interpolation model. For a
scalar mechanical mode, ignoring additional corrections only for this differential,

\[
d\log h=(\partial_T\ell_\eta-1/T)dT
+\partial_\zeta\ell_\eta\,d\zeta+d\log a
+d\log v-d\log q. \tag{U.11}
\]

Radius expansion, wall geometry and fluid transfer add their own derivatives. The
same T error appears in both viscosity and the denominator. Thus
`Cov(ln eta,T)=partial_T ell_eta Var(T)+partial_zeta ell_eta Cov(zeta,T)` locally,
with other shared terms as appropriate. Counting viscosity-temperature uncertainty
as independent and adding another thermometer error loses this dependency.

The viscosity calibration temperatures themselves use measured resistance readings
with shared reference offsets. Jointly fit/propagate those readings and future local
T values. A common temperature offset can cancel partly when evaluating a viscosity
curve calibrated on the same scale; the naive derivative term alone does not capture
that cancellation. Store the original temperature observations and joint fit, not
only a table of independent eta error bars.

For the direct thermal-normalization factor, `d ln T=dT/T`. For the complete mechanical
route its sensitivity is (U.11), often substantially larger. All temperature
requirements are therefore specified by projected endpoint uncertainty and bias,
not a universal decimal-place demand on a thermometer. The full 99.9% physical region
must stay in the fluorescence, capillary, material and single-reservoir domains.

## 17. Local heating, spatial gradients and stability

Map trap-off and trap-on local temperatures at the target settings, including theta1's
higher power. The increase in stiffness is not permission to assume equal local
viscosity or temperature. At theta3, adjust the ambient control to target a **local**
318 K, retaining the achieved value and uncertainty. The theta0 target is similarly
local 298 K. [Peterman, Gittes and Schmidt (2003)](https://research.vu.nl/en/publications/laser-induced-heating-in-optical-traps/)
shows that optical heating can affect trap calibration; no published temperature-rise
coefficient is substituted for a measured rise here.

Perform independent temperature and fiducial observations spanning the proposed record
duration, before the packet is locked, and maintain the declared monitors during
passive acquisition. Require T's within-record bounds on temperature and normalized
curvature. Additionally map their combined effect on the temporal likelihood, H,
centre and reference contrasts. A change within 0.001 in log T is not automatically
within the 0.0005 log-beta residual budget.

Temperature gradients can change local viscosity, produce convection or thermophoretic
forces, and invalidate a single thermal reservoir. Qualify the whole observation
volume with spatial bounds, measured chamber dimensions and a thermal/flow model.
Use independently driven/undriven reference-flow observations to bound background
advection; do not infer the absence of flow solely from a later B current estimate.
A post-acquisition monitor outside its frozen envelope invalidates the record. It
does not trigger a new fitted T(t) chosen to make beta constant.

After the 298-to-318 K change, demonstrate thermal and mechanical settling using the
independent monitors. Only then apply the fixed burn-in. Heating/cooling hysteresis
or irreversible bead/fluid changes require a new preparation or refusal, not pooling
with the preceding calibration. Uniform temperature within a certified error set is
an approximation qualification; a material gradient cannot be relabelled a uniform
reservoir by taking its spatial average.

## 18. Coordinate metrology

Define a right-handed physical laboratory frame in metres. Calibrate both stage axes
and camera mapping using an independently certified two-dimensional length grid and
interferometric stage displacements spanning the entire observation domain. Determine
x/y scale, shear/nonorthogonality, rotation, handedness, magnification, offset and
spatial distortion. A single scalar pixel size is insufficient. Bracket field changes
with fiducial checks and retain the full map covariance.

For an affine detector map `y=b+P x`, P maps physical coordinates to detector units.
The equivalent potential matrix is

\[
H_y=P^{-T}H_xP^{-1},\qquad
\Sigma_x=P^{-1}\Sigma_yP^{-T}. \tag{U.12}
\]

Force components transform as covectors: `F_y=P^{-T}F_x`, so work remains invariant.
Rotate both force and displacement to the same frame before fitting K. Clock and
encoder standards used in velocity are included in the same ledger. A length standard
shared by velocity, displacement and B coordinates may enter with different powers;
do not assume its beta sensitivity is either one or two without differentiating the
actual measurement chain.

Use an affine P in T's likelihood only when residual distortion across the retained
domain has a certified contribution within the combined model-error budget. A frozen
nonlinear image correction is permitted only with its induced observation/noise law
qualified as T requires. If material distortion makes the transformed noise
heteroscedastic or non-Gaussian, reject the T observation model; do not silently retain
an iid R after applying a nonlinear transformation.

Measure trap-axis orientation from the full mechanical matrix and map it into this
frame. The ellipse angle is defined modulo pi, with a fixed major-stiffness eigenvector
convention. Near a repeated eigenvalue its angle is undefined and must not acquire
an artificial tiny uncertainty; propagate matrix components or eigenspaces instead.
Circular fields remain valid full-rank geometries. Theta2 must have separately resolved
anisotropy and rotation as specified in §21.

## 19. Observation-instrument calibration

Retain T's model, with physical latent position X and detector output y:

\[
y_i=b_{\rm det}+P\int w_i(s)X(s)\,ds+\epsilon_i,
\quad \int w_i(s)ds=1,
\quad \epsilon_i\stackrel{\rm iid}{\sim}N(0,R_{\rm obs}). \tag{U.13}
\]

The camera calibration supplies b, P, the full 2-by-2 R, shutter kernels, timestamps
and their uncertainty. The independent-noise statement includes independence from
the latent motion after the qualified observation model. Exposure integration may
correlate transition and observation errors; V must use the exact augmented or
equivalent likelihood, not ordinary independent frame averages.

**Noise method:** observe immobilized beads/reference targets with the same image
formation, exposure, brightness, background, localization algorithm and relevant
field positions as the future bead. Independently driven calibrated targets qualify
tracking bias over the required motion and shutter range. Match or bracket the
actual photon/background range. Mechanical reference motion is measured separately;
immobilization does not entitle one to assign stage drift to white detector noise.
Estimate the full x/y noise covariance, temporal correlation envelope and distributional
shape from retained observations. Repeat across position, intensity, temperature and
settings; retain shared electronic/optical terms.

No `R = S_B - predicted thermal covariance`, passive PSD decomposition or fit of R to
make beta equal one is allowed. Material colored, state-dependent or non-Gaussian
localization error is OBSERVATION_MODEL_UNQUALIFIED under the fixed T model. A small
remaining discrepancy may enter the independently bounded residual set only with a
certified endpoint and coverage effect; a non-significant test alone is not a bound.
No colored-noise state is added silently to T's likelihood.

**Shutter/timing method:** use a traceable pulsed light source and photodiode/timebase
reference to measure exposure start, weighting kernel, duration, dead time, clock
drift/jitter and stage–camera synchronization. Determine rolling/global-shutter
behaviour explicitly. If row-dependent timing cannot be represented by the qualified
common position observation, refuse it. Retain uncertainty in w, P and R jointly.
The physical exposure must satisfy `t_exp<=0.1 tau_f`; the actual supported frame
interval must be rounded downward as T prescribes.

Across the complete beta/design envelope, require the largest normalized
localization-noise eigenvalue to be at most 0.05 and R PSD, P nonsingular, with
uncertainty. For the instantaneous signal this is the generalized covariance ratio
of R to `P Sigma_beta P^T`; exposure integration uses its actual signal covariance
in information calculations. Also bound the exposure-averaged noise ratio so a
blur reduction cannot hide inadequate signal; that ratio is recorded and propagated,
not assigned a new U tolerance. The full Fisher calculation remains
binding; an instantaneous ratio alone does not imply the assumed precision penalty.
Digitization, pixel locking, clipping, missing slots and saturation have the exact T
dispositions: every slot is accounted for; clipping invalidates; independent missingness
enters likelihood and
information; material binning requires a prospective redesign, not a post-B patch.

The methods are consistent with the observation issues treated by
[Berglund (2010), NIST](https://www.nist.gov/publications/statistics-camera-based-single-particle-tracking)
and the confined-motion treatment of [Calderon (2016)](https://arxiv.org/abs/1510.06062).
Neither source is a certificate that this camera has the required noise or bandwidth.

## 20. Relaxation-time qualification and T11 mapping

For qualified passive, conservative overdamped dynamics, the mechanical drift is
`A_phys=Gamma^-1 K`. Use the symmetric generalized-eigenvalue problem

\[
K v=\lambda\Gamma v,\qquad
L_\Gamma=\Gamma^{-1/2}K\Gamma^{-1/2},\qquad
\tau_r=1/\lambda_r(L_\Gamma). \tag{U.14}
\]

With isotropic drag this reduces to `tau_r=gamma/k_r`. For correlated calibration
variables take extrema over the full physical uncertainty region:

\[
\tau_f=\inf_{\phi\in\mathcal A}\,1/\lambda_{\max}(L_\Gamma),
\quad
\tau_s=\sup_{\phi\in\mathcal A}\,1/\lambda_{\min}(L_\Gamma). \tag{U.15}
\]

Additional qualified dynamic-model bounds enlarge these ranges. Do not sort stiffnesses
and relaxation times separately and lose their pairing. Every computed time and
confidence-domain bound must be finite and strictly positive, with sufficient numerical
accuracy. A zero or infinite time cannot be repaired by clipping.

There is an important dependency check. In a scalar steady drag fit,
`k=gamma v/q`, so `tau=gamma/k=q/v`. The common drag scale cancels from tau exactly
under that model, while it remains in H. In the tensor case, a directly measured
response `q=M v` gives `M=K^-1 Gamma` and `A_phys=M^-1`. Preserve this covariance;
adding independent gamma and k errors would destroy the cancellation. This identity
does not make the dynamic model correct at all frequencies.

Independently measure the **driven** frequency/step response in both axes. Static
chamber translation establishes the force scale; for the higher-frequency dynamic
check use independently calibrated optical trap-centre steering. This avoids assuming
that a macroscopic stage transfers its commanded velocity to the liquid at every
observation frequency. A calibrated steering/fiducial map and common timebase supply
the imposed centre displacement; qualify any accompanying stiffness/power change
within the same domain. For a centre displacement input, the retained model predicts
`X(omega)=(K+i omega Gamma)^-1 K Xstar(omega)`; for an independently known external
force the susceptibility is `(K+i omega Gamma)^-1`.

Use phase-locked response measurements, with independently timed exposure and at least
eight uniformly spaced phases per cycle. After the A-only pilot fixes tau bounds and
Delta, the production frequency set is DC plus logarithmically spaced angular
frequencies at four points per octave starting at `0.05/tau_s`, through `pi/Delta`,
including the two mechanical rates and the upper endpoint. Probe both independent
axes, both signs, at amplitudes inside the mechanically qualified range. The pilot
fixes the repeated-cycle count and plateau/settling durations before production A
measurements. Phase-locked equivalent-time measurements require qualified repeatability
and timing; they are not a claimed high-bandwidth capability of an untested camera.

The qualification also needs a certified physical bound on the higher-frequency tail
after exposure integration/sampling and a continuous residual envelope between probe
frequencies. A grid alone is not a proof. Propagate steering, shutter and phase
uncertainty and any inertial correction used to bound departures. No passive B corner
frequency or PSD is used for tau. If the steering map, frequency range or residual
bound cannot be qualified, the temporal model is unqualified for this apparatus.

For a liquid density rho, the scale `tau_nu=rho a^2/eta` warns about fluid-memory
effects; bead inertia introduces another time scale. For illustration only,
`rho=1000 kg/m^3`, `a=1 micrometre`, `eta=0.00089 Pa s` and `k=0.0001 N/m` give
`tau_nu about 1.12 microseconds`, `tau_k about 168 microseconds` and
`sqrt(tau_nu/tau_k) about 0.082`. This is neither a measured specimen nor a certified
beta bias. It shows why overdamped Markov behaviour cannot be assumed from the
static Stokes formula. [Franosch et al. (2011)](https://arxiv.org/abs/1106.6161)
provides direct physical evidence for hydrodynamic-memory effects.

Map the certified dynamic discrepancy to T's likelihood/gate error sets and the
complete residual budget. If it cannot fit, return TEMPORAL_MODEL_UNQUALIFIED; do
not introduce memory into the T estimator in U. Adjusting a later apparatus before
any B acquisition can be prospectively requalified, but changing the scientific
likelihood requires a T revision.

Once independent quantities exist, the deterministic handoff is exactly:

1. Form the joint envelope for H, Gamma, centre, drift band, P, R, w and their shared
   calibration variables. Its physical coverage and bounded errors are retained.
2. Compute finite positive tau bounds and the independent non-alias condition. Set
   the supported interval to the largest clock setting no greater than
   `min(120 microseconds,tau_f/5)`. Check exposure and continuous observation support.
3. Compute `N_0=ceil(450000 coth(Delta/tau_s))`. At candidate counts evaluate the
   exact expected Gaussian temporal information, profiling all T nuisance parameters.
4. Select the smallest integer `N_raw` in `[N_0,2N_0]` meeting the quadratic-equivalent
   target, the envelope infimum `I_logbeta.eff>=408164`, and T.29 for every positive
   gate. Use interval/global bounds, not an unchecked finite nuisance grid.
5. Freeze `D=N_raw Delta`, independent settling requirements, `20 tau_s` burn-in,
   initialization bounds, shutter, monitors and the complete slot schedule before B.
   If the finite search interval contains no qualifying count, refuse and return to T.

For Gaussian observation mean m and covariance C, deterministic information uses
`I_ab=m_a^T C^-1 m_b + (1/2) tr(C^-1 C_a C^-1 C_b)`; take the Schur complement for
centre and drift nuisance parameters. Calibration uncertainty remains auxiliary and
is not smuggled into extra conditional B information. T.29 uses the fixed risk
`0.025/32`, its fixed contrast ranks and the Minkowski sum of the two planning
ellipsoids and two copies of the bounded-error set. This requirement includes centre,
shape, quarter-stationarity and current precision. No actual count, duration or T.29
qualification is established by U because no actual packet exists. V must validate
finite-sample coverage/power before any adoption or experiment.

## 21. Field-by-field requirements and role preservation

Actual measured K, T and orientation determine V. Nominal targets define the intended
roles; one must not force actual measurements to equal them. Both blocks retain all
four targets in §3. The tests below are **necessary role checks derived from existing
T margins**, not new scientific tolerances around the nominal targets and not a
license to substitute a weaker experiment.

For every role, propagate the full A region and bounded errors, and apply the fixed
T11 information/positive-gate rule. An unresolved role is FIELD_ROLE_UNRESOLVED;
a confidently absent role is FIELD_ROLE_INVALID. Neither is an EBU theorem failure.
The actual acquisition manifest must continue to command T's nominal targets.
For a circular-role field, preserve circularity at T's existing shape resolution:
its scale-free distance to an isotropic stiffness is `G_circ=(1/2)ln kappa_2(K)`,
so require the joint upper bound on G_circ to be below `ln(1.05)`. This is the same
shape metric applied to role realization; it does not force measured eigenvalues
to agree or assert an exact physical degeneracy. The ellipse must instead resolve
its noncircular role by the lower-bound test below.

| Field | Physical requirement and role check |
|---|---|
| theta0 | Reference circular target at local 298 K; full tensor/centre calibration; no forced equality of measured eigenvalues |
| theta1 | Increased circular stiffness target at local 298 K; measure extra laser heating and actual stiffness ratio; no assumption that power ratio equals stiffness ratio |
| theta2 | Actual anisotropy and nonzero orientation relative to the calibrated axes resolved over the full A region; full off-diagonal stiffness covariance retained |
| theta3 | Circular target at actual local 318 K; separate local thermometry/viscosity and radius-transfer measurement; sufficient separation from theta0 |

**Temperature derivation.** Keeping the actual K but wrongly dividing it by the
reference T0 gives `H_wrong=(T3/T0) H_true` and hence
`beta_wrong=T0/T3`. Nominally `298/318=0.9371069182`, a 6.2893% decrease. To lie
strictly outside T's reciprocal 2% cross-field band, the actual ratio must satisfy

\[
\inf_{\mathcal A,\mathcal B}\log(T_3/T_0)>\log(1.02). \tag{U.16}
\]

At an exactly known T0=298 K, the strict point-value boundary is T3>303.96 K, a
separation greater than 5.96 K. With uncertainty, test the **joint ratio bound**,
not two nominal setpoints or a comparison of separately rounded confidence limits.
This is a role-separation boundary only. It does not replace the 318 K target, nor
claim T's planned power for an arbitrarily small excess beyond 2%. Finite-sample
sensitivity remains a V validation responsibility under the retained nominal design.

**Stiffness derivation.** At the same temperature, using the reference K0 in a truly
circular field with `K1=r K0` yields `beta_wrong=r`, not `1/r`. Thus the role needs
`inf log r>ln(1.02)` to put this omitted-stiffness perturbation outside the same
cross-field margin. With unequal realized temperatures, the mechanically isolated
failure mode still uses the actual T1 in both correct and wrong normalizations.
For nonscalar realized matrices, calculate the erroneous comparison through the full
likelihood; the ideal instantaneous Gaussian scale is
`beta_wrong=d/tr(K0 K1^-1)`, with shape failure retained separately. A scalar power
ratio must not conceal anisotropy. The nominal stiffness ratio is 2.1, far beyond
the role boundary; its realization has not been measured.

**Anisotropy and rotation derivation.** For a two-mode ellipse with ratio rho>1,
replacing its shape by an isotropic matrix leaves the scale-free log-shape distance
`G=(1/2)ln rho`. T's shape margin implies the necessary resolved-anisotropy condition
`inf rho>1.05^2=1.1025`. If the eigenvalues are correct but the ellipse is wrongly
left unrotated by an angle psi relative to its actual axes, the determinant-one
whitened comparison has

\[
G_{\rm rotation}=\operatorname{arcosh}\!\left[
1+\frac{(\rho-1)^2}{2\rho}\sin^2\psi\right]. \tag{U.17}
\]

The role requires the joint lower bound on this expression to exceed `ln(1.05)`.
At the nominal rho=2.5 and psi=30 degrees, G is approximately 0.470 (the exact
arithmetic is recorded in §36); the point-value minimum angle at rho=2.5 is about
2.95 degrees modulo the equivalent principal-axis conventions. These are derived
sensitivity boundaries, not a new acceptable angle target. Retain 30 degrees,
(150,60) micro-newtons/metre and T.29. Matrix-domain evaluation handles correlations
between rho, psi, axis mapping and temperature. A finite grid or an eigenvector
standard error at a degeneracy is insufficient.

T does not prescribe an additional universal manufacturing tolerance such as
“30 degrees plus/minus 5 degrees.” U does not invent one. Target settings, measured
realization, derived role resolution and full T qualification are separate fields
in the packet. Failure of a role leads to prospective apparatus correction before
B; an intentional change of a target or of a T power objective returns to T.

## 22. Two separately prepared blocks

Block 1 uses field order theta0, theta1, theta2, theta3. Block 2 uses theta3, theta2,
theta1, theta0, as fixed by T. Each block has a new individually identified bead,
freshly prepared liquid aliquot of the locked recipe, and newly assembled/cleaned
sample chamber with measured wall spacing and bead height. Re-seat and verify the
chamber and optical alignment; obtain an independent mechanical calibration and
local temperature/noise checks for every field. Returning the same unchanged chamber
to a saved setting and calling it a second preparation is insufficient.

The same microscope, encoder, camera, traceable standards and certified reference
materials may be reused, with their shared errors retained. Record fluid-preparation
mass measurements separately even if they use the same balance/reference. Retain
within-block same-bead dependencies and cross-block reference dependencies. Two
preparations do not imply eight independent calibrations.

The block is the independent physical preparation, not a random-effects distribution
estimated from only two points. Report both blocks separately and all required
within-block reference contrasts. Do not average away a failed block or claim the
precision improves by `sqrt(2)` for common standards. The reversed field order helps
expose order/thermal-history problems; it does not prove their absence.

## 23. Shared and common calibration standards

The covariance ledger has one entry per physical standard and its validity period:
length grid, interferometer wavelength/environment, stage/camera timebase, resistance
thermometer calibration, fluorescence reference curves, capillary constants, density
standard, holography wavelength/refractive-index standard and optical reference
spheres. Every observation names the standards it used and the same variable identifier
when an error is shared.

A calibration-reference replacement starts a new standard node with documented
transfer covariance, not an automatic independent reset. A shared offset may cancel
in a contrast while a shared gain multiplies the temperature difference and does not.
Common viscosity scale often cancels more strongly between fields than its temperature
slope or composition change. Within a block, the same-bead radius scale can cancel
while thermal expansion and height-dependent drag do not. A shared force/position
calibration must be differentiated through both A and B.

This ledger is the scientific meaning of shared covariance. A digest identifies its
content; it does not establish traceability or independence on its own.

## 24. Full covariance and auxiliary measurement model

Define the ordered primitive vector phi and its measurement law before deriving H.
It includes at least:

- all viscosity nodes, capillary/density standards and calibration temperatures;
- per-bead radius, optical/model inputs and temperature transfer;
- resistance/fluorescence parameters, local thermal maps and their interpolation;
- wall/chamber geometry, slip/shape bounds, driven fluid transfer and velocity standards;
- force/displacement fit variables, plateau mean covariances, centre and frame transfer;
- both coordinate maps, their distortion bounds, clock and encoder parameters;
- detector offsets/noise parameters, shutter kernels, synchronization and reference drift.

Group provenance as global, session, block, field and record variables, but preserve
all nonzero cross-group covariance. Write, for example, `phi=L z+e` with complete
`Cov(z,e)`, rather than defining groups to be independent by notation. Keep an index
map, units, standard identifiers, covariance version and justification for every
zero block. A PSD covariance can be singular when redundant derived variables are
included; use a declared independent primitive basis and its exact constraints, not
an arbitrary ridge. Only physical K, H and Gamma require strict positive definiteness
among those calibration matrices. K and c are normally derived outputs of the joint
fit. If represented by a sufficient fitted-summary vector instead, preserve their
complete cross-covariance with the original standards; never include both that summary
and its source primitives as independent uncertain inputs.

For auxiliary observation vector a, specify `p_A(a|phi)` or a justified confidence-set
construction, the estimator, finite-sample degrees of freedom where relevant, and
uncertainty in its estimated covariance. Shared systematic calibration parameters
must have a defensible measurement law or coverage set. A convenient Gaussian prior
on an unknown fixed bias is not frequentist coverage. Literature ranges and model
bounds without a repeatable error law stay in a bounded-error set B, not fictitious
zero-mean random draws.

Construct a **joint 99.9% physical calibration region** A for the complete packet,
with its stated frequentist coverage basis. This is stronger and safer than using
eight unrelated 99.9% intervals and claiming their intersection has 99.9% coverage.
If assembled from separate regions, the noncoverage allocations must sum to at most
0.001. Include covariance-estimation and model-envelope uncertainty. The physical
geometry, positivity and domain checks apply throughout this region plus the
separately bounded corrections. T's auxiliary error accounting must use this same
coverage allocation once, not add an unbudgeted 0.001 for every source or test.

Standard uncertainty, expanded uncertainty, coverage probability and deterministic
bias bound are distinct packet fields. The full correlated propagation follows the
measurement-model principle in [JCGM 100:2008](https://www.bipm.org/en/doi/10.59161/jcgm100-2008e).
That guide does not by itself prove the finite-N coverage of T's future inference;
V must establish it under the actual auxiliary model.

## 25. Propagation to U, H, V and log beta

Let `C_phi` denote the complete auxiliary covariance and use analytic or independently
verified Jacobians. For the physical Hessian and potential,

\[
dH=\frac{dK}{k_BT}-H\frac{dT}{T},\qquad
C_{\operatorname{vech}H}=J_H C_\phi J_H^T, \tag{U.18}
\]
\[
dV=\tfrac12q^T(dH)q-q^T H\,dx^*+q^T H\,dx
\]

when the last term represents uncertainty in the observation-coordinate conversion.
Retain the joint covariance with the centre, detector parameters, Gamma and tau;
separately listing their marginal covariances is insufficient. Derivatives of U
before normalization use K rather than H and retain their cross-covariance with T.

For a known coordinate scale and the ideal Gaussian covariance `Sigma=H^-1`, the
first-order scale sensitivity is

\[
d\log\beta=-\frac1d\operatorname{tr}(H^{-1}dH). \tag{U.19}
\]

A common declared scale error `H_A=c H_true` gives exactly `beta_hat=1/c` at the
population level; hence `delta ln beta=-delta ln c`. The sign is a required algebraic
check. Equation (U.19) is a diagnostic identity, not a replacement for T's temporal
likelihood with observation noise, shutter, free mean and drift nuisance parameters.

For that likelihood let theta contain log beta, mean and drift, and let
`s(theta,phi)` be its expected score with the prospective observation law held at
its true independently specified values. Implicit differentiation gives

\[
\frac{d\theta_*}{d\phi}
=-\left(\partial_\theta E s\right)^{-1}
  \partial_\phi E s, \tag{U.20}
\]

or the equivalent profiled expression. Extract its log-beta rows to obtain J_beta.
The derivative includes reprocessing effects when phi changes the coordinate or
timestamp map, and all shared observation calibration. Evaluate over T's beta/design
envelope, every field and block, with qualified nuisance bounds. This is a prospective
model sensitivity, not a derivative fitted to an observed B outcome.

Then

\[
C_{b,\mathrm{cal}}=J_\beta C_\phi J_\beta^T,
\qquad C_b=C_{b,\mathrm{cal}}+C_{B\mid\phi} \tag{U.21}
\]

at first order, using the joint formulation when cross-terms require it. The second
term is B sampling uncertainty and does not count toward the auxiliary 0.009/0.003
floors. Uncertainty in shared nuisance estimates is not counted twice.

Linear propagation must be checked against the full nonlinear measurement map over
the qualified region. Bound its second/higher-order remainder or use a deterministic
nonlinear enclosure under the justified auxiliary law. If the approximation cannot
meet the endpoint bias/coverage budget, it does not qualify merely because a local
Jacobian is small. No Monte Carlo is run in U.

For residual model discrepancies, specify an admissible set of true force, temperature,
response and observation laws constrained by independent measurements. For each law,
the expected Gaussian log likelihood is computable from its mean and covariance;
profile it to obtain the pseudo-true log beta and gate offsets. Bound their supremum
against the ideal retained model. This supplies a precise endpoint definition of
bias even for a time-response mismatch. A bound on a transfer curve by itself is
not yet a bound on log-beta bias or test size. Distributional deviations additionally
need the coverage/diagnostic treatment validated in V; a covariance match does not
prove Gaussianity.

Let delta_b range over the combined certified systematic set, including nonlinearity,
thermal/flow transfer, distortion, noise-model remainder, digitization and numerical
errors. Require jointly

\[
\max_i\sup|\delta b_i|\le0.0005,\qquad
\max_{b,j>0}\sup|\delta b_{bj}-\delta b_{b0}|\le0.0005. \tag{U.22}
\]

Two separate absolute bounds of 0.0005 imply only a possible contrast bound of 0.001.
The second inequality therefore needs its own correlated calculation. No residual
is simultaneously treated as a random zero-mean uncertainty and as an independent
bounded contribution unless the decomposition is explicitly justified.

## 26. Absolute 0.9% calibration qualification

For every one of the eight log-beta endpoints, require

\[
\sup_{\text{qualified design/auxiliary envelope}}
\sqrt{(C_{b,\mathrm{cal}})_{ii}}\le0.009. \tag{U.23}
\]

The envelope includes uncertainty in covariance estimation and calibration-model
parameters, not just their convenient point values. The projected variance includes
all A, observation and coordinate calibration, while excluding conditional B sampling
variation. It uses the validated nonlinear variance/enclosure if first-order (U.21)
is inadequate. Coverage of the resulting statistical interval remains governed by T
and later V. Expanded calibration intervals must not be compared directly with 0.009.

The following **engineering allocation** illustrates a sufficient way to distribute
standard-uncertainty contributions. It is not achieved data or an additional acceptance
rule. The actual rule remains the full correlated (U.23) and (U.24). For any grouping,
Minkowski's L2 inequality makes the sum of component standard uncertainties a
conservative bound even when they are correlated, provided the partition is an
actual additive linearized-error decomposition with no omitted cross-dependency.

| Projected source group | Example absolute contribution cap | Example contrast contribution cap |
|---|---:|---:|
| Viscosity measurement/model coefficients, with temperature dependence accounted separately | 0.0025 | 0.0006 |
| Per-bead radius/material transfer | 0.0020 | 0.0002 |
| Temperature and shared temperature/viscosity chain | 0.0010 | 0.0006 |
| Wall, shape and fluid-transfer calibration | 0.0005 | 0.0003 |
| Driven response/force fit and centre transfer | 0.0015 | 0.0007 |
| Coordinate/length/time standards | 0.0005 | 0.0002 |
| Localization/shutter calibration | 0.0005 | 0.0002 |
| Sum, before any remaining nonlinear contribution | **0.0085** | **0.0028** |

These numbers are dimensionless **endpoint** standard uncertainties. They do not mean
“every instrument must have this percentage accuracy.” Shared temperature effects
must be assigned once in this partition. A different prospective allocation can
qualify through the full covariance without meeting every illustrative cap; it cannot
change T's total limits or be chosen after B. Any remaining random nonlinear
contribution must fit the remaining room. Bounded bias still satisfies (U.22)
separately and is not paid for with unused variance.

No apparatus evidence presently demonstrates even the entries of this example.
In particular, per-bead absolute dimensional metrology and the total drag correction
can be limiting. Passing the relative criterion alone cannot certify an absolute
thermal scale because a shared scale bias can cancel from every contrast.

## 27. Cross-field 0.30% calibration qualification

Within each block let `d_bj=b_bj-b_b0`, j=1,2,3. With contrast matrix D,

\[
C_{d,\mathrm{cal}}=D C_{b,\mathrm{cal}}D^T,
\]
\[
\sup\sqrt{C_{b,\mathrm{cal}}[bj,bj]+C_{b,\mathrm{cal}}[b0,b0]
-2C_{b,\mathrm{cal}}[bj,b0]}\le0.003. \tag{U.24}
\]

All six contrasts must satisfy this; no across-block average replaces one of them.
The same envelope, nonlinear remainder and covariance-estimation requirements apply.
Source sensitivities enter as `(J_bj-J_b0) C_phi (J_bj-J_b0)^T`, exposing exactly which
shared errors cancel.

For example, an additive common log-scale error cancels identically, whereas a
viscosity slope error is multiplied by the temperature separation. The same thermometer
can improve a difference yet leave a common absolute bias. The same bead reduces
relative radius uncertainty only after thermal expansion and bead stability are
qualified. A two-bead comparison does not inherit the within-bead cancellation.

There is no algebraic inconsistency between the two T limits: in the abstract model
`b_i=g+e_i`, standard deviations `u(g)=0.006` and independent `u(e_i)=0.0015` give
`u(b_i)=0.00618466` and `u(b_j-b_0)=0.00212132`. This is a deterministic covariance
example, **not a physical estimate, packet or performance forecast**. Actual shared
and differential errors must be measured. The independent calibration law and its
confidence-set coverage must also support the full T contrast procedure.

## 28. Qualification and structured refusal

A packet is VALID only when every required measurement, covariance and provenance
link exists, every scientific-domain condition is certified and all T/U inequalities
are satisfied. Missing evidence is not interpreted as zero error. Store the failing
predicate, measured/allowed domain, standard references, affected fields and whether
the failure is physical, metrological, statistical or numerical.

| State / reason family | Meaning and consequence |
|---|---|
| INCOMPLETE_INPUT / MISSING_PROVENANCE / MISSING_COVARIANCE | Required input or dependency absent; no valid packet or unblind authorization |
| PRIMITIVE_PHYSICALLY_INVALID | Non-finite/nonpositive primitive or incompatible units/material/domain; refuse |
| NUMERICAL_REPRESENTATION_FAILURE | Derived gamma/tau/H unusable or certified precision unattainable; refuse before publication |
| HYDRODYNAMIC_MODEL_UNQUALIFIED | Walls, slip, flow, inertia or resistance model not bounded; refuse |
| TEMPORAL_MODEL_UNQUALIFIED | Driven response incompatible with T likelihood within its error budget; return for apparatus qualification or prospective T revision |
| THERMOMETRY_UNQUALIFIED / RESERVOIR_UNQUALIFIED | Local T, heating, gradients or probe perturbation not bounded; refuse |
| HARMONIC_DOMAIN_UNQUALIFIED / NONCONSERVATIVE_FORCE | Potential model not established on required domain; refuse |
| INSUFFICIENT_GEOMETRY_CALIBRATION | A region reaches non-SPD matrices, exceeds condition limit, or cannot resolve required field geometry; inconclusive, not projected to SPD |
| OBSERVATION_MODEL_UNQUALIFIED | Noise, blur, synchronization, distortion or photon regime outside T model; refuse |
| CALIBRATION_UNCERTAINTY_EXCESS | Absolute/contrast floor, bias bound or T.29 floor fails; more B frames do not cure a calibration floor |
| FIELD_ROLE_UNRESOLVED / FIELD_ROLE_INVALID | Required perturbation not resolved / absent; no substitute weaker field |
| T11_UNQUALIFIED | No count in the fixed range satisfies information and all positive-gate precision requirements |
| INVALID_RECORD_MONITOR | Later independent monitor, clipping, missingness or thermal/geometry state leaves frozen envelope; apply T invalid-record rule |
| VALID | All conditions passed on actual independent evidence; not asserted in U |

For geometry, require **every** H in the joint 99.9% region plus bounded corrections
to be SPD with `kappa_2(H)<=100`; perform certified enclosure rather than checking only
the estimate. Equal positive eigenvalues are allowed. No nearest-SPD repair, deletion
of an inconvenient direction, confidence-region truncation at positivity, unreported
regularization or uncertainty shrinkage is permitted. If a confidence region includes
invalid physical values because the measurement is too imprecise, classify insufficient
qualification; do not condition that region on physical admissibility to claim it passed.

Distinguish INVALID (demonstrated model/domain breach), INCONCLUSIVE (insufficient
precision or unresolved certificate) and INCOMPLETE (absent inputs). None is evidence
against an equilibrium theorem. Refusals apply to all primary and control paths and
must agree at construction, publication, recovery, comparison and terminal verification.
A boolean success flag without its scientific reasons is insufficient.

## 29. Scientific packet specification

This is a semantic schema for later implementation, not executable code and not a
populated packet. Exact serialization and schema validation belong to V.

| Packet group | Required contents and type |
|---|---|
| Identity | Protocol/version, T parent SHA, U specification identity, block/field/record IDs, timestamps, acquisition-stream labels, operator/instrument IDs |
| Apparatus manifest | Actual liquid recipe/batch, bead ID/material, chamber assembly, optical settings, drive/probe procedures, validity periods |
| Target settings | T's nominal k modes, orientation, temperatures, field order; explicitly tagged TARGET, not MEASURED |
| Raw observations | Immutable references and content digests for force/position/velocity plateaux, viscometry/density, holograms, temperature maps, calibration targets and timing pulses |
| Measured primitives | Values, SI units, measurement procedures, repetitions, fit versions, range certificates, actual temperature and pressure, finite-positive checks |
| Derived physical field | K=H_U, x-star, U difference function, local T, H=K/(k_B T), V function, matrix/eigenvector conventions and transformation maps |
| State space | Dimension, affine coordinates, domain/qualified spatial range, base measure, axial reduction/separability evidence, FOV/escape qualification |
| Hydrodynamics | eta(T) model and node data, per-bead radius/temperature transfer, gamma0, tensor Gamma, wall/shape/flow corrections, remainder bounds and model validity domain |
| Dynamics | Joint generalized modes/times, driven-response records and residual envelope, tau_f/tau_s, non-alias qualification; no B spectral estimates |
| Observation model | Detector offset/map, R and its calibration law, shutter kernels, timing/deadtime/synchronization, quantization and missingness policy, range qualifications |
| Uncertainty | Ordered independent phi basis; full C_phi and its estimation uncertainty; all cross-field/cross-block/reference links; auxiliary measurement law and coverage construction |
| Bounded errors | Joint systematic sets, individual physical sources, absolute/contrast projections, nonlinear/numerical remainder certificates |
| Qualification | Every predicate and reason code, full-region SPD/condition bounds, T floor/role/T.29/information checks, actual or pending state |
| Schedule | Supported Delta/exposure, N0, selected Nraw, D, settling, burn-in, monitors and every-slot accounting rule; no outcome-dependent extension |
| Constants | Exact SI k_B separated from measured standards; numerical precision for constants such as pi stated |
| Provenance/lock | Raw-source digests, standard/certificate identities, computation/method identities, covariance ordering, semantic-packet digest and prior-version linkage |

`k_B=1.380649e-23 J/K` is exact in the SI definition; do not give it a fictitious
measurement uncertainty. Realizing temperature and the joule/metre standards has
uncertainty, which belongs to the appropriate measurement chain.
[BIPM's kelvin definition](https://www.bipm.org/en/si-base-units/kelvin) is the source
for this exact constant. The chosen value's numerical representation still has a
bounded computational error.

Every quantity is tagged MEASURED, DERIVED, EXACT_CONSTANT, REFERENCE_INPUT,
TARGET_SETTING or QUALIFICATION_RESULT. References do not become measured values by
being placed in the same object. Missing values stay missing and prevent a VALID
packet. No fabricated nominal eta, bead radius, sigma, covariance or apparatus result
appears in the official slot.

**Forbidden A fields and dependencies:** passive B sample covariance/precision,
thermal-width stiffness, fitted beta, equilibrium density histogram, B normality or
current results, B-based camera noise, B-selected calibration method or B-adjusted
centre. A driven-displacement raw record must be typed as such, not banned merely
because it contains positions; semantic provenance matters more than a field-name
blacklist. B comparison outputs live in a different artifact after locks.

## 30. Lock identity and blinding interface

A method/protocol hash identifies the rule. A **semantic physical packet digest**
identifies the actual realized measurements, complete covariance, dependencies,
corrections, qualification and source references under that rule. The latter binds
all load-bearing content, including units, matrix orientation, component ordering,
shared-standard identities and uncertainty distributions. Canonical serialization
must be deterministic and reject ambiguous numeric/unit encodings. Store the semantic
preimage with the publication, not just a digest string.

The fixed dependency order is:

1. Approve the audited U route and subsequent V implementation/validation through
   the programme's later authority gates; freeze the pre-A apparatus/procedure manifest.
2. In an authorized physical stage, acquire and freeze A and observation-instrument
   measurements. Resolve every qualification without access to passive B outcomes.
3. Compute and independently verify the complete physical packet and deterministic
   schedule. Publish and lock it, including covariance and full raw-source provenance.
4. Acquire/retain passive B under the fixed schedule. Its free characterization uses
   only the permitted observation interface and is frozen independently.
5. Verify both locks and their actual publications; only then compare against A.
   Any later independent monitor veto is recorded, not used to refit the packet.

The locked packet fixes reference-monitor transfer functions and their conditional
uncertainty model. Actual monitor readings acquired later are immutable linked
observation artifacts, bound by B's preprocessing lock; they cannot be hashed before
they exist. Applying that already locked transfer is permitted. Refitting its
coefficients, its covariance law or the mechanical potential from those readings is
not. An out-of-domain reading invokes the frozen veto rather than a revised packet.

The exact physical acquisition ordering will be adopted later; nothing here issues
an unblind token or authorizes an experiment. If future operations collect encrypted
B earlier, the same publish-before-access boundary must be proved and expressly
adopted; it is not an implicit exception to this sequence.

The permitted B preprocessing interface contains the calibrated detector/coordinate
maps, timestamps, shutter/noise law, reference-only drift rule, opaque record IDs and
frozen observation validity rules. It does not expose A's H, V, mechanical residuals
or beta expectation. Do not leak H through metadata, formatted filenames or a nominal
stiffness field in this interface. Acquisition operators can know setpoints, and
durations or temperatures can make a field recognizable. The protection is a frozen
method and inaccessible comparison output, not an implausible claim that all operators
are psychologically blind to temperature.

A post-lock calibration correction creates a new identified artifact and an explicit
prospective disposition; it cannot silently rewrite an artifact already compared to
B. Exact packet identity differs from a null-law condition identity (§32). Neither
identity certifies that measurements are physically true.

## 31. Feasibility assessment: requirements versus evidence

No row below has an actual EBU calibration result. “Conditional” means that the method
has a physical measurement basis, while its joint accuracy here is not established.
The numerical contribution caps refer to §26's illustrative sufficient allocation;
the binding requirements are the complete covariance and T gates.

| Component | Selected method / scientific basis | Required uncertainty or qualification | Expected feasibility | Actual status |
|---|---|---|---|---|
| Viscosity | Actual-batch capillary viscometry plus density | Complete eta/T covariance; projected total budgets; example viscosity contributions 0.0025 absolute / 0.0006 contrast | Conditional; common capillary scale helps relative precision, but temperature slope/composition may limit it | NOT MEASURED |
| Bead radius | Per-bead calibrated holography, optical/hydrodynamic boundary qualification | Example endpoint contributions 0.0020 / 0.0002; shape/slip separately bounded | Demanding; published image precision alone is insufficient absolute metrology | NOT MEASURED |
| Local temperature | PRT anchors plus calibrated rhodamine-B maps | Full chain (U.11), example 0.0010 / 0.0006 contributions; spatial bias and T drift limits | Conditional; spatial averaging and optical perturbation may be limiting | NOT MEASURED |
| Wall/drag model | Measured chamber geometry and finite-chamber resistance | Tensor uncertainty, example 0.0005 / 0.0003 contributions; model remainder within joint bias set | Demanding near walls; a bare Stokes formula is insufficient | NOT MEASURED |
| Mechanical K and centre | Balanced 2D driven force fit with EIV | Full tensor/centre covariance; example 0.0015 / 0.0007 contributions; T shape/centre precision | Conditional; mean-displacement precision can improve with A repetition, common force errors cannot | NOT MEASURED |
| Coordinates | Traceable grid, interferometric stage, fiducials | Example 0.0005 / 0.0002 contributions; nonsingular map and bounded distortion | Conditional; x/y/shear/orientation and frame transfers all matter | NOT MEASURED |
| Noise/shutter | Immobilized and driven reference targets, optical timing pulses | Example 0.0005 / 0.0002 contributions; noise ratio <=0.05, exposure/timing constraints | Hardware dependent; photon count and frame rate can conflict | NOT MEASURED |
| Relaxation/Markov model | Independent driven response and generalized mechanical modes | Finite positive tau bounds, non-alias band and endpoint/coverage residual bounds | Significant risk from fluid memory, especially for stiff traps in low-viscosity liquid | NOT MEASURED |
| Harmonic/conservative domain | Full force map plus justified remainder bound | Joint log bias <=0.0005, shape/current/centre requirements and spatial-tail domain | Conditional; local derivative at the centre is not enough | NOT MEASURED |
| 298/318 K arm | Same standards, direct local maps and viscosity curve | Actual ratio role bound; differential covariance <=0.003 after all sources | Thermally accessible in principle; local homogeneity and long-duration stability unestablished | NOT MEASURED |
| Two preparations | Fresh bead/liquid/chamber assembly, full recalibration | Separate blocks with shared-standard covariance | Operationally feasible; does not establish statistical independence of standards | NOT MEASURED |
| Complete eight-record design | Exact T11 mapping and all positive gates | Information 450,000 / 408,164; count cap; T.29; later V complete-pass validation | Not determined without the actual apparatus packet | NOT MEASURED |

Evidence establishes that the constituent measurement methods exist. It does not
establish that a single apparatus can meet every requirement simultaneously. In
particular, no hardware frame rate, local thermometry accuracy, nonlinear remainder,
radius certificate or hydrodynamic-memory budget was found as an actual completed
measurement in the inspected controlling record. Values used in historical examples
or software fixtures cannot fill these gaps.

There is no demonstrated incompatibility with **all** plausible realizations of this
route. Nor is there evidence to claim joint feasibility achieved. If driven-response
qualification, temperature mapping or a calibration floor fails in the future, the
specified outcome is refusal, with a prospective apparatus or T-stage reconsideration
as appropriate. This is a bounded scientific design, not a promise to keep changing
models until the experiment passes.

## 32. Old F2 and F4 issues: specification closure only

The corrected historical reconstruction establishes two distinct questions.

**F2 primitive and derived validity.** Present code tests eta and radius individually
as finite positive primitives. That prevents two negative values from creating an
apparently positive drag. It does not by itself guarantee representable derived
quantities. The committed addendum documents the C7/C8 path with tiny positive
primitives (`eta=a=5e-324`) producing zero gamma/tau, reaching publication/unblind on
that historical path while strict recovery rejects it. The programme pause preserves
this as an unrepaired implementation problem.

U resolves the scientific specification by requiring primitive-domain, derived
physical-domain and numerical checks at one mandatory boundary before publication,
lock and any access permission, including paths that do not perform statistical
calibration. The same checks must be repeated by recovery and terminal verification.
**F2: RESOLVED IN SPECIFICATION; implementation not repaired, historical status not
cleared.** The separate low-level constructor question remains as the historical
record describes it; U does not mislabel an unreachable authority-unspecified path
as an independently established runtime defect.

**F4 physical construction and identity.** Existing `build_field` builds stiffness,
orientation and T from contract field specifications, while accepting eta/a and
limited uncertainty inputs. It is not an actual independent full-tensor force fit
with the covariance required here. U supplies the missing future scientific construction:
actual measured fluid/radius/temperature/geometry, complete mechanical and observation
calibration, joint uncertainty, and explicit qualification. No fixture viscosity,
nominal radius or nominal stiffness is promoted to a physical measurement.

The earlier assertion that every distinct realized eta/a pair must have a distinct
**contract** digest is unsupported. A frozen measurement rule can permit many realized
packets under one contract. Even different eta/a pairs can give the same product,
gamma and null-law condition in the old model. The corrected addendum identifies the
actual publication/evidence preimage as the proper place to bind their primitive
values. Its publication schema already distinguishes such realized packets; it does
not depend on the unsupported contract-digest claim.

Retain the separation:

| Identity | What it binds | What equality does not prove |
|---|---|---|
| Protocol / contract | Frozen rule and authority | Same realized physical measurements |
| Null-law calibration condition | All parameters relevant to that statistical law | Same physical packet, provenance or an automatically allowed artifact reuse |
| Physical packet / publication | Actual primitives, derived values, covariance, shared references and source evidence | Physical accuracy merely because a hash matches |

U's future packet extends the complete scientific content that must be bound; it
does not rewrite an old identity enumeration or grant reuse. Reuse would still need
explicit prospective authority and compatible dependence. **F4 construction is
specified prospectively; actual physical inputs remain unmeasured and old F4 authority
is unchanged.** No historical F-stage implementation is resumed.

## 33. U1–U12 disposition

Here COMPLETE means that the required method, inputs, uncertainty dependencies,
acceptance/refusal rules and later-stage interface have been specified. It does not
mean that future packets are VALID or that any numerical apparatus qualification
has been achieved.

| Item | Disposition | Closure in this specification |
|---|---|---|
| U1 Branch-A independence | COMPLETE | Four typed streams, no B-derived field/noise/centre, pre-B construction and locks |
| U2 Mechanical force/stiffness | COMPLETE | Controlled chamber drag, overdetermined 2D EIV fit, conservativity and uniform harmonic qualification |
| U3 Viscosity | COMPLETE | Actual-batch capillary/density route, fixed temperature interpolation, valid domain and joint eta/T covariance |
| U4 Bead radius | COMPLETE | Per-bead optical metrology with material/boundary qualification and thermal transfer |
| U5 Hydrodynamic drag | COMPLETE | Full resistance tensor, measured walls/flow, physical and numerical validity, memory qualification |
| U6 Thermometry/local T | COMPLETE | Traceable bulk anchors plus calibrated local maps, heating/gradients/perturbation and common-reference covariance |
| U7 Coordinates/orientation | COMPLETE | Full affine maps, distortion bound, force transformation and eigenspace-aware orientation |
| U8 Observation calibration | COMPLETE | Independent R, shutter/timing law, range and noise-model refusal; no passive thermal calibration |
| U9 Fields/blocks | COMPLETE | Exact T targets/orders, derived role resolution, two fresh preparations, fixed T11 mapping |
| U10 Calibration covariance | COMPLETE | Full primitive measurement law, shared references, nonlinear propagation and absolute/contrast uncertainty definitions |
| U11 Qualification/refusal | COMPLETE | Missing/invalid/inconclusive states, full-region SPD, physical/model/numerical gates and all-path refusal |
| U12 Packet/lock | COMPLETE | Semantic schema, complete actual-packet identity, provenance and publish-before-comparison boundary |

No item is declared NOT APPLICABLE merely because its measurement is difficult.
Physical measurements, numerical implementation and independent audit remain explicit
future dependencies. No load-bearing missing T rule was supplied by an invented
scientific margin: field-role minima are derived from T, and arbitrary manufacturing
tolerances are not introduced. HUMAN SCIENTIFIC DECISION REQUIRED: **NONE** for this
specification. Independent U audit can still identify a logical or physical-design gap.

## 34. U-to-V handoff — not begun

After independent U clearance and separate authorization, V must:

1. Implement the semantic packet schema, units/types, covariance/reference graph,
   immutable raw references and completeness validation. Distinguish actual data,
   synthetic parameter injection, target settings and exact constants.
2. Implement the selected mechanical EIV estimator and independent calibration ingestion,
   analytic/checked derivatives, matrix transformations and generalized-mode pairing.
   Preserve common Gamma–K and eta–T dependencies; validate all mandatory refusal paths.
3. Implement full primitive-law propagation, confidence-domain and bounded-error
   enclosures, numerical representation checks, SPD/conditioning certificates and
   the projection of residual models to scale and positive gates.
4. Implement observation-kernel/noise ingestion and exact temporal likelihood, including
   shutter-induced correlations, profile nuisance information and the fixed T11
   count rule. Validate the supported timestamp and missingness cases prospectively.
5. Implement complete packet publication/locking and independent recovery verification;
   keep protocol, actual-packet and null-law identities distinct. Test synthetic
   parameter injection without disguising it as an actual calibration packet.
6. Under V's separately adopted plan, establish finite-N inference, auxiliary coverage,
   critical ceilings, false-support size, controls, diagnostics and full-experiment
   power across the required domains. Retain the T seed-family separation and
   independent validation architecture. U has created no seeds or draws.

T's finite-N requirements, including achieved-size confidence bounds, 2.10 critical
ceiling and complete-pass lower bound, control these tasks. Planning information or
a finite grid is not a substitute for their validation. V must not be started merely
because this document exists. **V is blocked pending independent U audit.** W authority
adoption and any physical execution require their own subsequent gates.

## 35. Physical-execution handoff — not begun

A later separately authorized physical stage must obtain and preserve:

- a fully identified apparatus/preparation manifest and traceable certificates;
- actual liquid composition, density and viscosity curve, including reference checks,
  heating/cooling repeatability and model/domain bounds;
- actual per-bead radius, material/shape/boundary qualification and thermal transfer;
- measured wall geometry, fluid transfer, background flow and resistance correction;
- full two-axis force/displacement data, mechanical K, zero-force centre, nonlinear
  and nonconservative residual bounds, and independently driven response qualification;
- local temperature maps, bulk anchors, laser-heating/gradient/probe-effect bounds and
  record-duration stability at every field setting;
- coordinate, fiducial, detector, shutter, synchronization, localization and digitization
  calibration at the actual operating conditions;
- the complete primitive law/covariance, shared-standard graph, bounded errors,
  full-region geometry and uncertainty predicates, field-role checks and reasons;
- the resulting fixed sample counts, durations, settling/burn-in schedule and independent
  monitor envelopes, followed by separate packet locks before passive comparison.

All of these are **future measurements**, not results of U. The actual fluorescence
curve, viscosity nodes, radii, chamber dimensions, calibration covariance and camera
parameters remain unpopulated. The handoff does not collect even one observation,
run a trajectory or authorize the later optical-trap experiment.

## 36. Final status and static verification record

U-STAGE BRANCH-A PHYSICAL CALIBRATION SPECIFICATION: **COMPLETE — INDEPENDENT AUDIT
REQUIRED.** All U1–U12 are complete as design. Apparatus qualification is NOT ESTABLISHED;
physical calibration data are NOT COLLECTED. V and W have NOT STARTED. The baseline
DeltaJ defect is NON-BLOCKING here; repair before W. Book 1, all authority, plans,
contracts, seeds, seal and code remain unchanged.

Verification is limited to direct source inspection, strict JSON/AST reading, hashing,
dimensional reasoning and isolated deterministic arithmetic. No scientific module was
imported or executed. No scientific RNG, optimization of experimental outcomes,
trajectory, Monte Carlo, calibration acquisition, official campaign, unblinding or
real optical-trap experiment was performed.

The deterministic checks accompanying preparation of this report cover temperature
and stiffness scale signs, anisotropy/rotation formulae, wall-correction magnitudes,
scalar/tensor drag cancellation in relaxation, Jacobian covariance with shared
standards, and numerical positivity/underflow distinctions. They use mathematical
examples only and are not calibration packets. The completed arithmetic results are:

| Check | Result |
|---|---|
| Fixed-298 normalization at 318 K | beta = 0.9371069182389937; 6.2893081761% decrease |
| Strict 2% temperature-role boundary at exactly 298 K | T3 > 303.96 K, with uncertainty enlarging the required separation |
| Rotation log-shape at rho=2.5, psi=30 degrees | 0.4700036292457356 |
| Point rotation-role boundary at rho=2.5 | 2.9482778277 degrees; target remains 30 degrees |
| Displayed one-wall Faxen series at h/a=10 and 100 | 5.9482755552% and 0.5656694976% drag increments |
| Abstract common-scale covariance example | absolute standard uncertainty 0.0061846584; contrast 0.0021213203 |
| Noncommuting tensor drag cancellation | Exact rational-matrix equality `inverse(K^-1 Gamma)=Gamma^-1 K` verified |
| Nonorthogonal coordinate transform | Work and quadratic potential exactly invariant in rational arithmetic |
| Signed four-direction, three-radius polynomial design | Scalar cubic design rank 10, including intercept |
| Centre differential | Analytic derivative agreed with a symmetric numerical difference to 8.9e-12 absolute error |
| Tiny positive primitives | Positive primitive checks alone allow multiplication underflow to zero; distinct derived refusal required |

These checks validate specific formulae, not apparatus accuracy, field qualification,
finite-sample coverage or a proof of feasibility. The first centre-difference check
used an overly tight mixed floating-point tolerance and was replaced by an explicit
finite-difference tolerance; the derivative formula was unchanged.

The start snapshot contains 2,989 tracked regular files. A completed byte-hash comparison
confirmed all 2,989 unchanged. Strict JSON parsing and AST-literal inspection independently
reconstructed the protected analysis identity from 12 sources and execution identity
from 19 validation sources plus the driver; both match §2. The T report hash also
matches its starting value. The report's 36 numbered sections, 24 numbered equations,
local source links, Markdown table structure and whitespace were checked. The final
commit procedure requires the complete added-file diff to equal this reviewed draft,
exact-path staging, a clean diff check and a report-only staged filename list; the
post-commit verification repeats the protected-file comparison and confirms a clean
tree. No scientific test suite or runner is invoked by these checks.

Starting SHA: `ebcf2641fa2d8fe4ab95fef011e96fe53feeadc6`.
Authorized changed file: `docs/e1a/E1A_BRANCH_A_PHYSICAL_CALIBRATION_QUALIFICATION.md`.
The final commit SHA and this report's content hash are returned in the completion
message rather than inserted self-referentially into the report. The report is excluded
from the existing analysis/execution identity preimages. Existing execution authorization
remains FALSE and seal state remains PRE_DRIVER, with no official validation results
directory. This report is committed locally only. **PUSH: NO.**
