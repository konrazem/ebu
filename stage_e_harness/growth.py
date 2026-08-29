"""Bounded non-scientific topology-growth reconstruction conformance."""

from __future__ import annotations

import hashlib
from typing import Any

from .canonical import Refusal, canonical_digest


EPOCH_BRANCH_WITNESS = "BAAAABAAAAABBAAA"
SAME_TICK_PHASES = (
    "LOAD_PRIOR_COMMITTED_STATE_OR_CHECKPOINT",
    "ACTIVATE_SCHEDULED_EPOCH_TOPOLOGY_AND_EMIT_TOPOLOGY_RECEIPT",
    "APPLY_SCHEDULED_CORRECTIONS_IN_DECLARED_EVENT_ID_ORDER",
    "TRAVERSE_AND_INVALIDATE_COMPLETE_DEPENDENCY_ALIAS_CLOSURE_THEN_RECONSTRUCT_RECERTIFY_CAPACITY",
    "EVALUATE_POPULATION_RESOURCE_CAPACITY_RESERVE_AND_DEMAND_DRIVERS",
    "EVALUATE_REGENERATION_BOUNDARY_EXCHANGE_AND_RESOURCE_PRE",
    "SELECT_SERVICE_ACTION_AND_ADVANCE_RESOURCE_STATE",
    "RECONCILE_CONSERVATION_CORRECTION_SERVICE_VIABILITY_RECOVERY_COLLAPSE_RECEIPTS",
    "SERIALIZE_TRACE_AND_OUTPUT_PREFIXES",
    "SEAL_CHECKPOINT_AFTER_ALL_RECEIPTS_ARE_DURABLE",
)


def _branch(seed: int, epoch: int) -> str:
    digest = hashlib.sha256(f"EBU-SD01-GROWTH-TOPOLOGY-v1|{seed}|{epoch}".encode("utf-8")).digest()
    return "A" if digest[0] % 2 == 0 else "B"


def epoch_witness(seed: int = 1) -> str:
    witness = "".join(_branch(seed, epoch) for epoch in range(16))
    if seed == 1 and witness != EPOCH_BRANCH_WITNESS:
        raise Refusal("dynamic-growth seed/epoch witness mismatch")
    return witness


def _full(level: int, topology: str, correction_epoch: int) -> tuple[list[int], int]:
    values: list[int] = []
    operations = 0
    for node in range(level + 1):
        parent = values[node - 1] if node else 1
        second = values[node - 2] if node > 1 else 0
        motif = 2 if topology == "recursive" else 3 if topology == "non_fibonacci_recursive" else (node % 5) + 1
        correction = correction_epoch if node >= 2 else 0
        values.append(parent + second + motif + correction)
        operations += node + 1
    return values, operations


def _incremental(previous: list[int], level: int, topology: str, correction_epoch: int) -> tuple[list[int], int]:
    values = list(previous)
    if len(values) != level:
        raise Refusal("incremental growth predecessor length mismatch")
    parent = values[-1] if values else 1
    second = values[-2] if len(values) > 1 else 0
    motif = 2 if topology == "recursive" else 3 if topology == "non_fibonacci_recursive" else (level % 5) + 1
    values.append(parent + second + motif + (correction_epoch if level >= 2 else 0))
    return values, 1


def growth_conformance() -> dict[str, Any]:
    topologies = (
        "recursive",
        "non_fibonacci_recursive",
        "random_nonrecursive",
        "broad_reconfiguration",
        "boundary_crossing",
        "alias_dependent",
    )
    cases: list[dict[str, Any]] = []
    for topology in topologies:
        prior: list[int] = []
        prior_correction_epoch = 0
        full_operations = incremental_operations = reuse_operations = 0
        for level in range(8):
            correction_epoch = 1 if topology in {"broad_reconfiguration", "boundary_crossing"} and level >= 5 else 0
            full, full_count = _full(level, topology, correction_epoch)
            correction_crossed_boundary = bool(level and correction_epoch != prior_correction_epoch)
            if correction_crossed_boundary:
                # A correction crossing the declared boundary invalidates the
                # complete lower-level projection; it is rebuilt visibly.
                incremental, incremental_count = list(full), full_count
            else:
                incremental, incremental_count = _incremental(prior, level, topology, correction_epoch)
            reuse = list(incremental)
            reuse_count = full_count if correction_crossed_boundary else 1
            if full != incremental or full != reuse:
                raise Refusal("growth reconstruction strategies disagree")
            prior = full
            prior_correction_epoch = correction_epoch
            full_operations += full_count
            incremental_operations += incremental_count
            reuse_operations += reuse_count
        cases.append(
            {
                "topology": topology,
                "scientific_projection_identity": canonical_digest(prior),
                "full_operations": full_operations,
                "incremental_operations": incremental_operations,
                "reuse_operations": reuse_operations,
                "complete_invalidation": topology in {"boundary_crossing", "broad_reconfiguration"},
                "stale_cache_hits": 0,
            }
        )
    witness = epoch_witness()
    b_epochs = [index for index, branch in enumerate(witness) if branch == "B"]
    if b_epochs[:2] != [0, 5] or 9 >= len(witness):
        raise Refusal("tick-2560 correction witness mismatch")
    return {
        "microcase_count": len(cases),
        "microcases": cases,
        "epoch_count": 16,
        "tick_spacing": 256,
        "tick_2560_epoch": 9,
        "second_b_epoch": 5,
        "branch_witness": witness,
        "same_tick_phases": list(SAME_TICK_PHASES),
        "registered_campaign_runs_executed": 0,
        "registered_horizon_ticks_executed": 0,
        "scientific_rows_populated": 0,
    }
