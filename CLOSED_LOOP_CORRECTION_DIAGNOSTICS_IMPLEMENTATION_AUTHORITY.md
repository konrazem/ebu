# EBU Closed-Loop Correction Diagnostics Implementation Authority

**Status:** prospective CLCD-B implementation authority; unimplemented; unexecuted; unaudited

**Version:** 1.0.0

**Accepted branch:** `framework-v0.1`

**Accepted commit:** `cb13514f14260aa1d1deada03ca13845afb9289c`

**Accepted tree:** `bb445e18cb5bde39127b1a682d9bfc17f8b102fb`

## 1. Decision

This authority freezes a small inert implementation of the accepted
Closed-Loop Correction Dynamics milestone. The implementation may validate a
complete declaration and calculate exact finite rational controls. It may not
choose, start, or operate a correction controller.

The capability is valuable because it makes the milestone mechanically
checkable:

- a Möbius coordinate change can be verified as a representation change;
- a finite `BC`, `BDC`, or later derivative path can be exposed exactly;
- continuous and discrete feedback regimes can be classified without a plot;
- hidden modes can be identified relative to an observation map;
- correction closure can retain residual and transfer accounting; and
- a declared dependency graph can carry invalidation to the affected records.

These are implementation properties and declared-model diagnostics. They are
not empirical results.

## 2. Controlling authority

The controlling analytical authority is
`CLOSED_LOOP_CORRECTION_DYNAMICS_MILESTONE_AUTHORITY.md`. Its 14 claims, 28
static controls, three-stage boundary, book ownership, and nonclaims remain
unchanged. Framework I-6 through I-9 remain unchanged.

CLCD-B is limited to pure construction, validation, exact arithmetic, and
synthetic tests. CLCD-C scientific execution remains separately unauthorized.

## 3. Exact path boundary

Future implementation may change exactly six mode-`100644` paths:

1. append 14 CLCD failure codes to `src/ebu_framework/errors.py`;
2. append 27 root exports to `src/ebu_framework/__init__.py`;
3. add `src/ebu_framework/correction_protocol.py`;
4. add `src/ebu_framework/correction_diagnostics.py`;
5. add `tests/framework/fixtures/closed_loop_correction_diagnostics_v1.json`;
6. add `tests/framework/test_closed_loop_correction_diagnostics.py`.

No existing test, fixture, scientific module, execution module, durability
module, publication module, artifact module, trace module, dynamic module,
interaction module, or book file may change.

## 4. Public declaration surface

The protocol module owns these four closed enums:

- `ClosedLoopModelClass`;
- `CorrectionDiagnosticClaimStatus`;
- `ContinuousFeedbackRegime`; and
- `DiscreteFeedbackRegime`.

It owns these fifteen immutable, slot-based, keyword-only declarations:

- `RationalMatrix`;
- `CoordinateConjugacyDeclaration`;
- `FeedbackBlockDeclaration`;
- `FeedbackPathResult`;
- `ContinuousFeedbackDeclaration`;
- `ContinuousFeedbackResult`;
- `DiscreteFeedbackDeclaration`;
- `DiscreteFeedbackResult`;
- `ObservabilityDeclaration`;
- `ObservabilityResult`;
- `CorrectionClosureDeclaration`;
- `CorrectionClosureResult`;
- `DependencyGraphDeclaration`;
- `DependencyInvalidationResult`; and
- `ClosedLoopCorrectionProtocol`.

The exact field order and annotations are frozen mechanically. Formation is
strict: positional construction, unknown fields, missing fields, subclasses,
floating-point values, mutable collections, duplicate members, empty required
text, and hidden defaults fail closed.

The literal public name `CorrectionActionReceipt` is not introduced. Accepted
I-8 `CorrectionRecord` remains an artifact/manifest correction record, not a
physical correction-action receipt.

## 5. Public callable surface

The implementation exports exactly eight positional-only pure callables:

1. `validate_closed_loop_correction_protocol`;
2. `validate_coordinate_conjugacy`;
3. `detect_feedback_path`;
4. `classify_continuous_feedback`;
5. `classify_discrete_feedback`;
6. `evaluate_observability`;
7. `evaluate_correction_closure`; and
8. `compute_dependency_invalidation`.

No callable accepts a model callback, store, provider, runner, Gate,
authorization service, clock service, filesystem path, network client, random
source, settlement rule, or publication target.

## 6. Exact rational matrices

`RationalMatrix` contains a nonempty rectangular tuple of nonempty tuples of
exact `RationalV1` values. Matrix shape and row order are semantic.

The implementation may perform only finite exact addition, subtraction,
multiplication, identity construction, equality, and finite integer powers.
It does not expose a general inverse or matrix exponential.

## 7. Coordinate conjugacy

`validate_coordinate_conjugacy(declaration, a_e, /)` requires a complete
declared subset order, square `Z` and `M`, and

\[
MZ=ZM=I.
\]

It returns

\[
A_I=MA_EZ.
\]

It does not infer a subset basis, repair an incomplete table, estimate a
matrix, or claim that the coordinate change modifies physical dynamics.

## 8. Finite feedback-path diagnostic

For the declared block matrix

\[
K=\begin{bmatrix}A&B\\C&D\end{bmatrix},
\]

`detect_feedback_path(block, max_order, /)` calculates exact finite witnesses

\[
PK^mJ-A^m,
\qquad 1\le m\le \texttt{max_order}.
\]

It returns `BC`, the first nonzero tested order, and that exact operator. If no
tested operator is nonzero, the result is `NOT_APPLICABLE`; it does not claim
that the full trajectory difference is identically zero. This prevents a
finite search from silently becoming a universal no-influence theorem.

