# EBU current theory and authority index

```text
DOCUMENT TYPE:  NON-CONTROLLING NAVIGATIONAL INDEX (task artifact, not authority-tier)
AUTHORITY:      NONE; amends, replaces or outranks no source listed here
AUDIT:          NOT AN AUDIT; revision 2 after attribution audit NOT CLEARED
COORDINATE:     codex/v6-minimal-recovery-assessment
                @ a10f975c6b312b5ccd0b866e61ab2d5f3453d46e
COMPILED:       2026-10-08
STATE:          uncommitted working-tree file
```

If this index disagrees with a source it lists, the source governs under §B and
this index is wrong. It restates status; it does not decide it.

**Provenance labels** (audit outcomes and reported statuses):

| Label | Meaning |
|---|---|
| **VERIFIED FROM REPOSITORY EVIDENCE** | Established by committed content: a committed audit artifact, a commit record, or the document's own committed status or conclusion. |
| **REPORTED BY HANDOVER** | Stated in the 2026-10-08 programme handover, as restated in the Stage 1 task brief. Used for nothing else. |
| **REPORTED BY TASK BRIEF** | Supplied by a programme task or audit brief other than that handover. Where a committed report recites it, the recital is cited; a recital shows that the disposition was supplied to the authoring task, not the audit itself. Otherwise it is marked *uncommitted*. |

**Status classes** (they describe status; they create no authority rank):
AUTHORITY · INDEPENDENTLY CLEARED CONDITIONAL THEORY · EXPERIMENTAL DESIGN /
SPECIFICATION · REFUSED / FAILED CANDIDATE · NON-RELEASE IMPLEMENTATION ·
FUTURE UNVALIDATED WORK.

**Line references** (`X:n`) are to files at the coordinate above. Short names:
F foundation, B baseline, R path/equilibrium, MG Möbius–generator, FB feedback,
S equilibrium anchor, RF recursive field, SFE source-factor, M master theorem,
UNI unified semantics, T, U, VP V plan, UR U feasibility review.

## A. Verified repository coordinate

All rows: **VERIFIED FROM REPOSITORY EVIDENCE** (local Git; remote heads by
read-only `git ls-remote`, 2026-10-08).

| Item | Value |
|---|---|
| Repository | `konrazem/ebu`; `origin` = `https://github.com/konrazem/ebu.git` |
| Branch / HEAD / tree | `codex/v6-minimal-recovery-assessment` / `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` / `c127777ab756839b5f308bc3c4ba8dcc1a3412ca` |
| Remote head of that branch | `2f6f7e63861a8968ec83d745b73adaefc0c1f655` |
| Local-only commits | `387bd1ce04612596e078e4c4850a01566b6d37fc`, `7e5ee274694638cd8e0b2cc2e568e3435afc21a8`, `5434bcd78412d61985c41d5fa162b0e6b60a96b3`, `793457a2308afef810496f2a2ad36fedc794679f`, `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` |
| Published foundation | `origin/publication/physical-foundation` @ `c63d6833da10a75ef66db11f99fb5b5c68d94c5e` |
| Published scientific record | `origin/publication/scientific-record` @ `481753895509524c9d2674d1880d87712bb0ec18` |
| Not authority branches | `origin/main` @ `660d6e5a56cb096fe6d1e4d202f592155d982c79` and `origin/framework-v0.1` @ `a4af44afd3c878311ee373bc19e3be14b2aacec5` contain neither foundation nor baseline |

## B. Scientific authority precedence

Reproduced unchanged from B §0 (B:17–22). **VERIFIED FROM REPOSITORY EVIDENCE.**

