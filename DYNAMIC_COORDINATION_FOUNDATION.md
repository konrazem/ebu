# Dynamic Coordination Foundation

**Status:** Analytical foundation checkpoint v0.1
**Date:** 2026-08-12
**Primary home:** Part VIII, *Dynamic Coordination Fields and Society Geometry*
**Purpose:** Freeze a minimal dynamic vocabulary, provisional deterministic
system model, objective discipline, static examples, theorem candidates,
falsifiers, and open problems before any framework specification,
implementation, or scientific execution.

## 1. Scope, authority, and claim status

This document is a Phase B analytical foundation note. It uses definitions,
algebra, dimensional reasoning, and hand-worked finite examples only. It does
not report an experiment, validate a coordination policy, prove a theorem, or
authorize implementation.

Its planning authority is:

- EBU_FUTURE_BOOKS_STRUCTURE.md; and
- SEQUENTIAL_PARALLEL_BRIDGE.md v0.2 at commit
  2676912a3d16f7a630cc6f113331e3aa236727e0.

The bridge is the mathematical authority for the Part VI objects imported in
§2. This note adds a dynamic coordination layer; it does not silently replace,
rename, or broaden those objects.

The following labels are frozen for this note:

| Label | Meaning |
|---|---|
| Definition | A vocabulary or model choice adopted by v0.1 |
| Identity | An algebraic consequence of stated definitions |
| Static example | Hand arithmetic illustrating a possibility, not an observed result |
| Candidate theorem — UNPROVED | A statement requiring a separate proof or falsification programme |
| Coordination hypothesis — UNTESTED | A conditional empirical or model claim requiring preregistration |
| Institutional choice | A policy, priority, allocation, or valuation decision not selected by physics |
| Open problem | An unresolved question and not authorization to investigate it |

### 1.1 Scientific and operational exclusions

This note does not:

- invoke, investigate, correct, retry, finalize, or reinterpret Gate 1D-C;
- modify any Gate 1D-C protocol, plan, implementation, receipt, or result;
- begin the deterministic parallel-testing specification proposed by the
  sequential–parallel bridge;
- execute a model step, scientific function, simulation, trajectory, runner,
  finalizer, or candidate experiment;
- inspect or generate scientific outcomes;
- assume that coordination helps;
- assume that waves, synchronization, universal scaling laws, fractals,
  Fibonacci patterns, or collective benefits exist; or
- choose an economic constitution, settlement allocation, or universal social
  objective.

The preserved Gate 1D-C incident record remains outside this work: one
official invocation occurred, no receipt was created, no model state advanced,
the result directory remains absent, and the scientific state remains
**UNSTARTED**. Nothing in this document changes that state or authorizes a
second invocation.

## 2. Dependency boundary: Parts VI, VII, and VIII

Dynamic Coordination belongs primarily to Part VIII, *Dynamic Coordination
Fields and Society Geometry*. It depends on:

1. Part VI for sequential and joint-transition accounting; and
2. Part VII for routes, route actors, distance, losses, propagation, and
   infrastructure across space.

Part VIII asks how timing, placement, topology, information, commitments,
capacity, and scheduling alter the feasible histories built from those
foundations. It may apply Part VI and Part VII objects to a changing system,
but it may not present either foundation as a new Part VIII discovery.

### 2.1 Part VI objects imported unchanged

The following terms retain exactly the meanings frozen in
SEQUENTIAL_PARALLEL_BRIDGE.md v0.2:

| Imported object | Authoritative bridge location | Use in this note |
|---|---|---|
| Represented field distortion \(D(X)\) | §§3.2–3.3 and §17 | Applied only inside a declared compatible accounting boundary |
| Group EBU | §§3.8, 5, 9, and 10.1 | Used as the existing physical endpoint measure when a dynamic schedule forms a joint-transition group |
| Same-baseline field non-additivity \(N_G\) | §7 | Retained as the existing diagnostic; not treated as a dynamic allocation |
| Comparator-relative interaction \(I_{G\mid\pi}\) | §§6 and 9 | Retained relative to a named admissible comparator |
| Joint-transition group | §§3.5–3.7 and §17 | Used after applying the imported dependency rule |
| Group receipt and child records | §11 | Extended by dynamic provenance fields without changing physical closure |
| Effective interval, write support, and constraint support | §3.6 and §17 | Referenced for action instances; not redefined here |
| Admissible comparator discipline | §9 | Required for every schedule comparison |

No formula below is an alternative definition of any imported object. In
particular, a dynamic schedule does not turn an institutional settlement into
a physical contribution, a receipt batch into a joint transition, or a
same-baseline diagnostic into comparator-relative interaction.

### 2.2 Part VII dependency

This note uses a provisional graph representation so its dynamic questions can
be stated. The physical meanings of a route, route segment, route actor,
distance, transport loss, and propagation mechanism belong to the Part VII
route foundation. Until that foundation is frozen:

- an edge is only a typed connection declared by a model;
- edge delay and loss are parameters, not established universal laws;
- graph distance is not automatically physical distance;
- reachability is not delivery; and
- a graph path does not by itself identify causal or institutional credit.

## 3. Seven layers that must remain distinct

The foundation separates seven layers even when one software record later
contains fields for all of them.

| Layer | Symbol | Scientific role | Must not be confused with |
|---|---|---|---|
| Physical state | \(x_k\) | Stocks, field variables, conditions, accumulated burdens, and physical clocks at epoch \(k\) | A measurement of that state or a ledger balance |
| Network topology | \(g_k\) | Provider nodes, typed directed edges, availability, and physical connection state | The policy that chooses a route |
| Coordination policy | \(\mu\) | Rule mapping permitted information to proposed actions, reservations, schedules, and routes | A physical law or observed causal contribution |
| Objective family | \(\mathcal J\) | Declared criteria by which complete histories may be compared | Feasibility, morality, or a universal scalar |
| Constraints | \(\mathcal F_k\) | Physical, safety, contractual, informational, and institutional admissibility conditions | An objective to maximize |
| Measurements | \(y_k\) | Time-stamped, calibrated observations with uncertainty and provenance | The complete physical state |
| Institutional allocation | \(\lambda\) | Priority, access, settlement, residual, responsibility, or ownership assignment | Group EBU or identified physical causality |

A change in institutional allocation can alter later behaviour and therefore
later physical histories. That causal pathway must be represented explicitly.
The allocation itself does not retroactively become a physical measurement.

## 4. Minimal dynamic coordination model

### 4.1 Time and evaluation horizon

For the provisional discrete-time foundation, let:

\[
k\in\mathcal K_H:=\{0,1,\ldots,H\},
\]

where the epoch duration \(\Delta t\), clock origin, time zone when relevant,
and terminal horizon \(H\) are declared before comparison.

The **evaluation horizon** is the last epoch whose physical state, delivered
service, unresolved commitments, delayed effects, and coordination costs are
included in a stated comparison. A completion time and a settlement horizon
may differ. Effects due after \(H\) must remain visible as pending or excluded;
they must not be treated as zero.

Continuous time may later be necessary. Discretization error, simultaneous
event ordering, and the relation between \(\Delta t\) and physical time remain
open problems.

### 4.2 Dynamic coordination state

The provisional dynamic coordination state is:

\[
\boxed{Z_k=(x_k,g_k,q_k,c_k,\ell_k)}.
\]

Its components are:

- \(x_k\): typed physical stocks, field variables, accumulated resource use,
  physical condition, and any clock-dependent quantities needed by the
  declared boundary;
- \(g_k\): current provider-network topology and edge or node condition;
- \(q_k\): admitted but unserved demand, congestion queues, and in-transit
  payloads not already represented in \(x_k\);
- \(c_k\): accepted commitments, reservations, deadlines, and outstanding
  obligations;
- \(\ell_k\): delayed-effect events with due epochs, typed payloads or
  transformations, provenance, and unresolved status.

