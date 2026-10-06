"""Pure-Python numerical kernel for the E1a v5 candidate implementation.

No third-party numerical library is available in the validation environment,
so every linear-algebra and special-function primitive used by the candidate
pipeline is implemented here with explicit, auditable algorithms.

Design rules taken from the controlling sources:

* T-stage section 11 requires Cholesky solves and symmetric eigenvalue/log
  calculations, never an ambient pseudoinverse or an unstable explicit matrix
  square root, with a relative backward-error ceiling of ``1e-10`` for the
  normalised 2-by-2 operations.
* Repeated positive eigenvalues are valid; approaching zero is refused.
* Every routine that can fail numerically raises :class:`NumericalFailure`
  rather than returning a silently clipped value.
"""

from __future__ import annotations

import math
from typing import Sequence

Matrix = list[list[float]]
Vector = list[float]

#: Prospective relative backward-error ceiling, T-stage section 11.
BACKWARD_ERROR_CEILING = 1e-10

# ---------------------------------------------------------------------------
# Relative tolerances.  Every one of these is deliberately RELATIVE to the
# scale of the matrix it judges.  Physical quantities here span roughly 1e-29
# (exposure covariance blocks) to 1e+16 (thermal Hessians), so any absolute
# floor -- including the common ``max(1.0, ||A||)`` idiom -- silently becomes
# either vacuous or impossibly strict depending on the operand.
# ---------------------------------------------------------------------------
#: Relative defect above which a matrix offered as symmetric is refused.
SYMMETRY_RTOL = 1e-12
#: Relative discriminant below which a 2-by-2 symmetric matrix is isotropic.
DEGENERACY_RTOL = 1e-300
#: Relative pivot below which an LU factorisation declares singularity.
PIVOT_RTOL = 1e-290


class NumericalFailure(Exception):
    """A numerical operation could not be completed to the required accuracy."""


# ---------------------------------------------------------------------------
# Basic matrix helpers
# ---------------------------------------------------------------------------

def zeros(n: int, m: int | None = None) -> Matrix:
    m = n if m is None else m
    return [[0.0] * m for _ in range(n)]


def eye(n: int) -> Matrix:
    out = zeros(n)
    for i in range(n):
        out[i][i] = 1.0
    return out


def mat(rows: Sequence[Sequence[float]]) -> Matrix:
    return [[float(v) for v in row] for row in rows]


def shape(a: Matrix) -> tuple[int, int]:
    return len(a), len(a[0]) if a else 0


def matmul(a: Matrix, b: Matrix) -> Matrix:
    n, k = shape(a)
    k2, m = shape(b)
    if k != k2:
        raise NumericalFailure(f"matmul shape mismatch {shape(a)} x {shape(b)}")
    out = zeros(n, m)
    for i in range(n):
        ai = a[i]
        oi = out[i]
        for t in range(k):
            ait = ai[t]
            if ait == 0.0:
                continue
            bt = b[t]
            for j in range(m):
                oi[j] += ait * bt[j]
    return out


def matvec(a: Matrix, v: Sequence[float]) -> Vector:
    n, k = shape(a)
    if k != len(v):
        raise NumericalFailure("matvec shape mismatch")
    return [sum(a[i][j] * v[j] for j in range(k)) for i in range(n)]


def transpose(a: Matrix) -> Matrix:
    n, m = shape(a)
    return [[a[i][j] for i in range(n)] for j in range(m)]


def add(a: Matrix, b: Matrix) -> Matrix:
    n, m = shape(a)
    return [[a[i][j] + b[i][j] for j in range(m)] for i in range(n)]


def sub(a: Matrix, b: Matrix) -> Matrix:
    n, m = shape(a)
    return [[a[i][j] - b[i][j] for j in range(m)] for i in range(n)]


def scale(a: Matrix, c: float) -> Matrix:
    n, m = shape(a)
    return [[a[i][j] * c for j in range(m)] for i in range(n)]


def symmetrise(a: Matrix) -> Matrix:
    n, m = shape(a)
    if n != m:
        raise NumericalFailure("symmetrise requires a square matrix")
    return [[0.5 * (a[i][j] + a[j][i]) for j in range(n)] for i in range(n)]


def is_finite_matrix(a: Matrix) -> bool:
    return all(math.isfinite(v) for row in a for v in row)


