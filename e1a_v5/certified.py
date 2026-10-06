"""Certified derivatives: interval-arithmetic hyper-dual arithmetic.

The V4 sensitivity enclosure was rejected by independent audit, correctly.  It
combined a fine/coarse finite-difference agreement with a nine-point
least-squares smoothness residual and called the result certified.  Neither is
a bound:

* two finite-difference approximations at nearby step sizes can agree closely
  while sharing a material truncation bias, because agreement constrains the
  *difference* of their remainders, not either remainder;
* a least-squares residual over sampled points bounds the scatter at those
  points.  It says nothing about an unobserved higher derivative between them,
  and no theorem converts it into one.

V5 removes the estimate rather than patching it.  Two changes:

**No truncation error at all.**  Derivatives are evaluated by hyper-dual
arithmetic, which carries the chain rule exactly::

    x = v + d1 e1 + d2 e2 + d12 e1 e2 ,     e1^2 = e2^2 = 0

Seeding ``e1`` along one coordinate and ``e2`` along another makes the ``d12``
component of the result the exact mixed second partial derivative of the
*algorithm*.  There is no step size, so there is no truncation remainder to
bound.

**Rigorous floating-point enclosure.**  Each hyper-dual component is an
interval with outward rounding after every operation, so the returned interval
is a genuine enclosure of the exact real result of the algorithm.  IEEE-754
gives correctly-rounded ``+ - * /`` and ``sqrt``, within half an ulp, so a
one-ulp outward widening is sound; ``log`` and ``exp`` are not guaranteed
correctly rounded by the platform libm, so they are widened by two ulps.

What this does **not** claim: the enclosure bounds the error of *this
algorithm* evaluated in floating point.  It is not a bound on the distance
between the algorithm's exact output and the mathematical quantity the
algorithm approximates where the algorithm is itself iterative; those pieces
carry their own explicitly computed residual bounds, in
:mod:`e1a_v5.calibration`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

#: Unit roundoff.
EPS = 2.220446049250313e-16

Interval = tuple[float, float]


class CertificationFailure(Exception):
    """An interval operation left the domain where its bound is valid."""


# ---------------------------------------------------------------------------
# Interval primitives, outward rounded
# ---------------------------------------------------------------------------

_INF = float("inf")


def _out(lo: float, hi: float, ulps: int = 1) -> Interval:
    """Widen outward by ``ulps`` in each direction."""
    for _ in range(ulps):
        lo = math.nextafter(lo, -_INF)
        hi = math.nextafter(hi, _INF)
    return (lo, hi)


def iv(x: float) -> Interval:
    """A degenerate interval around an exactly representable float."""
    return (float(x), float(x))


def iadd(a: Interval, b: Interval) -> Interval:
    return _out(a[0] + b[0], a[1] + b[1])


def isub(a: Interval, b: Interval) -> Interval:
    return _out(a[0] - b[1], a[1] - b[0])


def ineg(a: Interval) -> Interval:
    return (-a[1], -a[0])


def imul(a: Interval, b: Interval) -> Interval:
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return _out(min(p), max(p))


def idiv(a: Interval, b: Interval) -> Interval:
    if b[0] <= 0.0 <= b[1]:
        raise CertificationFailure("interval division by an interval containing zero")
    q = (a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1])
    return _out(min(q), max(q))


def isqrt(a: Interval) -> Interval:
    if a[0] < 0.0:
        raise CertificationFailure("interval sqrt of a possibly negative interval")
    return _out(math.sqrt(a[0]), math.sqrt(a[1]))


def ilog(a: Interval) -> Interval:
    if a[0] <= 0.0:
        raise CertificationFailure("interval log of a possibly non-positive interval")
    # libm log is not guaranteed correctly rounded; widen by two ulps.
    return _out(math.log(a[0]), math.log(a[1]), ulps=2)


def iexp(a: Interval) -> Interval:
    return _out(math.exp(a[0]), math.exp(a[1]), ulps=2)


def imid(a: Interval) -> float:
    return 0.5 * (a[0] + a[1])


def irad(a: Interval) -> float:
    return 0.5 * (a[1] - a[0])


def imag(a: Interval) -> float:
    """Largest magnitude in the interval."""
    return max(abs(a[0]), abs(a[1]))


# ---------------------------------------------------------------------------
# Hyper-dual scalar over intervals
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class IHD:
    """``v + d1 e1 + d2 e2 + d12 e1 e2`` with every component an interval.

    The ``d12`` component of a result is the exact mixed second partial
    derivative of the computation with respect to whatever ``e1`` and ``e2``
    were seeded on, enclosed to floating-point rigour.
    """

    v: Interval
    d1: Interval = (0.0, 0.0)
    d2: Interval = (0.0, 0.0)
    d12: Interval = (0.0, 0.0)

    # -- construction ------------------------------------------------------
    @staticmethod
    def const(x: float) -> "IHD":
        return IHD(iv(x))

    @staticmethod
    def seed(x: float, s1: float = 0.0, s2: float = 0.0) -> "IHD":
        """Value ``x`` with first-order seeds along ``e1`` and ``e2``."""
        return IHD(iv(x), iv(s1), iv(s2), (0.0, 0.0))

    @staticmethod
    def promote(x) -> "IHD":
        return x if isinstance(x, IHD) else IHD.const(float(x))

    # -- arithmetic --------------------------------------------------------
    def __add__(self, o) -> "IHD":
        o = IHD.promote(o)
        return IHD(iadd(self.v, o.v), iadd(self.d1, o.d1),
                   iadd(self.d2, o.d2), iadd(self.d12, o.d12))

    __radd__ = __add__

    def __neg__(self) -> "IHD":
        return IHD(ineg(self.v), ineg(self.d1), ineg(self.d2), ineg(self.d12))

    def __sub__(self, o) -> "IHD":
        o = IHD.promote(o)
        return IHD(isub(self.v, o.v), isub(self.d1, o.d1),
                   isub(self.d2, o.d2), isub(self.d12, o.d12))

    def __rsub__(self, o) -> "IHD":
        return IHD.promote(o) - self

    def __mul__(self, o) -> "IHD":
        o = IHD.promote(o)
        v = imul(self.v, o.v)
        d1 = iadd(imul(self.v, o.d1), imul(self.d1, o.v))
        d2 = iadd(imul(self.v, o.d2), imul(self.d2, o.v))
        d12 = iadd(iadd(imul(self.v, o.d12), imul(self.d12, o.v)),
                   iadd(imul(self.d1, o.d2), imul(self.d2, o.d1)))
        return IHD(v, d1, d2, d12)

    __rmul__ = __mul__

    def _chain(self, f: Interval, fp: Interval, fpp: Interval) -> "IHD":
        """Apply a scalar function given its value and first two derivatives."""
        d1 = imul(fp, self.d1)
        d2 = imul(fp, self.d2)
        d12 = iadd(imul(fp, self.d12), imul(fpp, imul(self.d1, self.d2)))
        return IHD(f, d1, d2, d12)

    def __truediv__(self, o) -> "IHD":
        o = IHD.promote(o)
        # 1/o by the chain rule, then multiply: keeps one division only.
        inv = idiv(iv(1.0), o.v)
        minus_inv2 = ineg(imul(inv, inv))
        two_inv3 = imul(iv(2.0), imul(inv, imul(inv, inv)))
        return self * o._chain(inv, minus_inv2, two_inv3)

    def __rtruediv__(self, o) -> "IHD":
        return IHD.promote(o) / self

    def sqrt(self) -> "IHD":
        f = isqrt(self.v)
        fp = idiv(iv(0.5), f)
        fpp = ineg(idiv(iv(0.25), imul(f, self.v)))
        return self._chain(f, fp, fpp)

    def log(self) -> "IHD":
        f = ilog(self.v)
        fp = idiv(iv(1.0), self.v)
        fpp = ineg(idiv(iv(1.0), imul(self.v, self.v)))
        return self._chain(f, fp, fpp)

    def exp(self) -> "IHD":
        f = iexp(self.v)
        return self._chain(f, f, f)

    # -- inspection --------------------------------------------------------
    @property
    def value(self) -> float:
        return imid(self.v)

    @property
    def second(self) -> float:
        """Midpoint of the mixed second partial derivative."""
        return imid(self.d12)

    @property
    def second_radius(self) -> float:
        """Half-width of the mixed second partial derivative's enclosure."""
        return irad(self.d12)

    @property
    def first(self) -> float:
        return imid(self.d1)

    @property
    def first_radius(self) -> float:
        return irad(self.d1)

    def __abs__(self) -> float:
        """Magnitude of the VALUE component, for tolerance tests only."""
        return imag(self.v)

    def __lt__(self, o) -> bool:
        return imid(self.v) < (imid(o.v) if isinstance(o, IHD) else float(o))

    def __gt__(self, o) -> bool:
        return imid(self.v) > (imid(o.v) if isinstance(o, IHD) else float(o))

    def __le__(self, o) -> bool:
        return imid(self.v) <= (imid(o.v) if isinstance(o, IHD) else float(o))

    def __ge__(self, o) -> bool:
        return imid(self.v) >= (imid(o.v) if isinstance(o, IHD) else float(o))

    def __eq__(self, o) -> bool:  # pragma: no cover - identity comparisons only
        return isinstance(o, IHD) and (self.v, self.d1, self.d2, self.d12) == (
            o.v, o.d1, o.d2, o.d12)

    def __hash__(self) -> int:  # pragma: no cover
        return hash((self.v, self.d1, self.d2, self.d12))


