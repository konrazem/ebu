# E1a V-stage — procedure version 6 core repair report

```text
STATUS:                  NON-CONTROLLING CANDIDATE
PROCEDURE VERSION:       6  (v1 superseded; v2 AUDIT FAILED;
                             v3, v4, v5 NOT CLEARED)
AUTHORITY MODIFIED:      NO
EXECUTION AUTHORISED:    FALSE
V RELEASE:               NON-RELEASE
W-STAGE:                 BLOCKED
e1a-v4:                  UNTOUCHED (identities, contracts, plan, seal)
BASELINE SIGN DEFECT:    STILL OWED before W-stage authority freeze
```

This report is prospective engineering evidence for an independent auditor.
It records no validation outcome, consumes no confirmatory seed, uses no
physical data and authorises nothing.

| Coordinate | Commit |
|---|---|
| repair starting point (V5, audited) | `3b65a39fddc3aaaec350f7fdfc962428df2aac4a` |
| V plan clarification | `9c0480f68f14806145f3acf74ea5ed3972285a5e` |
| V6 core repair | `3b4e86eb846bd9d6cbb03400222e885961af83d6` |
| V6 freeze | `5874548e81b20d66fbfc24b5fc3bcaf97cbb1b42` |

| Object | SHA-256 |
|---|---|
| analysis procedure | `85add71db0a61543d4657537b124d80223313ef5f7a36bbe48e4c88cec250408` |
| synthetic generator | `2ab4c76bb772d83ccb199cf0b30659224390fb554fedb689a5029edcde50c361` |
| validation procedure | `072aba3d8d95a89d99449a3c30e700eb7984efb6442b0458117187c65d379144` |
| packet schema | `22f1f27a50b8cd4952e0efb640a083ee7967c7f21bdf0f90806a0f65abf21e63` |
| seed map | `268943c7f73b31026b2934929a7ae685c61ec981682f110df6d5ba5fdb62bc96` |
| gate semantics | `faec0e05385cd1e106777b05ac7d271c074d0087a34d615e2bb199225619aac1` |
| validation plan | `0ef888251bff0892e0afdda914677cc96d161ca0e6a9b47e8a386af9f3f66132` |

The plan's `frozen_at_commit` names the **code state** it freezes, which is the
repair commit; the freeze commit above is the one that writes the frozen plan
and cannot name itself.

---

## 1. What this repair was for

Independent audit of procedure version 5 returned **NOT CLEARED** and named
seven blocker families. All seven are repaired here, together with a narrow
clarification of the V validation plan that removes the one human decision V5
had escalated.

| | V5 state | V6 state |
|---|---|---|
| A | numerical sensitivity certification not actually guaranteed | guaranteed; see §4 |
| B | axial remainder set over an informal marginal 3σ | over the joint 99.9% physical region; §5 |
| C | official `C_φ` omitted ten of fifteen required categories | complete; §6 |
| D | the 0.0005 bias ceilings were computed, never compared | enforced predicates; §7 |
| E | localisation ratio omitted `P`; qualification read the B fit | detector coordinates, independent pre-B envelope; §8 |
| F | gate provenance was a typed artifact anyone could fill | a verifiable receipt; §9 |
| G | controls did not exercise their validation obligations | both do; §10 |

**Three further defects surfaced during the repair and are also fixed**, two of
them in the V6 work itself and caught by its own regressions:

* the `ln 2` doubling and the `ln m` negation were performed in the ambient
  decimal context, which rounds to 28 digits half-even and can round a lower
  bound *upward* — it stops being a bound;
* the `exp` series was evaluated with signed terms, where rounding an
  intermediate downward does not bound the next one;
* `ginnovation_mean`'s early-out tested only the **value** component, so at the
  linearisation point — where the offset difference is zero but its derivative
  is not — it discarded the centre rows of the expected information and made
  the system singular.

---

## 2. Scientifically cleared requirements — unchanged

Nothing in this repair reopens cleared science. The following are inputs, not
decisions taken here.

| Quantity | Value | Source |
|---|---:|---|
| absolute equivalence margin | `log 1.05` | T.7 |
| cross-field margin | `log 1.02` | T.8 |
| geometry margin | `log 1.05` | T.9 |
| centre margin, thermal units | 0.10 | T.9 |
| reversibility margin `r_irr` | 0.02 | T.10 |
| critical-value ceiling | 2.10 | T 20.2 |
| absolute calibration ceiling | 0.009 | T.24 / U.23 |
| contrast calibration ceiling | 0.003 | T.24 / U.24 |
| bounded bias, absolute and contrast | 0.0005 | T.18 / U.22 |
| instantaneous localisation ratio | ≤ 0.05 | T.23 / T 15.2 |
| exposure fraction | ≤ 0.1 τ_fast | T 15.2 |
| bandwidth product | ≤ 0.2 | T 12.2 |
| auxiliary confidence-set noncoverage | 0.001 | T 20.3 budget |
| required replicates | 5000 / 5000 / 2000 | T 20.3 |

