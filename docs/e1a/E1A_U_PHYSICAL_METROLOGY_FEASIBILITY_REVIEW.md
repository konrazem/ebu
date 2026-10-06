# E1a U physical/metrology feasibility review

**Assessment date:** 2026-10-06. **Status:** non-controlling scientific assessment, awaiting independent audit. **U-FEASIBILITY PACKET: REFUSE.**

The one frozen candidate, **UF-01**, cannot satisfy the existing deterministic gates. Even granting its proposed calibration law and an otherwise perfect apparatus, its **2 nm relative centre-registration uncertainty makes T.29 fail at infinite record length**, and its **2 nm per-frame localization noise exceeds T's 0.05 noise ratio in every field**. These are apparatus-choice failures, independent of V6's incorrect treatment of nonlinear Schur uncertainty. A complete physical residual-bias certificate and temporal-response certificate are also absent. Correcting V accounting alone cannot turn this candidate into a qualified replacement benchmark.

This is a refusal of **one apparatus proposal**, not proof of a generic limitation of the U route and not a T/U contradiction. No change to T or U authority is justified by these findings. A future V-only replacement still requires a different, independently defensible prospective apparatus packet; this report neither constructs nor authorizes one.

**V: NON-RELEASE. W: BLOCKED. Physical execution: NOT AUTHORISED.** No V7, estimator, validation runner, Monte Carlo, finite-N calibration, confirmatory seed, physical experiment, authority amendment or push was performed. Only this report is to be committed.

## 1. Scientific coordinate and interpretation

Starting branch: `codex/v6-minimal-recovery-assessment`. Starting commit: `e51dd077813340d3616d76644db5f3f888e04682`. The working tree was clean. Origin is `https://github.com/konrazem/ebu.git`; locally cached `origin/main` was `660d6e5a56cb096fe6d1e4d202f592155d982c79`. No fetch or claim about current remote equality is made; this is the requested local report commit on the recovery branch.

Read in the requested order: repository AGENTS, frozen physical foundation, theory baseline, S equilibrium anchor, T including T11a, U including its repaired axial/temporal and realized-field interfaces, then the committed V6 recovery assessment. The current user brief supplies the controlling **CLEARED** status for T, T11a and U; historical audit-pending headings in their files were not rewritten. V6 is evidence of the failed benchmark, not U authority.

The binding references are [T](E1A_MINIMAL_EQUILIBRIUM_EXPERIMENT_DESIGN.md), especially §§11, 15, 18, 22.4, T.29 and T11a; [U](E1A_BRANCH_A_PHYSICAL_CALIBRATION_QUALIFICATION.md), especially the full-3D Schur route, physical calibration sections, §20 and U.18–U.24; and the [prior recovery decision](EBU_V6_FAILURE_CONSOLIDATION_AND_MINIMAL_RECOVERY.md). The foundation defines the physical accounting; the S equilibrium identities do not supply a Markov approximation or instrument accuracy.

Three different quantities are kept separate throughout:

1. **An exact necessary-condition failure**, calculated inside the candidate's proposed law. One admissible nominal point is enough to disprove a universal gate.
2. **A conditional mathematical diagnostic**, such as a scalar covariance sub-block or bulk-fluid relaxation time. It is not a complete physical bound.
3. **An unestablished physical bound.** Its entry is `NE`, not zero, a fabricated allowance, or a measured failure. `NE` requires REFUSE under this brief.

The frozen selection below was saved before final arithmetic. Its UTF-8 section, from its heading through its final paragraph, has SHA-256 `c32f14f5c3b51e503fa01fea7ba3d274048ead48e73f14a48ecd2d9df2fbf088`. It is reproduced verbatim. This local hash documents sequencing and immutability of the proposal; it is not an authority freeze or independent timestamp certification.

## Frozen candidate UF-01 — conventional two-camera drag/holography packet

Prospective selection, 2026-10-06. This is a single conventional apparatus proposal, not an achieved apparatus or a PASS witness. It retains the previous benchmark's 0.5 micrometre bead scale and 2 nm localization/registration scale, now giving those numbers explicit physical roles. Preliminary dimensional inspection already flags centre registration as a possible problem; no claim of blind selection is made. The values below are fixed before the final arithmetic. No second candidate or post-calculation tuning is permitted in this review.

- Two fresh preparations: separate solid silica spheres, separate newly mixed liquid aliquots and separate sealed glass chambers. Block 1 field order 0,1,2,3; block 2 order 3,2,1,0. Common reference instruments remain common.
- Radius target a=0.500 micrometres at 298 K in each block. Target nominal radius at 318 K is also 0.500 micrometres for calculation only; radius is independently measured there, with nonzero thermal-change uncertainty. Silica density 2200 kg/m^3 is a nominal inertia input, not certified. Newtonian water with 1 micromole/litre rhodamine B, no added salt or surfactant, nominal ambient pressure 101325 Pa; batch composition, adsorption and hydrodynamic-radius transfer require qualification.
- Nominal liquid law eta_nom(T)=0.000890 exp[-0.022(T-298)+0.000100(T-298)^2] Pa s over 293--323 K. This deliberately explicit water-like engineering curve is not an IAPWS or mixture calibration. The actual U auxiliary law is log-linear interpolation of independently measured 1 K batch nodes, five ascending and five descending readings per node, independent density, and withheld half-kelvin checks. Temperature dependence, node covariance and interpolation residual remain load-bearing.
- Rectangular sealed chamber 2 mm by 2 mm by 200 micrometres, bead nominally at its centre: 100 micrometres from each broad face and 1 mm from each side. Full finite-domain no-slip incompressible Stokes traction map defines the steady resistance tensor. No sum of wall formulae is used as the certified resistance. Slip, roughness, nonsphericity and numerical traction error need separate residual bounds.
- Four effective lateral targets S in micronewtons/metre: S0=100 I, S1=210 I, S2=R(30 degrees) diag(150,60) R^T, S3=100 I. Temperatures T0=T1=T2=298 K and T3=318 K. In every field kappa=20 micronewtons/metre, b=(5,0)^T micronewtons/metre, A=S+bb^T/kappa, K3=[[A,b],[b^T,kappa]]. Centre target is zero. These are intended full force Hessians, not measured claims. A 1064 nm high-NA optical trap with static astigmatism, independently calibrated steering and power/temperature setting supplies the engineering architecture; no unverified laser-power-to-stiffness conversion is used as the force standard.
- Branch A uses the U 13 undirected nonzero {-1,0,1}^3 directions, both signs, three nominal displacement amplitudes (10,20,40 nm), at least three reversed cycles plus zero plateaux. Independent interferometric stage velocity and holographic 3D displacements feed an errors-in-variables full 3D force fit. Initial fit is unrestricted 3 by 3; symmetry is accepted only after the curl/residual check. Centre and stiffness are jointly propagated. Through-focus Lorenz--Mie bead characterization, calibrated coordinate standards and actual-batch viscosity supply the force chain; no B equilibrium fit supplies any A force scale.
- Branch B is a separate lateral camera channel, with independently cross-calibrated nominal P=I, box shutter 2 microseconds, nominal independent Gaussian localization standard deviation 2 nm per coordinate per frame. This is an engineering noise target at the specified exposure, not a claim that video-holography precision transfers to microsecond exposures. Nominal A-to-B relative fiducial-registration standard uncertainty is 2 nm per lateral coordinate, shared within a preparation; it is not the common origin that cancels. Residual detector-offset uncertainty is 0.2 nm per coordinate per record. Mechanical A-centre fit uncertainty is 1 nm lateral and 5 nm axial. Reference points are immobilized and translated, at matched photon levels and across the full axial range.
- Common frame/excitation timebase: 1 microsecond hardware frame tick, relative clock standard uncertainty 0.0001, relative shutter-duration standard uncertainty 0.001. Select the largest tick satisfying T's Delta<=min(120 microseconds,tau_fast/5) over the qualified A region. Use T's burn-in and smallest permitted count rule unchanged, not an assumed final Delta or N.
- Independent driven response: optical-centre steering in both lateral axes and signs, DC plus U's four frequencies/octave from 0.05/tau_slow through pi/Delta, including both mechanical rates and upper endpoint; 8 timed phases/cycle and 100 cycles/probe. A separate 1 MHz reference detector and phase-locked excitation permit phase sampling without claiming the B camera resolves all phases in a single period. Nominal relative steering-amplitude uncertainty 0.001 and phase uncertainty 0.1 degree; continuous between-probe and high-frequency-tail residual bounds are not supplied by those numbers.
- Proposed mapped spatial region: |q_x|,|q_y|<=100 nm, |z|<=250 nm. No harmonic, outside-tail or 3D conservative-force certificate is assumed from this box. Bath control targets: within-record |Delta log T|<=0.0002, curvature log drift<=0.0005, relative centre motion<=0.1 nm; these are targets, not bounds. Wait for physical settling, then at least 20 upper slow relaxation times with T's initial-condition bounds.

