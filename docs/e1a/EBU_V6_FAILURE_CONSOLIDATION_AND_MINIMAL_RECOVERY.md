# EBU V6 failure consolidation and minimal recovery decision

**Status:** scientific design assessment, non-controlling. **V release:** NON-RELEASE. **W:** BLOCKED. **Physical execution:** NOT AUTHORISED. No V code, T/U authority, validation run, or confirmatory seed is changed or used here.

**Controlling sources checked:** [T minimal design](E1A_MINIMAL_EQUILIBRIUM_EXPERIMENT_DESIGN.md), [U Branch-A specification](E1A_BRANCH_A_PHYSICAL_CALIBRATION_QUALIFICATION.md), [V validation plan](E1A_V5_VALIDATION_PLAN.md), [V6 report](E1A_V5_V6_CORE_REPAIR_REPORT.md), the frozen [case plan](e1a_v5_validation_plan.json), and the corresponding V6 validation/reduction/evidence implementation. External literature below is feasibility context, not EBU authority.

## Decision and scope

**Current V6 benchmark: UNQUALIFIED.** The reported 0.0005 failure is primarily a V-level error-accounting and benchmark-construction failure. It is not evidence of a T/U mathematical incompatibility or of a measured apparatus failure. Yet a *complete, physically credible U-compatible synthetic witness satisfying every pre-B deterministic gate has not been established*. The smallest defensible next step is **one narrow U feasibility review of the physical calibration and driven temporal-response envelope**, using the existing U method and unaltered T thresholds. No U specification amendment is recommended now. A V-plan replacement can follow only if that review yields a prospective packet with certified room in every gate. This is one sequential architecture, not alternative repairs.

This distinction matters: the *authority that is demonstrably wrong* is the V plan/accounting; the *minimum review level needed to claim a feasible recovery* is U physical/metrology feasibility. A scientific threshold need not change. The present numerical V6 failure cannot be cured by saying the physical apparatus merely needs better assumed metrology.

The classification is:

| Level | Finding | Consequence |
|---|---|---|
| A — software | V6's receipt can self-seal and self-declare release; negative-control counts are short; the official calibration derivative omits the selected viscosity/force path; the temporal qualifier is incomplete. Earlier arithmetic/sensitivity defects were repaired or certified in V6, but V6 still failed core audit. | Future implementation must match a settled scientific map. Do not patch V6 now. |
| B — V benchmark | The synthetic benchmark uses a 29-primitive union-bound box, an unrestricted spectral-ball outer bound for a rank-one Schur remainder, per-cell bias 0.00025, wall residual 0.005, and separately maximized contrast endpoints. The stochastic Schur Taylor remainder is booked as residual physical bias although the construction evaluates the exact Schur map. | This explains the current 0.0005 failure. Replace the benchmark prospectively after U feasibility review. |
| C — U feasibility | No certified full physical force/viscosity/geometry covariance and residual model-error set, nor the U-required driven frequency/step-response envelope, demonstrates the needed margins. | Narrow feasibility review required; U's existing measure/bound/refuse specification remains intact. |
| D — T design | No contradiction has been proved. U itself gives an abstract covariance example satisfying 0.009/0.003, but labels it nonphysical. | No T redesign warranted. |

## Exact V6 bias accounting

V6 computes \(B_j=0.00025-\log(1-\rho_j)\) and \(B_{j0}=0.0005-\log(1-\rho_j)-\log(1-\rho_0)\). These are **outer bounds under V's own decomposition**, not measured biases. Values below are dimensionless log-beta units and are common to both blocks at the V design point.

| Field | V6 \(\rho_j\) | V axial outer effect \(-\log(1-\rho_j)\) | V per-cell residual allowance | Reported absolute bound | Reported contrast vs θ0 |
|---|---:|---:|---:|---:|---:|
| θ0 | 0.00180816914 | 0.00180980585 | 0.00025000000 | 0.00205980585 | — |
| θ1 | 0.00085393295 | 0.00085429776 | 0.00025000000 | 0.00110429776 | 0.00316410361 |
| θ2 | 0.00296680973 | 0.00297121943 | 0.00025000000 | 0.00322121943 | 0.00528102528 |
| θ3 | 0.00180816914 | 0.00180980585 | 0.00025000000 | 0.00205980585 | 0.00411961170 |

