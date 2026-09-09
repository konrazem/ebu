# ACTC bounded derivation — local static validation

Disposition: **STATIC_DOCUMENT_CONSISTENCY_PASS; PREREGISTRATION INCOMPLETE**.
Base: `dfbc3285781de156f41db86933500cccda95bebf`, tree
`3d9a6d3e476239efb74c23a21d2be90070012879`.
Worktree: `/Users/konrad.grzyb/.codex/worktrees/bb3b/ebu`.

## Scope and reconstruction

The initial worktree was clean and HEAD equaled the requested base commit.
Ancestor AGENTS.md locations were checked; the repository AGENTS.md was read
in full. The complete ACTC authority and companion contract were read. Locked
source sections and JSON declarations relevant to the 25 decisions were
inspected, including the SD-10 declaration solely to verify its scope.
No scientific outcomes were inspected. Git identity matched the base author.

This increment adds exactly:

- [Authority amendment and decision table](ACTC_STATIC_DECISION_DERIVATION_AMENDMENT.md).
- [Standalone static reproduction check](actc_static_decision_derivation_check.py).
- This validation record.

All pre-existing tracked files remain unchanged, including the original ACTC
authority, contract, validation, SD-01 approval, predicates, preparation dossier,
source locks and campaign records. The additive amendment supplements the
historical authority; it does not change any null scientific value or status.

## Checks and review

Reproduce locally from this repository with
`python3 actc_static_decision_derivation_check.py`. The check uses only Python
standard-library document handling and read-only Git commands. It does not
import the framework, a model, a runner or diagnostics, and performs no
scientific calculation or stochastic draw.

The completed check verified the base tree; additive-only path scope; all
14 raw source/SD-01 approval locks against pinned committed bytes, SHA-256 and
byte counts; the two cited base ACTC hashes; strict JSON parsing with duplicate
key/nonfinite rejection; 25 unique ordered IDs and slots; all six table
columns populated; C classification of every complete slot; null/UNRESOLVED
scientific values; the separate A/B partial-binding inventory; local document
links; UTF-8/LF formatting; whitespace; and false execution, sealing and
preregistration flags. The SD-01 readiness gap remains OPEN and no SD-01
scientific binding or execution flag was adopted.

The first check invocation failed because the check expected seven columns
for the six-column decision table. The check and its description were
corrected to six; the completed rerun passed. No scientific declaration or
frozen requirement was changed to obtain that pass.

The author completed one local semantic review against the cited source
sections. The review distinguished complete-slot closure from partial
constraints, verified that no conditional example became an ACTC selection,
and checked that option families remain prospective and non-exhaustive.
Exact source inspection supported PB01 (symbolic equality), PB02 (conditional
existing-v1 size behavior) and PB03 (residual dimensions). The complete added
diff was reviewed before commit.

This is a local author's document review, not an independent audit. The
mechanical check verifies identity and document consistency; it cannot prove
that a scientific choice is unique or validate an adaptive system. Scientific,
numerical, synthetic-control, harness and full repository test suites were
not run and are not reported as passing. No schema for an ACTC runtime was
implemented or validated.

## Disposition and boundary

Whole-slot classification: **A = 0; B = 0; C = 25**. Separately bound conditional
subrequirements: **A = 1; B = 2**. This does not reduce the 25 complete open
slots. The original evidence level and unresolved scientific status remain.

No adaptive-controller implementation, model advance, simulation, outcome
inspection, AWS action, Docker use, data acquisition, external communication,
push, merge or publication occurred. The scoped local commit is authorized.
Its identity and final worktree status are checked after commit; its own SHA
is not embedded recursively in this record.

The remaining decisions and exact next local task are in the amendment.
That task has not begun. No later implementation, validation or execution
stage is authorized by this static pass.