The exact finite axial effects cleared conditionally by the V5 audit are also
unchanged as formulas:

```text
b*  = log d − log tr((I + E)^{-1}) ,    sup over ‖E‖ ≤ ρ  =  −log(1 − ρ)
G   = maxᵢ |log(1+λᵢ) − mean_j log(1+λⱼ)| ,
                                        sup  =  (d−1)/d · log((1+ρ)/(1−ρ))
```

What V6 changes is the **domain of the supremum** (§5), which is what the audit
asked for.

---

## 3. The validation-plan clarification

The V5 audit asked for a human decision on `CTL-ETA-T-COV`, because the frozen
plan's expectation read *coverage consequence detected*, which names no
per-replicate event. The controlling T design already resolves it: T names
temperature/viscosity covariance error as a required negative control, and
requires each required negative control separately to satisfy the false-support
bound.

Commit `9c0480f6` makes that explicit. It introduces **no new scientific
threshold** and alters no margin.

| | `CTL-ETA-T-COV` | `CTL-AXIAL-MEMORY` |
|---|---|---|
| primary release event | FALSE_SUPPORT | FALSE_SUPPORT |
| definition | the complete authoritative pipeline returns `SUPPORTED_WITHIN_DECLARED_TOLERANCES` under the declared covariance-misspecification alternative | the same, under the hidden-memory world |
| replicates | 5000 | 5000 |
| release condition | one-sided 95% Clopper–Pearson upper ≤ 0.025 | one-sided 95% Clopper–Pearson upper ≤ 0.025 |
| expected classification | — | `TEMPORAL_MODEL_UNQUALIFIED` and/or `INVALID_MEASUREMENT_OR_MODEL` |
| secondary output | correct and misspecified standard uncertainty, ratio and difference, interval width, classification changes — **mandatory, never a release criterion** | per-replicate classification, temporal qualification and its residual |

**HUMAN SCIENTIFIC DECISION REQUIRED: NONE.** Neither control's 5000 replicates
are executed in this repair.

The amendment is scoped exactly as the brief scopes it, to these two cases. The
other negative controls keep the 200 replicates the plan already carried; an
auditor may reasonably ask whether T's "each required negative control" reaches
them too, and that question is recorded here rather than answered unilaterally.

---

## 4. Blocker A — the numerical certification

### 4.1 What the audit rejected, and what replaced it

**The log/exp two-ulp assumption.** It rested on an undocumented platform
property, and an empirical accuracy test is not a proof. **No library
transcendental is called in the certified path.** `ilog` and `iexp` are
explicit truncated series with proved remainders over range reductions that are
exact in binary arithmetic:

```text
log :  x = m · 2^e   (math.frexp, exact)
       log x = log m + e log 2 ,   log m = −2 artanh u ,  u = (1−m)/(1+m) ∈ [0, ⅓]
       tail  ≤  u^{2N+1} / ((2N+1)(1 − u²))          N = 45

exp :  y = x / 2^k   (math.ldexp, exact),  |y| ≤ ½,  then k squarings
       exp|y| = Σ_{j≤N} |y|^j / j! ,
       |R_N| ≤ |y|^{N+1}/(N+1)! · 1/(1 − |y|/(N+2))  N = 40
```

Both are evaluated in `decimal` at 60 digits under **directed rounding**, so the
arithmetic itself rounds outward. The only borrowed property is
correctly-rounded decimal `+ − × ÷` under an explicit rounding mode, which the
General Decimal Arithmetic specification requires and which is the same category
of guarantee as IEEE-754 binary arithmetic — the category the interval
primitives already relied on.

The series is evaluated at `|y|` so **every term is positive**. That is not
cosmetic: with alternating signs, rounding an intermediate downward does not
produce a lower bound of the next one, because multiplying a lower bound by a
negative factor gives an upper bound. The negative branch is recovered by one
reciprocal with directed rounding.

