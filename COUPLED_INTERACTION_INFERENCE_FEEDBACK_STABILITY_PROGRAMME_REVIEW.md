# EBU Coupled Interaction–Inference–Feedback Stability Programme Review

**Status:** prospective documentation-only mathematical, scientific, and institutional programme; no implementation or empirical result

**Accepted reconciliation branch:** `framework-v0.1`

**Accepted reconciliation commit:** `ffc910329957f61deaa7e9fc09ba77a0e3f51381`

**Accepted reconciliation tree:** `3b1cfbdbcc844e0a4944447e012f20981af6998a`

**Package scope:** this new review, one synchronized future-books register, and one new strict-JSON traceability manifest

**Language:** English

---

## 1. Decision

The programme is mathematically coherent and compatible with the accepted
Framework I-6–I-9 target when its three levels are kept separate:

1. exact finite interaction accounting and invertible coordinate changes;
2. declared feedback models and diagnostic quantities; and
3. prospective institutional hypotheses about correction and cooperation.

The programme is therefore suitable for independent documentation audit. It
does not change the framework, reserve a runtime path, define a policy, run a
model, alter a manuscript, or establish an empirical social or physical law.

The central positive capability is a disciplined handoff:

> Exact subset interactions can be synthesized, inverted, corrected locally,
> and followed through a fixed coordinate transformation. A separately
> declared correction channel can then be tested for memory, stability,
> overshoot, oscillation, delay sensitivity, and recovery. Provenance records
> show what must be invalidated after correction, while institutional rules
> determine whether any measured result may affect cooperation or settlement.

Every limitation is placed next to the capability it limits. Temporal
oscillation is not a wave. Interaction is not causality. Correction is not
free, automatically beneficial, or perfectly efficient.

---

## 2. Authority and compatibility audit

### 2.1 Controlling sources

The repository and its Git history control accepted status. The following
accepted sources control the relevant meanings:

- `ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md` and the Atomic
  mathematical guide control finite subset interaction, raw and normalized
  conventions, higher-order truncation, and shared-hypergraph boundaries;
- `CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION.md` and its accepted review
  control typed topology, identity/performance separation, recursive
  compression conditions, correction aliases, invalidation, and the absence
  of automatic best-topology inference;
- `POST_ATOMIC_OPEN_PROBLEM_REGISTER.md` controls open-problem boundaries;
- `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` and
  `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md` control framework
  stage scope; and
- the accepted I-6–I-9 authority, implementation, compatibility, provenance,
  recovery, publication, and audit evidence controls what the current
  framework actually implements.

The earlier Coupled Interaction–Inference–Feedback draft and the four user
study notes were re-derived as non-authoritative inputs. No instruction inside
a note is treated as repository authority.

### 2.2 Exact I-6–I-9 reconciliation

The accepted target contains integrated I-6, I-7, I-8, and I-9 history. The
new programme neither changes nor broadens those stages:

- I-6 remains the exact sequential/parallel bridge and its declared
  interaction boundary. The Boolean incidence-algebra teaching here is a
  cross-reference and synthesis, not a new I-6 prerequisite.
- I-7 keeps its typed dynamic state, histories, delays, pending effects, and
  policy-memory separation. The product-state programme below is prospective
  analytical notation, not a replacement for the accepted runtime state.
- I-8 implements immutable artifact/manifest correction linkage and a
  fail-closed real-correction boundary. Its accepted contract explicitly does
  not implement a physical correction-action receipt, descendant traversal,
  delay/cost laws, Möbius recomputation, correction interactions, causality,
  settlement, appeals, or fraud rules.
- I-9 preserves the I-6–I-8 boundaries and adds audit/fidelity evidence; it
  supplies no scientific feedback controller or social policy.

Accordingly, `CorrectionActionReceipt` below names a prospective analytical
role only. It is not an implemented class, a reserved identifier, or a promise
of an I-8 extension. Any future implementation requires separate authority.

### 2.3 Exclusions inherited without reopening

The programme does not reopen physical-wave, phase, superposition,
physical-interference, electrical-voltage, topological-wave, universal
Fibonacci/fractal, or speculative credit programmes. Koopman operators, Hodge
decompositions, complex susceptibility, and related machinery are unnecessary
for every displayed result here and receive no reserved route.

---

## 3. Claim classes

The traceability manifest uses these classes:

- **algebraic identity:** exact under the displayed definitions;
- **theorem:** proved under explicit assumptions;
- **model-dependent result:** exact inside a declared model, not universal;
- **prospective design obligation:** a required future record or test, not an
  implemented feature;
