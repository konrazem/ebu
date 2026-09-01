# AWS-C0 cost, runtime-control, retrieval, and closure correction authority amendment

Status: **prospective authority only; no implementation, AWS, Docker, systemd,
container, scientific, deployment, or execution authority**

Authority ID:
`EBU-AWS-C0-COST-RUNTIME-RETRIEVAL-CLOSURE-CORRECTION-AUTHORITY-v1`

Accepted base commit:
`0bcc1729516f580c2fd30061ec2db15eb2364b2b`

Accepted base tree:
`7fc84a90875594c7bf666b4072b43b23ee5fbdd9`

## 1. Purpose and non-authority

This amendment closes only the evidence interfaces that presently make a
truthful AWS-C0 synthetic PASS unreachable. It does not approve the current
unaccepted implementation, make an AWS call, authorize spend, create or change
IAM, upload an object, deploy a stack, start an instance, send SSM, start a
service or container, run a rehearsal, repeat an attempt, or run science.

The accepted Stage E result remains finished and unchanged. The Stage F packet,
scientific configuration, scientific image, AWS/Linux binding, experiment,
interpretation, and publication remain separately frozen and separately
authorized. AWS-C0 and later C1 are infrastructure rehearsals only.

The original AWS-C0 authority and live-preparation correction remain in force
except for the exact versions, record fields, chronology, arithmetic, and
validation rules expressly replaced here. Any ambiguity resolves fail-closed.

Diagnostic commit `e18c881ba53bfe3cfb496533587f254a9a8f92a5`
(tree `0bb6844c54486962664a2d673b4a80b05caff5a7`, sole parent the
accepted base) is classified exactly
`NONACCEPTED_COST_RUNTIME_RETRIEVAL_CLOSURE_BLOCKED_DESIGN_SOURCE`. It is not a
predecessor, base, parent, or acceptable source for a corrected implementation.
Its explicit validator exit-2 blocker, unavailable runtime-control preimages,
unavailable cost-model/use inputs, incomplete root receipts, and independent
audit FAIL are retained only as diagnostic evidence. No bytes may be copied
from it merely because they existed there.

## 2. Defects this amendment closes

A conforming future implementation must not:

1. trust opaque IAM, bucket-control, network, quota, workflow, SSM, or
   change-set labels when their canonical preimages are unavailable at runtime;
2. treat a cost ceiling as observed cost or compute a cost from a digest without
   the exact cost-model bytes;
3. claim retrieval PASS without exact-version receipts for every mandatory
   predecessor root and material non-root object;
4. overload a pre-launch failure-closure seed with a post-start safe-close
   observation;
5. use an object's future VersionId or PutObject response in that object's own
   digest preimage;
6. confuse semantic evidence-root order with the publication chronology needed
   for retrieval to verify a cost record;
7. use an unpaginated or truncated S3 or Step Functions listing, or an
   unversioned "latest" object, as final proof;
8. report a finite attempt cost as an invoice or as a lifetime bound for
   retained storage and logs; or
9. accept a launch whose finalizer timeout exceeds the deployed Lambda timeout
   or whose resource envelope cannot contain all reachable work.

Until this amendment, its reachability correction, and a conforming future
implementation are separately accepted, the only truthful current disposition
is blocked/non-PASS-capable.

## 3. Canonical bytes and identities

All records are duplicate-key-free UTF-8 NFC JSON, recursively sorted by
Unicode code point, compact with comma/colon separators, integer-only and
finite, with no trailing data and no final line feed.

A root record contains `record_sha256`. Its digest preimage is the complete
canonical root with only `record_sha256` omitted. The root key binds that
preimage digest; the later object receipt binds the SHA-256 of the complete
stored bytes.

A non-root control record has no embedded self-digest. Its content-addressed
key and later object receipt bind the SHA-256 of its complete stored bytes.
Every identity has exactly `kind`, `sha256`, and `value`, with the last two
equal. Every S3 object receipt has exactly the bucket identity, key, opaque AWS
VersionId, byte count, complete-byte SHA-256, and AWS checksum value. Unknown
fields, identity kinds, record kinds, numeric representations, or digest rules
refuse.

An object's AWS VersionId and Put response are future observations. They are
bound only by a later record or returned out-of-band. No predicted VersionId,
self-receipt, or digest cycle is permitted.

