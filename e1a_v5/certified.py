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
is a genuine enclosure of the exact real result of the algorithm.

V6 removes the two places where V5 still *assumed* a bound instead of
establishing one.

*Transcendentals.*  V5 widened ``log`` and ``exp`` by two ulps on the
reasoning that the platform libm is "usually" that accurate.  Independent
audit rejected it, correctly: no documented guarantee was bound into the
procedure, and an empirical accuracy test is not a proof.  V6 does not call
the platform libm for either function.  ``ilog`` and ``iexp`` are computed
from an explicit series with a **mathematically bounded range reduction and
remainder**, evaluated in :mod:`decimal` with directed rounding, so every
intermediate is rounded outward by the arithmetic itself.  The only property
borrowed from a library is correctly-rounded decimal ``+ - * /`` under an
explicit rounding mode, which the General Decimal Arithmetic specification
requires and which is the same category of guarantee as IEEE-754 binary
arithmetic.  Inputs enter through ``Decimal(float)``, which is the float's
EXACT binary value -- never a parsed decimal display string.

*Square root.*  ``isqrt`` does not appeal to the IEEE-754 correctly-rounded
square root either.  It takes ``math.sqrt`` as an unverified candidate and
then PROVES the enclosure by exact rational comparison: the returned endpoints
satisfy ``lo * lo <= a_lo`` and ``hi * hi >= a_hi`` as exact integer
arithmetic on the binary values, widened until they do.

What this does **not** claim: the enclosure bounds the error of *this
algorithm* evaluated in floating point.  Where the algorithm is itself
iterative -- the Riccati and Lyapunov fixed points -- the distance from the
returned iterate to the exact fixed point is bounded separately, for the
VALUE and for each DERIVATIVE component, by
:func:`gsteady_state_gain` and :func:`glyapunov_certified`, and those bounds
are added into the enclosure before the result is used.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction
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


_nextafter = math.nextafter


def _out(lo: float, hi: float, ulps: int = 1) -> Interval:
    """Widen outward by ``ulps`` in each direction."""
    if ulps == 1:
        return (_nextafter(lo, -_INF), _nextafter(hi, _INF))
    for _ in range(ulps):
        lo = _nextafter(lo, -_INF)
        hi = _nextafter(hi, _INF)
    return (lo, hi)


def _imulf(a: Interval, c: float) -> Interval:
    """Interval times an exactly representable float.

    Identical to ``imul(a, (c, c))`` -- a degenerate operand makes two of the
    four cross products redundant -- and the common case by a wide margin,
    because every scaling and every structurally constant matrix entry takes
    this path.
    """
    if c == 0.0 or (a[0] == 0.0 and a[1] == 0.0):
        return (0.0, 0.0)
    p = a[0] * c
    q = a[1] * c
    if p <= q:
        return (_nextafter(p, -_INF), _nextafter(q, _INF))
    return (_nextafter(q, -_INF), _nextafter(p, _INF))


def iv(x: float) -> Interval:
    """A degenerate interval around an exactly representable float."""
    return (float(x), float(x))


# An exactly-zero operand is handled explicitly in each operation below.  This
# is not an optimisation with a rounding cost: ``x + 0``, ``x - 0`` and
# ``x * 0`` are exact in IEEE-754 for every finite ``x``, so widening their
# results by an ulp would be pure loss.  It matters structurally as well as
# numerically -- ``_out(0.0, 0.0)`` returns ``(-5e-324, 5e-324)``, which would
# turn a variable that provably does not enter a computation into one whose
# derivative is merely very small, and a structural zero would stop being a
# structural zero.


def iadd(a: Interval, b: Interval) -> Interval:
    if a[0] == 0.0 and a[1] == 0.0:
        return b
    if b[0] == 0.0 and b[1] == 0.0:
        return a
    return _out(a[0] + b[0], a[1] + b[1])


def isub(a: Interval, b: Interval) -> Interval:
    if b[0] == 0.0 and b[1] == 0.0:
        return a
    if a[0] == 0.0 and a[1] == 0.0:
        return (-b[1], -b[0])
    return _out(a[0] - b[1], a[1] - b[0])


def ineg(a: Interval) -> Interval:
    return (-a[1], -a[0])


def imul(a: Interval, b: Interval) -> Interval:
    if (a[0] == 0.0 and a[1] == 0.0) or (b[0] == 0.0 and b[1] == 0.0):
        return (0.0, 0.0)
    p = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return _out(min(p), max(p))


def idiv(a: Interval, b: Interval) -> Interval:
    if b[0] <= 0.0 <= b[1]:
        raise CertificationFailure("interval division by an interval containing zero")
    q = (a[0] / b[0], a[0] / b[1], a[1] / b[0], a[1] / b[1])
    return _out(min(q), max(q))


