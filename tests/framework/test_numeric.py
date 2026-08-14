"""Exact T0 validation for the frozen Framework I-2 numerical substrate."""

from __future__ import annotations

import ast
import copy
from collections import Counter
import hashlib
import json
from pathlib import Path
import unittest

from ebu_framework.canonical import encode_ecj1
from ebu_framework.errors import Applicability, FrameworkError
from ebu_framework.identity import ObjectContentHash, ObjectRef, ScientificId, SemanticVersion
from ebu_framework.numeric import (
    Binary64BitsV1,
    Completeness,
    DecimalV1,
    ErrorBound,
    ExactConversion,
    IntegerV1,
    NumericalOperation,
    NumericalResult,
    NumericalVariant,
    RationalV1,
    RuntimeConstraintSet,
    apply_exact_core_operation,
    decimal_to_rational_exact,
    normalize_core_number,
    validate_numerical_policy,
)


FIXTURE = Path(__file__).with_name("fixtures") / "numeric_vectors_v1.json"
FIXTURE_BYTES = 815_982
FIXTURE_SHA256 = "97c55e32319eb734c861fcce08a04f2e167afc6e32cd832bac2ec6d37277287a"
SPEC_SHA256 = "01f7392459af3eaccbd6966b1504fa1206997722677415d080b0b6883d8081ca"
PLAN_SHA256 = "f152d680028c4f35027371d036d7282fd1c5648274018237f98626afbacf170e"
BLOCK_COUNTS = (18, 35, 42, 4, 36, 107, 20, 41, 32)


class _IntSubclass(int):
    pass


class _PolicyProvider:
    """Read-only declaration provider whose operation methods are tripwires."""

    __slots__ = ("_values", "method_calls")

    def __init__(self, values: dict[str, object]) -> None:
        object.__setattr__(self, "_values", values)
        object.__setattr__(self, "method_calls", 0)

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("fixture policy declarations are immutable")

    def _read(self, name: str) -> object:
        try:
            return self._values[name]
        except KeyError as error:
            raise AttributeError(name) from error

    @property
    def policy_ref(self): return self._read("policy_ref")
    @property
    def owning_domain_ref(self): return self._read("owning_domain_ref")
    @property
    def supported_input_variants(self): return self._read("supported_input_variants")
    @property
    def supported_operations(self): return self._read("supported_operations")
    @property
    def result_variant_by_operation(self): return self._read("result_variant_by_operation")
    @property
    def precision_contract_ref(self): return self._read("precision_contract_ref")
    @property
    def rounding_contract_ref(self): return self._read("rounding_contract_ref")
    @property
    def comparison_tolerance_contract_ref(self): return self._read("comparison_tolerance_contract_ref")
    @property
    def approximation_contract_ref(self): return self._read("approximation_contract_ref")
    @property
    def error_bound_contract_ref(self): return self._read("error_bound_contract_ref")
    @property
    def overflow_underflow_nonfinite_contract_ref(self): return self._read("overflow_underflow_nonfinite_contract_ref")
    @property
    def signed_zero_contract_ref(self): return self._read("signed_zero_contract_ref")
    @property
    def backend_dependency_contract_ref(self): return self._read("backend_dependency_contract_ref")
    @property
    def cross_platform_contract_ref(self): return self._read("cross_platform_contract_ref")
    @property
    def failure_contract_ref(self): return self._read("failure_contract_ref")
    @property
    def evidence_requirement_refs(self): return self._read("evidence_requirement_refs")
    @property
    def runtime_constraints(self): return self._read("runtime_constraints")
    @property
    def completeness(self): return self._read("completeness")

    def _invoked(self):
        object.__setattr__(self, "method_calls", self.method_calls + 1)
        raise AssertionError("a numerical-policy method was invoked")

    def validate_operands(self, operation, operands, quantity_context):
        raise AssertionError("POLICY_METHOD_CALLED")

    def evaluate(self, operation, operands, quantity_context):
        raise AssertionError("POLICY_METHOD_CALLED")

    def compare(self, purpose, left, right, quantity_context):
        raise AssertionError("POLICY_METHOD_CALLED")

    def bound_error(self, operation, operands, result, quantity_context):
        raise AssertionError("POLICY_METHOD_CALLED")

    def runtime_requirements(self):
        raise AssertionError("POLICY_METHOD_CALLED")


