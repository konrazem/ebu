# AWS-C0 truthful first-deployment sequencing correction

## Checkpoint status: NOT_READY — independent review NOT APPROVED

The implementation below is a local candidate, not an approved deployment
path. The original 119-test pass did not cover the complete public schema gate.
The new full-entry regression is intentionally retained as a failing test, not
skipped or marked expected-failure. It demonstrates that accepted inherited
requirements remain unimplemented; no AWS continuation is permitted on the
strength of this candidate.

The narrow read-only reviewer confirmed three blockers:

- The inherited live-packet reconstruction set still requires all eleven
  controls, including workflow and SSM observations before their deployment.
  Moving only the lightweight control preimages does not remove this cycle.
- Launch requires the existing audit/static publication evidence, sealed EC2
  role context, and journal-capture budget evaluation, which are absent from
  the runtime's closed input interface.
- The current similarly named publication helper binds a future final manifest.
  It is not the accepted earlier audit/static publication binding and must not
  be substituted into launch.

The historical schemas and their requirements are preserved. A separately
scoped producer/runtime attachment and phase repair must implement the accepted
bindings, version the affected reconstruction phases, and demonstrate a complete
schema-valid positive path plus negative cases before independent approval.
No credentials, AWS calls, staging, deployment, instance start, smoke, or science
were used in this local correction. The completed host-inventory authorization
is exhausted and cannot be reused.

## New authority boundary found while implementing reconstruction

### Subsequent exact user authorization and local R64 implementation

The user subsequently authorized packet
`97be006dd5112b00854779a8ba668c6c5bbf0aae37f922907920db17d77d7b9f`
in full on 2026-09-07. That packet identifies the exact action as
`ec2:DescribeSecurityGroups`; its identity resolves the shortened "R64 ec2"
phrase in the accompanying message. The proposal and its original status are
preserved below and in the contract; a separate authorization reference records
the later decision. This authorizes the prospective correction, not waiver of
any gate or inference that AWS has been contacted.

A distinct read-plan/v2 now adds only R64. Its producer and runtime reconstruct
and verify the original 63-row v1 prefix and mapping against the unchanged pins,
bind the exact amendment and original-plan identities, retain eleven controls,
and add R64 only to the VPC mapping. Only the current unpublished packet/v6
schema/body is attached to the new plan; historical definitions are unchanged.

The new supplemental ingress producer and consumer derive the sorted union of
group IDs from complete, fresh R02/R04 responses for the exact stopped t3.small
instance. They cross-check owner, VPC, interface inventory, primary and secondary
group associations, request targets, chronology and actual item counts. R64
must return every requested group exactly once, with explicit empty
IpPermissions arrays. The count is computed from those arrays, not supplied
from a schema constant. Exact response metadata/request IDs, HTTP200, zero
reported retries, no continuation token and 64KiB per-source bounds are required.
These functions consume authenticated collector material; API-shaped JSON and
hashes alone are expressly not treated as authentication.

Ten focused tests pass, including rehashed target/source/response mutations and
exact UTC variants. Pinned CPython3.12.10 compilation and whitespace checks pass.
The existing read-only reviewer APPROVED this component after its timestamp
syntax fix. The global three-call reservation/collector, phased reconstruction
attachment and workflow integration are still required and are not covered by
that component approval. No IAM policy, credentials or AWS resources changed.
Work continues through those obligations; this is not a completion checkpoint.

The next local component adds a closed, bounded call-budget ledger. It reserves
at most one read in each of PREDEPLOYMENT, POSTDEPLOYMENT and EXECUTION_PREFLIGHT;
completion does not grant a fourth slot. Every next phase retains earlier
entries and requires new R02/R04 sources. A pending, uncertain or failed call
is terminal and does not return a slot. Successful completion must bind the
exact reserved sources, targets, collector, timing and actual ingress receipt.
Expected ledger identities must come from independently accepted prior phases,
not be accepted merely because an untrusted sender supplied matching hashes.

The local store uses a deterministic private `/private/tmp` directory per
attempt and exclusively created numbered snapshots. File and directory sync
precede a successful reservation return. Competing writers have one winner;
partial writes and missing histories are preserved and block continuation.
It does not silently repair, overwrite or reset the ledger. The store is local
crash/race protection, not authentication or protection against a user deleting
files, replacing the host or changing an unbound attempt. No cloud transport is
attached to it yet. Nineteen focused ingress/budget/store tests and pinned
compilation pass; the existing reviewer independently APPROVED both the pure
transitions and the local store as components only. Overall NOT_READY remains.

The prospective phase-binding record now joins a successful ingress observation
to its reserved slot, exact 64-row plan and independently anchored prior budget.
It preserves the complete prior history, requires the current phase's own fresh
sources and collector, and recomputes freshness at consumption. R04 must finish
before reservation; the later R64 call cannot retrospectively justify an early
reservation. A reviewer-found omission of that ordering was fixed with a
rehashed-ledger negative regression, and the component was then APPROVED.
Twenty-four focused ingress/budget/store/phase tests pass. The complete suite at
`5d31093` ran 200 tests: 199 passed, one public-entry reconstruction-binding error,
zero assertion failures, skipped tests or expected failures. These new records
are not yet the complete eleven-control reconstruction set or a cloud gate pass.

