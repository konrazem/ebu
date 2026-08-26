from __future__ import annotations

import ast
import copy
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src" / "ebu_framework"
AUTHORITY_FILES = (
    "unified_python_research_framework_i9_contract.json",
    "unified_python_research_framework_i9_validation_contract.json",
    "unified_python_research_framework_i9_predecessor_manifest.json",
    "unified_python_research_framework_i9_implementation_path_manifest.json",
)
AUTHORITY_RAW_SHA256 = {
    "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I9_AUTHORITY_AMENDMENT.md": (
        "11c48ec99e2d8238f455487139b87e1f7e170ec594f3f2f98bb0aebe7c59e2e4"
    ),
    "unified_python_research_framework_i9_contract.json": (
        "29b6b715f4fdc64ddc60a5323e103d664021927f951cf8edbde2ac93f6c50406"
    ),
    "unified_python_research_framework_i9_validation_contract.json": (
        "64097d37828ce46af80bece7a394f43e82ab1be2840f55917307267b0e8579c4"
    ),
    "unified_python_research_framework_i9_predecessor_manifest.json": (
        "012d3c64003833acbb72e4e9151bddc2f953a1d402e07a195293f8a736ecc06c"
    ),
    "unified_python_research_framework_i9_implementation_path_manifest.json": (
        "7a339f851e09a3e79755fabd143c9a2ce1efa6f52a9c85aa12f5f7f29b2f2f8b"
    ),
}
IMPLEMENTATION_PATHS = (
    ".github/workflows/tests.yml",
    "src/ebu_framework/validation.py",
    "tests/framework/safety.py",
    "tests/framework/test_validation_reachability.py",
)
PRIVATE_NAMES = (
    "_validate_group_descriptor",
    "_validate_source_locks",
    "_validate_implementation_surface",
    "_validate_forbidden_reachability",
    "_validate_group_evidence",
    "_validate_audit_mapping",
    "_authorize_t2_fixture",
)
CONSTANT_NAMES = (
    "_VALIDATION_GROUPS",
    "_I9_IMPLEMENTATION_PATHS",
    "_I9_ROOT_EXPORTS",
    "_I9_FAILURE_CODES",
    "_I9_PUBLIC_SIGNATURES",
    "_I9_DIRECT_IMPORTS",
    "_I9_T2_ALLOWLIST",
    "_I9_AUDIT_REGISTER",
)
T0_PATHS = (
    "tests/framework/test_ecj1.py",
    "tests/framework/test_hash_preimages.py",
    "tests/framework/test_identity_registry.py",
    "tests/framework/test_numeric.py",
    "tests/framework/test_primitives_envelopes.py",
    "tests/framework/test_i3_integration.py",
    "tests/framework/test_i3a_declarations.py",
    "tests/framework/test_i3b_declarations.py",
    "tests/framework/test_i3c_declarations.py",
    "tests/framework/test_i3d_declarations.py",
    "tests/framework/test_atomic_declarations.py",
    "tests/framework/test_interaction_declarations.py",
    "tests/framework/test_event_ownership.py",
    "tests/framework/test_route_guards.py",
    "tests/framework/test_validation_reachability.py",
)
T1_PATHS = (
    "tests/framework/test_authorization.py",
    "tests/framework/test_authorization_use.py",
    "tests/framework/test_capabilities.py",
    "tests/framework/test_event_ownership.py",
    "tests/framework/test_inert_durability.py",
    "tests/framework/test_artifact_recovery_publication.py",
)
T2_PATHS = (
    "tests/framework/test_bridge_exact_fixtures.py",
    "tests/framework/test_dynamic_static_identities.py",
)


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical_json_lf(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _independent_canonical_json_lf(value: object) -> bytes:
    if value is None:
        encoded = "null"
    elif value is True:
        encoded = "true"
    elif value is False:
        encoded = "false"
    elif type(value) is int:
        encoded = str(value)
    elif type(value) is str:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    elif type(value) is list:
        encoded = "[" + ",".join(
            _independent_canonical_json_lf(item).decode("utf-8")[:-1]
            for item in value
        ) + "]"
    elif type(value) is dict:
        encoded = "{" + ",".join(
            json.dumps(key, ensure_ascii=False)
            + ":"
            + _independent_canonical_json_lf(value[key]).decode("utf-8")[:-1]
            for key in sorted(value)
        ) + "}"
    else:
        raise TypeError(f"unsupported authority JSON value: {type(value).__name__}")
    return (encoded + "\n").encode("utf-8")


def _strict_json(path: Path) -> tuple[object, bytes]:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf") or not raw.endswith(b"\n") or b"\r" in raw:
        raise AssertionError(f"invalid authority JSON text encoding: {path}")

    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_float(value):
        raise ValueError(f"floating JSON number: {value}")

    def reject_constant(value):
        raise ValueError(f"non-finite JSON number: {value}")

    document = json.loads(
        raw.decode("utf-8", "strict"),
        object_pairs_hook=unique_pairs,
        parse_float=reject_float,
        parse_constant=reject_constant,
    )
    if type(document) is not dict:
        raise AssertionError(f"authority JSON top level is not an object: {path}")
    if _canonical_json_lf(document) != raw:
        raise AssertionError(f"authority JSON is not canonical: {path}")
    if _independent_canonical_json_lf(document) != raw:
        raise AssertionError(f"independent authority encoding differs: {path}")
    return document, raw


def _literal_assignments(tree: ast.Module) -> dict[str, object]:
    assignments = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            try:
                assignments[node.targets[0].id] = ast.literal_eval(node.value)
            except (TypeError, ValueError):
                continue
    return assignments


def _signature(node: ast.FunctionDef) -> str:
    def argument(value: ast.arg) -> str:
        result = value.arg
        if value.annotation is not None:
            result += ": " + ast.unparse(value.annotation)
        return result

    parts = []
    positional = node.args.posonlyargs + node.args.args
    defaults = [None] * (len(positional) - len(node.args.defaults)) + list(
        node.args.defaults
    )
    for index, (value, default) in enumerate(zip(positional, defaults)):
        rendered = argument(value)
        if default is not None:
            rendered += "=" + ast.unparse(default)
        parts.append(rendered)
        if node.args.posonlyargs and index + 1 == len(node.args.posonlyargs):
            parts.append("/")
    if node.args.vararg is not None:
        parts.append("*" + argument(node.args.vararg))
    elif node.args.kwonlyargs:
        parts.append("*")
    for value, default in zip(node.args.kwonlyargs, node.args.kw_defaults):
        rendered = argument(value)
        if default is not None:
            rendered += "=" + ast.unparse(default)
        parts.append(rendered)
    if node.args.kwarg is not None:
        parts.append("**" + argument(node.args.kwarg))
    result = "(" + ", ".join(parts) + ")"
    if node.returns is not None:
        result += " -> " + ast.unparse(node.returns)
    return result


def _module_exports(tree: ast.Module) -> tuple[str, ...]:
    exports: tuple[str, ...] = ()
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "__all__"
        ):
            exports = ast.literal_eval(node.value)
        elif (
            isinstance(node, ast.AugAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
            and isinstance(node.op, ast.Add)
        ):
            exports += ast.literal_eval(node.value)
    return exports


def _direct_imports(tree: ast.Module, package_modules: tuple[str, ...]) -> tuple[str, ...]:
    result = []
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom) or node.level != 1:
            continue
        names = (
            (node.module.split(".", 1)[0],)
            if node.module is not None
            else tuple(alias.name.split(".", 1)[0] for alias in node.names)
        )
        for name in names:
            if name in package_modules and name not in result:
                result.append(name)
    return tuple(result)


