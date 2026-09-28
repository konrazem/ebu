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
                               seed-map sha256, CANONICAL DRIVER file sha256)

    The expected value therefore CANNOT live in any of those inputs. Writing it
    into the plan would change the plan's sha256 and so change the very value it
    records -- an impossible fixed point. So:

        execution identity = hash of the frozen package inputs      (preimage)
        execution seal     = an EXTERNAL assertion of the expected identity

    The seal file `docs/e1a/e1a_v4_execution_seal.json` is deliberately EXCLUDED
    from the preimage. It is an assertion about the package, not part of it.

WHAT THE SEAL MAY NOT DO: NAME THE DRIVER
    The seal used to carry an authoritative `official_campaign_driver_module`, and
    the presence check was `os.path.exists` on whatever it named. An independent
    audit showed the consequence: with a correctly FROZEN seal naming
    `e1a_v4/validation/plan.py`, the complete execution gate PASSED while no
    campaign driver existed anywhere.

    The driver is now declared CANONICALLY in `e1a_v4/validation/driver.py`, which
    is itself hashed into the execution identity. A seal may RESTATE that
    declaration for reporting; any other value is refused. The seal asserts what
    the package's identity should be -- it does not get to decide which file the
    package is about to execute.

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

import re
from dataclasses import dataclass
from typing import Any

from .driver import (
    OFFICIAL_CAMPAIGN_DRIVER_ENTRY_POINT, OFFICIAL_CAMPAIGN_DRIVER_MODULE,
    OFFICIAL_CAMPAIGN_DRIVER_PATH, driver_state, require_canonical_driver,
    require_seal_driver_metadata,
)
from .refusals import (
    ExecutionAuthorisationMissing, ExecutionIdentityUnsealed, ExecutionNotAuthorised,
    ExecutionSealMalformed, ExecutionSealNotFrozen, ExecutionSealStateDisagreement,
)
from .strict_json import strict_load_file

#: The external seal. Deliberately NOT part of the execution-identity preimage.
SEAL_JSON = "docs/e1a/e1a_v4_execution_seal.json"
SEAL_SCHEMA = "e1a_v4_execution_seal/2"

STATE_PRE_DRIVER = "PRE_DRIVER"
STATE_FROZEN = "FROZEN"
SEAL_STATES = (STATE_PRE_DRIVER, STATE_FROZEN)

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ExecutionSeal:
    """An external assertion about the package. Built only by `load_seal`.

    It carries NO authoritative driver path: `restated_driver` exists purely for
    human reporting and is refused unless it repeats the canonical declaration.
    """

    state: str
    expected_execution_identity: str | None
    restated_driver: str | None
    note: str

    @property
    def is_frozen(self) -> bool:
        return self.state == STATE_FROZEN

    @property
    def driver_module(self) -> str:
        """Always the CANONICAL declaration. Never whatever the seal wrote."""
        return OFFICIAL_CAMPAIGN_DRIVER_PATH


def load_seal(root: str = ".") -> ExecutionSeal:
    """Read and validate the seal. Absent or malformed is FORGOTTEN -> REFUSAL."""
    try:
        raw = strict_load_file(f"{root}/{SEAL_JSON}" if root != "." else SEAL_JSON,
                               "the execution seal")
    except Exception as exc:                       # strict_json raises coded refusals
        if type(exc).__name__ == "PlanStructureInvalid":
            raise ExecutionSealMalformed(
                f"EXECUTION SEAL MISSING OR MALFORMED: {exc}. An absent seal is "
                "indistinguishable from a forgotten freeze and is never treated as "
                "'not yet frozen'; the not-yet-frozen state is declared explicitly."
            ) from None
        raise
    if raw.get("schema") != SEAL_SCHEMA:
        raise ExecutionSealMalformed(
            f"execution seal schema is {raw.get('schema')!r}, expected {SEAL_SCHEMA!r}")
    state = raw.get("state")
    if state not in SEAL_STATES:
        raise ExecutionSealMalformed(
            f"execution seal state is {state!r}; the declared lifecycle is {SEAL_STATES}")
    if "expected_execution_identity" not in raw:
        raise ExecutionSealMalformed(
            "execution seal omits the expected_execution_identity KEY. A missing key "
            "is forgotten, not 'not yet frozen'; declare it explicitly as null.")
    expected = raw["expected_execution_identity"]
    if state == STATE_PRE_DRIVER and expected is not None:
        raise ExecutionSealMalformed(
            "a PRE_DRIVER seal must carry expected_execution_identity = null: the "
            "official campaign driver does not exist, so no final identity can be "
            "meaningful yet")
    if state == STATE_FROZEN and not (isinstance(expected, str) and _HEX64.match(expected)):
        raise ExecutionSealMalformed(
            "a FROZEN seal must carry a 64-character lowercase hex "
            f"expected_execution_identity; found {expected!r}")

    # A seal MAY restate the canonical driver for reporting. It may not redefine it.
    restated = raw.get("restates_canonical_campaign_driver")
    require_seal_driver_metadata(restated)
    if "official_campaign_driver_module" in raw:
        raise ExecutionSealMalformed(
            "the execution seal carries an authoritative "
            "'official_campaign_driver_module' key. The driver is declared "
            f"canonically in e1a_v4/validation/driver.py as "
            f"{OFFICIAL_CAMPAIGN_DRIVER_PATH!r} and is bound into the execution "
            "identity; a seal may only RESTATE it, via "
            "'restates_canonical_campaign_driver'.")
    return ExecutionSeal(state, expected, restated, raw.get("note", ""))


def driver_present(root: str, module_path: str | None = None) -> bool:
    """Presence of THE canonical driver.

    `module_path` is accepted and IGNORED on purpose: callers that used to pass a
    seal-supplied path must not be able to steer this answer.
    """
    return driver_state(root) == "PRESENT"


def require_seal_plan_agreement(plan: dict[str, Any], seal: ExecutionSeal) -> None:
    """The plan's declared seal state and the external seal must agree."""
    declared = plan.get("execution_seal", {}).get("state")
    if declared != seal.state:
        raise ExecutionSealStateDisagreement(
            f"EXECUTION SEAL DISAGREEMENT: the validation plan declares state "
            f"{declared!r} but {SEAL_JSON} declares {seal.state!r}")


def require_execution_gate(root: str, plan: dict[str, Any],
                           recomputed_identity: str) -> None:
    """The complete pre-RNG execution gate. Every failure refuses BEFORE any draw.

    Ordered so that the MOST fundamental missing precondition is reported first:
    a driver that does not exist cannot have been audited, and an unaudited
    package cannot have been sealed, and an unsealed package cannot be authorised.
    """
    seal = load_seal(root)
    require_seal_plan_agreement(plan, seal)

    # binds to the CANONICAL declaration, never to anything the seal named
    require_canonical_driver(root)

    if not seal.is_frozen:
        raise ExecutionSealNotFrozen(
            f"EXECUTION REFUSED: the execution seal is {seal.state}, not {STATE_FROZEN}. "
            "The final expected execution identity is frozen only after the official "
            "campaign driver is implemented and independently audited.")
    if recomputed_identity != seal.expected_execution_identity:
        raise ExecutionIdentityUnsealed(
            f"EXECUTION REFUSED: recomputed execution identity {recomputed_identity} "
            f"does not equal the independently frozen seal "
            f"{seal.expected_execution_identity}")
    if not plan.get("execution_authorised", False):
        raise ExecutionAuthorisationMissing(
            "EXECUTION REFUSED: the frozen validation plan has execution_authorised = "
            "false. A FROZEN seal is not an authorisation; authorisation is a separate "
            "reviewed stage.")
