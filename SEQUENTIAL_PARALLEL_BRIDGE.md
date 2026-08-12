# The Sequential–Parallel Bridge of EBU

**Status:** Analytical foundation checkpoint v0.2
**Date:** 2026-08-12
**Purpose:** Freeze the audited mathematical bridge, provisional grouping rule, comparator discipline, and future deterministic test matrix before any parallel experiment or manuscript generation.

## 1. What this document is—and is not

This document is an internal theory note. It is intended to:

- derive the sequential–parallel connection from the fundamental EBU transition equation;
- distinguish algebraic identities from physical assumptions and untested hypotheses;
- introduce parallel groups without losing individual actions, actors, or responsibilities;
- preserve long-range, delayed-effect, and many-action questions for later testing;
- provide a reader-friendly path for future book revisions.

Version 0.2 also:

- records an independent algebra and worked-example audit of v0.1;
- defines a provisional operational rule for joint-transition groups;
- resolves the one-source, simultaneous-multi-action boundary at the level of
  physical measurement, while leaving individual settlement under O3 open;
- freezes a comparator decision procedure and a deterministic two-action
  analytical matrix;
- reconciles the theory with the current Part VI placement and the actual
  Gate 1D-C arm structure.

It is **not**:

- a modification of the locked Gate 1D-C protocol;
- evidence that the new parallel model is experimentally validated;
- a final book chapter;
- a complete theory of causality or allocation inside a parallel group.

The definitions in this note are analytical design decisions. They are not
observed results. The proposed tests in later sections have not been executed.

## 2. The idea in plain language

EBU measures the change between a before-state and an after-state:

\[
\boxed{EBU=D(\text{before})-D(\text{after})}
\]

If one journey is divided into several sequential steps, the intermediate distortion values cancel when the step values are added.

If several actions occur in parallel, the system can still measure the EBU of the combined transition from their common before-state to their common after-state.

Sequential and parallel execution have the same EBU when they produce the same final distortion. If parallel execution produces a different final distortion, the difference is the parallel interaction relative to the chosen sequential comparison.

This produces one foundation with two forms of observation:

- **Sequential:** observe and add consecutive transitions.
- **Parallel:** observe one joint transition of an overlapping action group.

## 3. Definitions and scientific status

### 3.1 System state

Let:

\[
X_t\in\mathcal X
\]

denote the complete system state relevant to the accounting boundary at time \(t\). The state may include physical sources, resource consumption, environmental effects, active commitments, and other variables required by the model.

**Modelling requirement:** If an effect matters physically but is omitted from \(X_t\), the resulting EBU calculation is incomplete.

### 3.2 Distortion function

Let:

\[
D:\mathcal X\rightarrow\mathbb R
\]

assign a distortion value to each state. Lower distortion represents a state closer to the defined balance condition.

The value \(D(X)\) is the **represented field distortion** at state \(X\)
under the declared accounting boundary. It may be nonlinear and may couple
several state coordinates. It is not a separately observed interaction term.

### 3.3 Transition EBU

For a transition from \(X_0\) to \(X_1\):

\[
\boxed{EBU(X_0\rightarrow X_1)=D(X_0)-D(X_1)}
\]

Therefore:

- \(EBU>0\): distortion decreased;
- \(EBU=0\): measured distortion did not change;
- \(EBU<0\): distortion increased.

Within EBU, this is the **foundational definition** used by the bridge.

### 3.4 Action transformation

An action \(A\) is represented provisionally by a transition rule:

\[
X' = T_A(X).
\]

This notation does not claim that every real action is deterministic. Later models may include time, uncertainty, environment, measurement error, or probability.

### 3.5 Parallel group

A **joint-transition group** \(G\) is a set of accepted actions that must be
evaluated through one common state transition because their effects cannot be
represented faithfully as independent transitions on the same frozen state:

\[
G=\{A_1,\ldots,A_n\}.
\]

The group preserves the identities of its child actions. Grouping does not mean that the actions disappear or that individual responsibility is erased.

The shorter term **parallel group** may be used only when the actions in the
joint-transition group also overlap in their effective intervals. A joint
transition may still require a schedule with different start and completion
times.

### 3.6 Effective interval, support, constraints, and boundary

For each accepted action \(A_i\), freeze before execution:

- its **effective interval** \(H_i=[s_i,h_i)\), beginning when its reservation
  or physical influence first constrains another action and ending at the
  declared measurement or settlement horizon;
- its **write support** \(W_i\), the state coordinates it may directly change;
- its **constraint support** \(C_i\), the sources, capacities, budgets,
  conservation rules, or other feasibility constraints it consumes or alters;
- its declared child transformation, quantities, commitments, and completion
  conditions; and
- its accounting boundary and distortion function.

Reading the same static datum is not by itself coupling. Sharing a geographic
label, an actor, or a receipt batch is also not by itself coupling.

### 3.7 Provisional exact grouping rule

At a declared evaluation horizon, first place candidate actions inside one
compatible accounting boundary. Construct an undirected dependency graph with
one node per action. Join \(A_i\) and \(A_j\) when:

1. their effective intervals overlap, \(H_i\cap H_j\neq\varnothing\); and
2. at least one of the following joint-evaluation conditions holds:
   - \(W_i\cap W_j\neq\varnothing\): they may change a common state coordinate;
   - \(C_i\cap C_j\neq\varnothing\): they share a source, capacity, budget, or
     other binding constraint;
   - one action changes a coordinate or commitment used by the other's
     transition, feasibility decision, completion condition, or declared
     measurement; or
   - the declared distortion function is not additively separable over the
     coordinates changed by the two actions on the registered domain; or
   - the declared observation model can identify only their common endpoint,
     not separate physically ordered endpoints.

The **minimal joint-transition groups are the connected components** of this
graph. Transitive closure is required: if \(A\) couples to \(B\) and \(B\)
couples to \(C\), all three belong to one group even when \(A\) and \(C\) do
not directly share a coordinate.

This rule is deliberately conservative and provisional. It makes five
boundaries exact:

- temporal overlap alone is insufficient;
- a common accounting boundary alone is insufficient;
- actions with disjoint supports and constraints may remain separate even if
  simultaneous, but separability must be shown rather than assumed;
- actions cannot be combined across incompatible distortion functions or
  units merely to obtain one number; and
- batching several receipts for measurement economy does not turn independent
  actions into a physical joint-transition group.

