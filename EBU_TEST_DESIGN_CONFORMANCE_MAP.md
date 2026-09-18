> **Current-scope notice — 18 September 2026.** Historical conformance map for the preserved prospective harness, not evidence or a Gaussian conformance map. Reported counts were not rerun in this reconciliation.
>
> Current navigation: [CURRENT_SCIENTIFIC_AUTHORITY.md](CURRENT_SCIENTIFIC_AUTHORITY.md).
> The pre-existing body below is preserved unchanged from checkpoint `924a4d9`.

# EBU Scientific Test Design — Section-by-Section Conformance Map

**Status: DERIVED CONFORMANCE ANALYSIS. Not an authority; adopts nothing;
preregisters nothing; authorizes no execution.**

**No scientific execution occurred.** No world, tick loop, trajectory,
simulation, parameter search, AWS, Docker or network call. Every check cited
below is a pure-function evaluation on a frozen or synthetic individual state,
a static/AST inspection, or a read-only Git query.

Design source: `test_design.md` (51 sections). Programme coordinate: **W-2**
(`V3.0_PROGRAMME_AUTHORITY_COORDINATE.md`).

---

## 0. Evidence classes, kept separate (design §43)

Every row below is tagged with one of these, and they are never merged.

| Tag | Meaning |
|---|---|
| **THEOREM** | Proved mathematics, under stated assumptions |
| **IMPL** | Committed or newly written implementation |
| **CAND** | Candidate scientific choice awaiting preregistration |
| **BLOCKED** | Blocked by missing mathematical or programme authority |
| **EVIDENCE** | An executed, recorded scientific result — **none exists here** |

**There is no EVIDENCE anywhere in this work.** Mathematical identities passing
is not scientific success (§43).

---

## 1. Conflicts found against committed authority

§0 of the design requires conflicts to be reported, not silently resolved.
Four conflicts and one correspondence are recorded, plus **three analytical
findings** (FINDING-1 and FINDING-2 blocking; FINDING-3 informative) from the
design-readiness review.
CONFLICT-4 is **reclassified as CORRESPONDENCE-4**: the candidate C3 fits §27
as a refinement and the design text is preserved unchanged. CONFLICT-1, 2, 3
and 5 remain open; 3 and 5 require author decisions. **Neither finding is
resolved here** — both require author decisions before the study can run.

### CONFLICT-1 — §13's per-action receipt vs. committed scheme 4/5

**Design §13** requires the simultaneous common-path settlement as a mandatory
gate, and says the per-action receipt must **not** be read as "a Shapley split".

**Committed authority** (`V3.0_LOCAL_EBU_FOUNDATION_DRAFT.md` §10.3, row 4)
names the identical formula
`∫₀¹ Δt q_e f_e(z + t·ΔtΣS q) dt − C_e` the **"Aumann–Shapley path
allocation"**, and marks it **"registered refinement, not required"**. Row 5,
"one action per source per micro-step", is **"adopted for the first formal
model"**. Theorem 8.2 assumes **(T3) one accepted action per micro-step**.

**Reconciliation, and what was implemented.** The *formula* and the *identity*
are not in conflict — only the interpretive label is. The closure identity

```
Σ_a R_a^V  =  V(z) − V(z + Δx_G)                                   [THEOREM]
```

follows from linearity of the integral plus the fundamental theorem of
calculus, for any C¹ `V` and any straight common path. It is implemented and
verified exactly (residual `0.0`, not merely within tolerance).

What remains open is the **split's meaning**, not the total. Escalation **E2**
(open problem O3 / 16.O3) records that no registered per-action decomposition
exists at `m ≥ 2`. `PerActionReceipt` therefore carries a licensed role and
refuses `settlement`, `wallet`, `causal_entitlement`, `shapley_allocation`,
`aumann_shapley_allocation`, `mobius_allocation`, `physical_path_claim`,
`responsibility_share` and `common_physical_path_claim`. **Status: total =
THEOREM; split = BLOCKED (E2).**

### CONFLICT-2 — §18 fixture F4 is unconstructible under the committed potential

**Design §18 F4** requires a legitimate fixture with `F(AB) > F(A) + F(B)`.

**Committed Definition 6.1** makes `V` separable with **convex** `v_i`. For two
actions pushing the **same direction** through a shared node `i`, the
interaction is exactly

```
I(AB) = −[ v_i(z) − 2v_i(z−q) + v_i(z−2q) ]  =  −(second difference of v_i) ≤ 0
```

by convexity — so positive interaction is **impossible** that way, and actions
on disjoint coordinates interact exactly zero by separability.

**Resolution used.** F4 is satisfied legitimately with **opposing flows**
through the shared node, where the two actions partly cancel: the interaction
becomes `+`(second difference)` ≥ 0`. The committed fixture realises
`I(AB) = +8` exactly. No potential was altered. The structural fact is itself
asserted as a check, so the workaround cannot be mistaken for a general claim.
**Status: IMPL.** Positive interaction from *same-direction* flows would need a
non-separable factor potential (`V(x) = Σ_α φ_α(x_{S_α})`, design §6), which is
**CAND** and not adopted.