The VPC output/v2 component now derives the original network facts from the
complete R04–R12 API responses, with explicit R02 dependency and the new R64
phase proof. It cross-checks all attached subnets, the unique primary subnet,
subnet ownership, route-table selection/main fallback, conditional NAT routes,
image/volume/snapshot targets, endpoints and interface-scoped Elastic IPs.
Conditional NAT and snapshot absence comes from actual dependency responses;
an empty response collection must be explicitly present. The returned output,
canonical bytes, hashes and conservative freshness age are regenerated from
those sources and compared in full by the consumer.

This implementation accepts one complete page and no more than sixteen items
per ancillary EC2 response, and also enforces the independently sealed EC2
limits when they are stricter. A continuation token or an incomplete/oversized
set refuses; generic multipage support is not claimed. R02/R04/R64 remain
nonempty. Ancillary R05–R12 may carry actual empty collections when semantically
valid. Historical v1 decoded/output schemas remain untouched. Seven VPC tests
and thirty-one combined focused tests pass. Review found and verified a fix
for primary-versus-secondary subnet substitution; independent sealed-bound
checks were also added and reviewed. The component is APPROVED; the complete
eleven-control attachment and authenticated collector are still unfinished.

The route-table fallback and lack of a subnet ID for an implicit association
follow the [AWS DescribeRouteTables API](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeRouteTables.html).

### Local constrained-role policy preparation

The reviewed local CloudFormation template now prepares the single prospective
finalizer-policy delta required for R64: `ec2:DescribeSecurityGroups` with
`Resource: "*"` and an `ec2:Region` equality condition for `us-east-1`. The
action is not folded into a generic read statement. The compact historical V5
operator session ceiling already contains `ec2:*`; it is therefore preserved
byte-for-byte rather than rewritten. This is only a local template binding:
there has been no IAM mutation, credential use, AWS call, or claim that the
regional condition substitutes for the exact attached-group request guard.

### Partial reconstruction progress boundary

A separate `aws_c0_runtime_control_reconstruction_progress/v2` envelope now
binds the exact v2 read-plan identity and all eleven ordered control slots. It
can carry canonical candidates only for the three currently implemented output
kinds: ACCOUNT_REGION, INSTANCE_PROFILE_SOLE_ROLE, and VPC_NETWORK_PATH. It does
not revalidate original source receipts, freshness, attempt or collector
context; a later source-bound attachment must do that before any pass claim.
The remaining eight slots are neutral explicit unresolved states with null outputs. Its fixed
`PARTIAL_NOT_READY` disposition and false completion flag prevent it from being
used as, or confused with, the historical v1 complete-reconstruction pass gate.
No live packet or cloud action consumes this partial envelope.

The next local attachment reruns those three constructors from retained source
receipt bundles. It requires an independently supplied predeployment-context
identity, a common phase start/freshness/session context, the independently
sealed EC2 pagination bounds, and the exact same R02 receipt for the profile
and VPC paths. Its output remains `PARTIAL_SOURCE_BOUND_NOT_READY`; it neither
fills the other eight controls nor changes the historical/live gates.
The address request uses its documented
[network-interface-id filter](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeAddresses.html).
Missing association state is conservatively refused rather than inferred.

The account and instance/profile reconstruction producers are now implemented
against their unchanged closed output schemas. R01 must match the independently
supplied constrained-session ARN/UserId and sealed collector region; it does
not establish or infer MFA or source identity. R02/R03/R13/R14 must show the
exact owned, stopped t3.small, its exact associated profile, and the sole role
with the expected unique RoleId. Ordered fresh responses, exact request scopes
and complete output bytes/hashes are checked. A matching ARN does not excuse
a changed RoleId. Both components received focused independent APPROVAL;
thirty-nine combined focused tests, pinned compilation and schema checks pass.
They are three implemented output components (account, instance/profile, VPC),
not a complete eleven-control set. The suite at `272bac5` ran 212 tests with
211 passes and the same one public-entry missing reconstruction binding.

The next source-specific local candidate reconstructs SERVICE_QUOTA from the
exact ordered R34 GetServiceQuota and R35 GetAWSDefaultServiceQuota receipts.
Both must be fresh authenticated successes for EC2 quota L-1216C47A, and both
must report a positive integral value. The emitted control value is always the
account's applied R34 value; the AWS default is retained as a separate witness
and is never substituted for it. The source-bound attachment now reruns four
constructors under the same immutable caller, collector, phase and freshness
context. Three direct quota tests and six progress/attachment tests pass. This
component has received focused controller review only because the active user
instruction forbids creating an assistant; no independent-review claim is made.
The attachment remains `PARTIAL_SOURCE_BOUND_NOT_READY` with seven unresolved
controls and cannot satisfy the historical v1 live gate.

