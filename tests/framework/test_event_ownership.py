"""Executable Framework I-5 V6 vectors and shared closed materializer."""

from __future__ import annotations

import ast
from copy import deepcopy
import json
from pathlib import Path
from typing import Any
import unittest

from ebu_framework import durability, events, faults, hashing, ownership, traces
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.identity import (
    CanonicalScientificTracePayloadHash,
    CanonicalTracePrefixHash,
    CanonicalTraceRowHash,
    ExecutionSemanticsHash,
    ObjectContentHash,
    ObjectRef,
    PolicyMemoryPayloadHash,
    ScientificId,
    SemanticVersion,
    StatePayloadHash,
)


_ROOT = Path(__file__).resolve().parents[2]
_VALIDATION_PATH = (
    _ROOT / "unified_python_research_framework_i5_validation_contract.json"
)
_MECHANICAL_PATH = _ROOT / "unified_python_research_framework_i5_contract.json"
_VALIDATION = json.loads(_VALIDATION_PATH.read_text(encoding="utf-8"))
_MATERIAL = _VALIDATION["materialization_contract"]


_VECTORS = tuple(_VALIDATION["vectors"])
_DYNAMIC_VECTORS = tuple(
    vector
    for vector in _VECTORS
    if vector["exercise_class"] != "STATIC_SOURCE_ASSERTION"
)
_CLOSED_INVOCATIONS = tuple(
    (
        vector["materialization"].get("baseline_call"),
        patch["value"],
    )
    for vector in _DYNAMIC_VECTORS
    for patch in vector["materialization"].get("patches", [])
    if patch["op"] == "apply_closed_variant"
)
_CLOSED_COORDINATES = {
    (owner, operand)
    for owner, variants in _MATERIAL["closed_variant_catalogue"].items()
    for operand in variants
}
assert len(_VECTORS) == 140
assert len(_DYNAMIC_VECTORS) == 111
assert len(_CLOSED_INVOCATIONS) == 60
assert len(_CLOSED_COORDINATES) == 39
assert set(_CLOSED_INVOCATIONS) == _CLOSED_COORDINATES
assert sum(
    vector["expected"]["completed_check_count"] for vector in _VECTORS
) == 253
assert sum(
    len(vector["expected"]["active_predicates"]) for vector in _VECTORS
) == 116
assert sum(
    vector["expected"]["failure_id"] != "NOT_APPLICABLE"
    for vector in _VECTORS
) == 104


_MODULES = {
    "durability": durability,
    "events": events,
    "faults": faults,
    "hashing": hashing,
    "ownership": ownership,
    "traces": traces,
}
_CLASSES = {
    f"ebu_framework.{module_name}.{name}": getattr(module, name)
    for module_name, module in _MODULES.items()
    for name in module.__all__
    if hasattr(module, name)
}
_ENUMS = {
    "Applicability": Applicability,
    "FailureCode": FailureCode,
    "PhaseOrdinal": events.PhaseOrdinal,
    "TraceCompleteness": events.TraceCompleteness,
    "OwnershipKind": ownership.OwnershipKind,
    "CommitOutcome": durability.CommitOutcome,
    "TraceRowKind": traces.TraceRowKind,
    "TraceValidationStatus": traces.TraceValidationStatus,
}
_DIGESTS = {
    "CanonicalScientificTracePayloadHash": CanonicalScientificTracePayloadHash,
    "CanonicalTracePrefixHash": CanonicalTracePrefixHash,
    "CanonicalTraceRowHash": CanonicalTraceRowHash,
    "DurabilityEvidenceDigest": hashing.DurabilityEvidenceDigest,
    "EventDeclarationDigest": hashing.EventDeclarationDigest,
    "EventKeyDigest": hashing.EventKeyDigest,
    "ExecutionSemanticsHash": ExecutionSemanticsHash,
    "ObjectContentHash": ObjectContentHash,
    "OwnershipDigest": hashing.OwnershipDigest,
    "PhaseCommitDigest": hashing.PhaseCommitDigest,
    "PolicyMemoryPayloadHash": PolicyMemoryPayloadHash,
    "RunEnvelopeDigest": hashing.RunEnvelopeDigest,
    "Sha256Digest": ObjectContentHash,
    "StatePayloadHash": StatePayloadHash,
    "TraceDigest": CanonicalTraceRowHash,
}