This tuple is conditionally Markov only relative to the declared physical
transition model, event rules, and complete inputs \(u_k,w_k\): once those are
fixed, \(Z_k\) must be sufficient to determine \(Z_{k+1}\). If two histories
with the same \(Z_k\) can have different successors under the same declared
inputs because a relevant physical memory variable was omitted, the state is
insufficient and must be expanded prospectively.

Closed-loop Markov sufficiency is a stronger requirement. If a controller,
estimator, or information policy uses history-dependent memory
\(m_k^\mu\)—including filters, learned parameters, prior messages, internal
clocks, or unresolved decisions—then the closed-loop representation must use
an augmented state such as:

\[
\widetilde Z_k=(Z_k,m_k^\mu).
\]

Alternatively, the relevant information history must be encoded in an
equivalent sufficient statistic. Controller memory remains analytically
distinct from physical state even when it is included in the augmented
closed-loop state.

Whenever an imported Part VI quantity is applied, a compatible boundary
\(\mathcal B\) must declare a representation map:

\[
X_k^{\mathcal B}=\Psi_{\mathcal B}(Z_k).
\]

That map includes every component of topology, queues, commitments, delayed
effects, resource use, and coordination overhead that is physically relevant
to the boundary. The imported \(D\) is evaluated on the resulting represented
state \(X_k^{\mathcal B}\), not automatically on the raw coordination tuple.
This mapping applies the bridge; it does not redefine represented field
distortion.

Policy \(\mu\), objectives \(\mathcal J\), constraints \(\mathcal F_k\),
measurements \(y_k\), and institutional allocations \(\lambda\) are not hidden
inside \(Z_k\). Version identifiers may be attached to the record, but they
remain separate analytical layers.

### 4.3 Provider network

At epoch \(k\), the provisional provider network is:

\[
g_k=(V_k,E_k,m_k),
\]

where:

- \(V_k\) is a finite set of typed provider, storage, conversion,
  transshipment, measurement, and sink nodes;
- \(E_k\subseteq V_k\times V_k\times\mathcal R\) is a set of directed,
  resource-typed connections; and
- \(m_k\) records whether each node or edge is available, degraded, failed,
  isolated, or under repair.

A **provider** is a declared locus capable of offering, transforming, storing,
measuring, routing, or accepting a typed service or resource. A provider may
be a physical facility, a person, an organization, or a composite boundary.
Provider identity does not by itself establish causality, ownership, or a
settlement share.

Node and edge membership may change with time. A stable identifier must
survive temporary unavailability so histories, commitments, and failures do
not disappear when topology changes.

### 4.4 Action instance

A dynamic action instance \(a_i\) is a versioned reference to the bridge's
action transformation together with:

- a unique identifier and action type;
- requesting actor and responsible provider identifiers;
- requested and accepted typed quantities;
- declared placement and, when applicable, route;
- proposed start, expected completion, and evaluation horizon;
- the imported effective interval, write support, and constraint support;
- prerequisites, deadlines, and completion conditions;
- associated commitments and reservations;
- measurement and uncertainty requirements; and
- the declared accounting boundary and receipt relationship.

The instance does not guarantee execution. It may be proposed, accepted,
reserved, active, completed, partially completed, failed, cancelled, expired,
or unresolved. State transitions between these statuses must be explicit.

### 4.5 Schedule

A **schedule** \(\sigma\) is a finite, versioned arrangement of action
instances and coordination events. It declares:

- proposed or accepted start and completion epochs;
- precedence and allowed overlap;
- routes and placements;
- reservation acquisition and release;
- capacity allocation and queue discipline;
- failure and rerouting rules;
- measurement epochs;
- a common evaluation horizon; and
- any named admissible sequential comparator required by the bridge.

A schedule is an input or policy output, not a physical outcome. A schedule
that violates constraints is inadmissible even if its arithmetic objective
would appear attractive.

### 4.6 Commitments and reservations

A **commitment** is an accepted future obligation with a provider, beneficiary,
typed quantity or service, time window, conditions, and status.

A **reservation** is the capacity claim used to support a commitment. For
resource \(r\) on edge or node \(e\) at epoch \(k\), let
\(R_{i,e,r,k}\geq0\) denote the capacity reserved for action \(i\). A basic
admission condition is:

\[
\sum_i R_{i,e,r,k}\leq U_{e,r,k},
\]

where \(U_{e,r,k}\) is the capacity available at the time of admission under
the declared topology and uncertainty rule.

A reservation is not stored material and is not delivered service. Failure
may make an accepted reservation physically unavailable. In that case the
obligation becomes impaired, breached, rerouted, or unresolved according to a
declared rule; it must not be erased from the record.

### 4.7 Capacity and congestion

For each typed edge or node \(e\), resource \(r\), and epoch \(k\), declare:

- installed capacity \(\bar U_{e,r,k}\);
- availability factor \(0\leq\alpha_{e,r,k}\leq1\);
- usable capacity \(U_{e,r,k}=\alpha_{e,r,k}\bar U_{e,r,k}\);
- reserved capacity;
- actual admitted load; and
- actual completed flow.

Physical capacity feasibility requires:

\[
0\leq\sum_i f_{i,e,r,k}\leq U_{e,r,k}.
\]

Reserved and spot service are parts of the same physical flow and must not be
counted twice.

For a lossless single queue, let \(b_{e,r,k}\) be newly presented requests,
\(a_{e,r,k}\) the part admitted to the queue, \(j_{e,r,k}\) the part rejected,
and \(d_{e,r,k}\) the part left pending outside the admitted queue. The
admission decision must close:

\[
b_{e,r,k}=a_{e,r,k}+j_{e,r,k}+d_{e,r,k}.
\]

The admitted-queue identity is provisionally:

\[
q_{e,r,k+1}
=q_{e,r,k}+a_{e,r,k}-f_{e,r,k}-z_{e,r,k},
\]

where completed flow \(f\) and \(z\), the expiry, cancellation, or abandonment
of already-admitted queued demand, share the same units as admitted arrival
\(a\). Rejected quantity \(j\) never enters \(q\) and therefore is recorded
separately rather than subtracted from it. Pending quantity \(d\) also remains
outside \(q\) until a later admission decision. With physical losses,
transformations, priorities, or multiple classes, separate typed terms are
required.

**Congestion** means that admitted load, requested load, or a queue interacts
with a binding capacity or service rule so that completion, delay, loss, or
feasibility changes. High utilization without any such effect is not by
itself congestion.

### 4.8 Delay and delayed effects

A route or action delay is a declared non-negative duration:

\[
\tau_{i,k}=\tau^{\mathrm{base}}_{i,k}
+ \tau^{\mathrm{queue}}_{i,k}
+ \tau^{\mathrm{processing}}_{i,k}
+ \tau^{\mathrm{failure}}_{i,k}.
\]

Terms are included only when the model represents the corresponding
mechanism. This additive expression is valid only when its components are
non-overlapping durations under a frozen event convention, or when the model
explicitly defines them as additive increments. If two causes occupy the same
elapsed interval, the interval must be assigned once through a mutually
exclusive decomposition; otherwise only total delay may be added and the
overlapping causes remain annotations. Delay may depend on state, load, route,
action class, or failure, but it must be deterministic for fixed declared
inputs in the deterministic foundation.

An item dispatched at epoch \(k\) is not available at its destination before
its declared arrival epoch. Its in-transit state or delayed-effect event
remains in \(q\) or \(\ell\), with provenance linking it to the originating
action.

A **delayed effect** is a registered future state change or measurement
obligation whose due epoch is later than the action's immediate endpoint.
Maturing a delayed effect is part of system evolution; attributing it
causally to the originating action remains subject to the bridge's warning
about later drive and later actions.

### 4.9 Uncertainty

Uncertainty is represented prospectively by:

- a declared set \(\mathcal W_k(Z_k)\) of admissible disturbances or parameter
  values;