def max_abs(a: Matrix) -> float:
    return max((abs(v) for row in a for v in row), default=0.0)


def frobenius(a: Matrix) -> float:
    return math.sqrt(sum(v * v for row in a for v in row))


def asymmetry(a: Matrix) -> float:
    """Return ``max |a_ij - a_ji|``, the raw symmetry defect."""
    n, m = shape(a)
    if n != m:
        raise NumericalFailure("asymmetry requires a square matrix")
    return max((abs(a[i][j] - a[j][i]) for i in range(n) for j in range(n)), default=0.0)


# ---------------------------------------------------------------------------
# Cholesky factorisation and solves
# ---------------------------------------------------------------------------

def cholesky(a: Matrix) -> Matrix:
    """Lower-triangular Cholesky factor ``L`` with ``L L^T = a``.

    Raises :class:`NumericalFailure` if ``a`` is not numerically SPD.  No
    clipping or nearest-SPD repair is performed (U-stage section 28).
    """
    n, m = shape(a)
    if n != m:
        raise NumericalFailure("cholesky requires a square matrix")
    if not is_finite_matrix(a):
        raise NumericalFailure("cholesky received a non-finite matrix")
    L = zeros(n)
    for i in range(n):
        for j in range(i + 1):
            s = a[i][j] - sum(L[i][t] * L[j][t] for t in range(j))
            if i == j:
                if not math.isfinite(s) or s <= 0.0:
                    raise NumericalFailure(
                        f"matrix not positive definite at pivot {i} (value {s!r})"
                    )
                L[i][j] = math.sqrt(s)
            else:
                L[i][j] = s / L[j][j]
    return L


def chol_solve(L: Matrix, b: Sequence[float]) -> Vector:
    """Solve ``L L^T x = b`` for a lower-triangular Cholesky factor ``L``."""
    n = len(L)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(L[i][t] * y[t] for t in range(i))) / L[i][i]
    x = [0.0] * n
    for i in reversed(range(n)):
        x[i] = (y[i] - sum(L[t][i] * x[t] for t in range(i + 1, n))) / L[i][i]
    return x


def chol_solve_mat(L: Matrix, B: Matrix) -> Matrix:
    """Solve ``L L^T X = B`` column-wise."""
    n, m = shape(B)
    cols = [chol_solve(L, [B[i][j] for i in range(n)]) for j in range(m)]
    return [[cols[j][i] for j in range(m)] for i in range(n)]


def spd_inverse(a: Matrix) -> Matrix:
    """Inverse of an SPD matrix via Cholesky solves (no explicit general inverse)."""
    L = cholesky(a)
    return chol_solve_mat(L, eye(len(a)))


def spd_logdet(a: Matrix) -> float:
    L = cholesky(a)
    return 2.0 * sum(math.log(L[i][i]) for i in range(len(L)))


def spd_quadform(a: Matrix, v: Sequence[float]) -> float:
    """Return ``v^T a^{-1} v`` using a Cholesky solve."""
    L = cholesky(a)
    x = chol_solve(L, list(v))
    return sum(v[i] * x[i] for i in range(len(v)))


# ---------------------------------------------------------------------------
# Symmetric eigendecomposition
# ---------------------------------------------------------------------------

