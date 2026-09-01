# AWS infrastructure rehearsal — 2026-09-01

Evidence class: **non-scientific infrastructure rehearsal**

No EBU scientific configuration, runner, trajectory, model-state advancement,
registered campaign or outcome inspection occurred.

## Outcome

- EC2 instance `i-048bac00bdb540a4e` verified as Ubuntu 24.04.4 LTS,
  x86-64, `t3.small`.
- Root EBS volume encrypted; IMDSv2 required; security group had zero inbound
  rules.
- Docker 29.7.2 installed; `hello-world` passed.
- AWS CLI 2.36.36 installed on the VM.
- VM identity resolved to assumed role `EBU-Rehearsal-EC2-Role`.
- ECR repository `ebu/ebu-stage-f` was immutable, AES-256 encrypted and empty;
  authentication/read access passed, then Docker login was removed.
- Synthetic result and checksum uploaded to S3 with AES-256 server-side
  encryption and a retained S3 version ID.
- Fresh VM download, fresh Mac download and a second Mac download after the
  instance stopped all matched SHA-256.
- Instance stopped after success; it was not terminated.

## Durable object

```text
s3://ebu-stage-f-results-k7m4p2/rehearsal/i-048bac00bdb540a4e/20260901T110354Z/synthetic-result.txt
```

SHA-256:

```text
63b9d408bbcc6b99ef58c301d41547d21ba06cee755ae68227cd7c4bd8b8a6dc
```

Checksum object:

```text
s3://ebu-stage-f-results-k7m4p2/rehearsal/i-048bac00bdb540a4e/20260901T110354Z/synthetic-result.txt.sha256
```

S3 version ID:

```text
UHL7dn2kIH2SZB85voyhbxqL3J.Oqg2.
```

SSM command ID:

```text
414cf5f4-0c51-4280-8539-9bbcb7fcf8b0
```

## Retained files

- `synthetic-result.txt` — exact downloaded S3 result bytes.
- `synthetic-result.txt.sha256` — portable checksum manifest.
- `s3-head-object.json` — retained storage metadata.
- `run-ebu-rehearsal-from-mac.sh` and `ebu-rehearsal-vm.sh` — exact scripts
  used for the completed run; historical, resource-specific, and not a Stage F
  runner.

Historical script SHA-256 values:

```text
82a3fcaae4d92fbae08d9c394e8c653e73ca66403259612b26b776b0d92ce6cb  run-ebu-rehearsal-from-mac.sh
3391fa0803ef5d911cefe17caa198e252394451316b2add6d1badd024823956c  ebu-rehearsal-vm.sh
```

The Mac control script used the then-active AWS root browser login to attach a
narrow inline role policy. No root access keys were created. Future routine
operations must use a named administrative identity with MFA and narrower
launch permissions.

Stopped EC2 instances do not incur instance usage/data-transfer charges, but
the retained EBS volume and S3 objects continue to incur storage charges. See
[AWS EC2 stopped-instance costs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html#stop-start-costs).
