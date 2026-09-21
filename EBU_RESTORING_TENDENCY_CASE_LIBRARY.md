# EBU restoring-tendency case library

**Version 1.1. A versioned permanent benchmark suite, not a planning note.**

This library defines **questions and environments**. It never defines expected
or favourable answers. A case is a disturbance and a measurement protocol; what
any mechanism does when subjected to it is a result, recorded elsewhere.

---

## 0. Governance

**Stable identifiers.** Every case has a permanent identifier `RT-Cnn`. An
identifier is never reused, never renumbered and never silently redefined.

**Mechanism independence.** Each case freezes its *physical question* —
disturbance, menu, measurement — separately from any EBU mechanism. Capacity
V1, Capacity V2, topology variants, factor-potential variants and any future
mechanism are **subjected to the same cases**. A mechanism variant may not
introduce a new scenario tailored to itself in place of an applicable existing
case; if an existing case is applicable, it must be run.

**Amendment rules.**
- Adding a new case: increment the minor version, append a new `RT-Cnn`.
- Clarifying wording without changing the physical content: minor version.
- Changing a case's disturbance, menu or measurement: this creates a **new
  identifier**, and the old one is retained and marked `SUPERSEDED-BY`. Results
  recorded against the old identifier remain valid for the old case.
- A case is never deleted. Retirement is a status, not an erasure.

**Results are preserved by mechanism and version.** `results/case_library/`
holds one record per (case, mechanism, mechanism version, run). Section 15
defines the ledger schema. A later system is compared against **exactly the
same disturbances** as an earlier one, or the comparison is not made.

**No expected answers.** Each case states a falsification question and what
would count as regulatory failure *in the registered failure vocabulary*. It
does not state what any mechanism is expected to do. Sections reading "what
must not be assumed" exist to keep it that way.

**Books.** The canonical worked examples of these cases are intended to become
the backbone of the explanatory books. A worked example may be written only
from a recorded result, never from an anticipated one.

**Status of this version: DEFINED, NOT YET EXECUTED.** No case below has a
registered run. The existing registered homeostasis study partially covers
`RT-C03`, `RT-C04`, `RT-C08`, `RT-C09` and `RT-C10`; those overlaps are noted
per case and are **not** recorded as case-library runs, because the case
protocols did not exist when that study was frozen.

**Version 1.1 amendment.** Section 3A adds fourteen demand-driven cases,
`RT-C13`–`RT-C26`, for the corrected economy in
`DEMAND_DRIVEN_EBU_SCIENTIFIC_CONTRACT.md`. No existing case is altered,
renumbered or retired: `RT-C01`–`RT-C12` keep their physical questions exactly,
and any mechanism claiming homeostatic properties in the arbitrary-action
environment is still measured against them. The demand-driven cases are
*additional* questions about an environment the earlier cases do not describe,
not replacements for them. As everywhere in this library, they define
disturbances and measurements and never expected answers.

## 1. Shared synthetic world

Unless a case says otherwise, the environment is the registered synthetic
world. **All dimensions are synthetic and carry no real-world calibration.**

| item | value |
|---|---|
| cells | 3, complete directed topology |
| conserved quantity | dimensionless stock, `M = 30` synthetic units |
| reference `x*` | `(10, 10, 10)` |
| scales `sigma` | `(1, 1, 1)` synthetic units |
| action menu | transfers of `q = 1`, groups of at most 2 |
| deviation ruler | `V = (1/2) sum_i ((x_i - x*_i)/sigma_i)^2`, `R^2 = 2V` |
| physical constraints | `x_i >= 0`, `sum_i x_i = M` — the only real boundaries |
| mandatory action | frozen; no abstain, wait or no-op in any case |

Reported quantities are defined in `EBU_RESTORING_TENDENCY_FOUNDATION.md`:
`dV_ext`, `dV_actor = -E`, `dV_total`, `D_A`, `D_T`, and the occupancy
diagnostics `O95`/`O99`.

