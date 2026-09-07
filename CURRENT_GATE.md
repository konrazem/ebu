# AWS-C0 current gate

- Last implementation commit: `3e4678b`; this checkpoint records its clean worktree state.
- First failing validation: `DeploymentSequenceTests.test_complete_schema_valid_chain_through_public_prepublication_gate` — the current live-packet schema requires `runtime_control_reconstruction_set_identity` and its complete evidence set.
- Active local paths: `aws/c0/finalizer/finalizer.py`, `scripts/build_aws_c0_preparation_records.py`, `scripts/build_aws_c0_sequence_schema.py`, generated `aws_c0_deployment_sequence_evidence_schema.json`, and `tests/aws/test_aws_c0_unattended_synthetic.py`.
- Authority: one existing `t3.small` platform smoke only, aggregate USD50 cap; R64 permits at most three exact guarded `ec2:DescribeSecurityGroups` reads; scientific execution is excluded. No AWS call or IAM change has occurred in this repair.
- Gate evidence: `aws_c0_deployment_sequence_correction_contract.json` records the exact R64 packet and current test result; `aws_c0_deployment_sequence_evidence_schema.json` is the deterministic current schema. Historical frozen source hashes remain `8ae16c96…ba438` and `c8edb270…7fe99`.
- The candidate-only envelope is now paired with a reviewed source-bound attachment for ACCOUNT_REGION, INSTANCE_PROFILE_SOLE_ROLE, and VPC_NETWORK_PATH. It replays retained source bundles under an externally expected context identity, shared R02, session/freshness/phase bindings, and sealed EC2 pagination bounds. It remains `PARTIAL_SOURCE_BOUND_NOT_READY` and cannot enter the v1 live gate.
- Next local unit: add the next missing source-specific reconstruction producer and attach it under the same immutable context rules. This remains local design/validation work; it does not authorize or require an AWS call.
