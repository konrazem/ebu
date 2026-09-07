# AWS-C0 truthful first-deployment sequencing correction

## Checkpoint status: FRESH REPLACEMENT PACKET READY — GATE 1 REQUIRED

On 2026-09-07 the first durably reserved PREDEPLOYMENT R64 request failed with
AWS `UnauthorizedOperation` because the deployed
`EBU-C0-Operator-492a4f1` inline policy did not allow
`ec2:DescribeSecurityGroups`. The failed append-only ledger is preserved as a
terminal attempt and must not be reset, retried, or replayed. The retained
instance was freshly verified `stopped`, no cloud mutation or smoke occurred,
and the failed preparation credentials were disposed.

The user subsequently authorized one recovery correction. It permitted a fresh
replacement preflight identity and only the already specified temporary
`ec2:DescribeSecurityGroups`, `Resource: "*"`, `ec2:Region=us-east-1` IAM delta
for the named constrained AWS-C0 roles as required. This recovery did not
authorize a second actual smoke, another permission, security-group mutation,
scientific execution, or public release. The exact UTF-8 recovery statement has SHA-256
`3532ac7f30849e1e90c54ea6f160a8b8eda94aed1ef3156dfee9466ffbe59ee3`.

The single fresh replacement attempt completed PREDEPLOYMENT R64 successfully
at `2026-09-07T14:36:24Z`. It read exactly security group
`sg-0d3be0dc4769f9f44`, retained the authenticated request and response, and
derived `ingress_rule_count=0`. Its attempt identity is
`e82a52b8d60a860c6254ef0936e6ef4c0c4ed2febe710fb48d6da7eb64a75340`;
its phase-binding file SHA-256 is
`a3eac1f5a0c32f05d147b7aa27853914dbe675ff567da11f12d73d6c38678b23`.
The first failed ledger remains terminal and was not replayed.

R64's 300-second freshness window closed at `2026-09-07T14:41:24Z` before the
remaining control observations and a complete atomic preparation packet could
be constructed. The successful recovery attempt is therefore preserved but
cannot truthfully authorize continuation, cannot be replayed, and cannot be
replaced again under the consumed one-attempt recovery authority. Full AWS
continuation remains fail-closed pending one new exact authority for a fresh,
atomic full preflight.

Verified cleanup removed only inline policy
`EBU-C0-Temporary-R64-Recovery-20260907`, proved it absent, proved the original
operator base policy remained byte-equivalent at SHA-256
`c2488566da9cd3a3b96f5d60cc2078858621db990d2c1e97293c61852e42b1b8`,
disposed the temporary session material, and reverified the exact retained
`t3.small` instance `stopped`. The cleanup completion SHA-256 is
`06aeb0ae51b66435b5dc1f2b3144b05e511360b72bff0cafe05850132d044f27`.
The finalizer role was absent and was neither created nor modified. No instance
start, platform smoke, scientific execution, push, merge, or publication
occurred.

The mandatory integration sequence is: AWS-C0 local implementation; one
bounded AWS platform smoke; evidence and cleanup passes; final independent
review; only then an exact merge-to-main proposal. No merge or push is
authorized. Scientific work must begin later from clean `main` or a fresh branch
based on it, never by continuing this accumulating AWS-C0 branch. When smoke
closes, the report must identify the precise merge base/head, CI and review
evidence, and requested merge authority.

The user has now authorized exactly one new atomic full-preflight attempt. It
must use a fresh identity without replaying either preserved ledger, collect
and bind every required preparation control including R64 inside one
300-second freshness window, and construct the complete preparation packet.
Only the exact temporary `ec2:DescribeSecurityGroups`, `Resource: "*"`,
`ec2:Region=us-east-1` delta may be added to the named constrained roles as
required, and it plus all temporary credentials must be removed after success
or failure. The one platform smoke remains unspent. Instance start, deployment,
smoke, science, push, merge, publication, and release remain prohibited until
the resulting packet receives its separate exact Gate 1 authorization. The
exact UTF-8 authorization statement has SHA-256
`7846fa788cda01d209d724e4f67e225af92b9df1d5636c852f48d38256518155`.

