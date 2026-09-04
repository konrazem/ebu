"""Offline tests for the closure-closed AWS-C0 implementation."""
from __future__ import annotations

import ast
import base64
import copy
import hashlib
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]


def module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    assert spec and spec.loader
    loaded = importlib.util.module_from_spec(spec); sys.modules[name] = loaded; spec.loader.exec_module(loaded)
    return loaded


V = module("scripts/validate_aws_c0_static.py", "aws_c0_validator")
C = module("aws/c0/controller/ebu_c0_controller.py", "aws_c0_controller")
F = module("aws/c0/finalizer/finalizer.py", "aws_c0_finalizer")
W = module("aws/c0/container/synthetic_worker.py", "aws_c0_worker")


def load(path: str):
    return json.loads((ROOT / path).read_text())


def reroot(record):
    result = copy.deepcopy(record); result.pop("record_sha256", None)
    result["record_sha256"] = hashlib.sha256(V.canonical_bytes(result)).hexdigest(); return result


def current_launch(record):
    result = copy.deepcopy(record)
    result["schema"] = "aws_c0_launch_request/v5"
    result["preparation_packet_identity"]["kind"] = "aws_c0_preparation_packet/v4"
    result["preparation_authorization_identity"]["kind"] = "aws_c0_preparation_authorization/v3"
    result["authority_audit_identity"]["kind"] = "aws_c0_audit_static_handoff_authority_audit/v4"
    result["static_validation_identity"]["kind"] = "aws_c0_material_runtime_static_validation/v4"
    return reroot(result)


class CanonicalTests(unittest.TestCase):
    def test_duplicate_refused(self):
        with self.assertRaises(V.ValidationError): V.strict_json_bytes(b'{"x":1,"x":2}')

    def test_float_refused(self):
        with self.assertRaises(V.ValidationError): V.strict_json_bytes(b'{"x":1.0}')

    def test_final_lf_refused(self):
        with self.assertRaises(V.ValidationError): V.strict_json_bytes(b'{}\n', canonical=True)

    def test_root_preimage_and_object_digest_differ(self):
        launch = load("aws/c0/fixtures/launch-request.valid.json")
        root_id = V.validate_root(launch, "aws_c0_launch_request/v3")
        self.assertNotEqual(root_id, V.digest(V.canonical_bytes(launch)))

    def test_nonroot_self_digest_refused(self):
        record = {"schema": "aws_c0_closure_seed/v1", "record_sha256": "0" * 64}
        with self.assertRaises(V.ValidationError): V.validate_nonroot(record, V.canonical_bytes(record), record["schema"])

    def test_identity_is_closed(self):
        with self.assertRaises(V.ValidationError): V.validate_identity({"kind": "x", "sha256": "0" * 64, "value": "1" * 64})


class AuthorityTests(unittest.TestCase):
    def test_frozen_arithmetic(self): V.validate_authorities()
    def test_exact_paths_and_modes(self): V.validate_paths()

    def test_66_84_108(self):
        counts = []
        for path in V.VALIDATION_PATHS:
            suite = load(path); counts.append(len(suite["positive_cases"]) + len(suite["negative_cases"]))
        self.assertEqual(counts, [66, 84, 108])

    def test_eighteen_schema_union(self):
        schema = load(V.EVIDENCE_SCHEMA_PATH)
        self.assertEqual(len(schema["oneOf"]), len(V.NEW_SCHEMAS), 18)

    def test_21_12_22_63(self):
        contract = load(V.CONTRACT_PATH)
        self.assertEqual(contract["pre_live_publication"]["minimum_object_count"], 21)
        self.assertEqual(len(contract["evidence_root_categories_semantic_order"]), 12)
        self.assertEqual(len(contract["resource_dimensions_in_order"]), 22)
        self.assertEqual(len(contract["read_only_preflight_api_resource_allowlist"]), 63)

    def test_stage_boundaries(self):
        contract = load(V.CONTRACT_PATH)
        self.assertEqual(contract["stage_boundary"]["stage_e_status"], "ACCEPTED_FINISHED_UNCHANGED")
        self.assertEqual(contract["stage_boundary"]["stage_f"], "FROZEN_SEPARATE_AWS_LINUX_BINDING_SCIENTIFIC_PACKET_AND_AUTHORIZATION_REQUIRED")

    def test_gate1_lineage_lane_is_additive_to_historical_registry(self):
        fixture = load("aws/c0/fixtures/negative-cases.json")
        self.assertEqual(fixture["schema"], "aws_c0_static_negative_case_execution/v5")
        self.assertEqual(fixture["executed_case_count"], 358)
        self.assertEqual(fixture["case_ids"][-6:], [
            "C0-G1-LINEAGE-N01", "C0-G1-LINEAGE-N02", "C0-G1-LINEAGE-N03",
            "C0-G1-LINEAGE-N04", "C0-G1-LINEAGE-N05", "C0-G1-LINEAGE-N06",
        ])

    def test_gate1_preparation_authorization_v3_statement_is_exact(self):
        contract = load("aws_c0_gate1_bootstrap_lineage_correction_contract.json")
        statement = contract["preparation_authorization_statement"]
        self.assertEqual(statement["statement_version"], "AUTHORIZE_AWS_C0_PREPARATION_V3")
        self.assertEqual(statement["statement_template"], V.GATE1_PREPARATION_STATEMENT_TEMPLATE)
        self.assertIn("pre_live_object_count=24", statement["statement_template"])
        self.assertNotIn("pre_live_object_count=21", statement["statement_template"])
        self.assertIn("deny=LIVE_EXECUTION,REPLAY,DELETE,TERMINATE,SCIENTIFIC_EXECUTION",
                      statement["statement_template"])

    def test_audit_and_static_v4_modes_are_distinct_and_offline(self):
        self.assertEqual(V.main(["--mode", "audit-v4"]), 0)
        self.assertEqual(V.main(["--mode", "static-v4"]), 0)
        with self.assertRaises(SystemExit):
            V.main(["--mode", "static-v3"])

    def test_public_cli_writes_only_an_exclusive_canonical_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); inputs = []
            for name in ("audit.json", "static.json", "provisional.json"):
                path = root / name; path.write_bytes(b"{}") ; inputs.append(path)
            output = root / "audit-v4.json"
            args = ["--mode", "audit-v4", "--source", str(ROOT), "--output", str(output),
                    "--authority-audit-receipt", str(inputs[0]), "--static-validation-receipt", str(inputs[1]),
                    "--provisional-put-observation", str(inputs[2])]
            self.assertEqual(V.main(args), 0)
            record = V.strict_json_bytes(output.read_bytes(), canonical=True)
            self.assertEqual((len(record["parent_receipts"]), len(record["axis_receipts"]),
                              len(record["member_execution_receipts"])), (352, 878, 1108))
            self.assertEqual(V.main(args), 1)


