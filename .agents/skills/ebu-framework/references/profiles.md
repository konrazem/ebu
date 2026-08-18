# EBU Framework Profiles

Select one primary profile from the user's requested stage. Add a secondary
profile only when the request explicitly combines their permissions. More
advanced repository state does not expand the selected profile.

## Orientation or status review

**Expected inputs**

- The repository or worktree and the status question.
- A stage, branch, commit, or authority hint when the question is narrower than
  the full framework.

**Permitted scope**

- Read Git metadata, committed authority, accepted evidence, implementation,
  and relevant diffs.
- Perform non-mutating local checks; query live refs only when current remote
  identity is part of the question.

**Minimum checks**

- Establish the worktree state, branch, `HEAD`, relevant upstream or target,
  and recent history.
- Locate the current stage declaration and distinguish accepted, candidate,
  planned, blocked, and unstarted work.
- Corroborate status with the applicable authority and accepted Git record.

**Prohibited operations**

- Do not edit, stage, commit, integrate, or publish.
- Do not run framework behavior, scientific tests, models, or Gates.
- Do not infer authority to begin the next stage.

**Expected output or report**

- Give the current status with commit and document evidence, discrepancies and
  limitations, and the next possible stage explicitly marked as not begun.

## Authority drafting

**Expected inputs**

- The exact proposed stage and authority deliverables.
- Current governing sources, accepted predecessor evidence, base identity, and
  authorized paths.

**Permitted scope**

- Create or edit only the named prospective authority, contract, plan, or
  disposition files.
- Use static parsing, hashing, schema, ordering, arithmetic, and consistency
  checks that do not import or execute production framework behavior.

**Minimum checks**

- Reconcile current normative and mechanical authority plus predecessor status.
- Freeze scope, inputs, parameters, ordering, schemas, validation classes,
  acceptance predicates, falsifiers, nonclaims, and later-stage exclusions to
  the degree required by the proposed stage.
- Make each supersession narrow and explicit; keep Markdown and matching JSON
  mechanically consistent.
- Check the exact diff and authorized path set with the scope utility.

**Prohibited operations**

- Do not modify implementation, tests, fixtures, results, or manuscripts unless
  separately named in the authority-drafting request.
- Do not execute a candidate, framework behavior, model, trajectory, or Gate.
- Do not self-accept, integrate, or begin implementation.

**Expected output or report**

- Provide the draft authority set, hashes or identities actually established,
  completed static checks, open questions, and the independent authority audit
  as a possible later stage not begun.

## Independent authority audit

**Expected inputs**

- The candidate authority commit or exact file set, its base, governing
  predecessor authority, and stated acceptance criteria.

**Permitted scope**

- Review the candidate read-only and create a report only if that report is an
  explicitly authorized deliverable.
- Independently parse and recompute static evidence with methods that do not
  rely only on the candidate's assertions.

**Minimum checks**

- Inspect the complete candidate diff and confirm its path boundary.
- Check normative/mechanical agreement, hashes, schemas, closed inventories,
  orderings, arithmetic, permissions, nonclaims, and supersession boundaries
  relevant to the stage.
- Verify that the candidate neither rewrites accepted history nor grants an
  unstated later-stage permission.
- List every acceptance criterion as passed, failed, or not completed.

**Prohibited operations**

- Do not repair the candidate during an independent audit.
- Do not run production framework code, scientific tests, models, or Gates.
- Do not accept, integrate, or publish unless separately authorized.

**Expected output or report**

- Lead with findings ordered by severity, cite exact evidence, give a clear
  audit disposition, and state every incomplete check without calling it a
  pass.

## Framework implementation

**Expected inputs**

- Explicit implementation authority for one stage or substage.
- The accepted authority identities, predecessor evidence, exact base, closed
  path manifest, interfaces, and authorized validation groups.

**Permitted scope**

- Change only implementation, fixture, test, or packaging paths assigned to the
  authorized stage.
- Run only the exact static or synthetic validation classes authorized for that
  stage.

**Minimum checks**

- Verify repository identity, predecessor acceptance, current authority hashes,
  and the clean starting scope before editing.
