# EBU — Unified marginal-vector, directional-action and field semantics

Date: 2026-10-07. Scope: theory reconstruction and mathematical semantics.

```text
STATUS: NON-CONTROLLING THEORY RECONSTRUCTION
AUDIT STATUS: PENDING INDEPENDENT AUDIT
PRIMARY CONCLUSION: A
FOUNDATION IMPACT: NO FOUNDATION CHANGE REQUIRED
GLOBAL SF / TA / BT CHOICE: NOT REQUIRED
SIGN POLICY SELECTED: NONE
```

## 1. Result

**EBU already values a complete physical response through one joint potential.**
At a differentiable state, the potential's marginal components and an action's
state-direction components pair to give one scalar slope. For a finite action,
the controlling value is the complete potential drop between its endpoints.
Neither construction requires first assigning components to sources or choosing
SF, TA or BT.

The hierarchy is

\[
\text{complete current state }z\ \longmapsto\ V(z),\ dV_z,
\qquad (dV_z,s_a)\longmapsto f_a=-dV_z(s_a),
\qquad (z,A_a z)\longmapsto E_a=V(z)-V(A_a z).
\]

Physical action response is a separate input: the marginal vector alone does
not specify an action, its endpoint, or how the system moves. Smoothness gives
a connection between the local slope and the finite drop; it is not required
for the finite definition itself.

SF certifies a physically identified **source contrast**. TA tests the sign
of the **already unified total action contrast**. BT requires both. These are
substantive, generally distinct certification predicates, but none aggregates
field dimensions or creates an alternative settlement formula. They are
optional relative to the valuation law and binding once a particular claim
invokes them.

**GLOBAL CHOICE NOT REQUIRED; sign predicates are claim-specific/application-specific.**
The prior unqualified “human sign-semantics decision still required” wording
in SF §18 and M §23 needs a narrow semantic clarification. M's actual assumption
lattice already makes orientation optional: A5 is not needed for its base
valuation, calculus, reduction, interaction or accounting identities. A programme
may choose to promise a particular sign property for an application, but the
mathematics does not require one global policy to make valuation exist.

This is principally **semantic recovery and reorganization of cleared
mathematics**, with explicit chain-rule corollaries. It is not a new physical
law. No particular source field is certified, no actor allocation is selected,
and W1's selected total-sign failure is preserved.

## 2. Scientific coordinate and provenance

| Item | Coordinate |
|---|---|
| Repository | `/Users/konrad.grzyb/code/ebu` |
| Branch | `codex/v6-minimal-recovery-assessment` |
| Starting commit | `df352d4a1ce28b7f133c004438263fa54cfb45ee` |
| Starting working tree | Clean |
| Cached `origin/main` | `660d6e5a56cb096fe6d1e4d202f592155d982c79` |
| Remote activity | None; the cached reference is not a freshly queried server HEAD |
| Authorized change | This report only; one local commit; no push |
| Report commit | The enclosing commit, identified in the completion response |

[Repository instructions](../../AGENTS.md) govern procedure. The frozen
foundation has precedence over the working baseline and conditional research.
The complete predecessor source readings are retained from the preceding stages
of this same task; their bytes were re-identified in the brief's dependency order,
and the proof-bearing interfaces were re-read in the committed checkout.
The additional historical stock note and relevant feedback, incidence and
sequential–parallel passages were inspected directly, including Git history.
The source hashes in Appendix A fix the exact versions used.

The present brief supplies independent clearance of F, R, MG, S, RF, the
narrowed W1 result, SF and the master theorem M at the starting commit.
That clearance is an input, not an audit performed by this report. Existing
pending-audit headers are preserved. F's legacy “freeze candidate” header is
resolved for precedence by B §0 and the pinned frozen hash, not edited here.
The scientific-record directory is absent from this checkout; historical
provenance is used where accessible in committed files and Git objects.

| Ref. | Committed source and controlling use |
|---|---|
| F | [Frozen foundation](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md), §§1–8, 12–18: layers, `μ`, `f`, finite `E`, losses, factors, interaction and accounts |
| B | [Working baseline](EBU_THEORY_BASELINE.md), §§0–7, 13, 16–18: precedence, units, local marginal potential, changing fields and historical accounts |
| R | [Path reconstruction](EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md), §§2–7, 12: path regularity, vector context, attribution boundaries |
| MG | [Möbius–generator continuity](EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md), §§3–16, 18–23: endpoint protocol, contextual marginals, affine and nonlinear response |
| S | [Equilibrium anchor](EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md), §§4–13, 16–19: conditional canonical scale and denomination |
| RF | [Recursive field theory](EBU_FIELD_RELATION_AND_RECURSIVE_SUFFICIENCY.md), §§3–14: root, joint assembly, sufficiency, memory, event boundaries and localism |
| SF | [Source-factor theorem](EBU_SOURCE_FACTOR_EMBEDDING_AND_ORIENTATION_THEOREM.md), Theorems 1–10 and §§14–18: identified factors, unchanged total and orientation predicates |
| M | [Master theorem](EBU_RECURSIVE_FIELD_SOURCE_FACTOR_CONTINUITY_UNIFICATION_THEOREM.md), §§3–7, 14–19, 23: optional assumptions and compatible shared scalar |
| W1 | [Narrowed water verdict](EBU_SOURCE_FIELD_W1_WATER_ADMISSION.md), §§5–10: distinct scoped water observable and selected coupled total |
| FB | [Feedback reconciliation](EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md), §§2–4, 18, 20–21: source provenance and complete loss-aware direction |
| SP | [Sequential–parallel bridge](../../SEQUENTIAL_PARALLEL_BRIDGE.md), §§3–7, 10, 14.1: live-state rebasing, joint measurement before allocation, named comparator |
| H28 | [Historical V2.8 draft](../../Foundation_v2.8_discrete_draft.md), Definitions 2.1–2.3 and Lemma 4.1: `μ`, state-change columns, stacked incidence and pairing |
| H27 | [Historical V2.7 mathematics](../../Foundation_v2.7_math.md), §2: earlier state-marginal / chemical-potential vocabulary, separated response laws |

### 2.1 Historical reconstruction rather than terminology by recollection

H28 explicitly defines `μ_i=∂_iV`, `μ=∇V`, columns `S_e`, their stacked
matrix, and `f_e=−∇VᵀS_e`. Its Lemma 4.1 contracts the stacked map with the
gradient. Thus the multi-action formula reconstructed below is already implicit
in that committed construction. Its separable homeostatic model, two-coordinate
loss boundary and mobility law are historical model choices, not present
universal assumptions.

The historical `research_notes/STOCK_PIPELINE_FEEDBACK_DERIVATION.md` was
read at snapshot `4d15bbd2405271c8d5ac6416caf4b49ddc3cded1`, Git blob
`0abb01f86d47b77ff3f96a0a9ece31c7a896f963`. It is recoverable with
`git show <snapshot>:research_notes/STOCK_PIPELINE_FEEDBACK_DERIVATION.md`.
Section 5 has the reduced `(S,Q,X)` dispatch and completion columns and their
marginals. Its status is explicitly conditional, unregistered and empirically
untested; retrieving it does not promote its kinetics to authority.
FB §18 derives the extended `(S,Q,X,W)` correction. FB was introduced by
`f3ef451773e5c421952c67382ea0a7d5b6565da8` and remains a non-controlling
reconciliation; its historical header is not independent audit evidence.
The current brief calls for the cleared historical constructions; every
identity used here is also checked against F and the explicitly cleared R/MG/M.

SP v0.2, introduced by `2676912a3d16f7a630cc6f113331e3aa236727e0`, records
an independent algebra audit in §14.1. Its provisional grouping rules,
experimental plans and institutional allocations remain outside this task.
Its older `D(X)` notation corresponds to the scalar state functional role;
this report retains canonical `V`, without importing historical “distortion”
or “chemical potential” as a universal physical interpretation.

## 3. Objects and the minimum assumptions

Let `Z` be the admitted state domain, represented locally by coordinates
`z=(z₁,…,zₙ)`. State completeness includes relevant reservoirs, ports, physical
memory, context and constraints. Coordinates of different physical kinds may
have different units. A constrained state space admits only tangent directions
and finite endpoints satisfying its constraints.

Assume a single-valued real finite joint potential `V` on all compared states,
in one physically justified root denomination. An action label specifies its
physical meaning, extent, boundary, duration/horizon, resolution rule and any
conditioning input. A deterministic finite response is `A_a z`; a realized
stochastic response is `A_a(z,ξ)`. Availability is declared separately.

The mathematical assumptions are modular:

| Claim | Additional conditions |
|---|---|
| Exact finite drop | Two admitted endpoints and one valid joint potential |
| Local directional quantity | Differentiability at the state and a differentiable physical action response there |
| Classical path identity | `V∈C¹` on a neighborhood of an admitted piecewise smooth path |
| Quadratic finite formula | Fixed quadratic `V`, symmetric Hessian, complete finite increment |
| Finite factor identities | Exact finite sum of factors at the same endpoints and units; physical identification for a source claim |
| Recursive reduction | Availability, reward and update sufficiency, or the appropriate joint conditional-kernel criterion |
| Boolean Möbius identity | Complete compatible finite coalition table |
| Mixed-derivative interpretation | Smooth composite response on the relevant cube face |
| Sign certificate | Independently specified orientation label and the corresponding source/total margin |
| Actor entry | Registered allowed event, identified boundary and an allocation/accounting rule closing to its complete value |

