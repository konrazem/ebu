# EBU Stage D Dynamic-Growth Campaign Authority Amendment

**Status:** prospective additive Stage D authority candidate; authority records
only; no harness implementation, model execution, transform, benchmark,
trajectory, runner, Gate, simulation, outcome inspection, result, figure, book,
release, or publication

**Authority version:** 1.0.0-candidate

**Exact accepted base:** `5a66c674a3a9a23861ac11b986754b2022e277dc`

**Exact accepted base tree:** `ee38ece14a945ddc8d4108f54ff2b813360c8c58`

## 1. Purpose and precedence

The accepted Stage D matrix registers fixed-topology long-run viability in
`SD-01` and finite canonical-motif/cache studies in `SD-07`. It does not
register a campaign in which population, resource state, demand, and the
dependency hypergraph grow together. This amendment closes that gap before
Stage E may be treated as complete.

The six accepted Stage D authority files, five accepted completion-oriented
continuation files, six accepted Stage E authority files, accepted workflow,
and accepted reachability durability file remain byte-for-byte unchanged.
This amendment is additive. It creates the nested campaign
`SD-01-GROWTH-v1`; it does not create a fifteenth study or reorder `SD-01`
through `SD-14`.

`SD-01-GROWTH-v1` executes prospectively as the second subcampaign of `SD-01`,
after the accepted fixed-topology `SD-01` cells and after all applicable Stage
E direct-oracle, Möbius, DAG, cache, continuation, schema, and isolation checks
have independently passed. It uses the accepted SD-06/SD-07 authorities and
future outcome-blind Stage E conformance, but it does not depend on an SD-07
scientific outcome. It completes before `SD-02` begins.

This candidate grants no Stage E implementation and no Stage F execution. A
later Stage E authority reconciliation must explicitly bind this amendment
and its permitted harness paths before the held Stage E candidate can be
accepted or integrated.

## 2. Exact candidate scope

The authority candidate adds exactly five regular mode-`100644` files:

1. `STAGE_D_DYNAMIC_GROWTH_CAMPAIGN_AUTHORITY_AMENDMENT.md`;
2. `stage_d_dynamic_growth_campaign_contract.json`;
3. `stage_d_dynamic_growth_campaign_evidence_schema.json`;
4. `stage_d_dynamic_growth_campaign_predecessor_manifest.json`;
5. `stage_d_dynamic_growth_campaign_validation_contract.json`.

Every predecessor file and every unrelated path must remain byte-identical.
Unknown, sixth, modified, renamed, deleted, mode-changed, implementation,
workflow, result, figure, manuscript, or release paths refuse this authority
phase.

## 3. Frozen scientific question and claim boundary

The registered question is:

> For the exact finite growing-system domain, do incremental structural
> expansion and certified canonical-motif reuse reproduce the complete
> accepted scientific output of full reconstruction while reducing
> recomputation under declared locality, canonical-equivalence, and boundary-
> invariance conditions, and how do viability, service, reserves, recovery,
> collapse, conservation, and correction accounting behave while population,
> resource capacity, demand, and structure expand? Under separately declared
> capacity-conversion and demographic-response semantics, can fully receipted
> net topology-generated usable capacity permit, rather than guarantee, a
> demographic response, and how do the three registered causal arms differ?

The strongest permitted positive statement is limited to the exact registered
model, topology family, demand process, policy, seed, horizon, numerical
policy, equivalence certificates, controls, and environment. It is level-5
registered scientific-simulation evidence only after Stage F. Static Stage E
oracle/cache equivalence is level-3/4 implementation evidence and is not a
scientific outcome.

No constant-time, constant-memory, universal scalability, universal topology,
empirical population, empirical ecology, optimality, or institutional claim is
permitted. Logistic demand is one scenario and not an assumed population law.
Fibonacci-like growth is one conditional worked benchmark and negative-control
family. A phyllotaxis analogy may motivate that benchmark; it is not evidence
that human systems should use Fibonacci topology.

The registered expansion is an exact logical dependency-topology activation
at each frozen expansion tick. It does not model or claim physical construction
or activation completion, cost, or delay. The accepted SD-10 and SD-14 delay
programmes remain separate and are not superseded. Any future physical-growth
claim requires a separate prospective amendment; topological compression alone
cannot stand for physical feasibility or homeostasis.

## 4. Frozen growing model

### 4.1 Time, population, resource, and expansion

Each valid scientific run has exactly 8,192 ticks numbered `0..8191`.
Expansion epochs are indexed exactly by `e=0..15`; epoch `e` activates at
tick `256*(e+1)`, before that tick's model transition. Thus the exact ticks
are `256,512,...,4096`. Define
`e(t)=min(16,floor(t/256))`, population `P_t=16+3*e(t)`, resource carrying
capacity `K_t=4*P_t`, protected reserve `R_t=P_t`, and initial resource stock
`x_0=48` resource-units. Population growth is therefore the exact registered
stepwise-linear trajectory; it is not inferred from any demand family.

Structural expansion begins from the exact path
`v_0->v_1->...->v_15`, with `v_15` the initial anchor, and adds three vertices
per epoch, ending at 64 vertices. All dependency edges and hyperedges point
from lower canonical vertex IDs to a higher canonical target. Hyperedge order
is at most four. The feasible poset is the exact reachability order of the
sealed acyclic dependency declaration; no framework-inferred scientific
topology is permitted.

Resource regeneration is
`g_t=(1/8)*x_t*(1-x_t/K_t)` under accepted `NUMERICAL-POLICY-01`. Expansion of
population, carrying capacity, or topology does not add physical stock.
External stock changes require one boundary receipt. Before service,
`x_pre=x_t+g_t-boundary_shock_t`; after served demand `u_t`,
`x_(t+1)=x_pre-u_t`. The dynamic-growth campaign freezes
`boundary_shock_t=0` at every tick; its shock demand process changes requested
service, not physical stock. Any later physical shock requires separate
prospective authority.

### 4.2 Demand processes

Requested demand is `D_t=P_t*q_t`. The six demand processes in the original
growth request are joined by a fixed baseline and a declining/migration-like
demand control from the approved conceptual bridge, for eight identities:

- `FIXED-v1`: `q_t=1/64`;
- `LINEAR-v1`: `q_t=1/64+t/(64*8192)`;
- `EXPONENTIAL-v1`: `q_0=1/64` and
  `q_(t+1)=q_t*(1+1/8192)`;
- `LOGISTIC-K1_16-v1`: `q_0=1/64`, declared carrying capacity
  `K_q=1/16`, rate `r_q=1/1024`, and
  `q_(t+1)=q_t+r_q*q_t*(1-q_t/K_q)`;
- `PULSED-SEASONAL-v1`: `q_t=1/32` when `t mod 512` is in `0..63`,
  otherwise `q_t=1/64`;
- `SHOCKS-v1`: `q_t=3/64` on inclusive intervals `2048..2175`,
  `4096..4351`, and `6144..6271`, otherwise `q_t=1/64`;
- `ADVERSARIAL-PHASE-v1`: `q_t=1/16` when `t mod 256` is in
  `192..255`, `q_t=5/64` on `2560..2623` and `5120..5183`, and
  `q_t=1/32` otherwise. Overlap uses the greatest declared value.
- `DECLINING-MIGRATION-v1`:
  `q_t=max(1/128,1/32-t/(32*8192))`. This is a declining-demand control;
  it does not rewrite the registered population trajectory or infer migration
  from observations.

All arithmetic follows `NUMERICAL-POLICY-01`; no later interpolation, fitted
growth law, adaptive adversary, resampling, or empirical interpretation is
permitted.

### 4.3 Sparse interaction and delivery capacity

The topology owns a sparse exact coefficient table, not a universal Boolean
table. Each active vertex contributes reduced-rational delivery-capacity
coefficient `1/16`; each order-2 dependency contributes `1/1024`; each order-3
hyperedge contributes `1/2048`; each order-4 hyperedge contributes `1/4096`.
The exact delivery capacity `C_t` is the reduced-rational sum of the active
coefficients after every scheduled correction. A coefficient constrains
delivery capacity; it never creates resource stock.

The unprotected policy serves
`u_t=min(D_t,C_t,max(0,x_pre))`. The reserve-robust policy uses the exact
five-action menu `M_t={0,D_t/4,D_t/2,3*D_t/4,D_t}`, restricted by `C_t`, and
selects the greatest action that leaves `x_(t+1)` in `[R_t,K_t]` and has a
nonempty next-tick reserve-feasible menu under both the declared next demand
and the registered stress branch `max(5/64,q_(t+1))`.
The canonical greatest-action tie break is mandatory. An empty current or
next-branch menu is a visible recursive-feasibility failure. At tick 8191,
the deterministic population/capacity/demand/topology drivers are evaluated
once at tick 8192 solely to construct the two next-branch feasibility menus;
no tick-8192 state transition, service, or scientific observation is created.

## 5. Frozen topology families

Every expansion attaches one sealed three-vertex motif. Motif `A` is the
ordered path from the prior canonical anchor through the three new vertices.
Motif `B` has two order-2 edges from the anchor to the first two new vertices
and one order-3 hyperedge from those vertices to the third. Vertex, edge,
hyperedge, label, boundary, and ordering identities are part of canonical
equivalence.

Exactly seven topology instances are registered:

1. `FIBONACCI-CONDITIONAL-v1`, one instance: motif symbols are the first 16
   symbols of the infinite fixed point of `A->AB, B->A`, beginning with `A`;
2. `THUE-MORSE-NONFIB-v1`, one instance: motif symbols are the first 16
   symbols of the fixed point of `A->AB, B->BA`, beginning with `A`;
3. `HASHED-NONRECURSIVE-v1`, four instances with seeds `0..3`: at epoch `e`,
   select `A` iff the first byte of SHA-256 over UTF-8
   `EBU-SD01-GROWTH-TOPOLOGY-v1|seed|e` is even, otherwise `B`; the declaration
   is nonrecursive and no motif reuse is presumed;
4. `BROAD-RECONFIGURATION-v1`, one instance: it follows the Fibonacci
   attachment schedule, but at epoch 8 uses the third new vertex as the
   canonical aggregation vertex and adds exact order-2 edges from the initial
   terminal plus every earlier motif terminal (eight prior terminals) to that
   vertex, changes the query boundary identity of every existing occurrence,
   and therefore requires complete affected-closure recomputation before any
   later recertification.

At tick 2560, which is epoch `e=9` and the tenth expansion, all families apply
the registered local correction to the second
occurrence of motif `B`: its order-3 coefficient changes from `1/2048` to
`3/4096`, with an exact correction receipt. At tick 5120, the newest occurrence
receives a label-version correction without a coefficient change. Both events
must invalidate the complete upward dependency and alias closure. The broad
family’s epoch-8 boundary change is intentionally nonlocal and must record a
broad invalidation. A local label or coefficient change that crosses a
certified boundary or changes external interactions is also nonlocal for that
query and must propagate upward; stale reuse is always forbidden.

The seed/tick witness is frozen rather than inferred: hashed seed 1 has the
16-symbol schedule `BAAAABAAAAABBAAA`, with its first two `B` occurrences at
epochs 0 and 5, both active before tick 2560. Every other registered topology
also has at least two `B` occurrences by epoch 9. A missing second occurrence,
a different epoch numbering, or a different hash preimage refuses before any
state transition.

At every tick, and identically for all three reconstruction strategies, the
same-tick order is exact: (1) load the prior committed state/checkpoint;
(2) activate the scheduled epoch topology and emit its topology receipt;
(3) apply every scheduled coefficient, label, or boundary correction in the
declared event-ID order; (4) traverse and invalidate the complete dependency
and alias closure, then reconstruct and recertify all affected coefficients,
boundaries, cache entries, and delivery capacity; (5) evaluate population,
resource-capacity, reserve, and demand drivers; (6) evaluate regeneration and
the external boundary exchange and form `x_pre`; (7) select service/action and
advance the resource state; (8) reconcile conservation, correction, service,
viability, recovery, and collapse receipts; (9) serialize the trace and output
prefixes; and (10) if this is a checkpoint tick, seal the checkpoint only after
all preceding receipts are durable. Reordering, strategy-dependent ordering,
or checkpointing an intermediate same-tick state refuses.