---

## 2. Environment cases

### RT-C01 — small isolated shock

- **Physical story.** A minor local disruption moves one synthetic unit between
  two cells; nothing further happens.
- **Forcing.** One conservative transfer of `q = 1` at `t = 0`; `u_t = 0`
  thereafter.
- **Menu.** Standard.
- **Policy.** All four; see `RT-C08`–`RT-C10`.
- **Measured.** `D_A` and `D_T` at the post-shock state; first return to
  `V = 0`; time to first re-entry into `H95`; whether the state is left
  displaced.
- **Falsification question.** From a displacement of one quantum, does the
  action process move inward at all?
- **Regulatory failure.** `D_T >= 0` at the post-shock state, or no return
  within the frozen horizon.
- **Must not be assumed.** That a one-quantum displacement is recoverable at
  all: whether the menu permits exact reversal is a property of the quantum
  ratio, not a given.

### RT-C02 — large isolated shock

- **Physical story.** A severe one-off disruption concentrates stock, then
  stops.
- **Forcing.** One conservative transfer of `q >> 1` at `t = 0` (declare the
  magnitude per run; suggested synthetic values 5, 10, 20 units);
  `u_t = 0` thereafter.
- **Measured.** Peak `R^2`; return time to declared shells; `D_T` along the
  return path; whether capacity earned during return alters later behaviour.
- **Falsification question.** Does the restoring tendency survive a
  displacement far larger than one action quantum, where exact reversal is
  impossible in one tick?
- **Regulatory failure.** EXCURSION NON-RETURN within the frozen horizon, or
  `D_T >= 0` at the post-shock state.
- **Must not be assumed.** That recovery from a large shock is qualitatively
  the same as from a small one. The action menu is finite; a large displacement
  may require many ticks or may be unreachable.

### RT-C03 — repeated low-level demand

- **Physical story.** Persistent minor disturbance at low frequency.
- **Forcing.** Conservative transfer of `q = 1` with per-tick probability
  `p = 1/4`, edge drawn uniformly.
- **Measured.** `g_T(v)`, the operating region, late-window movement of the
  `V` distribution, occupancy diagnostics.
- **Falsification question.** Under mild continuing disturbance, does a
  recurrent operating regime form, and where?
- **Regulatory failure.** OUTWARD DRIFT across late windows, or LOSS OF
  RESTORING TENDENCY at large deviation.
- **Must not be assumed.** That an operating level exists, or that it is
  unique. The drift curve may cross zero more than once.
- **Overlap.** Partially covered descriptively by the registered homeostasis
  study at `p_force = 1/4`. Not recorded as a case run.

### RT-C04 — persistent medium demand

- **Physical story.** Sustained ordinary load.
- **Forcing.** As `RT-C03` with `p = 1/2` and `p = 1`, sharing one raw
  disturbance process so schedules nest.
- **Measured.** As `RT-C03`, plus the load-to-load comparison.
- **Falsification question.** How does the operating regime move with
  disturbance frequency?
- **Regulatory failure.** As `RT-C03`, and additionally HIGH-DEVIATION CAPTURE
  rising with load.
- **Must not be assumed.** That the response to load is monotone.
- **Overlap.** Partially covered by the registered study. Not recorded.

### RT-C05 — rare catastrophic impulse

- **Physical story.** A rare, severe event against an otherwise ordinary load.
- **Forcing.** Background as `RT-C03`, plus an impulse of `q_cat >> 1` at
  declared rare intervals.
- **Measured.** Pre-impulse operating state; peak deviation; return
  trajectory; whether the post-impulse operating regime differs from the
  pre-impulse one.
- **Falsification question.** Does a rare severe event permanently move the
  operating regime, or is it absorbed?
- **Regulatory failure.** A post-impulse operating regime that does not return
  to the pre-impulse one within the frozen horizon.
- **Must not be assumed.** That impulses are independent of the state they hit.
  Capacity accumulated before the impulse may change the response entirely.

