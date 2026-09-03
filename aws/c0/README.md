# AWS-C0 closure-closed unattended synthetic rehearsal

This directory is a static implementation candidate. It grants no permission
to create, change, deploy, start, stop, or run anything in AWS. In particular,
it does not authorize a real EBU experiment, Stage F, credentials, or science.
Every live action remains behind the accepted packets and explicit approvals.

The accepted base is the carrier-reachability integration commit
`75985d21e1bbf7fb96c6942996e921615e217f6c`, tree
`3f2d926859feef77a10cbe0d705b38e52b56f7f5`. The rejected diagnostic commit
`e18c881` is design evidence only and must never be a base, parent, merge,
cherry-pick, or accepted implementation source.

## What AWS-C0 proves

AWS-C0 is an inert durability and operability rehearsal. It proves that a
stopped retained EC2 host can be verified, started once, handed one of three
synthetic modes, left unattended, stopped once by the Standard workflow, and
closed with exact-version evidence and an integer list-price upper bound. It
does not import the project runner, register a configuration, advance model
state, inspect an outcome, or produce a scientific output. All ten
zero-science counters remain zero.

The only attempt suffixes and derived modes are:

| Attempt suffix | Worker mode |
|---|---|
| `-SUCCESS` | `SUCCESS` |
| `-FAIL-AFTER-CHECKPOINT` | `FAIL_AFTER_CHECKPOINT` |
| `-TIMEOUT` | `TIMEOUT` |

No ambient mode override exists. There is no automatic Retry or attempt replay.

Stage E remains `ACCEPTED_FINISHED_UNCHANGED`. Stage F remains frozen and needs
a separate AWS/Linux scientific binding packet and a separate authorization.

## Phased AWS/Stage F execution plan

AWS-C0 is the reusable platform foundation, not a monolithic first scientific
run. Its foundation boundary is limited to journal lifecycle, deterministic
restart/reproducibility coordinates, exact-version storage, cost and security
controls, and a minimal common receipt envelope. The planned common envelope
contains only `schema`, `capsule_id`, `attempt_identity`, `sequence`,
`event_type`, `payload_identity`, `previous_receipt_sha256`, and
`receipt_sha256`; a capsule owns its separate typed payload.

Every later study is an independently registered capsule. Its registration
must seal its own inputs, outputs, controls, evidence payloads, budget, and
independent review before separate execution authorization. Adding a capsule
must not change the foundation envelope or make another capsule's evidence a
prerequisite.

The first executable capsule is `platform-smoke-known-case-v1`. It is bounded
to the existing inert success/failure/timeout known cases, zero scientific
imports and counters, a sealed duration/request/storage/currency ceiling, and
foundation lifecycle and exact-version receipt evidence. Its only conclusion
is platform operability for that sealed case. It must not claim a scientific
result and must not emit every future study's nested evidence payload.

The reusable local work is exact: `75985d2` supplies carrier reachability,
`6f79b58` binds the controller journal carrier, `d1d36fb` supplies the two
independently accepted lifecycle-ordering fixes, and `8e83a73` carries the
journal VersionId plus typed publication/readback receipt references. The
fixed 22-row handoff-table enforcement rejected in review remains a required
local foundation correction before any live authorization; none of these
checkpoints authorizes AWS use.

The complete 100-field requirement at
`aws_c0_audit_static_real_execution_registry_correction_evidence_schema.json#/$defs/final_s3_capture_aggregate/required`,
including every referenced nested authenticated-operation capture, carrier
external proof, fixed-size binding, terminal binding, arithmetic/time/hash,
journal-equality, and final-manifest-observation payload, is deferred in full.
Under a future separately accepted capsule authority, no part of that aggregate
is a launch gate or conformance claim for the first smoke capsule. Later study
capsules may adopt only their separately reviewed study-specific evidence
contract; the accepted 100-field authority is neither edited nor weakened by
this planning boundary. This deferral is non-operative unless and until that
separate authority explicitly partitions or supersedes the current aggregate
requirement; until then the complete existing 100-field requirement remains
mandatory and no AWS launch is authorized.

## Frozen arithmetic

The implementation adds exactly the 14 files in the accepted implementation
manifest. Static validation keeps the original 66 cases, preparation 84 cases,
and closure 108 cases separate: 258 coordinates total.

