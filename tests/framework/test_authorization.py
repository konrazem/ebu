"""Frozen T0 and synthetic T1 Framework I-4 authorization validation."""

from __future__ import annotations

import ast
import base64
from collections import Counter
from dataclasses import dataclass, fields, is_dataclass, replace
from enum import StrEnum
import hashlib
import inspect
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

import ebu_framework as framework
import ebu_framework.authorization as authorization
import ebu_framework.authorization_use as authorization_use
import ebu_framework.trust as trust
from ebu_framework.canonical import encode_ecj1, parse_ecj1
from ebu_framework.conservation import ConservationProfileSelection
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import FailureCode, FrameworkError
from ebu_framework.experiment import (
    ExecutionBinding,
    ExecutionIdentity,
    ExecutionMode,
    ExperimentConfiguration,
)
from ebu_framework.hashing import (
    compute_execution_semantics_hash,
    compute_object_content_hash,
)
from ebu_framework.identity import (
    ArtifactByteHash,
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)
from ebu_framework.numeric import IntegerV1
from ebu_framework.policy import MemoryMode
from nacl.signing import SigningKey


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).with_name("fixtures") / "authorization_vectors_v1.json"
MECHANICAL = ROOT / "unified_python_research_framework_i4_contract.json"
VALIDATION = ROOT / "unified_python_research_framework_i4_validation_contract.json"


def _strict(path: Path) -> object:
    def pairs(values: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in values:
            if key in result:
                raise AssertionError(f"duplicate JSON name in {path}: {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8", errors="strict"),
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            AssertionError(f"non-finite JSON number in {path}: {value}")
        ),
    )


def _fixture() -> tuple[dict[str, object], list[dict[str, object]]]:
    document = _strict(FIXTURE)
    assert type(document) is dict and type(document["vectors"]) is list
    return document, document["vectors"]


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


_RFC = (
    (
        bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"),
        b"",
        bytes.fromhex(
            "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e06522490155"
            "5fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
        ),
    ),
    (
        bytes.fromhex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"),
        b"\x72",
        bytes.fromhex(
            "92a009a9f0d4cab8720e820b5f642540a2b27b5416503f8fb3762223ebdb69da"
            "085ac1e43e15996e458f3613d0f11d8c387b2eaeb4302aeeb00d291612bb0c00"
        ),
    ),
    (
        bytes.fromhex("fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025"),
        b"\xaf\x82",
        bytes.fromhex(
            "6291d657deec24024827e69c3abe01a30ce548a284743a445e3680d7db5ac3ac"
            "18ff9b538d16f290ae67f760984dc6594a7c15e9716ed28dc027beceea1ec40a"
        ),
    ),
)


def _provider_input(case: str) -> tuple[str, bytes, str]:
    public, message, signature = _RFC[0]
    if case == "RFC8032_TEST_1":
        pass
    elif case == "RFC8032_TEST_2":
        public, message, signature = _RFC[1]
    elif case == "RFC8032_TEST_3":
        public, message, signature = _RFC[2]
    elif case == "ED25519CTX":
        message = b"Ed25519ctx"
    elif case == "ED25519PH":
        message = b"Ed25519ph"
    elif case == "PREHASH":
        message = b"prehash"
    elif case == "KEY_LENGTH_31":
        public = bytes(range(31))
    elif case == "KEY_LENGTH_33":
        public = bytes(range(33))
    elif case == "SIGNATURE_LENGTH_63":
        signature = signature[:63]
    elif case == "SIGNATURE_LENGTH_65":
        signature += b"\x00"
    elif case == "BASE64_PADDING":
        return _b64(public), message, _b64(signature) + "="
    elif case == "BASE64_NONALPHABET":
        return _b64(public), message, "*"
    elif case == "NONCANONICAL_Y":
        public = (2**255 - 19).to_bytes(32, "little")
    elif case == "SMALL_ORDER_PUBLIC":
        public = b"\x01" + b"\x00" * 31
    elif case == "SMALL_ORDER_R":
        signature = b"\x01" + b"\x00" * 63
    elif case == "S_EQUALS_L":
        signature = signature[:32] + trust._L.to_bytes(32, "little")
    elif case == "S_GREATER_L":
        signature = signature[:32] + (trust._L + 1).to_bytes(32, "little")
    elif case == "WRONG_KEY":
        public = _RFC[1][0]
    elif case == "WRONG_MESSAGE":
        message = b"{}"
    elif case == "WRONG_SIGNATURE":
        changed = bytearray(signature)
        changed[32] ^= 1
        signature = bytes(changed)
    else:
        raise AssertionError(case)
    return _b64(public), message, _b64(signature)


class FrameworkI4ProviderTests(unittest.TestCase):
    def test_i4v_001_through_i4v_020_provider(self) -> None:
        _, vectors = _fixture()
        selected = vectors[:20]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in selected),
            tuple(f"i4v-{index:03d}" for index in range(1, 21)),
        )
        import nacl.signing

        real_verify_key = nacl.signing.VerifyKey
        calls = Counter()

        class CountingVerifyKey:
            def __init__(self, *args: object, **kwargs: object) -> None:
                calls["constructor"] += 1
                self._delegate = real_verify_key(*args, **kwargs)

            def verify(self, *args: object, **kwargs: object) -> bytes:
                calls["verify"] += 1
                return self._delegate.verify(*args, **kwargs)

        for vector in selected:
            expected = vector["expected"]
            case = vector["effective_input"]["key_case"]
            public, message, signature = _provider_input(case)
            before = calls.copy()
            real_owner = trust.verify_ed25519_signature
            with self.subTest(vector_id=vector["vector_id"]), patch.object(
                trust, "verify_ed25519_signature", wraps=real_owner
            ) as owner, patch(
                "nacl.signing.VerifyKey", CountingVerifyKey
            ), framework.errors._i4_validation_context(
                expected["failure_ordinal"], vector["name"]
            ):
                if expected["outcome"] == "SUCCESS":
                    self.assertIsNone(
                        trust.verify_ed25519_signature(public, message, signature)
                    )
                else:
                    with self.assertRaises(FrameworkError) as raised:
                        trust.verify_ed25519_signature(public, message, signature)
                    envelope = raised.exception.envelope
                    self.assertEqual(envelope.failure_code.value, expected["failure_code"])
                    self.assertEqual(envelope.failure_ordinal, expected["failure_ordinal"])
                    self.assertNotIn("exception", envelope.human_summary.lower())
                    _assert_failure(self, vector, raised.exception)
            self.assertEqual(owner.call_count, 1)
            actual_constructor = calls["constructor"] - before["constructor"]
            actual_verify = calls["verify"] - before["verify"]
            self.assertEqual(actual_constructor, expected["provider_calls"]["verify_key_constructor"])
            self.assertEqual(actual_verify, expected["provider_calls"]["verify"])


_VALIDATION = _strict(VALIDATION)
_SEEDS = {
    label: SigningKey(bytes.fromhex(seed))
    for label, seed in _VALIDATION["fixed_authority"]["synthetic_key_seeds_hex"].items()
}
_ATTESTED = _VALIDATION["fixed_authority"]["injected_attested_utc"]
_VERSION = SemanticVersion("1.0.0")


def _key_material(label: str) -> tuple[SigningKey, str, str]:
    signing_key = _SEEDS[label]
    raw = bytes(signing_key.verify_key)
    return signing_key, "ed25519:" + hashlib.sha256(raw).hexdigest(), _b64(raw)


def _ref(kind: str, label: str, fill: str = "1") -> ObjectRef:
    return ObjectRef(
        object_id=ScientificId(f"ebu:{kind}:validation:{label}"),
        object_version=_VERSION,
        object_content_hash=ObjectContentHash("sha256:" + fill * 64),
    )


