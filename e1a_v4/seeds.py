"""Seed-family schema and separation. NO SEED VALUES ARE SET IN THIS STAGE.

The architecture must make it impossible to reuse calibration data as validation
evidence. Families are therefore disjoint by type, not by convention: a consumer
declares which family it may read, and `SeedMap.stream_for` refuses any other.

Seed VALUES are assigned only in the authorised stochastic-validation stage.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .numerics import Refusal


class SeedFamily(str, Enum):
    CALIBRATION = "calibration"
    VALIDATION = "validation"
    CONFIRMATORY = "confirmatory"
    BLINDED_SCALE_CONTROL = "blinded_scale_control"


#: Declared schema; enters the procedure identity. Values deliberately absent.
SEED_MAP_SCHEMA = {
    "families": [f.value for f in SeedFamily],
    "disjoint": True,
    "values_assigned_in_stage": "authorised stochastic validation",
    "reuse_policy": "a family may never be read by a consumer declared for another family",
}


@dataclass(frozen=True)
class SeedMap:
    """Seed values per family. Empty until the stochastic stage assigns them."""

    values: dict[SeedFamily, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        seen: dict[int, SeedFamily] = {}
        for fam, value in self.values.items():
            if not isinstance(fam, SeedFamily):
                raise Refusal(f"undeclared seed family {fam!r}")
            if value in seen:
                raise Refusal(
                    f"seed family {fam.value!r} reuses the seed of {seen[value].value!r}: "
                    "families must be disjoint"
                )
            seen[value] = fam

    def stream_for(self, consumer_family: SeedFamily, requested: SeedFamily) -> int:
        if consumer_family is not requested:
            raise Refusal(
                f"consumer declared for {consumer_family.value!r} may not read the "
                f"{requested.value!r} family"
            )
        if requested not in self.values:
            raise Refusal(
                f"no seed assigned for {requested.value!r}: seed values are set only in "
                "the authorised stochastic-validation stage"
            )
        return self.values[requested]