def eigh2(a: Matrix) -> tuple[tuple[float, float], Matrix]:
    """Analytic symmetric 2-by-2 eigendecomposition.

    Returns ``((lambda_min, lambda_max), Q)`` with orthonormal columns of ``Q``
    ordered to match.  Stable at repeated eigenvalues: the isotropic case
    returns the identity basis rather than dividing by a zero eigengap.
    """
    if shape(a) != (2, 2):
        raise NumericalFailure("eigh2 requires a 2-by-2 matrix")
    p, q = a[0][0], a[0][1]
    q2, r = a[1][0], a[1][1]
    # Relative to the matrix's OWN scale.  A max(1.0, .) floor here would make
    # this an absolute test, so a grossly asymmetric matrix of scale 1e-29
    # (an exposure block, say) would pass as symmetric.
    sym_scale = max(abs(p), abs(r), abs(q), abs(q2))
    if sym_scale > 0.0 and abs(q - q2) > SYMMETRY_RTOL * sym_scale:
        raise NumericalFailure(
            f"eigh2 requires a symmetric matrix "
            f"(relative defect {abs(q - q2) / sym_scale:.3e})"
        )
    q = 0.5 * (q + q2)
    tr = p + r
    diff = p - r
    disc = math.hypot(diff, 2.0 * q)
    lo = 0.5 * (tr - disc)
    hi = 0.5 * (tr + disc)
    # Degenerate (isotropic) case, judged relative to the matrix scale rather
    # than against a fixed denormal constant.
    iso_scale = max(abs(p), abs(r), abs(q))
    if disc <= 0.0 or (iso_scale > 0.0 and disc <= DEGENERACY_RTOL * iso_scale):
        return (lo, hi), eye(2)
    # Eigenvector for ``hi``: use the numerically larger of the two rows.
    if abs(diff) >= 0.0:
        v0 = [q, hi - p]
        v1 = [hi - r, q]
        n0 = math.hypot(*v0)
        n1 = math.hypot(*v1)
        if n1 >= n0:
            vx, vy = v1[0] / n1, v1[1] / n1
        elif n0 > 0.0:
            vx, vy = v0[0] / n0, v0[1] / n0
        else:  # pragma: no cover - unreachable while disc > 0
            vx, vy = 1.0, 0.0
    Q = [[-vy, vx], [vx, vy]]  # column 0 -> lo, column 1 -> hi
    return (lo, hi), Q


def _jacobi_eigh(a: Matrix, max_sweeps: int = 100) -> tuple[Vector, Matrix]:
    """Cyclic Jacobi symmetric eigendecomposition for small matrices."""
    n = len(a)
    A = [row[:] for row in a]
    V = eye(n)
    for _ in range(max_sweeps):
        off = math.sqrt(sum(A[i][j] ** 2 for i in range(n) for j in range(n) if i != j))
        if off <= 1e-300 or off <= 1e-16 * math.sqrt(
            sum(A[i][i] ** 2 for i in range(n)) + 1e-300
        ):
            break
        for p in range(n - 1):
            for q in range(p + 1, n):
                if abs(A[p][q]) <= 1e-300:
                    continue
                theta = (A[q][q] - A[p][p]) / (2.0 * A[p][q])
                t = math.copysign(1.0, theta) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0)
                s = t * c
                for k in range(n):
                    akp, akq = A[k][p], A[k][q]
                    A[k][p] = c * akp - s * akq
                    A[k][q] = s * akp + c * akq
                for k in range(n):
                    apk, aqk = A[p][k], A[q][k]
                    A[p][k] = c * apk - s * aqk
                    A[q][k] = s * apk + c * aqk
                for k in range(n):
                    vkp, vkq = V[k][p], V[k][q]
                    V[k][p] = c * vkp - s * vkq
                    V[k][q] = s * vkp + c * vkq
    vals = [A[i][i] for i in range(n)]
    order = sorted(range(n), key=lambda i: vals[i])
    svals = [vals[i] for i in order]
    svecs = [[V[r][i] for i in order] for r in range(n)]
    return svals, svecs


def eigh(a: Matrix) -> tuple[Vector, Matrix]:
    """Symmetric eigendecomposition, ascending eigenvalues, orthonormal columns."""
    a = symmetrise(a)
    if not is_finite_matrix(a):
        raise NumericalFailure("eigh received a non-finite matrix")
    if len(a) == 1:
        return [a[0][0]], [[1.0]]
    if len(a) == 2:
        (lo, hi), Q = eigh2(a)
        return [lo, hi], Q
    return _jacobi_eigh(a)


def eig_backward_error(a: Matrix, vals: Vector, Q: Matrix) -> float:
    """Relative backward error ``||Q diag(v) Q^T - a|| / ||a||``."""
    n = len(a)
    D = zeros(n)
    for i in range(n):
        D[i][i] = vals[i]
    recon = matmul(matmul(Q, D), transpose(Q))
    denom = max_abs(a)
    if denom == 0.0:
        return max_abs(sub(recon, a))
    return max_abs(sub(recon, a)) / denom


# ---------------------------------------------------------------------------
# Symmetric matrix functions
# ---------------------------------------------------------------------------