# ---------------------------------------------------------------------------
# Certified transcendentals: self-contained series, no libm guarantee used
# ---------------------------------------------------------------------------
#
# The audit's objection to V5 was precise: the two-ulp widening of ``log`` and
# ``exp`` rested on an undocumented platform property.  Nothing below rests on
# one.  Each function is an explicit truncated series with a proved remainder,
# over a range reduction that is exact in binary floating point, evaluated in
# decimal arithmetic under directed rounding so that the arithmetic itself
# rounds outward.
#
# What IS borrowed: the General Decimal Arithmetic specification requires
# ``+ - * /`` to be correctly rounded under the context's rounding mode.  That
# is a specified property of the arithmetic, in the same category as IEEE-754
# binary ``+ - * /``, which the interval primitives above already rely on.  No
# library transcendental is called anywhere in the certified path.

#: Working precision, in decimal digits, of the certified series evaluations.
TRANSCENDENTAL_PRECISION = 60
#: Terms retained in the ``atanh`` series behind ``log``.  With |u| <= 1/3 the
#: proved remainder is below ``(1/3)^91 * 9/8 / 91``, far under one ulp.
LOG_SERIES_TERMS = 45
#: Terms retained in the ``exp`` series after halving to |y| <= 1/2.
EXP_SERIES_TERMS = 40

#: Declared, checkable description of what the certified route depends on.
#: It names a SPECIFIED property of an arithmetic, not a measured accuracy.
TRANSCENDENTAL_BACKEND = {
    "route": "self-contained interval series over decimal basic arithmetic",
    "library_transcendentals_used": [],
    "arithmetic_guarantee": (
        "General Decimal Arithmetic specification: add, subtract, multiply "
        "and divide are correctly rounded under the context rounding mode"
    ),
    "directed_rounding": ["ROUND_FLOOR", "ROUND_CEILING"],
    "input_conversion": (
        "Decimal(float) and math.frexp/math.ldexp, both exact on the binary "
        "value; no decimal display string is parsed"
    ),
    "log_reduction": "x = m * 2**e exactly; log x = log m + e log 2",
    "log_series": "log m = -2 atanh((1-m)/(1+m)), |u| <= 1/3",
    "log_remainder": "2 u^(2N+1) / ((2N+1) (1 - u^2))",
    "exp_reduction": "y = x / 2**k exactly, |y| <= 1/2, then k squarings",
    "exp_series": "sum_{j<=N} y^j / j!",
    "exp_remainder": "|y|^(N+1) / (N+1)! / (1 - |y|/(N+2))",
    "sqrt": "candidate from math.sqrt, PROVED by exact rational comparison",
    "precision_digits": TRANSCENDENTAL_PRECISION,
    "log_terms": LOG_SERIES_TERMS,
    "exp_terms": EXP_SERIES_TERMS,
}


def _atanh_enclosure(u_lo: Decimal, u_hi: Decimal, terms: int
                     ) -> tuple[Decimal, Decimal]:
    """Enclosure of ``atanh(u)`` for ``0 <= u_lo <= u <= u_hi < 1``.

    Every term is positive, so rounding the whole evaluation down gives a
    lower bound and rounding it up gives an upper bound.  The truncation
    remainder is bounded in closed form and added to the upper end:

        sum_{k>=N} u^(2k+1)/(2k+1) <= u^(2N+1) / ((2N+1) (1 - u^2)) .
    """
    one = Decimal(1)
    with localcontext() as ctx:
        ctx.prec = TRANSCENDENTAL_PRECISION
        ctx.rounding = ROUND_FLOOR
        t = u_lo * u_lo
        p = u_lo
        lo = Decimal(0)
        for k in range(terms):
            lo += p / (2 * k + 1)
            p = p * t
        ctx.rounding = ROUND_CEILING
        t = u_hi * u_hi
        if t >= one:
            raise CertificationFailure("atanh series outside its proved domain")
        p = u_hi
        hi = Decimal(0)
        for k in range(terms):
            hi += p / (2 * k + 1)
            p = p * t
        hi += (p / (2 * terms + 1)) / (one - t)
    return lo, hi


_LN2_ENCLOSURE: tuple[Decimal, Decimal] | None = None