**Exact input conversion.** `Decimal(float)` is the float's exact binary value;
`math.frexp` and `math.ldexp` are exact. No decimal display string is parsed
anywhere, and a regression asserts `Fraction(Decimal(x)) == Fraction(x)` across
the range and that `Decimal(str(…))` and `Decimal(repr(…))` do not appear in the
module.

**Square root.** `isqrt` does not appeal to IEEE-754 either. `math.sqrt`
supplies an unverified candidate and the endpoints are widened until **exact
rational arithmetic** confirms `lo·lo ≤ a_lo` and `hi·hi ≥ a_hi`. The result is
at least as tight as a blind one-ulp widening and rests on nothing.

### 4.2 The Riccati value *and* derivative fixed points

V5 bounded the value only, and reported the bound rather than using it. Both are
repaired by one observation.

Hyper-dual numbers under

```text
‖x‖_w = |x₀| + w|x₁| + w|x₂| + w²|x₁₂|
```

form a Banach **algebra** for every weight `w > 0` — expanding `‖x‖‖y‖`
reproduces every cross term of the product's grading — and matrices over it
inherit a submultiplicative induced norm, the max row sum of entry norms. The
classical a posteriori contraction estimate therefore applies to the hyper-dual
iterate **as a whole**:

```text
‖X − X*‖_w ≤ ‖T(X) − X‖_w / (1 − L_w) ,
```

and reading the grading back gives one bound per component: `|ΔP₀| ≤ B`,
`|ΔP₁|, |ΔP₂| ≤ B/w`, `|ΔP₁₂| ≤ B/w²`. Every admissible weight gives a valid
bound for every component, so the tightest per component is the minimum over a
grid.

For the Riccati operator the Fréchet derivative is the classical
`DT(P)[Δ] = F_cl Δ F_clᵀ`, so `L_w = ‖F_cl‖_w²`. **That is a derivative at a
point, not a Lipschitz constant on a ball**, so the bound is computed, the ball
inflated eightfold, `F_cl` re-enclosed over the whole inflated ball, and the
recomputed bound required to fit back inside it. A recomputation that does not
fit refuses certification. That ε-inflation acceptance test is what makes the
contraction constant a bound over the enclosure, as §14 of the brief requires.

The discrete Lyapunov tail is bounded the same way:
`‖tail‖_w ≤ ‖Q‖_w ‖F‖_w^{2·2^m} / (1 − ‖F‖_w²)`, evaluated in logarithms because
the exponent is astronomical.

**Every one of these bounds is folded into the enclosure before the result is
used.** A regression inflates the proved bound by 10⁶ and asserts the returned
enclosure widens; a bound that were merely reported would not.

### 4.3 The linear solve

The residual is enclosed in interval arithmetic with the matrix entries
entering as the intervals they are — V5 accumulated it in ordinary floating
point and called the result certified.

The nonsingularity certificate no longer uses Weyl plus an eigensolver
reconstruction residual. That estimate had two faults: the residual was
returned **relative** to the matrix scale and then subtracted as if absolute,
and the reconstruction was computed in plain floating point with no account of
the eigenvector matrix's own loss of orthogonality. Instead,
`λ_min(S) ≥ μ` is equivalent to `S − μI ≻ 0`, and an **interval Cholesky** that
completes with every pivot's lower endpoint positive proves positive
definiteness for *every* member of the interval matrix. The float eigenvalues
propose candidate shifts; nothing in the certificate depends on their accuracy.

### 4.4 Failure semantics

If the transcendental enclosure, the Riccati or tangent enclosure, the
nonsingularity certificate or the roundoff bound cannot be established, the
sensitivity carries `certified = False` with a zero Jacobian and infinite radii.
A single uncertified row makes **every** qualification taken from that
calibration `UNRESOLVED_AT_NUMERICAL_PRECISION`. There is no heuristic fallback
and no partially certified result.

### 4.5 Measured

```text
sigma_abs       6.571943e-03   [6.570736e-03, 6.573149e-03]   PASS  (<= 0.009)
sigma_contrast  2.162946e-03   [2.160549e-03, 2.165343e-03]   PASS  (<= 0.003)

Riccati value bound            4.4e-12   relative to the covariance scale
Riccati derivative/mixed bound 5.0e-10   same scale
Lyapunov tail bound            2.2e-33   same scale
worst second-derivative radius 1.35e-07
linear-solve residual          2.36e-08
certified lambda_min           0.0720    by interval Cholesky
```

**NUMERICAL SENSITIVITY CERTIFICATION: CERTIFIED.**

The four exact reference derivatives lie inside the certified intervals:

