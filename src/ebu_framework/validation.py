"""Private inert Framework I-9 implementation-audit validators."""

from __future__ import annotations

from . import canonical as _canonical
from . import numeric as _numeric
from .identity import SourceFileRawSha256
from . import hashing as _hashing
from . import primitives as _primitives
from . import capabilities as _capabilities
from .capabilities import T2FixtureCapability
from . import errors as _errors


_VALIDATION_GROUPS = (('V0',
  'T0',
  ('pinned Unicode asset hashes and complete Unicode 15.0 normalization',
   'strict ECJ-1 bytes, ordering, escaping, integer and rejection vectors',
   'host Unicode, ICU, locale and network non-reachability'),
  ('object acceptance', 'policy', 'transition', 'host normalization'),
  ('tests/framework/test_ecj1.py',)),
 ('V1',
  'T0_T1',
  ('all named hash domains, frames, preimages and exclusions',
   'raw-source and canonical identity distinction',
   'synthetic temporary-registry idempotency and collision checks'),
  ('scientific registry', 'registered configuration', 'scientific execution'),
  ('tests/framework/test_hash_preimages.py',
   'tests/framework/test_identity_registry.py')),
 ('V2',
  'T0',
  ('complete accepted numeric fixture and operation matrix',
   'primitive compatibility, conversion and lifecycle predicates',
   'all declared precedence and multiply-invalid cases'),
  ('domain policy callback', 'host-float science', 'unit inference'),
  ('tests/framework/test_numeric.py', 'tests/framework/test_primitives_envelopes.py')),
 ('V3',
  'T0',
  ('all accepted I-3, D1, D2, atomic and interaction declarations',
   'configuration/binding split and settlement-causality repair',
   'static formation, projection and closed failure precedence'),
  ('model callback', 'state mutation', 'institutional default'),
  ('tests/framework/test_i3_integration.py',
   'tests/framework/test_i3a_declarations.py',
   'tests/framework/test_i3b_declarations.py',
   'tests/framework/test_i3c_declarations.py',
   'tests/framework/test_i3d_declarations.py',
   'tests/framework/test_atomic_declarations.py',
   'tests/framework/test_interaction_declarations.py')),
 ('V4',
  'T1',
  ('synthetic signatures, thresholds, delegation and revocation',
   'exact authorization targets and durable single-use conflict',
   'UQ-25 dependency and production-bootstrap static integrity'),
  ('production key', 'real stage authority', 'model entry'),
  ('tests/framework/test_authorization.py',
   'tests/framework/test_authorization_use.py')),
 ('V5',
  'T1',
  ('fabricated capability views and availability epochs',
   'forbidden traversal and read-set refusal',
   'stateless and stateful applicability'),
  ('scientific policy', 'registered world', 'live measurement'),
  ('tests/framework/test_capabilities.py',)),
 ('V6',
  'T0_T1',
  ('ten-phase constants and EventKey total order',
   'duplicate and ownership conflict refusal',
   'phase-8/phase-9 identifier non-duplication'),
  ('transition proposal', 'physical commit', 'state mutation'),
  ('tests/framework/test_event_ownership.py',)),
 ('V7',
  'T1',
  ('dummy atomic-store outcome classification',
   'immutable prefix framing and ambiguous commit handling',
   'policy-memory and physical-state transaction separation'),
  ('fault delivery', 'policy', 'state', 'runner'),
  ('tests/framework/test_inert_durability.py',)),
 ('V8',
  'T2',
  ('all M1-M9 fixture rows one at a time',
   'grouping, measurement, nonadditivity and named comparator outputs',
   'exact fixture authority hash and one-use capability'),
  ('trajectory', 'parameter search', 'causal inference', 'settlement choice'),
  ('tests/framework/test_bridge_exact_fixtures.py',)),
 ('V9',
  'T2',
  ('all six dynamic exact fixture rows one at a time',
   'capacity, queue, delay and route refusal identities',
   'no successor-to-predecessor chaining'),
  ('advance_epoch', 'route science', 'schedule comparison'),
  ('tests/framework/test_dynamic_static_identities.py',)),
 ('V10',
  'T1',
  ('dummy finalization, prefix, manifest and byte recovery',
   'write-once publication refusal and separate publication record',
   'non-destructive correction and I-8 provenance preservation'),
  ('result generation', 'analysis', 'real recovery', 'real publication'),
  ('tests/framework/test_artifact_recovery_publication.py',)),
 ('V11',
  'T0',
  ('source-text AST import/export/signature/hash/authority audit',
   'complete future path and acyclic import-graph closure',
   'forbidden reachability and zero scientific entry paths'),
  ('production import during AST audit',
   'dynamic import',
   'execution',
   'policy invocation',
   'state mutation',
   'runner finalizer result Gate network subprocess'),
  ('tests/framework/test_route_guards.py',
   'tests/framework/test_validation_reachability.py')))
_I9_IMPLEMENTATION_PATHS = ('.github/workflows/tests.yml',
 'src/ebu_framework/validation.py',
 'tests/framework/safety.py',
 'tests/framework/test_validation_reachability.py')
_I9_ROOT_EXPORTS = ('AccountingBoundary',
 'AliasRecord',
 'Applicability',
 'ArtifactByteHash',
 'AugmentedClosedLoopReplayStateHash',
 'AuthorizationUseKey',
 'Binary64BitsV1',
 'CanonicalBytes',
 'CanonicalScientificTracePayloadHash',
 'CanonicalTracePrefixHash',
 'CanonicalTraceRowHash',
 'CanonicalTraceState',
 'CanonicalizationVersion',
 'ClaimStatus',
 'ClockSystem',
 'CommonObjectEnvelope',
 'ComparisonResult',
 'CompatibilityResult',
 'Completeness',
 'ConversionRule',
 'CoreNumberV1',
 'DecimalV1',
 'Dimension',
 'DurabilityState',
 'Duration',
 'ECJ1Value',
 'Epoch',
 'ErrorBound',
 'ExactConversion',
 'ExecutionSemanticsHash',
 'FailureCode',
 'FailureEnvelope',
 'FailureEventKey',
 'FailureEvidenceRef',
 'FailureId',
 'FailureInterfaceRef',
 'FailureObjectRef',
 'FailureStage',
 'Horizon',
 'InformationViewHash',
 'Instant',
 'IntegerV1',
 'LifecycleStatus',
 'LifecycleTransition',
 'LifecycleValidationResult',
 'NamespaceEntry',
 'NamespaceRegistrySnapshot',
 'NumericalOperation',
 'NumericalPolicyV1',
 'NumericalResult',
 'NumericalVariant',
 'ObjectContentHash',
 'ObjectRef',
 'OperandValidationResult',
 'PolicyMemoryAdvance',
 'PolicyMemoryPayloadHash',
 'ProposalSetHash',
 'Quantity',
 'QuantityContext',
 'RationalV1',
 'RecordMetadata',
 'Region',
 'RegistryRecord',
 'RepresentedStateProjectionHash',
 'ResolutionDetail',
 'ResolutionRecord',
 'ResolutionState',
 'ResourceType',
 'RetryClass',
 'RuntimeConstraintSet',
 'ScientificId',
 'ScientificIdAllocationClaimV1',
 'ScientificStatusEffect',
 'SemanticVersion',
 'ServiceType',
 'SignConvention',
 'SourceFileRawSha256',
 'StateAdvance',
 'StatePayloadHash',
 'SupersessionRelation',
 'SupersessionValidationResult',
 'UncertaintyKind',
 'UncertaintyRecord',
 'Unit',
 '__version__',
 'allocate_scientific_id',
 'apply_exact_core_operation',
 'compute_artifact_byte_hash',
 'compute_augmented_replay_state_hash',
 'compute_canonical_trace_payload_hash',
 'compute_canonical_trace_prefix_hash',
 'compute_canonical_trace_row_hash',
 'compute_execution_semantics_hash',
 'compute_information_view_hash',
 'compute_object_content_hash',
 'compute_policy_memory_payload_hash',
 'compute_proposal_set_hash',
 'compute_represented_state_projection_hash',
 'compute_source_file_raw_sha256',
 'compute_state_payload_hash',
 'convert_quantity_exact',
 'decimal_to_rational_exact',
 'encode_ecj1',
 'normalize_core_number',
 'parse_ecj1',
 'parse_scientific_id',
 'parse_semantic_version',
 'register_draft',
 'resolve_alias',
 'resolve_ref',
 'validate_boundary_compatibility',
 'validate_clock_compatibility',
 'validate_conversion_rule',
 'validate_dimension_compatibility',
 'validate_horizon',
 'validate_lifecycle_transition',
 'validate_numerical_policy',
 'validate_object_envelope',
 'validate_quantity',
 'validate_region_compatibility',
 'validate_resolution_detail',
 'validate_resource_service_compatibility',
 'validate_sign_convention_compatibility',
 'validate_supersession_relation',
 'validate_time_basis',
 'validate_uncertainty_record',
 'validate_unit_compatibility',
 'SystemState',
 'RepresentedState',
 'ProjectionContract',
 'ConservationAccountLevel',
 'ConservationProfile',
 'ConservationProfileSelection',
 'ConservedQuantityDeclaration',
 'CoordinateCoefficient',
 'TransformationDeclarationKind',
 'InternalTransformationOrInvariantDeclaration',
 'BoundaryFlowDirection',
 'BoundaryFlowRollupRole',
 'BoundaryFlowChannelDeclaration',
 'ConservationEvidence',
 'ExactResidualExpectation',
 'UncertaintyAwareResidualExpectation',
 'ResidualExpectation',
 'DistortionModel',
 'ActionDefinition',
 'ActionInstance',
 'EffectiveInterval',
 'WriteSupport',
 'ConstraintSupport',
 'ActionStatus',
 'Provider',
 'ProviderNetwork',
 'TopologySnapshot',
 'CapacityLocus',
 'RoutePlan',
 'RouteSemanticsStatus',
 'AvailabilityStatus',
 'Commitment',
 'Reservation',
 'CapacityRecord',
 'Measurement',
 'MeasurementContract',
 'Schedule',
 'ComparatorSchedule',
 'ComparatorKind',
 'CoordinationEventDeclaration',
 'InformationContract',
 'InformationView',
 'InformationReadSet',
 'PolicyMemoryState',
 'MemoryMode',
 'CausalIdentificationStatus',
 'CausalRemainder',
 'Quote',
 'Receipt',
 'GroupReceipt',
 'ChildActionRecord',
 'SettlementShare',
 'GroupResidual',
 'SettlementClosureRecord',
 'Ledger',
 'LedgerEntry',
 'LedgerKind',
 'FaultScheduleV1',
 'FaultDirectiveV1',
 'FaultClass',
 'FaultTargetCoordinate',
 'FaultScheduleClass',
 'ExperimentConfiguration',
 'ExecutionBinding',
 'ExecutionMode',
 'OperationalExclusion',
 'ExecutionIdentity',
 'ArtifactRecord',
 'ExecutionResultManifest',
 'validate_state_record',
 'validate_projection_contract',
 'validate_conservation_profile_selection',
 'validate_conservation_profile',
 'validate_distortion_model',
 'validate_action_definition',
 'validate_action_instance',
 'validate_provider_network',
 'validate_route_plan',
 'validate_commitment',
 'validate_reservation',
 'validate_capacity_record',
 'validate_measurement',
 'validate_schedule',
 'validate_information_view',
 'validate_policy_memory_state',
 'validate_causal_remainder',
 'validate_settlement_closure',
 'validate_ledger',
 'validate_fault_schedule_boundary',
 'validate_experiment_configuration',
 'validate_execution_binding',
 'validate_execution_result_manifest',
 'ExtentDefinition',
 'AtomicRefinementDeclaration',
 'QuantityParticipationGeneratorDeclaration',
 'StateTransformationGeneratorDeclaration',
 'ConstitutiveGeneratorLink',
 'RegularityAndReparameterizationWitness',
 'HybridActivationDeclaration',
 'FiniteReconstructionWitness',
 'BoundaryHistoryEquivalenceWitness',
 'validate_extent_definition',
 'validate_atomic_refinement',
 'validate_quantity_participation_generator',
 'validate_state_transformation_generator',
 'validate_constitutive_generator_link',
 'validate_regularity_and_reparameterization_witness',
 'validate_hybrid_activation',
 'validate_finite_reconstruction',
 'validate_boundary_history_equivalence',
 'JointObjectiveDeclaration',
 'FiniteSetInteractionWitness',
 'SameBaselineNonadditivityWitness',
 'SerialComparatorInteractionWitness',
 'MixedMarginalWitness',
 'CommutatorWitness',
 'SharedConstraintFactor',
 'InteractionTopologySnapshot',
 'AllocationOptimalityWitness',
 'ScalarDecompositionWitness',
 'InstitutionalAcceptanceRule',
 'InstitutionalSettlementRule',
 'validate_joint_objective',
 'validate_finite_set_interaction',
 'validate_same_baseline_nonadditivity',
 'validate_serial_comparator_interaction',
 'validate_mixed_marginal',
 'validate_commutator',
 'validate_shared_constraint_factor',
 'validate_interaction_topology_snapshot',
 'validate_allocation_optimality',
 'validate_scalar_decomposition',
 'validate_institutional_acceptance_rule',
 'validate_institutional_settlement_rule',
 'SignatureProfile',
 'TrustEvidenceKind',
 'RevocableObjectKind',
 'RootRole',
 'KeyPinV1',
 'RootThresholdV1',
 'TrustProfileV1',
 'IssuerKeyV1',
 'IssuerEntry',
 'IssuerRegistrySnapshotV1',
 'DelegationCredentialV1',
 'RevocationEntryV1',
 'RevocationSnapshotV1',
 'TrustedTimeChallengeV1',
 'TrustedTimeAttestationV1',
 'AuthorizationAuthenticityEnvelopeV1',
 'TrustEvidenceEnvelopeV1',
 'TrustedTimeService',
 'RevocationService',
 'AuthorizationStateStore',
 'AuthorizedOperation',
 'AuthorizationValidationStatus',
 'AuthorizationCheckStatus',
 'StageAuthorization',
 'AuthorizationEvidenceBundle',
 'AuthorizationCheckRecord',
 'AuthorizationValidationRecord',
 'AuthorizationUseStatus',
 'AuthorizationUseStoreIdentity',
 'AuthorizationUseRecord',
 'ConsumeOutcome',
 'CapabilityClass',
 'AccessCapability',
 'compute_authorization_use_key',
 'verify_ed25519_signature',
 'validate_trust_profile',
 'validate_issuer_registry_snapshot',
 'validate_delegation_chain',
 'validate_trusted_time_attestation',
 'validate_revocation_snapshot',
 'validate_stage_authorization',
 'consume_stage_authorization',
 'accept_registry_object',
 'supersede_registry_object',
 'accept_experiment_configuration',
 'accept_execution_binding',
 'append_operational_ledger_entry',
 'build_synthetic_information_view',
 'EventKeyDigest',
 'EventDeclarationDigest',
 'OwnershipDigest',
 'PhaseCommitDigest',
 'DurabilityEvidenceDigest',
 'RunEnvelopeDigest',
 'TraceDigest',
 'PhaseOrdinal',
 'EventKey',
 'EventDeclaration',
 'PhaseCommitRecord',
 'TraceCompleteness',
 'OwnershipKind',
 'OpaqueLocusKey',
 'UpdateOwnershipClaim',
 'OwnershipConflict',
 'EpochUpdateOwnership',
 'OwnershipValidationRecord',
 'CommitOutcome',
 'PolicyMemoryTransaction',
 'PhysicalPhaseTransaction',
 'AtomicStoreRequest',
 'DurablePrefixEvidence',
 'AtomicStoreRejection',
 'AtomicStoreAmbiguity',
 'AtomicStoreUnavailable',
 'AtomicCommitOutcome',
 'AtomicStore',
 'PolicyDecisionStore',
 'PhaseCommitStore',
 'TraceRowKind',
 'TraceHeader',
 'TraceFooter',
 'CanonicalScientificTracePayloadV1',
 'CanonicalTraceRow',
 'TraceRowFrame',
 'CanonicalTracePrefix',
 'TraceExtensionEvidence',
 'CompleteTraceEvidence',
 'MinimumReconstructableTrace',
 'RunTraceEnvelopeV1',
 'TraceValidationStatus',
 'TraceValidationResult',
 'ProposalRecord',
 'ScreeningDisposition',
 'ScreeningResult',
 'PhaseCommitRequest',
 'T3EntryGuard',
 'ScientificExecutionLease',
 'FaultHookBoundary',
 'compute_event_key_digest',
 'compute_event_declaration_digest',
 'compute_ownership_digest',
 'compute_phase_commit_digest',
 'compute_durability_evidence_digest',
 'compute_run_envelope_digest',
 'order_event_keys',
 'validate_event_declaration',
 'validate_phase_commit_record',
 'build_epoch_update_ownership',
 'validate_update_ownership',
 'build_atomic_commit_request',
 'classify_inert_commit_failure',
 'validate_atomic_commit_outcome',
 'validate_policy_memory_transaction',
 'validate_durable_prefix',
 'project_canonical_trace_row',
 'frame_trace_row',
 'build_trace_prefix',
 'extend_trace_prefix',
 'validate_complete_trace_evidence',
 'build_minimum_reconstructable_trace',
 'build_run_trace_envelope',
 'validate_inert_fault_hook',
 'validate_t3_entry_guard',
 'validate_scientific_execution_lease',
 'begin_bound_scientific_execution',
 'propose_phase_updates',
 'screen_and_admit',
 'propose_joint_transition',
 'commit_phase_updates',
 'advance_epoch',
 'T2FixtureCapability',
 'DependencyEdge',
 'JointTransitionGroup',
 'AdmissibleComparatorSet',
 'GroupMeasurement',
 'SameBaselineNonadditivity',
 'ComparatorInteraction',
 'NonserializableGroup',
 'classify_joint_groups_fixture',
 'classify_joint_groups',
 'compute_group_measurement_fixture',
 'compute_group_measurement',
 'compute_same_baseline_nonadditivity_fixture',
 'compute_same_baseline_nonadditivity',
 'compute_comparator_interaction_fixture',
 'compute_comparator_interaction',
 'TopologyChangeEvent',
 'AdmissionDecision',
 'QueueRecord',
 'ReservationShortfall',
 'CongestionRecord',
 'DelayRecord',
 'InTransitRecord',
 'DelayedEffect',
 'DynamicUpdateRecord',
 'NaturalDriveContract',
 'validate_dynamic_static_identity',
 'propose_reroute',
 'RuntimeMetadata',
 'ResultArtifact',
 'SummaryArtifact',
 'FigureArtifact',
 'PublicationRecord',
 'CorrectionRecord',
 'SourceProvenance',
 'RuntimeProvenance',
 'EnvironmentProvenance',
 'ExecutionSemanticsProjection',
 'RecoveryClassification',
 'RecoveryRecord',
 'WriteOnceStore',
 'PublicationReceipt',
 'classify_execution_runtime_property',
 'finalize_inert_trace_payload',
 'finalize_trace_payload',
 'finalize_inert_manifest',
 'finalize_execution_result_manifest',
 'recover_inert_artifacts',
 'recover_artifacts',
 'create_inert_correction_record',
 'create_correction_record',
 'publish_inert_artifacts',
 'publish_artifacts')