The following is the frozen **proposed stochastic auxiliary law**, in standard-uncertainty units. Independent latent standard normals are used only as an explicit prospective measurement model; they are not evidence of achieved uncertainty or of bounded model discrepancy. Repeated source IDs below denote the same latent variable, not a new independent draw.

| Source ID | Scope and proposed standard uncertainty |
|---|---|
| ETA-REF | Global log-viscosity reference 0.002 |
| ETA-SLOPE | Global log-viscosity tilt 0.001*(T-298)/20 |
| ETA-DENS | Independent batch density-to-dynamic-viscosity scale 0.0003 per block |
| ETA-NODE | Independent log-viscosity node 0.0004 per block and each integer K node; shared by records using that node |
| TEMP-REF | Common thermometer offset 0.02 K, used in viscosity node temperatures and all local thermometry |
| TEMP-BLOCK | Thermometer transfer 0.01 K per block, common to its viscosity and local-temperature readings |
| TEMP-NODE | Temperature reading 0.01 K per batch node |
| TEMP-LOCAL | Independent local fluorescence/temperature reading 0.03 K per record |
| RADIUS-REF | Common optical-radius scale 0.001 |
| RADIUS-BEAD | Per-bead radius log error 0.002, shared within block |
| RADIUS-HOT | Additional measured hot-radius log error 0.0005 per block, zero coefficient in cold fields |
| GEOMETRY | Per chamber: each of six face distances 0.2 micrometres; each of three orientation angles 0.0001 rad; bead offset determined in the same 3D coordinate map |
| VELOCITY-REF | Common independent velocity scale 0.0005 |
| VELOCITY-BLOCK | Stage-transfer log scale 0.0003 per block |
| VELOCITY-FIELD | Drive-velocity log scale 0.0002 per record |
| COORD-A | Global coordinate matrix M_A=exp(0.0005 z I+0.0002 Z), Z having nine independent unit-normal entries; translations use the shared origin below |
| COORD-AB | Relative lateral matrix P_rel=exp(0.0002 Z_b), four independent normal entries per block; common COORD-A also enters the B map |
| ORIGIN | Common 3D origin, 100 nm per axis; cancels in correctly registered differences |
| FIT-K | Conditional sufficient-summary full K3 fit error: six independent symmetric and three antisymmetric orthonormal matrix-basis coefficients, each 0.001*Kref, Kref=100 micronewtons/metre, per record; no second independent copy of the raw fit error |
| FIT-CENTRE | Conditional centre-fit residual (1,1,5) nm per record; c=-K3 x_star retains induced stiffness/intercept covariance |
| FIDUCIAL-AB | Relative A-to-B transfer (2,2) nm per block, independent of common ORIGIN and mechanical centre residual |
| DETECTOR-OFFSET | (0.2,0.2) nm per record |
| NOISE | R_obs=4 nm^2 exp[(0.02 z_global+0.01 z_record)I+0.01(z_1 D+z_2 E)] in B-coordinate units; D=diag(1,-1), E=[[0,1],[1,0]], independent record anisotropy variables |
| CLOCK | Global relative clock error 0.0001; the same variable affects stage velocity if inferred from displacement/time, acquisition and driven phase; VELOCITY-REF is additional scale error conditional on this clock |
| SHUTTER | Common log exposure error 0.001 |
| DRIVE-RESPONSE | Per-block/axis steering log gain 0.001 and phase 0.1 degree; the common clock remains shared |

This factor model covers the chosen measurement uncertainties. It does not turn missing calibration certificates into data. It does not assign probabilities to slip, viscosity interpolation error, optical/hydrodynamic-radius mismatch, nonlinear force, nonconservative force, thermometry spatial transfer, detector-law mismatch or hydrodynamic memory. Their bounded residual set has to be established separately; none is frozen to zero or to an invented 0.00025 allowance.


## 2. Physical plausibility and evidence boundary

UF-01 is a conventional engineering proposal with some demanding metrology targets, not an exotic mathematical construction. Its errors are intentionally nonzero. The references below establish components or methods, not EBU qualification.

| Candidate item | Evidence classification and implication |
|---|---|
| Silica sphere, submicrometre radius, water, infrared optical trapping, 60–210 micro N/m lateral stiffness | Established experimental class; the specified full tensor and nonzero coupling are engineering targets. Franosch et al. discuss silica/polystyrene spheres in water and demonstrate stiff traps and fast detection in their own specimens [L4]. No claim that their measured tensor equals UF-01's. |
| Three-dimensional Lorenz–Mie characterization | Lee et al. demonstrate approximately 1% single-image radius/index characterization, nanometre lateral precision and 10 nm axial resolution [L1]. That supports the method, not UF-01's 0.2% per-bead standard uncertainty, 5 nm fitted axial centre or optical-to-hydrodynamic-radius accuracy. Averaging addresses random error, not an unbounded model offset. |
| Dyed liquid and nominal eta(T) | The explicit curve is a water-like target. IAPWS concerns ordinary water [L2]; it does not calibrate this mixture. Actual-batch capillary viscosity and independent density follow U and established viscometry [L3]. The 0.2% reference and 0.04% node targets are unverified engineering allocations. |
| Two fresh liquid batches and chambers | Straightforward preparation architecture. Independent preparation errors and common standards must coexist. A shared nominal recipe does not make the two viscosities identical. |
| Chamber and wall distances | Geometrically feasible engineering dimensions. Confined-sphere mobility is affected by both walls [L5]. Large wall distance is not a certificate that the correction or its uncertainty is zero. No verified finite-chamber traction calculation is supplied. |
| Temperature fields and 0.03 K local repeatability | Ross et al. report fluorescence precision spanning 0.03–3.5 degrees C depending on averaging, at their spatial/time resolution [L6]. Their precision is not accuracy, a bead-scale hotspot bound, or a demonstration at UF-01's illumination. Mixture/optics-specific calibration remains required [L7]. |
| Full driven force/displacement fit | Independent stage forcing and optical displacement are established methods. Tolic-Norrelykke et al. demonstrate driven calibration [L8], but combine it with thermal spectra; that shortcut cannot supply U's independent A force standard. UF-01 retains independently measured eta, radius and geometry. |
| 2 nm localization at 2 microseconds; 1 MHz reference channel | Nanometre/high-bandwidth detection has been demonstrated with interferometric apparatus [L4, L9]. Transfer to this camera/exposure/photon regime is an unsupported performance assumption. Even granting it, UF-01's noise ratio fails. |
| 2 nm A/B registration; coordinate/centre fit targets | Reasonable nanometre-scale metrology targets, not achieved accuracy. The relative registration is far above the precision demanded by this T field family. It is not removable by reusing a global origin. |
| Clock, shutter, steering amplitude/phase targets | Engineering targets. Measured shutter weighting and motion blur are essential [L10]; a box kernel and a fast clock do not demonstrate their own calibration. Eight-phase equivalent-time response also needs repeatability. |
| Gaussian noise, conservative harmonic force, no-slip boundary and stationary reservoir | Useful candidate laws whose applicability must be independently qualified. Treating them as exact physical facts would be unsupported optimism. The report does not do so. |