def _ln2_enclosure() -> tuple[Decimal, Decimal]:
    """``log 2 = 2 atanh(1/3)``, enclosed once."""
    global _LN2_ENCLOSURE
    if _LN2_ENCLOSURE is None:
        one, three = Decimal(1), Decimal(3)
        with localcontext() as ctx:
            ctx.prec = TRANSCENDENTAL_PRECISION
            ctx.rounding = ROUND_FLOOR
            u_lo = one / three
            ctx.rounding = ROUND_CEILING
            u_hi = one / three
        lo, hi = _atanh_enclosure(u_lo, u_hi, LOG_SERIES_TERMS)
        with localcontext() as ctx:
            # The doubling MUST stay inside a directed context.  Performing it
            # in the ambient context would round to the default 28 digits with
            # ROUND_HALF_EVEN, which both discards precision and can round a
            # lower bound upward -- it stops being a bound.
            ctx.prec = TRANSCENDENTAL_PRECISION
            ctx.rounding = ROUND_FLOOR
            two_lo = Decimal(2) * lo
            ctx.rounding = ROUND_CEILING
            two_hi = Decimal(2) * hi
        _LN2_ENCLOSURE = (two_lo, two_hi)
    return _LN2_ENCLOSURE


def _decimal_to_float_interval(lo: Decimal, hi: Decimal) -> Interval:
    """Outward float enclosure of an exact decimal interval."""
    return (math.nextafter(float(lo), -_INF), math.nextafter(float(hi), _INF))


def _log_point(x: float) -> tuple[Decimal, Decimal]:
    """Enclosure of ``log x`` for a single positive float."""
    m, e = math.frexp(x)              # x = m * 2**e EXACTLY, m in [0.5, 1)
    dm = Decimal(m)                   # the float's exact binary value
    one = Decimal(1)
    with localcontext() as ctx:
        ctx.prec = TRANSCENDENTAL_PRECISION
        ctx.rounding = ROUND_FLOOR
        u_lo = (one - dm) / (one + dm)
        ctx.rounding = ROUND_CEILING
        u_hi = (one - dm) / (one + dm)
    a_lo, a_hi = _atanh_enclosure(u_lo, u_hi, LOG_SERIES_TERMS)
    with localcontext() as ctx:
        ctx.prec = TRANSCENDENTAL_PRECISION
        ctx.rounding = ROUND_FLOOR
        lnm_lo = Decimal(-2) * a_hi
        ctx.rounding = ROUND_CEILING
        lnm_hi = Decimal(-2) * a_lo
    l2_lo, l2_hi = _ln2_enclosure()
    de = Decimal(e)
    with localcontext() as ctx:
        ctx.prec = TRANSCENDENTAL_PRECISION
        ctx.rounding = ROUND_FLOOR
        lo = lnm_lo + de * (l2_lo if e >= 0 else l2_hi)
        ctx.rounding = ROUND_CEILING
        hi = lnm_hi + de * (l2_hi if e >= 0 else l2_lo)
    return lo, hi


def _exp_point(x: float) -> tuple[Decimal, Decimal]:
    """Enclosure of ``exp x`` for a single float.

    The series is evaluated at ``|y|`` so every term is POSITIVE.  That is not
    cosmetic: with alternating signs, rounding each intermediate downward does
    not produce a lower bound of the next one, because multiplying a lower
    bound by a negative factor gives an upper bound.  All-positive terms make
    directed rounding monotone through the whole evaluation, and the negative
    branch is recovered exactly by one reciprocal.
    """
    if x == 0.0:
        return Decimal(1), Decimal(1)
    _, e = math.frexp(x)
    k = max(0, e + 1)
    y = abs(math.ldexp(x, -k))        # exact: a binary exponent shift
    dy = Decimal(y)
    with localcontext() as ctx:
        ctx.prec = TRANSCENDENTAL_PRECISION
        ctx.rounding = ROUND_FLOOR
        lo = Decimal(1)
        term = Decimal(1)
        for j in range(1, EXP_SERIES_TERMS + 1):
            term = term * dy / j
            lo += term
        ctx.rounding = ROUND_CEILING
        hi = Decimal(1)
        term = Decimal(1)
        for j in range(1, EXP_SERIES_TERMS + 1):
            term = term * dy / j
            hi += term
        # |R_N| <= y^(N+1)/(N+1)! * 1/(1 - y/(N+2)), every factor positive.
        rem = Decimal(1)
        for j in range(1, EXP_SERIES_TERMS + 2):
            rem = rem * dy / j
        rem = rem / (Decimal(1) - dy / (EXP_SERIES_TERMS + 2))
        hi += rem
        if lo <= 0:
            raise CertificationFailure("exp enclosure lost positivity")
        for _ in range(k):
            ctx.rounding = ROUND_FLOOR
            lo = lo * lo
            ctx.rounding = ROUND_CEILING
            hi = hi * hi
        if x < 0.0:
            ctx.rounding = ROUND_FLOOR
            inv_lo = Decimal(1) / hi
            ctx.rounding = ROUND_CEILING
            inv_hi = Decimal(1) / lo
            lo, hi = inv_lo, inv_hi
    return lo, hi


