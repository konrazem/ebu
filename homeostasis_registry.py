"""Registered homeostasis study: configuration, seed derivation and job set.

Implements `HOMEOSTASIS_STUDY_PREREGISTRATION.md`.

Lives outside the `homeostasis` package so registration tooling cannot perturb
the pinned package code identity.

Coupled forcing across loads
----------------------------

One counter-addressed raw forcing process is shared across every load level.
The per-tick uniform variate is drawn once, at a fixed address that does not
mention the load, and each load is realized by **thresholding that same
variate**. Consequently

    schedule(1/4)  subset of  schedule(1/2)  subset of  schedule(1)

and on a tick shared by two loads the raw edge and orientation proposal is
identical, because the edge is drawn at its own address which also does not
mention the load.

This is why the load is deliberately **absent** from the seed preimage. It is a
common-random-numbers design, registered before execution specifically to
isolate the causal effect of forcing *frequency*: two loads differ only in
which subset of one fixed disturbance stream is delivered, never in the
disturbances themselves.

Arm-specific `NULL_FORCING` is preserved as an observed consequence of arms
occupying different states. Arms share raw draws, not applied forcing. No
resample, clip, reversal, substitution or magnitude change occurs.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.numerics import Refusal
from homeostasis.harness import (
    DECLARED_LOADS,
    DECLARED_MENU_RULES,
    MENU_STRICT_PHYSICAL,
    MENU_WITH_NET_ZERO,
    code_identity,
)
from homeostasis.jobs import JobIdentity
from homeostasis.policies import CORE_POLICIES

PROTOCOL_ID = "EBU-HOMEOSTASIS-v1"
PREREGISTRATION_REF = "homeostasis-preregistration"
SEPARATOR = "|"
STREAM_NAMES = ("FORCING", "ACTOR")

STUDY_ID = "ebu-homeostasis-v1"
CONFIGURATION_ID = "cfg-3cell-homeostasis-v1"

# Frozen world, unchanged from registered Stage A/B.
REFERENCE = (10, 10, 10)
SCALES = (1, 1, 1)
QUANTA = (1,)
MAX_GROUP_SIZE = 2
DECLARED_MASS = Fraction(30)
FORCING_QUANTUM = Fraction(1)

# Frozen design.
HORIZON = 8192
BURN_IN = 2048
BLOCK = 2048
BLOCKS = 3
WINDOW = BLOCKS * BLOCK
REPLICATES = 64
LOADS = tuple(load.load_id for load in DECLARED_LOADS)
MENUS = (MENU_WITH_NET_ZERO, MENU_STRICT_PHYSICAL)
POLICIES = CORE_POLICIES

# The code identity this study is registered against.
REGISTERED_CODE_IDENTITY = (
    "8b462401a00ed8624fbd649e460b9e44e6adf8ba749ca1fa3872e9a6ddd4c3c6"
)
REGISTERED_GAUSSIAN_CODE_IDENTITY = (
    "a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55"
)


def seed_preimage(preregistration_sha: str, replicate: int, stream: str) -> bytes:
    """Seed address. The load is deliberately absent -- see the module note."""
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


def configuration_payload() -> dict:
    return {
        "protocol_id": PROTOCOL_ID,
        "study_id": STUDY_ID,
        "configuration_id": CONFIGURATION_ID,
        "reference": [str(v) for v in REFERENCE],
        "scales": [str(v) for v in SCALES],
        "quanta": [str(v) for v in QUANTA],
        "max_group_size": MAX_GROUP_SIZE,
        "declared_mass": str(DECLARED_MASS),
        "forcing_quantum": str(FORCING_QUANTUM),
        "loads": list(LOADS),
        "load_coupling": "shared raw process; each load thresholds the same per-tick variate",
        "load_in_seed_preimage": False,
        "menus": list(MENUS),
        "policies": list(POLICIES),
        "horizon": HORIZON,
        "burn_in": BURN_IN,
        "block": BLOCK,
        "blocks": BLOCKS,
        "replicates": REPLICATES,
        "capacity_version": "V1",
        "null_forcing_rule": "per-arm admissibility; no resample/clip/reverse/substitute",
        "owner_rule": "owner(a)=src(a)",
        "empty_group_in_menu": False,
        "potential_family": "EBU-POTENTIAL-LOCAL-GAUSSIAN-L1-v1",
        "event_profile": "EBU-GAUSSIAN-HOMEOSTASIS-PROFILE-v1",
        "region_rule": "EBU-GAUSSIAN-HOMEOSTATIC-REGION-v1",
        "primary_endpoint": "O95",
        "numeric_policy": "exact rational, tolerance 0",
    }


def configuration_identity() -> str:
    canonical = json.dumps(configuration_payload(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def assert_registered_identities() -> tuple[str, str]:
    from gaussian_harness.harness import code_identity as gaussian_identity
    actual = code_identity()
    if actual != REGISTERED_CODE_IDENTITY:
        raise Refusal(
            f"CODE_IDENTITY_MISMATCH: registered {REGISTERED_CODE_IDENTITY}, found {actual}"
        )
    pinned = gaussian_identity()
    if pinned != REGISTERED_GAUSSIAN_CODE_IDENTITY:
        raise Refusal(
            f"GAUSSIAN_CODE_IDENTITY_MISMATCH: registered "
            f"{REGISTERED_GAUSSIAN_CODE_IDENTITY}, found {pinned}"
        )
    return actual, pinned


def job_set(preregistration_sha: str) -> tuple[JobIdentity, ...]:
    """The complete registered job matrix, in canonical order."""
    manifest = derive_seed_manifest(preregistration_sha)
    configuration = configuration_identity()
    identity = code_identity()
    jobs: list[JobIdentity] = []
    for menu_rule in MENUS:
        for load_id in LOADS:
            for policy_id in POLICIES:
                for pair in manifest:
                    jobs.append(JobIdentity(
                        preregistration_id=f"{PROTOCOL_ID}@{preregistration_sha}",
                        configuration_identity=configuration,
                        code_identity=identity,
                        load_id=load_id,
                        policy_id=policy_id,
                        menu_rule=menu_rule,
                        replicate=pair.replicate,
                        horizon=HORIZON,
                        forcing_seed=pair.forcing_seed,
                        actor_seed=pair.actor_seed,
                    ))
    ids = [job.job_id for job in jobs]
    if len(set(ids)) != len(ids):
        raise Refusal("duplicate job identities in the registered matrix")
    return tuple(jobs)
