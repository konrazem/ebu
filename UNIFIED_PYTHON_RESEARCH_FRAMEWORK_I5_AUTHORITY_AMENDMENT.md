# Unified Python Research Framework I-5 Authority Amendment

Status: prospective authority candidate only. Framework I-5 is not implemented, executable, accepted, integrated, or published by this package.

## 1. Decision and authority boundary

This amendment freezes the inert deterministic event, physical-update ownership, abstract durability, and trace kernel planned for Framework I-5. It gives a later implementation exact records and static validators for ordering, conflict detection, atomic-group obligations, literal trace prefixes, and a hard boundary between validation and scientific execution. It authorizes only these five authority documents. The implementation plan remains planning input and does not grant implementation permission.

The predecessor is commit `98b9dea874ca57e4ed5f8aaea1584514af0e3823` with tree `112db4b465ac77df52ccbbf655292083579e45a8` on `framework-v0.1`; it contains 273 tracked paths, 185 accepted failure codes, 309 accepted root exports, 29 package modules, 152 package edges, and 155 accepted combined signature rows. The isolated candidate branch is `framework/i-5-event-durability-trace-authority`. HEAD is not advanced.

The JSON contract is the mechanical schema and ordering source. This Markdown file is its normative human rendering. Any disagreement is an integrity failure; neither file may be selected piecemeal.

## 2. Applicable sources and precedence

Repository governance, the repository-local `$ebu-framework` authority-drafting profile, the current framework specification, the current implementation plan, the accepted I-1 through I-4 packages, accepted atomic/D1/D2 declarations, the open-problem register, the dynamic foundation, the sequential-parallel bridge, governance/bootstrap requirements, dependency/compatibility authority, and the future-books structure were reconciled. The implementation plan controls planned surfaces only. Scientific or operational questions remain open unless this amendment expressly freezes the narrow inert I-5 slice.

