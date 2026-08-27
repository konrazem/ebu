"""Exact synthetic Framework I-8 provenance, recovery, and publication vectors."""

from __future__ import annotations

import ast
from dataclasses import fields, replace
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import re
from typing import Any
import unittest

import ebu_framework as framework
from ebu_framework.artifacts import (
    ArtifactRecord,
    CorrectionRecord,
    ExecutionResultManifest,
    FigureArtifact,
    PublicationRecord,
    ResultArtifact,
    SummaryArtifact,
)
from ebu_framework.authorization import (
    AuthorizationCheckRecord,
    AuthorizationCheckStatus,
    AuthorizationValidationRecord,
    AuthorizationValidationStatus,
    AuthorizedOperation,
)
from ebu_framework.authorization_use import AuthorizationUseRecord, AuthorizationUseStatus
from ebu_framework.canonical import encode_ecj1
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.experiment import (
    ExecutionBinding,
    ExecutionIdentity,
    ExecutionMode,
    RuntimeMetadata,
)
from ebu_framework.hashing import (
    compute_artifact_byte_hash,
    compute_canonical_trace_prefix_hash,
    compute_execution_semantics_hash,
    compute_object_content_hash,
    compute_run_envelope_digest,
)
from ebu_framework.identity import (
    ArtifactByteHash,
    AuthorizationUseKey,
    CanonicalScientificTracePayloadHash,
    CanonicalTracePrefixHash,
    ExecutionSemanticsHash,
    ObjectContentHash,
    ObjectRef,
    PolicyMemoryPayloadHash,
    ScientificId,
    SemanticVersion,
    SourceFileRawSha256,
    StatePayloadHash,
)
from ebu_framework.numeric import IntegerV1
from ebu_framework.primitives import ResolutionDetail, ResolutionState
from ebu_framework.provenance import (
    EnvironmentProvenance,
    ExecutionSemanticsProjection,
    RuntimeProvenance,
    SourceProvenance,
    classify_execution_runtime_property,
)
from ebu_framework.publication import (
    PublicationReceipt,
    _receipt_ref,
    _make_inert_write_once_store,
    create_correction_record,
    create_inert_correction_record,
    finalize_execution_result_manifest,
    finalize_inert_manifest,
    publish_artifacts,
    publish_inert_artifacts,
)
from ebu_framework.recovery import (
    RecoveryClassification,
    RecoveryRecord,
    recover_artifacts,
    recover_inert_artifacts,
)
from ebu_framework.traces import (
    CanonicalTracePrefix,
    CompleteTraceEvidence,
    RunTraceEnvelopeV1,
    TraceCompleteness,
    TraceValidationResult,
    TraceValidationStatus,
    finalize_inert_trace_payload,
    finalize_trace_payload,
)
from ebu_framework.trust import TrustedTimeAttestationV1


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "unified_python_research_framework_i8_validation_contract.json"
MECHANICAL_PATH = ROOT / "unified_python_research_framework_i8_contract.json"
PATHS_PATH = ROOT / "unified_python_research_framework_i8_implementation_path_manifest.json"
PREDECESSOR_PATH = ROOT / "unified_python_research_framework_i8_predecessor_manifest.json"
CONTRACT = json.loads(CONTRACT_PATH.read_bytes())
MECHANICAL = json.loads(MECHANICAL_PATH.read_bytes())
PATHS = json.loads(PATHS_PATH.read_bytes())
PREDECESSOR = json.loads(PREDECESSOR_PATH.read_bytes())
CLCD = json.loads((ROOT / "closed_loop_correction_diagnostics_contract.json").read_bytes())
VECTORS = tuple(CONTRACT["vectors"])
VERSION = SemanticVersion("1.0.0")


def _normalize(label: str) -> str:
    return re.sub(r"[^a-z0-9._-]", "-", label.lower()).strip("-")


def _ref(label: str) -> ObjectRef:
    normalized = _normalize(label)
    digest = hashlib.sha256(f"i8-ref:{normalized}".encode("utf-8")).hexdigest()
    return ObjectRef(
        object_id=ScientificId(f"ebu:validation:i8:{normalized}"),
        object_version=VERSION,
        object_content_hash=ObjectContentHash(f"sha256:{digest}"),
    )


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _ordered(*references: ObjectRef) -> tuple[ObjectRef, ...]:
    return tuple(sorted(references, key=_ref_key))


def _record_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _project(value: object) -> object:
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    if isinstance(value, Applicability):
        return value.value
    if isinstance(value, (ArtifactByteHash, ExecutionSemanticsHash, SourceFileRawSha256)):
        return str(value)
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    if hasattr(value, "value"):
        return value.value  # type: ignore[union-attr]
    return value


def _envelope(label: str, payload: object) -> CommonObjectEnvelope:
    object_id = _ref(label).object_id
    kind_id = _ref(label + "-kind").object_id
    schema_id = _ref(label + "-schema").object_id
    content_hash = compute_object_content_hash(
        object_id=object_id,
        object_kind=str(kind_id),
        schema_id=schema_id,
        schema_version=VERSION,
        object_version=VERSION,
        authority_refs=(_ref("authority"),),
        supersedes_ref=None,
        object_content_payload=payload,
    )
    return CommonObjectEnvelope(
        object_id=object_id,
        object_kind_id=kind_id,
        schema_id=schema_id,
        schema_version=VERSION,
        object_version=VERSION,
        authority_refs=(_ref("authority"),),
        supersedes_ref=Applicability.NOT_APPLICABLE,
        object_content_payload=bytes(encode_ecj1(payload)),
        object_content_hash=content_hash,
        lifecycle_status=LifecycleStatus.DRAFT,
        record_metadata_ref=Applicability.NOT_APPLICABLE,
    )


def _seal(runtime: type, label: str, values: dict[str, object]) -> object:
    provisional = runtime(envelope=_envelope(label, {}), **values)
    return replace(provisional, envelope=_envelope(label, provisional.to_ecj1()))


def _reseal(record: object, label: str, **changes: object) -> object:
    values = {
        field.name: getattr(record, field.name)
        for field in fields(record)
        if field.name != "envelope"
    }
    values.update(changes)
    return _seal(type(record), label, values)


def _resolution(state: ResolutionState) -> ResolutionDetail:
    na = Applicability.NOT_APPLICABLE
    if state is ResolutionState.PRESENT:
        return ResolutionDetail(
            state=state,
            present_value_ref=_ref("resolution-present"),
            completed_part_refs=(_ref("resolution-part"),),
            missing_part_refs=(),
            due_condition_ref=na,
            failure=na,
            boundary_edge_ref=na,
            reason_ref=na,
        )
    if state is ResolutionState.PARTIAL:
        return ResolutionDetail(
            state=state,
            present_value_ref=na,
            completed_part_refs=(_ref("resolution-part"),),
            missing_part_refs=(_ref("resolution-missing"),),
            due_condition_ref=na,
            failure=na,
            boundary_edge_ref=na,
            reason_ref=_ref("partial-reason"),
        )
    if state is ResolutionState.UNRESOLVED:
        return ResolutionDetail(
            state=state,
            present_value_ref=na,
            completed_part_refs=(),
            missing_part_refs=(_ref("resolution-missing"),),
            due_condition_ref=na,
            failure=na,
            boundary_edge_ref=na,
            reason_ref=_ref("unresolved-reason"),
        )
    return ResolutionDetail(
        state=ResolutionState.NOT_APPLICABLE,
        present_value_ref=na,
        completed_part_refs=(),
        missing_part_refs=(),
        due_condition_ref=na,
        failure=na,
        boundary_edge_ref=na,
        reason_ref=na,
    )


def _execution_identity(binding_ref: ObjectRef | None = None) -> ExecutionIdentity:
    return ExecutionIdentity(
        identity_ref=_ref("execution-identity"),
        execution_mode=ExecutionMode.DETERMINISTIC,
        configuration_ref=_ref("configuration"),
        binding_ref=binding_ref or _ref("binding"),
        attempt_ordinal=IntegerV1(1),
    )


