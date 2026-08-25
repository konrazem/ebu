# Unified Python Research Framework I-7 Dynamic Coordination Authority Amendment

## Status and authority

- **Status:** Prospective, unimplemented, unexecuted, unaudited authority candidate
- **Profile:** repository-local ebu-framework Authority drafting
- **Candidate branch:** framework/i-7-dynamic-coordination-authority-replacement
- **Required base commit:** 28a43846773ec2ac1f709e5387f3090f789c4a42
- **Required base tree:** 6b899f4707408409125746822e832f833c4dbcf5
- **Scope:** Framework I-7 Dynamic Coordination records, deterministic static mechanics, route refusal, and fail-closed T3 boundary only

This five-file package is authority only. It does not implement, import the framework, run project tests, materialize a fixture, advance model state, call a policy, execute a simulation or benchmark, create a result, edit a book, render, stage, commit, or push. The mechanical contract, validation contract, predecessor manifest, and implementation-path manifest are coequal mechanical controls. Any disagreement requires refusal.

Precedence is narrow: accepted bytes at the required tree; accepted I-3 through I-6 authority/contracts/implementations/manifests within their scopes; Dynamic Coordination Foundation v0.1 for dynamic vocabulary and six static examples; canonical topology/motif authority for domain responsibility, typed layers, and noninference; then this amendment only where it freezes formerly unspecified I-7 mechanics.

## Resolved scope

Repository reconstruction verifies all of the following:

- exactly ten public records: five I-3-deferred records and five plan-listed dynamic records;
- exactly one append-only availability arm, `ISOLATED`, after the accepted five-member prefix;
- exactly two plan-listed public callables;
- an exact private NoReturn T3 permit extension following the accepted I-6 pattern;
- `RouteRef` remains removed; accepted `ObjectRef` and `RoutePlan` remain the only route-reference mechanics;
- route semantics remain `PROVISIONAL_PART_VII`; no live reroute can succeed in I-7;
- dynamic scope covers capacity/topology change, admission, queue/congestion, reservation shortfall, delay, transit, rerouting refusal, delayed effects, commitment state, and policy-memory pairing; and
- validation is T0 source/refusal inspection plus six isolated T2 arithmetic cases, with a controlled but unavailable T3 boundary.

Domains, models, and providers declare or measure topology, dependency, routes, capacity, policy, delay, numerical policy, and admissibility. EBU represents and validates those declarations. It does not discover a best topology, route, policy, hidden edge, motif, poset, or hypergraph law.

Structural topology, active topology, and observed topology are different typed roles. Observation has provenance; causality remains absent unless a separate accepted identification protocol is referenced. Structural motifs, posets, and hypergraphs remain declared types or equivalence classes, never automatically inferred physical laws.

## Ten exact public records

| # | Owner | Record | Exact field order |
|---|---|---|---|
| 1 | network | `TopologyChangeEvent` | `envelope`, `effective_epoch`, `topology_before_ref`, `topology_after_ref`, `structural_topology_ref`, `active_topology_before_ref`, `active_topology_after_ref`, `change_kind`, `affected_provider_refs`, `affected_node_refs`, `affected_edge_refs`, `availability_before`, `availability_after`, `declaration_status`, `declaring_authority_ref`, `observation_provenance_ref`, `causal_identification_protocol_ref`, `cause_claim_status` |
| 2 | commitments | `AdmissionDecision` | `envelope`, `decision_epoch`, `request_ref`, `capacity_record_ref`, `topology_snapshot_ref`, `commitment_ref`, `policy_decision_ref`, `presented`, `admitted_to_queue`, `rejected`, `pending_outside_queue`, `disposition`, `allocation_rule_ref`, `queue_rule_ref`, `admissibility_evidence_refs`, `domain_authority_ref` |
| 3 | commitments | `QueueRecord` | `envelope`, `capacity_locus_ref`, `resource_type_ref`, `epoch`, `opening_queue`, `admitted_arrival`, `completed_flow`, `expired_cancelled_abandoned`, `closing_queue`, `rejected_outside_queue`, `pending_outside_queue`, `admission_decision_refs`, `queue_discipline_ref`, `priority_rule_ref`, `congestion_ref`, `domain_authority_ref` |
| 4 | commitments | `ReservationShortfall` | `envelope`, `epoch`, `capacity_record_ref`, `reservation_refs`, `affected_commitment_refs`, `reserved_total`, `usable_capacity`, `shortfall`, `allocation_rule_ref`, `disposition_refs`, `status`, `domain_authority_ref` |
| 5 | commitments | `CongestionRecord` | `envelope`, `capacity_locus_ref`, `epoch`, `requested_load`, `admitted_load`, `completed_flow`, `usable_capacity`, `opening_queue`, `closing_queue`, `binding_rule_ref`, `effect_kinds`, `effect_refs`, `queue_record_ref`, `status`, `domain_authority_ref` |
| 6 | dynamic | `DelayRecord` | `envelope`, `subject_ref`, `dispatch_epoch`, `arrival_epoch`, `base_delay`, `queue_delay`, `processing_delay`, `failure_delay`, `total_delay`, `decomposition_kind`, `cause_annotation_refs`, `event_convention_ref`, `numerical_policy_ref`, `domain_authority_ref` |
| 7 | dynamic | `InTransitRecord` | `envelope`, `payload_ref`, `originating_action_ref`, `route_plan_ref`, `completed_segment_refs`, `unfinished_suffix_refs`, `dispatch_epoch`, `expected_arrival_epoch`, `current_locus_ref`, `quantity`, `status`, `topology_snapshot_ref`, `delay_record_ref`, `completion_or_loss_ref`, `provenance_ref` |
| 8 | dynamic | `DelayedEffect` | `envelope`, `originating_action_ref`, `effect_kind_ref`, `due_epoch`, `payload_or_transformation_ref`, `destination_coordinate_ref`, `status`, `represented_in_state_ref`, `maturity_record_ref`, `cancellation_rule_ref`, `failure_consequence_ref`, `measurement_obligation_ref`, `provenance_ref`, `causal_identification_protocol_ref` |
| 9 | dynamic | `DynamicUpdateRecord` | `envelope`, `epoch`, `phase_ordinal`, `predecessor_state_ref`, `successor_state_ref`, `x_update_refs`, `g_update_refs`, `q_update_refs`, `c_update_refs`, `ell_update_refs`, `matured_effect_refs`, `topology_change_refs`, `admission_decision_refs`, `queue_record_refs`, `reservation_shortfall_refs`, `congestion_record_refs`, `delay_record_refs`, `in_transit_record_refs`, `delayed_effect_refs`, `policy_memory_before_ref`, `policy_memory_after_ref`, `policy_decision_ref`, `augmented_replay_state_ref`, `commitment_snapshot_before_ref`, `commitment_snapshot_after_ref`, `ownership_ref`, `physical_commit_ref`, `status` |
| 10 | dynamic | `NaturalDriveContract` | `envelope`, `epoch`, `phase_ordinal`, `model_ref`, `predecessor_state_ref`, `exogenous_input_refs`, `typed_balance_term_refs`, `proposed_update_ref`, `ownership_ref`, `numerical_policy_ref`, `domain_authority_ref`, `semantics_status` |