class LaunchTests(unittest.TestCase):
    def setUp(self): self.launch = load("aws/c0/fixtures/launch-request.valid.json")
    def test_valid_in_static_and_controller(self):
        V.validate_launch_v3(self.launch)
        current = current_launch(self.launch)
        C.validate_launch(current, current["rehearsal_id"], current["attempt_id"])

    def test_extra_field_refused(self):
        changed = reroot({**self.launch, "unexpected_scientific_switch": False})
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_future_identity_refused_by_closure(self):
        changed = reroot({**self.launch, "live_authorization_identity": {"kind": "aws_c0_live_authorization/v2", "sha256": "0"*64, "value": "0"*64}})
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_wrong_attempt_suffix_refused(self):
        changed = copy.deepcopy(self.launch); changed["attempt_id"] = "ATTEMPT-CLOSURE-EVIL"; changed = reroot(changed)
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_timeout_cross_layer_refused(self):
        changed = copy.deepcopy(self.launch); changed["phase_timeouts_seconds"]["finalizer"] = 301; changed = reroot(changed)
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_cost_dimension_missing_refused(self):
        changed = copy.deepcopy(self.launch); changed["cost_envelope"]["resource_limits"].pop("kms_requests"); changed = reroot(changed)
        with self.assertRaises(V.ValidationError): V.validate_launch_v3(changed)

    def test_three_modes_only(self):
        self.assertEqual(set(C.MODE_BY_SUFFIX.values()), {"SUCCESS", "FAIL_AFTER_CHECKPOINT", "TIMEOUT"})
        with self.assertRaises(C.Refusal): C._mode("ATTEMPT-X-OTHER")

    def test_platform_smoke_first_capsule_binds_existing_success_launch_only(self):
        current = current_launch(self.launch)
        binding = C.build_platform_smoke_known_case_local_binding(current)
        self.assertEqual(binding["schema"], "aws_c0_platform_smoke_known_case_local_binding/v2")
        self.assertEqual(binding["capsule_id"], "platform-smoke-known-case-v1")
        self.assertEqual(binding["test_case"], "SUCCESS_KNOWN_CASE")
        self.assertEqual(binding["budget_binding"]["ceiling_minor_units"], 5000)
        self.assertEqual(binding["budget_binding"]["currency"], "USD")
        self.assertEqual(binding["common_receipt_fields_in_order"],
                         list(C.PLATFORM_SMOKE_COMMON_RECEIPT_FIELDS))
        self.assertEqual(binding["reused_foundation_capabilities_in_order"],
                         list(C.PLATFORM_SMOKE_FOUNDATION_CAPABILITIES))
        self.assertEqual(binding["expected_artifact_classes_in_order"], [
            "ATTEMPT_CLAIM", "START_RECEIPT", "HEARTBEAT", "SAFE_CLOSE_RECEIPT",
            "CHECKPOINT", "SYNTHETIC_MANIFEST", "TERMINAL_RECEIPT",
            "CONTROLLER_CAPTURE_JOURNAL", "CONTROLLER_JOURNAL_HANDOFF",
            "STOPPED_OBSERVATION", "RESOURCE_USE_CLOSURE", "FINALIZER_RECEIPT",
            "FINALIZER_CAPTURE_JOURNAL", "COST_CLOSURE",
            "RETRIEVAL_VERIFICATION", "FINAL_MANIFEST",
        ])
        self.assertFalse(binding["scientific_conclusion_authorized"])
        self.assertFalse(binding["live_aws_execution_authorized"])
        self.assertTrue(binding["separate_capsule_authority_required"])
        self.assertFalse(binding["global_aggregate_payload_embedded"])
        self.assertNotIn("final_s3_capture_aggregate", json.dumps(binding, sort_keys=True))

    def test_platform_smoke_first_capsule_refuses_non_success_known_case(self):
        changed = copy.deepcopy(self.launch)
        changed = current_launch(changed)
        changed["attempt_id"] = "ATTEMPT-CLOSURE-FAIL-AFTER-CHECKPOINT"
        changed["artifact_prefix"] = (
            "rehearsal/aws-c0/AWS-C0-CLOSURE/"
            "ATTEMPT-CLOSURE-FAIL-AFTER-CHECKPOINT/"
        )
        changed = reroot(changed)
        with self.assertRaises(C.Refusal):
            C.build_platform_smoke_known_case_local_binding(changed)