def _execution_binding() -> ExecutionBinding:
    values: dict[str, object] = {
        "accepted_configuration_ref": _ref("configuration"),
        "implementation_refs": (_ref("implementation"),),
        "source_refs": (_ref("source"),),
        "entrypoint_semantics_ref": _ref("entrypoint"),
        "runtime_constraint_refs": (_ref("runtime"),),
        "operational_exclusions": (),
        "policy_memory_transition_contract_refs": (),
        "fault_delivery_contract_refs": (_ref("fault-delivery"),),
        "event_order_contract_ref": _ref("event-order"),
        "numerical_policy_contract_refs": (_ref("numerical-policy"),),
        "information_capability_contract_ref": _ref("information-capability"),
        "trace_schema_ref": _ref("trace-schema"),
        "result_schema_ref": _ref("result-schema"),
        "stochastic_contract_ref": Applicability.NOT_APPLICABLE,
    }
    values["execution_semantics_hash"] = compute_execution_semantics_hash(
        accepted_configuration_ref=values["accepted_configuration_ref"],
        implementation_refs=values["implementation_refs"],
        source_refs=values["source_refs"],
        implementation_entrypoint_semantics=values["entrypoint_semantics_ref"].to_ecj1(),
        science_affecting_runtime_constraints=[
            item.to_ecj1() for item in values["runtime_constraint_refs"]
        ],
        science_affecting_operational_exclusions=[],
        policy_memory_transition_contracts_or_not_applicable="NOT_APPLICABLE",
        fault_injection_delivery_contracts_or_not_applicable=[
            item.to_ecj1() for item in values["fault_delivery_contract_refs"]
        ],
        event_order_contract=values["event_order_contract_ref"].to_ecj1(),
        arithmetic_and_numerical_policy_contracts=[
            item.to_ecj1() for item in values["numerical_policy_contract_refs"]
        ],
        information_capability_contract=values[
            "information_capability_contract_ref"
        ].to_ecj1(),
        canonical_scientific_trace_schema_ref=values["trace_schema_ref"],
        scientific_result_schema_ref=values["result_schema_ref"],
        stochastic_generator_and_stream_contract_or_not_applicable="NOT_APPLICABLE",
    )
    return _seal(ExecutionBinding, "binding", values)  # type: ignore[return-value]


def _fixture(name: str) -> tuple[bytes, ArtifactByteHash, SourceFileRawSha256]:
    row = CONTRACT["fixture_inventory"]["dummy_bytes"][name]
    payload = bytes.fromhex(row["hex"])
    return (
        payload,
        ArtifactByteHash(row["artifact_byte_hash"]),
        SourceFileRawSha256(row["source_raw_sha256"]),
    )


def _artifact(name: str, *, present: bool = True, hash_name: str | None = None) -> ArtifactRecord:
    _, artifact_hash, _ = _fixture(hash_name or name)
    kind = "trace-kind" if name == "TRACE_PREFIX" else "result-kind"
    completeness = _resolution(ResolutionState.PRESENT)
    if not present:
        completeness = replace(
            completeness,
            present_value_ref=Applicability.NOT_APPLICABLE,
        )
    values = {
        "artifact_kind_ref": _ref(kind),
        "artifact_byte_hash": artifact_hash,
        "media_type": "text/plain" if name == "TRACE_PREFIX" else "application/octet-stream",
        "schema_ref": _ref("artifact-schema"),
        "producing_execution_identity": _execution_identity(),
        "content_ref": _ref("artifact-content") if present else Applicability.NOT_APPLICABLE,
        "completeness": completeness,
    }
    return _seal(ArtifactRecord, name.lower(), values)  # type: ignore[return-value]


def _manifest(state: str, artifact: ArtifactRecord | None = None) -> ExecutionResultManifest:
    artifact = artifact or _artifact("RESULT_A")
    na = Applicability.NOT_APPLICABLE
    if state == "PRESENT_AS_COMPLETE":
        values = {
            "ordered_artifact_refs": (_record_ref(artifact),),
            "terminal_state_ref": _ref("terminal-state"),
            "last_confirmed_state_ref": _ref("terminal-state"),
            "required_artifact_kind_refs": (artifact.artifact_kind_ref,),
            "missing_artifact_kind_refs": (),
            "completeness": _resolution(ResolutionState.PRESENT),
        }
    elif state == "PARTIAL":
        values = {
            "ordered_artifact_refs": (_record_ref(artifact),),
            "terminal_state_ref": na,
            "last_confirmed_state_ref": _ref("last-confirmed-state"),
            "required_artifact_kind_refs": (artifact.artifact_kind_ref,),
            "missing_artifact_kind_refs": (),
            "completeness": _resolution(ResolutionState.PARTIAL),
        }
    elif state == "UNRESOLVED":
        values = {
            "ordered_artifact_refs": (),
            "terminal_state_ref": na,
            "last_confirmed_state_ref": _ref("last-confirmed-state"),
            "required_artifact_kind_refs": (_ref("result-kind"),),
            "missing_artifact_kind_refs": (_ref("result-kind"),),
            "completeness": _resolution(ResolutionState.UNRESOLVED),
        }
    else:
        values = {
            "ordered_artifact_refs": (),
            "terminal_state_ref": na,
            "last_confirmed_state_ref": na,
            "required_artifact_kind_refs": (),
            "missing_artifact_kind_refs": (),
            "completeness": _resolution(ResolutionState.NOT_APPLICABLE),
        }
    values.update(
        {
            "configuration_ref": _ref("configuration"),
            "binding_ref": _ref("binding"),
            "execution_identity": _execution_identity(),
            "trace_completeness_ref": _ref("trace-completeness"),
            "policy_memory_ref": na,
        }
    )
    return _seal(ExecutionResultManifest, "manifest-" + state.lower(), values)  # type: ignore[return-value]


def _prefix() -> CanonicalTracePrefix:
    state_hash = StatePayloadHash(
        "sha256:"
        + hashlib.sha256(b"i8-digest:StatePayloadHash:prefix-state").hexdigest()
    )
    digest = compute_canonical_trace_prefix_hash(
        trace_header={"validation": "i8"},
        ordered_rows=(),
        confirmed_row_count=0,
        last_confirmed_state_payload_hash=state_hash,
        last_confirmed_policy_memory_payload_hash_or_not_applicable="NOT_APPLICABLE",
        last_confirmed_augmented_replay_state_hash_or_not_applicable="NOT_APPLICABLE",
        completeness_state="PARTIAL_DURABLE_PREFIX",
    )
    return CanonicalTracePrefix(row_frames=(), row_count=0, prefix_digest=digest)


def _trace_validation(state: str) -> TraceValidationResult:
    if state == "AMBIGUOUS":
        return TraceValidationResult(
            status=TraceValidationStatus.AMBIGUOUS,
            confirmed_prefix=Applicability.NOT_APPLICABLE,
            complete_evidence=Applicability.NOT_APPLICABLE,
        )
    prefix = _prefix()
    if state == "VALID_PREFIX":
        return TraceValidationResult(
            status=TraceValidationStatus.VALID_PREFIX,
            confirmed_prefix=prefix,
            complete_evidence=Applicability.NOT_APPLICABLE,
        )
    complete = CompleteTraceEvidence(
        trace_digest=CanonicalScientificTracePayloadHash(
            "sha256:"
            + hashlib.sha256(
                b"i8-digest:CanonicalScientificTracePayloadHash:complete-trace"
            ).hexdigest()
        ),
        last_prefix_digest=prefix.prefix_digest,
        confirmed_row_count=0,
        completeness=TraceCompleteness.COMPLETE,
        terminal_state_hash=StatePayloadHash(
            "sha256:"
            + hashlib.sha256(b"i8-digest:StatePayloadHash:terminal-state").hexdigest()
        ),
        terminal_memory_hash=PolicyMemoryPayloadHash(
            "sha256:"
            + hashlib.sha256(
                b"i8-digest:PolicyMemoryPayloadHash:terminal-memory"
            ).hexdigest()
        ),
    )
    return TraceValidationResult(
        status=TraceValidationStatus.VALID_COMPLETE,
        confirmed_prefix=prefix,
        complete_evidence=complete,
    )