_I9_FAILURE_CODES = ('CANONICALIZATION_FAILURE',
 'INVALID_ECJ1',
 'NONCANONICAL_ECJ1',
 'ECJ1_TYPE_UNSUPPORTED',
 'FLOAT_FORBIDDEN',
 'CYCLIC_OBJECT_GRAPH',
 'DUPLICATE_OBJECT_NAME',
 'INVALID_UNICODE_SCALAR',
 'UNASSIGNED_UNICODE_SCALAR',
 'UNICODE_DATA_INTEGRITY_FAILURE',
 'UNICODE_DATA_MALFORMED',
 'SCIENTIFIC_ID_INVALID',
 'SEMANTIC_VERSION_INVALID',
 'DIGEST_INVALID',
 'DIGEST_TYPE_MISMATCH',
 'HASH_DOMAIN_MISMATCH',
 'ARTIFACT_TOO_LARGE',
 'STABLE_KEY_INVALID',
 'NAMESPACE_UNREGISTERED',
 'RESERVED_NAMESPACE',
 'ALLOCATION_COLLISION',
 'ALLOCATION_CLAIM_CONFLICT',
 'REGISTRY_IMMUTABLE',
 'REGISTRY_RECORD_CONFLICT',
 'ALIAS_CONFLICT',
 'ALIAS_INVALID',
 'REF_NOT_FOUND',
 'VERSION_MISMATCH',
 'HASH_MISMATCH',
 'BOUNDARY_MISMATCH',
 'CLOCK_MISMATCH',
 'CONVERSION_RULE_MISMATCH',
 'CORE_NUMBER_INVALID',
 'DIMENSION_MISMATCH',
 'DIVISION_BY_ZERO',
 'ERROR_BOUND_INVALID',
 'HORIZON_INVALID',
 'IMPLICIT_ABSENCE_FORBIDDEN',
 'IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN',
 'INVALID_AGGREGATION',
 'LIFECYCLE_TRANSITION_INVALID',
 'NONFINITE_NUMBER_FORBIDDEN',
 'NUMERICAL_OPERATION_UNSUPPORTED',
 'NUMERICAL_POLICY_INCOMPLETE',
 'NUMERICAL_POLICY_REQUIRED',
 'QUANTITY_TYPE_MISMATCH',
 'REGION_MISMATCH',
 'RESOLUTION_STATE_INVALID',
 'SIGN_CONVENTION_MISMATCH',
 'SUPERSESSION_INVALID',
 'TIME_BASIS_MISMATCH',
 'UNCERTAINTY_RECORD_INVALID',
 'UNIT_MISMATCH',
 'I3_RECORD_FORMATION_INVALID',
 'I3_OBJECT_CONTENT_MISMATCH',
 'I3_COLLECTION_ORDER_INVALID',
 'I3_DUPLICATE_MEMBER',
 'STATE_PROJECTION_FAILURE',
 'MISSING_COORDINATE',
 'POLICY_MEMORY_NOT_APPLICABLE',
 'EPOCH_MISMATCH',
 'CONSERVATION_PROFILE_INVALID',
 'CONSERVATION_LEVEL_REQUIREMENT_MISSING',
 'CONSERVATION_QUANTITY_DUPLICATE',
 'CONSERVATION_COORDINATE_DUPLICATE',
 'CONSERVATION_FLOW_CHANNEL_DUPLICATE',
 'CONSERVATION_UNIT_MISMATCH',
 'CONSERVATION_EVIDENCE_INCOMPLETE',
 'CONSERVATION_ISOLATION_INVALID',
 'CONSERVATION_TOLERANCE_UNDECLARED',
 'PHYSICAL_POLICY_MEMORY_CONFLATION',
 'DISTORTION_DECLARATION_INVALID',
 'ACTION_DECLARATION_INVALID',
 'RESERVATION_CAPACITY_MISMATCH',
 'MEASUREMENT_CONTRACT_MISMATCH',
 'INADMISSIBLE_SCHEDULE',
 'MISSING_COMPARATOR',
 'PROVISIONAL_ROUTE_REQUIRED',
 'INFORMATION_VIEW_DECLARATION_INVALID',
 'CAUSAL_ATTRIBUTION_UNRESOLVED',
 'SETTLEMENT_LINK_INVALID',
 'SETTLEMENT_CLOSURE_FAILURE',
 'LEDGER_LINK_INVALID',
 'FAULT_SCHEDULE_INVALID',
 'FAULT_EXTENSION_UNAVAILABLE',
 'CONFIGURATION_INCOMPLETE',
 'EXECUTION_SEMANTICS_PROJECTION_FAILURE',
 'ARTIFACT_COMPLETENESS_INVALID',
 'EXTENT_DECLARATION_INVALID',
 'EXTENT_DIVISIBILITY_UNDECLARED',
 'ATOMIC_REFINEMENT_INVALID',
 'GENERATOR_DECLARATION_INVALID',
 'GENERATOR_LINK_INVALID',
 'AUGMENTED_STATE_INCOMPLETE',
 'REPARAMETERIZATION_WITNESS_INVALID',
 'HYBRID_ACTIVATION_INVALID',
 'FIXED_ACTIVATION_ACCOUNT_DUPLICATED',
 'RECONSTRUCTION_CLAIM_UNSUPPORTED',
 'BOUNDARY_HISTORY_EQUIVALENCE_INVALID',
 'BOUNDARY_ACCOUNT_PRESERVATION_INCOMPLETE',
 'FORBIDDEN_DECLARATION_RUNTIME_BEHAVIOR',
 'VALIDATOR_BYPASS_FORBIDDEN',
 'OBJECTIVE_GRAMMAR_INVALID',
 'SUBSET_PROTOCOL_INCOMPLETE',
 'SUBSET_LATTICE_INCOMPLETE',
 'MOBIUS_CLOSURE_FAILURE',
 'TRUNCATION_RESIDUAL_MISMATCH',
 'COMPARATOR_INTERACTION_INVALID',
 'MIXED_MARGINAL_WITNESS_INVALID',
 'COMMUTATOR_WITNESS_INVALID',
 'COMMUTATIVITY_SCOPE_OVERCLAIM',
 'SHARED_CONSTRAINT_OWNERSHIP_INVALID',
 'SHARED_BOUNDARY_VISIBILITY_MISSING',
 'INTERACTION_TOPOLOGY_INVALID',
 'HIDDEN_STATE_TOPOLOGY_UNRESOLVED',
 'BOUNDARY_INTERACTION_PRESERVATION_INVALID',
 'ALLOCATION_FEASIBILITY_INVALID',
 'OPTIMALITY_CERTIFICATE_INAPPLICABLE',
 'SCALAR_DECOMPOSITION_INVALID',
 'DECOMPOSITION_PROVENANCE_INCOMPLETE',
 'INSTITUTIONAL_RULE_INVALID',
 'CAUSAL_SETTLEMENT_CONFLATION',
 'SETTLEMENT_RESIDUAL_CLOSURE_MISSING',
 'PROHIBITED_INTERFERENCE_CLAIM',
 'I4_RECORD_FORMATION_INVALID',
 'PRODUCTION_BOOTSTRAP_MISSING',
 'TRUST_PROFILE_PIN_MISMATCH',
 'SIGNATURE_PROFILE_UNSUPPORTED',
 'KEY_ID_MISMATCH',
 'PUBLIC_KEY_INVALID',
 'SIGNATURE_ENCODING_INVALID',
 'SIGNATURE_INVALID',
 'ROOT_THRESHOLD_NOT_MET',
 'ROOT_PROOF_ORDER_INVALID',
 'ISSUER_REGISTRY_INVALID',
 'ISSUER_REGISTRY_ROLLBACK',
 'ISSUER_REGISTRY_GAP',
 'ISSUER_REGISTRY_EQUIVOCATION',
 'ISSUER_KEY_INVALID',
 'DELEGATION_CHAIN_INVALID',
 'DELEGATION_SCOPE_ESCALATION',
 'DELEGATION_DEPTH_EXCEEDED',
 'DELEGATION_CYCLE',
 'TRUSTED_TIME_UNAVAILABLE',
 'TRUSTED_TIME_CHALLENGE_MISMATCH',
 'TRUSTED_TIME_STALE',
 'TRUSTED_TIME_SEQUENCE_INVALID',
 'REVOCATION_UNAVAILABLE',
 'REVOCATION_SNAPSHOT_EXPIRED',
 'REVOCATION_ROLLBACK',
 'REVOCATION_GAP',
 'REVOCATION_EQUIVOCATION',
 'AUTHORIZATION_REVOKED',
 'AUTHORIZATION_SCOPE_MISMATCH',
 'AUTHORIZATION_STAGE_MISMATCH',
 'AUTHORIZATION_OPERATION_MISMATCH',
 'AUTHORIZATION_TARGET_MISMATCH',
 'AUTHORIZATION_CONFIGURATION_MISMATCH',
 'AUTHORIZATION_BINDING_MISMATCH',
 'AUTHORIZATION_EXECUTION_IDENTITY_MISMATCH',
 'AUTHORIZATION_PREDECESSOR_MISMATCH',
 'AUTHORIZATION_LIFECYCLE_MISMATCH',
 'AUTHORIZATION_EXCLUSION_MATCH',
 'BINDING_CONFIGURATION_MISMATCH',
 'AUTHORIZATION_USE_ALREADY_CONSUMED',
 'AUTHORIZATION_USE_UNRESOLVED',
 'AUTHORIZATION_USE_STORE_UNSUPPORTED',
 'AUTHORIZATION_USE_LEDGER_FAILURE',
 'REGISTRY_ACCEPTANCE_INVALID',
 'REGISTRY_SUPERSESSION_INVALID',
 'INFORMATION_CAPABILITY_INVALID',
 'INFORMATION_NOT_VISIBLE',
 'INFORMATION_NOT_AVAILABLE',
 'INFORMATION_TOO_OLD',
 'CURRENT_MEMORY_MISMATCH',
 'INFORMATION_TRAVERSAL_FORBIDDEN',
 'INFORMATION_READ_SET_DENIED',
 'VALIDATION_NAMESPACE_FORBIDDEN',
 'VALIDATION_KEY_FORBIDDEN',
 'DEPENDENCY_INTEGRITY_FAILURE',
 'SQLITE_VERSION_UNSUPPORTED',
 'SQLITE_SCHEMA_MISMATCH',
 'CAPABILITY_ESCALATION_FORBIDDEN',
 'POLICY_MEMORY_PROJECTION_FAILURE',
 'POLICY_MEMORY_MISMATCH',
 'I5_RECORD_FORMATION_INVALID',
 'PHASE_ORDINAL_INVALID',
 'EVENT_KEY_INVALID',
 'EVENT_KEY_DUPLICATE',
 'EVENT_ORDER_INVALID',
 'EVENT_IDENTITY_INVALID',
 'PHASE_8_PHASE_9_DUPLICATE_IDENTIFIER',
 'PHASE_PREDECESSOR_MISMATCH',
 'PHASE_COMMIT_RECORD_INVALID',
 'UPDATE_OWNERSHIP_CLAIM_INVALID',
 'INFORMATIONAL_MEMORY_OWNERSHIP_FORBIDDEN',
 'UPDATE_OWNERSHIP_CONFLICT',
 'OWNERSHIP_ORDER_INVALID',
 'PHASE_OWNERSHIP_MISMATCH',
 'ATOMIC_COMMIT_REQUEST_INVALID',
 'EXPECTED_TRACE_PREFIX_MISMATCH',
 'COMMIT_REJECTED',
 'COMMIT_AMBIGUOUS',
 'DURABILITY_UNAVAILABLE',
 'DURABILITY_EVIDENCE_MISSING',
 'DURABILITY_EVIDENCE_INCONSISTENT',
 'POLICY_MEMORY_TRANSACTION_INVALID',
 'PHYSICAL_PHASE_TRANSACTION_INVALID',
 'TRACE_ROW_INVALID',
 'TRACE_ROW_PREDECESSOR_MISMATCH',
 'TRACE_ROW_GAP',
 'TRACE_PREFIX_INVALID',
 'TRACE_PREFIX_NOT_LITERAL',
 'TRACE_PREFIX_MUTATION_FORBIDDEN',
 'TRACE_EXTENSION_IDENTITY_INVALID',
 'TRACE_COMPLETENESS_INVALID',
 'TRACE_EQUIVOCAL',
 'TRACE_EVIDENCE_MISSING',
 'MINIMUM_TRACE_INCOMPLETE',
 'RUN_TRACE_ENVELOPE_INVALID',
 'SCIENTIFIC_EXECUTION_LEASE_INVALID',
 'T3_ENTRY_GUARD_FAILED',
 'REAL_DURABILITY_BACKEND_UNAVAILABLE',
 'EXECUTION_CALLBACK_FORBIDDEN',
 'SCIENTIFIC_STATE_ADVANCE_FORBIDDEN',
 'I5_HASH_COLLISION',
 'FAULT_HOOK_INVALID',
 'I6_RECORD_FORMATION_INVALID',
 'INCOMPATIBLE_BOUNDARY',
 'UNRESOLVED_COUPLING',
 'GROUPING_FAILURE',
 'DIAGNOSTIC_UNDEFINED',
 'I7_RECORD_FORMATION_INVALID',
 'DYNAMIC_STATE_INCOMPLETE',
 'TOPOLOGY_LAYER_CONFLATION',
 'TOPOLOGY_PROVENANCE_INVALID',
 'DOMAIN_DYNAMIC_AUTHORITY_MISSING',
 'AVAILABILITY_TRANSITION_INVALID',
 'CAPACITY_IDENTITY_FAILURE',
 'CAPACITY_COMPLIANCE_FAILURE',
 'ADMISSION_BALANCE_FAILURE',
 'QUEUE_BALANCE_FAILURE',
 'REJECTED_DEMAND_QUEUE_MUTATION',
 'RESERVATION_SHORTFALL_INVALID',
 'CONGESTION_DECLARATION_INVALID',
 'DELAY_DECOMPOSITION_INVALID',
 'IN_TRANSIT_STATE_INVALID',
 'DELAYED_EFFECT_STATUS_INVALID',
 'UPDATE_DOUBLE_APPLICATION_FORBIDDEN',
 'NATURAL_DRIVE_PHASE_INVALID',
 'POLICY_MEMORY_PAIR_MISMATCH',
 'COMMITMENT_STATE_MISMATCH',
 'ROUTE_SEMANTICS_UNRESOLVED',
 'COMPLETED_ROUTE_REWRITE_FORBIDDEN',
 'DYNAMIC_NUMERICAL_POLICY_UNACCEPTED',
 'DYNAMIC_STATIC_IDENTITY_MISMATCH',
 'I8_RECORD_FORMATION_INVALID',
 'SOURCE_RUNTIME_PROPERTY_OUTSIDE_SECTION7',
 'PROVENANCE_INVENTORY_INVALID',
 'EXECUTION_SEMANTICS_CLASSIFICATION_INVALID',
 'TRACE_FINALIZATION_INVALID',
 'MISSING_ARTIFACT',
 'MANIFEST_COMPLETENESS_INVALID',
 'MANIFEST_MUTATION_FORBIDDEN',
 'AMBIGUOUS_PREFIX',
 'RECOVERY_RUN_BINDING_MISMATCH',
 'RECOVERY_AUTHORIZATION_MISMATCH',
 'RECOVERY_EXECUTION_FORBIDDEN',
 'ALREADY_EXISTS_DIFFERENT',
 'WRITE_ONCE_STORE_INVALID',
 'PUBLICATION_AUTHORIZATION_MISMATCH',
 'PUBLICATION_RECORD_INVALID',
 'CORRECTION_AUTHORIZATION_MISMATCH',
 'CORRECTION_AS_OVERWRITE_FORBIDDEN',
 'CORRECTION_RECORD_INVALID',
 'REAL_FINALIZATION_AUTHORITY_UNAVAILABLE',
 'REAL_RECOVERY_BACKEND_UNAVAILABLE',
 'REAL_PUBLICATION_BACKEND_UNAVAILABLE',
 'REAL_CORRECTION_AUTHORITY_UNAVAILABLE',
 'I8_HASH_COLLISION')