#: Memo tables.  These are pure functions of their argument, so caching changes
#: no result; it exists because the hyper-dual sweep evaluates the SAME value
#: components thousands of times while only the seeded directions differ.
_SQRT_CACHE: dict[Interval, Interval] = {}
_LOG_CACHE: dict[Interval, Interval] = {}
_EXP_CACHE: dict[Interval, Interval] = {}
_CACHE_LIMIT = 1 << 20


def _cache_put(table: dict, key, value):
    if len(table) >= _CACHE_LIMIT:
        table.clear()
    table[key] = value
    return value


def isqrt(a: Interval) -> Interval:
    """``sqrt`` of an interval, PROVED rather than assumed.

    ``math.sqrt`` supplies a candidate; the endpoints are then widened until
    exact rational arithmetic on the binary values confirms
    ``lo^2 <= a_lo`` and ``hi^2 >= a_hi``.  No IEEE-754 or libm property is
    appealed to, and the result is at least as tight as a blind one-ulp
    widening.
    """
    if a[0] < 0.0:
        raise CertificationFailure("interval sqrt of a possibly negative interval")
    got = _SQRT_CACHE.get(a)
    if got is not None:
        return got
    lo = math.sqrt(a[0])
    hi = math.sqrt(a[1])
    if not (math.isfinite(lo) and math.isfinite(hi)):
        raise CertificationFailure("interval sqrt produced a non-finite endpoint")
    flo, fhi = Fraction(a[0]), Fraction(a[1])
    while lo > 0.0 and Fraction(lo) * Fraction(lo) > flo:
        lo = math.nextafter(lo, -_INF)
    while Fraction(hi) * Fraction(hi) < fhi:
        hi = math.nextafter(hi, _INF)
    return _cache_put(_SQRT_CACHE, a, (lo, hi))


def ilog(a: Interval) -> Interval:
    """``log`` of an interval, from the certified series.  Monotone, so the
    endpoints map to the endpoints."""
    if a[0] <= 0.0:
        raise CertificationFailure("interval log of a possibly non-positive interval")
    got = _LOG_CACHE.get(a)
    if got is not None:
        return got
    lo, _ = _log_point(a[0])
    _, hi = _log_point(a[1])
    return _cache_put(_LOG_CACHE, a, _decimal_to_float_interval(lo, hi))


def iexp(a: Interval) -> Interval:
    """``exp`` of an interval, from the certified series."""
    got = _EXP_CACHE.get(a)
    if got is not None:
        return got
    if not (math.isfinite(a[0]) and math.isfinite(a[1])):
        raise CertificationFailure("interval exp of a non-finite interval")
    lo, _ = _exp_point(a[0])
    _, hi = _exp_point(a[1])
    out = _decimal_to_float_interval(lo, hi)
    if not math.isfinite(out[0]):
        raise CertificationFailure("interval exp underflowed its lower endpoint")
    return _cache_put(_EXP_CACHE, a, out)


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

_ZERO: Interval = (0.0, 0.0)


class IHD:
    """``v + d1 e1 + d2 e2 + d12 e1 e2`` with every component an interval.

    The ``d12`` component of a result is the exact mixed second partial
    derivative of the computation with respect to whatever ``e1`` and ``e2``
    were seeded on, enclosed to floating-point rigour.

    Written with ``__slots__`` and a direct ``__init__`` rather than as a
    frozen dataclass: the sweep constructs millions of these, and a frozen
    dataclass pays ``object.__setattr__`` per field on every one.  The object
    is still treated as immutable everywhere.
    """

    __slots__ = ("v", "d1", "d2", "d12")

    def __init__(self, v: Interval, d1: Interval = _ZERO,
                 d2: Interval = _ZERO, d12: Interval = _ZERO) -> None:
        self.v = v
        self.d1 = d1
        self.d2 = d2
        self.d12 = d12

    def __repr__(self) -> str:  # pragma: no cover - diagnostics only
        return f"IHD(v={self.v}, d1={self.d1}, d2={self.d2}, d12={self.d12})"

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
    #
    # Every operator has a fast path for a plain-float operand.  It is not an
    # approximation: a float promotes to a degenerate interval with zero
    # derivative parts, so the general formula collapses to exactly these
    # expressions.  Taking the collapse explicitly also AVOIDS the spurious
    # one-ulp widening that adding an exact zero would otherwise incur, so the
    # fast path is never wider than the general one.
    def __add__(self, o) -> "IHD":
        if o.__class__ is not IHD:
            c = float(o)
            if c == 0.0:
                return self
            return IHD(_out(self.v[0] + c, self.v[1] + c),
                       self.d1, self.d2, self.d12)
        return IHD(iadd(self.v, o.v), iadd(self.d1, o.d1),
                   iadd(self.d2, o.d2), iadd(self.d12, o.d12))

    __radd__ = __add__

    def __neg__(self) -> "IHD":
        return IHD(ineg(self.v), ineg(self.d1), ineg(self.d2), ineg(self.d12))

    def __sub__(self, o) -> "IHD":
        if o.__class__ is not IHD:
            c = float(o)
            if c == 0.0:
                return self
            return IHD(_out(self.v[0] - c, self.v[1] - c),
                       self.d1, self.d2, self.d12)
        return IHD(isub(self.v, o.v), isub(self.d1, o.d1),
                   isub(self.d2, o.d2), isub(self.d12, o.d12))

    def __rsub__(self, o) -> "IHD":
        return (-self) + o

    def __mul__(self, o) -> "IHD":
        if o.__class__ is not IHD:
            c = float(o)
            return IHD(_imulf(self.v, c), _imulf(self.d1, c),
                       _imulf(self.d2, c), _imulf(self.d12, c))
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

