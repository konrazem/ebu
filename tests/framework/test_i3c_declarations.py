"""Deterministic T0 conformance checks for the frozen I-3C authority slice."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import fields, is_dataclass, replace
from enum import StrEnum
from fractions import Fraction
import hashlib
import inspect
import json
from pathlib import Path
import unittest

import ebu_framework.causal as causal_module
from ebu_framework.canonical import encode_ecj1, parse_ecj1
from ebu_framework.causal import (
    CausalIdentificationStatus,
    CausalRemainder,
    validate_causal_remainder,
)
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.identity import (
    InformationViewHash,
    ObjectContentHash,
    ObjectRef,
    PolicyMemoryPayloadHash,
    ScientificId,
    SemanticVersion,
)
from ebu_framework.hashing import compute_object_content_hash
import ebu_framework.ledger as ledger_module
from ebu_framework.ledger import Ledger, LedgerEntry, LedgerKind, validate_ledger
from ebu_framework.numeric import IntegerV1
import ebu_framework.policy as policy_module
from ebu_framework.policy import (
    InformationContract,
    InformationReadSet,
    InformationView,
    MemoryMode,
    PolicyMemoryState,
    validate_information_view,
    validate_policy_memory_state,
)
from ebu_framework.primitives import (
    Duration,
    Epoch,
    Instant,
    Quantity,
    ResolutionDetail,
    ResolutionState,
)
import ebu_framework.settlement as settlement_module
from ebu_framework.settlement import (
    ChildActionRecord,
    GroupReceipt,
    GroupResidual,
    Quote,
    Receipt,
    SettlementClosureRecord,
    SettlementShare,
    validate_settlement_closure,
)
from ebu_framework.actions import EffectiveInterval


_REPO_ROOT = Path(__file__).resolve().parents[2]
_MECHANICAL_CONTRACT = _REPO_ROOT / "unified_python_research_framework_i3_contract.json"
_VALIDATION_CONTRACT = (
    _REPO_ROOT / "unified_python_research_framework_i3_validation_contract.json"
)
_REPAIR_VALIDATION_CONTRACT = (
    _REPO_ROOT
    / "unified_python_research_framework_i3c_settlement_causality_repair_validation_contract.json"
)
_REPAIR_FIXTURE = (
    _REPO_ROOT / "tests/framework/fixtures/i3c_settlement_causality_repair_v1.json"
)
_MODULES = {
    "policy": policy_module,
    "causal": causal_module,
    "settlement": settlement_module,
    "ledger": ledger_module,
}
_MODULE_NAMES = frozenset(f"ebu_framework.{name}" for name in _MODULES)
_PRODUCTION_PATHS = {
    name: _REPO_ROOT / f"src/ebu_framework/{name}.py" for name in _MODULES
}


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON name: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number: {value}")


def _load_contract(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    text = payload.decode("utf-8", "strict")
    decoder = json.JSONDecoder(
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    parsed, end = decoder.raw_decode(text)
    assert not text[end:].strip()
    assert type(parsed) is dict
    return parsed


def _load_array(path: Path) -> tuple[bytes, list[object]]:
    payload = path.read_bytes()
    assert not payload.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in payload
    assert payload.endswith(b"\n") and not payload.endswith(b"\n\n")
    text = payload.decode("utf-8", "strict")
    decoder = json.JSONDecoder(
        object_pairs_hook=_strict_object,
        parse_constant=_reject_constant,
    )
    parsed, end = decoder.raw_decode(text)
    assert not text[end:].strip()
    assert type(parsed) is list
    return payload, parsed


def _canonical_json_bytes(value: object, *, final_lf: bool = False) -> bytes:
    suffix = "\n" if final_lf else ""
    return (
        json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + suffix
    ).encode("utf-8", "strict")


def _recursive_canonical_bytes(value: object) -> bytes:
    if value is None:
        return b"null"
    if value is True:
        return b"true"
    if value is False:
        return b"false"
    if type(value) is int:
        return str(value).encode("ascii")
    if type(value) is str:
        return json.dumps(value, ensure_ascii=False).encode("utf-8", "strict")
    if type(value) is list:
        return b"[" + b",".join(
            _recursive_canonical_bytes(item) for item in value
        ) + b"]"
    assert type(value) is dict
    keys = sorted(value)
    return b"{" + b",".join(
        _recursive_canonical_bytes(key)
        + b":"
        + _recursive_canonical_bytes(value[key])
        for key in keys
    ) + b"}"


_RUNTIME_TYPES: dict[str, object] = {
    "Applicability": Applicability,
    "CausalIdentificationStatus": CausalIdentificationStatus,
    "CausalRemainder": CausalRemainder,
    "ChildActionRecord": ChildActionRecord,
    "CommonObjectEnvelope": CommonObjectEnvelope,
    "Duration": Duration,
    "EffectiveInterval": EffectiveInterval,
    "Epoch": Epoch,
    "GroupReceipt": GroupReceipt,
    "GroupResidual": GroupResidual,
    "InformationContract": InformationContract,
    "InformationReadSet": InformationReadSet,
    "InformationView": InformationView,
    "InformationViewHash": InformationViewHash,
    "Instant": Instant,
    "IntegerV1": IntegerV1,
    "Ledger": Ledger,
    "LedgerEntry": LedgerEntry,
    "LedgerKind": LedgerKind,
    "LifecycleStatus": LifecycleStatus,
    "MemoryMode": MemoryMode,
    "ObjectContentHash": ObjectContentHash,
    "ObjectRef": ObjectRef,
    "PolicyMemoryPayloadHash": PolicyMemoryPayloadHash,
    "PolicyMemoryState": PolicyMemoryState,
    "Quantity": Quantity,
    "Quote": Quote,
    "Receipt": Receipt,
    "ResolutionDetail": ResolutionDetail,
    "ResolutionState": ResolutionState,
    "ScientificId": ScientificId,
    "SemanticVersion": SemanticVersion,
    "SettlementClosureRecord": SettlementClosureRecord,
    "SettlementShare": SettlementShare,
}
_ENUM_TYPES = {
    "Applicability",
    "CausalIdentificationStatus",
    "LedgerKind",
    "LifecycleStatus",
    "MemoryMode",
    "ResolutionState",
}
_VALUE_TYPES = {
    "InformationViewHash",
    "ObjectContentHash",
    "PolicyMemoryPayloadHash",
    "ScientificId",
    "SemanticVersion",
}
_FORMATION_HELPERS = {
    "ebu_framework.policy": policy_module._formation_failure,
    "ebu_framework.causal": causal_module._formation_failure,
    "ebu_framework.settlement": settlement_module._formation_failure,
    "ebu_framework.ledger": ledger_module._formation_failure,
}
_VALIDATORS = {
    "validate_information_view": validate_information_view,
    "validate_policy_memory_state": validate_policy_memory_state,
    "validate_causal_remainder": validate_causal_remainder,
    "validate_settlement_closure": validate_settlement_closure,
    "validate_ledger": validate_ledger,
}


def _construct(descriptor: dict[str, object]) -> object:
    runtime_type = descriptor["runtime_type"]
    assert type(runtime_type) is str
    if runtime_type == "CanonicalBytes":
        utf8_hex = descriptor["utf8_hex"]
        assert type(utf8_hex) is str
        return bytes.fromhex(utf8_hex)
    if runtime_type == "tuple":
        members = descriptor["members"]
        assert type(members) is list
        return tuple(_construct(member) for member in members)
    if runtime_type in {"str", "bool", "int"}:
        return descriptor["value"]

    runtime_class = _RUNTIME_TYPES[runtime_type]
    if runtime_type in _ENUM_TYPES:
        return runtime_class(descriptor["value"])  # type: ignore[operator]
    if runtime_type in _VALUE_TYPES:
        return runtime_class(value=descriptor["value"])  # type: ignore[operator]

    constructor_arguments = descriptor["constructor_arguments"]
    assert type(constructor_arguments) is list
    keyword_arguments = {
        argument[0]: _construct(argument[2]) for argument in constructor_arguments
    }
    return runtime_class(**keyword_arguments)  # type: ignore[operator]


def _project(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is tuple:
        return [_project(member) for member in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _form_value(module: str, qualname: str, descriptor: dict[str, object]) -> object:
    value = _construct(descriptor)
    expected_type = _RUNTIME_TYPES[qualname]
    if type(value) is not expected_type:
        _FORMATION_HELPERS[module](qualname)
    return value


def _capture_framework_error(callable_value: object) -> FrameworkError:
    try:
        callable_value()  # type: ignore[operator]
    except FrameworkError as error:
        return error
    raise AssertionError("expected FrameworkError")


def _normalized_annotation(value: str) -> str:
    return "".join(value.replace('"', "'").split())


def _class_annotations(tree: ast.Module) -> dict[str, list[tuple[str, str]]]:
    result: dict[str, list[tuple[str, str]]] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            result[node.name] = [
                (item.target.id, ast.unparse(item.annotation))
                for item in node.body
                if isinstance(item, ast.AnnAssign)
                and isinstance(item.target, ast.Name)
            ]
    return result


def _direct_relative_imports(tree: ast.Module) -> list[str]:
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1:
            if node.module is not None:
                imports.append(node.module)
            else:
                imports.extend(alias.name for alias in node.names)
    return imports


def _frame(value: str) -> bytes:
    encoded = value.encode("utf-8", "strict")
    return len(encoded).to_bytes(8, "big") + encoded


def _independent_failure_id(envelope: dict[str, object]) -> str:
    parts = [
        _frame("ebu.failure-id.v1"),
        _frame(envelope["failure_code"]),  # type: ignore[arg-type]
        _frame(envelope["stage"]),  # type: ignore[arg-type]
    ]
    interface = envelope["interface_ref"]
    if type(interface) is dict:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(interface["module"]),  # type: ignore[arg-type]
                _frame(interface["qualname"]),  # type: ignore[arg-type]
                _frame(interface["interface_version"]),  # type: ignore[arg-type]
            )
        )
    else:
        assert interface == "NOT_APPLICABLE"
        parts.append(_frame("NOT_APPLICABLE"))
    object_refs = envelope["object_refs"]
    assert type(object_refs) is list
    parts.append(len(object_refs).to_bytes(8, "big"))
    for reference in object_refs:
        assert type(reference) is dict
        parts.extend(
            (
                _frame(reference["object_id"]),  # type: ignore[arg-type]
                _frame(reference["object_version"]),  # type: ignore[arg-type]
                _frame(reference["object_content_hash"]),  # type: ignore[arg-type]
            )
        )
    event_key = envelope["event_key"]
    if type(event_key) is dict:
        parts.extend(
            (
                _frame("APPLICABLE"),
                _frame(str(event_key["epoch"])),
                _frame(str(event_key["phase_ordinal"])),
                _frame(str(event_key["declared_priority"])),
                _frame(event_key["group_or_scope_id"]),  # type: ignore[arg-type]
                _frame(event_key["event_kind"]),  # type: ignore[arg-type]
                _frame(event_key["primary_object_id"]),  # type: ignore[arg-type]
                _frame(str(event_key["local_sequence"])),
            )
        )
    else:
        assert event_key == "NOT_APPLICABLE"
        parts.append(_frame("NOT_APPLICABLE"))
    parts.append(_frame(str(envelope["failure_ordinal"])))
    digest = hashlib.sha256(b"".join(parts)).hexdigest()
    return f"ebu:failure:core:sha256-{digest}"


def _assert_failure(
    error: FrameworkError,
    expected: dict[str, object],
    vector_id: str,
) -> None:
    actual = error.envelope.to_ecj1()
    expected_projection = expected["failure_envelope_projection"]
    assert type(expected_projection) is dict
    assert len(actual) == 16
    assert actual == expected_projection, vector_id
    assert actual["failure_code"] == expected["failure_code"], vector_id
    failure_id = actual["failure_id"]
    assert type(failure_id) is dict
    independently_derived = _independent_failure_id(actual)
    assert independently_derived == expected["failure_id"], vector_id
    assert failure_id["value"] == independently_derived, vector_id


_SETTLEMENT_PRECEDENCE = (
    "I3_OBJECT_CONTENT_MISMATCH",
    "IMPLICIT_ABSENCE_FORBIDDEN",
    "I3_COLLECTION_ORDER_INVALID",
    "I3_DUPLICATE_MEMBER",
    "SETTLEMENT_LINK_INVALID",
    "CONSERVATION_UNIT_MISMATCH",
    "SETTLEMENT_CLOSURE_FAILURE",
    "CAUSAL_ATTRIBUTION_UNRESOLVED",
    "HASH_MISMATCH",
)


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _envelope_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _rebuild_record(
    record: object,
    *,
    object_id: ScientificId | None = None,
    **changes: object,
) -> object:
    provisional = replace(record, **changes)
    envelope = provisional.envelope  # type: ignore[attr-defined]
    if object_id is not None:
        envelope = replace(envelope, object_id=object_id)
    projection = provisional.to_ecj1()  # type: ignore[attr-defined]
    payload = bytes(encode_ecj1(projection))
    content_hash = compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=(
            None
            if envelope.supersedes_ref is Applicability.NOT_APPLICABLE
            else envelope.supersedes_ref
        ),
        object_content_payload=projection,
    )
    rebuilt_envelope = replace(
        envelope,
        object_content_payload=payload,
        object_content_hash=content_hash,
    )
    return replace(provisional, envelope=rebuilt_envelope)


def _settlement_templates() -> tuple[object, ...]:
    contract = _load_contract(_VALIDATION_CONTRACT)
    vectors = contract["vectors"]
    assert type(vectors) is list
    baseline = next(
        vector for vector in vectors if vector["vector_id"] == "i3v-18-p"
    )
    ordered_arguments = baseline["materialized_effective_input"][
        "ordered_arguments"
    ]
    return tuple(_construct(argument["value"]) for argument in ordered_arguments)


def _quantity(
    template: Quantity,
    descriptor: dict[str, object],
    alternate_unit_ref: ObjectRef,
) -> Quantity:
    amount = descriptor["amount"]
    unit = descriptor["unit"]
    assert type(amount) is str and type(unit) is str
    assert unit in {"EBU", "USD"}
    return replace(
        template,
        magnitude=IntegerV1(value=int(amount)),
        unit_ref=(template.unit_ref if unit == "EBU" else alternate_unit_ref),
    )


def _build_settlement_arguments(
    vector_input: dict[str, object],
    templates: tuple[object, ...],
) -> tuple[object, ...]:
    (
        closure_template,
        quote_template,
        receipt_template,
        group_template,
        child_templates,
        residual_template,
        share_templates,
        _,
    ) = templates
    assert type(quote_template) is Quote
    assert type(receipt_template) is Receipt
    assert type(group_template) is GroupReceipt
    assert type(child_templates) is tuple and len(child_templates) == 1
    assert type(child_templates[0]) is ChildActionRecord
    assert type(residual_template) is GroupResidual
    assert type(share_templates) is tuple and len(share_templates) == 1
    assert type(share_templates[0]) is SettlementShare
    assert type(closure_template) is SettlementClosureRecord

    additional = vector_input["additional_active_failures"]
    assert type(additional) is list
    quote = quote_template
    if "I3_COLLECTION_ORDER_INVALID" in additional:
        ordered = tuple(
            sorted(
                (quote_template.request_ref, quote_template.distortion_ref),
                key=_ref_key,
            )
        )
        quote = _rebuild_record(
            quote_template,
            observation_refs=tuple(reversed(ordered)),
        )
        assert type(quote) is Quote

    receipt = _rebuild_record(
        receipt_template,
        quote_ref=_envelope_ref(quote),
    )
    assert type(receipt) is Receipt

    share_specs = vector_input["shares"]
    assert type(share_specs) is list
    alternate_unit_ref = quote_template.request_ref
    base_share = share_templates[0]
    shares: tuple[SettlementShare, ...] = tuple(
        _rebuild_record(
            base_share,
            object_id=ScientificId(value=f"ebu:object:i3c-scr:share-{index}"),
            amount=_quantity(
                residual_template.measured_total,
                share_spec,
                alternate_unit_ref,
            ),
            evidence_refs=(
                ()
                if share_spec["evidence_role"] == "NONE"
                else base_share.evidence_refs
            ),
        )
        for index, share_spec in enumerate(share_specs)
    )  # type: ignore[assignment]
    shares = tuple(sorted(shares, key=lambda share: _ref_key(_envelope_ref(share))))

    group_status = vector_input["group_causal_status"]
    assert type(group_status) is str
    group_receipt = _rebuild_record(
        group_template,
        child_receipt_refs=(_envelope_ref(receipt),),
        causal_status=CausalIdentificationStatus(group_status),
        settlement_ref=(
            group_template.measurement_ref
            if vector_input["group_settlement_link"] is True
            else Applicability.NOT_APPLICABLE
        ),
    )
    assert type(group_receipt) is GroupReceipt

    causal_kind = vector_input["child_causal_contribution"]
    assert type(causal_kind) is str
    causal_ref = (
        Applicability.NOT_APPLICABLE
        if causal_kind == "NOT_APPLICABLE"
        else child_templates[0].causal_contribution_ref
    )
    assert type(causal_ref) in {ObjectRef, Applicability}
    settlement_ref = (
        (
            _envelope_ref(shares[0])
            if shares
            else child_templates[0].settlement_share_ref
        )
        if vector_input["child_settlement_link"] is True
        else Applicability.NOT_APPLICABLE
    )
    child = _rebuild_record(
        child_templates[0],
        group_receipt_ref=(
            quote_template.request_ref
            if "SETTLEMENT_LINK_INVALID" in additional
            else _envelope_ref(group_receipt)
        ),
        causal_contribution_ref=causal_ref,
        settlement_share_ref=settlement_ref,
    )
    assert type(child) is ChildActionRecord
    child_actions = (child,)

    measured = vector_input["measured_total"]
    declared_share_total = vector_input["declared_share_total"]
    residual_value = vector_input["residual"]
    assert type(measured) is dict
    assert type(declared_share_total) is dict
    assert type(residual_value) is dict
    residual = _rebuild_record(
        residual_template,
        group_receipt_ref=_envelope_ref(group_receipt),
        measured_total=_quantity(
            residual_template.measured_total,
            measured,
            alternate_unit_ref,
        ),
        share_total=_quantity(
            residual_template.share_total,
            declared_share_total,
            alternate_unit_ref,
        ),
        residual=_quantity(
            residual_template.residual,
            residual_value,
            alternate_unit_ref,
        ),
    )
    assert type(residual) is GroupResidual

    closure_state = vector_input["closure_state"]
    assert type(closure_state) is str
    resolution = replace(
        closure_template.closure_resolution,
        state=ResolutionState(closure_state),
        present_value_ref=(
            closure_template.closure_resolution.present_value_ref
            if closure_state == "PRESENT"
            else Applicability.NOT_APPLICABLE
        ),
    )
    closure = _rebuild_record(
        closure_template,
        group_residual_ref=_envelope_ref(residual),
        share_refs=tuple(_envelope_ref(share) for share in shares),
        closure_resolution=resolution,
    )
    assert type(closure) is SettlementClosureRecord
    if "HASH_MISMATCH" in additional:
        bad_hash = ObjectContentHash(value="sha256:" + "f" * 64)
        if bad_hash == closure.envelope.object_content_hash:
            bad_hash = ObjectContentHash(value="sha256:" + "e" * 64)
        closure = replace(
            closure,
            envelope=replace(closure.envelope, object_content_hash=bad_hash),
        )

    argument_status = vector_input["argument_causal_status"]
    assert type(argument_status) is str
    return (
        closure,
        quote,
        receipt,
        group_receipt,
        child_actions,
        residual,
        shares,
        CausalIdentificationStatus(argument_status),
    )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(value) for value in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(value) for value in values)
    return len(keys) != len(set(keys))


def _ordered_records(values: tuple[object, ...]) -> bool:
    keys = tuple(_ref_key(_envelope_ref(record)) for record in values)
    return keys == tuple(sorted(keys))


def _duplicate_records(values: tuple[object, ...]) -> bool:
    return any(
        left == right
        for index, left in enumerate(values)
        for right in values[index + 1 :]
    )


def _quantity_units_match(left: Quantity, right: Quantity) -> bool:
    return left.unit_ref == right.unit_ref and left.dimension_ref == right.dimension_ref


def _core_fraction(value: object) -> Fraction:
    projected = value.to_ecj1()  # type: ignore[attr-defined]
    variant = projected["variant"]
    if variant == "INTEGER_V1":
        return Fraction(projected["value"])
    if variant == "RATIONAL_V1":
        return Fraction(projected["numerator"], projected["denominator"])
    if variant == "DECIMAL_V1":
        coefficient = projected["coefficient"]
        exponent = projected["exponent10"]
        if exponent >= 0:
            return Fraction(coefficient * 10**exponent)
        return Fraction(coefficient, 10 ** (-exponent))
    bits = int(projected["bits"], 16)
    sign = -1 if bits >> 63 else 1
    exponent_bits = (bits >> 52) & 0x7FF
    fraction_bits = bits & ((1 << 52) - 1)
    if exponent_bits == 0:
        significand = fraction_bits
        exponent = -1074
    else:
        significand = (1 << 52) | fraction_bits
        exponent = exponent_bits - 1023 - 52
    if exponent >= 0:
        return Fraction(sign * significand * 2**exponent)
    return Fraction(sign * significand, 2 ** (-exponent))


def _independent_object_hash_matches(record: object) -> bool:
    envelope = record.envelope  # type: ignore[attr-defined]
    supersedes = (
        envelope.supersedes_ref
        if type(envelope.supersedes_ref) is ObjectRef
        else None
    )
    recomputed = compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=supersedes,
        object_content_payload=parse_ecj1(envelope.object_content_payload),
    )
    return recomputed == envelope.object_content_hash


def _independent_settlement_active_codes(
    arguments: tuple[object, ...],
) -> tuple[str, ...]:
    (
        closure,
        quote,
        receipt,
        group_receipt,
        child_actions,
        residual,
        shares,
        causal_status,
    ) = arguments
    assert type(closure) is SettlementClosureRecord
    assert type(quote) is Quote
    assert type(receipt) is Receipt
    assert type(group_receipt) is GroupReceipt
    assert type(child_actions) is tuple
    assert type(residual) is GroupResidual
    assert type(shares) is tuple
    assert type(causal_status) is CausalIdentificationStatus

    active: set[str] = set()
    records = (
        closure,
        quote,
        receipt,
        group_receipt,
    ) + child_actions + (residual,) + shares
    if any(
        parse_ecj1(record.envelope.object_content_payload)  # type: ignore[attr-defined]
        != record.to_ecj1()  # type: ignore[attr-defined]
        for record in records
    ):
        active.add("I3_OBJECT_CONTENT_MISMATCH")

    applicability_values = (group_receipt.settlement_ref,) + tuple(
        value
        for child in child_actions
        for value in (
            child.causal_contribution_ref,
            child.settlement_share_ref,
        )
    )
    if any(value is Applicability.APPLICABLE for value in applicability_values):
        active.add("IMPLICIT_ABSENCE_FORBIDDEN")

    ref_collections = (
        quote.observation_refs,
        quote.state_refs,
        quote.parameter_refs,
        quote.uncertainty_refs,
        quote.accepted_quantity_refs,
        quote.unresolved_term_refs,
        quote.computation_dependency_refs,
        receipt.measurement_refs,
        receipt.delivered_quantity_refs,
        receipt.loss_refs,
        receipt.outflow_refs,
        receipt.unresolved_refs,
        group_receipt.child_receipt_refs,
        closure.share_refs,
    ) + tuple(child.measurement_refs for child in child_actions) + tuple(
        share.evidence_refs for share in shares
    )
    if (
        any(not _ordered_refs(values) for values in ref_collections)
        or not _ordered_records(child_actions)
        or not _ordered_records(shares)
    ):
        active.add("I3_COLLECTION_ORDER_INVALID")
    if (
        any(_duplicate_refs(values) for values in ref_collections)
        or _duplicate_records(child_actions)
        or _duplicate_records(shares)
    ):
        active.add("I3_DUPLICATE_MEMBER")

    receipt_ref = _envelope_ref(receipt)
    group_ref = _envelope_ref(group_receipt)
    if not (
        receipt.quote_ref == _envelope_ref(quote)
        and group_receipt.child_receipt_refs == (receipt_ref,)
        and all(child.group_receipt_ref == group_ref for child in child_actions)
        and residual.group_receipt_ref == group_ref
        and closure.group_residual_ref == _envelope_ref(residual)
        and closure.share_refs
        == tuple(_envelope_ref(share) for share in shares)
    ):
        active.add("SETTLEMENT_LINK_INVALID")

    comparison_quantities = (residual.share_total, residual.residual) + tuple(
        share.amount for share in shares
    )
    if any(
        not _quantity_units_match(residual.measured_total, quantity)
        for quantity in comparison_quantities
    ):
        active.add("CONSERVATION_UNIT_MISMATCH")

    if (
        sum(
            (_core_fraction(share.amount.magnitude) for share in shares),
            Fraction(),
        )
        != _core_fraction(residual.share_total.magnitude)
        or _core_fraction(residual.measured_total.magnitude)
        != _core_fraction(residual.share_total.magnitude)
        + _core_fraction(residual.residual.magnitude)
        or bool(shares)
        != (closure.closure_resolution.state is ResolutionState.PRESENT)
    ):
        active.add("SETTLEMENT_CLOSURE_FAILURE")

    if (
        causal_status is not CausalIdentificationStatus.IDENTIFIED
        or group_receipt.causal_status is not CausalIdentificationStatus.IDENTIFIED
    ) and any(
        type(child.causal_contribution_ref) is ObjectRef
        for child in child_actions
    ):
        active.add("CAUSAL_ATTRIBUTION_UNRESOLVED")
    if causal_status is CausalIdentificationStatus.IDENTIFIED and not child_actions:
        active.add("CAUSAL_ATTRIBUTION_UNRESOLVED")

    if any(not _independent_object_hash_matches(record) for record in records):
        active.add("HASH_MISMATCH")
    return tuple(code for code in _SETTLEMENT_PRECEDENCE if code in active)


def _reconstruct_supplemental_active_codes(
    vector: dict[str, object],
) -> tuple[str, ...]:
    layer = vector["validation_layer"]
    vector_input = vector["input"]
    assert type(layer) is str and type(vector_input) is dict
    if layer == "RECORD_FORMATION":
        return ("I3_RECORD_FORMATION_INVALID",)
    if layer == "UPSTREAM_EXISTING_NUMERIC_RULE":
        numeric_condition = vector_input["upstream_numeric_condition"]
        assert type(numeric_condition) is str
        return (
            "QUANTITY_TYPE_MISMATCH"
            if numeric_condition == "NEGATIVE_PROHIBITED_BY_DECLARED_RULE"
            else "CORE_NUMBER_INVALID",
        )
    if layer == "UPSTREAM_IMMUTABLE_PHYSICAL_RECORD":
        return ("REGISTRY_IMMUTABLE",)
    if layer in {
        "ACCEPTANCE_BOUNDARY",
        "EXTERNAL_INSTITUTIONAL_RULE_ACCEPTANCE",
    }:
        return ()
    assert layer == "SETTLEMENT_VALIDATOR"

    active = set(vector_input["additional_active_failures"])
    shares = vector_input["shares"]
    declared_total = vector_input["declared_share_total"]
    residual = vector_input["residual"]
    measured_total = vector_input["measured_total"]
    assert type(shares) is list
    assert type(declared_total) is dict
    assert type(residual) is dict
    assert type(measured_total) is dict
    if any(
        quantity["unit"] != measured_total["unit"]
        for quantity in (declared_total, residual, *shares)
    ):
        active.add("CONSERVATION_UNIT_MISMATCH")
    share_sum = sum(int(share["amount"]) for share in shares)
    if (
        share_sum != int(declared_total["amount"])
        or int(measured_total["amount"])
        != int(declared_total["amount"]) + int(residual["amount"])
        or bool(shares) != (vector_input["closure_state"] == "PRESENT")
    ):
        active.add("SETTLEMENT_CLOSURE_FAILURE")
    nonidentified = (
        vector_input["group_causal_status"] != "IDENTIFIED"
        or vector_input["argument_causal_status"] != "IDENTIFIED"
    )
    causal_claim = vector_input["child_causal_contribution"] in {
        "NUMERIC_OBJECT_REF",
        "LINKED_EVIDENCE_OBJECT_REF",
    }
    if nonidentified and causal_claim:
        active.add("CAUSAL_ATTRIBUTION_UNRESOLVED")
    return tuple(code for code in _SETTLEMENT_PRECEDENCE if code in active)


def test_i3c_runtime_and_static_inventory() -> None:
    contract = _load_contract(_MECHANICAL_CONTRACT)
    module_exports = contract["module_exports"]
    direct_imports = contract["direct_imports"]
    assert type(module_exports) is dict and type(direct_imports) is dict

    annotations: dict[str, list[tuple[str, str]]] = {}
    for module_name, path in _PRODUCTION_PATHS.items():
        source = path.read_text(encoding="utf-8")
        assert "entropy" not in source.casefold()
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec", dont_inherit=True)
        annotations.update(_class_annotations(tree))
        assert tuple(_MODULES[module_name].__all__) == tuple(
            module_exports[module_name]
        )
        assert _direct_relative_imports(tree) == direct_imports[module_name]

    types = contract["types"]
    assert type(types) is list
    selected_types = [entry for entry in types if entry[1] in _MODULES]
    assert len(selected_types) == 17
    for entry in selected_types:
        name, module_name, formation, members_or_fields = entry[:4]
        runtime_value = getattr(_MODULES[module_name], name)
        if formation == "FROZEN_DATACLASS":
            assert is_dataclass(runtime_value)
            parameters = runtime_value.__dataclass_params__
            assert parameters.frozen is True
            assert parameters.eq is True
            assert parameters.order is False
            assert parameters.unsafe_hash is False
            expected_fields = [field_spec[0] for field_spec in members_or_fields]
            assert [field.name for field in fields(runtime_value)] == expected_fields
            assert tuple(runtime_value.__slots__) == tuple(expected_fields)
            signature = inspect.signature(runtime_value)
            assert all(
                parameter.kind is inspect.Parameter.KEYWORD_ONLY
                for parameter in signature.parameters.values()
            )
            expected_annotations = [
                (field_spec[0], field_spec[1].split("/", 1)[0])
                for field_spec in members_or_fields
            ]
            assert [field_name for field_name, _ in annotations[name]] == expected_fields
            assert [
                _normalized_annotation(annotation)
                for _, annotation in annotations[name]
            ] == [
                _normalized_annotation(annotation)
                for _, annotation in expected_annotations
            ]
            for invalid_arguments in ({}, {"unknown_field": None}):
                raised = _capture_framework_error(
                    lambda invalid_arguments=invalid_arguments: runtime_value(
                        **invalid_arguments
                    )
                )
                assert raised.envelope.to_ecj1()["failure_code"] == (
                    "I3_RECORD_FORMATION_INVALID"
                )
        else:
            assert formation == "STRENUM"
            assert issubclass(runtime_value, StrEnum)
            assert list(runtime_value.__members__) == members_or_fields
            assert [member.value for member in runtime_value] == members_or_fields

    validators = contract["validators"]
    assert type(validators) is list
    selected_validators = [
        validator for validator in validators if validator["module"] in _MODULES
    ]
    assert len(selected_validators) == 5
    assert [validator["name"] for validator in selected_validators] == list(
        _VALIDATORS
    )
    for validator in selected_validators:
        signature = inspect.signature(_VALIDATORS[validator["name"]])
        assert list(signature.parameters) == validator["argument_order"]
        assert all(
            parameter.kind is inspect.Parameter.POSITIONAL_ONLY
            for parameter in signature.parameters.values()
        )
        assert signature.return_annotation in (None, "None")

    selected_interfaces = frozenset(_VALIDATORS)
    collection_rows = [
        row
        for row in contract["collection_contracts"]
        if row["owner_interface"] in selected_interfaces
    ]
    applicability_rows = [
        row
        for row in contract["applicability_contracts"]
        if row["owner_interface"] in selected_interfaces
    ]
    paired_rows = [
        row
        for row in contract["paired_quantity_compatibility_inventory"]
        if row["validator"] in selected_interfaces
    ]
    scan_rows = [
        row
        for row in contract["object_content_scan_orders"]
        if row["validator"] in selected_interfaces
    ]
    assert len(collection_rows) == 31
    assert len(applicability_rows) == 10
    assert len(paired_rows) == 5
    assert len(scan_rows) == 5
    assert [row["scan_position"] for row in paired_rows] == [
        0,
        1,
        0,
        1,
        "2_PLUS_CANONICAL_SHARE_INDEX_i",
    ]

    dependency_graph = {
        name: tuple(direct_imports[name]) for name in contract["module_exports"]
    }
    assert len(dependency_graph) == 15
    assert sum(len(dependencies) for dependencies in dependency_graph.values()) == 91
    visited: set[str] = set()
    active: set[str] = set()

    def visit(module: str) -> None:
        if module in visited:
            return
        assert module not in active
        active.add(module)
        for dependency in dependency_graph[module]:
            if dependency in dependency_graph:
                visit(dependency)
        active.remove(module)
        visited.add(module)

    for module in dependency_graph:
        visit(module)
    assert len(visited) == 15

    compatibility = _load_contract(
        _REPO_ROOT / "post_i4_legacy_test_compatibility_contract.json"
    )
    failures = tuple(code.value for code in FailureCode)
    i6 = _load_contract(
        _REPO_ROOT / "unified_python_research_framework_i6_contract.json"
    )
    failure_slices = compatibility["current_surface"]["failure_slices"]
    failure_projection = ("\n".join(failures) + "\n").encode("utf-8")
    assert (len(failures), tuple(row["stop"] for row in failure_slices)) == (
        232,
        (53, 88, 102, 124, 185),
    )
    assert failures[53:88] == tuple(contract["failure_append_order"])
    assert tuple(
        failures[row["start"] : row["stop"]] for row in failure_slices
    ) == tuple(tuple(row["values"]) for row in failure_slices)
    assert (
        failures[:185],
        failures[185:227],
        failures[:227],
    ) == (
        tuple(compatibility["current_surface"]["failure_order"]),
        tuple(
            _load_contract(
                _REPO_ROOT / "unified_python_research_framework_i5_contract.json"
            )["failure_append_order"]
        ),
        tuple(
            _load_contract(
                _REPO_ROOT / "post_i5_legacy_test_compatibility_contract.json"
            )["current_surface"]["failure_order"]
        ),
    )
    assert (
        len(("\n".join(failures[:227]) + "\n").encode("utf-8")),
        hashlib.sha256(("\n".join(failures[:227]) + "\n").encode("utf-8")).hexdigest(),
        len(("\n".join(failures[185:227]) + "\n").encode("utf-8")),
        hashlib.sha256(
            ("\n".join(failures[185:227]) + "\n").encode("utf-8")
        ).hexdigest(),
    ) == (
        5997,
        "4cb1daceb30c0f106e7ba288980d379da2403236593948b4be47247704555ae4",
        1103,
        "b70fccfca86d4b7118bf80593794b40a2ad8f3848dbe4ff0963741e4e56f3681",
    )
    assert failures[227:] == tuple(i6["failure_inventory"]["append_order"])
    assert (len(failure_projection), hashlib.sha256(failure_projection).hexdigest()) == (
        i6["failure_inventory"]["future_lf"]["byte_count"],
        i6["failure_inventory"]["future_lf"]["sha256"],
    )


def test_i3c_committed_authority_vectors() -> None:
    contract = _load_contract(_VALIDATION_CONTRACT)
    vectors = contract["vectors"]
    assert type(vectors) is list
    selected = [
        vector
        for vector in vectors
        if vector["materialized_effective_input"]["interface"]["module"]
        in _MODULE_NAMES
    ]
    assert len(selected) == 125
    assert Counter(vector["category"] for vector in selected) == {
        "FORMATION_POSITIVE": 17,
        "FORMATION_BOUNDARY": 17,
        "FORMATION_NEGATIVE": 17,
        "VALIDATOR_POSITIVE": 5,
        "VALIDATOR_BOUNDARY": 5,
        "ISOLATED_SINGLE_FAILURE": 32,
        "ADJACENT_PRECEDENCE_PAIR": 27,
        "MULTIPLY_INVALID_ALL_PRECEDENCE": 5,
    }

    effective_outcomes: dict[bytes, bytes] = {}
    exercised: Counter[str] = Counter()
    success_count = 0
    failure_count = 0
    for vector in selected:
        vector_id = vector["vector_id"]
        exercised[vector_id] += 1
        effective_input = vector["materialized_effective_input"]
        interface = effective_input["interface"]
        assert interface == vector["expected_interface"]
        assert vector["expected_stage"] == "I-3"
        ordered_arguments = effective_input["ordered_arguments"]
        expected = vector["expected"]

        effective_key = json.dumps(
            {
                "interface": interface,
                "ordered_arguments": ordered_arguments,
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        outcome_key = json.dumps(
            expected,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        previous = effective_outcomes.setdefault(effective_key, outcome_key)
        assert previous == outcome_key, vector_id

        if vector["category"].startswith("FORMATION_"):
            assert len(ordered_arguments) == 1
            descriptor = ordered_arguments[0]["value"]
            if expected["kind"] == "SUCCESS":
                value = _form_value(
                    interface["module"], interface["qualname"], descriptor
                )
                projection = _project(value)
                assert projection == descriptor["ecj1"], vector_id
                assert projection == expected["return_value"], vector_id
                assert projection == expected["successful_projection"], vector_id
                success_count += 1
            else:
                raised = _capture_framework_error(
                    lambda: _form_value(
                        interface["module"], interface["qualname"], descriptor
                    )
                )
                _assert_failure(raised, expected, vector_id)
                failure_count += 1
            continue

        arguments = []
        for argument in ordered_arguments:
            descriptor = argument["value"]
            value = _construct(descriptor)
            assert _project(value) == descriptor["ecj1"], vector_id
            arguments.append(value)
        validator = _VALIDATORS[interface["qualname"]]
        if expected["kind"] == "SUCCESS":
            assert validator(*arguments) is expected["return_value"], vector_id
            assert [_project(argument) for argument in arguments] == expected[
                "successful_projection"
            ], vector_id
            success_count += 1
        else:
            raised = _capture_framework_error(lambda: validator(*arguments))
            _assert_failure(raised, expected, vector_id)
            failure_count += 1

    assert len(exercised) == 125
    assert set(exercised.values()) == {1}
    assert len(effective_outcomes) == 125
    assert success_count == 44
    assert failure_count == 81

    selected_by_id = {vector["vector_id"]: vector for vector in selected}
    preserved_causal_vectors = {
        "i3v-18-s08": ["CAUSAL_ATTRIBUTION_UNRESOLVED"],
        "i3v-18-a07": [
            "SETTLEMENT_CLOSURE_FAILURE",
            "CAUSAL_ATTRIBUTION_UNRESOLVED",
        ],
        "i3v-18-a08": [
            "CAUSAL_ATTRIBUTION_UNRESOLVED",
            "HASH_MISMATCH",
        ],
        "i3v-18-m": list(_SETTLEMENT_PRECEDENCE),
    }
    for vector_id, active_codes in preserved_causal_vectors.items():
        vector = selected_by_id[vector_id]
        assert vector["precedence_evidence"]["active_failure_codes"] == active_codes
        child_descriptor = vector["materialized_effective_input"][
            "ordered_arguments"
        ][4]["value"]["members"][0]
        causal_descriptor = next(
            argument[2]
            for argument in child_descriptor["constructor_arguments"]
            if argument[0] == "causal_contribution_ref"
        )
        assert causal_descriptor["runtime_type"] == "ObjectRef"


def test_i3c_settlement_causality_repair_supplemental_vectors() -> None:
    repair_contract = _load_contract(_REPAIR_VALIDATION_CONTRACT)
    fixture_raw, fixture_vectors = _load_array(_REPAIR_FIXTURE)
    contract_vectors = repair_contract["supplemental_vectors"]
    projection = repair_contract["supplemental_fixture_projection"]
    assert type(contract_vectors) is list
    assert type(projection) is dict
    assert fixture_vectors == contract_vectors
    assert fixture_raw == _canonical_json_bytes(contract_vectors, final_lf=True)
    assert fixture_raw == _recursive_canonical_bytes(contract_vectors) + b"\n"
    assert len(fixture_raw) == projection["canonical_byte_count"] == 34418
    assert (
        hashlib.sha256(fixture_raw).hexdigest()
        == projection["canonical_sha256"]
        == "f4857cd3b36e2154143617ea7bb4b7cff45cb29292df0fa837effa4c6ec7cb58"
    )

    case_order = repair_contract["supplemental_case_order"]
    schema = repair_contract["supplemental_vector_schema"]
    assert type(case_order) is list and type(schema) is dict
    assert [vector["id"] for vector in fixture_vectors] == case_order
    assert len(case_order) == len(set(case_order)) == 36
    required_fields = set(schema["required_top_level_fields"])
    input_fields = set(schema["input_fields"])
    for vector in fixture_vectors:
        assert type(vector) is dict
        assert set(vector) == required_fields
        assert type(vector["input"]) is dict
        assert set(vector["input"]) == input_fields

    expected_outcomes = Counter(
        vector["expected"]["outcome"] for vector in fixture_vectors
    )
    assert expected_outcomes == {
        "SUCCESS": 9,
        "FAILURE": 25,
        "FAIL_CLOSED_NO_ACCEPTANCE": 2,
    }

    effective_outcomes: dict[bytes, bytes] = {}
    for vector in fixture_vectors:
        effective_key = _canonical_json_bytes(vector["input"])
        outcome_key = _canonical_json_bytes(vector["expected"])
        previous = effective_outcomes.setdefault(effective_key, outcome_key)
        assert previous == outcome_key, vector["id"]
    assert len(effective_outcomes) == 36

    templates = _settlement_templates()
    base_shares = templates[6]
    assert type(base_shares) is tuple and len(base_shares) == 1
    base_share = base_shares[0]
    assert type(base_share) is SettlementShare
    validator_calls: Counter[str] = Counter()
    exercised: Counter[str] = Counter()
    success_count = 0
    failure_count = 0
    fail_closed_count = 0

    for vector in fixture_vectors:
        assert type(vector) is dict
        vector_id = vector["id"]
        layer = vector["validation_layer"]
        vector_input = vector["input"]
        expected = vector["expected"]
        assert type(vector_id) is str
        assert type(layer) is str
        assert type(vector_input) is dict
        assert type(expected) is dict
        exercised[vector_id] += 1

        reconstructed = _reconstruct_supplemental_active_codes(vector)
        assert list(reconstructed) == expected["active_failures"], vector_id
        assert expected["first_failure"] == (
            reconstructed[0] if reconstructed else "NOT_APPLICABLE"
        ), vector_id

        if layer == "SETTLEMENT_VALIDATOR":
            arguments = _build_settlement_arguments(vector_input, templates)
            independently_active = _independent_settlement_active_codes(arguments)
            assert independently_active == reconstructed, vector_id
            before = _canonical_json_bytes(
                [_project(argument) for argument in arguments]
            )
            measurement_ref = arguments[3].measurement_ref  # type: ignore[attr-defined]
            validator_calls[vector_id] += 1
            if expected["accepted"] is True:
                assert validate_settlement_closure(*arguments) is None
                success_count += 1
            else:
                raised = _capture_framework_error(
                    lambda arguments=arguments: validate_settlement_closure(*arguments)
                )
                assert (
                    raised.envelope.to_ecj1()["failure_code"]
                    == expected["first_failure"]
                ), vector_id
                failure_count += 1
            after = _canonical_json_bytes(
                [_project(argument) for argument in arguments]
            )
            assert after == before, vector_id
            assert arguments[3].measurement_ref == measurement_ref  # type: ignore[attr-defined]
            continue

        if layer == "RECORD_FORMATION":
            constructor_arguments = {
                field.name: getattr(base_share, field.name)
                for field in fields(SettlementShare)
            }
            rule_ref_kind = vector_input["shares"][0]["rule_ref"]
            if rule_ref_kind == "MISSING":
                del constructor_arguments["rule_ref"]
            else:
                assert rule_ref_kind == "MALFORMED"
                constructor_arguments["rule_ref"] = "malformed"
            raised = _capture_framework_error(
                lambda constructor_arguments=constructor_arguments: SettlementShare(
                    **constructor_arguments
                )
            )
            assert (
                raised.envelope.to_ecj1()["failure_code"]
                == expected["first_failure"]
            ), vector_id
            failure_count += 1
            continue

        if layer == "UPSTREAM_EXISTING_NUMERIC_RULE":
            numeric_condition = vector_input["upstream_numeric_condition"]
            if numeric_condition == "MALFORMED_CORE_NUMBER":
                raised = _capture_framework_error(
                    lambda: IntegerV1(value="INVALID")  # type: ignore[arg-type]
                )
                assert (
                    raised.envelope.to_ecj1()["failure_code"]
                    == expected["first_failure"]
                ), vector_id
            else:
                assert numeric_condition == "NEGATIVE_PROHIBITED_BY_DECLARED_RULE"
                assert IntegerV1(value=-1).value == -1
                assert expected["first_failure"] == "QUANTITY_TYPE_MISMATCH"
            failure_count += 1
            continue

        if layer == "UPSTREAM_IMMUTABLE_PHYSICAL_RECORD":
            assert vector_input["physical_measurement_rewrite"] is True
            assert expected["first_failure"] == "REGISTRY_IMMUTABLE"
            assert FailureCode.REGISTRY_IMMUTABLE.value == expected["first_failure"]
            failure_count += 1
            continue

        assert layer in {
            "ACCEPTANCE_BOUNDARY",
            "EXTERNAL_INSTITUTIONAL_RULE_ACCEPTANCE",
        }
        assert expected["accepted"] is False
        assert expected["outcome"] == "FAIL_CLOSED_NO_ACCEPTANCE"
        assert reconstructed == ()
        fail_closed_count += 1

    validator_vector_ids = {
        vector["id"]
        for vector in fixture_vectors
        if vector["validation_layer"] == "SETTLEMENT_VALIDATOR"
    }
    assert len(exercised) == 36
    assert set(exercised.values()) == {1}
    assert len(validator_vector_ids) == len(validator_calls) == 29
    assert set(validator_calls) == validator_vector_ids
    assert set(validator_calls.values()) == {1}
    assert success_count == projection["success_count"] == 9
    assert failure_count == 25
    assert fail_closed_count == 2


class I3CDeclarationsTests(unittest.TestCase):
    def test_i3c_runtime_and_static_inventory(self) -> None:
        test_i3c_runtime_and_static_inventory()

    def test_i3c_committed_authority_vectors(self) -> None:
        test_i3c_committed_authority_vectors()

    def test_i3c_settlement_causality_repair_supplemental_vectors(self) -> None:
        test_i3c_settlement_causality_repair_supplemental_vectors()


if __name__ == "__main__":
    unittest.main()
