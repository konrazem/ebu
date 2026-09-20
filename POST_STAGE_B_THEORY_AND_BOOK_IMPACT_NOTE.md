# Post-Stage-B theory and book impact note

Status: **impact analysis only. No manuscript byte is modified.**

Records what the two registered studies falsified, what survives, why Capacity
V2 is a new model rather than a patch, and which chapters would eventually need
amendment. Supplements `STAGE_A_BOOK_UPDATE_IMPACT_NOTE.md` and
`STAGE_B_BOOK_UPDATE_IMPACT_NOTE.md` without superseding them.

## 1. What Stage A falsified

The hypothesis that persistent absolute EBU capacity yields a self-stabilizing
response to a finite disturbance.

It is now known to be **structurally impossible** in the registered world, not
merely unobserved. Theorem 2 of `CURRENT_CAPACITY_FAILURE_THEOREMS.md`: at the
reference `sum_i B_i = D`, so `max_i B_i >= D/n`, and whenever `D >= n q^2`
some owner can afford a damaging singleton. Stage A had `4 >= 3`. The observed
zero `REACHED_AND_STAYED` in 128/128 was therefore a theorem, not a statistic.

## 2. What Stage B falsified

The hypothesis that the same mechanism provides a durable advantage under
sustained forcing.

Also structural. `E[D_ext | x] = q^2 (1/n) sum_i 1/sigma_i^2 > 0` exactly and
independently of `x`, because the gradient term averages away under
exchangeable edge selection while the nonnegative curvature term cannot. With
`V` bounded and `V + sum B = J` exact, capacity must absorb the drift; it
reached a median 5400 against a deviation ceiling of 300, the rejection rate
halved, and the arm difference decayed below the preregistered practical
threshold.

## 3. What survives untouched

Everything except the long-run capacity semantics:

physical actions as primary; exact finite EBU `E = V_pre - V_post`; the Level-1
Local Gaussian potential; local evaluation; simultaneous group valuation;
common-path receipts and their exact closure; physical feasibility before EBU;
**EBU calculates, actors choose**; the random actor as a falsification
instrument; physical conservation; exact rational arithmetic; no direct
capacity transfer; no borrowing; no global runtime optimizer.

Both registered studies also confirmed the foundation twice over: exact
identities held in every one of 1,048,576 Stage-B ticks and in all of Stage A,
with byte-identical replay.

## 4. Why Capacity V2 is a new model, not a patch

V2 changes the capacity state law: `B_i` is capped by the cell's own current
local potential `V_i`, with the excess retired to a declared monotone ledger,
and the exact identity becomes `V + sum_i B_i + C = J`.

That is a different scientific object. It therefore lives on a separate code
path with its own model identity, the registered V1 mechanism is unmodified and
still byte-reproducible, and V2 carries no registered evidence of any kind. The
registered studies must never be re-described as tests of V2.

## 5. What is already proved about V2

Stated so the books do not later present derived facts as discoveries:

- **Theorem V2-1:** the reference is absorbing — the exact negation of the
  Theorem 2 that doomed V1.
- **Theorem V2-2:** `sum_i B_i <= V <= V_max`, so capacity cannot diverge.
- **Theorem V2-3:** a cell returning to its reference nets zero capacity.
- **Theorem V2-4:** the extended ledger closes exactly, `C` monotone.
- **Theorem V2-5:** with forcing off, the process reaches the reference and
  remains there almost surely.

**No empirical claim accompanies these.** V2 has been run only in conformance
probes at non-registered seeds.

## 6. Chapters that would eventually need amendment

| Location | Required change |
|---|---|
| Ch 43 `ch:capacity` | The chapter presents persistent nonnegative `B_i` as *the* proposed policy. It must be re-scoped as **V1, the falsified baseline**, with the two theorems explaining why, and V2 introduced as a separate declared model. This is the largest change in the series. |
| Ch 43 l.30 | "Whether that freedom enables useful later action or merely supports cycles" is now answered for V1: it supported cycles, provably. |
| Ch 42 `ch:cycles` l.84 | The nonclaim stands, and gains a proof: under V1 cycling is not a policy preference but a consequence of the accounting identity having no sink. |
| Ch 44 | The Onsager/finite-step discussion can now contrast a mechanism with no dissipation term (V1) against one with an explicit accounted sink (V2). |
| Ch 45 | Deadlock discussion stays hypothetical: zero deadlock ticks in both registered studies. |
| Ch 55 | Gains the methodological pair already recorded, plus a third example: a preregistered falsification target derived from the model's own algebra, which then fired. |
| Ch 61 | A long-run study has been run; its line 11 warning about accounts drifting while deviation settles is now an observation. |
| Ch 62 | The worked audit can cite two exact ledgers, including the extended `V + sum B + C = J`. |

Nothing in Part I requires change. Neither study nor V2 alters a definition,
theorem or mathematical statement of the potential, valuation or receipt
theory.

## 7. Hard constraints on any future book edit

- A separately authorized book stage; this task modified no manuscript.
- V1 must be labelled as falsified in its strong form, with the scope limits
  intact: one synthetic 3-cell lossless world, one potential, one menu.
- V2 must be labelled a **candidate** with no registered evidence, and its
  theorems must not be presented as experimental findings.
- No chapter may claim EBU is stable. Neither registered study shows it, and
  V2's absorption theorem is a lattice-and-menu-dependent result about a model
  that has not been registered.