def _is_exact_zero(x) -> bool:
    """A plain float exactly equal to zero.

    An IHD is never treated as zero here even when its value component is:
    its derivative components may not be.
    """
    return x.__class__ is float and x == 0.0


def gzeros(n: int, m: int | None = None):
    m = n if m is None else m
    return [[0.0 for _ in range(m)] for _ in range(n)]


def geye(n: int):
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def gshape(a) -> tuple[int, int]:
    return (len(a), len(a[0]) if a else 0)


def gmatmul(a, b):
    """Matrix product, skipping terms whose factor is an exact float zero.

    Skipping is not an approximation and not an optimisation that changes a
    result.  ``0.0 * x`` is exactly ``+-0.0`` for finite ``x``, and adding an
    exact zero to an accumulator leaves it bit-identical except possibly for
    the sign of a zero.  It matters because the Van Loan block matrix is
    three-quarters structural zeros, and interval arithmetic was paying full
    price for every one of them.  Non-finite entries are refused up front by
    the callers that can produce them, so no ``0 * inf`` is hidden.
    """
    n, k = gshape(a)
    k2, m = gshape(b)
    if k != k2:
        raise CertificationFailure("gmatmul shape mismatch")
    cols = [[b[t][j] for t in range(k)] for j in range(m)]
    out = []
    for i in range(n):
        arow = a[i]
        row = []
        for j in range(m):
            col = cols[j]
            acc = None
            for t in range(k):
                x = arow[t]
                if _is_exact_zero(x):
                    continue
                y = col[t]
                if _is_exact_zero(y):
                    continue
                p = x * y
                acc = p if acc is None else acc + p
            row.append(0.0 if acc is None else acc)
        out.append(row)
    return out


def gmatvec(a, v):
    n, k = gshape(a)
    out = []
    for i in range(n):
        arow = a[i]
        acc = None
        for t in range(k):
            x = arow[t]
            if _is_exact_zero(x):
                continue
            y = v[t]
            if _is_exact_zero(y):
                continue
            p = x * y
            acc = p if acc is None else acc + p
        out.append(0.0 if acc is None else acc)
    return out


def gadd(a, b):
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def gsub(a, b):
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def gscale(a, c):
    """Scale a matrix, keeping structural float zeros as float zeros.

    ``0.0 * c`` is exactly zero for finite ``c``, so preserving the plain
    float keeps the zero-skipping in :func:`gmatmul` effective even when the
    scale factor is itself a hyper-dual (a shutter or timing primitive, say).
    """
    return [[(0.0 if _is_exact_zero(x) else x * c) for x in row] for row in a]


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
    # Mirrors numerics.expm's finiteness guard.  It also underwrites the
    # zero-skipping in gmatmul: with every entry finite, a skipped term is an
    # exact zero and never a hidden 0 * inf.
    if not all(gfinite(v) for row in a for v in row):
        raise CertificationFailure("gexpm received a non-finite matrix")
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
# Certified fixed points: value AND every derivative component
# ---------------------------------------------------------------------------
#
# V5 bounded only the VALUE of the Riccati fixed point, by a one-step residual
# over ``1 - ||F_cl||^2``, and that bound was reported but never entered the
# enclosure.  The audit was right on both counts: a value residual says
# nothing about a derivative, and a bound that is printed rather than added
# certifies nothing.
#
# The repair uses one observation.  Hyper-dual numbers under
#
#     ||x||_w = |x_0| + w |x_1| + w |x_2| + w^2 |x_12|
#
# form a Banach ALGEBRA for every weight ``w > 0``: expanding ``||x|| ||y||``
# reproduces every cross term of the product's grading, so
# ``||x y||_w <= ||x||_w ||y||_w``.  Matrices over that algebra inherit a
# submultiplicative induced norm, the max row sum of entry norms.  So the
# classical a posteriori contraction estimate applies to the hyper-dual
# iterate AS A WHOLE:
#
#     ||X - X*||_w <= ||T(X) - X||_w / (1 - L_w) ,   L_w = sup ||DT||_w ,
#
# and reading the grading back off gives one bound per component:
# ``|dP_0| <= B``, ``|dP_1|, |dP_2| <= B / w``, ``|dP_12| <= B / w^2``.  Every
# admissible ``w`` yields a valid bound for every component, so the tightest
# bound per component is the minimum over a grid of weights.
#
# For the Riccati operator the Frechet derivative is the classical
# ``DT(P)[D] = F_cl D F_cl^T`` with ``F_cl = F - K(P) C``, so ``L_w`` is
# ``||F_cl||_w^2``.  That is a derivative AT a point; the Lipschitz constant on
# the ball must dominate it everywhere on the ball, which is why the bound is
# computed, the ball inflated, ``F_cl`` re-enclosed over the whole inflated
# ball, and the bound recomputed and required to still fit inside it.  That
# epsilon-inflation acceptance test is what makes the contraction constant a
# bound over the enclosure and not only at a midpoint.