# ---------------------------------------------------------------------------
# Generic scalar helpers: work on float and on IHD alike
# ---------------------------------------------------------------------------

def gsqrt(x):
    return x.sqrt() if isinstance(x, IHD) else math.sqrt(x)


def glog(x):
    return x.log() if isinstance(x, IHD) else math.log(x)


def gexp(x):
    return x.exp() if isinstance(x, IHD) else math.exp(x)


def gmag(x) -> float:
    """Magnitude as a plain float, for tolerance and pivoting decisions."""
    return abs(x) if not isinstance(x, IHD) else imag(x.v)


def gfinite(x) -> bool:
    if isinstance(x, IHD):
        return all(math.isfinite(c) for part in (x.v, x.d1, x.d2, x.d12)
                   for c in part)
    return math.isfinite(x)


def radius(x) -> float:
    """Enclosure half-width of the value component; zero for a plain float."""
    return irad(x.v) if isinstance(x, IHD) else 0.0


# ---------------------------------------------------------------------------
# Generic linear algebra: identical code at float and at IHD
# ---------------------------------------------------------------------------
#
# These mirror :mod:`e1a_v5.numerics` exactly in algorithm, so running them on
# plain floats must reproduce it.  A regression asserts that at the design
# point, which is what entitles the IHD evaluation to stand in for the cleared
# float core rather than quietly replacing it.