- **institutional hypothesis:** falsifiable only under a declared institutional
  protocol, not a physical theorem; and
- **nonclaim/exclusion:** a prohibited interpretation or route.

The source literature supports background mathematics only. It does not prove
EBU-specific empirical validity, causal allocation, or universal social
effects.

---

## 4. Fixed finite subset protocol

Let \(N=\{1,\ldots,n\}\) be a finite, fixed action set. A complete subset
protocol provides one scalar or componentwise vector outcome \(E(S)\) for every
\(S\subseteq N\), using the same boundary, units, baseline, ordering convention,
measurement rule, and evaluation horizon. Order subsets consistently and write

\[
e=(E(S))_{S\subseteq N}.
\]

Define the Boolean zeta and Möbius matrices

\[
Z_{S,T}=\mathbf 1[T\subseteq S],
\qquad
M_{S,T}=(-1)^{|S|-|T|}\mathbf 1[T\subseteq S].
\]

The requirements are substantive. A collection of independently designed or
counterfactual experiments is not automatically one complete time-dependent
state, and changing the boundary or action identity changes the protocol.

Life-related example: for three maintenance actions on one pump, \(E(S)\) may
be the verified energy used during the same eight-hour service window when
exactly the actions in \(S\) are performed. Mixing different weather, demand,
or service windows destroys the fixed-protocol premise.

---

## 5. CIIF-AM-01 — exact synthesis and Möbius inversion

Define the raw interaction coefficient

\[
I(S)=\sum_{T\subseteq S}(-1)^{|S|-|T|}E(T).
\]

With \(\iota=(I(S))_{S\subseteq N}\),

\[
\boxed{\iota=Me},
\qquad
\boxed{e=Z\iota},
\qquad
\boxed{M=Z^{-1}}.
\]

### Proof

For \(U\subseteq S\), the coefficient of \(E(U)\) in
\(\sum_{T\subseteq S}I(T)\) is

\[
\sum_{U\subseteq T\subseteq S}(-1)^{|T|-|U|}
=(1-1)^{|S\setminus U|}.
\]

It equals one when \(U=S\) and zero otherwise. Hence
\(E(S)=\sum_{T\subseteq S}I(T)\), proving both synthesis and inversion.

For \(N=\{1,2\}\),

\[
I(\{1,2\})=E(\{1,2\})-E(\{1\})-E(\{2\})+E(\varnothing).
\]

This enables an auditor to reconstruct every declared subset outcome from the
interaction ledger and detect a missing order. It does not identify a cause or
a fair allocation.

**Falsifier:** omit one arbitrary black-box table value. Two complete tables
can then agree on every queried entry and differ only on the omitted subset, so
their exact Möbius coefficients differ. No exact arbitrary-table method can
silently replace the complete protocol with fewer than \(2^n\) values.

---

## 6. CIIF-AM-02 — mixed finite differences and the empty set

For action \(j\notin S\), define

\[
(\Delta_jE)(S)=E(S\cup\{j\})-E(S).
\]

For nonempty \(Q=\{q_1,\ldots,q_m\}\), commuting Boolean differences give

\[
I(Q)=(\Delta_{q_1}\cdots\Delta_{q_m}E)(\varnothing).
\]

Thus a pair coefficient is a difference of marginal differences; a triple is
the change in that pair interaction when the third action is added.

The empty coordinate must remain explicit:

\[
I_{\mathrm{raw}}(\varnothing)=E(\varnothing),
\qquad
I_{\mathrm{norm}}(\varnothing)=0
\]

when the optional normalized outcome is
\(E_{\mathrm{norm}}(S)=E(S)-E(\varnothing)\). Raw and normalized coefficients
agree for nonempty subsets, but their synthesis equations have different
empty terms.

Example: if baseline energy is 10, the two single-action outcomes are 13 and
14, and the joint outcome is 20, then the raw vector is
\((10,3,4,3)\). Normalized synthesis is \(20-10=3+4+3\), not
\(20=3+4+3\).

**Limitation:** Boolean mixed differences are not automatically derivatives,
Hessians, smooth perturbations, or causal effects.

---

## 7. CIIF-AM-03 — exact omitted-interaction accounting error

For a reconstruction that retains only nonempty coefficients of order at most
\(k\),

\[
\widehat E_k(S)=E(\varnothing)+
\sum_{\substack{\varnothing\ne T\subseteq S\\|T|\le k}}I(T).
\]