_I9_PUBLIC_SIGNATURES = (('actions', 'validate_action_definition', '(definition: ActionDefinition, /) -> None'),
 ('actions',
  'validate_action_instance',
  '(instance: ActionInstance, route: RoutePlan | Applicability, /) -> None'),
 ('artifacts',
  'validate_execution_result_manifest',
  '(manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord, ...], /) -> '
  'None'),
 ('atomic', 'validate_extent_definition', '(record: ExtentDefinition, /) -> None'),
 ('atomic',
  'validate_atomic_refinement',
  '(record: AtomicRefinementDeclaration, extent: ExtentDefinition, /) -> None'),
 ('atomic',
  'validate_quantity_participation_generator',
  '(record: QuantityParticipationGeneratorDeclaration, extent: ExtentDefinition, /) -> '
  'None'),
 ('atomic',
  'validate_state_transformation_generator',
  '(record: StateTransformationGeneratorDeclaration, extent: ExtentDefinition, /) -> '
  'None'),
 ('atomic',
  'validate_constitutive_generator_link',
  '(record: ConstitutiveGeneratorLink, quantity_generator: '
  'QuantityParticipationGeneratorDeclaration, state_generator: '
  'StateTransformationGeneratorDeclaration, /) -> None'),
 ('atomic',
  'validate_regularity_and_reparameterization_witness',
  '(record: RegularityAndReparameterizationWitness, source_extent: ExtentDefinition, '
  'target_extent: ExtentDefinition, generator: '
  'QuantityParticipationGeneratorDeclaration | '
  'StateTransformationGeneratorDeclaration, /) -> None'),
 ('atomic',
  'validate_hybrid_activation',
  '(record: HybridActivationDeclaration, state_generator: '
  'StateTransformationGeneratorDeclaration, /) -> None'),
 ('atomic',
  'validate_finite_reconstruction',
  '(record: FiniteReconstructionWitness, state_generator: '
  'StateTransformationGeneratorDeclaration, hybrid: HybridActivationDeclaration | '
  'Applicability, /) -> None'),
 ('atomic',
  'validate_boundary_history_equivalence',
  '(record: BoundaryHistoryEquivalenceWitness, /) -> None'),
 ('authorization',
  'validate_stage_authorization',
  '(bundle: AuthorizationEvidenceBundle, requested_stage: str, requested_operation: '
  'AuthorizedOperation, target_object_refs: tuple[ObjectRef, ...], '
  'trusted_time_service: TrustedTimeService, revocation_service: RevocationService, '
  'state_store: AuthorizationStateStore, /) -> AuthorizationValidationRecord'),
 ('authorization_use',
  'consume_stage_authorization',
  '(validation: AuthorizationValidationRecord, store_identity: '
  'AuthorizationUseStoreIdentity, /) -> AuthorizationUseRecord'),
 ('authorization_use',
  'accept_registry_object',
  '(candidate: RegistryRecord, validation: AuthorizationValidationRecord, use_record: '
  'AuthorizationUseRecord, store_identity: AuthorizationUseStoreIdentity, /) -> '
  'RegistryRecord'),
 ('authorization_use',
  'supersede_registry_object',
  '(predecessor: RegistryRecord, successor: RegistryRecord, relation: '
  'SupersessionRelation, validation: AuthorizationValidationRecord, use_record: '
  'AuthorizationUseRecord, store_identity: AuthorizationUseStoreIdentity, /) -> '
  'tuple[RegistryRecord, RegistryRecord]'),
 ('authorization_use',
  'accept_experiment_configuration',
  '(configuration: ExperimentConfiguration, fault_schedule: FaultScheduleV1 | '
  'Applicability, validation: AuthorizationValidationRecord, use_record: '
  'AuthorizationUseRecord, store_identity: AuthorizationUseStoreIdentity, /) -> '
  'RegistryRecord'),
 ('authorization_use',
  'accept_execution_binding',
  '(binding: ExecutionBinding, accepted_configuration: RegistryRecord, validation: '
  'AuthorizationValidationRecord, use_record: AuthorizationUseRecord, store_identity: '
  'AuthorizationUseStoreIdentity, /) -> RegistryRecord'),
 ('authorization_use',
  'append_operational_ledger_entry',
  '(ledger: Ledger, entry: LedgerEntry, validation: AuthorizationValidationRecord, '
  'use_record: AuthorizationUseRecord, store_identity: AuthorizationUseStoreIdentity, '
  '/) -> tuple[Ledger, LedgerEntry]'),
 ('bridge',
  'classify_joint_groups_fixture',
  '(fixture_case: CanonicalBytes, capability: T2FixtureCapability, /) -> '
  'tuple[JointTransitionGroup, ...]'),
 ('bridge',
  'compute_group_measurement_fixture',
  '(fixture_case: CanonicalBytes, capability: T2FixtureCapability, /) -> '
  'GroupMeasurement'),
 ('bridge',
  'compute_same_baseline_nonadditivity_fixture',
  '(fixture_case: CanonicalBytes, capability: T2FixtureCapability, /) -> '
  'SameBaselineNonadditivity'),
 ('bridge',
  'compute_comparator_interaction_fixture',
  '(fixture_case: CanonicalBytes, capability: T2FixtureCapability, /) -> '
  'tuple[ComparatorInteraction, ...] | NonserializableGroup'),
 ('bridge',
  'classify_joint_groups',
  '(actions: tuple[ActionInstance, ...], declared_edges: tuple[DependencyEdge, ...], '
  'declared_groups: tuple[JointTransitionGroup, ...], dependency_relation_complete: '
  'bool, separability_evidence_refs: tuple[ObjectRef, ...], permit: '
  '_BridgeExecutionPermit, /) -> tuple[JointTransitionGroup, ...]'),
 ('bridge',
  'compute_group_measurement',
  '(group: JointTransitionGroup, before: RepresentedState, after: RepresentedState, '
  'distortion: DistortionModel, initial_distortion: Quantity, endpoint_distortion: '
  'Quantity, initial_evaluation_ref: ObjectRef, endpoint_evaluation_ref: ObjectRef, '
  'physical_measurement_ref: ObjectRef, group_measurement_envelope: '
  'CommonObjectEnvelope, group_quote_ref: ObjectRef | Applicability, '
  'group_quote_assumption_refs: tuple[ObjectRef, ...], nonadditivity_ref: ObjectRef | '
  'Applicability, comparator_set_ref: ObjectRef | Applicability, '
  'interaction_or_refusal_refs: tuple[ObjectRef, ...], '
  'causal_identification_protocol_ref: ObjectRef | Applicability, causal_status: '
  'CausalIdentificationStatus, causal_evidence_refs: tuple[ObjectRef, ...], '
  'causal_contribution_refs: tuple[ObjectRef, ...], causal_remainder_ref: ObjectRef | '
  'Applicability, settlement_rule_ref: ObjectRef | Applicability, '
  'settlement_share_refs: tuple[ObjectRef, ...], settlement_share_values: '
  'tuple[Quantity, ...], settlement_residual_value: Quantity | Applicability, '
  'settlement_residual_account_refs: tuple[ObjectRef, ...], '
  'settlement_validation_provenance_ref: ObjectRef | Applicability, '
  'unresolved_effect_refs: tuple[ObjectRef, ...], later_measurement_horizon_refs: '
  'tuple[ObjectRef, ...], permit: _BridgeExecutionPermit, /) -> GroupMeasurement'),
 ('bridge',
  'compute_same_baseline_nonadditivity',
  '(group_or_witness_ref: ObjectRef, physical_measurement_ref: ObjectRef | '
  "Applicability, basis_kind: Literal['PHYSICAL_JOINT_GROUP', "
  "'STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS'], action_refs: tuple[ObjectRef, ...], "
  'baseline_state_ref: ObjectRef, boundary_ref: ObjectRef, horizon_ref: ObjectRef, '
  'standalone_endpoint_refs: tuple[ObjectRef, ...] | Applicability, empty_baseline: '
  'Quantity | Applicability, singleton_values: tuple[Quantity, ...] | Applicability, '
  'joint_value: Quantity, d2_witness: SameBaselineNonadditivityWitness | '
  'Applicability, d2_witness_ref: ObjectRef | Applicability, nonadditivity_envelope: '
  'CommonObjectEnvelope, permit: _BridgeExecutionPermit, /) -> '
  'SameBaselineNonadditivity'),
 ('bridge',
  'compute_comparator_interaction',
  '(group_or_witness_ref: ObjectRef, physical_measurement_ref: ObjectRef | '
  "Applicability, comparison_kind: Literal['PHYSICAL_GROUP_COMPARATOR', "
  "'STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS'], comparator_set: "
  'AdmissibleComparatorSet, group_endpoint: RepresentedState, group_distortion: '
  'Quantity, group_ebu: Quantity, sequential_endpoints: tuple[RepresentedState, ...] | '
  'Applicability, sequential_distortions: tuple[Quantity, ...] | Applicability, '
  'sequential_values: tuple[Quantity, ...] | Applicability, d2_witnesses: '
  'tuple[SerialComparatorInteractionWitness, ...] | Applicability, d2_witness_refs: '
  'tuple[ObjectRef, ...] | Applicability, result_envelopes: '
  'tuple[CommonObjectEnvelope, ...], nonserializable_envelope: CommonObjectEnvelope | '
  'Applicability, permit: _BridgeExecutionPermit, /) -> tuple[ComparatorInteraction, '
  '...] | NonserializableGroup'),
 ('canonical', 'encode_ecj1', '(value: ECJ1Value) -> CanonicalBytes'),
 ('canonical', 'parse_ecj1', '(data: bytes) -> ECJ1Value'),
 ('capabilities',
  'build_synthetic_information_view',
  '(contract: InformationContract, expected_current_memory_ref_or_not_applicable: '
  'ObjectRef | Applicability, fabricated_fields: tuple[tuple[ObjectRef, '
  'CanonicalBytes, str], ...], attempted_read_set: InformationReadSet | Applicability, '
  'injected_now: str, /) -> tuple[InformationView, AccessCapability]'),
 ('causal', 'validate_causal_remainder', '(record: CausalRemainder, /) -> None'),
 ('commitments', 'validate_commitment', '(record: Commitment, /) -> None'),
 ('commitments',
  'validate_reservation',
  '(record: Reservation, capacity: CapacityRecord, /) -> None'),
 ('commitments', 'validate_capacity_record', '(record: CapacityRecord, /) -> None'),
 ('conservation',
  'validate_conservation_profile_selection',
  '(selection: ConservationProfileSelection, /) -> None'),
 ('conservation',
  'validate_conservation_profile',
  '(profile: ConservationProfile, /) -> None'),
 ('distortion', 'validate_distortion_model', '(model: DistortionModel, /) -> None'),
 ('durability',
  'validate_policy_memory_transaction',
  '(transaction: PolicyMemoryTransaction, /) -> None'),
 ('durability',
  'build_atomic_commit_request',
  '(*, request_ref: ObjectRef, expected_trace_prefix: TraceDigest, '
  'expected_phase_predecessor: PhaseCommitDigest | Applicability, '
  'policy_memory_transaction: PolicyMemoryTransaction | Applicability, '
  'physical_phase_transaction: PhysicalPhaseTransaction | Applicability, '
  'attempt_ordinal: int) -> AtomicStoreRequest'),
 ('durability',
  'classify_inert_commit_failure',
  "(request: AtomicStoreRequest, observed: Literal['REJECTED', 'AMBIGUOUS', "
  "'UNAVAILABLE'], evidence_refs: tuple[ObjectRef, ...], /) -> AtomicStoreRejection | "
  'AtomicStoreAmbiguity | AtomicStoreUnavailable'),
 ('durability',
  'validate_atomic_commit_outcome',
  '(request: AtomicStoreRequest, outcome: AtomicCommitOutcome, /) -> None'),
 ('durability',
  'validate_durable_prefix',
  '(expected: CanonicalTracePrefix, observed: CanonicalTracePrefix, outcome: '
  'CommitOutcome, /) -> None'),
 ('dynamic',
  'validate_dynamic_static_identity',
  '(fixture_case: CanonicalBytes, capability: T2FixtureCapability, /) -> None'),
 ('dynamic',
  'propose_reroute',
  '(route: RoutePlan, topology_change: TopologyChangeEvent, transit: InTransitRecord, '
  'proposed_unfinished_suffix_refs: tuple[ObjectRef, ...], permit: '
  '_DynamicExecutionPermit, /) -> RoutePlan'),
 ('envelopes',
  'validate_object_envelope',
  '(envelope: CommonObjectEnvelope) -> CompatibilityResult'),
 ('envelopes',
  'validate_lifecycle_transition',
  '(transition: LifecycleTransition) -> LifecycleValidationResult'),
 ('envelopes',
  'validate_supersession_relation',
  '(relation: SupersessionRelation) -> SupersessionValidationResult'),
 ('events', 'validate_event_declaration', '(declaration: EventDeclaration, /) -> None'),
 ('events',
  'order_event_keys',
  '(declarations: tuple[EventDeclaration, ...], /) -> tuple[EventDeclaration, ...]'),
 ('events',
  'validate_phase_commit_record',
  '(record: PhaseCommitRecord, expected_previous: PhaseCommitDigest | Applicability, '
  '/) -> None'),
 ('execution', 'validate_t3_entry_guard', '(guard: T3EntryGuard, /) -> None'),
 ('execution',
  'validate_scientific_execution_lease',
  '(lease: ScientificExecutionLease, operation: str, /) -> None'),
 ('execution',
  'begin_bound_scientific_execution',
  '(*, guard: T3EntryGuard, requested_operation: str) -> ScientificExecutionLease'),
 ('execution',
  'propose_phase_updates',
  '(*, lease: ScientificExecutionLease, phase: PhaseOrdinal, state_ref: ObjectRef, '
  'adapter_ref: ObjectRef) -> tuple[ProposalRecord, ...]'),
 ('execution',
  'screen_and_admit',
  '(*, lease: ScientificExecutionLease, proposals: tuple[ProposalRecord, ...], '
  'screening_adapter_ref: ObjectRef) -> tuple[ScreeningResult, ...]'),
 ('execution',
  'propose_joint_transition',
  '(*, lease: ScientificExecutionLease, proposals: tuple[ProposalRecord, ...], '
  'joint_adapter_ref: ObjectRef) -> ProposalRecord'),
 ('execution',
  'commit_phase_updates',
  '(*, lease: ScientificExecutionLease, request: PhaseCommitRequest) -> '
  'PhaseCommitRecord'),
 ('execution',
  'advance_epoch',
  '(*, lease: ScientificExecutionLease, epoch: int, initial_state_ref: ObjectRef, '
  'phase_input_refs: tuple[ObjectRef, ...]) -> RunTraceEnvelopeV1'),
 ('experiment',
  'validate_experiment_configuration',
  '(configuration: ExperimentConfiguration, fault_schedule: FaultScheduleV1 | '
  'Applicability, /) -> None'),
 ('experiment', 'validate_execution_binding', '(binding: ExecutionBinding, /) -> None'),
 ('faults',
  'validate_fault_schedule_boundary',
  '(schedule: FaultScheduleV1, /) -> None'),
 ('faults', 'validate_inert_fault_hook', '(hook: FaultHookBoundary, /) -> None'),
 ('hashing',
  'compute_object_content_hash',
  '(*, object_id: ScientificId, object_kind: str, schema_id: ScientificId, '
  'schema_version: SemanticVersion, object_version: SemanticVersion, authority_refs: '
  'tuple[ObjectRef, ...] | list[ObjectRef], supersedes_ref: ObjectRef | None, '
  'object_content_payload: ECJ1Value) -> ObjectContentHash'),
 ('hashing',
  'compute_authorization_use_key',
  '(*, stage_authorization_ref: ObjectRef, requested_operation: str, '
  'target_object_refs: tuple[ObjectRef, ...], '
  'accepted_configuration_ref_or_not_applicable: ObjectRef | Applicability, '
  'accepted_execution_binding_ref_or_not_applicable: ObjectRef | Applicability, '
  'execution_identity_or_not_applicable: ExecutionIdentity | Applicability) -> '
  'AuthorizationUseKey'),
 ('hashing',
  'compute_state_payload_hash',
  '(*, state_schema_ref: ObjectRef, epoch: ECJ1Value, physical_state_x: ECJ1Value, '
  'topology_state_g: ECJ1Value, queue_and_transit_state_q: ECJ1Value, '
  'commitment_state_c: ECJ1Value, delayed_effect_state_ell: ECJ1Value, '
  'declared_external_inputs_applied: tuple[Any, ...] | list[Any]) -> StatePayloadHash'),
 ('hashing',
  'compute_policy_memory_payload_hash',
  '(*, policy_ref: ObjectRef, memory_schema_ref: ObjectRef, '
  'available_for_decision_epoch: ECJ1Value, resolution_state: str, memory_payload: '
  'ECJ1Value) -> PolicyMemoryPayloadHash'),
 ('hashing',
  'compute_augmented_replay_state_hash',
  '(physical_state_payload_hash: StatePayloadHash, policy_memory_payload_hash: '
  'PolicyMemoryPayloadHash) -> AugmentedClosedLoopReplayStateHash'),
 ('hashing',
  'compute_represented_state_projection_hash',
  '(*, source_state_payload_hash: StatePayloadHash, boundary_ref: ObjectRef, '
  'projection_contract_ref: ObjectRef, included_coordinate_ids: tuple[Any, ...] | '
  'list[Any], excluded_coordinate_ids_and_resolution_states: tuple[Any, ...] | '
  'list[Any], represented_state_payload: ECJ1Value) -> RepresentedStateProjectionHash'),
 ('hashing',
  'compute_information_view_hash',
  '(*, policy_ref: ObjectRef, information_contract_ref: ObjectRef, decision_epoch: '
  'ECJ1Value, current_policy_memory_payload_hash_or_not_applicable: '
  'PolicyMemoryPayloadHash | str, ordered_visible_field_records: tuple[Any, ...] | '
  'list[Any], ordered_visible_object_refs: tuple[ObjectRef, ...] | list[ObjectRef]) -> '
  'InformationViewHash'),
 ('hashing',
  'compute_proposal_set_hash',
  '(*, policy_ref_or_open_loop_schedule_ref: ObjectRef, decision_coordinate: '
  'ECJ1Value, information_view_hash_or_not_applicable: InformationViewHash | str, '
  'before_policy_memory_payload_hash_or_not_applicable: PolicyMemoryPayloadHash | str, '
  'after_policy_memory_payload_hash_or_not_applicable: PolicyMemoryPayloadHash | str, '
  'ordered_proposal_payloads: tuple[Any, ...] | list[Any]) -> ProposalSetHash'),
 ('hashing',
  'compute_execution_semantics_hash',
  '(*, accepted_configuration_ref: ObjectRef, implementation_refs: tuple[Any, ...] | '
  'list[Any], source_refs: tuple[Any, ...] | list[Any], '
  'implementation_entrypoint_semantics: ECJ1Value, '
  'science_affecting_runtime_constraints: ECJ1Value, '
  'science_affecting_operational_exclusions: ECJ1Value, '
  'policy_memory_transition_contracts_or_not_applicable: ECJ1Value, '
  'fault_injection_delivery_contracts_or_not_applicable: ECJ1Value, '
  'event_order_contract: ECJ1Value, arithmetic_and_numerical_policy_contracts: '
  'ECJ1Value, information_capability_contract: ECJ1Value, '
  'canonical_scientific_trace_schema_ref: ObjectRef, scientific_result_schema_ref: '
  'ObjectRef, stochastic_generator_and_stream_contract_or_not_applicable: ECJ1Value) '
  '-> ExecutionSemanticsHash'),
 ('hashing',
  'compute_canonical_trace_row_hash',
  '(*, trace_schema_ref: ObjectRef, row_index: int, epoch: ECJ1Value, event_key: '
  'ECJ1Value, phase_ordinal: int, scientific_object_refs: tuple[Any, ...] | list[Any], '
  'predecessor_state_payload_hash: StatePayloadHash, successor_state_payload_hash: '
  'StatePayloadHash, information_view_hash_or_not_applicable: ECJ1Value, '
  'before_policy_memory_payload_hash_or_not_applicable: ECJ1Value, '
  'after_policy_memory_payload_hash_or_not_applicable: ECJ1Value, '
  'augmented_replay_state_hash_or_not_applicable: ECJ1Value, '
  'proposal_set_hash_or_not_applicable: ECJ1Value, '
  'admission_group_and_ownership_facts: ECJ1Value, typed_quantities: tuple[Any, ...] | '
  'list[Any], uncertainty_values: tuple[Any, ...] | list[Any], lifecycle_transitions: '
  'tuple[Any, ...] | list[Any], declared_scientific_or_model_faults: tuple[Any, ...] | '
  'list[Any], scientifically_relevant_failures: tuple[Any, ...] | list[Any], '
  'resolution_state: str, predecessor_trace_row_hash_or_genesis: CanonicalTraceRowHash '
  '| str) -> CanonicalTraceRowHash'),
 ('hashing',
  'compute_canonical_trace_prefix_hash',
  '(*, trace_header: ECJ1Value, ordered_rows: tuple[Any, ...] | list[Any], '
  'confirmed_row_count: int, last_confirmed_state_payload_hash: StatePayloadHash, '
  'last_confirmed_policy_memory_payload_hash_or_not_applicable: ECJ1Value, '
  'last_confirmed_augmented_replay_state_hash_or_not_applicable: ECJ1Value, '
  'completeness_state: str) -> CanonicalTracePrefixHash'),
 ('hashing',
  'compute_canonical_trace_payload_hash',
  '(*, trace_schema_ref: ObjectRef, accepted_configuration_object_content_hash: '
  'ObjectContentHash, execution_semantics_hash: ExecutionSemanticsHash, '
  'initial_state_payload_hash: StatePayloadHash, '
  'initial_policy_memory_payload_hash_or_not_applicable: ECJ1Value, '
  'initial_augmented_replay_state_hash_or_not_applicable: ECJ1Value, '
  'ordered_external_scientific_input_payload_hashes: tuple[Any, ...] | list[Any], '
  'fault_schedule_object_content_hash_or_not_applicable: ECJ1Value, '
  'stochastic_stream_identities_and_draw_coordinates_or_not_applicable: ECJ1Value, '
  'ordered_rows: tuple[Any, ...] | list[Any], '
  'terminal_or_last_confirmed_state_payload_hash: StatePayloadHash, '
  'terminal_or_last_confirmed_policy_memory_payload_hash_or_not_applicable: ECJ1Value, '
  'terminal_or_last_confirmed_augmented_replay_state_hash_or_not_applicable: '
  'ECJ1Value, confirmed_row_count: int, trace_completeness_state: str) -> '
  'CanonicalScientificTracePayloadHash'),
 ('hashing',
  'compute_artifact_byte_hash',
  '(exact_artifact_bytes: bytes) -> ArtifactByteHash'),
 ('hashing',
  'compute_source_file_raw_sha256',
  '(exact_file_bytes: bytes) -> SourceFileRawSha256'),
 ('hashing',
  'compute_event_key_digest',
  '(*, epoch: int, phase_ordinal: int, declared_priority: int, group_or_scope_id: str, '
  'event_kind: str, primary_object_id: str, local_sequence: int) -> EventKeyDigest'),
 ('hashing',
  'compute_event_declaration_digest',
  '(*, event_key_digest: EventKeyDigest, event_ref: ObjectRef, '
  'declared_simultaneity_ref_or_not_applicable: ObjectRef | Applicability, '
  'payload_hash: ObjectContentHash, predecessor_event_key_digest_or_not_applicable: '
  'EventKeyDigest | Applicability) -> EventDeclarationDigest'),
 ('hashing',
  'compute_ownership_digest',
  "(projection_kind: Literal['CLAIM', 'EPOCH'], projection: ECJ1Value, /) -> "
  'OwnershipDigest'),
 ('hashing',
  'compute_phase_commit_digest',
  '(projection: ECJ1Value, /) -> PhaseCommitDigest'),
 ('hashing',
  'compute_durability_evidence_digest',
  '(projection_without_evidence_digest: ECJ1Value, /) -> DurabilityEvidenceDigest'),
 ('hashing',
  'compute_run_envelope_digest',
  '(projection_without_envelope_digest: ECJ1Value, /) -> RunEnvelopeDigest'),
 ('identity', 'parse_scientific_id', '(value: str) -> ScientificId'),
 ('identity', 'parse_semantic_version', '(value: str) -> SemanticVersion'),
 ('interaction',
  'validate_joint_objective',
  '(record: JointObjectiveDeclaration, /) -> None'),
 ('interaction',
  'validate_finite_set_interaction',
  '(record: FiniteSetInteractionWitness, /) -> None'),
 ('interaction',
  'validate_same_baseline_nonadditivity',
  '(record: SameBaselineNonadditivityWitness, /) -> None'),
 ('interaction',
  'validate_serial_comparator_interaction',
  '(record: SerialComparatorInteractionWitness, /) -> None'),
 ('interaction',
  'validate_mixed_marginal',
  '(record: MixedMarginalWitness, /) -> None'),
 ('interaction',
  'validate_commutator',
  '(record: CommutatorWitness, left_generator: '
  'StateTransformationGeneratorDeclaration, right_generator: '
  'StateTransformationGeneratorDeclaration, /) -> None'),
 ('interaction',
  'validate_shared_constraint_factor',
  '(record: SharedConstraintFactor, /) -> None'),
 ('interaction',
  'validate_interaction_topology_snapshot',
  '(record: InteractionTopologySnapshot, factors: tuple[SharedConstraintFactor, ...], '
  'interactions: tuple[FiniteSetInteractionWitness, ...], equivalence: '
  'BoundaryHistoryEquivalenceWitness | Applicability, /) -> None'),
 ('interaction',
  'validate_allocation_optimality',
  '(record: AllocationOptimalityWitness, objective: JointObjectiveDeclaration, /) -> '
  'None'),
 ('interaction',
  'validate_scalar_decomposition',
  '(record: ScalarDecompositionWitness, objective: JointObjectiveDeclaration, '
  'allocation: AllocationOptimalityWitness, /) -> None'),
 ('interaction',
  'validate_institutional_acceptance_rule',
  '(record: InstitutionalAcceptanceRule, /) -> None'),
 ('interaction',
  'validate_institutional_settlement_rule',
  '(record: InstitutionalSettlementRule, acceptance_rule: InstitutionalAcceptanceRule, '
  '/) -> None'),
 ('ledger',
  'validate_ledger',
  '(ledger: Ledger, entries: tuple[LedgerEntry, ...], /) -> None'),
 ('network',
  'validate_provider_network',
  '(provider: Provider, network: ProviderNetwork, topology: TopologySnapshot, locus: '
  'CapacityLocus, /) -> None'),
 ('network', 'validate_route_plan', '(route: RoutePlan, /) -> None'),
 ('numeric', 'normalize_core_number', '(value: CoreNumberV1) -> CoreNumberV1'),
 ('numeric', 'decimal_to_rational_exact', '(value: DecimalV1) -> RationalV1'),
 ('numeric',
  'apply_exact_core_operation',
  '(operation: NumericalOperation, operands: tuple[CoreNumberV1, ...], *, '
  'exact_conversion: ExactConversion=ExactConversion.NOT_APPLICABLE) -> '
  'NumericalResult | ComparisonResult'),
 ('numeric',
  'validate_numerical_policy',
  '(policy: NumericalPolicyV1) -> Completeness'),
 ('observation',
  'validate_measurement',
  '(measurement: Measurement, contract: MeasurementContract, /) -> None'),
 ('ownership',
  'build_epoch_update_ownership',
  '(epoch: int, claims: tuple[UpdateOwnershipClaim, ...], /) -> EpochUpdateOwnership'),
 ('ownership',
  'validate_update_ownership',
  '(claims: tuple[UpdateOwnershipClaim, ...], /) -> OwnershipValidationRecord'),
 ('policy',
  'validate_information_view',
  '(contract: InformationContract, view: InformationView, read_set: InformationReadSet '
  '| Applicability, /) -> None'),
 ('policy',
  'validate_policy_memory_state',
  '(record: PolicyMemoryState, mode: MemoryMode, predecessor_epoch: Epoch | '
  'Applicability, /) -> None'),
 ('primitives',
  'validate_dimension_compatibility',
  '(left: Dimension, right: Dimension) -> CompatibilityResult'),
 ('primitives',
  'validate_conversion_rule',
  '(rule: ConversionRule, source_unit: Unit, target_unit: Unit) -> '
  'CompatibilityResult'),
 ('primitives',
  'validate_unit_compatibility',
  '(source: Unit, target: Unit, conversion_or_not_applicable: ConversionRule | '
  'Applicability) -> CompatibilityResult'),
 ('primitives',
  'validate_resolution_detail',
  '(record: ResolutionDetail) -> CompatibilityResult'),
 ('primitives',
  'validate_quantity',
  '(quantity: Quantity, expected_context: QuantityContext) -> CompatibilityResult'),
 ('primitives',
  'convert_quantity_exact',
  '(quantity: Quantity, source_unit: Unit, target_unit: Unit, rule: ConversionRule) -> '
  'Quantity'),
 ('primitives',
  'validate_resource_service_compatibility',
  '(resource: ResourceType, service: ServiceType) -> CompatibilityResult'),
 ('primitives',
  'validate_region_compatibility',
  '(left: Region, right: Region, parent_or_not_applicable: Region | Applicability, '
  'aggregation_rule_or_not_applicable: ObjectRef | Applicability) -> '
  'CompatibilityResult'),
 ('primitives',
  'validate_boundary_compatibility',
  '(left: AccountingBoundary, right: AccountingBoundary, parent_or_not_applicable: '
  'AccountingBoundary | Applicability, aggregation_rule_or_not_applicable: ObjectRef | '
  'Applicability) -> CompatibilityResult'),
 ('primitives',
  'validate_sign_convention_compatibility',
  '(left_or_not_applicable: ObjectRef | Applicability, right_or_not_applicable: '
  'ObjectRef | Applicability) -> CompatibilityResult'),
 ('primitives',
  'validate_time_basis',
  '(left_or_not_applicable: ObjectRef | Applicability, right_or_not_applicable: '
  'ObjectRef | Applicability, rate_required: bool) -> CompatibilityResult'),
 ('primitives',
  'validate_clock_compatibility',
  '(left: ClockSystem, right: ClockSystem) -> CompatibilityResult'),
 ('primitives',
  'validate_horizon',
  '(horizon: Horizon, pending_effect_due_pairs: tuple[tuple[ObjectRef, ObjectRef], '
  '...]) -> CompatibilityResult'),
 ('primitives',
  'validate_uncertainty_record',
  '(record: UncertaintyRecord) -> CompatibilityResult'),
 ('registry',
  'allocate_scientific_id',
  '(registry: _NamespaceRegistryStore, claim: ScientificIdAllocationClaimV1) -> '
  'ScientificId'),
 ('registry',
  'register_draft',
  '(registry: _ObjectRegistryStore, record: RegistryRecord, aliases: '
  'tuple[AliasRecord, ...]=()) -> RegistryRecord'),
 ('registry',
  'resolve_ref',
  '(registry: _ObjectRegistryStore, reference: ObjectRef) -> RegistryRecord'),
 ('registry',
  'resolve_alias',
  '(registry: _ObjectRegistryStore, alias: str) -> RegistryRecord'),
 ('scheduling',
  'validate_schedule',
  '(record: Schedule | ComparatorSchedule | CoordinationEventDeclaration, /) -> None'),
 ('settlement',
  'validate_settlement_closure',
  '(closure: SettlementClosureRecord, quote: Quote, receipt: Receipt, group_receipt: '
  'GroupReceipt, child_actions: tuple[ChildActionRecord, ...], residual: '
  'GroupResidual, shares: tuple[SettlementShare, ...], causal_status: '
  'CausalIdentificationStatus, /) -> None'),
 ('state',
  'validate_state_record',
  '(record: SystemState, projection_contract: ProjectionContract, predecessor_epoch: '
  'Epoch | Applicability, /) -> None'),
 ('state',
  'validate_projection_contract',
  '(represented: RepresentedState, contract: ProjectionContract, /) -> None'),
 ('traces', 'project_canonical_trace_row', '(row: CanonicalTraceRow, /) -> bytes'),
 ('traces', 'frame_trace_row', '(row: CanonicalTraceRow, /) -> TraceRowFrame'),
 ('traces',
  'build_trace_prefix',
  '(frames: tuple[TraceRowFrame, ...], /) -> CanonicalTracePrefix'),
 ('traces',
  'extend_trace_prefix',
  '(prefix: CanonicalTracePrefix, appended: tuple[TraceRowFrame, ...], /) -> '
  'tuple[CanonicalTracePrefix, TraceExtensionEvidence]'),
 ('traces',
  'validate_complete_trace_evidence',
  '(prefix: CanonicalTracePrefix, evidence: CompleteTraceEvidence, /) -> '
  'TraceValidationResult'),
 ('traces',
  'build_minimum_reconstructable_trace',
  '(*, events: tuple[EventDeclaration, ...], phases: tuple[PhaseCommitRecord, ...], '
  'ownership: EpochUpdateOwnership, proposal_and_screen_refs: tuple[ObjectRef, ...], '
  'policy_memory_transaction_refs: tuple[ObjectRef, ...], prefix: '
  'CanonicalTracePrefix, commit_dispositions: tuple[CommitOutcome, ...], completeness: '
  'TraceCompleteness) -> MinimumReconstructableTrace'),
 ('traces',
  'build_run_trace_envelope',
  '(*, canonical_trace_digest: TraceDigest | Applicability, execution_binding_ref: '
  'ObjectRef | Applicability, execution_identity: ExecutionIdentity | Applicability, '
  'operational_evidence_refs: tuple[ObjectRef, ...], completeness: TraceCompleteness) '
  '-> RunTraceEnvelopeV1'),
 ('trust',
  'verify_ed25519_signature',
  '(public_key_base64url: str, message: CanonicalBytes, signature_base64url: str, /) '
  '-> None'),
 ('trust',
  'validate_trust_profile',
  '(profile: TrustProfileV1, installed_distribution_receipt: CanonicalBytes, '
  'state_store: AuthorizationStateStore, /) -> None'),
 ('trust',
  'validate_issuer_registry_snapshot',
  '(snapshot: IssuerRegistrySnapshotV1, root_proofs: tuple[TrustEvidenceEnvelopeV1, '
  '...], profile: TrustProfileV1, state_store: AuthorizationStateStore, /) -> '
  'tuple[AuthorizationCheckRecord, ...]'),
 ('trust',
  'validate_delegation_chain',
  '(credentials: tuple[DelegationCredentialV1, ...], proofs: '
  'tuple[TrustEvidenceEnvelopeV1, ...], issuer_snapshot: IssuerRegistrySnapshotV1, '
  'profile: TrustProfileV1, authorization: StageAuthorization, attested_utc: str, '
  'revocation: RevocationSnapshotV1, /) -> IssuerEntry'),
 ('trust',
  'validate_trusted_time_attestation',
  '(challenge: TrustedTimeChallengeV1, attestation: TrustedTimeAttestationV1, profile: '
  'TrustProfileV1, state_store: AuthorizationStateStore, /) -> None'),
 ('trust',
  'validate_revocation_snapshot',
  '(snapshot: RevocationSnapshotV1, root_proofs: tuple[TrustEvidenceEnvelopeV1, ...], '
  'profile: TrustProfileV1, attested_utc: str, state_store: AuthorizationStateStore, '
  '/) -> None'),
 ('provenance',
  'classify_execution_runtime_property',
  "(property_class: str, /) -> Literal['EXECUTION_SEMANTICS','RUN_METADATA']"),
 ('traces',
  'finalize_inert_trace_payload',
  '(trace_validation: TraceValidationResult, run_envelope: RunTraceEnvelopeV1, '
  'trace_artifact: ArtifactRecord, trace_bytes: bytes, /) -> ArtifactRecord'),
 ('traces',
  'finalize_trace_payload',
  '(*, trace_validation: TraceValidationResult, run_envelope: RunTraceEnvelopeV1, '
  'trace_artifact: ArtifactRecord, authorization_validation: '
  'AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord) -> '
  'NoReturn'),
 ('publication',
  'finalize_inert_manifest',
  '(expected_manifest_ref: ObjectRef, manifest: ExecutionResultManifest, artifacts: '
  'tuple[ArtifactRecord,...], artifact_bytes: tuple[bytes,...], source: '
  'SourceProvenance, runtime: RuntimeProvenance, environment: EnvironmentProvenance, '
  'semantics: ExecutionSemanticsProjection, trace_validation: TraceValidationResult, '
  'run_envelope: RunTraceEnvelopeV1, authorization_validation: '
  'AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord, /) -> '
  'ExecutionResultManifest'),
 ('publication',
  'finalize_execution_result_manifest',
  '(*, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], '
  'authorization_validation: AuthorizationValidationRecord, authorization_use: '
  'AuthorizationUseRecord) -> NoReturn'),
 ('recovery',
  'recover_inert_artifacts',
  '(manifest: ExecutionResultManifest, artifact: ArtifactRecord, artifact_bytes: '
  'bytes, destination_bytes_or_not_applicable: bytes|Applicability, trace_validation: '
  'TraceValidationResult, run_envelope: RunTraceEnvelopeV1, authorization_validation: '
  'AuthorizationValidationRecord, authorization_use: AuthorizationUseRecord, /) -> '
  'RecoveryRecord'),
 ('recovery',
  'recover_artifacts',
  '(*, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], '
  'authorization_validation: AuthorizationValidationRecord, authorization_use: '
  'AuthorizationUseRecord) -> NoReturn'),
 ('publication',
  'create_inert_correction_record',
  '(candidate: CorrectionRecord, original: ArtifactRecord, replacement: '
  'ArtifactRecord, original_bytes: bytes, replacement_bytes: bytes, '
  'authorization_validation: AuthorizationValidationRecord, authorization_use: '
  'AuthorizationUseRecord, /) -> CorrectionRecord'),
 ('publication',
  'create_correction_record',
  '(*, candidate: CorrectionRecord, original: ArtifactRecord, replacement: '
  'ArtifactRecord, authorization_validation: AuthorizationValidationRecord, '
  'authorization_use: AuthorizationUseRecord) -> NoReturn'),
 ('publication',
  'publish_inert_artifacts',
  '(store: _InertWriteOnceStore, candidate: PublicationRecord, manifest: '
  'ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], artifact_bytes: '
  'tuple[bytes,...], authorization_validation: AuthorizationValidationRecord, '
  'authorization_use: AuthorizationUseRecord, /) -> PublicationRecord'),
 ('publication',
  'publish_artifacts',
  '(*, manifest: ExecutionResultManifest, artifacts: tuple[ArtifactRecord,...], '
  'authorization_validation: AuthorizationValidationRecord, authorization_use: '
  'AuthorizationUseRecord) -> NoReturn'))
