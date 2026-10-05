"""Global verdict engine: Layer L.

Implements the T-stage section 21 conjunction and classification table.  A
failed equivalence test is never automatically relabelled a discrepancy, and
invalid or refused cells never disappear from the planned experiment or its
complete-pass denominator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

from .refusals import Refusal

SUPPORTED = "SUPPORTED_WITHIN_DECLARED_TOLERANCES"
DISCREPANCY = "DISCREPANCY_ESTABLISHED"
INCONCLUSIVE = "INCONCLUSIVE_INSUFFICIENT_PRECISION"
INVALID = "INVALID_MEASUREMENT_OR_MODEL"
NOT_EVALUABLE = "COMPUTATION_NOT_EVALUABLE"

#: Density supported but reversibility contradicted (T-stage 12.3).
DENSITY_ONLY_CURRENT = (
    "DENSITY BRIDGE SUPPORTED WITHIN TOLERANCE; "
    "EQUILIBRIUM ANCHOR NOT ESTABLISHED - CURRENT DETECTED"
)
DENSITY_ONLY_INCONCLUSIVE = (
    "DENSITY BRIDGE SUPPORTED WITHIN TOLERANCE; REVERSIBILITY INCONCLUSIVE"
)


@dataclass(frozen=True)
class ComponentTally:
    """Counts of each required positive component."""

    absolute_pass: int = 0
    absolute_total: int = 8
    contrast_pass: int = 0
    contrast_total: int = 6
    shape_pass: int = 0
    centre_pass: int = 0
    stationarity_pass: int = 0
    current_pass: int = 0
    current_inconclusive: int = 0
    record_total: int = 8
    diagnostic_rejected: bool = False
    realization_valid: int = 0
    branch_a_valid: int = 0
    observation_valid: int = 0


@dataclass(frozen=True)
class Verdict:
    classification: str
    qualifier: str = ""
    tally: ComponentTally | None = None
    refusals: tuple[Refusal, ...] = ()
    detail: Mapping[str, object] = field(default_factory=dict)

    @property
    def complete_success(self) -> bool:
        return self.classification == SUPPORTED


def decide(
    tally: ComponentTally,
    refusals: Sequence[Refusal] = (),
    not_evaluable: bool = False,
) -> Verdict:
    """Apply the exact T-stage conjunction.

    Full support requires valid A, valid observation/support, valid realized
    fields, 8 absolute passes, 6 cross-field passes, 8 shape, 8 centre, 8
    stationarity, 8 current, and no rejected model diagnostic.  P4 is secondary
    and cannot rescue or fail the primary bridge.
    """
    refusals = tuple(refusals)
    if not_evaluable:
        return Verdict(NOT_EVALUABLE, "optimiser or numerical failure", tally, refusals)

    families = {r.family for r in refusals}
    if "NUMERICAL" in families:
        return Verdict(NOT_EVALUABLE, "numerical representation failure", tally, refusals)
    if "INVALID" in families:
        return Verdict(INVALID, "demonstrated model or domain breach", tally, refusals)
    if "INCOMPLETE" in families:
        return Verdict(INVALID, "required input or dependency absent", tally, refusals)

    n = tally.record_total
    structural_ok = (
        tally.branch_a_valid == n
        and tally.observation_valid == n
        and tally.realization_valid == n
    )
    if not structural_ok:
        if "INCONCLUSIVE" in families:
            return Verdict(INCONCLUSIVE, "unresolved qualification certificate", tally, refusals)
        return Verdict(INVALID, "a required record qualification did not pass", tally, refusals)

    density_ok = (
        tally.absolute_pass == tally.absolute_total
        and tally.contrast_pass == tally.contrast_total
        and tally.shape_pass == n
        and tally.centre_pass == n
    )
    stationary_ok = tally.stationarity_pass == n
    current_ok = tally.current_pass == n

    if tally.diagnostic_rejected:
        return Verdict(
            INVALID,
            "a declared model diagnostic was rejected; it vetoes a model-qualified bridge",
            tally,
            refusals,
        )

    if density_ok and stationary_ok and current_ok:
        return Verdict(SUPPORTED, "", tally, refusals)

    if density_ok and stationary_ok and not current_ok:
        qualifier = (
            DENSITY_ONLY_INCONCLUSIVE
            if tally.current_inconclusive > 0
            else DENSITY_ONLY_CURRENT
        )
        return Verdict(INCONCLUSIVE, qualifier, tally, refusals)

    if not stationary_ok:
        return Verdict(INVALID, "stationarity gate failed", tally, refusals)

    return Verdict(
        INCONCLUSIVE,
        "an interval overlapped its margin or required precision was not reached",
        tally,
        refusals,
    )
