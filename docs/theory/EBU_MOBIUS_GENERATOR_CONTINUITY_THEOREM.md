# EBU — Möbius–generator continuity theorem programme

Report date: 2026-10-05. Stage: **S-MG**, report-only.

```text
STATUS:                     NON-CONTROLLING THEORETICAL CANDIDATE
R-STAGE:                    INDEPENDENTLY CLEARED (user-supplied audit disposition)
SCIENTIFIC AUTHORITY:        UNCHANGED
BOOK 1:                     NOT MODIFIED
IMPLEMENTATION:              NONE
SCIENTIFIC EXECUTION:        NONE
CURRENT E1a-v4:              PRESERVED / PAUSED
EXECUTION AUTHORISED:        FALSE
INDEPENDENT THEOREM AUDIT:   REQUIRED BEFORE BOOK 1 INTEGRATION
NO NOVELTY CLAIM IS AUTHORISED BY THIS REPORT.
```

Theorems below are mathematical candidates with explicit hypotheses, independently derived
here and checked by exact algebra. They are not independently audited results, a new
preregistration, or physical evidence. The frozen foundation controls if wording conflicts.
The accompanying [prior-art appendix](EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md) records
source access, equation-level comparison, search coverage and limitations.

## 1. Executive result

**The continuity chain exists as a hierarchy of conditional identities.** Its unconditional
finite core is ordinary Möbius inversion applied to a declared coalition value table. A
physical transition map supplies that table; a generator is one possible way to obtain the
transition map. Smoothness, additivity, equilibrium density and entropy accounting enter at
different points and must not be silently inherited by the entire chain.

For a fixed field, a finite Boolean coalition domain, and the canonical sign convention,

\[
E(S)=V(x_0)-V(x_S),\quad x_\varnothing=x_0,\quad
m_E(T)=\Delta_T E(\varnothing)=-\Delta_T(V\circ x)(\varnothing)
\qquad(T\ne\varnothing).
\tag{1}
\]

These coefficients give the exact, unique multilinear expansion of the Boolean values.
With additive displacements they are negative physical mixed finite differences of `V`;
with adequate regularity those are integrals of mixed derivatives. A quadratic potential
has no interaction above order two **only when the endpoint map is affine in the action
indicators**. A quadratic potential composed with a nonlinear response can have every
interaction order.

A well-posed controlled flow makes (1) an immediate generator–flow–Möbius composition.
It does not supply a new law of motion, an actor transaction, or a proof of equilibrium.
If independently justified canonical density satisfies `p ∝ exp(−V)`, the same coefficients
are alternating log-probability contrasts. Under the *additional* accepted P4 benchmark
conditions, medium-entropy coefficients equal `k_B m_E`. Density agreement alone does not
establish reversibility or that entropy interpretation.

The core mathematics is established prior art. The strongest direct antecedents are
Grabisch–Marichal–Roubens for set functions and multilinear derivatives, and Jansma for
energy/probability Möbius interactions. Controlled-flow composition and higher chain rules
are direct applications of existing calculus and control theory. The possible EBU-specific
contribution is an architecture joining these objects to registered physical actions,
independent scale calibration and preserved historical accounts; this report establishes
neither novelty nor empirical success for that architecture.

## 2. Authority / provenance reconstruction

### 2.1 Starting coordinate and clearance provenance

| Item | Verified coordinate or disposition |
|---|---|
| Repository | `/Users/konrad.grzyb/code/ebu` |
| Branch | `gaussian/stage-a-environment` |
| Starting HEAD / R-stage repair | `6c1d0822790dc98e249a30ff5e8fa28202723e82` |
| Starting / audited tree | `eef3a510b0fc8227e57d02dd896a19cd388c426a` |
| Starting worktree | Clean |
| Live remote branch HEAD, read during S-MG | `dd0d6b0e5d370de1bda805e07215ea0be4d6d083` |
| R1–R6 clearance | Supplied explicitly in the current task; no material blocker, foundation amendment or human decision required for R-stage |
| Independent audit artifact | The current user brief supplies the disposition; this task does not claim to have performed that audit or recovered an additional committed audit file |

The R-stage report retains its historical “ready for re-audit” text. This task leaves it
unchanged and records the subsequent user-supplied clearance here. The repaired HEAD/tree
match the brief exactly. The enclosing new commit identifies this report's final revision;
no impossible self-referential commit hash is placed inside its own preimage.

### 2.2 Controlling sources and relevant historical sources

Authority order from [AGENTS.md](../../AGENTS.md): frozen foundation, working baseline,
then exploratory reports. The foundation, metadata, baseline and repaired R-stage were
read in this conversation; their exact bytes were rechecked at this stage. Current relevant
sections were inspected again before derivation.

| Source | What it establishes here; limits |
|---|---|
| [Canonical foundation](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md), §§3, 12–18, 21–27 | `E=V_pre−V_post`; `C¹` fixed-field path identity; rebasing; subset decomposition; quadratic **and** additive order bound; attribution not unique; entropy conditional |
| [Freeze metadata](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.meta.json) | Frozen bytes and canonical SHA-256, not a new scientific gate |
| [Theory baseline](EBU_THEORY_BASELINE.md), §§concerning E1a and equation/status register | Dimensionless physical potential; independent bridge calibration; preserved prospective study boundaries |
| [Cleared R-stage reconstruction](EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md), §§2, 6, 9–14, 25 | Path/field/density/reversibility/entropy distinctions; fixed-field versus cross-field denomination |
| [E1a-v4 design](../e1a/E1A_V4_PROSPECTIVE_DESIGN.md), §§8–9; [contract](../e1a/e1a_v4_design_contract.json) | Conditional benchmark entropy interpretation and independent branches; no evidence that experiments ran |
| [Sequential–parallel bridge](../../SEQUENTIAL_PARALLEL_BRIDGE.md), §§4–7 | Telescoping; named serial comparator; same-baseline nonadditivity as a **different** object |
| [Conservative-world candidate](../../CONSERVATIVE_WORLD_ADOPTION_PACKAGE_CANDIDATE.md), current-scope notice, A.3, C.5, F.1–F.10, G.1 | Prospective, not adopted, superseded as active first-study design; historical force/flux/opposition gaps; W0 excludes joint action |
| [Predecessor design](../../CONSERVATIVE_WORLD_FOUNDATION_DESIGN.md) and [candidate review](../../CONSERVATIVE_WORLD_ADOPTION_PACKAGE_REVIEW.md) | Earlier overstrong “not applicable” wording was narrowed to missing registration; this is not physical refutation |
| [SD-03 readiness](../../SD_03_PRE_EXECUTION_READINESS.md), §4 | Historical `Ψ_e` is accumulated opposition; `G_T` is a state-transformation generator; no constitutive edge law registered for W0 |
| [SD master register](../../SD_01_TO_14_MASTER_TEST_REGISTER.md), SD-03–07 | Generator, order, interaction, subset-lattice and motif responsibilities; historical readiness labels are not current execution permission |
| [Foundation v2.7](../../Foundation_v2.7_math.md), §2; [v2.8 discrete draft](../../Foundation_v2.8_discrete_draft.md) | Historical force–dissipation–flux and incidence concepts; not controlling current dynamics |
| [Physical action source](../../demand_driven_ebu/physical.py), `PhysicalAction.increment`, `PlanGroup.increment`, `can_happen_now` | Static example of fixed additive increments including loss sinks and source-funded feasibility; no code imported or executed |
| [Current navigation](../../CURRENT_SCIENTIFIC_AUTHORITY.md), [programme reconciliation](../../LOCAL_GAUSSIAN_EBU_PROGRAMME_RECONCILIATION.md), [book architecture](../../EBU_FUTURE_BOOKS_STRUCTURE.md) | Historical programmes remain historical; current eight-part editorial map; motif reuse is conditional and not causality |

Off-branch history was read directly from immutable Git blobs, not imported as active
checkout authority: `ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md` at blob prefix
`82b82d3d`, especially F5 and F13–F16; and
`ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md` at `875f069b`, §§3–4 and
finite-interaction/mixed-marginal/commutator declarations. Their exact signed inversion,
explicit possibly nonzero empty baseline, frozen subset protocol, quantity-fixed versus
rule-replayed semantics, and commutator orientation agree with the distinctions used below.
The motif programme was also inspected at commit
`4e1f5bac478bc60554d1980208b7cd92883b2b85`, file
`CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION.md`, blob
`7c90cfc10aba9c44d07a5bd2c86b20dfaf562339`, §§3–5 and 8. Its separate structural
layers, joint A1–A8 reuse conditions and black-box subset-query bound remain historical
prospective material. The atomic source full blob identifiers are
`82b82d3d6824adcfe071a19bc0b530417f592eab` and
`875f069b189c07af458ec7816289dad27eed3744`, respectively.
These are historical source coordinates, not newly adopted authorities. Section 21 gives
specific reconciliation instead of treating all historical documents as one simultaneous
scientific state.

### 2.3 Registration invariant

At a valuation event, one current field prices one new registered allowed action or declared
coalition. Physical evolution, a flow, waiting, or a `dθ` contribution does not by itself
create an actor EBU transaction. Historical entries are never repriced. Physical interaction,
causal attribution, actor credit and settlement are separate objects. No payment rule is
introduced here. All principal theorems below are fixed-field; cross-field denomination is
separate future work.

## 3. Definitions

Fix a field `θ`, omitted from formulas when unambiguous. Let `N={1,…,n}` be a finite set
of labelled actions. Freeze a subset protocol: baseline `x₀`, state coordinates and boundary,
action meanings/quantities, horizon, external conditions, admissibility, shared-constraint
resolution, and potential/units. Every required `S⊆N` has a defined endpoint `x_S` and value
under this same protocol. Physical interpretation requires every relevant intervention to
be admissible; a mathematical completion of missing values is not an experiment.

Define `x_∅=x₀`, `G(S)=V(x_S)`, `E(S)=G(∅)−G(S)` and

\[
c_T(S)=(-1)^{|T|-|S|}\quad(S\subseteq T),\qquad
m_E(T)=\sum_{S\subseteq T}c_T(S)E(S).
\tag{2}
\]

`E(∅)=m_E(∅)=0` follows from the stated endpoint assumption; it is not imposed on a
historical drift/cost model with nonzero empty value. For an arbitrary set function `F`,
`m_F(∅)=F(∅)`. The foundation's `v(S), I(T)` correspond here to `E(S), m_E(T)`.
For `i∉S`, define `Δ_iF(S)=F(S∪{i})−F(S)`; products `Δ_T` use distinct indices.
A context `S` and differentiated set `T` are always disjoint. All differences use addition
of a label, never removal/reversal without explicitly changing the formula.

No continuity, differentiability, additivity, equilibrium, Gaussianity or generator is
required for (2). Repeated endpoints are allowed. Arbitrary labels can be actor actions,
transitions or declared bundles; their institutional meanings are additional declarations.

A Boolean cube is a domain assumption. If only a feasible poset `P` exists, its inversion
uses its own incidence-algebra function `μ_P`; the Boolean signs cannot simply be retained.
For instance, an undefined `E(AB)` leaves `m_AB` undefined even if `E(A)` and `E(B)` exist.
Any value assigned to the missing corner produces a different coefficient.

## 4. Coalition finite-difference theorem

**Theorem A (finite coalition identity).**

**Assumptions and definitions.** Section 3's finite, complete subset table; real finite
values. For the potential version also `E=G(∅)−G`.

**Statement.** For every `T`, `m_E(T)=Δ_T E(∅)` (the empty operator is identity).
For nonempty `T`,

\[
m_E(T)=-\Delta_T G(\varnothing).
\tag{3}
\]

**Proof.** Let `U_i` add label `i`. On a subcube where the label is absent,
`Δ_i=U_i−Id`. Distinct `U_i` commute. Expanding
`∏_{i∈T}(U_i−Id)` chooses `U_i` exactly for a subset `S⊆T`; its sign is
`(−1)^{|T|−|S|}`. Evaluation at `∅` gives (2). For nonempty `T`, the constant term
has coefficient `Σ_{S⊆T}c_T(S)=(1−1)^{|T|}=0`, proving (3). ∎

**Removed-assumption check.** Missing corners make the sum undefined, not zero.
At `T=∅`, the potential formula would give `−G(∅)` instead of `E(∅)=0`, so its
nonempty restriction is essential. Changing the sign of the valuation changes every
coefficient's sign.

**Intuition.** An interaction is the part of a combined effect that survives successive
subtraction of effects visible on the faces of its action cube.

