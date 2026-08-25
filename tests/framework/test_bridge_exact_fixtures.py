from __future__ import annotations

import ast
import copy
from dataclasses import fields, replace
from fractions import Fraction
import hashlib
import inspect
import json
from pathlib import Path
import pickle
import unittest

import ebu_framework
from ebu_framework import bridge, capabilities, canonical, errors, hashing
from ebu_framework.actions import EffectiveInterval
from ebu_framework.causal import CausalIdentificationStatus
from ebu_framework.identity import ObjectContentHash, ObjectRef, SourceFileRawSha256
from ebu_framework.numeric import IntegerV1
from ebu_framework.scheduling import ComparatorKind


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "tests/framework/fixtures/bridge_m1_m9_v1.json"
CONTRACT_PATH = ROOT / "unified_python_research_framework_i6_contract.json"
VALIDATION_PATH = (
    ROOT / "unified_python_research_framework_i6_validation_contract.json"
)
PREDECESSOR_SIGNATURE_PATH = (
    ROOT / "post_i5_legacy_test_compatibility_contract.json"
)
FIXTURE_RELATIVE_PATH = "tests/framework/fixtures/bridge_m1_m9_v1.json"
FIXTURE_SHA256 = "8768b2f976b3b928b90c3b6d4b6d141de75fd5873fb52d61048748bf054779af"
FIXTURE_BLOB = "e3b5593ed5a58835be8a43560dc648bf2e4253f9"


