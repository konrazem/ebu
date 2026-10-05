# E1a Branch-A physical calibration and qualification specification

**Status: NON-CONTROLLING U-STAGE PHYSICAL CALIBRATION SPECIFICATION.**

| Programme item | Status |
|---|---|
| R / S-MG / S | CLEARED inputs; no theoretical reopening |
| T1–T12 | INDEPENDENTLY CLEARED; narrow target-realization interface gap identified, T amendment pending |
| Independent U audit | NOT CLEARED: axial marginalization and realized-field qualification |
| U repair | Axial specification repaired for re-audit; U9 GAP; field qualification BLOCKED |
| Physical calibration data | NOT COLLECTED |
| Apparatus qualification | NOT ESTABLISHED |
| V / W | NOT STARTED; V blocked by missing field-realization policy and independent re-audit |
| Execution | NOT AUTHORISED; existing execution flags remain false |

Prepared on 2026-10-05 against repository commit
`ebcf2641fa2d8fe4ab95fef011e96fe53feeadc6`, branch `codex/book-one-continuity`.
Bounded repair starts from failed U commit
`7c3346462f5aeed5dfef176ecaa4e5e9070e847a`. The original preparation coordinate above
is retained for provenance. This revision changes only the two audited blockers and
their necessary mathematical/status/handoff dependencies. It contains neither an
actual calibration packet nor a claim that an apparatus meets its requirements.

## 1. Executive result

Branch A will construct the potential through **controlled, externally driven
force–displacement calibration**, using a calibrated translating chamber, independently
measured fluid viscosity and actual bead radius, and a qualified finite-chamber
hydrodynamic resistance. The repaired route uses a full three-dimensional mechanical
fit and its zero-force centre, then a harmonic Schur complement to predict the observed
lateral marginal. Traceable local thermometry supplies the temperature in
`H_eff = K_eff/(k_B T)`. Coordinate, localization-noise and shutter calibrations are separate
measurement streams with a shared covariance ledger.

The selected route retains Stokes drag only inside its measured domain. It does not
assume an infinite liquid, a perfectly spherical bead, a correct nominal temperature,
or an exact stage-to-fluid velocity transfer. Hydrodynamic memory is a particular
qualification risk: static drag calibration alone does not establish the temporal
Gaussian model required by T. Independently driven response measurements must qualify
that approximation over the observation bandwidth; otherwise the apparatus is refused
for this design.

The axial construction is specified for independent re-audit; the overall U stage
remains **NOT CLEARED**. Instrument values and actual qualification remain unmeasured.
The cleared T report does not determine numerical field-target realization regions
or a required discrimination-power objective for departures from its nominal fields.
Under the user's instruction this gap is recorded, T is unchanged, and field
qualification and V remain blocked. No new scientific tolerance is invented.

For the EBU programme, the purpose is concrete: the mechanical energy landscape is
constructed without learning its scale from the distribution used to test it. A
successful later comparison can therefore inform the thermal-normalization claim.
A calibration refusal instead identifies a measurement limitation. It establishes
neither a failure of the equilibrium theorem nor a result about social mechanisms.

### 1.1 Bounded repair record

The independent U audit, as supplied in the commissioning repair brief, returned
**NOT CLEARED** with exactly two material blockers:

1. No selected quantitative independent axial marginalization/PMF qualification.
2. No binding realization rule preserving the intended T-stage physical challenges.

This revision repairs the axial specification in §5 and its direct dependencies.
It withdraws the inadequate weak-presence rules in §21, identifies the exact narrow
T-interface decision and blocks packet validity until that decision is adopted.
The user explicitly chose to record the gap and keep field qualification and V
blocked. Thus Blocker B is **contained by refusal, not scientifically closed**.
No T amendment is committed before its normative objectives are selected. Unrelated
U methods and budgets are preserved. This work is not an independent audit and does
not claim clearance of either the repair or the original U artifact.

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
  at the cleared T parent SHA above. T12 clearance is an explicit input of the user's U brief;
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
microsphere, independently observed chamber geometry, three-axis stage translation
for A calibration and a common physical coordinate frame. Passive Branch B remains
two-dimensional; this extends calibration, not the B observation or likelihood dimension.
The working liquid must be homogeneous,
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

For each block b and field j, construct the full mechanical stiffness K^(3), its
zero-force centre and the effective lateral curvature S=K_eff defined below. The
official two-dimensional field is

\[
U_{\rm eff}(q)-U_{\rm eff}(q_\star)=\tfrac12(q-q_\star)^T S(q-q_\star),
\quad H=H_{\rm eff}=S/(k_BT),\quad
V(q)=\tfrac12(q-q_\star)^T H_{\rm eff}(q-q_\star). \tag{U.1}
\]

Throughout the downstream two-dimensional density, uncertainty and geometry formulas,
K or H_U denotes this **effective lateral** S, and H denotes H_eff. The full 3D
matrix K^(3), its plane block K_qq and the effective matrix are separate packet fields.
Their units are N/m = J/m²; H_eff has units m⁻² and V is dimensionless. The base
measure for B's latent physical density is dq, after the axial marginalization below.
Do not interpret a principal block of the 3D drag as an effective 2D dynamical drag
without the qualification in §5.7. Camera support remains an observation limitation,
not conditioning on survival or an EBU conservation constraint.

Notation: in §§5.1–5.8 q is lateral position and Q=q-q_star is displacement. The
retained downstream formulas use x for position and q=x-x_star for displacement.

### 5.1 Observed state and selected reduction

Branch B observes **two-dimensional lateral detector coordinates**, interpreted through
§19's calibrated observation model as q=(x,y). The axial coordinate z is unobserved in
B and is marginalized. It is measured in the separate driven A calibration described
below. The density prediction is therefore for the lateral marginal with respect to
`dq=dx dy`, not for an energy slice at fixed z. A plane restriction `U(q,z0)` is not
an admissible substitute.

The single selected primary route is **independently driven full 3D force-response
calibration, followed by harmonic Schur-complement reduction**. A separability assertion
and a general nonlinear PMF reconstruction are not alternative official routes left
to V. Measured zero coupling is a special case of this route. A nonlinear potential
outside its bounded harmonic approximation causes refusal and would require a separate
prospective design decision.

Write Q=q-q_star and Z=z-z_star. After independent conservative-force qualification,

\[
U(q,z)=U_*+\tfrac12 Q^T A Q+Q^T b Z+\tfrac12\kappa Z^2,
\qquad
K^{(3)}=\begin{pmatrix}A&b\\b^T&\kappa\end{pmatrix},
\quad A=K_{qq},\quad b=K_{qz},\quad\kappa=K_{zz}. \tag{U.A1}
\]

Here A is 2-by-2, b is 2-by-1, and kappa is scalar. These symbols are local stiffness
blocks, not acquisition-stream labels. Require kappa>0 and full K^(3) SPD over the
joint physical calibration region. With product Lebesgue measure `dq dz`, fixed
uniform T and full Gaussian support, completing the square gives

