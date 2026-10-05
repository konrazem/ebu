# EBU — Feedback / oscillation theory reconciliation

## Status and scope

```text
NON-CONTROLLING THEORETICAL RECONCILIATION
R-STAGE: CLEARED
S-MG: CLEARED
OSCILLATION MODEL: ANALYTICALLY RECONSTRUCTED
BOOK 1: NOT MODIFIED
SD-10: NOT EXECUTED
SCIENTIFIC AUTHORITY: UNCHANGED
INDEPENDENT AUDIT: REQUIRED BEFORE BOOK 1 INTEGRATION
```

Prepared 2026-10-05. This report reconstructs conditional mathematics and proposes its
editorial placement. It registers no physical model, controller, valuation calibration,
experiment, actor settlement rule or scientific execution. R-stage and S-MG clearance
are the independent dispositions supplied in the task; they are not new clearance
conferred by this report. The author's algebra checks below are not independent audit.

## 1. Executive result

The historical stock/pipeline oscillator is mathematically correct under its declared
constant-coefficient, lossless, interior-branch assumptions. Its characteristic roots,
underdamped criterion, damping rate and exponential memory reduction follow from the
stock balances. The eliminated pending-stock initial condition must remain in the
reduced equation. A first-order residence compartment is not a fixed transport delay.

The connection to the cleared Möbius–Generator theorem is a conditional composition:

```text
registered action / control mapping
  → separately declared, well-posed feedback generator
  → evolution over a common horizon
  → comparable coalition endpoints
  → fixed potential V
  → finite EBU endpoint values
  → Möbius interaction across the coalition table
```

The generator explains endpoint production; the potential values endpoints; Möbius
inversion decomposes the resulting table. An ODE is not required for finite EBU or
Möbius inversion. Dynamics must neither replace these operations nor acquire authority
merely by being mathematically consistent with them.

Two historical wording clarifications are independently confirmed:

1. The oscillator's unit table declares a native burden unit **B**. No normalization
   from that burden to canonical dimensionless EBU is supplied by the inspected model,
   book section or identification programme. Write this quantity as `V_B`, and retain
   the missing calibration as a gap before interpreting its magnitude as EBU.
2. The historical arrival derivative is correct for its reduced `(S,Q,X)` potential.
   If an explicitly valued sink `W` receives the lost fraction, its contribution is
   `−(1−η)μ_W`. The audited lossless oscillator has `η=1`, so its equations and spectrum
   are unaffected.

The most useful new integration result is conditional but exact: fixed linear feedback
with additive coalition inputs preserves affine finite-horizon endpoints. A quadratic
potential then has no Möbius coefficients of order three or higher, regardless of the
number of oscillatory modes. Section 16 supplies an analytic oscillatory three-action
example with `m_ABC=0`. No trajectory was numerically generated.

## 2. Authority / provenance

### 2.1 Repository identity and precedence

The starting repository is `/Users/konrad.grzyb/code/ebu`, branch
`codex/book-one-continuity`, with a clean working tree:

```text
STARTING HEAD: a7655f30bde7b798ca98eacd9138f93b36abf733
STARTING TREE: d75b6603a87d5b93e27f9046500552dd4e69fbd6
HISTORICAL SNAPSHOT: 4d15bbd2405271c8d5ac6416caf4b49ddc3cded1
HISTORICAL STAGE-F BRANCH HEAD: cc5581c8e60df512bdbfe63889ae4147313edf7e
CACHED origin/gaussian/stage-a-environment: dd0d6b0e5d370de1bda805e07215ea0be4d6d083
```

The current local branch has no upstream configured. The remote reference above is the
local cached reference, not a claim about a freshly queried server. No fetch or push is
part of this task. The latest commits were inspected, including the S-MG report and the
R-stage reconstruction and correction. No unexpected working-tree changes were present.

Repository precedence is unchanged: frozen physical foundation, then working theory
baseline, then exploratory reports. The foundation's legacy unfrozen header is not
reopened: the baseline identifies its freeze provenance, and its canonical bytes are
unchanged. User-supplied subsequent independent clearance of the R/S reports is recorded
separately from their older internal audit-pending wording. Cleared reports remain
non-controlling reconciliations; they do not amend the core.

### 2.2 Source inventory and classification

Current paths below are relative to the repository. Historical paths in the next table
are Git objects, not files silently reinstated into the current checkout.