Every record is a frozen slotted keyword-only dataclass with exact field order and exact runtime types. Its leading `CommonObjectEnvelope` is excluded from `to_ecj1`; accepted `ebu.object-content.v1` over the complete payload is the only identity mechanism. Field rules, applicability arms, collection ordering, ECJ-1 projection, failure precedence, and constructor signatures are exact in `unified_python_research_framework_i7_contract.json`. No alternative or prose-only schema is authorized.

The first five records belong to accepted network/commitment declaration owners. The last five belong to the new dynamic module. The five accepted `SystemState` payload roles remain physical x, topology g, queue/transit q, commitments c, and delayed effects ell; policy memory remains outside physical state.

## Two public callables and private T3 boundary

| Callable | Class | Exact signature | I-7 success |
|---|---|---|---|
| `validate_dynamic_static_identity` | T2 | `(fixture_case: CanonicalBytes, capability: T2FixtureCapability, /) -> None` | six isolated cases |
| `propose_reroute` | T3 | `(route: RoutePlan, topology_change: TopologyChangeEvent, transit: InTransitRecord, proposed_unfinished_suffix_refs: tuple[ObjectRef, ...], permit: _DynamicExecutionPermit, /) -> RoutePlan` | none; fail closed |

`validate_dynamic_static_identity` consumes one exact one-use `T2FixtureCapability`, checks one DC1-DC6 fixture object, returns `None`, and cannot return a state or chainable scientific value. The future allowlist preserves all 36 accepted I-6 rows and appends exactly six I-7 rows for one interface and one frozen fixture hash.

`propose_reroute` is a T3-shaped future integration point, not an available operation. A private `_DynamicExecutionPermit` has no successful construction path and no issuer. Direct construction deterministically refuses with `CAPABILITY_ESCALATION_FORBIDDEN`. `execution._dynamic_execution_permit` validates accepted I-5 lease/guard shape and then raises `REAL_DURABILITY_BACKEND_UNAVAILABLE` at FailureStage I-7 before permit issuance. Independently, `_validate_route_guard` rejects `PROVISIONAL_PART_VII`. A successful I-7 live reroute return is therefore an authority violation.

## Dynamic identities and ten-phase ownership

The exact static identities are:

1. usable capacity: U = alpha times installed capacity, with 0 <= alpha <= 1;
2. physical compliance: 0 <= completed flow <= usable capacity;
3. admission: presented = admitted + rejected + pending outside;
4. queue: closing = opening + admitted - completed - expired/cancelled/abandoned;
5. reservation shortfall: max(0, reserved - usable), strictly positive in a shortfall record;
6. additive delay only under a frozen nonoverlap convention; otherwise components are absent and causes are annotations;
7. arrival epoch = dispatch epoch + total delay; and
8. every update reference belongs to one of x, g, q, c, ell and one physical owner phase.

Rejected and still-pending requests never enter the admitted queue. Pending delayed effects and in-transit payloads are nonzero states, not absence. Completed segments, incurred losses, delays, resource use, and commitments cannot be rewritten by a suffix proposal.

