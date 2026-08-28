"""Independently readable reference algorithms for Stage E conformance."""

from __future__ import annotations

from collections.abc import Iterable

from .canonical import Refusal


def direct_affected_vertices(vertices: int, edges: Iterable[tuple[int, int]], sources: Iterable[int]) -> tuple[int, ...]:
    """Enumerate simple paths from each source; suitable only for the small oracle domain."""

    edge_list = list(edges)
    if vertices < 0 or vertices > 12:
        raise Refusal("direct DAG oracle limited to at most 12 vertices")
    adjacency = [[] for _ in range(vertices)]
    seen_edges: set[tuple[int, int]] = set()
    for source, target in edge_list:
        if not (0 <= source < vertices and 0 <= target < vertices):
            raise Refusal("edge endpoint outside graph")
        if (source, target) in seen_edges:
            raise Refusal("duplicate edge")
        seen_edges.add((source, target))
        adjacency[source].append(target)
    for row in adjacency:
        row.sort()
    source_rows = sorted(set(sources))
    if any(source < 0 or source >= vertices for source in source_rows):
        raise Refusal("source outside graph")
    affected = set(source_rows)

    def visit(vertex: int, path: frozenset[int]) -> None:
        for target in adjacency[vertex]:
            if target in path:
                raise Refusal("cycle in direct DAG oracle")
            affected.add(target)
            visit(target, path | {target})

    for source in source_rows:
        visit(source, frozenset({source}))
    return tuple(sorted(affected))


def direct_fifo_order(vertices: int, edges: Iterable[tuple[int, int]], affected: Iterable[int]) -> tuple[int, ...]:
    selected = set(affected)
    adjacency = {vertex: [] for vertex in selected}
    indegree = {vertex: 0 for vertex in selected}
    seen: set[tuple[int, int]] = set()
    for source, target in edges:
        if (source, target) in seen:
            raise Refusal("duplicate edge")
        seen.add((source, target))
        if source in selected and target in selected:
            adjacency[source].append(target)
            indegree[target] += 1
    for row in adjacency.values():
        row.sort()
    queue = sorted(vertex for vertex in selected if indegree[vertex] == 0)
    output: list[int] = []
    head = 0
    while head < len(queue):
        vertex = queue[head]
        head += 1
        output.append(vertex)
        for target in adjacency[vertex]:
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    if len(output) != len(selected):
        raise Refusal("cycle in direct FIFO projection")
    return tuple(output)
