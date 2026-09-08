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

If a failed preparation has already created content-addressed versions below
the fixed preparation prefix, a fresh recovery must not collide with, delete,
or replay them. `recovery_plan` therefore derives a v2 staging namespace below
the same permitted prefix from the fresh attempt identity. It changes only S3
object coordinates; controller, unit, image, AWS account/Region/instance,
temporary-policy limits, one-start/one-command bounds, USD50 ceiling, and all
no-container/no-science conditions remain unchanged. The original v1 plan
remains unchanged for historical validation.

Staging is not smoke success. The final deployment/launch records must still
bind real post-staging artifacts, exact change-set contents, bounded credentials,
pricing and the preserved evidence graph before the one platform smoke attempt.

## Failed image-load diagnosis

If the one staging command fails after it has verified and retained the exact
archive, preserve that attempt and its cleanup as terminal. A fresh diagnostic
may start the same stopped `t3.small` once, issue one parameter-free private SSM
command, and stop it within 600 seconds. The diagnostic may only hash and inspect
the retained archive, read Docker client/server facts, check whether the exact
configuration identity is already present, read the bounded Docker journal
interval corresponding to the failed command, and report free space. It must not
load or run an image, write or delete a host file, start or enable a service,
contact S3, or execute science. Its temporary document and exact-document/host
transport policy must be absent again after the verified stop.

This diagnostic is recovery observation, not replay of the terminal staging
command and not a platform smoke. It changes no artifact byte, historical plan,
AWS permission boundary, scientific content, or USD50 aggregate ceiling. A
subsequent corrective staging attempt must be separately versioned from the
preserved v1/v2 plans and must bind the diagnostic result before it can run.

The versioned v3 repair is limited to the exact files retained by the failed v2
command. It revalidates their root ownership, mode, length, and SHA-256, calls
`docker image load` once with the explicit `linux/amd64` selector, and includes
bounded Docker stdout/stderr in any failure record. On success it performs the
same exact image/configuration/reference checks and exclusive controller/unit
installation as v2. It contacts neither S3 nor a registry, never runs a
container, and preserves the scratch files if any step fails. The prior v1/v2
plans and command bodies remain unchanged.

If v3 loads the exact image but fails because the containerd image store does
not resolve a configuration digest as an image name, the v4 finalizer must not
load it again. It inspects the saved tag, verifies the exact configuration ID,
platform, user, working directory, tag, and manifest digest reported by
`docker image ls --digests --no-trunc`, then exclusively installs the retained
controller/unit bytes and reloads systemd definitions without starting them.
The v4 plan binds the v3 plan and authenticated v3 failure. All no-container,
no-smoke, no-science, stopped-instance, cleanup, and cost boundaries remain.

On the containerd image store, an exact tag lookup can return the expected
configuration, platform, user, and working directory while omitting the legacy
`RepoTags` array. The v5 finalizer therefore removes only that redundant array
assertion. It retains the exact tag as the lookup and image-list filter and
still requires exactly one image-list row whose repository, tag, and manifest
digest match the sealed values. It binds the terminal v4 failure and changes no
other v4 operation or boundary.

The authenticated v4 failure was initially misclassified. Exact script-line
reconstruction proves that line 33 was the combined configuration-ID, OS, and
architecture assertion; the later legacy `RepoTags` assertion was not reached.
The terminal v5 command failed at that same combined assertion, so removing the
legacy assertion did not repair the observed mismatch. Neither failure output
identifies which combined member differed. The v5 image-list digest check,
controller/unit installation, and daemon reload were not reached. Any further
AWS observation must be a fresh, separately authorized, versioned diagnostic
that reports the non-secret exact-tag metadata fields individually without
loading or running the image, installing files, or consuming the platform
smoke. The v4 and v5 ledgers remain immutable and terminal.

The next authorized stage is one v2 image-metadata diagnostic. It binds the
terminal v5 plan, failure evidence, and command ID and reports the exact-tag
configuration ID, OS, architecture, user, working directory, repository
tags/digests, and bounded filtered image-list rows as separate observations.
It does not assert that mismatches pass. It may start the existing stopped
`t3.small` once, issue one parameter-free command, and must stop it within 600
seconds and remove its exact temporary document and policy. It cannot load or
run an image, mutate a host file, invoke systemd, contact S3 or a registry,
consume the platform smoke, or execute science.

The v2 diagnostic passed. The loaded image's exact tag, sole filtered
repository/tag row, manifest digest, OS, architecture, user, and working
directory all match. The sole mismatch is representational: Docker 29.7.2 with
the containerd image store reports image `Id` as the sealed manifest digest,
not the OCI configuration digest. A prospective finalizer repair may therefore
bind the already-proved archive manifest-to-configuration relationship, require
the loaded image ID and image-list digest to equal the sealed manifest digest,
and retain the separate exact configuration-field checks. It must not weaken or
remove any manifest, platform, user, working-directory, retained-byte, cleanup,
cost, no-container, no-smoke, or no-science requirement.

The authorized v6 finalizer implements that single proved correction. It binds
the terminal v5 plan/failure and authenticated v2 diagnostic, revalidates the
retained archive manifest-to-configuration relationship, then requires the
exact loaded tag and image-list row to identify the sealed manifest digest.
Exact OS, architecture, user, working directory, controller/unit bytes,
exclusive installation, daemon-reload-only, stopped-instance, temporary-control
cleanup, and cost boundaries remain unchanged. It does not reload or run the
image and cannot execute the platform smoke or science.

The v6 finalizer passed. It installed the exact retained controller and unit,
performed daemon-reload only, stopped the instance, and removed the temporary
v3 transport. The image was not reloaded or run, no service was started or
enabled, and the one platform smoke remains unspent. Host staging is complete;
the next phase is the separately gated deployment preparation and exact
unexecuted change-set construction required by the deployment sequence.