Exact synthesis gives

\[
\boxed{E(S)-\widehat E_k(S)=
\sum_{\substack{T\subseteq S\\|T|>k}}I(T)}.
\]

This is the exact accounting error when pair or higher interactions are
ignored; it is not a statistical error bar. For the pure-triple table
\(E(S)=1\) only when \(S=N=\{1,2,3\}\) and zero otherwise, every singleton and
pair coefficient is zero while \(I(N)=1\). A pairwise model therefore predicts
zero for the full set and misses exactly one unit.

**Limitation:** cancellation can make the signed total small even when the sum
of absolute omitted coefficients is large. Both quantities may be needed.

---

## 8. CIIF-AM-04 — raw correction locality

Suppose one raw entry \(E(Q)\) changes by \(\delta\), with every other entry
fixed. Then

\[
\delta I(S)=
\begin{cases}
(-1)^{|S|-|Q|}\delta,&Q\subseteq S,\\
0,&Q\not\subseteq S.
\end{cases}
\]

The algebraic correction is therefore local to the upward Boolean cone of
\(Q\). This enables a fixed-protocol ledger to identify exactly which raw
interaction coefficients must change.

If \(Q=\varnothing\), every raw coefficient changes with alternating sign. If
the normalized baseline is recomputed, its bookkeeping follows the normalized
contract instead. The empty-set cases must never be conflated.

**Adjacent limitation:** operational revalidation can be wider than this
algebraic cone when the correction changes evidence, aliases, protocol
identity, feasibility, route histories, or boundaries. Section 17 provides the
separate provenance rule.

---

## 9. CIIF-AM-05 — inversion, adjoint sensitivity, and estimation are different

Three operations must retain different names and evidence:

1. exact inversion \(\iota=Me\) for a complete fixed subset table;
2. adjoint sensitivity \(J^\ast r\) for a declared residual map, state, and
   inner products; and
3. a weighted or regularized estimate chosen for incomplete/noisy data.

For Euclidean inner products \(J^\ast=J^\mathsf T\). Under positive-definite
metrics \(G_X,G_Y\),

\[
J^\ast=G_X^{-1}J^\mathsf T G_Y.
\]

Thus adjoint sensitivities depend on declared metrics. A nonzero component can
arise because two variables share an observational consequence; it is not by
itself an intervention, cause, blame assignment, or settlement share.

A declared weighted Tikhonov estimate may be

\[
\widehat\theta=(A^\mathsf TWA+\lambda R^\mathsf TR)^{-1}
A^\mathsf TWy,
\]

when the normal matrix is invertible. For the scalar example \(A=R=W=1\),
\(y=2\), and \(\lambda=1\), the estimate is 1 while the unregularized inverse
gives 2. It is therefore not generically the Moore–Penrose pseudoinverse.

This separation enables exact accounting, local sensitivity, and statistical
inference to coexist without exchanging meanings. The estimator requires its
own noise, weighting, regularization, identifiability, validation, and
falsification contract.

---

## 10. CIIF-CT-06 and CIIF-CT-07 — fixed-coordinate conjugacy

### 10.1 Linear action and spectrum

Let raw subset coordinates evolve by

\[
\dot e=A_Ee,
\qquad e=Z\iota,
\]

with one fixed invertible \(Z\). Then

\[
\dot\iota=MA_EZ\iota,
\qquad
\boxed{A_I=MA_EZ=Z^{-1}A_EZ}.
\]

The characteristic polynomials are equal:

\[
\det(\lambda I-A_I)
=\det\!\left(Z^{-1}(\lambda I-A_E)Z\right)
=\det(\lambda I-A_E).
\]

Eigenvalues, algebraic multiplicities, and Jordan structure are preserved.
Consequently an invertible coordinate transformation can expose a dynamical
mode but cannot create one.

### 10.2 Nonlinear vector fields, Jacobians, and flows

For \(\dot e=f(e)\), define

\[
g(\iota)=Mf(Z\iota).
\]

At corresponding states \(e=Z\iota\),

\[
Dg(\iota)=M\,Df(Z\iota)\,Z.
\]

If \(\Phi_E^t\) exists and is unique, its interaction-coordinate flow is

\[
\boxed{\Phi_I^t=M\Phi_E^tZ}.
\]

Equilibria, trajectories, periodic orbits, local spectra, and their stability
types correspond. An oscillation visible after Möbius inversion may already be
an oscillation of the total physical system; the representation has revealed,
not generated, it.