## 6. Reconstruction strategies and controls

Each valid scientific configuration is executed with three algorithms:

- `FULL-REBUILD-v1` reconstructs every active vertex/hyperedge coefficient,
  canonical occurrence, query-boundary certificate, and delivery capacity at
  tick 0 and every expansion/correction event;
- `INCREMENTAL-NO-REUSE-v1` updates the sealed topology incrementally and
  recomputes the complete directly affected closure, but it never reuses a
  result merely because another occurrence is canonically equivalent;
- `CERTIFIED-MOTIF-REUSE-v1` may reuse a lower-order result only after all
  accepted A1-A8, complete-key, canonical-equivalence, boundary-invariance,
  dependency, alias, epoch, stochastic, numerical-policy, authority, code,
  artifact, and environment conditions pass.

The scientific-output projection contains every population, resource,
demand, topology-version, capacity, action, service, reserve, recovery,
collapse, conservation, correction, and disposition field. It excludes only
algorithm identity, wall time, memory, operation counts, cache events, and
provenance fields that are expected to differ. All three valid strategies must
produce byte-identical canonical scientific-output projections in every
matched cell. A mismatch is a falsifier, not a tolerance case.

The deliberately wrong equivalence control assigns motif `A` and motif `B`
the same canonical identity while retaining their different ordered
dependency/boundary declarations. It must refuse before a trajectory starts.
It is not an approximate run and cannot produce scientific evidence.

The six required controls are therefore closed:

1. full rebuild;
2. incremental expansion without motif reuse;
3. certified canonical-motif reuse;
4. deliberately wrong motif/equivalence assignment, which must refuse;
5. hashed random/nonrecursive topology;
6. broad reconfiguration with complete affected-closure invalidation.

For each eligible Fibonacci and Thue-Morse cell, incremental and certified
strategies must preserve the full-rebuild scientific output. A positive reuse-
efficiency disposition additionally requires
`recomputed_coefficients(CERTIFIED) < recomputed_coefficients(INCREMENTAL) <
recomputed_coefficients(FULL)` over the complete run, at least one certified
hit, zero stale hits, and exact invalidation receipts. Random topology carries
no reuse-efficiency presumption. At the broad event, all affected entries must
be recomputed; a local-reuse claim for that event refuses.

The testable claim is reduced recomputation, not constant computation. Wall
time or memory may fail to improve even when coefficient recomputation falls;
such evidence must be reported honestly. No `O(1)` or universal scalable-
growth claim is permitted.

## 7. Registered cells, seeds, and dependency order

The seven topology instances, eight demand processes, two policies, and three
valid reconstruction strategies create exactly `7*8*2*3=336` registered
scientific runs, grouped into 112 matched strategy triplets. The wrong-
equivalence preflight is applied to the seven topology instances under each of
the eight demand declarations with the reserve-robust policy, creating exactly
56 non-evidence refusal fixtures and zero trajectories.

Only hashed nonrecursive topologies use topology seeds, exactly integers
`0..3`. All demand and model evolution is deterministic. The accepted
stochastic-rule identity is `FORBIDDEN`, run seed is `0`, permitted stream list
is empty, and checkpoint counter tuple set is the accepted canonical empty
state. Unknown draws or streams refuse.

## 8. Viability, homeostasis, recovery, and collapse

The following predicates are fixed before implementation:

- viability: unprotected cells require `0<=x_t<=K_t`; reserve-robust cells
  require `R_t<=x_t<=K_t` at every pre/post state;
- service fraction: `1` when `D_t=0`, otherwise `u_t/D_t`;
- growth homeostasis: for every rolling 256-tick window ending after tick 1024,
  at least 240 ticks must be viable, reserve margin must never be negative for
  a reserve-robust claim, and service fraction must be at least `19/20` on at
  least 240 ticks; after the final expansion, all of the final 1000 ticks must
  be viable and have service fraction at least `19/20`;
- recovery: after each expansion, shock-window start, or correction, recovery
  is the least tick within 512 ticks followed by 64 consecutive ticks with
  viability, nonnegative protected reserve margin where claimed, and service
  fraction at least `19/20`; absence is `NOT_RECOVERED_ON_HORIZON`;
- collapse: the first tick outside the applicable viability set, or the first
  start of 128 consecutive ticks with service fraction below `1/2`; modeled
  collapse is a scientific outcome, not a computational failure;
- regeneration: every `g_t` and boundary exchange is separately recorded;
  increasing `K_t`, population, topology capacity, or reused computation never
  counts as resource inflow;
- recursive feasibility: every robust action and both registered next-demand
  branch menus are recorded, including the frozen terminal lookahead; an empty
  set fails that cell.

Claims remain cell-specific. Failure of a viability or recovery predicate is
visible negative scientific evidence after Stage F; timeout, identity failure,
checkpoint failure, or resource exhaustion is instead
`COMPUTATIONALLY_INCONCLUSIVE` or refusal and has no scientific sign.

## 9. Conservation and no-magical-gain accounting

The open control volume keeps separate ledgers for population boundary change,
resource stock, regeneration, external resource exchange, demand, served and
unmet demand, delivery capacity, reserve margin, topology additions/removals,
sparse interaction coefficients, correction deltas, cache reuse, computation,
and provenance. Population and carrying-capacity increases do not create
resource. Delivery capacity is not resource stock. Reserve margin is derived
and never added to stock. An internal transfer cancels once. A reused
coefficient retains its original calculation receipt plus one reuse receipt;
it does not create another interaction benefit or service unit.

Every expansion and correction emits a topology receipt, coefficient receipt,
dependency/alias invalidation receipt, and conservation receipt. Any missing,
duplicated, stale, or unreconciled receipt is a falsifier or refusal according
to its class.

## 10. Computational feasibility and hard limits

