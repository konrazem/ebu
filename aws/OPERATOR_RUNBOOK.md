# AWS operator runbook

Status: **infrastructure operations only; no scientific execution authority**

This is the short, copyable companion to the campaign plan. Run commands from
a normal Mac Terminal. None of the commands below configures or starts an EBU
scientific experiment.

## 1. Check the rehearsal instance and cost state

```bash
aws login

aws ec2 describe-instances \
  --instance-ids i-048bac00bdb540a4e \
  --region us-east-1 \
  --query 'Reservations[0].Instances[0].State.Name' \
  --output text
```

Expected current value: `stopped`.

If it ever says `running` after a rehearsal and no work should continue:

```bash
aws ec2 stop-instances \
  --instance-ids i-048bac00bdb540a4e \
  --region us-east-1

aws ec2 wait instance-stopped \
  --instance-ids i-048bac00bdb540a4e \
  --region us-east-1
```

Stopping is reversible. It pauses EC2 instance usage charges but not small
ongoing EBS and S3 storage charges. Other provisioned services such as Elastic
IP addresses, NAT gateways, VPC endpoints, snapshots or retained logs can also
charge if present. Do not terminate the instance unless its retained disk is
intentionally disposable.

## 2. Download and verify the completed rehearsal result

From the repository root:

```bash
./aws/scripts/download-results.sh \
  's3://ebu-stage-f-results-k7m4p2/rehearsal/i-048bac00bdb540a4e/20260901T110354Z/' \
  "$HOME/Downloads/ebu-rehearsal-20260901"
```

The destination must be absent or empty. The script is read-only and verifies
the downloaded checksum manifest.

To retrieve the exact retained S3 version of the result:

```bash
mkdir -p "$HOME/Downloads/ebu-rehearsal-exact-version"

aws s3api get-object \
  --bucket ebu-stage-f-results-k7m4p2 \
  --key rehearsal/i-048bac00bdb540a4e/20260901T110354Z/synthetic-result.txt \
  --version-id 'UHL7dn2kIH2SZB85voyhbxqL3J.Oqg2.' \
  --region us-east-1 \
  "$HOME/Downloads/ebu-rehearsal-exact-version/synthetic-result.txt"

cd "$HOME/Downloads/ebu-rehearsal-exact-version"
printf '%s  %s\n' \
  '63b9d408bbcc6b99ef58c301d41547d21ba06cee755ae68227cd7c4bd8b8a6dc' \
  'synthetic-result.txt' | shasum -a 256 --check
```

Expected final line: `synthetic-result.txt: OK`.

## 3. Before another infrastructure rehearsal

1. Use a named AWS identity with MFA instead of root for routine work.
2. Confirm the activity is labelled non-scientific and has no EBU campaign
   configuration.
3. Freeze the resource names, maximum vCPUs, time limit and cost ceiling.
4. Start only the resources required by that rehearsal.
5. Verify S3 receipts and hashes, then scale compute to zero.

The exact scripts under `rehearsals/2026-09-01/` are historical evidence. They
contain fixed resource IDs and IAM setup steps; do not treat them as a reusable
production launcher.

## 4. When preparing a real experiment

Ask the Codex coordinator to prepare an AWS Stage F launch packet. This request
authorizes preparation and validation only. The coordinator must:

1. verify the accepted Stage E identities and current CI state;
2. verify an independently accepted AWS/Linux execution binding exists;
3. build and validate the exact image, then bind it by ECR digest;
4. freeze the Standard workflow, Batch job definition, compute, timeout,
   checkpoints, retry policy, S3 prefix, IAM roles and cost envelope;
5. show the complete human-readable packet and its hash; and
6. stop without submitting until the user explicitly authorizes that exact
   packet.

After that explicit authorization, the coordinator starts one Step Functions
Standard workflow. Wait until it reports the workflow execution ARN, Batch job
ID, durable S3 start receipt and first heartbeat. At that point the Mac and
Codex may be closed; AWS continues the run.

On return, provide either the workflow execution ARN or campaign ID to Codex.
The coordinator can check AWS state and retrieve the immutable S3 prefix. Raw
files and checksums are preserved before any separately authorized scientific
interpretation.

## 5. What is not ready today

Stage E itself is accepted, but the current integrated line has a later exact
path-closure failure, and the accepted local Stage F binding is Windows/NTFS
specific. There is no accepted AWS/Linux binding or provisioned Standard
workflow/Batch campaign backend yet. Therefore no real AWS scientific launch
may occur from this branch.