def _envelope(
    label: str,
    kind: str,
    payload: object,
    *,
    lifecycle: LifecycleStatus = LifecycleStatus.ACCEPTED,
) -> CommonObjectEnvelope:
    object_id = ScientificId(f"ebu:{kind}:validation:{label}")
    kind_id = ScientificId(f"ebu:kind:validation:{kind}")
    schema_id = ScientificId(f"ebu:schema:validation:{kind}-v1")
    return CommonObjectEnvelope(
        object_id=object_id,
        object_kind_id=kind_id,
        schema_id=schema_id,
        schema_version=_VERSION,
        object_version=_VERSION,
        authority_refs=(),
        supersedes_ref=framework.Applicability.NOT_APPLICABLE,
        object_content_payload=bytes(encode_ecj1(payload)),
        object_content_hash=compute_object_content_hash(
            object_id=object_id,
            object_kind=str(kind_id),
            schema_id=schema_id,
            schema_version=_VERSION,
            object_version=_VERSION,
            authority_refs=(),
            supersedes_ref=None,
            object_content_payload=payload,
        ),
        lifecycle_status=lifecycle,
        record_metadata_ref=framework.Applicability.NOT_APPLICABLE,
    )


def _seal(
    runtime: type,
    label: str,
    kind: str,
    values: dict[str, object],
    *,
    lifecycle: LifecycleStatus = LifecycleStatus.ACCEPTED,
) -> object:
    provisional = runtime(
        envelope=_envelope(label, kind, {}, lifecycle=lifecycle), **values
    )
    return replace(
        provisional,
        envelope=_envelope(
            label, kind, provisional.to_ecj1(), lifecycle=lifecycle
        ),
    )


def _record_ref(record: object) -> ObjectRef:
    envelope = record.envelope
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _signature(
    signing_key: SigningKey, message: bytes
) -> tuple[str, ArtifactByteHash]:
    raw = signing_key.sign(message).signature
    return _b64(raw), ArtifactByteHash.from_hex(hashlib.sha256(raw).hexdigest())


@dataclass
class _StateStore:
    pinned: ObjectRef | framework.Applicability
    issuer_state: tuple[int, ObjectRef] | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    revocation_state: tuple[int, ObjectRef] | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    time_sequence: int | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    persisted: list[tuple[str, int, ObjectRef]] | None = None

    def __post_init__(self) -> None:
        if self.persisted is None:
            self.persisted = []

    def load_pinned_profile(self) -> ObjectRef | framework.Applicability:
        return self.pinned

    def load_last_issuer_state(
        self,
    ) -> tuple[int, ObjectRef] | framework.Applicability:
        return self.issuer_state

    def load_last_revocation_state(
        self,
    ) -> tuple[int, ObjectRef] | framework.Applicability:
        return self.revocation_state

    def load_last_time_sequence(
        self, service_id: ScientificId, /
    ) -> int | framework.Applicability:
        del service_id
        return self.time_sequence

    def persist_validated_state(
        self, kind: str, sequence: int, record_ref: ObjectRef, /
    ) -> None:
        assert self.persisted is not None
        self.persisted.append((kind, sequence, record_ref))


def _key_pin(label: str, role: trust.RootRole) -> trust.KeyPinV1:
    _, key_id, public = _key_material(label)
    return trust.KeyPinV1(
        key_id=key_id,
        public_key_base64url=public,
        role=role,
        not_before="2029-01-01T00:00:00.000000Z",
        expires_at="2031-01-01T00:00:00.000000Z",
    )


def _profile(
    profile_case: str = "VALID_SYNTHETIC_NONPRODUCTION",
) -> trust.TrustProfileV1:
    issuer_pins = tuple(
        _key_pin(
            f"ebu-i4-validation-issuer-root-{index}",
            trust.RootRole.ISSUER_ROOT,
        )
        for index in range(1, 4)
    )
    revocation_pins = tuple(
        _key_pin(
            f"ebu-i4-validation-revocation-root-{index}",
            trust.RootRole.REVOCATION_ROOT,
        )
        for index in range(1, 4)
    )
    time_pins = tuple(
        sorted(
            (
                _key_pin(
                    f"ebu-i4-validation-time-{index}",
                    trust.RootRole.TIME_SERVICE,
                )
                for index in range(1, 4)
            ),
            key=lambda item: bytes(encode_ecj1(item.to_ecj1())),
        )
    )
    production = profile_case in {"PRODUCTION", "PRODUCTION_NO_BOOTSTRAP"}
    wheel_hash = (
        "0" * 64
        if profile_case == "DEPENDENCY_MISMATCH"
        else "c949ea47e4206af7c8f604b8278093b674f7c79ed0d4719cc836902bf4517465"
    )
    values = {
        "signature_profile": trust.SignatureProfile.EBU_AUTHORIZATION_ED25519_V1,
        "issuer_root_threshold": trust.RootThresholdV1(
            role=trust.RootRole.ISSUER_ROOT,
            required_signatures=2,
            ordered_key_ids=tuple(sorted(pin.key_id for pin in issuer_pins)),
        ),
        "revocation_root_threshold": trust.RootThresholdV1(
            role=trust.RootRole.REVOCATION_ROOT,
            required_signatures=2,
            ordered_key_ids=tuple(
                sorted(pin.key_id for pin in revocation_pins)
            ),
        ),
        "time_service_keys": time_pins,
        "issuer_service_id": ScientificId(
            "ebu:time-service:validation:synthetic"
        ),
        "revocation_service_id": ScientificId(
            "ebu:revocation-service:validation:synthetic"
        ),
        "permitted_stages": ("I-4",),
        "permitted_operations": tuple(
            sorted(item.value for item in authorization.AuthorizedOperation)
        ),
        "maximum_delegation_depth": 4,
        "maximum_time_response_age_seconds": 30,
        "maximum_revocation_lifetime_seconds": 300,
        "validation_namespace_prefix": "validation",
        "production": production,
        "provider_distribution_name": "PyNaCl",
        "provider_distribution_version": "1.6.2",
        "provider_wheel_sha256": wheel_hash,
    }
    return _seal(
        trust.TrustProfileV1, "synthetic", "trust-profile", values
    )


def _issuer_key(
    issuer_id: ScientificId,
    label: str,
    *,
    expired: bool = False,
    mismatched: bool = False,
) -> trust.IssuerKeyV1:
    _, key_id, public = _key_material(label)
    if mismatched:
        key_id = "ed25519:" + "0" * 64
    return trust.IssuerKeyV1(
        issuer_id=issuer_id,
        key_id=key_id,
        public_key_base64url=public,
        not_before="2029-01-01T00:00:00.000000Z",
        expires_at=(
            "2030-01-01T00:00:10.000000Z"
            if expired
            else "2031-01-01T00:00:00.000000Z"
        ),
    )


def _issuer_entry(
    issuer_id: ScientificId,
    active_keys: tuple[trust.IssuerKeyV1, ...],
) -> trust.IssuerEntry:
    return trust.IssuerEntry(
        issuer_id=issuer_id,
        governance_evidence_refs=(),
        active_keys=tuple(
            sorted(
                active_keys,
                key=lambda item: bytes(encode_ecj1(item.to_ecj1())),
            )
        ),
        maximum_stages=("I-4",),
        maximum_operations=tuple(
            sorted(item.value for item in authorization.AuthorizedOperation)
        ),
        target_namespace_prefixes=("validation",),
        target_kind_ids=(
            ScientificId("ebu:kind:validation:registry-object"),
        ),
        delegation_allowed=True,
        maximum_delegated_depth=4,
        explicit_exclusions=("PUBLISH_ARTIFACTS",),
    )


def _trust_proof(
    evidence: object,
    profile: trust.TrustProfileV1,
    label: str,
    role: trust.RootRole,
    kind: trust.TrustEvidenceKind,
) -> trust.TrustEvidenceEnvelopeV1:
    _, key_id, _ = _key_material(label)
    values: dict[str, object] = {
        "signature_profile": (
            trust.SignatureProfile.EBU_AUTHORIZATION_ED25519_V1
        ),
        "evidence_kind": kind,
        "evidence_ref": _record_ref(evidence),
        "trust_profile_ref": _record_ref(profile),
        "signer_role": role,
        "signer_key_id": key_id,
        "signature_base64url": "AA",
        "proof_byte_hash": ArtifactByteHash.from_hex(
            hashlib.sha256(b"\x00").hexdigest()
        ),
    }
    provisional = _seal(
        trust.TrustEvidenceEnvelopeV1,
        f"proof-{key_id[-8:]}",
        "trust-proof",
        values,
    )
    signature, proof_hash = _signature(
        _SEEDS[label], trust._trust_message(provisional)
    )
    values["signature_base64url"] = signature
    values["proof_byte_hash"] = proof_hash
    return _seal(
        trust.TrustEvidenceEnvelopeV1,
        f"proof-{key_id[-8:]}",
        "trust-proof",
        values,
    )