## 3. Full physical dependency and one joint stochastic law

### 3.1 From liquid and geometry to stiffness and centre

Let g contain all six measured face distances, wall orientations, bead position/shape and boundary-condition parameters. For each of three unit translations solve, in the actual finite fluid domain,

\[
-\nabla p+\eta\nabla^2u=0,\qquad \nabla\cdot u=0,
\]

with no-slip on the stipulated surfaces and prescribed bead-relative translation. Integrating traction gives the resistance columns. Linearity in eta yields

\[
\Gamma^{(3)}=6\pi\eta(T;\zeta)a\,C(g/a,\chi),\qquad F_r=\Gamma^{(3)}v_r.
\]

The symmetric positive resistance follows from reciprocal work and positive viscous dissipation for this *specified* passive boundary-value problem. A numerical enclosure, boundary validity, axial flow transfer and residual slip/shape bounds are still needed to identify the actual apparatus with it. There is no certified numerical C in this packet. Using C=I below is restricted to explicitly labelled bulk-fluid time-scale diagnostics, never the force qualification.

The force balance is `F_r=K3 x_r+c+force-model residual`. Fit all three responses against the independently measured velocities and positions, including their errors; initially retain antisymmetric coefficients. The balanced paired design motivates the proposed conditional fit-summary covariance, but does not prove that covariance is achieved. In displacement-map notation, if `x-x_star=M v`, then `K3=Gamma M^{-1}`. The overdamped drift is `Gamma^{-1}K3=M^{-1}`: the same drag standard can cancel in the *steady inferred time constant* while remaining fully present in stiffness. Keeping Gamma and K3 as independent fitted errors would destroy that dependency.

Under a 3D coordinate change `x=M_A u`, transform the force/work covector consistently: `K_x=M_A^{-T} K_u M_A^{-1}`, `c_x=M_A^{-T}c_u`. If the fit is instead expressed using physical force components and raw camera coordinates, the intermediate conversion differs; all forces and coordinates must first be brought into the same work-conjugate basis. Centre propagation is

\[
x_*=-K_3^{-1}c,\qquad dx_*=-K_3^{-1}(dc+dK_3x_*).
\]

A fitted centre summary is not a second independent intercept observation: `c=-K3 x_star` induces its covariance with K3. Global origin, relative A/B registration and detector offsets have different roles.

### 3.2 Exact axial marginalization

For every allowed joint primitive assignment use the exact maps

\[
S=A-\frac{bb^T}{\kappa},\qquad H=\frac{S}{k_BT},\qquad
\Sigma_{\beta}=\beta^{-1}H^{-1}.
\]

For `Delta kappa=u kappa`, the exact difference from the first-order Schur expansion is

\[
R_S=-\frac{(\Delta b-u b)(\Delta b-u b)^T}{\kappa(1+u)}.
\]

This expression is negative semidefinite and rank at most one when the denominator is positive. It is a property of propagation through the uncertain nonlinear map, not a new physical source. The full auxiliary push-forward is `z -> measurements -> Gamma, K3,c -> S,H,x_star,P,R,w -> profiled expected score`. Any nonlinear change of mean, variance or coverage must be retained. No extra V-style Taylor-remainder bias is added to that exact map. If a linear approximation were actually used, its difference from this map would need its own approximation/coverage check.

For this refused packet, there is no justified *complete physical* push-forward enclosure: C and several physical residual laws are unqualified. Therefore no full nonlinear variance or physical 99.9% region is asserted. The Gaussian auxiliary proposal is a local measurement law, not permission to integrate through singular/indefinite K3 or to project an invalid fit back to SPD. Such outcomes must refuse qualification; no clipping or renormalization is silently performed.

### 3.3 Shared eta/T and radius dependency

Write viscosity calibration node abscissae as `t_bk=k+e_ref+e_block,b+e_node,bk` and local temperature as `T_bj=T_j+e_ref+e_block,b+e_local,bj`. Node ordinates have the ETA-REF, ETA-SLOPE, ETA-DENS and ETA-NODE factors from the freeze. Interpolate their logarithms at the measured local temperature; retain uncertainty of both abscissae and ordinates. At a node, use the actual neighbouring slopes/one-sided enclosure, not an arbitrarily smooth derivative.

Locally, with scalar drag-scale perturbations separated from tensor/coordinate effects,

\[
d\log H=(\partial_T\log\eta-1/T)dT
+\partial_\zeta\log\eta\,d\zeta+d\log a
+\text{geometry, velocity, displacement and tensor terms}.
\]

On the frozen smooth nominal curve, `partial_T log eta=-0.022+0.0002(T-298) K^{-1}`: it is -0.022 at 298 K and -0.018 at 318 K. The slopes of U's nominal 1 K interpolant bracket these by 0.0001. Thus an independent local-temperature error has coefficient near -0.025356 at 298 K and -0.021145 at 318 K in log H, not merely -1/T. It must not be structural-zeroed.

A common thermometer offset shifts *both* viscosity abscissae and local evaluation temperatures. Its interpolation-position effect cancels exactly when those transfers are truly common; its effect in the explicit kBT denominator remains. The residual local and node errors do not share that cancellation. This specifies the covariance physically rather than imposing a convenient correlation between stiffness and T.

Per-bead radius enters both `a` and `g/a` in C, as well as optical calibration. RADIUS-REF is common, RADIUS-BEAD is common only within each preparation, and RADIUS-HOT is a separate measured thermal transfer. Even within-block radius error need not cancel from contrasts if its geometry sensitivities change. Optical radius versus hydrodynamic boundary radius is a separate *model discrepancy*, not a second draw of the measured radius.

### 3.4 Complete proposed factor covariance, and its limit

There are **345 independent standard-normal auxiliary coordinates** in the frozen ledger: 66 viscosity, 73 thermometry, 5 radius, 18 geometry, 11 velocity, 10 A-coordinate, 8 relative B-coordinate, 3 origin, 72 fit-matrix, 24 fit-centre, 4 relative fiducial, 16 detector-offset, 25 observation-noise, 2 clock/shutter and 8 driven-response coordinates. This count excludes B thermal/noise observations and excludes deterministic discrepancies.

Let `z~N(0,I_345)` and let `phi=f(z)` be the full measurement map just specified. Log quantities and matrix exponentials use their frozen multiplicative parametrization; temperature, distance and additive fit coefficients use their frozen additive one. For raw local coordinates `delta phi=L z`, the complete proposed first-order covariance is

\[
C_\phi=LL^T,\qquad
L_{ri}=\left.\frac{\partial f_r}{\partial z_i}\right|_0.
\]

This is a constructive factor specification of every covariance entry, not an instruction to diagonalize the derived quantities. The full nonlinear auxiliary law is f applied to this same z, with invalid-domain refusal. For example the same ETA-REF column reaches every force, K3, Schur stiffness and log-beta endpoint; TEMP-REF reaches all viscosity nodes and local T; COORD-A reaches A and B; CLOCK reaches velocity, frame times and driven phase. Their duplicated *effects* are required cross-covariance, not duplicated *sources*. Conditional FIT-K is the residual fit uncertainty after conditioning on those standards. It is not also added as an unconditional independent K3 covariance.

A single conservative stochastic confidence ball is `||z||^2 <= 345+2 sqrt(345 log 1000)+2 log 1000`, radius **21.3647155**, with probability at least 0.999 by the chi-square Chernoff bound. This avoids eight unrelated confidence regions. It is only a proposed stochastic region: uncertainties of the allocations themselves and the physical residual set have not been established. It is not a full U-qualified physical region.

**FULL C_phi status:** the candidate's proposed random factor law is specified, including sharing and nonlinear maps; the actual apparatus covariance and its confidence envelope are **NOT ESTABLISHED**. Supplying 345 plausible normal variables does not establish them. No numerical entry below is represented as a complete measured C_phi or a physical endpoint upper bound.

