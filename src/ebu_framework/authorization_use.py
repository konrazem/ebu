"""Qualified local SQLite authorization consumption and protected I-4 hooks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import hashlib
import os
from pathlib import Path
import sqlite3
from typing import NoReturn

from . import authorization as _authorization
from .ledger import Ledger, LedgerEntry, LedgerKind, _validate_operational_append
from .registry import RegistryRecord, _with_lifecycle_status
from .experiment import (
    ExperimentConfiguration,
    ExecutionBinding,
    ExecutionIdentity,
    FaultScheduleV1,
    _validate_binding_acceptance,
    _validate_configuration_acceptance,
)
from .identity import AuthorizationUseKey, ObjectRef, ScientificId
from .hashing import compute_authorization_use_key, compute_object_content_hash
from .envelopes import (
    CommonObjectEnvelope,
    LifecycleStatus,
    SupersessionRelation,
    validate_supersession_relation,
)
from .errors import Applicability, FailureCode, FrameworkError, _i4_fail


AuthorizedOperation = _authorization.AuthorizedOperation
AuthorizationValidationRecord = _authorization.AuthorizationValidationRecord
AuthorizationValidationStatus = _authorization.AuthorizationValidationStatus

_APPLICATION_ID = 1161970993
_SCHEMA_VERSION = 1
_DATABASE_FILENAME = "authorization-use-v1.sqlite3"
_SUPPORTED_FILESYSTEMS = frozenset(
    {
        "macOS APFS local",
        "Linux ext4 local",
        "Linux XFS local",
        "Windows NTFS local",
    }
)
_DDL = (
    "PRAGMA application_id=1161970993;",
    "PRAGMA user_version=1;",
    "CREATE TABLE authorization_store_meta(singleton INTEGER PRIMARY KEY CHECK(singleton=1),schema_version INTEGER NOT NULL CHECK(schema_version=1),store_id TEXT NOT NULL UNIQUE,pinned_profile_ref_ecj1 BLOB NOT NULL,pinned_profile_hash TEXT NOT NULL,created_utc TEXT NOT NULL) STRICT;",
    "CREATE TABLE authorization_state(kind TEXT PRIMARY KEY CHECK(kind IN ('ISSUER','REVOCATION','TIME')),service_id TEXT NOT NULL,sequence INTEGER NOT NULL CHECK(sequence>=0),record_ref_ecj1 BLOB NOT NULL,record_hash TEXT NOT NULL,UNIQUE(kind,service_id,sequence)) STRICT;",
    "CREATE TABLE authorization_use(use_key TEXT PRIMARY KEY,authorization_ref_ecj1 BLOB NOT NULL,requested_operation TEXT NOT NULL,target_refs_ecj1 BLOB NOT NULL,configuration_ref_ecj1 BLOB NOT NULL,binding_ref_ecj1 BLOB NOT NULL,execution_identity_ecj1 BLOB NOT NULL,consumed_utc TEXT NOT NULL,validation_record_ecj1 BLOB NOT NULL,ledger_entry_id TEXT NOT NULL UNIQUE,status TEXT NOT NULL CHECK(status='CONSUMED'),FOREIGN KEY(ledger_entry_id) REFERENCES operational_ledger(entry_id) DEFERRABLE INITIALLY DEFERRED) STRICT;",
    "CREATE TABLE operational_ledger(entry_id TEXT PRIMARY KEY,predecessor_entry_id TEXT,entry_ordinal INTEGER NOT NULL UNIQUE CHECK(entry_ordinal>=0),payload_kind TEXT NOT NULL CHECK(payload_kind='AUTHORIZATION_USE'),payload_key TEXT NOT NULL UNIQUE,entry_ecj1 BLOB NOT NULL UNIQUE,FOREIGN KEY(predecessor_entry_id) REFERENCES operational_ledger(entry_id),FOREIGN KEY(payload_key) REFERENCES authorization_use(use_key) DEFERRABLE INITIALLY DEFERRED) STRICT;",
    "CREATE INDEX authorization_use_operation_idx ON authorization_use(requested_operation,authorization_ref_ecj1);",
    "CREATE UNIQUE INDEX operational_ledger_single_genesis_idx ON operational_ledger((predecessor_entry_id IS NULL)) WHERE predecessor_entry_id IS NULL;",
)


def _failure(code: FailureCode, interface: str, check: str) -> NoReturn:
    _i4_fail(code, "ebu_framework.authorization_use", interface, check)


def _formation_failure(name: str) -> NoReturn:
    _failure(FailureCode.I4_RECORD_FORMATION_INVALID, name, "exact record formation")


def _strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        if args or set(kwargs) != set(cls.__dataclass_fields__):  # type: ignore[attr-defined]
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
    if type(value) in {ScientificId, AuthorizationUseKey}:
        return str(value)
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if type(value) is Applicability:
        return value.value
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _record_projection(record: object) -> dict[str, object]:
    return {
        field: _project(getattr(record, field))
        for field in record.__dataclass_fields__  # type: ignore[attr-defined]
    }


def _ecj1(value: object) -> bytes:
    return bytes(_authorization._trust.encode_ecj1(_project(value)))


def _ref_key(reference: ObjectRef) -> bytes:
    return _ecj1(reference)


def _ordered_refs(values: object, *, nonempty: bool = False) -> bool:
    if not (
        type(values) is tuple
        and all(type(item) is ObjectRef for item in values)
        and (not nonempty or bool(values))
    ):
        return False
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _version_tuple(value: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in value.split("."))
    except ValueError:
        return ()


class AuthorizationUseStatus(StrEnum):
    CONSUMED = "CONSUMED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("AuthorizationUseStatus")


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AuthorizationUseStoreIdentity:
    store_id: ScientificId
    database_path: str
    filesystem_kind: str
    schema_version: int
    sqlite_version: str
    synthetic: bool

    def __post_init__(self) -> None:
        if not (
            type(self.store_id) is ScientificId
            and type(self.database_path) is str
            and bool(self.database_path)
            and type(self.filesystem_kind) is str
            and bool(self.filesystem_kind)
            and type(self.schema_version) is int
            and self.schema_version == _SCHEMA_VERSION
            and type(self.sqlite_version) is str
            and bool(_version_tuple(self.sqlite_version))
            and type(self.synthetic) is bool
        ):
            _formation_failure("AuthorizationUseStoreIdentity")
        path = Path(self.database_path)
        if not path.is_absolute() or path.name != _DATABASE_FILENAME:
            _formation_failure("AuthorizationUseStoreIdentity")
        try:
            normalized = path.resolve(strict=False)
        except OSError:
            _formation_failure("AuthorizationUseStoreIdentity")
        if (
            str(path) != str(normalized)
            or not path.parent.exists()
            or path.parent.is_symlink()
            or path.is_symlink()
        ):
            _formation_failure("AuthorizationUseStoreIdentity")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


@_strict_formation
@dataclass(frozen=True, slots=True, eq=True, order=False, unsafe_hash=False, kw_only=True)
class AuthorizationUseRecord:
    authorization_use_key: AuthorizationUseKey
    authorization_ref: ObjectRef
    requested_operation: AuthorizedOperation
    target_object_refs: tuple[ObjectRef, ...]
    accepted_configuration_ref_or_not_applicable: ObjectRef | Applicability
    accepted_execution_binding_ref_or_not_applicable: ObjectRef | Applicability
    execution_identity_or_not_applicable: ExecutionIdentity | Applicability
    consumed_utc: str
    store_id: ScientificId
    ledger_entry_id: ScientificId
    status: AuthorizationUseStatus

    def __post_init__(self) -> None:
        if not (
            type(self.authorization_use_key) is AuthorizationUseKey
            and type(self.authorization_ref) is ObjectRef
            and type(self.requested_operation) is AuthorizedOperation
            and _ordered_refs(self.target_object_refs, nonempty=True)
            and (
                type(self.accepted_configuration_ref_or_not_applicable) is ObjectRef
                or self.accepted_configuration_ref_or_not_applicable
                is Applicability.NOT_APPLICABLE
            )
            and (
                type(self.accepted_execution_binding_ref_or_not_applicable)
                is ObjectRef
                or self.accepted_execution_binding_ref_or_not_applicable
                is Applicability.NOT_APPLICABLE
            )
            and (
                type(self.execution_identity_or_not_applicable) is ExecutionIdentity
                or self.execution_identity_or_not_applicable
                is Applicability.NOT_APPLICABLE
            )
            and _authorization._timestamp(self.consumed_utc)
            and type(self.store_id) is ScientificId
            and type(self.ledger_entry_id) is ScientificId
            and self.status is AuthorizationUseStatus.CONSUMED
        ):
            _formation_failure("AuthorizationUseRecord")

    def to_ecj1(self) -> dict[str, object]:
        return _record_projection(self)


class ConsumeOutcome(StrEnum):
    CONSUMED = "CONSUMED"
    ALREADY_CONSUMED = "ALREADY_CONSUMED"
    UNRESOLVED = "UNRESOLVED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _enum_missing("ConsumeOutcome")


def _guard_synthetic(
    store_identity: AuthorizationUseStoreIdentity, interface: str
) -> None:
    if not store_identity.synthetic:
        _failure(
            FailureCode.PRODUCTION_BOOTSTRAP_MISSING,
            interface,
            "production bootstrap guard",
        )


def _qualify_store(
    store_identity: AuthorizationUseStoreIdentity, interface: str
) -> Path:
    path = Path(store_identity.database_path)
    if not (
        store_identity.filesystem_kind in _SUPPORTED_FILESYSTEMS
        and path.is_absolute()
        and path.name == _DATABASE_FILENAME
        and str(path) == str(path.resolve(strict=False))
        and path.parent.exists()
        and not path.parent.is_symlink()
        and not path.is_symlink()
    ):
        _failure(
            FailureCode.AUTHORIZATION_USE_STORE_UNSUPPORTED,
            interface,
            "filesystem and path qualification",
        )
    actual = _version_tuple(sqlite3.sqlite_version)
    captured = _version_tuple(store_identity.sqlite_version)
    if not ((3, 46, 0) <= actual < (4, 0, 0)) or captured != actual:
        _failure(
            FailureCode.SQLITE_VERSION_UNSUPPORTED,
            interface,
            "SQLite version",
        )
    return path


def _connect(path: Path, *, query_only: bool) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path), timeout=0.0, isolation_level=None)
    connection.execute("PRAGMA trusted_schema=OFF")
    connection.execute("PRAGMA foreign_keys=ON")
    journal_mode = connection.execute("PRAGMA journal_mode=DELETE").fetchone()[0]
    if str(journal_mode).lower() != "delete":
        raise sqlite3.DatabaseError("journal-mode-mismatch")
    connection.execute("PRAGMA synchronous=FULL")
    if connection.execute("PRAGMA synchronous").fetchone()[0] != 2:
        raise sqlite3.DatabaseError("synchronous-mismatch")
    connection.execute("PRAGMA temp_store=MEMORY")
    connection.execute("PRAGMA busy_timeout=0")
    connection.execute(f"PRAGMA query_only={'ON' if query_only else 'OFF'}")
    return connection


def _initialize_synthetic_store(
    path: Path,
    store_identity: AuthorizationUseStoreIdentity,
    validation: AuthorizationValidationRecord,
) -> None:
    if path.exists():
        return
    connection = _connect(path, query_only=False)
    try:
        for statement in _DDL:
            connection.execute(statement)
        connection.execute(
            "INSERT INTO authorization_store_meta(singleton,schema_version,store_id,pinned_profile_ref_ecj1,pinned_profile_hash,created_utc) VALUES(1,?,?,?,?,?)",
            (
                _SCHEMA_VERSION,
                str(store_identity.store_id),
                _ecj1(validation.trusted_time_attestation.trust_profile_ref),
                str(
                    validation.trusted_time_attestation.trust_profile_ref.object_content_hash
                ),
                validation.trusted_time_attestation.attested_utc,
            ),
        )
    finally:
        connection.close()


def _schema_exact(
    connection: sqlite3.Connection,
    store_identity: AuthorizationUseStoreIdentity,
    validation: AuthorizationValidationRecord,
) -> bool:
    if connection.execute("PRAGMA application_id").fetchone()[0] != _APPLICATION_ID:
        return False
    if connection.execute("PRAGMA user_version").fetchone()[0] != _SCHEMA_VERSION:
        return False
    if connection.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
        return False
    if connection.execute("PRAGMA synchronous").fetchone()[0] != 2:
        return False
    if connection.execute("PRAGMA trusted_schema").fetchone()[0] != 0:
        return False
    if connection.execute("PRAGMA temp_store").fetchone()[0] != 2:
        return False
    if connection.execute("PRAGMA busy_timeout").fetchone()[0] != 0:
        return False
    schema_rows = {
        (kind, name): sql
        for kind, name, sql in connection.execute(
            "SELECT type,name,sql FROM sqlite_schema WHERE name NOT LIKE 'sqlite_%'"
        )
    }
    expected_schema = {
        (
            "table" if statement.startswith("CREATE TABLE ") else "index",
            statement.split()[
                3 if statement.startswith("CREATE UNIQUE INDEX ") else 2
            ].split("(", 1)[0],
        ): statement.removesuffix(";")
        for statement in _DDL[2:]
    }
    if schema_rows != expected_schema:
        return False
    profile_ref = validation.trusted_time_attestation.trust_profile_ref
    meta = connection.execute(
        "SELECT schema_version,store_id,pinned_profile_ref_ecj1,pinned_profile_hash FROM authorization_store_meta WHERE singleton=1"
    ).fetchone()
    return meta == (
        _SCHEMA_VERSION,
        str(store_identity.store_id),
        _ecj1(profile_ref),
        str(profile_ref.object_content_hash),
    )


def _operation_details(
    validation: AuthorizationValidationRecord,
) -> tuple[
    AuthorizedOperation,
    ObjectRef | Applicability,
    ObjectRef | Applicability,
    ExecutionIdentity | Applicability,
]:
    if len(validation.effective_operations) != 1:
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            "consume_stage_authorization",
            "exact requested operation",
        )
    try:
        operation = AuthorizedOperation(validation.effective_operations[0])
    except (ValueError, FrameworkError):
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            "consume_stage_authorization",
            "exact requested operation",
        )
    targets = validation.effective_target_object_refs
    configuration: ObjectRef | Applicability = Applicability.NOT_APPLICABLE
    binding: ObjectRef | Applicability = Applicability.NOT_APPLICABLE
    execution: ExecutionIdentity | Applicability = Applicability.NOT_APPLICABLE
    if operation is AuthorizedOperation.ACCEPT_EXPERIMENT_CONFIGURATION:
        configuration = targets[0]
    elif operation is AuthorizedOperation.ACCEPT_EXECUTION_BINDING:
        configuration, binding = targets[:2]
    return operation, configuration, binding, execution


def _ledger_id(use_key: AuthorizationUseKey) -> ScientificId:
    digest = hashlib.sha256(
        _ecj1(
            {
                "authorization_use_key": str(use_key),
                "payload_kind": "AUTHORIZATION_USE",
            }
        )
    ).hexdigest()
    return ScientificId(f"ebu:ledger-entry:validation:sha256-{digest}")


def _new_use_record(
    validation: AuthorizationValidationRecord,
    store_identity: AuthorizationUseStoreIdentity,
) -> AuthorizationUseRecord:
    operation, configuration, binding, execution = _operation_details(validation)
    attestation = validation.trusted_time_attestation
    if type(attestation) is not _authorization.TrustedTimeAttestationV1:
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            "consume_stage_authorization",
            "validated trusted time",
        )
    return AuthorizationUseRecord(
        authorization_use_key=validation.authorization_use_key,
        authorization_ref=validation.authorization_ref,
        requested_operation=operation,
        target_object_refs=validation.effective_target_object_refs,
        accepted_configuration_ref_or_not_applicable=configuration,
        accepted_execution_binding_ref_or_not_applicable=binding,
        execution_identity_or_not_applicable=execution,
        consumed_utc=attestation.attested_utc,
        store_id=store_identity.store_id,
        ledger_entry_id=_ledger_id(validation.authorization_use_key),
        status=AuthorizationUseStatus.CONSUMED,
    )


def _stored_pair_exact(
    path: Path,
    record: AuthorizationUseRecord,
    validation: AuthorizationValidationRecord,
) -> bool:
    connection: sqlite3.Connection | None = None
    try:
        connection = _connect(path, query_only=True)
        use = connection.execute(
            "SELECT authorization_ref_ecj1,requested_operation,target_refs_ecj1,configuration_ref_ecj1,binding_ref_ecj1,execution_identity_ecj1,consumed_utc,validation_record_ecj1,ledger_entry_id,status FROM authorization_use WHERE use_key=?",
            (str(record.authorization_use_key),),
        ).fetchone()
        ledger = connection.execute(
            "SELECT predecessor_entry_id,entry_ordinal,payload_kind,payload_key,entry_ecj1 FROM operational_ledger WHERE entry_id=?",
            (str(record.ledger_entry_id),),
        ).fetchone()
        if use is None or ledger is None:
            return False
        expected_use = (
            _ecj1(record.authorization_ref),
            record.requested_operation.value,
            _ecj1(record.target_object_refs),
            _ecj1(record.accepted_configuration_ref_or_not_applicable),
            _ecj1(record.accepted_execution_binding_ref_or_not_applicable),
            _ecj1(record.execution_identity_or_not_applicable),
            record.consumed_utc,
            _ecj1(validation),
            str(record.ledger_entry_id),
            "CONSUMED",
        )
        entry = {
            "entry_id": str(record.ledger_entry_id),
            "entry_ordinal": ledger[1],
            "payload_key": str(record.authorization_use_key),
            "payload_kind": "AUTHORIZATION_USE",
            "predecessor_entry_id": (
                ledger[0]
                if ledger[0] is not None
                else Applicability.NOT_APPLICABLE.value
            ),
        }
        return (
            use == expected_use
            and ledger[2] == "AUTHORIZATION_USE"
            and ledger[3] == str(record.authorization_use_key)
            and ledger[4] == _ecj1(entry)
        )
    except (sqlite3.Error, OSError):
        return False
    finally:
        if connection is not None:
            connection.close()


def consume_stage_authorization(
    validation: AuthorizationValidationRecord,
    store_identity: AuthorizationUseStoreIdentity,
    /,
) -> AuthorizationUseRecord:
    interface = "consume_stage_authorization"
    if (
        type(validation) is not AuthorizationValidationRecord
        or type(store_identity) is not AuthorizationUseStoreIdentity
    ):
        _formation_failure(interface)
    _guard_synthetic(store_identity, interface)
    if not (
        validation.status
        is AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED
        and validation.failure is Applicability.NOT_APPLICABLE
        and len(validation.completed_checks) == 67
        and all(
            check.status is _authorization.AuthorizationCheckStatus.PASS
            for check in validation.completed_checks
        )
    ):
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            interface,
            "exact validated-not-consumed record",
        )
    path = _qualify_store(store_identity, interface)
    try:
        _initialize_synthetic_store(path, store_identity, validation)
    except (sqlite3.Error, OSError):
        _failure(
            FailureCode.SQLITE_SCHEMA_MISMATCH,
            interface,
            "schema initialization",
        )
    record = _new_use_record(validation, store_identity)
    connection: sqlite3.Connection | None = None
    began = False
    inserted_use = False
    commit_issued = False
    try:
        connection = _connect(path, query_only=False)
        if not _schema_exact(connection, store_identity, validation):
            _failure(
                FailureCode.SQLITE_SCHEMA_MISMATCH,
                interface,
                "schema and settings",
            )
        connection.execute("BEGIN IMMEDIATE")
        began = True
        if not _schema_exact(connection, store_identity, validation):
            _failure(
                FailureCode.SQLITE_SCHEMA_MISMATCH,
                interface,
                "transaction schema and settings",
            )
        connection.execute(
            "INSERT INTO authorization_use(use_key,authorization_ref_ecj1,requested_operation,target_refs_ecj1,configuration_ref_ecj1,binding_ref_ecj1,execution_identity_ecj1,consumed_utc,validation_record_ecj1,ledger_entry_id,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                str(record.authorization_use_key),
                _ecj1(record.authorization_ref),
                record.requested_operation.value,
                _ecj1(record.target_object_refs),
                _ecj1(record.accepted_configuration_ref_or_not_applicable),
                _ecj1(record.accepted_execution_binding_ref_or_not_applicable),
                _ecj1(record.execution_identity_or_not_applicable),
                record.consumed_utc,
                _ecj1(validation),
                str(record.ledger_entry_id),
                record.status.value,
            ),
        )
        inserted_use = True
        head = connection.execute(
            "SELECT entry_id,entry_ordinal FROM operational_ledger ORDER BY entry_ordinal DESC LIMIT 1"
        ).fetchone()
        predecessor = None if head is None else head[0]
        ordinal = 0 if head is None else head[1] + 1
        entry = {
            "entry_id": str(record.ledger_entry_id),
            "entry_ordinal": ordinal,
            "payload_key": str(record.authorization_use_key),
            "payload_kind": "AUTHORIZATION_USE",
            "predecessor_entry_id": (
                predecessor
                if predecessor is not None
                else Applicability.NOT_APPLICABLE.value
            ),
        }
        connection.execute(
            "INSERT INTO operational_ledger(entry_id,predecessor_entry_id,entry_ordinal,payload_kind,payload_key,entry_ecj1) VALUES(?,?,?,?,?,?)",
            (
                str(record.ledger_entry_id),
                predecessor,
                ordinal,
                "AUTHORIZATION_USE",
                str(record.authorization_use_key),
                _ecj1(entry),
            ),
        )
        commit_issued = True
        connection.execute("COMMIT")
        connection.close()
        connection = None
        return record
    except FrameworkError:
        if connection is not None and began and not commit_issued:
            try:
                connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
        raise
    except sqlite3.IntegrityError:
        if connection is not None and began:
            try:
                connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
        if not inserted_use and _stored_pair_exact(path, record, validation):
            _failure(
                FailureCode.AUTHORIZATION_USE_ALREADY_CONSUMED,
                interface,
                "exact duplicate",
            )
        if inserted_use:
            _failure(
                FailureCode.AUTHORIZATION_USE_LEDGER_FAILURE,
                interface,
                "coupled ledger append",
            )
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            interface,
            "unresolved uniqueness state",
        )
    except Exception:
        if connection is not None and began and not commit_issued:
            try:
                connection.execute("ROLLBACK")
            except sqlite3.Error:
                pass
        if commit_issued and _stored_pair_exact(path, record, validation):
            return record
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            interface,
            "ambiguous or storage outcome",
        )
    finally:
        if connection is not None:
            connection.close()


def _require_durable_use(
    validation: AuthorizationValidationRecord,
    use_record: AuthorizationUseRecord,
    store_identity: AuthorizationUseStoreIdentity,
    operation: AuthorizedOperation,
    targets: tuple[ObjectRef, ...],
    interface: str,
) -> None:
    _guard_synthetic(store_identity, interface)
    path = _qualify_store(store_identity, interface)
    if not (
        validation.status
        is AuthorizationValidationStatus.VALIDATED_NOT_CONSUMED
        and validation.failure is Applicability.NOT_APPLICABLE
        and use_record.authorization_use_key == validation.authorization_use_key
        and use_record.authorization_ref == validation.authorization_ref
        and use_record.requested_operation is operation
        and use_record.target_object_refs == targets
        and use_record.store_id == store_identity.store_id
        and use_record.status is AuthorizationUseStatus.CONSUMED
        and _stored_pair_exact(path, use_record, validation)
    ):
        _failure(
            FailureCode.AUTHORIZATION_USE_UNRESOLVED,
            interface,
            "durably matching consumed use",
        )


def accept_registry_object(
    candidate: RegistryRecord,
    validation: AuthorizationValidationRecord,
    use_record: AuthorizationUseRecord,
    store_identity: AuthorizationUseStoreIdentity,
    /,
) -> RegistryRecord:
    interface = "accept_registry_object"
    if not (
        type(candidate) is RegistryRecord
        and type(validation) is AuthorizationValidationRecord
        and type(use_record) is AuthorizationUseRecord
        and type(store_identity) is AuthorizationUseStoreIdentity
    ):
        _formation_failure(interface)
    targets = (candidate.object_ref,)
    _require_durable_use(
        validation,
        use_record,
        store_identity,
        AuthorizedOperation.ACCEPT_REGISTRY_OBJECT,
        targets,
        interface,
    )
    if candidate.lifecycle_status not in {
        LifecycleStatus.DRAFT,
        LifecycleStatus.REVIEWED,
    }:
        _failure(
            FailureCode.REGISTRY_ACCEPTANCE_INVALID,
            interface,
            "candidate lifecycle",
        )
    return _with_lifecycle_status(candidate, LifecycleStatus.ACCEPTED)


def supersede_registry_object(
    predecessor: RegistryRecord,
    successor: RegistryRecord,
    relation: SupersessionRelation,
    validation: AuthorizationValidationRecord,
    use_record: AuthorizationUseRecord,
    store_identity: AuthorizationUseStoreIdentity,
    /,
) -> tuple[RegistryRecord, RegistryRecord]:
    interface = "supersede_registry_object"
    if not (
        type(predecessor) is RegistryRecord
        and type(successor) is RegistryRecord
        and type(relation) is SupersessionRelation
        and type(validation) is AuthorizationValidationRecord
        and type(use_record) is AuthorizationUseRecord
        and type(store_identity) is AuthorizationUseStoreIdentity
    ):
        _formation_failure(interface)
    if type(relation.authorization_ref) is not ObjectRef:
        _failure(
            FailureCode.REGISTRY_SUPERSESSION_INVALID,
            interface,
            "relation authorization ref",
        )
    targets = (
        predecessor.object_ref,
        successor.object_ref,
        relation.authorization_ref,
    )
    _require_durable_use(
        validation,
        use_record,
        store_identity,
        AuthorizedOperation.SUPERSEDE_REGISTRY_OBJECT,
        targets,
        interface,
    )
    if not (
        predecessor.lifecycle_status is LifecycleStatus.ACCEPTED
        and successor.lifecycle_status in {
            LifecycleStatus.DRAFT,
            LifecycleStatus.REVIEWED,
        }
        and relation.predecessor_ref == predecessor.object_ref
        and relation.successor_ref == successor.object_ref
        and relation.authorization_ref == validation.authorization_ref
    ):
        _failure(
            FailureCode.REGISTRY_SUPERSESSION_INVALID,
            interface,
            "supersession records",
        )
    try:
        validate_supersession_relation(relation)
    except FrameworkError:
        _failure(
            FailureCode.REGISTRY_SUPERSESSION_INVALID,
            interface,
            "supersession owner validator",
        )
    return (
        _with_lifecycle_status(predecessor, LifecycleStatus.SUPERSEDED),
        _with_lifecycle_status(successor, LifecycleStatus.ACCEPTED),
    )


def accept_experiment_configuration(
    configuration: ExperimentConfiguration,
    fault_schedule: FaultScheduleV1 | Applicability,
    validation: AuthorizationValidationRecord,
    use_record: AuthorizationUseRecord,
    store_identity: AuthorizationUseStoreIdentity,
    /,
) -> RegistryRecord:
    interface = "accept_experiment_configuration"
    if not (
        type(configuration) is ExperimentConfiguration
        and (
            type(fault_schedule) is FaultScheduleV1
            or fault_schedule is Applicability.NOT_APPLICABLE
        )
        and type(validation) is AuthorizationValidationRecord
        and type(use_record) is AuthorizationUseRecord
        and type(store_identity) is AuthorizationUseStoreIdentity
    ):
        _formation_failure(interface)
    target = (_envelope_ref(configuration),)
    _require_durable_use(
        validation,
        use_record,
        store_identity,
        AuthorizedOperation.ACCEPT_EXPERIMENT_CONFIGURATION,
        target,
        interface,
    )
    try:
        _validate_configuration_acceptance(configuration, fault_schedule)
    except FrameworkError:
        _failure(
            FailureCode.REGISTRY_ACCEPTANCE_INVALID,
            interface,
            "configuration owner validator",
        )
    envelope = configuration.envelope
    draft = RegistryRecord(
        object_ref=target[0],
        object_kind=str(envelope.object_kind_id),
        canonical_value=envelope.object_content_payload,
        lifecycle_status=LifecycleStatus.DRAFT,
    )
    return _with_lifecycle_status(draft, LifecycleStatus.ACCEPTED)


def accept_execution_binding(
    binding: ExecutionBinding,
    accepted_configuration: RegistryRecord,
    validation: AuthorizationValidationRecord,
    use_record: AuthorizationUseRecord,
    store_identity: AuthorizationUseStoreIdentity,
    /,
) -> RegistryRecord:
    interface = "accept_execution_binding"
    if not (
        type(binding) is ExecutionBinding
        and type(accepted_configuration) is RegistryRecord
        and type(validation) is AuthorizationValidationRecord
        and type(use_record) is AuthorizationUseRecord
        and type(store_identity) is AuthorizationUseStoreIdentity
    ):
        _formation_failure(interface)
    targets = (accepted_configuration.object_ref, _envelope_ref(binding))
    _require_durable_use(
        validation,
        use_record,
        store_identity,
        AuthorizedOperation.ACCEPT_EXECUTION_BINDING,
        targets,
        interface,
    )
    try:
        _validate_binding_acceptance(binding, accepted_configuration)
    except FrameworkError:
        _failure(
            FailureCode.REGISTRY_ACCEPTANCE_INVALID,
            interface,
            "binding owner validator",
        )
    envelope = binding.envelope
    draft = RegistryRecord(
        object_ref=targets[1],
        object_kind=str(envelope.object_kind_id),
        canonical_value=envelope.object_content_payload,
        lifecycle_status=LifecycleStatus.DRAFT,
    )
    return _with_lifecycle_status(draft, LifecycleStatus.ACCEPTED)


def append_operational_ledger_entry(
    ledger: Ledger,
    entry: LedgerEntry,
    validation: AuthorizationValidationRecord,
    use_record: AuthorizationUseRecord,
    store_identity: AuthorizationUseStoreIdentity,
    /,
) -> tuple[Ledger, LedgerEntry]:
    interface = "append_operational_ledger_entry"
    if not (
        type(ledger) is Ledger
        and type(entry) is LedgerEntry
        and type(validation) is AuthorizationValidationRecord
        and type(use_record) is AuthorizationUseRecord
        and type(store_identity) is AuthorizationUseStoreIdentity
    ):
        _formation_failure(interface)
    targets = (_envelope_ref(ledger), _envelope_ref(entry))
    _require_durable_use(
        validation,
        use_record,
        store_identity,
        AuthorizedOperation.APPEND_OPERATIONAL_LEDGER_ENTRY,
        targets,
        interface,
    )
    if ledger.ledger_kind is not LedgerKind.OPERATIONAL:
        _failure(
            FailureCode.AUTHORIZATION_USE_LEDGER_FAILURE,
            interface,
            "operational ledger only",
        )
    try:
        _validate_operational_append(ledger, entry)
    except FrameworkError:
        _failure(
            FailureCode.AUTHORIZATION_USE_LEDGER_FAILURE,
            interface,
            "ledger owner validator",
        )
    return ledger, entry


_DEPENDENCY_SENTINELS = (
    os.fspath,
    CommonObjectEnvelope,
    compute_authorization_use_key,
    compute_object_content_hash,
)


__all__ = (
    "AuthorizationUseStatus",
    "AuthorizationUseStoreIdentity",
    "AuthorizationUseRecord",
    "ConsumeOutcome",
    "consume_stage_authorization",
    "accept_registry_object",
    "supersede_registry_object",
    "accept_experiment_configuration",
    "accept_execution_binding",
    "append_operational_ledger_entry",
)