- a measurement set or interval for each uncertain observed quantity;
- provenance and calibration for each bound; and
- a rule for propagation, contraction, expiry, and model mismatch.

For the deterministic foundation, a complete frozen disturbance history
\(w_{0:H-1}\) produces one history. Robust claims quantify over a declared set
of such histories. Probability is optional and may not be invented from a
range alone.

Unknown, stochastic, adversarial, and merely unmeasured are different statuses
and must not be collapsed into one number.

## 5. Provisional deterministic network evolution

### 5.1 State-transition form

For a fixed state schema, action set, schedule or policy output \(u_k\),
exogenous input \(w_k\), and versioned update rules:

\[
Z_{k+1}=\mathcal F_k(Z_k,u_k,w_k),
\qquad
y_k=\mathcal H_k(Z_k,\eta_k).
\]

Here \(\mathcal F_k\) is physical and operational evolution, while
\(\mathcal H_k\) is measurement. Measurement error \(\eta_k\) does not alter
physical state unless a separately modelled decision responds to the
measurement.

Deterministic means that the same complete inputs and event ordering produce
the same successor. It does not mean that the network is static, certain,
linear, reversible, or free of failures. This transition is Markov in \(Z_k\)
only conditional on declared \(u_k,w_k\). When \(u_k\) comes from a
history-dependent policy, the augmented closed-loop state from §4.2 must
include the policy's decision-relevant memory.

### 5.2 Provisional within-epoch order

The following ordering is frozen only as the v0.1 analytical default. A later
specification must either retain it or document a prospective replacement.

1. Mature delayed effects and arrivals due at the start of epoch \(k\).
2. Apply declared exogenous topology changes, failures, repairs, and capacity
   deratings effective at \(k\).
3. Record the resulting state and make the permitted measurement available to
   the policy.
4. Propose starts, stops, reservations, releases, routes, and reroutes using
   only permitted information.
5. Screen prerequisites, deadlines, commitments, safety constraints,
   topology, and capacity.
6. Admit, reject, defer, or partially accept requests using the frozen
   allocation and queue disciplines.
7. Build joint-transition groups using the imported Part VI rule and form the
   exact joint-transition proposal for every accepted group without yet
   mutating physical state.
8. Validate a disjoint update-ownership record, then commit each proposed
   physical transition, completed flow, conversion, loss, consumption,
   congestion effect, expiry, resource use, and physical coordination burden
   exactly once while recording the corresponding accounts.
9. Register new in-transit payloads and delayed-effect events; update
   commitments, reservations, and unresolved statuses.
10. Apply declared natural drive for the remainder of the epoch and produce
    the end-of-epoch record.

If two operations in this list do not commute, changing their order changes
the model. The later framework specification must therefore make event order
machine-readable and testable without treating the chosen order as a law of
nature.

Steps 7 and 8 separate transition construction from state mutation and
accounting. Their update-ownership record partitions the physical effects:
every flow, loss, conversion, resource use, and burden is owned by exactly one
state update. Accounting mirrors the committed update and may not apply it
again. The same no-double-application rule covers due events in step 1,
topology changes in step 2, delayed-event registration in step 9, and natural
drive in step 10. If an action transformation already includes a loss,
conversion, resource use, or burden, step 8 commits that term from the
transition proposal and does not add a second operational copy.

### 5.3 Changing edges and failures

For every edge \(e\), an availability state may change with time:

\[
m_e(k)\in\{\text{available},\text{degraded},\text{failed},
\text{isolated},\text{repairing}\}.
\]

The state maps to a declared availability factor. A failed edge has zero
usable capacity unless a separately declared degraded mode exists. No new
dispatch may use an unavailable edge.

Payload already beyond the failed segment, payload stranded before it, and
payload physically lost are distinct states. A reroute changes only the
unfinished route suffix. It may not rewrite completed segments, losses,
delays, resource use, or commitments.

### 5.4 Reservations under changing capacity

Admission must test reservations against capacity at the time required by the
declared guarantee. If later failure reduces capacity below previously
reserved demand:

\[
\sum_i R_{i,e,r,k}>U_{e,r,k},
\]

the record contains an explicit reservation shortfall. A priority or
allocation rule may decide which obligations are served, but it cannot make
the physical inequality disappear.

### 5.5 Delayed effects and the horizon

At horizon \(H\), every delayed event has exactly one status:

- matured and represented in the state;
- pending with a due epoch after \(H\);
- cancelled under an explicit physical or institutional rule;
- failed with its physical consequences recorded; or
- unresolved because necessary information is absent.

Pending and unresolved are not zero. A comparison that excludes them must
state that limitation and must not claim complete physical closure.

### 5.6 Policy and information timing

A coordination policy is a sequence:

\[
\mu=(\mu_0,\ldots,\mu_{H-1}),
\]

where \(\mu_k\) maps the policy's permitted information history to proposed
coordination decisions. The information set must state:

- observation epochs and ages;
- which topology and queue variables are visible;
- measurement uncertainty;
- active commitments and reservations;
- whether other providers' requests are visible; and
- any privacy or institutional restrictions.

A policy using future failures, future measurements, or candidate outcomes is
inadmissible unless those values were genuinely available at the decision
epoch. An open-loop schedule is the special case in which all decisions are
frozen before evolution.

## 6. How dynamic structure may affect a result

The following are mechanisms to represent, not conclusions to assume.

### 6.1 Timing

Changing an action's start can change:

- the live predecessor state;
- overlap and joint-transition grouping;
- available capacity and queue position;
- exposure to natural drive or failure;
- whether a deadline is met;
- the maturity of delayed effects by \(H\); and
- the admissible sequential comparator.

If none of these registered mechanisms changes, a timing effect has not been
established merely because clock labels differ.

### 6.2 Placement

Placement may change route availability, conversion loss, delay, local
capacity, exposure, measurement quality, and which accounting boundary is
needed. Nearer placement is not universally better: local scarcity,
inefficient conversion, fragile topology, concentrated burden, or missing
expertise may outweigh distance.

### 6.3 Topology

Topology may change reachability, bottleneck cuts, path diversity, failure
exposure, congestion, observability, and coordination overhead. Adding an edge
need not improve the physical result if it consumes resources, creates a
cascade path, changes incentives, or attracts load to a fragile bottleneck.

### 6.4 Phase

Phase is defined only relative to a declared recurrent reference with period
\(P>0\). For an action starting at time \(s_i\), one possible normalized phase
coordinate is:

\[
\phi_i=\frac{s_i\bmod P}{P}.
\]

This coordinate does not prove periodicity, synchronization, or a physical
phase interaction. If the reference is not stable over the horizon, phase
must be treated as local, uncertain, or undefined.

### 6.5 Scheduling

Scheduling may alter order, overlap, accepted quantities, queues, reservation
shortfalls, route selection, completion, and coordination cost. A schedule
comparison must preserve the bridge's comparator discipline. A difference
caused by rule-replayed quantities is not automatically an effect of
simultaneity.

### 6.6 Pattern-claim guardrails

| Proposed pattern claim | Minimum prospective requirement before testing | A non-pattern explanation that must remain available |
|---|---|---|
| Traveling wave | Declared propagated variable, topology or metric, source event, direction, finite speed or lag relation, attenuation rule, and null model | Independent delayed dispatches or diffusion |
| Synchronization | Declared oscillatory variables, phase estimator, coherence statistic, observation window, and null distribution | Common forcing or shared clock |
| Scaling law | Frozen system family, scale variable, response, range, competing functional forms, uncertainty, and out-of-sample rule | Finite-size saturation or piecewise capacity |
| Fractal structure | Declared object, scale range, dimension estimator, finite-size correction, and non-fractal alternatives | A branching graph with no scale invariance |
| Fibonacci recurrence | Exact recurrence or preregistered tolerance, index mapping, multiple-comparison control, and mechanistic alternative | Selective matching of a short integer sequence |
| Collective benefit | Complete objective vector, reference schedule, accounting boundary, coordination cost, and affected groups | Benefit to one region with transferred burden elsewhere |