### RT-C06 — multi-tick catastrophic forcing

- **Physical story.** A sustained emergency — disturbance far above the ordinary
  load for a declared number of consecutive ticks.
- **Forcing.** `q_cat` every tick for a declared window, then ordinary load
  resumes.
- **Measured.** Deviation during the window; `D_A` during the window; whether
  the actor layer remains restoring *while* being overwhelmed; physical
  boundary contact (`x_i = 0`).
- **Falsification question.** During sustained overwhelming disturbance, does
  the actor layer still pull inward even though the total drift is outward?
- **Regulatory failure.** `D_A >= 0` during the window, which would mean the
  action layer itself has stopped restoring, as distinct from being outmatched.
- **Must not be assumed.** That an outward total drift during an emergency is a
  failure. Per `EBU_RESTORING_TENDENCY_FOUNDATION.md` §12 it is not.

### RT-C07 — recovery after catastrophe ends

- **Physical story.** The emergency stops. The system is far from reference and
  its accounts are in an unusual configuration.
- **Forcing.** Continue `RT-C06`, then set the load to `RT-C03` or to zero.
- **Measured.** Return time and path; comparison with `RT-C02` from the same
  deviation but a *fresh* account state; explicit contrast of the two.
- **Falsification question.** Is recovery from a catastrophe the same as
  recovery from an equally large fresh shock, or does the accumulated account
  state change it?
- **Regulatory failure.** EXCURSION NON-RETURN; or return behaviour materially
  worse than `RT-C02` from matched deviation.
- **Must not be assumed.** That deviation alone determines recovery. This case
  exists precisely because the state is `(x, B)`, not `V`.

### RT-C11 — topology damage / route removal

- **Physical story.** A transfer route becomes permanently unusable.
- **Forcing.** Ordinary load as `RT-C03`; at a declared tick, remove one or
  more directed edges from the topology for the remainder of the run.
- **Menu.** Regenerated from the damaged topology. The menu shrinks; mandatory
  action still applies to whatever remains.
- **Measured.** Operating regime before and after removal; `D_T` on the damaged
  topology; whether any state becomes unreachable; `PHYSICAL_NO_ACTION`
  incidence.
- **Falsification question.** Does the restoring tendency survive loss of
  action routes, and how much loss is tolerated?
- **Regulatory failure.** LOSS OF RESTORING TENDENCY after removal, or states
  from which no feasible action exists.
- **Must not be assumed.** That the reference remains reachable at all. Edge
  removal can make exact restoration impossible; that is a finding, not a
  failure of the mechanism.

### RT-C12 — resource scarcity preventing immediate restoration

- **Physical story.** The stock needed to restore is not where it is needed;
  restoration must be staged through intermediate transfers.
- **Forcing.** Initialize or drive the state so that one or more cells hold
  less than one action quantum, so the restoring transfer is infeasible at its
  source.
- **Measured.** `NULL_FORCING` and infeasibility incidence; number of ticks of
  staging before the restoring action becomes available; `D_T` during the
  staged period.
- **Falsification question.** When restoration requires several ticks of
  preparation, does the process still find its way inward?
- **Regulatory failure.** Indefinite staging without net inward progress, or
  HIGH-DEVIATION CAPTURE at the scarcity boundary.
- **Must not be assumed.** That a feasible path exists. Source-funded
  feasibility can make a needed transfer unavailable for many ticks.

## 3. Policy-axis cases

These are not separate environments. They cross with every environment case and
exist so that policy results are recorded under stable identifiers.

### RT-C08 — random actors

- **Policy.** `control_random` and `ebu_random`, run as a matched pair on the
  identical raw disturbance stream.
- **Falsification question.** Does EBU affordability produce a more restoring
  actor layer than no affordability constraint, from comparable states?
- **Regulatory failure.** `D_A^{EBU-R}(S) >= D_A^{CTRL}(S)` over the
  large-deviation states represented.
