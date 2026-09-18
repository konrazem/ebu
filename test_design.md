> **Current-scope notice — 18 September 2026.** Superseded prospective test design. The Local Gaussian programme does not inherit its service/controller requirements. This body is preserved for trace, not an instruction to implement it.
>
> Current navigation: [CURRENT_SCIENTIFIC_AUTHORITY.md](CURRENT_SCIENTIFIC_AUTHORITY.md).
> The pre-existing body below is preserved from checkpoint `924a4d9`, with only its missing final newline normalized.

# EBU SCIENTIFIC TEST DESIGN TASK
# Build the Python experimental harness only after the mathematical foundation gate is accepted

Repository:

`/Users/konrad.grzyb/code/ebu`

This task defines the intended scientific-test architecture for EBU.

It is not permission to silently replace committed repository authority.

Before implementation, read the authoritative repository documents and reconcile this specification against them. If this specification conflicts with committed authority, stop and report the conflict rather than silently choosing one side.

The purpose of the Python programme is to create a small, immutable, reproducible physical world in which different local control rules face exactly the same externally generated demand history.

The main scientific question is:

> Can the EBU local field rule maintain a physically viable/homeostatic system while continuing to deliver meaningful service under persistent external disturbance?

The experiment must not give EBU access to global state, future demand, future rollout, or the final research metric.

---

# 0. Core conceptual architecture

The test must preserve the following separation.

## Physical layer

Real resources exist in physical state variables.

Real actions move or transform those resources.

Physical conservation, capacities, topology, and hard feasibility live here.

## Homeostatic field layer

The EBU potential evaluates the represented physical state relative to declared homeostatic / reserve conditions.

The field does not itself perform actions.

The correct conceptual statement is:

\[
\boxed{
\text{The action is the physical resource transformation.
The field is the instrument used to evaluate that transformation.}
}
\]

## Receipt layer

A verified physical action receives an EBU value from the change it creates in the declared field.

For finite actions this is an endpoint difference / path-integral object.

## Interaction-analysis layer

Möbius decomposition is used to discover and verify irreducible interaction structure.

It is not the ordinary runtime actor-settlement mechanism.

## Scientific-evaluation layer

Global metrics such as total burden, total service, survival, and failure are calculated after actions for research/audit.

Runtime local actors must not inspect these global research quantities.

---

# 1. Atomic physical-action principle

Do not model one action as the entire causal universe associated with it.

For example, if pumping water uses electricity, do not define one gigantic action containing:

- water transport;
- electricity generation;
- fuel extraction;
- fuel conversion;
- waste production;
- every upstream consequence.

Instead represent physically meaningful transformations as separate linked actions.

Conceptually:

\[
\text{fuel transformation}
\rightarrow
\text{electricity generation}
\rightarrow
\text{electricity use}
\rightarrow
\text{water movement}.
\]

Each transformation can have:

- its own physical state change;
- its own local field evaluation;
- its own receipt;
- its own timestamp / epoch.

This is essential.

EBU should remain compositional and local.

Do not recursively expand one receipt into every upstream and downstream cause.

---

# 2. First experimental world's physical scope

The first official test world should be deliberately minimal.

Unless committed authority requires otherwise, use:

\[
\boxed{\text{one conserved scalar resource}}
\]

distributed over a finite local network.

Examples of the abstract scalar could later represent:

- water;
- stored energy;
- material stock;
- some other conserved carrier.

Do not give the scalar a monetary interpretation.

The first experiment is about the mathematics and control behaviour, not about reproducing a complete economy.

---

# 3. Closed conservative world

For the first world, prefer lossless local transfer:

\[
\eta_e=1.
\]

For a transfer from node \(i\) to node \(j\) of quantity \(q\):

\[
x_i' = x_i-q,
\]

\[
x_j' = x_j+q.
\]

Therefore:

\[
\sum_i x_i'=\sum_i x_i.
\]

The implementation must check conservation after every executed joint event.

Define a numerical conservation residual such as

\[
r_{\rm cons}
=
\left|
\sum_i x_i^{t+1}
-
\sum_i x_i^t
\right|.
\]

The permitted tolerance must be explicit.

A run with conservation failure beyond tolerance is:

\[
\boxed{\text{INVALID}}
\]

rather than an EBU scientific failure.

Do not allow unexplained resource disappearance.

If future experiments introduce losses, then the lost quantity must either:

