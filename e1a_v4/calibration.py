"""Calibration artifacts for the Block-1 min-p null, and their consumption.

*** THE STOCHASTIC NULL CALIBRATION IS NOT AUTHORISED IN THIS STAGE. ***

This module implements the SCHEMA, the IDENTITY BINDING, the P-VALUE CONSUMPTION
and the DECISION SEMANTICS. It does not produce calibration draws, and it
contains no RNG. A run without a matching artifact fails closed; no threshold is
ever hard-coded and no v3 value is ever substituted.

REPAIR B1 — COMPLETE NULL-LAW BINDING. A `CalibrationArtifact` used to bind only
`procedure_identity` and a geometry signature over H_A's eigenvalue RATIOS and n.
That is not the null law. The Block-1 surrogate draws S with per-element variance
`Sigma_aa Sigma_bb (1 + [a==b]) / N_ab`, and `N_ab` depends on the temporal
correlation `phi_r = exp(-dt/tau_r)`. Two fields can therefore share a geometry
signature and have materially different null laws: `theta0_circular` and
`theta1_power` are both isotropic, so their eigenvalue ratios are identical, yet
their per-element effective sizes differ by a factor of about 1.47. The artifact
for one was accepted for the other, and the stored `field_id` was never compared.
`CalibrationCondition` below binds every input that changes the null law.

REPAIR B2 — NO QUADRATIC REPEATED WORK. `p_min_null` used a nested leave-one-out
scan, O(R^2), and `critical_p_min` recomputed it on every P1 evaluation. The
leave-one-out count obeys the exact finite identity

    1 + #{j != i : d_j >= d_i}  =  #{j : d_j >= d_i}

because the excluded term contributes exactly 1 (`d_i >= d_i`). Both sides are
integer counts, so this is an identity and not an approximation, and it holds
with arbitrary ties. The right-hand side is one sorted-array lookup, so the whole
null distribution costs O(R log R). It is computed ONCE at artifact construction
and stored; P1 consumes the stored threshold.

CLASSIFICATION
    p_value (empirical) ....... EXACT given the artifact; the artifact's own law is
                                a covariance-matched SURROGATE and is an APPROXIMATION
    Besag-Clifford correction . EXACT UNDER STATED ASSUMPTIONS (size <= alpha
                                CONDITIONAL on the draws coming from the true null)
    block-2 analytic p ........ APPROXIMATION (leading-order delta method)
    rank identity ............. EXACT (finite integer counts, ties included)
"""

from __future__ import annotations

import hashlib
import math
from bisect import bisect_left
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from .effective_size import bias_g2, var_g2
from .numerics import Refusal, jacobi, trace

BLOCK1_GATES = ("G1", "G2", "G3", "G4")

#: Artifact schema. Version 2 adds the complete calibration condition and the
#: precomputed null threshold. A version-1 artifact is NOT compatible and is
#: refused rather than reinterpreted; no official stochastic artifact exists yet.
CALIBRATION_ARTIFACT_SCHEMA = "e1a_v4_block1_calibration/2"


def canonical_float(x: float) -> str:
    """Exact, round-trippable, locale-independent float canonicalisation.

    `float.hex()` reproduces the IEEE-754 double exactly. A human-formatted
    rounded string must never be the scientific identity of a calibration.
    """
    v = float(x)
    if not math.isfinite(v):
        raise Refusal(f"non-finite value {x!r} cannot enter a calibration identity")
    return v.hex()


def branch_a_signature(H_A: Sequence[Sequence[float]], n: int) -> str:
    """PROVENANCE ONLY. Retained because the adopted design names it.

    It binds the eigenvalue RATIOS and n. It is NOT sufficient to identify a
    null law: it is blind to the temporal correlation and to the eigenvector
    orientation. Use `CalibrationCondition` for compatibility decisions.
    """
    lam, _ = jacobi(H_A)
    if min(lam) <= 0.0:
        raise Refusal("branch_a_signature needs a positive-definite H")
    base = min(lam)
    ratios = ",".join(f"{v / base:.12e}" for v in lam)
    return hashlib.sha256(f"E1A-V4-GEOM|{ratios}|n={n}".encode("utf-8")).hexdigest()