```text
d log beta* / d log k_A   = −1      contained
d log beta* / d log T_A   = +1      contained
d log beta* / d b_det,x   =  0      contained
d mu_x*     / d b_det,x   = −1      contained
```

### 4.6 What is NOT claimed

The enclosure bounds the error of **this algorithm** evaluated in floating
point: truncation (exactly zero — the chain rule is evaluated, there is no step
size), interval roundoff, and the distance from each iterative fixed point to
its exact value. It is not a claim about the distance between the T.6 expected
log likelihood and any physical quantity, and it is not a statistical
statement. That boundary is stated here rather than left to be inferred.

---

## 5. Blocker B — the joint 99.9% physical region

`JointCalibrationRegion` is a versioned object recording the primitive basis,
the per-primitive noncoverage allocation, the coverage factor it implies, the
declared latent structure, the bounded systematic set, the category
declarations and a construction identity.

The construction is deliberately conservative and, crucially, **valid whatever
the dependence structure**:

```text
R = { φ : |φᵢ − φ̂ᵢ| ≤ kᵢ σᵢ  for every i } ,   kᵢ = Φ^{-1}(1 − αᵢ/2) ,
Σ αᵢ ≤ 0.001   ⟹   P(φ ∉ R) ≤ 0.001   by the union bound.
```

| | value |
|---|---:|
| stochastic primitives | 29 |
| allocated noncoverage | 0.001 |
| guaranteed joint coverage | 0.999 |
| per-primitive coverage factor | 4.1416 |

No independence is assumed anywhere, and correlated primitives are **not**
redrawn as if independent: the declared shared thermometry latent stays in
`C_φ` and in the generating law, and the region records it. The deterministic
bounded systematics are a separate set and are never converted into variances;
the total physical qualification domain is the statistical region enlarged by
that set.

The Schur remainder enclosure is recomputed over this region, with the axial
half-extents taken from the region itself and the bounded wall/hydrodynamic
correction added to the coupling extent. The result is materially larger than
V5's shorthand:

| field | ρ (V5, marginal 3σ) | ρ (V6, joint region) |
|---|---:|---:|
| θ0, θ3 | 1.3314e-04 | 1.8082e-03 |
| θ1 | 6.2876e-05 | 8.5393e-04 |
| θ2 | 2.1845e-04 | 2.9668e-03 |

The exact suprema are reverified on the corrected radius and each is regressed
to dominate 25 sampled members of the set per field. Both auditor
counterexamples still fail:

```text
E = −0.0004999·I        exact scale effect  0.000500024992  >  0.0005   FAILS
E = diag(±0.048752)     exact geometry      0.048790679067  >= log 1.05 FAILS
```

Centre and rate effects go through the **U generalized-eigenvalue construction**
`λ(K, Γ)`, so an anisotropic or uncertain drag widens the relaxation-rate range
instead of being absorbed into a scalar stiffness factor. A regression
constructs a drag whose anisotropy raises the maximum rate and asserts the
scalar construction would have missed it.

---

## 6. Blocker C — the complete `C_φ`

### 6.1 Every required category is accounted for

All fifteen categories U requires are declared, each exactly once, as one of
`UNCERTAIN`, `EXACT_CONSTANT`, `FIXED_BY_VALIDATION_CASE`,
`BOUNDED_SYSTEMATIC` or `NOT_APPLICABLE`. **Absence cannot mean zero
uncertainty**: a missing category, an `UNCERTAIN` category with no members, a
`BOUNDED_SYSTEMATIC` with no finite bound, a non-stochastic classification with
no justification, or a registered primitive that no category claims — each
refuses construction.

| category | classification |
|---|---|
| viscosity / η(T) | UNCERTAIN |
| temperature calibration | UNCERTAIN |
| bead radius / material transfer | UNCERTAIN |
| 3D force/displacement calibration | UNCERTAIN |
| axial stiffness / coupling | UNCERTAIN |
| wall / hydrodynamic resistance | **BOUNDED_SYSTEMATIC** |
| coordinate transform `P` | UNCERTAIN |
| centre / fiducial transfer | UNCERTAIN |
| localisation covariance `R_obs` | UNCERTAIN |
| detector offset | UNCERTAIN |
| shutter / exposure | UNCERTAIN |
| timing / synchronisation | UNCERTAIN |
| shared standards | UNCERTAIN |
| block-specific | UNCERTAIN |
| field-specific | UNCERTAIN |

The wall/hydrodynamic correction is a **bounded model error** and is carried as
one, not converted into a Gaussian variable.

