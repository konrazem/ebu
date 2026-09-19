# Introductory chapters 01–07: authoring and source notes

## Scope and repository state

Authoring only, under `EDITORIAL_CONTRACT.md`. Read repository AGENTS in full.
Starting branch: `codex/local-gaussian-reconciliation`.
Starting HEAD: `05f3cb02d0c48e60de98342edfac9c36f2cecc6f`.
No upstream is configured. Existing untracked `books/` is expected parent-task
work and was preserved. This subtask owns only chapters 01–07 and these
introductory source/notes files. No model was imported or executed. No tests
that advance model state, commits, pushes, or scientific runtime edits.

## Editorial work

Read the original Chapter 1 extracted text and the earlier candidate's source
ledger and bibliography. Wrote full chapters following the original patient
teaching pattern: Ridge/Vale/clinic case, careful definitions, practical
distinctions, worked hypothetical arithmetic, common misunderstandings, guided
problems and answers, recap. No manual page breaks, duplicate filler,
historical Allee law, band-hinge penalty or numerical-error controller.

Chapter labels: motivation, money, scarcity, planet, research, homeostasis,
equilibrium. Sources use `intro-` namespaced citation keys. Input
`intro_sources.tex` inside the shared bibliography environment.

The empirical source paragraphs are deliberately short. Most surrounding
teaching prose is original argument or explicitly invented cases; it is not
a long paraphrase of a cited article. No direct quotations from external
sources are used. General ethical positions are identified as commitments.
No new scientific authority, calibration, controller, parameter freeze,
execution permission or institutional settlement rule is introduced.

## Source verification, 19 September 2026

| Key | Verified source and selected claim | Retrieval and scope |
| --- | --- | --- |
| intro-boe | BoE 2014 article: commercial-bank lending can create corresponding deposits; lending is constrained and monetary policy matters. | Official landing page opened successfully. Institutional explanation only, modern UK scope; no quantitative present-year claim. Source-dependent manuscript prose below 110 words. |
| intro-ets | European Commission: cap-and-trade, monitoring/reporting and surrender of allowances for covered emissions. | Official current page opened successfully. Pending 2026 proposal and outcome/price/coverage numbers deliberately omitted. Mechanism passage below 100 words. |
| intro-water | FAO water-scarcity overview distinguishes physical, access and infrastructure scarcity. | Official page opened successfully; no statistics. Attributed passage below 90 words; subsequent clinic cases are original hypothetical examples. |
| intro-health | WHO 2025 social-determinants report overview relates living conditions and resource/power access to health inequities. | Official overview opened successfully; not a full-report replication or causal effect-size claim. Attributed passage below 90 words. |
| intro-ipcc | AR6 SYR SPM A.1.1 and B.1.1: dated observed warming and named scenario estimates, including their stated ranges. | Direct official HTML/PDF retrieval returned 403 during this subtask; official indexed SPM and longer-report passages were retrieved and compared with the earlier candidate's locked passage ledger. All figures remain explicitly dated and conditional. No latest-year claim. Factual chapter prose, including practice answer, is below 200 words. |
| intro-ipbes | 2019 assessment: around one million animal/plant species threatened, not already extinct. | Official Secretariat explanatory-page search result retrieved; direct page access returned 403. Narrow headline only, independently agreeing with earlier candidate's inspected SPM ledger. Attributed passage below 70 words. |
| intro-resources | UNEP/IRP 2024 overview: conditional extraction increase, with declared baseline and horizon. | Official overview opened successfully. Conditional scenario headline only; no fabricated interval. Attributed passage below 90 words. |
| intro-homeostasis | McFarland et al. 2016: organism-level educational framework. | Official publisher indexed abstract/scope passage retrieved; direct DOI/fulltext returned 403 and PMC presented challenge. Narrow conceptual scope, under 100 attributed words; no medical guidance or economic theorem. |

For restricted retrievals, the bibliography identifies the primary source and
this note records the actual retrieval limitation. No claim of full source
audit or replication is made. The original hypothetical tank, household,
valve, garden and waste-container cases supply explanatory depth without
borrowing a source's extended exposition.

## Review checklist completed

- Every chapter starts with the contracted chapter/label format.
- Current-system criticism acknowledges monetary functions and existing
  environmental institutions; it does not claim money has no relation to life.
- Scarcity, access and exposure are distinguished; no one-number welfare claim.
- Environmental figures retain assessment vintage, baseline, period and
  conditional wording; no planetary projection is presented as an EBU result.
- Homeostasis is not identified with a Gaussian probability distribution or
  the dynamics of an undeclared controller.
- Reference, fixed point, steady flow and stability are distinguished.
- Physical totals of 20 and compatible references are arithmetically consistent.
- Gaussian scale is not silently measurement uncertainty.
- Permission, valuation, action selection and institutional rights remain
  distinct; no one-action-per-micro-step restriction is introduced.
- All examples and exercises are illustrative; no simulated observations.

## Local authoring checks

Shell word counts (including LaTeX command tokens): 01 = 2,752; 02 = 2,679;
03 = 2,622; 04 = 2,531; 05 = 2,580; 06 = 2,571; 07 = 2,729.
Total = 18,464 words. All seven chapter files and the bibliography have equal
opening/closing brace counts. A scan found no TODO, FIXME, PLACEHOLDER or
manual page-break commands. Citation keys were checked against the eight
provided bibliography entries. Read through the authored prose for semantic
and example consistency. `git diff --check` completed successfully for tracked
changes (these new untracked files are not covered by that Git command).
HEAD remains the starting SHA. No model state advanced.

The main task performs full build, cross-reference checks and visual review.
