"""SD-03 exact-rational oracle adapter - Atomic generator and finite EBU chain.

PROSPECTIVE. SD-03 is registered in
``stage_d_scientific_validation_master_matrix.json`` with status
``PROSPECTIVE_STAGE_E_THEOREM_NUMERICAL_THEN_STAGE_F_REGISTERED_STATIC_STUDY``
and the matrix itself carries ``PROSPECTIVE_NO_EXECUTION_NO_OUTCOMES``. This
module implements the adapter the matrix names as missing - "future Stage E
exact-rational oracle adapter" - and nothing else. It registers no study,
adopts no parameter, and runs no case.

WHAT SD-03 ASKS. Whether the declared chain

    V -> mu = grad V -> f_e -> Psi_e -> J_e -> G_T -> finite EBU

preserves units, boundaries, derivatives, generator semantics and accounting
"without treating any intermediate as the final score". Seven projections per
case; 192 registered cases; 1,344 evaluations.

EXACT RATIONAL ARITHMETIC, EVERYWHERE. Every value here is a
``fractions.Fraction``. The registered uncertainty rule is "all registered
values and comparisons are reduced-rational exact; tolerance and floating
substitution are forbidden", and ``stochastic_rules`` is ``FORBIDDEN``. This
module therefore REFUSES a ``float`` input rather than converting it: an
exactly representable float would pass silently and a non-representable one
would import a rounding error into an exact study. There is no tolerance
parameter anywhere and no comparison is approximate.

FOUR PROJECTIONS ARE COMPUTABLE. THREE ARE NOT. This is the central finding of
building the adapter, and it is a registration gap, not an implementation gap:

  V           computable  - the six potentials are registered in
                            configuration.parameters
  MU          computable  - registered as "mu=grad V"; taken here by EXACT
                            symbolic differentiation of the polynomial, not by
                            any difference quotient
  G_T         computable  - the generator authority defines G_T by
                            T_h(z) = z + h*G_T(z) + o(h); SD-03 declares
                            T_h(x)_i = x_i + h*(-1)^i/(i+1) exactly, with
                            o(h) identically zero, so G_T(x)_i = (-1)^i/(i+1)
  FINITE_EBU  computable  - the registered comparator "direct finite
                            potential difference". It is the INTERIOR
                            difference only and is boundary-mode independent;
                            the declared boundary term is a separate ledger
                            entry in ``accounting_ledger``

  F, PSI, J   REFUSED     - defined in this repository only on the EDGE
                            model, in Foundation_v2.7_math.md:
                              (2.3) Psi(J) =
                                    sum_e [J_e^2/(2 M_e) + theta_e J_e]
                              (2.6) J_e = M_e [f_e - theta_e]_+
                                    with f_e = mu_i - eta_e mu_j
                            f_e needs an EDGE (two endpoints) and eta_e;
                            Psi_e needs M_e and theta_e; J_e needs all of
                            them. SD-03's registered configuration declares
                            dimensions, potentials, action extents and
                            boundary modes - NO edge set, NO eta, NO mobility
                            and NO threshold - so none of the three is
                            evaluable on an SD-03 case.

``project`` raises ``UnregisteredProjection`` for those three rather than
supplying a stand-in. Substituting an edge law that SD-03 does not declare
would be choosing physics, and the registered falsifier "chain value differs
from its independent definition" is exactly what that would trip.

NO INTERMEDIATE IS THE SCORE. The registered falsifier "an intermediate is
reported as the final finite EBU" is enforced structurally: ``ChainValue``
carries its projection name, and ``finite_ebu_of`` accepts only a value whose
name is ``FINITE_EBU``. An intermediate cannot be passed off as the result by
accident.

EXECUTION SAFETY. Import-pure. No tick, trajectory, runner, simulation, world,
model state, network, Docker, AWS or external service. It imports only
``fractions``, ``hashlib``, ``itertools``, ``json``, ``dataclasses`` and
``typing``, and no project module. It does not execute the 192 registered
cases: ``registered_cases`` returns case IDENTIFIERS and evaluates nothing.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Mapping, Optional, Sequence

__all__ = [
    "SD03_STUDY_ID", "CHAIN_PROJECTIONS", "COMPUTABLE_PROJECTIONS",
    "UNREGISTERED_PROJECTIONS", "REGISTERED_CASE_COUNT",
    "REGISTERED_EVALUATION_COUNT", "REGISTERED_POTENTIAL_TEXT",
    "BASE_UNITS", "Unit", "DIMENSIONLESS", "STATE", "POTENTIAL",
    "ACTION_EXTENT", "Quantity", "Polynomial", "SD03Case", "SD03Configuration",
    "ChainValue", "AccountingLedger", "OracleError", "UnitMismatch",
    "UnregisteredProjection", "InexactInput", "ConfigurationRefused",
    "exact", "potential_polynomial", "displacement", "initial_state",
    "load_sd03_configuration", "registered_cases", "project",
    "chain_projections", "accounting_ledger", "finite_ebu_of",
    "integrated_generator_chain", "comparator_agreement",
]

SD03_STUDY_ID = "SD-03"

# SHA-256 of the canonical matrix bytes (git blob
# e6cd44f8b9e2e125403cb1359d819fc08afd2cb7). The adapter refuses any other
# file: the case structure must come from the registered matrix, never from
# this module.
SD03_MATRIX_SHA256 = (
    "081f2e994c23051514aef19a0516d1996d9c4b86cd528dfc05bf9d17658bdb81")

# The seven projections, in the order the matrix's owners.equations lists
# them. primary_evaluations_per_run is 7 and 192 * 7 = 1,344.
CHAIN_PROJECTIONS = ("V", "MU", "F", "PSI", "J", "G_T", "FINITE_EBU")
COMPUTABLE_PROJECTIONS = ("V", "MU", "G_T", "FINITE_EBU")
UNREGISTERED_PROJECTIONS = ("F", "PSI", "J")

REGISTERED_CASE_COUNT = 192
REGISTERED_EVALUATION_COUNT = 1344

# The registered potential text, verbatim from configuration.parameters. Each
# implementation below is bound to its own line and fails closed if the matrix
# text ever changes, so the formulas are implemented-and-checked rather than
# restated.
REGISTERED_POTENTIAL_TEXT = {
    "V0": "V0=0",
    "V1": "V1=sum(i+1)*x_i",
    "V2": "V2=sum(i+1)*x_i^2",
    "V3": "V3=sum_{i<j}(i+1)(j+1)*x_i*x_j",
    "V4": "V4=sum(i+1)*x_i^3",
    "V5": "V5=(1+sum x_i)^4",
}


class OracleError(ValueError):
    """Base class. Every failure mode here fails closed."""


class InexactInput(OracleError):
    """A value that is not exactly rational reached an exact computation."""


class UnitMismatch(OracleError):
    """Two quantities with different declared units were combined."""


class UnregisteredProjection(OracleError):
    """A chain projection no committed authority defines for SD-03."""


class ConfigurationRefused(OracleError):
    """The supplied matrix is not the registered one, or is malformed."""


def exact(value) -> Fraction:
    """Coerce to ``Fraction``, refusing anything not exactly rational.

    ``float`` is refused rather than converted. An exactly representable float
    would convert silently and a non-representable one would carry a rounding
    error into a study whose registered uncertainty rule forbids tolerance and
    floating substitution outright. ``bool`` is refused because ``True`` would
    otherwise become the state value 1.
    """
    if isinstance(value, bool):
        raise InexactInput(f"bool is not a state value, got {value!r}")
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        raise InexactInput(
            f"float {value!r} refused: SD-03 registers 'tolerance and "
            "floating substitution are forbidden'. Pass Fraction or int.")
    if isinstance(value, str):
        try:
            return Fraction(value)
        except (ValueError, ZeroDivisionError) as error:
            raise InexactInput(f"{value!r} is not an exact rational: {error}")
    raise InexactInput(f"cannot make {value!r} exactly rational")


# --------------------------------------------------------------------------
# declared units - exact integer exponent vectors, no conversion factors
# --------------------------------------------------------------------------
# The five units the matrix declares for SD-03 are: declared state units,
# potential-unit, potential-unit/state-unit, action-extent-unit, EBU-unit.
# Three are independent bases and "potential-unit/state-unit" is derived.
#
# EBU-unit is NOT a base here, and that is a disclosed gap rather than a
# decision: the matrix declares both "potential-unit" and "EBU-unit" but
# registers no identification between them. The finite value is therefore
# carried in potential-unit and never relabelled. Registering the
# identification is a prerequisite in the readiness document; inventing a
# conversion factor here would be the same error this module refuses for
# f_e, Psi_e and J_e.
BASE_UNITS = ("state", "potential", "action_extent")


@dataclass(frozen=True)
class Unit:
    """An exact exponent vector over ``BASE_UNITS``. No numeric factor."""
    exponents: tuple

    def __post_init__(self):
        if len(self.exponents) != len(BASE_UNITS):
            raise UnitMismatch(
                f"a unit needs one exponent per base {BASE_UNITS}")
        for value in self.exponents:
            if not isinstance(value, int) or isinstance(value, bool):
                raise UnitMismatch("unit exponents must be plain ints")

    def __mul__(self, other: "Unit") -> "Unit":
        return Unit(tuple(a + b for a, b in
                          zip(self.exponents, other.exponents)))

    def __truediv__(self, other: "Unit") -> "Unit":
        return Unit(tuple(a - b for a, b in
                          zip(self.exponents, other.exponents)))

    def power(self, n: int) -> "Unit":
        if not isinstance(n, int) or isinstance(n, bool):
            raise UnitMismatch("a unit power must be a plain int")
        return Unit(tuple(a * n for a in self.exponents))

    def __str__(self) -> str:
        parts = [f"{name}^{power}" for name, power
                 in zip(BASE_UNITS, self.exponents) if power]
        return "*".join(parts) if parts else "dimensionless"


DIMENSIONLESS = Unit((0, 0, 0))
STATE = Unit((1, 0, 0))
POTENTIAL = Unit((0, 1, 0))
ACTION_EXTENT = Unit((0, 0, 1))


@dataclass(frozen=True)
class Quantity:
    """An exact rational value carrying a declared unit.

    Addition and subtraction refuse a unit mismatch. That refusal IS the
    registered negative control "unit mismatch refuses"; it is not a
    convenience check and there is no permissive mode.
    """
    value: Fraction
    unit: Unit

    def __post_init__(self):
        object.__setattr__(self, "value", exact(self.value))
        if not isinstance(self.unit, Unit):
            raise UnitMismatch("a Quantity needs a declared Unit")

    def _require_same(self, other: "Quantity", operation: str) -> None:
        if not isinstance(other, Quantity):
            raise UnitMismatch(f"cannot {operation} a Quantity and "
                               f"{type(other).__name__}")
        if self.unit != other.unit:
            raise UnitMismatch(
                f"cannot {operation} {self.unit} and {other.unit}: SD-03 "
                "registers 'unit mismatch refuses'")

    def __add__(self, other: "Quantity") -> "Quantity":
        self._require_same(other, "add")
        return Quantity(self.value + other.value, self.unit)

    def __sub__(self, other: "Quantity") -> "Quantity":
        self._require_same(other, "subtract")
        return Quantity(self.value - other.value, self.unit)

    def __mul__(self, other: "Quantity") -> "Quantity":
        if not isinstance(other, Quantity):
            raise UnitMismatch("multiply Quantity by Quantity only")
        return Quantity(self.value * other.value, self.unit * other.unit)

    def __neg__(self) -> "Quantity":
        return Quantity(-self.value, self.unit)

    def __str__(self) -> str:
        return f"{self.value} [{self.unit}]"


# --------------------------------------------------------------------------
# exact multivariate polynomials - the derivative link, done symbolically
# --------------------------------------------------------------------------
class Polynomial:
    """An exact multivariate polynomial over ``Fraction`` in ``d`` variables.

    Terms map an exponent tuple to a coefficient; zero coefficients are
    dropped, so equality is structural and ``V0 = 0`` really is the empty
    polynomial.

    Differentiation is SYMBOLIC. SD-03's chain link is "mu = grad V", and a
    difference quotient - however small the step - would answer SD-04's
    question about truncation instead of SD-03's question about the
    derivative. No step size appears anywhere in this class.
    """

    __slots__ = ("dimension", "terms")

    def __init__(self, dimension: int, terms: Optional[Mapping] = None):
        if not isinstance(dimension, int) or isinstance(dimension, bool) \
                or dimension < 1:
            raise OracleError(f"dimension must be a positive int, got "
                              f"{dimension!r}")
        self.dimension = dimension
        cleaned = {}
        for exponents, coefficient in (terms or {}).items():
            key = tuple(exponents)
            if len(key) != dimension:
                raise OracleError(
                    f"exponent tuple {key} does not match dimension "
                    f"{dimension}")
            for power in key:
                if not isinstance(power, int) or isinstance(power, bool) \
                        or power < 0:
                    raise OracleError(
                        f"exponents must be non-negative ints, got {key}")
            value = exact(coefficient)
            if value:
                cleaned[key] = cleaned.get(key, Fraction(0)) + value
        self.terms = {k: v for k, v in cleaned.items() if v}

    @classmethod
    def zero(cls, dimension: int) -> "Polynomial":
        return cls(dimension, {})

    @classmethod
    def constant(cls, dimension: int, value) -> "Polynomial":
        return cls(dimension, {(0,) * dimension: exact(value)})

    @classmethod
    def variable(cls, dimension: int, index: int) -> "Polynomial":
        if not isinstance(index, int) or isinstance(index, bool) \
                or not 0 <= index < dimension:
            raise OracleError(f"variable index {index!r} out of range for "
                              f"dimension {dimension}")
        exponents = [0] * dimension
        exponents[index] = 1
        return cls(dimension, {tuple(exponents): Fraction(1)})

    def _require_same_dimension(self, other: "Polynomial") -> None:
        if not isinstance(other, Polynomial):
            raise OracleError("operand must be a Polynomial")
        if other.dimension != self.dimension:
            raise OracleError(
                f"dimension mismatch: {self.dimension} vs {other.dimension}")

    def __add__(self, other: "Polynomial") -> "Polynomial":
        self._require_same_dimension(other)
        merged = dict(self.terms)
        for key, value in other.terms.items():
            merged[key] = merged.get(key, Fraction(0)) + value
        return Polynomial(self.dimension, merged)

    def __mul__(self, other: "Polynomial") -> "Polynomial":
        self._require_same_dimension(other)
        merged = {}
        for left, a in self.terms.items():
            for right, b in other.terms.items():
                key = tuple(x + y for x, y in zip(left, right))
                merged[key] = merged.get(key, Fraction(0)) + a * b
        return Polynomial(self.dimension, merged)

    def scaled(self, factor) -> "Polynomial":
        value = exact(factor)
        return Polynomial(self.dimension,
                          {k: v * value for k, v in self.terms.items()})

    def power(self, n: int) -> "Polynomial":
        if not isinstance(n, int) or isinstance(n, bool) or n < 0:
            raise OracleError(f"polynomial power must be >= 0, got {n!r}")
        result = Polynomial.constant(self.dimension, 1)
        for _ in range(n):
            result = result * self
        return result

    def partial_derivative(self, index: int) -> "Polynomial":
        """Exact symbolic d/dx_index. No step size, no quotient."""
        if not isinstance(index, int) or isinstance(index, bool) \
                or not 0 <= index < self.dimension:
            raise OracleError(f"derivative index {index!r} out of range")
        derived = {}
        for exponents, coefficient in self.terms.items():
            power = exponents[index]
            if power == 0:
                continue
            key = list(exponents)
            key[index] = power - 1
            derived[tuple(key)] = coefficient * power
        return Polynomial(self.dimension, derived)

    def along_affine_path(self, point: Sequence,
                          direction: Sequence) -> "Polynomial":
        """Restrict to ``t -> self(point + t*direction)``, exactly.

        Returns a univariate polynomial in ``t``. Every coefficient is a
        Fraction: substituting an affine path into a polynomial is exact
        algebra, with no sampling and no step size.
        """
        base = [exact(v) for v in point]
        step = [exact(v) for v in direction]
        if len(base) != self.dimension or len(step) != self.dimension:
            raise OracleError(
                f"point and direction must have length {self.dimension}")
        result = Polynomial.zero(1)
        for exponents, coefficient in self.terms.items():
            term = Polynomial.constant(1, coefficient)
            for index, power in enumerate(exponents):
                if not power:
                    continue
                linear = Polynomial(1, {(0,): base[index],
                                        (1,): step[index]})
                term = term * linear.power(power)
            result = result + term
        return result

    def integrate_unit_interval(self) -> Fraction:
        """Exact ``int_0^1 self(t) dt`` for a univariate polynomial.

        Term by term: ``int_0^1 t^k dt = 1/(k+1)``. This is exact symbolic
        integration of a polynomial, NOT numerical quadrature - there is no
        node, no weight, no panel and no sample point anywhere in it.
        """
        if self.dimension != 1:
            raise OracleError(
                "integrate_unit_interval needs a univariate polynomial")
        total = Fraction(0)
        for (power,), coefficient in self.terms.items():
            total += coefficient * Fraction(1, power + 1)
        return total

    def evaluate(self, point: Sequence) -> Fraction:
        values = [exact(v) for v in point]
        if len(values) != self.dimension:
            raise OracleError(
                f"point of length {len(values)} for dimension "
                f"{self.dimension}")
        total = Fraction(0)
        for exponents, coefficient in self.terms.items():
            term = coefficient
            for value, power in zip(values, exponents):
                if power:
                    term *= value ** power
            total += term
        return total

    def degree(self) -> int:
        return max((sum(k) for k in self.terms), default=0)

    def __eq__(self, other) -> bool:
        return (isinstance(other, Polynomial)
                and other.dimension == self.dimension
                and other.terms == self.terms)

    def __repr__(self) -> str:
        return f"Polynomial(d={self.dimension}, terms={len(self.terms)})"


# --------------------------------------------------------------------------
# the six registered potentials, and the declared action
# --------------------------------------------------------------------------
def potential_polynomial(potential_id: str, dimension: int) -> Polynomial:
    """The registered potential ``potential_id`` as an exact polynomial.

    Built from ``REGISTERED_POTENTIAL_TEXT``'s formulas, with canonical
    zero-based indices ``i = 0..d-1`` as the matrix declares. ``V3``'s sum is
    over ``i < j``, so at ``d = 1`` it is the empty sum, exactly zero - the
    matrix registers ``d = 1`` and does not exclude ``V3`` there.
    """
    if potential_id not in REGISTERED_POTENTIAL_TEXT:
        raise OracleError(
            f"{potential_id!r} is not one of the six registered potentials "
            f"{tuple(REGISTERED_POTENTIAL_TEXT)}")
    if not isinstance(dimension, int) or isinstance(dimension, bool) \
            or dimension < 1:
        raise OracleError(f"dimension must be a positive int, got "
                          f"{dimension!r}")
    d = dimension
    x = [Polynomial.variable(d, i) for i in range(d)]
    if potential_id == "V0":                       # V0=0
        return Polynomial.zero(d)
    if potential_id == "V1":                       # V1=sum(i+1)*x_i
        total = Polynomial.zero(d)
        for i in range(d):
            total = total + x[i].scaled(i + 1)
        return total
    if potential_id == "V2":                       # V2=sum(i+1)*x_i^2
        total = Polynomial.zero(d)
        for i in range(d):
            total = total + x[i].power(2).scaled(i + 1)
        return total
    if potential_id == "V3":        # V3=sum_{i<j}(i+1)(j+1)*x_i*x_j
        total = Polynomial.zero(d)
        for i, j in itertools.combinations(range(d), 2):
            total = total + (x[i] * x[j]).scaled((i + 1) * (j + 1))
        return total
    if potential_id == "V4":                       # V4=sum(i+1)*x_i^3
        total = Polynomial.zero(d)
        for i in range(d):
            total = total + x[i].power(3).scaled(i + 1)
        return total
    # V5=(1+sum x_i)^4
    inner = Polynomial.constant(d, 1)
    for i in range(d):
        inner = inner + x[i]
    return inner.power(4)


def initial_state(dimension: int) -> tuple:
    """``x_i = (i+1)/10`` for canonical index ``i = 0..d-1``, exactly."""
    if not isinstance(dimension, int) or isinstance(dimension, bool) \
            or dimension < 1:
        raise OracleError(f"dimension must be a positive int, got "
                          f"{dimension!r}")
    return tuple(Fraction(i + 1, 10) for i in range(dimension))


def displacement(extent, dimension: int) -> tuple:
    """``Delta x_i = h*(-1)^i/(i+1)``, exactly.

    The registered displacement is linear in ``h`` with no remainder, which is
    what makes ``G_T`` computable: ``T_h(x) = x + h*G_T(x)`` holds exactly,
    with the ``o(h)`` of the generator authority's ``T-A1`` identically zero.
    """
    h = exact(extent)
    if not isinstance(dimension, int) or isinstance(dimension, bool) \
            or dimension < 1:
        raise OracleError(f"dimension must be a positive int, got "
                          f"{dimension!r}")
    return tuple(h * Fraction((-1) ** i, i + 1) for i in range(dimension))


def _generator_direction(dimension: int) -> tuple:
    """``G_T(x)_i = (-1)^i/(i+1)``: the exact per-extent rate of change.

    Derived, not chosen. The generator authority defines ``G_T`` by
    ``T_h(z) = z + h*G_T(z) + o(h)``; SD-03's declared ``T_h`` is exactly
    affine in ``h``, so ``G_T`` is its coefficient and is state-independent
    here. It is a rate per action extent, so its unit is state/action_extent.
    """
    return tuple(Fraction((-1) ** i, i + 1) for i in range(dimension))


# --------------------------------------------------------------------------
# the registered case structure, loaded - never rewritten
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class SD03Case:
    """One registered case identifier. Carries no computed value."""
    dimension: int
    potential_id: str
    extent: Fraction
    boundary_mode: str

    def __post_init__(self):
        object.__setattr__(self, "extent", exact(self.extent))
        if self.potential_id not in REGISTERED_POTENTIAL_TEXT:
            raise OracleError(f"unregistered potential {self.potential_id!r}")
        if self.boundary_mode not in ("CLOSED", "OPEN"):
            raise OracleError(
                f"boundary mode must be CLOSED or OPEN, got "
                f"{self.boundary_mode!r}")

    @property
    def case_id(self) -> str:
        return (f"d{self.dimension}|{self.potential_id}"
                f"|h={self.extent}|{self.boundary_mode}")


@dataclass(frozen=True)
class SD03Configuration:
    """The registered case axes, bound to a digest-pinned canonical matrix."""
    dimensions: tuple
    potential_ids: tuple
    extents: tuple
    boundary_modes: tuple
    matrix_sha256: str
    registered_case_count: int
    registered_evaluation_count: int

    @property
    def case_count(self) -> int:
        return (len(self.dimensions) * len(self.potential_ids)
                * len(self.extents) * len(self.boundary_modes))


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ConfigurationRefused(message)


def load_sd03_configuration(matrix_path: str) -> SD03Configuration:
    """Load SD-03's case axes from the canonical matrix, digest-verified.

    The matrix is the authority for the 192-case structure; this module is
    not.

    HOW THE BINDING ACTUALLY WORKS, precisely. The whole-file SHA-256 must
    equal the registered digest - that pin is the real guarantee, and it is
    what makes the axes below correspond to the registered ones. The axis
    values themselves are module literals, and the ``_require`` checks after
    the digest are substring containment against the registered text, not a
    grammar. They are a tripwire for a future edit, not an independent parse:
    if the digest gate were removed, a materially different matrix whose text
    happened to contain the same substrings would pass them. The digest is
    therefore load-bearing and the substring checks are secondary.

    Refuses on: a wrong digest, a missing or malformed SD-03 entry, an axis
    whose registered text is absent, a registered formula that no longer
    appears, or a case/evaluation count that does not reconcile with the
    matrix's own ``expected_evaluations`` and ``primary_evaluations_per_run``.
    """
    if not isinstance(matrix_path, str) or not matrix_path:
        raise ConfigurationRefused("matrix_path must be a non-empty string")
    try:
        with open(matrix_path, "rb") as handle:
            raw = handle.read()
    except OSError as error:
        raise ConfigurationRefused(f"cannot read the matrix: {error}")
    digest = hashlib.sha256(raw).hexdigest()
    _require(digest == SD03_MATRIX_SHA256,
             f"matrix digest {digest} is not the registered "
             f"{SD03_MATRIX_SHA256}; SD-03's case structure must come from "
             "the canonical matrix")
    try:
        matrix = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError) as error:
        raise ConfigurationRefused(f"matrix is not strict JSON: {error}")
    studies = matrix.get("studies")
    _require(isinstance(studies, list), "matrix has no studies list")
    found = [s for s in studies if isinstance(s, dict)
             and s.get("study_id") == SD03_STUDY_ID]
    _require(len(found) == 1, f"expected exactly one {SD03_STUDY_ID} entry")
    study = found[0]
    configuration = study.get("configuration")
    _require(isinstance(configuration, dict), "SD-03 has no configuration")
    parameters = configuration.get("parameters")
    _require(isinstance(parameters, list) and parameters,
             "SD-03 configuration has no parameters")
    joined = " || ".join(str(p) for p in parameters)

    # Each axis is confirmed against the registered text rather than assumed.
    for potential_id, text in REGISTERED_POTENTIAL_TEXT.items():
        _require(text in joined,
                 f"the registered formula {text!r} is not in the matrix; this "
                 "adapter's potential would no longer be the registered one")
    _require("six exact potentials" in joined,
             "the matrix no longer declares six exact potentials")
    _require("four action extents h in {-1,-1/2,1/2,1}" in joined,
             "the registered action extents changed")
    _require("Delta x_i=h*(-1)^i/(i+1)" in joined,
             "the registered displacement changed")
    _require("dimensions d in {1,2,4,8}" in joined,
             "the registered dimension set changed")
    _require("CLOSED with boundary contribution 0" in joined,
             "the registered CLOSED boundary mode changed")
    _require("OPEN with explicit contribution h/10 potential-unit included "
             "once" in joined, "the registered OPEN boundary mode changed")

    initial = " || ".join(str(p) for p
                          in configuration.get("initial_conditions", []))
    _require("x_i=(i+1)/10" in initial,
             "the registered initial state changed")
    uncertainty = str(configuration.get("uncertainty_rules", ""))
    _require("reduced-rational exact" in uncertainty
             and "floating substitution are forbidden" in uncertainty,
             "SD-03 no longer registers exact-rational-only arithmetic")
    _require(str(configuration.get("stochastic_rules")) == "FORBIDDEN",
             "SD-03 no longer forbids stochastic rules")

    feasibility = study.get("computational_feasibility", {})
    size = str(feasibility.get("exact_problem_size", ""))
    _require("= 192 cases" in size,
             f"the registered case count changed: {size!r}")
    evaluations = feasibility.get("expected_evaluations")
    _require(evaluations == REGISTERED_EVALUATION_COUNT,
             f"the registered evaluation count is {evaluations}, not "
             f"{REGISTERED_EVALUATION_COUNT}")
    per_case = feasibility.get("hard_caps", {}).get(
        "primary_evaluations_per_run")
    _require(per_case == len(CHAIN_PROJECTIONS),
             f"the matrix registers {per_case} evaluations per case but the "
             f"chain has {len(CHAIN_PROJECTIONS)} projections")

    equations = study.get("owners", {}).get("equations")
    _require(isinstance(equations, list)
             and len(equations) == len(CHAIN_PROJECTIONS),
             f"SD-03 registers {equations!r}, not {len(CHAIN_PROJECTIONS)} "
             "chain projections")

    config = SD03Configuration(
        dimensions=(1, 2, 4, 8),
        potential_ids=tuple(sorted(REGISTERED_POTENTIAL_TEXT)),
        extents=(Fraction(-1), Fraction(-1, 2), Fraction(1, 2), Fraction(1)),
        boundary_modes=("CLOSED", "OPEN"),
        matrix_sha256=digest,
        registered_case_count=REGISTERED_CASE_COUNT,
        registered_evaluation_count=REGISTERED_EVALUATION_COUNT)
    _require(config.case_count == REGISTERED_CASE_COUNT,
             f"parsed axes give {config.case_count} cases, not "
             f"{REGISTERED_CASE_COUNT}")
    _require(config.case_count * len(CHAIN_PROJECTIONS)
             == REGISTERED_EVALUATION_COUNT,
             "cases times projections does not equal the registered "
             "evaluation count")
    return config


def registered_cases(config: SD03Configuration) -> tuple:
    """The registered case IDENTIFIERS. Evaluates nothing.

    Enumerating identifiers is not running the study: no potential is built,
    no projection is computed and no output is produced. Executing the 192
    cases needs an authorization this module does not carry.
    """
    if not isinstance(config, SD03Configuration):
        raise OracleError("config must be an SD03Configuration")
    return tuple(
        SD03Case(dimension=d, potential_id=p, extent=h, boundary_mode=b)
        for d in config.dimensions
        for p in config.potential_ids
        for h in config.extents
        for b in config.boundary_modes)


# --------------------------------------------------------------------------
# the chain projections
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ChainValue:
    """One projection's exact value, tagged with which projection it is.

    The tag is load-bearing. SD-03's registered falsifier "an intermediate is
    reported as the final finite EBU" is prevented structurally: only a value
    whose ``projection`` is ``FINITE_EBU`` can leave ``finite_ebu_of``.
    """
    projection: str
    quantities: tuple          # one Quantity, or one per coordinate
    case_id: str

    def __post_init__(self):
        if self.projection not in CHAIN_PROJECTIONS:
            raise OracleError(f"unknown projection {self.projection!r}")
        for quantity in self.quantities:
            if not isinstance(quantity, Quantity):
                raise OracleError("a ChainValue holds Quantity values only")

    @property
    def scalar(self) -> Quantity:
        if len(self.quantities) != 1:
            raise OracleError(
                f"{self.projection} has {len(self.quantities)} components, "
                "not one scalar")
        return self.quantities[0]


# Every reason cites Foundation_v2.7_math.md, which is committed on this
# branch, and names exactly the parameters that equation needs.
_UNREGISTERED_REASON = {
    "F": ("the driving force is defined in Foundation_v2.7_math.md as "
          "f_e = mu_i - eta_e*mu_j (used in (2.6)). It is a difference of "
          "marginals across an EDGE, so it needs a two-endpoint edge and the "
          "transport efficiency eta_e."),
    "PSI": ("Foundation_v2.7_math.md (2.3) defines the dissipation potential "
            "Psi(J) = sum_e [J_e^2/(2*M_e) + theta_e*J_e] for J_e >= 0. It "
            "needs the edge mobility M_e and the threshold theta_e."),
    "J": ("Foundation_v2.7_math.md (2.6) gives the Onsager law "
          "J_e = M_e*[f_e - theta_e]_+, the minimiser of Psi_e(J_e) - f_e*J_e "
          "over J_e >= 0. It needs M_e, theta_e and f_e, hence also eta_e."),
}

_UNREGISTERED_COMMON = (
    " SD-03's registered configuration declares dimensions, six potentials, "
    "four action extents and two boundary modes - no edge set, no eta, no "
    "mobility and no threshold - so this projection is not evaluable on "
    "SD-03's declared cases. Neither atomic authority nor the conservation "
    "foundation supplies them: f_e, Psi_e, J_e, eta_e, M_e and theta_e occur "
    "zero times in all five cited dependencies. Register it explicitly "
    "before SD-03 executes; supplying a stand-in would choose physics the "
    "study does not declare.")


def project(case: SD03Case, projection: str) -> ChainValue:
    """One exact chain projection for one registered case.

    Refuses ``F``, ``PSI`` and ``J`` with the precise reason. Everything else
    is exact rational arithmetic with declared units.
    """
    if not isinstance(case, SD03Case):
        raise OracleError("case must be an SD03Case")
    if projection not in CHAIN_PROJECTIONS:
        raise OracleError(
            f"{projection!r} is not one of {CHAIN_PROJECTIONS}")
    if projection in UNREGISTERED_PROJECTIONS:
        raise UnregisteredProjection(
            f"{projection}: " + _UNREGISTERED_REASON[projection]
            + _UNREGISTERED_COMMON)

    d = case.dimension
    x = initial_state(d)
    polynomial = potential_polynomial(case.potential_id, d)

    if projection == "V":
        return ChainValue("V", (Quantity(polynomial.evaluate(x), POTENTIAL),),
                          case.case_id)
    if projection == "MU":
        gradient = tuple(
            Quantity(polynomial.partial_derivative(i).evaluate(x),
                     POTENTIAL / STATE)
            for i in range(d))
        return ChainValue("MU", gradient, case.case_id)
    if projection == "G_T":
        direction = _generator_direction(d)
        return ChainValue(
            "G_T",
            tuple(Quantity(value, STATE / ACTION_EXTENT)
                  for value in direction),
            case.case_id)

    # FINITE_EBU: the registered comparator "direct finite potential
    # difference", V(x + Delta x) - V(x), taken as an exact endpoint
    # difference. Never a quadrature, never a series, never a surrogate.
    delta = displacement(case.extent, d)
    moved = tuple(a + b for a, b in zip(x, delta))
    difference = polynomial.evaluate(moved) - polynomial.evaluate(x)
    return ChainValue("FINITE_EBU", (Quantity(difference, POTENTIAL),),
                      case.case_id)


def chain_projections(case: SD03Case) -> dict:
    """All seven projections for one case; the three unregistered as reasons.

    Returns a mapping from projection name to either a ``ChainValue`` or the
    string reason it is refused, so a caller sees the complete chain and which
    part of it no authority defines. It never substitutes a value.
    """
    result = {}
    for name in CHAIN_PROJECTIONS:
        try:
            result[name] = project(case, name)
        except UnregisteredProjection as error:
            result[name] = str(error)
    return result


def integrated_generator_chain(case: SD03Case) -> Quantity:
    """The SECOND registered comparator: the integrated generator chain.

    SD-03 registers three comparators - "direct finite potential difference",
    "integrated generator chain", "explicit boundary-accounting form". This is
    the second, and it is what gives the registered falsifier "chain value
    differs from its independent definition" something to fire on: without an
    independent route there is nothing to disagree with.

        int_0^1 grad V(x + t*h*G_T(x)) . (h*G_T(x)) dt

    It uses ONLY the three computable links V, MU and G_T. It needs no edge,
    no theta, no mobility and no eta, which is exactly why it is available
    when f_e, Psi_e and J_e are not.

    Exact throughout: the integrand is a polynomial in ``t`` because ``V`` is,
    and it is integrated symbolically term by term. Never quadrature, never
    sampled, never truncated.
    """
    if not isinstance(case, SD03Case):
        raise OracleError("case must be an SD03Case")
    d = case.dimension
    x = initial_state(d)
    delta = displacement(case.extent, d)
    polynomial = potential_polynomial(case.potential_id, d)
    total = Fraction(0)
    for index in range(d):
        partial = polynomial.partial_derivative(index)
        along = partial.along_affine_path(x, delta)
        total += along.integrate_unit_interval() * delta[index]
    return Quantity(total, POTENTIAL)


def comparator_agreement(case: SD03Case) -> dict:
    """Both computable comparators, and whether they agree EXACTLY.

    Agreement is ``==`` on ``Fraction``. There is no tolerance, so this is a
    genuine cross-check rather than a restatement: the two routes share only
    the potential's coefficients, and reach the value by different algebra -
    one by two endpoint evaluations, the other by restricting the gradient to
    the action path and integrating it.

    The third registered comparator, the explicit boundary-accounting form,
    is ``accounting_ledger``.
    """
    direct = finite_ebu_of(project(case, "FINITE_EBU"))
    integrated = integrated_generator_chain(case)
    if direct.unit != integrated.unit:
        raise UnitMismatch("the two comparators disagree on units")
    return {
        "case_id": case.case_id,
        "direct_finite_potential_difference": direct,
        "integrated_generator_chain": integrated,
        "difference": Quantity(direct.value - integrated.value, POTENTIAL),
        "agree_exactly": direct.value == integrated.value,
    }


def finite_ebu_of(value: ChainValue) -> Quantity:
    """Return the finite EBU, refusing any intermediate.

    This is the registered falsifier "an intermediate is reported as the final
    finite EBU", enforced rather than tested for. There is no argument that
    relaxes it.
    """
    if not isinstance(value, ChainValue):
        raise OracleError("finite_ebu_of takes a ChainValue")
    if value.projection != "FINITE_EBU":
        raise OracleError(
            f"{value.projection} is an intermediate chain value and must "
            "never be reported as the finite EBU (SD-03 falsifier: 'an "
            "intermediate is reported as the final finite EBU')")
    return value.scalar


# --------------------------------------------------------------------------
# units and accounting closure
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class AccountingLedger:
    """The declared ledger entries for one case, and their exact residual.

    ``conservation_accounting.no_double_count_rule`` reads "each chain term
    has one semantic owner and is included once in the final finite ledger".
    This records each owned entry once and reports the residual exactly.

    THE SIGN OF THE OPEN BOUNDARY TERM IS NOT REGISTERED. The matrix declares
    "OPEN with explicit contribution h/10 potential-unit included once" and
    gives no direction, so this ledger records the boundary as its own named
    additive entry and does NOT assert whether it is an inflow or an outflow.
    ``total`` is the sum of the entries, nothing more. Choosing a direction is
    an author registration and appears in the readiness document as a
    prerequisite.
    """
    case_id: str
    entries: tuple             # ((owner, Quantity), ...) each owner once
    total: Quantity
    omitted_boundary_residual: Quantity

    def owners(self) -> tuple:
        return tuple(owner for owner, _ in self.entries)


def _boundary_contribution(case: SD03Case) -> Quantity:
    """CLOSED: exactly 0. OPEN: exactly ``h/10`` potential-unit, once."""
    if case.boundary_mode == "CLOSED":
        return Quantity(Fraction(0), POTENTIAL)
    return Quantity(case.extent / 10, POTENTIAL)


def accounting_ledger(case: SD03Case) -> AccountingLedger:
    """Build the exact ledger and residual for one case.

    Two owners, each counted once: the interior finite potential difference,
    and the declared boundary exchange. ``omitted_boundary_residual`` is what
    the registered negative control "omitted boundary term leaves an explicit
    residual" must see - it is the boundary entry itself, so the residual is
    zero exactly when CLOSED and exactly ``h/10`` when OPEN.
    """
    if not isinstance(case, SD03Case):
        raise OracleError("case must be an SD03Case")
    interior = finite_ebu_of(project(case, "FINITE_EBU"))
    boundary = _boundary_contribution(case)
    entries = (("interior_finite_difference", interior),
               ("declared_boundary_exchange", boundary))
    names = [owner for owner, _ in entries]
    if len(set(names)) != len(names):
        raise OracleError("an owner appeared twice; that is a double count")
    total = interior + boundary          # refuses on any unit mismatch
    return AccountingLedger(
        case_id=case.case_id, entries=entries, total=total,
        omitted_boundary_residual=Quantity(total.value - interior.value,
                                           POTENTIAL))
