from __future__ import annotations

import ast
from dataclasses import fields, is_dataclass
from fractions import Fraction
import hashlib
import inspect
import json
from pathlib import Path
import unittest

import ebu_framework as ebu
from ebu_framework.errors import FrameworkError
from ebu_framework.identity import (
    ObjectContentHash,
    ObjectRef,
    ScientificId,
    SemanticVersion,
)
from ebu_framework.numeric import IntegerV1, RationalV1
from ebu_framework.primitives import ClaimStatus


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/framework/fixtures/closed_loop_correction_diagnostics_v1.json"
CONTRACT_PATH = ROOT / "closed_loop_correction_diagnostics_contract.json"
VALIDATION_PATH = ROOT / "closed_loop_correction_diagnostics_validation_contract.json"
AUTHORITY_PATH = ROOT / "CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_AUTHORITY.md"


def _strict_json(path: Path) -> object:
    def pairs(rows: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in rows:
            if key in result:
                raise AssertionError(f"duplicate key {key}")
            result[key] = value
        return result

    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=pairs,
        parse_float=lambda value: (_ for _ in ()).throw(AssertionError(value)),
        parse_constant=lambda value: (_ for _ in ()).throw(AssertionError(value)),
    )


def _rational(value: str | int) -> RationalV1:
    fraction = Fraction(value)
    return RationalV1(IntegerV1(fraction.numerator), IntegerV1(fraction.denominator))


def _text(value: RationalV1 | ebu.Applicability) -> str:
    if type(value) is ebu.Applicability:
        return value.value
    fraction = Fraction(value.numerator.value, value.denominator.value)
    return str(fraction.numerator) if fraction.denominator == 1 else str(fraction)


def _matrix(rows: list[list[str]]) -> ebu.RationalMatrix:
    return ebu.RationalMatrix(
        rows=tuple(tuple(_rational(value) for value in row) for row in rows)
    )


def _matrix_text(value: ebu.RationalMatrix) -> list[list[str]]:
    return [[_text(item) for item in row] for row in value.rows]


def _ref(name: str) -> ObjectRef:
    hexadecimal = hashlib.sha256(name.encode("ascii")).hexdigest()
    return ObjectRef(
        ScientificId(f"ebu:object:clcd:{name}"),
        SemanticVersion("1.0.0"),
        ObjectContentHash.from_hex(hexadecimal),
    )


def _protocol(*, missing_output: str | None = None) -> ebu.ClosedLoopCorrectionProtocol:
    contract = _strict_json(CONTRACT_PATH)
    outputs = tuple(contract["required_outputs"])  # type: ignore[index]
    if missing_output is not None:
        outputs = tuple(value for value in outputs if value != missing_output)
    nonclaims = tuple(contract["mandatory_nonclaims"])  # type: ignore[index]
    values = {
        name: _ref(name)
        for name in (
            "protocol",
            "physical-state",
            "scientific-state",
            "correction-state",
            "units-signs",
            "boundary",
            "clock-horizon",
            "initial-state",
            "parameter-domain",
            "uncorrected",
            "corrected",
            "coordinate",
            "embedding",
            "projection",
            "observation",
            "correction-law",
            "delay",
            "constraint",
            "numerical-method",
            "precision",
            "lifecycle",
            "closure",
            "dependency",
        )
    }
    return ebu.ClosedLoopCorrectionProtocol(
        protocol_ref=values["protocol"],
        protocol_version=SemanticVersion("1.0.0"),
        model_class=ebu.ClosedLoopModelClass.CONTINUOUS_LINEAR,
        physical_state_ref=values["physical-state"],
        scientific_state_ref=values["scientific-state"],
        correction_state_ref=values["correction-state"],
        units_and_signs_ref=values["units-signs"],
        boundary_ref=values["boundary"],
        clock_and_horizon_ref=values["clock-horizon"],
        initial_state_domain_ref=values["initial-state"],
        parameter_domain_ref=values["parameter-domain"],
        uncorrected_dynamics_ref=values["uncorrected"],
        corrected_dynamics_ref=values["corrected"],
        coordinate_contract_ref=values["coordinate"],
        embedding_ref=values["embedding"],
        projection_ref=values["projection"],
        observation_ref=values["observation"],
        correction_law_ref=values["correction-law"],
        delay_model_ref=values["delay"],
        constraint_and_saturation_ref=values["constraint"],
        numerical_method_ref=values["numerical-method"],
        precision_and_tolerance_ref=values["precision"],
        required_outputs=outputs,
        falsifiers=("TRAJECTORY_DIFFERENCE_ZERO", "CLOSURE_FAILURE"),
        correction_lifecycle_ref=values["lifecycle"],
        closure_contract_ref=values["closure"],
        dependency_contract_ref=values["dependency"],
        claim_status=ebu.CorrectionDiagnosticClaimStatus.STATIC_CONTROL,
        nonclaims=nonclaims,
    )


