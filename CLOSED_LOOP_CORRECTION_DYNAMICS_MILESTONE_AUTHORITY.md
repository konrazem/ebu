# EBU Closed-Loop Correction Dynamics Milestone Authority

**Status:** prospective authority and preregistration design; unimplemented; unexecuted; unaudited

**Version:** 1.0.0

**Accepted branch:** `framework-v0.1`

**Accepted commit:** `79883ad85d6c61bd32c1493cd7cc14a7062cb256`

**Accepted tree:** `adc7a83c1a259f3fa2be39b821baf625fd2f1582`

**Scope:** freeze the next EBU milestone that separates interaction-coordinate revelation from a genuine correction mechanism, and define the exact protocol that later implementation and scientific execution must follow.

This package does not change Framework I-6 through I-9, implement a feedback
controller, create a physical `CorrectionActionReceipt`, run a model, select a
policy, modify a manuscript, render a book, or establish an empirical law. The
mechanical, validation, source-lock, and traceability contracts are companions
to this authority. A semantic disagreement among them is an integrity failure.

## 1. Decision

The milestone is adopted.

Its central capability is:

> EBU can distinguish an interaction pattern that becomes visible under an
> invertible Möbius coordinate transformation from behaviour genuinely changed
> by an added correction channel. Under a declared model, it can then test
> memory, stability, overshoot, oscillation, delay sensitivity, recovery, and
> observability while keeping correction actions and receipts distinct from
> the history they correct.

This is an important project milestone because it connects exact interaction
accounting to dynamic correction theory without confusing representation with
mechanism or measurement with governance.

## 2. Controlling inputs and exact adoption of the two study answers

The repository controls accepted meaning. The two user study answers are
contextual inputs, not authority, but their valid content is adopted through
the already accepted Coupled Interaction–Inference–Feedback review.

| Study result | Accepted project home | Milestone disposition |
|---|---|---|
| Fixed complete Möbius coordinates cannot manufacture a dynamical mode | CIIF-CT-06 and CIIF-CT-07 | Required theorem control |
| `Delta(t) = P exp(Kt) J - exp(At)` distinguishes representation from changed physical trajectories | CIIF-CT-08 | Required mechanism diagnostic |
| `PK^2J - A^2 = BC`, with longer paths `B D^m C` when needed | CIIF-CT-08 | Required local influence control |
| Eliminating correction state produces `B exp(Dt) C` | CIIF-CT-10 | Required memory control |
| Continuous two-channel stability and oscillation regimes | CIIF-CT-11 | Required declared-model control |
| No-delay and one-step-delay stability margins | CIIF-CT-12 | Required delay control |
| Mode visibility depends on the declared observation map | CIIF-CT-08 and CIIF-CT-13 | Required observability control |
| Original and correction actions retain separate immutable receipts | CIIF-EA-14 | Prospective record obligation |
| Correction inputs, outputs, losses, residual, delay, and cost must close at a declared boundary | CIIF-EA-15 | Prospective closure obligation |
| Corrections propagate through explicit dependency edges | CIIF-EA-16 | Prospective invalidation obligation |
| Feedback may support conditional self-regulation but cannot guarantee perfect efficiency | CIIF-HYP-03 | Institutional hypothesis and nonclaim |

The exact source identities are frozen in
`closed_loop_correction_dynamics_milestone_source_manifest.json`.

## 3. Authority layers

The milestone has three authorization layers. Passing one layer does not
authorize the next.

1. **CLCD-A — authority and preregistration:** the present package. It freezes
   definitions, models, controls, validation vectors, book ownership, and
   nonclaims. It is static only.
2. **CLCD-B — inert implementation:** a later separately authorized package
   may add declarations, exact/pure diagnostic calculations, frozen fixtures,
   and tests. It may not start a scientific controller or advance model state.
3. **CLCD-C — scientific execution:** a later separately authorized and
   preregistered study may run the declared synthetic and domain models. It
   must preserve exact inputs, outputs, uncertainties, failures, and evidence.

