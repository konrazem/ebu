# EBU AWS-C0 unattended synthetic rehearsal authority amendment

Status: **PROSPECTIVE ADDITIVE NON-SCIENTIFIC AUTHORITY CANDIDATE ONLY**

Authority ID:
`EBU-AWS-C0-UNATTENDED-SYNTHETIC-REHEARSAL-AUTHORITY-v1`

Accepted base: commit
`a4af44afd3c878311ee373bc19e3be14b2aacec5`, tree
`619b59875cfa4c6ad4a7da4f6a1aaaa465d3f23a`.

This authority candidate defines a future, bounded, unattended AWS
infrastructure rehearsal using only synthetic payloads. It authorizes no AWS
mutation, spending, deployment, IAM change, image build or push, state-machine
execution, SSM command, instance start, systemd action, container start, or
scientific behavior. It is not Stage F readiness and cannot close any Stage F
scientific, institutional, runner, binding, host, packet, or execution gate.

`AWS_C0_UNATTENDED_SYNTHETIC_REHEARSAL_AUTHORITY_CANDIDATE_COMPLETE`

## 1. Exact candidate scope

The candidate adds exactly six regular mode-`100644` files:

1. `AWS_C0_UNATTENDED_SYNTHETIC_REHEARSAL_AUTHORITY_AMENDMENT.md`;
2. `aws_c0_unattended_synthetic_rehearsal_contract.json`;
3. `aws_c0_unattended_synthetic_rehearsal_evidence_schema.json`;
4. `aws_c0_unattended_synthetic_rehearsal_implementation_path_manifest.json`;
5. `aws_c0_unattended_synthetic_rehearsal_predecessor_manifest.json`;
6. `aws_c0_unattended_synthetic_rehearsal_validation_contract.json`.

No accepted file may be modified. A seventh path, deletion, rename, mode
change, symlink, submodule, generated evidence file, ignored-state exclusion,
force-push, or history rewrite refuses the candidate.

Authority drafting and audit are static and read-only except for these six
candidate files. They may use Git-object inspection, strict JSON parsing,
canonical hashing, schema/meta-schema validation, exact path comparison,
integer arithmetic, AST inspection, and deterministic in-memory negative
controls. They may not contact AWS, Docker, a package registry, or a project
runner.

## 2. Predecessor and diagnostic source

The only accepted base is the exact commit and tree above. Its Stage D, Stage
E, and Stage F authority and reachability bytes remain immutable.

Published commit `df7e8447dbe98ae21b78d97a07093b2f3de5555d`, tree
`847afbed0e750528b25c72e4c0e1d2c5643696af`, is classified exactly as
`PUBLISHED_DIAGNOSTIC_SOURCE_NOT_ACCEPTED_BASE`. It is not an accepted
predecessor, authority integration, implementation, validation result, or
execution record. Its sixteen AWS paths may supply content only to a later
separately authorized task. This authority neither integrates those paths nor
retroactively authorizes the interactive rehearsal they describe.

The completed 2026-09-01 EC2/SSM/S3/ECR rehearsal is historical diagnostic
input. It did not establish unattended operation, Step Functions control,
systemd recovery, finalization, scale-to-zero, scientific readiness, or Stage
F host binding.

## 3. Frozen AWS-C0 question and nonclaims

The future AWS-C0 rehearsal asks only:

> Can one exact synthetic-only attempt, submitted through a versioned AWS Step
> Functions Standard workflow to the existing EC2 instance, continue without
> the operator's Mac, emit ordered durable receipts, heartbeats and
> checkpoints, recover only as prospectively declared, finalize to immutable
> S3 objects, and return the instance to the declared stopped state within a
> frozen time and cost envelope?

A positive answer is non-scientific infrastructure evidence for that exact
AWS account, Region, instance, workflow definition, SSM document, controller,
service unit, finalizer, image digest, IAM set, timeout, and attempt. It is not
evidence about EBU models, campaign feasibility, scientific correctness,
Stage F readiness, arbitrary AWS reliability, or guaranteed four-day
operation.

## 4. Exact future architecture

The future implementation is limited to:

1. an AWS Step Functions **Standard** workflow as the durable coordinator;
2. exact Region `us-east-1`;
3. exact existing EC2 instance `i-048bac00bdb540a4e`;
4. one fixed, versioned SSM Command document named `EBU-C0-Start-v1`, whose
   canonical document bytes and SHA-256 are frozen before any live rehearsal;
5. one root-owned, non-user-writable, bounded systemd template service
   `ebu-c0@.service` invoking the exact controller by absolute path;
6. one standard-library Python controller that validates an inert launch
   request, starts exactly one synthetic container by immutable digest, and
   emits only AWS-C0 records;