- Implement frozen fields, ordering, projections, failures, tolerances,
  fixtures, imports, exports, and path ownership exactly.
- Inspect the complete diff, run the authorized validation with nonzero check
  counts, and use the scope utility against the authorized base and paths.
- Confirm accepted predecessor bytes and APIs remain unchanged where required.

**Prohibited operations**

- Do not edit authority to fit implementation or expand the file manifest.
- Do not enter another implementation stage or integration profile.
- Do not invoke a scientific callback, policy, state transition, runner,
  trajectory, outcome inspection, or Gate unless separately authorized as
  scientific execution.

**Expected output or report**

- Report the starting and final identities, exact files and purpose, validation
  commands and counts, scope result, whether scientific behavior executed, and
  the independent candidate audit as not begun.

## Independent candidate audit

**Expected inputs**

- The implementation candidate commit or range, exact base, accepted authority
  set, path manifest, public contract, and authorized audit checks.

**Permitted scope**

- Inspect the candidate, its complete diff, and permitted static or synthetic
  checks without modifying it.
- Write an audit report only when explicitly authorized.

**Minimum checks**

- Verify commit identity, path ownership, authority locks, predecessor
  preservation, imports, exports, projections, failure precedence, fixtures,
  and relevant invariants.
- Run only audit groups expressly authorized for this candidate and confirm
  completed nonzero counts.
- Use the scope utility and independently compare claimed evidence with actual
  files and command results.

**Prohibited operations**

- Do not fix or reformat the candidate during the audit.
- Do not substitute broader tests for missing authorization.
- Do not integrate, execute science, interpret results, or publish.

**Expected output or report**

- Lead with actionable findings and precise locations, then give the audit
  disposition, completed and omitted checks, scientific-execution statement,
  and limitations.

## Integration

**Expected inputs**

- Explicit integration authority naming the accepted candidate, target branch,
  expected base or parentage, permitted Git operations, and any required remote
  identity.

**Permitted scope**

- Perform only the named merge, fast-forward, cherry-pick, commit, or push.
- Resolve a conflict only when the accepted authority determines the exact
  result; otherwise stop for renewed review.

**Minimum checks**

- Verify candidate acceptance, local and required live identities, clean
  worktree, ancestry, and exact candidate diff before integration.
- Confirm the integrated tree has the accepted content and no additional path
  changes.
- Run only authorized post-integration checks and verify the resulting commit
  and remote ref when a push is authorized.

**Prohibited operations**

- Do not add new authority or implementation while integrating.
- Do not force-push, rewrite history, tag, release, or publish unless each
  operation is explicit.
- Do not begin a later framework or scientific stage.

**Expected output or report**

- Report starting, candidate, and final identities; parentage; exact integrated
  files; validation; commit and push status; and any later stage as not begun.

## Separately authorized scientific execution

**Expected inputs**

- Explicit execution authority and the exact frozen protocol, mechanical plan,
  configuration, execution binding, implementation, environment, invocation,
  identity checks, output locations, and retry or recovery rules.

**Permitted scope**

- Perform only the invocation count, execution, receipt, durability,
  finalization, or publication mechanics expressly granted by those sources.
- Apply operational compatibility or recovery rules only within their declared
  precedence and scope.

**Minimum checks**

- Verify every required repository, authority, source, environment, launcher,
  configuration, binding, destination, and pre-execution identity before model
  entry.
- Confirm that normative and mechanical sources agree and that the exact
  invocation is prospective, frozen, and still authorized.
- Preserve receipts and artifacts exactly, honor fail-closed and stopping
  rules, and record whether model state advanced.

**Prohibited operations**

- Do not tune parameters, worlds, seeds, tolerances, classifications, or
  hypotheses after observing candidate outcomes.
- Do not retry, recover, finalize, interpret, publish, correct, or commit beyond
  what the applicable authority explicitly permits.
- Do not treat execution authority as interpretation or later-stage authority.

**Expected output or report**

- Report the exact invocation and identities, durable receipt or failure state,
  artifacts created, state advancement, retries actually used, validation
  completed, and the separately authorized next stage as not begun.