Every identity context has a closed machine-readable kind table. Operator
authorization sources, API/control observation sources, usage source resources,
verified-object kinds, canonical-candidate field/array positions, and ordered
root positions have no prose fallback. Every policy ceiling, subset/PassRole
proof, remediation/rollback/change/effect plan, construction/derivation
contract, and rate-upper-bound proof carries its complete canonical preimage
bytes next to the identity or in the packet's closed bound-preimage bundle.
Unknown context, action, position, kind, or missing preimage refuses.

## 4. Corrected chronology and object arithmetic

The minimum fresh publication set through the complete pre-live packet is
exactly **21 objects**:

1. eight predetermined implementation artifacts;
2. five preapproval controls: operator-bootstrap packet-v1,
   operator-bootstrap authorization-v1, operator-bootstrap closure-v1,
   preparation-packet-v2, and preparation-authorization-v2;
3. one private-infrastructure-snapshot root;
4. one correction-authority-audit root;
5. one corrected-static-validation root;
6. one cost-model-v2 non-root object;
7. one pre-launch closure-seed non-root object;
8. one launch-request-v3 root;
9. one preparation-closure-v2 non-root object; and
10. one live-packet-v2 non-root object.

The arithmetic is `8 + 5 + 1 + 1 + 1 + 1 + 1 + 1 + 1 + 1 = 21`.
The preparation closure and live packet carry the first actual post-mutation
runtime-control preimages and bind the derived private snapshot; there is no
hidden twenty-second preparation bundle.

The accepted preparation-packet-v1 and preparation-authorization-v1 cannot
silently authorize these new objects or controls. This amendment replaces only
the first C0 preparation statement with the following exact v2 statement,
issued after the complete local canonical preparation-packet-v2 bytes have been
displayed and hashed, but before either preparation-v2 record is staged:

```text
AUTHORIZE_AWS_C0_PREPARATION_V2 preparation_packet_sha256={preparation_packet_sha256} implementation_commit={implementation_commit} implementation_tree={implementation_tree} account_identity_sha256={account_identity_sha256} region=us-east-1 instance_id=i-048bac00bdb540a4e preparation_session_assumer_identity_sha256={preparation_session_assumer_identity_sha256} operator_role_identity_sha256={operator_role_identity_sha256} preparation_session_policy_identity_sha256={preparation_session_policy_identity_sha256} preparation_policy_ceiling_identity_sha256={preparation_policy_ceiling_identity_sha256} preparation_policy_subset_proof_identity_sha256={preparation_policy_subset_proof_identity_sha256} preparation_pass_role_scope_proof_identity_sha256={preparation_pass_role_scope_proof_identity_sha256} preparation_session_max_duration_seconds={preparation_session_max_duration_seconds} preparation_session_expires_utc={preparation_session_expires_utc} artifact_bucket_identity_sha256={artifact_bucket_identity_sha256} pre_live_object_count=21 accounting_end_utc={accounting_end_utc} cost_ceiling_minor_units={cost_ceiling_minor_units} allow=RECHECK_READ_ONLY_PREFLIGHT,APPLY_EXACT_IAM_REMEDIATION,STAGE_EXACT_PRE_LIVE_OBJECTS,BOOTSTRAP_EXACT_STOPPED_INSTANCE,CREATE_ONE_UNEXECUTED_CHANGE_SET,FINALIZE_EXACT_LIVE_PACKET deny=LIVE_EXECUTION,REPLAY,DELETE,TERMINATE,SCIENTIFIC_EXECUTION
```

Preparation-packet-v2 binds only facts and bytes available before mutation: the
complete local canonical bytes and fresh publication targets of the three
bootstrap controls, eight already built artifacts, cost-model-v2, and
closure-seed; the exact initial pre-state for account/Region, stopped instance
and sole instance-profile role, IAM policy set, bucket/KMS controls, network
path, and quota; exact authority-audit, corrected-static-validation, snapshot,
artifact-publication, runtime-control, bootstrap, change-set/diff/effect,
launch, preparation-closure, and live-packet construction/derivation contracts;
and exact bucket/prefix/schema/key-derivation publication targets (not future
content-addressed keys), 21-kind/count plan, IAM
before/remediation/rollback plans, finite accounting window and retained
resource horizon, resource maxima, and cost ceiling. It does **not** predict a
post-mutation snapshot, AWS VersionId, change-set ARN/status/diff/output,
post-IAM policy set, post-bootstrap software state, final runtime-control
preimage, authority/reachability/implementation integration commit, or
PutObject receipt. Preparation-closure-v2 and live-packet-v2 first bind those
actual output-derived records and receipts after the authorized preparation
steps. The seed binds cost-model identity/key/full-byte digest, not its future
VersionId; launch-v3 later binds returned model and seed VersionIds.

