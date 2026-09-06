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
That amendment has NOT been implemented or authorized by this document.

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