| Phase | I-7 responsibility |
|---|---|
| 1 | mature due delayed effects and arrivals exactly once |
| 2 | apply declared exogenous topology/failure/repair/capacity changes exactly once |
| 3 | record permitted information; physical update forbidden |
| 4 | propose starts/stops/reservations/releases/routes/reroutes; no mutation |
| 5 | screen prerequisites/deadlines/commitments/safety/topology/capacity; no mutation |
| 6 | form admission partition and queue decision; rejected/pending outside |
| 7 | use accepted I-6 grouping/proposal; no mutation |
| 8 | validate ownership and commit each physical effect exactly once |
| 9 | register transit/effects and update commitment/reservation/status without replaying phase 8 |
| 10 | propose declared natural drive for remainder only |

Natural drive is a domain-declared proposal at phase 10 only. No I-7 record evaluates a model. Phase 8 owns each committed physical effect exactly once; phase 9 registers transit/effects and updates obligation status without reapplying phase-8 physics.

## Failure suffix and FailureIds

The accepted 232-member `FailureCode` order is immutable. Exactly 24 members append at ordinals 233-256:

| Ordinal | FailureCode | Exact meaning |
|---|---|---|
| 233 | `I7_RECORD_FORMATION_INVALID` | An I-7 record or callable has missing, extra, misordered, wrongly typed, nonexact, noncanonical, or inapplicable fields before semantic checks. |
| 234 | `DYNAMIC_STATE_INCOMPLETE` | The x,g,q,c,ell component contract or required typed balance/update evidence is incomplete. |
| 235 | `TOPOLOGY_LAYER_CONFLATION` | Structural declaration, active state, or observed topology roles are collapsed or mislabeled. |
| 236 | `TOPOLOGY_PROVENANCE_INVALID` | An observed topology/change lacks exact observation provenance or a declared change improperly supplies observed provenance. |
| 237 | `DOMAIN_DYNAMIC_AUTHORITY_MISSING` | A well-formed topology, route, capacity, queue, policy, delay, admissibility, or numerical declaration lacks its domain/provider authority ref. Under the required `ObjectRef` constructor surface and closed materialization language, omission is structurally blocked earlier by `I7_RECORD_FORMATION_INVALID`; this suffix is retained in order as an owner-precondition label and has no claimed dynamic exact-owner witness. |
| 238 | `AVAILABILITY_TRANSITION_INVALID` | The availability before/after pair is outside the frozen transition table or lacks required repair/failure evidence. |
| 239 | `CAPACITY_IDENTITY_FAILURE` | Usable capacity is not the exact accepted-policy product of installed capacity and availability factor. |
| 240 | `CAPACITY_COMPLIANCE_FAILURE` | Reserved, admitted, or completed physical flow exceeds the applicable usable capacity or a quantity is negative. |
| 241 | `ADMISSION_BALANCE_FAILURE` | Presented demand does not equal admitted plus rejected plus pending demand or disposition disagrees with the partition. |
| 242 | `QUEUE_BALANCE_FAILURE` | The admitted-queue identity does not close in one exact quantity context. |
| 243 | `REJECTED_DEMAND_QUEUE_MUTATION` | Rejected or still-pending outside demand is subtracted from or inserted into the admitted queue. |
| 244 | `RESERVATION_SHORTFALL_INVALID` | The claimed positive shortfall is not max(0,reserved-usable), or a nonpositive gap is represented as shortfall. |
| 245 | `CONGESTION_DECLARATION_INVALID` | No binding rule/effect supports the congestion claim or high utilization is mislabeled congestion. |
| 246 | `DELAY_DECOMPOSITION_INVALID` | Delay clocks, arrival arithmetic, nonoverlap declaration, additive total, or total-only applicability is invalid. |
| 247 | `IN_TRANSIT_STATE_INVALID` | Dispatch/arrival ordering, status arm, quantity, route partition, or completion/loss evidence is inconsistent. |
| 248 | `DELAYED_EFFECT_STATUS_INVALID` | The matured, pending, cancelled, failed, or unresolved status arm has inconsistent evidence or treats pending as zero/absence. |
| 249 | `UPDATE_DOUBLE_APPLICATION_FORBIDDEN` | One physical effect/ref is assigned to multiple components/phases or accounting attempts to reapply it. |
| 250 | `NATURAL_DRIVE_PHASE_INVALID` | Natural drive is proposed outside phase 10 or duplicates an earlier phase effect. |
| 251 | `POLICY_MEMORY_PAIR_MISMATCH` | The stateful before/after/decision/augmented replay tuple is incomplete, or stateless use supplies one of those refs. |
| 252 | `COMMITMENT_STATE_MISMATCH` | Commitment/reservation before/after or shortfall links are incomplete or inconsistent. |
| 253 | `ROUTE_SEMANTICS_UNRESOLVED` | A live route-dependent or rerouting claim is attempted while RouteSemanticsStatus remains PROVISIONAL_PART_VII. |
| 254 | `COMPLETED_ROUTE_REWRITE_FORBIDDEN` | A reroute attempts to replace, erase, reorder, or reinterpret a completed segment/history. |
| 255 | `DYNAMIC_NUMERICAL_POLICY_UNACCEPTED` | Exact arithmetic is unavailable and the required domain numerical policy is absent, unaccepted, or used outside its declared operation. Under required `numerical_policy_ref: ObjectRef`, exact reference equality, and no resolution/acceptance registry, omission is structurally blocked earlier by `I7_RECORD_FORMATION_INVALID`; this suffix is retained in order as an owner-precondition label and has no claimed dynamic exact-owner witness. |
| 256 | `DYNAMIC_STATIC_IDENTITY_MISMATCH` | One allowlisted closed static case does not equal its exact frozen expected arithmetic/status projection. |