That single authorized attempt was durably reserved at
`2026-09-07T15:34:56Z` with fresh attempt identity
`7c671d75b76a10fcd98f90ce03c4a2982b11224064c175bedddd371ad1b6e374`.
It failed at the constrained-session transition before credentials were issued,
before the 300-second control-collection window began, and before any R01-R64
control call. The collector supplied role-session name
`AWS-C0-ATOMIC-PREFLIGHT-492a4f1`, while the frozen trust and bootstrap
contract require exact preparation session name `AWS-C0-PREP-492a4f1`.
AWS therefore returned `AccessDenied` for `sts:AssumeRole`. This was a local
collector-coordinate error, not evidence that any required AWS control failed.
The attempt is terminal; it was not retried or replayed, and no preparation
packet was constructed.

The failure path removed only inline policy
`EBU-C0-Temporary-Atomic-Preflight-20260907`, verified the unchanged base-policy
SHA-256
`c2488566da9cd3a3b96f5d60cc2078858621db990d2c1e97293c61852e42b1b8`,
confirmed that no temporary credentials existed, and reverified the retained
`t3.small` instance `stopped`. The attempt-reservation, failure, and cleanup
file SHA-256 values are respectively
`53cf9515703473cc2852d21edc39e1d9cbcc2f445308d7344690d64a467172e7`,
`3d43a2b939295eb7cbe66f0a5cd3fe99bc819df9e98bd027fe22003cd74b1654`,
and `3e63cf324a4a34e0afd5c89843595ebee668edf4f22da4b9cacc2e17d68b2e1b`.
The collector is corrected offline to use and verify the exact sealed session
name, but this consumed authority does not permit another live attempt.
Continuation requires one separately authorized fresh replacement atomic
full-preflight. No instance start, deployment, smoke, science, push, merge,
publication, or release is authorized.

The user has now explicitly authorized exactly one such fresh replacement. It
must use the corrected exact session name `AWS-C0-PREP-492a4f1`, must not replay
any preserved attempt, and must collect and bind every required preparation
control including R64 inside one 300-second window before constructing the
complete packet. It may refresh read-only pricing evidence if required. Only
the previously authorized temporary regional `ec2:DescribeSecurityGroups`
permission may be applied, and that permission plus all temporary credentials
must be removed after success or failure. The exact UTF-8 replacement statement
has SHA-256
`e9276a2e75b02d7032f0d0207977c461ecd5a6520844f40cc1d884da21602727`.
The stopped `t3.small`, one unspent platform smoke, USD50 cap, historical
schemas, permissions, and scientific content remain fixed. Instance start,
deployment, smoke, science, push, merge, publication, and release remain
prohibited.

The single fresh replacement was durably reserved at
`2026-09-07T15:58:45Z` under attempt identity
`7c3081f711bb5d0ce775daa04c48ca73744f72d4c68601bb6650d58f46a75f3a`.
The corrected exact `AWS-C0-PREP-492a4f1` session was issued successfully and
the authorized read-only pricing refresh completed. Before the 300-second
control window began, local client construction failed because this installed
AWS SDK exposes Service Quotas as `service-quotas`, while the collector used
`servicequotas`. No R01-R64 control call or R64 budget occurred, and no packet
was constructed. This attempt is terminal and was not retried or replayed.

The fresh pricing model has SHA-256
`531adf3926363d78e8b04ec519d287b47a980e7fd7231c004934ce6636d80fad`,
is valid through `2026-09-08T17:58:50Z`, and bounds the exact sealed resource
limits at 175 USD minor units against the unchanged 5000-minor-unit cap. It is
read-only evidence, not Gate 1 authority. Cleanup removed only
`EBU-C0-Temporary-Replacement-Preflight-20260907`, proved the base policy
unchanged, disposed the issued temporary credentials, and reverified the
existing `t3.small` stopped. Reservation, failure, and cleanup SHA-256 values
are respectively
`2c489e69100918ad617ccd17ea35f3ea7f7c580e3c662ac0cdbe78c5b63d6fae`,
`50e4a33d66b6d91ef18eff7fec4cba8f8495cb9503badd264f96f9f96a2af6e2`,
and `ee44ca0815bc0851bc3de6e8676feec965b0afaf71cfffdffba36dba9b7dd75c`.
The SDK coordinate is corrected offline to `service-quotas`. Another live
attempt requires separate exact authority. All later-stage prohibitions remain.

