"""Branch A: the independently measured physical field.

ANTI-CIRCULARITY IS A TYPE BOUNDARY HERE, not a convention. A `BranchAField` is
built from mechanical and thermometric inputs only. Every construction names the
calibration route it used, and a route the contract forbids is refused:

    FORBIDDEN   power spectrum, corner frequency (k = 2 pi f_c gamma),
                equipartition (k = k_B T / sigma^2), the tested position
                histogram, any Branch-B statistic
    AUTHORISED  force-displacement with Stokes drag, independent calibrated
                thermometry

`assert_not_branch_b` additionally refuses any object carrying Branch-B
statistical output, so a sample covariance cannot be smuggled in as "stiffness".

CLASSIFICATION
    H from H_U and T ................ EXACT (definition)
    blinded scale control ........... EXACT (algebraic identity beta -> beta/c)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

from . import K_B
from .contract import ContractBinding
from .numerics import Matrix, Refusal, is_symmetric, jacobi, mm, TT

#: Attribute names that mark an object as carrying Branch-B statistical output.
BRANCH_B_MARKERS = ("sample_covariance", "S", "K", "beta_hat", "observations", "positions")


def assert_not_branch_b(obj: Any, what: str) -> None:
    """Refuse any object that looks like Branch-B statistical output."""
    for marker in BRANCH_B_MARKERS:
        if hasattr(obj, marker):
            raise Refusal(
                f"ANTI-CIRCULARITY: {what} carries Branch-B output {marker!r}; "
                "Branch A may not consume Branch-B statistics"
            )


def rotation(deg: float) -> Matrix:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [[c, -s], [s, c]]


def stiffness_matrix(k_modes: Sequence[float], rot_deg: float) -> Matrix:
    """Mechanical energy Hessian H_U from per-mode stiffnesses and trap orientation."""
    n = len(k_modes)
    hu: Matrix = [[k_modes[i] if i == j else 0.0 for j in range(n)] for i in range(n)]
    if rot_deg and n == 2:
        r = rotation(rot_deg)
        hu = mm(mm(r, hu), TT(r))
        hu = [[0.5 * (hu[i][j] + hu[j][i]) for j in range(n)] for i in range(n)]
    return hu


#: The APPROVED admissible domain of the Branch-A measured primitives, adopted
#: prospectively as disposition G6 and stated by design section 3.1:
#:
#:     For every E1a field, the Branch-A dynamic-viscosity input eta(T_theta)
#:     must be a finite real number strictly greater than zero. The bead-radius
#:     input a must be a finite real number strictly greater than zero.
#:
#: Checked on each primitive INDIVIDUALLY and BEFORE anything derived. A rule
#: stated on the product is insufficient: eta < 0 together with a < 0 gives
#: gamma = 6 pi eta a > 0 and a positive relaxation time, so a derived-quantity
#: check cannot tell that pair from a legitimate measurement.
def admissible_primitive(value: Any) -> bool:
    """Is `value` an admissible Branch-A measured primitive input?

    `bool` subclasses `int`, so `True` would otherwise pass as 1.0. A flag is
    not a physical measurement and is refused by identity, not by truthiness.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    number = float(value)
    return math.isfinite(number) and number > 0.0