\[
U-U_*=\tfrac12 Q^T S Q+
\tfrac12\kappa\left(Z+\kappa^{-1}b^T Q\right)^2,
\qquad S=A-b\kappa^{-1}b^T. \tag{U.A2}
\]

The translation of Z has unit Jacobian. Therefore

\[
\int_{\mathbb R}e^{-(U-U_*)/(k_BT)}dz
=\sqrt{\frac{2\pi k_BT}{\kappa}}
 e^{-Q^T S Q/(2k_BT)}. \tag{U.A3}
\]

The prefactor is independent of q because kappa is constant in this quadratic model.
It cancels on lateral normalization. Consequently the official density-bridge field is

\[
\boxed{K_{\rm eff}=S=K_{qq}-K_{qz}K_{zz}^{-1}K_{zq}},\qquad
\boxed{H_{\rm eff}=S/(k_BT)},\qquad
V_A(q)=\tfrac12 Q^T H_{\rm eff}Q. \tag{U.A4}
\]

This also follows from `(K^(3)^-1)_qq=S^-1`, but (U.A3) establishes the reference
measure and normalization explicitly; `det K^(3)=kappa det S`. For the scalar lateral
counterexample in the audit, A=k, b=g and kappa=k_z give `K_eff=k-g^2/k_z`, rather than k. Full SPD requires
`k k_z>g^2`. A stiff positive plane section by itself does not establish that condition.

Replacing the full exponent by `-beta U/(k_B T)` in this **quadratic** calculation
changes the axial prefactor to `sqrt(2 pi k_B T/(beta kappa))`; it remains independent
of q. Thus the lateral covariance is `beta^-1 H_eff^-1` without fitting any axial
or lateral passive covariance to calibrate H_eff.

For a general nonquadratic potential the canonical definition is instead

\[
U_{\rm PMF}(q)=-k_BT\log\int e^{-U(q,z)/(k_BT)}d\nu_z+C. \tag{U.A5}
\]

This requires the declared reservoir, reference measure, support and finite integral.
A q-dependent measure, accessible axial domain or axial curvature can contribute
additional terms. The Schur complement is not a universal replacement for (U.A5).
Nor does multiplying a general PMF by beta necessarily commute with marginalizing
`exp(-beta U/(k_B T))`. The selected primary route is the harmonic case in (U.A1)–(U.A4).

### 5.2 Independent axial position and force measurement

Extend the selected chamber-drag route to a **calibrated three-axis translation stage**.
An independently calibrated axial interferometric encoder supplies z displacement and
velocity of the chamber. In-situ Lorenz–Mie holographic localization supplies all three
bead coordinates during A drives, in a common physical frame. Calibrate its axial
scale, sign, linearity and lateral/axial cross-talk with immobilized reference spheres
translated through known three-dimensional displacements. Include refractive-index
mismatch, focal-depth conversion, aberrations, wavelength, bead-image parameters and
axis tilt. An apparent focus displacement is not automatically a physical z displacement.