## 4. Log-beta uncertainty: what can and cannot be established

U.20 defines the necessary derivative. With theta containing log beta, mean and drift,

\[
D_\phi\theta_*=-\{\partial_\theta E s\}^{-1}\partial_\phi E s,
\qquad C_{b,\mathrm{cal}}=J_\beta C_\phi J_\beta^T.
\]

The observation covariance, P, noise, shutter and time map belong in that expected score. U.19's noiseless trace identity is not substituted for the retained noisy temporal likelihood. For a pure independent stiffness scale `H -> exp(s) H`, however, the transformation `b -> b-s` leaves `beta H` invariant, including the likelihood's stationary covariance. Free drift remains free. This yields the exact scalar sensitivity -1 without fitting B and without assuming that a trace estimator is used.

One informative, explicitly partial covariance can therefore be calculated. At the nominal node temperatures retain just these independent scalar columns:

\[
s_{bj}=g_\eta+v_g+d_b+v_b+n_{b,k(j)}+v_{bj}
+{\bf1}_{j=3}h_\eta,
\]

with standard uncertainties respectively 0.002, 0.0005, 0.0003, 0.0003, 0.0004, 0.0002 and 0.001. Here k(j)=298 for j=0,1,2 and 318 for j=3. These are precisely ETA-REF, VELOCITY-REF, ETA-DENS, VELOCITY-BLOCK, ETA-NODE, VELOCITY-FIELD and ETA-SLOPE. Radius, thermometry, coordinates, fit/noise/shutter, geometry and response are **not** silently zero: they remain in the full map but outside this computed sub-block.

With `delta b=-s`, the within-block scalar covariance, in field order 0,1,2,3, is

\[
10^{-6}\begin{pmatrix}
4.63&4.59&4.59&4.43\\
4.59&4.63&4.59&4.43\\
4.59&4.59&4.63&4.43\\
4.43&4.43&4.43&5.63
\end{pmatrix}.
\]

Between blocks the corresponding entries are `10^-6*(4.25+1_{j=3,k=3})`, not zero: both preparations use the same viscosity reference, velocity reference and viscosity-tilt standard. Projecting the actual within-block differences gives cold-contrast variance `0.08*10^-6` and hot-contrast variance `1.40*10^-6`. The shared reference and batch terms cancel; the hot tilt and distinct hot/cold nodes do not.

Because the omitted columns are independent latent coordinates in this proposal, their first-order covariance contribution is positive semidefinite. Thus these numbers are rigorous **lower bounds on the candidate's nominal first-order calibration standard uncertainties**, conditional on its proposed random law. They are not upper bounds, not the full nonlinear result, and not a certificate over the physical envelope. Numerical subtraction from a ceiling is merely the *largest possible remaining room after this sub-block*; it is not earned headroom.

### Absolute calibration uncertainty — all eight records

| Record | Calculated scalar lower bound on u(log beta) | Ceiling | Maximum possible remaining room, not certified margin | Complete U.23 upper bound / gate |
|---|---:|---:|---:|---|
| Block 1, theta0 | 0.00215174348 | 0.009 | 0.00684825652 | NE / REFUSE |
| Block 1, theta1 | 0.00215174348 | 0.009 | 0.00684825652 | NE / REFUSE |
| Block 1, theta2 | 0.00215174348 | 0.009 | 0.00684825652 | NE / REFUSE |
| Block 1, theta3 | 0.00237276210 | 0.009 | 0.00662723790 | NE / REFUSE |
| Block 2, theta0 | 0.00215174348 | 0.009 | 0.00684825652 | NE / REFUSE |
| Block 2, theta1 | 0.00215174348 | 0.009 | 0.00684825652 | NE / REFUSE |
| Block 2, theta2 | 0.00215174348 | 0.009 | 0.00684825652 | NE / REFUSE |
| Block 2, theta3 | 0.00237276210 | 0.009 | 0.00662723790 | NE / REFUSE |

### Within-block contrast calibration uncertainty — all six contrasts

| Contrast | Calculated scalar lower bound on u(bj-b0) | Ceiling | Maximum possible remaining room, not certified margin | Complete U.24 upper bound / gate |
|---|---:|---:|---:|---|
| Block 1, theta1-theta0 | 0.000282842712 | 0.003 | 0.00271715729 | NE / REFUSE |
| Block 1, theta2-theta0 | 0.000282842712 | 0.003 | 0.00271715729 | NE / REFUSE |
| Block 1, theta3-theta0 | 0.00118321596 | 0.003 | 0.00181678404 | NE / REFUSE |
| Block 2, theta1-theta0 | 0.000282842712 | 0.003 | 0.00271715729 | NE / REFUSE |
| Block 2, theta2-theta0 | 0.000282842712 | 0.003 | 0.00271715729 | NE / REFUSE |
| Block 2, theta3-theta0 | 0.00118321596 | 0.003 | 0.00181678404 | NE / REFUSE |

The absolute scalar sub-block is dominated by the common viscosity reference; the hot contrast by the viscosity tilt. These are **not proved dominant in the complete physical uncertainty**. Full exact margins are unavailable because the complete certified physical/observation/temporal law is unavailable. Reporting a complete 0.009/0.003 PASS from this sub-block would repeat the incomplete-map mistake identified in V6.

## 5. Residual set and bounded bias

### 5.1 One source-resolved set, with missing bounds exposed

The stochastic uncertainties in the freeze are uncertainty in calibrated parameters. The following discrepancies concern failures of the corresponding physical or observation models *after* those parameters are specified. This is the only residual-source ledger; none is also assigned a fictitious independent Gaussian uncertainty.

| Residual source | Physical effect and mathematical entry | Sharing and set/sign structure | Evidence for a finite candidate bound |
|---|---|---|---|
| E-ETA | Actual-mixture viscosity interpolation/calibration-model error `r_eta,b(T)` multiplying eta by exp(r) | One function per batch, with common standard-model components where applicable; a hot/cold contrast uses its difference at two T values | NE. Frozen nominal curvature would give a log-linear 1 K interpolation bound 0.000025, but does not bound the actual mixture's curvature or reference-model error. |
| E-RADIUS | Optical-to-hydrodynamic surface/radius transfer, nonsphericity, coating/adsorption | One bead surface model per block, T dependent where warranted; affects both a and C | NE. Fitted optical radius uncertainty does not bound this transfer. |
| E-WALL | Slip/roughness, chamber-flow transfer and finite-domain traction-solver discrepancy `Delta Gamma(g,omega=0)` | Same chamber/boundaries across its four fields; tensor constrained by passive fluid mechanics, not an arbitrary independent endpoint sign | NE. Neither V's 0.005 nor zero is adopted. |
| E-FORCE | Nonlinear force, omitted optical/axial dependence and antisymmetric/nonconservative component | One physical force field per setting; shared optics link settings; must be enclosed over the full 3D domain | NE. Three amplitudes cannot alone certify a continuum or outside tails. |
| E-THERMAL | Unresolved spatial temperature gradient/hotspot and fluorescence-to-bead transfer | Field- and power-dependent with shared dye/optical transfer; enters both eta and kBT | NE. Repeatability is not a spatial-transfer bound. |
| E-REGISTER | Residual geometric distortion, defocus and mean transfer after fitted coordinate/centre parameters | One shared mapping per instrument/preparation plus qualified field dependence; distinguish from 2 nm random registration | NE. It is not absorbed by the free B mean for the centre gate. |
| E-OBS | Coloured/state-dependent/non-Gaussian detector noise, shutter-kernel shape, digitization and timing-model discrepancy | Same device/clock; field dependence through photon level and defocus; functions/kernels rather than independent cell offsets | NE. Positive R and an exposure-duration uncertainty do not bound these effects. |
| E-DYNAMIC | Hidden axial mode, fluid/bead inertia, hydrodynamic memory and driven-response residual/tail | One coupled response law determined by bead, fluid and chamber, with field-dependent stiffness; causal/passive where applicable | NE. A continuous, shutter-weighted envelope and endpoint map are missing. |
| E-STABILITY | Reservoir, centre, stiffness and current drift during settling/acquisition | Time functions per block/record constrained by monitors; proposed control targets alone impose no proved bound | NE. |
| E-NUMERIC | Traction interpolation and subsequent matrix/likelihood numerical error | Same algorithms/inputs, not independent random apparatus noise | NE for a future implementation; decimal arithmetic here is not its numerical certificate. |

