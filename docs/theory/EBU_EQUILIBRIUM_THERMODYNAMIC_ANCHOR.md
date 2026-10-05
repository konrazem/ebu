# EBU — Equilibrium thermodynamic anchor

Report date: 2026-10-05. Scientific stage: **S1–S8**, theoretical research and
synthesis, report only.

```text
STATUS:                 NON-CONTROLLING EQUILIBRIUM THERMODYNAMIC ANCHOR
R-STAGE:                INDEPENDENTLY CLEARED — supplied audit disposition
S-MG:                   INDEPENDENTLY CLEARED — supplied audit disposition
FEEDBACK THEORY:        INDEPENDENTLY CLEARED — supplied audit disposition
BOOK 1:                 INDEPENDENTLY CLEARED THEORETICAL EDITION; UNCHANGED
S1–S8:                  COMPLETE AS CONDITIONAL MATHEMATICS
S9:                     INDEPENDENT AUDIT REQUIRED; NOT PERFORMED HERE
E1a:                    PRESERVED / PAUSED
SCIENTIFIC AUTHORITY:    UNCHANGED
EXECUTION AUTHORISED:    FALSE
```

## 1. Executive result

**The controlling sources and cleared R-stage/S-MG results support all eight
S-stage items under explicit, distinct assumptions. No unresolved mathematical
gap remains in this bounded equilibrium anchor.** This is a synthesis-worker
disposition for independent S9 review, not independent clearance of this report,
experimental validation, or an amendment of scientific authority.

The primary theorem is the general canonical landscape identity

\[
V_\theta(x)=\frac{U_\theta(x)-U_\theta(x_\theta^*)}{k_BT_\theta},
\qquad J_\theta(x):=-\ln p_\theta(x)=V_\theta(x)+C_\theta.
\tag{1}
\]

Here the canonical ensemble is physically justified, the field and positive
temperature are fixed, and energy, support, coordinates and reference measure
refer to the same distribution. The additive constant is independent of the
state. Natural logarithms are used throughout.

This gives the canonical coefficient `β_bridge = 1`, without Gaussianity. On
a smooth interior it gives `K(x) = Hess J(x) = Hess V(x) = H(x)`. Only the
additional global harmonic, full-support, flat-measure assumptions give
`Σ⁻¹ = H` on accessible directions. Separately, the accepted P4 dynamical and
work conditions give `Δs_med = +k_B E`, `Δs_sys = −k_B E` and `Δs_tot = 0`.
**P4 does not depend on the harmonic covariance corollary.**

The report makes four qualifications explicit: density logs are relative to a
declared measure; an unrestricted fitted slope is identifiable only when `V`
varies; local curvature does not fix a whole landscape; and the no-work P4
benchmark excludes additional driving, rather than merely requiring that such
driving be recorded. These close possible ambiguities in a compressed account
without changing any cleared equation.

The resulting EBU denomination is a dimensionless thermal/log-density unit,
not a temperature-independent quantity of energy. Common denomination across
valid canonical fields is a theoretical prediction. Its realization across the
actual E1a fields remains empirically unestablished. No universal nonequilibrium
bridge, actor incentive, social outcome or economic efficiency theorem follows.
The benefit for the EBU programme is a precise physical comparison with a known
regime, while its more general potential and coalition mathematics retain their
own independent foundation.

## 2. Authority / provenance

### 2.1 Starting coordinate and precedence

| Item | Verified value |
|---|---|
| Repository | `/Users/konrad.grzyb/code/ebu` |
| Branch | `codex/book-one-continuity` |
| Starting HEAD | `f4c7277cddef5abf5fbfc8b43003b72596593e79` |
| Starting tree | `6e1073cdf8c353eb80f2fffcd084aa2985397fcb` |
| Starting working tree | Clean |
| Configured origin, fetch and push | `https://github.com/konrazem/ebu.git` |
| Upstream / intended remote target | No upstream configured; no remote target for this local-only commit |
| Remote operations for this stage | No fetch or push; no claim of freshly verified server HEAD |
| Authorized change | This report alone; local commit |

[Repository instructions](../../AGENTS.md) preserve the precedence of the
frozen physical foundation, working theory baseline and non-controlling
research reports. The scientific-record archive provides historical provenance;
this report does not revise it. Book 1 is exposition and is not used to establish
scientific authority.

The current brief explicitly supplies subsequent independent clearance of the
R-stage, S-MG, feedback reconciliation and Book 1. Their historical internal
audit-pending language is left unchanged. This task does not claim to have
conducted those audits or recovered an additional committed audit artifact.
The following commits were verified as ancestors of the starting HEAD:

| Input | Commit |
|---|---|
| R-stage repair | `6c1d0822790dc98e249a30ff5e8fa28202723e82` |
| S-MG theorem | `a7655f30bde7b798ca98eacd9138f93b36abf733` |
| Feedback reconciliation | `f3ef451773e5c421952c67382ea0a7d5b6565da8` |
| Book 1 content | `fd4fbd3fb11560311bd1ad9e97aa455ad00fc83d` |

The frozen foundation retains a historical freeze-candidate header. Its metadata,
baseline §0 and freeze commit `c63d6833da10a75ef66db11f99fb5b5c68d94c5e`
establish its authority. The 49,098 canonical bytes were compared with that
commit and both metadata digests. They match. Neither the stale header nor the
old metadata `committed: false` field reopens foundation status.

### 2.2 Sources and verified dependencies

The foundation and baseline were read directly before synthesis. The listed
research reports and E1a authority were inspected directly at the relevant
theorem, scope, provenance and prior-art sections; their conclusions were
checked against the governing equations, not merely copied from status tables.

| Source | Load-bearing content used here |
|---|---|
| [Frozen foundation](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md), §§2–3, 12–18, 21–25; [metadata](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.meta.json) | General endpoint definition; path regularity; telescoping; interaction algebra; separation of attribution, physics and institutional rules; circularity prohibition and conditional entropy status |
| [Working theory baseline](EBU_THEORY_BASELINE.md), §§4–5, 8–14, 18, 22 | Dimensionless normalization; restricted geometry; permanence versus commensurability; two independent branches; corrected temperature interpretation; accepted entropy conventions |
| [Cleared R-stage](EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md), §§2, 6–15 | Separate density/reversibility/P4/sampling assumptions; direct bridge; general Hessian corollary; full-support covariance; work sign; fixed versus moving field |
| [Cleared S-MG](EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md), §§3–8, 22–25 | Finite coalition identities; generator is additional; density versus stationarity; endpoint log contrasts; P4-scope entropy contrasts |
| [S-MG prior-art appendix](EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md), §§2, 5–8 | Existing Gibbs/log-density/Möbius antecedents; stochastic-thermodynamic and nonreversible-density references; no novelty license |
| [Cleared feedback reconciliation](EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md), §§1–2, 19–22 | Driven stable feedback does not establish a canonical distribution, thermal calibration or entropy bridge |
| [E1a-v4 prospective design](../e1a/E1A_V4_PROSPECTIVE_DESIGN.md), §§1–2, 8–9; [contract](../e1a/e1a_v4_design_contract.json), `entropy_semantics` | Thermal construction and branch independence; exact P4 scope; separate finite-reservoir constrained-macrostate object |

