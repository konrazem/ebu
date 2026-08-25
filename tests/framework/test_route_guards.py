"""Fail-closed I-7 route guards with completed-prefix preservation."""

from __future__ import annotations

from enum import Enum
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from ebu_framework import canonical, dynamic, errors, hashing, network
from ebu_framework.envelopes import CommonObjectEnvelope, LifecycleStatus
from ebu_framework.identity import ObjectContentHash, ObjectRef, ScientificId, SemanticVersion
from ebu_framework.numeric import IntegerV1
from ebu_framework.primitives import Epoch, Quantity, ResolutionDetail, ResolutionState


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "unified_python_research_framework_i7_validation_contract.json"


def _ref(label: str) -> ObjectRef:
    digest = hashlib.sha256(label.encode("utf-8")).hexdigest()
    return ObjectRef(
        object_id=ScientificId(f"ebu:object:validation:{label}"),
        object_version=SemanticVersion("1.0.0"),
        object_content_hash=ObjectContentHash.from_hex(digest),
    )


def _project(value: object) -> object:
    if type(value) is ObjectRef:
        return value.to_ecj1()
    if isinstance(value, errors.Applicability):
        return value.value
    if isinstance(value, Enum):
        return value.value
    if type(value) is tuple:
        return [_project(item) for item in value]
    if hasattr(value, "to_ecj1"):
        return value.to_ecj1()  # type: ignore[union-attr]
    return value


def _envelope(label: str, payload: dict[str, object]) -> CommonObjectEnvelope:
    authority = _ref("authority")
    object_id = ScientificId(f"ebu:object:validation:i7-{label}")
    kind = ScientificId(f"ebu:kind:framework:i7-{label}")
    schema = ScientificId(f"ebu:schema:framework:i7-{label}")
    version = SemanticVersion("1.0.0")
    content_hash = hashing.compute_object_content_hash(
        object_id=object_id,
        object_kind=str(kind),
        schema_id=schema,
        schema_version=version,
        object_version=version,
        authority_refs=(authority,),
        supersedes_ref=None,
        object_content_payload=payload,
    )
    return CommonObjectEnvelope(
        object_id=object_id,
        object_kind_id=kind,
        schema_id=schema,
        schema_version=version,
        object_version=version,
        authority_refs=(authority,),
        supersedes_ref=errors.Applicability.NOT_APPLICABLE,
        object_content_payload=bytes(canonical.encode_ecj1(payload)),
        object_content_hash=content_hash,
        lifecycle_status=LifecycleStatus.DRAFT,
        record_metadata_ref=errors.Applicability.NOT_APPLICABLE,
    )


def _record(record_type: type, label: str, **values: object):
    payload = {name: _project(value) for name, value in values.items()}
    return record_type(envelope=_envelope(label, payload), **values)


def _record_ref(record: object) -> ObjectRef:
    envelope = record.envelope  # type: ignore[attr-defined]
    return ObjectRef(
        object_id=envelope.object_id,
        object_version=envelope.object_version,
        object_content_hash=envelope.object_content_hash,
    )


def _quantity(value: int) -> Quantity:
    return Quantity(
        magnitude=IntegerV1(value),
        unit_ref=_ref("unit"),
        dimension_ref=_ref("dimension"),
        boundary_ref=_ref("boundary"),
        resource_type_ref=errors.Applicability.NOT_APPLICABLE,
        service_type_ref=errors.Applicability.NOT_APPLICABLE,
        region_ref=errors.Applicability.NOT_APPLICABLE,
        time_basis_ref=errors.Applicability.NOT_APPLICABLE,
        sign_convention_ref=errors.Applicability.NOT_APPLICABLE,
        uncertainty_ref=errors.Applicability.NOT_APPLICABLE,
        resolution=ResolutionDetail(
            state=ResolutionState.PRESENT,
            present_value_ref=errors.Applicability.NOT_APPLICABLE,
            completed_part_refs=(),
            missing_part_refs=(),
            due_condition_ref=errors.Applicability.NOT_APPLICABLE,
            failure=errors.Applicability.NOT_APPLICABLE,
            boundary_edge_ref=errors.Applicability.NOT_APPLICABLE,
            reason_ref=errors.Applicability.NOT_APPLICABLE,
        ),
    )


class RouteGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        validation = json.loads(CONTRACT.read_text(encoding="utf-8"))
        coordinates = {
            row["coordinate_id"]: row
            for row in validation["failure_identity_contract"]["coordinates"]
        }
        cls.failures = {
            row["vector_id"]: coordinates[row["coordinate_ref"]]
            for row in validation["failure_identity_contract"]["assignments"]
        }

    def setUp(self) -> None:
        self.clock = _ref("clock")
        self.edge_a = _ref("edge-a")
        self.edge_b = _ref("edge-b")
        self.edge_c = _ref("edge-c")
        self.route = _record(
            network.RoutePlan,
            "routeplan",
            origin_ref=_ref("origin"),
            destination_ref=_ref("destination"),
            ordered_segment_refs=(self.edge_a, self.edge_b),
            planning_epoch=Epoch(clock_ref=self.clock, index=IntegerV1(0)),
            information_snapshot_ref=_ref("information-snapshot"),
            expected_capacity_ref=_ref("capacity-record"),
            expected_delay_ref=_ref("delay-record"),
            unfinished_suffix_refs=(self.edge_b,),
            route_semantics_status=network.RouteSemanticsStatus.PROVISIONAL_PART_VII,
        )
        self.topology_change = _record(
            network.TopologyChangeEvent,
            "topologychangeevent",
            effective_epoch=Epoch(clock_ref=self.clock, index=IntegerV1(1)),
            topology_before_ref=_ref("topology-before"),
            topology_after_ref=_ref("topology-after"),
            structural_topology_ref=_ref("structural-topology"),
            active_topology_before_ref=_ref("active-before"),
            active_topology_after_ref=_ref("active-after"),
            change_kind="FAILURE",
            affected_provider_refs=(),
            affected_node_refs=(),
            affected_edge_refs=(self.edge_a,),
            availability_before=network.AvailabilityStatus.AVAILABLE,
            availability_after=network.AvailabilityStatus.FAILED,
            declaration_status="DOMAIN_DECLARED",
            declaring_authority_ref=_ref("authority"),
            observation_provenance_ref=errors.Applicability.NOT_APPLICABLE,
            causal_identification_protocol_ref=errors.Applicability.NOT_APPLICABLE,
            cause_claim_status="NOT_CLAIMED",
        )
        self.transit = _record(
            dynamic.InTransitRecord,
            "intransitrecord",
            payload_ref=_ref("payload"),
            originating_action_ref=_ref("action"),
            route_plan_ref=_record_ref(self.route),
            completed_segment_refs=(self.edge_a,),
            unfinished_suffix_refs=(self.edge_b,),
            dispatch_epoch=Epoch(clock_ref=self.clock, index=IntegerV1(0)),
            expected_arrival_epoch=Epoch(clock_ref=self.clock, index=IntegerV1(2)),
            current_locus_ref=_ref("node"),
            quantity=_quantity(4),
            status="IN_TRANSIT",
            topology_snapshot_ref=_ref("topology-snapshot"),
            delay_record_ref=_ref("delay-record"),
            completion_or_loss_ref=errors.Applicability.NOT_APPLICABLE,
            provenance_ref=_ref("provenance"),
        )

    def _assert_failure(self, vector_id: str, operation: object) -> None:
        expected = self.failures[vector_id]
        with self.assertRaises(errors.FrameworkError) as raised:
            operation()  # type: ignore[operator]
        envelope = raised.exception.envelope
        self.assertEqual(envelope.failure_code.value, expected["failure_code"])
        self.assertEqual(envelope.stage, errors.FailureStage.I7)
        self.assertEqual(str(envelope.failure_id), expected["failure_id"])
        self.assertEqual(envelope.interface_ref.module, expected["module"])
        self.assertEqual(envelope.interface_ref.qualname, expected["qualname"])

    def test_i7v_057_provisional_route_semantics_refusal(self) -> None:
        real_owner = dynamic._validate_route_guard
        with patch.object(dynamic, "_validate_route_guard", wraps=real_owner) as owner:
            self._assert_failure(
                "I7V-057",
                lambda: dynamic._validate_route_guard(
                    self.route,
                    self.transit.completed_segment_refs,
                    (self.edge_c,),
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_058_completed_rewrite_precedes_route_semantics(self) -> None:
        real_owner = dynamic._validate_route_guard
        with patch.object(dynamic, "_validate_route_guard", wraps=real_owner) as owner:
            self._assert_failure(
                "I7V-058",
                lambda: dynamic._validate_route_guard(
                    self.route,
                    self.transit.completed_segment_refs,
                    (self.edge_a, self.edge_c),
                ),
            )
            self.assertEqual(owner.call_count, 1)

    def test_i7v_059_exact_private_permit_owner_refuses(self) -> None:
        real_owner = dynamic._DynamicExecutionPermit
        with patch.object(dynamic, "_DynamicExecutionPermit", wraps=real_owner) as owner:
            self._assert_failure("I7V-059", dynamic._DynamicExecutionPermit)
            self.assertEqual(owner.call_count, 1)

    def test_i7v_070_completed_rewrite_precedence_witness(self) -> None:
        real_owner = dynamic._validate_route_guard
        with patch.object(dynamic, "_validate_route_guard", wraps=real_owner) as owner:
            self._assert_failure(
                "I7V-070",
                lambda: dynamic._validate_route_guard(
                    self.route,
                    self.transit.completed_segment_refs,
                    (self.edge_a, self.edge_c),
                ),
            )
            self.assertEqual(owner.call_count, 1)


if __name__ == "__main__":
    unittest.main()
