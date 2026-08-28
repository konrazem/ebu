"""Synthetic-only checkpoint, attempt-binding, and cumulative-accounting checks."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable

from .canonical import Refusal, canonical_digest, identity, verify_identity


EMPTY_ARRAY_DIGEST = "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945"
EMPTY_COUNTER_SET_DIGEST = "8976a0ffe0e7e82b5b69727d6c92da65a3144e3bcb65e109fe6345e9d4b004c6"
POLICY_FIELDS = (
    "parallelization_boundary_identity",
    "worker_allocation_policy_identity",
    "storage_location_identity",
    "durability_policy_identity",
    "restart_policy_identity",
)


def counter_tuple_set_preimage(checkpoint: dict[str, Any]) -> dict[str, Any]:
    return {
        "permitted_stream_set_identity": checkpoint["permitted_stream_set_identity"],
        "ordered_permitted_stream_ids": checkpoint["ordered_permitted_stream_ids"],
        "next_counter_tuples": checkpoint["next_counter_tuples"],
    }


def validate_counter_state(checkpoint: dict[str, Any]) -> None:
    mode = checkpoint.get("counter_state_mode")
    streams = checkpoint.get("ordered_permitted_stream_ids")
    tuples = checkpoint.get("next_counter_tuples")
    if not isinstance(streams, list) or not isinstance(tuples, list):
        raise Refusal("checkpoint counter arrays missing")
    if streams != sorted(streams) or len(streams) != len(set(streams)):
        raise Refusal("permitted streams must be unique UTF-8-sorted")
    if [row.get("stream_id") for row in tuples] != streams:
        raise Refusal("counter tuple projection differs from permitted stream set")
    if mode == "DETERMINISTIC_EMPTY":
        expected_set = {"kind": "permitted_stream_set/v2", "value": EMPTY_ARRAY_DIGEST, "sha256": EMPTY_ARRAY_DIGEST}
        expected_tuple = {"kind": "next_counter_tuple_set/v2", "value": EMPTY_COUNTER_SET_DIGEST, "sha256": EMPTY_COUNTER_SET_DIGEST}
        if checkpoint.get("seed") != 0 or checkpoint.get("stochastic_rule_identity", {}).get("value") != "FORBIDDEN":
            raise Refusal("deterministic checkpoint stochastic authority mismatch")
        if streams or tuples or checkpoint.get("permitted_stream_set_identity") != expected_set:
            raise Refusal("deterministic checkpoint must contain canonical empty state")
        if checkpoint.get("next_counter_tuple_set_identity") != expected_tuple:
            raise Refusal("deterministic empty counter digest mismatch")
    elif mode == "STOCHASTIC_NONEMPTY":
        if not streams or not tuples:
            raise Refusal("stochastic checkpoint requires complete nonempty counters")
        expected_stream_digest = canonical_digest(streams)
        expected_stream_identity = {
            "kind": "permitted_stream_set/v2",
            "value": expected_stream_digest,
            "sha256": expected_stream_digest,
        }
        if checkpoint.get("permitted_stream_set_identity") != expected_stream_identity:
            raise Refusal("stochastic permitted-stream identity mismatch")
        for row in tuples:
            if set(row) != {"stream_id", "tick", "event_index", "draw_index", "attempt_index", "draw_status"}:
                raise Refusal("counter tuple shape mismatch")
            if row["draw_status"] != "READY" or not 0 <= row["attempt_index"] <= 999_999:
                raise Refusal("terminal or invalid counter cannot continue")
        verify_identity(checkpoint["next_counter_tuple_set_identity"], counter_tuple_set_preimage(checkpoint), kind="next_counter_tuple_set/v2")
    else:
        raise Refusal("unknown counter-state mode")


def process_allocation_preimage(record: dict[str, Any]) -> dict[str, Any]:
    return {key: record[key] for key in ("worker_count", "ordered_worker_allocations", "scheduler_allocation_identity", "policy_conformance_receipt_identity")}


def validate_process_allocation(record: dict[str, Any]) -> None:
    workers = record.get("ordered_worker_allocations")
    count = record.get("worker_count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 1 or not isinstance(workers, list) or len(workers) != count:
        raise Refusal("process allocation worker count mismatch")
    if [worker.get("worker_ordinal") for worker in workers] != list(range(count)):
        raise Refusal("worker ordinals must be contiguous and ordered")
    process_keys = [(worker.get("process_identity", {}).get("sha256"), worker.get("process_index")) for worker in workers]
    if len(process_keys) != len(set(process_keys)):
        raise Refusal("duplicate process identity/index")
    expected = canonical_digest(process_allocation_preimage(record))
    if record.get("allocation_sha256") != expected:
        raise Refusal("process allocation digest mismatch")


def attempt_binding_preimage(record: dict[str, Any]) -> dict[str, Any]:
    keys = (
        "campaign_id",
        "scientific_run_id",
        "campaign_execution_binding_identity",
        "attempt_ordinal",
        "incoming_checkpoint_identity",
        *POLICY_FIELDS,
        "process_allocation_identity",
        "policy_conformance_receipt_identity",
    )
    return {key: record[key] for key in keys}


def validate_attempt_binding(record: dict[str, Any]) -> None:
    validate_process_allocation(record["process_allocation"])
    allocation_digest = canonical_digest(process_allocation_preimage(record["process_allocation"]))
    allocation_identity = record["process_allocation_identity"]
    if allocation_identity != {"kind": "process_allocation/v2", "value": allocation_digest, "sha256": allocation_digest}:
        raise Refusal("embedded process allocation identity mismatch")
    if record["policy_conformance_receipt_identity"] != record["process_allocation"]["policy_conformance_receipt_identity"]:
        raise Refusal("singular policy conformance receipt mismatch")
    expected = canonical_digest(attempt_binding_preimage(record))
    if record.get("binding_sha256") != expected:
        raise Refusal("attempt binding digest mismatch")


@dataclass(frozen=True)
class SyntheticState:
    sequence: int
    accumulator: int
    trace: tuple[int, ...]

    def value(self) -> dict[str, Any]:
        return {"sequence": self.sequence, "accumulator": self.accumulator, "trace": list(self.trace)}


def synthetic_step(state: SyntheticState, study_index: int) -> SyntheticState:
    """Pure arithmetic fixture; it is not an EBU model state transition."""

    next_value = state.accumulator * 17 + (study_index + 1) * 13 + state.sequence
    return SyntheticState(state.sequence + 1, next_value, state.trace + (next_value,))


def synthetic_uninterrupted(study_index: int, length: int = 28) -> SyntheticState:
    state = SyntheticState(0, study_index + 1, ())
    for _ in range(length):
        state = synthetic_step(state, study_index)
    return state


def synthetic_sliced(study_index: int, slices: int, length: int = 28) -> tuple[SyntheticState, dict[str, int]]:
    if slices not in {1, 2, 7} or length % slices:
        raise Refusal("synthetic continuation slices outside frozen domain")
    state = SyntheticState(0, study_index + 1, ())
    cumulative = {"attempt_count": 0, "primary_evaluations": 0, "physical_trace_bytes": 0, "logical_trace_bytes": 0}
    per_slice = length // slices
    for _attempt in range(slices):
        previous = deepcopy(cumulative)
        for _ in range(per_slice):
            state = synthetic_step(state, study_index)
            cumulative["primary_evaluations"] += 1
            cumulative["physical_trace_bytes"] += 8
            cumulative["logical_trace_bytes"] += 8
        cumulative["attempt_count"] += 1
        if any(cumulative[key] < previous[key] for key in cumulative):
            raise AssertionError("synthetic cumulative ledger reset")
    return state, cumulative


def continuation_equivalence(study_ids: Iterable[str]) -> dict[str, int]:
    study_ids = tuple(study_ids)
    comparisons = 0
    for index, _study_id in enumerate(study_ids):
        reference = synthetic_uninterrupted(index)
        reference_digest = canonical_digest(reference.value())
        for slices in (1, 2, 7):
            result, ledger = synthetic_sliced(index, slices)
            if canonical_digest(result.value()) != reference_digest:
                raise Refusal("synthetic checkpoint suffix differs from uninterrupted result")
            if ledger["attempt_count"] != slices or ledger["primary_evaluations"] != 28:
                raise Refusal("synthetic continuation cumulative accounting mismatch")
            comparisons += 1
    return {"studies": len(study_ids), "slice_comparisons": comparisons}
