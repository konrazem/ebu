"""Exact DAG oracle agreement and O(V+E) FIFO Kahn conformance."""

from __future__ import annotations

import hashlib
import math
import resource
import sys
import time
from dataclasses import dataclass
from typing import Iterable, Sequence

from .canonical import Refusal, canonical_bytes, canonical_digest
from .oracles import direct_affected_vertices, direct_fifo_order


@dataclass(frozen=True)
class TraversalCounters:
    vertices: int
    edges: int
    indegree_initializations: int
    vertex_enqueues: int
    vertex_dequeues: int
    edge_inspections: int
    ready_queue_appends: int
    ready_queue_head_advances: int
    ready_node_comparisons: int
    logical_storage_slots: int


@dataclass(frozen=True)
class TraversalResult:
    affected: tuple[int, ...]
    order: tuple[int, ...]
    counters: TraversalCounters


def canonicalize_edges(edges: Iterable[tuple[int, int]]) -> tuple[list[tuple[int, int]], int, int]:
    rows = list(edges)
    if len(rows) == len(set(rows)) and rows == sorted(rows):
        return rows, 0, 0
    if len(rows) != len(set(rows)):
        raise Refusal("duplicate edge")
    width = 1
    comparisons = 0
    auxiliary = [None] * len(rows)
    source = rows
    destination = auxiliary
    while width < len(rows):
        for start in range(0, len(rows), 2 * width):
            left, middle, right = start, min(start + width, len(rows)), min(start + 2 * width, len(rows))
            i, j, out = left, middle, left
            while i < middle and j < right:
                comparisons += 1
                if source[i] <= source[j]:
                    destination[out] = source[i]
                    i += 1
                else:
                    destination[out] = source[j]
                    j += 1
                out += 1
            while i < middle:
                destination[out] = source[i]
                i += 1
                out += 1
            while j < right:
                destination[out] = source[j]
                j += 1
                out += 1
        source, destination = destination, source
        width *= 2
    result = list(source)
    bound = len(rows) * math.ceil(math.log2(len(rows))) if len(rows) > 1 else 0
    if comparisons > bound:
        raise AssertionError("canonical mergesort comparison bound defect")
    return result, comparisons, len(rows)


def fifo_kahn(vertices: int, edges: Sequence[tuple[int, int]], sources: Iterable[int]) -> TraversalResult:
    if not isinstance(vertices, int) or isinstance(vertices, bool) or vertices < 0 or vertices > 100_000:
        raise Refusal("DAG vertex count outside frozen cap")
    if len(edges) > 500_000:
        raise Refusal("DAG edge count outside frozen cap")
    if list(edges) != sorted(edges) or len(edges) != len(set(edges)):
        raise Refusal("FIFO Kahn requires sealed canonical unique edges")
    adjacency = [[] for _ in range(vertices)]
    for source, target in edges:
        if not (0 <= source < target < vertices):
            if not (0 <= source < vertices and 0 <= target < vertices):
                raise Refusal("edge endpoint outside graph")
            if source == target or source > target:
                raise Refusal("cycle or non-forward edge")
        adjacency[source].append(target)
    source_set = set(sources)
    if any(source < 0 or source >= vertices for source in source_set):
        raise Refusal("source outside graph")
    affected = set(source_set)
    frontier = list(sorted(source_set))
    head = 0
    reach_inspections = 0
    while head < len(frontier):
        vertex = frontier[head]
        head += 1
        for target in adjacency[vertex]:
            reach_inspections += 1
            if target not in affected:
                affected.add(target)
                frontier.append(target)
    selected = sorted(affected)
    selected_set = set(selected)
    indegree = [0] * vertices
    relevant_edges = 0
    for source, target in edges:
        if source in selected_set and target in selected_set:
            indegree[target] += 1
            relevant_edges += 1
    queue = [vertex for vertex in selected if indegree[vertex] == 0]
    enqueues = len(queue)
    order: list[int] = []
    queue_head = 0
    inspections = 0
    while queue_head < len(queue):
        vertex = queue[queue_head]
        queue_head += 1
        order.append(vertex)
        for target in adjacency[vertex]:
            if target not in selected_set:
                continue
            inspections += 1
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                enqueues += 1
    if len(order) != len(selected):
        raise Refusal("cycle in affected DAG")
    counters = TraversalCounters(
        vertices=len(selected),
        edges=relevant_edges,
        indegree_initializations=len(selected),
        vertex_enqueues=enqueues,
        vertex_dequeues=len(order),
        edge_inspections=inspections,
        ready_queue_appends=enqueues,
        ready_queue_head_advances=len(order),
        ready_node_comparisons=0,
        logical_storage_slots=7 * len(selected) + 2 * relevant_edges,
    )
    if inspections > relevant_edges or enqueues > len(selected):
        raise AssertionError("FIFO Kahn operation bound defect")
    return TraversalResult(tuple(selected), tuple(order), counters)