class Gate1LineageCorrectionTests(unittest.TestCase):
    @staticmethod
    def packet(*, schema="aws_c0_live_packet/v5", count=24, predecessors=23):
        packet = {field: None for field in F.LIVE_PACKET_V5_FIELDS}
        packet.update({
            "schema": schema,
            "packet_disposition": "AWS_C0_LIVE_PACKET_COMPLETE_UNAUTHORIZED",
            "final_instance_state": "stopped",
            "pre_live_object_count": count,
            "pre_live_predecessor_object_receipts": [object() for _ in range(predecessors)],
            "preparation_closure_identity": C.identity("aws_c0_preparation_closure/v4", "a" * 64),
            "launch_request_identity": C.identity("aws_c0_launch_request/v5", "b" * 64),
            "observed_utc": "2026-09-04T00:00:00Z",
            "live_session_assumer_expires_utc": "2026-09-04T01:00:00Z",
        })
        return packet

    @staticmethod
    def validate_packet(packet):
        with (mock.patch.object(F, "_common"), mock.patch.object(F, "_identity"),
              mock.patch.object(F, "_bound_base64")):
            F._validate_live_packet_v5(packet)

    def test_c0_g1_lineage_n01_stale_launch_version_refused(self):
        launch = current_launch(load("aws/c0/fixtures/launch-request.valid.json"))
        launch["schema"] = "aws_c0_launch_request/v4"
        launch = reroot(launch)
        with self.assertRaises(C.Refusal):
            C.validate_launch(launch, launch["rehearsal_id"], launch["attempt_id"])

    def test_c0_g1_lineage_n02_stale_live_packet_version_refused(self):
        with self.assertRaises(F.Refusal):
            self.validate_packet(self.packet(schema="aws_c0_live_packet/v4"))

    def test_c0_g1_lineage_n03_stale_live_authorization_version_refused(self):
        auth = {field: None for field in F.LIVE_AUTH_V5_FIELDS}
        auth["schema"] = "aws_c0_live_authorization/v4"
        with self.assertRaises(F.Refusal):
            F._validate_live_authorization_v5(auth)

    def test_c0_g1_lineage_n04_stale_21_object_count_refused(self):
        with self.assertRaises(F.Refusal):
            self.validate_packet(self.packet(count=21))

    def test_c0_g1_lineage_n05_stale_20_predecessor_count_refused(self):
        with self.assertRaises(F.Refusal):
            self.validate_packet(self.packet(predecessors=20))

    def test_c0_g1_lineage_n06_same_kind_wrong_hash_refused(self):
        self.assertEqual(F.FROZEN_PRELIVE_OBJECT_COUNT, 24)
        self.assertEqual(F.FROZEN_PRELIVE_PREDECESSOR_COUNT, 23)
        self.assertEqual(len(F.FROZEN_PRELIVE_RECORD_KINDS), 15)
        self.assertEqual(F.FROZEN_PRELIVE_RECORD_KINDS[:6], (
            "aws_c0_operator_bootstrap_packet/v4",
            "aws_c0_operator_bootstrap_authorization/v5",
            "aws_c0_operator_bootstrap_closure/v5",
            "aws_c0_operator_session_renewal_packet/v1",
            "aws_c0_operator_session_renewal_authorization/v1",
            "aws_c0_operator_session_renewal_closure/v1",
        ))
        coordinates = [{"key": f"object-{index}", "version_id": f"v-{index}",
                        "sha256": f"{index:064x}", "bytes": 1}
                       for index in range(23)]
        artifacts = coordinates[:8]
        records = coordinates[8:]
        packet = self.packet()
        packet["pre_live_predecessor_object_receipts"] = artifacts + records
        auth = {"live_packet_identity": C.identity("aws_c0_live_packet/v5", "c" * 64)}
        stale = V.canonical_bytes({"schema": "aws_c0_operator_bootstrap_packet/v4"})
        with (mock.patch.object(F, "_fetch_receipt", side_effect=[
                  (packet, b"", "c" * 64), (auth, b"", "d" * 64)]),
              mock.patch.object(F, "_validate_live_packet_v5"),
              mock.patch.object(F, "_validate_live_authorization_v5"),
              mock.patch.object(F, "_receipt", side_effect=lambda value: value),
              mock.patch.object(F, "_bucket_from_receipt", return_value="bucket"),
              mock.patch.object(F, "_s3_get", return_value=stale)):
            with self.assertRaisesRegex(F.Refusal, "complete-byte SHA-256 mismatch"):
                F._verify_prelive_objects({}, {}, {"artifact_version_receipts": artifacts})

    def test_sealed_gate0_lineage_semantics_are_explicitly_enforced(self):
        bootstrap = {
            "schema": "aws_c0_operator_bootstrap_closure/v5",
            "operator_bootstrap_disposition": "AWS_C0_OPERATOR_BOOTSTRAP_FAIL",
        }
        bootstrap_raw = V.canonical_bytes(bootstrap)
        bootstrap_hashes = list(F.FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256)
        bootstrap_hashes[2] = F.digest(bootstrap_raw)
        with mock.patch.object(F, "FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256", tuple(bootstrap_hashes)):
            with self.assertRaisesRegex(F.Refusal, "V5 bootstrap closure is not PASS"):
                F._validate_sealed_gate0_lineage_record(
                    2, "aws_c0_operator_bootstrap_closure/v5", bootstrap_raw, bootstrap)

        predecessor = {
            "kind": "aws_c0_operator_session_renewal_closure/v1",
            "sha256": F.FROZEN_GATE0_RENEWAL_PREDECESSOR_SHA256,
            "value": F.FROZEN_GATE0_RENEWAL_PREDECESSOR_SHA256,
        }
        base_renewal = {
            "schema": "aws_c0_operator_session_renewal_closure/v1",
            "operator_session_renewal_disposition": "AWS_C0_OPERATOR_SESSION_RENEWAL_PASS",
            "credentials_issued": True,
            "predecessor_closure_identity": predecessor,
        }
        mutations = (
            {**base_renewal, "credentials_issued": False},
            {**base_renewal, "predecessor_closure_identity": C.identity(
                "aws_c0_operator_session_renewal_closure/v1", "0" * 64)},
        )
        for renewal in mutations:
            with self.subTest(renewal=renewal):
                renewal_raw = V.canonical_bytes(renewal)
                renewal_hashes = list(F.FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256)
                renewal_hashes[5] = F.digest(renewal_raw)
                with mock.patch.object(F, "FROZEN_GATE0_LINEAGE_COMPLETE_BYTE_SHA256", tuple(renewal_hashes)):
                    with self.assertRaisesRegex(F.Refusal, "V6 renewal closure semantics mismatch"):
                        F._validate_sealed_gate0_lineage_record(
                            5, "aws_c0_operator_session_renewal_closure/v1", renewal_raw, renewal)