If an interaction crosses two existing accounting boundaries, a parent
boundary with a declared state and distortion function must be registered
before grouping. Otherwise the cross-boundary component remains unresolved;
its values must not be silently added.

### 3.8 Several simultaneous actions attached to one source

Several accepted actions that overlap while drawing from the same source or
aggregate budget satisfy the grouping rule automatically: their common source
belongs to their constraint support, and normally also to their write support.
The physical successor depends on the accepted quantity vector and its joint
constraint resolution:

\[
X_G=T_G\!\left(X_0; q_1^{\mathrm{acc}},\ldots,
q_n^{\mathrm{acc}}\right),
\qquad
\sum_i q_i^{\mathrm{acc}}\leq Q_{\max}.
\]

The physically measured value is one group finite difference:

\[
\boxed{EBU_G=D(X_0)-D(X_G)}.
\]

Independently evaluating every child against \(X_0\) is not a valid group
settlement on a nonlinear shared source. It can double-count improvement or
undercharge joint damage. The exact joint value therefore replaces the naive
sum for physical closure.

This resolves **how the physical transition is measured**. It does not resolve
how that joint value is divided among child actions or actors. Proportional,
marginal, path-based, equal, guaranteed, or joint-account settlements remain
allocation rules unless separately justified. Their general multi-source,
multi-tick incentives and split invariance remain O3.

Actions attached to the same source but executed in disjoint effective
intervals, with the later action recomputed from the live predecessor state
and with no overlapping reservation, are sequential rather than parallel.

## 4. Sequential telescoping

Consider two sequential actions:

\[
X_0\xrightarrow{A}X_A\xrightarrow{B}X_{AB}.
\]

The first transition has EBU:

\[
EBU_A=D(X_0)-D(X_A).
\]

The second action must be evaluated against the state left by the first:

\[
EBU_{B\mid A}=D(X_A)-D(X_{AB}).
\]

Adding them gives:

\[
\begin{aligned}
EBU_A+EBU_{B\mid A}
&=D(X_0)-D(X_A)+D(X_A)-D(X_{AB})\\
&=D(X_0)-D(X_{AB}).
\end{aligned}
\]

The intermediate state cancels:

\[
\boxed{EBU_{A\rightarrow B}=EBU_A+EBU_{B\mid A}=D(X_0)-D(X_{AB})}
\]

For \(n\) sequential transitions:

\[
X_0\rightarrow X_1\rightarrow\cdots\rightarrow X_n,
\]

\[
\boxed{\sum_{i=1}^{n}\bigl[D(X_{i-1})-D(X_i)\bigr]=D(X_0)-D(X_n)}
\]

This is an **algebraic identity** following directly from the EBU transition definition.

### 4.1 What telescoping does not prove

Telescoping does not prove that:

- the state is measured completely;
- the distortion function is physically correct;
- every causal contribution is individually identifiable;
- two different execution paths reach the same final state;
- delayed or external effects have already been captured.

It proves only that correctly measured consecutive EBU differences add to the EBU difference between the first and last measured states.

## 5. Parallel group EBU

Let the parallel execution of \(A\) and \(B\) move the system from \(X_0\) to \(X_{\parallel}\):

\[
X_0\xrightarrow{A\parallel B}X_{\parallel}.
\]

The group EBU is:

\[
\boxed{EBU_{A\parallel B}=D(X_0)-D(X_{\parallel})}
\]

For a general parallel group \(G\):

\[
\boxed{EBU_G=D(X_0)-D(X_G)}
\]

This measures the physical result of the group transition. It does not automatically identify the separate causal EBU of every child action.

## 6. The sequential–parallel bridge

To compare parallel execution with sequential execution, the sequential order must be named.

For the comparison order \(A\rightarrow B\):

\[
X_{AB}=T_B(T_A(X_0)).
\]

Define the parallel interaction relative to that order:

\[
\boxed{I_{AB\parallel(A\rightarrow B)}=EBU_{A\parallel B}-EBU_{A\rightarrow B}}
\]

Substituting the endpoint equations gives:

\[
\begin{aligned}
I_{AB\parallel(A\rightarrow B)}
&=\bigl[D(X_0)-D(X_{\parallel})\bigr]
-\bigl[D(X_0)-D(X_{AB})\bigr]\\
&=D(X_{AB})-D(X_{\parallel}).
\end{aligned}
\]

Therefore:

\[
\boxed{EBU_{A\parallel B}=EBU_{A\rightarrow B}+I_{AB\parallel(A\rightarrow B)}}
\]

where:

\[
\boxed{I_{AB\parallel(A\rightarrow B)}=D(X_{AB})-D(X_{\parallel})}
\]

### 6.1 Interpretation

- \(I=0\): parallel and selected sequential execution end at equal distortion.
- \(I>0\): parallel execution ends with less distortion than the selected sequential comparison.
- \(I<0\): parallel execution ends with more distortion than the selected sequential comparison.

### 6.2 State equivalence and EBU equivalence

If:

\[
X_{\parallel}=X_{AB},
\]

then necessarily:

\[
I=0.
\]

However, identical final states are sufficient but not necessary. Two different states may have the same distortion:

\[
D(X_{\parallel})=D(X_{AB})
\quad\Rightarrow\quad
I=0.
\]

Thus:

- **state equivalence** is the stronger condition;
- **EBU equivalence** requires only equal final distortion under the chosen \(D\).

### 6.3 Order dependence

The reverse sequential order is:

\[
X_{BA}=T_A(T_B(X_0)).
\]

If:

\[
X_{AB}\neq X_{BA},
\]

the actions are order-dependent. Parallel execution then has at least two possible sequential comparisons:

\[
I_{AB\parallel(A\rightarrow B)}=D(X_{AB})-D(X_{\parallel}),
\]

\[
I_{AB\parallel(B\rightarrow A)}=D(X_{BA})-D(X_{\parallel}).
\]

There is no scientifically honest, unique, unnamed “sequential interaction” unless the comparison order or another reference rule has been fixed.

## 7. Field distortion and same-baseline non-additivity

For every child with a declared standalone transformation using its accepted
quantity, define the hypothetical same-baseline endpoint and value:

\[
X_i^{(0)}=T_{A_i}(X_0;q_i^{\mathrm{acc}}),
\qquad
EBU_i^{(0)}=D(X_0)-D(X_i^{(0)}).
\]

These are diagnostic values in which every child is evaluated as if it alone
received the complete common before-state. They are not consecutive
transitions, child settlements, or causally identified contributions.

