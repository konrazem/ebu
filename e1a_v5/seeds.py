"""V-stage seed architecture: part of Layer M.

Disjoint seed namespaces, frozen before their corresponding validation results
are inspected.  Old ``e1a_v4`` seeds are deliberately NOT reused: their
scientific identity does not match this procedure.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rng import Stream, derive_seed

#: Root namespace tag.  Changing it changes every derived seed.
#:
#: V3 uses a NEW root. Procedure semantics changed between V2 and V3 -- the
#: success predicate, the axial qualification, the diagnostic family and the
#: profile standard error all behave differently -- so V2 stochastic streams,
#: whose outcomes have already been inspected, must not be reused for V3
#: confirmatory validation.
ROOT = "e1a_v5/validation/v3/2026-10-06"

#: The superseded V2 root, retained so the disjointness can be checked.
ROOT_V2 = "e1a_v5/validation/2026-10-06"

#: Disjoint seed families (V-stage brief section 53), versioned for V3.
CALIBRATION = "calibration-v3"
SIZE = "size_validation-v3"
DIAGNOSTIC = "diagnostic_validation-v3"
POWER = "complete_power-v3"
CONTROL = "negative_control-v3"

FAMILIES = (CALIBRATION, SIZE, DIAGNOSTIC, POWER, CONTROL)

#: The V2 family names, for the disjointness regression only.
FAMILIES_V2 = (
    "calibration", "size_validation", "diagnostic_validation",
    "complete_power", "negative_control",
)


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

    def disjoint_from_v2(self, family_v3: str, family_v2: str, case_id: str,
                         replicates: int = 64) -> bool:
        """True when no V3 replicate seed collides with the V2 stream.

        Both the root and the family name changed, so this is expected to hold
        by construction; it is checked rather than asserted.
        """
        v3 = {self.replicate_seed(family_v3, case_id, r) for r in range(replicates)}
        v2_map = SeedMap(root=ROOT_V2)
        v2 = set()
        for r in range(replicates):
            v2.add(derive_seed(
                derive_seed(derive_seed(ROOT_V2, family_v2), case_id), "rep", r))
        return not (v3 & v2)
