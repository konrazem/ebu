# EBU AWS campaign operations

This directory records AWS infrastructure rehearsals and the prospective
operational design for unattended EBU campaigns. It is deliberately separate
from scientific authority, scientific implementation, and scientific
execution.

## Current status

- Branch: `aws/campaign-orchestration`
- Branch base: `a4af44afd3c878311ee373bc19e3be14b2aacec5`
- Completed infrastructure rehearsal: `2026-09-01`
- Rehearsal EC2 instance: stopped, not terminated
- Durable result: stored in S3 and independently SHA-256 verified after the
  instance stopped
- Scientific configuration: not run
- Scientific execution: not authorized
- AWS Stage F execution binding: not defined or accepted

The accepted Stage E integration remains commit
`c43ead831c3e4021405985134ed564b761bb1aed`. Its GitHub Actions run
`33231168021` completed successfully. The newest integrated framework line has
a later Stage E path-closure refusal caused by prospective Stage F authority
files. The existing Stage F local binding is Windows/NTFS/Docker Desktop
specific and cannot certify Ubuntu EC2 or AWS Batch. See
`AWS_STAGE_E_TO_STAGE_F_READINESS.md`.

## Contents

- `AWS_UNATTENDED_CAMPAIGN_PLAN.md` — proposed four-day, Mac-independent AWS
  lifecycle and required gates.
- `AWS_STAGE_E_TO_STAGE_F_READINESS.md` — exact repository status and blockers.
- `OPERATOR_RUNBOOK.md` — copyable stop, verify, download, and future-launch
  sequence.
- `campaigns/` — machine-readable infrastructure record and a deliberately
  non-executable future campaign template.
- `iam/` — the narrow policy used by the completed rehearsal.
- `rehearsals/2026-09-01/` — exact rehearsal scripts and retained evidence.
- `scripts/download-results.sh` — read-only S3 result retrieval and checksum
  verification.

## Download the completed result now

From the repository root on the Mac:

```bash
./aws/scripts/download-results.sh \
  's3://ebu-stage-f-results-k7m4p2/rehearsal/i-048bac00bdb540a4e/20260901T110354Z/' \
  "$HOME/Downloads/ebu-rehearsal-20260901"
```

The destination must not already contain files. The script verifies the active
AWS account, downloads both objects, checks the `.sha256` manifest, and prints
the local location. It never starts an instance and never executes EBU code.

If the AWS login has expired, run `aws login` first and repeat the download.
Do not create root access keys.

For byte-exact retrieval of the retained result version instead of the newest
key version, use the `s3api get-object` command in `OPERATOR_RUNBOOK.md`.

## What happens when a real campaign is eventually authorized

The intended operational backend is an AWS Step Functions Standard workflow
coordinating AWS Batch on managed On-Demand EC2, not a four-day interactive
SSM command. SSM `AWS-RunShellScript` has a 48-hour maximum execution timeout;
a Standard workflow can run for up to one year and AWS Batch supports job
timeouts without a maximum. After AWS accepts the workflow and its Batch job,
they run independently of this Mac and Codex. The Mac may be shut down.
Checkpoints, heartbeats, logs, receipts, and final results must be written to
AWS services, not kept only on the computer that submitted the job.

For a real campaign, the user can return to Codex and ask the coordinator to
prepare the exact launch packet. Preparation and validation do not authorize
science. After the packet passes and the user explicitly authorizes that exact
packet, the coordinator starts the AWS workflow and returns durable AWS IDs.
Only after the start receipt and first heartbeat are visible in AWS should the
Mac be closed. Four days later, this task or a new task can inspect status and
download the immutable result prefix; the result does not depend on the
original Codex task remaining open.

That future workflow remains blocked until all gates in
`AWS_STAGE_E_TO_STAGE_F_READINESS.md` are satisfied and the user gives a new,
explicit post-packet scientific execution authorization.

## Branch and merge boundary

This is an isolated operations/proposal branch. The repository's current
reachability validator uses an exact changed-path closure; adding AWS paths is
not accepted by the existing closure. Do not merge this branch or weaken that
validator merely to make these files pass. A separate AWS operational
authority/reachability stage must prospectively accept the exact AWS path set.