7. one separately hashed finalizer that verifies terminal evidence and
   requests the declared cleanup path even after controller failure;
8. one synthetic worker image containing no EBU source, package, harness,
   runner, configuration, model, scientific seed, or candidate output;
9. immutable S3 keys under a dedicated AWS-C0 rehearsal prefix, never a Stage
   F campaign prefix; and
10. an exact final state requiring the instance to be stopped or a retained
    typed failure proving why that postcondition was not achieved.

AWS Batch, ECS, Lambda scientific execution, Step Functions Express,
interactive SSM as the long-running controller, a Mac-resident supervisor,
Spot capacity, mutable image tags, and automatic attempt replay are outside
AWS-C0.

## 5. Identity, privacy, and durability

Every root record contains `record_sha256`. Its sole valid digest preimage is
the complete canonical root record with only `record_sha256` omitted. Canonical
JSON is UTF-8 NFC, recursively key-sorted, integer-only, compact,
duplicate-key-free, finite, and has no final line feed. For an identity that
references a root record, `identity.value`, `identity.sha256`, and that
record's `record_sha256` are byte-identical lowercase SHA-256 values; the
identity object is not part of the referenced record's preimage. No other
field omission, null substitution, presentation serialization, or future
object metadata is permitted.

Every non-root identity kind must have one closed preimage rule frozen in the
live packet, and `identity.value` and `identity.sha256` both equal the SHA-256
of that exact preimage. In particular, the finalizer-observation identity is
the SHA-256 of the complete embedded canonical `finalizer_observation` object
with no field omitted. An unknown identity kind or undeclared preimage refuses.

Private AWS account, role, ARN, absolute-path, host, command invocation, and
billing material is retained outside Git. Credentials, tokens, session
material, root keys, Docker credentials, private manifest bytes, and instance
metadata credentials must never enter a repository artifact or public record.

The launch request, start receipt, each heartbeat, each checkpoint, terminal
receipt, finalizer receipt, retrieval verification, cost closure, and final
manifest use fresh versioned keys. No record is overwritten. An attempt
identity is consumed at most once. A retry or continuation requires its own
exact later authority and new attempt identity; infrastructure failure is not
permission to repeat a consumed attempt.

S3 and workflow history are durable sources. Terminal success requires byte
counts, SHA-256 values, object version identities, monotonic record ordering,
the expected synthetic-only manifest, a post-controller finalizer receipt,
retrieval PASS, cost-closure PASS, and the exact stopped-instance
postcondition. CloudWatch output alone is never completion evidence.

Failure is first-class evidence. A pre-start refusal, controller failure,
timeout, missing heartbeat or checkpoint, hash mismatch, unavailable cost
observation, exceeded cost ceiling, finalizer failure, or failed stop may omit
success-only identities and must close as typed FAIL or INCONCLUSIVE evidence.
No such record may be relabelled PASS. The finalizer receipt records whether a
controller terminal receipt existed, the cleanup request and disposition, the
observed instance state, and any stop-failure code in a closed finalizer
observation preimage. The receipt then binds that preimage and identity to the
fresh S3 object version, byte count, and digest that retain the observation.
It never tries to include an object's own future version identity in that
object's hashed preimage.

Publication evidence is always later than the object it witnesses. Retrieval
verification carries ordered object receipts for prior launch, start,
heartbeat, checkpoint, terminal, finalizer, and cost records, including fresh
keys, AWS-assigned version IDs, byte counts, and hashes. The final manifest's
own PutObject response is retained as an out-of-band Step Functions and S3
publication observation and is verified by the later operator retrieval; the
final manifest never self-attests its future version ID or object hash.

The Step Functions Standard supervisor, not the fallible finalizer process,
emits the finalization-closure record on every path. That record distinguishes
finalizer not-started, completed, failed, and timed-out states; separately
records whether cleanup was requested and whether the instance stopped; and
can close truthfully even when no controller terminal receipt exists.

## 6. Zero-science boundary

Every AWS-C0 record must carry zero counters for:

- EBU/project-runner imports;
- framework or Stage E harness imports;
- registered scientific configuration construction;
- model-state advances;
- trajectories, simulations, transforms, and Gates;
- scientific RNG draws;
- candidate outcome inspection; and
- scientific result, figure, book, interpretation, release, or publication
  creation.

The schema is closed against scientific configuration, model, trajectory,
seed, outcome, result, claim, figure, interpretation, or publication fields.
The synthetic worker may exercise only inert CPU, memory, timer, checksum,
heartbeat, checkpoint, restart, S3, logging, and cleanup behavior declared in
the later frozen AWS-C0 packet.

No AWS-C0 PASS changes `stage_f_execution_authorized=false`, resolves a Stage
F route gap, seals a campaign binding, or permits a scientific image build.