@dataclass(frozen=True)
class BranchAField:
    """One declared field, measured independently of the position histogram."""

    field_id: str
    H_U: Matrix                       # mechanical energy Hessian, N/m
    T: float                          # calibrated temperature, K
    x_star: list[float]               # declared reference point
    k_modes: tuple[float, ...]        # per-mode stiffness, N/m
    rot_deg: float                    # trap-axis orientation, degrees
    viscosity: float                  # eta(T), Pa s - Branch-A measured
    bead_radius: float                # a, m - Branch-A measured
    calibration_route: str
    sigma_k: float = 0.0              # per-mode relative stiffness uncertainty
    sigma_psi_deg: float = 0.0        # trap-axis orientation uncertainty
    sigma_T: float = 0.0              # thermometry uncertainty, K
    scale_factor: float = 1.0         # 1.0 for primary data; c for the blinded control
    provenance: str = ""
    status: str = "VALID"

    def __post_init__(self) -> None:
        if not is_symmetric(self.H_U):
            raise Refusal(f"{self.field_id}: H_U must be symmetric")
        if self.T <= 0.0:
            raise Refusal(f"{self.field_id}: temperature must be positive")
        if len(self.x_star) != len(self.H_U):
            raise Refusal(f"{self.field_id}: x_star dimension mismatch")
        # PRIMITIVE PHYSICAL DOMAIN, before anything derived. A present but
        # inadmissible eta or a is a MEASUREMENT outcome, not a construction
        # error, so it takes the same disposition the measured stiffness takes:
        # the field is recorded BRANCH_A_INVALID rather than refusing to exist.
        # An ABSENT input never reaches here -- it is caught upstream by the
        # field-construction resolver and keeps its own undeclared-input
        # lifecycle, which is a different scientific state.
        if not (admissible_primitive(self.viscosity)
                and admissible_primitive(self.bead_radius)):
            object.__setattr__(self, "status", "BRANCH_A_INVALID")
        lam, _ = jacobi(self.H_U)
        if min(lam) <= 0.0:
            object.__setattr__(self, "status", "BRANCH_A_INVALID")
        if self.scale_factor <= 0.0:
            raise Refusal(f"{self.field_id}: scale factor must be positive")

    @property
    def m(self) -> int:
        return len(self.H_U)

    @property
    def H(self) -> Matrix:
        """H = H_U / (k_B T), scaled by the declared (possibly blinded) factor."""
        f = self.scale_factor / (K_B * self.T)
        return [[self.H_U[i][j] * f for j in range(self.m)] for i in range(self.m)]

    @property
    def gamma(self) -> float:
        """Stokes drag coefficient, 6 pi eta a. Branch-A measured, never fitted."""
        return 6.0 * math.pi * self.viscosity * self.bead_radius

    @property
    def tau_modes(self) -> tuple[float, ...]:
        """Per-mode relaxation times tau_r = gamma / k_r. Never one scalar."""
        return tuple(self.gamma / k for k in self.k_modes)

    @property
    def is_valid(self) -> bool:
        return self.status == "VALID"

    def blinded(self, c: float) -> "BranchAField":
        """Blinded scale control: declared scale -> c * declared scale.

        Under the ideal null the analysis must then recover beta_hat = 1/c,
        because beta_hat = m / tr(H_A S) and H_A -> c H_A. The primary field is
        NOT mutated; a new object is returned.
        """
        if c <= 0.0:
            raise Refusal("blinding factor must be positive")
        return BranchAField(
            field_id=f"{self.field_id}__blinded_c={c!r}",
            H_U=self.H_U, T=self.T, x_star=list(self.x_star), k_modes=self.k_modes,
            rot_deg=self.rot_deg, viscosity=self.viscosity, bead_radius=self.bead_radius,
            calibration_route=self.calibration_route, sigma_k=self.sigma_k,
            sigma_psi_deg=self.sigma_psi_deg, sigma_T=self.sigma_T,
            scale_factor=self.scale_factor * c,
            provenance=f"{self.provenance}|blinded_scale_control(c={c!r})",
            status=self.status,
        )


def build_field(
    binding: ContractBinding,
    spec: Mapping[str, Any],
    *,
    calibration_route: str,
    viscosity: float,
    bead_radius: float,
    x_star: Sequence[float] | None = None,
    uncertainties: Mapping[str, float] | None = None,
) -> BranchAField:
    """Build one Branch-A field from a CONTRACT field spec. Route-checked."""
    assert_not_branch_b(spec, "field specification")
    if calibration_route in binding.forbidden_branch_a_routes:
        raise Refusal(
            f"ANTI-CIRCULARITY: calibration route {calibration_route!r} is forbidden "
            f"by the adopted contract. Authorised: {binding.authorised_branch_a_routes}"
        )
    if calibration_route not in binding.authorised_branch_a_routes:
        raise Refusal(
            f"calibration route {calibration_route!r} is not on the authorised list "
            f"{binding.authorised_branch_a_routes}; refusing rather than assuming"
        )
    k_modes = tuple(float(k) * 1e-6 for k in spec["k_uN_per_m"])   # uN/m -> N/m
    rot = float(spec.get("rot_deg", 0.0))
    unc = dict(uncertainties or {})
    return BranchAField(
        field_id=str(spec["id"]),
        H_U=stiffness_matrix(k_modes, rot),
        T=float(spec["T_K"]),
        x_star=list(x_star) if x_star is not None else [0.0] * len(k_modes),
        k_modes=k_modes,
        rot_deg=rot,
        viscosity=viscosity,
        bead_radius=bead_radius,
        calibration_route=calibration_route,
        sigma_k=float(unc.get("sigma_k", 0.0)),
        sigma_psi_deg=float(unc.get("sigma_psi_deg", 0.0)),
        sigma_T=float(unc.get("sigma_T", 0.0)),
        provenance=f"contract:{binding.sha256[:12]}|route:{calibration_route}",
    )