The user has now supplied that separate exact authority for one fresh
replacement atomic full-preflight after the SDK-coordinate failure. It binds
the installed SDK identifier `service-quotas`, the exact session name
`AWS-C0-PREP-492a4f1`, and a fresh attempt identity; none of the preserved
attempts may be replayed. The valid bounded read-only pricing evidence may be
reused, or refreshed read-only if required. Only the previously authorized
temporary regional `ec2:DescribeSecurityGroups`, `Resource: "*"`,
`ec2:Region=us-east-1` permission may be applied, and it plus all temporary
credentials must be removed after success or failure. Every required control,
including R64, must be collected and bound within 300 seconds, and the complete
preparation packet must be constructed and validated. The exact UTF-8
authorization statement is 913 bytes and has SHA-256
`b74e4d81312e7c564f2d059640ba6633941d942554de588443d40fe3a01f6c71`.
The stopped `t3.small`, one unspent smoke, USD50 cap, schemas, permissions, and
scientific content remain fixed. Instance start, deployment, smoke, science,
push, merge, publication, and release remain prohibited.

The one SDK-corrected replacement was durably reserved at
`2026-09-07T17:38:00Z` under fresh attempt identity
`aa4fb7ab315f4ad86bf92fd7c0ee773723d38e8eeca8578d7ad5ef1aff2c6c08`.
The exact preparation session was issued, the validated USD1.75 pricing model
was reused, and 22 authenticated control receipts through R23 were collected
inside the new window. R20 confirmed the sealed bucket is in `us-east-1`, R21
confirmed versioning enabled, R22 confirmed AES256 default encryption, and R23
confirmed all four public-access-block controls true. The required R24
`s3:GetBucketPolicy` call then returned AWS `NoSuchBucketPolicy` because the
sealed bucket has no resource policy.

This is a real fail-closed bucket-control precondition, not another local SDK
coordinate error: the frozen `BUCKET_CONTROLS_KMS` producer requires R20-R25 to
be successful authenticated reads and requires a bounded strict-JSON bucket
policy with non-public policy status. R25, R31-R35, and R64 were not called; no
R64 budget was created and no preparation packet was constructed. The attempt
is terminal and will not be retried or replayed. Its reservation and failure
file SHA-256 values are respectively
`7a66d9e1340ff3042196c6e2125b707254dea7ad37b62c1b5ba13ce20fcd6271`
and `bb465855f63bc69818ece9fbdf850fa83c5d2fa2f5a2022814440b391d0772f2`.

Verified cleanup removed only
`EBU-C0-Temporary-SDK-Corrected-Preflight-20260907`, disposed the issued
temporary credentials, proved that the sole remaining inline policy is the
unchanged base policy and no managed policy is attached, and reverified the
existing `t3.small` stopped. Cleanup SHA-256 is
`01167e906856982ac894de69df947daa5d9612e52b1733b5baeaa6ca3ba54b0c`.
The one actual platform smoke remains unspent. Continuation now requires a
separate exact authority for the required sealed-bucket policy remediation and,
after verified remediation, one separately authorized fresh atomic full-
preflight. No such remediation or later attempt has begun.

