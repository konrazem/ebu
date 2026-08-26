"""Inert declarations for closed-loop correction diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NoReturn
import unicodedata

from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureStage,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)
from .identity import ObjectRef, SemanticVersion
from .numeric import RationalV1
from .primitives import ClaimStatus


_REQUIRED_OUTPUTS = (
    "TRAJECTORIES_AND_EQUILIBRIA",
    "SPECTRA_OR_ROOTS",
    "DAMPING_FREQUENCY_PERIOD_VISIBILITY",
    "PEAK_OVERSHOOT",
    "RECOVERY_TIME",
    "DELAY_SENSITIVITY_AND_MARGIN",
    "CORRECTION_ACTION_RESOURCE_COST_OR_WORK",
    "TRAJECTORY_DIFFERENCE",
    "RECEIPT_RESIDUAL_DEPENDENCY_AND_CLOSURE",
    "NUMERICAL_ERRORS_FAILURES_AND_UNRESOLVED_EVIDENCE",
)
_MANDATORY_NONCLAIMS = (
    "NO_UNIVERSAL_CONTROLLER",
    "NO_PERFECT_EFFICIENCY",
    "NO_AUTOMATIC_TOPOLOGY",
    "NO_AUTOMATIC_CAUSAL_ATTRIBUTION",
    "NO_AUTOMATIC_SETTLEMENT",
    "NO_PHYSICAL_WAVE",
    "NO_ELECTRICAL_VOLTAGE",
    "NO_SCIENTIFIC_EXECUTION",
)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef(
        "ebu_framework.correction_protocol", name, "1.0.0"
    )


def _failure(code: FailureCode, interface: str) -> NoReturn:
    _fail(
        code,
        f"{interface} rejected {code.value}",
        stage=FailureStage.STATIC_AND_SYNTHETIC_VALIDATION,
        interface_ref=_interface(interface),
        scientific_status_effect=ScientificStatusEffect.UNSTARTED_PRESERVED,
        retry_class=RetryClass.FORBIDDEN,
    )


def _formation_failure(interface: str) -> NoReturn:
    _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)


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


def _visible_ascii(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and value.isascii()
        and unicodedata.normalize("NFC", value) == value
        and all(0x20 < ord(character) < 0x7F for character in value)
    )


def _string_tuple(value: object, *, nonempty: bool = False) -> bool:
    return (
        type(value) is tuple
        and (bool(value) or not nonempty)
        and all(_visible_ascii(item) for item in value)
        and len(value) == len(set(value))
    )


class ClosedLoopModelClass(StrEnum):
    CONTINUOUS_LINEAR = "CONTINUOUS_LINEAR"
    CONTINUOUS_NONLINEAR = "CONTINUOUS_NONLINEAR"
    DISCRETE_IMMEDIATE = "DISCRETE_IMMEDIATE"
    DISCRETE_ONE_STEP_DELAY = "DISCRETE_ONE_STEP_DELAY"
    DECLARED_EXTENSION = "DECLARED_EXTENSION"


class CorrectionDiagnosticClaimStatus(StrEnum):
    STATIC_CONTROL = "STATIC_CONTROL"
    MODEL_EXACT_UNDER_DECLARATION = "MODEL_EXACT_UNDER_DECLARATION"
    PREREGISTERED_HYPOTHESIS = "PREREGISTERED_HYPOTHESIS"
    EMPIRICALLY_SUPPORTED_WITHIN_PROTOCOL = "EMPIRICALLY_SUPPORTED_WITHIN_PROTOCOL"
    FALSIFIED_WITHIN_PROTOCOL = "FALSIFIED_WITHIN_PROTOCOL"
    UNRESOLVED = "UNRESOLVED"


class ContinuousFeedbackRegime(StrEnum):
    ASYMPTOTICALLY_STABLE_REAL_DECAY = "ASYMPTOTICALLY_STABLE_REAL_DECAY"
    ASYMPTOTICALLY_STABLE_DAMPED_OSCILLATION = (
        "ASYMPTOTICALLY_STABLE_DAMPED_OSCILLATION"
    )
    PERSISTENT_UNDAMPED_OSCILLATION_BOUNDARY = (
        "PERSISTENT_UNDAMPED_OSCILLATION_BOUNDARY"
    )
    UNSTABLE_GROWING_OSCILLATION = "UNSTABLE_GROWING_OSCILLATION"
    UNSTABLE_GROWING_REAL = "UNSTABLE_GROWING_REAL"
    SADDLE_INSTABILITY = "SADDLE_INSTABILITY"
    NONASYMPTOTIC_BOUNDARY = "NONASYMPTOTIC_BOUNDARY"


class DiscreteFeedbackRegime(StrEnum):
    IMMEDIATE_MONOTONE_DECAY = "IMMEDIATE_MONOTONE_DECAY"
    IMMEDIATE_DEADBEAT = "IMMEDIATE_DEADBEAT"
    IMMEDIATE_ALTERNATING_DECAY = "IMMEDIATE_ALTERNATING_DECAY"
    DELAYED_REAL_DECAY = "DELAYED_REAL_DECAY"
    DELAYED_CRITICAL_DECAY = "DELAYED_CRITICAL_DECAY"
    DELAYED_DAMPED_OSCILLATION = "DELAYED_DAMPED_OSCILLATION"
    PERSISTENT_BOUNDARY = "PERSISTENT_BOUNDARY"
    UNSTABLE = "UNSTABLE"


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class RationalMatrix:
    rows: tuple[tuple[RationalV1, ...], ...]

    def __post_init__(self) -> None:
        if (
            type(self.rows) is not tuple
            or not self.rows
            or any(type(row) is not tuple or not row for row in self.rows)
            or any(type(value) is not RationalV1 for row in self.rows for value in row)
            or len({len(row) for row in self.rows}) != 1
        ):
            _failure(FailureCode.CLCD_MATRIX_SHAPE_INVALID, "RationalMatrix")


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class CoordinateConjugacyDeclaration:
    action_ids: tuple[str, ...]
    subset_order: tuple[tuple[str, ...], ...]
    zeta: RationalMatrix
    mobius: RationalMatrix
    extent_basis_ref: ObjectRef
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            _string_tuple(self.action_ids, nonempty=True)
            and type(self.subset_order) is tuple
            and self.subset_order
            and all(
                type(subset) is tuple
                and all(type(item) is str and item in self.action_ids for item in subset)
                and len(subset) == len(set(subset))
                for subset in self.subset_order
            )
            and len(self.subset_order) == len(set(self.subset_order))
            and type(self.zeta) is RationalMatrix
            and type(self.mobius) is RationalMatrix
            and type(self.extent_basis_ref) is ObjectRef
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(
                FailureCode.CLCD_COORDINATE_BASIS_INCOMPLETE,
                "CoordinateConjugacyDeclaration",
            )


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class FeedbackBlockDeclaration:
    a: RationalMatrix
    b: RationalMatrix
    c: RationalMatrix
    d: RationalMatrix
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            all(type(value) is RationalMatrix for value in (self.a, self.b, self.c, self.d))
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(FailureCode.CLCD_FEEDBACK_BLOCK_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class FeedbackPathResult:
    bc: RationalMatrix
    first_nonzero_order: int | Applicability
    first_nonzero_operator: RationalMatrix | Applicability
    tested_through_order: int

    def __post_init__(self) -> None:
        absent = (
            self.first_nonzero_order is Applicability.NOT_APPLICABLE
            and self.first_nonzero_operator is Applicability.NOT_APPLICABLE
        )
        present = (
            type(self.first_nonzero_order) is int
            and 1 <= self.first_nonzero_order <= self.tested_through_order
            and type(self.first_nonzero_operator) is RationalMatrix
        )
        if not (
            type(self.bc) is RationalMatrix
            and type(self.tested_through_order) is int
            and self.tested_through_order > 0
            and (absent or present)
        ):
            _failure(FailureCode.CLCD_FEEDBACK_PATH_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class ContinuousFeedbackDeclaration:
    a: RationalV1
    d: RationalV1
    b: RationalV1
    k: RationalV1
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            all(type(value) is RationalV1 for value in (self.a, self.d, self.b, self.k))
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class ContinuousFeedbackResult:
    s: RationalV1
    q: RationalV1
    discriminant: RationalV1
    regime: ContinuousFeedbackRegime

    def __post_init__(self) -> None:
        if not (
            all(type(value) is RationalV1 for value in (self.s, self.q, self.discriminant))
            and type(self.regime) is ContinuousFeedbackRegime
        ):
            _failure(FailureCode.CLCD_STABILITY_CLASSIFICATION_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class DiscreteFeedbackDeclaration:
    model_class: ClosedLoopModelClass
    kappa: RationalV1
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            type(self.model_class) is ClosedLoopModelClass
            and self.model_class
            in {
                ClosedLoopModelClass.DISCRETE_IMMEDIATE,
                ClosedLoopModelClass.DISCRETE_ONE_STEP_DELAY,
            }
            and type(self.kappa) is RationalV1
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(FailureCode.CLCD_DELAY_CLASSIFICATION_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class DiscreteFeedbackResult:
    immediate_root: RationalV1 | Applicability
    discriminant: RationalV1 | Applicability
    root_modulus_squared: RationalV1 | Applicability
    regime: DiscreteFeedbackRegime

    def __post_init__(self) -> None:
        if not (
            all(type(value) in {RationalV1, Applicability} for value in (self.immediate_root, self.discriminant, self.root_modulus_squared))
            and type(self.regime) is DiscreteFeedbackRegime
        ):
            _failure(FailureCode.CLCD_DELAY_CLASSIFICATION_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class ObservabilityDeclaration:
    observation: RationalMatrix
    modes: tuple[RationalMatrix, ...]
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            type(self.observation) is RationalMatrix
            and type(self.modes) is tuple
            and self.modes
            and all(type(mode) is RationalMatrix for mode in self.modes)
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(FailureCode.CLCD_OBSERVABILITY_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class ObservabilityResult:
    visible: tuple[bool, ...]
    projected_modes: tuple[RationalMatrix, ...]

    def __post_init__(self) -> None:
        if not (
            type(self.visible) is tuple
            and type(self.projected_modes) is tuple
            and len(self.visible) == len(self.projected_modes)
            and all(type(value) is bool for value in self.visible)
            and all(type(value) is RationalMatrix for value in self.projected_modes)
        ):
            _failure(FailureCode.CLCD_OBSERVABILITY_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class CorrectionClosureDeclaration:
    stock_change: RationalV1
    boundary_in: RationalV1
    boundary_out: RationalV1
    generation: RationalV1
    consumption: RationalV1
    residual: RationalV1
    internal_transfers: tuple[tuple[RationalV1, RationalV1], ...]
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        values = (
            self.stock_change,
            self.boundary_in,
            self.boundary_out,
            self.generation,
            self.consumption,
            self.residual,
        )
        if not (
            all(type(value) is RationalV1 for value in values)
            and type(self.internal_transfers) is tuple
            and all(
                type(pair) is tuple
                and len(pair) == 2
                and all(type(value) is RationalV1 for value in pair)
                and pair[0] == pair[1]
                for pair in self.internal_transfers
            )
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(FailureCode.CLCD_CORRECTION_CLOSURE_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class CorrectionClosureResult:
    closure_rhs: RationalV1
    closes: bool
    internal_transfers_cancel: bool

    def __post_init__(self) -> None:
        if not (
            type(self.closure_rhs) is RationalV1
            and type(self.closes) is bool
            and type(self.internal_transfers_cancel) is bool
        ):
            _failure(FailureCode.CLCD_CORRECTION_CLOSURE_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyGraphDeclaration:
    vertices: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    corrected_vertex: str
    inventory_complete: bool
    claim_status: ClaimStatus

    def __post_init__(self) -> None:
        if not (
            _string_tuple(self.vertices, nonempty=True)
            and type(self.edges) is tuple
            and len(self.edges) == len(set(self.edges))
            and all(
                type(edge) is tuple
                and len(edge) == 2
                and all(type(vertex) is str and vertex in self.vertices for vertex in edge)
                and edge[0] != edge[1]
                for edge in self.edges
            )
            and type(self.corrected_vertex) is str
            and self.corrected_vertex in self.vertices
            and type(self.inventory_complete) is bool
            and type(self.claim_status) is ClaimStatus
        ):
            _failure(FailureCode.CLCD_DEPENDENCY_GRAPH_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class DependencyInvalidationResult:
    descendants: tuple[str, ...]
    topological_order: tuple[str, ...]

    def __post_init__(self) -> None:
        if not (
            _string_tuple(self.descendants)
            and _string_tuple(self.topological_order)
            and set(self.descendants) == set(self.topological_order)
        ):
            _failure(FailureCode.CLCD_DEPENDENCY_GRAPH_INVALID, type(self).__name__)


@_strict_formation
@dataclass(frozen=True, slots=True, kw_only=True)
class ClosedLoopCorrectionProtocol:
    protocol_ref: ObjectRef
    protocol_version: SemanticVersion
    model_class: ClosedLoopModelClass
    physical_state_ref: ObjectRef
    scientific_state_ref: ObjectRef
    correction_state_ref: ObjectRef
    units_and_signs_ref: ObjectRef
    boundary_ref: ObjectRef
    clock_and_horizon_ref: ObjectRef
    initial_state_domain_ref: ObjectRef
    parameter_domain_ref: ObjectRef
    uncorrected_dynamics_ref: ObjectRef
    corrected_dynamics_ref: ObjectRef
    coordinate_contract_ref: ObjectRef | Applicability
    embedding_ref: ObjectRef
    projection_ref: ObjectRef
    observation_ref: ObjectRef
    correction_law_ref: ObjectRef
    delay_model_ref: ObjectRef
    constraint_and_saturation_ref: ObjectRef
    numerical_method_ref: ObjectRef
    precision_and_tolerance_ref: ObjectRef
    required_outputs: tuple[str, ...]
    falsifiers: tuple[str, ...]
    correction_lifecycle_ref: ObjectRef
    closure_contract_ref: ObjectRef
    dependency_contract_ref: ObjectRef
    claim_status: CorrectionDiagnosticClaimStatus
    nonclaims: tuple[str, ...]

    def __post_init__(self) -> None:
        refs = (
            self.protocol_ref,
            self.physical_state_ref,
            self.scientific_state_ref,
            self.correction_state_ref,
            self.units_and_signs_ref,
            self.boundary_ref,
            self.clock_and_horizon_ref,
            self.initial_state_domain_ref,
            self.parameter_domain_ref,
            self.uncorrected_dynamics_ref,
            self.corrected_dynamics_ref,
            self.embedding_ref,
            self.projection_ref,
            self.observation_ref,
            self.correction_law_ref,
            self.delay_model_ref,
            self.constraint_and_saturation_ref,
            self.numerical_method_ref,
            self.precision_and_tolerance_ref,
            self.correction_lifecycle_ref,
            self.closure_contract_ref,
            self.dependency_contract_ref,
        )
        if not (
            all(type(value) is ObjectRef for value in refs)
            and type(self.protocol_version) is SemanticVersion
            and type(self.model_class) is ClosedLoopModelClass
            and type(self.coordinate_contract_ref) in {ObjectRef, Applicability}
            and _string_tuple(self.required_outputs, nonempty=True)
            and _string_tuple(self.falsifiers, nonempty=True)
            and type(self.claim_status) is CorrectionDiagnosticClaimStatus
            and _string_tuple(self.nonclaims, nonempty=True)
        ):
            _formation_failure(type(self).__name__)


def validate_closed_loop_correction_protocol(
    declaration: ClosedLoopCorrectionProtocol, /
) -> ClosedLoopCorrectionProtocol:
    if type(declaration) is not ClosedLoopCorrectionProtocol:
        _formation_failure("validate_closed_loop_correction_protocol")
    if (
        declaration.required_outputs != _REQUIRED_OUTPUTS
        or declaration.nonclaims != _MANDATORY_NONCLAIMS
        or declaration.coordinate_contract_ref is Applicability.APPLICABLE
    ):
        _failure(
            FailureCode.CLCD_PROTOCOL_INCOMPLETE,
            "validate_closed_loop_correction_protocol",
        )
    return declaration


__all__ = (
    "ClosedLoopModelClass",
    "CorrectionDiagnosticClaimStatus",
    "ContinuousFeedbackRegime",
    "DiscreteFeedbackRegime",
    "RationalMatrix",
    "CoordinateConjugacyDeclaration",
    "FeedbackBlockDeclaration",
    "FeedbackPathResult",
    "ContinuousFeedbackDeclaration",
    "ContinuousFeedbackResult",
    "DiscreteFeedbackDeclaration",
    "DiscreteFeedbackResult",
    "ObservabilityDeclaration",
    "ObservabilityResult",
    "CorrectionClosureDeclaration",
    "CorrectionClosureResult",
    "DependencyGraphDeclaration",
    "DependencyInvalidationResult",
    "ClosedLoopCorrectionProtocol",
    "validate_closed_loop_correction_protocol",
)
