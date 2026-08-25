# Unified Python Research Framework I-8 Provenance, Recovery, and Publication Authority Amendment

## Accepted coordinate and authority

This is a prospective, unaudited Authority-drafting candidate on `framework/i-8-provenance-recovery-publication-authority`. The sole starting commit is `83fd6040fde6d72ab0e938ab72c38f9246520b58` with tree `8867d3a8a952a12c72ff4bd6bc29b1dcfa8ce0a0`. Local `framework-v0.1`, `origin/framework-v0.1`, and a fresh live `origin` query all resolve to that commit. I-7 authority and implementation are accepted and unchanged. Repository bytes and the repository-local `ebu-framework` Authority-drafting profile govern.

This package creates documentation and mechanical contracts only. It authorizes no implementation, project test, scientific/model behavior, result, finalization, recovery, publication, correction decision, commit, push, merge, release, or I-9 work.

## Purpose and positive value

I-8 gives the project a reproducible evidence boundary: source and runtime facts are recorded at the layer where they matter; full traces, durable prefixes, run envelopes, artifacts, and manifests keep distinct identities; recovery can restore only proven identical bytes; publication is exercised safely in an inert write-once store; and corrections append linked facts without rewriting scientific history.

The value is durable auditability, not a claim that a model is true. A complete inventory helps another reader reproduce evidence; it does not certify causality, empirical validity, institutional approval, or a real backend's crash safety.

## Controlling locks and precedence

The mechanical contract locks 62 accepted authority/governance sources. Its lock projection is 11563 bytes with SHA-256 `36c6d5b7f991e1103dccfdcc75f497317cfcc347c9034210775a927ce7994d5b`. The predecessor manifest reconstructs every one of the 312 accepted paths by two independent routes.

Precedence is accepted predecessor bytes and narrow repairs; accepted specification/plan assignments; accepted I-4 authorization; accepted I-5 trace/durability/recovery evidence and DC25; accepted I-6/I-7 additive compatibility; then this exact I-8 suffix. A genuine conflict or missing authority stops work.

## Conceptual and type boundaries

The following are not interchangeable:

- source inventory: exact commit, source refs, raw SHA-256 values, and artifact-byte hashes;
- runtime/environment inventory: pinned dependencies/interpreter/OS/arithmetic/concurrency/allowlist and separate run observations;
- execution semantics: every fact able to change scientific behavior;
- run metadata: identity, host, clock, path, storage, logs, trust evidence, publication facts, and operational interruption that cannot select science;
- artifact content: exact immutable bytes plus an `ArtifactRecord`;
- full trace, prefix, and run envelope: distinct types, domains, and completeness meanings;
- finalization: validation of already supplied evidence, never row/result generation;
- recovery: evidence-classified same-bytes reconstruction, never execution;
- publication fact and correction record: separate immutable facts linked to the unchanged manifest/history.

`COMPLETE`, `PARTIAL`, `UNRESOLVED`, and `NOT_APPLICABLE` remain typed states. The accepted manifest uses `ResolutionState.PRESENT` as its complete arm; I-8 names that semantic arm `COMPLETE_AS_RESOLUTION_PRESENT` without changing the I-3 field. None of these states becomes zero, empty, `null`, omission, or success.

## Exact public and private surface

The accepted 419-name root is preserved and receives exactly 25 names, producing 444. The accepted 256-code failure prefix is preserved and receives exactly 24 codes, producing 280.

