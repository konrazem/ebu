"""Mechanical, outcome-blind seed derivation. NOTHING IS DRAWN HERE.

Choosing a seed is not running an experiment, so this stage may FREEZE seed
values. They are never hand-picked: every seed is a domain-separated SHA-256 of
declared strings, so the derivation can be re-executed by a reviewer and must
reproduce the committed seed map byte for byte.

    master        = H( DOMAIN | "master"    | contract_sha256 | campaign )
    family seed   = H( DOMAIN | "family"    | master_hex      | family    )
    replicate     = H( DOMAIN | "replicate" | family_hex      | case | rep )
    subcondition  = H( canon("subcondition", replicate_hex, subcondition_id) )
    scope         = H( canon("scope",         subcondition_hex, scope)        )

The last two levels are EXTENSIONS. They change none of the three above: every
master, family and replicate value is bit-identical to the committed seed map.

`canon` is a deterministic domain-separated SERIALISATION, not string
concatenation: the parts are JSON-encoded with sorted separators and ASCII
escaping, so a separator inside an identifier cannot forge a different tuple.

WHY THE SUBCONDITION LEVEL IS REQUIRED. A case declares several distinct
synthetic scenarios - four sigma_psi scenarios for C1/C2/C3, twelve uncertainty
cells for C5, three rho conditions for C6, four false-bridge alternatives for
C7. Without a subcondition level they all resolve to one stream, so different
declared scenarios would silently share random numbers. They are separate
declared scenarios and are independently random BY DEFAULT.

WHY THE SCOPE LEVEL IS REQUIRED, and why it is NOT simply "per field". Randomness
scope is a property of the quantity, not of the loop it happens to sit in:

    experiment scope   the Branch-A COMMON-MODE calibration error. ONE draw per
                       synthetic experiment, SHARED across all four fields. That
                       sharing is what makes it cancel in the P2 ratio and not in
                       P3, so redrawing it per field would destroy the dependence
                       structure P2 exists to test.
    field scope        per-mode stiffness, orientation and thermometry error;
                       the calibration surrogate draws; the Branch-B trajectory
                       innovations. Independent per field.

ACCIDENTAL cross-subcondition sharing is a defect. INTENTIONAL within-experiment
sharing is part of the frozen model. The two are distinguished here explicitly.

H(x) = first 8 bytes of sha256(x), big-endian, as an unsigned 64-bit integer.

FAMILY SET. The analysis layer (`e1a_v4.seeds`) declares four families and is
left UNTOUCHED, so the analysis procedure identity does not move. Branch-A
measurement error is exogenous randomness that the analysis never sees, so it
gets its OWN family here rather than silently reusing the Branch-B trajectory
stream.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping

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


#: The scope of a quantity drawn once per experiment and shared across fields.
EXPERIMENT_SCOPE = "experiment"


def _canon(*parts: str) -> str:
    """Deterministic, escaping-safe serialisation. NOT string concatenation."""
    return SEED_DOMAIN + json.dumps(list(parts), separators=(",", ":"), ensure_ascii=True)


def subcondition_seed(rep_seed: int, subcondition_id: str) -> int:
    """Per-declared-scenario stream inside one replicate. DERIVATION, NOT A DRAW.

    Different declared subconditions are independently random by default.
    """
    if not subcondition_id:
        raise Refusal("subcondition id must be non-empty")
    return _h64(_canon("subcondition", f"{rep_seed:016x}", subcondition_id))


def scope_seed(sub_seed: int, scope: str) -> int:
    """Per-scope stream inside one subcondition replicate. DERIVATION, NOT A DRAW.

    `scope` is EXPERIMENT_SCOPE for a quantity shared across the fields of one
    synthetic experiment, or a field id for a per-field quantity.
    """
    if not scope:
        raise Refusal("stochastic scope must be non-empty")
    return _h64(_canon("scope", f"{sub_seed:016x}", scope))


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


# --------------------------------------------------------------------------
# CASE-SCOPED ENFORCEMENT (repair B3)
#
# `FrozenSeedMap.stream` compares the two family arguments a caller supplies and
# nothing else. It is a symmetry check, not a permission check: passing the same
# family twice satisfies it, so ANY family was reachable for ANY case and the
# case plan was honoured only by convention. That is a specification requirement,
# not a mechanically enforced rule, and it must not be described as one.
#
# `CaseSeedAccess` is the enforced boundary. It is constructed from the frozen
# plan, so the authorisation comes from the committed case declaration rather
# than from the caller. The OFFICIAL runner obtains streams only through it.
# `family_seed` and `replicate_seed` remain reusable primitives: a mathematical
# derivation is not an authorisation, and the boundary is where authorisation is
# decided.
# --------------------------------------------------------------------------

#: Plan key carrying each case's authorised families. Machine-readable, not prose.
ALLOWED_FAMILIES_KEY = "allowed_seed_families"


@dataclass(frozen=True)
class CaseSeedAccess:
    """Case-scoped seed authorisation. The only route an official run may use."""

    case_id: str
    allowed: tuple[str, ...]
    seed_map: FrozenSeedMap
    subconditions: tuple[str, ...] = ()

    @classmethod
    def from_plan(cls, case_id: str, plan: Mapping[str, Any],
                  seed_map: FrozenSeedMap) -> "CaseSeedAccess":
        cases = {c["case_id"]: c for c in plan.get("cases", [])}
        if case_id not in cases:
            raise Refusal(
                f"unknown case {case_id!r}: the frozen plan declares "
                f"{sorted(cases)}. Seed access is granted per declared case only."
            )
        case = cases[case_id]
        if ALLOWED_FAMILIES_KEY not in case:
            raise Refusal(
                f"case {case_id!r} does not declare {ALLOWED_FAMILIES_KEY!r}; refusing "
                "rather than inferring permissions from prose"
            )
        declared = tuple(case[ALLOWED_FAMILIES_KEY])
        if not declared:
            raise Refusal(f"case {case_id!r} declares an empty seed-family list")
        known = {f.value for f in ValidationSeedFamily}
        unknown = [f for f in declared if f not in known]
        if unknown:
            raise Refusal(f"case {case_id!r} declares undeclared seed families {unknown}")
        if len(set(declared)) != len(declared):
            raise Refusal(f"case {case_id!r} repeats a seed family")
        subs = tuple(s["subcondition_id"] for s in case.get("subconditions", []))
        if not subs:
            raise Refusal(
                f"case {case_id!r} declares no subconditions; every stochastic case must "
                "carry an explicit machine-readable subcondition list"
            )
        if len(set(subs)) != len(subs):
            raise Refusal(f"case {case_id!r} repeats a subcondition id")
        return cls(case_id, declared, seed_map, subs)

    def _authorise(self, family: ValidationSeedFamily) -> ValidationSeedFamily:
        if not isinstance(family, ValidationSeedFamily):
            raise Refusal(f"undeclared validation seed family {family!r}")
        if family.value not in self.allowed:
            raise Refusal(
                f"SEED FAMILY REFUSED: case {self.case_id!r} is authorised for "
                f"{list(self.allowed)} and requested {family.value!r}. The frozen case "
                "plan decides this, not the caller."
            )
        return family

    def family(self, family: ValidationSeedFamily) -> int:
        """The family seed, only if this case declares that family."""
        fam = self._authorise(family)
        return self.seed_map.stream(fam, fam)

    def replicate(self, family: ValidationSeedFamily, replicate: int) -> int:
        """A replicate seed inside an authorised family. DERIVATION, NOT A DRAW.

        Deriving a seed creates no generator and draws no number. The four
        stages stay separately reported: seed derivation, RNG construction,
        random draw, trajectory generation.
        """
        return replicate_seed(self.family(family), self.case_id, replicate)

    def subcondition(self, family: ValidationSeedFamily, subcondition_id: str,
                     replicate: int) -> int:
        """A declared scenario's stream. DERIVATION, NOT A DRAW."""
        if subcondition_id not in self.subconditions:
            raise Refusal(
                f"SUBCONDITION REFUSED: case {self.case_id!r} declares "
                f"{list(self.subconditions)} and was asked for {subcondition_id!r}. "
                "Subcondition identities come from the frozen plan, not the caller."
            )
        return subcondition_seed(self.replicate(family, replicate), subcondition_id)

    def stream(self, family: ValidationSeedFamily, subcondition_id: str,
               replicate: int, scope: str) -> int:
        """The scientific stream identity. DERIVATION, NOT A DRAW.

        Distinct for every (family, case, subcondition, replicate, scope), so two
        declared scenarios never share randomness and scheduling order cannot
        change a stream. `scope` is EXPERIMENT_SCOPE or a field id.
        """
        return scope_seed(self.subcondition(family, subcondition_id, replicate), scope)