None of smoothness, source factorization, equilibrium or SF/TA/BT is necessary
for the bare finite endpoint definition. This is M's modular structure, not a
relaxation of physical admission obligations.

## 4. Marginal potential, action direction and invariant pairing

### 4.1 Recovering the terminology and units

In the declared coordinates,

\[
\boxed{\mu_j(z)=\partial_{z_j}V(z),\qquad \mu(z)=\nabla_z V(z).} \tag{1}
\]

B §6 calls this the **local marginal potential**. F calls `f` the **local
differential driving quantity**; B calls it the **directional differential
value along an action path**. “Marginal burden” and H27's “local chemical
potential” describe particular historical models. Neither “burden” nor chemical
meaning is protected in the general theory. “Marginal EBU” alone is ambiguous:
it can refer to a state derivative, an action slope or a finite contextual
increment. These are distinguished below.

For one action extent `q`, let `s_a=dz/dq` at the current point of the action
path. Then

\[
\boxed{f_a(z)=-\mu(z)^{\mathsf T}s_a(z)=-\frac{d}{dq}V(z(q)).} \tag{2}
\]

A positive `f_a` means that increasing this action extent locally decreases
`V`. It does not say that every finite amount of the action has positive EBU.
It is the **negative** directional derivative, not the unsigned derivative
and not an assumed law of motion.

In the frozen normalized convention `[V]=[E]=1`. Using “EBU” to name that
dimensionless denomination, `[μ_j]=EBU/[z_j]`, `[s_{a,j}]=[z_j]/[q]`,
`[f_a]=EBU/[q]`, and `[H_ij]=EBU/([z_i][z_j])`. Every term in (2) therefore
has the same units, even if the state coordinates have different units.
This does not turn EBU into joules or select a universal energy conversion.

The action direction is a physical input. A finite increment `Δ` becomes a
constant direction only for the declared interpolation `z(t)=z₀+tΔ`, where
`t` is dimensionless. It must not be confused with the derivative of an
arbitrary finite response at every point.

### 4.2 Covector versus vector

The intrinsic object is the differential, a covector / one-form:

\[
dV_z=\sum_j\mu_j(z)\,dz_j,\qquad
s_a\in T_zZ,\qquad
\boxed{f_a=-dV_z(s_a).} \tag{3}
\]

The displayed column `μ` contains the components of that covector. Euclidean
notation identifies the covector with a gradient vector using the chosen
Euclidean metric; the ordinary dot product is then legitimate in those fixed
coordinates. With a general metric `g`, use `g(grad_g V,s_a)=dV(s_a)`.
No metric choice is needed to define the covector-vector pairing itself.
“Scalar projection” is a useful informal description, but this is a contraction,
not necessarily an orthogonal projection onto a unit direction.

For a smooth invertible coordinate change `y=h(z)` with Jacobian `J`,

\[
s_a^{(y)}=J s_a^{(z)},\qquad
\mu^{(y)}=J^{-\mathsf T}\mu^{(z)},\qquad
(\mu^{(y)})^{\mathsf T}s_a^{(y)}=(\mu^{(z)})^{\mathsf T}s_a^{(z)}. \tag{4}
\]

**Proof.** Apply the chain rule to `V_y=V_z∘h⁻¹` and to the same physical
action path. The Jacobians cancel in the pairing. **QED.**

For example, `y=100z` changes `μ_y` to `μ_z/100` and `s_y` to `100s_z`;
it leaves `f` unchanged. Comparing raw gradient magnitudes across differently
scaled coordinates would not have this invariance. For probability-derived
potentials this argument presumes the same scalar and consistently transformed
reference measure; recomputing `−log` of a density against a new flat measure
can introduce a Jacobian term and is a different operation (S §12.2).

This precision helps EBU change coordinates without changing action values.
It neither replaces the foundation's useful notation nor introduces a metric
or “field health” measure into it.

## 5. The loss-aware completion example

Use the historical physical coordinates `(S,Q,X,W)`: source inventory, pending
inventory, usable inventory and a represented loss destination. Do not confuse
the inventory symbol `S` here with the response matrix in §7. For a completion
extent measured in one carrier unit, with usable fraction `η`,

\[
s_A=(0,-1,\eta,1-\eta)^{\mathsf T}.
\]

The carrier column sums to zero when all four coordinates use the same carrier
unit. Valuation then gives

\[
\boxed{f_A=-(0\mu_S-\mu_Q+\eta\mu_X+(1-\eta)\mu_W)
=\mu_Q-\eta\mu_X-(1-\eta)\mu_W.} \tag{5}
\]

Each sign comes from the physical direction: pending stock decreases, usable
stock increases, and loss-destination stock increases. The three terms are
contributions to **one completion slope**, not three independent prices or
three settlements. Coupling inside `V` does not change this chain rule.

The reduced formula `f_A=μ_Q−ημ_X` is complete at a state **if and only if**
`(1−η)μ_W=0` there. For it to be the correct local formula all along a path,
that product must vanish all along the path. Losslessness `η=1` and zero sink
marginal `μ_W=0` are separately sufficient; losslessness does not imply the sink
has zero marginal. A valued sink can also have zero marginal at a particular
state. An integrated omitted term might accidentally cancel over one finite
path; that does not validate the reduced pointwise formula.

F §7 supplies a concrete check on the three changing coordinates: at
`(Q,X,W)=(6,5,2)`, reference `(4,4,0)`, unit quadratic scales and `η=1/2`,
`μ=(2,1,2)`. The full slope is `1/2`; dropping the sink gives `3/2`.
The exact finite value is

\[
E(q)=\tfrac12q-\tfrac34q^2.
\]

Thus `E(q)/q→1/2`, while `E(1)=−1/4`. Both the sink correction and the
finite curvature correction are material. Dispatch has the distinct direction
`(−1,1,0,0)` and slope `μ_S−μ_Q`; it cannot be replaced by a completion or
end-to-end direction merely because the same consignment is involved.

**System meaning.** The complete direction prevents usable output from being
credited while the represented loss destination is silently omitted. The
finite formula also prevents a favorable infinitesimal signal from being
mistaken for a favorable arbitrarily large transfer.

## 6. Exact finite action value and curvature

### 6.1 The endpoint rule and path relation

For a registered complete endpoint comparison,

\[
\boxed{E_a=V(z_{\rm pre})-V(z_{\rm post}).} \tag{6}
\]

For an admitted piecewise smooth path `z(q)` and a single-valued `C¹` potential,

\[
\boxed{E_a=\int_{q_0}^{q_1}f_a(z(q))\,dq
=-\int_\Gamma dV=-\int_\Gamma\nabla V\cdot dz.} \tag{7}
\]

**Proof.** Integrate `dV/dq=dV(z'(q))` on each smooth piece and telescope.
No simply-connectedness assumption is needed when the actual single-valued
potential is already given. **QED.** This is F §3 / R §§2–4 / M U4.
If only independent marginal relations are supplied, existence of that potential
is a separate integrability problem: closed comparison integrals must vanish
(RF §7.2). Common units alone do not establish it.

Equation (7) evaluates the same finite drop, not another issue of EBU. It does
not authorize actor credits along arbitrary physical paths. Nonsmooth or
discrete actions can retain (6) while lacking this classical derivative branch;
Brownian paths require the appropriate stochastic calculus, not a classical
piecewise smooth interpretation. Conditional expected values require a supplied
response law and must be distinguished from realized endpoint entries.

### 6.2 The exact quadratic correction

For a fixed quadratic `V(z)=b+ℓᵀz+½zᵀHz`, `H=Hᵀ`, with
`μ=ℓ+Hz` at the predecessor and complete increment `Δ`,

\[
\boxed{E=-\mu^{\mathsf T}\Delta-\tfrac12\Delta^{\mathsf T}H\Delta.} \tag{8}
\]

**Proof.** Expand `V(z+Δ)` and use symmetry of `H`. The cross term is
`zᵀHΔ`; it combines with `ℓᵀΔ` to give `μᵀΔ`. **QED.**
The formula needs no positive-definiteness for its algebra. Positivity or
convexity only supplies additional sign properties. At a critical point,
`μ=0`, a positive-definite quadratic still gives negative EBU for every
nonzero finite displacement.

For a general `C²` potential on a neighborhood of the straight segment,

\[
E=-\mu(z)^{\mathsf T}\Delta
-\int_0^1(1-t)\Delta^{\mathsf T}H(z+t\Delta)\Delta\,dt. \tag{9}
\]

