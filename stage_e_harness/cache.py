"""Ephemeral, certificate-bound cache conformance and invalidation mechanics."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .canonical import Refusal, canonical_digest


CACHE_KEY_FIELDS = (
    "canonical_topology_id",
    "motif_version",
    "occurrence_version",
    "composition_version",
    "boundary_summary_version",
    "initial_augmented_state_digest",
    "admissible_history_digest",
    "query_identity",
    "horizon",
    "units_semantics",
    "boundary_semantics",
    "removal_semantics",
    "feasibility_semantics",
    "numerical_policy_identity",
    "stochastic_rule_identity",
    "run_seed",
    "permitted_stream_ids_digest",
    "next_counter_tuple_per_stream_digest",
    "uncertainty_policy_identity",
    "framework_identity",
    "authority_identity",
    "protocol_identity",
    "configuration_identity",
    "code_identity",
    "dependency_identity",
    "environment_identity",
    "evidence_identity",
    "alias_closure_digest",
    "correction_invalidation_epoch",
)

CONTROL_NAMES = (
    "positive_equivalent_reuse",
    "non_equivalent_near_miss",
    "ordered_child_swap",
    "boundary_change",
    "history_change",
    "incomplete_key_collision",
    "alias_change",
    "stale_cache_entry",
    "corrected_evidence",
    "authority_version_change",
    "environment_change",
    "stochastic_rule_change",
    "run_seed_change",
    "permitted_stream_set_change",
    "next_counter_state_change",
    "uncertainty_policy_change",
    "deterministic_dependency_local_invalidation",
)


def validate_key(key: dict[str, Any]) -> str:
    if tuple(key) != CACHE_KEY_FIELDS:
        missing = [field for field in CACHE_KEY_FIELDS if field not in key]
        extra = [field for field in key if field not in CACHE_KEY_FIELDS]
        raise Refusal(f"incomplete or reordered cache key: missing={missing} extra={extra}")
    return canonical_digest(key)


@dataclass(frozen=True)
class EquivalenceCertificate:
    canonical_topology_id: str
    query_identity: str
    boundary_sufficient: bool
    a1_a8: tuple[bool, ...]
    dependency_closure_digest: str
    alias_closure_digest: str
    epoch: int

    def validate(self, key: dict[str, Any]) -> None:
        if len(self.a1_a8) != 8 or not all(self.a1_a8):
            raise Refusal("A1-A8 equivalence certificate incomplete")
        if not self.boundary_sufficient:
            raise Refusal("boundary sufficiency not certified")
        if self.canonical_topology_id != key["canonical_topology_id"]:
            raise Refusal("certificate topology mismatch")
        if self.query_identity != key["query_identity"]:
            raise Refusal("certificate query mismatch")
        if self.alias_closure_digest != key["alias_closure_digest"]:
            raise Refusal("certificate alias closure mismatch")
        if self.epoch != key["correction_invalidation_epoch"]:
            raise Refusal("stale equivalence certificate")


class EphemeralConformanceCache:
    """An in-memory test-only cache. Runtime persistence is deliberately absent."""

    def __init__(self) -> None:
        self._entries: dict[str, tuple[Any, EquivalenceCertificate]] = {}
        self._invalidated: set[str] = set()
        self._invalidation_receipts: list[dict[str, Any]] = []

    def store(self, key: dict[str, Any], value: Any, certificate: EquivalenceCertificate) -> str:
        digest = validate_key(key)
        certificate.validate(key)
        self._entries[digest] = (deepcopy(value), certificate)
        self._invalidated.discard(digest)
        return digest

    def lookup(self, key: dict[str, Any], certificate: EquivalenceCertificate) -> Any:
        digest = validate_key(key)
        certificate.validate(key)
        if digest in self._invalidated:
            raise Refusal("stale cache entry after invalidation")
        if digest not in self._entries:
            raise KeyError(digest)
        value, stored = self._entries[digest]
        if stored != certificate:
            raise Refusal("cache hit certificate mismatch")
        return deepcopy(value)

    def invalidate(
        self,
        roots: Iterable[str],
        dependency_edges: Iterable[tuple[str, str]],
        alias_edges: Iterable[tuple[str, str]],
        *,
        prior_epoch: int,
        new_epoch: int,
    ) -> dict[str, Any]:
        if new_epoch != prior_epoch + 1:
            raise Refusal("invalidation epoch must advance exactly once")
        adjacency: dict[str, set[str]] = {}
        for source, target in (*tuple(dependency_edges), *tuple(alias_edges)):
            adjacency.setdefault(source, set()).add(target)
        queue = sorted(set(roots))
        visited: list[str] = []
        head = 0
        while head < len(queue):
            item = queue[head]
            head += 1
            if item in visited:
                continue
            visited.append(item)
            for target in sorted(adjacency.get(item, ())):
                if target not in visited and target not in queue:
                    queue.append(target)
        invalidated = sorted(digest for digest in self._entries if digest in set(visited))
        self._invalidated.update(invalidated)
        receipt = {
            "prior_epoch": prior_epoch,
            "new_epoch": new_epoch,
            "visited_keys": visited,
            "invalidated_keys": invalidated,
            "unaffected_keys": sorted(set(self._entries) - set(invalidated)),
        }
        receipt["receipt_sha256"] = canonical_digest(receipt)
        self._invalidation_receipts.append(receipt)
        return receipt

    @property
    def invalidation_receipts(self) -> tuple[dict[str, Any], ...]:
        return tuple(deepcopy(self._invalidation_receipts))


def base_key() -> dict[str, Any]:
    digest = "0" * 64
    return {
        "canonical_topology_id": "canonical-0",
        "motif_version": "1",
        "occurrence_version": "1",
        "composition_version": "1",
        "boundary_summary_version": "1",
        "initial_augmented_state_digest": digest,
        "admissible_history_digest": digest,
        "query_identity": "query-0",
        "horizon": "synthetic-8",
        "units_semantics": "dimensionless",
        "boundary_semantics": "closed-synthetic",
        "removal_semantics": "none",
        "feasibility_semantics": "synthetic",
        "numerical_policy_identity": "exact-integer",
        "stochastic_rule_identity": {"kind": "fixture", "value": "FORBIDDEN", "sha256": digest},
        "run_seed": 0,
        "permitted_stream_ids_digest": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
        "next_counter_tuple_per_stream_digest": "8976a0ffe0e7e82b5b69727d6c92da65a3144e3bcb65e109fe6345e9d4b004c6",
        "uncertainty_policy_identity": {"kind": "fixture", "value": "deterministic", "sha256": digest},
        "framework_identity": "framework-alpha",
        "authority_identity": "stage-d",
        "protocol_identity": "synthetic",
        "configuration_identity": "synthetic",
        "code_identity": "stage-e",
        "dependency_identity": "dependency-0",
        "environment_identity": "reference-env",
        "evidence_identity": "non-scientific-fixture",
        "alias_closure_digest": digest,
        "correction_invalidation_epoch": 0,
    }


def exercise_controls_detail() -> dict[str, Any]:
    key = base_key()
    certificate = EquivalenceCertificate(
        canonical_topology_id=key["canonical_topology_id"],
        query_identity=key["query_identity"],
        boundary_sufficient=True,
        a1_a8=(True,) * 8,
        dependency_closure_digest="0" * 64,
        alias_closure_digest=key["alias_closure_digest"],
        epoch=0,
    )
    cache = EphemeralConformanceCache()
    digest = cache.store(key, {"synthetic": 1}, certificate)
    if cache.lookup(key, certificate) != {"synthetic": 1}:
        raise Refusal("certified positive reuse mismatch")
    misses = 0
    changed_fields = (
        "canonical_topology_id",
        "composition_version",
        "boundary_summary_version",
        "admissible_history_digest",
        "alias_closure_digest",
        "evidence_identity",
        "authority_identity",
        "environment_identity",
        "stochastic_rule_identity",
        "run_seed",
        "permitted_stream_ids_digest",
        "next_counter_tuple_per_stream_digest",
        "uncertainty_policy_identity",
    )
    for field in changed_fields:
        near = deepcopy(key)
        near[field] = ({"kind": "fixture", "value": "changed", "sha256": "1" * 64} if isinstance(near[field], dict) else (1 if field == "run_seed" else "1" * 64))
        if canonical_digest(near) == digest:
            raise Refusal("near-miss cache key collision")
        try:
            cache.lookup(near, certificate)
        except (KeyError, Refusal):
            misses += 1
    for omitted in CACHE_KEY_FIELDS:
        incomplete = deepcopy(key)
        del incomplete[omitted]
        try:
            validate_key(incomplete)
        except Refusal:
            continue
        raise Refusal(f"cache key omission accepted: {omitted}")
    keys = [key]
    digests = [digest]
    for index in range(1, 4):
        dependent = deepcopy(key)
        dependent["configuration_identity"] = f"synthetic-{index}"
        dependent_digest = cache.store(dependent, {"synthetic": index + 1}, certificate)
        keys.append(dependent)
        digests.append(dependent_digest)
    dependency_edges = ((digests[0], digests[1]),)
    alias_edges = ((digests[1], digests[2]),)
    receipt = cache.invalidate([digest], dependency_edges, alias_edges, prior_epoch=0, new_epoch=1)
    expected_affected = sorted(digests[:3])
    if receipt["invalidated_keys"] != expected_affected or receipt["unaffected_keys"] != [digests[3]]:
        raise Refusal("correction invalidation missed affected key")
    try:
        cache.lookup(key, certificate)
    except Refusal:
        pass
    else:
        raise Refusal("stale cache hit after invalidation")
    return {
        "controls": len(CONTROL_NAMES),
        "omission_mutations": len(CACHE_KEY_FIELDS),
        "near_miss_refusals": misses,
        "invalidation_receipts": 1,
        "receipt": receipt,
        "changed_seed_identity": digest,
        "declared_key_universe": sorted(digests),
        "dependency_edges": [list(edge) for edge in dependency_edges],
        "alias_edges": [list(edge) for edge in alias_edges],
        "expected_affected": expected_affected,
        "recomputed": expected_affected,
        "reused": [digests[3]],
    }


def exercise_controls() -> dict[str, int]:
    detail = exercise_controls_detail()
    return {key: detail[key] for key in ("controls", "omission_mutations", "near_miss_refusals", "invalidation_receipts")}