Formally the required common set is the set of *simultaneously admissible physical laws* `(r_eta, surface, chamber, force, thermal, observation, response, drift, numerical error)` constrained by independent qualification. The ledger identifies coordinates and dependencies of that set. Its numerical envelopes and cross-source compatibility are **not supplied**. Consequently it is an **incomplete residual set**, not a bounded set that can support U.22.

### 5.2 Correct joint endpoint problem

For an admissible law e, compute its observed mean and covariance, including exposure and sampling. The expected Gaussian negative log likelihood contains `log det C_theta + tr(C_theta^{-1} C_true(e))` and the mean-displacement quadratic term. Profile its mean/drift nuisance parameters to define `b_*(e)`; the residual endpoint is `delta b(e)=b_*(e)-b_*(0)`. This definition also covers a non-Markov true covariance without pretending that it has become a qualified retained likelihood. Distributional/coverage effects still require later V treatment.

The required bounds are

\[
B_{bj}=\sup_{e\in\mathcal E}|\delta b_{bj}(e)|,\qquad
B_{b,j0}=\sup_{e\in\mathcal E}|\delta b_{bj}(e)-\delta b_{b0}(e)|.
\]

Both endpoints of a contrast use the **same e**. For a pure shared scale residual s that multiplies every H, `delta b=-s` exactly; its contrast contribution is zero, while its absolute contribution is `sup|s|`. For a batch viscosity function, the isolated scale contribution to the hot contrast is `-[r_eta,b(318)-r_eta,b(298)]`. There is no basis for replacing that difference by two independently selected extrema. Nor is there evidence here that it vanishes.

There is no numerical supremum to evaluate until admissibility is bounded. `NE` below is the scientifically correct result; it does not mean measured infinity or prove that physical bias exceeds the ceiling. In particular, the supplied evidence does not exclude a 0.001 common residual log-force scale: such a scale would violate the absolute gate while cancelling from all contrasts. This is an identifiability warning, not a claim that this apparatus has a 0.001 error or that 0.001 is its actual supremum.

### Absolute bounded bias — all eight records

| Record | Certified joint supremum | Ceiling | Certified headroom | Dominant source / status |
|---|---|---:|---|---|
| Block 1, theta0 | NE | 0.0005 | NE | Cannot rank missing physical residual bounds / REFUSE |
| Block 1, theta1 | NE | 0.0005 | NE | Same / REFUSE |
| Block 1, theta2 | NE | 0.0005 | NE | Same / REFUSE |
| Block 1, theta3 | NE | 0.0005 | NE | Same; additional hot-field transfer / REFUSE |
| Block 2, theta0 | NE | 0.0005 | NE | Cannot rank missing physical residual bounds / REFUSE |
| Block 2, theta1 | NE | 0.0005 | NE | Same / REFUSE |
| Block 2, theta2 | NE | 0.0005 | NE | Same / REFUSE |
| Block 2, theta3 | NE | 0.0005 | NE | Same; additional hot-field transfer / REFUSE |

### Contrast bounded bias — all six contrasts

| Contrast | Certified shared-set supremum | Ceiling | Certified headroom | Dominant source / status |
|---|---|---:|---|---|
| Block 1, theta1-theta0 | NE | 0.0005 | NE | Field-dependent force/response/observation effects lack a certified bound; dominance unestablished / REFUSE |
| Block 1, theta2-theta0 | NE | 0.0005 | NE | Same, including tensor/shape transfer / REFUSE |
| Block 1, theta3-theta0 | NE | 0.0005 | NE | Same, including eta/T and hot-radius transfer / REFUSE |
| Block 2, theta1-theta0 | NE | 0.0005 | NE | Field-dependent force/response/observation effects lack a certified bound; dominance unestablished / REFUSE |
| Block 2, theta2-theta0 | NE | 0.0005 | NE | Same, including tensor/shape transfer / REFUSE |
| Block 2, theta3-theta0 | NE | 0.0005 | NE | Same, including eta/T and hot-radius transfer / REFUSE |

No numerical bias allowance is tuned to leave 0.00001 of cosmetic headroom. Removing V's spurious nonlinear bias allocation does not establish any of these physical suprema.

## 6. Decisive centre failure, independent of bias accounting

At the nominal canonical point, thermal width in the stiffest lateral direction is `sigma_min=sqrt(kBT/lambda_max(S))`. The proposed relative fiducial-registration error has covariance `4 nm^2 I` in each preparation. It is independent of mechanical-centre and detector-offset errors. Even if all B sampling error and every other source vanished, the centre-contrast covariance retains this matrix.

For the fixed two-dimensional centre contrast, T.29 uses `gamma_g=0.025/32`. A rank-2 Gaussian ellipsoid has radius `sqrt(chi2_2(q))=sqrt(-2 log(1-q))`. Therefore the two ellipsoids in T.29 have the combined radial factor

\[
c_m=\sqrt{-2\log(0.025/32)}+\sqrt{-2\log(0.025)}
=3.78275438191+2.71620303148=6.49895741339.
\]

Their Minkowski sum already gives a necessary planning value

\[
\sup g(w)\ \ge\ c_m\,(2\,\mathrm{nm})/\sigma_{\min}.
\]

This is an **exact lower bound on the required worst case at the nominal point**, not a measured centre displacement or a complete worst-case upper bound. Additional independent errors or either copy of the residual set cannot repair it. At infinite B length, including only the separately specified 1 nm mechanical centre and 0.2 nm detector offset changes 2 nm to `sqrt(5.04) nm=2.24499443 nm` and makes the result still worse.

| Fields in both blocks | sigma_min (nm) | Registration-only T.29 floor | Ceiling | Ceiling minus floor | Floor including mechanical centre and detector offset |
|---|---:|---:|---:|---:|---:|
| theta0 | 6.41430746 | 2.02639411 | 0.10 | -1.92639411 | 2.27462174 |
| theta1 | 4.42629267 | 2.93652404 | 0.10 | -2.83652404 | 3.29624006 |
| theta2 | 5.23726011 | 2.48181579 | 0.10 | -2.38181579 | 2.78583131 |
| theta3 | 6.62605752 | 1.96163628 | 0.10 | -1.86163628 | 2.20193126 |

**CENTRE: REFUSE, proved candidate failure.** The strongest field alone requires *total* isotropic centre-error standard uncertainty below **0.0681077346 nm** in this ideal infinite-data, zero-residual calculation. The actual necessary budget is tighter when other contributions are present. UF-01's 2 nm relative registration is about 29.4 times that necessary ceiling. This is not a proposal to change the candidate to 0.068 nm, and it is not a claim that such accuracy is impossible in every U apparatus.

The common ORIGIN cancels from correctly registered differences. FIDUCIAL-AB is a *relative transfer error* and does not cancel. Treating it as a common global origin would be an implementation/modeling defect. Its block sharing correlates all centre gates within that preparation, but each gate is required to pass; sharing does not divide this floor by four or two. Collecting a longer B record cannot overcome it. Even the single 97.5% ellipse alone is too large, so the conclusion does not depend on delicate interpretation of the two-ellipse planning factor.

## 7. Observation gate: a second proved failure

At the candidate's nominal `P=I`, `R_obs=4 nm^2 I`,

\[
r_{obs}(\beta)=4\,\mathrm{nm}^2\,\beta\,
\lambda_{\max}(S)/(k_BT).
\]