Production control, institutional settlement, and public deployment remain
outside all three layers unless separately authorized.

## 4. Required declaration grammar

A later CLCD-B implementation must represent, without hidden defaults:

- protocol identity and version;
- model class: continuous linear, continuous nonlinear, discrete immediate,
  discrete delayed, or explicitly named extension;
- typed physical, scientific, and correction state;
- units, signs, boundary, clocks, horizon, and admissible initial states;
- raw subset basis, fixed zeta matrix `Z`, inverse Möbius matrix `M`, and the
  conditions under which the coordinate theorem is applicable;
- uncorrected generator or update;
- corrected block generator or update, including `A`, `B`, `C`, and `D` where
  the linear block model is used;
- embedding `J`, projection `P`, observation map `H`, and named observables;
- correction law, gain, delay, saturation, constraints, and stopping rule;
- numerical method, precision, tolerance, convergence check, and analytic
  controls;
- correction-action lifecycle, immutable receipt references, resource/cost
  accounts, residual, and dependency graph;
- expected outputs, falsifiers, uncertainty treatment, and claim status.

Missing applicability conditions fail closed. A validator must not invent a
state, unit, matrix, boundary, observation map, causal interpretation, or
settlement rule.

## 5. Test A — Möbius validity

For the fixed complete subset basis, require

\[
MZ=ZM=I.
\]

The action set, subset order, clocks, boundary, and normalization convention
must remain fixed. A changing basis, clipping, filtering, estimation,
projection, or incomplete subset table is not a coordinate-only comparison.

## 6. Test B — coordinate-only equivalence

For a linear model,

\[
\boxed{A_I=MA_EZ=Z^{-1}A_EZ}.
\]

For a nonlinear vector field,

\[
g(\iota)=Mf(Z\iota),
\qquad
Dg(\iota)=M Df(Z\iota)Z.
\]

When the flow exists uniquely,

\[
\boxed{\Phi_I^t=M\Phi_E^tZ}.
\]

Therefore corresponding equilibria, trajectories, periodic orbits, local
spectra, and stability types are preserved. The coordinate change can reveal
a mode; it cannot create it.

## 7. Test C — spectral preservation

For the linear coordinate-only comparison, require

\[
\det(\lambda I-A_I)=\det(\lambda I-A_E).
\]

The comparison must also preserve algebraic multiplicity and Jordan structure.
An oscillation visible only after plotting an interaction coordinate is not a
new physical mode when these identities hold.

## 8. Test D — genuine feedback influence

For

\[
K=\begin{bmatrix}A&B\\C&D\end{bmatrix},
\qquad
Jx=(x,0),
\qquad
P(x,c)=x,
\]

define

\[
\boxed{\Delta(t)=Pe^{Kt}J-e^{At}}.
\]

`Delta(t)` identically zero means the declared correction channel changes no
admissible projected physical trajectory under the declared initial
conditions. A nonzero operator for some time proves that at least one
admissible physical trajectory changes.

The exact derivative sequence is

\[
Pe^{Kt}J-e^{At}
=\sum_{m\ge0}\frac{t^m}{m!}(PK^mJ-A^m).
\]

Since `PKJ=A` and

\[
\boxed{PK^2J-A^2=BC},
\]

`BC != 0` gives a second-order influence witness. If `BC = 0`, later paths
such as `BDC`, `BD^2C`, and the complete sequence remain mandatory.

## 9. Test E — hidden-state memory

Eliminating the correction state in the declared finite-dimensional linear
time-invariant model gives

\[
c(t)=e^{Dt}c(0)+\int_0^t e^{D(t-s)}Cx(s)\,ds
\]

and

\[
\dot x(t)=Ax(t)+Be^{Dt}c(0)
+\int_0^t Be^{D(t-s)}Cx(s)\,ds.
\]

The exact memory kernel is

