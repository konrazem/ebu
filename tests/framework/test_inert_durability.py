"""Executable Framework I-5 V7 vectors and source-only V11 vectors."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any
import unittest

from tests.framework.test_event_ownership import (
    _ROOT,
    _VALIDATION,
    _run_dynamic_vector,
    _static_vector,
)


_V7_V11 = tuple(
    vector for vector in _VALIDATION["vectors"] if vector["group"] in {"V7", "V11"}
)
assert sum(vector["group"] == "V7" for vector in _V7_V11) == 63
assert sum(vector["group"] == "V11" for vector in _V7_V11) == 29
assert len(_V7_V11) == 92


def _validation_trees() -> tuple[tuple[Path, str, ast.Module], ...]:
    paths = (
        _ROOT / "tests" / "framework" / "test_event_ownership.py",
        _ROOT / "tests" / "framework" / "test_inert_durability.py",
    )
    rows = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec", dont_inherit=True)
        rows.append((path, source, tree))
    return tuple(rows)


def _call_names(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if isinstance(function, ast.Name):
            names.append(function.id)
        elif isinstance(function, ast.Attribute):
            names.append(function.attr)
    return tuple(names)


def _import_names(tree: ast.AST) -> tuple[str, ...]:
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            names.append(node.module or "")
            assert all(
                alias.name != "*" and alias.asname is None
                for alias in node.names
            )
    return tuple(names)


def _run_reachability(vector: dict[str, Any]) -> None:
    owner = vector["interface"].rsplit(".", 1)[-1]
    trees = _validation_trees()
    calls = tuple(name for _, _, tree in trees for name in _call_names(tree))
    imports = tuple(name for _, _, tree in trees for name in _import_names(tree))
    if owner == "VALIDATION_NO_EXECUTION_IMPORT":
        assert all(name != "ebu_framework.execution" for name in imports)
    elif owner == "NO_T3_ENTRY_CALL":
        assert not {
            "begin_bound_scientific_execution",
            "validate_t3_entry_guard",
        } & set(calls)
    elif owner == "NO_LEASE_CONSTRUCTION":
        assert not {"ScientificExecutionLease", "T3EntryGuard"} & set(calls)
    elif owner == "NO_HISTORICAL_RUNNER":
        forbidden = ("runner", "simulation", "trajectory", "finalizer", "gate")
        assert all(
            not any(word in name.casefold() for word in forbidden)
            for name in imports
        )
    elif owner == "NO_DYNAMIC_IMPORT":
        assert "importlib" not in imports
        assert not {"__import__", "eval", "exec"} & set(calls)
    elif owner == "NO_NETWORK":
        assert not {"socket", "http", "urllib", "requests"} & {
            name.split(".", 1)[0] for name in imports
        }
    elif owner == "NO_SUBPROCESS":
        assert "subprocess" not in imports and "system" not in calls
    elif owner == "NO_ENTROPY":
        assert not {"random", "secrets", "uuid", "time"} & {
            name.split(".", 1)[0] for name in imports
        }
        assert not {"uuid4", "getpid", "getppid"} & set(calls)
    elif owner == "NO_PRODUCTION_BOOTSTRAP":
        assert not {"bootstrap", "load_provider", "provider_loader"} & set(calls)
    elif owner == "NO_PUBLICATION_RECOVERY":
        assert not {
            "publish",
            "recover",
            "correct",
            "finalize_result",
        } & set(calls)
    elif owner == "NO_MODEL_STEP":
        assert not {"step", "advance", "transition"} & set(calls)
    elif owner == "NO_FAULT_DELIVERY":
        assert not {"deliver_fault", "execute_fault_schedule"} & set(calls)
    else:
        raise AssertionError(f"unknown static reachability owner {owner}")


class FrameworkI5V7V11Tests(unittest.TestCase):
    """One exact unittest invocation for every accepted V7/V11 vector."""


def _install_v7_v11_test(vector: dict[str, Any]) -> None:
    def test(self: FrameworkI5V7V11Tests) -> None:
        if vector["group"] == "V7":
            _run_dynamic_vector(vector)
        elif vector["kind"] == "STATIC_REACHABILITY":
            _run_reachability(vector)
        else:
            _static_vector(vector)
        expected = vector["expected"]
        for counter in (
            "model_step_count",
            "policy_call_count",
            "scientific_callback_count",
            "real_store_call_count",
            "fault_delivery_count",
            "t3_entry_count",
            "input_mutation_count",
        ):
            self.assertEqual(expected[counter], 0)

    test.__name__ = f"test_{vector['vector_id'].replace('-', '_')}"
    setattr(FrameworkI5V7V11Tests, test.__name__, test)


for _vector in _V7_V11:
    _install_v7_v11_test(_vector)