The design envelope includes beta=1.10, where this is largest. All four nominal points belong to the proposed region, so their values are lower bounds on any full-envelope supremum. They already fail, even before uncertainty in R, P, temperature or stiffness is included.

| Fields in both blocks | Ratio at beta=1 | Ratio at beta=1.10 | Ceiling | Ceiling minus envelope-point value | Necessary noise s.d. ceiling at this point (nm) |
|---|---:|---:|---:|---:|---:|
| theta0 | 0.097221081 | 0.106943189 | 0.05 | -0.056943189 | 1.36753495 |
| theta1 | 0.204164270 | 0.224580697 | 0.05 | -0.174580697 | 0.94368877 |
| theta2 | 0.145831621 | 0.160414783 | 0.05 | -0.110414783 | 1.11658761 |
| theta3 | 0.091106547 | 0.100217202 | 0.05 | -0.050217202 | 1.41268021 |

**OBSERVATION NOISE: REFUSE, proved candidate failure.** Knowing and subtracting R in a likelihood does not waive T's observation-noise ceiling. Averaging frames changes the observation kernel and timing; it is not the frozen 2 microsecond candidate and is not done here.

R is positive and P invertible at nominal, and the chosen exponential parametrizations preserve these algebraic properties. They do not demonstrate the required physical whiteness, Gaussianity, coordinate transfer or shutter shape. For a bulk scalar-drag *diagnostic only*, the 2 microsecond exposure is 0.02384, 0.05007, 0.03577 and 0.03557 of the nominal fast lateral relaxation times, below 0.1. That does not qualify exposure over the missing physical response envelope. The full observation gate remains REFUSE.

## 8. Axial, shape, field-realization and numerical domains

### 8.1 Static axial map

The frozen nominal construction has `A=S+bb^T/kappa`; its exact Schur complement is the target S, with no approximate subtraction. Nominal eigenvalues of K3, in micro N/m, are:

| Field | K3 eigenvalues | K3 condition number | H condition number |
|---|---|---:|---:|
| theta0 | 19.6934642, 100, 101.556536 | 5.156865 | 1 |
| theta1 | 19.8693703, 210, 211.380630 | 10.638517 | 1 |
| theta2 | 19.7053923, 60.4597808, 151.084827 | 7.667182 | 2.5 |
| theta3 | Same stiffness eigenvalues as theta0 | 5.156865 | 1 |

All nominal domains are finite and SPD, kappa=20>0 and H's condition number is well below 100. As a restricted check, the conditional symmetric FIT-K perturbation in the proposed joint Gaussian ball has Frobenius/operator norm at most `0.001*Kref*21.3647155=2.13647155 micro N/m`. Holding all other primitives nominal, Weyl's bound keeps K3 strictly positive with minimum at least 17.55699 micro N/m, and therefore its exact Schur complement is SPD. This is a **fit-only check**. It does not certify the combined Gamma/coordinate/physical-error region, conservativity or backward error.

**AXIAL/STATIC: REFUSE / unresolved full-region qualification.** Nominal algebra works; actual 3D force, covariance, nonlinear domain, axial observation transfer and support are not independently qualified. No large artificial Taylor bias is used to create this refusal. Conversely, a nominal SPD matrix is not evidence of physical qualification.

### 8.2 Shape and realized fields

At a perfectly harmonic canonical nominal law, `Sigma=H^{-1}` gives the T4 intrinsic shape statistic G=0 (also zero for any pure scalar beta). Nominal distance to the threshold is `log(1.05)=0.0487901642`. This is not a worst-case shape bound. Tensor fit, map distortion, force nonlinearity, axial transfer and observation-law discrepancies have no joint physical enclosure here. **SHAPE: REFUSE / worst-case upper bound and margin NE.** A scalar trace or determinant cannot establish it.

The T11a target values are exactly represented in the frozen nominal matrices: temperature challenge `log(318/298)=0.0649578963`; power eigen-log shifts both `log(2.1)=0.741937345`; elliptical target `R30 diag(log1.5,log0.6) R30^T`. Nominal temperature and power edge distances are respectively 0.00649578963 and 0.07419373447, and the elliptical matrix-distance allowance is 0.0510825624. Nominal elliptical distance from target is zero. Both preparations have these same nominal distances but different uncertain specimens.

These do **not** verify the full-region requirements: temperature log-ratio [0.0584621066,0.0714536859], both power eigenmodes [0.6677436103,0.8161310792], the full symmetric elliptical log-matrix ball, and retained scalar planning discrimination including its 0.037783519 challenge requirement. None can be certified from nominal matrices alone or a scalar 5% norm surrogate. **FIELD REALIZATION: REFUSE / full physical region NE.** The T11a design is specified; the missing item is this candidate's physical qualification, not missing policy widths.

### 8.3 Conditioning and numerical accuracy

The nominal SPD/conditioning check passes as an algebraic diagnostic. Over the complete physical region, positivity of K3/kappa/S/H, inverse/Schur domains, condition number <=100, and relative backward error <=1e-10 remain unestablished. No production matrix algorithm was changed or certified. **CONDITIONING: REFUSE / full-region certificate NE.** The report's arithmetic poses no sign of a fundamental singularity; it cannot stand in for that certificate.

## 9. Temporal response and hydrodynamic memory

### 9.1 Hidden axial dynamics survives exact static marginalization

For the ideal full-3D overdamped model, let `A3=Gamma3^{-1}K3`. The lateral covariance is

\[
C_q(t)=E_q e^{-A_3t} k_BT K_3^{-1}E_q^T.
\]

A closed retained 2D OU law is guaranteed by `(A3)qz=0`; this is not implied by `S>0`. At the central point of the symmetric rectangular chamber the nominal resistance is diagonal by reflection symmetry. With the frozen `b=(5,0)^T`, `(A3)qz` is nonzero. Eliminating z gives a frequency-dependent lateral inverse susceptibility. Using the `exp(-i omega t)` convention and scalar lateral/axial frictions for this illustrative elimination,

\[
D_q(\omega)=A-i\omega\gamma_q I
-\frac{bb^T}{\kappa-i\omega\gamma_z}.
\]

Its zero-frequency stiffness is S, but its high-frequency stiffness part tends to A. The relative rank-one static correction has size

\[
\left\|S^{-1/2}\frac{bb^T}{\kappa}S^{-1/2}\right\|_{op}
=\frac{b^TS^{-1}b}{\kappa}.
\]

This equals 0.0125, 0.005952381, 0.011458333 and 0.0125 in fields 0–3. These are exact nominal *stiffness-transfer indicators*, not log-beta bias or permission to add those numbers to a bias budget. They demonstrate why exact Schur marginalization does not remove hidden temporal memory. The lateral process contains additional mode structure even before fluid inertia is considered. Approximation might still be possible within a proved endpoint budget; it has not been established here.

### 9.2 Hydrodynamic memory scale

The no-slip unbounded-fluid response contains the term

\[
\widehat\gamma(\omega)=6\pi\eta a
\left(1+\sqrt{-i\omega\tau_\nu}-i\omega\tau_\nu/9\right),
\qquad \tau_\nu=\rho a^2/\eta,
\]

with the square root of positive real part; bead inertia enters separately in the susceptibility. This is the hydrodynamic-memory law in Franosch et al., equation (14) [L4]. A small inertial time alone does not make the square-root term zero.

For an explicitly **bulk diagnostic**, take rounded water density 1000 kg/m^3; it is not a certified dyed-batch density or a replacement for the frozen density measurement. The frozen eta curve and radius give the following. `Delta_diag` is the nominal 1 microsecond-tick choice for a fictitious bulk 2D model; it is **not** the qualified apparatus Delta.