None of these requirements is satisfied merely by a visually suggestive plot.
No such plot or outcome is produced in this note.

## 7. Candidate objective family

Dynamic Coordination does not have one justified universal scalar objective.
The default evaluation record is an ordered collection of typed metrics with
directions, boundaries, horizons, uncertainty, and reference schedules.

### 7.1 Physical improvement

When one compatible boundary and declared distortion function cover the
comparison, the imported group EBU may serve as one physical endpoint metric.
It does not replace service, viability, delay, future capacity, uncertainty,
or unresolved delayed effects. Equal represented distortion may hide
different physical states and different future feasibility.

### 7.2 Viability

Let physical constraint \(j\) be written:

\[
g_j(Z_k)\geq0.
\]

The dimensioned viability margin is \(g_j(Z_k)\) in the units of that
constraint. A normalized margin may be used only with a prospectively
declared positive reference scale \(s_j\):

\[
\widehat g_j(Z_k)=\frac{g_j(Z_k)}{s_j}.
\]

Possible viability criteria include the vector of minimum margins over the
horizon, the count and duration of violations, and terminal distance from a
declared viable set. A minimum over heterogeneous unnormalized quantities is
invalid.

### 7.3 Service

For resource or service class \(r\) and region \(z\):

\[
S_{r,z}(\sigma;H)=\sum_{k=0}^{H}d_{r,z,k}^{\mathrm{completed}},
\]

where completion, quality, location, and deadline conditions are declared.
Service quantities may be summed only within compatible units and service
definitions. Requested, accepted, dispatched, arrived, and usable service are
different quantities.

### 7.4 Delay

For a compatible service class \(r\), quantity-weighted lateness is:

\[
L_r(\sigma;H)=
\sum_i q_{i,r}^{\mathrm{completed}}
\max(0,t_i^{\mathrm{arrival}}-t_i^{\mathrm{deadline}}).
\]

Other legitimate delay records include queue time, completion time, maximum
lateness, and the vector of delays by actor or region. Aggregation weights and
the treatment of incomplete actions must be explicit.

### 7.5 Resilience

Resilience is not a synonym for ordinary performance. A candidate resilience
record compares a declared reference condition \(w^0\) with named failure or
disturbance conditions \(w\), using compatible service and viability metrics.
Examples include:

- worst-case service shortfall by class and region;
- time to return to a viable set;
- commitments completed despite a named failure set;
- residual capacity after removal of declared nodes or edges; and
- irreversible burden created during recovery.

Redundant infrastructure and the resources needed to build and maintain it
remain inside the accounting boundary when relevant.

### 7.6 Uncertainty

Candidate uncertainty metrics include dimensioned interval width, worst-case
constraint margin, probability of violation under a justified distribution,
model discrepancy, observation age, and unresolved-effect count. Interval
widths in unlike units cannot be added without a declared transformation.
Smaller reported uncertainty is not better if it was achieved by omitting
unknown effects.

### 7.7 Coordination cost

Coordination cost is a typed vector that may include:

- sensing and calibration;
- communication and data movement;
- computation and storage;
- negotiation, waiting, and reservation holding;
- verification and group-receipt production;
- unused reserved capacity;
- rerouting and recovery; and
- institutional labour, privacy exposure, or other declared burdens.

Physical coordination costs belong in the represented state and distortion
boundary when applicable. Institutional burdens that are not physical EBU
must remain separately visible.

### 7.8 Comparison rules

A future study may prospectively choose one of these rules:

1. **Feasibility first:** reject every schedule violating hard constraints,
   then compare the remaining metric vectors.
2. **Pareto comparison:** schedule \(A\) dominates \(B\) only when it is no
   worse on every declared criterion and strictly better on at least one.
3. **Lexicographic rule:** rank criteria in a declared order before outcomes.
4. **Epsilon-constraint rule:** optimize one metric while keeping declared
   bounds on the others.
5. **Scalarization:** use a dimensionally valid, prospectively justified set
   of transformations and weights, with sensitivity reported.

Scalar weights encode priorities or institutional values unless a physical
derivation establishes otherwise. Weights may not be tuned after candidate
outcomes are inspected.

## 8. Dimensional discipline and accounting boundaries

### 8.1 Typed quantities

Every stock, flow, capacity, reservation, service, loss, delay, burden, and
cost must declare:

- resource or service type;
- physical dimension and unit;
- spatial region and node or edge when relevant;
- time basis for rates;
- sign convention;
- measurement or model provenance; and
- uncertainty status.

A capacity of \(5\ \mathrm{kg\,h^{-1}}\) cannot be compared directly with an
inventory of \(5\ \mathrm{kg}\). Energy, water, mass, habitat, time, and
computation cannot be summed merely because each is represented by a number.

Resource conversion requires a declared transformation. If resource \(r\) is
converted to \(s\):

\[
o_{s,k}=\eta_{r\to s,k}\,i_{r,k},
\]

then the units and physical interpretation of \(\eta\), coproducts, losses,
and waste must be recorded. A price is not a physical conversion coefficient.

### 8.2 Regional stock-flow closure

For compatible resource \(r\) in region \(z\), a provisional stock identity
is:

\[
x_{r,z,k+1}
=x_{r,z,k}
+p_{r,z,k}
+b^{\mathrm{in}}_{r,z,k}
+t^{\mathrm{in}}_{r,z,k}
+\rho_{r,z,k}
+v^{\mathrm{out}}_{r,z,k}
-b^{\mathrm{out}}_{r,z,k}
-t^{\mathrm{out}}_{r,z,k}
-v^{\mathrm{in}}_{r,z,k}
-c_{r,z,k}
-\ell_{r,z,k},
\]

where production \(p\), declared external-boundary inflow
\(b^{\mathrm{in}}\), transfers from other included regions
\(t^{\mathrm{in}}\), returns \(\rho\), declared external-boundary outflow
\(b^{\mathrm{out}}\), transfers to other included regions
\(t^{\mathrm{out}}\), conversion output into resource \(r\)
\(v^{\mathrm{out}}\), resource-\(r\) input consumed by conversion
\(v^{\mathrm{in}}\), consumption \(c\), and loss \(\ell\) share the stock unit
for one epoch. The superscripts on \(v\) describe flow relative to the
resource-\(r\) account, not relative to the conversion device. A declared
external-boundary inflow is an allowed source term, not unexplained creation.
A transfer exported from one included region and imported to another is one
internal flow: the parent boundary must cancel the matching
\(t^{\mathrm{out}}\) and \(t^{\mathrm{in}}\) exactly once. Production,
conversion, coproduct, storage, return, consumption, and loss terms must
follow their declared typed balance rather than being inferred from capacity
compliance.

Conservation may require energy, mass, charge, species, or other domain
accounts. No universal list is implied.

### 8.3 Boundary register

Every dynamic comparison must freeze:

1. state schema and distortion version;
2. resource and service types with units;
3. included nodes, edges, providers, regions, and actors;
4. initial epoch, terminal horizon, and delayed-effect treatment;
5. lifecycle stages and external physical effects;
6. topology, route, and failure scope;
7. commitments, reservations, and coordination overhead;
8. measurement systems, ages, uncertainty, and missing variables;
9. natural drive and external inputs;
10. objective vector and reference schedule;
11. institutional priority and settlement rules; and
12. unresolved cross-boundary effects.

If two systems lack a compatible parent boundary, their physical EBU values
must not be added. An institutional exchange rate or priority weight does not
create physical compatibility.

## 9. Six hand-worked static examples

These examples are arithmetic fixtures only. They are not trajectories,
executed tests, or candidate outcomes. Their numbers illustrate possible
mechanisms and make no empirical claim.