def gzeros(n: int, m: int | None = None):
    m = n if m is None else m
    return [[0.0 for _ in range(m)] for _ in range(n)]


def geye(n: int):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def gshape(a) -> tuple[int, int]:
    return (len(a), len(a[0]) if a else 0)


def gmatmul(a, b):
    n, k = gshape(a)
    k2, m = gshape(b)
    if k != k2:
        raise CertificationFailure("gmatmul shape mismatch")
    out = []
    for i in range(n):
        row = []
        for j in range(m):
            acc = a[i][0] * b[0][j]
            for t in range(1, k):
                acc = acc + a[i][t] * b[t][j]
            row.append(acc)
        out.append(row)
    return out


def gmatvec(a, v):
    n, k = gshape(a)
    out = []
    for i in range(n):
        acc = a[i][0] * v[0]
        for t in range(1, k):
            acc = acc + a[i][t] * v[t]
        out.append(acc)
    return out


def gadd(a, b):
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def gsub(a, b):
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def gscale(a, c):
    return [[a[i][j] * c for j in range(len(a[0]))] for i in range(len(a))]


def gtranspose(a):
    return [[a[i][j] for i in range(len(a))] for j in range(len(a[0]))]


def gsym(a):
    n = len(a)
    return [[(a[i][j] + a[j][i]) * 0.5 for j in range(n)] for i in range(n)]


