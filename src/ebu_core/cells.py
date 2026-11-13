"""One economic cell: its records and its exact field, slope and inverse stiffness.

A cell is split into two immutable records:

* :class:`CellDesign` — what the cell *is*: its identity, the declared
  resource coordinate, its reference ``x_star`` (J) and stiffness ``K`` (1/J).
* :class:`Cell` — a design together with the current resource amount ``x`` (J).

For one cell the module evaluates exactly::

    Phi = K (x - x_star)^2 / 2      imbalance field, J
    m   = K (x - x_star)            current slope, dimensionless
    c   = 1 / K                     inverse stiffness (response scale), J

``Phi`` measures how far the represented amount is from its reference. It is
not an additional store of resource energy: an empty cell with a positive
reference has a positive field. Each cell's values depend on that cell alone.

What this module deliberately does *not* decide
-----------------------------------------------
* Physical feasibility. Any exact ``x`` and ``x_star`` are evaluated; there
  is no sign, capacity, stock, power or whole-unit rule. Those are explicit
  application constraints still to be declared.
* Resource compatibility. ``resource_key`` is an application's declaration
  of which resource coordinate and joule mapping the cell uses. Two cells
  sharing a key are not thereby proven physically interchangeable or
  calibrated.
* Lifecycle. Nothing here creates, removes or redesigns cells. An empty cell
  remains a cell and keeps its field.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from .exact import to_exact

__all__ = [
    "CellDesign",
    "Cell",
    "CellEvaluation",
    "make_cell",
    "imbalance_field",
    "slope",
    "inverse_stiffness",
    "evaluate_cell",
]


def _check_label(value: object, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name}: expected a string, got {type(value).__name__}")
    if not value or value != value.strip():
        raise ValueError(
            f"{name}: must be nonempty and have no leading or trailing whitespace, got {value!r}"
        )


@dataclass(frozen=True)
class CellDesign:
    """Immutable design of one cell.

    Numeric fields accept anything :func:`ebu_core.exact.to_exact` accepts
    and are stored as exact :class:`~fractions.Fraction` values.

    Attributes:
        cell_id: nonempty identifier of the cell.
        resource_key: nonempty application label for the resource
            coordinate and its joule mapping (a declaration, not a proof).
        x_star: reference coordinate, in J.
        K: stiffness, in 1/J; must be strictly positive.
    """

    cell_id: str
    resource_key: str
    x_star: Fraction
    K: Fraction

    def __post_init__(self) -> None:
        _check_label(self.cell_id, "cell_id")
        _check_label(self.resource_key, "resource_key")
        # Frozen dataclass: normalise through object.__setattr__ once, here.
        object.__setattr__(self, "x_star", to_exact(self.x_star, "x_star"))
        stiffness = to_exact(self.K, "K")
        if stiffness <= 0:
            raise ValueError(f"K: stiffness must be > 0, got {stiffness}")
        object.__setattr__(self, "K", stiffness)


@dataclass(frozen=True)
class Cell:
    """Immutable current state of one cell: its design and resource amount.

    Attributes:
        design: the cell's :class:`CellDesign`.
        x: current resource coordinate, in J (stored as a Fraction).
    """

    design: CellDesign
    x: Fraction

    def __post_init__(self) -> None:
        if not isinstance(self.design, CellDesign):
            raise TypeError(f"design: expected CellDesign, got {type(self.design).__name__}")
        object.__setattr__(self, "x", to_exact(self.x, "x"))

    @property
    def cell_id(self) -> str:
        return self.design.cell_id

    @property
    def resource_key(self) -> str:
        return self.design.resource_key

    @property
    def x_star(self) -> Fraction:
        return self.design.x_star

    @property
    def K(self) -> Fraction:
        return self.design.K


@dataclass(frozen=True)
class CellEvaluation:
    """Immutable result of :func:`evaluate_cell`.

    Attributes:
        cell: the evaluated cell.
        phi: imbalance field ``K (x - x_star)^2 / 2``, in J.
        m: slope ``K (x - x_star)``, dimensionless.
        c: inverse stiffness ``1 / K``, in J.
    """

    cell: Cell
    phi: Fraction
    m: Fraction
    c: Fraction


def make_cell(*, cell_id: str, resource_key: str, x: object, x_star: object, K: object) -> Cell:
    """Build a validated :class:`Cell` from plain inputs.

    All arguments are keyword-only so that ``x`` and ``x_star`` cannot be
    swapped by position.
    """
    return Cell(CellDesign(cell_id, resource_key, x_star, K), x)


def _require_cell(cell: object) -> Cell:
    if not isinstance(cell, Cell):
        raise TypeError(f"expected Cell, got {type(cell).__name__}")
    return cell


def imbalance_field(cell: Cell) -> Fraction:
    """Return ``Phi = K (x - x_star)^2 / 2`` in J, exactly."""
    _require_cell(cell)
    departure = cell.x - cell.design.x_star
    return cell.design.K * departure * departure / 2


def slope(cell: Cell) -> Fraction:
    """Return the dimensionless slope ``m = K (x - x_star)``, exactly.

    Negative: below the reference. Zero: at the reference. Positive: above it.
    """
    _require_cell(cell)
    return cell.design.K * (cell.x - cell.design.x_star)


def inverse_stiffness(cell: Cell) -> Fraction:
    """Return the response scale ``c = 1 / K`` in J, exactly."""
    _require_cell(cell)
    return 1 / cell.design.K


def evaluate_cell(cell: Cell) -> CellEvaluation:
    """Return field, slope and inverse stiffness of ``cell`` together."""
    return CellEvaluation(
        cell=_require_cell(cell),
        phi=imbalance_field(cell),
        m=slope(cell),
        c=inverse_stiffness(cell),
    )