| Source | Classification and use |
|---|---|
| `AGENTS.md` | Current repository instructions: static-only scope, authority precedence, exact-path commit and no unauthorized execution. |
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` and its metadata | **CURRENT AUTHORITY** for the fixed normalized potential, endpoint sign, directional definitions and conditional physical interpretations. |
| `docs/theory/EBU_THEORY_BASELINE.md` | **CURRENT WORKING THEORY** and authority navigation; preserves conditional boundaries rather than supplying the tank's kinetic laws. |
| `docs/theory/EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md` | **CURRENT WORKING THEORY**, non-controlling, independently cleared per task: fixed-field path identity, physical/ledger distinction and equilibrium/P4 boundaries. |
| `docs/theory/EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md` | **CURRENT WORKING THEORY**, non-controlling, independently cleared per task. Especially §§3–5, 8–16, 17–20, 23–26 and 31: comparable tables, affine/quadratic bounds, generator interface, drift baseline, equilibrium and editorial map. |
| `docs/theory/EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md` | Current non-controlling prior-art mapping; no authority to claim novelty. |
| `CURRENT_SCIENTIFIC_AUTHORITY.md` and `LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md` | Current authority/provenance navigation; retained Stage-F material does not authorize running it on this branch. |
| `EBU_FUTURE_BOOKS_STRUCTURE.md` and `LOCAL_GAUSSIAN_EBU_BOOK_SERIES_RECONCILIATION.md` | **CURRENT editorial authority**, **PROSPECTIVE** architecture, not scientific constitutive authority. Current feedback ownership is Part VII. |
| `SD_01_TO_14_MASTER_TEST_REGISTER.md`, SD-10 row and dependency summary | **PROSPECTIVE** study register: SD-10 blocked on SD-06/SD-07, needs a benchmark. It contains a proposed run scale, not completed results. |
| `docs/history/BOOKS_STRUCTURE_STAGE_F_4d15bbd.md` | **HISTORICAL** editorial snapshot. Its numbering must be translated through the current book map. |
| `Foundation_v2.7_math.md` and `Foundation_v2.8_discrete_draft.md` | **HISTORICAL / SUPERSEDED for current core precedence**; provenance of older burden/force/response vocabulary, not authority to replace the normalized current potential. |

The following were inspected from snapshot `4d15bbd2405271c8d5ac6416caf4b49ddc3cded1`:

| Historical path | Git blob | Classification / relevant content |
|---|---|---|
| `COUPLED_INTERACTION_INFERENCE_FEEDBACK_STABILITY_PROGRAMME_REVIEW.md` | `637f192832bd76f767a078508ecde13be481ec7e` | **HISTORICAL, PROSPECTIVE, EMPIRICALLY UNTESTED** programme; §§4–6 and 10–15 separate outcome inversion, correction, conjugacy, hidden memory and continuous/discrete stability. |
| `CLOSED_LOOP_CORRECTION_DYNAMICS_MILESTONE_AUTHORITY.md` | `8dad2f834185359eeec025508d5e2ed0b3f4406a` | **HISTORICAL prospective stage authority**: CLCD-A declarations, CLCD-B inert implementation, separately authorized CLCD-C science. Retained provenance is not present execution permission. |
| `CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_AUTHORITY.md` | `088ff2c9e418993191127a11959bcd8f43919400` | **HISTORICAL prospective implementation authority**: exact diagnostics, not a feedback-study result. |
| `research_notes/STOCK_PIPELINE_FEEDBACK_DERIVATION.md` | `0abb01f86d47b77ff3f96a0a9ece31c7a896f963` | **HISTORICAL, UNREGISTERED, EMPIRICALLY UNTESTED** analytical model construction; §§3–8 provide balances, Jacobian, action directions, oscillator and countermodels. |
| `research_notes/BURDEN_FEEDBACK_LORENTZ_BOOK_SECTION.md` | `aa1446ea820f2e1e40c688fbc23c5851981ce318` | **HISTORICAL, BOOK-ONLY, EMPIRICALLY UNTESTED** worked section; units in §1, oscillator §§2–4, stability/shortage §§5–7. Introduced at `1234710bbc332688cb4e1fb8be3653337ce82ac4`; not an integrated regenerated volume. |
| `research_notes/MOBIUS_IDENTIFICATION_FEEDBACK.md` | `82c100fba386388a331eed3ee1c2dcc73a390fc2` | **HISTORICAL, PROSPECTIVE, EMPIRICALLY UNTESTED** identification synthesis; inversion does not identify a unique causal mechanism or independently identify every coefficient. |
| `research_notes/NATIVE_BURDEN_RESPONSE_IDENTIFICATION_PROGRAMME.md` | `93bf5a9930275ca217046cdff369f0cb55600602` | Explicit **UNREGISTERED**, high-priority future research. Native burdens and measured response require separate domain declarations; the tank quadratic is a model-specific choice, not a discovered universal metric. |
| `src/ebu_framework/correction_diagnostics.py` and `tests/framework/fixtures/closed_loop_correction_diagnostics_v1.json` | Read at the same historical snapshot | **HISTORICAL implementation/fixtures**: algebraic classifier, conjugacy and path diagnostics; fixture records declare `model_steps: 0`. Static source inspection only here. |
| `research_notes/check_burden_feedback_lorentz.py` | Read at the same historical snapshot | **HISTORICAL exact arithmetic check**, not an empirical dataset or trajectory. Its identities were independently reconstructed below. |

These classifications can overlap: a correct historical book derivation can also be
unregistered and empirically untested. The historical files are recoverable with
`git show <snapshot>:<path>`; their absence from the current checkout does not erase
their provenance or promote them into current scientific authority.

### 2.3 Protected reference identities

SHA-256 identities checked before report creation:

| Current source | SHA-256 |
|---|---|
| Canonical physical foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Foundation metadata | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| Working theory baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| R-stage reconstruction | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| S-MG theorem | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| S-MG prior-art appendix | `ac8128659ff0955ef16197c37c5698f6039c2f4d074c25e2f9c48ef2e89199ff` |
| Current future-book structure | `e9361596e3424cc5043977715a474867116edbc2d01dc3b387401a41e8e0ec68` |
| Current book-series reconciliation | `12bc1e016fbdb91fde0e3a9625a5d42b45019c4d7bda5c0c4729acf42f5ba15c` |

The permitted change is this new report alone. Section 25 records broader byte-preservation
and static validation; no authority amendment is encoded by the proofs that follow.

## 3. Historical feedback model

Let physical source inventory be `S`, pending inventory `Q`, and usable receiver stock
`X`, all for one resource. Let `D` dispatch from source to pending, `A` complete pending
stock, `η` be the usable arrival fraction, `ℓ` a separate pending loss rate, `I_s` source
input, and `R,C` receiver supply and consumption. The historical accounting is

\[
\dot S=I_s-D,\qquad \dot Q=D-A-\ell,\qquad
\dot X=R-C+\eta A.
\]

Consequently,

\[
\frac{d}{dt}(S+Q+X)=I_s+R-C-\ell-(1-\eta)A.
\]

This is an open represented-resource account. Internal conversions require their
receiving coordinates when the boundary includes them. A maintained source does not
mean replenishment or process costs are free.

The specific oscillator imposes a maintained source with zero marginal burden on the
relevant branch, fixed positive `w,M,τ,h`, lossless arrival `η=1`, `ℓ=R=0`, constant
consumption `C=h`, no active capacity constraints, and one smooth deficit branch
`0<X<L`. Its native receiver burden and two additional laws are

\[
V_B(X)=w(L-X)^2,\quad
D=M[-V_B'(X)]=\nu(L-X),\quad \nu=2wM,\quad A=Q/\tau.
\]

The dispatch law uses the currently evaluated completed-transfer shortage signal and
ignores `Q` in that signal. It is an explicit controller policy, not a consequence of
stock conservation, and not the instantaneous source-to-pipeline derivative. Arrival
is an independently declared first-order residence law. Neither law follows solely
from the EBU potential. The two internal balances are therefore

\[
\boxed{\dot X=Q/\tau-h,\qquad \dot Q=\nu(L-X)-Q/\tau.} \tag{F1}
\]

### Separate error-feedback structures

The historical coupled-feedback programme also studies a general correction state,
continuous block systems and discrete residual recurrences. The tank is one physically
interpreted specialization, not an identification of every error loop with a pipeline.

| Object | Meaning |
|---|---|
| `L−X` | Service shortage on this deficit branch. |
| `x=X−X_*` | Deviation from the driven operating point. |
| `r=X−X_hat` | Prediction residual for a declared forecast and information set. |
| Controller signal / `u` | Input specified by a policy; its definition need not equal any of the above. |
| `−∇V·s` | Directional potential decrease per unit action extent. |
| Physical feedback signal | A measured or transmitted quantity and its declared response law. |
| `E=V_pre−V_post` | Finite endpoint valuation, not a residual or controller state. |

For the immediate discrete correction `r_(n+1)=(1−κ)r_n`, stability is `0<κ<2`;
`κ=1` is deadbeat and `1<κ<2` gives alternating decay. At `κ=0` the residual persists,
and at `κ=2` it alternates without decay. Outside `[0,2]` a nonzero residual grows.

For the one-step-old correction `r_(n+1)=r_n−κr_(n−1)`, the polynomial is
`z²−z+κ`. Both roots lie inside the unit circle exactly for `0<κ<1`: real modes
for `0<κ<1/4`, a repeated root at `1/4`, and complex decaying modes for `1/4<κ<1`.
At `κ=0` a neutral mode remains; at `κ=1` the roots are `exp(±iπ/3)` and generic
nonzero solutions are periodic with period six. Outside `[0,1]` an unstable mode exists.
These are distinct sampled models, not the tank equation or its automatically selected
discretization. Their sampled gains are dimensionless; a sampling-time bridge needs a
separate derivation. Their restoring signs are consistent with their stated equations.

## 4. Units and normalization

The historical book section explicitly declares resource unit `U`, physical time `T`,
and burden unit `B`, with no assertion that B is a joule. It does not establish B as
canonical EBU merely by using the letter `V` or the phrase EBU burden.

| Quantity | Units |
|---|---|
| `X,Q,L,x,q` | `U` |
| `D,A,h,u` | `U/T` |
| `τ` | `T` |
| `ν=2wM` | `1/T` |
| `w` | `B/U²` |
| `M` | `U²/(B T)` |
| `V_B`, auxiliary `𝓔_B` | `B` |
| `−V_B'`, directional derivative per resource extent | `B/U` |
| `λ,α,ω` | `1/T` |
| Memory kernel `𝒦` below | `1/T²` |

Thus `M(−V_B')`, `ν(L−X)` and `Q/τ` are rates `U/T`. All terms in each stock
balance have the same units. The normalized characteristic polynomial has units
`1/T²`; `τλ²+λ+ν` has units `1/T`. In `τ ẍ+ẋ+νx=0`, every term is `U/T`;
in its version divided by τ, every term is `U/T²`. The discriminant `1−4ντ`
and damping ratio are dimensionless. The stability derivative below has units `B/T`.

**Case A: canonical normalized potential.** Under the current normalization, `V` is
dimensionless, so `E=V_pre−V_post` is dimensionless EBU valuation. If the same quadratic
shape is legitimately adopted with dimensional stocks, its coefficient has units
`U⁻²`, and a corresponding dispatch response coefficient has units `U²/T`.