def gmax_abs(a) -> float:
    return max((gmag(v) for row in a for v in row), default=0.0)


def gcholesky(a):
    """Lower Cholesky factor; same algorithm as ``numerics.cholesky``."""
    n, m = gshape(a)
    if n != m:
        raise CertificationFailure("gcholesky requires a square matrix")
    L = gzeros(n)
    for i in range(n):
        for j in range(i + 1):
            s = a[i][j]
            for t in range(j):
                s = s - L[i][t] * L[j][t]
            if i == j:
                if not gfinite(s) or gmag(s) == 0.0 or (
                    not isinstance(s, IHD) and s <= 0.0
                ) or (isinstance(s, IHD) and s.v[0] <= 0.0):
                    raise CertificationFailure(
                        f"gcholesky: not positive definite at pivot {i}"
                    )
                L[i][j] = gsqrt(s)
            else:
                L[i][j] = s / L[j][j]
    return L


def gchol_solve_mat(L, B):
    n = len(L)
    k = len(B[0])
    Y = gzeros(n, k)
    for c in range(k):
        for i in range(n):
            s = B[i][c]
            for t in range(i):
                s = s - L[i][t] * Y[t][c]
            Y[i][c] = s / L[i][i]
    X = gzeros(n, k)
    for c in range(k):
        for i in reversed(range(n)):
            s = Y[i][c]
            for t in range(i + 1, n):
                s = s - L[t][i] * X[t][c]
            X[i][c] = s / L[i][i]
    return X


def gspd_inverse(a):
    return gsym(gchol_solve_mat(gcholesky(a), geye(len(a))))


def glu_solve(a, b):
    """Solve ``a X = b`` by LU with partial pivoting.

    Pivoting compares magnitudes of the VALUE component.  That is the standard
    and sound choice: the infinitesimal and interval parts do not change which
    row is largest unless the comparison is a tie, in which case either choice
    is a valid factorisation of the same matrix.
    """
    n, m = gshape(a)
    if n != m:
        raise CertificationFailure("glu_solve requires a square matrix")
    A = [row[:] for row in a]
    B = [row[:] for row in b]
    k = len(B[0])
    scale_a = gmax_abs(a)
    floor = 1e-290 * scale_a if scale_a > 0.0 else 0.0
    for col in range(n):
        piv = max(range(col, n), key=lambda r: gmag(A[r][col]))
        if gmag(A[piv][col]) <= floor:
            raise CertificationFailure(f"glu_solve: singular at column {col}")
        if piv != col:
            A[col], A[piv] = A[piv], A[col]
            B[col], B[piv] = B[piv], B[col]
        pv = A[col][col]
        for r in range(col + 1, n):
            f = A[r][col] / pv
            if gmag(f) == 0.0:
                continue
            for c in range(col, n):
                A[r][c] = A[r][c] - f * A[col][c]
            for c in range(k):
                B[r][c] = B[r][c] - f * B[col][c]
    X = gzeros(n, k)
    for r in reversed(range(n)):
        for c in range(k):
            s = B[r][c]
            for t in range(r + 1, n):
                s = s - A[r][t] * X[t][c]
            X[r][c] = s / A[r][r]
    return X