1. appear in another explicit physical coordinate such as heat/waste;
2. cross a declared model boundary; or
3. follow another repository-authoritative accounting mechanism.

Do not silently destroy resource.

---

# 4. No automatic self-healing world

The physical world must not generate corrective demand simply because a coordinate is below or above its homeostatic band.

That would build the desired outcome into the world.

External demand must be independent of:

- \(V\);
- \(\nabla V\);
- reserve violation;
- whether fulfilling the request improves homeostasis;
- which controller is currently being tested.

For the first world, unless authority already defines autonomous dynamics, prefer:

\[
u(x)=0
\]

between controlled physical actions.

Then the stochastic demand itself provides persistent disturbance.

Autonomous regeneration may be studied later as a separate fixed physical mechanism.

---

# 5. Hard physical constraints versus homeostatic boundaries

Do not confuse physical impossibility with homeostatic undesirability.

Each state coordinate should have at least two conceptually different classes of limits.

## Hard physical domain

For example:

\[
0\le x_i\le K_i.
\]

Violating this is physically impossible.

## Homeostatic / desirable range

For example:

\[
L_i\le x_i\le U_i.
\]

A state may physically exist outside this region but be undesirable or dangerous.

Reserve conditions such as \(R_i\) are part of the declared viability model, not automatically hard physical impossibility.

This distinction must exist explicitly in the code.

---

# 6. Homeostatic potential

Use the currently authoritative EBU potential for the first experiment.

If the current authority remains the separable quadratic burden, conceptually:

\[
V(x)=\sum_i v_i(x_i)
\]

with terms such as

\[
v_i(x_i)
=
\alpha_i[L_i-x_i]_+^2
+
\beta_i[x_i-U_i]_+^2
+
\chi_i[R_i-x_i]_+^2.
\]

Do not invent new weights or boundaries during implementation.

All parameters must come from an explicitly versioned experiment configuration / preregistration.

The architecture should permit future factor potentials of the form

\[
V(x)=\sum_\alpha \phi_\alpha(x_{S_\alpha}),
\]

but the first experiment does not need to solve the general nonseparable case unless repository authority already requires it.

The potential is not total physical energy.

It measures represented homeostatic burden relative to the declared field model.

---

# 7. Frozen synchronous tick

Every ordinary simulation tick must follow one clear protocol.

At the start of tick \(t\):

\[
x_t
\]

is frozen for proposal/evaluation purposes.

Every local actor receives only the local information permitted by its controller.

All candidate actions for that tick are generated from the same frozen state.

Do not update one node and then allow another nominally simultaneous actor to see that partially updated state.

The sequence is:

1. freeze state;
2. reveal externally generated demand for this tick;
3. generate local requests / proposals;
4. apply hard physical feasibility;
5. apply provider / P1C permission;
6. jointly resolve shared-source constraints;
7. obtain accepted action vector;
8. settle the accepted simultaneous group;
9. execute the accepted joint physical change;
10. verify conservation and accounting;
11. compute research metrics;
12. advance to the next state.

The physical successor is conceptually:

\[
x_{t+1}
=
x_t+\sum_a\Delta x_a^{\rm accepted}.
\]

Do not use round-robin execution as the canonical synchronous model.

---

# 8. Requested, permitted, accepted, measured, delivered

Keep these quantities distinct.

For every action/request record at least:

\[
q^{\rm requested},
\]

\[
q^{\rm permitted},
\]

\[
q^{\rm accepted},
\]

\[
q^{\rm measured},
\]

\[
q^{\rm delivered}.
\]

Do not calculate final receipts from the original request if the physical resolver changed the quantity.

Settlement must correspond to what actually occurred.

A requested quantity of 10 that resolves to 6 must settle the physical event of 6.

---

# 9. Provider permission and shared-source resolution

A request does not automatically create a right to consume all physically available source stock.

The physical/provider layer must determine how much may actually be served.

When multiple outgoing actions share a source, apply the repository-authoritative P1C / shared-source resolver.

If the aggregate requested quantity exceeds the source's safe authorised export budget, jointly resolve the outgoing actions.

If current authority uses proportional scaling, implement exactly that.

Do not turn this physical resolver into a social-priority or EBU-value theorem.

It is a physical permission mechanism.

---

# 10. The ordinary action object

Each physical action should carry enough information to identify:

- source;
- destination;
- resource/carrier;
- requested quantity;
- accepted quantity;
- physical direction/vector;
- start epoch;
- end epoch if duration is represented;
- responsible action/actor identity;
- local topology edge;
- physical permission evidence;
- receipt.

Avoid attaching global world state to an action object unless strictly needed for offline audit.

---

# 11. Process burden \(C\) in the first world

For the first conservative scalar-transfer experiment, prefer:

\[
\boxed{C_a=0}
\]

unless committed authority explicitly requires otherwise.

The reason is not that real actions have no energetic or material consequences.

The reason is that additional physical transformations should normally appear as their own atomic actions rather than being hidden inside another action's generic process penalty.

For example:

water transfer receipt != entire electricity supply-chain receipt.

If electricity use is modeled, model an electricity action separately.

Therefore do not invent:

- labour costs;
- monetary costs;
- arbitrary transaction penalties;
- synthetic transport penalties;
- generic "effort" values.

inside \(C_a\).

A future experiment can study genuine residual process burden separately.

---

# 12. Exact finite EBU for one action

For a finite physical action, preserve the authoritative exact finite EBU formulation.

For the field component:

\[
F_a
=
V(z)-V(x_{\rm post}).
\]

Where the path representation is valid:

\[
F_a
=
-\int_{\gamma_a}\nabla V(x)^Tdx.
\]

For an edge transfer under the existing local-force notation this should agree with the authoritative local force integral.

Do not replace the exact finite receipt by a frozen first-order derivative approximation in the canonical test.

Approximations may be tested later under SD-04 or equivalent approximation studies.

---

# 13. Simultaneous common-path settlement

This is a mandatory mathematical gate before the long-run experiment.

Suppose the accepted simultaneous group is

\[
G=\{1,\ldots,m\}
\]

with accepted physical action increments

\[
\Delta x_1,\ldots,\Delta x_m.
\]

Define

\[
\Delta x_G
=
\sum_a\Delta x_a.
\]

For the synchronous constant-rate tick, the proposed natural path is

\[
x(\lambda)
=
z+\lambda\Delta x_G,
\qquad
0\le\lambda\le1.
\]

For each action define the field receipt candidate

\[
R_a^V
=
-\int_0^1
\nabla V(x(\lambda))^T
\Delta x_a
\,d\lambda.
\]

The foundation must verify:

\[
\boxed{
\sum_aR_a^V
=
V(z)-V(z+\Delta x_G)
}
\]

under the declared assumptions.

Interpret this physically as:

> each physical action receives the accumulated local marginal-field contribution of its own action direction while all simultaneous actions move together along the same actual/common path.

Do not interpret it as:

- a fairness vote;
- a Shapley split;
- a post-hoc synergy allocation;
- an arbitrary game-theory convention.

The desired interpretation is:

\[
\boxed{\text{work-like physical path integral}}
\]

for the represented burden field.

---

# 14. No interaction bank

Do not create persistent pair/triple/etc. balances simply because actions interact.

If:

\[
F(A)=8,
\]

\[
F(B)=7,
\]

and

\[
F(AB)=20,
\]

then the interaction term

\[
I(AB)=5
\]

means:

\[
20=8+7+5.
\]

It does not mean that another 5 must be created after the 20 has already been measured.

The relational effect is already present in the realised joint field change.

Therefore:

\[
\boxed{\text{Möbius interaction is not additional EBU issuance.}}
\]

Persistent physical capacity should exist only if represented by an actual persistent state coordinate.

---

# 15. Möbius role

Möbius is not the ordinary runtime settlement engine.

Its primary roles are:

1. interaction detection;
2. pair/higher-order topology discovery;
3. hyperedge / motif analysis;
4. recursive-topology validation;
5. independent reconstruction of exact group field value;
6. selected-event scientific audit.

For selected small events, define the subset field-value function

\[
F(S)=V(z)-V(x_S),
\]

where every subset begins from the same frozen baseline and uses the same physical protocol.

Important:

each subset may resolve to a different accepted quantity.

For example:

\[
\rho(A)=5
\]

while

\[
\rho(AB)=(3,3).
\]

This is valid if the same physical resolver generates those outcomes.

Do not force subset quantities to equal the quantities present in the full group.

---

# 16. Möbius versus path receipts

The following identity is the desired foundation/audit relation:

\[
\boxed{
V(z)-V(x_G)
=
-\int_{\gamma_G}\nabla V^Tdx
=
\sum_aR_a^V
=
\sum_{S\le G} I_F(S)
}
\]

where \(I_F\) denotes Möbius interaction coefficients of the field-value function.

These are different decompositions of the same group field total.

Do not require:

\[
R_a^V
\]

to equal some fixed subset sum of Möbius coefficients.

The interpretations differ:

Path receipts answer:

> how did the realised physical event accumulate field-value change along each actual action direction?

Möbius answers:

> what irreducible counterfactual interaction structure exists among subsets?

Only the reconstructed group total must agree.

---

# 17. Boolean versus feasible-poset Möbius

Do not assume every interaction family is a full Boolean powerset.

If repository authority supports a non-Boolean feasible configuration poset, use it.

A physically valid zero-execution configuration can still exist.

A structurally impossible / undefined configuration must not be invented and assigned value zero merely to complete a Boolean cube.

Use the actual repository-authoritative poset Möbius function when required.

The long-run runtime does not need to enumerate the full poset every tick.

---

# 18. Foundation conformance gate

Before running any 20,000-tick scientific campaign, build tiny exact fixtures.

These tests are mandatory.

## F1 — one finite action

Verify:

\[
\text{endpoint difference}
=
\text{local/path integral}.
\]

## F2 — two symmetric simultaneous actions

Verify:

\[
\text{endpoint}
=
\text{group path integral}
=
\text{sum per-action path receipts}.
\]

If Möbius audit is enabled also verify reconstruction.

## F3 — asymmetric simultaneous actions

Use unequal quantities and/or local fields.

Verify that the settlement does not artificially produce equal receipts.

## F4 — positive interaction

Construct a legitimate fixture where

\[
F(AB)>F(A)+F(B).
\]

Verify that the positive interaction is already included in joint path settlement.

Do not issue it again.

## F5 — negative interaction

Construct a fixture where

\[
F(AB)<F(A)+F(B).
\]

Verify that independent frozen quotes would overstate the true group field result.

## F6 — genuine three-way interaction

Create a small tractable fixture where a three-way term can be independently checked.

## F7 — shared-source resolution

Verify that subset counterfactuals may resolve to different quantities.

## F8 — conservation

Verify exact closed-system resource conservation.

## F9 — long/overlapping epochs

Verify live-state segmentation and receipt telescoping.

## F10 — Möbius reconstruction

Verify inverse Möbius returns the exact declared group field value.

Include both Boolean and feasible-poset cases if repository authority requires both.

---

# 19. Deliberately broken negative controls

The conformance suite must prove that incorrect implementations fail.

Include deliberate errors such as:

- using requested quantity instead of accepted quantity;
- evaluating from stale state;
- applying an arbitrary sequential order to a simultaneous event;
- settling independent same-baseline quotes as if additive;
- adding Möbius interaction on top of already exact group EBU;
- changing baseline between subset counterfactuals;
- silently changing the potential definition;
- violating source capacity;
- losing resource from the closed system;
- allowing a controller to read global \(V\);
- allowing a controller to inspect future demand.

A conformance system that passes deliberately broken implementations is not sufficient.

---

# 20. Long-duration physical actions

The real world contains actions with duration.

The model must not assume that a field observed at the beginning remains valid forever.

General conceptual form:

\[
R_a^V
=
-\int_{t_a^{start}}^{t_a^{end}}
\nabla V(x(t))^T
\dot x_a(t)\,dt.
\]

If action A acts from \(t=0\) to \(10\), while action B begins at \(t=6\):

- A reads the field during its actual progression;
- B begins from the live field state at \(t=6\);
- from \(t=6\) to \(10\), both contribute to the same evolving state;
- after A ends, B continues from the resulting live state.

For discrete simulation, represent this as sufficiently fine live epochs.

Do not freeze a long-duration action's original field indefinitely.

If future evolution depends on historical information not present in the current state, the state representation is incomplete and must be extended.

---

# 21. Long-duration testing is separate from first runtime simplicity

The main long-run cellular experiment may initially use actions that complete within one tick.

This is acceptable because the duration/history theorem is independently tested in dedicated fixtures.

Do not complicate the first 20,000-tick world merely to demonstrate every possible duration phenomenon simultaneously.

---

# 22. Immutable world principle

Once the official long-run experiment is preregistered, freeze the world definition.

The following must not change between controller arms:

1. topology;
2. state variables;
3. capacities;
4. physical transition law;
5. conservation law;
6. homeostatic boundaries;
7. reserve boundaries;
8. EBU potential;
9. physical resolver;
10. path-settlement law;
11. demand history;
12. initial state.

Different controller arms must experience the same world.

Do not tune the environment separately for EBU and comparison policies.

---

# 23. Initial state

The official sustained-demand runs begin from a valid/homeostatic state:

\[
x_0\in\mathcal H.
\]

Think of this as the solved Rubik's-cube state.

The experiment asks whether a controller can preserve useful structure under persistent externally imposed disturbance.

Do not begin EBU runs from a specially advantageous state unavailable to other controllers.

---

# 24. External demand generation

Demand must be exogenous.

Generate the entire demand sequence independently of the tested controller.

Use a seeded random generator.

The generated sequence must be reproducible.

For every seed:

1. generate the complete demand history once;
2. store/hash it;
3. replay the identical history for every controller.

This is common-random-number experimental design.

No controller may alter future demand generation.

The first implementation should support configurable demand models rather than hard-code one undocumented distribution.

Candidate models to support include:

- bounded discrete/i.i.d. demand;
- bounded Poisson-like arrivals;
- bursty Markov-modulated demand.

But do not choose the canonical scientific distribution or its parameters silently in code.

Those must be preregistered.

---

# 25. Demand must not encode homeostatic correction

Never implement logic such as:

> if node is below \(L\), generate demand that sends resource toward it.

That would make the environment itself homeostatically intelligent.

Requests should represent independent external needs/disturbances.

The controller decides how to respond.

---

# 26. Same demand for all controllers

For a given experimental trajectory:

\[
D_{0:T}
\]

must be identical across all controller arms.

Do not use different random seeds for different controllers.

Do not regenerate demand after a controller fails unless the scientific protocol explicitly defines censoring.

---

# 27. Comparison controllers

At minimum support the following controller families.

The exact formulas must be documented and preregistered.

They must be plausible controls, not intentionally poor strawmen.

## C0 — no-action / reject control

Reject all optional service requests.

Purpose:

- sanity check;
- demonstrate that trivial state preservation can coexist with zero service.

This controller cannot be considered scientifically successful merely because it preserves homeostasis.

## C1 — local greedy controller

A simple local policy using only immediate local information and physical feasibility.

It must not use the EBU field.

Its exact local heuristic must be declared.

## C2 — myopic service controller

Attempt to maximise immediate demand satisfaction subject to hard physical feasibility.

Do not give it future information.

Purpose:

- show what happens when current service is prioritised without EBU homeostatic field guidance.

## C3 — reserve-aware non-field controller

Use explicitly declared local reserve/safety constraints but not the EBU potential gradient/force.

Purpose:

- separate the value of basic reserve protection from the richer EBU field.

## C4 — EBU local-field controller

Use the authoritative local EBU marginal/force mechanism.

It receives no global \(V\).

It receives no future rollout.

It receives no future demand.

All controllers must use the same physical resolver after producing their proposals.

---

# 28. Runtime locality rule

The EBU controller must not inspect:

- global \(V(x)\);
- distant unrelated states;
- global average health;
- future demand;
- future simulated rollout;
- oracle feasibility;
- other controller outcomes;
- final research score.

It may use only repository-authorised local information.

The scientific evaluator may compute global \(V\) after execution.

This distinction must be enforced by architecture, not merely by documentation.

Prefer interfaces that make forbidden global reads impossible or obvious.

---

# 29. Offline feasibility oracle

Scientific interpretation needs to distinguish:

\[
\text{controller failure}
\]

from

\[
\text{physically impossible challenge}.
\]

For a sufficiently small world, implement an offline/reference feasibility oracle if computationally tractable.

The oracle may use global information and future demand because it is not a runtime controller.

Its purpose is only to classify whether the registered challenge could, in principle, have met the preregistered service/viability target.

Never expose oracle outputs to the tested controllers.

---

# 30. Long-run horizon

The intended sustained-disturbance experiment uses a long fixed horizon, such as:

\[
T=20\,000\text{ ticks},
\]

but the exact official horizon must come from preregistration.

Do not stop merely because the system temporarily returns to homeostasis.

New external demand is still coming.

Early termination is permitted only for:

- mathematically conclusive invalidity;
- unrecoverable physical failure under the preregistered definition;
- other explicitly preregistered absorbing conditions.

---

# 31. Service metrics

State preservation alone is not sufficient.

Record at least:

\[
Q_{\rm requested},
\]

\[
Q_{\rm permitted},
\]

\[
Q_{\rm accepted},
\]

\[
Q_{\rm measured},
\]

\[
Q_{\rm delivered},
\]

\[
Q_{\rm unmet}.
\]

Also derive quantities such as:

\[
\text{service ratio}
=
\frac{Q_{\rm delivered}}{Q_{\rm requested}}
\]

when denominator is nonzero.

Do not construct one arbitrary weighted score combining service and homeostasis unless separately justified.

Report the dimensions separately first.

---

# 32. Viability/homeostatic metrics

Record at least:

- \(V(x_t)\);
- number of nodes below \(L_i\);
- number above \(U_i\);
- reserve violations;
- time outside viable bands;
- maximum violation depth;
- duration of violations;
- first failure time where applicable;
- terminal state;
- unrecoverable-state flag if defined.

Keep raw trajectories so later analysis does not depend on one preselected summary statistic.

---

# 33. Physical/accounting metrics

Record at least:

- total resource;
- conservation residual;
- requested versus accepted quantities;
- source-capacity violations;
- per-action field receipt;
- total group field receipt;
- endpoint field difference;
- settlement closure residual.

For audited events also record:

- Möbius reconstruction;
- interaction coefficients;
- Möbius closure residual.

---

# 34. Settlement closure metric

For each simultaneous event define a residual such as:

\[
r_{\rm settle}
=
\left|
F(G)-\sum_aR_a^V
\right|.
\]

Require it below an explicitly registered numerical tolerance.

For selected Möbius-audited events also compute:

\[
r_{\rm Mobius}
=
\left|
F(G)-\sum_{S\le G}I_F(S)
\right|.
\]

A settlement/conformance violation beyond tolerance makes the affected run:

\[
\boxed{\text{INVALID}}
\]

not EBU-FAIL.

---

# 35. Run classifications

Every official trajectory must receive one of four top-level scientific statuses.

## SUCCESS

The controller completes the registered challenge while satisfying the preregistered:

- physical validity;
- viability requirements;
- minimum service conditions.

## EBU-FAIL

For the EBU controller specifically:

the EBU policy violates the preregistered target in a challenge independently shown to be physically controllable under the registered conditions.

Examples may include:

- avoidable reserve collapse;
- avoidable service collapse;
- destructive cycle;
- avoidable entry into an unrecoverable state.

Do not label a physically impossible demand history EBU-FAIL.

## PHYSICALLY-IMPOSSIBLE

The preregistered service/viability target cannot be achieved by any physically admissible policy according to the independent challenge certificate/oracle.

## INVALID

The experiment itself broke its assumptions.

Examples:

- conservation failure;
- incorrect settlement closure;
- forbidden global controller access;
- wrong demand replay;
- protocol mismatch;
- corrupted event log;
- numerical failure beyond registered tolerance.

Invalid results must not be counted as scientific successes or failures.

---

# 36. No "reject everything" success loophole

A controller that preserves perfect homeostasis by refusing every demand has not demonstrated useful regulation.

The preregistration must include a service requirement.

Therefore success must involve both:

\[
\boxed{\text{viability preservation}}
\]

and

\[
\boxed{\text{meaningful delivered service}}.
\]

Do not hide the tradeoff inside an arbitrary weighted objective.

Report both axes.

---

# 37. Wallet/accounts

Do not invent wallet semantics during this physical test implementation.

First inspect committed authority.

If wallets are not required for the first physical validation, keep the core world/controller/settlement harness independent of wallets.

If an authoritative account layer is later enabled:

- accounts must be finite/persistent according to the applicable authority;
- interaction terms must not automatically create pair/triple wallets;
- path receipts belong to actual physical actions/actors according to the proved settlement law;
- account behaviour must not alter the physical conservation law.

The first scientific question should remain testable without unresolved institutional accounting assumptions where possible.

---

# 38. Reproducibility

Every official run must record:

- repository commit SHA;
- experiment-spec version/hash;
- controller version;
- world configuration hash;
- topology hash;
- initial-state hash;
- demand-sequence seed;
- demand-sequence hash;
- numerical tolerances;
- Python/environment version;
- run identifier.

