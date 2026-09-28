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
from ..numerics import Matrix, Refusal, chol, inv, mm, TT


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

    def stationary_covariance(self) -> Matrix:
        scaled = [[self.beta_true * self.H_true[i][j] for j in range(len(self.H_true))]
                  for i in range(len(self.H_true))]
        return inv(scaled)


def ou_observations(truth: TruthSpec, rng: Generator) -> list[list[float]]:
    """The declared Branch-B process. Stationary at step 0; no burn-in.

        x_0     ~ N(0, Sigma)                     stationary initialisation
        x_{k+1} = phi_r x_k + sqrt(1-phi_r^2) * L z      per mode, exact transition
    """
    sigma = truth.stationary_covariance()
    low = chol(sigma)
    m = len(sigma)
    phis = [math.exp(-truth.dt / t) for t in truth.tau_true]
    z0 = rng.normal(m)
    x = [sum(low[i][k] * z0[k] for k in range(m)) for i in range(m)]
    out = [list(x)]
    for _ in range(truth.n_samples - 1):
        z = rng.normal(m)
        kick = [sum(low[i][k] * z[k] for k in range(m)) for i in range(m)]
        x = [phis[i] * x[i] + math.sqrt(1.0 - phis[i] * phis[i]) * kick[i] for i in range(m)]
        out.append(list(x))
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
    return TruthSpec(field.field_id, field.H, field.tau_modes, beta_true, dt, n_samples)
