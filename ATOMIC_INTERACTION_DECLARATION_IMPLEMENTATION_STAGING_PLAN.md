# Atomic and interaction declaration implementation staging plan

Status: **prospective staging plan only; no implementation is authorized or begun**.

## 1. Purpose and authority boundary

This plan divides a possible later implementation of the [atomic and interaction declaration authority](ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md) into two independently authorized stages. The exact schemas, signatures, domains, predicates, precedence, failures, exports, imports, fixture projections, and nonclaims come from [the mechanical contract](atomic_interaction_declaration_contract.json) and [the validation contract](atomic_interaction_declaration_validation_contract.json). The complete accepted base is frozen by [the predecessor manifest](atomic_interaction_declaration_predecessor_manifest.json).

This document does not authorize file creation, production edits, test or fixture materialization, imports, execution, commit, push, or acceptance. Future implementers must not edit the frozen authority to make implementation or tests pass. Any incompatibility fails closed and returns to a separately authorized authority-correction stage.

## 2. Shared preconditions for any later implementation

Before D1 or D2 begins, a future task must independently establish:

1. the specifically authorized stage;
2. a clean isolated worktree on the exact accepted predecessor named for that stage;
3. equality of local, tracking, and freshly queried live target refs;
4. complete predecessor-manifest reconstruction;
5. strict duplicate-key parsing and matching Markdown/JSON authority;
6. absence of every unauthorized generated path;
7. a reviewed exact-path scope; and
8. explicit permission for the implementation and tests that the stage requires.

Both stages remain standard-library-only. They may construct frozen records, project ECJ-1 content, and run named local T0 validators. They may not add behavior callbacks, resolve opaque references, execute generators/flows/jumps, evaluate model subsets, optimize, allocate, settle, simulate, advance model state, invoke a Gate, or create scientific claims.

## 3. Stage D1 — atomic, finite, hybrid, and recursive core

### 3.1 Authorization dependency

D1 requires an independently audited and accepted five-file authority package based on `a99319a1a420413bb4a88156a7218e113712da99`. Acceptance of this plan alone is insufficient.

### 3.2 Exact declaration ownership

The new `atomic` module owns exactly:

1. `ExtentDefinition`
2. `AtomicRefinementDeclaration`
3. `QuantityParticipationGeneratorDeclaration`
4. `StateTransformationGeneratorDeclaration`
5. `ConstitutiveGeneratorLink`
6. `RegularityAndReparameterizationWitness`
7. `HybridActivationDeclaration`
8. `FiniteReconstructionWitness`
9. `BoundaryHistoryEquivalenceWitness`

It also owns the nine adjacent named validators in declaration order. Its exact direct internal imports are `primitives`, `numeric`, `identity`, `envelopes`, and `errors`; no other direct import is permitted.

### 3.3 Exact path scope

Only these five paths may change in a future D1 implementation:

| Disposition | Path | Purpose |
| --- | --- | --- |
| Modified | `src/ebu_framework/errors.py` | Append the 14 D1 failure identifiers, preserving the accepted 88-code prefix. |
| Modified | `src/ebu_framework/__init__.py` | Append nine D1 types and then nine D1 validators, preserving the accepted 219-name prefix. |
| New | `src/ebu_framework/atomic.py` | Implement only the nine frozen D1 records, ECJ-1 projections, and pure local validators. |
| New | `tests/framework/fixtures/atomic_declaration_v1.json` | Materialize exactly the frozen 731-vector D1 projection. |
| New | `tests/framework/test_atomic_declarations.py` | Verify D1 formation, projection, predicate, precedence, failure, export, import, and inertness contracts. |

No sixth path is authorized.

### 3.4 Frozen surface delta

D1 appends failures 89–102 in the contract’s exact order, producing 102 total. It appends exactly 18 root exports—nine record types followed by nine validators—producing 237 total. The projected root-export LF SHA-256 is `b78004bc3368d2d7bd8a50de9829bb1b693bffc6a96a8663336aea7922c41d29`.

The materialized fixture must contain exactly 731 vectors: 108 successes and 623 failures or deliberate no-results; 731 constructor calls, 327 validator calls, and 1,870 predicate calls. Its canonical array projection must be exactly 469,664 bytes with SHA-256 `6b4ecac191320e4ee6b02763249fdc9db14b7fb19091814ca10c6703e36acda9`.

### 3.5 Required implementation order

1. Reconstruct and verify the accepted prefixes and full predecessor before editing.
2. Append the exact D1 failures without altering existing members or precedence.
3. Implement the nine frozen keyword-only dataclasses in declaration order.
4. Implement deterministic ECJ-1 projection for every field except `envelope`.
5. Implement each pure validator in its exact predicate order and first-failure rule.
6. Append the exact root exports without reordering the accepted prefix.
7. Materialize the D1 descriptor projection byte-for-byte.
8. Add only the scoped static/T0 tests and run only the separately authorized validation set.
9. Reconstruct exports, failures, signatures, imports, fixture identity, and exact path scope independently.