A result must be reproducible from saved inputs.

---

# 39. Event log

Produce a machine-readable event log.

For every tick include at least:

- tick index;
- pre-state hash / state;
- demand events;
- proposals;
- requested quantities;
- physical permissions;
- accepted quantities;
- executed/measured quantities;
- state increments;
- post-state;
- \(V_{\rm pre}\);
- \(V_{\rm post}\);
- per-action receipts;
- group receipt;
- conservation residual;
- settlement residual;
- controller identifier;
- invalidity flags.

Do not require full Möbius decomposition in every tick log.

Selected Möbius audits can have a separate detailed record.

---

# 40. Suggested Python architecture

Keep components separate enough that scientific assumptions cannot silently bleed together.

Use modules/classes corresponding conceptually to:

1. physical world/state;
2. topology;
3. potential/field;
4. action representation;
5. demand generator;
6. physical permission/resolver;
7. controllers;
8. settlement/path integration;
9. conservation checks;
10. Möbius audit;
11. experiment runner;
12. metrics/classification;
13. reproducibility/configuration.

Prefer pure functions and immutable/frozen pre-state snapshots where practical.

Do not let controllers directly mutate world state.

The runner owns state transition.

---

# 41. Determinism and random-number discipline

The only intended stochasticity in the first experiment should come from explicitly seeded external demand generation unless another source is preregistered.

Do not call global uncontrolled random functions throughout the codebase.

Use explicit random-generator objects.

Given:

- same initial state;
- same world config;
- same controller;
- same demand stream;

the simulation result must be deterministic.

---

# 42. Numerical integration

Do not silently substitute rough numerical quadrature for a mathematically exact receipt when an analytic or piecewise-exact method is available.

For the current piecewise-quadratic potential, investigate exact/piecewise analytic path integration.

If numerical integration is used:

- method must be explicit;
- tolerance must be explicit;
- error must be checked against endpoint closure;
- tolerance must be tighter than the scientific effect sizes being interpreted.

Endpoint difference remains an independent closure check.

---

# 43. Research separation

Keep three evidence classes distinct.

## Mathematical/conformance evidence

Examples:

- endpoint = path;
- path shares close to group total;
- Möbius reconstruction;
- conservation.

## Software evidence

Examples:

- implementation reproduces exact fixtures;
- deterministic replay works;
- negative controls fail correctly.

## Scientific behavioural evidence

Examples:

- EBU preserves homeostasis longer;
- EBU delivers more service at similar violation rates;
- EBU enters fewer unrecoverable states.

Do not claim scientific success merely because mathematical identities pass.

---

# 44. Preregistration before official long-run runs

Before official evidence is generated, freeze a versioned experiment specification containing:

- canonical topology;
- node count;
- capacities;
- homeostatic bands;
- reserve bands;
- potential parameters;
- demand model;
- demand parameters;
- seed list / trajectory count;
- controller definitions;
- physical resolver;
- initial state;
- horizon;
- numerical tolerances;
- success criteria;
- failure criteria;
- physically-impossible criteria;
- metrics;
- early-stop rules;
- Möbius-audit sampling policy.

Do not tune these after inspecting EBU results and then present the tuned run as preregistered evidence.

Exploratory development runs must be clearly marked exploratory.

---

# 45. SD programme protection

Do not silently rename this experiment SD-01 or replace any canonical SD study.

First inspect committed programme authority.

If existing SD-01 is deterministic or already registered differently, this stochastic sustained-demand world requires:

- a prospective new registration;
- or an explicit approved amendment.

Do not rewrite historical study identity.

---

# 46. First official campaign should remain small enough to understand

Do not begin with a giant realistic economy.

The first world must be small enough that:

- every action can be audited;
- subset interactions can be checked on selected events;
- conservation is obvious;
- oracle/reference analysis is feasible;
- failures can be explained physically;
- the full state can be inspected.

Complexity can increase only after the small world passes the foundation and falsification tests.

---

# 47. What must NOT be introduced in the first world

Do not add unless specifically authorised:

- money;
- prices;
- market clearing;
- trading;
- speculative expectations;
- learning agents;
- RL;
- social preference scores;
- fairness weights;
- arbitrary EBU prices;
- arbitrary utility functions;
- giant supply chains;
- interaction wallets;
- endogenous demand designed to restore homeostasis;
- global runtime optimisation.

These would confound the first scientific question.