### 6.2 The primitives reach the inference

The analysis-side map carries every primitive that physically reaches it. The
measured log-β row for `block1/theta0`:

```text
log_k_standard              −1.000000000    log_p_gain               +2.000000000
log_T_standard              +1.000000000    p_shear                  −0.012355308
log_bead_radius             +2.000000000    log_r_obs_scale          +0.022083123
log_force_displacement_cal  −1.000000000    log_t_exp                −0.017991607
log_axial_stiffness         −0.007875222    log_dt                   +0.017991607
log_axial_coupling          +0.015750443    log_k_block@block1       −1.000000000
b_det_x, b_det_y             0.000000000    log_T_block@block1       +1.000000000
                                            log_k_field@block1/theta0 −1.000000000
```

The axial reduction is **differentiated**, not assumed: `κ` and `b` move
separately and the Schur complement is formed generically from them.

### 6.3 Structural zeros are demonstrated

Four primitives have a zero row: the two viscosity parameters and the two
fiducial coordinates. The zero is **structural** — those variables do not enter
the analysis model at all, because the estimator profiles the full drift `A`
freely and the fiducial enters only the centre statistic — and is detected by
building the model with a seed on that primitive alone and asking whether the
seed survives into any object the likelihood reads. A variable absent from a
computation cannot affect it, so this is a proof rather than a measurement.

The deterministic suite additionally evaluates one of those columns numerically
and confirms it encloses zero to better than 1e-6. That is weaker than the
structural argument by construction: the Riccati fixed-point inflation widens
every component, including one that is identically zero.

### 6.4 Shared covariance is structural

A shared standard is **one latent variable**, not an asserted off-diagonal:

```text
φᵢ = Σ_l aᵢₗ σᵢ z_l + sqrt(1 − Σ aᵢₗ²) σᵢ eᵢ ,   z, e independent standard normals
```

with `a = sqrt(ρ)` on both the stiffness and temperature standards, giving
correlation exactly 0.7 and the declared variances unchanged. The structure
survives into the **generating law**, which is what makes `CTL-ETA-T-COV` a
real misspecification rather than a matrix edit. A loading set exceeding the
declared standard uncertainty refuses.

---

## 7. Blocker D — the bounded-bias ceilings

Both 0.0005 ceilings are enforced qualification predicates on the official
path, with T's inclusive semantics, the contrast on its own jointly computed
bound and never inferred from two absolute bounds. A breach refuses with
`CALIBRATION_UNCERTAINTY_EXCESS`.

**The design point is UNQUALIFIED.** Over the corrected region:

| | bounded bias | ceiling | |
|---|---:|---:|---|
| absolute, θ0/θ3 | 2.060e-03 | 0.0005 | EXCEEDS |
| absolute, θ1 | 1.104e-03 | 0.0005 | EXCEEDS |
| absolute, θ2 | 3.221e-03 | 0.0005 | EXCEEDS |
| contrast θ1−θ0 | 3.164e-03 | 0.0005 | EXCEEDS |
| contrast θ2−θ0 | 5.281e-03 | 0.0005 | EXCEEDS |
| contrast θ3−θ0 | 4.120e-03 | 0.0005 | EXCEEDS |

This is reported as measured. The audit had already found contrast values of
0.000696–0.000852 labelled qualified under V5's *smaller* region, so the breach
is not an artefact of the new region — the new region makes the absolute
ceiling fail too. **The model error is not shrunk to make a design point pass.**
A prospective design change would be separate reviewed work.

A regression confirms the predicate is a **gate and not a wall**: a record whose
certified remainder set is small enough passes it, and one whose set is large
does not.

---

## 8. Blocker E — observation qualification

### 8.1 Detector coordinates

```text
S_y   = P Σ Pᵀ
r_loc = λ_max( S_y^{−1/2} R_obs S_y^{−1/2} )   ≤ 0.05
```

`P` is a required argument. The auditor's case — `Σ = I`, `P = 0.1 I`,
`R_obs = 0.01 I` — gives **exactly 1.0** and fails; V5's latent comparison
reported 0.01 and passed.

### 8.2 Independent and pre-Branch-B

`ObservationEnvelope` is built from Branch-A physics and instrument calibration
only: the locked thermal Hessian, the calibrated drag, the instrument's
detector map, localisation covariance and timing, the certified
axial-remainder radius, and T's declared design/power range of `log β` — which
is taken as the hull of every true scale the preregistered cases declare,
widened by the T.7 margin, so the envelope cannot be narrowed by choosing a
convenient range. **No fitted quantity enters**, and a record with no envelope
is unqualified rather than unqualifiable.

