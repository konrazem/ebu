"""Future synthetic-world CONFIGURATION. Nothing here draws a random number.

Every quantity below is a deterministic function of Branch-A parameters. The
RNG is an injected interface, and the only implementation supplied in this stage
is `ForbiddenRNG`, which refuses every call. The stochastic synthetic-validation
campaign is a separate authorised stage.

CLASSIFICATION
    tau_modes, stationary_covariance, phi_modes ... EXACT (definitions)
    stationary_initial_spec ....................... EXACT specification, NOT a draw
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol, Sequence

from .branch_a import BranchAField
from .effective_size import phi_of
from .numerics import Matrix, Refusal, inv, jacobi


class RNGInterface(Protocol):
    """Injection point for the authorised stochastic stage. Not implemented here."""

    def normal(self, count: int) -> list[float]: ...


class ForbiddenRNG:
    """The only RNG available in this stage. Every call is a refusal."""

    def normal(self, count: int) -> list[float]:
        raise Refusal(
            "STOCHASTIC DRAW NOT AUTHORISED IN THIS STAGE: the synthetic-validation "
            "campaign is a separate authorisation. No random numbers, no initial "
            "states, no trajectories, no OU stepping."
        )


@dataclass(frozen=True)
class WorldConfig:
    """Deterministic configuration of one future synthetic field realisation."""

    field: BranchAField
    T_total: float          # s, record length
    dt: float               # s, sampling interval
    beta_true: float = 1.0  # the benchmark prediction; never used to force an estimate

    def __post_init__(self) -> None:
        if self.T_total <= 0.0 or self.dt <= 0.0:
            raise Refusal("T_total and dt must be positive")
        if self.dt >= min(self.field.tau_modes):
            raise Refusal("dt must be shorter than the fastest relaxation time")
        if self.beta_true <= 0.0:
            raise Refusal("beta_true must be positive")

    @property
    def n_samples(self) -> int:
        return int(round(self.T_total / self.dt))

    @property
    def tau_modes(self) -> tuple[float, ...]:
        return self.field.tau_modes

    @property
    def phi_modes(self) -> tuple[float, ...]:
        return tuple(phi_of(self.dt, tau) for tau in self.tau_modes)

    @property
    def stationary_covariance(self) -> Matrix:
        """Sigma = (beta_true * H)^-1, the stationary covariance of the future world."""
        h = self.field.H
        scaled = [[self.beta_true * h[i][j] for j in range(len(h))] for i in range(len(h))]
        return inv(scaled)

    def stationary_initial_spec(self) -> dict[str, object]:
        """SPECIFICATION of the stationary initial distribution. NOT a draw.

        Starting a trajectory at x = 0 is not stationary and needs burn-in;
        drawing x_0 from N(0, Sigma) is exactly stationary and needs none. The
        specification is recorded here so the authorised stage cannot silently
        choose the other convention.
        """
        return {
            "distribution": "multivariate_normal",
            "mean": [0.0] * self.field.m,
            "covariance": self.stationary_covariance,
            "burn_in_steps": 0,
            "rationale": "exactly stationary at step 0; no burn-in required",
            "drawn_in_this_stage": False,
        }

    def sample(self, rng: RNGInterface) -> list[list[float]]:
        """Would generate the trajectory. Refuses under the only available RNG."""
        rng.normal(1)
        raise Refusal("unreachable: ForbiddenRNG refuses first")
