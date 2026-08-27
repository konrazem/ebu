---
name: ebu-framework
description: Reconstruct and carry out an explicitly invoked EBU framework stage with authority-scoped checks and proportionate validation. Use only when the user invokes $ebu-framework; do not use for book or unrelated repository work.
---

# EBU Framework

Use this workflow only when the user explicitly invokes `$ebu-framework`.

## Establish the task boundary

1. Identify the requested framework stage and select exactly one primary
   profile from [references/profiles.md](references/profiles.md). Read that
   profile before acting.
2. Separate orientation, authority drafting, authority audit, implementation,
   candidate audit, integration, and scientific execution. Do not treat one as
   permission for another.
3. Resolve an ambiguity before acting when different answers would change the
   authority set, permitted files, validation class, or external effect.

## Reconstruct the current state

1. Establish the repository root, worktree state, branch, `HEAD`, relevant base
   and target refs, and recent stage history. Check a live remote only when the
   request or applicable authority requires live identity.
2. Locate current stage status and authority from committed Git history and the
   applicable specification, plan, amendments, contracts, dispositions, and
   accepted implementation evidence. Do not use chat summaries as authority.
3. Read only the current authority and implementation sections needed for the
   requested stage. When a normative Markdown document and mechanical contract
   govern the same material, check both and fail closed on disagreement.
4. Distinguish active authority from historical locks, superseded values, later
   proposals, and files whose presence does not grant permission.

## Control scope and validation

1. Record the exact authorized paths and base revision before editing. When
   those are known, run `scripts/check_git_scope.py` before handoff and whenever
   scope drift is suspected.
2. Use only validation authorized for the selected profile. Static inspection,
   strict parsing, hashing, schema checks, AST checks, and explicitly permitted
   pure or synthetic checks do not by themselves authorize a scientific run.
3. Treat any model-state advance, scientific callback, policy invocation,
   runner, trajectory, candidate-outcome inspection, or Gate operation as
   scientific execution unless the committed authority explicitly classifies
   and permits that exact operation.
4. Fail closed on a genuine repository-identity, authority, scientific,
   invariant, or path-scope discrepancy. Do not change frozen requirements to
   make a candidate pass.
5. Stop at the requested stage. Identify a later possible stage as not begun
   rather than starting it automatically.

Report the result, evidence checked, exact changes or read-only scope,
validation completed, whether any scientific behavior executed, unresolved
issues, and repository operations actually performed.
