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
