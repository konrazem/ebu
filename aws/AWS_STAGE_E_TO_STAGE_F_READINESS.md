# Stage E to AWS Stage F readiness

Status: **readiness record; no execution authorization**

## Verified repository state

- Current AWS branch base:
  `a4af44afd3c878311ee373bc19e3be14b2aacec5`
- Accepted Stage E integration:
  `c43ead831c3e4021405985134ed564b761bb1aed`
- Accepted Stage E tree:
  `212777d569af527ce9532ea6c836ff2225465d87`
- Stage E GitHub Actions run: `33231168021`
- Retained Stage E artifact ID: `9708926559`
- Retained Stage E artifact SHA-256:
  `2b2b5cc213082392bda715e82b9a23f670b7628b92848ace9455724f903bc345`
- Stage E record explicitly states
  `stage_f_execution_authorized=false`.

Stage E implementation was integrated and its exact integration commit passed
the Stage E, framework, packaging and conventional CI lanes. Stage E therefore
does not need to be re-run scientifically; it created no scientific outcome.

## Current-line blocker

At current integrated commit `a4af44a`, GitHub Actions run `33416849135` has
successful conventional/framework/packaging lanes but a failed
`stage-e-scientific-harness` lane. The refusal is an exact implementation-path
closure mismatch: the current line contains prospective Stage F authority and
reachability paths that the accepted Stage E implementation closure does not
accept.

This is not evidence that the accepted Stage E run failed retroactively. It is
evidence that the later integrated line is not currently a clean Stage E
validation target. The validator must not be weakened or given a broad `aws/**`
exception. A separate prospective authority/reachability stage must accept the
exact additional paths.

## Why the existing Stage F binding cannot run on AWS

The integrated Stage F local execution-binding authority is explicitly bound
to a local Windows host, NTFS/USN evidence and Docker Desktop behavior. An
Ubuntu EC2 or AWS Batch worker cannot produce those host guarantees. The fact
that the OCI image is Linux/amd64 does not make the host binding portable.

Current Stage F records are prospective authority/reachability records. The
required `stage_f_binding/` implementation and an accepted AWS binding do not
exist at this branch base. No scientific launch is authorized.

## Required path before a real AWS experiment

1. Preserve accepted Stage E commit/evidence identities.
2. Decide and independently audit the correct base for a parallel AWS binding;
   do not silently reinterpret the Windows binding.
3. Create an AWS/Linux/Step Functions/AWS Batch execution-binding authority
   candidate with an exact path manifest, schema, predecessor identities and
   validation contract.
4. Integrate that authority only after independent PASS.
5. Implement and audit the exact AWS binding/reachability closure.
6. Complete non-scientific Step Functions/Batch, checkpoint, interruption, IAM
   and scale-to-zero rehearsals.
7. Build the scientific image and bind it by ECR digest.
8. Produce the complete human-readable Stage F campaign packet required by
   Stage E, including counts, measured throughput, duration, memory, storage,
   checkpoints, controls, falsifiers and cost.
9. Ask the user for one new explicit authorization for that exact packet.
10. Only then start the scientific Standard workflow that submits the Batch
    job.

## What can proceed on this branch

- record the completed infrastructure rehearsal;
- provide read-only result retrieval and checksum verification;
- design AWS architecture and cost/recovery controls;
- create non-executable templates with authorization set to false;
- run syntax, JSON, hash and other static tests of these operations files.

Scientific image construction, registered campaign execution, outcome
inspection, retry of a consumed attempt, interpretation and publication remain
outside this branch.