The third authority adds 18 closed record schemas. The pre-live packet contains
exactly 21 immutable objects:

| Class | Count |
|---|---:|
| implementation artifacts | 8 |
| operator bootstrap packet, authorization, closure; preparation packet-v2 and authorization-v2 | 5 |
| private infrastructure snapshot root | 1 |
| closure authority audit root | 1 |
| closure static-validation root | 1 |
| cost-model-v2 | 1 |
| closure-seed-v1 | 1 |
| launch-request-v3 root | 1 |
| preparation-closure-v2 | 1 |
| live-packet-v2 | 1 |
| **total** | **21** |

The live authorization is later and is not object 22 of preparation. A hidden
runtime-control bundle is forbidden: the six initial controls are canonical
preimages inside preparation-packet-v2, and the eleven fresh final controls are
canonical preimages inside preparation-closure-v2 and live-packet-v2.

The final semantic root order is exactly:

1. closure authority audit v1;
2. closure static validation v1;
3. private infrastructure snapshot v1;
4. launch request v3;
5. start receipt v3;
6. heartbeat roots;
7. checkpoint roots;
8. terminal root;
9. finalizer receipt v2;
10. retrieval verification v2;
11. cost closure v2; and
12. final manifest v2.

Publication after terminal is intentionally different: stopped observation,
resource-use closure, finalizer, cost, retrieval, final manifest, then the
non-root final-manifest-publication observation. Retrieval verifies the already
published cost root but the final manifest restores semantic retrieval-before-
cost order. The final manifest never self-attests its future S3 receipt.

## Evidence identity and storage rules

Canonical JSON is duplicate-free UTF-8 NFC, sorted and compact, integer-only,
with no final line feed. For an authorized root, `record_sha256` is SHA-256 of
the canonical record with only `record_sha256` omitted. Its S3 receipt hashes
all stored bytes. A non-root control or payload has no embedded self-digest;
its identity, content-addressed key, and receipt all hash the complete stored
bytes.

Every object receipt binds the authenticated bucket identity, exact key,
VersionId, byte count, full-byte SHA-256, and S3 checksum. Retrieval uses only
`ListObjectVersions` and exact `GetObject` VersionIds. It consumes all pages,
records token chains and terminal markers, enforces sealed page/item bounds,
and refuses delete markers, duplicate coordinates, repeated tokens, latest or
unversioned reads.

The controller seals and conditionally publishes its bounded capture journal,
reads back the exact returned VersionId, and then conditionally publishes one
acyclic fixed-key carrier at
`evidence/controller-capture-journal-handoff.json`. The carrier contains the
observed controller journal VersionId and the typed publication-receipt
identity; it contains no coordinate for its own future Put. During closure the
finalizer derives that key only from the sealed attempt prefix, performs one
bounded exact-key `ListObjectVersions`, gets the carrier by the discovered
VersionId, validates the carrier and its embedded receipt references, and gets
the controller journal by the carried exact VersionId. These three operations
are captured before final-manifest construction. The fixed-size response then
binds the controller journal, the sole carrier, and the finalizer journal while
retaining full history only in the two immutable journal objects.

The only recursive capture exclusions, in causal order, are controller-journal
Put, its exact-version Get, carrier Put, finalizer-journal Put, and its
exact-version Get. A sixth exclusion, a second carrier, a latest read, or a
direct state-machine substitute for the carrier refuses.

## Three approvals and the acyclic chronology

### Gate 0 — constrained operator bootstrap

If read-only inventory observes only temporary root, stop. Root may perform
only the separately approved, narrowly bounded operator-role bootstrap. Its
packet, approval, and closure are private local control evidence at first;
their S3 receipts are not presupposed. After bootstrap, root is barred from all
preparation and live actions. A constrained assumed-role session is mandatory.

### Gate 1 — preparation approval

Before this approval, local deterministic builds, hashing, canonical record
construction, Git inspection, and AWS read-only inventory are permitted. The
preparation packet must bind the exact existing versioned bucket and a fresh
preparation prefix, the initial six read-only control preimages, exact IAM
before/remediation/rollback plans, eight artifact candidates, cost-model and
closure-seed candidates, and exact change-set construction plans. It must not
predict future VersionIds, post-mutation identities, the launch identity, an
execution, start, heartbeat, or terminal.

