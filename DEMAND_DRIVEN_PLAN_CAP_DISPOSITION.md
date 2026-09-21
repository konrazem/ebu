# Disposition of the plan-size cap

**Question.** `DemandWorld.max_plan_size` limits how many actions one plan may
contain. Is it (A) a computational enumeration limit, or (B) a physical
constraint that no more than `K` actions may execute in one epoch?

**Disposition: A — a computational enumeration limit.** Settled from existing
authority; no user decision is required.

---

## 1. Why the question arose

In the registered arbitrary-action studies exactly one group executed per
tick, so "at most `K` actions per plan" and "at most `K` actions per tick"
coincided and the distinction never had to be made.

The demand-driven model resolves several independent components in the same
epoch, so the two readings now differ. Under (A) a decomposed epoch may
execute more total actions than any single plan contains. Under (B) the limit
is global and legitimately couples otherwise separate demands.

The independent auditor's counterexample made the stakes concrete: three
independent one-unit deliveries, a limit of two, and a coupling defect that
merged them — three actions were then required where two were permitted, and
all service vanished. The coupling defect is fixed separately; the cap's
status still had to be settled, because it is what converted the mis-coupling
into a loss of service.

## 2. What authority says

Three sources, all in the registered lineage, agree.

1. **`gaussian_harness/candidates.py`**, module docstring:

   > A finite menu is an experimental restriction, not a claim that every
   > physically divisible quantity has been enumerated.

   The limit is described as a restriction on *enumeration*, and the sentence
   explicitly disclaims a physical reading.

2. **Object placement.** `max_group_size` is a field of `MenuSpecification`.
   The registered code keeps a separate object, `PhysicalRules`, documented as
   "Declared hard physical bounds and topology", holding cells, edges and the
   stock upper bound. The cap was not put there. That separation is a design
   statement, not an accident of layout.

3. **`LOCAL_GAUSSIAN_EBU_STAGE_A_DECISION_PACKET.md` §C**, under *Exhaustive
   deterministic enumeration*:

   > `m_max` is configuration, defaulting to 2 for the Stage-A fixture.

   It is listed among parameters chosen "on minimality grounds", alongside
   cell count and horizon — study configuration, not declared physics.

No source anywhere in the repository asserts a physical simultaneity limit, and
no world declares a mechanism that would enforce one.

## 3. What follows, and what is implemented

Under (A) the cap may not decide physical possibility. Three consequences are
implemented.

### 3.1 Coupling does not consult the cap

Coupling is derived from the **structural reach**
(`enumeration.structural_reach`): the tokens any *minimal* plan serving a
requirement could bind, computed from the world. It contains no reference to
`max_plan_size`. Coupling therefore cannot change when the cap changes.

### 3.2 An empty menu is not evidence of impossibility

`plans.serviceability` distinguishes four cases, and the harness reports each
as its own status:

| case | status | meaning |
|---|---|---|
| a complete executable plan exists within the cap | `EXECUTED` path | ordinary |
| none within the cap, but one exists uncapped | `SEARCH_INCOMPLETE_AT_PLAN_CAP` | the **search** was inadequate; physics permits service |
| none at any size | `NO_COMPLETE_PHYSICAL_PLAN` | genuine physical impossibility |
| the uncapped search exceeded its own budget | `SEARCH_BUDGET_EXCEEDED` | refuses to report a negative it did not establish |

The uncapped search is exact rather than heuristic. A minimal plan uses only
structural-reach routes and at most one action per route, so choosing per
route over that set is a complete search of the minimal plans, and it is
cheap because the reach is small. Where it would not be cheap, the fourth row
fails closed instead of guessing.

### 3.3 Admission asks about physics, so it ignores the cap

`admission.unserviceable_ids` calls `physically_serviceable`, not the capped
existence test. A demand serviceable only beyond the cap is therefore admitted
and then reported `SEARCH_INCOMPLETE_AT_PLAN_CAP`, which makes the search
limitation visible in the record instead of silently encoding it as physical
scarcity.

This is deliberately the uncomfortable choice. It can leave an obligation the
actor cannot discharge within the configured menu. That is the honest
behaviour under (A): the remedy is to raise the cap for that study, and the
status exists precisely so the need is visible before a study is frozen rather
than inferred afterwards from a puzzling rejection rate.

## 4. What is *not* claimed

- Not that the cap is scientifically inert. It restricts the actor's menu, and
  a menu restriction is a real feature of the experiment. What it may not do
  is masquerade as physics.
- Not that (B) is wrong as a model. A world that genuinely declares a
  simultaneity limit is a coherent and interesting variant — but it would be a
  **global** constraint on the whole jointly executed action set, it would
  legitimately couple otherwise separate demands, and it would need declaring
  as physics. No such declaration exists, so it is not adopted.
- Not that the per-component semantics are unchanged. They are not silently
  preserved: under (A) the cap bounds enumeration per plan, and the resulting
  asymmetry — a decomposed epoch may execute more total actions than the cap —
  is stated, tested, and held constant on both sides of the decomposition
  oracle so it cannot contaminate that comparison.

## 5. If a later study wants (B)

It must declare the simultaneity limit as a physical constraint of the world,
apply it to the combined executed action set at the joint gate rather than per
component, and accept that it couples demands. That is a model change
requiring its own authorization, and it would supersede this disposition for
that study only.