def gexpm(a, terms: int = 18):
    """Scaling-and-squaring matrix exponential; mirrors ``numerics.expm``."""
    n, m = gshape(a)
    if n != m:
        raise CertificationFailure("gexpm requires a square matrix")
    nrm = max((sum(gmag(v) for v in row) for row in a), default=0.0)
    s = 0
    while nrm > 0.5:
        nrm /= 2.0
        s += 1
    if s > 60:
        raise CertificationFailure("gexpm scaling overflow")
    A = gscale(a, 1.0 / (2.0 ** s)) if s else [row[:] for row in a]
    result = geye(n)
    term = geye(n)
    for kk in range(1, terms + 1):
        term = gscale(gmatmul(term, A), 1.0 / kk)
        result = gadd(result, term)
    for _ in range(s):
        result = gmatmul(result, result)
    return result


#: Doubling cap for the discrete Lyapunov solve.
LYAP_DOUBLINGS = 64
#: Extra steps run past the float-determined count, so the derivative
#: components are converged well past the value components.
ITERATION_PAD = 4


def value_of(x) -> float:
    return imid(x.v) if isinstance(x, IHD) else float(x)


def value_matrix(m):
    return [[value_of(x) for x in row] for row in m]


def contains_ihd(*mats) -> bool:
    return any(isinstance(x, IHD) for m in mats for row in m for x in row)


def glyapunov_steps(f, q, doublings: int = LYAP_DOUBLINGS, tol: float = 1e-15) -> int:
    """Doublings the FLOAT iteration needs; used to fix the interval run.

    An interval iteration cannot use a convergence test: interval widths only
    grow, so the test may never fire and the iteration runs to its cap,
    accumulating width with no benefit.  The step count is therefore decided
    once on the value components and then applied verbatim to the interval
    run, which performs exactly the same arithmetic and so encloses it.
    """
    A = [row[:] for row in f]
    P = [row[:] for row in q]
    for k in range(doublings):
        AP = gmatmul(gmatmul(A, P), gtranspose(A))
        newP = gadd(P, AP)
        A = gmatmul(A, A)
        delta = gmax_abs(gsub(newP, P))
        ref = gmax_abs(newP)
        P = newP
        if ref == 0.0 or delta <= tol * ref:
            return k + 1
    return doublings


def glyapunov_fixed(f, q, steps: int):
    """``P = F P F^T + Q`` by exactly ``steps`` doublings, no convergence test."""
    A = [row[:] for row in f]
    P = [row[:] for row in q]
    for _ in range(steps):
        AP = gmatmul(gmatmul(A, P), gtranspose(A))
        P = gadd(P, AP)
        A = gmatmul(A, A)
    return gsym(P)


def glyapunov_discrete(f, q, doublings: int = LYAP_DOUBLINGS, tol: float = 1e-15):
    """Solve ``P = F P F^T + Q``; mirrors ``numerics.solve_lyapunov_discrete``."""
    if contains_ihd(f, q):
        steps = glyapunov_steps(value_matrix(f), value_matrix(q), doublings, tol)
        return glyapunov_fixed(f, q, min(doublings, steps + ITERATION_PAD))
    return glyapunov_fixed(f, q, glyapunov_steps(f, q, doublings, tol))


# ---------------------------------------------------------------------------
# The expected-likelihood path, generically
# ---------------------------------------------------------------------------
#
# One implementation of the T.6 expected log likelihood, run at float for the
# cross-check against the cleared core and at IHD for the production
# sensitivity.  Keeping a single implementation is what makes the cross-check
# meaningful: there is no second algorithm that could drift.

@dataclass(frozen=True)
class GStateSpace:
    """Generic discrete-time realisation; mirrors ``observation.StateSpace``."""

    f: list
    q: list
    c_obs: list
    r_eff: list
    s_cross: list
    offset: list
    sigma: list