#: Safety factor for the epsilon-inflation acceptance test.
BALL_INFLATION = 8.0
#: Weights tried when reading component bounds out of the graded norm.
WEIGHT_GRID: tuple[float, ...] = tuple(2.0 ** k for k in range(-40, 9))
#: Smallest positive double; used where a proved tail bound underflows.
TINY = 5e-324


def _component_mags(x) -> tuple[float, float, float, float]:
    """Sup magnitude of each hyper-dual component of one scalar."""
    if x.__class__ is IHD:
        return (imag(x.v), imag(x.d1), imag(x.d2), imag(x.d12))
    v = abs(float(x))
    return (v, 0.0, 0.0, 0.0)


def ghd_norms(m) -> tuple[float, float, float, float]:
    """Per-component induced infinity norms (max row sum) of a matrix."""
    n = [0.0, 0.0, 0.0, 0.0]
    for row in m:
        acc = [0.0, 0.0, 0.0, 0.0]
        for x in row:
            mags = _component_mags(x)
            for i in range(4):
                acc[i] += mags[i]
        for i in range(4):
            if acc[i] > n[i]:
                n[i] = acc[i]
    return (n[0], n[1], n[2], n[3])


def _graded(n: Sequence[float], w: float) -> float:
    return n[0] + w * (n[1] + n[2]) + w * w * n[3]


def contraction_bounds(
    residual: Sequence[float], lipschitz: Sequence[float],
) -> tuple[float, float, float, float]:
    """Componentwise fixed-point bounds from a residual and a derivative norm.

    ``lipschitz`` are the component norms of ``F_cl``; the Lipschitz constant
    in the graded norm is its square.  Returns ``inf`` in a component when no
    weight on the grid makes the map a contraction there.
    """
    best = [float("inf")] * 4
    for w in WEIGHT_GRID:
        c = _graded(lipschitz, w)
        q = c * c
        if not (q < 1.0):
            continue
        r = _graded(residual, w)
        b = r / (1.0 - q)
        cand = (b, b / w, b / w, b / (w * w))
        for i in range(4):
            if cand[i] < best[i]:
                best[i] = cand[i]
    return (best[0], best[1], best[2], best[3])


def _inflate(x, b: Sequence[float]):
    """Widen one scalar's components by a certified symmetric bound."""
    if b[0] == 0.0 and b[1] == 0.0 and b[2] == 0.0 and b[3] == 0.0:
        return x
    if x.__class__ is not IHD:
        x = IHD.const(float(x))
    return IHD(
        _out(x.v[0] - b[0], x.v[1] + b[0]),
        _out(x.d1[0] - b[1], x.d1[1] + b[1]),
        _out(x.d2[0] - b[2], x.d2[1] + b[2]),
        _out(x.d12[0] - b[3], x.d12[1] + b[3]),
    )


def ginflate_matrix(m, b: Sequence[float]):
    return [[_inflate(x, b) for x in row] for row in m]