### 3.6 D1 acceptance gate

D1 may be accepted only if every projected vector passes, all counts and identities match, the import graph is acyclic, every opaque-reference-resolution/runtime/state-advance/scientific-execution counter is zero, predecessor bytes remain unchanged, and independent implementation audit accepts the exact five-path delta. D1 acceptance does not authorize D2.

## 4. Stage D2 — interaction, topology, allocation, and institutions

### 4.1 Authorization dependency

D2 requires a separately authorized, implemented, validated, audited, committed, and accepted D1 predecessor at an identity named by the future D2 task. The present checkpoint and authority candidate do not supply that later SHA.

### 4.2 Exact declaration ownership

The new `interaction` module owns exactly:

1. `JointObjectiveDeclaration`
2. `FiniteSetInteractionWitness`
3. `SameBaselineNonadditivityWitness`
4. `SerialComparatorInteractionWitness`
5. `MixedMarginalWitness`
6. `CommutatorWitness`
7. `SharedConstraintFactor`
8. `InteractionTopologySnapshot`
9. `AllocationOptimalityWitness`
10. `ScalarDecompositionWitness`
11. `InstitutionalAcceptanceRule`
12. `InstitutionalSettlementRule`

It also owns the twelve adjacent named validators in declaration order. Its exact direct internal imports are `atomic`, `causal`, `primitives`, `numeric`, `identity`, `envelopes`, and `errors`; no other direct import is permitted.

### 4.3 Exact path scope

Only these five paths may change in a future D2 implementation:

| Disposition | Path | Purpose |
| --- | --- | --- |
| Modified | `src/ebu_framework/errors.py` | Append the 22 D2 failures after the accepted D1 suffix. |
| Modified | `src/ebu_framework/__init__.py` | Append twelve D2 types and then twelve D2 validators after the accepted D1 suffix. |
| New | `src/ebu_framework/interaction.py` | Implement only the twelve frozen D2 records, ECJ-1 projections, and pure local validators. |
| New | `tests/framework/fixtures/interaction_declaration_v1.json` | Materialize exactly the frozen 1,043-vector D2 projection. |
| New | `tests/framework/test_interaction_declarations.py` | Verify D2 formation, projection, predicate, precedence, failure, export, import, and inertness contracts. |

No sixth path is authorized.

### 4.4 Frozen surface delta

D2 appends failures 103–124 in the contract’s exact order, producing 124 total. It appends exactly 24 root exports—twelve record types followed by twelve validators—producing 261 total. The projected root-export LF SHA-256 is `1506b3b72fd2be9227aab349f7e84e69e3a77c7233fc8da3d244d7471292f4d9`.

The materialized fixture must contain exactly 1,043 vectors: 167 successes and 876 failures or deliberate no-results; 1,043 constructor calls, 527 validator calls, and 3,224 predicate calls. Its canonical array projection must be exactly 662,163 bytes with SHA-256 `33f577a28f1964ad79c80a2909512e196825f875f30959c8752d8190fed29399`.

### 4.5 Required implementation order

1. Reconstruct the independently accepted D1 predecessor and verify every accepted prefix.
2. Append the exact D2 failures without changing the accepted 102-code prefix.
3. Implement the twelve frozen keyword-only dataclasses in declaration order.
4. Implement deterministic ECJ-1 projection for every field except `envelope`.
5. Implement each pure validator in exact predicate order and first-failure rule.
6. Append the exact root exports without reordering the accepted 237-name prefix.
7. Materialize the D2 descriptor projection byte-for-byte.
8. Add only the scoped static/T0 tests and run only the separately authorized validation set.
9. Reconstruct exports, failures, signatures, imports, fixture identity, and exact path scope independently.

### 4.6 D2 acceptance gate

D2 may be accepted only if every D2 vector passes, D1 remains unchanged, all counts and identities match, the projected package has exactly 25 modules and 124 direct internal edges, the I3-plus-extension graph has exactly 17 modules and 103 edges, both graphs have zero cycles, every prohibited call/advance counter is zero, and independent implementation audit accepts the exact five-path delta.

## 5. Prohibited coupling and scope expansion

Neither stage may alter existing declarations for stylistic consistency, consolidate modules, add convenience defaults, infer reference targets, broaden enum domains, weaken predicate precedence, materialize unspecified fixtures, add dependencies, or introduce execution helpers. Wave, phase-superposition, physical-interference, and electrical-voltage programmes remain excluded and create no implementation obligation.

Framework I-4 implementation, book revision, PDF rendering, empirical work, scientific execution, publication, and any later D3 stage are outside both D1 and D2. A future task must authorize each separately.

## 6. Handoff marker

`ATOMIC_INTERACTION_DECLARATION_IMPLEMENTATION_STAGING_PLAN_COMPLETE`
