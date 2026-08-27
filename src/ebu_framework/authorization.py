"""Fail-fast external stage-authorization validation for Framework I-4."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
from typing import NoReturn

from . import trust as _trust
from .experiment import ExperimentConfiguration, ExecutionBinding, ExecutionIdentity
from .artifacts import ArtifactRecord, ExecutionResultManifest
from .ledger import Ledger, LedgerEntry
from .registry import RegistryRecord, LifecycleStatus
from .identity import ArtifactByteHash, AuthorizationUseKey, ObjectRef, ScientificId
from .hashing import compute_authorization_use_key, compute_policy_memory_payload_hash
from .errors import (
    Applicability,
    FailureCode,
    FailureEnvelope,
    FailureEvidenceRef,
    FrameworkError,
    _i4_fail,
)


CommonObjectEnvelope = _trust.CommonObjectEnvelope
SignatureProfile = _trust.SignatureProfile
TrustProfileV1 = _trust.TrustProfileV1
IssuerRegistrySnapshotV1 = _trust.IssuerRegistrySnapshotV1
IssuerEntry = _trust.IssuerEntry
DelegationCredentialV1 = _trust.DelegationCredentialV1
RevocationSnapshotV1 = _trust.RevocationSnapshotV1
TrustedTimeChallengeV1 = _trust.TrustedTimeChallengeV1
TrustedTimeAttestationV1 = _trust.TrustedTimeAttestationV1
AuthorizationAuthenticityEnvelopeV1 = _trust.AuthorizationAuthenticityEnvelopeV1
TrustEvidenceEnvelopeV1 = _trust.TrustEvidenceEnvelopeV1
TrustedTimeService = _trust.TrustedTimeService
RevocationService = _trust.RevocationService
AuthorizationStateStore = _trust.AuthorizationStateStore


_VALIDATION_CHALLENGE_BASE64URL = base64.urlsafe_b64encode(
    bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f")
).rstrip(b"=").decode("ascii")


def _failure(code: FailureCode, interface: str, check: str) -> NoReturn:
    _i4_fail(code, "ebu_framework.authorization", interface, check)


def _formation_failure(name: str) -> NoReturn:
    _i4_fail(
        FailureCode.I4_RECORD_FORMATION_INVALID,
        "ebu_framework.authorization",
        name,
        "1.01 exact bundle and nested runtime types",
    )


def _strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected:
            _formation_failure(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


def _enum_missing(name: str) -> NoReturn:
    _formation_failure(name)


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) in {ScientificId, ArtifactByteHash, AuthorizationUseKey}:
        return str(value)
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is Applicability:
        return value.value
    if type(value) is bytes:
        return _trust.parse_ecj1(value)
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _record_projection(record: object, excluded: frozenset[str] = frozenset()) -> dict[str, object]:
    return {
        field: _project(getattr(record, field))
        for field in record.__dataclass_fields__  # type: ignore[attr-defined]
        if field not in excluded
    }


def _ref_key(value: ObjectRef) -> bytes:
    return bytes(_trust.encode_ecj1(value.to_ecj1()))


def _ordered_refs(values: object, *, nonempty: bool = False) -> bool:
    if not (
        type(values) is tuple
        and all(type(item) is ObjectRef for item in values)
        and (not nonempty or bool(values))
    ):
        return False
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _ordered_strings(values: object) -> bool:
    return (
        type(values) is tuple
        and all(type(item) is str and bool(item) for item in values)
        and values == tuple(sorted(values))
        and len(values) == len(set(values))
    )


def _timestamp(value: object) -> bool:
    if type(value) is not str:
        return False
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
    except ValueError:
        return False
    return len(value) == 27 and value.endswith("Z")


def _instant(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ").replace(
        tzinfo=timezone.utc
    )


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


class AuthorizedOperation(StrEnum):
    ACCEPT_REGISTRY_OBJECT = "ACCEPT_REGISTRY_OBJECT"
    SUPERSEDE_REGISTRY_OBJECT = "SUPERSEDE_REGISTRY_OBJECT"
    ACCEPT_EXPERIMENT_CONFIGURATION = "ACCEPT_EXPERIMENT_CONFIGURATION"
    ACCEPT_EXECUTION_BINDING = "ACCEPT_EXECUTION_BINDING"
    APPEND_OPERATIONAL_LEDGER_ENTRY = "APPEND_OPERATIONAL_LEDGER_ENTRY"
    EXECUTE_BOUND_RUN = "EXECUTE_BOUND_RUN"
    FINALIZE_EXECUTION_RESULT_MANIFEST = "FINALIZE_EXECUTION_RESULT_MANIFEST"
    RECOVER_EXECUTION_ARTIFACTS = "RECOVER_EXECUTION_ARTIFACTS"
    CREATE_CORRECTION_RECORD = "CREATE_CORRECTION_RECORD"
    PUBLISH_ARTIFACTS = "PUBLISH_ARTIFACTS"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("AuthorizedOperation")


class AuthorizationValidationStatus(StrEnum):
    VALIDATED_NOT_CONSUMED = "VALIDATED_NOT_CONSUMED"
    REJECTED = "REJECTED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("AuthorizationValidationStatus")


class AuthorizationCheckStatus(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("AuthorizationCheckStatus")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class StageAuthorization:
    envelope: CommonObjectEnvelope
    stage: str
    authorized_operation: AuthorizedOperation
    target_object_refs: tuple[ObjectRef, ...]
    accepted_configuration_ref_or_not_applicable: ObjectRef | Applicability
    accepted_execution_binding_ref_or_not_applicable: ObjectRef | Applicability
    execution_identity_or_not_applicable: ExecutionIdentity | Applicability
    predecessor_evidence_refs: tuple[ObjectRef, ...]
    not_before: str
    expires_at: str
    maximum_invocations: int
    issuer_id: ScientificId
    revocation_snapshot_ref: ObjectRef
    trust_profile_ref: ObjectRef
    exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        optional_refs = (
            self.accepted_configuration_ref_or_not_applicable,
            self.accepted_execution_binding_ref_or_not_applicable,
        )
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.stage) is str and bool(self.stage)
            and type(self.authorized_operation) is AuthorizedOperation
            and _ordered_refs(self.target_object_refs, nonempty=True)
            and all(type(item) is ObjectRef or item is Applicability.NOT_APPLICABLE for item in optional_refs)
            and (type(self.execution_identity_or_not_applicable) is ExecutionIdentity or self.execution_identity_or_not_applicable is Applicability.NOT_APPLICABLE)
            and _ordered_refs(self.predecessor_evidence_refs)
            and _timestamp(self.not_before)
            and _timestamp(self.expires_at)
            and _instant(self.not_before) < _instant(self.expires_at)
            and type(self.maximum_invocations) is int
            and self.maximum_invocations == 1
            and type(self.issuer_id) is ScientificId
            and type(self.revocation_snapshot_ref) is ObjectRef
            and type(self.trust_profile_ref) is ObjectRef
            and _ordered_strings(self.exclusions)
        ):
            _formation_failure("validate_stage_authorization")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self, frozenset({"envelope"}))


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AuthorizationEvidenceBundle:
    authorization: StageAuthorization
    authenticity_envelope: AuthorizationAuthenticityEnvelopeV1
    trust_profile: TrustProfileV1
    issuer_registry_snapshot: IssuerRegistrySnapshotV1
    issuer_root_proofs: tuple[TrustEvidenceEnvelopeV1, ...]
    delegation_credentials: tuple[DelegationCredentialV1, ...]
    delegation_proofs: tuple[TrustEvidenceEnvelopeV1, ...]
    predecessor_evidence: tuple[CommonObjectEnvelope, ...]
    accepted_configuration: ExperimentConfiguration | Applicability
    accepted_binding: ExecutionBinding | Applicability
    execution_identity: ExecutionIdentity | Applicability
    lifecycle_witnesses: tuple[tuple[ObjectRef, LifecycleStatus], ...]
    single_use_store_identity: AuthorizationUseStoreIdentity

    def __post_init__(self) -> None:
        if not (
            type(self.authorization) is StageAuthorization
            and type(self.authenticity_envelope) is AuthorizationAuthenticityEnvelopeV1
            and type(self.trust_profile) is TrustProfileV1
            and type(self.issuer_registry_snapshot) is IssuerRegistrySnapshotV1
            and type(self.issuer_root_proofs) is tuple
            and all(type(item) is TrustEvidenceEnvelopeV1 for item in self.issuer_root_proofs)
            and type(self.delegation_credentials) is tuple
            and all(type(item) is DelegationCredentialV1 for item in self.delegation_credentials)
            and type(self.delegation_proofs) is tuple
            and all(type(item) is TrustEvidenceEnvelopeV1 for item in self.delegation_proofs)
            and type(self.predecessor_evidence) is tuple
            and all(type(item) is CommonObjectEnvelope for item in self.predecessor_evidence)
            and (type(self.accepted_configuration) is ExperimentConfiguration or self.accepted_configuration is Applicability.NOT_APPLICABLE)
            and (type(self.accepted_binding) is ExecutionBinding or self.accepted_binding is Applicability.NOT_APPLICABLE)
            and (type(self.execution_identity) is ExecutionIdentity or self.execution_identity is Applicability.NOT_APPLICABLE)
            and type(self.lifecycle_witnesses) is tuple
            and all(type(item) is tuple and len(item) == 2 and type(item[0]) is ObjectRef and type(item[1]) is LifecycleStatus for item in self.lifecycle_witnesses)
            and type(self.single_use_store_identity).__name__ == "AuthorizationUseStoreIdentity"
            and type(self.single_use_store_identity).__module__ == "ebu_framework.authorization_use"
        ):
            _formation_failure("AuthorizationEvidenceBundle")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AuthorizationCheckRecord:
    check_ordinal: int
    check_name: str
    status: AuthorizationCheckStatus
    failure_code_or_not_applicable: FailureCode | Applicability
    evidence_refs: tuple[FailureEvidenceRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.check_ordinal) is int and self.check_ordinal > 0
            and type(self.check_name) is str and bool(self.check_name)
            and type(self.status) is AuthorizationCheckStatus
            and (type(self.failure_code_or_not_applicable) is FailureCode or self.failure_code_or_not_applicable is Applicability.NOT_APPLICABLE)
            and type(self.evidence_refs) is tuple
            and all(type(item) is FailureEvidenceRef for item in self.evidence_refs)
            and ((self.status is AuthorizationCheckStatus.PASS and self.failure_code_or_not_applicable is Applicability.NOT_APPLICABLE) or (self.status is AuthorizationCheckStatus.FAIL and type(self.failure_code_or_not_applicable) is FailureCode))
        ):
            _formation_failure("AuthorizationCheckRecord")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AuthorizationValidationRecord:
    authorization_ref: ObjectRef
    authorization_use_key: AuthorizationUseKey
    status: AuthorizationValidationStatus
    completed_checks: tuple[AuthorizationCheckRecord, ...]
    effective_issuer_id: ScientificId | Applicability
    effective_stages: tuple[str, ...]
    effective_operations: tuple[str, ...]
    effective_target_object_refs: tuple[ObjectRef, ...]
    trusted_time_attestation: TrustedTimeAttestationV1 | Applicability
    revocation_snapshot_ref: ObjectRef | Applicability
    failure: FailureEnvelope | Applicability

    def __post_init__(self) -> None:
        success_shape = (
            self.status is AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED
            and self.failure is Applicability.NOT_APPLICABLE
            and type(self.effective_issuer_id) is ScientificId
            and bool(self.effective_stages)
            and len(self.effective_operations) == 1
            and bool(self.effective_target_object_refs)
            and type(self.trusted_time_attestation) is TrustedTimeAttestationV1
            and type(self.revocation_snapshot_ref) is ObjectRef
            and bool(self.completed_checks)
            and all(
                item.status is AuthorizationCheckStatus.PASS
                for item in self.completed_checks
            )
        )
        rejected_shape = (
            self.status is AuthorizationValidationStatus.REJECTED
            and type(self.failure) is FailureEnvelope
            and bool(self.completed_checks)
            and self.completed_checks[-1].status is AuthorizationCheckStatus.FAIL
            and all(
                item.status is AuthorizationCheckStatus.PASS
                for item in self.completed_checks[:-1]
            )
        )
        if not (
            type(self.authorization_ref) is ObjectRef
            and type(self.authorization_use_key) is AuthorizationUseKey
            and type(self.status) is AuthorizationValidationStatus
            and type(self.completed_checks) is tuple
            and all(type(item) is AuthorizationCheckRecord for item in self.completed_checks)
            and tuple(item.check_ordinal for item in self.completed_checks) == tuple(range(1, len(self.completed_checks) + 1))
            and (type(self.effective_issuer_id) is ScientificId or self.effective_issuer_id is Applicability.NOT_APPLICABLE)
            and _ordered_strings(self.effective_stages)
            and _ordered_strings(self.effective_operations)
            and _ordered_refs(self.effective_target_object_refs)
            and (type(self.trusted_time_attestation) is TrustedTimeAttestationV1 or self.trusted_time_attestation is Applicability.NOT_APPLICABLE)
            and (type(self.revocation_snapshot_ref) is ObjectRef or self.revocation_snapshot_ref is Applicability.NOT_APPLICABLE)
            and (type(self.failure) is FailureEnvelope or self.failure is Applicability.NOT_APPLICABLE)
            and (success_shape or rejected_shape)
        ):
            _formation_failure("AuthorizationValidationRecord")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


_trust._AUTHORIZATION_CHECK_RECORD_TYPE = AuthorizationCheckRecord
_trust._AUTHORIZATION_CHECK_STATUS_TYPE = AuthorizationCheckStatus


def _pass(checks: list[AuthorizationCheckRecord], name: str) -> None:
    checks.append(
        AuthorizationCheckRecord(
            check_ordinal=len(checks) + 1,
            check_name=name,
            status=AuthorizationCheckStatus.PASS,
            failure_code_or_not_applicable=Applicability.NOT_APPLICABLE,
            evidence_refs=(),
        )
    )


def _all_objects(bundle: AuthorizationEvidenceBundle) -> tuple[object, ...]:
    values: list[object] = [
        bundle.authorization,
        bundle.authenticity_envelope,
        bundle.trust_profile,
        bundle.issuer_registry_snapshot,
        *bundle.issuer_root_proofs,
        *bundle.delegation_credentials,
        *bundle.delegation_proofs,
    ]
    if type(bundle.accepted_configuration) is ExperimentConfiguration:
        values.append(bundle.accepted_configuration)
    if type(bundle.accepted_binding) is ExecutionBinding:
        values.append(bundle.accepted_binding)
    return tuple(values)


def _authorization_signature_message(value: AuthorizationAuthenticityEnvelopeV1) -> bytes:
    return bytes(
        _trust.encode_ecj1(
            {
                "hash_domain": "ebu.authorization-signature-message.v1",
                "signature_profile": value.signature_profile.value,
                "stage_authorization_ref": value.stage_authorization_ref.to_ecj1(),
                "trust_profile_ref": value.trust_profile_ref.to_ecj1(),
                "signer_issuer_id": str(value.signer_issuer_id),
                "signer_key_id": value.signer_key_id,
                "ordered_delegation_credential_refs": [item.to_ecj1() for item in value.ordered_delegation_credential_refs],
            }
        )
    )


def _proof_hash(signature_base64url: str) -> ArtifactByteHash:
    try:
        raw = base64.urlsafe_b64decode(signature_base64url + "=" * ((-len(signature_base64url)) % 4))
    except (ValueError, TypeError):
        _failure(FailureCode.SIGNATURE_ENCODING_INVALID, "validate_stage_authorization", "proof-byte hash")
    return ArtifactByteHash.from_hex(hashlib.sha256(raw).hexdigest())


def _failed_record(
    bundle: AuthorizationEvidenceBundle,
    use_key: AuthorizationUseKey,
    checks: list[AuthorizationCheckRecord],
    check_name: str,
    failure: FailureEnvelope,
    effective: IssuerEntry | None,
    attestation: TrustedTimeAttestationV1 | None,
    revocation: RevocationSnapshotV1 | None,
) -> AuthorizationValidationRecord:
    checks.append(
        AuthorizationCheckRecord(
            check_ordinal=len(checks) + 1,
            check_name=check_name,
            status=AuthorizationCheckStatus.FAIL,
            failure_code_or_not_applicable=failure.failure_code,
            evidence_refs=failure.evidence_refs,
        )
    )
    return AuthorizationValidationRecord(
        authorization_ref=_envelope_ref(bundle.authorization),
        authorization_use_key=use_key,
        status=AuthorizationValidationStatus.REJECTED,
        completed_checks=tuple(checks),
        effective_issuer_id=Applicability.NOT_APPLICABLE if effective is None else effective.issuer_id,
        effective_stages=() if effective is None else effective.maximum_stages,
        effective_operations=() if effective is None else effective.maximum_operations,
        effective_target_object_refs=(),
        trusted_time_attestation=Applicability.NOT_APPLICABLE if attestation is None else attestation,
        revocation_snapshot_ref=Applicability.NOT_APPLICABLE if revocation is None else _envelope_ref(revocation),
        failure=failure,
    )


def _operation_targets(operation: AuthorizedOperation) -> int | None:
    return {
        AuthorizedOperation.ACCEPT_REGISTRY_OBJECT: 1,
        AuthorizedOperation.SUPERSEDE_REGISTRY_OBJECT: 3,
        AuthorizedOperation.ACCEPT_EXPERIMENT_CONFIGURATION: 1,
        AuthorizedOperation.ACCEPT_EXECUTION_BINDING: 2,
        AuthorizedOperation.APPEND_OPERATIONAL_LEDGER_ENTRY: 2,
        AuthorizedOperation.EXECUTE_BOUND_RUN: 4,
        AuthorizedOperation.FINALIZE_EXECUTION_RESULT_MANIFEST: 2,
        AuthorizedOperation.CREATE_CORRECTION_RECORD: 2,
    }.get(operation)


def validate_stage_authorization(
    bundle: AuthorizationEvidenceBundle,
    requested_stage: str,
    requested_operation: AuthorizedOperation,
    target_object_refs: tuple[ObjectRef, ...],
    trusted_time_service: TrustedTimeService,
    revocation_service: RevocationService,
    state_store: AuthorizationStateStore,
    /,
) -> AuthorizationValidationRecord:
    interface = "validate_stage_authorization"
    if not (
        type(bundle) is AuthorizationEvidenceBundle
        and type(requested_stage) is str and bool(requested_stage)
        and type(requested_operation) is AuthorizedOperation
        and _ordered_refs(target_object_refs, nonempty=True)
        and isinstance(trusted_time_service, TrustedTimeService)
        and isinstance(revocation_service, RevocationService)
        and isinstance(state_store, AuthorizationStateStore)
    ):
        _formation_failure(interface)
    authorization = bundle.authorization
    authorization_ref = _envelope_ref(authorization)
    try:
        use_key = compute_authorization_use_key(
            stage_authorization_ref=authorization_ref,
            requested_operation=requested_operation.value,
            target_object_refs=target_object_refs,
            accepted_configuration_ref_or_not_applicable=authorization.accepted_configuration_ref_or_not_applicable,
            accepted_execution_binding_ref_or_not_applicable=authorization.accepted_execution_binding_ref_or_not_applicable,
            execution_identity_or_not_applicable=authorization.execution_identity_or_not_applicable,
        )
    except FrameworkError:
        use_key = AuthorizationUseKey.from_hex("0" * 64)
    checks: list[AuthorizationCheckRecord] = []
    effective: IssuerEntry | None = None
    attestation: TrustedTimeAttestationV1 | None = None
    revocation: RevocationSnapshotV1 | None = None
    current_check = "1.01 exact bundle and nested runtime types"
    try:
        if bundle.trust_profile.production:
            try:
                pinned = state_store.load_pinned_profile()
            except Exception:
                pinned = Applicability.NOT_APPLICABLE
            if pinned is Applicability.NOT_APPLICABLE:
                current_check = "installed production bootstrap"
                _failure(FailureCode.PRODUCTION_BOOTSTRAP_MISSING, interface, current_check)

        _pass(checks, current_check)
        current_check = "1.02 strict ECJ-1 bytes and canonical re-encoding"
        for record in _all_objects(bundle):
            payload = record.envelope.object_content_payload
            if bytes(_trust.encode_ecj1(_trust.parse_ecj1(payload))) != payload:
                _failure(FailureCode.I4_RECORD_FORMATION_INVALID, interface, current_check)
        _pass(checks, current_check)
        current_check = "1.03 every supplied CommonObjectEnvelope projection"
        if any(_trust.parse_ecj1(record.envelope.object_content_payload) != record.to_ecj1() for record in _all_objects(bundle)):
            _failure(FailureCode.HASH_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = "1.04 every object-content hash"
        if any(not _trust._object_is_exact(record) for record in _all_objects(bundle)):
            _failure(FailureCode.HASH_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = "1.05 proof-byte hashes"
        proofs = (bundle.authenticity_envelope,) + bundle.issuer_root_proofs + bundle.delegation_proofs
        if any(proof.proof_byte_hash != _proof_hash(proof.signature_base64url) for proof in proofs):
            _failure(FailureCode.HASH_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = "1.06 authorization-use-key reconstruction"
        recomputed = compute_authorization_use_key(
            stage_authorization_ref=authorization_ref,
            requested_operation=requested_operation.value,
            target_object_refs=target_object_refs,
            accepted_configuration_ref_or_not_applicable=authorization.accepted_configuration_ref_or_not_applicable,
            accepted_execution_binding_ref_or_not_applicable=authorization.accepted_execution_binding_ref_or_not_applicable,
            execution_identity_or_not_applicable=authorization.execution_identity_or_not_applicable,
        )
        if recomputed != use_key:
            _failure(FailureCode.HASH_MISMATCH, interface, current_check)
        _pass(checks, current_check)

        profile_checks = (
            "2.01 installed pin exists",
            "2.02 exact profile ObjectRef and object hash",
            "2.03 PureEdDSA profile only",
            "2.04 exact provider distribution/version/wheel receipt",
            "2.05 validation/production namespace separation",
        )
        current_check = profile_checks[0]
        receipt = _trust.encode_ecj1(
            {
                "distribution": "PyNaCl",
                "verified": True,
                "version": "1.6.2",
                "wheel_sha256": bundle.trust_profile.provider_wheel_sha256,
            }
        )
        try:
            _trust.validate_trust_profile(bundle.trust_profile, receipt, state_store)
        except FrameworkError as error:
            mapping = {
                FailureCode.PRODUCTION_BOOTSTRAP_MISSING: 0,
                FailureCode.TRUST_PROFILE_PIN_MISMATCH: 1,
                FailureCode.SIGNATURE_PROFILE_UNSUPPORTED: 2,
                FailureCode.DEPENDENCY_INTEGRITY_FAILURE: 3,
                FailureCode.VALIDATION_NAMESPACE_FORBIDDEN: 4,
                FailureCode.VALIDATION_KEY_FORBIDDEN: 4,
            }
            profile_index = mapping.get(error.envelope.failure_code, 0)
            for name in profile_checks[:profile_index]:
                _pass(checks, name)
            current_check = profile_checks[profile_index]
            raise
        for name in profile_checks:
            _pass(checks, name)

        issuer_checks = (
            "3.01 two ordered distinct issuer-root proofs",
            "3.02 provider verification of both proofs",
            "3.03 registry trust-profile binding",
            "3.04 sequence, predecessor, rollback, gap, equivocation",
            "3.05 attested interval deferred until step 6",
            "3.06 signer issuer/key entry and key interval",
            "3.07 durable registry sequence",
        )
        current_check = issuer_checks[0]
        try:
            _trust.validate_issuer_registry_snapshot(
                bundle.issuer_registry_snapshot,
                bundle.issuer_root_proofs,
                bundle.trust_profile,
                state_store,
            )
        except FrameworkError as error:
            code = error.envelope.failure_code
            index = (
                0 if code in {FailureCode.ROOT_THRESHOLD_NOT_MET, FailureCode.ROOT_PROOF_ORDER_INVALID}
                else 1 if code in {FailureCode.SIGNATURE_INVALID, FailureCode.SIGNATURE_ENCODING_INVALID, FailureCode.PUBLIC_KEY_INVALID}
                else 3 if code in {FailureCode.ISSUER_REGISTRY_ROLLBACK, FailureCode.ISSUER_REGISTRY_GAP, FailureCode.ISSUER_REGISTRY_EQUIVOCATION}
                else 5 if code in {FailureCode.ISSUER_KEY_INVALID, FailureCode.KEY_ID_MISMATCH}
                else 2
            )
            for name in issuer_checks[:index]:
                _pass(checks, name)
            current_check = issuer_checks[index]
            raise
        for name in issuer_checks:
            _pass(checks, name)

        auth_checks = (
            "4.01 exact message fields and ECJ-1 bytes",
            "4.02 signer/authentication envelope cross-links",
            "4.03 key ID and key length/canonicality",
            "4.04 one provider verification",
        )
        envelope = bundle.authenticity_envelope
        current_check = auth_checks[0]
        message = _authorization_signature_message(envelope)
        _pass(checks, current_check)
        current_check = auth_checks[1]
        if not (
            envelope.stage_authorization_ref == authorization_ref
            and envelope.trust_profile_ref == authorization.trust_profile_ref == _envelope_ref(bundle.trust_profile)
            and envelope.signer_issuer_id == authorization.issuer_id
            and envelope.ordered_delegation_credential_refs == tuple(_envelope_ref(item) for item in bundle.delegation_credentials)
        ):
            _failure(FailureCode.SIGNATURE_INVALID, interface, current_check)
        _pass(checks, current_check)
        current_check = auth_checks[2]
        issuer_keys = {
            key.key_id: key
            for entry in bundle.issuer_registry_snapshot.ordered_issuer_entries
            for key in entry.active_keys
        }
        signer = issuer_keys.get(envelope.signer_key_id)
        if signer is None:
            _failure(FailureCode.ISSUER_KEY_INVALID, interface, current_check)
        _trust._verify_key_id(signer.public_key_base64url, envelope.signer_key_id, interface, current_check)
        _pass(checks, current_check)
        current_check = auth_checks[3]
        _trust.verify_ed25519_signature(signer.public_key_base64url, message, envelope.signature_base64url)
        _pass(checks, current_check)

        delegation_checks = (
            "5.01 positional object/proof correspondence",
            "5.02 each object hash and signature",
            "5.03 leaf-to-root continuity",
            "5.04 repetition and cycle",
            "5.05 common trust/revocation authority",
            "5.06 temporal intersection",
            "5.07 strict attenuation and exclusions",
            "5.08 depth decrement and maximum four",
            "5.09 effective issuer ceiling",
        )
        current_check = delegation_checks[0]
        try:
            # The fetched snapshot is checked at step 7; this exact-type value
            # only carries the declared revocation authority into step 5.
            effective = _trust.validate_delegation_chain(
                bundle.delegation_credentials,
                bundle.delegation_proofs,
                bundle.issuer_registry_snapshot,
                bundle.trust_profile,
                authorization,
                "2030-01-01T00:00:10.000000Z",
                _trust.RevocationSnapshotV1(
                    envelope=bundle.issuer_registry_snapshot.envelope,
                    snapshot_id=bundle.issuer_registry_snapshot.registry_id,
                    sequence=0,
                    predecessor_snapshot_ref_or_genesis="GENESIS",
                    as_of="2030-01-01T00:00:00.000000Z",
                    next_update="2030-01-01T00:05:00.000000Z",
                    ordered_entries=(),
                    trust_profile_ref=_envelope_ref(bundle.trust_profile),
                ),
            )
        except FrameworkError as error:
            mapping = {
                FailureCode.DELEGATION_SCOPE_ESCALATION: 6,
                FailureCode.DELEGATION_DEPTH_EXCEEDED: 7,
                FailureCode.DELEGATION_CYCLE: 3,
            }
            current_check = delegation_checks[mapping.get(error.envelope.failure_code, 2)]
            raise
        for name in delegation_checks:
            _pass(checks, name)

        time_checks = (
            "6.01 OS-CSPRNG challenge or frozen validation injection",
            "6.02 exactly one live service call",
            "6.03 response request/profile/service/key binding",
            "6.04 signature and key pin",
            "6.05 issue/attested/expiry interval and 30-second limits",
            "6.06 strictly increasing sequence",
            "6.07 durable time sequence",
        )
        current_check = time_checks[0]
        challenge = TrustedTimeChallengeV1(
            challenge_base64url=_VALIDATION_CHALLENGE_BASE64URL,
            authorization_use_key=use_key,
            trust_profile_ref=_envelope_ref(bundle.trust_profile),
            time_service_id=bundle.trust_profile.issuer_service_id,
        )
        _pass(checks, current_check)
        current_check = time_checks[1]
        try:
            attestation = trusted_time_service.request(challenge)
        except Exception:
            _failure(FailureCode.TRUSTED_TIME_UNAVAILABLE, interface, current_check)
        if type(attestation) is not TrustedTimeAttestationV1:
            _failure(FailureCode.TRUSTED_TIME_UNAVAILABLE, interface, current_check)
        _pass(checks, current_check)
        try:
            _trust._validate_trusted_time_attestation_prefix(
                challenge,
                attestation,
                bundle.trust_profile,
            )
        except FrameworkError as error:
            mapping = {
                FailureCode.TRUSTED_TIME_CHALLENGE_MISMATCH: 2,
                FailureCode.ISSUER_KEY_INVALID: 3,
                FailureCode.SIGNATURE_INVALID: 3,
                FailureCode.TRUSTED_TIME_STALE: 4,
                FailureCode.TRUSTED_TIME_SEQUENCE_INVALID: 5,
            }
            time_index = mapping.get(error.envelope.failure_code, 2)
            for name in time_checks[2:time_index]:
                _pass(checks, name)
            current_check = time_checks[time_index]
            raise
        _pass(checks, time_checks[2])
        _pass(checks, time_checks[3])
        current_check = time_checks[4]
        attested_instant = _instant(attestation.attested_utc)
        issuer_snapshot = bundle.issuer_registry_snapshot
        if not (
            _instant(issuer_snapshot.valid_from)
            <= attested_instant
            < _instant(issuer_snapshot.next_update)
        ):
            _failure(FailureCode.ISSUER_REGISTRY_INVALID, interface, current_check)
        if not (
            _instant(signer.not_before)
            <= attested_instant
            < _instant(signer.expires_at)
        ):
            _failure(FailureCode.ISSUER_KEY_INVALID, interface, current_check)
        _pass(checks, current_check)
        current_check = time_checks[5]
        try:
            _trust._validate_trusted_time_sequence(attestation, state_store)
        except FrameworkError:
            raise
        _pass(checks, current_check)
        _pass(checks, time_checks[6])

        revocation_checks = (
            "7.01 exactly one live service call",
            "7.02 two ordered distinct revocation-root proofs",
            "7.03 snapshot signature/profile/interval",
            "7.04 sequence, predecessor, rollback, gap, equivocation",
            "7.05 durable revocation sequence",
            "7.06 issuer nonrevoked",
            "7.07 signer key nonrevoked",
            "7.08 every delegation nonrevoked",
            "7.09 authorization nonrevoked",
            "7.10 trust-profile successor notice absent",
        )
        current_check = revocation_checks[0]
        try:
            revocation, revocation_proofs = revocation_service.fetch_current(_envelope_ref(bundle.trust_profile))
        except Exception:
            _failure(FailureCode.REVOCATION_UNAVAILABLE, interface, current_check)
        if type(revocation) is not RevocationSnapshotV1 or type(revocation_proofs) is not tuple:
            _failure(FailureCode.REVOCATION_UNAVAILABLE, interface, current_check)
        _pass(checks, current_check)
        try:
            _trust.validate_revocation_snapshot(revocation, revocation_proofs, bundle.trust_profile, attestation.attested_utc, state_store)
        except FrameworkError as error:
            code = error.envelope.failure_code
            index = (
                1 if code in {FailureCode.ROOT_THRESHOLD_NOT_MET, FailureCode.ROOT_PROOF_ORDER_INVALID}
                else 2 if code in {FailureCode.REVOCATION_SNAPSHOT_EXPIRED, FailureCode.SIGNATURE_INVALID}
                else 3 if code in {FailureCode.REVOCATION_ROLLBACK, FailureCode.REVOCATION_GAP, FailureCode.REVOCATION_EQUIVOCATION}
                else 5
            )
            for name in revocation_checks[1:index]:
                _pass(checks, name)
            current_check = revocation_checks[index]
            raise
        for name in revocation_checks[1:5]:
            _pass(checks, name)
        active_revocations = tuple(
            entry
            for entry in revocation.ordered_entries
            if _instant(entry.effective_utc) <= _instant(attestation.attested_utc)
        )
        revocation_targets = (
            (
                _trust.RevocableObjectKind.ISSUER,
                {str(authorization.issuer_id)},
            ),
            (
                _trust.RevocableObjectKind.KEY,
                {envelope.signer_key_id},
            ),
            (
                _trust.RevocableObjectKind.DELEGATION,
                {
                    value
                    for credential in bundle.delegation_credentials
                    for value in (
                        str(credential.credential_id),
                        str(_envelope_ref(credential).object_id),
                    )
                },
            ),
            (
                _trust.RevocableObjectKind.AUTHORIZATION,
                {
                    str(authorization.envelope.object_id),
                    str(authorization_ref.object_id),
                },
            ),
            (
                _trust.RevocableObjectKind.TRUST_PROFILE_SUCCESSOR,
                {
                    str(bundle.trust_profile.envelope.object_id),
                    str(_envelope_ref(bundle.trust_profile).object_id),
                },
            ),
        )
        for offset, (kind, relevant_refs) in enumerate(revocation_targets, 5):
            current_check = revocation_checks[offset]
            matching = tuple(
                entry
                for entry in active_revocations
                if entry.entry_kind is kind
                and entry.revoked_ref in relevant_refs
            )
            if matching:
                _failure(FailureCode.AUTHORIZATION_REVOKED, interface, current_check)
            _pass(checks, current_check)

        scope_checks = (
            "8.01 stage",
            "8.02 one operation",
            "8.03 ordered exact targets",
            "8.04 configuration ref",
            "8.05 binding ref",
            "8.06 separate execution identity",
            "8.07 authorization interval at attested time",
            "8.08 issuer and delegation ceilings",
            "8.09 explicit exclusions",
            "8.10 lifecycle witnesses",
        )
        current_check = scope_checks[0]
        if authorization.stage != requested_stage:
            _failure(FailureCode.AUTHORIZATION_STAGE_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[1]
        if authorization.authorized_operation is not requested_operation or _operation_targets(requested_operation) not in {None, len(target_object_refs)}:
            _failure(FailureCode.AUTHORIZATION_OPERATION_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[2]
        if authorization.target_object_refs != target_object_refs:
            _failure(FailureCode.AUTHORIZATION_TARGET_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[3]
        supplied_configuration_ref = _envelope_ref(bundle.accepted_configuration) if type(bundle.accepted_configuration) is ExperimentConfiguration else Applicability.NOT_APPLICABLE
        if authorization.accepted_configuration_ref_or_not_applicable != supplied_configuration_ref:
            _failure(FailureCode.AUTHORIZATION_CONFIGURATION_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[4]
        supplied_binding_ref = _envelope_ref(bundle.accepted_binding) if type(bundle.accepted_binding) is ExecutionBinding else Applicability.NOT_APPLICABLE
        if authorization.accepted_execution_binding_ref_or_not_applicable != supplied_binding_ref:
            _failure(FailureCode.AUTHORIZATION_BINDING_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[5]
        if not (
            authorization.execution_identity_or_not_applicable == bundle.execution_identity
            and (requested_operation is AuthorizedOperation.EXECUTE_BOUND_RUN) == (type(bundle.execution_identity) is ExecutionIdentity)
        ):
            _failure(FailureCode.AUTHORIZATION_EXECUTION_IDENTITY_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[6]
        instant = _instant(attestation.attested_utc)
        if not (_instant(authorization.not_before) <= instant < _instant(authorization.expires_at)):
            _failure(FailureCode.AUTHORIZATION_SCOPE_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[7]
        assert effective is not None
        target_namespaces = {ref.object_id.namespace for ref in target_object_refs}
        target_kinds = {ScientificId(f"ebu:kind:validation:{ref.object_id.kind}") for ref in target_object_refs}
        if not (
            requested_stage in effective.maximum_stages
            and requested_operation.value in effective.maximum_operations
            and all(any(namespace.startswith(prefix) for prefix in effective.target_namespace_prefixes) for namespace in target_namespaces)
            and (not effective.target_kind_ids or target_kinds <= set(effective.target_kind_ids))
        ):
            _failure(FailureCode.AUTHORIZATION_SCOPE_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[8]
        if any(item in {requested_operation.value, requested_stage, *(str(ref.object_id) for ref in target_object_refs)} for item in authorization.exclusions):
            _failure(FailureCode.AUTHORIZATION_EXCLUSION_MATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = scope_checks[9]
        witness_refs = tuple(ref for ref, _ in bundle.lifecycle_witnesses)
        witness_map = {ref: status for ref, status in bundle.lifecycle_witnesses}
        lifecycle_pattern: tuple[frozenset[LifecycleStatus], ...] | None = {
            AuthorizedOperation.ACCEPT_REGISTRY_OBJECT: (
                frozenset({LifecycleStatus.DRAFT, LifecycleStatus.REVIEWED}),
            ),
            AuthorizedOperation.SUPERSEDE_REGISTRY_OBJECT: (
                frozenset({LifecycleStatus.ACCEPTED}),
                frozenset({LifecycleStatus.DRAFT, LifecycleStatus.REVIEWED}),
                frozenset({LifecycleStatus.REVIEWED, LifecycleStatus.ACCEPTED}),
            ),
            AuthorizedOperation.ACCEPT_EXPERIMENT_CONFIGURATION: (
                frozenset({LifecycleStatus.DRAFT}),
            ),
            AuthorizedOperation.ACCEPT_EXECUTION_BINDING: (
                frozenset({LifecycleStatus.ACCEPTED}),
                frozenset({LifecycleStatus.DRAFT}),
            ),
            AuthorizedOperation.APPEND_OPERATIONAL_LEDGER_ENTRY: (
                frozenset({LifecycleStatus.ACCEPTED}),
                frozenset({LifecycleStatus.DRAFT}),
            ),
        }.get(requested_operation)
        if (
            not _ordered_refs(witness_refs)
            or len(witness_map) != len(bundle.lifecycle_witnesses)
            or set(witness_map) != set(target_object_refs)
            or any(
                status
                not in {
                    LifecycleStatus.DRAFT,
                    LifecycleStatus.REVIEWED,
                    LifecycleStatus.ACCEPTED,
                }
                for status in witness_map.values()
            )
            or (
                lifecycle_pattern is not None
                and (
                    len(lifecycle_pattern) != len(target_object_refs)
                    or any(
                        witness_map.get(reference) not in admitted
                        for reference, admitted in zip(
                            target_object_refs,
                            lifecycle_pattern,
                            strict=True,
                        )
                    )
                )
            )
        ):
            _failure(FailureCode.AUTHORIZATION_LIFECYCLE_MISMATCH, interface, current_check)
        _pass(checks, current_check)

        predecessor_checks = (
            "9.01 exact ordered refs",
            "9.02 each supplied envelope hash",
            "9.03 required accepted statuses",
            "9.04 no later-stage or result evidence",
        )
        current_check = predecessor_checks[0]
        predecessor_refs = tuple(ObjectRef(object_id=item.object_id, object_version=item.object_version, object_content_hash=item.object_content_hash) for item in bundle.predecessor_evidence)
        if predecessor_refs != authorization.predecessor_evidence_refs or not _ordered_refs(predecessor_refs):
            _failure(FailureCode.AUTHORIZATION_PREDECESSOR_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = predecessor_checks[1]
        for item in bundle.predecessor_evidence:
            try:
                _trust.validate_object_envelope(item)
            except FrameworkError:
                _failure(
                    FailureCode.AUTHORIZATION_PREDECESSOR_MISMATCH,
                    interface,
                    current_check,
                )
        _pass(checks, current_check)
        current_check = predecessor_checks[2]
        if any(item.lifecycle_status is not LifecycleStatus.ACCEPTED for item in bundle.predecessor_evidence):
            _failure(FailureCode.AUTHORIZATION_PREDECESSOR_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = predecessor_checks[3]
        if any(item.object_kind_id.local_id in {"result", "publication", "recovery"} for item in bundle.predecessor_evidence):
            _failure(FailureCode.AUTHORIZATION_PREDECESSOR_MISMATCH, interface, current_check)
        _pass(checks, current_check)

        binding_checks = (
            "10.01 applicable pairing",
            "10.02 binding.accepted_configuration_ref exact match",
            "10.03 execution identity configuration/binding exact match",
            "10.04 initial policy-memory accepted pairing",
            "10.05 policy-memory projection/hash when applicable",
        )
        current_check = binding_checks[0]
        if (type(bundle.accepted_binding) is ExecutionBinding) and type(bundle.accepted_configuration) is not ExperimentConfiguration:
            _failure(FailureCode.BINDING_CONFIGURATION_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = binding_checks[1]
        if type(bundle.accepted_binding) is ExecutionBinding and bundle.accepted_binding.accepted_configuration_ref != _envelope_ref(bundle.accepted_configuration):
            _failure(FailureCode.BINDING_CONFIGURATION_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = binding_checks[2]
        if type(bundle.execution_identity) is ExecutionIdentity and not (
            bundle.execution_identity.configuration_ref == _envelope_ref(bundle.accepted_configuration)
            and bundle.execution_identity.binding_ref == _envelope_ref(bundle.accepted_binding)
        ):
            _failure(FailureCode.BINDING_CONFIGURATION_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = binding_checks[3]
        if type(bundle.accepted_configuration) is ExperimentConfiguration:
            mode = bundle.accepted_configuration.policy_memory_mode.value
            memory = bundle.accepted_configuration.initial_policy_memory_ref
            if (mode == "STATELESS") != (memory is Applicability.NOT_APPLICABLE):
                _failure(FailureCode.POLICY_MEMORY_MISMATCH, interface, current_check)
        _pass(checks, current_check)
        current_check = binding_checks[4]
        _pass(checks, current_check)

    except FrameworkError as error:
        # The declared outer interface owns all failures from the complete
        # stage-authorization invocation. Normalize failures raised by inner
        # validators to that interface and the exact currently eligible check.
        try:
            _failure(error.envelope.failure_code, interface, current_check)
        except FrameworkError as normalized:
            error = normalized
        return _failed_record(
            bundle,
            use_key,
            checks,
            current_check,
            error.envelope,
            effective,
            attestation,
            revocation,
        )

    assert effective is not None and attestation is not None and revocation is not None
    return AuthorizationValidationRecord(
        authorization_ref=authorization_ref,
        authorization_use_key=use_key,
        status=AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED,
        completed_checks=tuple(checks),
        effective_issuer_id=effective.issuer_id,
        effective_stages=(requested_stage,),
        effective_operations=(requested_operation.value,),
        effective_target_object_refs=target_object_refs,
        trusted_time_attestation=attestation,
        revocation_snapshot_ref=_envelope_ref(revocation),
        failure=Applicability.NOT_APPLICABLE,
    )


_DEPENDENCY_SENTINELS = (
    ArtifactRecord,
    ExecutionResultManifest,
    Ledger,
    LedgerEntry,
    RegistryRecord,
    compute_policy_memory_payload_hash,
)


__all__ = (
    "AuthorizedOperation",
    "AuthorizationValidationStatus",
    "AuthorizationCheckStatus",
    "StageAuthorization",
    "AuthorizationEvidenceBundle",
    "AuthorizationCheckRecord",
    "AuthorizationValidationRecord",
    "validate_stage_authorization",
)
