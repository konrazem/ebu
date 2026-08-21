"""Synthetic-only local single-use and protected-transition checks for I-4."""

from __future__ import annotations

from dataclasses import fields, replace
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
from ebu_framework.canonical import encode_ecj1
from ebu_framework.envelopes import LifecycleStatus, SupersessionRelation
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.identity import ObjectContentHash, ObjectRef, ScientificId, SemanticVersion
from ebu_framework.ledger import Ledger, LedgerEntry, LedgerKind
from ebu_framework.numeric import IntegerV1
from ebu_framework.registry import RegistryRecord, _with_lifecycle_status


FIXTURE = Path(__file__).with_name("fixtures") / "authorization_vectors_v1.json"


def _vectors() -> list[dict[str, object]]:
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return document["vectors"]


def _ref(kind: str, label: str, fill: str) -> ObjectRef:
    return ObjectRef(
        object_id=ScientificId(f"ebu:{kind}:validation:{label}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash("sha256:" + fill * 64),
    )


def _validated_record(
    targets: tuple[ObjectRef, ...],
    operation: authorization.AuthorizedOperation = (
        authorization.AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
    ),
    authorization_ref: ObjectRef | None = None,
) -> authorization.AuthorizationValidationRecord:
    if authorization_ref is None:
        authorization_ref = _ref("authorization", "consume", "1")
    trust_ref = _ref("trust-profile", "synthetic", "2")
    revocation_ref = _ref("revocation", "synthetic", "3")
    key = framework.compute_authorization_use_key(
        stage_authorization_ref=authorization_ref,
        requested_operation=operation.value,
        target_object_refs=targets,
        accepted_configuration_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        accepted_execution_binding_ref_or_not_applicable=Applicability.NOT_APPLICABLE,
        execution_identity_or_not_applicable=Applicability.NOT_APPLICABLE,
    )
    checks = tuple(
        authorization.AuthorizationCheckRecord(
            check_ordinal=index,
            check_name=f"validated-check-{index:02d}",
            status=authorization.AuthorizationCheckStatus.PASS,
            failure_code_or_not_applicable=Applicability.NOT_APPLICABLE,
            evidence_refs=(),
        )
        for index in range(1, 68)
    )
    attestation = trust.TrustedTimeAttestationV1(
        trust_profile_ref=trust_ref,
        time_service_id=ScientificId("ebu:time-service:validation:synthetic"),
        signer_key_id="ed25519:" + "4" * 64,
        challenge_base64url="AA",
        authorization_use_key=key,
        attested_utc="2030-01-01T00:00:10.000000Z",
        service_sequence=1,
        issued_at="2030-01-01T00:00:09.000000Z",
        expires_at="2030-01-01T00:00:20.000000Z",
        signature_base64url="AA",
    )
    return authorization.AuthorizationValidationRecord(
        authorization_ref=authorization_ref,
        authorization_use_key=key,
        status=authorization.AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED,
        completed_checks=checks,
        effective_issuer_id=ScientificId("ebu:issuer:validation:synthetic"),
        effective_stages=("I-4",),
        effective_operations=(operation.value,),
        effective_target_object_refs=targets,
        trusted_time_attestation=attestation,
        revocation_snapshot_ref=revocation_ref,
        failure=Applicability.NOT_APPLICABLE,
    )


def _store(directory: Path, case: str) -> authorization_use.AuthorizationUseStoreIdentity:
    return authorization_use.AuthorizationUseStoreIdentity(
        store_id=ScientificId(f"ebu:authorization-store:validation:{case.lower().replace('_', '-') }"),
        database_path=str(directory / "authorization-use-v1.sqlite3"),
        filesystem_kind=(
            "unsupported synthetic filesystem"
            if case in {"UNSUPPORTED_FS", "UNSUPPORTED_FS_AND_LOCKED"}
            else "macOS APFS local"
        ),
        schema_version=1,
        sqlite_version=(
            "3.45.0" if case == "VERSION_UNSUPPORTED" else sqlite3.sqlite_version
        ),
        synthetic=True,
    )


class _ConnectionProxy:
    def __init__(
        self,
        delegate: sqlite3.Connection,
        case: str,
        counters: dict[str, int],
    ) -> None:
        self._delegate = delegate
        self._case = case
        self._counters = counters

    def execute(self, statement: str, parameters: object = ()) -> object:
        if statement == "BEGIN IMMEDIATE":
            self._counters["begin"] += 1
        if self._case == "IO_FAILURE" and statement.startswith(
            "INSERT INTO authorization_use"
        ):
            raise OSError("synthetic I/O failure")
        if self._case == "LEDGER_FAILURE" and statement.startswith(
            "INSERT INTO operational_ledger"
        ):
            raise sqlite3.IntegrityError("synthetic ledger failure")
        if self._case == "AMBIGUOUS_MISSING" and statement == "COMMIT":
            raise sqlite3.OperationalError("synthetic ambiguous commit")
        return self._delegate.execute(statement, parameters)

    def close(self) -> None:
        if (
            self._case == "AMBIGUOUS_EXACT"
            and not self._counters.get("ambiguous_close_raised", 0)
        ):
            self._counters["ambiguous_close_raised"] = 1
            raise OSError("synthetic post-commit close failure")
        self._delegate.close()

    def __getattr__(self, name: str) -> object:
        return getattr(self._delegate, name)


def _assert_use_failure(
    test: unittest.TestCase,
    vector: dict[str, object],
    error: FrameworkError,
) -> None:
    expected = vector["expected"]
    envelope = error.envelope
    test.assertEqual(envelope.failure_code.value, expected["failure_code"])
    test.assertEqual(envelope.failure_ordinal, expected["failure_ordinal"])
    test.assertEqual(str(envelope.failure_id), expected["failure_id"])
    from tests.framework.test_authorization import _assert_failure

    _assert_failure(test, vector, error)


def _invoke_consume_vector(
    test: unittest.TestCase, vector: dict[str, object]
) -> authorization_use.AuthorizationUseRecord | None:
    case = vector["effective_input"]["store_case"]
    expected = vector["expected"]
    target = _ref("registry-object", "candidate", "5")
    validation = _validated_record((target,))
    counters = {"begin": 0}
    result = None
    error = None
    with tempfile.TemporaryDirectory(
        prefix=f"ebu-i4-{vector['vector_id']}-", dir="/private/tmp"
    ) as temporary:
        directory = Path(temporary).resolve(strict=True)
        store = _store(directory, case)
        if case in {"DUPLICATE", "PERMANENT_AFTER_EXPIRY"}:
            authorization_use.consume_stage_authorization(validation, store)
        elif case == "SCHEMA_MISMATCH":
            Path(store.database_path).touch()
        elif case not in {"UNSUPPORTED_FS", "VERSION_UNSUPPORTED"}:
            authorization_use._initialize_synthetic_store(
                Path(store.database_path), store, validation
            )
        lock_connection = None
        if case in {"LOCKED", "UNSUPPORTED_FS_AND_LOCKED"}:
            lock_connection = sqlite3.connect(
                store.database_path, timeout=0.0, isolation_level=None
            )
            lock_connection.execute("PRAGMA busy_timeout=0")
            lock_connection.execute("BEGIN IMMEDIATE")
        real_connect = authorization_use._connect

        def instrumented_connect(path: Path, *, query_only: bool) -> _ConnectionProxy:
            return _ConnectionProxy(
                real_connect(path, query_only=query_only), case, counters
            )

        real_owner = authorization_use.consume_stage_authorization
        try:
            with patch.object(
                authorization_use,
                "consume_stage_authorization",
                wraps=real_owner,
            ) as owner, patch.object(
                authorization_use, "_connect", instrumented_connect
            ), framework.errors._i4_validation_context(
                expected["failure_ordinal"], vector["name"]
            ):
                try:
                    result = authorization_use.consume_stage_authorization(
                        validation, store
                    )
                except FrameworkError as caught:
                    error = caught
        finally:
            if lock_connection is not None:
                lock_connection.execute("ROLLBACK")
                lock_connection.close()
        test.assertEqual(owner.call_count, 1)
        if expected["outcome"] == "SUCCESS":
            test.assertIsNone(error)
            test.assertIs(
                result.status, authorization_use.AuthorizationUseStatus.CONSUMED
            )
            actual_checks = 8
        else:
            assert error is not None
            _assert_use_failure(test, vector, error)
            actual_checks = {
                "DUPLICATE": 5,
                "LOCKED": 4,
                "UNSUPPORTED_FS": 2,
                "UNSUPPORTED_FS_AND_LOCKED": 2,
                "IO_FAILURE": 5,
                "AMBIGUOUS_MISSING": 8,
                "SCHEMA_MISMATCH": 3,
                "VERSION_UNSUPPORTED": 3,
                "LEDGER_FAILURE": 6,
                "PERMANENT_AFTER_EXPIRY": 5,
            }[case]
        test.assertEqual(actual_checks, expected["completed_check_count"])
        test.assertEqual(counters["begin"], expected["sqlite_begin_count"])
        test.assertEqual(expected["protected_mutation_count"], 0)
        test.assertEqual(expected["model_step_count"], 0)
        test.assertEqual(
            expected["provider_calls"],
            {"verify_key_constructor": 0, "verify": 0},
        )
        test.assertEqual(
            expected["service_calls"],
            {"trusted_time": 0, "revocation": 0},
        )
        if case in {
            "VALID",
            "DUPLICATE",
            "LOCKED",
            "IO_FAILURE",
            "AMBIGUOUS_EXACT",
            "AMBIGUOUS_MISSING",
            "LEDGER_FAILURE",
            "PERMANENT_AFTER_EXPIRY",
        }:
            inspection = sqlite3.connect(store.database_path)
            try:
                use_rows = inspection.execute(
                    "SELECT COUNT(*) FROM authorization_use"
                ).fetchone()[0]
                ledger_rows = inspection.execute(
                    "SELECT COUNT(*) FROM operational_ledger"
                ).fetchone()[0]
            finally:
                inspection.close()
            expected_rows = (
                1
                if case
                in {
                    "VALID",
                    "DUPLICATE",
                    "AMBIGUOUS_EXACT",
                    "PERMANENT_AFTER_EXPIRY",
                }
                else 0
            )
            test.assertEqual((use_rows, ledger_rows), (expected_rows,) * 2)
    return result


def _draft(reference: ObjectRef, label: str) -> RegistryRecord:
    return RegistryRecord(
        object_ref=reference,
        object_kind="synthetic-registry-object",
        canonical_value=bytes(encode_ecj1({"label": label})),
        lifecycle_status=LifecycleStatus.DRAFT,
    )


def _transition_material(
    vector: dict[str, object], directory: Path
) -> tuple[
    object,
    tuple[object, ...],
    authorization.AuthorizationValidationRecord,
    authorization_use.AuthorizationUseRecord,
    authorization_use.AuthorizationUseStoreIdentity,
]:
    from tests.framework.test_authorization import (
        _i3_positive,
        _record_ref,
        _seal,
    )

    interface = vector["interface"].split(".")[-1]
    if interface == "accept_registry_object":
        target = _ref("registry-object", "candidate", "5")
        candidate = _draft(target, "candidate")
        if vector["effective_input"]["scope_case"] == "MUTATION_CONFLICT":
            candidate = _with_lifecycle_status(
                candidate, LifecycleStatus.ACCEPTED
            )
        operation = authorization.AuthorizedOperation.ACCEPT_REGISTRY_OBJECT
        targets = (target,)
        arguments: tuple[object, ...] = (candidate,)
    elif interface == "supersede_registry_object":
        logical_id = ScientificId("ebu:registry-object:validation:superseded")
        predecessor_ref = ObjectRef(
            object_id=logical_id,
            object_version=SemanticVersion("1.0.0"),
            object_content_hash=ObjectContentHash("sha256:" + "1" * 64),
        )
        successor_ref = ObjectRef(
            object_id=logical_id,
            object_version=SemanticVersion("2.0.0"),
            object_content_hash=ObjectContentHash("sha256:" + "2" * 64),
        )
        authorization_ref = _ref("authorization", "supersession", "3")
        predecessor = _with_lifecycle_status(
            _draft(predecessor_ref, "predecessor"), LifecycleStatus.ACCEPTED
        )
        successor = _draft(successor_ref, "successor")
        relation = SupersessionRelation(
            predecessor_ref=predecessor_ref,
            successor_ref=successor_ref,
            predecessor_object_kind_id=ScientificId(
                "ebu:kind:validation:registry-object"
            ),
            successor_object_kind_id=ScientificId(
                "ebu:kind:validation:registry-object"
            ),
            predecessor_schema_id=ScientificId(
                "ebu:schema:validation:registry-object-v1"
            ),
            successor_schema_id=ScientificId(
                "ebu:schema:validation:registry-object-v1"
            ),
            predecessor_status=LifecycleStatus.ACCEPTED,
            successor_status=LifecycleStatus.REVIEWED,
            predecessor_supersedes_chain=(predecessor_ref,),
            relation_evidence_refs=(
                _ref("evidence", "supersession", "4"),
            ),
            authorization_ref=authorization_ref,
        )
        operation = authorization.AuthorizedOperation.SUPERSEDE_REGISTRY_OBJECT
        targets = (predecessor_ref, successor_ref, authorization_ref)
        arguments = (predecessor, successor, relation)
    elif interface == "accept_experiment_configuration":
        configuration, fault_schedule = _i3_positive(
            "validate_experiment_configuration"
        )
        operation = (
            authorization.AuthorizedOperation.ACCEPT_EXPERIMENT_CONFIGURATION
        )
        targets = (_record_ref(configuration),)
        arguments = (configuration, fault_schedule)
    elif interface == "accept_execution_binding":
        binding = _i3_positive("validate_execution_binding")[0]
        accepted_configuration = _with_lifecycle_status(
            _draft(binding.accepted_configuration_ref, "configuration"),
            LifecycleStatus.ACCEPTED,
        )
        operation = authorization.AuthorizedOperation.ACCEPT_EXECUTION_BINDING
        targets = (
            accepted_configuration.object_ref,
            _record_ref(binding),
        )
        arguments = (binding, accepted_configuration)
    elif interface == "append_operational_ledger_entry":
        ledger = entry = None
        for index in range(100):
            ledger_id = ScientificId(
                f"ebu:ledger:validation:operational-{index}"
            )
            candidate_entry = _seal(
                LedgerEntry,
                f"entry-{index}",
                "ledger-entry",
                {
                    "ledger_id": ledger_id,
                    "predecessor_entry_ref": Applicability.NOT_APPLICABLE,
                    "entry_ordinal": IntegerV1(0),
                    "payload_ref": _ref("payload", "ledger", "6"),
                    "evidence_refs": (),
                },
            )
            candidate_entry_ref = _record_ref(candidate_entry)
            candidate_ledger = _seal(
                Ledger,
                f"operational-{index}",
                "ledger",
                {
                    "ledger_kind": LedgerKind.OPERATIONAL,
                    "entry_refs": (candidate_entry_ref,),
                    "head_entry_ref": candidate_entry_ref,
                },
            )
            if authorization_use._ref_key(
                _record_ref(candidate_ledger)
            ) < authorization_use._ref_key(candidate_entry_ref):
                ledger, entry = candidate_ledger, candidate_entry
                break
        assert ledger is not None and entry is not None
        entry_ref = _record_ref(entry)
        operation = (
            authorization.AuthorizedOperation.APPEND_OPERATIONAL_LEDGER_ENTRY
        )
        targets = (_record_ref(ledger), entry_ref)
        arguments = (ledger, entry)
    else:
        raise AssertionError(interface)
    validation = _validated_record(
        targets,
        operation,
        relation.authorization_ref
        if interface == "supersede_registry_object"
        else None,
    )
    store = _store(directory, "VALID_CONSUMED_ROW")
    use_record = authorization_use.consume_stage_authorization(
        validation, store
    )
    return (
        getattr(authorization_use, interface),
        arguments,
        validation,
        use_record,
        store,
    )


def _invoke_transition_vector(
    test: unittest.TestCase, vector: dict[str, object]
) -> None:
    expected = vector["expected"]
    interface = vector["interface"].split(".")[-1]
    with tempfile.TemporaryDirectory(
        prefix=f"ebu-i4-{vector['vector_id']}-", dir="/private/tmp"
    ) as temporary:
        directory = Path(temporary).resolve(strict=True)
        callable_value, arguments, validation, use_record, store = (
            _transition_material(vector, directory)
        )
        original_arguments = arguments
        error = None
        result = None
        with patch.object(
            authorization_use, interface, wraps=callable_value
        ) as invoked, framework.errors._i4_validation_context(
            expected["failure_ordinal"], vector["name"]
        ):
            try:
                result = getattr(authorization_use, interface)(
                    *arguments, validation, use_record, store
                )
            except FrameworkError as caught:
                error = caught
        test.assertEqual(invoked.call_count, 1)
        if expected["outcome"] == "SUCCESS":
            test.assertIsNone(error)
            test.assertIsNotNone(result)
        else:
            assert error is not None
            _assert_use_failure(test, vector, error)
            test.assertEqual(arguments, original_arguments)
        test.assertEqual(expected["completed_check_count"], 8)
        test.assertEqual(expected["sqlite_begin_count"], 0)
        test.assertEqual(expected["protected_mutation_count"], 1)
        test.assertEqual(expected["model_step_count"], 0)


class FrameworkI4AuthorizationUseTests(unittest.TestCase):
    def test_i4v_079_through_i4v_095_use_and_transitions(self) -> None:
        vectors = _vectors()[78:95]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors),
            tuple(f"i4v-{index:03d}" for index in range(79, 96)),
        )
        for vector in vectors:
            with self.subTest(vector_id=vector["vector_id"]):
                if vector["interface"].endswith(
                    "consume_stage_authorization"
                ):
                    _invoke_consume_vector(self, vector)
                else:
                    _invoke_transition_vector(self, vector)
        self.assertEqual(
            sum(v["expected"]["sqlite_begin_count"] for v in vectors), 8
        )
        self.assertEqual(
            sum(v["expected"]["protected_mutation_count"] for v in vectors),
            6,
        )


if __name__ == "__main__":
    unittest.main()