def normalised_H(H_A: Sequence[Sequence[float]]) -> tuple[tuple[float, ...], ...]:
    """H_A / tr(H_A): the scale-canonical representative of the null law.

    Every Block-1 gate is invariant to H_A -> c H_A for c > 0, because S scales
    as 1/c and K as c, and all four gates are built from trace-normalised or
    whitened combinations. Verified numerically to floating-point rounding. The
    normalised matrix therefore captures ALL of H_A that the null law sees: the
    eigenvalue ratios AND the eigenvector orientation, which G1 depends on
    because it compares matrix ELEMENTS in the laboratory frame.

    SCALE INVARIANCE IS EXACT IN REAL ARITHMETIC, NOT BIT-EXACT IN IEEE-754.
    `normalised_H(c*H)` differs from `normalised_H(H)` in the last unit in the
    last place, so the digest does NOT identify the two. That is deliberate and
    is the conservative direction: an artifact calibrated at H is REFUSED for
    c*H rather than silently reused. The frozen authority does not permit
    calibration reuse across fields, so refusing a mathematically legitimate
    reuse costs nothing and matches the fail-closed preference.
    """
    t = trace(H_A)
    if not math.isfinite(t) or t <= 0.0:
        raise Refusal("normalised_H needs a positive finite trace")
    return tuple(tuple(float(v) / t for v in row) for row in H_A)