def _issuer_material(
    profile: trust.TrustProfileV1,
    issuer_case: str,
    *,
    include_delegate: bool = False,
) -> tuple[
    trust.IssuerRegistrySnapshotV1,
    tuple[trust.TrustEvidenceEnvelopeV1, ...],
    _StateStore,
]:
    issuer_id = ScientificId("ebu:issuer:validation:issuer-1")
    root_key = _issuer_key(
        issuer_id,
        "ebu-i4-validation-issuer-1",
        expired=issuer_case == "KEY_EXPIRED",
        mismatched=issuer_case == "KEY_ID_MISMATCH",
    )
    auxiliary_labels = (
        "ebu-i4-validation-issuer-root-1",
        "ebu-i4-validation-issuer-root-2",
        "ebu-i4-validation-issuer-root-3",
        "ebu-i4-validation-revocation-root-1",
    )
    root_keys = (root_key,) + (
        tuple(_issuer_key(issuer_id, label) for label in auxiliary_labels)
        if include_delegate
        else ()
    )
    entries = [_issuer_entry(issuer_id, root_keys)]
    if include_delegate:
        delegate_id = ScientificId("ebu:issuer:validation:delegate-1")
        entries.append(
            _issuer_entry(
                delegate_id,
                (
                    _issuer_key(
                        delegate_id, "ebu-i4-validation-delegate-1"
                    ),
                ),
            )
        )
    sequence = 0
    predecessor: ObjectRef | str = "GENESIS"
    last: tuple[int, ObjectRef] | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    prior = _ref("issuer-registry", "prior", "8")
    if issuer_case == "ROLLBACK":
        last = (1, prior)
    elif issuer_case == "GAP":
        sequence, predecessor, last = 2, prior, (0, prior)
    elif issuer_case == "EQUIVOCATION":
        last = (0, prior)
    values = {
        "registry_id": ScientificId(
            "ebu:issuer-registry:validation:synthetic"
        ),
        "sequence": sequence,
        "predecessor_snapshot_ref_or_genesis": predecessor,
        "valid_from": "2029-12-31T00:00:00.000000Z",
        "next_update": (
            "2030-01-01T00:00:10.000000Z"
            if issuer_case == "EXPIRED"
            else "2030-01-01T00:05:00.000000Z"
        ),
        "ordered_issuer_entries": tuple(
            sorted(
                entries,
                key=lambda item: bytes(encode_ecj1(item.to_ecj1())),
            )
        ),
        "trust_profile_ref": _record_ref(profile),
    }
    snapshot = _seal(
        trust.IssuerRegistrySnapshotV1,
        f"issuer-{issuer_case.lower()}",
        "issuer-registry",
        values,
    )
    proofs = tuple(
        sorted(
            (
                _trust_proof(
                    snapshot,
                    profile,
                    f"ebu-i4-validation-issuer-root-{index}",
                    trust.RootRole.ISSUER_ROOT,
                    trust.TrustEvidenceKind.ISSUER_REGISTRY,
                )
                for index in (1, 2)
            ),
            key=lambda item: item.signer_key_id,
        )
    )
    if issuer_case == "THRESHOLD_ONE":
        proofs = proofs[:1]
    elif issuer_case == "DUPLICATE_ROOT":
        proofs = (proofs[0], proofs[0])
    elif issuer_case == "PROOF_ORDER":
        proofs = tuple(reversed(proofs))
    return snapshot, proofs, _StateStore(
        pinned=_record_ref(profile), issuer_state=last
    )


def _stage_authorization(
    profile: trust.TrustProfileV1,
    revocation_ref: ObjectRef,
    issuer_id: ScientificId,
    target_refs: tuple[ObjectRef, ...],
    *,
    operation: authorization.AuthorizedOperation = (
        authorization.AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
    ),
    stage: str = "I-4",
    configuration_ref: ObjectRef | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    ),
    binding_ref: ObjectRef | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    ),
    execution_identity: ExecutionIdentity | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    ),
    predecessor_refs: tuple[ObjectRef, ...] = (),
    not_before: str = "2029-12-31T00:00:00.000000Z",
    expires_at: str = "2031-01-01T00:00:00.000000Z",
    exclusions: tuple[str, ...] = (),
) -> authorization.StageAuthorization:
    values = {
        "stage": stage,
        "authorized_operation": operation,
        "target_object_refs": target_refs,
        "accepted_configuration_ref_or_not_applicable": configuration_ref,
        "accepted_execution_binding_ref_or_not_applicable": binding_ref,
        "execution_identity_or_not_applicable": execution_identity,
        "predecessor_evidence_refs": predecessor_refs,
        "not_before": not_before,
        "expires_at": expires_at,
        "maximum_invocations": 1,
        "issuer_id": issuer_id,
        "revocation_snapshot_ref": revocation_ref,
        "trust_profile_ref": _record_ref(profile),
        "exclusions": exclusions,
    }
    return _seal(
        authorization.StageAuthorization, "stage", "authorization", values
    )


def _delegation_material(
    case: str,
    profile: trust.TrustProfileV1,
    snapshot: trust.IssuerRegistrySnapshotV1,
    revocation_ref: ObjectRef,
    target_refs: tuple[ObjectRef, ...],
) -> tuple[
    tuple[trust.DelegationCredentialV1, ...],
    tuple[trust.TrustEvidenceEnvelopeV1, ...],
    authorization.StageAuthorization,
]:
    root_id = ScientificId("ebu:issuer:validation:issuer-1")
    if case == "VALID_NONE":
        return (), (), _stage_authorization(
            profile, revocation_ref, root_id, target_refs
        )
    depth = (
        4
        if case == "DEPTH_FIVE"
        else 2
        if case
        in {
            "REPEATED_CREDENTIAL",
            "REPEATED_ISSUER_KEY",
            "CYCLE",
            "CONTINUITY_BREAK",
        }
        else 1
    )
    labels = [
        "ebu-i4-validation-issuer-1",
        "ebu-i4-validation-delegate-1",
        "ebu-i4-validation-issuer-root-1",
        "ebu-i4-validation-issuer-root-2",
        "ebu-i4-validation-issuer-root-3",
    ]
    ids = [root_id] + [
        ScientificId(f"ebu:issuer:validation:delegate-{index}")
        for index in range(1, depth + 1)
    ]
    if case in {"REPEATED_ISSUER_KEY", "CYCLE"}:
        ids[-1] = root_id
        labels[depth] = labels[0]
    rootward: list[trust.DelegationCredentialV1] = []
    for index in range(depth):
        _, delegator_key, _ = _key_material(labels[index])
        _, delegate_key, _ = _key_material(labels[index + 1])
        stages = (
            ("I-4", "I-5") if case == "STAGE_ESCALATION" else ("I-4",)
        )
        operations = (
            tuple(
                sorted(
                    item.value for item in authorization.AuthorizedOperation
                )
            )
            if case != "OPERATION_ESCALATION"
            else tuple(
                sorted(
                    (
                        *(
                            item.value
                            for item in authorization.AuthorizedOperation
                        ),
                        "UNDECLARED",
                    )
                )
            )
        )
        parent: ObjectRef | str = (
            "REGISTRY_ENTRY" if index == 0 else _record_ref(rootward[-1])
        )
        if case == "CONTINUITY_BREAK" and index == depth - 1:
            parent = _ref("delegation", "wrong-parent", "9")
        values = {
            "credential_id": ScientificId(
                "ebu:delegation:validation:repeated"
                if case == "REPEATED_CREDENTIAL"
                else f"ebu:delegation:validation:credential-{index + 1}"
            ),
            "delegator_issuer_id": ids[index],
            "delegator_key_id": delegator_key,
            "delegate_issuer_id": ids[index + 1],
            "delegate_key_id": delegate_key,
            "parent_credential_ref_or_registry_entry": parent,
            "permitted_stages": stages,
            "permitted_operations": operations,
            "target_namespace_prefixes": (
                ("other",) if case == "TARGET_ESCALATION" else ("validation",)
            ),
            "target_kind_ids": (
                ScientificId("ebu:kind:validation:registry-object"),
            ),
            "not_before": (
                "2028-01-01T00:00:00.000000Z"
                if case == "TIME_ESCALATION"
                else "2029-12-31T00:00:00.000000Z"
            ),
            "expires_at": "2030-12-31T00:00:00.000000Z",
            "delegation_allowed": True,
            "remaining_maximum_depth": (
                2 if case == "DEPTH_FIVE" and index == 0 else max(0, 3 - index)
            ),
            "revocation_registry_ref": revocation_ref,
            "explicit_exclusions": (
                () if case == "EXCLUSION_DROP" else ("PUBLISH_ARTIFACTS",)
            ),
        }
        rootward.append(
            _seal(
                trust.DelegationCredentialV1,
                f"credential-{case.lower()}-{index + 1}",
                "delegation",
                values,
            )
        )
    credentials = tuple(reversed(rootward))
    proof_items = []
    for credential in credentials:
        label = next(
            item
            for item in labels
            if _key_material(item)[1] == credential.delegator_key_id
        )
        proof_items.append(
            _trust_proof(
                credential,
                profile,
                label,
                trust.RootRole.ISSUER_ROOT,
                trust.TrustEvidenceKind.DELEGATION_CREDENTIAL,
            )
        )
    _, leaf_key_id, _ = _key_material(labels[depth])
    del leaf_key_id
    stage = _stage_authorization(
        profile, revocation_ref, ids[-1], target_refs
    )
    return credentials, tuple(proof_items), stage