def _object_ref(spec: dict[str, Any]) -> ObjectRef:
    return ObjectRef(
        object_id=ScientificId(spec["object_id"]),
        object_version=SemanticVersion(spec["object_version"]),
        object_content_hash=ObjectContentHash(spec["object_content_hash"]),
    )


def _enum(expression: str) -> object:
    class_name, member_name = expression.split(".", 1)
    return _ENUMS[class_name].__members__[member_name]


def _digest(name: str, value: str) -> object:
    return _DIGESTS[name](value=value) if name in {
        "DurabilityEvidenceDigest",
        "EventDeclarationDigest",
        "EventKeyDigest",
        "OwnershipDigest",
        "PhaseCommitDigest",
        "RunEnvelopeDigest",
    } else _DIGESTS[name](value)


def _expand(value: object) -> object:
    if type(value) is list:
        return [_expand(item) for item in value]
    if type(value) is not dict:
        return value
    if "$record" in value:
        name = value["$record"]
        if name == "TraceDigest":
            return CanonicalTraceRowHash(_MATERIAL["atoms"]["sha_a"])
        spec = deepcopy(_MATERIAL["record_catalogue"][name])
        expanded = _expand(spec)
        if "$variant" in value:
            expanded["_variant"] = value["$variant"]
        return expanded
    if "$atom" in value:
        atom = _MATERIAL["atoms"][value["$atom"]]
        if type(atom) is dict and atom.get("$construct") == "ObjectRef":
            return _object_ref(atom["kwargs"])
        return _expand(atom)
    if "$enum" in value:
        return _enum(value["$enum"])
    if "$digest_type" in value:
        return _digest(value["$digest_type"], value["value"])
    if "$bytes_hex" in value:
        return bytes.fromhex(value["$bytes_hex"])
    if "$construct" in value:
        if value["$construct"] == "ObjectRef":
            return _object_ref(value["kwargs"])
        raise AssertionError(f"unsupported atom constructor {value['$construct']}")
    return {key: _expand(item) for key, item in value.items()}


def _parts(pointer: str) -> list[str]:
    if pointer in {"", "/"}:
        return []
    return [
        part.replace("~1", "/").replace("~0", "~")
        for part in pointer[1:].split("/")
    ]


def _get(root: object, pointer: str) -> object:
    current = root
    for part in _parts(pointer):
        current = current[int(part)] if type(current) is list else current[part]
    return current


def _set(root: object, pointer: str, value: object) -> None:
    parts = _parts(pointer)
    parent = _get(root, "/" + "/".join(parts[:-1])) if len(parts) > 1 else root
    key = parts[-1]
    if type(parent) is list:
        parent[int(key)] = value
    else:
        parent[key] = value


def _remove(root: object, pointer: str) -> None:
    parts = _parts(pointer)
    parent = _get(root, "/" + "/".join(parts[:-1])) if len(parts) > 1 else root
    key = parts[-1]
    if type(parent) is list:
        del parent[int(key)]
    else:
        del parent[key]


def _support(
    name: str, *, baseline: object, current: object
) -> object:
    spec = _MATERIAL["closed_variant_support_catalogue"][name]
    base = _resolve_value(
        spec["base"], baseline=baseline, current=current, local=None
    )
    local = deepcopy(base)
    _apply_operations(
        local,
        spec.get("operations", []),
        baseline=baseline,
        current=current,
        local=local,
    )
    return local


