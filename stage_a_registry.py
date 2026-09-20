"""Stage-A registered configuration, mechanical seed derivation and runner.

Implements sections 2, 3, 6, 8 and 12 of `STAGE_A_PREREGISTRATION.md`.

This module lives outside `gaussian_harness` on purpose: the preregistration
pins the package's code identity, so registration-time tooling must not perturb
it.

Seeds are never chosen by hand. Each is derived from the frozen preregistration
commit, so the whole seed set is auditable by anyone who can recompute a
SHA-256, and no seed can be swapped because a result looks surprising.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.harness import (
    ARM_CONTROL,
    ARM_EBU,
    Run,
    TickBudget,
    WorldConfiguration,
    code_identity,
)
from gaussian_harness.numerics import Refusal
from gaussian_harness.stage_a import ShockSpecification, draw_shock, stage_a_world

PROTOCOL_ID = "EBU-STAGE-A-V1"
SEPARATOR = "|"
STREAM_NAMES = ("FORCING", "ACTOR")

# Frozen by STAGE_A_PREREGISTRATION.md sections 2, 6 and 8.
REFERENCE = (10, 10, 10)
SCALES = (1, 1, 1)
QUANTA = (1,)
MAX_GROUP_SIZE = 2
SHOCK_MAGNITUDES = (2,)
REPLICATES = 128
HORIZON = 256
STUDY_ID = "ebu-stage-a-v1"
CONFIGURATION_ID = "cfg-3cell-stage-a-v1"

# The frozen preregistration commit is resolved by this tag, so the executor
# never takes the preregistration SHA from a conversational string.
PROTOCOL_ID_COMMIT_REF = "stage-a-preregistration"

REGISTERED_CODE_IDENTITY = (
    "a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55"
)


def seed_preimage(preregistration_sha: str, replicate: int, stream: str) -> bytes:
    """Exact ASCII preimage: PROTOCOL|C_pre|rrr|STREAM, no trailing newline."""
    if len(preregistration_sha) != 40 or preregistration_sha != preregistration_sha.lower():
        raise Refusal("preregistration sha must be 40 lowercase hex characters")
    if not all(character in "0123456789abcdef" for character in preregistration_sha):
        raise Refusal("preregistration sha must be hexadecimal")
    if not 0 <= replicate <= 999:
        raise Refusal("replicate index must fit three decimal digits")
    if stream not in STREAM_NAMES:
        raise Refusal(f"undeclared stream name {stream!r}")
    text = SEPARATOR.join((PROTOCOL_ID, preregistration_sha, f"{replicate:03d}", stream))
    return text.encode("ascii")


def derive_seed(preregistration_sha: str, replicate: int, stream: str) -> int:
    """First 8 bytes of the SHA-256 preimage, big-endian unsigned 64-bit."""
    digest = hashlib.sha256(seed_preimage(preregistration_sha, replicate, stream)).digest()
    return int.from_bytes(digest[:8], "big")


@dataclass(frozen=True)
class SeedPair:
    replicate: int
    forcing_seed: int
    actor_seed: int


def derive_seed_manifest(preregistration_sha: str) -> tuple[SeedPair, ...]:
    return tuple(
        SeedPair(
            replicate,
            derive_seed(preregistration_sha, replicate, "FORCING"),
            derive_seed(preregistration_sha, replicate, "ACTOR"),
        )
        for replicate in range(REPLICATES)
    )


def registered_world(arm: str) -> WorldConfiguration:
    return stage_a_world(
        STUDY_ID,
        CONFIGURATION_ID,
        list(REFERENCE),
        list(SCALES),
        list(QUANTA),
        MAX_GROUP_SIZE,
        arm=arm,
    )


def registered_shocks() -> ShockSpecification:
    return ShockSpecification.declare(list(SHOCK_MAGNITUDES))


def configuration_payload() -> dict:
    """Canonical description of every frozen configuration parameter."""
    return {
        "protocol_id": PROTOCOL_ID,
        "study_id": STUDY_ID,
        "configuration_id": CONFIGURATION_ID,
        "reference": [str(value) for value in REFERENCE],
        "scales": [str(value) for value in SCALES],
        "quanta": [str(value) for value in QUANTA],
        "max_group_size": MAX_GROUP_SIZE,
        "shock_magnitudes": [str(value) for value in SHOCK_MAGNITUDES],
        "replicates": REPLICATES,
        "horizon": HORIZON,
        "arms": [ARM_EBU, ARM_CONTROL],
        "owner_rule": "owner(a)=src(a)",
        "empty_group_in_menu": False,
        "potential_family": "EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1",
        "event_profile": "EBU-GAUSSIAN-EVENT-PROFILE-v1",
        "numeric_policy": "exact rational, tolerance 0",
    }


def configuration_identity() -> str:
    canonical = json.dumps(configuration_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_registered_code_identity() -> str:
    """Fail closed if the harness code has drifted from the preregistration."""
    actual = code_identity()
    if actual != REGISTERED_CODE_IDENTITY:
        raise Refusal(
            f"CODE_IDENTITY_MISMATCH: registered {REGISTERED_CODE_IDENTITY}, found {actual}"
        )
    return actual


def run_registered_replicate(arm: str, pair: SeedPair, preregistration_sha: str) -> Run:
    """One registered replicate: shock at tick 0, then HORIZON actor ticks."""
    world = registered_world(arm)
    budget = TickBudget.registered_study(HORIZON + 1, f"{PROTOCOL_ID}@{preregistration_sha}")
    run = Run(world, pair.forcing_seed, pair.actor_seed, budget)
    shock = draw_shock(world, registered_shocks(), pair.forcing_seed)
    first = run.run_tick(forcing=shock, actor_enabled=False)
    if first.audit_ledger <= 0:
        raise Refusal(
            f"ZERO_OR_NEGATIVE_SHOCK: replicate {pair.replicate} drew D={first.audit_ledger}"
        )
    for _ in range(HORIZON):
        run.run_tick()
    return run