def _object_ref(value: dict[str, str]) -> ObjectRef:
    return ObjectRef(
        ScientificId(value["object_id"]),
        SemanticVersion(value["object_version"]),
        ObjectContentHash(value["object_content_hash"]),
    )


def _apply_patches(value: object, patches: list[list[object]]) -> object:
    result = copy.deepcopy(value)
    for patch in patches:
        operation, pointer = patch[:2]
        parts = [part.replace("~1", "/").replace("~0", "~") for part in str(pointer).split("/")[1:]]
        parent = result
        for part in parts[:-1]:
            parent = parent[int(part)] if isinstance(parent, list) else parent[part]
        leaf = parts[-1]
        if operation == "remove":
            if isinstance(parent, list):
                del parent[int(leaf)]
            else:
                del parent[leaf]
        elif operation == "replace":
            replacement = copy.deepcopy(patch[2])
            if isinstance(parent, list):
                parent[int(leaf)] = replacement
            else:
                parent[leaf] = replacement
        else:
            raise AssertionError(f"unsupported frozen patch operation: {operation}")
    return result


def _transport(value: object) -> object:
    if isinstance(value, dict) and set(value) == {"literal", "patches"}:
        return _transport(_apply_patches(value["literal"], value["patches"]))
    if isinstance(value, dict) and set(value) == {"bytes_hex"}:
        return bytes.fromhex(value["bytes_hex"])
    if isinstance(value, dict) and set(value) == {"python_value"}:
        item = value["python_value"]
        kind, literal = item["type"], item["value"]
        if kind == "BOOL": return literal == "true"
        if kind == "INT_SUBCLASS": return _IntSubclass(int(literal))
        if kind == "FLOAT": return float(literal)
        if kind == "DICT": return copy.deepcopy(literal)
        if kind == "LIST": return list(literal)
        if kind == "BYTEARRAY": return bytearray.fromhex(literal)
        if kind == "MEMORYVIEW": return memoryview(bytes.fromhex(literal))
        if kind == "BYTES_SUBCLASS": return type("BytesSubclass", (bytes,), {})(bytes.fromhex(literal))
        if kind == "POLICY_PROVIDER_RAISES": return _policy_provider(literal)
        raise AssertionError(f"unknown frozen Python transport: {kind}")
    if isinstance(value, dict):
        return {key: _transport(member) for key, member in value.items()}
    if isinstance(value, list):
        return [_transport(member) for member in value]
    return value


def _materialize(value: object) -> object:
    value = _transport(value)
    if value == "NOT_APPLICABLE":
        return Applicability.NOT_APPLICABLE
    if isinstance(value, list):
        return [_materialize(member) for member in value]
    if not isinstance(value, dict):
        return value
    keys = set(value)
    if keys == {"object_content_hash", "object_id", "object_version"}:
        return _object_ref(value)
    if value.get("variant") == "INTEGER_V1":
        return IntegerV1(value["value"])
    if value.get("variant") == "RATIONAL_V1":
        return RationalV1(IntegerV1(value["numerator"]), IntegerV1(value["denominator"]))
    if value.get("variant") == "DECIMAL_V1":
        return DecimalV1(IntegerV1(value["coefficient"]), IntegerV1(value["exponent10"]))
    if value.get("variant") == "BINARY64_BITS_V1":
        return Binary64BitsV1(value["bits"])
    if "bound_kind" in value:
        return ErrorBound(
            value["bound_kind"],
            _materialize(value["lower"]),
            _materialize(value["upper"]),
            _materialize(value["unit_ref"]),
            _materialize(value["policy_ref"]),
            Completeness(value["completeness"]),
        )
    return {key: _materialize(member) for key, member in value.items() if key != "schema_version"}


def _policy_provider(declaration: dict[str, object]) -> _PolicyProvider:
    raw = _transport(declaration)
    values: dict[str, object] = {}
    for name, value in raw.items():
        if name == "schema_id":
            continue
        if name == "supported_input_variants":
            values[name] = tuple(NumericalVariant(item) for item in value)
        elif name == "supported_operations":
            values[name] = tuple(NumericalOperation(item) for item in value)
        elif name == "result_variant_by_operation":
            values[name] = tuple((NumericalOperation(row[0]), NumericalVariant(row[1])) for row in value)
        elif name == "evidence_requirement_refs":
            values[name] = tuple(_materialize(item) for item in value)
        elif name == "runtime_constraints":
            values[name] = RuntimeConstraintSet(
                tuple(_materialize(item) for item in value["constraint_refs"]),
                Applicability(value["applicability"]),
                Completeness(value["completeness"]),
            )
        elif name == "completeness":
            values[name] = Completeness(value)
        else:
            values[name] = _materialize(value)
    return _PolicyProvider(values)


