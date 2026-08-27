"""Exact, policy-free I-2 numerical substrate."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import gcd
import re
from typing import Protocol, TypeAlias, runtime_checkable

from .canonical import ECJ1Value
from .errors import (
    Applicability,
    FailureCode,
    FailureEnvelope,
    FailureInterfaceRef,
    FailureStage,
    _fail,
)
from .identity import ObjectRef


_HEX64_RE = re.compile(r"[0-9a-f]{16}", re.ASCII)


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef("ebu_framework.numeric", name, "1.0.0")


def _failure(code: FailureCode, interface: str, summary: str) -> "NoReturn":
    _fail(
        code,
        summary,
        stage=FailureStage.I2,
        interface_ref=_interface(interface),
    )


from typing import NoReturn  # noqa: E402


class NumericalVariant(StrEnum):
    INTEGER = "INTEGER"
    RATIONAL = "RATIONAL"
    DECIMAL = "DECIMAL"
    BINARY64_BITS = "BINARY64_BITS"


class NumericalOperation(StrEnum):
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    NEGATE = "NEGATE"
    COMPARE = "COMPARE"


class ExactConversion(StrEnum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    INTEGER_DIVISION_TO_RATIONAL = "INTEGER_DIVISION_TO_RATIONAL"
    DECIMAL_TO_RATIONAL = "DECIMAL_TO_RATIONAL"


class Completeness(StrEnum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"


@dataclass(frozen=True, slots=True, order=True)
class IntegerV1:
    value: int

    def __post_init__(self) -> None:
        if type(self.value) is not int:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "IntegerV1",
                "IntegerV1 requires an exact built-in integer",
            )

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {"value": self.value, "variant": "INTEGER_V1"}


@dataclass(frozen=True, slots=True, order=True)
class RationalV1:
    numerator: IntegerV1
    denominator: IntegerV1

    def __post_init__(self) -> None:
        if type(self.numerator) is not IntegerV1 or type(self.denominator) is not IntegerV1:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "RationalV1",
                "rational fields require exact IntegerV1 values",
            )
        numerator = self.numerator.value
        denominator = self.denominator.value
        if denominator == 0:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "RationalV1",
                "a rational denominator cannot be zero",
            )
        if numerator == 0:
            numerator, denominator = 0, 1
        else:
            if denominator < 0:
                numerator, denominator = -numerator, -denominator
            divisor = gcd(abs(numerator), denominator)
            numerator //= divisor
            denominator //= divisor
        object.__setattr__(self, "numerator", IntegerV1(numerator))
        object.__setattr__(self, "denominator", IntegerV1(denominator))

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "denominator": self.denominator.value,
            "numerator": self.numerator.value,
            "variant": "RATIONAL_V1",
        }


@dataclass(frozen=True, slots=True, order=True)
class DecimalV1:
    coefficient: IntegerV1
    exponent10: IntegerV1

    def __post_init__(self) -> None:
        if type(self.coefficient) is not IntegerV1 or type(self.exponent10) is not IntegerV1:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "DecimalV1",
                "decimal fields require exact IntegerV1 values",
            )
        coefficient = self.coefficient.value
        exponent = self.exponent10.value
        if coefficient == 0:
            exponent = 0
        else:
            while coefficient % 10 == 0:
                coefficient //= 10
                exponent += 1
        object.__setattr__(self, "coefficient", IntegerV1(coefficient))
        object.__setattr__(self, "exponent10", IntegerV1(exponent))

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "coefficient": self.coefficient.value,
            "exponent10": self.exponent10.value,
            "variant": "DECIMAL_V1",
        }


@dataclass(frozen=True, slots=True, order=True)
class Binary64BitsV1:
    bits: str

    def __post_init__(self) -> None:
        if type(self.bits) is not str or _HEX64_RE.fullmatch(self.bits) is None:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "Binary64BitsV1",
                "binary64 bits require exactly sixteen lowercase hexadecimal digits",
            )
        if (int(self.bits, 16) >> 52) & 0x7FF == 0x7FF:
            _failure(
                FailureCode.NONFINITE_NUMBER_FORBIDDEN,
                "Binary64BitsV1",
                "binary64 NaN and infinity encodings are forbidden",
            )

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {"bits": self.bits, "variant": "BINARY64_BITS_V1"}


CoreNumberV1: TypeAlias = IntegerV1 | RationalV1 | DecimalV1 | Binary64BitsV1
_CORE_TYPES = (IntegerV1, RationalV1, DecimalV1, Binary64BitsV1)


def _variant(value: CoreNumberV1) -> NumericalVariant:
    mapping = {
        IntegerV1: NumericalVariant.INTEGER,
        RationalV1: NumericalVariant.RATIONAL,
        DecimalV1: NumericalVariant.DECIMAL,
        Binary64BitsV1: NumericalVariant.BINARY64_BITS,
    }
    try:
        return mapping[type(value)]
    except KeyError:
        _failure(
            FailureCode.CORE_NUMBER_INVALID,
            "normalize_core_number",
            "value is not an exact CoreNumberV1 member",
        )


def _project(value: object) -> ECJ1Value:
    if isinstance(value, StrEnum):
        return value.value
    if type(value) in _CORE_TYPES:
        return value.to_ecj1()  # type: ignore[union-attr]
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[no-any-return,union-attr]
    if type(value) is tuple:
        return [_project(item) for item in value]
    return value  # type: ignore[return-value]


def normalize_core_number(value: CoreNumberV1) -> CoreNumberV1:
    if type(value) is IntegerV1:
        return IntegerV1(value.value)
    if type(value) is RationalV1:
        return RationalV1(value.numerator, value.denominator)
    if type(value) is DecimalV1:
        return DecimalV1(value.coefficient, value.exponent10)
    if type(value) is Binary64BitsV1:
        return Binary64BitsV1(value.bits)
    _failure(
        FailureCode.CORE_NUMBER_INVALID,
        "normalize_core_number",
        "value is not an exact CoreNumberV1 member",
    )


def decimal_to_rational_exact(value: DecimalV1) -> RationalV1:
    if type(value) is not DecimalV1:
        _failure(
            FailureCode.CORE_NUMBER_INVALID,
            "decimal_to_rational_exact",
            "explicit decimal conversion requires DecimalV1",
        )
    coefficient = value.coefficient.value
    exponent = value.exponent10.value
    if exponent >= 0:
        return RationalV1(IntegerV1(coefficient * 10**exponent), IntegerV1(1))
    return RationalV1(IntegerV1(coefficient), IntegerV1(10 ** (-exponent)))


@dataclass(frozen=True, slots=True)
class RuntimeConstraintSet:
    constraint_refs: tuple[ObjectRef, ...]
    applicability: Applicability
    completeness: Completeness

    def __post_init__(self) -> None:
        if type(self.constraint_refs) is not tuple or not all(
            type(reference) is ObjectRef for reference in self.constraint_refs
        ):
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "RuntimeConstraintSet",
                "constraint_refs must be an exact ObjectRef tuple",
            )
        if type(self.applicability) is not Applicability or type(self.completeness) is not Completeness:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "RuntimeConstraintSet",
                "runtime-constraint markers require exact enum values",
            )

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "applicability": self.applicability.value,
            "completeness": self.completeness.value,
            "constraint_refs": [reference.to_ecj1() for reference in self.constraint_refs],
            "schema_version": 1,
        }


def _conditional_ref(value: object) -> bool:
    return type(value) is ObjectRef or type(value) is Applicability


@dataclass(frozen=True, slots=True)
class QuantityContext:
    dimension_ref: ObjectRef
    unit_ref: ObjectRef
    resource_type_ref: ObjectRef | Applicability
    service_type_ref: ObjectRef | Applicability
    region_ref: ObjectRef | Applicability
    time_basis_ref: ObjectRef | Applicability
    sign_convention_ref: ObjectRef | Applicability
    boundary_ref: ObjectRef
    uncertainty_applicability: Applicability

    def __post_init__(self) -> None:
        if type(self.dimension_ref) is not ObjectRef or type(self.unit_ref) is not ObjectRef or type(self.boundary_ref) is not ObjectRef:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "QuantityContext",
                "quantity context requires exact mandatory ObjectRef values",
            )
        if not all(
            _conditional_ref(value)
            for value in (
                self.resource_type_ref,
                self.service_type_ref,
                self.region_ref,
                self.time_basis_ref,
                self.sign_convention_ref,
            )
        ) or type(self.uncertainty_applicability) is not Applicability:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "QuantityContext",
                "quantity context has an invalid conditional coordinate",
            )

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "boundary_ref": self.boundary_ref.to_ecj1(),
            "dimension_ref": self.dimension_ref.to_ecj1(),
            "region_ref": _project(self.region_ref),
            "resource_type_ref": _project(self.resource_type_ref),
            "schema_version": 1,
            "service_type_ref": _project(self.service_type_ref),
            "sign_convention_ref": _project(self.sign_convention_ref),
            "time_basis_ref": _project(self.time_basis_ref),
            "uncertainty_applicability": self.uncertainty_applicability.value,
            "unit_ref": self.unit_ref.to_ecj1(),
        }


@dataclass(frozen=True, slots=True)
class OperandValidationResult:
    operation: NumericalOperation
    operand_variants: tuple[NumericalVariant, ...]
    policy_ref: ObjectRef
    quantity_context: QuantityContext
    valid: bool
    completeness: Completeness
    failure: FailureEnvelope | Applicability

    def __post_init__(self) -> None:
        if type(self.operation) is not NumericalOperation or type(self.operand_variants) is not tuple or not all(
            type(item) is NumericalVariant for item in self.operand_variants
        ) or type(self.policy_ref) is not ObjectRef or type(self.quantity_context) is not QuantityContext:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "OperandValidationResult",
                "operand validation result has invalid field types",
            )
        if type(self.valid) is not bool or type(self.completeness) is not Completeness:
            _failure(
                FailureCode.CORE_NUMBER_INVALID,
                "OperandValidationResult",
                "operand validation result markers must be typed",
            )
        if self.valid:
            valid_relation = self.completeness is Completeness.COMPLETE and self.failure is Applicability.NOT_APPLICABLE
        else:
            valid_relation = type(self.failure) is FailureEnvelope
        if not valid_relation:
            _failure(
                FailureCode.NUMERICAL_POLICY_INCOMPLETE,
                "OperandValidationResult",
                "operand validation result fields are contradictory",
            )

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "completeness": self.completeness.value,
            "failure": _project(self.failure),
            "operand_variants": [item.value for item in self.operand_variants],
            "operation": self.operation.value,
            "policy_ref": self.policy_ref.to_ecj1(),
            "quantity_context": self.quantity_context.to_ecj1(),
            "schema_version": 1,
            "valid": self.valid,
        }


def _number_zero(value: CoreNumberV1) -> bool:
    if type(value) is IntegerV1:
        return value.value == 0
    if type(value) is RationalV1:
        return value.numerator.value == 0
    if type(value) is DecimalV1:
        return value.coefficient.value == 0
    if type(value) is Binary64BitsV1:
        return value.bits in {"0000000000000000", "8000000000000000"}
    return False


def _compare_same_variant(left: CoreNumberV1, right: CoreNumberV1) -> int:
    if type(left) is not type(right):
        raise TypeError("internal mixed exact comparison")
    if type(left) is IntegerV1:
        a, b = left.value, right.value
    elif type(left) is RationalV1:
        a = left.numerator.value * right.denominator.value
        b = right.numerator.value * left.denominator.value
    elif type(left) is DecimalV1:
        exponent = min(left.exponent10.value, right.exponent10.value)
        a = left.coefficient.value * 10 ** (left.exponent10.value - exponent)
        b = right.coefficient.value * 10 ** (right.exponent10.value - exponent)
    else:
        raise TypeError("binary64 comparison requires a policy")
    return (a > b) - (a < b)


@dataclass(frozen=True, slots=True)
class ErrorBound:
    bound_kind: str
    lower: CoreNumberV1 | Applicability
    upper: CoreNumberV1 | Applicability
    unit_ref: ObjectRef | Applicability
    policy_ref: ObjectRef | Applicability
    completeness: Completeness

    def __post_init__(self) -> None:
        interface = "ErrorBound"
        if type(self.bound_kind) is not str or type(self.completeness) is not Completeness:
            _failure(FailureCode.ERROR_BOUND_INVALID, interface, "invalid bound kind or completeness")
        if not _conditional_ref(self.unit_ref) or not _conditional_ref(self.policy_ref):
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "bound applicability must be explicit")
        if self.bound_kind == "EXACT_ZERO":
            if not (
                type(self.lower) is IntegerV1
                and type(self.upper) is IntegerV1
                and self.lower.value == 0
                and self.upper.value == 0
                and self.unit_ref is Applicability.NOT_APPLICABLE
                and self.policy_ref is Applicability.NOT_APPLICABLE
            ):
                _failure(FailureCode.ERROR_BOUND_INVALID, interface, "EXACT_ZERO fields are contradictory")
            return
        kinds = {"ABSOLUTE", "RELATIVE", "ULP", "INTERVAL"}
        if self.bound_kind not in kinds:
            _failure(FailureCode.ERROR_BOUND_INVALID, interface, "unknown error-bound kind")
        if type(self.lower) not in _CORE_TYPES or type(self.upper) not in _CORE_TYPES:
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "nonzero bounds require both endpoints")
        if type(self.lower) is not type(self.upper):
            _failure(
                FailureCode.IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,
                interface,
                "bound endpoints must use one exact variant",
            )
        if self.policy_ref is not Applicability.NOT_APPLICABLE and type(self.policy_ref) is not ObjectRef:
            _failure(FailureCode.NUMERICAL_POLICY_REQUIRED, interface, "bound policy must be explicitly applicable")
        if self.policy_ref is Applicability.NOT_APPLICABLE:
            _failure(FailureCode.NUMERICAL_POLICY_REQUIRED, interface, "nonzero bounds require a policy reference")
        if self.bound_kind in {"ABSOLUTE", "INTERVAL"} and type(self.unit_ref) is not ObjectRef:
            _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "absolute and interval bounds require a unit")
        if type(self.lower) is Binary64BitsV1:
            _failure(FailureCode.NUMERICAL_POLICY_REQUIRED, interface, "binary64 bounds require a domain policy")
        if self.bound_kind in {"RELATIVE", "ULP"} and self.unit_ref is not Applicability.NOT_APPLICABLE:
            _failure(FailureCode.ERROR_BOUND_INVALID, interface, "relative and ULP bounds cannot carry a unit")
        if self.bound_kind == "ULP" and type(self.lower) is not IntegerV1:
            _failure(FailureCode.ERROR_BOUND_INVALID, interface, "ULP bounds require integers")
        zero: CoreNumberV1
        if type(self.lower) is IntegerV1:
            zero = IntegerV1(0)
        elif type(self.lower) is RationalV1:
            zero = RationalV1(IntegerV1(0), IntegerV1(1))
        else:
            zero = DecimalV1(IntegerV1(0), IntegerV1(0))
        if _compare_same_variant(self.lower, zero) < 0 or _compare_same_variant(self.lower, self.upper) > 0:
            _failure(FailureCode.ERROR_BOUND_INVALID, interface, "error-bound endpoints are negative or reversed")

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "bound_kind": self.bound_kind,
            "completeness": self.completeness.value,
            "lower": _project(self.lower),
            "policy_ref": _project(self.policy_ref),
            "schema_version": 1,
            "unit_ref": _project(self.unit_ref),
            "upper": _project(self.upper),
        }


def _exact_zero_bound() -> ErrorBound:
    zero = IntegerV1(0)
    return ErrorBound(
        "EXACT_ZERO",
        zero,
        zero,
        Applicability.NOT_APPLICABLE,
        Applicability.NOT_APPLICABLE,
        Completeness.COMPLETE,
    )


@dataclass(frozen=True, slots=True)
class NumericalResult:
    value: CoreNumberV1
    operation: NumericalOperation
    operand_variants: tuple[NumericalVariant, ...]
    policy_ref: ObjectRef | Applicability
    rounding_evidence_ref: ObjectRef | Applicability
    error_bound: ErrorBound
    completeness: Completeness

    def __post_init__(self) -> None:
        if type(self.value) not in _CORE_TYPES or type(self.operation) is not NumericalOperation or type(self.operand_variants) is not tuple or not all(
            type(item) is NumericalVariant for item in self.operand_variants
        ) or not _conditional_ref(self.policy_ref) or not _conditional_ref(self.rounding_evidence_ref) or type(self.error_bound) is not ErrorBound or type(self.completeness) is not Completeness:
            _failure(FailureCode.CORE_NUMBER_INVALID, "NumericalResult", "numerical result has invalid field types")
        if self.completeness is Completeness.COMPLETE and self.error_bound.completeness is not Completeness.COMPLETE:
            _failure(FailureCode.ERROR_BOUND_INVALID, "NumericalResult", "complete result cannot carry an incomplete bound")
        if self.policy_ref is Applicability.NOT_APPLICABLE and (
            self.rounding_evidence_ref is not Applicability.NOT_APPLICABLE
            or self.error_bound.bound_kind != "EXACT_ZERO"
        ):
            _failure(FailureCode.ERROR_BOUND_INVALID, "NumericalResult", "policy-free results must be exact")

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "completeness": self.completeness.value,
            "error_bound": self.error_bound.to_ecj1(),
            "operand_variants": [item.value for item in self.operand_variants],
            "operation": self.operation.value,
            "policy_ref": _project(self.policy_ref),
            "rounding_evidence_ref": _project(self.rounding_evidence_ref),
            "schema_version": 1,
            "value": _project(self.value),
        }


@dataclass(frozen=True, slots=True)
class ComparisonResult:
    ordering: str
    purpose: str
    policy_ref: ObjectRef | Applicability
    error_bound: ErrorBound | Applicability
    completeness: Completeness

    def __post_init__(self) -> None:
        if type(self.ordering) is not str or self.ordering not in {"LESS", "EQUAL", "GREATER"}:
            _failure(FailureCode.CORE_NUMBER_INVALID, "ComparisonResult", "invalid comparison ordering")
        if type(self.purpose) is not str or self.purpose not in {"EXACT_CORE", "DOMAIN_DECISION", "TOLERANCE_CLASSIFICATION"}:
            _failure(FailureCode.CORE_NUMBER_INVALID, "ComparisonResult", "invalid comparison purpose")
        if not _conditional_ref(self.policy_ref) or not (
            type(self.error_bound) is ErrorBound or type(self.error_bound) is Applicability
        ) or type(self.completeness) is not Completeness:
            _failure(FailureCode.CORE_NUMBER_INVALID, "ComparisonResult", "comparison result has invalid field types")
        if self.purpose == "EXACT_CORE":
            if self.policy_ref is not Applicability.NOT_APPLICABLE or self.error_bound is not Applicability.NOT_APPLICABLE or self.completeness is not Completeness.COMPLETE:
                _failure(FailureCode.ERROR_BOUND_INVALID, "ComparisonResult", "exact comparison fields are contradictory")
        elif type(self.policy_ref) is not ObjectRef or type(self.error_bound) is not ErrorBound:
            _failure(FailureCode.NUMERICAL_POLICY_REQUIRED, "ComparisonResult", "domain comparison requires policy and bound")

    def to_ecj1(self) -> dict[str, ECJ1Value]:
        return {
            "completeness": self.completeness.value,
            "error_bound": _project(self.error_bound),
            "ordering": self.ordering,
            "policy_ref": _project(self.policy_ref),
            "purpose": self.purpose,
            "schema_version": 1,
        }


def _result(operation: NumericalOperation, operands: tuple[CoreNumberV1, ...], value: CoreNumberV1) -> NumericalResult:
    return NumericalResult(
        value,
        operation,
        tuple(_variant(item) for item in operands),
        Applicability.NOT_APPLICABLE,
        Applicability.NOT_APPLICABLE,
        _exact_zero_bound(),
        Completeness.COMPLETE,
    )


def _decimal_add(left: DecimalV1, right: DecimalV1, subtract: bool = False) -> DecimalV1:
    exponent = min(left.exponent10.value, right.exponent10.value)
    left_value = left.coefficient.value * 10 ** (left.exponent10.value - exponent)
    right_value = right.coefficient.value * 10 ** (right.exponent10.value - exponent)
    coefficient = left_value - right_value if subtract else left_value + right_value
    return DecimalV1(IntegerV1(coefficient), IntegerV1(exponent))


def _decimal_divide(left: DecimalV1, right: DecimalV1) -> DecimalV1 | None:
    numerator = left.coefficient.value
    denominator = right.coefficient.value
    divisor = gcd(abs(numerator), abs(denominator))
    numerator //= divisor
    denominator //= divisor
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return None
    places = max(twos, fives)
    coefficient = numerator * 2 ** (places - twos) * 5 ** (places - fives)
    exponent = left.exponent10.value - right.exponent10.value - places
    return DecimalV1(IntegerV1(coefficient), IntegerV1(exponent))


def apply_exact_core_operation(
    operation: NumericalOperation,
    operands: tuple[CoreNumberV1, ...],
    *,
    exact_conversion: ExactConversion = ExactConversion.NOT_APPLICABLE,
) -> NumericalResult | ComparisonResult:
    interface = "apply_exact_core_operation"
    if type(operation) is not NumericalOperation:
        _failure(FailureCode.NUMERICAL_OPERATION_UNSUPPORTED, interface, "operation is outside the closed matrix")
    if type(exact_conversion) is not ExactConversion:
        _failure(FailureCode.NUMERICAL_OPERATION_UNSUPPORTED, interface, "exact conversion marker is invalid")
    expected_arity = 1 if operation is NumericalOperation.NEGATE else 2
    if type(operands) is not tuple or len(operands) != expected_arity:
        _failure(FailureCode.CORE_NUMBER_INVALID, interface, "operation has the wrong operand arity")
    if not all(type(item) in _CORE_TYPES for item in operands):
        _failure(FailureCode.CORE_NUMBER_INVALID, interface, "operands must be exact core-number values")
    normalized = tuple(normalize_core_number(item) for item in operands)
    if normalized != operands:
        _failure(FailureCode.CORE_NUMBER_INVALID, interface, "operands must already be normalized")
    if operation is NumericalOperation.DIVIDE and _number_zero(operands[1]):
        _failure(FailureCode.DIVISION_BY_ZERO, interface, "divisor is mathematical zero")
    variants = tuple(_variant(item) for item in operands)
    if len(set(variants)) != 1:
        _failure(
            FailureCode.IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,
            interface,
            "mixed variants require an explicit external conversion",
        )
    variant = variants[0]
    if variant is NumericalVariant.BINARY64_BITS:
        _failure(FailureCode.NUMERICAL_POLICY_REQUIRED, interface, "binary64 evaluation requires an accepted domain policy")
    nondivisible_integer = (
        operation is NumericalOperation.DIVIDE
        and variant is NumericalVariant.INTEGER
        and operands[0].value % operands[1].value != 0  # type: ignore[union-attr]
    )
    if nondivisible_integer:
        if exact_conversion is not ExactConversion.INTEGER_DIVISION_TO_RATIONAL:
            _failure(
                FailureCode.IMPLICIT_NUMERIC_CONVERSION_FORBIDDEN,
                interface,
                "nondivisible integer division requires explicit rational conversion",
            )
    elif exact_conversion is not ExactConversion.NOT_APPLICABLE:
        _failure(FailureCode.NUMERICAL_OPERATION_UNSUPPORTED, interface, "conversion request is unused or unsupported")

    if operation is NumericalOperation.COMPARE:
        order = _compare_same_variant(operands[0], operands[1])
        return ComparisonResult(
            { -1: "LESS", 0: "EQUAL", 1: "GREATER" }[order],
            "EXACT_CORE",
            Applicability.NOT_APPLICABLE,
            Applicability.NOT_APPLICABLE,
            Completeness.COMPLETE,
        )
    if operation is NumericalOperation.NEGATE:
        value = operands[0]
        if type(value) is IntegerV1:
            answer: CoreNumberV1 = IntegerV1(-value.value)
        elif type(value) is RationalV1:
            answer = RationalV1(IntegerV1(-value.numerator.value), value.denominator)
        else:
            answer = DecimalV1(IntegerV1(-value.coefficient.value), value.exponent10)  # type: ignore[union-attr]
        return _result(operation, operands, answer)

    left, right = operands
    if type(left) is IntegerV1:
        if operation is NumericalOperation.ADD:
            answer = IntegerV1(left.value + right.value)  # type: ignore[union-attr]
        elif operation is NumericalOperation.SUBTRACT:
            answer = IntegerV1(left.value - right.value)  # type: ignore[union-attr]
        elif operation is NumericalOperation.MULTIPLY:
            answer = IntegerV1(left.value * right.value)  # type: ignore[union-attr]
        elif nondivisible_integer:
            answer = RationalV1(left, right)  # type: ignore[arg-type]
        else:
            answer = IntegerV1(left.value // right.value)  # type: ignore[union-attr]
    elif type(left) is RationalV1:
        right_r = right
        if operation is NumericalOperation.ADD:
            numerator = left.numerator.value * right_r.denominator.value + right_r.numerator.value * left.denominator.value  # type: ignore[union-attr]
            denominator = left.denominator.value * right_r.denominator.value  # type: ignore[union-attr]
        elif operation is NumericalOperation.SUBTRACT:
            numerator = left.numerator.value * right_r.denominator.value - right_r.numerator.value * left.denominator.value  # type: ignore[union-attr]
            denominator = left.denominator.value * right_r.denominator.value  # type: ignore[union-attr]
        elif operation is NumericalOperation.MULTIPLY:
            numerator = left.numerator.value * right_r.numerator.value  # type: ignore[union-attr]
            denominator = left.denominator.value * right_r.denominator.value  # type: ignore[union-attr]
        else:
            numerator = left.numerator.value * right_r.denominator.value  # type: ignore[union-attr]
            denominator = left.denominator.value * right_r.numerator.value  # type: ignore[union-attr]
        answer = RationalV1(IntegerV1(numerator), IntegerV1(denominator))
    else:
        right_d = right
        if operation is NumericalOperation.ADD:
            answer = _decimal_add(left, right_d)  # type: ignore[arg-type]
        elif operation is NumericalOperation.SUBTRACT:
            answer = _decimal_add(left, right_d, True)  # type: ignore[arg-type]
        elif operation is NumericalOperation.MULTIPLY:
            answer = DecimalV1(
                IntegerV1(left.coefficient.value * right_d.coefficient.value),  # type: ignore[union-attr]
                IntegerV1(left.exponent10.value + right_d.exponent10.value),  # type: ignore[union-attr]
            )
        else:
            quotient = _decimal_divide(left, right_d)  # type: ignore[arg-type]
            if quotient is None:
                _failure(FailureCode.NUMERICAL_POLICY_REQUIRED, interface, "repeating decimal division requires a policy")
            answer = quotient
    return _result(operation, operands, answer)


@runtime_checkable
class NumericalPolicyV1(Protocol):
    @property
    def policy_ref(self) -> ObjectRef: ...
    @property
    def owning_domain_ref(self) -> ObjectRef: ...
    @property
    def supported_input_variants(self) -> tuple[NumericalVariant, ...]: ...
    @property
    def supported_operations(self) -> tuple[NumericalOperation, ...]: ...
    @property
    def result_variant_by_operation(self) -> tuple[tuple[NumericalOperation, NumericalVariant], ...]: ...
    @property
    def precision_contract_ref(self) -> ObjectRef | Applicability: ...
    @property
    def rounding_contract_ref(self) -> ObjectRef | Applicability: ...
    @property
    def comparison_tolerance_contract_ref(self) -> ObjectRef | Applicability: ...
    @property
    def approximation_contract_ref(self) -> ObjectRef | Applicability: ...
    @property
    def error_bound_contract_ref(self) -> ObjectRef | Applicability: ...
    @property
    def overflow_underflow_nonfinite_contract_ref(self) -> ObjectRef: ...
    @property
    def signed_zero_contract_ref(self) -> ObjectRef | Applicability: ...
    @property
    def backend_dependency_contract_ref(self) -> ObjectRef: ...
    @property
    def cross_platform_contract_ref(self) -> ObjectRef: ...
    @property
    def failure_contract_ref(self) -> ObjectRef: ...
    @property
    def evidence_requirement_refs(self) -> tuple[ObjectRef, ...]: ...
    @property
    def runtime_constraints(self) -> RuntimeConstraintSet: ...
    @property
    def completeness(self) -> Completeness: ...

    def validate_operands(self, operation: NumericalOperation, operands: tuple[CoreNumberV1, ...], quantity_context: QuantityContext) -> OperandValidationResult: ...
    def evaluate(self, operation: NumericalOperation, operands: tuple[CoreNumberV1, ...], quantity_context: QuantityContext) -> NumericalResult: ...
    def compare(self, purpose: str, left: CoreNumberV1, right: CoreNumberV1, quantity_context: QuantityContext) -> ComparisonResult: ...
    def bound_error(self, operation: NumericalOperation, operands: tuple[CoreNumberV1, ...], result: NumericalResult, quantity_context: QuantityContext) -> ErrorBound: ...
    def runtime_requirements(self) -> RuntimeConstraintSet: ...


_POLICY_FIELDS = (
    "policy_ref",
    "owning_domain_ref",
    "supported_input_variants",
    "supported_operations",
    "result_variant_by_operation",
    "precision_contract_ref",
    "rounding_contract_ref",
    "comparison_tolerance_contract_ref",
    "approximation_contract_ref",
    "error_bound_contract_ref",
    "overflow_underflow_nonfinite_contract_ref",
    "signed_zero_contract_ref",
    "backend_dependency_contract_ref",
    "cross_platform_contract_ref",
    "failure_contract_ref",
    "evidence_requirement_refs",
    "runtime_constraints",
    "completeness",
)


def _ordered_unique_refs(values: tuple[ObjectRef, ...]) -> bool:
    keys = tuple(
        (str(item.object_id), str(item.object_version), str(item.object_content_hash))
        for item in values
    )
    return keys == tuple(sorted(keys)) and len(keys) == len(set(keys))


def validate_numerical_policy(policy: NumericalPolicyV1) -> Completeness:
    interface = "validate_numerical_policy"
    missing = object()
    values = {name: getattr(policy, name, missing) for name in _POLICY_FIELDS}
    if any(value is missing for value in values.values()):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "policy declaration omits a required property")
    unconditional_refs = (
        "policy_ref",
        "owning_domain_ref",
        "overflow_underflow_nonfinite_contract_ref",
        "backend_dependency_contract_ref",
        "cross_platform_contract_ref",
        "failure_contract_ref",
    )
    if any(type(values[name]) is not ObjectRef for name in unconditional_refs):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "policy declaration omits an unconditional reference")
    if type(values["precision_contract_ref"]) is not ObjectRef and type(values["precision_contract_ref"]) is not Applicability:
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "precision applicability is not explicit")
    conditional_names = (
        "rounding_contract_ref",
        "comparison_tolerance_contract_ref",
        "approximation_contract_ref",
        "error_bound_contract_ref",
        "signed_zero_contract_ref",
    )
    if any(not _conditional_ref(values[name]) for name in conditional_names):
        _failure(FailureCode.IMPLICIT_ABSENCE_FORBIDDEN, interface, "policy conditional applicability is not explicit")
    variants = values["supported_input_variants"]
    operations = values["supported_operations"]
    result_rows = values["result_variant_by_operation"]
    evidence = values["evidence_requirement_refs"]
    constraints = values["runtime_constraints"]
    declared = values["completeness"]
    complete = True
    complete &= type(values["policy_ref"]) is ObjectRef and values["policy_ref"] != values["owning_domain_ref"]
    complete &= type(variants) is tuple and bool(variants) and all(type(item) is NumericalVariant for item in variants)
    if type(variants) is tuple and all(type(item) is NumericalVariant for item in variants):
        complete &= tuple(variants) == tuple(sorted(set(variants), key=list(NumericalVariant).index))
    complete &= type(operations) is tuple and bool(operations) and all(type(item) is NumericalOperation for item in operations)
    if type(operations) is tuple and all(type(item) is NumericalOperation for item in operations):
        complete &= tuple(operations) == tuple(sorted(set(operations), key=list(NumericalOperation).index))
    complete &= type(result_rows) is tuple and all(
        type(row) is tuple and len(row) == 2 and type(row[0]) is NumericalOperation and type(row[1]) is NumericalVariant
        for row in result_rows
    )
    if type(operations) is tuple and all(type(item) is NumericalOperation for item in operations) and type(result_rows) is tuple:
        expected_ops = tuple(item for item in operations if item is not NumericalOperation.COMPARE)
        complete &= tuple(row[0] for row in result_rows if type(row) is tuple and len(row) == 2) == expected_ops
        complete &= len(result_rows) == len(expected_ops)
        complete &= all(row[1] in variants for row in result_rows if type(row) is tuple and len(row) == 2 and type(variants) is tuple)
    complete &= type(values["precision_contract_ref"]) is ObjectRef
    binary = type(variants) is tuple and NumericalVariant.BINARY64_BITS in variants
    compare = type(operations) is tuple and NumericalOperation.COMPARE in operations
    if binary:
        complete &= type(values["rounding_contract_ref"]) is ObjectRef
        complete &= type(values["approximation_contract_ref"]) is ObjectRef
        complete &= type(values["error_bound_contract_ref"]) is ObjectRef
        complete &= type(values["signed_zero_contract_ref"]) is ObjectRef
    else:
        complete &= values["signed_zero_contract_ref"] is Applicability.NOT_APPLICABLE
    if compare:
        complete &= type(values["comparison_tolerance_contract_ref"]) is ObjectRef
    complete &= type(evidence) is tuple and bool(evidence) and all(type(item) is ObjectRef for item in evidence)
    if type(evidence) is tuple and all(type(item) is ObjectRef for item in evidence):
        complete &= _ordered_unique_refs(evidence)
    complete &= type(constraints) is RuntimeConstraintSet
    if type(constraints) is RuntimeConstraintSet:
        if constraints.applicability is Applicability.APPLICABLE:
            complete &= bool(constraints.constraint_refs) and _ordered_unique_refs(constraints.constraint_refs)
            complete &= constraints.completeness is Completeness.COMPLETE
        else:
            complete &= not constraints.constraint_refs and constraints.completeness is Completeness.COMPLETE
    complete &= type(declared) is Completeness
    if declared is Completeness.INCOMPLETE and complete:
        return Completeness.INCOMPLETE
    if not complete or declared is not Completeness.COMPLETE:
        _failure(FailureCode.NUMERICAL_POLICY_INCOMPLETE, interface, "numerical policy declaration is structurally incomplete")
    return Completeness.COMPLETE


__all__ = (
    "Binary64BitsV1",
    "ComparisonResult",
    "Completeness",
    "CoreNumberV1",
    "DecimalV1",
    "ErrorBound",
    "ExactConversion",
    "IntegerV1",
    "NumericalOperation",
    "NumericalPolicyV1",
    "NumericalResult",
    "NumericalVariant",
    "OperandValidationResult",
    "QuantityContext",
    "RationalV1",
    "RuntimeConstraintSet",
    "apply_exact_core_operation",
    "decimal_to_rational_exact",
    "normalize_core_number",
    "validate_numerical_policy",
)
