"""Fail-closed slot schema for a long-run study protocol.

This module is INFRASTRUCTURE.  It defines nothing scientific: it supplies no
world, no parameter, no hypothesis, no metric, no falsifier and no horizon, and
it contains no default for any of them.  Its only job is to REFUSE a protocol
that is incomplete, unfrozen, or presented for execution while a standing
blocker is open.

It makes the unfilled slots of ``V3.0_LONG_RUN_STUDY_FRAMEWORK.md`` §7
enforceable rather than prose.  A slot left unfilled is a refusal condition,
never a default - so this module cannot be used to invent a study.

Execution safety.  Importing or calling anything here must not run a model
step, a runner, a simulation, a trajectory or a tick, and must not open a file
for writing or touch the network.  ``require_executable`` NEVER returns
successfully while any escalation in ``authority_coordinate.OPEN_ESCALATIONS``
stands; today that is all five, so every protocol is currently unexecutable by
construction.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

import authority_coordinate as ac

__all__ = [
    "ProtocolError", "IncompleteProtocol", "UnfrozenProtocol",
    "ProtocolNotExecutable",
    "SLOTS", "SCIENTIFIC_SLOTS", "canonical_bytes", "protocol_hash",
    "validate_protocol", "require_frozen", "require_executable",
    "unfilled_slots",
]


class ProtocolError(Exception):
    """Base: the protocol schema refused."""


class IncompleteProtocol(ProtocolError):
    """One or more required slots are unfilled, empty, or unknown."""


class UnfrozenProtocol(ProtocolError):
    """The protocol's canonical hash does not match the declared freeze."""


class ProtocolNotExecutable(ProtocolError):
    """A standing blocker forbids execution regardless of completeness."""


# Every slot of the framework document, in its declared order.  There is no
# default for any of them; the value is supplied by an adopted author protocol
# or the slot refuses.
SLOTS: Mapping[str, str] = {
    "S-W": "world: topology, coordinates, boundary, account level",
    "S-P": "potential V_loc: which coordinates enter, with which parameters",
    "S-Q": "conservation profile per quantity (field list: "
           "CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md section 14.2)",
    "S-C": "C_a declaration per action class, with category",
    "S-A": "action set and its atomic decomposition (framework rules A-1..A-4)",
    "S-M": "simultaneous-action bound m and the group resolver",
    "S-R": "arms and their selection rules",
    "S-D": "regeneration, demand and disturbance processes",
    "S-V": "reserve and homeostasis constraint definitions",
    "S-T": "horizon, burn-in, measurement window",
    "S-H": "hypotheses, metrics, falsifiers, positive controls, outcome "
           "classes, interpretation rules",
    "S-U": "potential-unit to EBU-unit identification, or an explicit "
           "restriction to ranking only",
    "S-X": "execution authorization, host, and caps",
}

# The slots that are preregistration rather than architecture.  They belong to
# the author alone; no agent may fill them.  Kept as a named set so that a
# future caller can check the boundary explicitly rather than by convention.
SCIENTIFIC_SLOTS = ("S-W", "S-P", "S-R", "S-D", "S-V", "S-T", "S-H", "S-U",
                    "S-X")


def canonical_bytes(protocol: Mapping) -> bytes:
    """Canonical JSON encoding: sorted keys, compact, ASCII, no NaN.

    Mirrors the canonicalization the repository already uses for plan digests
    so that a protocol hash is comparable with the rest of the programme.
    """
    return json.dumps(protocol, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def protocol_hash(protocol: Mapping) -> str:
    """SHA-256 over the canonical encoding."""
    return hashlib.sha256(canonical_bytes(protocol)).hexdigest()


def unfilled_slots(protocol: Mapping) -> tuple:
    """Slots that are absent, ``None``, or empty after stripping."""
    missing = []
    for slot in SLOTS:
        if slot not in protocol:
            missing.append(slot)
            continue
        value = protocol[slot]
        if value is None:
            missing.append(slot)
        elif isinstance(value, str) and not value.strip():
            missing.append(slot)
        elif isinstance(value, (list, tuple, dict)) and len(value) == 0:
            missing.append(slot)
    return tuple(missing)


def validate_protocol(protocol: Mapping) -> Mapping:
    """Refuse unless every slot is filled and no unknown slot is present."""
    if not isinstance(protocol, Mapping):
        raise IncompleteProtocol("a protocol must be a mapping of slot -> value")
    unknown = tuple(sorted(set(protocol) - set(SLOTS)))
    if unknown:
        raise IncompleteProtocol(
            f"unknown slot(s) {unknown}; the declared slots are "
            f"{tuple(SLOTS)}. An unrecognized slot is refused rather than "
            f"ignored, so a protocol cannot smuggle in an undeclared choice.")
    missing = unfilled_slots(protocol)
    if missing:
        raise IncompleteProtocol(
            f"unfilled slot(s) {missing}. Each is a refusal condition, never a "
            f"default: "
            + "; ".join(f"{s} = {SLOTS[s]}" for s in missing))
    return protocol


def require_frozen(protocol: Mapping, declared_hash: str) -> str:
    """Refuse unless the protocol matches its declared freeze exactly."""
    validate_protocol(protocol)
    if not isinstance(declared_hash, str) or len(declared_hash) != 64:
        raise UnfrozenProtocol(
            "declared_hash must be a 64-character SHA-256 hex digest")
    actual = protocol_hash(protocol)
    if actual != declared_hash.lower():
        raise UnfrozenProtocol(
            f"protocol hash mismatch: computed {actual}, declared "
            f"{declared_hash.lower()}. A frozen preregistration is never "
            f"altered to make an implementation or a result pass.")
    return actual


def require_executable(protocol: Mapping, declared_hash: str) -> None:
    """Refuse execution while any standing blocker is open.

    This function has no success path today and is not expected to acquire one
    without explicit author decisions.  It validates and freeze-checks first,
    so that an incomplete protocol is reported as incomplete rather than merely
    blocked, and then refuses on the open escalations.
    """
    require_frozen(protocol, declared_hash)
    standing = tuple(sorted(ac.OPEN_ESCALATIONS))
    if standing:
        detail = "; ".join(f"{code}: {ac.OPEN_ESCALATIONS[code]}"
                           for code in standing)
        raise ProtocolNotExecutable(
            f"execution refused: {len(standing)} standing escalation(s) "
            f"require an author decision. {detail} "
            f"See {ac.COORDINATE_DOCUMENT} section 6.")