This is a finite sparse/low-order study. It is not an arbitrary Boolean
Möbius problem. If an exact Boolean subproblem is introduced, accepted
`MOBIUS-EXACT-01` still requires direct-oracle agreement, declares
`O(n*2^n)` transform arithmetic plus subset-evaluation cost and `O(2^n)`
storage, and keeps `n<=18`, subset count `<=262144`, and hyperedge order `<=4`.
No approximation may replace the exact registered study.

The dynamic-growth domain is capped at 64 vertices, 1,024 edges/hyperedges,
hyperedge order four, dependency/propagation depth 64, horizon 8,192, 396 valid
runs, 76 wrong-equivalence plus 150 misscaling refusal fixtures (226 total),
132 strategy triplets, 720 coefficient-transport oracle arithmetic/preflight
operations, 20 GiB total logical output, 5 GiB trace per run, 4 GiB
process-tree peak memory per attempt, 14,400 active seconds per attempt, and
1,200,000 primary evaluations per attempt/run. Transport-oracle and misscaling
records are outcome-blind theorem/numerical conformance with no model state
advance and create no additional scientific-run attempt.

The worst registered full-rebuild topology performs at most 1,550 coefficient
evaluations: 1,415 across tick 0 and the 16 expansion boundaries, including
the broad epoch, plus 135 at the separate tick-5120 correction. An unprotected
run has at most `8192+1550=9742` primary evaluations. A robust run has at most
`56*8192+1550=460302`. Across the 168 unprotected and 168 robust demand-driven
runs, the declared upper estimate is `168*(9742+460302)=78967392` primary
evaluations. The 60 capacity-population runs are capped at 10,000 each, adding
600,000; the complete estimate is 79,567,392. These are not prose-only
subcaps: every capacity-population configuration, local computation record,
local limit decision, and campaign summary must carry the exact closed
`CAPACITY-POPULATION-v1` profile with per-run primary evaluations `10000`,
study cumulative primary evaluations `600000`, per-attempt wall seconds
`14400`, process-tree peak RSS `4294967296`, trace bytes per run `5368709120`,
and logical study output `21474836480`. The local computation and decision
records bind the corresponding inherited Stage D/continuation computation and
limit-decision identities. A missing, substituted, reset, or larger profile,
or a cumulative count above 600,000, refuses or is computationally
inconclusive and is never a scientific result.
Operation classes remain
separate: transition/menu checks, coefficient evaluations, canonicalization,
DAG traversal, cache lookup, invalidation, receipt serialization, and output
bytes.

Before Stage F, outcome-blind Stage E measurements must record wall time,
process-tree peak RSS, coefficient/subset/hyperedge evaluations, canonical
candidates, vertices/edges inspected, recomputed/reused coefficients, hits,
misses, invalidation radius, propagation depth, storage, trace/output bytes,
and checkpoint/restart costs on the frozen environment. They are feasibility
evidence, not scientific outcomes.

The completion-oriented continuation authority applies. Checkpoint cadence is
every 256 ticks after a complete model/topology/cache/receipt boundary. One
scientific identity spans ordered attempt slices. Attempt counters and campaign
counters never reset. No slice may change input, algorithm, authority,
environment, numerical policy, topology, approximation status, cache key, or
scientific meaning. The prospective campaign envelope is capped at 3,168
attempts, 2,592,000 cumulative active seconds, 475,200,000 cumulative primary
evaluations, 80 GiB cumulative physical writes, 20 GiB logical output, 180
calendar days, and 4 GiB maximum process-tree peak memory. These are terminal
integrity budgets, not scientific answers.

If a cap or feasibility boundary is exceeded, the exact study refuses before
execution or becomes `COMPUTATIONALLY_INCONCLUSIVE` with immutable partial
evidence. It is never silently approximated, sampled, truncated, topology-
reduced, or interpreted positively or negatively. Any approximation programme
requires separate prospective authority, error bounds, controls, evidence
class, and interpretation rules.

## 11. Recursive Möbius surplus theorem and growth corollaries

This amendment freezes a composition-layer identity. It does not modify the
local/main EBU equation.

For each declared recursive composition
`M_(n+1)=M_n composed-with M_(n-1)`, define the two-child macro set function
`e_n` on `{x,y}` under one frozen protocol, boundary, units, history,
feasibility, removal, preservation, loss, process-account, commitment, and
settlement semantics:

- `e_n(empty)=E(empty)`;
- `e_n({x})=E(M_n)`;
- `e_n({y})=E(M_(n-1))`;
- `e_n({x,y})=E(M_(n+1))`.

The raw Boolean two-child coefficient is exactly

`I_n({x,y})=e_n({x,y})-e_n({x})-e_n({y})+e_n(empty)=J_n`.

With `R_n=E(M_n)-E(empty)`, inverse/zeta reconstruction is

`R_(n+1)=R_n+R_(n-1)+J_n`.

Let `F_0=0,F_1=1`. For every `n>=1`, induction then gives the forced
recurrence projection

`R_n=F_n*R_1+F_(n-1)*R_0+sum_(k=1)^(n-1) F_(n-k)*J_k`.

If every `J_k=0`, the declared surplus sequence obeys the homogeneous
Fibonacci recurrence. Lucas scaling occurs only for Lucas-compatible initial
conditions; for example `R_0=2c,R_1=c` gives `R_n=c*L_n`. An incompatible
base must not be relabeled Lucas. Neither recurrence is inferred from
population data or assumed universal.

If a model omits registered interactions, its exact reconstruction error is

`error_n=sum_(k=1)^(n-1) F_(n-k)*J_k`.

A correction `delta` to `J_q` changes each later `R_n` by
`F_(n-q)*delta` for `n>q`. This is algebraic dependency propagation. It is not
a physical wave, physical superposition, or causal-propagation claim.

For a declared finite feasible poset `P`, the controlling incidence-algebra
relations are

`I(x)=sum_(y<=x) mu_P(y,x)E(y)`,
`E(x)=sum_(y<=x) I(y)`, and
`delta I(x)=sum_(q<=x) mu_P(q,x)delta E(q)`.

Only elements of the declared feasible poset exist. A Boolean value for an
infeasible subset must never be invented.

