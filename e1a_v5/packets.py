"""Typed scientific packet structures for the E1a v5 candidate pipeline.

Layer A of the V-stage implementation.  These are *candidate* schemas; they do
not populate, supersede or reuse any ``e1a_v4`` packet identity.

Provenance discipline
---------------------
Every scalar carried by a packet records how it came to exist.  The V-stage
brief requires the schema to distinguish synthetic auxiliary values from real
measurements so that a synthetic fixture can never be mistaken for a real
calibration packet.  ``SYNTHETIC_MEASURED`` is the only measurement-like kind
this package can produce, and every packet carries ``synthetic=True``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .numerics import Matrix
from .refusals import Refusal


class ValueKind(str, Enum):
    """Provenance kind for a packet scalar (V-stage brief section 8)."""

    #: A synthetic stand-in for an independently measured auxiliary value.
    #: This package can never emit a non-synthetic measured value.
    SYNTHETIC_MEASURED = "SYNTHETIC_MEASURED_LIKE"
    #: Computed from other packet values by a recorded formula.
    DERIVED = "DERIVED"
    #: A defining constant (for example k_B).
    EXACT_CONSTANT = "EXACT_CONSTANT"
    #: An external reference standard supplied to the procedure.
    REFERENCE_INPUT = "REFERENCE_INPUT"
    #: A nominal preregistered design target, never a realised value.
    TARGET_SETTING = "TARGET_SETTING"
    #: The output of a qualification predicate.
    QUALIFICATION_RESULT = "QUALIFICATION_RESULT"


@dataclass(frozen=True)
class TracedValue:
    """A canonical-SI scalar with its provenance kind and source unit."""

    value: float
    kind: ValueKind
    unit: str
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "value": self.value,
            "kind": self.kind.value,
            "unit": self.unit,
            "note": self.note,
        }


class FieldId(str, Enum):
    """The four preregistered fields (T-stage section 7)."""

    THETA0 = "theta0"  # circular reference, nominal 100/100 uN/m at 298 K
    THETA1 = "theta1"  # stiffness challenge, nominal 2.1-fold
    THETA2 = "theta2"  # ellipse, nominal R30 diag(150, 60)
    THETA3 = "theta3"  # temperature challenge, nominal 318 K

    @property
    def index(self) -> int:
        return {"theta0": 0, "theta1": 1, "theta2": 2, "theta3": 3}[self.value]


class BlockId(str, Enum):
    """The two independently prepared blocks (T-stage section 23)."""

    BLOCK1 = "block1"
    BLOCK2 = "block2"

    @property
    def index(self) -> int:
        return {"block1": 0, "block2": 1}[self.value]


#: The eight records of one complete experiment, in fixed order.
RECORDS: tuple[tuple[BlockId, FieldId], ...] = tuple(
    (b, f) for b in (BlockId.BLOCK1, BlockId.BLOCK2) for f in FieldId
)

#: The six within-block reference contrasts (T-stage section 10).
CONTRASTS: tuple[tuple[BlockId, FieldId], ...] = tuple(
    (b, f)
    for b in (BlockId.BLOCK1, BlockId.BLOCK2)
    for f in (FieldId.THETA1, FieldId.THETA2, FieldId.THETA3)
)


@dataclass(frozen=True)
class BranchAPacket:
    """Branch-A physical calibration packet for one (block, field) record.

    All matrices are in canonical SI.  ``k3`` is the full 3-by-3 mechanical
    stiffness; the official lateral matrix is its Schur complement, never the
    plane block ``k3[:2, :2]``.
    """

    block: BlockId
    field: FieldId
    #: Full 3D stiffness K^(3) in N/m, ordered (x, y, z).
    k3: Matrix
    #: Independently measured local temperature, K.
    temperature: TracedValue
    #: Dynamic viscosity at the local temperature, Pa.s.
    viscosity: TracedValue
    #: Bead radius, m.
    bead_radius: TracedValue
    #: Independently established lateral trap centre, m.
    centre: Sequence[float]
    #: Primitive auxiliary covariance, in the order given by ``phi_names``.
    c_phi: Matrix
    phi_names: Sequence[str]
    #: Certified bounded systematic log-beta contributions for this record.
    bounded_bias: float = 0.0
    #: Identity of the realisation policy this packet was qualified against.
    policy_version: str = ""
    synthetic: bool = True
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.synthetic:
            raise ValueError(
                "e1a_v5 packets are synthetic-only; a non-synthetic packet "
                "cannot be constructed by this candidate implementation"
            )


@dataclass(frozen=True)
class ObservationCalibrationPacket:
    """Observation-instrument calibration packet (T-stage section 15.1)."""

    #: Detector offset b_det, m.
    b_det: Sequence[float]
    #: Invertible physical-to-detector map P.
    p_matrix: Matrix
    #: Localisation noise covariance R_obs, m^2.
    r_obs: Matrix
    #: Shutter exposure length, s.
    t_exp: float
    #: Frame interval, s.
    dt: float
    #: Number of frames in the record.
    n_frames: int
    synthetic: bool = True
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.synthetic:
            raise ValueError("e1a_v5 observation packets are synthetic-only")


@dataclass(frozen=True)
class BranchBPacket:
    """Branch-B passive observation packet: the raw detector record."""

    block: BlockId
    field: FieldId
    #: Observed 2D detector positions, one per frame, in detector units (m).
    y: Sequence[Sequence[float]]
    #: Actual frame timestamps, s.
    timestamps: Sequence[float]
    synthetic: bool = True

    def __post_init__(self) -> None:
        if not self.synthetic:
            raise ValueError("e1a_v5 Branch-B packets are synthetic-only")

    @property
    def n_frames(self) -> int:
        return len(self.y)


@dataclass(frozen=True)
class ComparisonPacket:
    """One (block, field) comparison: locked A, calibrated observation, free B."""

    branch_a: BranchAPacket
    observation: ObservationCalibrationPacket
    branch_b: BranchBPacket

    @property
    def key(self) -> tuple[BlockId, FieldId]:
        return (self.branch_a.block, self.branch_a.field)


@dataclass(frozen=True)
class RecordResult:
    """Per-record analysis output."""

    block: BlockId
    field: FieldId
    b_hat: float | None = None
    b_se: float | None = None
    mu_hat: Sequence[float] | None = None
    a_hat: Matrix | None = None
    sigma_hat: Matrix | None = None
    absolute_interval: tuple[float, float] | None = None
    geometry_stat: float | None = None
    geometry_upper: float | None = None
    centre_stat: float | None = None
    centre_upper: float | None = None
    stationarity_upper: float | None = None
    current_stat: float | None = None
    current_upper: float | None = None
    diagnostic_stat: float | None = None
    realization_status: str | None = None
    refusals: tuple[Refusal, ...] = ()
    evaluable: bool = True

    @property
    def refused(self) -> bool:
        return bool(self.refusals)


@dataclass(frozen=True)
class ValidationCase:
    """A preregistered V-stage validation case."""

    case_id: str
    purpose: str
    #: "size", "diagnostic", "power", "control", "unit".
    family: str
    seed_namespace: str
    replicates: int
    expectation: str
    detail: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    """Outcome of one validation case."""

    case_id: str
    family: str
    replicates_run: int
    events: int
    point_estimate: float
    bound: float
    bound_kind: str  # "cp_upper" or "cp_lower"
    required: float
    passed: bool
    detail: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "family": self.family,
            "replicates_run": self.replicates_run,
            "events": self.events,
            "point_estimate": self.point_estimate,
            "bound": self.bound,
            "bound_kind": self.bound_kind,
            "required": self.required,
            "passed": self.passed,
            "detail": dict(self.detail),
        }
