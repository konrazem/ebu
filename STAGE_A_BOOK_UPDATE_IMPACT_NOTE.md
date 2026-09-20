# Stage-A book update impact note

Status: **impact analysis only. No manuscript is modified by this task.**

The books were regenerated and reconciled around the Local Gaussian direction
and are frozen for implementation work. This note records what the registered
Stage-A result would change if and when a separately authorized book stage
opens. It is deliberately conservative: a registered result on one synthetic
3-cell world licenses very few sentence changes.

Source of the result: `STAGE_A_REGISTERED_REPORT.md`, preregistration
`025eee1efaa0723d04234cfe5ae9d1a319de7206`. Chapter references are to
`books/part_ii_integrated/` on `codex/book-series-eight-parts`.

## 1. Statements that could become observed results

| Location | Current status | What Stage A now supports |
|---|---|---|
| Ch 42 `ch:cycles`, l.84 — "It does not prove that actors prefer recovery over cycling or refusal." | correctly stated nonclaim | The nonclaim stands, but an observation can now be *added*: in this world the random affordable actor cycled in 128/128 replicates and refused in none. The sentence should not be deleted; it is still true that closure does not prove preference. |
| Ch 43 `capacity accounts`, l.30 — "Whether that freedom enables useful later action or merely supports cycles is precisely the sort of question that remains for research." | open question | For this world the question now has an answer: it supported cycles. Executed events split a median 62 positive-value to 60 negative-value, and trajectories left equilibrium a median of 46 times. This is a *scoped* answer for one world, not a general one, so the sentence becomes "remained open until Stage A, which for the smallest world found ..." rather than being removed. |
| Ch 45 `feasibility and the long-run boundary`, ll.57-58 — lists distance occupation, recovery time, cycling, refusal, distribution as things that "can genuinely differ" | anticipated observables | All five are now measured quantities with registered definitions and values: equilibrium occupancy 0.252 vs 0.000, first hitting time 3.5 vs 22 ticks, cycling 128/128 vs 9/128, refusal zero in both arms. |
| Ch 48 `the smallest honest Gaussian world` | described but not instantiated | The described world now exists as executable code with a hand-checkable fixture, and has been run under registration. The chapter can cite the world's identity hash and the worked arithmetic. |
| Ch 54 `randomness, paired controls and reproducibility` | design argument | Byte-identical replay from seeds alone is now demonstrated, and the behavioural blindness property (changing every Gaussian scale changes every EBU value but no control choice) is a passing test rather than an intention. |
| Ch 62 `a worked audit` | worked example | The three-cell walkthrough now has a committed exact counterpart whose residuals are literally zero, suitable for direct citation. |

## 2. Statements that remain hypotheses and must not be upgraded

- **Anything about EBU stability.** Stage A found no convergence. The EBU arm
  never settled: zero replicates classified `REACHED_AND_STAYED`. No sentence
  anywhere may move from hypothesis to result on the strength of this study.
- **Ch 41 `a path attribution is not an entitlement`.** Untouched. Exact
  closure of `sum_a R_a = E_G` was confirmed at zero residual, which is
  arithmetic and remains explicitly not causal identification, fairness,
  ownership or spending entitlement.
- **Ch 45 route-blocking and deadlock.** Stage A observed **zero** deadlock
  ticks, so it provides no empirical support either way. Deadlock discussion
  stays hypothetical until Stage B.
- **Ch 61 `what a long-run study could show`.** Stage A is a single-shock
  transient study, not a long-run study. Line 9's "may recover, cycle, become
  trapped or refuse" keeps its conditional mood; only "cycle" has any
  observation behind it, and only for this world.
- **Ch 57-60**, historical engine, calibration and loss boundary. Untouched.
  Stage A used a lossless world with `C_G = 0` and says nothing about loss.
- **Any economic or institutional reading.** Out of scope entirely.

## 3. The limitation that most affects the book

Stage A's headline number is a p-value of roughly 5.9e-39, and the book must
**not** quote it as a strong result. The registered report establishes that the
paired ordering was structurally forced in 128/128 pairs: `A_EBU <= 1` follows
from `V + sum B = D` with `B >= 0`, and the control exceeded 1 in every
replicate, so the test had almost no power to return anything but unanimity.

Any future chapter text drawing on Stage A must carry that decomposition with
it. A book sentence of the form "EBU significantly outperformed the control"
would be a misreading of the study's own report. The defensible sentences are:

- the unconstrained control diverged far above the injected disturbance
  (median normalised cumulative deviation 14.97 versus 0.244); and
- the constrained arm stayed within a narrow band *partly by construction*, and
  cycled perpetually rather than converging.

This is also a worked illustration of a methodological point the books already
make: a structurally bounded endpoint can manufacture overwhelming significance
without scientific content. Ch 55 `tests that can genuinely detect being wrong`
is the natural home for it, as a real example from this programme rather than a
hypothetical.

## 4. Where updates would belong

1. **Ch 48 and Ch 62** — smallest concrete changes: cite the executed world and
   the exact worked audit.
2. **Ch 55** — add the structurally-forced-endpoint example from section 3.
3. **Ch 42, 43, 45** — narrow scoped observations, each explicitly bounded to
   "one synthetic three-cell lossless world, one shock magnitude".
4. **Ch 61** — note that a long-run study is prepared but not run, referencing
   `STAGE_B_PREREGISTRATION_CANDIDATE.md`, without implying its outcome.

Nothing in Part I requires change; Stage A alters no definition, theorem or
mathematical statement.

## 5. Preconditions before any book edit

- A separately authorized book stage. This task did not modify books.
- The scoping language of section 2 preserved verbatim in any new sentence.
- No chapter may cite Stage A as evidence for stability, convergence,
  attribution legitimacy, or any claim about loss, service or an economy.
