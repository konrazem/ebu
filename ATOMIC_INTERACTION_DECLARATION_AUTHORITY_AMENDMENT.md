# Atomic and interaction declaration authority amendment

Status: **prospective declaration authority candidate; unimplemented; unaudited; no scientific execution**.

## 1. Authority, checkpoint, and precedence

This amendment freezes inert declaration schemas and local validators for the accepted atomic-generator, recursive-composition, parallel-interaction, allocation, and institutional-rule vocabulary. It is based on `framework-v0.1` at `a99319a1a420413bb4a88156a7218e113712da99`. That same commit is the required accepted I3C repair, and `ff23d70c022a5c5cf3cb130b55568680de87ae97` is the required integrated atomic-authority ancestor.

The controlling sources are [the atomic-generator authority](ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md), [its mechanical contract](atomic_generator_foundation_contract.json), [its validation contract](atomic_generator_foundation_validation_contract.json), [the post-atomic open-problem register](POST_ATOMIC_OPEN_PROBLEM_REGISTER.md), [the book-traceability manifest](atomic_generator_book_traceability_manifest.json), the accepted I3C settlement-causality repair authority and implementation, and the accepted I1–I3E contracts. This amendment is narrowly additive. It changes no accepted mathematics, declaration, signature, failure, behavior, fixture, book, result, or status. A conflict fails closed.

The normative mechanical source is [the declaration contract](atomic_interaction_declaration_contract.json). [The validation contract](atomic_interaction_declaration_validation_contract.json) freezes synthetic projected evidence, [the predecessor manifest](atomic_interaction_declaration_predecessor_manifest.json) freezes the complete accepted tree, and [the staging plan](ATOMIC_INTERACTION_DECLARATION_IMPLEMENTATION_STAGING_PLAN.md) separates later D1 and D2 implementation. This Markdown and those JSON contracts must agree; disagreement is an integrity failure, never permission to select a preferred rendering.

## 2. Authorization boundary

This package authorizes declarations only. It does not authorize implementation, fixture materialization, tests, execution, optimization, allocation, settlement, simulation, model advance, registry acceptance, publication, book revision, rendering, or scientific interpretation. Every declared object is a T0 record: deterministic construction, deterministic ECJ-1 projection, and its named local validator are its entire permitted runtime surface.

D1 and D2 are designed coherently but are separate future authorization boundaries. D1 does not imply D2. D2 requires a separately authorized, implemented, validated, audited, and accepted D1 predecessor.

## 3. Global declaration contract

- Every declaration is an exact `@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)` with no defaults, omitted fields, unknown fields, subclasses, `None`, or Python `float`.
- All fields are structurally required and immutable. Semantic absence is expressible only by the field’s declared `Applicability` or `ResolutionDetail` arm. There are no prospective runtime-fillable fields.
- Every field except `envelope` participates in deterministic `object_content_payload` in declared order. The envelope hash must match the ECJ-1 projection exactly.
- `ObjectRef` values are opaque exact triples. A local object-kind syntax check proves compatibility only; target meaning requires a directly supplied companion record or separately authorized external acceptance. Validators never resolve references.
- Every tuple collection rejects duplicates. `CANONICAL_REF` orders `ObjectRef` triples; recursive-key collections use declared keys; `SEMANTIC_SEQUENCE` preserves order after duplicate rejection; subset rows order by cardinality and then lexicographic reference key, empty first.
- Numbers are exact `CoreNumberV1`; implicit conversion and binary approximation are forbidden. Unit, dimension, boundary, sign, coordinate, and time compatibility precede arithmetic. Conversion is explicit.
- Each declaration carries only its listed `ClaimStatus` values and all required closed nonclaim codes. Construction without the owning validator yields no accepted declaration.
- Schema version `1.x` permits no field, order, type, enum, default, projection, predicate, precedence, or reference-role change. Such a change needs new prospective authority and a schema major.
- Forbidden behavior includes callbacks, policy/model calls, transitions, flows, jumps, subset evaluation, comparison, optimization, allocation, settlement, registry acceptance, opaque-reference resolution, I/O, clock access, randomness, network access, and mutation.

## 4. Mathematical representation boundary

These formulas define what records may *represent*; the records and validators do not evaluate them.

- An extent declares its family, coordinate, unit, dimension, domain, topology, orientation, and divisibility. Divisibility is declaration-specific; it is never inferred universally. For every finite transformation family, the required identity boundary is \(T_0=I\). A generator claim requires a compatible declared refinement and an explicit right-derivative existence, nonexistence, or unresolved arm.
- Quantity participation and complete augmented-state transformation are distinct. A quantity generator records incidence/participation coordinates and process accounts. A state generator records the full represented augmented-state coordinate set, including explicit inapplicability for every closed role. A constitutive link connects them without identifying either with the other.
- Reparameterization records the map, inverse applicability, derivative scale, regularity, orientation, domain, topology, transformed generator, and joint transformation of densities and integration limits. Orientation reversal requires a separately declared reversible flow; a clock is not silently added to state.
- Finite reconstruction records linear-semigroup, nonlinear-flow, ordered-nonautonomous, or hybrid jump/flow form, with existence, regularity, domain, remainder, and applicable uniqueness/order witnesses. The sole first-order expansion form preserves \(T_0=I\); it does not make a formal series a proved solution.
- Hybrid activation separates continuous within-mode flow from jumps. Off quantity, minimum active bundle, maximum quantity, fixed activation burden, jump/flow order, commitment state, and a once-only fixed-cost account are explicit. Hidden fixed activation and duplicated fixed burden fail closed.
- Boundary equivalence is history-wide over all admitted histories, not snapshot equality or one-state generator equality. It separately records burden, conservation, loss, commitment, applicable settlement, process-account, hidden-state, and explicitly exported internal-topology preservation.

For a finite frozen action set \(A\), a subset protocol contains every \(S\subseteq A\) exactly once, including an explicit \(E(\varnothing)\). The signed Möbius coefficient is

\[\kappa(S)=\sum_{T\subseteq S}(-1)^{|S|-|T|}E(T),\qquad E(S)=\sum_{T\subseteq S}\kappa(T).\]

Zero, positive, negative, and pure higher-order coefficients are admissible exact algebraic results. A truncated representation carries an exact explicit residual. Möbius closure is not physical conservation, causality, value entitlement, wave interference, or a settlement price.

Same-baseline nonadditivity compares joint and singleton values against the same explicit empty baseline. Serial-comparator interaction compares parallel and frozen serial protocols. A mixed-marginal witness records a complete quantity rectangle and the exact finite difference \(E_{11}-E_{10}-E_{01}+E_{00}\); normalization by increments is permitted only under declared regularity and unit conditions. Nonsmooth finite differences remain distinct from derivative claims.

A commutator witness records local execution-order sensitivity in the fixed orientation “left after right minus right after left,” including bracket, finite order difference, remainder, extent, domain, topology, modes, and regularity. Zero at one state does not establish commutativity on a neighbourhood.

A shared factor identifies the joining constraint or mechanism, participating actions, hierarchy (`TREE`, `DAG`, `FEDERATION`, or `OVERLAPPING_AUTHORITY`), owner, lowest complete common or declared factor boundary, distributed protocol when applicable, and visibility/resolution facts. An interaction-topology snapshot separates structural from active hyperedges and records typed interaction references plus factor nodes. Boundary-invariance evidence says only whether exposed interaction survives the declared encapsulation and history scope.

Objectives are feasibility-first and explicitly scalar, Pareto-vector, lexicographic-vector, or epsilon-constrained. Marginal-equalization and KKT evidence is typed, not universal: KKT may be local, global only with convexity, inapplicable for discrete/nonsmooth structure, or unused. Scalar decomposition is optional and closes exactly with path provenance and residual.

Allocation, causal identification, institutional acceptance, and institutional settlement are separate records. Institutional settlement may remain valid when causality is unidentified, but it may not be relabelled causal. Physical history is immutable, rule authority and provenance are explicit, and settlement closes only as \(M=\sum_i s_i+r\) with explicit residual \(r\).

## 5. Stage ownership and declaration inventory

| Stage | Declaration | Owner module | Exact purpose | Validator |
| --- | --- | --- | --- | --- |
| D1 | `ExtentDefinition` | `atomic` | Declare one admissible extent coordinate, its closed family, units, domain, topology, orientation, and declaration-specific divisibility. | `validate_extent_definition` |
| D1 | `AtomicRefinementDeclaration` | `atomic` | Declare whether limiting right refinement exists for one finite transformation family without replacing the finite transaction. | `validate_atomic_refinement` |
| D1 | `QuantityParticipationGeneratorDeclaration` | `atomic` | Declare typed carrier participation per unit of one accepted extent. | `validate_quantity_participation_generator` |
| D1 | `StateTransformationGeneratorDeclaration` | `atomic` | Declare the derivative of the complete augmented state under one extent. | `validate_state_transformation_generator` |
| D1 | `ConstitutiveGeneratorLink` | `atomic` | Link quantity participation to complete state transformation through declared incidence or constitutive rows. | `validate_constitutive_generator_link` |
| D1 | `RegularityAndReparameterizationWitness` | `atomic` | Freeze regularity and the exact generator claim inherited, separately declared, or refused under one coordinate reparameterization. | `validate_regularity_and_reparameterization_witness` |
| D1 | `HybridActivationDeclaration` | `atomic` | Declare discrete activation, minimum bundle, continuous within-mode flow, commitment-aware state, exact jump/flow order, and single fixed-cost placement. | `validate_hybrid_activation` |
| D1 | `FiniteReconstructionWitness` | `atomic` | Declare conditional finite reconstruction, T0 identity, domains, regularity, existence, uniqueness, order, and remainder. | `validate_finite_reconstruction` |
| D1 | `BoundaryHistoryEquivalenceWitness` | `atomic` | Declare all-history boundary equivalence with hidden-state relation preservation and separate burden, conservation, loss, commitment, settlement, and account evidence. | `validate_boundary_history_equivalence` |
| D2 | `JointObjectiveDeclaration` | `interaction` | Declare feasibility-first scalar or typed-vector objective grammar, horizon, uncertainty, existence, regularity, and deterministic tie rule. | `validate_joint_objective` |
| D2 | `FiniteSetInteractionWitness` | `interaction` | Record the complete frozen Boolean-subset protocol, explicit empty value, exact signed Möbius coefficients, and exact optional truncation residuals. | `validate_finite_set_interaction` |
| D2 | `SameBaselineNonadditivityWitness` | `interaction` | Record same-baseline group nonadditivity without conflating it with Möbius or serial-comparator interaction. | `validate_same_baseline_nonadditivity` |
| D2 | `SerialComparatorInteractionWitness` | `interaction` | Record parallel-versus-serial difference under one baseline, state, boundary, horizon, exogenous history, and serial order. | `validate_serial_comparator_interaction` |
| D2 | `MixedMarginalWitness` | `interaction` | Record a local rectangular mixed difference and only when applicable its normalized C2 mixed-marginal interpretation. | `validate_mixed_marginal` |
| D2 | `CommutatorWitness` | `interaction` | Record local execution-order sensitivity, componentwise bracket and order difference, orientation, domain, regularity, scope, and remainder. | `validate_commutator` |
| D2 | `SharedConstraintFactor` | `interaction` | Declare a shared constraint, actions joined, and complete owner under tree, DAG, federation, or overlapping authority. | `validate_shared_constraint_factor` |
| D2 | `InteractionTopologySnapshot` | `interaction` | Declare structural and active typed action hypergraphs, factor incidence, boundary nodes, hidden-state resolution, and boundary-interaction preservation. | `validate_interaction_topology_snapshot` |
| D2 | `AllocationOptimalityWitness` | `interaction` | Record feasibility and the exact conditional certificate for one selected allocation without performing optimization. | `validate_allocation_optimality` |
| D2 | `ScalarDecompositionWitness` | `interaction` | Record an optional path-provenanced decomposition of a selected scalar with explicit closure and residual. | `validate_scalar_decomposition` |
| D2 | `InstitutionalAcceptanceRule` | `interaction` | Declare an inert institutional acceptance rule with authority, provenance, eligibility, horizon, tie, appeal, expiry, and cancellation semantics. | `validate_institutional_acceptance_rule` |
| D2 | `InstitutionalSettlementRule` | `interaction` | Declare an inert settlement rule that preserves physical history, separates causal claims, and requires explicit residual closure. | `validate_institutional_settlement_rule` |