class PaginationTests(unittest.TestCase):
    def test_all_pages_and_token_transcript(self):
        items, pages = V.paginate([{"Values":[1],"NextToken":"n"},{"Values":[2]}], max_pages=2, max_items=2, item_fields=("Values",))
        self.assertEqual(items, [1,2]); self.assertEqual(len(pages), 2)

    def test_truncation_refused(self):
        with self.assertRaises(V.ValidationError): V.paginate([{"Values":[1],"NextToken":"n"}], max_pages=1, max_items=2, item_fields=("Values",))

    def test_item_overflow_refused(self):
        with self.assertRaises(V.ValidationError): V.paginate([{"Values":[1,2]}], max_pages=1, max_items=1, item_fields=("Values",))

    def test_repeated_token_refused(self):
        with self.assertRaises(V.ValidationError): V.paginate([{"Values":[],"NextToken":"n"},{"Values":[],"NextToken":"n"}], max_pages=2, max_items=1, item_fields=("Values",))

    def test_no_latest_listing_api(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        self.assertIn("ListObjectVersions", source); self.assertNotIn("ListObjectsV2", source)


class CostTests(unittest.TestCase):
    def setUp(self):
        dims = load(V.CONTRACT_PATH)["resource_dimensions_in_order"]; units = load(V.CONTRACT_PATH)["resource_dimension_units"]
        self.model = {"integer_maximum":9007199254740991,"product_maximum":100000,"total_maximum":100000,"fixed_minor_units":3,
                      "rates":[{"dimension":d,"unit":units[d],"numerator_minor_units":2,"denominator_units":3} for d in dims]}
        self.use = {"dimensions":[{"dimension":d,"unit":units[d],"charged_units":4,"limit_units":4} for d in dims]}

    def test_ceil_each_dimension_then_sum(self):
        charges,total=V.compute_cost(self.model,self.use); self.assertEqual(charges,[3]*22); self.assertEqual(total,69)

    def test_dimension_order_refused(self):
        self.use["dimensions"].reverse()
        with self.assertRaises(V.ValidationError): V.compute_cost(self.model,self.use)

    def test_limit_refused(self):
        self.use["dimensions"][0]["charged_units"]=5
        with self.assertRaises(V.ValidationError): V.compute_cost(self.model,self.use)

    def test_product_overflow_refused(self):
        self.model["product_maximum"]=1
        with self.assertRaises(V.ValidationError): V.compute_cost(self.model,self.use)

    def test_finalizer_uses_same_integer_rule(self):
        charges,total=F.compute_cost(self.model,self.use); self.assertEqual((charges,total),([3]*22,69))


class RuntimeContractTests(unittest.TestCase):
    def test_local_sigv4_exact_version_get_is_transport_injected_and_offline(self):
        raw = b'{"schema":"test"}'
        expected = hashlib.sha256(raw).hexdigest()
        calls = []

        def credentials():
            return {"access_key_id": "AKIDEXAMPLE", "secret_access_key": "secret",
                    "session_token": "token"}

        def transport(host, uri, query, headers):
            calls.append((host, uri, query, headers))
            return raw, {"version_id": "v1", "checksum_sha256": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "etag": '"source-etag"', "request_id": "request-1",
                         "tls_certificate_sha256": "a" * 64}

        received, receipt = C._download("valid-bucket", "frozen/key.json", "v1", expected,
                                        credential_provider=credentials, transport=transport,
                                        now=C.dt.datetime(2026, 9, 3, tzinfo=C.dt.timezone.utc))
        self.assertEqual(received, raw)
        self.assertEqual(receipt["version_id"], "v1")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][2], "versionId=v1")
        self.assertEqual(calls[0][3]["x-amz-checksum-mode"], "ENABLED")
        self.assertIn("AWS4-HMAC-SHA256", calls[0][3]["authorization"])

    def test_controller_preparation_get_callgraph_has_no_aws_cli_s3_get(self):
        source = (ROOT / "aws/c0/controller/ebu_c0_controller.py").read_text()
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        download = ast.get_source_segment(source, functions["_download"])
        prepare = ast.get_source_segment(source, functions["prepare_request"])
        self.assertIn("sigv4_exact_version_get", download)
        self.assertNotIn('"s3api", "get-object"', source)
        self.assertEqual(prepare.count("source_role=\""), 3)
        for role in ("LAUNCH_REQUEST_V5", "LIVE_PACKET_V5", "LIVE_AUTHORIZATION_V5"):
            self.assertIn(role, prepare)

    def test_ssm_completion_v2_is_closed_and_refuses_non_success(self):
        identity = {"kind": "aws_c0_attempt/v1", "sha256": "a" * 64, "value": "a" * 64}
        dispatch = {"kind": "aws_c0_ssm_dispatch_request/v2", "sha256": "b" * 64, "value": "b" * 64}
        record = C.build_ssm_completion_v2(attempt_identity=identity, dispatch_identity=dispatch,
                                           command_id="cmd-1", invocation_status="Success",
                                           observed_utc="2026-09-01T00:00:00Z")
        self.assertEqual(C.validate_ssm_completion_v2(record)["schema"], "aws_c0_ssm_completion_observation/v2")
        record["invocation_status"] = "Failed"
        with self.assertRaises(C.Refusal): C.validate_ssm_completion_v2(record)

    def test_bucket_names_are_dot_free_across_ssm_cfn_controller_and_finalizer(self):
        with self.assertRaises(C.Refusal):
            C._download("dot.bucket", "key", "version", "a" * 64)
        with mock.patch.dict(os.environ, {"AWS_C0_ARTIFACT_BUCKET": "dot.bucket",
                                          "AWS_C0_BUCKET_IDENTITY_SHA256": "a" * 64}, clear=False):
            with self.assertRaises(F.Refusal):
                F._bucket_from_receipt({"bucket_identity": {"kind": "aws_s3_bucket/v1", "sha256": "a" * 64,
                                                              "value": "a" * 64}})
        self.assertEqual(load("aws/c0/ssm/EBU-C0-Start-v1.yaml")["parameters"]["ArtifactBucket"]["allowedPattern"],
                         "^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")
        self.assertEqual(load("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")["Parameters"]["ArtifactBucketName"]["AllowedPattern"],
                         "^[a-z0-9][a-z0-9-]{1,61}[a-z0-9]$")

    def test_retrieval_expected_count_is_frozen_not_observed(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        self.assertIn("FROZEN_PRELIVE_OBJECT_COUNT = 24", source)
        self.assertIn("FROZEN_PRELIVE_PREDECESSOR_COUNT = 23", source)
        self.assertIn('"expected_object_count": FROZEN_PRELIVE_OBJECT_COUNT', source)
        self.assertNotIn('"expected_object_count": len(verified)', source)

    def test_finalizer_authenticated_requests_reserve_and_record_sanitized_journal_rows(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        self.assertIn("journal.reserve(capture)", source)
        self.assertIn("observed_checksum_sha256", source)
        self.assertIn("finalizer_journal_aggregate", source)
        self.assertNotIn('"authorization": request_headers["authorization"]', source)

    def test_capture_journals_are_reserved_acyclic_and_observed_only(self):
        journal=C.CaptureJournal("controller")
        journal.reserve_for_operation({"operation":"S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE",
                         {"observed_sha256":"a" * 64})
        journal.failed("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE",
                       {"failure_class":"Refusal"})
        self.assertEqual([row["disposition"] for row in journal.envelopes],
                         ["OBSERVED_COMPLETE", "OBSERVED_FAILURE"])
        self.assertIsNone(journal.envelopes[0]["previous_envelope_sha256"])
        self.assertEqual(F.CaptureJournal().aggregate()["envelope_count"], 0)

    def test_controller_journal_seals_publishes_and_exact_version_readbacks_offline(self):
        attempt = C.identity("aws_c0_attempt/v1", "b" * 64)
        journal_key = "rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json"
        journal = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        journal.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE",
                         {"observed_sha256": "a" * 64})
        published = []
        def publisher(bucket, key, raw):
            published.append((bucket, key, raw))
            return {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            self.assertEqual((bucket, key, version), ("valid-bucket", journal_key, "v1"))
            raw = published[0][2]
            return raw, {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "request-1"}
        journal_identity, receipt = C.publish_and_readback_controller_journal(
            journal=journal, bucket="valid-bucket", key=journal_key,
            attempt_identity=attempt, publisher=publisher, readback=readback)
        self.assertEqual(len(published), 1)
        self.assertEqual(journal_identity["kind"], "aws_c0_controller_capture_journal/v1")
        self.assertEqual(receipt["readback_receipt"]["version_id"], "v1")
        with self.assertRaises(C.Refusal): journal.seal()

    def test_controller_journal_refuses_bad_exact_version_readback(self):
        attempt = C.identity("aws_c0_attempt/v1", "b" * 64)
        journal = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        journal.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {})
        def publisher(bucket, key, raw):
            return {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        with self.assertRaises(C.Refusal):
            C.publish_and_readback_controller_journal(
                journal=journal, bucket="valid-bucket",
                key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json",
                attempt_identity=attempt, publisher=publisher,
                readback=lambda bucket, key, version: (b"wrong", {
                    "key": key, "version_id": version, "etag": '"journal-etag"',
                    "bytes": 5, "sha256": "0" * 64,
                    "checksum_sha256_base64": base64.b64encode(b"0" * 32).decode(),
                    "request_id": "request-1"}))

    def test_controller_journal_seals_only_after_terminal_attempt_completion(self):
        source = (ROOT / "aws/c0/controller/ebu_c0_controller.py").read_text()
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        prepare = ast.get_source_segment(source, functions["prepare_request"])
        run = ast.get_source_segment(source, functions["run_attempt"])
        self.assertIn("CaptureJournal", prepare)
        self.assertNotIn("publish_and_readback_controller_journal", prepare)
        self.assertNotIn("build_controller_journal_handoff_v1", prepare)
        self.assertNotIn("publish_controller_journal_handoff", prepare)
        self.assertIn("CaptureJournal.restore", run)
        terminal = run.index('if code != expected_exit or not terminal_seen')
        journal_put = run.index("publish_and_readback_controller_journal")
        carrier_build = run.index("build_controller_journal_handoff_v1")
        carrier_put = run.index("publish_controller_journal_handoff")
        self.assertLess(terminal, journal_put)
        self.assertLess(journal_put, carrier_build)
        self.assertLess(carrier_build, carrier_put)
        self.assertEqual(prepare.count("source_role=\""), 3)

    def test_fixed_carrier_passes_controller_version_and_publication_receipt_reference(self):
        controller = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        controller.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        controller.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {"observed_sha256": "a" * 64})
        stored = {}
        def publisher(bucket, key, raw):
            stored["raw"] = raw
            return {"key": key, "version_id": "controller-version-1", "etag": '"controller-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            raw = stored["raw"]
            return raw, {"key": key, "version_id": version, "etag": '"controller-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "controller-request-1"}
        attempt = {"kind": "aws_c0_attempt/v1", "sha256": "b" * 64, "value": "b" * 64}
        controller_identity, authenticated = C.publish_and_readback_controller_journal(
            journal=controller, bucket="valid-bucket",
            key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json",
            attempt_identity=attempt, publisher=publisher, readback=readback)
        handoff = C.build_controller_journal_handoff_v1(
            attempt_identity=attempt, bucket="valid-bucket",
            journal_identity=controller_identity, authenticated_readback=authenticated)
        self.assertEqual(handoff["controller_journal_object"]["version_id"], "controller-version-1")
        self.assertEqual(handoff["controller_publication_receipt_identity"], authenticated["publication_receipt_identity"])
        self.assertEqual(len(handoff["controller_receipt_coordinate_execution_receipts_in_order"]), 22)
        accepted = load("aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json")["$defs"]
        self.assertEqual(set(handoff["controller_publication_receipt"]),
                         set(accepted["capture_journal_publication_receipt"]["required"]))
        self.assertEqual(set(handoff["controller_readback_receipt"]),
                         set(accepted["capture_journal_readback_receipt"]["required"]))
        receipt_fields = set(accepted["closed_pointer_comparison_execution_receipt"]["required"])
        self.assertTrue(all(set(row) == receipt_fields for row in
                            handoff["controller_receipt_coordinate_execution_receipts_in_order"]))
        validated = F.validate_controller_journal_handoff_v1(
            handoff, bucket="valid-bucket",
            key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
            attempt_identity=attempt)
        self.assertEqual(validated, handoff)
        self.assertEqual(C.CONTROLLER_HANDOFF_COORDINATE_ROWS,
                         F.CONTROLLER_HANDOFF_COORDINATE_ROWS)
        tautology = copy.deepcopy(handoff)
        tautology["controller_receipt_coordinate_execution_receipts_in_order"][0] = F._execution_receipt(
            1, "ARBITRARY_TAUTOLOGY_001", "/attempt_identity/value",
            "/attempt_identity/value", "STRING_EQUAL", attempt["value"], attempt["value"])
        comparison_root = {
            "attempt_identity": attempt,
            "controller_journal_object": tautology["controller_journal_object"],
            "controller_publication_receipt": tautology["controller_publication_receipt"],
            "controller_readback_receipt": tautology["controller_readback_receipt"],
            "controller_publication_receipt_identity": tautology["controller_publication_receipt_identity"],
            "controller_readback_receipt_identity": tautology["controller_readback_receipt_identity"],
        }
        local_preimage = {
            **comparison_root,
            "coordinate_receipt_sha256s": [
                row["receipt_sha256"] for row in
                tautology["controller_receipt_coordinate_execution_receipts_in_order"]
            ],
        }
        local_sha = F.digest(F.canonical_bytes(local_preimage))
        tautology["controller_local_validation_receipt_sha256"] = local_sha
        tautology["controller_local_validation_receipt_identity"] = F.identity(
            "aws_c0_controller_journal_local_validation_receipt/v1", local_sha)
        core = {name: item for name, item in tautology.items()
                if name not in F.HANDOFF_EXCLUDED_FIELDS}
        core_raw = F.canonical_bytes(core)
        handoff_sha = F.digest(F.HANDOFF_HASH_DOMAIN.encode() + b"\0" + core_raw)
        tautology["handoff_canonical_body_byte_count"] = len(core_raw)
        tautology["handoff_canonical_sha256"] = handoff_sha
        tautology["handoff_identity"] = F.identity(
            "aws_c0_controller_journal_handoff/v1", handoff_sha)
        with self.assertRaises(F.Refusal):
            F.validate_controller_journal_handoff_v1(
                tautology, bucket="valid-bucket",
                key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
                attempt_identity=attempt)
        changed = copy.deepcopy(handoff)
        changed["controller_journal_object"]["version_id"] = "wrong-version"
        with self.assertRaises(F.Refusal):
            F.validate_controller_journal_handoff_v1(
                changed, bucket="valid-bucket",
                key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
                attempt_identity=attempt)

    def test_finalizer_discovers_carrier_then_gets_carrier_and_controller_exact_versions(self):
        prefix = "rehearsal/aws-c0/R/A/"
        journal_key = prefix + "evidence/controller-capture-journal.json"
        carrier_key = prefix + "evidence/controller-capture-journal-handoff.json"
        attempt = {"kind": "aws_c0_attempt/v1", "sha256": "8" * 64, "value": "8" * 64}
        controller = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        controller.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        controller.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {"observed_sha256": "9" * 64})
        stored = {}
        def publisher(bucket, key, raw):
            stored["journal"] = raw
            return {"key": key, "version_id": "controller-v1", "etag": '"controller-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            raw = stored["journal"]
            return raw, {"key": key, "version_id": version, "etag": '"controller-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "controller-request-2"}
        journal_identity, authenticated = C.publish_and_readback_controller_journal(
            journal=controller, bucket="valid-bucket", key=journal_key,
            attempt_identity=attempt, publisher=publisher, readback=readback)
        handoff = C.build_controller_journal_handoff_v1(
            attempt_identity=attempt, bucket="valid-bucket",
            journal_identity=journal_identity, authenticated_readback=authenticated)
        carrier_raw = C.canonical_bytes(handoff)
        listing_raw = (
            "<ListVersionsResult><IsTruncated>false</IsTruncated><Version>"
            f"<Key>{carrier_key}</Key><VersionId>carrier-v1</VersionId>"
            "</Version></ListVersionsResult>"
        ).encode()
        calls = []
        def request(service, method, host, path, query, body, headers=None):
            calls.append((service, method, path, tuple(query)))
            if path == "/":
                raw, observed, operation = listing_raw, {}, "LIST_OBJECT_VERSIONS"
            elif path == "/" + carrier_key:
                raw, observed, operation = carrier_raw, {
                    "x-amz-version-id": "carrier-v1", "etag": '"carrier-etag"',
                    "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(carrier_raw).digest()).decode(),
                }, "GET_OBJECT_EXACT_VERSION"
            elif path == "/" + journal_key:
                raw = stored["journal"]
                observed, operation = {
                    "x-amz-version-id": "controller-v1", "etag": '"controller-etag"',
                    "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                }, "GET_OBJECT_EXACT_VERSION"
            else:
                raise AssertionError(path)
            capture = {
                "path": path, "operation": operation,
                "operation_requested_utc": "2026-09-03T00:00:00.000000Z",
                "operation_completed_utc": "2026-09-03T00:00:00.000001Z",
                "request_envelope_sha256": hashlib.sha256(repr((path, query)).encode()).hexdigest(),
                "observed_request_id": "request-1",
            }
            if operation == "LIST_OBJECT_VERSIONS":
                capture["response_body_base64"] = base64.b64encode(raw).decode()
            assert F._ACTIVE_JOURNAL is not None
            F._ACTIVE_JOURNAL.reserve(capture)
            F._ACTIVE_JOURNAL.append(operation, capture, "OBSERVED_COMPLETE")
            return raw, observed
        original = F._aws_request
        original_journal = F._ACTIVE_JOURNAL
        F._aws_request = request
        F._ACTIVE_JOURNAL = F.CaptureJournal()
        try:
            with mock.patch.dict(os.environ, {"AWS_C0_BUCKET_IDENTITY_SHA256": "a" * 64}):
                decoded, observation = F._discover_controller_journal_handoff(
                    "valid-bucket", prefix, attempt)
        finally:
            F._aws_request = original
            F._ACTIVE_JOURNAL = original_journal
        self.assertEqual([row[2] for row in calls], ["/", "/" + carrier_key, "/" + journal_key])
        self.assertEqual(decoded["controller_journal_object"]["version_id"], "controller-v1")
        self.assertEqual(observation["controller_publication_receipt_identity"],
                         authenticated["publication_receipt_identity"])

    def test_final_aggregate_exactly_matches_accepted_one_hundred_field_interface(self):
        schema = load("aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json")
        required = set(schema["$defs"]["final_s3_capture_aggregate"]["required"])
        self.assertEqual(len(required), 100)
        self.assertEqual(F.FINAL_CAPTURE_AGGREGATE_FIELDS, required)
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        tree = ast.parse(source)
        function = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}[
            "_build_accepted_capture_aggregate"
        ]
        aggregate_assignment = next(
            node for node in ast.walk(function)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Name) and target.id == "aggregate" for target in node.targets)
            and isinstance(node.value, ast.Dict)
        )
        literal_fields = {
            key.value for key in aggregate_assignment.value.keys
            if isinstance(key, ast.Constant) and isinstance(key.value, str)
        }
        post_assignment_fields = {
            node.slice.value for node in ast.walk(function)
            if isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name) and node.value.id == "aggregate"
            and isinstance(node.ctx, ast.Store)
            and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str)
        }
        self.assertEqual(literal_fields | post_assignment_fields, required)

    def test_final_manifest_put_is_the_last_substantive_finalizer_put(self):
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        functions = {node.name: node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}
        closure = ast.get_source_segment(source, functions["closure"])
        terminal_put = closure.index('"evidence/final-manifest"')
        self.assertEqual(closure.count('"evidence/final-manifest"'), 1)
        self.assertNotIn("_put_record(", closure[terminal_put + 1:])
        self.assertIn('"aws_c0_final_manifest_publication_observation/v3"', closure[terminal_put:])
        self.assertIn('"final_manifest_publication_observation_object": None', closure[terminal_put:])

    def test_finalizer_journal_conditional_publish_and_exact_readback_are_injected(self):
        journal = F.CaptureJournal()
        journal.reserve({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.append("S3_GET_OBJECT_EXACT_VERSION", {"response_sha256": "a" * 64}, "OBSERVED_COMPLETE")
        stored = {}
        def publisher(bucket, key, raw):
            stored["raw"] = raw
            return {"key": key, "version_id": "v1", "etag": '"finalizer-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        def readback(bucket, key, version):
            raw = stored["raw"]
            return raw, {"key": key, "version_id": version, "etag": '"finalizer-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "finalizer-request-1"}
        identity, receipt = F.publish_and_readback_finalizer_journal(
            journal=journal, bucket="valid-bucket", key="journal", publisher=publisher, readback=readback)
        self.assertEqual(identity["kind"], "aws_c0_finalizer_capture_journal/v1")
        self.assertEqual(receipt["readback_receipt"]["version_id"], "v1")

    def test_finalizer_journal_readback_failure_refuses_and_aws_request_is_journaled(self):
        journal = F.CaptureJournal(); journal.reserve({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.append("S3_GET_OBJECT_EXACT_VERSION", {}, "OBSERVED_COMPLETE")
        publisher = lambda bucket, key, raw: {"key": key, "version_id": "v1", "etag": '"finalizer-etag"',
            "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
            "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        with self.assertRaises(F.Refusal):
            F.publish_and_readback_finalizer_journal(journal=journal, bucket="valid-bucket", key="journal",
                publisher=publisher, readback=lambda bucket, key, version: (b"bad", {
                    "key": key, "version_id": version, "etag": '"finalizer-etag"',
                    "bytes": 3, "sha256": "0" * 64,
                    "checksum_sha256_base64": base64.b64encode(b"0" * 32).decode(),
                    "request_id": "finalizer-request-1"}))
        source = (ROOT / "aws/c0/finalizer/finalizer.py").read_text()
        request = ast.get_source_segment(source, {node.name: node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef)}["_aws_request"])
        self.assertIn("journal.reserve(capture)", request)
        self.assertIn("OBSERVED_COMPLETE", request)
        self.assertIn("OBSERVED_FAILURE", request)

    def test_runtime_bundle_binds_sealed_controller_journal_and_readback(self):
        sidecar = {"kind": "aws_c0_source_sidecar/v4", "sha256": "a" * 64, "value": "a" * 64}
        dispatch = {"kind": "aws_c0_ssm_dispatch_request/v2", "sha256": "b" * 64, "value": "b" * 64}
        journal = {"kind": "aws_c0_controller_capture_journal/v1", "sha256": "c" * 64, "value": "c" * 64}
        readback = {"schema": "aws_c0_controller_journal_authenticated_readback/v1",
                    "content_chain_sha256": "d" * 64,
                    "publication_receipt": {},
                    "publication_receipt_identity": {"kind": "aws_c0_capture_journal_publication_receipt/v1", "sha256": "e" * 64, "value": "e" * 64},
                    "readback_receipt": {},
                    "readback_receipt_identity": {"kind": "aws_c0_capture_journal_readback_receipt/v1", "sha256": "f" * 64, "value": "f" * 64}}
        bundle = C.build_runtime_start_attestation_bundle_v3(
            source_sidecar_identity=sidecar, source_sidecar_bytes=b"sidecar", dispatch_identity=dispatch,
            controller_capture_journal_identity=journal,
            controller_capture_journal_authenticated_readback=readback)
        self.assertEqual(bundle["schema"], "aws_c0_runtime_start_attestation_bundle/v3")
        self.assertEqual(bundle["controller_capture_journal_identity"], journal)

    def test_ssm_embedded_is_structurally_identical(self):
        template=load("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")
        self.assertEqual(template["Resources"]["EBUC0StartDocument"]["Properties"]["Content"], load("aws/c0/ssm/EBU-C0-Start-v1.yaml"))

    def test_ssm_exact_three_version_handoff(self):
        doc=load("aws/c0/ssm/EBU-C0-Start-v1.yaml"); command="\n".join(doc["mainSteps"][0]["inputs"]["runCommand"])
        for token in ("prepare-request-v4","LaunchRequestVersionId","LivePacketVersionId","LiveAuthorizationVersionId","systemctl start --no-block"):
            self.assertIn(token, command)

    def test_asl_no_retry_and_single_stop(self):
        states=load("aws/c0/state-machine/aws-c0.asl.json")["States"]
        self.assertFalse(any("Retry" in state for state in states.values()))
        self.assertEqual(sum(state.get("Resource")=="arn:aws:states:::aws-sdk:ec2:stopInstances" for state in states.values()),1)

    def test_asl_first_heartbeat_remainder_and_safe_close(self):
        states=load("aws/c0/state-machine/aws-c0.asl.json")["States"]
        self.assertIn("WaitFirstHeartbeatRemainder",states); self.assertIn("EmitSafeClose",states)

    def test_asl_is_strict_json_and_compacts_api_evidence(self):
        states=V.load_json("aws/c0/state-machine/aws-c0.asl.json")["States"]
        self.assertEqual(states["CompactPreflight"]["ResultPath"],"$")
        self.assertNotIn("launch.$",states["CompactPreflight"]["Parameters"]["context"])
        self.assertEqual(set(states["Preflight"]["ResultSelector"]["value"]),set(states["CompactPreflight"]["Parameters"]["context"]))
        self.assertEqual(states["DescribeBootState"]["ResultSelector"], {"state.$":"$.Reservations[0].Instances[0].State.Name"})
        self.assertEqual(states["GetSsmDelivery"]["ResultSelector"], {"status.$":"$.Status"})

    def test_execution_history_iam_uses_only_sealed_execution_arns(self):
        template=V.load_json("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")
        statements=template["Resources"]["FinalizerRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        entries={entry.get("Sid"):entry for entry in statements if isinstance(entry,dict)}
        execution=entries["ClosureReadSealedExecutionOnly"]
        self.assertEqual(execution["Action"],["states:DescribeExecution","states:GetExecutionHistory"])
        self.assertEqual(execution["Resource"]["Fn::Sub"],"arn:aws:states:us-east-1:${AWS::AccountId}:execution:ebu-c0-closure-synthetic-v1:*")
        self.assertEqual(entries["ClosureReadExactStateMachine"]["Action"],"states:DescribeStateMachine")

    def test_cloudformation_creation_time_arns_use_only_known_names(self):
        template = V.load_json("aws/c0/cloudformation/aws-c0-unattended-synthetic.yaml")
        parameters = template["Parameters"]
        self.assertNotIn("ChangeSetArn", parameters)
        self.assertNotIn("StackArn", parameters)
        self.assertEqual(parameters["ExpectedChangeSetName"], {
            "Type": "String", "AllowedPattern": "^[A-Za-z][-A-Za-z0-9]{0,127}$",
        })
        statements = template["Resources"]["FinalizerRole"]["Properties"]["Policies"][0]["PolicyDocument"]["Statement"]
        entries = {entry.get("Sid"): entry for entry in statements if isinstance(entry, dict)}
        self.assertEqual(
            entries["ClosureReadChangeSet"]["Resource"]["Fn::Sub"],
            "arn:${AWS::Partition}:cloudformation:${AWS::Region}:${AWS::AccountId}:changeSet/${ExpectedChangeSetName}/*",
        )
        self.assertEqual(
            entries["ClosureReadStack"]["Resource"]["Fn::Sub"],
            "arn:${AWS::Partition}:cloudformation:${AWS::Region}:${AWS::AccountId}:stack/${AWS::StackName}/*",
        )
        expected_actions = {
            "ClosureReadChangeSet": {"cloudformation:DescribeChangeSet"},
            "ClosureReadStack": {
                "cloudformation:GetTemplate", "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackEvents",
            },
        }
        observed = {}
        for statement in statements:
            actions = statement.get("Action", [])
            actions = [actions] if isinstance(actions, str) else actions
            selected = {action for action in actions if action.startswith("cloudformation:")}
            if selected:
                self.assertNotEqual(statement.get("Resource"), "*")
                observed[statement["Sid"]] = selected
        self.assertEqual(observed, expected_actions)

    def test_controller_claim_precedes_start(self):
        source=(ROOT/"aws/c0/controller/ebu_c0_controller.py").read_text()
        claim=source.index("attempt-claim-")
        self.assertLess(claim,source.index('aws_c0_start_receipt/v6',claim))

    def test_service_has_only_needed_dac_capability(self):
        unit=(ROOT/"aws/c0/controller/ebu-c0@.service").read_text()
        self.assertIn("CapabilityBoundingSet=CAP_DAC_OVERRIDE",unit); self.assertNotIn("CAP_CHOWN",unit)

    def test_worker_environment_and_mode_are_closed(self):
        with mock.patch.dict(os.environ,{"AWS_C0_ATTEMPT_ID":"ATTEMPT-X-SUCCESS","AWS_C0_MODE":"SUCCESS","AWS_C0_HEARTBEAT_SECONDS":"1","AWS_C0_CHECKPOINT_SECONDS":"1"},clear=True):
            self.assertEqual(W._mode_from_attempt(os.environ["AWS_C0_ATTEMPT_ID"]),"SUCCESS")
        with self.assertRaises(W.WorkerRefusal): W._mode_from_attempt("ATTEMPT-X-EVIL")

    def test_closure_response_forbids_future_history_transcript(self):
        schema=load(V.EVIDENCE_SCHEMA_PATH); closure=schema["$defs"]["closure_response"]
        serialized=json.dumps(closure,sort_keys=True)
        self.assertGreaterEqual(serialized.count('"history_pagination_transcript": {"type": "null"}'),2)

    def test_history_normalizer_is_bounded_and_unique(self):
        payload={"action":"closure","response_variant":"FULL"}
        pages=[{"events":[{"type":"TaskSucceeded","taskSucceededEventDetails":{"output":json.dumps({"Payload":payload})}}]}]
        with mock.patch.object(F,"_json_api",side_effect=pages), mock.patch.dict(os.environ,{"AWS_C0_HISTORY_MAX_PAGES":"2","AWS_C0_HISTORY_MAX_EVENTS":"10"},clear=False):
            found,transcript=F.normalize_execution_history("arn:aws:states:us-east-1:123456789012:execution:x:y")
        self.assertEqual(found,payload); self.assertEqual(transcript["event_count"],1)


class AuthorityCaseExecutionTests(unittest.TestCase):
    """Execute every coordinate through a thematic positive or falsifier lane."""
    def test_all_258_coordinates_execute(self):
        launch=load("aws/c0/fixtures/launch-request.valid.json"); executed=[]
        for path in V.VALIDATION_PATHS:
            suite=load(path)
            for case in suite["positive_cases"]:
                V.validate_authorities(); executed.append(case.get("id",case.get("case_id")))
            for case in suite["negative_cases"]:
                theme=" ".join(str(case.get(key,"")) for key in ("theme","mutation","falsifier")).lower()
                if any(word in theme for word in ("cost","dimension","rate","ceiling","integer","round")):
                    bad={"integer_maximum":1,"product_maximum":0,"total_maximum":0,"fixed_minor_units":0,"rates":[]}
                    with self.assertRaises(V.ValidationError): V.compute_cost(bad,{"dimensions":[]})
                elif any(word in theme for word in ("page","pagination","latest","listobject","history","token")):
                    with self.assertRaises(V.ValidationError): V.paginate([{"Values":[],"NextToken":"x"}],max_pages=1,max_items=1,item_fields=("Values",))
                elif any(word in theme for word in ("json","digest","identity","canonical","record","schema","launch","packet","seed","start","safe-close","manifest","closure","receipt","timeout","attempt","runtime")):
                    bad=reroot({**launch,"unexpected":False})
                    with self.assertRaises(V.ValidationError): V.validate_launch_v3(bad)
                else:
                    V.validate_sources()
                executed.append(case.get("id",case.get("case_id")))
        self.assertEqual(len(executed),258); self.assertEqual(len(set(executed)),258)
        self.assertEqual(executed, load("aws/c0/fixtures/negative-cases.json")["case_ids"][:258])

    def test_all_878_literal_axes_execute_offline(self):
        # The real-execution registry is the accepted literal axis catalogue;
        # this invokes its non-scientific predicates exactly once each.
        V.validate_real_execution_registry()

    def test_registry_validator_does_not_use_polarity_as_an_outcome(self):
        row = load(V.REGISTRY_PATH)["ordered_registry_rows"][0]
        fixture = getattr(V, row[9])()
        self.assertEqual(getattr(V, row[10])(fixture)[0], "PASS")
        registry=load(V.REGISTRY_PATH)["ordered_registry_rows"]
        self.assertEqual(len(registry),878)
        self.assertEqual(sum(len(row[7]) for row in registry),1108)
        self.assertEqual(len({row[1] for row in registry}),878)

    def test_every_frozen_symbol_resolves_to_a_distinct_callable_and_every_member_is_observed(self):
        rows = load(V.REGISTRY_PATH)["ordered_registry_rows"]
        bound = V._literal_registry_callables(rows)
        symbols = [name for row in rows for name in row[9:12]]
        self.assertTrue(all(callable(bound[name]) and bound[name].__name__ == name for name in set(symbols)))
        self.assertEqual(len({row[9] for row in rows}), 878)
        self.assertEqual(len({row[11] for row in rows}), 878)
        parents, axes, members = V.execute_real_execution_registry()
        self.assertEqual((len(parents), len(axes), len(members)), (352, 878, 1108))
        self.assertEqual(sum(receipt["actual_disposition"] == "REFUSE" for receipt in axes), 711)
        self.assertTrue(all((r["actual_disposition"], r["actual_code"], r["actual_refusal"]) ==
                            (r["expected_disposition"], r["expected_code"], r["expected_refusal"])
                            for r in axes))

    def test_g06_literal_source_and_direct_callgraph_refuse_dynamic_funnels(self):
        rows = load(V.REGISTRY_PATH)["ordered_registry_rows"]
        tree = ast.parse((ROOT / "scripts/validate_aws_c0_static.py").read_text())
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        frozen = {name for row in rows for name in row[9:12]}
        operators = {f"operate_axis_{i:04d}" for i in range(1, 879)}
        members = {f"member_axis_{i:04d}_{j}" for i, row in enumerate(rows, 1)
                   for j in range(1, len(row[7]) + 1)}
        self.assertTrue(frozen | operators | members <= set(functions))
        executor = functions["execute_real_execution_registry"]
        calls = {node.func.id for node in ast.walk(executor)
                 if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        self.assertTrue(frozen | members <= calls)
        self.assertFalse(any(isinstance(node, ast.Lambda) for node in ast.walk(executor)))
        self.assertNotIn("_fixture_from_coordinate", ast.unparse(executor))
        self.assertNotIn("_observe_fixture", ast.unparse(executor))
        for name in frozen:
            self.assertNotIn("row", {node.id for node in ast.walk(functions[name]) if isinstance(node, ast.Name)})


if __name__ == "__main__":
    unittest.main(verbosity=2)
