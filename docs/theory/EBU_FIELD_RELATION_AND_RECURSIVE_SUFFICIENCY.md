# EBU — Field relation and recursive sufficiency theory

Date: 2026-10-07. Stage: theoretical research and scientific design.

**NON-CONTROLLING REPORT — PENDING INDEPENDENT AUDIT.** This document proposes
conditions and proves conditional results. It neither certifies actual source
fields nor changes the frozen foundation, experimental authority, or ledger
implementation.

## 1. Decision and the architecture it actually establishes

**A. RECURSIVE LOCAL-FIELD EBU IS MATHEMATICALLY COHERENT UNDER EXPLICIT CONDITIONS.**

The principle “history is accumulated in physical state, not replayed in price”
is valid for a restricted, physically specified class of systems. It is not a
theorem that an arbitrary small collection of present measurements summarizes
every physical history. Three separate requirements do the work:

1. **A common physical denomination:** independent calibration fixes the scale
   of the same kind of quantity throughout the admitted network.
2. **A compatible potential:** the joint system has one single-valued potential,
   including relevant interactions and boundary terms. Consistent units alone
   do not establish this property.
3. **A sufficient recursive state:** current state and the action determine the
   next-state/value law without hidden dependence on past actions. Physical
   memory must be retained where it matters.

With a well-posed local update, explicit physical boundaries, and an identified
registered-action transition, these conditions preserve

\[
E=V_{\mathrm{pre}}-V_{\mathrm{post}}.
\]

The proposed structure is **a rooted calibration network over a physical
factor/coupling hypergraph**, with a sufficient state and a separate historical
ledger. A calibration relation compares representations of a physical quantity;
a physical coupling changes physical states. These are different relations.
Neither relation carries a product's accumulated historical EBU price.

The report supplies exact composition and loop conditions, a recursive closure
theorem, counterexamples, quantified approximation bounds, an explicit
production-chain interface, and a nontrivial finite-community model. The latter
is a conditional physical model, not a certification of an actual village.

The E1a classification is **NECESSARY BUT INCOMPLETE** for the proposed
thermal-equilibrium root family. Its unit-slope prediction is a necessary local
consistency property of that particular root. The specific apparatus or
experiment is not logically necessary to every possible realization of EBU.
E1a does not establish the three requirements above for a general network.

No foundation amendment is required to make this restricted architecture
coherent. Universal environmental valuation, finite-dimensional closure of all
physical memory, and positive social consequences of every positive EBU remain
separate claims; none follows from the theorem.

## 2. Authority, provenance, and scope

| Item | Verified coordinate |
|---|---|
| Repository | `/Users/konrad.grzyb/code/ebu` |
| Branch | `codex/v6-minimal-recovery-assessment` |
| Starting commit | `d03de8e26c6f8f8d29aa73457c125132cc29816c` |
| Starting worktree | Clean |
| Cached `origin/main` | `660d6e5a56cb096fe6d1e4d202f592155d982c79` |
| Remote verification | No fetch; cached reference is not a claim about current server HEAD |
| Authorized output | This report alone, locally committed; no push |
| Report commit | Identified by the enclosing Git commit and completion response |

The authority order is the [frozen foundation](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md),
the [working baseline](EBU_THEORY_BASELINE.md), then non-controlling research
reports. Both controlling documents were read in full, in that order. The
foundation's historical freeze-candidate wording is resolved by its metadata
and the baseline's authority record; it is not an invitation to edit it.

The relevant results were reconstructed from the
[R-stage report](EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md),
[S-MG theorem](EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md), and
[S-stage anchor](EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md). The inherited independent
clearance of R/S-MG is recorded by the S-stage source. This report does not claim
to conduct another independent audit or promote the S-stage document to frozen
authority. The historical `docs/scientific_record/` archive is absent from this
checkout; no archive files were created or changed.

| Source | SHA-256 at starting commit |
|---|---|
| Frozen foundation | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Working baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| R-stage | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| S-MG | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| S-stage anchor | `5b92fdf5749ee05db63f32320e2b34a10afa2c98ceaf2e7a996f78b2df60505f` |

Inherited results used without a replacement proof for novelty are: fixed-field
endpoint valuation and telescoping; factor cancellation; the separate moving-
field term; S-MG's distinction between raw and no-action-centered values; its
conditional expected-value interface; and the scoped equilibrium bridge and
thermal denomination. The additional propositions below are elementary
calibration, integrability, and state-reduction arguments assembled for this
architecture. No claim of new general mathematics is made.

This task does not repair V6, reopen U apparatus selection, change T/U criteria,
or start a later experimental stage. Earlier experimental refusals are not
counterexamples to the conditional architecture proved here.

## 3. Abstract root denomination: what has to be fixed

### 3.1 A root is a physical quantity contract, not a chosen number

A root contract specifies:

- the **kind of physical quantity** being compared and its orientation;
- a reproducible realization of its unit, with independently determined inputs;
- the admissible state/transition domain, coordinates, reference measure where
  relevant, and boundary convention;
- calibration relations and their uncertainties, including shared systematic
  errors and validity conditions;
- at least one nonzero contrast, and domain-wide checks of the proposed scale;
- which changes preserve the same unit and which require a new scientific model.

Write its dimensionless potential coordinate as

\[
V_R(z)=\frac{Q_R(z)-Q_R(z_*)}{q_R},\qquad q_R>0.
\tag{1}
\]

Here `Q_R`, its physical meaning, and `q_R` must be independently specified;
`q_R` cannot be fitted merely to make EBU comparisons pass. Equation (1) is a
generic representation, not an assertion that all EBU is energy divided by a
universal energy constant. An intrinsically dimensionless physical quantity
can supply the root directly.