The validation contract assigns every negative dynamic vector to its exact constructor/callable/private-interface owner. Each isolated I-7 coordinate freezes stage I-7, full `FailureInterfaceRef`, interface version 1.0.0, empty ordered object refs, event key NOT_APPLICABLE, ordinal 0, exact binary preimage hex/size/hash, and derived `FailureId`. There are 36 distinct stored coordinates and 44 negative assignments. Representative-interface substitution is forbidden; distinct-coordinate byte/ID collisions require refusal. Required-field deletions in `I7V-029`, `I7V-033`, `I7V-043`, `I7V-050`, `I7V-056`, and `I7V-068` are exact constructor attempts that fail first as `I7_RECORD_FORMATION_INVALID`; in particular, `I7V-029` no longer claims the unreachable later domain-authority predicate.

## Closed validation vectors

The closed contract contains 100 vectors: 70 materializable exact-owner invocations and 30 explicit static witnesses. Dynamic outcomes are {'FAIL_CLOSED': 44, 'SUCCESS': 26}; the 44 negative assignments use 25 dynamically reachable failure codes, while the retained structurally unreachable suffixes above have only explicit static owner-precondition witnesses. The 30 static rows freeze their individual expected witnesses; completed checks total 314. Every vector has zero model, policy, state-advance, scientific-result, durable-write, and successful-reroute counters.

The validation contract freezes an exact 13-row feature-coverage map for capacity, topology/availability, admission, queue, congestion, shortfall, delay, in-transit state, route refusal/reroute guard, delayed effects, policy-memory/commitment pairing, capability, and prohibited reachability. Every row names its authorized positive or required-refusal vectors, negative vectors, and independent static witnesses. A route “positive” is a successful refusal check, never a successful live reroute.

Positive and negative coverage includes capacity, topology status/provenance, admission, queue, congestion, reservation shortfall, delay, in-transit, route refusal and completed-suffix preservation, delayed effects, policy-memory/commitment pairing, capability issuance/consumption, ten-phase ownership, and prohibited reachability. Five multiple-active witnesses prove precedence reachability on one effective input. Every dynamic vector constructs support first and calls its exact owner once; every static vector names a source, AST, JSON pointer, arithmetic, Git, or nonclaim witness. `I7V-059` calls the exact private `_DynamicExecutionPermit` refusal constructor; `I7V-065` and `I7V-066` call the exact `_issue_t2_fixture_capability` owner for wrong-hash and unallowlisted-pair refusal rather than substituting the later validator.

The materialization/precedence audit independently covers all 70 dynamic vectors and all 30 static witnesses. It searches required-field deletion, missing/extra fields, wrong types, malformed closed-domain values, invalid support construction, constructor failure masked as later semantics, inverted precedence, representative-owner substitution, missing baseline/catalogue expansion, and unreachable outcome. Ten dynamic rows required mechanical correction (`I7V-029`, `I7V-033`, `I7V-043`, `I7V-050`, `I7V-056`, `I7V-058`, `I7V-059`, `I7V-065`, `I7V-066`, and `I7V-068`); the other 60 dynamic rows retain their meanings. `I7V-058` now records `ROUTE_SEMANTICS_UNRESOLVED` as active but shadowed behind the unchanged first failure `COMPLETED_ROUTE_REWRITE_FORBIDDEN`, matching the identical route-guard state exercised by the explicit precedence witness. Static witnesses `I7S-022` and `I7S-029` now state the corresponding unreachable-owner boundaries explicitly. No new scientific or normative design choice was required.

The six future fixture cases preserve the Dynamic Foundation arithmetic exactly. DC4 is counterfactual alternate-path arithmetic plus a mandatory live refusal; it is not route science. The fixture is canonical compact JSON plus LF, 2244 bytes, raw SHA-256 cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d.

Authority-drafting validation now checks only documents and Git objects. It does not import `ebu_framework`, execute prospective vectors, materialize the future fixture, or run project tests.

## Implementation path and exact patches

The future closed path boundary contains 20 paths: 4 new, 6 production modifications, and 10 compatibility-only test modifications.