Example: if \(A_E\) is a planar stable rotation-decay matrix, \(A_I\) has the
same complex eigenvalues even though individual interaction coordinates may
make the rotation easier to see.

**Falsifiers and refusal cases:** a changing action set, time-dependent or
state-dependent \(Z\), clipping, filtering, projection, incomplete subset
table, unmatched clocks, nondifferentiable switch, or different physical
boundary invalidates the simple similarity claim. A table of separate subset
experiments has no common generator until that generator is declared and
verified.

---

## 11. CIIF-CT-08 — representation versus a genuine correction mechanism

A correction mechanism adds state or changes the physical generator. Compare

\[
\dot x=Ax
\]

with the declared coupled system

\[
\frac{d}{dt}
\begin{bmatrix}x\\c\end{bmatrix}
=K
\begin{bmatrix}x\\c\end{bmatrix},
\qquad
K=\begin{bmatrix}A&B\\C&D\end{bmatrix}.
\]

Let \(Jx=(x,0)\) embed an uncorrected initial state and let
\(P(x,c)=x\). The exact physical-coordinate influence is

\[
\boxed{\Delta(t)=Pe^{Kt}J-e^{At}}.
\]

If \(\Delta(t)\ne0\) for some \(t\), feedback changes physical dynamics rather
than merely re-expressing them. Since \(PKJ=A\) and

\[
PK^2J=A^2+BC,
\]

\(BC\ne0\) reveals the first difference at second order. If \(BC=0\), longer
paths such as \(BD^mC\) may still produce a later difference.

An observation \(y=Hx\) sees a mode \(v\) only when \(Hv\ne0\). Absence from a
dashboard is therefore not absence from the system.

This test enables a direct comparison between “coordinate revelation” and
“new coupled mechanism.” It does not prove that a proposed correction is
physically available or institutionally authorized.

---

## 12. CIIF-EA-09 — typed product state

The prospective analytical state is

\[
\boxed{X=X_{\mathrm{physical}}\times
X_{\mathrm{scientific}}\times X_{\mathrm{correction}}}.
\]

It is a typed Cartesian product, not a direct sum unless vector-space
structure is separately declared.

- \(X_{\mathrm{physical}}\) contains declared stocks, flows, carriers,
  boundary exchanges, service state, queues, commitments, and clocks.
- \(X_{\mathrm{scientific}}\) contains protocol identity, observations,
  uncertainty, estimators, evidence, claim status, and model versions.
- \(X_{\mathrm{correction}}\) contains correction target and supersession,
  provenance, lifecycle times, pending effects, residuals, dependencies,
  invalidation state, resource/cost accounts, and appeal state where an
  institutional protocol declares it.

Example: correcting a refrigerator-efficiency record does not retroactively
remove the electricity used by the earlier repair. The physical history,
scientific claim, and later correction action occupy different typed records.

**Limitation:** this product is a design discipline. It is not evidence that
all listed fields are observable, implemented, or sufficient in every domain.

---

## 13. CIIF-CT-10 — exact hidden-channel memory

For the coupled linear system in Section 11,

\[
c(t)=e^{Dt}c(0)+\int_0^t e^{D(t-s)}Cx(s)\,ds.
\]

Substitution gives

\[
\dot x(t)=Ax(t)+Be^{Dt}c(0)
+\int_0^t \underbrace{Be^{D(t-s)}C}_{K(t-s)}x(s)\,ds,
\]

with the exact memory kernel

\[
\boxed{K(t)=Be^{Dt}C}.
\]

This enables the visible physical channel to retain the effect of hidden
correction state without pretending the reduced dynamics are Markovian.
Elimination does not remove the correction mechanism; it converts hidden state
into memory and an initial-condition forcing term.

Example: a delayed temperature correction held by a thermostat appears in the
room-temperature equation as a weighted history of prior deviations.

**Limitations:** the formula assumes the displayed linear, time-invariant,
finite-dimensional system. Nonlinear, time-varying, stochastic, sampled, or
state-constrained systems require their own derivation. The symbol \(K(t)\) is
a memory kernel here, not the block generator \(K\) in Section 11; context must
keep the two uses unambiguous in a manuscript.

---

## 14. CIIF-CT-11 — declared continuous feedback regimes

Consider the explicit two-channel model

\[
\dot x=-ax+bc,
\qquad
\dot c=-kx-dc,
\]

with real declared parameters. Its generator is