For an exact domain extension `A_(t+1)=A_t union B_t`, every old coefficient
has an exact preservation theorem: if `E_(t+1)(T)=E_t(T)` for every
`T subseteq S` and `S subseteq A_t`, then
`I_(t+1)(S)=I_t(S)` because the defining Möbius sums are term-for-term equal.
New elements alone do not require old coefficients to be recomputed. Any old
subset-value, boundary, history, feasibility, removal, settlement, authority,
or result-affecting change reopens the exact declared upward cone and any
dependent/alias summaries. This theorem is the authority for incremental
extension; cache reuse still requires the complete A1-A8 and key obligations.

Future Stage E must verify the theorem with direct two-child subset tables and
inverse reconstruction across 18 exact sequence/baseline fixtures and levels
`1..15`, exactly 270 macro tables. The sequence fixtures are: homogeneous
Fibonacci `R_0=0,R_1=1,J=0`; Lucas-compatible `R_0=6,R_1=3,J=0`;
Lucas-incompatible `R_0=1,R_1=1,J=0`; positive impulse `J_4=2`;
negative impulse `J_4=-2`; and alternating `J_k=(-1)^k`, each under baselines
`E(empty)` in `{0,5,-3}`. It must cover nonzero positive and negative `J_n`,
nonzero `E(empty)`, the forced projection, missing-interaction error, and
correction propagation. A perturbed recursion at level 8, a broken A1-A8
certificate, and a stale cache must refuse the Fibonacci-kernel/reuse claim.
Full expanded calculation through level 16 and the registered nonrecursive
hashed topology family are mandatory comparators.

The feasible-poset oracle domain is the exact chain-3, antichain-4, V-3, and
diamond-4 declarations. For seeds `0..7`, values are deterministic signed
integers derived from the first SHA-256 byte of UTF-8
`EBU-SD01-GROWTH-POSET-v1|poset_id|seed|element_id` by
`5+(byte mod 17)-8`. The 32 base transforms and all 224 one-element correction
cases with deltas `+2` and `-3` must match direct incidence-algebra evaluation,
zeta reconstruction, and the correction formula. Infeasible Boolean-extension
fixtures must refuse.

A separate conditional capacity benchmark may set `c=1/16`,
`C_n=c*F_(n+1)`, reserve margin target `P_t/64`, and
`n_t=min{n in 0..32:C_n>=D_t+P_t/64}`. If no such level exists, it records
`CAPACITY_LEVEL_NOT_REACHED`. Under the proved per-occurrence/additivity
assumptions and an unbounded growing demand, `n_t=Theta(log D_t)`; for the
bounded logistic-demand scenario after population saturates, the selected
level eventually saturates. This benchmark is not a population law,
homeostasis proof, or capacity prescription.

Under accepted A1-A8 with uniformly bounded-size summaries and bounded
composition cost, summaries through recursive level `n` cost `O(n)` while
expanded occurrences are `F_(n+1)=Theta(phi^n)`. Therefore summary computation
is `O(log N)` in expanded occurrence count `N` under those conditions.
Physical construction, physical storage, data collection, coefficient
acquisition, boundary certification, and arbitrary primitive all-subset
Möbius reconstruction do not become `O(log N)`; the last remains exponential.

### 11.1 Recursive coefficient transport, scaling, and residuals

Canonical equivalence does not by itself say that an exposed coefficient is
numerically unchanged at a larger recursive level. For each coefficient that
may be transported from `M_n` into `M_(n+1)`, the controlling provider,
domain, or model authority, or an accepted mathematical derivation, must first
freeze a role-preserving coordinate map

`iota_n: exposed_coordinates(M_n) -> exposed_coordinates(M_(n+1))`

and a typed scaling operator. The operator binds the source and target roles,
units, query, boundary, state, history, protocol, numerical policy, authority,
and derivation identities. In the scalar case the prediction is

`Ihat_(n+1)(iota_n S)=lambda_(n,S)*I_n(S)`

and the exact residual is

`K_(n+1)(iota_n S)=I_(n+1)(iota_n S)-lambda_(n,S)*I_n(S)`.

`K=0` establishes only the declared scaling relation for that exact
coordinate and frozen context. `K!=0` is new scale-dependent interaction,
boundary, state, congestion, delay, or other declared content; it remains
visible in evidence and may not be silently absorbed into the factor. Missing
mapping, factor, units equivalence, query equivalence, provider/derivation
authority, or residual refuses scaled reuse.

The scaling classes are disjoint:

1. invariant/intensive uses `lambda=1` only for an unchanged intensive query;
2. occurrence-extensive uses `lambda=N_(n+1)/N_n` only under proved identical
   per-occurrence contribution and complete additivity;
3. boundary-extensive uses the declared exposed-boundary ratio, not total
   occurrence count;
4. degree-homogeneous uses `lambda=s_n^alpha_S` only with a separately
   justified scale variable and degree;
5. scale-dependent transport records the declared factor and explicit
   nonzero or zero residual; and
6. non-scalable coordinates are recomputed directly and never scaled.

For `N(M_n)=F_(n+1)`, an occurrence-extensive coefficient has the conditional
factor `F_(n+2)/F_(n+1)`, which approaches `phi`. A declared Lucas-compatible
occurrence family has the analogous `L_(n+2)/L_(n+1)` ratio with different
finite-level bases. Neither limit applies to every EBU or Möbius coefficient.
EBU does not infer an institutionally, socially, or physically correct factor.

A correction obeys the exact relation

`delta I_(n+1)(iota_n S)=lambda_(n,S)*delta I_n(S)+delta K_(n+1)(iota_n S)`.

The scaling-operator identity and class enter `composition_version`; the
transport map, roles, and query equivalence enter `query_identity`; source and
target units enter `units_semantics`; boundary equivalence enters
`boundary_semantics`; the rule, factor, residual, and transport closure enter
`dependency_identity`; aliases enter `alias_closure_digest`; and any change to
the map, rule, factor, degree, units, query, boundary, residual, provider, or
derivation increments `correction_invalidation_epoch` and invalidates every
dependent larger-level result before reuse. The accepted 29-field cache-key
shape is preserved; these are closed preimages of its existing fields.

