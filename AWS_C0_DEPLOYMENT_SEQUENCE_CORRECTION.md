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
