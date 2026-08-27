"""Optional immutable I-3 conservation declarations and pure T0 checks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import json
from typing import Literal, NoReturn, TypeAlias

from .primitives import (
    Quantity,
    ResolutionDetail,
    ResolutionState,
)
from .numeric import (
    Binary64BitsV1,
    CoreNumberV1,
    DecimalV1,
    IntegerV1,
    RationalV1,
)
from .identity import ObjectRef
from .envelopes import CommonObjectEnvelope, validate_object_envelope
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureObjectRef,
    FailureStage,
    FrameworkError,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)


_CORE_NUMBER_TYPES = (IntegerV1, RationalV1, DecimalV1, Binary64BitsV1)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.conservation", name, "1.0.0")


def _failure(
    code: FailureCode,
    interface: str,
    *,
    summary: str | None = None,
    object_ref: FailureObjectRef | None = None,
) -> NoReturn:
    _fail(
        code,
        summary or f"{interface} rejected {code.value}",
        stage=FailureStage.I3,
        interface_ref=_interface(interface),
        object_refs=() if object_ref is None else (object_ref,),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.I3_RECORD_FORMATION_INVALID, interface)


def _strict_formation(cls: type) -> type:
    generated_init = cls.__init__

    def strict_init(self: object, *args: object, **kwargs: object) -> None:
        expected_fields = set(cls.__dataclass_fields__)  # type: ignore[attr-defined]
        if args or set(kwargs) != expected_fields:
            _formation_failure(cls.__name__)
        generated_init(self, **kwargs)

    strict_init.__wrapped__ = generated_init  # type: ignore[attr-defined]
    cls.__init__ = strict_init  # type: ignore[method-assign]
    return cls


def _object_or_applicability(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


def _object_ref_tuple(value: object) -> bool:
    return type(value) is tuple and all(type(item) is ObjectRef for item in value)


def _ref_key(reference: ObjectRef) -> tuple[str, str, str]:
    return (
        str(reference.object_id),
        str(reference.object_version),
        str(reference.object_content_hash),
    )


def _project(value: object) -> object:
    if type(value) is Applicability:
        return value.value
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if isinstance(value, StrEnum):
        return value.value
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _projection_bytes(value: object) -> bytes:
    return json.dumps(
        _project(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


class ConservationAccountLevel(StrEnum):
    REDUCED_REPRESENTED_STOCK = "REDUCED_REPRESENTED_STOCK"
    OPEN_CONTROL_VOLUME = "OPEN_CONTROL_VOLUME"
    ISOLATED_BOUNDARY_COMPLETE = "ISOLATED_BOUNDARY_COMPLETE"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("ConservationAccountLevel")


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ConservationProfile:
    envelope: CommonObjectEnvelope
    account_level: ConservationAccountLevel
    boundary_ref: ObjectRef
    parent_boundary_ref: ObjectRef | Applicability
    physical_state_schema_ref: ObjectRef
    conserved_quantities: tuple[ConservedQuantityDeclaration, ...]
    transformation_declarations: tuple[
        InternalTransformationOrInvariantDeclaration, ...
    ]
    boundary_flow_channels: tuple[BoundaryFlowChannelDeclaration, ...]
    evidence: ConservationEvidence
    residual_expectation: ResidualExpectation
    policy_memory_applicability: Applicability
    nonclaim_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.envelope) is CommonObjectEnvelope
            and type(self.account_level) is ConservationAccountLevel
            and type(self.boundary_ref) is ObjectRef
            and _object_or_applicability(self.parent_boundary_ref)
            and type(self.physical_state_schema_ref) is ObjectRef
            and type(self.conserved_quantities) is tuple
            and all(
                type(item) is ConservedQuantityDeclaration
                for item in self.conserved_quantities
            )
            and type(self.transformation_declarations) is tuple
            and all(
                type(item) is InternalTransformationOrInvariantDeclaration
                for item in self.transformation_declarations
            )
            and type(self.boundary_flow_channels) is tuple
            and all(
                type(item) is BoundaryFlowChannelDeclaration
                for item in self.boundary_flow_channels
            )
            and type(self.evidence) is ConservationEvidence
            and type(self.residual_expectation)
            in (ExactResidualExpectation, UncertaintyAwareResidualExpectation)
            and type(self.policy_memory_applicability) is Applicability
            and _object_ref_tuple(self.nonclaim_refs)
        ):
            _formation_failure("ConservationProfile")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "account_level": self.account_level.value,
            "boundary_ref": self.boundary_ref.to_ecj1(),
            "parent_boundary_ref": _project(self.parent_boundary_ref),
            "physical_state_schema_ref": self.physical_state_schema_ref.to_ecj1(),
            "conserved_quantities": [
                item.to_ecj1() for item in self.conserved_quantities
            ],
            "transformation_declarations": [
                item.to_ecj1() for item in self.transformation_declarations
            ],
            "boundary_flow_channels": [
                item.to_ecj1() for item in self.boundary_flow_channels
            ],
            "evidence": self.evidence.to_ecj1(),
            "residual_expectation": self.residual_expectation.to_ecj1(),
            "policy_memory_applicability": self.policy_memory_applicability.value,
            "nonclaim_refs": [item.to_ecj1() for item in self.nonclaim_refs],
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ConservationProfileSelection:
    applicability: Applicability
    profile_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.applicability) is Applicability
            and _object_ref_tuple(self.profile_refs)
        ):
            _formation_failure("ConservationProfileSelection")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "applicability": self.applicability.value,
            "profile_refs": [item.to_ecj1() for item in self.profile_refs],
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ConservedQuantityDeclaration:
    quantity_ref: ObjectRef
    unit_ref: ObjectRef
    dimension_ref: ObjectRef
    coordinate_coefficients: tuple[CoordinateCoefficient, ...]
    explicit_loss_channel_refs: tuple[ObjectRef, ...]
    explicit_outflow_channel_refs: tuple[ObjectRef, ...]
    unresolved_channel_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.quantity_ref) is ObjectRef
            and type(self.unit_ref) is ObjectRef
            and type(self.dimension_ref) is ObjectRef
            and type(self.coordinate_coefficients) is tuple
            and all(
                type(item) is CoordinateCoefficient
                for item in self.coordinate_coefficients
            )
            and _object_ref_tuple(self.explicit_loss_channel_refs)
            and _object_ref_tuple(self.explicit_outflow_channel_refs)
            and _object_ref_tuple(self.unresolved_channel_refs)
        ):
            _formation_failure("ConservedQuantityDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "quantity_ref": self.quantity_ref.to_ecj1(),
            "unit_ref": self.unit_ref.to_ecj1(),
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "coordinate_coefficients": [
                item.to_ecj1() for item in self.coordinate_coefficients
            ],
            "explicit_loss_channel_refs": [
                item.to_ecj1() for item in self.explicit_loss_channel_refs
            ],
            "explicit_outflow_channel_refs": [
                item.to_ecj1() for item in self.explicit_outflow_channel_refs
            ],
            "unresolved_channel_refs": [
                item.to_ecj1() for item in self.unresolved_channel_refs
            ],
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class CoordinateCoefficient:
    coordinate_ref: ObjectRef
    coefficient: CoreNumberV1
    unit_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.coordinate_ref) is ObjectRef
            and type(self.coefficient) in _CORE_NUMBER_TYPES
            and type(self.unit_ref) is ObjectRef
        ):
            _formation_failure("CoordinateCoefficient")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "coordinate_ref": self.coordinate_ref.to_ecj1(),
            "coefficient": self.coefficient.to_ecj1(),
            "unit_ref": self.unit_ref.to_ecj1(),
        }


class TransformationDeclarationKind(StrEnum):
    INTERNAL_TRANSFORMATION_MAP = "INTERNAL_TRANSFORMATION_MAP"
    DECLARED_INVARIANT = "DECLARED_INVARIANT"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("TransformationDeclarationKind")


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class InternalTransformationOrInvariantDeclaration:
    declaration_ref: ObjectRef
    declaration_kind: TransformationDeclarationKind
    quantity_refs: tuple[ObjectRef, ...]
    coordinate_refs: tuple[ObjectRef, ...]
    contract_ref: ObjectRef
    evidence_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.declaration_ref) is ObjectRef
            and type(self.declaration_kind) is TransformationDeclarationKind
            and _object_ref_tuple(self.quantity_refs)
            and _object_ref_tuple(self.coordinate_refs)
            and type(self.contract_ref) is ObjectRef
            and _object_ref_tuple(self.evidence_refs)
        ):
            _formation_failure(
                "InternalTransformationOrInvariantDeclaration"
            )

    def to_ecj1(self) -> dict[str, object]:
        return {
            "declaration_ref": self.declaration_ref.to_ecj1(),
            "declaration_kind": self.declaration_kind.value,
            "quantity_refs": [item.to_ecj1() for item in self.quantity_refs],
            "coordinate_refs": [
                item.to_ecj1() for item in self.coordinate_refs
            ],
            "contract_ref": self.contract_ref.to_ecj1(),
            "evidence_refs": [item.to_ecj1() for item in self.evidence_refs],
        }


class BoundaryFlowDirection(StrEnum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"
    ZERO_EXCHANGE = "ZERO_EXCHANGE"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("BoundaryFlowDirection")


class BoundaryFlowRollupRole(StrEnum):
    EXTERNAL_BOUNDARY = "EXTERNAL_BOUNDARY"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    EXPLICIT_LOSS = "EXPLICIT_LOSS"
    EXPLICIT_UNRESOLVED = "EXPLICIT_UNRESOLVED"

    @classmethod
    def _missing_(cls, value: object) -> NoReturn:
        _formation_failure("BoundaryFlowRollupRole")


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class BoundaryFlowChannelDeclaration:
    channel_ref: ObjectRef
    quantity_ref: ObjectRef
    unit_ref: ObjectRef
    direction: BoundaryFlowDirection
    sign_convention_ref: ObjectRef
    rollup_role: BoundaryFlowRollupRole
    source_boundary_ref: ObjectRef | Applicability
    target_boundary_ref: ObjectRef | Applicability
    observability: ResolutionDetail
    explicit_zero_exchange: bool

    def __post_init__(self) -> None:
        if not (
            type(self.channel_ref) is ObjectRef
            and type(self.quantity_ref) is ObjectRef
            and type(self.unit_ref) is ObjectRef
            and type(self.direction) is BoundaryFlowDirection
            and type(self.sign_convention_ref) is ObjectRef
            and type(self.rollup_role) is BoundaryFlowRollupRole
            and _object_or_applicability(self.source_boundary_ref)
            and _object_or_applicability(self.target_boundary_ref)
            and type(self.observability) is ResolutionDetail
            and type(self.explicit_zero_exchange) is bool
        ):
            _formation_failure("BoundaryFlowChannelDeclaration")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "channel_ref": self.channel_ref.to_ecj1(),
            "quantity_ref": self.quantity_ref.to_ecj1(),
            "unit_ref": self.unit_ref.to_ecj1(),
            "direction": self.direction.value,
            "sign_convention_ref": self.sign_convention_ref.to_ecj1(),
            "rollup_role": self.rollup_role.value,
            "source_boundary_ref": _project(self.source_boundary_ref),
            "target_boundary_ref": _project(self.target_boundary_ref),
            "observability": self.observability.to_ecj1(),
            "explicit_zero_exchange": self.explicit_zero_exchange,
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ConservationEvidence:
    observability_resolution: ResolutionDetail
    boundary_completeness_evidence_refs: tuple[ObjectRef, ...]
    carrier_completeness_evidence_refs: tuple[ObjectRef, ...]
    zero_exchange_evidence_refs: tuple[ObjectRef, ...]
    unresolved_channel_refs: tuple[ObjectRef, ...]
    nonclaim_refs: tuple[ObjectRef, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.observability_resolution) is ResolutionDetail
            and _object_ref_tuple(self.boundary_completeness_evidence_refs)
            and _object_ref_tuple(self.carrier_completeness_evidence_refs)
            and _object_ref_tuple(self.zero_exchange_evidence_refs)
            and _object_ref_tuple(self.unresolved_channel_refs)
            and _object_ref_tuple(self.nonclaim_refs)
        ):
            _formation_failure("ConservationEvidence")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "observability_resolution": self.observability_resolution.to_ecj1(),
            "boundary_completeness_evidence_refs": [
                item.to_ecj1()
                for item in self.boundary_completeness_evidence_refs
            ],
            "carrier_completeness_evidence_refs": [
                item.to_ecj1()
                for item in self.carrier_completeness_evidence_refs
            ],
            "zero_exchange_evidence_refs": [
                item.to_ecj1() for item in self.zero_exchange_evidence_refs
            ],
            "unresolved_channel_refs": [
                item.to_ecj1() for item in self.unresolved_channel_refs
            ],
            "nonclaim_refs": [item.to_ecj1() for item in self.nonclaim_refs],
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class ExactResidualExpectation:
    expected_residual: Quantity
    comparison_rule: Literal["EXACT_EQUALITY"]

    def __post_init__(self) -> None:
        if not (
            type(self.expected_residual) is Quantity
            and type(self.comparison_rule) is str
            and self.comparison_rule == "EXACT_EQUALITY"
        ):
            _formation_failure("ExactResidualExpectation")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "expected_residual": self.expected_residual.to_ecj1(),
            "comparison_rule": self.comparison_rule,
        }


@_strict_formation
@dataclass(
    frozen=True,
    slots=True,
    eq=True,
    order=False,
    unsafe_hash=False,
    kw_only=True,
)
class UncertaintyAwareResidualExpectation:
    expected_residual: Quantity
    uncertainty_ref: ObjectRef
    numerical_policy_ref: ObjectRef
    tolerance_ref: ObjectRef | Applicability
    comparison_rule_ref: ObjectRef

    def __post_init__(self) -> None:
        if not (
            type(self.expected_residual) is Quantity
            and type(self.uncertainty_ref) is ObjectRef
            and type(self.numerical_policy_ref) is ObjectRef
            and _object_or_applicability(self.tolerance_ref)
            and type(self.comparison_rule_ref) is ObjectRef
        ):
            _formation_failure("UncertaintyAwareResidualExpectation")

    def to_ecj1(self) -> dict[str, object]:
        return {
            "expected_residual": self.expected_residual.to_ecj1(),
            "uncertainty_ref": self.uncertainty_ref.to_ecj1(),
            "numerical_policy_ref": self.numerical_policy_ref.to_ecj1(),
            "tolerance_ref": _project(self.tolerance_ref),
            "comparison_rule_ref": self.comparison_rule_ref.to_ecj1(),
        }


ResidualExpectation: TypeAlias = (
    ExactResidualExpectation | UncertaintyAwareResidualExpectation
)


def _failure_object(profile: ConservationProfile) -> FailureObjectRef:
    envelope = profile.envelope
    return FailureObjectRef(
        object_id=str(envelope.object_id),
        object_version=str(envelope.object_version),
        object_content_hash=str(envelope.object_content_hash),
    )


def _object_content_check(profile: ConservationProfile) -> None:
    stored = profile.envelope.to_ecj1()["object_content_payload"]
    if stored != profile.to_ecj1():
        interface = "validate_conservation_profile"
        _failure(
            FailureCode.I3_OBJECT_CONTENT_MISMATCH,
            interface,
            summary=(
                f"{interface} rejected I3_OBJECT_CONTENT_MISMATCH "
                "at argument 1 (profile)"
            ),
            object_ref=_failure_object(profile),
        )


def _ordered_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return keys == tuple(sorted(keys))


def _duplicate_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(_ref_key(item) for item in values)
    return len(keys) != len(set(keys))


def _embedded_key(value: object, first_ref: ObjectRef) -> tuple[object, ...]:
    return _ref_key(first_ref), _projection_bytes(value)


def _ordered_embedded(values: tuple[object, ...], field: str) -> bool:
    first_field = {
        "conserved_quantities": "quantity_ref",
        "transformation_declarations": "declaration_ref",
        "boundary_flow_channels": "channel_ref",
        "coordinate_coefficients": "coordinate_ref",
    }[field]
    keys = tuple(
        _embedded_key(item, getattr(item, first_field)) for item in values
    )
    return keys == tuple(sorted(keys))


def _duplicate_embedded(values: tuple[object, ...]) -> bool:
    projections = tuple(_projection_bytes(item) for item in values)
    return len(projections) != len(set(projections))


def _all_ref_collections(
    profile: ConservationProfile,
) -> tuple[tuple[ObjectRef, ...], ...]:
    collections: list[tuple[ObjectRef, ...]] = [profile.nonclaim_refs]
    for quantity in profile.conserved_quantities:
        collections.extend(
            (
                quantity.explicit_loss_channel_refs,
                quantity.explicit_outflow_channel_refs,
                quantity.unresolved_channel_refs,
            )
        )
    for declaration in profile.transformation_declarations:
        collections.extend(
            (
                declaration.quantity_refs,
                declaration.coordinate_refs,
                declaration.evidence_refs,
            )
        )
    evidence = profile.evidence
    collections.extend(
        (
            evidence.boundary_completeness_evidence_refs,
            evidence.carrier_completeness_evidence_refs,
            evidence.zero_exchange_evidence_refs,
            evidence.unresolved_channel_refs,
            evidence.nonclaim_refs,
        )
    )
    return tuple(collections)


def _collections_ordered(profile: ConservationProfile) -> bool:
    if not all(_ordered_refs(values) for values in _all_ref_collections(profile)):
        return False
    if not _ordered_embedded(
        profile.conserved_quantities, "conserved_quantities"
    ):
        return False
    if not _ordered_embedded(
        profile.transformation_declarations, "transformation_declarations"
    ):
        return False
    if not _ordered_embedded(
        profile.boundary_flow_channels, "boundary_flow_channels"
    ):
        return False
    return all(
        _ordered_embedded(
            quantity.coordinate_coefficients, "coordinate_coefficients"
        )
        for quantity in profile.conserved_quantities
    )


def _collections_duplicated(profile: ConservationProfile) -> bool:
    if any(_duplicate_refs(values) for values in _all_ref_collections(profile)):
        return True
    if any(
        _duplicate_embedded(values)
        for values in (
            profile.conserved_quantities,
            profile.transformation_declarations,
            profile.boundary_flow_channels,
        )
    ):
        return True
    return any(
        _duplicate_embedded(quantity.coordinate_coefficients)
        for quantity in profile.conserved_quantities
    )


def _object_hash_matches(profile: ConservationProfile) -> bool:
    try:
        validate_object_envelope(profile.envelope)
    except FrameworkError:
        return False
    return True


def validate_conservation_profile_selection(
    selection: ConservationProfileSelection,
    /,
) -> None:
    if type(selection) is not ConservationProfileSelection:
        _formation_failure("ConservationProfileSelection")
    if (
        selection.applicability is Applicability.APPLICABLE
        and not selection.profile_refs
    ) or (
        selection.applicability is Applicability.NOT_APPLICABLE
        and selection.profile_refs
    ):
        _failure(
            FailureCode.IMPLICIT_ABSENCE_FORBIDDEN,
            "validate_conservation_profile_selection",
        )
    if not _ordered_refs(selection.profile_refs):
        _failure(
            FailureCode.I3_COLLECTION_ORDER_INVALID,
            "validate_conservation_profile_selection",
        )
    if _duplicate_refs(selection.profile_refs):
        _failure(
            FailureCode.I3_DUPLICATE_MEMBER,
            "validate_conservation_profile_selection",
        )
    return None


def _exact_nonzero_external(channel: BoundaryFlowChannelDeclaration) -> bool:
    return (
        channel.rollup_role is BoundaryFlowRollupRole.EXTERNAL_BOUNDARY
        and channel.direction
        in (BoundaryFlowDirection.INFLOW, BoundaryFlowDirection.OUTFLOW)
        and not channel.explicit_zero_exchange
    )


def _exact_external_inflow(channel: BoundaryFlowChannelDeclaration) -> bool:
    return (
        _exact_nonzero_external(channel)
        and channel.direction is BoundaryFlowDirection.INFLOW
    )


def _exact_external_outflow(channel: BoundaryFlowChannelDeclaration) -> bool:
    return (
        _exact_nonzero_external(channel)
        and channel.direction is BoundaryFlowDirection.OUTFLOW
    )


def _exact_zero_external(channel: BoundaryFlowChannelDeclaration) -> bool:
    return (
        channel.rollup_role is BoundaryFlowRollupRole.EXTERNAL_BOUNDARY
        and channel.direction is BoundaryFlowDirection.ZERO_EXCHANGE
        and channel.explicit_zero_exchange
    )


def _malformed_external(channel: BoundaryFlowChannelDeclaration) -> bool:
    return (
        channel.rollup_role is BoundaryFlowRollupRole.EXTERNAL_BOUNDARY
        and not _exact_nonzero_external(channel)
        and not _exact_zero_external(channel)
    )


def _profile_invalid_row(profile: ConservationProfile) -> str | None:
    if (
        type(profile.parent_boundary_ref) is ObjectRef
        and profile.parent_boundary_ref == profile.boundary_ref
    ):
        return "DIRECT_SELF_PARENT"
    if any(
        channel.rollup_role is BoundaryFlowRollupRole.INTERNAL_TRANSFER
        and not (
            type(channel.source_boundary_ref) is ObjectRef
            and type(channel.target_boundary_ref) is ObjectRef
            and channel.source_boundary_ref != channel.target_boundary_ref
        )
        for channel in profile.boundary_flow_channels
    ):
        return "C08"
    if (
        profile.account_level is ConservationAccountLevel.OPEN_CONTROL_VOLUME
        and any(
            _exact_zero_external(channel)
            for channel in profile.boundary_flow_channels
        )
    ):
        return "C13"
    return None


def _level_requirement_row(profile: ConservationProfile) -> str | None:
    if not profile.conserved_quantities:
        return "C01"
    if any(
        not declaration.coordinate_coefficients
        for declaration in profile.conserved_quantities
    ):
        return "C02"
    if profile.account_level in (
        ConservationAccountLevel.OPEN_CONTROL_VOLUME,
        ConservationAccountLevel.ISOLATED_BOUNDARY_COMPLETE,
    ) and not profile.boundary_flow_channels:
        return "C04"
    if (
        profile.account_level is ConservationAccountLevel.OPEN_CONTROL_VOLUME
        and not any(
            _exact_nonzero_external(channel)
            for channel in profile.boundary_flow_channels
        )
    ):
        return "C05"
    if (
        profile.account_level
        is ConservationAccountLevel.ISOLATED_BOUNDARY_COMPLETE
        and not any(
            _exact_zero_external(channel)
            for channel in profile.boundary_flow_channels
        )
    ):
        return "C14"
    return None


def _evidence_requirement_row(profile: ConservationProfile) -> str | None:
    if profile.account_level not in (
        ConservationAccountLevel.OPEN_CONTROL_VOLUME,
        ConservationAccountLevel.ISOLATED_BOUNDARY_COMPLETE,
    ):
        return None
    evidence = profile.evidence
    if not evidence.boundary_completeness_evidence_refs:
        return "C16"
    if not evidence.carrier_completeness_evidence_refs:
        return "C17"
    if (
        profile.account_level
        is ConservationAccountLevel.ISOLATED_BOUNDARY_COMPLETE
        and not evidence.zero_exchange_evidence_refs
    ):
        return "C18"
    if (
        evidence.observability_resolution.state is not ResolutionState.PRESENT
        or evidence.observability_resolution.missing_part_refs
    ):
        return "C19"
    if profile.account_level is ConservationAccountLevel.OPEN_CONTROL_VOLUME:
        quantity_unresolved = sorted(
            _ref_key(reference)
            for declaration in profile.conserved_quantities
            for reference in declaration.unresolved_channel_refs
        )
        evidence_unresolved = sorted(
            _ref_key(reference)
            for reference in evidence.unresolved_channel_refs
        )
        if quantity_unresolved != evidence_unresolved:
            return "C20"
        outflow_keys = {
            _ref_key(channel.channel_ref)
            for channel in profile.boundary_flow_channels
            if channel.direction is BoundaryFlowDirection.OUTFLOW
        }
        if any(
            _ref_key(reference) not in outflow_keys
            for declaration in profile.conserved_quantities
            for reference in declaration.explicit_outflow_channel_refs
        ):
            return "C21"
        loss_keys = {
            _ref_key(channel.channel_ref)
            for channel in profile.boundary_flow_channels
            if channel.rollup_role is BoundaryFlowRollupRole.EXPLICIT_LOSS
        }
        if any(
            _ref_key(reference) not in loss_keys
            for declaration in profile.conserved_quantities
            for reference in declaration.explicit_loss_channel_refs
        ):
            return "C22"
    return None


def _isolation_invalid_row(profile: ConservationProfile) -> str | None:
    if (
        profile.account_level
        is not ConservationAccountLevel.ISOLATED_BOUNDARY_COMPLETE
    ):
        return None
    channels = profile.boundary_flow_channels
    if any(_exact_external_inflow(channel) for channel in channels):
        return "C06"
    if any(_exact_external_outflow(channel) for channel in channels):
        return "C07"
    if any(
        channel.rollup_role is BoundaryFlowRollupRole.EXPLICIT_LOSS
        for channel in channels
    ):
        return "C09"
    if any(
        channel.rollup_role is BoundaryFlowRollupRole.EXPLICIT_UNRESOLVED
        for channel in channels
    ):
        return "C10"
    if any(
        declaration.unresolved_channel_refs
        for declaration in profile.conserved_quantities
    ):
        return "C11"
    if profile.evidence.unresolved_channel_refs:
        return "C12"
    if any(_malformed_external(channel) for channel in channels):
        return "C15"
    if any(
        declaration.explicit_outflow_channel_refs
        for declaration in profile.conserved_quantities
    ):
        return "C23"
    if any(
        declaration.explicit_loss_channel_refs
        for declaration in profile.conserved_quantities
    ):
        return "C24"
    return None


def validate_conservation_profile(profile: ConservationProfile, /) -> None:
    if type(profile) is not ConservationProfile:
        _formation_failure("ConservationProfile")
    _object_content_check(profile)

    invalid_applicability = profile.parent_boundary_ref is Applicability.APPLICABLE
    for channel in profile.boundary_flow_channels:
        invalid_applicability = invalid_applicability or (
            channel.source_boundary_ref is Applicability.APPLICABLE
            or channel.target_boundary_ref is Applicability.APPLICABLE
        )
    if type(profile.residual_expectation) is UncertaintyAwareResidualExpectation:
        invalid_applicability = invalid_applicability or (
            profile.residual_expectation.tolerance_ref
            is Applicability.APPLICABLE
        )
    if invalid_applicability:
        _failure(
            FailureCode.IMPLICIT_ABSENCE_FORBIDDEN,
            "validate_conservation_profile",
        )

    if not _collections_ordered(profile):
        _failure(
            FailureCode.I3_COLLECTION_ORDER_INVALID,
            "validate_conservation_profile",
        )
    if _collections_duplicated(profile):
        _failure(
            FailureCode.I3_DUPLICATE_MEMBER,
            "validate_conservation_profile",
        )

    if _profile_invalid_row(profile) is not None:
        _failure(
            FailureCode.CONSERVATION_PROFILE_INVALID,
            "validate_conservation_profile",
        )

    quantity_keys = tuple(
        _ref_key(item.quantity_ref) for item in profile.conserved_quantities
    )
    if len(quantity_keys) != len(set(quantity_keys)):
        _failure(
            FailureCode.CONSERVATION_QUANTITY_DUPLICATE,
            "validate_conservation_profile",
        )

    if any(
        len(
            keys := tuple(
                _ref_key(coefficient.coordinate_ref)
                for coefficient in declaration.coordinate_coefficients
            )
        )
        != len(set(keys))
        for declaration in profile.conserved_quantities
    ):
        _failure(
            FailureCode.CONSERVATION_COORDINATE_DUPLICATE,
            "validate_conservation_profile",
        )

    channel_keys = tuple(
        _ref_key(item.channel_ref) for item in profile.boundary_flow_channels
    )
    if len(channel_keys) != len(set(channel_keys)):
        _failure(
            FailureCode.CONSERVATION_FLOW_CHANNEL_DUPLICATE,
            "validate_conservation_profile",
        )

    if any(
        coefficient.unit_ref != declaration.unit_ref
        for declaration in profile.conserved_quantities
        for coefficient in declaration.coordinate_coefficients
    ):
        _failure(
            FailureCode.CONSERVATION_UNIT_MISMATCH,
            "validate_conservation_profile",
        )

    if _level_requirement_row(profile) is not None:
        _failure(
            FailureCode.CONSERVATION_LEVEL_REQUIREMENT_MISSING,
            "validate_conservation_profile",
        )

    if _evidence_requirement_row(profile) is not None:
        _failure(
            FailureCode.CONSERVATION_EVIDENCE_INCOMPLETE,
            "validate_conservation_profile",
        )

    if _isolation_invalid_row(profile) is not None:
        _failure(
            FailureCode.CONSERVATION_ISOLATION_INVALID,
            "validate_conservation_profile",
        )

    if (
        type(profile.residual_expectation)
        is UncertaintyAwareResidualExpectation
        and profile.residual_expectation.tolerance_ref
        is Applicability.NOT_APPLICABLE
    ):
        _failure(
            FailureCode.CONSERVATION_TOLERANCE_UNDECLARED,
            "validate_conservation_profile",
        )

    if not _object_hash_matches(profile):
        _failure(FailureCode.HASH_MISMATCH, "validate_conservation_profile")
    return None


__all__ = (
    "ConservationAccountLevel",
    "ConservationProfile",
    "ConservationProfileSelection",
    "ConservedQuantityDeclaration",
    "CoordinateCoefficient",
    "TransformationDeclarationKind",
    "InternalTransformationOrInvariantDeclaration",
    "BoundaryFlowDirection",
    "BoundaryFlowRollupRole",
    "BoundaryFlowChannelDeclaration",
    "ConservationEvidence",
    "ExactResidualExpectation",
    "UncertaintyAwareResidualExpectation",
    "ResidualExpectation",
    "validate_conservation_profile_selection",
    "validate_conservation_profile",
)