### 9.1 Independent providers

Two disconnected providers deliver the same grade of water to two separate
local tanks during one one-hour epoch:

| Provider | Capacity | Accepted delivery | Shared constraint |
|---|---:|---:|---|
| \(P_1\) | \(3\ \mathrm{L\,h^{-1}}\) | \(2\ \mathrm L\) | None |
| \(P_2\) | \(4\ \mathrm{L\,h^{-1}}\) | \(3\ \mathrm L\) | None |

Each delivery is below its own capacity:

\[
2\leq3,\qquad3\leq4.
\]

Because the tanks, capacities, write supports, and constraint supports are
disjoint, changing \(P_1\)'s accepted quantity does not change \(P_2\)'s
feasibility in this declared fixture. Both deliveries total \(5\ \mathrm L\)
only because their service type and units are compatible.

The imported Part VI grouping rule, not simultaneous clock time, determines
whether they remain separate. Storing the receipts in one batch would not
make the providers physically interactive.

### 9.2 Shared-capacity congestion

Two providers each request \(4\) crates on one edge with capacity
\(6\) crates per epoch. Both requests arrive at epoch \(0\), and a frozen
equal-share service rule allocates the edge. All \(8\) crates are admitted to
the queue in this fixture; none is rejected or left pending outside it.

\[
f_A=f_B=3,\qquad f_A+f_B=6.
\]

At the end of the epoch:

\[
q_A=0+4-3-0=1,\qquad q_B=0+4-3-0=1.
\]

Completed service is \(6\) crates, and queued demand is \(2\) crates. Recording
two independent deliveries of \(4\) would imply \(8>6\) and violate capacity.
Rejecting one crate per provider instead would be a different admission
decision: the rejected crates would be recorded outside the queue and the
end-of-epoch queue would be zero.

If deadlines allow a second identical epoch, the remaining two crates can be
served later, but they carry positive delay. Thus total service by a longer
horizon can be equal while the delay record differs. Shared capacity creates
a joint constraint; it does not determine the institutionally preferred
queue discipline.

### 9.3 Delayed delivery

A destination requires \(4\ \mathrm{kg}\) of material by the start of epoch
\(2\). One route has capacity \(5\ \mathrm{kg}\) per dispatch and deterministic
delay of two epochs.

Dispatch at epoch \(0\):

\[
t^{\mathrm{arrival}}=0+2=2,
\]

so all \(4\ \mathrm{kg}\) arrive by the declared deadline.

Dispatch at epoch \(1\):

\[
t^{\mathrm{arrival}}=1+2=3,
\]

so zero usable service is available at the deadline even though the same
quantity eventually arrives. At horizon \(H=2\), the later dispatch is
pending, not lost and not completed.

The arithmetic shows why dispatch, arrival, usable service, and horizon must
remain distinct. It does not establish that two epochs is a real route delay.

### 9.4 Topology failure and rerouting

A source \(S\) can reach sink \(T\) by:

- route \(S\to A\to T\), capacity \(4\) crates and total delay two epochs; or
- route \(S\to B\to C\to T\), capacity \(3\) crates and total delay three
  epochs.

An accepted request is \(4\) crates. Edge \(A\to T\) fails before dispatch.
The first route then has zero usable capacity. Rerouting on the alternate path
gives:

\[
\text{dispatched}=3,\qquad
\text{unserved}=4-3=1,\qquad
t^{\mathrm{arrival}}=3.
\]

The alternate path preserves three crates of service at a later horizon, but
it does not fulfill the original four-crate, two-epoch commitment. The record
must retain the failed reservation, one-crate shortfall, added delay, and
resources used by rerouting.

This example does not prove that redundancy is always beneficial; maintaining
the alternate route could cost more or create other burdens than it avoids.

### 9.5 Timing-dependent cooperation

Provider \(A\) produces \(3\ \mathrm{MJ}\) of recoverable waste heat during
epoch \(0\). Provider \(B\) needs \(3\ \mathrm{MJ}\) of heat during the same
epoch. There is no storage, and unused heat dissipates at the end of an epoch.

With overlap and a lossless local connection:

\[
\text{heat transferred}=\min(3,3)=3\ \mathrm{MJ}.
\]

If \(B\)'s demand is scheduled at epoch \(1\), the epoch-0 heat remaining is:

\[
3-3=0\ \mathrm{MJ},
\]

so the transfer at epoch \(1\) is zero. Cooperation depends here on a declared
temporal complementarity. Storage, route loss, coordination energy, or a
different demand profile could reverse the comparison.

The example shows a possible timing mechanism. It is not evidence of
synchronization, a wave, or a general collective benefit.

### 9.6 Coordination that worsens the physical result

A cold-handling edge can process \(5\) crates per epoch. Two providers each
have \(4\) perishable crates. Unprocessed crates expire at the end of the epoch
in which they are released.

With releases scheduled separately:

\[
\text{epoch 0 service}=4,\qquad
\text{epoch 1 service}=4,\qquad
\text{total}=8.
\]

A coordinator instead aligns both releases at epoch \(0\):

\[
\text{requested}=8,\qquad
\text{served}=5,\qquad
\text{expired}=3.
\]

All eight crates are admitted in this fixture, none is rejected, and the
three unserved admitted crates expire:

\[
q_1=0+8-5-3=0.
\]

The coordinated schedule delivers three fewer crates before a common
two-epoch horizon, even before including coordination cost. The worsening is
caused by synchronizing perishable load at a binding capacity. A policy label
such as cooperative, central, distributed, or optimized cannot substitute for
the physical accounting.

## 10. Candidate theorem register — all unproved

Every entry below is a **candidate theorem — UNPROVED**. A future proof must
use the exact state, boundary, topology, event order, and assumptions stated
in its preregistration. A future falsification test requires separate
authorization.

### T-DC-1 — One-step feasibility preservation

**Assumptions.**

1. \(Z_k\) satisfies every registered physical constraint.
2. Admission rejects or truncates every action that would violate capacity,
   stock, safety, route, or timing constraints.
3. Each accepted transformation preserves its declared local constraints.
4. Due delayed effects and exogenous changes lie inside the feasibility set
   used at admission, or a registered emergency rule restores feasibility
   before physical execution.
5. Arithmetic, event ordering, and update ownership are exact, so no physical
   effect is omitted or applied twice.

**Candidate conclusion.** The successor \(Z_{k+1}\) is feasible.

**Future falsifier.** Produce one input satisfying all five assumptions for
which any registered constraint is violated at \(k+1\).

**Counterexample when assumptions fail.** A reservation is admitted against
capacity \(5\), an unmodelled failure reduces capacity to \(2\), and the model
still dispatches \(5\). Feasibility fails because assumption 4 was false.

### T-DC-2 — Viable-set invariance

**Assumptions.**

1. A closed viable set \(\mathcal V\) is declared in complete dynamic
   coordination state space.
2. The closed-loop state is augmented with every controller or
   information-history memory variable that affects the policy.
3. For every \(\widetilde Z\) whose physical coordination projection
   \(Z\in\mathcal V\), and every admissible disturbance \(w\), the policy
   selects a feasible \(u\) whose successor projection satisfies
   \(\mathcal F(Z,u,w)\in\mathcal V\).
4. Observation and actuation delay are represented in \(Z\) or in the
   augmented controller state according to their physical or informational
   role.
5. The actual disturbance remains in the declared uncertainty set.
6. The state-transition model is correct over the stated horizon.

**Candidate conclusion.** Starting in \(\mathcal V\), the closed-loop history
remains in \(\mathcal V\) for the declared horizon.

**Future falsifier.** Under the assumptions, exhibit the first epoch at which
\(Z_k\notin\mathcal V\).

**Counterexample when assumptions fail.** A tank policy observes a two-epoch
old level but the delay is omitted from state; the tank crosses its lower
bound before replenishment. Assumption 4 fails.