_I9_DIRECT_IMPORTS = (('canonical', 'errors'),
 ('identity', 'canonical'),
 ('identity', 'errors'),
 ('hashing', 'canonical'),
 ('hashing', 'errors'),
 ('hashing', 'identity'),
 ('envelopes', 'canonical'),
 ('envelopes', 'errors'),
 ('envelopes', 'hashing'),
 ('envelopes', 'identity'),
 ('numeric', 'canonical'),
 ('numeric', 'errors'),
 ('numeric', 'identity'),
 ('primitives', 'envelopes'),
 ('primitives', 'errors'),
 ('primitives', 'identity'),
 ('primitives', 'numeric'),
 ('registry', 'canonical'),
 ('registry', 'errors'),
 ('registry', 'envelopes'),
 ('registry', 'identity'),
 ('state', 'canonical'),
 ('state', 'primitives'),
 ('state', 'identity'),
 ('state', 'envelopes'),
 ('state', 'hashing'),
 ('state', 'errors'),
 ('conservation', 'primitives'),
 ('conservation', 'numeric'),
 ('conservation', 'identity'),
 ('conservation', 'envelopes'),
 ('conservation', 'errors'),
 ('distortion', 'state'),
 ('distortion', 'primitives'),
 ('distortion', 'numeric'),
 ('distortion', 'identity'),
 ('distortion', 'envelopes'),
 ('distortion', 'errors'),
 ('actions', 'state'),
 ('actions', 'primitives'),
 ('actions', 'identity'),
 ('actions', 'envelopes'),
 ('actions', 'errors'),
 ('network', 'state'),
 ('network', 'actions'),
 ('network', 'primitives'),
 ('network', 'identity'),
 ('network', 'envelopes'),
 ('network', 'registry'),
 ('network', 'errors'),
 ('commitments', 'actions'),
 ('commitments', 'network'),
 ('commitments', 'primitives'),
 ('commitments', 'identity'),
 ('commitments', 'envelopes'),
 ('commitments', 'errors'),
 ('observation', 'state'),
 ('observation', 'primitives'),
 ('observation', 'identity'),
 ('observation', 'envelopes'),
 ('observation', 'errors'),
 ('scheduling', 'actions'),
 ('scheduling', 'network'),
 ('scheduling', 'commitments'),
 ('scheduling', 'primitives'),
 ('scheduling', 'identity'),
 ('scheduling', 'envelopes'),
 ('scheduling', 'errors'),
 ('policy', 'observation'),
 ('policy', 'scheduling'),
 ('policy', 'primitives'),
 ('policy', 'identity'),
 ('policy', 'envelopes'),
 ('policy', 'hashing'),
 ('policy', 'errors'),
 ('causal', 'primitives'),
 ('causal', 'identity'),
 ('causal', 'envelopes'),
 ('causal', 'errors'),
 ('settlement', 'actions'),
 ('settlement', 'observation'),
 ('settlement', 'causal'),
 ('settlement', 'primitives'),
 ('settlement', 'numeric'),
 ('settlement', 'identity'),
 ('settlement', 'envelopes'),
 ('settlement', 'errors'),
 ('ledger', 'primitives'),
 ('ledger', 'identity'),
 ('ledger', 'envelopes'),
 ('ledger', 'hashing'),
 ('ledger', 'errors'),
 ('faults', 'primitives'),
 ('faults', 'identity'),
 ('faults', 'envelopes'),
 ('faults', 'hashing'),
 ('faults', 'errors'),
 ('experiment', 'conservation'),
 ('experiment', 'policy'),
 ('experiment', 'faults'),
 ('experiment', 'primitives'),
 ('experiment', 'identity'),
 ('experiment', 'envelopes'),
 ('experiment', 'hashing'),
 ('experiment', 'errors'),
 ('artifacts', 'experiment'),
 ('artifacts', 'ledger'),
 ('artifacts', 'primitives'),
 ('artifacts', 'identity'),
 ('artifacts', 'envelopes'),
 ('artifacts', 'hashing'),
 ('artifacts', 'errors'),
 ('atomic', 'primitives'),
 ('atomic', 'numeric'),
 ('atomic', 'identity'),
 ('atomic', 'envelopes'),
 ('atomic', 'errors'),
 ('interaction', 'atomic'),
 ('interaction', 'causal'),
 ('interaction', 'primitives'),
 ('interaction', 'numeric'),
 ('interaction', 'identity'),
 ('interaction', 'envelopes'),
 ('interaction', 'errors'),
 ('trust', 'canonical'),
 ('trust', 'identity'),
 ('trust', 'envelopes'),
 ('trust', 'hashing'),
 ('trust', 'errors'),
 ('authorization', 'trust'),
 ('authorization', 'experiment'),
 ('authorization', 'artifacts'),
 ('authorization', 'ledger'),
 ('authorization', 'registry'),
 ('authorization', 'identity'),
 ('authorization', 'hashing'),
 ('authorization', 'errors'),
 ('authorization_use', 'authorization'),
 ('authorization_use', 'ledger'),
 ('authorization_use', 'registry'),
 ('authorization_use', 'experiment'),
 ('authorization_use', 'identity'),
 ('authorization_use', 'hashing'),
 ('authorization_use', 'envelopes'),
 ('authorization_use', 'errors'),
 ('capabilities', 'authorization'),
 ('capabilities', 'policy'),
 ('capabilities', 'observation'),
 ('capabilities', 'experiment'),
 ('capabilities', 'hashing'),
 ('capabilities', 'identity'),
 ('capabilities', 'errors'),
 ('events', 'actions'),
 ('events', 'faults'),
 ('events', 'primitives'),
 ('events', 'identity'),
 ('events', 'hashing'),
 ('events', 'errors'),
 ('ownership', 'events'),
 ('ownership', 'state'),
 ('ownership', 'identity'),
 ('ownership', 'hashing'),
 ('ownership', 'errors'),
 ('durability', 'events'),
 ('durability', 'ownership'),
 ('durability', 'policy'),
 ('durability', 'ledger'),
 ('durability', 'hashing'),
 ('durability', 'errors'),
 ('traces', 'events'),
 ('traces', 'policy'),
 ('traces', 'state'),
 ('traces', 'experiment'),
 ('traces', 'artifacts'),
 ('traces', 'hashing'),
 ('traces', 'canonical'),
 ('traces', 'errors'),
 ('dynamic', 'network'),
 ('dynamic', 'commitments'),
 ('dynamic', 'scheduling'),
 ('dynamic', 'policy'),
 ('dynamic', 'events'),
 ('dynamic', 'ownership'),
 ('dynamic', 'state'),
 ('dynamic', 'primitives'),
 ('dynamic', 'identity'),
 ('dynamic', 'envelopes'),
 ('dynamic', 'canonical'),
 ('dynamic', 'capabilities'),
 ('dynamic', 'errors'),
 ('execution', 'authorization'),
 ('execution', 'authorization_use'),
 ('execution', 'capabilities'),
 ('execution', 'experiment'),
 ('execution', 'events'),
 ('execution', 'ownership'),
 ('execution', 'durability'),
 ('execution', 'traces'),
 ('execution', 'actions'),
 ('execution', 'state'),
 ('execution', 'policy'),
 ('execution', 'scheduling'),
 ('execution', 'faults'),
 ('execution', 'identity'),
 ('execution', 'errors'),
 ('execution', 'bridge'),
 ('execution', 'dynamic'),
 ('bridge', 'state'),
 ('bridge', 'distortion'),
 ('bridge', 'actions'),
 ('bridge', 'settlement'),
 ('bridge', 'scheduling'),
 ('bridge', 'causal'),
 ('bridge', 'interaction'),
 ('bridge', 'primitives'),
 ('bridge', 'numeric'),
 ('bridge', 'canonical'),
 ('bridge', 'envelopes'),
 ('bridge', 'identity'),
 ('bridge', 'errors'),
 ('bridge', 'capabilities'),
 ('provenance', 'experiment'),
 ('provenance', 'artifacts'),
 ('provenance', 'traces'),
 ('provenance', 'identity'),
 ('provenance', 'hashing'),
 ('provenance', 'errors'),
 ('recovery', 'artifacts'),
 ('recovery', 'traces'),
 ('recovery', 'durability'),
 ('recovery', 'authorization'),
 ('recovery', 'authorization_use'),
 ('recovery', 'ledger'),
 ('recovery', 'hashing'),
 ('recovery', 'errors'),
 ('publication', 'artifacts'),
 ('publication', 'provenance'),
 ('publication', 'recovery'),
 ('publication', 'authorization'),
 ('publication', 'authorization_use'),
 ('publication', 'ledger'),
 ('publication', 'hashing'),
 ('publication', 'errors'),
 ('validation', 'canonical'),
 ('validation', 'numeric'),
 ('validation', 'identity'),
 ('validation', 'hashing'),
 ('validation', 'primitives'),
 ('validation', 'capabilities'),
 ('validation', 'errors'))