def _spd_function(a: Matrix, f, name: str, certify: bool) -> Matrix:
    vals, Q = eigh(a)
    if certify:
        err = eig_backward_error(a, vals, Q)
        if err > BACKWARD_ERROR_CEILING:
            raise NumericalFailure(
                f"{name}: eigendecomposition backward error {err:.3e} exceeds "
                f"ceiling {BACKWARD_ERROR_CEILING:.1e}"
            )
    n = len(a)
    scaleref = max(abs(v) for v in vals) if vals else 0.0
    for v in vals:
        if not math.isfinite(v) or v <= 0.0:
            raise NumericalFailure(f"{name} requires a positive definite matrix (eig {v!r})")
        if scaleref > 0.0 and v / scaleref < 1e-14:
            raise NumericalFailure(
                f"{name}: eigenvalue {v!r} approaches zero relative to {scaleref!r}"
            )
    D = zeros(n)
    for i in range(n):
        D[i][i] = f(vals[i])
    return symmetrise(matmul(matmul(Q, D), transpose(Q)))


def logm_spd(a: Matrix, certify: bool = True) -> Matrix:
    """Symmetric matrix logarithm of an SPD matrix."""
    return _spd_function(a, math.log, "logm_spd", certify)


def sqrtm_spd(a: Matrix, certify: bool = True) -> Matrix:
    """Unique symmetric positive square root of an SPD matrix."""
    return _spd_function(a, math.sqrt, "sqrtm_spd", certify)


def inv_sqrtm_spd(a: Matrix, certify: bool = True) -> Matrix:
    """Unique symmetric positive inverse square root of an SPD matrix."""
    return _spd_function(a, lambda v: 1.0 / math.sqrt(v), "inv_sqrtm_spd", certify)


def op_norm_sym(a: Matrix) -> float:
    """Operator 2-norm of a symmetric matrix."""
    vals, _ = eigh(a)
    return max(abs(v) for v in vals)


def op_norm(a: Matrix) -> float:
    """Operator 2-norm of a general square matrix via ``sqrt(lambda_max(A^T A))``."""
    ata = matmul(transpose(a), a)
    vals, _ = eigh(symmetrise(ata))
    top = max(vals)
    return math.sqrt(top) if top > 0.0 else 0.0


def cond2_spd(a: Matrix) -> float:
    """Spectral condition number of an SPD matrix."""
    vals, _ = eigh(a)
    lo, hi = min(vals), max(vals)
    if lo <= 0.0:
        raise NumericalFailure("cond2_spd requires a positive definite matrix")
    return hi / lo


def is_spd(a: Matrix) -> bool:
    try:
        cholesky(a)
    except NumericalFailure:
        return False
    return True


def generalized_eigvals_spd(a: Matrix, b: Matrix) -> Vector:
    """Ascending eigenvalues of the pencil ``(a, b)`` with ``b`` SPD.

    Uses the symmetric whitening ``b^{-1/2} a b^{-1/2}`` (T11a section 22.6.3
    forbids eigenvectors of the non-symmetric ``b^{-1} a``).
    """
    Bi = inv_sqrtm_spd(b)
    M = symmetrise(matmul(matmul(Bi, a), Bi))
    vals, _ = eigh(M)
    return vals


def whitened_contrast(a: Matrix, b: Matrix) -> Matrix:
    """Return the symmetric whitened contrast ``b^{-1/2} a b^{-1/2}``."""
    Bi = inv_sqrtm_spd(b)
    return symmetrise(matmul(matmul(Bi, a), Bi))


def log_generalized_contrast(a: Matrix, b: Matrix) -> Matrix:
    """Return ``log(b^{-1/2} a b^{-1/2})`` as a symmetric matrix."""
    return logm_spd(whitened_contrast(a, b))


# ---------------------------------------------------------------------------
# Normal distribution
# ---------------------------------------------------------------------------

_SQRT2 = math.sqrt(2.0)
_SQRT2PI = math.sqrt(2.0 * math.pi)


def norm_cdf(x: float) -> float:
    """Standard normal CDF via :func:`math.erfc` (accurate in both tails)."""
    return 0.5 * math.erfc(-x / _SQRT2)


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / _SQRT2PI