### CONFLICT-3 — §35's four run statuses are not exhaustive

**Design §35** requires every official trajectory to receive exactly one of
`SUCCESS`, `EBU-FAIL`, `PHYSICALLY-IMPOSSIBLE`, `INVALID`.

Two reachable cases fit none of them:

1. the **EBU arm** misses the target but **no oracle verdict exists** — §35
   requires EBU-FAIL to rest on a challenge "independently shown to be
   physically controllable", so the label is unavailable;
2. a **comparison arm** misses the target — a legitimate, expected outcome for
   a control, yet EBU-FAIL is EBU-specific, SUCCESS is false, INVALID is untrue
   and PHYSICALLY-IMPOSSIBLE is unproven.

`classify_run` **refuses** in both cases rather than guessing a label.
**Status: BLOCKED — author decision required** (register a fifth status such as
`TARGET-MISSED`, or require an oracle verdict for every official run).

### CORRESPONDENCE-4 (formerly CONFLICT-4) — §27's C3 and the candidate refinement

**Reclassified.** This was recorded as a conflict. On review it is **not** one:
the candidate draft *fits* §27's description, and **the original design text is
preserved unchanged**. What follows documents the correspondence.

**Design §27 C3** requires: *"Use explicitly declared local reserve/safety
constraints but not the EBU potential gradient/force. Purpose: separate the
value of basic reserve protection from the richer EBU field."*

**The candidate `C3-reserve-and-band-aware`** uses exactly that and nothing
more: declared local reserve and safety constraints (`R_j`, `L_i`, `L_j`,
`U_j`), and **no** `μ`, `f_e`, `α`, `β` or `χ` — none of which its typed view
even carries. It is a **candidate refinement** of §27's C3, not a replacement
for it: it adds *structure* (three lexicographic stages over one band-safe
budget, with an explicit share rule) while using the *same class of declared
constraints* §27 names.

| §27 requirement | Candidate draft |
|---|---|
| explicitly declared local **reserve** constraints | stage 1: `[R_j − x_j]₊ / η_e`, from `NodeSpec.reserve` |
| explicitly declared local **safety** constraints | stage 2 `L_j`, stage 3 `U_j`, source floor `L_i` |
| **not** the EBU potential gradient/force | `C3View` carries no `μ`, `f_e`, `α`, `β`, `χ` — structurally absent |
| separate basic protection from the richer field | it is the non-field arm the field is measured against |

**No design amendment is required and none is proposed.** §27 stands as
written.

**History preserved.** Two drafting errors were corrected on the way here and
are recorded rather than erased: (1) an early draft bounded export by the
reserve coordinate `[x_i − R_i]₊`, which left the source below its own lower
band on fixture A and produced two false claims, both withdrawn; (2) the
correction to (1) removed reserve awareness entirely on the false premise that
`R_eff` already supplied it. See packet Part 0.

**Status: IMPL (candidate draft).** `C3-reserve-and-band-aware` remains
`CANDIDATE_UNAPPROVED`; `build()` refuses. Its stage ordering is
**proposal-level only** — the stage-blind resolver can leave a Stage-1 reserve
deficit unserved while Stage-3 service executes. And see **FINDING-2** below:
whether *any* positive budget is authorized for this world is now itself an
open question.

### CONFLICT-5 — §27's common resolver has no destination-side rule

**Design §27** requires that *"all controllers must use the same physical
resolver after producing their proposals."* The committed resolver
(`p1c_v29` Amendment 4, reproduced in `W.resolve_shared_source`) resolves
contention **at the source**. Its incoming quantity is carried as
`incoming_usable` and marked *"DIAGNOSTIC ONLY; not budgeted"*.

So when several independently controlled sources feed **one** destination and
their individually valid proposals jointly exceed `K_j`, **no committed
authority says how to allocate the shortfall**. First-come, edge-order,
proportional, max-min and field-priority allocations would each be an
unreviewed scientific rule.

**Conservative resolution for the FIRST study, at configuration time.** No
destination-contention allocation rule is invented. Instead the candidate world
configuration is restricted to `deg⁻(j) ≤ 1` for every node eligible to
receive, validated by `W.require_single_source_destinations` when the
configuration is constructed — **before** demand, controller construction or
any tick. A violating topology **fails during configuration validation**; it
does not survive to `apply_joint` and become an `INVALID` run, which would
mis-attribute a configuration error to a controller's outcome. This is
expressed on the **configured topology**, not per-tick on whichever edges
happen to be active.

The restriction is **a prospective first-study domain restriction: not a
general EBU theorem, not a property of all future worlds, and not yet a frozen
preregistration parameter.**

Individual hard destination headroom remains **common physical feasibility**
and is still clamped for every arm:  `q_e ≤ [K_j − x_j]_+ / η_e`.
`W.require_resolved_destination_contention` is retained as defence in depth and
still fails closed if contention ever reaches it.

A related but distinct problem is **G-4**: `U_j` is a *homeostatic band*, not
hard capacity, so it must **not** be moved into the common resolver — doing so
would give C1, C2 and C4 a protection they did not choose — and C3's upper-band
claim is consequently established **only** under the single-source restriction.

