# Capacity-V2 requirements

Formalizes the target a replacement affordability mechanism must hit, **before**
any mechanism is designed. Derived from `CURRENT_CAPACITY_FAILURE_THEOREMS.md`.

Notation: `V_i = (1/2)((x_i - x*_i)/sigma_i)^2`, `V = sum_i V_i`, `B_i` the
owner capacity, `J` the external deviation ledger, `Delta B_i` the same-event
netted owned receipts of an executed group, `R_max` the receipt bound of
Theorem 6.

Each requirement is stated so it can be checked, and is marked as a **hard
constraint** (a candidate failing it is rejected) or a **target** (a candidate
failing it is admissible but weaker).

## Hard constraints

**R1 — EBU calculates; actors choose.** *Hard.* No mechanism may rank, score or
select actions by EBU value, potential, marginal or distance from reference.
Check: the chooser receives opaque candidate identities and a count only, as it
does now.

**R2 — No intelligent homeostatic ranking.** *Hard.* Affordability is a
predicate, never a preference order. Check: the admissibility test returns a
boolean per candidate and is invariant to permuting the candidate list.

**R3 — Negative-EBU actions require genuinely available capacity.** *Hard.* If
`Delta B_i < 0` for owner `i`, execution requires that owner to hold sufficient
capacity by a rule that is not vacuous. Check: there exist reachable states in
which a negative-EBU group is refused.

**R4 — No borrowing, no negative balance.** *Hard.* `B_i >= 0` at all times.

**R9 — No global liquidity pool.** *Hard.* No shared account, no transfer
between owners, no redistribution.

**R10 — No arbitrary issuance.** *Hard.* Capacity may arise only from executed
action receipts. No genesis grant, refill, subsidy or periodic credit.

**R11 — Any disappearance or saturation is explicitly accounted.** *Hard.*
If capacity ceases to be spendable, the amount must enter a declared ledger
term. Nothing disappears unaccounted.

**R12 — Exact accounting remains possible.** *Hard.* An exact identity must
close at zero tolerance on every tick. The V1 identity `V + sum B = J` **is not
itself sacred**; an extended exact identity such as

    V_t + sum_i B_i(t) + C_t = J_t

with `C` a declared monotone retirement ledger is fully acceptable. What is
required is exactness, not the particular form.

**R13 — Historical reproducibility.** *Hard.* Stage-A and Stage-B mechanism,
code identity, artifacts and preregistrations remain byte-reproducible. V2 must
be a separate model path, never an in-place edit.

**R14 — Falsifiable with random actors.** *Hard.* The mechanism must be testable
under the same random-choice policy, with outcomes that could come out against
it.

**R15 — No tunable constant without physical or statistical interpretation.**
*Hard.* Any scalar in the rule must be derivable from declared model objects
(reference, scales, quanta, topology, potential). A free parameter chosen to
make results look good is disqualifying. Note that a rule with *no* new scalar
is strictly preferable to one with a derived scalar.

## Targets

**R5 — Positive EBU may create usable capacity.** *Target.* Restorative work
should be able to fund later action; a rule that retires everything instantly is
admissible but degenerate.

**R6 — Bounded self-created destructive ability.** *Target, and the direct
answer to Corollary 1.1.* Repeated self-created damage and repair must not
accumulate unlimited net new destructive ability. Desired provable form: for a
closed local cycle returning cell `i` to its starting coordinate,
`Delta B_i <= 0` unless new external deviation entered.

**R7 — Stationary disturbance must not cause unbounded capacity.** *Target, and
the direct answer to Theorem 5.* Desired provable form: `sum_i B_i(t) <= K` for
some `K` derived from the declared model, uniformly in `t`, under stationary
forcing.

**R8 — Locality.** *Target, strongly preferred.* Capacity semantics should
depend only on a cell's own factor, or on the factors its actions touch. A rule
requiring global `V`, a global episode registry, or knowledge of other cells'
balances is a significant demerit.

## Derived success criteria

From the theorems, a candidate that satisfies the hard constraints should be
judged on whether it can *prove*:

- **T-A (bounded capacity).** `sum_i B_i(t) <= K` with `K` derived, not chosen.
- **T-B (absorbing reference).** At `x = x*`, no group with `delta_G != 0` is
  affordable — which by Theorem 2 is exactly what V1 fails.
- **T-C (no free cycle).** A closed local excursion nets `Delta B_i <= 0`.
- **T-D (exact extended ledger).** `V + sum B + C = J` holds at zero tolerance,
  with `C` monotone nondecreasing.

## Explicit non-requirements

- **Convergence is not required.** Per the controlling distinction, success may
  be *persistent bounded protection* rather than damping to exact equilibrium.
  Both must be reported separately and neither may be redefined after results.
- **Beating the control on every metric is not required.**
- **Preserving `V + sum B = J` in its V1 form is not required** (see R12).

## What would falsify a candidate

A candidate is falsified if, under registered execution with random actors, it
shows unbounded `sum_i B_i` under stationary forcing, or a vanishing
affordability rejection rate, or requires a constant with no derivation, or
breaks exact accounting, or is shown to rank actions by value.