The user has now authorized all required steps for the platform smoke path and
directed that the already identified remediation steps proceed without repeated
authorization prompts. In the present gate this authorizes one exact
sealed-bucket policy remediation followed by one fresh atomic full-preflight,
with every preserved attempt remaining terminal and unreplayed. The remediation
may add only a deny-only TLS enforcement policy to
`ebu-stage-f-results-k7m4p2`: `s3:*` is denied for both the bucket ARN and its
object ARN when `aws:SecureTransport` is `false`; it grants no principal or
action. Its canonical 240-byte JSON has SHA-256
`be7fdd7bb9af2436ac6b7af34520eb2c0262d52816823a57347970c7400d8fc0`.
The exact general authorization statements have SHA-256
`4f94936ce46521e241d50ded3995555dd47aa19f864ecd264fe36573da0af3b3`,
`42345f9541f76815ddf344b20f2a1ae6b3717dbd3935a55245ec76efd8935683`,
and `7ece0910dc9bb14751aa5c99feee076510720fb6723323f96f60a6fdd412d532`.
The fresh preflight retains the exact session, corrected SDK coordinate,
300-second complete-control window, USD50 cap, stopped `t3.small`, one-smoke
limit, and mandatory temporary-permission and credential cleanup. A resulting
packet must still be bound by the frozen packet-specific Gate 1 mechanism
before instance start, deployment, or smoke; no future packet identity is
predicted here. Scientific execution, push, merge, publication, and release
remain prohibited.

The exact bucket remediation completed at `2026-09-07T18:09:47Z`. Before the
write, authenticated reads reconfirmed the sealed bucket in `us-east-1`,
versioning enabled, AES256 default encryption, all four public-access-block
controls true, and no bucket policy. AWS then accepted the exact 240-byte
deny-only TLS policy and returned that policy byte-equivalent on readback with
`PolicyStatus.IsPublic=false`. No grant, rollback, instance start, deployment,
smoke, science, or publication occurred. Reservation, prestate, and completion
SHA-256 values are respectively
`2eb78b503b30d1cec39453b9c63a1ecf5fd1ceb465a54202177fff0f23e0b869`,
`5fc18c3019df9bebe2d502b95bbf745944abca1449074b0f479c903af696d7b3`,
and `697c9526a3f02cb231376eff1279375d62d2676b5818e689ffa28bf6972dd19f`.
The authorized fresh no-replay atomic full-preflight is not yet begun.

That fresh attempt was reserved at `2026-09-07T18:13:10Z` under identity
`ccb9918407378490ea7b7cde0afdf81f9c9eda9e1b116b33d22c9ffbbce01b90`.
It collected 26 successful authenticated receipts through R35, including the
now-passing R24 and R25 bucket controls, then reserved its sole R64 budget. R64
returned `UnauthorizedOperation`. The temporary role policy had been written
and read back, but the constrained session was assumed in the same second with
no effective-policy propagation proof. The fixed preparation session policy
already permits `ec2:*`; the missing guard is therefore a confirmed-allow IAM
simulation before issuing the constrained session. This attempt is terminal
and will not be replayed. Reservation, failure, R64 reservation, and cleanup
SHA-256 values are respectively
`c90c8dd09a86c3ccd762af594776a0cfdaa2ecb3ae0457b184fdddcd8cc2385a`,
`8fb268bd65a1ad7c9226337facd0a1b8422b762a7bfe1616fc9e0e2369c5e989`,
`217a8cc96f3a27b7016bf219f0ebfaa1e3676e069faf0a6c797082e7d8a517ee`,
and `594e4568e2130d35d5af8898e4f3ea462b66057e935892e1759d1f637a56a1a3`.
Cleanup removed the temporary permission, disposed credentials, retained the
non-public bucket remediation, and reverified the stopped `t3.small`. Under the
standing all-required-steps authority, one fresh attempt after adding the
effective-policy propagation guard is authorized and not begun.

That guarded attempt was reserved at `2026-09-07T18:16:27Z` under identity
`58c4cfa9a461e1b0eb074a50ac5638f5cc8ca8d9b46ce8911ff0189ecf1c7651`.
IAM simulation returned `allowed`, but the constrained session issued only five
seconds later still received R64 `UnauthorizedOperation`. The official EC2
authorization reference confirms `ec2:Region` is supported for this action;
the remaining correction is a 60-second STS propagation interval after the
confirmed simulation. This attempt is terminal and cleanup passed. Reservation,
propagation-proof, failure, and cleanup SHA-256 values are respectively
`ad454d11dd9f4de0e548f6ebceb7c278fe16eca1e5562439d52de9f2e478d21b`,
`6301863402bf1d0f867f3ace840aa3063c16b945989ddce13b5f459fc66101fc`,
`904db40e9c127655610ce07cf634af29c56d1a1cd7a9256597bf51ff177f7e65`,
and `79d6bc1a9f57e7c52b52b9ba19b2354841a98e6c6a6a30bdca5c9c76c1693c6f`.
One fresh attempt after that correction remains authorized and not begun.

