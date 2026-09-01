# Prospective unattended AWS campaign plan

Status: **infrastructure and operations proposal only**

This plan explains how a future four-day EBU run can continue after the user
closes the Mac. It does not select scientific parameters, seal an execution
binding, submit a scientific job, authorize a retry, inspect an outcome, or
change any accepted Stage D/E/F scientific record.

## 1. Why the Mac is not the runtime

The Mac is only a submission and retrieval client. Once AWS accepts a job, the
AWS control plane and compute environment own its lifecycle. Closing Terminal,
Codex, or the Mac must not affect the job.

An interactive SSM session is suitable for setup and short rehearsals, but not
for a four-day controller command: the `AWS-RunShellScript` document's maximum
execution timeout is 172,800 seconds (48 hours). The proposed long-run backend
is an AWS Step Functions Standard workflow coordinating AWS Batch on managed
On-Demand EC2. A Standard workflow can remain active for up to one year and
uses exactly-once workflow execution semantics; AWS Batch supports explicit
job timeouts without a maximum. Both retain state independently of the Mac.

Official references:

- [SSM document timeout schema](https://docs.aws.amazon.com/systems-manager/latest/userguide/documents-schemas-features.html)
- [AWS Batch job timeouts](https://docs.aws.amazon.com/batch/latest/userguide/job_timeouts.html)
- [AWS Batch automated retries](https://docs.aws.amazon.com/batch/latest/userguide/job_retries.html)
- [AWS Batch job definitions](https://docs.aws.amazon.com/batch/latest/userguide/job_definitions.html)
- [AWS Batch CloudWatch logging](https://docs.aws.amazon.com/batch/latest/userguide/using_awslogs.html)
- [Step Functions integration with AWS Batch](https://docs.aws.amazon.com/step-functions/latest/dg/connect-batch.html)
- [Standard and Express workflow types](https://docs.aws.amazon.com/step-functions/latest/dg/choosing-workflow-type.html)

## 2. Proposed AWS components

| Component | Purpose | Required control |
| --- | --- | --- |
| ECR `ebu/ebu-stage-f` | Immutable OCI image | Execute by digest, never by mutable tag |
| Step Functions Standard | Durable campaign coordinator | Versioned definition; one execution per sealed campaign; Batch `.sync` integration |
| AWS Batch managed EC2 environment | Mac-independent scheduling and compute | On-Demand first; fixed architecture and bounded maximum vCPUs |
| AWS Batch job queue | Ordered campaign submission | One accepted queue identity in the binding |
| AWS Batch job definition | Image, command, resources, roles, logs | Immutable recorded revision plus canonical JSON hash |
| Job IAM role | Container access to its S3 attempt prefix | No IAM, EC2, ECR push, or cross-campaign write permission |
| Execution role | Pull ECR image and write CloudWatch logs | Standard narrow ECR/log permissions |
| S3 | Binding, checkpoints, receipts, results and manifests | Unique keys, versioning, encryption and checksum manifests |
| CloudWatch Logs | Standard output/error independent of local disk | Fixed log group and retention policy |
| EventBridge Scheduler | Independent maximum-runtime backstop | One-time deadline frozen in the packet; cancellation recorded |
| SNS (optional) | Completion/failure notification | User-approved subscription; no scientific interpretation |

Step Functions is the coordinator and AWS Batch is the compute backend. Neither
is provisioned by this branch.

## 3. Durable S3 layout

Every future campaign gets a unique, immutable prefix:

```text
s3://ebu-stage-f-results-k7m4p2/campaigns/<campaign-id>/
├── binding/
│   ├── campaign-request.json
│   ├── campaign-request.sha256
│   ├── execution-binding.json
│   └── execution-binding.sha256
├── attempts/<attempt-id>/
│   ├── START-RECEIPT.json
│   ├── heartbeats/<sequence>.json
│   ├── checkpoints/<sequence>/...
│   ├── logs/...
│   ├── outputs/...
│   ├── SHA256SUMS
│   └── COMPLETE.json or FAILED.json
└── campaign-manifest.json
```

No object is silently overwritten. A retry, if scientifically authorized,
uses a new attempt ID and retains all prior evidence. S3 is the durable source;
CloudWatch is operational visibility, not the sole scientific record.

## 4. Fail-closed launch packet

Before submission, the coordinator must present one human-readable packet and
one canonical machine record containing at least:

1. exact source commit and tree;
2. accepted Stage E integration and evidence identities;
3. accepted AWS execution-binding authority and validation evidence;
4. scientific OCI image repository and exact digest;
5. campaign-request raw and canonical SHA-256;
6. AWS account, Region, Standard state-machine ARN and definition hash, Batch
   queue and job-definition revision;
7. vCPU, memory, architecture, storage, expected duration and maximum timeout;
8. complete S3 prefix and IAM role identities;
9. retry policy, checkpoint policy and interruption semantics;
10. controls, falsifiers, terminal dispositions and cost envelope;
11. proof that every pre-execution validation lane passed; and
12. a field that remains `scientific_execution_authorized=false` until the
    user gives a new explicit authorization for that exact packet.

A tag such as `latest`, placeholder, unsealed field, wrong account, failed CI,
missing digest, mutable configuration, broadened IAM policy, or changed
scientific source refuses submission.

## 5. Proposed lifecycle

### Phase A — infrastructure only

1. Keep the completed S3/ECR/SSM rehearsal as historical evidence.
2. Replace routine root login with a named human administrative identity and
   MFA; never create root access keys.
3. Provision a minimal Standard workflow and AWS Batch test environment using
   Infrastructure as Code.
4. Submit only a synthetic container that emits heartbeats, checkpoints and a
   final checksum manifest.
5. Turn the Mac off during that rehearsal and verify the job completes.
6. Reboot or replace a test worker and prove synthetic checkpoint recovery.
7. Verify workflow history, CloudWatch logs and optional completion/failure
   notification.
8. Verify the independent deadline backstop and that the compute environment
   scales to zero after completion.

These operations produce no scientific result.

### Phase B — AWS binding authority

1. Draft a separate AWS/Linux/Step Functions/AWS Batch execution-binding
   authority. Do not claim the existing Windows/NTFS/Docker Desktop binding
   applies.
2. Freeze the exact AWS path set and reachability changes prospectively.
3. Implement the AWS binding and validator on a separate branch.
4. Run only permitted outcome-blind validation and infrastructure rehearsals.
5. Obtain independent audit and integrate only after PASS.

### Phase C — image and campaign preparation

1. Build the scientific image from the accepted source coordinate.
2. Run all accepted build and validation lanes before any scientific launch.
3. Push once to immutable ECR and record its digest.
4. Register the exact Batch job-definition revision using that digest.
5. Version the Standard state machine and record its ARN and canonical
   definition hash.
6. Create and hash the complete campaign request and execution binding.
7. Calculate the cost envelope and confirm service quotas/capacity.
8. Present the sealed campaign packet to the user.

### Phase D — separately authorized scientific submission

1. The user explicitly authorizes the exact sealed packet.
2. The launch client rechecks account, commit, tree, CI, image digest, binding,
   state-machine version, queue, job definition, roles, S3 prefix and absence
   of prior consumption.
3. Start exactly one Standard workflow execution for the authorized packet.
4. The workflow writes a start receipt, submits exactly one Batch attempt with
   the run-a-job (`.sync`) integration, and records both IDs durably in S3.
5. Return the workflow execution ARN, Batch job ID, S3 prefix, timeout and
   monitoring commands to the user.
6. The user may close the Mac. AWS continues independently.

### Phase E — unattended operation

1. The Standard workflow remains the durable coordinator; the Batch container
   uploads periodic heartbeats and atomic checkpoints.
2. CloudWatch retains standard output/error.
3. Failure handling follows the accepted binding. AWS Batch automatic retries
   remain set to one attempt unless the scientific protocol explicitly permits
   more; infrastructure failure is not permission to repeat a consumed
   scientific attempt.
4. The terminal record is uploaded before the job exits.

### Phase F — retrieval and finalization

1. Query the Standard workflow and Batch for `SUCCEEDED` or `FAILED` without
   interpreting science.
2. Download the complete S3 attempt prefix.
3. Verify every checksum and exact object/version identity.
4. Preserve the raw artifacts before interpretation.
5. Perform a separately authorized audit/interpretation stage.
6. Scale the Batch environment to zero and retain only explicitly required
   storage/logs.

## 6. Four-day defaults to be decided prospectively

The following are operational candidates, not accepted values:

- Batch timeout candidate: 432,000 seconds (five days for a four-day expected
  run, leaving a bounded completion margin);
- Step Functions workflow timeout candidate: greater than the Batch timeout
  plus bounded finalization time, and less than the one-year service maximum;
- retry attempts: one unless separately authorized;
- compute: On-Demand for first scientific campaigns, not Spot;
- heartbeats: fixed interval with monotonically increasing sequence;
- checkpoints: immutable sequence directories and one manifest per checkpoint;
- log retention: explicit finite period;
- Batch maximum vCPUs: bounded by the accepted campaign and account quota;
- automatic scale-down: zero desired vCPUs after no queued/running work.
- independent one-time deadline: fail closed after the frozen campaign limit,
  even if the normal workflow finalizer is unavailable.

These values must be frozen in the future AWS binding/campaign packet, not
silently inherited from this proposal.

## 7. Pre-Stage-F AWS rehearsals

Recommended order, each explicitly labelled non-scientific:

1. completed EC2/SSM/Docker/S3/ECR synthetic-result rehearsal;
2. Standard workflow plus Batch `hello-world`, CloudWatch and S3 receipt
   rehearsal;
3. four-hour synthetic workflow/heartbeat/checkpoint run with the Mac shut
   down;
4. synthetic interruption and checkpoint-resume rehearsal;
5. immutable ECR digest and wrong-digest refusal rehearsal;
6. IAM negative tests proving cross-prefix write and ECR push are denied;
7. quota/capacity/cost rehearsal at each intended instance size using an
   outcome-blind synthetic CPU/memory kernel;
8. full-duration synthetic soak only if shorter rehearsals cannot establish
   the operational property.

None may call the EBU scientific runner, advance model state, use a registered
campaign configuration, or inspect a candidate scientific outcome.