Define the **same-baseline field non-additivity** of group \(G\) as:

\[
\boxed{N_G:=EBU_G-\sum_{i\in G}EBU_i^{(0)}}.
\]

Thus \(N_G\) is the correction required when replacing a naive sum of
same-baseline child values with the exact joint finite difference. A positive
\(N_G\) means the group value exceeds that naive sum; a negative \(N_G\)
means it falls below it. The sign has no universal moral or causal meaning.

The diagnostic is defined only when the child transformations, accepted
quantities, common boundary, and same-baseline endpoints are all declared. It
can reflect nonlinear field coupling, redundancy, cancellation, shared
constraints, or a difference between the joint and standalone mechanisms. It
does not allocate the correction among children.

### 7.1 Scalar nonlinear example

Let:

\[
D(x)=x^2
\]

and suppose two actions change the state by \(a\) and \(b\). The total endpoint is \(x+a+b\), and:

\[
EBU=x^2-(x+a+b)^2.
\]

The exact group value is:

\[
EBU_G=-2x(a+b)-a^2-b^2-2ab.
\]

The same-baseline child values sum to:

\[
EBU_A^{(0)}+EBU_B^{(0)}=-2x(a+b)-a^2-b^2,
\]

and therefore:

\[
\boxed{N_G=-2ab}.
\]

This cross-term is a real correction to naive same-baseline addition. It shows
that both changes enter the same nonlinear distortion function. It does
**not**, by itself, prove a uniquely parallel physical interaction.

A correct sequential calculation already includes the cross-term because the second action is evaluated against the state left by the first:

\[
EBU_A=x^2-(x+a)^2,
\]

\[
EBU_{B\mid A}=(x+a)^2-(x+a+b)^2.
\]

Therefore:

\[
EBU_A+EBU_{B\mid A}=x^2-(x+a+b)^2.
\]

**Key distinction:**

- \(N_G\) compares exact joint measurement with a naive same-baseline sum;
- \(I_{G\mid\pi}\) compares exact joint measurement with a named live-state
  sequential schedule;
- a nonlinear shared field can have \(N_G\neq0\) while
  \(I_{G\mid\pi}=0\) because the correct sequential calculation already
  contains the same field correction; and
- neither quantity by itself identifies causal child contributions or fixes
  institutional settlement shares.

## 8. Worked examples

### 8.1 Example 1 — Parallel and sequential are equivalent

A tank has a target volume of \(10\) litres. Define:

\[
D(V)=(V-10)^2.
\]

Initially:

\[
V_0=6,\qquad D(V_0)=16.
\]

Action \(A\) adds \(2\) litres. Action \(B\) adds \(1\) litre.

Sequentially:

\[
6\xrightarrow{A}8\xrightarrow{B}9.
\]

For \(A\):

\[
EBU_A=16-4=12.
\]

For \(B\) after \(A\):

\[
EBU_{B\mid A}=4-1=3.
\]

Therefore:

\[
EBU_{A\rightarrow B}=12+3=15.
\]

If both additions occur in parallel and the final volume is also \(9\) litres:

\[
EBU_{A\parallel B}=16-1=15.
\]

Thus:

\[
I=15-15=0.
\]

The field is nonlinear, but there is no additional parallel interaction because the final distortion is the same.

**Exercise:** Reverse the sequential order. Does the final distortion change? Does the allocation of step EBU change?

### 8.2 Example 2 — True positive parallel interaction

Suppose a heavy unstable panel requires two supports applied at the same time. Applied separately, each support fails to move the panel safely. Use a simplified distortion scale:

\[
D(X_0)=9.
\]

In the sequential comparison, neither temporary support creates a lasting transition:

\[
D(X_{AB})=9,
\qquad
EBU_{A\rightarrow B}=9-9=0.
\]

Applied simultaneously, the panel reaches a stable state:

\[
D(X_{\parallel})=1,
\qquad
EBU_{A\parallel B}=9-1=8.
\]

Therefore:

\[
I=8-0=8.
\]

This is a model of synergy: simultaneity changes the endpoint.

**Exercise:** Which measurements would be required to show that the improvement came from simultaneity rather than from an omitted state variable?

### 8.3 Example 3 — Negative parallel interaction

Two repair operations share a narrow workspace. Performed sequentially, they leave:

\[
D(X_{AB})=2.
\]

Performed simultaneously, interference between the workers leaves:

\[
D(X_{\parallel})=5.
\]

If the initial distortion is \(10\):

\[
EBU_{A\rightarrow B}=10-2=8,
\]

\[
EBU_{A\parallel B}=10-5=5.
\]

Thus:

\[
I=5-8=-3.
\]

Parallel execution created less improvement than sequential execution.

**Exercise:** Would the result change if parallel execution finished earlier and time itself were included in the state?

### 8.4 Example 4 — Cancellation does not erase resource use

Let the state contain both a target deviation \(y\) and cumulative resource use \(r\). Define:

\[
D(y,r)=y^2+\lambda r,
\qquad \lambda>0.
\]

Initially:

\[
(y_0,r_0)=(0,0).
\]

Action \(A\) changes \(y\) by \(+1\), action \(B\) changes it by \(-1\), and each consumes one unit of resource. After both actions:

\[
(y_1,r_1)=(0,2).
\]

The target effects cancel, but:

\[
EBU_G=D(0,0)-D(0,2)=0-2\lambda=-2\lambda.
\]

The actions did not annihilate. Their target effects cancelled while their resource consequences remained.

**Exercise:** What false conclusion would result if \(r\) were omitted from the system state?

### 8.5 Example 5 — Order dependence

Let:

\[
T_A(x)=2x,
\qquad
T_B(x)=x+1,
\qquad
x_0=1,
\qquad
D(x)=x^2.
\]

Then:

\[
A\rightarrow B:\quad 1\rightarrow2\rightarrow3,
\qquad D=9,
\]

while:

\[
B\rightarrow A:\quad 1\rightarrow2\rightarrow4,
\qquad D=16.
\]

Because the sequential endpoints differ, a parallel result cannot be compared with “the” sequential result until a comparison order is declared.

**Exercise:** If a parallel rule produces \(x_{\parallel}=3.5\), calculate the interaction relative to both sequential orders.

## 9. Many-action generalization

For a parallel group:

\[
G=\{A_1,\ldots,A_n\},
\]

let \(X_G\) be the parallel endpoint.