def gaugmented_generator(a):
    d = len(a)
    g = gzeros(2 * d, 2 * d)
    for i in range(d):
        for j in range(d):
            g[i][j] = -a[i][j]
        g[d + i][i] = 1.0
    return g


def gvan_loan(g, diffusion, h: float):
    d2 = len(g)
    big = gzeros(2 * d2, 2 * d2)
    for i in range(d2):
        for j in range(d2):
            big[i][j] = -g[i][j]
            big[i][d2 + j] = diffusion[i][j]
            big[d2 + i][d2 + j] = g[j][i]
    m = gexpm(gscale(big, h))
    b12 = [[m[i][d2 + j] for j in range(d2)] for i in range(d2)]
    b22 = [[m[d2 + i][d2 + j] for j in range(d2)] for i in range(d2)]
    f = gtranspose(b22)
    q = gsym(gmatmul(f, b12))
    return f, q


def gbuild_state_space(a_drift, sigma, mu, p_matrix, r_obs, b_det, dt, t_exp):
    """Mirrors ``observation.build_state_space`` exactly."""
    d = len(sigma)
    if not (0.0 <= t_exp <= dt):
        raise CertificationFailure("exposure must satisfy 0 <= t_exp <= dt")
    asig = gmatmul(a_drift, sigma)
    ll = gsym(gadd(asig, gtranspose(asig)))
    gcholesky(ll)  # diffusion must be SPD; raises otherwise
    f_full = gexpm(gscale(a_drift, -dt))
    if t_exp == 0.0:
        q_trans = gsym(gsub(sigma, gmatmul(gmatmul(f_full, sigma), gtranspose(f_full))))
        return GStateSpace(
            f=f_full, q=q_trans, c_obs=[row[:] for row in p_matrix],
            r_eff=[row[:] for row in r_obs], s_cross=gzeros(d, d),
            offset=[b_det[i] + sum((p_matrix[i][j] * mu[j]) for j in range(d))
                    for i in range(d)],
            sigma=sigma,
        )
    g = gaugmented_generator(a_drift)
    diff = gzeros(2 * d, 2 * d)
    for i in range(d):
        for j in range(d):
            diff[i][j] = ll[i][j]
    phi_exp, q_exp = gvan_loan(g, diff, t_exp)
    phi_uu = [[phi_exp[i][j] for j in range(d)] for i in range(d)]
    phi_ju = [[phi_exp[d + i][j] for j in range(d)] for i in range(d)]
    q_uu = [[q_exp[i][j] for j in range(d)] for i in range(d)]
    q_jj = [[q_exp[d + i][d + j] for j in range(d)] for i in range(d)]
    q_uj = [[q_exp[i][d + j] for j in range(d)] for i in range(d)]
    gap = dt - t_exp
    if gap > 0.0:
        phi_gap = gexpm(gscale(a_drift, -gap))
        q_gap = gsym(gsub(sigma, gmatmul(gmatmul(phi_gap, sigma), gtranspose(phi_gap))))
    else:
        phi_gap = geye(d)
        q_gap = gzeros(d, d)
    scale_p = gscale(p_matrix, 1.0 / t_exp)
    c_obs = gmatmul(scale_p, phi_ju)
    r_eff = gsym(gadd(gmatmul(gmatmul(scale_p, q_jj), gtranspose(scale_p)), r_obs))
    q_trans = gsym(gadd(gmatmul(gmatmul(phi_gap, q_uu), gtranspose(phi_gap)), q_gap))
    s_cross = gmatmul(gmatmul(phi_gap, q_uj), gtranspose(scale_p))
    return GStateSpace(
        f=gmatmul(phi_gap, phi_uu), q=q_trans, c_obs=c_obs, r_eff=r_eff,
        s_cross=s_cross,
        offset=[b_det[i] + sum((p_matrix[i][j] * mu[j]) for j in range(d))
                for i in range(d)],
        sigma=sigma,
    )