The v2 statement and packet contain no preparation-packet or preparation-
authorization self-key, predicted VersionId, or object receipt. They bind
closed content-addressed-key derivation contracts; only after each complete
canonical byte string exists is its key derived from its full-byte SHA-256.
After approval, packet-v2 and authorization-v2 are staged once;
their AWS receipts are first bound by the later preparation closure and live
packet. Preparation-authorization-v2 binds the exact statement/source and
complete packet-byte identity; the packet-preapproved assumer and operator
role; exact session-policy canonical bytes and identity; policy ceiling and
subset proof; scoped PassRole proof; maximum duration and expiry; and the
subsequently observed session identity only when its canonical STS observation
proves exact derivation from those controls. It contains no packet object
receipt. None of the bootstrap candidates contains or predicts an S3 VersionId
or object receipt before approval. The three operator-bootstrap records remain
v1. Preparation v1 records do not satisfy this amendment.

The live packet is published before the second C0 approval. The later
live-authorization-v2 is a separate fresh non-root object and is not counted in
the 21 pre-live objects.

This amendment replaces only the second C0 statement with the following exact
v2 statement, issued after the complete live-packet-v2 publication observation:

```text
AUTHORIZE_AWS_C0_LIVE_V2 live_packet_sha256={live_packet_sha256} live_packet_key={live_packet_key} live_packet_version_id={live_packet_version_id} change_set_identity_sha256={change_set_identity_sha256} account_identity_sha256={account_identity_sha256} region=us-east-1 instance_id=i-048bac00bdb540a4e attempt_identity_sha256={attempt_identity_sha256} live_session_assumer_identity_sha256={live_session_assumer_identity_sha256} execution_operator_role_identity_sha256={execution_operator_role_identity_sha256} execution_session_policy_identity_sha256={execution_session_policy_identity_sha256} execution_session_policy_ceiling_identity_sha256={execution_session_policy_ceiling_identity_sha256} execution_session_policy_subset_proof_identity_sha256={execution_session_policy_subset_proof_identity_sha256} pass_role_scope_proof_identity_sha256={pass_role_scope_proof_identity_sha256} execution_session_max_duration_seconds={execution_session_max_duration_seconds} live_session_assumer_expires_utc={live_session_assumer_expires_utc} allow=ASSUME_EXACT_LIVE_SESSION,PUBLISH_EXACT_LIVE_AUTHORIZATION,EXECUTE_EXACT_CHANGE_SET,START_ONE_EXACT_EXECUTION deny=REPLAY,OTHER_CHANGE_SET,OTHER_ATTEMPT,SCIENTIFIC_EXECUTION
```

Live-packet-v2 preapproves the exact live assumer, execution role, complete
session-policy bytes and identity, ceiling/subset proof, resource-scoped
PassRole proof, maximum duration, and expiry. After the separately issued
statement, that exact constrained session may self-assume once,
live-authorization-v2 may bind the observed session only with a closed STS
derivation proof, and it may publish that one canonical record with
`If-None-Match:*` at the packet-declared key. No other S3 write is allowed by
this addition. Its returned receipt is retained before the exact change set and
execution start.

The pre-launch `aws_c0_closure_seed/v1` is staged before launch-v3. It supplies
only the exact bucket, prefix, attempt, finalizer, time/cost envelope, preknown
Standard state-machine ARN and identity, deterministic execution-name
derivation, sealed S3-version and execution-history pagination bounds, closure
state name, and failure-record coordinates needed to emit typed, immutable
closure evidence if the launch or live packet is malformed. Launch-v3 binds its
identity and exact object receipt. The seed cannot bind launch-v3, start-v3, a
heartbeat, an execution ARN, or a workflow observation that does not exist yet.

After start-v3 and heartbeat zero, a distinct
`aws_c0_safe_close_receipt/v1` is published. It binds one Standard execution
observed `RUNNING`, the exact accepted start-v3 root receipt, and the exact
heartbeat-zero root receipt. Its own PutObject receipt is returned out-of-band.
The two records are never overloaded or substituted for one another.

After worker termination the publication chronology is:

1. terminal root or typed missing-terminal observation;
2. stopped-instance observation;
3. non-root resource-use closure;
4. finalizer-receipt-v2 root;
5. cost-closure-v2 root;
6. exact-version retrieval-verification-v2 root;
7. final-manifest-v2 root; and
8. non-root final-manifest-publication observation.

The final publication observation binds the final-manifest PutObject receipt.
Its own PutObject receipt and the complete closure response remain out-of-band
in Standard workflow history. Neither retrieval nor the final manifest can
claim that future observation as a predecessor.

## 5. Runtime-control preimages and fresh preflight

The preparation packet carries only the exact initial six-control pre-state and
closed derivation contracts. The preparation closure and live-packet-v2 first
carry the output-derived private snapshot, artifact receipts, change-set
observations, and final eleven closed canonical runtime-control preimages with
authenticated observation receipts for:

- account and Region;
- exact instance, stopped state, instance-profile ARN, and sole role ARN;
- complete inline and attached IAM policy set, permissions boundary, trust
  policy, and relevant session-policy ceiling;
- bucket Region, versioning, default encryption, public-access block, applicable
  bucket/KMS policies, and exact artifact/evidence prefixes;
- VPC, subnet, interfaces, routes, public-address state, NAT gateways, and VPC
  endpoints;
- authenticated Standard-instance quota observation;
- Step Functions Standard definition, role, logging, and exact state-machine
  ARN;
- SSM document bytes/version/permissions;
- finalizer, controller, service, image, and container-runtime identities;
- exact CloudFormation change-set ARN, status, execution status, template,
  parameters, canonical diff, and effect API/resource sets; and
- every immutable artifact key, VersionId, byte count, complete-byte digest, and
  checksum.

Every claimed read is drawn from a machine-readable action/resource allowlist;
it includes `s3:GetBucketPolicy`, `kms:GetKeyPolicy`,
`ssm:DescribeDocumentPermission`, and `states:DescribeStateMachine`, together
with every other IAM, S3, KMS, EC2, Service Quotas, Step Functions, SSM,
CloudFormation, Lambda, and Logs read used by reconstruction. The allowlist
contains no mutating action.
Each allowlist row contains exactly one action and one resource selector.
`ec2:DescribeAddresses` is included. Actions without AWS resource-level
authorization, including applicable list/describe calls and
`ssm:DescribeInstanceInformation`, use `*`; resource-scoped reads use only the
sealed ARN or bucket/prefix selector.

Immediately before `StartInstances`, the finalizer exact-version-fetches every
bound object, recomputes every identity, queries the exact live resources, and
reconstructs those canonical preimages. Any missing preimage, pagination token,
truncation, extra or missing policy, changed state, stale observation,
unauthenticated quota, wrong workflow type, wrong role, unavailable control,
or identity mismatch emits typed refusal. Labels alone never pass.

The one executed change set must be the exact packet-bound change set and its
resulting stack outputs must exactly match the sealed state-machine ARN,
function identity, roles, SSM document, instance, Region, and artifact versions.
There is no CloudFormation service role and no arbitrary workflow input.

## 6. Version changes and acyclicity

The twelve evidence-root categories remain exactly twelve. This amendment
replaces versions only where required:

1. `aws_c0_cost_runtime_closure_authority_audit/v1`;
2. `aws_c0_cost_runtime_closure_static_validation/v1`;
3. `aws_c0_private_infrastructure_snapshot/v1`;
4. `aws_c0_launch_request/v3`;
5. `aws_c0_start_receipt/v3`;
6. `aws_c0_heartbeat/v1`;
7. `aws_c0_checkpoint/v1`;
8. `aws_c0_terminal_receipt/v1`;
9. `aws_c0_finalizer_receipt/v2`;
10. `aws_c0_retrieval_verification/v2`;
11. `aws_c0_cost_closure/v2`; and
12. `aws_c0_final_manifest/v2`.

Launch-v3 is staged after the audit/static/snapshot/cost-model/closure-seed and
artifact objects, so it binds their exact receipts together with the exact
preparation-packet-v2 and preparation-authorization-v2 identities and receipts.
It does not contain a
preparation-closure, live-packet, live-authorization, execution, start, or later
identity.