A sequential comparison requires an ordering \(\pi\), a permutation of the actions:

\[
X_{\pi}
=T_{A_{\pi(n)}}\circ\cdots\circ T_{A_{\pi(1)}}(X_0).
\]

Sequential telescoping gives:

\[
EBU_{\mathrm{seq},\pi}=D(X_0)-D(X_{\pi}).
\]

Group EBU is:

\[
EBU_G=D(X_0)-D(X_G).
\]

The interaction relative to ordering \(\pi\) is:

\[
\boxed{I_{G\mid\pi}=EBU_G-EBU_{\mathrm{seq},\pi}=D(X_{\pi})-D(X_G)}
\]

This is the proposed mathematical bridge for many actions.

### 9.1 Admissible sequential comparators

The comparator is part of the scientific claim, not a formatting choice. For
a group \(G\), let \(\Pi_G\) be the preregistered set of admissible sequential
schedules. A schedule belongs to \(\Pi_G\) only if it:

1. starts from the same represented state \(X_0\);
2. contains the same child actions and declared commitments;
3. uses live predecessor states rather than independent copies of \(X_0\);
4. respects physical feasibility, precedence, reservations, deadlines, and
   safety constraints;
5. fixes whether accepted child quantities are held constant or are
   recomputed by the declared allocation rule;
6. includes the same exogenous drive and a common evaluation horizon; and
7. represents waiting time, duration, resource use, and completion time in
   the state whenever they affect \(D\) or later feasibility.

If no schedule satisfies these requirements, there is no valid sequential
comparator. Group EBU remains defined, but comparator-relative interaction is
reported as **undefined**, not forced to zero and not compared with a
physically impossible serial history.

### 9.2 Comparator decision table

| Situation | Required comparator rule | Required report |
|---|---|---|
| Every admissible order reaches the same represented endpoint | Use a preregistered identifier order for reproducibility | One interaction value; confirm order invariance |
| Endpoints differ but one physical or contractual precedence is mandatory | Use that mandatory order | Interaction relative to the named order |
| Reservation order or actual start order is the scientific object | Use the frozen observed order, without outcome-dependent substitution | Interaction relative to that order; state why it is relevant |
| Several non-commuting orders are feasible and none is privileged | Evaluate every preregistered feasible order, or a preregistered exact extremum procedure | The vector or range \([\min_{\pi\in\Pi_G}I_{G\mid\pi},\max_{\pi\in\Pi_G}I_{G\mid\pi}]\), plus endpoints |
| A policy requires one canonical order despite several feasible orders | Freeze the policy order before results | The canonical value and sensitivity to the other registered orders; do not call it unique physics |
| Large \(n\) makes all permutations impractical | Freeze a schedule family, sampling rule, or exact optimization method before execution | Coverage, omitted schedules, and uncertainty; no post-result comparator search |
| No feasible sequential schedule preserves the declared children and constraints | No comparator is valid | Group EBU and `nonserializable`; interaction undefined |

The default for the first deterministic two-action programme is: enumerate
both feasible orders; if their represented endpoints are equal, use the lower
identifier order as the compact reported comparator and retain the equality
check. If endpoints differ, report both interactions. This default is an
analytical design decision for the proposed test programme, not a universal
social priority rule.

### 9.3 Quantity-fixed and rule-replayed comparisons

Shared-capacity systems expose a distinction that must never remain implicit:

- A **quantity-fixed comparator** serializes the already accepted group
  quantities. It isolates the physical effect of simultaneity for the same
  child deliveries.
- A **rule-replayed comparator** re-applies the declared permission and
  allocation rule after each predecessor state. It compares complete
  scheduling institutions, and accepted quantities may differ by order.

Both can be legitimate, but they answer different questions. A report must
name which was used. A difference caused solely by reallocation is not
evidence that simultaneity itself changed the endpoint.

## 10. Four quantities that must not be conflated

The diagnostic \(N_G\) from §7 remains separate from the four operational
categories below. In particular, it is not a fifth kind of child attribution
or settlement.

### 10.1 Physical measurement of the joint transition

The group endpoint determines the physical transition value:

\[
\boxed{M_G:=EBU_G=D(X_0)-D(X_G)}.
\]

This is an endpoint measurement under the declared state and distortion
boundary. It is not automatically a causal estimate of what each child did,
and it is not a comparison with what would have happened without the group.

### 10.2 Comparator-relative parallel interaction

For an admissible named comparator \(\pi\):

\[
\boxed{I_{G\mid\pi}=D(X_\pi)-D(X_G)}.
\]

This measures the endpoint advantage or disadvantage of the group schedule
relative to that comparator. It changes when a non-commuting comparator
changes. It is not an individual child value.

### 10.3 Causally identified child contribution

A child contribution \(C_i\) exists as a scientific estimate only under a
declared intervention or causal model with evidence sufficient to identify
it. Evidence may include:

- separate meters with demonstrated closure;
- controlled interventions or isolated action trials;
- a validated structural causal model;
- identifiable resource flows; or
- a preregistered decomposition whose interaction remainder is retained.

Even then, non-additive systems may require an explicit causal interaction or
unidentified remainder:

\[
M_G=\sum_{i\in G}C_i+C_{\mathrm{interaction}}+R_{\mathrm{causal}}.
\]

This equation is a bookkeeping form for a particular validated causal model,
not a universal decomposition theorem. If the evidence does not identify the
terms, the correct status is **unidentified**.

### 10.4 Institutionally assigned settlement share

Let \(S_i\) be the settlement assigned to child \(i\), and let \(R_G\) be the
explicit group residual carried by a provider, institution, reserve, joint
account, or unresolved account. Physical closure requires:

\[
\boxed{\sum_{i\in G}S_i+R_G=M_G.}
\]

The simpler equation \(\sum_i S_i=M_G\) is valid only when the registered
settlement rule sets \(R_G=0\). A binding pre-action promise may deliberately
make actor settlements differ from later causal estimates; the residual must
remain visible rather than rewriting the physical endpoint.

Possible allocation rules include measured causal contribution, predefined
proportional shares, reservation-order allocation, equal division,
provider-guaranteed shares, or permanently joint settlement. Except for a
causally identified rule with adequate evidence, these are institutional
design choices. They must be frozen before outcome inspection whenever
discretion could bias the allocation.

## 11. Group receipt architecture

“Join” should mean:

> Measure the common physical transition once while preserving every child action, actor, provider, promise, and responsibility.