Every predicate is evaluated at the closed-form **worst case**:

```text
r_loc ≤ (1 + u_R) e^{b_max} (1 + ρ) / (1 − u_P)²
        · λ_max( R_cal , P_cal H_A^{−1} P_calᵀ )

rate  ≤ max λ(K, Γ) · (1 + ρ) / (1 − u_Γ)       → exposure and bandwidth
```

Measured at the nominal design point: `r_loc` 0.0200 → worst case 0.0259 ≤
0.05; exposure 0.0500 → 0.0523 ≤ 0.1; bandwidth 0.1500 → 0.1564 ≤ 0.2.

The exposure-averaged ratio keeps U's separate role and is recorded alongside,
never in place of, the instantaneous ceiling.

`CTL-NOISE-HI` fails with `P = I` and with a nontrivial `P`; a *consistent*
change of detector coordinates — `P` and `R_obs` together — changes nothing, as
it should.

The fitted bandwidth check remains as a distinct **Branch-B** diagnostic. The
two roles are kept apart.

---

## 9. Blocker F — the gate calibration receipt

Typing V4's string did not make it evidence: a caller could still construct the
type and fill every field with whatever it liked, so a non-empty identity
remained the whole trust model.

`GateCalibrationReceipt` binds the gate family, the procedure version, the
analysis, validation, plan and seed-map identities, the calibration seed
namespace, the calibration case/domain identity, the replicate count, the
radius, the coverage target, the calibration result digest and the release
state — and carries a **digest of all of it** that the production builder
recomputes. A caller who invents fields gets a digest that does not recompute;
one who copies a real receipt and alters a field gets the same; one who
supplies a genuine receipt from another procedure version, plan or domain is
refused on the identity comparison.

Seventeen forgery routes are regressed, including a mutated critical value, a
mutated replicate count, a missing result digest, an unreleased calibration, a
plain string and a synthetic fixture.

Fixtures are separated by **type**: `SyntheticGateFixture` is a different class
with its own constructor, and no production API accepts it. There is no boolean
on the trusted class that an ordinary caller could leave unset.

Finite-N calibration has **not** run, so **no production receipt exists** and
every gate is `UNCALIBRATED`. That is the expected state, not a defect:
complete support is unavailable outside explicitly marked test fixtures.

---

## 10. Blocker G — the two negative controls

### 10.1 `CTL-ETA-T-COV`

The control draws **fresh auxiliary measurements** from the declared generating
law, shared thermometry latent included, and the analyst locks in exactly what
those measurements say — the field, the detector map, the localisation
covariance, the offset and the timing. The misspecification is that the
*analyser's* `C_φ` omits the latent and treats the two standards as
independent; the data do not. V5 edited the analyser's matrix and drew nothing.

Recorded in every replicate: the correct and misspecified standard
uncertainties, their ratio and difference, the contrast uncertainties, the
absolute interval widths and the top-level classification.

Measured at 1200 frames per record:

```text
sigma_abs correct (shared)      6.571943e-03
sigma_abs misspecified          7.182648e-03
difference                      6.107052e-04
ratio misspecified / correct    1.092926
sigma_contrast, both models     2.162946e-03   (difference exactly 0)
```

Two observations for the auditor. The omission **overstates** the absolute
uncertainty here by 9.3% — V4 had asserted it always understates, and **no
universal sign is claimed**, in the plan, in the code or in this report. And
the contrast is **exactly unaffected**: the shared standards enter both
endpoints with the same sensitivity, so the contrast row differences them away
and the covariance between them cannot reach it. That is a property of this
primitive map, recorded, not generalised.

### 10.2 `CTL-AXIAL-MEMORY`

Nothing is annotated. The retained 2D temporal model is qualified against an
**independently measured driven response**.

The test is the one property that separates the admissible class from
everything else, with no fitting at all. For **any** 2D linear system the mean
response to a prepared displacement is a semigroup,

```text
R(t) = e^{−A t}   ⟹   R(2τ) = R(τ)²   for every τ and every admissible A,
```

so a measured violation beyond the measurement's own standard error excludes
the **whole** admissible class at once. A lateral projection of a three-mode
system is not a semigroup, because the hidden mode's state at time τ is not a
function of the lateral state alone.