Every new identity uses SHA-256 over UTF-8 canonical JSON with sorted object
keys, compact separators, and exact array order; duplicate keys, floating
numbers, and non-finite values refuse. The transport-map preimage is exactly
`mapping_version,level_n,source_coordinate_identity,target_coordinate_identity,
coordinate_role`. The factor preimage is exactly
`scaling_rule_identity,scaling_class,level_n,coordinate_role,scaling_factor,
source_units_identity,target_units_identity,provider_or_derivation_identity`.
The operator preimage is exactly
`scaling_rule_identity,scaling_class,source_coordinate_identity,
target_coordinate_identity,coordinate_role,source_units_identity,
target_units_identity,query_equivalence_identity,boundary_equivalence_identity,
provider_or_derivation_identity`.
The residual preimage is exactly
`level_n,direct_target_coefficient,scaled_prediction,scaling_residual`.
Composition, query, units, boundary, dependency, and alias projection
identities use the exact field lists frozen in the mechanical contract. The
same transport, authority, equivalence, factor, and residual identities must
appear in the parent oracle record and nested cache binding; a mismatch
refuses before reuse.

Future Stage E must implement direct-versus-scaled reduced-rational oracles for
levels `1..15`. The registered valid scalar families are: invariant
`I_n=3/8,lambda=1,K=0`; Fibonacci occurrence-extensive
`I_n=F_(n+1)/16,lambda=F_(n+2)/F_(n+1),K=0`; Lucas
occurrence-extensive `I_n=L_(n+1)/16,lambda=L_(n+2)/L_(n+1),K=0`;
boundary-extensive with `B_n=2(n+1)`, `I_n=B_n/32`, and
`lambda=B_(n+1)/B_n`; degree-homogeneous with
`I_n=(n+1)^2/256`, `s_n=(n+2)/(n+1)`, `alpha=2`; and a
nonzero-residual control `I_n=n/64,lambda=1,K=1/64`. These are 90
valid scalar transport rows. Fifteen non-scalable hashed-boundary rows require
direct recomputation. Each scalar row has the two correction cases
`(delta I_n,delta K)=(2/64,0)` and `(-3/64,1/128)`, exactly 180
correction reconstructions.

Ten misscaling mutations at every level create exactly 150 preflight refusal
fixtures and zero misscaled reuse trajectories: missing map, missing factor,
missing units equivalence, missing query equivalence, invariant mislabeled
occurrence-extensive, occurrence-extensive mislabeled invariant, boundary
mislabeled occurrence-extensive, wrong homogeneous degree, hidden nonzero
residual, and a factor assigned to a non-scalable coordinate. Stage F retains
the invariant, Fibonacci- and Lucas-occurrence-extensive, boundary-scaled,
degree-homogeneous, nonzero-residual, deliberately misscaled, and non-scalable
controls. Direct coefficients and scaled predictions must agree exactly where
`K=0`; where `K!=0`, direct target value must equal scaled prediction plus the
visible residual. Any other relation refuses evidence promotion.

### 11.2 Three causal arms and the conditional capacity-population bridge

The central conditional synthesis is:

> Recursive topology may generate net interaction benefits that expand usable
> carrying capacity. Where demographic behaviour responds positively to that
> capacity, the benefit can enable population growth. EBU tests this connection
> rather than presuming it universally.

Stage F must keep three causal arms separate and execute them in this order:

1. `ARM-1-DEMAND-DRIVES-TOPOLOGY` is the existing 336-run matrix: registered
   population and demand drive the 16 logical expansion events, and capacity
   never feeds back into population;
2. `ARM-2-TOPOLOGY-CAPACITY-PERMITS-DEMOGRAPHY` has ten registered capacity-
   population scenarios under all three reconstruction strategies, exactly 30
   runs: topology levels are exogenous, capacity may enter the declared
   demographic response, and population may not change expansion; and
3. `ARM-3-BIDIRECTIONAL-FEEDBACK` repeats the same ten scenarios and three
   strategies, exactly 30 runs: capacity may enter the demographic response,
   and the receipted population-derived required-capacity projection may request
   the next declared topology level.

Together the programme contains 396 scientific runs and 132 matched strategy
triplets. The three arms are interventions in registered models, not evidence
that any direction is universal in real populations.

For Arms 2 and 3, use levels `0..16`, base capacities `C_0=2,C_1=3`, and the
exact capacity-compatible recurrence

`C_(n+1)=C_n+C_(n-1)+J^C_n-X_(n+1)`.

`J^C_n` is the residual that the declared capacity model and typed conversion
receipt permit to enter usable capacity. An arbitrary positive EBU or Möbius
coefficient is not carrying capacity. The complete expansion burden is

`X_m=construction+maintenance+resource+correction+delay+loss`, where every
transition row has source `n in 1..15` and target `m=n+1 in 2..16`.
All burden predicates use the target index `m`, never the source index: the
exact components are construction `1/16`, maintenance `m/256`, resource
`1/32`, correction `1/64` iff `m in {10,16}` and zero otherwise, delay
`1/64` plus `1/16` only in the response-delay control, and loss `1/64` plus
`2` only when `m=8` in the capacity-shock control. Every component has
one typed owner receipt; `X` is their exact reduced-rational sum. These are
synthetic registered capacity-account units, not empirical physical costs or
evidence that construction completed.

The exact population bookkeeping is separately receipted as
`P_m=P_(m-1)+B_m-D^death_m+M_m`. Once the scenario equation has produced its
exact target `P_m`, the unique canonical ledger is
`Delta_m=P_m-P_(m-1)`, `B_m=max(Delta_m,0)`,
`D^death_m=max(-Delta_m,0)`, and `M_m=0`. Births, deaths, and migration are
therefore nonnegative reduced rationals and cannot be chosen as an arbitrary
signed decomposition. The positive-compatible, zero, negative,
positive-nonconvertible-after-conversion, and capacity-shock controls freeze
`P_n=rho*C_n` with constant `rho=4` over the compared levels. Under those
premises,

`P_(n+1)=P_n+P_(n-1)+rho*(J^C_n-X_(n+1))`.

