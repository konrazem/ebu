"""I-1-only synthetic factories and forbidden-reachability guards."""

from __future__ import annotations

import ast
import builtins
from contextlib import contextmanager
from pathlib import Path
import sys
from typing import Iterator

from ebu_framework.identity import (
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)
from ebu_framework.registry import (
    NamespaceEntry,
    NamespaceRegistrySnapshot,
    _NamespaceRegistryStore,
    _ObjectRegistryStore,
)


_FORBIDDEN_IMPORT_PREFIXES = (
    "ebu_framework.execution",
    "exp_",
    "experiments_",
    "gate1dc_v30",
    "finalize_v30_gate1dc",
    "energy_balance",
    "ebu_v",
)
_FORBIDDEN_CALL_NAMES = frozenset(
    {
        "advance_epoch",
        "begin_bound_scientific_execution",
        "build_information_view",
        "classify_joint_groups",
        "commit_phase_updates",
        "compute_group_measurement",
        "evaluate_distortion",
        "measure_state",
        "policy_propose",
        "propose_joint_transition",
        "propose_phase_updates",
        "screen_and_admit",
    }
)


def synthetic_ref(object_id: str, fill: str) -> ObjectRef:
    return ObjectRef(
        object_id=ScientificId(object_id),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash("sha256:" + fill * 64),
    )


def synthetic_namespace_store() -> _NamespaceRegistryStore:
    registry_ref = synthetic_ref(
        "ebu:registry:validation:synthetic-ns-v1", "0"
    )
    owner_ref = synthetic_ref(
        "ebu:authority:validation:synthetic-owner", "1"
    )
    policy_ref = synthetic_ref(
        "ebu:allocation-policy:validation:sha256-fullhex-v1", "2"
    )
    entry = NamespaceEntry(
        namespace="synthetic",
        namespace_id=ScientificId("ebu:namespace:core:synthetic"),
        owning_authority_ref=owner_ref,
        allocation_policy_ref=policy_ref,
        reserved=False,
    )
    return _NamespaceRegistryStore(
        NamespaceRegistrySnapshot(registry_ref=registry_ref, entries=(entry,))
    )


def synthetic_object_store() -> _ObjectRegistryStore:
    return _ObjectRegistryStore()


def assert_safe_test_module(path: Path) -> int:
    """Statically prove one inspected I-1 module has no T3/legacy reachability."""

    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))
    checks = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                checks += 1
                if alias.name.startswith(_FORBIDDEN_IMPORT_PREFIXES):
                    raise AssertionError(f"forbidden import {alias.name} in {path}")
        elif isinstance(node, ast.ImportFrom):
            module = ("." * node.level) + (node.module or "")
            checks += 1
            if module.startswith(_FORBIDDEN_IMPORT_PREFIXES):
                raise AssertionError(f"forbidden import {module} in {path}")
        elif isinstance(node, ast.Call):
            name = None
            if isinstance(node.func, ast.Name):
                name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                name = node.func.attr
            checks += 1
            if name in _FORBIDDEN_CALL_NAMES:
                raise AssertionError(f"forbidden T3 call {name} in {path}")
    lowered = source.lower()
    for forbidden_text in (
        "results/v3.0",
        "v30_gate1dc",
        "gate1d_c",
    ):
        checks += 1
        if forbidden_text in lowered:
            raise AssertionError(f"forbidden path token {forbidden_text} in {path}")
    return checks


@contextmanager
def forbidden_import_guard() -> Iterator[None]:
    """Block forbidden imports for the duration of one synthetic check."""

    original_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if level == 0 and name.startswith(_FORBIDDEN_IMPORT_PREFIXES):
            raise AssertionError(f"forbidden process import: {name}")
        return original_import(name, globals, locals, fromlist, level)

    builtins.__import__ = guarded_import
    try:
        yield
    finally:
        builtins.__import__ = original_import
    loaded_forbidden = [
        name for name in sys.modules if name.startswith(_FORBIDDEN_IMPORT_PREFIXES)
    ]
    if loaded_forbidden:
        raise AssertionError(f"forbidden modules loaded: {loaded_forbidden}")


__all__ = (
    "assert_safe_test_module",
    "forbidden_import_guard",
    "synthetic_namespace_store",
    "synthetic_object_store",
    "synthetic_ref",
)