| Source | Raw bytes | Raw SHA-256 | Role |
|---|---:|---|---|
| `AGENTS.md` | 1853 | `b23e3e26c336fe2db258e735f20e60e291d7f22cf9ee9d5e623d69ba141c002b` | repository governance |
| `.agents/skills/ebu-framework/SKILL.md` | 2977 | `81ab31ce62d58f9058a38aafd511c8f98d7e1142640967bbd3daccd1068e810c` | workflow skill |
| `.agents/skills/ebu-framework/references/profiles.md` | 9791 | `ab8e68b4c53630a9fe25367c8e40f0e51a17030e1428aaf38f0fafcda0eb8a5f` | authority-drafting profile |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md` | 421632 | `713b3ceb694721710ffeca8b9efc7cb1c54317ed922a2ba5e352b01faa8c82fa` | controlling specification |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md` | 251659 | `7dfc8da2b8c31e8b66b867bc7c894f4f6218420391e21c6443c48645c884a336` | controlling planning input |
| `EBU_FUTURE_BOOKS_STRUCTURE.md` | 138686 | `ee0aba306c863b975e4d13bfc33690845c04fa107508400c8401587980530fba` | future-books boundary |
| `DYNAMIC_COORDINATION_FOUNDATION.md` | 71170 | `6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95` | exact ten-phase source |
| `SEQUENTIAL_PARALLEL_BRIDGE.md` | 53003 | `34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10` | joint-group and physical-boundary source |
| `POST_ATOMIC_OPEN_PROBLEM_REGISTER.md` | 27776 | `68aca0614f41dbfad8c248c4d43fd29835234c13dc31536f194f3dc92e6be320` | UQ register |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I1_PACKAGING_AMENDMENT.md` | 45775 | `a27aedf955c1e7bbf7039efc905951f516e070a2f36dc24b23c72d75f6a2f448` | accepted I-1 authority |
| `unified_python_research_framework_packaging_contract.json` | 54712 | `edf2bd33361e7b2b2e083a10535c87e1e1cbbd36d21c2a3f3004f12b1743c351` | accepted I-1 mechanical authority |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3_AUTHORITY_AMENDMENT.md` | 156290 | `eaa3c80efa6ff0beae6f3ad8da3be67fb61f3cc5223b2067c256732ebf7bdfbc` | accepted I-3 authority |
| `unified_python_research_framework_i3_contract.json` | 345638 | `d8acef250314e1405b048a324c9f855010f7927cc8760e2f827bba85253d7979` | accepted I-3 mechanical authority |
| `unified_python_research_framework_i3_validation_contract.json` | 49384569 | `9ecd849f24ecd3e55883874263c10c181fea2e16a3000e87e4fc7fe02c2ccb2b` | accepted I-3 validation authority |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3C_SETTLEMENT_CAUSALITY_REPAIR_AUTHORITY_AMENDMENT.md` | 18759 | `78e5b5e662cce41e2421e7e534309b6c9591436d39eb135f4bb71c72906e483a` | accepted I-3C repair authority |
| `unified_python_research_framework_i3c_settlement_causality_repair_contract.json` | 20877 | `2ffc97f0bd93a219a56e324a806c01b0e48c5b8882b674aa1f67cc3ff0872c93` | accepted I-3C repair contract |
| `ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md` | 41359 | `eb559a68163571d80bbe564d68a57a915e128090b1dbb26bfd9d1c4ec4a7b8d3` | accepted atomic-generator/interaction authority |
| `atomic_generator_foundation_contract.json` | 42855 | `b204f06bd11e7c605acc8afadbf82021fe5e3c1030e1f3f4c3659e71afd5d8a4` | accepted atomic-generator/interaction contract |
| `atomic_generator_foundation_validation_contract.json` | 63776 | `df54297b9c45220f28806304e30f9a654b338165ecd5970a0a2428b8e362a800` | accepted atomic-generator validation |
| `ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md` | 115771 | `80d83942d20745b9edeb3c5c8c05d052a616ef97ac9edb1af494d568acf68669` | accepted D1/D2 declaration authority |
| `atomic_interaction_declaration_contract.json` | 256881 | `565cc3947d9a3abc99ece694ec823ad0f945dbb1c7634586bcf43f2e36c2549a` | accepted D1/D2 contract |
| `atomic_interaction_declaration_validation_contract.json` | 1618558 | `b40b80aef4a67826186fde40bf0b0ee9dec6e3db27c6809c2a2da075abe1b401` | accepted D1/D2 validation |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I4_AUTHORITY_AMENDMENT.md` | 37767 | `9414005a6f6fcfc9868c5094c350b43172c28d8510cac390a89c5c3c95b75365` | accepted I-4 authority |
| `unified_python_research_framework_i4_contract.json` | 86797 | `dcd26f45dd33086acb29bc76710d3a9215a5d3b04878c54f9ec52a5970a6574d` | accepted I-4 mechanical authority |
| `unified_python_research_framework_i4_validation_contract.json` | 324578 | `a662ffee52bd4c9b8f926b23624d8d8fad4b64223e1fa61234f852f1a0c9b9ec` | accepted I-4 validation |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I4_GOVERNANCE_BOOTSTRAP_REQUIREMENTS.md` | 15143 | `9cea9392375623e1b95727f6ff7761735133906011f63a260831ee7656133f9f` | governance/bootstrap boundary |
| `UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I4_UQ25_DEPENDENCY_DECISION.md` | 11721 | `863f0179da8db043ad98f5025cd99a0e09ccf5914f287ff2b45fcfb1730d372f` | accepted dependency decision |
| `unified_python_research_framework_i4_uq25_dependency_contract.json` | 32485 | `55b9a146927e0c37488dbf8489fc3d3d9afc05e8fc52bd7c402189fd5d598338` | accepted dependency contract |
| `post_i4_legacy_test_compatibility_contract.json` | 102133 | `347f2fc9cd44bab3c1bfa1ae6b8b6da8c544ef13f1e41494d05b4bfffea2aa82` | accepted compatibility surface |
| `post_i4_legacy_test_compatibility_validation_contract.json` | 67952 | `fcb9c9bb2a42902dec60abe8dcfb2a9d0366f15d794262e56a142072b984c5a1` | accepted compatibility validation |

### 2.1 Explicit planning reconciliation

- **Issue:** The controlling ten-phase sources freeze ordinals and full prose but do not assign semantic enum labels. **Resolution:** PhaseOrdinal members are neutral PHASE_1 through PHASE_10 only; /ten_phase_order.normative_text is the exact accepted name/meaning and cannot be shortened or replaced. **Scope:** Nomenclature only; no phase content or order changes.
- **Issue:** Canonical trace row, prefix, and payload hash domains and callables already exist in the accepted I-1 surface. **Resolution:** I-5 reuses compute_canonical_trace_row_hash, compute_canonical_trace_prefix_hash, and compute_canonical_trace_payload_hash byte-identically. TraceDigest is only a closed alias of their accepted result wrappers. **Scope:** No accepted domain, preimage, callable, result type, or export is duplicated or redefined.
- **Issue:** Plan §10.2 names the compact all-stage I-5 public families, while this task requires exact typed sub-outcomes, reconstruction evidence, T3 guards, and inert fault-hook declarations. **Resolution:** Every plan-named event, ownership, durability, and trace type is retained exactly; supplementary I-5 public records/enums make the task-required distinctions explicit. This amendment prospectively narrows only the I-5 catalogue and does not alter accepted I-1 through I-4 exports. **Scope:** Representational I-5 additions only; no scientific or backend decision.
- **Issue:** Plan §10.2 lists ScientificExecutionLease under capabilities, but the task-authorized I-5 path table assigns T3 entry/lease responsibility to new execution.py and does not authorize capabilities.py modification. **Resolution:** ScientificExecutionLease is declared by execution.py for I-5; capabilities.py remains byte-identical and supplies only the already accepted capability prerequisites. **Scope:** Narrow prospective I-5 ownership resolution; no lease is constructible under I-5.
- **Issue:** The plan names CommitOutcome while the task requires separate requested, committed, rejected, ambiguous, and unavailable evidence forms. **Resolution:** CommitOutcome is the exact five-member enum; AtomicCommitOutcome is its closed concrete evidence union, with DurablePrefixEvidence representing committed prefix evidence and separate inert failure evidence records. **Scope:** Typed abstract classification only; zero accepted stores.

## 3. What I-5 establishes

I-5 establishes deterministic serialization of already-declared events, explicit epoch-wide ownership of opaque physical loci, deterministic rejection of duplicate/conflicting updates, a precise abstract atomicity obligation, reconstructable inert history, literal immutable-prefix evidence, and fail-closed T3 guards. These are bookkeeping and safety mechanics. They do not choose or evaluate scientific transformations, policies, worlds, schedules, routes, stochastic processes, or outcomes.

All inputs and outputs are immutable. Exact tuples are never inferred from sets or mappings. No result may depend on a clock, randomness, process identity, filesystem ordering, hash iteration, a network, a provider loader, a callback, or hidden state. Rejection has zero effect on state, policy memory, ownership, evidence, or trace bytes.

## 4. Accepted ten-phase order

The names below are machine labels for the controlling prose; the prose and ordinals are unchanged. Reordering is not an I-5 option.

| Ordinal | Machine name | Controlling meaning |
|---:|---|---|
| 1 | `PHASE_1` | Mature delayed effects and arrivals due at the start of epoch k. |
| 2 | `PHASE_2` | Apply declared exogenous topology changes, failures, repairs, and capacity deratings effective at k. |
| 3 | `PHASE_3` | Record the resulting state and make the permitted measurement available to the policy. |
| 4 | `PHASE_4` | Propose starts, stops, reservations, releases, routes, and reroutes using only permitted information. |
| 5 | `PHASE_5` | Screen prerequisites, deadlines, commitments, safety constraints, topology, and capacity. |
| 6 | `PHASE_6` | Admit, reject, defer, or partially accept requests using the frozen allocation and queue disciplines. |
| 7 | `PHASE_7` | Build joint-transition groups using the imported Part VI rule and form the exact joint-transition proposal for every accepted group without yet mutating physical state. |
| 8 | `PHASE_8` | Validate a disjoint update-ownership record, then commit each proposed physical transition, completed flow, conversion, loss, consumption, congestion effect, expiry, resource use, and physical coordination burden exactly once while recording the corresponding accounts. |
| 9 | `PHASE_9` | Register new in-transit payloads and delayed-effect events; update commitments, reservations, and unresolved statuses. |
| 10 | `PHASE_10` | Apply declared natural drive for the remainder of the epoch and produce the end-of-epoch record. |

Phases 7 and 8 separate proposal formation from mutation. Phase 8 binds physical ownership and the once-only physical commit record. Phase 9 may register later transit/delay/status objects, but it may not repeat an identifier already committed by phase 8 in the same epoch. I-5 represents these boundaries without performing a phase.

## 5. Closed declaration inventory

The future public surface contains exactly 50 new types. Field order, annotations, applicability, construction rules, and enum members are exact in the mechanical contract.

| Module | Type | Kind | Exact field order or signature |
|---|---|---|---|
| `hashing` | `EventKeyDigest` | frozen-slotted-dataclass | value |
| `hashing` | `EventDeclarationDigest` | frozen-slotted-dataclass | value |
| `hashing` | `OwnershipDigest` | frozen-slotted-dataclass | value |
| `hashing` | `PhaseCommitDigest` | frozen-slotted-dataclass | value |
| `hashing` | `DurabilityEvidenceDigest` | frozen-slotted-dataclass | value |
| `hashing` | `RunEnvelopeDigest` | frozen-slotted-dataclass | value |
| `hashing` | `TraceDigest` | closed-type-alias | CanonicalTraceRowHash\|CanonicalTracePrefixHash\|CanonicalScientificTracePayloadHash |
| `events` | `PhaseOrdinal` | IntEnum | enum values in contract |
| `events` | `EventKey` | frozen-slotted-dataclass | epoch, phase_ordinal, declared_priority, group_or_scope_id, event_kind, primary_object_id, local_sequence |
| `events` | `EventDeclaration` | frozen-slotted-dataclass | key, event_ref, declared_simultaneity_ref, payload_hash, predecessor_event_key |
| `events` | `PhaseCommitRecord` | frozen-slotted-dataclass | epoch, phase_ordinal, previous_phase_commit_digest, ordered_event_digests, epoch_ownership_digest, physical_phase_record_ref, trace_row_digest |
| `events` | `TraceCompleteness` | StrEnum | enum values in contract |
| `ownership` | `OwnershipKind` | StrEnum | enum values in contract |
| `ownership` | `OpaqueLocusKey` | frozen-slotted-dataclass | namespace, coordinate |
| `ownership` | `UpdateOwnershipClaim` | frozen-slotted-dataclass | epoch, phase_ordinal, event_key, owner_ref, locus, ownership_kind |
| `ownership` | `OwnershipConflict` | frozen-slotted-dataclass | locus, first_claim, second_claim |
| `ownership` | `EpochUpdateOwnership` | frozen-slotted-dataclass | epoch, claims, digest |
| `ownership` | `OwnershipValidationRecord` | frozen-slotted-dataclass | status, ownership, conflict |
| `durability` | `CommitOutcome` | StrEnum | enum values in contract |
| `durability` | `PolicyMemoryTransaction` | frozen-slotted-dataclass | decision_ref, prior_memory_hash, next_memory_hash, trace_row_digest |
| `durability` | `PhysicalPhaseTransaction` | frozen-slotted-dataclass | phase_commit, ownership, ledger_evidence_ref, trace_row_digest |
| `durability` | `AtomicStoreRequest` | frozen-slotted-dataclass | request_ref, expected_trace_prefix, expected_phase_predecessor, policy_memory_transaction, physical_phase_transaction, attempt_ordinal |
| `durability` | `DurablePrefixEvidence` | frozen-slotted-dataclass | request_ref, committed_prefix, phase_commit_digest, evidence_digest |
| `durability` | `AtomicStoreRejection` | frozen-slotted-dataclass | request_ref, preserved_prefix, failure_code |
| `durability` | `AtomicStoreAmbiguity` | frozen-slotted-dataclass | request_ref, last_confirmed_prefix, evidence_refs |
| `durability` | `AtomicStoreUnavailable` | frozen-slotted-dataclass | request_ref, preserved_prefix |
| `durability` | `AtomicCommitOutcome` | closed-type-alias | DurablePrefixEvidence\|AtomicStoreRejection\|AtomicStoreAmbiguity\|AtomicStoreUnavailable |
| `durability` | `AtomicStore` | runtime-checkable-Protocol | commit(self, request: AtomicStoreRequest, /) -> AtomicCommitOutcome |
| `durability` | `PolicyDecisionStore` | runtime-checkable-Protocol | commit_policy_decision(self, transaction: PolicyMemoryTransaction, expected_prefix: CanonicalTracePrefixHash, /) -> AtomicCommitOutcome |
| `durability` | `PhaseCommitStore` | runtime-checkable-Protocol | commit_phase(self, transaction: PhysicalPhaseTransaction, expected_prefix: CanonicalTracePrefixHash, /) -> AtomicCommitOutcome |
| `traces` | `TraceRowKind` | StrEnum | enum values in contract |
| `traces` | `TraceHeader` | frozen-slotted-dataclass | trace_schema_ref, accepted_configuration_object_content_hash, execution_semantics_hash, initial_state_payload_hash, initial_policy_memory_payload_hash |
| `traces` | `TraceFooter` | frozen-slotted-dataclass | terminal_or_last_confirmed_state_payload_hash, terminal_or_last_confirmed_policy_memory_payload_hash, confirmed_row_count, trace_completeness |
| `traces` | `CanonicalScientificTracePayloadV1` | frozen-slotted-dataclass | header, ordered_rows, footer, payload_hash |
| `traces` | `CanonicalTraceRow` | frozen-slotted-dataclass | row_index, row_kind, event_key, phase_ordinal, predecessor_row_digest, record_refs, payload_hashes |
| `traces` | `TraceRowFrame` | frozen-slotted-dataclass | row_digest, frame_bytes |
| `traces` | `CanonicalTracePrefix` | frozen-slotted-dataclass | row_frames, row_count, prefix_digest |
| `traces` | `TraceExtensionEvidence` | frozen-slotted-dataclass | prior_prefix_digest, extended_prefix_digest, appended_row_digests |
| `traces` | `CompleteTraceEvidence` | frozen-slotted-dataclass | trace_digest, last_prefix_digest, confirmed_row_count, completeness, terminal_state_hash, terminal_memory_hash |
| `traces` | `MinimumReconstructableTrace` | frozen-slotted-dataclass | accepted_event_keys, phase_commit_digests, ownership_digest, proposal_and_screen_refs, policy_memory_transaction_refs, trace_prefix, commit_dispositions, completeness |
| `traces` | `RunTraceEnvelopeV1` | frozen-slotted-dataclass | canonical_trace_digest, execution_binding_ref, execution_identity, operational_evidence_refs, completeness, envelope_digest |
| `traces` | `TraceValidationStatus` | StrEnum | enum values in contract |
| `traces` | `TraceValidationResult` | frozen-slotted-dataclass | status, confirmed_prefix, complete_evidence |
| `execution` | `ProposalRecord` | frozen-slotted-dataclass | event_key, proposal_ref, common_pre_state_hash, proposed_update_refs |
| `execution` | `ScreeningDisposition` | StrEnum | enum values in contract |
| `execution` | `ScreeningResult` | frozen-slotted-dataclass | proposal_ref, disposition, admitted_update_refs, reason_refs |
| `execution` | `PhaseCommitRequest` | frozen-slotted-dataclass | phase_ordinal, proposals, screening_results, ownership, atomic_request |
| `execution` | `T3EntryGuard` | frozen-slotted-dataclass | stage_authorization_ref, authorization_use_ref, execution_binding_ref, capability_ref, real_durability_backend_ref |
| `execution` | `ScientificExecutionLease` | frozen-slotted-dataclass | guard, lease_ref, operation, consumed |
| `faults` | `FaultHookBoundary` | frozen-slotted-dataclass | applicability, fault_schedule_ref, delivery_ref |

### 5.1 Events

`PhaseOrdinal` records which accepted phase owns an event. `EventKey` records the exact seven-part stable key `(epoch, phase_ordinal, declared_priority, group_or_scope_id, event_kind, primary_object_id, local_sequence)`. The object that experiences no change is the immutable declaration itself; ordering merely returns a tuple. This matters because equal keys cannot fall back to container or thread order. For example, two dummy declarations at epoch 0, phase 4, priority 0, scope `scope-a`, kind `DUMMY_EVENT`, primary object `...:a`, and local sequence 0 are rejected as duplicates. I-5 does not decide what the event means or whether its proposed transformation is scientifically correct.

`EventDeclaration` binds a key, stable event reference, optional declared-simultaneity group, payload hash, and literal predecessor. `PhaseCommitRecord` records the preceding phase digest, ordered event digests, epoch ownership digest, physical-record applicability, and the trace row bound to the phase. These records are experienced by no mutable engine; they are immutable evidence supplied to validators. For example, a phase-1 dummy record has `NOT_APPLICABLE` predecessor, while phase 2 must name phase 1 exactly. The record does not perform a transition or prove the named payload is valid science.

`TraceCompleteness` records explicit complete, declared-fault-terminal, partial-prefix, absent, unresolved, or invalid evidence states. The trace/envelope carries the status; no scientific object is changed by classification. `DECLARED_FAULT_TERMINAL` is representable for compatibility with the specification but unreachable until UQ-38 authority.

### 5.2 Ownership

`OpaqueLocusKey` records only a namespace and uninterpreted coordinate bytes. `UpdateOwnershipClaim` says which proposed update owns that physical locus in an epoch/phase. `EpochUpdateOwnership` is the canonical, duplicate-free, disjoint tuple and digest. The physical update—not an accounting mirror or policy-memory record—is the object that would later experience the change. Explicit ownership prevents the same loss, conversion, resource use, burden, transit registration, or natural drive from being applied twice.

For example, owner A and owner B may claim synthetic loci `00` and `01`; construction succeeds. If both claim `00`, `OwnershipConflict` identifies the lexicographically first pair and the validator rejects. It never selects a winner, allocates capacity, applies a transformation, or interprets coordinates. Informational policy-memory ownership is expressly outside physical ownership and is rejected if inserted as a physical claim.

### 5.3 Abstract durability

`AtomicStoreRequest` records a stable request, exact expected trace prefix, phase predecessor, applicable policy-memory and/or physical-phase transaction, and attempt ordinal. The later store would experience a commit attempt; no I-5 authority object performs one. Coupling policy decision, next memory, physical phase record, ledger evidence, ownership, and trace row prevents a successful abstract outcome from splitting those facts.

`DurablePrefixEvidence`, `AtomicStoreRejection`, `AtomicStoreAmbiguity`, and `AtomicStoreUnavailable` record typed observations. A committed dummy example must name the request and its exact literal extension. A rejected or unavailable example preserves the original prefix byte-for-byte. An ambiguous example records only the last confirmed prefix/evidence and cannot be treated as committed, rejected, or safe to retry. This is an obligation schema, not a backend, filesystem transaction, database guarantee, crash test, or distributed-consensus claim.

`AtomicStore` is a protocol declaration only. This authority accepts zero implementations. A Python instance, tuple, dictionary, temporary file, or protocol-conforming class is not durable-atomic evidence.

### 5.4 Traces

`CanonicalTraceRow` records row index/kind, event and phase coordinate, predecessor row digest, stable record references, and dummy or replay-relevant payload hashes. The row is the object appended later; it does not cause the referenced event. Its ECJ-1 projection excludes execution identity, clock, host, process, storage, diagnostics, recovery, correction, publication, and sensitive/domain data unnecessary for reconstruction.

`TraceRowFrame` is `u64be(row_byte_length) || row_ecj1`. `CanonicalTracePrefix` is the literal concatenation of frames, not a row count and hash standing in for absent bytes. `TraceExtensionEvidence` requires a nonempty literal suffix. For example, one dummy row frame may extend an empty known prefix; presenting unchanged bytes as an extension fails. Prior bytes never mutate.

`CompleteTraceEvidence` binds the full digest, last prefix, count, completeness, and terminal/last-confirmed state and memory hashes. `MinimumReconstructableTrace` retains only the facts needed to determine event order, phase predecessors, ownership, proposal/screen/commit disposition, policy-memory identity, trace predecessor, commit outcome, and completeness class. `RunTraceEnvelopeV1` separately records run-specific references. Neither an envelope nor a summary substitutes for missing canonical bytes, and I-8 finalization/publication remains deferred.

### 5.5 Execution and fault boundaries

`ProposalRecord`, `ScreeningResult`, and `PhaseCommitRequest` record supplied boundaries; I-5 does not select proposals, screen constraints, allocate requests, or commit physical state. A synthetic proposal can state a common pre-state hash and opaque update references, but it cannot call a transition function. Its limitation is deliberate: scientific meaning and behavior belong to later authorized adapters.

`T3EntryGuard` and `ScientificExecutionLease` make the execution boundary explicit. A valid guard would require an accepted authorization use, binding, T3 capability, and separately accepted real durability backend. Because I-5 accepts no backend, every T3 entry fails with `REAL_DURABILITY_BACKEND_UNAVAILABLE` before lease creation, callback invocation, or phase 1. Validation may not import `execution`, construct a lease, or invoke any T3 callable.

`FaultHookBoundary` records only the all-`NOT_APPLICABLE` base hook. A synthetic all-inert hook validates; any applicable schedule or delivery reference is rejected. The hook cannot deliver a fault and invents no kind, target, acknowledgement, continuation, or terminal semantics before UQ-38.

## 6. Callable and signature inventory

Exactly 32 public callables and 9 required private helpers are frozen. T0/T1 callables operate only on supplied inert records/bytes. T3 and guard-only signatures are prospective fail-closed boundaries and are statically unreachable from validation.

| Module | Callable | Class | Exact signature |
|---|---|---|---|
| `hashing` | `compute_event_key_digest` | `T0` | `(*, epoch: int, phase_ordinal: int, declared_priority: int, group_or_scope_id: str, event_kind: str, primary_object_id: str, local_sequence: int) -> EventKeyDigest` |
| `hashing` | `compute_event_declaration_digest` | `T0` | `(*, event_key_digest: EventKeyDigest, event_ref: ObjectRef, declared_simultaneity_ref_or_not_applicable: ObjectRef\|Applicability, payload_hash: ObjectContentHash, predecessor_event_key_digest_or_not_applicable: EventKeyDigest\|Applicability) -> EventDeclarationDigest` |
| `hashing` | `compute_ownership_digest` | `T0` | `(projection_kind: Literal['CLAIM','EPOCH'], projection: ECJ1Value, /) -> OwnershipDigest` |
| `hashing` | `compute_phase_commit_digest` | `T0` | `(projection: ECJ1Value, /) -> PhaseCommitDigest` |
| `hashing` | `compute_durability_evidence_digest` | `T0` | `(projection_without_evidence_digest: ECJ1Value, /) -> DurabilityEvidenceDigest` |
| `hashing` | `compute_run_envelope_digest` | `T0` | `(projection_without_envelope_digest: ECJ1Value, /) -> RunEnvelopeDigest` |
| `events` | `order_event_keys` | `T0` | `(declarations: tuple[EventDeclaration,...], /) -> tuple[EventDeclaration,...]` |
| `events` | `validate_event_declaration` | `T0` | `(declaration: EventDeclaration, /) -> None` |
| `events` | `validate_phase_commit_record` | `T0` | `(record: PhaseCommitRecord, expected_previous: PhaseCommitDigest\|Applicability, /) -> None` |
| `ownership` | `build_epoch_update_ownership` | `T0` | `(epoch: int, claims: tuple[UpdateOwnershipClaim,...], /) -> EpochUpdateOwnership` |
| `ownership` | `validate_update_ownership` | `T0` | `(claims: tuple[UpdateOwnershipClaim,...], /) -> OwnershipValidationRecord` |
| `durability` | `build_atomic_commit_request` | `T1` | `(*, request_ref: ObjectRef, expected_trace_prefix: TraceDigest, expected_phase_predecessor: PhaseCommitDigest\|Applicability, policy_memory_transaction: PolicyMemoryTransaction\|Applicability, physical_phase_transaction: PhysicalPhaseTransaction\|Applicability, attempt_ordinal: int) -> AtomicStoreRequest` |
| `durability` | `classify_inert_commit_failure` | `T1` | `(request: AtomicStoreRequest, observed: Literal['REJECTED','AMBIGUOUS','UNAVAILABLE'], evidence_refs: tuple[ObjectRef,...], /) -> AtomicStoreRejection\|AtomicStoreAmbiguity\|AtomicStoreUnavailable` |
| `durability` | `validate_atomic_commit_outcome` | `T1` | `(request: AtomicStoreRequest, outcome: AtomicCommitOutcome, /) -> None` |
| `durability` | `validate_policy_memory_transaction` | `T0` | `(transaction: PolicyMemoryTransaction, /) -> None` |
| `durability` | `validate_durable_prefix` | `T1` | `(expected: CanonicalTracePrefix, observed: CanonicalTracePrefix, outcome: CommitOutcome, /) -> None` |
| `traces` | `project_canonical_trace_row` | `T0` | `(row: CanonicalTraceRow, /) -> bytes` |
| `traces` | `frame_trace_row` | `T0` | `(row: CanonicalTraceRow, /) -> TraceRowFrame` |
| `traces` | `build_trace_prefix` | `T0` | `(frames: tuple[TraceRowFrame,...], /) -> CanonicalTracePrefix` |
| `traces` | `extend_trace_prefix` | `T0` | `(prefix: CanonicalTracePrefix, appended: tuple[TraceRowFrame,...], /) -> tuple[CanonicalTracePrefix,TraceExtensionEvidence]` |
| `traces` | `validate_complete_trace_evidence` | `T0` | `(prefix: CanonicalTracePrefix, evidence: CompleteTraceEvidence, /) -> TraceValidationResult` |
| `traces` | `build_minimum_reconstructable_trace` | `T0` | `(*, events: tuple[EventDeclaration,...], phases: tuple[PhaseCommitRecord,...], ownership: EpochUpdateOwnership, proposal_and_screen_refs: tuple[ObjectRef,...], policy_memory_transaction_refs: tuple[ObjectRef,...], prefix: CanonicalTracePrefix, commit_dispositions: tuple[CommitOutcome,...], completeness: TraceCompleteness) -> MinimumReconstructableTrace` |
| `traces` | `build_run_trace_envelope` | `T0` | `(*, canonical_trace_digest: TraceDigest\|Applicability, execution_binding_ref: ObjectRef\|Applicability, execution_identity: ExecutionIdentity\|Applicability, operational_evidence_refs: tuple[ObjectRef,...], completeness: TraceCompleteness) -> RunTraceEnvelopeV1` |
| `faults` | `validate_inert_fault_hook` | `T0` | `(hook: FaultHookBoundary, /) -> None` |
| `execution` | `validate_t3_entry_guard` | `T3_GUARD_ONLY` | `(guard: T3EntryGuard, /) -> None` |
| `execution` | `validate_scientific_execution_lease` | `T3_GUARD_ONLY` | `(lease: ScientificExecutionLease, operation: str, /) -> None` |
| `execution` | `begin_bound_scientific_execution` | `T3` | `(*, guard: T3EntryGuard, requested_operation: str) -> ScientificExecutionLease` |
| `execution` | `propose_phase_updates` | `T3` | `(*, lease: ScientificExecutionLease, phase: PhaseOrdinal, state_ref: ObjectRef, adapter_ref: ObjectRef) -> tuple[ProposalRecord,...]` |
| `execution` | `screen_and_admit` | `T3` | `(*, lease: ScientificExecutionLease, proposals: tuple[ProposalRecord,...], screening_adapter_ref: ObjectRef) -> tuple[ScreeningResult,...]` |
| `execution` | `propose_joint_transition` | `T3` | `(*, lease: ScientificExecutionLease, proposals: tuple[ProposalRecord,...], joint_adapter_ref: ObjectRef) -> ProposalRecord` |
| `execution` | `commit_phase_updates` | `T3` | `(*, lease: ScientificExecutionLease, request: PhaseCommitRequest) -> PhaseCommitRecord` |
| `execution` | `advance_epoch` | `T3` | `(*, lease: ScientificExecutionLease, epoch: int, initial_state_ref: ObjectRef, phase_input_refs: tuple[ObjectRef,...]) -> RunTraceEnvelopeV1` |

Required private helpers:

- `events._event_key_projection(key: EventKey, /) -> tuple[object,...]`
- `events._phase_identity_guard(declarations: tuple[EventDeclaration,...], /) -> None`
- `ownership._claim_order_key(claim: UpdateOwnershipClaim, /) -> tuple[object,...]`
- `durability._transaction_trace_digest(request: AtomicStoreRequest, /) -> TraceDigest`
- `traces._trace_row_ecj1_projection(row: CanonicalTraceRow, /) -> dict[str,object]`
- `traces._literal_prefix_bytes(prefix: CanonicalTracePrefix, /) -> bytes`
- `execution._require_i5_unavailable_backend(guard: T3EntryGuard, /) -> NoReturn`
- `hashing._i5_frame_fields(domain: bytes, fields: tuple[bytes,...], /) -> bytes`
- `faults._reject_fault_delivery(hook: FaultHookBoundary, /) -> None`

## 7. Hash domains and byte projections

I-5 uses the existing SHA-256 and canonicalization authority without changing any accepted domain. Each genuinely new I-5 preimage is `FRAME(domain) || FRAME(field_1) ...`, where `FRAME(x)=u64be(len(x)) || x`. Canonical trace row, prefix, and payload hashes instead reuse their already accepted ECJ-1 preimages and callables byte-identically. Output/self-reference digest fields are excluded. Typed wrappers prevent cross-domain substitution; a domain mismatch or distinct-preimage collision fails closed.

| Kind | Domain | Status | Synthetic preimage bytes | Synthetic SHA-256 |
|---|---|---|---:|---|
| `EVENT_KEY` | `ebu.event-key.v1` | `NEW_I5_DOMAIN` | 117 | `sha256:a10236b81dc0a918b6f1c493d60551bd0a685228a4b49d0bb2d7028e69a28192` |
| `EVENT_DECLARATION` | `ebu.event-declaration.v1` | `NEW_I5_DOMAIN` | 263 | `sha256:36dc5da6c06f2af30855936eab028d494448807548e89a133527bd5770c966cd` |
| `OWNERSHIP_CLAIM` | `ebu.ownership-claim.v1` | `NEW_I5_DOMAIN` | 203 | `sha256:684abb6dfbd2950d4f5ddb16203e0726dc16f2c44e20a2194fc6a69ba4e996f5` |
| `EPOCH_OWNERSHIP` | `ebu.epoch-ownership.v1` | `NEW_I5_DOMAIN` | 127 | `sha256:e1a6324c6d214507e626eb96024b90757a2a04a66bcf01aef3725f478b96d102` |
| `PHASE_COMMIT` | `ebu.phase-commit.v1` | `NEW_I5_DOMAIN` | 370 | `sha256:8a10e66ee1734b1ca080c465689ea16775fcbc285225904c9bfe2e78e65a96df` |
| `DURABILITY_EVIDENCE` | `ebu.durability-evidence.v1` | `NEW_I5_DOMAIN` | 223 | `sha256:3436c8bcc563c71822476883953f6dc2035cb2bcf4b701755d5ea18c246767ed` |
| `RUN_ENVELOPE` | `ebu.run-envelope.v1` | `NEW_I5_DOMAIN` | 189 | `sha256:5fcc15e49a67f24bce804dbe149e69de891059c28f964a88a76d1b7180924c90` |
| `TRACE_ROW` | `ebu.canonical-trace-row.v1` | `ACCEPTED_I1_DOMAIN_REUSED_BYTE_IDENTICALLY` | 1177 | `sha256:2baa49f2f7986a052e24e86152362456b0f564d20dd0ca759a518ff7805700cb` |
| `TRACE_PREFIX` | `ebu.canonical-trace-prefix.v1` | `ACCEPTED_I1_DOMAIN_REUSED_BYTE_IDENTICALLY` | 454 | `sha256:11d47f87a471f939cd946f1d0c41a38390df5e0c45354dad6fe33e62aa4fdddb` |
| `FULL_TRACE` | `ebu.canonical-scientific-trace-payload.v1` | `ACCEPTED_I1_DOMAIN_REUSED_BYTE_IDENTICALLY` | 1325 | `sha256:1ac42875dddd575ec8a4d4df4b539757433fdab7f3074d201389a888bbbcd1a0` |

## 8. Failures, exports, signatures, and graphs

The accepted 185-code failure prefix remains byte-identical (`4894` LF-framed bytes, SHA-256 `7696b43a1d0412888b6284c85ed0a67f55b74549e2df0c93daf3a48b2594b6c3`). Exactly 42 codes append at ordinals 186–227. The future 227-code projection is `5997` bytes with SHA-256 `4cb1daceb30c0f106e7ba288980d379da2403236593948b4be47247704555ae4`. Within each callable, formation precedes semantic checks and the exact callable-specific list in the mechanical contract decides multiple-active precedence.

| Ordinal | FailureCode | Owner | Activation/meaning |
|---:|---|---|---|
| 186 | `I5_RECORD_FORMATION_INVALID` | `errors` | an I-5 constructor receives a missing, extra, wrongly ordered, wrongly typed, non-exact, noncanonical, or inapplicable field before any semantic interface check |
| 187 | `PHASE_ORDINAL_INVALID` | `events` | a phase is not the exact PhaseOrdinal member PHASE_1 through PHASE_10 or disagrees with the accepted ordinal/name row |
| 188 | `EVENT_KEY_INVALID` | `events` | one of the seven EventKey coordinates violates its exact type, grammar, range, or pre-mutation assignment rule |
| 189 | `EVENT_KEY_DUPLICATE` | `events` | two declarations have equal full EventKey values |
| 190 | `EVENT_ORDER_INVALID` | `events` | supplied declaration order is not the exact increasing EventKey order or declared predecessor does not occupy the immediately previous position |
| 191 | `EVENT_IDENTITY_INVALID` | `events` | event_ref, primary_object_id, payload hash, phase identity, or declared simultaneity is inconsistent within one declaration |
| 192 | `PHASE_8_PHASE_9_DUPLICATE_IDENTIFIER` | `events` | a phase-9 registration repeats an identifier already physically committed in phase 8 |
| 193 | `PHASE_PREDECESSOR_MISMATCH` | `events` | a non-first phase or event names a predecessor other than the exact immediately accepted digest/key, or a first item supplies a predecessor |
| 194 | `PHASE_COMMIT_RECORD_INVALID` | `events` | phase, event digests, ownership binding, physical-record applicability, or trace-row binding is internally inconsistent |
| 195 | `UPDATE_OWNERSHIP_CLAIM_INVALID` | `ownership` | a claim has mismatched epoch/phase/event/owner/locus fields or a noncanonical opaque locus |
| 196 | `INFORMATIONAL_MEMORY_OWNERSHIP_FORBIDDEN` | `ownership` | an informational policy-memory coordinate is presented as physical ownership |
| 197 | `UPDATE_OWNERSHIP_CONFLICT` | `ownership` | two different owners claim the same opaque physical locus |
| 198 | `OWNERSHIP_ORDER_INVALID` | `ownership` | claims are not in the exact locus/event/owner canonical order or contain an exact duplicate |
| 199 | `PHASE_OWNERSHIP_MISMATCH` | `events` | a claim epoch/phase disagrees with its EventKey or the epoch-wide ownership record |
| 200 | `ATOMIC_COMMIT_REQUEST_INVALID` | `durability` | the request has no applicable transaction, mismatched shared trace row, invalid attempt ordinal, or inconsistent request identity |
| 201 | `EXPECTED_TRACE_PREFIX_MISMATCH` | `durability` | the observed/request-bound prefix digest or literal bytes differ from the exact expected prefix |
| 202 | `COMMIT_REJECTED` | `durability` | the supplied inert outcome is exactly REJECTED after request and expected-prefix validation |
| 203 | `COMMIT_AMBIGUOUS` | `durability` | the inert observation cannot establish committed versus uncommitted |
| 204 | `DURABILITY_UNAVAILABLE` | `durability` | the abstract store boundary was unavailable before an accepted commit outcome and the exact prefix is preserved |
| 205 | `DURABILITY_EVIDENCE_MISSING` | `durability` | a COMMITTED or AMBIGUOUS classification lacks the exact evidence required for that classification |
| 206 | `DURABILITY_EVIDENCE_INCONSISTENT` | `durability` | evidence request, prefix, phase, exclusion projection, or evidence digest conflicts with the request/outcome |
| 207 | `POLICY_MEMORY_TRANSACTION_INVALID` | `durability` | decision, before/after memory applicability, lineage, or trace-row coupling is inconsistent |
| 208 | `PHYSICAL_PHASE_TRANSACTION_INVALID` | `durability` | phase record, epoch ownership, ledger evidence, or common trace-row binding is inconsistent |
| 209 | `TRACE_ROW_INVALID` | `traces` | row index/kind/phase/event applicability, canonical refs/hashes, or ECJ-1 projection violates the closed row schema |
| 210 | `TRACE_ROW_PREDECESSOR_MISMATCH` | `traces` | row zero does not use the genesis applicability rule or a later row does not name the immediately preceding row hash |
| 211 | `TRACE_ROW_GAP` | `traces` | literal row indices are not contiguous from the prefix start or an appended suffix does not begin at the prior row count |
| 212 | `TRACE_PREFIX_INVALID` | `traces` | row count, frames, frame lengths, row digests, prefix digest, or literal concatenation is inconsistent |
| 213 | `TRACE_PREFIX_NOT_LITERAL` | `traces` | a prefix claim supplies only metadata/hash/count and not the exact ordered frame bytes |
| 214 | `TRACE_PREFIX_MUTATION_FORBIDDEN` | `traces` | observed prior prefix bytes differ from the accepted literal prefix |
| 215 | `TRACE_EXTENSION_IDENTITY_INVALID` | `traces` | an extension is empty or claims byte identity as growth |
| 216 | `TRACE_COMPLETENESS_INVALID` | `traces` | completeness status, confirmed count, terminal evidence, or complete-payload binding violates its exact applicability rule |
| 217 | `TRACE_EQUIVOCAL` | `traces` | two supplied evidence paths assign different bytes/digests or completeness to the same row index/prefix coordinate |
| 218 | `TRACE_EVIDENCE_MISSING` | `traces` | the classification requires literal prefix/full-trace/terminal evidence that is absent |
| 219 | `MINIMUM_TRACE_INCOMPLETE` | `traces` | one of the eight UQ-29 reconstruction determinations cannot be made from the supplied minimum record and bytes |
| 220 | `RUN_TRACE_ENVELOPE_INVALID` | `traces` | canonical trace reference, binding/identity applicability, operational evidence order, completeness, or exclusion digest is inconsistent |
| 221 | `SCIENTIFIC_EXECUTION_LEASE_INVALID` | `execution` | a lease is malformed, consumed, nonlocal, wrong-operation, wrong-binding, reconstructed, or otherwise not an exact live lease |
| 222 | `T3_ENTRY_GUARD_FAILED` | `execution` | accepted authorization use, execution binding, T3 capability, operation binding, or required backend prerequisite is absent or inconsistent |
| 223 | `REAL_DURABILITY_BACKEND_UNAVAILABLE` | `execution` | T3 entry requires a real backend but I-5 accepts none |
| 224 | `EXECUTION_CALLBACK_FORBIDDEN` | `execution` | an I-5 or validation path attempts to invoke a scientific callback |
| 225 | `SCIENTIFIC_STATE_ADVANCE_FORBIDDEN` | `execution` | an I-5 or validation path could advance scientific state |
| 226 | `I5_HASH_COLLISION` | `hashing` | distinct valid I-5 preimages produce the same digest; fail closed without resolution |
| 227 | `FAULT_HOOK_INVALID` | `faults` | the fault hook is not exactly the all-NOT_APPLICABLE inert boundary |

The accepted 309-export root prefix remains byte-identical (`6838` bytes, SHA-256 `aa8c120278412a994869f9a4de9e353c2283a137568fec0d643b6e164f045db8`). The 50 type names then 32 callable names append as an 82-name suffix. The future 391-export projection is `8625` bytes with SHA-256 `f27ed982d7e646be870404239ad617d181df8276728f9a3f1fc878c5bbfa46db`.

The accepted 155 signature rows remain unchanged. I-5 appends 82 public rows for a future total of 237; combined canonical size is 118010 bytes and SHA-256 `083a429b0fd36dda80d62a9113fe81e758c17c210385d10e76dc2c2a80dbdaba`. Module-local exports are exact in the mechanical contract.

The future package graph has 34 modules, 192 direct edges, and zero cycles; its projection is 2619 bytes, SHA-256 `96055fd0d2dc4dd0f3bcbf2cb169967c7bceffc8d70b50252e154b5649c38bcb`. The I-3+D1+D2+I-4+I-5 extension graph has 26 modules, 171 edges, and zero cycles; its projection is 2276 bytes, SHA-256 `91968c5320599969fb29824dfed009174e2c3de6136d6aaa59eb36f2ef439909`. Validation cannot import execution; execution cannot import validation. Dynamic imports, network/subprocess reachability, historical runner/finalizer/Gate paths, production bootstrap, hidden backends, and new dependencies are prohibited.

## 9. Closed future implementation path boundary

This section freezes audit scope only. It does not authorize implementation. No path outside the eleven-row manifest may later change without new authority, and accepted additive compatibility rules require no existing compatibility-test edit.

| Path | Status | Owner | Purpose |
|---|---|---|---|
| `src/ebu_framework/events.py` | `NEW` | `events` | Ten-phase constants, EventKey ordering, immutable event and phase-commit declarations. |
| `src/ebu_framework/ownership.py` | `NEW` | `ownership` | Epoch-wide physical update ownership and deterministic conflict detection. |
| `src/ebu_framework/durability.py` | `NEW` | `durability` | Abstract atomic grouping, typed outcomes, and prefix-preservation declarations. |
| `src/ebu_framework/traces.py` | `NEW` | `traces` | Canonical inert rows, literal framed prefixes, completeness, reconstruction, and run-envelope declarations. |
| `src/ebu_framework/execution.py` | `NEW` | `execution` | Prospective T3 signatures and fail-closed backend/lease guards only. |
| `src/ebu_framework/hashing.py` | `MODIFIED` | `hashing` | Append I-5 digest wrappers, framed hash domains, and exact digest callables. |
| `src/ebu_framework/faults.py` | `MODIFIED` | `faults` | Append the inert all-NOT_APPLICABLE hook declaration and validator. |
| `src/ebu_framework/errors.py` | `MODIFIED` | `errors` | Append 42 FailureCode members and necessary static failure mapping; preserve the already accepted FailureStage.I5 member. |
| `src/ebu_framework/__init__.py` | `MODIFIED` | `root_exports` | Append exactly 82 I-5 root exports after the accepted 309-name prefix. |
| `tests/framework/test_event_ownership.py` | `NEW` | `V6_validation` | Materialize V6 event/order/ownership vectors and static no-effect assertions. |
| `tests/framework/test_inert_durability.py` | `NEW` | `V7_V11_validation` | Materialize inert V7 durability/trace/fault vectors and V11 AST reachability evidence without importing execution. |

The four modified predecessors carry exact mode/blob/size/raw-SHA identities in the implementation manifest. The seven new paths have expected mode `100644`. Existing compatibility tests are excluded because the integrated rules already derive additive failure, export, module, edge, signature, and domain changes.

## 10. Validation authority

The validation contract stores all 140 vectors internally; no fixture path is authorized. Counts are V6=48, V7=63, and V11=29. Kinds are FORMATION_BOUNDARY=50, MULTIPLE_ACTIVE_PRECEDENCE=12, POSITIVE=24, SINGLE_FAILURE=42, STATIC_REACHABILITY=12. Dynamic owning constructor/interface calls total 111; predicate activations total 116; completed checks total 253. The corrected canonical vector projection is 112376 bytes, SHA-256 `7d6ec486ba0b8d17152734789ea868abf58fdb5468d39898cf19b609bdafea8c`.

Every failure vector is assigned to the exact constructor, callable, or static source owner whose frozen failure precedence contains its expected code. Closed dynamic variants use the existing root path `/` of that owner baseline, supporting records construct before the single owning invocation, and the validation contract freezes exact local witnesses for the fifteen dynamically reassigned cases. The three reassigned execution cases remain static prospective source assertions. Their expected `FailureId` values are derived from the corrected exact owner under the unchanged `ebu.failure-id.v1` framing; the incorrectly owned IDs are not aliases or accepted alternatives.

V6 uses opaque synthetic coordinates and inert declarations to cover all ten phases, total ordering, equal-key rejection, stable ordering, phase-8/phase-9 identity exclusion, disjoint/conflicting ownership, informational-memory exclusion, precedence, and zero mutation. V7 uses dummy bytes and closed inert store observations to cover typed outcomes, predecessor/prefix checks, atomic groups, ambiguity, missing evidence, row projection/framing, literal prefixes, gaps/equivocation, policy-memory coupling, and inert faults. V11 parses text and AST only to prove T3/lease/runner/finalizer/Gate, dynamic import, network, subprocess, entropy, bootstrap, publication/recovery, model-step, and fault-delivery non-reachability.

Every dynamic vector identifies one exact owning future constructor or interface, a closed recursive materialization catalogue, deterministic patches, exact expected outcome and FailureId, completed-check count, and zero-effect counters. Future tests must actually construct/invoke that owner; metadata assertions do not satisfy the vector. Static vectors never import execution. The authority-drafting checks performed now validate the documents only and do not execute these prospective vectors.

### 10.1 Closed-variant materialization

`apply_closed_variant` is keyed by the complete ordered coordinate `(baseline_call, failure-code operand)`. The mechanical catalogue contains 39 distinct coordinates for 60 stored invocations and 36 distinct operands. Every invocation resolves exactly once; missing, ambiguous, unresolved, and unused expansion counts are all zero. `I5_RECORD_FORMATION_INVALID`, `PHASE_PREDECESSOR_MISMATCH`, and `TRACE_ROW_GAP` each require owner-specific expansions under more than one baseline. No failure code alone selects a mutation.

The materializer recursively expands atoms, records, exact enum members, digest wrappers, bytes, structural variants, and named supports into one normalized call. It computes baseline correlations, saves an immutable baseline snapshot, and then processes vector patches in stored order. Each coordinate row declares its exact baseline and operand, ordered operations, path-existence proof, literal or catalogue-derived values, supports, recomputations and dependency order, active predicate, deliberately inactive predicates, construction proof, and first owner failure. Only `replace`, `append_current_copy`, `append_support`, `prepend_support`, `replace_tuple`, exact-constructor replacement, and deterministic event-predecessor relinking are admitted. Every path must exist when used. Only listed derived values may be recomputed. Runtime choice, search, inference from the expected result, and undeclared repair are forbidden.

The exact coordinate inventory is:

| Baseline | Operand | Exact activating operation summary |
|---|---|---|
| `events.validate_event_declaration` | `I5_RECORD_FORMATION_INVALID` | replace `EventDeclaration.key` with exact wrong-type string |
| `events.validate_event_declaration` | `PHASE_ORDINAL_INVALID` | replace nested phase with exact int `0` |
| `events.validate_event_declaration` | `EVENT_IDENTITY_INVALID` | replace `event_ref` with `object_ref_b` |
| `events.order_event_keys` | `EVENT_KEY_INVALID` | replace first `local_sequence` with `-1` |
| `events.order_event_keys` | `EVENT_KEY_DUPLICATE` | append two exact current declaration copies and link literal predecessors |
| `events.order_event_keys` | `EVENT_ORDER_INVALID` | append a copy, make the first key sequence `1`, and deterministically relink the chain, yielding decreasing order |
| `events.order_event_keys` | `PHASE_8_PHASE_9_DUPLICATE_IDENTIFIER` | replace tuple with exact phase-8 and phase-9 support declarations sharing the primary identifier |
| `events.order_event_keys` | `PHASE_PREDECESSOR_MISMATCH` | append increasing key `1` while retaining `NOT_APPLICABLE` predecessor |
| `events.validate_phase_commit_record` | `PHASE_COMMIT_RECORD_INVALID` | make the phase-1 physical-record reference applicable |
| `events.validate_phase_commit_record` | `PHASE_PREDECESSOR_MISMATCH` | replace expected predecessor with exact digest `sha256:2222…2222` |
| `ownership.validate_update_ownership` | `UPDATE_OWNERSHIP_CLAIM_INVALID` | change first EventKey primary identity to object-b while owner remains object-a |
| `ownership.validate_update_ownership` | `INFORMATIONAL_MEMORY_OWNERSHIP_FORBIDDEN` | replace kind with `INFORMATIONAL_POLICY_MEMORY` |
| `ownership.validate_update_ownership` | `UPDATE_OWNERSHIP_CONFLICT` | append exact owner-b claim at the same locus |
| `ownership.validate_update_ownership` | `OWNERSHIP_ORDER_INVALID` | prepend exact owner-b/locus-01 claim before the smaller baseline claim |
| `ownership.validate_update_ownership` | `PHASE_OWNERSHIP_MISMATCH` | replace first claim phase with `PHASE_2` while its EventKey stays `PHASE_1` |
| `durability.build_atomic_commit_request` | `ATOMIC_COMMIT_REQUEST_INVALID` | replace attempt ordinal with `-1` |
| `durability.build_atomic_commit_request` | `PHYSICAL_PHASE_TRANSACTION_INVALID` | replace physical transaction trace digest with `sha256:2222…2222` |
| `durability.validate_policy_memory_transaction` | `I5_RECORD_FORMATION_INVALID` | replace `decision_ref` with exact wrong-type string |
| `durability.validate_policy_memory_transaction` | `POLICY_MEMORY_TRANSACTION_INVALID` | make only `next_memory_hash` applicable |
| `durability.validate_atomic_commit_outcome` | `EXPECTED_TRACE_PREFIX_MISMATCH` | replace request expected prefix with `sha256:2222…2222` |
| `durability.validate_atomic_commit_outcome` | `COMMIT_REJECTED` | replace outcome with exact baseline-bound rejection support |
| `durability.validate_atomic_commit_outcome` | `COMMIT_AMBIGUOUS` | replace outcome with exact baseline-bound ambiguity having one evidence ref |
| `durability.validate_atomic_commit_outcome` | `DURABILITY_UNAVAILABLE` | replace outcome with exact baseline-bound unavailable support |
| `durability.validate_atomic_commit_outcome` | `DURABILITY_EVIDENCE_MISSING` | exact constructor map removes phase evidence from committed evidence or evidence refs from ambiguity; recompute only committed evidence digest |
| `durability.validate_atomic_commit_outcome` | `DURABILITY_EVIDENCE_INCONSISTENT` | replace evidence request with object-b and recompute evidence digest |
| `traces.project_canonical_trace_row` | `TRACE_ROW_INVALID` | replace event key with `NOT_APPLICABLE` in an event row |
| `traces.project_canonical_trace_row` | `TRACE_ROW_PREDECESSOR_MISMATCH` | give row zero exact predecessor digest `sha256:2222…2222` |
| `traces.build_trace_prefix` | `TRACE_ROW_GAP` | change the exact source row to index `1`, bind omitted row-zero predecessor, and recompute row digest/frame |
| `traces.build_trace_prefix` | `TRACE_PREFIX_INVALID` | retain valid literal bytes but replace their supplied row digest with `sha256:2222…2222` |
| `traces.build_trace_prefix` | `TRACE_PREFIX_NOT_LITERAL` | replace sole frame bytes with exact empty bytes |
| `traces.extend_trace_prefix` | `TRACE_PREFIX_MUTATION_FORBIDDEN` | replace appended predecessor with `sha256:2222…2222` and recompute row digest/frame |
| `traces.extend_trace_prefix` | `TRACE_EXTENSION_IDENTITY_INVALID` | replace appended tuple with exact empty tuple |
| `traces.extend_trace_prefix` | `TRACE_ROW_GAP` | change appended source row index to `2` and recompute row digest/frame |
| `traces.validate_complete_trace_evidence` | `TRACE_COMPLETENESS_INVALID` | replace confirmed row count with `0` |
| `traces.validate_complete_trace_evidence` | `TRACE_EQUIVOCAL` | replace last-prefix digest with `sha256:2222…2222` |
| `traces.validate_complete_trace_evidence` | `TRACE_EVIDENCE_MISSING` | remove the sole literal frame bytes while retaining claimed metadata |
| `traces.validate_complete_trace_evidence` | `MINIMUM_TRACE_INCOMPLETE` | construct an exact phase-commit row without reconstruction refs and recompute row, frame, prefix, and evidence bindings |
| `traces.build_run_trace_envelope` | `RUN_TRACE_ENVELOPE_INVALID` | make execution binding applicable while identity remains `NOT_APPLICABLE` |
| `faults.validate_inert_fault_hook` | `FAULT_HOOK_INVALID` | make only hook applicability `APPLICABLE`; no schedule or delivery reference is supplied |

Eight stored negative controls fail closed for an unknown baseline, unknown operand, missing coordinate, duplicate coordinate, nonexistent path, unresolved token, undeclared recomputation dependency, and runtime-choice instruction.

### 10.2 Reachability correction and precedence proofs

Failure precedence selects the first failure only after predicates are true; it does not prove that arbitrary predicate pairs can coexist. A `MULTIPLE_ACTIVE_PRECEDENCE` vector is admissible only when one closed deterministic effective input proves every listed predicate simultaneously true. Production precedence is unchanged.

The prior `i5v-127` pair was impossible because a predecessor-rejecting mutation needs a nonempty appended row while extension identity requires empty or byte-identical growth. The authorized correction keeps owner, expected `TRACE_PREFIX_MUTATION_FORBIDDEN`, owner-derived FailureId, class, completed-check count, and all zero counters, but replaces the second predicate with later `TRACE_ROW_GAP`. Its exact final witness leaves the accepted prefix valid, supplies one nonempty structurally valid appended frame at row index `2`, sets predecessor digest `sha256:2222…2222` rather than the accepted terminal digest, and recomputes row digest then frame bytes. Mutation and gap are both true; formation, prefix-invalid, and extension-identity are false. Individual coverage remains at `i5v-053` for mutation, `i5v-054` for extension identity, `i5v-050` for row gap, and `i5v-126` for gap-before-prefix-invalid. Predicate counts change only from extension identity 2→1 and row gap 2→3; the total stays 116 with 42 unique predicates.

All 12 multiple-precedence vectors are jointly reachable:

| Vector | Simultaneously true predicates | Closed joint witness and first result |
|---|---|---|
| `i5v-117` | key invalid + duplicate | three equal keys with sequence `-1`; key invalid first |
| `i5v-118` | duplicate + order invalid | final sequence `1,0,0,0` with relinked predecessors; duplicate first |
| `i5v-119` | phase record invalid + predecessor mismatch | applicable phase-1 physical ref and different expected predecessor; record invalid first |
| `i5v-120` | ownership claim invalid + conflict | first event/owner mismatch plus distinct owners on locus `00`; claim invalid first |
| `i5v-121` | informational ownership + conflict | informational owner-a claim and owner-b claim on locus `00`; informational exclusion first |
| `i5v-122` | ownership order invalid + phase mismatch | reversed disjoint claims and first claim phase/event-key disagreement; order invalid first |
| `i5v-123` | expected prefix mismatch + rejection | changed current expected prefix plus rejection preserving immutable baseline prefix; mismatch first |
| `i5v-124` | ambiguity + evidence missing | exact ambiguity with empty evidence refs; ambiguity first |
| `i5v-125` | formation invalid + policy-memory invalid | wrong decision-ref type plus before/after applicability mismatch; formation first |
| `i5v-126` | row gap + prefix invalid | valid literal row `1` plus deliberately mismatched supplied row digest; gap first |
| `i5v-127` | prefix mutation + row gap | valid appended row `2` with wrong accepted-prefix predecessor; mutation first |
| `i5v-128` | completeness invalid + evidence missing | confirmed count `0` plus absent literal bytes for claimed row; completeness first |

### 10.3 Independent static reconstruction

Two separately implemented materializers—one duplicate-rejecting Python normalized-call interpreter and one Node iterative expression reducer—independently reconstructed the same 140 stored-order effective-input rows, 60 coordinate-resolution rows, 140 first-result rows, 104 non-`NOT_APPLICABLE` FailureIds, predicate rows, call rows, and witness rows. Both obtained 111 dynamic owners, 29 static witnesses, 116 predicate activations, and 253 completed checks. All eight negative controls failed closed. Separately, `git ls-tree`/`git cat-file` reconstruction and `git archive`/independent blob hashing reconstructed all 273 predecessor rows and both stored predecessor projections exactly. Neither validation route imported or executed framework modules.

| Projection | Canonical bytes | SHA-256 |
|---|---:|---|
| vectors | 112376 | `7d6ec486ba0b8d17152734789ea868abf58fdb5468d39898cf19b609bdafea8c` |
| effective inputs | 237247 | `ca871a8fcc9c695f70ea618a802b77d3bf1d26e86386e90ac8614f085a05db04` |
| closed-variant invocations | 10192 | `6b5cd0b45d52df1a98671cb4ab10b9573775418ff0d816a666e66d5f47cbe99e` |
| expected results | 18168 | `6d171e5d9f1632692fd40f6e52823a4b81b6db1120a5b8fa065255baafd12efd` |
| predicates | 9804 | `b22f24ed1e4e24d3c0df3801a1b63de79f0ad504d96734c059114661aa2982e4` |
| call counts | 17435 | `464033cb03eff607ae6aa96e0be61a60f36fe7de995dd379d3320ca7f413a2f9` |
| owner and joint witnesses | 13861 | `c9f5be034c7c98d660f3987ce50e540a76a1b371a7a890abd237139a49460b4e` |
| independently derived FailureIds | 13314 | `4c1cf99d42b95424bde8d9f779bd0ec302b4237ba9c912c84644036559cd940d` |

## 11. UQ-26, UQ-29, and DC25

**UQ-26:** I-5 freezes abstract atomic grouping; coupling among physical phase, policy decision, next memory, ledger evidence, ownership, and trace; expected-prefix/predecessor requirements; typed outcomes; failure-prefix preservation; ambiguous classification; and a recovery-evidence boundary. Backend selection, filesystem/database/distributed durability, real crash consistency, recovery implementation, and deployment remain open. No backend is accepted.

**UQ-29:** I-5 freezes the minimum data-minimized records and literal prefix bytes needed for the eight inert reconstruction determinations. It deliberately excludes unnecessary domain and sensitive data. Later scientific replay payload requirements remain open.

**DC25:** Durable receipt/trace mechanics are separate from later correction authority and later publication semantics. I-5 never mutates or reinterprets an accepted historical trace. Corrections must be separate linked records under later authority; finalization, recovery behavior, and publication remain I-8 concerns.

## 12. Guarantees and nonclaims

The mechanical guarantees are conditional: valid exact records have a deterministic total key order; exact opaque claims have a deterministic first conflict; literal prefix checking detects byte mutation, gaps, predecessor mismatch, and empty extension claims; and the abstract transaction schema requires the named facts to share one outcome. These are mathematical/data-structure consequences of frozen projections and validation order, not empirical findings.

This package does not establish physical correctness of a domain model; existence or uniqueness of scientific dynamics; optimality; causality; settlement fairness; empirical validity; production durability; crash safety of a real backend; distributed consensus; fault-injection semantics; stochastic behavior; route behavior; recovery, correction, finalization, or publication implementation; or a scientific result.

It also implements no transformation, policy, state advancement, world/domain model, schedule, runner, trajectory, backend, durability store, fault delivery, simulation, or experiment behavior. No book, manuscript, image, rendering, or published artifact is produced.

## 13. Exact lifecycle

1. I-5 authority drafting
2. independent authority audit
3. authority feature commit and push
4. independent authority integration
5. separate I-5 implementation
6. independent implementation audit and feature push
7. independent implementation integration
8. clean full framework discovery and I-5 evidence
9. only then I-6 authority

No step authorizes its successor. This candidate completes only step 1 if independently accepted as a draft. Independent authority audit is the next possible stage and has not begun.

## 14. Candidate completion condition

A conforming drafting checkout leaves HEAD at the accepted base, the index empty, every tracked path unchanged, and exactly the five named authority files untracked/unstaged. Static checks may parse, hash, count, inspect Git, and parse source AST. They may not import `ebu_framework`, run project tests, construct prospective runtime declarations, invoke a model/policy/runner/Gate, advance state, simulate, render, recover, finalize, or publish.