## 7. Exact later repository scope

After independent authority PASS and normal integration, one separately
audited static reachability change may modify exactly
`tests/framework/test_validation_reachability.py`. It must preserve every
accepted Stage C/D/E/F phase and add only literal AWS-C0 authority-only and
completed-implementation phases. Prefix, glob, ignore, dynamic, or
unknown-path allowances are forbidden.

Only after reachability integration and an exact-coordinate independent PASS
may a later implementation add the fourteen paths in
`aws_c0_unattended_synthetic_rehearsal_implementation_path_manifest.json`.
It may add no fifteenth path and may modify no accepted path. The dedicated CI
workflow performs static validation only and receives no AWS credential,
secret, OIDC token, deployment permission, or live-network rehearsal step.

The accepted Stage E validator and evidence remain unchanged. The known
current-line Stage E descendant path-closure refusal is not relabelled PASS by
AWS-C0. Any later proposal to change `scripts/validate_stage_e_harness.py` is a
separate authority boundary.

## 8. Prospective live-rehearsal gate

Authority and implementation acceptance do not authorize a live rehearsal.
Before any AWS mutation, the controller must present a complete human-readable
AWS-C0 packet and canonical machine record containing the exact account and
Region identities, exact existing instance identity and required initial
`stopped` state, bound fresh private-infrastructure-snapshot identity,
workflow and SSM document identities, controller/service/finalizer/image
digests, container-runtime-policy identity, IAM-policy-set identity, S3 prefix,
static-validation and authenticated-quota-observation identities, attempt and
cleanup deadlines, phase timeouts, heartbeat and checkpoint intervals, the
one declared cleanup path, retry bound, currency, cost-model identity, cost
ceiling, exact maximum EC2 seconds, S3 storage and request counts, ECR bytes,
CloudWatch bytes, Step Functions transitions, Lambda invocations and duration,
KMS requests, data-transfer bytes, public-IPv4 seconds, NAT-gateway seconds,
VPC-endpoint seconds, and all zero-science counters.

The runtime validator must prove the deadline ordering, timeout relationships,
record ordering, count equalities, identity/digest equalities, finalizer
chronology, and reconciliation of the cost closure to that exact launch
envelope. It must also prove that the bound infrastructure snapshot is fresh,
authenticated, quota-verified, in the same account/Region/instance/workflow/
SSM/IAM set as the launch request, and records the exact initial state
`stopped`. JSON Schema shape validation alone is never sufficient for those
cross-record facts.

A new explicit user statement issued after that exact packet is required for
the live AWS-C0 rehearsal. It authorizes only the bounded synthetic attempt in
the packet. It does not authorize Stage F, scientific configuration, a
scientific image, or a scientific run.

## 9. Operator-supplied quota fact

The exact operator-supplied statement is retained as unverified input:

```text
Region us-east-1; quota name All Standard new limit; value 64; effective after 30 minutes.
```

Its evidence class is `OPERATOR_SUPPLIED_UNVERIFIED_QUOTA_FACT`. It is not
independently verified, is not a capacity guarantee, and is never execution
authority. A live packet must replace or accompany it with a contemporaneous
authenticated AWS quota observation and fail closed if the two disagree.

## 10. Required independent gates

The mandatory order is:

1. fixed-coordinate independent audit of these six authority files;
2. normal integration of the exact audited authority candidate;
3. exact one-path static reachability correction and independent audit;
4. exact fourteen-path implementation and static validation;
5. independent implementation and zero-science audit;
6. normal implementation integration and dedicated exact-target static CI;
7. outcome-blind private infrastructure and IAM review;
8. complete AWS-C0 packet; and
9. a new explicit post-packet authorization before any live AWS mutation.

Self-review is not independent. A failed, skipped, partial, filtered,
zero-check, unsealed, stale, or missing gate is not PASS.

## 11. Mandatory refusals

Refuse on a wrong base or tree; acceptance of the diagnostic commit; any path
outside the exact phase closure; any altered predecessor byte; a wildcard
allowlist; a changed Stage E or Stage F scientific rule; a non-Standard
workflow; another EC2 instance; a mutable SSM document, service, controller,
finalizer, or image; non-root service ownership; unbounded runtime, retry,
compute, storage, or cost; a credential in Git; an IAM privilege outside the
closed packet; reuse or overwrite; missing durable evidence; a Mac-dependent
controller; a scientific import, field, action, output, or claim; an
unverified quota statement promoted to authority; or live AWS activity before
the separate post-packet authorization.

Independent authority acceptance means only that this six-file prospective
package is ready for normal integration. It authorizes no implementation,
validation execution beyond the static audit, AWS mutation, spending,
deployment, synthetic rehearsal, scientific work, interpretation, release,
or publication.