@dataclass(frozen=True)
class CalibrationCondition:
    """Every input that changes the Block-1 null law, and nothing that does not.

    WHAT IS BOUND, and why (see the repair report's dependency table):

        field_id .............. provenance and fail-safe isolation. NOT the
                                mathematical protection: two fields may share a
                                name and differ in law, or differ in name and
                                share one.
        H_normalised .......... the null law's whole dependence on H_A: ratios
                                (all gates) and orientation (G1).
        n ..................... enters N_ab, hence every per-element variance.
        dt, tau_modes ......... the PRIMITIVES of the temporal law.
        phi_modes ............. the sufficient reduction, phi_r = exp(-dt/tau_r).
                                Bound alongside its primitives, not instead of
                                them, so a caller cannot supply an inconsistent
                                pair and be silently accepted.
        mode_blocks ........... derived from the four above plus theta_cap, and
                                bound as a cross-check because G3 is evaluated
                                per resolvability block.
        theta_cap_deg ......... determines mode_blocks, hence G3.
        alpha_1 ............... determines the stored critical p_min.
        replicates ............ determines the resolution of the empirical null.
        gates ................. the set p_min is minimised over.
        calibrator_identity ... which generator produced the draws.
        procedure_identity,
        contract_sha256,
        plan_sha256 ........... authority provenance, already required.

    NOT bound, with reason:
        T_total ............... exactly n * dt; adds nothing.
        N_ab .................. exactly determined by (phi_modes, n); the
                                primitives are bound instead, which is strictly
                                stronger (see repair report section B1).
        rank_tol .............. never read on the calibration path.
        alpha_2 ............... block 2 only; not a Block-1 input.
        delta_cross/delta_abs/z  P2 and P3 only.
        sigma_k/cm/psi/T ...... the calibrator never reads them.
        overall scale of H_A .. cancels in exact arithmetic; the normalised form is
                                the canonical representative. NOT bit-invariant, so
                                the digest is fail-closed about scale by one ulp.
    """

    field_id: str
    m: int
    H_normalised: tuple[tuple[float, ...], ...]
    n: int
    dt: float
    tau_modes: tuple[float, ...]
    phi_modes: tuple[float, ...]
    mode_blocks: tuple[tuple[int, ...], ...]
    theta_cap_deg: float
    alpha_1: float
    replicates: int
    gates: tuple[str, ...]
    calibrator_identity: str
    procedure_identity: str
    contract_sha256: str
    plan_sha256: str

    def __post_init__(self) -> None:
        if not self.field_id:
            raise Refusal("calibration condition needs a field_id")
        if self.m < 1 or len(self.H_normalised) != self.m:
            raise Refusal("calibration condition: H dimension mismatch")
        if any(len(row) != self.m for row in self.H_normalised):
            raise Refusal("calibration condition: H must be square")
        if self.n < 2:
            raise Refusal("calibration condition: n must be at least 2")
        if len(self.phi_modes) != self.m or len(self.tau_modes) != self.m:
            raise Refusal("calibration condition: one phi and one tau per mode")
        if self.dt <= 0.0 or any(t <= 0.0 for t in self.tau_modes):
            raise Refusal("calibration condition: dt and tau must be positive")
        for phi, tau in zip(self.phi_modes, self.tau_modes):
            if not (0.0 <= phi < 1.0):
                raise Refusal(f"calibration condition: phi must satisfy 0 <= phi < 1, got {phi!r}")
            implied = math.exp(-self.dt / tau)
            if abs(phi - implied) > 1e-12 * max(1.0, implied):
                raise Refusal(
                    "calibration condition: phi_modes disagree with exp(-dt/tau_modes); "
                    "the primitives and their reduction must be consistent"
                )
        if self.replicates < 1:
            raise Refusal("calibration condition: replicates must be positive")
        if tuple(self.gates) != BLOCK1_GATES:
            raise Refusal(f"calibration condition: gate set must be {BLOCK1_GATES}")
        flat = [i for blk in self.mode_blocks for i in blk]
        if sorted(flat) != list(range(self.m)):
            raise Refusal("calibration condition: mode blocks must partition the modes")

    def canonical(self) -> dict[str, Any]:
        """The exact preimage. Floats via `float.hex()`, never rounded text."""
        return {
            "schema": CALIBRATION_ARTIFACT_SCHEMA,
            "field_id": self.field_id,
            "m": self.m,
            "H_normalised": [[canonical_float(v) for v in row] for row in self.H_normalised],
            "n": self.n,
            "dt": canonical_float(self.dt),
            "tau_modes": [canonical_float(t) for t in self.tau_modes],
            "phi_modes": [canonical_float(p) for p in self.phi_modes],
            "mode_blocks": [list(b) for b in self.mode_blocks],
            "theta_cap_deg": canonical_float(self.theta_cap_deg),
            "alpha_1": canonical_float(self.alpha_1),
            "replicates": self.replicates,
            "gates": list(self.gates),
            "calibrator_identity": self.calibrator_identity,
            "procedure_identity": self.procedure_identity,
            "contract_sha256": self.contract_sha256,
            "plan_sha256": self.plan_sha256,
        }

    def preimage(self) -> str:
        import json
        return json.dumps(self.canonical(), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True)

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.preimage().encode("utf-8")).hexdigest()

    def first_difference(self, other: "CalibrationCondition") -> str | None:
        """The first component that differs. Makes a refusal diagnosable."""
        mine, theirs = self.canonical(), other.canonical()
        for key in sorted(mine):
            if mine[key] != theirs.get(key):
                return key
        return None


def ge_counts(sorted_ascending: Sequence[float], value: float) -> int:
    """#{d in draws : d >= value}, exact with ties, by one sorted lookup."""
    return len(sorted_ascending) - bisect_left(sorted_ascending, value)


def p_min_null_reference(null_draws: Mapping[str, Sequence[float]],
                         gates: Sequence[str] = BLOCK1_GATES) -> tuple[float, ...]:
    """REFERENCE ONLY, kept for equivalence tests. The superseded O(R^2) form.

    Never called on the execution path. `CalibrationArtifact.p_min_null` returns
    the same values in O(R log R).
    """
    r = len(null_draws[gates[0]])
    out: list[float] = []
    for i in range(r):
        best = 1.0
        for gate in gates:
            draws = null_draws[gate]
            obs = draws[i]
            p = (1 + sum(1 for j, d in enumerate(draws) if j != i and d >= obs)) / r
            best = min(best, p)
        out.append(best)
    return tuple(sorted(out))


