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

**This is a declared design choice, not a logical consequence.** What the
authority in §2 settles is that the cap is a menu restriction rather than
physics, and therefore that it must not be reported as impossibility. It does
*not* by itself compel admitting beyond-cap obligations: refusing to admit
them, with an explicit non-scarcity reason, would be an equally coherent
policy under (A). Admission is chosen here because it keeps admission's
question purely physical and surfaces the limitation in the record rather than
folding it into a rejection rate. A study may adopt the alternative, provided
it declares the distinct reason and does not record it as scarcity.

It can leave an obligation the actor cannot discharge within the configured
menu. The status exists precisely so that need is visible before a study is
frozen rather than inferred afterwards from a puzzling rejection rate.

### 3.4 Three verdicts, kept apart all the way down

The uncapped search returns one of three answers, and **every caller must
preserve all three**:

| verdict | meaning | coupling | admission |
|---|---|---|---|
| `PHYSICALLY_SERVICEABLE` | a plan was found | full structural reach | not blocked |
| `PHYSICALLY_IMPOSSIBLE` | the whole space was enumerated, nothing found | empty reach; coupled only by shared pool | blocked |
| `SEARCH_BUDGET_EXCEEDED` | the search ran out of budget | **full** structural reach | **not** blocked; recorded as undecided |

An independent audit found both downstream collapses: coupling emptied the
reach for any non-serviceable verdict, and admission blocked on any
non-serviceable verdict. Either turns a computational limit into a physical
claim — the first deletes real dependencies, the second records a scarcity
rejection the search never established.

The search itself was also strengthened, because the old form manufactured
uncertainty. It pre-computed the worst-case space and refused before trying,
so nineteen independent one-unit suppliers against a one-unit request — with
nineteen one-action plans available — returned `SEARCH_BUDGET_EXCEEDED`. The
search now enumerates in increasing plan size and is bounded by the work it
actually does, so it answers such a case on the first evaluation and spends
budget only on requirements it cannot satisfy. `SEARCH_BUDGET_EXCEEDED` is
therefore now rare and genuine.

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

## 4a. Completeness requirement before confirmatory execution

Raising the cap until an observed `SEARCH_INCOMPLETE_AT_PLAN_CAP` rate merely
"looks negligible" is outcome-driven tuning and is **not** permitted. Before a
confirmatory run, the preregistration must declare one of the following, in
advance:

1. **Completeness.** A cap proved sufficient for the declared world and
   arrival law, so that `SEARCH_INCOMPLETE_AT_PLAN_CAP` cannot occur — for
   example a cap at least as large as the largest requirement any declared
   arrival can create, divided by the largest quantum. The registered run then
   asserts a zero rate and fails closed otherwise.
2. **An explicit computational-failure rule.** A declared maximum rate, fixed
   before execution, together with the disposition of a run that exceeds it —
   invalidated, or reported with the incomplete epochs excluded under a
   pre-declared rule. The rate is a falsifier of the *search*, never of the
   mechanism.

Either way the rule is fixed outcome-blind. This is recorded as a required
gate in `DEMAND_DRIVEN_FIRST_STUDY_DECISION_PACKET.md` §3.3.

## 5. If a later study wants (B)

It must declare the simultaneity limit as a physical constraint of the world,
apply it to the combined executed action set at the joint gate rather than per
component, and accept that it couples demands. That is a model change
requiring its own authorization, and it would supersede this disposition for
that study only.