This follows by integrating the derivative of `V(z+tΔ)` twice. A bound
`‖H‖≤L` in an explicitly chosen, dimensionally scaled norm gives
`|E+μᵀΔ|≤L‖Δ‖²/2`. Without a declared bound or the exact quadratic form,
a frozen-gradient approximation is not an exact finite settlement.
Ordinary Hessian components express curvature in a chosen affine coordinate
system; under nonlinear reparameterization they acquire gradient-dependent
terms. Neither a diagonal Hessian nor a specific split of mixed derivatives
is an invariant source-ownership statement.

**System meaning.** A scalar action value can include all coupled dimensions
while remaining computationally explicit. Curvature records how those
sensitivities change during a finite move; omitting it can reverse the sign.

## 7. Action incidence and the marginal action-value vector

### 7.1 Several action extents

At a state where a fixed labelled family of `k` action directions is defined,
let

\[
S(z)=[s_1(z)\ \cdots\ s_k(z)]\in\mathbb R^{n\times k},\qquad
dq\in\mathbb R^k,\qquad dz=S(z)\,dq.
\]

Here `S_ji` has units `[z_j]/[q_i]`. The chain rule gives

\[
dV=\mu^{\mathsf T}S\,dq,\qquad
\boxed{f=-S^{\mathsf T}\mu\in\mathbb R^k,\quad f_i=-\mu^{\mathsf T}s_i,\quad
-dV=f^{\mathsf T}dq.} \tag{10}
\]

This is the stacked version of F's local directional quantity and H28's
explicit columns. No separability or linearity of `V` is used. Each component
of `f` describes a distinct labelled action slope; a specified combined extent
has **one scalar** first-order effect `fᵀdq`. A vector of alternatives does
not mean multiple independent settlements for one completed joint action.

A constant stoichiometric/incidence matrix is a useful special case.
For a genuinely conserved linear carrier account `Lz`, admissible closed
columns satisfy `LS=0`; reactions or open ports need their declared balances.
Heterogeneous material and energy coordinates cannot simply be summed as one
carrier. Loss destinations and boundary effects must be represented.
`S` supplies state response, not an allocation, a mobility, or a decision law.
The joint differential `dz=S dq` is assumed for the allowed joint variations;
it does not authorize simultaneous extents of mutually incompatible actions.

At a boundary, admissible extents may form only a cone, and derivatives may
be one-sided. The unrestricted matrix notation is local on a suitable smooth
mode. A changing action family or discrete action does not automatically have
one globally fixed-dimensional differentiable `f`.

### 7.2 Nonlinear response and what a local matrix cannot supply

If an actual `C¹` response surface `z=R(q)` is given on an action-coordinate
domain, its Jacobian is `J_R∈R^{n×k}`. Then

\[
\boxed{\nabla_q(V\circ R)=J_R^{\mathsf T}\mu(R(q)),\qquad
f(q)=-J_R^{\mathsf T}\mu(R(q)).} \tag{11}
\]

The left side is a column of partial derivatives for a scalar function of a
vector `q`, not an ambiguously oriented `dV/dq` matrix. When `k=1`, this
reduces to (2). Under a change of action coordinates, `f` transforms as a
covector in action space; “vector” here means its convenient column array.
Rescaling one extent rescales its slope inversely, leaving `fᵀdq` invariant.

A state-dependent collection of possible directions `S(z)` does not by itself
supply a global response surface `R(q)`. Noncommuting directions, modes and
history can make order matter. For example, the vector fields `(1,0)` and
`(0,x)` have bracket `(0,1)`: starting at `(0,0)`, the unit maps
`A(x,y)=(x+1,y)` and `B(x,y)=(x,y+x)` reach `(1,1)` in order A then B,
and `(1,0)` in order B then A. These are static map compositions, not executed
trajectories. Both endpoint valuations are well-defined; an unordered shared
endpoint is not. For `V=(x²+y²)/2` their drops are `−1` and `−1/2`.

Nor can the action-value vector generally reconstruct the full state marginal.
Any covector `ν` with `Sᵀν=0` can be added to `μ` without changing `f` at that
state. Inaccessible directions and the action family matter. This is the
local counterpart of B §5's accessible-subspace qualification.

**Recommendation.** Use **action response matrix** generally, **action incidence
matrix** for its declared stoichiometric special case, and **marginal action-value
vector** for `f`. These clarify existing notation; they are recommendations
pending audit, not canonical authority edits.

## 8. Vector context and the extended field

Write `V=V(x,λ)` with `λ∈R^m`; `λ` denotes the vector `θ` used as external
context in R, avoiding collision with RF's retained-state notation. For a
physically justified extended potential on `z=(x,λ)`,

\[
\boxed{dV=\nabla_xV\cdot dx+\nabla_\lambda V\cdot d\lambda=\nabla_zV\cdot dz.} \tag{12}
\]

Equivalently, the one-form is `dV=Σ_j∂_{z_j}V dz_j`. Along an action path both blocks enter
`f=−∇_xVᵀx'−∇_λVᵀλ'`. This is the clean unified differential description
of a changing multidimensional context (R §6, M U4 equation (6)).

In R's example `V=λx²/2`, `(x,λ)=(1+q,1+3q)`, `0≤q≤1`, the complete
drop is `−15/2`: the state integral is `−4`, and the context integral is
`−7/2`. Discarding the second block does not preserve the action value.
The separate integrals need not be endpoint functions; their sum is. They
are not automatically actor and environment allocations.

A family of unrelated fixed-context potentials with arbitrary offsets does
not acquire comparable cross-context levels merely by adjoining `λ` as a
coordinate. A valid common extended potential and boundary are required.
An action-induced context change inside the registered event is included in
its complete endpoints. Evolution outside that event is passive. If action
and environment act concurrently, a declared combined event map or justified
chronological subdivision is needed; causality alone does not uniquely split
them. Historical actor entries are not repriced in either case.

## 9. Recursive state, finite action maps and feedback

### 9.1 What is stored and what is evaluated

For a deterministic family of registered finite actions define

\[
\mathcal E_a(z)=V(z)-V(A_a z),\qquad
\mathcal E(z)=(\mathcal E_{a_1}(z),\ldots,\mathcal E_{a_k}(z)). \tag{13}
\]

For state-dependent availability, the better object is a **labelled map**

\[
\boxed{\mathcal P(z):\mathcal A(z)\longrightarrow\mathbb R,\qquad
 a\longmapsto\mathcal E_a(z).} \tag{14}
\]

A bare set of numbers `{ℰ_a(z)}` loses which action has which value and collapses
coincident values. The map retains action identity, quantity, horizon and
protocol. In a stochastic model retain `ℰ_a(z,ξ)` and its conditional law;
`E[ℰ_a(z,ξ)|z,a]` is a conditional expected quote, not an already realized entry.
Unavailable or incompletely specified actions have no claimed exact value.
Institutional permission may depend on separate institutional state; physical
state sufficiency does not determine every legal or account-based permission.

If `A_{a,0}(z)=z` and `q↦A_{a,q}(z)` is differentiable at zero with direction
`s_a(z)`, then

\[
\left.\frac{d}{dq}\mathcal E_{a,q}(z)\right|_{q=0}=f_a(z). \tag{15}
\]

For a `C²` potential and a `C²` response near zero, put `r_a=∂_q²A_{a,q}(z)|₀`. Then
`ℰ_{a,q}=q f_a−½q²(s_aᵀHs_a+μᵀr_a)+o(q²)`.
Thus response curvature, as well as potential curvature, separates a finite
quote from its local slope. With a constant response column and quadratic
potential the `r_a` term vanishes and (8) is exact.

### 9.2 Two update channels and permanent entries

With current sufficient state, relevant inputs and declared event maps,

\[
\widetilde z_n=A_{a_n}(z_n,\xi_n^a),\qquad
z_{n+1}=P(\widetilde z_n,\xi_n^p)=F(z_n,a_n,\xi_n), \tag{16}
\]

\[
E_n=V(z_n)-V(\widetilde z_n),\qquad
D_n=V(\widetilde z_n)-V(z_{n+1}). \tag{17}
\]

Only `E_n` is the registered action total. `D_n` records the passive potential
drop. With no registered action take `A_∅=Id`, so actor entries are unchanged
even when `P` changes the field. If aggregate registered balances close by
`C_{n+1}−C_n=E_n`, then

\[
\Delta(C+V)=-D_n,\qquad
\sum_{n=0}^{N-1}(E_n+D_n)=V(z_0)-V(z_N). \tag{18}
\]

**Proof.** Substitute (17) and cancel the intermediate potential levels.
**QED.** These are accounting identities, not physical carrier conservation.
For a single registered actor an allocation may assign the total to that actor;
a multi-actor event requires a separate closing allocation. Neither gradients
nor sign predicates choose it.

Next-state marginals and action slopes are evaluated afresh:

\[
\mu_{n+1}=\nabla V(z_{n+1}),\qquad
f(z_{n+1})=-S(z_{n+1})^{\mathsf T}\mu_{n+1}. \tag{19}
\]

They **may**, but need not, differ from their previous values. This is the
valuation feedback: the action changes relevant physical state, and that state
changes later valuations. It is not a feedback control law until an action
selection/response law is independently supplied. No historical action-price
vector is an input to (13)–(19). Past physical effects must survive in the
current state when future-relevant; pending deliveries, damage or reservoir
memory cannot be discarded just because past prices are unnecessary.