def _time_material(
    case: str,
    profile: trust.TrustProfileV1,
    use_key: framework.AuthorizationUseKey,
    store: _StateStore,
) -> tuple[
    trust.TrustedTimeChallengeV1, trust.TrustedTimeAttestationV1
]:
    challenge = trust.TrustedTimeChallengeV1(
        challenge_base64url=authorization._VALIDATION_CHALLENGE_BASE64URL,
        authorization_use_key=use_key,
        trust_profile_ref=_record_ref(profile),
        time_service_id=profile.issuer_service_id,
    )
    time_label = next(
        label
        for label in _SEEDS
        if label.startswith("ebu-i4-validation-time-")
        and _key_material(label)[1] == profile.time_service_keys[0].key_id
    )
    _, signer_id, _ = _key_material(time_label)
    values: dict[str, object] = {
        "trust_profile_ref": _record_ref(profile),
        "time_service_id": profile.issuer_service_id,
        "signer_key_id": signer_id,
        "challenge_base64url": challenge.challenge_base64url,
        "authorization_use_key": use_key,
        "attested_utc": _ATTESTED,
        "service_sequence": 1,
        "issued_at": "2030-01-01T00:00:09.000000Z",
        "expires_at": "2030-01-01T00:00:20.000000Z",
        "signature_base64url": "AA",
    }
    if case == "CHALLENGE_MISMATCH":
        values["challenge_base64url"] = _b64(b"x" * 32)
    elif case == "USE_KEY_MISMATCH":
        values["authorization_use_key"] = (
            framework.AuthorizationUseKey.from_hex("f" * 64)
        )
    elif case == "PROFILE_MISMATCH":
        values["trust_profile_ref"] = _ref(
            "trust-profile", "other", "e"
        )
    elif case == "SIGNER_UNPINNED":
        _, values["signer_key_id"], _ = _key_material(
            "ebu-i4-validation-issuer-1"
        )
        time_label = "ebu-i4-validation-issuer-1"
    elif case == "WINDOW_OVER_30":
        values["issued_at"] = "2030-01-01T00:00:00.000000Z"
        values["expires_at"] = "2030-01-01T00:00:31.000000Z"
    elif case == "STALE":
        values["expires_at"] = "2030-01-01T00:00:10.000000Z"
    elif case == "SEQUENCE_REPLAY":
        store.time_sequence = 1
    provisional = trust.TrustedTimeAttestationV1(**values)
    values["signature_base64url"] = _signature(
        _SEEDS[time_label], trust._time_message(provisional)
    )[0]
    return challenge, trust.TrustedTimeAttestationV1(**values)


def _revocation_material(
    case: str,
    profile: trust.TrustProfileV1,
    store: _StateStore,
    revoked: tuple[trust.RevocableObjectKind, str] | None = None,
) -> tuple[
    trust.RevocationSnapshotV1,
    tuple[trust.TrustEvidenceEnvelopeV1, ...],
]:
    sequence = 0
    predecessor: ObjectRef | str = "GENESIS"
    prior = _ref("revocation", "prior", "a")
    if case == "ROLLBACK":
        store.revocation_state = (1, prior)
    elif case == "GAP":
        sequence, predecessor, store.revocation_state = 2, prior, (0, prior)
    elif case == "EQUIVOCATION":
        store.revocation_state = (0, prior)
    entries: tuple[trust.RevocationEntryV1, ...] = ()
    if revoked is not None:
        entries = (
            trust.RevocationEntryV1(
                entry_kind=revoked[0],
                revoked_ref=revoked[1],
                effective_utc="2030-01-01T00:00:00.000000Z",
                reason="synthetic validation revocation",
            ),
        )
    values = {
        "snapshot_id": ScientificId("ebu:revocation:validation:synthetic"),
        "sequence": sequence,
        "predecessor_snapshot_ref_or_genesis": predecessor,
        "as_of": "2030-01-01T00:00:00.000000Z",
        "next_update": (
            "2030-01-01T00:00:10.000000Z"
            if case == "EXPIRED"
            else "2030-01-01T00:05:00.000000Z"
        ),
        "ordered_entries": entries,
        "trust_profile_ref": _record_ref(profile),
    }
    snapshot = _seal(
        trust.RevocationSnapshotV1,
        f"revocation-{case.lower()}",
        "revocation",
        values,
    )
    proofs = tuple(
        sorted(
            (
                _trust_proof(
                    snapshot,
                    profile,
                    f"ebu-i4-validation-revocation-root-{index}",
                    trust.RootRole.REVOCATION_ROOT,
                    trust.TrustEvidenceKind.REVOCATION_SNAPSHOT,
                )
                for index in (1, 2)
            ),
            key=lambda item: item.signer_key_id,
        )
    )
    if case == "THRESHOLD_ONE":
        proofs = proofs[:1]
    return snapshot, proofs


def _authenticity(
    stage: authorization.StageAuthorization,
    profile: trust.TrustProfileV1,
    credentials: tuple[trust.DelegationCredentialV1, ...],
    *,
    wrong: bool = False,
) -> trust.AuthorizationAuthenticityEnvelopeV1:
    if credentials:
        signer_label = next(
            label
            for label in _SEEDS
            if _key_material(label)[1] == credentials[0].delegate_key_id
        )
    else:
        signer_label = "ebu-i4-validation-issuer-1"
    _, signer_key_id, _ = _key_material(signer_label)
    values: dict[str, object] = {
        "signature_profile": (
            trust.SignatureProfile.EBU_AUTHORIZATION_ED25519_V1
        ),
        "stage_authorization_ref": _record_ref(stage),
        "trust_profile_ref": _record_ref(profile),
        "signer_issuer_id": stage.issuer_id,
        "signer_key_id": signer_key_id,
        "ordered_delegation_credential_refs": tuple(
            _record_ref(item) for item in credentials
        ),
        "signature_base64url": "AA",
        "proof_byte_hash": ArtifactByteHash.from_hex(
            hashlib.sha256(b"\x00").hexdigest()
        ),
        "signer_credential_evidence_refs": (),
    }
    provisional = _seal(
        trust.AuthorizationAuthenticityEnvelopeV1,
        "authenticity",
        "authenticity",
        values,
    )
    signature, proof_hash = _signature(
        _SEEDS[signer_label],
        authorization._authorization_signature_message(provisional),
    )
    if wrong:
        raw = bytearray(
            base64.urlsafe_b64decode(signature + "=" * ((-len(signature)) % 4))
        )
        raw[32] ^= 1
        signature = _b64(bytes(raw))
        proof_hash = ArtifactByteHash.from_hex(
            hashlib.sha256(bytes(raw)).hexdigest()
        )
    values["signature_base64url"] = signature
    values["proof_byte_hash"] = proof_hash
    return _seal(
        trust.AuthorizationAuthenticityEnvelopeV1,
        "authenticity",
        "authenticity",
        values,
    )