def _run_envelope(state: str, *, binding_ref: ObjectRef | None = None) -> RunTraceEnvelopeV1:
    validation = _trace_validation(state)
    identity = _execution_identity()
    binding = binding_ref or _ref("binding")
    digest = (
        validation.complete_evidence.trace_digest
        if state == "VALID_COMPLETE"
        else Applicability.NOT_APPLICABLE
    )
    projection = [
        str(digest) if digest is not Applicability.NOT_APPLICABLE else "NOT_APPLICABLE",
        str(binding.object_id),
        str(identity.identity_ref.object_id),
        "0",
        (
            TraceCompleteness.COMPLETE.value
            if state == "VALID_COMPLETE"
            else TraceCompleteness.PARTIAL_DURABLE_PREFIX.value
        ),
    ]
    return RunTraceEnvelopeV1(
        canonical_trace_digest=digest,
        execution_binding_ref=binding,
        execution_identity=identity,
        operational_evidence_refs=(),
        completeness=(
            TraceCompleteness.COMPLETE
            if state == "VALID_COMPLETE"
            else TraceCompleteness.PARTIAL_DURABLE_PREFIX
        ),
        envelope_digest=compute_run_envelope_digest(projection),
    )


def _authorization(
    operation: AuthorizedOperation,
    targets: tuple[ObjectRef, ...],
    manifest: ExecutionResultManifest | None = None,
    identity: ExecutionIdentity | None = None,
    *,
    use_operation: AuthorizedOperation | None = None,
) -> tuple[AuthorizationValidationRecord, AuthorizationUseRecord]:
    manifest = manifest or _manifest("PRESENT_AS_COMPLETE")
    identity = identity or manifest.execution_identity
    targets = tuple(sorted(targets, key=lambda item: bytes(encode_ecj1(item.to_ecj1()))))
    use_key = AuthorizationUseKey(
        "sha256:"
        + hashlib.sha256(
            f"i8-authorization:{operation.value}".encode("utf-8")
        ).hexdigest()
    )
    attestation = TrustedTimeAttestationV1(
        trust_profile_ref=_ref("trust-profile"),
        time_service_id=ScientificId("ebu:service:validation:time"),
        signer_key_id="ed25519:" + "0" * 64,
        challenge_base64url="A" * 43,
        authorization_use_key=use_key,
        attested_utc="2000-01-01T00:00:00.000000Z",
        service_sequence=0,
        issued_at="2000-01-01T00:00:00.000000Z",
        expires_at="2000-01-02T00:00:00.000000Z",
        signature_base64url="AA",
    )
    check = AuthorizationCheckRecord(
        check_ordinal=1,
        check_name="I8_SYNTHETIC_VALIDATION",
        status=AuthorizationCheckStatus.PASS,
        failure_code_or_not_applicable=Applicability.NOT_APPLICABLE,
        evidence_refs=(),
    )
    validation = AuthorizationValidationRecord(
        authorization_ref=_ref("authorization"),
        authorization_use_key=use_key,
        status=AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED,
        completed_checks=(check,),
        effective_issuer_id=ScientificId("ebu:issuer:validation:i8"),
        effective_stages=("I-8",),
        effective_operations=(operation.value,),
        effective_target_object_refs=targets,
        trusted_time_attestation=attestation,
        revocation_snapshot_ref=_ref("revocation-snapshot"),
        failure=Applicability.NOT_APPLICABLE,
    )
    use = AuthorizationUseRecord(
        authorization_use_key=use_key,
        authorization_ref=_ref("authorization"),
        requested_operation=use_operation or operation,
        target_object_refs=targets,
        accepted_configuration_ref_or_not_applicable=identity.configuration_ref,
        accepted_execution_binding_ref_or_not_applicable=identity.binding_ref,
        execution_identity_or_not_applicable=identity,
        consumed_utc="2000-01-01T00:00:00.000000Z",
        store_id=ScientificId("ebu:store:validation:i8"),
        ledger_entry_id=ScientificId("ebu:entry:validation:i8"),
        status=AuthorizationUseStatus.CONSUMED,
    )
    return validation, use


def _provenance() -> tuple[
    SourceProvenance,
    RuntimeProvenance,
    EnvironmentProvenance,
    ExecutionSemanticsProjection,
]:
    _, artifact_hash, raw_hash = _fixture("RESULT_A")
    execution_classes = tuple(MECHANICAL["closed_domains"]["section7_execution_semantics_classes"])
    run_classes = tuple(MECHANICAL["closed_domains"]["section7_run_metadata_classes"])
    source = SourceProvenance(
        repository_identity_ref=_ref("repository"),
        source_commit="83fd6040fde6d72ab0e938ab72c38f9246520b58",
        ordered_source_refs=(_ref("source"),),
        ordered_source_raw_sha256=(raw_hash,),
        ordered_source_artifact_byte_hashes=(artifact_hash,),
        dirty_source_state="FORBIDDEN",
        completeness=_resolution(ResolutionState.PRESENT),
    )
    runtime = RuntimeProvenance(
        interpreter_ref=_ref("interpreter"),
        dependency_closure_refs=(_ref("dependency"),),
        os_architecture_contract_ref=_ref("os-architecture"),
        numerical_hardware_backend_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        arithmetic_contract_refs=(_ref("arithmetic"),),
        concurrency_contract_ref=_ref("concurrency"),
        entry_semantics_ref=_ref("entry-semantics"),
        fault_delivery_contract_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        stochastic_contract_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        included_property_classes=execution_classes,
        completeness=_resolution(ResolutionState.PRESENT),
    )
    environment = EnvironmentProvenance(
        normalized_allowlist_refs=(_ref("allowlist"),),
        operational_exclusion_refs=(_ref("exclusion"),),
        blocked_nonread_property_names=("validation-i8",),
        run_specific_property_classes=run_classes,
        run_specific_evidence_refs=tuple(
            _ref(f"run-evidence-{index}") for index in range(1, 13)
        ),
        completeness=_resolution(ResolutionState.PRESENT),
    )
    binding = _execution_binding()
    semantics = ExecutionSemanticsProjection(
        accepted_configuration_ref=binding.accepted_configuration_ref,
        binding=binding,
        execution_semantics_hash=binding.execution_semantics_hash,
        source_provenance_ref=_ref("source-provenance"),
        runtime_provenance_ref=_ref("runtime-provenance"),
        environment_provenance_ref=_ref("environment-provenance"),
        included_property_classes=execution_classes,
        excluded_run_metadata_classes=run_classes,
    )
    return source, runtime, environment, semantics


def _publication_candidate(
    manifest: ExecutionResultManifest,
    artifact: ArtifactRecord,
    *,
    receipt_label: str = "publication-receipt-written-once",
    manifest_ref: ObjectRef | None = None,
) -> PublicationRecord:
    values = {
        "manifest_ref": manifest_ref or _record_ref(manifest),
        "authorization_ref": _ref("authorization"),
        "authorization_validation_ref": _ref("authorization-validation"),
        "authorization_use_ref": _ref("authorization-use"),
        "ordered_published_artifact_refs": (_record_ref(artifact),),
        "ordered_published_artifact_byte_hashes": (artifact.artifact_byte_hash,),
        "publisher_identity_ref": _ref("publisher"),
        "destination_content_addresses": (str(artifact.artifact_byte_hash),),
        "publication_time_evidence_ref": Applicability.NOT_APPLICABLE,
        "publication_receipt_ref": (
            _ref(receipt_label)
            if receipt_label == "unrelated"
            else _receipt_ref(
                str(artifact.artifact_byte_hash),
                (
                    "ALREADY_IDENTICAL"
                    if receipt_label.endswith("already-identical")
                    else "WRITTEN_ONCE"
                ),
            )
        ),
        "completeness": _resolution(ResolutionState.PRESENT),
    }
    return _seal(PublicationRecord, "publication-record", values)  # type: ignore[return-value]


