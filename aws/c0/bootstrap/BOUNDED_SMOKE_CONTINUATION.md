# Bounded platform-smoke continuation

On 2026-09-06, after the completed host inventory, the user requested completion
of the smoke test and readiness checks before scientific execution, with
continuation without ordinary permission interruptions. The originating local
AUDITOR task (`01a011df-5b07-7693-a117-731908097325`, user turn
`01a0775a-d802-7c90-8c2b-1881912a4e94`) delegated the complete bounded
platform-smoke path to the sole AWS-C0 controller. The controller verified the
actual user message in that task before proceeding.

The authorized workflow includes local byte-bound staging design and validation,
staging the reviewed image/controller/unit, controlled CloudFormation change-set
construction/review/execution, and exactly one platform smoke attempt on the
retained t3.small instance. It includes ordinary local commits and exact cleanup.
It does not authorize a larger or additional instance, scientific execution,
registered study/model/trajectory, publication, repository push or release.

Account 623609441658, us-east-1, instance i-048bac00bdb540a4e, aggregate USD50
ceiling remain fixed. The prior inventory approval is exhausted; this is new
continuation authority, not replay of its packet. Historical V5/V6 triplets,
24-object lineage and preparation/live separation are preserved. Do not claim
that the user reviewed future AWS identifiers or that generated approval text
was typed by the user. Preserve the actual delegated authority basis separately.

## Exact host staging prerequisite

`staging_transport.py` builds a three-object plan from committed raw LF bytes
and the already verified archive SHA-256. Controller and unit hashes must refer
to the current committed correction; image/worker bytes remain unchanged.
Stage to content-addressed keys under the existing permitted preparation prefix
in ebu-stage-f-results-k7m4p2, with conditional create, SHA-256 checksum, exact
returned VersionId, and exact-version readback. No future VersionId is guessed.
The three receipts are a subset of the eight deployment artifacts, not three
additional members of the frozen 24-object closure lineage.

The temporary private document EBU-C0-Stage-492a4f1-v1 has no command parameters.
Its body is generated only after validating the actual three write receipts.
The only preparation-session exception is one expiring inline policy
EBU-C0-Staging-Transport-v1 granting exact-document read and exact-document/host
SendCommand. Bind role ID, AWS-C0-PREP-492a4f1, source identity konrad, exact
principal ARN and expiry at most two hours. The SSO operator may only create,
verify and remove this exact temporary transport; no caller, trust, MFA,
AdministratorAccess or base/session-policy change is implied.

One bounded start, one staging command, at most 900 running seconds, and
verified stop/transport cleanup are required. Recompute cost and verify current
coordinates, role controls, bucket controls and session cleanup reserve first.
The existing instance profile must have a separately verified exact permission
plan for the three downloads; lack of permission is not authority for a broad
policy. No package installation, external image pull or ECR API is needed.

The host command verifies free space and absent destination files; downloads
exact S3 versions and checks their bytes/checksums; loads the already verified
image archive once; verifies the configuration, platform, non-root user and
immutable repository digest; creates the controller/unit exclusively with root
ownership; reloads systemd definitions without enabling or starting a unit; and
removes only its exact verified download scratch files. Conflicts refuse rather
than overwrite. A partial failure must preserve its observations and trigger
stop/cleanup; no repeated smoke attempt or silent repair is permitted.

Staging is not smoke success. The final deployment/launch records must still
bind real post-staging artifacts, exact change-set contents, bounded credentials,
pricing and the preserved evidence graph before the one platform smoke attempt.