- **Must not be assumed.** That the comparison is stable in accumulated
  capacity. It provably is not, under V1.

### RT-C09 — aligned actors

- **Policy.** `ebu_aligned`.
- **Falsification question.** Is `arg max E_G` the most restorative action
  available under affordability, at every state?
- **Regulatory failure.** Any state where an affordable candidate leaves a
  lower post-action `V` than the selected one.
- **Must not be assumed.** That good aligned behaviour is evidence of a good
  signal in general. Where the quantum ratio permits exact reversal, perfect
  behaviour is a theorem, not a measurement.

### RT-C10 — hostile actors

- **Policy.** `ebu_hostile`.
- **Falsification question.** Does affordability prevent persistent
  high-deviation capture under deliberately destructive choice?
- **Regulatory failure.** HIGH-DEVIATION CAPTURE, EXCURSION NON-RETURN, or
  drift worse than the unconstrained control.
- **Must not be assumed.** That a hostile actor will restore, ever, or that
  constraining its menu constrains its damage.

## 3A. Demand-driven cases (version 1.1)

These cases apply to any mechanism running the corrected demand-driven economy,
in which an actor chooses only among complete, executable, irredundant plans
that serve a currently existing demand. They do **not** apply to the
arbitrary-action environment of sections 2 and 3, and results from the two
environments are never pooled.

### Shared demand-driven world

Unless a case says otherwise. **All dimensions are synthetic and carry no
real-world calibration.**

| item | value |
|---|---|
| resources | 2, on disjoint node sets, so independent components exist |
| coordinates | one stock per (resource, node); references and scales declared per run |
| accounts | held by **nodes**, so account sharing is a live coupling channel |
| routes | declared per resource, with hard capacity and efficiency `eta` |
| loss | `eta = 1` unless the case says otherwise; a lossy route must name its sink |
| service contract | complete service only; overshoot permitted; no partial service |
| admission | random compatible-subset, EBU-blind |
| mandatory action | frozen; no voluntary no-op in any case |
| capacity | V1 unless the case declares a variant; `B_i(0) = 0` |
| demand set | unordered; no FIFO, deadline, priority or service order |

Reported quantities are those of `EBU_RESTORING_TENDENCY_FOUNDATION.md`, plus
four demand-driven ones that every case must report:

- the epoch-status distribution over `NO_ACTIVE_DEMAND`,
  `NO_COMPLETE_PHYSICAL_PLAN`, `ALL_PLANS_EBU_UNAFFORDABLE`, `EXECUTED`;
- the economic-outcome distribution over `E_SERVED`,
  `E_REJECTED_PHYSICAL_SCARCITY`, `E_REJECTED_INCOMPATIBLE`,
  `E_ADMITTED_BUT_EBU_UNAFFORDABLE`;
- the **stuck-component fraction**: epochs in which some component holds an
  unserviceable member (finding F-1);
- the per-owner capacity distribution, not only `B_total` (finding F-3).

### RT-C13 — economic demand only

- **Physical story.** The physical system starts at its reference and is never
  disturbed. All obligations are external economic requests.
- **Demand.** `E` arrivals under a declared law; no natural disturbance.
- **Measured.** `D_A`, `D_T`; whether `V` departs from zero and whether it
  returns; the economic-outcome distribution; per-owner capacity.
- **Falsification question.** When the only reason to act is economic, does the
  physical state stay near its reference, drift, or settle somewhere else?
- **Regulatory failure.** OUTWARD DRIFT across late windows, or EXCURSION
  NON-RETURN within the frozen horizon.
- **Must not be assumed.** That economic service is physically neutral. Serving
  a delivery moves stock, and at the reference every such move raises `V`.

### RT-C14 — physical demand only, under a demand-conditioned menu

- **Physical story.** Natural disturbance only; no economic demand ever
  arrives.