The 60-second-propagated attempt was reserved at `2026-09-07T18:19:59Z`
under identity `6a745471e62c587c8ba092e9ead1f661f6dfe6fe75c96111091ab7e83cd7b78e`.
R64 succeeded and its authenticated receipt, ingress observation, completed
budget, and phase binding were durably written. Packet construction then
stopped on a local VPC-builder context mismatch: the collector passed
`freshness_max_seconds` to `validate_r64_phase_binding`, whose freshness is
already sealed in the read plan. The attempt is terminal and cleanup passed.
Reservation, failure, and cleanup SHA-256 values are
`6b133bdebb7481ec07f3a2dbf56b2cd8c56c98a1b16d0fb9caf950bc370ce1d7`,
`7441a81a195ddfa06beaef71c48725363080c59a76e0759532161558a23ffb99`,
and `8815e4fc065fec7f313d74e1951633b317a56292d28cfc8ab1cda3ba6c7931fd`.
No further fresh attempt is authorized by the consumed authority.

The user has now exactly authorized one new fresh atomic full-preflight after
terminal attempt
`6a745471e62c587c8ba092e9ead1f661f6dfe6fe75c96111091ab7e83cd7b78e`.
It may correct only the VPC phase context by omitting the unsupported duplicate
`freshness_max_seconds` argument; the read plan's 300-second bound remains
unchanged. It must retain the verified deny-only bucket policy,
`service-quotas` SDK identifier, exact `AWS-C0-PREP-492a4f1` session, 60-second
IAM propagation interval, sole temporary regional
`ec2:DescribeSecurityGroups` permission, mandatory cleanup, stopped
`t3.small`, one-smoke limit, and USD50 cap. Every required control including
one fresh R64 must be bound and the complete packet constructed and validated.
The exact 823-byte UTF-8 statement has SHA-256
`b9b59a8f9c357ad53ac3fcb7f015803d9b903f57ef6439bf71db559f50324040`.
Science, push, merge, publication, and release remain prohibited.

The single authorized corrected attempt completed at
`2026-09-07T19:09:40Z` under fresh identity
`03a1179d756d119f66a87c30d14bd13ab637a3ece9101cbe7fcbb2ab6479dbca`.
All six predeployment control outputs were reconstructed from authenticated
receipts in the frozen order, R64 read exactly security group
`sg-0d3be0dc4769f9f44` and derived zero ingress rules, and the complete control
window was 7 seconds against the unchanged 300-second maximum. The source
attachment SHA-256 is
`b918f8378c99225cca6ad8de28bb90c6363cbd6e2ff44bcb409d7b7766018413`.

The complete 465,749-byte `aws_c0_preparation_packet/v6` has identity and
complete-byte SHA-256
`9ebb5af1f13a6b13f66ec15748613b13dc170b02507677773aa7038920815231`.
It binds implementation commit `6f7df4852f7eb9a1590d4db283ec49624eb2a251`,
tree `f679eb997a6d2cc3870b2158ef1e2eee03b332ff`, read-plan/v3 identity
`c9d2abf122a8b48828ce40fe4b8beb1346c7e7c19bfc85a1268d1747bb3d3bf7`,
and a USD1.75 maximum against the USD50 cap. Independent schema and semantic
validation passed. No publication occurred.

Cleanup removed only `EBU-C0-Temporary-VpcContext-Preflight-20260907`,
disposed the temporary credentials, proved the unchanged sole base policy and
no attached policies, retained the non-public deny-only bucket policy, and
reverified the existing `t3.small` stopped. Reservation, R64 phase binding,
completion, and cleanup SHA-256 values are respectively
`c3c8d495edddfc317987e856c672d19d2f7ba1ee78981e56fc17073516774e44`,
`caece59b2ae16125c07047d3c60ba25d79a2524c49d3247d32b16a9004d8e268`,
`737dba1be1520b0d31cd5d1f5d062626cdbdba317ba4bf5955d17cf4f86a77d0`,
and `438e0d1045b155b3d1ea689c0ca4a04c038191613a8dc62072f72e6db8da6413`.
The one platform smoke remains unspent. Instance start, deployment, and smoke
remain blocked until the exact packet-bound Gate 1 statement is supplied.