def _projection(value: object) -> object:
    if isinstance(value, (Completeness, Applicability)):
        return value.value
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()
    return value


def _declared_operation(value: object) -> object:
    return next(
        (member for member in NumericalOperation if member.value == value),
        value,
    )


def _invoke(vector: dict[str, object]) -> tuple[object, tuple[_PolicyProvider, ...]]:
    operation = vector["operation"]
    raw_inputs = vector["inputs"]
    providers: list[_PolicyProvider] = []
    if operation == "STATIC_POLICY_NONINVOCATION":
        provider = _transport(raw_inputs[0])
        providers.append(provider)
        validate_numerical_policy(provider)
        nested = raw_inputs[1]
        return _invoke({"operation": "ebu_framework.numeric.apply_exact_core_operation", "inputs": nested})[0], tuple(providers)
    if operation == "ebu_framework.numeric.validate_numerical_policy":
        declaration = _transport(raw_inputs[0])
        provider = declaration if isinstance(declaration, _PolicyProvider) else _policy_provider(declaration)
        providers.append(provider)
        return validate_numerical_policy(provider), tuple(providers)
    inputs = [_materialize(item) for item in raw_inputs]
    if operation == "ebu_framework.numeric.IntegerV1": return IntegerV1(inputs[0]), ()
    if operation == "ebu_framework.numeric.RationalV1": return RationalV1(inputs[0], inputs[1]), ()
    if operation == "ebu_framework.numeric.DecimalV1": return DecimalV1(inputs[0], inputs[1]), ()
    if operation == "ebu_framework.numeric.Binary64BitsV1": return Binary64BitsV1(inputs[0]), ()
    if operation == "ebu_framework.canonical.encode_ecj1": return encode_ecj1(inputs[0]), ()
    if operation == "ebu_framework.numeric.normalize_core_number": return normalize_core_number(inputs[0]), ()
    if operation == "ebu_framework.numeric.ErrorBound":
        return ErrorBound(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], Completeness(raw_inputs[5])), ()
    if operation == "ebu_framework.numeric.NumericalResult":
        return NumericalResult(
            inputs[0], NumericalOperation(raw_inputs[1]),
            tuple(NumericalVariant(item) for item in raw_inputs[2]),
            inputs[3], inputs[4], inputs[5], Completeness(raw_inputs[6]),
        ), ()
    if operation == "ebu_framework.numeric.apply_exact_core_operation":
        return apply_exact_core_operation(
            _declared_operation(raw_inputs[0]),
            tuple(_materialize(item) for item in raw_inputs[1]),
            exact_conversion=ExactConversion(raw_inputs[2]),
        ), ()
    if operation == "ebu_framework.numeric.decimal_to_rational_exact":
        return decimal_to_rational_exact(inputs[0]), ()
    raise AssertionError(f"numeric adapter has no operation route for {operation}")


def _assert_vector(test: unittest.TestCase, vector: dict[str, object]) -> int:
    expected = vector["expected"]
    providers: tuple[_PolicyProvider, ...] = ()
    if expected["outcome"] == "FAILURE":
        try:
            _invoke(vector)
        except FrameworkError as error:
            envelope = error.envelope
        else:
            test.fail(f"{vector['vector_id']} did not raise its frozen failure")
        test.assertEqual(envelope.failure_code.value, expected["failure_code"])
        test.assertEqual(envelope.failure_id.value, expected["failure_id"])
        test.assertEqual(envelope.failure_ordinal, expected["failure_ordinal"])
        test.assertEqual(envelope.stage.value, expected["failure_stage"])
        interface = envelope.interface_ref
        projected_interface = interface.value if isinstance(interface, Applicability) else interface.to_ecj1()
        test.assertEqual(projected_interface, expected["failure_interface_ref"])
    else:
        result, providers = _invoke(vector)
        projection = _projection(result)
        test.assertEqual(projection, expected["projection"], vector["vector_id"])
        test.assertEqual(bytes(encode_ecj1(projection)).hex(), expected["canonical_hex"], vector["vector_id"])
    test.assertTrue(all(provider.method_calls == 0 for provider in providers), vector["vector_id"])
    return 1