def _correction_candidate(
    original: ArtifactRecord,
    replacement: ArtifactRecord,
    *,
    replacement_ref: ObjectRef | None = None,
    repeated: bool = False,
) -> CorrectionRecord:
    values = {
        "original_artifact_or_manifest_ref": _record_ref(original),
        "replacement_artifact_or_manifest_ref": replacement_ref
        or _record_ref(replacement),
        "correction_scope_ref": _ref("correction-scope"),
        "reason_ref": _ref("correction-reason"),
        "method_ref": _ref("correction-method"),
        "authorization_ref": _ref("authorization"),
        "authorization_validation_ref": _ref("authorization-validation"),
        "authorization_use_ref": _ref("authorization-use"),
        "scientific_execution_repeated": repeated,
        "prior_publication_refs": (_ref("prior-publication"),),
        "new_manifest_ref_or_not_applicable": _ref("new-manifest"),
        "evidence_ledger_relation_ref": _ref("evidence-ledger-relation"),
        "completeness": _resolution(ResolutionState.PRESENT),
    }
    return _seal(CorrectionRecord, "correction-record", values)  # type: ignore[return-value]


def _formation_case(number: int) -> tuple[type, dict[str, object]]:
    artifact = _artifact("RESULT_A")
    source, runtime, environment, semantics = _provenance()
    manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
    trace = _trace_validation("VALID_PREFIX")
    run = _run_envelope("VALID_PREFIX")
    pairs: tuple[tuple[type, dict[str, object]], ...] = (
        (
            RuntimeMetadata,
            {
                "execution_identity": _execution_identity(),
                "run_identity_ref": _ref("form-runtime-run"),
                "authorization_use_ref": _ref("form-runtime-authorization"),
                "wall_clock_evidence_ref": Applicability.NOT_APPLICABLE,
                "host_process_evidence_refs": (_ref("form-runtime-host"),),
                "storage_evidence_refs": (_ref("form-runtime-storage"),),
                "diagnostic_evidence_refs": (_ref("form-runtime-diagnostic"),),
                "completeness": _resolution(ResolutionState.PRESENT),
            },
        ),
        (
            ResultArtifact,
            {
                "artifact_record": artifact,
                "scientific_payload_ref": _ref("scientific-payload"),
                "trace_payload_or_prefix_ref": _ref("trace-payload"),
                "run_envelope_ref": _ref("run-envelope"),
                "runtime_metadata_ref": _ref("runtime-metadata"),
                "derivation_refs": (_ref("derivation"),),
                "scientific_completeness": _resolution(ResolutionState.PRESENT),
            },
        ),
        (
            SummaryArtifact,
            {
                "artifact_record": artifact,
                "ordered_source_result_refs": (_ref("source-result"),),
                "analysis_code_refs": (_ref("analysis-code"),),
                "derivation_refs": (_ref("derivation"),),
                "completeness": _resolution(ResolutionState.PRESENT),
            },
        ),
        (
            FigureArtifact,
            {
                "artifact_record": artifact,
                "ordered_source_result_or_summary_refs": (_ref("source-result"),),
                "figure_code_refs": (_ref("figure-code"),),
                "evidence_label": "SCHEMATIC",
                "completeness": _resolution(ResolutionState.PRESENT),
            },
        ),
        (
            PublicationRecord,
            {
                field.name: getattr(_publication_candidate(manifest, artifact), field.name)
                for field in fields(PublicationRecord)
            },
        ),
        (
            CorrectionRecord,
            {
                field.name: getattr(_correction_candidate(artifact, _artifact("RESULT_B")), field.name)
                for field in fields(CorrectionRecord)
            },
        ),
        (
            SourceProvenance,
            {
                field.name: getattr(source, field.name)
                for field in fields(SourceProvenance)
            },
        ),
        (
            RuntimeProvenance,
            {
                field.name: getattr(runtime, field.name)
                for field in fields(RuntimeProvenance)
            },
        ),
        (
            EnvironmentProvenance,
            {
                field.name: getattr(environment, field.name)
                for field in fields(EnvironmentProvenance)
            },
        ),
        (
            ExecutionSemanticsProjection,
            {
                field.name: getattr(semantics, field.name)
                for field in fields(ExecutionSemanticsProjection)
            },
        ),
        (
            RecoveryRecord,
            {
                "classification": RecoveryClassification.RECOVERED_IDENTICAL,
                "manifest_ref": _record_ref(manifest),
                "artifact_ref": _record_ref(artifact),
                "artifact_byte_hash": artifact.artifact_byte_hash,
                "trace_prefix_hash": trace.confirmed_prefix.prefix_digest,
                "run_envelope_digest": run.envelope_digest,
                "execution_identity": manifest.execution_identity,
                "authorization_validation_ref": _ref("authorization-validation"),
                "authorization_use_ref": _ref("authorization-use"),
                "destination_content_address": str(artifact.artifact_byte_hash),
                "destination_prior_hash_or_not_applicable": Applicability.NOT_APPLICABLE,
                "recovered_artifact_ref": _record_ref(artifact),
                "completeness": _resolution(ResolutionState.PRESENT),
            },
        ),
        (
            PublicationReceipt,
            {
                "receipt_ref": _ref("form-publication-receipt"),
                "content_address": str(artifact.artifact_byte_hash),
                "artifact_byte_hash": artifact.artifact_byte_hash,
                "prior_state": "ABSENT",
                "write_outcome": "WRITTEN_ONCE",
                "stored_byte_count": len(_fixture("RESULT_A")[0]),
            },
        ),
    )
    return pairs[(number - 32) // 2]


def _trace_artifact_with_id(artifact: ArtifactRecord, object_id: ScientificId) -> ArtifactRecord:
    payload = artifact.to_ecj1()
    old = artifact.envelope
    content_hash = compute_object_content_hash(
        object_id=object_id,
        object_kind=str(old.object_kind_id),
        schema_id=old.schema_id,
        schema_version=old.schema_version,
        object_version=old.object_version,
        authority_refs=old.authority_refs,
        supersedes_ref=None,
        object_content_payload=payload,
    )
    envelope = replace(old, object_id=object_id, object_content_hash=content_hash)
    return replace(artifact, envelope=envelope)


def _run_semantic_constructor(number: int) -> object:
    source, runtime, _, semantics = _provenance()
    if number == 56:
        return RuntimeProvenance(
            **{
                field.name: (
                    getattr(runtime, field.name) + ("UNDECLARED_OUTSIDE_SECTION7",)
                    if field.name == "included_property_classes"
                    else getattr(runtime, field.name)
                )
                for field in fields(runtime)
            }
        )
    if number == 57:
        return SourceProvenance(
            **{
                field.name: (
                    () if field.name == "ordered_source_raw_sha256" else getattr(source, field.name)
                )
                for field in fields(source)
            }
        )
    if number == 58:
        return ExecutionSemanticsProjection(
            **{
                field.name: (
                    getattr(semantics, field.name) + ("HOST_IDENTITY",)
                    if field.name == "included_property_classes"
                    else getattr(semantics, field.name)
                )
                for field in fields(semantics)
            }
        )
    return ExecutionSemanticsProjection(
        **{
            field.name: (
                ExecutionSemanticsHash("sha256:" + "f" * 64)
                if field.name == "execution_semantics_hash"
                else getattr(semantics, field.name)
            )
            for field in fields(semantics)
        }
    )


def _run_trace_vector(number: int) -> ArtifactRecord:
    state = "VALID_PREFIX" if number == 64 else "VALID_COMPLETE"
    validation = _trace_validation(state)
    run = _run_envelope(state)
    artifact = _artifact("TRACE_PREFIX")
    payload = _fixture("TRACE_PREFIX")[0]
    if number == 66:
        artifact = _trace_artifact_with_id(
            artifact, ScientificId("ebu:object:production:not-validation")
        )
    if number == 67:
        artifact = _artifact("TRACE_PREFIX", present=False)
    if number in {68, 71}:
        artifact = _artifact("TRACE_PREFIX", hash_name="RESULT_B")
    if number in {69, 71}:
        validation = _trace_validation("AMBIGUOUS")
    if number == 70:
        run = _run_envelope("VALID_COMPLETE", binding_ref=_ref("binding-other"))
    return finalize_inert_trace_payload(validation, run, artifact, payload)


def _run_manifest_vector(number: int) -> ExecutionResultManifest:
    state = "PARTIAL" if number in {73, 80, 84} else "UNRESOLVED" if number == 74 else "PRESENT_AS_COMPLETE"
    artifact = _artifact("RESULT_A")
    payload = _fixture("RESULT_A")[0]
    manifest = _manifest(state, artifact)
    expected_ref = _record_ref(manifest)
    artifacts: tuple[ArtifactRecord, ...] = (artifact,)
    payloads: tuple[bytes, ...] = (payload,)
    validation = _trace_validation("VALID_COMPLETE")
    run = _run_envelope("VALID_COMPLETE")
    if number in {75, 82}:
        artifacts, payloads = (), ()
    if number in {76, 83}:
        artifact = _artifact("RESULT_A", hash_name="RESULT_B")
        manifest = _manifest(state, artifact)
        expected_ref = _record_ref(manifest)
        artifacts = (artifact,)
    if number in {77, 83}:
        validation = _trace_validation("AMBIGUOUS")
    if number == 78:
        run = _run_envelope("VALID_COMPLETE", binding_ref=_ref("binding-other"))
    if number == 80:
        manifest = _reseal(
            manifest,
            "manifest-invalid-completeness",
            completeness=_resolution(ResolutionState.PRESENT),
        )  # type: ignore[assignment]
        expected_ref = _record_ref(manifest)
    if number == 81:
        expected_ref = _ref("manifest-other")
    source, runtime, environment, semantics = _provenance()
    targets = _ordered(manifest.execution_identity.identity_ref, _record_ref(manifest))
    validation_auth, use_auth = _authorization(
        AuthorizedOperation.FINALIZE_EXECUTION_RESULT_MANIFEST,
        targets,
        manifest,
        use_operation=(
            AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
            if number in {79, 84}
            else None
        ),
    )
    return finalize_inert_manifest(
        expected_ref,
        manifest,
        artifacts,
        payloads,
        source,
        runtime,
        environment,
        semantics,
        validation,
        run,
        validation_auth,
        use_auth,
    )


def _run_recovery_vector(number: int) -> RecoveryRecord:
    artifact = _artifact("RESULT_A")
    manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
    payload = _fixture("RESULT_A")[0]
    destination: bytes | Applicability = (
        payload if number == 86 else Applicability.NOT_APPLICABLE
    )
    trace_state = "VALID_PREFIX" if number == 87 else "VALID_COMPLETE"
    validation = _trace_validation(trace_state)
    run = _run_envelope(trace_state)
    if number in {88, 95}:
        manifest = _manifest("UNRESOLVED", artifact)
    if number in {89, 96}:
        artifact = _artifact("RESULT_A", hash_name="RESULT_B")
        manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
    if number in {90, 97}:
        validation = _trace_validation("AMBIGUOUS")
    if number == 91:
        run = _run_envelope("VALID_COMPLETE", binding_ref=_ref("binding-other"))
    if number in {94, 98}:
        destination = _fixture("RESULT_B")[0]
    targets = _ordered(_record_ref(manifest), _record_ref(artifact))
    validation_auth, use_auth = _authorization(
        AuthorizedOperation.RECOVER_EXECUTION_ARTIFACTS,
        targets,
        manifest,
        use_operation=(
            AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
            if number in {92, 98}
            else None
        ),
    )
    if number == 93:
        other_targets = (_ref("target-other"),)
        validation_auth, use_auth = _authorization(
            AuthorizedOperation.RECOVER_EXECUTION_ARTIFACTS,
            other_targets,
            manifest,
        )
    return recover_inert_artifacts(
        manifest,
        artifact,
        payload,
        destination,
        validation,
        run,
        validation_auth,
        use_auth,
    )


class _StructuralStore:
    def observe(self, content_address: str, /) -> Applicability:
        return Applicability.NOT_APPLICABLE

    def put_if_absent_or_identical(
        self, content_address: str, artifact_bytes: bytes, /
    ) -> PublicationReceipt:
        raise AssertionError("structural substitute must never be called")


def _run_publication_vector(number: int) -> PublicationRecord:
    artifact = _artifact("RESULT_A")
    manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
    payload = _fixture("RESULT_A")[0]
    snapshot = "SAME" if number == 100 else "DIFFERENT" if number in {106, 114} else "ABSENT"
    entries = (
        ((str(artifact.artifact_byte_hash), payload),)
        if snapshot == "SAME"
        else (
            ((str(artifact.artifact_byte_hash), _fixture("RESULT_B")[0]),)
            if snapshot == "DIFFERENT"
            else ()
        )
    )
    store: object = _make_inert_write_once_store(entries)
    receipt_label = (
        "publication-receipt-already-identical"
        if snapshot == "SAME"
        else "publication-receipt-written-once"
    )
    candidate = _publication_candidate(
        manifest, artifact, receipt_label=receipt_label
    )
    artifacts: tuple[ArtifactRecord, ...] = (artifact,)
    payloads: tuple[bytes, ...] = (payload,)
    if number in {101, 111}:
        artifacts, payloads = (), ()
    if number in {102, 112}:
        artifact = _artifact("RESULT_A", hash_name="RESULT_B")
        manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
        candidate = _publication_candidate(manifest, artifact)
        artifacts = (artifact,)
    if number == 103:
        manifest = _manifest("PARTIAL", artifact)
        candidate = _publication_candidate(manifest, artifact)
    if number == 107:
        store = _StructuralStore()
    if number in {108, 114}:
        candidate = _publication_candidate(
            manifest, artifact, receipt_label="unrelated"
        )
    if number in {109, 110}:
        candidate = _publication_candidate(
            manifest, artifact, manifest_ref=_ref("manifest-other")
        )
    targets = _ordered(_record_ref(manifest), *tuple(_record_ref(item) for item in artifacts))
    validation_auth, use_auth = _authorization(
        AuthorizedOperation.PUBLISH_ARTIFACTS,
        targets,
        manifest,
        use_operation=(
            AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
            if number in {104, 113}
            else None
        ),
    )
    if number == 105:
        validation_auth, use_auth = _authorization(
            AuthorizedOperation.PUBLISH_ARTIFACTS,
            (_ref("target-other"),),
            manifest,
        )
    return publish_inert_artifacts(
        store,
        candidate,
        manifest,
        artifacts,
        payloads,
        validation_auth,
        use_auth,
    )


def _run_correction_vector(number: int) -> CorrectionRecord:
    original = _artifact("RESULT_A")
    replacement_artifact = _artifact("RESULT_B")
    original_bytes = _fixture("RESULT_A")[0]
    replacement_bytes = _fixture("RESULT_B")[0]
    if number == 116:
        original = _artifact("RESULT_A", present=False)
    if number == 117:
        original = _artifact("RESULT_A", hash_name="RESULT_B")
    if number == 118:
        replacement_artifact = _artifact("RESULT_B", hash_name="RESULT_A")
    if number == 120:
        replacement_artifact = original
        replacement_bytes = original_bytes
    if number in {121, 124, 125}:
        replacement_artifact = _artifact("RESULT_B", hash_name="RESULT_A")
        replacement_bytes = original_bytes
    candidate = _correction_candidate(original, replacement_artifact)
    if number in {122, 125}:
        candidate = _correction_candidate(
            original,
            replacement_artifact,
            replacement_ref=_ref("unrelated"),
        )
    if number == 123:
        candidate = _correction_candidate(
            original, replacement_artifact, repeated=True
        )
    targets = _ordered(_record_ref(original), _record_ref(candidate))
    validation_auth, use_auth = _authorization(
        AuthorizedOperation.CREATE_CORRECTION_RECORD,
        targets,
        identity=original.producing_execution_identity,
        use_operation=(
            AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
            if number in {119, 124}
            else None
        ),
    )
    return create_inert_correction_record(
        candidate,
        original,
        replacement_artifact,
        original_bytes,
        replacement_bytes,
        validation_auth,
        use_auth,
    )


def _guard_values() -> tuple[
    ExecutionResultManifest,
    tuple[ArtifactRecord, ...],
    AuthorizationValidationRecord,
    AuthorizationUseRecord,
]:
    artifact = _artifact("RESULT_A")
    manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
    targets = _ordered(_record_ref(manifest), _record_ref(artifact))
    validation, use = _authorization(
        AuthorizedOperation.PUBLISH_ARTIFACTS, targets, manifest
    )
    return manifest, (artifact,), validation, use


def _run_guard(number: int) -> None:
    manifest, artifacts, validation, use = _guard_values()
    if number == 126:
        finalize_trace_payload(
            trace_validation=_trace_validation("VALID_COMPLETE"),
            run_envelope=_run_envelope("VALID_COMPLETE"),
            trace_artifact=_artifact("TRACE_PREFIX"),
            authorization_validation=validation,
            authorization_use=use,
        )
    if number == 127:
        finalize_execution_result_manifest(
            manifest=manifest,
            artifacts=artifacts,
            authorization_validation=validation,
            authorization_use=use,
        )
    if number == 128:
        recover_artifacts(
            manifest=manifest,
            artifacts=artifacts,
            authorization_validation=validation,
            authorization_use=use,
        )
    if number == 129:
        publish_artifacts(
            manifest=manifest,
            artifacts=artifacts,
            authorization_validation=validation,
            authorization_use=use,
        )
    original = artifacts[0]
    replacement_artifact = _artifact("RESULT_B")
    create_correction_record(
        candidate=_correction_candidate(original, replacement_artifact),
        original=original,
        replacement=replacement_artifact,
        authorization_validation=validation,
        authorization_use=use,
    )


def _execute_dynamic(vector: dict[str, Any]) -> object:
    number = int(vector["vector_id"].removeprefix("I8V-"))
    if number <= 28:
        property_class = (
            MECHANICAL["closed_domains"]["section7_execution_semantics_classes"]
            + MECHANICAL["closed_domains"]["section7_run_metadata_classes"]
        )[number - 1]
        return classify_execution_runtime_property(property_class)
    if number == 29:
        return classify_execution_runtime_property("UNDECLARED_OUTSIDE_SECTION7")
    if number in {30, 31}:
        return classify_execution_runtime_property(7)  # type: ignore[arg-type]
    if 32 <= number <= 55:
        runtime, kwargs = _formation_case(number)
        if number % 2:
            kwargs.pop(tuple(runtime.__dataclass_fields__)[-1])
        return runtime(**kwargs)
    if 56 <= number <= 59:
        return _run_semantic_constructor(number)
    if 60 <= number <= 63:
        state = {
            60: "PRESENT_AS_COMPLETE",
            61: "PARTIAL",
            62: "UNRESOLVED",
            63: "NOT_APPLICABLE",
        }[number]
        return _manifest(state)
    if 64 <= number <= 71:
        return _run_trace_vector(number)
    if 72 <= number <= 84:
        return _run_manifest_vector(number)
    if 85 <= number <= 98:
        return _run_recovery_vector(number)
    if 99 <= number <= 114:
        return _run_publication_vector(number)
    if 115 <= number <= 125:
        return _run_correction_vector(number)
    return _run_guard(number)


def _assert_success_projection(vector: dict[str, Any], result: object) -> None:
    number = int(vector["vector_id"].removeprefix("I8V-"))
    expected = vector["expected"]["result_projection"]
    if number <= 28:
        assert result == expected["disposition"]
    elif 32 <= number <= 55:
        assert type(result).__name__ == expected["runtime_type"]
    elif 60 <= number <= 63:
        assert type(result) is ExecutionResultManifest
        assert result.completeness.state.value == {
            "PRESENT_AS_COMPLETE": "PRESENT",
            "PARTIAL": "PARTIAL",
            "UNRESOLVED": "UNRESOLVED",
            "NOT_APPLICABLE": "NOT_APPLICABLE",
        }[expected["manifest_state"]]
    elif number in {64, 65}:
        assert type(result) is ArtifactRecord
    elif number in {72, 73, 74}:
        assert type(result) is ExecutionResultManifest
    elif number in {85, 86, 87}:
        assert type(result) is RecoveryRecord
        assert result.classification.value == expected["classification"]
        assert result.authorization_validation_ref == _ref(
            "authorization-validation"
        )
        assert result.authorization_use_ref == _ref("authorization-use")
    elif number in {99, 100}:
        assert type(result) is PublicationRecord
    elif number == 115:
        assert type(result) is CorrectionRecord


def _run_dynamic_vector(vector: dict[str, Any]) -> None:
    expected = vector["expected"]
    if expected["outcome"] == "FAILURE":
        try:
            _execute_dynamic(vector)
        except FrameworkError as error:
            envelope = error.envelope
            assert envelope.failure_code.value == expected["failure_code"]
            assert envelope.failure_ordinal == expected["failure_ordinal"]
            assert str(envelope.failure_id) == expected["failure_id"]
            assert envelope.stage.value == "I-8"
            assert envelope.object_refs == ()
            assert envelope.event_key is Applicability.NOT_APPLICABLE
        else:
            raise AssertionError("expected exact I-8 failure")
    else:
        result = _execute_dynamic(vector)
        _assert_success_projection(vector, result)


def _relative_import_graph() -> dict[str, list[str]]:
    package = ROOT / "src/ebu_framework"
    order = tuple(PATHS["future_import_graph"]["package_module_order"])
    known = set(order)
    graph: dict[str, list[str]] = {}
    for name in order:
        tree = ast.parse((package / f"{name}.py").read_text(encoding="utf-8"))
        imports: list[str] = []
        for node in tree.body:
            if not isinstance(node, ast.ImportFrom) or node.level != 1:
                continue
            names = (
                (node.module.split(".", 1)[0],)
                if node.module is not None
                else tuple(alias.name.split(".", 1)[0] for alias in node.names)
            )
            for imported in names:
                if imported in known and imported not in imports:
                    imports.append(imported)
        graph[name] = imports
    return graph


def _run_static_vector(vector: dict[str, Any]) -> None:
    witness = vector["construction"]["static_witness"]
    kind = witness["kind"]
    package = ROOT / "src/ebu_framework"
    authorized = {row["path"] for row in PATHS["exact_construction_patches"]}
    if kind == "AST_IMPORT_GRAPH":
        graph = _relative_import_graph()
        assert graph == PATHS["future_import_graph"]["direct_imports"]
        assert len(graph) == 39
        assert sum(map(len, graph.values())) == 243
        remaining = set(graph)
        while remaining:
            ready = {
                name
                for name in remaining
                if not set(graph[name]).intersection(remaining)
            }
            assert ready
            remaining -= ready
    elif kind == "AST_FORBIDDEN_REACHABILITY":
        for filename in witness["sources"]:
            tree = ast.parse((package / filename).read_text(encoding="utf-8"))
            imported = {
                node.module.split(".")[-1]
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom) and node.module
            }
            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            assert not {"execution", "runner", "model", "trajectory", "simulation"} & imported
            assert not {"run", "simulate", "model_step", "execute_gate"} & calls
    elif kind == "AST_EXTERNAL_EFFECT":
        for filename in witness["sources"]:
            tree = ast.parse((package / filename).read_text(encoding="utf-8"))
            roots = {
                alias.name.split(".")[0]
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            }
            calls = {
                node.func.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            }
            assert not {"socket", "urllib", "requests", "subprocess", "sqlite3"} & roots
            assert "open" not in calls
    elif kind == "SOURCE_FIELD_AUDIT" and "type" in witness:
        names = {field.name for field in fields(ExecutionResultManifest)}
        assert not any(
            any(token in name for token in witness["forbidden_fields"])
            for name in names
        )
    elif kind == "SOURCE_FIELD_AUDIT":
        assert "manifest_ref" in PublicationRecord.__dataclass_fields__
        assert "original_artifact_or_manifest_ref" in CorrectionRecord.__dataclass_fields__
        assert PublicationRecord.__dataclass_params__.frozen
        assert CorrectionRecord.__dataclass_params__.frozen
    elif kind == "SOURCE_LITERAL_AUDIT":
        source = (package / witness["source"]).read_text(encoding="utf-8")
        assert all(json.dumps(item) in source for item in witness["included"])
        assert all(json.dumps(item) in source for item in witness["run_metadata"])
    elif kind == "HASH_PROOF":
        for name, row in witness["fixtures"].items():
            payload = bytes.fromhex(row["hex"])
            assert len(payload) == row["byte_count"], name
            assert hashlib.sha256(payload).hexdigest() == row["raw_sha256"]
            assert str(compute_artifact_byte_hash(payload)) == row["artifact_byte_hash"]
    elif kind == "TYPE_SEPARATION":
        runtime = [
            framework.CanonicalScientificTracePayloadHash,
            framework.CanonicalTracePrefixHash,
            framework.RunEnvelopeDigest,
            framework.ArtifactByteHash,
        ]
        assert len(set(runtime)) == 4
        assert all(left is not right for i, left in enumerate(runtime) for right in runtime[i + 1 :])
    elif kind == "AUTHORIZATION_TARGET_AUDIT":
        i4 = json.loads(
            (ROOT / "unified_python_research_framework_i4_contract.json").read_bytes()
        )
        contract = i4["operation_target_contract"]
        assert all(operation in contract for operation in witness["operations"])
    elif kind == "T3_GUARD_AUDIT":
        owners = {
            "finalize_trace_payload": finalize_trace_payload,
            "finalize_execution_result_manifest": finalize_execution_result_manifest,
            "recover_artifacts": recover_artifacts,
            "publish_artifacts": publish_artifacts,
            "create_correction_record": create_correction_record,
        }
        assert all(
            inspect.signature(owners[name]).return_annotation in {"NoReturn", framework.NoReturn}
            if hasattr(framework, "NoReturn")
            else inspect.signature(owners[name]).return_annotation == "NoReturn"
            for name in witness["callables"]
        )
    elif kind == "PREDECESSOR_PRESERVATION":
        import subprocess

        stage_c = json.loads(
            (
                ROOT / "framework_alpha_packaging_release_candidate_contract.json"
            ).read_bytes()
        )
        stage_c_predecessor = json.loads(
            (
                ROOT
                / "framework_alpha_packaging_release_candidate_predecessor_manifest.json"
            ).read_bytes()
        )
        reconciliation = stage_c["test_inventory_reconciliation"][
            "artifact_predecessor_preservation_reconciliation"
        ]
        exact_paths = (
            ".github/workflows/tests.yml",
            "EBU_FUTURE_BOOKS_STRUCTURE.md",
            "build_backend/ebu_build_backend.py",
            "tests/framework/safety.py",
        )
        stage_c_modified = (
            ".github/workflows/tests.yml",
            "build_backend/ebu_build_backend.py",
        )
        current_byte_preserved = (
            "EBU_FUTURE_BOOKS_STRUCTURE.md",
            "tests/framework/safety.py",
        )
        assert tuple(reconciliation["exact_reconciled_paths"]) == exact_paths
        assert tuple(reconciliation["stage_c_modified_paths"]) == stage_c_modified
        assert tuple(reconciliation["current_byte_preserved_paths"]) == current_byte_preserved
        reconciliation_rows = {
            row["path"]: row for row in reconciliation["rows"]
        }
        assert tuple(reconciliation_rows) == exact_paths
        stage_c_rows = {
            row["path"]: row for row in stage_c_predecessor["controlling_paths"]
        }
        for row in PREDECESSOR["rows"]:
            if row["i8_future_disposition"] != "PRESERVED":
                continue
            path = row["path"]
            if path in reconciliation_rows:
                frozen = reconciliation_rows[path]
                assert (
                    row["mode"],
                    row["git_object"],
                    row["byte_count"],
                    row["raw_sha256"],
                ) == (
                    frozen["i8_mode"],
                    frozen["i8_git_object"],
                    frozen["i8_byte_count"],
                    frozen["i8_raw_sha256"],
                )
                i8_payload = subprocess.run(
                    ["git", "cat-file", "blob", row["git_object"]],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                ).stdout
                assert (len(i8_payload), hashlib.sha256(i8_payload).hexdigest()) == (
                    row["byte_count"],
                    row["raw_sha256"],
                )
                accepted_base = (
                    frozen["accepted_stage_c_base_mode"],
                    frozen["accepted_stage_c_base_git_object"],
                    frozen["accepted_stage_c_base_byte_count"],
                    frozen["accepted_stage_c_base_raw_sha256"],
                )
                if path in stage_c_modified:
                    stage_row = stage_c_rows[path]
                    assert (
                        stage_row["mode"],
                        stage_row["git_object"],
                        stage_row["byte_count"],
                        stage_row["raw_sha256"],
                    ) == accepted_base
                    base_payload = subprocess.run(
                        ["git", "cat-file", "blob", stage_row["git_object"]],
                        cwd=ROOT,
                        check=True,
                        capture_output=True,
                    ).stdout
                    assert (
                        len(base_payload),
                        hashlib.sha256(base_payload).hexdigest(),
                    ) == (stage_row["byte_count"], stage_row["raw_sha256"])
                else:
                    head_row = subprocess.run(
                        ["git", "ls-tree", "HEAD", "--", path],
                        cwd=ROOT,
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout.split()
                    payload = (ROOT / path).read_bytes()
                    assert (
                        head_row[0],
                        head_row[2],
                        len(payload),
                        hashlib.sha256(payload).hexdigest(),
                    ) == accepted_base
                continue
            payload = (ROOT / path).read_bytes()
            assert len(payload) == row["byte_count"]
            assert hashlib.sha256(payload).hexdigest() == row["raw_sha256"]
    elif kind == "PATH_SCOPE":
        operations = [row["operation"] for row in PATHS["exact_construction_patches"]]
        assert len(authorized) == witness["path_count"]
        assert operations.count("NEW") == witness["new"]
        assert operations.count("MODIFIED") == witness["modified"]
        assert operations.count("COMPATIBILITY_ONLY_MODIFIED") == witness["compatibility_only"]
    elif kind == "NO_DEPENDENCY_DRIFT":
        predecessor_rows = {row["path"]: row for row in PREDECESSOR["rows"]}
        for path in witness["files"]:
            payload = (ROOT / path).read_bytes()
            assert hashlib.sha256(payload).hexdigest() == predecessor_rows[path]["raw_sha256"]
    elif kind in {"NO_I9_CI", "NO_MANUSCRIPT_OUTPUT"}:
        assert not any(
            path.startswith(("books/", "results/", "figures/", ".github/"))
            or path.endswith((".tex", ".pdf"))
            or path in witness.get("forbidden", ())
            for path in authorized
        )
    elif kind == "OPEN_PROBLEM_AUDIT":
        amendment = (ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I8_AUTHORITY_AMENDMENT.md").read_text()
        status_evidence = {
            "DC25": ("DC25 remains exact", "separate"),
            "UQ-26": ("UQ-26 still blocks", "real recovery"),
            "UQ-27": ("UQ-27 still blocks", "real publication store"),
            "UQ-28": ("UQ-28 still blocks", "correction authority"),
            "UQ-36": ("UQ-36 is enforced only", "section-7 closed-world assumptions"),
        }
        assert set(witness["statuses"]) == set(status_evidence)
        assert all(
            all(fragment in amendment for fragment in status_evidence[key])
            for key in witness["statuses"]
        )
    elif kind == "MANIFEST_IMMUTABILITY_PROOF":
        artifact = _artifact("RESULT_A")
        manifest = _manifest("PRESENT_AS_COMPLETE", artifact)
        candidate = _publication_candidate(manifest, artifact)
        assert candidate.manifest_ref == _record_ref(manifest)
        assert ExecutionResultManifest.__dataclass_params__.frozen
    elif kind == "RECOVERY_NO_EXECUTION":
        source = (package / witness["source"]).read_text(encoding="utf-8")
        tree = ast.parse(source)
        assert "execution" not in _relative_import_graph()["recovery"]
        assert not {
            "run",
            "execute",
            "advance_epoch",
            "model_step",
        } & {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
    elif kind == "WRITE_ONCE_PROOF":
        tree = ast.parse((package / "publication.py").read_text(encoding="utf-8"))
        method = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == "put_if_absent_or_identical"
            and len(node.body) > 1
        )
        text = ast.unparse(method)
        assert "WRITTEN_ONCE" in text
        assert "ALREADY_IDENTICAL" in text
        assert "ALREADY_EXISTS_DIFFERENT" in text
    elif kind == "CORRECTION_NONDESTRUCTIVE_PROOF":
        tree = ast.parse((package / "publication.py").read_text(encoding="utf-8"))
        owner = next(
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "create_inert_correction_record"
        )
        text = ast.unparse(owner)
        assert "original_ref == replacement_ref" in text
        assert "original_bytes == replacement_bytes" in text
        assert "return candidate" in text
    else:
        raise AssertionError(f"unknown static witness {kind}")


class FrameworkI8ExactVectors(unittest.TestCase):
    """One exact owning-path invocation or static witness per frozen vector."""


def _install_vector_test(vector: dict[str, Any]) -> None:
    def test(self: FrameworkI8ExactVectors) -> None:
        if vector["vector_id"].startswith("I8V-"):
            _run_dynamic_vector(vector)
            self.assertEqual(vector["owner_call_count"], 1)
        else:
            _run_static_vector(vector)
            self.assertEqual(vector["owner_call_count"], 0)
        self.assertEqual(vector["runner_calls"], 0)
        self.assertEqual(vector["model_calls"], 0)
        self.assertEqual(vector["policy_calls"], 0)
        self.assertEqual(vector["network_calls"], 0)
        self.assertEqual(vector["filesystem_publication_writes"], 0)
        self.assertEqual(vector["state_advances"], 0)
        self.assertFalse(vector["representative_interface_substitution"])

    test.__name__ = f"test_{vector['vector_id'].replace('-', '_')}"
    setattr(FrameworkI8ExactVectors, test.__name__, test)


for _vector in VECTORS:
    _install_vector_test(_vector)


class FrameworkI8AggregateContract(unittest.TestCase):
    def test_exact_vector_and_failure_coordinate_totals(self) -> None:
        inventory = CONTRACT["inventory"]
        outcomes = [vector["expected"]["outcome"] for vector in VECTORS]
        self.assertEqual(len(VECTORS), inventory["vector_count"])
        self.assertEqual(sum(value == "SUCCESS" for value in outcomes), 55)
        self.assertEqual(sum(value == "FAILURE" for value in outcomes), 75)
        self.assertEqual(sum(value == "STATIC_PASS" for value in outcomes), 20)
        self.assertEqual(sum(vector["owner_call_count"] for vector in VECTORS), 130)
        self.assertEqual(
            sum(vector["precedence"]["completed_check_count"] for vector in VECTORS),
            446,
        )
        self.assertEqual(
            sum(len(vector["precedence"]["active_predicates"]) for vector in VECTORS),
            90,
        )
        self.assertEqual(sum(vector["inert_store_method_calls"] for vector in VECTORS), 3)
        failures = [
            vector["expected"]["failure_id"]
            for vector in VECTORS
            if vector["expected"]["outcome"] == "FAILURE"
        ]
        self.assertEqual(len(failures), 75)
        self.assertEqual(len(set(failures)), 54)
        self.assertEqual(len(failures) - len(set(failures)), 21)
        coordinates = {
            (
                row["failure_code"],
                row["stage"],
                row["interface"]["module"],
                row["interface"]["qualname"],
                row["failure_ordinal"],
            ): row["failure_id"]
            for row in CONTRACT["failure_identity_contract"]["coordinate_catalogue"]
        }
        self.assertEqual(len(coordinates), 54)
        self.assertEqual(len(set(coordinates.values())), 54)

    def test_exact_public_inventory_signatures_and_canonical_authority(self) -> None:
        root_exports = tuple(framework.__all__)
        failure_codes = tuple(code.value for code in FailureCode)
        self.assertEqual(len(root_exports), 471)
        self.assertEqual(len(set(root_exports)), 471)
        self.assertEqual(len(failure_codes), 294)
        self.assertEqual(len(set(failure_codes)), 294)
        self.assertEqual(root_exports[419:444], tuple(MECHANICAL["root_exports"]["append_order"]))
        self.assertEqual(root_exports[444:], tuple(CLCD["root_export_suffix"]))
        self.assertEqual(
            failure_codes[256:280],
            tuple(row["name"] for row in MECHANICAL["failure_inventory"]["append_rows"]),
        )
        self.assertEqual(failure_codes[280:], tuple(CLCD["failure_suffix"]))
        self.assertEqual(len(MECHANICAL["public_types"]), 14)
        self.assertEqual(len(MECHANICAL["public_callables"]), 11)
        self.assertEqual(len(MECHANICAL["private_types"]), 1)
        self.assertEqual(len(MECHANICAL["private_callables"]), 4)
        for row in MECHANICAL["public_types"]:
            runtime = getattr(
                importlib.import_module(f"ebu_framework.{row['module']}"),
                row["name"],
            )
            if row["kind"] == "FROZEN_DATACLASS":
                self.assertTrue(runtime.__dataclass_params__.frozen)
                self.assertEqual(
                    tuple(field.name for field in fields(runtime)),
                    tuple(field[0] for field in row["fields"]),
                )
                self.assertEqual(
                    tuple(inspect.signature(runtime).parameters),
                    tuple(field[0] for field in row["fields"]),
                )
                self.assertTrue(
                    all(
                        parameter.kind is inspect.Parameter.KEYWORD_ONLY
                        and parameter.default is inspect.Parameter.empty
                        for parameter in inspect.signature(runtime).parameters.values()
                    )
                )
            elif row["kind"] == "STRENUM":
                self.assertEqual(tuple(runtime.__members__), tuple(row["values"]))
            else:
                self.assertTrue(runtime._is_protocol)
        normalized = lambda value: "".join(  # noqa: E731
            value.replace("'", "").replace('"', "").split()
        )
        for module_name, name, expected in (
            MECHANICAL["signatures"]["i8_public_rows"]
            + MECHANICAL["signatures"]["i8_private_rows"]
        ):
            runtime = getattr(
                importlib.import_module(f"ebu_framework.{module_name}"), name
            )
            self.assertEqual(
                normalized(str(inspect.signature(runtime))),
                normalized(expected),
            )
        private_class_rows = []
        for module_name in ("provenance", "recovery", "publication"):
            tree = ast.parse(
                (ROOT / f"src/ebu_framework/{module_name}.py").read_text(
                    encoding="utf-8"
                )
            )
            private_class_rows.extend(
                (module_name, node.name)
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name.startswith("_")
            )
        self.assertEqual(
            private_class_rows,
            [("publication", "_InertWriteOnceStore")],
        )
        for path in (CONTRACT_PATH, MECHANICAL_PATH, PATHS_PATH, PREDECESSOR_PATH):
            payload = path.read_bytes()
            self.assertTrue(payload.endswith(b"\n"))
            self.assertNotIn(b"\r", payload)
            parsed = json.loads(payload)
            canonical = (
                json.dumps(
                    parsed,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                    allow_nan=False,
                )
                + "\n"
            ).encode("utf-8")
            self.assertEqual(payload, canonical)


if __name__ == "__main__":
    unittest.main()