@dataclass
class _TimeService:
    case: str
    profile: trust.TrustProfileV1
    store: _StateStore
    calls: int = 0

    def request(
        self, challenge: trust.TrustedTimeChallengeV1, /
    ) -> trust.TrustedTimeAttestationV1:
        self.calls += 1
        if self.case == "SERVICE_MISSING":
            raise OSError("synthetic unavailable")
        return _time_material(
            self.case,
            self.profile,
            challenge.authorization_use_key,
            self.store,
        )[1]


@dataclass
class _RevocationService:
    case: str
    profile: trust.TrustProfileV1
    store: _StateStore
    revoked: tuple[trust.RevocableObjectKind, str] | None
    calls: int = 0

    def fetch_current(
        self, profile_ref: ObjectRef, /
    ) -> tuple[
        trust.RevocationSnapshotV1,
        tuple[trust.TrustEvidenceEnvelopeV1, ...],
    ]:
        self.calls += 1
        if self.case == "SERVICE_MISSING":
            raise OSError("synthetic unavailable")
        assert profile_ref == _record_ref(self.profile)
        return _revocation_material(
            self.case, self.profile, self.store, self.revoked
        )


@dataclass
class _OuterMaterial:
    bundle: authorization.AuthorizationEvidenceBundle
    requested_stage: str
    requested_operation: authorization.AuthorizedOperation
    requested_targets: tuple[ObjectRef, ...]
    time_service: _TimeService
    revocation_service: _RevocationService
    store: _StateStore


def _i3_positive(qualname: str) -> tuple[object, ...]:
    from tests.framework.test_i3d_declarations import _construct

    contract = _strict(
        ROOT / "unified_python_research_framework_i3_validation_contract.json"
    )
    row = next(
        item
        for item in contract["vectors"]
        if item["materialized_effective_input"]["interface"]["qualname"]
        == qualname
        and item["category"] == "VALIDATOR_POSITIVE"
    )
    return tuple(
        _construct(argument["value"])
        for argument in row["materialized_effective_input"][
            "ordered_arguments"
        ]
    )


def _binding_for_configuration(
    binding: ExecutionBinding, config: ExperimentConfiguration
) -> ExecutionBinding:
    values = {
        field.name: getattr(binding, field.name)
        for field in fields(binding)
        if field.name not in {"envelope", "execution_semantics_hash"}
    }
    values["accepted_configuration_ref"] = _record_ref(config)
    values["execution_semantics_hash"] = compute_execution_semantics_hash(
        accepted_configuration_ref=values["accepted_configuration_ref"],
        implementation_refs=values["implementation_refs"],
        source_refs=values["source_refs"],
        implementation_entrypoint_semantics=values[
            "entrypoint_semantics_ref"
        ].to_ecj1(),
        science_affecting_runtime_constraints=[
            item.to_ecj1() for item in values["runtime_constraint_refs"]
        ],
        science_affecting_operational_exclusions=[
            item.to_ecj1()
            for item in values["operational_exclusions"]
            if item.science_affecting
        ],
        policy_memory_transition_contracts_or_not_applicable=(
            [
                item.to_ecj1()
                for item in values["policy_memory_transition_contract_refs"]
            ]
            if values["policy_memory_transition_contract_refs"]
            else framework.Applicability.NOT_APPLICABLE.value
        ),
        fault_injection_delivery_contracts_or_not_applicable=(
            [item.to_ecj1() for item in values["fault_delivery_contract_refs"]]
            if values["fault_delivery_contract_refs"]
            else framework.Applicability.NOT_APPLICABLE.value
        ),
        event_order_contract=values["event_order_contract_ref"].to_ecj1(),
        arithmetic_and_numerical_policy_contracts=[
            item.to_ecj1()
            for item in values["numerical_policy_contract_refs"]
        ],
        information_capability_contract=values[
            "information_capability_contract_ref"
        ].to_ecj1(),
        canonical_scientific_trace_schema_ref=values["trace_schema_ref"],
        scientific_result_schema_ref=values["result_schema_ref"],
        stochastic_generator_and_stream_contract_or_not_applicable=(
            values["stochastic_contract_ref"].to_ecj1()
            if type(values["stochastic_contract_ref"]) is ObjectRef
            else framework.Applicability.NOT_APPLICABLE.value
        ),
    )
    return _seal(
        ExecutionBinding,
        "execution-binding",
        "execution-binding",
        values,
    )