The ordinary static source and algebra checks reported in §24 are the author's
verification. **They are not S9 adversarial verification.**

## 3. S-stage dependency map

This is a branching hierarchy. Placing covariance before entropy on a page must
not make Gaussianity an assumption of the entropy theorem.

```text
S1: independently justified canonical ensemble
    + correct U, fixed theta, fixed T > 0
    + declared coordinates, support and reference measure
    + finite positive normalizer and accounted multiplicity factors
                         |
S2: V = (U - U*)/(k_B T)  |
                         v
S3: p = exp(-V)/Z_V  <=>  J = V + C
              |
              +--> S4: canonical beta_bridge = 1
              |        [unique slope if V is nonconstant]
              |
              +--> S5: C2 smooth interior --> K(x) = H(x)
              |
              +--> S6: global quadratic V, full affine support,
              |        flat measure, restricted H > 0 --> Sigma_T^-1 = H_T
              |
              +--> S7: resolved conservative overdamped single-bath model,
              |        no driving work, stationary equilibrium ensemble,
              |        complete heat/entropy accounting --> P4 identities
              |
              +--> S8: dimensionless thermal/log-probability denomination;
                       same predicted coefficient in each valid canonical field

Separate foundation: supplied V --> endpoint E, path theorem with regularity,
                     telescoping, cycle-zero and finite coalition algebra.
                     These do not wait for S or for equilibrium.

Separate empirical requirement: independent physical and probability branches;
                               actual cross-field realization remains untested.
```

No arrow runs from a fitted density or a desired economic benefit back to the
physical construction of `V`. No arrow runs from `Σ⁻¹ = H` to a proof that the
actual dynamics are reversible. These missing arrows are deliberate mathematical
boundaries, not unfinished S-stage derivations.

## 4. S1 — Canonical assumptions

Fix `θ`. Let `Ω_θ` be the declared accessible state space and `ν_θ` its reference
measure. Write `P_θ` for a probability measure and `p_θ=dP_θ/dν_θ` for its density
(or its mass function for counting measure). These are different objects.

| Label | Assumption | What it supplies |
|---|---|---|
| A1 | The canonical ensemble is independently physically justified for this system and boundary | Physical reason for the canonical weight; a supplied scalar potential alone is insufficient |
| A2 | Field `θ` and bath temperature `T_θ > 0` are fixed during the comparison | One energy function, one thermal scale and one normalization constant |
| A3 | `U_θ` is the correct energy for the declared configurational states and ensemble | Exponent `−U_θ/(k_B T_θ)`; no silent replacement of energy by a fitted statistical potential |
| A4 | Support `Ω_θ`, reference measure `ν_θ`, coordinates and their units are declared together | Meaning of the density and any derivatives of its log |
| A5 | Degeneracies, density of states, coordinate Jacobians and eliminated coordinates are accounted for | No missing state-dependent factor multiplying the canonical weight |
| A6 | `0 < Z_{U,θ} := ∫_{Ω_θ} exp[−U_θ/(k_B T_θ)] dν_θ < ∞` | A normalized probability law |
| A7 | `x_θ*∈Ω_θ` has finite energy and finite positive density; the same positivity/finite-value conditions hold at each compared endpoint | A finite reference and finite endpoint contrasts |

In A1, the canonical bath idealization is part of the physical model; an arbitrary
finite isolated reservoir does not give an exact canonical weight automatically.
For a resolved classical configurational description, integrating momenta that
contribute only an `x`-independent factor is harmless. Eliminating other degrees
of freedom generally need not have that property (§12). A1–A7 are a clean
sufficient set for this benchmark, not a characterization of every process that
can happen to have a Boltzmann-shaped invariant density.

Temperature is a physical quantity here. Its independent measurement belongs
to the E1a physical branch. Algebra needs a specified positive `T`; an empirical
non-circular comparison additionally needs its independent physical calibration.
No measurement precision, apparatus or estimator is selected in S-stage.

Four assumption classes remain separate:

| Class | Additional requirement | Logical role |
|---|---|---|
| Canonical density | A1–A7 | Derives the distribution and S3 bridge |
| Reversible equilibrium | Declared well-posed dynamics preserve that measure and satisfy detailed balance under their appropriate time reversal | Property of the stationary process, not just its density |
| P4 entropy interpretation | §13's thermodynamically consistent conservative overdamped model and complete energy/entropy boundary | Relates EBU to heat and the three distinct entropy changes |
| Sampling / estimation | Observations represent the intended law; time-series sampling has a justified ergodicity argument | Makes observations informative about the density; not needed for logarithmic algebra |

Zero stationary current characterizes the reversible benchmark in the declared
overdamped configurational setting with its equilibrium boundaries. It is not
asserted as a universal test for dynamics containing odd time-reversal variables.
Ergodicity also does not manufacture canonicality or detailed balance.

**S1: COMPLETE.** Source dependency: R-stage §9.2, S-MG §23, baseline §14.

## 5. S2 — Thermal normalization

With A1–A7, set `U_θ* := U_θ(x_θ*)` and define

\[
V_\theta(x)=\frac{U_\theta(x)-U_\theta^*}{k_BT_\theta},
\qquad
E_\theta(a\to b)=V_\theta(a)-V_\theta(b)
=\frac{U_\theta(a)-U_\theta(b)}{k_BT_\theta}.
\tag{2}
\]

Both `V` and `E` are dimensionless because `k_B T` has units of energy. The
reference energy cancels from every fixed-field endpoint difference. Shifting
`U` by a state-independent constant and shifting its reference by the same
constant leaves `V` unchanged. Choosing another finite reference shifts `V`
by a constant and changes the intercept of `J`, but leaves `E` and `H` unchanged.

For the general bridge, the reference need not be a minimizer, and `V` need not
be nonnegative. The centered harmonic statement in §11 additionally chooses
the restricted minimum as its reference. `T=0` is outside (2); negative
temperature ensembles are outside the stated benchmark. Spatial or temporal
variation of temperature within one transition cannot be silently inserted into
this fixed-temperature theorem.

This gives EBU a physical normalization in the canonical benchmark without
altering the foundation's general declaration of `V`. It does not identify every
potential in the EBU programme with mechanical energy.

**S2: COMPLETE.** Source dependency: baseline §14.1 and R-stage §§9–10.

## 6. S3 — Direct Boltzmann bridge theorem

**Theorem S3.** Under A1–A7, use the density representative

\[
p_\theta(x)=Z_{U,\theta}^{-1}e^{-U_\theta(x)/(k_BT_\theta)}.
\]

Define `Z_{V,θ}=∫ exp(−V_θ)dν_θ`. Then

\[
Z_{V,\theta}=e^{U_\theta^*/(k_BT_\theta)}Z_{U,\theta},\qquad
p_\theta=Z_{V,\theta}^{-1}e^{-V_\theta},\qquad
\boxed{J_\theta:= -\ln p_\theta=V_\theta+C_\theta},
\tag{3}
\]

where `C_θ = ln Z_{V,θ} = ln Z_{U,θ} + U_θ*/(k_B T_θ)` is constant in `x`.

**Proof.** Substitute `U_θ/(k_B T_θ)=V_θ+U_θ*/(k_B T_θ)` into the integral
and canonical weight, then take the natural logarithm. A6 makes the normalizer
finite and nonzero, and A7 makes the compared logarithms finite. ∎