@dataclass(frozen=True)
class CalibrationArtifact:
    """Null draws for the Block-1 gates at ONE fully specified calibration condition.

    The reusable null quantities are computed ONCE here, at construction, and
    stored: the sorted marginals, the p_min null distribution and the critical
    p_min. P1 consumes them and never rebuilds them. They are functions of the
    calibration draws and the frozen alpha alone, so no validation observation
    can reach them (see `artifact_sha256`, which covers the stored values).
    """

    kind: str
    procedure_identity: str
    field_id: str
    n: int
    m: int
    alpha_1: float
    null_draws: Mapping[str, tuple[float, ...]]
    condition: CalibrationCondition
    schema: str = CALIBRATION_ARTIFACT_SCHEMA
    provenance: str = ""
    is_fixture: bool = False

    def __post_init__(self) -> None:
        if self.kind != "block1_min_p":
            raise Refusal(f"unsupported calibration kind {self.kind!r}")
        if self.schema != CALIBRATION_ARTIFACT_SCHEMA:
            raise Refusal(
                f"unsupported calibration artifact schema {self.schema!r}; this build "
                f"requires {CALIBRATION_ARTIFACT_SCHEMA!r}. A schema-1 artifact bound "
                "only the eigenvalue ratios and is refused, not reinterpreted."
            )
        missing = [g for g in BLOCK1_GATES if g not in self.null_draws]
        if missing:
            raise Refusal(f"calibration artifact missing null draws for {missing}")
        sizes = {g: len(self.null_draws[g]) for g in BLOCK1_GATES}
        if len(set(sizes.values())) != 1:
            raise Refusal(f"calibration draws must be paired across gates, got {sizes}")
        r = next(iter(sizes.values()))
        if r < 1:
            raise Refusal("calibration artifact contains no draws")
        for gate in BLOCK1_GATES:
            for value in self.null_draws[gate]:
                if not math.isfinite(value):
                    raise Refusal(
                        f"INVALID CALIBRATION ARTIFACT: gate {gate!r} carries the "
                        f"non-finite null draw {value!r}. Refusing rather than sorting it."
                    )
        if not isinstance(self.condition, CalibrationCondition):
            raise Refusal("calibration artifact requires a CalibrationCondition")
        if self.condition.field_id != self.field_id:
            raise Refusal("artifact field_id disagrees with its calibration condition")
        if self.condition.n != self.n or self.condition.m != self.m:
            raise Refusal("artifact (n, m) disagree with its calibration condition")
        if self.condition.alpha_1 != self.alpha_1:
            raise Refusal("artifact alpha_1 disagrees with its calibration condition")
        if self.condition.replicates != r:
            raise Refusal(
                f"calibration condition declares R = {self.condition.replicates} but the "
                f"artifact carries {r} draws"
            )
        if self.condition.procedure_identity != self.procedure_identity:
            raise Refusal("artifact procedure identity disagrees with its condition")

        # --- computed ONCE; P1 never rebuilds any of this ---------------------
        ordered = {g: tuple(sorted(self.null_draws[g])) for g in BLOCK1_GATES}
        object.__setattr__(self, "_sorted", ordered)
        p_min = []
        for i in range(r):
            best = 1.0
            for gate in BLOCK1_GATES:
                p = ge_counts(ordered[gate], self.null_draws[gate][i]) / r
                if p < best:
                    best = p
            p_min.append(best)
        object.__setattr__(self, "_p_min_null", tuple(sorted(p_min)))
        idx = max(0, int(math.floor(self.alpha_1 * r)) - 1)
        object.__setattr__(self, "_critical_p_min", self._p_min_null[idx])

    @property
    def replicates(self) -> int:
        return len(self.null_draws["G1"])

    @property
    def sorted_null(self) -> Mapping[str, tuple[float, ...]]:
        """Stored ascending marginals. Reused by every p-value lookup."""
        return self._sorted

    def p_value(self, gate: str, observed: float) -> float:
        """Barnard / Besag-Clifford Monte-Carlo p-value: (1 + #{null >= obs})/(R + 1).

        Size <= alpha for ANY R, but only CONDITIONAL on the draws coming from
        the true null law. They come from a surrogate, so the guarantee is
        conditional and the unconditional size still requires validation.

        Identical to the superseded linear scan; the stored sorted marginal
        turns it into one lookup.
        """
        if gate not in self.null_draws:
            raise Refusal(f"no null draws for gate {gate!r}")
        if not math.isfinite(observed):
            raise Refusal(f"non-finite observed statistic {observed!r} for gate {gate!r}")
        return (1 + ge_counts(self._sorted[gate], observed)) / (self.replicates + 1)

    def p_min_null(self) -> tuple[float, ...]:
        """Null distribution of p_min, by leave-one-out over the paired draws.

        Stored, not recomputed. Equal to `p_min_null_reference` exactly, by the
        finite identity 1 + #{j != i : d_j >= d_i} = #{j : d_j >= d_i}.
        """
        return self._p_min_null

    def critical_p_min(self) -> float:
        """The alpha_1 quantile of p_min's own null distribution. Stored."""
        return self._critical_p_min

    @property
    def artifact_sha256(self) -> str:
        """Covers the condition, the draws AND the stored derived quantities."""
        import json
        payload = {
            "schema": self.schema,
            "kind": self.kind,
            "condition_sha256": self.condition.sha256,
            "null_draws": {g: [canonical_float(v) for v in self.null_draws[g]]
                           for g in BLOCK1_GATES},
            "p_min_null": [canonical_float(v) for v in self._p_min_null],
            "critical_p_min": canonical_float(self._critical_p_min),
            "is_fixture": bool(self.is_fixture),
        }
        text = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