Preparation-closure-v2 binds launch-v3. Live-packet-v2 binds the PASS
preparation closure and launch-v3. Live-authorization-v2 binds the already
published live packet. Start-v3 binds launch-v3, live-packet-v2,
live-authorization-v2, closure seed, one consumed attempt, exact workflow
execution, exact SSM command, and accepted start disposition. These arrows are
acyclic and no future value is patched into an earlier object.

Finalizer preflight resolves the packet-declared live-authorization key through
fully paginated versions and requires exactly one version whose complete bytes
equal the exact workflow input. Its sealed preflight output passes the exact
launch, packet, and authorization receipts plus workflow ARN through the fixed
SSM document. The host controller writes one exclusive root-owned `0600`
source-sidecar containing those coordinates, refuses symlinks and ambient
substitution, exact-version-fetches all three records, and cross-binds them
before publishing start-v3. SSM's only later command remains the nonblocking
fixed systemd unit start.

## 7. Integer-rational cost model and resource use

`aws_c0_cost_model/v2` is a human-reviewable canonical non-root object retained
at an exact version. It contains one exact dimension for every costed resource,
with a closed unit, nonnegative integer numerator in USD minor units, strictly
positive integer denominator in resource units, and a closed embedded
`aws_c0_pricing_observation/v1` preimage. That observation binds exact Pricing
API/action/request/response bytes, offer/version/SKU/term/rate/tier/unit,
currency-conversion inputs, authenticated source receipt, observation and
validity times, and a machine-checkable proof that the selected rational is at
least every applicable tier/minimum across the sealed quantity/window, plus the
rule
`CEIL_EACH_DIMENSION_THEN_SUM_FIXED`.

The authenticated pricing-source canonical bytes are embedded in the cost
model and bound by its source identity; they do not create an uncounted
preparation object. The cost-model object receipt is the immutable publication
receipt for both the reviewed rational rates and that embedded source preimage.

No float, decimal string, binary approximation, implicit free tier, discount,
credit, tax, exchange rate, spot assumption, price tier, or unstated minimum is
permitted. A source with tiers or minimums must be converted before approval to
one conservative monotone rational upper-bound rate valid over the complete
sealed quantity and accounting window. Every integer is between zero and
`9007199254740991`, every multiplication is performed with arbitrary-precision
integers, and every operand and result is range-checked against the contract's
declared product and total maxima. Overflow, excess range, unknown unit, stale
validity, or missing dimension makes cost unavailable.

Launch-v3 seals the exact maximum vector and a finite accounting window. The
vector includes compute seconds, public-IPv4/NAT/endpoint seconds, API request
counts, Lambda duration, Step Functions transitions, transfer and ingestion
bytes, and retained-resource byte-seconds or GiB-seconds for EBS, S3 versions,
CloudWatch logs, ECR if nonzero, and snapshots if nonzero. A zero maximum is
allowed only when the packet proves the resource is absent and cannot be
created by the exact effect set.

`aws_c0_resource_use_closure/v1` supplies one row per exact dimension. Each
exact row binds a closed `aws_c0_usage_observation/v1` preimage and exact object
receipt: API/action/request/response, source resource and unit, observed value
and time, authentication disposition, and any fully consumed pagination
transcript. If exact usage is unavailable or lagging, the row uses
`SEALED_MAXIMUM_SUBSTITUTION` and charged units equal the sealed maximum. If
usage is exact, charged units are at least observed units and no greater than
the sealed maximum. Any observation above a maximum is a typed resource-limit
failure and cannot yield PASS.

For every dimension `i`, the cost closure recomputes:

```text
charge_i = (charged_units_i * numerator_i + denominator_i - 1) // denominator_i
upper_bound_minor_units = fixed_minor_units + sum(charge_i)
```

Every equality is checked from exact stored bytes. Cost PASS requires the model
validity to cover the entire accounting window, exact dimension equality among
model/launch/use closure, all limits respected, a stopped instance, and the
recomputed integer upper bound at or below the sealed ceiling.

The seed, both cost-envelope forms, launch, and live packet carry identical
positive integer page/item maxima for `iam:ListAttachedRolePolicies` and
`iam:ListRolePolicies`, plus aggregate IAM maxima. Every token and count is
consumed and cross-bound; missing/repeated tokens, per-loop excess, aggregate
overflow, or disagreement refuses.