A proposed group record contains:

- group identifier;
- accounting boundary, state schema, distortion version, units, and horizon;
- common initial state or state reference;
- each child's effective interval, write support, and constraint support;
- dependency edges and the connected-component grouping decision;
- committed actions already affecting the field;
- child action records;
- group quote and its assumptions;
- accepted quantity vector and joint permission/allocation rule;
- observed group endpoint;
- physical group EBU;
- same-baseline child diagnostic inputs and \(N_G\), when defined;
- admissible sequential-comparator set and named reported comparator;
- interaction value or range, when a valid comparator exists;
- causal evidence, identified contributions, and causal remainder status;
- institutional allocation rule and its version;
- individual settlement shares;
- provider, institutional, reserve, joint, or unresolved residuals;
- unresolved effects and later measurement horizons.

Grouping must not delete child receipts or erase responsibility.

A **receipt batch** may contain several independent groups to share storage,
communication, or verification work. The batch must retain their separate
initial states, endpoints, and values. Batch membership is never evidence of
physical interaction.

## 12. Receipt batching and its possible economy

The cost of producing a receipt is itself a physical and computational activity. It should be kept separate from the EBU of the target action unless the declared accounting boundary combines them.

Let non-negative quantities represent measurement and verification resource costs:

- \(K_0\): shared baseline/final-state measurement cost;
- \(K_i\): action-specific verification cost for action \(i\);
- \(K_G\): additional group coordination and interaction-analysis cost.

Separate receipts cost:

\[
K_{\mathrm{separate}}=nK_0+\sum_{i=1}^{n}K_i.
\]

A group receipt costs:

\[
K_{\mathrm{group}}=K_0+\sum_{i=1}^{n}K_i+K_G.
\]

The modelled saving is:

\[
\boxed{K_{\mathrm{separate}}-K_{\mathrm{group}}=(n-1)K_0-K_G}
\]

The group receipt is cheaper only if:

\[
\boxed{K_G<(n-1)K_0}
\]

The subtraction is algebraically correct under the stated cost model. The
model assumes that exactly one baseline/final measurement of equivalent
quality can replace \(n\) separate measurements, every \(K_i\) is unchanged by
grouping, and all additional group work is represented by \(K_G\). If
grouping changes measurement quality, child-verification cost, latency, or
risk, the cost equations must be extended before using the inequality.

This is not a universal EBU law. It is a conditional batching model that must
be tested using real measurement, computation, communication, storage, and
coordination costs. It applies to receipt production and does not itself
define a joint physical transition.

## 13. Long-range and delayed actions

The bridge does not replace long-range testing. It reveals why long-range actions require additional temporal definitions.

An action may appear complete at \(t_1\) while important effects arrive at a later horizon \(T\):

\[
X_{t_0}\xrightarrow{A}X_{t_1}\rightarrow X_T.
\]

At least two values may be relevant:

\[
EBU_{\mathrm{immediate}}=D(X_{t_0})-D(X_{t_1}),
\]

\[
EBU_{\mathrm{horizon}\,T}=D(X_{t_0})-D(X_T).
\]

Their difference is:

\[
\Delta EBU_{\mathrm{delayed}}=D(X_{t_1})-D(X_T).
\]

The subtraction is a temporal accounting identity when the same state and
distortion definitions apply at all three horizons. It does not by itself
attribute the later change to action \(A\): natural drive, later actions, and
boundary changes may also contribute. Causal attribution requires a declared
counterfactual or another identified model. If elapsed time, ageing, waiting,
or opportunity loss matters, the clock and the corresponding physical state
must be represented rather than appended as an informal explanation.

The scientific work remains to determine:

- which horizon is appropriate;
- how causality is attributed across distance and time;
- how uncertainty grows with the horizon;
- when a receipt remains open, provisional, or settled;
- how later actions interacting with the same field are separated;
- how irreversible or distributed effects are represented.

Long-range actions therefore remain a dedicated testing workstream after the
local transition baseline.

## 14. Independent equation audit and deterministic two-action matrix

No model step, trajectory, runner, candidate experiment, or result inspection
was used for this section. Every check is symbolic arithmetic or a hand-worked
finite example.

### 14.1 Equation audit of v0.1

| Object | Audit result | Qualification or correction in v0.2 |
|---|---|---|
| \(EBU(X_0\to X_1)=D(X_0)-D(X_1)\) | Correct as the adopted transition definition | It is an endpoint value under the declared boundary, not automatically an action-causal effect |
| Two-step and \(n\)-step telescoping | Algebraically exact | Every term must use the live predecessor state, the same \(D\), and compatible boundaries |
| \(EBU_G=D(X_0)-D(X_G)\) | Correct as group-transition measurement | Group membership now follows §§3.6–3.8 rather than unspecified “sufficient overlap” |
| \(I_{G\mid\pi}=EBU_G-EBU_{\mathrm{seq},\pi}=D(X_\pi)-D(X_G)\) | Sign and cancellation correct | Interaction is undefined when no admissible serial comparator exists |
| State equivalence versus equal distortion | Correct | Equal \(D\) can hide different future capacity; both endpoints must be retained |
| Nonlinear \(-2ab\) example | Expansion and conclusion correct | A cross-term alone is not parallel interaction |
| Same-baseline child sum | Not named in v0.1 | Defined as diagnostic \(N_G=EBU_G-\sum_iEBU_i^{(0)}\); it is neither live-state telescoping nor causal allocation |
| Many-action permutation formula | Correct | A permutation is insufficient when duration, waiting, or exogenous drive matters; the comparator may need a full schedule |
| Simple settlement closure \(\sum_iS_i=EBU_G\) | Correct only for zero residual | Replaced by \(\sum_iS_i+R_G=EBU_G\) |
| Batching saving \((n-1)K_0-K_G\) | Algebraically correct | Conditional on equivalent shared measurement and unchanged child costs |
| Delayed component \(D(X_{t_1})-D(X_T)\) | Algebraically correct | It is not action attribution without a causal comparator |

The v0.1 numerical examples also check out. In the tank example the reverse
order allocates step EBU as \(7+8\), rather than \(12+3\), while preserving
the total \(15\). In the order-dependence example with
\(x_\parallel=3.5\),

\[
EBU_G=1-12.25=-11.25,
\]

so:

\[
I_{G\mid A\to B}=-11.25-(-8)=-3.25,
\qquad
I_{G\mid B\to A}=-11.25-(-15)=3.75.
\]