def _base_candidate_bytes(path: str) -> bytes:
    raw = (ROOT / path).read_bytes()
    if path == "tests/framework/safety.py":
        prefix, separator, _ = raw.partition(b"\n\n_I9_FORBIDDEN_T3_INTERFACES = (")
        if not separator:
            raise AssertionError("I-9 safety append marker is absent")
        return prefix
    if path == ".github/workflows/tests.yml":
        prefix, separator, _ = raw.partition(b"\n\n  framework-t0:\n")
        if not separator:
            raise AssertionError("I-9 workflow append marker is absent")
        restored = (prefix + b"\n").replace(b"  workflow_dispatch:\n", b"", 1)
        if b"workflow_dispatch" in restored:
            raise AssertionError("workflow dispatch restoration was ambiguous")
        return restored
    return raw


def _blob_id(raw: bytes) -> str:
    framed = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    return hashlib.sha1(framed).hexdigest()


def _assert_projection(value: object, identity: dict[str, object]) -> None:
    encoded = _canonical_json_lf(value)
    if len(encoded) != identity["byte_count"]:
        raise AssertionError("canonical projection byte count differs")
    if _sha256(encoded) != identity["sha256"]:
        raise AssertionError("canonical projection hash differs")


def _table_rows(path: Path) -> tuple[tuple[str, ...], ...]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = tuple(cell.strip() for cell in stripped[1:-1].split("|"))
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return tuple(rows)


def _assert_ordered_table_rows(path: Path, expected: list[list[str]]) -> None:
    actual = _table_rows(path)
    cursor = 0
    for row in expected:
        wanted = tuple(row)
        while cursor < len(actual) and actual[cursor] != wanted:
            cursor += 1
        if cursor == len(actual):
            raise AssertionError(f"authority table row is absent from {path.name}: {wanted[0]}")
        cursor += 1


def _apply_mutations(baseline: dict[str, object], mutations: list[dict[str, object]]):
    materialized = copy.deepcopy(baseline)
    for mutation in mutations:
        operation = mutation["op"]
        path = mutation["path"]
        if type(path) is not list or not path:
            raise AssertionError("mutation path is not a nonempty JSON array")
        if operation == "APPEND":
            target = materialized
            for component in path:
                target = target[component]
            if type(target) is not list:
                raise AssertionError("APPEND target is not an exact list")
            target.append(copy.deepcopy(mutation["value"]))
            continue
        parent = materialized
        for component in path[:-1]:
            parent = parent[component]
        leaf = path[-1]
        if operation == "REPLACE":
            parent[leaf] = copy.deepcopy(mutation["value"])
        elif operation == "DELETE":
            del parent[leaf]
        else:
            raise AssertionError(f"unknown mutation operation: {operation}")
    return materialized


def _recursive_tuple(value: object) -> object:
    if type(value) is list:
        return tuple(_recursive_tuple(item) for item in value)
    return value