The axial half-widths are V's nonzero synthetic \(u(\log\kappa)=0.02\), \(u(\log b)=0.05\), multiplied by a 4.1416 marginal factor from V's 29-primitive Bonferroni construction for one joint 99.9% region. V adds its wall/hydrodynamic bound 0.005 to the coupling half-width. The resulting \(\rho\) is an upper bound on the **second-order Taylor remainder** of \(S=K_{qq}-bb^T/\kappa\) under uncertain \(b,\kappa\). It is not an independently observed force, temperature, or response-law discrepancy. Removing only the 0.005 wall addition leaves axial effects 0.001741228 (θ0/3), 0.000821941 (θ1), and 0.002858570 (θ2). Thus wall addition contributes only about 0.000069, 0.000032, and 0.000113 respectively to these field bounds; the large failure is principally the treatment of Schur uncertainty and the conservative region/image, not the wall number alone.

The 0.00025 allowance is V's chosen per-cell systematic budget, with no source-resolved covariance or shared-error model. Counting two full 0.00025 allowances already exhausts the contrast ceiling before any axial term. V5's smaller 3σ region likewise failed some contrast ceilings (about 0.000696–0.000852); V6's wider, correctly covered region amplified an existing problem. Neither 0.00025 nor 0.005 is prescribed by T or U. T/U prescribe the final 0.0005 joint endpoint limits and a way to measure, propagate, bound, or refuse physical errors.

**Double counting and nonlinearity.** The exact Schur map is already evaluated from measured full \(K^{(3)}\) in the V construction. If the future analysis propagates the *full nonlinear* auxiliary law through that exact map, the Taylor remainder of a first-order surrogate is not a second, independent physical bias. It remains relevant to checking a first-order covariance/coverage approximation; any nonlinear shift of the estimator's centre must still be calculated and accounted for. If a production algorithm actually uses the linearized Schur map, its uncorrected remainder *is* approximation error and cannot be dropped. V6 also places the same wall/hydrodynamic source in its drag envelope and in the axial-coupling half-width without a calibrated common-source transfer to both quantities. This is an accounting overlap, not proof that wall effects vanish. Temperature, coordinate, and observation errors similarly require one primitive ledger and one joint map; the record does not prove literal duplication of their numerical terms.

**Incompatible extrema.** V's sum of independent per-field maxima is a valid but possibly loose upper enclosure; its validity is not refuted by unattainable corners. It is not a certified supremum of a contrast over the *shared* physical/error set. In fact the exact Schur Taylor remainder factorizes as \(R=-(\delta b-u b)(\delta b-u b)^T/[\kappa(1+u)]\), \(u=\delta\kappa/\kappa\): it is negative semidefinite and rank at most one. An unrestricted two-dimensional spectral ball contains impossible positive and full-rank directions. The axial primitives are global in V's primitive vector, so independently choosing adverse axial corners for θj and θ0 ignores sharing. A correct contrast enclosure evaluates \(\sup_{(\phi,e)\in\mathcal A\times\mathcal B}|\delta b_{bj}(\phi,e)-\delta b_{b0}(\phi,e)|\) under one common primitive/error assignment. Do not infer cancellation without this joint calculation.

## Prospective synthetic choices and feasibility

All figures in this table are **V-only inputs**, not achieved metrology or U-prescribed instrument tolerances. U fixes the measurement architecture, not these magnitudes. Relative standard uncertainties refer to logarithmic primitives where V defines them that way.

