# Local Gaussian EBU — Stage-A preregistration CANDIDATE

Status: **candidate for author review. NOT FROZEN. NOT AUTHORIZED TO EXECUTE.**

This document proposes the Stage-A study. Executing it is roadmap gate G4 and
requires separate author authorization. Nothing here is evidence, and the
harness passing its conformance suites is not evidence that EBU is stable.

Implementation base: branch `gaussian/stage-a-environment`, decision packet
`LOCAL_GAUSSIAN_EBU_STAGE_A_DECISION_PACKET.md`, protocol id
`EBU-GAUSSIAN-STAGE-A-SINGLE-SHOCK-v1`.

## 1. Question

After one declared conservative disturbance, with external forcing then OFF,
how does a world of randomly-acting cells behave when their actions are
filtered by EBU capacity affordability, compared with a matched world where
the same random actors are filtered only by physical feasibility?

EBU calculates; actors choose. The study measures a *dynamical consequence of
an accounting constraint*, not the performance of a controller.

## 2. Declared world

| Item | Proposed value | Basis |
|---|---|---|
| Cells `n` | 3 | smallest world with both disjoint and shared-coordinate groups |
| Reference `x*` | (10, 10, 10) | hand-checkable; sets `M = 30` |
| Scales `sigma` | (1, 1, 1) | unit geometry; no empirical calibration claimed |
| Declared mass `M` | 30 | `sum(x*_i)`, so the reference is mass-compatible |
| Topology | complete directed graph, 6 edges | no topological asymmetry to confound the arms |
| Quantum set | {1} | one finite quantum; menu restriction, not a divisibility claim |
| `m_max` | 2 | admits simultaneous groups and pair interaction |
| Candidate groups | 21 (6 singletons + 15 pairs) | exhaustive deterministic enumeration |
| Upper bound | none | the fixed-mass simplex already bounds the state |
| Initial state | `x_0 = x*`, `V_0 = 0`, `B_i(0) = 0`, `J_0 = 0` | task section 28 |
| Shock | one draw, `u_0 = s(e_p - e_q)`, `s` from {2} | conservative, `1^T u = 0` exactly |
| Horizon | 64 ticks per run | the conformance ceiling; a longer horizon needs its own authorization |
| Replicates | 64 actor seeds per arm | fixed in advance; see section 6 on seeds |

All values are exact rationals under the ratified G0 Exact Arithmetic
Decision. No parameter may be changed after any trajectory is inspected.

## 3. Arms

- **Arm A** `ebu_affordability_random_actor`: physical feasibility, then EBU
  capacity affordability, then uniform random choice.
- **Arm B** `physical_feasibility_random_actor`: physical feasibility, then
  uniform random choice. The matched physical-random **scientific control**,
  not an inferior controller.

Both arms share the identical world, menu, feasibility rule, canonical
ordering, forcing seed and actor seed. Because Stage A forces only at `t = 0`
from the identical initial state `x*`, the applied shock is provably identical
in both arms: this is common applied forcing, not merely common raw draws.
Arm B records a signed shadow ledger so the accounting identity stays
auditable; it is never used to filter.

## 4. Fixed audit identities

Every tick of every run, at exact equality and zero tolerance:

1. `V(x_t) + sum_i B_i(t) = J_t` with `J_t = D_shock` constant for `t >= 0`.
2. `sum_i x_i(t) = M`.
3. `x_i(t) >= 0`.
4. `sum_a R_a = E_G` for the executed group.
5. Arm A only: `B_i(t) >= 0`.

A violation of any of these is a **software or mathematical conformance
failure** and invalidates the run. It is not a scientific finding.

## 5. Registered metrics

Defined before execution, computed per run and reported per arm as
distributions, never as a single headline number.

| Metric | Definition |
|---|---|
| `V_final` | `V(x_T)` at the horizon |
| `V_min`, `V_max` | extremes of `V(x_t)` over the run |
| `V_mean_occupancy` | `(1/T) sum_t V(x_t)`, deviation occupancy |
| `time_to_half` | first `t` with `V(x_t) <= D_shock / 2`, else censored |
| `time_to_reference` | first `t` with `V(x_t) = 0`, else censored |
| `returns_to_reference` | count of ticks with `V(x_t) = 0` |
| `deadlock_ticks` | ticks with status `DEADLOCK` |
| `executed_ticks` | ticks with status `EXECUTED` |
| `distinct_states`, `max_revisits` | `(V, sum B)` occupancy, for cycling |
| `balance_concentration` | `max_i B_i(T) / sum_i B_i(T)`, or 0 if the total is 0 |
| `affordable_fraction` | mean `len(affordable)/len(feasible)` per tick |