The declared measurement architecture: τ = 1.5 × the lateral slow relaxation
time, 6000 prepared releases per lateral direction, an initial displacement of
6 stationary standard deviations, a 5σ band on the measurement's own standard
error, and a required resolution of 0.20. **A band too wide to exclude anything
returns `UNRESOLVED`, which does not qualify** — the fail-closed direction.

Measured:

| world | residual | band | status |
|---|---:|---:|---|
| nominal 2D | 0.012 | 0.071 | QUALIFIED |
| hidden-memory 3D | 0.296 | 0.065 | **UNQUALIFIED** |

In the complete experiment all eight records refuse with
`TEMPORAL_MODEL_UNQUALIFIED` and the authoritative verdict is
`INVALID_MEASUREMENT_OR_MODEL` — the planned scientific classification.

The Branch-B side remains lateral only; the analyser is never given a hidden
coordinate. The 3D witness — `K3` positive definite, Schur complement valid,
lateral marginal exactly `k_B T K_eff^{-1}`, Chapman–Kolmogorov residual far
from zero — is retained as a supplementary deterministic reference.

### 10.3 The hand-set flag is gone

`AxialEvidence.fully_qualified` now takes the temporal item as a keyword
parameter with no literal on any production path. Every caller derives it: at
construction from the built world's own exact semigroup residual (0.0 for the
2D design, 0.257 for the hidden-memory world), per replicate from the
measurement. `axial_memory_specs` takes its locked field straight from the
Schur complement rather than through the qualified reduction, because the
control's whole point is a world the reduction does not qualify; the refusal
happens where it belongs, in the per-replicate measurement.

**MANUAL `temporal_qualified` FLAG: ABSENT.**

---

## 11. Certified versus unresolved numerical objects

| object | state | basis |
|---|---|---|
| truncation error of the derivative | **EXACTLY ZERO** | hyper-dual chain rule; no step size |
| floating-point roundoff | **CERTIFIED** | outward-rounded intervals everywhere |
| `log`, `exp` | **CERTIFIED** | self-contained series, proved remainder, directed decimal rounding |
| `sqrt` | **CERTIFIED** | proved per call by exact rational comparison |
| Riccati fixed point, value | **CERTIFIED** | graded-norm contraction, ε-inflation verified |
| Riccati fixed point, derivatives | **CERTIFIED** | same estimate, read per component |
| discrete Lyapunov tail | **CERTIFIED** | closed-form geometric tail |
| expected-information nonsingularity | **CERTIFIED** | interval Cholesky of the shifted matrix |
| linear-solve error | **CERTIFIED** | interval residual × certified inverse norm |
| 0.009 / 0.003 qualification | **PASS** | on the certified enclosure |
| 0.0005 bias ceilings | **FAIL at this design point** | enforced predicate; see §7 |
| finite-N critical values | **UNCALIBRATED** | no calibration has run |
| diagnostic null scales | **UNCALIBRATED** | no calibration has run |
| continuous nuisance coverage | **OPEN** | validation enablement work |

---

## 12. Systematic fail-open re-audit

The whole `e1a_v5` package was searched again, over executable lines only —
comments and docstrings excluded — for fourteen pattern classes: evidence→pass,
evidence→zero, bare identity→authority, fixture→production, B-fit→pre-B
qualification, empty `all()`, dict overwrite, NaN fall-through, nominal
fallback, unverified receipt, uncertified value treated as certified, and
exception swallowing.

Findings:

* **Zero** occurrences of bare-string gate identity, raw-statistic
  substitution, bare `except`, or a fixture reachable from a production API.
* **Three real defects found and fixed**, listed in §1: two directed-rounding
  soundness errors in this repair's own transcendental code, and
  `ginnovation_mean`'s value-only early-out, which silently removed the centre
  rows of the expected information.
* Surviving load-bearing occurrences, each inspected and documented:
  * `NOT_RUN_REASONS.get(driver, "")` — an empty reason cannot make an
    unimplemented driver runnable, because `runnable` separately requires the
    driver to be in `IMPLEMENTED_DRIVERS`;
  * `grouped.get(key, [])` in the contrast builder — an empty list yields no
    contrast, which is fail-closed;
  * `doc.get("cases", [])` in the contract checker — an empty plan makes every
    code case *missing from the plan*, which fails;
  * `axial_bias = 0.0 if axial is None` — the same branch emits
    `INCOMPLETE_INPUT` and makes the bias evidence `MISSING`, so the zero never
    reaches a qualification;
  * `branch_a_valid=True` for synthetic records — a construction-time property
    of a synthetic packet, labelled as such, and not a physical packet
    assertion;
  * the two dimensionless `optimize.py` tolerances — unchanged and safe.