**Status: CONTAINED for the first study by a declared domain restriction;
the general resolver remains BLOCKED.** Recorded as a future open problem: a
**policy-neutral multi-source destination resolver** (Q-5).

### FINDING-1 — C4 is behaviourally identical to C0 under the stated initial condition

**BLOCKING.** With `L_i ≤ x_i(0) ≤ U_i` (design requirement), `R_i ≤ L_i`
(candidate domain restriction) and the separable band/reserve potential
(Definition 6.1), every branch guard in `d0_v29.marginal` is false, so
`μ_i = 0` **exactly** at every node. Then `f_e = 0`, and since `θ_e ≥ 0` is
enforced by `d0_v29.Edge`, `excess = −θ_e ≤ 0` and `J_e = 0`. C4's sizing is
`min(Δt·J_e, c_e)`, and demand enters **only** as the cap `c_e`, so no demand
history can lift it. The accepted vector is zero, the state is unchanged, and
the argument reapplies by induction at every tick.

Verified as absent rather than assumed: no drive/regeneration/source term exists
in `ebu_test_world` (`WorldState.successor` is reached only from `apply_joint`,
whose totals come solely from `Action.increment`); `d0_v29.natural_drive` is
never referenced by the study world.

Consequence: C4 delivers **zero service in perpetuity** and shows *perfect
viability with zero service* — the exact C0 signature §36 exists to refuse. The
existing fixtures **do not settle this**: both start outside the band
(`j1 = 3 < L = 4` in A; all three below in B), which is the only reason C4 acts
in them. They are preserved, with the limitation stated.

**Status: BLOCKED — author decision required.** Recorded as an analytical
limitation of **this** controller/world/initial-condition combination, **not**
generalised to EBU mechanisms. See
`V3.0_DESIGN_READINESS_NOTE_C4_DEGENERACY_AND_P1C_APPLICABILITY.md` finding 1
and alternatives A0–A4.

### FINDING-2 — no permission policy adopted for this world (corrected)

**BLOCKING.** Reading `p1c_v29._source_budget` — the **complete** budget
dispatch, not `robust_budget`'s arithmetic alone — the committed permission
policy is:

| state | type | budget rate |
|---|---|---|
| P | **regenerative** | `robust_budget` (A4.5) |
| P | **finite** | **0** — "positive extraction is depletion, not preservation" |
| P | **irreversible** | **0** — "safe extraction rate is zero" |
| R / I | any stock | **0** |
| F | **flow** | `min(flow_cap, [x+Δt·u]₊/Δt)` |

`robust_budget`'s own docstring states it "assumes the caller has already
classified the source as State P and **typed it regenerative**".

This world declares **no regeneration in its plant** (identity clause 3), `u = 0`,
and interior stocks holding a conserved scalar. Every honest typing —
`finite` or `irreversible` — yields **budget 0**; `regenerative` is factually
false and `flow` requires an external flow with no stock reserve. With budget 0,
`σ = 0` and **every arm becomes behaviourally identical to C0**.

**Two corrections to this row's earlier text.**

1. **Gate-2.1B Theorem 4.1 is PROVED** — review §4.1 is titled "proved",
   carries a full algebraic proof, and §13.1 lists it as "full proof". The
   phrase "validated numerically — NOT proved" in `p1c_v29.py` refers to that
   module's **implementation conformance**, not the theorem.
2. **Withdrawn: that P1C presupposes resource leaving the accounted system.**
   A4.1 and Theorem 4.1's assumption (A6) already carry incoming transfers
   `Σ_in η_e q_e^acc`; the proof merely *drops* `I_i ≥ 0` as one-sided slack,
   which is conservatism, not an assumption about where resource goes.

The actual distinction: **global conservation and local source preservation are
different properties.** A transfer can preserve the system total while drawing
down its source — which is exactly what the reserve bound constrains. Theorem
4.1 is therefore **mathematically applicable to internal transfers** under
(A1)–(A9) with no reinterpretation. Mathematical applicability is **not**
adoption: it does not override the dispatch, does not supply a policy for this
study, and does not make proportional scaling the adopted allocator.

**Where the obstacle actually lies.** For a `finite` source with `x > R_eff`
and (A8) holding, Theorem 4.1 would permit a positive one-step-safe export, and
review §6.4 says the reserve is preserved "for a finite number of ticks". The
dispatch instead elects the **long-run** reading (`q^long = 0`, Definition 6.3,
Impossibility 6.4). So this is a **policy choice in force**, not a proof that
one-tick positive export is unsafe. `o14_v30.screen_budget` is the committed
precedent: *"O14 registers regenerative sources only"* — when positive export
was needed, the **source type** was changed up front, not the budget
transplanted.

Proportional scaling: **Observation 7.1** classifies frozen-state proportional
source scaling as the minimal allocator preserving aggregate bound,
simultaneity, order-invariance and locality — but records it is **outside the
V2.8 D0 theorem** and that **"its guarantees need separate proof"**; Thm 4.1
covers only the aggregate `Q_i`. Open problem (iv) is joint multi-source/
multi-edge invariance under proportional allocation.

