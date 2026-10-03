# E1a-v4 — PROGRAMME PAUSE RECORD

**Record type:** REPORT ONLY. This file is a project-control record, **not authority**.

It changes no authority document, no plan, no contract, no seed map, no implementation, no
test, no execution seal and no execution flag. `execution_authorised` remains `false` in the
frozen plan because it was already `false`; this record does not set it and could not.

---

## 1. Decision recorded

```
E1a-v4 HIGH-ASSURANCE EXECUTION TRACK
PAUSED PENDING SCIENTIFIC REDESIGN REVIEW
```

Paused at its current committed coordinate. **Preserved, not rejected, not deleted, not
rewritten, not sealed, not run.**

| | |
|---|---|
| paused at HEAD | `bd9a3a111068e5be72bcdf21c5bd15b82da73012` |
| branch | `gaussian/stage-a-environment` |
| plan version | `1.17.0` |
| last implementation commit | `7f0647624c4a415071411c719fd615a54357f452` (F2e passive-drag runtime) |
| working tree at pause | clean |
| pushed | no |

---

## 2. Why now

Two independent reasons, and the first is the practical one.

**The track was already blocked.** F2 is NOT CLEARED. Two items stand, both recorded at
`9ada901` and `bd9a3a1`:

- the **C7/C8 numerical-gating defect** — `eta = a = 5e-324` is realised, published and
  issues the Branch-B unblind token, while strict publication/recovery verification refuses
  the same record. CONFIRMED, independently reproduced, **repair not started**;
- the **`BranchARealisation.calibration_condition` constructor question** — AUTHORITY
  UNSPECIFIED, currently unreachable by any official path.

So pausing before F3 forfeits no available progress. F3–F8 were not startable.

**A redesign proposal is under review.** "EBU E1a BRIDGE REDESIGN ANALYSIS" proposes making
the direct Boltzmann bridge `p_θ(x) ∝ exp[−β V_θ(x)]` the primary hypothesis, with the
Gaussian whitened-covariance form as the estimator and `K = βH` as a secondary diagnostic.
It is marked NOT YET AUTHORITATIVE by its own header. A bounded analysis of it is committed
alongside this record at `docs/e1a/E1A_BRIDGE_REDESIGN_BOUNDED_ANALYSIS.md`.

That analysis found, among other things, that the proposal's estimator is **algebraically
identical** to the one E1a-v4 already uses, that the experiment is **systematics-limited**
rather than statistics-limited, and that the Branch-A uncertainty budget is **structurally
incomplete under the currently authorised Route A**. None of those findings is settled; all
require independent review.

---

## 3. What is paused

```
F3 - F8                                   DO NOT CONTINUE
official campaign                         NOT RUN
final execution seal                      NOT FROZEN
trajectory-bearing integration suite      DEFERRED, NOT RUN
C7/C8 numerical-gating repair             NOT STARTED  (blocked by the pause, not by difficulty)
F4 field construction / drag inputs       OPEN
```

## 4. What is NOT paused and NOT affected

```
the committed E1a-v4 record            PRESERVED IN FULL
git history                            NOT REWRITTEN
frozen foundation and theory baseline  UNCHANGED
the design contract and plan           UNCHANGED
every identity                         UNCHANGED
the books                              UNCHANGED - no book asserts the redesign is accepted
pure/static test suites                STILL PASSING, see section 6
```

## 5. Assets explicitly preserved

The reclassification is conceptual only. E1a-v4 is retained as a **high-assurance execution
and reproducibility framework** rather than as the minimum experiment needed to test
`β = 1`. The following carry forward under any redesign outcome:

```
Branch-A / Branch-B separation and the anti-circularity type boundary
hashing, publication order and the publish-before-unblind guarantee
calibration identity and the null-law binding invariant
provenance verification, restart safety and lock reconciliation
structured refusals and whole-record consistency
the four declared field definitions
the positive (blinded-scale) and negative (false-bridge) controls
exact seed families and their disjointness
mutation and authority-gap infrastructure
execution sealing machinery
```

The bounded analysis records which of these are **core science** (Branch-A/Branch-B
separation, blinding order, seed disjointness, the two controls) and which are **software
certification** (lock stores, restart reconciliation, mutation classes, sealing). That
distinction matters for the redesign; neither group is discarded here.

---

## 6. Verified state at the moment of pause

```
4,002 checks, 0 failures, 17 suites, 0 suite(s) not clean
static preflight: PASSED

contract   d7215ae4636a88a6542d616c8c974d6a5aeca9f68ba487a7a39cac338593fad4
design     25b637c3af0e92d73f6dec0e992da9dd42d9fadc00020e89f20b76c2f1ad70a6
foundation 6d9aed2440196f7f85d9651649b7168574f365adf8057b8d4ae2709b03f01507
baseline   0a01b3566c5ba37674f87ba827732e8d7f694fb5a532901e5883ea8317b74eaa
plan       fbe1877826a3947399065451b9bfa3fba730243c144d33648bf05b631a7ba9e4
seed map   c25f2da8ab9a465ae588d7beeeb8ecd6ed0bd70174badeea98985255a58d28af
analysis   60122602528f7e89ae3aa6716a20db5a0bf6e89ad52bc7b1e031318327add527
execution  442e3d53e3e6f660b78af350e1d5db2312eccb09dca78e764c0442e476aa166b   (PRE_DRIVER, unsealed)

OFFICIAL CAMPAIGN      NOT RUN       SCIENTIFIC RNG DRAWS    0
OFFICIAL RESULTS       NONE          OFFICIAL TRAJECTORIES   0
EXECUTION SEAL         NOT FROZEN    CALIBRATION EXECUTIONS  0
EXECUTION AUTHORISED   FALSE         CAMPAIGN JOBS           0
SEED MAP               UNCHANGED, no family drawn
```

`results/e1a_v4_validation` does not exist.

---

## 7. Resuming

This pause is lifted by an explicit decision recorded in this repository, not by the
absence of objection and not by a task existing. Resumption should state which of these it
is:

1. **Resume E1a-v4 unchanged** (proposal Option A) — next action is the C7/C8 repair, then
   the F2 constructor question, then F3.
2. **Adopt a redesign** — requires a prospective amendment to frozen authority before any
   implementation, following the same amendment pattern used for disposition G6.
3. **Split the tracks** (proposal §31) — Track S scientific benchmark, Track V this
   framework as its infrastructure. Requires deciding which E1a-v4 controls Track S inherits.

Until then: no implementation, no authority amendment, no execution.

---

**Nothing in this record authorises execution. Nothing in it changes any frozen artifact.**