For a general measure-theoretic density the identity holds almost everywhere;
point evaluations use the specified canonical representative, or its smooth
version on the region concerned. Probabilities of individual points in a
continuous space are not densities. Finite-bin probabilities are integrals,
not direct substitutes for `p(x)` in (3).

Absolute log density is interpreted in the declared coordinate units and
reference-measure convention. Equivalently one can use a dimensionless reference
measure, such as coordinate volume divided by fixed reference scales. Constant
rescaling of that measure only moves `C_θ`. This avoids giving an invariant
meaning to the logarithm of a dimensional numerical density. Nonconstant
measure changes are different and are handled in §12.

The baseline's relative rarity has a different zero but the same content:

\[
J_{\mathrm{prob},\theta}(x)
=-\ln\frac{p_\theta(x)}{p_\theta(x_\theta^*)}=V_\theta(x),\qquad
E_\theta(a\to b)=J_\theta(a)-J_\theta(b)
=\ln\frac{p_\theta(b)}{p_\theta(a)}.
\tag{4}
\]

For clarity, every ordinary change `ΔA` in this report means `A_post−A_pre`.
Consequently **`ΔJ = −E`**; the *drop* in rarity, `J_pre−J_post`, is `+E`.
Baseline §14.3 writes `ΔJ_prob = E` without defining that orientation there.
**Read as a post-minus-pre change, that line has the wrong sign.** It is
consistent only if its `ΔJ_prob` names a decrease. This input notation/sign
defect is recorded explicitly; the foundation's endpoint definition, equation
(4) and the accepted entropy signs resolve the mathematical result. The
baseline itself is unchanged. `J_prob` is finite rarity, not an asymptotic
large-deviation rate function without a declared speed.

**Non-circularity.** This implication starts from physically justified canonical
statistical mechanics and independently specified energy and temperature. It is
not a proof that an arbitrary declared EBU field is physically correct. Defining
`p ∝ exp(−V)` and using the constructed density as independent evidence for `V`
would violate foundation §21. E1a preserves two branches: A constructs `V` from
independent physical information; B observes `p` without using A's `V` or `H` to
define it. T-stage must preserve this separation. No redesign is made here.

**Classification:** standard canonical statistical mechanics plus EBU thermal
normalization; **not an EBU discovery**. The same direct proof is already cleared
in R-stage §9.1. **S3: COMPLETE.**

## 7. S4 — The `β_bridge = 1` corollary

Equation (3) realizes the bridge form

\[
J_\theta=\beta_{\mathrm{bridge},\theta}V_\theta+C_\theta
\quad\text{with}\quad \boxed{\beta_{\mathrm{bridge},\theta}=1}.
\tag{5}
\]

If a coefficient and intercept are both unknown, uniqueness needs two compared
states with different `V`. Subtracting (3) from any putative affine bridge gives
`(β_bridge−1)V = constant`; evaluating at those two states forces `β_bridge=1`.
On a constant-potential domain the canonical formula still has coefficient one,
but every slope can be absorbed into an intercept. Such a domain cannot identify
the slope. This is an identifiability qualification, not a failure of S3.

For a common positive scale error `V̂=cV`, `0<c<∞`, substitution gives

\[
J=\frac{1}{c}\widehat V+C,\qquad
\boxed{\widehat\beta_{\mathrm{bridge}}=1/c}.
\tag{6}
\]

If the physical branch is too large, the fitted coefficient is too small. An
additional constant shift in `V̂` is absorbed by the intercept. `c=0` erases
identifiability; negative `c` reverses the physical energy orientation and is
not the benchmark's positive calibration factor. A state-dependent error need
not admit any single bridge coefficient. No Gaussian assumption occurs in
(5) or (6), and no estimator or hidden-factor value is designed here.

**S4: COMPLETE.** Source dependency: R-stage §§9–10 and baseline §14.2.

## 8. `β_thermo` versus `β_bridge`

| Symbol | Definition | Units | Role |
|---|---|---|---|
| `β_thermo,θ` | `1/(k_B T_θ)` | Inverse energy | Converts mechanical energy to a dimensionless canonical exponent |
| `β_bridge,θ` | Coefficient of already normalized `V_θ` in `J_θ=β_bridge,θ V_θ+C_θ` | Dimensionless | Compares physical and statistical landscape scales |

Temperature changes `β_thermo`. With correct thermal normalization it does not
change the predicted `β_bridge=1`. Writing both quantities as an undifferentiated
`β` hides precisely the distinction the E1a correction established.

The working entropy candidate sometimes writes `β_bridge=κ/k_B` when a separate
physical entropy-deficit relation and its Einstein/Boltzmann interpretation are
valid. That does not set the frozen foundation's general `κ` universally to
`k_B`. The benchmark and the general entropy question retain separate scopes.

## 9. S5 — General non-Gaussian equilibrium

Quadraticity is absent from S3. A normalizable canonical quartic, double-well or
other nonquadratic configurational potential obeys exactly the same logarithmic
identity under A1–A7. S3 itself does not need derivatives. The smooth version
of S5 additionally assumes `V∈C²` on an open interior region in accessible
coordinates, with the positive canonical density there.

For the cleared illustrative dimensionless potential on `ℝ`,

\[
V(x)=\tfrac12x^2+x^4,\qquad
p(x)=Z^{-1}e^{-V(x)},\qquad H(x)=1+12x^2,
\tag{7}
\]

the normalizer is finite, and `J=V+ln Z` while the density is non-Gaussian.
This is a mathematical illustration of the theorem, not independent physical
evidence obtained by defining a density from a chosen potential. Positive
curvature everywhere is also not a general canonical requirement: a confining
double well may have negative local curvature at its barrier.

For EBU this means that the equilibrium comparison is not restricted to the
Gaussian Level-1 constitutive hypothesis. It also means that a non-Gaussian
shape alone is not a bridge failure. **S5: COMPLETE.** Source: R-stage §11.1.

## 10. The `K = H` differential corollary

Differentiating the landscape identity on the smooth interior gives

\[
\nabla J=\nabla V,\qquad
\boxed{K(x):=\nabla_x^2J(x)=\nabla_x^2V(x)=H(x)}.
\tag{8}
\]

For an exact constant-coefficient bridge `J=β_bridge V+C`, the corresponding
identity is `K=β_bridge H`. State-dependent coefficients would add derivative
terms. In constrained coordinates, differentiate the restricted functions; do
not treat inaccessible directions as observed zero-curvature directions.

The implication goes from the landscape to its derivatives. It does not reverse
from a single point: `V=x²/2` and `J=x²/2+εx⁴+C`, `ε>0`, have equal Hessians
at zero but different landscapes. Both can be normalized on `ℝ`. Even Hessian
equality throughout a connected open region only implies
`J−V=aᵀx+b`, since its gradient is constant. A gradient anchor is needed to
remove `a`; a reference value fixes `b`. For instance shifted full Gaussians
share a precision while having different means. On disconnected regions the
integration constants can differ between components.

This is a genuine limit on inference from curvature, not a remaining proof gap.
Neither (8) nor a Hessian at a minimum determines the global covariance of a
nonquadratic or truncated density. No boundary Hessian is asserted where the
log density ceases to be smooth or finite. **General `K=H`: COMPLETE.**