One explicit preparation approval may authorize only:

- exact IAM remediation and exact after-state readback;
- staging the predetermined immutable artifacts and control records once;
- a bounded stopped-host start/SSM verification/stop bootstrap (no package
  installation; Docker 29.7.2 and AWS CLI 2.36.36 are historical expectations
  only and must be freshly verified);
- creation, but not execution, of one exact CloudFormation change set; and
- staging snapshot, audit, static-validation, cost model, seed, launch-v3,
  preparation-closure-v2, and live-packet-v2.

The preparation session may not execute the change set, start the workflow,
start the rehearsal attempt, publish live authorization, replay, or run science.
It ends with the instance stopped and the change set unexecuted.

### Gate 2 — live approval

The returned VersionIds, checksums, byte counts, bootstrap evidence, current
control preimages, exact change-set diff, and 21-object receipt set feed a final
live-packet-v2. Only after reviewing that complete packet may the user sign the
exact live-authorization-v2 statement. The constrained live session may publish
that one authorization, execute that one change set, wait for completion,
retrieve its outputs, and start one exact Standard execution. It denies replay,
other change sets, other attempts, and science.

The Standard execution input is closed and contains only the exact
live-authorization-v2 object receipt:

```json
{"live_authorization":{"bucket_identity":{"kind":"aws_s3_bucket/v1","sha256":"<sealed-bucket-identity>","value":"<same>"},"bytes":1234,"checksum_sha256_base64":"<checksum>","key":"<exact-attempt-prefix>/live-authorization.json","sha256":"<full-byte-sha256>","version_id":"<exact-version-id>"}}
```

Angle-bracket values above are operator-supplied sealed values, not defaults.
Do not put the launch, credentials, mode, arbitrary arguments, or a second
object into workflow input.

## Build and host preparation (only after Gate 1)

Builds happen locally and deterministically. Record the exact base image digest,
source bytes, build arguments, resulting OCI digest, controller bytes, service
unit bytes, SSM document bytes, ASL bytes, template bytes, and finalizer zip
bytes. Stage each artifact to its predetermined content-addressed key with a
conditional create, capture the fresh VersionId/byte/hash/checksum receipt, and
read that exact version back. A collision, existing key, missing checksum,
second version, or byte mismatch stops preparation.

The stopped host bootstrap is a verification, not an installer. After the
bounded start, wait for SSM Online, then verify exact Docker/AWS CLI versions,
the preloaded immutable image digest, controller digest, service-unit digest,
root ownership, `0600` request directory policy, and the Docker daemon. Any
mismatch stops and rolls the host back to `stopped`; do not download a package,
pull an image, or repair in place without new authority.

## Deployment and launch (only after Gate 2)

1. Execute the reviewed CloudFormation change set once.
2. Wait for a terminal stack status; a pending or failed stack is not launchable.
3. Read exact stack outputs and re-check the state-machine definition, role,
   logging, Lambda configuration, SSM document content/version/permissions,
   IAM pagination, bucket/KMS controls, network path, quota, artifacts, seed,
   model, and stopped instance against live-packet-v2.
4. Publish live-authorization-v2 once with a fresh conditional key and verify
   its exact version.
5. Start one execution whose name equals the attempt ID and whose input is the
   one receipt shown above.

The workflow performs one `StartInstances`, a bounded SSM no-block handoff,
bounded first-heartbeat polling (15-second chunks plus an exact final
remainder), safe-close after accepted start-v3 and heartbeat sequence zero,
bounded heartbeat/attempt polling, one non-reentrant `StopInstances`, stopped
readback, and closure. Every started path converges on stop and closure. There
is no `Retry` field.

The SSM document runs exactly two commands: controller `prepare-request-v3`
with exact key/VersionId/SHA/bytes for launch-v3, live-packet-v2, and live-
authorization-v2 plus the workflow ARN; then `systemctl start --no-block` for
the exact attempt unit. The root-owned exclusive `0600` sidecar binds those
coordinates. The controller re-fetches all three exact versions, claims the
attempt with a deterministic non-root conditional S3 object, publishes
start-v3, and only then starts the networkless read-only container.