def _outer_material(vector: dict[str, object]) -> _OuterMaterial:
    inputs = vector["effective_input"]
    profile_case = inputs["profile_case"]
    profile = _profile(profile_case)
    target = _ref("registry-object", "candidate", "4")
    other_target = _ref("registry-object", "other", "5")
    requested_targets = (target,)
    operation = authorization.AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
    requested_operation = operation
    stage = requested_stage = "I-4"
    scope_case = inputs["scope_case"]
    if scope_case == "STAGE_MISMATCH":
        stage = "I-3"
    elif scope_case == "OPERATION_MISMATCH":
        operation = authorization.AuthorizedOperation.PUBLISH_ARTIFACTS
    elif scope_case == "TARGET_MISMATCH":
        requested_targets = (other_target,)
    elif scope_case == "VALID_EXECUTE_BOUND_RUN":
        operation = requested_operation = (
            authorization.AuthorizedOperation.EXECUTE_BOUND_RUN
        )
        requested_targets = tuple(
            _ref("registry-object", f"execute-{index}", str(index))
            for index in range(1, 5)
        )
    revocation_placeholder = _ref("revocation", "synthetic", "3")
    include_delegate = inputs["delegation_case"] != "VALID_NONE"
    snapshot, issuer_proofs, store = _issuer_material(
        profile,
        inputs["issuer_case"],
        include_delegate=include_delegate,
    )
    if profile_case == "PRODUCTION_NO_BOOTSTRAP":
        store.pinned = framework.Applicability.NOT_APPLICABLE
    elif profile_case == "PIN_MISMATCH":
        store.pinned = _ref("trust-profile", "wrong-pin", "d")
    credentials, delegation_proofs, stage_authorization = (
        _delegation_material(
            inputs["delegation_case"],
            profile,
            snapshot,
            revocation_placeholder,
            requested_targets,
        )
    )
    auth_values = {
        field.name: getattr(stage_authorization, field.name)
        for field in fields(stage_authorization)
        if field.name != "envelope"
    }
    auth_values["stage"] = stage
    auth_values["authorized_operation"] = operation
    auth_values["target_object_refs"] = (
        (target,) if scope_case == "TARGET_MISMATCH" else requested_targets
    )
    auth_values["not_before"] = (
        "2030-01-01T00:00:11.000000Z"
        if scope_case == "NOT_YET_VALID"
        else "2029-12-31T00:00:00.000000Z"
    )
    auth_values["expires_at"] = (
        "2030-01-01T00:00:10.000000Z"
        if scope_case == "EXPIRED"
        else "2031-01-01T00:00:00.000000Z"
    )
    auth_values["exclusions"] = (
        (operation.value,) if scope_case == "EXCLUSION_MATCH" else ()
    )
    predecessor = _envelope(
        "predecessor", "registry-object", {"synthetic": True}
    )
    predecessor_ref = ObjectRef(
        object_id=predecessor.object_id,
        object_version=predecessor.object_version,
        object_content_hash=predecessor.object_content_hash,
    )
    predecessor_evidence: tuple[CommonObjectEnvelope, ...] = ()
    if inputs["predecessor_case"] == "MISMATCH":
        auth_values["predecessor_evidence_refs"] = (predecessor_ref,)
    config: ExperimentConfiguration | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    binding: ExecutionBinding | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    execution: ExecutionIdentity | framework.Applicability = (
        framework.Applicability.NOT_APPLICABLE
    )
    if scope_case == "CONFIGURATION_MISMATCH":
        auth_values["accepted_configuration_ref_or_not_applicable"] = _ref(
            "configuration", "missing", "6"
        )
    if scope_case == "BINDING_MISMATCH":
        auth_values[
            "accepted_execution_binding_ref_or_not_applicable"
        ] = _ref("binding", "missing", "7")
    if scope_case == "EXECUTION_IDENTITY_MISMATCH":
        execution = ExecutionIdentity(
            identity_ref=_ref("execution", "identity", "8"),
            execution_mode=ExecutionMode.DETERMINISTIC,
            configuration_ref=_ref("configuration", "identity", "9"),
            binding_ref=_ref("binding", "identity", "a"),
            attempt_ordinal=IntegerV1(1),
        )
        auth_values["execution_identity_or_not_applicable"] = execution
    if inputs["binding_case"] == "CONFIGURATION_MISMATCH":
        config = _i3_positive("validate_experiment_configuration")[0]
        binding = _i3_positive("validate_execution_binding")[0]
        auth_values["accepted_configuration_ref_or_not_applicable"] = (
            _record_ref(config)
        )
        auth_values[
            "accepted_execution_binding_ref_or_not_applicable"
        ] = _record_ref(binding)
    if scope_case == "VALID_EXECUTE_BOUND_RUN":
        config = _i3_positive("validate_experiment_configuration")[0]
        binding = _binding_for_configuration(
            _i3_positive("validate_execution_binding")[0], config
        )
        execution = ExecutionIdentity(
            identity_ref=_ref("execution", "identity", "8"),
            execution_mode=ExecutionMode.DETERMINISTIC,
            configuration_ref=_record_ref(config),
            binding_ref=_record_ref(binding),
            attempt_ordinal=IntegerV1(1),
        )
        auth_values["accepted_configuration_ref_or_not_applicable"] = (
            _record_ref(config)
        )
        auth_values[
            "accepted_execution_binding_ref_or_not_applicable"
        ] = _record_ref(binding)
        auth_values["execution_identity_or_not_applicable"] = execution
    stage_authorization = _seal(
        authorization.StageAuthorization,
        "stage-outer",
        "authorization",
        auth_values,
    )
    authenticity = _authenticity(
        stage_authorization,
        profile,
        credentials,
        wrong=inputs["key_case"] == "WRONG_SIGNATURE",
    )
    revocation_case = inputs["revocation_case"]
    revoked = None
    if revocation_case == "REVOKED_ISSUER":
        revoked = (
            trust.RevocableObjectKind.ISSUER,
            str(stage_authorization.issuer_id),
        )
    elif revocation_case == "REVOKED_KEY":
        revoked = (
            trust.RevocableObjectKind.KEY,
            authenticity.signer_key_id,
        )
    elif revocation_case == "REVOKED_DELEGATION":
        revoked = (
            trust.RevocableObjectKind.DELEGATION,
            str(credentials[0].credential_id),
        )
    elif revocation_case == "REVOKED_AUTHORIZATION":
        revoked = (
            trust.RevocableObjectKind.AUTHORIZATION,
            str(stage_authorization.envelope.object_id),
        )
    elif revocation_case == "TRUST_PROFILE_SUCCESSOR":
        revoked = (
            trust.RevocableObjectKind.TRUST_PROFILE_SUCCESSOR,
            str(profile.envelope.object_id),
        )
    time_service = _TimeService(inputs["time_case"], profile, store)
    revocation_service = _RevocationService(
        revocation_case, profile, store, revoked
    )
    lifecycle = (
        LifecycleStatus.SUPERSEDED
        if scope_case == "LIFECYCLE_MISMATCH"
        else LifecycleStatus.REVIEWED
    )
    bundle = authorization.AuthorizationEvidenceBundle(
        authorization=stage_authorization,
        authenticity_envelope=authenticity,
        trust_profile=profile,
        issuer_registry_snapshot=snapshot,
        issuer_root_proofs=issuer_proofs,
        delegation_credentials=credentials,
        delegation_proofs=delegation_proofs,
        predecessor_evidence=predecessor_evidence,
        accepted_configuration=config,
        accepted_binding=binding,
        execution_identity=execution,
        lifecycle_witnesses=tuple(
            (item, lifecycle) for item in requested_targets
        ),
        single_use_store_identity=(
            authorization_use.AuthorizationUseStoreIdentity(
                store_id=ScientificId(
                    "ebu:authorization-store:validation:outer"
                ),
                database_path="/private/tmp/authorization-use-v1.sqlite3",
                filesystem_kind=(
                    "unsupported"
                    if inputs["store_case"] == "UNSUPPORTED_FS"
                    else "macOS APFS local"
                ),
                schema_version=1,
                sqlite_version=sqlite3.sqlite_version,
                synthetic=True,
            )
        ),
    )
    return _OuterMaterial(
        bundle,
        requested_stage,
        requested_operation,
        requested_targets,
        time_service,
        revocation_service,
        store,
    )


@dataclass
class _InvocationCounts:
    constructor: int = 0
    verify: int = 0
    interface: int = 0


def _invoke_with_provider_count(
    callable_value: object,
) -> tuple[object | None, FrameworkError | None, _InvocationCounts]:
    import nacl.signing

    real_verify_key = nacl.signing.VerifyKey
    counts = _InvocationCounts()

    class CountingVerifyKey:
        def __init__(self, *args: object, **kwargs: object) -> None:
            counts.constructor += 1
            self._delegate = real_verify_key(*args, **kwargs)

        def verify(self, *args: object, **kwargs: object) -> bytes:
            counts.verify += 1
            return self._delegate.verify(*args, **kwargs)

    try:
        with patch("nacl.signing.VerifyKey", CountingVerifyKey):
            return callable_value(), None, counts
    except FrameworkError as error:
        return None, error, counts


def _frame(value: str) -> bytes:
    encoded = value.encode("utf-8", "strict")
    return len(encoded).to_bytes(8, "big") + encoded


def _independent_failure_id(envelope: object) -> str:
    parts = [
        _frame("ebu.failure-id.v1"),
        _frame(envelope.failure_code.value),
        _frame(envelope.stage.value),
    ]
    if envelope.interface_ref is framework.Applicability.NOT_APPLICABLE:
        parts.append(_frame("NOT_APPLICABLE"))
    else:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(envelope.interface_ref.module),
                _frame(envelope.interface_ref.qualname),
                _frame(envelope.interface_ref.interface_version),
            )
        )
    parts.append(len(envelope.object_refs).to_bytes(8, "big"))
    for reference in envelope.object_refs:
        parts.extend(
            (
                _frame(str(reference.object_id)),
                _frame(str(reference.object_version)),
                _frame(str(reference.object_content_hash)),
            )
        )
    if envelope.event_key is framework.Applicability.NOT_APPLICABLE:
        parts.append(_frame("NOT_APPLICABLE"))
    else:
        parts.append(_frame(str(envelope.event_key)))
    parts.append(_frame(str(envelope.failure_ordinal)))
    return "ebu:failure:core:sha256-" + hashlib.sha256(
        b"".join(parts)
    ).hexdigest()


