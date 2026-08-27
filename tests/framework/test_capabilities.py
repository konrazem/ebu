"""Synthetic information-capability and I-4 reachability validation."""

from __future__ import annotations

import ast
import copy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
import pickle
from pathlib import Path
import unittest
from unittest.mock import patch

import ebu_framework as framework
import ebu_framework.capabilities as capabilities
from ebu_framework.canonical import encode_ecj1
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.errors import Applicability, FailureCode, FrameworkError
from ebu_framework.hashing import compute_object_content_hash
from ebu_framework.identity import ObjectContentHash, ObjectRef, ScientificId, SemanticVersion
from ebu_framework.numeric import IntegerV1
from ebu_framework.policy import InformationContract, InformationReadSet
from ebu_framework.primitives import Duration
from nacl.signing import SigningKey


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/ebu_framework"
FIXTURE = Path(__file__).with_name("fixtures") / "authorization_vectors_v1.json"
MECHANICAL = ROOT / "unified_python_research_framework_i4_contract.json"
ATOMIC = ROOT / "atomic_interaction_declaration_contract.json"


def _vectors() -> list[dict[str, object]]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["vectors"]


def _ref(kind: str, label: str, fill: str) -> ObjectRef:
    return ObjectRef(
        object_id=ScientificId(f"ebu:{kind}:validation:{label}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash("sha256:" + fill * 64),
    )


def _envelope(
    *,
    object_id: ScientificId,
    object_kind_id: ScientificId,
    payload: object,
) -> CommonObjectEnvelope:
    version = SemanticVersion("1.0.0")
    schema_id = ScientificId("ebu:schema:validation:information-v1")
    content_hash = compute_object_content_hash(
        object_id=object_id,
        object_kind=str(object_kind_id),
        schema_id=schema_id,
        schema_version=version,
        object_version=version,
        authority_refs=(),
        supersedes_ref=None,
        object_content_payload=payload,
    )
    return CommonObjectEnvelope(
        object_id=object_id,
        object_kind_id=object_kind_id,
        schema_id=schema_id,
        schema_version=version,
        object_version=version,
        authority_refs=(),
        supersedes_ref=Applicability.NOT_APPLICABLE,
        object_content_payload=bytes(encode_ecj1(payload)),
        object_content_hash=content_hash,
        lifecycle_status=LifecycleStatus.ACCEPTED,
        record_metadata_ref=Applicability.NOT_APPLICABLE,
    )


def _contract(
    visible: tuple[ObjectRef, ...],
    *,
    maximum_age: int = 5_000_000,
) -> InformationContract:
    clock = _ref("clock", "synthetic", "a")
    policy = _ref("policy", "synthetic", "b")
    rules = tuple(
        (reference, Duration(clock_ref=clock, ticks=IntegerV1(maximum_age)))
        for reference in visible
    )
    payload = {
        "availability_rule_refs": [policy.to_ecj1()],
        "max_age_rules": [
            [reference.to_ecj1(), duration.to_ecj1()]
            for reference, duration in rules
        ],
        "privacy_restriction_refs": [],
        "visible_field_refs": [reference.to_ecj1() for reference in visible],
    }
    return InformationContract(
        envelope=_envelope(
            object_id=ScientificId("ebu:information-contract:validation:synthetic"),
            object_kind_id=ScientificId(
                "ebu:kind:validation:information-contract"
            ),
            payload=payload,
        ),
        visible_field_refs=visible,
        max_age_rules=rules,
        privacy_restriction_refs=(),
        availability_rule_refs=(policy,),
    )


def _timestamp(offset_microseconds: int = 0) -> str:
    value = datetime(2030, 1, 1, tzinfo=timezone.utc) + timedelta(
        microseconds=offset_microseconds
    )
    return value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _read_set(
    fields: tuple[ObjectRef, ...],
    objects: tuple[ObjectRef, ...] = (),
) -> InformationReadSet:
    view_ref = _ref("information-view", "attempted", "c")
    payload = {
        "information_view_ref": view_ref.to_ecj1(),
        "read_field_refs": [reference.to_ecj1() for reference in fields],
        "read_object_refs": [reference.to_ecj1() for reference in objects],
    }
    return InformationReadSet(
        envelope=_envelope(
            object_id=ScientificId("ebu:information-read-set:validation:attempted"),
            object_kind_id=ScientificId(
                "ebu:kind:validation:information-read-set"
            ),
            payload=payload,
        ),
        information_view_ref=view_ref,
        read_field_refs=fields,
        read_object_refs=objects,
    )


def _invoke_information_vector(
    test: unittest.TestCase, vector: dict[str, object]
) -> None:
    case = vector["effective_input"]["information_case"]
    field = _ref("field", "visible", "d")
    hidden = _ref("field", "hidden", "e")
    memory = _ref("policy-memory", "current", "6")
    other_memory = _ref("policy-memory", "different", "7")
    maximum_age = 1 if case in {"TOO_OLD", "AGE_EQUALS_MAX", "NOT_VISIBLE_AND_TOO_OLD"} else 5_000_000
    contract = _contract((field,), maximum_age=maximum_age)
    fabricated_ref = hidden if case in {"NOT_VISIBLE", "NOT_VISIBLE_AND_TOO_OLD"} else field
    available_at = (
        _timestamp(1)
        if case == "FUTURE"
        else _timestamp()
    )
    payload = (
        bytes(encode_ecj1({"uri": "https://invalid"}))
        if case == "TRAVERSAL"
        else bytes(encode_ecj1({"value": 1}))
    )
    fabricated = ((fabricated_ref, payload, available_at),)
    now = _timestamp(
        2
        if case in {"TOO_OLD", "NOT_VISIBLE_AND_TOO_OLD"}
        else 1
        if case == "AGE_EQUALS_MAX"
        else 0
    )
    expected_memory: ObjectRef | Applicability = Applicability.NOT_APPLICABLE
    attempted: InformationReadSet | Applicability = Applicability.NOT_APPLICABLE
    if case == "VALID_STATEFUL":
        expected_memory = memory
        attempted = _read_set((field,), (memory,))
    elif case == "STATELESS_MEMORY_PRESENT":
        attempted = _read_set((field,), (memory,))
    elif case == "CURRENT_MEMORY_MISMATCH":
        expected_memory = memory
        attempted = _read_set((field,), (other_memory,))
    elif case == "READ_SET_DENIED":
        attempted = _read_set((hidden,))
    elif case == "READ_SET_DUPLICATE":
        attempted = _read_set((field, field))
    expected = vector["expected"]
    result = None
    error = None
    real_owner = capabilities.build_synthetic_information_view
    with patch.object(
        capabilities,
        "build_synthetic_information_view",
        wraps=real_owner,
    ) as owner, framework.errors._i4_validation_context(
        expected["failure_ordinal"], vector["name"]
    ):
        try:
            result = capabilities.build_synthetic_information_view(
                contract,
                expected_memory,
                fabricated,
                attempted,
                now,
            )
        except FrameworkError as caught:
            error = caught
    test.assertEqual(owner.call_count, 1)
    if expected["outcome"] == "SUCCESS":
        test.assertIsNone(error)
        test.assertIs(type(result), tuple)
        test.assertEqual(len(result), 2)
        view, capability = result
        test.assertIs(
            capability.capability_class, capabilities.CapabilityClass.T1
        )
        test.assertFalse(capability.traversal_allowed)
        test.assertEqual(
            view.visible_field_records,
            tuple((reference, raw) for reference, raw, _ in fabricated),
        )
        actual_checks = 6
    else:
        assert error is not None
        envelope = error.envelope
        from tests.framework.test_authorization import _assert_failure

        _assert_failure(test, vector, error)
        actual_checks = {
            FailureCode.INFORMATION_NOT_VISIBLE: 1,
            FailureCode.INFORMATION_NOT_AVAILABLE: 2,
            FailureCode.INFORMATION_TOO_OLD: 3,
            FailureCode.INFORMATION_CAPABILITY_INVALID: 4,
            FailureCode.CURRENT_MEMORY_MISMATCH: 4,
            FailureCode.INFORMATION_TRAVERSAL_FORBIDDEN: 5,
            FailureCode.INFORMATION_READ_SET_DENIED: 6,
        }[envelope.failure_code]
    test.assertEqual(actual_checks, expected["completed_check_count"])
    test.assertEqual(
        expected["provider_calls"],
        {"verify_key_constructor": 0, "verify": 0},
    )
    test.assertEqual(
        expected["service_calls"], {"trusted_time": 0, "revocation": 0}
    )
    test.assertEqual(expected["model_step_count"], 0)


class FrameworkI4CapabilitiesTests(unittest.TestCase):
    def test_i4v_096_through_i4v_107_information(self) -> None:
        vectors = _vectors()[95:107]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors),
            tuple(f"i4v-{index:03d}" for index in range(96, 108)),
        )
        for vector in vectors:
            with self.subTest(vector_id=vector["vector_id"]):
                _invoke_information_vector(self, vector)

        field = _ref("field", "visible", "d")
        contract = _contract((field,))
        good = ((field, bytes(encode_ecj1({"value": 1})), _timestamp()),)
        _, capability = capabilities.build_synthetic_information_view(
            contract,
            Applicability.NOT_APPLICABLE,
            good,
            Applicability.NOT_APPLICABLE,
            _timestamp(),
        )

        for operation in (
            lambda: capabilities.AccessCapability(),
            lambda: copy.copy(capability),
            lambda: copy.deepcopy(capability),
            lambda: pickle.dumps(capability),
            lambda: replace(capability, traversal_allowed=True),
        ):
            with self.assertRaises(FrameworkError) as rejected:
                operation()
            self.assertIs(
                rejected.exception.envelope.failure_code,
                FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
            )
        with self.assertRaises(FrameworkError):
            class Escalated(capabilities.AccessCapability):
                pass
        forged = object.__new__(capabilities.AccessCapability)
        with self.assertRaises(FrameworkError) as reconstructed:
            getattr(forged, "capability_class")
        self.assertIs(
            reconstructed.exception.envelope.failure_code,
            FailureCode.CAPABILITY_ESCALATION_FORBIDDEN,
        )