class FrameworkI2NumericTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FIXTURE.read_bytes()
        cls.document = json.loads(cls.raw)

    def test_fixture_identity_schema_and_counts(self) -> None:
        self.assertEqual(len(self.raw), FIXTURE_BYTES)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), FIXTURE_SHA256)
        self.assertFalse(self.raw.endswith(b"\n"))
        self.assertEqual(list(self.document), [
            "fixture_class", "implementation_plan_raw_sha256", "schema_id",
            "schema_version", "specification_raw_sha256", "vectors",
        ])
        self.assertEqual(self.document["fixture_class"], "T0_STATIC_I2")
        self.assertEqual(self.document["specification_raw_sha256"], SPEC_SHA256)
        self.assertEqual(self.document["implementation_plan_raw_sha256"], PLAN_SHA256)
        vectors = self.document["vectors"]
        self.assertEqual(len(vectors), 335)
        self.assertEqual([vector["vector_id"] for vector in vectors], [f"i2-{number:04d}" for number in range(1, 336)])
        self.assertEqual(len({vector["case"] for vector in vectors}), 335)
        self.assertEqual(Counter(vector["expected"]["outcome"] for vector in vectors), Counter({
            "FAILURE": 214, "VALUE": 76, "COMPATIBILITY": 42, "COMPARISON": 3,
        }))
        self.assertEqual(len({vector["operation"] for vector in vectors}), 31)
        categories = ("NORMAL_FORM", "CONSTRUCTOR", "EXACT_OPERATION", "EXACT_CONVERSION", "POLICY_REFUSAL", "COMPATIBILITY", "ENVELOPE", "LIFECYCLE", "PRECEDENCE")
        self.assertEqual(tuple(sum(vector["category"] == category for vector in vectors) for category in categories), BLOCK_COUNTS)
        for vector in vectors:
            self.assertEqual(list(vector), ["case", "category", "expected", "inputs", "operation", "quantity_context", "vector_id"])

    def test_vectors_i2_0001_through_i2_0135(self) -> None:
        completed = 0
        for vector in self.document["vectors"][:135]:
            with self.subTest(vector_id=vector["vector_id"], case=vector["case"]):
                completed += _assert_vector(self, vector)
        self.assertEqual(completed, 135)

    def test_policy_provider_methods_are_never_invoked(self) -> None:
        tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
        provider_class = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "_PolicyProvider"
        )
        expected_methods = {
            "validate_operands": ("self", "operation", "operands", "quantity_context"),
            "evaluate": ("self", "operation", "operands", "quantity_context"),
            "compare": ("self", "purpose", "left", "right", "quantity_context"),
            "bound_error": ("self", "operation", "operands", "result", "quantity_context"),
            "runtime_requirements": ("self",),
        }
        provider_methods = tuple(
            node
            for node in provider_class.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and not node.name.startswith("_")
            and not any(
                isinstance(decorator, ast.Name) and decorator.id == "property"
                for decorator in node.decorator_list
            )
        )
        self.assertEqual(tuple(node.name for node in provider_methods), tuple(expected_methods))
        for method in provider_methods:
            self.assertIs(type(method), ast.FunctionDef)
            self.assertFalse(method.decorator_list)
            self.assertFalse(method.args.posonlyargs)
            self.assertEqual(
                tuple(argument.arg for argument in method.args.args),
                expected_methods[method.name],
            )
            self.assertIsNone(method.args.vararg)
            self.assertFalse(method.args.kwonlyargs)
            self.assertFalse(method.args.kw_defaults)
            self.assertIsNone(method.args.kwarg)
            self.assertFalse(method.args.defaults)
            self.assertEqual(len(method.body), 1)
            statement = method.body[0]
            self.assertIs(type(statement), ast.Raise)
            self.assertIsNone(statement.cause)
            self.assertIs(type(statement.exc), ast.Call)
            self.assertIs(type(statement.exc.func), ast.Name)
            self.assertEqual(statement.exc.func.id, "AssertionError")
            self.assertFalse(statement.exc.keywords)
            self.assertEqual(len(statement.exc.args), 1)
            self.assertIs(type(statement.exc.args[0]), ast.Constant)
            self.assertEqual(statement.exc.args[0].value, "POLICY_METHOD_CALLED")

        vector = self.document["vectors"][134]
        with self.assertRaises(FrameworkError) as caught:
            _invoke(vector)
        self.assertEqual(caught.exception.envelope.failure_code.value, "NUMERICAL_POLICY_REQUIRED")


if __name__ == "__main__":
    unittest.main()