---

## 13. Procedure identities and seeds

Identities are recorded in `docs/e1a/e1a_v5_validation_plan.json` under
`identities`, over an ordered preimage of module path and file digest followed
by the canonical JSON of the declared configuration. The validation identity
binds every result-affecting module, including `certified.py`,
`calibration.py`, `observation.py`, `reduction.py`, `generate.py`,
`validation/contract.py`, `validation/harness.py` and `validation/run.py`.

Seeds: a new root `e1a_v5/validation/v6/2026-10-06`, five confirmatory
families, each checked disjoint from the V5, V4, V3 and V2 streams **and from
every engineering stream past and present** — an earlier version's engineering
draws have been inspected as thoroughly as its confirmatory ones.
`engineering-v6` carries every draw made during this repair. The confirmatory
families are **frozen and unconsumed**.

---

## 14. Deterministic evidence

```text
test_e1a_v5_kernel.py          83 checks
test_e1a_v5_procedure.py      184 checks
test_e1a_v5_v3_repairs.py     175 checks
test_e1a_v5_v4_repairs.py     484 checks
test_e1a_v5_v5_repairs.py     264 checks
test_e1a_v5_v6_repairs.py    1019 checks
                             ----
                             2209 checks, 0 failures
```

Thirteen deterministic controls and references pass, including the four new
ones: `REF-TEMPORAL-QUALIFICATION` (the machinery deriving both answers from
the two worlds), `REF-OBS-DETECTOR-COORDS` (the `P = 0.1 I` counterexample),
`REF-JOINT-REGION` (the region's coverage basis) and the retained
`REF-AXIAL-MEMORY-WITNESS` and `REF-ETA-T-COV-ALGEBRA`.

Preserved and regression-protected, untouched by this repair: the T.6
likelihood, shutter integration, profile-fit failure semantics, the
current-control construction, the Riccati SI-scale convergence fix, the `eigh2`
and `lu_solve` fixes, the `ScientificInterval` evidence checks and the
diagnostic contradiction handling. The generic float kernel still reproduces
the cleared core bit for bit.

---

## 15. Engineering smoke sample

`docs/e1a/e1a_v5_v6_smoke_results.json` is an **ENGINEERING SMOKE SAMPLE**, not
a validation result. It is drawn entirely from `engineering-v6` at 1200 frames
per record — about 0.3% of the T.23 information target — and can never
contribute to a RELEASE verdict.

---

## 16. Future validation obligations

Nothing below is done, and none of it is authorised by this repair.

```text
finite-N critical-value calibration      NOT RUN
false-equivalence size validation        NOT RUN   (5000 per configuration)
diagnostic-family size validation        NOT RUN   (5000 per configuration)
complete eight-record power validation   NOT RUN   (2000 experiments)
CTL-ETA-T-COV confirmatory run           NOT RUN   (5000, CP upper <= 0.025)
CTL-AXIAL-MEMORY confirmatory run        NOT RUN   (5000, CP upper <= 0.025)
continuous nuisance-domain coverage      OPEN
multi-record contrast driver             NOT IMPLEMENTED
geometry/centre gate-boundary driver     NOT IMPLEMENTED
e1a_v5 suites in CI                      PENDING, required before W adoption
baseline section 14.3 sign defect        STILL OWED before W-stage freeze
design-point bounded-bias qualification  UNQUALIFIED; a prospective design
                                         change would be separate reviewed work
```

The joint 99.9% calibration region introduced in §5 is a **U physical and
calibration object**. It is not, and must not be confused with, the still-open
finite-N nuisance-uniform coverage problem, which remains V validation
enablement work.

---

## 17. Status

```text
V6 CORE:                        READY FOR INDEPENDENT AUDIT
V RELEASE:                      NON-RELEASE
W-STAGE:                        BLOCKED
HUMAN SCIENTIFIC DECISION:      NONE
AUTHORITY MODIFIED:             NO
OLD V4 AUTHORITY MODIFIED:      NO
REAL DATA USED:                 NO
PHYSICAL CALIBRATION DATA USED: NO
SCIENTIFIC RNG:                 engineering-v6 only
CONFIRMATORY RNG:               NOT USED
REAL OPTICAL-TRAP EXPERIMENT:   NOT RUN
EXECUTION AUTHORISED:           FALSE
```

V2, V3, V4 and V5 results are retained as historical evidence and are labelled
**SUPERSEDED PROCEDURE EVIDENCE**. They are not V6 validation.
