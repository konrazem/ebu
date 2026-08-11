# Repository Guidance for Codex

This file applies to the entire repository. Reproducibility and scientific
integrity take priority over speed.

## Project purpose and source of truth

- EBU is a scientific research repository.
- The committed repository, Git history, frozen protocols and JSON plans,
  disposition documents, manifests, and implementation are authoritative.
- Chat history and remembered summaries are not authoritative scientific
  records. Reconstruct each task's state from Git and committed documents.

## Gate 1D-C authoritative operational sources

- `V3.0_GATE1D_C_EXECUTION_FINALIZATION_ADDENDUM.md` and
  `v30_gate1dc_execution_finalization_contract.json` are the authoritative
  prospective operational sources for Gate 1D-C execution durability,
  publication, recovery, finalization, and result-commit mechanics.
- Their precedence is deliberately narrow. They supersede only the Gate 1D-C
  protocol's original execution command and incomplete operational
  finalization mechanics where the addendum and contract say so explicitly.
  They do not change or reinterpret any scientific content.
- `V3.0_GATE1D_C_OUTCOME_DISCRIMINATION_PROTOCOL.md` and
  `v30_gate1dc_outcome_discrimination_plan.json` retain precedence over every
  hypothesis, parameter, comparison, metric, threshold, tolerance, predicate,
  falsifier, positive control, outcome class, interpretation rule, limitation,
  and non-claim. Any scientific conflict requires fail-closed refusal.
- `V3.0_GATE1D_C_MACOS_ENVIRONMENT_COMPATIBILITY_ADDENDUM.md` and
  `v30_gate1dc_macos_environment_compatibility_contract.json` are the
  authoritative prospective sources for the Gate 1D-C macOS process-entry
  environment and its immediate normalization. Their precedence is limited to
  the explicitly superseded environment entry, normalization, official
  invocations, source-provenance inventory, and dependent manifest-provenance
  rows. They change no scientific content or other operational mechanic.
- The execution/finalization addendum and contract retain precedence over every
  operational rule outside that narrow compatibility scope, including all
  state, receipt durability, retry, publication, failure, finalization, and
  result-commit mechanics. Any conflict outside the narrow scope requires
  fail-closed refusal.
- Each Markdown addendum and its corresponding JSON contract must agree. The
  applicable JSON is the mechanical schema and ordering source; its Markdown
  counterpart is the normative human rendering. Any mismatch is an integrity
  failure, not permission to choose one selectively.

## Required start-of-task checks

- Read every applicable `AGENTS.md` before acting.
- Inspect the working tree, branch, local HEAD, intended remote HEAD, and recent
  history before editing.
- Identify the authorized gate and stage from the request and committed record.
- Read the complete protocol, plan, disposition, and implementation sources
  relevant to that stage.
- Stop on an unexpected dirty tree, branch or hash mismatch, or unexplained
  artifact. Never delete, revert, stash, or overwrite unexplained user work.

## Authorization boundaries

- Work only on the explicitly authorized gate and stage. Do not automatically
  continue to a later stage.
- Treat analytical design, preregistration, implementation, pre-execution
  validation, execution, interpretation, and publication as separate
  authorization boundaries.
- Later-stage files do not authorize later-stage work. If scope is ambiguous or
  must expand, stop and ask.

## Scientific integrity

- Preregister hypotheses, parameters, comparisons, metrics, falsifiers, and
  interpretation rules before execution.
- Never alter a frozen preregistration to make implementation or results pass.
- Never tune parameters, worlds, tolerances, classifications, or hypotheses
  after inspecting candidate outcomes unless a separate protocol explicitly
  authorizes it.
- Keep scientifically open comparisons open; do not optimize the design or
  implementation to make EBU win.
- Distinguish mathematical guarantees, implementation tests, and empirical
  findings. Preserve information boundaries and prevent future-data or result
  leakage.
- Treat committed result artifacts and manifests as immutable unless an
  explicit correction stage is authorized.

## Execution safety

- Before any command that might advance model state, determine whether the
  authorized stage permits execution.
- When execution is forbidden, do not call step functions, runners,
  simulations, or trajectories, even for one tick, and do not disguise an
  experiment as a unit test.
- For static-only validation, restrict work to inspection, algebra, arithmetic,
  strict parsing, hashing, schemas, and isolated pure-function checks on frozen
  or synthetic individual states.
- Do not run parameter searches, optimizations, or outcome-inspecting
  experiments without explicit authorization.
- Preserve enough command and validation evidence to establish what did and
  did not execute.

## Implementation discipline

- Prefer the smallest faithful change set. Preserve architecture and semantics
  unless the authorized task explicitly changes them.
- Avoid unrelated refactoring, formatting churn, and new dependencies.
- Implement frozen plans exactly, including deterministic seeds, ordering,
  tie-breaking, tolerances, schemas, and filenames.
- Fail closed on preregistration hash, configuration, schema, or invariant
  mismatches.
- Never silently weaken a guarantee or replace a mathematical requirement with
  an empirical assumption.

## Testing and validation

- Run only tests permitted by the current stage.
- Validate relevant hashes, schemas, constants, deterministic ordering, and
  protocol-to-implementation consistency.
- Inspect the complete diff, run `git diff --check`, and confirm the changed
  files exactly match the authorized scope.
- If validation reveals a scientific incompatibility, stop rather than changing
  foundational semantics to force a pass.

## Git discipline

- Preserve unrelated changes and avoid destructive Git operations.
- Commit and push only when explicitly authorized.
- Before committing, stage exact reviewed paths and inspect the staged filename
  list and complete diff.
- After pushing, verify local HEAD equals the intended remote branch and the
  working tree is clean.
- Never rewrite published history without explicit authorization.

## Completion reports

For every completed stage, report:

- starting and final SHAs;
- exact changed files and their purpose;
- validation and tests performed;
- whether any model state or scientific experiment executed;
- applicable hashes or manifests;
- commit and push status;
- limitations, blockers, and unresolved scientific questions; and
- the next possible stage, clearly identified as not begun.

## Stability

- Keep this guidance durable across gates. Do not record a current branch,
  HEAD, gate, plan hash, experimental conclusion, temporary filename, date,
  progress summary, or other one-time task state here; those belong in
  committed scientific documents and task prompts.

## Communication

- Communicate in English unless the user explicitly requests another language.
- Lead with the result and explain scientific terminology plainly.
- Never claim verification passed when checks terminated, were skipped, or
  produced no completed findings.