#: Riccati iteration cap and convergence tolerance, relative to the
#: covariance's own scale.
RICCATI_MAX = 20000
RICCATI_TOL = 1e-14


def _riccati_step(ss: GStateSpace, p, d: int):
    ct = gtranspose(ss.c_obs)
    ft = gtranspose(ss.f)
    s_inn = gsym(gadd(gmatmul(gmatmul(ss.c_obs, p), ct), ss.r_eff))
    l = gcholesky(s_inn)
    s_inv = gchol_solve_mat(l, geye(d))
    gain = gmatmul(gadd(gmatmul(gmatmul(ss.f, p), ct), ss.s_cross), s_inv)
    p_next = gsym(gsub(gadd(gmatmul(gmatmul(ss.f, p), ft), ss.q),
                       gmatmul(gmatmul(gain, s_inn), gtranspose(gain))))
    return p_next, gain, s_inn


def _riccati_float_solution(ss_float: GStateSpace):
    """``(P, iterations)`` of the float Riccati, run to convergence."""
    d = len(ss_float.sigma)
    p = [row[:] for row in ss_float.sigma]
    for k in range(RICCATI_MAX):
        p_next, _, _ = _riccati_step(ss_float, p, d)
        scale = gmax_abs(p_next)
        delta = gmax_abs(gsub(p_next, p))
        p = p_next
        if scale > 0.0 and delta <= RICCATI_TOL * scale:
            return p, k + 1
    raise CertificationFailure("steady-state Riccati did not converge")


#: Interval refinement steps taken from the float fixed point.  The Riccati
#: map contracts by ``||F_cl||^2`` per step, which is of order 1e-4 here, so a
#: handful of steps converges the derivative components far past double
#: precision while the interval width is paid only once per step.
RICCATI_REFINE = 6


def _float_state_space(ss: GStateSpace) -> GStateSpace:
    return GStateSpace(
        f=value_matrix(ss.f), q=value_matrix(ss.q), c_obs=value_matrix(ss.c_obs),
        r_eff=value_matrix(ss.r_eff), s_cross=value_matrix(ss.s_cross),
        offset=[value_of(v) for v in ss.offset], sigma=value_matrix(ss.sigma),
    )


def gsteady_state_gain(ss: GStateSpace):
    """Steady-state predictor gain, innovation covariance, and the residual.

    The returned residual is the exact one-step Riccati residual at the point
    the iteration stopped.  The Riccati map is a contraction with factor
    ``||F_cl||^2`` in the induced norm, so a one-step residual ``r`` places the
    exact fixed point within ``r / (1 - ||F_cl||^2)``; that bound is what
    enters the certified enclosure.

    The iteration count is fixed from a float pre-run rather than decided by a
    convergence test on the interval iterate, for the reason given in
    :func:`glyapunov_steps`.
    """
    d = len(ss.sigma)
    if contains_ihd(ss.sigma, ss.f, ss.q, ss.c_obs, ss.r_eff, ss.s_cross):
        # Start the interval iteration AT the float fixed point.  Iterating
        # from Sigma instead means every early step differences two quantities
        # of Sigma's scale to produce a P several times smaller, and interval
        # arithmetic cannot see that cancellation, so the width of the large
        # scale is carried forward and compounded once per iteration.
        p_hat, _ = _riccati_float_solution(_float_state_space(ss))
        p = p_hat
        refine = RICCATI_REFINE
    else:
        p = [row[:] for row in ss.sigma]
        _, refine = _riccati_float_solution(ss)
    for _ in range(min(RICCATI_MAX, refine)):
        p, gain, s_inn = _riccati_step(ss, p, d)
    p_check, gain, s_inn = _riccati_step(ss, p, d)
    residual = gmax_abs(gsub(p_check, p))
    closed = gsub(ss.f, gmatmul(gain, ss.c_obs))
    cl_norm = max(sum(gmag(v) for v in row) for row in closed)
    return gain, s_inn, residual, cl_norm


