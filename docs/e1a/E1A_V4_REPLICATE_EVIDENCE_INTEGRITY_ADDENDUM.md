# E1a v4 replicate evidence integrity addendum

This addendum records the repair of two record-integrity gaps found after the
replicate decision composition report, and the subsequent preflight probe for
C8. It changes no endpoint, factor, threshold, denominator, or scientific
decision. It does not authorise execution.

## Scope and provenance

The earlier report, `E1A_V4_REPLICATE_DECISION_COMPOSITION_REPORT.md`, describes
the state at work commit `1f5ae3821298282f8ea4ce3c030eb1a16025b736` and
report commit `364e5d9ed91fa6dc2051118db7b37ae43fbc8c31`. Its statement
that C8 composition is checked only when factor branches happen to be present
is superseded for C8 by work commit
`0338a76c2a03a5b2041ca9ea9a3a4b7869daf71d`. Its 3,643-check table remains
a historical result for that earlier tree, not the count for the current code.

The work commit is the current `gaussian/stage-a-environment` HEAD. The
preflight change and this addendum are uncommitted and unpushed. The tracked
working tree was clean before the preflight change.

## C8 factor evidence is required

Before `0338a76`, a C8 record could claim `scale_recovered=True` with only a
passing `1.07` branch, or with one failed branch and a second branch lacking a
`p3_passed` decision. The generic composition check skipped malformed or absent
branch evidence. Endpoint validation accepted those records, and direct
aggregation counted a C8 success.

The repaired endpoint validator reads the paired factors from C8's single
frozen plan subcondition. It requires the exact branch keys, the ordered
`scale_factors` list, each branch's matching `c`, and a strict Boolean
`p3_passed` for each factor. It then requires `scale_recovered` to equal the
conjunction of those decisions. C8's declared factors remain `1.07` and `0.90`;
the producer and release rule are unchanged. Valid two-branch successes and
failures still pass. Malformed evidence refuses as
`TERMINAL_RECORD_INCONSISTENT` in validation and aggregation.

## C1 counts require the full field roster

Before `0338a76`, direct `campaign_counts_from_records` could count a C1
success from one field record while the other three planned fields were absent.
`replicate_outcomes` now checks each replicate's exact field roster from the
frozen plan before deriving `p1_all` and `complete_pass`. A missing, extra, or
duplicated field refuses as `RESULT_FIELD_SET_MISMATCH`. The official campaign
orchestration already had a separate job-completeness check; this closes the
direct counter's gap.

## Preflight now probes the C8 rule

`release_authority.require_per_field_implementation_conformance` now calls the
same pure `scale_recovery_failure` function with C8's factors from the plan. It
accepts a complete paired success and a correctly recorded paired failure. It
refuses absent or malformed branches, an absent factor, an invalid branch
decision, a wrong factor list or label, and a recovery claim that contradicts a
failed factor. A malformed plan factor produces the coded
`IMPLEMENTATION_AUTHORITY_LAG` refusal instead of an uncaught conversion error.

The release-authority tests replace this function with four weakened variants:
a rule that checks nothing, one that checks only supplied branches, one that
checks only factor keys, and one that refuses valid evidence. Conformance
rejects each variant. A separate check confirms that the full static preflight
also rejects the rule that checks nothing. Runtime tests exercise the driver's
call site; preflight probes the pure rule without importing or executing the
campaign driver.

## Verification and execution boundary

One coherent run of the fifteen permitted static and pure suites completed
with **3,665 checks, 0 failures, and 0 unclean suites**:

| Suite | Checks |
|---|---:|
| `test_e1a_v4_release_authority.py` | 1,237 |
| `test_e1a_v4_driver_endpoints.py` | 626 |
| `test_e1a_v4_terminal_calibration.py` | 538 |
| `test_e1a_v4_coherence_hardening.py` | 138 |
| `test_e1a_v4_size_semantics.py` | 138 |
| `test_e1a_v4_repair.py` | 126 |
| `test_e1a_v4.py` | 122 |
| `test_e1a_v4_case_scope.py` | 114 |
| `test_e1a_v4_generating_model.py` | 113 |
| `test_e1a_v4_plan_coherence.py` | 113 |
| `test_e1a_v4_calibration_scope.py` | 105 |
| `test_e1a_v4_preexec.py` | 104 |
| `test_e1a_v4_contract_plan.py` | 75 |
| `test_e1a_v4_dispositions.py` | 64 |
| `test_e1a_v4_preexec_corrections.py` | 52 |
| **Total** | **3,665** |

Every suite exited successfully and printed exactly one parseable completion
summary; the total excludes no crashed or incomplete suite. `git diff --check`
passes, and a separate canonical full preflight passes with this addendum
present. The eight authority sources listed in the previous report remain
byte-identical. The analysis procedure identity remains
`dd2ed732db4348b0b25ce5fe83096d38f5b9c1748ee5916eecaf2c1aef2e2e1f`.
The execution identity moved from the committed repair's
`ea2df04669f0ea7ec96fba9a5a88e8df516bf5b62677c91209212b9e96302c9c`
to `92a28e450ef8ed00c6eba72ca638c180c6d3ceaadf433c7a43b394f93aad89d1`
because `release_authority.py` changed. It is not frozen.

No scientific random draw, model trajectory, calibration execution, or official
campaign job ran. The execution seal remains `PRE_DRIVER` with authorisation
false. The trajectory-bearing `test_e1a_v4_campaign_driver.py` remains deferred.
F2–F8 remain open. Independent re-audit is the next stage and has not begun.

## What this does NOT establish

**`F7 — Remaining C8 implementation inputs` remains OPEN.** The exact claim here
is narrow: the C8 factor-evidence requirement *that the frozen plan already
declares* is now checked by preflight and by both the endpoint validator and the
counter. That is record integrity against existing authority. It is not a finding
that every remaining C8 implementation input is scientifically specified, and
nothing in this addendum closes F7 or any other open F-stage item.