_SECOND_PRECEDENCE = {
    "i4v-108": "SIGNATURE_INVALID",
    "i4v-109": "DELEGATION_CYCLE",
    "i4v-110": "TRUSTED_TIME_STALE",
    "i4v-111": "REVOCATION_ROLLBACK",
    "i4v-112": "AUTHORIZATION_TARGET_MISMATCH",
    "i4v-113": "AUTHORIZATION_PREDECESSOR_MISMATCH",
    "i4v-114": "BINDING_CONFIGURATION_MISMATCH",
    "i4v-115": "AUTHORIZATION_USE_STORE_UNSUPPORTED",
    "i4v-116": "INFORMATION_TOO_OLD",
    "i4v-117": "AUTHORIZATION_USE_UNRESOLVED",
}
_NOT_APPLICABLE_RETRY = {
    "TRUSTED_TIME_UNAVAILABLE",
    "TRUSTED_TIME_CHALLENGE_MISMATCH",
    "TRUSTED_TIME_STALE",
    "TRUSTED_TIME_SEQUENCE_INVALID",
    "REVOCATION_UNAVAILABLE",
    "REVOCATION_SNAPSHOT_EXPIRED",
    "AUTHORIZATION_USE_UNRESOLVED",
    "AUTHORIZATION_USE_STORE_UNSUPPORTED",
    "AUTHORIZATION_USE_LEDGER_FAILURE",
}
_UNRESOLVED_DURABILITY = {
    "TRUSTED_TIME_SEQUENCE_INVALID",
    "REVOCATION_ROLLBACK",
    "REVOCATION_GAP",
    "REVOCATION_EQUIVOCATION",
    "AUTHORIZATION_USE_UNRESOLVED",
    "AUTHORIZATION_USE_LEDGER_FAILURE",
}


def _independent_predicates(
    vector: dict[str, object], first_failure: str
) -> tuple[str, ...]:
    second = _SECOND_PRECEDENCE.get(vector["vector_id"])
    return (first_failure,) if second is None else (first_failure, second)


def _assert_failure(
    test: unittest.TestCase,
    vector: dict[str, object],
    failure: FrameworkError | object,
) -> None:
    expected = vector["expected"]
    envelope = failure.envelope if type(failure) is FrameworkError else failure
    test.assertEqual(envelope.failure_code.value, expected["failure_code"])
    test.assertEqual(envelope.failure_ordinal, expected["failure_ordinal"])
    test.assertEqual(str(envelope.failure_id), expected["failure_id"])
    test.assertEqual(
        str(envelope.failure_id), _independent_failure_id(envelope)
    )
    test.assertEqual(
        envelope.interface_ref.module + "." + envelope.interface_ref.qualname,
        "ebu_framework." + vector["interface"],
    )
    test.assertEqual(
        tuple(expected["predicate_truth_set"]),
        _independent_predicates(vector, envelope.failure_code.value),
    )
    code = envelope.failure_code.value
    test.assertEqual(envelope.to_ecj1()["schema_id"], "ebu.failure-envelope/1")
    test.assertEqual(envelope.stage.value, "I-4")
    test.assertEqual(envelope.interface_ref.interface_version, "1.0.0")
    test.assertEqual(envelope.object_refs, ())
    test.assertIs(envelope.event_key, framework.Applicability.NOT_APPLICABLE)
    test.assertEqual(envelope.state_advance.value, "NONE")
    test.assertEqual(envelope.policy_memory_advance.value, "NONE")
    trace = envelope.canonical_trace_state
    test.assertIs(trace.applicability, framework.Applicability.NOT_APPLICABLE)
    test.assertIs(trace.completeness, framework.Applicability.NOT_APPLICABLE)
    test.assertIs(trace.confirmed_row_count, framework.Applicability.NOT_APPLICABLE)
    test.assertIs(trace.durable_prefix_ref, framework.Applicability.NOT_APPLICABLE)
    test.assertEqual(
        envelope.scientific_status_effect.value, "UNSTARTED_PRESERVED"
    )
    expected_retry = (
        "REQUIRES_AUTHORITY"
        if code == "PRODUCTION_BOOTSTRAP_MISSING"
        else "NOT_APPLICABLE"
        if code in _NOT_APPLICABLE_RETRY
        else "FORBIDDEN"
    )
    test.assertEqual(envelope.retry_class.value, expected_retry)
    expected_durability = (
        "UNRESOLVED"
        if code in _UNRESOLVED_DURABILITY
        else "NONE_DURABLE"
        if code == "AUTHORIZATION_USE_ALREADY_CONSUMED"
        else "NOT_APPLICABLE"
    )
    test.assertEqual(envelope.durability_state.value, expected_durability)
    test.assertEqual(envelope.evidence_refs, ())
    expected_summary = (
        f"{envelope.interface_ref.qualname} rejected {code}"
        if code == "I4_RECORD_FORMATION_INVALID"
        else f"{envelope.interface_ref.qualname} rejected {code} at {vector['name']}"
    )
    test.assertEqual(envelope.human_summary, expected_summary)


def _assert_counts(
    test: unittest.TestCase,
    vector: dict[str, object],
    counts: _InvocationCounts,
) -> None:
    expected = vector["expected"]
    test.assertEqual(
        counts.constructor,
        expected["provider_calls"]["verify_key_constructor"],
    )
    test.assertEqual(counts.verify, expected["provider_calls"]["verify"])
    test.assertEqual(expected["model_step_count"], 0)
    test.assertEqual(counts.interface, 1)


_INNER_CHECK_COUNT = {
    "validate_issuer_registry_snapshot": {
        FailureCode.ROOT_THRESHOLD_NOT_MET: 1,
        FailureCode.ROOT_PROOF_ORDER_INVALID: 1,
        FailureCode.ISSUER_REGISTRY_ROLLBACK: 4,
        FailureCode.ISSUER_REGISTRY_GAP: 4,
        FailureCode.ISSUER_REGISTRY_EQUIVOCATION: 4,
        FailureCode.KEY_ID_MISMATCH: 6,
    },
    "validate_delegation_chain": {
        FailureCode.DELEGATION_CHAIN_INVALID: 3,
        FailureCode.DELEGATION_CYCLE: 4,
        FailureCode.DELEGATION_SCOPE_ESCALATION: 7,
        FailureCode.DELEGATION_DEPTH_EXCEEDED: 8,
    },
    "validate_trusted_time_attestation": {
        FailureCode.TRUSTED_TIME_CHALLENGE_MISMATCH: 1,
        FailureCode.ISSUER_KEY_INVALID: 2,
        FailureCode.TRUSTED_TIME_STALE: 3,
        FailureCode.TRUSTED_TIME_SEQUENCE_INVALID: 4,
    },
    "validate_revocation_snapshot": {
        FailureCode.ROOT_THRESHOLD_NOT_MET: 1,
        FailureCode.REVOCATION_SNAPSHOT_EXPIRED: 2,
        FailureCode.REVOCATION_ROLLBACK: 3,
        FailureCode.REVOCATION_GAP: 3,
        FailureCode.REVOCATION_EQUIVOCATION: 3,
    },
}


def _invoke_inner(
    vector: dict[str, object],
) -> tuple[object | None, FrameworkError | None, _InvocationCounts, _StateStore]:
    inputs = vector["effective_input"]
    profile = _profile(inputs["profile_case"])
    snapshot, proofs, store = _issuer_material(
        profile,
        inputs["issuer_case"],
        include_delegate=inputs["delegation_case"] != "VALID_NONE",
    )
    target = (_ref("registry-object", "candidate", "4"),)
    revocation, revocation_proofs = _revocation_material(
        inputs["revocation_case"], profile, store
    )
    credentials, delegation_proofs, stage = _delegation_material(
        inputs["delegation_case"],
        profile,
        snapshot,
        _record_ref(revocation),
        target,
    )
    use_key = framework.compute_authorization_use_key(
        stage_authorization_ref=_record_ref(stage),
        requested_operation=stage.authorized_operation.value,
        target_object_refs=stage.target_object_refs,
        accepted_configuration_ref_or_not_applicable=(
            stage.accepted_configuration_ref_or_not_applicable
        ),
        accepted_execution_binding_ref_or_not_applicable=(
            stage.accepted_execution_binding_ref_or_not_applicable
        ),
        execution_identity_or_not_applicable=(
            stage.execution_identity_or_not_applicable
        ),
    )
    challenge, attestation = _time_material(
        inputs["time_case"], profile, use_key, store
    )
    interface = vector["interface"]
    if interface == "trust.validate_issuer_registry_snapshot":
        call = lambda: trust.validate_issuer_registry_snapshot(
            snapshot, proofs, profile, store
        )
    elif interface == "trust.validate_delegation_chain":
        call = lambda: trust.validate_delegation_chain(
            credentials,
            delegation_proofs,
            snapshot,
            profile,
            stage,
            _ATTESTED,
            revocation,
        )
    elif interface == "trust.validate_trusted_time_attestation":
        call = lambda: trust.validate_trusted_time_attestation(
            challenge, attestation, profile, store
        )
    elif interface == "trust.validate_revocation_snapshot":
        call = lambda: trust.validate_revocation_snapshot(
            revocation, revocation_proofs, profile, _ATTESTED, store
        )
    else:
        raise AssertionError(interface)
    owner_name = interface.split(".")[-1]
    real_owner = getattr(trust, owner_name)
    with patch.object(
        trust, owner_name, wraps=real_owner
    ) as owner, framework.errors._i4_validation_context(
        vector["expected"]["failure_ordinal"], vector["name"]
    ):
        result, error, counts = _invoke_with_provider_count(call)
    counts.interface = owner.call_count
    return result, error, counts, store


