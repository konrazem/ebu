"""Branch B: deterministic analysis of supplied observations, and G1-G5.

Branch B CONSUMES observations. It never generates them: there is no RNG in this
module and no trajectory is produced anywhere in this package.

    S        = (1/n) sum (x_i - x*)(x_i - x*)^T        sample covariance
    K        = S^-1                                     rarity curvature
    beta_hat = m / tr(H_A S)                            the adopted estimator

CLASSIFICATION
    S, K, beta_hat ............ EXACT (definitions, up to floating-point rounding)
    G1, G2, G3, G4 ............ EXACT functions of (H_A, K); their NULL laws are not
    G5 ........................ EXACT statistic; its finite-sample null is NOT exact
    resolvable ................ EXACT rule; its operating characteristic REQUIRES
                                STOCHASTIC VALIDATION
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from .effective_size import N_element
from .numerics import Matrix, Refusal, inv, jacobi, mm, sym_pow, trace, TT
from .status import AnalysisStatus

#: G5 centring convention, preserved from the adopted design and made explicit.
G5_WHITENING_CENTRE = "declared x_star"
G5_MOMENT_CENTRE = "sample mean of the whitened coordinate"


# --------------------------------------------------------------- Branch B basics
def sample_covariance(observations: Sequence[Sequence[float]], x_star: Sequence[float]) -> Matrix:
    n = len(observations)
    if n < 2:
        raise Refusal("sample covariance needs at least two observations")
    m = len(x_star)
    centred = [[float(row[i]) - x_star[i] for i in range(m)] for row in observations]
    return [[sum(a[i] * a[j] for a in centred) / n for j in range(m)] for i in range(m)]


def rank_guard(S: Matrix, rank_tol: float) -> float:
    """Refuse a rank-deficient or non-positive covariance BEFORE inversion."""
    lam, _ = jacobi(S)
    lo, hi = min(lam), max(lam)
    if hi <= 0.0:
        raise Refusal("accessible space invalid: non-positive covariance")
    if lo <= 0.0:
        raise Refusal(f"accessible space invalid: non-positive eigenvalue {lo:.3e}")
    if lo / hi < rank_tol:
        raise Refusal(f"accessible space invalid: lambda_min/lambda_max = {lo/hi:.3e} < {rank_tol:.0e}")
    return lo / hi


def beta_mle(H_A: Matrix, S: Matrix) -> float:
    """beta_hat = m / tr(H_A S). Never clamped, never forced towards 1."""
    m = len(H_A)
    t = trace(mm(H_A, S))
    if not math.isfinite(t) or t <= 0.0:
        raise Refusal(f"tr(H_A S) must be finite and positive, got {t!r}")
    return m / t


# --------------------------------------------------------------- mode resolvability
def resolvable(lam_a: float, lam_b: float, N_12: float, theta_cap_deg: float) -> bool:
    """True when two eigen-directions are resolvable at the adopted cap.

    merge iff  (rho - 1)/sqrt(rho)  <  1 / (theta_cap_rad * sqrt(N_12))

    with rho the ratio of the two Branch-A eigenvalues (>= 1 by construction).
    Boundary convention: equality merges, i.e. resolvable requires STRICT >.
    """
    if lam_a <= 0.0 or lam_b <= 0.0:
        raise Refusal("resolvability needs positive eigenvalues")
    rho = max(lam_a, lam_b) / min(lam_a, lam_b)
    separation = (rho - 1.0) / math.sqrt(rho)
    threshold = 1.0 / (math.radians(theta_cap_deg) * math.sqrt(N_12))
    return separation > threshold


def resolvability_boundary_ratio(N_12: float, theta_cap_deg: float) -> float:
    """The eigenvalue ratio at which (rho-1)/sqrt(rho) exactly equals the threshold."""
    u = 1.0 / (math.radians(theta_cap_deg) * math.sqrt(N_12))
    return ((u + math.sqrt(u * u + 4.0)) / 2.0) ** 2


def resolvability_blocks(lam: Sequence[float], N: Matrix, theta_cap_deg: float) -> list[list[int]]:
    """Group eigenvalue indices into blocks of mutually unresolvable directions."""
    blocks: list[list[int]] = [[0]]
    for i in range(1, len(lam)):
        prev = blocks[-1][-1]
        if resolvable(lam[prev], lam[i], N[prev][i], theta_cap_deg):
            blocks.append([i])
        else:
            blocks[-1].append(i)
    return blocks


# --------------------------------------------------------------- G1 - G5
def G1(H_A: Matrix, K: Matrix) -> float:
    """Trace-normalised shape difference. Scale-invariant in H and in K."""
    def tn(a: Matrix) -> Matrix:
        t = trace(a)
        if t == 0.0:
            raise Refusal("G1 needs a nonzero trace")
        return [[a[i][j] / t for j in range(len(a))] for i in range(len(a))]
    a, b = tn(H_A), tn(K)
    return max(abs(a[i][j] - b[i][j]) for i in range(len(a)) for j in range(len(a)))


def G2(H_A: Matrix, K: Matrix) -> float:
    """Whitened spectral spread: eigenvalue ratio of H^-1/2 K H^-1/2.

    The whitened SYMMETRIC form is used deliberately. Forming inv(H) @ K and
    taking a general eigensystem is numerically unstable and is superseded.
    """
    w = sym_pow(H_A, -0.5)
    lam, _ = jacobi(mm(mm(w, K), w))
    if min(lam) <= 0.0:
        raise Refusal("G2: whitened matrix is not positive definite")
    return max(lam) / min(lam)


def principal_angles(u: Matrix, v: Matrix) -> list[float]:
    g = mm(TT(u), v)
    ev, _ = jacobi(mm(TT(g), g))
    return [math.degrees(math.acos(min(1.0, max(0.0, math.sqrt(max(0.0, e)))))) for e in ev]


def G3(H_A: Matrix, K: Matrix, blocks: Sequence[Sequence[int]]) -> list[float]:
    """Principal angles per resolvability block, in degrees.

    An unresolved block contributes the angles between SUBSPACES, never an
    inferred direction for an individually unresolved mode.
    """
    n = len(H_A)
    _, qh = jacobi(H_A)
    _, qk = jacobi(K)
    out: list[float] = []
    for blk in blocks:
        if len(blk) == 1:
            i = blk[0]
            a = [qh[k][i] for k in range(n)]
            b = [qk[k][i] for k in range(n)]
            dot = min(1.0, max(-1.0, abs(sum(a[t] * b[t] for t in range(n)))))
            out.append(math.degrees(math.acos(dot)))
        else:
            u = [[qh[k][i] for i in blk] for k in range(n)]
            v = [[qk[k][i] for i in blk] for k in range(n)]
            out.extend(principal_angles(u, v))
    return out


def G4(H_A: Matrix, K: Matrix) -> float:
    """Worst relative disagreement between eigenvalue ratios of H and of K."""
    lh, _ = jacobi(H_A)
    lk, _ = jacobi(K)
    worst = 0.0
    for i in range(len(lh)):
        for j in range(i + 1, len(lh)):
            rh = lh[j] / lh[i]
            rk = lk[j] / lk[i]
            worst = max(worst, abs(rk - rh) / rh)
    return worst


def g2_per_mode(observations: Sequence[Sequence[float]], H_A: Matrix,
                x_star: Sequence[float]) -> list[float]:
    """Sample excess kurtosis g2 = m4/m2^2 - 3 on each whitened coordinate.

    Whitening is about the DECLARED x_star; the moments are centred on the
    SAMPLE MEAN of the whitened coordinate. Both conventions are preserved from
    the adopted design and are named in G5_WHITENING_CENTRE / G5_MOMENT_CENTRE.
    This is the sample-kurtosis estimator, NOT a raw fourth moment.
    """
    w = sym_pow(H_A, 0.5)
    m = len(H_A)
    z = [[sum(w[i][k] * (float(row[k]) - x_star[k]) for k in range(m)) for i in range(m)]
         for row in observations]
    out: list[float] = []
    for i in range(m):
        col = [row[i] for row in z]
        n = len(col)
        mu = sum(col) / n
        m2 = sum((a - mu) ** 2 for a in col) / n
        m4 = sum((a - mu) ** 4 for a in col) / n
        if m2 <= 0.0:
            raise Refusal("G5: degenerate whitened coordinate")
        out.append(m4 / (m2 * m2) - 3.0)
    return out


def G5(observations: Sequence[Sequence[float]], H_A: Matrix, x_star: Sequence[float]) -> float:
    return max(abs(g) for g in g2_per_mode(observations, H_A, x_star))


# --------------------------------------------------------------- the analysis result
@dataclass(frozen=True)
class FieldAnalysis:
    """One field's Branch-B analysis. `beta_hat` exists only when ESTIMATED."""

    field_id: str
    status: AnalysisStatus
    detail: str = ""
    S: Matrix | None = None
    K: Matrix | None = None
    beta_hat: float | None = None
    g1: float | None = None
    g2_spread: float | None = None
    g3: list[float] | None = None
    g4: float | None = None
    g5: float | None = None
    blocks: list[list[int]] | None = None
    N_matrix: Matrix | None = None

    @property
    def is_estimated(self) -> bool:
        return self.status is AnalysisStatus.ESTIMATED

    def require_beta(self) -> float:
        """Fail closed. Replaces the historical unconditional `result['beta_hat']`."""
        if not self.is_estimated or self.beta_hat is None:
            raise Refusal(
                f"{self.field_id}: beta not estimated (status {self.status.value}); "
                "downstream endpoints must fail closed"
            )
        return self.beta_hat


