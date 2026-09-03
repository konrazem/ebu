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
        current = reroot({**self.launch, "schema": "aws_c0_launch_request/v4"})
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
                         "request_id": "request-1", "tls_certificate_sha256": "a" * 64}

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
        for role in ("LAUNCH_REQUEST_V4", "LIVE_PACKET_V4", "LIVE_AUTHORIZATION_V4"):
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
        self.assertIn("FROZEN_PRELIVE_OBJECT_COUNT = 21", source)
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
            self.assertEqual((bucket, key, version), ("valid-bucket", "journal", "v1"))
            raw = published[0][2]
            return raw, {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                         "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                         "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode(),
                         "request_id": "request-1"}
        journal_identity, receipt = C.publish_and_readback_controller_journal(
            journal=journal, bucket="valid-bucket", key="journal", publisher=publisher, readback=readback)
        self.assertEqual(len(published), 1)
        self.assertEqual(journal_identity["kind"], "aws_c0_controller_capture_journal/v1")
        self.assertEqual(receipt["readback_receipt"]["version_id"], "v1")
        with self.assertRaises(C.Refusal): journal.seal()

    def test_controller_journal_refuses_bad_exact_version_readback(self):
        journal = C.CaptureJournal("EC2_INSTANCE_PROFILE_CONTROLLER")
        journal.reserve_for_operation({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        journal.complete("S3_GET_OBJECT_EXACT_VERSION", "EC2_INSTANCE_PROFILE", {})
        def publisher(bucket, key, raw):
            return {"key": key, "version_id": "v1", "etag": '"journal-etag"',
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "checksum_sha256_base64": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
        with self.assertRaises(C.Refusal):
            C.publish_and_readback_controller_journal(
                journal=journal, bucket="valid-bucket", key="journal", publisher=publisher,
                readback=lambda bucket, key, version: (b"wrong", {
                    "key": key, "version_id": version, "etag": '"journal-etag"',
                    "bytes": 5, "sha256": "0" * 64,
                    "checksum_sha256_base64": base64.b64encode(b"0" * 32).decode(),
                    "request_id": "request-1"}))

    def test_controller_journal_lifecycle_is_in_preparation_callgraph(self):
        source = (ROOT / "aws/c0/controller/ebu_c0_controller.py").read_text()
        tree = ast.parse(source)
        functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
        prepare = ast.get_source_segment(source, functions["prepare_request"])
        self.assertIn("CaptureJournal", prepare)
        self.assertIn("publish_and_readback_controller_journal", prepare)
        self.assertIn("build_controller_journal_handoff_v1", prepare)
        self.assertIn("publish_controller_journal_handoff", prepare)
        self.assertIn("CONTROLLER_JOURNAL_HANDOFF_SUFFIX", prepare)
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
        controller_identity, authenticated = C.publish_and_readback_controller_journal(
            journal=controller, bucket="valid-bucket",
            key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal.json",
            publisher=publisher, readback=readback)
        attempt = {"kind": "aws_c0_attempt/v1", "sha256": "b" * 64, "value": "b" * 64}
        handoff = C.build_controller_journal_handoff_v1(
            attempt_identity=attempt, bucket="valid-bucket",
            journal_identity=controller_identity, authenticated_readback=authenticated)
        self.assertEqual(handoff["controller_journal_object"]["version_id"], "controller-version-1")
        self.assertEqual(handoff["controller_publication_receipt_identity"], authenticated["publication_receipt_identity"])
        self.assertEqual(len(handoff["controller_receipt_coordinate_execution_receipts_in_order"]), 22)
        validated = F.validate_controller_journal_handoff_v1(
            handoff, bucket="valid-bucket",
            key="rehearsal/aws-c0/R/A/evidence/controller-capture-journal-handoff.json",
            attempt_identity=attempt)
        self.assertEqual(validated, handoff)
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
            publisher=publisher, readback=readback)
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
                return listing_raw, {}
            if path == "/" + carrier_key:
                return carrier_raw, {"x-amz-version-id": "carrier-v1", "etag": '"carrier-etag"',
                                     "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(carrier_raw).digest()).decode()}
            if path == "/" + journal_key:
                raw = stored["journal"]
                return raw, {"x-amz-version-id": "controller-v1", "etag": '"controller-etag"',
                             "x-amz-checksum-sha256": base64.b64encode(hashlib.sha256(raw).digest()).decode()}
            raise AssertionError(path)
        original = F._aws_request
        F._aws_request = request
        try:
            with mock.patch.dict(os.environ, {"AWS_C0_BUCKET_IDENTITY_SHA256": "a" * 64}):
                decoded, observation = F._discover_controller_journal_handoff(
                    "valid-bucket", prefix, attempt)
        finally:
            F._aws_request = original
        self.assertEqual([row[2] for row in calls], ["/", "/" + carrier_key, "/" + journal_key])
        self.assertEqual(decoded["controller_journal_object"]["version_id"], "controller-v1")
        self.assertEqual(observation["controller_publication_receipt_identity"],
                         authenticated["publication_receipt_identity"])

    def test_three_coordinate_aggregate_binds_distinct_keys_and_carrier_observation(self):
        attempt = {"kind": "aws_c0_attempt/v1", "sha256": "a" * 64, "value": "a" * 64}
        handoff = {
            "attempt_identity": attempt,
            "controller_journal_object": {"bucket": "valid-bucket",
                                            "key": "prefix/evidence/controller-capture-journal.json",
                                            "version_id": "controller-v1", "etag": '"controller-etag"',
                                            "checksum_sha256_base64": base64.b64encode(bytes.fromhex("b" * 64)).decode(),
                                            "byte_count": 200, "object_sha256": "b" * 64,
                                            "content_chain_sha256": "6" * 64},
            "controller_publication_receipt_identity": {"kind": "aws_c0_capture_journal_publication_receipt/v1", "sha256": "c" * 64, "value": "c" * 64},
            "controller_readback_receipt_identity": {"kind": "aws_c0_capture_journal_readback_receipt/v1", "sha256": "d" * 64, "value": "d" * 64},
            "controller_local_validation_receipt_identity": {"kind": "aws_c0_controller_journal_local_validation_receipt/v1", "sha256": "7" * 64, "value": "7" * 64},
            "controller_local_validation_receipt_sha256": "7" * 64,
            "handoff_identity": {"kind": "aws_c0_controller_journal_handoff/v1", "sha256": "e" * 64, "value": "e" * 64},
            "handoff_canonical_sha256": "e" * 64,
        }
        carrier = {"key": "prefix/evidence/controller-capture-journal-handoff.json",
                   "schema": "aws_c0_controller_journal_handoff_external_proof/v1",
                   "version_id": "carrier-v1", "etag": '"carrier-etag"',
                   "checksum_sha256_base64": base64.b64encode(bytes.fromhex("f" * 64)).decode(),
                   "bytes": 300, "sha256": "f" * 64,
                   "list_transcript_identity": {"kind": "aws_c0_pagination_transcript/v1", "sha256": "1" * 64, "value": "1" * 64},
                   "handoff_identity": handoff["handoff_identity"],
                   "handoff_canonical_sha256": handoff["handoff_identity"]["sha256"],
                   "controller_journal_version_id": "controller-v1",
                   "controller_publication_receipt_identity": handoff["controller_publication_receipt_identity"],
                   "controller_envelope_count": 3}
        finalizer = F.CaptureJournal()
        finalizer.reserve({"operation": "S3_GET_OBJECT_EXACT_VERSION"})
        finalizer.append("S3_GET_OBJECT_EXACT_VERSION", {"response_sha256": "2" * 64}, "OBSERVED_COMPLETE")
        projection = finalizer.aggregate()
        _, finalizer_identity = finalizer.seal()
        publication = {"key": "prefix/evidence/finalizer-capture-journal.json", "version_id": "finalizer-v1",
                       "etag": '"finalizer-etag"', "bytes": 100, "sha256": "3" * 64,
                       "checksum_sha256_base64": base64.b64encode(bytes.fromhex("3" * 64)).decode()}
        publication_sha = F.digest(F.canonical_bytes({"bucket_name": "valid-bucket", **publication}))
        readback_receipt = {**publication, "request_id": "finalizer-request-1"}
        readback_sha = F.digest(F.canonical_bytes({"bucket_name": "valid-bucket", **readback_receipt}))
        publication_identity = F.identity("aws_c0_capture_journal_publication_receipt/v1", publication_sha)
        readback_identity = F.identity("aws_c0_capture_journal_readback_receipt/v1", readback_sha)
        finalizer_readback = {"schema": "aws_c0_journal_authenticated_readback/v1",
                              "content_chain_sha256": "2" * 64,
                              "publication_receipt": publication,
                              "publication_receipt_identity": publication_identity,
                              "readback_receipt": readback_receipt,
                              "readback_receipt_identity": readback_identity}
        aggregate = F.build_three_coordinate_capture_aggregate(
            attempt_identity=attempt, handoff=handoff, carrier_observation=carrier,
            finalizer_journal_identity=finalizer_identity,
            finalizer_readback=finalizer_readback, finalizer_projection=projection)
        self.assertEqual(aggregate["controller_journal_version_id"], "controller-v1")
        self.assertEqual(aggregate["controller_publication_receipt_identity"], handoff["controller_publication_receipt_identity"])
        self.assertEqual(aggregate["total_envelope_count"], 4)

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
        sidecar = {"kind": "aws_c0_source_sidecar/v3", "sha256": "a" * 64, "value": "a" * 64}
        dispatch = {"kind": "aws_c0_ssm_dispatch_request/v2", "sha256": "b" * 64, "value": "b" * 64}
        journal = {"kind": "aws_c0_controller_capture_journal/v1", "sha256": "c" * 64, "value": "c" * 64}
        readback = {"schema": "aws_c0_controller_journal_authenticated_readback/v1",
                    "content_chain_sha256": "d" * 64,
                    "publication_receipt": {},
                    "publication_receipt_identity": {"kind": "aws_c0_capture_journal_publication_receipt/v1", "sha256": "e" * 64, "value": "e" * 64},
                    "readback_receipt": {},
                    "readback_receipt_identity": {"kind": "aws_c0_capture_journal_readback_receipt/v1", "sha256": "f" * 64, "value": "f" * 64}}
        bundle = C.build_runtime_start_attestation_bundle_v2(
            source_sidecar_identity=sidecar, source_sidecar_bytes=b"sidecar", dispatch_identity=dispatch,
            controller_capture_journal_identity=journal,
            controller_capture_journal_authenticated_readback=readback)
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

    def test_controller_claim_precedes_start(self):
        source=(ROOT/"aws/c0/controller/ebu_c0_controller.py").read_text()
        claim=source.index("attempt-claim-")
        self.assertLess(claim,source.index('aws_c0_start_receipt/v5',claim))

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
