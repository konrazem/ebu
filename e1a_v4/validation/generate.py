"""Prospective synthetic generators. WRITTEN, NOT EXECUTED.

Two independent generating layers, each with its OWN seed family, so Branch-A
measurement error can never be a disguised function of the Branch-B trajectory:

    BRANCH B   the declared correlated observation process (exact OU transition,
               stationary initialisation), family VALIDATION / CALIBRATION /
               CONFIRMATORY / BLINDED_SCALE_CONTROL
    BRANCH A   the measurement-error model that turns H_true into the H_A the
               analysis actually receives, family BRANCH_A_MEASUREMENT

`H_true` is known to the SCORING layer. It is never passed to the analysis
pipeline: `analyse_field` receives only the Branch-A field, exactly as in the
real experiment.

NOTHING IN THIS MODULE DRAWS A NUMBER BY ITSELF. Every draw comes from an
injected generator supplied by the authorised execution stage.

CLASSIFICATION
    exact OU transition ......... EXACT (stationary covariance is exactly Sigma;
                                  Euler-Maruyama inflates it by 2/(2-dt/tau) and
                                  is NOT used)
    Branch-A measurement model .. EXACT realisation of the declared uncertainty model
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, Sequence

from ..branch_a import BranchAField, rotation, stiffness_matrix
from ..numerics import Matrix, Refusal, inv, jacobi


class Generator(Protocol):
    """Injected by the authorised execution stage. Never constructed here."""

    def normal(self, count: int) -> list[float]: ...


@dataclass(frozen=True)
class TruthSpec:
    """Synthetic truth. Known to the scoring layer, never to the analysis."""

    field_id: str
    H_true: Matrix
    tau_true: tuple[float, ...]
    beta_true: float
    dt: float
    n_samples: int
    x_star: tuple[float, ...] = ()

    def stationary_covariance(self) -> Matrix:
        scaled = [[self.beta_true * self.H_true[i][j] for j in range(len(self.H_true))]
                  for i in range(len(self.H_true))]
        return inv(scaled)


def modal_ou_parameters(truth: TruthSpec) -> tuple[Matrix, tuple[float, ...], tuple[float, ...]]:
    """Pure parameters for the exact stationary transition in H_true eigenmodes.

    ``tau_true`` is ordered with ascending eigenvalue, the same convention as
    ``jacobi``. Applying distinct mode phis directly in lab coordinates would
    destroy stationarity whenever H_true is rotated and anisotropic.
    """
    m = len(truth.H_true)
    if (m < 1 or len(truth.tau_true) != m or truth.dt <= 0.0 or
            truth.beta_true <= 0.0 or truth.n_samples < 1 or
            (truth.x_star and len(truth.x_star) != m)):
        raise Refusal("invalid dimensions or nonpositive OU truth parameters")
    eigenvalues, q = jacobi(truth.H_true)
    if any(lam <= 0.0 or not math.isfinite(lam) for lam in eigenvalues):
        raise Refusal("OU truth requires positive-definite H_true")
    if any(t <= 0.0 or not math.isfinite(t) for t in truth.tau_true):
        raise Refusal("OU truth requires positive finite modal relaxation times")
    products = [eigenvalues[r] * truth.tau_true[r] for r in range(m)]
    if any(not math.isclose(v, products[0], rel_tol=1e-10) for v in products[1:]):
        raise Refusal("modal relaxation times are not paired with H_true eigenmodes")
    phis = tuple(math.exp(-truth.dt / t) for t in truth.tau_true)
    modal_sd = tuple(1.0 / math.sqrt(truth.beta_true * lam) for lam in eigenvalues)
    return q, phis, modal_sd


def ou_observations(truth: TruthSpec, rng: Generator) -> list[list[float]]:
    """Exact stationary modal OU process, rotated back to laboratory coordinates.

    In each mode: z_0 ~ N(0, 1/(beta*lambda)), and
    z_next = phi*z + sqrt(1-phi^2)*sd*epsilon. Thus the full covariance is
    Q diag(1/(beta*lambda)) Q^T at every step, including step zero.
    """
    q, phis, modal_sd = modal_ou_parameters(truth)
    m = len(phis)
    centre = truth.x_star or (0.0,) * m
    normals = rng.normal(m)
    z = [modal_sd[r] * normals[r] for r in range(m)]
    out: list[list[float]] = []
    for step in range(truth.n_samples):
        if step:
            normals = rng.normal(m)
            z = [phis[r] * z[r] + math.sqrt(1.0 - phis[r] ** 2) * modal_sd[r] * normals[r]
                 for r in range(m)]
        out.append([centre[i] + sum(q[i][r] * z[r] for r in range(m)) for i in range(m)])
    return out


@dataclass(frozen=True)
class BranchAErrorModel:
    """The declared Branch-A measurement-error model. Its own seed family."""

    sigma_cm: float          # common-mode scale, ONE draw per experiment
    sigma_k: float           # per-mode stiffness, independent per mode
    sigma_psi_deg: float     # trap-axis orientation
    sigma_T: float           # thermometry, K

    def measure(self, field: BranchAField, rng: Generator, common_mode: float) -> BranchAField:
        """Produce the H_A the analysis receives. `common_mode` is drawn ONCE
        per experiment by the caller and shared across every field, which is what
        makes it cancel in the P2 ratio and not in P3."""
        m = len(field.k_modes)
        draws = rng.normal(m + 2)
        k_obs = tuple(k * (1.0 + self.sigma_k * draws[i]) for i, k in enumerate(field.k_modes))
        psi = field.rot_deg + self.sigma_psi_deg * draws[m]
        t_obs = field.T + self.sigma_T * draws[m + 1]
        if t_obs <= 0.0:
            raise Refusal("measured temperature must remain positive")
        return BranchAField(
            field_id=field.field_id, H_U=stiffness_matrix(k_obs, psi), T=t_obs,
            x_star=list(field.x_star), k_modes=k_obs, rot_deg=psi,
            viscosity=field.viscosity, bead_radius=field.bead_radius,
            calibration_route=field.calibration_route, sigma_k=self.sigma_k,
            sigma_psi_deg=self.sigma_psi_deg, sigma_T=self.sigma_T,
            scale_factor=field.scale_factor * (1.0 + self.sigma_cm * common_mode),
            provenance=f"{field.provenance}|branch_a_measurement",
        )


def truth_from_field(field: BranchAField, dt: float, n_samples: int,
                     beta_true: float = 1.0) -> TruthSpec:
    """Synthetic truth built from a NOISELESS Branch-A field specification."""
    # jacobi orders H eigenvalues ascending; k_modes is declared in source order
    # (theta2: 150, 60), so carry each relaxation time with its stiffness.
    tau_by_eigenvalue = tuple(t for _, t in sorted(zip(field.k_modes, field.tau_modes)))
    return TruthSpec(field.field_id, field.H, tau_by_eigenvalue, beta_true, dt,
                     n_samples, tuple(field.x_star))
