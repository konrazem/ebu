"""V-stage seed architecture: part of Layer M.

Disjoint seed namespaces, frozen before their corresponding validation results
are inspected.  Old ``e1a_v4`` seeds are deliberately NOT reused: their
scientific identity does not match this procedure.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rng import Stream, derive_seed

#: Root namespace tag.  Changing it changes every derived seed.
ROOT = "e1a_v5/validation/2026-10-06"

#: Disjoint seed families (V-stage brief section 53).
CALIBRATION = "calibration"
SIZE = "size_validation"
DIAGNOSTIC = "diagnostic_validation"
POWER = "complete_power"
CONTROL = "negative_control"

FAMILIES = (CALIBRATION, SIZE, DIAGNOSTIC, POWER, CONTROL)


@dataclass(frozen=True)
class SeedMap:
    """Deterministic (family, case, replicate) -> seed mapping."""

    root: str = ROOT

    def family_seed(self, family: str) -> int:
        if family not in FAMILIES:
            raise ValueError(f"unknown seed family {family!r}")
        return derive_seed(self.root, family)

    def case_seed(self, family: str, case_id: str) -> int:
        return derive_seed(self.family_seed(family), case_id)

    def replicate_seed(self, family: str, case_id: str, replicate: int) -> int:
        return derive_seed(self.case_seed(family, case_id), "rep", replicate)

    def stream(self, family: str, case_id: str, replicate: int) -> Stream:
        return Stream(
            self.replicate_seed(family, case_id, replicate),
            label=f"{family}/{case_id}/{replicate}",
        )

    def disjoint(self, a: tuple[str, str, int], b: tuple[str, str, int]) -> bool:
        return self.replicate_seed(*a) != self.replicate_seed(*b)