The accounting window has exact inclusive start and exclusive end timestamps.
Its end must cover attempt/cleanup plus the packet's retained-resource horizon.
Storage quantities are charged as byte-seconds or GiB-seconds across that
horizon, not merely bytes at closure. The result is a conservative list-price
upper bound for the declared window, **not an AWS invoice, lifetime cost,
refund, credit, tax, or post-horizon claim**. Retained EBS, S3, CloudWatch, KMS,
snapshot, public-address, NAT, or endpoint resources may continue to cost money
after that horizon. Deletion is not authorized by this amendment.

## 8. Retrieval and semantic root order

Retrieval-v2 exact-version-fetches and verifies complete bytes, canonical
digests, root preimages, keys, VersionIds, byte counts, and checksums for:

- the authority audit, corrected static validation, snapshot, launch-v3,
  start-v3, every heartbeat, every checkpoint, terminal, finalizer-v2, and
  cost-v2 roots;
- all 21 pre-live objects and the later live-authorization-v2;
- safe-close receipt, resource-use closure, and expected synthetic manifest;
  and
- every other packet-declared material control object.

All S3 `ListObjectVersions` and Standard execution-history pages must be
captured in closed canonical pagination transcripts. Each transcript binds
ordered request/response hashes, page count, incoming/outgoing token chain,
terminal marker, version/delete-marker/duplicate or event counts, and the
sealed page/item/event maxima. All pages must be consumed to terminal
pagination state with repeated/missing token detection. A truncated response,
delete marker,
unexpected version, duplicate key/version, unversioned read, HEAD/latest
substitution, checksum absence, or extra material object refuses.

Cost-v2 must be published before retrieval-v2 so retrieval can verify its exact
receipt. The accepted **semantic** final-manifest order nevertheless remains:
authority audit, static validation, snapshot, launch, start, all heartbeats in
sequence, all checkpoints in sequence, terminal, finalizer, retrieval, cost,
final manifest. Publication chronology and semantic order are separate closed
fields; swapping either, or pretending retrieval existed before the cost bytes
it verifies, refuses.

With one heartbeat and one checkpoint, retrieval contains exactly the ten
available predecessor root identities: authority audit, static validation,
snapshot, launch, start, heartbeat zero, checkpoint zero, terminal, finalizer,
and already-published cost. Retrieval never includes its own identity. Its
separate semantic-category field states the eleven predecessor categories in
final-manifest order (retrieval before cost), while its publication-order field
states that cost was published before retrieval. The final manifest alone can
bind retrieval as the eleventh prior-root identity.

PASS requires at least heartbeat zero and checkpoint zero. All sequences begin
at zero, are contiguous, and have exact predecessor identities. The final
manifest contains every prior root identity in semantic order, plus exact
category offsets/counts; `record_count` equals the identity list length. It does
not include itself in that list and does not self-attest its Put receipt.

## 9. Safe-close and closure-history gates

The Mac may close only after the operator independently proves:

1. the retained exact Standard execution ARN currently reports `RUNNING`;
2. exactly one `aws_c0_safe_close_receipt/v1` exists at the attempt's sealed key
   and exact VersionId;
3. its complete bytes, checksum, identity, and out-of-band Put receipt verify;
4. its start-v3 receipt exact-version-fetches to
   `AWS_C0_START_ACCEPTED` with null failure fields; and
5. its heartbeat receipt exact-version-fetches to sequence zero, null previous
   heartbeat identity, the same attempt identity, and a fresh timestamp.

Seeing a key, trusting latest, observing only `RUNNING`, or seeing only a start
receipt is insufficient.

The closure Lambda response is a closed tagged union. `FULL` carries
`action="closure"`, final status, bucket and workflow identities, final-manifest
and retrieval identities/receipts, and final-manifest-publication-observation
identity/receipt. `HISTORY_FALLBACK` is always constructible from the closure
seed when launch, cost, retrieval, final-manifest, or publication fails; every
unavailable coordinate is null, each missing semantic category is enumerated,
and typed failure phase/code plus closure-seed identity/receipt and the exact
history-retrieval contract/bounds remain in the response. The raw response does
not claim a transcript of its own future `TaskSucceeded` event. After
termination the operator consumes history, persists the closed transcript, and
then extracts the unique closure payload. PASS permits only `FULL` and no
failed semantic coordinate field. A successful Standard execution normalizes this
from `DescribeExecution.output`. FAIL or INCONCLUSIVE has no execution output;
the operator consumes every page of `GetExecutionHistory` with execution data,
decodes Lambda integration output, and requires exactly one `TaskSucceeded`
payload with `action="closure"`. Zero, multiple, truncated, malformed, or
wrong-execution candidates refuse. Every final-manifest/publication task has a
Catch to the fallback closure state, so workflow history remains a total
recovery source even when PutObject fails.

