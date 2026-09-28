"""Mechanical, outcome-blind seed derivation. NOTHING IS DRAWN HERE.

Choosing a seed is not running an experiment, so this stage may FREEZE seed
values. They are never hand-picked: every seed is a domain-separated SHA-256 of
declared strings, so the derivation can be re-executed by a reviewer and must
reproduce the committed seed map byte for byte.

    master        = H( DOMAIN | "master"    | contract_sha256 | campaign )
    family seed   = H( DOMAIN | "family"    | master_hex      | family    )
    replicate     = H( DOMAIN | "replicate" | family_hex      | case | rep )

H(x) = first 8 bytes of sha256(x), big-endian, as an unsigned 64-bit integer.

FAMILY SET. The analysis layer (`e1a_v4.seeds`) declares four families and is
left UNTOUCHED, so the analysis procedure identity does not move. Branch-A
measurement error is exogenous randomness that the analysis never sees, so it
gets its OWN family here rather than silently reusing the Branch-B trajectory
stream.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum

from .. import seeds as analysis_seeds
from ..numerics import Refusal
from . import CAMPAIGN_LABEL, SEED_DOMAIN


class ValidationSeedFamily(str, Enum):
    CALIBRATION = "calibration"
    VALIDATION = "validation"
    CONFIRMATORY = "confirmatory"
    BLINDED_SCALE_CONTROL = "blinded_scale_control"
    BRANCH_A_MEASUREMENT = "branch_a_measurement"


#: The analysis layer's four families are a strict subset. Verified, not assumed.
ANALYSIS_FAMILIES = tuple(f.value for f in analysis_seeds.SeedFamily)


def _h64(text: str) -> int:
    return int.from_bytes(hashlib.sha256(text.encode("utf-8")).digest()[:8], "big")


def master_seed(contract_sha256: str, campaign: str = CAMPAIGN_LABEL) -> int:
    if len(contract_sha256) != 64:
        raise Refusal("master seed needs the full contract sha256")
    return _h64(f"{SEED_DOMAIN}|master|{contract_sha256}|{campaign}")


def family_seed(master: int, family: ValidationSeedFamily) -> int:
    if not isinstance(family, ValidationSeedFamily):
        raise Refusal(f"undeclared validation seed family {family!r}")
    return _h64(f"{SEED_DOMAIN}|family|{master:016x}|{family.value}")


def replicate_seed(fam_seed: int, case_id: str, replicate: int) -> int:
    if replicate < 0:
        raise Refusal("replicate index must be nonnegative")
    if "|" in case_id or not case_id:
        raise Refusal("invalid case id")
    return _h64(f"{SEED_DOMAIN}|replicate|{fam_seed:016x}|case={case_id}|rep={replicate}")


@dataclass(frozen=True)
class FrozenSeedMap:
    """The committed seed map. Derived, never chosen."""

    contract_sha256: str
    campaign: str
    master: int
    families: dict[str, int]

    @classmethod
    def derive(cls, contract_sha256: str, campaign: str = CAMPAIGN_LABEL) -> "FrozenSeedMap":
        m = master_seed(contract_sha256, campaign)
        fams = {f.value: family_seed(m, f) for f in ValidationSeedFamily}
        if len(set(fams.values())) != len(fams):
            raise Refusal("derived family seeds collided; derivation is broken")
        return cls(contract_sha256, campaign, m, fams)

    def as_json(self) -> dict:
        return {
            "schema": "e1a_v4_seed_map/1",
            "domain": SEED_DOMAIN,
            "campaign": self.campaign,
            "contract_sha256": self.contract_sha256,
            "derivation": {
                "hash": "first 8 bytes of sha256(text), big-endian unsigned",
                "master": "DOMAIN|master|contract_sha256|campaign",
                "family": "DOMAIN|family|master_hex16|family_name",
                "replicate": "DOMAIN|replicate|family_hex16|case=<id>|rep=<index>",
                "hand_picked_values": False,
            },
            "master_seed": self.master,
            "families": dict(sorted(self.families.items())),
            "analysis_layer_families": list(ANALYSIS_FAMILIES),
            "drawn_in_this_stage": False,
        }

    def stream(self, consumer: ValidationSeedFamily, requested: ValidationSeedFamily) -> int:
        """A consumer may read only its own family. No shared mutable RNG state."""
        if consumer is not requested:
            raise Refusal(
                f"consumer declared for {consumer.value!r} may not read {requested.value!r}"
            )
        return self.families[requested.value]
