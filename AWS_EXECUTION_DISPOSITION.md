# AWS execution disposition for the homeostasis mission

**Status: blocking finding, with the local half of the equivalence gate
completed.**

**No AWS API call, SSO call, console action, resource creation, upload,
download or spend occurred in producing this document.** The only local checks
performed were the presence of the AWS CLI binary (`aws-cli/2.36.36`) and the
existence of `~/.aws/config` as a file. No credential, profile or account
identifier was read, and no endpoint was contacted.

---

## 1. What mission section 20 assumes, and what is actually there

Section 20 states that *"the project previously invested in AWS execution
infrastructure"* and that this is the stage to reactivate it. That premise is
half true, and the half that is false is the blocking half.

**What exists.** One completed **non-scientific infrastructure rehearsal**,
dated 2026-09-01, recorded on the branch `aws/campaign-orchestration` (tip
`df7e844`). It verified: an Ubuntu 24.04 `t3.small` EC2 instance with an
encrypted root volume, IMDSv2 required and no inbound rules; Docker installed
and `hello-world` passing; an empty immutable ECR repository readable under an
assumed role; and a synthetic text file uploaded to S3 with a retained version
ID and SHA-256 verified from three separate downloads, including one after the
instance stopped.

That is a real and useful result. It establishes that an instance can be
launched, can authenticate, and can write a durable verified object.

**What does not exist.**

1. **No EBU scientific code has ever executed on AWS.** The rehearsal's
   durable object is `synthetic-result.txt`. The rehearsal record states
   plainly: *"No EBU scientific configuration, runner, trajectory,
   model-state advancement, registered campaign or outcome inspection
   occurred."*
2. **No execution binding exists for this programme's code.** The integrated
   Stage-F local binding is, in its own authority's words, *"explicitly bound
   to a local Windows host, NTFS/USN evidence and Docker Desktop behavior"*,
   and `AWS_STAGE_E_TO_STAGE_F_READINESS.md` records that *"an Ubuntu EC2 or
   AWS Batch worker cannot produce those host guarantees."* There is no
   binding for `gaussian_harness` or `homeostasis` on any host.
3. **The intended backend is a design, not an implementation.** Step Functions
   Standard plus AWS Batch on managed On-Demand EC2 is described in
   `aws/README.md` as what *"the intended operational backend"* would be. No
   state machine, job definition, queue, compute environment, container image
   or job manifest exists.
4. **None of it is on this line of development.** The `aws/` directory is not
   present at HEAD. Its branch carries an explicit instruction against merging:
   *"Do not merge this branch or weaken that validator merely to make these
   files pass. A separate AWS operational authority/reachability stage must
   prospectively accept the exact AWS path set."*
5. **The required path is ten steps, none completed.**
   `AWS_STAGE_E_TO_STAGE_F_READINESS.md` enumerates them, from auditing a base
   for a parallel AWS binding through building and digest-pinning a scientific
   image to *"one new explicit authorization for that exact packet."* The
   Gaussian programme has completed none, and those steps are written for the
   framework/Stage-F lineage rather than for this code at all.

## 2. Why the equivalence gate cannot be run

Mission section 21 requires each of at least two frozen rehearsal
configurations to be run *"once locally; once through the AWS execution path"*
and the canonical scientific payloads compared.

**There is no AWS execution path for this code.** The gate is not failing; one
of its two sides does not exist. Constructing it is the ten-step programme
above, not a step inside this task.

This meets mission section 33's stop condition for AWS. It is reported rather
than worked around: nothing here merges the operations branch, weakens the
reachability validator, or launches an instance on the strength of a rehearsal
that ran different code.

## 3. What was completed instead: the local half of the gate

The substantive content of section 21 is not "a cloud ran it" but *"identical
code identity, config identity, seed identity, canonical physical trajectory,
EBU values, choices, receipts, accounting, and final artifact hash"*, with
environment metadata separated from the scientific payload. All of that is
host-independent, and it is now implemented and proven locally in
`homeostasis/jobs.py`.

**Job identity (section 22).** `JobIdentity` carries the preregistration id,
configuration identity, code identity, load, policy, menu rule, replicate,
horizon and both seeds. `job_id` is the SHA-256 of a separator-guarded ASCII
preimage over exactly those fields.

**Canonical payload versus envelope (section 21).** The payload holds
scientific content only. `ExecutionEnvelope` — executor, attempt, start time,
host — sits structurally beside the payload and outside its hash, so a cloud
artifact and a local artifact of the same identity are comparable byte for byte
on the part that matters.

**Proven properties**, asserted by the conformance suite rather than claimed:

- the payload hash is a pure function of the job identity;
- re-running the same identity yields an identical hash — retries are
  idempotent, so section 27's "rerun the exact same immutable job identity" is
  safe by construction;
- running jobs in a different order changes nothing, so scheduling order cannot
  influence results;
- a different envelope — different executor, attempt, host and start time —
  changes nothing;
- no wall clock, environment variable, process identifier or host name is
  reachable from a job's execution path;
- `manifest()` reports duplicate identities carrying *different* payload
  hashes as an integrity conflict rather than merging them.

When an AWS execution path is eventually built, the gate reduces to running
these same identities there and comparing `payload_sha256`. The local side is
finished.

## 4. What would have to happen before registered AWS execution

In dependency order, and none of it authorized by this task:

1. An AWS/Linux execution-binding authority candidate for **this** code, with
   an exact path manifest, schema, predecessor identities and validation
   contract — the existing Windows binding must not be silently reinterpreted.
2. Independent PASS and integration of that authority.
3. Implementation and audit of the binding and its reachability closure,
   including a prospective decision on the `aws/**` path set that the current
   validator rejects.
4. Non-scientific Step Functions, Batch, checkpoint, interruption, IAM and
   scale-to-zero rehearsals.
5. A scientific container image, pinned by ECR digest.
6. The host-speed measurement `S` that `V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md`
   section 7 specifies, before any dollar ceiling is defensible.
7. The complete human-readable campaign packet: counts, throughput, duration,
   memory, storage, checkpoints, controls, falsifiers and cost.
8. One new explicit author authorization for that exact packet.

## 5. Recommendation

**Run the registered study locally.** The mission's own cost reasoning already
points this way: `V3.0_LONG_HORIZON_COST_AND_LAUNCH_PLAN.md` section 5 concluded
that the medium-horizon study *"is not a compute problem and does not need
AWS"*, and section 20 of the mission itself says AWS is for *"parallel
registered replication"*, not for changing scientific semantics.

Measured on this machine by the rehearsal itself — 393,216 ticks in 493
seconds, **1.25 ms per tick** — the full section 23 matrix (4 policies, 3
loads, 64 replicates, 8192 ticks, 6,291,456 arm-ticks) is roughly **2.2 hours
of single-threaded CPU**, and trivially parallel across independent jobs.
Adding the menu-rule factor of `NET_ZERO_GROUPS_FINDING.md` doubles it to about
4.4 hours. That is an overnight local run, not a cloud programme.

Building an AWS execution binding to save a few hours of laptop time would mean
completing an eight-step authority programme, and would put the first-ever
cloud execution of EBU scientific code on the critical path of a study whose
results do not depend on where it runs.

**Recommended disposition: execute the registered matrix locally; keep the AWS
binding as separate future infrastructure work with its own authorization.**
The job architecture above is deliberately host-agnostic, so nothing is lost:
when the binding exists, the same identities move to it unchanged and the
equivalence gate becomes a hash comparison.
