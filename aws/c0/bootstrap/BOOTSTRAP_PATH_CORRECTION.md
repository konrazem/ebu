# First-deployment bootstrap transport correction

Authorized by the user's 2026-09-06 approval of the narrowly scoped bootstrap
correction. Additive prerequisite only; historical V5/V6 and 24-object lineage
are unchanged. No scientific execution or large instance is permitted.

Account 623609441658, us-east-1, instance i-048bac00bdb540a4e only. Create or
verify one private Command document, EBU-C0-Bootstrap-492a4f1-v1, separate from
CloudFormation ownership. Never precreate or replace EBU-C0-Start-v1.

The exact SSO operator may create/verify this one document and attach/remove
one temporary inline policy EBU-C0-Bootstrap-Transport-v1 on
EBU-C0-Operator-492a4f1. This is the sole narrow exception to the earlier
SSO-preparation prohibition. It does not change konrad, AdministratorAccess,
trust, role tags, duration, original base policy, compact V5 session policy,
instance-role policy, or unrelated resources. The preparation session receives
only exact-document GetDocument/DescribeDocument and exact-document/instance
SendCommand, conditioned on its role ID/session name, source identity konrad
and a maximum two-hour expiration. No wildcard, PassRole, document creation,
live-session grant or arbitrary command is added to that session.

Read back policy and document before use. Allow bounded IAM propagation up to
240 seconds; never add permissions on an AccessDenied response or blindly
repeat uncertain mutations. Refuse conflicting pre-existing material.

The initial parameter-free command inspects fixed host facts only: machine,
Docker/AWS CLI versions, Docker daemon, exact EBU file metadata/hash and the
verified image's presence. No image/service execution, software installation,
file copy, S3 fetch, Docker load or user shell is permitted. Successful
inventory is not successful bootstrap or smoke. Subsequent staging material
must be separately byte-bound and validated; no silent document change.

Only start the retained instance after a fresh cost bound covers this operation
and retained resources within the standing aggregate USD 50 cap. One command,
60-second execution timeout, at most 900 seconds of instance running time for
this inventory, with stop verification after success or failure. Missing
software is evidence, not permission to install packages.

Remove the temporary policy after use/failure, verify original policy state,
and delete the bootstrap document only if this attempt created it and exact
version/content still match. Never delete pre-existing or CloudFormation-owned
documents. These are exact cleanup exceptions, not general delete permission.
Preserve all local creation/readback/dispatch/stop/cleanup evidence. No AWS
execution is implied merely by generating this local material.