def exact_oracle_case(vertices: int, edges: Iterable[tuple[int, int]], sources: Iterable[int]) -> TraversalResult:
    edge_rows, _, _ = canonicalize_edges(edges)
    source_rows = tuple(sources)
    oracle_affected = direct_affected_vertices(vertices, edge_rows, source_rows)
    oracle_order = direct_fifo_order(vertices, edge_rows, oracle_affected)
    optimized = fifo_kahn(vertices, edge_rows, source_rows)
    if optimized.affected != oracle_affected or optimized.order != oracle_order:
        raise Refusal("DAG optimized result disagrees with direct oracle")
    return optimized


def _complete_domain() -> Iterable[tuple[int, list[tuple[int, int]], tuple[int, ...]]]:
    for vertices in range(6):
        possible = [(left, right) for left in range(vertices) for right in range(left + 1, vertices)]
        for edge_mask in range(1 << len(possible)):
            edges = [edge for index, edge in enumerate(possible) if edge_mask & (1 << index)]
            for source_mask in range(1 << vertices):
                sources = tuple(index for index in range(vertices) if source_mask & (1 << index))
                yield vertices, edges, sources


def _family_edges(vertices: int, family: str) -> list[tuple[int, int]]:
    if family == "empty":
        return []
    if family == "complete_acyclic":
        return [(i, j) for i in range(vertices) for j in range(i + 1, vertices)]
    if family == "deep_chain":
        return [(i, i + 1) for i in range(vertices - 1)]
    if family == "wide_out_frontier":
        return [(0, i) for i in range(1, vertices)]
    if family == "wide_in_frontier":
        return [(i, vertices - 1) for i in range(vertices - 1)]
    if family == "disconnected_two_chains":
        midpoint = vertices // 2
        return [(i, i + 1) for i in range(midpoint - 1)] + [(i, i + 1) for i in range(midpoint, vertices - 1)]
    if family == "diamond_ladder":
        return [(i, j) for i in range(vertices) for j in (i + 1, i + 2) if j < vertices]
    if family == "sparse_skip_chain":
        return [(i, i + 1) for i in range(vertices - 1)] + [(i, i + 3) for i in range(vertices - 3)]
    raise Refusal(f"unknown DAG family: {family}")


def _source_sets(vertices: int) -> tuple[tuple[int, ...], ...]:
    return ((), (0,), (vertices - 1,), tuple(range(0, vertices, 2)), tuple(range(vertices)))


def _edge_order(edges: list[tuple[int, int]], mode: int) -> list[tuple[int, int]]:
    if mode == 0:
        return list(edges)
    if mode == 1:
        return list(reversed(edges))
    if mode == 2:
        return edges[::2] + edges[1::2]
    if mode == 3:
        return edges[1::2] + edges[::2]
    raise AssertionError