The opposite signs are not a contradiction; they demonstrate why the
comparator must be named.

### 14.2 Frozen analytical matrix

The following nine cases are the minimum matrix proposed for a later,
separately preregistered deterministic study. “Falsifier” below means a
future test condition; none has been evaluated.

#### M1 — Independent actions

Let \(X=(x,y)\), \(D=x^2+y^2\), and \(X_0=(2,3)\). Define
\(T_A(x,y)=(x-1,y)\) and \(T_B(x,y)=(x,y-1)\). Both sequential orders and
the parallel rule reach \((1,2)\).

\[
EBU_G=13-5=8,
\qquad N_G=0,
\qquad I_{G\mid A\to B}=I_{G\mid B\to A}=0.
\]

These actions have disjoint supports and require no joint-transition group;
they may still be executed or batched together. **Future falsifier:** a
nonzero interaction or a shared constraint appears under the declared
complete state, disproving independence or state completeness.

#### M2 — Shared-source capacity conflict

Let \(X=(s,a,b)\), \(D=(2-a)^2+(2-b)^2\), and
\(X_0=(3,0,0)\). Two children each request two units from a source with
aggregate capacity three. For accepted quantity \(q\), define
\(T_A(q)(s,a,b)=(s-q,a+q,b)\) and
\(T_B(q)(s,a,b)=(s-q,a,b+q)\). A frozen proportional parallel allocator accepts
\((1.5,1.5)\), giving \(X_G=(0,1.5,1.5)\):

\[
EBU_G=8-0.5=7.5.
\]

Each accepted 1.5-unit child has same-baseline value \(3.75\), so
\(N_G=7.5-(3.75+3.75)=0\).

A quantity-fixed serialization of the accepted vector reaches the same
endpoint in either order, so \(I=0\). A rule-replayed serialization accepts
\((2,1)\) or \((1,2)\), gives distortion \(1\), and therefore has
\(I=0.5\) relative to either order. The latter difference is caused by the
allocation rule, not by simultaneity alone. **Future falsifiers:** accepted
export exceeds three; independent same-baseline settlements replace the joint
value; or the report fails to distinguish quantity-fixed from rule-replayed
comparators.

#### M3 — Endpoint-equivalent execution on a shared nonlinear field

Let \(D(V)=(V-10)^2\), \(V_0=6\), \(T_A(V)=V+2\),
\(T_B(V)=V+1\), and \(T_G(V)=V+3\). Both orders and parallel execution
reach \(V=9\):

\[
EBU_G=16-1=15,
\qquad N_G=15-(12+7)=-4,
\qquad I=0.
\]

The nonlinear step allocations differ by order, but the endpoint value does
not. **Future falsifier:** equal endpoints produce unequal group and
sequential EBU, indicating an implementation, boundary, or cost-accounting
mismatch.

#### M4 — Positive parallel interaction

Let \(X=d\), \(D(d)=d\), and \(d_0=9\). For non-overlapping execution,
\(T_A(d)=T_B(d)=d\): each temporary support leaves no lasting change, so the
registered sequential comparator ends at \(9\). The simultaneous joint
transformation is \(T_G(9)=1\):

\[
EBU_{\mathrm{seq}}=0,
\quad EBU_G=8,
\quad N_G=8,
\quad I=8.
\]

**Future falsifier:** the joint endpoint does not have lower distortion than
the registered sequential endpoint, or the apparent gain disappears when an
omitted support state or duration is added.

#### M5 — Negative parallel interaction

Let \(D(d)=d\), \(d_0=10\), and for separated work define
\(T_A(d)=T_B(d)=\max(0,d-4)\). Both registered sequential schedules finish
at \(d=2\), while the simultaneous interference rule \(T_G(10)=5\) makes the
joint schedule finish at \(d=5\):

\[
EBU_{\mathrm{seq}}=8,
\quad EBU_G=5,
\quad N_G=5-(4+4)=-3,
\quad I=-3.
\]

**Future falsifier:** the joint endpoint is not worse than the comparator, or
the difference is entirely a hidden mismatch in duration, resources, or
child quantities.

#### M6 — Cancellation with retained resource use

Let \(X=(y,r)\), \(D(y,r)=y^2+\lambda r\), \(\lambda>0\), and
\(X_0=(0,0)\). Define \(T_A(y,r)=(y+1,r+1)\) and
\(T_B(y,r)=(y-1,r+1)\). The joint rule applies both increments. Both complete
schedules end at \((0,2)\):

\[
EBU_G=-2\lambda,
\qquad N_G=(-2\lambda)-2(-1-\lambda)=2,
\qquad I=0.
\]

**Future falsifier:** the result is reported as zero merely because \(y\)
cancels, or consumed resources disappear from the represented state.

#### M7 — Redundancy

Let \(x\) be remaining deficit, \(D(x)=x^2\), \(x_0=2\), and
\(T_A(x)=T_B(x)=T_G(x)=0\). Either child alone sets \(x=0\); applying the
second after the first changes nothing. The joint and sequential endpoints are
both zero:

\[
EBU_G=4,
\qquad N_G=4-(4+4)=-4,
\qquad I=0.
\]

Two independent same-baseline credits of four would sum to eight and violate
physical closure. **Future falsifier:** child settlements plus residual exceed
four, or the redundant child is described as a second measured restoration.

#### M8 — Order dependence

Let \(T_A(x)=2x\), \(T_B(x)=x+1\), \(D(x)=x^2\), \(x_0=1\), and let the
declared parallel rule give \(x_G=3.5\). Then:

\[
X_{AB}=3,
\quad X_{BA}=4,
\quad EBU_G=-11.25,
\quad N_G=-11.25-(-3-3)=-5.25,
\]

\[
I_{G\mid A\to B}=-3.25,
\qquad I_{G\mid B\to A}=3.75.
\]

**Future falsifier:** the implementation composes either order incorrectly,
or reports one unnamed interaction while suppressing the other admissible
order.

#### M9 — Causally inseparable group

Let \(X=d\), \(D(d)=d\), and \(d_0=5\). The declared mechanism has only a
joint transformation, \(T_G(5)=1\); neither child has a physically admissible
standalone or sequential transformation. Therefore:

\[
EBU_G=4,
\]

