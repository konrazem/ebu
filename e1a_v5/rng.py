"""Explicit deterministic PRNG plumbing.

No process-global implicit RNG is used anywhere in this package: every
stochastic function receives an explicit :class:`Stream`.  The underlying
algorithm is the CPython Mersenne Twister (``random.Random``), seeded from a
recorded integer and able to report and restore its full internal state.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from typing import Sequence

#: Recorded PRNG identity, written into every validation artefact.
PRNG_ALGORITHM = "python-stdlib-MersenneTwister-19937"
PRNG_VARIATE = "Box-Muller-free: random.gauss (Kinderman-Monahan ratio-of-uniforms)"


def derive_seed(*parts: object) -> int:
    """Derive a 64-bit seed deterministically from namespace parts.

    The digest input is the exact UTF-8 encoding of the parts joined by ``|``,
    so the mapping from (namespace, case, replicate) to seed is reproducible
    and inspectable, never drawn from an ambient source.
    """
    payload = "|".join(str(p) for p in parts).encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


@dataclass
class Stream:
    """An explicitly seeded random stream."""

    seed: int
    label: str = ""

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    def state(self) -> tuple:
        return self._rng.getstate()

    def set_state(self, state: tuple) -> None:
        self._rng.setstate(state)

    def gauss(self) -> float:
        return self._rng.gauss(0.0, 1.0)

    def normals(self, n: int) -> list[float]:
        g = self._rng.gauss
        return [g(0.0, 1.0) for _ in range(n)]

    def uniform(self) -> float:
        return self._rng.random()

    def spawn(self, *parts: object) -> "Stream":
        """Derive a child stream in a disjoint namespace."""
        return Stream(derive_seed(self.seed, *parts), label=f"{self.label}/{'/'.join(map(str, parts))}")


def mvn_sample(stream: Stream, mean: Sequence[float], chol: Sequence[Sequence[float]]) -> list[float]:
    """Draw from ``N(mean, L L^T)`` given the lower Cholesky factor ``L``."""
    d = len(mean)
    z = stream.normals(d)
    return [mean[i] + sum(chol[i][j] * z[j] for j in range(i + 1)) for i in range(d)]