def _invoke_outer(
    vector: dict[str, object],
) -> tuple[
    authorization.AuthorizationValidationRecord,
    _InvocationCounts,
    _OuterMaterial,
]:
    material = _outer_material(vector)
    call = lambda: authorization.validate_stage_authorization(
        material.bundle,
        material.requested_stage,
        material.requested_operation,
        material.requested_targets,
        material.time_service,
        material.revocation_service,
        material.store,
    )
    real_owner = authorization.validate_stage_authorization
    with patch.object(
        authorization, "validate_stage_authorization", wraps=real_owner
    ) as owner, framework.errors._i4_validation_context(
        vector["expected"]["failure_ordinal"], vector["name"]
    ):
        result, error, counts = _invoke_with_provider_count(call)
    counts.interface = owner.call_count
    assert error is None
    assert type(result) is authorization.AuthorizationValidationRecord
    return result, counts, material


class FrameworkI4TrustTests(unittest.TestCase):
    def test_i4v_021_through_i4v_063_trust(self) -> None:
        document, vectors = _fixture()
        selected = vectors[20:63]
        self.assertEqual(document["vectors"], _VALIDATION["vectors"])
        self.assertEqual(
            tuple(vector["vector_id"] for vector in selected),
            tuple(f"i4v-{index:03d}" for index in range(21, 64)),
        )
        mechanical = _strict(MECHANICAL)
        self.assertEqual(
            tuple(trust.__all__), tuple(mechanical["module_exports"]["trust"])
        )
        success_counts = {
            "trust.validate_issuer_registry_snapshot": 7,
            "trust.validate_delegation_chain": 9,
            "trust.validate_trusted_time_attestation": 5,
            "trust.validate_revocation_snapshot": 4,
        }
        for vector in selected:
            with self.subTest(vector_id=vector["vector_id"]):
                if vector["interface"] == (
                    "authorization.validate_stage_authorization"
                ):
                    record, counts, material = _invoke_outer(vector)
                    self.assertEqual(
                        len(record.completed_checks),
                        vector["expected"]["completed_check_count"],
                    )
                    self.assertEqual(
                        material.time_service.calls,
                        vector["expected"]["service_calls"]["trusted_time"],
                    )
                    self.assertEqual(
                        material.revocation_service.calls,
                        vector["expected"]["service_calls"]["revocation"],
                    )
                    self.assertIs(
                        record.status,
                        authorization.AuthorizationValidationStatus.REJECTED,
                    )
                    _assert_failure(self, vector, record.failure)
                else:
                    result, error, counts, store = _invoke_inner(vector)
                    if vector["expected"]["outcome"] == "SUCCESS":
                        self.assertIsNone(error)
                        actual_checks = success_counts[vector["interface"]]
                        if type(result) is tuple:
                            self.assertEqual(len(result), actual_checks)
                    else:
                        assert error is not None
                        _assert_failure(self, vector, error)
                        actual_checks = _INNER_CHECK_COUNT[
                            vector["interface"].split(".")[-1]
                        ][error.envelope.failure_code]
                    self.assertEqual(
                        actual_checks,
                        vector["expected"]["completed_check_count"],
                    )
                    self.assertEqual(
                        vector["expected"]["service_calls"],
                        {"trusted_time": 0, "revocation": 0},
                    )
                    self.assertLessEqual(len(store.persisted or []), 1)
                _assert_counts(self, vector, counts)


class FrameworkI4AuthorizationTests(unittest.TestCase):
    def test_i4v_064_through_i4v_078_scope(self) -> None:
        _, vectors = _fixture()
        selected = vectors[63:78]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in selected),
            tuple(f"i4v-{index:03d}" for index in range(64, 79)),
        )
        invoked_count = 0
        real_outer = authorization.validate_stage_authorization
        for vector in selected:
            with self.subTest(vector_id=vector["vector_id"]):
                if vector["vector_id"] == "i4v-077":
                    profile = _profile()
                    target = (_ref("registry-object", "candidate", "4"),)
                    with patch.object(
                        authorization,
                        "validate_stage_authorization",
                        wraps=real_outer,
                    ) as not_invoked, framework.errors._i4_validation_context(
                        77, vector["name"]
                    ), self.assertRaises(FrameworkError) as raised:
                        _stage_authorization(
                            profile,
                            _ref("revocation", "synthetic", "3"),
                            ScientificId("ebu:issuer:validation:issuer-1"),
                            target,
                            operation=(
                                authorization.AuthorizedOperation.ACCEPT_REGISTRY_OBJECT,
                                authorization.AuthorizedOperation.PUBLISH_ARTIFACTS,
                            ),
                        )
                    self.assertEqual(not_invoked.call_count, 0)
                    _assert_failure(self, vector, raised.exception)
                    self.assertEqual(
                        vector["expected"]["completed_check_count"], 1
                    )
                    continue
                with patch.object(
                    authorization,
                    "validate_stage_authorization",
                    wraps=real_outer,
                ) as invoked:
                    record, counts, material = _invoke_outer(vector)
                invoked_count += invoked.call_count
                self.assertEqual(invoked.call_count, 1)
                self.assertEqual(
                    len(record.completed_checks),
                    vector["expected"]["completed_check_count"],
                )
                self.assertEqual(
                    material.time_service.calls,
                    vector["expected"]["service_calls"]["trusted_time"],
                )
                self.assertEqual(
                    material.revocation_service.calls,
                    vector["expected"]["service_calls"]["revocation"],
                )
                if vector["expected"]["outcome"] == "SUCCESS":
                    self.assertIs(
                        record.status,
                        authorization.AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED,
                    )
                else:
                    self.assertIs(
                        record.status,
                        authorization.AuthorizationValidationStatus.REJECTED,
                    )
                    _assert_failure(self, vector, record.failure)
                _assert_counts(self, vector, counts)
        self.assertEqual(invoked_count, 14)


class FrameworkI4PrecedenceTests(unittest.TestCase):
    def test_i4v_108_through_i4v_117_precedence(self) -> None:
        _, vectors = _fixture()
        selected = vectors[107:117]
        self.assertEqual(len(selected), 10)
        for vector in selected:
            with self.subTest(vector_id=vector["vector_id"]):
                truths = vector["expected"]["predicate_truth_set"]
                self.assertGreaterEqual(len(truths), 2)
                self.assertEqual(vector["expected"]["failure_code"], truths[0])
                if vector["interface"] == (
                    "authorization.validate_stage_authorization"
                ):
                    record, counts, material = _invoke_outer(vector)
                    _assert_failure(self, vector, record.failure)
                    self.assertEqual(
                        len(record.completed_checks),
                        vector["expected"]["completed_check_count"],
                    )
                    self.assertEqual(
                        material.time_service.calls,
                        vector["expected"]["service_calls"]["trusted_time"],
                    )
                    self.assertEqual(
                        material.revocation_service.calls,
                        vector["expected"]["service_calls"]["revocation"],
                    )
                    _assert_counts(self, vector, counts)
                elif vector["interface"].startswith("capabilities."):
                    from tests.framework.test_capabilities import (
                        _invoke_information_vector,
                    )

                    _invoke_information_vector(self, vector)
                else:
                    from tests.framework.test_authorization_use import (
                        _invoke_consume_vector,
                    )

                    _invoke_consume_vector(self, vector)


if __name__ == "__main__":
    unittest.main()