def require_calibration(
    artifact: CalibrationArtifact | None,
    *,
    procedure_identity: str,
    condition: CalibrationCondition,
) -> CalibrationArtifact:
    """Fail closed unless the artifact was calibrated at EXACTLY this condition."""
    if artifact is None:
        raise Refusal(
            f"CALIBRATION_MISSING for {condition.field_id}: the Block-1 min-p null has not "
            "been calibrated. Stochastic calibration is a separate authorised stage; this "
            "implementation refuses rather than assuming a threshold."
        )
    if artifact.schema != CALIBRATION_ARTIFACT_SCHEMA:
        raise Refusal(
            f"CALIBRATION_SCHEMA_MISMATCH for {condition.field_id}: artifact schema "
            f"{artifact.schema!r} != required {CALIBRATION_ARTIFACT_SCHEMA!r}"
        )
    if artifact.procedure_identity != procedure_identity:
        raise Refusal(
            f"CALIBRATION_IDENTITY_MISMATCH for {condition.field_id}: artifact was produced "
            f"under {artifact.procedure_identity[:16]}..., this run is {procedure_identity[:16]}..."
        )
    if artifact.field_id != condition.field_id:
        raise Refusal(
            f"CALIBRATION_FIELD_MISMATCH: artifact was calibrated for "
            f"{artifact.field_id!r} and was requested for {condition.field_id!r}"
        )
    if artifact.condition.sha256 != condition.sha256:
        differing = artifact.condition.first_difference(condition)
        raise Refusal(
            f"CALIBRATION_CONDITION_MISMATCH for {condition.field_id}: artifact condition "
            f"{artifact.condition.sha256[:16]}... != analysed condition "
            f"{condition.sha256[:16]}...; first differing component: {differing!r}"
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
