# The Sequential–Parallel Bridge of EBU

**Status:** Working theory checkpoint v0.1  
**Date:** 2026-08-11  
**Purpose:** Freeze the mathematical bridge between sequential and parallel EBU before changing the existing books or experiments.

## 1. What this document is—and is not

This document is an internal theory note. It is intended to:

- derive the sequential–parallel connection from the fundamental EBU transition equation;
- distinguish algebraic identities from physical assumptions and untested hypotheses;
- introduce parallel groups without losing individual actions, actors, or responsibilities;
- preserve long-range, delayed-effect, and many-action questions for later testing;
- provide a reader-friendly path for future book revisions.

It is **not**:

- a modification of the locked Gate 1DC protocol;
- evidence that the new parallel model is experimentally validated;
- a final book chapter;
- a complete theory of causality or allocation inside a parallel group.

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

A parallel group \(G\) is a set of actions whose relevant physical intervals and accounting boundaries overlap sufficiently that the system must evaluate their common transition:

\[
G=\{A_1,\ldots,A_n\}.
\]

The group preserves the identities of its child actions. Grouping does not mean that the actions disappear or that individual responsibility is erased.

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

## 7. A correction concerning nonlinear fields

Let:

\[
D(x)=x^2
\]

and suppose two actions change the state by \(a\) and \(b\). The total endpoint is \(x+a+b\), and:

\[
EBU=x^2-(x+a+b)^2.
\]

Expanding produces a cross-term \(-2ab\). This cross-term shows that both changes enter the same nonlinear distortion function. It does **not**, by itself, prove a uniquely parallel physical interaction.

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

- a nonlinear shared field can produce cross-terms even when sequential and parallel endpoints are identical;
- genuine parallel interaction, as defined here, exists only when parallel execution changes the final distortion relative to the named sequential comparison.

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

### 9.1 Open problem: choosing the sequential comparator

Possible comparison rules include:

- actual reservation order;
- actual start-time order;
- a physically natural order;
- the best feasible sequential schedule;
- the worst feasible sequential schedule;
- a policy-defined canonical order;
- all relevant orders reported as a range.

No single rule should be adopted before it is tested against the purpose of the comparison.

## 10. Group measurement and individual shares

The field may objectively determine:

\[
EBU_G=D(X_0)-D(X_G),
\]

without determining unique individual causal values.

When separate causal evidence exists, individual effects may be estimated or measured. Evidence may include:

- separate meters;
- controlled experiments;
- validated causal models;
- isolated action trials;
- identifiable resource flows.

When such evidence does not exist, the system should not disguise an allocation rule as a physical measurement.

Let \(S_i\) be the assigned settlement share for child action \(i\). A conservation requirement for a simple closed group settlement is:

\[
\boxed{\sum_{i\in G}S_i=EBU_G}
\]

In the fuller responsibility model, actor shares, provider residuals, institutional guarantees, reserves, and other ledger accounts must together reconcile to the physical group EBU.

Possible allocation rules include:

- measured causal contribution;
- predefined proportional shares;
- reservation-order allocation;
- equal division;
- provider-guaranteed shares;
- permanently joint settlement.

The chosen rule should be fixed before the result is known whenever discretionary hindsight could bias the allocation.

## 11. Group receipt architecture

“Join” should mean:

> Measure the common physical transition once while preserving every child action, actor, provider, promise, and responsibility.

A proposed group record contains:

- group identifier;
- shared source and accounting boundary;
- common initial state or state reference;
- overlap interval;
- committed actions already affecting the field;
- child action records;
- group quote and its assumptions;
- observed group endpoint;
- physical group EBU;
- named sequential comparator, when used;
- interaction value, when identifiable;
- causal evidence or allocation rule;
- individual settlement shares;
- provider or institutional residuals;
- unresolved effects and later measurement horizons.

Grouping must not delete child receipts or erase responsibility.

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

This is not yet a universal EBU law. It is a conditional batching model that must be tested using real measurement, computation, communication, storage, and coordination costs.

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

This is only a temporal accounting identity. The scientific work remains to determine:

- which horizon is appropriate;
- how causality is attributed across distance and time;
- how uncertainty grows with the horizon;
- when a receipt remains open, provisional, or settled;
- how later actions interacting with the same field are separated;
- how irreversible or distributed effects are represented.

Long-range actions therefore remain a dedicated testing workstream after the local sequential baseline.

## 14. Validation programme

The new theory should be tested in layers. The current locked sequential experiment must remain unchanged unless separately authorized.

### Layer 0 — Algebra and specification review

- verify every telescoping derivation;
- verify signs and endpoint definitions;
- distinguish state equivalence from distortion equivalence;
- require a named sequential comparator;
- identify all assumptions embedded in \(X\), \(D\), and \(T\).

### Layer 1 — Existing sequential baseline

- preserve Gate 1DC as the currently locked sequential study;
- resolve its operational preflight incident separately;
- do not add parallel mechanisms to that gate;
- retain its results as the \(|G|=1\) baseline when scientific execution is later authorized.

### Layer 2 — Deterministic two-action bridge tests

Test:

- endpoint-equivalent sequential and parallel actions;
- nonlinear distortion with no true parallel interaction;
- positive interaction;
- negative interaction;
- cancellation with resource use retained;
- redundancy;
- capacity conflict;
- both sequential orders.

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

## 15. Placement in the EBU books

### 15.1 Existing introductory material

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

### 15.2 Part VII

Part VII is the natural place for:

- the committed/live field used for pre-action quotes;
- reservations and overlapping quoted actions;
- group quotes and group receipts;
- child receipt preservation;
- provider responsibility and residual reconciliation.

The exact insertion point must wait until the authoritative Part VII structure is reconciled.

### 15.3 Dedicated advanced book

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

### 15.4 Editorial rule

Do not rewrite the existing books immediately. First validate this bridge, then audit every relevant passage and classify it as:

- unchanged;
- needs a qualification;
- needs a cross-reference;
- needs replacement;
- belongs only in the advanced book.

## 16. Vocabulary to keep stable

| Term | Meaning |
|---|---|
| Individual transition | One identified action evaluated across its before- and after-state |
| Sequential transition | An ordered chain in which every action sees the state left by previous actions |
| Parallel group | Overlapping actions evaluated within one common transition boundary |
| Group EBU | The measured distortion change of the group endpoint |
| Sequential comparator | The declared order or schedule used as the reference for a parallel result |
| Parallel interaction | The EBU difference between a parallel endpoint and a named sequential comparator |
| Child action record | The preserved action-level identity inside a group record |
| Assigned individual share | A settlement allocation, not automatically a measured causal fact |
| Committed field | The observable state plus active commitments relevant to later quotes |
| Receipt batching | Sharing real measurement or verification work across several action records |
| Delayed EBU component | The distortion change observed after the immediate action endpoint |

## 17. Questions deliberately left open

1. What exact overlap condition creates a parallel group?
2. Must two actions share a source, a field component, a time interval, or all three?
3. Which sequential comparator should be canonical when actions do not commute?
4. Should the theory report an interaction range over several feasible orders?
5. How should waiting time and completion time enter the state?
6. When is individual causal contribution identifiable?
7. Which allocation rules are normatively acceptable when causality is not identifiable?
8. When does group receipt batching create a real resource saving?
9. How are quotes revised when new actions join a group after reservation?
10. How are delayed, long-range, and cross-boundary effects kept causally traceable?
11. When may a receipt settle, and when must it remain provisional?
12. How does the model behave for large \(n\), stochastic actions, and incomplete observation?

## 18. The next controlled step

Before any manuscript rewrite or parallel experiment:

1. review this note for conceptual agreement;
2. verify every equation independently;
3. build a table of two-action test cases with explicit \(X\), \(D\), transformations, endpoints, and expected results;
4. decide how the sequential comparator is selected;
5. freeze bridge terminology;
6. create a separate, authorized parallel-testing specification;
7. only then audit the current books and design the advanced volume in detail.

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
\boxed{I_{G\mid\pi}=EBU_G-EBU_{\mathrm{seq},\pi}=D(X_{\pi})-D(X_G)}
\]

These equations unify sequential and parallel accounting while keeping genuinely new parallel behaviour visible as an endpoint difference relative to a declared sequential comparison.
