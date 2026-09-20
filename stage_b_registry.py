"""Stage-B registered configuration, seed derivation and continuous-forcing runner.

Implements sections 3, 4, 6, 8 and 14 of `STAGE_B_PREREGISTRATION.md`.

Lives outside `gaussian_harness` so registration tooling cannot perturb the
pinned package code identity, which is unchanged from Stage A.

The mechanism is unchanged. Nothing here adds capacity decay, expiry, caps,
pooling, borrowing or any selection that reads EBU.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from fractions import Fraction

from gaussian_harness.forcing import ForcingIncrement
from gaussian_harness.harness import (
    ARM_CONTROL,
    ARM_EBU,
    Run,
    TickBudget,
    WorldConfiguration,
    code_identity,
)
from gaussian_harness.numerics import Refusal
from gaussian_harness.rng import STREAM_FORCING, Counter, uniform_index
from gaussian_harness.stage_a import stage_a_world

PROTOCOL_ID = "EBU-STAGE-B-V1"
PREREGISTRATION_REF = "stage-b-preregistration"
SEPARATOR = "|"
STREAM_NAMES = ("FORCING", "ACTOR")

# Frozen by STAGE_B_PREREGISTRATION.md sections 3, 4, 5, 6 and 8.
REFERENCE = (10, 10, 10)
SCALES = (1, 1, 1)
QUANTA = (1,)
MAX_GROUP_SIZE = 2
FORCING_QUANTUM = Fraction(1)          # q0: the only declared transfer quantum
HORIZON = 8192
BURN_IN = 2048
BLOCK = 2048
BLOCKS = 3
WINDOW = BLOCKS * BLOCK                # 6144
REPLICATES = 64
V_MAX = Fraction(300)                  # exact, at every simplex vertex
DECLARED_MASS = Fraction(30)
STUDY_ID = "ebu-stage-b-v1"
CONFIGURATION_ID = "cfg-3cell-stage-b-v1"

REGISTERED_CODE_IDENTITY = (
    "a9158eefb4eaf7d2dd609f1292d97f245290d73ec4e0393288ce5fd47725fe55"
)

STATUS_NULL_FORCING = "NULL_FORCING"


def seed_preimage(preregistration_sha: str, replicate: int, stream: str) -> bytes:
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


def exact_v_max() -> Fraction:
    """V is convex on {x>=0, sum x = M}, so its maximum is at a vertex M*e_k."""
    world = registered_world(ARM_EBU)
    potential = world.potential
    best = Fraction(0)
    for index in range(potential.dimension):
        vertex = tuple(
            DECLARED_MASS if position == index else Fraction(0)
            for position in range(potential.dimension)
        )
        best = max(best, potential.value_total(vertex))
    return best


def raw_forcing_proposal(
    configuration: WorldConfiguration, forcing_seed: int, tick: int
) -> ForcingIncrement:
    """Draw the raw environmental proposal: edge only, amplitude fixed at q0.

    Depends solely on the forcing seed and the tick, so both arms receive the
    identical raw environmental process.
    """
    edges = tuple(sorted(configuration.rules.edges))
    counter = Counter(
        configuration.study_id,
        configuration.configuration_id,
        forcing_seed,
        STREAM_FORCING,
        tick,
        0,
        0,
    )
    index, _ = uniform_index(counter, len(edges))
    source, destination = edges[index]
    return ForcingIncrement(source, destination, FORCING_QUANTUM)


def configuration_payload() -> dict:
    return {
        "protocol_id": PROTOCOL_ID,
        "study_id": STUDY_ID,
        "configuration_id": CONFIGURATION_ID,
        "reference": [str(v) for v in REFERENCE],
        "scales": [str(v) for v in SCALES],
        "quanta": [str(v) for v in QUANTA],
        "max_group_size": MAX_GROUP_SIZE,
        "forcing_quantum": str(FORCING_QUANTUM),
        "forcing_every_tick": True,
        "null_forcing_rule": "per-arm admissibility; no resample/clip/reverse/substitute",
        "horizon": HORIZON,
        "burn_in": BURN_IN,
        "block": BLOCK,
        "blocks": BLOCKS,
        "replicates": REPLICATES,
        "v_max": str(V_MAX),
        "declared_mass": str(DECLARED_MASS),
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
    actual = code_identity()
    if actual != REGISTERED_CODE_IDENTITY:
        raise Refusal(
            f"CODE_IDENTITY_MISMATCH: registered {REGISTERED_CODE_IDENTITY}, found {actual}"
        )
    return actual


def run_registered_replicate(arm: str, pair: SeedPair, preregistration_sha: str) -> dict:
    """One registered replicate under continuous forcing.

    Streams per-tick columns and clears the harness record buffer each tick, so
    memory stays flat across an 8192-tick horizon.
    """
    world = registered_world(arm)
    budget = TickBudget.registered_study(HORIZON, f"{PROTOCOL_ID}@{preregistration_sha}")
    run = Run(world, pair.forcing_seed, pair.actor_seed, budget)

    columns: dict[str, list] = {
        key: []
        for key in (
            "V", "sumB", "minB", "maxB", "J", "d_ext", "x_min", "status",
            "raw_forcing", "applied", "null_forcing",
            "n_feasible", "n_affordable", "n_rejected", "ebu_sign",
        )
    }
    balances_end = None
    worst_accounting = Fraction(0)
    worst_conservation = Fraction(0)
    worst_nonnegativity = Fraction(0)
    negative_capacity_ticks = 0
    previous_audit = Fraction(0)

    for tick in range(HORIZON):
        proposal = raw_forcing_proposal(world, pair.forcing_seed, tick)
        admissible = run.state[proposal.source] >= FORCING_QUANTUM
        record = run.run_tick(forcing=proposal if admissible else None)

        d_ext = record.audit_ledger - previous_audit
        previous_audit = record.audit_ledger

        rejected = 0
        for _, rows in record.projected_balances:
            if any(balance < 0 for _, balance in rows):
                rejected += 1
        chosen_value = dict(record.ebu_values).get(record.chosen_id)

        columns["V"].append(record.audit_potential)
        columns["sumB"].append(record.balance_total)
        columns["minB"].append(min(record.balances))
        columns["maxB"].append(max(record.balances))
        columns["J"].append(record.audit_ledger)
        columns["d_ext"].append(d_ext)
        columns["x_min"].append(min(record.state_after))
        columns["status"].append(record.status)
        columns["raw_forcing"].append(proposal.forcing_id)
        columns["applied"].append(record.forcing)
        columns["null_forcing"].append(not admissible)
        columns["n_feasible"].append(len(record.feasible_ids))
        columns["n_affordable"].append(len(record.affordable_ids))
        columns["n_rejected"].append(rejected)
        columns["ebu_sign"].append(
            (chosen_value > 0) - (chosen_value < 0) if chosen_value is not None else 0
        )

        worst_accounting = max(worst_accounting, abs(record.accounting_residual))
        worst_conservation = max(worst_conservation, abs(record.conservation_residual))
        worst_nonnegativity = max(worst_nonnegativity, abs(record.nonnegativity_residual))
        if arm == ARM_EBU and min(record.balances) < 0:
            negative_capacity_ticks += 1
        balances_end = record.balances
        run.records.clear()

    return {
        "columns": columns,
        "balances_end": balances_end,
        "run_id": run.run_id,
        "max_accounting_residual": worst_accounting,
        "max_conservation_residual": worst_conservation,
        "max_nonnegativity_residual": worst_nonnegativity,
        "negative_capacity_ticks": negative_capacity_ticks,
    }