### T-DC-3 — Schedule serializability

**Assumptions.**

1. Accepted actions use identical fixed quantities in all comparisons.
2. Shared constraints, admission, and allocation have already been resolved,
   and no serialization changes those resolutions.
3. For every applicable admissible order \(\pi\), the declared joint execution
   applies each child transformation exactly once and its semantics equal the
   corresponding live-state composition on the reachable registered domain:

   \[
   T_G
   =T_{A_{\pi(n)}}\circ\cdots\circ T_{A_{\pi(1)}}.
   \]

   No undeclared simultaneous-only synergy, interference, loss, conversion,
   resource use, burden, or other state update is present.
4. When the conclusion covers more than one order, the child transformations
   commute on the reachable registered domain; disjoint imported write and
   constraint supports are one sufficient route to that condition.
5. No action changes another's prerequisites, completion, measurement, or
   delay.
6. Topology, natural drive, coordination cost, update ownership, and horizon
   treatment are identical.
7. Waiting and duration have no omitted physical effect.
8. Every compared sequential schedule is admissible under the bridge.

**Candidate conclusion.** Joint execution and every admissible serialization
to which assumption 3 applies reach the same complete represented endpoint;
therefore the imported comparator-relative interaction is zero for each named
applicable order.

**Future falsifier.** Satisfy all eight assumptions and obtain unequal complete
endpoints for any applicable admissible order.

**Counterexample when assumptions fail.** Let
\(T_A(x)=T_B(x)=x+1\). The child transformations commute, but suppose a
simultaneous-only mechanism makes the declared joint rule
\(T_G(x)=x+3\). Serial execution reaches \(x+2\), whereas joint execution
reaches \(x+3\). Commutativity alone is insufficient; assumption 3 was false.

### T-DC-4 — Typed stock-flow balance and capacity compliance

**Assumptions.**

1. Every resource account satisfies a prospectively declared typed stock-flow
   balance of the form in §8.2, including initial and terminal stock,
   production, declared external-boundary inflows and outflows, internal
   transfers, returns, consumption, conversion, loss, expiry, and storage
   changes wherever applicable.
2. Every term has compatible dimensions and is counted exactly once under the
   update-ownership rule in §5.2.
3. Internal transfers cancel at the parent boundary, while declared external
   boundary inflows and other declared source terms remain visible and are
   allowed.
4. Completed flow on every node and edge never exceeds its separately
   declared usable capacity.
5. Reservations are capacity claims, not additional stock or flow.
6. Every conversion and production term obeys its declared typed
   transformation, including coproducts and losses.

**Candidate conclusion.** Two distinct properties hold: every compatible
resource account has zero unexplained stock-flow residual after all of its
declared typed balance terms are included; and aggregate completed flow
separately respects every node and edge capacity. Capacity compliance does not
by itself prove conservation.

**Future falsifier.** Under all six assumptions, find either a nonzero
unexplained typed stock-flow residual or completed flow above usable capacity.

**Counterexample when assumptions fail.** A node can duplicate three stored
crates into six while sending only four through an edge of capacity five.
Capacity compliance passes, but the stock-flow balance fails because the
extra stock has no declared source. Conversely, three crates entering through
a declared external boundary are legitimate inflow rather than creation;
omitting that boundary term would create a false conservation failure.

### T-DC-5 — Bounded queue and delay

**Assumptions.**

1. A single compatible service class uses a work-conserving queue.
2. Initial backlog is finite.
3. Admitted queue arrivals, rather than all presented or rejected requests,
   satisfy a declared finite burst envelope.
4. Over every interval, guaranteed service exceeds admissible long-run arrival
   by a positive margin.
5. Base processing and propagation delay are bounded.
6. No failure removes the guaranteed service during the stated horizon.

**Candidate conclusion.** Backlog and completion delay have finite bounds
derivable from the burst envelope, service guarantee, initial backlog, and
base delay.

**Future falsifier.** Meet all six assumptions and produce a backlog or delay
above the prospectively derived bound.

**Counterexample when assumptions fail.** Average arrivals are below capacity,
but an unbounded instantaneous burst creates unbounded waiting. Assumption 3
fails even though the average looks safe.

### T-DC-6 — Reservation soundness

**Assumptions.**

1. Reservations are admitted against a robust lower bound on capacity for
   every epoch in their interval.
2. The sum of overlapping reservations does not exceed that lower bound.
3. Prerequisite stocks and routes are reserved consistently.
4. Providers cannot double-sell the same capacity.
5. Actual conditions remain in the registered uncertainty set.

**Candidate conclusion.** Every admitted reservation can be physically
honoured at its promised capacity, although the beneficiary may still cancel
or fail other completion conditions.

**Future falsifier.** Meet all assumptions and identify an admitted
reservation that cannot be served for physical capacity reasons.

**Counterexample when assumptions fail.** Two ledgers each reserve four units
of the same five-unit edge because the ledgers are not reconciled. Assumption
4 fails.

### T-DC-7 — Failure rerouting feasibility

**Assumptions.**

1. After the named failures, the residual network is a finite directed graph
   with non-negative finite edge capacities and one source \(s\) and one sink
   \(t\). A multiple-source or multiple-sink problem is first reduced
   explicitly to this form with a finite super-source and super-sink whose
   incident capacities encode the declared supplies and demands.
2. One conserved commodity and a required finite flow \(Q\geq0\) are declared.
3. The source can supply at least \(Q\) and the sink can accept at least
   \(Q\); those limits are represented by network capacities, including the
   super-source or super-sink edges when that reduction is used.
4. Every \(s\)-\(t\) cut in that residual network has capacity at least \(Q\).
5. Flow conservation is required at every intermediate node.
6. There are no additional path, deadline, conversion, priority, integral-flow,
   or multicommodity constraints.
7. Rerouting itself consumes no omitted capacity or stock.

**Candidate conclusion.** A feasible residual \(s\)-\(t\) flow of value
\(Q\), and therefore a feasible rerouting in this restricted model, exists
after the named edge or node failures.

**Future falsifier.** Meet all seven assumptions and show that no feasible
\(s\)-\(t\) flow of value \(Q\) exists.

**Counterexample when assumptions fail.** Two commodities each have a path
individually but require the same bottleneck simultaneously. The
single-commodity assumption fails. Likewise, naming several sources and sinks
without an explicit super-source/super-sink reduction leaves the stated
\(s\)-\(t\) cut condition undefined.

### T-DC-8 — Robust feasibility

**Assumptions.**

1. The uncertainty set is frozen prospectively and includes the realized
   disturbance and measurement error.
2. The policy certifies all hard constraints for every element of that set.
3. State, delay, topology, commitment, and decision-relevant controller-memory
   models are complete enough for the constraints.
4. Numerical and measurement tolerances are conservative and dimensionally
   valid.
5. Policy execution matches the certified decision.

**Candidate conclusion.** The realized history satisfies every certified hard
constraint over the declared horizon.

**Future falsifier.** Meet all assumptions and observe a certified constraint
violation.

**Counterexample when assumptions fail.** The registered failure set contains
one failed edge, but two adjacent edges fail. The actual disturbance is
outside the set, so assumption 1 fails.

### T-DC-9 — Certified no-harm fallback

**Assumptions.**

1. The feasible candidate set contains a named reference schedule.
2. Every physical burden, delayed effect, uncertainty penalty, and
   coordination cost relevant to the claim is inside the boundary.
3. Candidate metrics are predicted without future-data leakage and are exact
   for the declared model.
4. The selection rule accepts a replacement only if it is no worse than the
   reference on every declared criterion and strictly better on at least one.
5. The selected schedule is executed as certified.

**Candidate conclusion.** The selected schedule cannot be worse than the
reference on the declared metric vector within the model and horizon.

**Future falsifier.** Meet all assumptions and obtain a worse declared metric
component than the reference.