| V synthetic input | Present choice | Origin and possible prospective action | Plausibility assessment |
|---|---:|---|---|
| Nominal four fields | 100/100, 210/210, 150/60 µN/m at 30°, and 100/100 at 318 K | T nominal targets; retain | Target, not performance |
| Bead radius / viscosity | 0.5 µm / 0.89 mPa·s | V apparatus selection; retain or choose another pre-A specimen | Plausible as nominal inputs |
| Axial κ / coupling | 0.20 / 0.05 of reference stiffness | V physical design point; may select a different measured full-3D realization, never suppress axial measurement | Plausible nominal, dynamic closure unproved |
| Reference stiffness, block and field standard uncertainties | 0.0060, 0.0010, 0.0015 | V auxiliary-law design | Differential components plausible as a synthetic law; absolute chain needs traceability |
| Temperature standard/block | 0.0010 / 0.0005 | V; U requires local thermometry and η(T) coupling | Plausible stochastic choices, residual thermal transfer unproved |
| Viscosity reference / slope | 0.0020 / 0.0050 | V; put through Γ→force→full K3 and correlated T chain | Absolute 0.2% demanding but conceivable; hot-field slope effect unqualified |
| Radius / force transfer | 0.0010 / 0.0015 | V; per-bead 3D radius and independent driven-force fit required | Demanding; no evidence for this specimen |
| Axial κ / coupling uncertainties | 0.020 / 0.050 | V; propagate nonlinear Schur under joint law | Plausible synthetic uncertainty, not bias by itself |
| Coordinate gain / shear | 0.0010 / 0.0005 | V; preserve A/B map and centre cross-covariance | Demanding but conceivable |
| R_obs scale / detector / fiducial | 0.020 / 2 nm / 2 nm | V; detector and centre paths remain | Plausible synthetic stochastic values; independent noise law unproved |
| Shutter / clock | 0.0010 / 0.0001 | V; require measured kernel and common timebase | Plausible synthetic standards, not a response certificate |
| Wall/hydrodynamic *residual* | 0.005 | V bounded model error, not random uncertainty; cannot relabel Gaussian | 0.5% plausible as an error bound, but too large if it maps near one-for-one to scale bias |
| Other residual bias | 0.00025 per cell | V blanket allocation; replace with measured source-resolved shared set | A sub-0.05% total endpoint bound is **not presently justified** |
| Noise ratio / exposure / bandwidth placement | 0.02 / 0.05τf / 0.75 of 0.2 ceiling | V selected margins inside T limits | Numerically possible; physical response and Fisher envelope unproved |

Primary metrology evidence supports caution rather than a success claim. U itself explicitly states that its example source allocations are not achieved measurements and identifies per-bead dimensions and total drag correction as possible limits. NIST's review of water viscosity reference values retained a 0.25% uncertainty recommendation for the 20 °C absolute reference, showing why a convenient table value does not establish a 0.05% endpoint residual. Published optical-trap calibrations show that wall positioning and hydrodynamic correction can create percent-level force errors; hydrodynamic memory has been directly observed in optical traps. These papers do **not** prove EBU infeasible, but none certifies the combined EBU absolute, contrast, residual-bias, and driven-response requirements. Sources: [NIST water-viscosity review](https://srd.nist.gov/JPCRD/jpcrd105.pdf), [axial optical-tweezer calibration](https://pmc.ncbi.nlm.nih.gov/articles/PMC2711482/), [Franosch et al., Nature 2011](https://www.nature.com/articles/nature10498), and [JCGM 100/101](https://www.bipm.org/en/web/guest/publications/guides).

### One feasible-witness attempt, and why it is incomplete

Retain V's nonzero bead, viscosity, axial coupling, and all nonzero stochastic uncertainties, full 3D A response and 2D B observation. Use the exact Schur map. Replace the blanket 0.00025 per-cell budget by a source-resolved common/error set whose *jointly propagated* endpoint absolute and contrast suprema each fit 0.0005; specifically a proposed design target of ≤0.00020 absolute and ≤0.00020 contrast leaves margin for numerical error. Calibrate a finite-chamber wall/flow transfer so its residual, rather than its fitted uncertainty, is included in that set. Keep the measured viscosity/radius/force uncertainties in the joint \(C_\phi\), with η(T) covariance. Independently measure and enclose driven response per U §20.