## 11. S6 — Global harmonic Gaussian corollary

**Theorem S6.** In declared numerical coordinates let the full accessible
affine space be `x=x*+Qz`, `z∈ℝ^d`, where `Q` has orthonormal columns in the
chosen coordinate convention. Assume:

1. `V(x*+Qz)=½zᵀH_T z` globally, with `H_T=QᵀHQ` symmetric positive definite;
2. the reference measure is Lebesgue measure `dz`, up to a fixed positive
   constant, on the entire accessible space;
3. the density bridge holds globally with a constant `β_bridge>0`;
4. there is no boundary, truncation or additional weight that changes these
   Gaussian moments.

The normalizer is then finite. With ordinary `dz`, writing `b=β_bridge`,

\[
Z_b=(2\pi)^{d/2}\det(bH_T)^{-1/2},\qquad
p_z(z)=\frac{\det(bH_T)^{1/2}}{(2\pi)^{d/2}}
\exp[-\tfrac12z^T(bH_T)z],
\]
\[
\Sigma_z=(bH_T)^{-1},\qquad
\boxed{\Sigma_z^{-1}=H_T\quad\text{at }b=1}.
\tag{9}
\]

**Proof.** Diagonalize the symmetric matrix `H_T=RΛRᵀ` with orthogonal `R`
and all `λ_r>0`. Orthogonal substitution `y=Rᵀz` preserves `dz` and separates
the integral into `d` one-dimensional Gaussian integrals. Each normalized
factor has zero mean and variance `1/(bλ_r)`; distinct factors have zero
covariance. Transforming back gives `R(bΛ)⁻¹Rᵀ=(bH_T)⁻¹`. ∎

For an unconstrained full space `Q=I`, equation (9) reads `Σ⁻¹=H`. For a proper
affine subspace the ambient covariance is
`Σ_x=Q H_T⁻¹ Qᵀ` at `b=1`, generally singular. No ambient inverse is required.
In the centered statement `x*` is the restricted minimum and mean. A global
quadratic with a linear term can instead be completed to a square; it shifts
the mean without changing the covariance formula. An arbitrary reference is
therefore not evidence of mean alignment.

Positive definiteness is required on accessible directions, not on unobservable
ambient directions. A zero-curvature unbounded accessible direction prevents
normalization of this flat-measure quadratic density. Modal scales
`σ_r²=1/λ_r` are variances in these Gaussian normal coordinates at `b=1`.
They are not automatically marginal variances in arbitrary coupled physical
coordinates. Coordinates with unlike physical units require their declared
scales before interpreting Euclidean orthonormal modes.

A local Taylor approximation around a minimum is insufficient for the exact
global statement. Approximate Gaussian moment claims need their own error
control. No such approximation or experimental covariance estimator is adopted
here. **S6: COMPLETE.** Source: cleared R-stage §11.2 and baseline §5.

## 12. Support, measure and truncation boundaries

### 12.1 The cleared truncated-Gaussian counterexample

On `[-1,1]` with ordinary Lebesgue measure, take `V(x)=x²/2` and
`p(x)=Z⁻¹exp(−x²/2)`. On the open interior, `J=V+ln Z` and `K=H=1` exactly.
Symmetry gives mean zero, and integration of
`(x exp(−x²/2))'=(1−x²)exp(−x²/2)` gives

\[
\Sigma=\operatorname{Var}(X)
=1-\frac{2e^{-1/2}}{Z}<1,\qquad
Z=\int_{-1}^{1}e^{-x^2/2}\,dx.
\tag{10}
\]

Thus `Σ⁻¹≠H`, despite the exact interior bridge and identical interior
curvatures. The boundary term in (10) is precisely what the full-space Gaussian
calculation lacks. This reuses R-stage §11.2's cleared counterexample; it is
not a simulation or a new physical model.

### 12.2 Density-of-states factors and coordinate changes

Suppose instead the density with respect to `dx` is

\[
p_x(x)=Z^{-1}g(x)e^{-U(x)/(k_BT)},\qquad g(x)>0.
\]

For the bare thermal mechanical potential, on the smooth interior where the
derivatives exist, the correct equations are

\[
J_x=V-\ln g+C,\qquad K_x=H-\nabla^2\ln g.
\tag{11}
\]

Only a constant `g` is absorbed in the intercept without changing the
landscape. If `dν=g(x)dx`, the density relative to `ν` instead has the bare
canonical form; the comparison must actually use that measure. Choosing a
measure after seeing the data to force agreement is not an independent test.
Equivalently one may introduce a separately justified potential of mean force
`U_eff=U−k_BT ln g`. It must be identified as such: its derivative is not
automatically the bare mechanical force, and its differences do not automatically
supply the P4 heat equation for `U`.

Starting from `p_x=Z_x⁻¹exp(−V)` in the original Lebesgue coordinates, take a
smooth diffeomorphism `y=f(x)` with nonzero Jacobian determinant and use new
Lebesgue measure. Then

\[
p_y(y)=p_x(x)\left|\det\frac{\partial x}{\partial y}\right|,
\qquad
J_y(y)=V(x)+C-\ln\left|\det\frac{\partial x}{\partial y}\right|.
\tag{12}
\]

A nonconstant Jacobian therefore changes the log-density landscape. If the
reference measure itself is pushed forward consistently, the scalar relation
is preserved. Under nonlinear coordinates, ordinary Hessians also acquire
coordinate-transformation terms; `H_T=QᵀHQ` in §11 is an **affine** restriction,
not a general rule for nonlinear constraint manifolds.

### 12.3 Marginalization and coarse states

For a resolved energy `U(x,y)` with flat product measure, the marginal weight of
`x` is `∫ exp[−U(x,y)/(k_BT)]dy`. It is not generally
`exp[−U(x,y*)/(k_BT)]`, nor is integration generally equivalent to minimizing
over `y`. The integral may define an effective free energy; the theorem then
requires that independently justified effective object and the correct
reference measure. An unobserved coordinate cannot simply be discarded because
the displayed density looks Gaussian.

These distinctions preserve the full harmonic result on a properly specified
affine subspace while blocking invalid extensions to arbitrary truncated,
coarse-grained or reparameterized descriptions. They are part of S1/S6 scope,
not empirical design choices made by this report.

## 13. S7 — Entropy / P4 consistency

### 13.1 Scope of the accepted benchmark

The relevant P4 is **E1a-v4 design §§8–9**. It is a deterministic
physical/theoretical consistency check, not an experimental entropy endpoint.
Its algebraic pass contributes no empirical evidence. It is distinct from the
foundation's broader historical roadmap question about changing-field freedom.

The joint entropy identities require all of the following:

1. A thermodynamically consistent, conservative **overdamped** single-reservoir
   model, with the declared mechanical/configurational energy `U` and
   `F_trap=−∇U`. Its thermal noise/mobility relation and equilibrium boundary
   conditions are part of that physical model, not consequences of the EBU
   definition.
2. Fixed field and fixed positive temperature: no moving trap, parameter driving
   or other time-dependent energy term during the transition.
3. The stationary canonical **ensemble** at both endpoint times, in the same
   declared physical coordinate/measure convention. An individual microstate
   need not sit at the energy minimum.