def _resolve_value(
    value: object,
    *,
    baseline: object,
    current: object,
    local: object | None,
) -> object:
    if type(value) is dict:
        if "$baseline_copy" in value:
            return deepcopy(_get(baseline, value["$baseline_copy"]))
        if "$current_copy" in value:
            return deepcopy(_get(current, value["$current_copy"]))
        if "$enclosing_copy" in value:
            return deepcopy(_get(current, value["$enclosing_copy"]))
        if "$support" in value:
            return _support(value["$support"], baseline=baseline, current=current)
        if "$support_copy" in value:
            row = value["$support_copy"]
            support = _support(row["support"], baseline=baseline, current=current)
            return deepcopy(_get(support, row["path"]))
    return _expand(value)


def _apply_operations(
    root: object,
    operations: list[dict[str, Any]],
    *,
    baseline: object,
    current: object,
    local: object | None,
) -> None:
    for operation in operations:
        op = operation["op"]
        if op == "replace":
            _set(
                root,
                operation["path"],
                _resolve_value(
                    operation["value"],
                    baseline=baseline,
                    current=current,
                    local=local,
                ),
            )
        elif op == "replace_tuple":
            _set(
                root,
                operation["path"],
                [
                    _resolve_value(
                        item,
                        baseline=baseline,
                        current=current,
                        local=local,
                    )
                    for item in operation["items"]
                ],
            )
        elif op == "append_current_copy":
            _get(root, operation["list_path"]).append(
                deepcopy(_get(root, operation["source_path"]))
            )
        elif op in {"append_support", "prepend_support"}:
            sequence = _get(root, operation["list_path"])
            support = _support(
                operation["support"], baseline=baseline, current=current
            )
            if op == "append_support":
                sequence.append(support)
            else:
                sequence.insert(0, support)
        elif op == "relink_event_predecessor_chain":
            sequence = _get(root, operation["path"])
            for index in range(1, len(sequence)):
                predecessor = _get(
                    sequence[index - 1], operation["source_relative"]
                )
                _set(
                    sequence[index],
                    operation["target_relative"],
                    deepcopy(predecessor),
                )
        elif op == "remove":
            _remove(root, operation["path"])
        elif op == "replace_by_constructor":
            node = _get(root, operation["path"])
            case = operation["cases"].get(node.get("constructor"))
            assert case is not None
            _apply_operations(
                node,
                case["operations"],
                baseline=baseline,
                current=current,
                local=node,
            )
        else:
            raise AssertionError(f"unsupported closed operation {op}")


def _construct(value: object) -> object:
    if type(value) is list:
        return tuple(_construct(item) for item in value)
    if type(value) is not dict or "constructor" not in value:
        if type(value) is dict:
            return {key: _construct(item) for key, item in value.items()}
        return value
    constructor_name = value["constructor"]
    constructor = _CLASSES[constructor_name]
    positional = tuple(_construct(item) for item in value.get("positional", []))
    kwargs = {
        key: _construct(item) for key, item in value.get("kwargs", {}).items()
    }
    return constructor(*positional, **kwargs)


def _walk_records(value: object):
    if type(value) is dict:
        if "constructor" in value:
            yield value
        for child in value.values():
            yield from _walk_records(child)
    elif type(value) is list:
        for child in value:
            yield from _walk_records(child)


def _correlate_records(root: object) -> None:
    records = list(_walk_records(root))
    for node in reversed(records):
        constructor = node.get("constructor")
        if constructor == "ebu_framework.traces.TraceRowFrame":
            source = _construct(node["materializer_source"])
            frame = traces.frame_trace_row(source)
            node["kwargs"]["row_digest"] = frame.row_digest
            node["kwargs"]["frame_bytes"] = frame.frame_bytes
        elif constructor == "ebu_framework.traces.CanonicalTracePrefix":
            frames = _construct(node["kwargs"]["row_frames"])
            prefix = traces.build_trace_prefix(frames)
            node["kwargs"]["row_count"] = prefix.row_count
            node["kwargs"]["prefix_digest"] = prefix.prefix_digest
        elif constructor == "ebu_framework.durability.PhysicalPhaseTransaction":
            phase = node["kwargs"]["phase_commit"]
            node["kwargs"]["trace_row_digest"] = deepcopy(
                phase["kwargs"]["trace_row_digest"]
            )