The packet-bound Gate 1 statement was received through a Markdown-escaped
transport form no later than `2026-09-07T20:04:37Z`. That 1,649-byte form has
SHA-256 `b88356331e0c03192d574eb758aa06a158f6ebcf89239c7c1f2e351c9de9885f`.
The user's explicit direction to remove those presentation escapes was observed
no earlier than `2026-09-07T20:10:36Z`. Removing the 77 escape characters
produces the exact required 1,572-byte statement with SHA-256
`0255ae0b12910e8548660c8302f3c9eb4f2a4456da47d2382d68d413d2028e89`,
but the packet's exact preparation session had expired at
`2026-09-07T20:09:33Z` before that ambiguity was resolved.

The frozen choreography requires the packet's exact unexpired caller before
every mutation and requires a fresh preparation identity and approval after
session replacement. Therefore no Gate 1 AWS call, mutation, instance start,
deployment, platform smoke, or science occurred. The expired packet and both
authorization messages remain historical evidence and cannot be replayed. The
next permissible recovery is a fresh preparation identity, packet, and exact
packet-bound approval.

The user then explicitly authorized all steps required to perform the platform
smoke. The exact 104-byte UTF-8 statement has SHA-256
`43bae506aa510764e33a1a95df768ac5031d0bd2181be1d03cef05859c262908`.
Within the existing frozen boundaries, this authorizes exactly one fresh
replacement atomic preflight to construct a new preparation identity and
packet after the expired packet. The expired packet and every prior attempt
remain historical and cannot be replayed. The collector retains the exact
session name, 60-second IAM propagation interval, 300-second freshness bound,
sole temporary regional `ec2:DescribeSecurityGroups` permission, mandatory
cleanup, stopped `t3.small`, one-smoke limit, and USD50 cap. Scientific
execution, push, merge, publication, and release remain prohibited.

The controller will remove Markdown presentation escapes itself without asking
the user to retype a statement. The new packet's exact Gate 1 approval remains
a cryptographic boundary that can only be rendered after that packet exists;
this goal authorization does not invent or preauthorize an unknown digest.

The single authorized expired-packet recovery attempt completed successfully at
`2026-09-07T20:23:14Z` under fresh attempt identity
`d0f00f06a9d8008b5971694a55d8c29ae6810ac10a5e829fd9662fc5fcef9746`.
All six controls were reconstructed in the frozen order in 7 seconds under the
unchanged 300-second maximum. R64 read exactly security group
`sg-0d3be0dc4769f9f44` and derived zero ingress rules. The source-attachment
SHA-256 is `3817962f52503a8307f73838c5bdae63091133f0ff6e969255bd186d422d9ece`.

The new 465,749-byte `aws_c0_preparation_packet/v6` has identity and
complete-byte SHA-256
`51c57d0efe0444ebf1cc4ef8634878703f123da069eebac75a13bbf3fba7bf46`.
It binds implementation commit `71c9db01fa1102ae38803b109603d734c91cb9b9`,
tree `46deae7d70681c9655893156399541c9a05a684c`, and preparation-session
expiry `2026-09-07T21:23:06Z`. Independent local schema and semantic validation
passed. Cost remains USD1.75 under the USD50 cap. No publication occurred.

Attempt cleanup removed only
`EBU-C0-Temporary-ExpiredPacket-Recovery-20260907`, proved the base policy
unchanged, disposed temporary credentials, and verified the existing
`t3.small` stopped. The cleanup record is complete with no errors. A later
independent AWS recheck could not authenticate because the local AWS login had
expired; this does not replace or weaken the successful authenticated cleanup
evidence. No deployment, instance start, smoke, or science occurred. The one
platform smoke remains unspent pending exact packet-bound Gate 1 authority.