For fixed `V∈C²` and a supplied differentiable physical law `ż=b(z,t)`,
`μ̇=Hż` and `ḟ=−Ṡᵀμ−SᵀHż` in a fixed smooth action family.
Explicit time dependence adds `∂_tμ`, or is included as justified context.
For a state-block marginal `μ_x(x,λ)`, the analogous derivative is
`H_xx ẋ+H_xλ λ̇`. These are chain-rule consequences conditional on the
motion; the potential does not forecast that motion by itself.

## 10. One joint local field and its spatial limits

The recommended description is **one multidimensional joint field for the
admitted action boundary**, with several physical coordinates and possibly
several source domains and factors. A network can have many local patches.
“Unified” means compatible valuation of a complete response, not a proof that
one small finite vector captures an entire economy or that arbitrary local
fields can be glued together.

| Object | Meaning; not interchangeable with the other rows |
|---|---|
| State coordinate | One component of a representation of current physical condition |
| Source field/domain | A physical subsystem with declared boundary, ports and constitutive meaning |
| Factor `φ_α` | A scalar term in a justified representation of `V`, possibly spanning several sources |
| Interaction term | A coupled dependence inside `V` or a finite action-table interaction, with its type specified |
| Context coordinate | A parameter/environmental degree of freedom; part of the extended state only when its cross-context potential is justified |
| Marginal component | A derivative with respect to a coordinate; can receive contributions from many factors |

Common denomination is necessary for physically comparable field values but
does not prove compatible joint assembly. RF §7's equal-unit covector
`(y,0)` has integral `−1` around the unit square, so it cannot be `dV` on
that square. A supplied potential avoids that reconstruction problem.

Exact localization is possible when all changing factors and their complete
supports are included; unchanged factors cancel. Long-range coupling, response
propagation or hidden memory can enlarge the required neighborhood. Truncation
needs a bound such as `Σ_omitted |E_α|≤ε`. A reduction needs the RF/M
sufficiency conditions, not just a compact current scalar `V`, a gradient or
an observed snapshot. The “field” is this sufficient physical condition and
context, not a stored list of old prices.

## 11. Factors, gradient components and nonseparable potentials

For a finite exact factorization in a common denomination,

\[
V(z)=b+\sum_\alpha\phi_\alpha(z_{S_\alpha}),
\quad
\mu=\sum_\alpha\nabla\phi_\alpha,
\quad
f_a=\sum_\alpha[-d\phi_\alpha(s_a)],
\quad
E_a=\sum_\alpha[\phi_\alpha(z)-\phi_\alpha(A_a z)]. \tag{20}
\]

Factors are embedded on the full state; `b` is constant on the comparisons.
For the derivative identities the factors must be differentiable at the state.
For an infinite representation, appropriate convergence and interchange
conditions would be needed; none is presumed here. All endpoints, boundaries
and units must match. Approximate embeddings retain their residual contrast.

**Proof.** Differentiate the finite sum and use linearity of the covector
pairing; subtract the finite sum at the two endpoints. **QED.** This is F §13,
SF Theorem 2 and M U2. A touched coupled factor is reevaluated as a whole.

`−dφ_α(s_a)` is a **local factor contribution** to the slope; `δφ_α` is a
**finite factor contribution**. Calling either a source contribution requires
independent physical source identification and embedding as in SF Theorems
3, 4 and 8. The term “marginal contribution” must specify derivative versus
finite contextual meaning. Gradient components are indexed by coordinates;
factor contributions are indexed by factors. Their indices need not even
have the same cardinality.

A differentiable nonseparable `V` still has `dV` and an exact endpoint drop.
No source separation theorem is needed to evaluate either. For
`V=φ_A+φ_B+φ_AB`,

\[
f_a=-d\phi_A(s_a)-d\phi_B(s_a)-d\phi_{AB}(s_a).
\]

The interaction enters once without first deciding whether A or B owns it.
A source-bundled decomposition may later assign parts of that interaction by
an explicit convention; the complete action value is unaffected. This is
exactly the separation retained by SF §7.1 and M U2.

### 11.1 One coupled example, three distinct decompositions

Take the mathematical potential
`V(x,y)=x²/2+y²/2+xy/2` and direction `s=(−1,1)` at `(2,0)`.
Then `μ=(2,1)`, so the unified local slope is `f=1`. Its coordinate pairings
are `(2,−1)`, while the three factor slopes are `(2,0,−1)`.
Neither list is an actor allocation.

For the complete unit increment to `(1,1)`, the exact value is `2−3/2=1/2`.
The factor contrasts are `(3/2,−1/2,−1/2)`, again summing to `1/2`.
The quadratic correction is `−½sᵀHs=−1/2`, explaining the difference from
the initial slope. Coupling is included without inventing separate field
prices. This is an algebraic witness, not a proposed physical source model.

### 11.2 Why factor identity still matters

Writing `V=φ_s+Ψ=(φ_s+g)+(Ψ−g)` preserves the total and its derivatives
but changes the proposed source contrast by `g(pre)−g(post)`. Algebra alone
cannot certify which source interpretation is correct. SF Theorem 3 requires
allowed gauges to be constant on connected components of the claimed comparison
graph to preserve all source contrasts. Root calibration and a favorable sign
do not remove this identification requirement.

Thus factorization is secondary to the **valuation law**, but can be primary
in a **constitutive construction or efficient implementation** of `V`.
One can compute the total exactly from changing factors without materializing
a global potential level. “Joint first” expresses semantic authority, not a
mandatory order of numerical operations, and it does not mean factor theory
has become dispensable for source claims.

## 12. Joint action, synergy and sequential marginal values

Fix a compatible complete table with `z_∅=z₀` and
`E(C)=V(z₀)−V(z_C)`. All action meanings, extents, contexts, constraints and
horizons must match. Then `E(∅)=0` and

\[
E_{AB}=V(z_0)-V(z_{AB}),\qquad
m_{AB}=E_{AB}-E_A-E_B. \tag{21}
\]

The joint value is defined independently of the standalone values. Adding
standalone quotes from the same predecessor gives the joint value only if
the appropriate additivity condition holds. Möbius decomposition explains
the difference; it creates no extra issue.

Define the contextual finite increment

\[
E(B\mid A)=V(z_A)-V(z_{AB}).
\]

Substitution immediately proves

\[
\boxed{E_A+E(B\mid A)=E_{AB},\qquad
m_{AB}=E(B\mid A)-E_B.} \tag{22}
\]

The name “actual sequential B after A” additionally requires its physical
execution to reach `z_AB` with the same comparison protocol. Otherwise it is
only the specified contextual endpoint difference. If actual serial B reaches
`y_AB`, then

\[
E_{\rm serial}(B\mid A)-E_B
=m_{AB}+V(z_{AB})-V(y_{AB}). \tag{23}
\]

The extra term is a named endpoint-comparator discrepancy. Equality of the two
final potential levels suffices for equal totals; equality of states is stronger.
Noncommuting maps or different waiting times do not contradict telescoping.

In §11.1's example let A be `Δ_A=(−1,0)` and B be `Δ_B=(0,1)`.
The same-base values are `E_A=3/2`, `E_B=−3/2`, while `E_AB=1/2`.
The rebased value is `E(B|A)=−1`, giving `m_AB=1/2`. The translations
commute and the serial and parallel endpoints coincide; the named
parallel-versus-serial advantage is zero although the Möbius pair is nonzero.
This is precisely SP §§6–7's distinction between comparator-relative
interaction and same-baseline nonadditivity, formalized in MG §7.

The sequential marginal is a **finite contrast in a changed context**.
It is not `μ_j`, and in general it is not even the local slope `f_B`.
For more actions, MG §6 gives
`E(C∪{i})−E(C)=Σ_{T⊆C}m_E(T∪{i})`.
This does not select a unique allocation among actors or prove causal influence.

**System meaning.** Repricing the next action from its actual predecessor
prevents duplicate credits for an effect already achieved. Retaining the joint
endpoint avoids losing beneficial or adverse interactions between actions.

## 13. The differential-to-Möbius continuity chain

Let `N` be a finite labelled action family. Define the full Boolean table
as above, and `G(C)=V(z_C)`. For nonempty `T⊆N`,

\[
\boxed{m_E(T)=\sum_{C\subseteq T}(-1)^{|T|-|C|}E(C)
=-\Delta_TG(\varnothing).} \tag{24}
\]

**Proof.** Expand the mixed difference. Its nonempty alternating sum annihilates
the common baseline `V(z₀)`. **QED.** No differentiability is needed. At the
empty set `m_E(∅)=0`, not `−V(z₀)`. Missing or inadmissible corners cannot be
silently filled with zero. A no-action endpoint with passive drift requires
an explicitly centered table or a retained nonzero empty value, as MG explains;
that change of comparator does not redefine actor settlement.

For fixed additive increments `h_i`, `z_C=z₀+Σ_{i∈C}h_i`, and `V∈C^r`
on a neighborhood of the relevant parallelotope (`r=|T|`), repeated FTC gives