_I9_T2_ALLOWLIST = (('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M1',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M1',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M1',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M1',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M2',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M2',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M2',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M2',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M3',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M3',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M3',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M3',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M4',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M4',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M4',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M4',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M5',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M5',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M5',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M5',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M6',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M6',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M6',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M6',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M7',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M7',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M7',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M7',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M8',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M8',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M8',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M8',
  'compute_comparator_interaction_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M9',
  'classify_joint_groups_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M9',
  'compute_group_measurement_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M9',
  'compute_same_baseline_nonadditivity_fixture'),
 ('V8',
  'tests/framework/fixtures/bridge_m1_m9_v1.json',
  '8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af',
  'M9',
  'compute_comparator_interaction_fixture'),
 ('V9',
  'tests/framework/fixtures/dynamic_static_v1.json',
  'cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d',
  'DC1',
  'validate_dynamic_static_identity'),
 ('V9',
  'tests/framework/fixtures/dynamic_static_v1.json',
  'cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d',
  'DC2',
  'validate_dynamic_static_identity'),
 ('V9',
  'tests/framework/fixtures/dynamic_static_v1.json',
  'cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d',
  'DC3',
  'validate_dynamic_static_identity'),
 ('V9',
  'tests/framework/fixtures/dynamic_static_v1.json',
  'cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d',
  'DC4',
  'validate_dynamic_static_identity'),
 ('V9',
  'tests/framework/fixtures/dynamic_static_v1.json',
  'cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d',
  'DC5',
  'validate_dynamic_static_identity'),
 ('V9',
  'tests/framework/fixtures/dynamic_static_v1.json',
  'cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d',
  'DC6',
  'validate_dynamic_static_identity'))