4. No additional driving work, hidden reservoirs, unresolved energetic degrees
   of freedom, state-dependent intrinsic entropy, or other omitted heat/entropy
   channels in the accounting boundary.

In particular, merely recording a nonzero extra work input does not restore the
no-work formula. Such a process has a different energy balance. These are the
accepted benchmark assumptions unpacked, not a new dynamics adoption.

For P4 the reference convention is the resolved configurational volume measure,
up to a constant scale. A nonconstant change of measure or a coarse-state
description requires the corresponding entropy bookkeeping; it cannot be
inserted into `s_sys=−k_B ln p` while silently retaining the same bare mechanical
heat equation. Section 12's algebraic freedom does not remove this physical
restriction.

### 13.2 Proof and signs

Take heat `Q_med` positive **into the reservoir** and external driving work
`W_in` positive into the resolved system. With `ΔU=U_post−U_pre`, the declared
first-law convention is `ΔU=W_in−Q_med`. In the no-work benchmark `W_in=0`, so

\[
Q_{\rm med}=U_{\rm pre}-U_{\rm post}=k_BT E,
\qquad
\boxed{\Delta s_{\rm med}=Q_{\rm med}/T=+k_BE}.
\tag{13}
\]

The stochastic system entropy uses the actual ensemble density at each time,
`s_sys(x,t)=−k_B ln p(x,t)` in the stated reference convention. Since that
density is the same stationary canonical one at both times, (3) gives

\[
\boxed{\Delta s_{\rm sys}
=-k_B\ln\frac{p(x_{\rm post})}{p(x_{\rm pre})}
=-k_BE},\qquad
\boxed{\Delta s_{\rm tot}
=\Delta s_{\rm med}+\Delta s_{\rm sys}=0}.
\tag{14}
\]

This short proof consolidates E1a's accepted result and S-MG §25. It does not
assume quadratic energy or use covariance. `+k_BE` is **not total stochastic
entropy production**. The identities hold realization by realization within
the declared overdamped benchmark. They do not say that each medium-entropy
change is nonnegative. In a stationary ensemble with finite mean energy,
`⟨E⟩=0`; positive and negative thermal fluctuations do not create an average
source of free energy or an actor payment entitlement.