**Counterexample when assumptions fail.** A centralized schedule reduces
transport delay but omits sensing energy and privacy burden. The complete
boundary can be worse because assumption 2 fails.

## 11. Coordination hypothesis register — all untested

Each row is a **coordination hypothesis — UNTESTED**. Conditions are part of
the claim. A result outside those conditions neither confirms nor refutes it.

| ID | Conditional hypothesis | Future falsifier | Static counterexample or null mechanism |
|---|---|---|---|
| H-DC-1 Peak staggering | When flexible deadlines, perishable loss, and coordination cost permit it, moving load away from a binding shared-capacity peak improves service or delay relative to a named reference | Under the frozen conditions, the staggered schedule is not better on its declared service or delay metric | No capacity binds, so staggering only delays completion |
| H-DC-2 Placement | When route loss and delay dominate every declared local offset, placing service nearer demand improves the complete physical metric vector | Near placement satisfying the conditions is equal or worse on a preregistered component | The nearer provider uses a much less efficient conversion process |
| H-DC-3 Redundancy | When named failures disconnect the primary route and an alternate retains sufficient residual capacity, maintained redundancy improves failure-condition service after its full lifecycle cost is recorded | The redundant design does not improve declared failure service or violates another bound | The alternate route shares the same hidden cut and fails simultaneously |
| H-DC-4 Temporal complementarity | When one action produces a non-storable input required by another, overlap within the valid time window improves usable service relative to separated schedules | Qualified overlap yields no improvement in usable service | Storage makes separated timing equivalent, or interference makes overlap worse |
| H-DC-5 Phase-aware scheduling | For a verified periodic driver with stable phase and sufficient forecast accuracy, a preregistered phase-aware policy improves a named metric over a phase-blind reference | The policy fails its declared improvement threshold under the registered periodic regime | The driver drifts, so estimated phase becomes stale |
| H-DC-6 Adaptive rerouting | With timely failure information and an alternate route having residual capacity, adaptive rerouting improves delivered service over a frozen failed-route schedule | Rerouting under those conditions does not improve service or breaches a harder constraint | Reroute information arrives after the deadline |
| H-DC-7 Dynamic receipt economy | Group receipt production reduces total verification resources only when the bridge's batching condition holds and dynamic latency, risk, and measurement quality are non-worse | Full accounted group cost is not lower or quality degrades | Coordination analysis costs more than the shared measurement saves |
| H-DC-8 Joint coordination | Within a prospectively frozen finite admissible joint-schedule class, and under a declared shared constraint and accurate common information, at least one joint schedule Pareto-dominates the named independent local-policy reference | Exhaustively evaluate every member of the frozen finite admissible class and find no dominating schedule, or provide a valid proof that no dominating schedule exists in the frozen class | Central coordination is stale and synchronizes load into a bottleneck |
| H-DC-9 Traveling-wave regime | In a named network and parameter regime, a disturbance satisfies prospectively frozen propagation, lag, direction, attenuation, and null-model criteria | Any required wave criterion fails or a registered non-wave model explains the data at least as well | Independent dispatch delays create a moving-looking sequence without propagation |
| H-DC-10 Synchronization regime | In a named oscillatory system, coupling produces coherence above a frozen common-forcing null while phase relations remain stable for the declared window | Coherence does not exceed the null or disappears after common forcing is controlled | All providers follow the same external clock without interacting |
| H-DC-11 Scaling regime | Across a frozen family and scale range, a named response follows a preregistered scaling form better than registered alternatives and predicts held-out scales | Fit or held-out prediction fails the frozen criterion | A capacity ceiling creates a short log-log segment that mimics a power law |
| H-DC-12 Collective benefit | A named coordination policy improves every protected physical and service criterion, after costs and transferred burdens, relative to a named feasible reference | Any protected group or metric is worse beyond its frozen tolerance | Aggregate service rises by exporting burden to an unmeasured region |

Fractal and Fibonacci claims are deliberately absent from the hypothesis
register. They require their own future, separately justified mechanism,
statistic, alternatives, and multiple-comparison control; visual resemblance
is not a coordination hypothesis.

H-DC-8 is existential. Failure of a search procedure to find a dominating
schedule does not falsify it unless the frozen finite admissible class was
exhausted, or a valid non-existence proof covers that class. Expanding or
changing the schedule class after inspection would define a different
hypothesis.

## 12. Dynamic receipt and audit requirements

When a schedule produces an imported joint-transition group, the group receipt
architecture remains authoritative. A dynamic extension should add references
for:

- schedule and policy versions;
- controller-memory or sufficient-information-state versions;
- topology snapshots and topology-change events;
- admission, rejection, pending-request, queue-discipline, and
  capacity-allocation versions;
- transition proposals, update ownership, and commit/accounting records
  sufficient to prove that no physical effect was applied twice;
- reservations, shortfalls, releases, and breaches;
- route and reroute histories;
- dispatch, arrival, completion, and evaluation epochs;
- matured, pending, failed, and unresolved delayed effects;
- measurement ages, calibration, and uncertainty sets;
- natural drive and exogenous-event provenance;
- objective vector and named reference schedule; and
- coordination resource use.

These fields extend provenance; they do not change group physical measurement,
the preservation of child actions, comparator discipline, causal
identifiability limits, institutional settlement closure, or the distinction
between a receipt batch and a physical group.

An audit must be able to reconstruct which information was available to the
policy at every decision epoch. Later observations may correct a provisional
record through an authorized mechanism, but they may not be backfilled into
the earlier decision as if they had been known.

## 13. Frozen terminology v0.1

The following table freezes usage for this foundation. Imported terms point
to their source rather than being redefined.

| Term | Frozen use |
|---|---|
| Represented field distortion | Imported unchanged from the bridge |
| Group EBU | Imported unchanged from the bridge |
| Same-baseline field non-additivity | Imported unchanged from the bridge |
| Comparator-relative interaction | Imported unchanged from the bridge |
| Joint-transition group | Imported unchanged from the bridge |
| Group receipt | Imported unchanged from the bridge |
| Effective interval | Imported unchanged from the bridge |
| Dynamic coordination state | The tuple \(Z_k=(x_k,g_k,q_k,c_k,\ell_k)\), conditionally sufficient for the declared physical one-step evolution given complete declared inputs |
| Augmented closed-loop state | \(\widetilde Z_k=(Z_k,m_k^\mu)\), or an equivalent sufficient statistic, including every controller or information-history memory that affects future decisions |
| Physical state | Typed physical stocks, conditions, burdens, and physical clocks represented by \(x_k\) |
| Provider | A declared service, transformation, storage, routing, measurement, or sink locus |
| Provider network | Time-indexed typed nodes, directed edges, and their availability state |
| Topology state | The node, edge, availability, degradation, failure, and repair component \(g_k\) |
| Action instance | A versioned, scheduled reference to an imported action transformation with dynamic conditions |
| Schedule | A versioned arrangement of action and coordination events over a declared horizon |
| Coordination policy | A rule mapping permitted information to proposed schedules, reservations, routes, or other coordination decisions |
| Commitment | An accepted future obligation with quantity or service, time window, conditions, and status |
| Reservation | A capacity claim supporting a commitment; not stock or delivered service |
| Installed capacity | Maximum declared capacity before availability derating |
| Usable capacity | Installed capacity multiplied by the declared availability factor |
| Residual capacity | Usable capacity remaining after the declared accepted or reserved load, with the accounting convention stated |
| Congestion | A binding load–capacity interaction that changes completion, delay, loss, or feasibility |
| Queue | Admitted but unserved demand under a declared service discipline |
| Admitted queue arrival | Newly presented demand accepted into a queue; rejected or still-pending demand remains outside the queue |
| Rejected request | Newly presented demand denied admission and recorded separately, never subtracted from an admitted queue |
| Delay | Declared time between relevant events; component durations must be non-overlapping or explicitly defined as additive |
| Delayed effect | A registered future physical change or measurement obligation with provenance and due epoch |
| Evaluation horizon | The terminal epoch included in a stated comparison |
| Placement | The declared node, region, or physical location of an action or provider |
| Route | A Part VII object provisionally represented here by a typed path |
| Rerouting | Prospective replacement of an unfinished route suffix after a declared event |
| Phase | Position relative to a verified recurrent reference; undefined without such a reference |
| Uncertainty set | Prospectively declared admissible values or disturbances, without an implied probability |
| Viability margin | A dimensioned constraint margin, normalized only by a declared compatible scale |
| Resilience | Performance or viability under named disturbances and recovery conditions, including relevant costs |
| Coordination cost | Typed physical and institutional resources or burdens required to coordinate |
| Institutional allocation | Priority, access, settlement, residual, responsibility, or ownership rule not inferred from physical EBU |
| Serializable schedule | A joint schedule whose declared joint semantics equal the applicable live-state composition of its child transformations under the assumptions of a declared serializability statement; commutativity alone is insufficient |