| State | Path | Owner | Purpose |
|---|---|---|---|
| MODIFIED | `src/ebu_framework/__init__.py` | ROOT_EXPORT_SUFFIX_OWNER | Eagerly import the five deferred records and seven dynamic names; append exact 12-name suffix after accepted 407-name prefix. |
| MODIFIED | `src/ebu_framework/capabilities.py` | DYNAMIC_T2_CAPABILITY_EXTENSION | Append exactly six DC1-DC6 allowlist rows for validate_dynamic_static_identity and route their fail-fast owner coordinates to FailureStage.I7; preserve all 36 I-6 rows and I-4 behavior. |
| MODIFIED | `src/ebu_framework/commitments.py` | COMMITMENT_DYNAMIC_DECLARATION_OWNER | Append AdmissionDecision, QueueRecord, ReservationShortfall, CongestionRecord and exact private validators; preserve accepted commitment/reservation/capacity behavior. |
| NEW | `src/ebu_framework/dynamic.py` | DYNAMIC_MODULE_OWNER | Create exact ten-phase dynamic declarations, private validators/permit consumer/route guard, one T2 callable, and one fail-closed T3 callable with the frozen imports/exports/signatures. |
| MODIFIED | `src/ebu_framework/errors.py` | FAILURE_SUFFIX_OWNER | Append exactly 24 FailureCode members at ordinals 233-256; preserve the accepted 232-code prefix and all other error bytes/exports. |
| MODIFIED | `src/ebu_framework/execution.py` | T3_DYNAMIC_PERMIT_NORETURN_GUARD_OWNER | Append only dynamic import and _dynamic_execution_permit; accepted lease/guard checks then deterministic FailureStage.I7 REAL_DURABILITY_BACKEND_UNAVAILABLE; no permit construction. |
| MODIFIED | `src/ebu_framework/network.py` | NETWORK_DYNAMIC_DECLARATION_OWNER | Append ISOLATED to AvailabilityStatus and add TopologyChangeEvent plus its exact private validator; preserve every accepted declaration, validator, import edge, and export prefix. |
| NEW | `tests/framework/fixtures/dynamic_static_v1.json` | DYNAMIC_STATIC_FIXTURE_OWNER | Materialize exactly the canonical compact JSON plus LF bytes frozen in the validation contract. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_atomic_declarations.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_bridge_exact_fixtures.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_capabilities.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| NEW | `tests/framework/test_dynamic_static_identities.py` | DYNAMIC_T2_TEST_OWNER | Implement exact one-at-a-time DC1-DC6 T2 cases and negative controls; never import execution or return/reuse SystemState. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_i3_integration.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_i3a_declarations.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_i3b_declarations.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_i3c_declarations.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_i3d_declarations.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_interaction_declarations.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| COMPATIBILITY_ONLY_MODIFIED | `tests/framework/test_primitives_envelopes.py` | ADDITIVE_INVENTORY_RECONCILIATION | Reconcile only exact append-only failure/root/module/import/T2 inventories made stale by I-7; no accepted behavior changes. |
| NEW | `tests/framework/test_route_guards.py` | ROUTE_GUARD_TEST_OWNER | Implement T0 route-refusal and suffix-preservation checks; never invoke or import execution. |

The implementation-path manifest freezes 12 ordered construction patches. Each patch has an exact operation, anchor, symbol/field/signature/export/import/vector payload, and an empty variants array. Implementation must apply those patches in ID order. No prose substitution, alternate schema, helper export, extra import, extra failure, extra availability arm, fixture rewrite, or incidental test churn is allowed.

The future package graph has 36 modules, 221 direct edges, and zero cycles. `dynamic` never imports `execution`; `execution` appends the one directional dynamic edge. T0/T2 validation imports neither execution nor historical runners.

## Exact projections

| Projection | Bytes/items | SHA-256 |
|---|---|---|
| accepted root LF | 9053 | 8d23ebd11805d6324e0f926ebf487972def9d154b26edf333e8d080177033192 |
| future root LF | 9273 | 492a02780bace0ca64a3bbe4e7444c4709113ed7081557ad784cf38a7601ba98 |
| accepted FailureCode LF | 6105 | e3e5949ad4e603450c254a07a3b506dcfd14becade95b3be4b2f6fd2a93ca9b5 |
| future FailureCode LF | 6802 | 4e969462f499ef25e0ff32f3502154483c8d1604fcbc8f3650c5c5d95d1247ba |
| public type rows | 18020 | 7e309fe4567e96bc5614b147fb0956883eb4a32843f9b6c46be4f8d4c15f168c |
| public callable rows | 882 | b21fcd0be903b50f4e26d5a409824ae6ed96b254a9ed8efc980ede4cccc01243 |
| failure coordinates | 22358 | 0264a2d5a2b29d88349625e9c261fffbb2e765fad9f228553547a7972a5f29e0 |
| validation vectors | 34898 | d5e2998c82e0700e19f3adcbfc38eb9c093a08d5f855a67836b5dfca02b23dc2 |
| future fixture | 2244 | cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d |
| predecessor path LF | 11245 | a82882f6a13f0b3115d2c9f58b88257ed69c0bf29bae4d56f71776087abf595d |
| predecessor identity rows | 50308 | 57b970ca8b12b131d97a7a24f6f7c404660ac8935a57aca7f6f76fa14a47ec21 |
| future import graph | 2974 | a4dc03e376f61ba1587690561e94ee55e3587aa7cf5e47e1c9fddb3d64e32f28 |

The predecessor manifest contains 303 exact base-tree rows and 123375584 raw payload bytes. Git-tree/cat-file reconstruction and independent archive/filesystem reconstruction must agree on every path, mode, Git object, byte count, and raw SHA-256.