| Field | tau_fast / tau_slow (microseconds), bulk 2D | Delta_diag (microseconds) | tau_nu (microseconds) | sqrt(tau_nu/tau_fast) | sqrt(pi*tau_nu/Delta_diag) |
|---|---:|---:|---:|---:|---:|
| theta0 | 83.8805 / 83.8805 | 16 | 0.280899 | 0.057869 | 0.234850 |
| theta1 | 39.9431 / 39.9431 | 7 | 0.280899 | 0.083860 | 0.355059 |
| theta2 | 55.9203 / 139.8009 | 11 | 0.280899 | 0.070875 | 0.283239 |
| theta3 | 56.2268 / 56.2268 | 11 | 0.419052 | 0.086330 | 0.345949 |

The last two columns measure the magnitude of the square-root friction term at a mechanical rate and at the illustrative Nyquist endpoint. They are **not beta biases**. They show that a zero-memory hypothesis is not justified just by saying the particle is overdamped. The finite chamber changes the exact response, especially at long times; its kernel must be enclosed rather than replaced by this bulk calculation. The 2 microsecond shutter does not suppress the entire relevant band: at the theta1 illustrative Nyquist endpoint its box-kernel amplitude is about 0.967. There is no candidate-specific residual/tail proof after exposure and aliasing.

**HYDRODYNAMIC MEMORY: REFUSE / UNRESOLVED.** UF-01 has identifiable hidden-mode and fluid-memory mechanisms. No certified mapping shows their combined effect on profiled log beta, shape, stationarity, current or coverage to fit the retained T model and 0.0005 residual limits. This is not proof that every physical fluid violates T at the required endpoint tolerance.

### 9.3 The required response architecture, and the missing certificate

The frozen candidate uses the existing U architecture, not V's one-lag witness. Once a qualified A-only pilot supplies tau bounds and Delta, use

\[
\omega_k=(0.05/\tau_s)2^{k/4},
\]

through the upper band, adding the exact `pi/Delta` endpoint and both mechanical rates, plus DC. Probe both lateral axes, both signs, within qualified amplitudes, with at least eight phases per cycle. UF-01 proposes 100 cycles per probe; the A-only pilot must establish their adequacy before production. A count specified in a document is not an amplitude/phase precision certificate.

For orientation only, the bulk diagnostic bands would be approximately [596,196350], [1252,448799], [358,285599] and [889,285599] rad/s in fields 0–3. No production grid is frozen from these unqualified bounds. Independent optical-centre steering, the common clock and matched shutter calibration are required; macroscopic stage command is not assumed to equal high-frequency liquid velocity.

A valid packet would supply one continuous enclosure of the driven response, including amplitude, phase, cross-axis transfer, interpolation between probes and the high-frequency tail after the shutter and sampling map. It would then propagate that enclosure through the profiled expected likelihood and each gate. Neither Gaussian fit residuals at finitely many frequencies, nor a response curve, nor one-lag agreement supplies that endpoint/coverage certificate. **TEMPORAL RESPONSE: REFUSE / required envelope and map NE.** No new memory-aware estimator or T revision is introduced.

## 10. Support, conservativity, stability and information

**Support/harmonic domain — REFUSE.** The proposed 100 nm lateral/250 nm axial box is a mapping domain, not a certificate of harmonicity. The nominal quadratic model has axial standard deviations about 14.39–14.91 nm, making its Gaussian tails appear small; this does not bound tails of the actual optical potential, force saturation, escape or conditional axial behavior. The actual full potential/force remainder over the occupied domain and the outside Boltzmann/tail contribution are NE. U requires the probability of clipping/selection in any of all eight records to fit T's 1e-4 rule, including continuous exposure and burn-in. It cannot be inferred from a local Hessian or discrete plateaux alone.

**Conservativity/reversibility — REFUSE.** Nominal K3 is symmetric. Real optical scattering, fluid flow and tensor-fit antisymmetry are not thereby excluded. The free full fit and independent driven response must bound the nonconservative part and satisfy the current ratio upper limit <0.02. No such envelope is supplied. We do not impose reversibility inside the B fit to manufacture agreement.

**Settling/stationarity — REFUSE.** The candidate's target drift values lie below T's temperature 0.001 and curvature 0.002 tolerances, but have no duration-dependent sensor/transfer certificate. Centre drift is also load-bearing. After physical thermal/mechanical settling, U/T require 20 upper slow relaxation times and the stipulated initial-mean/second-moment bounds. The ideal bound `10 exp(-20)=2.06e-8` is conditional on the correct relaxation envelope, which is absent. A hidden axial mode or memory tail cannot be assigned the bulk 2D tau without qualification.

**Information and count — REFUSE.** T requires the smallest permitted N in `[N0,2N0]`, with `N0=ceil(450000 coth(Delta/tau_s))`, quadratic-equivalent count >=450000, efficient log-beta information >=408164 and T.29. For reference only, inserting the unqualified bulk 2D times and tick choices above gives N0 = 2,387,683; 2,594,005; 5,730,925; 2,329,458. These are arithmetic illustrations, not selected counts or information results.

The physical observation covariance needed for the information calculation has not been qualified. In a specified Gaussian law its entries would enter

\[
I_{ab}=m_a^T C^{-1}m_b+\tfrac12\operatorname{tr}(C^{-1}C_aC^{-1}C_b),
\]

followed by the Schur complement over fitted nuisance parameters. No ideal `N*d/2` or effective-count surrogate replaces this calculation. More decisively, §6 proves T.29 fails even at infinite N, so **there exists no count in T's allowed range that qualifies UF-01**, regardless of whether the scale-information threshold alone could be reached. This impossibility result needs neither finite-N validation nor a new estimator. T.28 therefore refuses this instantiated design and returns it for prospective scientific review; that is not evidence that every other apparatus realization requires a changed T threshold.

**Two preparations — REFUSE in each.** Blocks 1 and 2 have equal numerical nominal bounds because their frozen targets and uncertainty magnitudes are equal. They are not copies with independent global instruments: the 345-factor law shares standards, while bead/batch/chamber/relative-registration and record residual factors are distinct. The centre and noise counterexamples apply separately to every record of each block; no averaging across preparations can rescue them.

## 11. Gate disposition and ownership

| Deterministic requirement | Best justified result for UF-01 | Verdict and owner |
|---|---|---|
| Absolute calibration <=0.009 | Conditional nominal scalar floors 0.002151743–0.002372762; full nonlinear envelope upper bound NE | REFUSE, candidate metrology qualification missing |
| Contrast calibration <=0.003 | Conditional nominal scalar floors 0.000282843 and 0.001183216; full upper bound NE | REFUSE, candidate metrology qualification missing |
| Absolute bounded bias <=0.0005 | Actual shared residual supremum NE | REFUSE, candidate residual certification missing |
| Contrast bounded bias <=0.0005 | Actual same-assignment contrast supremum NE | REFUSE, candidate residual certification missing |
| T4 shape <log1.05 | Nominal zero only; complete physical upper bound NE | REFUSE, candidate tensor/observation/support qualification missing |
| Centre <0.10; T.29 planning | Necessary nominal registration-only planning floor 1.961636–2.936524; worst shortfall at theta1 2.836524 | **REFUSE, proved apparatus-choice failure** |
| Observation noise <=0.05 | Nominal design-envelope points 0.100217–0.224581; worst shortfall 0.174581 | **REFUSE, proved apparatus-choice failure** |
| Observation map, shutter, exposure, bandwidth | Positive/invertible nominal parametrization; exposure fits bulk diagnostic; full physical envelope NE | REFUSE, candidate qualification missing |
| T11a realized fields | Correct nominal targets; full-region certificate and discrimination NE | REFUSE, candidate qualification missing; no T11a policy gap |
| Axial/full K3/Schur | Nominal SPD and exact Schur work; whole physical region NE | REFUSE, candidate qualification missing |
| Temporal response / hydrodynamic memory | Nonzero hidden coupling and substantial memory indicators; continuous endpoint-bound certificate NE | REFUSE, candidate dynamic compatibility unresolved |
| Reversibility/stability/settling | Control targets only; no physical current/drift envelope | REFUSE, candidate qualification missing |
| Support/harmonic/tails | Proposed mapping box only; no physical continuum/outside-tail proof | REFUSE, candidate qualification missing |
| Conditioning/backward error | Nominal H condition 1–2.5; physical region and implementation certificate NE | REFUSE, candidate qualification missing |
| Information/count | No N can remove the centre-calibration floor; physical information envelope also NE | REFUSE, proved candidate count infeasibility via T.29 |