def ginnovation_covariance(truth: GStateSpace, model: GStateSpace, gain):
    d = len(truth.sigma)
    fm_kc = gsub(model.f, gmatmul(gain, model.c_obs))
    kct = gmatmul(gain, truth.c_obs)
    m = gzeros(2 * d, 2 * d)
    for i in range(d):
        for j in range(d):
            m[i][j] = truth.f[i][j]
            m[d + i][j] = kct[i][j]
            m[d + i][d + j] = fm_kc[i][j]
    krk = gmatmul(gmatmul(gain, truth.r_eff), gtranspose(gain))
    sk = gmatmul(truth.s_cross, gtranspose(gain))
    q = gzeros(2 * d, 2 * d)
    for i in range(d):
        for j in range(d):
            q[i][j] = truth.q[i][j]
            q[i][d + j] = sk[i][j]
            q[d + i][j] = sk[j][i]
            q[d + i][d + j] = krk[i][j]
    p = glyapunov_discrete(m, gsym(q))
    g = gzeros(d, 2 * d)
    for i in range(d):
        for j in range(d):
            g[i][j] = truth.c_obs[i][j]
            g[i][d + j] = -model.c_obs[i][j]
    gpg = gmatmul(gmatmul(g, p), gtranspose(g))
    return gsym(gadd(gpg, truth.r_eff))


def ginnovation_mean(truth: GStateSpace, model: GStateSpace, gain):
    d = len(truth.sigma)
    dc = [truth.offset[i] - model.offset[i] for i in range(d)]
    if all(gmag(v) == 0.0 for v in dc):
        return [0.0] * d
    closed = gsub(model.f, gmatmul(gain, model.c_obs))
    m = gsub(geye(d), closed)
    rhs = [[v] for v in gmatvec(gain, dc)]
    xbar = [row[0] for row in glu_solve(m, rhs)]
    cx = gmatvec(model.c_obs, xbar)
    return [dc[i] - cx[i] for i in range(d)]


@dataclass(frozen=True)
class LoglikResult:
    value: object
    riccati_residual: float
    closed_loop_norm: float

    @property
    def riccati_fixed_point_bound(self) -> float:
        """Distance from the returned P to the exact Riccati fixed point.

        The iteration ``P -> F_cl P F_cl^T + (.)`` is a contraction with factor
        ``||F_cl||^2`` in the induced norm, so a one-step residual ``r`` puts
        the fixed point within ``r / (1 - ||F_cl||^2)``.
        """
        c2 = self.closed_loop_norm * self.closed_loop_norm
        if c2 >= 1.0:
            return float("inf")
        return self.riccati_residual / (1.0 - c2)


def gexpected_loglik(truth: GStateSpace, model: GStateSpace) -> LoglikResult:
    """Expected log likelihood per frame of ``model`` under data from ``truth``."""
    d = len(truth.sigma)
    gain, s_inn, residual, cl_norm = gsteady_state_gain(model)
    var_v = ginnovation_covariance(truth, model, gain)
    vbar = ginnovation_mean(truth, model, gain)
    l = gcholesky(s_inn)
    logdet = glog(l[0][0])
    for i in range(1, d):
        logdet = logdet + glog(l[i][i])
    logdet = logdet * 2.0
    s_inv = gchol_solve_mat(l, geye(d))
    tr = s_inv[0][0] * var_v[0][0]
    for i in range(d):
        for j in range(d):
            if i == 0 and j == 0:
                continue
            tr = tr + s_inv[i][j] * var_v[j][i]
    quad = vbar[0] * s_inv[0][0] * vbar[0]
    for i in range(d):
        for j in range(d):
            if i == 0 and j == 0:
                continue
            quad = quad + vbar[i] * s_inv[i][j] * vbar[j]
    total = logdet + tr + quad + d * math.log(2.0 * math.pi)
    return LoglikResult(total * -0.5, residual, cl_norm)