def analyse_field(
    field,
    observations: Sequence[Sequence[float]],
    *,
    rank_tol: float,
    theta_cap_deg: float,
    phi_modes: Sequence[float],
) -> FieldAnalysis:
    """End-to-end Branch-B analysis of ONE field's supplied observations.

    Fail-closed at every stage: a refused step yields a named status and NO
    `beta_hat`, so no downstream endpoint can read one that does not exist.
    Observations are CONSUMED, never generated.
    """
    fid = getattr(field, "field_id", "<unnamed>")
    if not getattr(field, "is_valid", True):
        return FieldAnalysis(fid, AnalysisStatus.BRANCH_A_INVALID,
                             "Branch-A field is not positive definite")
    H_A = field.H
    n = len(observations)
    try:
        S = sample_covariance(observations, field.x_star)
    except Refusal as exc:
        return FieldAnalysis(fid, AnalysisStatus.ANALYSIS_INVALID, str(exc))
    try:
        rank_guard(S, rank_tol)
    except Refusal as exc:
        return FieldAnalysis(fid, AnalysisStatus.RANK_GUARD_FAIL, str(exc), S=S)
    try:
        K = inv(S)
    except Refusal as exc:
        return FieldAnalysis(fid, AnalysisStatus.NON_POSITIVE_DEFINITE, str(exc), S=S)

    nmat = [[N_element(phi_modes[a], phi_modes[b], n) for b in range(len(phi_modes))]
            for a in range(len(phi_modes))]
    lam_h, _ = jacobi(H_A)
    blocks = resolvability_blocks(lam_h, nmat, theta_cap_deg)
    try:
        g1 = G1(H_A, K)
        g2s = G2(H_A, K)
        g3 = G3(H_A, K, blocks)
        g4 = G4(H_A, K)
        g5 = G5(observations, H_A, field.x_star)
        beta = beta_mle(H_A, S)
    except Refusal as exc:
        return FieldAnalysis(fid, AnalysisStatus.ANALYSIS_INVALID, str(exc), S=S, K=K)
    return FieldAnalysis(fid, AnalysisStatus.ESTIMATED, "", S=S, K=K, beta_hat=beta,
                         g1=g1, g2_spread=g2s, g3=g3, g4=g4, g5=g5,
                         blocks=blocks, N_matrix=nmat)