## Teaching traceability

The feature record below keeps capability and project value prominent while putting each limit immediately beside the claim.

### 1. Five-part dynamic state

| Teaching element | Frozen content |
|---|---|
| Meaning | Keep physical x, active topology g, admitted queue/transit q, commitments c, and delayed effects ell distinct. |
| Why it matters | A missing or merged component can make two apparently equal snapshots have different successors. |
| What it enables | Auditable one-step state sufficiency claims and exact ownership. |
| Assumptions | fixed declared schema; complete exogenous inputs; no hidden physical memory |
| Exact math/proof | Z_k=(x_k,g_k,q_k,c_k,ell_k); DynamicUpdateRecord requires five disjoint update collections. |
| Ordinary-life example | A delivery van, the road closure, waiting orders, promised deadlines, and a later refund are different facts. |
| Falsifier/refusal | If equal Z_k values under equal inputs can yield different successors, refuse and expand state prospectively. |
| Claim class | prospective architecture; conditional sufficiency only |
| Positive project value | Prevents silent history loss while giving later models a shared auditable state spine. |

### 2. Declared active topology with provenance

| Teaching element | Frozen content |
|---|---|
| Meaning | Structural topology, active topology, and observed topology remain separate typed roles. |
| Why it matters | A declared possible edge is not proof it is active or measured. |
| What it enables | Time-indexed failures, repairs, isolation, and membership histories without topology discovery. |
| Assumptions | domain/provider supplies relations; stable object identifiers |
| Exact math/proof | TopologyChangeEvent binds structural_topology_ref plus active before/after refs and a declared/observed provenance arm. |
| Ordinary-life example | A road on a map, a road currently open, and a traffic-camera observation are related but not identical. |
| Falsifier/refusal | Deleting the required authority ObjectRef fails first as I7_RECORD_FORMATION_INVALID; a well-formed semantic absence has only static owner-precondition coverage, while invalid provenance or layer conflation still fails closed at the exact owner. |
| Claim class | prospective architecture |
| Positive project value | Makes changing connectivity inspectable without pretending EBU inferred hidden edges. |

### 3. ISOLATED availability

| Teaching element | Frozen content |
|---|---|
| Meaning | Append one exact active-status arm for a provider/node/edge that exists structurally but is disconnected for the declared active scope. |
| Why it matters | Failure, repair, degradation, and isolation have different operational consequences. |
| What it enables | Retention of stable identity and commitments while new dispatch is refused. |
| Assumptions | declared scope; declared transition evidence |
| Exact math/proof | AvailabilityStatus accepted prefix plus exact suffix ISOLATED; no other arm changes. |
| Ordinary-life example | A staffed clinic may exist and be functional yet be unreachable after a bridge closure. |
| Falsifier/refusal | An inferred hidden cut or unsupported transition fails AVAILABILITY_TRANSITION_INVALID. |
| Claim class | institutional schema choice |
| Positive project value | Avoids erasing temporarily disconnected assets from history. |

### 4. Capacity identity and compliance

| Teaching element | Frozen content |
|---|---|
| Meaning | Installed capacity, availability factor, usable capacity, reserved load, admitted load, and completed flow remain distinct. |
| Why it matters | Counting reservation as flow or ignoring derating can invent service. |
| What it enables | Exact static capacity screens and explicit shortfalls. |
| Assumptions | compatible units; accepted domain numerical policy; declared availability factor |
| Exact math/proof | U=alpha times Ubar and 0<=sum f_i<=U, checked exactly in T2 fixtures. |
| Ordinary-life example | A six-seat shuttle with one seat unavailable has five usable seats, not six. |
| Falsifier/refusal | Product mismatch or flow above usable capacity fails closed. |
| Claim class | identity under declarations |
| Positive project value | Gives admission and congestion records a common physical ceiling. |

### 5. Admission partition

| Teaching element | Frozen content |
|---|---|
| Meaning | Every presented request is admitted, rejected, or left pending outside the queue exactly once. |
| Why it matters | Rejected work must not silently inflate or reduce a queue. |
| What it enables | Comparable admission histories and later policy audit. |
| Assumptions | one compatible quantity context; frozen allocation rule |
| Exact math/proof | b=a+j+d. |
| Ordinary-life example | At a restaurant, guests may be seated, turned away, or asked to wait before joining the seated queue. |
| Falsifier/refusal | Any nonclosing partition or disposition mismatch fails ADMISSION_BALANCE_FAILURE. |
| Claim class | algebraic identity |
| Positive project value | Separates capacity decisions from subsequent service mechanics. |

### 6. Queue and congestion

| Teaching element | Frozen content |
|---|---|
| Meaning | Queue holds admitted but unserved demand; congestion additionally requires a binding rule and an observed/declared effect. |
| Why it matters | High utilization alone is not congestion, and rejected requests are not backlog. |
| What it enables | Exact backlog accounting and testable delay/loss/feasibility effects. |
| Assumptions | lossless single-class fixture unless extra typed terms are declared; frozen queue discipline |
| Exact math/proof | q_{k+1}=q_k+a_k-f_k-z_k, while j_k and d_k remain outside. |
| Ordinary-life example | Cars admitted onto a ferry lane wait in that lane; cars diverted before entry do not. |
| Falsifier/refusal | Rejected-demand mutation, nonclosing balance, or effect-free congestion fails closed. |
| Claim class | identity plus declared classification |
| Positive project value | Lets later work distinguish scarcity, admission, waiting, and actual congestion. |