def norm_logcdf(x: float) -> float:
    """``log Phi(x)``, stable for very negative ``x``."""
    if x > -1.0:
        c = norm_cdf(x)
        if c <= 0.0:
            raise NumericalFailure("norm_logcdf underflow")
        return math.log(c)
    # Asymptotic continued-fraction style expansion for the far left tail.
    v = 0.5 * math.erfc(-x / _SQRT2)
    if v > 0.0:
        return math.log(v)
    z = -x
    s = 1.0
    term = 1.0
    for k in range(1, 12):
        term *= -(2 * k - 1) / (z * z)
        s += term
    return -0.5 * z * z - math.log(z * _SQRT2PI) + math.log(abs(s))


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF, Acklam initialisation plus Halley polish."""
    if not (0.0 < p < 1.0):
        if p == 0.0:
            return -math.inf
        if p == 1.0:
            return math.inf
        raise NumericalFailure(f"norm_ppf requires 0 < p < 1, got {p!r}")
    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )
    plow = 0.02425
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    elif p <= 1.0 - plow:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
            ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0
        )
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    # Halley refinement to full double precision.
    for _ in range(3):
        e = norm_cdf(x) - p
        u = e / norm_pdf(x)
        x = x - u / (1.0 + 0.5 * x * u)
    return x


# ---------------------------------------------------------------------------
# Regularised incomplete beta and Clopper-Pearson bounds
# ---------------------------------------------------------------------------

def _betacf(a: float, b: float, x: float) -> float:
    """Lentz continued fraction for the incomplete beta function."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + aa / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-16:
            return h
    raise NumericalFailure("incomplete beta continued fraction did not converge")


def betainc_reg(a: float, b: float, x: float) -> float:
    """Regularised incomplete beta ``I_x(a, b)``."""
    if not (0.0 <= x <= 1.0):
        raise NumericalFailure(f"betainc_reg requires 0 <= x <= 1, got {x!r}")
    if x == 0.0:
        return 0.0
    if x == 1.0:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - math.exp(
        lbeta + b * math.log1p(-x) + a * math.log(x)
    ) * _betacf(b, a, 1.0 - x) / b


def betaincinv_reg(a: float, b: float, y: float) -> float:
    """Inverse of :func:`betainc_reg` in ``x`` by monotone bisection.

    Bisection is used deliberately: it is unconditionally convergent and
    bit-reproducible, which matters more here than iteration count.
    """
    if not (0.0 <= y <= 1.0):
        raise NumericalFailure("betaincinv_reg requires 0 <= y <= 1")
    if y == 0.0:
        return 0.0
    if y == 1.0:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if mid <= lo or mid >= hi:
            break
        if betainc_reg(a, b, mid) < y:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def clopper_pearson_upper(k: int, n: int, conf: float = 0.95) -> float:
    """One-sided Clopper-Pearson upper confidence bound for a proportion.

    ``k`` successes out of ``n`` trials.  Exact (beta-quantile) construction;
    no normal approximation is used anywhere in the release criteria.
    """
    if n <= 0:
        raise NumericalFailure("clopper_pearson_upper requires n > 0")
    if not (0 <= k <= n):
        raise NumericalFailure("clopper_pearson_upper requires 0 <= k <= n")
    if k == n:
        return 1.0
    return betaincinv_reg(k + 1, n - k, conf)


def clopper_pearson_lower(k: int, n: int, conf: float = 0.95) -> float:
    """One-sided Clopper-Pearson lower confidence bound for a proportion."""
    if n <= 0:
        raise NumericalFailure("clopper_pearson_lower requires n > 0")
    if not (0 <= k <= n):
        raise NumericalFailure("clopper_pearson_lower requires 0 <= k <= n")
    if k == 0:
        return 0.0
    return betaincinv_reg(k, n - k + 1, 1.0 - conf)


def binom_sf(k: int, n: int, p: float) -> float:
    """``P(X > k)`` for ``X ~ Binomial(n, p)`` via the beta identity."""
    if k >= n:
        return 0.0
    if k < 0:
        return 1.0
    return betainc_reg(k + 1, n - k, p)


def binom_cdf(k: int, n: int, p: float) -> float:
    return 1.0 - binom_sf(k, n, p)


def max_successes_for_upper_bound(n: int, target: float, conf: float = 0.95) -> int:
    """Largest ``k`` whose Clopper-Pearson upper bound stays at or below ``target``."""
    lo, hi = 0, n
    best = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if clopper_pearson_upper(mid, n, conf) <= target:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def min_successes_for_lower_bound(n: int, target: float, conf: float = 0.95) -> int:
    """Smallest ``k`` whose Clopper-Pearson lower bound reaches ``target``."""
    lo, hi = 0, n
    best = n + 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if clopper_pearson_lower(mid, n, conf) >= target:
            best = mid
            hi = mid - 1
        else:
            lo = mid + 1
    return best