**Case B: native burden.** `V_B=w(L−X)²` carries B. Its difference is native burden
relief, not automatically a canonical EBU magnitude. A declared, justified mapping
into the current normalized potential, with fixed evaluation conventions and any
required calibration/reference scale, is missing from the inspected historical model.
The native-burden programme expressly leaves model-specific burden declarations and
empirical response identification open. No source inspected here supplies this bridge.

For illustration of the dimensional requirement only, **if independently justified**, a
fixed positive scale `B_0` with units B and fixed offset `c_B` could support

\[
V=(V_B-c_B)/B_0,\quad E=[V_B(\mathrm{pre})-V_B(\mathrm{post})]/B_0,\quad
w_0=w/B_0,\quad M_0=B_0M,\quad 2w_0M_0=\nu.
\]

This does not select `B_0`, make an arbitrary scaling scientifically authoritative, or
claim that this affine map is the only permissible future normalization. A nonlinear
map changes the gradient/curvature relationship and requires a new dispatch derivation;
a changing field or scale also changes the comparison. Frequency identifies neither
an absolute burden scale nor the separate factors `w,M`. The two quantities must remain
distinct in Book 1 until a suitable mapping is actually declared.

## 5. Operating point

Steady stock levels require `A_*=D_*=h`. Therefore

\[
Q_*=\tau h,\qquad X_*=L-h/\nu. \tag{1}
\]

With positive coefficients and `L>h/ν`, this is an interior state with
`0<X_*<L`, `Q_*>0`, positive dispatch and positive ongoing consumption. Define

\[
x=X-X_*,\qquad q=Q-Q_*.
\]

A negative `q` is below-normal pending stock, not negative physical inventory.
Since the shortage persists,