\[
\boxed{\mathcal K(t)=Be^{Dt}C}.
\]

The initial-condition forcing term must not be dropped. Nonlinear,
time-varying, stochastic, sampled, constrained, and distributed-delay models
require their own derivation.

## 10. Test F — stability, oscillation, delay, and recovery

For the declared continuous model

\[
\dot x=-ax+bc,
\qquad
\dot c=-kx-dc,
\]

the characteristic polynomial is

\[
p(\lambda)=\lambda^2+(a+d)\lambda+(ad+bk).
\]

With `s=a+d`, `q=ad+bk`, and discriminant

\[
\mathfrak D=s^2-4q=(a-d)^2-4bk,
\]

the protocol must distinguish stable real decay, damped oscillation,
persistent boundary oscillation, growing oscillation, growing real modes,
saddle instability, and non-asymptotic boundaries exactly as frozen in
CIIF-CT-11. Damping, period, overshoot, and recovery are reported only for
named observables, initial conditions, norms, tolerances, and horizons.

For the immediate update

\[
r_{n+1}=(1-\kappa)r_n
\]

and one-step delayed update

\[
r_{n+1}=r_n-\kappa r_{n-1},
\]

the exact accepted stability intervals remain those of CIIF-CT-12. A longer
or different delay requires a new root or Lyapunov analysis.

## 11. Test G — observability

For output `y=H[x;c]`, a mode with eigenvector `v` is directly visible only
when

\[
Hv\ne0.
\]

A hidden mode is not absent from the system. A visible oscillation is not by
itself a physical wave, causal attribution, or evidence that feedback is
beneficial.

## 12. Frozen comparative outputs

Every later scientific protocol must compare a frozen uncorrected system with
a frozen corrected system and report, as applicable:

1. trajectories and equilibria;
2. spectra or characteristic roots;
3. damping, frequency, period, and mode visibility;
4. peak overshoot for named observables and initial conditions;
5. recovery time under a declared norm and tolerance;
6. delay sensitivity and the stability margin that changes;
7. accumulated correction action, typed resource/cost, and physical work only
   when conjugate variables, units, signs, and boundary are declared;
8. `Delta(t)` or an explicitly justified nonlinear counterpart;
9. correction receipt, residual, dependency invalidation, and closure status;
10. all numerical error controls, failed checks, and unresolved evidence.

## 13. Frozen synthetic control family

The validation contract freezes static exact controls for:

- Boolean zeta/Möbius inversion and equal-spectrum conjugacy;
- no-influence feedback;
- second-order `BC` influence;
- a longer hidden path with `BC=0` but `BDC!=0`;
- stable real decay, damped oscillation, persistent oscillation, growing
  oscillation, and saddle instability;
- immediate monotone decay, immediate alternating decay, delayed real decay,
  delayed damped oscillation, delayed persistent oscillation, and delayed
  instability;
- visible and hidden modes;
- immutable correction receipts, physical/accounting closure, dependency
  propagation, and missing-edge failure.

These are static authority vectors. They are not scientific results.

## 14. Correction action, receipt, and closure

For original action `a` and correction action `c`, preserve

\[
R_a\ne R_c,
\qquad
R_c\ne-R_a.
\]

The correction must carry its own provenance, authorization, lifecycle times,
delay, pending state, resource use, loss, residual, uncertainty, dependency,
audit, and applicable appeal references. It cannot erase the original action,
receipt, result, or physical history.

At a declared physical boundary, require typed closure of the form

\[
\Delta S=B_{\mathrm{in}}-B_{\mathrm{out}}+G-C+R.
\]

Internal transfers cancel exactly once. Original and correction process
accounts must be disjoint or explicitly reconciled. EBU is not thereby a
conserved physical substance, and an unexplained residual cannot be set to
zero by institutional rule.

## 15. Dependency propagation