\[
m_E(T)=-\int_{[0,1]^r}
D^rV\!\left(z_0+\sum_{i\in T}t_i h_i\right)[h_i:i\in T],dt. \tag{25}
\]

In particular,
`m_AB=−∫₀¹∫₀¹ h_AᵀH(z₀+t h_A+u h_B)h_B\,dt\,du`.
For a quadratic potential this is exactly `−h_AᵀHh_B`, and every order
`≥3` vanishes. A Hessian at a single point is not generally the finite pair.
With increments `h_i=ε_i s_i` tending to zero and continuous mixed derivatives,
`m_E(T)/(∏ε_i)→−D^rV(z₀)[s_i:i∈T]`.
The unnormalized finite coefficient tends to zero; it is not simply equal to
a local mixed derivative.

For a nonlinear smooth response `z=R(u)` matching the coalition vertices,
with `u` dimensionless indicators, define `g=V∘R`. Repeated FTC now gives

\[
m_E(T)=-\int_{[0,1]^T}\partial_Tg(u_T,0_{N\setminus T})\,du_T,
\quad
\nabla_u^2g=J_R^{\mathsf T}H J_R+\sum_j\mu_j\nabla_u^2R_j. \tag{26}
\]

The pair derivative is
`∂_{ij}g=D²V[R_i,R_j]+DV[R_ij]`.
The second term cannot be discarded merely because `V` is quadratic.
For three distinct labels it becomes
`D³V[R_i,R_j,R_k]+D²V[R_ij,R_k]+D²V[R_ik,R_j]+D²V[R_jk,R_i]+DV[R_ijk]`.
These are MG §§15–16's chain-rule terms, not new physical assumptions.
The smooth extension must exist on the needed face; an arbitrary interpolation
of vertices does not identify intermediate physical responses. Different
extensions can redistribute derivative-origin contributions while retaining
the same total finite coefficient.

M U11's exact witness is `V(z)=z²/2`, `z_C=|C|²` for three actions.
The cardinality values `(0,−1/2,−8,−81/2)` give `m_123=−18`.
The potential is quadratic; the composite response is not. Conversely,
`V(z)=z³` with additive unit increments gives `m_123=−6`.
Thus neither a quadratic potential alone nor additive response alone proves
the pair-only bound.

The continuity chain is therefore

```text
specified smooth joint response and potential
  → local composite derivatives / action slopes
  → integration over the registered response or action cube
  → exact endpoint / coalition values
  → finite Möbius hierarchy
```

The endpoint and Möbius steps also exist without the smooth branch. Every link
retains its own hypotheses. “Marginal” here is differentiation or contextual
subtraction, not statistical marginalization: replacing full `V` by
`−log∫exp(−V)` is M U6–U8's distinct operation, generally changing values
unless its residual contrast vanishes on the specified comparisons.

## 14. Root denomination and localism

For a legitimate same-kind calibration `V'=cV+d`, with constants `c>0,d`
on the comparison domain and the same physical coordinates and responses,

\[
\mu'=c\mu,\qquad H'=cH,\qquad f'=cf,\qquad E'_a=cE_a. \tag{27}
\]

**Proof.** Differentiate or subtract the affine relation; `d` drops out.
**QED.** Root conversion divides out the representation scale, so corresponding
values agree. A state-dependent scale or offset introduces extra derivative
and endpoint terms and is not this theorem. No field-specific multiplier is
introduced to engineer desired signs. Units of action extent must also be
aligned before slopes are compared.

With one fixed `V`, two local states can have different gradients and different
values for the same physical action. For `V(x)=(x−2)²/2`, a withdrawal
`A_h(x)=x−h`, `h>0`, gives

\[
f(x)=x-2,\qquad \mathcal E_h(x)=h(x-2)-\tfrac12h^2. \tag{28}
\]

At `h=1/2`, states `x=1` and `x=3/2` give slopes `−1,−1/2` and exact
values `−5/8,−3/8`. The ruler is unchanged; the starting physical condition
is different. This is a symbolic localism example, not a fitted resource law.

The inequalities are possible, not necessary consequences of unequal states.
For linear `V(x)=x`, every state has the same marginal and same value for a
fixed increment. Even unequal gradients can give equal action values:
`V=(x²+y²)/2`, states `(1,0)` and `(1,2)`, and direction `(1,0)` have
identical `f=−1`; adding `(1/2,0)` gives `E=−5/8` at both states.
Their gradient difference lies in a direction the action does not change.

Current localism therefore changes **new** action values when relevant state
or response changes. It does not retrospectively change a historical entry,
and a shared denomination does not assert equal prices for identically named
but physically different events.

## 15. SF, TA and BT: exact roles and logical independence

For one predeclared physical sign claim, let `σ∈{−1,+1}` be its intended
orientation, fixed independently of the computed sign. This symbol replaces
SF's `s` here to avoid collision with the action direction `s_a`. A source
claim uses a physically identified embedded factor contrast `E_s`. Let
`E=E_s+E_rest` when the exact decomposition is justified. Then

\[
\mathrm{SF}:\ \sigma E_s>0,\qquad
\mathrm{TA}:\ \sigma E>0,\qquad
\mathrm{BT}:\ (\sigma E_s>0)\ \land\ (\sigma E>0). \tag{29}
\]

For exact factorization BT can equivalently use
`σE_s>0` and `σE_rest>−σE_s`.
This is SF Theorem 5 / M U2 equation (4), unchanged.

| Regime | Exact category | What it adds | Effect on the valuation law |
|---|---|---|---|
| SF | Source-orientation certification predicate | A sign property of an independently identified source contribution on the declared comparison set | None: complete settlement remains `E`, possibly with a different sign |
| TA | Total-action sign predicate; an admission filter if adopted for an application | A constraint on the already defined total for an independently labelled action class | None: it filters/adjudicates a scalar, and aggregates nothing |
| BT | Joint source-and-total certification | Conjunction of the two claims | None: not a rule for combining dimensions and not a second total |

TA itself needs no source factorization. SF and BT need source identification
and embedding before their algebraic signs can be physical certificates.
All three can be used as diagnostic truth tests; satisfying a numerical
inequality alone does not establish every physical prerequisite.

### 15.1 Why unified valuation does not make the predicates redundant

The cleared SF examples use `φ_s(w)=(w−2)²`, `Ψ(y)=y`, and the independently
declared depletion label `σ=−1`:

| Complete comparison | `E_s` | `E_rest` | `E` | Predicate result |
|---|---:|---:|---:|---|
| `(1,10)→(0,0)` | `−3` | `10` | `7` | SF true, TA false, BT false |
| `(3,0)→(2,2)` | `1` | `−2` | `−1` | SF false, TA true, BT false |
| `(1,0)→(0,0)` | `−3` | `0` | `−3` | SF, TA and BT true |

These are mathematical countermodels, not physical certificates for a source.
They prove SF and TA are generally incomparable, and BT can be nonempty.
Every row nevertheless has a unique unified total before any predicate is
chosen. They disprove both “one regime is necessary to calculate E” and
“unification makes source/total distinctions meaningless.”

Pointwise strict signs and uniform robust margins are different claims.
A uniform certificate requires a positive infimum over its declared joint
state/action/outcome/uncertainty domain. Pointwise positivity can approach zero
as action size shrinks. Existing source and total error bounds must accompany
a robust claim; this reconstruction introduces no thresholds or sign repairs.

### 15.2 No logically necessary global choice

**Proposition — orientation is not an input to the valuation map.** Given the
admitted complete potential and action endpoints, (6), (10), (13) and the
conditional identities derived from them are defined without `σ`, `E_s` or a
regime variable. Therefore no one-time global SF/TA/BT choice is necessary
for unified EBU valuation or for its recursive extension.

**Proof.** The right sides use only the stated potential, response, state and
calibration. Introducing a predicate on the resulting values does not change
those right sides. F §§3, 13–17 establishes that order; RF §§7–10 preserves it;
SF §18.1 says all regimes keep complete settlement. M §3 explicitly separates
A5 from its base, U2 says it is unnecessary for the other identities, and M §19
calls signs necessary only for the chosen orientation certificate. **QED.**

A programme may make a uniform sign promise as an additional application
requirement. It must then specify which quantity, independently defined physical
labels, domain, uncertainty and strict/neutral cases it means. It cannot switch
from TA to SF after a TA failure and call the old claim successful. The same
action may deplete one source and restore another; opposite source labels can
coexist, but demanding both opposite signs of its single total is inconsistent.
Likewise, strict positive-drop labels around a complete comparison cycle
contradict telescoping. These restrictions remain substantive.

The precise replacement for the over-broad earlier framing is:

> No global SF/TA/BT choice is required to define or operate the conditional
> valuation mathematics. For each additional orientation claim, specify and
> certify the source predicate, total predicate, or their conjunction on its
> declared domain. Until then no such sign guarantee is claimed.

This is a proposed **semantic clarification only**, not a change to SF/M
inequalities, hypotheses or proofs and not an adopted sign policy.

## 16. Restorative meaning and the primacy of total settlement