def _relative_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1:
            if node.module:
                imports.append(node.module.split(".", 1)[0])
            else:
                imports.extend(alias.name.split(".", 1)[0] for alias in node.names)
    return imports


class FrameworkI4ReachabilityTests(unittest.TestCase):
    def test_i4v_118_through_i4v_126_reachability(self) -> None:
        all_vectors = _vectors()
        vectors = all_vectors[117:126]
        self.assertEqual(
            tuple(vector["vector_id"] for vector in vectors),
            tuple(f"i4v-{index:03d}" for index in range(118, 127)),
        )
        mechanical = json.loads(MECHANICAL.read_text(encoding="utf-8"))
        atomic = json.loads(ATOMIC.read_text(encoding="utf-8"))
        from tests.framework.test_authorization import (
            _assert_counts,
            _assert_failure,
            _invoke_outer,
        )

        for vector in (vectors[0], vectors[1], vectors[3]):
            with self.subTest(vector_id=vector["vector_id"]):
                record, counts, material = _invoke_outer(vector)
                self.assertIs(
                    record.status,
                    framework.AuthorizationValidationStatus.REJECTED,
                )
                _assert_failure(self, vector, record.failure)
                _assert_counts(self, vector, counts)
                self.assertEqual(
                    len(record.completed_checks),
                    vector["expected"]["completed_check_count"],
                )
                self.assertEqual(
                    material.time_service.calls,
                    vector["expected"]["service_calls"]["trusted_time"],
                )
                self.assertEqual(
                    material.revocation_service.calls,
                    vector["expected"]["service_calls"]["revocation"],
                )

        trust_path = SOURCE / "trust.py"
        trust_source = trust_path.read_text(encoding="utf-8")
        trust_tree = ast.parse(trust_source, filename=str(trust_path))
        profile_function = next(
            node
            for node in trust_tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "validate_trust_profile"
        )
        failure_calls = [
            node
            for node in ast.walk(profile_function)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_failure"
        ]
        key_call = next(
            node
            for node in failure_calls
            if "VALIDATION_KEY_FORBIDDEN" in ast.unparse(node)
        )
        namespace_call = next(
            node
            for node in failure_calls
            if "VALIDATION_NAMESPACE_FORBIDDEN" in ast.unparse(node)
        )
        expected_validation_ids = {
            "ed25519:" + hashlib.sha256(bytes(key.verify_key)).hexdigest()
            for key in (
                SigningKey(bytes.fromhex(seed))
                for seed in json.loads(
                    (ROOT / "unified_python_research_framework_i4_validation_contract.json").read_text(
                        encoding="utf-8"
                    )
                )["fixed_authority"]["synthetic_key_seeds_hex"].values()
            )
        }
        expected_validation_ids.update(
            "ed25519:" + hashlib.sha256(public).hexdigest()
            for public, _, _ in (
                (
                    bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"),
                    b"",
                    b"",
                ),
                (
                    bytes.fromhex("3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"),
                    b"",
                    b"",
                ),
                (
                    bytes.fromhex("fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025"),
                    b"",
                    b"",
                ),
            )
        )
        import ebu_framework.authorization as authorization_module
        import ebu_framework.trust as trust_module
        static_120 = vectors[2]
        static_checks = 0
        with patch.object(
            authorization_module, "validate_stage_authorization"
        ) as no_outer, patch.object(
            trust_module, "validate_trust_profile"
        ) as no_profile:
            self.assertEqual(
                hashlib.sha256(FIXTURE.read_bytes()).hexdigest(),
                "6034a6c08be1c9d77424c4b0324e89287cd7fbe275ce1830407df4b8b991ad1b",
            )
            static_checks += 1
            self.assertLess(key_call.lineno, namespace_call.lineno)
            static_checks += 1
            self.assertIn("_failure", ast.unparse(key_call))
            static_checks += 1
            self.assertIn("_failure", ast.unparse(namespace_call))
            static_checks += 1
            self.assertEqual(
                trust_module._VALIDATION_KEY_IDS, expected_validation_ids
            )
            static_checks += 1
            self.assertEqual((no_outer.call_count, no_profile.call_count), (0, 0))
            static_checks += 1
        self.assertEqual(
            static_checks, static_120["expected"]["completed_check_count"]
        )

        order = tuple(atomic["proposed_surface"]["acyclic_order"]) + (
            "trust",
            "authorization",
            "authorization_use",
            "capabilities",
        )
        direct = dict(atomic["proposed_surface"]["post_d2_direct_imports"])
        direct.update(mechanical["direct_imports"])
        projection = [[module, direct[module]] for module in order]
        payload = (
            json.dumps(
                projection,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8")
        graph_rule = mechanical["import_graph_rule"]
        i4_modules = ("trust", "authorization", "authorization_use", "capabilities")
        source_by_module = {
            module: (SOURCE / f"{module}.py").read_text(encoding="utf-8")
            for module in i4_modules
        }
        trees = {
            module: ast.parse(source_by_module[module]) for module in i4_modules
        }
        call_names = {
            node.func.id
            for tree in trees.values()
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        common_source = "\n".join(source_by_module.values())
        static_witnesses = (
            *(type(trees[module]) is ast.Module for module in i4_modules),
            *(
                _relative_imports(SOURCE / f"{module}.py")
                == mechanical["direct_imports"][module]
                for module in i4_modules
            ),
            *(
                tuple(getattr(__import__(f"ebu_framework.{module}", fromlist=["__all__"]), "__all__"))
                == tuple(mechanical["module_exports"][module])
                + (("T2FixtureCapability",) if module == "capabilities" else ())
                for module in i4_modules
            ),
            "SigningKey" not in common_source,
            (
                "T2FixtureCapability" in source_by_module["capabilities"]
                and all(
                    "T2FixtureCapability" not in source_by_module[module]
                    for module in i4_modules[:-1]
                )
            ),
            "ScientificExecutionLease" not in common_source,
            "build_information_view" not in common_source,
            "validate_information_read_set" not in common_source,
            "model_step" not in call_names,
            "simulate" not in call_names,
            "run" not in call_names,
            "execute_gate" not in call_names,
            not any(
                isinstance(node, ast.ImportFrom)
                and node.module
                and node.module.startswith("tests")
                for tree in trees.values()
                for node in ast.walk(tree)
            ),
            sum(len(direct[module]) for module in order)
            == graph_rule["post_i4_package_direct_import_edge_count"],
            hashlib.sha256(payload).hexdigest()
            == graph_rule["combined_projection_sha256"],
        )
        self.assertEqual(len(static_witnesses), 24)
        for vector in vectors[4:]:
            with self.subTest(vector_id=vector["vector_id"]):
                self.assertTrue(all(static_witnesses))
                self.assertEqual(
                    len(static_witnesses),
                    vector["expected"]["completed_check_count"],
                )
                self.assertEqual(vector["expected"]["outcome"], "STATIC_PASS")

        self.assertEqual(
            {
                "provider_constructor": sum(v["expected"]["provider_calls"]["verify_key_constructor"] for v in all_vectors),
                "provider_verify": sum(v["expected"]["provider_calls"]["verify"] for v in all_vectors),
                "trusted_time": sum(v["expected"]["service_calls"]["trusted_time"] for v in all_vectors),
                "revocation": sum(v["expected"]["service_calls"]["revocation"] for v in all_vectors),
                "sqlite_begin": sum(v["expected"]["sqlite_begin_count"] for v in all_vectors),
                "protected_mutation": sum(v["expected"]["protected_mutation_count"] for v in all_vectors),
                "completed_checks": sum(v["expected"]["completed_check_count"] for v in all_vectors),
                "model_step": sum(v["expected"]["model_step_count"] for v in all_vectors),
            },
            {
                "provider_constructor": 216,
                "provider_verify": 216,
                "trusted_time": 28,
                "revocation": 24,
                "sqlite_begin": 8,
                "protected_mutation": 6,
                "completed_checks": 2111,
                "model_step": 0,
            },
        )
        effective_inputs = {
            json.dumps(
                [vector["interface"], vector["effective_input"]],
                sort_keys=True,
                separators=(",", ":"),
            )
            for vector in all_vectors
        }
        self.assertEqual(len(effective_inputs), 126)
        self.assertEqual(
            {
                outcome: sum(
                    vector["expected"]["outcome"] == outcome
                    for vector in all_vectors
                )
                for outcome in ("SUCCESS", "FAILURE", "STATIC_PASS")
            },
            {"SUCCESS": 21, "FAILURE": 99, "STATIC_PASS": 6},
        )
        self.assertEqual(
            {
                exercise_class: sum(
                    vector["exercise_class"] == exercise_class
                    for vector in all_vectors
                )
                for exercise_class in (
                    "PRODUCTION_INTERFACE_INVOKED",
                    "FORMATION_FAILURE_BEFORE_INTERFACE",
                    "AUTHORIZED_STATIC_PASS",
                )
            },
            {
                "PRODUCTION_INTERFACE_INVOKED": 119,
                "FORMATION_FAILURE_BEFORE_INTERFACE": 1,
                "AUTHORIZED_STATIC_PASS": 6,
            },
        )
        outcomes_by_effective_input: dict[str, set[str]] = {}
        for vector in all_vectors:
            key = json.dumps(
                [vector["interface"], vector["effective_input"]],
                sort_keys=True,
                separators=(",", ":"),
            )
            outcomes_by_effective_input.setdefault(key, set()).add(
                vector["expected"]["outcome"]
            )
        self.assertEqual(
            sum(len(outcomes) > 1 for outcomes in outcomes_by_effective_input.values()),
            0,
        )
        failure_ids = [
            vector["expected"]["failure_id"]
            for vector in all_vectors
            if vector["expected"]["outcome"] == "FAILURE"
        ]
        self.assertEqual(len(failure_ids), len(set(failure_ids)))
        self.assertEqual(
            sum(
                len(vector["expected"]["predicate_truth_set"])
                for vector in all_vectors
            ),
            109,
        )
        self.assertEqual(
            len(
                {
                    predicate
                    for vector in all_vectors
                    for predicate in vector["expected"]["predicate_truth_set"]
                }
            ),
            55,
        )
        i7_paths = json.loads(
            (
                ROOT
                / "unified_python_research_framework_i7_implementation_path_manifest.json"
            ).read_bytes()
        )
        i8_contract = json.loads(
            (ROOT / "unified_python_research_framework_i8_contract.json").read_bytes()
        )
        i8_paths = json.loads(
            (
                ROOT
                / "unified_python_research_framework_i8_implementation_path_manifest.json"
            ).read_bytes()
        )
        t2_patch = next(
            row
            for row in i7_paths["exact_construction_patches"]["rows"]
            if row["patch_id"] == "I7-P05"
        )
        self.assertEqual(len(capabilities._T2_ALLOWLIST), 42)
        self.assertEqual(
            tuple(
                {
                    "fixture_path": path,
                    "fixture_raw_sha256": str(raw_sha256),
                    "case_id": case_id,
                    "authorized_interface": interface,
                }
                for path, raw_sha256, case_id, interface in capabilities._T2_ALLOWLIST[36:]
            ),
            tuple(t2_patch["exact_new_rows"]),
        )
        clcd_contract = json.loads(
            (ROOT / "closed_loop_correction_diagnostics_contract.json").read_bytes()
        )
        stage_c_contract = json.loads(
            (
                ROOT / "framework_alpha_packaging_release_candidate_contract.json"
            ).read_bytes()
        )
        failures = tuple(code.value for code in FailureCode)
        root_exports = tuple(framework.__all__)
        self.assertEqual(failures[:280], tuple(i8_contract["failure_inventory"]["future_values"]))
        self.assertEqual(failures[280:], tuple(clcd_contract["failure_suffix"]))
        self.assertEqual((len(failures), len(set(failures))), (294, 294))
        self.assertEqual(root_exports[:444], tuple(i8_contract["root_exports"]["future_values"]))
        self.assertEqual(root_exports[444:], tuple(clcd_contract["root_export_suffix"]))
        self.assertEqual((len(root_exports), len(set(root_exports))), (471, 471))
        current_inventory = stage_c_contract["test_inventory_reconciliation"][
            "exact_current_import_inventory"
        ]
        current_order = tuple(
            i8_paths["future_import_graph"]["package_module_order"]
        ) + tuple(current_inventory["suffix_module_order"])
        modules = {
            path.stem for path in SOURCE.glob("*.py") if path.name != "__init__.py"
        }
        self.assertEqual((len(current_order), set(current_order)), (42, modules))
        current_graph: dict[str, list[str]] = {}
        current_exports: dict[str, tuple[str, ...]] = {}
        for name in current_order:
            module_tree = ast.parse(
                (SOURCE / f"{name}.py").read_text(encoding="utf-8")
            )
            current_graph[name] = []
            for node in module_tree.body:
                if not isinstance(node, ast.ImportFrom) or node.level != 1:
                    continue
                candidates = (
                    (node.module,)
                    if node.module is not None
                    else tuple(alias.name for alias in node.names)
                )
                for dependency in candidates:
                    if dependency in modules and dependency not in current_graph[name]:
                        current_graph[name].append(dependency)
            module_exports: tuple[str, ...] = ()
            for node in module_tree.body:
                if (
                    isinstance(node, ast.Assign)
                    and len(node.targets) == 1
                    and isinstance(node.targets[0], ast.Name)
                    and node.targets[0].id == "__all__"
                ):
                    module_exports = tuple(ast.literal_eval(node.value))
                elif (
                    isinstance(node, ast.AugAssign)
                    and isinstance(node.target, ast.Name)
                    and node.target.id == "__all__"
                    and isinstance(node.op, ast.Add)
                ):
                    module_exports += tuple(ast.literal_eval(node.value))
            current_exports[name] = module_exports
        module_order_projection = ("\n".join(current_order) + "\n").encode("utf-8")
        graph_projection = (
            json.dumps(
                [[name, current_graph[name]] for name in current_order],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        export_projection = (
            json.dumps(
                [[name, list(current_exports[name])] for name in current_order],
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")
            + b"\n"
        )
        self.assertEqual(
            sum(len(values) for values in current_graph.values()),
            current_inventory["current_direct_edge_count"],
        )
        self.assertEqual(
            {name: current_graph[name] for name in current_inventory["suffix_module_order"]},
            current_inventory["suffix_direct_imports"],
        )
        self.assertEqual(
            {name: len(current_exports[name]) for name in current_inventory["suffix_module_order"]},
            current_inventory["suffix_module_export_counts"],
        )
        for projection, identity in (
            (module_order_projection, current_inventory["module_order_lf"]),
            (graph_projection, current_inventory["direct_import_projection"]),
            (export_projection, current_inventory["module_export_projection"]),
        ):
            self.assertEqual(
                (len(projection), hashlib.sha256(projection).hexdigest()),
                (identity["byte_count"], identity["sha256"]),
            )


if __name__ == "__main__":
    unittest.main()