### 7. Reservation shortfall and commitment memory

| Teaching element | Frozen content |
|---|---|
| Meaning | A later capacity loss does not erase a previously accepted capacity claim or obligation. |
| Why it matters | Priority rules can allocate pain but cannot remove the physical gap. |
| What it enables | Impaired, breached, reroute-proposed, or unresolved commitment histories. |
| Assumptions | reconciled reservation set; matching quantity context |
| Exact math/proof | shortfall=max(0,R-U), strictly positive for ReservationShortfall. |
| Ordinary-life example | Four booked seats remain four promises even when a vehicle failure leaves only three usable seats. |
| Falsifier/refusal | Wrong arithmetic or missing commitment link fails closed. |
| Claim class | identity plus institutional status |
| Positive project value | Preserves accountability across capacity changes. |

### 8. Delay decomposition

| Teaching element | Frozen content |
|---|---|
| Meaning | Delay is either an exact sum of nonoverlapping declared components or one total with causes kept as annotations. |
| Why it matters | Two causes occupying the same elapsed interval cannot both be added. |
| What it enables | Deterministic dispatch/arrival timing without fabricated causal shares. |
| Assumptions | one clock; frozen event convention; accepted numerical policy |
| Exact math/proof | tau=base+queue+processing+failure only under nonoverlap; arrival=dispatch+tau. |
| Ordinary-life example | A train stopped for one ten-minute interval by both a signal and congestion was delayed ten minutes, not twenty. |
| Falsifier/refusal | Overlap marked additive or total mismatch fails DELAY_DECOMPOSITION_INVALID; deleting required numerical_policy_ref fails earlier as I7_RECORD_FORMATION_INVALID, with DYNAMIC_NUMERICAL_POLICY_UNACCEPTED retained only as a static owner-precondition label under this closed surface. |
| Claim class | conditional identity |
| Positive project value | Makes timing arithmetic reproducible while keeping causal claims modest. |

### 9. In-transit state and suffix preservation

| Teaching element | Frozen content |
|---|---|
| Meaning | Dispatched payload remains distinct from arrived, stranded, and lost payload; completed route history is immutable. |
| Why it matters | A path change cannot rewrite already incurred delay, loss, or resource use. |
| What it enables | Auditable handoff and future rerouting once route authority exists. |
| Assumptions | declared route plan; ordered segment history |
| Exact math/proof | completed segments and unfinished suffix are disjoint; arrival is not before dispatch. |
| Ordinary-life example | A parcel past depot A but blocked before depot B cannot be rerouted as if depot A never handled it. |
| Falsifier/refusal | Segment overlap, impossible timing, or inconsistent status fails closed. |
| Claim class | prospective architecture |
| Positive project value | Prevents retrospective route-history editing. |

### 10. Delayed effects

| Teaching element | Frozen content |
|---|---|
| Meaning | Every later effect is matured, pending, cancelled, failed, or unresolved with exact evidence. |
| Why it matters | Pending and unknown consequences are not zero. |
| What it enables | Honest finite-horizon comparisons and later correction governance. |
| Assumptions | declared due epoch; stable provenance |
| Exact math/proof | The status arms are mutually exclusive and collectively exhaustive for the record. |
| Ordinary-life example | A rebate due next month is still pending at this month's close; it has not disappeared. |
| Falsifier/refusal | Wrong status/evidence arm or causal claim without protocol fails closed. |
| Claim class | prospective architecture |
| Positive project value | Keeps obligations and future physical consequences visible. |

### 11. Rerouting refusal

| Teaching element | Frozen content |
|---|---|
| Meaning | I-7 names a live proposal interface but supplies no permit and retains PROVISIONAL_PART_VII semantics. |
| Why it matters | A graph path is not yet an authorized physical route law. |
| What it enables | A stable future integration point without allowing premature route science. |
| Assumptions | accepted I-5 lease boundary; future Part VII authority needed |
| Exact math/proof | No valid _DynamicExecutionPermit exists and _validate_route_guard rejects PROVISIONAL_PART_VII; successful return count is zero. |
| Ordinary-life example | Software can record that a detour is needed without claiming the detour is safe, legal, or passable. |
| Falsifier/refusal | Any I-7 live successful RoutePlan return is an authority violation; the exact dynamic refusal witness is direct _DynamicExecutionPermit construction, not a fabricated propose_reroute invocation. |
| Claim class | fail-closed architecture |
| Positive project value | Makes future routing extensible without weakening current scientific controls. |

### 12. Policy-memory pairing