# ---------------------------------------------------------------------------
# General (non-symmetric) linear algebra: LU solve and matrix exponential
# ---------------------------------------------------------------------------

def lu_solve(a: Matrix, b: Matrix) -> Matrix:
    """Solve ``a X = b`` by LU with partial pivoting (general square ``a``).

    Singularity is judged relative to the matrix's own scale.  An absolute
    pivot floor would declare a genuinely singular matrix of scale 1e-29
    non-singular, which is exactly the SI-scale failure mode this package
    audits for.
    """
    n, m = shape(a)
    if n != m:
        raise NumericalFailure("lu_solve requires a square matrix")
    nb, k = shape(b)
    if nb != n:
        raise NumericalFailure("lu_solve shape mismatch")
    A = [row[:] for row in a]
    B = [row[:] for row in b]
    a_scale = max_abs(a)
    pivot_floor = PIVOT_RTOL * a_scale if a_scale > 0.0 else 0.0
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) <= pivot_floor:
            raise NumericalFailure(
                f"lu_solve: matrix is singular at column {col} "
                f"(pivot {abs(A[piv][col]):.3e} vs scale {a_scale:.3e})"
            )
        if piv != col:
            A[col], A[piv] = A[piv], A[col]
            B[col], B[piv] = B[piv], B[col]
        pivval = A[col][col]
        for r in range(col + 1, n):
            f = A[r][col] / pivval
            if f == 0.0:
                continue
            for c in range(col, n):
                A[r][c] -= f * A[col][c]
            for c in range(k):
                B[r][c] -= f * B[col][c]
    X = zeros(n, k)
    for r in reversed(range(n)):
        for c in range(k):
            s = B[r][c] - sum(A[r][t] * X[t][c] for t in range(r + 1, n))
            X[r][c] = s / A[r][r]
    return X


def general_inverse(a: Matrix) -> Matrix:
    """Inverse of a general square matrix via LU solves."""
    return lu_solve(a, eye(len(a)))


def expm(a: Matrix, terms: int = 18) -> Matrix:
    """Matrix exponential by scaling-and-squaring with a truncated Taylor series.

    Deterministic and dependency-free.  The squaring count is chosen so the
    scaled norm is below 1/2, where the truncated series is accurate to well
    past double precision for the matrix sizes used here (<= 6).
    """
    n, m = shape(a)
    if n != m:
        raise NumericalFailure("expm requires a square matrix")
    if not is_finite_matrix(a):
        raise NumericalFailure("expm received a non-finite matrix")
    nrm = max((sum(abs(v) for v in row) for row in a), default=0.0)
    s = 0
    while nrm > 0.5:
        nrm /= 2.0
        s += 1
    if s > 60:
        raise NumericalFailure("expm scaling overflow; matrix norm is too large")
    A = scale(a, 1.0 / (2.0 ** s)) if s else [row[:] for row in a]
    result = eye(n)
    term = eye(n)
    for k in range(1, terms + 1):
        term = scale(matmul(term, A), 1.0 / k)
        result = add(result, term)
    for _ in range(s):
        result = matmul(result, result)
    if not is_finite_matrix(result):
        raise NumericalFailure("expm produced a non-finite result")
    return result


def solve_lyapunov_discrete(f: Matrix, q: Matrix, max_iter: int = 400, tol: float = 1e-15) -> Matrix:
    """Solve ``P = F P F^T + Q`` by doubling (squared-smoothing) iteration."""
    n = len(f)
    A = [row[:] for row in f]
    P = [row[:] for row in q]
    for _ in range(max_iter):
        AP = matmul(matmul(A, P), transpose(A))
        newP = add(P, AP)
        A = matmul(A, A)
        delta = max_abs(sub(newP, P))
        ref = max_abs(newP)
        P = newP
        if ref == 0.0 or delta <= tol * ref:
            break
        if not is_finite_matrix(P):
            raise NumericalFailure("discrete Lyapunov iteration diverged")
    return symmetrise(P)
