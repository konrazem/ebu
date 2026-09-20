# Stage-B book update impact note

Status: **impact analysis only. No manuscript byte is modified by this task.**

Records what the registered Stage-B result would change if a separately
authorized book stage opens. Conservative by design: two registered studies on
one synthetic 3-cell world license few sentence changes.

Source: `STAGE_B_REGISTERED_REPORT.md`, preregistration
`4c826a9be4c6306fa57698eb23c1076ebf75b970`. Chapter references are to
`books/part_ii_integrated/` on `codex/book-series-eight-parts`. This note
supplements, and does not supersede, `STAGE_A_BOOK_UPDATE_IMPACT_NOTE.md`.

## 1. The chapter the result most directly answers

**Ch 43 `ch:capacity`, line 30** currently reads, of an owner spending
accumulated capacity on a negative-valued action:

> "Whether that freedom enables useful later action or merely supports cycles is
> precisely the sort of question that remains for research."

Stage A answered the cycling half for a transient. **Stage B answers a sharper
version**: under sustained forcing that freedom *grows without bound*. Median
terminal `sum_i B_i` reached 5400 against a deviation ceiling `V_max = 300`, and
the fraction of feasible groups refused on capacity grounds halved across the
analysis window, 0.0662 to 0.0332.

The defensible replacement is not "the question is settled" but:
*for this world, accumulated capacity progressively weakened the constraint
itself, and the study did not observe that process stop.*

## 2. The chapter the result most strikingly vindicates

**Ch 61 `ch:interpretation`, line 11** already says:

> "Deviation may appear to settle while external audit or capacity balances
> continue to drift. A stationarity claim must therefore identify its subject..."

This is now **an observation rather than an anticipation**. Stage B found
exactly that split: the control arm's physical `V/V_max` was nearly flat across
blocks (0.2571, 0.2527, 0.2525) while `sum_i B_i` grew at roughly 0.43–0.67 per
tick in both arms and never saturated. The EBU arm's physical marginal was still
drifting, reported as `NO EVIDENCE OF LATE-WINDOW STATIONARITY`.

The sentence needs no correction. It can gain a citation to a registered result
that instantiates it.

## 3. Statements that could become observed results

| Location | What Stage B supports |
|---|---|
| Ch 42 `ch:cycles` l.84 | Nonclaim stands. Stage B adds that under sustained drive neither arm refused and neither deadlocked, in 1,048,576 ticks. |
| Ch 44 l.85, "random affordable actors can spend capacity on negative-valued actions" | Now quantified: in the EBU arm the gate refused 3–7% of feasible groups, declining across the window; the control's counterfactual refusal rate was 53–65%. |
| Ch 45 ll.57-58, observables that "can genuinely differ" | Measured under continuous drive: deviation occupancy, boundary occupancy, relaxation time and refusal all have registered values. Notably both arms share the **same relaxation lag of 32**, so the constraint shifts the deviation level without changing temporal structure. |
| Ch 61 `what a long-run study could show` | A long-run study has now been run. The chapter can cite it while keeping its conditional framing for everything not yet tested. |
| Ch 55 `tests that can genuinely detect being wrong` | Gains a second worked example: Stage B's preregistered falsification target was stated before execution, derived from the model's own algebra, and was confirmed. That is what a test that can detect being wrong looks like when it fires. |

## 4. Statements that must not be upgraded

- **Anything about EBU stability, convergence or damping.** Neither study shows
  any. Stage A cycled perpetually; Stage B was still drifting at horizon end.
- **Any claim that the difference vanishes.** Stage B shows it shrinking, not
  reaching zero. It remained negative in 61/64 replicates in the final block.
- **Deadlock discussion (Ch 45).** Zero deadlock ticks in both studies. It stays
  hypothetical.
- **Forcing-intensity dependence.** One fixed amplitude `q0 = 1` by design.
- **Ch 41, path attribution.** Untouched. Exact closure remains arithmetic and
  not entitlement.
- **Ch 57-60**, historical engine, calibration, loss boundary. Untouched; both
  studies were lossless with `C_G = 0`.

## 5. The methodological point worth adding

Stage A and Stage B together make a point the books already gesture at, now with
evidence from this programme:

- Stage A's primary test returned `p ≈ 6e-39` and was **near-uninformative**,
  because EBU accounting guaranteed `V <= D` while the control was unbounded, so
  the ordering was forced in 128/128 pairs.
- Stage B corrected the normalization to a common physical bound `V_max`, under
  which both arms lie in `[0,1]` and their ranges overlap. Its `p ≈ 1e-19` is a
  **weaker number carrying far more information**.

Ch 55 is the natural home. The lesson is that a structurally bounded endpoint
can manufacture overwhelming significance without scientific content, and that
the remedy is a treatment-independent normalization chosen before execution.

A second point belongs beside it: Stage B's effect was statistically
unambiguous yet sat essentially **at** the preregistered practical threshold
(median -0.0559 against `delta_meaningful = 0.05`, CI `[-0.0616, -0.0503]`) and
fell **below** it in the final two blocks. Declaring a magnitude threshold in
advance is what made that readable.

## 6. Where updates would belong

1. **Ch 43** — the sharpest change: capacity accumulation weakens the gate.
2. **Ch 61** — cite the registered long-run study against its own line 11.
3. **Ch 55** — the two methodological examples in section 5.
4. **Ch 44, 45** — narrow quantified observations, each bounded to
   "one synthetic three-cell lossless world at one forcing amplitude".

Nothing in Part I requires change. Stage B alters no definition, theorem or
mathematical statement.

## 7. Preconditions before any book edit

- A separately authorized book stage; this task modified no manuscript.
- Scoping language of section 4 preserved verbatim in any new sentence.
- No chapter may cite Stage B as evidence for stability, convergence, or as
  justification for a capacity mechanism the programme has not adopted. The
  alternatives in `NEXT_STUDY_MECHANISM_ALTERNATIVES_PACKET.md` are candidate
  future models and must not appear as current design.
