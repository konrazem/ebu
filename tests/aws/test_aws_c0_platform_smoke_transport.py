import base64
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "platform_smoke_transport", ROOT / "aws/c0/bootstrap/platform_smoke_transport.py"
)
P = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(P)


def worker_stdout(attempt):
    def sha(value):
        return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    rows = [{
        "account": P.ACCOUNT, "attempt_id": attempt, "container_execution": True,
        "image_manifest_sha256": P.IMAGE_MANIFEST_SHA256, "image_reference": P.IMAGE_REFERENCE,
        "instance_id": P.INSTANCE, "region": P.REGION,
        "schema": "aws_c0_user_operated_platform_smoke_host_binding/v1",
        "scientific_execution": False,
    }]
    for sequence in range(2):
        rows.append({"event": "heartbeat", "sequence": sequence,
                     "monotonic_nanoseconds": sequence + 1,
                     "payload_sha256": sha({"attempt_id": attempt, "event": "heartbeat", "mode": "SUCCESS", "sequence": sequence})})
        rows.append({"event": "checkpoint", "sequence": sequence,
                     "synthetic_progress_units": sequence + 1,
                     "payload_sha256": sha({"attempt_id": attempt, "event": "checkpoint", "mode": "SUCCESS",
                                            "sequence": sequence, "synthetic_progress_units": sequence + 1})})
    manifest = sha({"attempt_id": attempt, "checkpoint_count": 2, "heartbeat_count": 2,
                    "mode": "SUCCESS", "schema": "aws_c0_synthetic_manifest_payload/v1",
                    "synthetic_progress_units": 2})
    rows.append({"event": "terminal", "disposition": "AWS_C0_SYNTHETIC_PASS",
                 "failure_phase": "NONE", "failure_code": None,
                 "last_heartbeat_sequence": 1, "last_checkpoint_sequence": 1,
                 "synthetic_manifest_sha256": manifest})
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows)


class PlatformSmokeTransportTests(unittest.TestCase):
    attempt = "ATTEMPT-USER-20260908T120000Z-SUCCESS"

    def material(self):
        plan = P.build_plan(self.attempt)
        script = base64.b64decode(plan["command_script_base64"])
        command_id = "12345678-1234-1234-1234-123456789abc"
        send = {"Command": {**plan["send_command_request"], "CommandId": command_id}}
        invocation = {"CommandId": command_id, "InstanceId": P.INSTANCE,
                      "DocumentName": P.DOCUMENT, "Status": "Success", "ResponseCode": 0,
                      "StandardOutputContent": worker_stdout(self.attempt), "StandardErrorContent": ""}
        caller = {"Account": P.ACCOUNT, "Arn": "arn:aws:iam::" + P.ACCOUNT + ":user/test", "UserId": "AIDATEST"}
        stopped = {"Reservations": [{"OwnerId": P.ACCOUNT, "Instances": [{
            "InstanceId": P.INSTANCE, "InstanceType": "t3.small", "State": {"Code": 80, "Name": "stopped"}
        }]}]}
        uploaded = invocation["StandardOutputContent"].encode()
        sha256 = hashlib.sha256(uploaded).hexdigest()
        checksum = base64.b64encode(bytes.fromhex(sha256)).decode()
        upload = {"VersionId": "exact-upload-version", "ChecksumSHA256": checksum, "ETag": '"upload-etag"'}
        retrieved = uploaded
        retrieval = {"VersionId": "exact-upload-version", "ContentLength": len(retrieved),
                     "ChecksumSHA256": checksum, "ETag": '"upload-etag"', "Metadata": {"sha256": sha256}}
        return plan, script, caller, send, invocation, stopped, uploaded, upload, retrieved, retrieval

    @staticmethod
    def names():
        return ("plan", "script", "caller", "send", "invocation", "stopped",
                "uploaded", "upload", "retrieved", "retrieval")

    def test_plan_uses_managed_document_and_binds_exact_script_and_image(self):
        plan, script, *_ = self.material()
        self.assertEqual(plan["document_name"], "AWS-RunShellScript")
        self.assertEqual(plan["temporary_private_document_operations"], 0)
        self.assertEqual(plan["iam_mutations"], 0)
        self.assertEqual(plan["result_bucket"], "ebu-stage-f-results-k7m4p2")
        self.assertTrue(plan["result_key"].startswith("rehearsal/"))
        self.assertEqual(plan["maximum_s3_puts"], 1)
        self.assertEqual(plan["maximum_s3_exact_version_gets"], 1)
        self.assertEqual(plan["command_script_sha256"], hashlib.sha256(script).hexdigest())
        self.assertEqual(plan["send_command_request"]["Parameters"]["commands"], [script.decode()])
        self.assertIn(P.IMAGE_REFERENCE.encode(), script)
        self.assertNotIn(b"aws ssm", script)
        self.assertNotIn(b"aws iam", script)
        self.assertNotIn(b"create-document", script)

    def test_complete_pass_binds_command_invocation_and_stopped_receipt(self):
        evidence = P.seal_evidence(**dict(zip(self.names(), self.material())))
        self.assertEqual(evidence["disposition"], "FORMAL_PLATFORM_SMOKE_PASS")
        self.assertEqual(evidence["ssm_command_id"], "12345678-1234-1234-1234-123456789abc")
        self.assertEqual(evidence["final_stopped_instance"]["state"], "stopped")
        self.assertFalse(evidence["prior_manual_run_used_as_formal_evidence"])
        self.assertEqual(evidence["worker_validation"]["checkpoint_count"], 2)
        self.assertEqual(evidence["s3_result_object"]["version_id"], "exact-upload-version")
        self.assertTrue(evidence["s3_result_object"]["exact_version_retrieval_verified"])

    def test_mismatches_refuse_or_fail_closed(self):
        fields = list(self.material())
        fields[3]["Command"]["DocumentName"] = "EBU-C0-Temporary"
        with self.assertRaises(P.Refusal):
            P.seal_evidence(**dict(zip(self.names(), fields)))
        fields = list(self.material())
        fields[5]["Reservations"][0]["Instances"][0]["State"] = {"Code": 16, "Name": "running"}
        with self.assertRaises(P.Refusal):
            P.seal_evidence(**dict(zip(self.names(), fields)))
        fields = list(self.material())
        fields[4]["StandardErrorContent"] = "worker failed"
        evidence = P.seal_evidence(**dict(zip(self.names(), fields)))
        self.assertEqual(evidence["disposition"], "FORMAL_PLATFORM_SMOKE_FAIL")
        fields = list(self.material())
        fields[8] = fields[8] + b"tampered"
        with self.assertRaisesRegex(P.Refusal, "retrieval bytes"):
            P.seal_evidence(**dict(zip(self.names(), fields)))
        fields = list(self.material())
        fields[9]["VersionId"] = "other-version"
        with self.assertRaisesRegex(P.Refusal, "returned VersionId"):
            P.seal_evidence(**dict(zip(self.names(), fields)))

    def test_cli_preparation_is_exclusive_and_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "sealed"
            self.assertEqual(P.main(["prepare", "--attempt-id", self.attempt, "--output-dir", str(output)]), 0)
            plan = json.loads((output / "plan.json").read_text())
            P.validate_plan(plan, (output / "command-script.sh").read_bytes())
            self.assertEqual(json.loads((output / "parameters.json").read_text()),
                             plan["send_command_request"]["Parameters"])
            self.assertEqual(P.main(["prepare", "--attempt-id", self.attempt, "--output-dir", str(output)]), 1)


if __name__ == "__main__":
    unittest.main()