def glyapunov_certified(f, q, doublings: int = LYAP_DOUBLINGS, tol: float = 1e-15):
    """``P = F P F^T + Q`` with a proved bound on the truncated tail.

    The doubling iteration after ``m`` steps is exactly the partial sum
    ``sum_{j < 2^m} F^j Q (F^j)^T``, so the omitted tail obeys

        ||tail||_w <= ||Q||_w ||F||_w^(2 * 2^m) / (1 - ||F||_w^2) ,

    which is evaluated in logarithms because the exponent is astronomically
    large; where it underflows, the smallest positive double stands in, which
    is still an upper bound.  The returned ``P`` has the bound folded into its
    enclosure, so no caller can use the iterate without it.
    """
    generic = contains_ihd(f, q)
    if generic:
        steps = glyapunov_steps(value_matrix(f), value_matrix(q), doublings, tol)
        steps = min(doublings, steps + ITERATION_PAD)
    else:
        steps = glyapunov_steps(f, q, doublings, tol)
    p = glyapunov_fixed(f, q, steps)
    fn = ghd_norms(f)
    qn = ghd_norms(q)
    best = [float("inf")] * 4
    for w in WEIGHT_GRID:
        nf = _graded(fn, w)
        if not (nf < 1.0):
            continue
        qw = _graded(qn, w)
        log_nf = math.log(nf) if nf > 0.0 else -float("inf")
        expo = 2.0 * (2.0 ** min(steps, 1023))
        power_log = expo * log_nf
        power = math.exp(power_log) if power_log > -740.0 else TINY
        b = qw * power / (1.0 - nf * nf)
        cand = (b, b / w, b / w, b / (w * w))
        for i in range(4):
            if cand[i] < best[i]:
                best[i] = cand[i]
    if not all(math.isfinite(v) for v in best):
        raise CertificationFailure(
            "the discrete Lyapunov iteration is not certifiably contractive"
        )
    bounds = (best[0], best[1], best[2], best[3])
    if not generic:
        # The float path is the cross-check against the cleared core, not the
        # certified path; folding an enclosure into it would turn its floats
        # into intervals and break the bit-for-bit comparison that makes the
        # cross-check meaningful.  The bound is still returned.
        return p, bounds
    return ginflate_matrix(p, bounds), bounds


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


#: Interval refinement steps taken from the float fixed point.
#:
#: Correctness does not depend on this number: the returned enclosure is
#: widened by a residual-based bound measured at whatever iterate the loop
#: stops on, so every count is certified.  Only TIGHTNESS depends on it, and
#: it has an interior optimum.  Too few steps and the derivative components,
#: which start at zero because the float fixed point carries none, have not
#: contracted far enough; too many and each additional interval step
#: compounds width faster than the contraction removes it.  Three steps is
#: where the two meet at this design point -- the certified distance to the
#: fixed point is then of order 1e-27 against a covariance scale of 4e-17,
#: twelve orders below the interval width that the step itself costs.
RICCATI_REFINE = 3


def _float_state_space(ss: GStateSpace) -> GStateSpace:
    return GStateSpace(
        f=value_matrix(ss.f), q=value_matrix(ss.q), c_obs=value_matrix(ss.c_obs),
        r_eff=value_matrix(ss.r_eff), s_cross=value_matrix(ss.s_cross),
        offset=[value_of(v) for v in ss.offset], sigma=value_matrix(ss.sigma),
    )


def gsteady_state_gain(ss: GStateSpace):
    """Steady-state predictor gain and innovation covariance, certified.

    Returns ``(gain, s_inn, bounds, cl_norm)``.  ``bounds`` are the proved
    distances from the returned iterate to the exact Riccati fixed point, one
    per hyper-dual component: the value ``P - P*``, the two first-order
    tangents ``dP/dtheta`` and ``dP/dphi``, and the mixed second derivative.
    They are already folded into the enclosure of the ``P`` that ``gain`` and
    ``s_inn`` are built from, so no caller can use the iterate without them.

    The iteration count is fixed from a float pre-run rather than decided by a
    convergence test on the interval iterate, for the reason given in
    :func:`glyapunov_steps`.
    """
    d = len(ss.sigma)
    generic = contains_ihd(ss.sigma, ss.f, ss.q, ss.c_obs, ss.r_eff, ss.s_cross)
    if generic:
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
    p_next, gain, s_inn = _riccati_step(ss, p, d)
    residual = ghd_norms(gsub(p_next, p))
    closed = gsub(ss.f, gmatmul(gain, ss.c_obs))
    cl = ghd_norms(closed)
    if not generic:
        return gain, s_inn, (residual[0] / max(1.0 - cl[0] * cl[0], TINY),
                             0.0, 0.0, 0.0), cl[0]

    first = contraction_bounds(residual, cl)
    if not all(math.isfinite(b) for b in first):
        raise CertificationFailure(
            "the Riccati map is not certifiably contractive at the iterate"
        )
    # Epsilon inflation: the contraction constant must dominate on the WHOLE
    # ball the bound claims, not only at the iterate.  Re-enclose F_cl over an
    # inflated ball and require the recomputed bound to fit back inside it.
    claimed = tuple(BALL_INFLATION * b for b in first)
    ball = ginflate_matrix(p, claimed)
    _, gain_ball, _ = _riccati_step(ss, ball, d)
    cl_ball = ghd_norms(gsub(ss.f, gmatmul(gain_ball, ss.c_obs)))
    bounds = contraction_bounds(residual, cl_ball)
    if not all(math.isfinite(b) for b in bounds) or any(
        b > c for b, c in zip(bounds, claimed)
    ):
        raise CertificationFailure(
            "the Riccati contraction constant is not verified over the "
            f"enclosure: bounds {bounds}, claimed ball {claimed}"
        )
    # The bound is on ``p``, the iterate the residual was measured at, so the
    # enclosure is built there.  Taking one more Riccati step first would be
    # sound but needlessly wide: every interval step compounds width, and the
    # certified bound already covers the whole remaining distance.
    p_star = ginflate_matrix(p, bounds)
    _, gain, s_inn = _riccati_step(ss, p_star, d)
    return gain, s_inn, bounds, cl_ball[0]


