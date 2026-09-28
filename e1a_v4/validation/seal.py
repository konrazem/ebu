"""Execution-seal lifecycle. The gate the AUTHORISED stochastic stage must pass.

THE PROBLEM THIS SOLVES
    A package that recomputes its own execution identity and then compares it to
    nothing has not been sealed: any change to the package changes the identity
    and the check still passes. A seal is only a seal if the expected value was
    frozen INDEPENDENTLY, before the run, by a reviewer.

SELF-REFERENCE, and how it is avoided
    The execution identity is the hash of the frozen package inputs:

        execution identity = H(validation module hashes, analysis identity,
                               plan JSON sha256, plan Markdown sha256,
                               seed-map sha256)

    The expected value therefore CANNOT live in any of those inputs. Writing it
    into the plan would change the plan's sha256 and so change the very value it
    records -- an impossible fixed point. So:

        execution identity = hash of the frozen package inputs      (preimage)
        execution seal     = an EXTERNAL assertion of the expected identity

    The seal file `docs/e1a/e1a_v4_execution_seal.json` is deliberately EXCLUDED
    from the preimage. It is an assertion about the package, not part of it.

THE STATE MACHINE
    PRE_DRIVER   the official campaign driver does not exist yet, so no final
                 identity can be meaningful. `expected_execution_identity` MUST
                 be null. Preflight may pass; EXECUTION REFUSES.
    FROZEN       the driver exists and has been independently audited, and a
                 reviewer has frozen the expected identity. `expected_execution_
                 identity` MUST be a 64-hex digest. Execution is eligible only if
                 it matches the recomputation AND `execution_authorised` is true.

    `execution_authorised = true` is set by a SEPARATE final authorisation task.
    A FROZEN seal is not an authorisation, and an authorisation without a FROZEN
    seal is refused.

NOT-YET-FROZEN versus FORGOTTEN
    These must never look alike. An ABSENT seal file, an ABSENT state, or an
    ABSENT expected-identity KEY is treated as FORGOTTEN and refuses. Only the
    explicit pair (state = PRE_DRIVER, expected_execution_identity = null) means
    "deliberately not yet frozen".

CLASSIFICATION
    every check here ... EXACT (string equality and declared-state comparison)

NO RNG. Nothing in this module draws or advances any model state.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from typing import Any

from ..numerics import Refusal

#: The external seal. Deliberately NOT part of the execution-identity preimage.
SEAL_JSON = "docs/e1a/e1a_v4_execution_seal.json"
SEAL_SCHEMA = "e1a_v4_execution_seal/1"

STATE_PRE_DRIVER = "PRE_DRIVER"
STATE_FROZEN = "FROZEN"
SEAL_STATES = (STATE_PRE_DRIVER, STATE_FROZEN)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class ExecutionNotAuthorised(Refusal):
    """Umbrella: this run is NOT cleared to execute.

    The subclasses name WHICH precondition is missing, so a refusal can never be
    read as "just flip the authorisation flag". Every one of them is raised before
    any RNG object can exist.
    """


class CampaignDriverAbsent(ExecutionNotAuthorised):
    """The official campaign driver does not exist, so nothing can be executed."""


class ExecutionSealNotFrozen(ExecutionNotAuthorised):
    """No independently frozen expected execution identity exists yet."""


class ExecutionIdentityUnsealed(ExecutionNotAuthorised):
    """The recomputed identity does not equal the independently frozen seal."""


class ExecutionAuthorisationMissing(ExecutionNotAuthorised):
    """Driver, seal and identity are in order, but authorisation was not granted."""


@dataclass(frozen=True)
class ExecutionSeal:
    """An external assertion about the package. Built only by `load_seal`."""

    state: str
    expected_execution_identity: str | None
    driver_module: str
    note: str

    @property
    def is_frozen(self) -> bool:
        return self.state == STATE_FROZEN


def load_seal(root: str = ".") -> ExecutionSeal:
    """Read and validate the seal. Absent or malformed is FORGOTTEN -> REFUSAL."""
    path = os.path.join(root, SEAL_JSON)
    if not os.path.exists(path):
        raise Refusal(
            f"EXECUTION SEAL MISSING: {SEAL_JSON} is absent. An absent seal is "
            "indistinguishable from a forgotten freeze and is never treated as "
            "'not yet frozen'; the not-yet-frozen state is declared explicitly."
        )
    with open(path, encoding="utf-8") as handle:
        try:
            raw = json.load(handle)
        except json.JSONDecodeError as exc:
            raise Refusal(f"execution seal is not valid JSON: {exc}") from exc
    if raw.get("schema") != SEAL_SCHEMA:
        raise Refusal(f"execution seal schema is {raw.get('schema')!r}, "
                      f"expected {SEAL_SCHEMA!r}")
    state = raw.get("state")
    if state not in SEAL_STATES:
        raise Refusal(
            f"execution seal state is {state!r}; the declared lifecycle is {SEAL_STATES}"
        )
    if "expected_execution_identity" not in raw:
        raise Refusal(
            "execution seal omits the expected_execution_identity KEY. A missing key "
            "is forgotten, not 'not yet frozen'; declare it explicitly as null."
        )
    expected = raw["expected_execution_identity"]
    if state == STATE_PRE_DRIVER and expected is not None:
        raise Refusal(
            "a PRE_DRIVER seal must carry expected_execution_identity = null: the "
            "official campaign driver does not exist, so no final identity can be "
            "meaningful yet"
        )
    if state == STATE_FROZEN and not (isinstance(expected, str) and _HEX64.match(expected)):
        raise Refusal(
            "a FROZEN seal must carry a 64-character lowercase hex "
            f"expected_execution_identity; found {expected!r}"
        )
    driver = raw.get("official_campaign_driver_module")
    if not isinstance(driver, str) or not driver:
        raise Refusal("execution seal must name official_campaign_driver_module")
    return ExecutionSeal(state, expected, driver, raw.get("note", ""))


def driver_present(root: str, module_path: str) -> bool:
    """Is the official campaign driver actually on disk? Presence only."""
    return os.path.exists(os.path.join(root, module_path))


def require_seal_plan_agreement(plan: dict[str, Any], seal: ExecutionSeal) -> None:
    """The plan's declared seal state and the external seal must agree."""
    declared = plan.get("execution_seal", {}).get("state")
    if declared != seal.state:
        raise Refusal(
            f"EXECUTION SEAL DISAGREEMENT: the validation plan declares state "
            f"{declared!r} but {SEAL_JSON} declares {seal.state!r}"
        )


