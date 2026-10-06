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
#: V6 uses a NEW root.  The plan's negative-control counts and release events
#: changed, the auxiliary primitive model and its joint region changed, the
#: observation qualification moved into detector coordinates and onto an
#: independent envelope, the temporal model is now qualified from a measured
#: response, and the gate trust model became a verifiable receipt.  V5
#: streams, whose outcomes the V5 audit has inspected, must not be reused.
ROOT = "e1a_v5/validation/v6/2026-10-06"

#: Superseded roots, retained so disjointness can be checked rather than
#: asserted.
ROOT_V5 = "e1a_v5/validation/v5/2026-10-06"
ROOT_V4 = "e1a_v5/validation/v4/2026-10-06"
ROOT_V3 = "e1a_v5/validation/v3/2026-10-06"
ROOT_V2 = "e1a_v5/validation/2026-10-06"

#: Disjoint CONFIRMATORY seed families.  Frozen here and NOT executed.
CALIBRATION = "critical-calibration-v6"
SIZE = "size-validation-v6"
DIAGNOSTIC = "diagnostic-validation-v6"
POWER = "complete-power-v6"
CONTROL = "negative-controls-v6"

CONFIRMATORY_FAMILIES = (CALIBRATION, SIZE, DIAGNOSTIC, POWER, CONTROL)

#: The engineering namespace.  Everything drawn during implementation and
#: smoke testing comes from here.  It is explicitly NOT part of any
#: confirmatory validation and no result drawn from it may be reported as a
#: validation outcome; keeping it separate is what stops a repair session from
#: consuming -- and so inspecting -- a future confirmatory stream.
ENGINEERING = "engineering-v6"

FAMILIES = CONFIRMATORY_FAMILIES + (ENGINEERING,)

#: Earlier family names, for the disjointness regressions only.
FAMILIES_V5 = (
    "critical-calibration-v5", "size-validation-v5", "diagnostic-validation-v5",
    "complete-power-v5", "negative-controls-v5",
)
ENGINEERING_V5 = "engineering-v5"
FAMILIES_V4 = (
    "critical-calibration-v4", "size-validation-v4", "diagnostic-validation-v4",
    "complete-power-v4", "negative-controls-v4",
)
ENGINEERING_V4 = "engineering-v4"
FAMILIES_V3 = (
    "calibration-v3", "size_validation-v3", "diagnostic_validation-v3",
    "complete_power-v3", "negative_control-v3",
)
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

    def disjoint_from(
        self, family: str, root: str, family_old: str, case_id: str,
        replicates: int = 64,
    ) -> bool:
        """True when no V4 replicate seed collides with an earlier stream.

        Both the root and the family names changed, so this holds by
        construction; it is checked rather than asserted.
        """
        new = {self.replicate_seed(family, case_id, r) for r in range(replicates)}
        old = {
            derive_seed(derive_seed(derive_seed(root, family_old), case_id), "rep", r)
            for r in range(replicates)
        }
        return not (new & old)

    def engineering_disjoint_from_confirmatory(
        self, case_id: str, replicates: int = 256
    ) -> bool:
        """The engineering namespace shares no seed with any confirmatory one."""
        eng = {self.replicate_seed(ENGINEERING, case_id, r) for r in range(replicates)}
        for fam in CONFIRMATORY_FAMILIES:
            conf = {self.replicate_seed(fam, case_id, r) for r in range(replicates)}
            if eng & conf:
                return False
        return True

    def disjoint_from_all_engineering(
        self, family: str, case_id: str, replicates: int = 256
    ) -> bool:
        """No confirmatory seed collides with ANY engineering stream, past or present.

        The V5 brief requires disjointness from every engineering stream, not
        only the current one: an earlier version's engineering draws have been
        inspected just as thoroughly as its confirmatory ones.
        """
        new = {self.replicate_seed(family, case_id, r) for r in range(replicates)}
        for root, eng in ((ROOT, ENGINEERING), (ROOT_V5, ENGINEERING_V5),
                          (ROOT_V4, ENGINEERING_V4)):
            old = {
                derive_seed(derive_seed(derive_seed(root, eng), case_id), "rep", r)
                for r in range(replicates)
            }
            if new & old:
                return False
        return True