`cc.p1c_tick_budget_quantity` reproduces the arithmetic **without** the
classification and type dispatch its source says the caller must perform, and so
silently applied the regenerative branch to a non-regenerative world. The
distinction now recorded: **reuse of proportional scaling** `σ = min(1, B/Q_req)`
is legitimate and faithful; **adoption of the complete P1C permission policy**
has *not* occurred and would yield zero here.

Accordingly the C3 `σ < 1` demonstration is **qualified**: it shows what
proportional scaling does to a *supplied* budget, and does **not** establish that
any positive budget is authorized for this world.

**Status: BLOCKED — a prospective permission decision is required.** No source
was relabelled regenerative and no alternative budget law was introduced. See
the design-readiness note finding 2 and alternatives B0–B3.

### FINDING-3 — "EBU controller" is not one thing; a finite-action selection rule already exists

Committed sources separate **seven** notions: field force (`d0_v29.edge_flux`,
committed); automatic flux `J_e` (committed, V2.8 scope only); **externally
motivated finite requests** (foundation draft §5 **event 3** — a protocol slot
whose rule is **unspecified**, filled with the flux in every implementation);
physical permission (`p1c_v29`, Thm 4.1 **proved**, dispatch **adopted**); the
**exact finite EBU quote** (Candidate design **6.5**, `ebu_quote_v30` —
**CANDIDATE**, computed *after* allocation on `[0, q_acc]`, and "can never be an
authorisation"); **action selection and sizing** (`o14_v30.select_arm_D/_B/_S`
over one shared `candidate_menu` — **registered at O14 scope**); and
post-resolution attribution (group total **THEOREM**, per-action split
**BLOCKED, E2/O3**). The six-layer table (§4.1) and nine-event ordering (§5)
contain **no selection layer** — selection appears only as event 6, "the actor
accepts, rejects, or redesigns", a slot rather than a policy.

`select_arm_D` is a genuine finite-action EBU rule: largest **strictly
positive** exact total quote, explicit **rest** branch, ties by lower edge index
then lower quantity-menu index, and it "never ranks per unit". But **it
degenerates here for two independent reasons**: (a) `candidate_menu` enumerates
*fractions of the mobility-scaled flux*, so when `μ ≡ 0` the menu is empty and
every arm rests — including the service arm S; and (b) from a fully in-band
state with `C_a = 0` (design §11 prefers `C_a = 0`),
`Δe_quote(q) = −[v_i(after) + v_j(after)] − C_a(q) ≤ 0`, with equality iff the
transfer keeps both endpoints in band — so the best attainable quote is
**neutral (0)**, never positive, and a strictly-positive threshold rests.

Simultaneous overlapping actions: **additivity is not assumed and is not
established** — E2/O3, and O14's own table marks proportional-`q_acc` sharing a
"candidate default" with unproven split-invariance.

**Status: informative, and it changes the remedy.** A demand-driven
finite-action EBU arm needs exactly two declared policy choices — a
request-generation rule at event 3, and an acceptance threshold admitting
neutral quotes — neither of which is invented here. See the readiness note
Finding 3 and Part 4.

---

## 2. Section-by-section map

`ebu_test_world` = W, `ebu_test_settlement` = S, `ebu_test_protocol` = P,
`study_harness` = H, `study_protocol_schema` = SP.