Censoring is reported explicitly. A censored `time_to_reference` is recorded
as censored, never as the horizon and never dropped.

## 6. Seeds and blindness disclosure

Seeds must be fixed before execution. Proposed rule: forcing seed `F = 1`, and
actor seeds `A_k = 1000 + k` for `k = 0..63`, per arm-matched pair.

**Disclosure, offered so the author can judge blindness rather than being
asked to trust it.** During implementation the harness was run for software
conformance on this same 3-cell world at seeds `(11, 29)`, `(11, 30)`,
`(11, 31)` and `(3, 7)`, for at most 8 ticks, and those trajectories were
observed. The world parameters above were chosen before those runs, on the
stated minimality grounds, and were not adjusted afterwards. The proposed
seed set deliberately excludes every seed already observed. If the author
judges that observing any trajectory on this world compromises Stage-A
blindness, the correct remedy is to change the world or the seed rule now,
before freezing, not after seeing results.

No metric, threshold or outcome class below was chosen by inspecting any
trajectory.

## 7. Outcome classes

Declared in advance and mutually exclusive at the run level. All are
admissible results.

| Class | Criterion at the horizon |
|---|---|
| `REFERENCE_RECOVERY` | `V(x_T) = 0` |
| `PARTIAL_RECOVERY` | `0 < V(x_T) < D_shock` |
| `NO_IMPROVEMENT` | `V(x_T) >= D_shock` and no deadlock |
| `CYCLING` | `max_revisits >= 4` and `V` never settles |
| `DEADLOCK_TERMINAL` | the final 8 ticks are all `DEADLOCK` |

`REFERENCE_RECOVERY` is **not** the success condition of the study. It is one
observation among five.

## 8. Comparison and falsifiers

Primary comparison: the distribution of `V_mean_occupancy` in Arm A versus
Arm B across the 64 matched seed pairs, reported with the full paired
differences, not only a summary statistic.

The hypothesis under test is that the EBU capacity constraint changes
post-shock dynamics relative to matched physical-random behaviour. It is
falsified if:

1. the paired distributions are statistically indistinguishable under the
   preregistered test; or
2. Arm A's deviation occupancy is *higher* than Arm B's; or
3. Arm A reaches `DEADLOCK_TERMINAL` in a majority of runs while Arm B does
   not, and deviation occupancy does not improve.

Outcome 3 is a real possibility of this design: with zero genesis balances, an
owner can be unable to afford any action, and the honest result is deadlock.

**Boundedness is not a finding.** Both arms live on a bounded fixed-mass
simplex, so `V` is bounded above in both by construction. No claim of the form
"EBU keeps the system bounded" may be drawn from this study.

## 9. Non-claims

This study, whatever it shows, does not establish that EBU is stable, that the
capacity rule is causally or ethically correct attribution, that the
common-path receipt is a fair share, that the reference is an optimum, or that
any real economy behaves this way. It concerns one synthetic three-cell
lossless world with one shock and one declared potential.

A negative or null Stage-A result is not permission to change the model, and
does not authorize Stage B.

## 10. Open items requiring an author decision before freezing

1. **Empty-group menu membership.** The implementation keeps the empty group
   out of the uniform sampling menu, so deadlock stays observable and no
   arbitrary menu-size-dependent do-nothing mass enters the process. Including
   it is defensible and would change the stochastic process. Decision needed.
2. **Seed rule**, in light of the section 6 disclosure.
3. **Replicate count and horizon**, which set the cost.
4. **The statistical test** for section 8's primary comparison.

## 11. Execution preconditions

Before any Stage-A run:

- this document is frozen and hashed, and its id is supplied to
  `TickBudget.registered_study`, which currently fails closed without one;
- both conformance suites pass at the executing commit;
- the worktree is clean and the code identity is recorded in every log;
- the author authorizes gate G4 explicitly.

None of these is satisfied by this branch as it stands.
