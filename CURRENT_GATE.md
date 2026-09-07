# AWS-C0 current gate

- Commit: `5a7c3dd`; worktree clean.
- First failing validation: `DeploymentSequenceTests.test_complete_schema_valid_chain_through_public_prepublication_gate` — the current live-packet schema requires `runtime_control_reconstruction_set_identity` and its complete evidence set.
- Active local paths: `aws/c0/finalizer/finalizer.py`, `scripts/build_aws_c0_preparation_records.py`, `scripts/build_aws_c0_sequence_schema.py`, generated `aws_c0_deployment_sequence_evidence_schema.json`, and `tests/aws/test_aws_c0_unattended_synthetic.py`.
- Authority: one existing `t3.small` platform smoke only, aggregate USD50 cap; R64 permits at most three exact guarded `ec2:DescribeSecurityGroups` reads; scientific execution is excluded. No AWS call or IAM change has occurred in this repair.
- Gate evidence: `aws_c0_deployment_sequence_correction_contract.json` records the exact R64 packet and current test result; `aws_c0_deployment_sequence_evidence_schema.json` is the deterministic current schema. Historical frozen source hashes remain `8ae16c96…ba438` and `c8edb270…7fe99`.