This extends the existing per-bead optical method rather than using thermal variance
to identify axial stiffness. [Lee et al. (2007)](https://arxiv.org/abs/0712.1738)
demonstrates holographic 3D localization, including axial position information. Its
reported resolution is evidence for the sensing principle, not a traceable calibration
or demonstrated EBU uncertainty. No instrument capability is asserted here.

For steady plateaux use the **full 3-by-3** finite-chamber resistance Gamma^(3), including
normal-to-wall resistance and its cross-components, with the same independently
measured eta, radius and geometry already required by §§8–11. The three-dimensional
force input is `F^(3)=Gamma^(3) v_rel^(3)`. A parallel-wall Faxen correction for lateral
motion cannot be reused as the normal drag coefficient. Axial flow transfer is measured
by the same independent driven-advection procedure, using 3D localization; no passive
spectrum, equipartition relation or B covariance provides an axial force standard.

Axial chamber motion can change wall distance, refraction, focal depth, trap centre and
stiffness. Use paired positive/negative velocity plateaux at matched chamber heights,
with an independently calibrated optical/fiducial transfer at those heights. Reduce
each probe to the declared record geometry through that measured transfer and its
covariance. A small stroke alone is not proof that K^(3) stayed fixed. If field changes,
velocity transfer, bead height or optical perturbation cannot be bounded within the
existing residual/uncertainty budgets, return AXIAL_REDUCTION_UNQUALIFIED; do not fit
a single K^(3) to unqualified changing fields.

An independent axial force transducer or a nonlinear PMF method could be future
substitutes, but neither is selected in this specification. Absence of an adequate
axial stage/position/drag calibration is a refusal, not permission for V to choose
another route.

### 5.3 Full 3D identification and relation to the retained lateral probes

Fit the vector equilibrium relation

\[
F^{(3)}_r=K^{(3)}X_r+c^{(3)},\qquad
X=(x,y,z)^T,\qquad X_\star=-(K^{(3)})^{-1}c^{(3)}. \tag{U.A6}
\]

The conservative fit has six stiffness components
`K_xx,K_xy,K_xz,K_yy,K_yz,K_zz` and three intercept components. First fit the unrestricted
3-by-3 response for curl/conservativity diagnostics; impose symmetry only after their
qualification, following §12. Estimate all nine physical parameters jointly with
force, position, geometry and standard nuisances using the existing errors-in-variables
construction. The lateral centre is the q projection of X_star, with full covariance.
Here zero force means zero imposed drag. The fitted conservative potential includes
any independently qualified stationary gravity/buoyancy contribution; a constant
conservative load shifts the centre. Uncontrolled background flow cannot be absorbed
into that centre to qualify an equilibrium record (§7).

Three independent force directions with paired signs can identify an affine response
when the measured design has full rank. The selected production design is overdetermined:
retain the original four lateral directions and add the remaining directions in

\[
\{(u_x,u_y,u_z):u_i\in\{-1,0,1\},\ u\ne0,\
\text{first nonzero component is }+1\}, \tag{U.A7}
\]

with each direction normalized in physical space. There are 13 undirected directions:
three axes, six face diagonals and four body diagonals. Both signs and three amplitude
levels give **78 nonzero plateaux per complete cycle**, including the original 24
lateral probes. This adds independent z forcing and mixed xz/yz/xyz probes; lateral
motion alone cannot identify b and kappa. Zero-force references, at least three
cycles, reversed cycle order, A-only pilot selection of fixed counts and the existing
mean-covariance treatment remain as in §§12–13. Amplitudes cover the qualified **3D**
volume at thermal radii R/3, 2R/3 and R under the pilot's full K^(3), with propagated
placement uncertainty. This does not use passive B widths.
The directions specify desired physical displacements. The A-only pilot maps these
to the required velocity/force vectors, which generally point in different directions;
qualification uses the measured 3D design, not nominal commands.

The six stiffness entries are identified by the independent derivatives of the three
force components with respect to the three measured positions; the three intercepts
locate x_star, y_star and z_star. Require full rank of the physical displacement/force
design after nuisance profiling, finite covariance and a qualified numerical solution.
The specified directions also identify all 20 monomials of a scalar cubic polynomial
in three variables. They support the full vector nonlinearity check, including xyz;
finite probes still require a justified between-probe remainder bound under §13.

Eliminating z from the static **force** equations gives an additional check:

\[
S q+c_{\rm eff}=F_q-b\kappa^{-1}F_z,
\qquad c_{\rm eff}=c_q-b\kappa^{-1}c_z. \tag{U.A8}
\]

If independently established F_z=0, a relaxed lateral response can measure S directly;
it does not identify b and kappa separately. Without that axial-force condition a
lateral fit need not measure either A or S. Equations (U.A6)–(U.A8) remove that ambiguity.
The old 2D fit remains a lateral-subset consistency check using the reduced force in
(U.A8); it is no longer a stand-alone construction of the official physical H.

### 5.4 Schur covariance, scale and orientation

For a general positive axial block C, with S=A-B C^-1 B^T,

\[
dS=dA-dB C^{-1}B^T-B C^{-1}dB^T
+B C^{-1}(dC)C^{-1}B^T. \tag{U.A9}
\]

For the selected single axial coordinate, in component order
`v=(A11,A12,A22,b1,b2,kappa)` the Jacobian to `(S11,S12,S22)` is

\[
J_S=\begin{pmatrix}
1&0&0&-2b_1/\kappa&0&b_1^2/\kappa^2\\
0&1&0&-b_2/\kappa&-b_1/\kappa&b_1b_2/\kappa^2\\
0&0&1&0&-2b_2/\kappa&b_2^2/\kappa^2
\end{pmatrix}. \tag{U.A10}
\]

Chain this with the full 3D EIV and coordinate Jacobians, not only six marginal error
bars. With existing primitive vector phi enlarged by the axial measurements,
`C_vech(S)=J_S,phi C_phi J_S,phi^T`, retaining cross-covariance with T, centres, drag,
observation calibration and every other field/block. Normalization gives
`dH_eff=dS/(k_B T)-H_eff dT/T`. Small estimated b is not evidence that its uncertainty
or the second-order Schur term is zero. Near b=0 the leading Jacobian in b vanishes;
propagate the quadratic term by the existing nonlinear-enclosure requirement, not a
zero-variance linearization.

Let `X=P_3 u` map the calibrated 3D instrument coordinates to physical coordinates.
Stiffness transforms as `K^(3)=P_3^-T K_u P_3^-1`; for `L=dP_3 P_3^-1`,

\[
dK^{(3)}=P_3^{-T}(dK_u)P_3^{-1}-L^T K^{(3)}-K^{(3)}L. \tag{U.A11}
\]

This explicitly includes tilt/orientation and axial scale. Forces transform as
covectors and stage velocities as vectors under the same map. A **pure reparametrization**
`z'=s z` changes b to b/s and kappa to kappa/s², leaving S exactly invariant; a
covariance implementation must preserve that cancellation. Actual axial-scale error
can still affect inferred forces, wall heights, fluid transfer and optical cross-talk.
It is propagated through those measurement dependencies, not added as an independent
percentage to S or dismissed by the coordinate-invariance identity.

All axial derivatives feed §25's actual profiled temporal-likelihood sensitivity.
In the ideal instantaneous Gaussian diagnostic,
`d log beta=-(1/2) tr(S^-1 dS)`. Therefore the enlarged Jacobian contributes inside
`J_beta C_phi J_beta^T`; it receives **no additional 0.009 allowance**. For a contrast,
use `(J_beta,bj-J_beta,b0) C_phi (J_beta,bj-J_beta,b0)^T`, including field-dependent
b, kappa, thermal effects and shared axial references. It receives **no additional
0.003 allowance**. Any cancellation must follow from this covariance, not a declaration
that the same sensor was used.

### 5.5 Quantitative axial scale and shape qualification

Always publish S and H_eff for the lateral comparison, even when the correction looks
small. Record the exact diagnostic difference `Delta K_axial=-b kappa^-1 b^T`.
For A SPD define

\[
r=\frac{b^T A^{-1}b}{\kappa},\quad 0\le r<1. \tag{U.A12}
\]

Full SPD is equivalent to kappa>0 and S SPD; in this case r<1. If the plane block A
were mistakenly used against the true lateral covariance, the eigenvalues of its
whitened covariance would be `1` and `1/(1-r)`. Consequently

\[
\beta_{\rm plane}=\frac{2(1-r)}{2-r},\quad
|\log\beta_{\rm plane}|=\log\frac{2-r}{2(1-r)},\quad
G_{\rm plane}=-\tfrac12\log(1-r). \tag{U.A13}
\]

These quantify both scale and geometry impact; a scalar trace check alone is
insufficient. They are **diagnostics of the omitted correction**, not a new permitted
axial tolerance. A large precisely known correction can be retained provided the
resulting S meets every actual field, precision and model requirement. A small
uncertain correction cannot simply be dropped.

For uncertainty and residual-model qualification, use exactly T4's scale-independent
matrix statistic. For a locked H_eff estimate `Hhat=Rhat^T Rhat`, and each candidate
true effective curvature H in the joint physical/model region, form

\[
M(H)=Rhat\,H^{-1}Rhat^T,\quad
w(H)=\log M(H)-\tfrac12\log\det M(H)I. \tag{U.A14}
\]

Propagate the two independent components of w, and the lateral centre, jointly into
T.29's fixed contrast basis, covariance and bounded-error sets. The positive shape
gate remains the T4 97.5% upper limit below ln(1.05), with T.29's fixed planning
allocation and all other error sources included. Require the total 0.009 absolute
and 0.003 contrast standard-uncertainty limits, the joint 0.0005 absolute/contrast
bias bounds, full-region H_eff SPD/condition limit and the positive-gate precision
condition. Axial terms cannot spend those allowances a second time. The separate
field-target geometry check is presently blocked under §21; T4's density-agreement
margin is not a substitute target-realization tolerance.

### 5.6 Harmonic support, residual bounds and axial observation effects

The Gaussian integral is exact for the full quadratic model on the stated product
support. Actual finite walls, escape, nonquadratic force terms and unobserved excursions
must be covered independently; conditioning on a narrow axial camera window would
change the tested law. Extend the mechanical force map, conservative qualification,
thermometry and smoothness bounds to the full 3D volume. The permitted fluctuation-
averaging correction uses only driven A position moments as in §13. It never uses
an axial equipartition or passive covariance estimate to obtain a stiffness.

A quantitative way to bound the reduction remainder is to write
`U=U_quad+R(q,z)` from the independent force reconstruction. At each q let Q_q be the
normalized axial Gaussian in (U.A3), with mean
`z_star-kappa^-1 b^T(q-q_star)` and variance `k_B T/kappa`. On the mechanically
qualified axial interval, certify
`a(q)<=R(q,z)/(k_B T)<=b_R(q)` and its gradient/Hessian bounds. Let epsilon_Q(q) be
the Gaussian mass outside that interval and let t_plus(q) bound the actual outside
Boltzmann integral divided by the full quadratic integral at q. The latter needs an
independent energy/support bound; a Gaussian tail for the quadratic approximation
alone does not bound an arbitrary physical tail. Then

\[
L(q)=e^{-b_R(q)}[1-\epsilon_Q(q)]
\le \frac{I_{\rm true}(q)}{I_{\rm quad}(q)}
\le e^{-a(q)}[1-\epsilon_Q(q)]+t_+(q)=U_b(q). \tag{U.A15}
\]

For positive L, the dimensionless PMF correction lies in
`[-log U_b(q),-log L(q)]`; subtract its independently bounded value at q_star to
obtain the potential-difference remainder. Missing or infinite tail bounds cause
refusal. In the global uniform case `|R/(k_B T)|<=epsilon`, the PMF value correction
is at most epsilon and its difference from the centre at most 2 epsilon. This is a
bound, not an allocated numerical tolerance.

To qualify shape as well as potential values, retain derivative bounds and propagate
the corresponding independently specified physical-model set through (U.A14) and §25.
For fixed product support and justified differentiation under the integral,
`Hess_q U_PMF = E[U_qq] - Cov(U_q)/(k_B T)`. These expectations are calculated from
the independently measured physical potential and its certified remainder set, not
from a passive B covariance. Support-boundary terms must be included if relevant;
otherwise that non-product case is unqualified for this route. Finite force samples
alone do not establish uniform remainder or tail bounds. No nonlinear PMF is installed
as a new primary likelihood in this repair; the bounds only qualify the existing
harmonic approximation. Evaluate its error over the same scale/field envelope used
in T and include it in the existing bias, shape, centre and diagnostic budgets.
For an exponent scaled by beta, the same bound uses beta R/(k_B T) and axial Gaussian
variance k_B T/(beta kappa); a certificate only at beta=1 does not cover that envelope.

Finally, qualify defocus-dependent lateral tracking using independently moved 3D
reference targets. A linear choice of physical lateral axes may absorb a calibrated
projection; residual dependence of the lateral detector map/noise on hidden z must
fit §19's fixed observation law and its existing error budget. No per-frame B axial
estimate is introduced to rescue an invalid 2D observation model. Missing axial
support, unbounded defocus effects or nonuniform axial temperature invokes
AXIAL_REDUCTION_UNQUALIFIED or the existing observation/reservoir refusal as applicable.

### 5.7 Direct temporal consequence of eliminating z

A correct Gaussian lateral **density** need not have a two-dimensional Markov path.
For the independently calibrated full overdamped model, let
`A_3=(Gamma^(3))^-1 K^(3)` and let E_q project onto the two observed coordinates.
Under the canonical benchmark its lateral lag covariance is

\[
C_q(t)=E_q e^{-A_3t}(k_BT[K^{(3)}]^{-1})E_q^T,\quad t\ge0. \tag{U.A16}
\]

In general this is not `exp(-A_2 t) k_B T S^-1` for one constant 2-by-2 A_2.
The sufficient exact-closure condition `(A_3)_qz=0` makes the q equation autonomous;
otherwise require the independently driven 3D response and its observation transfer
to bound the deviation from T's retained 2D temporal model under §20. Fast axial
relaxation alone is not a numerical error bound.

Under exact closure, put `mu_eff=[(Gamma^(3))^-1]_qq`. Then
`A_2=(A_3)_qq=mu_eff S` and `Gamma_eff=mu_eff^-1`. Thus even in this exact case
the appropriate 2D drag is an inverse mobility block, generally the Schur complement
of the axial drag block, rather than Gamma_qq. Propagate its shared covariance with S.

Do not set `tau=gamma/k_eff` or take the qq block of Gamma^(3) without proving the
required dynamical reduction. Use independently qualified lateral response/time
bounds for the unchanged T11 schedule. If hidden-mode memory cannot fit the existing
residual and coverage/diagnostic requirements, refuse the realization under
TEMPORAL_MODEL_UNQUALIFIED, linked to AXIAL_REDUCTION_UNQUALIFIED. A 3D hidden-state
likelihood is not introduced by this repair and cannot be selected by V. This is a
direct dependency of Blocker A, not a reopening of T's unrelated statistical design.

### 5.8 Axial qualification predicate

No comparison packet is VALID unless all of the following hold on the full existing
joint 99.9% physical region, with bounded model errors also included:

1. Axial position, applied force, b and kappa are independently identified with complete
   covariance and provenance; the 3D force design and numerical solution are qualified.
2. K^(3) is SPD, kappa>0, and S is SPD; H_eff satisfies T's existing
   condition-number and numerical requirements. No clipping or SPD projection repairs
   a failed region.
3. The 3D conservative harmonic approximation, product-support reduction, residual/tail
   bounds, local temperature and lateral observation transfer are qualified.
4. The enlarged total log-beta uncertainty and bias satisfy 0.009/0.003 and 0.0005,
   respectively; axial shape/centre terms satisfy T.29 with every other contribution.
5. The lateral temporal reduction meets the unchanged T likelihood/bandwidth requirements.
6. The effective lateral fields satisfy the separately adopted target-realization policy;
   that policy is not yet specified and is blocked under §21.

Failure of items 1–5 produces AXIAL_REDUCTION_UNQUALIFIED with its precise dependency
reason (and existing subsidiary codes). Missing or failed item 6 produces the field
realization refusal in §28; unresolved target geometry is also recorded in axial
qualification so it cannot be hidden by an otherwise valid Schur calculation.
Specification of the axial method is complete for re-audit; **no axial measurement or
physical qualification has been performed**.

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

For the repaired primary construction, apply the following force balance in three
physical dimensions as specified in §5.2. Its two-dimensional reduction uses the
reduced force in (U.A8); a lateral-only fit is not the official field construction.
For the full 3D use of (U.2), K, Gamma, x and x-star mean K^(3), Gamma^(3), X and X_star.
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

The retained 2D construction below is the lateral-subset consistency check within
§5.3's primary 3D EIV fit. Its K and c are S and c_eff, and its force is the reduced
force (U.A8). The 24 lateral probes are retained within the 78-probe 3D cycle; they
cannot by themselves certify axial blocks or the official lateral marginal.
In this check, the force notation Gamma(phi) v_r below means the reduced 3D force
F_q-b kappa^-1 F_z, not a principal-block drag multiplied by lateral velocity alone.

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

Apply these existing lateral conditions to the effective field from §5, and extend
the force/nonlinearity measurements to the 3D volume and axial conditional tails
specified in §§5.3 and 5.6. The d=2 tail identity below still concerns the observed
lateral marginal; it does not qualify an unobserved axial tail on its own.

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

The A centre is the q projection of the **3D zero-imposed-drag centre** in (U.A6),
transferred to B through independently measured fiducials. Equivalently use S and
the reduced intercept c_eff in (U.A8), with their full shared covariance. The following
2D centre differential then applies:

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

The axial detector cross-talk/defocus qualification in §5.6 is an additional direct
dependency of reducing the physical state; it does not add a B axial observation or
change this likelihood. Retain T's model, with physical latent position X and detector output y:

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

The following 2D time formulas require the independently qualified dynamical closure
in §5.7. They cannot be applied to S and the qq block of Gamma^(3) by substitution.
The full 3D generalized modes and driven response supply the closure/error certificate;
only then may an equivalent 2D drag/drift and its bounds be used. A failure leaves T's
likelihood unqualified, rather than introducing a hidden axial state in V.

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

## 21. Field realization: narrow T-interface gap and binding refusal

### 21.1 Audit correction and source finding

The weak presence predicates in the failed U report are withdrawn as qualification
rules. Neither `T3/T0>1.02`, `r_k>1.02`, a barely resolved ellipse nor commanding the
nominal settings establishes realization of T's named challenges. In particular,
304 K and a stiffness ratio 1.021 are not admitted by any rule in this revision.
The earlier use of T4's ln(1.05) density-agreement margin as a circular-target
realization tolerance is also withdrawn.

**NARROW T-STAGE AMENDMENT REQUIRED.** Direct inspection of T §7 finds prospective
nominal targets and distinct field purposes, together with an explicit prohibition
on silently substituting temperatures or tolerances. T §§22.1–22.4 fixes information,
calibration limits and true-bridge complete-pass planning. T §20.3 requires at least
0.90 unconditional complete-pass probability when the correct bridge holds. That
is not a required discovery probability under a wrong-normalization alternative.
T §22.5 calculates planning discrimination for named 10% absolute and 5% relative
alternatives, but does not declare a minimum discovery probability for realized
field departures or a target-conformance region around its nominal fields.

Even interpreting those named alternatives as challenge benchmarks would not uniquely
supply target widths around 298/318 K, 100/210 micro-newtons/metre or the specified
ellipse. It would not supply an upper field departure, a matrix target tolerance or
a joint temperature/stiffness conformance rule. The 0.009/0.003 calibration requirements
limit measurement uncertainty; they do not choose how different the accurately
measured object is allowed to be from its target. The 5%/2% beta-equivalence margins
compare probability and energy; they are not actuator or field-construction tolerances.

The programme instruction for this repair is to **record this gap and keep field
qualification and V blocked**. T remains byte-for-byte unchanged. No numerical region,
new power objective or T amendment is adopted here. This is a pending normative
scientific decision, not a mathematical derivation that can be assigned to V.

### 21.2 Target objects and uncertainty convention

The following target matrices describe the **effective lateral mechanical curvature**
that T's two-dimensional density model tests, now unambiguously K_eff from §5, not an
unobserved plane block K_qq. Let R_30 be a rotation by 30 degrees in the independently
calibrated lateral physical axes.

| Named field | Preregistered target | Realized object used in analysis | Required region; current status |
|---|---|---|---|
| theta0 | `K0*=100 I` micro N/m; local T0*=298 K | Independently measured K_eff,0 and local T0 | Reference absolute scale, near-isotropic matrix and temperature conformity region: NOT SPECIFIED BY T |
| theta1 | `K1*=210 I` micro N/m; local T1*=298 K; target ratio 2.1 | Measured K_eff,1, K_eff,0, T1 and joint covariance | Target-centred stiffness/temperature region and preservation of confinement/relaxation/detector/heating challenge: NOT SPECIFIED BY T |
| theta2 | `K2*=R_30 diag(150,60) R_30^T` micro N/m; local T2*=298 K | Full measured K_eff,2, including cross term and orientation | Matrix target-conformity region with scale, eigenvalue separation and orientation jointly controlled: NOT SPECIFIED BY T |
| theta3 | `K3*=100 I` micro N/m; local T3*=318 K, reference local 298 K | Measured K_eff,3 and local T3, with reference covariance | Temperature and mechanical target-conformity region plus thermal-normalization discrimination objective: NOT SPECIFIED BY T |

Target values do not imply infinitely precise control. The missing object is a
**predeclared nonzero realization region** that preserves the scientific challenges.
Exact equality is not silently imposed as a replacement. No fixed eigenvector angle
is meaningful for an exactly isotropic reference; matrix conformity handles this
without inventing a reference orientation test at a degeneracy.

Retain U's existing joint **99.9% physical calibration region**, including all shared
and axial uncertainties and separately bounded errors. Let its projection to the
realized field parameters of one block be C_b. Once the programme adopts a target
region R_T and its challenge-preservation policy, qualification requires

\[
C_b\subseteq R_T,
\quad\inf_{\vartheta\in C_b}P_{\rm detect,j}(\vartheta)
\ge p_{j,*}\ \text{where that objective is adopted}, \tag{U.F1}
\]

together with every existing T information, precision, physical and model gate.
This uses the existing coverage convention; it adds no new confidence level.
C_b and R_T remain different objects. Large calibration uncertainty cannot make a
weak realization acceptable by merely making a confidence region overlap the target.
Both preparation blocks must pass independently, with every named field represented;
there is no averaging of a strong block and a weak block.

R_T and any required p_j,* are currently **missing mandatory scientific inputs**.
Consequently (U.F1) is not evaluable and no named-field comparison packet can be VALID.
This is the binding rule until the narrow T amendment is selected and independently
reviewed. Final V/H always uses measured S and T; it never substitutes a nominal
matrix or nominal temperature to manufacture target conformity.

### 21.3 Deterministic temperature-discrimination calculation

For the wrong fixed-reference normalization using 298 K,

\[
\beta_{\rm wrong}(T)=298/T,
\quad h_T(T)=\left|\log(298/T)\right|. \tag{U.F2}
\]

If the actual reference is T0 rather than exactly 298 K, the wrong model's within-block
log contrast has magnitude `abs(log(T/T0))`; the common 298 numerator cancels. The
absolute and contrast alternatives must not be confused. Correct normalization
predicts beta=1 regardless of the realized temperature.

Use exactly T's normal planning calculation, not a new test. At N*=450000,

\[
s_a=\sqrt{0.009^2+1.1025/450000}=0.0091350971533,
\quad s_c=\sqrt{0.003^2+2.205/450000}=0.0037282703765,
\]
\[
P^{\rm plan}_{\rm abs}(T)=\Phi\!\left[
\frac{h_T(T)-\log(1.05)-0.001}{s_a}-3.273078364\right],
\]
\[
P^{\rm plan}_{\rm cross}(T,T0)=\Phi\!\left[
\frac{|\log(T/T0)|-\log(1.02)-0.001}{s_c}-3.273078364\right]. \tag{U.F3}
\]

The 3.273078364 value is T.30's conservative first-step threshold for the 47-test
Holm/Bonferroni discovery family. It is not the 2.10 positive-equivalence critical
ceiling. The 0.001 retains both the 0.0005 bounded displacement and interval expansion.
These are signed named-direction discrepancy probabilities under the same normal
planning approximation, not achieved power or a new finite-N result.

For any actual qualification region, use the infimum of (U.F3) over its joint local
T/T0 region and the qualified standard-error envelope. The calibration covariance
already enters s_a/s_c through the fixed T architecture; it is not added again as
an independent thermometer error. Taking the infimum additionally guards against
an uncertain physical challenge. At departures outside the envelope where the
planning variance is justified, (U.F3) is only a formal extrapolation and cannot
certify a field.

The deterministic point-temperature comparison at T0=298 K gives:

| T | `abs(log(T/298))` | T.30 cross-field planning detection |
|---:|---:|---:|
| 304 K | 0.0199342149008 | 0.0002274435852, approximately 0.023% |
| 318 K | 0.0649578962748 | Approximately `1 - 5.16e-18` under the idealized planning approximation |

This quantifies the audit counterexample without treating the near-one number as a
laboratory guarantee. The old point boundary 303.96 K merely puts the wrong model
outside the 2% equivalence band. It does not preserve the nominal challenge or supply
high discovery probability.

If a future amendment selects p_* for this specific contrast objective, the hotter-field
point boundary at a known reference is algebraically

\[
T\ge T0\exp\{\log(1.02)+0.001+
 s_c[3.273078364+\Phi^{-1}(p_*)]\}. \tag{U.F4}
\]

Uncertain T/T0 requires the full-region inequality, not plugging in a convenient point.
Power alone provides a lower strength boundary, **not** a target-conformity width or
an upper acceptable temperature. For illustration of the unresolved decision only,
p_*=0.90, 0.95 or 0.99 would give point boundaries approximately 309.475, 309.894 or
310.683 K at a known 298 K reference. **None is adopted.** Even those power levels
would allow temperatures well below 318 K, demonstrating why target conformity is a
separate required scientific choice.

### 21.4 Stiffness challenge

T defines two circular target eigenvalues, 100 and 210 micro N/m, giving a nominal
factor 2.1 in **both modes**. It does not define a replacement scalar averaging rule
for materially nonproportional realized matrices. For exactly proportional effective
curvatures `S1=r_k S0`, omission of the stiffness change while using the actual field
temperature predicts `beta_wrong=r_k`. Its log effect is `abs(log r_k)`, and the
T.30 planning expression is (U.F3) with that effect in place of the temperature contrast.

For `r_k=1.021`, this expression is approximately **0.0005218639151**, or 0.0522%
named-discrepancy probability at the specified planning precision. It is not a
qualified version of the 2.1-fold challenge. A formal insertion of 2.1 gives an
extremely strong scalar effect; no finite-N guarantee outside the qualified variance
and nuisance envelope is inferred from that extrapolation.

For general realized S0,S1, retain the matrix pair and its uncertainty. The ideal
instantaneous wrong-reference-scale diagnostic is `2/tr(S0 S1^-1)` with a separate
T4 shape contrast; it is not a newly adopted definition of an admissible stiffness
ratio. The generalized eigenvalues of `(S1,S0)` express changes in both directions;
all are 2.1 at the target. A future target region must control the matrices' absolute
scales, their relative changes, shape and nominal temperature, so that detector
range, confinement/relaxation and heating dependence retain their intended challenge.
A power threshold for a scalar omitted-stiffness alternative alone does not determine
such a region. No acceptable interval around 2.1 is derived uniquely from T.

### 21.5 Matrix-level reference and ellipse conformity

Use T4's intrinsic matrix geometry as a **metric**, while keeping its density-test
threshold distinct from a presently missing target-conformity threshold. For a target
mechanical matrix S_j,* and realized S_j, let `S_j,*=R_j,*^T R_j,*` and form

\[
M_{j,*}=R_{j,*}S_j^{-1}R_{j,*}^T,\quad
s_{j,*}=\tfrac12\log\det M_{j,*},\quad
g_{j,*}=\|\log M_{j,*}-s_{j,*}I\|_{\rm op}. \tag{U.F5}
\]

The scalar s controls overall mechanical scale; g controls unequal modes, rotation
and off-diagonal structure in a coordinate-invariant comparison. Carry their joint
uncertainty from the full Schur/coordinate/temperature model. Pair them with actual
local T target conformity; comparing H alone could conceal compensating K/T departures.
At the ellipse target, the matrix in micro N/m is
`[[127.5,38.9711431703],[38.9711431703,82.5]]` in the specified frame. A full-matrix
region avoids arbitrary separate angle and eigenvalue tolerances.

For an ellipse with eigenvalue ratio rho and an omitted rotation psi, the diagnostic
shape contrast remains

\[
G_{\rm omit\ rotation}=\operatorname{arcosh}
\left[1+\frac{(\rho-1)^2}{2\rho}\sin^2\psi\right]. \tag{U.F6}
\]

It is 0.4700036292 at rho=2.5 and psi=30 degrees. Merely requiring this number to
exceed ln(1.05) admitted angles near 2.95 degrees in the failed specification; that
presence test is withdrawn. T4's bound applies to agreement of the actual density
with its measured potential, not to proximity of that potential to the designed
30-degree ellipse. T supplies no numerical bounds on s_j,* or g_j,* for target
realization, nor a discovery-power floor against each weakened geometry challenge.
The reference likewise requires scale and matrix target conformity; it cannot be
redefined by an arbitrary accurately measured anisotropic trap.

### 21.6 Exact pending programme decision and dispositions

The narrow amendment must select and preregister:

1. A nonzero target-conformance region for each local T and effective lateral mechanical
   matrix, including the reference, the near-2.1 two-mode change, and the specified
   rotated ellipse. It must state treatment of correlations and be applied by the
   existing joint 99.9% containment rule (U.F1).
2. The quantitative meaning of preserving each named challenge: for example minimum
   discovery probabilities for the named wrong-normalization/wrong-stiffness/wrong-
   geometry alternatives, or an explicitly selected minimum retained nominal effect
   under the fixed T inference and information rules. Any chosen objective needs
   target conformity as well; it is not sufficient alone.
3. A versioned region/predicate and pre-B qualification protocol, with conservative
   treatment of realization uncertainty and applicability of the planning envelope.

Reasonable scientific choices include retaining a specified portion of nominal
challenge strength or requiring a declared detection power such as 0.90, 0.95 or 0.99
for the named alternatives. These are **decision families, not recommended or adopted
numbers**. The acceptable target widths and matrix neighbourhoods express experimental
purpose; neither likelihood algebra nor a calibration certificate selects them.
Changing the 450000/408164 information targets, beta margins, block count or unrelated
T gates is outside this amendment.

Once a region exists, containment establishes qualification. A region crossing its
boundary is FIELD_REALIZATION_UNRESOLVED and cannot yield VALID; a certified outside
realization is FIELD_REALIZATION_OUT_OF_SPEC. The latter invalidates the named record
for the preregistered design and requires separately authorized reconstruction or
reacquisition, not a beta/theorem failure. While the region itself is missing, use
FIELD_REALIZATION_SPECIFICATION_MISSING. This currently blocks **all eight named
records**, including theta0 and both preparation blocks. Heating of theta1 is evaluated
against its own local-temperature target region, not merely the 318 K arm's region.

The downstream Schur/uncertainty formulas are specified. Numerical target predicates,
field-validity release and their V validators depend on this unresolved T decision.
U9 remains GAP; no wording elsewhere in this report authorizes a weaker challenge.

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
expose order/thermal-history problems; it does not prove their absence. Each block must
also separately satisfy §21's adopted realization policy; that policy is presently
missing, so neither block can be released as a valid named-field experiment.

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
- full 3D force/displacement fit variables, six stiffness entries, three centre/intercept
  entries, axial sensing/axis-map nuisances and plateau mean covariances; the derived
  Schur matrix and q-centre retain all shared covariances under §5.4;
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

Let `C_phi` denote the complete auxiliary covariance, now including the axial variables
of §5.4, and use analytic or independently verified Jacobians. Here K=S and H=H_eff;
the Schur Jacobian and its nonlinear remainder precede the existing propagation.
No new axial uncertainty or bias allowance is added. For the physical Hessian and potential,

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
| AXIAL_REDUCTION_UNQUALIFIED | Missing/unidentified axial blocks or provenance, nonpositive axial/full matrix, unqualified harmonic/support/dynamical reduction, or failed propagated budgets/geometry; no VALID packet |
| FIELD_REALIZATION_SPECIFICATION_MISSING | Target region or challenge-preservation policy not adopted; CURRENT blocking state for all named records |
| FIELD_REALIZATION_UNRESOLVED | Existing joint 99.9% region straddles an adopted realization boundary; no VALID packet |
| FIELD_REALIZATION_OUT_OF_SPEC | Independently certified outside the adopted target region; invalid for the named experimental role, not a beta/theorem failure |
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
| Full physical field | K^(3), K_qq, K_qz, K_zz, full zero-force centre/intercept, local T, 3D coordinate/force maps and complete covariance |
| Official lateral field | K_eff=S, q-star, U_eff difference function, H_eff=S/(k_B T), V function; unambiguously the matrix for B's lateral density |
| Axial qualification | 3D calibration and sensing provenance; Schur correction/Jacobian/nonlinear covariance; support/remainder, geometry and dynamical-reduction certificates; qualification/refusal result |
| Field realization | Nominal target, measured effective field/T and joint uncertainty, adopted target-region/power predicate and version, per-field/per-block status; missing policy explicitly blocks VALID |
| State space | Full 3D calibration state and 2D observed lateral marginal, product measure/support, axial integration/remainder evidence, qualified spatial range and FOV/escape qualification |
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
| Mechanical K and centre | Balanced 3D driven EIV fit and lateral Schur reduction | Full tensor/centre covariance; example 0.0015 / 0.0007 contributions; T shape/centre precision | Conditional; mean-displacement precision can improve with A repetition, common force errors cannot | NOT MEASURED |
| Coordinates | Traceable grid, interferometric stage, fiducials | Example 0.0005 / 0.0002 contributions; nonsingular map and bounded distortion | Conditional; x/y/shear/orientation and frame transfers all matter | NOT MEASURED |
| Noise/shutter | Immobilized and driven reference targets, optical timing pulses | Example 0.0005 / 0.0002 contributions; noise ratio <=0.05, exposure/timing constraints | Hardware dependent; photon count and frame rate can conflict | NOT MEASURED |
| Relaxation/Markov model | Independent driven response and generalized mechanical modes | Finite positive tau bounds, non-alias band and endpoint/coverage residual bounds | Significant risk from fluid memory, especially for stiff traps in low-viscosity liquid | NOT MEASURED |
| Axial marginal reduction | 3D chamber drag and calibrated holographic position; Schur complement | Full-region axial/full SPD, full covariance/nonlinear bounds, existing total scale/shape/bias budgets and 2D temporal closure | Conditional; axial normal drag, optical-height transfer and hidden-mode memory must be qualified | NOT MEASURED |
| Named-field target conformance | Versioned region plus challenge-preservation objective | §21; no new numeric width or power floor adopted | BLOCKED: narrow T-interface decision required | NOT MEASURED |
| Harmonic/conservative domain | Full force map plus justified remainder bound | Joint log bias <=0.0005, shape/current/centre requirements and spatial-tail domain | Conditional; local derivative at the centre is not enough | NOT MEASURED |
| 298/318 K arm | Same standards, direct local maps and viscosity curve | Target-conformance/power policy missing (§21); differential covariance <=0.003 after all sources | Thermally accessible in principle; local homogeneity and long-duration stability unestablished | NOT MEASURED |
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
is unchanged.** No historical F-stage implementation is resumed. The bounded repair
makes the prospective field construction explicitly K^(3) to S to H_eff; release
of any named field additionally remains blocked by the target-realization gap in §21.
This does not reopen the unchanged F2 specification or amend old F4 authority.

## 33. U1–U12 disposition

Here COMPLETE means that the required method, inputs, uncertainty dependencies,
acceptance/refusal rules and later-stage interface have been specified. It does not
mean that future packets are VALID or that any numerical apparatus qualification
has been achieved.

| Item | Disposition | Closure in this specification |
|---|---|---|
| U1 Branch-A independence | COMPLETE | Four typed streams, no B-derived field/noise/centre, pre-B construction and locks |
| U2 Mechanical force/stiffness | REPAIRED AS SPECIFICATION | Full 3D driven EIV identification, axial localization/drag, Schur reduction and conservative harmonic qualification; re-audit required |
| U3 Viscosity | COMPLETE | Actual-batch capillary/density route, fixed temperature interpolation, valid domain and joint eta/T covariance |
| U4 Bead radius | COMPLETE | Per-bead optical metrology with material/boundary qualification and thermal transfer |
| U5 Hydrodynamic drag | COMPLETE | Full resistance tensor, measured walls/flow, physical and numerical validity, memory qualification |
| U6 Thermometry/local T | COMPLETE | Traceable bulk anchors plus calibrated local maps, heating/gradients/perturbation and common-reference covariance |
| U7 Coordinates/orientation | COMPLETE | Full affine maps, distortion bound, force transformation and eigenspace-aware orientation |
| U8 Observation calibration | COMPLETE | Independent R, shutter/timing law, range and noise-model refusal; no passive thermal calibration |
| U9 Fields/blocks | GAP | Nominal T targets/orders retained; target-conformance regions and challenge-preservation objective missing; no weak-field substitution or VALID packet |
| U10 Calibration covariance | REPAIRED AS SPECIFICATION | Existing hierarchy/budgets retained; Schur/axial terms and nonlinear correction propagated with all shared dependencies |
| U11 Qualification/refusal | REPAIRED AS SPECIFICATION | AXIAL_REDUCTION_UNQUALIFIED and missing/unresolved/out-of-spec realization states block all VALID comparison packets as applicable |
| U12 Packet/lock | REPAIRED AS SPECIFICATION | Full 3D blocks, official H_eff, axial covariance/provenance and mandatory versioned realization policy/status added; old lock semantics retained |

The previous global COMPLETE/NONE disposition is withdrawn. Unrelated methods are
preserved under the supplied audit scope; this is not a new independent clearance.
HUMAN/PROGRAMME SCIENTIFIC DECISION REQUIRED TO CLOSE U9: the narrowly specified
realization regions and challenge-preservation objectives in §21.6. For this repair,
the user chose to record that gap and retain the block; no further decision is assumed.
Physical measurements and independent re-audit remain future requirements.

## 34. U-to-V handoff — not begun

Only after the narrow T-interface decision is adopted, U is independently re-cleared
and separate authorization is given, V must:

1. Implement the semantic packet schema, units/types, covariance/reference graph,
   immutable raw references and completeness validation. Distinguish actual data,
   synthetic parameter injection, target settings and exact constants.
2. Implement the selected full 3D mechanical EIV estimator, axial sensing/force ingestion,
   Schur reduction and its covariance/nonlinear bounds, coordinate transformations and
   the required lateral dynamical closure. Preserve common Gamma–K and eta–T dependencies;
   validate axial and field-realization refusals without replacing measured H_eff by a target.
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
because this document exists. **V is blocked by the missing T realization policy and
independent U re-audit.** V must not choose an axial-reduction route, target tolerance,
weaker temperature/stiffness/ellipse challenge or new power objective. It must implement
the scientifically adopted validators exactly. W authority adoption and physical
execution require their own subsequent gates.

## 35. Physical-execution handoff — not begun

A later separately authorized physical stage must obtain and preserve:

- a fully identified apparatus/preparation manifest and traceable certificates;
- actual liquid composition, density and viscosity curve, including reference checks,
  heating/cooling repeatability and model/domain bounds;
- actual per-bead radius, material/shape/boundary qualification and thermal transfer;
- measured wall geometry, fluid transfer, background flow and resistance correction;
- full three-axis force/displacement and axial position data, K^(3) and its blocks,
  full zero-force centre, Schur K_eff/H_eff and covariance, nonlinear/nonconservative
  residual and support bounds, and independently driven lateral-reduction qualification;
- local temperature maps, bulk anchors, laser-heating/gradient/probe-effect bounds and
  record-duration stability at every field setting;
- coordinate, fiducial, detector, shutter, synchronization, localization and digitization
  calibration at the actual operating conditions;
- the complete primitive law/covariance, shared-standard graph, bounded errors,
  full-region geometry and uncertainty predicates, and per-block target-region checks
  under a separately adopted policy; until that policy exists these checks remain blocked;
- the resulting fixed sample counts, durations, settling/burn-in schedule and independent
  monitor envelopes, followed by separate packet locks before passive comparison.

All of these are **future measurements**, not results of U. The actual fluorescence
curve, viscosity nodes, radii, chamber dimensions, calibration covariance and camera
parameters remain unpopulated. The handoff does not collect even one observation,
run a trajectory or authorize the later optical-trap experiment.

## 36. Bounded repair status and static verification record

Independent U audit: **NOT CLEARED**. This revision specifies the axial repair and
records/contains the realization defect; it does not self-audit or claim independent
clearance. **U9 remains GAP. FIELD QUALIFICATION AND V REMAIN BLOCKED.** T has not been
amended because the user chose to record the missing normative decision rather than
supply a new field-target policy. The next scientific action is the narrow programme
review of §21.6, followed by independent re-audit; neither is performed here.

The Gaussian square completion, determinant factorization, lateral inverse-block
identity, Schur differential and pure axial-coordinate invariance are derived in §5.
They and a shared-covariance propagation example were checked in exact rational
arithmetic on a nonzero-coupling matrix. The specified 13-direction, signed,
three-radius 3D probe design has rank 20 for scalar cubic terms. T.30's normal planning
calculations were evaluated directly, without random draws or trajectory data.
The rational example uses A=[[4,1],[1,3]], b=(1,1/2), kappa=2, hence
S=[[7/2,3/4],[3/4,23/8]], in abstract consistent units. Its shared input covariance
is I/10000 + 11^T/40000 in the six-component order of (U.A10). The 13-direction
homogeneous polynomial ranks are 1, 3, 6 and 10 for degrees 0–3; the three signed
amplitude levels separate the degrees, so direction normalization preserves rank.
The effective-drag identity in §5.7 was also checked on a rational autonomous example.


| Deterministic check | Result |
|---|---|
| Gaussian completion/inverse-block identity | S=A-b kappa^-1 b^T and `(K^(3)^-1)_qq=S^-1` checked on the rational example |
| Schur differential and axial reparametrization | Component Jacobian and exact pure-z-scaling cancellation checked on that example |
| Nonzero-coupling algebraic example | r=0.1363636364; plane-only beta=0.9268292683; plane-only G=0.0733017371 |
| 3D probe design | 78 nonzero plateaux; scalar cubic monomial rank 20 |
| T planning contrast standard error | 0.0037282703765 at 450000 equivalents |
| 304 K wrong-normalization alternative | Named cross-discrepancy planning probability 0.0002274435852 |
| 318 K wrong-normalization alternative | Planning failure tail about 5.16e-18; not an achieved-power claim |
| Stiffness ratio 1.021 alternative | Named cross-discrepancy planning probability 0.0005218639151 |
| Illustrative unadopted p*=0.90/0.95/0.99 | Point thermal lower boundaries 309.475/309.894/310.683 K; these are not target-conformance regions |

These are mathematical examples and planning formula checks, not calibration packets,
physical results, finite-N validation or an independent audit. No scientific module,
RNG, Monte Carlo, model trajectory, calibration acquisition, optical-trap experiment,
old F-stage repair or official campaign is run. Execution authorization remains FALSE.

Repair starting SHA: `7c3346462f5aeed5dfef176ecaa4e5e9070e847a`.
Cleared T SHA: `ebcf2641fa2d8fe4ab95fef011e96fe53feeadc6`.
Failed-U source SHA-256:
`c627ff3df0f4797709e2473f97122751268cd2870c444c91ef30dc58256d6c79`.
The only authorized changed file in this repair is this U report. The starting snapshot
covers 2,990 tracked files; the other 2,989, including T, all authority, Book 1, code,
plans, contracts and seal, are byte-identical in the completed comparison. Strict
JSON parsing and AST-literal inspection reconstruct the unchanged analysis identity
from 12 sources and execution identity from 19 validation sources plus the driver,
matching §2. Both execution flags remain FALSE, seal state remains PRE_DRIVER and no
official validation result exists. The report remains outside both identity preimages.
The untouched method sections and F2 specification were compared directly; section,
equation, local-link and table structure checks passed. Complete-diff review and
exact-path staging precede one local repair commit; its full SHA and report hash are returned
in the completion message. **PUSH: NO.** The baseline DeltaJ defect remains non-blocking
here and must be repaired before W; it is not edited in this task.