- **Demand.** `P` derived from the state each epoch.
- **Measured.** `D_A`, `D_T`, the operating region, return times, occupancy
  diagnostics; menu sizes.
- **Falsification question.** Restricting the menu to demand-serving plans is a
  restriction. Does a restoring tendency survive it?
- **Regulatory failure.** LOSS OF RESTORING TENDENCY at large deviation, or
  OUTWARD DRIFT.
- **Must not be assumed.** That this reproduces `RT-C03`/`RT-C04`. The menus
  differ; the environments are not comparable and results are not pooled.

### RT-C15 — simultaneous economic and physical demand

- **Physical story.** Both demand classes are continuously active.
- **Demand.** Declared arrival law and declared disturbance law, independent.
- **Measured.** All four required distributions; whether either class is
  systematically served later than the other; component sizes.
- **Falsification question.** With both classes live in one unordered
  obligation set, does the system regulate, and is either class starved?
- **Regulatory failure.** Any registered failure term; plus a declared
  starvation flag if one class's completion rate is systematically lower.
- **Must not be assumed.** That the two classes are independent in effect. They
  compete through stocks, routes and accounts.

### RT-C16 — economic scarcity

- **Physical story.** Requests routinely exceed what physically exists.
- **Demand.** An arrival law whose quantity alphabet includes values beyond
  what the quanta and plan-size cap can deliver.
- **Measured.** Scarcity-rejection rate; whether rejection is decided before
  any EBU value exists; the physical trajectory alongside it.
- **Falsification question.** Does the system distinguish physical
  impossibility from economic unaffordability, and does scarcity perturb the
  physical state at all?
- **Regulatory failure.** Any scarcity outcome recorded as an EBU rejection, or
  any truncation, regeneration or top-up of an oversized request.
- **Must not be assumed.** That scarcity is rare, or that it is harmless.

### RT-C17 — EBU unaffordability

- **Physical story.** Physical plans exist and none is affordable.
- **Demand.** Declared so that negative-EBU service is the only option for some
  component, at low capacity.
- **Measured.** `ALL_PLANS_EBU_UNAFFORDABLE` epoch fraction; how long a demand
  stays admitted-unaffordable; per-owner capacity; whether it is ever served.
- **Falsification question.** Does unaffordability act as a brake that protects
  the physical state, a stall that freezes the economy, or neither?
- **Regulatory failure.** The registered failure terms; plus a declared
  permanent-stall flag.
- **Must not be assumed.** That unaffordability is protective. It is a
  constraint on actors, not a goal of the mechanism.

### RT-C18 — economic action creating physical demand

- **Physical story.** Serving an economic request depletes a source below its
  reference, creating new physical demand — the wave.
- **Demand.** An arrival law whose service necessarily draws a source below
  reference.
- **Measured.** Wave incidence per served economic demand; the induced `P`
  series; whether induced demand is itself served; `D_T` along the induced path.
- **Falsification question.** Does economic activity generate physical demand
  that the same mechanism then resolves, or does it accumulate?
- **Regulatory failure.** OUTWARD DRIFT driven by induced demand, or
  EXCURSION NON-RETURN.
- **Must not be assumed.** That every economic action creates a wave. Whether
  it does depends on the plan chosen, and therefore on the policy.

### RT-C19 — loss-generated physical demand

- **Physical story.** A lossy route wastes part of what it carries; the waste
  is represented explicitly.
- **Demand.** As declared; at least one route with `eta < 1` and a named sink.
- **Measured.** Cumulative loss; the reachable potential floor; the recurrent
  level actually occupied; the gap between them.
- **Falsification question.** With the reference unreachable by construction,
  is there still a restoring tendency **toward the reachable floor**?
- **Regulatory failure.** Movement away from the reachable floor across late
  windows.
- **Must not be assumed.** That restoring tendency can be measured against
  `x*` here. It cannot. Finding F-2 shows mandatory complete service can hold
  the system strictly above the floor, and a floor-relative definition must be
  declared before this case is run.