The fresh packet's packet-bound Gate 1 statement was received through a
Markdown-escaped transport form at `2026-09-07T20:29:44Z`, before the bound
preparation session's `2026-09-07T21:23:06Z` expiry. The 1,649-byte transport
form has SHA-256
`2e47bdb80285152d42e4b0e77493923ef528e68ef00c91ad874696fe88d828eb`.
Removing its 77 presentation escape characters produces the exact required
1,572-byte statement with SHA-256
`63b2d269482455b9a80623bfae92c2228e794d5c1ee7c8876c9ec288877ea75b`.
It matches packet
`51c57d0efe0444ebf1cc4ef8634878703f123da069eebac75a13bbf3fba7bf46`
and authorizes only the six enumerated preparation actions while preserving
the five enumerated denials.

The first read-only AWS identity recheck at `2026-09-07T20:31:40Z` reported
that the local AWS session had expired and requires interactive `aws login`.
No Gate 1 AWS call or mutation, instance start, deployment, smoke, or science
occurred. Preparation is authorized but fail-closed pending AWS
reauthentication; the exact approval does not authorize live execution,
science, replay, delete, or terminate.

The later IAM Identity Center recheck at `2026-09-07T20:40:56Z` succeeded for
profile `ebu-admin` as
`arn:aws:sts::623609441658:assumed-role/AWSReservedSSO_AdministratorAccess_64c4d6b6ee31634c/konrad`.
This is the expected non-root bootstrap identity, and the mistaken default
root-login flow was cancelled without using it for a preparation action.

That successful login does not recover the packet's exact constrained
preparation session. Its public receipt has SHA-256
`f3d936f903033b7de7c67bb9be9306a84e889f2d35fe9a2b88e84ca394183b34`
and binds the original STS request ID and `2026-09-07T21:23:06Z` expiry. The
attempt's already-preserved cleanup record, SHA-256
`2f089d73820e4e0979a0d36f10cc76ff5a19d6a1d8a028a11cac028a15fcc3cc`,
proves those temporary credentials were disposed. Re-assuming the same role
and session name would create a replacement session, which the frozen
choreography requires to have a fresh packet and approval. Therefore packet
`51c57d0efe0444ebf1cc4ef8634878703f123da069eebac75a13bbf3fba7bf46`
and its accepted authorization remain historical evidence but cannot be used
for a mutation. No AWS preparation action, instance start, deployment, smoke,
or science occurred.

The original NOT_READY checkpoint below is retained as historical diagnosis;
it is not the current recovery disposition.

## Historical checkpoint: NOT_READY — independent review NOT APPROVED

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

`ARTIFACT_VERSION_SET` is reconstructed from the frozen R26–R30 reads under a
stricter one-page, sixteen-item local implementation bound. R26 and R27 must
enumerate exactly the same eight current versioned objects under the sealed
prefix; R28 is not called because every accepted read is version-pinned. Each
R29 exact-version body is fully consumed into a versioned content binding whose
byte count and SHA-256 must equal the R29 checksum and independent R30 object-
attributes checksum. Large bodies are never embedded in JSON. The output/v1
schema, actions, permissions, scientific content, cost ceiling and publication
scope are unchanged.

The dependent progress/v5 and source attachment/v4 append the artifact output
after the six earlier candidates while retaining the frozen eleven-control
order. Sealed context/v4 adds only the artifact prefix and S3 list bounds, and
attachment/v4 recomputes the exact six-control attachment/v3 predecessor.
Seven source-bound predeployment controls leave four unresolved controls and
still cannot make a complete-set or readiness claim.

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

### Prospective live carrier v7 correction

The later explicit user authority to repair every necessary AWS-C0 stage
authorizes a prospective carrier correction without changing historical
schemas. `aws_c0_live_packet/v6` and `aws_c0_live_authorization/v6` remain
unchanged and continue to document the earlier impossible requirement for a
complete eleven-control reconstruction before CloudFormation created all of
those resources.