| rank | source | role |
|---|---|---|
| **1** | `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | **FROZEN PHYSICAL FOUNDATION.** Wins every conflict |
| **2** | `docs/scientific_record/` (branch `publication/scientific-record`) | historical provenance — audits, gates, evidence manifest |
| **3** | `docs/theory/EBU_THEORY_BASELINE.md` ("this document" in B §0) | current post-freeze research status |
| **4** | exploratory reports / AI task transcripts | candidate claims only, never authority |

[`AGENTS.md`](../../AGENTS.md) controls repository procedure and states the same
scientific order: "frozen foundation > working theory baseline > exploratory
reports" (`AGENTS.md:21`). No CONDITIONAL, OPEN or EXPERIMENTAL result enters
the physical core without an explicit independent scientific gate (B §0;
`AGENTS.md`).

The committed hierarchy has no rank for independently cleared conditional
theory, and this index creates none. That term is a status class only. Every
§D report declares itself non-controlling (§I). The handover's ordering also
places the scientific record after the baseline and names a cleared-conditional
tier (**REPORTED BY HANDOVER**); the committed hierarchy above governs.

## C. Controlling foundation and baseline

| Component | Document @ version | Status · class | Independent-audit outcome | Provenance limitation |
|---|---|---|---|---|
| Frozen physical foundation | [`docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md`](../physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md), frozen at `c63d6833da10a75ef66db11f99fb5b5c68d94c5e`; HEAD carries the identical blob `aa756d30b056f7c12b2b7b49925da0b12bb06c49` | FROZEN · **AUTHORITY** (rank 1). VERIFIED FROM REPOSITORY EVIDENCE: freeze commit, B §0 pin, B meta | Independent freeze audit **CONDITIONAL PASS** and final freeze-closure audit **CONDITIONAL PASS**: VERIFIED FROM REPOSITORY EVIDENCE (`docs/scientific_record/physical_foundation/FOUNDATION_INDEPENDENT_FREEZE_AUDIT.md:342`, `FOUNDATION_FINAL_FREEZE_CLOSURE_AUDIT.md:127` at `481753895509524c9d2674d1880d87712bb0ec18`). Final narrow audit PASS: stated in the freeze commit message (a commit record; no separate artifact) | F's own header still reads "FREEZE CANDIDATE. NOT FROZEN" (documentary issue, M:123). The record manifest notes that some audit bodies were taken from session transcripts or the ChatGPT project record (`EVIDENCE_MANIFEST.json:16`) |
| Working theory baseline | [`docs/theory/EBU_THEORY_BASELINE.md`](EBU_THEORY_BASELINE.md) @ `f8a13fde3a9559a01123b0adb484e8bddf040b80`; meta @ `a8b8c815b0f96ef36650be29a5de138fa26ad02d` | ACTIVE WORKING BASELINE · **AUTHORITY** (rank 3). VERIFIED FROM REPOSITORY EVIDENCE | Not an audited theorem object | Built 2026-09-28. Its current-experiment and next-gate fields still name E1a v4 (B §24; meta `next_gate`). It records none of §§D–H. This index does not update it |

## D. Conditional mathematics

All rows: status class INDEPENDENTLY CLEARED CONDITIONAL THEORY, as reported.
The two outcome columns keep the handover and task-brief sources separate.

| Component | Document @ last change | Committed status (VERIFIED FROM REPOSITORY EVIDENCE) | Outcome — REPORTED BY HANDOVER | Outcome — REPORTED BY TASK BRIEF | Provenance limitation |
|---|---|---|---|---|---|
| R — path/equilibrium semantics, finite endpoint valuation | [R](EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md) @ `6c1d0822790dc98e249a30ff5e8fa28202723e82` | "R-STAGE REPAIR: COMPLETE — INDEPENDENT RE-AUDIT REQUIRED" (R:7) | Not separately stated. The handover states "FINITE EBU: cleared" without naming R | **INDEPENDENTLY CLEARED**, recited as "user-supplied audit disposition" (MG:7; also S:8, FB:87, T:4). The first audit of `0a4c229a3299ee1e6ed4a2e5efb964b7334ed0e4` was NOT CLEARED (recited, R:32) | No audit artifact; MG:76 states that none was recovered |
| S-MG — Möbius–generator continuity, with prior-art appendix | [MG](EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md), [appendix](EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md) @ `a7655f30bde7b798ca98eacd9138f93b36abf733` | "INDEPENDENT THEOREM AUDIT: REQUIRED BEFORE BOOK 1 INTEGRATION" (MG:14); the appendix also requires literature verification (appendix:10) | Not separately stated | **INDEPENDENTLY CLEARED**, recited at S:9 and U:7; the appendix as "Cleared" at S:971 | No audit artifact |
| Feedback/oscillation reconciliation | [FB](EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md) @ `f3ef451773e5c421952c67382ea0a7d5b6565da8` | "INDEPENDENT AUDIT: REQUIRED BEFORE BOOK 1 INTEGRATION" (FB:13) | Not separately stated | **INDEPENDENTLY CLEARED**, recited at S:10 | No audit artifact |
| S — canonical equilibrium/root anchor | [S](EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md) @ `0fad60bfb8df919df24227756f8ef03480dad2e3` | "S9: INDEPENDENT AUDIT REQUIRED; NOT PERFORMED HERE" (S:13); cross-field commensurability "EMPIRICALLY UNESTABLISHED" (S:854) | Not separately stated. The handover's "ROOT PHYSICAL VALIDATION: not yet demonstrated" concerns physical validation (§I) | **INDEPENDENTLY CLEARED**, recited at T:5 ("S9 clearance supplied in the task") and U:7 | No audit artifact. A conditional theorem; no physical root validation |
| RF — recursive sufficient-state field | [RF](EBU_FIELD_RELATION_AND_RECURSIVE_SUFFICIENCY.md) @ `7e912b9e3b0b3b8fd75db1fd9443b55bda9b73b2` | "PENDING INDEPENDENT AUDIT" (RF:5) | **"RECURSIVE FIELD THEORY: independently cleared"** | **INDEPENDENTLY CLEARED**, recited at W1:106, SFE:125 and UNI:92 | No audit artifact. Bytes unchanged since those recitals |
| SFE — source-factor embedding and orientation | [SFE](EBU_SOURCE_FACTOR_EMBEDDING_AND_ORIENTATION_THEOREM.md) @ `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` | "PENDING INDEPENDENT THEOREM AUDIT" (SFE:7); conclusion A, compatible under explicit conditions (SFE:8) | **"SOURCE-FACTOR MATHEMATICS: independently cleared"** | **INDEPENDENTLY CLEARED**, recited at UNI:92 for the version at `df352d4a1ce28b7f133c004438263fa54cfb45ee` | The file changed after that recital in `387bd1ce…`, `7e5ee274…`, `793457a2…` and `a10f975c…`, all local-only. Clearance of the current bytes rests on the handover |
| M — master unification theorem | [M](EBU_RECURSIVE_FIELD_SOURCE_FACTOR_CONTINUITY_UNIFICATION_THEOREM.md) @ `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` | "PENDING INDEPENDENT THEOREM AUDIT" (M:7); conclusion A, one compatible hierarchy, no foundation change | **"MASTER UNIFICATION THEOREM: independently cleared"** | **INDEPENDENTLY CLEARED**, recited at UNI:92 for the version at `df352d4a1ce28b7f133c004438263fa54cfb45ee` | Same version gap as SFE. M:103 pins SFE by its historical "original reading" SHA-256 `547de25e…`, not the current bytes |
| Unified marginal-vector and directional-action semantics | [UNI](EBU_UNIFIED_MARGINAL_VECTOR_DIRECTIONAL_ACTION_SEMANTICS.md) @ `793457a2308afef810496f2a2ad36fedc794679f` | "PENDING INDEPENDENT AUDIT" (UNI:7); conclusion A; "NEXT BOUNDED TASK: INDEPENDENT AUDIT OF THIS REPORT — NOT BEGUN" (UNI:1417) | **"UNIFIED MARGINAL-VECTOR SEMANTICS: independently cleared"** | None | No recital and no audit artifact; last change is local-only |
| Unified joint-field theory architecture (RF + SFE + M + UNI) | as above | Each component non-controlling (§I) | **"EBU UNIFIED JOINT-FIELD THEORY ARCHITECTURE: INDEPENDENTLY CLEARED"**; names `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` as the final bounded semantic-repair commit | The `a10f975c…` repair brief reports the preceding global audit NOT CLEARED on two documentary findings only, with everything else cleared (*uncommitted*; not recited) | No artifact for either audit |

## E. Current unified field semantics

Each row's source text is committed. Audit provenance follows the source
document's row in §§C–D.

| Element | Statement | Source | Class |
|---|---|---|---|
| Finite EBU | `E = V_pre − V_post`; one complete registered finite action receives one complete endpoint value | F:37, F:101; UNI:50 | **AUTHORITY** (frozen definition) |
| Marginal potential | `μ = ∇V` | F:52; B:201 | **AUTHORITY** |
| Local action slope | `f_a = −dV(s_a)`; for labelled directions, `f = −Sᵀμ`. In fixed Euclidean coordinates `f_a = −μᵀs_a`, the a-th entry of `−Sᵀμ` (handover form) | UNI:27, UNI:226, UNI:1011 | INDEPENDENTLY CLEARED CONDITIONAL THEORY |
| No competing settlements | Factor contrasts, coordinate differentials, local slopes and Möbius coefficients are not further EBU settlements | UNI:50–53 | INDEPENDENTLY CLEARED CONDITIONAL THEORY |
| Diagnostics | Source, factor, coordinate and Möbius quantities are diagnostic decompositions. Source and total signs are diagnostic properties of one valuation | UNI:11, UNI:46, UNI §15 (UNI:856), UNI:1040; B:248 (Möbius) | INDEPENDENTLY CLEARED CONDITIONAL THEORY; B row is **AUTHORITY** |
| Orientation assumption | Generic, optional, unparameterized A5 "Declared orientation property", applying only to a specific declared physical sign claim; not required for base valuation | M:201, M:333 | INDEPENDENTLY CLEARED CONDITIONAL THEORY |
| Actor allocation | A separate layer that must close to the complete total under a separately declared, foundation-compatible convention | M:1829 | INDEPENDENTLY CLEARED CONDITIONAL THEORY |
| Institutional interpretation | A separate later layer using already-defined EBU values; it does not alter the physical value | SFE:1305–1308 | INDEPENDENTLY CLEARED CONDITIONAL THEORY |
| Market price | A separate institutional object | UNI:1095 | INDEPENDENTLY CLEARED CONDITIONAL THEORY |

## F. Retired concepts and active replacement

| Retired (do not revive) | Active replacement | Removed in | Evidence |
|---|---|---|---|
| `SF` / `TA` / `BT` regime taxonomy; `MASTER-SF`, `MASTER-TA`, `MASTER-BT` | None: source and total signs are diagnostic properties of one valuation | `387bd1ce04612596e078e4c4850a01566b6d37fc` (reframed), `7e5ee274694638cd8e0b2cc2e568e3435afc21a8` (removed) | UNI §15; SFE §18; M §23 |
| Global sign regime, programme sign choice, human sign decision, source/total/both programme choice | "No orientation regime, branch, mode or policy in EBU, and no global sign decision" | `7e5ee274…`, `793457a2308afef810496f2a2ad36fedc794679f` | M:1805; UNI:57–58 |
| `A5(r)` | Generic optional A5 (§E) | Last residue removed at `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` | M:201 |
| "the programme's institutional sign semantics" | Institutional interpretation as a separate later layer | `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` | SFE:1305–1308 |

**Removal: VERIFIED FROM REPOSITORY EVIDENCE.** At `a10f975c…`, every match for
these terms in `docs/theory`, `docs/e1a`, the foundation and `AGENTS.md` is an
explicit denial.

**Audit of the removal: REPORTED BY HANDOVER** ("RETIRED SIGN REGIMES: removed
from active theory"; architecture cleared, §D last row).

## G. W1 status

| Item | Content | Provenance |
|---|---|---|
| Document | [W1](EBU_SOURCE_FIELD_W1_WATER_ADMISSION.md) @ `5434bcd78412d61985c41d5fa162b0e6b60a96b3` (local-only) | VERIFIED FROM REPOSITORY EVIDENCE |
| Status · class | Primary result **B**: the selected complete W1 water–drive–bath action potential is refused for the requested whole-action sign. A scoped water factor is possible in principle but not certified. Thermal root status is "PARTIALLY CHALLENGED" (W1:11–12, W1:411). Class: **REFUSED / FAILED CANDIDATE** for the selected complete candidate | VERIFIED FROM REPOSITORY EVIDENCE (the report's conclusion) |
| Handover | "W1 COMPLETE WATER CANDIDATE: refused". No separate W1 re-audit outcome is stated | REPORTED BY HANDOVER |
| Task brief | Narrowing disposition "W1 SOURCE-FIELD REFUSAL: VERDICT REQUIRES NARROWING", with the mathematics accepted, recited at W1:92 | REPORTED BY TASK BRIEF |
| Own header | "INDEPENDENT RE-AUDIT: PENDING" (W1:8) | VERIFIED FROM REPOSITORY EVIDENCE |
| Limitation | M:103 table pins W1 by its original-reading SHA-256 `382df734…`. M:104–112 records the current `70efbc49…` after `5434bcd7…` | VERIFIED FROM REPOSITORY EVIDENCE |

## H. E1a and T/U/V status

| Component | Document @ version | Status · class (VERIFIED FROM REPOSITORY EVIDENCE) | Outcome — REPORTED BY HANDOVER | Outcome — REPORTED BY TASK BRIEF; own text |
|---|---|---|---|---|
| E1a v4 | [v4 design](../e1a/E1A_V4_PROSPECTIVE_DESIGN.md) @ `a8b8c815b0f96ef36650be29a5de138fa26ad02d`; implementation `e1a_v4/` | The baseline's current experiment. The track is paused: preserved, not sealed, not run (commit message `dd0d6b0e5d370de1bda805e07215ea0be4d6d083`; T:8). **NON-RELEASE IMPLEMENTATION** | Not stated | None (paused) |
| T — minimal equilibrium design | [T](../e1a/E1A_MINIMAL_EQUILIBRIUM_EXPERIMENT_DESIGN.md) @ `fb977f425a25d3252fdcfb510b767448aa839fe9` (base design `ebcf2641fa2d8fe4ab95fef011e96fe53feeadc6`) | Non-controlling T-stage experiment design (T:3). **EXPERIMENTAL DESIGN / SPECIFICATION**. Execution: NOT AUTHORISED (T:11) | Not stated | Base T **CLEARED**: "as reported by the commissioning brief" (T:1295). T11a amendment `E1A-T11a-RF-v1` **CLEARED**, recited at UR:15. Own text: T11a "not yet independently cleared" (T:1296); T12 "INDEPENDENT AUDIT REQUIRED" (T:7) |
| U — Branch-A physical calibration specification | [U](../e1a/E1A_BRANCH_A_PHYSICAL_CALIBRATION_QUALIFICATION.md) @ `c3f64361be74f1ade30856f528c0987719bb7947` | Non-controlling U-stage calibration specification (U:3). **EXPERIMENTAL DESIGN / SPECIFICATION**. U9 complete as specification; not physically qualified; calibration data not collected; apparatus qualification not established (U:10–12) | Not stated | Original U audit **NOT CLEARED**, with re-audit of the repair required (recited, U:9–10). Later **CLEARED**, recited at UR:15. Own text: "NOT INDEPENDENTLY CLEARED" (U:47) |
| V — pre-execution validation | [V plan](../e1a/E1A_V5_VALIDATION_PLAN.md) and [JSON](../e1a/e1a_v5_validation_plan.json) @ `5874548e81b20d66fbfc24b5fc3bcaf97cbb1b42` (procedure 6); implementation `e1a_v5/`. Reports: [pre-execution](../e1a/E1A_V5_PREEXECUTION_VALIDATION_REPORT.md) @ `2e39ae682dd6d67561beaa5755b16546748d2f79`, [V6 core repair](../e1a/E1A_V5_V6_CORE_REPAIR_REPORT.md) @ `4c88a5f021cd58b50b590634af87c937a61d477f`, [V6 recovery](../e1a/EBU_V6_FAILURE_CONSOLIDATION_AND_MINIMAL_RECOVERY.md) @ `e51dd077813340d3616d76644db5f3f888e04682` | V **NON-RELEASE**; V6 benchmark "UNQUALIFIED" (V6 recovery:9); W BLOCKED. A "baseline sign defect" is still owed before the W-stage authority freeze (VP:11). **NON-RELEASE IMPLEMENTATION** | "V-STAGE IMPLEMENTATION: NON-RELEASE" (status) | Procedure v2 AUDIT FAILED; v3, v4 and v5 NOT CLEARED (recited, VP:6–7). V6 "still failed core audit" (recited, V6 recovery level-A row) |
| UF-01 — selected optical apparatus | [UR](../e1a/E1A_U_PHYSICAL_METROLOGY_FEASIBILITY_REVIEW.md) @ `d03de8e26c6f8f8d29aa73457c125132cc29816c` | "U-FEASIBILITY PACKET: REFUSE": apparatus-choice failures (2 nm registration and localization), not a T/U contradiction (UR:3–7). **REFUSED / FAILED CANDIDATE** | "E1a CURRENT SELECTED OPTICAL APPARATUS: refused / unqualified" | None. Own header: "awaiting independent audit" (UR:3) |

## I. Release and physical-execution restrictions

| Restriction | State | Provenance |
|---|---|---|
| V-stage release | NON-RELEASE | VERIFIED FROM REPOSITORY EVIDENCE (pre-execution report:10, V6 core repair report, UR:9) |
| W-stage | BLOCKED | VERIFIED FROM REPOSITORY EVIDENCE |
| Physical execution | NOT AUTHORISED | VERIFIED FROM REPOSITORY EVIDENCE (T:11; V reports; UR:9) |
| Real physical or calibration data | Not used; not collected | VERIFIED FROM REPOSITORY EVIDENCE (pre-execution report header; U:11) |
| Release tags | No tag contains any commit after `f8a13fde…` | VERIFIED FROM REPOSITORY EVIDENCE |
| Theory reports | Each §D report and W1 declares itself non-controlling in its header (R:6, MG:6, appendix:6, FB:6, S:7, RF:5, SFE:6, M:6, UNI:6, W1:7). A closing "AUTHORITY MODIFIED" line reading NO appears at MG:1686, FB:1138, S:1131, RF:1337, SFE:1546, M:1892, UNI:1426 and W1:1218; MG and S use padded spacing. R has no such line. The appendix states "SCIENTIFIC AUTHORITY: UNCHANGED" (appendix:7) | VERIFIED FROM REPOSITORY EVIDENCE |
| Root physical validation | Not demonstrated | REPORTED BY HANDOVER; consistent with S:854 and W1:411 |
| Multi-field physical EBU | Not demonstrated | REPORTED BY HANDOVER; no committed demonstration exists |
| Book 1 | A committed edition exists at `fd4fbd3fb11560311bd1ad9e97aa455ad00fc83d`, with an integration report at `f4c7277cddef5abf5fbfc8b43003b72596593e79`; no Book 1 commit follows. M:1787 conditions any integration of new theory on independent clearance | Committed edition and M:1787: VERIFIED FROM REPOSITORY EVIDENCE. Edition clearance: S:11 states "BOOK 1: INDEPENDENTLY CLEARED THEORETICAL EDITION" without naming a source or artifact (REPORTED BY TASK BRIEF, recited). Deferral: "BOOK 1: deferred" (REPORTED BY HANDOVER); the `a10f975c…` repair brief also deferred Book 1 regeneration (REPORTED BY TASK BRIEF, *uncommitted*) |

## J. Next scientific gate

| Statement | Provenance |
|---|---|
| **Next bounded task:** the programme roadmap / scientific validation plan, a planning document with no execution. **NOT BEGUN**; this index does not authorize it | REPORTED BY TASK BRIEF, *uncommitted*: the `a10f975c…` repair brief (§11) deferred "the programme roadmap" and Book 1 regeneration until independent re-audit of that repair. The attribution audit of this index names "the programme roadmap/scientific validation plan" as the step after this index's repair. REPORTED BY HANDOVER: the architecture INDEPENDENTLY CLEARED with `a10f975c…` as the final repair. The re-audit's own wording is not available to this index |
| **Physical-root study** ("ASTRA's root study"): **NOT BEGUN**. Nothing in the repository designs or authorizes it. Class: **FUTURE UNVALIDATED WORK** | REPORTED BY TASK BRIEF, *uncommitted*: the Stage 1 brief forbids advancing to it. Root physical validation is "not yet demonstrated": REPORTED BY HANDOVER |
| The committed theory record still names independent audit as the next stage (M:1801; UNI:1307, UNI:1417); the handover reports that clearance as obtained (§D) | Text: VERIFIED FROM REPOSITORY EVIDENCE. Outcome: REPORTED BY HANDOVER |
| The baseline's `next_gate`, "E1a v4 bounded implementation", is stale | VERIFIED FROM REPOSITORY EVIDENCE |
| E1a: after the UF-01 refusal, "a future V-only replacement still requires a different, independently defensible prospective apparatus packet; this report neither constructs nor authorizes one" (UR:7) | VERIFIED FROM REPOSITORY EVIDENCE |

## K. Evidence register and unresolved limitations

| Path | Last-change commit | SHA-256 |
|---|---|---|
| `AGENTS.md` | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` | `168307e07f79d980a5545bc4283619f44e5ba54eb750212783daf65356bb2e94` |
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.md` | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` (frozen at `c63d6833da10a75ef66db11f99fb5b5c68d94c5e`) | `6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507` |
| `docs/physical_foundation/EBU_PHYSICAL_FOUNDATION_CANONICAL.meta.json` | `c0099d8f7eea95a0f683f3c09fef71bdffc369af` | `b7771b54002b02433c2aede767ce1b7e04b79096613f7f2b5a1927cd6f94b39d` |
| `docs/theory/EBU_THEORY_BASELINE.md` | `f8a13fde3a9559a01123b0adb484e8bddf040b80` | `0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa` |
| `docs/theory/EBU_THEORY_BASELINE.meta.json` | `a8b8c815b0f96ef36650be29a5de138fa26ad02d` | `b7225e9f8614488ae2953a8a6a6016aaa476180cdcadb5b16e181e4f2d56f133` |
| `docs/theory/EBU_PATH_EQUILIBRIUM_SEMANTICS_RECONSTRUCTION.md` | `6c1d0822790dc98e249a30ff5e8fa28202723e82` | `5b2ac35a87cdd12981a4eb55e716685ce42aa6b61a2cd6c6a2efddbef745b5de` |
| `docs/theory/EBU_MOBIUS_GENERATOR_CONTINUITY_THEOREM.md` | `a7655f30bde7b798ca98eacd9138f93b36abf733` | `2378f618f9bff309c77ccdb940be1b86500fbf97b1398133d88d1aec4bc1dbee` |
| `docs/theory/EBU_MOBIUS_GENERATOR_PRIOR_ART_APPENDIX.md` | `a7655f30bde7b798ca98eacd9138f93b36abf733` | `ac8128659ff0955ef16197c37c5698f6039c2f4d074c25e2f9c48ef2e89199ff` |
| `docs/theory/EBU_FEEDBACK_OSCILLATION_THEORY_RECONCILIATION.md` | `f3ef451773e5c421952c67382ea0a7d5b6565da8` | `a18d11d309efcb4490e8dc0b7a86a327026c0a58a755e649722d9a9071882c18` |
| `docs/theory/EBU_EQUILIBRIUM_THERMODYNAMIC_ANCHOR.md` | `0fad60bfb8df919df24227756f8ef03480dad2e3` | `5b92fdf5749ee05db63f32320e2b34a10afa2c98ceaf2e7a996f78b2df60505f` |
| `docs/theory/EBU_FIELD_RELATION_AND_RECURSIVE_SUFFICIENCY.md` | `7e912b9e3b0b3b8fd75db1fd9443b55bda9b73b2` | `685b90eb6acef40b5a8277a9652ef3dceaf4017f91c47df3853a75e2a7f139e3` |
| `docs/theory/EBU_SOURCE_FACTOR_EMBEDDING_AND_ORIENTATION_THEOREM.md` | `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` | `684dbda50a27b5c53aff9747c9fabc7683fc610b53afe325179cd9698e25f839` |
| `docs/theory/EBU_RECURSIVE_FIELD_SOURCE_FACTOR_CONTINUITY_UNIFICATION_THEOREM.md` | `a10f975c6b312b5ccd0b866e61ab2d5f3453d46e` | `3d5d352dde4f89d711abbc5d860b2a49656aa180d77557970f6c752b8c831fe6` |
| `docs/theory/EBU_UNIFIED_MARGINAL_VECTOR_DIRECTIONAL_ACTION_SEMANTICS.md` | `793457a2308afef810496f2a2ad36fedc794679f` | `660efdf962871898faef95f2c4e957e091b459ae2e9b48897f1ebf2aadb79171` |
| `docs/theory/EBU_SOURCE_FIELD_W1_WATER_ADMISSION.md` | `5434bcd78412d61985c41d5fa162b0e6b60a96b3` | `70efbc4988dc32fdc5d49e98020c81afe3f33c04ceb8e4b151dd75426f0ebf85` |
| `docs/e1a/E1A_V4_PROSPECTIVE_DESIGN.md` | `a8b8c815b0f96ef36650be29a5de138fa26ad02d` | `25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6` |
| `docs/e1a/E1A_MINIMAL_EQUILIBRIUM_EXPERIMENT_DESIGN.md` | `fb977f425a25d3252fdcfb510b767448aa839fe9` | `10ddfdceb90454a87cd83a7868c65a1e1b7a7147cc4e8360faf70225ba6d4519` |
| `docs/e1a/E1A_BRANCH_A_PHYSICAL_CALIBRATION_QUALIFICATION.md` | `c3f64361be74f1ade30856f528c0987719bb7947` | `af66f3fe640c25b5bf0bc11e61f3b77e944c70f2e4a2a040841b65a12d4b8d0a` |
| `docs/e1a/E1A_V5_VALIDATION_PLAN.md` | `5874548e81b20d66fbfc24b5fc3bcaf97cbb1b42` | `2ffbb9db25ca631818938ff27d93131ebe40dc9c75ca039602f15088cdf2bdca` |
| `docs/e1a/e1a_v5_validation_plan.json` | `5874548e81b20d66fbfc24b5fc3bcaf97cbb1b42` | `0ef888251bff0892e0afdda914677cc96d161ca0e6a9b47e8a386af9f3f66132` |
| `docs/e1a/E1A_V5_PREEXECUTION_VALIDATION_REPORT.md` | `2e39ae682dd6d67561beaa5755b16546748d2f79` | `81ae22b3c06fcfb4b3b4598e703b75f12d8a0136757b2c4fd9b820fca9a68c90` |
| `docs/e1a/E1A_V5_V6_CORE_REPAIR_REPORT.md` | `4c88a5f021cd58b50b590634af87c937a61d477f` | `a0549d514f5371faf30486369affb25d65e8f12ea8b9ec1aa030b4091cf0f10c` |
| `docs/e1a/EBU_V6_FAILURE_CONSOLIDATION_AND_MINIMAL_RECOVERY.md` | `e51dd077813340d3616d76644db5f3f888e04682` | `a2f8d74000d896e7e8fc04903af65d7dc653424086998442e1903c6a20828dc3` |
| `docs/e1a/E1A_U_PHYSICAL_METROLOGY_FEASIBILITY_REVIEW.md` | `d03de8e26c6f8f8d29aa73457c125132cc29816c` | `e69398bba6a4688c4e8c150eb69896e20569fdd7f78e10810744d52a08bf5fa1` |

**Unresolved limitations**

1. **Audit artifacts.** Apart from the foundation, no committed audit artifact
   exists for any component above. Every outcome labelled REPORTED BY HANDOVER
   or REPORTED BY TASK BRIEF rests on that report or on its committed recital.
2. **Reports are uncommitted.** The handover is known here only as restated in
   the Stage 1 task brief. The task briefs marked *uncommitted* (the
   `a10f975c…` repair brief, the Stage 1 brief, and the attribution audit of
   this index) are not in the repository.
3. **Version gap.** The repository recital of M and SFE clearance (UNI:92)
   covers the versions at `df352d4a…`, not the current bytes.
4. **Historical headers.** Pending-audit headers and F's freeze-candidate header
   are retained historical wording. This index rewrites none of them.
5. **Stale baseline.** The baseline (rank 3) does not reflect §§D–J. Updating it
   is a separate authorized stage.
6. **Unpushed commits.** The five local-only commits mean GitHub does not yet
   carry `a10f975c…`. Pushing requires explicit authorization.
7. **This index is uncommitted.** It has no commit coordinate of its own, and its
   line references go stale when the cited files change.