### RT-C20 — external natural shock plus economic demand

- **Physical story.** A catastrophic natural impulse lands while economic
  obligations are outstanding.
- **Demand.** Declared disturbance impulse at a declared epoch, with an active
  arrival law.
- **Measured.** Peak `R^2`; return time; admission behaviour during the
  excursion; whether outstanding economic demands become unserviceable.
- **Falsification question.** Does an economic load change the system's
  response to a shock?
- **Regulatory failure.** EXCURSION NON-RETURN, or a stuck-component fraction
  that does not recover after the impulse ends.
- **Must not be assumed.** That the shock response is separable from the
  economic load.

### RT-C21 — hostile plan selection

- **Physical story.** Actors answer every obligation by the most physically
  damaging complete plan available.
- **Policy.** `argmin E_G` over affordable complete plans.
- **Measured.** All required distributions; reachable damage; comparison against
  the no-EBU comparator on the **same** admitted components.
- **Falsification question.** How far can an adversary push the system when it
  must still serve every obligation completely?
- **Regulatory failure.** Registered failure terms.
- **Must not be assumed.** That the corrected hostile actor is safer than the
  arbitrary-action one. Its menu is narrower and its every action is
  demand-justified, but no direction may be presumed, and the earlier adverse
  finding is not evidence here.

### RT-C22 — aligned plan selection

- **Policy.** `argmax E_G` over affordable complete plans.
- **Measured.** As `RT-C21`.
- **Falsification question.** Does maximizing EBU within a demand-serving menu
  point toward the reference?
- **Regulatory failure.** Registered failure terms.
- **Must not be assumed.** That the aligned arm is trivially perfect. The
  endpoint-saturation theorem's hypothesis is **not** satisfied in this
  environment: plans are multi-action and overshoot is permitted, so exact
  reversal need not be available or uniquely maximal.

### RT-C23 — random plan selection

- **Policy.** Uniform over affordable complete plans.
- **Measured.** As `RT-C21`, plus the capacity-regime sweep of section 5.
- **Falsification question.** Does the affordability gate alone produce a
  restoring tendency when the menu is demand-conditioned?
- **Regulatory failure.** Registered failure terms.
- **Must not be assumed.** That the gate erodes with accumulated capacity here
  as it provably does on the arbitrary-action menu. That is a theorem about a
  different menu.

### RT-C24 — closed-cycle no issuance

- **Physical story.** An actor-only sequence that returns the represented state
  exactly to its start.
- **Demand.** Whatever drives the sequence; no external injection during the
  window.
- **Measured.** `sum_t E_t`; `delta B_total`; the per-owner distribution; the
  capacity-source residual.
- **Falsification question.** Does the mechanism issue net capacity over a
  closed cycle?
- **Regulatory failure.** Any nonzero `delta B_total` under the theorem's
  hypotheses. This is a **conformance** case: a failure is an implementation
  defect, not a scientific result.
- **Must not be assumed.** That a path with loss is a closed cycle. It is not,
  and must be classified separately.

### RT-C25 — competing economic-demand admission

- **Physical story.** Several requests arrive that cannot all be met together.
- **Demand.** At least two arrival slots, with a quantity alphabet that makes
  joint service impossible at realistic stock levels.
- **Measured.** Distribution over admitted subsets; incompatible-rejection
  rate; whether any destination or quantity is systematically favoured.
- **Falsification question.** Is admission genuinely arbitrary, or does some
  quantity, destination or count become privileged in practice?
- **Regulatory failure.** Any detectable dependence of the admitted subset on
  EBU, capacity or the potential; or a systematic preference over quantity or
  customer count.
- **Must not be assumed.** That uniform choice over inclusion-maximal subsets
  is uniform over demands. It is not, and the induced per-demand rates must be
  reported rather than assumed flat.

### RT-C26 — joint multi-demand plan