def _phase_digest(phase_node: dict[str, Any]) -> hashing.PhaseCommitDigest:
    phase = _construct(phase_node)
    predecessor = phase.previous_phase_commit_digest
    projection = [
        str(phase.epoch),
        str(phase.phase_ordinal.value),
        str(predecessor)
        if type(predecessor) is hashing.PhaseCommitDigest
        else Applicability.NOT_APPLICABLE.value,
        str(len(phase.ordered_event_digests)),
        ",".join(str(item) for item in phase.ordered_event_digests),
        str(phase.epoch_ownership_digest),
        str(phase.trace_row_digest),
    ]
    return hashing.compute_phase_commit_digest(projection)


def _evidence_digest(node: dict[str, Any]) -> hashing.DurabilityEvidenceDigest:
    evidence = _construct(node)
    phase = evidence.phase_commit_digest
    return hashing.compute_durability_evidence_digest(
        [
            str(evidence.request_ref.object_id),
            str(evidence.committed_prefix),
            str(phase)
            if type(phase) is hashing.PhaseCommitDigest
            else Applicability.NOT_APPLICABLE.value,
        ]
    )


def _resolve_variants(root: object) -> None:
    for node in list(_walk_records(root)):
        variant_name = node.pop("_variant", None)
        if variant_name is None:
            continue
        variant = _MATERIAL["variant_catalogue"][variant_name]
        _apply_operations(
            node,
            variant["operations"],
            baseline=root,
            current=root,
            local=node,
        )


def _baseline_call(name: str) -> dict[str, Any]:
    root = _expand(deepcopy(_MATERIAL["call_catalogue"][name]))
    _resolve_variants(root)
    _correlate_records(root)
    if name == "traces.extend_trace_prefix":
        prefix_frame = root["positional"][0]["kwargs"]["row_frames"][0]
        appended_frame = root["positional"][1][0]
        appended_frame["materializer_source"]["kwargs"][
            "predecessor_row_digest"
        ] = deepcopy(prefix_frame["kwargs"]["row_digest"])
        source = _construct(appended_frame["materializer_source"])
        correlated = traces.frame_trace_row(source)
        appended_frame["kwargs"]["row_digest"] = correlated.row_digest
        appended_frame["kwargs"]["frame_bytes"] = correlated.frame_bytes
    elif name == "durability.validate_atomic_commit_outcome":
        request = root["positional"][0]
        evidence = root["positional"][1]
        evidence["kwargs"]["request_ref"] = deepcopy(
            request["kwargs"]["request_ref"]
        )
        evidence["kwargs"]["committed_prefix"] = deepcopy(
            request["kwargs"]["expected_trace_prefix"]
        )
        physical = request["kwargs"]["physical_phase_transaction"]
        evidence["kwargs"]["phase_commit_digest"] = _phase_digest(
            physical["kwargs"]["phase_commit"]
        )
        evidence["kwargs"]["evidence_digest"] = _evidence_digest(evidence)
    elif name == "traces.validate_complete_trace_evidence":
        prefix = root["positional"][0]
        evidence = root["positional"][1]
        evidence["kwargs"]["trace_digest"] = deepcopy(
            prefix["kwargs"]["prefix_digest"]
        )
        evidence["kwargs"]["last_prefix_digest"] = deepcopy(
            prefix["kwargs"]["prefix_digest"]
        )
        evidence["kwargs"]["confirmed_row_count"] = prefix["kwargs"][
            "row_count"
        ]
    return root