def require_execution_gate(root: str, plan: dict[str, Any], recomputed_identity: str) -> None:
    """The complete pre-RNG execution gate. Every failure refuses BEFORE any draw.

    Ordered so that the MOST fundamental missing precondition is reported first:
    a driver that does not exist cannot have been audited, and an unaudited
    package cannot have been sealed, and an unsealed package cannot be authorised.
    """
    seal = load_seal(root)
    require_seal_plan_agreement(plan, seal)

    if not driver_present(root, seal.driver_module):
        raise CampaignDriverAbsent(
            f"EXECUTION REFUSED: the official campaign driver {seal.driver_module} is "
            "ABSENT. A passing static preflight is not an execution clearance."
        )
    if not seal.is_frozen:
        raise ExecutionSealNotFrozen(
            f"EXECUTION REFUSED: the execution seal is {seal.state}, not {STATE_FROZEN}. "
            "The final expected execution identity is frozen only after the official "
            "campaign driver is implemented and independently audited."
        )
    if recomputed_identity != seal.expected_execution_identity:
        raise ExecutionIdentityUnsealed(
            f"EXECUTION REFUSED: recomputed execution identity {recomputed_identity} "
            f"does not equal the independently frozen seal "
            f"{seal.expected_execution_identity}"
        )
    if not plan.get("execution_authorised", False):
        raise ExecutionAuthorisationMissing(
            "EXECUTION REFUSED: the frozen validation plan has execution_authorised = "
            "false. A FROZEN seal is not an authorisation; authorisation is a separate "
            "reviewed stage."
        )