This is a **prospective candidate**, not an existence certificate: 0.00020 is a design target, not an achieved or literature-supported bound. Adding viscosity to the force-to-K3 derivative changes V6's 0.006572/0.002163 uncertainty results; neither the resulting 0.009/0.003 margins nor the hot-field contrast is certified. The 0.005 wall residual may itself overwhelm 0.0005 if it maps substantially to stiffness. The one-lag test does not certify the hydrodynamic-memory response over U's frequency band. Consequently **FEASIBLE U-COMPATIBLE SYNTHETIC WITNESS: NO, not yet established**. This is a lack of a justified witness, not a proof that no witness can exist.

| Deterministic pre-B gate | Binding T/U requirement | Candidate status |
|---|---|---|
| Absolute / contrast calibration | Each ≤0.009 / ≤0.003 standard uncertainty over full envelope | V6 partial figures pass; corrected full η/T/force map uncomputed — UNRESOLVED |
| Absolute / contrast residual bias | Each joint supremum ≤0.0005 | V6 FAIL; proposed source-resolved set unmeasured — UNRESOLVED |
| T4 shape / centre | Shape upper <ln1.05; centre upper <0.10 thermal units | Full corrected physical/observation envelope absent — UNRESOLVED |
| T11a field realization | Both preparations, full joint 99.9% region, retained challenges and ≥0.90 scalar planning discrimination | Nominal values alone insufficient — UNRESOLVED |
| Observation | P invertible, R PSD, instantaneous ratio ≤0.05, exposure ≤0.1τf, exact shutter/noise and independent calibration | V nominal ratios inside ceilings; physical distribution/transfer not certified — UNRESOLVED |
| Axial/static geometry | Full K3 and κ positive, Schur SPD, corrected harmonic/tail and nonlinear domains | Nominal construction SPD; whole corrected joint region not certified — UNRESOLVED |
| Temporal model | U §20 driven response over full band, continuous residual and tail mapped to endpoint/gates | One-lag witness insufficient — UNRESOLVED |
| Reversibility and within-record stability | Independently qualified conservative conditions, \(r_{irr}\) upper <0.02, \(|\Delta\log T|\leq0.001\), normalized-curvature log change ≤0.002, plus T stationarity/lag and settling/burn-in requirements | Physical preparation/monitor envelope absent — UNRESOLVED |
| Numerical, support, information | κ₂(H)≤100, backward error ≤1e−10, qualified support; exact information ≥408164 and T.29 at smallest N in [N0,2N0] | No corrected envelope/count search certificate — UNRESOLVED |

No row marked UNRESOLVED may be inferred PASS from a nominal design point. A truly feasible witness needs finite, nonzero auxiliary uncertainty, a justified residual-error set and actual deterministic proofs for all rows. It cannot be manufactured by typing smaller synthetic error bars.

## Correct full calibration dependency and gate architecture

Build an independent primitive basis with source IDs at global/session/block/field/record scope and a joint auxiliary measurement law or justified confidence set. The relevant paths are

\[
\eta(T;\zeta),a,\text{geometry}\longrightarrow
\Gamma=6\pi\eta a C\longrightarrow F=\Gamma v
\longrightarrow (K^{(3)},c)\longrightarrow
S=K_{qq}-bb^T/\kappa\longrightarrow H=S/(k_BT)
\longrightarrow E_{A,B}[s]\longrightarrow b_* =\log\beta_* .
\]