For the mathematical use “restorative means `V_post<V_pre`,” the statement
“restorative actions have positive EBU” follows exactly from the definition.
The analogous degrading statement follows for `V_post>V_pre`. Equality gives
zero. These are frozen sign semantics relative to the admitted potential.

A separate physical label such as replenishing a particular stock, restoring
an ecological function or depleting a source need not coincide with that
ordering of the **complete** potential. Establishing the correspondence is
an additional physical/semantic claim. A desire that whole-action degradation
always receives negative settlement is a programme intent expressed as a TA
claim on those independently labelled complete events. A source-only intent
is an SF claim. Neither follows merely by attaching the word “restoration”
to a coordinate change. A label chosen from the answer's sign makes the
claim tautological, not a test of an independently described physical property.

Whenever a complete valid joint potential and a registered, identified action
boundary exist, **`E_total=V_pre−V_post` is the controlling finite settlement
basis**. The word “basis” matters: actor registration and allocation are
separate Layer-3 conditions. One scalar physical total need not correspond to
one actor or a unique distribution among actors. A passive potential change
is not an actor transaction. These are existing boundaries, not qualifications
introduced by source-factor theory.

Factor contrasts explain that total; with physical identification they support
source claims, and with signs they support certification. They are not extra
actor issues. If an allocation uses them, that allocation still needs a declared
rule closing to the joint value. F §§15–18 explicitly distinguishes closure
from unique ownership, causality or fairness.

## 17. Unified synergy/field principle and the settlement table

**Proposition — semantic priority of the complete response.** Under the admitted
state, potential and response assumptions, the finite physical valuation is
fixed by the complete endpoint contrast. Where the relevant additional
hypotheses hold, differentiation, factor decomposition and Möbius inversion
are compatible descriptions or diagnostics of those same values; none creates
additional physical value or determines an actor split.

**Proof.** Equation (6) fixes the total independently of decomposition.
Differentiation gives (2); integration (7) recovers the same finite total.
Exact factor linearity gives (20). For a complete coalition table, (24)
transforms already defined values and Möbius inversion reconstructs them
exactly. No new endpoint change enters any of these operations. F's allocation
layer remains separate. **QED.**

This is the same semantic principle behind “joint endpoint before synergy
allocation” and “joint field before component attribution.” It does **not**
assert that coordinate, factor and coalition decompositions are identical.
Coordinate integrals may be path-dependent; factor identities require actual
factorizations; Möbius terms compare counterfactual endpoints. The principle
also does not require first computing a global number in software: exact
factor sums are a valid way to evaluate it, and constitutive factor models may
be how `V` is obtained in the first place.

| Object | Form | Role | Actor settlement? |
|---|---|---|---|
| Current state | `z` | Sufficient physical condition/context | No |
| Potential | `V(z)` | Joint scalar state potential | No, a level is not an entry |
| Marginal potential | `μ`, intrinsically `dV` | Coordinate sensitivities | No |
| Action response | `S` or `J_R` | How action extents change the complete state | No |
| Marginal action-value vector | `f=−Sᵀμ` | Local action slopes | No; `fᵀdq` is an infinitesimal contribution, not `f` as an entry |
| Finite action value | `E=V_pre−V_post` | Exact physical settlement basis | Yes when registered and under a closing allocation |
| Factor contrasts | `E_α` | Explanation, source identification/certification | Not extra issuance; not automatic actor shares |
| Möbius terms | `m_E(T)` | Finite interaction decomposition on a declared table | Not extra issuance or automatic allocation |
| Current action map | `𝒫(z):a↦ℰ_a(z)` | Labelled available finite comparisons | Only the selected realized registered event is settled |

The draft table's proposed “except infinitesimal limit” exception for `f` is
removed: its units are EBU per extent. The limiting density is not itself a
finite actor entry. Any continuous accounting construction must integrate it
over a declared registered process and retain the existing boundary rules.

## 18. Monitoring outputs and the field-health boundary

A useful mathematical output family is
`z(r,t), V(z), μ(z), H(z), S(z), f(z), 𝒫(z)` and, where a complete matched
coalition table exists, `m_E(T)`. Spatial position is written `r` here to avoid
confusing it with a state coordinate. A distributed model needs its own
spatial domain and observation specification; this list does not implement one.

| Output | What it establishes within the declared model | Useful role and boundary |
|---|---|---|
| Current `z(r,t)` and context | Represented physical condition; observed or inferred according to an explicit observation model | Monitoring and scenario initialization; sufficiency is a separate claim |
| `V(z)` | Potential level in the specified gauge | Within-model comparisons; absolute levels are gauge-dependent |
| `μ=∇V` | Local sensitivity to coordinate perturbations | Sensitivity analysis; compare only with specified units/scales and feasible directions |
| `H=∇²V` | Local curvature and coordinate coupling | Finite-step corrections and response sensitivity; not the dynamic Jacobian or a causal network by itself |
| `S` / `J_R` | Declared physical response to action extents | Identifies which state sensitivities an action actually uses |
| `f=−Sᵀμ` | Local slopes of those action values | Small-action comparison in common extent units; no unlimited finite extrapolation |
| `𝒫(z)` | Exact finite values for the declared current action family or conditional laws for unresolved outcomes | Scenario comparison; validity depends on the endpoint model and domain |
| `ż`, `μ̇`, `ḟ` | Evolution/sensitivity rate when a physical law or measured time change is supplied | Forecasting inputs; future prediction requires identified dynamics, inputs and observation/error assumptions |
| Factor and Möbius diagnostics | How a specified total decomposes, or how matched action combinations differ | Explaining coupling, identifying sensitivity to scenarios; no automatic causal or ownership claim |

A large `μ_j` means a large potential change per **specified unit** in that
direction. It is not automatically scarcity, hazard, forecast, market price
or social value. Early warning needs a separately defined event/threshold and
a relationship between these observables and that event. Curvature and
interaction diagnostics can inform that model; they do not create it.
These boundaries leave the mathematical outputs useful without assigning
unsupported meanings to them.

**FIELD HEALTH SCALAR: NOT JUSTIFIED GENERICALLY; CONDITIONAL ON A SEPARATE
PHYSICAL MODEL.** A scalar settlement does not imply scalar environmental
health. None of `V`, `‖∇V‖` or distance to a reference is a universal health
index. `V` has a chosen physical meaning and an arbitrary additive gauge;
a gradient norm needs a metric and scales; distance needs a reference and a
metric. At a critical point the gradient vanishes whether the point is a
minimum, a maximum or a saddle. A small represented potential cannot certify
unrepresented physical dimensions.

Moreover a scalar level need not be a sufficient state even for valuation:
for `V(x)=x²/2`, states `1` and `−1` have the same level but the action
`x↦x+1` has values `−3/2` and `+1/2`. The field may legitimately remain
multidimensional while every registered action has one scalar physical total.
A future health index would need its own physical meaning and justification;
none is invented for visualization here.

## 19. Symbolic source-to-shop example

Consider declared source, production, transport and shop events. Each has a
current complete state, actual endpoint response and a compatible joint
potential; relevant physical effects are carried forward through the state
and ports. Choose one **physical use of an apple**, denoted `a_apple`, with
its quantity and endpoint protocol specified symbolically. At the shop's
current sufficient state `z_t`,

\[
\boxed{E_{\rm apple}(z_t)=V(z_t)-V(A_{\rm apple}(z_t)).} \tag{30}
\]

All currently affected physical dimensions enter through those endpoints.
If an exact factorization exists, changing source, storage, transport-memory,
resource and coupled factors explain the number; these are possible structural
roles, not an asserted apple physiology or apparatus model. If matched
multi-action endpoints are specified, Möbius terms can describe their
interaction. Neither decomposition creates additional settlement.

No upstream historical EBU is replayed into (30). Earlier expenditure of
materials or energy remains relevant only through present physical consequences
or sufficient memory/boundary state, not through the old number charged for it.
Across a sequence, actual action and passive drops telescope as in (18).
Historical actor entries keep their recorded values and calibration versions.

“Buy,” “consume” and “use” cannot be treated as one physical map by vocabulary
alone. A change of legal ownership that leaves every admitted physical state
coordinate unchanged has zero physical endpoint drop in this model; its market
price is a separate institutional object. A consumption or use event may have
a different physical endpoint. No actual apple law, ownership inference or
universal fundamental apple potential is supplied by (30).

**System meaning.** This architecture values the next actual change in current
conditions without duplicating prior receipts. It can explain that value using
physical factors while keeping the action total and allocation boundary clear.

## 20. E1a and W1 under the recovered semantics

### 20.1 E1a: unchanged objective and design

S's canonical branch supplies the scoped normalization
`V=(U−U*)/(k_BT)`, with the independent physical canonical assumptions and
reference measure held correctly. It predicts `J=−log p=V+C`, hence
`β_bridge=1` and `E=J_pre−J_post`; ordinary post-minus-pre `ΔJ` is `−E`.
The P4 medium/system entropy statements require their additional thermodynamic
conditions. None is a universal claim about arbitrary environmental fields.