The frozen controls include a direct `BC` path and a hidden `BDC` path with
`BC=0`.

## 9. Continuous regime classifier

For

\[
\dot x=-ax+bc,
\qquad
\dot c=-kx-dc,
\]

the implementation calculates

\[
s=a+d,
\qquad q=ad+bk,
\qquad \mathfrak D=s^2-4q.
\]

The closed regimes are stable real decay, stable damped oscillation,
persistent undamped boundary oscillation, growing oscillation, growing real
modes, saddle instability, and other non-asymptotic boundary. Classification
is exact and model-local. It does not prove benefit, safety, or empirical
validity.

## 10. Discrete regime classifier

The immediate model uses root `1-kappa`. The one-step delayed model uses

\[
z^2-z+\kappa.
\]

The exact closed regimes distinguish monotone decay, deadbeat response,
alternating decay, delayed real decay, delayed critical decay, delayed damped
oscillation, persistent boundary, and instability. Longer, distributed,
fractional, nonlinear, or state-dependent delays are not classified.

## 11. Observability

`evaluate_observability` multiplies a declared observation matrix by each
declared column mode. A mode is marked visible exactly when the product is
nonzero. Hidden does not mean absent, harmless, or causally irrelevant.

## 12. Correction closure

The closure diagnostic calculates

\[
R_{\mathrm{closure}}
=B_{\mathrm{in}}-B_{\mathrm{out}}+G-C+R
\]

and compares it with the declared stock change. Every internal transfer is an
explicit equal out/in pair and cancels exactly once. A mismatched transfer is
a formation failure. A nonclosing account returns `closes=false`; it does not
erase or change the declared residual. EBU is not declared to be a conserved
physical substance.

## 13. Dependency invalidation

The dependency declaration uses unique visible-ASCII vertex IDs, unique edges,
an explicit corrected vertex, and an explicit inventory-complete flag. The
graph must be acyclic. When complete, the diagnostic returns all reachable
descendants and one deterministic topological order preserving the declared
vertex order.

An incomplete inventory cannot certify outside records as unaffected. No
missing edge is interpreted as independence and no topology is inferred.

## 14. Protocol completeness

`ClosedLoopCorrectionProtocol` records all 29 fields frozen by CLCD-A through
exact object references, closed enums, required-output names, falsifiers, and
nonclaims. `validate_closed_loop_correction_protocol` checks completeness,
ordering, duplicates, applicability, and the mandatory exclusion set. It does
not resolve the references or execute their content.

## 15. Failure surface

Exactly fourteen failures are appended, in this order:

1. `CLCD_RECORD_FORMATION_INVALID`;
2. `CLCD_PROTOCOL_INCOMPLETE`;
3. `CLCD_MATRIX_SHAPE_INVALID`;
4. `CLCD_COORDINATE_BASIS_INCOMPLETE`;
5. `CLCD_MOBIUS_INVERSE_INVALID`;
6. `CLCD_COORDINATE_EQUIVALENCE_INVALID`;
7. `CLCD_FEEDBACK_BLOCK_INVALID`;
8. `CLCD_FEEDBACK_PATH_INVALID`;
9. `CLCD_STABILITY_CLASSIFICATION_INVALID`;
10. `CLCD_DELAY_CLASSIFICATION_INVALID`;
11. `CLCD_OBSERVABILITY_INVALID`;
12. `CLCD_CORRECTION_CLOSURE_INVALID`;
13. `CLCD_DEPENDENCY_GRAPH_INVALID`; and
14. `CLCD_EXECUTION_FORBIDDEN`.

Every failure uses `FailureStage.STATIC_AND_SYNTHETIC_VALIDATION`, preserves an
unstarted scientific status, advances no state or policy memory, and is
nonretryable without a corrected declaration.

## 16. Import and inertness boundary

The new protocol module may import only `identity`, `numeric`, `primitives`,
and `errors`. The new diagnostics module may import only
`correction_protocol`, `numeric`, and `errors`. Root `__init__` may import and
export the two modules.

There is no import or dynamic reachability to `execution`, `dynamic`,
`durability`, `authorization`, `authorization_use`, `publication`, `recovery`,
`artifacts`, `traces`, a provider, a runner, a model callback, or a scientific
state transition.

## 17. Frozen validation family

The validation contract freezes 34 ordered vectors:

- protocol completeness and incomplete-protocol failure;
- matrix formation, Möbius inverse, and similarity;
- direct, hidden, and absent finite feedback paths;
- seven continuous regimes;
- eight immediate/delayed discrete regimes;
- visible and hidden modes;
- closing and nonclosing correction accounts plus transfer mismatch;
- dependency reachability, incomplete inventory, and cycle failure; and
- two static prohibited-reachability/nonclaim controls.

Every dynamic vector invokes its exact owning public interface once. Static
controls import no framework module.

## 18. Book traceability

CLCD-B adds no chapter. It supplies implementation evidence to the existing
owners VI.15, VIII.3, VIII.10, VIII.13, VIII.15, and VIII.16, with the
dependency control supporting VII.11–VII.12. Current manuscripts and PDFs do
not change under this authority.

## 19. Exclusions

This authority establishes no controller, optimization, policy choice,
trajectory integration, matrix exponential, empirical fit, automatic
topology, causal attribution, settlement, fairness result, perfect efficiency,
physical wave, phase, superposition, electrical voltage, universal Fibonacci
law, production operation, or scientific execution.

## 20. Completion boundary

A fresh independent audit must reproduce the predecessor, exact schemas,
signatures, failures, exports, import graph, 34 vectors, path boundary, and
inertness controls. Passing this authority permits only a separate
implementation candidate and synthetic validation. It does not permit CLCD-C.

CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_AUTHORITY_READY