Two dimensionless numbers are not necessarily the same kind of quantity.
Efficiency, a logarithmic density ratio, and a normalized preference score
cannot be added merely because all have dimension one. The metrological
requirement is a common quantity and reference, not typography. The standard
notion of traceability is a documented calibration chain with uncertainty;
comparability concerns quantities of the same kind traceable to a common
reference. Traceability alone does not guarantee adequate uncertainty.
[JCGM VIM 2.41](https://jcgm.bipm.org/vim/en/2.41.html),
[JCGM VIM 2.46](https://jcgm.bipm.org/vim/en/2.46.html).

### 3.2 Gauge freedom and forbidden scale freedom

For a fixed context,

\[
V'(z)=V(z)+b\ \Longrightarrow\ E'=E,
\qquad
V'(z)=cV(z)+b\ \Longrightarrow\ E'=cE.
\tag{2}
\]

Thus a state-independent additive offset is harmless to endpoint differences.
A positive multiplicative conversion is allowed only when it is a determined
conversion from a raw instrument/quantity convention into the root unit. It is
not a free field-specific parameter. A negative conversion would also reverse
the physical orientation and is outside this contract.

If a field label `λ` stays fixed during an action, an offset `b(λ)` cancels.
If `λ` changes between endpoints, it need not cancel. To telescope across such
changes one must align those offsets in a common extended potential, or retain
the field-change term explicitly. An arbitrary state-dependent “zero” is a
change of valuation, not gauge freedom.

**Consequence for EBU:** the ruler can remain stable while stiffness,
temperature, resource levels, geometry, and other physical conditions change
the value of an action. Freezing action prices would suppress exactly the
physical information that a local field is meant to represent.

## 4. Criterion for an EBU-admissible source field

Use “certified” here as the name of a required scientific status, not a status
conferred on a real field by writing this report. A source-field contract is

\[
\mathcal C_i=(D_i,z_i,\lambda_i,V_i,\mathcal A_i,K_i,\mathcal R_i,
\mathcal P_i,\mathcal U_i).
\tag{3}
\]

The entries specify an operating domain, resolved physical state, context,
potential, admissible actions, update map/kernel, root calibration,
physical ports/interactions, and uncertainty description. Admission requires
all of the following.

| Requirement | Admission condition | Failure it prevents |
|---|---|---|
| Physical meaning | State variables and the potential's physical interpretation have an independent constitutive basis | Renaming an arbitrary score as a field |
| Observability | Required state and parameters can be determined, or bounded adequately for the declared valuation | Treating unobserved memory as absent |
| State function | A single-valued potential exists on the declared state domain; transitions use compatible endpoints | Path-dependent work silently called an endpoint potential |
| Root traceability | Its scale and sign follow the root contract through independently justified relations | Choosing a multiplier to obtain a desired EBU value |
| Domain | Valid states, actions, horizons, support, boundaries and error bounds are explicit | Uncontrolled extrapolation |
| Dynamics | Action and passive update maps are well posed and retain needed memory | Assuming a potential supplies a motion law |
| Local dependence | The affected factors/ports and any distant influences are specified | Omitting remote consequences by assertion |
| Composition | Shared factors, boundary terms and interaction potentials are compatible with a joint potential | Adding individually plausible but mutually inconsistent fields |
| Independence | Calibration evidence is not constructed from the same fitted value it is supposed to test | Defining `p ∝ exp(−V)` and calling this independent confirmation |

A bounded physical operating domain is the preferred certification contract.
Mathematical compactness is not compulsory: a noncompact domain can be admitted
with proved integrability, well-posedness and appropriate uniform or local error
control. Unbounded extrapolation without such controls cannot be admitted.

Being a Lyapunov function, having a minimum, being smooth, or correlating with
desirable outcomes does not suffice. Each property survives many arbitrary
changes of scale or shape. A physical measurement of some inputs also does not
make an arbitrary weighted combination of them a physical potential.

**A calibrated upstream source does not automatically certify downstream
fields.** Their constitutive relations, memory, joint potential and scale must
still be justified. A chain of physical causation is not, by itself, a chain of
metrological calibration.

## 5. Three relations that must not be conflated

### 5.1 Calibration relation: the same quantity in two representations

For two valid descriptions of the **same physical potential contrast**, a
calibration map has the form

\[
C_{ij}(v)=c_{ij}v+d_{ij},\qquad c_{ij}>0.
\tag{4}
\]

This is a transition between quantity coordinates, not between arbitrary
physical landscapes. The affine restriction expresses preservation of
differences up to a fixed unit conversion. A nonlinear sensor response may
first require a nonlinear measurement correction; its corrected physical
potential coordinate must then satisfy the common-unit relation.

Once both descriptions are in root units, a comparison of the same contrast
has slope one. This does **not** require a water field's function to equal a
trap field's function, nor does it require equal EBU for equal joules released
at different temperatures. Those are different physical comparisons.

### 5.2 Physical coupling: a state transition with ports

An admissible directed influence `G_{A→B}` is the B-component of a declared joint
update, for example

\[
z_B^+=G_{A\to B}(z_A,z_B,m_{AB},u_A,u_B,\xi_{AB}),
\tag{5}
\]

with compatible updates of A, the port/interface memory `m_AB`, and all affected
boundary states. `u` denotes physical controls; `ξ` denotes specified exogenous
inputs or resolved noise. It is generally not a function of A alone. The same
water inflow has a different effect on dry soil and saturated soil.

A relation states its carrier units, physical balances, constitutive response,
delay, support, operating domain, and uncertainty. It evaluates the new joint
state in the already calibrated potential. It does not multiply the recipient's
EBU denomination by an efficiency. An efficiency changes transferred energy or
material and therefore endpoints; it is not an exchange rate between EBU units.

### 5.3 Coarse-graining: retaining less state

A projection `π:z→θ` identifies several detailed states. It needs its own
sufficiency conditions (§8). Static minimization, averaging, or a Schur
complement does not establish those conditions. The baseline's quadratic
coarse-graining theorem is a static potential result. S-stage §12.3 also shows
why minimizing over hidden coordinates and integrating them out are generally
different operations. Neither operation automatically gives closed dynamics.

**Scientific benefit:** each relation can fail independently. An accurate pump
law cannot repair an arbitrary denomination; a perfect calibration cannot
repair a missing soil-memory coordinate; and both can hold while proposed
local potentials fail to assemble into a common potential.

## 6. Calibration composition and the no-drift theorem

### 6.1 Exact composition

From `v_j=c_ij v_i+d_ij` and `v_k=c_jk v_j+d_jk`,

\[
c_{ik}=c_{jk}c_{ij},\qquad
d_{ik}=c_{jk}d_{ij}+d_{jk}.
\tag{6}
\]

These equalities apply on an overlap where direct and composed maps represent
the same quantity at the same physical state/context. A comparison over
different temperatures or different physical states must first account for
those changes; it is not automatically a calibration-loop test.

For a path with consecutive maps `(c_1,d_1),…,(c_m,d_m)`,

\[
c_P=\prod_{r=1}^m c_r,
\qquad
d_P=\sum_{r=1}^m d_r\prod_{s=r+1}^m c_s.
\tag{7}
\]

Empty products equal one. A calibration loop returning to the same description
must satisfy

\[
c_P=1,\qquad d_P=0.
\tag{8}
\]

The first equation is the **no multiplicative denomination drift** condition.
The second is required to return absolute potential coordinates consistently.
If only endpoint differences within a chart are used, a constant offset around
a loop is invisible to those differences. It still obstructs a single globally
aligned potential across charts. The two requirements must not be confused.

### 6.2 Proposition 1 — Rooted calibration consistency

Assume a connected graph of invertible affine calibration maps, consistent
inverse maps, and domains on which all compared compositions are defined.
There is a path-independent affine calibration from a chosen root to every
node if and only if every closed comparison walk acts as the identity.
For difference scales alone, the corresponding necessary and sufficient
condition is `∏c=1` on every closed comparison walk.

**Proof.** If root-to-node maps are path independent, traverse any path and
return along another; its composition is the identity. Conversely, choose one
root-to-node path for each node. Any second choice differs by a closed walk;
identity of that walk makes both maps equal. Fixing the root fixes the scale.
The same proof using only slopes establishes the difference-scale statement.
For partial charts this assertion is restricted to their common comparison
domains; disconnected domains require separate compatibility information.

This is an algebraic consistency theorem, not a physical calibration theorem.
For example, freely choosing positive node multipliers `s_i` and setting
`c_ij=s_j/s_i` makes every scale loop close, even if the choices have no physical
basis. Independent root traceability in §§3–4 is therefore indispensable in
addition to the cocycle condition.

An illustrative raw-unit chain `c_AB=2`, `c_BC=3` requires `c_AC=6` and a return
factor `1/6`. A return factor `1/5` gives a loop factor `6/5`, contradicting a
single denomination. The numbers illustrate algebra only; they are not
proposed physical calibration constants.

### 6.3 Uncertainty does not disappear around a loop

For measured slopes, define `ℓ_e=ln c_e`. A loop discrepancy is
`r_P=Σ_e s_e ℓ_e`, with orientation signs `s_e`. Its variance is
`sᵀ Cov(ℓ) s`; shared calibration errors must remain in that covariance. A
nonzero resolved discrepancy refuses the claimed common calibration on that
domain. Projecting fitted coefficients onto a cycle-consistent graph is a
modeling operation, not independent proof that the original measurements agree.
This report creates no numerical acceptance threshold.

### 6.4 Physical routes have a different composition rule

For physical updates, composition is function composition on the full required
state, or composition of transition kernels. For deterministic maps,

\[
F_{AC}^{\rm sequential}=F_{BC}\circ F_{AB}.
\tag{9}
\]

A direct route need equal this map only if it is claimed to implement the same
physical protocol and endpoint. Two routes may have different loss, delay or
reservoir changes and therefore different endpoints. Their EBU values then may
differ without denomination drift. If their complete endpoints agree and use
one potential, their total endpoint values agree by the foundation's theorem.
An omitted transport buffer or bath state can create a false appearance of
equal endpoints.

For kernels the corresponding composition integrates over the retained
intermediate state: `K_AC(z,D)=∫K_BC(y,D)K_AB(z,dy)`. Discarding an interface
variable before this composition requires the sufficiency property of §8.
Simultaneous feedback must instead have a well-posed joint evolution or joint
constraint solution; arbitrary sequential traversal of its edges is not a
derivation of that solution. A physical loop returning to a field label need
not be the identity on physical states. Only a return to the same complete
state has the potential-cycle consequence in §14.2.

## 7. Common units are not enough: assembling the potential

### 7.1 Factor assembly

A useful representation on the joint state is

\[
\mathcal V(z)=\sum_{\alpha\in\mathcal F}
\phi_\alpha(z_{S_\alpha}).
\tag{10}
\]

Every factor has the common denomination and a physical interpretation within
the joint model. Each physical contribution appears once. Interactions may
involve more than two fields, so a hypergraph is more general than a pair graph.
This representation is a condition to justify, not permission to add any
individually calibrated scalars. A global potential need not be separable, and
a factorization need not be unique.

For instance, calibrated mechanical springs can supply a joint energy
`U=k₁x²/2+k₂y²/2+k_c(x−y)²/2`; division by a common fixed thermal scale gives
a physical coupled potential within that model. The coupling factor appears
once. Adding it independently to both node totals would double it. The
mechanical constants have physical units and calibration; they are not
arbitrary dimensionless social weights.

### 7.2 Proposition 2 — Integrability of local marginal relations

Suppose proposed smooth local marginal relations define a one-form
`ω=Σ_j μ_j(z) dz_j` on a connected open domain in Euclidean state space.
A single-valued `𝒱` satisfying
`d𝒱=ω` exists if and only if the integral of `ω` around every closed
piecewise-smooth comparison curve is zero. If `ω` is continuously
differentiable, cross-partial equality is a local necessary condition; on a
simply connected open domain it is sufficient. On a domain with holes, periods
around the holes must also vanish.

**Proof.** If `ω=d𝒱`, the fundamental theorem makes every closed integral zero.
Conversely, define `𝒱(z)` by integrating from a fixed base point. Zero closed
integrals make the result path independent, and local differentiation gives
`d𝒱=ω`. The local cross-partial statement follows from this exactness condition.

The discrete version uses an action comparison graph with value `r(z,z')`.
Include the formal reverse of each comparison with negative value, whether or
not reverse execution is physically possible. A potential with
`r(z,z')=𝒱(z)−𝒱(z')` exists exactly when every closed comparison walk has zero
sum. Define it by path sums to prove sufficiency. Checking executable directed
cycles alone is insufficient: an acyclic diamond can contain two inconsistent
routes between the same endpoints.

**Counterexample.** `μ_x=y`, `μ_y=0` uses one unit everywhere. Around the unit
square, in the order `(0,0)→(1,0)→(1,1)→(0,1)→(0,0)`, its integral is `−1`.
All calibration maps could be identity maps while no joint potential exists.
Thus calibration-loop consistency and physical potential integrability are
independent requirements.

**EBU consequence:** a network must pass both. Rejecting an incompatible
assembly preserves the foundation; silently settling its path-dependent
increments as though they came from one `V` would violate it.

## 8. State sufficiency: definition, theorem, and approximation

### 8.1 What the definition says

Let `h` be a physically possible history and `σ(h)=θ` a proposed current-state
summary. For deterministic actions, **one-step valuation sufficiency** means
that histories with the same `θ` admit the same physical actions and give the
same value for each of those actions. This is a definition; writing
`E(a;θ)` does not prove it.

**Recursive sufficiency** additionally requires that the next reduced state
depends only on `θ`, the action, and the specified new input. In a stochastic
system, require the joint conditional law

\[
\operatorname{Law}(E_n,\theta_{n+1}\mid h_n,a_n)
=K_{a_n}(\theta_n;dE,d\theta').
\tag{11}
\]

The joint law matters: separate reward and next-state marginals can lose
correlations relevant to subsequent records. Time, environmental inputs and
noise-memory variables must be included in state or in the explicitly
conditioned input. An unspecified `ξ` cannot conceal dependence on the past.

### 8.2 Proposition 3 — Exact recursive reduction

Let detailed state be `z`, reduced state `θ=π(z)`, and detailed deterministic
action transition `A_a`. Assume:

1. Physical action availability is constant on each fiber of `π`.
2. `π(A_a z)=\bar A_a(πz)` for every admitted action and state.
3. `𝒱(z)−𝒱(A_a z)=e_a(πz)` is constant on each fiber.
4. Passive/boundary updates also descend through `π`, with their physical
   inputs retained, and maps stay in the certified domain.

Then every finite sequence of admitted actions and passive updates has a
reduced recursive realization; every action value is obtained from its current
reduced state without the earlier action vector.

**Proof.** Condition 2 supplies the next reduced action state independently of
the representative detailed state. Condition 3 supplies its value. Condition 4
supplies the next pre-action state. Repeating this argument is induction over
the sequence length. Equal starting reduced states and equal new inputs give
equal reduced paths and values. No historical action list enters the induction.

For stochastic kernels, replace conditions 2–3 by equality of the joint
pushforward law of `(E,πz')` for all detailed states in a fiber, and impose the
corresponding passive condition. Successive conditioning gives the same
conclusion for the joint law of future reduced states and values under any
policy based on the retained state/observations. It does not force two
independent random realizations to have identical values.

The general subject is established state abstraction/bisimulation rather than
an EBU invention; see [Givan, Dean and Greig, *Equivalence notions and model
minimization in Markov decision processes*](https://www.sciencedirect.com/science/article/pii/S0004370202003764).
The proposition above states the particular endpoint-reward and passive-update
conditions needed here and supplies their proof.

### 8.3 A convenient stronger condition and its limit

If `𝒱(z)=v(πz)+constant` and transitions descend through `π`, then condition 3
holds immediately and

\[
e_a(\theta)=v(\theta)-v(\bar A_a\theta).
\tag{12}
\]

This is the preferred endpoint-preserving construction. It is stronger than
reward sufficiency: an omitted contribution can cancel for every action if
it is action-invariant. Such cancellation must be proved, including passive
updates and later actions. If only a reward reduction is available, a reduced
state potential is not automatic; its comparison graph must satisfy §7.2.

Keeping only the numerical value of `V` is generally insufficient. With
`V(x)=x²/2`, states `x=1` and `x=−1` have the same potential. The action
`x→x+1` gives `−3/2` and `+1/2`, respectively. A field is a state description,
not just its current scalar potential level.

### 8.4 Realized value versus a prediction

For a stochastic action,

\[
E_n=\mathcal V(\theta_n)-\mathcal V(A_{a_n}(\theta_n,\xi_n^a))
\tag{13}
\]

is a realized endpoint value. Before the new outcome is known, current state
determines its conditional distribution or, when integrable, its expectation.
The literal formula `E_n=ℰ(a_n;θ_n)` predicts a unique realized number only
for deterministic transitions, a deterministic value despite stochastic
endpoints, or an action record that already specifies its resolved outcome.
An expected quote is not silently substituted for realized settlement. This
preserves the S-MG §22 distinction.

### 8.5 Quantified approximate sufficiency

An approximate model must state its error and horizon. For example, suppose
`|𝒱(z)−v(πz)|≤ε_V` on the certified domain. Suppose a one-action reduced
endpoint differs from the true projected endpoint by at most `ε_A`, and `v`
is `L_V`-Lipschitz. With the exact initial reduced state,

\[
|E-\widehat E|\le 2\varepsilon_V+L_V\varepsilon_A.
\tag{14}
\]

This follows by adding and subtracting the true projected endpoint value and
using the triangle inequality. If the full reduced update has one-step state
defect at most `ε_F` and is `L_F`-Lipschitz, state error satisfies

\[
\delta_n\le L_F^n\delta_0+
\varepsilon_F\sum_{j=0}^{n-1}L_F^j.
\tag{15}
\]

For a directly certified approximate reward with uniform defect `ε_E` and
Lipschitz constant `L_E`, the step-value error is at most
`ε_E+L_E δ_n`. Summing these bounds gives a finite-horizon cumulative error
bound. The proof is the repeated triangle inequality, not a simulated result.
If `L_F≥1`, the bound need not remain small at long horizons. Stochastic
versions require a declared coupling or probability metric and corresponding
regularity; deterministic bounds are not automatically stochastic guarantees.

Measurement uncertainty, model-reduction error and calibration uncertainty
remain distinct. Correlated errors must not be reduced by pretending repeated
use of one calibration creates independent evidence.

## 9. Physical memory and the precise no-history claim

The minimum claim is **sufficiency for the declared action family and horizon**.
It does not require the state to predict every physically conceivable action.
The state may need inventories, spatial profiles, temperatures, concentration,
phase, accumulated damage, sorption states, organism age/cohort information,
transport buffers, reservoir levels, and controller state. Which entries are
necessary follows from the dynamics and valuation, not from a generic list.

For example, two pumps with the same visible water level but different wear
can consume different energy for the next identical withdrawal. A model using
water level alone fails. Adding a physically meaningful wear variable can
repair that particular omission if its update also closes. The past repairs
and operating hours need not be replayed if their relevant effects are fully
represented by the current wear state.

Projection can generate genuine memory. Consider a scalar memory term

\[
m(t)=\int_0^t K(t-s)u(s)\,ds.
\tag{16}
\]

If `K(t)=Σ_{r=1}^M b_r exp(−α_r t)`, retain `M` internal states satisfying
`\dot m_r=−α_r m_r+b_r u`; then `m=Σm_r` has an exact finite realization
with appropriate initial memory. For a generic kernel this construction does
not apply. A finite-dimensional time-invariant linear realization has transfer
function `C(sI−A)⁻¹B+D`, which is rational; a nonrational memory response
therefore has no exact realization in that class. An explicit transport delay
can require an entire in-transit profile rather than one inventory number.
The general appearance of memory after reducing physical variables is already
central to [Mori's generalized Langevin construction](https://academic.oup.com/ptp/article/33/3/423/1925580).

One may retain a function-valued current physical state. That avoids replaying
actor actions but does not establish a small finite data structure. Where no
adequate finite observable state exists, use a quantified approximation or
refuse the proposed finite-state certification. Encoding an arbitrary history
in the digits of one real number is not physical compression: it lacks the
required observability, regularity and finite-precision meaning.

Partial observation is another limit. A filtering distribution can sometimes
be updated recursively, but it can be infinite-dimensional and describes
knowledge of state, not the exact physical state. It does not entitle an
uncertain estimator to issue an exact physical valuation.

The theorem excludes the historical action vector from **current physical
valuation**. It does not erase settlement records, metrological provenance,
legal ownership, or causal responsibility records. These are different
information requirements. Physically identical apples may have different
owners or certification histories; no physical-state theorem reconstructs
those facts.

## 10. One bounded recursive architecture

### 10.1 State and two physical update channels

Let `Θ_n` be the certified network state immediately before a registered
action. It includes the needed local fields and interfaces. Let `a=∅` mean
that no registered action occurs. Use

\[
\widetilde\Theta_n=A_{a_n}(\Theta_n,\xi_n^a),\qquad
\Theta_{n+1}=P_{\Delta t_n,\xi_n^p}(\widetilde\Theta_n),
\tag{17}
\]

where `A_∅=identity`. `A` represents the identified action transition; `P`
represents passive evolution, explicit boundary fluxes, spatial propagation
and elapsed time. These maps may be joint network maps rather than independent
node updates. Correlated inputs and interface states must be retained.

Thus the requested form is

\[
\Theta_{n+1}=F(\Theta_n,a_n,\xi_n),\qquad F=P\circ A.
\tag{18}
\]

Only a registered action creates its actor entry:

\[
E_n=\mathcal V(\Theta_n)-\mathcal V(\widetilde\Theta_n),\qquad
B_{i,n+1}=B_{i,n}+E_n
\tag{19}
\]

for the registered actor `i`; all other balances are unchanged. If no action
is registered, every actor balance is unchanged even if `P` changes all fields.
Multi-actor actions need a declared allocation whose sum equals the joint
value; the physical theory does not choose the allocation.

### 10.2 The separation is an assumption to establish

Equations (17)–(19) give an exact construction for physically identified event
transitions separated from passive intervals. They do not establish that an
arbitrary continuous action/environment mixture can be split this way.
Noncommuting dynamics, simultaneous forcing, or hidden boundary work can make
such a split nonunique or only approximate.

The bounded architecture admits an action only when its endpoints and
accounting boundary are identified: either external context is held fixed for
that transition, or an independently justified extended potential includes the
action-induced field changes. Arbitrary offsets between changing field charts
cannot be used to manufacture an endpoint value. Mixed transitions without
identified attribution are outside this exact settlement construction.

In particular, the raw change over a no-action time interval can be nonzero.
It is a physical potential change, not an actor action value. Subtracting a
counterfactual passive trajectory would define S-MG's distinct relative
comparator; this report does not adopt that comparator as a replacement for
the controlling actor endpoint rule.

### 10.3 Explicit balance with passive evolution

Let `C_n=Σ_i B_i,n` and
`D_n=𝒱(\widetilde Θ_n)−𝒱(Θ_n+1)` be the passive potential drop. Then

\[
C_{n+1}-C_n=E_n,\qquad
\mathcal V(\Theta_{n+1})-\mathcal V(\Theta_n)=-E_n-D_n,
\tag{20}
\]

and hence

\[
\Delta(C+\mathcal V)=-D_n.
\tag{21}
\]

An auxiliary physical audit total accumulating `D_n` would make the extended
sum constant. It is not an actor balance or new actor issuance. With explicit
boundary or model-context events, include their potential changes in `D_n`
only when the extended potential is valid; otherwise report the comparison
as unavailable. These are accounting identities, not first-law conservation.

Every entry keeps its original value, physical context and calibration version.
A later state change affects a new entry. It does not retrospectively change
the earlier number. An institutional correction procedure, if ever needed,
is a separate matter and is not introduced here. If institutions restrict an
actor's permitted actions using balances, ownership or past conduct, those
rules use a separate institutional state. The sufficiency theorem concerns
physical action availability and valuation; it does not claim that physical
fields alone determine every legal or financial permission.

### 10.4 Proposition 4 — Recursive field closure

Assume a physically identified root and independent source traceability
(§§3–4), calibration consistency (§6), a compatible joint potential (§7),
recursive state sufficiency (§8), certified local/boundary update relations,
and the action/passive separation just specified. Require every transition to
remain in the admitted domain and every uncertainty claim to meet its declared
scope. Then equations (17)–(21) define a consistent recursive EBU system with
one denomination, field-dependent action values, no historical repricing and
no actor ledger change from passive evolution.

**Proof.** Proposition 1 fixes representation-independent units. Proposition 2
or an explicit joint potential fixes representation-independent endpoint
differences. Proposition 3 makes each current valuation and subsequent state
available recursively. Equation (19) uses only the current action endpoints;
equations (20)–(21) account separately for the remaining evolution. Historical
entries are absent from the arguments of `A`, `P` and `𝒱`. All required
properties follow. No assertion of physical realizability beyond the stated
contracts is used. Section 15 gives a conditional physical witness rather
than leaving this theorem as an empty set of assumptions.

## 11. Local fields, different action values, and spatial scope

Write the physical field state as `θ(x,t)` and the network state as its required
spatial collection plus discrete interface variables. A local action `a` need
only evaluate factors that change:

\[
E(a;\Theta)=\sum_{\alpha:\,\phi_\alpha\ \mathrm{changes}}
\left[\phi_\alpha(\Theta_{\rm pre})-
\phi_\alpha(\Theta_{\rm post})\right].
\tag{22}
\]

This is the foundation's factor-cancellation result. The needed neighborhood
is the support of those factors and of the endpoint response, not necessarily
one point or one administrative region. For finite-range interactions and a
bounded causal response, that neighborhood can be finite. A long-range
interaction, global constraint, or diffusive response may require a larger
field or a controlled truncation. If omitted factors satisfy
`Σ_omitted |Δφ_α|≤ε_local`, the valuation error is bounded by that sum.
Without such a bound, locality is not established by omitting them.

### Water withdrawal example

For water of density `ρ` in a vertical tank with constant cross-sectional area
`A`, volume `w`, bottom datum zero, its gravitational energy is

\[
U_w(w)=\frac{\rho g}{2A}w^2.
\tag{23}
\]

This follows by integrating `ρg z A dz` to depth `w/A`. Transferring volume
`q` from that tank into a receiver at fixed elevation `H`, above the initial
surface, raises the water's total gravitational energy by

\[
\Delta U_w=\rho g\left[Hq-\frac{wq-q^2/2}{A}\right]>0.
\tag{24}
\]

For the same `q`, a depleted tank has smaller `w` and therefore a greater
lifting requirement. If a physically specified pump has fixed efficiency
`0<η<1` on this domain, energy drawn from its source is `ΔU_w/η` and the
resolved heat loss is `L=(η⁻¹−1)ΔU_w`. In the finite-reservoir model of §15,
with the same initial bath energy `u` at both sites, the joint registered
transition has

\[
E=c\ln(1+L/u).
\tag{25}
\]

It differs between abundant and depleted sites with the same action volume,
same root unit, and same machine law. All the source/receiver/source-energy/
bath consequences are included. No field-specific normalization is introduced.
For an ideal lossless pump, the corresponding whole-system value in this
particular model is zero; the nonzero water-factor change alone would not be
the whole action value.

This example establishes state dependence, not a general scarcity or welfare
law. In this thermodynamic witness, greater dissipation produces a larger
positive potential drop. It would be scientifically wrong to claim from this
alone that wasting more energy benefits society. An ecological interpretation
needs its own justified potential and scope. A global average of water levels
would erase the actual local lifting difference and is not licensed here.

## 12. Field network and objects within it

### 12.1 The appropriate network

| Structure | Nodes / objects | Relation semantics | Required consistency |
|---|---|---|---|
| Calibration network | Root and quantity descriptions/standards | Same-quantity comparison and conversion | Path-independent root scale; affine cocycle on shared domains |
| State/factor hypergraph | Certified state components and joint potential factors | Which variables enter each contribution | One compatible potential; no duplicated factor |
| Physical coupling network | Fields, interfaces, reservoirs and boundary ports | Transport, transduction, reaction, delay and response | Well-posed joint update and physical carrier balances |
| Actor/registration layer | Actors and registered events | Who receives the settled entry | No event duplication; allocations close to joint E |

A “source” may mean a metrological reference or a source of material/energy.
The first establishes a ruler; the second supplies a physical flux. A root
calibration node need not supply any physical energy to the community.

Every sink is either represented by a valued physical state or declared as a
boundary/audit-only destination. It cannot silently disappear. Carrier
conservation applies separately to each conserved quantity in appropriate
units. Kilograms, joules and EBU are not interchangeable conserved carriers.
Open boundary inflows/outflows prevent a claim of isolation.

### 12.2 Do goods need their own fundamental potential?

**NO — an independent fundamental `V` for each product category is not
required.** An apple, chair, phone or house can participate in actions whose
physical consequences are evaluated through existing certified fields and
joint factors. The mathematics requires enough state to determine those
consequences; it does not require a universal apple-price function.

This answer has a substantive condition: goods may carry physically necessary
state. Composition, temperature, location, degradation, structural condition,
or stored energy may need representation. Interactions involving a product
may require new physically justified factors. Saying “the apple has no separate
fundamental potential” does not license omitting its relevant condition or
effects.

An ownership-only transfer with identical physical endpoints has `E=0` under
the controlling rule. Storage, cooling, repair, transport or consumption can
change physical state and have nonzero value. A shop's commercial payment,
markup or profit is not derived merely by applying this physical endpoint rule.
The architecture is therefore a physical accounting framework; an entire
institutional economy does not follow from the no-product-potential result.

## 13. Production chain without replaying upstream prices

### 13.1 Current state and a port-resolved chain

Consider

```text
primary source → energy → pumping → irrigation → orchard → apple → shop
```

Use current state
`Θ=(r,e,w,s,o,p,c,m,b,λ,t)`, where `r` is the source reservoir, `e` usable
energy/storage state, `w` water levels/profiles, `s` soil condition, `o` orchard
condition/cohorts, `p` fruit state/inventory, `c` shop/storage state, `m` transit
and other memory, and `b` physical boundary reservoirs/flux descriptors. These
are classes of physical variables, not a claim that one scalar per class
suffices.

For each registered stage `j`, set `\widetilde Θ_j=A_j(Θ_j)` and
`E_j=𝒱(Θ_j)−𝒱(\widetilde Θ_j)`, followed by the actual passive update to
`Θ_j+1`. Stochastic endpoints use §8.4. The following are interfaces a certified
model must supply, not newly certified agricultural laws.

| Stage and registered action | Explicit recursive state change | Required physical relation / memory |
|---|---|---|
| Source capture or conversion | `r'=r−q_r`; `e'=e+Q_e`; update losses/emissions in `b` | Constitutive map from source extraction to energy and each residue; depletion and source state |
| Energy delivery | `e_source'=e_source−Q`; `e_pump'=e_pump+η_e Q`; heat port receives `(1−η_e)Q` where this efficiency model applies | Energy balance, storage state, delivery delay and state-dependent efficiency |
| Pumping | `w_source'=w_source−q`; `w_delivery'=w_delivery+q`; `e'=e−W(q,w,m)`; update heat and wear | Actual lift, pressure, pump condition, leakage and transported-water state |
| Irrigation | `w_delivery'=w_delivery−q`; `s'=I(s,q,m,λ)`; runoff/drainage/evaporation go to specified ports | Soil profile, infiltration capacity, chemical inputs, delayed drainage |
| Orchard intervention | `o'=O(o,s,a_orchard,m,λ)`; update soil and material/energy ports | Water stress, disease/damage, phenology, soil interaction and any relevant age structure |
| Harvest and handling | Move the physically harvested fruit from `o` to `p`; update plant condition, machinery energy and residues | No creation of a second copy of the same biomass; current fruit composition/condition |
| Delivery to shop | Move `p` between locations; update transit, cooling, transport energy and storage environment | Temperature exposure embodied in relevant degradation state; location and inventory conservation |
| Shop action | `c',p',e',b',m'=S(c,p,e,b,m,a_shop,λ)` | Current storage, handling, refrigeration or other physical consequence of this action |

The shorthand state equations must be expanded to homogeneous carrier balances
for each material/energy stream. For example, an irradiation-driven orchard
requires light/energy, water, carbon and nutrient inputs and heat/gas/residue
outputs; water alone does not specify photosynthesis. Coefficients such as
`η_e` and response maps are admissible only on independently justified domains.

Sunlight arrival, rainfall, ripening, evaporation and natural deterioration
are passive or external updates unless there is an identified registered
intervention. Natural apple growth is not automatically an actor transaction.
Registering an irrigation event does not automatically make every subsequent
day of growth another credit to that actor.

### 13.2 The shop-stage result

Under Proposition 3, two histories that arrive at the same sufficient current
shop neighborhood, relevant interfaces and boundary conditions produce the
same law of value for the same shop action:

\[
E_{\rm shop}=\mathcal V(\Theta_{\rm current})-
\mathcal V(A_{\rm shop}\Theta_{\rm current}).
\tag{26}
\]

The earlier values `E_source,…,E_delivery` are not arguments. Their persistent
physical consequences are already in the current state. Unchanged remote
factors cancel; a genuinely coupled remote consequence still has to be included
or bounded. Historical invoices are neither physical state variables nor a
replacement for the response law.

### 13.3 What cannot simply be compressed away

A single fruit count does not determine spoilage, cultivar, composition or
thermal damage. A single soil-water number may not determine its depth profile
or future drainage. A delivery total may not determine goods still in transit.
If these features affect the next action, the proposed state is insufficient.
Their exact required representation can be large or function-valued.

Attribution of an old pollutant to a particular past actor cannot generally be
recovered from its present concentration. Legal ownership, provenance promises
and liability are also not consequences of the physical-state reduction. If
the programme wants those claims, it must retain suitable separate records.
This does not require replaying historical prices to value a new physical action.

**Disposition of the complete apple chain:** conditional recursive closure is
proved if all its contracts hold; actual root-traceable orchard, degradation
and ecological potentials are not supplied by the controlling E1a sources.
Consequently this report does not certify the whole real chain. That is a
specific missing physical admission, not a contradiction of recursive accounting.

## 14. Double counting, fixed historical entries, and external entry

### 14.1 Proposition 5 — Incremental accounting avoids inherited recharges

For a sequence of actual adjacent action endpoints under one potential and
without intervening passive changes,

\[
\sum_{n=0}^{N-1}
[\mathcal V(\Theta_n)-\mathcal V(\Theta_{n+1})]
=\mathcal V(\Theta_0)-\mathcal V(\Theta_N).
\tag{27}
\]

This is the already-cleared telescoping theorem. With passive intervals,

\[
\sum_n E_n+\sum_n D_n
=\mathcal V(\Theta_0)-\mathcal V(\Theta_N).
\tag{28}
\]

Persistent effects do not get charged again merely because they are still
present. An unchanged factor contributes zero to the next difference. When an
existing condition changes the response or marginal value of a new action,
that changed **increment** belongs to the new transition. It is not another
charge for the entire old state.

The sufficient bookkeeping conditions are: actual updated endpoints; one
representation of each physical contribution; no duplicate registrations of
one transition; separate passive changes; and a single closing joint value for
overlapping/simultaneous actions. A fixed-baseline valuation of every action
generally fails these conditions. S-MG's joint coalition table can describe
simultaneous interactions; summing its singleton values need not equal its
joint value, and no extra EBU is created by separately listing interaction terms.

Example: for `V=x²/2`, two successive increments `0→1→2` have values `−1/2`
and `−3/2`, totaling `−2`. Two stale-baseline singleton values would total
`−1`, missing the interaction. Adding a historical charge again at the second
stage would be a different error. Correct rebasing handles both without a
historical price vector.

A pollutant remaining unchanged in a downstream state is not a new charge.
A later registered cleanup changes the physical state and may legitimately
receive its own endpoint value. If unassisted pollution later spreads, that
changes the field without automatically altering the polluter's historical
entry. Comprehensive retrospective causal liability is an additional policy,
not a result of this ledger rule.

### 14.2 Three loops with different meanings

| Loop | Exact statement | What does not follow |
|---|---|---|
| Calibration loop | Same quantity returns with slope one; offset zero for aligned levels | No physical dynamics is implied |
| Complete-state potential loop | Sum of all endpoint potential changes is zero | Actor sums alone need not be zero when passive steps intervene |
| Isolated physical carrier loop | Each conserved carrier satisfies its physical balance, with every reservoir included | EBU is not thereby a conserved material or energy carrier |

For a closed full-state path with passive segments, equation (28) gives
`ΣE=−ΣD`, not necessarily `ΣE=0`. An individual actor can also have a nonzero
sum even when all registered actions jointly sum to zero. The foundation
already separates actor history from current physical state. Omitting a bath,
source depletion or export may make a physically open path look closed.

### 14.3 External resources and products

An external product cannot receive a root-linked value for its unknown upstream
history merely by entering the network. There are three precise cases:

1. **Full admitted boundary transition:** its current state and all affected
   fields are adequately characterized, its boundary relation is root-traceable,
   and the endpoint transition is within the potential's domain. Value that
   registered transition; no historical action replay is required.
2. **Known internal consequence only:** an internal handling/cooling transition
   has a certified value but upstream or other consequences are outside the
   boundary. Report the bounded internal claim and its boundary; do not call
   it the product's complete embodied value.
3. **Unresolved required contribution:** refuse a numerical total. If scientific
   information restricts admissible completions to a set `U`, report the set
   or interval of possible endpoint values. A one-sided bound may support a
   separately declared conservative policy, but zero is not a scientifically
   neutral replacement for an unknown signed contribution.

For an interval to be meaningful, extrema or valid bounds over `U` must be
established and the set must cover the physically possible completions. A
default chosen for convenience is not a calibration. Conversely, lack of an
upstream invoice alone is not a reason to refuse a fully observed current
physical transition: the architecture expressly avoids price-history replay.

## 15. A minimal finite-community witness

### 15.1 Why a finite bath is useful here

To demonstrate closure without an unmentioned infinite reservoir, consider an
idealized village utility consisting of two water stores, a finite mechanical
energy source, a pump, and a finite thermal reservoir. Material and energy
boundaries are known. This is a conceptual physical model, not an optical
apparatus proposal, certification of actual equipment, or a social experiment.

Let water volumes be `w_A,w_B`, with fixed `w_A+w_B=W`. Let
`U_w(w_A,w_B)` be their calibrated gravitational energy, obtained by expressions
such as (23), with receiver elevations included. Let `e` be energy in a
calibrated raised weight or other explicitly modeled mechanical store. All
settled endpoints have no unaccounted kinetic energy. Let total isolated energy
be `E_tot` and bath energy be

\[
u=E_{\rm tot}-e-U_w(w_A,w_B)>0.
\tag{29}
\]

Choose an ideal bath with independently specified microcanonical state count
on the relevant energy shell

\[
\Omega_b(u)=C(u/u_0)^c,\qquad c>0.
\tag{30}
\]

Here the exponent `c` comes from the bath's physical density of states; it is
not a tunable EBU weight. For example, a bath energy that is a positive
quadratic form in `f>2` resolved microscopic coordinates has enclosed phase
volume proportional to `u^(f/2)` and shell density proportional to
`u^(f/2−1)`, fixing `c=f/2−1` in that shell convention. This follows by rescaling
the ellipsoidal energy ball and differentiating its volume. It establishes a
possible density of states, not a memoryless heat-transfer law.
Energy-shell convention, coordinate measure inherited from the specified
physical phase volume, and any configurational degeneracy are fixed in
advance; a freely chosen state-dependent reweighting is excluded. Assume the remaining
constrained configurational factor is constant in those coordinates. This is
the same type of restricted assumption identified in S-stage §13.3.

The constrained bath entropy and compatible joint potential are then

\[
S_b=k_B\ln\Omega_b,\qquad
\mathcal V=-\ln\Omega_b(u)+\mathrm{constant}
=-c\ln(u/u_0)+\mathrm{constant}.
\tag{31}
\]

The potential is a log of an independently specified physical multiplicity,
not a probability manufactured from an arbitrary chosen score. One unit is a
natural-log unit of the constrained weight, equivalently a constrained bath
entropy change of `k_B` under this model. Its canonical small-excursion limit
connects to the thermal denomination, as shown below. This is a conditional
extension example, not promotion of a new potential into authority.

### 15.2 Certified relations within the ideal model

The state can be `(w_A,w_B,e,u)` subject to the two constraints, with pump mode
and any needed control state included. All actuator/control work is included
in the draw from `e`; no unrecorded external work is allowed in the isolated
example. Choose a bounded operating domain with
strictly positive bath energy, finite storage, and a calibrated pump law.
For a registered transfer of water volume `q` from A to B, define

\[
\begin{aligned}
w_A'&=w_A-q,& w_B'&=w_B+q,\\
\Delta U_w&=U_w(w_A',w_B')-U_w(w_A,w_B),\\
e'&=e-\Delta U_w-L,& u'&=u+L,
\end{aligned}
\tag{32}
\]

where `L≥0` is the independently specified dissipative loss for that operation
and all endpoints must remain in the operating domain. For a pumping operation
with `ΔU_w>0`, a fixed-efficiency idealization gives
`L=(η⁻¹−1)ΔU_w`; more general state-dependent laws require their own contract.
Carrier balances are explicit:

\[
\Delta(w_A+w_B)=0,\qquad \Delta(e+U_w+u)=0.
\tag{33}
\]

The action's EBU value is nevertheless generally nonzero:

\[
E=\mathcal V_{\rm pre}-\mathcal V_{\rm post}
=c\ln\frac{u+L}{u}.
\tag{34}
\]

The physical update and value depend on current volumes, stored energy, bath
energy and the current pump law, not on the list of past pumping actions. The
state has finite dimension in this stipulated ideal model. This requires the
additional constitutive assumption that the stated endpoint loss law closes
on these variables: a bath density of states alone does not prove it. A finite
Hamiltonian bath can retain microscopic memory, so no exact microscopic
Markov reduction is inferred from equation (30). The witness is exact inside
the specified macroscopic endpoint model; real hydraulic or thermal memory
would require additional state or a quantified reduction before admission.

The temperature follows from the specified bath:
`1/T=∂S_b/∂u=c k_B/u`. Thus for small `L/u`,

\[
E=c\ln(1+L/u)=\frac{L}{k_BT}+O\big(c(L/u)^2\big).
\tag{35}
\]

The exact logarithm, not the leading thermal approximation, is used for the
finite example. A changing bath temperature changes the physical action value
while the natural-log denomination stays fixed. Summing separate bare
mechanical energies divided by different local temperatures would not recover
this joint potential and is not substituted for it.

### 15.3 Passive evolution and closure

A passive release of mechanical stored energy `ℓ≥0` into the bath updates
`e'=e−ℓ`, `u'=u+ℓ` without any actor entry. The next registered pump action is
priced with the new `u`. If the mechanism has delays or uncontrolled kinetic
energy, those must be included before this simplified update is exact.

The community's known primary source is its finite mechanical store; it is
not replenished for free. The heat destination is a represented finite bath.
The water boundary is closed. A physically complete return to the original
state would require restoring source energy and bath state as well as water
levels. Returning the water alone is not a closed loop. The total potential
change over a genuinely closed extended-state loop is zero; the physical
energy balance (33) is a separate statement.

This witnesses mathematical closure of a finite, restricted physical network.
It also exposes the limit of the social interpretation: the chosen potential
rewards entropy increase of its constrained bath when an action is registered.
It does not prove that this is a desirable payment rule, an ecological burden
measure, or an incentive for energy efficiency. A different physically justified
application potential would require its own admission. Mathematical coherence
and a socially useful choice of physical quantity are different questions.

Adding a real orchard, apples and shop to this finite model is allowed only
after their missing contracts in §13 are supplied. The report does not label
that larger network certified by analogy with pumps and water stores.

## 16. E1a assessed after the abstract requirements

### 16.1 What the established anchor actually gives

Within the S-stage canonical assumptions,

\[
V_\lambda(x)=\frac{U_\lambda(x)-U_\lambda(x_*)}{k_BT_\lambda},\qquad
J_\lambda=-\ln p_\lambda=V_\lambda+C_\lambda,
\qquad \beta_{\rm bridge}=1.
\tag{36}
\]

`U`, positive temperature, support, ensemble and reference measure must refer
to the same independently justified physical system. The bridge identifies
its slope only if `V` varies. A nonconstant density-of-states factor or a
coordinate Jacobian cannot be absorbed into a constant. The sign is
`J_post−J_pre=−E`, as corrected in R/S; the baseline's historical contrary
sign is not propagated here.

This establishes a dimensionless thermal/log-density denomination for that
field family. At fixed temperature a positive unit equals a decrease of
mechanical energy by `k_BT` in the scoped conversion. It is not a universal
temperature-independent energy unit `k_BT_ref`. The density ratio is an
endpoint configuration-density ratio in one declared measure, not a
transition probability.

Under the additional P4 assumptions, `Δs_med=+k_BE`, `Δs_sys=−k_BE`, and
`Δs_tot=0`. Those identities are not extended to arbitrary controlled actions,
hidden work, mixed baths or nonstationary ensembles. Canonical density alone
does not prove reversible dynamics or a sufficient reduced state.

### 16.2 Required properties versus supplied properties

| Required root/network property | E1a thermal anchor supplies it? |
|---|---|
| Physically meaningful, independently calibrated local scale | Yes conditionally, through the independently determined thermal mechanical potential and density comparison |
| Non-arbitrary multiplier | Unit slope is the canonical prediction; a freely fitted rescaling is not allowed |
| Stable unit with field-dependent values | Yes within the valid canonical family |
| Realized calibration across actual fields with adequate uncertainty | An experimental question; the conditional theorem is not a completed measurement |
| Same-kind interpretation for new biological/ecological/source fields | No |
| Certified transport/coupling and interaction potentials | No |
| Global potential compatibility and calibration-loop closure of a network | No |
| Finite sufficient memory state and local response closure | No |
| Actor/passive separation, attribution and institutional desirability | No |

### 16.3 Single classification

**E1a tests a necessary but incomplete root property.**

“Necessary” is conditional on using the proposed canonical thermal family as
the root: if independently determined thermal potential and the correctly
specified canonical density require incompatible non-unit slopes, that root
realization fails its defining scale relation. “Incomplete” means that a
successful local comparison still does not establish transportable same-kind
calibration, compatible joint potentials, or recursive state sufficiency.

The mathematical closure theorem does not assume equilibrium or
`β_bridge=1`. Its load-bearing requirement is a non-arbitrary common physical
scale. E1a is one scoped route to testing such a scale, not the unique possible
experiment and not a logical prerequisite for every alternative root. This
qualification prevents turning the classification into a claim that the
current optical apparatus must succeed for EBU mathematics to be coherent.

The additional property most directly missing from a standalone E1a anchor is
**transportability to an admitted class of other physical quantities/states
through independently justified, path-consistent calibration relations**.
Joint-potential and sufficient-state certification then remain separate
network requirements. One may not use the word “root” to infer all three.

## 17. Falsification and the level at which a failure lands

| Failure observation or mathematical counterexample | What it defeats | What it does not automatically defeat |
|---|---|---|
| Claimed endpoint values have nonzero sum on a closed complete-state comparison loop under one fixed potential | That claim to implement the potential foundation, or its asserted state completeness | The algebraic identity for an actual single-valued potential |
| Every available candidate root retains an arbitrary multiplier with no independent physical identification | Physical realization of the proposed rooted architecture, until a root is supplied | Conditional endpoint mathematics |
| Two asserted same-quantity calibrations require incompatible root scales or resolved nonidentity loop slope | That source/calibration network; if unavoidable for the required class, its common-denomination architecture | All other possible restricted source classes |
| Same apparent state and same action give history-dependent values or future-state laws beyond declared uncertainty | The proposed state summary and its exact recursive certificate | An enlarged sufficient state, if one exists |
| No finite observable state or controlled finite approximation can support the required actions/horizon | A finite-state implementation for that domain; potentially the universal finite-state ambition | A restricted domain or a function-valued physical state |
| Local marginals fail integrability despite consistent units | Proposed joint potential/network assembly | Denomination traceability by itself |
| Required distant effects have no justified local representation or bounded truncation | The claimed local valuation for that action | A larger-domain valuation |
| An alleged closed loop omits bath changes, source depletion, export or a changed context | The asserted physical boundary/completeness | Potential telescoping on a genuinely complete loop |
| Double counting remains unavoidable after event/factor identity and sufficient state are fully specified | The proposed composition/registration architecture; revise or refuse it | A ledger whose events and factors satisfy §14 |
| A source's constitutive law, calibration or memory model fails | That source contract | The entire foundation or a different source |
| Actual apparatus cannot meet its uncertainty requirements | That apparatus realization or design | The canonical conditional theorem or the abstract recursive theorem |
| A coherent thermal ledger rewards a socially undesirable dissipative operation | A claim that this root alone guarantees welfare/efficiency | Mathematical consistency of its signed endpoint accounting |

The first row is not a way to empirically falsify the telescoping identity.
It tests whether the asserted physical model, boundaries and values actually
satisfy its hypotheses. A universal claim can be defeated by one required
unadmittable domain even though a small certified community remains coherent.

The minimal observable state may be found by asking which histories are
indistinguishable under **all admissible future interventions**. This defines
an equivalence relation, but it does not prove that the quotient has finite
dimension, can be measured, or is locally accessible. Those are substantive
failure conditions rather than formalities to hide in notation.

## 18. Bounded outcome, checks, and independent-audit handoff

### 18.1 One architecture, with its exact conditions

The recommendation is one restricted architecture:

```text
one physically identified root quantity and unit
→ admissible source contracts
→ root-consistent calibration maps
  + jointly compatible physical coupling/potential factors
→ sufficient current local/interface/boundary state
→ identified registered action endpoint transition
→ root-calibrated endpoint EBU entry
→ separate passive/boundary update
→ next current-state action valuation
```

Admission is conditional on **same-kind traceability, calibration composition,
one compatible potential, recursive sufficiency, adequate spatial/boundary
coverage, well-posed domain-preserving updates, and identified event accounting**.
These conditions cannot be replaced by “everything is connected.” Failure of
one condition refuses that proposed admission; it does not authorize an
arbitrary conversion, hidden history variable, or modified foundation.

For EBU, this structure can make current physical accounting efficient: only
affected factors need evaluation and earlier actions need not be recomputed.
It can preserve local differences, make the unit auditable, and avoid repeated
charges for an unchanged inherited condition. Those are direct mathematical
and information-processing benefits. Social welfare, fair allocation, actor
incentives and the ecological usefulness of a selected potential require
additional claims; the thermal witness shows why they cannot be inferred from
coherence alone.

### 18.2 Request coverage

| Brief item | Resolution |
|---|---|
| Root denomination and gauge | §§3, 6, 16 |
| Source-field admission | §4 |
| State sufficiency and no historical action vector | §§8–9 |
| Recursive update and passive evolution | §10 |
| Relations, units, composition and loops | §§5–7, 14.2 |
| Locality and water example | §11 |
| Field network and actor distinction | §12.1 |
| Goods and fundamental potentials | §12.2 |
| Source-to-shop chain | §13 |
| Double counting and historical ledgers | §§10, 14 |
| External entry | §14.3 |
| Finite community | §15 |
| E1a relevance after abstract theory | §16 |
| Falsification levels | §17 |
| Primary decision | A, §1 and §18.1 |

### 18.3 Validation performed and scope preserved

Validation is limited to source inspection, proof checking, exact illustrative
algebra/arithmetic, link/path and document checks, source hashes, and Git diff
review. No runner, trajectory, parameter search, Monte Carlo, confirmatory seed,
physical execution, apparatus design, or experimental implementation is part of
this work. Exact arithmetic checks cover affine composition, its loop failure,
the factor/rebasing example, and the finite-community carrier identities.

The report is the sole authorized changed file. The five source hashes in §2
provide the controlling/research-source comparison record. The completion
response records the report commit and final working-tree status; the report
does not embed its own circular commit hash.

Independent audit is the next possible stage, **not begun here**. Its sharpest
targets are: the distinction between scale cocycles and potential integrability;
the joint-law requirement for stochastic reduction; the treatment of mixed
action/passive intervals; the finite-bath witness and its constrained measure;
and the conditional meaning of E1a's necessity. No independent clearance is
claimed by this authorial synthesis.

```text
AUTHORITY MODIFIED: NO
EXPERIMENTAL DESIGN MODIFIED: NO
CODE MODIFIED: NO
MONTE CARLO: NO
PHYSICAL EXECUTION: NO
PUSH: NO

EBU RECURSIVE FIELD THEORY:
COHERENT UNDER EXPLICIT CONDITIONS
```