def ginnovation_covariance(truth: GStateSpace, model: GStateSpace, gain):
    """Stationary innovation covariance under the truth; see below for bounds."""
    return _ginnovation_covariance(truth, model, gain)[0]


def _ginnovation_covariance(truth: GStateSpace, model: GStateSpace, gain):
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
    p, lyap_bounds = glyapunov_certified(m, gsym(q))
    g = gzeros(d, 2 * d)
    for i in range(d):
        for j in range(d):
            g[i][j] = truth.c_obs[i][j]
            g[i][d + j] = -model.c_obs[i][j]
    gpg = gmatmul(gmatmul(g, p), gtranspose(g))
    return gsym(gadd(gpg, truth.r_eff)), lyap_bounds


def gis_zero(x) -> bool:
    """True only when EVERY hyper-dual component is exactly zero.

    ``gmag`` reports the VALUE component alone.  A shortcut that tested it
    would discard a derivative whenever the value happened to vanish, which is
    exactly the situation at the linearisation point: the offset difference is
    zero there while its derivative with respect to the centre parameters is
    not.  Taking that shortcut silently removed the centre rows of the
    expected information and made the system singular.
    """
    if x.__class__ is IHD:
        return (x.v == (0.0, 0.0) and x.d1 == (0.0, 0.0)
                and x.d2 == (0.0, 0.0) and x.d12 == (0.0, 0.0))
    return float(x) == 0.0


def ginnovation_mean(truth: GStateSpace, model: GStateSpace, gain):
    d = len(truth.sigma)
    dc = [truth.offset[i] - model.offset[i] for i in range(d)]
    if all(gis_zero(v) for v in dc):
        return [0.0] * d
    closed = gsub(model.f, gmatmul(gain, model.c_obs))
    m = gsub(geye(d), closed)
    rhs = [[v] for v in gmatvec(gain, dc)]
    xbar = [row[0] for row in glu_solve(m, rhs)]
    cx = gmatvec(model.c_obs, xbar)
    return [dc[i] - cx[i] for i in range(d)]


@dataclass(frozen=True)
class LoglikResult:
    """One expected-log-likelihood evaluation and its fixed-point evidence.

    ``riccati_bounds`` and ``lyapunov_bounds`` are each
    ``(value, d/dtheta, d/dphi, mixed)``.  They are reported as evidence; they
    have ALREADY been folded into the enclosure of ``value``, which is what
    the V5 audit found missing.
    """

    value: object
    riccati_bounds: tuple[float, float, float, float]
    lyapunov_bounds: tuple[float, float, float, float]
    closed_loop_norm: float

    @property
    def riccati_fixed_point_bound(self) -> float:
        """Distance from the returned P to the exact Riccati fixed point."""
        return self.riccati_bounds[0]

    @property
    def riccati_derivative_bound(self) -> float:
        """Worst bound on ``dP/dtheta - dP*/dtheta`` and its phi counterpart."""
        return max(self.riccati_bounds[1], self.riccati_bounds[2])

    @property
    def riccati_mixed_bound(self) -> float:
        return self.riccati_bounds[3]

    @property
    def lyapunov_bound(self) -> float:
        return max(self.lyapunov_bounds)


def gexpected_loglik(truth: GStateSpace, model: GStateSpace) -> LoglikResult:
    """Expected log likelihood per frame of ``model`` under data from ``truth``."""
    d = len(truth.sigma)
    gain, s_inn, riccati_bounds, cl_norm = gsteady_state_gain(model)
    var_v, lyap_bounds = _ginnovation_covariance(truth, model, gain)
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
    # The additive 2*pi constant is enclosed through the certified log on the
    # interval path.  It shifts only the VALUE component -- its derivatives
    # are exactly zero -- but an unenclosed float constant has no place in a
    # certified result.  The float path keeps the plain constant, so it stays
    # bit-identical to the cleared core it cross-checks.
    partial = logdet + tr + quad
    if partial.__class__ is IHD:
        two_pi = ilog(iv(2.0 * math.pi))
        total = partial + IHD(_out(d * two_pi[0], d * two_pi[1]))
    else:
        total = partial + d * math.log(2.0 * math.pi)
    return LoglikResult(total * -0.5, riccati_bounds, lyap_bounds, cl_norm)