while \(I_{G\mid\pi}\) is undefined, individual causal contributions are
unidentified, \(N_G\) is undefined because no standalone child
transformations exist, and institutional shares must satisfy
\(\sum_iS_i+R_G=4\). **Future falsifier:** a sequential endpoint or individual
causal number is invented without a declared intervention model, or assigned
shares are labelled as measured physics.

### 14.3 Matrix summary

| Case | Joint group required? | Same-baseline diagnostic | Comparator result | Individual causal status |
|---|---|---|---|---|
| M1 independent | No, if separability is verified | \(N_G=0\) | Both orders, \(I=0\) | Separately measurable in the declared state |
| M2 shared capacity | Yes | \(N_G=0\) for accepted vector | Quantity-fixed \(I=0\); rule-replayed \(I=0.5\) | Allocation-dependent unless separately identified |
| M3 endpoint-equivalent | Yes for common-field measurement | \(N_G=-4\) | Both orders, \(I=0\) | Step values order-dependent |
| M4 positive interaction | Yes | \(N_G=8\) | \(I=8\) | Joint mechanism; child split not implied |
| M5 negative interaction | Yes | \(N_G=-3\) | \(I=-3\) | Joint interference; child split not implied |
| M6 cancellation | Yes if simultaneous/common resource | \(N_G=2\) | \(I=0\), group EBU negative | Resource use identifiable; target shares need care |
| M7 redundancy | Yes for common endpoint | \(N_G=-4\) | \(I=0\) | Naive independent credit forbidden |
| M8 order dependence | Yes | \(N_G=-5.25\) | Both values required | Comparator-relative |
| M9 inseparable | Yes | Undefined | No valid comparator | Unidentified; allocation only |

## 15. Validation programme

The new theory should be tested in layers. Gate 1D-C and every other locked
study must remain unchanged unless separately authorized.

### Layer 0 — Algebra and specification review

- verify every telescoping derivation;
- verify signs and endpoint definitions;
- distinguish state equivalence from distortion equivalence;
- distinguish same-baseline non-additivity from comparator-relative interaction;
- require a named sequential comparator;
- identify all assumptions embedded in \(X\), \(D\), and \(T\);
- verify dependency-graph grouping and receipt-batch separation;
- verify units and boundary compatibility before any cross-action sum.

### Layer 1 — Existing Gate 1D-C boundary

- preserve Gate 1D-C exactly as frozen;
- restricted arms B/C/D/S select at most one action per configured source per
  micro-step;
- C and D quote and settle only the selected restricted action;
- arm A can execute several simultaneous outgoing deliveries, but it is a
  settlement-free capability-superset benchmark and is forbidden as the
  alignment baseline;
- retain arm A's exact group-versus-naive diagnostic without converting it
  into child settlements or an O3 resolution;
- do not present the whole gate as a \(|G|=1\) experiment;
- preserve the operational incident record: one official invocation failed in
  preflight before receipt creation or model-state advancement, the scientific
  state remains `UNSTARTED`, the cumulative invocation count remains one, and
  any second invocation requires separate explicit authorization;
- resolve that operational incident separately;
- do not add parallel mechanisms to that gate;
- if scientific execution is later authorized, use the restricted arms as the
  one-action-per-source baseline and arm A only as its registered
  settlement-free capability comparator.

### Layer 2 — Deterministic two-action bridge tests

Test:

- endpoint-equivalent sequential and parallel actions;
- nonlinear distortion with no true parallel interaction;
- positive interaction;
- negative interaction;
- cancellation with resource use retained;
- redundancy;
- capacity conflict;
- both sequential orders;
- quantity-fixed versus rule-replayed shared-capacity comparators;
- causally inseparable groups with undefined serial interaction.

### Layer 3 — Group receipt and allocation tests

Test:

- causally separable child actions;
- causally inseparable groups;
- conservation of settlement shares;
- provider-guaranteed allocations;
- shared measurement savings;
- cases in which grouping costs more than separate receipts.

### Layer 4 — Many-action and scheduling tests

Test:

- increasing group sizes;
- permutation/order sensitivity;
- reservation policies;
- congestion and shared capacity;
- stale committed-field information;
- comparisons with serializability, transactions, locks, and scheduling in computer science.

Computer-science concepts are comparisons and design tools, not automatic proofs of physical EBU laws.

### Layer 5 — Long-range and delayed-effect tests

Test:

- propagation across connected sources;
- delayed state changes;
- different settlement horizons;
- overlapping causal chains;
- uncertainty and later correction;
- irreversible effects;
- actions whose consequences cross the original accounting boundary.

### Layer 6 — Stochastic and empirical models

- add measurement error and uncertainty;
- compare predicted and realized group EBU;
- test provider learning and reconciliation;
- evaluate robustness under incomplete observation;
- determine which theoretical quantities are empirically identifiable.

## 16. Placement in the EBU books

### 16.1 Existing introductory material

After readers learn:

\[
EBU=D(X_0)-D(X_1),
\]

add a short bridge titled provisionally:

> **From One Action to Many Actions**

It should contain only:

1. one transition;
2. two sequential transitions;
3. cancellation of the middle state;
4. one endpoint-equivalent parallel example;
5. a warning that group EBU is not automatically individual causal EBU;
6. a forward reference to the advanced treatment.

### 16.2 Part VI

Part VI, *Sequential and Parallel EBU Dynamics*, is the primary home for:

- the committed/live field used for pre-action quotes;
- reservations and overlapping quoted actions;
- group quotes and group receipts;
- child receipt preservation;
- causal-identifiability limits;
- institutional allocation and residual reconciliation;
- receipt batching and settlement horizons; and
- the explicit O3 boundary.

Part VII, *Across Distance*, may import these definitions for route-wide
groups, actors, and infrastructure, but must not redefine them or present them
as new foundations.

### 16.3 Dedicated advanced book

The full theory warrants a dedicated volume with the working title:

> **Sequential and Parallel EBU Dynamics**

It should include:

- proofs and counterexamples;
- commuting and non-commuting actions;
- comparator choice;
- nonlinear fields;
- genuine parallel interaction;
- cancellation, redundancy, synergy, and interference;
- group receipts and allocations;
- receipt batching;
- many-action scaling;
- computer scheduling comparisons;
- long-range and delayed effects;
- simulations, worked examples, and exercises.

This dedicated volume is the current Part VI.

### 16.4 Editorial rule

Do not rewrite the existing books immediately. First validate this bridge, then audit every relevant passage and classify it as:

- unchanged;
- needs a qualification;
- needs a cross-reference;
- needs replacement;
- belongs only in the advanced book.

## 17. Frozen vocabulary

| Term | Meaning |
|---|---|
| Action transformation | A declared rule mapping a live predecessor state and action inputs to a successor state |
| Effective interval | The interval from an action's first binding reservation or physical influence to its declared measurement horizon |
| Write support | State coordinates an action may directly change |
| Constraint support | Sources, capacities, budgets, or feasibility constraints an action consumes or alters |
| Compatible accounting boundary | A common state schema, distortion definition, units, and horizon within which values may be compared or closed |
| Represented field distortion | The value \(D(X)\) assigned to a complete represented state under one compatible boundary |
| Dependency edge | Verified overlap plus at least one joint-evaluation condition from §3.7 |
| Joint-transition group | A connected component of the dependency graph evaluated through one common transition |
| Parallel group | A joint-transition group whose effective intervals overlap |
| Sequential transition | An ordered chain in which every action uses the state left by previous actions |
| Admissible comparator set | Every preregistered sequential schedule satisfying the requirements of §9.1 |
| Quantity-fixed comparator | A serialization that preserves the accepted group quantities |
| Rule-replayed comparator | A serialization that recomputes permission and allocation after each predecessor state |
| Group EBU | The measured distortion change \(D(X_0)-D(X_G)\) of the group endpoint |
| Same-baseline field non-additivity | \(N_G=EBU_G-\sum_iEBU_i^{(0)}\), the diagnostic correction to naive child values all evaluated against \(X_0\) |
| Comparator-relative interaction | \(D(X_\pi)-D(X_G)\) for one named admissible sequential comparator |
| State equivalence | Equality of complete represented endpoints |
| EBU equivalence | Equality of endpoint distortion, which does not require state equality |
| Causally identified child contribution | A child value supported by a declared, validated intervention or causal model |
| Child action record | The preserved action-level identity inside a group record |
| Institutional settlement share | An assigned ledger value, not automatically a measured causal fact |
| Group residual | The explicit account that closes group EBU when child settlements do not sum to it |
| Committed field | The observable state plus active commitments relevant to later quotes |
| Receipt batch | Independent records grouped for measurement or verification economy without implying physical interaction |
| Delayed EBU component | The distortion change observed after the immediate action endpoint |
| Nonserializable group | A group for which no sequential schedule preserves the declared children and constraints |

## 18. Questions deliberately left open

1. How should the provisional dependency rule be extended when coupling is
   uncertain, delayed, or known only through an imperfect model?
2. What operational evidence is sufficient to prove that simultaneous actions
   with apparently disjoint support are genuinely separable?
3. Does any purpose-independent canonical comparator exist for non-commuting
   actions, or should applications retain a comparator set permanently?
4. How can interaction ranges over large feasible schedule sets be computed
   without outcome-dependent comparator selection?
5. How should waiting, duration, completion time, ageing, and exogenous drive
   enter the represented state and comparator schedule?
6. When are individual causal contributions identifiable, and how should an
   unidentified causal remainder be represented?
7. Which institutional allocation rules are acceptable when causality is not
   identifiable? General multi-source and multi-tick allocation, split
   invariance, and request-inflation incentives remain O3.
8. When does receipt batching create a real resource saving after measurement
   quality, latency, risk, and coordination cost are included?
9. How are quotes and group membership revised when actions join, leave, fail,
   or change quantity after reservation?
10. How are delayed, long-range, and cross-boundary effects kept causally
    traceable when later groups touch the same field?
11. When may a receipt settle, and when must it remain provisional or carry an
    unresolved residual?
12. How does the model behave for large \(n\), stochastic actions, dynamic
    dependency graphs, and incomplete observation?
13. When can several resource accounts be placed in one compatible boundary
    without inventing an unjustified scalar conversion?
14. Which higher-order interaction decompositions are useful without being
    mistaken for unique causal allocation?
15. How should equal-distortion but different-state endpoints be compared when
    they imply different future viability or capacity?
16. Which structural tests of \(D\) and the child transformations are
    sufficient to establish same-baseline additivity before execution, without
    using candidate outcomes to choose group membership?

## 19. Proposed separately authorized deterministic testing specification

The next bridge-specific scientific stage is a separate **deterministic parallel-testing specification and preregistration**. It has not begun and is
not authorized by this note. That future document should freeze, before any
implementation or execution:

1. versioned state schemas, distortion functions, units, transformations,
   effective intervals, supports, and constraints for M1–M9;
2. the expected dependency graph and group components for every fixture;
3. both feasible two-action orders, the admissible comparator set, and whether
   each comparison is quantity-fixed or rule-replayed;
4. exact expected endpoints, same-baseline child values, \(N_G\), EBU values,
   interactions, closure equations, and numerical tolerances derived without
   trajectories;
5. separate hypotheses and falsifiers for physical measurement, comparator
   logic, causal-identifiability status, institutional settlement closure, and
   batching cost;
6. a settlement-free shared-source physical test before any proposed O3
   allocation experiment;
7. provenance, information boundaries, write-once result mechanics, and
   explicit no-tuning rules; and
8. a strict exclusion keeping Gate 1D-C protocols, plans, code, tests, results,
   incident resolution, and execution authorization unchanged.

Analytical preregistration, implementation, pre-execution validation,
scientific execution, interpretation, and publication must remain separately
authorized stages. Part VI manuscript generation remains later still.

Under the project-wide planning register, review and authorized publication of
this v0.2 checkpoint come first; the remaining Phase B foundation notes and
framework specification may also precede the testing specification. This
section proposes the test specification's contents without changing that
project sequence.

The core bridge to carry forward is:

\[
\boxed{EBU(X_0\rightarrow X_1)=D(X_0)-D(X_1)}
\]

\[
\boxed{EBU_{\mathrm{seq},\pi}=D(X_0)-D(X_{\pi})}
\]

\[
\boxed{EBU_G=D(X_0)-D(X_G)}
\]

\[
\boxed{N_G=EBU_G-\sum_{i\in G}\left[D(X_0)-D(X_i^{(0)})\right]}
\]

\[
\boxed{I_{G\mid\pi}=EBU_G-EBU_{\mathrm{seq},\pi}=D(X_{\pi})-D(X_G)}
\]

These equations unify sequential and parallel accounting while separating the
same-baseline field correction from genuinely new parallel behaviour, which
remains an endpoint difference relative to a declared sequential comparison.