For a declared acyclic provenance graph, a corrected record invalidates or
marks pending every reachable dependent whose claim may change. Recalculation
uses each dependent record's accepted protocol in topological order and emits
new versions rather than mutating history.

A missing dependency edge prevents certification that an outside record is
unaffected. No interaction sign, topology motif, correction receipt, or
feedback coefficient automatically selects a best topology or assigns blame.

## 16. Framework boundary

The accepted framework already supplies prerequisites:

- I-6: sequential/parallel measurement and declared interaction boundaries;
- I-7: typed dynamic state, histories, delays, routes, queues, and pending
  effects;
- I-8: immutable artifact/manifest correction linkage and a fail-closed
  boundary against physical correction execution; and
- I-9: fidelity, reachability, durability, and CI evidence.

It does not yet implement the richer correction state, physical correction
action/receipt, scientific feedback controller, memory/stability diagnostic
runtime, or institutional policy described here. No accepted framework file
is changed by CLCD-A.

## 17. Book ownership and replacement discipline

The existing synchronized book plan is sufficient and remains
chapter-count-neutral:

- VI.14 owns exact interaction coordinates and omitted-order error;
- VI.15 owns correction locality and fixed-coordinate conjugacy;
- VII.11–VII.12 own provenance dependencies, sensitivity, estimation, and the
  noncausal boundary;
- VIII.2 owns typed correction state;
- VIII.3 owns correction actions, receipts, and closure;
- VIII.10 owns delay and feedback margin;
- VIII.13 owns hidden memory;
- VIII.15 owns stability, overshoot, oscillation, and recovery;
- VIII.16 owns corrected-versus-uncorrected diagnostics;
- IX.18 owns cooperation hypotheses; and
- IX.19 owns protected disclosure, contestability, and correction institutions.

No additional topology, feedback, wave, voltage, or generic limitation chapter
is appended. Each primary chapter must explain what the result enables, give a
life-related example, show the equation or proof, and place limitations beside
the claim. Current manuscripts and PDFs remain unchanged until separately
authorized regeneration.

## 18. Institutional relationship boundary

The project may test whether visible interaction and immutable correction
support cooperation, early disclosure, learning, and recovery. It must also
test surveillance, gaming, power asymmetry, retaliation, free-riding, unequal
benefit capture, double counting, opaque allocation, and correction storms.

The following remain separate:

1. measured group interaction;
2. estimated individual contribution;
3. causally identified responsibility;
4. explicit fairness judgment; and
5. authorized entitlement, compensation, liability, or settlement.

Conditional self-regulation means bounded residual-triggered correction whose
gain and delay survive the declared stability tests. It does not mean automatic
perfection, permanent stability, or a moral ranking of people.

## 19. Nonclaims and exclusions

This authority establishes no:

- universal correction law or best controller;
- guarantee of convergence, monotone improvement, perfect efficiency, zero
  residual, zero delay, or zero correction cost;
- automatic discovery of missing actions, interactions, dependencies, or
  topology;
- physical-wave, phase, superposition, interference, electrical-voltage,
  Hodge, complex-response, or universal Fibonacci/fractal programme;
- causal attribution, blame, fairness, reward, punishment, settlement, or
  institutional legitimacy from an interaction coefficient;
- empirical validation of a social, economic, biological, or physical model;
- production bootstrap, autonomous control, or scientific execution.

Temporal feedback oscillation is a valid model phenomenon under declared
conditions. It is not a universal EBU wave.

## 20. Audit and completion boundary

A fresh audit must independently reproduce every source lock, exact arithmetic
vector, classification, failure, book owner, scope rule, and Git boundary. It
must verify that no accepted file changed and that the candidate adds only the
four companion authority files.

Passing CLCD-A authorizes neither CLCD-B nor CLCD-C. The next possible stage is
an independent authority audit. No implementation, simulation, manuscript
change, rendering, commit, or push is performed by this draft.

CLOSED_LOOP_CORRECTION_DYNAMICS_MILESTONE_AUTHORITY_READY