The account producer follows the actual fields documented by
[GetCallerIdentity](https://docs.aws.amazon.com/STS/latest/APIReference/API_GetCallerIdentity.html).
Its role-ID syntax follows the already accepted local context schema, rather
than assuming every AWS unique identifier has one fixed length.

### Prospective IAM source-mapping correction

The user explicitly authorized a prospective IAM reconstruction output/v2 and
corresponding read-plan/v3 whose only semantic correction is `source_row_ids`
R15–R19. Historical output/v1 and read-plan/v1/v2 remain unchanged. Plan/v3
reconstructs and validates the complete v2 predecessor, preserves all 64 rows,
actions, resources, conditions and every other control mapping, and changes
only the IAM output kind/schema binding. This grants no AWS action, permission,
scientific execution, cost increase or publication authority.

The user's subsequent authorization to fix every necessary AWS-C0 stage permits
one explicit evidence-only cross-control binding from the already required R14
`iam:GetRole` observation to IAM output/v2. The binding carries only the role
ARN, instance-profile ARN and canonical trust-policy SHA-256. Direct IAM policy
sources remain exactly R15–R19; R14 remains owned by
`INSTANCE_PROFILE_SOLE_ROLE`. The binding adds no AWS read or mutation and does
not change any historical schema, action, permission, scientific boundary,
cost ceiling or publication authority. IAM list pagination remains closed and
bounded by the already sealed IAM pagination limits.

The dependent partial progress/v3 and source attachment/v2 are prospective
extensions only. They bind read-plan/v3, insert IAM in the original eleven-
control order, carry the sealed IAM pagination limits, and recompute the exact
four-control attachment/v1 predecessor before accepting the fifth output.
They remain `PARTIAL_NOT_READY` and `PARTIAL_SOURCE_BOUND_NOT_READY`: five
source-bound predeployment controls leave six controls unresolved and cannot
claim the historical complete reconstruction set.

The next local producer implements the already frozen
`BUCKET_CONTROLS_KMS` output/v1 without changing its schema or read plan.
R20–R25 must be fresh ordered authenticated S3 successes for the sealed bucket.
R31–R33 must all be absent for authenticated AES256 encryption and must all be
fresh ordered authenticated KMS successes for an `aws:kms` key. The one-page,
sixteen-tag KMS bound is enforced; a truncated tag response, unusable key,
public bucket policy status, incomplete public-access block, or substituted
bucket identity fails closed. This is a pure producer implementation and adds
no AWS action, permission, scientific authority, cost, or publication scope.

The dependent progress/v4 and source attachment/v3 are prospective extensions.
They preserve read-plan/v3, insert `BUCKET_CONTROLS_KMS` in the frozen control
order, add only the sealed bucket name and typed bucket identity to context/v3,
and recompute the exact five-control attachment/v2 predecessor. Six source-
bound predeployment controls leave five controls unresolved, so both records
remain explicitly partial and not ready.

Continuation from `2b11b1b` investigated the actual missing
`runtime_control_reconstruction_set_identity` producer/consumer obligation,
not just the absent field. A distinct prospective phased reconstruction set
can preserve the original 63 reads and eleven control slots while carrying
predeployment, postdeployment, execution-preflight and completion evidence at
the correct times. The independent reviewer confirmed that design direction.
Already-due reads still require fresh, correctly targeted, complete responses;
future reads cannot be invented and old complete-reconstruction dispositions
cannot label phase fragments.

One required reconstructed fact has no accepted observation source. The frozen
`decoded_vpc_network_observation` requires `ingress_rule_count` exactly zero,
with source rows R04–R12. Neither those rows nor any other row in the closed
R01–R63 universe reads security-group ingress permissions. Network-interface
responses contain group identifiers, not those groups' complete rule sets.
The same interface/group identifiers are consistent with an empty rule set or
with an inbound rule added to that group: hashing those identifiers cannot
distinguish the two cases. This is a local observability conflict, not an
observed claim about the actual instance's rules.

The scoped independent review found no accepted separate fresh ingress-rule
source. The frozen contract's `NO_ROW_OUTSIDE_R01_THROUGH_R63` and
`NO_UNDECLARED_READ` invariants forbid silently adding the missing API call.
The R51 amendment changes only its specified policy-absence result and does
not authorize a new action outside that closed universe. No zero was supplied
from a schema constant, a planned template, an old snapshot or group IDs.

AWS's [NetworkInterface response definition](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_NetworkInterface.html)
documents group identifiers. Its [DescribeSecurityGroups response](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSecurityGroups.html)
includes the actual inbound `ipPermissions`. The
[EC2 service authorization reference](https://docs.aws.amazon.com/service-authorization/latest/reference/list_ec2.html)
lists no resource-level scope for DescribeSecurityGroups and supports the
`ec2:Region` condition. Consequently an added IAM allow would have Resource `*`
within us-east-1; exact instance-attached group IDs must additionally be enforced
by the reviewed request guard. This limitation is disclosed, not represented as
an IAM-enforced exact-group restriction.

The proposed minimal new authority is the complete object at
`/pending_network_ingress_amendment_packet` in
`aws_c0_deployment_sequence_correction_contract.json`. Its identity is SHA-256
of its complete canonical JSON, with no trailing newline:
`97be006dd5112b00854779a8ba668c6c5bbf0aae37f922907920db17d77d7b9f`.
It preserves every original row and historical record, adds only prospective
R64 DescribeSecurityGroups, keeps the zero-ingress requirement, and permits at
most three bounded exact-group reads in the existing one-smoke sequence after
all gates pass. Only the two named constrained roles/session ceilings could
gain that single read action if required; konrad, AdministratorAccess, trust,
MFA, session durations and security-group rules stay unchanged. It does not
increase the aggregate USD50 cap, host count, instance type or smoke count.
All other effective permissions remain unchanged. The additional read permission
must be removed from any surviving named role during verified cleanup; the
proposal expressly covers that cleanup and temporary-session disposal.
Its allow/deny rules apply only to this additional R64 authority, not as a new
grant for the rest of the existing bounded smoke sequence. Public publication
remains forbidden; existing privately staged evidence is not a public release.

This packet is a proposal, not user authorization or deployed policy. No code
gate, historical schema, read-plan pin, permission or AWS resource has been
changed to accept R64. The full-entry regression remains unskipped and red.
No AWS API, credentials, staging, deployment, instance start, smoke, science,
push or publication occurred while investigating and preparing this decision.

The existing independent read-only reviewer recomputed the final packet hash
above, verified both frozen source pins and the named finalizer role, and
APPROVED the proposal for presentation only. This is not approval of an
implementation or AWS execution. Local canonical-identity, source-pin, scope,
document consistency, deterministic schema generation and whitespace checks
pass. Runtime code and tests are unchanged from `2b11b1b`; its 180/181 result
remains the last complete suite run, not a newly claimed green suite.

Exact proposed user authorization (not yet received):

> I authorize AWS-C0 network-ingress source amendment packet SHA-256 97be006dd5112b00854779a8ba668c6c5bbf0aae37f922907920db17d77d7b9f in full. Prospectively add R64 ec2:DescribeSecurityGroups, preserve the original R01–R63 and historical evidence, and implement, validate, independently review and commit the required local bindings. After all gates pass, permit at most three bounded reads of the exact security groups attached to i-048bac00bdb540a4e in account 623609441658, us-east-1, within the existing one-smoke authorization. If required, add only this read action to EBU-C0-Operator-492a4f1 and EBU-C0-Corrected-Finalizer-v1 and their session ceilings, with all other effective permissions unchanged. I understand this action requires regional IAM Resource:* and exact group targeting must be enforced by the reviewed request guard. Remove the added permission during verified cleanup. Do not change security-group rules, konrad, AdministratorAccess, trust, source identity, MFA or session duration. Retain the aggregate USD50 cap, one existing t3.small host, one smoke and no scientific execution, larger compute, push or public release. Continue the already authorized workflow automatically within these boundaries.

## Broader local repair: phase producers and a result-contract boundary

The subsequent AUDITOR delegation (source turn
`01a0783b-9e1e-7ba0-bf20-8e551f9d338c`) requests the broader local attachment
repair under standing local-work authority while expressly preserving accepted
semantics. It does not supply an exact user amendment of a frozen response rule.

Draft pure local producers now retain the exact 63 accepted action/resource/
condition obligations and bind their source bytes. Four producer phases separate
predeployment, deployed resources, current-execution preflight, and completion.
R37 DescribeExecution remains ALWAYS but cannot have a receipt before execution
exists. Future rows are explicitly NOT_YET_PRODUCED with no receipt or evaluated
condition; they are never labelled NOT_CALLED or PASS. Actual due receipt
validation checks the accepted closed shape, source/caller/row/action bindings,
canonical request/response hashes, chronology and fixed pagination bounds.

These are low-level draft producers, not a complete reconstruction or runtime
attachment. They explicitly return complete_reconstruction_claimed=false. They
do not certify resource-selector resolution, full pagination closure, source
authentication by themselves, publication bindings or launch readiness. Seven
focused offline tests cover preservation, chronology, omitted observations,
false ALWAYS conditions, drift, tampering and the R51 boundary below. The
previous full-public-entry regression remains failing and unskipped.

### R51 cannot be repaired solely by moving its phase

Subsequent explicit user authority on 2026-09-06 now permits the prospective
POLICY_ABSENT amendment described below. That supersedes the pending-decision
status of the historical proposal, not the historical HTTP200 receipt meaning.
The new pure producer/finalizer validator and new result schema preserve exact
R49/R51/R50 call order, function ARN, revision/code identity, source/caller,
request/response bytes, error type and sealed freshness. Old receipt schemas
remain unchanged. The v2 phase producer binds the same R49/R50 receipt objects
to the R51 result, and distinguishes CALLED_POLICY_ABSENT from API success.
No credentials, cloud APIs, deployment or permission changes are authorized.
This amendment alone does not complete the broader runtime/publication
attachment work or establish readiness.

The accepted R51 row is ALWAYS lambda:GetPolicy for the exact finalizer function;
its called receipt requires HTTP 200. The template creates that function but no
AWS::Lambda::Permission or other resource-policy producer. Thus the local design
does not supply the policy whose successful retrieval the contract requires.
This is a predicted contract incompatibility, not an observed AWS failure.

AWS documents GetPolicy as reading the resource-based policy and documents
ResourceNotFoundException/404. Its EventBridge troubleshooting also treats that
GetPolicy error as a reason to add a resource-policy permission. Reading these
public documents did not access the account or use credentials:

- https://docs.aws.amazon.com/lambda/latest/api/API_GetPolicy.html
- https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-troubleshooting.html
- https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-lambda-permission.html

No permission is added merely to satisfy the evidence check. Nor is a 404
relabeled as an old-contract HTTP200 success. Both would exceed the instruction
to preserve accepted semantics in this evidence-only repair.

The proposed no-permission-change resolution requires an explicit prospective
R51 result-contract amendment: retain the exact mandatory call and authenticated
request/response capture; accept either the existing exact-policy/HTTP200 branch
or a distinct POLICY_ABSENT branch only for authenticated
ResourceNotFoundException, with matching R49/R50 proof of the exact function's
existence. AccessDenied, generic404, timeout, missing bytes, wrong function,
transport failure or missing existence evidence must still refuse. Historical
records stay unchanged; absence must never be presented as policy success.
That was the historical proposal, not authority granted by this document.
The subsequent explicit user amendment above authorized its implementation;
commit `4449418` implements it and the narrow reviewer APPROVED that component.

## Local source-proof checkpoint after the R51 amendment

R51 is resolved locally, not by an AWS retry. Its seven focused tests pass.
The broader path remains NOT_READY and has a separate confirmed architecture
boundary. These facts must not be presented as an R51 failure or a policy-change
request.

The accepted source-structure proof requires four exact state-machine pointers:
`/States/PreflightTaskFailed`, `/States/ObserveSsmCompletion`,
`/States/PollController`, and `/States/SafeClose`. None exists in the current
ASL source. Its actual `PreflightFailureClosure`, `PollAttempt`, and
`EmitSafeClose` states invoke Lambda helpers with reachable S3 operations:

- `preflight_failure` -> `_history_fallback` -> `_exact_environment_record`
  -> `_fetch_receipt` -> `_s3_get` -> `_aws_request("s3", ...)`.
- `poll` -> `_find_roots` -> S3 exact-version Get and ListObjectVersions.
- `safe_close` -> `_find_roots`, `_put_record`, and
  `_exact_environment_record` -> S3 reads/listing/publication.

The new `inspect_journal_zero_s3_obligations` diagnostic parses exact source
bytes and records concrete counterexamples. It never returns a complete proof
or readiness PASS, even when it finds no counterexample. Four tests cover the
actual conflict, ineffective state aliases, non-proof status, and unexecuted
nested definitions. The same diagnostic was run using actual CPython 3.12.10
built in an isolated temporary directory; the installed interpreter was not
changed. No scientific source or workload was executed.

The narrow reviewer independently confirmed that no producer can truthfully
emit the frozen zero-S3 certificate while preserving both this ASL behavior and
the certificate semantics. Attaching fields, aliases, or increasing a numeric
budget does not repair it. The R37 execution-observation carrier is a separate
attachment task: a bounded Preflight result/history carrier is a candidate,
not an implemented or verified readiness claim. Preflight's five source reads
remain a complete budget-inventory obligation, not an independently proved
contradiction of its narrower three-read branch.

The safe role-context producer is also now implemented as a partial utility.
It requires the complete unchanged private snapshot schema and root digest,
stopped-state and source chronology, and the four exact R02/R03/R13/R14
authenticated receipt shapes. Actual sole role/profile/RoleId data must agree.
Four tests include drift, pagination, missing sources, snapshot shape/state/time,
and root-identity versus stored-byte hash separation. The caller must still
provide the fully derived and bound snapshot and phase evidence: this utility
does not independently certify workflow, quota, IAM-set derivation, or runtime
attachment. The reviewer found no blocker to committing these explicitly
partial NOT_READY utilities.

The minimum next scope decision is a prospective local ASL/helper architecture
correction that implements the frozen zero-S3 design. The current correction
explicitly preserves ASL behavior, so that change is not inferred here. A
different choice to allow nonzero helper S3 would instead require an explicit
semantic amendment with complete capture, capacity and cost proofs; it is not
silently substituted. Historical records, permissions, science boundaries,
24/23 counts, capture channels, 512-envelope/1MiB bounds, and AWS prohibition
remain unchanged. Full-public-entry validation remains mandatory and failing;
none of the component passes authorizes deployment or execution.

Validation at this partial checkpoint: 142 tests ran, 141 passed, one errored;
zero skips or expected failures. The complete public prepublication regression
still refuses the missing `runtime_control_read_plan_identity`. The 15 focused
R51/role/diagnostic tests pass. Schema determinism, compilation under actual
CPython 3.12.10, and whitespace checks pass. Audit-v4/static-v4 entry-point tests
ran in the full suite; their component success is not full readiness.

### Subsequent overnight authority: local architecture repair may continue

Before this checkpoint was sealed, a newer delegation arrived from AUDITOR.
The actual source user message was read and verified in turn
`01a0788e-15f2-79d3-a26b-66c0cd65fff5` of the same source task: the user asks
for overnight takeover, smoke if possible, and authorizes "all necessary work
including running AWS instances." The delegation preserves the existing USD50
cap, retained small instance, one platform smoke, cleanup and no science or
larger instance. This is not an exact future packet approval invented by the
controller.

That newer broad implementation authority permits the necessary prospective
local ASL/helper architecture correction, including directly affected transport
and evidence bindings, to implement the frozen zero-S3 design. It supersedes
the earlier local file/ASL-behavior limitation for this bounded repair, not any
historical evidence meaning. No zero-S3, authentication, resource/cost bound,
24/23 count, permission-ceiling or scientific requirement is relaxed. The
partial utilities are committed first; architecture repair continues locally.
AWS remains untouched at this checkpoint and cannot proceed on component tests
or the standing instruction alone without complete gate validation and review.

### START dispatch interface component

The next local component restores the accepted full
`aws_c0_ssm_dispatch_request/v2` envelope: document name/version, exact instance,
attempt identity, and exactly 21 singleton-array semantic parameters. The
generator validates the unchanged historical schema and the runtime independently
matches those semantics against explicit argv. The transport pair names now
match the accepted `SsmDispatchRequestCanonicalJsonBase64` and
`SsmDispatchRequestSha256`; the standalone and embedded SSM document still have
exactly 23 parameters. The missing explicit region argument and bucket/argument
name mismatch are corrected. Downloaded sources can verify attempt and deployed
document/version bindings but cannot supply semantic argument values.

Five focused tests pass, including complete construction/schema/runtime/CLI
round trips, split/unknown/extra envelopes, explicit-argument disagreement,
cross-source drift, refusal before credentials, and the actual isolated token
regex guard. The reviewer found and then verified fixes for underscore-token
and exact second-resolution UTC handling, and APPROVED this component only.
Historical schema files and IAM policies are unchanged. No command document,
systemd service, container, credential flow or AWS operation was executed.

This is START parsing/construction, not complete source-sidecar attachment.
The source-sidecar, short local helpers, ASL architecture, full publication and
journal proof attachments and complete public gate remain NOT_READY. The
controller does not treat this component approval as smoke readiness.

Post-commit validation at `6e658fa` ran 147 tests: 143 passed, two failed and two
errored, with zero skips/expected failures. Three failures shared the exact-path
gate's older omission of the newly authorized SSM-document repair; the fourth
was the existing complete-public-gate error. The prospective path enumeration
now adds only that exact SSM path under the verified overnight source authority.
Historical Gate 1 exclusions remain unchanged, and a negative test proves an
unrelated path is still refused. Both targeted path tests and both affected
audit-v4/static-v4 public-entry tests pass after this scope-binding correction.
This does not convert the unresolved complete-public-gate error to a pass.

### Separate helper request transport component

The prospective `aws_c0_controller_local_helper_request/v1` is now a pure local
plan/validator for STATUS or SAFE_CLOSE only, never START. It embeds the exact
unchanged dispatch/v2 START request and a launch-bound attempt deadline. The
runtime validator requires separate expected START/deadline inputs, validates
the complete singleton-array semantics, and refuses early, expired, extended,
noncanonical or cross-attempt requests. The maximum interval is the existing
43200-second workflow bound, not a relaxation of any shorter launch or instance
budget. Helper envelopes reuse the existing two transport slots; all 21 semantic
parameters remain unchanged and the START validator rejects helper types.

Four helper tests plus the five START tests pass (9/9). The existing reviewer
APPROVED this pure component for a partial NOT_READY commit, not runtime use.
Actual base64/hash decoding from helper argv, independently bound local-source
loading, local status/marker actions, SSM branches and ASL wiring are still
required. No helper has been sent or executed, no credential flow invoked, no
AWS resource touched, and no historical schema changed.

### Persistent local operational status component

The controller now projects successful START, heartbeat-zero/latest-heartbeat,
and terminal publications into a closed 16 KiB local operational cache. Each
projection keeps the root identity separate from the complete stored-byte hash
and actual publication version/checksum. Heartbeats must advance exactly once
and cannot move backwards in observed time; the terminal flag does not imply
journal handoff completion. The handoff flag is set only after successful worker
exit validation and controller-journal handoff publication.

Status lives beneath the existing persistent StateDirectory, not the ephemeral
RuntimeDirectory removed at service exit. Root-owned mode-0700 directories are
opened without following symlinks, and mode-0600 status replacement is atomic
and synchronized through directory-relative operations. No service settings,
permissions, cloud objects, scientific boundaries or historical schemas change.
Seven focused tests pass, including a filesystem model of runtime-directory
removal, unsafe ownership/mode/symlink refusals, chronology and publication-byte
bindings. These tests do not execute the service or the synthetic worker.
The existing independent reviewer inspected both fixes and APPROVED this
component only for a partial NOT_READY commit; the reviewer did not claim to
execute the parent-run tests or approve the remaining integration.

This is a local operational cache, not an authenticated evidence root or a
successful independent readback claim. Bound-source loading, SSM/ASL attachment,
full proof bindings and the complete public gate
remain unfinished. The broader correction remains NOT_READY; AWS and credential
access remain prohibited during this local-only amendment.

The subsequent decoder/status-reader component bounds encoded transport before
decoding and requires canonical base64, canonical JSON and the exact same-byte
digest. Helper validation still requires separately supplied expected START and
deadline; the helper cannot supply its own trusted context. The status reader
opens the exact file relative to the pinned private directory, refuses symlinks,
nonregular files, multiple hard links, wrong ownership/modes and oversized input,
then checks stable metadata and the closed source-bound cache. It never creates
a missing directory/file, obtains credentials, issues a command or declares
missing/incomplete status complete. Clock freshness remains an explicit future
caller obligation, not an assumption that a consistent older snapshot is fresh.

The four new decoder/reader tests and the earlier sixteen START/helper/status
tests pass (20/20). The same independent reviewer APPROVED this component only,
after inspecting code/tests; these are parent-run offline tests, not AWS or
service execution. The full suite at preceding commit `de49024` ran 159 tests:
158 passed, one existing full-entry schema error, no skips or expected failures.
The error is not waived and does not authorize any cloud continuation.

### Local helper command integration after `e47db87`

The existing flat local source file is now cross-bound to explicit helper argv,
the exact prepared launch bytes, the saved START dispatch and all three chained
GET captures. Descriptor-pinned reads require root-owned private directories and
single-link bounded regular files. Rehashed/rechained negative tests check the
actual operation, source identity, request-envelope hash and sequential capture
timestamps, rather than merely detecting broken hashes. This is operational
source consistency, not acceptance of the still-incomplete full provenance
sidecar required by the historical evidence contract.

Dedicated local STATUS and SAFE_CLOSE entry points do not prepare requests,
request credentials, use S3, execute containers or start services. STATUS keeps
missing cache, stale heartbeat, terminal-awaiting-handoff and completed journal
handoff distinct; no state claims an authenticated evidence root or synthetic
outcome. Its 20000-byte bound plus framing fits the 24000-character inline SSM
stdout limit documented by
[AWS GetCommandInvocation](https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_GetCommandInvocation.html).

SAFE_CLOSE writes one private exclusive marker requesting a readiness observation
only after accepted START and fresh heartbeat-zero/latest-heartbeat projections,
and before terminal. The marker does not stop the worker and does not claim
completed safe close. This preserves the existing workflow's healthy-observation
then continued-execution behavior. Actual cleanup and accepted safe-close evidence
remain the later workflow/closure responsibilities; a local marker is not their
substitute.

The standalone and embedded command documents retain exactly 23 parameters and
route both helper operations before request-directory creation, preparation and
the one original service start. Helpers exit explicitly; classifier/helper
failure propagates under set-eu. Only typed START can reach the original startup
path. Twenty focused tests pass; the existing independent reviewer approved the
loader, actions and routing components separately. No AWS command document,
service or cloud resource was executed or modified in this local validation.
SSM/ASL consumption and complete evidence proofs remain required before smoke.

### Full local validation at `0a0c35f`

The complete offline suite ran 181 tests in 121.054 seconds: 180 passed,
zero assertion failures, one error, zero skips and zero expected failures.
The retained full-public-entry regression refuses the missing
`runtime_control_reconstruction_set_identity`. All R51 amendment tests and the
audit-v4/static-v4 entry-point regressions passed within this run. This is not
an approved complete evidence chain or readiness result.

The existing read-only reviewer independently APPROVED the six-file helper
component, including the final fresh-heartbeat narrowing and shell failure-path
regressions. That component approval does not approve the unfinished ASL,
publication, phase-reconstruction or source-journal proof integration. The
historical full-suite results below remain historical and are not overwritten.
No AWS access, credentials, permission changes, deployment, instance start,
smoke, science, push or publication occurred during this local validation.

### Historical validated local checkpoint at `d67a644`

The later source instruction `01a07a46-d7cd-7970-b7bd-677f9a2ba25f` requires
continuation through all necessary engineering to the bounded platform smoke,
not termination at this historical local checkpoint. It does not waive any
readiness proof or authorize scientific work. Runtime/cloud work remains gated
on completed local integration and fresh bounded account/cost/session checks.

The next integrated component constructs the complete accepted read-plan/v1,
retaining all 63 exact actions, resource selectors, conditions and pagination
bounds. The constructor and runtime independently check pinned SHA-256 hashes of
the canonical accepted sealed_read_plan, its rows and its control mapping. The
map hash is the canonical complete required_control_mapping hash; the contract
identity is the canonical complete sealed_read_plan hash. The complete plan
identity includes the selected freshness interval (an exact integer 1–300s).
This is an input plan, not a claim that R37 or any future action has happened.

Three focused tests pass, including independently rehashed action/resource/map
mutations and runtime-gate attachment. The same reviewer independently recomputed
the three source pins and APPROVED this component only. The full-entry candidate
now supplies this real constructor output and advances to the missing
runtime_control_reconstruction_set_identity error. No missing reconstruction is
treated as a pass, and the following earlier checkpoint counts remain historical.

The complete suite ran 163 tests in 86.613 seconds: 162 passed, zero assertion
failures, one existing error, zero skips and zero expected failures. The error
remains `DeploymentSequenceTests.test_complete_schema_valid_chain_through_public_prepublication_gate`,
whose first missing live-packet field is `runtime_control_read_plan_identity`.
The audit-v4/static-v4 and exclusive-output regression tests pass within this
suite; this does not make their synthetic receipt fixtures production evidence.
All six directly involved Python files compile under the pinned CPython 3.12.10,
and the deterministic derived-schema check passes.

A local inspection of the same failing candidate confirms further missing read
plan/reconstruction, publication, sealed-role and journal-budget bindings, plus
incorrect candidate identity kinds. The seed passes its shape check, but shape
alone is not an authenticated observation or completion claim. No accepted
schema has been weakened and the full-entry regression is intentionally neither
skipped nor reclassified as an expected failure.

Remaining local integration order: independently bound source loading and
freshness/completion handling; actual SSM/ASL helper attachment with the frozen
zero-S3 behavior; complete publication, phase-reconstruction and source-journal
proof producers with real full-entry positive/negative coverage. These are
unfinished implementation requirements, not a request for wider AWS permissions.
No AWS access, credentials, deployment, instance start, smoke, science, push or
publication was performed while making or validating this checkpoint.

This is the bounded local-only correction requested in the existing AUDITOR
task, user turn `01a077f4-71f5-7421-a5c3-c178e8c7c9a1`, delegated to the sole
controller. It permits implementation, local validation, normal local commits
and one narrow independent review. It does not authorize an AWS call, credential
renewal, upload, deployment, instance start, smoke or scientific execution during
this correction. The source user message asks continuation after the reported
blocker; this document does not claim the user typed a future generated packet.

## Minimal change

The existing closure seed required an authenticated workflow observation before
the workflow existed. Both the preparation closure and live packet also required
eleven observed controls before CloudFormation created the workflow and SSM
document. Existing records remain historical and immutable.

Seed-v2 instead binds intended deployment input bytes and fixed coordinates,
explicitly not deployed identity. Launch remains an input-only record, referring
only to already published artifacts and seed versions. The generic template
artifact is not a later resolved-parameter manifest: the latter must never be
substituted into the eight-artifact set or bound by an earlier seed.

Preparation retains six initial observations. Preparation closure and live
packet retain nine observed controls, excluding the two not-yet-created workflow
and SSM document. Their expected bytes are explicit deployment inputs. The
unexecuted change set remains an actual observed input to the later operation.

The exact prior deployment authority is recorded before ExecuteChangeSet.
The live session itself must already have separate valid assumption authority;
the exact deployment statement uses its actual issued expiry and authorizes
ExecuteChangeSet/publication/start only, never the already completed assumption.
Following the one authorized execution and successful stack completion, eleven
authenticated controls are collected. Live-authorization-v6 binds these results,
their producing action, the earlier authority and the intended inputs before
StartExecution. Its later publication does not retroactively authorize execution.
Workflow definition, role, logging and document content/version must agree with
the intended source bytes and real deployment outputs. The Lambda repeats direct
workflow/document checks before the workflow can start the instance.

The postdeployment authorization remains the existing later object, not an extra
pre-live object. The 24/23 counts and exact six V5/V6 historical bytes/kinds remain
unchanged. The explicit transitive version map is in
`aws_c0_deployment_sequence_correction_contract.json`; old schema meanings are
not repurposed. No dummy receipt, predicted VersionId, preliminary foundation
deployment, replay, scientific behavior, new instance or permission broadening
is permitted. The same account, region, retained t3.small and USD50 cap apply.

The correction does not change trust, caller permissions, compact V5 policy,
scientific payload, controller transport arity, SSM command body or ASL behavior.
Any AWS continuation must use fresh actual observations and separately valid
bounded authority; local tests are not deployed readiness.
