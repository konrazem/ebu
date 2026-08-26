# Closed-Loop Correction Diagnostics Implementation Staging Plan

**Status:** prospective implementation sequence; no implementation or execution authorized by this file

**Accepted commit:** `cb13514f14260aa1d1deada03ca13845afb9289c`

## Stage B1 — public declarations and failures

Add `correction_protocol.py` with the four enums and fifteen declarations
frozen by the mechanical contract. Append exactly fourteen failure codes to
`FailureCode`. Formation must remain immutable, keyword-only, exact-type, and
fail-closed.

No diagnostic calculation, model callback, state transition, or I-8 record
change occurs in B1.

## Stage B2 — exact diagnostics

Add `correction_diagnostics.py` with the eight positional-only pure callables.
Use `Fraction` internally only after exact conversion from `RationalV1`, and
return normalized `RationalV1` values. Implement finite matrix operations,
finite derivative-path detection, scalar continuous/discrete classification,
observability multiplication, closure arithmetic, and acyclic dependency
reachability.

Do not implement matrix exponentials, trajectory integration, callbacks,
stores, providers, or controllers.

## Stage B3 — exports

Append the exact 27-name suffix to root `__all__` and import only the two new
modules. Preserve the exact 444-name predecessor prefix.

## Stage B4 — fixture and direct tests

Materialize
`tests/framework/fixtures/closed_loop_correction_diagnostics_v1.json` from the
34 frozen validation vectors. Add one direct test module that:

- invokes every owning callable once per owning-call vector;
- constructs the exact owning declaration once per formation vector;
- reconstructs all expected rational results and first failures;
- checks schemas, annotations, signatures, failures, exports, imports, and
  forbidden reachability;
- confirms zero model steps and zero scientific executions; and
- verifies the fixture byte identity.

## Stage B5 — applicable predecessor regression

Run the new direct suite, the complete accepted framework discovery, and the
repository scope and whitespace checks in a disposable verified environment.
Any legacy inventory assertion made obsolete only by the authorized additive
surface must be reported rather than silently changed. No existing test path
is authorized for modification.

## Stage B6 — independent audit and integration

An independent audit must reconstruct the authority package, predecessor,
future schemas, failures, exports, signatures, graph, fixture, and all 34
vectors. Only after PASS may the exact six implementation paths be committed
and integrated normally without force.

## Closed path set

Modified:

- `src/ebu_framework/errors.py`
- `src/ebu_framework/__init__.py`

New:

- `src/ebu_framework/correction_protocol.py`
- `src/ebu_framework/correction_diagnostics.py`
- `tests/framework/fixtures/closed_loop_correction_diagnostics_v1.json`
- `tests/framework/test_closed_loop_correction_diagnostics.py`

Everything else is prohibited.

## Stop conditions

Stop for a mathematical contradiction, an authority disagreement, an
unrepresentable vector, an import/reachability escape, an unexpected
predecessor behavioral regression, or unsafe repository state. Checker bugs,
missing optional utilities, stale display text, and other nonsemantic workflow
issues are not scientific blockers and must be corrected or reported without
abandoning the stage.

CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_STAGING_PLAN_READY