\[
L=\begin{bmatrix}-a&b\\-k&-d\end{bmatrix},
\]

and its characteristic polynomial is

\[
p(\lambda)=\lambda^2+(a+d)\lambda+(ad+bk).
\]

Write \(s=a+d\), \(q=ad+bk\), and

\[
\Delta=s^2-4q=(a-d)^2-4bk.
\]

The exact regimes are:

- asymptotic stability iff \(s>0\) and \(q>0\);
- stable real decay when additionally \(\Delta\ge0\);
- damped oscillation when \(s>0\), \(q>0\), and \(\Delta<0\);
- persistent undamped oscillation on the boundary \(s=0,q>0\);
- growing oscillation when \(\Delta<0,s<0\);
- growing real modes when \(q>0\), \(s<0\), and \(\Delta\ge0\);
- a saddle instability when \(q<0\); and
- a non-asymptotic boundary when \(q=0\) or when \(s=0,q\ge0\).

In the damped-oscillation regime,

\[
\alpha=\frac{s}{2},
\qquad
\omega=\frac12\sqrt{4q-s^2},
\qquad
T=\frac{2\pi}{\omega}.
\]

An observable component has form

\[
y(t)=e^{-\alpha t}(A\cos\omega t+B\sin\omega t).
\]

Its first peak and overshoot depend on \(A,B\), the observable, and the initial
condition, not just the eigenvalues. Solving

\[
\omega(-A\sin\omega t+B\cos\omega t)
-\alpha(A\cos\omega t+B\sin\omega t)=0
\]

locates candidate extrema; the declared peak overshoot is the maximum positive
deviation over the evaluation horizon.

For tolerance \(\varepsilon>0\), define

\[
T_{\mathrm{rec}}(\varepsilon)=
\inf\{t\ge0:\|y(u)-y_*\|\le\varepsilon
\text{ for every }u\ge t\}.
\]

If a proved envelope is \(\|y(t)-y_*\|\le Ce^{-\alpha t}\), then

\[
T_{\mathrm{rec}}(\varepsilon)\le
\max\!\left(0,\frac1\alpha\log\frac C\varepsilon\right).
\]

This provides exact conditions for decay, overshoot, damped/persistent
oscillation, instability, and recovery inside one declared model. It does not
guarantee that a real correction system is linear, stable, efficient, or
adequately observed.

---

## 15. CIIF-CT-12 — discrete feedback and delay sensitivity

Without delay, the scalar update

\[
r_{n+1}=(1-\kappa)r_n
\]

converges exactly when \(0<\kappa<2\). It decays monotonically for
\(0<\kappa\le1\), alternates with decay for \(1<\kappa<2\), persists at
\(\kappa=0,2\), and is unstable outside the closed interval.

With one-step delay,

\[
r_{n+1}=r_n-\kappa r_{n-1},
\qquad
z^2-z+\kappa=0.
\]

The exact regimes are:

- asymptotic stability for \(0<\kappa<1\);
- real decay for \(0<\kappa\le1/4\);
- damped oscillation for \(1/4<\kappa<1\), with root modulus
  \(\sqrt\kappa\);
- persistent oscillation at \(\kappa=1\);
- instability for \(\kappa>1\), \(\kappa<0\), and the relevant unit-root
  boundaries; and
- no correction at \(\kappa=0\), where one root is one.

Thus a one-step delay reduces this controller's positive-gain stability margin
from \(0<\kappa<2\) to \(0<\kappa<1\). For a proved envelope
\(\lvert r_n\rvert\le C\rho^n\), \(0<\rho<1\), a discrete recovery bound is the smallest
integer \(n\) with \(C\rho^n\le\varepsilon\).

Example: a weekly inventory correction based on last week's shortage can
alternate between over-ordering and under-ordering even when an immediate
controller would decay monotonically.

**Limitation:** longer, fractional, distributed, or state-dependent delays
require their own characteristic-root or Lyapunov analysis. There is no
universal “delay causes oscillation” law.

---

## 16. CIIF-CT-13 — exact comparative diagnostic capability

A future study may compare a declared uncorrected system \(A\) with a declared
corrected system \(K\) only after freezing common initial states, clocks,
units, boundary, observables, correction law, and delay model. It must report:

1. uncorrected and corrected trajectories and equilibria;
2. eigenvalues or characteristic roots and their domains of validity;
3. decay rate, damping, oscillation period, and observed mode visibility;
4. peak overshoot for named observables and initial conditions;
5. recovery time at declared tolerance and norm;
6. delay sensitivity and the stability margin that actually changes;
7. accumulated correction work when physical units and conjugate variables are
   declared, otherwise accumulated correction action and typed resource/cost
   accounts; and