`aws_c0_live_packet/v7` instead binds the exact
`aws_c0_runtime_control_read_plan/v3` and embeds the source-revalidated
`aws_c0_runtime_control_reconstruction_source_attachment/v5`. That attachment
contains the eight controls whose authenticated API sources can be consumed
before deployment. The packet still carries all nine predeployment semantic
preimages, including the already published software-and-image material, and
the existing postdeployment software/image drift comparison remains mandatory.
`aws_c0_live_authorization/v7` still carries all eleven postdeployment
preimages and directly repeats the packet's attachment identity.

The v7 packet also binds the change-set reconstruction output and its derived
API/resource effect identities. The historical orphan fields
`runtime_control_reconstruction_set_identity`,
`runtime_control_reconstruction_set`,
`packet_declared_other_material_coordinates`, and
`publication_upgrade_binding` are not reinterpreted or weakened in v6; they
are absent only from the prospective v7 carrier and replaced by the complete
inline source attachment plus its canonical identity. No AWS action,
permission, scientific content, cost boundary, publication authority, or
software drift predicate changes.

### Prospective launch carrier v7 correction

The user's following explicit approval authorizes a prospective
`aws_c0_launch_request/v7` and a local commit. Historical launch/v6 remains
unchanged. Launch/v7 omits ten duplicate proof fields for which the repository
has no production constructor and which neither runtime launch validator ever
consumed. It preserves the exact authority-audit, static-validation, private
infrastructure snapshot, cost model, closure seed, eight artifact receipts,
timeouts, retry count, cleanup path, stopped `t3.small` target, and USD 50
boundary.

The omitted role-context duplicate is replaced downstream by the live-packet/v7
source attachment's exact R02, R03, R13, and R14 reconstruction plus the
explicit authenticated R14 IAM cross-control binding. The publication duplicate
remains represented by the exact authority-audit-v4 and static-validation-v4
identities and object receipts already required in launch. The journal-budget
duplicate remains represented by the exact static-validation-v4 identity and
object already required in launch. This correction removes unsupported claims;
it does not remove their underlying evidence sources or runtime safety gates.

Because the preparation packet prospectively enumerates the exact record kinds
that will exist before execution, launch/v7 also requires a versioned carrier
extension through `aws_c0_preparation_packet/v6`,
`aws_c0_preparation_authorization/v5`, and
`aws_c0_preparation_closure/v6`. Packet/v6 names the prospective launch/v7,
closure/v6, and live-packet/v7 kinds; authorization/v5 binds packet/v6;
launch/v7 binds packet/v6 and authorization/v5; closure/v6 binds all three.
This extension changes no field except those carrier-kind constants and the
already authorized launch/v7 field removals. All packet/v5, authorization/v4,
launch/v6, closure/v5, live-packet/v6, and live-authorization/v6 schemas remain
byte-identical historical definitions.

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

## Authenticated CREATE change-set reconstruction

CloudFormation creates a unique stack ID in `REVIEW_IN_PROGRESS` when it creates
a CREATE change set for a new stack. The predeployment change-set producer must
therefore collect all of R45 through R48; no missing-stack exception or null
receipt is valid. R45 must show the exact named change set as `CREATE_COMPLETE`
and `AVAILABLE`, R46 must return original template bytes matching the sealed
template SHA-256, R47 must show the same stack in `REVIEW_IN_PROGRESS`, and R48
must be a complete terminal same-stack event page.

The producer derives the resource-effect identity from the complete R45 change
list and cross-binds the closed effect-API plan to that derived resource set.
It retains the historical `aws_c0_change_set_effects_observation/v1` output and
R45–R48 source mapping. Its one-page, sixteen-item bounds are explicit and it
adds no action, permission, deployment, publication, cost, or scientific
authority. Construction and tests are pure local operations and do not claim
that any AWS observation has occurred.

Progress/v6 and source-attachment/v5 add this output after the six existing
infrastructure controls and before the exact artifact-version set, preserving
read-plan/v3 and the source-attachment/v4 predecessor. The independently sealed
context/v5 carries the exact change-set ARN, stack name, template hash, effect
API plan, and one-page/sixteen-item CloudFormation bounds. The attachment reruns
all eight producers. It remains `PARTIAL_SOURCE_BOUND_NOT_READY`; Standard
workflow, SSM document, and software/image set are still unresolved.