| Teaching element | Frozen content |
|---|---|
| Meaning | Physical state remains separate from policy memory, while stateful replay binds before memory, decision, after memory, and augmented replay state together. |
| Why it matters | Hidden controller history can otherwise make replay nondeterministic. |
| What it enables | Auditable closed-loop reconstruction without calling a policy in static validation. |
| Assumptions | single declared memory lineage; accepted I-3/I-5 memory semantics |
| Exact math/proof | All four stateful refs are present together or all are NOT_APPLICABLE. |
| Ordinary-life example | A thermostat's current temperature and its learned schedule are separate, but replay needs both. |
| Falsifier/refusal | A partial tuple fails POLICY_MEMORY_PAIR_MISMATCH. |
| Claim class | accepted architecture extended prospectively |
| Positive project value | Preserves deterministic replay boundaries for future closed-loop studies. |

### 13. Ten-phase no-double-application

| Teaching element | Frozen content |
|---|---|
| Meaning | Each effect is proposed, screened, committed, registered, or naturally driven at its one owning phase. |
| Why it matters | Accounting must mirror a physical update, not perform it again. |
| What it enables | Traceable within-epoch ordering and phase-level audit. |
| Assumptions | accepted I-5 EventKey and ownership; disjoint refs |
| Exact math/proof | DynamicUpdateRecord partitions refs across x,g,q,c,ell and rejects cross-component or phase-8/phase-9 duplicates. |
| Ordinary-life example | Charging a card and writing the receipt are two records of one payment, not two payments. |
| Falsifier/refusal | Any ref owned twice fails UPDATE_DOUBLE_APPLICATION_FORBIDDEN. |
| Claim class | accepted architecture with I-7 mapping |
| Positive project value | Reduces silent double-counting across complex dynamic events. |

### 14. T2 static fixtures and T3 control

| Teaching element | Frozen content |
|---|---|
| Meaning | Six hand-derived cases run one at a time under exact one-use capabilities; live science remains T3 and unavailable. |
| Why it matters | Arithmetic checks should not become a disguised trajectory or policy experiment. |
| What it enables | Early deterministic validation of basic identities and refusals. |
| Assumptions | exact frozen bytes; no successor chaining; no SystemState return |
| Exact math/proof | The allowlist has exactly six I-7 rows and one interface; each capability is consumed once. |
| Ordinary-life example | Checking six calculator examples is not operating the transport network. |
| Falsifier/refusal | Wrong hash or unallowlisted case/interface fails at the exact _issue_t2_fixture_capability owner; reuse fails at the exact validator, and direct private-permit construction proves T3 refusal. |
| Claim class | validation architecture |
| Positive project value | Builds confidence in mechanics without spending scientific authority. |

### 15. Domain responsibility and noninference

| Teaching element | Frozen content |
|---|---|
| Meaning | Domains/providers declare or measure topology, dependency, route, capacity, delay, policy, and admissibility; EBU represents and validates. |
| Why it matters | Generic data cannot establish hidden edges, best policy, causality, or entitlement. |
| What it enables | Reusable typed records across domains without a universal optimizer. |
| Assumptions | external domain authority; explicit provenance |
| Exact math/proof | Every relevant record carries domain_authority_ref or declaring_authority_ref; no discover/best/infer callable exists. |
| Ordinary-life example | A hospital declares which ambulance routes and capacities are valid; the ledger checks the declaration instead of inventing roads. |
| Falsifier/refusal | Deleting a required authority field fails I7_RECORD_FORMATION_INVALID before semantics. DOMAIN_DYNAMIC_AUTHORITY_MISSING is retained honestly as a static owner-precondition label because the closed surface has no typed missing-authority value or runtime resolver; inferred hidden relations remain forbidden. |
| Claim class | accepted architecture |
| Positive project value | Keeps the framework broadly useful without overclaiming scientific expertise. |

## Nonclaims and later stages

This package does not solve arbitrary 2^N evaluation; infer or optimize any topology, route, hidden edge, policy, queue discipline, priority, delay law, motif, poset, or hypergraph; establish a Part VII route law; or claim wave, physical phase, superposition, interference, electrical voltage, scaling, recurrence, fractal, Fibonacci, synchronization, or collective benefit.

It makes no dynamic exact-owner reachability claim for `DOMAIN_DYNAMIC_AUTHORITY_MISSING` or `DYNAMIC_NUMERICAL_POLICY_UNACCEPTED` under the required `ObjectRef` declaration surface and closed materialization language; those suffixes have static owner-precondition evidence, while required-field omission is `I7_RECORD_FORMATION_INVALID`. It makes no dynamic exact `propose_reroute` invocation claim: the private permit is unissuable and exact refusal coverage is direct `_DynamicExecutionPermit` construction.

It does not attribute causality without a separate accepted protocol. It does not equate settlement with measurement or causal contribution and authorizes no settlement operation. It does not finalize, recover, correct, publish, or audit an I-8/I-9 result. It does not execute a model, policy, state transition, simulation, trajectory, benchmark, Gate, runner, finalizer, renderer, manuscript, or book.

The next possible stage is an independent audit of exactly these five authority files. That audit, implementation, implementation audit, integration, scientific execution, interpretation, publication, commit, and push have not begun.

READY_FOR_INDEPENDENT_FRAMEWORK_I7_DYNAMIC_COORDINATION_AUTHORITY_AUDIT