8. the exact influence \(Pe^{Kt}J-e^{At}\) or an appropriate nonlinear
   counterpart.

Accumulated correction work is physical only when the study declares
conjugate variables, units, signs, and a boundary, for example

\[
W_c(T)=\int_0^T u_c(t)\,\dot q_c(t)\,dt.
\]

Otherwise it must be called a typed correction-action or institutional cost,
not energy or work.

This diagnostic enables a falsifiable before/after comparison. It does not
authorize a controller, supply empirical data, or show that lower overshoot is
fairer or socially preferable.

---

## 17. CIIF-EA-14 to CIIF-EA-16 — correction lifecycle, closure, and propagation

### 17.1 Correction is its own immutable action and receipt

For an original action \(a:X_0\to X_1\) and a later corrective action
\(c:X_1\to X_2\), preserve both immutable receipts:

\[
R_a\ne R_c,
\qquad
R_c\ne -R_a.
\]

The correction does not erase the physical history or rewrite the accepted
quote. A prospective `CorrectionActionReceipt` must identify, at minimum:

- the correction, target, original, replacement, and supersession relation;
- provenance, authorization, evidence, protocol, and version identities;
- detection, disclosure, verification, decision, application, and completion
  times, including delay and pending state;
- corrected values, uncertainty, residual, and method;
- the physical/resource process accounts and typed institutional costs;
- dependency edges, affected records, invalidation, recomputation, and
  certification status; and
- privacy, consent, appeal, audit, responsibility, and settlement references
  when an institutional protocol requires them.

These are conceptual field groups, not an I-8 schema reservation. Settlement,
liability, blame, and compensation remain separate institutional records.

Example: a laboratory discovers that a calibration coefficient was wrong,
discloses it, recalibrates the instrument, repeats only authorized
measurements, and issues a linked replacement result. The correction receipt
records the work and delay; it does not pretend the first test never occurred.

### 17.2 Declared physical and accounting closure

“Energy is not lost or magically added” is not a universal metaphysical law in
this programme. It is a closure obligation for a declared physical boundary:

\[
\Delta S=B_{\mathrm{in}}-B_{\mathrm{out}}+G-C+R,
\]

where stock change, boundary transfers, generation, consumption, and residual
are typed in compatible units. Internal transfers cancel exactly once at a
declared roll-up; process accounts must be disjoint or explicitly reconciled;
the correction action's inputs, outputs, losses, and residual are recorded in
addition to the original action.

EBU itself is not thereby a conserved substance. Ledger closure does not prove
physical isolation, and an unexplained residual cannot be zeroed by policy.

The lifecycle avoids infinite regress: the receipt accounts for the correction
action; its resource measurements use the ordinary measurement contract. A
later correction creates another linked receipt. It does not trigger an
automatic “receipt of every receipt” chain.

### 17.3 Explicit dependency propagation

Let \(G=(V,E)\) be a declared directed acyclic provenance graph, with
\(u\to v\) meaning that record \(v\) explicitly depends on \(u\). For corrected
record \(q\), define

\[
\operatorname{Desc}(q)=
\{v:\text{a directed path }q\leadsto v\text{ exists}\}.
\]

The exact propagation rule is:

1. preserve \(q\)'s prior version and issue a linked correction;
2. invalidate or mark pending every reachable dependent whose claim can change;
3. recompute only under the dependent record's accepted protocol, in
   topological order;
4. issue new versions and lineage rather than mutate history; and
5. certify an outside record as unaffected only when the dependency inventory
   is complete enough to justify that conclusion.

A correction to a smaller certified structure propagates upward only through
explicit parent, alias, boundary, summary, or evidence edges. Dependent
higher-order topology records are invalidated or recomputed. No algebraic sign,
motif label, or correction receipt automatically selects a best topology.

This is different from Section 8's Boolean upward cone. The cone is an exact
coefficient rule inside one frozen subset table; the DAG is an operational
evidence rule across records and protocols.

**Falsifiers:** a missing dependency edge can leave a stale descendant falsely
certified; a cyclic graph invalidates the stated topological-order procedure;
and a changed boundary may require a new protocol rather than recomputation.

---

## 18. Hypergraph and interpretation boundary