Outcome and evidence availability are independent. A deterministic
FAIL-AFTER-CHECKPOINT or TIMEOUT may be fully evidenced, stopped, retrieved,
costed, and manifested with all twelve root categories, zero missing
categories, `AWS_C0_FINAL_FAIL`, and a `FULL` closure response. An observed
hash mismatch is retrieval FAIL with complete evidence, not UNAVAILABLE. A
stale or invalid cost input may make cost unavailable while its root evidence
is still present. Missing categories are listed if and only if required
coordinates are absent; only incomplete evidence uses `HISTORY_FALLBACK`.

## 10. Timeout, cleanup, and disposition rules

Every loop consumes a sealed positive integer budget and also checks exact
attempt, worker, overall, cleanup, and accounting deadlines. There is no Retry
field and no automatic replay. Exactly one non-reentrant `StopInstances` state
is reachable after the instance-start request. Every started path converges on
stop observation and closure.

The launch finalizer timeout must be no greater than the deployed Lambda
timeout, and the sealed Lambda-duration maximum must contain every reachable
finalizer invocation and duration. The state-machine total timeout, phase sum,
instance-running maximum, Step Functions transition maximum, S3 request maxima,
and cleanup window must conservatively contain their reachable paths.

Preparation closure, start, resource-use, finalizer, cost, retrieval, and final
manifest schemas each use closed conditional disposition constraints. PASS
requires non-null exact predecessors, success booleans, stopped state, and empty
failure fields. Fully evidenced FAIL requires typed outcome failure fields but
zero missing categories. Incomplete evidence requires truthful nullable
coordinates and exact missing categories. A malformed/pre-start path may bind
the closure seed without fabricating launch, start, terminal, use, cost,
retrieval, or final-manifest predecessors.

PASS requires all runtime controls fresh and equal, one accepted start, the
expected deterministic synthetic SUCCESS terminal and manifest, all immutable
chains, stopped state, finalizer PASS, retrieval PASS, cost PASS, complete final
manifest, and empty failure codes. A declared synthetic failure is FAIL. A
missing/unavailable control, terminal, stop, cost, retrieval, or closure fact is
INCONCLUSIVE unless the schema mandates FAIL. No failure is relabelled PASS.

Malformed launch or live input uses only the exact closure seed to publish typed
pre-start INCONCLUSIVE evidence. It cannot start the instance, infer missing
values, or publish a launch/start PASS.

## 11. Zero-science boundary

Every record carries the accepted ten zero-science counters. The future 14-path
implementation may import only standard-library control-plane code plus the
finalizer's tightly bounded AWS protocol library boundary. It may not import
EBU framework, Stage E harness, project runner, scientific configuration,
simulation, model, trajectory, Gate, RNG, result inspection, or scientific
output code. Synthetic worker payloads remain deterministic inert counters and
hashes in exactly SUCCESS, FAIL-AFTER-CHECKPOINT, and TIMEOUT modes.

No AWS-C0 result is Stage F readiness, a scientific outcome, or permission to
run a real experiment.

## 12. Integration and implementation boundary

This candidate consists of exactly six new mode-`100644` authority files. It
must be independently audited and explicitly accepted before integration. A
later reachability correction may modify only
`tests/framework/test_validation_reachability.py`, freeze these six hashes and
coordinates, add exact positive/negative lanes, and preserve all prior lanes.
It modifies exactly one existing path and adds zero paths. The sealed scope
counts are global `144 -> 158` and descendant `94 -> 108`.

Only after authority and reachability integration may a future implementation
candidate add exactly the same 14 new paths already named by the accepted AWS-C0
implementation manifest. No fifteenth implementation path, authority-path
modification, Stage E modification, live operation, or scientific operation is
authorized. The implementation must be rebuilt from the accepted authority,
not blessed by reducing assertions around an unaccepted draft.

Authority acceptance itself still authorizes none of the three operator
statements, preparation actions, live actions, or AWS execution. Those remain
post-packet user decisions under the accepted choreography.

## Completion marker

`AWS_C0_COST_RUNTIME_RETRIEVAL_CLOSURE_CORRECTION_AUTHORITY_COMPLETE`