def _recompute(root: object, rows: list[dict[str, Any]]) -> None:
    for row in sorted(rows, key=lambda item: item["order"]):
        parent_pointer = row["target"].rsplit("/", 1)[0]
        parent = _get(root, parent_pointer)
        expected_constructor = row.get("when_constructor")
        if expected_constructor is not None:
            record_pointer = parent_pointer.rsplit("/kwargs", 1)[0]
            record = _get(root, record_pointer)
            if record.get("constructor") != expected_constructor:
                continue
        target_node = _get(root, row["target"])
        callable_name = row["callable"]
        if callable_name.endswith("compute_canonical_trace_row_hash"):
            source = _construct(_get(root, row["dependencies"][0]))
            replacement = traces.frame_trace_row(source).row_digest
        elif callable_name.endswith("frame_trace_row"):
            source = _construct(_get(root, row["dependencies"][0]))
            replacement = traces.frame_trace_row(source).frame_bytes
        elif callable_name.endswith("compute_canonical_trace_prefix_hash"):
            frames = _construct(_get(root, row["dependencies"][0]))
            replacement = traces.build_trace_prefix(frames).prefix_digest
        elif callable_name.endswith("compute_durability_evidence_digest"):
            record_pointer = parent_pointer.rsplit("/kwargs", 1)[0]
            replacement = _evidence_digest(_get(root, record_pointer))
        elif callable_name == "copy_exact":
            replacement = deepcopy(_get(root, row["dependencies"][0]))
        else:
            raise AssertionError(f"unsupported recomputation {callable_name}")
        assert target_node is not None
        _set(root, row["target"], replacement)


def _materialize_dynamic(
    vector: dict[str, Any],
) -> tuple[object, tuple[Any, ...], dict[str, Any]]:
    materialization = vector["materialization"]
    if vector["exercise_class"] == "EXACT_CONSTRUCTOR_INVOKED":
        name = materialization["record_catalogue"]
        node = _expand(deepcopy(_MATERIAL["record_catalogue"][name]))
        baseline = deepcopy(node)
        _apply_operations(
            node,
            materialization["patches"],
            baseline=baseline,
            current=node,
            local=node,
        )
        constructor = _CLASSES[node["constructor"]]
        args = tuple(_construct(item) for item in node.get("positional", []))
        kwargs = {
            key: _construct(item) for key, item in node.get("kwargs", {}).items()
        }
        return constructor, args, kwargs
    baseline_name = materialization["baseline_call"]
    node = _baseline_call(baseline_name)
    immutable_baseline = deepcopy(node)
    for patch in materialization["patches"]:
        assert patch["op"] == "apply_closed_variant" and patch["path"] == "/"
        variant = _MATERIAL["closed_variant_catalogue"][baseline_name][patch["value"]]
        _apply_operations(
            node,
            variant["operations"],
            baseline=immutable_baseline,
            current=node,
            local=node,
        )
        _recompute(node, variant.get("recompute", []))
    module_name, callable_name = baseline_name.split(".", 1)
    owner = getattr(_MODULES[module_name], callable_name)
    args = tuple(_construct(item) for item in node.get("positional", []))
    kwargs = {
        key: _construct(item) for key, item in node.get("kwargs", {}).items()
    }
    return owner, args, kwargs


def _failure_projection(error: FrameworkError) -> dict[str, Any]:
    return error.envelope.to_ecj1()


def _run_dynamic_vector(vector: dict[str, Any]) -> None:
    owner, args, kwargs = _materialize_dynamic(vector)
    before = repr((args, kwargs))
    expected = vector["expected"]
    if expected["outcome"] == "SUCCESS":
        owner(*args, **kwargs)
    else:
        caught: FrameworkError | None = None
        try:
            owner(*args, **kwargs)
        except FrameworkError as error:
            caught = error
        assert caught is not None
        projection = _failure_projection(caught)
        assert projection["failure_code"] == expected["failure_code"]
        assert projection["failure_id"]["value"] == expected["failure_id"]
        assert projection["failure_ordinal"] == expected["failure_ordinal"]
    assert repr((args, kwargs)) == before
    for counter in (
        "model_step_count",
        "policy_call_count",
        "scientific_callback_count",
        "real_store_call_count",
        "fault_delivery_count",
        "t3_entry_count",
        "input_mutation_count",
    ):
        assert expected[counter] == 0
    assert expected["completed_check_count"] >= 1
    assert len(expected["active_predicates"]) == len(
        set(expected["active_predicates"])
    )


