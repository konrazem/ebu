# ACTC D02/D03/D05 choice packet — static validation

Disposition: **STATIC_DOCUMENT_CONSISTENCY_PASS; AUTHOR CHOICES UNRESOLVED**.
Baseline: `531836aab8cdfd52224408e5768d9c0a19d6988a`.
Baseline tree: `f9d2fecf822a54e4acaa5c8a6242cac47a0a3587`.
Worktree: `/Users/konrad.grzyb/.codex/worktrees/8188/ebu`.

## Scope and reconstruction

The starting worktree was clean and HEAD matched the requested baseline.
Repository and ancestor AGENTS.md locations were checked; the repository
instructions were read in full. Git author name/email matched the baseline
author. The complete ACTC authority, companion contract and static decision
amendment were read, followed by the cited source sections and JSON pointers.
Git history and committed source locks supplied the state, not a remembered
study summary. No scientific outcomes were inspected.

Exactly two documentation files are added:

- [Scientific-choice packet](ACTC_D02_D03_D05_SCIENTIFIC_CHOICE_PACKET.md).
- This validation record.

All pre-existing tracked files remain byte-identical to baseline, including
SD-01, original ACTC declarations and campaign records. No code, runtime schema,
scientific parameter, observation record or result artifact was added.

Branch-scope clarification after review of `6149e33`: the complete four-commit
chain on `codex/actc-choice-packet` (`1e98dac`, `dfbc328`, `531836a`,
`6149e33`) is **static-design material plus a static verifier**, not
documentation-only. The two-file description above applies to the choice-packet
increment. Commit `531836a` introduced
[actc_static_decision_derivation_check.py](actc_static_decision_derivation_check.py),
which is preserved unchanged and permitted only as a static document-consistency
checker. Its checks use standard-library document handling and read-only Git;
its path-scope check covers the original three-file derivation increment.
This clarification grants no scientific, AWS, Docker, model-execution or
outcome-inspection capability or authority, and changes no scientific choice.

## Completed mechanical checks

Checks used only read-only Git operations and Python standard-library text,
JSON and SHA-256 handling, plus Git whitespace checks. No project checker,
model, runner or diagnostic module was imported or executed.

1. Starting commit/tree identity and absence of changes to tracked baseline
   paths were verified. Final changed-path scope contains only the two added
   Markdown files.
2. All nine ACTC source-manifest entries matched their pinned committed bytes,
   recorded byte counts and raw SHA-256 hashes; current bytes also matched.
   Referenced JSON files were strictly parsed with duplicate-key and
   nonfinite-constant rejection. This is syntax/record consistency, not an
   ACTC runtime-schema conformance claim.
3. The original 25 decision IDs remained unique and ordered, their slot names
   unique, and every value null with status UNRESOLVED. Execution authorization,
   preregistration completion and binding-packet sealing flags remained false.
4. Six option tables were checked for exactly their expected unique option
   labels: Q1–Q3, I1–I2, M1–M3, B1–B3, T1–T2, E1–E3. All rows include units,
   consequences and dependencies. Document links resolve, UTF-8/LF formatting
   and trailing whitespace checks pass, and the complete addition was read.
5. Source pointers for D02/D03/D05 and model classes, evidence levels and
   preregistration obligations were checked against parsed committed sources.
   The three controlling documents have the identities below at the baseline.

| File | Raw bytes | SHA-256 |
|---|---:|---|
| `ADAPTIVE_CALIBRATION_AND_TOPOLOGY_CONTROL_AUTHORITY.md` | 19050 | `6c347858e89a91557391b893f6a64573b4fa9fc8e0c07ee9aac0dec8154e71ff` |
| `adaptive_calibration_and_topology_control_contract.json` | 17456 | `546f906a77fedf649dfd5651d3cd5e7fab97588ef0f58d08e1cf01b655b414ef` |
| `ACTC_STATIC_DECISION_DERIVATION_AMENDMENT.md` | 18913 | `a474411e9dcd70eaee411ae53671040af67aca9771e0dcdc4f1e5987acc16c77` |

The initial mechanical pass explicitly deferred the link to this validation
record until its creation; the final pass included it. No failed scientific
check or zero-check scientific run is being presented as a pass.

## Bounded semantic review and limitations

The local author reviewed source-to-option compatibility. Endpoint templates
and interpretation families are clearly marked as new proposals, with no
recommended default or adopted question. Choosing a label alone cannot close
an incomplete declaration. Both required control roles, matched calibration
exposure, common boundaries, budgets and terminal inventories are retained.

The review checked that model forms are not inherited study equations or
adaptive stability proofs; typed structural and physical graphs remain
distinct; interval amounts are not rates; and the three account levels do
not exchange claim strength. PB01 does not choose an empirical zero tolerance,
PB02 does not choose a graph size, and PB03 does not choose a quantity or scale.

Empirical-source options are conditional admission paths, not named datasets
claimed to be available or approved. Source identity and admission criteria
are still required from the author. A pending collection cannot close empirical
availability, and simulated observations cannot substitute for empirical data.
No empirical compatibility, identifiability or intervention effect was tested.

The three requested declarations are explicitly distinguished from full
25-slot preregistration closure and subsequent binding review. No slot was
marked resolved and no packet was sealed. This is a local author's review,
not an independent audit or scientific/numerical validation. Scientific tests,
synthetic controls, simulations, harnesses and full repository tests were not
run and are not reported as passing. No new runtime schema was validated.

## Local completion and next task

The delegated task explicitly requested authorization for local documentation
commits. The first staging attempt was denied because the worktree's Git index
is outside the writable directory; escalated staging then succeeded. The
staged addition and whitespace checks passed.

Automatic approval review rejected the subsequent local commit: it did not
recognize a trusted user message explicitly authorizing the commit and also
flagged disabling repository hooks. Hooks had been disabled in the proposed
command to preserve the static-only execution boundary. The rejected command
did not create a commit; at that point no alternate commit mechanism had been
attempted and the two-file packet remained staged at the unchanged baseline.

Subsequently, the packet was committed normally at
`6149e33ad174ec362c75e6fea1db5a7c43facb87` (`6149e33`), with hooks enabled.
That commit contains both packet files and supersedes the historical pending
commit/approval state above. Git records the committed contents; the normal
hooks-enabled completion is recorded by the coordinating task and explicitly
confirmed in this correction's instruction. No remote equivalence is asserted.

No SD-01 modification, implementation, model advance, stochastic draw,
simulation, Gate/runner execution, outcome inspection, data acquisition,
AWS/Docker use, external communication, push, merge or publication occurred.

This review correction changes only this validation record. Static checks
verify the one-file diff, unchanged checker and scientific declarations, all
14 source/approval byte locks, the 25 null/UNRESOLVED slots, false execution
and sealing flags, document links and whitespace. The original increment's
checker and scientific tests are not run for this correction. The next action
is **independent read-only re-review** of the corrected local commit.

The study author must choose the primary question/endpoint and claim rule,
the system/equations/typed boundary, and the empirical source/admission rules.
The next scientific-design task is the local additive decision receipt specified at the
end of the choice packet, after those author answers arrive. That receipt,
later sealing and every implementation or execution stage have not begun.