\[
\boxed{V_B(X_*)=w(h/\nu)^2>0,\qquad V_B'(X_*)=-2wh/\nu\ne0.} \tag{2}
\]

A stationary stock level under maintained flow is not zero burden, a minimum of this
receiver potential, or automatically thermodynamic equilibrium. Globally affine
mathematical equations may leave the physical branch; physical conclusions require
an invariant feasible neighborhood or an explicit admissibility proof.

## 6. Linearization

Subtracting (1) from (F1) gives exactly

\[
\boxed{\dot x=q/\tau,\qquad \dot q=-\nu x-q/\tau.} \tag{3}
\]

There is no Taylor error for the stated affine branch laws. For the more general
historical factorization

\[
\dot X=R(X)-C(X)+\eta A(Q),\qquad
\dot Q=D(X,Q)-A(Q)-\ell(Q),
\]

the local Jacobian at a feasible operating point instead has the form

\[
J=\begin{pmatrix}-a&b\\-k&-d\end{pmatrix},\quad
 a=C'-R',\ b=\eta A',\ k=-D_X,\ d=A'+\ell'-D_Q.
\]

For `C¹` laws the remainder is `o(‖(x,q)‖)`; for `C²` laws it is `O(‖(x,q)‖²)`.
The local characteristic polynomial is
`λ²+(a+d)λ+(ad+bk)`. It is Hurwitz exactly when `a+d>0` and `ad+bk>0`;
complex modes require `(a−d)²<4bk`. These are linearization statements, not a
universal exact sinusoidal solution for a nonlinear system. If the observable is
decoupled, an eigenmode need not be visible in it.

For the tank, `a=0`, `b=d=1/τ`, `k=ν`. A receiver deficit increases dispatch,
which later increases arrival: the sign is restoring for `ν>0`. Reversing this sign
with physical `τ>0` produces a saddle, as §8 shows. No mislabeled positive-feedback
sign was found in the inspected equations. Terminology alone cannot impose a sign on
the derivatives of a more general controller.

## 7. Characteristic roots

For (3),

\[
J=\begin{pmatrix}0&1/\tau\\-\nu&-1/\tau\end{pmatrix},\qquad
\det(\lambda I-J)=\lambda(\lambda+1/\tau)+\nu/\tau.
\]

Thus, for `τ≠0`,

\[
\lambda^2+\frac\lambda\tau+\frac\nu\tau=0
\quad\Longleftrightarrow\quad
\tau\lambda^2+\lambda+\nu=0,
\]

and completing the square gives

\[
(2\tau\lambda+1)^2=1-4\nu\tau,\qquad
\boxed{\lambda_\pm=\frac{-1\pm\sqrt{1-4\nu\tau}}{2\tau}.} \tag{4}
\]

Trace `−1/τ`, determinant `ν/τ` and units all agree. The roots are rates.
Differentiating `ẋ=q/τ` and substituting `q=τẋ` also gives

\[
\boxed{\tau\ddot x+\dot x+\nu x=0.} \tag{5}
\]

With extra dispatch `u(t)` in `q̇`, the right-hand side of (5) is `u(t)`.
A changing consumption rate would need its own derivation; it cannot be inserted as
an identical dispatch input without checking the stock equations.

## 8. Oscillation criterion

For the declared physical domain `ν>0, τ>0`:

| Regime | Eigenmodes | Stability |
|---|---|---|
| `0<4ντ<1` | Two distinct real negative rates | Asymptotically stable |
| `4ντ=1` | Repeated rate `−1/(2τ)`; the matrix is not scalar and is defective | Asymptotically stable, critical damping; `x=(C_1+C_2t)e^(−t/(2τ))` |
| `4ντ>1` | Complex conjugate rates with real part `−1/(2τ)` | Asymptotically stable, damped oscillatory modes |

Thus **`4ντ>1` is necessary and sufficient for complex oscillatory eigenmodes in
this two-state model**. An observed oscillation also requires a nonzero excitation and
an observable projection onto the mode. The unperturbed operating point stays still.
Real modes can produce a nonmonotone transient for some initial states without
producing an underdamped sinusoidal mode.

For completeness, the purely algebraic extension outside the physical domain is:

| Parameters | Result |
|---|---|
| `τ>0, ν<0` | Negative determinant: one positive and one negative real root, a saddle. |
| `τ>0, ν=0` | Roots `0,−1/τ`; no asymptotic convergence of every state to the origin. |
| `τ<0, ν>0` | Negative determinant: a saddle. |
| `τ<0, ν=0` | Roots `0,−1/τ`, with a positive root. |
| `τ<0, ν<0` | Positive trace and determinant: growing real, repeated or complex modes as `1−4ντ` is positive, zero or negative. |
| `τ=0` | Original residence equations undefined; (4) cannot be evaluated. |

A zero-residence *reduced model* sets arrival equal to dispatch and gives
`ẋ=−νx`. This is a singular reduction, potentially with an initial fast transient,
not substitution of zero into a formula containing `1/τ`.

The inequality is neither a universal EBU oscillation law nor a condition for arbitrary
nonlinear, delayed, discrete or hybrid feedback. In particular, the different policy
`D=ν(L−X−Q)` gives

\[
X_*=L-h/\nu-\tau h,\quad Q_*=\tau h,\quad
\det(\lambda I-J)=(\lambda+\nu)(\lambda+1/\tau).
\]

Its interior requires `L>h/ν+τh`; both rates are real and negative. Tracking pending
stock is necessary for complete state accounting, but neither forces this policy nor
proves oscillation. The changed operating point also prevents treating this example as
a matched empirical performance comparison.

## 9. Damping / frequency

In the underdamped regime,

\[
\lambda_\pm=-\alpha\pm i\omega,\quad
\boxed{\alpha=\frac1{2\tau},\qquad
\omega=\frac{\sqrt{4\nu\tau-1}}{2\tau}.}
\]

A free response has the form

\[
x(t)=e^{-\alpha t}[C_1\cos(\omega t)+C_2\sin(\omega t)].
\]

The amplitude decay rate is `α`, the angular frequency is `ω`, the ordinary frequency
is `ω/(2π)`, and the oscillation period is `2π/ω`. Rates and frequencies have units
`1/T`; the period and envelope time `1/α=2τ` have units T. Also

\[
\omega_0=\sqrt{\nu/\tau},\qquad
\zeta=\frac{1}{2\sqrt{\nu\tau}},\qquad
\omega^2=\omega_0^2-\alpha^2.
\]

Stronger restoring response `ν` and the residence timescale `τ` jointly determine the
regime through `ντ`. The envelope and frequency remain separate quantities. At fixed
`ν`, frequency need not increase monotonically with τ.

The historical Lorentz comparison is an equality of differential-equation form with
`ÿ+Γẏ+ω_0²y=F/m`, where `Γ=1/τ`. It does not identify inventory with momentum,
B with mechanical energy, or feedback with an electromagnetic wave. It is the Lorentz
optical oscillator, not the Lorenz chaotic system. The historical distinction between
a free underdamped mode (`ντ>1/4`) and a nonzero-frequency displacement-response peak
under sinusoidal dispatch (`ντ>1/2`) is also correct for this transfer function.

Under informative free-mode observations **and this validated model**, inverse formulas
would give `τ=1/(2α)` and `ν=(α²+ω²)/(2α)`. They identify `wM`, not separate `w,M`,
a normative service threshold, or an absolute EBU calibration. No observations were
fitted. Frequency, damping, eigenvalues and phase lag are dynamical quantities, not EBU
prices; price requires the declared finite potential difference.

## 10. Memory-kernel reduction

Multiply `q̇+q/τ=−νx` by `e^(t/τ)` and integrate from the initial time zero:

\[
q(t)=e^{-t/\tau}q_0-\nu\int_0^t e^{-(t-s)/\tau}x(s)\,ds.
\]

Hence

\[
\boxed{\dot x(t)=\frac{q_0}{\tau}e^{-t/\tau}
       +\int_0^t\mathcal K(t-s)x(s)\,ds,\quad
\mathcal K(r)=-\frac\nu\tau e^{-r/\tau}\mathbf1_{r\ge0}.} \tag{F2}
\]

The convolution is over past `s≤t`. It is causal, has negative sign for positive
`ν,τ`, and decays with τ. Its integral over nonnegative lag is `−ν`, not one;
it is a restoring kernel, not a probability density. The normalized residence factor
`e^(−r/τ)/τ` integrates to one, but the complete kernel includes `−ν`.
The kernel's units `T⁻²` give `U/T` after multiplication by stock and integration.

An added dispatch input contributes the separate forcing convolution

\[
\frac1\tau\int_0^t e^{-(t-s)/\tau}u(s)\,ds
\]

to `ẋ`. Omitting that term is justified only for the unforced deviation system.

For a general constant block system

\[
\dot x=Ax+Bc,\qquad\dot c=Cx+Dc,
\]

elimination yields

\[
\dot x=Ax+Be^{Dt}c_0+\int_0^t Be^{D(t-s)}Cx(s)\,ds. \tag{6}
\]

Here the memory kernel is `Be^(Dr)C`; the tank specializes to
`A=0,B=1/τ,C=−ν,D=−1/τ`. Multiple hidden linear states give a matrix exponential,
with sums of modal exponentials and possibly polynomial factors for Jordan blocks.
Decay requires stability of the contributing hidden dynamics. Time-varying linear
systems use a two-time transition matrix; nonlinear hidden dynamics generally give
a nonlinear history functional. One exponential compartment proves no universal
exponential-memory law.

## 11. Initial-condition term

The compulsory homogeneous contribution in (F2) is

\[
\boxed{(q_0/\tau)e^{-t/\tau},\qquad q_0=Q(0)-Q_*.} \tag{7}
\]

It vanishes when **deviation** `q_0=0`, meaning `Q(0)=Q_*`, not an empty physical
pipeline. In particular `Q(0)=0` would give `q_0=−τh` here. At `t=0`, (F2)
correctly gives `ẋ(0)=q_0/τ`. Dropping (7) for an arbitrary pending state changes
the initial-value problem.

Given declared inputs, `(x,q)` is a Markovian deterministic two-state representation.
The scalar `x` description is nonlocal in history and still needs the eliminated
initial state. Equivalently, the second-order scalar equation needs both `x(0)` and
`ẋ(0)=q_0/τ`. These formulations are equivalent only with those data carried over.
Two identical present `x` values with different pending stock have different futures.

Historical discussion uses “delay” broadly for memory and pending effects; the detailed
stock/book sources already distinguish a residence model from a fixed travel time.
Book 1 should consistently call τ a **first-order lag / residence timescale**. A true
fixed transport time `d>0` would impose `A(t)=D(t−d)` with a compatible dispatch
history and lead, for the same shortage policy, to

\[
\dot x(t)=-\nu x(t-d),\qquad \lambda+\nu e^{-\lambda d}=0.
\]

That is a delay differential equation with a different spectrum and a history state.
Equal total Q need not imply equal scheduled arrivals. An age distribution, due-event
state or equivalent history cannot be dropped merely to reuse the two-state formula.

## 12. Stability measure versus EBU

The historical auxiliary quantity should be written with a distinct symbol and native
unit:

\[
\boxed{\mathcal E_B(x,q)=wx^2+\frac{q^2}{2M\tau}.} \tag{8}
\]

Both terms have units B, and the form is positive definite for positive `w,M,τ`.
Its stock term is the burden with its operating-point tangent removed:

\[
V_B(X)-V_B(X_*)-V_B'(X_*)(X-X_*)=wx^2.
\]

It is therefore neither the receiver burden `V_B(X)` nor the finite EBU difference
`E`. The pending term is chosen to cancel a dynamical cross term; it is not an
independently established valuation of pending inventory.

Using `ν=2wM`,

\[
\dot{\mathcal E}_B
=2wx\frac q\tau+\frac q{M\tau}\left(-2wMx-\frac q\tau\right)
=\boxed{-\frac{q^2}{M\tau^2}\le0.} \tag{9}
\]

Zero derivative at one instant does not establish rest: at `q=0`,
`q̇=−νx`, so the largest invariant subset of `q=0` is the origin.
The spectrum or the invariant-set argument proves asymptotic stability of the affine
model. Applied physically, the conclusion is limited to an invariant neighborhood
that satisfies the branch/boundary assumptions. With dispatch forcing,
`𝓔̇_B=−q²/(Mτ²)+qu/(Mτ)`; an input may inject deviation. Units B/T do not make
this mechanical power without an additional physical identification.

The historical individual-state counterexample checks exactly. In compatible units,
let `w=1`, `M=1/2`, `τ=2`, `ν=1`, `L=10`, `h=2`. Then `(X_*,Q_*)=(8,4)`.
At the admissible state `(X,Q)=(9,3)`, `(x,q)=(1,−1)` and

\[
V_B=1B,\quad V_B(X_*)=4B,\quad \dot V_B=+1B/T,\quad
\mathcal E_B=\tfrac32B,\quad\dot{\mathcal E}_B=-\tfrac12B/T.
\]

This is single-state arithmetic, not a trace. Receiver burden increases as deviation
from a persistently burdened operating point shrinks. A fixed positive affine
normalization preserves that sign distinction, but no absolute EBU scale was thereby
calibrated. Stabilizing a controller need not improve the declared valuation or total
source/process account. Objective alignment is an additional model/policy condition.

A related historical obstruction is correctly scoped: for an unforced instantaneous
symmetric gradient law `ż=−G(z)∇V(z)`, `G=Gᵀ⪰0`, at a smooth critical minimum
with Hessian `H⪰0`, the linearization `−G_*H` has real nonpositive eigenvalues.
For positive definite `G_*` this follows by similarity to
`−G_*^(1/2)HG_*^(1/2)`; the nonzero-spectrum conclusion extends to semidefinite
`G_*`. Moreover `V̇=−∇VᵀG∇V≤0` forbids a nonconstant periodic orbit: zero
integrated dissipation forces zero velocity along it. This obstruction does not apply
unchanged to driven, lagged, discrete or arbitrary controlled systems such as (F1).

## 13. Generator interpretation

Use `T_f` for the observation horizon so that it cannot be confused with residence
parameter τ. On the declared branch the augmented feedback generator with additional
dispatch is

\[
z=(x,q),\qquad b(z,u)=
\begin{pmatrix}q/\tau\\-\nu x-q/\tau+u\end{pmatrix}.
\]

For an admissible coalition `\mathcal S`, a registered mapping supplies `u_\mathcal S`;
a well-posed flow supplies `z_\mathcal S(T_f)=\Phi^{T_f}_{u_\mathcal S}(z_0)`.
The fixed potential is then evaluated on the corresponding physical state. Recording
Q as future-relevant state does not require that a particular potential value Q;
the valued coordinates and all boundaries must be declared explicitly.

The raw endpoint table is

\[
E^{\rm raw}_{\mathcal S}=V(z_0)-V(z_{\mathcal S}(T_f)).
\]

With autonomous drift, `z_∅(T_f)` need not equal `z_0`, so `E^raw_∅` need not be
zero. A declared empty-coalition-relative comparison is

\[
E_{\mathcal S}=V(z_\varnothing(T_f))-V(z_{\mathcal S}(T_f))
=E^{\rm raw}_{\mathcal S}-E^{\rm raw}_\varnothing.
\]

This subtraction changes the empty coefficient and the total reference value, while
leaving every nonempty Möbius coefficient unchanged. It does not automatically remove
all causal confounding, price a transaction, or revalue an old actor entry. The explicit
example below starts at the operating point with zero empty input, so raw and relative
tables coincide.

Each coalition must share the declared initial state, horizon, field, boundary and
comparison conventions, and be admissible under them. A complete comparable outcome
table permits inversion even without continuous dynamics. Missing coalitions cannot
silently be replaced by zero. Abstract controls are not by themselves authorization
for physical acts, causal experiments, or actor settlements.

## 14. Oscillation versus Möbius interaction

For a complete fixed-baseline table,

\[
m_T=\sum_{\mathcal S\subseteq T}(-1)^{|T|-|\mathcal S|}E_{\mathcal S}.
\]

| Concept | What it describes |
|---|---|
| Eigenvalues / poles | Temporal modes of a specified dynamical system or its linearization/transfer representation. |
| Oscillation | A temporal response property; complex modes also need excitation and observation. |
| Möbius order | The number of action labels in a cross-coalition finite difference of endpoint values. |
| Interaction source | The composed table `V∘z(\mathcal S)`, including potential shape, response and comparison conventions. |

Oscillation alone implies neither pair nor triple interaction. For example, the linear
feedback of §16 with a linear potential gives a linear coalition table and no
coefficients of order two or higher, while retaining oscillatory responses. With its
quadratic potential it has pair terms but identically zero triple terms. Conversely,
the monotone example in §17 has a nonzero triple term without oscillation. These
counterexamples establish that neither modal complexity nor interaction order
determines the other.

The historical coordinate claim also needs its premise: if a complete outcome vector
really is the state of a declared common linear evolution `Ė=A_E E`, a fixed invertible
Möbius matrix `\mathsf M` and inverse zeta matrix `\mathsf Z` give
`ṁ=\mathsf M A_E\mathsf Z m`. This similarity preserves eigenvalues; the coordinate
change creates no oscillatory mode. However, a collection of alternative finite-horizon
experiments does not automatically form one such physical evolving state. Repeatedly
inverting endpoint tables is not evidence for a closed generator in interaction
coordinates. Truncation is not invertible conjugacy, and a time-varying transformation
adds a derivative term.

Similarly, the historical feedback influence expression
`P exp(K_aug t)J−exp(At)` compares two specified evolution operators. For the block
system in (6), with `P` projecting onto x and `J` injecting zero hidden deviation,
the difference begins at `BC t²/2`; in the tank `BC=−ν/τ`. This is an algebraic
feedback contribution relative to that comparator. It supplies neither an automatically
valid physical counterfactual nor new modes merely from Möbius coordinates.

## 15. Linear feedback / affine endpoint theorem

**Theorem F3 (conditional affine endpoint preservation).** Let every admissible
coalition share the initial state `z_0`, finite horizon `T_f`, integrable coefficients,
and the same well-posed linear state dynamics. Allow a common forcing `g_0(t)` and
fixed additive action inputs `g_i(t)`:

\[
\dot z=F(t)z+g_0(t)+\sum_{i\in\mathcal S}g_i(t). \tag{10}
\]

Then the endpoint is affine in the coalition indicators:

\[
\boxed{z_{\mathcal S}(T_f)=z_\varnothing(T_f)+\sum_{i\in\mathcal S}h_i(T_f).}
\]

**Proof.** Let `U(t,s)` be the common state-transition matrix. Variation of constants
and linearity of integration give

\[
z_\varnothing(T_f)=U(T_f,0)z_0+
\int_0^{T_f}U(T_f,s)g_0(s)\,ds,\quad
h_i(T_f)=\int_0^{T_f}U(T_f,s)g_i(s)\,ds.
\]

Substitution into (10), or uniqueness of the initial-value problem, proves the claim.
The theorem concerns actual endpoints, not a small-time approximation. A fixed common
state-feedback gain can be included in F. Coalition-dependent gains generally cannot.

Any finite number of linear hidden/feedback modes is allowed, including complex modes,
repeated roots and time-varying common matrices. Stability is not necessary for the
finite-horizon algebra provided endpoints exist and remain admissible. For physical
constraints, every coalition used must remain in the same unswitched affine model;
otherwise the premise is lost. “Input-affine” or “linear in state for each fixed input”
is weaker than (10): a term `u z` makes the state matrix input-dependent and need not
produce additive finite-time responses.

## 16. Quadratic pair-only feedback corollary

**Corollary F3a.** Under F3, let one fixed potential on all relevant endpoints be

\[
V(z)=c+\ell^Tz+\tfrac12 z^THz,\qquad H=H^T.
\]

Write `\bar z=z_∅(T_f)`. Expansion yields

\[
E_{\mathcal S}=
-\sum_{i\in\mathcal S}(\ell+H\bar z)^Th_i
-\frac12\sum_{i,j\in\mathcal S}h_i^THh_j.
\]

On Boolean indicators, squares reduce to the indicator itself. Thus

\[
m_{\{i\}}=-(\ell+H\bar z)^Th_i-\tfrac12h_i^THh_i,\quad
m_{\{i,j\}}=-h_i^THh_j,\quad
\boxed{m_T=0\quad\text{for }|T|\ge3.} \tag{11}
\]

An empty raw drift value contributes only to `m_∅`. This is an exact consequence of
the S-MG affine/quadratic theorem at every common finite horizon. It does not require
positive-definite H, and a rank-deficient receiver-only potential is legitimate as a
supplied valuation. It does not assert a normalizable full-state equilibrium density.

### Analytic oscillatory example with zero triple interaction

For an abstract teaching example, explicitly use nondimensional state and time and a
**declared dimensionless potential** `V(X,Q)=(3−X)²/2`. This is a new analytic
construction, not calibration of historical B, a registered test or a fitted process.
Take `ν=τ=1`, `w_0=1/2`, `M_0=1`, `L=3`, `h=1`, giving `(X_*,Q_*)=(2,1)`.
All three action labels add a constant extra dispatch `ε=1/100`, over the same horizon.
For a coalition of size `m=0,1,2,3`, with common initial deviation `(0,0)`, the equations
are

\[
\dot x=q,\qquad\dot q=-x-q+m\epsilon.
\]

Here `4ντ=4>1`. Set `ω=√3/2` and

\[
g(t)=1-e^{-t/2}\left[\cos(\omega t)+\frac1{\sqrt3}\sin(\omega t)\right],
\qquad
\dot g(t)=\frac2{\sqrt3}e^{-t/2}\sin(\omega t).
\]

Direct differentiation gives `g̈+ġ+g=1`, `g(0)=ġ(0)=0`. Hence the exact
solution functions are `x_\mathcal S=mεg(t)`, `q_\mathcal S=mεġ(t)`.
For a nonempty coalition, `x−mε` is a nonzero decaying sinusoid and `q` changes sign
repeatedly. These are oscillatory transients about the input-shifted operating point;
the empty coalition remains still. Stating and differentiating these functions does
not numerically advance a model.

Feasibility is analytic too. For all `t≥0`,
`|g(t)|≤1+2/√3<3`, `|ġ(t)|≤2/√3<2`. Thus for every coalition
`|x|<0.09`, `|q|<0.06`, so `1.91<X<2.09`, `Q>0.94`, and
`D=1−x+mε>0.91`. The receiver stays strictly within `(0,3)`, pending stock and
dispatch remain positive, and no capacity switch is invoked. The maintained source
and absent binding capacities remain explicit assumptions, not a resource-cost claim.

For any fixed horizon `T_f`, put `r=εg(T_f)`. The complete table, grouped by size, is

\[
E_0=0,\quad E_1=r-\tfrac12r^2,\quad
E_2=2r-2r^2,\quad E_3=3r-\tfrac92r^2.
\]

Every singleton has `E_1` and every pair `E_2`. Therefore

\[
m_{AB}=E_2-2E_1=-r^2,\qquad
\boxed{m_{ABC}=E_3-3E_2+3E_1-E_0=0.}
\]

These expressions hold symbolically in r; no horizon scan, generated time series or
scientific RNG was used. Replacing the potential by a linear supplied potential such
as `V=X` gives `E_m=−mr` and zero pair as well as higher interaction, with the same
dynamics. Neither potential example asserts an equilibrium or an actor payout.

## 17. Nonlinear feedback / higher-order interaction boundary

**Boundary F4.** Coalition-dependent gains, gain scheduling, saturation, switching,
thresholds, constraints, state-dependent action quantities, shared-resource resolution
or nonlinear plant dynamics can make the finite-horizon endpoint map nonaffine. The
hypothesis of F3 then needs to be re-established; the pair-only conclusion cannot be
assumed merely because V remains quadratic. Some changes may remain affine over the
particular coalition table or cancel after valuation, so high-order interaction is
possible, never guaranteed by the word “nonlinear.”

Two analytic counterexamples make the boundary explicit, with dimensionless variables
and no physical registration claim:

* **Nonoscillatory high order:** fixed controls `a_i∈{0,1}` and
  `ẏ=a_1a_2a_3`, `y(0)=0`, `V(y)=y` give
  `E=−T_f a_1a_2a_3`. The trajectory is constant or monotone, while
  `m_{ABC}=−T_f≠0` for positive horizon. The controls combine nonadditively.
* **Nonlinear response without high order:** `ẏ=u/(2y)`, `y(0)=1`,
  `u=|\mathcal S|≥0`, has `y²=1+ut`. With `V(y)=y²/2`,
  `E_\mathcal S=−T_f|\mathcal S|/2`. The endpoint map is nonlinear in u,
  but valuation cancels that nonlinearity and all orders above one vanish.

S-MG also gives the gain-dependent example `ẏ=u y`, whose exponential flow is
nonadditive in coalition input even though the state equation is linear for each fixed
u. The correct diagnostic is the table of `V∘z(\mathcal S)`, not spectrum alone or a
syntax check for a nonlinear term. These examples are algebraic constructions, not
new scientific claims about an EBU installation.

## 18. Loss-aware force clarification

The historical stock note §5 explicitly uses the reduced state `(S,Q,X)` and the
separable potential `v_S(S)+v_Q(Q)+v_X(X)`. One unit of completion changes that
represented state by `(0,−1,η)`. With `μ_j=∂_jV`, the negative directional
derivative is indeed

\[
f_A=\mu_Q-\eta\mu_X.
\]

This is correct for that declared reduced potential. It is not automatically the
full-system derivative when loss is valued elsewhere. In the extended state
`(S,Q,X,W)`, one unit of completion with loss fraction `1−η` has increment

\[
s_A=(0,-1,\eta,1-\eta)^T.
\]

For a differentiable full potential, whether separable or not,

\[
\boxed{f_A=-\nabla V\cdot s_A
=\mu_Q-\eta\mu_X-(1-\eta)\mu_W.} \tag{12}
\]

The sign follows because the sink coordinate **increases**. The reduced expression
is complete when the extra term vanishes, including `η=1` or zero sink marginal.
Merely naming the sink does not justify ignoring its value; conversely, tracking a
coordinate does not force its potential marginal to be nonzero. For the audited
lossless oscillator `η=1`, the correction vanishes identically and changes none of
its balances, roots, memory or stability results.

Dispatch has direction `s_D=(−1,1,0,0)` and derivative `μ_S−μ_Q`.
A completed transfer has a different increment. The policy in §3 deliberately uses an
end-to-end shortage signal; it must not be described as the instantaneous dispatch
force. Native-potential derivatives have units B/U, normalized derivatives U⁻¹.
Neither is automatically a mechanical force in newtons, a flux, or a generator.
A physical response law, units and incidence mapping must be separately supplied.

## 19. Equilibrium / nonequilibrium boundary

The tank maintains dispatch, arrival and consumption `h>0`. It is a driven operating
model. Stability, a positive quadratic Lyapunov measure, damped oscillations and even
possession of a supplied potential do not establish a canonical equilibrium measure.
No noise law, invariant distribution, reference measure, reversibility, local detailed
balance, reservoir temperature or complete work/heat account was supplied here.

In particular, this reconciliation does **not** derive or transfer to the oscillator

\[
p\propto e^{-V},\qquad \beta_{\rm bridge}=1,\qquad
\Delta s_{\rm med}=k_BE,\qquad\Delta s_{\rm tot}=0.
\]

The R-stage and S-MG separate supplied-potential identities from canonical-density
algebra, and separate both from the full conditions behind E1a's P4 entropy relation.
Those conditions must be checked independently; a decreasing `𝓔_B` is not an entropy
proof. A receiver-only quadratic also does not by itself normalize a distribution over
an unrestricted pending coordinate.

Feedback mathematics is a useful bridge toward later driven and nonequilibrium work.
It does not solve the required stochastic dynamics, probability-current or physical
entropy-production programme. Conditional generator theory can be taught in the
introductory theorem chain; the more extensive coordination/memory programme retains
current Part VII ownership. No E1a authority, calibration, verdict, execution seal or
paused study is amended by this report.

## 20. Actor-registration boundary

Autonomous ring-down is physical evolution, not a fresh registered actor transaction.
If no new registered action occurs during relaxation, an actor's EBU balance does not
update merely because the state or potential changes. Historical entries remain
fixed; subsequent physical motion does not reprice them.

An already registered action may have a predeclared finite-horizon endpoint settlement;
that is evaluated under its own authorized semantics. It does not license continual
new credits while the system rings down. A later action is evaluated under the
then-current field/state and its declared comparison rules. Empty-baseline subtraction
and interaction decomposition supply neither actor attribution nor permissions,
entitlement, compensation or fairness rules. Those questions remain separate.

## 21. Transient/path/endpoint distinctions

For one fixed `C¹` potential and an absolutely continuous admissible path,

\[
E=V(z(0))-V(z(T_f))
=-\int_\Gamma\nabla V\cdot dz
=-\int_0^{T_f}\nabla V(z(t))^Tb(z(t),u(t))\,dt.
\]

The last integral integrates the **rate of potential change**, with a minus sign.
It is not generally the residence burden

\[
\int_0^{T_f}V(z(t))\,dt.
\]

The latter carries an additional time unit, and depends on how long the path remains
at each burden. Equal endpoints give equal finite EBU under a fixed field, while
transient peaks, accumulated burden, overshoot or total process costs can differ.
An oscillating trajectory may temporarily improve or worsen V before its endpoint.
Endpoint EBU alone does not report those intermediate extrema.

Settling time, overshoot, integrated error, stability margins and Lyapunov decrease
remain separate controller metrics. A future objective or path/action functional can
include them only after its units, boundaries, valuation and relation to existing
accounts are declared; they must not be silently added to endpoint EBU or counted twice.
If the potential itself changes with time, the chain rule also includes `∂_tV`;
one cannot reuse the fixed-field path identity without that qualification. The state
space path integral does not turn every traversed state into a ledger event.

## 22. Prior-art status

A focused primary-source check was sufficient; no broad novelty search was attempted.
The following sources were accessed on 2026-10-05:

| Primary source | Scope actually checked / relevance |
|---|---|
| Eduardo D. Sontag, [*Mathematical Control Theory*, second edition](https://www.sontaglab.org/FTPDIR/sontag_mathematical_control_theory_springer98.pdf), §2.7, equations (2.25)–(2.27), Lemmas 2.7.4 and 2.7.10, printed pp. 46–50 | Common linear state evolution and variation of constants establish the standard affine-input result. The realization formula `CΦ(t,s)B` and its time-invariant form support the state-space/convolution connection. |
| Karl J. Åström and Richard M. Murray, author-maintained [*Feedback Systems*: Linear Systems chapter page](https://www.fbswiki.org/wiki/index.php/Linear_Systems) | Matrix exponential and convolution are standard linear-systems tools. The author chapter page was read; attempted chapter-PDF requests timed out, so full PDF inspection is not claimed. |
| Feynman, Leighton and Sands, [*The Feynman Lectures on Physics*, I.24, §24-2](https://www.feynmanlectures.caltech.edu/I_24.html), equations (24.12)–(24.20) | Standard damped-oscillator roots and transient decay/frequency. The tank formulas follow by coefficient matching and the independent stock derivation above. |
| Feynman, Leighton and Sands, [*The Feynman Lectures on Physics*, II.32, §32-1](https://www.feynmanlectures.caltech.edu/II_32.html), equation (32.1) | Confirms the bounded optical Lorentz analogy, not an EBU constitutive law or a complete classical theory of atoms. |

The hidden-state elimination in §§10–11 is derived here directly with an integrating
factor; the affine endpoint result in §15 is the standard variation-of-constants
argument. The Möbius/quadratic degree bound is the already cleared S-MG result applied
to this endpoint map. References classify the mathematics; they supply no empirical
validation of the tank's dispatch or arrival law and no institutional authority.

**THE OSCILLATION CONDITION AND MEMORY-KERNEL DERIVATION ARE STANDARD
DYNAMICAL-SYSTEMS / CONTROL MATHEMATICS. NO NOVELTY CLAIM IS AUTHORISED.**

Any EBU contribution considered here is interpretation and integration with its declared
valuation, interaction and accounting framework, not invention of damped oscillators,
linear realization or superposition of linear-system responses.

## 23. Proposed Book 1 placement

The current eight-part map assigns coordination, memory and system dynamics to
**Part VII**, which corresponds to historical Part VIII. The book-series reconciliation
explicitly preserves the burden-to-damped-response section there. Historical
`VIII.15` and the identification cross-reference `VII.12` must be read in their
historical numbering; this report does not globally renumber those source files.

For the introductory “Book 1” theorem chain, follow the existing S-MG §31 proposal
and insert a compact conditional feedback example immediately **after the generator
interface**, before the broader discussion of nonlinear response and equilibrium:

```text
potential and sign
  → fixed-field path identity and sequential telescoping
  → comparable coalition endpoints and Möbius inversion
  → additive/quadratic bounds
  → generator / transition-map interface
  → declared feedback, oscillation and hidden-state memory
  → affine linear-feedback theorem and oscillatory pair-only example
  → nonlinear-response interaction and counterexamples
  → conditional equilibrium, probability and entropy bridges
  → nonequilibrium and registration boundaries
```

This order lets readers separate valuation from motion before encountering oscillation,
and proves the relation to Möbius interaction before moving to statistical/thermodynamic
interpretations. It preserves the current editorial plan: Part I introduces objects,
Part II develops rigorous mathematics/evidence, Part V deepens interactions, Part VII
owns advanced feedback/coordination, and Part VIII owns institutions. It is not a
proposal to move the whole advanced programme into the introduction or invent a new
approved chapter number.

A compact theorem hierarchy for later editing is:

| Local label | Result | Preconditions / place |
|---|---|---|
| F1 | Declared two-state stock/pipeline generator, equations (F1)/(3) | Lossless, fixed positive laws, maintained source, feasible smooth branch. |
| F1a | Characteristic roots and stability, (4) | Linear branch; physical `ν,τ>0`. |
| F1b | Exact complex-mode condition `4ντ>1` | Mode criterion, with separate excitation/observation caveat. |
| F1c | Decay `1/(2τ)` and frequency `√(4ντ−1)/(2τ)` | Underdamped regime. |
| F2 | Equivalent exponential memory reduction | Must retain `(q_0/τ)e^(−t/τ)` and any input convolution. |
| F3 | Affine coalition endpoints under common linear feedback | Common initial state/horizon, additive inputs, same admissible model. |
| F3a | Quadratic potential has at most pairwise interaction | Exact finite-horizon valuation; arbitrary number of modes. |
| F4 | Nonlinear endpoint boundary | High-order terms can appear but need not; evaluate the composed table. |

These are local exposition labels, not new scientific-authority stages or a renaming
of historical E1a F1–F8. Independent audit must precede Book 1 integration. No book
source, current structure document, chapter or manuscript was edited.

## 24. Required future experimental work

The inspected current SD-10 register says **BLOCKED on SD-06 and SD-07** and **needs a
benchmark**. Historical CLCD stages distinguish declarations and inert diagnostics
from separately authorized scientific execution. The reviewed fixtures and arithmetic
examples are not feedback-study outcomes. No completed SD-10/CLCD feedback-study result
or empirical validation of this oscillator was found in the inspected source/result
inventory. This is a scoped provenance finding, not a claim that no unrelated historical
EBU document ever mentions simulated oscillation. The task supplies no new empirical
evidence, and SD-10 remains unexecuted here.

Future work, if separately authorized, would need:

1. A named physical or controlled process, complete state/boundary and feasible operating
   region; distinguish a residence law from transport history and hidden source effects.
2. Justified dispatch and arrival mechanisms, measurement of dispatch/arrival where
   possible, noise and sampling treatment, and adequate excitation/observability.
3. A fixed native or canonical valuation, explicit units and any justified normalization;
   frequencies alone cannot choose a service band, burden scale or the separate `w,M`.
4. Registered hypotheses, comparators, parameters, outcomes, falsifiers and analysis,
   including whether endpoints or separate transient/path metrics are being tested.
5. Independent records for checking predictions and a separate authorization for any
   controller intervention or adaptation. Identification success alone does not establish
   stable control, lower total burden or legitimate actor settlement.
6. The applicable SD-10 dependencies, benchmark, implementation and explicit execution
   gate. This list neither adopts a design nor starts any of those stages.

| Category | Disposition |
|---|---|
| **MATHEMATICALLY SETTLED** | Conditional roots, regimes, memory identity, storage derivative, affine endpoint proof and quadratic degree bound; still subject to independent audit of this report. |
| **HISTORICAL DEFINITION** | Native B, endpoint-signal dispatch policy, residence compartment and the particular auxiliary quadratic. |
| **CURRENT AUTHORITY** | Normalized valuation, fixed-field and ledger boundaries, separately conditional physical/entropy interpretation; unchanged. |
| **BOOK CLARIFICATION** | Distinguish B from canonical EBU; include a valued sink in the derivative; distinguish lag, modes, interaction, stability and price. |
| **FUTURE MODEL CHOICE** | Physical system, policy information, hidden states, loss and arrival kinetics, admissible controls. |
| **EXPERIMENTAL CHOICE** | Excitation, observation, noise model, independent comparisons and registered test design. |
| **HUMAN SCIENTIFIC DECISION** | Adoption of a new physical model or missing normalization/valuation authority and later scientific gates, if pursued. No human choice is needed to decide the sign in (12) or the roots of the declared polynomial. |

## 25. Final disposition

### 25.1 Exact questions

| Question | Answer |
|---|---|
| **Q1. IS THE HISTORICAL TWO-STATE FEEDBACK MODEL MATHEMATICALLY CORRECT?** | **CONDITIONAL.** Yes for the declared affine, lossless, interior stock/pipeline model; not a universal constitutive law. |
| **Q2. ARE THE CHARACTERISTIC ROOTS CORRECT?** | **YES**, for `τ≠0`, with the physical domain stated. |
| **Q3. IS 4 nu tau > 1 THE EXACT OSCILLATORY-MODE CONDITION FOR THIS MODEL?** | **YES**, in the declared `ν>0,τ>0` model; visibility requires excitation. Outside that domain the same negative-discriminant test need not describe decay. |
| **Q4. IS THE SYSTEM ASYMPTOTICALLY STABLE FOR nu>0, tau>0?** | **YES** for the linear model; physical use is limited to its feasible invariant branch. |
| **Q5. IS THE REPORTED EXPONENTIAL MEMORY KERNEL CORRECT?** | **YES**, for this first-order hidden state, with the homogeneous term and any forcing retained. |
| **Q6. MUST AN INITIAL-CONDITION TERM BE RETAINED AFTER ELIMINATING PENDING STOCK?** | **YES**. It vanishes only under the corresponding declared initial condition. |
| **Q7. IS THE MODEL A TRUE PURE DELAY OR A FIRST-ORDER LAG / HIDDEN-STATE MEMORY MODEL?** | **FIRST-ORDER LAG / HIDDEN-STATE MEMORY MODEL.** |
| **Q8. IS THE HISTORICAL V ALREADY CANONICAL DIMENSIONLESS EBU?** | **UNDECLARED.** B is explicit; a canonical normalization bridge was not found. |
| **Q9. WHAT NORMALIZATION WOULD BE REQUIRED BEFORE A NATIVE BURDEN B IS CALLED EBU?** | An explicitly justified, fixed mapping to the canonical dimensionless potential with its reference scale and calibration; §4's affine formula is conditional, not a chosen scale. |
| **Q10. IS THE AUXILIARY STABILITY MEASURE THE SAME OBJECT AS FINITE EBU E?** | **NO.** It is a positive native-unit deviation/storage measure. |
| **Q11. DOES OSCILLATION IMPLY NONZERO MÖBIUS INTERACTION?** | **NO.** |
| **Q12. DOES NONZERO MÖBIUS INTERACTION IMPLY OSCILLATION?** | **NO.** |
| **Q13. WITH FIXED LINEAR FEEDBACK + ADDITIVE ACTION INPUTS, IS THE FINITE-HORIZON ENDPOINT MAP AFFINE IN COALITION INDICATORS?** | **YES**, under F3's common state, horizon, matrix, comparison and admissibility assumptions. |
| **Q14. UNDER THAT CONDITION AND QUADRATIC V, DO ALL MÖBIUS ORDERS >=3 VANISH?** | **YES**, exactly at each fixed horizon. |
| **Q15. CAN COALITION-DEPENDENT GAINS / SWITCHING / CONSTRAINTS CREATE HIGHER-ORDER INTERACTION THROUGH A NONLINEAR ENDPOINT MAP?** | **YES**, potentially; no guarantee for a particular table. |
| **Q16. DOES NONLINEAR FEEDBACK NECESSARILY CREATE HIGHER-ORDER INTERACTION?** | **NO.** |
| **Q17. IS f_A = mu_Q - eta mu_X COMPLETE WHEN A VALUED LOSS-SINK COORDINATE IS PRESENT?** | **NO in general**; completeness requires the extra contribution to vanish. The full expression includes `−(1−η)μ_sink`. |
| **Q18. IS THE LOSSLESS eta=1 OSCILLATOR AFFECTED BY THE SINK CORRECTION?** | **NO.** |
| **Q19. DOES ASYMPTOTIC STABILITY ESTABLISH CANONICAL EQUILIBRIUM?** | **NO.** |
| **Q20. DO E1a ENTROPY/P4 CLAIMS AUTOMATICALLY APPLY TO THE DRIVEN OSCILLATOR?** | **NO.** |
| **Q21. DOES AUTONOMOUS RING-DOWN CREATE ACTOR EBU TRANSACTIONS?** | **NO.** |
| **Q22. SHOULD FEEDBACK / OSCILLATION THEORY ENTER BOOK 1?** | **QUALIFIED:** the conditional theorem chain and example after independent audit, with advanced programme ownership retained in current VII. |
| **Q23. WHERE SHOULD IT ENTER RELATIVE TO THE S-MG GENERATOR INTERFACE?** | Immediately after that interface, before nonlinear-response interaction and the independently conditional equilibrium bridge; see §23. |
| **Q24. IS ANY SCIENTIFIC EXECUTION AUTHORISED BY THIS RECONCILIATION?** | **NO.** |
| **Q25. WHAT MUST BE INDEPENDENTLY AUDITED BEFORE BOOK 1 INTEGRATION?** | Provenance/authority status; model and domain; signs/units/normalization gap; roots/regimes and forcing; kernel/initial condition; stability-versus-valuation example; common-baseline F3 proof; all-coalition feasibility and zero-triple example; nonlinear counterexamples; full sink derivative; path/entropy/ledger boundaries; prior-art status; current book placement and execution nonclaims. |

### 25.2 Validation and change boundary

Source review included current authority and editorial records, historical Git objects,
static implementation/fixture inspection and the focused external primary sources in
§22. No historical module, model runner or test suite capable of advancing model state
was invoked. No scientific RNG, fitting, optimization, parameter search, integration,
time-sampled response, campaign or physical experiment was used.

A self-contained Python standard-library check performed **nine exact identity groups**
with rational arithmetic, formal Laurent polynomials and a symbolic trigonometric
basis. All nine completed; zero failed:

1. Characteristic determinant expansion and completing-square root certificate.
2. Storage cross-term cancellation and relative-burden identity.
3. Pending-aware countermodel polynomial factorization.
4. Conditional normalization invariance of `2wM`.
5. Historical individual-state arithmetic in §12.
6. Analytic step-response differential equation and initial conditions.
7. Pair/triple Möbius identities for arbitrary action amplitudes, including §16.
8. Full loss-sink directional sign.
9. Dimensional identities for rates, potential and storage.

For the only trigonometric check, represent a function by its coefficients in the
formal basis `(1,e^(−t/2)cos(√3t/2),e^(−t/2)sin(√3t/2)/√3)`. Differentiation is
the exact rational map `(a,b,c)↦(0,(−b+c)/2,(−3b−c)/2)`. Applying it twice to
`g=(1,−1,−1)` verifies `g̈+ġ+g=1` and the two initial conditions without evaluating
any positive time. The general proofs and feasibility inequalities are given in the
body; finite arithmetic checks do not substitute for them.

The report-only scope was checked against a before-write SHA-256 inventory of all
**2,901 pre-existing tracked files**. Every such file remained byte-identical. The
new report's structure, all 25 required question identifiers, math/code-fence balance,
named source paths, historical Git objects and protected identities were checked.
`git diff --check`, the
complete new-file diff, exact staged filename list and complete staged diff were
reviewed before the focused local commit. The final commit identity is reported to
the requester rather than embedded circularly in its own content.

Only `docs/theory/EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md` is added.
No source code, Book 1, book architecture, scientific authority, E1a contract, frozen
result or execution seal is changed. No existing commit is amended and nothing is
pushed. The next possible stage is independent audit of this report; Book 1 integration
and experimental work have not begun.

```text
FEEDBACK / OSCILLATION THEORY RECONCILIATION: COMPLETE
INDEPENDENT AUDIT: REQUIRED BEFORE BOOK 1 INTEGRATION
SD-10: NOT EXECUTED
BOOK 1: NOT MODIFIED
AUTHORITY MODIFIED: NO
CODE MODIFIED: NO
SCIENTIFIC RNG: NOT USED
MODEL TRAJECTORY: NOT RUN
OFFICIAL LONG-RUN CAMPAIGN: NOT RUN
REAL OPTICAL-TRAP EXPERIMENT: NOT RUN
EXECUTION AUTHORISED: FALSE
PUSH: NO
```
