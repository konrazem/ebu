"""Calibration artifacts for the Block-1 min-p null, and their consumption.

*** THE STOCHASTIC NULL CALIBRATION IS NOT AUTHORISED IN THIS STAGE. ***

This module implements the SCHEMA, the IDENTITY BINDING, the P-VALUE CONSUMPTION
and the DECISION SEMANTICS. It does not produce calibration draws, and it
contains no RNG. A run without a matching artifact fails closed; no threshold is
ever hard-coded and no v3 value is ever substituted.

A `CalibrationArtifact` is bound to the procedure identity AND to the Branch-A
geometry it was calibrated at, because G1/G3/G4 null laws depend on H's spectrum.

CLASSIFICATION
    p_value (empirical) ....... EXACT given the artifact; the artifact's own law is
                                a covariance-matched SURROGATE and is an APPROXIMATION
    Besag-Clifford correction . EXACT UNDER STATED ASSUMPTIONS (size <= alpha
                                CONDITIONAL on the draws coming from the true null)
    block-2 analytic p ........ APPROXIMATION (leading-order delta method)
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .effective_size import bias_g2, var_g2
from .numerics import Refusal, jacobi

BLOCK1_GATES = ("G1", "G2", "G3", "G4")


def branch_a_signature(H_A: Sequence[Sequence[float]], n: int) -> str:
    """Identity of the geometry a calibration was produced at.

    Uses the eigenvalue RATIOS (scale-invariant, matching the gates) and n.
    """
    lam, _ = jacobi(H_A)
    if min(lam) <= 0.0:
        raise Refusal("branch_a_signature needs a positive-definite H")
    base = min(lam)
    ratios = ",".join(f"{v / base:.12e}" for v in lam)
    return hashlib.sha256(f"E1A-V4-GEOM|{ratios}|n={n}".encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CalibrationArtifact:
    """Null draws for the Block-1 gates at one (geometry, n). Schema only here."""

    kind: str
    procedure_identity: str
    field_id: str
    n: int
    m: int
    geometry_signature: str
    alpha_1: float
    null_draws: Mapping[str, tuple[float, ...]]
    provenance: str = ""
    is_fixture: bool = False

    def __post_init__(self) -> None:
        if self.kind != "block1_min_p":
            raise Refusal(f"unsupported calibration kind {self.kind!r}")
        missing = [g for g in BLOCK1_GATES if g not in self.null_draws]
        if missing:
            raise Refusal(f"calibration artifact missing null draws for {missing}")
        sizes = {g: len(self.null_draws[g]) for g in BLOCK1_GATES}
        if len(set(sizes.values())) != 1:
            raise Refusal(f"calibration draws must be paired across gates, got {sizes}")
        if next(iter(sizes.values())) < 1:
            raise Refusal("calibration artifact contains no draws")

    @property
    def replicates(self) -> int:
        return len(self.null_draws["G1"])

    def p_value(self, gate: str, observed: float) -> float:
        """Barnard / Besag-Clifford Monte-Carlo p-value: (1 + #{null >= obs})/(R + 1).

        Size <= alpha for ANY R, but only CONDITIONAL on the draws coming from
        the true null law. They come from a surrogate, so the guarantee is
        conditional and the unconditional size still requires validation.
        """
        if gate not in self.null_draws:
            raise Refusal(f"no null draws for gate {gate!r}")
        draws = self.null_draws[gate]
        return (1 + sum(1 for d in draws if d >= observed)) / (len(draws) + 1)

    def p_min_null(self) -> tuple[float, ...]:
        """Null distribution of p_min, by leave-one-out over the paired draws."""
        r = self.replicates
        out: list[float] = []
        for i in range(r):
            best = 1.0
            for gate in BLOCK1_GATES:
                draws = self.null_draws[gate]
                obs = draws[i]
                p = (1 + sum(1 for j, d in enumerate(draws) if j != i and d >= obs)) / r
                best = min(best, p)
            out.append(best)
        return tuple(sorted(out))

    def critical_p_min(self) -> float:
        """The alpha_1 quantile of p_min's own null distribution."""
        nulls = self.p_min_null()
        idx = max(0, int(math.floor(self.alpha_1 * len(nulls))) - 1)
        return nulls[idx]


def require_calibration(
    artifact: CalibrationArtifact | None,
    *,
    procedure_identity: str,
    H_A: Sequence[Sequence[float]],
    n: int,
    field_id: str,
) -> CalibrationArtifact:
    """Fail closed when calibration is absent or bound to a different procedure."""
    if artifact is None:
        raise Refusal(
            f"CALIBRATION_MISSING for {field_id}: the Block-1 min-p null has not been "
            "calibrated. Stochastic calibration is a separate authorised stage; this "
            "implementation refuses rather than assuming a threshold."
        )
    if artifact.procedure_identity != procedure_identity:
        raise Refusal(
            f"CALIBRATION_IDENTITY_MISMATCH for {field_id}: artifact was produced under "
            f"{artifact.procedure_identity[:16]}..., this run is {procedure_identity[:16]}..."
        )
    expected = branch_a_signature(H_A, n)
    if artifact.geometry_signature != expected:
        raise Refusal(
            f"CALIBRATION_IDENTITY_MISMATCH for {field_id}: artifact geometry signature "
            f"{artifact.geometry_signature[:16]}... != analysed geometry {expected[:16]}..."
        )
    return artifact


def block2_p_value(g5_observed: float, phi: float, n: int) -> float:
    """APPROXIMATION: two-sided p for G5 from the leading-order delta-method null.

    g2 is approximately N(bias, 24 A4 / n). This is NOT an exact finite-sample
    null and must not be described as one.
    """
    sd = math.sqrt(var_g2(phi, n))
    if sd <= 0.0:
        raise Refusal("block2_p_value: degenerate null scale")
    z = abs(g5_observed - bias_g2(phi, n)) / sd
    return math.erfc(z / math.sqrt(2.0))
