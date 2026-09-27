"""Floating-point linear algebra for E1a, and the fail-closed Refusal type.

WHY FLOATS, when `gaussian_harness.numerics` mandates exact `Fraction`:
E1a's statistics are eigenvalues, principal angles and fourth standardised
moments. An eigenvalue of a rational matrix is in general irrational, so an
exact-rational policy cannot represent the quantities this experiment measures.
Floats are therefore the correct dtype HERE, and the exact-rational policy of
the Stage-A harness is untouched and not imported.

Every routine is a pure function of its arguments. No RNG, no state.

CLASSIFICATION
    mm, TT, inv, chol, jacobi, sym_pow ... EXACT UNDER STATED ASSUMPTIONS
        (exact in real arithmetic; subject to floating-point rounding, and
         `jacobi` is iterative with a declared convergence threshold)
"""

from __future__ import annotations

import math
from typing import Sequence

Matrix = list[list[float]]
Vector = list[float]


class Refusal(Exception):
    """Fail-closed refusal. Never caught to substitute a convenient default."""


def mm(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> Matrix:
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
            for i in range(len(a))]


def TT(a: Sequence[Sequence[float]]) -> Matrix:
    return [list(row) for row in zip(*a)]


def is_symmetric(a: Sequence[Sequence[float]], tol: float = 1e-12) -> bool:
    n = len(a)
    if any(len(row) != n for row in a):
        return False
    return all(abs(a[i][j] - a[j][i]) <= tol * max(1.0, abs(a[i][j])) for i in range(n) for j in range(n))


def inv(a: Sequence[Sequence[float]]) -> Matrix:
    """Gauss-Jordan with partial pivoting. Refuses a singular matrix."""
    n = len(a)
    m = [list(a[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[piv][col]) < 1e-300:
            raise Refusal("singular matrix: refusing to invert")
        m[col], m[piv] = m[piv], m[col]
        p = m[col][col]
        m[col] = [v / p for v in m[col]]
        for r in range(n):
            if r != col and m[r][col] != 0.0:
                f = m[r][col]
                m[r] = [m[r][k] - f * m[col][k] for k in range(2 * n)]
    return [row[n:] for row in m]


def chol(a: Sequence[Sequence[float]]) -> Matrix:
    """Lower Cholesky factor. Refuses a non-positive-definite matrix."""
    n = len(a)
    low: Matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = a[i][j] - sum(low[i][k] * low[j][k] for k in range(j))
            if i == j:
                if s <= 0.0:
                    raise Refusal("matrix is not positive definite")
                low[i][j] = math.sqrt(s)
            else:
                low[i][j] = s / low[j][j]
    return low


def jacobi(a: Sequence[Sequence[float]], iters: int = 500) -> tuple[list[float], Matrix]:
    """Symmetric eigensystem by cyclic Jacobi rotations, eigenvalues ascending.

    Returned as (eigenvalues, Q) with Q's COLUMNS the eigenvectors. The
    symmetric algorithm is used deliberately: forming `inv(H) @ K` and taking a
    general eigensystem is numerically unstable and is superseded by the
    whitened symmetric treatment used throughout this package.
    """
    n = len(a)
    mat = [list(row) for row in a]
    q: Matrix = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    scale = max((abs(mat[i][i]) for i in range(n)), default=1.0) or 1.0
    for _ in range(iters):
        p, r, mx = 0, min(1, n - 1), 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(mat[i][j]) > mx:
                    mx, p, r = abs(mat[i][j]), i, j
        if mx < 1e-15 * scale:
            break
        th = 0.5 * math.atan2(2 * mat[p][r], mat[p][p] - mat[r][r])
        c, s = math.cos(th), math.sin(th)
        for k in range(n):
            x, y = mat[p][k], mat[r][k]
            mat[p][k], mat[r][k] = c * x + s * y, -s * x + c * y
        for k in range(n):
            x, y = mat[k][p], mat[k][r]
            mat[k][p], mat[k][r] = c * x + s * y, -s * x + c * y
        for k in range(n):
            x, y = q[k][p], q[k][r]
            q[k][p], q[k][r] = c * x + s * y, -s * x + c * y
    order = sorted(range(n), key=lambda i: mat[i][i])
    return [mat[i][i] for i in order], [[q[k][i] for i in order] for k in range(n)]


def sym_pow(a: Sequence[Sequence[float]], power: float) -> Matrix:
    """A**power for symmetric positive-definite A, via its eigensystem."""
    lam, q = jacobi(a)
    if min(lam) <= 0.0:
        raise Refusal("sym_pow requires a positive-definite matrix")
    n = len(a)
    d = [[lam[i] ** power if i == j else 0.0 for j in range(n)] for i in range(n)]
    return mm(mm(q, d), TT(q))


def trace(a: Sequence[Sequence[float]]) -> float:
    return sum(a[i][i] for i in range(len(a)))