## 14. Explicit open-problem register

Every item below is unresolved. The register freezes questions, not answers or
authorization.

| ID | Open problem |
|---|---|
| O-DC-1 | What is the smallest state that remains sufficient when commitments, ageing, failures, delayed effects, and policy memory interact? |
| O-DC-2 | Which continuous-time formulation preserves the bridge while resolving simultaneous events and discretization dependence? |
| O-DC-3 | Which Part VII route definitions, distance measures, loss laws, and actor closures should replace the provisional graph abstraction? |
| O-DC-4 | How should topology-changing actions be grouped when they alter the supports or feasibility of later actions? |
| O-DC-5 | How should reservations be guaranteed when capacity uncertainty is correlated across providers and time? |
| O-DC-6 | Which queue disciplines are physically efficient, robust, and institutionally acceptable, and how should their priorities remain separate? |
| O-DC-7 | What delay bounds survive bursty multicommodity traffic, conversions, deadlines, and failures? |
| O-DC-8 | How should pending delayed effects constrain comparison and settlement beyond a finite horizon? |
| O-DC-9 | When can a delayed effect be causally attributed rather than merely linked by provenance? |
| O-DC-10 | Which dynamic schedule comparators are admissible when actions change quantities, routes, or group membership over time? |
| O-DC-11 | How should equal-distortion endpoints be ranked when future viability, topology, or capacity differs? |
| O-DC-12 | Can multi-resource viability be summarized without hiding dimensioned tradeoffs or institutional weights? |
| O-DC-13 | Which uncertainty sets are scientifically justified, and how should model mismatch outside them remain visible? |
| O-DC-14 | What robustness guarantees remain possible with stale, local, privacy-limited, or strategically reported measurements? |
| O-DC-15 | Under which conditions does additional connectivity improve resilience rather than increase cascade exposure or resource burden? |
| O-DC-16 | What prospective diagnostics distinguish propagation waves from diffusion, common forcing, dispatch sequences, and plotting artefacts? |
| O-DC-17 | Which topology spectra, if any, predict physical coordination outcomes after units, direction, weights, and dynamics are included? |
| O-DC-18 | Over what registered system families could any scaling claim be meaningful, and which competing forms must be retained? |
| O-DC-19 | Is any recurrence, self-similarity, fractal dimension, or Fibonacci-like structure mechanistically justified rather than selected after inspection? |
| O-DC-20 | How should coordination overhead, privacy, contestability, and institutional power be represented without converting them into invented physical units? |
| O-DC-21 | When are child causal contributions identifiable in dynamic groups whose topology, delay, and membership change? |
| O-DC-22 | Which settlement and residual rules preserve audit closure without being mislabelled as measured physical causality? |
| O-DC-23 | Can a no-harm policy be certified when measurements and models are uncertain and affected groups have non-scalar objectives? |
| O-DC-24 | What proof methods are suitable for feasibility, invariance, serializability, queue bounds, typed stock-flow balance, capacity compliance, and robustness in the final model? |
| O-DC-25 | How should framework provenance and write-once result mechanics remain compatible with dynamic receipts and later authorized corrections? |
| O-DC-26 | Which analytical fixtures should be frozen before any dynamic implementation, without beginning the separate parallel-testing programme? |

## 15. Part VIII, *Dynamic Coordination Fields and Society Geometry*: chapter role and handoff

This foundation supplies the common vocabulary for the planned Part VIII
chapters on objects, signals, objectives, timing, phase, placement, topology,
delay, propagation, waves, spectra, interaction, resilience, scaling,
recurrence, fractals, and society-scale coordination.

It does not supply evidence for those chapters. A later chapter may state a
surviving theorem or empirical pattern only after its assumptions, protocol,
implementation, validation, execution, and interpretation have crossed their
separate authorization boundaries.

Part VI remains primary for joint transitions, comparators, group receipts,
and settlement closure. Part VII remains primary for routes, distance, route
actors, and spatial infrastructure. Part VIII, *Dynamic Coordination Fields
and Society Geometry*, is primary for time-dependent coordination over those
foundations.

## 16. Proposed scope of a separately authorized unified Python research-framework specification

The next framework deliverable should be a specification, not implementation.
Subject to separate authorization, it should freeze:

1. immutable, versioned schemas for physical state, topology, queues,
   admission decisions, rejections, commitments, reservations, delayed
   effects, measurements, uncertainty, and decision-relevant controller
   memory;
2. typed provider, resource, region, edge, route, action-instance, and schedule
   identifiers with dimensional validation;
3. explicit interfaces to the imported distortion, action, grouping,
   comparator, group-EBU, non-additivity, interaction, and receipt objects
   without redefining them;
4. the exact deterministic event order, clock semantics, horizon semantics,
   state-update ownership, transition-construction versus commit/accounting
   semantics, and rules preventing duplicate application of simultaneous
   events or physical effects;
5. capacity admission, rejection, allocation, admitted-queue accounting,
   congestion, expiry, loss, conversion, failure, repair, reservation
   shortfall, rerouting, and non-overlapping or explicitly additive delay
   contracts;
6. an in-transit and delayed-effect mechanism that retains provenance and
   exposes pending or unresolved effects at every horizon;
7. open-loop schedule and closed-loop policy interfaces with augmented
   controller-memory state and machine-checkable information boundaries
   preventing future-data and outcome leakage;
8. objective-vector, feasibility, Pareto, lexicographic, epsilon-constraint,
   and prospectively declared scalarization records;
9. dimensional and regional typed stock-flow checks, including declared
   external boundary inflows, parent-boundary cancellation, explicit
   conversion coefficients, and a separate capacity-compliance check;
10. robust uncertainty interfaces that separate sets, probabilities,
    measurement error, model discrepancy, and out-of-set events;
11. dynamic extensions to group receipts, child preservation, topology and
    schedule provenance, commitments, reroutes, delayed effects, and
    coordination costs;
12. proof-obligation and property-check interfaces for the unproved
    feasibility, invariance, exact joint-composition serializability, typed
    stock-flow balance, capacity compliance, delay, reservation, finite
    single-source/single-sink rerouting, robustness, and no-harm candidates,
    plus exhaustive finite-class or proof-based falsification for existential
    schedule hypotheses;
13. hand-derived analytical fixtures with exact expected static values, kept
    distinct from scientific simulations and candidate experiments;
14. canonical configuration hashing, environment capture, immutable manifests,
    row-level traces, error states, recovery rules, and write-once result
    mechanics;
15. strict stage controls separating specification, implementation,
    non-scientific validation, preregistration, scientific execution,
    interpretation, and publication; and
16. explicit exclusions preserving every frozen Gate 1D-C source and incident
    state and preventing the framework work from beginning the deterministic
    parallel-testing specification.

That unified Python research-framework specification is a separately
authorized Phase B deliverable. It has not been created, implemented, tested,
or begun by this analytical foundation.