def _canonical_json_lf(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def _git_blob(raw: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw,
        usedforsecurity=False,
    ).hexdigest()


def _fraction(value: object) -> Fraction:
    projected = value.to_ecj1()  # type: ignore[union-attr]
    variant = projected["variant"]
    if variant == "INTEGER_V1":
        return Fraction(projected["value"])
    if variant == "RATIONAL_V1":
        return Fraction(projected["numerator"], projected["denominator"])
    if variant == "DECIMAL_V1":
        coefficient = projected["coefficient"]
        exponent = projected["exponent10"]
        return (
            Fraction(coefficient * 10**exponent)
            if exponent >= 0
            else Fraction(coefficient, 10 ** (-exponent))
        )
    bits = int(projected["bits"], 16)
    sign = -1 if bits >> 63 else 1
    exponent_bits = (bits >> 52) & 0x7FF
    fraction_bits = bits & ((1 << 52) - 1)
    if exponent_bits == 0:
        significand, exponent = fraction_bits, -1074
    else:
        significand = (1 << 52) | fraction_bits
        exponent = exponent_bits - 1023 - 52
    return (
        Fraction(sign * significand * 2**exponent)
        if exponent >= 0
        else Fraction(sign * significand, 2 ** (-exponent))
    )


def _ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _project_applicability(value: object) -> object:
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if isinstance(value, errors.Applicability):
        return value.value
    return value


def _bundle_projections(record: object) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    envelope = record.envelope  # type: ignore[attr-defined]
    payload = record.to_ecj1()  # type: ignore[attr-defined]
    payload_bytes = canonical.encode_ecj1(payload)
    constructor = {
        "authority_refs": [item.to_ecj1() for item in envelope.authority_refs],
        "lifecycle_status": envelope.lifecycle_status.value,
        "object_content_hash": str(envelope.object_content_hash),
        "object_content_payload": {
            "byte_count": len(payload_bytes),
            "constructor": "CanonicalBytes",
            "ecj1_value": payload,
            "sha256": hashlib.sha256(payload_bytes).hexdigest(),
        },
        "object_id": str(envelope.object_id),
        "object_kind_id": str(envelope.object_kind_id),
        "object_version": str(envelope.object_version),
        "record_metadata_ref": _project_applicability(envelope.record_metadata_ref),
        "schema_id": str(envelope.schema_id),
        "schema_version": str(envelope.schema_version),
        "supersedes_ref": _project_applicability(envelope.supersedes_ref),
    }
    preimage = {
        "authority_refs": constructor["authority_refs"],
        "hash_domain": "ebu.object-content.v1",
        "object_content_payload": payload,
        "object_id": constructor["object_id"],
        "object_kind": constructor["object_kind_id"],
        "object_version": constructor["object_version"],
        "schema_id": constructor["schema_id"],
        "schema_version": constructor["schema_version"],
        "supersedes_ref": (
            None
            if envelope.supersedes_ref is errors.Applicability.NOT_APPLICABLE
            else envelope.supersedes_ref.to_ecj1()
        ),
    }
    return constructor, preimage, _ref(record).to_ecj1()


def _record_bundle(record: object) -> dict[str, object]:
    constructor, preimage, reference = _bundle_projections(record)
    return {
        "envelope_constructor": constructor,
        "object_content_hash_preimage": preimage,
        "object_ref": reference,
        "to_ecj1": record.to_ecj1(),  # type: ignore[attr-defined]
    }


def _bundle_with_payload_field(
    bundle: dict[str, object], field_name: str, value: object
) -> dict[str, object]:
    result = copy.deepcopy(bundle)
    envelope = bridge._envelope(bundle)
    payload = result["to_ecj1"]
    payload[field_name] = value
    payload_bytes = canonical.encode_ecj1(payload)
    constructor = result["envelope_constructor"]
    constructor["object_content_payload"] = {
        "byte_count": len(payload_bytes),
        "constructor": "CanonicalBytes",
        "ecj1_value": payload,
        "sha256": hashlib.sha256(payload_bytes).hexdigest(),
    }
    content_hash = hashing.compute_object_content_hash(
        object_id=envelope.object_id,
        object_kind=str(envelope.object_kind_id),
        schema_id=envelope.schema_id,
        schema_version=envelope.schema_version,
        object_version=envelope.object_version,
        authority_refs=envelope.authority_refs,
        supersedes_ref=None,
        object_content_payload=payload,
    )
    constructor["object_content_hash"] = str(content_hash)
    result["object_content_hash_preimage"] = {
        "authority_refs": constructor["authority_refs"],
        "hash_domain": "ebu.object-content.v1",
        "object_content_payload": payload,
        "object_id": constructor["object_id"],
        "object_kind": constructor["object_kind_id"],
        "object_version": constructor["object_version"],
        "schema_id": constructor["schema_id"],
        "schema_version": constructor["schema_version"],
        "supersedes_ref": None,
    }
    result["object_ref"]["object_content_hash"] = str(content_hash)
    return result


def _signature_parameter_names(signature: str) -> tuple[str, ...]:
    content = signature[1 : signature.rfind(") ->")]
    segments: list[str] = []
    start = 0
    depth = 0
    quote = ""
    for index, character in enumerate(content):
        if quote:
            if character == quote:
                quote = ""
        elif character in {"'", '"'}:
            quote = character
        elif character in "[({":
            depth += 1
        elif character in "]) }".replace(" ", ""):
            depth -= 1
        elif character == "," and depth == 0:
            segments.append(content[start:index].strip())
            start = index + 1
    segments.append(content[start:].strip())
    return tuple(
        segment.split(":", 1)[0].strip()
        for segment in segments
        if segment not in {"/", "*"} and ":" in segment
    )


class BridgeExactFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        cls.validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
        cls.predecessor = json.loads(
            PREDECESSOR_SIGNATURE_PATH.read_text(encoding="utf-8")
        )
        cls.raw = FIXTURE_PATH.read_bytes()
        cls.document = canonical.parse_ecj1(cls.raw[:-1])
        cls.cases = {
            row["case_id"]: row
            for row in cls.document["case_materializations"]
        }
        cls.raw_hash = SourceFileRawSha256("sha256-raw:" + FIXTURE_SHA256)
        assignments = cls.validation["failure_identity_contract"][
            "vector_coordinate_assignments"
        ]
        cls.assignments = {row["vector_id"]: row for row in assignments}

    def _issue(self, case_id: str, interface: str) -> capabilities.T2FixtureCapability:
        return capabilities._issue_t2_fixture_capability(
            fixture_path=FIXTURE_RELATIVE_PATH,
            fixture_raw_sha256=self.raw_hash,
            case_id=case_id,
            authorized_interface=interface,
        )

    def _assert_vector_failure(self, vector_id: str, operation: object) -> None:
        assignment = self.assignments[vector_id]
        with self.assertRaises(errors.FrameworkError) as raised:
            operation()  # type: ignore[operator]
        envelope = raised.exception.envelope
        provenance = assignment["materialization_provenance"]
        expected_interface = provenance["owning_interface_ref"]
        self.assertEqual(envelope.failure_code.value, assignment["expected_first_failure"])
        self.assertEqual(str(envelope.failure_id), assignment["derived_failure_id"])
        self.assertEqual(envelope.stage, errors.FailureStage.I6)
        self.assertEqual(envelope.state_advance, errors.StateAdvance.NONE)
        self.assertEqual(envelope.interface_ref.to_ecj1(), expected_interface)

    def _graphs(self) -> dict[str, dict[str, object]]:
        return {
            case_id: bridge._materialize_fixture_case(case)
            for case_id, case in self.cases.items()
        }

    def test_frozen_fixture_identity_and_strict_json_controls(self) -> None:
        identity = self.validation["fixture_inventory"]["future_identity"]
        self.assertEqual(len(self.raw), 3_505_514)
        self.assertEqual(hashlib.sha256(self.raw).hexdigest(), FIXTURE_SHA256)
        self.assertEqual(_git_blob(self.raw), FIXTURE_BLOB)
        self.assertEqual(identity["byte_count"], len(self.raw))
        self.assertEqual(identity["raw_sha256"], FIXTURE_SHA256)
        self.assertEqual(identity["git_blob"], FIXTURE_BLOB)
        self.assertEqual(
            self.document, self.contract["matrix"]["future_fixture_document"]
        )
        self.assertEqual(
            self.document,
            self.validation["fixture_inventory"]["future_fixture_document"],
        )
        self.assertTrue(self.raw.endswith(b"\n"))
        self.assertFalse(self.raw.endswith(b"\n\n"))
        self.assertNotIn(b"\r", self.raw)
        self.assertNotIn(b"\xef\xbb\xbf", self.raw[:3])
        self.assertEqual(canonical.encode_ecj1(self.document) + b"\n", self.raw)
        with self.assertRaises(errors.FrameworkError):
            canonical.parse_ecj1(b'{"duplicate":1,"duplicate":2}')
        for token in (b"NaN", b"Infinity", b"-Infinity"):
            with self.subTest(token=token):
                with self.assertRaises(errors.FrameworkError):
                    canonical.parse_ecj1(b'{"nonfinite":' + token + b"}")

    def test_all_36_positive_interface_row_vectors(self) -> None:
        vectors = self.validation["fixture_inventory"]["positive_vectors"]
        self.assertEqual(len(vectors), 36)
        held_outputs: list[object] = []
        for vector in vectors:
            with self.subTest(vector=vector["vector_id"]):
                interface = vector["interface"]
                result = getattr(bridge, interface)(
                    self.raw,
                    self._issue(vector["case_id"], interface),
                )
                expected = self.cases[vector["case_id"]][
                    "interface_expected_outputs"
                ][interface]
                if type(result) is tuple:
                    actual = [_record_bundle(item) for item in result]
                else:
                    actual = _record_bundle(result)
                self.assertEqual(actual, expected)
                projection = canonical.encode_ecj1(actual) + b"\n"
                self.assertEqual(
                    len(projection), vector["expected_output_projection_byte_count"]
                )
                self.assertEqual(
                    hashlib.sha256(projection).hexdigest(),
                    vector["expected_output_projection_sha256"],
                )
                self.assertFalse(hasattr(result, "system_state"))
                held_outputs.append(result)
        self.assertEqual(len(held_outputs), 36)

    def test_static_group_measurement_settlement_fields_fail_closed(self) -> None:
        graph = bridge._materialize_fixture_case(self.cases["M1"])
        measurement = graph["measurement"]
        reconstructed = bridge._group_measurement(
            copy.deepcopy(self.cases["M1"]["group_measurement_record"])
        )
        self.assertEqual(reconstructed, measurement)
        self.assertEqual(
            reconstructed.measurement_kind,
            "STATIC_SEPARATE_ACTION_AGGREGATE_WITNESS",
        )

        zero = replace(measurement.ebu_value, magnitude=IntegerV1(0))
        present_arm = {
            "settlement_rule_ref": measurement.before_state_ref.to_ecj1(),
            "settlement_share_refs": [measurement.endpoint_state_ref.to_ecj1()],
            "settlement_share_values": [measurement.ebu_value.to_ecj1()],
            "settlement_residual_value": zero.to_ecj1(),
            "settlement_residual_account_refs": [measurement.horizon_ref.to_ecj1()],
            "settlement_validation_provenance_ref": (
                measurement.endpoint_evaluation_ref.to_ecj1()
            ),
        }
        mutations = [
            (field_name, {field_name: value})
            for field_name, value in present_arm.items()
        ] + [("complete_settlement_present_arm", present_arm)]
        expected_failure_id = (
            "ebu:failure:core:sha256-"
            "5cfb1de38843b0ed4fdc5b9869ee2664e72c4515b3037a7fc3a5ce3158632f87"
        )
        expected_interface = errors.FailureInterfaceRef(
            "ebu_framework.bridge", "GroupMeasurement", "1.0.0"
        )

        for mutation_name, changes in mutations:
            bundle = copy.deepcopy(
                self.cases["M1"]["group_measurement_record"]
            )
            for field_name, value in changes.items():
                bundle = _bundle_with_payload_field(bundle, field_name, value)
            with self.subTest(mutation=mutation_name):
                with self.assertRaises(errors.FrameworkError) as raised:
                    bridge._group_measurement(bundle)
                envelope = raised.exception.envelope
                self.assertEqual(
                    envelope.failure_code,
                    errors.FailureCode.I6_RECORD_FORMATION_INVALID,
                )
                self.assertEqual(str(envelope.failure_id), expected_failure_id)
                self.assertEqual(envelope.stage, errors.FailureStage.I6)
                self.assertEqual(envelope.state_advance, errors.StateAdvance.NONE)
                self.assertEqual(envelope.interface_ref, expected_interface)

    def test_physical_settlement_and_causal_arms_remain_unchanged(self) -> None:
        graph = bridge._materialize_fixture_case(self.cases["M2"])
        original = graph["measurement"]
        reconstructed = bridge._group_measurement(
            copy.deepcopy(self.cases["M2"]["group_measurement_record"])
        )
        self.assertEqual(reconstructed, original)
        self.assertEqual(reconstructed.measurement_kind, "PHYSICAL_JOINT_GROUP")
        self.assertIsInstance(reconstructed.physical_measurement_ref, ObjectRef)
        self.assertIs(
            reconstructed.causal_status,
            CausalIdentificationStatus.UNIDENTIFIED,
        )
        self.assertEqual(reconstructed.causal_contribution_refs, ())

        zero = replace(original.ebu_value, magnitude=IntegerV1(0))
        settlement_fields = {
            "settlement_rule_ref": original.before_state_ref.to_ecj1(),
            "settlement_share_refs": [original.endpoint_state_ref.to_ecj1()],
            "settlement_share_values": [original.ebu_value.to_ecj1()],
            "settlement_residual_value": zero.to_ecj1(),
            "settlement_residual_account_refs": [original.horizon_ref.to_ecj1()],
            "settlement_validation_provenance_ref": (
                original.endpoint_evaluation_ref.to_ecj1()
            ),
        }
        settled_bundle = copy.deepcopy(
            self.cases["M2"]["group_measurement_record"]
        )
        for field_name, value in settlement_fields.items():
            settled_bundle = _bundle_with_payload_field(
                settled_bundle, field_name, value
            )
        settled = bridge._group_measurement(settled_bundle)
        self.assertEqual(settled.measurement_kind, "PHYSICAL_JOINT_GROUP")
        self.assertIs(settled.causal_status, CausalIdentificationStatus.UNIDENTIFIED)
        self.assertEqual(settled.settlement_share_values, (original.ebu_value,))
        self.assertEqual(_fraction(settled.settlement_residual_value.magnitude), 0)
        self.assertEqual(
            _fraction(settled.settlement_share_values[0].magnitude)
            + _fraction(settled.settlement_residual_value.magnitude),
            _fraction(settled.ebu_value.magnitude),
        )

        invalid_bundle = _bundle_with_payload_field(
            settled_bundle,
            "settlement_residual_value",
            original.ebu_value.to_ecj1(),
        )
        with self.assertRaises(errors.FrameworkError) as raised:
            bridge._group_measurement(invalid_bundle)
        envelope = raised.exception.envelope
        self.assertEqual(
            envelope.failure_code,
            errors.FailureCode.SETTLEMENT_CLOSURE_FAILURE,
        )
        self.assertEqual(
            str(envelope.failure_id),
            "ebu:failure:core:sha256-"
            "fa7e430b7d1a4391266d4f259bbae7c78b80699df2c251e973b546b689034b63",
        )
        self.assertEqual(
            envelope.interface_ref,
            errors.FailureInterfaceRef(
                "ebu_framework.bridge", "GroupMeasurement", "1.0.0"
            ),
        )

    def test_exact_80_arithmetic_assertions_and_batching_witness(self) -> None:
        graphs = self._graphs()
        assertion_count = 0

        def exact(left: Fraction, right: Fraction) -> None:
            nonlocal assertion_count
            self.assertEqual(left, right)
            assertion_count += 1

        for case_id in self.cases:
            measurement = graphs[case_id]["measurement"]
            exact(
                _fraction(measurement.ebu_value.magnitude),
                _fraction(measurement.initial_distortion.magnitude)
                - _fraction(measurement.endpoint_distortion.magnitude),
            )
        for case_id in tuple(self.cases)[:-1]:
            nonadditivity = graphs[case_id]["nonadditivity"]
            exact(
                _fraction(nonadditivity.nonadditivity_value.magnitude),
                _fraction(nonadditivity.joint_value.magnitude)
                - sum(
                    (_fraction(item.magnitude) for item in nonadditivity.singleton_values),
                    Fraction(0),
                ),
            )
        for case_id in self.cases:
            measurement = graphs[case_id]["measurement"]
            for interaction in graphs[case_id]["interactions"]:
                interaction_value = _fraction(interaction.interaction_value.magnitude)
                exact(
                    interaction_value,
                    _fraction(interaction.group_ebu.magnitude)
                    - _fraction(interaction.sequential_ebu.magnitude),
                )
                exact(
                    interaction_value,
                    _fraction(interaction.sequential_distortion.magnitude)
                    - _fraction(interaction.group_distortion.magnitude),
                )
                exact(
                    _fraction(interaction.sequential_ebu.magnitude),
                    _fraction(measurement.initial_distortion.magnitude)
                    - _fraction(interaction.sequential_distortion.magnitude),
                )
        headline_ebu = {
            "M1": Fraction(8),
            "M2": Fraction(15, 2),
            "M3": Fraction(15),
            "M4": Fraction(8),
            "M5": Fraction(5),
            "M6": Fraction(-2),
            "M7": Fraction(4),
            "M8": Fraction(-45, 4),
            "M9": Fraction(4),
        }
        for case_id, expected in headline_ebu.items():
            exact(
                _fraction(graphs[case_id]["measurement"].ebu_value.magnitude),
                expected,
            )
        self.assertEqual(assertion_count, 80)

        headline_nonadditivity = {
            "M1": Fraction(0),
            "M2": Fraction(0),
            "M3": Fraction(-4),
            "M4": Fraction(8),
            "M5": Fraction(-3),
            "M6": Fraction(2),
            "M7": Fraction(-4),
            "M8": Fraction(-21, 4),
        }
        for case_id, expected in headline_nonadditivity.items():
            self.assertEqual(
                _fraction(
                    graphs[case_id]["nonadditivity"].nonadditivity_value.magnitude
                ),
                expected,
            )
        self.assertEqual(
            Fraction(
                self.cases["M6"]["input_program"]["state_construction"][
                    "distortion"
                ]["lambda"]
            ),
            Fraction(1),
        )

        m2 = graphs["M2"]
        m2_values = {
            (item.replay_kind, tuple(str(ref.object_id) for ref in item.ordering_refs)):
            _fraction(item.interaction_value.magnitude)
            for item in m2["interactions"]
        }
        self.assertEqual(sorted(set(m2_values.values())), [Fraction(0), Fraction(1, 2)])
        self.assertEqual(
            _fraction(graphs["M6"]["nonadditivity"].nonadditivity_value.magnitude),
            Fraction(2),
        )
        m8_interactions = tuple(
            _fraction(item.interaction_value.magnitude)
            for item in graphs["M8"]["interactions"]
        )
        self.assertEqual(m8_interactions, (Fraction(-13, 4), Fraction(15, 4)))
        m9 = graphs["M9"]
        self.assertIsInstance(m9["refusal"], bridge.NonserializableGroup)
        self.assertIs(
            m9["nonadditivity"].nonadditivity_value,
            errors.Applicability.NOT_APPLICABLE,
        )
        self.assertEqual(m9["interactions"], ())

        batching = self.validation["fixture_inventory"][
            "receipt_batching_static_witness"
        ]
        self.assertEqual(Fraction(9) - Fraction(6), Fraction(3))
        self.assertEqual((3 - 1) * Fraction(2) - Fraction(1), Fraction(3))
        self.assertFalse(batching["physical_ebu_participation"])

    def test_exact_148_construction_and_159_identity_reconstructions(self) -> None:
        graphs = self._graphs()
        representatives = {
            "DependencyEdge": graphs["M2"]["edges"][0],
            "JointTransitionGroup": graphs["M2"]["group"],
            "AdmissibleComparatorSet": graphs["M2"]["comparator_set"],
            "GroupMeasurement": graphs["M2"]["measurement"],
            "SameBaselineNonadditivity": graphs["M2"]["nonadditivity"],
            "ComparatorInteraction": graphs["M2"]["interactions"][0],
            "NonserializableGroup": graphs["M9"]["refusal"],
        }
        construction_count = 0
        type_rows = {
            row["name"]: row
            for row in self.contract["public_types"]["rows"]
            if row["owner"] == "bridge"
        }
        for name, record in representatives.items():
            row = type_rows[name]
            self.assertEqual(list(record.__dataclass_fields__), row["field_order"])
            for field_name in row["field_order"]:
                self.assertTrue(hasattr(record, field_name))
                construction_count += 1
            record_type = type(record)
            self.assertTrue(record_type.__dataclass_params__.frozen)
            construction_count += 1
            self.assertFalse(hasattr(record, "__dict__"))
            construction_count += 1
            self.assertTrue(
                all(
                    parameter.kind is inspect.Parameter.KEYWORD_ONLY
                    for parameter in inspect.signature(record_type).parameters.values()
                )
            )
            construction_count += 1
        m2 = graphs["M2"]
        link_assertions = (
            m2["measurement"].group_or_witness_ref == _ref(m2["group"]),
            m2["comparator_set"].group_or_witness_ref == _ref(m2["group"]),
            m2["nonadditivity"].group_or_witness_ref == _ref(m2["group"]),
            m2["receipt"].group_ref == _ref(m2["group"]),
            m2["receipt"].measurement_ref == _ref(m2["measurement"]),
            graphs["M9"]["refusal"].comparator_set_ref
            == _ref(graphs["M9"]["comparator_set"]),
        )
        for linked in link_assertions:
            self.assertTrue(linked)
            construction_count += 1
        self.assertEqual(construction_count, 148)

        records_and_bundles: list[tuple[object, dict[str, object]]] = []
        for case_id, case in self.cases.items():
            graph = graphs[case_id]
            if type(graph["group"]) is bridge.JointTransitionGroup:
                records_and_bundles.append((graph["group"], case["joint_group_record"]))
            records_and_bundles.extend(
                (
                    (graph["measurement"], case["group_measurement_record"]),
                    (
                        graph["nonadditivity"],
                        case["same_baseline_nonadditivity_record"],
                    ),
                )
            )
            if type(graph["refusal"]) is bridge.NonserializableGroup:
                records_and_bundles.append(
                    (graph["refusal"], case["nonserializable_group_record"])
                )
            else:
                records_and_bundles.extend(
                    zip(graph["interactions"], case["comparator_interaction_records"])
                )
            if graph["receipt"] is not errors.Applicability.NOT_APPLICABLE:
                records_and_bundles.append(
                    (graph["receipt"], case["accepted_group_receipt_record"])
                )
        self.assertEqual(len(records_and_bundles), 53)
        reconstruction_count = 0
        for record, bundle in records_and_bundles:
            constructor, preimage, reference = _bundle_projections(record)
            self.assertEqual(constructor, bundle["envelope_constructor"])
            reconstruction_count += 1
            self.assertEqual(preimage, bundle["object_content_hash_preimage"])
            reconstruction_count += 1
            self.assertEqual(reference, bundle["object_ref"])
            reconstruction_count += 1
        self.assertEqual(reconstruction_count, 159)

    def test_all_44_t2_capability_and_parse_refusals(self) -> None:
        vectors = [
            row
            for row in self.validation["fixture_inventory"]["negative_vectors"]
            if row["classification"] == "T2_CAPABILITY_OR_PARSE_REFUSAL"
        ]
        self.assertEqual(len(vectors), 44)
        other_interface = {
            "classify_joint_groups_fixture": "compute_group_measurement_fixture",
            "compute_group_measurement_fixture": "classify_joint_groups_fixture",
            "compute_same_baseline_nonadditivity_fixture": "classify_joint_groups_fixture",
            "compute_comparator_interaction_fixture": "classify_joint_groups_fixture",
        }
        for vector in vectors:
            interface = vector["owner_interface"]
            mutation = vector["single_mutation"]
            function = getattr(bridge, interface)

            def operation() -> None:
                if mutation == "DIRECT_CONSTRUCTION":
                    capabilities.T2FixtureCapability(authorized_interface=interface)
                elif mutation == "COPY":
                    copy.copy(self._issue("M1", interface))
                elif mutation == "PICKLE_OR_DESERIALIZE":
                    pickle.dumps(self._issue("M1", interface))
                elif mutation == "REUSE_AFTER_CONSUME":
                    capability = self._issue("M1", interface)
                    capabilities._consume_t2_fixture_capability(
                        capability, interface, "M1"
                    )
                    function(self.raw, capability)
                elif mutation == "WRONG_INTERFACE":
                    function(self.raw, self._issue("M1", other_interface[interface]))
                elif mutation == "WRONG_CASE":
                    capability = self._issue("M1", interface)
                    object.__setattr__(capability, "case_id", "M2")
                    function(self.raw, capability)
                elif mutation == "WRONG_FIXTURE_PATH":
                    capabilities._issue_t2_fixture_capability(
                        fixture_path="tests/framework/fixtures/not-authorized.json",
                        fixture_raw_sha256=self.raw_hash,
                        case_id="M1",
                        authorized_interface=interface,
                    )
                elif mutation == "WRONG_FIXTURE_RAW_HASH":
                    capabilities._issue_t2_fixture_capability(
                        fixture_path=FIXTURE_RELATIVE_PATH,
                        fixture_raw_sha256=SourceFileRawSha256(
                            "sha256-raw:" + "0" * 64
                        ),
                        case_id="M1",
                        authorized_interface=interface,
                    )
                elif mutation == "INPUT_RAW_HASH_MISMATCH":
                    changed = self.raw.replace(b'"fixture_version":"1.0.0"', b'"fixture_version":"1.0.1"', 1)
                    function(changed, self._issue("M1", interface))
                elif mutation == "DUPLICATE_JSON_KEY":
                    function(
                        b'{"fixture_id":"a","fixture_id":"b"}\n',
                        self._issue("M1", interface),
                    )
                elif mutation == "NONFINITE_JSON_TOKEN":
                    function(
                        b'{"nonfinite":NaN}\n', self._issue("M1", interface)
                    )
                else:  # pragma: no cover - closed by the authority inventory
                    self.fail(mutation)

            with self.subTest(vector=vector["vector_id"]):
                self._assert_vector_failure(vector["vector_id"], operation)

    def test_121_field_totality_and_49_formation_identity_vectors(self) -> None:
        graphs = self._graphs()
        representatives = {
            "DependencyEdge": graphs["M2"]["edges"][0],
            "JointTransitionGroup": graphs["M2"]["group"],
            "AdmissibleComparatorSet": graphs["M2"]["comparator_set"],
            "GroupMeasurement": graphs["M2"]["measurement"],
            "SameBaselineNonadditivity": graphs["M2"]["nonadditivity"],
            "ComparatorInteraction": graphs["M2"]["interactions"][0],
            "NonserializableGroup": graphs["M9"]["refusal"],
        }
        negatives = self.validation["fixture_inventory"]["negative_vectors"]
        totality = [row for row in negatives if row["classification"] == "RECORD_FIELD_TOTALITY"]
        formation = [
            row
            for row in negatives
            if row["classification"] == "RECORD_FORMATION_OR_IDENTITY_REFUSAL"
        ]
        self.assertEqual(len(totality), 121)
        self.assertEqual(len(formation), 49)

        for vector in totality:
            record = representatives[vector["owner_interface"]]
            record_type = type(record)
            field_name = vector["single_mutation"].split("=", 1)[0]
            kwargs = {field.name: getattr(record, field.name) for field in fields(record)}
            kwargs[field_name] = object()
            with self.subTest(vector=vector["vector_id"]):
                self._assert_vector_failure(
                    vector["vector_id"], lambda: record_type(**kwargs)
                )

        collection_field = {
            "DependencyEdge": "dependency_kinds",
            "JointTransitionGroup": "child_action_refs",
            "AdmissibleComparatorSet": "action_refs",
            "GroupMeasurement": "child_action_refs",
            "SameBaselineNonadditivity": "action_refs",
            "ComparatorInteraction": "ordering_refs",
            "NonserializableGroup": "action_refs",
        }
        for vector in formation:
            record = representatives[vector["owner_interface"]]
            record_type = type(record)
            mutation = vector["single_mutation"]
            kwargs = {field.name: getattr(record, field.name) for field in fields(record)}

            def operation() -> None:
                if mutation == "POSITIONAL_ARGUMENT":
                    record_type(*kwargs.values())
                elif mutation == "OMITTED_REQUIRED_FIELD":
                    reduced = dict(kwargs)
                    reduced.pop(next(iter(reduced)))
                    record_type(**reduced)
                elif mutation == "EXTRA_FIELD":
                    record_type(**kwargs, authority_extra=object())
                elif mutation == "ENVELOPE_OBJECT_CONTENT_HASH_MISMATCH":
                    altered = dict(kwargs)
                    altered["envelope"] = replace(
                        record.envelope,
                        object_content_hash=ObjectContentHash.from_hex("0" * 64),
                    )
                    record_type(**altered)
                elif mutation == "NON_NFC_STRING":
                    altered = dict(kwargs)
                    first = next(name for name in altered if name != "envelope")
                    altered[first] = "e\u0301"
                    record_type(**altered)
                elif mutation in {"UNSORTED_COLLECTION", "DUPLICATE_COLLECTION_MEMBER"}:
                    altered = dict(kwargs)
                    name = collection_field[vector["owner_interface"]]
                    current = altered[name]
                    if mutation == "UNSORTED_COLLECTION" and name == "dependency_kinds":
                        altered[name] = (
                            "SHARED_CONSTRAINT",
                            "SHARED_WRITE_SUPPORT",
                        )
                    else:
                        altered[name] = (
                            tuple(reversed(current))
                            if mutation == "UNSORTED_COLLECTION"
                            else (current[0], current[0])
                        )
                    record_type(**altered)
                else:  # pragma: no cover - closed by the authority inventory
                    self.fail(mutation)

            with self.subTest(vector=vector["vector_id"]):
                self._assert_vector_failure(vector["vector_id"], operation)

    def test_all_38_semantic_single_mutation_refusals(self) -> None:
        graphs = self._graphs()
        m2 = graphs["M2"]
        m8 = graphs["M8"]
        m9 = graphs["M9"]
        edge = m2["edges"][0]
        group = m2["group"]
        comparator_set = m2["comparator_set"]
        measurement = m2["measurement"]
        nonadditivity = m2["nonadditivity"]
        interaction = next(
            item
            for item in m2["interactions"]
            if _fraction(item.interaction_value.magnitude) == Fraction(1, 2)
        )
        refusal = m9["refusal"]
        receipt = m2["receipt"]
        zero = replace(measurement.ebu_value, magnitude=IntegerV1(0))
        other_ref = measurement.before_state_ref

        semantic = [
            row
            for row in self.validation["fixture_inventory"]["negative_vectors"]
            if row["classification"] == "SEMANTIC_SINGLE_MUTATION_REFUSAL"
        ]
        self.assertEqual(len(semantic), 38)

        def nonoverlapping_edge() -> None:
            right = EffectiveInterval(
                start=edge.left_effective_interval.end,
                end=edge.right_effective_interval.end,
                clock_ref=edge.right_effective_interval.clock_ref,
            )
            replace(edge, right_effective_interval=right)

        def ungrouped_without_evidence() -> None:
            changes = {
                "child_action_refs": group.child_action_refs[:1],
                "child_effective_intervals": group.child_effective_intervals[:1],
                "child_write_supports": group.child_write_supports[:1],
                "child_constraint_supports": group.child_constraint_supports[:1],
                "child_commitment_refs": group.child_commitment_refs[:1],
                "accepted_quantity_refs": group.accepted_quantity_refs[:1],
                "dependency_edges": (),
                "separability_evidence_ref": errors.Applicability.NOT_APPLICABLE,
            }
            replace(group, **changes)

        def nonsequential_comparator() -> None:
            schedule = replace(
                comparator_set.comparator_schedules[0],
                comparator_kind=ComparatorKind.OPEN_LOOP_REFERENCE,
            )
            replace(
                comparator_set,
                comparator_schedules=(schedule,) + comparator_set.comparator_schedules[1:],
            )

        def comparator_baseline_mismatch() -> None:
            schedule = replace(
                comparator_set.comparator_schedules[0],
                baseline_state_ref=comparator_set.exogenous_drive_ref,
            )
            replace(
                comparator_set,
                comparator_schedules=(schedule,) + comparator_set.comparator_schedules[1:],
            )

        def settlement_changes(
            *, residual: object, provenance: object, duplicate_total: bool = False
        ) -> dict[str, object]:
            return {
                "settlement_rule_ref": measurement.before_state_ref,
                "settlement_share_refs": (measurement.endpoint_state_ref,),
                "settlement_share_values": (measurement.ebu_value,),
                "settlement_residual_value": (
                    measurement.ebu_value if duplicate_total else residual
                ),
                "settlement_residual_account_refs": (measurement.horizon_ref,),
                "settlement_validation_provenance_ref": provenance,
            }

        def d2_nonadditivity_mismatch() -> None:
            case = copy.deepcopy(self.cases["M2"])
            case["same_baseline_nonadditivity_record"] = _bundle_with_payload_field(
                case["same_baseline_nonadditivity_record"],
                "d2_witness_ref",
                case["admissible_comparator_set_record"]["object_ref"],
            )
            bridge._materialize_fixture_case(case)

        def order_not_in_comparator_set() -> None:
            case = copy.deepcopy(self.cases["M2"])
            bundles = case["comparator_interaction_records"]
            bundles[0] = _bundle_with_payload_field(
                bundles[0],
                "comparator_schedule_ref",
                case["comparator_schedule_records"][1]["object_ref"],
            )
            bridge._materialize_fixture_case(case)

        def d2_interaction_mismatch() -> None:
            case = copy.deepcopy(self.cases["M2"])
            bundles = case["comparator_interaction_records"]
            bundles[0] = _bundle_with_payload_field(
                bundles[0],
                "d2_witness_ref",
                case["admissible_comparator_set_record"]["object_ref"],
            )
            bridge._materialize_fixture_case(case)

        def nonserializable_schedule_present() -> None:
            case = copy.deepcopy(self.cases["M9"])
            case["comparator_schedule_records"].append(
                copy.deepcopy(self.cases["M2"]["comparator_schedule_records"][0])
            )
            bridge._materialize_fixture_case(case)

        operations = {
            "NONOVERLAPPING_INTERVAL": nonoverlapping_edge,
            "UNKNOWN_DEPENDENCY_KIND": lambda: replace(
                edge, dependency_kinds=("UNKNOWN_DEPENDENCY_KIND",)
            ),
            "RELATION_NOT_COMPLETE": lambda: replace(
                group, dependency_relation_complete=False
            ),
            "MISSING_TRANSITIVE_CHILD": lambda: replace(
                group, child_action_refs=group.child_action_refs[:1]
            ),
            "INCOMPATIBLE_COMMON_BOUNDARY": lambda: replace(
                group, common_boundary_ref=group.common_before_state_ref
            ),
            "NO_SEPARABILITY_EVIDENCE_FOR_UNGROUPED_ACTION": ungrouped_without_evidence,
            "MISALIGNED_ZIPPED_TUPLES": lambda: replace(
                comparator_set, replay_kinds=comparator_set.replay_kinds[:-1]
            ),
            "NON_SEQUENTIAL_COMPARATOR_KIND": nonsequential_comparator,
            "BASELINE_MISMATCH": comparator_baseline_mismatch,
            "MISSING_LIVE_PREDECESSOR_EVIDENCE": lambda: replace(
                comparator_set, live_predecessor_evidence_refs=()
            ),
            "OUTCOME_DEPENDENT_SELECTION": lambda: replace(
                comparator_set,
                named_reported_comparator_refs=comparator_set.named_reported_comparator_refs[:1],
            ),
            "MISSING_LARGE_N_OMISSION_OR_UNCERTAINTY_REPORT": lambda: replace(
                comparator_set,
                selection_kind="PREREGISTERED_LARGE_N_COVERAGE",
                omitted_schedule_refs=(),
                coverage_and_uncertainty_ref=errors.Applicability.NOT_APPLICABLE,
            ),
            "SECOND_PHYSICAL_MEASUREMENT": lambda: replace(
                measurement,
                interaction_or_refusal_refs=(measurement.physical_measurement_ref,),
            ),
            "EBU_ARITHMETIC_MISMATCH": lambda: replace(
                measurement, ebu_value=zero
            ),
            "RECEIPT_BACK_REFERENCE_CYCLE": lambda: replace(
                measurement, group_quote_ref=_ref(receipt)
            ),
            "CAUSAL_CONTRIBUTION_WITHOUT_IDENTIFIED_PROTOCOL": lambda: replace(
                measurement, causal_contribution_refs=(other_ref,)
            ),
            "PARTIALLY_IDENTIFIED_CAUSAL_CONTRIBUTION": lambda: replace(
                measurement,
                causal_status=CausalIdentificationStatus.PARTIALLY_IDENTIFIED,
                causal_identification_protocol_ref=measurement.initial_evaluation_ref,
                causal_evidence_refs=(measurement.endpoint_evaluation_ref,),
                causal_contribution_refs=(other_ref,),
                causal_remainder_ref=measurement.horizon_ref,
            ),
            "PARTIALLY_IDENTIFIED_WITHOUT_REMAINDER": lambda: replace(
                measurement,
                causal_status=CausalIdentificationStatus.PARTIALLY_IDENTIFIED,
                causal_identification_protocol_ref=measurement.initial_evaluation_ref,
                causal_evidence_refs=(measurement.endpoint_evaluation_ref,),
                causal_remainder_ref=errors.Applicability.NOT_APPLICABLE,
            ),
            "UNIDENTIFIED_CAUSAL_CONTRIBUTION": lambda: replace(
                measurement, causal_contribution_refs=(other_ref,)
            ),
            "CAUSAL_AND_SETTLEMENT_REF_ALIAS": lambda: replace(
                measurement,
                causal_status=CausalIdentificationStatus.IDENTIFIED,
                causal_identification_protocol_ref=measurement.initial_evaluation_ref,
                causal_evidence_refs=(measurement.endpoint_evaluation_ref,),
                causal_contribution_refs=(other_ref,),
                **{
                    **settlement_changes(
                        residual=zero,
                        provenance=measurement.endpoint_evaluation_ref,
                    ),
                    "settlement_share_refs": (other_ref,),
                },
            ),
            "SETTLEMENT_SHARE_WITHOUT_RULE_PROVENANCE": lambda: replace(
                measurement,
                **{
                    **settlement_changes(
                        residual=zero,
                        provenance=measurement.endpoint_evaluation_ref,
                    ),
                    "settlement_rule_ref": errors.Applicability.NOT_APPLICABLE,
                },
            ),
            "SETTLEMENT_SHARE_WITHOUT_EXPLICIT_RESIDUAL": lambda: replace(
                measurement,
                **settlement_changes(
                    residual=errors.Applicability.NOT_APPLICABLE,
                    provenance=measurement.endpoint_evaluation_ref,
                ),
            ),
            "SETTLEMENT_SUM_PLUS_RESIDUAL_MISMATCH": lambda: replace(
                measurement,
                **settlement_changes(
                    residual=zero,
                    provenance=measurement.endpoint_evaluation_ref,
                    duplicate_total=True,
                ),
            ),
            "SETTLEMENT_WITHOUT_VALIDATION_PROVENANCE": lambda: replace(
                measurement,
                **settlement_changes(
                    residual=zero,
                    provenance=errors.Applicability.NOT_APPLICABLE,
                ),
            ),
            "NONZERO_EMPTY_BASELINE": lambda: replace(
                nonadditivity, empty_baseline=nonadditivity.singleton_values[0]
            ),
            "UNIT_MISMATCH": lambda: replace(
                nonadditivity,
                singleton_values=(
                    replace(
                        nonadditivity.singleton_values[0],
                        unit_ref=nonadditivity.baseline_state_ref,
                    ),
                    nonadditivity.singleton_values[1],
                ),
            ),
            "DIMENSION_MISMATCH": lambda: replace(
                nonadditivity,
                singleton_values=(
                    replace(
                        nonadditivity.singleton_values[0],
                        dimension_ref=nonadditivity.baseline_state_ref,
                    ),
                    nonadditivity.singleton_values[1],
                ),
            ),
            "UNDEFINED_COERCED_TO_ZERO": lambda: replace(
                m9["nonadditivity"], nonadditivity_value=m9["nonadditivity"].joint_value
            ),
            "D2_WITNESS_REF_MISMATCH": None,
            "ORDER_NOT_IN_COMPARATOR_SET": order_not_in_comparator_set,
            "INTERACTION_ARITHMETIC_MISMATCH": lambda: replace(
                interaction, interaction_value=zero
            ),
            "NUMERIC_ZERO_PRESENT": lambda: replace(
                refusal,
                serialized_interaction_value=errors.Applicability.APPLICABLE,
            ),
            "SCHEDULE_PRESENT": nonserializable_schedule_present,
            "GROUP_REF_MISMATCH": lambda: bridge._validate_group_receipt_link(
                replace(receipt, group_ref=measurement.before_state_ref),
                group,
                measurement,
            ),
            "MEASUREMENT_REF_MISMATCH": lambda: bridge._validate_group_receipt_link(
                replace(receipt, measurement_ref=measurement.before_state_ref),
                group,
                measurement,
            ),
        }

        for vector in semantic:
            mutation = vector["single_mutation"]
            if mutation == "D2_WITNESS_REF_MISMATCH":
                operation = (
                    d2_nonadditivity_mismatch
                    if vector["owner_interface"] == "SameBaselineNonadditivity"
                    else d2_interaction_mismatch
                )
            elif mutation == "UNIT_MISMATCH" and vector["owner_interface"] == "ComparatorInteraction":
                operation = lambda: replace(
                    interaction,
                    sequential_distortion=replace(
                        interaction.sequential_distortion,
                        unit_ref=interaction.sequential_endpoint_ref,
                    ),
                )
            elif mutation == "DIMENSION_MISMATCH" and vector["owner_interface"] == "ComparatorInteraction":
                operation = lambda: replace(
                    interaction,
                    sequential_distortion=replace(
                        interaction.sequential_distortion,
                        dimension_ref=interaction.sequential_endpoint_ref,
                    ),
                )
            else:
                operation = operations[mutation]
            with self.subTest(vector=vector["vector_id"]):
                self._assert_vector_failure(vector["vector_id"], operation)

    def test_failure_coordinate_catalogue_and_all_297_assignments(self) -> None:
        inventory = self.validation["fixture_inventory"]
        negatives = inventory["negative_vectors"]
        identity = self.validation["failure_identity_contract"]
        catalogue = identity["coordinate_catalogue"]
        assignments = identity["vector_coordinate_assignments"]
        self.assertEqual(inventory["complete_validation_vector_count"], 334)
        self.assertEqual(len(inventory["positive_vectors"]), 36)
        self.assertEqual(inventory["static_source_law_vector_count"], 1)
        self.assertEqual(len(negatives), 297)
        self.assertEqual(len(catalogue), 73)
        self.assertEqual(len(assignments), 297)
        self.assertEqual([row["vector_id"] for row in assignments], [row["vector_id"] for row in negatives])
        projections = (
            (
                negatives,
                92_522,
                "9141e569f4c80946c556963b8546478382e0718cb263a719ab92a8e5520bbef0",
            ),
            (
                catalogue,
                90_746,
                "04fb0efd9ba792a5b3478cc553e8b2f1f3cde07fb90e45e394c3a2812872b3e0",
            ),
            (
                assignments,
                365_495,
                "2d13af380d3c214920a93bc8ef1250b20b6a36ac7ed5ccc44168675a65b03384",
            ),
            (
                identity["collision_audit"],
                704,
                "9578153f0bd48667f69d15c8043ecf37f95d9b237b2a4e05140a3c9edd7865bf",
            ),
            (
                identity,
                458_953,
                "ad54fbca725c1120ab268d184f21f9ac55dad587e64602ba4dac99398b43d259",
            ),
        )
        for value, byte_count, sha256 in projections:
            projection = _canonical_json_lf(value)
            self.assertEqual(len(projection), byte_count)
            self.assertEqual(hashlib.sha256(projection).hexdigest(), sha256)
        failure_id_rows = [
            {
                "coordinate_ref": row["coordinate_ref"],
                "derived_failure_id": row["derived_failure_id"],
                "vector_id": row["vector_id"],
            }
            for row in assignments
        ]
        failure_id_projection = _canonical_json_lf(failure_id_rows)
        self.assertEqual(len(failure_id_projection), 62_594)
        self.assertEqual(
            hashlib.sha256(failure_id_projection).hexdigest(),
            "cf73fbe9b3a75aeed874903019368731a50c601e90f798e680025c5575fcc2f0",
        )

        derived_ids: set[str] = set()
        for row in catalogue:
            interface = errors.FailureInterfaceRef(
                row["interface_ref"]["module"],
                row["interface_ref"]["qualname"],
                row["interface_ref"]["interface_version"],
            )
            derived = errors._derive_failure_id(
                errors.FailureCode(row["failure_code"]),
                errors.FailureStage.I6,
                interface,
                (),
                errors.Applicability.NOT_APPLICABLE,
                row["failure_ordinal"],
            )
            self.assertEqual(str(derived), row["derived_failure_id"])
            preimage = b"".join(
                (
                    errors._frame("ebu.failure-id.v1"),
                    errors._frame(row["failure_code"]),
                    errors._frame("I-6"),
                    errors._frame("APPLICABLE"),
                    errors._frame(interface.module),
                    errors._frame(interface.qualname),
                    errors._frame(interface.interface_version),
                    (0).to_bytes(8, "big"),
                    errors._frame("NOT_APPLICABLE"),
                    errors._frame(str(row["failure_ordinal"])),
                )
            )
            self.assertEqual(len(preimage), row["preimage_byte_count"])
            self.assertEqual(preimage.hex(), row["preimage_hex"])
            self.assertEqual(hashlib.sha256(preimage).hexdigest(), row["preimage_sha256"])
            derived_ids.add(str(derived))
        self.assertEqual(len(derived_ids), 73)

        coordinates = {row["coordinate_ref"]: row for row in catalogue}
        for vector, assignment in zip(negatives, assignments, strict=True):
            coordinate = coordinates[assignment["coordinate_ref"]]
            provenance = assignment["materialization_provenance"]
            self.assertEqual(assignment["vector_id"], vector["vector_id"])
            self.assertEqual(assignment["expected_first_failure"], vector["expected_first_failure"])
            self.assertEqual(assignment["derived_failure_id"], coordinate["derived_failure_id"])
            self.assertEqual(provenance["owner_interface_label"], vector["owner_interface"])
            self.assertFalse(provenance["representative_interface_substitution"])
            self.assertFalse(provenance["state_advanced"])
        audit = identity["collision_audit"]
        self.assertEqual(audit["distinct_coordinate_count"], 73)
        self.assertEqual(audit["distinct_derived_failure_id_count"], 73)
        self.assertEqual(audit["repeated_coordinate_group_count"], 28)
        self.assertEqual(audit["vectors_in_repeated_coordinate_groups"], 252)
        self.assertEqual(audit["additional_vectors_sharing_an_identical_coordinate"], 224)
        self.assertEqual(audit["conflicting_coordinate_assignments"], 0)
        self.assertEqual(audit["distinct_coordinate_hash_collisions"], 0)

    def test_t3_nonreachability_and_static_prebackend_boundary(self) -> None:
        vectors = [
            row
            for row in self.validation["fixture_inventory"]["negative_vectors"]
            if row["classification"] == "T3_NONREACHABILITY"
        ]
        self.assertEqual(len(vectors), 8)
        forged = object.__new__(bridge._BridgeExecutionPermit)
        for vector in vectors[::2]:
            function = getattr(bridge, vector["owner_interface"])
            arguments = [object() for _ in inspect.signature(function).parameters]
            arguments[-1] = forged
            with self.subTest(vector=vector["vector_id"]):
                self._assert_vector_failure(
                    vector["vector_id"], lambda f=function, a=arguments: f(*a)
                )

        execution_path = ROOT / "src/ebu_framework/execution.py"
        execution_source = execution_path.read_text(encoding="utf-8")
        execution_tree = ast.parse(execution_source)
        permit_node = next(
            node
            for node in execution_tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "_bridge_execution_permit"
        )
        source = ast.get_source_segment(execution_source, permit_node)
        self.assertIn("REAL_DURABILITY_BACKEND_UNAVAILABLE", source)
        self.assertEqual(ast.unparse(permit_node.returns), "NoReturn")
        self.assertNotIn("_BridgeExecutionPermit(", source)
        self.assertNotIn("return _bridge", source)
        self.assertEqual(
            [row["single_mutation"] for row in vectors[1::2]],
            [
                "classify_joint_groups",
                "compute_group_measurement",
                "compute_same_baseline_nonadditivity",
                "compute_comparator_interaction",
            ],
        )

    def test_failure_export_signature_and_import_surfaces(self) -> None:
        i7_contract = json.loads(
            (ROOT / "unified_python_research_framework_i7_contract.json").read_bytes()
        )
        i7_paths = json.loads(
            (
                ROOT
                / "unified_python_research_framework_i7_implementation_path_manifest.json"
            ).read_bytes()
        )
        failure_order = tuple(item.value for item in errors.FailureCode)
        expected_failures = tuple(
            self.predecessor["current_surface"]["failure_order"]
        ) + tuple(self.contract["failure_inventory"]["append_order"]) + tuple(
            i7_contract["failure_inventory"]["append_order"]
        )
        self.assertEqual(failure_order, expected_failures)
        self.assertEqual(len(failure_order), 256)
        failure_lf = ("\n".join(failure_order) + "\n").encode("utf-8")
        self.assertEqual(
            len(failure_lf), i7_contract["failure_inventory"]["future_lf"]["byte_count"]
        )
        self.assertEqual(
            hashlib.sha256(failure_lf).hexdigest(),
            i7_contract["failure_inventory"]["future_lf"]["sha256"],
        )

        root_exports = tuple(ebu_framework.__all__)
        expected_root_exports = tuple(
            self.predecessor["current_surface"]["root_export_order"]
        ) + tuple(self.contract["root_exports"]["append_order"]) + tuple(
            i7_contract["root_exports"]["append_order"]
        )
        self.assertEqual(root_exports, expected_root_exports)
        self.assertEqual(len(root_exports), 419)
        root_lf = ("\n".join(root_exports) + "\n").encode("utf-8")
        self.assertEqual(
            len(root_lf), i7_contract["root_exports"]["future_lf"]["byte_count"]
        )
        self.assertEqual(
            hashlib.sha256(root_lf).hexdigest(),
            i7_contract["root_exports"]["future_lf"]["sha256"],
        )
        self.assertEqual(tuple(bridge.__all__), tuple(self.contract["root_exports"]["bridge_module_exports"]))

        accepted_rows = self.predecessor["current_surface"][
            "combined_signature_projection"
        ]["current_rows"]
        signature_rows = accepted_rows + self.contract["signatures"]["i6_rows"]
        signature_projection = _canonical_json_lf(signature_rows)
        self.assertEqual(len(signature_rows), 253)
        self.assertEqual(len(signature_projection), 140_368)
        self.assertEqual(
            hashlib.sha256(signature_projection).hexdigest(),
            "db22a09b5634fb48453d466216ca4f0f1f0791ce6a24797ec6b29ab405596037",
        )
        for row in self.contract["public_types"]["rows"]:
            owner = capabilities if row["owner"] == "capabilities" else bridge
            runtime_type = getattr(owner, row["name"])
            self.assertEqual(list(runtime_type.__dataclass_fields__), row["field_order"])
        for row in self.contract["public_callables"]["rows"]:
            runtime = getattr(bridge, row["name"])
            self.assertEqual(
                tuple(inspect.signature(runtime).parameters),
                _signature_parameter_names(row["signature"]),
            )

        package = ROOT / "src/ebu_framework"
        graph: dict[str, list[str]] = {}
        module_names = {path.stem for path in package.glob("*.py") if path.name != "__init__.py"}
        for module in i7_paths["future_import_graph"]["package_module_order"]:
            tree = ast.parse((package / f"{module}.py").read_text(encoding="utf-8"))
            imports: list[str] = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.level == 1:
                    if node.module in module_names:
                        imports.append(node.module)
                    elif node.module is None:
                        imports.extend(
                            alias.name for alias in node.names if alias.name in module_names
                        )
            graph[module] = list(dict.fromkeys(imports))
        self.assertEqual(graph, i7_paths["future_import_graph"]["direct_imports"])
        self.assertEqual(len(graph), 36)
        self.assertEqual(sum(map(len, graph.values())), 221)
        graph_projection = _canonical_json_lf(
            [
                [module, graph[module]]
                for module in i7_paths["future_import_graph"]["package_module_order"]
            ]
        )
        self.assertEqual(
            len(graph_projection),
            i7_paths["future_import_graph"]["projection_byte_count"],
        )
        self.assertEqual(
            hashlib.sha256(graph_projection).hexdigest(),
            i7_paths["future_import_graph"]["projection_sha256"],
        )


if __name__ == "__main__":
    unittest.main()