def _claim() -> ClaimStatus:
    return ClaimStatus.MODEL_DEPENDENT_RESULT


class ClosedLoopCorrectionDiagnosticsTests(unittest.TestCase):
    def test_fixture_identity_and_authority_projection(self) -> None:
        fixture_bytes = FIXTURE_PATH.read_bytes()
        validation = _strict_json(VALIDATION_PATH)
        fixture = _strict_json(FIXTURE_PATH)
        self.assertEqual(
            (len(fixture_bytes), hashlib.sha256(fixture_bytes).hexdigest()),
            (
                validation["fixture_projection"]["raw_bytes"],  # type: ignore[index]
                validation["fixture_projection"]["sha256"],  # type: ignore[index]
            ),
        )
        self.assertEqual(fixture["vectors"], validation["vectors"])  # type: ignore[index]
        self.assertEqual(len(fixture["vectors"]), 34)  # type: ignore[arg-type,index]
        self.assertTrue(
            AUTHORITY_PATH.read_text(encoding="utf-8").rstrip().endswith(
                "CLOSED_LOOP_CORRECTION_DIAGNOSTICS_IMPLEMENTATION_AUTHORITY_READY"
            )
        )

    def test_exact_public_surface_and_inert_graph(self) -> None:
        contract = _strict_json(CONTRACT_PATH)
        enum_names = [row["name"] for row in contract["closed_enums"]]  # type: ignore[index]
        schema_rows = contract["public_schemas"]  # type: ignore[index]
        callable_rows = contract["public_callables"]  # type: ignore[index]
        for name in enum_names:
            self.assertTrue(issubclass(getattr(ebu, name), str))
        for row in schema_rows:
            cls = getattr(ebu, row["name"])
            self.assertTrue(is_dataclass(cls), row["name"])
            self.assertTrue(cls.__dataclass_params__.frozen)
            self.assertEqual(
                [field.name for field in fields(cls)],
                [field[0] for field in row["fields"]],
            )
            self.assertEqual(
                [str(field.type).replace("'", "") for field in fields(cls)],
                [field[1] for field in row["fields"]],
            )
        for name, signature in callable_rows:
            normalized = str(inspect.signature(getattr(ebu, name))).replace("'", "")
            self.assertEqual(normalized, signature)
        error_tree = ast.parse((ROOT / "src/ebu_framework/errors.py").read_text())
        failure_names: list[str] = []
        for node in error_tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "FailureCode":
                failure_names = [
                    item.targets[0].id
                    for item in node.body
                    if isinstance(item, ast.Assign)
                    and isinstance(item.targets[0], ast.Name)
                ]
        self.assertEqual(len(failure_names), 294)
        self.assertEqual(failure_names[-14:], contract["failure_suffix"])
        self.assertEqual(len(ebu.__all__), 471)
        self.assertEqual(list(ebu.__all__[-27:]), contract["root_export_suffix"])
        source_root = ROOT / "src/ebu_framework"
        modules = {path.stem for path in source_root.glob("*.py")}
        edges: set[tuple[str, str]] = set()
        for path in source_root.glob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.level:
                    if node.module:
                        target = node.module.split(".", 1)[0]
                        if target in modules:
                            edges.add((path.stem, target))
                    else:
                        for alias in node.names:
                            target = alias.name.split(".", 1)[0]
                            if target in modules:
                                edges.add((path.stem, target))
        self.assertEqual((len(modules), len(edges)), (43, 298))
        expected_new = {
            ("correction_protocol", "identity"),
            ("correction_protocol", "numeric"),
            ("correction_protocol", "primitives"),
            ("correction_protocol", "errors"),
            ("correction_diagnostics", "correction_protocol"),
            ("correction_diagnostics", "numeric"),
            ("correction_diagnostics", "errors"),
            ("__init__", "correction_protocol"),
            ("__init__", "correction_diagnostics"),
        }
        self.assertTrue(expected_new <= edges)
        forbidden = set(contract["import_boundary"]["forbidden_reachability"])  # type: ignore[index]
        adjacency = {name: set() for name in modules}
        for source, target in edges:
            adjacency[source].add(target)
        reachable = set()
        frontier = ["correction_protocol", "correction_diagnostics"]
        while frontier:
            source = frontier.pop()
            for target in adjacency[source]:
                if target not in reachable:
                    reachable.add(target)
                    frontier.append(target)
        self.assertFalse(reachable & forbidden)
        for path in (
            source_root / "correction_protocol.py",
            source_root / "correction_diagnostics.py",
        ):
            text = path.read_text()
            for token in (
                "model_callback",
                "matrix_exp",
                "scipy",
                "numpy",
                "subprocess",
                "socket",
                "sqlite",
                "open(",
                "Path(",
            ):
                self.assertNotIn(token, text)

    def test_all_frozen_vectors(self) -> None:
        vectors = _strict_json(FIXTURE_PATH)["vectors"]  # type: ignore[index]
        calls = 0
        formations = 0
        for vector in vectors:
            if vector["exercise_class"] == "STATIC":
                self.assertEqual(vector["model_steps"], 0)
                continue
            expected_failure = vector["expected"].get("first_failure")
            try:
                result = self._execute(vector)
            except FrameworkError as error:
                self.assertEqual(error.envelope.failure_code.value, expected_failure)
                result = None
            else:
                self.assertIsNone(expected_failure)
                self._assert_result(vector, result)
            if vector["exercise_class"] == "FORMATION":
                formations += 1
            else:
                calls += 1
        self.assertEqual((calls, formations), (29, 2))

    def _execute(self, vector: dict[str, object]) -> object:
        identifier = vector["vector_id"]
        data = vector["input"]
        if identifier == "CLCD-B-V002":
            declaration = _protocol()
            result = ebu.validate_closed_loop_correction_protocol(declaration)
            self.assertIs(result, declaration)
            return result
        if identifier == "CLCD-B-V003":
            return ebu.validate_closed_loop_correction_protocol(
                _protocol(missing_output="RECOVERY_TIME")
            )
        if identifier == "CLCD-B-V004":
            return _matrix(data["rows"])
        if identifier in {"CLCD-B-V005", "CLCD-B-V006"}:
            declaration = ebu.CoordinateConjugacyDeclaration(
                action_ids=tuple(data["action_ids"]),
                subset_order=tuple(tuple(row) for row in data["subset_order"]),
                zeta=_matrix(data["zeta"]),
                mobius=_matrix(data["mobius"]),
                extent_basis_ref=_ref("extent-basis"),
                claim_status=_claim(),
            )
            return ebu.validate_coordinate_conjugacy(declaration, _matrix(data["a_e"]))
        if identifier in {"CLCD-B-V007", "CLCD-B-V008", "CLCD-B-V009"}:
            declaration = ebu.FeedbackBlockDeclaration(
                a=_matrix(data["a"]),
                b=_matrix(data["b"]),
                c=_matrix(data["c"]),
                d=_matrix(data["d"]),
                claim_status=_claim(),
            )
            return ebu.detect_feedback_path(declaration, data["max_order"])
        if "CLCD-B-V010" <= identifier <= "CLCD-B-V016":
            declaration = ebu.ContinuousFeedbackDeclaration(
                a=_rational(data["a"]),
                d=_rational(data["d"]),
                b=_rational(data["b"]),
                k=_rational(data["k"]),
                claim_status=_claim(),
            )
            return ebu.classify_continuous_feedback(declaration)
        if "CLCD-B-V017" <= identifier <= "CLCD-B-V025":
            declaration = ebu.DiscreteFeedbackDeclaration(
                model_class=ebu.ClosedLoopModelClass(data["model_class"]),
                kappa=_rational(data["kappa"]),
                claim_status=_claim(),
            )
            return ebu.classify_discrete_feedback(declaration)
        if identifier == "CLCD-B-V026":
            declaration = ebu.ObservabilityDeclaration(
                observation=_matrix(data["observation"]),
                modes=tuple(_matrix(value) for value in data["modes"]),
                claim_status=_claim(),
            )
            return ebu.evaluate_observability(declaration)
        if identifier in {"CLCD-B-V027", "CLCD-B-V028", "CLCD-B-V029"}:
            base = {
                "stock_change": _rational(data.get("stock_change", "0")),
                "boundary_in": _rational(data.get("boundary_in", "0")),
                "boundary_out": _rational(data.get("boundary_out", "0")),
                "generation": _rational(data.get("generation", "0")),
                "consumption": _rational(data.get("consumption", "0")),
                "residual": _rational(data.get("residual", "0")),
                "internal_transfers": tuple(
                    (_rational(left), _rational(right))
                    for left, right in data["internal_transfers"]
                ),
                "claim_status": _claim(),
            }
            declaration = ebu.CorrectionClosureDeclaration(**base)
            return ebu.evaluate_correction_closure(declaration)
        if identifier in {"CLCD-B-V030", "CLCD-B-V031", "CLCD-B-V032"}:
            declaration = ebu.DependencyGraphDeclaration(
                vertices=tuple(data["vertices"]),
                edges=tuple(tuple(value) for value in data["edges"]),
                corrected_vertex=data["corrected_vertex"],
                inventory_complete=data["inventory_complete"],
                claim_status=_claim(),
            )
            return ebu.compute_dependency_invalidation(declaration)
        raise AssertionError(identifier)

    def _assert_result(self, vector: dict[str, object], result: object) -> None:
        identifier = vector["vector_id"]
        expected = vector["expected"]
        if identifier == "CLCD-B-V002":
            self.assertIsInstance(result, ebu.ClosedLoopCorrectionProtocol)
        elif identifier == "CLCD-B-V005":
            self.assertEqual(_matrix_text(result), expected["a_i"])
        elif identifier in {"CLCD-B-V007", "CLCD-B-V008", "CLCD-B-V009"}:
            self.assertEqual(_matrix_text(result.bc), expected["bc"])
            self.assertEqual(
                result.first_nonzero_order.value
                if type(result.first_nonzero_order) is ebu.Applicability
                else result.first_nonzero_order,
                expected["first_nonzero_order"],
            )
            if "first_nonzero_operator" in expected:
                self.assertEqual(
                    _matrix_text(result.first_nonzero_operator),
                    expected["first_nonzero_operator"],
                )
        elif "CLCD-B-V010" <= identifier <= "CLCD-B-V016":
            self.assertEqual(_text(result.s), expected["s"])
            self.assertEqual(_text(result.q), expected["q"])
            self.assertEqual(_text(result.discriminant), expected["discriminant"])
            self.assertEqual(result.regime.value, expected["regime"])
        elif "CLCD-B-V017" <= identifier <= "CLCD-B-V025":
            self.assertEqual(result.regime.value, expected["regime"])
            for field in ("immediate_root", "discriminant", "root_modulus_squared"):
                if field in expected:
                    self.assertEqual(_text(getattr(result, field)), expected[field])
        elif identifier == "CLCD-B-V026":
            self.assertEqual(list(result.visible), expected["visible"])
            self.assertEqual(
                [_matrix_text(value) for value in result.projected_modes],
                expected["projected_modes"],
            )
        elif identifier in {"CLCD-B-V027", "CLCD-B-V028"}:
            self.assertEqual(_text(result.closure_rhs), expected["closure_rhs"])
            self.assertEqual(result.closes, expected["closes"])
            self.assertEqual(
                result.internal_transfers_cancel,
                expected["internal_transfers_cancel"],
            )
        elif identifier == "CLCD-B-V030":
            self.assertEqual(list(result.descendants), expected["descendants"])
            self.assertEqual(list(result.topological_order), expected["topological_order"])


if __name__ == "__main__":
    unittest.main()