def _derive_i9_failure_id(code: str, owner: str, ordinal: int) -> str:
    def frame(value: str) -> bytes:
        encoded = value.encode("utf-8", "strict")
        return len(encoded).to_bytes(8, "big") + encoded

    preimage = b"".join(
        (
            frame("ebu.failure-id.v1"),
            frame(code),
            frame("I-9"),
            frame("APPLICABLE"),
            frame("ebu_framework.validation"),
            frame(owner),
            frame("1.0.0"),
            (0).to_bytes(8, "big"),
            frame("NOT_APPLICABLE"),
            frame(str(ordinal)),
        )
    )
    return "ebu:failure:core:sha256-" + hashlib.sha256(preimage).hexdigest()


class ValidationReachabilityTests(unittest.TestCase):
    def test_complete_i9_authority_and_reachability(self) -> None:
        contract, validation_contract, predecessor, manifest = self._static_audit()
        self._dynamic_replay(validation_contract)
        inventory = validation_contract["inventory"]
        self.assertEqual(inventory["vector_count"], 97)
        self.assertEqual(inventory["completed_check_count_total"], 292)
        print(
            "I9_AUTHORITY_VECTORS=97 "
            "DYNAMIC=69 STATIC=28 CHECKS=292 ACTIVE_PREDICATES=50"
        )

    def _static_audit(self):
        documents = []
        for path in AUTHORITY_FILES:
            document, raw = _strict_json(ROOT / path)
            self.assertEqual(_sha256(raw), AUTHORITY_RAW_SHA256[path])
            documents.append(document)
        for path, expected in AUTHORITY_RAW_SHA256.items():
            self.assertEqual(_sha256((ROOT / path).read_bytes()), expected)
        contract, validation_contract, predecessor, manifest = documents

        self.assertEqual(
            manifest["authority"]["accepted_predecessor"],
            "fully integrated accepted I-8 coordinate",
        )
        self.assertEqual(
            predecessor["authority"]["required_start_commit"],
            "4ab6f9ca32e32a3801c6a4b6872b34b206e6da7e",
        )
        self.assertEqual(
            predecessor["authority"]["required_start_tree"],
            "591ad275116e9dc28bf0443aae80142e5ad86ec5",
        )

        inventory = validation_contract["inventory"]
        self.assertEqual(inventory["vector_count"], 97)
        self.assertEqual(inventory["dynamic_vector_count"], 69)
        self.assertEqual(inventory["static_witness_count"], 28)
        self.assertEqual(
            inventory["outcome_counts"],
            {"FAILURE": 50, "STATIC_PASS": 28, "SUCCESS": 19},
        )
        self.assertEqual(inventory["completed_check_count_total"], 292)
        self.assertEqual(inventory["active_predicate_count_total"], 50)
        for zero_key in (
            "filesystem_write_count_total",
            "model_call_count_total",
            "network_call_count_total",
            "policy_call_count_total",
            "runner_call_count_total",
            "state_advance_count_total",
            "subprocess_call_count_total",
        ):
            self.assertEqual(inventory[zero_key], 0)

        vectors = validation_contract["vectors"]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors[:69]),
            tuple(f"I9V-{index:03d}" for index in range(1, 70)),
        )
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors[69:]),
            tuple(f"I9S-{index:03d}" for index in range(1, 29)),
        )
        vector_024 = vectors[23]
        self.assertEqual(vector_024["vector_id"], "I9V-024")
        self.assertEqual(vector_024["precedence"]["first_failure_ordinal"], 3)
        self.assertEqual(
            vector_024["precedence"]["active_predicates"], ["CLASS_NOT_T3"]
        )
        self.assertEqual(
            vector_024["expected"]["failure_code"],
            "CAPABILITY_ESCALATION_FORBIDDEN",
        )
        self.assertEqual(
            vector_024["expected"]["failure_id"],
            "ebu:failure:core:sha256-a05524aae5b8bda0625ba6b2ee1c669632bf46b480c8489cbb425900280ac3d0",
        )
        _assert_projection(vectors, validation_contract["projections"]["all_vectors"])
        _assert_projection(vectors[:69], validation_contract["projections"]["dynamic_vectors"])
        _assert_projection(vectors[69:], validation_contract["projections"]["static_vectors"])
        _assert_projection(
            validation_contract["construction_baselines"],
            validation_contract["projections"]["construction_baselines"],
        )
        _assert_projection(
            validation_contract["checklists"],
            validation_contract["projections"]["checklists"],
        )
        _assert_projection(
            validation_contract["failure_identity_contract"]["coordinate_catalogue"],
            validation_contract["projections"]["failure_coordinate_catalogue"],
        )

        self._audit_predecessor_and_locks(contract, predecessor)
        self._audit_validation_ast(contract, manifest)
        self._audit_public_surface(contract, manifest)
        self._audit_import_graph(manifest)
        self._audit_tables(contract)
        self._audit_safety_and_ci(manifest)
        self._audit_text_and_markdown(contract)
        self._audit_static_vectors(validation_contract)
        self._audit_cross_document(contract, validation_contract, predecessor, manifest)
        return documents

    def _audit_predecessor_and_locks(self, contract, predecessor) -> None:
        source_locks = contract["governing_source_chain"]["locks"]
        self.assertEqual(len(source_locks), 73)
        for row in source_locks:
            raw = _base_candidate_bytes(row["path"])
            self.assertEqual(len(raw), row["byte_count"], row["path"])
            self.assertEqual(_sha256(raw), row["raw_sha256"], row["path"])
            self.assertEqual(_blob_id(raw), row["git_object"], row["path"])

        rows = predecessor["rows"]
        self.assertEqual(len(rows), 321)
        self.assertEqual(len({row["path"] for row in rows}), 321)
        total_bytes = 0
        path_rows = []
        identity_rows = []
        for row in rows:
            raw = _base_candidate_bytes(row["path"])
            total_bytes += len(raw)
            self.assertEqual(len(raw), row["byte_count"], row["path"])
            self.assertEqual(_sha256(raw), row["raw_sha256"], row["path"])
            self.assertEqual(_blob_id(raw), row["git_object"], row["path"])
            path_rows.append(row["path"])
            identity_rows.append([row["path"], row["byte_count"], row["raw_sha256"]])
        self.assertEqual(total_bytes, predecessor["tree_inventory"]["total_byte_count"])
        path_projection = ("\n".join(path_rows) + "\n").encode("utf-8")
        self.assertEqual(
            _sha256(path_projection),
            predecessor["tree_inventory"]["path_projection"]["sha256"],
        )
        projected_rows = [
            [row[field] for field in predecessor["row_schema"]] for row in rows
        ]
        _assert_projection(
            projected_rows,
            predecessor["reconstruction"]["route_A"]["expected_projection"],
        )
        _assert_projection(
            identity_rows,
            predecessor["reconstruction"]["route_B"]["expected_raw_identity_projection"],
        )

    def _audit_validation_ast(self, contract, manifest) -> None:
        path = SOURCE / "validation.py"
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        compile(tree, str(path), "exec")
        assignments = _literal_assignments(tree)
        self.assertEqual(tuple(assignments), CONSTANT_NAMES + ("__all__",))
        self.assertEqual(assignments["__all__"], ())

        groups = tuple(
            (
                row["group_id"],
                row["class"],
                tuple(row["permitted_checks"]),
                tuple(row["explicitly_unreachable"]),
                tuple(row["exact_test_paths"]),
            )
            for row in contract["validation_authority"]["groups"]
        )
        self.assertEqual(assignments["_VALIDATION_GROUPS"], groups)
        self.assertEqual(tuple(row[0] for row in groups), tuple(f"V{i}" for i in range(12)))
        self.assertNotIn("T3", tuple(row[1] for row in groups))
        self.assertEqual(assignments["_I9_IMPLEMENTATION_PATHS"], IMPLEMENTATION_PATHS)
        self.assertEqual(
            assignments["_I9_ROOT_EXPORTS"],
            tuple(contract["accepted_surface"]["root_exports"]["values"]),
        )
        self.assertEqual(
            assignments["_I9_FAILURE_CODES"],
            tuple(contract["accepted_surface"]["failure_codes"]["values"]),
        )
        self.assertEqual(
            assignments["_I9_PUBLIC_SIGNATURES"],
            tuple(tuple(row) for row in contract["accepted_surface"]["public_signature_rows"]["rows"]),
        )
        self.assertEqual(
            assignments["_I9_DIRECT_IMPORTS"],
            tuple(tuple(row) for row in manifest["future_import_graph"]["direct_edges"]),
        )
        self.assertEqual(
            assignments["_I9_AUDIT_REGISTER"],
            tuple(row[1] for row in contract["audit_register"]["combined_rows"]),
        )

        bridge_path = "tests/framework/fixtures/bridge_m1_m9_v1.json"
        dynamic_path = "tests/framework/fixtures/dynamic_static_v1.json"
        bridge = json.loads((ROOT / bridge_path).read_text(encoding="utf-8"))
        dynamic = json.loads((ROOT / dynamic_path).read_text(encoding="utf-8"))
        bridge_hash = _sha256((ROOT / bridge_path).read_bytes())
        dynamic_hash = _sha256((ROOT / dynamic_path).read_bytes())
        expected_allowlist = tuple(
            ("V8", bridge_path, bridge_hash, row["case_id"], row["interface"])
            for row in bridge["positive_interface_vectors"]
        ) + tuple(
            ("V9", dynamic_path, dynamic_hash, row["case_id"], row["owner"])
            for row in dynamic["cases"]
        )
        self.assertEqual(assignments["_I9_T2_ALLOWLIST"], expected_allowlist)
        self.assertEqual(len(expected_allowlist), 42)

        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
        self.assertEqual(tuple(node.name for node in functions), PRIVATE_NAMES)
        self.assertEqual(
            [["validation", node.name, _signature(node)] for node in functions],
            manifest["private_signature_rows"],
        )
        self.assertFalse(any(isinstance(node, (ast.ClassDef, ast.Lambda)) for node in ast.walk(tree)))
        nested_functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        self.assertEqual(len(nested_functions), 7)

        relative_imports = _direct_imports(
            tree, tuple(manifest["future_import_graph"]["package_module_order"])
        )
        self.assertEqual(
            relative_imports,
            ("canonical", "numeric", "identity", "hashing", "primitives", "capabilities", "errors"),
        )
        forbidden_calls = {
            "__import__",
            "compile",
            "eval",
            "exec",
            "import_module",
            "open",
            "run",
            "Popen",
        }
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (
                    node.func.id
                    if isinstance(node.func, ast.Name)
                    else node.func.attr
                    if isinstance(node.func, ast.Attribute)
                    else ""
                )
                self.assertNotIn(name, forbidden_calls)

    def _audit_public_surface(self, contract, manifest) -> None:
        init_tree = ast.parse((SOURCE / "__init__.py").read_text(encoding="utf-8"))
        root_exports = _module_exports(init_tree)
        expected_root = tuple(contract["accepted_surface"]["root_exports"]["values"])
        self.assertEqual(root_exports, expected_root)
        self.assertEqual(len(root_exports), 444)
        self.assertEqual(len(set(root_exports)), 444)
        self.assertFalse(any(name.startswith("I9") for name in root_exports))

        errors_tree = ast.parse((SOURCE / "errors.py").read_text(encoding="utf-8"))
        failure_class = next(
            node
            for node in errors_tree.body
            if isinstance(node, ast.ClassDef) and node.name == "FailureCode"
        )
        failure_codes = tuple(
            node.targets[0].id
            for node in failure_class.body
            if isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        )
        self.assertEqual(
            failure_codes,
            tuple(contract["accepted_surface"]["failure_codes"]["values"]),
        )
        self.assertEqual(len(failure_codes), 280)
        self.assertFalse(any(code.startswith("I9_") for code in failure_codes))

        expected_exports = dict(manifest["module_exports"])
        expected_exports["validation"] = []
        for module, expected in expected_exports.items():
            tree = ast.parse((SOURCE / f"{module}.py").read_text(encoding="utf-8"))
            self.assertEqual(_module_exports(tree), tuple(expected), module)
        self.assertEqual(_module_exports(ast.parse((SOURCE / "validation.py").read_text())), ())

        actual_functions = {}
        for path in SOURCE.glob("*.py"):
            if path.stem in {"__init__", "validation"}:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in tree.body:
                if isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    actual_functions[(path.stem, node.name)] = node
        expected_rows = contract["accepted_surface"]["public_signature_rows"]["rows"]
        self.assertEqual(len(expected_rows), 154)
        self.assertEqual(len(actual_functions), 154)
        self.assertEqual(
            set(actual_functions), {(row[0], row[1]) for row in expected_rows}
        )
        for module, name, signature in expected_rows:
            expected_node = ast.parse(f"def _expected{signature}:\n    pass\n").body[0]
            actual_node = actual_functions[(module, name)]
            self.assertEqual(
                ast.dump(actual_node.args, include_attributes=False),
                ast.dump(expected_node.args, include_attributes=False),
                f"{module}.{name}",
            )
            self.assertEqual(
                ast.dump(actual_node.returns, include_attributes=False),
                ast.dump(expected_node.returns, include_attributes=False),
                f"{module}.{name}",
            )

        _assert_projection(
            contract["accepted_surface"]["public_signature_rows"]["rows"],
            contract["accepted_surface"]["public_signature_rows"]["projection"],
        )
        _assert_projection(
            contract["accepted_surface"]["module_exports"],
            contract["accepted_surface"]["module_export_projection"],
        )

    def _audit_import_graph(self, manifest) -> None:
        graph = manifest["future_import_graph"]
        modules = tuple(graph["package_module_order"])
        self.assertEqual(len(modules), 40)
        actual_imports = {}
        for module in modules:
            tree = ast.parse((SOURCE / f"{module}.py").read_text(encoding="utf-8"))
            actual_imports[module] = _direct_imports(tree, modules)
        self.assertEqual(
            actual_imports,
            {module: tuple(values) for module, values in graph["direct_imports"].items()},
        )
        edges = tuple(
            (module, dependency)
            for module in modules
            for dependency in actual_imports[module]
        )
        self.assertEqual(edges, tuple(tuple(row) for row in graph["direct_edges"]))
        self.assertEqual(len(edges), 250)
        self.assertNotIn(("validation", "execution"), edges)
        self.assertFalse(any(target == "validation" and source != "validation" for source, target in edges))

        visiting = set()
        visited = set()

        def visit(module: str) -> None:
            if module in visiting:
                raise AssertionError(f"import cycle reaches {module}")
            if module in visited:
                return
            visiting.add(module)
            for dependency in actual_imports[module]:
                visit(dependency)
            visiting.remove(module)
            visited.add(module)

        for module in modules:
            visit(module)
        self.assertEqual(len(visited), 40)

        reachable = set()
        pending = ["validation"]
        while pending:
            module = pending.pop()
            if module in reachable:
                continue
            reachable.add(module)
            pending.extend(actual_imports[module])
        self.assertNotIn("execution", reachable)
        _assert_projection(graph["direct_edges"], graph["projection"])

    def _audit_tables(self, contract) -> None:
        invariants = contract["audit_register"]["invariants"]
        specification_threats = contract["audit_register"]["specification_threats"]
        implementation_threats = contract["audit_register"]["implementation_plan_threats"]
        open_rows = contract["open_boundaries"]["post_atomic_register_snapshot"]
        self.assertEqual(invariants["count"], 67)
        self.assertEqual(specification_threats["count"], 45)
        self.assertEqual(implementation_threats["count"], 26)
        self.assertEqual(contract["audit_register"]["combined_count"], 138)
        self.assertEqual(open_rows["disposition_row_occurrence_count"], 180)
        _assert_ordered_table_rows(
            ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md",
            invariants["rows"],
        )
        _assert_ordered_table_rows(
            ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md",
            specification_threats["rows"],
        )
        _assert_ordered_table_rows(
            ROOT / "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md",
            implementation_threats["rows"],
        )
        _assert_ordered_table_rows(
            ROOT / "POST_ATOMIC_OPEN_PROBLEM_REGISTER.md",
            open_rows["rows_in_document_order"],
        )
        _assert_projection(invariants["rows"], invariants["projection"])
        _assert_projection(specification_threats["rows"], specification_threats["projection"])
        _assert_projection(implementation_threats["rows"], implementation_threats["projection"])
        _assert_projection(open_rows["rows_in_document_order"], open_rows["projection"])
        _assert_projection(
            contract["audit_register"]["combined_rows"],
            contract["audit_register"]["combined_projection"],
        )

    def _audit_safety_and_ci(self, manifest) -> None:
        safety_path = ROOT / "tests/framework/safety.py"
        safety_raw = safety_path.read_bytes()
        self.assertEqual(
            _sha256(_base_candidate_bytes("tests/framework/safety.py")),
            "40346595695d908a575dbc8fe8228564f2e182268a0822b93ce5b0db03246eb6",
        )
        safety_tree = ast.parse(safety_raw.decode("utf-8"), filename=str(safety_path))
        safety_assignments = _literal_assignments(safety_tree)
        self.assertIn("i9_forbidden_observation_guard", _module_exports(safety_tree))
        self.assertEqual(
            safety_assignments["_I9_FORBIDDEN_DYNAMIC_IMPORT_CALLS"],
            ("import_module", "invalidate_caches", "reload"),
        )
        self.assertIn("subprocess", safety_assignments["_I9_FORBIDDEN_PROCESS_MODULE_PREFIXES"])
        self.assertIn("results", safety_assignments["_I9_FORBIDDEN_HISTORICAL_MODULE_PREFIXES"])
        safety_imports = {
            alias.name.split(".", 1)[0]
            for node in safety_tree.body
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        self.assertFalse(safety_imports & {"ebu_framework", "subprocess", "socket", "requests"})

        workflow_path = ROOT / ".github/workflows/tests.yml"
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertEqual(
            _sha256(_base_candidate_bytes(".github/workflows/tests.yml")),
            "4d12f834e52bf92a723ab1e2c9723a9b395344320f3c95482b64d9133c766d23",
        )
        self.assertEqual(workflow.count("  workflow_dispatch:\n"), 1)
        self.assertEqual(workflow.count("  framework-t0:\n"), 1)
        self.assertEqual(workflow.count("  framework-t1:\n"), 1)
        self.assertEqual(workflow.count("  framework-t2:\n"), 1)
        self.assertNotIn("framework-t3", workflow.lower())
        self.assertIn("if: github.event_name == 'workflow_dispatch'", workflow)
        self.assertEqual(
            workflow.count("python -m pip install --require-hashes -r requirements-framework.lock"),
            3,
        )
        self.assertEqual(workflow.count('python-version: "3.14"'), 3)
        self.assertEqual(workflow.count('python-version: "3.14.2"'), 0)
        self.assertNotIn("python -m pip install --no-deps .", workflow)
        self.assertNotIn("python -m pip install .", workflow)
        self.assertEqual(workflow.count("or result.skipped"), 4)
        self.assertEqual(workflow.count("or result.expectedFailures"), 4)
        self.assertEqual(workflow.count("or result.unexpectedSuccesses"), 4)

        t0 = workflow.split("  framework-t0:\n", 1)[1].split("  framework-t1:\n", 1)[0]
        t1 = workflow.split("  framework-t1:\n", 1)[1].split("  framework-t2:\n", 1)[0]
        t2 = workflow.split("  framework-t2:\n", 1)[1]
        pattern = re.compile(r'"(tests/framework/test_[a-z0-9_]+\.py)"')
        self.assertEqual(tuple(pattern.findall(t0)), T0_PATHS)
        self.assertEqual(tuple(pattern.findall(t1)), T1_PATHS)
        self.assertEqual(tuple(pattern.findall(t2)), T2_PATHS)
        self.assertEqual(
            list(manifest["ci_boundary"]["push_pull_request"]["T0"]), list(T0_PATHS)
        )
        self.assertEqual(
            list(manifest["ci_boundary"]["push_pull_request"]["T1"]), list(T1_PATHS)
        )
        self.assertEqual(
            list(manifest["ci_boundary"]["workflow_dispatch_only"]["T2"]), list(T2_PATHS)
        )
        for required in (
            "2e7848dc495c4b2d5fb2ea09d668f2b240d3ec02",
            "8f570082e40304b156aa18714c65938777126f74",
            "8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af",
            "cacb79a4b52eb714b79424524c12cba9f8a4d2327abe99c2b76260c4621a898d",
            "I9_T2_AUTHORITY_ALLOWLIST=42",
        ):
            self.assertIn(required, t2)
        for region, label in ((t0, "T0"), (t1, "T1"), (t2, "T2")):
            self.assertIn(f"{label}_COMPLETED_TESTS=", region)
            self.assertIn("count <= 0", region)
            self.assertIn(
                'export PYTHONPATH="$compatibility_root/src:'
                '$compatibility_root/tests/framework"',
                region,
            )
        self.assertIn(
            'export PYTHONPATH="$candidate_root/src:'
            '$candidate_root/tests/framework"',
            t0,
        )

    def _audit_text_and_markdown(self, contract) -> None:
        for path in IMPLEMENTATION_PATHS + tuple(AUTHORITY_RAW_SHA256):
            raw = (ROOT / path).read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), path)
            self.assertNotIn(b"\r", raw, path)
            self.assertTrue(raw.endswith(b"\n"), path)
            raw.decode("utf-8", "strict")
            self.assertFalse(
                any(line.endswith((b" ", b"\t")) for line in raw.splitlines()), path
            )
        for source in (
            "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_SPECIFICATION.md",
            "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_IMPLEMENTATION_PLAN.md",
            "POST_ATOMIC_OPEN_PROBLEM_REGISTER.md",
            "UNIFIED_PYTHON_RESEARCH_FRAMEWORK_I9_AUTHORITY_AMENDMENT.md",
        ):
            text = (ROOT / source).read_text(encoding="utf-8")
            self.assertEqual(text.count("```"), 2 * (text.count("```") // 2), source)
            self.assertEqual(text.count("]("), len(re.findall(r"\]\([^\n)]*\)", text)), source)
        self.assertEqual(contract["future_implementation_boundary"]["path_count"], 4)
        self.assertNotIn(
            "report", tuple(Path(path).name.lower() for path in IMPLEMENTATION_PATHS)
        )

    def _audit_static_vectors(self, validation_contract) -> None:
        vectors = validation_contract["vectors"][69:]
        expected_kinds = (
            "PACKAGE_CARDINALITY",
            "PREDECESSOR_ROUTE_A",
            "PREDECESSOR_ROUTE_B",
            "PREDECESSOR_ROUTE_AGREEMENT",
            "ACCEPTED_TARGET",
            "ROOT_EXPORTS",
            "FAILURE_CODES",
            "PUBLIC_SIGNATURES",
            "MODULE_EXPORTS",
            "IMPORT_GRAPH",
            "NO_EXECUTION_EDGE",
            "IMPLEMENTATION_PATH_CLOSURE",
            "DEPENDENCY_LOCKS",
            "UNICODE_LOCKS",
            "VALIDATION_GROUPS",
            "VECTOR_MATERIALIZATION",
            "FAILURE_IDS",
            "COLLISION_AUDIT",
            "INVARIANT_REGISTER",
            "SPECIFICATION_THREAT_REGISTER",
            "IMPLEMENTATION_PLAN_THREAT_REGISTER",
            "OPEN_PROBLEM_REGISTER",
            "SOURCE_LOCKS",
            "CROSS_DOCUMENT_AGREEMENT",
            "MARKDOWN_INTEGRITY",
            "TEXT_INTEGRITY",
            "GIT_SCOPE",
            "HISTORICAL_SAFETY",
        )
        self.assertEqual(
            tuple(vector["construction"]["static_witness"]["kind"] for vector in vectors),
            expected_kinds,
        )
        for vector in vectors:
            witness = vector["construction"]["static_witness"]
            self.assertEqual(vector["exercise_class"], "AUTHORIZED_STATIC_WITNESS")
            self.assertEqual(vector["owner_interface"], "STATIC_ONLY")
            self.assertEqual(vector["owner_call_count"], 0)
            self.assertEqual(vector["expected"]["outcome"], "STATIC_PASS")
            self.assertEqual(vector["expected"]["result_projection"], witness)
            _assert_projection(
                witness, vector["expected"]["result_projection_identity"]
            )
            self.assertEqual(vector["precedence"]["completed_check_count"], 1)

    def _audit_cross_document(self, contract, validation_contract, predecessor, manifest) -> None:
        self.assertEqual(
            tuple(contract["future_implementation_boundary"]["paths"]), IMPLEMENTATION_PATHS
        )
        self.assertEqual(
            tuple(row[1] for row in manifest["inventory"]["rows"]),
            (
                "src/ebu_framework/validation.py",
                "tests/framework/test_validation_reachability.py",
                "tests/framework/safety.py",
                ".github/workflows/tests.yml",
            ),
        )
        self.assertEqual(
            {row[1] for row in manifest["inventory"]["rows"]},
            set(IMPLEMENTATION_PATHS),
        )
        self.assertEqual(manifest["inventory"]["path_count"], 4)
        self.assertEqual(manifest["inventory"]["modified_count"], 2)
        self.assertEqual(manifest["inventory"]["new_count"], 2)
        self.assertEqual(manifest["future_root_export_suffix"], [])
        self.assertEqual(manifest["future_failure_suffix"], [])
        self.assertEqual(manifest["future_public_signature_rows"], [])
        self.assertFalse(manifest["dependency_drift"]["allowed"])
        self.assertEqual(manifest["ci_boundary"]["T3_job_count"], 0)
        self.assertFalse(contract["validation_authority"]["T3_authorized"])
        self.assertEqual(predecessor["tree_inventory"]["row_count"], 321)
        self.assertEqual(contract["accepted_surface"]["predecessor_tree_row_count"], 321)
        self.assertEqual(contract["audit_register"]["combined_count"], 138)
        self.assertEqual(
            validation_contract["audit_register_contract"]["post_atomic_open_disposition_occurrences"],
            180,
        )

    def _dynamic_replay(self, validation_contract) -> None:
        source_path = str(ROOT / "src")
        tests_path = str(ROOT / "tests/framework")
        if source_path not in sys.path:
            sys.path.insert(0, source_path)
        if tests_path not in sys.path:
            sys.path.insert(0, tests_path)

        from ebu_framework import capabilities
        from ebu_framework import validation
        from ebu_framework.errors import Applicability, FrameworkError
        from ebu_framework.identity import SourceFileRawSha256
        from safety import i9_forbidden_observation_guard

        owners = {name: getattr(validation, name) for name in PRIVATE_NAMES}
        baselines = validation_contract["construction_baselines"]
        outcomes = {"SUCCESS": 0, "FAILURE": 0}
        owner_calls = {name: 0 for name in PRIVATE_NAMES}
        active_predicates = 0
        completed_checks = 0
        delegated_calls = 0
        failure_coordinates = {}

        real_delegate = capabilities._issue_t2_fixture_capability
        with mock.patch.object(
            capabilities,
            "_issue_t2_fixture_capability",
            wraps=real_delegate,
        ) as delegated:
            for vector in validation_contract["vectors"][:69]:
                construction = vector["construction"]
                baseline = baselines[construction["baseline_id"]]
                materialized = _apply_mutations(
                    baseline, construction["closed_mutation_program"]
                )
                self.assertEqual(materialized, construction["materialized_call"])
                _assert_projection(
                    materialized, construction["materialized_call_identity"]
                )
                owner_name = materialized["owner"]
                self.assertEqual(vector["owner_interface"], f"validation.{owner_name}")
                materializers = materialized["argument_materialization"]
                positional = materialized["positional"]
                self.assertEqual(len(materializers), len(positional))
                arguments = []
                for materializer, value in zip(materializers, positional):
                    if materializer == "str":
                        arguments.append(value)
                    elif materializer == "SourceFileRawSha256('sha256-raw:'+value)":
                        arguments.append(SourceFileRawSha256("sha256-raw:" + value))
                    elif materializer.startswith("tuple["):
                        arguments.append(_recursive_tuple(value))
                    else:
                        raise AssertionError(f"unknown argument materializer: {materializer}")

                before_delegate = delegated.call_count
                owner_calls[owner_name] += 1
                expected = vector["expected"]
                with i9_forbidden_observation_guard():
                    if expected["outcome"] == "SUCCESS":
                        result = owners[owner_name](*arguments)
                    else:
                        with self.assertRaises(FrameworkError) as caught:
                            owners[owner_name](*arguments)
                        result = caught.exception
                delta = delegated.call_count - before_delegate
                delegated_calls += delta
                self.assertEqual(delta, vector["delegated_owner_call_count"])

                if expected["outcome"] == "SUCCESS":
                    outcomes["SUCCESS"] += 1
                    if result is None:
                        projection = {"return": "None"}
                    else:
                        projection = {
                            "authorized_interface": object.__getattribute__(
                                result, "authorized_interface"
                            ),
                            "capability_class": type(result).__name__,
                            "case_id": object.__getattribute__(result, "case_id"),
                            "fixture_path": object.__getattribute__(result, "fixture_path"),
                            "fixture_raw_sha256": object.__getattribute__(
                                result, "fixture_raw_sha256"
                            ).hex_digest,
                        }
                    self.assertEqual(projection, expected["result_projection"])
                    _assert_projection(projection, expected["result_projection_identity"])
                else:
                    outcomes["FAILURE"] += 1
                    envelope = result.envelope
                    precedence = vector["precedence"]
                    ordinal = precedence["first_failure_ordinal"]
                    self.assertEqual(envelope.failure_ordinal, ordinal)
                    self.assertEqual(envelope.failure_code.value, expected["failure_code"])
                    self.assertEqual(envelope.stage.value, "I-9")
                    self.assertEqual(envelope.interface_ref.module, "ebu_framework.validation")
                    self.assertEqual(envelope.interface_ref.qualname, owner_name)
                    self.assertEqual(envelope.interface_ref.interface_version, "1.0.0")
                    self.assertEqual(envelope.object_refs, ())
                    self.assertIs(envelope.event_key, Applicability.NOT_APPLICABLE)
                    failure_id = _derive_i9_failure_id(
                        expected["failure_code"], owner_name, ordinal
                    )
                    self.assertEqual(str(envelope.failure_id), failure_id)
                    self.assertEqual(expected["failure_id"], failure_id)
                    coordinate = (expected["failure_code"], owner_name, ordinal)
                    if failure_id in failure_coordinates:
                        self.assertEqual(failure_coordinates[failure_id], coordinate)
                    failure_coordinates[failure_id] = coordinate

                active_predicates += len(vector["precedence"]["active_predicates"])
                completed_checks += vector["precedence"]["completed_check_count"]

        self.assertEqual(outcomes, {"SUCCESS": 19, "FAILURE": 50})
        self.assertEqual(sum(owner_calls.values()), 69)
        self.assertTrue(all(count > 0 for count in owner_calls.values()))
        self.assertEqual(active_predicates, 50)
        self.assertEqual(completed_checks, 264)
        self.assertEqual(delegated_calls, 2)
        self.assertEqual(len(failure_coordinates), 37)
        self.assertEqual(
            validation_contract["failure_identity_contract"]["collision_audit"][
                "distinct_coordinate_collision_count"
            ],
            0,
        )


if __name__ == "__main__":
    unittest.main()
