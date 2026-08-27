"""Pure exact diagnostics for the closed-loop correction milestone."""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import NoReturn

from .correction_protocol import (
    ClosedLoopModelClass,
    ContinuousFeedbackDeclaration,
    ContinuousFeedbackRegime,
    ContinuousFeedbackResult,
    CoordinateConjugacyDeclaration,
    CorrectionClosureDeclaration,
    CorrectionClosureResult,
    DependencyGraphDeclaration,
    DependencyInvalidationResult,
    DiscreteFeedbackDeclaration,
    DiscreteFeedbackRegime,
    DiscreteFeedbackResult,
    FeedbackBlockDeclaration,
    FeedbackPathResult,
    ObservabilityDeclaration,
    ObservabilityResult,
    RationalMatrix,
)
from .errors import (
    Applicability,
    FailureCode,
    FailureInterfaceRef,
    FailureStage,
    RetryClass,
    ScientificStatusEffect,
    _fail,
)
from .numeric import IntegerV1, RationalV1


_Matrix = tuple[tuple[Fraction, ...], ...]


def _interface(name: str) -> FailureInterfaceRef:
    return FailureInterfaceRef(
        "ebu_framework.correction_diagnostics", name, "1.0.0"
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


def _fraction(value: RationalV1) -> Fraction:
    return Fraction(value.numerator.value, value.denominator.value)


def _rational(value: Fraction) -> RationalV1:
    return RationalV1(
        IntegerV1(value.numerator),
        IntegerV1(value.denominator),
    )


def _matrix(value: RationalMatrix) -> _Matrix:
    return tuple(tuple(_fraction(item) for item in row) for row in value.rows)


def _rational_matrix(value: _Matrix) -> RationalMatrix:
    return RationalMatrix(
        rows=tuple(tuple(_rational(item) for item in row) for row in value)
    )


def _shape(value: _Matrix) -> tuple[int, int]:
    return len(value), len(value[0])


def _identity(size: int) -> _Matrix:
    return tuple(
        tuple(Fraction(row == column) for column in range(size))
        for row in range(size)
    )


def _zero(rows: int, columns: int) -> _Matrix:
    return tuple(tuple(Fraction() for _ in range(columns)) for _ in range(rows))


def _multiply(left: _Matrix, right: _Matrix, interface: str) -> _Matrix:
    if _shape(left)[1] != _shape(right)[0]:
        _failure(FailureCode.CLCD_MATRIX_SHAPE_INVALID, interface)
    return tuple(
        tuple(
            sum(
                (left[row][index] * right[index][column] for index in range(len(right))),
                Fraction(),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def _subtract(left: _Matrix, right: _Matrix, interface: str) -> _Matrix:
    if _shape(left) != _shape(right):
        _failure(FailureCode.CLCD_MATRIX_SHAPE_INVALID, interface)
    return tuple(
        tuple(left[row][column] - right[row][column] for column in range(len(left[0])))
        for row in range(len(left))
    )


def _power(value: _Matrix, order: int, interface: str) -> _Matrix:
    rows, columns = _shape(value)
    if rows != columns or type(order) is not int or order < 0:
        _failure(FailureCode.CLCD_MATRIX_SHAPE_INVALID, interface)
    result = _identity(rows)
    for _ in range(order):
        result = _multiply(result, value, interface)
    return result


def _nonzero(value: _Matrix) -> bool:
    return any(item != 0 for row in value for item in row)


def validate_coordinate_conjugacy(
    declaration: CoordinateConjugacyDeclaration,
    a_e: RationalMatrix,
    /,
) -> RationalMatrix:
    interface = "validate_coordinate_conjugacy"
    if type(declaration) is not CoordinateConjugacyDeclaration or type(a_e) is not RationalMatrix:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    expected_subsets = {
        tuple(items)
        for size in range(len(declaration.action_ids) + 1)
        for items in combinations(declaration.action_ids, size)
    }
    if set(declaration.subset_order) != expected_subsets:
        _failure(FailureCode.CLCD_COORDINATE_BASIS_INCOMPLETE, interface)
    zeta = _matrix(declaration.zeta)
    mobius = _matrix(declaration.mobius)
    source = _matrix(a_e)
    size = len(declaration.subset_order)
    if any(_shape(value) != (size, size) for value in (zeta, mobius, source)):
        _failure(FailureCode.CLCD_MATRIX_SHAPE_INVALID, interface)
    expected_zeta = tuple(
        tuple(
            Fraction(set(source_subset).issubset(target_subset))
            for source_subset in declaration.subset_order
        )
        for target_subset in declaration.subset_order
    )
    if zeta != expected_zeta:
        _failure(FailureCode.CLCD_COORDINATE_EQUIVALENCE_INVALID, interface)
    identity = _identity(size)
    if (
        _multiply(mobius, zeta, interface) != identity
        or _multiply(zeta, mobius, interface) != identity
    ):
        _failure(FailureCode.CLCD_MOBIUS_INVERSE_INVALID, interface)
    return _rational_matrix(
        _multiply(_multiply(mobius, source, interface), zeta, interface)
    )


def detect_feedback_path(
    declaration: FeedbackBlockDeclaration,
    max_order: int,
    /,
) -> FeedbackPathResult:
    interface = "detect_feedback_path"
    if type(declaration) is not FeedbackBlockDeclaration:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    if type(max_order) is not int or max_order <= 0:
        _failure(FailureCode.CLCD_FEEDBACK_PATH_INVALID, interface)
    a, b, c, d = map(
        _matrix, (declaration.a, declaration.b, declaration.c, declaration.d)
    )
    n, n_columns = _shape(a)
    r, r_columns = _shape(d)
    if (
        n != n_columns
        or r != r_columns
        or _shape(b) != (n, r)
        or _shape(c) != (r, n)
    ):
        _failure(FailureCode.CLCD_FEEDBACK_BLOCK_INVALID, interface)
    block = tuple(
        tuple(a[row]) + tuple(b[row]) for row in range(n)
    ) + tuple(tuple(c[row]) + tuple(d[row]) for row in range(r))
    projection = tuple(
        tuple(Fraction(row == column) for column in range(n + r))
        for row in range(n)
    )
    embedding = tuple(
        tuple(Fraction(row == column) for column in range(n))
        for row in range(n + r)
    )
    bc = _multiply(b, c, interface)
    first_order: int | Applicability = Applicability.NOT_APPLICABLE
    first_operator: RationalMatrix | Applicability = Applicability.NOT_APPLICABLE
    for order in range(1, max_order + 1):
        operator = _subtract(
            _multiply(
                _multiply(projection, _power(block, order, interface), interface),
                embedding,
                interface,
            ),
            _power(a, order, interface),
            interface,
        )
        if _nonzero(operator):
            first_order = order
            first_operator = _rational_matrix(operator)
            break
    return FeedbackPathResult(
        bc=_rational_matrix(bc),
        first_nonzero_order=first_order,
        first_nonzero_operator=first_operator,
        tested_through_order=max_order,
    )


def classify_continuous_feedback(
    declaration: ContinuousFeedbackDeclaration, /
) -> ContinuousFeedbackResult:
    interface = "classify_continuous_feedback"
    if type(declaration) is not ContinuousFeedbackDeclaration:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    a, d, b, k = map(
        _fraction, (declaration.a, declaration.d, declaration.b, declaration.k)
    )
    s = a + d
    q = a * d + b * k
    discriminant = s * s - 4 * q
    if q < 0:
        regime = ContinuousFeedbackRegime.SADDLE_INSTABILITY
    elif s > 0 and q > 0 and discriminant < 0:
        regime = ContinuousFeedbackRegime.ASYMPTOTICALLY_STABLE_DAMPED_OSCILLATION
    elif s > 0 and q > 0:
        regime = ContinuousFeedbackRegime.ASYMPTOTICALLY_STABLE_REAL_DECAY
    elif s == 0 and q > 0:
        regime = ContinuousFeedbackRegime.PERSISTENT_UNDAMPED_OSCILLATION_BOUNDARY
    elif s < 0 and q > 0 and discriminant < 0:
        regime = ContinuousFeedbackRegime.UNSTABLE_GROWING_OSCILLATION
    elif s < 0 and q > 0:
        regime = ContinuousFeedbackRegime.UNSTABLE_GROWING_REAL
    else:
        regime = ContinuousFeedbackRegime.NONASYMPTOTIC_BOUNDARY
    return ContinuousFeedbackResult(
        s=_rational(s),
        q=_rational(q),
        discriminant=_rational(discriminant),
        regime=regime,
    )


def classify_discrete_feedback(
    declaration: DiscreteFeedbackDeclaration, /
) -> DiscreteFeedbackResult:
    interface = "classify_discrete_feedback"
    if type(declaration) is not DiscreteFeedbackDeclaration:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    kappa = _fraction(declaration.kappa)
    if declaration.model_class is ClosedLoopModelClass.DISCRETE_IMMEDIATE:
        root = 1 - kappa
        if 0 < kappa < 1:
            regime = DiscreteFeedbackRegime.IMMEDIATE_MONOTONE_DECAY
        elif kappa == 1:
            regime = DiscreteFeedbackRegime.IMMEDIATE_DEADBEAT
        elif 1 < kappa < 2:
            regime = DiscreteFeedbackRegime.IMMEDIATE_ALTERNATING_DECAY
        elif kappa in {0, 2}:
            regime = DiscreteFeedbackRegime.PERSISTENT_BOUNDARY
        else:
            regime = DiscreteFeedbackRegime.UNSTABLE
        return DiscreteFeedbackResult(
            immediate_root=_rational(root),
            discriminant=Applicability.NOT_APPLICABLE,
            root_modulus_squared=Applicability.NOT_APPLICABLE,
            regime=regime,
        )
    if declaration.model_class is not ClosedLoopModelClass.DISCRETE_ONE_STEP_DELAY:
        _failure(FailureCode.CLCD_DELAY_CLASSIFICATION_INVALID, interface)
    discriminant = 1 - 4 * kappa
    if 0 < kappa < Fraction(1, 4):
        regime = DiscreteFeedbackRegime.DELAYED_REAL_DECAY
        modulus: RationalV1 | Applicability = Applicability.NOT_APPLICABLE
    elif kappa == Fraction(1, 4):
        regime = DiscreteFeedbackRegime.DELAYED_CRITICAL_DECAY
        modulus = _rational(Fraction(1, 4))
    elif Fraction(1, 4) < kappa < 1:
        regime = DiscreteFeedbackRegime.DELAYED_DAMPED_OSCILLATION
        modulus = _rational(kappa)
    elif kappa in {0, 1}:
        regime = DiscreteFeedbackRegime.PERSISTENT_BOUNDARY
        modulus = _rational(kappa) if kappa == 1 else Applicability.NOT_APPLICABLE
    else:
        regime = DiscreteFeedbackRegime.UNSTABLE
        modulus = _rational(kappa) if kappa > Fraction(1, 4) else Applicability.NOT_APPLICABLE
    return DiscreteFeedbackResult(
        immediate_root=Applicability.NOT_APPLICABLE,
        discriminant=_rational(discriminant),
        root_modulus_squared=modulus,
        regime=regime,
    )


def evaluate_observability(
    declaration: ObservabilityDeclaration, /
) -> ObservabilityResult:
    interface = "evaluate_observability"
    if type(declaration) is not ObservabilityDeclaration:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    observation = _matrix(declaration.observation)
    projected: list[RationalMatrix] = []
    visible: list[bool] = []
    for mode_value in declaration.modes:
        mode = _matrix(mode_value)
        if _shape(mode)[1] != 1 or _shape(observation)[1] != _shape(mode)[0]:
            _failure(FailureCode.CLCD_OBSERVABILITY_INVALID, interface)
        result = _multiply(observation, mode, interface)
        projected.append(_rational_matrix(result))
        visible.append(_nonzero(result))
    return ObservabilityResult(
        visible=tuple(visible),
        projected_modes=tuple(projected),
    )


def evaluate_correction_closure(
    declaration: CorrectionClosureDeclaration, /
) -> CorrectionClosureResult:
    interface = "evaluate_correction_closure"
    if type(declaration) is not CorrectionClosureDeclaration:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    rhs = (
        _fraction(declaration.boundary_in)
        - _fraction(declaration.boundary_out)
        + _fraction(declaration.generation)
        - _fraction(declaration.consumption)
        + _fraction(declaration.residual)
    )
    transfers_cancel = all(left == right for left, right in declaration.internal_transfers)
    return CorrectionClosureResult(
        closure_rhs=_rational(rhs),
        closes=rhs == _fraction(declaration.stock_change),
        internal_transfers_cancel=transfers_cancel,
    )


def compute_dependency_invalidation(
    declaration: DependencyGraphDeclaration, /
) -> DependencyInvalidationResult:
    interface = "compute_dependency_invalidation"
    if type(declaration) is not DependencyGraphDeclaration:
        _failure(FailureCode.CLCD_RECORD_FORMATION_INVALID, interface)
    if not declaration.inventory_complete:
        _failure(FailureCode.CLCD_DEPENDENCY_GRAPH_INVALID, interface)
    indegree = {vertex: 0 for vertex in declaration.vertices}
    outgoing = {vertex: [] for vertex in declaration.vertices}
    for source, target in declaration.edges:
        indegree[target] += 1
        outgoing[source].append(target)
    queue = [vertex for vertex in declaration.vertices if indegree[vertex] == 0]
    complete_order: list[str] = []
    while queue:
        vertex = queue.pop(0)
        complete_order.append(vertex)
        for target in outgoing[vertex]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(complete_order) != len(declaration.vertices):
        _failure(FailureCode.CLCD_DEPENDENCY_GRAPH_INVALID, interface)
    descendants: set[str] = set()
    frontier = [declaration.corrected_vertex]
    while frontier:
        vertex = frontier.pop(0)
        for target in outgoing[vertex]:
            if target not in descendants:
                descendants.add(target)
                frontier.append(target)
    descendant_order = tuple(
        vertex for vertex in declaration.vertices if vertex in descendants
    )
    topological_order = tuple(
        vertex for vertex in complete_order if vertex in descendants
    )
    return DependencyInvalidationResult(
        descendants=descendant_order,
        topological_order=topological_order,
    )


__all__ = (
    "validate_coordinate_conjugacy",
    "detect_feedback_path",
    "classify_continuous_feedback",
    "classify_discrete_feedback",
    "evaluate_observability",
    "evaluate_correction_closure",
    "compute_dependency_invalidation",
)