_I9_AUDIT_REGISTER = ('I-001',
 'I-002',
 'I-003',
 'I-004',
 'I-005',
 'I-006',
 'I-007',
 'I-008',
 'I-009',
 'I-010',
 'I-011',
 'I-012',
 'I-013',
 'I-014',
 'I-015',
 'I-016',
 'I-017',
 'I-018',
 'I-019',
 'I-020',
 'I-021',
 'I-022',
 'I-023',
 'I-024',
 'I-025',
 'I-026',
 'I-027',
 'I-028',
 'I-029',
 'I-030',
 'I-031',
 'I-032',
 'I-033',
 'I-034',
 'I-035',
 'I-036',
 'I-037',
 'I-038',
 'I-039',
 'I-040',
 'I-041',
 'I-042',
 'I-043',
 'I-044',
 'I-045',
 'I-046',
 'I-047',
 'I-048',
 'I-049',
 'I-050',
 'I-051',
 'I-052',
 'I-053',
 'I-054',
 'I-055',
 'I-056',
 'I-057',
 'I-058',
 'I-059',
 'I-060',
 'I-061',
 'I-062',
 'I-063',
 'I-064',
 'I-065',
 'I-066',
 'I-067',
 'TM-001',
 'TM-002',
 'TM-003',
 'TM-004',
 'TM-005',
 'TM-006',
 'TM-007',
 'TM-008',
 'TM-009',
 'TM-010',
 'TM-011',
 'TM-012',
 'TM-013',
 'TM-014',
 'TM-015',
 'TM-016',
 'TM-017',
 'TM-018',
 'TM-019',
 'TM-020',
 'TM-021',
 'TM-022',
 'TM-023',
 'TM-024',
 'TM-025',
 'TM-026',
 'TM-027',
 'TM-028',
 'TM-029',
 'TM-030',
 'TM-031',
 'TM-032',
 'TM-033',
 'TM-034',
 'TM-035',
 'TM-036',
 'TM-037',
 'TM-038',
 'TM-039',
 'TM-040',
 'TM-041',
 'TM-042',
 'TM-043',
 'TM-044',
 'TM-045',
 'I0-TM-001',
 'I0-TM-002',
 'I0-TM-003',
 'I0-TM-004',
 'I0-TM-005',
 'I0-TM-006',
 'I0-TM-007',
 'I0-TM-008',
 'I0-TM-009',
 'I0-TM-010',
 'I0-TM-011',
 'I0-TM-012',
 'I0-TM-013',
 'I0-TM-014',
 'I0-TM-015',
 'I0-TM-016',
 'I0-TM-017',
 'I0-TM-018',
 'I0-TM-019',
 'I0-TM-020',
 'I0-TM-021',
 'I0-TM-022',
 'I0-TM-023',
 'I0-TM-024',
 'I0-TM-025',
 'I0-TM-026')