E1a addresses the **root ruler / canonical scale branch**. It does not test
all dimensions of a future environmental state, all entries of `S`, future
source factors, global recursive closure or an economy. Writing `f=−Sᵀμ`
neither alters an E1a objective nor resolves its apparatus/qualification
questions. All T/U/V designs, qualification states and execution boundaries
remain unchanged.

### 20.2 W1: joint gradient exists, total-sign refusal survives

The narrowed W1 report compares two distinct objects. Its scoped canonical
water observable `V_w=(U_w−U*)/(k_BT_ref)` has negative withdrawal contrast
below equal head and favorable restoration contrast within that domain.
Its **selected complete finite-bath potential** is instead

\[
V(w,e)=-c_b\log\frac{u}{u_*},\qquad
u=H_0-e-U_w(w)>0,\qquad c_b>0,
\]

where `u` is the bath energy and `u_*` is a fixed positive reference. The
symbol `H_0` denotes W1's conserved complete physical energy, not a Hessian.
Its marginals are

\[
\mu_w=\frac{c_bU'_w}{u},\qquad \mu_e=\frac{c_b}{u},\qquad
V_{we}=\frac{c_bU'_w}{u^2}.
\]

The nonzero mixed derivative on the stated lower-column domain precludes an
independent unary separation into a water term and drive term. Nevertheless
the **joint gradient and endpoint value exist without source allocation**.
For the complete action with dissipation `L≥0`, W1 derives

\[
\boxed{E_{\rm total}=c_b\log(1+L/u).} \tag{31}
\]

It is positive for dissipative withdrawal and zero at `L=0`. Both fail the
claimed strictly negative complete-withdrawal value. No positive root
rescaling or change from gradient notation to a covector changes that result.

As a local algebraic check, along any smooth realization of the same complete
energy account, `u'=L'` and `e'=−U'_w w'−L'`; pairing the two joint marginals
gives `f=−(c_b/u)(U'_w w'+e')=c_bL'/u`. Integrating, when the stated path
regularity holds, recovers (31). This is a conditional rewriting of the
existing endpoint account, not a newly supplied hydraulic response law.

W1 therefore illustrates the danger of confusing a scoped source diagnostic
with a complete finite action. More precisely, the favorable water observable
has **not** been certified as an embedded physical factor of that chosen joint
potential. It would overstate the result to call it an already proved component
whose value is simply added to other independent prices. The source-factor
possibility remains open; the selected complete-action orientation remains
failed. This does not refute endpoint valuation, all possible water sources
or the root denomination. It also does not establish efficiency or welfare:
the selected model's larger positive value for more dissipation is exactly
why its intended total-sign interpretation fails.

## 21. Effect on the existing theorem hierarchy

| Source | Classification | Exact disposition |
|---|---|---|
| Frozen foundation | **UNCHANGED** | Its `V/μ/f/E` hierarchy, complete loss direction, factor linearity and Layer-3 allocation already supply the recovered semantics |
| R path theory | **UNCHANGED** | Classical path and vector-context differential used with existing regularity and registration limits |
| S-MG | **UNCHANGED** | Complete-table, contextual marginal and smooth composite-response theorems applied exactly |
| S equilibrium anchor | **UNCHANGED** | Root/canonical branch remains conditional; no universal field or action-response claim added |
| Recursive field theory | **UNCHANGED** | Current state, ports, sufficiency, action/passive channels and no historical repricing retained |
| Source-factor theory | **SEMANTIC CLARIFICATION ONLY** | Its theorems already preserve total settlement. SF §18's unqualified final “decision still required” line is narrowed to an additional declared orientation claim, not a global valuation prerequisite |
| Master unification theorem | **SEMANTIC CLARIFICATION ONLY** | M §23's global-choice framing is narrowed using M's own optional A5 and U1/U2/§19. No theorem equation or condition changes |
| W1 narrowed result | **UNCHANGED** | Existing selected total-sign refusal and uncertified source embedding retained; no re-admission or potential redesign |

No narrow mathematical repair or foundation conflict was found in this
reconstruction. These are classifications in a new candidate report; no source
file or authority wording is amended.

### 21.1 Where the master theorem already contains the answer

| M location | Content recovered here |
|---|---|
| §3, A1/A2/A6 and the base after the assumption table | Joint state, finite scalar and event boundary precede orientation |
| §3, A5; §19 branch-status table | Orientation is an added claim, necessary only for the chosen certificate |
| U1, §4 | Complete recursively evaluable action total; no second settlement from additional descriptions |
| U2, §5, equation (3) | Exact factor sums, unchanged total under legitimate refactorization |
| U2, §5, equation (4) | SF/TA/BT predicates; explicit statement that A5 is not needed for the other identities |
| U3, §6 | Positive calibration covariance and agreement after root conversion |
| U4, §7, equations (5)–(6) | Joint path pairing, vector context and event registration boundaries |
| U8, §11, equation (19) | Exact finite quadratic correction |
| U11, §14, equation (28); §§14.2–14.3 | Nonempty Möbius transform, affine/quadratic bound, nonlinear response and actual sequential endpoints |
| U11b, §14.4 | Optional supplied-generator path and expected-value interface |
| U12, §15 | Conditional canonical scale, covariance and entropy branches |
| U13, §16, equations (34)–(36) | Action/passive telescoping and conditional ledger closure |
| U14, §17 | Compatibility under separately named hypotheses rather than universal implications |
| §23 | The over-broad global decision wording to clarify, while keeping its mathematical regime table |

The explicit `S`-matrix formulation and coordinate-covector language foreground
existing chain-rule content. They do not require revising the cleared master
proofs. The substantive new output is the logically narrower framing of the
human sign decision, together with an unambiguous vocabulary for the three
kinds of marginal.

## 22. Proposed canonical formula set and terminology

This compact presentation is **subject to independent audit**, not a replacement
for the frozen finite definition. All symbols carry the domain, units, response
and regularity qualifications established above:

\[
\begin{aligned}
\mu(z)&=\nabla_zV(z), & dV&=\sum_j\mu_j\,dz_j,\\
s_a(z)&=\left.\partial_q A_{a,q}(z)\right|_{q=0}, & f_a(z)&=-dV_z(s_a(z)),\\
dz&=S(z)\,dq, & f(z)&=-S(z)^{\mathsf T}\mu(z),\\
\mathcal E_a(z)&=V(z)-V(A_a z), &
\mathcal P(z)&:\ a\in\mathcal A(z)\longmapsto\mathcal E_a(z),\\
E_a&=-\int_\Gamma dV=\int f_a\,dq, &
E_{\rm quad}&=-\mu_{\rm pre}^{\mathsf T}\Delta-\tfrac12\Delta^{\mathsf T}H\Delta,\\
dV&=\nabla_xV\cdot dx+\nabla_\lambda V\cdot d\lambda, &&\\
\widetilde z_n&=A_{a_n}(z_n,\xi_n^a), & z_{n+1}&=P(\widetilde z_n,\xi_n^p),\\
E_n&=V(z_n)-V(\widetilde z_n), & D_n&=V(\widetilde z_n)-V(z_{n+1}),\\
\Delta C_n&=E_n, & \Delta(C+V)&=-D_n,\\
E(C)&=V(z_\varnothing)-V(z_C), &
m_E(T)&=-\Delta_T(V\circ z_\bullet)(\varnothing),\quad T\ne\varnothing.
\end{aligned} \tag{32}
\]

In the local finite-action derivative use `∂_q A_{a,q}(z)|₀` and evaluate
`dV` at `z`; along an extended action path evaluate both at the current
`A_{a,q}(z)`. For a nonlinear multi-extent response substitute `S=J_R(q)`.
The relative coalition table has `m_E(∅)=E(∅)=0`; a raw drifting empty value
must instead be retained or explicitly centered. Ledger equations apply only
when the declared registration/allocation conditions hold. No passive actor
issue, policy choice or market-price law is encoded by this display.

| Symbol | Recommended term | Status / reason |
|---|---|---|
| `V` | EBU potential; joint potential when emphasizing scope | Canonical symbol; do not protect a universal “burden” interpretation |
| `z` | Complete current physical state, or admitted extended state | Includes sufficient physical context and memory |
| `λ` / context `θ` | Field/context coordinates | Distinct from a retained state called `θ` in some reduction statements |
| `μ` | Local marginal potential; marginal-potential components | B's existing term; intrinsically the components of `dV` |
| `s_a` | Action direction per extent | Physical response, not a price or motion law |
| `S` | Action response matrix; incidence matrix in the stoichiometric case | Existing historical construction, generalized cautiously |
| `f_a` | Directional differential value; local marginal action value per extent | Preserves B's meaning; avoids unqualified “force” |
| `f` | Marginal action-value vector | Column of action-space covector components for a declared family |
| `E_a`, `ℰ_a` | Exact finite action EBU | Controlling endpoint value |
| `𝒫(z)` | Current EBU action map / finite action-value map | Labelled map, newly foregrounded terminology pending audit |
| `E(B|A)` | Contextual finite marginal action value | Distinct from state derivative and local slope |

“EBU price field” can be misunderstood as a market-price or historical-price
storage object. Prefer the action-map terms. “Generalized field” does not
identify which of state, covector or action map is meant, and “marginal EBU
vector” loses the state-versus-action distinction. No canonical symbols are
renamed, and no mechanical-force terminology is needed here.

## 23. Verification, coverage and audit handoff

### 23.1 Verification boundary

Validation is restricted to source inspection, hashing, exact algebra and
arithmetic on explicitly displayed mathematical objects, document structure,
and Git scope checks. No source model was imported or stepped. There was no
trajectory, generator integration, Monte Carlo, seed consumption, optimization,
parameter fitting, apparatus operation or scientific experiment.

The validation certificate in Appendix B records the completed static checks.
These are author checks, not the independent audit requested next. The source
hash ledger permits an auditor to identify all dependencies without relying
on conversational memory. Existing scientific documents remain byte-identical.

### 23.2 Coverage of every substantive request

| Brief section(s) | Report location |
|---|---|
| 0–2: coordinate, question, authority and historical sources | §§1–3, Appendix A |
| 3–7: marginals, direction, loss and covectors | §§4–5 |
| 8–9: finite rule and quadratic correction | §6 |
| 10–12: vector context, current field and unified local field | §§8–10 |
| 13–15: factors, nonseparability and interactions | §11 |
| 16–18: synergy, sequential marginals and finite interactions | §§12–13 |
| 19–21: decomposition, settlement and original architecture | §§9–11, 16–17 |
| 22: monitoring role | §18 |
| 23–28: incidence, nonlinear response, action maps and feedback | §§7, 9 |
| 29–31: root and localism | §14 |
| 32–37: regimes, global choice and sign semantics | §§15–16 |
| 38–40: table, unified principle and continuity | §§13, 17 |
| 41–42: SF/master relationship | §§15.2, 21 |
| 43–44: E1a and W1 | §20 |
| 45–47: data outputs, health and current action map | §§9, 18 |
| 48: apple example | §19 |
| 49–50: primary verdict and human sign decision | §§1, 15.2, 24 |
| 51–54: formulas, terminology and theorem/foundation impact | §§21–22 |
| 55–57: deliverable, completion fields and verdict | §24, completion response and enclosing commit |

### 23.3 Focus of the next bounded task

The next task is **one independent audit of this report**, not yet begun.
Its key questions are whether the global-choice narrowing follows from the
cleared optional A5 structure; whether local/finite and state/action marginals
stay distinct; whether the covariance, loss and nonlinear-response formulas
are correct; and whether W1's actual refusal and uncertified factor status
remain intact. The source/total independence examples, noncommuting response,
finite sign reversal and localism counterexamples are adversarial audit targets.

No human scientific decision is needed to finish this reconstruction. A future
application that asserts a source or total orientation still needs its named
physical claim, domain and certification conditions. That is a future
application obligation, not an unresolved global choice blocking the present
valuation mathematics. No such policy has been selected here.

## Appendix A. Exact source identities

The following committed working-tree files were hashed before drafting and
rechecked after the mathematical validation. References are defined in §2.
The eight scientific dependencies F through M are the brief's controlling
sequence; W1 and the historical sources provide the additional interfaces.

| Reference | SHA-256 |
|---|---|
| AGENTS | `168307e07f79d980a5545bc4283619f44e5ba54eb750212783daf65356bb2e94` |
| F | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| B | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| R | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| MG | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| S | `5b92fdf5749ee05db63f32320e2b34a10afa2c98ceaf2e7a996f78b2df60505f` |
| RF | `685b90eb6acef40b5a8277a9652ef3dceaf4017f91c47df3853a75e2a7f139e3` |
| SF | `547de25e1c847bca29c894fbc68def76162ea4b27d1b21dfae54670ce7124f3e` |
| M | `634bfc654a1f54f0fe537559f324aba58423e008b9d71182f8a71d2b9200b8cf` |
| W1 | `382df7347f162006450c60cea44e00d6e8b54115d8b0182ca6dee450752611e7` |
| FB | `a18d11d309efcb4490e8dc0b7a86a327026c0a58a755e649722d9a9071882c18` |
| SP | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` |
| H28 | `e5e2eb523a2da34fe0d248ce564a0b7f37d13bb0da6c56370a98413622cf3fe4` |
| H27 | `4f0de05073760ba280c4f82f9e3036f8de248e1033a180ce87742d336a4547df` |

The historical stock note has Git blob `0abb01f86d47b77ff3f96a0a9ece31c7a896f963`
at the snapshot in §2.1 and SHA-256
`dd2643defbe78d774c225a07b8d89f0a36fca62dd33af36bd370cd202d9462a3`.
Its retrieved bytes were read as reference material, not restored into the
checkout. No synced project reference, source report or historical object was
modified.

## Appendix B. Completed static validation certificate

**60 exact symbolic/rational checks passed.** These checks used a temporary,
standard-library polynomial/Fraction calculation, independent of repository
model code. Coefficient equality was used for the polynomial identities;
rational arithmetic was used for the displayed finite witnesses. The scratch
checker is not a production implementation and is not part of the commit.

| Group | Checks | Completed scope |
|---|---:|---|
| Loss direction and finite sink example | 9 | Signs, carrier sum, omitted term, lossless nonzero sink marginal, full/reduced slopes, exact finite polynomial, sign reversal and derivative limit |
| Differential/quadratic/calibration algebra | 8 | Symbolic general two-coordinate quadratic with arbitrary coefficients, exact line integral, remainder, coordinate and action-extent reparameterization, positive affine covariance |
| Moving context | 3 | State part `−4`, context part `−7/2`, complete drop `−15/2` |
| Coupled factors and sequential values | 12 | Gradient and action slope, factor closure, finite total, standalone/rebased values and pair coefficient in §11–§12 |
| Nonlinear response | 11 | Two Jacobian pullback components, four composite Hessian entries, integrated mixed derivative, finite-response acceleration terms and both noncommuting endpoint values |
| Möbius identities and order boundary | 5 | Quadratic-affine zero triple, quadratic-nonlinear `−18`, cubic-affine `−6`, complete-table inversion and contextual recursion |
| Sign predicates | 3 | All three SF/TA/BT countermodel rows, including their source and residual arithmetic |
| Localism and state sufficiency | 5 | Both finite localism values, an unchanged projection, equal potential levels with different next-action values |
| Event/accounting identities | 2 | Action-plus-passive telescoping and passive ledger remainder |
| W1 differential interface | 2 | Cancellation of water/drive differential terms and the endpoint bath-energy ratio; logarithm sign follows analytically from monotonicity |
| **Total** | **60** | **All passed** |

The proofs in the body establish the general claims under their assumptions;
a finite collection of checks is not substituted for those proofs. The
arbitrary three-label table used to check inversion was
`E(∅),E(1),E(2),E(12),E(3),E(13),E(23),E(123) = (0,2,−1,4,3,8,−2,6)`.
The nonlinear response check used
`R(q,r)=(q+r²,qr)`, `V(x,y)=x²/2+y²/2+xy/2`, differentiating its polynomial
composite exactly. No response model was numerically advanced.

Additional completed document checks: all 14 working-tree reference hashes
matched; the historical Git blob matched; all 32 numbered equation tags were
present once and in order; display-math and code fences balanced; every local
Markdown source link resolved; no draft placeholders remained. These are
structural checks, not a claim of a typeset PDF build. Only Markdown was
requested and authorized.

Final exact-path staging, complete diff review, whitespace validation and
clean-tree verification are recorded by the enclosing commit and completion
response. No experiment or independent audit was performed by this task.

## 24. Final disposition

The original architecture is recovered with its authority boundaries intact:
current complete field → local marginal potential + physical action response
→ scalar directional slope / exact finite endpoint value → registered closing
allocation → updated physical field → new valuations from that field.
Historical balances remain historical. Smoothness, factorization, coalitions,
root traceability and sign certificates enter only where their specific claims
need them.

```text
PRIMARY CONCLUSION: A
GLOBAL SF / TA / BT CHOICE: NOT REQUIRED
HUMAN SCIENTIFIC DECISION REQUIRED FOR THIS RECONSTRUCTION: NONE
NEXT BOUNDED TASK: INDEPENDENT AUDIT OF THIS REPORT — NOT BEGUN
FOUNDATION: UNCHANGED — NO FOUNDATION CHANGE REQUIRED
R: UNCHANGED
S-MG: UNCHANGED
S: UNCHANGED
RECURSIVE FIELD THEORY: UNCHANGED
SOURCE-FACTOR THEORY: SEMANTIC CLARIFICATION ONLY
MASTER THEORY: SEMANTIC CLARIFICATION ONLY
W1: UNCHANGED
AUTHORITY MODIFIED: NO
EXPERIMENTAL DESIGN MODIFIED: NO
CODE MODIFIED: NO
MONTE CARLO: NO
PHYSICAL EXECUTION: NO
PUSH: NO
```

A. SF / TA / BT ARE SECONDARY CERTIFICATION PREDICATES;
UNIFIED JOINT-FIELD VALUATION IS PRIMARY

EBU UNIFIED MARGINAL-VECTOR / DIRECTIONAL-ACTION SEMANTICS:
RECONSTRUCTION COMPLETE