| Owner | Public type | Exact shape/boundary |
|---|---|---|
| `experiment` | `RuntimeMetadata` | `execution_identity: ExecutionIdentity`; `run_identity_ref: ObjectRef`; `authorization_use_ref: ObjectRef`; `wall_clock_evidence_ref: ObjectRef|Applicability`; `host_process_evidence_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `storage_evidence_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `diagnostic_evidence_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `completeness: ResolutionDetail` |
| `artifacts` | `ResultArtifact` | `artifact_record: ArtifactRecord`; `scientific_payload_ref: ObjectRef`; `trace_payload_or_prefix_ref: ObjectRef`; `run_envelope_ref: ObjectRef`; `runtime_metadata_ref: ObjectRef`; `derivation_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `scientific_completeness: ResolutionDetail` |
| `artifacts` | `SummaryArtifact` | `artifact_record: ArtifactRecord`; `ordered_source_result_refs: tuple[ObjectRef,...]/SEMANTIC_SEQUENCE`; `analysis_code_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `derivation_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `completeness: ResolutionDetail` |
| `artifacts` | `FigureArtifact` | `artifact_record: ArtifactRecord`; `ordered_source_result_or_summary_refs: tuple[ObjectRef,...]/SEMANTIC_SEQUENCE`; `figure_code_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `evidence_label: Literal[SCHEMATIC,MATHEMATICALLY_DERIVED,TESTED_IMPLEMENTATION,OBSERVED_REGISTERED_RUN,RESEARCH_HYPOTHESIS,INSTITUTIONAL_DESIGN_CHOICE]`; `completeness: ResolutionDetail` |
| `artifacts` | `PublicationRecord` | `envelope: CommonObjectEnvelope`; `manifest_ref: ObjectRef`; `authorization_ref: ObjectRef`; `authorization_validation_ref: ObjectRef`; `authorization_use_ref: ObjectRef`; `ordered_published_artifact_refs: tuple[ObjectRef,...]/SEMANTIC_SEQUENCE`; `ordered_published_artifact_byte_hashes: tuple[ArtifactByteHash,...]/SEMANTIC_SEQUENCE`; `publisher_identity_ref: ObjectRef`; `destination_content_addresses: tuple[str,...]/SEMANTIC_SEQUENCE`; `publication_time_evidence_ref: ObjectRef|Applicability`; `publication_receipt_ref: ObjectRef`; `completeness: ResolutionDetail` |
| `artifacts` | `CorrectionRecord` | `envelope: CommonObjectEnvelope`; `original_artifact_or_manifest_ref: ObjectRef`; `replacement_artifact_or_manifest_ref: ObjectRef`; `correction_scope_ref: ObjectRef`; `reason_ref: ObjectRef`; `method_ref: ObjectRef`; `authorization_ref: ObjectRef`; `authorization_validation_ref: ObjectRef`; `authorization_use_ref: ObjectRef`; `scientific_execution_repeated: bool`; `prior_publication_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `new_manifest_ref_or_not_applicable: ObjectRef|Applicability`; `evidence_ledger_relation_ref: ObjectRef`; `completeness: ResolutionDetail` |
| `provenance` | `SourceProvenance` | `repository_identity_ref: ObjectRef`; `source_commit: str/LOWER_HEX40`; `ordered_source_refs: tuple[ObjectRef,...]/SEMANTIC_SEQUENCE`; `ordered_source_raw_sha256: tuple[SourceFileRawSha256,...]/SEMANTIC_SEQUENCE`; `ordered_source_artifact_byte_hashes: tuple[ArtifactByteHash,...]/SEMANTIC_SEQUENCE`; `dirty_source_state: Literal[FORBIDDEN]`; `completeness: ResolutionDetail` |
| `provenance` | `RuntimeProvenance` | `interpreter_ref: ObjectRef`; `dependency_closure_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `os_architecture_contract_ref: ObjectRef`; `numerical_hardware_backend_ref_or_not_applicable: ObjectRef|Applicability`; `arithmetic_contract_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `concurrency_contract_ref: ObjectRef`; `entry_semantics_ref: ObjectRef`; `fault_delivery_contract_ref_or_not_applicable: ObjectRef|Applicability`; `stochastic_contract_ref_or_not_applicable: ObjectRef|Applicability`; `included_property_classes: tuple[str,...]/SECTION7_INCLUDED_ORDER`; `completeness: ResolutionDetail` |
| `provenance` | `EnvironmentProvenance` | `normalized_allowlist_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `operational_exclusion_refs: tuple[ObjectRef,...]/CANONICAL_REF`; `blocked_nonread_property_names: tuple[str,...]/CODEPOINT_ORDER`; `run_specific_property_classes: tuple[str,...]/SECTION7_RUN_METADATA_ORDER`; `run_specific_evidence_refs: tuple[ObjectRef,...]/SEMANTIC_SEQUENCE`; `completeness: ResolutionDetail` |
| `provenance` | `ExecutionSemanticsProjection` | `accepted_configuration_ref: ObjectRef`; `binding: ExecutionBinding`; `execution_semantics_hash: ExecutionSemanticsHash`; `source_provenance_ref: ObjectRef`; `runtime_provenance_ref: ObjectRef`; `environment_provenance_ref: ObjectRef`; `included_property_classes: tuple[str,...]/SECTION7_INCLUDED_ORDER`; `excluded_run_metadata_classes: tuple[str,...]/SECTION7_RUN_METADATA_ORDER` |
| `recovery` | `RecoveryClassification` | NO_DURABLE_EXECUTION_RECEIPT, RECOVERED_IDENTICAL, PARTIAL_DURABLE_PREFIX, NO_DURABLE_TRACE, UNRESOLVED_DURABILITY, PUBLICATION_INCOMPLETE |
| `recovery` | `RecoveryRecord` | `classification: RecoveryClassification`; `manifest_ref: ObjectRef`; `artifact_ref: ObjectRef`; `artifact_byte_hash: ArtifactByteHash`; `trace_prefix_hash: CanonicalTracePrefixHash`; `run_envelope_digest: RunEnvelopeDigest`; `execution_identity: ExecutionIdentity`; `authorization_validation_ref: ObjectRef`; `authorization_use_ref: ObjectRef`; `destination_content_address: str`; `destination_prior_hash_or_not_applicable: ArtifactByteHash|Applicability`; `recovered_artifact_ref: ObjectRef`; `completeness: ResolutionDetail` |
| `publication` | `WriteOnceStore` | `observe(content_address: str, /) -> bytes|Applicability`; `put_if_absent_or_identical(content_address: str, artifact_bytes: bytes, /) -> PublicationReceipt` |
| `publication` | `PublicationReceipt` | `receipt_ref: ObjectRef`; `content_address: str`; `artifact_byte_hash: ArtifactByteHash`; `prior_state: Literal[ABSENT,SAME_BYTES]`; `write_outcome: Literal[WRITTEN_ONCE,ALREADY_IDENTICAL]`; `stored_byte_count: int` |

| Class | Owner and exact signature | No-bypass boundary |
|---|---|---|
| `T0` | `provenance.classify_execution_runtime_property(property_class: str, /) -> Literal['EXECUTION_SEMANTICS','RUN_METADATA']` | exact membership only; no alias, substring, default, or observation-dependent classification |
| `T1` | `traces.finalize_inert_trace_payload(trace_validation: TraceValidationResult, run_envelope: RunTraceEnvelopeV1, trace_artifact: ArtifactRecord, trace_bytes: bytes, /) -> ArtifactRecord` | validation namespace, dummy bytes, literal prefix, distinct run envelope, no row creation/state advance |
| `T3_GUARD` | `traces.finalize_trace_payload(*, trace_validation: TraceValidationResult, run_envelope: RunTraceEnvelopeV1, trace_artifact: ArtifactRecord, authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord) -> NoReturn` | fails before any backend, row creation, runner, model, policy, state, or filesystem call |
| `T1` | `publication.finalize_inert_manifest(expected_manifest_ref: ObjectRef, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], artifact_bytes: tuple[bytes,...], source: SourceProvenance, runtime: RuntimeProvenance, environment: EnvironmentProvenance, semantics: ExecutionSemanticsProjection, trace_validation: TraceValidationResult, run_envelope: RunTraceEnvelopeV1, authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord, /) -> ExecutionResultManifest` | calls accepted I-3 manifest validation, returns the identical immutable manifest object, and admits only synthetic dummy refs/bytes |
| `T3_GUARD` | `publication.finalize_execution_result_manifest(*, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord) -> NoReturn` | I-8 excludes real result/finalization; no runner/backend import exists |
| `T1` | `recovery.recover_inert_artifacts(manifest: ExecutionResultManifest, artifact: ArtifactRecord, artifact_bytes: bytes, destination_bytes_or_not_applicable: bytes|Applicability, trace_validation: TraceValidationResult, run_envelope: RunTraceEnvelopeV1, authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord, /) -> RecoveryRecord` | same supplied bytes only; never imports/calls execution and never writes a store |
| `T3_GUARD` | `recovery.recover_artifacts(*, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord) -> NoReturn` | UQ-26 guard; no AtomicStore method call and no runner/execution import |
| `T1` | `publication.create_inert_correction_record(candidate: CorrectionRecord, original: ArtifactRecord, replacement: ArtifactRecord, original_bytes: bytes, replacement_bytes: bytes, authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord, /) -> CorrectionRecord` | synthetic refs only, scientific_execution_repeated is false, original and history remain unchanged, no correction decision |
| `T3_GUARD` | `publication.create_correction_record(*, candidate: CorrectionRecord, original: ArtifactRecord, replacement: ArtifactRecord, authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord) -> NoReturn` | UQ-28 guard; does not classify, interpret, choose, rerun, or overwrite |
| `T1` | `publication.publish_inert_artifacts(store: _InertWriteOnceStore, candidate: PublicationRecord, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], artifact_bytes: tuple[bytes,...], authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord, /) -> PublicationRecord` | sealed in-memory store, exact content address, one interface call, unchanged manifest, separate record |
| `T3_GUARD` | `publication.publish_artifacts(*, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], authorization_validation: AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord) -> NoReturn` | UQ-27 guard; no network, filesystem destination, real store, backend bootstrap, or runner path |

The only new private stateful type is sealed `_InertWriteOnceStore`; it holds a private copy of dummy bytes in memory. It cannot be structurally substituted, subclassed, copied, pickled, persisted, or given a path/URI/socket/database/provider. The mechanical contract closes all private helper signatures.

## Deterministic provenance and finalization mechanics

Section 7 is closed over 16 execution-semantics classes and 12 run-metadata classes. `classify_execution_runtime_property` performs exact membership only. An unknown class, undeclared runtime read, unpinned dependency, or branch on run metadata fails before any scientific state advance.

`finalize_inert_trace_payload` validates an already supplied literal dummy prefix/full artifact against its byte hash and separate run envelope; it creates no row. `finalize_inert_manifest` calls the accepted I-3 manifest validator, checks exact bytes, provenance, execution-semantics hash, prefix/run binding, consumed authorization, and completeness, then returns the identical frozen manifest object. Publication or correction facts in that preimage fail.

The complete rule is:

\[
\operatorname{COMPLETE}(M) \Rightarrow \operatorname{missing}(M)=\varnothing \land \operatorname{trace}(M)=\mathrm{COMPLETE}.
\]

Any missing required artifact, hash mismatch, partial prefix, or absent terminal evidence makes `COMPLETE` false; the immutable manifest remains `PARTIAL` or `UNRESOLVED`.

## Same-bytes recovery

Recovery proves all four obligations: exact content identity, exact prefix/run/manifest binding, exact consumed authorization, and destination compatibility. It performs no write and has no import/call path to execution.

\[
H_{\mathrm{art}}(b_{\mathrm{source}})=h_{\mathrm{record}},\qquad b_{\mathrm{destination}}\in\{\mathrm{ABSENT},b_{\mathrm{source}}\}.
\]

Different destination bytes fail `ALREADY_EXISTS_DIFFERENT`; an ambiguous prefix fails `AMBIGUOUS_PREFIX`; missing/hash/run/authorization mismatches fail at their exact earlier precedence. Recovery never resets an invocation, fabricates a receipt, extends an ambiguous suffix, or calls a runner.

## Dummy write-once publication and correction

The dummy key is exactly `ArtifactByteHash(bytes)`. An absent key becomes `WRITTEN_ONCE`; an existing identical payload returns `ALREADY_IDENTICAL`; existing different bytes fail. The store is process-memory-only and produces a separate candidate `PublicationRecord` that references the unchanged manifest.

A correction is a new forward-time immutable fact and corrected-object relation. Forward-time means logical append order only: I-8 adds no clock, timestamp, current-time read, physical action, or resource field. It uses exact typed original/superseded and replacement/corrected `ObjectRef` values, different bytes, and the already-authorized reason, scope, authority, method, and scientific-execution-repetition fact, then appends a separate `CorrectionRecord`:

\[
\mathrm{history}_{\mathrm{after}}=\mathrm{history}_{\mathrm{before}}\mathbin{\|\!\|}\mathrm{CorrectionRecord}(r_{0},r_{1}),\quad r_{0}\ne r_{1}.
\]

The original action, result, artifact, manifest, figure, publication, claims, and physical history remain preserved; the new fact neither overwrites nor negates them. `CorrectionRecord` remains separate from `PublicationRecord`, immutable scientific/result manifests, recovery evidence, and any future physical `CorrectionActionReceipt`. The inert correction says `scientific_execution_repeated=false`; the general record reports whether repetition occurred but never authorizes it or selects a scientific conclusion, correction class, interpretation, physical action, or rerun. UQ-28 remains open.

Same-bytes recovery is restoration/reconstruction of already-durable evidence, not correction. Different bytes fail recovery and require separately authorized new corrected artifact/manifest relations; they never overwrite the recovered destination or historical object.

I-8 deliberately adds no declaration, field, vector, failure, path, or API for a physical `CorrectionActionReceipt`; physical correction-resource measurement; quote-to-actual residual/reconciliation; descendant traversal or delay-cost laws; Möbius coefficient recomputation; correction groups or interaction measurement; causal responsibility; settlement shares; penalties; appeals; fraud/negligence allocation; physical-literature claims; or scientific experiments. Exact `ObjectRef` extension plus separate future authority is sufficient. Any later correction-locality claim remains governed by the accepted Atomic F13 authority, including its exact distinction between the unrestricted raw upward-cone domain (including the empty set) and the normalized convention whose empty coefficient remains zero; this amendment neither reproduces nor extends that theorem.

## Failures, authorization, and precedence

| Ordinal | FailureCode | Meaning |
|---:|---|---|
| 257 | `I8_RECORD_FORMATION_INVALID` | An I-8 constructor or interface received a missing, extra, positional, or wrong-runtime-type field. |
| 258 | `SOURCE_RUNTIME_PROPERTY_OUTSIDE_SECTION7` | A supplied source/runtime/environment class is outside the closed plan section 7 classification. |
| 259 | `PROVENANCE_INVENTORY_INVALID` | A provenance inventory is unordered, duplicated, length-misaligned, dirty, incomplete, or layer-confused. |
| 260 | `EXECUTION_SEMANTICS_CLASSIFICATION_INVALID` | A science-affecting property was placed in run metadata or a run-only property was allowed to select science. |
| 261 | `TRACE_FINALIZATION_INVALID` | Trace/prefix/run-envelope facts do not form one exact inert finalization relation. |
| 262 | `MISSING_ARTIFACT` | A required exact artifact reference or byte payload is absent. |
| 263 | `MANIFEST_COMPLETENESS_INVALID` | A manifest completeness claim contradicts missing artifacts, trace completeness, or terminal/last-confirmed evidence. |
| 264 | `MANIFEST_MUTATION_FORBIDDEN` | Publication/correction facts or a changed preimage were presented as an in-place manifest update. |
| 265 | `AMBIGUOUS_PREFIX` | The supplied durable prefix has competing, equivocal, invalid, or unresolved evidence. |
| 266 | `RECOVERY_RUN_BINDING_MISMATCH` | Recovery evidence does not bind the exact manifest, prefix, run envelope, binding, and execution identity. |
| 267 | `RECOVERY_AUTHORIZATION_MISMATCH` | Consumed recovery authorization does not match operation, targets, configuration, binding, and execution identity. |
| 268 | `RECOVERY_EXECUTION_FORBIDDEN` | A recovery surface could reach execution, a runner, state advance, or scientific recomputation. |
| 269 | `ALREADY_EXISTS_DIFFERENT` | A content-addressed destination already holds different bytes. |
| 270 | `WRITE_ONCE_STORE_INVALID` | The inert store is not the exact sealed in-memory write-once implementation or violated its protocol. |
| 271 | `PUBLICATION_AUTHORIZATION_MISMATCH` | Consumed publication/finalization authorization does not match its exact operation and targets. |
| 272 | `PUBLICATION_RECORD_INVALID` | A separate publication record or receipt does not match the unchanged manifest and exact published bytes. |
| 273 | `CORRECTION_AUTHORIZATION_MISMATCH` | Consumed correction authorization does not match the original and proposed replacement targets. |
| 274 | `CORRECTION_AS_OVERWRITE_FORBIDDEN` | A correction attempts to reuse identity/bytes or replace historical artifact, manifest, figure, or publication facts. |
| 275 | `CORRECTION_RECORD_INVALID` | A correction record does not preserve and link the exact original and replacement evidence. |
| 276 | `REAL_FINALIZATION_AUTHORITY_UNAVAILABLE` | Production/scientific finalization is outside the inert I-8 implementation authority. |
| 277 | `REAL_RECOVERY_BACKEND_UNAVAILABLE` | UQ-26 leaves real execution-store recovery unavailable. |
| 278 | `REAL_PUBLICATION_BACKEND_UNAVAILABLE` | UQ-27 leaves real publication-store operation unavailable. |
| 279 | `REAL_CORRECTION_AUTHORITY_UNAVAILABLE` | UQ-28 leaves real correction classification and decision authority unavailable. |
| 280 | `I8_HASH_COLLISION` | Two distinct I-8 validation coordinates derived one FailureId or two distinct projected records derived one forbidden identity. |

I-8 reuses the accepted I-4 operations and exact targets. Validation and consumed-use records must agree on use key, operation, targets, configuration, binding, and execution identity. Synthetic construction in a T1 vector is validation material only and cannot mint production authority.

Every failing vector freezes one complete `FailureId` coordinate at stage I-8, owner version 1.0.0, empty object-ref tuple, `NOT_APPLICABLE` event key, and the first active predicate ordinal. No alias, default, object substitution, or later failure may replace the first owner.

## Validation vectors

The validation contract freezes 150 vectors: 130 exact single-owner dynamic materializations and 20 static witnesses. Outcomes are `{"FAILURE": 75, "STATIC_PASS": 20, "SUCCESS": 55}`. Dynamic owner calls total 130; completed checks total 446; active predicates total 90. Runner, model, policy, state-advance, network, and filesystem-publication-write counts are all zero.

The canonical vector bytes are 362048 bytes with SHA-256 `71bfc2db820b84e2d86ba6f57b44deb689da0222c6bd373b3ec24698b39e2c44`. Every non-static vector constructs support, applies exact mutations, and calls its exact production/private owner once. Static witnesses name an AST/source/JSON/Git/hash/path proof and call no representative interface.

Negative controls include ambiguous prefix, missing artifact, hash mismatch, different destination bytes, unauthorized publication, property outside section 7, partial manifest falsely complete, manifest mutation, runner/execution reachability, and correction as overwrite. All vector inputs use the embedded dummy bytes; no real store is written.

## Closed implementation path

A later separately authorized implementation may touch exactly 19 paths: 4 new, 5 production modifications, and 10 compatibility-only test reconciliations.

| State | Path | Owner | Purpose |
|---|---|---|---|
| `NEW` | `src/ebu_framework/provenance.py` | `I8_PROVENANCE_OWNER` | Own four exact provenance records, the closed section-7 classifier, and pure supplied-value projection validation. |
| `NEW` | `src/ebu_framework/recovery.py` | `I8_RECOVERY_OWNER` | Own evidence classification, same-bytes inert recovery, and the no-real-backend T3 guard; no execution edge. |
| `NEW` | `src/ebu_framework/publication.py` | `I8_PUBLICATION_OWNER` | Own inert manifest finalization, sealed in-memory write-once publication, correction relations, separate receipts/records, and real-operation guards. |
| `NEW` | `tests/framework/test_artifact_recovery_publication.py` | `I8_T1_TEST_OWNER` | Materialize the exact V10 dummy-byte vectors and V11 static witnesses; never write a real store or import execution. |
| `MODIFIED` | `src/ebu_framework/__init__.py` | `I8_ROOT_EXPORT_SUFFIX_OWNER` | Append the exact 25-name I-8 public suffix after the accepted 419-name root prefix. |
| `MODIFIED` | `src/ebu_framework/artifacts.py` | `I8_ARTIFACT_RECORD_SUFFIX_OWNER` | Preserve accepted ArtifactRecord/ExecutionResultManifest/validator bytes semantically and append exactly five immutable record types plus private formation/projection helpers. |
| `MODIFIED` | `src/ebu_framework/errors.py` | `I8_FAILURE_SUFFIX_OWNER` | Append exactly 24 FailureCode members at ordinals 257-280; FailureStage.I8 already exists and remains unchanged. |
| `MODIFIED` | `src/ebu_framework/experiment.py` | `I8_RUNTIME_METADATA_SUFFIX_OWNER` | Append RuntimeMetadata only; preserve accepted configuration, binding, identity, validation, hashing, and UQ-36 projection behavior. |
| `MODIFIED` | `src/ebu_framework/traces.py` | `I8_TRACE_FINALIZATION_SUFFIX_OWNER` | Append two finalization callables; preserve all I-5 row/prefix/full/run identities and existing exports. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_atomic_declarations.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_bridge_exact_fixtures.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_capabilities.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_i3_integration.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_i3a_declarations.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_i3b_declarations.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_i3c_declarations.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_i3d_declarations.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_interaction_declarations.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |
| `COMPATIBILITY_ONLY_MODIFIED` | `tests/framework/test_primitives_envelopes.py` | `ADDITIVE_INVENTORY_RECONCILIATION` | Replace only stale I-7 terminal failure/root/module/signature/import counts/hashes with I-8 manifest projections; preserve every accepted test case, assertion meaning, fixture, and execution class. |

The future graph has 39 modules, 243 direct edges, and 0 cycles. Provenance, recovery, publication, and trace finalization have no execution edge. `hashing.py`, `identity.py`, dependencies, fixtures, I-9/CI, manuscripts, books, PDFs, results, models, providers, runners, and every unlisted path are prohibited.

## Teaching traceability

### 1. Source/runtime/run-metadata separation

**Plain meaning:** Inputs that can change science are frozen into execution semantics; host names and clocks remain run facts.

**Positive value:** A later reader can tell what must match for replay without confusing it with where or when a run happened.

**Ordinary example:** A recipe's ingredient amounts affect the cake; the kitchen's street address identifies the occasion but should not change the recipe.

**Assumptions:** all result-producing reads are prospectively declared or blocked.

**Proof obligation:** `If property p can select value/branch/order/arithmetic/failure/row/terminal state, p is in S and enters H_sem; R is disjoint and cannot select science: S intersection R = empty.`

**Falsifier/refusal:** An unknown read, unpinned dependency, or branch on a run-metadata property fails before any state advance.

**Honest nonclaim:** Matching hashes does not prove the scientific model is true.

### 2. Immutable evidence

**Plain meaning:** Once an artifact or manifest is identified, later events point to it instead of editing it.

**Positive value:** The project keeps a durable audit trail of what was actually known and recorded at each stage.

**Ordinary example:** A signed receipt stays unchanged; a later note is stapled beside it rather than erasing the original total.

**Assumptions:** accepted object refs and byte hashes are collision-free for the observed corpus.

**Proof obligation:** `ObjectRef=(id,version,H_content) and ArtifactByteHash=H_art(bytes); changing content or bytes requires a new identity/version/hash.`

**Falsifier/refusal:** Any attempt to place destination, receipt, publication time, or correction fact into the prior manifest fails.

**Honest nonclaim:** Immutability does not certify institutional endorsement or scientific truth.

### 3. Partial versus complete manifest

**Plain meaning:** A checklist missing a required item remains partial or unresolved; it is never treated as complete because an empty placeholder exists.

**Positive value:** Downstream readers can safely distinguish usable complete evidence from honestly incomplete evidence.

**Ordinary example:** A moving inventory with three of four boxes checked is partial even if the unchecked box's line is blank.

**Assumptions:** required artifact kinds and trace completeness were fixed prospectively.

**Proof obligation:** `COMPLETE implies missing_required = empty and trace=COMPLETE; missing_required != empty implies manifest in {PARTIAL,UNRESOLVED}.`

**Falsifier/refusal:** A PRESENT/complete manifest with a missing artifact, mismatched hash, partial prefix, or absent terminal evidence fails.

**Honest nonclaim:** A complete manifest proves inventory closure, not correctness of its scientific conclusion.

### 4. Same-bytes recovery

**Plain meaning:** Recovery can reattach only the exact bytes already evidenced for the exact run and prefix; different bytes belong to a separately authorized corrected-object relation.

**Positive value:** Operational restoration cannot quietly become a rerun, scientific recomputation, correction, or overwrite.

**Ordinary example:** Restoring a scanned contract is acceptable only when every byte matches the recorded fingerprint; a retyped version is a different document.

**Assumptions:** exact manifest/artifact/prefix/run/authorization evidence is supplied.

**Proof obligation:** `H_art(source)=recorded_hash and destination is absent or destination_bytes=source_bytes; recovered_ref=original_ref.`

**Falsifier/refusal:** Missing artifact, hash mismatch, ambiguous prefix, wrong run, wrong authority, or different destination bytes fails.

**Honest nonclaim:** I-8 proves no real crash consistency because UQ-26 remains open.

### 5. Write-once dummy publication

**Plain meaning:** The inert store writes an absent content-address once, accepts already identical bytes, and refuses different bytes.

**Positive value:** Publication evidence can be tested without risking an external destination or rewriting an artifact.

**Ordinary example:** A locker numbered by a package fingerprint may be filled once; the same package can be confirmed, but a different package cannot replace it.

**Assumptions:** the store is the sealed in-memory dummy type; authorization targets match.

**Proof obligation:** `key=H_art(bytes); put(key,b)=WRITTEN_ONCE if absent, ALREADY_IDENTICAL if stored=b, otherwise ALREADY_EXISTS_DIFFERENT.`

**Falsifier/refusal:** A structural store substitute, wrong key/hash, wrong authorization, different bytes, or mismatched receipt fails.

**Honest nonclaim:** No network/filesystem destination, durable backend, mirror, or production publication protocol is accepted.

### 6. Non-destructive correction

**Plain meaning:** A correction is a new forward-time linked fact and corrected object relation, never an eraser, negation, recovery operation, or physical-history rewrite.

**Positive value:** The framework preserves what was originally known, shows what changed and why, supports reproducible audit, and supplies an immutable substrate for a separately authorized later correction-feedback programme.

**Ordinary example:** A newspaper posts an erratum that names yesterday's article; it does not replace every archived copy as though the error never existed.

**Assumptions:** only dummy artifacts are used; UQ-28 authority/classification remains unresolved.

**Proof obligation:** `history_after = history_before || CorrectionRecord(original_ref,replacement_ref), with original_ref != replacement_ref and H(original_bytes) != H(replacement_bytes).`

**Falsifier/refusal:** Same ref, same bytes, wrong authority, wrong link, claimed rerun, or history mutation fails.

**Honest nonclaim:** The record does not choose a correction class, scientific conclusion, interpretation, rerun decision, physical action, resource measurement, causal responsibility, or settlement consequence.

## Open questions and nonclaims

UQ-26 still blocks real recovery against an execution store and any claim of real crash consistency. UQ-27 still blocks a real publication store, destination, receipt protocol, or production bootstrap. UQ-28 still blocks correction authority/classification/decision workflow. UQ-29/UQ-30 remain open for study-specific trace/privacy/restricted provenance. UQ-36 is enforced only within the accepted section-7 closed-world assumptions. DC25 remains exact: durability, correction, and publication are separate, and historical evidence is not reinterpreted or mutated.

This package claims reproducible evidence mechanics, durable audit structure under exact bytes, non-rewriting scientific history, and safe separation of dummy publication/correction facts. It does not claim real backend durability, distributed consensus, crash safety, scientific truth, causal identification, fair settlement, empirical success, external publication, or institutional endorsement.

## Handoff

A conforming drafting checkout remains at the accepted HEAD/tree, has an empty index and no tracked modifications, and contains exactly these five untracked files. Static validation may parse, hash, reconstruct Git objects, inspect AST/source text, and simulate the prospective materialization contract. It may not import framework/provider modules, run project tests, construct real scientific objects, execute, recover, finalize, publish, correct, render, or start I-9.

The next possible stage is an independent audit of exactly this five-file authority package. No implementation or later stage has begun.

READY_FOR_INDEPENDENT_FRAMEWORK_I8_PROVENANCE_RECOVERY_PUBLICATION_AUTHORITY_AUDIT