- **Physical story.** One action contributes to several obligations at once.
- **Demand.** Declared so that a single action serves at least two demands.
- **Measured.** Frequency of multi-demand actions; provenance breadth; explicit
  check that no service credit is doubled; component sizes.
- **Falsification question.** Does the mechanism handle overlapping obligations
  without double-crediting service or EBU?
- **Regulatory failure.** Any demand recorded as served by a plan whose net
  increment does not meet its requirement; any receipt sum differing from
  `E_G`. This is a **conformance** case.
- **Must not be assumed.** That overlapping obligations are rare.

## 4. Applicability matrix

`X` = applicable and should be run for any mechanism claiming homeostatic
properties. `o` = applicable where the mechanism declares a capacity or account
layer.

| case | V1 | V2 | topology variants | factor-potential variants |
|---|---|---|---|---|
| RT-C01, RT-C02 | X | X | X | X |
| RT-C03, RT-C04 | X | X | X | X |
| RT-C05, RT-C06, RT-C07 | X | X | X | X |
| RT-C11 | X | X | X | X |
| RT-C12 | X | X | X | X |
| RT-C08, RT-C09, RT-C10 | X | X | X | X |
| capacity-regime sweep (§5) | o | o | o | o |

Demand-driven cases apply only to mechanisms running the corrected economy.
`—` means the case is not defined for that environment, which is a statement
about applicability and not about quality.

| case | demand-driven V1 | demand-driven V2 | arbitrary-action mechanisms |
|---|---|---|---|
| RT-C13, RT-C14, RT-C15 | X | X | — |
| RT-C16, RT-C17 | X | X | — |
| RT-C18 | X | X | — |
| RT-C19 | X | X | — |
| RT-C20 | X | X | — |
| RT-C21, RT-C22, RT-C23 | X | X | — |
| RT-C24, RT-C26 | X | X | — |
| RT-C25 | X | X | — |
| capacity-regime sweep (§5) | o | o | o |

`RT-C19` additionally requires a declared floor-relative definition of
restoring tendency before it may be run; see finding F-2.

## 5. Mandatory capacity-regime reporting

Any mechanism with an account layer must report every applicable case at **at
least two declared capacity regimes**, because a single regime is provably
insufficient to characterise V1: its restoring advantage is a property of the
low-capacity regime and vanishes identically above a computable threshold.

Minimum: the zero-account regime, and a regime at or above the mechanism's
gate-inactivity threshold if one exists. If no such threshold exists, that must
be stated and demonstrated.

## 6. Results ledger

Machine-readable companion: `ebu_restoring_tendency_case_library.json`, with
one record per `(case_id, mechanism, mechanism_version, run_id)`. Required
fields:

```
case_id              RT-Cnn
case_library_version the version of this document the run was executed under
mechanism            e.g. capacity_v1 / capacity_v2
mechanism_version    the mechanism's own identity string
code_identity        package hash at execution
preregistration      commit or tag, or "exploratory"
evidence_class       registered | exploratory | conformance | theorem
capacity_regime      declared regime label and B specification
measurements         the case's declared measured quantities
failure_flags        any registered failure vocabulary terms that fired
notes                limitations; never an interpretation of another mechanism
```

**A record is never edited after it is written.** A correction is a new record
referencing the old one.

## 7. Current ledger status

**Empty.** No case has a recorded run under any mechanism, in either
environment. The registered homeostasis study overlaps `RT-C03`, `RT-C04`,
`RT-C08`, `RT-C09` and `RT-C10` descriptively, but the case protocols did not
exist when it was frozen, so nothing from it is entered as a case-library
result.

The demand-driven conformance gate and rehearsal likewise enter **nothing**.
Conformance establishes that the implementation obeys its contract; the
rehearsal is explicitly non-confirmatory. Neither is a case run, and neither
may be recorded as one. `RT-C24` and `RT-C26` are marked conformance cases
because a failure of either is an implementation defect, but they still require
a declared run under a declared mechanism version before a record exists.