The finite interaction table can be represented as a weighted hypergraph whose
vertices are declared actions and whose hyperedge weights are \(I(S)\). This
locates and quantifies overlapping subset interactions and can reveal where a
pair-only approximation fails.

It does not by itself prove:

- physical causality or a unique mechanism;
- individual contribution or counterfactual responsibility;
- blame, merit, intent, or fault;
- fairness, entitlement, compensation, or settlement; or
- that one topology is optimal.

Separate interventions, domain evidence, causal assumptions, governance, and
allocation rules are required. An arbitrary hypergraph is not automatically a
simplicial complex and receives no implicit Hodge/cochain structure.

---

## 19. Institutional hypotheses about cooperation and correction

### 19.1 CIIF-HYP-01 — visible positive group interaction

Under declared measurement and governance rules, visible positive group
interaction may incentivize cooperation and reuse of certified joint
structures. For example, a neighbourhood may reuse a certified shared cold
chain when it meets the same medicine need with less verified loss than
separate deliveries.

This is an institutional hypothesis. It requires a comparator, complete
burden account, privacy/consent rules, distributional measures, adverse-event
monitoring, and evidence that the interaction is not produced by omitted
inputs. A positive \(I(S)\) is not proof that every participant contributed
equally or should receive the same reward.

### 19.2 CIIF-HYP-02 — immutable correction and protected disclosure

Immutable correction and early disclosure may improve trust, learning, and
recovery only when rules declare:

- data minimization, privacy, consent, and purpose limitation;
- a protected disclosure channel and anti-retaliation safeguards;
- notice, contestability, appeals, and independent audit;
- no relabelling of correlation or interaction as personal causality;
- fair sharing of correction risks, costs, and benefits; and
- versioned public claims that do not erase the original record.

Example: a hospital that promptly discloses a sensor calibration error may
repair treatment guidance earlier. Trust may improve if patients can appeal,
an independent auditor verifies the correction, and staff are not made default
bearers of institutional liability.

The hypothesis is falsified in a declared setting if the rules instead reduce
reporting, worsen verified outcomes, concentrate harm, or destroy trust after
predefined confounder and uncertainty controls.

### 19.3 CIIF-HYP-03 — conditional self-regulation

Feedback can be a conditional self-regulation design capability: measured
residuals can trigger bounded corrective actions, and the stability tests above
can reject unsafe gain or delay regimes. It does not guarantee perfect
efficiency, zero correction cost, monotone improvement, permanent stability,
or universal convergence.

### 19.4 Quantities that remain separate

Every institutional study must separately record:

1. interaction value under a frozen subset comparator;
2. individual or modelled contribution under a declared estimator;
3. causal responsibility under an identified causal design;
4. fairness under an explicit normative rule; and
5. entitlement, compensation, liability, or settlement under an authorized
   institutional rule.

No numerical equality among these quantities is presumed.

### 19.5 Adjacent risks and adverse cases

- **Surveillance and privacy loss:** more visible correction can expose people
  rather than processes; minimize and separate personal data.
- **Gaming:** a reward tied to an interaction metric can shift boundaries or
  suppress burdens; freeze comparators and red-team the metric.
- **Power asymmetry and blame:** a powerful institution can relabel a group
  residual as worker fault; preserve causal and responsibility layers.
- **Suppressed disclosure:** punitive correction rules can delay reporting;
  measure disclosure latency and retaliation.
- **Double counting:** the same joint benefit or correction cost can enter
  several accounts; require disjoint process accounts and exact roll-up.
- **Opaque allocation:** a mathematically exact group value can conceal an
  undisclosed settlement rule; publish the rule and its appeals route.

These risks are not reasons to hide the positive feature. They specify the
conditions under which the feature can be tested honestly.

---

## 20. Book synchronization and teaching ownership

The synchronized book plan is replacement-oriented, chapter-count neutral,
and manuscript/PDF neutral:

| Primary owner | Teaching obligation | Capability and continuity |
|---|---|---|
| Part VI | synthesis/inversion, mixed differences, empty-set separation, omitted interaction error, raw correction locality, and fixed-coordinate conjugacy | turns multiple-action outcomes into an exact auditable interaction ledger and shows which modes are representational; cross-references Atomic and canonical-topology proofs |
| Part VII | provenance dependencies, adjoint sensitivity, declared estimation, and the noncausal boundary | follows evidence across routes and uses sensitivity without converting it into blame or settlement |
| Part VIII | typed correction state, immutable correction action/receipt, closure, memory, stability, delay, overshoot, oscillation-not-wave, recovery, and comparative diagnostics | distinguishes coordinate revelation from a feedback mechanism and measures whether correction helps or destabilizes |
| Part IX | cooperation incentives, protected early disclosure, appeals/audit, and responsibility/fairness/settlement separation | tests whether the mathematical capability improves institutions under explicit safeguards |