---

# 48. Main scientific comparison

The experiment should ultimately generate, for every common demand trajectory, comparable trajectories such as:

\[
V_{\rm EBU}(t),
\]

\[
V_{\rm greedy}(t),
\]

\[
V_{\rm service}(t),
\]

\[
V_{\rm reserve}(t),
\]

alongside delivered-service trajectories.

The objective is not to assume that EBU will win.

The objective is to determine whether it actually demonstrates a useful local-regulation property under conditions where:

- the world does not help it;
- demand does not know the potential;
- controllers have the same physical resources;
- future information is unavailable;
- conservation is enforced;
- trivial no-service preservation is not sufficient.

A negative result is scientifically valid.

---

# 49. Order of implementation

Build in this order.

## Phase 1 — pure physical world

Implement:

- state;
- topology;
- local transfer;
- hard feasibility;
- conservation.

No EBU controller yet.

Prove deterministic physical transitions.

## Phase 2 — potential and local field

Implement current authoritative:

- \(V\);
- local marginals;
- edge forces.

Verify against hand-computed fixtures.

## Phase 3 — one-action exact receipt

Verify:

\[
\text{endpoint}
=
\text{path integral}.
\]

## Phase 4 — simultaneous path settlement

Implement group path and per-action receipts.

Verify exact closure.

Do not proceed if this gate fails.

## Phase 5 — Möbius audit

Implement selected-event counterfactual decomposition.

Verify:

\[
\text{Möbius reconstruction}
=
\text{same group field total}.
\]

Möbius remains an audit/research path, not the per-tick settlement dependency.

## Phase 6 — physical resolver / P1C

Implement shared-source permissions and accepted quantities.

Re-run settlement fixtures using accepted rather than requested quantities.

## Phase 7 — demand replay

Implement deterministic seeded demand sequences and identical replay across controllers.

## Phase 8 — baseline controllers

Implement no-action, greedy, myopic-service, and reserve-aware policies.

## Phase 9 — EBU controller

Implement only the local authorised EBU policy.

Ensure it cannot read global/future variables.

## Phase 10 — metrics and classification

Implement:

- service;
- viability;
- conservation;
- settlement closure;
- run status.

## Phase 11 — long-duration fixture

Add live-epoch/overlap tests independently of the main long-run campaign.

## Phase 12 — preregistration lock

Freeze scientific parameters and hashes.

Only after this point perform official long-run evidence runs.

---

# 50. Required implementation report before official runs

Before launching the official campaign, report:

1. exact repository authority used;
2. exact mathematical identities implemented;
3. all assumptions;
4. all remaining open issues;
5. foundation-fixture results;
6. negative-control results;
7. conservation tolerances;
8. settlement tolerances;
9. controller information boundaries;
10. reproducibility evidence;
11. preregistration hash.

Return one of:

\[
\boxed{\text{READY FOR PREREGISTERED RUN}}
\]

\[
\boxed{\text{FOUNDATION INCOMPLETE}}
\]

or

\[
\boxed{\text{IMPLEMENTATION INVALID}}
\]

Do not launch the official scientific campaign when foundation identities are failing.

---

# 51. Central principles that must survive implementation

Do not lose these while coding.

### Principle A

\[
\boxed{
\text{Physical actions move resources.
The field evaluates those actions.}
}
\]

### Principle B

\[
\boxed{
\text{Local runtime information;
global theorem/evaluation only outside the decision path.}
}
\]

### Principle C

\[
\boxed{
\text{Sequential causal chains remain chains of atomic receipts,
not one recursively expanded mega-action.}
}
\]

### Principle D

\[
\boxed{
\text{Simultaneous actions share one actual/common physical path.}
}
\]

### Principle E

\[
\boxed{
\text{Interaction modifies the realised field/path result;
it is not extra issuance afterward.}
}
\]

### Principle F

\[
\boxed{
\text{Möbius reveals interaction structure;
it does not decide who gets what.}
}
\]

### Principle G

\[
\boxed{
\text{Conservation and homeostatic burden are different layers.}
}
\]

### Principle H

\[
\boxed{
\text{The environment must not secretly implement homeostatic control for EBU.}
}
\]

### Principle I

\[
\boxed{
\text{Useful service and system viability must both be measured.}
}
\]

### Principle J

\[
\boxed{
\text{The experiment is allowed to falsify EBU.}
}
\]