You may close the laptop after `StartExecution` returns and the safe-close
receipt exists. Step Functions, EC2, Lambda, SSM, S3, and systemd continue in
AWS; the Mac is not part of the execution. Closing the laptop before those two
facts is not an accepted unattended handoff.

## Cost closure

The cost model contains exactly 22 ordered dimensions and authenticated AWS
Pricing request/response receipts, offer/tier/conversion fields, rational upper
bound proofs, and validity covering the complete accounting window including
the retained-resource horizon. It contains no float, implicit free tier,
discount, credit, refund, tax, or exchange-rate assumption.

For every dimension the finalizer uses an exact authenticated usage observation
or the sealed launch maximum. Maximum substitution has no pretend observation
and charges exactly the limit. With arbitrary-precision integers and explicit
`2^53-1` input/product/total bounds, charge is:

```text
(charged_units * numerator_minor_units + denominator_units - 1) // denominator_units
```

The total is fixed minor units plus all 22 individually rounded charges. Cost
PASS requires exact model and use bytes/receipts, equal dimensions/order/units,
full-window validity, all limits respected, stopped instance, and recomputed
total at or below the sealed ceiling. It is a list-price upper bound for the
sealed window, never an invoice claim.

## Downloading and recovering results

For PASS, use `DescribeExecution.output`; it is the FULL closure response and
contains exact bucket identity and exact object receipts for final manifest,
retrieval verification, and final-manifest-publication observation. Download
each with its exact key and VersionId, then verify byte count, SHA-256 and S3
checksum before parsing canonical JSON. Follow the final manifest’s ordered
identities and the retrieval record’s verified object receipts to download the
synthetic manifest and every prior root. Never use `aws s3 cp` without a
VersionId and never select `latest`.

For FAIL or INCONCLUSIVE, fully paginate `GetExecutionHistory` with the closure
seed’s page/event bounds. Normalize the complete transcript, then locate exactly
one `TaskSucceeded` Lambda payload whose `action` is `closure`. Zero, multiple,
truncated, or malformed candidates refuse. A raw Lambda closure response sets
both history transcript fields to null because its own `TaskSucceeded` event is
still in the future. COMPLETE evidenced FAIL uses `FULL`, all final coordinates,
and zero missing categories. Incomplete evidence uses `HISTORY_FALLBACK`, typed
missing categories and failure coordinates.

A successful synthetic download includes the synthetic manifest plus its
hash/checksum evidence. The earlier two-file rehearsal result remains useful as
a transport smoke test, but it is not this closure chain.

## Instance cost and lunch / interruption guidance

The retained stopped EBS volume and any retained S3 versions, logs, ECR image,
snapshot, KMS key, NAT gateway, VPC endpoint, or public IPv4 allocation can
still incur charges. A stopped EC2 instance does not accrue instance-running
compute, but attached storage and other retained resources can. Outside an
explicitly approved preparation or attempt window, keep instance
`i-048bac00bdb540a4e` stopped and check the sealed retained-resource inventory.

It is safe to take a break while the instance is confirmed stopped. During a
proper unattended run, it is safe to leave only after the execution is RUNNING
and safe-close exists. If this repository task is interrupted locally, all work
is ordinary Git worktree state and can be resumed; interruption itself grants
no AWS action.

## More rehearsals and a real experiment

Each additional AWS-C0 attempt needs a new attempt ID with one supported suffix,
a fresh prefix, fresh exact objects, a new live packet, a new live approval, and
one execution. Evidence from one attempt is never replayed into another.

A real experiment is not “AWS-C0 with a different container command.” Before
Stage F, retain the accepted Stage E result, define a separate AWS/Linux
scientific binding, independently review configuration identity, model/code and
container provenance, RNG/checkpoint semantics, resource/cost envelope,
four-day timeout and recovery, result schema, validation gates, and publication
rules, then obtain the separate Stage F authorization. Nothing in these 14
files supplies or implies that authority.

## Offline verification

These commands are credential-free and must run with bytecode disabled:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/validate_aws_c0_static.py
PYTHONDONTWRITEBYTECODE=1 python3 -B tests/aws/test_aws_c0_unattended_synthetic.py
```

They use only the Python standard library and local Git/repository bytes. Do
not run Docker, AWS, systemd, a package installer, or any scientific runner as
part of static validation.
