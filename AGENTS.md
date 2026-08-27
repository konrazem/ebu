# Repository Guidance for Codex

This file applies to the entire repository. EBU is a scientific research
project, so reproducibility and scientific integrity take priority over speed.

## Source and scope

- Treat committed Git records and the authority documents applicable to the
  active task as authoritative. Chat history and remembered summaries are not
  scientific records.
- Preserve unrelated user work. Stop on unexplained repository changes or a
  genuine identity, authority, scientific, or scope discrepancy.
- Stay within the explicitly authorized stage. Do not automatically proceed to
  a later stage.
- Keep scientific design, implementation, validation, execution,
  interpretation, and publication as separate authorization boundaries.

## Scientific and validation boundaries

- Never execute a model, simulation, trajectory, runner, Gate, or other
  scientific behavior without explicit authorization for that execution.
- Use validation proportionate to the active task and permitted by its current
  authority.
- Never weaken, reinterpret, or tune a frozen scientific requirement to obtain
  a passing implementation, validation, or result.
- Report incomplete, skipped, terminated, zero-check, or failed validation
  truthfully; none is a pass.

## Repository operations

- Preserve unrelated changes and avoid destructive Git operations.
- Commit, push, merge, tag, release, publish, or rewrite history only when the
  user explicitly authorizes that operation.

## Skill routing

- When a task explicitly invokes `$ebu-framework` or `$ebu-books`, follow that
  skill.
- Do not load either specialized workflow for unrelated tasks.

## Communication

- Communicate clearly in English unless the user requests another language.
- Lead with the result and distinguish verified facts, limitations, and work
  that has not begun.