| § | Requirement | Status | Where / why |
|---|---|---|---|
| 0 | Five-layer separation (physical / field / receipt / interaction / evaluation) | **IMPL** | W, S, P are separate modules; the field never moves resource |
| 1 | Atomic action, no recursive mega-action | **IMPL** | `W.Action` has no `parent`, `children` or `expand()` — Principle C is structural |
| 2 | One conserved scalar on a finite network | **IMPL** (architecture) / **CAND** (the instance) | `W.Topology`, `W.WorldSpec`; the world itself is slot S-W |
| 3 | Closed conservative world, `η=1`, explicit residual + tolerance | **IMPL** | `W.conservation_residual`, `W.apply_joint`; `η<1` without a declared `loss_sink` **refuses**. Tolerance is a required argument (**CAND** value). **`r_cons` alone is insufficient and is no longer relied on alone**: a zero residual is also produced by an *undeclared* sink change masking an active-stock discrepancy, by a *decrease* of the irreversible loss account, and by a sink used as a **plug** while both per-node increments are wrong — all three demonstrated, none caught by the residual. `W.conservation_profile` checks the source, destination and sink increments **separately**, taking the expected sink from the **action law** (`Action.loss`), and `W.sink_increment` refuses an undeclared or decreasing sink. Both are **additive**: `conservation_residual` and `apply_joint` are unchanged, and at `η = 1` the guards are inert. Committed basis: `CONSERVATION_AND_BOUNDARY_ACCOUNTING_FOUNDATION.md` §4.1 (a zero residual “does not prove that every exchange was observed”) and §4.3 (no universal zero-residual rule, no hidden global tolerance). See `V3.0_FIRST_STUDY_RESOURCE_MODEL_AND_LOSS_ACCOUNTING.md` |
| 4 | No self-healing world; demand independent of `V`, `∇V`, reserve, controller | **IMPL** (structural) | `W.generate_demand_schedule`'s `draw(unit, tick, edge)` signature cannot receive state — the forbidden logic is unwritable. `u(x)=0` is **CAND** |
| 5 | Hard physical domain vs homeostatic band vs reserve | **IMPL** | Three separate predicates, never collapsed. **Four** distinct layers are now kept apart: (1) hard capacity `K_j` — common physical feasibility, clamped in `common_opportunities` and re-checked on the joint successor; (2) the **provider/export floor `R_eff`** — common, at the resolver, bounding what a source may *send*; (3) the **homeostatic reserve coordinate `R`** (`NodeSpec.reserve`) — supplied by **no** common layer, so a controller wanting it must carry it, which C3 does in stage 1; (4) the homeostatic band `L, U` — voluntarily managed by C3. **`R_eff` ≠ `R`**: `W.RESERVE_CONCEPTS` declares both and their absence of relationship, and `W.require_reserve_concepts_distinct` refuses the conflation. Candidate domain restriction `0 ≤ R ≤ L ≤ U ≤ K` is validated at configuration time — committed `NodeSpec` does **not** guarantee it |
| 6 | Committed homeostatic potential | **IMPL** (reused, not forked) | `S.potential` calls `d0_v29.penalty`; `S.marginal_at` calls `d0_v29.marginal`. Parameters **CAND**. Factor potentials `Σ_α φ_α` **SAFE-TODO** |
| 7 | Frozen synchronous tick, 12 steps, no round-robin | **IMPL** | `P.plan_tick` (steps 1–7, advances nothing) + `P.execute_tick` (8–12); all controllers see the same frozen state. Hard feasibility is decided on the **joint successor** `W.joint_successor` — `0 ≤ x_j + Σ_{e→j} η q^acc − Σ_{j→k} q^acc ≤ K_j` — so a node that simultaneously receives and sends is evaluated once, on its net increment; per-edge headroom is used only as an opportunity cap where its isolated-transfer assumption holds |
| 8 | requested / permitted / accepted / measured / delivered | **IMPL** | `W.QuantityLadder`, with monotonicity enforced and `audit_clean()` for Thm 8.2 (T4) |
| 9 | Provider permission, shared-source proportional resolver | **IMPL** (source side) / **BLOCKED** (destination side, G-3) | `W.resolve_shared_source` reproduces `p1c_v29` A4: `σ = min(1, Q_max/Q_req)`, and is applied identically to every arm with the budget invisible to all of them. **Units:** its `budget` is a tick **quantity**; `p1c_v29.robust_budget` returns a **rate**, so a caller must convert via `W.tick_quantity_from_rate` (`q = Δt·J`) — invisible at `Δt = 1`, hence the named function. Contested **destinations** have no committed rule: contained for the first study by the configuration-time restriction `deg⁻(j) ≤ 1`, with `W.require_resolved_destination_contention` retained as defence in depth; see CONFLICT-5. **The resolver can still bind after a controller proposes**: `σ = 1` would require `L_i ≥ R_eff + ε_x + Δt·ε_u`, which no declared ordering provides, so `q^accepted = σ·q^proposed` and no lexicographic saturation is claimed (`cc.P1C_BINDING_ANALYSIS`, `cc.p1c_binding_demonstration`). **Wiring `p1c_v29.robust_budget` is NOT the outstanding item — applicability is (FINDING-2).** The complete policy is `_source_budget`, which returns 0 for `finite`/`irreversible` stock sources and States R/I; the robust budget is the **regenerative** State-P branch alone. This world declares no regeneration, so committed P1C permits **zero** export and no arm can deliver service. A prospective permission decision is required. `R_eff` is a **stock quantity**; the budget is a rate |
| 10 | Action object fields | **IMPL** | `W.Action`; carries no global world state, per §10 |
| 11 | `C_a = 0` in the first world | **IMPL** (by omission) | No `C` term exists in `S`; receipts are pure field differences. Non-zero `C` is **CAND** |
| 12 | Exact finite EBU for one action | **IMPL** / **THEOREM** | `S.path_integral` vs `S.endpoint_difference`; fixture F1 residual `0.0` |
| 13 | Simultaneous common-path settlement | **THEOREM** (total) / **BLOCKED** (split, E2) | `S.settle_group`; see CONFLICT-1 |
| 14 | No interaction bank | **IMPL** | `S.require_no_double_issuance`; **no function anywhere adds coefficients to a settled total** |
| 15 | Möbius role = audit, subsets may re-resolve | **IMPL** | `S.subset_field_value` re-resolves every subset from the same frozen baseline; fixture F7 |
| 16 | Möbius and path receipts are different decompositions | **IMPL** | Only the group total is required to agree; no per-action/subset equality is imposed |
| 17 | Boolean **and** feasible-poset Möbius | **IMPL** | `S.boolean_mobius`, `S.poset_mobius`. A structurally impossible configuration is **absent, never fabricated as zero** |
| 18 | Fixtures F1–F10 | **IMPL** (all ten) | `test_ebu_foundation.py` groups 1–10; F4 see CONFLICT-2 |
| 19 | Eleven deliberately broken negative controls | **IMPL** (all eleven) | `test_ebu_foundation.py` group 11 |
| 20 | Long-duration actions, live epochs, telescoping | **IMPL** / **THEOREM** | `S.telescope_path`, `S.settle_segments`; exact for 2 and 8 segments; a later action reads the **live** state |
| 21 | Duration tested separately from the first runtime | **IMPL** | `W.Action.is_instantaneous`; F9 is independent of any campaign |
| 22 | Immutable world across arms (12 items) | **IMPL** | `W.WorldSpec.digest` covers all of them; `W.WorldState` refuses a foreign spec digest |
| 23 | Initial state `x₀ ∈ H` | **BLOCKING (FINDING-1)** / **CAND** | `P.ViabilityMetrics.evaluate` can test membership; an explicit `require_homeostatic(x₀)` gate is not yet wired. **The initial condition is no longer a detail: `x₀ ∈ H` together with `R ≤ L` makes `μ ≡ 0`, which makes the EBU arm identically inactive (FINDING-1).** Choosing `x₀` is therefore a scientific decision that determines whether the study can test anything, not just a preregistered value |
| 24 | Exogenous demand, generated once, hashed, replayed | **IMPL** | `W.generate_demand_schedule`, `W.DemandSchedule.digest`. The three candidate models are **CAND** and deliberately unselected |
| 25 | Demand must not encode homeostatic correction | **IMPL** (structural) | See §4 |
| 26 | Identical demand across arms (common random numbers) | **IMPL** | `W.DemandSchedule.verify_replay`. Opportunity semantics are **demand-triggered and demand-bounded** (Q-1): `d_e(t) = 0 ⇒ c_e(t) = 0` and `c_e ≤ d_e`, applied for every arm in `common_opportunities` before any controller logic, so C4 cannot create an autonomous zero-demand transfer. Autonomous EBU rebalancing is a **separate future study**, not mixed in here |
| 27 | Controllers C0–C4 | **CAND** (all five); CONFLICT-4 **resolved** | `ebu_candidate_controllers.DRAFTS` — five drafts, each carrying all thirteen disclosures and two `ILLUSTRATIVE_FIXTURE_ONLY` worked examples **derived by executing the declared rule** (`_example` → `CANDIDATE_RULES`), never transcribed; **all `CANDIDATE_UNAPPROVED`**, `build()` refuses for every one, C0 included, and also refuses a conformance fixture offered as a rule. **C3 is redrafted** as **three-stage reserve-and-band-aware** (`A_i = [x_i − L_i]_+`; stage 1 destination reserve deficits, stage 2 lower-band deficits, stage 3 upper-band-capped ordinary service; recursive stage budgets; exact capped max-min water-filling) and renamed `C3-reserve-and-band-aware` — see CONFLICT-4, which is **resolved without a design amendment**. Its ordering is **proposal-level only**: the stage-blind resolver can leave a Stage-1 reserve deficit unserved while Stage-3 service executes. **FINDING-1: under the stated in-band initial condition C4 is behaviourally identical to C0** (μ ≡ 0 ⇒ J ≡ 0 ⇒ zero proposals ⇒ unchanged state, by induction, for every demand history), so the arm set is degenerate as currently specified; the fixtures start outside the band and do not settle it. G-1 and G-2 are **CLOSED** (`W.EdgeSpec`; `CommonLocalContext.endpoint_specs`); new gaps **G-3**/**G-4** block multi-source cases. All controllers share one physical resolver. See `V3.0_PROSPECTIVE_STUDY_CONTROLLER_DECISION_PACKET.md` |
| 28 | Runtime locality enforced by architecture | **IMPL** | `P.LocalView.__getattr__` refuses every undeclared read; `P.build_local_view` exposes only the source's own out-edge endpoints. For the candidate study this is strengthened from *refusal* to **structural absence**: one immutable `CommonLocalContext` (built without any controller argument) is projected into typed `C0View`…`C4View`, each carrying exactly the fields its family's formula consumes — `C3View` has no `α, β, χ, μ, f_e`, no `R_eff` and no provider budget to read — but it **does** carry each destination's homeostatic `R_j`, because no common layer supplies it. `information_ledger()` records three distinct things: present in the context / exposed by the view / consumed by the formula |
| 29 | Offline feasibility oracle, never exposed | **IMPL** (isolation) / **BLOCKED** (verdict) | `P.FeasibilityOracle.verdict_for_evaluator` refuses any non-evaluator caller; `as_local_view` exists only to refuse. The `decide` function depends on the S-H target |
| 30 | Long horizon, early stop only if preregistered | **CAND** | `T = 20 000` and absorbing conditions are slots S-T / S-H |
| 31 | Service metrics, reported on their own axis | **IMPL** | `P.ServiceMetrics`; `service_ratio` returns **`None`** on zero demand rather than a misleading `1.0` |
| 32 | Viability metrics | **IMPL** (per-state) / **SAFE-TODO** (trajectory aggregates) | `P.ViabilityMetrics`. Time-outside-band, violation duration, first-failure time, terminal state and the unrecoverable flag are trajectory-level accumulators |
| 33 | Physical / accounting metrics | **IMPL** | `P.PhysicalMetrics` + `P.TickRecord` |
| 34 | Settlement closure metric, breach ⇒ INVALID | **IMPL** | `S.settle_group` raises `ClosureViolation`; `S.audit_group` gives `r_Möbius` |
| 35 | Four run classifications | **IMPL** | Raw facts (`PhysicalValidity`, `ArmResult`, `OracleResult`) kept separate from derived labels (`derive_ebu_run_label`) and from per-claim conclusions (`ClaimConclusion`); see CONFLICT-3 |
| 36 | No "reject everything" success loophole | **IMPL** | SUCCESS requires `viability_ok` **and** `service_ok`. The criterion is **uniform**: `ArmResult` carries no controller-identity branch, C0 fails it because it delivers nothing rather than because a rule names C0, and a C0-family arm meeting both axes would record `TARGET_MET`. A check asserts both. **But FINDING-1 means C4 records TARGET_MISSED at every horizon for a reason that is not a regulation failure**, and FINDING-2 means the same of every arm — the predicate is sound; the design cannot currently exercise it. Separately, the conformance fixture is no longer the study's C0: `P.FixtureRejectAllController` carries family `FIXTURE-ONLY`, is constructible only via `for_conformance_fixture()`, and `P.require_study_controller` refuses it (closes R-1) |
| 37 | Wallets | **BLOCKED / correctly absent** | No wallet semantics were invented. The atomic account package is unaccepted (**E4**) |
| 38 | Reproducibility record | **IMPL** | `P.ReproducibilityRecord`, all 12 fields required, none defaulted |
| 39 | Machine-readable per-tick event log | **IMPL** | `P.TickRecord` carries every field §39 lists; Möbius detail stays a separate record |
| 40 | 13-component architecture | **IMPL** | W (1,2,4,5,6,9) · S (3,8,10) · P (7,11,12,13) |
| 41 | Determinism, no global RNG | **IMPL** | SHA-256 counter mode throughout; a test asserts **no `random` import** in any module |
| 42 | Exact integration, not silent quadrature | **IMPL** / **THEOREM** | `S.path_breakpoints` splits at every `L`/`U`/`R` crossing, making the integrand piecewise **linear** — trapezoid is then exact. Endpoint difference remains an independent check |
| 43 | Three evidence classes kept distinct | **IMPL** (reporting discipline) | This document; every row is tagged |
| 44 | Preregistration, 20 fields, frozen | **IMPL** (mechanism) / **CAND** (content) | `P.Preregistration` requires all 20 and hash-freezes; `SP` enforces the 13 slots |
| 45 | SD programme protection — do not rename as SD-01 | **IMPL** (naming) / **BLOCKED** (registration) | Named **`prospective stochastic sustained-demand conservative-world study`**, **no SD number**, explicitly not SD-01, and **not** called regenerative — no regeneration exists in the plant. Registration remains an author decision |
| 46 | First campaign small enough to audit | **CAND** | World size is preregistered; the fixtures use 3–4 nodes |
| 47 | Forbidden first-world features | **IMPL** | None of money, prices, markets, RL, fairness weights, wallets or endogenous corrective demand exists; a test asserts it |
| 48 | Main scientific comparison | **BLOCKED** | Requires official runs; none is authorized |
| 49 | Phases 1–12 | **IMPL** Phases 1–11 (fixture level) / **BLOCKED** Phase 12 | Phase 12 is the preregistration lock |
| 50 | Pre-run implementation report | **IMPL** | `P.readiness_report`; today's verdict is **FOUNDATION INCOMPLETE** |
| 51 | Principles A–J | **IMPL** (enforced, not documented) | A: field never acts · B: `LocalView` refusal · C: no action expansion · D: common path · E: no double issuance · F: Möbius is audit-only · G: conservation ≠ burden · H: demand signature · I: both axes reported · J: EBU-FAIL is reachable |

---

## 3. Verdict (design §50)

```
FOUNDATION INCOMPLETE  —  and the STUDY DESIGN is additionally BLOCKED
                          by FINDING-1 and FINDING-2
                          (FINDING-3 changes the remedy, not the verdict)
```

**The foundation and the study design are separate verdicts.** The foundation
mechanism checks pass. The *study design* does not currently support the
comparison it was built for: FINDING-1 makes the EBU arm identically inactive
under the stated initial condition, and FINDING-2 leaves no adopted permission
policy, which would make every arm inactive. FINDING-3 shows the intended
question has more committed machinery available than assumed — a registered
finite-action EBU selection rule, an exact finite quote, and a committed event
ordering with proposal and decision slots — so the remaining gaps are two named
policy choices rather than new theory. All require author decisions; none is
resolved here.

**Recommended direction (not adopted):** demand-driven finite-action selection
using the exact finite EBU quote, paired with a permission decision. It is the
only direction whose subject matter is *"can EBU guide responses to external
service requests while preserving homeostasis?"*. A perturbed-start recovery
study is a separate, narrower option and is **not** recommended as a first
move.

Foundation fixtures: **F1–F10 pass**. Negative controls: **all eleven fail
correctly**. Closure residuals are **exactly 0.0**, not merely within
tolerance. The default gate now runs **19 groups, 631 checks** and is
**STATIC/PURE ONLY, machine-enforced**: it calls no `apply_joint`, `plan_tick`
or `execute_tick`, and parses its own source to assert that. The two checks
that do perform a model transition moved to
`test_ebu_foundation_transitions.py`, a separate execution class gated behind
`EBU_ALLOW_MODEL_TRANSITIONS=1` and deliberately **not** on the default CI
path; CI asserts it refuses. A previous footer claiming
`Model-state advancement: NONE` was **false** and is withdrawn — the accurate
record is **2 single synthetic transitions**, 0 trajectories, no scientific
evidence. But the preregistration is unfrozen and
escalations **E2–E5** stand, so `P.ExperimentRunner.run_campaign` has no
success path, and **no official run may be launched**.

Closing G-1 and G-2 and resolving Q-1/Q-2/Q-3 **removed obstacles; it granted
no approval.** Two new blocking gaps (**G-3**, **G-4**) and two new conflicts
(**CONFLICT-4**, **CONFLICT-5**) were opened by the correction, and both new
gaps fail closed.

## 4. Explicit non-claims

- Nothing here is scientific evidence. No world was run and no outcome inspected.
- No world, parameter, band, weight, demand distribution, horizon, threshold,
  success criterion or controller heuristic is adopted or proposed.
- The simultaneous-path field attribution creates **no** wallet credit,
  ownership, fairness claim, causal entitlement, Shapley meaning or extra
  interaction issuance, under either declared path semantics. The
  physical-path reading is confined to `model_realised_constant_rate` and is
  not generalised beyond it. E2 stands.
- F4's positive interaction holds **only** for opposing flows through a shared
  node under a separable convex potential, with its exact fixture assumptions
  asserted in the suite. It is **not** a claim about same-direction
  interaction or about any non-separable potential.
- Simultaneous groups remain representable at any size; **no permanent
  one-action-only design is forced**.
- **No dominance relation is asserted anywhere.** Dominance is defined over a
  registered metric set; slot **S-M is unfilled**, so the earlier claim that
  "C3 dominates C4" on illustrative fixture A is **withdrawn as a category
  error**, not merely corrected. Illustrative fixtures report delivered
  quantity, post-states and band/reserve violations as **separate dimensions**
  with no aggregate.
- The corrected C3 (`A_i = [x_i − L_i]_+`, two-stage) is a **candidate draft**,
  not an adopted controller. Its `build()` refuses. §27's naming conflict is
  recorded as **CONFLICT-4** and is an author decision.
- Declaring the `W.EdgeSpec` schema is **not** selecting `M_e` or `theta_e`;
  both remain unfilled preregistration slots and every reader refuses rather
  than defaulting them.
- **Gate-2.1B Theorem 4.1 is PROVED** (full algebra). An earlier revision of
  this map and of the readiness note called it "numerically validated, not
  proved"; that is **withdrawn** — the phrase in `p1c_v29.py` describes
  implementation conformance. Not proved, separately: long-run sustainability
  for non-regenerating stocks (Impossibility 6.4), the per-edge allocator's own
  guarantees (Observation 7.1), the `K∞` kernel (Observation 5.2).
- **Withdrawn: that P1C presupposes resource leaving the accounted system.**
  Its update already carries incoming transfers. The real distinction is that
  global conservation and local source preservation are different properties.
- **No selection or acceptance rule was invented**, and simultaneous quotes are
  not assumed additive (E2/O3). The existence of an exact quote implies no
  policy — committed sources state it "can never be an authorisation".
- **`R_eff` ≠ `R`, and `R_eff` does not implement `R`.** The provider/export
  floor is never cited as homeostatic reserve protection; an earlier revision
  did so and that inference is withdrawn. Nothing in the resolver moves
  resource toward a destination below its `R`.
- **C3's lexicographic ordering is proposal-level only.** No realised
  reserve-first saturation is claimed; `σ < 1` is reachable and demonstrated.
- The domain restrictions (`deg⁻(j) ≤ 1`, `0 ≤ R ≤ L ≤ U ≤ K`, `η = 1`) are
  **prospective first-study restrictions** validated at configuration time:
  not universal EBU theorems, not claims about future worlds, not frozen
  preregistration parameters, and none fixes a numeric value.
- **The earlier "Model-state advancement: NONE" claim is withdrawn.**
- The world remains **conservative** (`η = 1`); nothing here extends it to a
  lossy domain, and quantity is conserved exactly across every illustrative
  fixture (asserted per arm, per fixture).
- No contested-destination allocation rule was invented. G-3 fails closed.
- N/H/X remains excluded and is not revived.
- Nothing was committed, pushed, merged or deleted.