The A/B coordinate maps and their transfer uncertainty feed the force/displacement fit and B observation. The centre feeds both the centre gate and the profiled likelihood. P, R_obs, detector offset, shutter kernel, exposure and timestamps feed the **observation law** and thus the profiled expected-score derivative; their effects are not inferred from static \(H\) alone. Shared standards enter once with full cross-covariance. A sufficient fitted summary of full \(K^{(3)}\), centre and their covariance is legitimate only if its covariance and cross-covariance with η, T, radius, geometry, coordinates and observation standards are retained. Never count the source primitives and their fitted summary as independent information. Calculate \(J_\beta\) from U.20 and \(C_{b,cal}=J_\beta C_\phi J_\beta^T\), then verify nonlinear coverage/variance with the exact map. Project contrast rows with the actual within-block difference operator and shared covariance. Keep bounded residual law/model errors in a separate joint set and compute U.22 directly.

Viscosity is **not structurally zero** merely because the B drift parameter is freely profiled: η fixes the independently driven force standard, which fixes \(K^{(3)}\), S and H. In a simple scalar steady fit \(K=\Gamma v/q\), \(d\log K=d\log\eta+d\log a+\cdots\), so the ideal scale derivative gives \(d\log\beta\approx-d\log\eta\) before shared cancellations. The same Γ can cancel from steady \(\tau=\Gamma/K=q/v\) while remaining in H. A shared thermometer enters η(T) and the denominator of H: locally \(d\log h=(\partial_T\log\eta-1/T)dT+\partial_\zeta\log\eta\,d\zeta+d\log a+\cdots\). CTL-ETA-T-COV must generate auxiliary readings with this true η(T)/T dependence, analyze them with a deliberately wrong broken dependency/covariance, count false complete support separately over 5,000 experiments, and record correct versus wrong uncertainty/interval effects. An invented stiffness/T correlation is not that control.

A pure global translation of all fiducials can have a zero log-beta row in a translation-invariant free-mean likelihood, while moving the registered centre and its 0.10-thermal-unit gate. That zero requires an algebraic proof in the actual A/B map and cannot erase fiducial cross-covariance or centre uncertainty. Coordinate gain/shear generally affect H/P and log beta; detector offsets can be profiled for log beta yet remain nonzero for centre. Keep separate \(J_\beta\), \(J_{centre}\), shape and current/gate maps.

U temporal qualification requires independent, calibrated driven step/frequency response in both lateral axes and signs. After an A-only pilot fixes τ and Δ, measure DC plus **four angular frequencies per octave from 0.05/τs through π/Δ**, including both mechanical rates and the upper endpoint, with at least **eight timed phases per cycle**. Use independently calibrated steering/force and timebase, propagate phase, amplitude, shutter and interpolation uncertainties, enclose residuals continuously between probes and the high-frequency tail after exposure/sampling, and map the whole envelope to T's likelihood and gate error budgets. Refuse if the steering map, band, residual, tail or endpoint effect cannot be bounded. V6's prepared-release one-lag semigroup check is a useful *hidden-memory witness only*: satisfying one lag is neither an equivalence theorem nor U's specified qualification.

## Negative controls and gate provenance

The frozen V plan has 51 named cases. The classification and required counts are:

| Class | Named cases | Current planned count | Required disposition |
|---|---|---:|---|
| Stochastic negative controls, 17 | CTL-COMMON-07, CTL-FIELD-106, CTL-FIELD-MIX, CTL-FIELD-110, CTL-HARD-025, CTL-GEOM-TRACE, CTL-GEOM-ROT, CTL-CURRENT, CTL-ETA-T-COV, CTL-NOISE-HI, CTL-NOISE-HEAVY, CTL-NOISE-COLOR, CTL-NOISE-STATE, CTL-BLUR-MISMATCH, CTL-DRIFT, CTL-SELECTION, CTL-AXIAL-MEMORY | 13,000: 15×200 + 2×5,000 | **17×5,000 = 85,000**, separately; +72,000 vs plan; each false-complete-support upper bound ≤0.025 |
| Positive/power, 5 | POWER-NOMINAL, POWER-CONDLIM, POWER-NOISEHI, CTL-BLIND-107, CTL-BLIND-090 | 6,400 | Keep their separate power/blinded-recovery obligations; not false-support controls |
| Calibration/statistical-size/diagnostic, 21 | CAL-SCALE-01, CAL-CONTRAST-01, CAL-SHAPE-01, CAL-CENTRE-01, CAL-STAT-01, CAL-CURRENT-01, CAL-DIAG-01; SIZE-ABS-LO, SIZE-ABS-HI, SIZE-CON-LO, SIZE-CON-HI, SIZE-SHAPE-BD, SIZE-CENTRE-BD, SIZE-CURRENT-BD, SIZE-NUIS-NOISE, SIZE-NUIS-EXP, SIZE-NUIS-COND, SIZE-NUIS-CAL; DIAG-NULL-NOM, DIAG-NULL-EXP, DIAG-NULL-COND | 98,000 | Keep distinct calibration, size and diagnostic rules |
| Deterministic references, 8 | CTL-AXIAL-COUPLE, CTL-RF-TEMP-304, CTL-RF-STIFF-1021, CTL-RF-MODES, CTL-RF-ELLIPSE, CTL-RF-STRADDLE, CTL-RF-VALID, CTL-OPT-FAIL | 8 | One deterministic reference each; not stochastic controls |

**Negative-control required total: 85,000 experiments.** The existing total of 117,408 named-case iterations would become **189,408** if all other counts remain unchanged; this arithmetic is planning only, not permission to run them. The false-support rule is a per-control Clopper–Pearson upper bound, not one pooled result.

A `GateCalibrationReceipt` whose fields, digest and `released=True` can be constructed by the same caller does not prove that calibration ran or was independently released. The non-self-authorizing chain is: **frozen procedure and seed/plan identities → calibration execution → immutable result and result digest in an independently controlled record → independent release decision bound to that digest → receipt referencing the released record → verification against that record**. Digest consistency protects integrity after release; it cannot mint release authority.

## Single bounded recovery architecture

Perform **one pre-B U-feasibility packet review** on a single prospectively frozen Branch-A synthetic apparatus candidate: complete η(T)/radius/geometry/force-to-full-K3 auxiliary law; exact Schur/nonlinear uncertainty; common-source bounded residual set; independent driven response over U's full band; and deterministic enclosures for every gate in the table above. Its output is a signed PASS or REFUSE with explicit margins and source provenance. If it passes, the *next* V-plan revision implements that frozen packet and the already-fixed T/U rules; if it refuses, the named physical bottleneck determines whether a narrowly scoped U specification issue exists. No threshold is weakened by this review. This is one sequence, not parallel fallback designs.

**Validation enablement requires all of:** (1) implementation core matches the consolidated full dependency/error architecture; (2) prospective true-bridge packet passes every deterministic T/U pre-B gate, including physical response and T11a fields; (3) each negative control has its correct generating world, event and 5,000 count; (4) U's driven temporal qualification is implemented as specified; and (5) gate calibration provenance is independent of the receipt. The validation plan and procedure must be frozen before finite-N calibration. No existing V6 result meets these conditions.

**What not to repair yet:** V6 code; finite-N calibration; Monte Carlo scaling; continuous-nuisance coverage; confirmatory seeds; compute optimisation; CI integration; W-stage authority; and physical execution. These would consume effort or risk invalidating provenance before the physical/error architecture is settled.

**Human scientific decision required:** whether the prospective U-feasibility packet, when completed, contains a physically defensible residual-bias and driven-response certificate for the chosen specimen. Today there is no numerical decision to approve; the review must produce one. **Next implementation task:** none before that review; afterward, at most one bounded V-plan/core implementation task against the frozen PASS packet.

**Primary recovery level:** NARROW U FEASIBILITY REVIEW. **Minimum authority change demonstrated now:** V plan only; no U specification or T design change is justified. **V release:** NON-RELEASE. **W:** BLOCKED. **Physical execution:** NOT AUTHORISED.

EBU V-STAGE RECOVERY:
NARROW U-STAGE REVIEW IS REQUIRED
