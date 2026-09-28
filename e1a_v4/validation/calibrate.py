"""Block-1 min-p calibration generator. WRITTEN, NOT EXECUTED.

It produces the paired G1-G4 null statistics the bounded implementation consumes,
using ONLY the CALIBRATION seed family, and binds the artifact to the procedure
identity, the Branch-A geometry signature, the contract and the plan.

G5 IS DELIBERATELY ABSENT. G5 is not a function of the covariance, so generating
it here as an independent companion would destroy its real relationship to the
trajectory statistics. G5 is validated in the VALIDATION layer from fully
generated observations, where the true G1-G5 dependence arises naturally, and the
two blocks are combined by a union bound that assumes no independence.

CLASSIFICATION
    covariance-matched surrogate ... APPROXIMATION. The exact law of S for a
        correlated record is a weighted sum of chi-squares, not Wishart; the
        surrogate matches the first two moments only. Case C4 measures the
        resulting operating-quantile discrepancy. REQUIRES STOCHASTIC VALIDATION.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from ..calibration import BLOCK1_GATES, CalibrationArtifact, branch_a_signature
from ..effective_size import N_element
from ..geometry import G1, G2, G3, G4, resolvability_blocks
from ..numerics import Matrix, Refusal, chol, inv, jacobi, mm, sym_pow, TT
from .generate import Generator

GENERATOR_IDENTITY = "EBU-E1A-V4-BLOCK1-SURROGATE-CALIBRATOR-v1"


def surrogate_covariance_draw(H_A: Matrix, n: int, phis: Sequence[float],
                              rng: Generator) -> Matrix:
    """One covariance-matched surrogate draw of S. APPROXIMATION, by construction.

    S is drawn Gaussian about Sigma = H_A^-1 with the per-element covariance the
    declared correlated process implies, Cov(S_ab,S_cd) = (d_ac d_bd + d_ad d_bc)
    Sigma_aa Sigma_bb / N_ab in the Branch-A eigenbasis. The result is symmetrised
    and refused if it is not positive definite.
    """
    lam, q = jacobi(H_A)
    m = len(H_A)
    sig_modal = [1.0 / lam[r] for r in range(m)]
    draws = rng.normal(m * m)
    modal: Matrix = [[0.0] * m for _ in range(m)]
    idx = 0
    for a in range(m):
        for b in range(a, m):
            nab = N_element(phis[a], phis[b], n)
            var = (sig_modal[a] * sig_modal[b] * (1.0 + (1.0 if a == b else 0.0))) / nab
            mean = sig_modal[a] if a == b else 0.0
            val = mean + math.sqrt(var) * draws[idx]
            idx += 1
            modal[a][b] = modal[b][a] = val
    s_modal_ok, _ = jacobi(modal)
    if min(s_modal_ok) <= 0.0:
        raise Refusal("surrogate draw is not positive definite")
    return mm(mm(q, modal), TT(q))


@dataclass(frozen=True)
class CalibrationRequest:
    """Everything needed to produce one artifact. Contains no RNG."""

    field_id: str
    H_A: Matrix
    n: int
    phis: tuple[float, ...]
    replicates: int
    alpha_1: float
    theta_cap_deg: float
    procedure_identity: str
    contract_sha256: str
    plan_sha256: str


def generate_block1_artifact(request: CalibrationRequest, rng: Generator) -> CalibrationArtifact:
    """Produce the paired null draws. NOT RUN IN THE PRE-EXECUTION STAGE."""
    if request.replicates < 1:
        raise Refusal("calibration needs at least one replicate")
    lam, _ = jacobi(request.H_A)
    nmat = [[N_element(request.phis[a], request.phis[b], request.n)
             for b in range(len(request.phis))] for a in range(len(request.phis))]
    blocks = resolvability_blocks(lam, nmat, request.theta_cap_deg)
    cols: dict[str, list[float]] = {g: [] for g in BLOCK1_GATES}
    for _ in range(request.replicates):
        S = surrogate_covariance_draw(request.H_A, request.n, request.phis, rng)
        K = inv(S)
        cols["G1"].append(G1(request.H_A, K))
        cols["G2"].append(G2(request.H_A, K))
        cols["G3"].append(max(G3(request.H_A, K, blocks)))
        cols["G4"].append(G4(request.H_A, K))
    return CalibrationArtifact(
        kind="block1_min_p",
        procedure_identity=request.procedure_identity,
        field_id=request.field_id,
        n=request.n, m=len(request.H_A),
        geometry_signature=branch_a_signature(request.H_A, request.n),
        alpha_1=request.alpha_1,
        null_draws={g: tuple(cols[g]) for g in BLOCK1_GATES},
        provenance=(f"{GENERATOR_IDENTITY}|contract={request.contract_sha256[:12]}"
                    f"|plan={request.plan_sha256[:12]}|R={request.replicates}"),
        is_fixture=False)