def _validate_group_descriptor(
    group_id: str,
    validation_class: str,
    permitted_checks: tuple[str, ...],
    explicitly_unreachable: tuple[str, ...],
    exact_test_paths: tuple[str, ...],
    /,
) -> None:
    """Validate one exact inert V0-V11 group descriptor."""

    if not (
        type(group_id) is str
        and type(validation_class) is str
        and type(permitted_checks) is tuple
        and all(type(item) is str for item in permitted_checks)
        and type(explicitly_unreachable) is tuple
        and all(type(item) is str for item in explicitly_unreachable)
        and type(exact_test_paths) is tuple
        and all(type(item) is str for item in exact_test_paths)
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 group descriptor formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_descriptor', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    matching = tuple(row for row in _VALIDATION_GROUPS if row[0] == group_id)
    if len(matching) != 1:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 validation group is outside V0-V11',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_descriptor', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    expected = matching[0]
    if validation_class == "T3" or validation_class != expected[1]:
        _errors._fail(
                    _errors.FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                    'I-9 validation class is mismatched or escalated',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_descriptor', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if permitted_checks != expected[2] or exact_test_paths != expected[4]:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 checks or exact test paths differ from authority',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_descriptor', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if explicitly_unreachable != expected[3]:
        _errors._fail(
                    _errors.FailureCode.SCIENTIFIC_STATE_ADVANCE_FORBIDDEN,
                    'I-9 forbidden reachability set is incomplete',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_descriptor', "1.0.0"
                    ),
                    failure_ordinal=5,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )


def _validate_source_locks(
    rows: tuple[tuple[str, str, str, int, str], ...],
    /,
) -> None:
    """Validate the exact 73 controlling source-lock rows."""

    expected = (('AGENTS.md',
      '100644',
      '8610e8f07c3f462d6a4a6e2b4b677f56ffd89ae5',
      1853,
      'b23e3e26c336fe2db258e735f20e60e291d7f22cf9ee9d5e623d69ba141c002b'),
     ('.agents/skills/ebu-framework/SKILL.md',
      '100644',
      'b978bee8560f39d5e4aeb2f56461f7cfdab669ee',
      2977,
      '81ab31ce62d58f9058a38aafd511c8f98d7e1142640967bbd3daccd1068e810c'),
     ('.agents/skills/ebu-framework/references/profiles.md',
      '100644',
      '2aa798bb71f83d0fbc3ac5ba5542326c55e4676b',
      9791,
      'ab8e68b4c53630a9fe25367c8e40f0e51a17030e1428aaf38f0fafcda0eb8a5f'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md',
      '100644',
      '3fcd230a9daaba3ff885fb9438d1273f71264ed6',
      257943,
      'a9532ca3e4be11566cca67da368756221c8e5b88e09a69e9187af67fdf5a32b0'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md',
      '100644',
      'fbcceb0ce05f6d98f345658cf4cd6a86f1789334',
      429850,
      '2978e8b1de79c0e403841675cbdecab1e250e7ef3538216761028b34f7594460'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I1_PACKAGING_AMENDMENT.md',
      '100644',
      '7860e79bd5606fc0a923ecde3c89a03cf9cd0f53',
      45775,
      'a27aedf955c1e7bbf7039efc905951f516e070a2f36dc24b23c72d75f6a2f448'),
     ('unified_python_research_framework_packaging_contract.json',
      '100644',
      '32b1b2cc21023e2ff35171824968af548f0f7be3',
      54712,
      'edf2bd33361e7b2b2e083a10535c87e1e1cbbd36d21c2a3f3004f12b1743c351'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3_AUTHORITY_AMENDMENT.md',
      '100644',
      '01d61453d7ab149ddd3fa91f90d690e97ad299de',
      156290,
      'eaa3c80efa6ff0beae6f3ad8da3be67fb61f3cc5223b2067c256732ebf7bdfbc'),
     ('unified_python_research_framework_i3_contract.json',
      '100644',
      '9c7730652f160803ba52ce2b9bdb98d4cdee102e',
      345638,
      'd8acef250314e1405b048a324c9f855010f7927cc8760e2f827bba85253d7979'),
     ('unified_python_research_framework_i3_validation_contract.json',
      '100644',
      '3d06ab15713673050f29422ec2b21d85b257a938',
      49384569,
      '9ecd849f24ecd3e55883874263c10c181fea2e16a3000e87e4fc7fe02c2ccb2b'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I3C_SETTLEMENT_CAUSALITY_REPAIR_AUTHORITY_AMENDMENT.md',
      '100644',
      'b2b4ea415af775eb2c3bbcf24b4c52b0207c82ed',
      18759,
      '78e5b5e662cce41e2421e7e534309b6c9591436d39eb135f4bb71c72906e483a'),
     ('unified_python_research_framework_i3c_settlement_causality_repair_contract.json',
      '100644',
      'd16082f8462034ff0eab4bd1e3a7b02561f4c543',
      20877,
      '2ffc97f0bd93a219a56e324a806c01b0e48c5b8882b674aa1f67cc3ff0872c93'),
     ('unified_python_research_framework_i3c_settlement_causality_repair_predecessor_manifest.json',
      '100644',
      '245d1d22a2185f4718b21e6a6e70e28b9e3e506e',
      78166,
      'dc8a03c1ec92daf0f8edebd7c2a8b827541ea0b47bf7463a33d8d21f7092159d'),
     ('unified_python_research_framework_i3c_settlement_causality_repair_validation_contract.json',
      '100644',
      '08c528322d98b2497013ae363e552ee99a744b39',
      49734,
      '6cf24ff04632a70191b45d297d449df2a5ad662a6cd5408cd4bd5e8e1bab7a36'),
     ('ATOMIC_GENERATOR_FOUNDATION_AUTHORITY_AMENDMENT.md',
      '100644',
      '82b82d3d6824adcfe071a19bc0b530417f592eab',
      41359,
      'eb559a68163571d80bbe564d68a57a915e128090b1dbb26bfd9d1c4ec4a7b8d3'),
     ('atomic_generator_foundation_contract.json',
      '100644',
      'af244330dc0da36e0e56600cc6b731a9a7455348',
      42855,
      'b204f06bd11e7c605acc8afadbf82021fe5e3c1030e1f3f4c3659e71afd5d8a4'),
     ('atomic_generator_foundation_predecessor_manifest.json',
      '100644',
      '04b7fc5a8d68ba1c1ae07c31359367494676417a',
      75209,
      '26e6cd35b3f62cf39d6233e97822b04172bd662b90c7424cb0169099d18be6c6'),
     ('atomic_generator_foundation_validation_contract.json',
      '100644',
      '3900e0b1e02723c4e5813a71eec2e2a5c328c1f8',
      63776,
      'df54297b9c45220f28806304e30f9a654b338165ecd5970a0a2428b8e362a800'),
     ('ATOMIC_INTERACTION_DECLARATION_AUTHORITY_AMENDMENT.md',
      '100644',
      '875f069b189c07af458ec7816289dad27eed3744',
      115771,
      '80d83942d20745b9edeb3c5c8c05d052a616ef97ac9edb1af494d568acf68669'),
     ('atomic_interaction_declaration_contract.json',
      '100644',
      '3343c149367334018864a0c8522148097a455f7f',
      256881,
      '565cc3947d9a3abc99ece694ec823ad0f945dbb1c7634586bcf43f2e36c2549a'),
     ('atomic_interaction_declaration_predecessor_manifest.json',
      '100644',
      '20287bf07997bb9a075f5b4e4ea1752663d1c2d6',
      84137,
      'aa82f2b96b0be3f5a540c971baef77f492d64f5681a999385be9f6be20586a50'),
     ('atomic_interaction_declaration_validation_contract.json',
      '100644',
      '4004f732ff3b471befc90357f7072707ac751af9',
      1618558,
      'b40b80aef4a67826186fde40bf0b0ee9dec6e3db27c6809c2a2da075abe1b401'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I4_AUTHORITY_AMENDMENT.md',
      '100644',
      '1ec473016fbe5d087996d79a49cc4cf04481ad19',
      37767,
      '9414005a6f6fcfc9868c5094c350b43172c28d8510cac390a89c5c3c95b75365'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I4_GOVERNANCE_BOOTSTRAP_REQUIREMENTS.md',
      '100644',
      '00a48d379ba4fe5a14c7187c87549d11cfcba4e4',
      15143,
      '9cea9392375623e1b95727f6ff7761735133906011f63a260831ee7656133f9f'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I4_UQ25_DEPENDENCY_DECISION.md',
      '100644',
      '0c78cc5467867abe65959cc4cb69ae1972be69c2',
      11721,
      '863f0179da8db043ad98f5025cd99a0e09ccf5914f287ff2b45fcfb1730d372f'),
     ('unified_python_research_framework_i4_contract.json',
      '100644',
      '10ab1c5a1d643b479b9491d02243220c9aba68cd',
      86797,
      'dcd26f45dd33086acb29bc76710d3a9215a5d3b04878c54f9ec52a5970a6574d'),
     ('unified_python_research_framework_i4_governance_bootstrap_schema.json',
      '100644',
      'b92487d0877544c91ec5b961fbe7f5a0d58660c3',
      21567,
      'c496ae223f823b30e9e06782c9151a2f13e568d5ca84dd6df02fc52e901eff8d'),
     ('unified_python_research_framework_i4_predecessor_manifest.json',
      '100644',
      'a94371e58cc9dfd6cfa1443595281322ee5ac030',
      112093,
      'dbf67c1eda88a9dc053c5f0c75b92f164b2442f118d0f559746e01942f811b4e'),
     ('unified_python_research_framework_i4_uq25_dependency_contract.json',
      '100644',
      'cbeffd2b65e7e95cb0d7c4e5d051257cc24cb495',
      32485,
      '55b9a146927e0c37488dbf8489fc3d3d9afc05e8fc52bd7c402189fd5d598338'),
     ('unified_python_research_framework_i4_validation_contract.json',
      '100644',
      'be4cad0880c4b1e9c4524789b4f5c97893dd217f',
      324578,
      'a662ffee52bd4c9b8f926b23624d8d8fad4b64223e1fa61234f852f1a0c9b9ec'),
     ('POST_I4_LEGACY_TEST_COMPATIBILITY_AUTHORITY_AMENDMENT.md',
      '100644',
      '37fb88862ff8dfbdd3167c0f17dcd69aba2b1b96',
      24391,
      'ff7144fc819bc9145120a75689ae937e75503abbd77cee030cc19a9e615815f1'),
     ('post_i4_legacy_test_compatibility_contract.json',
      '100644',
      '3b07f0d4b698909bd3ace565df938599b0eae1a4',
      102133,
      '347f2fc9cd44bab3c1bfa1ae6b8b6da8c544ef13f1e41494d05b4bfffea2aa82'),
     ('post_i4_legacy_test_compatibility_predecessor_manifest.json',
      '100644',
      'f17b82611a47a3836e12d2ba273f957d6ba81b24',
      108670,
      '5ebe836d92202deef2b926c12887d0abbbf01c21162adb56163bf2ff58015e94'),
     ('post_i4_legacy_test_compatibility_validation_contract.json',
      '100644',
      '0080a02be141a60481717b2e2125617ec6e44550',
      67952,
      'fcb9c9bb2a42902dec60abe8dcfb2a9d0366f15d794262e56a142072b984c5a1'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I5_AUTHORITY_AMENDMENT.md',
      '100644',
      'b7ed713cd8c15c01cc0ce05943c7bf5c62f38828',
      62583,
      'd1f0c3bb526cd70a4e9274ca6b55a6ebfb0eedd00a43f7333f6b28563d9d9de7'),
     ('unified_python_research_framework_i5_contract.json',
      '100644',
      'dce3b854a96d9263badbd07a8df5f260e17a03c5',
      167648,
      '140f01f03953dee3ffbbe00bd869c5494a7f0bab1f65ca7690959b21d72af7d3'),
     ('unified_python_research_framework_i5_implementation_path_manifest.json',
      '100644',
      'ba9e1cbd1d79b49b09a4475f01df657157cab6c6',
      25632,
      '73af5094a331f127a45d11aa4b7a5e3d85d48aeaa63929f10569f96d25a9c885'),
     ('unified_python_research_framework_i5_predecessor_manifest.json',
      '100644',
      'f03460e9639aadcc733ba1baa88ee644680a5921',
      128622,
      'efc6301925a81f4a0e826d22d353445f08100395bda91dbf61171579663f8dd0'),
     ('unified_python_research_framework_i5_validation_contract.json',
      '100644',
      'd5d5feaa41a5db9dfbc6d0d4c427443afbb58b52',
      295581,
      '28b699b1c14c6180469db96c11f1e38aa0e3e9d6f55d35a86d6d526c65f97718'),
     ('POST_I5_LEGACY_TEST_COMPATIBILITY_AUTHORITY_AMENDMENT.md',
      '100644',
      '36560a9ac120ca01ca42ec800da34e45051bf095',
      28853,
      'af9f6ef723e0503e20f2f82f0c9c848aca372b436886054edbaf9899096c5f33'),
     ('post_i5_legacy_test_compatibility_contract.json',
      '100644',
      'cf8dd0d191cf18de39fcf4de3b321fb9aeb4069a',
      494664,
      'fdff8e43e187190ecdff4ad19eb711e95ec1a09f8c61fb1016879a3e557eaba6'),
     ('post_i5_legacy_test_compatibility_predecessor_manifest.json',
      '100644',
      '7a32eaa78269bb7cb2d1584173558a540d5a2817',
      128620,
      '96d0a1455d6f17c42785e4b153f1a5d6f92fbc50e155dce1f23d46aacc0f457f'),
     ('post_i5_legacy_test_compatibility_validation_contract.json',
      '100644',
      'e5b78d4b5851c77c631d3a7617e9d5a051dfc967',
      140068,
      'd642a665935142970567eecc1d21bc187963763ec07446cdb01867e430a51d56'),
     ('SEQUENTIAL_PARALLEL_BRIDGE.md',
      '100644',
      'e4c5dbec7e025dba102f5fa5b26843f891ad881b',
      53003,
      '34feaae6bdd8e7b9f8b8989933c847f725a1557609eb8fb059a563d9c3db4f10'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I6_AUTHORITY_AMENDMENT.md',
      '100644',
      '327155ad5911000184d0ecfed290b47b1d6dd18d',
      72509,
      '89d13a52b210790ee3ba4f613054db7dbaf8e32a8cde73ba2d426f0f04d6149e'),
     ('unified_python_research_framework_i6_contract.json',
      '100644',
      'c469b591af26addbe95c36a3baa2ecbe21b4691d',
      4128718,
      '2a2884f4da0accbdac3541a0672ce2449229711d091ab5e2caa18e19b5f999bd'),
     ('unified_python_research_framework_i6_implementation_path_manifest.json',
      '100644',
      '187408dbf0da5255d15057514a230aa8131ab9ab',
      27177,
      'fd6ca5f3118c8617fbeb1bad90708bb2e4f59cf2b08054e203d493dcc86371ed'),
     ('unified_python_research_framework_i6_predecessor_manifest.json',
      '100644',
      '41bfab7ba0ed2b06fe05b5213073b1fd869a9097',
      132264,
      '1550c84b545b9ef3c218af73fddcb063d671b39e5a928d92bdbd5f0d53729dda'),
     ('unified_python_research_framework_i6_validation_contract.json',
      '100644',
      '2f3b3397a67ce09b003fba386aa1f7dbf3d9783a',
      4103785,
      '0baa8a0dfefb18d3be88571a1936765a3f77467631de31753d68591a4ef93d23'),
     ('DYNAMIC_COORDINATION_FOUNDATION.md',
      '100644',
      '55c926b8d192272bddf2a2caba6f1a306691ca02',
      71170,
      '6f9bf4a95e307c5a44ad386aa5e680d917c13b547b3bdbaffab1e4d11a1d5a95'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I7_AUTHORITY_AMENDMENT.md',
      '100644',
      'c260f38c1009dd5873a0ce6745360de510e2b990',
      43795,
      '9293d4f5a787ac57b1e5ee4faf8a01d0058d1a502463fc5a15c27b86d7659b64'),
     ('unified_python_research_framework_i7_contract.json',
      '100644',
      '925f554203f7b638aa99fa232d56e56b2b2e019b',
      155280,
      '2c39979f395aa0a1df33bdbcc2108a31ca3bf7379ed151e2670b7a462ced6698'),
     ('unified_python_research_framework_i7_implementation_path_manifest.json',
      '100644',
      '0c239eafc6aa5487ee10cd5701bcdee90b6ac788',
      37531,
      '52267d3c391bd5da2d06089744a1637d45425af49109d36f9f8bfa0644794e53'),
     ('unified_python_research_framework_i7_predecessor_manifest.json',
      '100644',
      '0cb6994300c39c94c8128d777a89c337766d7fbc',
      135121,
      '7d8aa007170c935b2089bb5c0a5d20908a808fc8f1567d6ab4b357edcc1b17bb'),
     ('unified_python_research_framework_i7_validation_contract.json',
      '100644',
      'f0efbf534e20c87c4e84ca7088463d8d5ccc4aa6',
      184387,
      '2fc7780b8dcdb45f0dcf314543ae952911841790f0b03669c9fe20084cc6ee9b'),
     ('UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I8_AUTHORITY_AMENDMENT.md',
      '100644',
      'ba25aefc907253e12b11d40124f519d70fa43e9c',
      36953,
      '9cbb90ff9dac77d3fb481d257de2dafd79087c37c529b238129a46bc9088bfad'),
     ('unified_python_research_framework_i8_contract.json',
      '100644',
      '95b9b8bfca5438b7df03f7f5c119b9246bae1cca',
      268369,
      'c814b57d5435757f2ebb8f1cd3b17cfa6559a7860ee1db3efa93a3b2cf5e9606'),
     ('unified_python_research_framework_i8_implementation_path_manifest.json',
      '100644',
      '38589b0ed0b17164a08cee66f56bd2ec108876ac',
      44824,
      '9b042c306f4e84863f142b986561ff3c279f5b84e83e646ce433743fef30cd8f'),
     ('unified_python_research_framework_i8_predecessor_manifest.json',
      '100644',
      '55058350558b68a621642db79344e759b4c686e5',
      210768,
      '572b887a3a08d3f3fa2cca8f6308df13793b3b3154d940a43df944cb5fa90ca2'),
     ('unified_python_research_framework_i8_validation_contract.json',
      '100644',
      'c0924eadd9bb7a04d30832fca6805cdf58c345e9',
      528833,
      '71c087ed20e11375e0e6708d34d86d6dfab62764d86ef5247fd2439a1d5f705a'),
     ('POST_ATOMIC_OPEN_PROBLEM_REGISTER.md',
      '100644',
      '42ac0203543d57d773ea53f54c8a42aae66e8f85',
      32173,
      '957206891476ce360760ab23dac541ae6df5b5de8473bc6cf23c9c4b7ae631a5'),
     ('CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md',
      '100644',
      '09c97b66502bd252470ca40081207bf209b68608',
      40027,
      'b164b8079ebafbb86309f1c2a073c3467fc43356a719c95bd89227a1064e9d4a'),
     ('CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_FOUNDATION.md',
      '100644',
      '7c90cfc10aba9c44d07a5bd2c86b20dfaf562339',
      29970,
      '3820015fa540e86b191199a65c5740459f8fd5989ec2756564859bfb45507812'),
     ('CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_IMPLEMENTATION_STAGING_PLAN.md',
      '100644',
      '8fa6609714418524309c3c74c60165ede907d155',
      12509,
      '0e55e27a4ae1037d994651feb08177795780e631f455e2b4e8c3539e76cd0281'),
     ('CANONICAL_TOPOLOGY_MOTIF_PROGRAMME_REVIEW.md',
      '100644',
      '9e760620e98e561ef904103677cbc2d0dda8a5b7',
      67229,
      '2dc3daed05a46641e8de30fa8745fae0a8e7e46c51626804d0c5239c6305fb1d'),
     ('canonical_topology_motif_programme_contract.json',
      '100644',
      '46e3aac28e10f0fb87318236d95e1ad154383311',
      35884,
      '76833a3f58fa1dd68d4d6940bf8f8639464a298047b15d89e909c249a330b56d'),
     ('canonical_topology_motif_programme_predecessor_manifest.json',
      '100644',
      'a40cb8214684f063e2c0e1ab549968570f723e0b',
      113797,
      '1bf3a44919552d70f43c14c42c84b360e0d46d004caa46ac9883a7a5d85cfcdf'),
     ('canonical_topology_motif_programme_validation_contract.json',
      '100644',
      '8f1bbe026af892c139752b2e6d665627f782c914',
      39181,
      '2cbb9044a2607d8bb27619440be69755a9f30d35cfc00297d89955e8ae4288ba'),
     ('EBU_FUTURE_BOOKS_STRUCTURE.md',
      '100644',
      '654145ef732814047a0e5a45bdd0edb732104390',
      132360,
      '46d63759e2538ab37671be8ada9a61f1cabfec62fa6afe9063ed15a882698a6f'),
     ('pyproject.toml',
      '100644',
      '21bfad4d94f4a32f7ea3ebcb2fb9f46861ad16c6',
      399,
      '98c7112d08a2d0b4251d2b79bcf583bef8ce4560be55dcdddec6b3a6fdffbb4b'),
     ('requirements-framework.lock',
      '100644',
      '907bdff88be25741f04980ae5e6a769df2a61d4d',
      2036,
      '8d37c527af8caf5b168d397fbc35e651f98266c51aefc12a1ad415c97c34663a'),
     ('.github/workflows/tests.yml',
      '100644',
      '3359df95cc0dc426e8969a0587de141df2596a48',
      1610,
      '4d12f834e52bf92a723ab1e2c9723a9b395344320f3c95482b64d9133c766d23'),
     ('tests/framework/safety.py',
      '100644',
      'aed40a86f2a23f56fece345288db189ea59be4d0',
      4633,
      '40346595695d908a575dbc8fe8228564f2e182268a0822b93ce5b0db03246eb6'))
    if not (
        type(rows) is tuple
        and all(
            type(row) is tuple
            and len(row) == 5
            and type(row[0]) is str
            and type(row[1]) is str
            and type(row[2]) is str
            and type(row[3]) is int
            and type(row[4]) is str
            for row in rows
        )
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 source-lock row formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_source_locks', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if tuple((row[0], row[1], row[2]) for row in rows) != tuple(
        (row[0], row[1], row[2]) for row in expected
    ):
        _errors._fail(
                    _errors.FailureCode.DEPENDENCY_INTEGRITY_FAILURE,
                    'I-9 source path, mode, or object inventory differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_source_locks', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if tuple(row[3] for row in rows) != tuple(row[3] for row in expected):
        _errors._fail(
                    _errors.FailureCode.DEPENDENCY_INTEGRITY_FAILURE,
                    'I-9 source byte counts differ',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_source_locks', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if tuple(row[4] for row in rows) != tuple(row[4] for row in expected):
        _errors._fail(
                    _errors.FailureCode.HASH_MISMATCH,
                    'I-9 source raw hashes differ',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_source_locks', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )


def _validate_implementation_surface(
    changed_paths: tuple[str, ...],
    root_exports: tuple[str, ...],
    failure_codes: tuple[str, ...],
    public_signatures: tuple[tuple[str, str, str], ...],
    direct_edges: tuple[tuple[str, str], ...],
    dependency_locks: tuple[tuple[str, int, str], ...],
    /,
) -> None:
    """Validate the exact private I-9 implementation surface."""

    if not (
        type(changed_paths) is tuple
        and all(type(item) is str for item in changed_paths)
        and type(root_exports) is tuple
        and all(type(item) is str for item in root_exports)
        and type(failure_codes) is tuple
        and all(type(item) is str for item in failure_codes)
        and type(public_signatures) is tuple
        and all(
            type(row) is tuple
            and len(row) == 3
            and all(type(item) is str for item in row)
            for row in public_signatures
        )
        and type(direct_edges) is tuple
        and all(
            type(row) is tuple
            and len(row) == 2
            and all(type(item) is str for item in row)
            for row in direct_edges
        )
        and type(dependency_locks) is tuple
        and all(
            type(row) is tuple
            and len(row) == 3
            and type(row[0]) is str
            and type(row[1]) is int
            and type(row[2]) is str
            for row in dependency_locks
        )
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 implementation-surface formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if changed_paths != _I9_IMPLEMENTATION_PATHS:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 changed-path set differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if root_exports != _I9_ROOT_EXPORTS:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 root-export tuple differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if failure_codes != _I9_FAILURE_CODES:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 failure-code tuple differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if public_signatures != _I9_PUBLIC_SIGNATURES:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 public-signature rows differ',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=5,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    modules = tuple(dict.fromkeys(item for edge in _I9_DIRECT_IMPORTS for item in edge))
    indegree = {module: 0 for module in modules}
    outgoing = {module: [] for module in modules}
    graph_valid = direct_edges == _I9_DIRECT_IMPORTS and len(modules) == 40
    for source, target in direct_edges:
        if source not in outgoing or target not in indegree:
            graph_valid = False
            continue
        outgoing[source].append(target)
        indegree[target] += 1
        if (source == "validation" and target == "execution") or (
            source != "validation" and target == "validation"
        ):
            graph_valid = False
    ready = [module for module in modules if indegree[module] == 0]
    completed = 0
    while ready:
        source = ready.pop()
        completed += 1
        for target in outgoing[source]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if not graph_valid or completed != 40:
        _errors._fail(
                    _errors.FailureCode.SCIENTIFIC_STATE_ADVANCE_FORBIDDEN,
                    'I-9 import graph differs, cycles, or reaches execution',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=6,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    expected_dependency_locks = (('pyproject.toml',
      399,
      '98c7112d08a2d0b4251d2b79bcf583bef8ce4560be55dcdddec6b3a6fdffbb4b'),
     ('requirements-framework.lock',
      2036,
      '8d37c527af8caf5b168d397fbc35e651f98266c51aefc12a1ad415c97c34663a'))
    if dependency_locks != expected_dependency_locks:
        _errors._fail(
                    _errors.FailureCode.DEPENDENCY_INTEGRITY_FAILURE,
                    'I-9 dependency locks differ',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_implementation_surface', "1.0.0"
                    ),
                    failure_ordinal=7,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )


def _validate_forbidden_reachability(
    findings: tuple[tuple[str, str, str], ...],
    /,
) -> None:
    """Reject every closed I-9 forbidden-reachability finding."""

    capability_and_process = (
        "T3_INTERFACE",
        "T3_CAPABILITY",
        "PROCESS_ENTRY",
        "NETWORK_ENTRY",
        "SUBPROCESS_ENTRY",
        "DYNAMIC_IMPORT",
    )
    non_recovery_science = (
        "EXECUTION_IMPORT",
        "HISTORICAL_RUNNER",
        "HISTORICAL_FINALIZER",
        "GATE_PATH",
        "RESULT_PATH",
        "RUNNER_CALL",
        "FINALIZER_CALL",
        "MODEL_CALL",
        "POLICY_CALL",
        "SCIENTIFIC_CALL",
    )
    recovery = ("RECOVERY_EXECUTION",)
    closed_kinds = capability_and_process + non_recovery_science + recovery
    if not (
        type(findings) is tuple
        and all(
            type(row) is tuple
            and len(row) == 3
            and all(type(item) is str for item in row)
            and row[1] in closed_kinds
            for row in findings
        )
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 reachability finding formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_forbidden_reachability', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(row[1] in capability_and_process for row in findings):
        _errors._fail(
                    _errors.FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                    'I-9 capability or process boundary is reachable',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_forbidden_reachability', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(row[1] in non_recovery_science for row in findings):
        _errors._fail(
                    _errors.FailureCode.SCIENTIFIC_STATE_ADVANCE_FORBIDDEN,
                    'I-9 non-recovery scientific entry is reachable',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_forbidden_reachability', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(row[1] in recovery for row in findings):
        _errors._fail(
                    _errors.FailureCode.RECOVERY_EXECUTION_FORBIDDEN,
                    'I-9 recovery can reach execution',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_forbidden_reachability', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )


def _validate_group_evidence(
    rows: tuple[tuple[str, str, int, int, str, bool, str], ...],
    /,
) -> None:
    """Validate complete non-scientific V0-V11 evidence rows."""

    expected = (('V0',
      'PASS',
      0,
      3,
      '8eb04d39d8afad05ff81226bff0d2a60a8138422e46c6baa87cc9b571003e576',
      False,
      'T0'),
     ('V1',
      'PASS',
      0,
      3,
      '00932977bad37c1e3e3c6984ce84e0d51bacc7b08f2498ffef58517249906dd1',
      False,
      'T0_T1'),
     ('V2',
      'PASS',
      0,
      3,
      '68a78d08cfb7ce1ba67fb492d16a10f9d124fa233049e2733930890f03a3d269',
      False,
      'T0'),
     ('V3',
      'PASS',
      0,
      3,
      '9c45001cd829b3e10025ed42509c19229308d3aa02ca6a82bc70ad2cfacfaad0',
      False,
      'T0'),
     ('V4',
      'PASS',
      0,
      3,
      'b5d849881ff1f5fae97f3d4268155cb31565fda40957e57abae17aadd55ad155',
      False,
      'T1'),
     ('V5',
      'PASS',
      0,
      3,
      'e6bba08af48f291b6d98009743f84bc994c751d43b37cd31b87892181e89cf8f',
      False,
      'T1'),
     ('V6',
      'PASS',
      0,
      3,
      'bb1de815c9cd3282649ca6fa4efa0523db197451340b0e8ffcddb84bfef17b3a',
      False,
      'T0_T1'),
     ('V7',
      'PASS',
      0,
      3,
      '85f5015ac8b23b166ec5ac104770a5c0239d3d75351a5ac0373e4a8e495e0c32',
      False,
      'T1'),
     ('V8',
      'PASS',
      0,
      3,
      'bbe540456d03c55a74707084a73cebefe09dfd0cb87100adbf3268b543665af6',
      False,
      'T2'),
     ('V9',
      'PASS',
      0,
      3,
      '884becea724c42ea0fdbd236b054c276f80b719bb04ebfead2f84e6d15bbb824',
      False,
      'T2'),
     ('V10',
      'PASS',
      0,
      3,
      '5191874cbfbe154160dc62324ae4d1a4c338fa059ef2e4df31d181416e902aae',
      False,
      'T1'),
     ('V11',
      'PASS',
      0,
      3,
      'b392257cc7d06b8729fd4704e23c89fe10a5b1ccf106b47bd0c6d2f92e21aa96',
      False,
      'T0'))
    if not (
        type(rows) is tuple
        and all(
            type(row) is tuple
            and len(row) == 7
            and type(row[0]) is str
            and type(row[1]) is str
            and type(row[2]) is int
            and type(row[3]) is int
            and type(row[4]) is str
            and type(row[5]) is bool
            and type(row[6]) is str
            for row in rows
        )
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 group-evidence formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if tuple(row[0] for row in rows) != tuple(row[0] for row in expected):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 group-evidence set is incomplete or out of order',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(row[1] != "PASS" or row[2] != 0 for row in rows):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 group did not pass with zero exit',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(row[3] <= 0 for row in rows):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 group has no completed checks',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if tuple(row[4] for row in rows) != tuple(row[4] for row in expected):
        _errors._fail(
                    _errors.FailureCode.HASH_MISMATCH,
                    'I-9 group evidence hashes differ',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=5,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(row[5] for row in rows):
        _errors._fail(
                    _errors.FailureCode.SCIENTIFIC_STATE_ADVANCE_FORBIDDEN,
                    'I-9 group evidence reports scientific reachability',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=6,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    expected_classes = {row[0]: row[1] for row in _VALIDATION_GROUPS}
    if any(row[6] != expected_classes[row[0]] for row in rows):
        _errors._fail(
                    _errors.FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                    'I-9 group evidence class differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_group_evidence', "1.0.0"
                    ),
                    failure_ordinal=7,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )


def _validate_audit_mapping(
    rows: tuple[
        tuple[str, str, str, tuple[str, ...], tuple[str, ...]], ...
    ],
    /,
) -> None:
    """Validate the complete ordered 138-row inert audit mapping."""

    if not (
        type(rows) is tuple
        and all(
            type(row) is tuple
            and len(row) == 5
            and type(row[0]) is str
            and type(row[1]) is str
            and type(row[2]) is str
            and type(row[3]) is tuple
            and all(type(item) is str for item in row[3])
            and type(row[4]) is tuple
            and all(type(item) is str for item in row[4])
            for row in rows
        )
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 audit-mapping formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_audit_mapping', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if tuple(row[0] for row in rows) != _I9_AUDIT_REGISTER:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 audit register is incomplete or out of order',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_audit_mapping', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    dispositions = (
        "SATISFIED_BY_CODE_AND_COMPLETED_EVIDENCE",
        "SATISFIED_BY_STATIC_PROOF",
        "INERT_OPEN_ITEM_OUTSIDE_I9_IMPLEMENTATION",
        "NAMED_NON_RELEASE_BLOCKER",
    )
    if any(row[1] not in dispositions for row in rows):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 audit disposition is outside the closed domain',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_audit_mapping', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(
        row[1] in dispositions[:2] and (not row[2] or not row[3])
        for row in rows
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 satisfied mapping evidence is insufficient',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_audit_mapping', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if any(
        (row[1] == "NAMED_NON_RELEASE_BLOCKER" and not row[2])
        or (
            row[1] == "INERT_OPEN_ITEM_OUTSIDE_I9_IMPLEMENTATION"
            and (not row[2] or not row[4])
        )
        for row in rows
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 blocker or open-boundary mapping is insufficient',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_validate_audit_mapping', "1.0.0"
                    ),
                    failure_ordinal=5,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )


def _authorize_t2_fixture(
    group_id: str,
    fixture_path: str,
    fixture_raw_sha256: SourceFileRawSha256,
    case_id: str,
    authorized_interface: str,
    /,
) -> T2FixtureCapability:
    """Validate I-9 T2 authority, then delegate once to the accepted issuer."""

    if not (
        type(group_id) is str
        and type(fixture_path) is str
        and type(fixture_raw_sha256) is SourceFileRawSha256
        and type(case_id) is str
        and type(authorized_interface) is str
    ):
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 T2 authority formation is invalid',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_authorize_t2_fixture', "1.0.0"
                    ),
                    failure_ordinal=1,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    group_rows = tuple(row for row in _VALIDATION_GROUPS if row[0] == group_id)
    if len(group_rows) != 1 or group_rows[0][1] != "T2":
        _errors._fail(
                    _errors.FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
                    'I-9 T2 group is unauthorized',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_authorize_t2_fixture', "1.0.0"
                    ),
                    failure_ordinal=2,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    group_allowlist = tuple(row for row in _I9_T2_ALLOWLIST if row[0] == group_id)
    if not group_allowlist or fixture_path != group_allowlist[0][1]:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 T2 fixture path differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_authorize_t2_fixture', "1.0.0"
                    ),
                    failure_ordinal=3,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    raw_hex = fixture_raw_sha256.hex_digest
    if raw_hex != group_allowlist[0][2]:
        _errors._fail(
                    _errors.FailureCode.HASH_MISMATCH,
                    'I-9 T2 fixture raw hash differs',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_authorize_t2_fixture', "1.0.0"
                    ),
                    failure_ordinal=4,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    if (
        group_id,
        fixture_path,
        raw_hex,
        case_id,
        authorized_interface,
    ) not in _I9_T2_ALLOWLIST:
        _errors._fail(
                    _errors.FailureCode.VALIDATOR_BYPASS_FORBIDDEN,
                    'I-9 T2 case or interface is outside the allowlist',
                    stage=_errors.FailureStage.I9,
                    interface_ref=_errors.FailureInterfaceRef(
                        "ebu_framework.validation", '_authorize_t2_fixture', "1.0.0"
                    ),
                    failure_ordinal=5,
                    scientific_status_effect=(
                        _errors.ScientificStatusEffect.UNSTARTED_PRESERVED
                    ),
                    retry_class=_errors.RetryClass.FORBIDDEN,
                )
    return _capabilities._issue_t2_fixture_capability(
        fixture_path=fixture_path,
        fixture_raw_sha256=fixture_raw_sha256,
        case_id=case_id,
        authorized_interface=authorized_interface,
    )


__all__ = ()