The Langevin paths used in stochastic thermodynamics are not generally
piecewise-smooth curves. The heat integral uses the Stratonovich convention,
whose stochastic chain rule gives the conservative endpoint difference; it is
not justified by applying the foundation's classical path theorem to a Brownian
path without that convention. The first-law proof above avoids that category
error. For the established conventions see [Seifert, §§2.3–2.5, Eqs. (19),
(27)–(31)](https://arxiv.org/pdf/1205.4176); the review uses `k_B=1`, restored
explicitly here.

If extra work is present but the same resolved energy balance still applies,
`Q_med/T=k_BE+W_in/T`, not (13). If the initial ensemble is noncanonical,
the actual `−k_B ln p(x,t)` is not replaced by the stationary density just
because a stationary solution exists. Either change prevents the P4 cancellation
from following as stated. Underdamped motion also requires kinetic-energy and
phase-space bookkeeping rather than the configurational formula alone.

### 13.3 Separate constrained-macrostate entropy

Current authority retains a fourth object. It considers a microcanonical
bead-plus-reservoir composite with fixed total energy, the bead held at `x`,
an `x`-independent constrained configurational entropy, and the reservoir energy
`E_tot−U(x)`. At fixed reservoir volume,

\[
\left.\frac{dS_{\rm res}}{dE_{\rm res}}\right|_{\rm vol}=\frac1T,
\qquad
\left.\frac{d^2S_{\rm res}}{dE_{\rm res}^2}\right|_{\rm vol}
=-\frac1{T^2C_V}.
\tag{15}
\]

To display the reference dependence correctly, write `u(x)=U(x)−U*` and expand
around reservoir energy `E_res*=E_tot−U*`. Smooth reservoir entropy and a small
energy excursion give
`S_constr(x)=constant−u(x)/T+O(u(x)²/(T²C_V))`. Thus between the two constrained
macrostates,

\[
\Delta S_{\rm constr}=k_BE
+O\!\left(\frac{u_{\rm pre}^2+u_{\rm post}^2}{T^2C_V}\right).
\tag{16}
\]

This is the authority's symbolic finite-bath remainder expressed with a declared
expansion reference. It requires the reservoir curvature scale to remain
controlled over the energy excursion and `|u|/(TC_V)` small. It is not exact
canonical equality for an arbitrary finite bath. The reference `T` is that of
the expansion; the finite-bath remainder accounts for its response.
`C_V`, not `C_P`, belongs in (15) because both derivatives are at fixed volume.
No numerical heat capacity, reservoir size or decision rule is introduced.

`ΔS_constr` is a difference between constrained composite macrostates. It is
neither stochastic system entropy along an unconstrained path, nor heat flow,
nor total stochastic entropy production. Its leading equality with `k_BE` is
a separate result. Holding or moving a constraint is not automatically a P4
no-work trajectory. The general foundation ansatz `S=S_eq−κV` remains a
conditional entropy-deficit identification; it is not silently equated with
`s_sys=k_B(V+C)`, which has the opposite dependence on `V`.

### 13.4 S-MG inheritance

If **each** entry of a common-field coalition table satisfies the full P4 scope,
linearity of its already-cleared Möbius transform gives

\[
m_{\Delta s_{\rm med}}(T)=k_Bm_E(T),\qquad
m_{\Delta s_{\rm sys}}(T)=-k_Bm_E(T),\qquad
m_{\Delta s_{\rm tot}}(T)=0.
\tag{17}
\]

An imposed coalition intervention may inject work even when its endpoints lie
in the canonical density's support. Endpoint compatibility alone therefore does
not establish (17) for the intervention. No new entropy, generator or actor
settlement rule is obtained by applying this linear transform.

**S7: COMPLETE within the accepted P4 scope.** No general entropy identification
or physical experiment is needed to complete this conditional proof.

## 14. Mechanical work sign

In the mechanical trap benchmark, for fixed field and temperature,

\[
F_{\rm trap}=-\nabla U,\qquad
W_{\rm by\ trap}=\int F_{\rm trap}\cdot dx
=U_{\rm pre}-U_{\rm post},\qquad
\boxed{E=\frac{W_{\rm by\ trap}}{k_BT}}.
\tag{18}
\]

The work is **by the trap force**. For quasistatic externally imposed motion
against that conservative force, the conservative contribution to external work
is `W_against trap=−W_by trap=ΔU`. For example, with `U(x)=x²/2` in consistent
energy and coordinate units, displacement `0→1` gives trap work `−1/2` and
external work against the trap `+1/2`. Additional dissipative external work,
if present, must be added separately.

`W_by trap` is a conservative force-displacement contribution. It must not be
confused with `W_in`, the parameter/nonconservative driving work in §13's
chosen first-law convention, which vanishes in the static P4 benchmark. This
explains why a nonzero trap-force integral can coexist with the description
“no-work transition.” The sign example involving external control does not
certify a P4 entropy identity for that controlled process.

The foundation's general `−∫∇V·dx` remains a potential-difference theorem,
not a mechanical-work law. Only an independently established relation between
`V` and a mechanical `U` permits (18). Likewise the general directional `f`
is not automatically a measured mechanical force. This is precisely the
cleared R-stage §15 boundary.

## 15. Density and reversibility remain separate

A density describes where a system is distributed. A generator and its boundary
conditions determine how probability moves. For a declared Markov process,
stationarity requires `ℒ*p=0`; a supplied density alone does not prove it.
Detailed balance concerns time reversal of stationary paths and is stronger.

The cleared R-stage §13.3 counterexample suffices. In dimensionless coordinates,
with diffusion operator equal to the Laplacian, let

\[
V(x,y)=\tfrac12(x^2+y^2),\quad
p=(2\pi)^{-1}e^{-V},\quad b=(-x-y,-y+x).
\]

Then `∇p=(-x,−y)p`, so the stationary current is

\[
j=bp-\nabla p=(-y,x)p,\qquad
\nabla\cdot j=-y(-xp)+x(-yp)=0,
\tag{19}
\]

with decay at infinity. Yet `j/p=(0,1)` at `(1,0)`. The normalized Boltzmann
density is invariant under these dynamics despite a nonzero circulating current.
It therefore satisfies the density bridge without ordinary overdamped detailed
balance. This is an analytic witness, not an adopted EBU model or an executed
trajectory. The general divergence-free perturbation construction is established
in [Duncan–Lelièvre–Pavliotis, §1.3, Eqs. (6)–(8)](https://arxiv.org/html/1506.04934).

Matching `p ∝ exp(−V)` can supply the stationary endpoint system-entropy
identity when that density really is the ensemble at both times. It cannot
alone supply the heat/reservoir identity, the no-driving condition, or total
entropy cancellation. The counterexample blocks precisely that inference.
Local detailed balance, when physically justified, also must not be confused
with global detailed balance; driven channel-resolved transitions can obey the
former while sustaining cycle currents. S-MG §23 preserves that distinction.

## 16. S8 — Thermodynamic denomination

Within the canonical benchmark, **one EBU is one dimensionless unit of thermal
potential decrease, equivalently one natural-log unit of endpoint density ratio**:

\[
E=1\quad\Longleftrightarrow\quad
\ln\frac{p_{\rm post}}{p_{\rm pre}}=1
\quad\Longleftrightarrow\quad
U_{\rm pre}-U_{\rm post}=k_BT.
\tag{20}
\]

The ratio uses the same declared measure at both endpoints. It is a ratio of
configuration densities, not the probability of a transition and not a claim
about the probabilities of arbitrary finite bins. With the further P4
conditions, that same positive unit corresponds to `+k_B` entropy delivered to
the reservoir and `−k_B` stochastic system-entropy change. It corresponds to
zero total entropy production in that equilibrium benchmark.

The energy represented by a fixed EBU amount scales with the **local field's
temperature**. EBU therefore is not a fixed number of joules independent of
temperature. The relation `ΔU_drop=k_B T E` is a scoped conversion, not the
retracted declaration `1 EBU=k_B T_ref` as a universal energy-valued unit.

This normalization gives the intended denomination programme a concrete
physical meaning: it compares energy differences against each field's thermal
scale. It does not supply an exchange rate, social welfare metric, ownership
rule, natural incentive or universal ecological burden. Those are separate
claims, not missing assumptions to be concealed in this theorem.

**S8: COMPLETE as a conditional denomination statement.** Source: baseline
§§4, 8, 13–14 and cleared R-stage §§10, 12, 14–15.

## 17. The same unit does not mean an unchanged action value

A new action is evaluated at its current state and field:

\[
E_\theta(a\to b)
=\frac{U_\theta(a)-U_\theta(b)}{k_BT_\theta}.
\tag{21}
\]

Even with the same geometric endpoints, changing stiffness, reference position,
coupling or temperature can change this number. In a one-dimensional harmonic
example `U_θ(x)=½k_θ(x−r_θ)²`, the value is
`k_θ[(a−r_θ)²−(b−r_θ)²]/(2k_B T_θ)`. The physical consequences relative to the
thermal scale have changed. That does not by itself mean the denomination
changed. The same action name may also conceal different endpoints; its
physical transition must be specified before comparing values.

Here “action price” refers only to this EBU valuation, not an institutional
market price. Historical entries retain their recorded value. A field change
does not reprice a completed action, and no new registered allowed action means
no new actor transaction. This preserves the R-stage/S-MG registration
boundary. Permanence is bookkeeping; physical commensurability is a further
claim (§18). Neither determines fairness or individual allocation.

## 18. Cross-field prediction versus evidence

For each member of a family of fields separately satisfying A1–A7, with its
correct thermal normalization, S3 predicts

\[
\beta_{\mathrm{bridge},\theta}=1
\quad\text{for every such field }\theta.
\tag{22}
\]

This is an exact **theoretical canonical prediction**. It does not certify that
the actual physical construction and observed distribution in every planned
experimental field satisfy those assumptions. The programme has not established
cross-field physical denomination empirically. E1a is preserved/paused; no
official campaign or optical-trap experiment is run by this task.

Where every fixed-field transition also satisfies P4, an equal EBU amount
predicts the same multiple of `k_B` medium entropy across fields even though its
energy amount can differ. That conditional consequence is not an experiment
and does not validate arbitrary driven actions, reservoirs or field transitions.

Temperature is a particularly strong denomination check. For a fixed arbitrary
energy scale `B_0`, the superseded construction `Ṽ=(U−U*)/B_0` would instead
give `J=[B_0/(k_B T)]Ṽ+C`. Proper thermal normalization removes that
temperature-dependent coefficient, predicting one for the dimensionless bridge.
The temperature comparison thus probes the physical scaling itself. No field
values, temperature range, sample counts or decision rules are chosen here.

**Status:** common canonical coefficient predicted; actual cross-field
commensurability **EMPIRICALLY UNESTABLISHED**. This is not a human scientific
decision or an unresolved theorem gap. It is the boundary between a completed
conditional theorem and the later empirical programme.

## 19. Relation to topology and S-MG continuity

### 19.1 Fixed-field identities do not wait for the equilibrium anchor

For a single-valued `V_θ`, fixed-field endpoint differences telescope:

\[
\sum_{i=0}^{n-1}[V_\theta(x_i)-V_\theta(x_{i+1})]
=V_\theta(x_0)-V_\theta(x_n).
\tag{23}
\]

A closed cycle gives zero. For `C¹` `V_θ` and admissible piecewise-smooth
curves in its domain, the foundation also gives
`E=−∫_γ∇V_θ·dx`. Because a single-valued potential is supplied, no
simply-connected-domain assumption is needed for this statement. A merely
curl-free field without a supplied global potential is a different problem.

For any finite, complete, consistently declared subset table of endpoints,
S-MG gives, for nonempty `T`,

\[
m_E(T)=\sum_{S\subseteq T}(-1)^{|T|-|S|}E(S)
=-\sum_{S\subseteq T}(-1)^{|T|-|S|}V(x_S).
\tag{24}
\]

Neither (23) nor (24) requires equilibrium, Gaussianity, a generator or
`β_bridge=1`. Physical use of the subset table additionally requires its stated
admissibility and common comparison protocol. Missing corners are not zeros.
Sequential rebasing is distinct from summing same-base action quotes;
nonzero Möbius interaction is consistent with path independence between fixed
endpoints. Interactions decompose already-defined EBU and create no additional
issuance.

S3 supplies a new *interpretation within its physical scope* of that existing
algebra, not its existence. For the same positive canonical density and measure
at all required endpoints, S-MG §24 gives

\[
m_E(T)=\sum_{S\subseteq T}(-1)^{|T|-|S|}\ln p(x_S),
\quad T\ne\varnothing.
\tag{25}
\]

The normalization constant cancels because the signs sum to zero. Under a
constant nonunit bridge coefficient the log contrast instead equals
`β_bridge m_E`. These are endpoint density contrasts, not automatically a
joint distribution of action indicators, cumulants or mutual information.
S7's entropy version needs every coalition's additional P4 conditions.

The quadratic pair-only bound continues to require affine/additive coalition
endpoints as well as a quadratic potential. A nonlinear response can generate
higher-order coefficients even with quadratic `V`. Stable or oscillatory
feedback supplies neither canonicality nor a thermal scale; the feedback
reconciliation §19 explicitly leaves those physical questions separate.

### 19.2 Moving fields and the limit of extended-state algebra

For a declared single-valued `C¹` `V(x,θ)` and an admissible joint path,

\[
V_{\rm pre}-V_{\rm post}
=-\int\nabla_xV\cdot dx-\int\nabla_\theta V\cdot d\theta.
\tag{26}
\]

Endpoint differences telescope on nodes `(x,θ)` as ordinary state-function
arithmetic. The state and field contributions may separately depend on the
joint path. In particular, a field-dependent additive choice for `V` cancels
from fixed-field action values but changes cross-field differences; a consistent
extended declaration must be supplied before interpreting them.

This mathematics establishes neither common physical denomination nor a rule
allocating the field term to an actor. Direct physical addition of historical
EBU from different fields requires justified commensurability, and the empirical
claim remains unestablished. Algebraic extended-state telescoping is already
available; its proposed cross-field physical/accounting use has this extra
requirement. Field evolution alone is not a registered earning event.

## 20. Nonequilibrium boundary

**S-stage establishes no universal nonequilibrium bridge.**

| Away from equilibrium | What remains justified |
|---|---|
| Supplied `V`, finite endpoint differences, telescoping and complete-table Möbius inversion | Their algebra survives under its original domain assumptions |
| Fixed-field classical path identity and extended-state chain rule | Survive with their regularity and admissible-path assumptions |
| Boltzmann density and `β_bridge=1` | Not guaranteed |
| Stationarity, detailed balance and reversible equilibrium | Not guaranteed; one does not infer them from a scalar potential |
| P4 heat/entropy identification and `Δs_tot=0` | Not guaranteed; work, reservoir, ensemble and state boundaries remain essential |
| Stable common thermodynamic denomination across actual fields | Requires its own physical justification and evidence |

Some nonreversible dynamics preserve exactly a Boltzmann density, as §15 shows.
That permits the density algebra there; it does not make the full P4 theorem
universal. Conversely, failure of Boltzmann form does not invalidate the
foundation's arithmetic on a supplied state function. Dynamics, quasipotentials,
native burden scales and feedback metrics are not promoted into the frozen EBU
core by this report.

## 21. Prior-art status

Only a bounded primary-source check was made for classification, not a new
novelty search. The proofs above are short reconstructions from definitions and
cleared source equations. The following selected source material was accessed
on 2026-10-05:

| Source / access | Checked scope | Classification supported |
|---|---|---|
| Feynman, Leighton and Sands, [*The Feynman Lectures on Physics*, I.40](https://www.feynmanlectures.caltech.edu/I_40.html), selected full text, §40–2, Eqs. (40.2)–(40.3), plus the Gaussian integral discussion | Canonical spatial exponential and its logarithmic relation to energy; ordinary Gaussian normalization | Standard classical statistical mechanics and Gaussian calculus |
| U. Seifert (2012), [*Stochastic thermodynamics, fluctuation theorems and molecular machines*](https://arxiv.org/pdf/1205.4176), selected full author manuscript, §§2.3–2.5, Eqs. (19), (27)–(31) | First-law convention, medium entropy, ensemble-dependent stochastic system entropy and total entropy balance | Standard stochastic thermodynamics; `k_B` restored in this report |
| A. B. Duncan, T. Lelièvre and G. A. Pavliotis, [*Variance Reduction using Nonreversible Langevin Samplers*](https://arxiv.org/html/1506.04934), selected full author text, §1.3, Eqs. (6)–(8) | Invariant density with an added weighted divergence-free drift | Density agreement does not imply reversibility |
| Cleared [S-MG prior-art appendix](EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md), §§2, 5–8 | Existing Gibbs/log-linear/Möbius classification and source-access limits | Log-density interaction conversion is not an EBU discovery |

Attempts to access David Tong's canonical-ensemble lecture at two author-site
URLs returned access errors; that material is not relied upon. No complete
review of all pages of the external works is claimed. No quotations from them
are needed for the result.

Canonical weights, the log-density bridge, harmonic inverse covariance and
the stochastic entropy benchmark are standard results. The possible EBU
contribution is its use of the thermal normalization with independent physical
and probability branches and an intended stable-denomination programme tied
to declared physical actions. This report makes **no novelty claim**, and
does not establish empirical success or societal effects of that architecture.

## 22. Formal S1–S8 disposition

“Complete” means the stated conditional theorem and its scope are mathematically
closed for this synthesis task. It does not mean assumptions have been measured
in every field, that the report has passed S9, or that authority has changed.

| Item | Disposition | Verified basis / boundary |
|---|---|---|
| **S1 Canonical equilibrium assumptions** | **COMPLETE** | §4 separates energy, measure, support and normalizer from dynamics, entropy and sampling; R-stage §9.2 / S-MG §23 |
| **S2 Thermal normalization** | **COMPLETE** | §5 checks dimensions, positive temperature and reference cancellation; baseline §14.1 |
| **S3 Direct Boltzmann bridge** | **COMPLETE** | §6 gives the canonical substitution and logarithm with explicit intercept, endpoint sign and non-circular physical provenance |
| **S4 `β_bridge=1`** | **COMPLETE** | §7 gives the coefficient, nonconstant-domain identifiability condition and scale-error orientation `1/c` |
| **S5 General equilibrium non-Gaussian form** | **COMPLETE** | §§9–10; quadraticity is not used, and smoothness enters only for differential claims |
| **General `K=H`** | **COMPLETE** | §10; exact on smooth interior, with no inverse inference from one local Hessian |
| **S6 Harmonic/Gaussian corollary** | **COMPLETE** | §§11–12; global quadratic/full affine support/flat measure/restricted positive definiteness, with cleared truncation counterexample |
| **S7 Entropy / P4 consistency** | **COMPLETE** | §§13–15; additional dynamical, thermal, ensemble and no-driving conditions; four entropy objects kept distinct |
| **S8 Stable thermodynamic denomination meaning** | **COMPLETE** | §§16–18; dimensionless thermal/log unit, not fixed joules or constant action value; actual cross-field realization remains unestablished |

No additional theorem is needed to prove these conditional statements. The
points requiring care were resolved by exposing assumptions already present
in the controlling/cleared sources and by elementary sign and scope checks.
The baseline's unqualified `ΔJ` notation has the sign defect identified in §6
when read as a post-minus-pre change. It is not carried forward with that
reading. The endpoint definition and accepted system-entropy sign already
determine the correct result; this documentary issue is not a gap in S1–S8.

Remaining matters are classified rather than concealed:

| Matter | Classification / next owner |
|---|---|
| Adversarial verification of this theorem artifact | **S9 required**, separate independent auditor |
| Actual energy calibration, density recovery and common coefficient across fields | Later empirical programme; no result asserted |
| Experimental estimators, noise, sample size, apparatus and field construction | Later T/U/V stages, not begun here |
| Universal nonequilibrium bridge or general physical entropy identification | Not established by this equilibrium task |
| New authority adoption | Not conferred by this report or by its local commit |
| Book 1 Chapter 33 malformed rendered `r != 0`; 17 diagram assets versus 16 placed figures | User-reported non-blocking editorial corrections; recorded only, not repaired or recounted here |

**Human scientific decision required for S1–S8: NONE.** The absence of a later
experiment does not create a mathematical gap or require an invented decision.

## 23. T-stage handoff — conditional on S9 clearance

| T-stage may assume if S9 clears | Scope it must preserve |
|---|---|
| Primary theoretical target: **`J=V+C`** | Same physically justified canonical states, measure and support; independent branches |
| Absolute scale prediction: **`β_bridge=1`** | Correct thermal normalization; nonconstant comparison domain for slope identification |
| Cross-field prediction: **the same `β_bridge=1`** | Each field separately satisfies the canonical assumptions; actual evidence is still required |
| General geometry prediction: **`K=H`** | Smooth interior in matching accessible coordinates; does not establish the full landscape in reverse |
| Global covariance prediction: **`Σ_T⁻¹=H_T`** | Only the harmonic, full affine support, flat-measure special case |
| Entropy: **secondary conditional benchmark** | Accepted P4 assumptions; it is not the primary bridge endpoint or total entropy `k_BE` |
| Density agreement | Does not certify stationarity under an arbitrary generator, reversibility, or the whole P4 account |
| Hidden common scale `V̂=cV` | Exact nondegenerate slope is `1/c`, not `c` |

T-stage must retain independent physical construction of `V` and independent
observation of `p`. Nothing here selects moment versus likelihood methods,
finite-sample test size, sample count, observation-noise model, Route-A
apparatus, PRNG, field values or construction, or C1–C8 replacements. Existing
E1a authority, decision rules, plan and seal remain exactly as they are.

**T-STAGE: UNBLOCKED PENDING S9 AUDIT.** This means its theoretical prerequisite
is ready for that independent review; T-stage has not started and is not
authorized to execute by this document.

## 24. Verification record and final status

### 24.1 Bounded verification

Verification is limited to source inspection, direct proofs and counterexamples,
closed-form algebra, strict JSON/AST parsing and byte hashing. Scientific modules
were not imported. No RNG was created, no model was stepped, no trajectories
were generated and no calibration or experimental campaign was run.

The author checked the dependency edges in §3, reference and endpoint signs in
§§5–7, the distinction between landscape/curvature/covariance, the cleared
truncation and nonreversible-current counterexamples, and the P4 first-law and
entropy signs. These checks establish the readiness of the artifact for review;
they do not replace S9.

Twenty-eight small static assertions passed using exact rational arithmetic
and polynomial coefficient differentiation. They cover normalization and
reference cancellation, the reciprocal scale factor, local/global Hessian
counterexamples, restricted matrix inversion, sign and boundary coefficients,
and the canonical Möbius log-contrast. For example, `H=[[2,1],[1,3]]` has
inverse `[[3,−1],[−1,2]]/5`; the three unit-increment coalition contrast of
`V=x²/2+x⁴` at zero is `−36` in both EBU and log-density form. These are
finite algebraic witnesses, not statistical trials, simulated transitions or
substitutes for the general proofs. The document also passed checks of its
24 numbered sections, 26 numbered equations, paired display delimiters, local
source links and protected hash strings.

The repository's analysis and execution identity recipes were inspected directly
in `e1a_v4/identity.py` and `e1a_v4/validation/plan.py`. Independent static
recomputation used their literal source lists, adopted contract values, exact
JSON serialization and SHA-256. The analysis identity covers 12 scientific
modules; the execution identity adds 19 validation modules, the plans, seed map
and separately bound driver bytes. The seal was checked separately.
**This report is excluded from those inspected preimages.** A new Git commit
changes Git history, not those defined scientific identities.

The following protected starting identities were recomputed unchanged before
commit:

| Object | SHA-256 |
|---|---|
| Frozen foundation, 49,098 bytes | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Foundation metadata | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| Working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| R-stage report | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| S-MG theorem | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| S-MG prior-art appendix | `ac8128659ff0955ef16197c37c5698f6039c2f4d074c25e2f9c48ef2e89199ff` |
| Feedback reconciliation | `a18d11d309efcb4490e8dc0b7a86a327026c0a58a755e649722d9a9071882c18` |
| E1a design | `25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6` |
| E1a contract | `d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4` |
| Validation plan JSON | `fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4` |
| Validation plan Markdown | `2d40781593c607de31e68f42e713641a97335e198ed3453bbe677e76682f0d93` |
| Seed map | `c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af` |
| Execution seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` |
| Analysis identity, configuration `{}` | `60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527` |
| Execution identity | `442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b` |

Plan and seal retain `execution_authorised=false`; the seal remains
`PRE_DRIVER`, with expected execution identity `null`. The label is reported
literally and does not assert absence of driver code. The official
`results/e1a_v4_validation` output remains absent.

### 24.2 Change boundary and completion

The starting snapshot covers **2,987 tracked regular files**. Pre-commit
verification confirmed that all of those files retained their bytes and the
only new repository file was
`docs/theory/EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md`. The complete new-file diff,
whitespace, source links and exact staged path were inspected before the local
commit. The enclosing commit identifies the final report without
placing a self-referential commit hash inside its own preimage; its full SHA is
returned with the completion response. No push is performed.

```text
S1–S8:                    COMPLETE AS SCOPED CONDITIONAL RESULTS
GENERAL K=H:              COMPLETE ON THE SMOOTH INTERIOR
S9:                       INDEPENDENT AUDIT REQUIRED; NOT PERFORMED
HUMAN SCIENTIFIC DECISION: NONE
T-STAGE:                  UNBLOCKED PENDING S9 AUDIT; NOT STARTED
CROSS-FIELD DENOMINATION:  THEORETICAL PREDICTION; EMPIRICALLY UNESTABLISHED
NONEQUILIBRIUM BRIDGE:     NOT ESTABLISHED
BOOK 1:                   UNCHANGED
E1a:                      PRESERVED / PAUSED
AUTHORITY MODIFIED:        NO
CODE MODIFIED:             NO
SCIENTIFIC RNG:            NOT USED
MODEL / TRAJECTORY RUN:    NONE
CALIBRATION:               NOT RUN
OFFICIAL CAMPAIGN:         NOT RUN
OPTICAL-TRAP EXPERIMENT:   NOT RUN
EXECUTION AUTHORISED:      FALSE
PUSH:                     NO
```

**S1–S8 EQUILIBRIUM THERMODYNAMIC ANCHOR COMPLETE — S9 INDEPENDENT AUDIT REQUIRED.**
