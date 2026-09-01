from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[2]
AWS_ROOT = ROOT / "aws"
REHEARSAL = AWS_ROOT / "rehearsals" / "2026-09-01"


class AwsCampaignAssetsTests(unittest.TestCase):
    def test_all_aws_json_files_parse(self) -> None:
        for path in AWS_ROOT.rglob("*.json"):
            with self.subTest(path=path.relative_to(ROOT)):
                json.loads(path.read_text(encoding="utf-8"))

    def test_historical_result_hash_is_exact(self) -> None:
        result = REHEARSAL / "synthetic-result.txt"
        checksum = (REHEARSAL / "synthetic-result.txt.sha256").read_text(
            encoding="utf-8"
        ).split()[0]
        self.assertEqual(hashlib.sha256(result.read_bytes()).hexdigest(), checksum)
        self.assertEqual(
            checksum,
            "63b9d408bbcc6b99ef58c301d41547d21ba06cee755ae68227cd7c4bd8b8a6dc",
        )

    def test_records_are_non_scientific_and_non_executable(self) -> None:
        record = json.loads(
            (AWS_ROOT / "campaigns" / "aws-infrastructure-rehearsal-20260901.json")
            .read_text(encoding="utf-8")
        )
        template = json.loads(
            (AWS_ROOT / "campaigns" / "campaign-request.template.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertFalse(record["scientific_execution_authorized"])
        self.assertEqual(record["scientific_configuration"], "NOT_RUN")
        self.assertEqual(record["scientific_workload"], "NOT_RUN")
        self.assertFalse(template["scientific_execution_authorized"])
        self.assertEqual(template["status"], "DRAFT_NON_EXECUTABLE")
        self.assertIn("REQUIRED_", template["scientific_source"]["commit"])
        self.assertEqual(template["step_functions"]["workflow_type"], "STANDARD")
        self.assertEqual(
            template["stage_e"]["accepted_evidence_sha256"],
            "2b2b5cc213082392bda715e82b9a23f670b7628b92848ace9455724f903bc345",
        )

    def test_historical_script_hashes_are_exact(self) -> None:
        expected = {
            "run-ebu-rehearsal-from-mac.sh":
                "82a3fcaae4d92fbae08d9c394e8c653e73ca66403259612b26b776b0d92ce6cb",
            "ebu-rehearsal-vm.sh":
                "3391fa0803ef5d911cefe17caa198e252394451316b2add6d1badd024823956c",
        }
        for filename, digest in expected.items():
            with self.subTest(filename=filename):
                self.assertEqual(
                    hashlib.sha256((REHEARSAL / filename).read_bytes()).hexdigest(),
                    digest,
                )

    def test_rehearsal_policy_is_prefix_scoped_and_has_no_ecr_write(self) -> None:
        policy = json.loads(
            (AWS_ROOT / "iam" / "rehearsal-ec2-role-policy.json").read_text(
                encoding="utf-8"
            )
        )
        actions: list[str] = []
        resources: list[str] = []
        for statement in policy["Statement"]:
            action = statement["Action"]
            actions.extend(action if isinstance(action, list) else [action])
            resource = statement["Resource"]
            resources.extend(resource if isinstance(resource, list) else [resource])
        self.assertNotIn("*", actions)
        self.assertNotIn("ecr:PutImage", actions)
        self.assertNotIn("ecr:InitiateLayerUpload", actions)
        self.assertIn(
            "arn:aws:s3:::ebu-stage-f-results-k7m4p2/rehearsal/*", resources
        )
        self.assertNotIn("arn:aws:s3:::ebu-stage-f-results-k7m4p2/*", resources)

    def test_shell_scripts_have_valid_bash_syntax(self) -> None:
        scripts = [AWS_ROOT / "scripts" / "download-results.sh"]
        historical = [
            REHEARSAL / "run-ebu-rehearsal-from-mac.sh",
            REHEARSAL / "ebu-rehearsal-vm.sh",
        ]
        scripts.extend(path for path in historical if path.exists())
        for script in scripts:
            completed = subprocess.run(
                ["bash", "-n", str(script)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