D1 owns exactly nine atomic, finite, hybrid, and recursive-core declarations. D2 owns exactly twelve interaction, topology, allocation, and institutional declarations.

## 6. Exact declaration schemas

### 6.1. `ExtentDefinition` (D1, `atomic`)

Declare one admissible extent coordinate, its closed family, units, domain, topology, orientation, and declaration-specific divisibility.

Object kind: `ebu:object-kind:atomic-interaction:extent-definition`. Schema: `ebu:schema:atomic-interaction:extent-definition-v1` at `1.0.0`. Validator signature: `(record: ExtentDefinition, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `extent_family` | `LiteralDomain[EXTENT_FAMILY]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 3 | `action_family_ref` | `ObjectRef` | NOT_APPLICABLE | No | ACTION_FAMILY |
| 4 | `coordinate_ref` | `ObjectRef` | NOT_APPLICABLE | No | EXTENT_COORDINATE |
| 5 | `coordinate_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 6 | `coordinate_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 7 | `generator_codomain_ref` | `ObjectRef` | NOT_APPLICABLE | No | STATE_OR_QUANTITY_CODOMAIN |
| 8 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | EXTENT_DOMAIN |
| 9 | `topology_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_TOPOLOGY |
| 10 | `orientation` | `LiteralDomain[EXTENT_ORIENTATION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 11 | `divisibility` | `LiteralDomain[DIVISIBILITY_STATUS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 12 | `carrier_or_bundle_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | CARRIER_OR_IMMUTABLE_BUNDLE |
| 13 | `clock_or_order_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | CLOCK_OR_EVENT_ORDER |
| 14 | `path_or_process_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | PATH_OR_PROCESS |
| 15 | `lower_bound` | `Quantity\|Applicability` | coordinate unit | Applicability/Resolution arm | NO_OBJECT_REFERENCE |
| 16 | `upper_bound` | `Quantity\|Applicability` | coordinate unit | Applicability/Resolution arm | NO_OBJECT_REFERENCE |
| 17 | `interval_closure` | `LiteralDomain[INTERVAL_CLOSURE]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `reversible_flow_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | SEPARATELY_DECLARED_REVERSIBLE_FLOW |
| 19 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_UNIVERSAL_DIVISIBILITY`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 21 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `EXTENT_DECLARATION_INVALID` → `EXTENT_DIVISIBILITY_UNDECLARED` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.2. `AtomicRefinementDeclaration` (D1, `atomic`)

Declare whether limiting right refinement exists for one finite transformation family without replacing the finite transaction.

Object kind: `ebu:object-kind:atomic-interaction:atomic-refinement-declaration`. Schema: `ebu:schema:atomic-interaction:atomic-refinement-declaration-v1` at `1.0.0`. Validator signature: `(record: AtomicRefinementDeclaration, extent: ExtentDefinition, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 3 | `action_family_ref` | `ObjectRef` | NOT_APPLICABLE | No | ACTION_FAMILY |
| 4 | `base_state_ref` | `ObjectRef` | NOT_APPLICABLE | No | AUGMENTED_STATE |
| 5 | `finite_transformation_ref` | `ObjectRef` | NOT_APPLICABLE | No | FINITE_TRANSFORMATION_FAMILY |
| 6 | `generator_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | QUANTITY_OR_STATE_GENERATOR |
| 7 | `epsilon_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 8 | `topology_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_TOPOLOGY |
| 9 | `right_derivative_status` | `LiteralDomain[DERIVATIVE_STATUS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 10 | `derivative_witness_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | RIGHT_DERIVATIVE_WITNESS |
| 11 | `nonexistence_witness_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | NONEXISTENCE_WITNESS |
| 12 | `finite_transaction_preserved` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 13 | `indivisible_entity_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | INDIVISIBLE_ENTITY |
| 14 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_MINIMAL_TRANSACTION`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 16 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `ATOMIC_REFINEMENT_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.3. `QuantityParticipationGeneratorDeclaration` (D1, `atomic`)

Declare typed carrier participation per unit of one accepted extent.

Object kind: `ebu:object-kind:atomic-interaction:quantity-participation-generator-declaration`. Schema: `ebu:schema:atomic-interaction:quantity-participation-generator-declaration-v1` at `1.0.0`. Validator signature: `(record: QuantityParticipationGeneratorDeclaration, extent: ExtentDefinition, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 3 | `action_definition_ref` | `ObjectRef` | NOT_APPLICABLE | No | ActionDefinition |
| 4 | `carrier_ref` | `ObjectRef` | NOT_APPLICABLE | No | NONATOMIC_TYPED_CARRIER |
| 5 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 6 | `generator_contract_ref` | `ObjectRef` | NOT_APPLICABLE | No | PURE_GENERATOR_CONTRACT |
| 7 | `input_quantity_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | QUANTITY_DECLARATION |
| 8 | `output_quantity_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | QUANTITY_DECLARATION |
| 9 | `value_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 10 | `value_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 11 | `extent_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 12 | `extent_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 13 | `generator_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | DERIVED_UNIT_VALUE_PER_EXTENT |
| 14 | `generator_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DERIVED_DIMENSION_VALUE_PER_EXTENT |
| 15 | `orientation` | `LiteralDomain[GENERATOR_ORIENTATION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | GENERATOR_DOMAIN |
| 17 | `topology_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_TOPOLOGY |
| 18 | `sign_convention_ref` | `ObjectRef` | NOT_APPLICABLE | No | SIGN_CONVENTION |
| 19 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | NONOVERLAPPING_PROCESS_ACCOUNT |
| 20 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_INSTITUTIONAL_ENDORSEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 22 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `GENERATOR_DECLARATION_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.4. `StateTransformationGeneratorDeclaration` (D1, `atomic`)

Declare the derivative of the complete augmented state under one extent.

Object kind: `ebu:object-kind:atomic-interaction:state-transformation-generator-declaration`. Schema: `ebu:schema:atomic-interaction:state-transformation-generator-declaration-v1` at `1.0.0`. Validator signature: `(record: StateTransformationGeneratorDeclaration, extent: ExtentDefinition, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 3 | `action_definition_ref` | `ObjectRef` | NOT_APPLICABLE | No | ActionDefinition |
| 4 | `augmented_state_schema_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMPLETE_AUGMENTED_STATE_SCHEMA |
| 5 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 6 | `generator_contract_ref` | `ObjectRef` | NOT_APPLICABLE | No | PURE_STATE_GENERATOR_CONTRACT |
| 7 | `state_coordinate_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | STATE_COORDINATE |
| 8 | `derivative_component_units` | `tuple[tuple[ObjectRef,ObjectRef,ObjectRef],...]@CANONICAL_REF_KEY` | NOT_APPLICABLE | No | STATE_COORDINATE_UNIT_DIMENSION |
| 9 | `represented_state_role_codes` | `tuple[str,...]@CANONICAL_CLOSED_STATE_ROLE` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 10 | `inapplicable_state_role_codes` | `tuple[str,...]@CANONICAL_CLOSED_STATE_ROLE` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 11 | `state_completeness_witness_ref` | `ObjectRef` | NOT_APPLICABLE | No | BEHAVIORAL_STATE_SUFFICIENCY_WITNESS |
| 12 | `extent_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 13 | `extent_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 14 | `orientation` | `LiteralDomain[GENERATOR_ORIENTATION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | GENERATOR_DOMAIN |
| 16 | `topology_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_TOPOLOGY |
| 17 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | NONOVERLAPPING_PROCESS_ACCOUNT |
| 18 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 19 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_UNIVERSAL_MINIMAL_STATE`, `NO_CAUSAL_IDENTIFICATION`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 20 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `GENERATOR_DECLARATION_INVALID` → `AUGMENTED_STATE_INCOMPLETE` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.5. `ConstitutiveGeneratorLink` (D1, `atomic`)

Link quantity participation to complete state transformation through declared incidence or constitutive rows.

Object kind: `ebu:object-kind:atomic-interaction:constitutive-generator-link`. Schema: `ebu:schema:atomic-interaction:constitutive-generator-link-v1` at `1.0.0`. Validator signature: `(record: ConstitutiveGeneratorLink, quantity_generator: QuantityParticipationGeneratorDeclaration, state_generator: StateTransformationGeneratorDeclaration, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `quantity_generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | QuantityParticipationGeneratorDeclaration |
| 3 | `state_generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | StateTransformationGeneratorDeclaration |
| 4 | `extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 5 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 6 | `link_kind` | `LiteralDomain[GENERATOR_LINK_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 7 | `map_contract_ref` | `ObjectRef` | NOT_APPLICABLE | No | PURE_CONSTITUTIVE_OR_INCIDENCE_MAP |
| 8 | `quantity_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | QUANTITY_DECLARATION |
| 9 | `state_coordinate_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | STATE_COORDINATE |
| 10 | `unit_relation_rows` | `tuple[tuple[ObjectRef,ObjectRef,ObjectRef,ObjectRef\|Applicability],...]@CANONICAL_REF_KEY` | NOT_APPLICABLE | No | QUANTITY_UNIT_STATE_COORDINATE_DERIVATIVE_UNIT_CONVERSION |
| 11 | `orientation` | `LiteralDomain[GENERATOR_ORIENTATION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 12 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMMON_GENERATOR_DOMAIN |
| 13 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | NONOVERLAPPING_PROCESS_ACCOUNT |
| 14 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_INSTITUTIONAL_ENDORSEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 16 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `GENERATOR_LINK_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.6. `RegularityAndReparameterizationWitness` (D1, `atomic`)

Freeze regularity and the exact generator claim inherited, separately declared, or refused under one coordinate reparameterization.

Object kind: `ebu:object-kind:atomic-interaction:regularity-and-reparameterization-witness`. Schema: `ebu:schema:atomic-interaction:regularity-and-reparameterization-witness-v1` at `1.0.0`. Validator signature: `(record: RegularityAndReparameterizationWitness, source_extent: ExtentDefinition, target_extent: ExtentDefinition, generator: QuantityParticipationGeneratorDeclaration|StateTransformationGeneratorDeclaration, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | QUANTITY_OR_STATE_GENERATOR |
| 3 | `source_extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 4 | `target_extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 5 | `reparameterization_kind` | `LiteralDomain[REPARAMETERIZATION_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 6 | `source_coordinate_ref` | `ObjectRef` | NOT_APPLICABLE | No | EXTENT_COORDINATE |
| 7 | `target_coordinate_ref` | `ObjectRef` | NOT_APPLICABLE | No | EXTENT_COORDINATE |
| 8 | `source_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 9 | `target_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 10 | `map_ref` | `ObjectRef` | NOT_APPLICABLE | No | COORDINATE_MAP |
| 11 | `inverse_map_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | INVERSE_COORDINATE_MAP |
| 12 | `derivative_scale` | `CoreNumberV1\|Applicability` | source extent per target extent | Applicability/Resolution arm | NO_OBJECT_REFERENCE |
| 13 | `regularity_codes` | `tuple[str,...]@CANONICAL_CLOSED_REGULARITY` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 14 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | REPARAMETERIZATION_DOMAIN |
| 15 | `topology_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_TOPOLOGY |
| 16 | `orientation_preserved` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `generator_claim` | `LiteralDomain[REPARAMETERIZATION_CLAIM]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `clock_added_to_state` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 19 | `transformed_generator_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | TRANSFORMED_GENERATOR |
| 20 | `density_and_limits_transform_together` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `integrated_change_invariant` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `witness_ref` | `ObjectRef` | NOT_APPLICABLE | No | REGULARITY_CHAIN_RULE_WITNESS |
| 23 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 24 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 25 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `THEOREM`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_RUNTIME_BEHAVIOR`, `NO_PHYSICAL_PROPAGATION`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 25 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `REPARAMETERIZATION_WITNESS_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.7. `HybridActivationDeclaration` (D1, `atomic`)

Declare discrete activation, minimum bundle, continuous within-mode flow, commitment-aware state, exact jump/flow order, and single fixed-cost placement.

Object kind: `ebu:object-kind:atomic-interaction:hybrid-activation-declaration`. Schema: `ebu:schema:atomic-interaction:hybrid-activation-declaration-v1` at `1.0.0`. Validator signature: `(record: HybridActivationDeclaration, state_generator: StateTransformationGeneratorDeclaration, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `action_definition_ref` | `ObjectRef` | NOT_APPLICABLE | No | ActionDefinition |
| 3 | `state_generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | StateTransformationGeneratorDeclaration |
| 4 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 5 | `mode_schema_ref` | `ObjectRef` | NOT_APPLICABLE | No | DISCRETE_MODE_SCHEMA |
| 6 | `inactive_mode_ref` | `ObjectRef` | NOT_APPLICABLE | No | INACTIVE_MODE |
| 7 | `active_mode_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ACTIVE_MODE |
| 8 | `quantity_coordinate_ref` | `ObjectRef` | NOT_APPLICABLE | No | QUANTITY_COORDINATE |
| 9 | `off_quantity` | `Quantity` | quantity coordinate unit | No | NO_OBJECT_REFERENCE |
| 10 | `minimum_active_quantity` | `Quantity` | quantity coordinate unit | No | NO_OBJECT_REFERENCE |
| 11 | `maximum_active_quantity` | `Quantity` | quantity coordinate unit | No | NO_OBJECT_REFERENCE |
| 12 | `activation_burden` | `Quantity` | burden unit | No | NO_OBJECT_REFERENCE |
| 13 | `activation_transition_ref` | `ObjectRef` | NOT_APPLICABLE | No | DISCRETE_JUMP |
| 14 | `within_mode_flow_ref` | `ObjectRef` | NOT_APPLICABLE | No | CONTINUOUS_WITHIN_MODE_FLOW |
| 15 | `jump_flow_order` | `LiteralDomain[JUMP_FLOW_ORDER]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `fixed_cost_account_ref` | `ObjectRef` | NOT_APPLICABLE | No | SINGLE_FIXED_ACTIVATION_ACCOUNT |
| 17 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | NONOVERLAPPING_PROCESS_ACCOUNT |
| 18 | `commitment_state_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMMITMENT_AWARE_STATE |
| 19 | `fixed_cost_counted_once` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_GLOBAL_OPTIMALITY_WITHOUT_CERTIFICATE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 22 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `HYBRID_ACTIVATION_INVALID` → `FIXED_ACTIVATION_ACCOUNT_DUPLICATED` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.8. `FiniteReconstructionWitness` (D1, `atomic`)

Declare conditional finite reconstruction, T0 identity, domains, regularity, existence, uniqueness, order, and remainder.

Object kind: `ebu:object-kind:atomic-interaction:finite-reconstruction-witness`. Schema: `ebu:schema:atomic-interaction:finite-reconstruction-witness-v1` at `1.0.0`. Validator signature: `(record: FiniteReconstructionWitness, state_generator: StateTransformationGeneratorDeclaration, hybrid: HybridActivationDeclaration|Applicability, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `state_generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | StateTransformationGeneratorDeclaration |
| 3 | `extent_ref` | `ObjectRef` | NOT_APPLICABLE | No | ExtentDefinition |
| 4 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 5 | `initial_state_ref` | `ObjectRef` | NOT_APPLICABLE | No | AUGMENTED_STATE |
| 6 | `finite_transformation_ref` | `ObjectRef` | NOT_APPLICABLE | No | FINITE_TRANSFORMATION |
| 7 | `reconstruction_kind` | `LiteralDomain[RECONSTRUCTION_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 8 | `zero_extent_identity` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 9 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | EVOLUTION_DOMAIN |
| 10 | `operator_domain_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | OPERATOR_DOMAIN |
| 11 | `regularity_witness_ref` | `ObjectRef` | NOT_APPLICABLE | No | RegularityAndReparameterizationWitness |
| 12 | `existence_witness_ref` | `ObjectRef` | NOT_APPLICABLE | No | EXISTENCE_WITNESS |
| 13 | `uniqueness_witness_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | UNIQUENESS_WITNESS |
| 14 | `ordered_evolution_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | ORDERED_EVOLUTION_FAMILY |
| 15 | `hybrid_activation_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | HybridActivationDeclaration |
| 16 | `finite_extent` | `Quantity` | extent unit | No | NO_OBJECT_REFERENCE |
| 17 | `expansion_form` | `LiteralDomain[EXPANSION_FORM]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `remainder_ref` | `ObjectRef` | NOT_APPLICABLE | No | REMAINDER_MEANING |
| 19 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | NONOVERLAPPING_PROCESS_ACCOUNT |
| 20 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `THEOREM`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_RUNTIME_BEHAVIOR`, `NO_PHYSICAL_PROPAGATION`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 22 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `RECONSTRUCTION_CLAIM_UNSUPPORTED` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.9. `BoundaryHistoryEquivalenceWitness` (D1, `atomic`)

Declare all-history boundary equivalence with hidden-state relation preservation and separate burden, conservation, loss, commitment, settlement, and account evidence.

Object kind: `ebu:object-kind:atomic-interaction:boundary-history-equivalence-witness`. Schema: `ebu:schema:atomic-interaction:boundary-history-equivalence-witness-v1` at `1.0.0`. Validator signature: `(record: BoundaryHistoryEquivalenceWitness, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `detailed_boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | DETAILED_BOUNDARY |
| 3 | `parent_boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | PARENT_BOUNDARY |
| 4 | `detailed_state_schema_ref` | `ObjectRef` | NOT_APPLICABLE | No | DETAILED_AUGMENTED_STATE_SCHEMA |
| 5 | `parent_state_schema_ref` | `ObjectRef` | NOT_APPLICABLE | No | PARENT_AUGMENTED_STATE_SCHEMA |
| 6 | `initial_state_relation_ref` | `ObjectRef` | NOT_APPLICABLE | No | RELATED_HIDDEN_INITIAL_STATE |
| 7 | `admitted_history_contract_ref` | `ObjectRef` | NOT_APPLICABLE | No | ALL_ADMITTED_REQUEST_OBSERVATION_HISTORIES |
| 8 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 9 | `equivalence_kind` | `LiteralDomain[EQUIVALENCE_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 10 | `evolution_relation_ref` | `ObjectRef` | NOT_APPLICABLE | No | HISTORY_EQUIVALENCE_PROOF |
| 11 | `observable_codes` | `tuple[str,...]@CANONICAL_CLOSED_BOUNDARY_OBSERVABLE` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 12 | `burden_preservation_ref` | `ObjectRef` | NOT_APPLICABLE | No | BURDEN_PRESERVATION |
| 13 | `conservation_preservation_ref` | `ObjectRef` | NOT_APPLICABLE | No | CONSERVATION_PRESERVATION |
| 14 | `loss_preservation_ref` | `ObjectRef` | NOT_APPLICABLE | No | LOSS_PRESERVATION |
| 15 | `commitment_preservation_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMMITMENT_PRESERVATION |
| 16 | `settlement_preservation_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | SETTLEMENT_VISIBLE_PRESERVATION |
| 17 | `process_account_preservation_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_PROCESS_ACCOUNT_PRESERVATION |
| 18 | `hidden_state_relation_preserved` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 19 | `all_admitted_histories_covered` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `snapshot_equality_only` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `one_state_generator_equality_only` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `internal_topology_export_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | EXPLICIT_INTERNAL_EXPORT |
| 23 | `resolution` | `ResolutionDetail` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 24 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 25 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 26 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `THEOREM`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_INTERNAL_TOPOLOGY_PRESERVATION_UNLESS_EXPORTED`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 26 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `BOUNDARY_HISTORY_EQUIVALENCE_INVALID` → `BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `HASH_MISMATCH`.

### 6.10. `JointObjectiveDeclaration` (D2, `interaction`)

Declare feasibility-first scalar or typed-vector objective grammar, horizon, uncertainty, existence, regularity, and deterministic tie rule.

Object kind: `ebu:object-kind:atomic-interaction:joint-objective-declaration`. Schema: `ebu:schema:atomic-interaction:joint-objective-declaration-v1` at `1.0.0`. Validator signature: `(record: JointObjectiveDeclaration, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 3 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 4 | `action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 5 | `feasibility_constraint_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | FEASIBILITY_CONSTRAINT |
| 6 | `objective_kind` | `LiteralDomain[OBJECTIVE_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 7 | `scalar_objective_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | SCALAR_OBJECTIVE |
| 8 | `vector_component_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | TYPED_VECTOR_COMPONENT |
| 9 | `component_unit_refs` | `tuple[ObjectRef,...]@SEMANTIC_SEQUENCE` | NOT_APPLICABLE | No | UNIT |
| 10 | `selection_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | SELECTION_RULE |
| 11 | `epsilon_constraint_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | EPSILON_CONSTRAINT |
| 12 | `optimization_direction` | `LiteralDomain[OPTIMIZATION_DIRECTION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 13 | `uncertainty_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | UNCERTAINTY |
| 14 | `existence_assumption_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | EXISTENCE_ASSUMPTION |
| 15 | `regularity_assumption_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | REGULARITY_ASSUMPTION |
| 16 | `deterministic_tie_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | DETERMINISTIC_TIE_RULE |
| 17 | `feasibility_first` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 19 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `INSTITUTIONAL_DESIGN_CHOICE`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_UNIVERSAL_SCALAR_OBJECTIVE`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 20 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `OBJECTIVE_GRAMMAR_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.11. `FiniteSetInteractionWitness` (D2, `interaction`)

Record the complete frozen Boolean-subset protocol, explicit empty value, exact signed Möbius coefficients, and exact optional truncation residuals.

Object kind: `ebu:object-kind:atomic-interaction:finite-set-interaction-witness`. Schema: `ebu:schema:atomic-interaction:finite-set-interaction-witness-v1` at `1.0.0`. Validator signature: `(record: FiniteSetInteractionWitness, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `subset_protocol_ref` | `ObjectRef` | NOT_APPLICABLE | No | FROZEN_SUBSET_PROTOCOL |
| 3 | `action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 4 | `initial_augmented_state_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMPLETE_AUGMENTED_STATE |
| 5 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 6 | `state_schema_ref` | `ObjectRef` | NOT_APPLICABLE | No | AUGMENTED_STATE_SCHEMA |
| 7 | `burden_definition_ref` | `ObjectRef` | NOT_APPLICABLE | No | BURDEN_DEFINITION |
| 8 | `value_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 9 | `value_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 10 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 11 | `exogenous_history_ref` | `ObjectRef` | NOT_APPLICABLE | No | FROZEN_EXOGENOUS_HISTORY |
| 12 | `action_removal_semantics` | `LiteralDomain[ACTION_REMOVAL_SEMANTICS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 13 | `constraint_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | CONSTRAINT |
| 14 | `shared_constraint_resolver_ref` | `ObjectRef` | NOT_APPLICABLE | No | SHARED_CONSTRAINT_RESOLVER |
| 15 | `active_mode_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ACTIVE_MODE |
| 16 | `loss_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | LOSS_ACCOUNT |
| 17 | `commitment_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMMITMENT_ACCOUNT |
| 18 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_NONOVERLAPPING_PROCESS_ACCOUNT |
| 19 | `subset_values` | `tuple[tuple[tuple[ObjectRef,...],Quantity],...]@COMPLETE_SUBSET_CARDINALITY_LEX` | value unit | No | NO_OBJECT_REFERENCE |
| 20 | `empty_baseline` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 21 | `mobius_coefficients` | `tuple[tuple[tuple[ObjectRef,...],Quantity],...]@COMPLETE_SUBSET_CARDINALITY_LEX` | value unit | No | NO_OBJECT_REFERENCE |
| 22 | `normalization` | `LiteralDomain[INTERACTION_NORMALIZATION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 23 | `truncation_order` | `IntegerV1\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | NO_OBJECT_REFERENCE |
| 24 | `truncation_residuals` | `tuple[tuple[tuple[ObjectRef,...],Quantity],...]@SUBSET_CARDINALITY_LEX` | value unit | No | NO_OBJECT_REFERENCE |
| 25 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 26 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 27 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `ALGEBRAIC_IDENTITY`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_PHYSICAL_CONSERVATION_FROM_MOBIUS_CLOSURE`, `NO_PHYSICAL_PHASE_INTERFERENCE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 27 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `SUBSET_PROTOCOL_INCOMPLETE` → `SUBSET_LATTICE_INCOMPLETE` → `MOBIUS_CLOSURE_FAILURE` → `TRUNCATION_RESIDUAL_MISMATCH` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.12. `SameBaselineNonadditivityWitness` (D2, `interaction`)

Record same-baseline group nonadditivity without conflating it with Möbius or serial-comparator interaction.

Object kind: `ebu:object-kind:atomic-interaction:same-baseline-nonadditivity-witness`. Schema: `ebu:schema:atomic-interaction:same-baseline-nonadditivity-witness-v1` at `1.0.0`. Validator signature: `(record: SameBaselineNonadditivityWitness, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `subset_protocol_ref` | `ObjectRef` | NOT_APPLICABLE | No | FROZEN_SUBSET_PROTOCOL |
| 3 | `action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 4 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 5 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 6 | `empty_baseline` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 7 | `joint_value` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 8 | `singleton_values` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | value unit | No | NO_OBJECT_REFERENCE |
| 9 | `nonadditivity_value` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 10 | `value_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 11 | `value_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 12 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_PROCESS_ACCOUNT |
| 13 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 14 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `ALGEBRAIC_IDENTITY`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_PHYSICAL_PHASE_INTERFERENCE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 15 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `COMPARATOR_INTERACTION_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.13. `SerialComparatorInteractionWitness` (D2, `interaction`)

Record parallel-versus-serial difference under one baseline, state, boundary, horizon, exogenous history, and serial order.

Object kind: `ebu:object-kind:atomic-interaction:serial-comparator-interaction-witness`. Schema: `ebu:schema:atomic-interaction:serial-comparator-interaction-witness-v1` at `1.0.0`. Validator signature: `(record: SerialComparatorInteractionWitness, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `comparison_protocol_ref` | `ObjectRef` | NOT_APPLICABLE | No | FROZEN_PARALLEL_SERIAL_PROTOCOL |
| 3 | `action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 4 | `parallel_schedule_ref` | `ObjectRef` | NOT_APPLICABLE | No | Schedule |
| 5 | `serial_comparator_ref` | `ObjectRef` | NOT_APPLICABLE | No | ComparatorSchedule |
| 6 | `serial_order_refs` | `tuple[ObjectRef,...]@SEMANTIC_SEQUENCE` | NOT_APPLICABLE | No | ActionInstance |
| 7 | `initial_augmented_state_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMPLETE_AUGMENTED_STATE |
| 8 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 9 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 10 | `exogenous_history_ref` | `ObjectRef` | NOT_APPLICABLE | No | FROZEN_EXOGENOUS_HISTORY |
| 11 | `parallel_value` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 12 | `serial_value` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 13 | `interaction_value` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 14 | `value_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 15 | `value_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 16 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_PROCESS_ACCOUNT |
| 17 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 19 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `ALGEBRAIC_IDENTITY`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_PHYSICAL_PHASE_INTERFERENCE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 19 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `COMPARATOR_INTERACTION_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.14. `MixedMarginalWitness` (D2, `interaction`)

Record a local rectangular mixed difference and only when applicable its normalized C2 mixed-marginal interpretation.

Object kind: `ebu:object-kind:atomic-interaction:mixed-marginal-witness`. Schema: `ebu:schema:atomic-interaction:mixed-marginal-witness-v1` at `1.0.0`. Validator signature: `(record: MixedMarginalWitness, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `action_i_ref` | `ObjectRef` | NOT_APPLICABLE | No | ActionInstance |
| 3 | `action_j_ref` | `ObjectRef` | NOT_APPLICABLE | No | ActionInstance |
| 4 | `quantity_coordinate_i_ref` | `ObjectRef` | NOT_APPLICABLE | No | QUANTITY_COORDINATE |
| 5 | `quantity_coordinate_j_ref` | `ObjectRef` | NOT_APPLICABLE | No | QUANTITY_COORDINATE |
| 6 | `base_quantity_i` | `Quantity` | coordinate i unit | No | NO_OBJECT_REFERENCE |
| 7 | `base_quantity_j` | `Quantity` | coordinate j unit | No | NO_OBJECT_REFERENCE |
| 8 | `delta_i` | `Quantity` | coordinate i unit | No | NO_OBJECT_REFERENCE |
| 9 | `delta_j` | `Quantity` | coordinate j unit | No | NO_OBJECT_REFERENCE |
| 10 | `rectangle_value_00` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 11 | `rectangle_value_10` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 12 | `rectangle_value_01` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 13 | `rectangle_value_11` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 14 | `mixed_difference` | `Quantity` | value unit | No | NO_OBJECT_REFERENCE |
| 15 | `normalized_mixed_marginal` | `Quantity\|ResolutionDetail` | value unit per both coordinate units | No | NO_OBJECT_REFERENCE |
| 16 | `regularity_status` | `LiteralDomain[MIXED_REGULARITY]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `rectangle_domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMPLETE_RECTANGLE_DOMAIN |
| 18 | `active_mode_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ACTIVE_MODE |
| 19 | `topology_snapshot_ref` | `ObjectRef` | NOT_APPLICABLE | No | InteractionTopologySnapshot |
| 20 | `tolerance_ref` | `ObjectRef` | NOT_APPLICABLE | No | NUMERICAL_TOLERANCE |
| 21 | `sign_convention_ref` | `ObjectRef` | NOT_APPLICABLE | No | SIGN_CONVENTION |
| 22 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_PROCESS_ACCOUNT |
| 23 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 24 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 25 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `THEOREM`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_PHYSICAL_PHASE_INTERFERENCE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 25 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `MIXED_MARGINAL_WITNESS_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.15. `CommutatorWitness` (D2, `interaction`)

Record local execution-order sensitivity, componentwise bracket and order difference, orientation, domain, regularity, scope, and remainder.

Object kind: `ebu:object-kind:atomic-interaction:commutator-witness`. Schema: `ebu:schema:atomic-interaction:commutator-witness-v1` at `1.0.0`. Validator signature: `(record: CommutatorWitness, left_generator: StateTransformationGeneratorDeclaration, right_generator: StateTransformationGeneratorDeclaration, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `left_generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | StateTransformationGeneratorDeclaration |
| 3 | `right_generator_ref` | `ObjectRef` | NOT_APPLICABLE | No | StateTransformationGeneratorDeclaration |
| 4 | `base_state_ref` | `ObjectRef` | NOT_APPLICABLE | No | AUGMENTED_STATE |
| 5 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 6 | `domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMMON_FLOW_DOMAIN |
| 7 | `topology_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_TOPOLOGY |
| 8 | `active_mode_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ACTIVE_MODE |
| 9 | `step_extent` | `Quantity` | common extent unit | No | NO_OBJECT_REFERENCE |
| 10 | `composition_orientation` | `LiteralDomain[COMMUTATOR_ORIENTATION]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 11 | `bracket_components` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | state per extent squared | No | NO_OBJECT_REFERENCE |
| 12 | `order_difference_components` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | state | No | NO_OBJECT_REFERENCE |
| 13 | `remainder_components` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | state | No | NO_OBJECT_REFERENCE |
| 14 | `regularity_codes` | `tuple[str,...]@CANONICAL_CLOSED_REGULARITY` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `commutativity_scope` | `LiteralDomain[COMMUTATIVITY_SCOPE]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `commutativity_status` | `LiteralDomain[COMMUTATIVITY_STATUS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `remainder_meaning_ref` | `ObjectRef` | NOT_APPLICABLE | No | ORDER_REMAINDER_MEANING |
| 18 | `process_account_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_PROCESS_ACCOUNT |
| 19 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `THEOREM`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_NEIGHBOURHOOD_COMMUTATIVITY_FROM_ONE_STATE`, `NO_PHYSICAL_PROPAGATION`, `NO_PHYSICAL_PHASE_INTERFERENCE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 21 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `COMMUTATOR_WITNESS_INVALID` → `COMMUTATIVITY_SCOPE_OVERCLAIM` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.16. `SharedConstraintFactor` (D2, `interaction`)

Declare a shared constraint, actions joined, and complete owner under tree, DAG, federation, or overlapping authority.

Object kind: `ebu:object-kind:atomic-interaction:shared-constraint-factor`. Schema: `ebu:schema:atomic-interaction:shared-constraint-factor-v1` at `1.0.0`. Validator signature: `(record: SharedConstraintFactor, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `factor_kind` | `LiteralDomain[FACTOR_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 3 | `action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 4 | `constraint_ref` | `ObjectRef` | NOT_APPLICABLE | No | SHARED_CONSTRAINT |
| 5 | `constraint_unit_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | UNIT |
| 6 | `timing_contract_ref` | `ObjectRef` | NOT_APPLICABLE | No | TIMING_CONTRACT |
| 7 | `hierarchy_kind` | `LiteralDomain[HIERARCHY_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 8 | `ownership_kind` | `LiteralDomain[FACTOR_OWNERSHIP_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 9 | `owner_boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | COMPLETE_FACTOR_OWNER_BOUNDARY |
| 10 | `lowest_common_boundary_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | UNIQUE_LOWEST_COMPLETE_COMMON_BOUNDARY |
| 11 | `distributed_protocol_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | DISTRIBUTED_RESOLUTION_PROTOCOL |
| 12 | `authority_ref` | `ObjectRef` | NOT_APPLICABLE | No | FACTOR_AUTHORITY |
| 13 | `demand_visibility_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | COMPLETE_DEMAND_VISIBILITY |
| 14 | `hidden_state_resolution` | `ResolutionDetail` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `binding_resolution` | `ResolutionDetail` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `MODEL_DEPENDENT_RESULT`, `INSTITUTIONAL_DESIGN_CHOICE`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_PHYSICAL_PROPAGATION`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 18 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `SHARED_BOUNDARY_VISIBILITY_MISSING` → `SHARED_CONSTRAINT_OWNERSHIP_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.17. `InteractionTopologySnapshot` (D2, `interaction`)

Declare structural and active typed action hypergraphs, factor incidence, boundary nodes, hidden-state resolution, and boundary-interaction preservation.

Object kind: `ebu:object-kind:atomic-interaction:interaction-topology-snapshot`. Schema: `ebu:schema:atomic-interaction:interaction-topology-snapshot-v1` at `1.0.0`. Validator signature: `(record: InteractionTopologySnapshot, factors: tuple[SharedConstraintFactor,...], interactions: tuple[FiniteSetInteractionWitness,...], equivalence: BoundaryHistoryEquivalenceWitness|Applicability, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 3 | `state_ref` | `ObjectRef` | NOT_APPLICABLE | No | AUGMENTED_STATE |
| 4 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 5 | `subset_protocol_ref` | `ObjectRef` | NOT_APPLICABLE | No | FROZEN_SUBSET_PROTOCOL |
| 6 | `vertex_action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 7 | `structural_pair_edges` | `tuple[tuple[ObjectRef,ObjectRef,LiteralDomain[INTERACTION_TYPE],ObjectRef],...]@CANONICAL_EDGE` | NOT_APPLICABLE | No | TYPED_PAIR_EDGE |
| 8 | `structural_hyperedges` | `tuple[tuple[tuple[ObjectRef,...],LiteralDomain[INTERACTION_TYPE],ObjectRef],...]@CANONICAL_HYPEREDGE` | NOT_APPLICABLE | No | TYPED_HYPEREDGE |
| 9 | `active_pair_edges` | `tuple[tuple[ObjectRef,ObjectRef,LiteralDomain[INTERACTION_TYPE],ObjectRef],...]@CANONICAL_EDGE` | NOT_APPLICABLE | No | TYPED_PAIR_EDGE |
| 10 | `active_hyperedges` | `tuple[tuple[tuple[ObjectRef,...],LiteralDomain[INTERACTION_TYPE],ObjectRef],...]@CANONICAL_HYPEREDGE` | NOT_APPLICABLE | No | TYPED_HYPEREDGE |
| 11 | `factor_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | SharedConstraintFactor |
| 12 | `factor_incidence` | `tuple[tuple[ObjectRef,ObjectRef],...]@CANONICAL_PAIR` | NOT_APPLICABLE | No | FACTOR_ACTION |
| 13 | `boundary_node_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | BOUNDARY_NODE |
| 14 | `physical_transport_topology_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | PHYSICAL_TRANSPORT_TOPOLOGY |
| 15 | `institutional_constraint_topology_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | INSTITUTIONAL_CONSTRAINT_TOPOLOGY |
| 16 | `hidden_state_resolution` | `ResolutionDetail` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `boundary_equivalence_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | BoundaryHistoryEquivalenceWitness |
| 18 | `exposed_interaction_pairs` | `tuple[tuple[ObjectRef,ObjectRef],...]@CANONICAL_PAIR` | NOT_APPLICABLE | No | DETAILED_REPLACEMENT_INTERACTION |
| 19 | `boundary_preservation_status` | `LiteralDomain[BOUNDARY_PRESERVATION_STATUS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 20 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `DEFINITION`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_PHYSICAL_PROPAGATION`, `NO_INTERNAL_TOPOLOGY_PRESERVATION_UNLESS_EXPORTED`, `NO_PHYSICAL_PHASE_INTERFERENCE`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 22 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `INTERACTION_TOPOLOGY_INVALID` → `HIDDEN_STATE_TOPOLOGY_UNRESOLVED` → `BOUNDARY_INTERACTION_PRESERVATION_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.18. `AllocationOptimalityWitness` (D2, `interaction`)

Record feasibility and the exact conditional certificate for one selected allocation without performing optimization.

Object kind: `ebu:object-kind:atomic-interaction:allocation-optimality-witness`. Schema: `ebu:schema:atomic-interaction:allocation-optimality-witness-v1` at `1.0.0`. Validator signature: `(record: AllocationOptimalityWitness, objective: JointObjectiveDeclaration, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `objective_ref` | `ObjectRef` | NOT_APPLICABLE | No | JointObjectiveDeclaration |
| 3 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 4 | `horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 5 | `selected_action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ActionInstance |
| 6 | `selected_quantities` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | action quantity | No | NO_OBJECT_REFERENCE |
| 7 | `selected_mode_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | SELECTED_MODE |
| 8 | `feasibility_certificate_ref` | `ObjectRef` | NOT_APPLICABLE | No | FEASIBILITY_CERTIFICATE |
| 9 | `certificate_kind` | `LiteralDomain[OPTIMALITY_CERTIFICATE_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 10 | `constraint_qualification_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | CONSTRAINT_QUALIFICATION |
| 11 | `convexity_or_globality_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | GLOBALITY_CERTIFICATE |
| 12 | `active_constraint_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ACTIVE_CONSTRAINT |
| 13 | `marginal_values` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | objective per quantity | No | NO_OBJECT_REFERENCE |
| 14 | `deterministic_tie_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | DETERMINISTIC_TIE_RULE |
| 15 | `kkt_applicability` | `LiteralDomain[KKT_APPLICABILITY]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `result_resolution` | `ResolutionDetail` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 19 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `THEOREM`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_GLOBAL_OPTIMALITY_WITHOUT_CERTIFICATE`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 19 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `ALLOCATION_FEASIBILITY_INVALID` → `OPTIMALITY_CERTIFICATE_INAPPLICABLE` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.19. `ScalarDecompositionWitness` (D2, `interaction`)

Record an optional path-provenanced decomposition of a selected scalar with explicit closure and residual.

Object kind: `ebu:object-kind:atomic-interaction:scalar-decomposition-witness`. Schema: `ebu:schema:atomic-interaction:scalar-decomposition-witness-v1` at `1.0.0`. Validator signature: `(record: ScalarDecompositionWitness, objective: JointObjectiveDeclaration, allocation: AllocationOptimalityWitness, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `objective_ref` | `ObjectRef` | NOT_APPLICABLE | No | JointObjectiveDeclaration |
| 3 | `allocation_ref` | `ObjectRef` | NOT_APPLICABLE | No | AllocationOptimalityWitness |
| 4 | `decomposition_kind` | `LiteralDomain[DECOMPOSITION_KIND]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 5 | `path_ref` | `ObjectRef` | NOT_APPLICABLE | No | DECLARED_DECOMPOSITION_PATH |
| 6 | `baseline_value` | `Quantity` | scalar unit | No | NO_OBJECT_REFERENCE |
| 7 | `selected_total` | `Quantity` | scalar unit | No | NO_OBJECT_REFERENCE |
| 8 | `shares` | `tuple[tuple[ObjectRef,Quantity],...]@CANONICAL_REF_KEY` | scalar unit | No | NO_OBJECT_REFERENCE |
| 9 | `residual` | `Quantity` | scalar unit | No | NO_OBJECT_REFERENCE |
| 10 | `closure_rule` | `LiteralDomain[DECOMPOSITION_CLOSURE_RULE]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 11 | `differentiability_witness_ref` | `ObjectRef\|Applicability` | NOT_APPLICABLE | Applicability/Resolution arm | DIFFERENTIABILITY_WITNESS |
| 12 | `path_provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | PATH_PROVENANCE |
| 13 | `closure_resolution` | `ResolutionDetail` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 14 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `ALGEBRAIC_IDENTITY`, `MODEL_DEPENDENT_RESULT`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_SETTLEMENT_ENTITLEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 16 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `IMPLICIT_ABSENCE_FORBIDDEN` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `SCALAR_DECOMPOSITION_INVALID` → `DECOMPOSITION_PROVENANCE_INCOMPLETE` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.20. `InstitutionalAcceptanceRule` (D2, `interaction`)

Declare an inert institutional acceptance rule with authority, provenance, eligibility, horizon, tie, appeal, expiry, and cancellation semantics.

Object kind: `ebu:object-kind:atomic-interaction:institutional-acceptance-rule`. Schema: `ebu:schema:atomic-interaction:institutional-acceptance-rule-v1` at `1.0.0`. Validator signature: `(record: InstitutionalAcceptanceRule, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `jurisdiction_ref` | `ObjectRef` | NOT_APPLICABLE | No | JURISDICTION |
| 3 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 4 | `issuing_authority_ref` | `ObjectRef` | NOT_APPLICABLE | No | INSTITUTIONAL_AUTHORITY |
| 5 | `eligible_actor_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ELIGIBLE_ACTOR |
| 6 | `eligible_action_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | ELIGIBLE_ACTION |
| 7 | `decision_domain_ref` | `ObjectRef` | NOT_APPLICABLE | No | DISCRETE_ACCEPTANCE_DOMAIN |
| 8 | `rule_expression_ref` | `ObjectRef` | NOT_APPLICABLE | No | INERT_RULE_EXPRESSION |
| 9 | `priority_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | PRIORITY_RULE |
| 10 | `deterministic_tie_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | DETERMINISTIC_TIE_RULE |
| 11 | `effective_horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 12 | `appeal_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | APPEAL_RULE |
| 13 | `expiry_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | EXPIRY_RULE |
| 14 | `cancellation_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | CANCELLATION_RULE |
| 15 | `provenance_authority_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | INSTITUTIONAL_PROVENANCE |
| 16 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 17 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 18 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `INSTITUTIONAL_DESIGN_CHOICE`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_IDENTIFICATION`, `NO_INSTITUTIONAL_ENDORSEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 18 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `INSTITUTIONAL_RULE_INVALID` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

### 6.21. `InstitutionalSettlementRule` (D2, `interaction`)

Declare an inert settlement rule that preserves physical history, separates causal claims, and requires explicit residual closure.

Object kind: `ebu:object-kind:atomic-interaction:institutional-settlement-rule`. Schema: `ebu:schema:atomic-interaction:institutional-settlement-rule-v1` at `1.0.0`. Validator signature: `(record: InstitutionalSettlementRule, acceptance_rule: InstitutionalAcceptanceRule, /) -> None`.

| # | Field | Exact type | Units/dimension rule | Semantic absence allowed | Reference role |
| --- | --- | --- | --- | --- | --- |
| 1 | `envelope` | `CommonObjectEnvelope` | NOT_APPLICABLE | No | COMMON_ENVELOPE |
| 2 | `acceptance_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | InstitutionalAcceptanceRule |
| 3 | `jurisdiction_ref` | `ObjectRef` | NOT_APPLICABLE | No | JURISDICTION |
| 4 | `boundary_ref` | `ObjectRef` | NOT_APPLICABLE | No | AccountingBoundary |
| 5 | `issuing_authority_ref` | `ObjectRef` | NOT_APPLICABLE | No | INSTITUTIONAL_AUTHORITY |
| 6 | `settlement_basis` | `LiteralDomain[SETTLEMENT_BASIS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 7 | `causal_identification_requirement` | `LiteralDomain[CAUSAL_REQUIREMENT]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 8 | `causal_claim_status` | `LiteralDomain[CAUSAL_CLAIM_STATUS]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 9 | `share_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | INSTITUTIONAL_SHARE_RULE |
| 10 | `beneficiary_eligibility_ref` | `ObjectRef` | NOT_APPLICABLE | No | BENEFICIARY_ELIGIBILITY |
| 11 | `settlement_unit_ref` | `ObjectRef` | NOT_APPLICABLE | No | UNIT |
| 12 | `settlement_dimension_ref` | `ObjectRef` | NOT_APPLICABLE | No | DIMENSION |
| 13 | `physical_measurement_ref` | `ObjectRef` | NOT_APPLICABLE | No | IMMUTABLE_PHYSICAL_GROUP_MEASUREMENT |
| 14 | `explicit_residual_required` | `bool` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 15 | `closure_rule` | `LiteralDomain[SETTLEMENT_CLOSURE_RULE]` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 16 | `residual_ownership_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | RESIDUAL_OWNERSHIP_RULE |
| 17 | `dispute_resolution_rule_ref` | `ObjectRef` | NOT_APPLICABLE | No | DISPUTE_RESOLUTION_RULE |
| 18 | `effective_horizon_ref` | `ObjectRef` | NOT_APPLICABLE | No | Horizon |
| 19 | `provenance_authority_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | INSTITUTIONAL_PROVENANCE |
| 20 | `claim_status` | `ClaimStatus` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 21 | `nonclaim_codes` | `tuple[str,...]@CANONICAL_CLOSED_NONCLAIM` | NOT_APPLICABLE | No | NO_OBJECT_REFERENCE |
| 22 | `provenance_refs` | `tuple[ObjectRef,...]@CANONICAL_REF` | NOT_APPLICABLE | No | DECLARATION_PROVENANCE |

Allowed claims: `INSTITUTIONAL_DESIGN_CHOICE`. Required nonclaims: `NO_EMPIRICAL_VALIDATION`, `NO_CAUSAL_MEANING_FOR_INSTITUTIONAL_SHARE`, `NO_INSTITUTIONAL_ENDORSEMENT`, `NO_RUNTIME_BEHAVIOR`.

Identity: Every field except envelope is included; no derived exclusions. Applicability: Every field is structurally required; only declared Applicability or ResolutionDetail arms represent semantic absence. Null and omitted keys are forbidden. References: ObjectRef is opaque; only directly supplied companion records can establish target semantics.

Immutability: every one of the 22 fields above is immutable; prospective fields: none. Versioning: No 1.x field, enum, default, projection, predicate, precedence, or role change; such change requires new prospective authority and schema major.

Validator predicate precedence (first active failure only): `I3_OBJECT_CONTENT_MISMATCH` → `I3_COLLECTION_ORDER_INVALID` → `I3_DUPLICATE_MEMBER` → `UNIT_MISMATCH` → `DIMENSION_MISMATCH` → `INSTITUTIONAL_RULE_INVALID` → `CAUSAL_SETTLEMENT_CONFLATION` → `SETTLEMENT_RESIDUAL_CLOSURE_MISSING` → `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` → `PROHIBITED_INTERFERENCE_CLAIM` → `HASH_MISMATCH`.

## 7. Closed domains

No unlisted enum value is valid. Domain member order is normative.

| Domain | Ordered members |
| --- | --- |
| `EXTENT_FAMILY` | `PHYSICAL_TIME`, `PROCESS_OR_ROUTE_EXTENT`, `TYPED_CARRIER_QUANTITY`, `DIMENSIONLESS_PARTICIPATION` |
| `EXTENT_ORIENTATION` | `INCREASING_CLOCK`, `DECLARED_FORWARD_PROCESS`, `DECLARED_FORWARD_CARRIER`, `ZERO_TO_ONE_PARTICIPATION` |
| `DIVISIBILITY_STATUS` | `DECLARED_NONATOMIC`, `DECLARED_REFINABLE_IMMUTABLE_BUNDLE`, `NOT_DIVISIBLE` |
| `INTERVAL_CLOSURE` | `UNBOUNDED`, `CLOSED`, `LEFT_CLOSED_RIGHT_OPEN`, `OPEN` |
| `DERIVATIVE_STATUS` | `EXISTS`, `DOES_NOT_EXIST`, `UNRESOLVED` |
| `GENERATOR_ORIENTATION` | `FORWARD`, `SEPARATELY_DECLARED_REVERSIBLE` |
| `GENERATOR_LINK_KIND` | `INCIDENCE`, `CONSTITUTIVE`, `COMBINED` |
| `REPARAMETERIZATION_KIND` | `POSITIVE_AFFINE`, `POSITIVE_NONLINEAR_C1`, `ORIENTATION_REVERSING`, `SINGULAR_OR_NONINVERTIBLE`, `NON_C1` |
| `REPARAMETERIZATION_CLAIM` | `AUTOMATIC_UNIT_INHERITANCE`, `EXPLICIT_CHAIN_RULE_WITNESS`, `SEPARATE_REVERSIBLE_FLOW_REQUIRED`, `GENERATOR_CLAIM_REFUSED` |
| `JUMP_FLOW_ORDER` | `ACTIVATION_THEN_FLOW`, `FLOW_THEN_DEACTIVATION`, `ACTIVATION_FLOW_DEACTIVATION` |
| `RECONSTRUCTION_KIND` | `LINEAR_SEMIGROUP`, `NONLINEAR_FLOW`, `ORDERED_NONAUTONOMOUS_EVOLUTION`, `HYBRID_JUMP_FLOW` |
| `EXPANSION_FORM` | `T0_IDENTITY_AND_FIRST_ORDER_REMAINDER` |
| `EQUIVALENCE_KIND` | `SEMICONJUGACY`, `BISIMULATION`, `OTHER_PROVED_HISTORY_WITNESS` |
| `OBJECTIVE_KIND` | `SCALAR`, `VECTOR_PARETO`, `VECTOR_LEXICOGRAPHIC`, `VECTOR_EPSILON_CONSTRAINT` |
| `OPTIMIZATION_DIRECTION` | `MINIMIZE`, `MAXIMIZE` |
| `ACTION_REMOVAL_SEMANTICS` | `QUANTITY_FIXED`, `RULE_REPLAYED` |
| `INTERACTION_NORMALIZATION` | `RAW_WITH_EXPLICIT_EMPTY`, `NORMALIZED_BY_EMPTY` |
| `MIXED_REGULARITY` | `C2_ON_COMPLETE_RECTANGLE`, `NONSMOOTH_FINITE_DIFFERENCE_ONLY`, `GENERALIZED_DERIVATIVE_SEPARATELY_AUTHORIZED`, `UNRESOLVED` |
| `COMMUTATOR_ORIENTATION` | `LEFT_AFTER_RIGHT_MINUS_RIGHT_AFTER_LEFT` |
| `COMMUTATIVITY_SCOPE` | `ONE_STATE`, `DECLARED_NEIGHBOURHOOD` |
| `COMMUTATIVITY_STATUS` | `COMMUTING_ON_DECLARED_NEIGHBOURHOOD`, `NONCOMMUTING`, `ZERO_AT_ONE_STATE_ONLY`, `UNRESOLVED` |
| `FACTOR_KIND` | `CAPACITY`, `COMMITMENT`, `AUTHORITY`, `SAFETY`, `VIABILITY`, `OTHER_DECLARED` |
| `HIERARCHY_KIND` | `TREE`, `DAG`, `FEDERATION`, `OVERLAPPING_AUTHORITY` |
| `FACTOR_OWNERSHIP_KIND` | `LOWEST_COMPLETE_COMMON_BOUNDARY`, `DECLARED_FACTOR_BOUNDARY`, `DISTRIBUTED_PROTOCOL` |
| `BOUNDARY_PRESERVATION_STATUS` | `NOT_ASSESSED`, `PRESERVED_ALL_EXPOSED_SUBSETS`, `NOT_PRESERVED` |
| `OPTIMALITY_CERTIFICATE_KIND` | `GLOBAL_DIRECT`, `KKT_LOCAL`, `KKT_GLOBAL_CONVEX`, `COMBINATORIAL`, `MIXED_INTEGER`, `PARETO`, `LEXICOGRAPHIC`, `EPSILON_CONSTRAINT` |
| `KKT_APPLICABILITY` | `APPLICABLE_LOCAL_ONLY`, `APPLICABLE_GLOBAL_WITH_CONVEXITY`, `INAPPLICABLE_DISCRETE_OR_NONSMOOTH`, `NOT_USED` |
| `DECOMPOSITION_KIND` | `AUMANN_SHAPLEY_RADIAL`, `OTHER_DECLARED_PATH` |
| `DECOMPOSITION_CLOSURE_RULE` | `SELECTED_TOTAL_EQUALS_BASELINE_PLUS_SHARES_PLUS_RESIDUAL` |
| `SETTLEMENT_BASIS` | `INDEPENDENT_INSTITUTIONAL_RULE`, `IDENTIFIED_CAUSAL_RULE` |
| `CAUSAL_REQUIREMENT` | `NOT_REQUIRED_FOR_INSTITUTIONAL_SETTLEMENT`, `IDENTIFIED_REQUIRED_FOR_CAUSAL_CLAIM` |
| `CAUSAL_CLAIM_STATUS` | `NOT_MADE`, `IDENTIFIED` |
| `SETTLEMENT_CLOSURE_RULE` | `MEASURED_TOTAL_EQUALS_SHARE_TOTAL_PLUS_EXPLICIT_RESIDUAL` |
| `INTERACTION_TYPE` | `MOBIUS_FINITE`, `SAME_BASELINE_NONADDITIVITY`, `SERIAL_COMPARATOR`, `MIXED_MARGINAL`, `COMMUTATOR_ORDER`, `SHARED_CONSTRAINT`, `BOUNDARY_PRESERVED` |

The ordered closed nonclaim, regularity, augmented-state-role, and boundary-observable code lists are mechanically frozen in the declaration contract. They are not extensible under schema version 1.x.

## 8. Failure inventory and precedence

The accepted 88-code inventory remains an exact prefix (2125 LF-projection bytes; SHA-256 `0a9e0c22d74d0a1891af19546422296881d2fa6ba16319238def55578c9706d3`). D1 appends exactly 14 codes and D2 appends exactly 22 more. Final count: 124. Existing failure precedence is unchanged.

| Ordinal | Stage | Identifier | Exact trigger meaning |
| --- | --- | --- | --- |
| 89 | D1 | `EXTENT_DECLARATION_INVALID` | Extent family, coordinate, bounds, orientation, domain, topology, carrier/bundle, clock/order, path/process, or reversible-flow applicability is inconsistent. |
| 90 | D1 | `EXTENT_DIVISIBILITY_UNDECLARED` | Refinement or generator semantics are asserted without a compatible explicit divisibility declaration for the extent. |
| 91 | D1 | `ATOMIC_REFINEMENT_INVALID` | The refinement does not preserve T0 identity and the finite transaction, or its derivative existence/nonexistence arms are inconsistent. |
| 92 | D1 | `GENERATOR_DECLARATION_INVALID` | A quantity-participation or state-transformation generator has inconsistent coordinate, codomain, orientation, domain, topology, sign, or account semantics. |
| 93 | D1 | `GENERATOR_LINK_INVALID` | The constitutive/incidence link does not connect compatible quantity and state generators over the same extent, boundary, units, and coordinates. |
| 94 | D1 | `AUGMENTED_STATE_INCOMPLETE` | A state generator omits a represented stock, conversion, loss, burden, commitment, queue, transit, delayed-effect, mode, topology, clock, or policy-memory role without explicitly declaring it inapplicable. |
| 95 | D1 | `REPARAMETERIZATION_WITNESS_INVALID` | The declared parameter map, inverse/applicability, derivative scale, regularity, orientation, transformed generator, density/limit transformation, or integrated-change claim is inconsistent. |
| 96 | D1 | `HYBRID_ACTIVATION_INVALID` | Off, minimum-active, maximum-active, transition, mode, jump/flow order, commitment, or fixed-burden semantics are inconsistent. |
| 97 | D1 | `FIXED_ACTIVATION_ACCOUNT_DUPLICATED` | The same fixed activation burden is represented more than once across its fixed-cost account and process accounts. |
| 98 | D1 | `RECONSTRUCTION_CLAIM_UNSUPPORTED` | The finite reconstruction kind, T0 identity, existence, uniqueness, regularity, ordered evolution, hybrid activation, domain, or remainder support is insufficient for the stated claim. |
| 99 | D1 | `BOUNDARY_HISTORY_EQUIVALENCE_INVALID` | The witness asserts history-wide boundary equivalence without all admitted histories, compatible initial states/evolution, or while relying only on snapshot or one-state generator equality. |
| 100 | D1 | `BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE` | Burden, conservation, loss, commitment, applicable settlement, process-account, hidden-state, or exported internal-topology preservation is incomplete. |
| 101 | D1 | `FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR` | Declaration code exposes or embeds behavior beyond deterministic construction, projection, and local T0 validation. |
| 102 | D1 | `VALIDATOR_BYPASS_FORBIDDEN` | Construction without the owning validator has no accepted declaration result. |
| 103 | D2 | `OBJECTIVE_GRAMMAR_INVALID` | Scalar/vector objective arms, feasibility-first rule, units, selection rule, epsilon constraints, direction, assumptions, or deterministic tie rule are inconsistent. |
| 104 | D2 | `SUBSET_PROTOCOL_INCOMPLETE` | A required frozen subset coordinate or complete nonoverlapping account is absent. |
| 105 | D2 | `SUBSET_LATTICE_INCOMPLETE` | Every Boolean subset including empty is not present exactly once in cardinality-lexicographic order. |
| 106 | D2 | `MOBIUS_CLOSURE_FAILURE` | Exact Möbius coefficient or inverse reconstruction arithmetic fails. |
| 107 | D2 | `TRUNCATION_RESIDUAL_MISMATCH` | An exact truncation reconstruction omits, misorders, mis-signs, or misstates its explicit residual. |
| 108 | D2 | `COMPARATOR_INTERACTION_INVALID` | Same-baseline or serial-comparator interaction values do not close exactly under the frozen common boundary, state, horizon, accounts, and comparison protocol. |
| 109 | D2 | `MIXED_MARGINAL_WITNESS_INVALID` | The complete rectangle, increments, units, regularity arm, finite difference, normalized mixed marginal, topology, tolerance, or sign convention is inconsistent. |
| 110 | D2 | `COMMUTATOR_WITNESS_INVALID` | The ordered compositions, bracket, order difference, remainder, extent, domain, topology, modes, orientation, or regularity evidence is inconsistent. |
| 111 | D2 | `COMMUTATIVITY_SCOPE_OVERCLAIM` | A zero commutator at one state is promoted to neighbourhood commutativity without the required neighbourhood witness. |
| 112 | D2 | `SHARED_CONSTRAINT_OWNERSHIP_INVALID` | A shared factor lacks coherent kind, participating actions, constraint, timing, hierarchy, owner, lowest common boundary, distributed protocol, or authority. |
| 113 | D2 | `SHARED_BOUNDARY_VISIBILITY_MISSING` | The owning or factor boundary cannot see all demand, state, or binding information required to represent the shared constraint. |
| 114 | D2 | `INTERACTION_TOPOLOGY_INVALID` | Structural/active hyperedges, typed interaction references, factor nodes, action membership, boundary, state, horizon, or subset protocol are inconsistent. |
| 115 | D2 | `HIDDEN_STATE_TOPOLOGY_UNRESOLVED` | A topology or factor claim depends on hidden state whose resolution is neither explicit nor fail-closed unresolved. |
| 116 | D2 | `BOUNDARY_INTERACTION_PRESERVATION_INVALID` | A claimed preserved exposed interaction lacks complete subset, coefficient, account, hidden-state, or history-wide boundary evidence. |
| 117 | D2 | `ALLOCATION_FEASIBILITY_INVALID` | The proposed allocation violates feasibility-first constraints, boundary/horizon/action scope, or objective compatibility. |
| 118 | D2 | `OPTIMALITY_CERTIFICATE_INAPPLICABLE` | The certificate kind or KKT claim is incompatible with the declared discrete, nonsmooth, nonconvex, vector, or regularity conditions. |
| 119 | D2 | `SCALAR_DECOMPOSITION_INVALID` | The selected scalar total, baseline, shares, interaction terms, and explicit residual do not satisfy the declared exact closure rule. |
| 120 | D2 | `DECOMPOSITION_PROVENANCE_INCOMPLETE` | A scalar decomposition lacks its declared path, ordering, protocol, action, interaction, objective, or source-witness provenance. |
| 121 | D2 | `INSTITUTIONAL_RULE_INVALID` | An acceptance or settlement rule lacks immutable authority, policy, version, effective interval, deterministic procedure, eligibility, precedence, or provenance. |
| 122 | D2 | `CAUSAL_SETTLEMENT_CONFLATION` | A nonidentified institutional share is causally relabelled or a causal rule lacks identified status. |
| 123 | D2 | `SETTLEMENT_RESIDUAL_CLOSURE_MISSING` | Explicit measured-total equals share-total plus residual closure and immutable physical history are not required. |
| 124 | D2 | `PROHIBITED_INTERFERENCE_CLAIM` | A declaration creates a wave, phase-superposition, physical-interference, or electrical-voltage claim or obligation. |

Formation uses existing `I3_RECORD_FORMATION_INVALID`; object-content, tuple order, duplicates, units/dimensions, implicit absence, and hashes reuse accepted failures. A constructor failure precedes any validator. Otherwise each declaration uses the exact validator order in section 6 and emits only its first active failure. `VALIDATOR_BYPASS_FORBIDDEN` denotes no accepted declaration result when the owning validator is not called.

## 9. Interaction capability

| Representation | Capability |
| --- | --- |
| hypergraph | where and among which actions |
| type | what kind of interaction |
| coefficient | signed finite magnitude under frozen protocol |
| mixed_marginal | local quantity coupling |
| commutator | local execution-order sensitivity |
| shared_factor | joining constraint/mechanism and owner |
| boundary_invariance | whether exposed interaction survives qualifying encapsulation |
| excluded_interpretation | not waves, phase superposition, physical interference, voltage, causality, or settlement entitlement |

The word “interaction” here is algebraic, operational, or institutional as declared. It never denotes wave propagation, phase superposition, physical interference, or electrical voltage.

## 10. Framework surface and import graph

Static reconstruction at the checkpoint finds 23 package modules and 112 direct internal edges. The accepted root export prefix contains 219 names (4410 LF bytes; SHA-256 `b79f89d46e7817d7ea8ba819497641754007bf52e712372ac50b41ef06d66c3d`). The accepted failure prefix contains 88 codes. The exact 65-row public-function signature projection is frozen in the mechanical contract (11404 canonical bytes; SHA-256 `a61da9d09db7a010d71b1bb57b50abb8232db90367f90869b47c970e69e372a5`); accepted type signatures remain locked by its named packaging, specification, I3, and predecessor-byte sources.

| Current module | Exact direct internal imports |
| --- | --- |
| `actions` | `state`, `primitives`, `identity`, `envelopes`, `errors` |
| `artifacts` | `experiment`, `ledger`, `primitives`, `identity`, `envelopes`, `hashing`, `errors` |
| `canonical` | `errors` |
| `causal` | `primitives`, `identity`, `envelopes`, `errors` |
| `commitments` | `actions`, `network`, `primitives`, `identity`, `envelopes`, `errors` |
| `conservation` | `primitives`, `numeric`, `identity`, `envelopes`, `errors` |
| `distortion` | `state`, `primitives`, `numeric`, `identity`, `envelopes`, `errors` |
| `envelopes` | `canonical`, `errors`, `hashing`, `identity` |
| `errors` | none |
| `experiment` | `conservation`, `policy`, `faults`, `primitives`, `identity`, `envelopes`, `hashing`, `errors` |
| `faults` | `primitives`, `identity`, `envelopes`, `hashing`, `errors` |
| `hashing` | `canonical`, `errors`, `identity` |
| `identity` | `canonical`, `errors` |
| `ledger` | `primitives`, `identity`, `envelopes`, `hashing`, `errors` |
| `network` | `state`, `actions`, `primitives`, `identity`, `envelopes`, `registry`, `errors` |
| `numeric` | `canonical`, `errors`, `identity` |
| `observation` | `state`, `primitives`, `identity`, `envelopes`, `errors` |
| `policy` | `observation`, `scheduling`, `primitives`, `identity`, `envelopes`, `hashing`, `errors` |
| `primitives` | `envelopes`, `errors`, `identity`, `numeric` |
| `registry` | `canonical`, `errors`, `envelopes`, `identity` |
| `scheduling` | `actions`, `network`, `commitments`, `primitives`, `identity`, `envelopes`, `errors` |
| `settlement` | `actions`, `observation`, `causal`, `primitives`, `numeric`, `identity`, `envelopes`, `errors` |
| `state` | `canonical`, `primitives`, `identity`, `envelopes`, `hashing`, `errors` |

The smallest coherent expansion is two modules:

| Stage | New module | Exact direct imports | Declarations | Validators |
| --- | --- | --- | --- | --- |
| D1 | `atomic` | `primitives`, `numeric`, `identity`, `envelopes`, `errors` | 9 | 9 |
| D2 | `interaction` | `atomic`, `causal`, `primitives`, `numeric`, `identity`, `envelopes`, `errors` | 12 | 12 |

D1 appends 18 root exports, producing 237 total; D2 appends 24, producing 261 total. The existing 219 names remain the exact prefix. Post-D1 and post-D2 LF hashes are `b78004bc3368d2d7bd8a50de9829bb1b693bffc6a96a8663336aea7922c41d29` and `1506b3b72fd2be9227aab349f7e84e69e3a77c7233fc8da3d244d7471292f4d9`. Exactly 42 new type/validator signatures are frozen mechanically.

D1 root suffix: `ExtentDefinition`, `AtomicRefinementDeclaration`, `QuantityParticipationGeneratorDeclaration`, `StateTransformationGeneratorDeclaration`, `ConstitutiveGeneratorLink`, `RegularityAndReparameterizationWitness`, `HybridActivationDeclaration`, `FiniteReconstructionWitness`, `BoundaryHistoryEquivalenceWitness`, `validate_extent_definition`, `validate_atomic_refinement`, `validate_quantity_participation_generator`, `validate_state_transformation_generator`, `validate_constitutive_generator_link`, `validate_regularity_and_reparameterization_witness`, `validate_hybrid_activation`, `validate_finite_reconstruction`, `validate_boundary_history_equivalence`.

D2 root suffix: `JointObjectiveDeclaration`, `FiniteSetInteractionWitness`, `SameBaselineNonadditivityWitness`, `SerialComparatorInteractionWitness`, `MixedMarginalWitness`, `CommutatorWitness`, `SharedConstraintFactor`, `InteractionTopologySnapshot`, `AllocationOptimalityWitness`, `ScalarDecompositionWitness`, `InstitutionalAcceptanceRule`, `InstitutionalSettlementRule`, `validate_joint_objective`, `validate_finite_set_interaction`, `validate_same_baseline_nonadditivity`, `validate_serial_comparator_interaction`, `validate_mixed_marginal`, `validate_commutator`, `validate_shared_constraint_factor`, `validate_interaction_topology_snapshot`, `validate_allocation_optimality`, `validate_scalar_decomposition`, `validate_institutional_acceptance_rule`, `validate_institutional_settlement_rule`.

The full projected package has 25 modules and 124 edges; the I3 declaration graph plus this extension has 17 modules and 103 edges. Both graphs are acyclic (`cycle_count = 0`). No accepted module or edge changes.

## 11. Projected validation fixtures

The validation contract freezes descriptors, not implementation fixtures. Every vector has the declared schema and stable stage-local ID order. Effective-input collision identity excludes ID and expected output and includes stage, declaration, category, baseline profile, and mutation. Identical effective inputs must have identical outcomes; this projection has no identical-input or conflicting-outcome collision.

| Projection | Future path | Vectors | Success | Failure/no-result | Constructor calls | Validator calls | Predicate calls | Canonical bytes | SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D1 | `tests/framework/fixtures/atomic_declaration_v1.json` | 731 | 108 | 623 | 731 | 327 | 1870 | 469664 | `6b4ecac191320e4ee6b02763249fdc9db14b7fb19091814ca10c6703e36acda9` |
| D2 | `tests/framework/fixtures/interaction_declaration_v1.json` | 1043 | 167 | 876 | 1043 | 527 | 3224 | 662163 | `33f577a28f1964ad79c80a2909512e196825f875f30959c8752d8190fed29399` |

Combined: 1774 vectors, 275 successes, 1499 failures/no-results, and 854 validator calls. Opaque-reference resolutions, runtime-behavior calls, model-state advances, and scientific executions are all exactly zero.

Coverage includes every declaration success; every missing field and exact-type boundary; all 39 enum-bearing positions, their 134 valid member boundaries, and every invalid enum; applicability arms; every tuple order and duplicate boundary; every adjacent validator-precedence pair; every multiply-invalid first-failure selection; and all required semantic, prohibited-claim, validator-bypass, and forbidden-behavior cases.

## 12. Predecessor and preservation

The complete predecessor projection freezes 250 paths from tree `449f71e6535094fd243fc645ef3ef995bafabc2e`, totaling 104706658 raw object-payload bytes. Its canonical projection is 59555 bytes with SHA-256 `b2a28eee2f00fe3ff97091c4a3f228e9299ad36184ccbcb8200d1fbfea5bba0f`. Every predecessor path, mode, type, Git object, raw SHA-256, and byte count is recorded; no path is selected out.

The candidate delta is exactly the five authority files named by the predecessor manifest. All accepted I1–I3E behavior, corrected I3C settlement behavior, declarations, signatures, failure identifiers and precedence, fixtures, root-export prefix, import edges, identities, canonicalization, lifecycle, conservation, quotes, receipts, `GroupReceipt`, provenance, governance, atomic and interaction authority, book traceability, books, manuscripts, PDFs, generators, and Framework I-4 authority/implementation status remain unchanged.

## 13. Explicit nonclaims and excluded programmes

- No empirical validation, causal identification, institutional endorsement, registry acceptance, or scientific result.
- No generator, flow, jump, transition, subset evaluation, comparator, objective, optimizer, allocation, acceptance, settlement, model, simulation, policy, runner, or Gate executes.
- Möbius closure is algebraic, not physical conservation.
- Interaction and allocation witnesses establish no causality or entitlement.
- Institutional rules are inert and confer no authority or execution.
- Wave, phase-superposition, physical-interference, and electrical-voltage programmes remain excluded with no field, enum, validator, implementation, test, fixture, book, or stage obligation.

Wave, phase-superposition, physical-interference, and electrical-voltage programmes are explicitly excluded. They create no declaration, field, enum, validator, implementation, test, fixture, book, or stage obligation. The single prohibited-claim failure and rejection vectors enforce that exclusion; they do not instantiate those programmes.

## 14. Completion boundary

This authority candidate is complete only as a five-file, untracked, unstaged, documentation-only package. Independent authority audit is required before acceptance. D1 implementation, D2 implementation, Framework I-4 implementation, book revision/rendering, and scientific execution are separate later tasks and are not begun.

`ATOMIC_INTERACTION_DECLARATION_AUTHORITY_CANDIDATE_COMPLETE`