This is a testable conditional projection, never a universal demographic law.
It does not guarantee growth, authorize demographic control, or infer births,
deaths, migration, behaviour, health, institutions, or causality from a
coefficient.

Each of Arms 2 and 3 freezes ten exact scenarios: positive capacity-compatible
residual; zero residual; negative residual; positive but non-capacity-
convertible residual; capacity allocated to reserve; capacity allocated to
quality; demographic transition with `rho=4` through level 8 and `rho=2`
afterward; one-level demographic-response delay; an exact level-8 capacity
shock; and a direct hashed nonrecursive topology. Reserve and quality allocations
are excluded from demographic-response capacity. The nonrecursive case has no
recursive projection. Arm 3 records
`expansion_rho_effective_n=P_n/C_n`, which is a required positive reduced
rational and is distinct from any scenario's demographic-response factor.
Thus `required_capacity_n=P_n/expansion_rho_effective_n+1/16=C_n+1/16`.
For every source level `n=1..15`, only that exact strict inequality plus one
typed request receipt authorizes target level `n+1`; all 15 requests must be
present. At level 16 the exact terminal disposition is
`COMPLETED_LEVEL_16_NO_FURTHER_REQUEST`. A null, zero, negative, arbitrary, or
scenario-response-substituted expansion ratio refuses; a missing request
stalls visibly and forbids fabrication of later level rows.

The capacity-population scenarios use one exact registered service-demand
process, `CP-FIXED-SERVICE-v1`, at every level: `D_n=P_n/64`. Initial
population is `P_0=8`; `P_1=12` except the response-delay scenario, where
`P_1=8`. Reserve and quality accumulators are exact: `Q^R_0=Q^R_1=0` and
`Q^Q_0=Q^Q_1=0`; at every target `m=2..16`, the reserve scenario adds `3/8`
only to `Q^R_m`, the quality scenario adds `3/8` only to `Q^Q_m`, and every
other increment is zero. The demographic-response capacity is
`A_m=C_m-Q^R_m-Q^Q_m`, must be nonnegative, and is the only capacity allowed
to serve demand or enter the reserve/quality demographic equations.

Resource/service state is separate from carrying capacity. Freeze
`S_0=2,S_1=3`. For target `m=n+1`, regeneration is
`G_m=max(0,(A_m-S_n)/4)`, boundary exchange is exactly zero,
`S^pre_m=min(A_m,S_n+G_m)`, served demand is
`U_m=min(D_m,A_m,max(0,S^pre_m))`, unmet demand is `D_m-U_m`, and
`S_m=S^pre_m-U_m`. Increasing `C`, `A`, topology, population, or a reused
coefficient never adds resource stock; only the separately receipted `G_m`
does so. The service fraction is `1` when `D_m=0`, otherwise `U_m/D_m`, and
the service-reserve margin is `A_m-D_m`.

For these 15 target-level rows, resource viability is
`0<=S^pre_m<=A_m` and `0<=S_m<=A_m`. A four-level homeostasis window ending
at `m=5..16` passes iff at least three of its four target levels are viable,
at least three have service fraction at least `19/20`, and every one has
nonnegative service-reserve margin; the terminal homeostasis predicate also
requires levels `13..16` all viable with service fraction at least `19/20`.
Recovery events are the level-8 shock burden, the level-10 correction burden,
the level-16 correction burden, and each response-delay activation. Recovery
is the first target within the next three levels followed by two consecutive
viable levels with service fraction at least `19/20` and nonnegative reserve
margin; insufficient remaining horizon is exactly `NOT_RECOVERED_ON_HORIZON`.
Collapse is the first target-level viability exit or the first of two
consecutive target levels with service fraction below `1/2`. These predicates,
event identities, first-event levels, and receipts are recorded per run and
reconciled in the capacity-population campaign summary.

Every scenario runs full rebuild, incremental without reuse, and certified
motif reuse; their scientific projections must match exactly. Capacity,
residual conversion, every burden component, population, births, deaths,
migration, demand, reserve/quality allocation, service, viability,
homeostasis, recovery/collapse, corrections, limits, and conservation are all
trace- and receipt-bound. Zero/negative results and benefits allocated away
from demographic response remain visible rather than being reclassified.

Stage F must compare certified incremental reconstruction with full expanded/
full-rebuild calculation for exact scientific-output equality and measured
work, while measuring viability and homeostasis separately. Structural or
topological compression alone is never sufficient evidence of homeostasis.

Every one of the 20 capacity-population strategy triplets emits one closed
comparison record binding the causal arm, scenario, three run identities,
three projection identities, three operation/output records, every relevant
invalidation receipt, exact projection equality, and the preregistered
recomputation-efficiency disposition. The 20 additional wrong-equivalence
preflights are keyed by the two causal arms and ten scenarios, use the
certified-reuse strategy, and refuse before a level transition. Together with
the 56 demand-driven fixtures this preserves exactly 76 representable refusal
fixtures.

## 11.3 External conceptual input and future-book-only nature reference

The user-approved external conceptual bridge
`EBU_RECURSIVE_MOBIUS_GROWTH_THEOREM_AND_STUDY_BRIDGE.md` is recorded as
25,305 bytes with SHA-256
`7f2a236a6ab2be50d5841bc309b38eedf558911d876c46624b14798cd73eb668`.
It is conceptual input, not accepted repository authority, a predecessor lock,
or scientific evidence.

Swinton et al., “Novel Fibonacci and non-Fibonacci structure in the
sunflower” (*Royal Society Open Science*, 2016) is recorded only as a useful
supporting reference for a future audited book. Its Fibonacci and non-Fibonacci
observations may be used briefly to discourage universal-law overclaiming. It
is not a programme source, authority input, empirical basis for the EBU
theorem, or reason to select or alter any registered model, topology, control,
falsifier, or interpretation. The EBU mathematics and registered-model design
stand independently. No manuscript is changed here.

## 12. Required evidence and traceability

The amendment defines closed prospective records:

- `dynamic_growth_configuration/v1`;
- `growth_epoch_manifest/v1`;
- `growth_trace_row/v1`;
- `growth_reconstruction_comparison/v1`;
- `growth_invalidation_receipt/v1`;
- `recursive_mobius_surplus_oracle/v1`;
- `recursive_coefficient_transport_oracle/v1`;
- `coefficient_scaling_refusal_fixture/v1`;
- `feasible_poset_mobius_oracle/v1`;
- `growth_capacity_benchmark/v1`;
- `capacity_population_configuration/v1`;
- `capacity_population_level_record/v1`;
- `capacity_population_reconstruction_comparison/v1`;
- `capacity_population_computation_record/v1`;
- `capacity_population_limit_decision/v1`;
- `capacity_population_campaign_summary/v1`;
- `growth_campaign_summary/v1`; and
- `wrong_equivalence_fixture/v1`.

They bind the accepted authority and artifact identities, campaign/run/
attempt/checkpoint identities, exact demand/topology/policy/algorithm cell,
scientific-output projection, population/resource/demand/topology state,
coefficients, service/reserve/recovery/collapse predicates, operation counters,
cache events, certificates, corrections, invalidations, conservation receipts,
limits, environment, and output digests.

Prospective schema validation must first validate all 29 complete fixtures,
covering every one of the 25 closed schema definitions and both valid branches
where a definition has materially distinct scalable/non-scalable,
Arm-2/Arm-3, or Arm-1/capacity-population forms. This includes dynamic and
capacity-population configurations, rows, comparisons, computations, limit
decisions, summaries, scalar and non-scalable transport/cache records, and
both wrong-equivalence domains. The immutable fixture objects
and exact RFC-6902-style single patch operation for every negative live inside
the repository validation contract; a checker must reconstruct the target
fixture, apply only that patch, and require refusal. Each frozen
schema-negative case then applies only its named mutation to a complete valid
instance of its named target and must refuse. Validating `{}` or any generic,
unrelated malformed instance does not establish the frozen negative case.

Every reduced rational is canonical: denominator is strictly positive; the
numerator and denominator are in lowest terms; zero is exactly `0/1`; and a
negative-zero spelling is forbidden. Values such as `2/2`, `-0/1`, `0/2`, or
a negative denominator refuse before identity construction.

The chain is:

`equation -> configuration -> code/artifact -> Stage E oracle and harness test
-> immutable Stage F campaign/run/attempt/checkpoint/trace/receipt -> output
-> independent reconstruction -> table/figure -> bounded claim disposition`.

An independent result audit must reconstruct every scientific output from raw
traces without cached summaries; compare all 132 strategy triplets; verify all
76 wrong-equivalence refusals, 105 direct coefficient-transport rows, 180
transport-correction cases, and 150 misscaling refusals; replay topology construction, canonical
certificates, invalidation closures, corrections, ledgers, checkpoints, and
resource counts; and separate computational performance from scientific
viability before any interpretation.

The future book must not add a disconnected or repetitive chapter. Part V owns
the growing-population/capacity causal arms, viability, and homeostasis bridge;
Part VI and the mathematical appendix own recursive Möbius surplus,
Fibonacci/Lucas projections, coefficient scaling, residuals, and proofs. The
relevant chapter culmination may use one light synthesis: a successful system
could help create conditions in which future generations have meaningful
resources available. It may not promise resources, control demography, or
claim universal causation. Results and diagrams remain forbidden until Stage F
execution and Stage G independent audit. Part VII may cross-reference expansion
and reconfiguration, and Part IX may contain only a short later cross-reference.
No book work is authorized here.

## 13. Falsifiers and stop conditions

The campaign refuses or falsifies, as applicable, on any of the following:

- scientific-output projection mismatch between valid strategies;
- a certified stale hit, incomplete key, failed A1-A8 condition, missing
  boundary certificate, or wrong-equivalence acceptance;
- local invalidation that omits an affected ancestor/alias, or broad change
  treated as local;
- coefficient, service, stock, reserve, correction, boundary, or receipt
  double count;
- hidden stock creation from population, capacity, topology, or reuse;
- positive reuse-efficiency claim without strict eligible-cell recomputation
  reduction and zero stale hits;
- constant-computation, universal-Fibonacci, phyllotaxis-as-evidence,
  logistic-population-law, universal-scalability, empirical, or optimality
  language;
- a raw macro coefficient different from `J_n`, failed inverse reconstruction,
  forced-projection mismatch, Lucas label on incompatible bases, wrong
  missing-interaction error, or wrong correction multiplier;
- a feasible-poset transform that invents an infeasible Boolean value;
- a missing or role-changing transport map, undeclared scaling factor, missing
  units/query equivalence, wrong scaling class or degree, hidden residual,
  scaled non-scalable coordinate, wrong correction reconstruction, or scaling
  input omitted from the cache dependency/invalidation projection;
- an arbitrary positive EBU or Möbius coefficient relabeled carrying capacity,
  any omitted construction/maintenance/resource/correction/delay/loss burden
  or receipt, or a mismatched capacity-conversion identity;
- the conditional population recurrence used without the exact capacity law,
  constant `rho`, `P_n=rho*C_n`, common units, boundary, protocol, and receipt
  premises;
- a capacity benefit presented as guaranteed population growth, demographic
  control, universal causation, or evidence that future resources are assured;
- one causal arm substituted for another, or zero/negative/nonconvertible,
  reserve/quality, demographic-transition, delay, shock, or nonrecursive
  controls hidden or reclassified;
- an `O(log N)` claim for physical construction, storage, data collection,
  coefficient acquisition, boundary certification, or arbitrary all-subset
  reconstruction;
- topological compression treated as sufficient evidence of homeostasis;
- silent approximation, sampling, truncation, topology alteration, changed
  seed/input/algorithm/environment, counter reset, or post-outcome protocol
  change;
- missing raw output, checkpoint, trace, receipt, provenance, or limit record.

Authority integration requires an independent PASS. A later reachability
durability change requires a separately audited one-path authority and normal
integration. Stage E reconciliation and implementation remain frozen until
both are closed. No scientific execution or outcome inspection is authorized.

## STAGE_D_DYNAMIC_GROWTH_CAMPAIGN_AUTHORITY_COMPLETE