def agreement_suite() -> dict[str, int]:
    complete = adversarial = hashed = 0
    for vertices, edges, sources in _complete_domain():
        exact_oracle_case(vertices, edges, sources)
        complete += 1
    families = ("empty", "complete_acyclic", "deep_chain", "wide_out_frontier", "wide_in_frontier", "disconnected_two_chains", "diamond_ladder", "sparse_skip_chain")
    for vertices in range(6, 13):
        for family in families:
            edges = _family_edges(vertices, family)
            for sources in _source_sets(vertices):
                for mode in range(4):
                    exact_oracle_case(vertices, _edge_order(edges, mode), sources)
                    adversarial += 1
        possible = [(i, j) for i in range(vertices) for j in range(i + 1, vertices)]
        for seed in range(32):
            edges = [edge for edge in possible if hashlib.sha256(f"EBU-SD-DAG-v1|{vertices}|{seed}|{edge[0]}|{edge[1]}".encode()).digest()[0] % 2 == 0]
            for sources in _source_sets(vertices):
                for mode in range(4):
                    exact_oracle_case(vertices, _edge_order(edges, mode), sources)
                    hashed += 1
    invalid = 0
    for vertices in range(6, 13):
        chain = _family_edges(vertices, "deep_chain")
        for invalid_edges in (chain + [(vertices - 1, 0)], chain + [chain[0]]):
            try:
                exact_oracle_case(vertices, invalid_edges, (0,))
            except Refusal:
                invalid += 1
            else:
                raise Refusal("invalid DAG control was accepted")
    if (complete, adversarial, hashed, invalid) != (33867, 1120, 4480, 14):
        raise AssertionError("DAG agreement-domain arithmetic defect")
    return {"complete_cases": complete, "adversarial_cases": adversarial, "hash_cases": hashed, "valid_cases": complete + adversarial + hashed, "invalid_cases": invalid}


def _complexity_edges(vertices: int, edge_count: int) -> list[tuple[int, int]]:
    if edge_count > vertices * (vertices - 1) // 2:
        raise Refusal("requested complexity graph cannot be acyclic")
    rows: list[tuple[int, int]] = []
    # Deterministic diagonals make a forward sparse/dense DAG without hashing or sampling.
    gap = 1
    while len(rows) < edge_count:
        for source in range(vertices - gap):
            rows.append((source, source + gap))
            if len(rows) == edge_count:
                break
        gap += 1
    rows.sort()
    return rows


def complexity_cell(vertices: int, edges: int, cell_class: str) -> dict[str, int | str]:
    allowed = {(128, 256, "sparse"), (1024, 4096, "sparse"), (10000, 50000, "sparse"), (100000, 500000, "sparse"), (512, 130816, "dense_acyclic")}
    if (vertices, edges, cell_class) not in allowed:
        raise Refusal("DAG complexity cell outside frozen grid")
    discovered_edges = list(reversed(_complexity_edges(vertices, edges)))
    started = time.monotonic_ns()
    edge_rows, canonicalization_comparisons, canonicalization_auxiliary_edge_slots = canonicalize_edges(discovered_edges)
    result = fifo_kahn(vertices, edge_rows, (0,))
    elapsed = time.monotonic_ns() - started
    counters = result.counters
    output = {"affected": list(result.affected), "order": list(result.order)}
    output_bytes = len(canonical_bytes(output))
    if counters.edge_inspections != edges or counters.indegree_initializations != vertices:
        raise Refusal("DAG exact traversal counter mismatch")
    return {
        "vertices": vertices,
        "edges": edges,
        "class": cell_class,
        "elapsed_ns": elapsed,
        "primary_operations": counters.indegree_initializations + counters.edge_inspections,
        "logical_storage_slots": counters.logical_storage_slots,
        "storage_bytes": counters.logical_storage_slots * 8 + canonicalization_auxiliary_edge_slots * 16,
        "output_bytes": output_bytes,
        "peak_process_tree_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * (1024 if sys.platform.startswith("linux") else 1),
        "affected_digest": canonical_digest(list(result.affected)),
        "order_digest": canonical_digest(list(result.order)),
        "indegree_initializations": counters.indegree_initializations,
        "vertex_enqueues": counters.vertex_enqueues,
        "vertex_dequeues": counters.vertex_dequeues,
        "edge_inspections": counters.edge_inspections,
        "ready_queue_appends": counters.ready_queue_appends,
        "ready_queue_head_advances": counters.ready_queue_head_advances,
        "ready_node_comparisons": counters.ready_node_comparisons,
        "canonicalization_input_edge_count": edges,
        "canonicalization_comparisons": canonicalization_comparisons,
        "canonicalization_auxiliary_edge_slots": canonicalization_auxiliary_edge_slots,
    }