The **dominant proved obstruction** is the relative centre-metrology floor. Detector noise is a second independent proved obstruction. Missing residual/temporal certificates are not ranked numerically because no defensible source magnitudes exist. In particular, hydrodynamic-memory indicators are not recast as 0.08 log-beta bias.

The owner classification is **A — candidate apparatus choice**, with additional unresolved candidate U-qualification evidence. There is no proof for **B — generic limitation of the selected U route**, and none for **C — actual T/U incompatibility**. Nanometre positional *resolution* and sub-0.1 nm A/B registration *uncertainty* are different claims; cited component capabilities do not settle the latter's attainability.

## 12. One bounded next scientific review; no implementation

The old V6 0.0005 failure and this refusal have different logical roles. V6 overcounted a stochastic Schur remainder as physical bias and used an incomplete eta/force map; those remain implementation/benchmark defects. UF-01 demonstrates additional apparatus-choice failures after that bookkeeping is separated. Its unknown actual bias bounds cannot be inferred from V6's failed synthetic bounds. **Minimum authority change established by this review: none to U or T.** A future replacement benchmark would change V, but is not scientifically ready.

The next step is **one independent apparatus-attainability/adjudication review of this refusal**, using the same T field family and U measurement architecture. Its single decision is whether available, independently traceable metrology and physical-response evidence can support a future jointly qualified packet. It must address the necessary total centre-error limit below 0.0681077 nm at theta1, the instantaneous noise requirement below 0.943689 nm at that point, and an actual shared 0.0005 residual/temporal endpoint certificate. These are necessary conditions from this fixed design, not three separately authorized repair projects or a newly selected apparatus.

The reviewer should distinguish a failure of this proposal from an evidence-backed generic limitation before requesting any authority change. No retuning of UF-01 is performed here. No smaller uncertainty is asserted to be attainable merely because algebra permits it. If that later review supplies a defensible new packet, it must be prospectively frozen and all gates recomputed before any V-plan replacement. If it cannot, it must name the physical obstacle; a T or U amendment would require a separately scoped scientific decision, not a code workaround.

**Human scientific decision required now: NONE.** Refusal follows from unchanged thresholds. Independent audit remains required; accepting the refusal does not authorize physical work. **Next implementation task: NONE.** A bounded V-plan/core replacement is conditional on a later all-gates PASS and is not begun.

## 13. Arithmetic, provenance and validation record

Only source inspection, algebra and deterministic arithmetic were used. Centre factors, thermal widths, noise ratios, scalar covariance, viscosity values and time-scale diagnostics were evaluated with Python's Decimal at 60-digit precision; displayed decimal values are rounded. Nominal symmetric 3x3 eigenvalues were separately evaluated by a standard symmetric eigensolver. These are not Monte Carlo, trajectory simulation, estimator fitting or finite-N calibration. No EBU scientific runner or production estimator was invoked. An initial optional arbitrary-precision-library import was unavailable; Decimal supplied the completed high-precision arithmetic instead.

The numerical uncertainty of the displayed arithmetic is negligible relative to the large proved centre/noise shortfalls. It is not a substitute for metrology uncertainty. All genuinely missing physical bounds are labelled NE. The frozen candidate text is unchanged after arithmetic; only the report is added. Repository validation consists of exact scope review, full diff inspection, whitespace/diff checks, link/section and frozen-text checks, then one local commit and a clean-tree check. No tests that execute scientific state are appropriate or run.

Source SHA-256 values at the starting commit:

| Source | SHA-256 |
|---|---|
| AGENTS.md | `168307e07f79d980a5545bc4283619f44e5ba54eb750212783daf65356bb2e94` |
| Physical foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Theory baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| S equilibrium anchor | `5b92fdf5749ee05db63f32320e2b34a10afa2c98ceaf2e7a996f78b2df60505f` |
| T including T11a | `10ddfdceb90454a87cd83a7868c65a1e1b7a7147cc4e8360faf70225ba6d4519` |
| U Branch-A specification | `af66f3fe640c25b5bf0bc11e61f3b77e944c70f2e4a2a040841b65a12d4b8d0a` |
| V6 recovery assessment | `a2f8d74000d896e7e8fc04903af65d7dc653424086998442e1903c6a20828dc3` |

The report commit is identified in the delivery response; a file cannot embed its own eventual Git commit SHA without changing that SHA. This report is an assessment, not a gate receipt or a claim of independent release.

## 14. Primary literature consulted

- **[L1]** Lee et al. (2007), [Characterizing and tracking single colloidal particles with video holographic microscopy](https://arxiv.org/abs/0712.1738). Primary radius/3D-position demonstration. Its accuracy and precision statements are not automatically standard uncertainties for this packet.
- **[L2]** IAPWS, [R12-08 viscosity formulation for ordinary water](https://iapws.org/technical-guidance/release/viscosity). Authoritative water-property formulation, not the actual dyed-batch calibration.
- **[L3]** NBS, [Viscometer calibrating liquids and capillary tube viscometers, Monograph 55](https://nvlpubs.nist.gov/nistpubs/Legacy/MONO/nbsmonograph55.pdf). Primary metrology basis for capillary/reference-liquid calibration; no historical uncertainty is asserted as a modern lower bound.
- **[L4]** Franosch et al. (2011), [Resonances arising from hydrodynamic memory in Brownian motion](https://arxiv.org/abs/1106.6161), especially [full text, equation (14)](https://arxiv.org/pdf/1106.6161). Experimental memory observation and the friction law used for the diagnostic calculation.
- **[L5]** Dufresne, Altman and Grier (2001), [Brownian dynamics of a sphere between parallel walls](https://arxiv.org/abs/cond-mat/0008316). Confined mobility measurements and comparison with approximate wall models; not a certified rectangular-chamber error envelope.
- **[L6]** Ross, Gaitan and Locascio (2001), [Temperature measurement in microfluidic systems using a temperature-dependent fluorescent dye](https://www.nist.gov/publications/temperature-measurement-microfluidic-systems-using-temperature-dependent-fluorescent). Demonstrated fluorescence precision and spatial/time-resolution context.
- **[L7]** Shah et al. (2009), [Generalized temperature measurement equations for rhodamine B dye solution and its application to microfluidics](https://www.nist.gov/publications/generalized-temperature-measurement-equations-rhodamine-b-dye-solution-and-its). Mixture-dependent fluorescence calibration context.
- **[L8]** Tolic-Norrelykke et al. (2006), [Calibration of optical tweezers with positional detection in the back-focal-plane](https://arxiv.org/abs/physics/0603037). Driven calibration feasibility; its use of thermal spectra is not imported into the independent U force route.
- **[L9]** Grimm, Franosch and Jeney (2012), [High-resolution detection of Brownian motion for quantitative optical tweezers experiments](https://arxiv.org/abs/1208.1114). High-bandwidth detection and memory-aware analysis in a different calibration design; not permission to calibrate A from B.
- **[L10]** Berglund (2010), [Statistics of camera-based single-particle tracking](https://www.nist.gov/publications/statistics-camera-based-single-particle-tracking). Measurement-noise and exposure-blur theory; not certification of UF-01's shutter or detector.

**ALL DETERMINISTIC T/U GATES: REFUSE. U-FEASIBILITY PACKET: REFUSE.**

**V RELEASE: NON-RELEASE. W: BLOCKED. PHYSICAL EXECUTION: NOT AUTHORISED. AUTHORITY MODIFIED: NO. CODE MODIFIED: NO. MONTE CARLO: NO. PUSH: NO.**

E1a U PHYSICAL/METROLOGY FEASIBILITY:
PROSPECTIVE PACKET REFUSED