**Prior art / EBU status.** Known Möbius/discrete-derivative identity, with the frozen EBU
orientation substituted. [Grabisch–Marichal–Roubens, §§1–3](https://ikojadin.perso.univ-pau.fr/kappalab/pub/GraMarRouMOR2000.pdf).
Non-controlling derivation; no additional issuance, physical conservation or ownership claim.

## 5. Exact discrete-Taylor representation

**Corollary A2 (unique pseudo-Boolean multilinear representation).**

**Assumptions and definitions.** Any real `F` on all vertices of `{0,1}ⁿ`; identify a
vertex with its support and define `z_T=∏_{i∈T}z_i`, `z_∅=1`.

**Statement.**

\[
F(z)=\sum_{T\subseteq N}m_F(T)z_T,\qquad
E(z)=\sum_{\varnothing\ne T\subseteq N}m_E(T)z_T.
\tag{4}
\]

This is exact on the vertices, with **no remainder, no small-action approximation, and
no continuum assumption**. The same polynomial is the unique *multilinear* extension
to the cube, but need not equal a physical response interpolation there.

**Proof.** At vertex `1_S`, the right side is `Σ_{T⊆S}m_F(T)`. Substitution of (2)
gives the coefficient of `F(R)` as
`Σ_{R⊆T⊆S}(−1)^{|T|−|R|}=(1−1)^{|S\R|}`, hence only `R=S` remains.
For uniqueness, if the difference of two expansions vanishes at all vertices, its constant
coefficient vanishes at `∅`; induction on subset size then forces each remaining coefficient
to vanish. ∎

**Removed-assumption check.** Without multilinearity, infinitely many extensions exist:
adding `z₁(1−z₁)` leaves every vertex unchanged. Without a complete table, uniqueness of
all coefficients fails. A nonzero `F(∅)` cannot be dropped.

**Intuition / terminology.** The product `z_T` switches on when all members of `T` are
present. Preferred name: Möbius or pseudo-Boolean multilinear expansion; for normalized
coalition games the coefficients are **exactly Harsanyi dividends**. “Discrete Taylor” is a
useful pedagogical description with this basis and base vertex stated. It is not an ordinary
truncated Taylor series, a Walsh expansion in ±1 variables, or a Shapley allocation.

**Prior art / EBU status.** Standard result, explicitly linked to Harsanyi dividends in
[Grabisch–Marichal–Roubens, Eq. (8)](https://ikojadin.perso.univ-pau.fr/kappalab/pub/GraMarRouMOR2000.pdf).
See appendix references R1–R5. No new mathematics claimed.

## 6. Recursive interaction theorem

**Corollary A1 (contextual recursion).**

**Assumptions and definitions.** A complete table; disjoint `S,T`; `i∉S∪T`.

**Statement.**

\[
\Delta_{T\cup\{i\}}E(S)
=\Delta_T E(S\cup\{i\})-\Delta_T E(S),\qquad
\Delta_T E(S)=\sum_{R\subseteq S}m_E(T\cup R).
\tag{5}
\]

For a single `A`, `Δ_AE(S)` is its marginal value in context `S`. A pair is the change
in that marginal caused by `B`. A triple is the change in the `A–B` pair caused by `C`.
At order `k`, one measures the change in a `(k−1)`-way interaction upon adding the last
label. The empty-context value is `m_E(T)`; a different background can change it.

**Proof.** The first identity is the definition of the final difference and commutation
of distinct additions. Apply `Δ_T` to (4): a monomial survives only if it contains every
index in `T`; at background `S` its remaining indices must lie in `S`. This gives the
second identity. ∎

**Removed-assumption check.** If `T={A,B}` and `m_ABC≠0`, then the pair in context
`{C}` is `m_AB+m_ABC`, not `m_AB`. If an index is already present, the stated distinct-label
interpretation is unavailable. A background-averaged interaction is a different statistic.

**Intuition / prior art / EBU status.** This is the standard reference-context epistasis
recursion and set-function derivative. It explains the EBU coefficient without claiming
causal influence or statistical dependence; [Poelwijk et al.](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004771)
and appendix R3/R6 give the prior-art distinction between anchored and averaged interactions.

## 7. Sequential–parallel bridge

**Proposition SP (rebased endpoint bridge).**

**Assumptions and definitions.** One fixed potential and declared endpoints `x₀,x_A,x_B,x_AB`.
Define the *contextual endpoint difference*
`E(B|A)=V(x_A)−V(x_AB)` and analogously `E(A|B)`. Calling these actual sequential
execution values additionally requires the corresponding execution maps to reach `x_AB`.

**Statement.**

\[
E(A)+E(B\mid A)=E(AB),\qquad
m_{AB}=E(B\mid A)-E(B)=E(A\mid B)-E(A).
\tag{6}
\]

For a nested chain `∅=S₀⊂S₁⊂⋯⊂S_n=N`, contextual differences telescope to `E(N)`.

**Proof.** Insert the four potential values. Intermediate levels cancel in the sum;
subtract the same-base single-action value to obtain `E(AB)−E(A)−E(B)`, which is
`m_AB` because `E(∅)=0`. The chain is the same cancellation repeated. ∎

**Removed-assumption check.** If actual `B` after `A` reaches `y_AB≠x_AB`, the actual
second value is `V(x_A)−V(y_AB)`. Its deviation from the same-base `E(B)` equals
`m_AB−[V(y_AB)−V(x_AB)]`. The bracketed quantity is the bridge document's named
parallel-versus-serial comparator, not the Möbius coefficient. Equality of final potential
levels is sufficient for equality of values, though not for equality of physical states.
Field changes between steps invalidate cancellation of a single fixed `V` unless all
field-change terms are included as in the R-stage report.

**Conservativity check.** Take `V(x)=x²/2`, `x₀=0`, two unit translations. All path integrals
between 0 and 2 equal `−2`. Yet `E(A)=E(B)=−1/2`, `E(AB)=−2`, and `m_AB=−1`.
The actual rebased second value is `−3/2`. Synergy compares **different counterfactual
endpoints**; path independence compares **the same endpoint pair**. Thus nonzero synergy
is fully compatible with an exact conservative potential.

**Intuition / prior art / EBU status.** Standard telescoping and discrete differentiation;
foundation §§12, 14 and the historical bridge establish the EBU distinctions. For more than
two actions, same-base group nonadditivity is `Σ_{T⊆N, |T|≥2}m_E(T)`, not just `m_E(N)`.
No individual attribution convention is selected.

## 8. Additive coalition-state theorem

**Theorem B (physical mixed finite differences).**

**Assumptions and definitions.** Section 3 plus fixed vectors `h_i` in a finite-dimensional
real vector space, `x_S=x₀+Σ_{i∈S}h_i`. All vertex values are in `V`'s domain. Write
`Δ_hV(x)=V(x+h)−V(x)`.

**Statement.** For nonempty `T={i₁,…,i_k}`,

\[
m_E(T)=-\Delta_{h_{i_1}}\cdots\Delta_{h_{i_k}}V(x_0).
\tag{7}
\]

**Proof.** Expanding the commuting physical translations gives the same alternating sum
of `V(x₀+Σ_{i∈S}h_i)` as Theorem A. ∎

**Removed-assumption check.** With `V=x²/2` and `x(z)=z₁+z₂+z₃+z₁z₂`, Theorem A
gives a triple `−1`, whereas the fixed three unit translations in (7) give zero (§20).
A resolver that changes a previously accepted quantity when another action joins is not a
fixed-increment map.

**Intuition / prior art / EBU status.** Labels translate the physical state by fixed vectors,
so their Boolean differences become ordinary directional finite differences. This is a
direct substitution into standard finite-difference calculus, and includes the canonical
quadratic setting as a special case. No vector independence or positive increments are
needed; repeated or opposite directions are allowed.

## 9. Repeated-FTC representation

**Corollary B1 (parallelotope integral).**

**Assumptions and definitions.** Theorem B; `V∈C^k(U)` on an open neighborhood `U` of
`P_T={x₀+Σ_{r=1}^k t_r h_{i_r}:0≤t_r≤1}`. Coordinates are finite-dimensional.
The parallelotope may be degenerate. Only its containment is needed; `U` need not be
convex or simply connected.

**Statement.**

\[
m_E(T)=-\int_{[0,1]^k}
D^kV\left(x_0+\sum_{r=1}^k t_rh_{i_r}\right)
[h_{i_1},\ldots,h_{i_k}]\,dt.
\tag{8}
\]

**Proof.** Put `g(t)=V(x₀+Σt_rh_{i_r})`. One-variable FTC gives the difference in the
first coordinate as the integral of `∂₁g`. Repeat for each remaining coordinate. Continuity
of the mixed derivatives on the compact cube permits changing integration order. The
chain rule for an affine map gives `∂₁⋯∂_k g=D^kV[h_{i₁},…,h_{i_k}]`. Equation (7)
supplies the minus sign. Symmetry follows from `C^k` mixed-partial symmetry, not from
an assumption that distinct actions are physically identical. ∎

**Weaker clean hypothesis.** It suffices that the pullback `g` is `C^k` near the cube,
even if `V` is less regular in unused directions. More generally, fix a differentiation
order and require the successive coordinate derivatives to have absolutely continuous
one-dimensional sections, with compatible face traces and integrable mixed derivative,
so that every successive FTC step and Fubini interchange above is valid. This explicit
iterated-FTC condition is weaker than `C^k`; there is no unique “weakest” regularity class
being asserted. Mere existence of an almost-everywhere mixed derivative is insufficient.
For `k=1`, the Cantor function has derivative zero almost everywhere but endpoint difference
one; absolute continuity is the missing property. Its product with the other coordinates
supplies higher-dimensional counterexamples.

**Removed-assumption check.** Knowing only vertex values cannot determine an integral
through a hole where the potential is undefined. Nonsmooth switches may preserve the exact
finite theorem while invalidating this classical derivative formula.

**Intuition / prior art / EBU status.** A finite interaction is the average mixed response
over the whole action parallelotope, with the displacement vectors included. This is
repeated FTC, not a new EBU theorem of calculus; the derivative interpretation is a
conditional extension of the finite foundation.

## 10. Continuous Taylor connection

**Corollary B1a (small-action asymptotic with proved remainder).**

**Assumptions and definitions.** Fixed directions `d_i`, `h_i=εd_i`, `ε→0`, with all
sufficiently small parallelotopes inside a neighborhood of `x₀`. Let `k=|T|≥1` and
`V∈C^k` there. Norms below are consistent vector/operator norms.

**Statement.**

\[
m_E(T)=-\varepsilon^kD^kV(x_0)[d_{i_1},\ldots,d_{i_k}]+o(|\varepsilon|^k).
\tag{9}
\]

If `D^kV` is locally Lipschitz with constant `L`, then the remainder `R` obeys

\[
|R|\le {L\over2}|\varepsilon|^{k+1}
\left(\sum_{i\in T}\|d_i\|\right)\prod_{i\in T}\|d_i\|.
\tag{10}
\]

Thus `C^{k+1}` is a simple sufficient condition for `O(|ε|^{k+1})`, and local Lipschitz
continuity of `D^kV` is enough. This is a sufficient condition, not a necessary one for
special directions or cancellations.

**Proof.** Substitute `εd_i` into (8) and subtract the integral with constant integrand
`D^kV(x₀)`. If `ω(r)` is a local modulus of continuity of `D^kV`, the absolute remainder
is bounded by
`|ε|^k ω(|ε|Σ‖d_i‖)∏‖d_i‖`, proving (9). Under Lipschitz regularity, use
`‖Σt_i εd_i‖≤|ε|Σt_i‖d_i‖` and `∫t_i dt=1/2` to obtain (10). ∎

**Removed-assumption check.** `C^k` alone does not give the extra power. For any `k≥1`
and `0<α<1`, take `V(x)=x_+^{k+α}`, `x₀=0`, `k` identical positive unit directions.
Its `k`th derivative is continuous and zero at 0, but the finite difference is a nonzero
constant times `ε^{k+α}` for `ε>0`. Nonzero follows also from (8), since the `k`th derivative
is positive away from zero. It is not `O(ε^{k+1})`.

**Intuition / prior art / EBU status.** Small actions sample local mixed curvature;
finite actions sample its integral over a region. Ordinary Taylor asymptotics approximate
the physical landscape. Equation (4) exactly reconstructs the Boolean table at every
fixed `ε`. These are different statements. This is standard calculus applied to EBU.

## 11. Polynomial-degree theorem

**Corollary B2 (degree ceiling and its sharper restriction).**

**Assumptions and definitions.** An affine map `x(z)=x₀+Az` and a polynomial
potential of total degree at most `d`. The columns of `A` are the action displacements.
Let `q(z)=V(x₀+Az)`.

**Statement.** `m_E(T)=0` whenever `|T|>d`. More sharply, replace `d` by the degree
of `q`, or by the degree of its unique Boolean reduction `q̄` obtained by replacing every
positive exponent of each `z_i` by one and collecting coefficients. The sharp ceiling is
`deg q̄`; cancellations after collection matter. If `D^kV` annihilates the selected directions
throughout their parallelotope, (8) also gives that selected coefficient zero without global
polynomiality.

**Proof.** Affine substitution cannot increase total degree. On Boolean vertices,
`z_i^r=z_i` for positive integers `r`. Boolean reduction cannot increase degree either.
The coefficient of `z_T` in `q̄` is `−m_E(T)` for nonempty `T`, by uniqueness in (4).
No monomial of degree above these bounds remains. ∎

**Removed-assumption check.** Quadratic `V` with nonlinear `x` violates the ceiling based
on `deg V` (§20). A polynomial `V(x,y)=x⁴+y²/2` has global degree four, but actions confined
to the `y` direction see degree two. Conversely, a zero selected triple does not determine
global degree: `V=x⁴`, baseline `−3/2`, three unit actions has zero triple (§30).

**Intuition / prior art / EBU status.** An order-`k` Boolean monomial needs `k` distinct
labels. Powers of one label do not create extra interaction order. This is a standard
polynomial/pseudo-Boolean corollary, extending the already frozen quadratic result.

## 12. Quadratic pair-only corollary

**Corollary B3.**

**Assumptions and definitions.** One fixed field; all subset values defined; a quadratic
potential on the relevant states,
`V(x)=½(x−x*)ᵀH(x−x*)`, with constant symmetric `H`; fixed additive displacements `h_i`.
Set `μ=H(x₀−x*)`. Positive definiteness is not required for this algebra, though it matters
for a normalizable full-space Gaussian equilibrium density.

**Statement.**

\[
m_i=-\mu^Th_i-\tfrac12h_i^THh_i,\qquad
m_{ij}=-h_i^THh_j,\qquad m_E(T)=0\ (|T|\ge3).
\tag{11}
\]

**Proof.** Expand the quadratic at `x₀+Σz_i h_i` and use `z_i²=z_i` on the vertices.
The cross terms `h_iᵀHh_j` occur twice in the square and cancel the factor `1/2`.
The valuation supplies the minus sign. There are no higher-degree monomials. ∎

**Removed-assumption check.** Cubic potential with additive actions gives §13's nonzero
triple; quadratic potential with a nonlinear response gives §20's nonzero triple. A varying
Hessian or field across coalitions cannot be treated as one constant `H`. For an arbitrary
nonsymmetric matrix in `xᵀHx/2`, the relevant Hessian is `(H+Hᵀ)/2`, not the raw matrix.

**Intuition / prior art / EBU status.** `H` measures potential curvature. The pair coefficient
is the negative bilinear overlap of two action directions in that geometry; it can have
either sign even when `H` is positive definite. Orthogonal directions can have zero pair
interaction. Foundation §14 already states this result. The E1a connection is theoretical:
its curvature measurements would constrain this local geometry under its own conditions.
**No E1a optical-trap experiment or action-synergy measurement has been run here.**

## 13. Cubic and quartic examples

These are exact algebraic witnesses for Theorem B, not claims that odd polynomials define
normalizable equilibrium densities on the full real line.

For `V(x)=λx³/6`, baseline `b₀` and additive displacements `a,b,c`, three differences
annihilate degrees below three. The coefficient of `abc` in `(b₀+a+b+c)³` is `3!=6`.
Consequently

\[
m_{ABC}=-\lambda abc.
\tag{12}
\]

For `V(x)=λx⁴/24` and four displacements `a,b,c,d`, four differences similarly give

\[
m_{ABCD}=-\lambda abcd.
\tag{13}
\]

These results hold at every baseline. They can also be read directly from (8), since the
third/fourth derivatives are constant. With unit increments and `λ=1`, both are `−1`.
With `(λ,a,b,c)=(5,2,−3,4)`, the cubic triple is `120`; with
`(λ,a,b,c,d)=(2,1,2,−1,3)`, the quartic coefficient is `12`, independently of the baseline.
Both signs and factorial normalizations were checked by exact rational subset sums.
Removing the normalizing factorial changes the value: the foundation's `V=x³` unit example
has `m_ABC=−6`. These are standard polynomial examples, with no novelty or physical adoption.

## 14. General nonlinear coalition-state map

The map `x:{0,1}ⁿ→Ω` need not be additive or smooth. State dependence, shared constraints,
physical coupling, thresholds, scheduling or a rule-replayed action can alter a coalition's
endpoint. The exact object is the **composite** `G=V∘x` on the declared cube.

For any selected nonempty `T`, higher-order interaction exists **if and only if**
`Δ_T(V∘x)(0)≠0`. Nonquadratic `V` and a nonlinear response are possible sources, not
sufficient conditions. For orders above two, quadratic `V` plus affine `x` excludes
interaction; its contrapositive is a rejection of that conjunction, not identification of
which physical component failed.

Disjoint physical write supports do not prove absence of valuation interaction if `V`
couples them. Conversely, a nonlinear coordinate can be invisible to `V`, and therefore
produce no valuation interaction. Action-interaction hyperedges belong to the value table;
they need not coincide with edges of the physical graph or factors of a chosen model.

A useful factor consequence is exact: if `G(z)=Σ_a G_a(z_{K_a})` and no `K_a` contains
`T`, then `m_E(T)=0`. Each summand is independent of at least one differentiated label,
so its difference vanishes. This requires a factorization of the **composite**, not just
of `V`: a nonlinear response can couple previously separate potential factors.

## 15. Composite-map theorem

**Theorem CM.**

**Assumptions and definitions.** A complete finite coalition map and potential as in §3.
For the derivative representation only, assume a `C^k` extension `x` near the cube face
for `T`, and `V∈C^k` near its image. Complementary indicators are held at zero.

**Statement.** For `k=|T|≥1`,

\[
m_E(T)=-\Delta_T[V\circ x](0)
=-\int_{[0,1]^T}\partial_T[V\circ x](z_T,0_{N\setminus T})\,dz_T,
\tag{14}
\]

where the second equality requires the extension hypotheses. The first does not.

**Proof.** The first equality is Theorem A. Apply repeated coordinate FTC directly to the
composite extension for the second. All extensions with the same vertices give the same
integral total, because the integral is its alternating vertex sum. ∎

**Removed-assumption check.** A thresholded or purely discrete response need not have the
required derivatives. Nonetheless the vertex theorem survives. Choosing arbitrary smooth
interpolation does not establish intermediate physical states or dynamics. Two extensions
with identical vertices can have different derivative contributions (§16).

**Intuition / prior art / EBU status.** The finite table knows the combined outcome of
potential and response, not their separate internal explanations. This is a direct
composition of known structures; it is the appropriate general EBU interaction object.

## 16. Smooth chain-rule decomposition

### 16.1 Pair and triple formulas

**Proposition CR.** Under §15's smoothness assumptions, define `x_B=∂_B x` for a
nonempty subset of distinct coordinate labels; evaluate all derivatives at the same point.
Then

\[
\partial_{ij}(V\circ x)=D^2V[x_i,x_j]+DV[x_{ij}],
\tag{15}
\]

\[
\begin{aligned}
\partial_{ijk}(V\circ x)={}&D^3V[x_i,x_j,x_k]\\
&+D^2V[x_{ij},x_k]+D^2V[x_{ik},x_j]+D^2V[x_{jk},x_i]\\
&+DV[x_{ijk}].
\end{aligned}
\tag{16}
\]

**Proof.** Differentiate `DV[x_i]` once to obtain (15). Differentiating its two terms once
more gives one derivative of `D²V`, two derivatives of its arguments, one derivative of
`DV`, and one derivative of `x_ij`, yielding exactly the five terms in (16). Symmetry of
`D²V` permits the displayed order. All coefficients are one because `i,j,k` are distinct.
Repeated labels would collect indistinguishable terms and introduce multiplicities. ∎

The first term describes potential curvature acting on first response derivatives; the
second describes the potential gradient acting on a mixed response. Integrating their
**negative sum** gives finite synergy. At triple order, both potential third derivatives
and pair/triple response derivatives contribute. An additive map eliminates every `x_B`
with more than one label; a quadratic potential eliminates `D³V`, but not the other terms.

### 16.2 General chain-rule formula

**Proposition CR-general (set-partition Faà di Bruno).** Assume `x,V∈C^k` on the neighborhoods
specified in §15. For a nonempty set `T` of `k` distinct labels, let `Π(T)` be its partitions
into nonempty disjoint blocks. Then

\[
\partial_T(V\circ x)
=\sum_{\pi\in\Pi(T)}D^{|\pi|}V(x)[x_B:B\in\pi].
\tag{17}
\]

The order of block arguments is irrelevant because the derivative is symmetric.
Combining (17) with (14) gives the general integrated interaction decomposition.
Appendix B supplies the full domain/derivative formulation and integrated corollary.

**Proof by induction.** For one label this is the chain rule. Suppose the formula holds
for `T`, and differentiate with respect to a fresh label `j`. Differentiating the outer
`D^{|π|}V(x)` creates the new singleton block `{j}`. Differentiating one of its multilinear
arguments replaces `x_B` by `x_{B∪{j}}`, inserting `j` into that block. Every partition of
`T∪{j}` falls into exactly one of these disjoint cases, and removing `j` recovers its
unique predecessor and affected block. Thus every term appears once, with coefficient
one. This completes the induction. Smoothness justifies all derivatives and symmetry. ∎

**Removed-assumption check / intuition.** With repeated indices the partition sum still
works if occurrences are separately labelled, but grouping equal terms creates the usual
Faà di Bruno coefficients. Without the differentiability order, only the finite identity
is assured. A partition records which action labels first combine inside the response,
and how many resulting response groups meet in a derivative of `V`.

**Prior art / EBU status.** This is standard higher chain-rule combinatorics; compare
[Hardy, Proposition 1 and Example 1](https://arxiv.org/pdf/math/0601149). The vector-valued
form above follows by the displayed multilinear proof. It is not an EBU invention.

### 16.3 Why the origin split is not canonical

Take `V=x²/2` and the two-variable extensions
`x^(a)=z₁+z₂` and `x^(b)=z₁+z₂+z₁(1−z₁)z₂`. They agree at every Boolean vertex.
For (15), the integrals of `(D²V[x₁,x₂], DV[x₁₂])` over the unit square are respectively
`(1,0)` and `(7/6,−1/6)`. Both give `m_AB=−1`, but their curvature/response splits differ.
These four rational values were checked directly by polynomial integration.

Even a physically chosen extension does not make the split coordinate invariant. On a
region where `dV≠0`, one can use `y₁=V(x)` as one coordinate in a local chart. The potential
then becomes linear in `y₁`, shifting the derivative nonlinearity to the transformed
response. Coordinate changes transform the generator too. Only the composite vertex value
and its coefficient are invariant when all objects are consistently transformed. A claim
of a unique causal or physical origin requires extra structure and evidence.

## 17. Generator terminology

| Term | Mathematical object | Role and boundary |
|---|---|---|
| Deterministic vector field | `b_θ(x,u)`; written `Ψ_θ(x,u)` in the task | Instantaneous state derivative; a declared dynamical interface, not the potential |
| Flow map | `Φ_θ^τ(x₀;u)` | Finite-time state response when the ODE is well posed |
| Discrete transition map | `T_a:x↦x'` | A finite action; need not embed in any continuous flow |
| Controlled transition map | `T(x,u)` or `T[x,u(·)]` | Declared input/protocol to endpoint; can include a resolver or hybrid event |
| Action-state response map | `S↦x_S` | Coalition table of endpoints; the only dynamical input required by the finite theorem |
| Lie derivative | `L_bF=DF[b]` | Generator of pullback of observables along a smooth deterministic flow |
| Markov infinitesimal generator | `ℒF=lim_{t↓0}(P_tF−F)/t` on its domain | Operator on observables; not a vector of state velocities |
| Force/flux chain | `f`, constitutive `J`, incidence/conversion to `ẋ` | A possible physical construction, with separate units, registration and boundary conditions |
| Historical edge/quantity generator | `G_Q` or typed carrier change per extent | Quantity participation; needs a declared constitutive/incidence link to state change |
| Historical state-transformation generator | `T_h(z)=z+hG_T(z)+o(h)` | Derivative of an augmented transformation in declared extent/topology; extent need not be time |
| Historical `Ψ_e(J_e)` | Accumulated opposition / dissipation potential | Scalar function of flux, with derivative `r_e`; **not** the vector field `Ψ_θ(x,u)` |

To avoid the last collision, use `b` for the abstract vector field below. The task's
`ẋ=Ψ_θ(x,u)` is interpreted as `ẋ=b_θ(x,u)`, explicitly distinct from historical `Ψ_e`.
No universal relationship is inferred merely from identical letters.

## 18. Generator→flow→coalition theorem

**Theorem C (generator–flow–Möbius interface).**

**Assumptions and definitions.** Fix `θ`, `x₀`, horizon `τ`, and a control `u_S` for each
coalition. For constant controls assume `b_θ(·,u_S)` is continuous and locally Lipschitz in
state on an open domain, and every solution exists on `[0,τ]` without leaving the declared
domain. Assume the subset protocol is physically admissible and
`Φ_θ^τ(x₀;u_∅)=x₀`. Define
`x_S=Φ_θ^τ(x₀;u_S)`, `G_τ(S)=V_θ(x_S)`, and `E_τ(S)=V_θ(x₀)−G_τ(S)`.
For predetermined time-varying controls, replace the autonomous flow by a well-posed
Carathéodory evolution map with measurable time dependence and an integrable local
Lipschitz bound; the same endpoint result applies. No control smoothness is needed for
the finite table once all endpoints are well defined.

**Statement.** For every nonempty `T`,

\[
m_{E_\tau}(T)=-\Delta_T\big[S\mapsto
V_\theta(\Phi_\theta^\tau(x_0;u_S))\big](\varnothing).
\tag{18}
\]

If `V∈C¹` along the solutions, each coalition additionally satisfies

\[
E_\tau(S)=-\int_0^\tau DV_\theta(x_S(t))[b_\theta(x_S(t),u_S)]\,dt.
\tag{19}
\]

**Proof.** Local uniqueness and stipulated existence give a single-valued endpoint for each
control. Equation (18) is Theorem A applied to their composite table. Along each solution,
the ordinary/absolutely-continuous chain rule gives `dV/dt=DV[b]`; integration gives (19).
Finite summation may also be interchanged with these integrals. ∎

**Removed-assumption checks.** Continuity alone need not give a unique endpoint: `ẋ=√|x|`,
`x₀=0`, admits both remaining at zero and delayed departures. A declared selection rule could
restore a response map, but uniqueness would no longer follow from the ODE assumptions.
Smooth `ẋ=x²`, `x₀=1`, blows up at time 1, so smoothness alone does not supply all horizons.
An unregistered control-to-action mapping is not filled in by the theorem.

**Empty-coalition correction.** A default control may cause natural drift. If its endpoint
is `y_∅≠x₀`, raw `E^raw(S)=V(x₀)−V(y_S)` has generally nonzero `E^raw(∅)` and lies
outside §3's normalized setup. Either require the stated fixed empty endpoint, or explicitly
declare the alternative reference

\[
E^{rel}(S)=V(y_\varnothing)-V(y_S)
=E^{raw}(S)-E^{raw}(\varnothing).
\tag{20}
\]

Every nonempty Möbius coefficient is unchanged by this constant shift; the empty coefficient
and total valuation are changed. This is an optional comparator, not permission to reprice
accounts or attribute background evolution to actors. For example, `ẋ=1+u`, `x₀=0`,
`τ=1`, `V=x`, `u_∅=0`, gives raw empty value `−1`, not zero. A fixed empty endpoint at one
horizon need not imply `b(x₀,u_∅)=0`; the latter is a stronger, convenient condition that
keeps it fixed at all times by uniqueness.

**Intuition / prior art / EBU status.** Generator: how state moves. Flow: the resulting
endpoint. Potential: its valuation. Möbius: decomposition. Registration: whether an actor
transaction exists. This theorem is an immediate composition of known ODE and set-function
structures, not a new constitutive law. It is an **INTERFACE** to EBU valuation; identifying
and validating a particular physical generator is a physical extension. See
[Sontag](https://sontaglab.org/mct.html), appendix R13–R14.

## 19. Short-time generator expansion

### 19.1 First three orders

**Proposition ST.** Fix a constant control `u` and an autonomous vector field. Write at
`x₀`: `v=b(x₀,u)`, `A=D_xb(x₀,u)`, `B=D_x²b(x₀,u)`. Suppose the solution stays in a
compact tube in the open domain; `b∈C³` and `V∈C⁴` there, with bounded derivatives.
These are clean sufficient assumptions for the displayed third-order expansions with
fourth-order remainder, uniform over the finite control set.

\[
\Phi^\tau=x_0+\tau v+\frac{\tau^2}{2}Av
+\frac{\tau^3}{6}\{B[v,v]+A^2v\}+O(\tau^4),
\tag{21}
\]

\[
\begin{aligned}
E_\tau(u)={}&-\tau DV[v]\\
&-\frac{\tau^2}{2}\{D^2V[v,v]+DV[Av]\}\\
&-\frac{\tau^3}{6}\{D^3V[v,v,v]+3D^2V[v,Av]
+DV[B[v,v]+A^2v]\}+O(\tau^4).
\end{aligned}
\tag{22}
\]

All potential derivatives in (22) are evaluated at `x₀`.

**Proof.** Differentiate the ODE: `x'=b`, `x''=D b·b`, and
`x'''=D²b[b,b]+Db·Db·b`. The fourth time derivative exists and is bounded under the
stated `C³` hypothesis, giving (21) by one-variable Taylor's theorem in time. Differentiate
`V(x(t))` three times: its derivatives are the three braces in (22). The fourth derivative
is bounded under `V∈C⁴`, `b∈C³`, so the Taylor integral remainder is `O(τ⁴)`. Subtract
from `V(x₀)`. Equivalently the coefficients are `−L_b^rV/r!`. ∎

**Weaker orders and removed assumptions.** For just
`Φ^τ=x₀+τv+O(τ²)`, locally Lipschitz `b` bounded on the short trajectory suffices:
integrate `b(x(t))−b(x₀)=O(t)`. A locally Lipschitz gradient of `V` gives the corresponding
first-order energy remainder. Mere continuous gradient gives a little-o first-order
remainder, not necessarily `O(τ²)`; §10's Hölder example supplies the obstruction.
For time-dependent controls the coefficients also involve explicit time dependence;
(21)–(22) cannot be transplanted unchanged. None of these finite-order formulas asserts
convergence of an infinite Lie series.

### 19.2 Control-affine interaction order

**Proposition ST-affine.** Suppose `b_z=f₀+Σ_i z_i f_i`, with constant Boolean controls,
`V∈C^{k+1}` and all `f_i∈C^k` near a common short-time compact tube. Require §18's empty
endpoint condition at every sufficiently small horizon, or use its explicitly declared
relative comparator. Let `L_iF=DF[f_i]`.
For `T` with `k` distinct labels,

\[
m_{E_\tau}(T)=
-\frac{\tau^k}{k!}\sum_{\pi\in\operatorname{Perm}(T)}
L_{\pi_1}\cdots L_{\pi_k}V(x_0)+O(\tau^{k+1}).
\tag{23}
\]

In particular `m_T=O(τ^k)`; the leading coefficient may vanish.

**Proof.** The finite time Taylor formula is
`V(Φ_z^τ)=Σ_{r=0}^k τ^r L_z^rV(x₀)/r!+O(τ^{k+1})`.
Expand `L_z=L₀+Σz_iL_i` without commuting its factors. A word of length `r` contains
at most `r` distinct action labels. `Δ_T` kills every word for `r<k`. At `r=k`, a word
survives only if each member of `T` occurs exactly once: no drift letter, repeated label,
or label outside `T` can occur. These words are precisely the `k!` permutations in (23).
There are finitely many vertices, so their remainder sum retains the stated order. ∎

**Removed-assumption check.** With nonlinear control dependence
`b_z=z₁z₂z₃` and linear `V=x`, baseline zero, the triple is `−τ`, violating an `O(τ³)`
claim. Conversely control-affinity does not impose a finite interaction ceiling: repeated
state dependence in Lie derivatives can create all orders (§20). A nonsmooth shared-capacity
resolver may invalidate both the input-affine representation and this expansion.

**Intuition / prior art / EBU status.** A length-`r` response word can mix at most `r` labels
when input enters affinely. This is known nonlinear response / Volterra / Chen–Fliess
structure, specialized by a Boolean contrast. [Fliess](https://www.numdam.org/item/BSMF_1981__109__3_0/)
and [Sontag, §2.11 and Chapter 4](https://sontaglab.org/FTPDIR/sontag_mathematical_control_theory_springer98.pdf)
are prior art. Equation (23) is a direct corollary, not a novelty claim or executed flow.

## 20. Generator-origin interaction

### 20.1 Quadratic potential, nonlinear response

Let `x₀=0`, `V=x²/2`, `s=z₁+z₂+z₃`, and `x(z)=s+αz₁z₂`. Boolean reduction yields

\[
G(z)=\tfrac12\sum_i z_i+\sum_{i<j}z_i z_j
+(2\alpha+\tfrac12\alpha^2)z_1z_2+\alpha z_1z_2z_3,
\qquad m_{123}=-\alpha.
\tag{24}
\]

At `α=1`, the complete endpoint and EBU table is:

| Coalition | ∅ | A | B | C | AB | AC | BC | ABC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `x_S` | 0 | 1 | 1 | 1 | 3 | 2 | 2 | 4 |
| `E(S)` | 0 | −1/2 | −1/2 | −1/2 | −9/2 | −2 | −2 | −8 |

The alternating triple is `−8+9/2+2+2−3/2=−1`. This endpoint map can be generated
analytically by `ẋ=u₁+u₂+u₃+αu₁u₂`, constant controls, horizon 1, initial state 0.
No trajectory was generated to establish the formula. The generator is nonlinear in
control; the potential remains quadratic. Even linear `V=x` gives triple `−1` when
`x(z)=z₁z₂z₃` (equivalently `ẋ=u₁u₂u₃`, horizon 1).

### 20.2 Linear in state is not jointly linear in state and control

For `ẋ=u x`, `u_S=|S|`, `x₀=1`, and `V=x²/2`, the analytic solution gives

\[
x_S=e^{\tau|S|},\qquad
m_E(T)=-\tfrac12(e^{2\tau}-1)^{|T|}\quad(T\ne\varnothing).
\tag{25}
\]

Proof: the subset sum of `e^{2τ|S|}` factorizes as
`∏_{i∈T}(e^{2τ}−1)`. The empty endpoint stays at 1. Every order is nonzero for `τ>0`.
The vector field is linear in `x` for fixed input and affine in input for fixed state, but
**bilinear jointly**. Finite-time exponentiation makes its coalition response nonlinear.
For small `τ`, the leading coefficient is `−2^{k−1}τ^k`, agreeing with (23).

A correct sufficient all-time pair-only condition is

\[
\dot x=A(t)x+b_0(t)+\sum_i z_i b_i(t),
\tag{26}
\]

with common control-independent `A(t)`, common initial state, well-defined linear evolution,
and fixed controls/protocols entering additively. Variation of constants makes
`x_S(τ)=x_∅(τ)+Σ_{i∈S}h_i(τ)`. A fixed quadratic potential is therefore at most pairwise
in `z` for every permitted horizon. To use the core baseline additionally require
`x_∅(τ)=x₀`; otherwise state the relative comparator. Input-dependent state matrices,
saturation, constraints and coalition-specific timings need not satisfy this condition.

### 20.3 Mixed potential and response origin

Keep `x=s+αz₁z₂` but take `V=x³/6`. Direct subtraction gives

\[
m_{123}=-1-\frac52\alpha-\frac12\alpha^2.
\tag{27}
\]

One derivation starts with the additive-map triple `−1`; only `AB` and `ABC` change.
Their changes contribute
`−[(3+α)³−27−(2+α)³+8]/6=−5α/2−α²/2`.
For the displayed smooth extension, (16)'s nonzero triple terms are
`(1+αz₂)(1+αz₁)` and `αx`; their cube integrals are
`1+α+α²/4` and `3α/2+α²/4`. Both contribute at `α=1`, yielding `−9/4−7/4=−4`.
These are contributions relative to the declared coordinates and extension, not a canonical
causal split (§16.3).

### 20.4 Nonlinear dynamics need not create synergy

Let `ẋ=u/(2x)` on `x>0`, `u_S=|S|`, `x₀=1`, `τ=1`, `V=x²/2`.
The exact endpoint is `x_S=√(1+|S|)`, so `E(S)=−|S|/2` and every interaction of order
at least two is zero. This is a genuinely nonlinear state equation and nonlinear endpoint
map. The potential composition makes the value modular. This counterexample also shows
that nonlinearity alone is not a sufficient generator-origin interaction condition.

### 20.5 Sequential generators, brackets and comparator orientation

For smooth local flows of fields `X,Y`, define the usual observable bracket
`[X,Y]=DY·X−DX·Y`, so `[L_X,L_Y]=L_[X,Y]`. With this convention,

\[
\Phi_Y^\tau\!\circ\Phi_X^\tau(x)
-\Phi_X^\tau\!\circ\Phi_Y^\tau(x)
=\tau^2[X,Y](x)+O(\tau^3).
\tag{28}
\]

Second-order expansions prove this: the two cross terms are `DY·X` and `DX·Y`.
The historical atomic source instead uses `[G_i,G_j]_s=DG_iG_j−DG_jG_i` for
“left after right minus right after left.” That is the opposite bracket when labels are
kept fixed; the displayed compositions must be translated with their signs.

Example: `X=∂_x`, `Y=x∂_y`, initially `(0,0)`. `X` then `Y`, each for time `τ`, ends
at `(τ,τ²)`; `Y` then `X` ends at `(τ,0)`. For `V=y`, their values differ by `−τ²`.
Yet each is an exact endpoint difference. A simultaneous control `X+Y` over time `τ`
would end at `(τ,τ²/2)` and needs its own declared coalition/horizon protocol.

Baker–Campbell–Hausdorff expansions for the observable pullbacks begin
`log(e^{τL_X}e^{τL_Y})=τ(L_X+L_Y)+τ²[L_X,L_Y]/2+…`, as a formal or suitably justified
local expansion. No convergence for arbitrary unbounded operators is claimed. One-point
vanishing of a bracket does not establish neighborhood commutativity. Brackets describe
ordered execution; Boolean Möbius contrasts describe an unordered, declared endpoint
table. They are distinct future generator interfaces, consistent with historical SD-04/05,
and not a replacement for the current finite core.

## 21. Historical generator reconciliation

### 21.1 What the old chain actually meant

In historical v2.7 §2, for an edge direction with source loss `−1` and destination gain
`η_e`, `μ=∇V_state` yields `dV/dq=−μ_i+η_eμ_j`, hence
`f_e=μ_i−η_eμ_j`. The historical dissipation potential was

\[
\Psi_e(J)=\frac{J^2}{2M_e}+\vartheta_e J,\quad J\ge0,\ M_e>0.
\tag{29}
\]

Here `ϑ_e` denotes the historical threshold to avoid collision with the pricing field `θ`.
Minimizing `Ψ_e(J)−f_eJ` gives `J=M_e[f_e−ϑ_e]_+`; equivalently its opposition derivative
is `r_e(J)=ϑ_e+J/M_e`. The vector state evolution then requires an incidence/conversion
law such as `ẋ=Σ_e s_eJ_e`, boundary terms and any other state processes. Thus the scalar
`Ψ_e` does not itself equal `ẋ`. The abstract theorem can accept a resulting vector field,
but requires none of these particular constitutive equations.

| Object / claim | Historical disposition | Current S-MG treatment |
|---|---|---|
| `E=V_pre−V_post`, path identity | Adopted in current frozen foundation with stated hypotheses | Controlling valuation; retained |
| `f=−DV[dx/dq]` | Current foundation §3/6 adopts a local directional quantity | Does not establish mobility or a mechanical law |
| Two-endpoint `f_e=μ_i−η_eμ_j` | Derived within historical reduced edge representation; W0 F.5 **UNREGISTERED**, readiness **REFUSED** for missing edge declaration | Conditional directional formula; include loss sink/environment terms when the complete current boundary requires them |
| `J_e=M_e[f_e−ϑ_e]_+` | Historical constitutive choice; W0 F.6 **MISSING**, no registered relation to its integer `q` | Neither required nor adopted; not refuted solely because another model uses integers |
| Historical `Ψ_e` | Dissipation/opposition scalar; W0 F.7 **MISSING / UNREGISTERED**, derivation deferred to future Part I under separate authority | Kept distinct from abstract vector field; no authority backflow |
| Raw Euler `q=ΔtJ` | v2.7 law (2), a discretization of the historical continuous law | Requires its own step/domain assumptions |
| Safe gated line search | v2.7 law (3), coordinate descent with a different objective; excludes the dissipation terms in its size optimizer | Rejected equivalence: it is not generally the same Onsager flux or its discretization |
| W0 conservative world | Prospective candidate, never adopted there; superseded as active first-study substrate | Historical evidence of missing declarations, not current experimental authority |
| Old universal divisibility / collapsed “generator” roles | Narrowed in off-branch atomic amendment F2/F5 | Declared extents and two generator roles are useful interfaces, not universal assumptions |
| Process cost / institutional allocation | Historical candidate and unresolved scoped declarations | Excluded from current core; conditional extension below only |

No blanket retraction of force, flux or dissipation mathematics was found. What was superseded
was the active substrate and forward programme; what was refused was an undeclared chain
for a particular world. An old predecessor's “not applicable” wording is not evidence that
the law was experimentally rejected. SD-03 readiness explicitly deferred the needed
opposition derivation, while SD-05 and SD-06 own multi-action and subset-lattice questions.

### 21.2 Incidence, feasibility and topology

For declared fixed accepted rates `q_i`, horizon `dt`, and fixed incidence columns `s_i`,
`h_i=dt s_i q_i` gives `x_S=x₀+Σ_{i∈S}h_i`, so Theorems B/B3 apply. If `q_i` already
means a transferred quantity rather than a rate, the increment is `s_i q_i`; multiplying by
`dt` again would be dimensionally wrong. If one action spans multiple edges, sum its
fixed edge increments first to define its `h_i`.

The static current-branch action source constructs such vectors with source removal,
delivered destination quantity and loss sink quantity. Its feasibility checks distinguish
source-funded simultaneous execution from funding an outflow with an arrival in the same
instant. Additive endpoint algebra does not waive these checks or prove that every subset
is admissible. State-dependent flux integrated over a horizon, coalition-sensitive accepted
quantities, binding capacities and rule replay can instead make `h_i` depend on `S`; then
only the composite finite theorem applies without additional proof.

W0 intentionally allowed at most one actor/action per independent block and disjoint block
operations; its C.5/F.9/G.1 contain neither a registered joint interaction object nor the
subset table needed for SD-06. This does not prove that arbitrary coupled potentials on
those coordinates have zero interaction. The historical package did not register such an
EBU table. A missing experiment is not a zero coefficient.

Physical graph topology, factor support, feasible-action posets and value-interaction
hypergraphs are different structures. Möbius inversion applies to a declared order of
subsets, not automatically to physical adjacency. Motif reuse is justified only if the
complete result-affecting state/field/action protocol is equivalent. A label-preserving
bijection with identical coalition values has identical coefficients by (2); this proves
only the algebraic reuse of that table. Runtime/history reuse in the historical motif
programme requires all A1–A8 jointly, including complete boundary/composition information,
all subset interactions, cache identity and provenance, dependency invalidation, and
history-wide boundary equivalence. Its prerequisite, shared-factor, order, interaction and
boundary layers must not be collapsed into one graph. Graph isomorphism or visual similarity
does not establish these requirements. No compressed algorithm, cache or SD campaign is
implemented here.

### 21.3 Conditional process-cost extension

If a separately authorized model defines a real set function `C(S)` for process burdens
not already represented in `V`, and defines `E_net(S)=E(S)−C(S)`, then linearity of (2)
gives `m_net(T)=m_E(T)−m_C(T)` for **all** `T`, including the empty coefficient.
Proof: distribute the finite signed sum. Without a declared cost table the expression is
undefined. Modular cost alters only singletons (and possibly the constant); nonlinear
coalition cost can introduce higher orders. Double-counting a burden already in `V` is
not remedied by the algebra. This is a conditional extension of a different declared
valuation, not an insertion of `C` into the current physical foundation.

## 22. Stochastic generator interface

A Markov generator acts on observables; its adjoint evolves distributions. In a finite state
space with rates `k(x,y)≥0` for `x≠y`,

\[
(\mathcal LF)(x)=\sum_{y\ne x}k(x,y)[F(y)-F(x)],\qquad
P_t=e^{t\mathcal L},\qquad \mathcal L^*p=0
\tag{30}
\]

is the stationarity equation. For diffusions, the same notation requires an operator domain,
boundary conditions and an appropriate reference measure; not every formal differential
operator generates a well-posed stochastic process.

**Proposition MC (conditional expected-value interface).** For each coalition let `P_τ^S`
be a declared Markov transition semigroup and suppose `V` is integrable under every endpoint
law from `x₀`. Set `\bar G(S)=(P_τ^S V)(x₀)` and
`\bar E^raw(S)=V(x₀)−\bar G(S)`. Then for nonempty `T`,

\[
m_{\bar E}(T)=-\sum_{S\subseteq T}c_T(S)(P_\tau^SV)(x_0).
\tag{31}
\]

This holds for the raw table or its explicitly normalized reference
`\bar E^rel(S)=\bar G(∅)−\bar G(S)`. In finite state space, with finite `V`, expansion
of the matrix exponential gives the corresponding convergent generator series. In general
spaces a first-order expansion requires `V` in the generator domain; higher powers and
remainders require corresponding domain and regularity hypotheses.

**Proof.** Use Theorem A on the scalar expected-value table; finite linear combinations
commute with integration when each expectation is finite. In finite dimension the matrix
exponential series converges in norm, giving its stated expansion. ∎

**Removed-assumption check.** A heavy-tailed endpoint law can make `E[V]` infinite, so
finite Möbius contrasts are then undefined. Nonzero natural evolution under the empty
control again invalidates a forced zero raw baseline. Independent endpoint experiments
do not themselves define a joint random vector of potential outcomes; such a coupling is
needed before claiming the random coefficient's cross-coalition covariance. Even when
defined, `E[log p(X)]≠log E[p(X)]` in general. A single endpoint `x_S`, an expected value,
and an ensemble average must not be interchanged.

**Intuition / prior art / EBU status.** The same finite algebra can decompose a separately
declared expectation, but that is a different scientific observable. Standard semigroup
background: [Sargent–Stachurski, Chapter 6](https://continuous-time-mcs.quantecon.org/generators.html).
No stochastic actor valuation rule, universal diffusion model or scientific execution is
adopted by this report.

## 23. Equilibrium compatibility

### 23.1 Density, stationarity, reversibility and current

| Property | Meaning in its stated setting | What it does not imply alone |
|---|---|---|
| Boltzmann form | `p=Z⁻¹e^(−V)` relative to a fixed measure, `0<Z<∞` | Stationarity under an arbitrary generator or reversibility |
| Stationarity | `ℒ*p=0`, with boundary conditions | Detailed balance, zero currents or canonical density |
| Detailed balance, even-variable finite jump process | `p_x k_xy=p_y k_yx` for every edge | Thermodynamic interpretation without a physical reservoir model |
| Reversibility | Stationary path law is invariant under the appropriate time reversal | Universal zero ordinary current for variables with odd time-reversal parity |
| Zero stationary current | In the declared overdamped configurational diffusion, no probability flux | A general criterion for arbitrary underdamped or magnetic systems |

The R-stage hierarchy is retained: supplied-potential identities require no equilibrium;
canonical density algebra has separate assumptions; reversible equilibrium and P4 entropy
need further dynamical/accounting conditions.

### 23.2 Langevin / OU examples, derived without simulation

For constant symmetric positive definite `D`, consider formally
`dX_t=b(X_t)dt+√(2D)dW_t`, with well-posed dynamics and appropriate no-flux/decay conditions.
Its density current is `j=bp−D∇p`. If `p∝e^(−V)` and

\[
b=-D\nabla V+c,\qquad \nabla\cdot(cp)=0,
\tag{32}
\]

then `j=cp`, so `∇·j=0` and the density is stationary. For `c=0`, integration by parts
makes the generator symmetric in `L²(p)` with the stated boundary conditions, yielding
the usual reversible overdamped realization. These are sufficient compatible models,
not laws inferred from EBU valuation.

For `V=xᵀHx/2` with `H` positive definite and a constant skew matrix `Q`, choose
`b=−(D+Q)Hx`. Then `c=−QHx`; the two terms in `div(cp)/p` vanish because
`tr(QH)=0` and `(Hx)ᵀQ(Hx)=0`. The Gaussian with covariance `H⁻¹` is stationary.
`Q≠0` yields nonzero current away from its null set, breaking ordinary overdamped
reversibility while preserving exactly the Boltzmann density. Example `D=H=I₂`,
`Q=[[0,−1],[1,0]]` has `j/p=(y,−x)` and zero divergence weighted by `p`.
This directly refutes “Boltzmann density means detailed balance.”
[Nonreversible Langevin prior art](https://arxiv.org/html/1506.04934), Eqs. (6)–(8).

If `D` varies in space, Itô drift and current formulas require the corresponding derivative
terms; (32) cannot simply be reused unchanged. On a constrained or truncated domain,
normalization and boundary conditions must be checked and Gaussian inverse-covariance
claims need the R-stage's additional full-support assumptions.

### 23.3 Jump processes and local detailed balance

For strictly positive `p_x`, reversible rates can be constructed using symmetric nonnegative
conductances `a_xy=a_yx` by `k_xy=a_xy/p_x`. Along edges with both rates positive,

\[
\log\frac{k(x,y)}{k(y,x)}
=\log\frac{p_y}{p_x}=V(x)-V(y)=E(x\to y).
\tag{33}
\]

**Proof.** Divide `p_x k_xy=p_y k_yx` and insert the Boltzmann density. Summing (33)
over a path telescopes; a cycle gives zero. This is a conditional generator-level
representation of the endpoint difference. ∎

**Removed-assumption check.** On a three-state ring with clockwise rate 2 and
counterclockwise rate 1, the stationary distribution is uniform (`V` constant), but the
clockwise log-rate ratio is `ln 2`, whereas endpoint `E=0`. Stationarity and Boltzmann
form do not imply (33). An irreversible edge with zero reverse rate produces an infinite
log ratio, outside the finite formula.

Under a physically justified single-bath, no-extra-driving, resolved-state local-detailed-
balance model, `k_B log(k_xy/k_yx)` is the medium entropy flow. If `V=U/(k_BT)+constant`
with no omitted internal degeneracy, (33) then gives `Δs_med=k_BE`. Multiple reservoirs,
chemical work, driving or hidden channels add terms or require channel-resolved rates.
With coarse-grained states carrying intrinsic entropy, the log-rate ratio can include that
entropy as well as bath flow; identifying it with bare medium entropy needs additional
bookkeeping. A free-energy potential cannot silently be treated as bare configurational
energy. Local detailed balance can hold in a driven stationary process with nonzero cycle
affinities; it is not synonymous with global detailed balance. See
[Maes, Eq. (10) and scope discussion](https://arxiv.org/pdf/2011.09200).

**Intuition / status.** Rate ratios provide another conditional continuity link, not an
extra universal axiom. Arbitrary imposed coalition controls need not share the equilibrium
generator or the no-extra-work condition. The probability theorem below concerns endpoint
density values; it does not assert that every coalition was generated by equilibrium
relaxation or has equilibrium entropy accounting.

## 24. Möbius–probability theorem

**Theorem D (canonical-density interaction).**

**Assumptions and definitions.** Section 3, plus a specified reference measure and support,
a finite normalizer `0<Z<∞`, and finite positive density or mass
`p(x_S)=Z⁻¹exp(−V(x_S))` at every required endpoint. For a physical canonical claim, the
ensemble, energy, temperature, coordinates and density-of-states treatment must be
independently justified as in R-stage §9.2 A. The following algebra only needs the stated
relation at these points.

**Statement.**

\[
E(S)=\log\frac{p(x_S)}{p(x_0)},\qquad
m_E(T)=\sum_{S\subseteq T}c_T(S)\log p(x_S)
=\log\prod_{S\subseteq T}p(x_S)^{c_T(S)},\quad T\ne\varnothing.
\tag{34}
\]

In particular,

\[
m_{AB}=\log\frac{p_{AB}p_0}{p_Ap_B},\qquad
m_{ABC}=\log\frac{p_{ABC}p_Ap_Bp_C}{p_{AB}p_{AC}p_{BC}p_0}.
\tag{35}
\]

**Proof.** `log p(x)=−V(x)−log Z`. Subtracting endpoint logs gives `E`; the constant
`−log p(x₀)` in the resulting set function cancels because `Σc_T=0`. Likewise `−log Z`
cancels from the mixed difference. Exponentiation of the finite sum proves the product.
Expanding the four and eight signs gives (35). ∎

**Removed-assumption checks.** Zero density yields undefined/infinite logarithms rather
than a finite coefficient. Under `p∝exp(−β_bridge V)`, the log contrast is
`β_bridge m_E` for a constant within-field scale, not necessarily `m_E`. An unaccounted
state-dependent density-of-states factor contributes its own log contrast. A density is
relative to a measure: under `y=f(x)` with a new Lebesgue measure, the density picks up
`−log|det Df|`; nonconstant Jacobians need not cancel. Transforming the reference measure
consistently preserves the original scalar relation. Probabilities of points in continuous
space are zero; (34) uses densities in a declared measure, not point masses disguised as
densities. Finite bin probabilities require integrating over bins or a separately justified
small-bin approximation.

**Intuition / prior art / EBU status.** Potential decrease is an increased equilibrium
density ratio; the interaction is its multiplicative contrast across a coalition cube.
No stationarity or reversibility conclusion follows from the algebra alone. This is
established Gibbs/log-linear/Möbius mathematics; Jansma's direct equation comparison is
in the [appendix](EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md#2-jansma-equation-level-comparison).
The beta-equals-one relation must not be established empirically by defining the physical
branch from the probability branch.

### 24.1 Statistical distinctions

`p(x_S)` usually names densities at intervention/counterfactual endpoints. It is not
necessarily a joint distribution of the binary action indicators. Endpoints can even repeat.
One can *define* artificial weights `q(z)=p(x_z)/Σ_w p(x_w)` on action patterns; their
nonempty anchored log-linear coefficients then equal (34), since normalization cancels.
That construction supplies no empirical action distribution, independence or causal claim.

If instead a positive joint binary distribution `q` is independently declared, the pair
contrast is its ordinary log odds ratio in the face where other indicators equal zero;
the higher contrasts are reference-cell log-linear parameters. A zero pair contrast in
one face does not establish unconditional independence or independence in every context.
For example `log q(z)=constant+a z₁z₂z₃` has anchored pair coefficient zero, but its
conditional pair log odds ratio at `z₃=1` is `a`.

Interaction information is an alternating sum of **marginal entropies**, not of pointwise
log probabilities. Multi-information is `ΣH(X_i)−H(X_N)` and is nonnegative. Connected
information compares maximum-entropy distributions matching successive marginal orders.
Cumulants are derivatives of the log moment-generating function, or partition-lattice
combinations of moments. None is generally equal to (34). A noisy parity distribution
makes the difference explicit in §30. Statistical log-linear coefficients are also
coding/background dependent; a ±1 spin coupling requires its corresponding basis transform.
See appendix R9–R12 for the primary literature and distinct constructions.

## 25. Entropy Möbius theorem

**Corollary D2 (accepted-P4-scope scaling).**

**Assumptions and definitions.** Each coalition entry has a compatible path/process with
the *same* fixed field and temperature, a conservative overdamped single-reservoir model,
the stationary equilibrium density used at both endpoint times, and no omitted additional
work or entropy channels. The canonical energy normalization, state/boundary and entropy
conventions are those in the cleared R-stage §9.2 C and E1a-v4 design §§8–9. These hypotheses
must hold for every coalition in the comparison, including its reference. Define the
medium, stochastic-system and total entropy-change tables for those processes.

**Statement.** In that scope,

\[
\Delta s_{med}(S)=k_BE(S),\quad
\Delta s_{sys}(S)=-k_BE(S),\quad\Delta s_{tot}(S)=0,
\]
\[
m_{\Delta s_{med}}(T)=k_Bm_E(T),\quad
m_{\Delta s_{sys}}(T)=-k_Bm_E(T),\quad
m_{\Delta s_{tot}}(T)=0.
\tag{36}
\]

**Proof.** In the stipulated benchmark, conservative heat to the medium equals `U_pre−U_post`,
so division by `T` gives `k_BE`. Stochastic system entropy is `−k_B log p`, whose endpoint
change is `−k_BE` by (34). Their sum is zero. Apply the linear transform (2) to each
entrywise equality. This includes the empty entry when it is consistently specified. ∎

**Removed-assumption check.** The driven ring of §23 has positive cycle entropy flow
while `V` is constant; the current-carrying Gaussian has density agreement without the
reversible P4 conditions. Imposed actions may inject work, so even perfectly known endpoint
values do not imply (36) for their executed interventions. Hidden reservoirs, field changes
or coarse-grained internal entropy likewise require extra terms. Total entropy is not
universally zero. An expected entropy and a stochastic endpoint entropy are different
objects unless the averaging protocol is supplied.

**Intuition / prior art / EBU status.** This is linearity applied to the already conditional
benchmark relation, not a discovery about entropy. Standard stochastic thermodynamics:
[Seifert](https://arxiv.org/abs/1205.4176). The foundation's separate constrained-macrostate
entropy-deficit relation `S=S_eq−κV` is not silently identified with the stochastic system
entropy above; its ensemble and boundary conditions remain separate. No new P4 experiment,
entropy authority or universal nonequilibrium equivalence is established.

## 26. Testability and uncertainty

### 26.1 What must be compared

For a selected `k`-action face, the unrestricted exact coefficient involves all `2^k`
coalitions. At `k=3`,

\[
m_{ABC}=E(ABC)-E(AB)-E(AC)-E(BC)+E(A)+E(B)+E(C)-E(\varnothing).
\tag{37}
\]

The last entry is structurally zero under §3, so there are seven nontrivial EBU entries,
but eight endpoint potential/density values including the reference. Assumed structural
models may reduce measurement needs; that no longer independently tests an unrestricted
table. Estimating one coefficient does not require all `2^n` coalitions if the remaining
labels are fixed to a declared context.

Comparable interventions require the same initial state/preparation distribution, field,
coordinates, boundary, duration, action extents/meaning, environment and subset semantics.
Quantities fixed across subsets and rules replayed across subsets define different tables.
Feasibility, drift, hidden interventions, resetting/preparation costs, and measurement
selection must be addressed before interpreting a contrast physically. A counterfactual
endpoint cannot be replaced by a convenient interpolation without changing the experiment.

### 26.2 Exact variance identity and systematic error

**Proposition U.** Let a random vector of comparable estimates `\widehat{E}` have finite
second moments and covariance matrix `C_E`; extend `c_T` by zero outside its face. Then

\[
\hat m_T=c_T^T\widehat{\mathbf E},\quad
\operatorname{Var}(\hat m_T)=c_T^TC_Ec_T,\quad
\operatorname{Bias}(\hat m_T)=c_T^T\operatorname{Bias}(\widehat{\mathbf E}).
\tag{38}
\]

**Proof.** Center the vector, expand the square of its linear contrast, and use the
covariance definition; expectation gives the bias formula. No independence is used. ∎

**Removed-assumption check.** Dropping off-diagonal entries is wrong with shared
calibration or baseline estimates. Without finite second moments the variance need not
exist. Uncertainty in the estimated covariance and nonlinear plug-in bias are not covered
merely by writing (38).

**Baseline distinction.** A common additive gauge/error `a` on **all potential estimates**
`\hat G_S` cancels because `Σc_T=0`. An uncertain reference potential `\hat G₀` used in
`\hat E_S=\hat G₀−\hat G_S` for nonempty `S`, with `\hat E_∅=0` exactly, generally
**does not cancel**. Its loading is
`Σ_{S≠∅}c_T(S)=−c_T(∅)=(−1)^{k+1}`. For independent equally uncertain endpoint levels,
`Var(\hat G_S)=σ²` including the baseline, the coefficient variance is `2^kσ²`. Written
as nonempty EBU estimates, the same example has diagonal variances `2σ²` and shared
covariances `σ²`; treating these EBU estimates as independent would overcount uncertainty.

**Equal-variance special cases.** If all `2^k` supplied coalition estimates really are
independent with variance `σ²`, (38) gives `2^kσ²`. However, that premise cannot hold with
positive `σ²` when `E(∅)=0` is imposed exactly. If only the `2^k−1` nonempty EBU estimates
are independent with equal variance and the zero is exact, the answer is
`(2^k−1)σ²`. For a triple, these two legitimate cases give `8σ²` and `7σ²` respectively.
They describe different error models, not competing arithmetic.

**Shared calibration and scale.** For calibration parameters `a`, a first-order uncertainty
model is `δE≈J_a δa+ε`, giving
`C_E≈J_a C_a J_aᵀ+C_ε+J_a Cov(δa,ε)+Cov(ε,δa)J_aᵀ`.
These are local propagation approximations; (38) remains exact for the actual covariance.
A common multiplicative scale `b` changes the coefficient to `b m_E`; it does not cancel
like an offset. First-order propagation adds `m_E² Var(b)` and correlation terms when
`b` is estimated. Field curvature/temperature calibration can correlate every coalition
and the two measurement branches. Coalition-specific noise, model discrepancy and field
drift need separate bias/covariance treatment.

For deterministic bounded errors, if each of `2^k` potential levels has absolute error at
most `η`, then `|δm_T|≤2^kη` by the triangle inequality. If the empty EBU is exact and the
other EBU errors are separately bounded by `η`, the bound is `(2^k−1)η`. Tighter bounds
require declared correlation or structure. No confidence level, sample size, threshold or
hypothesis decision has been preregistered here.

### 26.3 What a nonzero quadratic-benchmark triple would mean

The null theorem is a conjunction: one fixed quadratic potential on a sufficient state
representation; fixed additive action displacements; a common field/baseline/protocol;
all required admissible subset values; and accurate comparable valuation. A statistically
resolved `m_ABC≠0` is inconsistent with that conjunction. It does **not** uniquely prove
that `V` is nonquadratic. Alternatives include nonadditive response/nonlinear generator,
constraint resolution, unrepresented state, field drift, measurement error and model
misspecification. Conversely a zero triple does not establish the conjunction or exclude
higher orders elsewhere. Small-action high-order signals of size `ε^k` can become difficult
to resolve against errors even when the exact formula is correct.

**Prior art / status.** Linear-contrast variance and delta-method propagation are standard;
this is a theoretical design analysis only. The exponential number of corners and error
amplification motivate careful targeted benchmarks, not claims of universal scalability.

## 27. Theorem-driven experimental programme

These are **proposals, not preregistrations**. Only the allowed scratch algebra corresponding
to Test 0 was performed in this report. No official SD, E1a or future topology campaign ran.

| Proposed test | Target prediction / comparison | Necessary scientific preparation | Status |
|---|---|---|---|
| 0 — deterministic algebra | Inversion, recursion, degree ceiling, polynomial examples, probability signs, entropy linearity | Exact finite tables and symbolic expressions | Scratch checks performed; certificate below; not a model execution |
| 1 — additive quadratic triple null | `m_ABC=0` | Independent confirmation of fixed increments, quadratic domain, fixed field and covariance model | Proposed only |
| 2 — quadratic pair | `m_AB=−h_AᵀHh_B` | Independent `H` and displacements; full four-corner comparison | Proposed only |
| 3 — controlled cubic positive benchmark | `m_ABC=−λabc` | A physical domain where a declared cubic contribution is justified; stability/boundary/scale accounting | Proposed only |
| 4 — quadratic potential, nonlinear response | Nonzero triple predicted by a separately identified response law | Distinguish response nonlinearity from potential error; e.g. §20's map as an algebraic target | Proposed only |
| 5 — equilibrium two-branch interaction bridge | Branch A physical-potential contrast versus Branch B density log contrast | Independent calibration and reference measure, comparable endpoints, joint uncertainty, density-support checks | Proposed only; no circular construction of A from B |
| 6 — later cross-field interaction | Commensurate higher-order contrasts across fields | Prior evidence for denomination/scale comparability, declared action matching | Future only; fixed-field theorem does not authorize it |

A post-E1a benchmark should begin with the pair prediction and triple null before attempting
a positive high-order physical case. This is a logical dependency, not an adopted execution
order or apparatus selection. Candidate controls, intervention feasibility, statistical
thresholds and power require a separate scientific design and approval stage. The current
`beta_bridge=1` E1a target and its pause are unchanged.

## 28. Prior-art comparison

The [separate appendix](EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md) is necessary to keep the
proof sequence readable while documenting search coverage and the requested equation-level
comparison. Searches were performed through **2026-10-05**, including 2025–2026 work.
This is a substantive targeted review, not a publication-level proof of absence of antecedents.

| Mathematical construction | Closest established setting | Exact relation / distinction |
|---|---|---|
| `E:2^N→R` | Cooperative game / pseudo-Boolean function | Exactly the same mathematical object; actions add physical declarations |
| `m_E(T)` | Harsanyi dividend / Boolean Möbius coefficient | Exactly the same normalized coefficient, not a new interaction index |
| Recursive marginal differences | Reference-background epistasis | Same alternating differences; genotype/phenotype semantics differ from physical action/potential semantics |
| Multilinear extension and its derivatives | Set-function calculus; Shapley and Banzhaf interactions | Anchored coefficient differs from averages across contexts and attribution rules |
| Functional ANOVA / Sobol decomposition | Orthogonal decomposition relative to a product input measure | Depends on integration and centering; variance contributions are not signed anchored dividends |
| Pair/triple probability products | Reference-cell log-linear interactions / Gibbs couplings | Same formulas once a positive binary distribution and coding are specified; coalition endpoints do not automatically constitute one |
| Interaction information / connected information | Entropy contrasts and maximum-entropy hierarchies | Different observables and transforms, not equal merely because both use “interaction” |
| General chain rule | Set-partition Faà di Bruno | Standard calculus; no unique coordinate-free allocation between response and potential terms |
| Controlled response and generator powers | Lie derivatives, Volterra and Chen–Fliess expansions | Composition with Möbius inversion is immediate; finite-order bounds require the stated hypotheses |
| Equilibrium density / rate / entropy relations | Gibbs statistics and stochastic thermodynamics | Known physical relations with independent model, measure and accounting assumptions |

Jansma is especially close to the energy/probability synthesis; Grabisch–Marichal–Roubens
is especially close to the exact discrete derivative and multilinear mathematics. Neither
should be displaced by an EBU-specific name for those results. Newer energy-fragmentation
and Shapley-interaction work found in 2026 strengthens the need to acknowledge the broader
established programme. Their empirical/computational studies were not reproduced here.

## 29. Novelty matrix

**NO NOVELTY CLAIM IS AUTHORISED BY THIS REPORT.** Classification below concerns the
mathematical relationship, not publication priority or acceptance into EBU authority.

| Candidate result | Classification | Reason / permitted EBU claim |
|---|---|---|
| Möbius equals discrete derivative | KNOWN STANDARD RESULT | Boolean inversion, §4 |
| Unique multilinear / discrete-Taylor expansion | KNOWN STANDARD RESULT | Pseudo-Boolean / Harsanyi representation, §5 |
| Recursive higher-order interpretation | KNOWN RESULT IN DIFFERENT NOTATION | Contextual finite differences / epistasis, §6 |
| Sequential rebasing and parallel correction | DIRECT COROLLARY | Endpoint cancellation and Möbius identity; physical endpoint compatibility explicit |
| Repeated-FTC representation | KNOWN STANDARD RESULT | Iterated one-dimensional FTC, §9 |
| Continuous Taylor leading term and remainder | DIRECT COROLLARY | Classical local regularity and Taylor estimates, §10 |
| Polynomial-degree ceiling | DIRECT COROLLARY | Affine substitution and Boolean degree reduction, §11 |
| Quadratic pair-only result | KNOWN RESULT IN DIFFERENT NOTATION | Elementary quadratic algebra; already in frozen foundation |
| Composite `V∘x` theorem | DIRECT COROLLARY | Apply the known transform to a composite table |
| Generator–flow–Möbius theorem | DIRECT COROLLARY | Well-posed response map plus finite inversion |
| Potential versus response derivative terms | KNOWN STANDARD RESULT | Chain rule / Faà di Bruno; split not canonical |
| Control-affine short-time order bound | DIRECT COROLLARY | Word degree in Lie-derivative expansion, §19 |
| Canonical log-probability coefficients | KNOWN PHYSICS + EBU NOTATION | Gibbs/log-linear interactions; direct Jansma antecedent |
| Entropy Möbius scaling | KNOWN PHYSICS + EBU NOTATION | Conditional P4 relation followed by linearity |
| Finite-table uncertainty propagation | KNOWN STANDARD RESULT | Linear-contrast covariance; baseline cautions contextualized |
| Registration / new-action pricing / preserved entries | NEW EBU SYNTHESIS (architectural description only) | A proposed combination of declared roles; no proof of uniqueness, fairness or novelty |
| Entire potential–response–coalition–denomination–account chain | NEW EBU SYNTHESIS; NOVELTY UNCLEAR | Coherent project organization; no exhaustive architecture-level priority determination |
| Cross-field stable denomination | NOVELTY UNCLEAR; OPEN PHYSICAL PROGRAMME | Not proved by fixed-field algebra; independent calibration/evidence required |

No row is promoted to **POTENTIALLY NOVEL RESULT** on the evidence of this review. That
category remains available in principle but is not needed to describe the work honestly.
The synthesis may be useful without any new Möbius theorem. Publication-level novelty
requires independent theorem audit, dedicated verification of the literature review and
external expert review. In particular, algebraic closure does not establish a scientifically
new unit, a universal economic value measure or stable capacity dynamics.

## 30. Counterexamples

### 30.1 Campaign against the tempting generalizations

All examples below are deterministic analytic constructions. No model or stochastic
experiment was run.

| Statement attacked | Counterexample / exact disposition |
|---|---|
| Nonquadratic `V` always causes high-order synergy | `V(x,y)=x⁴+y²/2`, actions only in `y`: every order above two vanishes. Scalar `x⁴` at baseline `−3/2` with three unit increments has selected triple zero. |
| Quadratic `V` never causes high-order synergy | §20.1: `x=s+z₁z₂`, `V=x²/2`, triple `−1`. |
| Nonlinear `x` always causes high-order synergy | `x(z)=√(1+Σz_i)`, `V=x²/2`, baseline 1: `E=−Σz_i/2`. |
| Zero triple implies quadratic `V` | Scalar quartic cancellation above; one selected coefficient cannot determine a function globally. |
| Pair synergy means path dependence | §7: quadratic unit translations give pair `−1` while every fixed-endpoint potential integral is path independent. |
| Boltzmann density means detailed balance | §23.2's skew OU current or §23.3's biased ring with uniform density. |
| Log-probability Möbius equals interaction information | Noisy parity example below; one is an unbounded signed log contrast, the other a bounded entropy contrast. |
| Möbius coefficients uniquely determine causal attribution | A value table has no causal model or institutional allocation axiom. Foundation §15's exact endpoint example admits `(1/2,1/2)`, `(1,0)` and `(0,1)` allocations with the same total and unchanged table. |
| Generator nonlinearity necessarily gives nonzero interaction | §20.4's nonlinear `u/(2x)` flow produces a modular value table. |
| Linear-in-state generator gives pair-only forever | §20.2's bilinear `u x` flow yields every order. Joint affine dependence with control-independent state matrix is a sufficient replacement. |
| The empty coalition always remains `x₀` under a flow | §18's natural drift `ẋ=1+u`; raw empty value `−1`. |
| Any sequential execution reaches the coalition endpoint | Noncommuting fields in §20.5; state/field protocol must establish compatibility. |
| `C^k` guarantees an `O(ε^{k+1})` remainder | §10's `x_+^{k+α}` has only `ε^{k+α}` remainder. |
| Pair curvature/response split is extension independent | §16.3's same vertices give split `(1,0)` versus `(7/6,−1/6)`. |
| A zero anchored pair log ratio proves action independence | `log q=constant+a z₁z₂z₃` has pair zero at the reference face and nonzero pair at background `z₃=1`. |
| Common baseline uncertainty always cancels | §26: structural `E_∅=0` leaves reference loading `(−1)^{k+1}`. |

The attribution example is underdetermination, not a proposed causal model: an aggregate
interaction coefficient has no variable that selects which actor owns it. Even distributing
a pair dividend as `(λm_AB,(1−λ)m_AB)` preserves the group total for every `λ`; selecting
`λ` requires an additional rule. The theorem does not select one.

### 30.2 Explicit information counterexample

Let a positive binary distribution assign mass `(1−δ)/4` to each even-parity three-bit
pattern and `δ/4` to each odd-parity pattern, where `0<δ<1/2`. Every single-bit marginal
is uniform, and every pair is independent uniform. The anchored triple log contrast is

\[
I_{\log}=4\log\frac{\delta}{1-\delta}.
\]

The entropy co-information convention
`I₃=H(A)+H(B)+H(C)−H(AB)−H(AC)−H(BC)+H(ABC)` gives

\[
I_3=h(\delta)-\log2,\qquad
h(\delta)=-\delta\log\delta-(1-\delta)\log(1-\delta).
\]

As `δ↓0`, the first diverges to `−∞`, while the second approaches `−log 2`.
The opposite convention for interaction-information sign remains bounded and cannot
restore equality. Multi-information is instead `log2−h(δ)≥0`. This example distinguishes
three objects even when a genuine joint binary distribution is available.

### 30.3 Exact validation certificate

A standard-library scratch program, outside the repository, evaluated rational tables,
formal polynomials, derivatives, integrals and finite sums. It imported no repository
module, created no scientific RNG, and solved no trajectory numerically. Its full source
is preserved as a documentation code block in Appendix A below, so validation is reviewable
without committing implementation files. Formal exponential coefficients and exact
substitution `exp(2τ)=2` are algebraic checks of (25), not time stepping.

| Check | Exact result |
|---|---|
| Inversion on every delta-function basis table for `n=0,…,6` | 127 basis tables; 5,461 reconstruction equalities; all passed |
| Context/recursion on four-action table `F(s)=3+s³−7s` (integer mask `s`) | 81 disjoint context/set pairs; every available fresh-label recursion passed |
| Boolean degree ceiling for four-variable monomials of total degree ≤4 | 70 monomials checked |
| Quadratic `V=3x²/2`, baseline 1/2, increments `(1,2,−1)` | `m_AB=−6`, `m_ABC=0`; rebased identity also `−6` |
| Cubic `V=5x³/6`, increments `(2,−3,4)` | Triple `120` |
| Quartic `V=2x⁴/24`, baseline 7, increments `(1,2,−1,3)` | Four-way `12` |
| Quadratic potential plus §20.1 nonlinear map | Complete eight-entry rational table; triple `−1` |
| Linear potential plus product map | Triple `−1` |
| Quartic with zero selected triple | Exactly `0` |
| Mixed cubic response | Formula (27) at six declared rational `α`; at `α=1`, `−4` with integrals `9/4` and `7/4` |
| Faà di Bruno versus direct polynomial differentiation | Exact equality at orders 1–4 for a quartic composed with a four-variable nonlinear map |
| Composite derivative integral versus vertex contrast | Exact equality at orders 1–4 on that same polynomial |
| Same-vertex extension split | Quadratic integral split `(1,0)` versus `(7/6,−1/6)`; totals agree |
| Generator-linear additive short-time case | `ẋ=Σz_i`, quadratic `V`: pair coefficient of `τ²` is `−1`, triple zero |
| Generator-bilinear case | First nonzero formal coefficients for orders 1–5 are `−2^{k−1}`; exact finite-time coefficients at `exp(2τ)=2` equal `−1/2` for orders 1–6 |
| General short-time derivative formulas | Exact polynomial equality of second/third Lie derivatives for `b=x²+u`, `V=x⁴/4` |
| Positive weights `(2,3,5,7,11,13,17,19)` in bitmask order | Pair product `14/15`, triple product `3135/3094`; common normalization cancels |
| Entropy linearity | Every coefficient scales; exact rational representative `k_B=7/3` checks the implementation of the algebra; arbitrary `k_B` proved in §25 |
| Variance contractions | Independent eight potential levels: `8σ²`; independent seven EBU entries: `7σ²`; shared-baseline EBU covariance: `8σ²` |

The first draft of a scratch extension check incorrectly expected its curvature contribution
to remain 1; exact integration returned `7/6`. The expectation was corrected and the
compensating response `−1/6` verified. This is not an altered scientific outcome or a tuned
model: it exposed the very nonuniqueness illustrated in §16.3. All results reported above
are the final checked algebra. Finite checks support the worked examples; the general
claims rest on proofs, and the author's own checks do not constitute independent audit.

## 31. Book-1 theorem map

The generator is **an interface**, not a prerequisite for finite valuation. The endpoint
identity makes sense for discrete, hybrid or measured transitions without an ODE. A
specified generator explains how endpoints arise and may add physical predictions. Its
adoption and empirical validation are separate physical extensions; its mathematics can
be taught now as a conditional interface after audit. “Future only” applies to adopting
missing constitutive laws and institutional policies, not to writing the abstract theorem.

Proposed non-binding order:

| Order | Teaching step | Candidate dependency |
|---:|---|---|
| 1 | State potential and canonical sign | Foundation §3; present §§2–3 |
| 2 | Exact path integral | Cleared R-stage; fixed-field `C¹` assumptions |
| 3 | Sequential telescoping and rebasing | SP, §7 |
| 4 | Simultaneous coalition endpoints and common baseline | §3; admissibility before inversion |
| 5 | Exact Möbius / discrete Taylor expansion | A and A2, §§4–5 |
| 6 | Recursive marginal/pair/triple explanation | A1, §6 |
| 7 | Additive actions, mixed derivatives and local Taylor | B/B1/B1a/B2/B3, §§8–13 |
| 8 | Generator and transition-map interface | C, §§17–19; empty-coalition caveat |
| 9 | Potential, response and mixed interaction sources | CM/CR, §§14–16, 20; noncanonical split |
| 10 | Canonical density bridge | Cleared R-stage hierarchy; §23 |
| 11 | Log-probability interaction | D, §24; joint-distribution distinction |
| 12 | Conditional entropy representation | D2, §25 |
| 13 | Nonequilibrium boundary and uncertainty | §§22–26; current does not destroy a supplied potential |
| 14 | Future action registration and economic/account layer | §2.3 and authority gaps; no attribution theorem invented |

This teaching spine does not replace the repository's current eight-part editorial plan.
Its existing Part I introduces physical objects, Part II develops mathematics/evidence,
Part V deepens interaction/topology, and Part VIII owns institutions. A future editor can
place the introductory theorem chain and defer advanced proofs appropriately. No page-count
promise, chapter rewrite, manuscript integration or book-file modification occurs here.

Independent audit must cover A/A1/A2; SP and its endpoint compatibility; B/B1/B1a/B2/B3;
CM/CR including extension dependence; C including drift normalization; ST/ST-affine and
bracket orientation; MC's observable/domain distinction; D and reference measures; D2's
full P4 scope; U's baseline/scale covariance; every counterexample and the prior-art mapping.
Authority consistency and the separation of physical value from actor attribution are
part of that audit, not optional editorial polish.

## 32. Authority gaps / human decisions

| Issue | Classification | Required disposition |
|---|---|---|
| Finite inversion, recursion, unique polynomial, calculus proofs | MATHEMATICALLY SETTLED under listed assumptions; KNOWN PRIOR ART | Independent checking of this report before integration; no new human choice needed to make the identities true |
| Canonical sign and foundation quadratic bound | CURRENT AUTHORITY | Preserve unchanged |
| R-stage clearance | CURRENT TASK DISPOSITION supplied by user | Accepted for this stage; no manufactured re-clearance gate |
| Adopting S-MG wording into books or authority | THEORY AUTHORITY GAP | Independent theorem audit first; later explicit integration authorization |
| Choice of an action universe, reference context, horizon and missing-corner treatment | DEFINITIONAL CHOICE | Must be specified in each future model; no universal completion of infeasible subsets |
| Concrete vector field, discrete map or constraint resolver | EXPERIMENTAL CHOICE / APPARATUS-DEPENDENT | Identify and validate separately; abstract theorem does not choose it |
| Drift comparator versus no-drift baseline | DEFINITIONAL CHOICE | State raw/relative semantics explicitly; do not silently change current actor valuation |
| Weak regularity beyond iterated FTC / nonsmooth hybrid calculus | THEORY AUTHORITY GAP | Exact finite result remains valid; generalized derivative theory only if separately developed |
| Canonical ensemble, support, reference measure and scale | APPARATUS-DEPENDENT / CURRENT CONDITIONAL AUTHORITY | Independent physical justification and calibration |
| Higher-order physical benchmark design | EXPERIMENTAL CHOICE; later HUMAN SCIENTIFIC DECISION REQUIRED | Separate proposed design, apparatus, thresholds and authorization; none needed to finish this report |
| Cross-field stable denomination and action matching | EXPERIMENTAL CHOICE / OPEN PHYSICAL QUESTION | Future commensurability evidence; keep fixed-field theorem separate |
| Entropy beyond accepted P4, driven/multiple reservoirs | FUTURE NONEQUILIBRIUM THEORY | No universal entropy scaling claimed |
| Causal ownership and institutional allocation | THEORY AUTHORITY GAP; later HUMAN SCIENTIFIC DECISION REQUIRED | Supply causal/institutional rules independently; algebra does not select them |
| Architecture-level novelty and priority | KNOWN PRIOR ART for components; NOVELTY UNCLEAR for the whole architecture | Dedicated literature verification and external expert review |

There is **no human scientific decision required to complete the authorized report-only
S-MG task**. Future choices are listed as future work, not used to stop current derivations
or to revive cleared R-stage blockers. No foundation amendment is proposed or performed.

## 33. Final disposition

### 33.1 Answers to all required questions

| Question | Answer |
|---|---|
| Q1 — Is Möbius synergy exactly a higher-order discrete difference of coalition value? | **YES**, for the declared complete Boolean table: `m_E(T)=Δ_TE(∅)`. |
| Q2 — Is it the negative difference of `V∘x`? | **YES**, for nonempty `T`, canonical endpoint orientation and common fixed baseline/field. |
| Q3 — Is the multilinear/discrete-Taylor representation exact? | **YES, QUALIFIED**: exact unique multilinear vertex representation, not a claim that an arbitrary physical interpolation is multilinear. |
| Q4 — Is k-way interaction recursively a change in order k−1? | **YES**, with distinct added labels and a declared disjoint context. |
| Q5 — Do additive displacements give k-fold physical differences? | **YES**, with fixed vectors and all required endpoints in the domain. |
| Q6 — Does repeated FTC hold? | **CONDITIONAL** on neighborhood/pullback `C^k` or an explicitly valid iterated-FTC regularity condition. |
| Q7 — Is the small-action leading term controlled by `D^kV`? | **CONDITIONAL** on additive scaled directions and regularity; `C^k` gives little-o order k, local Lipschitz `D^kV` gives big-O order k+1. |
| Q8 — Do affine map plus degree-d potential imply no orders above d? | **YES, CONDITIONAL** on those hypotheses; Boolean reduced restricted degree can be sharper. |
| Q9 — Do quadratic plus additive actions eliminate all orders ≥3? | **YES** under fixed field, fixed increments and defined subset values. |
| Q10 — Can quadratic potential have high orders through nonlinear response? | **YES**; §§20.1–20.2 give exact triple and all-order examples. |
| Q11 — Is the general object `V∘x`? | **YES**, on the registered coalition domain; no unique split into physical origins follows. |
| Q12 — Can a generator connect rigorously through its flow? | **CONDITIONAL** on a well-posed finite-horizon evolution, registered control mapping and consistent empty baseline. |
| Q13 — Is the historical f/J/Ψ chain required? | **NO**; it is one possible, separately declared physical construction. |
| Q14 — Can generator nonlinearity create high-order interaction? | **YES**, but not necessarily; §20.4 gives a nonlinear zero-interaction counterexample. |
| Q15 — Do canonical density conditions give exact log-probability coefficients? | **YES, CONDITIONAL** on the declared positive density/measure relation at all endpoints; no reversibility inference from density alone. |
| Q16 — Does accepted P4 give `k_B` medium-entropy scaling? | **YES, CONDITIONAL** on the full P4 conditions for every entry, including no omitted work. |
| Q17 — Is the core mathematics known elsewhere? | **YES**; standard algebra/calculus/physics and direct corollaries. |
| Q18 — Closest prior art? | Grabisch–Marichal–Roubens (2000), Eqs. (8), (10), (19), (23), for dividends and derivatives; Jansma (2025), version-5 preprint §III C.1 Eqs. (41)–(47), for energy/log-probability interactions; Harsanyi, pseudo-Boolean and epistasis traditions are direct antecedents. |
| Q19 — What may be distinctive? | The declared combination of physical endpoint valuation, registered actions, joint-before-attribution accounting, response physics, independent beta calibration, future denomination testing and non-repriced capacity records. **No novelty claim; architecture-level priority remains unestablished.** |
| Q20 — Generator classification? | **INTERFACE**; concrete dynamical laws are PHYSICAL EXTENSIONS. It is not foundational to finite valuation. |
| Q21 — What needs independent audit before Book 1? | The complete theorem/proof/assumption list in §31, worked counterexamples, authority compatibility, statistical/entropy boundaries and prior-art mapping. |
| Q22 — Does S-MG change core `beta_bridge=1` E1a target? | **NO**. The target, pause, identities and execution authorization remain unchanged. |
| Q23 — Does it suggest a post-E1a higher-order topology benchmark? | **YES, CONDITIONAL**: §27's pair/triple and nonlinear-response comparisons are proposals requiring a separate design and authorization. |

### 33.2 Scientific identities and scope

Identity verification used strict JSON parsing, static AST extraction of constants and
source lists, and SHA-256 hashing only. No scientific module was imported. The analysis
recipe in `e1a_v4/identity.py` binds implementation identity, foundation/baseline/design/
contract hashes, its exact scientific-module list, adopted rules, configuration `{}` and
seed-map schema. The execution recipe in `e1a_v4/validation/plan.py` adds its exact
validation-module list, JSON and Markdown plan hashes, seed map and separate driver bytes.
The seal is outside that recipe and was checked separately. **Neither S-MG report is in
any of these inspected preimages.** Source-list exclusion was checked explicitly, not
assumed from a report-only filename.

The following hashes are the verified starting values and the required unchanged final
values. An enclosing Git commit necessarily changes repository commit/tree identities;
that is different from changing a defined scientific procedure identity.

| Bound object | SHA-256 |
|---|---|
| Frozen foundation (49,098 bytes) | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| Foundation metadata | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| Working theory baseline | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| Repaired R-stage report | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| E1a design | `25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6` |
| E1a contract | `d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4` |
| Validation plan JSON | `fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4` |
| Validation plan Markdown | `2d40781593c607de31e68f42e713641a97335e198ed3453bbe677e76682f0d93` |
| Seed map | `c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af` |
| Execution seal | `4df7bb145c588efe6cff788efa5e4f29b6d2aba23e75333f37ef84d8c43715a9` |
| Analysis procedure identity (configuration `{}`) | `60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527` |
| Execution procedure identity | `442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b` |

Plan and seal both retain `execution_authorised=false`; seal state is `PRE_DRIVER` and
expected execution identity is `null`. The historical label does not mean driver code is
absent: the inspected identity recipe hashes the driver bytes that exist. No official
`results/e1a_v4_validation` directory was created. Existing authority, books, code, seeds,
plans, seals and result artifacts were left unchanged.

The only committed changes in this stage are this theorem report and its prior-art appendix.
Validation consists of the exact certificate, proof and counterexample review, required
section/question/source-link checks, complete diff inspection, whitespace checks and
before/after identity recomputation. A focused new commit preserves the repair commit and
all earlier history. No push is authorized or performed. Independent theorem audit is the
next possible stage and has **not** been performed by this report's author.

```text
S-MG THEOREM PACKAGE:         COMPLETE — INDEPENDENT AUDIT REQUIRED
BOOK 1 READY FOR INTEGRATION: NO — INDEPENDENT THEOREM AUDIT REQUIRED
AUTHORITY MODIFIED:          NO
BOOK FILES MODIFIED:         NO
CODE MODIFIED:               NO
SCIENTIFIC RNG:              NOT USED
TRAJECTORY / MODEL EXECUTION: NONE
OFFICIAL LONG-RUN CAMPAIGN:  NOT RUN
REAL OPTICAL-TRAP EXPERIMENT: NOT RUN
EXECUTION AUTHORISED:        FALSE
PUSH:                       NO
```

## Appendix A. Reproducible scratch algebra certificate

This code block is documentary validation material, not an EBU implementation or an
experiment runner. It can be copied to a temporary file and run with standard Python 3.
It needs no repository imports or dependencies. The formal proof of arbitrary-order
identities remains in the numbered sections; bounded checks are not substituted for proof.

Scratch source SHA-256: `729be79514b5a1bbfddc24400963aa61899db3686b828bbdf25f44fe6465ffc5`.

```python
"""S-MG scratch algebra certificate. Standard library; no repository imports or RNG."""
from fractions import Fraction as F
from itertools import product
from math import factorial, prod
import json

checks = {}
def subsets(t):
    return [s for s in range(t + 1) if s & t == s]
def mob(v, t):
    return sum(((-1)**(t.bit_count()-s.bit_count())*v[s] for s in subsets(t)), F(0))
def table(n, endpoint, potential):
    g = [potential(endpoint(tuple((s >> i) & 1 for i in range(n)))) for s in range(1 << n)]
    return [g[0]-a for a in g]
def check(label, actual, expected):
    assert actual == expected, (label, actual, expected)
    checks[label] = str(actual)

# Exhaustive basis verification, not statistical trials or parameter fitting.
basis_tables = reconstruction_equalities = 0
for n in range(7):
    for r in range(1 << n):
        v = [F(s == r) for s in range(1 << n)]
        m = [mob(v,t) for t in range(1 << n)]
        for s in range(1 << n):
            assert sum(m[t] for t in subsets(s)) == v[s]
            reconstruction_equalities += 1
        basis_tables += 1
checks['basis_tables_n0_to_n6'] = basis_tables
checks['basis_reconstruction_equalities'] = reconstruction_equalities

quad = table(3, lambda z: F(1,2)+sum(F(h)*a for h,a in zip((1,2,-1),z)), lambda x: F(3,2)*x*x)
check('quadratic_pair',mob(quad,3),-6)
check('quadratic_triple',mob(quad,7),0)
check('sequential_rebase',quad[3]-quad[1]-quad[2],mob(quad,3))
cubic=table(3,lambda z: sum(F(h)*a for h,a in zip((2,-3,4),z)),lambda x: F(5,6)*x**3)
check('cubic_lambda5_a2_bminus3_c4',mob(cubic,7),120)
quartic=table(4,lambda z: F(7)+sum(F(h)*a for h,a in zip((1,2,-1,3),z)),lambda x: F(2,24)*x**4)
check('quartic_lambda2_a1_b2_cminus1_d3',mob(quartic,15),12)
nonlinear=table(3,lambda z: F(sum(z)+z[0]*z[1]),lambda x:x*x/2)
check('quadratic_nonlinear_triple',mob(nonlinear,7),-1)
check('quadratic_nonlinear_table',nonlinear,[F(0),F(-1,2),F(-1,2),F(-9,2),F(-1,2),F(-2),F(-2),F(-8)])
linear=table(3,lambda z:F(prod(z)),lambda x:x)
check('linear_potential_nonlinear_triple',mob(linear,7),-1)
zero=table(3,lambda z:F(-3,2)+sum(z),lambda x:x**4)
check('nonquadratic_selected_triple_zero',mob(zero,7),0)
# Mixed cubic example: independently expand scalar formula at several exact alpha.
for a in (F(-2),F(-1),F(0),F(1),F(2),F(1,3)):
    mixed=table(3,lambda z:F(sum(z))+a*z[0]*z[1],lambda x:x**3/6)
    check('mixed_cubic_alpha_'+str(a),mob(mixed,7),-1-F(5,2)*a-a*a/2)

# Rational polynomial ring; normal derivatives/integrals, not Boolean derivatives.
D=4; O=(0,)*D
def const(c): return {O:F(c)} if c else {}
def var(i): return {tuple(int(j==i) for j in range(D)):F(1)}
def add(*ps):
    out={}
    for p in ps:
        for a,c in p.items(): out[a]=out.get(a,F(0))+c
    return {a:c for a,c in out.items() if c}
def scale(p,c): return {a:v*c for a,v in p.items() if v*c}
def mul(p,q):
    out={}
    for a,c in p.items():
        for b,d in q.items():
            e=tuple(x+y for x,y in zip(a,b));out[e]=out.get(e,F(0))+c*d
    return {a:c for a,c in out.items() if c}
def power(p,k):
    out=const(1)
    for _ in range(k):out=mul(out,p)
    return out
def deriv(p,i):
    out={}
    for a,c in p.items():
        if a[i]:
            b=list(a);b[i]-=1;out[tuple(b)]=c*a[i]
    return out
def ds(p,indices):
    for i in indices:p=deriv(p,i)
    return p
def ev(p,z):return sum((c*prod(F(v)**a for v,a in zip(z,e)) for e,c in p.items()),F(0))
def integ(p,indices):
    # Other coordinates are anchored at zero.
    return sum((c/prod(F(e[i]+1) for i in indices) for e,c in p.items() if all(e[j]==0 for j in range(D) if j not in indices)),F(0))
def partitions(xs):
    if not xs:yield [];return
    a,*rest=xs
    for p in partitions(rest):
        yield [(a,)]+p
        for j in range(len(p)):yield p[:j]+[(a,)+p[j]]+p[j+1:]
z=[var(i) for i in range(D)]
x=add(*z,mul(z[0],z[1]),scale(mul(z[2],z[3]),2))
g=scale(power(x,4),F(1,24))
for k in range(1,5):
    inds=tuple(range(k));terms=[]
    for pi in partitions(list(inds)):
        p=scale(power(x,4-len(pi)),F(1,factorial(4-len(pi))))
        for block in pi:p=mul(p,ds(x,block))
        terms.append(p)
    assert add(*terms)==ds(g,inds)
    e=[ev(g,(0,0,0,0))-ev(g,tuple((s>>i)&1 for i in range(D))) for s in range(16)]
    assert mob(e,(1<<k)-1)==-integ(ds(g,inds),inds)
checks['chain_rule_and_composite_FTC_orders'] = '1,2,3,4: exact polynomial equality'
# Split the mixed cubic triple into derivative-origin contributions.
x3=add(z[0],z[1],z[2],mul(z[0],z[1]))
potential_term=mul(mul(deriv(x3,0),deriv(x3,1)),deriv(x3,2))
response_term=mul(x3,deriv(deriv(x3,0),1))
check('mixed_cubic_potential_derivative_integral',integ(potential_term,(0,1,2)),F(9,4))
check('mixed_cubic_response_derivative_integral',integ(response_term,(0,1,2)),F(7,4))
check('mixed_cubic_triple_total',-integ(add(potential_term,response_term),(0,1,2)),-4)
# Fixed vertices, changed extension redistributes derivative integrals.
xa=add(z[0],z[1]);xb=add(xa,mul(mul(z[0],add(const(1),scale(z[0],-1))),z[1]))
check('extension_A_curvature',integ(mul(deriv(xa,0),deriv(xa,1)),(0,1)),1)
check('extension_B_curvature',integ(mul(deriv(xb,0),deriv(xb,1)),(0,1)),F(7,6))
check('extension_B_response',integ(mul(xb,ds(xb,(0,1))),(0,1)),F(-1,6))
# This simpler vertex-vanishing bump happens not to change the quadratic split.
xc=add(xa,mul(z[0],add(const(1),scale(z[0],-1))))
assert integ(mul(deriv(xc,0),deriv(xc,1)),(0,1))==1
# Use nonlinear potential cubic to get nontrivial split with the first bump.
curv=scale(mul(xb,mul(deriv(xb,0),deriv(xb,1))),2)
resp=mul(power(xb,2),ds(xb,(0,1)))
check('extension_cubic_curvature',integ(curv,(0,1)),F(47,20))
check('extension_cubic_response',integ(resp,(0,1)),F(-7,20))
assert integ(add(curv,resp),(0,1))==2
# Formal flow certificates: polynomial coefficients in time, no integration of a model.
# xdot=u*x, x0=1, V=x^2/2; for r>=1, E coefficient is -2^(r-1)*u^r/r!.
for k in range(1,6):
    for r in range(k+1):
        v=[F(0) if r==0 else F(-2**r,2*factorial(r))*F(s.bit_count())**r for s in range(1<<k)]
        val=mob(v,(1<<k)-1)
        if r<k:assert val==0
        else:assert val==-2**(k-1)
checks['bilinear_flow_first_nonzero_orders'] = 'k=1..5: coefficient -2^(k-1) at tau^k'
# Exact finite-time algebra at exp(2*tau)=2, equivalently tau=log(2)/2.
for k in range(1,7):
    v=[(F(1)-F(2)**s.bit_count())/2 for s in range(1<<k)]
    assert mob(v,(1<<k)-1)==F(-1,2)
checks['bilinear_flow_finite_time_orders'] = 'k=1..6: -1/2 at exp(2*tau)=2'
# Linear additive generator xdot=sum(z), x0=0: E=-tau^2 (sum z)^2/2.
v=table(3,lambda z:F(sum(z)),lambda x:x*x/2)
check('linear_additive_flow_pair_tau2_coefficient',mob(v,3),-1)
check('linear_additive_flow_triple',mob(v,7),0)
# Probability ratios: exact rational product; logarithms remain symbolic.
w=[F(2),F(3),F(5),F(7),F(11),F(13),F(17),F(19)]
p=[a/sum(w) for a in w]
def ratio(p,t):return prod(p[s]**((-1)**(t.bit_count()-s.bit_count())) for s in subsets(t))
check('probability_pair_product',ratio(p,3),F(14,15))
check('probability_triple_product',ratio(p,7),F(3135,3094))
check('probability_normalization_cancels',ratio(p,7),ratio(w,7))
for t in range(8):
    assert mob([F(7,3)*a for a in nonlinear],t)==F(7,3)*mob(nonlinear,t)
    assert mob([-F(7,3)*a for a in nonlinear],t)==-F(7,3)*mob(nonlinear,t)
checks['entropy_formal_scaling'] = 'all eight coefficients; symbolic linearity represented at kB=7/3'
# Covariance contractions from explicit error loadings; exact baseline treatment.
k=3;c=[F((-1)**(k-s.bit_count())) for s in range(8)]
C=[[F(i==j) for j in range(8)] for i in range(8)]
check('independent_eight_G_variance',sum(c[i]*C[i][j]*c[j] for i in range(8) for j in range(8)),8)
check('independent_seven_E_variance',sum(c[i]*c[i] for i in range(1,8)),7)
Cshared=[[F(0) if i==0 or j==0 else F(1)+F(i==j) for j in range(8)] for i in range(8)]
check('seven_E_shared_baseline_variance',sum(c[i]*Cshared[i][j]*c[j] for i in range(8) for j in range(8)),8)
# All monomial tables in four variables of total degree at most four.
monomials=0
for exponents in product(range(5), repeat=4):
    if sum(exponents)>4:continue
    vals=[F(prod(((s>>i)&1)**exponents[i] for i in range(4))) for s in range(16)]
    for t in range(16):
        if t.bit_count()>sum(exponents):assert mob(vals,t)==0
    monomials+=1
checks['degree_ceiling_monomials'] = monomials
# Recursion and contextual-dividend identity on a full four-action polynomial table.
vals=[F(3)+F(s*s*s-7*s) for s in range(16)]
coeff=[mob(vals,t) for t in range(16)]
context_checks=0
def contextual(s,t):
    return sum(((-1)**(t.bit_count()-r.bit_count())*vals[s|r] for r in subsets(t)),F(0))
for s in range(16):
    for t in range(16):
        if s&t:continue
        assert contextual(s,t)==sum(coeff[t|r] for r in subsets(s))
        for i in range(4):
            if (s|t)&(1<<i)==0:
                assert contextual(s,t|(1<<i))==contextual(s|(1<<i),t)-contextual(s,t)
        context_checks+=1
checks['contextual_identity_pairs'] = context_checks
# Lie-derivative short-time coefficients for b=x^2+u, V=x^4/4.
v=add(power(z[0],2),z[1]);V=scale(power(z[0],4),F(1,4))
L=lambda p:mul(v,deriv(p,0))
a=deriv(v,0);b=deriv(a,0)
formula2=add(mul(deriv(deriv(V,0),0),power(v,2)),mul(deriv(V,0),mul(a,v)))
formula3=add(mul(ds(V,(0,0,0)),power(v,3)),scale(mul(ds(V,(0,0)),mul(v,mul(a,v))),3),mul(deriv(V,0),add(mul(b,power(v,2)),mul(power(a,2),v))))
assert L(L(V))==formula2 and L(L(L(V)))==formula3
checks['short_time_Lie_orders_2_3'] = 'exact polynomial equality for b=x^2+u, V=x^4/4'
print(json.dumps(checks,indent=2,sort_keys=True))
```

## Appendix B. General higher-chain-rule and integrated interaction proof

This appendix states the precise finite-dimensional result used in §16 without assuming
that a Boolean table has a unique physical interpolation. It is classical set-partition
Faà di Bruno calculus, applied to the declared composite.

**Setting.** Let `U⊆Rⁿ` and `Ω⊆Rᵈ` be open. Let `x:U→Ω` and `V:Ω→R` be `C^k`.
Let `T⊆{1,…,n}` have `k≥1` distinct labels. For nonempty `B⊆T`, define the vector
`x_B(z)=∂_B x(z)` by iterated coordinate differentiation. Let `Π(T)` be the finite set of
partitions of `T` into nonempty disjoint blocks. The `r`th Fréchet derivative `D^rV(y)`
is a symmetric `r`-linear form. All expressions below are evaluated at one common `z∈U`.

**Claim.**

\[
\partial_T(V\circ x)(z)
=\sum_{\pi\in\Pi(T)}
 D^{|\pi|}V(x(z))[x_B(z):B\in\pi].
\]

The block arguments can be listed in any order. There are no multiplicity factors when
every differentiated coordinate label is distinct.

**Proof.** For `k=1`, the ordinary chain rule gives `∂_i(V∘x)=DV(x)[x_i]`, which is
the sole partition. To perform the inductive step, take a fresh label `j` and a partition
`π` of `T`. Differentiating its summand by the chain and multilinear product rules gives

\[
\begin{aligned}
\partial_j\{D^{|\pi|}V(x)[x_B:B\in\pi]\}
={}&D^{|\pi|+1}V(x)[x_j,x_B:B\in\pi]\\
&+\sum_{B\in\pi}D^{|\pi|}V(x)
 [x_{B\cup\{j\}},x_C:C\in\pi\setminus\{B\}].
\end{aligned}
\]

The first term corresponds to adjoining the singleton block `{j}`. Each term in the
second sum corresponds to inserting `j` into exactly one old block. Conversely, a partition
of `T∪{j}` either contains `{j}` as a block, or has a unique larger block containing `j`.
Deleting the singleton, or deleting `j` from that larger block, recovers exactly one
predecessor partition and exactly one differentiation term. These cases are exhaustive
and disjoint, proving every required summand occurs once. At each stage up to order `k`,
the assumed derivatives exist continuously. Their symmetry justifies reordering blocks
and coordinate derivatives. Induction completes the proof. ∎

**Integrated corollary.** Suppose `U` contains the closed face
`Q_T={z:z_i∈[0,1] for i∈T, z_i=0 otherwise}`. Its compactness and the stated smoothness
make every integrand continuous and integrable. Successive one-dimensional FTC identities,
with Fubini for these continuous functions, give

\[
\begin{aligned}
m_E(T)
&=-\sum_{\pi\in\Pi(T)}\int_{[0,1]^T}
 D^{|\pi|}V(x(z_T,0))[x_B(z_T,0):B\in\pi],dz_T.
\end{aligned}
\]

The finite sum and integral commute. The endpoint identity establishes the minus sign and
shows that the sum of the integrals is independent of which smooth extension realizes the
same vertices. The separate partition integrals need not be extension independent.

For an affine response, all blocks larger than one vanish, leaving only the partition into
singletons and the repeated-FTC formula involving `D^kV`. For a quadratic potential, all
terms with more than two blocks vanish, but one- and two-block partitions can still contain
arbitrarily many action labels through higher derivatives of a nonlinear response. This
is the precise derivative reason that quadratic curvature alone gives no general ceiling
on coalition interaction order.

If coordinates repeat, label the derivative occurrences first and sum over their partitions;
collecting equal terms creates the usual integer coefficients. If the requested derivative
order does not exist, the displayed classical chain rule is not asserted. The finite
Möbius theorem still holds for a complete real vertex table. The report supplies no physical
law selecting an interpolation and no invariant causal attribution to its partition terms.

Prior art: [Hardy (2006), Proposition 1 and its proof](https://arxiv.org/pdf/math/0601149);
the argument above states the vector-valued inner-map version explicitly.