def _static_vector(vector: dict[str, Any]) -> None:
    interface = vector["interface"]
    module_name = interface.split(".")[1]
    source_path = _ROOT / "src" / "ebu_framework" / f"{module_name}.py"
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(source_path))
    compile(tree, str(source_path), "exec", dont_inherit=True)
    declaration_name = interface.rsplit(".", 1)[-1]
    expected_code = vector["expected"]["failure_code"]
    materialization = vector["materialization"]
    if "source_assertion" in materialization:
        functions = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
        }
        pending = [declaration_name]
        reachable: list[ast.FunctionDef] = []
        while pending:
            name = pending.pop()
            if name not in functions or functions[name] in reachable:
                continue
            owner = functions[name]
            reachable.append(owner)
            pending.extend(
                node.func.id
                for node in ast.walk(owner)
                if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id in functions
            )
        owner_source = "\n".join(
            ast.get_source_segment(source, owner) or "" for owner in reachable
        )
        assert expected_code in owner_source
        prohibited_calls = {
            "callback",
            "commit",
            "step",
            "system",
            "urlopen",
        }
        calls = {
            node.func.attr
            if isinstance(node.func, ast.Attribute)
            else node.func.id
            for owner in reachable
            for node in ast.walk(owner)
            if isinstance(node, ast.Call)
            and isinstance(node.func, (ast.Attribute, ast.Name))
        }
        assert not prohibited_calls & calls
        return
    record_name = materialization["record_catalogue"]
    aliases = {
        node.target.id: node
        for node in tree.body
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name)
    }
    classes = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    if record_name in {"TraceDigest", "AtomicCommitOutcome"}:
        assert record_name in aliases
        assert ast.unparse(aliases[record_name].annotation) == "TypeAlias"
        return
    declaration = classes[record_name]
    if record_name in {"AtomicStore", "PolicyDecisionStore", "PhaseCommitStore"}:
        assert any(ast.unparse(base) == "Protocol" for base in declaration.bases)
        assert any(
            ast.unparse(decorator) == "runtime_checkable"
            for decorator in declaration.decorator_list
        )
        return
    if record_name == "ScreeningDisposition":
        assert any(ast.unparse(base) == "StrEnum" for base in declaration.bases)
        assert any(
            keyword.arg == "metaclass"
            and ast.unparse(keyword.value) == "_I5EnumType"
            for keyword in declaration.keywords
        )
        return
    assert any(
        ast.unparse(decorator) == "_strict_formation"
        for decorator in declaration.decorator_list
    )
    removed_field = materialization["patches"][0]["path"].rsplit("/", 1)[-1]
    assert any(
        isinstance(node, ast.AnnAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == removed_field
        for node in declaration.body
    )


_V6 = tuple(vector for vector in _VALIDATION["vectors"] if vector["group"] == "V6")
assert len(_V6) == 48


class FrameworkI5V6Tests(unittest.TestCase):
    """One exact unittest invocation for every accepted V6 vector."""


def _install_v6_test(vector: dict[str, Any]) -> None:
    def test(self: FrameworkI5V6Tests) -> None:
        self.assertNotEqual(
            vector["exercise_class"], "STATIC_SOURCE_ASSERTION"
        )
        _run_dynamic_vector(vector)

    test.__name__ = f"test_{vector['vector_id'].replace('-', '_')}"
    setattr(FrameworkI5V6Tests, test.__name__, test)


for _vector in _V6:
    _install_v6_test(_vector)