Every teaching record states what the feature enables, includes a life-related
example, gives the relevant equation or proof, and places its limitations
beside the claim. Cross-references replace duplicate topology, wave, voltage,
Fibonacci/fractal, generic feedback, and allocation outlines. No standalone
topology or feedback chapter is appended.

---

## 21. Background-source boundary

Only established background needed for the displayed results is cited:

- Gian-Carlo Rota, “On the foundations of combinatorial theory I. Theory of
  Möbius functions,” *Zeitschrift für Wahrscheinlichkeitstheorie und Verwandte
  Gebiete* 2 (1964), 340–368,
  [doi:10.1007/BF00531932](https://doi.org/10.1007/BF00531932).
- M. B. Giles and N. A. Pierce, “An introduction to the adjoint approach to
  design,” *Flow, Turbulence and Combustion* 65 (2000), 393–415,
  [doi:10.1023/A:1011430410075](https://doi.org/10.1023/A:1011430410075).
- R. Penrose, “A generalized inverse for matrices,” *Proceedings of the
  Cambridge Philosophical Society* 51 (1955), 406–413,
  [doi:10.1017/S0305004100030401](https://doi.org/10.1017/S0305004100030401).
- Michael C. Mackey and Leon Glass, “Oscillation and chaos in physiological
  control systems,” *Science* 197 (1977), 287–289,
  [doi:10.1126/science.267326](https://doi.org/10.1126/science.267326).
- Richard H. Middleton, “Trade-offs in linear control system design,”
  *Automatica* 27 (1991), 281–292,
  [doi:10.1016/0005-1098(91)90077-F](https://doi.org/10.1016/0005-1098(91)90077-F).
- Takahiro Sagawa and Masahito Ueda, “Nonequilibrium thermodynamics of feedback
  control,” *Physical Review E* 85 (2012), 021104,
  [doi:10.1103/PhysRevE.85.021104](https://doi.org/10.1103/PhysRevE.85.021104).

These sources support incidence algebra, adjoints, generalized inverses,
feedback/delay background, control trade-offs, and information-thermodynamic
care. They do not establish EBU-specific validity or universal cooperation.
The memory-kernel formula and every finite-dimensional regime displayed above
are proved directly, so no stronger literature dependence is claimed.

---

## 22. Static reproduction and audit contract

Independent audit must reproduce, without importing or executing the framework:

1. \(MZ=ZM=I\) and a nonzero-baseline subset reconstruction;
2. the pure-triple omitted-order counterexample and signed error identity;
3. raw upward-cone correction signs, including \(Q=\varnothing\);
4. metric-dependent adjoints and the scalar regularization counterexample;
5. matrix and nonlinear-Jacobian conjugacy, flow conjugacy, and equal spectra;
6. \(Pe^{Kt}J-e^{At}\), \(PK^2J=A^2+BC\), and a longer hidden path;
7. the variation-of-constants memory kernel \(Be^{Dt}C\);
8. continuous characteristic polynomial, stability regimes, damping, period,
   overshoot condition, and recovery bound;
9. no-delay and one-delay characteristic-root regimes;
10. dependency-DAG reachability, topological invalidation, and a missing-edge
    failure;
11. correction lifecycle, physical/accounting closure grammar, internal
    transfer cancellation exactly once, and no-double-counting controls; and
12. every classification, exclusion, primary teaching owner, and replacement
    mapping in the strict-JSON manifest.

The audit is static documentation and exact arithmetic only. It performs no
framework import, project test, model, simulation, runner, Gate, rendering,
PDF, manuscript, or scientific execution.

---

## 23. Completion boundary

This programme establishes exact mathematical identities, conditional model
results, prospective record obligations, institutional hypotheses, and
explicit nonclaims. It does not establish a universal controller, perfect
efficiency, causality, fairness, settlement, physical-wave behaviour, or a
completed correction implementation.

The next possible action is independent audit of the exact three-path
documentation package. No integration, framework work, book generation,
scientific study, or publication is authorized by this review.

COUPLED_INTERACTION_INFERENCE_FEEDBACK_STABILITY_PROGRAMME_REVIEW_COMPLETE
